# - *- coding: utf- 8 - *-
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import settings
import pafy
import telebot
import os
import time
from moviepy.editor import *

bot = telebot.TeleBot(settings.TOKEN)

ONE_MINUTE = 60
start_part1 = 0
end_part1 = 40 * ONE_MINUTE
end_part2 = 2 * 40 * ONE_MINUTE
end_part3 = 3 * 40 * ONE_MINUTE
end_part4 = 4 * 40 * ONE_MINUTE


def wait():  # Дает время на завершение операций на диске (возможно не нужна)
    print("wait")
    print("wait")
    print("wait")
    print("wait")
    print("wait")
    print("wait")
    print("wait")
    print("wait")
    print("wait")
    time.sleep(3)


def delete_old_files():  # Удаляет все временные файлы
    files = os.listdir()
    for file in files:
        if file[-4:] == '.mp4' or file[-4:] == 'part' or file[-4:] == '.mp3' \
                or file[-4:] == '.m4a' or file[-4:] == 'webm':
            os.remove(file)


def rename_files(title):  # Переименовывает файлы в 'podcast.mp4
    files = os.listdir()
    for file in files:
        if file[-4:] == '.mp4' or file[-4:] == 'part' or file[-4:] == 'webm':
            os.rename(file, str(title+".mp4"))


def mp4_to_mp3_conversion(title):  # Преобразовывает mp4 в mp3
    video_clip = VideoFileClip(str(title+".mp4"))
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(str(title+".mp3"))
    audio_clip.close()
    video_clip.close()


def split_mp3(start_part, end_part, count_parts, title):  # Разделяет mp3 на нужно количество частей
    ffmpeg_extract_subclip(str(title+".mp3"), start_part, end_part, 'part' + str(count_parts) + "_" + title + ".mp3")


def get_parts_count(max_video_length):  # Определяет на сколько частей делить mp3
    if max_video_length < end_part1:
        return 1  # 1 часть
    elif max_video_length < end_part2:
        return 2  # 2 части
    elif max_video_length < end_part3:
        return 3  # 3 части
    elif max_video_length < end_part4:
        return 4  # 4 части
    else:
        return 0  # Видео слишком длинное


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет!"
                                      "\nОтправь в чат ссылку на youtube видео, а я верну тебе mp3 файл."
                                      "\nЕго можно слушать с выключенным экраном телефона, как подкаст.")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, "При возникновении ошибок остановите бота и очистите чат."
                                      "\nПосле этого перезапустите бота."
                                      "\nМаксимальная длина видео 2 часа 40 минут")


@bot.message_handler(content_types=['text'])
def send_text(message):
    delete_old_files()  # Очищаем каталог от временных файлов

    try:  # Получаем ссылку на видео
        url = message.text
        video = pafy.new(url)
        max_video_length = video.length
        title = video.title

        title = title.replace('|', '_')
        title = title.replace(' ', '_')
        title = title.replace(':', '_')
        title = title.replace('?', '_')
        title = title.replace('/', '_')

        if max_video_length <= end_part4:

            bot.send_message(message.chat.id, "Пожалуйста ожидайте. "
                                              "\nМинимально необходимое качество видео - 360p"
                                              "\nЕсли видео большое, то на его обработку может уйти много времени "
                                              "(до 15 минут при очень больших видео)."
                                              "\nНе отправляйте боту ничего пока он не ответит на предыдущее сообщение,"
                                              "это может замедлить его работу")

            try:  # Скачиваем видео
                streams = video.streams
                for stream in streams:
                    print(stream.resolution, stream.extension)
                    if stream.resolution[-3:] == '360':
                        stream.download()
                    #  elif stream.resolution[-3:] == '360':
                    #  stream.download()
            except:
                bot.send_message(message.chat.id, "Не удалось скачать, минимальное качество видео должно быть 360")

            wait()

            try:  # Переименовываем файл, чтобы дальше с ним удобно работать
                rename_files(title)
            except:
                bot.send_message(message.chat.id, "Не удалось переименовать файл")

            wait()

            try:  # Конвертируем в mp3
                mp4_to_mp3_conversion(title)
            except:
                bot.send_message(message.chat.id, "Не удалось конвертировать в mp3")

            wait()

            try:  # Разделяем большой mp3 файл на части и отправляем пользователю
                parts_count = get_parts_count(max_video_length)
                if parts_count == 1:
                    audio = open(title + ".mp3", 'rb')
                    bot.send_audio(message.chat.id, audio, timeout=60)
                    audio.close()
                elif parts_count == 2:
                    split_mp3(start_part1, end_part1, 1, title)
                    audio = open("part1_" + title + ".mp3", 'rb')
                    bot.send_audio(message.chat.id, audio, timeout=60)
                    wait()
                    audio.close()
                    split_mp3(end_part1, end_part2, 2, title)
                    audio = open("part2_" + title + ".mp3", 'rb')
                    bot.send_audio(message.chat.id, audio, timeout=60)
                    audio.close()
                elif parts_count == 3:
                    split_mp3(start_part1, end_part1, 1, title)
                    audio = open("part1_" + title + ".mp3", 'rb')
                    bot.send_audio(message.chat.id, audio, timeout=60)
                    audio.close()
                    split_mp3(end_part1, end_part2, 2, title)
                    audio = open("part2_" + title + ".mp3", 'rb')
                    bot.send_audio(message.chat.id, audio, timeout=60)
                    audio.close()
                    split_mp3(end_part2, end_part3, 3, title)
                    audio = open("part3_" + title + ".mp3", 'rb')
                    bot.send_audio(message.chat.id, audio, timeout=60)
                    audio.close()
                elif parts_count == 4:
                    split_mp3(start_part1, end_part1, 1, title)
                    audio = open("part1_" + title + ".mp3", 'rb')
                    bot.send_audio(message.chat.id, audio, timeout=60)
                    audio.close()
                    split_mp3(end_part1, end_part2, 2, title)
                    audio = open("part2_" + title + ".mp3", 'rb')
                    bot.send_audio(message.chat.id, audio, timeout=60)
                    audio.close()
                    split_mp3(end_part2, end_part3, 3, title)
                    audio = open("part3_" + title + ".mp3", 'rb')
                    bot.send_audio(message.chat.id, audio, timeout=60)
                    audio.close()
                    split_mp3(end_part3, end_part4, 4, title)
                    audio = open("part4_" + title + ".mp3", 'rb')
                    bot.send_audio(message.chat.id, audio, timeout=60)
                    audio.close()
                elif parts_count == 0:
                    bot.send_message(message.chat.id, "Максимальная длина видео 2 часа 40 минут")

                print("Дошел до конца!")

            except:
                bot.send_message(message.chat.id, "Не удалось порезать на части и отправить."
                                                  "\nПомните, что качество видео должно быть не менее 360p!")

            delete_old_files()

        else:
            bot.send_message(message.chat.id, "Видео слишком большое. Максимум 2 часа 40 минут")

    except:
        bot.send_message(message.chat.id, "Некорректная ссылка")


bot.polling()
