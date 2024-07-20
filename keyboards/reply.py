from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb= ReplyKeyboardMarkup(
    keyboard=  [
        [
            KeyboardButton(text="О нас"),
            KeyboardButton(text="Наши продукты")
         ],
        [
            KeyboardButton(text="FAQ")
        ],
        [
            KeyboardButton(text="Записаться")
        ]
    ],
    resize_keyboard=True
)

admin_kb = ReplyKeyboardMarkup(
    keyboard= [
        [
            KeyboardButton(text="Добавить товар"),
            KeyboardButton(text="Продукты")
         ],
        [
            KeyboardButton(text="Добавить мастера"),
            KeyboardButton(text="Мастеры")
        ],
        [
            KeyboardButton(text="Создать рассылку"),
            KeyboardButton(text="Назад")
        ],
        [
            KeyboardButton(text="Справка")
        ]
    ],
    resize_keyboard=True
)

send_phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отправить номер телефона☎️", request_contact=True)
        ],
        [
            KeyboardButton(text="Нет")
        ]
    ],
    resize_keyboard=True
)