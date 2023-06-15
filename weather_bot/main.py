import requests
import datetime
from Token import tg_bot_token, token  # token and api(individual)
from aiogram import Bot, types, Dispatcher
from aiogram.utils import executor

bot = Bot(token=tg_bot_token)

dispatcher = Dispatcher(bot)


@dispatcher.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply('Please insert city name')


@dispatcher.message_handler()
async def get_weather(message: types.Message):
    smile_icon = {
        'Clear': 'Ясно \U00002600',
        'Clouds': 'Облачно \U00002601',
        'Rain': 'Дождь \U00002614',
        'Drizzle': 'Дождь \U00002614',
        'Thunderstorm': 'Гроза \U0000026A1',
        'Snow': 'Снег \U0001F328',
        'Mist': 'Туман \U0001F32b',

    }

    try:
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={token}&units=metric"
        )
        data = r.json()
        # pprint(data)
        city = data['name']
        temp = data['main']['temp']

        weather_discrip = data['weather'][0]['main']
        if weather_discrip in smile_icon:
            wrIcon = smile_icon[weather_discrip]
        else:
            wrIcon = 'Please look out the window'

        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        wind = data['wind']['speed']
        sunrise_time = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
        sunset_time = datetime.datetime.fromtimestamp(data['sys']['sunset'])
        length_of_the_day = datetime.datetime.fromtimestamp(data['sys']['sunset']) - datetime.datetime.fromtimestamp(
            data['sys']['sunrise'])
        await message.reply(f'***{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}***\n'
                            f'Weather in this city : {city}\nTemperature: {temp}C°{wrIcon}\n'
                            f'Humidity: {humidity}%\nPressure: {pressure}m.of.m\nwind: {wind}m.of.s\n'
                            f'Sunrise_time: {sunrise_time}\nSunset_time: {sunset_time}\nLength_of_the_day: {length_of_the_day}\n'
                            f'<><><>Good day!<><><>'
                            )

    except:
        await message.reply('\U00002653 Check your city name \U00002653')


if __name__ == '__main__':
    executor.start_polling(dispatcher)
