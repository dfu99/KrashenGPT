"""
Handle completed batches from OpenAI
"""

from settings.config import GPT_API_KEY
from openai import OpenAI
client = OpenAI(api_key=GPT_API_KEY)
import os
import json
from datetime import datetime

def import_jsonl(filename):
    data = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            json_object = json.loads(line.strip())
            data.append(json_object)
    return data

# Set directories
completions_dir = os.path.join("sentence_generator", "batches", "completions")
os.makedirs(completions_dir, exist_ok=True)
pending_dir = os.path.join("sentence_generator", "batches", "pending")
output_dir = os.path.join("sentence_generator", "batches", "output")

# Get information from OpenAI
batches = client.batches.list(limit=30)
filelist = client.files.list()

# Check completed batches
for batch in batches:
    if batch.status == "completed":
        for file in filelist: # Find the corresponding filename
            if file.id == batch.input_file_id:
                filename = file.filename
                print(filename, "completed.")
                lang = filename.split("-")[0]
                filenum = int(filename.split("-")[2][:2])
        # Get the completion data
        file_response = client.files.content(batch.output_file_id)

        # Save it as JSONL
        save_path = os.path.join(completions_dir, filename)
        with open (save_path, 'w') as f:
            f.write(file_response.text)

        # Revise old JSONL using completions
        completions = import_jsonl(save_path)
        old_path = os.path.join(pending_dir, filename)
        old_data = import_jsonl(old_path)

        # Match request id's
        new_data = []
        for i, newitem in enumerate(completions):
            reqid = newitem['custom_id']
            new_content = newitem['response']['body']['choices'][0]['message']['content']

            # Requests are not guaranteed to be in order, but it should be close
            start_idx = i-5 if i-5>0 else 0
            end_idx = i+5
            for olditem in old_data[start_idx:end_idx]:
                old_content = olditem['body']['messages'][1]['content']
                if olditem['custom_id'] == reqid:
                    try: # If 1, no revision was suggested
                        if int(new_content) == 1:
                            new_data.append(old_content)
                        else:
                            print(f"Unknown response {new_content}.")
                    except ValueError: # Otherwise it is a string
                        new_data.append(new_content)
                    break
            else:
                print(f"Did not find matching request for {reqid}.")

        # Output the finished proofread file
        timestamp = datetime.now().isoformat(timespec='minutes')
        os.makedirs(os.path.join(output_dir, lang), exist_ok=True)
        filename = f'generated_sentences_{lang}_{timestamp}_{filenum:02d}.json'
        filepath = os.path.join(output_dir, lang, filename)
        with open(filepath, 'w') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
    