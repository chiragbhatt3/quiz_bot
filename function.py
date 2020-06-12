import pandas as pd
from database import *
from decimal import Decimal


def default_fun(n):
    default_msg = "Hi " + n + " I am SIRPI QuizBot\n" \
                              "Type *1* to start the quiz\n" \
                              "Type *2* for help\n" \
                              "Type *3* to learn more about me\n" \
                              "Type *4* to view past performance\n"
    return default_msg


def help_fun():
    help_msg = "Hi, I am a Quiz Chatbot\nWith me you can try out various quizzes and analyze your performance\n" \
               "To try different quizzes type *1*\nYou will get a list of available quizzes, select any quiz by typing\nthe quiz code and select the format\n" \
               "There you go!\nAttempt the quiz and after the quiz you can type *#* to analyze your performance\nHappy Quizzing!! "
    return help_msg


def learn_fun():
    learn_msg = "Hi, I am SIRPI QuizBot! \n" \
                "I conduct quizzes\nIf you want to conduct a quiz then please\nvisit to xyz.com and upload your quiz\n" \
                "Type *1* to start the quiz\n" \
                "Type *2* for help\n"
    return learn_msg


def start_fun():
    start_msg = "Here are the list of available quizzes \n" \
                "Type the quiz code to start the quiz\n" \
                "Type *0* to exit"
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
                                                                                               "C. " + str(
            data.iloc[number - 1][
                3]) + "\n" \
                      "D. " + str(data.iloc[number - 1][4]) + "\n"


def analyze_fun(j):
    analyze_msg = "\n" + data.iloc[j]['Question'] + "\n" + \
                  option(j + 1) + "Your response: " + user_input.iloc[j]['Answer'] + \
                  "\nCorrect response: " + user_input.iloc[j]['Correct'] + "\n"
    return analyze_msg


data = pd.DataFrame()
quiz_size = data.shape[0]
user_input = pd.DataFrame()


def set_quiz_fun(code):
    global data
    global quiz_size
    global user_input
    data = quiz_data_pd[(quiz_data_pd.Code == code)]
    quiz_size = data.shape[0]
    user_input = pd.DataFrame(list(zip(["NA"] * quiz_size, [False] * quiz_size, [0] * quiz_size)),
                              columns=['Answer', 'Result', 'Time'])
    user_input['Correct'] = data['Correct'].values


def past_performace_fun(number, j):
    udata = user_data_pd[(user_data_pd.Phone == number)]
    qsize = udata.shape[0]
    print(number)
    print(qsize)
    num = qsize - 1 - j
    print(num)
    if num < 0:
        return " "
    else:
        qcode = udata.iloc[num][2]
        qname = select_quiz_name_fun(qcode)
        qmname = select_quiz_master_name_fun(qcode)
        msg_per = qname + " by " + qmname + "\nOn: " + udata.iloc[num][3].strftime('%Y/%m/%d') + "\n" \
                                                                                                 "Points scored: " + str(
            udata.iloc[num][6]) + "\n" \
                                  "Time taken: " + str(udata.iloc[num][5]) + "\n"
        print(msg_per)
        return msg_per


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


def end_msg_fun(q, c, a, p, t):
    end_msg = "Thank you for attempting the quiz!!\n" \
              "Total questions : " + str(q) + "\n" \
                                              "Correct answer : " + str(c) + "\n" \
                                                                             "Incorrect answer : " + str(a - c) + "\n" \
                                                                                                                  "Not attempted : " + str(
        q - a) + "\n" \
                 "Points scored : " + str(p) + "\n" \
                                               "Total time taken : " + str(t) + "\n" \
                                                                                "Type *#* to get analysis of the quiz \n" \
                                                                                "Type *1* to try other quizzes\n" \
                                                                                "Type *0* to exit \nHappy Quizzing!!"
    return end_msg


def add_to_user_data(phone_num, name, code, now, then, time, points, form):
    now_format = now.strftime('%Y-%m-%d %H:%M:%S')
    then_format = then.strftime('%Y-%m-%d %H:%M:%S')
    point_format = points.item()
    val = (phone_num, name, code, now_format, then_format, time, point_format, form)
    try:
        mariadb_connection = mariadb.connect(user=credentials.USER_NAME,
                                             password=credentials.PASSWORD,
                                             database=credentials.DB_NAME,
                                             host=credentials.HOST_NAME)
        cursor = mariadb_connection.cursor()
        cursor.execute("INSERT INTO user_data VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", val)
        mariadb_connection.commit()
        print(cursor.rowcount, "Record inserted successfully into user_data table")
        cursor.close()
    except mariadb.Error as error:
        print("Failed to insert record into user_data table".format(error))
    finally:
        if (mariadb_connection.is_connected()):
            mariadb_connection.close()
            print("MariaDB connection is closed")


def new_user(phone_num):
    return not phone_num in user_info_pd['Phone'].tolist()


def add_new_user(phone_num, name):
    try:
        mariadb_connection = mariadb.connect(user=credentials.USER_NAME,
                                             password=credentials.PASSWORD,
                                             database=credentials.DB_NAME,
                                             host=credentials.HOST_NAME)
        cursor = mariadb_connection.cursor()
        val = (phone_num, name)
        cursor.execute("INSERT INTO user_info VALUES (%s,%s)", val)
        mariadb_connection.commit()
        print(cursor.rowcount, "Record inserted successfully into user_info table")
        cursor.close()
    except mariadb.Error as error:
        print("Failed to insert record into user_info table".format(error))
    finally:
        print(user_info_pd)
        if (mariadb_connection.is_connected()):
            mariadb_connection.close()
            print("MariaDB connection is closed")


def get_user_name_fun(phone_num):
    return user_info_pd[(user_info_pd.Phone == phone_num)].iloc[0][1]
