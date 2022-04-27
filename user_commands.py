import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler

from menus import *
from core import *

@checkuser
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello")


@checkuser
def help(update, context):
    text = '<b>Список комманд:</b>\n'\
          '<code>/profile</code> - посмотреть свой профиль\n'\
          '<code>/neworder</code> - арендовать комнату\n'\
          '<code>/myorders</code> - посмотреть свою бронь\n'

    menu = get_menu('main')

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             reply_markup=menu.reply_markup,
                             parse_mode=ParseMode.HTML)

@checkuser
def all_messages(update, context):
    text = "Я не знаю как на это ответить. Воспользуйтесь разделом 'Помощь' (/help)"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             reply_markup=get_menu('main').reply_markup,
                             parse_mode=ParseMode.HTML)


@checkuser
def my_profile(update, context):
    user = User.get(id = update.message.from_user.id)

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=get_profile(user),
                             parse_mode=ParseMode.HTML)


def cancel(update, context):
    text = "Бронирование отменено"
    context.bot.send_message(chat_id = update.effective_chat.id, 
                            text = text,
                            parse_mode = ParseMode.HTML)
    return ConversationHandler.END

def new_order(update, context):

    text = "Выберете комнату\n"

    rooms = Room.select()

    buttons = []
    text = "<b>Название\t Цена\t вместимость</b>\n"
    for room in rooms:
        text += f"{room.name}: {room.price}p. - {room.max_people_count}чел.\n"
        buttons.append(InlineKeyboardButton(room.name, callback_data= f'@order_room@{room.id}'))

    context.user_data['state'] = 1

    menu = InlineKeyboardMarkup(build_menu(buttons=buttons, n_cols=1, footer_buttons=None))
    context.bot.send_message(chat_id = update.effective_chat.id, text = text, parse_mode = ParseMode.HTML, reply_markup = menu)

    return 0 


def count_people(update, context):
    text = "Укажите количество гостей"
    context.bot.send_message(chat_id = update.effective_chat.id, text = text, parse_mode = ParseMode.HTML)
    context.user_data['state'] = 2
    return 1


def phone(update, context):
    context.user_data['count_people'] = update.message.text
    room =Room.get(id = ','.join(context.user_data['room']))
    if int(context.user_data['count_people']) > int(room.max_people_count):
        text = "Ошибка. Вас слишком много для этой комнаты"
        context.bot.send_message(chat_id = update.effective_chat.id, text = text, parse_mode = ParseMode.HTML)
        return count_people(update, context)
    
    text = "Укажите телефон"
    context.bot.send_message(chat_id = update.effective_chat.id, text = text, parse_mode = ParseMode.HTML)
    context.user_data['state'] = 3
    return 2


def finish_order(update, context):
    context.user_data['phone'] = update.message.text

    order = Order(
        user = User.get(id = update.message.from_user.id),
        room =','.join(context.user_data['room']),
        count_people = context.user_data['count_people'],
        phone = context.user_data['phone']
    )
    order.save()

    text = get_order(order)
    context.bot.send_message(chat_id = update.effective_chat.id, text = text, parse_mode = ParseMode.HTML)
    context.user_data['state'] = ''

    admins = User.select().where(User.status == 'admin')
    for admin in admins:
        context.bot.send_message(
            chat_id=admin.id,
            text=f"<b>Поступил новый заказ!</b>\n" + get_order(order),
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=get_order_buttons(order)
        )

    context.user_data.clear()

    return ConversationHandler.END

@checkuser
def my_order(update, context):
    user = User.get(id=update.message.from_user.id)
    if user.order:
        text = "<b>Ваша бронь:</b>\n"
        order = get_user_order(user)
        text += order.text
        reply_markup = order.reply_markup
    else:
        text = "У вас нет брони"
        reply_markup = None

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=reply_markup
    )