import calendar
import datetime
import locale
import os

from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart, StateFilter, or_f, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import async_session

from ORM.ORM_Query import orm_get_customers_id, orm_add_customer, orm_update_customer, orm_get_products, \
    orm_get_product, orm_get_masters, orm_add_customer_phone, orm_get_customer_phone, orm_get_customer
from filters.chat_type import ChatTypeFilter
from keyboards.inline import inline_kb_builder, inline_calendar_builder
from keyboards.reply import start_kb, send_phone_kb

load_dotenv(find_dotenv())

supergroup_id = os.getenv("supergroup_id")

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


cal = calendar.TextCalendar()


@user_private_router.message(CommandStart())
async def start(message:types.Message,session:async_session):
    if message.from_user.id not in await orm_get_customers_id(session):
        data = {
            "first_name": message.from_user.first_name,
            "user_id": message.from_user.id,
        }
        await orm_add_customer(session, data)

    await message.answer("Привет!👋\nМеня зовут KateEyesBot."
                         " Я помогаю узнать кто мы такие, ознакомиться с нашими продуктами,"
                         " а еще я отвечвю на часто задаваемые вопросы\n"
                         "Так же прямо здесь вы можете оформить заявку и наш менеджер свяжется с вами в ближайшее время\n"
                         "Начнем ?)...🚀",
                         reply_markup=start_kb)


@user_private_router.message(or_f((Command("about")),(F.text.lower() == "о нас")))
async def about_us(message:types.Message):
    await message.answer("Мы сеть салонов KateEyes, и мы пытаемся сделать мир красивее и лучше.\n"
                         "Мы вдохновляемся тем, что именно красота спасет мир и именно в ощущении "
                         "прекрасного находится связывающее всех людей звено❤️‍🔥\n"
                         "Наша команда молодых, красивых и квалифицированных специалистов 👩‍🎓"
                         "помогает людям приобщиться к этому принципу и ощутить его на себе\n"
                         "Присоединяйтесь, записывайтесь к нам на прием и главное - не бойтесь быть собой! 💋")

@user_private_router.message(or_f((Command("products")),(F.text.lower() == "наши продукты")))
async def our_products(message:types.Message,session:async_session):
        for product in await orm_get_products(session):
            await message.answer(f"{product.name}\n{product.description}\nPrice:{round(product.price,2)}$")


@user_private_router.message(or_f((Command("FAQ")),(F.text.lower() == "faq")))
async def our_products(message:types.Message):
        await message.answer("Я еще только учусь и вопросов мне еще не задавли)\n"
                             "Обещаю в будущем стать умнее и больше вам помогать🥺")


##########FSM Make order##########


class MakeOrder(StatesGroup):
    phone = State()
    add_phone = State()
    products = State()
    day = State()
    all_right = State()


############### Функция формирования календаря ##########################
############### Возвращает список списков с неделями ####################
def get_calendar(year:int, month:int):
    locale.setlocale(locale.LC_TIME, 'ru')

    calendar_obj = cal.monthdayscalendar(year,month)

    month_name_obj = datetime.datetime.strptime(str(month), "%m")
    month_name = month_name_obj.strftime("%B")

    days_list = []

    days_list.append(["<-", f"beforemonth_{year}_{month}"])
    days_list.append([month_name," "])
    days_list.append(["->",f"nextmonth_{year}_{month}"])


    days_list.append(["Пн"," "])
    days_list.append(["Вт"," "])
    days_list.append(["Ср"," "])
    days_list.append(["Чт"," "])
    days_list.append(["Пт"," "])
    days_list.append(["Сб"," "])
    days_list.append(["Вс"," "])


    for week in calendar_obj:
        week[:] = [day if day!=0 else " " for day in week]

    for week in calendar_obj:
        for day in week:
            if day != " ":
                days_list.append([str(day),f"day_{month}_{day}"])
            else:
                days_list.append([str(day), f"falseday_"])

    days_list.append(["Назад", f"beforestep_{MakeOrder.products}"])

    return days_list




@user_private_router.callback_query(F.data.startswith("nextmonth_"))
async def get_next(callback:types.CallbackQuery):

    date_list = callback.data.split("_")[1:]


    if int(date_list[1]) == 12:
        year = int(date_list[0])+1
        month = 1
    else:
        year = int(date_list[0])
        month = int(date_list[1])+1

    btns = get_calendar(year,month)

    await callback.message.edit_reply_markup(
                                  reply_markup=inline_calendar_builder(
                                      data = btns,
                                  )
                                  )



@user_private_router.callback_query(F.data.startswith("beforemonth_"))
async def get_before(callback:types.CallbackQuery):

    date_list = callback.data.split("_")[1:]


    if int(date_list[1]) == 1:
        year = int(date_list[0])-1
        month = 12
    else:
        year = int(date_list[0])
        month = int(date_list[1])-1

    btns = get_calendar(year,month)

    await callback.message.edit_reply_markup(
                                  reply_markup=inline_calendar_builder(
                                      data = btns,
                                  )
                                  )

##############  Возвращает на старницу выбора услуги (кнопка Назад) ################
@user_private_router.callback_query(StateFilter("*"), F.data.startswith("beforestep_"))
async def come_back(callbak: types.CallbackQuery, state: FSMContext,session:async_session):
    btns = {}
    for product in await orm_get_products(session):
        btns[product.name] = f"product_{product.id}"
    btns["Выйти"] = f"out_"
    await callbak.message.edit_text("Выберите услугу:")
    await callbak.message.edit_reply_markup(
                         reply_markup=inline_kb_builder(
                             btns=btns
                         ))
    await state.set_state(MakeOrder.products)


#####################  Кнопка выйти (обнуляет состояние) ########################
@user_private_router.callback_query(MakeOrder.products, F.data.startswith("out_"))
async def out(callback:types.CallbackQuery,session:async_session,state:FSMContext):
    await callback.message.delete()
    await callback.message.answer("Будем ждать вас)\n",reply_markup=start_kb)

    await state.clear()



###########start###########



@user_private_router.message(StateFilter(None), F.text.lower() == "записаться")
async def review_phone (message:types.Message,session:async_session,state:FSMContext):
    ###############Проверяем наличе юзера в базе#################
    ###############Т.к в случае, если слетят БД,#################\
    ###############у пользователя останется начатый диалог#################
    ###############а в базе его не будет#################
    if message.from_user.id not in await orm_get_customers_id(session):
        data = {
            "first_name": message.from_user.first_name,
            "user_id": message.from_user.id,
        }
        await orm_add_customer(session, data)
    #################### Проверям наличие телефона #################################
    customer_phone = await orm_get_customer_phone(session, message.from_user.id)

    if customer_phone != [None] and customer_phone != []:
        btns = {}
        for product in await orm_get_products(session):
            btns[product.name] = f"product_{product.id}"
        btns["Выйти"] = f"out_"
        await message.answer(f"Выберите услугу:",
                             reply_markup=inline_kb_builder(
                                 btns=btns
                             ))
        await state.set_state(MakeOrder.products)
    else :
        await message.answer("Для записи нам необходим ваш номер телефона\nПожалуйста, поделитесь номером, "
                             "чтобы мы могли уточнить детали вашей записи",reply_markup=send_phone_kb)
        await state.set_state(MakeOrder.add_phone)



@user_private_router.callback_query(StateFilter("*"), F.data.startswith("want_"))
async def want_review_phone(callback:types.CallbackQuery,session:async_session,state:FSMContext):

    ###############Проверяем наличе юзера в базе#################
    ###############Т.к в случае, если слетят БД,#################\
    ###############у пользователя останется начатый диалог#################
    ###############а в базе его не будет#################
    if callback.from_user.id not in await orm_get_customers_id(session):
        data = {
            "first_name": callback.from_user.first_name,
            "user_id": callback.from_user.id,
        }
        await orm_add_customer(session, data)
    #################### Проверям наличие телефона #################################
    customer_phone = await orm_get_customer_phone(session, callback.from_user.id)

    if customer_phone != [None] and customer_phone != []:
        btns = {}
        for product in await orm_get_products(session):
            btns[product.name] = f"product_{product.id}"
        btns["Выйти"] = f"out_"
        await callback.message.answer(f"Выберите услугу:",
                             reply_markup=inline_kb_builder(
                                 btns=btns
                             ))
        await state.set_state(MakeOrder.products)
    else :
        await callback.message.answer("Для записи нам необходим ваш номер телефона\nПожалуйста, поделитесь номером, "
                             "чтобы мы могли уточнить детали вашей записи",reply_markup=send_phone_kb)
        await state.set_state(MakeOrder.add_phone)



@user_private_router.message(MakeOrder.add_phone, F.text.lower()=="нет")
async def dont_add_phone (message:types.Message, state:FSMContext):

    await message.answer("Нам жаль, что вам чем либо не подошел наш сервис 😢\nОбязательно возвращайтесь к нам снова",
                         reply_markup=start_kb)
    await state.clear()



@user_private_router.message(MakeOrder.add_phone, F.contact)
async def add_phone (message:types.Message,session:async_session,state:FSMContext):

    number = {
        "phone_number": message.contact.phone_number
    }
    await orm_add_customer_phone(session,number,message.from_user.id)

    await message.answer("Отлично!\nДанные успешно обновлены\nНажмите кнопку Записаться ⬇️",reply_markup=start_kb)

    await state.set_state(MakeOrder.phone)


@user_private_router.message(MakeOrder.phone,F.text.lower() == "записаться")
async def choise_product(message: types.Message, state: FSMContext, session:async_session):

    btns = {}
    for product in await orm_get_products(session):
        btns[product.name] = f"product_{product.id}"
    btns["Выйти"] = f"out_"
    await message.answer(f"Выберите услугу:",
                         reply_markup=inline_kb_builder(
                         btns=btns
                         ))
    await state.set_state(MakeOrder.products)



@user_private_router.callback_query(MakeOrder.products, F.data.startswith("product_"))
async def review_choise_product(callbak:types.CallbackQuery,state:FSMContext,session:async_session):

    product_id = int(callbak.data.split('_')[-1])

    product_obj = await orm_get_product(session,product_id)
    product_name = product_obj.name
    product_description = product_obj.description

    await callbak.message.edit_text(f"{product_name}\n{product_description}",
                                 reply_markup=inline_kb_builder(
                                     btns={
                                         "Выбрать":f"choiseproduct_{product_name}",
                                         "Назад" : f"beforestep_"
                                     }
                                 ))
    await state.set_state(MakeOrder.day)



@user_private_router.callback_query(MakeOrder.day, F.data.startswith("choiseproduct_"))
async def choise_day(callback:types.CallbackQuery, state: FSMContext, session: async_session):

    await state.update_data(product_to_order = callback.data.split("_")[-1])

    date = str(datetime.datetime.now())

    date = date.split("-")

    days_list = get_calendar(int(date[0]), int(date[1]))

    await callback.message.edit_text("Пожалуйста, выберите ориентрововчный день для записи")
    await callback.message.edit_reply_markup(reply_markup=inline_calendar_builder(

    data = days_list
    ))
    await state.set_state(MakeOrder.day)




@user_private_router.callback_query(MakeOrder.day, F.data.startswith("day_"))
async def all_right(callback:types.CallbackQuery,session:async_session,state:FSMContext):

    await state.update_data(day_to_order=callback.data.split("_")[2])
    await state.update_data(month_to_order=callback.data.split("_")[1])

    data = await state.get_data()

    product_name= data["product_to_order"]

    month_name_obj = datetime.datetime.strptime(data["month_to_order"], "%m")
    month_name = month_name_obj.strftime("%B")

    await callback.message.edit_text(f"Отлично!\nИтак, ваша запись:\n"
                                     f"{product_name},  {month_name} {data['day_to_order']}",)
    await callback.message.edit_reply_markup(
                                  reply_markup=inline_kb_builder(
                                      btns={
                                          "Верно":f"right_",
                                          "Нет":f"notright_"
                                      }
                                  ))


    await state.set_state(MakeOrder.phone)

@user_private_router.callback_query(MakeOrder.phone, F.data.startswith("right_"))
async def finale_right(callback:types.CallbackQuery,session:async_session,state:FSMContext,bot:Bot):

    data = await state.get_data()

    await orm_update_customer(session,data,callback.from_user.id)

    product_name= data["product_to_order"]

    month_name_obj = datetime.datetime.strptime(data["month_to_order"], "%m")
    month_name = month_name_obj.strftime("%B")

    day = data['day_to_order']

    phone_obj = await orm_get_customer_phone(session,callback.from_user.id)
    phone_str = "".join([i if i not in ["[, ], ', "] else "" for i in phone_obj])
    phone = "+" + phone_str[0] + "-" + phone_str[1:]

    await bot.send_message(text=f"Имя : {callback.from_user.first_name}\nUsername : {callback.from_user.username}\nНомер телефона {phone}\n\n"
                                f"Услуга : {product_name}\nДата : {month_name} {day}\n",
                                chat_id=supergroup_id)

    await callback.message.answer("Отлично!\nВ ближайшее время с вами свяжется наш менеджер для уточнения деталей")
    await state.clear()


@user_private_router.callback_query(MakeOrder.phone, F.data.startswith("notright_"))
async def finale_notright(callback:types.CallbackQuery,session:async_session,state:FSMContext):

    await callback.message.answer("Чтож, давайте начнем сначала")

    btns = {}
    for product in await orm_get_products(session):
        btns[product.name] = f"product_{product.id}"
    btns["Выйти"] = f"out_"
    await callback.message.answer(f"Выберите услугу:",
                         reply_markup=inline_kb_builder(
                             btns=btns
                         ))
    await state.set_state(MakeOrder.products)