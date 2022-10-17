import pandas as pd
from sqlalchemy  import Float, Numeric, create_engine
import sqlalchemy

engine = create_engine('mysql://root:sudheer123@localhost/students_data')
df1 = pd.read_excel('students_sheet.xlsx')
sample_tenth_cgpa = df1['tenth_cgpa'].head
print(sample_tenth_cgpa)

for i in df1.iterrows():
    print(i)