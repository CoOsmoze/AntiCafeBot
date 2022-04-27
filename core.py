from menus import *
from models import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def is_user_exist(id):
    try:
        user = User.get(id = id)
        if not user.id:
            raise DoesNotExist
        return True
    except DoesNotExist:
        return False


def checkuser(function):
    def check(update, context):
        if not is_user_exist(id = update.message.from_user.id):
            if update.message.from_user.username:
                username = update.message.from_user.username
            else:
                username = 'none'

            user = User.create(
                id = update.message.from_user.id,
                status='user',
                name = update.message.from_user.first_name,
                username = username,
            )
            user.save()
        function(update, context)
    return check

def checkadmin(function):
    def check(update, context):
        user = User.get(id=update.message.from_user.id)
        if user.status == 'admin':
            function(update, context)
    return check


def get_profile(user):
    if user:
        text =  f"<b>Профиль</b>\n" \
                f"Id: <code>{user.id}</code>\n" \
                f"Статус: {user.status}\n" \
                f"Имя: {user.name}\n" \
                f"@{user.username}"
        return text

def get_user_buttons(user):
    if user:
        buttons =[InlineKeyboardButton('Бронь', callback_data=f"@userorder@{user.id}")]
        return InlineKeyboardMarkup(build_menu(buttons, n_cols=1))

def get_user_order(user, admin=False):
    buttons = []
    text = ''
    prefix = ''
    if admin:
        prefix = 'admin'
    for order in user.order:
        text += f"Бронь #<code>{order.id}</code>\n"
        buttons.append(InlineKeyboardButton(f"Бронь {order.id}", callback_data=f'@{prefix}order@{order.id}'))
    reply_markup = InlineKeyboardMarkup(build_menu(buttons, n_cols=1))

    user_order = namedtuple('menu', 'text reply_markup')
    user_order.text = text
    user_order.reply_markup = reply_markup
    return user_order

def get_order(order, user=False):
    if order:
        text = ''
        if user:
            user = User.get(id=order.user)
            text += f"Пользователь #<code>{user.id}</code> @{user.username}\n"

        text += f"<b>Бронь #{order.id}</b>\n\n"\
                f"Статус: <i>{order.status}</i>\n"\
                f"Телефон: <i>{order.phone}</i>\n\n"

        order_text = f"Комната:\n"
        room = Room.get(id=order.room)
        total_price = int(room.price) + (int(order.count_people) * 500)
        order_text += f"<i>{room.name}</i>\n" \
                    f"<i>цена комнаты: {room.price}p/</i>\n" \
                    f"<i>кол-во гостей: {order.count_people}</i>\n" \
                    f"<i>Итоговая цена: {total_price}p.</i>"
    
        text += order_text
        return text

def get_order_buttons(order, user = False):
    buttons = []
    if user:
        if order.status == 'В обработке':
            buttons.append(InlineKeyboardButton('Подтвердить бронь', callback_data=f"@confirm@{order.id}"))
        buttons.append(InlineKeyboardButton('Удалить бронь', callback_data=f"@delete@{order.id}"))
        return InlineKeyboardMarkup(build_menu(buttons, n_cols=1))
    else:
        buttons.append(InlineKeyboardButton('Удалить бронь', callback_data=f"@userdeleteorder@{order.id}"))
        return InlineKeyboardMarkup(build_menu(buttons, n_cols=1))
