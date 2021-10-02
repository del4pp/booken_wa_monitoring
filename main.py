import telebot
from bs4 import BeautifulSoup
import requests
from telebot.util import user_link
import config, database
from fake_useragent import UserAgent
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.DEBUG)
bot = telebot.TeleBot(config.token)

url_auction = 'https://newauction.com.ua/listing/offer/sovremennye_izdanija-129063?flt_prp_is_hidden=neq_nin_MACRO_TRUE&flt_prp_offerstate=0&flt_prp_sesend=between__macro_now__-__macro_hours_after__2_&flt_prp_sesstart=lt__macro_now&flt_sin_46349334951764=1&srt_prp_cur_price=dsc&pg=0&ipp=180'

def parse():
    response = requests.get(url_auction, headers=requests.utils.default_headers())
    soup = BeautifulSoup(response.text, 'lxml')

    product_name = ''
    product_img = ''
    product_price = ''
    product_time_end = ''
    product_url = ''

    for product_info in soup.findAll('div', attrs={'class':'public_offer_snippet_container'}):
        for p_name in product_info.findAll('a', attrs={'class':'offers__item__title'}):
            product_name = p_name.text
            product_url = 'https://newauction.com.ua/' + str(p_name['href'])
        for p_img in product_info.findAll('div', attrs={'class':'offer_item_popup_photo'}):
            product_img = p_img['data-original']
        for p_price in product_info.findAll('div', attrs={'class':'price'}):
            product_price = p_price.text
        for p_time_end in product_info.findAll('div', attrs={'class':'offers__item__expiry'}):
            product_time_end = p_time_end.text

        product_new = database.check_new_book(product_url)
        if not product_new:
            send_telegram(product_name, product_img, product_price, product_time_end, product_url)
            database.inser_book_in_db(product_url)
        else:
            time.sleep(1800)

def send_telegram(product_name, product_img, product_price, product_time_end, product_url):
    message_text = """
Книга - "{0}"

Ціна - {1} грн.

{2}
    """.format(product_name, str(product_price).replace('\n', ''), str(product_time_end).replace('\n', ''))
    menu_buy = telebot.types.InlineKeyboardMarkup()
    menu_buy.row(telebot.types.InlineKeyboardButton(text='Купити', url=product_url))

    response = requests.get(product_img)
    file = open("top_img.png", "wb")
    file.write(response.content)
    file.close()
    
    top_img = open("top_img.png", 'rb') 
    bot.send_photo('604377972', photo=top_img, caption=message_text, reply_markup=menu_buy)
    top_img.close()

def main():
    parse()

while True:
    try:
        main()
    except Exception as e:
        bot.send_message('604377972', str(e))