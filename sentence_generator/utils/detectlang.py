import spacy
from spacy.language import Language
from spacy_language_detection import LanguageDetector

print("Loading a spacy English pipeline for language detection...")
nlp = spacy.load("en_core_web_sm")
print("Loaded!")

def get_lang_detector(nlp, name):
    return LanguageDetector(seed=42)

def detect(text):
    Language.factory("language_detector", func=get_lang_detector)
    try:
        nlp.add_pipe('language_detector', last=True)
    except ValueError:
        pass

    # Document level language detection
    doc = nlp(text)
    language = doc._.language
    return language['language']

if __name__ == "__main__":
    text = "안녕하세요. 한국어 텍스트 분석을 해보겠습니다. 한국어는 아름다운 언어입니다."
    print(detect(text))
    text = "ピーター・デュースバーグ () などのように"
    print(detect(text))