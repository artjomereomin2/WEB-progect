from gp import GetPlaces
from random import randrange as r
from random import choice
import math
from datetime import timedelta

KEY = '9e17d9d0-1bf0-4b91-a0a8-1d208b733889'

text_analizer = GetPlaces()


def GeoFind


class Vertex:
    def __init__(self, name, type, address, location):  # название, адресс, координаты
        self.name = name
        self.type = type
        self.address = address
        self.location = location

    def __repr__(self):
        return f'{self.type} "{self.name}", {self.address}'

    def get_distance(self, other):
        # p1 и p2 - это кортежи из двух элементов - координаты точек
        degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
        a_lon, a_lat = self.location
        b_lon, b_lat = other.location

        # Берем среднюю по широте точку и считаем коэффициент для нее.
        radians_lattitude = math.radians((a_lat + b_lat) / 2.)
        lat_lon_factor = math.cos(radians_lattitude)

        # Вычисляем смещения в метрах по вертикали и горизонтали.
        dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
        dy = abs(a_lat - b_lat) * degree_to_meters_factor

        # Вычисляем расстояние между точками.
        distance = math.sqrt(dx * dx + dy * dy)

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
        places = text_analizer.where_to_go(text, command_type)
        print(text, command_type)
        line = '\n'
        try:
            if command_type == '/FindAny':
                points = GeoFind(text[1], self.start, text[0])
                ansewrs = []
                for point in points:
                    ansewrs.append(f"*-{point[0]}. {Vertex(line, line, line, self.start).timeRepr(point)}")
                return f'Найдены следующие результаты:\n{line.join(ansewrs)}'
            if command_type == '/From':
                now = GeoFind(text[0], self.start)[0]
                points = {text[1]: GeoFind(text[1], self.start, 5)}
                way, time = self.find([text[1]], points, now)
                return f"Ближе всего {way[0].repr()}. {normal_time(time)}."
            if command_type == '/FindList':
                now = self.start
                points = {place_name: GeoFind(place_name, self.start, 5) for place_name in text}
                way, time = self.find(text, points, now)
                res = [f"*-{way[i]}" for i in range(len(way))]
                return f"Мы нашли для вас оптимальный маршрут:\n{line.join(res)}"
            if command_type == '/FindOrder':
                now = self.start
                points = {place_name: GeoFind(place_name, self.start, 5) for place_name in text}
                way, time = self.find(text, points, now, order=True)
                res = [f"*-{way[i]}" for i in range(len(way))]
                return f"Мы нашли для вас оптимальный маршрут:\n{line.join(res)}"
            if command_type == '/Text':
                now = self.start
                points = {place_name: GeoFind(place_name, self.start, 5) for place_name in text}
                way, time = self.find(text, points, now)
                res = [f"*-{way[i]}" for i in range(len(way))]
                return f"Мы нашли для вас оптимальный маршрут:\n{line.join(res)}"
        except IndexError:
            return 'Сначала отправьте геолокацию'
        except AttributeError:
            return 'Сначала отправьте геолокацию'
        """points = {}

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
        
            result = self.find(places, points, 'START', -1, [],
                               places)  # TODO вместо -1,-1 нужно вписать координаты пользователя
            points = []
            for place in result[0]:
                points.append(f"*-{place.name}({place.address})")
            ans = normal_time(result[1])
            return f"Следуйте по маршруту:\n{line.join(points)}\n{' '.join(ans)}"""

    def find(self, to_go, points, start, order=False):  # TODO add order
        self.points = points
        self.begin = start
        return self.go("START", -1, [], to_go, order=order)

    def go(self, now_type, ind, way, to_go, time=0, order=False):
        # print(now_type, ind, way, to_go, time)
        if not to_go:
            return way, time
        best_way = []
        best_time = 10 ** 9
        for _ in range(5):
            try_type = choice(to_go)
            if not order:
                try_ind = r(len(self.points[try_type]))
            else:
                try_ind = 0
            try_way = way + [self.points[try_type][try_ind]]
            try_to_go = to_go.copy()
            try_to_go.pop(try_to_go.index(try_type))
            if now_type != "START":
                try_time = time + self.points[now_type][ind].time(self.points[try_type][try_ind])
            else:
                try_time = time + Vertex("START", "START", "NOWHERE", self.begin).time(self.points[try_type][try_ind])
            resway, restime = self.go(try_type, try_ind, try_way, try_to_go, try_time, order=order)
            if restime < best_time:
                best_way = resway.copy()
                best_time = restime
        return best_way, best_time

# example.do_work()

# v1, v2 = Vertex("Москва", "город", "Москва", (55.755799, 37.617617)), Vertex("Питер", "город", "Питер", (59.938955, 30.315644))
# print(v1.time(v2))

# print(example.do_work("остановка автобуса 67 рынок Северный", '/Text'))
