from flask import Flask, request
from function import *
from datetime import *
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
quizcode = "NA"
user_type_name= False
user_name = ""
view_leaderboard = False
quiz_data = pd.DataFrame()
user_input = pd.DataFrame()

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
    global view_leaderboard
    global quiz_data
    global user_input

    incoming_msg = request.values.get('Body', '').lower()
    phone_num = str(request.values.get('From').replace("whatsapp:+", ""))
    resp = MessagingResponse()
    msg = resp.message()

    if not ongoing_session:
        if view_leaderboard:
            quiz_info = get_all_quiz_info()
            if incoming_msg in '0':
                view_leaderboard = False
                msg.body(default_fun(user_name))
                return str(resp)
            elif incoming_msg.upper() in (quiz_info['Quiz_code']).tolist():
                selected_quiz_info = quiz_info[quiz_info['Quiz_code'] == incoming_msg.upper()]
                msg_str = selected_quiz_info.iloc[0][1] + " by " + selected_quiz_info.iloc[0][2] + "\n"
                msg.body(msg_str)
                msg1 = resp.message()
                msg1.body(get_leaderboard(incoming_msg.upper()))
                msg2 = resp.message()
                msg2.body("press *0* to exit")
                return str(resp)
            else:
                msg_select_quiz = "Sorry I didn't understand the message! \n Type a valid code to see the leaderboard or type *0* to exit"
                msg.body(msg_select_quiz)
                return str(resp)
        if user_type_name:
            if '1' in incoming_msg:
                add_new_user(phone_num,user_name)
                msg.body(default_fun(user_name))
                msg.media("https://filetest1.s3.amazonaws.com/Sirpi_Bot_Folder/SirpiBot.png")
                user_type_name = False
            else:
                user_name = request.values.get('Body', '')
                msg_confirm_name = confirm_name_fun(user_name)
                msg.body(msg_confirm_name)
            return str(resp)
        if incoming_msg in ['hi', 'hi ','hello', 'hello'] :
            user_name = get_user_name(phone_num)
            if user_name == "new user":
                msg_new = "Welcome! I am SIRPI QuizBot\n Please type your name to get started\n"
                msg.media("https://filetest1.s3.amazonaws.com/Sirpi_Bot_Folder/SirpiBot.png")
                user_type_name = True
                msg.body(msg_new)
            else:
                msg.body(default_fun(user_name))
                msg.media("https://filetest1.s3.amazonaws.com/Sirpi_Bot_Folder/SirpiBot.png")
            return str(resp)
        elif incoming_msg in ['1','2','3','4','5','6']:
            if '1' in incoming_msg:
                ongoing_session = True
            elif '2' in incoming_msg:
                msg.body(help_fun())
                return str(resp)
            elif '3' in incoming_msg:
                msg.body(learn_fun())
                return str(resp)
            elif '4' in incoming_msg:
                msg.body("Performance Analysis")
                msg1 = resp.message()
                msg1.body(past_user_performace_fun(phone_num))
                return str(resp)
            elif '5' in incoming_msg:
                quiz_info = get_quiz_info()
                num_quiz = quiz_info.shape[0]
                if num_quiz == 0:
                    msg.body("No ongoing quiz\npress *0* to exit")
                    return str(resp)
                else:
                    lb_msg = "Type the quiz code to view leaderboard "
                    msg.body(lb_msg)
                    view_leaderboard = True
                    for j in range(num_quiz):
                        quiz_option = quiz_info.iloc[j][1] + " by " + quiz_info.iloc[j][2] + "\n" \
                                    "Quiz Code: " + quiz_info.iloc[j][0] +"\n"
                        msg_option = resp.message()
                        msg_option.body(quiz_option)
                    msg_ex = resp.message()
                    msg_ex.body("press *0* to exit")
                    return str(resp)
            else:
                f_quiz = future_quiz_info_fun()
                fsize = f_quiz.shape[0]
                if fsize == 0:
                    msg.body("No upcoming quizzes!!")
                    return str(resp)
                else:
                    msg.body("Upcoming Quizzes\n")
                    for j in range(fsize):
                        quiz_option = f_quiz.iloc[j][1] + " by " + f_quiz.iloc[j][2] + "\n" \
                                     "Quiz Code: " + f_quiz.iloc[j][0] + "\n" \
                                     "Marking Scheme: +" + str(f_quiz.iloc[j][4]) + "/" + str(f_quiz.iloc[j][5]) + "\n"\
                                     "Starts On: " + str(f_quiz.iloc[j][7]) + "\n"\
                                    "Ends On: " + str(f_quiz.iloc[j][8]) + "\n"
                        msg_option = resp.message()
                        msg_option.body(quiz_option)
                    return str(resp)
        else:
            msg.body(did_not_understand_fun())
            return str(resp)
    if ongoing_session and not ongoing_quiz:
        quiz_info = get_quiz_info()
        if incoming_msg in ['0','1','#','next']:
            if '1' in incoming_msg:
                num_quiz = quiz_info.shape[0]
                if num_quiz == 0:
                    msg.body("No ongoing quiz\npress *0* to exit")
                    return str(resp)
                else:
                    question_number = 0
                    attempted_question = 0
                    correct_answer = 0
                    msg.body(start_fun())
                    for j in range(num_quiz):
                        quiz_option = quiz_info.iloc[j][1] + " by " + quiz_info.iloc[j][2] + "\n" \
                                      "Quiz Code: " + \
                                      quiz_info.iloc[j][0] + "\n" \
                                        "Total question: " + str(quiz_info.iloc[j][3]) + "\n"\
                                       "Marking Scheme: +" + str(quiz_info.iloc[j][4]) + "/" + str(quiz_info.iloc[j][5]) + "\n\n"
                        msg_option = resp.message()
                        msg_option.body(quiz_option)
                    msg_ex = resp.message()
                    msg_ex.body("press *0* to exit")
                    return str(resp)
            elif '0' in incoming_msg:
                ongoing_session = False
                msg.body(default_fun(user_name))
                return str(resp)
            elif 'next' in incoming_msg:
                ongoing_quiz = True
            else:
                msg.body("Detailed Analysis")
                for i in range(quiz_size):
                    msg_analyse = resp.message()
                    option_msg = "A. " + str(quiz_data.iloc[i][1]) + "\n" \
                                "B. " + str(quiz_data.iloc[i][2]) + "\n" \
                                 "C. " + str(quiz_data.iloc[i][3]) + "\n" \
                                "D. " + str(quiz_data.iloc[i][4]) + "\n"
                    analyze_msg = "\n" + quiz_data.iloc[i]['Question'] + "\n" + \
                                  option_msg + "Your response: " + user_input.iloc[i]['Answer'] + \
                                  "\nCorrect response: " + user_input.iloc[i]['Correct'] + "\n"
                    msg_analyse.body(analyze_msg)
                return str(resp)
        elif incoming_msg.upper() in (quiz_info['Quiz_code']).tolist():
            quizcode = incoming_msg.upper()
            selected_quiz_info = quiz_info[quiz_info.Quiz_code == incoming_msg.upper()]
            quiz_data = get_quiz_data(incoming_msg.upper())
            print(quiz_data)
            quiz_size = quiz_data.shape[0]
            user_input = pd.DataFrame(list(zip(["NA"] * quiz_size, [False] * quiz_size, [0] * quiz_size)), columns=['Answer', 'Result', 'Time'])
            user_input['Correct'] = quiz_data['Correct'].values
            positive_marks = selected_quiz_info.iloc[0][4]
            negative_marks = selected_quiz_info.iloc[0][5]
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
                       "+" + str(positive_marks) + " points for each correct answer \n" + str(negative_marks) + " points for each wrong answer \n" \
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
                        global_end_time = datetime.now()
                        total_time = (global_end_time-global_start_time).total_seconds()
                        total_time = round(total_time, 2)
                        points = (correct_answer * positive_marks) + (
                                    (attempted_question - correct_answer) * negative_marks)
                        add_to_user_data(phone_num,user_name,quizcode,global_start_time,global_end_time,total_time,points,quiz_format)
                        end_msg = end_msg_fun(question_number,correct_answer,attempted_question,points,total_time)
                        msg.body(end_msg)
                    else:
                        question_number = question_number + 1
                        option_msg = "A. " + str(quiz_data.iloc[question_number - 1][1]) + "\n" \
                                                                                           "B. " + str(
                            quiz_data.iloc[question_number - 1][2]) + "\n" \
                                                                      "C. " + str(
                            quiz_data.iloc[question_number - 1][3]) + "\n" \
                                                                      "D. " + str(
                            quiz_data.iloc[question_number - 1][4]) + "\n"
                        question_msg = quiz_data.iloc[question_number - 1][0] + "\n\n" + option_msg + "\n"
                        msg.body(question_msg)
                        global_start_time = datetime.now()
                        start_time = datetime.now()
                elif incoming_msg in ['a', 'b', 'c', 'd']:
                    if quiz_data.iloc[question_number - 1][5].lower() == incoming_msg:
                        end_time = datetime.now()
                        time_taken = (end_time - start_time).total_seconds()
                        time_taken = round(time_taken,2)
                        attempted_question = attempted_question + 1
                        correct_answer = correct_answer + 1
                        user_input.at[question_number - 1, 'Answer'] = incoming_msg.upper()
                        user_input.at[question_number - 1, 'Result'] = True
                        user_input.at[question_number - 1, 'Time'] = time_taken
                    else:
                        end_time = datetime.now()
                        time_taken = (end_time - start_time).total_seconds()
                        time_taken = round(time_taken, 2)
                        attempted_question = attempted_question + 1
                        user_input.at[question_number - 1, 'Answer'] = incoming_msg.upper()
                        user_input.at[question_number - 1, 'Result'] = False
                        user_input.at[question_number - 1, 'Time'] = time_taken
                    if question_number == quiz_size:
                        ongoing_quiz = False
                        global_end_time = datetime.now()
                        total_time = (global_end_time - global_start_time).total_seconds()
                        total_time = round(total_time, 2)
                        points = (correct_answer * positive_marks) + (
                                    (attempted_question - correct_answer) * negative_marks)
                        add_to_user_data(phone_num, user_name, quizcode, global_start_time,global_end_time,total_time, points, quiz_format)
                        end_msg = end_msg_fun(question_number,correct_answer,attempted_question,points,total_time)
                        msg.body(end_msg)
                    else:
                        question_number = question_number + 1
                        option_msg = "A. " + str(quiz_data.iloc[question_number - 1][1]) + "\n" \
                                    "B. " + str(quiz_data.iloc[question_number - 1][2]) + "\n" \
                                    "C. " + str(quiz_data.iloc[question_number- 1][3]) + "\n" \
                                    "D. " + str(quiz_data.iloc[question_number - 1][4]) + "\n"
                        question_msg = quiz_data.iloc[question_number - 1][0] + "\n\n" + option_msg + "\n"
                        msg.body(question_msg)
                        start_time = datetime.now()
                else:
                    ongoing_quiz = False
                    global_end_time = datetime.now()
                    total_time = (global_end_time - global_start_time).total_seconds()
                    total_time = round(total_time, 2)
                    points = (correct_answer * positive_marks) + ((attempted_question - correct_answer) * negative_marks)
                    add_to_user_data(phone_num, user_name, quizcode, global_start_time, global_end_time,total_time,points, quiz_format)
                    end_msg = end_msg_fun(question_number,correct_answer,attempted_question,points,total_time)
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
                        global_end_time = datetime.now()
                        total_time = (global_end_time - global_start_time).total_seconds()
                        total_time = round(total_time, 2)
                        points = (correct_answer * positive_marks) + (
                                    (attempted_question - correct_answer) * negative_marks)
                        add_to_user_data(phone_num, user_name, quizcode, global_start_time, global_end_time,total_time, points, quiz_format)
                        end_msg = end_msg_fun(question_number, correct_answer, attempted_question,points, total_time)
                        msg.body(end_msg)
                    else:
                        question_number = question_number + 1
                        option_msg = "A. " + str(quiz_data.iloc[question_number - 1][1]) + "\n" \
                                                                                           "B. " + str(
                            quiz_data.iloc[question_number - 1][2]) + "\n" \
                                                                      "C. " + str(
                            quiz_data.iloc[question_number - 1][3]) + "\n" \
                                                               "D. " + str(
                            quiz_data.iloc[question_number - 1][4]) + "\n"
                        question_msg = quiz_data.iloc[question_number - 1][0] + "\n\n" + option_msg + "\n"
                        msg.body(question_msg)
                        global_start_time = datetime.now()
                        start_time = datetime.now()
                elif incoming_msg in ['a', 'b', 'c', 'd'] and ongoing_question:
                    ongoing_question = False
                    if quiz_data.iloc[question_number - 1][5].lower() == incoming_msg:
                        end_time = datetime.now()
                        time_taken = (end_time - start_time).total_seconds()
                        time_taken = round(time_taken, 2)
                        ans_msg = "Yay!! that's a correct answer\n" \
                                  "Time taken: " + str(time_taken)
                        msg.body(ans_msg)
                        attempted_question = attempted_question + 1
                        correct_answer = correct_answer + 1
                        user_input.at[question_number - 1, 'Answer'] = incoming_msg.upper()
                        user_input.at[question_number - 1, 'Result'] = True
                        user_input.at[question_number - 1, 'Time'] = time_taken
                    else:
                        end_time = datetime.now()
                        time_taken = (end_time - start_time).total_seconds()
                        time_taken = round(time_taken, 2)
                        ans_msg = "That's incorrect answer\n" \
                                    "Correct answer: " + user_input.iloc[question_number-1]['Correct'] + "\n"\
                                  "Time taken: " + str(time_taken) + "\n"
                        msg.body(ans_msg)
                        attempted_question = attempted_question + 1
                        user_input.at[question_number - 1, 'Answer'] = incoming_msg.upper()
                        user_input.at[question_number - 1, 'Result'] = False
                        user_input.at[question_number - 1, 'Time'] = time_taken
                    if question_number == quiz_size:
                        ongoing_quiz = False
                        global_end_time = datetime.now()
                        total_time = (global_end_time - global_start_time).total_seconds()
                        total_time = round(total_time, 2)
                        points = (correct_answer * positive_marks) + (
                                    (attempted_question - correct_answer) * negative_marks)
                        add_to_user_data(phone_num, user_name, quizcode, global_start_time, global_end_time,total_time, points, quiz_format)
                        end_msg = end_msg_fun(question_number, correct_answer,attempted_question,points, total_time)
                        msg_end = resp.message()
                        msg_end.body(end_msg)
                    else:
                        msg_next = resp.message()
                        question_msg = "Type *next* for the next question\nType *0* to quit\n"
                        msg_next.body(question_msg)
                elif '0' in incoming_msg:
                    ongoing_quiz = False
                    global_end_time = datetime.now()
                    total_time = (global_end_time - global_start_time).total_seconds()
                    total_time = round(total_time, 2)
                    points = (correct_answer * positive_marks) + ((attempted_question - correct_answer) * negative_marks)
                    add_to_user_data(phone_num, user_name, quizcode, global_start_time, global_end_time, total_time,points, quiz_format)
                    end_msg = end_msg_fun(question_number, correct_answer, attempted_question, points,total_time)
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

