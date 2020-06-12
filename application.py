from flask import Flask, request
import function
import time
import datetime
from database import *
import requests
import pandas as pd
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

question_number = 0
correct_answer = 0
ongoing_session = False
ongoing_quiz = False
attempted_question = 0
global_start_time = 0
global_end_time = 0
start_time = 0
end_time = 0
positive_marks = 0
negative_marks = 0
quiz_size = 0
quiz_format = 's'
ongoing_question = False
time_taken = 0
phone_num = 0
name = "Chirag"
quizcode = "NA"
user_type_name= False
user_name = ""


@app.route('/bot', methods=['POST'])
def bot():
    global question_number
    global correct_answer
    global ongoing_session
    global ongoing_quiz
    global attempted_question
    global start_time
    global end_time
    global global_start_time
    global global_end_time
    global quiz_size
    global positive_marks
    global negative_marks
    global quiz_format
    global ongoing_question
    global time_taken
    global phone_num
    global quizcode
    global user_type_name
    global user_name


    incoming_msg = request.values.get('Body', '').lower()
    phone_num = str(request.values.get('From').replace("whatsapp:+", ""))
    resp = MessagingResponse()
    msg = resp.message()

    if not ongoing_session :
        if user_type_name:
            if '1' in incoming_msg:
                function.add_new_user(phone_num,user_name)
                msg.body(function.default_fun(user_name))
                msg.media("https://filetest1.s3.amazonaws.com/Sirpi_Bot_Folder/SirpiBot.png")
                user_type_name = False
            else:
                user_name = request.values.get('Body', '')
                msg_confirm_name = "You have selected " + request.values.get('Body', '') + " as your name\n"\
                "Press 1 to continue with this name or type a different name\n"
                "This name will be used as your id for all the quizzes\n"
                msg.body(msg_confirm_name)
            return str(resp)
        if incoming_msg in ['hi', 'hi ','hello', 'hello'] :
            if function.new_user(phone_num):
                msg_new = "Welcome! I am SIRPI QuizBot\n Please type your name to get started\n"
                msg.media("https://filetest1.s3.amazonaws.com/Sirpi_Bot_Folder/SirpiBot.png")
                user_type_name = True
                msg.body(msg_new)
            else:
                n = function.get_user_name_fun(phone_num)
                msg.body(function.default_fun(n))
                msg.media("https://filetest1.s3.amazonaws.com/Sirpi_Bot_Folder/SirpiBot.png")
            return str(resp)
        elif incoming_msg in ['1','2','3','4']:
            if '1' in incoming_msg:
                ongoing_session = True
            elif '2' in incoming_msg:
                msg.body(function.help_fun())
                return str(resp)
            elif '4' in incoming_msg:
                msg.body("Perforamance Analysis")
                for j in range(3):
                    msg1 = resp.message()
                    msg1.body(function.past_performace_fun(phone_num,j))
                return str(resp)
            else:
                msg.body(function.learn_fun())
                return str(resp)
        else :
            msg.body("Sorry, I did not understand the message!\n"
                      "Type *1* to start the quiz\n" \
                        "Type *2* for help\n" \
                    "Type *3* to learn more about me")
            return str(resp)
    if ongoing_session and not ongoing_quiz:
        if incoming_msg in ['0','1','#','next']:
            if '1' in incoming_msg:
                question_number = 0
                attempted_question = 0
                correct_answer = 0
                msg.body(function.start_fun())
                for j in range(function.quiz_info_pd.shape[0]):
                    quiz_option = function.quiz_info_pd.iloc[j][0] + " by " + function.quiz_info_pd.iloc[j][1] + "\n" \
                                                                                                                 "Quiz Code: " + \
                                  function.quiz_info_pd.iloc[j][
                                      2] + "\n" \
                                           "Marking Scheme: +" + str(
                        function.quiz_info_pd.iloc[j][3]) + "/" + str(function.quiz_info_pd.iloc[j][4]) + "\n\n"
                    msg_option = resp.message()
                    msg_option.body(quiz_option)
                return str(resp)
            elif '0' in incoming_msg:
                ongoing_session = False
                msg.body(function.default_fun(user_name))
                return str(resp)
            elif 'next' in incoming_msg:
                ongoing_quiz = True
            else:
                msg.body("Detailed Analysis")
                for i in range(quiz_size):
                    msg_analyse = resp.message()
                    msg_analyse.body(function.analyze_fun(i))
                    print(function.analyze_fun(i))
                return str(resp)
        elif function.select_quiz_fun(incoming_msg.upper()):
            quizcode = incoming_msg.upper()
            function.set_quiz_fun(incoming_msg.upper())
            quiz_size = function.quiz_size
            positive_marks = function.postive_marks_fun(incoming_msg.upper())
            negative_marks = function.negative_marks_fun(incoming_msg.upper())
            msg.body("Please select the Format")
            format_msg1 = "Speedy Quiz:\nAnswers at the end of the quiz,\nNext question will come immediately\n"\
                        "Type *S* for Speedy Quiz"
            format1 = resp.message()
            format1.body(format_msg1)
            format_msg2 = "Long Quiz:\nAnswer after every response,\nNext question when you type *next*\n" \
                          "Type *L* for Long Quiz"
            format2 = resp.message()
            format2.body(format_msg2)
            return str(resp)
        elif incoming_msg in ['s','l']:
            quiz_format = incoming_msg.lower()
            format_name = 'Speedy'
            if quiz_format in 's':
                format_name = 'Speedy'
            if quiz_format in 'l':
                format_name = 'Long'

            msg_ins = "Instructions: \nThis quiz has " + str(quiz_size) + " questions \n" \
                                                "+" + str(positive_marks) + " points for each correct answer \n" + str(
                negative_marks) + " points for each wrong answer \n" \
                "You have selected " + format_name + " quiz format \n"\
                "Type *next* to continue \n All the best!!"
            msg.body(msg_ins)
            return str(resp)
        else:
            msg_select_quiz = "Sorry I didn't understand the message! \n Type a valid code to start the quiz or type *0* to exit"
            msg.body(msg_select_quiz)
            return str(resp)
    if  ongoing_quiz:
        if 's' in quiz_format:
            if incoming_msg in ['a','b','c','d','0','next']:
                if 'next' in incoming_msg:
                    if question_number == quiz_size:
                        ongoing_quiz = False
                        global_end_time = datetime.datetime.now()
                        total_time = float(global_end_time.strftime('%S.%f')[:-4]) - float(global_start_time.strftime('%S.%f')[:-4])
                        points = (correct_answer * positive_marks) + (
                                    (attempted_question - correct_answer) * negative_marks)
                        function.add_to_user_data(phone_num,name,quizcode,global_start_time,global_end_time,total_time,points,quiz_format)
                        end_msg = function.end_msg_fun(question_number,correct_answer,attempted_question,points,total_time)
                        msg.body(end_msg)
                    else:
                        question_number = question_number + 1
                        question_msg = function.question(question_number) + "\n\n" + function.option(question_number) + "\n"
                        msg.body(question_msg)
                        global_start_time = datetime.datetime.now()
                        start_time = datetime.datetime.now()
                elif incoming_msg in ['a', 'b', 'c', 'd']:
                    if function.answer(question_number, incoming_msg):
                        end_time = datetime.datetime.now()
                        time_taken = float(end_time.strftime('%S.%f')[:-4]) - float(start_time.strftime('%S.%f')[:-4])
                        attempted_question = attempted_question + 1
                        correct_answer = correct_answer + 1
                        function.user_input.at[question_number - 1, 'Answer'] = incoming_msg.upper()
                        function.user_input.at[question_number - 1, 'Result'] = True
                        function.user_input.at[question_number - 1, 'Time'] = time_taken
                    else:
                        end_time = datetime.datetime.now()
                        time_taken = float(end_time.strftime('%S.%f')[:-4]) - float(start_time.strftime('%S.%f')[:-4])
                        attempted_question = attempted_question + 1
                        function.user_input.at[question_number - 1, 'Answer'] = incoming_msg.upper()
                        function.user_input.at[question_number - 1, 'Result'] = False
                        function.user_input.at[question_number - 1, 'Time'] = time_taken
                    if question_number == quiz_size:
                        ongoing_quiz = False
                        global_end_time = datetime.datetime.now()
                        total_time = float(global_end_time.strftime('%S.%f')[:-4]) - float(global_start_time.strftime('%S.%f')[:-4])
                        points = (correct_answer * positive_marks) + (
                                    (attempted_question - correct_answer) * negative_marks)
                        function.add_to_user_data(phone_num, name, quizcode, global_start_time,global_end_time,total_time, points, quiz_format)
                        end_msg = function.end_msg_fun(question_number,correct_answer,attempted_question,points,total_time)
                        msg.body(end_msg)
                    else:
                        question_number = question_number + 1
                        question_msg = function.question(question_number) + "\n\n" + function.option(question_number) + "\n"
                        msg.body(question_msg)
                        start_time = datetime.datetime.now()
                else:
                    ongoing_quiz = False
                    global_end_time = datetime.datetime.now()
                    total_time = float(global_end_time.strftime('%S.%f')[:-4]) - float(global_start_time.strftime('%S.%f')[:-4])
                    points = (correct_answer * positive_marks) + ((attempted_question - correct_answer) * negative_marks)
                    function.add_to_user_data(phone_num, name, quizcode, global_start_time, global_end_time,total_time,points, quiz_format)
                    end_msg = function.end_msg_fun(question_number,correct_answer,attempted_question,points,total_time)
                    msg.body(end_msg)
            else:
                ans_msg = "Please select among *A/B/C/D* \nOr type *next* for the next question\nType *0* to end the quiz"
                msg.body(ans_msg)
            return str(resp)
        if 'l' in quiz_format:
            if incoming_msg in ['a','b','c','d','0','next']:
                if 'next' in incoming_msg:
                    ongoing_question = True
                    if question_number == quiz_size:
                        ongoing_quiz = False
                        global_end_time = datetime.datetime.now()
                        total_time = float(global_end_time.strftime('%S.%f')[:-4]) - float(global_start_time.strftime('%S.%f')[:-4])
                        points = (correct_answer * positive_marks) + (
                                    (attempted_question - correct_answer) * negative_marks)
                        function.add_to_user_data(phone_num, name, quizcode, global_start_time, global_end_time,total_time, points, quiz_format)
                        end_msg = function.end_msg_fun(question_number, correct_answer, attempted_question,points, total_time)
                        msg.body(end_msg)
                    else:
                        question_number = question_number + 1
                        question_msg = function.question(question_number) + "\n\n" + function.option(question_number) + "\n"
                        msg.body(question_msg)
                        global_start_time = datetime.datetime.now()
                        start_time = datetime.datetime.now()
                elif incoming_msg in ['a', 'b', 'c', 'd'] and ongoing_question:
                    ongoing_question = False
                    if function.answer(question_number, incoming_msg):
                        end_time = datetime.datetime.now()
                        time_taken = float(end_time.strftime('%S.%f')[:-4]) - float(start_time.strftime('%S.%f')[:-4])
                        ans_msg = "Yay!! that's a correct answer\n" \
                                  "Time taken: " + str(time_taken)
                        msg.body(ans_msg)
                        attempted_question = attempted_question + 1
                        correct_answer = correct_answer + 1
                        function.user_input.at[question_number - 1, 'Answer'] = incoming_msg.upper()
                        function.user_input.at[question_number - 1, 'Result'] = True
                        function.user_input.at[question_number - 1, 'Time'] = time_taken
                    else:
                        end_time = datetime.datetime.now()
                        time_taken = float(end_time.strftime('%S.%f')[:-4]) - float(start_time.strftime('%S.%f')[:-4])
                        ans_msg = "That's incorrect answer\n" \
                                    "Correct answer: " + function.user_input.iloc[question_number-1]['Correct'] + "\n"\
                                  "Time taken: " + str(time_taken) + "\n"
                        msg.body(ans_msg)
                        attempted_question = attempted_question + 1
                        function.user_input.at[question_number - 1, 'Answer'] = incoming_msg.upper()
                        function.user_input.at[question_number - 1, 'Result'] = False
                        function.user_input.at[question_number - 1, 'Time'] = time_taken
                    if question_number == quiz_size:
                        ongoing_quiz = False
                        global_end_time = datetime.datetime.now()
                        total_time = float(global_end_time.strftime('%S.%f')[:-4]) - float(global_start_time.strftime('%S.%f')[:-4])
                        points = (correct_answer * positive_marks) + (
                                    (attempted_question - correct_answer) * negative_marks)
                        function.add_to_user_data(phone_num, name, quizcode, global_start_time, global_end_time,total_time, points, quiz_format)
                        end_msg = function.end_msg_fun(question_number, correct_answer,attempted_question,points, total_time)
                        msg_end = resp.message()
                        msg_end.body(end_msg)
                    else:
                        msg_next = resp.message()
                        question_msg = "Type *next* for the next question\nType *0* to quit\n"
                        msg_next.body(question_msg)
                elif '0' in incoming_msg:
                    ongoing_quiz = False
                    global_end_time = datetime.datetime.now()
                    total_time = float(global_end_time.strftime('%S.%f')[:-4]) - float(global_start_time.strftime('%S.%f')[:-4])
                    points = (correct_answer * positive_marks) + ((attempted_question - correct_answer) * negative_marks)
                    function.add_to_user_data(phone_num, name, quizcode, global_start_time, global_end_time, total_time,points, quiz_format)
                    end_msg = function.end_msg_fun(question_number, correct_answer, attempted_question, points,total_time)
                    msg.body(end_msg)
                else:
                    ans_msg = "Please type *next* for the next question! \nType *0* to end the quiz"
                    msg.body(ans_msg)
            else:
                if ongoing_question:
                    ans_msg = "Please select among *A/B/C/D* \nOr type *next* for the next question! \nType *0* to end the quiz"
                else:
                    ans_msg = "Please type *next* for the next question! \nType *0* to end the quiz"
                msg.body(ans_msg)
            return str(resp)

if __name__ == '__main__':
    app.run(debug=True)

