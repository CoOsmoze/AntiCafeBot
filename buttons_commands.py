from telegram.ext import ConversationHandler
import telegram
from menus import *
from models import *
from core import *
from user_commands import new_order


def btn_handler(update, context):
    query = update.callback_query
    data = query.data.split("@")[1:]

    buttons = []
    buttons.append(InlineKeyboardButton("Арендовать", callback_data = "@doneorder"))

    footer_keyboard = [
        InlineKeyboardButton('Назад', callback_data='@exit')
    ]
    menu = InlineKeyboardMarkup(build_menu(buttons=buttons, n_cols=1, footer_buttons=footer_keyboard))


    if data[0] == 'exit':
        new_order(update, context) 

    if data[0] == 'doneorder':
        return 1

    if data[0] == 'order_room':
        user = User.get(id=query.message.chat.id)
        if user.order:
            context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="У вас уже есть бронь"
            )
            return ConversationHandler.END

        room = Room.get(id = data[1])
        context.user_data['room'] = [data[1]]
        context.bot.send_photo(chat_id=update.effective_chat.id,
                             caption=f"Вы выбрали комнату: {room.name}\n",
                             photo = open(f"media/room{data[1]}.jpg", 'rb',),
                             reply_markup = menu)

    if data[0] == 'order':
        order = Order.get(id=data[1])
        text = get_order(order)
        reply_markup = get_order_buttons(order)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.HTML,reply_markup=reply_markup)

    if data[0] == 'adminorder':
        order = Order.get(id=data[1])
        text = get_order(order, True)
        reply_markup = get_order_buttons(order, True)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    if data[0] == 'confirm':
        order = Order.get(id=int(data[1]))
        order.status = 'Принят'
        order.save()

        context.bot.edit_message_reply_markup(
            chat_id=update.effective_chat.id,
            message_id=query.message.message_id,
            reply_markup=get_order_buttons(order)
        )

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы успешно приняли бронь!',
            parse_mode=telegram.ParseMode.HTML,
        )
        context.bot.send_message(
            chat_id=order.user.id,
            text=f'Бронь {order.id} принята. Ждем вас!',
            parse_mode=telegram.ParseMode.HTML,
        )


    if data[0] == 'delete':
        order = Order.get(id=int(data[1]))

        context.bot.edit_message_reply_markup(
            chat_id=update.effective_chat.id,
            message_id=query.message.message_id,
            reply_markup=None
        )

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы успешно отменили бронь!',
            parse_mode=telegram.ParseMode.HTML,
        )
        context.bot.send_message(
            chat_id=order.user.id,
            text=f'Ваша бронь #{order.id} отменена!',
            parse_mode=telegram.ParseMode.HTML,
        )
        order.delete_instance()

    if data[0] == 'userdeleteorder':
        order = Order.get(id=int(data[1]))
        context.bot.edit_message_reply_markup(
            chat_id=update.effective_chat.id,
            message_id=query.message.message_id,
            reply_markup=None
        )
        context.bot.send_message(
            chat_id=order.user.id,
            text=f'Ваша бронь #{order.id} отменена!',
            parse_mode=telegram.ParseMode.HTML,
        )
        order.delete_instance()

    if data[0] == 'userorder':
        user = User.get(id=data[1])
        if user:
            order = get_user_order(user, True)
            text = f' Бронь пользовтеля #<code>{user.id}</code>:\n' + order.text
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                parse_mode=telegram.ParseMode.HTML,
                reply_markup=order.reply_markup
            )


