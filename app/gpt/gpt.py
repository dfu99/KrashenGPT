from app import app
from openai import OpenAI

# OpenAI API Key 
client = OpenAI(api_key=app.config['GPT_API_KEY'])


def get_new_text(words, difficulty, language, history=None):
    """
    Given a set of vocabulary words, generates a sentence of the input difficulty
    Prompt keywords to determine sentence difficulty
    Easy: "extremely simple"
    Medium: "very simple"
    Hard: "simple"
    Extreme: "complex"
    """
    if len(words) <= 1:
        words_list = "".join(words)
    else:
        words_list = " and ".join(words)
    msg = "Write a {} {} sentence using {}. ".format(difficulty, language, words_list)
    if history:
        msg += "Make the sentence as similar as possible in sentence structure to {}. ".format(history)
    msg+= "Print only the original sentence and no translations or explanations."
    print("[GPT]", msg)
    query = client.chat.completions.create( 
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "user", "content": msg}
        ]
    )
    response = query.choices[0].message.content
    print("[GPT]", response)
    return response

def generate_batch(part_of_speech, language, context, size=3):
    """
    Produce a batch of length (size) of vocabulary in (parts_of_speech) in the given (language) and with the specified (context)
    """
    msg = f"Give me a list of {size} simple {language} {part_of_speech}s in {language}. The context is {context}. Print only the {language}, without any translation or explanation, and without numbering. Print as a comma-separated list formatted for Python in one line with no spaces."
    print("[GPT]", msg)
    query = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "user", "content": msg}
        ]
    )
    response = query.choices[0].message.content.replace(", ", ",").split(',')
    print("[GPT]", response)
    return response

    
def permute_sentence(last_sentence, language):
    """
    Generates a sentence in the language that is similar to the last sentence
    """
    msg = f"Provide a {language} sentence that has a very similar structure to {last_sentence}. Print only the sentence itself. Do not provide any supplementary information or translation."
    query = client.chat.completions.create( 
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "user", "content": msg}
        ]
    )
    response = query.choices[0].message.content
    print("[GPT]", response)
    return response

def check_correctness(target_sentence, user_answer, language):
    """
    # Verifies the correctness of a translation
    # :param target_sentence: Original language sentence
    # :param user_answer: Translation answer provided by the user
    # :param language: Language of the target sentence
    # :return: 1 if translation is acceptable. 0 if unacceptable.
    """
    msg = f"Confirm, using only the exact strings '1' for 'Yes' or '0' for 'No', whether '{user_answer} is a semantically sufficient translation for the {language} phrase {target_sentence}."
    print("[GPT]", msg)

    query = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "user", "content": msg}
        ]
    )
    response = query.choices[0].message
    print("[GPT]", response)

    if response.content == '1':
        return 1
    
    # Add another layer of prompts
    # Sometimes, subtleties are lost between languages, and GPT seems very picky about this
    # So we'll also ask if the user translation is semantically similar to the translated target sentence, when both are in the same language
    else:
        query = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "user", "content": msg},
                {"role": "assistant", "content": response.content},
                {"role": "user", "content": "Provide the correct translation. Print the translation only without any explanation."}
            ]
        )
        response = query.choices[0].message
        print("[GPT]", response)
        native_translation = response.content

        msg = f"Confirm, using only the exact strings '1' for 'Yes' or '0' for 'No', whether '{user_answer}' \
            is a semantically similar to '{native_translation}'."
        query = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "user", "content": msg}
            ]
        )
        response = query.choices[0].message
        print("[GPT]", response)

        # Decide if native translation and user answer are similar
        if query.choices[0].message.content == '1':
            return 1
        else:
            return 0