import telebot
from telebot import types
import requests
import json
import fnmatch

bot = telebot.TeleBot('***')
API = '***'

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn2 = types.KeyboardButton("Расписание рейсов между станциями")
    markup.add(btn2)
    bot.send_message(message.chat.id, text="Привет, {0.first_name}! Выбери, что ты хочешь увидеть".format(message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    if(message.text == "Расписание рейсов между станциями"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(back)
        bot.send_message(message.chat.id, text="Введи станции в формате: станция отправления + станция прибытия + дата поездки(гггг-мм-дд)", reply_markup=markup)
    elif (message.text == "Вернуться в главное меню"):
        start(message)
    else:
        ms = message.text.strip().split('+')
        res = requests.get(f'https://api.rasp.yandex.net/v3.0/stations_list/?apikey={API}&lang=ru_RU&format=json')
        data = json.loads(res.text)
        code1 = 0
        code2 = 0
        if len(ms) == 3:
            if fnmatch.fnmatch(str(ms[2]), '????-??-??') and int(str(ms[2])[5] + str(ms[2])[6]) <= 12 and int(
                    str(ms[2])[8] + str(ms[2])[9]) <= 31:
                day = ms[2]
                for i in range(len(data['countries'][29]["regions"][53]['settlements'])):
                    for j in range(len(data['countries'][29]["regions"][53]['settlements'][i]['stations'])):
                        if data['countries'][29]["regions"][53]['settlements'][i]['stations'][j]['title'] == ms[0]:
                            code1 = data['countries'][29]["regions"][53]['settlements'][i]["stations"][j]['codes'][
                                'yandex_code']
                        if data['countries'][29]["regions"][53]['settlements'][i]['stations'][j]['title'] == ms[1]:
                            code2 = data['countries'][29]["regions"][53]['settlements'][i]["stations"][j]['codes'][
                                'yandex_code']
                if code1 != 0 and code2 != 0:
                    res = requests.get(
                        f'https://api.rasp.yandex.net/v3.0/search/?apikey={API}&format=json&from={code1}&to={code2}&lang=ru_RU&page=1&date={day}&transport_types=suburban,train')
                    data = json.loads(res.text)
                    info = ''
                    bot.send_message(message.chat.id, f'Расписание поездов от станции {ms[0]} до станции {ms[1]}. Дата: {ms[2]}')
                    for i in range(len(data['segments'])):
                        info += 'Время отправления: ' + data['segments'][i]['departure'].split('T')[1][
                                                        :5] + ' по местному времени' + '\n'
                        info += 'Время прибытия: ' + data['segments'][i]['arrival'].split('T')[1][
                                                     :5] + ' по местному времени' + '\n'
                        info += 'Остановки: ' + data['segments'][i]['stops'] + '\n'
                        info += 'Продолжительность рейса: ' + str(int(data['segments'][i]['duration']) // 60) + ' минут' + '\n'
                        bot.send_message(message.chat.id, info)
                        info = f'Расписание поездов от станции {ms[0]} до станции {ms[1]}. Дата: {ms[2]} \n'
                    bot.send_message(message.chat.id, '«Данные предоставлены сервисом Яндекс.Расписания» http://rasp.yandex.ru')
                else:
                    bot.reply_to(message, 'Не могу найти такую станцию')
            else:
                bot.reply_to(message, 'Неверный формат даты. Повторите ввод')
        else:
            bot.reply_to(message, 'Неверный формат данных. Повторите ввод')



bot.polling(none_stop=True)