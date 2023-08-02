# importing Flask and other modules
from flask import Flask, request, render_template, jsonify
from dbload import bank_validation
import os
import math
import random
import smtplib
import re
import cv2
import base64


import pandas as pd

import pyodbc

CAPTCHA_CONFIG = {'SECRET_CAPTCHA_KEY':  '[CAPTCHA KEY HERE]'}
from flask_simple_captcha import CAPTCHA


from sqlalchemy import create_engine
from sqlalchemy.engine import URL

def mask_cc_number(cc_string, digits_to_keep=4, mask_char='*'):
   cc_string_total = sum(map(str.isdigit, cc_string))

   if digits_to_keep >= cc_string_total:
       print("Not enough numbers. Add 10 or more numbers to the credit card number.")

   digits_to_mask = cc_string_total - digits_to_keep
   masked_cc_string = re.sub('\d', mask_char, cc_string, digits_to_mask)

   return masked_cc_string


con_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\aniket.idnani\OneDrive - Concentrix Corporation\Bank KYC system\ProjectDB-KYC.accdb;'

connection_url  = URL.create("access+pyodbc", query={"odbc_connect": con_str})
engine = create_engine(connection_url)

query = "SELECT * FROM BANK_VALIDATION"

with engine.connect() as con:
   bank_validation = pd.read_sql_query(query, con=con)
   
query = "SELECT * FROM BANK"

with engine.connect() as con:
   bank = pd.read_sql_query(query, con=con)

query = "SELECT * FROM AADHAAR_VALIDATION"

with engine.connect() as con:
   aadhaar_validation = pd.read_sql_query(query,con=con)

face_detector1 = cv2.CascadeClassifier('c:/ProgramData/Anaconda3/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml')

def detect_bounding_box(vid):
   gray_image = cv2.cvtColor(vid, cv2.COLOR_BGR2GRAY)
   faces = face_detector1.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))
   for (x, y, w, h) in faces:
      cv2.rectangle(vid, (x, y), (x + w, y + h), (0, 255, 0), 4)
   return faces




# Flask constructor
app = Flask(__name__)






@app.route('/')
def step1():
   return render_template("alt_index.html")
# A decorator used to tell the application
# which URL is associated function


@app.route('/cam', methods =["POST"])

def cam():
   # eye_dectector1 = cv2.CascadeClassifier('haarcascade_eye.xml')
   # reading the input image now
   check = 0
   smilecheck = 0
   faceCascade = cv2.CascadeClassifier('c:/ProgramData/Anaconda3/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml')
   smileCascade = cv2.CascadeClassifier('c:/ProgramData/Anaconda3/Lib/site-packages/cv2/data/haarcascade_smile.xml')
   cap = cv2.VideoCapture(0)
   cap.set(3,640) # set Width
   cap.set(4,480) # set Height

   while True:
      ret, img = cap.read()
      gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      faces = faceCascade.detectMultiScale(
         gray,
         scaleFactor=1.3,
         minNeighbors=5,      
         minSize=(30, 30)
      )

      for (x,y,w,h) in faces:
         cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
         roi_gray = gray[y:y+h, x:x+w]
         roi_color = img[y:y+h, x:x+w]
         
         smile = smileCascade.detectMultiScale(
               roi_gray,
               scaleFactor= 1.5,
               minNeighbors=15,
               minSize=(25, 25),
               )
         
         for (xx, yy, ww, hh) in smile:
               cv2.rectangle(roi_color, (xx, yy), (xx + ww, yy + hh), (0, 255, 0), 2)
         smilecheck+= len(smile)   
                  
      cv2.imshow('video', img)

      check+=len(faces)

      if cv2.waitKey(1) & 0xFF == ord("q"):
         break

   cap.release()
   cv2.destroyAllWindows()
   if check > 5 & smilecheck>0:
      return success()
   else:
      return render_template("newind2.html")
      
@app.route('/validate', methods=["GET", "POST"])
def gfg():
   global b_index
   global cust_id
   if request.method == "POST":
      # getting input with name = fname in HTML form
      cust_id = request.form.get("cust_id")
      # getting input with name = lname in HTML form
      dob = request.form.get("dob")
      mobile_no = request.form.get("mob_no")
      email_addr = request.form.get("email_id")
      b_index = bank_validation[bank_validation['customer_id']==str(cust_id)].index.values
      if bank_validation.loc[b_index[0]]['mob_no']==mobile_no and bank_validation.loc[b_index[0]]['DOB']==str(dob) and bank_validation.loc[b_index[0]]['Email']==email_addr:
         return aadhaar_link()
      else:
         return incorrect_credentials1()
      return str(bank_validation[bank_validation['customer_id']==str(cust_id)])
   return render_template("index.html")

@app.route('/start')
def success():
   pass
   return render_template("newind.html")

@app.route('/kyc', methods=["GET", "POST"])
def begin():
   global a_index
   global one_time_password
   global email_id
   global mobile_no
   if request.method == "POST":
      # getting input with name = fname in HTML form
      aadhaar_number = request.form.get("aadhaar_no")
      # getting input with name = lname in HTML form
      mobile_no = request.form.get("mob_number")
      email_id = request.form.get("email_id")
      a_index = aadhaar_validation[aadhaar_validation['aadhaar_number']==str(aadhaar_number)].index.values
      if aadhaar_validation.loc[a_index[0]]['Email']==email_id:
         #one_time_password = gen_otp()
         return fa()
      else:
         return incorrect_credentials2()
   cust_name = bank.loc[b_index[0]]['full_name']
   return render_template("index6.html", variable = cust_name)


@app.route('/aadhaar-validate')
def fa():
   pass
   global one_time_password
   digits = "0123456789"
   one_time_password =""

   for i in range(6):
      one_time_password += digits[math.floor(random.random()*10)]
   cust_name = bank.loc[b_index[0]]['full_name']
   s = smtplib.SMTP('smtp.gmail.com', 587)
   s.starttls()
   message = "Your OTP for completing ANX Bank KYC is " + one_time_password
   s.login('[enter email address]', "[enter account code here]")
   s.sendmail('&&&&&&', email_id, message)
   return render_template("index7.html", variable = cust_name)

@app.route('/enter-otp', methods=["GET", "POST"])
def verify():
   if request.method == "POST":
      entered_otp = request.form.get("otp")
      if one_time_password == entered_otp:
         return home()
      else:
         return render_template('newind3.html')
   cust_name = bank.loc[b_index[0]]['full_name']
   return render_template("index8.html", variable = cust_name)

@app.route('/kyc-completed')
def home():
   pass
   cust_name = bank.loc[b_index[0]]['full_name']
   dob  = bank.loc[b_index[0]]['DOB']
   branch_code = bank.loc[b_index[0]]['branch_code']
   mobile = aadhaar_validation.loc[a_index[0]]['mob_no']
   cust_id_masked = ("*" * (len(cust_id) - 4) + cust_id[-4:])
   mobile_no_masked = ("*" * (len(mobile) - 4) + mobile[-4:])
   return render_template("index9.html", v2 = cust_name, v1 = cust_id_masked, v3 = mobile_no_masked , v4 = branch_code)


@app.route('/invalid')
def incorrect_credentials1():
   pass 
   return render_template("index4.html")

def incorrect_credentials2():
   pass 
   return render_template("newind4.html")

@app.route('/link-aadhaar')
def aadhaar_link():   
   cust_name = bank.loc[b_index[0]]['full_name']
   return render_template("index5.html", variable = cust_name)

@app.route('/faq')
def faq():
   pass
   return render_template('index3.html')

if __name__=='__main__':
   app.run(debug=True)

