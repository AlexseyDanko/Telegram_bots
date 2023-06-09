import requests
from bs4 import BeautifulSoup
import telebot
import random

URL = 'https://anekdotov.net/anekdot/'
api_key = '#########################'# api your telegram bot


def parsing(URL):
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'lxml')
    base = soup.find_all('div', class_='anekdot')
    return [i.text.replace('\n', "") for i in base]


list_jokes = parsing(URL)
random.shuffle(list_jokes)

bot = telebot.TeleBot(api_key)


@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id, 'Hello, please enter any number: ')


@bot.message_handler(content_types=['text'])
def jokes(message):
    if message.text.lower() in '123456789':
        bot.send_message(message.chat.id, list_jokes[0])
        del list_jokes[0]
    else:
        'Please enter any number'


bot.polling()
