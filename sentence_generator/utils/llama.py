import requests
import json

def response_generator(response):
    """
    Generator function to yield streaming responses.
    """
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            try:
                json_response = json.loads(decoded_line)
                yield json_response['response']
            except json.JSONDecodeError:
                print(f"Error decoding JSON: {decoded_line}")

def query_llama(prompt, model="llama3.1", stream=False):
    """
    Send a prompt to the locally running Llama 3.1 model via Ollama.
    
    :param prompt: The prompt to send to the model
    :param model: The model to use (default is "llama2:3.1")
    :param stream: Whether to stream the response (default is False)
    :return: The model's response
    """
    url = "http://localhost:11434/api/generate"
    
    data = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }
    
    response = requests.post(url, json=data, stream=stream)
    
    if response.status_code == 200:
        if stream:
            return response_generator(response)
        else:
            return response.json()['response']
    else:
        print(f"Error: Received status code {response.status_code}")
        return None
    

def from_sentence(language, sentence, num, variation):
    """
    OLlama Local Query
    """
    conditions = f"Only provide the {language}. \
            Do not explain. \
            Do not provide romanized or translated versions of the text. \
            Do not number the responses. \
            Format the output as a semicolon-separated list. \
            Do not add leading or trailing spaces at each semicolon. \
            All responses must be in their native langauge text."
    if variation=="tone":
        msg = f"Create {num} variations of the {language} sentence {sentence} \
            in terms of tone, such as being polite, rude, respectful, casual, \
                or in a hurry."
    elif variation=="similarity":
        msg = f"Create {num} very similar {language} sentences to {sentence}."
    elif variation=="tense":
        msg = f"Create {num} variations of the {language} sentence {sentence} \
            in terms of verb tense."
    elif variation=="subject":
        msg = f"Create {num} variations of the {language} sentence {sentence} \
            in terms of the subject."
    elif variation=="verb":
        msg = f"Create {num} variations of the {language} sentence {sentence} \
            in terms of the verb."
    elif variation=="adverb":
        msg = f"Create {num} variations of the {language} sentence {sentence} \
            in terms of the adverb."
    elif variation=="adjective":
        msg = f"Create {num} variations of the {language} sentence {sentence} \
            in terms of the adjective."
    elif variation=="object":
        msg = f"Create {num} variations of the {language} sentence {sentence} \
            in terms of the object."
    prompt = msg + conditions
    response = query_llama(prompt)
    return response

def from_context(language, word, num, part, subpart):
    """
    OLlama Local Query
    Llama-8b model is not strong enough to avoid Romanizing some Asian texts
    and additionally requires a word to strengthen the prompt.
    It's very consistent and probably best not to use it.
    """
    prompt = f"Create {num} simple {language} sentences using {word} that \
        demonstrate variations in {part}s, specifically, {subpart}. \
        All sentences must be written in native {language} characters. \
            Only provide the {language}. \
            Do not explain. \
            Do not provide romanized or translated versions of the text. \
            Do not number the responses. \
            Format the output as a semicolon-separated list. \
            Do not add leading or trailing spaces at each semicolon. \
            "
    response = query_llama(prompt)
    return response

def from_vocab(language, word, num):
    """
    OLlama Local Query
    """
    prompt = f"Create {num} simple {language} sentences using {word}. \
        Only provide the {language}. \
        Do not explain. \
        Do not provide romanized or translated versions of the text. \
        Do not number the responses. \
        Format the output as a semicolon-separated list. \
        Do not add leading or trailing spaces at each semicolon. \
        All responses must be in their native langauge text."
    response = query_llama(prompt)
    return response

if __name__ == "__main__":
    # Test generation from vocabulary
    num = 3
    languages = ["Japanese", "Korean", "Spanish", "French", "German", "English", "Russian", "Chinese"]

    print("VOCAB: ========")
    vocab = {"Japanese": "ねこ",
                "Korean": "곰",
                "Spanish": "perro",
                "French": "chat",
                "German": "Hund",
                "English": "dog",
                "Russian": "собака",
                "Chinese": "猫"}
    for lang in languages:
        print(lang, from_vocab(lang, vocab[lang], num))

    # print("CONTEXTS: ========")
    # for lang in languages:
    #     print(lang)
    #     for part in CONTEXTS.keys():
    #         for subpart in CONTEXTS[part]:
    #             print(from_context(lang, vocab[lang], num, part, subpart))

    print("SENTENCES: ========")
    sentences = {"Japanese": "ねこの名前はマミです",
                 "Korean": "곰은 동물이야",
                 "Spanish": "Mi perro es muy feo",
                 "French": "Le chat est grisé",
                 "German": "Der Hund ist groß",
                 "English": "The dog is happy",
                 "Russian": "собака бежит по улице",
                 "Chinese": "猫在睡觉"}
    for lang in languages:
        for variation in ["tone", "similarity", "tense", "subject", "verb", "adverb", "adjective", "object"]:
            print(lang, from_sentence(lang, sentences[lang], 2, variation))
