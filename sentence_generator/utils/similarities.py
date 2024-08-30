import os, h5py
import numpy as np
from collections import defaultdict
from huggingface_hub import hf_hub_download
from settings import SIMMTX_DIR
from utils import load_json
import math

def sentence_to_vector(sentence, nlp_model, w2v_model):
    """Convert a sentence to a vector by averaging word embeddings."""
    tokens = nlp_model(sentence)
    vectors = [w2v_model[token.text] for token in tokens if token.text in w2v_model]
    if not vectors:
        return np.zeros(w2v_model.vector_size)
    return np.mean(vectors, axis=0)

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def calculate_similarities(sentences, nlp_model, w2v_model):
    """Calculate similarities between all pairs of sentences."""
    vectors = [sentence_to_vector(sentence, nlp_model, w2v_model) for sentence in sentences]
    similarities = defaultdict(list)
    
    for i, sentence in enumerate(sentences):
        for j, other_sentence in enumerate(sentences):
            if i != j:
                try:
                    similarity = cosine_similarity(vectors[i], vectors[j])
                except RuntimeWarning:
                    print(f"[RuntimeWarning]: {sentence} (norm: {np.linalg.norm(vectors[i])}) or \
                          {sentence} (norm: {np.linalg.norm(vectors[j])}) may cause divide by zero error.")
                    similarity = -1
                similarities[sentence].append((other_sentence, similarity))
        if (i+1)%1000 == 0:
            print(f"Similarity matrix progress: [{(i+1):>6d}/{len(sentences):>6d}]")
    return similarities

def list_to_idx_lookup(li):
    lookup_table = {}
    key_seq = []
    for idx, item in enumerate(li):
        lookup_table[item] = idx
        key_seq.append(item)
    return lookup_table, key_seq

def export_similarties(lang, similarities, fileno):
    """Exports the similarities as a h5 file"""
    print("Exporting similarity matrix to hdf5 file, which can take awhile...")
    sentence_indices, key_seq = list_to_idx_lookup(list(similarities.keys()))
    sz = len(similarities.keys())
    mtx = np.ones((sz, sz))
    for sentence in similarities.keys():
        idx = sentence_indices[sentence]
        for other_sentence in similarities[sentence]:
            jdx = sentence_indices[other_sentence[0]]
            mtx[idx, jdx] = other_sentence[1]
    filepath = os.path.join(SIMMTX_DIR, lang, lang+f"_simmtx_{fileno:02d}.h5")
    os.makedirs(os.path.join(SIMMTX_DIR, lang), exist_ok=True)
    with h5py.File(filepath, 'w') as f:
        f.create_dataset('matrix', data=mtx, compression="gzip", compression_opts=9)
        dt = h5py.special_dtype(vlen=str)
        sentences_dataset = f.create_dataset('sentences', (len(key_seq),), dtype=dt)
        for i, s in enumerate(key_seq):
            sentences_dataset[i] = s
    print(f"Similarity matrix exported to {filepath}.")
    return filepath

def to_matrix(lang, filepath, nlp_model, w2v_model, shuffle=False):
    import random
    # Load input sentences from JSON file
    print("Loading input sentences...")
    sentencesJSON = load_json(filepath)
    if shuffle:
        random.shuffle(sentencesJSON)
    print(f"Loaded a corpus of {len(sentencesJSON)} sentences!")
    print("Calculating similarities between all sentence pairs.")
    # Calculate similarities
    # Batch every 10000 to reduce computing cost
    # Over 20000 appears to use too much memory
    batch = 10000
    outpaths = []
    for fileno, sentences in enumerate(
        [sentencesJSON[i*batch:i*batch+batch] for i in range(math.ceil(len(sentencesJSON) / batch))],start=0):
        similarities = calculate_similarities(sentences, nlp_model, w2v_model)
        outpath = export_similarties(lang, similarities, fileno) # Save this as h5 file
        outpaths.append(outpath)
    return outpaths
    
if __name__ == "__main__":
    to_matrix()