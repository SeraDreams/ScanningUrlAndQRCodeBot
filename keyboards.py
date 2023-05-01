from aiogram import types


""" -------КЛАВИАТУРЫ------- """
"1"
Start = 'Начать 🚀'
keyboard_start = types.ReplyKeyboardMarkup(resize_keyboard=True).add(Start)
"2"
URL, QRcode = 'Отправить ссылку 👀', 'Отправить QR-Code 📩'
keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True).add(URL, QRcode)
"3"
Backup = 'Назад ↩️'
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(Backup)