from extensions.extensions import app, get_db_connection, mail
from flask import Flask, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from datetime import datetime, timedelta
import os
import jwt
from flask_mail import Message
import random
import cloudinary
import cloudinary.uploader
import base64
from PIL import Image
import io
import cloudinary.api

SECRET_KEY = os.getenv('SECRET_KEY', 'hontoniano')  # Replace 'mysecretkey' with an actual key


def generate_otp():
    # Generate a random 6-digit OTP
    otp = random.randint(100000, 999999)
    return otp

cloudinary.config(
  cloud_name = "dqmhfzfis",
  api_key = "697753886725887",
  api_secret = "o5cuPJrAk2WaeiQERBeCBhyRuPo",
  secure=True
)


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
        email_or_phone = request.form.get("email")  # Changed to identifier
        password = request.form.get("password")

        if not email_or_phone or not password:
            return jsonify({'message': "Error: not all fields were sent or filled", 'status': 404})

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the identifier is an email or phone number
        if "@" in email_or_phone:  # Check if it's an email
            cur.execute("SELECT password, name, phone_number, balance FROM userauth WHERE email = %s", (email_or_phone,))
        else:  # Treat it as a phone number
            cur.execute("SELECT password, name, email, balance FROM userauth WHERE phone_number = %s", (email_or_phone,))

        user = cur.fetchone()

        if user is None:
            return jsonify({'message': "User not found", 'status': 404})

        stored_password, name, phone_number, balance = (user if "@" in email_or_phone else (user[0], user[1], user[2], user[3]))

        # Verify the password
        if check_password_hash(stored_password, password):
            # Create the payload for the JWT token without expiration
            payload = {
                'email': email_or_phone if "@" in email_or_phone else user[2],  # Use email if it's an email, else use the fetched email
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
        print(f"This is your email: {email}")

        # Check if the user already exists
        cur.execute("SELECT * FROM userauth WHERE email = %s", (email.strip(),))
        existing_user = cur.fetchone()
        print(f"Ex: {existing_user}")

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
    


def driverLogin():
    try:
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        password = request.form.get("password")

        if not email and not phone_number:
            return jsonify({'message': "Error: Email or phone number must be provided", 'status': 404})

        if not password:
            return jsonify({'message': "Error: Password is required", 'status': 404})

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the driver exists based on email or phone_number
        if email:
            cur.execute("SELECT password, id, email, user_type, phone_number, name FROM userauth WHERE email = %s AND user_type = %s", (email, 'driver'))
        else:
            cur.execute("SELECT password, id, email, user_type, phone_number, name FROM userauth WHERE phone_number = %s AND user_type = %s", (phone_number, 'driver'))

        driver = cur.fetchone()

        if driver is None:
            return jsonify({'message': "Driver not found", 'status': 404})

        stored_password, driver_id, driver_email, user_type, phone_no, name = driver

        # Verify the password
        if check_password_hash(stored_password, password):
            # Create the payload for the JWT token
            payload = {
                'driver_id': driver_id,
                'email': driver_email,
                'user_type': user_type,
                'phone_number': phone_no,
                'name': name
            }

            # Generate the token
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

            conn.close()

            # Send back the token in the response
            return jsonify({
                'message': "Login successful",
                'token': token,  # Sending the token in the response
                'status': 200
            })
        else:
            conn.close()
            return jsonify({'message': "Incorrect password", 'status': 403})

    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'message': f"An error occurred: {str(e)}", 'status': 500})
    

def driverSignup():
    try:
        email = request.form.get("email")
        phone_no = request.form.get("phone_number")
        name = request.form.get("name")
        gender = request.form.get("gender")
        age = request.form.get("age")
        password = request.form.get("password")

        # Validate input
        if not email or not phone_no or not name or not gender or not age or not password:
            return jsonify({'message': "Incomplete credentials", 'status': 409})

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if email or phone number already exists
        cur.execute("""
            SELECT * FROM userauth WHERE email = %s OR phone_number = %s
        """, (email, phone_no))
        cs = cur.fetchone()

        if cs is not None:
            return jsonify({'message': "Email or phone number already exists", 'status': 409})

        # Hash the password using generate_password_hash
        hashed_password = generate_password_hash(password)

        # Insert new driver into the userauth table
        cur.execute("""
            INSERT INTO userauth (email, phone_number, name, gender, age, password, user_type) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (email, phone_no, name, gender, age, hashed_password, 'driver'))

        conn.commit()  # Commit the changes to the database

        # Create the payload for the JWT token
        payload = {
            'email': email,
            'phone_number': phone_no,
            'name': name,
            'gender': gender,
            'age': age,
            'user_type': 'driver',
        }

        # Generate the token
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # Close the database connection
        cur.close()
        conn.close()

        # Send back the token in the response
        return jsonify({
            'message': "Signup successful",
            'token': token,
            'status': 200
        })

    except Exception as e:
        return jsonify({'message': f"An error occurred: {str(e)}", 'status': 500})


def checkVerificationStatus():
    try:
        # Retrieve email and phone number from the request
        email = request.form.get("email")
        phone_no = request.form.get("phone_number")

        # Set up the database connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Check for email verification status
        if email:
            cur.execute("SELECT status FROM verificationdetails WHERE email = %s", (email,))
            result = cur.fetchone()
            if result:
                cur.close()
                conn.close()
                return jsonify({
                    'status': 200,
                    'verification_status': result[0],  # Assuming status is at index 0
                    'message': "Verification status retrieved successfully."
                })

        # Check for phone number verification status
        if phone_no:
            cur.execute("SELECT status FROM verificationdetails WHERE phone_number = %s", (phone_no,))
            result = cur.fetchone()
            if result:
                cur.close()
                conn.close()
                return jsonify({
                    'status': 200,
                    'verification_status': result[0],  # Assuming status is at index 0
                    'message': "Verification status retrieved successfully."
                })

        # If no email or phone number provided or no result found
        cur.close()
        conn.close()
        return jsonify({
            'status': 404,
            'verification_status': 'pending',
            'message': "Verification details not found."
        })

    except Exception as e:
        cur.close()
        conn.close()
        return jsonify({'status': 500, 'verification_status': None, 'message': f"An error occurred: {str(e)}"})

def uploadVerificationImages():
    try:
        # Parse the JSON payload
        data = request.get_json()

        # Retrieve email, car color, and plate number from the request
        email = data.get("email")
        car_color = data.get("carColor")
        plate_number = data.get("plate_number")

        # Retrieve Base64-encoded images from the payload
        carPhotoBase64 = data['images'].get("carPhoto")
        driverPhotoBase64 = data['images'].get("driverPhoto")
        licensePhotoBase64 = data['images'].get("licensePhoto")
        platePhotoBase64 = data['images'].get("platePhoto")
        driverWithCarPhotoBase64 = data['images'].get("driverWithCarPhoto")

        # Create a response dictionary to hold Cloudinary URLs
        response_data = {}

        # Function to upload Base64-encoded image to Cloudinary
        def upload_base64_to_cloudinary(file_key, base64_string):
            if base64_string:
                # Remove the data URL prefix (e.g., 'data:image/jpeg;base64,')
                image_data = base64_string.split(",")[1]
                # Decode the Base64 string into bytes
                image_bytes = base64.b64decode(image_data)
                # Use io.BytesIO to create a file-like object from the bytes
                image_file = io.BytesIO(image_bytes)
                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(image_file)
                # Save the Cloudinary URL in the response data
                response_data[file_key] = upload_result['secure_url']
            else:
                response_data[file_key] = None

        # Upload each image to Cloudinary
        upload_base64_to_cloudinary("carPhoto", carPhotoBase64)
        upload_base64_to_cloudinary("driverPhoto", driverPhotoBase64)
        upload_base64_to_cloudinary("licensePhoto", licensePhotoBase64)
        upload_base64_to_cloudinary("platePhoto", platePhotoBase64)
        upload_base64_to_cloudinary("driverWithCarPhoto", driverWithCarPhotoBase64)

        # Check if any images were successfully uploaded
        if not response_data:
            return jsonify({'message': "No images uploaded", 'status': 409})

        # Save the uploaded image links along with other details to the database
        return saveLinksToDB(data=response_data, email=email, car_color=car_color, plate_number=plate_number)

    except Exception as e:
        return jsonify({'message': f"An error occurred: {str(e)}", 'status': 500})

def saveLinksToDB(data, email, car_color, plate_number):  # Include car_color as a parameter
    try:
        print("T: ")  # Debug statement

        # Check for missing required parameters
        if not email:
            return jsonify({'message': "Missing required parameters", 'status': 409})

        # Retrieve the Cloudinary URLs from the response data
        car_photo_url = data.get("carPhoto")
        driver_photo_url = data.get("driverPhoto")
        license_photo_url = data.get("licensePhoto")
        plate_photo_url = data.get("platePhoto")
        driver_with_car_photo_url = data.get("driverWithCarPhoto")
        print("1/5")
        # Get a connection to the database
        conn = get_db_connection()
        cur = conn.cursor()
        print("2")
        # Insert the uploaded image URLs into the database with status 'pending'
        cur.execute("""INSERT INTO verificationdetails (
            email, phone_number, car_color, car_photo, driver_photo, 
            license_photo, plate_photo, driver_with_car_photo, status, plate_number
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
            email, '08071273078', car_color, car_photo_url, driver_photo_url, 
            license_photo_url, plate_photo_url, driver_with_car_photo_url, 'pending', plate_number
        ))
        print("3")
        # Commit the changes
        conn.commit()

        # Close the connection
        cur.close()
        conn.close()
        print("$")
        return jsonify({
            'message': "Verification details saved successfully with status 'pending'",
            'status': 200
        })

    except Exception as e:
        return jsonify({'message': f"An error occurred while saving to DB: {str(e)}", 'status': 500})
