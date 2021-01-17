import time
import telebot  # pip install pyTelegramBotAPI
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot_admin = []
bot_session = {}
bot_user_session = []
TOKEN = #机器人TOKEN
ADMIN_GROUP_ID = #管理频道ID
PUBLIC_CHANNEL= #频道ID
func1 = [{
    "S1_1": "张",
    "S1_2": "赵",
    "S1_3": "王"
}, {
    "S2_1": "小",
    "S2_2": "子",
    "S2_3": "少"
}]


def bot_sub1():
    bot = telebot.TeleBot(TOKEN)
    print(func1)
    bot_info = bot.get_me()
    print(bot_info)

    @bot.message_handler(commands=['function1'])
    def bot_function1(msg):
        try:
            if msg.chat.id < 0:
                return
            if msg.chat.id in bot_session:
                del bot_session[msg.from_user.id]
            bot_session[msg.from_user.id] = {"mode": "func1", "status": "start", "data": {}}
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("开始功能", callback_data="func1:button:-1:start"))
            bot.reply_to(msg, "功能演示1", reply_markup=markup)
        except Exception as e:
            print(e)

    @bot.callback_query_handler(func=lambda message: True)
    def callback_query(msg):
        try:
            if msg.from_user.id < 0:
                return
            if msg.from_user.id not in bot_session:
                bot.edit_message_text("操作错误", chat_id=msg.from_user.id, message_id=msg.message.message_id)
                return
            callback_data = msg.data.split(':')
            # print(callback_data)
            if callback_data[0] == 'func1' and bot_session[msg.from_user.id]["mode"] == "func1":
                if callback_data[1] == "button":
                    select_id = int(callback_data[2])  # 获取操作id，默认开始为-1
                    markup_list = [[]]

                    if callback_data[3] not in ['start', 'back', 'finish']:
                        bot_session[msg.from_user.id]["data"][select_id] = callback_data[3]
                    result_str = get_select_str(func1, bot_session[msg.from_user.id]["data"])
                    if select_id == -1:  # 特殊操作检测
                        if callback_data[3] == 'finish':
                            if len(bot_session[msg.from_user.id]["data"]) != len(func1):
                                bot.edit_message_text("内部错误", chat_id=msg.from_user.id,
                                                      message_id=msg.message.message_id)
                            else:
                                bot.edit_message_text("你发送的为 {}".format(result_str), chat_id=msg.from_user.id,
                                                      message_id=msg.message.message_id)
                                admin_send_text = '用户id:{}\n'.format(msg.from_user.id) #在管理员频道中，这条消息获取用户的ID
                                admin_send_text += '用户:[{} {}](tg://user?id={}) \n'.format(msg.from_user.first_name,
                                                                                           msg.from_user.last_name,
                                                                                           msg.from_user.id)
                                admin_send_text += '发送的内容为:{}\n'.format(result_str)
                                bot_session[msg.from_user.id]["text"] = admin_send_text  # 转发频道消息
                                fwd_msg = bot.send_message(ADMIN_GROUP_ID, admin_send_text,
                                                           parse_mode='Markdown',
                                                           disable_web_page_preview=True)
                                admin_send_text2 = "是否采用"
                                markup = InlineKeyboardMarkup()
                                markup.add(InlineKeyboardButton('采用', callback_data='func1:group:receive'),
                                           InlineKeyboardButton('拒绝', callback_data='func1:group:reject'))
                                bot.reply_to(fwd_msg, admin_send_text2, reply_markup=markup)
                            return
                    if select_id + 1 == len(func1):  # 当func1循环完成
                        # print(result_str)
                        markup_list[0].append(InlineKeyboardButton('是否确认发送【{}】'.format(result_str),
                                                                   callback_data="func1:button:-1:finish"))
                    else:
                        for item, key in func1[select_id + 1].items():
                            markup_list[0].append(
                                InlineKeyboardButton(key,
                                                     callback_data="func1:button:{}:{}".format(select_id + 1, item)))
                    if 0 <= select_id < len(func1):
                        markup_list.append(
                            [InlineKeyboardButton("返回上一页", callback_data="func1:button:{}:back".format(select_id - 1))])

                    # print(bot_session[msg.from_user.id])
                    bot.edit_message_reply_markup(msg.from_user.id, msg.message.message_id,
                                                  reply_markup=InlineKeyboardMarkup(markup_list))
                if callback_data[1] == "group":
                    if callback_data[2] in ['receive', 'reject']:
                        if callback_data[2] == 'receive':
                            # print(msg.message.json)
                            # print(msg.message.json['reply_to_message']['message_id'])
                            user_id = int(msg.message.json['reply_to_message']['text'].split('\n')[0].split(':')[1])
                            # print(msg)
                            # print(msg.message.json['reply_to_message']['text'])
                            # print(user_id)
                            bot.send_message(PUBLIC_CHANNEL, bot_session[user_id]["text"], parse_mode='Markdown',
                                             disable_web_page_preview=True)
                            # bot.forward_message(chat_id=PUBLIC_CHANNEL,
                            #                    from_chat_id=ADMIN_GROUP_ID,
                            #                    #message_id=msg.message.message_id-1)
                            #                    message_id=msg.message.json['reply_to_message']['message_id'])
                        bot.edit_message_text('选择完成', chat_id=ADMIN_GROUP_ID, message_id=msg.message.message_id)
                        del bot_session[user_id]
        except Exception as e:
            print(e)

    def get_select_str(func_str, select):
        resutl = ""
        for item, key in select.items():
            resutl += func_str[item][key]
        return resutl

    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        # logger.error(e)
        time.sleep(15)


if __name__ == '__main__':
    bot_sub1()
