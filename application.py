from flask import Flask, request
import function
import time
import requests
import pandas as pd
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

quiz_size = function.quiz_size
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

    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    if 'start' in incoming_msg:
        ongoing_session = True
        ongoing_quiz = False
        question_number = 0
        attempted_question = 0
        correct_answer = 0
        msg.body(function.start_fun())
        for j in range(function.quiz_info_pd.shape[0]):
            quiz_option = function.quiz_info_pd.iloc[j][0] + " by " + function.quiz_info_pd.iloc[j][1] + "\n" \
                                                                                     "Quiz Code: " + function.quiz_info_pd.iloc[j][
                              2] + "\n" \
                                   "Marking Scheme: +" + str(
                function.quiz_info_pd.iloc[j][3]) + "/" + str(function.quiz_info_pd.iloc[j][4]) + "\n\n"
            msg_option = resp.message()
            msg_option.body(quiz_option)
    elif ongoing_session:
        if function.select_quiz_fun(incoming_msg.upper()):
            function.quiz_set_fun(incoming_msg.upper())
            quiz_size = function.quiz_size
            positive_marks = function.postive_marks_fun(incoming_msg.upper())
            negative_marks = function.negative_marks_fun(incoming_msg.upper())
            msg_select_quiz = "You have selected " + \
                              function.select_quiz_name_fun(incoming_msg.upper()) + \
                              " quiz by " + function.select_quiz_master_name_fun(incoming_msg.upper()) + "\n"\
                            "This quiz has " + str(quiz_size) + " questions \n"\
                            "+" + str(positive_marks) + " points for each correct answer \n" +  str(negative_marks) + " for each negative one \n"\
                                "Type *next* to continue \n All the best!!"
            msg.body(msg_select_quiz)
            ongoing_session = False
            ongoing_quiz = True
        elif 'exit' in incoming_msg:
            ongoing_session = False;
            msg.body(function.default_fun())
        else :
            msg_select_quiz = "Sorry that's not a valid code! \n Type a valid code to start the quiz or type *exit* to return back"
            msg.body(msg_select_quiz)
    elif incoming_msg in ['hi', 'hi ', 'learn', 'hello', 'hello', 'help']:
        if incoming_msg in ['hi', 'hi ', 'hello', 'hello']:
            msg.body(function.default_fun())
            msg.media("https://filetest1.s3.amazonaws.com/Sirpi_Bot_Folder/SirpiBot.png")
        elif 'learn' in incoming_msg:
            msg.body(function.learn_fun())
        else:
            msg.body(function.help_fun())
    elif 'quit' in incoming_msg:
        ongoing_quiz = False
        global_end_time = time.time()
        total_time = (global_end_time - global_start_time).__round__(2)
        points = (correct_answer*positive_marks) + ((attempted_question - correct_answer)*negative_marks)
        print(function.user_input)
        end_msg = "Thank you for attempting the quiz!!\n" \
                  "Total questions : " + str(question_number) + "\n" \
                  "Correct answer : " + str(correct_answer) + "\n" \
                  "Incorrect answer : " + str(attempted_question - correct_answer) + "\n" \
                  "Not attempted : " + str(question_number - attempted_question) + "\n"\
                  "Points score : " + str(points) + "\n"\
                  "Total time taken : " + str(total_time) + "\n"\
                "Type *analysis* to get detailed analysis of the quiz \n"\
                "Type *start* to try other quizzes or reattempt this quiz \n Happy Quizzing!!"
        msg.body(end_msg)
    elif 'analysis' in incoming_msg:
        msg.body("Detailed Analysis")
        print(quiz_size)
        for i in range(quiz_size):
            msg_analyse = resp.message()
            msg_analyse.body(function.analyze_fun(i))
    elif ongoing_quiz:
        if 'next' in incoming_msg:
            if question_number == quiz_size :
                ongoing_quiz = False
                global_end_time = time.time()
                total_time = (global_end_time - global_start_time).__round__(2)
                points = (correct_answer * positive_marks) + ((attempted_question - correct_answer) * negative_marks)
                end_msg = "Thank you for attempting the quiz!!\n" \
                          "Total questions : " + str(question_number) + "\n" \
                           "Correct answer : " + str(correct_answer) + "\n" \
                           "Incorrect answer : " + str(attempted_question - correct_answer) + "\n" \
                           "Not attempted : " + str(question_number - attempted_question) + "\n" \
                            "Points score : " + str(points) + "\n" \
                             "Total time taken : " + str(total_time) + "\n" \
                              "Type *analysis* to get detailed analysis of the quiz \n" \
                              "Type *start* to try other quizzes or reattempt this quiz \n Happy Quizzing!!"
                msg.body(end_msg)
            else:
                question_number = question_number + 1
                question_msg = function.question(question_number) + "\n\n" + function.option(question_number) + "\n"
                msg.body(question_msg)
                global_start_time = time.time()
                start_time = time.time()
        elif incoming_msg in ['a', 'b', 'c', 'd']:
            if function.answer(question_number, incoming_msg):
                end_time = time.time()
                time_taken = (end_time - start_time).__round__(2)
                #user_answer[question_number-1] = incoming_msg
                ans_msg = "Yay!! that's a correct answer\n"\
                            "Time taken: " + str(time_taken)
                msg.body(ans_msg)
                attempted_question = attempted_question + 1
                correct_answer = correct_answer + 1
                function.user_input.at[question_number -1,'Answer'] = incoming_msg.upper()
                function.user_input.at[question_number - 1,'Result'] = True
                function.user_input.at[question_number - 1,'Time'] = time_taken


            else:
                end_time = time.time()
                time_taken = (end_time - start_time).__round__(2)
                #user_answer[question_number-1] = incoming_msg
                ans_msg = "That's incorrect answer\n"\
                            "Time taken: " + str(time_taken) + "\n"
                msg.body(ans_msg)
                attempted_question = attempted_question + 1
                function.user_input.at[question_number - 1,'Answer'] = incoming_msg.upper()
                function.user_input.at[question_number - 1,'Result'] = False
                function.user_input.at[question_number - 1,'Time'] = time_taken
            if question_number == quiz_size:
                ongoing_quiz = False
                global_end_time = time.time()
                total_time = (global_end_time - global_start_time).__round__(2)
                points = (correct_answer * positive_marks) + ((attempted_question - correct_answer) * negative_marks)
                end_msg = "Thank you for attempting the quiz!!\n" \
                          "Total questions : " + str(question_number) + "\n" \
                           "Correct answer : " + str(correct_answer) + "\n" \
                           "Incorrect answer : " + str(attempted_question - correct_answer) + "\n" \
                           "Not attempted : " + str(question_number - attempted_question) + "\n" \
                           "Points score : " + str(points) + "\n" \
                            "Total time taken : " + str(total_time) + "\n" \
                            "Type *analysis* to get detailed analysis of the quiz \n" \
                            "Type *start* to try other quizzes or reattempt this quiz \n Happy Quizzing!!"
                msg_end = resp.message()
                msg_end.body(end_msg)
            else:
                msg_next = resp.message()
                question_number = question_number + 1
                question_msg = function.question(question_number) + "\n\n" + function.option(question_number) + "\n"
                msg_next.body(question_msg)
                start_time = time.time()
        else:
            ans_msg = "Please select among *A/B/C/D* \nor type *next* to move to next question! \n type *quit* to end the quiz"
            msg.body(ans_msg)
    else:
        msg.body("Sorry, I did not understand the message")
    return str(resp)


if __name__ == '__main__':
    app.run(debug=True)

