import time
from urllib.parse import urlparse
from aiogram.utils import executor
from config import *
from src.convert_qrcode_to_link import get_link_qr_code
from src.link_check import check_link
from aiogram.dispatcher import FSMContext
from utils import States
from keyboards import keyboard, keyboard_start, keyboard_menu
from all_bot_messages import error_qrcode, error_url, error_ban_url, instruction, greetings, output_table


# Функция для защиты от флуда
async def anti_flood(message: types.Message, *args, **kwargs):
    await message.delete()


@dp.message_handler(commands=['start'])
@dp.throttled(anti_flood, rate=1)
async def process_start_command(message: types.Message):
    await message.answer(greetings, reply_markup=keyboard_start)


@dp.message_handler(text='Начать 🚀')
@dp.throttled(anti_flood, rate=1)
async def start_menu(message: types.Message, state: FSMContext):
    await message.answer('Выберите <b>одно</b> из действий:\n\n1⃣ --> URL\n\n2⃣ --> QRCode', reply_markup=keyboard_menu)


@dp.message_handler(commands=["qr_code"])
@dp.throttled(anti_flood, rate=1)
async def cmd_qrcode(message: types.Message, state: FSMContext):
    await state.set_state(States.all()[0])
    await bot.send_message(message.from_user.id, "⬆️ Отправь <b>QR-код</b>, который хочешь проверить: ⬆️")


@dp.message_handler(commands=["url"])
@dp.throttled(anti_flood, rate=1)
async def cmd_url(message: types.Message, state: FSMContext):
    await state.set_state(States.all()[1])
    await bot.send_message(message.from_user.id, "📝 Напиши <b>URL</b>, который хочешь проверить: 📝")


@dp.message_handler(commands=["help"])
@dp.throttled(anti_flood, rate=1)
async def cmd_help(message: types.Message):
    await message.answer(instruction)


@dp.message_handler(text='Отправить ссылку 👀')
@dp.throttled(anti_flood, rate=1)
async def processing_url(message: types.Message, state: FSMContext):
    await state.set_state(States.all()[1])
    await bot.send_message(message.from_user.id, "Напиши <b>URL</b>, который хочешь проверить: ", reply_markup=keyboard)


@dp.message_handler(text='Отправить QR-Code 📩')
@dp.throttled(anti_flood, rate=1)
async def processing_qr_code(message: types.Message, state: FSMContext):
    await state.set_state(States.all()[0])
    await bot.send_message(message.from_user.id, "Отправь <b>QR-код</b>, который хочешь проверить: ",
                           reply_markup=keyboard)


@dp.message_handler(text='Назад ↩️', state=States.QR_STATE[0])
@dp.throttled(anti_flood, rate=1)
async def processing_qr_code(message: types.Message, state: FSMContext):
    await state.reset_state()
    await message.answer('🔄 <b>ИДЁТ ПЕРЕНАПРАВЛЕНИЕ В ГЛАВНОЕ ОКНО, ПОЖАЛУЙСТА, ПОДОЖДИТЕ...</b> 🔄')
    time.sleep(0.5)
    await message.answer("Вы в главном меню, выберите <b>одно</b> из действий:\n\n1⃣ --> URL\n\n2⃣ --> QRCode",
                         reply_markup=keyboard_menu)


@dp.message_handler(text='Назад ↩️', state=States.URL_STATE[0])
@dp.throttled(anti_flood, rate=1)
async def processing_url(message: types.Message, state: FSMContext):
    await state.reset_state()
    await message.answer('🔄 <b>ИДЁТ ПЕРЕНАПРАВЛЕНИЕ В ГЛАВНОЕ ОКНО, ПОЖАЛУЙСТА, ПОДОЖДИТЕ...</b> 🔄')
    time.sleep(0.5)
    await message.answer("Вы в главном меню, выберите <b>одно</b> из действий:\n\n1⃣ --> URL\n\n2⃣ --> QRCode",
                         reply_markup=keyboard_menu)


@dp.message_handler(state=States.URL_STATE[0])
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
        await state.set_state(States.all()[1])
    except:
        try:
            parsed_url = urlparse(url)
            domain = 'http://' + parsed_url.netloc + '/'
            result = check_link(domain)
            time.sleep(1)
            await message.reply(error_ban_url, parse_mode='HTML', reply=False)
            time.sleep(1)
            await message.reply(output_table(domain=domain, result=result), parse_mode="HTML", reply=False)
            await state.set_state(States.all()[1])
        except:
            await message.reply(error_url, parse_mode='HTML', reply=False)
            await state.set_state(States.all()[1])


@dp.message_handler(state=States.QR_STATE[0], content_types=['photo'])
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


@dp.message_handler(content_types=['text'])
@dp.throttled(anti_flood, rate=1)
async def handle_text(message: types.Message):
    await message.answer("Такой команды не существует. Используйте команду /help, чтобы узнать доступные команды.")


@dp.message_handler(state=States.QR_STATE[0], content_types=['text'])
@dp.throttled(anti_flood, rate=1)
async def check_message_qrcode(message: types.Message, state: FSMContext):
    if message.text:
        await message.answer("Вы в режиме проверки QR-Code, чтобы бот работал ему надо скинуть фотографию")
        await state.set_state(States.all()[0])
    else:
        await state.set_state(States.all()[0])
        pass


@dp.message_handler(state=States.URL_STATE[0], content_types=['photo'])
@dp.throttled(anti_flood, rate=1)
async def check_message_qrcode(message: types.Message, state: FSMContext):
    if message.photo:
        await message.answer("Вы в режиме проверки ссылок, чтобы бот работал ему надо написать рабочую ссылку")
        await state.set_state(States.all()[0])
    else:
        await state.set_state(States.all()[0])
        pass

if __name__ == '__main__':
    executor.start_polling(dp)
