from gp import GetPlaces
from random import randrange as r
from random import choice
import math
from datetime import timedelta

text_analizer = GetPlaces()


class Vertex:
    def __init__(self, name, type, address, location):  # название, адресс, координаты
        self.name = name
        self.type = type
        self.address = address
        self.location = location

    def get_distance(self, other):
        # p1 и p2 - это кортежи из двух элементов - координаты точек
        radius = 6373.0

        lon1 = math.radians(self.location[0])
        lat1 = math.radians(self.location[1])
        lon2 = math.radians(other.location[0])
        lat2 = math.radians(other.location[1])

        d_lon = lon2 - lon1
        d_lat = lat2 - lat1

        a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
        c = 2 * math.atan2(a ** 0.5, (1 - a) ** 0.5)

        distance = radius * c
        return distance

    def time(self, other):
        return timedelta(hours=self.get_distance(other) / 4).seconds

    def timeRepr(self, other):
        res = timedelta(hours=self.get_distance(other) / 4)
        s = str(res).split()
        # print(s)
        days = int(s[0])
        hours = int(s[2].split(':')[0])
        minutes = int(s[2].split(':')[1])
        ans = ['Идти']
        if days:
            ans.append(f"{days} дней")
        if hours:
            ans.append(f"{hours} часов")
        if minutes:
            ans.append(f"{minutes} минут")
        return ' '.join(ans)


def normal_time(sec):
    res = timedelta(seconds=sec)
    days = res.days
    seconds = res.seconds
    hours = (seconds % (3600 * 24)) // 3600
    minutes = seconds % 60
    ans = ['Идти']
    if days:
        ans.append(f"{days} дней")
    if hours:
        ans.append(f"{hours} часов")
    if minutes:
        ans.append(f"{minutes} минут")
    return ans


class WayFinder:
    def __init__(self):
        self.start = ()

    def do_work(self, text, num, command_type):
        line = '\n'
        if command_type == '/FindAny':
            points = ...  # TODO вписать поиск ближайших
            return f'Найдены следующие результаты:\n{line.join([f"{Vertex(line, line, line, self.start).time(point)}" for point in points])}'
        if command_type == '/From':
            points = ...  # TODO вписать поиск ближайших
            # TODO доделать

        self.points = {}
        places = text_analizer.where_to_go(text, command_type)
        for place in places:
            # TODO тут нужно вписать фунцкию, которая по названию(н-р 'аптека')
            #  и кол-ву необходимых результатов ищет ближайшие(геокодером)
            #  места(их название, тип места(аптека,ресторан...), адресс и координаты)
            mid_ress = ...
            mid_ress = [(f'{place}{i}', place, f'Московская{i}', (r(1000), r(1000))) for i in range(5)]
            self.points[place] = []
            for x in mid_ress:
                self.points[place].append(Vertex(*x))
        # print(self.points)
        try:
            result = self.find('START', -1, [], places)  # TODO вместо -1,-1 нужно вписать координаты пользователя
            points = []
            for place in result[0]:
                points.append(f"*-{place.name}({place.address})")
            ans = normal_time(result[1])
            return f"Следуйте по маршруту:\n{line.join(points)}\n{' '.join(ans)}"
        except IndexError:
            return 'Сначала отправьте геолокацию'
        except AttributeError:
            return 'Сначала отправьте геолокацию'

    def find(self, now_type, ind, way, to_go, time=0):
        # print(now_type, ind, way, to_go, time)
        if not to_go:
            return way, time
        best_way = []
        best_time = 10 ** 9
        for _ in range(5):
            try_type = choice(to_go)
            try_ind = r(len(self.points[try_type]))
            try_way = way + [self.points[try_type][try_ind]]
            try_to_go = to_go.copy()
            try_to_go.pop(try_to_go.index(try_type))
            if now_type != "START":
                try_time = time + self.points[now_type][ind].time(self.points[try_type][try_ind])
            else:
                try_time = time + Vertex("START", "START", "NOWHERE", self.start).time(self.points[try_type][try_ind])
            resway, restime = self.find(try_type, try_ind, try_way, try_to_go, try_time)
            if restime < best_time:
                best_way = resway.copy()
                best_time = restime
        return best_way, best_time


example = WayFinder()

# example.do_work()

# v1, v2 = Vertex("Москва", "город", "Москва", (55.755799, 37.617617)), Vertex("Питер", "город", "Питер", (59.938955, 30.315644))
# print(v1.time(v2))

print(example.do_work("остановка автобуса 67 рынок Северный", '/Text'))
