import pymorphy2


class GetPlaces:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def get_letters_and_etc(self, text: str):
        new_text = ''
        others = ''
        for c in text:
            if c.isalpha() or c in [' ', '\n']:
                new_text += c.lower()
            else:
                others += c
        return (new_text.split(), others)

    def where_to_go(self, text):
        words, others = self.get_letters_and_etc(text)
        nouns = []
        for word in words:
            if "NOUN" in self.morph.parse(word)[0].tag:
                nouns.append(self.morph.parse(word)[0].normal_form)
        return nouns
