import telebot
from flask import Flask
import os
import threading
import requests
from bs4 import BeautifulSoup

TOKEN = "7939579434:AAG6U4ZfG8EGKooZtr6yJ_GAZ8YWvnQp5n0"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot está rodando!"

# Função para extrair informações de um link
def extrair_informacoes(link):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(link, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Exemplo: Ajuste os seletores de acordo com a estrutura do site
        titulo = soup.find('title').text.strip()
        preco = soup.find(class_='price').text.strip()  # Ajuste o seletor conforme necessário

        return f"Título: {titulo}\nPreço: {preco}\nLink: {link}"
    except Exception as e:
        return f"Erro ao processar o link: {e}"

# Tratamento de mensagens com links
@bot.message_handler(func=lambda message: "http" in message.text)
def processar_link(message):
    link = message.text.strip()
    bot.reply_to(message, "Processando o link, aguarde...")
    informacoes = extrair_informacoes(link)
    bot.reply_to(message, informacoes)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! Envie um link de produto para eu buscar as informações.")

# Inicia o bot em uma thread separada
def start_bot():
    bot.polling()

threading.Thread(target=start_bot).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # FORÇANDO A PORTA 10000
    app.run(host="0.0.0.0", port=port)
