from utils.detectlang import detect
import os, json
from settings import FILTERS, VOCAB_DIR
from pathlib import Path

PUNCTUATION = "!$%&'()*+,-./\:;<>?~°×“”’「」『』〈〉《》…–—−―·。、】【・£" + '"'
NUMBERS = '0123456789'

# Read file line by line
def read_file(filepath):
    lines = []
    with open(filepath, 'r') as f:
        for line in f:
            # Strip the line number and count columns
            lines.append(line.strip().split("\t")[1])
    return lines

def isword(entry):
    if not any(c in NUMBERS+PUNCTUATION for c in entry):
        return True
    return False

def islang(entry, langs):
    el = detect(entry)
    if el in langs:
        return True
    return False

def isentity(entry, nlp_model):
    doc = nlp_model(entry)
    for token in doc:
        if token.pos_ == "PROPN":
            return True
    return False

def check_entries(db, langs, nlp_model):
    new_db = []
    count = {"nonword": 0, "nonlang": 0, "entity": 0}
    for i, entry in enumerate(db, start=1):
        # Remove the punctuation entries
        if not isword(entry):
            count["nonword"] += 1
        elif not islang(entry, langs):
            count["nonlang"] += 1
        elif isentity(entry, nlp_model):
            count["entity"] += 1
        else:
            new_db.append(entry)
        # Print our progress
        if i % 1000 == 0:
            print(f"Progress: {i:>6d}/{len(db):<6d}")
    print("Removed {} non-word entries.".format(count["nonword"]))
    print("Removed {} non-language entries.".format(count["nonlang"]))
    print("Removed {} entity entries.".format(count["entity"]))
    return new_db

def clean(lang, filename, nlp_model):
    data = read_file(filename)
    print(f"Imported frequency list of {len(data)} entries.")

    # Set a filter of possible languages
    # This is not always straightforward
    # Languages from similar families can get mixed
    langs_filter = FILTERS[lang]
    # Verify each entry on the frequency list
    db = check_entries(data, langs_filter, nlp_model)
    # Save cleaned output to JSON
    output_path = os.path.join(VOCAB_DIR, lang, Path(filename).stem+"_freq.json")
    with open(output_path, 'w') as outf:
        json.dump(db, outf, indent=2, ensure_ascii=False)
    print("Exported cleaned frequency list to {} with {} entries.".format(
        output_path, len(db)
    ))
    return output_path
