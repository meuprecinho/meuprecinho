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

# Lista de domínios suportados
LOJAS_SUPORTADAS = [
    "amazon.com.br",
    "mercadolivre.com.br",
    "shopee.com.br",
    "shein.com.br",
    "magazineluiza.com.br",
    "paguemenos.com.br"
]

# Função para validar o link
def validar_link(link):
    for loja in LOJAS_SUPORTADAS:
        if loja in link:
            return True
    return False

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
            descricao = soup.find('div', {'id': 'feature-bullets'}).text.strip() if soup.find('div', {'id': 'feature-bullets'}) else "Descrição não encontrada"

        elif "mercadolivre.com.br" in link:
            titulo = soup.find('h1', {'class': 'ui-pdp-title'}).text.strip() if soup.find('h1', {'class': 'ui-pdp-title'}) else "Título não encontrado"
            preco = soup.find('span', {'class': 'price-tag-fraction'}).text.strip() if soup.find('span', {'class': 'price-tag-fraction'}) else "Preço não encontrado"
            descricao = soup.find('p', {'class': 'ui-pdp-description__content'}).text.strip() if soup.find('p', {'class': 'ui-pdp-description__content'}) else "Descrição não encontrada"

        elif "shopee.com.br" in link:
            titulo = soup.find('div', {'class': 'qaNIZv'}).text.strip() if soup.find('div', {'class': 'qaNIZv'}) else "Título não encontrado"
            preco = soup.find('div', {'class': 'vioxXd'}).text.strip() if soup.find('div', {'class': 'vioxXd'}) else "Preço não encontrado"
            descricao = "Descrição não disponível para Shopee."

        elif "shein.com.br" in link:
            titulo = soup.find('h1', {'class': 'product-intro__head-name'}).text.strip() if soup.find('h1', {'class': 'product-intro__head-name'}) else "Título não encontrado"
            preco = soup.find('span', {'class': 'normal-price'}).text.strip() if soup.find('span', {'class': 'normal-price'}) else "Preço não encontrado"
            descricao = soup.find('div', {'class': 'product-intro__description'}).text.strip() if soup.find('div', {'class': 'product-intro__description'}) else "Descrição não encontrada"

        elif "magazineluiza.com.br" in link:
            titulo = soup.find('h1', {'data-testid': 'heading-product-title'}).text.strip() if soup.find('h1', {'data-testid': 'heading-product-title'}) else "Título não encontrado"
            preco = soup.find('p', {'data-testid': 'price-value'}).text.strip() if soup.find('p', {'data-testid': 'price-value'}) else "Preço não encontrado"
            descricao = "Descrição não disponível para Magazine Luiza."

        elif "paguemenos.com.br" in link:
            titulo = soup.find('h1', {'class': 'product-name'}).text.strip() if soup.find('h1', {'class': 'product-name'}) else "Título não encontrado"
            preco = soup.find('span', {'class': 'price'}).text.strip() if soup.find('span', {'class': 'price'}) else "Preço não encontrado"
            descricao = "Descrição não disponível para Pague Menos."

        else:
            titulo = "Título não encontrado"
            preco = "Preço não encontrado"
            descricao = "Descrição não encontrada"

        return f"**Título:** {titulo}\n**Preço:** {preco}\n**Descrição:** {descricao}\n**Link:** {link}"
    except Exception as e:
        return f"Erro ao processar o link: {e}"

# Tratamento de mensagens com links
@bot.message_handler(func=lambda message: "http" in message.text)
def processar_link(message):
    link = message.text.strip()
    if validar_link(link):
        bot.reply_to(message, "Processando o link, aguarde...")
        informacoes = extrair_informacoes(link)
        bot.reply_to(message, informacoes)
    else:
        bot.reply_to(message, "Desculpe, este link não é suportado. Envie um link de uma loja válida.")

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
