from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from mysql.connector import Error
import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()
def get_healthcare_response(user_input):
    load_dotenv()
    key_ = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=key_)
    print(client)


    
    conversation = [
        {"role": "system", "content": "You are here to support in human mental health care related queries, suppose if a user posting deviated question suggest them to ask only mental health related queries to serve your sole purpose and suggest them few mental health related queries to ask"},
        {"role": "user", "content": user_input},
    ]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )

    return completion.choices[0].message.content



app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database' : 'user_details'
}

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    error_message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # connect mysql and flask application
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # query to checkl if username and password is allready exist
        query = "SELECT * FROM datas WHERE username=%s AND password=%s"
        cursor.execute(query, (username, password))

        user_data = cursor.fetchone()

        if user_data:
            # if login is success then go to the chatbot page
            conn.close()
            return redirect(url_for('chatbot'))
        else:
            # if log in unsuccess then show the error message
            conn.close()
            error_message = "Invalid username or password. Please try again."

    return render_template('index.html', error_message=error_message)

# sign up route

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        phone_number = request.form['phone_number']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # check password and confim password match or not
        if password != confirm_password:
            error_message = "Password and Confirm Password do not match."
            return render_template('signup.html', error_message=error_message)

        # Check if username already exists
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT * FROM datas WHERE username=%s and password=%s"
        cursor.execute(query, (username, password))
        existing_user = cursor.fetchone()

        if existing_user:
            error_message = "Username and  password is already exists. Please choose another username or password "
            conn.close()
            return render_template('signup.html', error_message=error_message)
        # Store user details in database
        else:
            insert_query = "INSERT INTO datas (username, phonenumber, password) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (username, phone_number, password))
            conn.commit()
            conn.close()

            # if sign up is success then go to sign up success page
            return render_template('signup_success.html', username = username)

    return render_template('signup.html')


@app.route('/chatbot')
def chatbot():
    return render_template("chatbot.html")

@app.route('/submit', methods=['POST'])
def submit():
    user_message = request.json.get('message')
    response = get_healthcare_response(user_message)
    return jsonify({'message': response})

if __name__ == '__main__':
    app.run(debug=True)