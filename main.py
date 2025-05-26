import os
from dotenv import load_dotenv
from datetime import datetime
import telebot


load_dotenv()
API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)

user_data = {}
current_question = {}

setup_questions = {
    1: "What is your name?",
    2: "What is your date of birth? (MM/DD/YYYY)",
    3: "Do you want to set a weekly reminder of your current week of your life? (yes/no)"
}

@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.chat.id, "Hello. Write down commands here later")

@bot.message_handler(commands=['setup'])
def setup(message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    current_question[user_id] = 1
    ask_questions(user_id)

def date_check(date_str):
    try:
        birthday = datetime.strptime(date_str, '%m/%d/%Y')
        today = datetime.now()
        age = (today - birthday).days // 365

        if 13 <= age <= 120:
            return True
        return False
    except ValueError:
        return False
    
def week_calculation(user_id):
    dob = user_data[user_id]['dob']
    birthday = datetime.strptime(dob, '%m/%d/%Y')
    today = datetime.now()
    age_in_days = (today - birthday).days
    weeks = age_in_days // 7
    user_data[user_id]['weeks'] = weeks
    
    total_weeks = 78*52 # Assuming average lifespan of 78 years
    user_data[user_id]['total_weeks'] = total_weeks




def ask_questions(user_id):
    if len(user_data[user_id]) < len(setup_questions):
        question = setup_questions[current_question[user_id]]
        bot.send_message(user_id, question)
        bot.register_next_step_handler_by_chat_id(user_id, process_answer)
    else:
        week_calculation(user_id)

        message = f"Hello {user_data[user_id]['name']}! You are currently on week {user_data[user_id]['weeks']} of your life. Estimated {user_data[user_id]['total_weeks'] - user_data[user_id]['weeks']} weeks left. Tempus fugit."
        bot.send_message(user_id, message)

def process_answer(message):
    if current_question[message.from_user.id] == 1:
        user_data[message.from_user.id]['name'] = message.text
        current_question[message.from_user.id] += 1
    elif current_question[message.from_user.id] == 2:
        date = message.text
        if date_check(date):
            user_data[message.from_user.id]['dob'] = message.text
            current_question[message.from_user.id] += 1
        else:
            bot.send_message(message.from_user.id, "Invalid date format. Please use MM/DD/YYYY.")
    elif current_question[message.from_user.id] == 3:
        if message.text.lower() in ['yes', 'no']:
            user_data[message.from_user.id]['reminder'] = message.text.lower()
            current_question[message.from_user.id] += 1
        else:
            bot.send_message(message.from_user.id, "Please answer with 'yes' or 'no'.")
        
    ask_questions(message.from_user.id)
    


bot.polling()