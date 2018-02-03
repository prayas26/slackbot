# -*- coding: utf-8 -*-
import json
import bot
from flask import Flask, request, make_response, render_template
import db
import string
import random
import smtplib

pyBot = bot.Bot()
slack = pyBot.client
database = db.Database()

app = Flask(__name__)
    
def id_generator(size=10, chars=string.ascii_lowercase + string.digits):
    x = ''.join(random.choice(chars) for _ in range(size))
    print(x)
    return x

def _event_handler(event_type, slack_event):
    if 'username' in slack_event["event"]:
        pass
    else:
        if event_type == "message":
            query_text = slack_event["event"]["text"]
            query_channel = slack_event["event"]["channel"]
            team_id = slack_event["team_id"]
            pyBot.handle_command(query_channel, query_text, slack_event, team_id)
    return make_response("hello", 200)

@app.route("/signup", methods=["POST"])
def signup():
    fn = request.form["firstname"]
    ln = request.form["lastname"]
    email_id = request.form["eid"]
    url = request.form["url"]
    space = request.form["spacekey"]
    pyBot.new_func(fn, ln, email_id, url, space)
    check = database.verify_generate(url, space)

    if check == None:
        id_token = id_generator()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("id@email.com", "your_password")
        subject = "WikiBot OTP"
        print "hey hello"
        txt = "Your OTP for WikiBot login is '"+id_token+"'"
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % ("prayas.mittal@gmail.com", email_id, subject, txt)
        server.sendmail("prayas.mittal@gmail.com", email_id, message)
        server.close()
        print id_token
        pyBot.store_token(id_token)
        return render_template("generate.html")
    else:
        return render_template("failed.html", fn=fn, url=url)

@app.route("/generate", methods=["GET", "POST"])
def check_token():
    secret = request.form["token"]
    ch_token = pyBot.lis1[0]
    print ch_token
    print secret
    if ch_token != secret:
        return render_template("tokenerror.html")
    else:
        fn = pyBot.lis[0]
        ln = pyBot.lis[1]
        email_id = pyBot.lis[2]
        url = pyBot.lis[3]
        space = pyBot.lis[4]
        token = pyBot.lis1[0]
        database.create_creds(fn, ln ,email_id, url, space, token)
        client_id = pyBot.oauth['client_id']
        scope = pyBot.oauth['scope']
        return render_template("install.html", client_id=client_id, scope=scope)

@app.route("/login", methods=["POST"])
def user_login():
    url = request.form["url"]
    space = request.form["spacekey"]
    return render_template("verify.html", url=url, space=space)

@app.route("/verify", methods=["POST"])
def verify_user():
    url = request.form["url"]
    space = request.form["spacekey"]
    token = request.form["token"]
    check_db = database.check_url_token(url, token)
    if check_db == None:
        return render_template("tokenerror.html")
    else:
        client_id = pyBot.oauth['client_id']
        scope = pyBot.oauth['scope']
        print client_id, scope
        return render_template("install.html", client_id=client_id, scope=scope)

# installation page for the bot
@app.route("/install", methods=["GET", "POST"])
def pre_install():
    client_id = pyBot.oauth["client_id"]
    scope = pyBot.oauth["scope"]
    fn = pyBot.lis[0]
    ln = pyBot.lis[1]
    email = pyBot.lis[2]
    url = pyBot.lis[3]
    space = pyBot.lis[4]
    token = pyBot.lis1
    return render_template("install.html", client_id=client_id, scope=scope)

#thanks page after installation is successful
@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    code_arg = request.args.get('code')
    url = pyBot.lis[3]
    space = pyBot.lis[4]
    pyBot.auth(code_arg, url, space)
    return render_template("thanks.html")

# triggers when any event is created or triggered 
@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data) # stores the information about event in the variable
    print slack_event
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })
    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)
        make_response(message, 403, {"X-Slack-No-Retry": 1})
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        if 'username' in slack_event["event"]: # validates if the event is triggered by user and not by the bot
            pass
        else:
            print "event_handler"
            return _event_handler(event_type, slack_event)
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

if __name__ == '__main__':
    app.run(debug=True)
