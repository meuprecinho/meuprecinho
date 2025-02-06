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

        # Identificar e extrair informações dependendo da loja
        if "amazon.com.br" in link:
            titulo = soup.find(id='productTitle').text.strip() if soup.find(id='productTitle') else "Título não encontrado"
            preco = soup.find('span', {'class': 'a-price-whole'}).text.strip() if soup.find('span', {'class': 'a-price-whole'}) else "Preço não encontrado"
        
        elif "mercadolivre.com.br" in link:
            titulo = soup.find('h1', {'class': 'ui-pdp-title'}).text.strip() if soup.find('h1', {'class': 'ui-pdp-title'}) else "Título não encontrado"
            preco = soup.find('span', {'class': 'price-tag-fraction'}).text.strip() if soup.find('span', {'class': 'price-tag-fraction'}) else "Preço não encontrado"
        
        elif "shopee.com.br" in link:
            titulo = soup.find('div', {'class': 'qaNIZv'}).text.strip() if soup.find('div', {'class': 'qaNIZv'}) else "Título não encontrado"
            preco = soup.find('div', {'class': 'vioxXd'}).text.strip() if soup.find('div', {'class': 'vioxXd'}) else "Preço não encontrado"
        
        elif "shein.com.br" in link:
            titulo = soup.find('h1', {'class': 'product-intro__head-name'}).text.strip() if soup.find('h1', {'class': 'product-intro__head-name'}) else "Título não encontrado"
            preco = soup.find('span', {'class': 'normal-price'}).text.strip() if soup.find('span', {'class': 'normal-price'}) else "Preço não encontrado"
        
        elif "magazinevoce.com.br" in link or "magazineluiza.com.br" in link:
            titulo = soup.find('h1', {'data-testid': 'heading-product-title'}).text.strip() if soup.find('h1', {'data-testid': 'heading-product-title'}) else "Título não encontrado"
            preco = soup.find('p', {'data-testid': 'price-value'}).text.strip() if soup.find('p', {'data-testid': 'price-value'}) else "Preço não encontrado"
        
        else:
            titulo = "Título não encontrado"
            preco = "Preço não encontrado"

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
