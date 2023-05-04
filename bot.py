import time
from urllib.parse import urlparse
from aiogram.utils import executor
from config import *
from src.convert_qrcode_to_link import get_link_qr_code
from src.link_check import check_link
from aiogram.dispatcher import FSMContext
from utils import States
from keyboards import keyboard_start
from all_bot_messages import *


# Функция для защиты от флуда
async def anti_flood(message: types.Message, *args, **kwargs):
    await message.delete()


# Обработчик команды /start
# Переводит бота в состояние URL_STATE и отправляет приветственное сообщение
@dp.message_handler(commands=['start'], state='*')
@dp.throttled(anti_flood, rate=1)
async def process_start_command(message: types.Message, state: FSMContext):
    await state.set_state(States.all()[0])
    await message.answer(greetings, reply_markup=keyboard_start)


# Обработчик текста "Перезапуск Бота🚀"
# Переводит бота в состояние URL_STATE и отправляет сообщение с просьбой отправить QR-код или ссылку
@dp.message_handler(text='Перезапуск Бота🚀', state='*')
@dp.throttled(anti_flood, rate=1)
async def start_menu(message: types.Message, state: FSMContext):
    await state.set_state(States.all()[0])
    await message.answer('Отправьте боту <b>QR-Code</b> или <b>ссылку</b>:')


# Обработчик команды /help
# Отправляет инструкцию по использованию бота
@dp.message_handler(commands=["help"], state='*')
@dp.throttled(anti_flood, rate=1)
async def cmd_help(message: types.Message):
    await message.answer(instruction)


# Обработчик текстовых сообщений
# Получает URL-адрес от пользователя, проверяет его на наличие вредоносного содержимого и отправляет результат проверки
@dp.message_handler(state=States.URL_STATE[0], content_types=['text'])
@dp.throttled(anti_flood, rate=1)
async def solution_url(message: types.Message, state: FSMContext):
    url = message.text
    await message.reply("🔅 Идёт проверка ссылки... 🔅", reply=False)
    time.sleep(1)
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.scheme + '://' + parsed_url.netloc + '/'
        result = check_link(domain)
        time.sleep(1)
        await message.reply(output_table(domain=domain, result=result), reply=False)
        await state.set_state(States.all()[0])
    except:
        try:
            parsed_url = urlparse(url)
            domain = 'http://' + parsed_url.netloc + '/'
            result = check_link(domain)
            time.sleep(1)
            await message.reply(error_ban_url, parse_mode='HTML', reply=False)
            time.sleep(1)
            await message.reply(output_table(domain=domain, result=result), parse_mode="HTML", reply=False)
            await state.set_state(States.all()[0])
        except:
            await message.reply(error_url, parse_mode='HTML', reply=False)
            await state.set_state(States.all()[0])


# Обработчик фото-сообщений
# Получает изображение QR-кода от пользователя, извлекает URL-адрес из него,
# проверяет его на наличие вредоносного содержимого и отправляет результат проверки
@dp.message_handler(state=States.URL_STATE[0], content_types=['photo'])
@dp.throttled(anti_flood, rate=1)
async def solution_qrcode(message: types.Message, state: FSMContext):
    await message.reply("⬇️ Изображение скачивается... ⬇️", reply=False)
    time.sleep(1)
    user_id = message.from_user.id
    await message.photo[-1].download(f'src/img_{user_id}.png')
    try:
        url = get_link_qr_code(user_id=user_id)
        await message.reply("🔅 Идёт проверка ссылки... 🔅", reply=False)
        time.sleep(1)
        try:
            time.sleep(1)
            parsed_url = urlparse(url)
            domain = parsed_url.scheme + '://' + parsed_url.netloc + '/'
            result = check_link(domain)
            await message.reply(output_table(domain=domain, result=result), reply=False)
            await state.set_state(States.all()[0])
        except:
            try:
                time.sleep(1)
                parsed_url = urlparse(url)
                domain = 'http://' + parsed_url.netloc + parsed_url.path
                result = check_link(domain)
                await message.reply(error_ban_url, parse_mode='HTML', reply=False)
                time.sleep(1)
                await message.reply(output_table(domain=domain, result=result), parse_mode='HTML', reply=False)
                await state.set_state(States.all()[0])
            except:
                await message.reply("<b>⚠️ Ссылка в QR-коде некорректная... ⚠️</b>", parse_mode='HTML', reply=False)
                await state.set_state(States.all()[0])
    except:
        await message.reply(error_qrcode, parse_mode='HTML', reply=False)
        await state.set_state(States.all()[0])


# Запуск бота в режиме polling
if __name__ == '__main__':
    executor.start_polling(dp)
