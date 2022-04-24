import pymorphy2


class GetPlaces:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def get_letters_and_etc(self, text: str):
        new_text = ''
        others = ''
        for c in text:
            if c.isalpha() or c.isdigit():
                new_text += c
            else:
                new_text += f' {c} '
        return new_text.split()

    def where_to_go(self, text):
        words = self.get_letters_and_etc(text)
        to_find = []
        i = 0
        while i < len(words):
            word = words[i]
            if "NOUN" in self.morph.parse(word)[0].tag:
                name = [word]
                while i >= 0:
                    words.pop(i)
                    i -= 1
                    if i >= 0 and 'ADJF' in self.morph.parse(words[i])[0].tag:
                        name = [words[i]] + name
                    else:
                        break
                to_find.append(' '.join(name))
            i += 1
        i = 0
        while i < len(words):
            word = words[i]
            if word[0].isupper():
                name = [word]
                while i >= 0:
                    words.pop(i)
                    i -= 1
                    if i >= 0 and 'ADJF' in self.morph.parse(words[i])[0].tag:
                        name = [words[i]] + name
                    else:
                        break
                to_find.append(' '.join(name))
            i += 1
        return to_find


example = GetPlaces()
