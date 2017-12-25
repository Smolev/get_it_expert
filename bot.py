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
texts[3] = ['Python', 'C++', 'PHP','C#', 'Java', 'iOS','Android', 'Javascript','Go', 'Ruby', 'Разработчик БД SQL',
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
        text += 'Имя: {} \n'.format(user.first_name)
    if user.last_name:
        text += 'Фамилия: {} \n'.format(user.last_name)
    if user.username:
        text += 'Username: {} \n'.format(user.username)

    text += 'Город: {} \n'.format(data['City'])
    text += 'Специализация: {} \n'.format(data['Ability'])
    text += 'Уровень: {} \n'.format(data['Level'])
    return text


def send_mail(chat, document, text, extension):

    gmail_user = "getit.resume@gmail.com"
    gmail_pwd = config.password
    FROM = gmail_user
    TO = ['getitbot@gmail.com']
    
    msg = MIMEMultipart('mixed')
    msg['From'] = FROM
    msg['To'] = ', '.join(TO)
    msg['Subject'] = "Resume"

    text = MIMEText(text, "html", _charset="utf-8")

    with open(document, "rb") as doc:
        docAttachment = MIMEApplication(doc.read(), _subtype=extension)
        docAttachment.add_header('content-disposition', 'attachment', filename=('utf-8', '', document))

    msg.attach(text)
    msg.attach(docAttachment)

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
        markup.row('Москва', 'Казань', 'Уфа')
        markup.row('Санкт-Петербург', 'Красноярск')
        markup.row('Новосибирск', 'Екатеринбург')
        markup.row('Воронеж', 'Нижний Новгород')
        markup.row('Томск', 'Самара', 'Рязань')
        markup.row(u'\U00002B05'+'Назад')
        return markup
    elif status == 3:
        markup.row('Python', 'C++', 'PHP')
        markup.row('C#', 'Java', 'iOS')
        markup.row('Android', 'Javascript')
        markup.row('Go', 'Ruby', 'Oracle')
        markup.row('Разработчик БД SQL', 'Postgres')
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
        if data['Target'] == 'HR':
            answer += 'Специализация кандидата: *{}*\n'.format(data['Ability'])
        else:
            answer += 'Специализация: *{}*\n'.format(data['Ability'])
    if 'Level' in data and data['Level']:
        answer += 'Уровень: *{}*\n'.format(data['Level'])
    answer += '\n'
    return answer


def get_prediction(Name_area, Ability, Level):
    # db = DBHelper()
    # vacancy = db.get_vacancy(Name_area, Ability, Level)
    # resume = db.get_resume(Name_area, Ability, Level)
    # db.close()
    # amount, mean = 0, 0
    # if not (vacancy and resume):
    #     logging.info('Ошибка в обращении к бд')
    #     return 0, 0
    # if vacancy['Amount']:
    #     amount = vacancy['Amount']
    #     vacancy_mean = vacancy['answer_mean']
    #     if resume['Amount']:
    #         resume_mean = resume['answer_mean']
    #         mean = (vacancy_mean + resume_mean)/2
    #     else:
    #         mean = vacancy_mean
    # else:
    #     if resume['Amount']:
    #         resume_mean = resume['answer_mean']
    #         mean = resume_mean
    # return amount, mean
    db = DBHelper()
    answer = db.get_mean(Name_area, Ability, Level)
    db.close()
    low, high = 0, 0
    if not answer:
        logging.info('Ошибка в обращении к бд')
        return 0, 0
    if answer['low']:
        low, high = answer['low'], answer['high']
        return low, high
    return low, high


def text_on_predicition(low, high, ability, level, info):
    # answer = ''
    # if mean:
    #     answer += 'Ожидаемая зарплата: ' + '*' + str(int(mean)) + '*' + '\n'
    # else:
    #     answer = 'К сожалению, у нас нет данных по зарплатам специалистов, удовлетворяющих требуемым параметрам.\n\n'
    #     return answer
    # if amount:
    #     answer += 'Среднее количество вакансий в месяц: '
    #     if amount < 5:
    #         answer += '*Меньше 5*'
    #     elif amount < 10:
    #         answer += '*От 5 до 10*'
    #     elif amount < 20:
    #         answer += '*От 10 до 20*'
    #     elif amount < 50:
    #         answer += '*От 20 до 50*'
    #     else:
    #         answer += '*Больше 50*'
    #     answer += '\n\n' + give_recomends(ability)+'\n'
    # return answer
    answer = ''
    if low:
        if info == 'HR':
            answer += 'Ожидания кандидата: ' + '\nот '+ '*' + str(low) + '*' + ' до ' + '*' + str(high)+'*' '\n\n'
        else:
            answer += 'Ожидаемая зарплата: ' + '\nот '+ '*' + str(low) + '*' + ' до ' + '*' + str(high)+'*' '\n\n'
    else:
        answer = 'К сожалению, у нас нет данных по зарплатам специалистов, удовлетворяющих требуемым параметрам.\n\n'
        return answer
    if level == 'Junior':
        return answer
    else:
        answer += give_recomends(ability)+'\n'
    return answer 

def give_recomends(ability):
    # recommend_dict = {'Android': ['Java', 'SQL'],
    #  'C#': ['SQL'],
    #  'C++': ['SQL', 'C#'],
    #  'CSS': ['HTML', 'Javascript'],
    #  'Go': ['SQL'],
    #  'HTML': ['CSS', 'Javascript'],
    #  'IOS': ['SQL', 'Swift'],
    #  'Java': ['SQL', 'Javascript', 'HTML', 'Python'],
    #  'Javascript': ['HTML', 'CSS', 'SQL', 'PHP'],
    #  'Oracle': ['SQL'],
    #  'PHP': ['SQL', 'Javascript', 'HTML', 'CSS'],
    #  'Postgres': ['SQL'],
    #  'Python': ['SQL', 'Javascript', 'Postgres'],
    #  'Ruby': ['SQL', 'Python'],
    #  'SQL': ['Javascript', 'PHP', 'HTML', 'CSS', 'Postgres']}

    recommend_dict = {'Android': '*Java* (знание *Android SDK*), *SQL*',
     'C#': '*C#*, *SQL*',
     'C++': '*C\C++*, *SQL*',
     'CSS': '*HTML*, *Javascript*',
     'Go': 'Знание *GOlang*, *SQL* (возможно *PL/SQL*)',
     'HTML': '*CSS*, *Javascript*',
     'IOS': '*Swift*, *Objective-c*, *iOS SDK*, *SQL*',
     'Java': '*Java* (*SE*, *EE*, *Spring*, *Swing*, *Hybernate*, *GWT*, *Struts2*, *JSF*, *SWT*), ' +
      '*SQL* (возможно потребуется *PL/SQL*), возможно потребуется знание *JavaScript*',
     'Javascript':  '*JavaScript* (*Jquery*, *Angular*, *React*), *SQL*',
     'Oracle': '*Pl/SQL*',
     'PHP': '*PHP* (*WordPress*, *Yii\Yii2*, *Laravel*, *Symfony*), *SQL*, возможно потребуется знание *JavaScript*',
     'Postgres': '*SQL*',
     'Python': '*Python* (*Django*, *Flask*, *Pyramid*), *SQL*, возможно потребуется знание *JavaScript*',
     'Ruby': '*Ruby* (*ROR*, *Padrino*, *Sinatra*, *LotusRB*, *Volt*), *SQL* (*PL/SQL*), возможно потребуется знание *JavaScript*',
     'SQL': '*SQL*, *PL/SQL*'}

    recommend = ''
    #for reccomendation in recommend_dict[ability]:
    #    recommend += ' *'+ reccomendation +'*' + ','
    text = 'По Вашей специализации в вакансиях чаще всего встречаются следующие навыки: '
    text += recommend_dict[ability] + '\n'
    return text



def get_text(status):
    text = 'Ошибка'
    answer_text = ["Наша почта: it@get-it.io\nНаш сайт: http://get-it.io\nТел.: +7(495)773-46-67\n"+
                    "Канал с IT вакансиями:\n@getitrussia\n\n",
                    "Вас приветствует бот сервиса по IT-подбору *GetIT*. Бот выдает аналитику по заработной плате IT-специалистов. " +
                    "Для начала работы с ботом добавьте информацию о себе.",
                    "Введите город:",
                    "Введите основную специализацию:",
                    "Junior - до 1 года.\nMiddle - от 1 до 3 лет.\nSenior - от 3 лет.\nВведите cвой опыт:", 
                    "Вы можете отправить свое резюме в базу GetIT для оценки.\nВ случае подходящей вакансии наш специалист свяжется с Вами."+
                    "\n\nДля подробной консультации по Вашему резюме позвоните по номеру:\n+7(925)710-18-99\n\n" +
                    "Контакты:\nit@get-it.io\n+7(495)773-46-67\nhttp://get-it.io\n@getitrussia",
                    "Прикрепите к сообщению Ваше резюме в формате pdf, zip, rtf, txt или docx.",
                    "Если Вам нужна помощь в IT-подборе, специалисты GetIT ответят на все вопросы и проконсультируют Вас по вакансии.\n\n" +
                    "Контакты:\nit@get-it.io\n+7(495)773-46-67\nhttp://get-it.io\n"]

    if status > -1 and status < 8:
        text = answer_text[status] 
    return text


def check_text3(mes_text):
    if mes_text in ['Разработчик БД SQL', 'iOS']:
        if mes_text == 'Разработчик БД SQL':
            return 'SQL'
        if mes_text == 'iOS':
            return 'IOS'        
    return mes_text


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
        logging.info('new message: %s %s %s name: %s %s time:  %s' % (message.chat.id, state, message.text, message.chat.first_name, message.chat.last_name, time.asctime()))
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
                mes_text = message.text
                mes_text = check_text3(message.text)
                add_user_info(chat, state, mes_text)
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
                low, high = get_prediction(user_info['City'], user_info['Ability'], user_info['Level'].lower())
                information_text = text_on_predicition(low, high, user_info['Ability'], user_info['Level'], user_info['Target'])
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
        logging.info('Важная ошибка! Отправка и получение сообщений! %s, time%s' % (sys.exc_info()[0], time.asctime()))
        sys.exc_info()[0]
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
                    extension = message.document.file_name.split('.')[-1]
                    if extension not in ['pdf', 'docx', 'doc','zip', 'txt', 'rtf']:
                        bot.send_message(chat, 'Неправильный формат файла. Пожалуйста, отправьте резюме в формате *pdf*, *zip*, *rtf*, *txt* или *docx*!',
                                         parse_mode="Markdown")
                        return 0
                    if message.document.file_size > 15000000:
                        bot.send_message(chat, 'Ваше резюме слишком большое по объёму.\nПожалуйста, напишите нам на почту: it@get-it.io')
                        return 0 
                    file_info = bot.get_file(message.document.file_id)
                    text = 'Резюме отправляется.'
                    bot.send_message(chat, text)
                    mail_text = get_mail_text(chat, message.chat)
                    with open('resumes/' + message.document.file_id + '.' + extension, "wb") as file:
                        response = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.token, file_info.file_path))
                        file.write(response.content)
                        print('Got it')
                        delete_user_info(chat, 1)
                        delete_user_info(chat, 2)
                        delete_user_info(chat, 3)
                        delete_user_info(chat, 4)
                    text = send_mail(chat, 'resumes/' + message.document.file_id + '.' + extension, mail_text, extension)
                    bot.send_message(chat, text)
            else:
                bot.send_message(chat, 'Неправильный формат файла. Пожалуйста, отправьте резюме в формате  *pdf*, *zip*, *rtf*, *txt* или *docx*!',
                                         parse_mode="Markdown")
        else:
            if message.document:
                if message.document.file_id:
                    logging.info('Chat, file: %s %s ' % (chat, message.document.file_id))
            information_text = ''
            markup = get_markup(state)
            data_info = get_user_info(chat)
            text = information_text + text_user_info(data_info)
            text += get_text(state)
            bot.send_message(chat, text, reply_markup=markup, parse_mode="Markdown")
    except:
        print('Фатальная ошибка отправки резюме.')
        logging.info('Фатальная ошибка отправки резюме. %s,\n time: %s' % (sys.exc_info()[0], time.asctime()))


if __name__ == '__main__':
    db.setup()
    db.close()
    while True:
        try:
            bot.polling(none_stop=True)
        except:
            print('ERROR! polling fail')
            logging.info('Telegram does not answer %s '% (time.asctime()))
            time.sleep(15)

