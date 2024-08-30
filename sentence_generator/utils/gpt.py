from settings.config import GPT_API_KEY
from openai import OpenAI

client = OpenAI(api_key=GPT_API_KEY)

def from_sentence(language, sentence, num, prompt):
    """
    OpenAI API Query
    """
    system_msg = f"For the following queries: \
             Only provide the {language}. \
             Do not provide romanized or translated versions of the text. \
             Do not number the responses. \
             Format the output as a semicolon-separated list. Do not add leading or trailing spaces at each semicolon."
    if prompt=="tone":
        user_msg = f"Create {num} variations of the {language} sentence {sentence} in terms of tone, such as being polite, rude, respectful, casual, or in a hurry."
    elif prompt=="similarity":
        user_msg = f"Create {num} very similar {language} sentences to {sentence}."
    elif prompt=="tense":
        user_msg = f"Create {num} variations of the {language} sentence {sentence} in terms of verb tense."
    elif prompt=="subject":
        user_msg = f"Create {num} variations of the {language} sentence {sentence} in terms of the subject."
    elif prompt=="verb":
        user_msg = f"Create {num} variations of the {language} sentence {sentence} in terms of the verb."
    elif prompt=="adverb":
        user_msg = f"Create {num} variations of the {language} sentence {sentence} in terms of the adverb."
    elif prompt=="adjective":
        user_msg = f"Create {num} variations of the {language} sentence {sentence} in terms of the adjective."
    elif prompt=="object":
        user_msg = f"Create {num} variations of the {language} sentence {sentence} in terms of the object."
    query = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
    )
    response = query.choices[0].message.content
    return response

def from_context(language, num, part, subpart):
    """
    OpenAI API Query
    """
    system_msg = f"For the following queries: \
            Only provide the {language}. \
            Do not provide romanized or translated versions of the text. \
            Do not number the responses. \
            Format the output as a semicolon-separated list. Do not add leading or trailing spaces at each semicolon."
    user_msg = f"Create {num} simple {language} sentences that "\
        f"demonstrate variations in {part}s, specifically, {subpart}."
    query = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
    )
    response = query.choices[0].message.content
    return response

def from_vocab(language, word, num):
    """
    OpenAI API Query
    """
    system_msg = f"You are assisting a person to learn {language} as a second language. \
             I am going to ask you to generate many example sentences or phrases. \
             Each sentence or phrase should be simple and have a little bit of variety, \
             but not a lot of variety such that the user can focus on learning only a few new vocabulary at a time. \
             Only provide the {language}. \
             Do not provide romanized or translated versions of the text. \
             Do not number the responses. \
             Format the output as a semicolon-separated list. Do not add leading or trailing spaces at each semicolon."
    user_msg = f"Create {num} simple {language} sentences using {word}."
    query = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
    )
    response = query.choices[0].message.content
    return response