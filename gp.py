import pymorphy2


class GetPlaces:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def get_letters_and_etc(self, text: str):
        new_text = ''
        others = ''
        for c in text:
            if c.isalpha() or c in [' ', '\n']:
                new_text += c
            else:
                others += c
        return (new_text.split(), others)

    def where_to_go(self, text):
        words, others = self.get_letters_and_etc(text)
        nouns = []
        for i in range(len(words)):
            word = words[i]
            print(self.morph.parse(word)[0].tag)
            if "NOUN" in self.morph.parse(word)[0].tag or (
                    "ADJF" in self.morph.parse(word)[0].tag and word[0].isupper()):
                if i != 0 and "ADJF" in self.morph.parse(words[i - 1])[0].tag:
                    nouns.append(
                        f"{self.morph.parse(words[i - 1])[0].normal_form} {self.morph.parse(word)[0].normal_form}")
                else:
                    nouns.append(self.morph.parse(word)[0].normal_form)
        return nouns


example = GetPlaces()

print(example.where_to_go('Было бы неплохо добраться до Красивой площади Ленина'))
