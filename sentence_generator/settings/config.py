import os

# Add your own OpenAI API key here
GPT_API_KEY=''

# Initialize some variables for some frequently accessed directories
PROJECT_DIR = 'sentence_generator'
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
VOCAB_DIR = os.path.join(DATA_DIR, 'vocab')
GEN_DIR = os.path.join(DATA_DIR, "gen", "sentences")
MERGE_DIR = os.path.join(DATA_DIR, "gen", "merges")
WORD2VEC_DIR = os.path.join(DATA_DIR, "word2vec")
SIMMTX_DIR = os.path.join(DATA_DIR, "simmtx")
