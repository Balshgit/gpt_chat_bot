from telegram import InlineKeyboardButton

from constants import BotStagesEnum

main_keyboard = (
    (
        InlineKeyboardButton("Обо мне", callback_data=str(BotStagesEnum.about_me)),
        InlineKeyboardButton("Веб версия", callback_data=str(BotStagesEnum.website)),
    ),
    (
        InlineKeyboardButton("Помощь", callback_data=str(BotStagesEnum.help)),
        InlineKeyboardButton("О боте", callback_data=str(BotStagesEnum.about_bot)),
    ),
)
