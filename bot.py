import disnake
from disnake.ext import commands
import speech_recognition as sr
import asyncio
from collections import defaultdict
import numpy as np
from io import BytesIO

bot = commands.Bot(command_prefix=".", help_command=None, intents=disnake.Intents.all())

recognizer = sr.Recognizer()
user_timeout_count = defaultdict(int)  # Хранит количество раз, когда пользователь произнес ключевые слова

KEYWORDS = ["фимоз", "обоюндо", "пацан", "сосал"]
TIMEOUT_INCREMENT = 60  # Увеличение таймаута на 60 секунд за каждое повторное слово

@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready to work")

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    if after.channel is not None and before.channel is None:
        voice_channel = after.channel
        voice_client = await voice_channel.connect()

        @bot.loop.create_task
        async def listen_to_voice(voice_client):
            while voice_client.is_connected():  
                audio_data = await voice_client.recv()  # Получаем аудиопоток

                # Преобразование аудиоданных для распознавания
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                audio_buffer = BytesIO(audio_array.tobytes())

                with sr.AudioFile(audio_buffer) as source:
                    audio_data = recognizer.record(source)
                    try:
                        text = recognizer.recognize_google(audio_data, language='ru-RU')
                        print(f'Распознанный текст: {text}')

                        if any(word in text for word in KEYWORDS):
                            user_timeout_count[member.id] += 1
                            timeout_duration = user_timeout_count[member.id] * TIMEOUT_INCREMENT

                            await member.timeout(timeout_duration)  # Применение таймаута
                            await member.send(f"Вы получили таймаут на {timeout_duration // 60} минут за использование запрещенных слов!")

                    except sr.UnknownValueError:
                        print("Не удалось распознать речь")
                    except sr.RequestError as e:
                        print(f"Ошибка запроса к сервису распознавания речи: {e}")

                await asyncio.sleep(1)

        bot.loop.create_task(listen_to_voice())

@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready to work")

bot.run("MTMyMTkzODQzNjYwMDM3242342343242OTIzNA.G4f2KP.7n5_y1VOEpbBAw7XIvRXdJnJ6EpPcumfhTA4is")