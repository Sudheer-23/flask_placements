# pandas is a library with which we can perform extraction of  data, sending data to database, reading excel files etc.

import pandas as pd

# importing flask files do that we can implement the functionality for the site
from flask import Flask, request, render_template, redirect, get_flashed_messages, flash, url_for,session

# imported flask forms for submitting the data
from flask_wtf import FlaskForm
from wtforms import FileField,SubmitField
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename 

# import OS for uploaidng,deleting the files and then store the in the respective folders
import os

# import smtplib for semding email
import smtplib  
from email.message import EmailMessage

#import DateTime module 
from datetime import date

# import these modules for connecting the 
from flaskext.mysql import MySQL
import pymysql
from sqlalchemy  import Float, Numeric, String, create_engine
import sqlalchemy
import mysql.connector as c

app = Flask(__name__)
app.secret_key = "SudheerFUKA"
app.config['UPLOAD_FOLDER'] = "C:/Sudheer/flask_placements/"
app.config['UPLOAD_FOLDER_1'] = "students_data"
app.config['UPLOAD_FOLDER_2'] = "updated_students_data"

# Connection 1
mysql = MySQL()
# MySQL Configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'sudheer123'
app.config['MYSQL_DATABASE_DB'] = 'students_data'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

con1 = c.connect(host = "localhost",user = "root",password = "sudheer123",database = "students_data")

# This class is for creating the flask forms (attachment upload)
class Upload_attachment(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")


# This class is for creating the flask forms (excel sheet upload)
class Upload_excel_file(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

# This route is for the home page that has to be loaded when the site opens
@app.route('/')
def home():
    return render_template('home_2.html')

@app.route('/signin', methods = ['GET','POST'])
def signin():
    if request.method=='GET':
        return render_template('admin_login.html')
    if request.method == 'POST':
        email = request.form['email']
        passw = request.form['password']
        print(email)
        print(passw)
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute("select pwd from admindata where email = %s;",(email))
        data = cur.fetchall()
        con.commit()
        cur.close()
        d = data[0]
    if passw == d['pwd']:
        return render_template("home_page.html")
    else:
        return render_template('admin_login.html',msg ="Incorrect Email Or Password")

@app.route('/signup',methods = ['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup_form.html')
    name   = request.form['fullname']
    email  = request.form['email']
    mobile = request.form['number']
    gender = request.form['gender']
    pass1  = request.form['password1']
    pass2  = request.form['password2']
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('select COUNT(name) FROM admindata;')
    len = cur.fetchall()[0]
    con.commit()
    cur.close()
    
    if(len[0] > 0): 
        con = mysql.connect()
        cur = con.cursor()
        cur.execute('select email from admindata;')
        data = cur.fetchall()[0]
        con.commit()
        cur.close()
    else:
        con = mysql.connect()
        cur = con.cursor()
        cur.execute('INSERT INTO admindata(name,email,mobile,gender,pwd) VALUES(%s,%s,%s,%s,%s);',(name,email,mobile,gender,pass2))
        con.commit()
        cur.close()

    if email in data:
        return render_template('signup_form.html',msg = 'Looks like you are already registered')
    elif pass1 == pass2:
         con = mysql.connect()
         cur = con.cursor()
         cur.execute('INSERT INTO admindata(name,email,mobile,gender,pwd) VALUES(%s,%s,%s,%s,%s);',(name,email,mobile,gender,pass2))
         con.commit()
         cur.close()
         return render_template('signup_form.html',msg = "successfully Registered",data = data,l = len)
    else:
        return render_template('signup_form.html',msg ='Password Miss match')


@app.route('/display_eligibility_filters_form')
def display_eligibility_filters_form():
    return render_template('eligibility_filters_form.html')

@app.route('/display_eligibility',methods = ['GET','POST'])
def display_eligibility():
    if request.method == 'GET':
        pass
        
    elif request.method == 'POST':
        c = request.form['company']
        py = request.form['passout_year']
        by = request.form['btech_year']
        sem = request.form['sem']
        branches = request.form.getlist('branch_selection')
        per_b = request.form['criteria_btech']
        per_i = request.form['criteria_inter']
        per_t = request.form['criteria_tenth']
        b = request.form['backlog-selection']
        gen = request.form['gender']

        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        if (gen == 'Male') or (gen == 'Female'):
            cur.execute("select * FROM sqldb1 WHERE btech_percentage>={per_b} AND inter_Percentage>={per_i} AND tenth_percentage>={per_t} AND gender='{gen}' AND total_backlogs>={b};".format(per_b=per_b,per_i=per_i,per_t=per_t,gen=gen,b=b))
        else:
            cur.execute("select * FROM sqldb1 WHERE btech_percentage>={per_b} AND inter_percentage>={per_i} AND tenth_percentage>={per_t} AND total_backlogs>={b};".format(per_b=per_b,per_i=per_i,per_t=per_t,b=b))
        data_eligible = cur.fetchall()
        con.commit()
        cur.close()
        return render_template('eligibility_table.html', data = data_eligible, c = " Eligible Students List For {}".format(c),sem=sem)


# This route is for uploading the excel sheet of students data which has to be inserted into the database 
@app.route('/upload_into_students_data',methods = ['GET','POST'])
def upload_into_students_data(): 
    form = Upload_excel_file()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER_1'],secure_filename(file.filename))) # Then save the file
        pymysql.install_as_MySQLdb()
        engine = create_engine('mysql://root:sudheer123@localhost/students_data')
        df1 = pd.read_excel('students_data\students_sheet.xlsx')
        df1 = pd.read_excel("students_data\students_sheet.xlsx",dtype = {"total_backlogs":Numeric,"tenth_cgpa":float,"tenth_percentage":float,"inter_cgpa":float,"inter_percentage":float,"diploma_percentage":float,"placement_status":String})
        df1.to_sql("sqldb1",con= engine,if_exists ="append")

        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute("UPDATE sqldb1 SET gender='Male' WHERE gender=' Male';")
        con.commit()

        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute("UPDATE sqldb1 SET gender='Female' WHERE gender=' Female';")
        con.commit()

        file = 'students_sheet.xlsx'  #( File name)
        location = "students_data/"   # (File location)
        path = os.path.join(location, file) # (Path)
        os.remove(path)  # (Remove the file, 'sample_sheet.xlsx')
        return "File has been uploaded and pushed into database and deleted."
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
        df1 = pd.read_excel("updated_students_data\sheet.xlsx",dtype = {"total_backlogs":Numeric})
        df1.to_sql("sqldb2",con= engine,if_exists ="append")
    
        file = 'sheet.xlsx'  #( File name)
        location = "updated_students_data/"   # (File location)
        path = os.path.join(location, file) # (Path)
        os.remove(path)  # (Remove the file, 'sheet.xlsx')

        return "Plzz go back and click on update"
        
    return render_template('upload_sheet2.html',form=form)

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

    '''This database call is necessary  but it should be performed after once the sqldb1 table is updated 
           then we have to delete the table'''

    con = mysql.connect()
    cur = con.cursor(pymysql.cursors.DictCursor)
    data = cur.execute("DROP TABLE sqldb2;")
    data = cur.fetchall()
    cur.close()
    return redirect(url_for('upload_into_updated_students_data'))
    #return render_template('upload_sheet2.html',students1 = li1, d_backlogs_1 = d_backlogs_1, d_backlogs_2 = d_backlogs_2, d_btech_per_1 = d_btech_per_1, d_btech_per_2 = d_btech_per_2, students2 = li2)

@app.route('/student_table',methods=['GET','POST'])
def student_table():
    if request.method == 'GET':
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        data = cur.execute("SELECT * FROM sqldb1;")
        data = cur.fetchall()
        con.close()
        return render_template('output_test_3.html',data = data)
        # I feel this code aint required so just commenting for now
    '''elif request.method == 'POST':
        f = request.form['Rounds']
        s1 = request.form.getlist('mycheckbox') 

        for i in s1:
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)
            data = cur.execute("SELECT * FROM sqldb1 WHERE roll_no = '{}';".format(i))
            data = cur.fetchall()
            con.close()

        s2 = []
        for i in s1:
            s2.append(int(i))
            

        return render_template('filter.html',filter = f,s=s1,data = data)'''

@app.route('/display_company_filters_form')
def display_company_filters_form():
    return render_template("company_filters_form.html")

@app.route('/company_logs',methods=['GET','POST'])
def company_logs():
    if request.method == 'GET':
        return "Hello"
    elif request.method == 'POST':
        c = request.form['company']
        c_em = request.form['company_mail']
        c_yr = request.form['passout_year']
        c_btech_yr = request.form['btech_year']
        branches = request.form.getlist('branch_selection') 
        c_per_b = request.form['criteria_btech']
        c_per_i = request.form['criteria_inter']
        c_per_t = request.form['criteria_tenth']
        c_b = request.form['backlog-selection']
        c_gen = request.form['gender']

        t_name = c + '_' + c_yr + '_' + c_btech_yr 

        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        tables_data = cur.execute("SHOW TABLES;")
        tables_data = cur.fetchall()
        cur.close()
        con.commit()

        table_names = []
        for table in tables_data:
            table_names.append(table['Tables_in_students_data'])
        
        t_name = t_name.lower()
        
        count = 0
        for i in table_names:
            if(t_name == i):
                count = count + 1
        
        if(count == 0):
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)
            data = cur.execute("CREATE TABLE {}(roll_no VARCHAR(250),email VARCHAR(250),rounds VARCHAR(250),PRIMARY KEY(roll_no));".format(t_name))
            data = cur.fetchall()
            cur.close()
            con.commit()

            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)
            if(c_gen == 'Male' or c_gen == 'Female'):
                data = cur.execute("INSERT INTO {}(roll_no, email) SELECT roll_no,emails FROM sqldb1 WHERE btech_percentage >= {} AND inter_percentage >= {} AND tenth_percentage >= {} AND total_backlogs >= {} AND gender = '{}';".format(t_name,c_per_b,c_per_i,c_per_t,c_b,c_gen))
            else:
                data = cur.execute("INSERT INTO {}(roll_no, email) SELECT roll_no,emails FROM sqldb1 WHERE btech_percentage >= {} AND inter_percentage >= {} AND tenth_percentage >= {} AND total_backlogs >= {};".format(t_name,c_per_b,c_per_i,c_per_t,c_b))
            data = cur.fetchall()
            cur.close()
            con.commit()

            return redirect(url_for('company_tables'))
        else:
            
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)
            data = cur.execute("SELECT roll_no FROM sqldb1 WHERE btech_percentage >= {} AND inter_percentage >= {} AND tenth_percentage >= {} AND total_backlogs >= {} AND gender = '{}';".format(c_per_b,c_per_i,c_per_t,c_b,c_gen))
            data = cur.fetchall()
            cur.close()
            con.commit()

            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)
            data = cur.execute("INSERT INTO {}(roll_no, email) SELECT roll_no,emails FROM sqldb1 WHERE btech_percentage >= {} AND inter_percentage >= {} AND tenth_percentage >= {} AND total_backlogs >= {} AND gender = '{}';".format(t_name,c_per_b,c_per_i,c_per_t,c_b,c_gen))
            data = cur.fetchall()
            cur.close()
            con.commit()
            return redirect(url_for('company_tables'))


        '''con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        data = cur.execute("SELECT * FROM sqldb1 WHERE btech_percentage >= {};".format(c_per_b))
        data = cur.fetchall()
        cur.close()
        con.commit()


        return render_template('list_of_companies.html',table_names = table_names,t_name = t_name,c_em = c_em, c_yr = c_yr, c_btech_yr = c_btech_yr, branches =  branches, c_per_b = c_per_b, c_per_i = c_per_i, c_per_t = c_per_t, c_b = c_b, c_gen = c_gen,data = data) 
'''

@app.route('/company_tables')
def company_tables():
    con = mysql.connect()
    cur = con.cursor(pymysql.cursors.DictCursor)
    tables_data = cur.execute("SHOW TABLES;")
    tables_data = cur.fetchall()
    cur.close()
    con.commit()

    company_table_names = []
    primary_tables = []
    for table in tables_data:
        if(table['Tables_in_students_data'] != 'sqldb1') and  (table['Tables_in_students_data'] != 'sqldb2') and (table['Tables_in_students_data'] != 'companies'):
            company_table_names.append(table['Tables_in_students_data'])
        else:
            primary_tables.append(table['Tables_in_students_data'])

    print(company_table_names)
    print(primary_tables)
    return render_template('list_of_company_tables.html',table_names=company_table_names)

@app.route('/show_company_table/<name>',methods=['GET','POST'])
def show_company_table(name):
    con = mysql.connect()
    cur = con.cursor(pymysql.cursors.DictCursor)
    cur.execute('SELECT * FROM {};'.format(name))
    data = cur.fetchall()
    cur.close()
    return render_template('company_wise_details.html',data = data, name = name)

@app.route('/delete_company_table/<name>')
def delete_company_table(name):
    con = mysql.connect()
    cur = con.cursor(pymysql.cursors.DictCursor)
    data = cur.execute("DROP TABLE {};".format(name))
    data = cur.fetchall()
    cur.close()
    return redirect(url_for('company_tables'))

@app.route('/update_rounds/<name>',methods=['GET','POST'])
def update_rounds(name):
    if request.method == 'POST':
        f = request.form['Rounds']
        s1 = request.form.getlist('mycheckbox') 

        for i in s1:
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)
            data = cur.execute("UPDATE {} SET rounds = '{}' WHERE roll_no = '{}';".format(name,f,i))
            data = cur.fetchall()
            cur.close()
            con.commit()

        '''s2 = []
        for i in s1:
            s2.append(int(i))'''

        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute('SELECT * FROM {};'.format(name))
        data = cur.fetchall()
        cur.close()
        return render_template('company_wise_details.html',data = data, name = name)


@app.route('/send_company_mails/<name>',methods = ['GET','POST'])
def send_company_mails(name):
    form = Upload_attachment()
    return render_template('draft_mail.html',form = form,name = name)

@app.route('/send_mail',methods=['GET','POST'])
def send_mail():
    if request.method == 'POST':
        form = Upload_attachment()
        if form.validate_on_submit():
            file = form.file.data # First grab the file
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
            
        c = request.form['company']
        sam_msg = request.form['message']
        # procedure 1
        '''con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute('SELECT email FROM {};'.format(c))
        data = cur.fetchall()
        cur.close()
         
        email_li = []
        for i in data:
            s = i['email']
            
            if('\xa0' in s):
                s = s.replace(u'\xa0', u' ')
                email_li.append(i[1:])
            else:
                email_li.append(i) 
            email_li.append(s)'''

        # procedure 2
        cursor = con1.cursor()
        cursor.execute('select email from {};'.format(c))
        data_mailList = cursor.fetchall()
        con1.commit()
        cursor.close()

        email_li = ['sudheer.edu.feb@gmail.com','19nu1a0519@nsrit.edu.in','19nu1a0527@nsrit.edu.in','19nu1a0588@nsrit.edu.in','19nu1a0537@nsrit.edu.in']
        for i in data_mailList:
            s = i[0]
            s = str(s)
            if('.com' in s):
                if('\xa0' in s):
                    s = s.replace(u'\xa0', u' ')
                    email_li.append(s[1:])
                else:
                    email_li.append(s) 
        
        email_id = "lolday606@gmail.com"
        email_pass = "ztskhwqzmvanmjqn"
        
        msg = EmailMessage()
        msg['subject'] = "Testing mail feature with smtplib"
        msg['From'] = email_id
        msg['To'] = email_li
        msg.set_content(sam_msg)

        for each_file in os.listdir():
            s = ''
            for i in each_file:
                if(i != '.'):
                    s = s + i
                elif(i == '.'):
                    break
            
            if(s == c):
                print("Hello",c)
                with open(each_file,'rb') as f:
                    file_data = f.read()
                    file_name = f.name
                    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
        # important
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as smtp:
            smtp.login(email_id,email_pass)
            smtp.send_message(msg)
        return render_template("mail_output.html",mails = email_li,form = form, name = c)

# important  
'''@app.route('/send_company_mails/<name>')
def send_company_mails(name):
    con = mysql.connect()
    cur = con.cursor(pymysql.cursors.DictCursor)
    data = cur.execute("SELECT email FROM {};".format(name))
    data = cur.fetchall()
    cur.close()
    return render_template('draft_mail.html',data=data)'''
        
@app.route('/tables')
def tables():
    con = mysql.connect()
    cur = con.cursor(pymysql.cursors.DictCursor)
    tables_data = cur.execute("SHOW TABLES;")
    tables_data = cur.fetchall()
    cur.close()
    con.commit()

    company_table_names = []
    primary_tables = []
    for table in tables_data:
        if(table['Tables_in_students_data'] != 'sqldb1') and  (table['Tables_in_students_data'] != 'sqldb2') and (table['Tables_in_students_data'] != 'companies'):
            company_table_names.append(table['Tables_in_students_data'])
        else:
            primary_tables.append(table['Tables_in_students_data'])
    print(company_table_names)
    print(primary_tables)
    return render_template('list_of_other_tables.html',table_names=primary_tables)

@app.route('/show_table/<name>',methods=['GET','POST'])
def show_table(name):
    con = mysql.connect()
    cur = con.cursor(pymysql.cursors.DictCursor)
    cur.execute('SELECT * FROM {};'.format(name))
    data = cur.fetchall()
    cur.close()
    return render_template('table_wise_details.html',data=data,name=name)

@app.route('/placed_students')
def placed_students():

    con = mysql.connect()
    cur = con.cursor(pymysql.cursors.DictCursor)
    tables_data = cur.execute("SHOW TABLES;")
    tables_data = cur.fetchall()
    cur.close()
    con.commit()

    company_table_names = []
    primary_tables = []
    for table in tables_data:
        if(table['Tables_in_students_data'] != 'sqldb1') and  (table['Tables_in_students_data'] != 'sqldb2') and (table['Tables_in_students_data'] != 'companies'):
            company_table_names.append(table['Tables_in_students_data'])
        else:
            primary_tables.append(table['Tables_in_students_data'])

    # this code is to take out each comapny table and then diaplay all the students who got selected
    '''li = {}
    for i in company_table_names:
        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        data = cur.execute("SELECT * FROM {} WHERE rounds = 'Selected'".format(i))
        data = cur.fetchall()
        cur.close()
        con.commit() 
        li[i] = data'''

    return render_template('placed_students_details.html',table_names = company_table_names)

@app.route('/display_students',methods=['GET','POST'])
def display_students():
    if request.method == 'POST':
        company = request.form['company_tables']
        round = request.form['Rounds']

        con = mysql.connect()
        cur = con.cursor(pymysql.cursors.DictCursor)
        if(round == 'None'):
            data = cur.execute("SELECT * FROM {};".format(company))
        else:
            data = cur.execute("SELECT * FROM {} WHERE rounds = '{}';".format(company,round))
        data = cur.fetchall()
        cur.close()
        con.commit()

        return render_template('selected_students.html',data=data,round=round,company=company)

@app.route('/new_features')
def new_features():
    return render_template('test_table.html')

@app.route('/table_creation_form')
def table_creation_form():
    return "hello"

@app.route('/quiz_form',methods=["GET","POST"])
def quiz_form():
    return render_template('quiz_form.html')

@app.route('/Student_profile')
def Student_profile():
    return render_template('Student_profile.html')

@app.route('/signup_form',methods=['GET','POST'])
def signup_form():
    return render_template('signup_form.html')

@app.route('/home_2',methods=['GET','POST'])
def home_2():
    return render_template('home_2.html')

@app.route('/admin_login')
def admin():
    return render_template('admin_login.html')

@app.route('/admin_home',methods=['GET','POST'])
def admin_home():
    return render_template('admin_home.html')

@app.route('/student_login',methods=['GET','POST'])
def student_login():
    return render_template('student_login.html')



if(__name__) == '__main__':
    app.run(port=2000,debug=True)