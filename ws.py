from gp import GetPlaces
from random import randrange as r
from random import choice
import math
import requests
from bigbrain import flashsort
import asyncio
from datetime import timedelta
from keys import KEY
from data import db_session
from data.users import User
from data.requests import Requests
from telegram import ReplyKeyboardMarkup
import sqlalchemy

text_analizer = GetPlaces()


def markup_function(id, db_sess):
    k = list(map(lambda x: x.request,
                 list(db_sess.query(Requests).filter(Requests.user_id == id))))
    if len(k) > 3:
        k = k[-3:]
    reply_keyboard = [['/SetLocation', '/SetAddress', '/help'],
                      k]
    return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


def GeoFind(name, near=(45.929773, 51.554219), ammount=5):
    try:
        search_api_server = "https://search-maps.yandex.ru/v1/"
        near_1, near_2 = near
        near = str(near_1) + ',' + str(near_2)

        search_params = {
            "apikey": KEY,
            "text": name,
            "lang": "ru_RU",
            "ll": near,
            "spn": "0.1,0.1",
            "results": ammount
        }

        response = requests.get(search_api_server, params=search_params).json()
        if not response:
            pass
        points = []
        for i in response['features']:
            coords = i['geometry']['coordinates']
            try:
                points.append(
                    Vertex(i['properties']['CompanyMetaData']['name'],
                           name,
                           i['properties']['CompanyMetaData']['address'], coords))
            except KeyError:
                points.append(
                    Vertex(i['properties']['name'],
                           name,
                           i['properties']['name'], coords))
        return points
    except Exception:
        return False


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
        a_lon, a_lat = self.location
        b_lon, b_lat = other.location

        # Берем среднюю по широте точку и считаем коэффициент для нее.
        radius = 6373.0

        lon1 = math.radians(a_lon)
        lat1 = math.radians(a_lat)
        lon2 = math.radians(b_lon)
        lat2 = math.radians(b_lat)

        d_lon = lon2 - lon1
        d_lat = lat2 - lat1

        a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
        c = 2 * math.atan2(a ** 0.5, (1 - a) ** 0.5)

        distance = radius * c
        return distance

    def time(self, other):
        return self.get_distance(other) / 4  # hours

    def timeRepr(self, other):
        res = timedelta(hours=self.get_distance(other) / 4)
        s = str(res).split()
        try:
            days = s[-3]
        except Exception:
            days = False
        hours = int(s[-1].split(':')[0])
        minutes = int(s[-1].split(':')[1])
        ans = ['Идти']
        if days:
            ans.append(f"{days} дней")
        if hours:
            ans.append(f"{hours} часов")
        if minutes:
            ans.append(f"{minutes} минут")
        return ' '.join(ans)


def normal_time(hours):
    sec = int(hours * 3600)
    days = sec // (3600 * 24)
    sec -= days * 3600 * 24
    hours = sec // 3600
    sec -= hours * 3600
    minutes = sec // 60
    sec -= minutes * 60
    ans = ['Идти']
    iss = False
    if days:
        ans.append(f"{days} дней")
    if hours:
        ans.append(f"{hours} часов")
    if minutes:
        ans.append(f"{minutes} минут")
    return ' '.join(ans)


class WayFinder:
    def __init__(self):
        self.time = 0

    def add_user(self, id, last_name, first_name, lang, is_bot, db_sess):
        try:
            user = User()
            user.id = id
            user.last_name = last_name
            user.first_name = first_name
            user.lang = lang
            user.is_bot = int(is_bot)
            db_sess.add(user)
            db_sess.commit()
        except sqlalchemy.exc.IntegrityError:
            db_sess.rollback()

    def set_location(self, id, coords, db_sess):
        user = db_sess.query(User).filter(User.id == id).first()
        user.longitude = coords[0]
        user.latitude = coords[1]
        db_sess.commit()

    async def do_work(self, text, command_type, id, db_sess, coords, update):
        try:
            a, b = coords
        except Exception:
            update.message.reply_text('Сначала отправьте координаты')
            return

        self.update = update

        request = Requests()
        request.user_id = id
        if command_type != 'From':
            request.request = command_type + ' ' + ' '.join(text)
        else:
            request.request = command_type + ' ' + text[0] + ' to ' + text[1]
        db_sess.add(request)
        db_sess.commit()

        goodness = 10
        line = '\n'
        to_say = None
        if command_type == '/FindOne':
            points = GeoFind(' '.join(text), coords, goodness)
            if not points:
                to_say = 'Я вас не понимаю('
            else:
                res = flashsort(points, key=lambda x: Vertex('line', 'line', 'line', coords).time(x))[0]
                time = Vertex('line', 'line', 'line', coords).time(res)
                to_say = f'Объект найден:\n{res}. {normal_time(time)}'
        if command_type == '/FindAny':
            points = GeoFind(' '.join(text[1:]), coords, text[0])
            if not points:
                to_say = 'Я вас не понимаю('
            else:
                ansewrs = []
                for point in points:
                    ansewrs.append((f"*-{point}. {Vertex('line', 'line', 'line', coords).timeRepr(point)}",
                                    Vertex('line', 'line', 'line', coords).time(point)))
                ansewrs = flashsort(ansewrs, key=lambda x: x[1])
                res = []
                for place in ansewrs:
                    res.append(place[0])
                to_say = f'Найдены следующие результаты:\n{line.join(res)}'
        if command_type == '/From':
            now = GeoFind(text[0], coords, 1)[0].location
            if not now:
                to_say = 'Я вас не понимаю('
            else:
                points = {text[1]: GeoFind(text[1], coords, goodness)}
                way, time = await self.find([text[1]], points, now)
                return f"Маршрут построен:\nИз {way[0].__repr__()} . {normal_time(time)}."
        if command_type == '/FindList':
            now = coords
            points = {place_name: GeoFind(place_name, coords, goodness) for place_name in text}
            if not points:
                to_say = 'Я вас не понимаю('
            else:
                way, time = await self.find(text, points, now)
                res = [f"*-{way[i]}" for i in range(len(way))]
                to_say = f"Мы нашли для вас оптимальный маршрут:\n{line.join(res)}. {normal_time(time)} без учёта времени пребывания на местах."
        if command_type == '/FindOrder':
            now = coords
            points = {place_name: GeoFind(place_name, coords, goodness) for place_name in text}
            if not points:
                to_say = 'Я вас не понимаю('
            else:
                way, time = await self.find(text, points, now, order=True)
                res = [f"*-{way[i]}" for i in range(len(way))]
                to_say = f"Мы нашли для вас оптимальный маршрут:\n{line.join(res)}. {normal_time(time)} без учёта времени пребывания на местах."
        if command_type == '/Text':
            to_find = text_analizer.where_to_go(' '.join(text))
            now = coords
            points = {place_name: GeoFind(place_name, coords, goodness) for place_name in to_find}
            if not points:
                to_say = 'Я вас не понимаю('
            else:
                way, time = await self.find(to_find, points, now)

                res = [f"*-{way[i]}" for i in range(len(way))]
                to_say = f"Мы нашли для вас оптимальный маршрут:\n{line.join(res)}. {normal_time(time)} без учёта времени пребывания на местах."
        update.message.reply_text(to_say, reply_markup=markup_function(update.message.from_user.id, db_sess))

    async def find(self, to_go, points, start, order=False):
        self.points = points
        self.begin = start
        self.time = 0
        return await self.go("START", -1, [], to_go, order=order)

    def add_people(self, id, last_name, first_name, lang, is_bot, coords):
        pass

    async def go(self, now_type, ind, way, to_go, time=0, order=False):
        await asyncio.sleep(10 ** (-100))  # ???
        self.time += 1
        if self.time == 2 * 10 ** 5 and self.update is not None:
            self.update.message.reply_text('Ищем место поближе')
        if self.time == 4 * 10 ** 5 and self.update is not None:
            self.update.message.reply_text('Строим наиболее удобный маршрут')
        if self.time == 6 * 10 ** 5 and self.update is not None:
            self.update.message.reply_text('Почти готово')
        count = len(to_go)
        goodness = {0: 0, 1: 100, 2: 80, 3: 20, 4: 5}.get(count, 1)

        if not to_go:
            return way, time
        best_way = []
        best_time = 10 ** 9
        for _ in range(goodness):
            if not order:
                try_type = choice(to_go)
            else:
                try_type = to_go[0]
            try_ind = r(len(self.points[try_type]))
            try_way = way + [self.points[try_type][try_ind]]
            try_to_go = to_go.copy()
            try_to_go.pop(try_to_go.index(try_type))
            if now_type != "START":
                try_time = time + self.points[now_type][ind].time(self.points[try_type][try_ind])
            else:
                try_time = time + Vertex("START", "START", "NOWHERE", self.begin).time(self.points[try_type][try_ind])
            resway, restime = await self.go(try_type, try_ind, try_way, try_to_go, try_time, order=order)
            if restime < best_time:
                best_way = resway.copy()
                best_time = restime
        return best_way, best_time
