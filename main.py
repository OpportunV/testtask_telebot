import json
from typing import Optional, Tuple

import telebot as tb
from flask import Flask, request

import tools


def init_bot(token: str, saver: tools.Saver, web_data: Optional[Tuple[str, Flask]] = None) -> tb.TeleBot:
    """
    
    :param token: str, bot token
    :param saver: tools.Saver instance or other, must have method add
    :param web_data: optional tuple(url, app), required for webhook
    :return: telebot.TeleBot instance
    """
    bot = tb.TeleBot(token, threaded=False)
    
    bot.remove_webhook()
    if web_data is not None:
        url, app = web_data
        bot.set_webhook(url=url)
        
        @app.route(f'/{url.split("/")[-1]}', method=['POST'])
        def webhook():
            update = tb.types.Update.de_json(request.stream.read().decode('utf-8'))
            bot.process_new_updates([update])
            return 'ok', 200
        
    @bot.message_handler(commands=['start', 'help'])
    def start_handler(message):
        bot.send_message(message.chat.id, "Now you can send audios or photos!\nI'll do something with it.")
        
    @bot.message_handler(content_types=['audio'])
    def audio_handler(message):
        audio = bot.download_file(bot.get_file(message.audio.file_id).file_path)
        
        uid = str(message.chat.id)
        filename = bot.get_file(message.audio.file_id).file_path.split('/')[-1]
        
        saver.add(uid, 'audio', filename, audio)

    @bot.message_handler(content_types=['voice'])
    def voice_handler(message):
        audio = bot.download_file(bot.get_file(message.voice.file_id).file_path)
    
        uid = str(message.chat.id)
        filename = bot.get_file(message.voice.file_id).file_path.split('/')[-1]
    
        saver.add(uid, 'audio', filename, audio)

    @bot.message_handler(content_types=['photo'])
    def image_handler(message):
        image = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
        if tools.contains_face(image):
            uid = str(message.chat.id)
            filename = bot.get_file(message.photo[-1].file_id).file_path.split('/')[-1]
            
            saver.add(uid, 'image', filename, image)

    return bot


def main():
    try:
        with open('config.json') as f:
            token = json.load(f)['token']
    except FileNotFoundError:
        raise FileNotFoundError('Config file is not found.')
    except KeyError:
        raise AttributeError('Token data is missing!')
    
    saver = tools.Saver()
    bot = init_bot(token, saver)
    print('Bot is active!')
    try:
        bot.polling(none_stop=True)
    finally:
        saver.save()
        print('Data saved successfully!')
    

if __name__ == '__main__':
    main()
