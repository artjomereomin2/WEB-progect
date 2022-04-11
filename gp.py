import pymorphy2


# /FindOne ... - Ищет ближайший объект, указанный после команды, оценивает время до него
# /FindAny ...(количество) ...(объект) - Ищет ближайшие объекты, количество и тип которых указано после команды, оценивает время до них
# /SetLocation ...(геолокация) - Задаёт начальное местоположение
# /From ...(место откуда) to ...(место куда) - Оценивает время пути между 2 точками
# /Text ...(предложение) - Расапознаёт запрос пользователя и сообщает куда и как долго ему нужно идти

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

    def where_to_go(self, text, command_type='/Text'):
        words, others = self.get_letters_and_etc(text)
        if command_type == '/FindOne':
            return words
        if command_type == '/FindAny':
            return (words[0], ' '.join(words[1:]))
        if command_type == '/From':
            ans = [[], []]
            k = 0
            for word in words:
                if word != 'to':
                    ans[k].append(word)
                else:
                    k = 1
            return ans
        if command_type == '/Text':
            nouns = []
            for i in range(len(words)):
                word = words[i]
                # print(self.morph.parse(word)[0].tag)
                if "NOUN" in self.morph.parse(word)[0].tag or (
                        "ADJF" in self.morph.parse(word)[0].tag and word[0].isupper()):
                    if i != 0 and "ADJF" in self.morph.parse(words[i - 1])[0].tag:
                        nouns.append(
                            f"{self.morph.parse(words[i - 1])[0].normal_form} {self.morph.parse(word)[0].normal_form}")
                    else:
                        nouns.append(self.morph.parse(word)[0].normal_form)
            return nouns


example = GetPlaces()

# print(example.where_to_go('Где здесь хорошая аптека к Солнечному'))
