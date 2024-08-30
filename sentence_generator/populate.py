from settings import FREQLISTS, EMBEDDINGS, PIPELINES, VOCAB_DIR, WORD2VEC_DIR, MERGE_DIR
from gensim.models import KeyedVectors
import spacy, json, os, shutil
from pathlib import Path
import utils.llama as gpt_llama
import utils.gpt as gpt_openai
from utils import generate, mergejson, sentencerank, cleanfreqlist, \
        resample_sentences, similarities, convert, fixgen

    
def populate(lang, target_corpus_size=500, target_mean=0, max_merge_size=None,
             from_vocab=False, from_freq=False, from_context=False, from_sentence=False,
             batch_vocab=3, batch_freq=3, batch_context=3, batch_sentence=3,
             sample_limit=5,
             vocab_filepath=None,
             freq_filepath=None,
             generator=gpt_openai):
    
    # Load word embeddings
    print("Loading word2vec model using gensim...")
    w2vpath = os.path.join(WORD2VEC_DIR, EMBEDDINGS[lang])
    w2v_model = KeyedVectors.load_word2vec_format(w2vpath)
    print("Loaded!")

    # Load language model
    print("Loading spacy pipeline...")
    nlp_model = spacy.load(PIPELINES[lang])
    print("Loaded!")

    # Always clean the freq_file first
    exist_filepath = os.path.join(VOCAB_DIR, lang, Path(freq_filepath).stem+"_freq.json")
    if os.path.isfile(exist_filepath):
        cleaned_freq_filepath = exist_filepath
        print("Existing cleaned frequecy list found. Skipping the cleaning process.")
    else:
        cleaned_freq_filepath = cleanfreqlist.clean(lang, freq_filepath, nlp_model)
    
    # If we already have more than enough sentences,
    # Skip generation
    # Just to make things easier for automating corpus generation
    if max_merge_size:
        exist_filepath = os.path.join(MERGE_DIR, lang, "sentences.json")
        if os.path.isfile(exist_filepath):
            with open(exist_filepath, 'r', encoding='utf-8') as f:
                corpus_size = len(json.load(f))
            if corpus_size >= max_merge_size:
                print("Existing sentences corpus found with more than the max size. Skipping the generation process.")
                from_vocab = False
                from_context = False
                from_freq = False
                from_sentence = False
            else:
                print("Generating corpus as requested.")

    # Populate from vocabulary list sources
    # Final size = batchsize * #entries
    # Only takes in a single, consolidated file
    # Because vocab lists can be large, pass through a sample limit
    if from_vocab:
        generate.vocab2sentence(lang, vocab_filepath, batch_vocab, sample=sample_limit, generator=generator)
    
    # Populate from frequency list sources
    # A 10k scrape can have 10000-20000 unique entries
    # Final size = batchsize * #entries
    # Because vocab lists can be large, pass through a sample limit
    if from_freq:
        generate.vocab2sentence(lang, cleaned_freq_filepath, batch_freq, sample=sample_limit, generator=generator)

    # Populate from context sources
    # 57 categories
    # Final size = batchsize * #categories
    if from_context:
        generate.context2sentence(lang, batch_context, generator=generator)

    # Re-consolidate everything in the directory into a single file
    # Only if we generated new text
    merged_filepath = mergejson.merge_generated(lang)

    # Expands upon the above corpus
    # We generally want to keep things under 50,000 sentences
    # 8x categories
    # Final size = batchsize * 8 * #prev_sentences
    if from_sentence:
        generate.sentence2sentence(lang, merged_filepath, batch_sentence, sample=sample_limit, generator=generator)

    # Also merge in the expanded corpus
    merged_filepath = mergejson.merge_generated(lang)

    # For most languages with spaces, GPT can sometimes generate poor output
    # These should be caught at generation
    # But if they're not, do it again anyways
    if lang not in ['ja', 'zh']:
        fixgen.remove_stubs(lang)

    # Sort the merged corpus by the frequency list
    sorted_filepath = sentencerank.rank(lang, merged_filepath, cleaned_freq_filepath, nlp_model)

    # We will not need the ENTIRE list
    # Focus on a portion of the corpus depending on user's proficiency
    pruned_filepath = resample_sentences.sample(lang, sorted_filepath, target_corpus_size, method="gaussian", mean=target_mean)

    # From the reduced corpus, generate:
    # - a h5 similarity matrix
    # - a JSON with the sentences only
    simmtx_paths = similarities.to_matrix(lang, pruned_filepath, nlp_model, w2v_model)

    # Convert the JSON into SQL
    # Save into /instance/
    convert.from_json(lang, pruned_filepath)

    # Copy the .h5 files into /instance/
    for f in simmtx_paths:
        filename = os.path.basename(f)
        shutil.copyfile(f, os.path.join("instance", "h5", filename))

if __name__ == "__main__":
    for lang in ['ja', 'zh', 'es', 'fr', 'ru', 'de', 'ko']:
        freq_filename=FREQLISTS[lang]
        freq_filepath = os.path.join(VOCAB_DIR, lang, freq_filename)
        populate(lang, target_corpus_size=10000, target_mean=0, max_merge_size=20000,
                sample_limit=500,
                from_vocab=False,
                from_freq=False,
                from_context=False, 
                from_sentence=False,
                freq_filepath=freq_filepath,
                generator=gpt_llama
                )
