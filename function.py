import pandas as pd
from database import *

def default_fun():
    default_msg = "Hi! I'm SIRPI Bot.\n" \
                  "Type *start* to get started\n" \
                  "Type *help* for help \n" \
                  "Type *learn* to know more about me!"
    return default_msg


def help_fun():
    help_msg = "type *start* to start the quiz.\n" \
               "type *quit* to end the quiz.\n" \
               "type *next* to attempt next question."
    return help_msg


def learn_fun():
    learn_msg = "Hi, I am SIRPI Bot! \n" \
                "I conduct quizzes"
    return learn_msg


def start_fun():
    start_msg = "Hi, here are the list of available quizzes \n" \
                "Type the quiz code of the quiz you want to attempt"
    return start_msg


def question(number):
    if number > quiz_size:
        return "no more questions!"
    else:
        return data.iloc[number - 1][0]


def answer(number, ans):
    if number > quiz_size:
        return False
    else:
        if data.iloc[number - 1][5].lower() == ans:
            return True
        else:
            return False


def option(number):
    if number > quiz_size:
        return "no more questions!"
    else:
        return "A. " + str(data.iloc[number - 1][1]) + "\n" \
                                                  "B. " + str(data.iloc[number - 1][2]) + "\n" \
                                                                                     "C. " + str(data.iloc[number - 1][
                   3])+ "\n" \
                        "D. " + str(data.iloc[number - 1][4]) + "\n"




def analyze_fun(j):
    analyze_msg = "\n" + data.iloc[j]['Question'] + "\n" + \
                  option(j+1) + "Your response: " +  user_input.iloc[j]['Answer'] + \
                  "\nCorrect response: " + user_input.iloc[j]['Correct'] + "\n"
    return analyze_msg

def select_quiz_fun(code):
    return code in quiz_info_pd['Code'].tolist()


def select_quiz_name_fun(code):
    return quiz_info_pd[(quiz_info_pd.Code == code)].iloc[0][0]
def select_quiz_master_name_fun(code):
    return quiz_info_pd[(quiz_info_pd.Code == code)].iloc[0][1]
def postive_marks_fun(code):
    return quiz_info_pd[(quiz_info_pd.Code == code)].iloc[0][3]
def negative_marks_fun(code):
    return quiz_info_pd[(quiz_info_pd.Code == code)].iloc[0][4]
