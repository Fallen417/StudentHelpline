from flask import Flask, render_template, request, session
from threading import Thread
import shelve
import os
from random import randint
from datetime import datetime

key=os.getenv("key")
app = Flask('')
app.secret_key=bytes(randint(1,10000))

@app.route("/")
def home():
  if "username" in session:
    return render_template("ask.html")
  else:
    return render_template("home.html")

@app.route("/register")
def empty_register():
  return render_template("register.html")

@app.route("/register",methods=["POST"])
def register():
  username=request.form["username"]
  password=request.form["password"]
  confirm_password=request.form["confirm-password"]
  if password!=confirm_password:
    return render_template("register.html",error="Passwords do not match!")
  with shelve.open("accounts") as accounts:
    if username in accounts:
      return render_template("register.html",error="Username taken!")
    accounts[username]=(username,password)
    return render_template("register.html",success="Account successfully created!")

@app.route("/login")
def empty_login():
  return render_template("login.html")

@app.route("/login",methods=["POST"])
def login():
  username=request.form["username"]
  password=request.form["password"]
  with shelve.open("accounts") as accounts:
    if username in accounts:
      if accounts[username]==(username,password):
        session["username"]=username
        return render_template("ask.html")
      else:
        return render_template("login.html",failed="Incorrect username or password")
    else:
      return render_template("login.html",failed="Incorrect username or password")

@app.route("/ask", methods=["GET", "POST"])
def ask():
  if "username" in session:
    if request.method == "GET":
      return render_template("ask.html")
    else:
      prob = request.form.get("prob")
      probs = open("INFO.txt", "a")
      probs.write(prob + "\n")
      probs.close()
      return render_template("ask.html", prob=prob)
  return render_template("home.html")

@app.route("/reply", methods=["GET"])
def replies():
  if "username" in session:
    probs = open("INFO.txt", "r")
    problem = probs.readlines()
    probs.close()
    replying = open("REPLY.txt", "r")
    replies = replying.readlines()
    replying.close()
    return render_template("replies.html", problem=problem, replies=replies)
  return render_template("home.html")

@app.route("/settings")
def settings():
  if "username" in session:
    return render_template("home2.html")
  else:
    return render_template("home.html")

@app.route("/change")
def empty_change():
  if "username" in session:
    return render_template("change.html")
  return render_template("home.html")

@app.route("/change", methods=["GET", "POST"])
def change():
  if "username" in session:
    password=request.form["current"]
    new=request.form["new"]
    confirm_new=request.form["confirm-new"]
    with shelve.open("accounts") as accounts:
      if (session["username"],password)!=accounts[session["username"]]:
        return render_template("change.html",error="Incorrect current password")
      if new!=confirm_new:
        return render_template("change.html",error="Passwords do not match!")
      accounts[session["username"]]=(session["username"],new)
      return render_template("change.html",success="Password successfully changed!")
  return render_template("home.html")

@app.route("/admin")
def admin():
  if "admin" in session:
    with shelve.open("accounts") as accounts:
      return render_template("admin.html",accounts=accounts)
  return render_template("admin_login.html")

@app.route("/admin",methods=["POST"])
def admin_actual():
  if "admin" in session:
    username=request.form["username"]
    password=request.form["password"]
    confirm_password=request.form["confirm-password"]
    delete=request.form["delete"]
    with shelve.open("accounts") as accounts:
      if delete=="":
        if username not in accounts:
          return render_template("admin.html",accounts=accounts,error="Account does not exist!")
        if password!=confirm_password:
          return render_template("admin.html",accounts=accounts,error="Passwords do not match!")
        accounts[username]=(username,password)
        return render_template("admin.html",accounts=accounts,success="Password successfully changed!")
      else:
        if delete in accounts:
          del accounts[delete]
          return render_template("admin.html",accounts=accounts,success="Account successfully deleted!")
        else:
          return render_template("admin.html",accounts=accounts,error="Account does not exist!") 
  else:
    password=request.form["password"]
    date = datetime.now()
    dater = date.strftime("%A%B")
    datecode = ''.join(str(ord(c)) for c in dater)
    if password==datecode:  #https://www.browserling.com/tools/text-to-ascii
    #871011001101011151009712165112114105108
      session["admin"]="yep"
      return render_template("admin.html")
    else:
      return render_template("admin_login.html",error="Incorrect admin password!")

@app.route("/admin-questions", methods = ["GET", "POST"])
def admin_questions():
  if "admin" in session:
    if request.method== "GET":
        probs = open("INFO.txt", "r")
        problem = probs.readlines()
        probs.close()
        replying = open("REPLY.txt", "r")
        replies = replying.readlines()
        replying.close()
        return render_template("admin_questions.html", problem=problem, replies=replies)
    else:
      probs = open("INFO.txt", "r")
      problems = probs.readlines()
      probs.close()
      ans = request.form.get("ans")
      reply = open("REPLY.txt", "a")
      reply.write(str(ans) + '\n')
      reply.close()
      replying2 = open("REPLY.txt", "r")
      replies2 = replying2.readlines()
      replying2.close()
      return render_template("admin_questions.html", problems=problems, replies2=replies2)
  else:
    return render_template("admin_login.html")

@app.route("/deleteall")
def deleteall():
  if "admin" in session:
    filey = open("INFO.txt","r+")
    filey.truncate(0)
    filey.close()
    filey2 = open("REPLY.txt","r+")
    filey2.truncate(0)
    filey2.close()
    return render_template("admin.html")
  return render_template("home.html")

@app.route("/spooky")
def spooky():
  return render_template("scary.html")

@app.route("/admin-logout")
def admin_logout():
  session.pop("admin")
  return render_template("home.html")

@app.route("/logout")
def logout():
  session.pop("username",None)
  return render_template("home.html")

def run():
  app.run(host="0.0.0.0", port=8080)

t = Thread(target=run)
t.start()