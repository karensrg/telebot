import random
import telebot
import constants

bot = telebot.TeleBot(constants.token)
file = open("database.txt", "r").read()
idLib = {}
idList = file.split(";")
for elm in idList[:-1]:
    idLib[elm.split(":")[0]] = [int(elm.split(":")[1]), 0, {"numlist": [], "bet": 0, "right_num": 0}]


def user_name(last_update):
    if 'username' in last_update['from']:
        last_chat_name = last_update['from']['username']
    else:
        if ['last_name'] in last_update['from']:
            last_chat_name = f"{last_update['from']['first_name']}_" \
                             f"{last_update['from']['last_name']}"
        else:
            last_chat_name = last_update['from']['first_name']
    return last_chat_name


def bet(last_chat_id, balance, last_chat_name, last_chat_text):
    idLib[last_chat_id][2]["bet"] = int(last_chat_text)
    if idLib[last_chat_id][2]["bet"] <= balance:
        idLib[last_chat_id][2]["numlist"] = []
        while len(idLib[last_chat_id][2]["numlist"]) != 4:
            nm = str(random.choice(range(1, 101)))
            if nm not in idLib[last_chat_id][2]["numlist"]:
                idLib[last_chat_id][2]["numlist"].append(nm)
        keyboard = telebot.types.InlineKeyboardMarkup()
        numlist = idLib[last_chat_id][2]["numlist"]
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=numlist[0], callback_data=numlist[0]),
            telebot.types.InlineKeyboardButton(text=numlist[1], callback_data=numlist[1]))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=numlist[2], callback_data=numlist[2]),
            telebot.types.InlineKeyboardButton(text=numlist[3], callback_data=numlist[3]))
        bot.send_message(last_chat_id, "Ok, lets go!\nWhat number?", reply_markup=keyboard)
        idLib[last_chat_id][1] = 2
        idLib[last_chat_id][2]["right_num"] = random.choice(idLib[last_chat_id][2]["numlist"])
        print(f"{last_chat_name}'s right num is {idLib[last_chat_id][2]['right_num']}")
    else:
        bot.send_message(last_chat_id, f"Don't have enough balance!\nYour balance is {balance}")


def answercheck(last_chat_text, last_chat_id, name):
    if last_chat_text in idLib[last_chat_id][2]["numlist"]:
        if idLib[last_chat_id][2]["right_num"] == last_chat_text:
            idLib[last_chat_id][0] += idLib[last_chat_id][2]["bet"]
            print(f"{name} win's {idLib[last_chat_id][2]['bet']}, his balance is {idLib[last_chat_id][0]}.")
            bot.send_message(last_chat_id,
                             f"You Win!\nYour balance is {idLib[last_chat_id][0]}")
        else:
            idLib[last_chat_id][0] -= idLib[last_chat_id][2]["bet"]
            print(f"{name} lose's {idLib[last_chat_id][2]['bet']}, his balance is {idLib[last_chat_id][0]}.")
            bot.send_message(last_chat_id,
                             f"You Lose :(\nYour balance is {idLib[last_chat_id][0]}")
        idLib[last_chat_id][1] = 0
        updated_base = ""
        for key in idLib:
            updated_base += f"{key}:{idLib[key][0]}:{idLib[key][1]};"
        with open("database.txt", "w") as fl:
            fl.write(updated_base)
    else:
        bot.send_message(last_chat_id, "Number not in choices, try again ...")


def main():
    @bot.callback_query_handler(func=lambda call: True)
    def callbacker(callback):
        online_count = 0
        for user in idLib:
            if idLib[user][1] in [1, 2]:
                online_count += 1
        print(f"Users online: {online_count}")
        last_chat_id = str(callback.from_user.id)
        balance = idLib[last_chat_id][0]
        last_chat_text = str(callback.data)
        if 'username' in str(callback.from_user):
            last_chat_name = str(callback.from_user.username)
        else:
            if 'last_name' in str(callback.from_user):
                last_chat_name = f"{str(callback.from_user.first_name)}_" \
                                 f"{str(callback.from_user.last_name)}"
            else:
                last_chat_name = str(callback.from_user.first_name)
        if idLib[last_chat_id][1] == 1:
            bet(last_chat_id, balance, last_chat_name, last_chat_text)
        elif idLib[last_chat_id][1] == 2:
            answercheck(last_chat_text, last_chat_id, last_chat_name)

    @bot.message_handler(content_types=["text"])
    def handle_text(mess):
        last_update = mess.json

        # data of user
        last_chat_name = user_name(last_update)
        last_chat_text = last_update['text']
        last_chat_id = str(last_update['from']['id'])

        # new user registration
        if last_chat_id not in idLib:
            with open("database.txt", "a") as fl:
                new_data = f"{last_chat_id}:5000:{last_chat_name};"
                idLib[new_data.split(":")[0]] = [int(new_data.split(":")[1]), 0,
                                                 {"numlist": [], "bet": 0, "right_num": 0}]
                fl.write(new_data)

        # massage checking
        balance = idLib[last_chat_id][0]
        if last_chat_text == "💰Баланс":
            bot.send_message(last_chat_id, f"Your balance is {balance}")
        if idLib[last_chat_id][1] == 0:
            if last_chat_text == "/start":
                user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
                user_markup.row("💰Баланс", "🎰  Играть")
                bot.send_message(last_chat_id, "Hello, do you want lose some money?", reply_markup=user_markup)
            if last_chat_text == "🎰  Играть":
                if balance != 0:
                    idLib[last_chat_id][1] = 1
                    keyboardbet = telebot.types.InlineKeyboardMarkup()
                    keyboardbet.add(
                        telebot.types.InlineKeyboardButton(text="100", callback_data="100"),
                        telebot.types.InlineKeyboardButton(text="200", callback_data="200"),
                        telebot.types.InlineKeyboardButton(text="500", callback_data="500"))
                    keyboardbet.add(
                        telebot.types.InlineKeyboardButton(text="1000", callback_data="1000"),
                        telebot.types.InlineKeyboardButton(text="2000", callback_data="2000"),
                        telebot.types.InlineKeyboardButton(text="5000", callback_data="5000"))
                    bot.send_message(last_chat_id, f"How much will we play?", reply_markup=keyboardbet)
                else:
                    bot.send_message(last_chat_id, "Balance is 0 :(")
        elif idLib[last_chat_id][1] == 1:
            if last_chat_text.isnumeric():
                bet(last_chat_id, balance, last_chat_name, last_chat_text)
            elif last_chat_text != 'balance':
                bot.send_message(last_chat_id, "Wrong value, try again ...")
        elif idLib[last_chat_id][1] == 2:
            if last_chat_text.isnumeric():
                answercheck(last_chat_text, last_chat_id, last_chat_name)
            else:
                bot.send_message(last_chat_id, "Wrong value, try again ...")

    bot.polling(none_stop=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
