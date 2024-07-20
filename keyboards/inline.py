from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def inline_kb_builder(*,btns:dict[str,str],size:tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(
            InlineKeyboardButton(text=text,callback_data=data)
        )
    return keyboard.adjust(*size).as_markup()


def inline_calendar_builder (*, data:list[list],size:tuple[int]=(3,7)):
    keyboard = InlineKeyboardBuilder()
    for inside_list in data:
        keyboard.add(
            InlineKeyboardButton(text = str(inside_list[0]), callback_data=inside_list[1])
        )
    return keyboard.adjust(*size).as_markup()