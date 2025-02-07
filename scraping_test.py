import telebot
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# Sua chave de API do Telegram
TOKEN = '7939579434:AAFyEN7D5XpRAjOWoAt-HrrJxjDuSua723s'  # Chave API inserida
bot = telebot.TeleBot(TOKEN)

# Função para capturar as informações do produto
def buscar_informacoes(link, chat_id):
    try:
        # Enviar mensagem de "Buscando dados do produto..."
        bot.send_message(chat_id, "Buscando dados do produto...🔍🛍️")

        # Configurações do Chrome
        options = Options()
        options.add_argument("--headless")  # Roda o navegador em modo invisível
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(link)
        
        # Esperar o carregamento da página
        time.sleep(3)

        # Scraping do nome do produto
        try:
            nome_produto = driver.find_element(By.CSS_SELECTOR, "h1[data-testid='heading-product-title']").text
        except Exception as e:
            nome_produto = "Nome não encontrado"
            print(f"Erro ao capturar nome do produto: {e}")

        # Scraping do preço original
        try:
            preco_original = driver.find_element(By.CSS_SELECTOR, "p[data-testid='price-original']").text
        except Exception as e:
            preco_original = "Preço original não encontrado"
            print(f"Erro ao capturar preço original: {e}")

        # Scraping do preço com desconto
        try:
            preco_com_desconto = driver.find_element(By.CSS_SELECTOR, "p[data-testid='price-value']").text
        except Exception as e:
            preco_com_desconto = "Preço com desconto não encontrado"
            print(f"Erro ao capturar preço com desconto: {e}")

        # Scraping do parcelamento
        try:
            parcelamento_element = driver.find_elements(By.CSS_SELECTOR, "p[data-testid='installment']")
            parcelamento = parcelamento_element[0].text if parcelamento_element else None
        except Exception as e:
            parcelamento = None
            print(f"Erro ao capturar parcelamento: {e}")

        # Scraping do cupom (se disponível)
        try:
            cupom_element = driver.find_elements(By.CSS_SELECTOR, "span[data-testid='coupon-code']")
            cupom = cupom_element[0].text if cupom_element else "Cupom não disponível"
        except Exception as e:
            cupom = "Cupom não disponível"
            print(f"Erro ao capturar cupom: {e}")

        # Scraping da imagem do produto
        try:
            # Tentativa de capturar imagem de alta qualidade
            imagem_url_element = driver.find_element(By.CSS_SELECTOR, "img[data-testid='media-gallery-image']")
            imagem_url = imagem_url_element.get_attribute('src').replace("90x90", "500x500")
        except Exception as e:
            imagem_url = "Imagem não encontrada"
            print(f"Erro ao capturar imagem: {e}")

        # Baixar a imagem em alta qualidade
        if imagem_url != "Imagem não encontrada":
            imagem_resposta = requests.get(imagem_url)
            if imagem_resposta.status_code == 200:
                with open("produto.jpg", "wb") as file:
                    file.write(imagem_resposta.content)
                imagem_url = "produto.jpg"  # Atualizando a imagem_url para o caminho do arquivo

        # Fechar o navegador corretamente
        driver.quit()

        # Formatando a mensagem a ser enviada
        msg = (f"🛍️ {nome_produto}\n\n"
               f"~de R$ {preco_original}~\n"
               f"💸 por R$ {preco_com_desconto} 🚨🚨\n")

        # Adicionando parcelamento se disponível
        if parcelamento:
            msg += f"💳 {parcelamento} sem juros\n\n"

        msg += (f"👉Link p/ comprar: {link}\n\n"
                f"*Promoção sujeita a alteração a qualquer momento")

        # Enviando a mensagem com a imagem do produto
        return imagem_url, msg

    except Exception as e:
        print(f"Ocorreu um erro ao buscar as informações do produto: {e}")
        return None, "Erro ao buscar informações do produto."

    finally:
        if driver:
            driver.quit()

# Função para responder ao comando do Telegram
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! Envie um link de produto para eu buscar as informações.")

# Função para lidar com mensagens de texto (links)
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    link = message.text
    chat_id = message.chat.id
    imagem_url, msg = buscar_informacoes(link, chat_id)
    
    if imagem_url and os.path.exists(imagem_url):
        with open(imagem_url, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=msg, parse_mode='Markdown')
    else:
        bot.reply_to(message, msg)

# Iniciar o bot
bot.polling()
