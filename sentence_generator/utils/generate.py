import json
from datetime import datetime
from settings import CONTEXTS, GEN_DIR, ISOCODES
from utils import load_json, fixgen
import os
import random
import utils.gpt as gpt_openai
import utils.llama as gpt_llama

def export_json(lang, data):
    # Save the generated sentences
    timestamp = datetime.now().isoformat(timespec='minutes')
    filename = f'generated_sentences_{lang}_{timestamp}.json'
    os.makedirs(os.path.join(GEN_DIR, lang), exist_ok=True)
    filepath = os.path.join(GEN_DIR, lang, filename)
    with open (filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath

def vocab2sentence(lang, filepath, batchsize, sample=None, generator=gpt_openai):
    """
    filename: JSON file, each element is a single vocabulary word
    batchsize: Size of each GPT prompt output
    """
    vocabulary = load_json(filepath)
    if sample and sample < len(vocabulary):
        vocabulary = random.sample(vocabulary, sample)
    language = ISOCODES[lang]
    all_sentences = []

    max_size = len(vocabulary)
    print(f"Generating sentences from {max_size} vocabulary words.")
    
    for i, word in enumerate(vocabulary, start=1):
        while True:
            response = generator.from_vocab(language, word, batchsize)
            generated_sentences = [s.strip() for s in response.split(";")]
            # Check if response is well-conditioned
            if len(generated_sentences)==batchsize or generator==gpt_llama:
                break
            # print("Warning, regenerating poor output.")
        # Show some console output for each thing we add just so we know the process is moving
        for sentence in generated_sentences:
            # print(f"Added {sentence}")
            # Skip empty and one-word sentences,
            #   except in zh, ja, which may have no spaces
            if fixgen.is_not_stub(sentence) or lang in ['ja','zh']:
                if fixgen.is_not_mal(sentence, lang):
                    all_sentences.append(sentence)
        if i%100==0:
            print(f"vocab2sentence progress: [{i:>6d}/{max_size:>6d}]")
    outpath = export_json(lang, all_sentences)
    return outpath

def context2sentence(lang, batchsize, generator=gpt_openai):
    """
    batchsize: Size of each GPT prompt output
    """
    language = ISOCODES[lang]
    all_sentences = []

    max_size = 57
    i = 0
    print(f"Generating sentences from {max_size} parts of speech patterns.")

    # There are 57 parts of speech context categories
    for part in CONTEXTS.keys():
        for subpart in CONTEXTS[part]:
            while True:
                if generator == gpt_openai:
                    response = generator.from_context(language, batchsize, part, subpart)
                generated_sentences = [s.strip() for s in response.split(";")]
                # Check if response is well-conditioned
                if len(generated_sentences)==batchsize or generator==gpt_llama:
                    break
                # print("Warning, regenerating poor output.")
            # Show some console output for each thing we add just so we know the process is moving
            for sentence in generated_sentences:
                # print(f"Added {sentence}")
                # Skip empty and one-word sentences,
                #   except in zh, ja, which may have no spaces
                if fixgen.is_not_stub(sentence) or lang in ['ja','zh']:
                    if fixgen.is_not_mal(sentence, lang):
                        all_sentences.append(sentence)
            i+=1
            if i%100==0:
                print(f"context2sentence progress: [{i:>6d}/{max_size:>6d}]")
    outpath = export_json(lang, all_sentences)
    return outpath

def sentence2sentence(lang, filepath, batchsize, sample=500, generator=gpt_openai):
    """
    filename: JSON file, each element is a single sentence
    batchsize: Size of each GPT prompt output
    """
    sentences = load_json(filepath)
    if sample and sample < len(sentences):
        sentences = random.sample(sentences, sample)
    language = ISOCODES[lang]
    outpaths = []

    max_size = len(sentences)
    print(f"Generating sentences from variations of {max_size} existing sentences.")

    # Sentence to sentence will expand the corpus by batch_size * len(variation)
    # e.g. batch=10, prompts=8, input=1000, output = 80000
    for variation in ["tone", "similarity", "tense", "subject", "verb", "adverb", "adjective", "object"]:
        all_sentences = []
        for i, sentence in enumerate(sentences, start=1):
            while True:
                response = generator.from_sentence(language, sentence, batchsize, variation)
                generated_sentences = [s.strip() for s in response.split(";")]
                # Check if response is well-conditioned
                if len(generated_sentences)==batchsize or generator==gpt_llama:
                    break
                # print("Warning, regenerating poor output.")
            # Show some console output for each thing we add just so we know the process is moving
            for sentence in generated_sentences:
                # print(f"Added {sentence}")
                # Skip empty and one-word sentences,
                #   except in zh, ja, which may have no spaces
                if fixgen.is_not_stub(sentence) or lang in ['ja','zh']:
                    if fixgen.is_not_mal(sentence, lang):
                        all_sentences.append(sentence)
            if i%100==0:
                print(f"sentence2sentence progress ({variation}): [{i:>6d}/{max_size:>6d}]")
        # Since this can be a lot, save per variation
        outpath = export_json(lang, all_sentences)
        outpaths.append(outpath)
    return outpaths

if __name__ == "__main__":
    # Vocab to Sentences
    filename = "kanji-array-n5.json"
    LANG = 'ja'
    batch_size = 10 # Number of sentences generated for each word
    vocab2sentence(filename, batch_size)
    
 