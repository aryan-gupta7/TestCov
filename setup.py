from flask import Flask, request, render_template, redirect, url_for
import psycopg2
import os
import smtplib

app = Flask(__name__)

DATABASE_URL = os.environ['DATABASE_URL']
GMAIL_ID = os.environ['ID']
PASSWORD = os.environ['PASSWORD']
ARYAN_ID = os.environ['ARYAN_ID']
AKSHAT_ID = os.environ['AKSHAT_ID']

names = []
def createtable_tests():
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=con.cursor()
    table="""
        CREATE TABLE total_tests (
            tests TEXT
        )
        """
    cur.execute(table)
    con.commit()
    cur=con.cursor()
    sqlite_insert_with_param = f"INSERT INTO total_tests(tests) VALUES ('0');"
    cur.execute(sqlite_insert_with_param)
    con.commit()

def update(ques, ans):
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=con.cursor()
    sqlite_insert_with_param = f"UPDATE questions_answers SET answer = '{ans}' WHERE question = '{ques}';"
    cur.execute(sqlite_insert_with_param)
    con.commit()

def delete(ques):
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=con.cursor()
    sqlite_insert_with_param = f"DELETE FROM questions_answers WHERE question = '{ques}';"
    cur.execute(sqlite_insert_with_param)
    con.commit()

def total_test():
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=con.cursor()
    cur.execute("SELECT tests FROM total_tests")
    tests=cur.fetchall()
    return int(tests[0][0])

def plus_one_test():
    tests = total_test()
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=con.cursor()
    sqlite_insert_with_param = f"UPDATE total_tests SET tests = '{tests+1}' WHERE tests = '{tests}';"
    cur.execute(sqlite_insert_with_param)
    con.commit()

def createtable():
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=con.cursor()
    table="""
        CREATE TABLE questions_answers (
            name TEXT,
            age TEXT,
            email TEXT,
            question TEXT,
            answer TEXT
        )
        """
    cur.execute(table)
    con.commit()

def retrieve():
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = con.cursor()
    cur.execute("SELECT * FROM questions_answers")
    users = cur.fetchall()
    con.close()
    return users

def enter_data(name,age,email,ques,ans):
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = con.cursor()
    sqlite_insert_with_param = f"INSERT INTO questions_answers(name,age,email,question,answer) VALUES ('{name}','{age}','{email}','{ques}','{ans}');"
    cur.execute(sqlite_insert_with_param)
    con.commit()
    con.close()

def probablity(ans):
    symptoms=[90,70,59,40,35,31,27,20,15,10]
    percentage = 0
    for i in range(len(ans)):
        if ans[i] == "YES":
            percentage += max(100 - symptoms[i],symptoms[i])
        else:
            percentage += min(symptoms[i],100-symptoms[i])
    return percentage//len(ans)

def send_mail(to,subject,message):
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        try:
            s.login(GMAIL_ID, PASSWORD)
        except Exception as e:
            print(f"Couldn't login. {e}")
        try:
            s.sendmail(GMAIL_ID, to, f"Subject: {subject}\n\n{message}")
        except:
            pass
        s.quit()

@app.route('/')
def main():
    try:
        createtable() 
    except:
        pass
    try:
        createtable_tests() 
    except:
        pass
    return redirect(url_for('home'))

@app.route('/home',methods=["GET","POST"])
def home():
    tests_done = total_test()
    text = f"We have already done {tests_done} succesfull tests for free."
    if request.method == "GET":
        return render_template('home.html',test=text)
    else:
        response = request.form["Response"]
        if response == "Test Now":
            return redirect(url_for('test'))
        elif response == "About Us":
            return redirect(url_for('about'))
        elif response == "FAQ(s)":
            return redirect(url_for('faqs'))
        else:
            return render_template('home.html',test=text)

@app.route('/test',methods=["GET","POST"])
def test():
    questions = {"a":"Do you have fever?",
    "b":"Do you feel extremely tired or fatigued?",
    "c":"Do you have dry cough?",
    "d":"Do you have lossed appetite(don't feel hungry)?",
    "e":"Do you have body-aches?",
    "f":"Do you feel shortness or breath?",
    "g":"Does mucus or phlegm comes from your nose?",
    "h":"Do you lost sense of smelling?",
    "i":"Do you have constant pain in chest?",
    "j":"Do you have diarrhea?"
    }
    if request.method == 'GET':
        return render_template('test.html',questions=questions)
    else:
        name = request.form['name']
        questions = ['a','b','c','d','e','f','g','h','i','j']
        ans = []
        for question in questions:
            ans.append(request.form[question])
        plus_one_test()
        names.append(name)
        return redirect(url_for('result',percentage=probablity(ans)))

@app.route('/test/result/<percentage>',methods=['GET','POST'])
def result(percentage):
    if request.method == "GET":
        return render_template("result.html", probab=percentage)
    else:
        response = request.form['Response']
        if response == 'Test Again':
            return redirect(url_for('test'))
        elif response == 'About Us':
            return redirect(url_for('about'))
        elif response == 'FAQ(s)':
            return redirect(url_for('faqs'))


@app.route('/about',methods=['GET','POST'])
def about():
    if request.method == 'GET':
        return render_template('Aboutus.html')
    else:
        response = request.form['Response']
        if response == "Back to Home Page":
            return redirect(url_for("home"))
        else:
            return redirect(url_for('about'))


@app.route('/FAQs',methods=['GET','POST'])
def faqs():
    ques_ans = retrieve()
    questions = []
    for item in ques_ans:
        questions.append((item[0],item[3],item[4]))

    if request.method == 'GET':
        return render_template('faqs.html',questions=questions[::-1])
    else:
        response = request.form['Response']
        if response == "Ask a question":
            return redirect(url_for('ask'))
        else:
            return redirect(url_for('faqs'))


@app.route('/ask',methods=['GET','POST'])
def ask():
    if request.method == 'GET':
        return render_template('ask.html')
    else:
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        question = request.form['question']
        enter_data(name,age,email,question,"Not answered")
        send_mail(AKSHAT_ID,f"A question is asked by {name}",f"The question asked is --\n {question}.\n Answer this as soon as possible.")
        send_mail(ARYAN_ID,f"A question is asked by {name}",f"The question asked is --\n {question}.\n Answer this as soon as possible.")
        return redirect(url_for('asked'))


@app.route('/asked',methods=['GET','POST'])
def asked():
    if request.method == 'GET':
        return render_template('asked.html')
    else:
        response = request.form['Response']
        if response == 'Back to FAQ(s)':
            return redirect(url_for('faqs'))
        elif response == 'Back to Home Page':
            return redirect(url_for('home'))
        else:
            return redirect(url_for('asked'))

@app.route("/answer/<password>", methods = ['GET','POST'])
def answer(password):
    if password == PASSWORD:
        ques_ans = retrieve()
        questions = []
        for item in ques_ans:
            if item[4] == "Not answered":
                questions.append(item)
        if len(questions) == 0:
            questions.append(["NO QUESTIONS UNANSWERED"])
        if request.method == 'GET':
            return render_template("ans.html",ques=questions[0])
        else:
            answer = request.form['answer']
            if answer == "DELETE" or answer == "-d":
                delete(questions[0][3])
            elif answer == "SKIP" or answer == "-s":
                delete(questions[0][3])
                enter_data(questions[0][0],questions[0][1],questions[0][2],questions[0][3],questions[0][4])
            else:
                update(questions[0][3], answer)
                send_mail(questions[0][2],"Answer for your question by TestCov",f"Hi {questions[0][0]},\nWe are Aryan and Akshat from TestCov, your question was {questions[0][3]}\nAnd, Your answer for the question is - \n{answer}")
            return redirect(url_for("answer",password=PASSWORD))
    else:
        return redirect(url_for('home'))

@app.route('/<anything>')
def not_found(anything):
    return render_template('404_not_found.html',anything=anything)

if __name__ == "__main__":
    app.run()
