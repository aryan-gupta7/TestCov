from flask import Flask, render_template,request,redirect,url_for
import sqlite3 as sql
import psycopg2
import os

app = Flask(__name__)
DATABASE_URL = os.environment.get['DATABASE_URL']
symptoms=[90,70,59,40,35,31,27,20,15,10]

def createtable():
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

def probablity(ans):
    percentage = 0
    for i in range(len(ans)):
        if ans[i] == "YES":
            percentage += max(100 - symptoms[i],symptoms[i])
        else:
            percentage += min(symptoms[i],100-symptoms[i])
    return percentage//len(ans)

@app.route("/")
def main():
    try:createtable()
    except:pass
    return redirect(url_for("home"))

@app.route("/home", methods=['GET', 'POST'])
def home():
    tests = "We have already done free "+str(total_test())+" succesfull tests!"
    if request.method == 'GET':
        return render_template("home.html", test=tests)

    else:
        response = request.form['Response']
        if response == "About Us":
            return redirect(url_for("AboutUs"))
        elif response == "Test Now":
            return redirect(url_for("Testing"))
        return redirect(url_for("home"))

@app.route("/AboutUs", methods=['GET', 'POST'])
def AboutUs():
    if request.method == "GET":
        return render_template("Aboutus.html")
    
    else:
        return redirect(url_for("home"))

@app.route("/Testing", methods=['GET', 'POST'])
def Testing():
    if request.method == "GET":
        return render_template("test.html")

    else:
        questions = ['a','b','c','d','e','f','g','h','i','j']
        ans = []
        for question in questions:
            try:
                ans.append(request.form[question])
            except:
                return redirect(url_for("error"))
        plus_one_test()
        return redirect(url_for("result",percentage=probablity(ans)))

@app.route("/Testing/error")
def error():
    return render_template("error.html", code = "Select all fields")

@app.route("/Testing/result/<percentage>", methods=['GET', 'POST'])
def result(percentage):
    if request.method == "GET":
        return render_template("result.html", probab=percentage)
    else:
        response = request.form['Response']
        if response == "About Us":
            return redirect(url_for("AboutUs"))
        elif response == "Test Again":
            return redirect(url_for("Testing"))
        return redirect(url_for("home"))

if __name__ == "__main__":
    app.run()
