from flask import Flask
from flaskext.mysql import MySQL
import pymysql

app = Flask(__name__)

mysql = MySQL()
# MySQL Configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'sudheer123'
app.config['MYSQL_DATABASE_DB'] = 'students_data'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


def change_gender_male():
    con = mysql.connect()
    cur = con.cursor(pymysql.cursors.DictCursor)
    data = cur.execute("UPDATE sqldb1 SET gender='Male' WHERE gender='\xa0Male';")
    con.commit()
    cur.close()
    return data

def change_gender_female():
    con = mysql.connect()
    cur = con.cursor(pymysql.cursors.DictCursor)
    data = cur.execute("UPDATE sqldb1 SET gender='Female' WHERE gender='\xa0Female';")
    con.commit()
    cur.close()
    return data