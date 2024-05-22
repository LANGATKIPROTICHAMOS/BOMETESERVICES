from flask import Flask, render_template, request, redirect, url_for, session, json, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import mysql.connector
import random
import string
from werkzeug.utils import secure_filename
import os
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from flask import flash
import requests

app = Flask(__name__)

app.secret_key = '39923184'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '39923184'
app.config['MYSQL_DB'] = 'bometeservices'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

@app.route("/")
def index():
    return render_template('index.html')


def get_next_buid():
    #cursor = conn.cursor()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT BUID FROM users ORDER BY ID DESC LIMIT 1")
    lastid = cursor.fetchone()
    cursor.close()
    if lastid:
        lastidnum = int(lastid[0].split('-')[1])
        newid = lastidnum + 1
    else:
        newid = 1

    return f"BUID-{newid:04d}"

def send_sms(api_key, email, sender_id, message, phone):
    url = "https://api.umeskiasoftwares.com/api/v1/sms"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "api_key": api_key,
        "email": email,
        "Sender_Id": sender_id,
        "message": message,
        "phone": phone
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'password' in request.form:
        BUID = get_next_buid()
        name = request.form['name']
        useremail = request.form['email']
        password = request.form['password']
        phonenumber = request.form['phone']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (useremail,))
        account = cursor.fetchone()
        
        if account:
            msg = 'Email already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', useremail):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Username must contain only characters and numbers!'
        elif not name or not password or not useremail:
            msg = 'Please fill out the form!'
        else:
            hashed_password = bcrypt.generate_password_hash(password)
            
            cursor.execute('INSERT INTO users(BUID, FullName, Email, Phone, Password) VALUES (%s, %s, %s, %s, %s)', (BUID, name, useremail, phonenumber, hashed_password,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

            api_key = "TDY0Nzk5OFA6amx3emI3c3I="
            email = "amoslangat184@gmail.com"
            sender_id = "UMS_SMS"
            message = f"Hello {name}, You have successfully created a Bomet E-Services Account with email {useremail}. Your Bomet User ID is: {BUID}, Kind Regards\n"
            phone = phonenumber

            response = send_sms(api_key, email, sender_id, message, phone)
            print(response)
            
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    
    return render_template('register.html', msg=msg)

@app.route('/login')
def login():
    return render_template('login-v2.html')








if __name__ == "__main__":
    app.run(debug=True)