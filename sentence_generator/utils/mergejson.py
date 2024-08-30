import json
import os
from settings import GEN_DIR, MERGE_DIR

def merge_generated(lang):
    path = os.path.join(GEN_DIR, lang)
    jsondb_list = [f for f in os.listdir(path) \
                   if os.path.isfile(os.path.join(path, f)) \
                    and f.endswith(".json") \
                    and (lang in f)]
    print("Merging the following files:")
    for filename in jsondb_list:
        print(filename)
    all_sentences = []
    for filename in jsondb_list:
        filepath = os.path.join(path, filename)
        with open(filepath, 'r') as file:
            new_sentences = json.load(file)
        all_sentences += new_sentences

    # Remove doubles, just in case
    non_unique_count = len(all_sentences)
    all_sentences = list(set(all_sentences))
    unique_count = len(all_sentences)
    print(f"Detected and removed {non_unique_count-unique_count} duplicates.")

    outpath = os.path.join(MERGE_DIR, lang, "sentences.json")
    os.makedirs(os.path.join(MERGE_DIR, lang), exist_ok=True)
    with open(outpath, 'w') as out:
        json.dump(all_sentences, out, indent=2, ensure_ascii=False)
    return outpath