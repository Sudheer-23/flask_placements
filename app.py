# pandas is a library with which we can perform extraction of  data, sending data to database, reading excel files etc.
from colorama import Cursor
import pandas as pd

# importing flask files do that we can implement the functionality for the site
from flask import Flask, request, render_template, redirect, get_flashed_messages, flash, url_for

# imported flask forms for submitting the data
from flask_wtf import FlaskForm
from wtforms import FileField,SubmitField
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename 

# import OS for uploaidng the files and then store the in the respective folders
import os

# import smtplib for semding email
import smtplib  
from email.message import EmailMessage

#import DateTime module 
from datetime import date

# import these modules for connecting the 
from flaskext.mysql import MySQL
import pymysql
from sqlalchemy  import NUMERIC, Float, Numeric, create_engine
import sqlalchemy


app = Flask(__name__)
app.secret_key = "Sudheer"
app.config['UPLOAD_FOLDER_1'] = "students_data"
app.config['UPLOAD_FOLDER_2'] = "updated_students_data"

mysql = MySQL()
# MySQL Configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'sudheer123'
app.config['MYSQL_DATABASE_DB'] = 'students_data'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# This class is for creating the flask forms 
class Upload_excel_file(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

# This route is for the home page that has to be loaded when the site opens
@app.route('/')
def home():
    return render_template('home_page.html')

# This route is for uploading the excel sheet of students data which has to be inserted into the database 
@app.route('/upload_into_students_data',methods = ['GET','POST'])
def upload_into_students_data(): 
    form = Upload_excel_file()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER_1'],secure_filename(file.filename))) # Then save the file
        pymysql.install_as_MySQLdb()
        engine = create_engine('mysql://root:sudheer123@localhost/students_data')
        df1 = pd.read_excel('students_data\sample_sheet.xlsx')
        df1 = pd.read_excel("students_data\sample_sheet.xlsx",dtype = {"total_backlogs":NUMERIC})
        df1.to_sql("sqldb1",con= engine,if_exists ="append")
        return "File has been uploaded."
    return render_template('upload_sheet1.html',form = form)

# This route is for uploading the excel sheet of only those students data which has to be updated in the database 
@app.route('/upload_into_updated_students_data',methods = ['GET','POST'])
def upload_into_updated_students_data(): 
    form = Upload_excel_file()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER_2'],secure_filename(file.filename))) # Then save the file
        pymysql.install_as_MySQLdb()
        engine = create_engine('mysql://root:sudheer123@localhost/students_data')
        df1 = pd.read_excel('updated_students_data\sheet.xlsx')
        #df1 = pd.read_excel("updated_students_data\sheet.xlsx",dtype = {"total_backlogs":Numeric})
        df1.to_sql("sqldb2",con= engine,if_exists ="append")
        return "File has been uploaded."
    return render_template('upload_sheet2.html',form = form)

# This 
@app.route('/test1')
def test1():
    con = mysql.connect()
    cur = con.cursor(pymysql.cursors.DictCursor)
    data = cur.execute('select * from sqldb1;')
    data = cur.fetchall()
    cur.close()
    d = data[0]
    return render_template('output_test_1.html', students = d)

# This route is for testing the functionality of updating the database
@app.route('/test2')
def test2():
    # MYSQL connection and query for selecting all the rows of sqldb2
    con = mysql.connect()
    cur = con.cursor(pymysql.cursors.DictCursor)
    data = cur.execute('select * from sqldb2;')
    data = cur.fetchall()
    cur.close()
    # Dictionary for storing those backlogs as value and roll_no as a key from sqldb2
    d_backlogs_1 = {}
    for i in data:
        d_backlogs_1[(i['roll_no'])] = i['total_backlogs']
    # Dictionary for storing those btech percentages as value and roll_no as a key from sqldb2
    d_btech_per_1 = {}
    for i in data:
        d_btech_per_1[(i['roll_no'])] = i['btech_percentage']
    # Iterate through the keys present in dictionary and now according to the roll no filter those rows whose values have to be updated in the sqldb1 table
    li1 = []
    for i in d_backlogs_1:
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        data1 = cur.execute("select * from sqldb1 where roll_no = '{}';".format(i))
        data1 = cur.fetchall()
        li1.append(data1[0])
        cur.close()
        d = data1[0]
    # Dictionary for storing those backlogs as value and roll_no as a key from sqldb1
    d_backlogs_2 = {}
    for i in li1:
        d_backlogs_2[(i['roll_no'])] = i['total_backlogs']
    # Dictionary for storing those btech percentages as value and roll_no as a key from sqldb1
    d_btech_per_2 = {}
    for i in li1:
        d_btech_per_2[(i['roll_no'])] = i['btech_percentage']
    # Iterate through the keys present in dictionary and now according to the roll no filter those rows whose values have to be updated (i.e values of columns btech_percentage and backlogs count) in the sqldb1 table
    li2 = []
    for i in d_backlogs_1:
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        data2 = cur.execute("UPDATE sqldb1 SET total_backlogs = '{}', btech_percentage = '{}' where roll_no = '{}';".format(d_backlogs_1[i], d_btech_per_1[i], i))
        con.commit()
    return render_template('output_test_2.html',students1 = li1, d_backlogs_1 = d_backlogs_1, d_backlogs_2 = d_backlogs_2, d_btech_per_1 = d_btech_per_1, d_btech_per_2 = d_btech_per_2, students2 = li2)

@app.route('/student_table')
def student_table():
    con = pymysql.connect()
    cur = con.cursor(pymysql.cursors.DictCursor)
    data = cur.execute("SELECT * FROM sqldb1;")
    return render_template('output_test_3.html')


if(__name__) == '__main__':
    app.run(port=2000,debug=True)