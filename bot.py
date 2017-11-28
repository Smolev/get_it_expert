import config
import telebot
from telebot import types
import requests
import smtplib
import os
import sys
import logging
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dbhelper import DBHelper


db = DBHelper()
bot = telebot.TeleBot(config.token)
logging.basicConfig(filename="logbot.log", level=logging.INFO, filemode='w')

texts = [[] for i in range(8)]
texts[0] = ['Главное меню']
texts[1] = ['HR', 'IT-специалист', 'Контакты']
texts[2] = ['Москва', 'Санкт-Петербург', 'Казань','Новосибирск', 'Красноярск','Екатеринбург', 'Воронеж','Уфа', 'Нижний Новгород',
'Томск', 'Самара', 'Рязань', u'\U00002B05'+'Назад']
texts[3] = ['Python', 'C++', 'PHP','C#', 'Java', 'IOS','Android', 'Javascript','Go', 'Ruby', 'SQL',
'Oracle', 'Postgres', u'\U00002B05'+'Назад к выбору города']
texts[4] = ['Junior', 'Middle', 'Senior', u'\U00002B05'+'Назад к выбору специализации']
texts[5]= ['Отправить резюме', 'Главное меню']
texts[6] = ['Главное меню']
texts[7] = ['Главное меню']

def add_user_info(chat, param=None, value=None):
    keys = {2: 'City', 3: 'Ability',
            4: 'Level', 1: 'Target'}
    db = DBHelper()
    db.add_user_info(chat, keys[param], value)
    db.close()


def delete_user_info(chat, param=None):
    keys = {2: 'City', 3: 'Ability',
            4: 'Level', 1: 'Target'}
    db = DBHelper()
    db.delete_user_info(chat, keys[param])
    db.close()


def get_user_info(chat):
    db = DBHelper()
    info = db.get_user_info(chat)
    db.close()
    return info



def get_mail_text(chat, user):
    data = get_user_info(chat)
    text = 'Данные о пользователе:\n'
    if user.first_name:
        text += 'Имя: {} \n\n'.format(user.first_name)
    if user.last_name:
        text += 'Фамилия: {} \n'.format(user.last_name)
    if user.username:
        text += 'Username: {} \n'.format(user.username)

    text += 'Город: {} \n'.format(data['City'])
    text += 'Специализация: {} \n'.format(data['Ability'])
    text += 'Уровень: {} \n'.format(data['Level'])
    return text


def send_mail(chat, document, text):

    gmail_user = "getit.resume@gmail.com"
    gmail_pwd = config.password
    FROM = gmail_user
    TO = ['getitbot@gmail.com']
    
    msg = MIMEMultipart('mixed')
    msg['From'] = FROM
    msg['To'] = ', '.join(TO)
    msg['Subject'] = "Resume"

    text = MIMEText(text, "html", _charset="utf-8")

    with open(document, "rb") as pdf:
        pdfAttachment = MIMEApplication(pdf.read(), _subtype="pdf")
        pdfAttachment.add_header('content-disposition', 'attachment', filename=('utf-8', '', document))

    msg.attach(text)
    msg.attach(pdfAttachment)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, msg.as_string())
        server.close()
        os.remove(document)
        logging.info('successfully sent the mail from chat: %s, doc: %s '% (chat, document))
        return 'Резюме успешно доставлено.'
    except:
        logging.info('ailed to send mail, from chat: %s, docname: %s'% (chat, document) )
        return 'Не удалось доставить резюме. Для консультации Вы можете написать на наша почту it@get-it.io.'


def get_markup(status):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if status == 0:
        markup.row('Главное меню')
        return markup
    elif status == 1:
        markup.row('HR')
        markup.row('IT-специалист')
        markup.row('Контакты')
        return markup
    elif status == 2:
        markup.row('Москва', 'Санкт-Петербург', 'Казань')
        markup.row('Новосибирск', 'Красноярск')
        markup.row('Екатеринбург', 'Воронеж')
        markup.row('Уфа', 'Нижний Новгород')
        markup.row('Томск', 'Самара', 'Рязань')
        markup.row(u'\U00002B05'+'Назад')
        return markup
    elif status == 3:
        markup.row('Python', 'C++', 'PHP')
        markup.row('C#', 'Java', 'IOS')
        markup.row('Android', 'Javascript')
        markup.row('Go', 'Ruby', 'SQL')
        markup.row('Oracle', 'Postgres')
        markup.row(u'\U00002B05'+'Назад к выбору города')
        return markup
    elif status == 4:
        markup.row('Junior')
        markup.row('Middle')
        markup.row('Senior')
        markup.row(u'\U00002B05'+'Назад к выбору специализации')
        return markup
    elif status == 5:
        markup.row('Отправить резюме')
        markup.row('Главное меню')
        return markup
    elif status == 6 or status == 7:
        markup.row('Главное меню')
        return markup
    return markup


def text_user_info(data):
    if not data:
        return ''
    answer = ''
    if 'Target' in data and data['Target']:
        answer += 'Вы: *{}*\n'.format(data['Target'])
    if 'City' in data and data['City']:
        answer += 'Город: *{}*\n'.format(data['City'])
    if 'Ability' in data and data['Ability']:
        answer += 'Специализация: *{}*\n'.format(data['Ability'])
    if 'Level' in data and data['Level']:
        answer += 'Уровень: *{}*\n'.format(data['Level'])
    answer += '\n'
    return answer


def get_prediction(Name_area, Ability, Level):
    db = DBHelper()
    vacancy = db.get_vacancy(Name_area, Ability, Level)
    resume = db.get_resume(Name_area, Ability, Level)
    db.close()
    amount, mean = 0, 0
    if not (vacancy and resume):
        logging.info('Ошибка в обращении к бд')
        return 0, 0
    if vacancy['Amount']:
        amount = vacancy['Amount']
        vacancy_mean = vacancy['answer_mean']
        if resume['Amount']:
            resume_mean = resume['answer_mean']
            mean = (vacancy_mean + resume_mean)/2
        else:
            mean = vacancy_mean
    else:
        if resume['Amount']:
            resume_mean = resume['answer_mean']
            mean = resume_mean
    return amount, mean


def text_on_predicition(amount, mean, ability):
    answer = ''
    if mean:
        answer += 'Ожидаемая зарплата: ' + '*' + str(int(mean)) + '*' + '\n'
    else:
        answer = 'К сожалению, у нас нет данных по зарплатам специалистов, удовлетворяющих требуемым параметрам.\n\n'
        return answer
    if amount:
        answer += 'Среднее количество вакансий в месяц: '
        if amount < 5:
            answer += '*Меньше 5*'
        elif amount < 10:
            answer += '*От 5 до 10*'
        elif amount < 20:
            answer += '*От 10 до 20*'
        elif amount < 50:
            answer += '*От 20 до 50*'
        else:
            answer += '*Больше 50*'
        answer += '\n\n' + give_recomends(ability)+'\n'
    return answer

def give_recomends(ability):
    recommend_dict = {'Android': ['Java', 'SQL'],
     'C#': ['SQL'],
     'C++': ['SQL', 'C#'],
     'CSS': ['HTML', 'Javascript'],
     'Go': ['SQL'],
     'HTML': ['CSS', 'Javascript'],
     'IOS': ['SQL', 'Swift'],
     'Java': ['SQL', 'Javascript', 'HTML', 'Python'],
     'Javascript': ['HTML', 'CSS', 'SQL', 'PHP'],
     'Oracle': ['SQL'],
     'PHP': ['SQL', 'Javascript', 'HTML', 'CSS'],
     'Postgres': ['SQL'],
     'Python': ['SQL', 'Javascript', 'Postgres'],
     'Ruby': ['SQL', 'Python'],
     'SQL': ['Javascript', 'PHP', 'HTML', 'CSS', 'Postgres']}
    recommend = ''
    for reccomendation in recommend_dict[ability]:
        recommend += ' *'+ reccomendation +'*' + ','
    text = 'По Вашей специализации в вакансиях чаще всего встречаются следующие навыки:'
    text += recommend[:-1] + '\n'
    return text



def get_text(status):
    text = 'Ошибка'
    answer_text = ["Наша почта: it@get-it.io\nНаш сайт: http://get-it.io\nТел.: + 7(495) 773-46-67\nMoб.: +7 (925) 710-18-99\n"+
                    "Канал с IT вакансиями:\nhttps://t.me/getitpro \n\n",
                    "Данный бот компании *GetIT* может подсказать примерную зарплату по IT-специальностям.\n" +
                    "Для того, чтобы получить прогноз, необходимо добавить информацию о себе",  
                    "Введите город:",
                    "Введите основную специализацию:",
                    "Введите уровень владения:", 
                    "Вы можете отправить нам свое резюме, чтобы мы могли его точнее оценить.",
                    "Прикрепите к сообщению pdf-версию Вашего резюме",
                    "Если Вам нужна помощь в подборе IT-специалиста, Вы можете обратиться к нам:\nНаша почта - it@get-it.io\n" +
                    "Наш сайт http://get-it.ion\nТел.: + 7(495) 773-46-67"]

    if status > -1 and status < 8:
        text = answer_text[status] 
    return text


@bot.message_handler(commands=['start'])
def handle_start_help(message):
    try:
        chat = message.chat.id
        logging.info('Start, user: %s %s %s' % (chat, message.chat.first_name, message.chat.last_name))
        db = DBHelper()
        if not str(db.get_state(chat)).isdigit():
            db.add_user(chat)
            state = db.get_state(chat)
        else:
            db.update_state(chat, 1)
            delete_user_info(chat, 1)
            delete_user_info(chat, 2)
            delete_user_info(chat, 3)
            delete_user_info(chat, 4)
            state = db.get_state(chat)
        db.close()
        markup = get_markup(state)
        text = get_text(state)
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
    except:
        print('Важная ошибка!\n Команда start.')



@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): 
    try:
        db = DBHelper()
        chat = message.chat.id
        state = db.get_state(chat)
        db.close()
        information_text = ''
        if not str(state).isdigit():
            bot.send_message(chat, 'Начините работу с ботом командой /start.')
            return 0
        logging.info('new message: %s %s %s' % (message.chat.id, state, message.text))
        if message.text in texts[0] and state == 0:  # 0 - контакты
            db = DBHelper()
            db.update_state(chat, 1)
            db.close()
        elif message.text in texts[1] and state == 1: # 1 - главное меню
            if message.text == 'Контакты':
                db = DBHelper()
                db.update_state(chat, 0)
                db.close()
            else:
                db = DBHelper()
                db.update_state(chat, 2)
                db.close()
                add_user_info(chat, state, message.text)
        elif message.text in texts[2] and state == 2: # 2 - город
            if message.text == u'\U00002B05'+'Назад':
                db = DBHelper()
                db.update_state(chat, 1)
                db.close()
                delete_user_info(chat, 1)
            else:
                add_user_info(chat, state, message.text)
                db = DBHelper()
                db.update_state(chat, 3)
                db.close()
        elif message.text in texts[3] and state == 3: # 3 - специализация
            if message.text == u'\U00002B05'+'Назад к выбору города':
                delete_user_info(chat, 2)
                db = DBHelper()
                db.update_state(chat, 2)
                db.close()
            else:
                add_user_info(chat, state, message.text)
                db = DBHelper()
                db.update_state(chat, 4)
                db.close()
        elif message.text in texts[4] and state == 4: # 4 - уровень
            if message.text == u'\U00002B05'+'Назад к выбору специализации':
                delete_user_info(chat, 3)
                db = DBHelper()
                db.update_state(chat, 3)
                db.close()
            else:
                add_user_info(chat, state, message.text)
                db = DBHelper()
                user_info = get_user_info(chat)
                db.close()
                amount, mean = get_prediction(user_info['City'], user_info['Ability'], user_info['Level'].lower())
                information_text = text_on_predicition(amount, mean, user_info['Ability'])
                target = get_user_info(chat)['Target']
                if target:
                    db = DBHelper()
                    if target == 'HR':
                        db.update_state(chat, 7)
                    else:
                        db.update_state(chat, 5)
                    db.close()
        elif message.text in texts[5] and state == 5: # 5 - 
            if message.text == 'Отправить резюме':
                db = DBHelper()
                db.update_state(chat, 6)
                db.close()
            else:
                db = DBHelper()
                db.update_state(chat, 1)
                db.close()
                delete_user_info(chat, 1)
                delete_user_info(chat, 2)
                delete_user_info(chat, 3)
                delete_user_info(chat, 4)
        elif message.text in texts[6] and (state == 6 or state == 7):
            db = DBHelper()
            db.update_state(chat, 1)
            db.close()
            delete_user_info(chat, 1)
            delete_user_info(chat, 2)
            delete_user_info(chat, 3)
            delete_user_info(chat, 4)
        else:
            if message.text.upper() == 'SVD':
                bot.send_message(chat, 'https://vk.com/pitpen')
            markup = get_markup(state)
            text = 'Для отправки текстовых сообщений, пожалуйста, воспользуйтесь предложенной клавиатурой.\n\n' + get_text(state)
            bot.send_message(chat, text, reply_markup=markup, parse_mode="Markdown")
            return 0
        db = DBHelper()
        state = db.get_state(chat)
        db.close()
        markup = get_markup(state)
        if state == 6:
            text = get_text(state)
            bot.send_message(chat, text, reply_markup=markup, parse_mode="Markdown")
            return 0 
        data_info = get_user_info(chat)
        text = information_text + text_user_info(data_info)
        text += get_text(state)
        bot.send_message(chat, text, reply_markup=markup, parse_mode="Markdown")
    except:
        print('Важная ошибка! Отправка и получение сообщений!')
        delete_user_info(chat, 1)
        delete_user_info(chat, 2)
        delete_user_info(chat, 3)
        delete_user_info(chat, 4)
        db = DBHelper()
        db.update_state(chat, 1)
        db.close()
        db = DBHelper()
        state = db.get_state(chat)
        db.close()
        markup = get_markup(state)
        bot.send_message(chat, 'Ошбика ввода данных, пожалуйста, начните сначала', reply_markup=markup)


@bot.message_handler(content_types=['document', 'photo', 'audio', 'video', 'voice', 'location'])
def handle_docs(message):
    try:
        chat = message.chat.id
        db = DBHelper()
        state = db.get_state(chat)
        if not db.get_state(chat):
            bot.send_message(chat, 'Начините работу с ботом командой /start.')
            return 0
        db.close()
        if state == 6:
            if message.document:
                if message.document.file_id:
                    if message.document.file_name.split('.')[-1] != 'pdf':
                        bot.send_message(chat, 'Неправильный формат файла. Пожалуйста, отправьте резюме в формате *pdf*!',
                                         parse_mode="Markdown")
                        return 0
                    if message.document.file_size > 15000000:
                        bot.send_message(chat, 'Ваше резюме слишком большое по объёму.\nПожалуйста, напишите нам на почту: it@get-it.io')
                        return 0 
                    file_info = bot.get_file(message.document.file_id)
                    text = 'Резюме отправляется.'
                    bot.send_message(chat, text)
                    with open('resumes/' + message.document.file_id + '.pdf', "wb") as file:
                        response = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.token, file_info.file_path))
                        file.write(response.content)
                        print('Got it')
                        delete_user_info(chat, 1)
                        delete_user_info(chat, 2)
                        delete_user_info(chat, 3)
                        delete_user_info(chat, 4)

                    text = send_mail(chat, 'resumes/' + message.document.file_id + '.pdf', str(chat))
                    bot.send_message(chat, text)
            else:
                bot.send_message(chat, 'Неправильный формат файла. Пожалуйста, отправьте резюме в формате *pdf*!',
                                         parse_mode="Markdown")
        else:
            information_text = ''
            markup = get_markup(state)
            data_info = get_user_info(chat)
            text = information_text + text_user_info(data_info)
            text += get_text(state)
            bot.send_message(chat, text, reply_markup=markup, parse_mode="Markdown")
    except:
        print('Фатальная ошибка отправки резюме.')

def polling_bot(bot):
    try:
        bot.polling(none_stop=True)
    except:
        print('ERROR! polling fail')
        time.sleep(3)
        polling_bot(bot)

if __name__ == '__main__':
    db.setup()
    db.close()
    polling_bot(bot)

