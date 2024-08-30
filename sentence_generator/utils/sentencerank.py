import json, os
from settings import MERGE_DIR
from collections import Counter
from pathlib import Path
from utils import load_json

def calculate_difficulty_score(sentence, freqs_list, nlp_model):
    # Process the text
    doc = nlp_model(sentence)

    # Tokenize
    tokens = [token.text for token in doc]

    # Initialize some stats
    score = 0
    hits = 0
    misses = 0

    # Count frequencies
    freq = Counter(tokens)
    for word, _ in freq.most_common():
        if word in freqs_list:
            hits += 1
            fidx = freqs_list.index(word)
        else:
            misses += 1
            fidx = 0
        # Calculate score using index of frequency list
        score += fidx
    return score, hits, misses

def sort_by_freqs(sentences, freqs, nlp_model):
    total_hits = 0
    total_misses = 0
    # Sort each language's sentences in ascending difficulty according to the 
    #   frequency list. Less frequent = More difficult.
    # [idx=0, easiest], [idx=-1, hardest]
    sentences_sorted = []
    for i, sentence in enumerate(sentences, start=1):
        score, hits, misses = calculate_difficulty_score(sentence, freqs, nlp_model)
        total_hits += hits
        total_misses += misses
        sentences_sorted.append([sentence, score])
        # Print our progress
        if i % 1000 == 0:
            print(f"Progress: {i:>6d}/{len(sentences):<6d}")
    sentences_sorted = sorted(sentences_sorted, key=lambda x: x[1], reverse=False)
    sentences_sorted = [s[0] for s in sentences_sorted]
    # Check the coverage of the freq list
    coverage = total_hits/(total_hits + total_misses) * 100
    return sentences_sorted, coverage

def export_json(data, outpath):
    with open(outpath, 'w') as out:
        json.dump(data, out, indent=2, ensure_ascii=False)

def rank(lang, sentences_fpath, freq_fpath, nlp_model):
    sentencesJSON = load_json(sentences_fpath)
    print(f"Loaded a corpus of {len(sentencesJSON)} sentences!")

    # Load the cleaned up frequency list
    with open(freq_fpath, 'r', encoding='utf-8') as f:
        freqJSON = json.load(f)
    print(f"Loaded a frequency corpus of {len(freqJSON)} vocabulary!")

    # Sort with reference to frequency
    print("Calculating sentence difficulty:")
    sentences_sorted, coverage = sort_by_freqs(sentencesJSON, freqJSON, nlp_model)
    
    # Export to another JSON
    output_filename = Path(sentences_fpath).stem
    outpath = os.path.join(MERGE_DIR, lang, output_filename+"_sorted.json")
    export_json(sentences_sorted, outpath)
    print("Exported a sorted list of sentences " \
        f"with frequency list coverage of {coverage:3.2f}%.")
    return outpath