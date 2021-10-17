def default_fun(n):
    default_msg = "Hi " + n + " I am SIRPI QuizBot\n" \
                              "Type *1* to start the quiz\n" \
                              "Type *2* for help\n" \
                              "Type *3* to learn more about me\n" \
                              "Type *4* to view past 5 performance\n"\
                              "Type *5* to see the leaderboard\n"\
                               "Type *6* to see the upcoming quizzes\n"
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

def confirm_name_fun(user_name):
    msg_confirm_name = "You have selected " + user_name + " as your name\n"\
                        "Press 1 to continue with this name or type a different name\n"\
                        "This name will be used as your id for all the quizzes\n"
    return msg_confirm_name

def did_not_understand_fun():
    return "Sorry, I did not understand the message!\n"\
            "Type *1* to start the quiz\n" \
            "Type *2* for help\n" \
            "Type *3* to learn more about me\n"\
             "Type *4* to view past performance\n"\
             "Type *5* to see the leaderboard\n"\
              "Type *6* to see the upcoming quizzes\n"

def end_msg_fun(q, c, a, p, t):
    # "Total time taken : " + str(t) + "\n" \
    end_msg = "Thank you for attempting the quiz!!\n" \
              "Total questions : " + str(q) + "\n" \
              "Correct answer : " + str(c) + "\n" \
              "Incorrect answer : " + str(a - c) + "\n" \
               "Not attempted : " + str(q - a) + "\n" \
               "Points scored : " + str(p) + "\n" \
               "Type *#* to get analysis of the quiz \n" \
                 "Type *1* to try other quizzes\n" \
                  "Type *0* to exit \nHappy Quizzing!!"
    return end_msg


