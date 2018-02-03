import pymysql.cursors

class Database(object):
    def __init__(self):
        self.host = "database link"
        self.usrnme = "username"
        self.pswrd = "password"
        self.dbnme = "db_name"
        self.connection = pymysql.connect(host=self.host,
                             user=self.usrnme,
                             password=self.pswrd,
                             db=self.dbnme,
                             cursorclass=pymysql.cursors.DictCursor)

    def con_auth(self, ti, bi, b_a_t, ui):
        with self.connection.cursor() as cursor:
            com = "SELECT * FROM users WHERE team_id='"+ti+"'"
            cursor.execute(com)
            tid = cursor.fetchone()
            if tid == None:
                sql = "INSERT INTO users VALUES('"+ti+"', '"+bi+"', '"+b_a_t+"', '"+ui+"')"
                cursor.execute(sql)
            else:
                sql_com = "UPDATE users SET user_id = '"+ui+"', bot_token = '"+b_a_t+"', bot_id = '"+bi+"' WHERE team_id = '"+ti+"'"
                cursor.execute(sql_com)
        self.connection.commit()

    def con_check(self, slack_event, team_id):
        team = slack_event["team_id"]
        with self.connection.cursor() as cursor:
            sql1 = "SELECT bot_token, bot_id FROM users where team_id='"+team_id+"'"
            cursor.execute(sql1)
            row = cursor.fetchone()
        self.connection.commit()
        return row

    def user_details(self, ti, site, space):
        with self.connection.cursor() as cursor:
            com = "SELECT * FROM user_info WHERE team_id='"+ti+"'"
            cursor.execute(com)
            tid = cursor.fetchone()
            if tid == None:
                sql = "INSERT INTO user_info VALUES('"+ti+"', '"+site+"', '"+space+"')"
                cursor.execute(sql)
            else:
                sql_com = "UPDATE user_info SET url = '"+site+"', spacekey = '"+space+"' WHERE team_id = '"+ti+"'"
                cursor.execute(sql_com)
        self.connection.commit()

    def con_check_creds(self, slack_event, team_id):
        team = slack_event["team_id"]
        with self.connection.cursor() as cursor:
            sql1 = "SELECT * FROM user_info where team_id='"+team_id+"'"
            cursor.execute(sql1)
            row = cursor.fetchone()
        self.connection.commit()
        return row

    def verify_generate(self, url, spacekey):
        with self.connection.cursor() as cursor:
            sql2 = "SELECT * FROM credentials WHERE url='"+url+"' and space='"+spacekey+"'"
            cursor.execute(sql2)
            row = cursor.fetchone()
        self.connection.commit()
        return row

    def check_token(self, email, secret):
        with self.connection.cursor() as cursor:
            sql3 = "SELECT * FROM credentials WHERE eid='"+email+"' and token='"+secret+"'"
            cursor.execute(sql3)
            row = cursor.fetchone()
        self.connection.commit()
        return row

    def create_creds(self, fn, ln, email_id, url, space, token):
        with self.connection.cursor() as cursor:
            sql4 = "INSERT INTO credentials VALUES('"+token+"', '"+fn+"', '"+ln+"', '"+email_id+"', '"+url+"', '"+space+"')"
            cursor.execute(sql4)
        self.connection.commit()

    def check_url_token(self, url, token):
        with self.connection.cursor() as cursor:
            sql5 = "SELECT * FROM credentials WHERE url='"+url+"' and token='"+token+"'"
            cursor.execute(sql5)
            row = cursor.fetchone()
        self.connection.commit()
        return row

    def put_token(self, token):
        with self.connection.cursor() as cursor:
            sql1 = "INSERT INTO tok VALUES('"+token+"')"
            cursor.execute(sql1)
            row = cursor.fetchone()
        self.connection.commit()
        return row