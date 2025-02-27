import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import sys  # Импортируем модуль sys
import re  # Импортируем модуль re для работы с регулярными выражениями

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для сохранения ID пользователя и текста в текстовый файл с кодировкой UTF-8
def save_user_data(user_id, username, text):
    # Если username не None, формируем строку с username. Иначе используем user_id
    if username:
        data_to_write = f"@{username}: {text}\n"
    else:
        data_to_write = f"{user_id}: {text}\n"

    # Проверяем, существует ли файл
    try:
        if os.path.exists('users_data.txt'):
            with open('users_data.txt', 'r', encoding='utf-8') as file:
                existing_data = file.readlines()
            # Если данных нет, добавляем их
            if data_to_write not in existing_data:
                with open('users_data.txt', 'a', encoding='utf-8') as file:
                    file.write(data_to_write)
        else:
            # Если файла нет, создаём его и записываем данные
            with open('users_data.txt', 'w', encoding='utf-8') as file:
                file.write(data_to_write)
    except Exception as e:
        logger.error(f"Ошибка при записи в файл: {e}")  # Добавляем обработку исключений

# Функция для получения токена
def get_token():
    token_file = 'token.txt'
    token = None  # Инициализируем token как None
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r', encoding='utf-8') as file:
                token = file.read().strip()
                if token:
                    return token
        except Exception as e:
            logger.error(f"Ошибка при чтении токена: {e}")

    # Если token отсутствует, запрашиваем ввод и сохраняем
    if not token:
        token = input("Пожалуйста, введите токен вашего бота: ").strip()
        try:
            with open(token_file, 'w', encoding='utf-8') as file:
                file.write(token)
        except Exception as e:
            logger.error(f"Ошибка при записи токена: {e}")
    return token

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Здравствуйте, {user.first_name}! Какое авто из опубликованных в приложении вас интересует? Уточните информацию."
    )

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    username = user.username  # Получаем username пользователя (может быть None)
    user_text = update.message.text

    logger.info(f"Получено сообщение от user_id={user_id}, username={username}, текст={user_text}") #Log received message
    # Сохраняем ID пользователя (или username) и текст в файл
    save_user_data(user_id, username, user_text)

    # Отправляем ответ пользователю
    await update.message.reply_text("Хорошо, ожидайте, с вами совсем скоро свяжется оператор.")

# Основная функция для запуска бота
def main() -> None:
    # Получаем токен
    TOKEN = get_token()

    # Создаём приложение Telegram-бота
    application = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    # Проверяем, выполняется ли скрипт как исполняемый файл (exe)
    is_exe = getattr(sys, 'frozen', False)

    if is_exe:
        # Скрываем консоль если токен уже есть (скрываем до запуска main())
        if os.path.exists("token.txt") and os.path.getsize("token.txt") > 0:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)  # 0 = SW_HIDE

        # Если да, создаем необходимые файлы и каталоги в текущей директории (где лежит exe)
        try:
            if not os.path.exists("token.txt"):
                open("token.txt", "w", encoding="utf-8").close()  # Создаем пустой файл token.txt
            if not os.path.exists("users_data.txt"):
                open("users_data.txt", "w", encoding="utf-8").close()  # Создаем пустой файл users_data.txt
        except Exception as e:
            logger.error(f"Ошибка при создании файлов для exe: {e}")


    main()