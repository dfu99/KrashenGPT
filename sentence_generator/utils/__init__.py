# from .gpt import from_context, from_sentence, from_vocab
# from .mergejson import merge_generated
# from .generate import vocab2sentence, context2sentence, sentence2sentence
# from .resample_sentences import sample
# from .sentencerank import rank
# from .similarities import to_matrix

import json

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data