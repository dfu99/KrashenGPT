import json, os
import numpy as np
from pathlib import Path
from settings import MERGE_DIR
from utils import load_json

def export_json(data, outpath):
    with open (outpath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return outpath

def sample(lang, filepath, size, method="gaussian", **kwargs):
    sentences = load_json(filepath)
    # Resize if input is smaller than our intended size
    if len(sentences) < size:
        print("Not enough sentences. Resizing to input size.")
        size = len(sentences)
    if 'mean' in kwargs:
        mean = kwargs.get('mean')
    if method=="uniform":
        subset = np.random.choice(sentences, size)
    elif method=="gaussian":
        sigma = len(sentences)/3
        mu = 0
        x = np.linspace(-3*sigma, 3*sigma, len(sentences)*2)
        pdf = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-(x - mu)**2 / (2 * sigma**2))
        start_idx = int(len(sentences) - mean)
        end_idx = int(len(sentences) + len(sentences) - mean)
        pdf = pdf[start_idx:end_idx]
        p = pdf / np.sum(pdf)
        subset = list(np.random.choice(sentences, size=size, replace=False, p=p))
    output_filename = Path(filepath).stem
    outpath = os.path.join(MERGE_DIR, lang, output_filename+"_pruned.json")
    export_json(subset, outpath)
    return outpath

if __name__ == "__main__":
    filepath = os.path.join(MERGE_DIR, lang, "sentences_sorted.json")
    sample(filepath, 20000, method="gaussian", mean=0)