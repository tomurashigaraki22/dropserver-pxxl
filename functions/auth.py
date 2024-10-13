from extensions.extensions import app, get_db_connection, mail
from flask import Flask, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from datetime import datetime, timedelta
import os
import jwt
from flask_mail import Message
import random

SECRET_KEY = os.getenv('SECRET_KEY', 'hontoniano')  # Replace 'mysecretkey' with an actual key


def generate_otp():
    # Generate a random 6-digit OTP
    otp = random.randint(100000, 999999)
    return otp



def send_otp_email(recipient_email, otp):
    try:
        subject = "Your OTP Code"
        # HTML content with basic styling
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 20px;">
            <h2 style="color: #4CAF50;">Verify Your Email</h2>
            <p>Hi,</p>
            <p>Thank you for registering. Please use the following One-Time Password (OTP) to verify your email address:</p>
            <h1 style="color: #333;">{otp}</h1>
            <p style="font-size: 12px; color: #888;">This OTP is valid for 10 minutes. Do not share it with anyone.</p>
            <p>Thank you,<br>The DropApp Team</p>
        </body>
        </html>
        """
        # Send the email
        msg = Message(subject, recipients=[recipient_email])
        msg.html = html_content
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def verifyEmail():
    try:
        email = request.form.get("email")
        print(f"EMAIL: {email}")

        if not email:
            return jsonify({"message": "Email not sent", "status": 404})
        print("@")

        # Generate OTP
        otp = generate_otp()
        print(f"OTP: {otp}")

        # Send the OTP to the user's email
        email_sent = send_otp_email(email, otp)
        if email_sent:
            return jsonify({"message": "OTP sent to your email", "status": 200, "otp": otp})  # Return OTP for testing, remove in production
        else:
            return jsonify({"message": "Failed to send OTP", "status": 500})

    except Exception as e:
        return jsonify({"message": str(e), "status": 500})
    

def add_to_balance():
    try:
        email = request.form.get("email")
        amount_to_add = request.form.get("amount_to_add")

        if not email:
            return jsonify({'message': "Error: Email not provided", 'status': 404})
        if not amount_to_add:
            return jsonify({'message': "Error: Amount to add not provided", 'status': 404})

        # Ensure the amount to add is a valid number (int or float)
        try:
            amount_to_add = float(amount_to_add)
        except ValueError:
            return jsonify({'message': "Invalid amount format", 'status': 400})

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the user exists
        cur.execute("SELECT balance FROM userauth WHERE email = %s", (email,))
        user = cur.fetchone()

        if user is None:
            return jsonify({'message': "User not found", 'status': 404})

        # Get the current balance
        current_balance = float(user[0])

        # Add the new amount to the current balance
        new_balance = current_balance + amount_to_add

        # Update the user's balance in the database
        cur.execute("UPDATE userauth SET balance = %s WHERE email = %s", (new_balance, email))
        conn.commit()
        conn.close()

        return jsonify({
            'message': "Balance updated successfully",
            'new_balance': new_balance,
            'status': 200
        })

    except Exception as e:
        return jsonify({'message': f"An error occurred: {str(e)}", 'status': 500})
    

def get_balance():
    try:
        email = request.form.get("email")

        if not email:
            return jsonify({'message': "Error: Email not provided", 'status': 404})

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the user exists and fetch the balance
        cur.execute("SELECT balance FROM userauth WHERE email = %s", (email,))
        user = cur.fetchone()

        if user is None:
            return jsonify({'message': "User not found", 'status': 404})

        balance = user[0]  # Assuming 'balance' is the first column in the result

        conn.close()

        return jsonify({
            'message': "Balance fetched successfully",
            'balance': balance,
            'status': 200
        })

    except Exception as e:
        return jsonify({'message': f"An error occurred: {str(e)}", 'status': 500})
        

def changePassword():
    try:
        # Get the request data
        email = request.form.get('email')
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')

        # Ensure all fields are provided
        if not email or not old_password or not new_password:
            return jsonify({'message': 'Error: All fields are required', 'status': 400})

        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch the user's existing password from the database
        cur.execute("SELECT password FROM userauth WHERE email = %s", (email,))
        user = cur.fetchone()

        if user is None:
            return jsonify({'message': "User not found", 'status': 404})

        stored_password = user[0]

        # Verify that the old password matches the one in the database
        if not check_password_hash(stored_password, old_password):
            conn.close()
            return jsonify({'message': 'Incorrect old password', 'status': 403})

        # Check if the new password is different from the old password
        if check_password_hash(stored_password, new_password):
            conn.close()
            return jsonify({'message': 'New password cannot be the same as the old password', 'status': 400})

        # Hash the new password
        hashed_new_password = generate_password_hash(new_password)

        # Update the password in the database
        cur.execute("UPDATE userauth SET password = %s WHERE email = %s", (hashed_new_password, email))
        conn.commit()
        conn.close()

        # Return success message
        return jsonify({'message': 'Password changed successfully', 'status': 200})

    except Exception as e:
        return jsonify({'message': f"An error occurred: {str(e)}", 'status': 500})
        

def login():
    try:
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return jsonify({'message': "Error: not all fields were sent or filled", 'status': 404})
        
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the user exists
        cur.execute("SELECT password, name, phone_number, balance FROM userauth WHERE email = %s", (email,))
        user = cur.fetchone()
        
        if user is None:
            return jsonify({'message': "User not found", 'status': 404})

        stored_password, name, phone_number, balance = user

        # Verify the password
        if check_password_hash(stored_password, password):
            # Create the payload for the JWT token without expiration
            payload = {
                'email': email,
                'phone_number': phone_number,
                'name': name,
                'user_type': 'user',
                'balance': balance
            }

            # Generate the token
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

            conn.close()

            # Send back the token in the response
            return jsonify({
                'message': "Login successful",
                'token': token,  # Sending the token with the caption 'token'
                'status': 200
            })
        else:
            conn.close()
            return jsonify({'message': "Incorrect password", 'status': 403})

    except Exception as e:
        return jsonify({'message': f"An error occurred: {str(e)}", 'status': 500})

# Secret key for encoding the JWT

def userSignup():
    try:
        email = request.form.get("email")
        password = request.form.get("password")
        phone_number = request.form.get("number")
        name = request.form.get("name")

        if not email or not password or not phone_number or not name:
            return jsonify({'message': "Error: not all fields were sent or filled", 'status': 404})
        
        conn = get_db_connection()
        cur = conn.cursor()

        # Hash the password for security
        hashed_password = generate_password_hash(password)

        # Check if the user already exists
        cur.execute("SELECT * FROM userauth WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            return jsonify({'message': "User with this email already exists", 'status': 409})

        # Insert the new user into the database
        cur.execute("""
            INSERT INTO userauth (email, password, phone_number, name, user_type, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (email, hashed_password, phone_number, name, 'user', datetime.now()))

        conn.commit()

        # Create the payload for the JWT token without expiration
        payload = {
            'email': email,
            'phone_number': phone_number,
            'name': name,
            'user_type': 'user',
            'balance': 0
        }

        # Generate the token
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        conn.close()

        # Send back the token in the response
        return jsonify({
            'message': "Signup successful",
            'token': token,  # Sending the token with the caption 'token'
            'status': 201
        })

    except Exception as e:
        return jsonify({'message': f"An error occurred: {str(e)}", 'status': 500})
