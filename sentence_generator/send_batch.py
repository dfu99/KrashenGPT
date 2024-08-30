"""
Sends proofread batches to OpenAI API
"""

import json
import os
from settings import ISOCODES
from utils import load_json
from settings.config import GPT_API_KEY
import os
clear = lambda: os.system('clear')

import time

from openai import OpenAI
client = OpenAI(api_key=GPT_API_KEY)

GEN_DIR = os.path.join("sentence_generator", "data", "gen", "sentences")

def save_jsonl(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for item in data:
            json_line = json.dumps(item, ensure_ascii=False)
            file.write(json_line + '\n')

def make_batch_request(language, filepath):
    """
    Turn each sentence into a request
    """
    data = []
    sentences = load_json(filepath)
    for i, sentence in enumerate(sentences, start=1):
        req = {"custom_id": f"request-{i:05d}",
               "method": "POST",
               "url": "/v1/chat/completions", 
               "body": {
                    "model": "gpt-4o-mini", 
                    "messages": [
                        {"role": "system", "content": 
                        f"If the following {language} sentence is grammaticaly " +\
                        "correct and sounds natural, answer with only a '1'. " +\
                        f"If it is not, answer with only the {language} sentence " +\
                        "that would make more sense. Avoid suggesting unnecessary changes."
                        },
                        {"role": "user", "content": f"{sentence}"}
                        ],
                "max_tokens": 1000
            }}
        data.append(req)
    return data
        
def create_batches(lang):
    language = ISOCODES[lang]
    batch_dir = os.path.join("sentence_generator", "batches", "pending")
    os.makedirs(batch_dir, exist_ok=True)
    # Use the generated JSON lists as the source
    path = os.path.join(GEN_DIR, lang)
    # Get all the JSONs in the language's directory
    jsondb_list = [f for f in os.listdir(path) \
                if os.path.isfile(os.path.join(path, f)) \
                and f.endswith(".json") \
                and (lang in f)]
    # For each file, convert each sentence into a chat completion request
    for i, filename in enumerate(jsondb_list):
        filepath = os.path.join(path, filename)
        data = make_batch_request(language, filepath)
        # Save it to JSONL format
        outname = os.path.join(batch_dir, f"{lang}-req-{i:02d}.jsonl")
        save_jsonl(data, outname)

        # Send the file to OpenAI
        client.files.create(
            file=open(outname, "rb"),
            purpose="batch"
        )

def send_batch(file):
    """
    Pull the file id from OpenAI,
    then send it into the batch queue
    """
    client.batches.create(
    input_file_id=file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
    metadata={
        "description": f"proofread {file.filename}"
    }
)

if __name__ == "__main__":
    # Create and upload the batch files
    # for lang in ['de', 'es', 'fr', 'ja', 'ko', 'ru', 'zh']:
    #     create_batches(lang)
    
    # In a loop,
    #   Check our currently running and completed batches
    #   Compare with our full list of files we uploaded
    #   Start batches within as long we are under our usage limit
    while True:
        clear()
        batch_limit = 2 # Usage limit
        active_batches = 0
        batches = client.batches.list(limit=100)
        
        # Check batch statuses
        completed_file_id_list = []
        for batch in batches:
            if batch.status != "failed":
                print(batch.metadata['description'], batch.id, "status:", 
                      batch.status, batch.request_counts)
            if batch.status == "in_progress":
                active_batches += 1
                completed_file_id_list.append(batch.input_file_id)
            elif batch.status == "validating":
                active_batches += 1
                completed_file_id_list.append(batch.input_file_id)
            elif batch.status == "finalizing":
                active_batches += 1
                completed_file_id_list.append(batch.input_file_id)
            elif batch.status == "completed":
                completed_file_id_list.append(batch.input_file_id)
        print(f"Active batches ({active_batches}/{batch_limit})")

        # Check uploaded files
        filelist = client.files.list()
        pending_file_id_list = [file.id for file in filelist \
                                if file.id not in completed_file_id_list \
                                    and file.purpose=="batch"]
        # Exit the loop if we are done
        if len(pending_file_id_list) == 0:
            break
        else:
            print(f"Remaining batches: {len(pending_file_id_list)}")

        # Check all our files
        # Submit the ones that have not been completed yet
        #   if we are under usage limits
        for file in filelist:
            if file.id in pending_file_id_list:
                if active_batches < batch_limit:
                    active_batches += 1
                    send_batch(file)
                    break
        time.sleep(300)

