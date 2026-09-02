"""
Kiro Telegram Bot (Gemini)
Бесплатный AI-ассистент в Telegram на базе Google Gemini.
Запуск: C:\Python314\python.exe bot.py
"""

import asyncio
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8819556227:AAE3pZi1kEaD2UNAtoGZ0ZkGDv1yxv6KcyY"
GEMINI_API_KEY = "AQ.Ab8RN6JNG5bIntai6VQN6au81c3z0o-hQ_VGa2cEY3f03DDKVg"

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Настраиваем Gemini
genai.configure(api_key=GEMINI_API_KEY)

# История чатов (сохраняется пока бот запущен)
chat_sessions: dict[int, object] = {}

SYSTEM_PROMPT = (
    "Ты Kiro 👻 — умный AI-помощник в Telegram. "
    "Отвечай кратко и по делу на русском языке. "
    "Будь дружелюбным, полезным и немного весёлым. "
    "Можешь помогать с вопросами, задачами, объяснениями, переводами и советами."
)

def get_chat_session(chat_id: int):
    """Получить или создать сессию чата для пользователя"""
    if chat_id not in chat_sessions:
        model = genai.GenerativeModel(
            model_name="gemini-3.6-flash",
            system_instruction=SYSTEM_PROMPT
        )
        chat_sessions[chat_id] = model.start_chat(history=[])
    return chat_sessions[chat_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я Kiro 👻 — твой AI-помощник.\n\n"
        "Пиши мне что угодно — отвечу прямо здесь!\n\n"
        "Команды:\n"
        "/start — приветствие\n"
        "/clear — очистить историю разговора\n"
        "/help — помощь"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Что я умею:\n\n"
        "• Отвечать на вопросы\n"
        "• Объяснять сложные темы просто\n"
        "• Переводить тексты\n"
        "• Придумывать идеи\n"
        "• Помогать с задачами\n"
        "• Вести диалог и помнить контекст\n\n"
        "Просто напиши мне!"
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in chat_sessions:
        del chat_sessions[chat_id]
    await update.message.reply_text("🧹 История разговора очищена!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text
    user_name = update.effective_user.first_name or "друг"

    logger.info(f"Сообщение от {user_name}: {user_text[:50]}")

    # Показываем индикатор печати
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        chat = get_chat_session(chat_id)
        response = await asyncio.to_thread(chat.send_message, user_text)
        reply = response.text
        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Ошибка Gemini: {e}")
        # Пробуем сбросить сессию при ошибке
        if chat_id in chat_sessions:
            del chat_sessions[chat_id]
        await update.message.reply_text(
            "⚠️ Что-то пошло не так. Попробуй ещё раз или напиши /clear"
        )

def main():
    print("🤖 Kiro Bot (Gemini) запускается...")
    print(f"   Telegram: {BOT_TOKEN[:15]}...")
    print(f"   Gemini: {GEMINI_API_KEY[:15]}...")
    print("   Нажми Ctrl+C для остановки\n")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен! Открой Telegram и напиши боту.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
