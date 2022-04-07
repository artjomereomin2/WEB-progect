from gp import GetPlaces
from random import randrange as r
from random import choice

text_analizer = GetPlaces()

# 2022-04-07 22:03:17,254 - telegram.ext.dispatcher - DEBUG - Processing Update: {'message': {'chat': {'username': '***', 'first_name': '***', 'type': 'private', 'id': ***}, 'message_id': 440, 'new_chat_members': [], 'new_chat_photo': [], 'entities': [], 'caption_entities': [], 'group_chat_created': False, 'supergroup_chat_created': False, 'location': {'latitude': ***, 'longitude': ***}, 'date': 1649354597, 'channel_chat_created': False, 'photo': [], 'delete_chat_photo': False, 'from': {'username': '***', 'is_bot': False, 'id': ***, 'language_code': 'ru', 'first_name': '***'}}, 'update_id': 81211740}


class Vertex:
    def __init__(self, name, type, address, location):  # название, адресс, координаты
        self.name = name
        self.type = type
        self.address = address
        self.location = location

    def dist(self, other):
        # может быть не работает
        return ((self.location[0] - other.location[0]) ** 2 + (self.location[1] - other.location[1]) ** 2) ** 0.5


class WayFinder:
    def do_work(self, text):
        self.points = []
        places = text_analizer.where_to_go(text)
        for place in places:
            # TODO тут нужно вписать фунцкию, которая по названию(н-р 'аптека')
            #  и кол-ву необходимых результатов ищет ближайшие(геокодером)
            #  места(их название, тип места(аптека,ресторан...), адресс и координаты)
            mid_ress = ...
            mid_ress = [(f'{place}{i}', place, f'Московская{i}', (r(1000), r(1000))) for i in range(5)]
            for x in mid_ress:
                self.points.append(Vertex(*x))
        result = self.find(0, 0, places)  # TODO вместо 0,0 нужно вписать координаты пользователя

    def find(self, x0, y0, to_find, v=-1, way=[], dist=0):
        if not to_find:
            return dist, way
        best_dist = 10 ** 9
        best_way = []
        for i in range(10):
            to_go_i = r(len(self.points))
            to_go = self.points[to_go_i]
            if to_go.type not in to_find:
                continue
            new_find_list = to_find.copy()
            new_find_list.pop(new_find_list.index(to_go.type))
            d, w = self.find(x0, y0, new_find_list, to_go_i, )  # TODO ДОДЕЛАТЬ МАРШРУТ
