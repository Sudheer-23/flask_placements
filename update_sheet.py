import pandas as pd
import pymysql
from sqlalchemy  import create_engine
import sqlalchemy
pymysql.install_as_MySQLdb()
engine = create_engine('mysql://root:sudheer123@localhost/students_data')
df1 = pd.read_excel('students_data_sheets\sheet.xlsx',sheet_name='cse')
#df1.to_sql("sqldb2",con= engine,if_exists ="append")
print(df1.head())
print('Success')