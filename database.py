import pandas as pd
import mysql.connector as mariadb
import credentials
from datetime import *


mariadb_connection = mariadb.connect(user=credentials.USER_NAME,
                                     password=credentials.PASSWORD,
                                     database=credentials.DB_NAME,
                                     host=credentials.HOST_NAME)

def get_quiz_info():
    cursor = mariadb_connection.cursor()
    today = datetime.now().strftime("%Y") + "-" + datetime.now().strftime("%m") + "-" + datetime.now().strftime("%d")
    today_tuple = (today,today)
    info_query = "SELECT * FROM quiz_info where start_date <= %s AND end_date >= %s"
    cursor.execute(info_query,today_tuple)
    quiz_info = cursor.fetchall()
    return  pd.DataFrame(quiz_info, columns=['Quiz_code','Quiz_name', 'QM_name','Total_question','Positive_marks','Negative_marks','Upload_date','Start_date','End_date'])

def get_all_quiz_info():
    cursor = mariadb_connection.cursor()
    today = datetime.now().strftime("%Y") + "-" + datetime.now().strftime("%m") + "-" + datetime.now().strftime("%d")
    today_tuple = (today,)
    info_query = "SELECT * FROM quiz_info where start_date <= %s"
    cursor.execute(info_query, today_tuple)
    quiz_info = cursor.fetchall()
    return pd.DataFrame(quiz_info, columns=['Quiz_code', 'Quiz_name', 'QM_name', 'Total_question', 'Positive_marks',
                                            'Negative_marks', 'Upload_date', 'Start_date', 'End_date'])

def get_quiz_data(code):
    print(code)
    code_tuple = (code,)
    try:
        cursor = mariadb_connection.cursor()
        cursor.execute("SELECT question,A,B,C,D,correct FROM quiz_data WHERE quiz_code = %s", code_tuple)
        quiz_data = cursor.fetchall()
        print(quiz_data)
        quiz_data_pd = pd.DataFrame(quiz_data,columns=['Question', 'A', 'B', 'C', 'D','Correct'])
        print("Quiz data fetched successfully ")
        cursor.close()
        return quiz_data_pd
    except mariadb.Error as error:
        cursor.close()
        print("Failed to get quiz data".format(error))
        return pd.DataFrame()

def get_user_name(phone):
    phone_tuple = (phone,)
    try:
        cursor = mariadb_connection.cursor()
        user_name_info_query = "SELECT * FROM user_info WHERE phone_num = %s"
        cursor.execute(user_name_info_query, phone_tuple)
        user_name = cursor.fetchall()
        user_name_pd = pd.DataFrame(user_name,columns=['Phone', 'Name'])
        print("Successfully fetches user name")
        if user_name_pd.shape[0] == 0:
            return "new user"
        else:
            return user_name_pd.iloc[0][1]
        cursor.close()
    except mariadb.Error as error:
        print("Failed to get user name".format(error))

def add_new_user(phone_num,name):
    val = (phone_num, name)
    try:
        cursor = mariadb_connection.cursor()
        cursor.execute("INSERT INTO user_info VALUES (%s,%s)", val)
        mariadb_connection.commit()
        print(cursor.rowcount, "Record inserted successfully into user_info table")
        cursor.close()
    except mariadb.Error as error:
        cursor.close()
        print("Failed to insert record into user_info table".format(error))

def get_leaderboard(code):
    code_tuple = (code,)
    try:
        cursor = mariadb_connection.cursor()
        user_query = "SELECT * FROM user_data WHERE quiz_code = %s"
        cursor.execute(user_query,code_tuple)
        leaderboard_data = cursor.fetchall()
        cursor.close()
        print("Successfully fetched leaderboard")
        leaderboard_data_pd = pd.DataFrame(leaderboard_data, columns=['Phone','Name','Code','Start', 'End', 'time', 'points', 'format'])
        leaderboard_data_pd = leaderboard_data_pd.groupby(['Name','Code'])['points'].max().reset_index().sort_values(by='points',ascending=False)
        lb_size = leaderboard_data_pd.shape[0]
        print(lb_size)
        if lb_size == 0:
            return "No one has attempted the quiz"
        elif lb_size == 1:
            return "1. " + leaderboard_data_pd.loc[0]['Name'] + "  " + str(leaderboard_data_pd.iloc[0]['points']) + "\n"
        elif lb_size == 2:
            return "1. " + leaderboard_data_pd.iloc[0]['Name'] + "  " + str(leaderboard_data_pd.iloc[0]['points']) + "\n" \
                   "2. " + leaderboard_data_pd.iloc[1]['Name'] + "  " + str(leaderboard_data_pd.iloc[1]['points']) + "\n"
        else:
            return "1. " + leaderboard_data_pd.iloc[0]['Name'] + "  " + str(leaderboard_data_pd.iloc[0]['points']) + "\n" \
                   "2. " + leaderboard_data_pd.iloc[1]['Name'] + "  " + str(leaderboard_data_pd.iloc[1]['points']) + "\n" \
                   "3. " + leaderboard_data_pd.iloc[2]['Name'] + "  " + str(leaderboard_data_pd.iloc[2]['points']) + "\n"
    except mariadb.Error as error:
        cursor.close()
        print("Failed to get leaderboard".format(error))
        return ""

def future_quiz_info_fun():
    try:
        cursor = mariadb_connection.cursor()
        today = datetime.now().strftime("%Y") + "-" + datetime.now().strftime("%m") + "-" + datetime.now().strftime("%d")
        today_tuple = (today,)
        future_info_query = "SELECT * FROM quiz_info where start_date > %s"
        cursor.execute(future_info_query,today_tuple)
        future_quiz_info = cursor.fetchall()
        print("Successfully fetched future quizzes")
        future_quiz_info_pd = pd.DataFrame(future_quiz_info,
                                           columns=['Quiz_code', 'Quiz_name', 'QM_name', 'Total_question',
                                                    'Positive_marks',
                                                    'Negative_marks', 'Upload_date', 'Start_date', 'End_date'])
        cursor.close()
        print("Successfully fetched future quizzes")
        return future_quiz_info_pd
    except mariadb.Error as error:
        cursor.close()
        print("Unable to fetch future quizzes")
        return pd.DataFrame()

def past_user_performace_fun(number):
    number_tuple = (number,)
    quiz_info = get_all_quiz_info()
    print(quiz_info)
    try:
        cursor = mariadb_connection.cursor()
        user_query = "SELECT * FROM user_data WHERE phone_num = %s"
        cursor.execute(user_query,number_tuple)
        user_data = cursor.fetchall()
        cursor.close()
        print("Successfully fetched user data")
        user_data_pd = pd.DataFrame(user_data, columns=['Phone', 'Name', 'Code', 'Start', 'End', 'time', 'points', 'format'])
        print(user_data_pd)
        qsize = user_data_pd.shape[0]
        if qsize == 0:
            return "No past performance \nPlease attempt quiz first\n"
        j = qsize - 1
        msg_arr = []
        while j >= qsize - 5:
            if j < 0:
                msg_arr.append("")
                j = j - 1
            else:
                qcode = user_data_pd.iloc[j][2]
                selected_quiz = quiz_info[quiz_info.Quiz_code == qcode]
                qname = selected_quiz.iloc[0][1]
                qmname = selected_quiz.iloc[0][2]
                msg_pp = qname + " by " + qmname + "\nOn: " + user_data_pd.iloc[j][3].strftime('%Y/%m/%d') + "\n" \
                         "Points scored: " + str(user_data_pd.iloc[j][6]) + "\n" \
                         "Time taken: " + str(user_data_pd.iloc[j][5]) + "\n"
                msg_arr.append(msg_pp)
                j = j - 1
        return msg_arr[0] + "\n" + msg_arr[1] +"\n" +  msg_arr[2] +"\n"+ msg_arr[3] +"\n"+ msg_arr[4]
    except mariadb.Error as error:
        cursor.close()
        return "Unable to access user data"

def add_to_user_data(phone_num, name, code, now, then, time, points, form):
    now_format = now.strftime('%Y-%m-%d %H:%M:%S')
    then_format = then.strftime('%Y-%m-%d %H:%M:%S')
    point_format = points.item()
    val = (phone_num, name, code, now_format, then_format, time, point_format, form)
    cursor = mariadb_connection.cursor()
    try:
        cursor.execute("INSERT INTO user_data VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", val)
        mariadb_connection.commit()
        print(cursor.rowcount, "Record inserted successfully into user_data table")
        cursor.close()
    except mariadb.Error as error:
        cursor.close()
        print("Failed to insert record into user_data table".format(error))






