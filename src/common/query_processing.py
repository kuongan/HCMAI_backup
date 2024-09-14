from pyvi import ViUtils, ViTokenizer
from deep_translator import GoogleTranslator
import translate
from difflib import SequenceMatcher
from langdetect import detect

class Translation():
    def __init__(self, from_lang='vi', to_lang='en', mode='google'):
        self.__mode = mode
        self.__from_lang = from_lang
        self.__to_lang = to_lang

        if mode == 'google':
            self.translator = GoogleTranslator(source=self.__from_lang, target=self.__to_lang)
        elif mode == 'translate':
            self.translator = translate.Translator(from_lang=self.__from_lang, to_lang=self.__to_lang)
        else:
            raise ValueError("Invalid mode. Choose either 'google' or 'translate'.")

    def preprocessing(self, text):
        return text.lower()

    def __call__(self, text):
        text = self.preprocessing(text)
        if self.__mode == 'translate':
            return self.translator.translate(text)
        elif self.__mode == 'google':
            return self.translator.translate(text)
        else:
            raise ValueError("Invalid mode. Choose either 'google' or 'translate'.")

class Text_Preprocessing():
    def __init__(self, stopwords_path=r'src/app/static/data/vietnamese-stopwords-dash.txt'):
        with open(stopwords_path, 'rb') as f:
            lines = f.readlines()
        self.stop_words = [line.decode('utf8').replace('\n','') for line in lines]

    def find_substring(self, string1, string2):

        match = SequenceMatcher(None, string1, string2, autojunk=False).find_longest_match(0, len(string1), 0, len(string2))
        return string1[match.a:match.a + match.size].strip()

    def remove_stopwords(self, text):

        text = ViTokenizer.tokenize(text)
        return " ".join([w for w in text.split() if w not in self.stop_words])

    def lowercasing(self, text):
        return text.lower() 

    def uppercasing(self, text):
        return text.upper()

    def add_accents(self, text): 

        return ViUtils.add_accents(u"{}".format(text))

    def remove_accents(self, text): 

        return ViUtils.remove_accents(u"{}".format(text))


    def __call__(self, text):

        text = self.lowercasing(text)
        text = self.remove_stopwords(text)
        # text = self.remove_accents(text)
        # text = self.add_accents(text)
        return text