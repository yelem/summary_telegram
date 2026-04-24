import openai
from telethon import TelegramClient, events
import pytz
from openai import OpenAI
import asyncio

# ==================== НАЛАШТУВАННЯ ====================

# 1. Ключі від облікового запису (з my.telegram.org)
API_ID = ####
API_HASH = '####'

# 2. Ключі від бота та нейромережі
BOT_TOKEN = '####'
MISTRAL_API_KEY = '####'
MY_CHAT_ID = #####  # Telegram ID

# 3. Список каналів
CHANNELS = ['####', '####']
POSTS_LIMIT = 4  # Скільки останніх дописів брати з кожного

# ===================================================

ai_client = OpenAI(api_key=MISTRAL_API_KEY, base_url="https://api.mistral.ai/v1")

# Ініціалізуємо клієнти
user_client = TelegramClient('user_session', API_ID, API_HASH)
bot_client = TelegramClient('bot_session', API_ID, API_HASH)


async def get_summary(text):
    """Робить вижимку через Mistral"""
    max_retries = 3
    base_delay = 2

    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(
                ai_client.chat.completions.create,
                model="open-mistral-nemo",
                messages=[
                    {"role": "system", "content": """Ти — професійний редактор новин. Відповідай ВИКЛЮЧНО українською мовою.

АЛГОРИТМ ДІЙ:
1. Оціни розмір наданого тексту.
2. Якщо текст довгий (3 і більше речень): стисни його суть до 1-2 речень.
3. Якщо текст короткий (1-2 речення): скопіюй його як є, слово в слово.

ФОРМАТ ВІДПОВІДІ:
Ти повинен повернути ТІЛЬКИ готовий текст за шаблоном нижче. Категорично заборонено друкувати свої правила, думки чи інструкції.

**📌 [Придумай короткий заголовок]**
- [Тут розмісти текст, отриманий на кроці 2 або 3]

Використовуй емодзі та жирний шрифт для акцентів."""},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content
        except openai.RateLimitError:
            if attempt == max_retries - 1:
                return "API Mistral перевантажений."
            await asyncio.sleep(base_delay * (2 ** attempt))
        except openai.AuthenticationError:
            return "Помилка: Неправильний API-ключ Mistral."
        except Exception as e:
            if attempt == max_retries - 1:
                return f"Помилка підсумовування: {e}"
            await asyncio.sleep(base_delay)

    # Явний fallback на випадок, якщо цикл завершився без return
    return "Не вдалося отримати підсумок."


async def main():
    print("Запускаю збір новин...")

    # Підключаємо обидва акаунти
    await user_client.start()
    await bot_client.start(bot_token=BOT_TOKEN)

    # Відправляємо собі повідомлення, що процес пішов
    await bot_client.send_message(MY_CHAT_ID, "Почав збирати новини. Зачекай хвилинку...")

    final_message = "**Новини:**\n\n"

    # Виносимо timezone за межі циклу
    kiev_tz = pytz.timezone('Europe/Kyiv')

    for channel in CHANNELS:
        print(f"Читаю канал {channel}...")
        final_message += f"**Джерело: {channel}**\n"

        try:
            raw_messages = await user_client.get_messages(channel, limit=10)
        except Exception as e:
            print(f"Помилка при читанні каналу {channel}: {e}")
            final_message += f"⚠️ Не вдалося отримати повідомлення з каналу.\n\n"
            continue

        text_messages = [msg for msg in raw_messages if msg.text]
        recent_messages = text_messages[:POSTS_LIMIT]
        recent_messages.reverse()

        for message in recent_messages:
            time_str = message.date.astimezone(kiev_tz).strftime("%H:%M")

            summary = await get_summary(message.text)
            await asyncio.sleep(1.5)

            channel_name = channel.replace('@', '')
            post_link = f"https://t.me/{channel_name}/{message.id}"

            final_message += f"🕒 **{time_str}** • {summary}\n🔗 [Читати]({post_link})\n\n"

        final_message += "—\n"

    # --- ВІДПРАВКА ДОВГИХ ПОВІДОМЛЕНЬ ---
    MAX_LENGTH = 4090  # Залишаємо трохи запасу від ліміту 4096

    # Розбиваємо текст на частини
    parts = []
    while len(final_message) > 0:
        if len(final_message) <= MAX_LENGTH:
            parts.append(final_message)
            break

        # Шукаємо останній перенос рядка в межах ліміту
        split_index = final_message.rfind('\n', 0, MAX_LENGTH)

        # Якщо переносу не знайшли — ріжемо жорстко
        if split_index == -1:
            split_index = MAX_LENGTH

        parts.append(final_message[:split_index])
        final_message = final_message[split_index:].lstrip()

    # Відправляємо всі частини по черзі
    for part in parts:
        await bot_client.send_message(MY_CHAT_ID, part, link_preview=False)
        await asyncio.sleep(0.5)

    # ---------------------------------------------------

    print("Готово! Новини відправлені в Telegram.")

    # Відключаємо клієнти
    await user_client.disconnect()
    await bot_client.disconnect()


asyncio.run(main())