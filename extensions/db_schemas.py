from extensions.extensions import app, get_db_connection, socketio
from flask import Flask, request, jsonify, send_from_directory


def database_schemas():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS location (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(80) NOT NULL,
                latitude DECIMAL(10, 8) NOT NULL DEFAULT 0.0,
                longitude DECIMAL(11, 8) NOT NULL DEFAULT 0.0,
                user_type VARCHAR(80) NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS driver_location (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(80) NOT NULL,
                latitude DECIMAL(10, 8) NOT NULL DEFAULT 0.0,
                longitude DECIMAL(11, 8) NOT NULL DEFAULT 0.0,
                user_type VARCHAR(80) NOT NULL
            )
        """)
        cur.execute("""
            ALTER TABLE userauth
            ADD COLUMN phone_number VARCHAR(80) NOT NULL,
            ADD COLUMN user_type VARCHAR(80) NOT NULL DEFAULT 'user',
            ADD COLUMN balance INT NOT NULL DEFAULT 0
        """)
        cur.execute("""
                CREATE TABLE IF NOT EXISTS userauth (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(80) NOT NULL,
                    password VARCHAR(80) NOT NULL,
                    created_at VARCHAR(80) NOT NULL,
                    user_type VARCHAR(80) NOT NULL
                );
            """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(80) NOT NULL,
                transaction_id VARCHAR(100) NOT NULL,
                reference_id VARCHAR(100) NOT NULL,
                months_paid INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
                CREATE TABLE IF NOT EXISTS user_rides (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(80) NOT NULL,
                    driver_email VARCHAR(80) NOT NULL,
                    ride_id VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        cur.execute("""
                CREATE TABLE IF NOT EXISTS driver_rides (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(80) NOT NULL,
                    password VARCHAR(80) NOT NULL,
                    created_at VARCHAR(80) NOT NULL
                )
            """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Exception occurred {str(e)}")