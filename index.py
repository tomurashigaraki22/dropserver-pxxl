from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import emit, join_room, leave_room, SocketIO
from extensions.extensions import get_db_connection, socketio, app, mysql
from extensions.db_schemas import database_schemas
from functions.auth import userSignup, login, verifyEmail, changePassword, get_balance, add_to_balance, driverLogin, driverSignup, checkVerificationStatus, uploadVerificationImages, saveLinksToDB
from functions.riders import haversine, find_closest_rider
import re

###testing purposes###

@app.route('/tables', methods=['GET'])
def get_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    cur.close()
    return jsonify(tables)

@app.route("/alter-table/<email>/<status>", methods=["GET"])
def alterTable(email, status):
    try:
        if not status:
            return jsonify({"Message": "Status value is required"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        
        # Update the status column for the specified email
        cur.execute("""
            UPDATE verificationdetails SET status = %s WHERE email = %s
        """, (status, email))  # Update with the new status
        
        conn.commit()  # Commit the changes to the database
        return jsonify({"Message": "Status updated successfully"}), 200

    except Exception as e:
        return jsonify({"Message": f"An error occurred: {str(e)}"}), 500


@app.route('/describe/<table_name>', methods=['GET'])
def describe_table(table_name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"DESCRIBE {table_name}")
    description = cur.fetchall()
    cur.close()
    return jsonify(description)


@app.route('/show/<table_name>', methods=['GET'])
def show_table(table_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Use parameterized queries to prevent SQL injection
        cur.execute(f"SELECT * FROM {table_name}")
        records = cur.fetchall()
        
        # Fetch the column names
        column_names = [desc[0] for desc in cur.description]
        
        # Create a list of dictionaries for the records
        results = []
        for record in records:
            results.append(dict(zip(column_names, record)))

        cur.close()
        return jsonify(results), 200  # Return records with a 200 OK status

    except Exception as e:
        print(f"Error retrieving records: {str(e)}")
        return jsonify({'status': 500, 'message': 'Internal Server Error', 'error': str(e)}), 500



###testing ends###



@app.route("/signupUser", methods=["GET", "POST"])
def signupUser():
    return userSignup()

@app.route("/login", methods=["GET", "POST"])
def logins():
    return login()

@app.route("/verify_email", methods=["GET", "POST"])
def verifyEmails():
    return verifyEmail()

@app.route("/changePassword", methods=["GET", "POST"])
def changePass():
    return changePassword()

@app.route("/getBalance", methods=["GET", "POST"])
def getBalance():
    return get_balance()

@app.route("/add_to_balance", methods=["GET", "POST"])
def addBalance():
    return add_to_balance()

@app.route("/driverLogin", methods=["GET", "POST"])
def driverLogins():
    return driverLogin()

@app.route("/driverSignup", methods=["GET", "POST"])
def driverSignups():
    return driverSignup()

@app.route("/checkVerificationStatus", methods=["GET", "POSt"])
def getStatus():
    return checkVerificationStatus()

@app.route("/uploadImages", methods=["GET", "POST"])
def uploadImages():
    return uploadVerificationImages()
    

connected_users = {}

# Event handler for when a user connects
@socketio.on('connect')
def handle_connect():
    print('Client connected:', request.sid)

@socketio.on('register_user')
def handle_register_user(data):
    email = data['email']
    if email:
        if email not in connected_users:
            connected_users[email] = set()  # Initialize a set for multiple connections
        connected_users[email].add(request.sid)  # Add current socket ID to user's set
        print(f'User {email} connected with Socket ID {request.sid}')
        emit('connected', {'message': f'Connected as {email}'})  # Confirm connection

@socketio.on('disconnect')
def handle_disconnect():
    # Remove the socket from connected_users based on request.sid
    for email, sockets in list(connected_users.items()):
        if request.sid in sockets:
            sockets.discard(request.sid)  # Remove the socket ID
            print(f'User {email} disconnected from socket ID {request.sid}')
            if not sockets:  # If no more sockets for this user, remove from dictionary
                del connected_users[email]
            # Clean up user's location from the database
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM location WHERE email = %s", (email,))
                conn.commit()
                print(f'Location for {email} has been removed from the database')
            except Exception as e:
                print(f"Error removing location for {email}: {str(e)}")
            break

@socketio.on("Nothing")
def nothingSUp():
    try:
        print(f"Hello World it's me")
    except Exception as e:
        print(f"Error updating location: {str(e)}")
        emit('update_error', {'status': 500, 'message': 'Internal Server Error', 'error': str(e)})

@socketio.on('update_location')
def update_location(data):
    try:
        # Extract details from the received data
        email = data.get('email')
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        user_type = data.get("type")
        print(f"Updating Location For {user_type} {email}")


        if not email or not longitude or not latitude:
            emit('update_error', {'status': 400, 'message': 'Missing required parameters'})
            return

        # Establish a connection to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the email exists in the location table
        cur.execute("SELECT COUNT(*) FROM location WHERE email = %s", (email,))
        count = cur.fetchone()[0]

        if count > 0:
            # Update the existing location details for the provided email
            cur.execute("""
                UPDATE location 
                SET longitude = %s, latitude = %s 
                WHERE email = %s
            """, (longitude, latitude, email))
        else:
            # Insert a new record for the email if it doesn't exist
            if user_type:
                cur.execute("""
                    INSERT INTO location (email, longitude, latitude, user_type) 
                    VALUES (%s, %s, %s, %s)
                """, (email, longitude, latitude, user_type))
            else:
                cur.execute("""
                    INSERT INTO location (email, longitude, latitude, user_type) 
                    VALUES (%s, %s, %s, %s)
                """, (email, longitude, latitude, "user"))

        # Commit the changes to the database
        conn.commit()

        # Close the cursor and connection
        cur.close()
        conn.close()

        # Emit a success message back to the client
        emit('update_success', {'status': 200, 'message': 'Location updated successfully'})

    except Exception as e:
        # Handle any exceptions and emit an error event back to the client
        print(f"Error updating location: {str(e)}")
        emit('update_error', {'status': 500, 'message': 'Internal Server Error', 'error': str(e)})


@socketio.on('get_all_locations')
def get_all_locations(data):
    try:
        # Extract the user's email from the received data
        email = data.get('email')
        print(f"Email: {email}")

        if not email:
            emit('get_locations_error', {'status': 400, 'message': 'Email is required'})
            return

        # Establish a connection to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch all locations except for the user's own location
        cur.execute("""
            SELECT email, longitude, latitude, user_type 
            FROM location 
            WHERE email != %s
        """, (email,))

        locations = cur.fetchall()
        print(f"Locations Object: {locations}")

        # Close the cursor and connection
        cur.close()
        conn.close()

        # Format the result as a list of dictionaries
        result = [
            {
                'email': row[0],
                'longitude': float(row[1]),  # Convert Decimal to float
                'latitude': float(row[2]),   # Convert Decimal to float
                'user_type': row[3],
            }
            for row in locations
        ]

        # Emit the locations back to the client
        emit('locations_data', {'status': 200, 'locations': result})

    except Exception as e:
        # Handle any exceptions and emit an error event back to the client
        print(f"Error retrieving locations: {str(e)}")
        emit('get_locations_error', {'status': 500, 'message': 'Internal Server Error', 'error': str(e)})


rider_sockets = {}

@socketio.on('book_ride')
def book_ride(data):
    print('Starting book ride shit')
    user_email = data.get('email')
    user_location = data.get('location_coords')  # User's location should be passed here as a dict {'latitude': ..., 'longitude': ...}
    destinationDetails = data.get("dest_details")
    destination_location = data.get("dest_coords")
    amount = data.get("amount")
    destText = data.get("destination")

    print(f"Email: {user_email}, Location: {user_location}, DestinationDetails: {destinationDetails}, amount: {amount}, destText: {destText}, Destination_location: {destination_location}")


    # Sample data structure for all riders' locations
    # available_riders = [{'email': 'rider1@example.com', 'latitude': ..., 'longitude': ...}, ...]

    available_riders = data.get('allRiders')  # Fetch this from your database or wherever you're storing it

    if not available_riders:
        emit('ride_request_error', {'status': 404, 'message': 'No available riders found'})
        return

    # Find the closest rider
    closest_rider = find_closest_rider(user_location, available_riders)
    print(f"Closest rider is right here: {closest_rider}")

    if closest_rider:
        rider_sid = connected_users.get(closest_rider['email'])
        print(f"Closest rider email; {closest_rider['email']}")
        if rider_sid:
            # Emit a ride request to the closest rider
            socketio.emit('ride_request', {
                'user_email': user_email,
                'location': user_location,
                'rider_email': closest_rider['email'],
                'details': destinationDetails,
                'amount': amount,
                'Place': destText,
                'destination': destination_location
            }, to=rider_sid)  # Send request to the specific rider
            emit('ride_request_sent', {'status': 200, 'message': 'Ride request sent to the rider'})
        else:
            print(f"CON: {connected_users}")
            print('Rider not found')
    else:
        emit('ride_request_error', {'status': 404, 'message': 'No suitable rider found'})


# Function to extract username from email
def extract_username(email):
    return re.split(r'@', email)[0]


@socketio.on('accept_ride')
def handle_accept_ride(data):
    user_email = data.get('user_email')
    driver_email = data.get('driver_email')

    # Generate the ride ID (room name)
    ride_id = f"{extract_username(driver_email)}{extract_username(user_email)}"
    
    # Join both the driver and the user to the room
    join_room(ride_id)

    # Notify both participants they've joined the room
    emit('joined_ride_room', {'ride_id': ride_id, 'message': f"Joined ride room {ride_id}"}, room=ride_id)

    print(f"Driver {driver_email} and User {user_email} joined room {ride_id}")



if __name__ == '__main__':
    try:
        # Initialize database schemas
        database_schemas()
        print("Database schemas initialized successfully.")
    except Exception as e:
        print(f"Exception occurred when initializing database schemas: {str(e)}")

    try:
        # Run SocketIO server
        socketio.run(app, host='0.0.0.0', port=1245, debug=True, use_reloader=True)
    except Exception as e:
        print(f"Exception occurred when starting the SocketIO server: {str(e)}")