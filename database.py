import pandas as pd
import mysql.connector as mariadb
import credentials

mariadb_connection = mariadb.connect(user=credentials.USER_NAME,
                                     password=credentials.PASSWORD,
                                     database=credentials.DB_NAME,
                                     host=credentials.HOST_NAME)
cursor = mariadb_connection.cursor()

info_query = "SELECT quiz_name,qm_name,quiz_code,positive_marks,negative_marks FROM quiz_table group by quiz_name,qm_name"
cursor.execute(info_query)
quiz_info = cursor.fetchall()
quiz_info_pd = pd.DataFrame(quiz_info, columns=['Quiz', 'QM', 'Code', 'Positive', 'Negative'])

data_query = "SELECT Question,A,B,C,D,Correct,quiz_code FROM quiz_table"
cursor.execute(data_query)
quiz_data = cursor.fetchall()
quiz_data_pd = pd.DataFrame(quiz_data, columns=['Question', 'A', 'B', 'C', 'D', 'Correct', 'Code'])

data = pd.DataFrame()
quiz_size = data.shape[0]
user_input = pd.DataFrame()



def quiz_set_fun(code):
    global data
    global quiz_size
    global user_input
    data = quiz_data_pd[(quiz_data_pd.Code == code)]
    quiz_size = data.shape[0]
    user_input = pd.DataFrame(list(zip(["NA"]*quiz_size,[False]*quiz_size,[0]*quiz_size)),columns =['Answer','Result','Time'])
    user_input['Correct'] = data['Correct'].values