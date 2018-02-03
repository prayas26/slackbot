import os
import xmlrpc.client
import re
from stripogram import html2text
from slackclient import SlackClient
import db
import wikipedia
import sys
reload(sys)
sys.setdefaultencoding("UTF-8")

database = db.Database()

class Bot(object):
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "wikibot"
        self.emoji = ":robot_face:"
        self.oauth = {"client_id": "############.############",
                      "client_secret": "########################",
                      "scope": "bot"}
        self.verification = "#####"
        self.client = SlackClient("")

    def auth(self, code, url, space):
        auth_response = self.client.api_call(
                                "oauth.access",
                                client_id=self.oauth["client_id"],
                                client_secret=self.oauth["client_secret"],
                                code=code
                                )
        print auth_response
        ui = auth_response["user_id"]
        ti = auth_response["team_id"]
        bi = auth_response["bot"]["bot_user_id"]
        b_a_t = auth_response["bot"]["bot_access_token"]
        database.user_details(ti, url, space)
        database.con_auth(ti, bi, b_a_t, ui)

    def push(self, channel_id, command, slack_event, team_id):
        check = database.con_check(slack_event, team_id)
        print team_id
        if check == None:
            pass
        else:
            print command
            self.client = SlackClient(check["bot_token"])
            row = database.con_check_creds(slack_event, team_id)
            site_URL = row["url"] # base url of the confluence wiki
            spacekey = row["spacekey"] # name of the space
            username = "admin" # username
            pwd = "24061997" # password
            server = xmlrpc.client.ServerProxy(site_URL + "/rpc/xmlrpc")
            token = server.confluence2.login(username, pwd) # create session and login to confluence wiki
            try:
                pages_list = server.confluence2.getPage(token, spacekey, command) # get the contents of the page with the title
                respond = html2text(pages_list["content"]) # converts the html and raw data into plain text
                self.client.api_call("chat.postMessage", channel=channel_id, # send the reply to the slack channel
                                      text=respond)
            except:
                try:
                    pages_list = server.confluence2.getLabelContentByName(token, command) # search with label name and returns list
                    for i in pages_list:
                        respond_page = i["title"]
                        page = server.confluence2.getPage(token, spacekey, respond_page)
                        respond = html2text(page["content"])+"\nFor More:"+i["url"]
                        self.client.api_call("chat.postMessage", channel=channel_id, text=respond)

                except:
                    page_list=server.confluence2.getPages(token, spacekey)
                    j=0
                    for i in page_list:
                        respond_page=i["title"]
                        page=server.confluence2.getPage(token, spacekey, respond_page)
                        respond=html2text(page["content"])
                        respond=str(respond)
                        var = command.encode("utf-8")
                        fin = (str(respond.lower().find(var.lower()))).encode("utf-8")
                        if fin > str(-1):
                            while j == 0:
                                not_found = "The exact query was not found, but I found relevant result in the following -"
                                self.client.api_call("chat.postMessage", channel=channel_id, text=not_found)
                                break
                            self.client.api_call("chat.postMessage", channel=channel_id, text=respond)
                            j=j+1
                            if(j==5):
                                break
                    if j == 0:
                        sorry_msg = "I am afraid, I was unable to find what you searched for.\nHold on, I am searching Wikipedia..\n"
                        self.client.api_call("chat.postMessage", channel=channel_id,
                                          text=sorry_msg)
                        try:
                            wikipage = wikipedia.page(command)
                            summary = wikipedia.summary(command, sentences=5)
                            if len(summary) < 70:
                                summary = wikipage.summary(command)
                            txt = summary+"\nFor more: "+wikipage.url
                        except wikipedia.PageError:
                            txt = "Sorry! No results found on Wikipedia!\n Please check again what you were searching for."
                        except wikipedia.DisambiguationError as e:
                            res = e.options
                            txt1 = "\n".join(res)
                            txt = command+" may refer to:\n"+txt1+"\nTry searching for one of these."

                        self.client.api_call("chat.postMessage", channel=channel_id,
                                              text=txt)

    def handle_command(self, channel_id, command, slack_event, team_id):
        print "handle command"
        if slack_event["event"]["channel"][0] == "C" or slack_event["event"]["channel"][0] == "G":
            if(command[:12]=="<@"+slack_event["authed_users"][0]+">"):
                command=command[13:]
                self.push(channel_id, command, slack_event, team_id)

        elif slack_event["event"]["channel"][0] == "D":
            if(command[:12]=="<@"+slack_event["authed_users"][0]+">"):
                command=command[13:]
                self.push(channel_id, command, slack_event, team_id)
            else:
                print command
                self.push(channel_id, command, slack_event, team_id)

    def new_func(self, fn, ln, email_id, url, space):
        self.lis = [fn, ln, email_id, url, space]

    def store_token(self, token):
        self.lis1 = [token]