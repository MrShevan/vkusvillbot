import telebot
import logging
import os
import io

import pandas as pd
from PIL import Image
from more_itertools import chunked

from lib import ReceiptProcessor
from lib import make_image, make_image_barcode

from config import API_TOKEN
from config import goods_synset_path, goods_images_path, map_path, log_file, shelve_name
from config import save_photo, save_dir
from config import show_barcode, chunk_len

# ------------------------------------ BOT INITIALIZE -----------------------------------------
synset = pd.read_csv(goods_synset_path)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s::%(levelname)s::%(name)s::%(message)s",
                    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
                    datefmt='%Y-%m-%d %H:%M')

bot = telebot.TeleBot(API_TOKEN)
receipt_processor = ReceiptProcessor(synset['Товар'].values)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message,
                 "Привет, Я ВкусВилл бот.\n" +
                 "Я помогу тебе найти местоположение товаров в магазине.\n" +
                 "Пришли мне фото сборочного чека, или отправь в соообщение название товара.")


# Handle text message
@bot.message_handler(content_types=['text'])
def echo_message(message):
    chat_id = message.chat.id
    result, goods, probs = receipt_processor.text_process(message.text)

    logging.info(f'Chat_id: {chat_id} ' +
                 f'Received text: "{message.text}" ' +
                 f'Result: {result} ' +
                 f'Goods: {list(goods)} ' +
                 f'Probabilities: {probs}')

    if not result:
        bot.reply_to(message,
                     "Не могу подобрать товар, попробуй указать более полное имя товара.\n" +
                     "Или отправь крупное фото чека.")

    else:
        if not show_barcode:
            image = make_image(goods_images_path, result, synset, shelve_name)

        else:
            image = make_image_barcode(goods_images_path, result, synset, shelve_name)

        bot.send_photo(chat_id, image)

        # Send map photo in the end
        map_image = open(map_path, 'rb')
        bot.send_photo(chat_id, map_image)


# Handle photo or document message
@bot.message_handler(content_types=['photo', 'document'])
def handle_docs_photo(message):
    try:
        chat_id = message.chat.id

        is_content_photo = message.content_type == 'photo'
        file = message.photo[2] if is_content_photo else message.document

        file_id = file.file_id
        file_name = file_id + '.jpg' if is_content_photo else file.file_name
        file_info = bot.get_file(file_id)

        downloaded_file = bot.download_file(file_info.file_path)

        # Image Save
        if save_photo:
            save_path = os.path.join(save_dir, file_name)
            with open(save_path, 'wb') as new_file:
                new_file.write(downloaded_file)

        # Convert from Bytes to PIL image format
        image = Image.open(io.BytesIO(downloaded_file))
        result, goods, probs = receipt_processor.image_process(image)

        logging.info(f'Chat_id: {chat_id} ' +
                     f'Received text: "{message.text}" ' +
                     f'Result: {result} ' +
                     f'Goods: {list(goods)} ' +
                     f'Probabilities: {probs}')

        if not result:
            bot.reply_to(message,
                         "Не могу подобрать товары, попробуй сфотографиировать чек крупнее." +
                         "Или укажи конкретный товар в сообщении.")

        else:
            # Split list of result goods into chunks of len 12
            for chunk in chunked(result, chunk_len):
                if not show_barcode:
                    image = make_image(goods_images_path, chunk, synset, shelve_name)

                else:
                    image = make_image_barcode(goods_images_path, chunk, synset, shelve_name)

                bot.send_photo(chat_id, image)

            # Send map photo in the end
            map_image = open(map_path, 'rb')
            bot.send_photo(chat_id, map_image)

    except Exception as e:
        bot.reply_to(message, e)


if __name__ == '__main__':
    bot.polling()
