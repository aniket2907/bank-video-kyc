import pyodbc
import pandas as pd
import numpy as np

from sqlalchemy import create_engine
from sqlalchemy.engine import URL


con_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\aniket.idnani\OneDrive - Concentrix Corporation\Bank KYC system\ProjectDB-KYC.accdb;'


connection_url  = URL.create("access+pyodbc", query={"odbc_connect": con_str})
engine = create_engine(connection_url)


# query = "SELECT * FROM AADHAAR"

# with engine.connect() as con:
#     aadhaar = pd.read_sql_query(query, con=con)

# print(aadhaar.head())


query = "SELECT * FROM AADHAAR_VALIDATION"

with engine.connect() as con:
    aadhaar_validation = pd.read_sql_query(query, con=con)

#print(aadhaar_validation.head())


# query = "SELECT * FROM BANK"

# with engine.connect() as con:
#     bank = pd.read_sql_query(query, con=con)
# print(bank.head())


query = "SELECT * FROM BANK_VALIDATION"

with engine.connect() as con:
    bank_validation = pd.read_sql_query(query, con=con)

#print(bank_validation.head())


query = "SELECT * FROM BRANCH_DETAILS"

with engine.connect() as con:
    branch_details = pd.read_sql_query(query, con=con)

#print(branch_details.head())


query = "SELECT * FROM BANK AADHAAR_LINK"

with engine.connect() as con:
    bank_aadhaar_link = pd.read_sql_query(query, con=con)

# print(bank_aadhaar_link.head())


query = "SELECT * FROM ACCOUNT_DETAILS"

with engine.connect() as con:
    account_details = pd.read_sql_query(query, con=con)

# print(account_details.head())


query = "SELECT * FROM ACCOUNT_INDEX"

with engine.connect() as con:
    account_index = pd.read_sql_query(query, con=con)

# print(account_index.head(10))
b_index = bank_validation[bank_validation['customer_id']=='7494098'].index.values
print(b_index[0])

index = aadhaar_validation[aadhaar_validation['aadhaar_number']=='169530821305'].index.values
print(index[0])
print(aadhaar_validation[aadhaar_validation['aadhaar_number']=='169530821305'])
query = 'SELECT PHOTO, SIGNATURE, CUSTOMER_ID FROM BANK'

with engine.connect() as con:
    df = pd.read_sql_query(query, con=con)

data2excel = pd.ExcelWriter('photo_sig_ref.xlsx')

df.to_excel(data2excel, index = False)

data2excel.save()




