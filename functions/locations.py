from extensions.extensions import app, socketio, get_db_connection
from flask import request, jsonify, Flask


def saveLocationToDb():
    try:
        # Get longitude, latitude, and email from request
        longitude = request.form.get("longitude")
        latitude = request.form.get("latitude")
        email = request.form.get('email')

        if not longitude or not latitude or not email:
            return jsonify({'status': 400, 'message': 'Missing required parameters'}), 400

        # Establish a connection to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert location data into the 'location' table
        cur.execute("""
            INSERT INTO location (email, longitude, latitude, user_type) 
            VALUES(%s, %s, %s, %s)
        """, (email, longitude, latitude, "user"))

        # Commit the transaction and close the connection
        conn.commit()
        cur.close()
        conn.close()

        # Return a success response
        return jsonify({'status': 200, 'message': 'Location saved successfully'}), 200

    except Exception as e:
        # Handle exceptions and return an error response
        print(f"Error saving location: {str(e)}")
        return jsonify({'status': 500, 'message': 'Internal Server Error', 'error': str(e)}), 500