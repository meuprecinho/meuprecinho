import telebot
from flask import Flask
import os
import threading
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

TOKEN = "7939579434:AAG6U4ZfG8EGKooZtr6yJ_GAZ8YWvnQp5n0"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot está rodando!"

# Formatar mensagem promocional

def formatar_mensagem(nome, preco_antigo, preco_atual, frete, avaliacao, link, loja):
    cupom = "\n🔖 **Cupom de desconto:** **meuprecinho** 🏷️" if "paguemenos.com.br" in loja else ""
    return (f"🔥 **OFERTA IMPERDÍVEL!** 🔥\n\n"
            f"🛒 **Produto:** {nome}\n"
            f"💰 **De:** R${preco_antigo} **Por:** R${preco_atual}\n"
            f"🚚 **Frete:** {frete}\n\n"
            f"⭐ **Avaliação:** {avaliacao} ⭐\n"
            f"📉 **Desconto válido por tempo limitado!**\n\n"
            f"🔗 **Compre agora:** {link}\n"
            f"⚠️ **Estoque limitado!** Garanta o seu antes que acabe!{cupom}")

# Função para extrair informações de um produto
def extrair_informacoes(link):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(link, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        titulo, preco_antigo, preco_atual, frete, avaliacao = "Não encontrado", "-", "-", "Consultar", "-"

        if "amazon.com.br" in link:
            titulo = soup.find(id='productTitle').text.strip() if soup.find(id='productTitle') else titulo
            preco_atual = soup.find('span', {'class': 'a-price-whole'}).text.strip() if soup.find('span', {'class': 'a-price-whole'}) else preco_atual
            avaliacao = soup.find('span', {'class': 'a-icon-alt'}).text.strip() if soup.find('span', {'class': 'a-icon-alt'}) else avaliacao
        
        elif "mercadolivre.com.br" in link:
            titulo = soup.find('h1', {'class': 'ui-pdp-title'}).text.strip() if soup.find('h1', {'class': 'ui-pdp-title'}) else titulo
            preco_atual = soup.find('span', {'class': 'price-tag-fraction'}).text.strip() if soup.find('span', {'class': 'price-tag-fraction'}) else preco_atual
        
        elif "shopee.com.br" in link:
            titulo = soup.find('div', {'class': 'qaNIZv'}).text.strip() if soup.find('div', {'class': 'qaNIZv'}) else titulo
            preco_atual = soup.find('div', {'class': 'vioxXd'}).text.strip() if soup.find('div', {'class': 'vioxXd'}) else preco_atual
        
        elif "paguemenos.com.br" in link:
            titulo = soup.find('h1', {'class': 'product-name'}).text.strip() if soup.find('h1', {'class': 'product-name'}) else titulo
            preco_atual = soup.find('span', {'class': 'price'}).text.strip() if soup.find('span', {'class': 'price'}) else preco_atual
        
        return formatar_mensagem(titulo, preco_antigo, preco_atual, frete, avaliacao, link, link)
    except Exception as e:
        return f"Erro ao processar o link: {e}"

# Tratamento de mensagens com links
@bot.message_handler(func=lambda message: "http" in message.text)
def processar_link(message):
    link = message.text.strip()
    bot.reply_to(message, "⏳ Processando a oferta, aguarde...")
    informacoes = extrair_informacoes(link)
    bot.reply_to(message, informacoes)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! Envie um link de produto ou loja para eu buscar as informações.")

# Inicia o bot em uma thread separada
def start_bot():
    bot.polling(none_stop=True)

threading.Thread(target=start_bot).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # FORÇANDO A PORTA 10000
    app.run(host="0.0.0.0", port=port)
