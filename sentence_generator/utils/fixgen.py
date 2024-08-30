import json
import os
from settings import GEN_DIR, ISOCODES
from utils import load_json, gpt

PUNCTUATION = "$%&()*+/\:;<>~°×“”’「」『』〈〉《》…–—−―·】【・£" + '"' + "；"
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def is_not_stub(sentence):
    if len(sentence.split())>1:
        return True
    return False

def is_not_mal(sentence, lang):
    if (not any(c in PUNCTUATION for c in sentence)) and (not '\n' in sentence):
        if lang in ['zh', 'ja', 'ru', 'ko']:
            if not any(c in ALPHABET for c in sentence):
                return True
        else:
            return True
    return False

def remove_stubs(lang):
    if lang in ['ja', 'zh']:
        print("Warning, dangerous config error!")
        return
    path = os.path.join(GEN_DIR, lang)
    jsondb_list = [f for f in os.listdir(path) \
                    if os.path.isfile(os.path.join(path, f)) \
                    and f.endswith(".json") \
                    and (lang in f)]

    for filename in jsondb_list:
        fixed = []
        filepath = os.path.join(path, filename)
        with open(filepath, 'r') as file:
            sentences = json.load(file)
        for sentence in sentences:
            if is_not_stub(sentence):
                fixed.append(sentence)
        noncnt = len(sentences)
        fixcnt = len(fixed)
        print(f"Removed {noncnt-fixcnt} stub entries from {filename}.")

        with open(filepath, 'w') as out:
            json.dump(fixed, out, indent=2, ensure_ascii=False)

def remove_mal(lang):
    """
    Remove malformed sentences
    """
    path = os.path.join(GEN_DIR, lang)
    print(path)

    jsondb_list = [f for f in os.listdir(path) \
                    if os.path.isfile(os.path.join(path, f)) \
                    and f.endswith(".json") \
                    and (lang in f)]

    for filename in jsondb_list:
        fixed = []
        filepath = os.path.join(path, filename)
        with open(filepath, 'r') as file:
            sentences = json.load(file)
        for sentence in sentences:
            if is_not_mal(sentence, lang):
                fixed.append(sentence)
        noncnt = len(sentences)
        fixcnt = len(fixed)
        print(f"Removed {noncnt-fixcnt} poorly generated entries from {filename}.")

        with open(filepath, 'w') as out:
            json.dump(fixed, out, indent=2, ensure_ascii=False)      

# if __name__ == "__main__":
    # for lang in ['ja', 'zh', 'ko', 'ru', 'es', 'fr', 'de']:
        # remove_stubs(lang)
        # remove_mal(lang)