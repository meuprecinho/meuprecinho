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

# Função para extrair informações de produtos em um link de loja Shopee usando Selenium
def extrair_produtos_shopee(link_loja):
    driver = None
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(link_loja)
        
        # Esperar o carregamento da página
        driver.implicitly_wait(10)
        
        # Encontra todos os produtos listados na página da loja
        produtos = driver.find_elements(By.CLASS_NAME, 'shopee-search-item-result__item')
        resultado = []

        for produto in produtos:
            try:
                titulo = produto.find_element(By.CLASS_NAME, 'line-clamp-2').text.strip()
                preco = produto.find_element(By.CLASS_NAME, 'vioxXd').text.strip()
                link_produto = produto.find_element(By.TAG_NAME, 'a').get_attribute('href')
                resultado.append(f"Título: {titulo}\nPreço: {preco}\nLink: {link_produto}")
            except Exception as e:
                resultado.append("Erro ao extrair produto")

        return "\n\n".join(resultado) if resultado else "Nenhum produto encontrado na loja."
    except Exception as e:
        return f"Erro ao processar a loja: {e}"
    finally:
        if driver:
            driver.quit()

# Função para extrair informações de um link de produto ou loja
def extrair_informacoes(link):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(link, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        if "shopee.com.br" in link and "/shop/" in link:
            return extrair_produtos_shopee(link)  # Processa o link da loja Shopee

        # Identificar e extrair informações dependendo da loja
        titulo = "Título não encontrado"
        preco = "Preço não encontrado"

        if "amazon.com.br" in link:
            titulo = soup.find(id='productTitle').text.strip() if soup.find(id='productTitle') else titulo
            preco = soup.find('span', {'class': 'a-price-whole'}).text.strip() if soup.find('span', {'class': 'a-price-whole'}) else preco
        
        elif "mercadolivre.com.br" in link:
            titulo = soup.find('h1', {'class': 'ui-pdp-title'}).text.strip() if soup.find('h1', {'class': 'ui-pdp-title'}) else titulo
            preco = soup.find('span', {'class': 'price-tag-fraction'}).text.strip() if soup.find('span', {'class': 'price-tag-fraction'}) else preco
        
        elif "shopee.com.br" in link:
            titulo = soup.find('div', {'class': 'qaNIZv'}).text.strip() if soup.find('div', {'class': 'qaNIZv'}) else titulo
            preco = soup.find('div', {'class': 'vioxXd'}).text.strip() if soup.find('div', {'class': 'vioxXd'}) else preco
        
        elif "shein.com.br" in link:
            titulo = soup.find('h1', {'class': 'product-intro__head-name'}).text.strip() if soup.find('h1', {'class': 'product-intro__head-name'}) else titulo
            preco = soup.find('span', {'class': 'normal-price'}).text.strip() if soup.find('span', {'class': 'normal-price'}) else preco
        
        elif "magazineluiza.com.br" in link:
            titulo = soup.find('h1', {'data-testid': 'heading-product-title'}).text.strip() if soup.find('h1', {'data-testid': 'heading-product-title'}) else titulo
            preco = soup.find('p', {'data-testid': 'price-value'}).text.strip() if soup.find('p', {'data-testid': 'price-value'}) else preco
        
        elif "magazinevoce.com.br" in link:
            titulo = soup.find('h1', {'class': 'product-title'}).text.strip() if soup.find('h1', {'class': 'product-title'}) else titulo
            preco = soup.find('span', {'class': 'price-value'}).text.strip() if soup.find('span', {'class': 'price-value'}) else preco
        
        elif "paguemenos.com.br" in link:
            titulo = soup.find('h1', {'class': 'product-name'}).text.strip() if soup.find('h1', {'class': 'product-name'}) else titulo
            preco = soup.find('span', {'class': 'price'}).text.strip() if soup.find('span', {'class': 'price'}) else preco

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
    bot.reply_to(message, "Olá! Envie um link de produto ou loja para eu buscar as informações.")

# Inicia o bot em uma thread separada
def start_bot():
    bot.polling(none_stop=True)

threading.Thread(target=start_bot).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # FORÇANDO A PORTA 10000
    app.run(host="0.0.0.0", port=port)
