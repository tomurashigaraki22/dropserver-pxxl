from flask import Flask, request, jsonify
import datetime
from extensions.extensions import get_db_connection



def calculate_expiration_date(months_paid):
    # Calculate the expiration date based on the number of months paid
    return datetime.datetime.now() + datetime.timedelta(days=months_paid * 30)  # Approximation

def subscribe_user(email, transaction_id, reference_id, months_paid):
    # Connect to the database
    conn = get_db_connection()
    cur = conn.cursor()

    # Calculate the expiration date
    expiration_date = calculate_expiration_date(months_paid)

    # Insert the subscription into the database
    cur.execute("""
        INSERT INTO subscriptions (email, transaction_id, reference_id, months_paid, expires_at) 
        VALUES (%s, %s, %s, %s, %s)
    """, (email, transaction_id, reference_id, months_paid, expiration_date))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Subscription created successfully.", "expires_at": expiration_date})

def check_subscription_status(email):
    # Connect to the database
    conn = get_db_connection()
    cur = conn.cursor()

    # Check the latest subscription for the user
    cur.execute("""
        SELECT expires_at 
        FROM subscriptions 
        WHERE email = %s 
        ORDER BY created_at DESC 
        LIMIT 1
    """, (email,))
    
    subscription = cur.fetchone()
    cur.close()
    conn.close()

    if subscription:
        expires_at = subscription[0]
        if expires_at > datetime.datetime.now():
            return jsonify({"message": "User is currently subscribed.", "expires_at": expires_at})
        else:
            return jsonify({"message": "User's subscription has expired."})
    else:
        return jsonify({"message": "No active subscription found."})