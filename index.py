from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import emit, join_room, leave_room, SocketIO
from extensions.extensions import get_db_connection, socketio, app, mysql
from extensions.db_schemas import database_schemas
from functions.auth import userSignup, login, verifyEmail, changePassword, get_balance, add_to_balance, driverLogin, driverSignup, checkVerificationStatus, uploadVerificationImages, saveLinksToDB
from functions.riders import haversine, find_closest_rider, endRide, endRide2
import re
import datetime
from functions.generate_ids import generate_transaction_and_reference_ids

###testing purposes###

@app.route('/tables', methods=['GET'])
def get_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    cur.close()
    return jsonify(tables)

@app.route("/alter-table", methods=["GET"])
def alterTable():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the 'status' column exists in 'user_rides'
        cur.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'user_rides' AND COLUMN_NAME = 'status'
        """)
        status_column_exists = cur.fetchone()

        # If 'status' column doesn't exist, add it
        if not status_column_exists:
            cur.execute("""
                ALTER TABLE user_rides
                ADD COLUMN status VARCHAR(80) NOT NULL DEFAULT 'ongoing'
            """)
            conn.commit()  # Commit the changes

        # Check if the 'expires_at' column exists in 'subscriptions'
        cur.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'subscriptions' AND COLUMN_NAME = 'expires_at'
        """)
        expires_at_column_exists = cur.fetchone()

        # If 'expires_at' column doesn't exist, add it
        if not expires_at_column_exists:
            cur.execute("""
                ALTER TABLE subscriptions
                ADD COLUMN expires_at TIMESTAMP DEFAULT NULL
            """)
            conn.commit()  # Commit the changes

        return jsonify({"Message": "'status' and 'expires_at' columns added or already exist"}), 200

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

@app.route("/endRide", methods=["GET", "POST"])
def endTheRide():
    return endRide()

@app.route("/endRide2", methods=["GET", "POST"])
def endTheRide2():
    return endRide2()

def calculate_expiration_date(months_paid):
    # Calculate the expiration date based on the number of months paid
    return datetime.datetime.now() + datetime.timedelta(days=months_paid * 30)  # Approximation

@app.route('/subscribe', methods=['POST'])
def subscribe_user():
    # Extract data from the request form
    email = request.form.get('email')
    transaction_id = generate_transaction_and_reference_ids()  # Assuming you have this function
    reference_id = request.form.get("reference_id")
    months_paid = request.form.get('months_paid')

    # Validate inputs
    if not email or not transaction_id or not reference_id or not months_paid or int(months_paid) <= 0:
        return jsonify({"message": "Invalid input parameters.", "status": 400})  # Return status code in JSON body

    try:
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Calculate the expiration date
        expiration_date = calculate_expiration_date(int(months_paid))

        # Insert the subscription into the database
        cur.execute("""
            INSERT INTO subscriptions (email, transaction_id, reference_id, months_paid, expires_at) 
            VALUES (%s, %s, %s, %s, %s)
        """, (email, transaction_id, reference_id, months_paid, expiration_date))

        conn.commit()

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}", "status": 500})  # Return status code in JSON body
    
    return jsonify({"message": "Subscription created successfully.", "expires_at": expiration_date, "status": 201})  # Status code 201 in JSON body



@app.route('/check_subscription', methods=['POST'])
def check_subscription_status():
    # Extract email from the request form
    email = request.form.get('email')

    if not email:
        return jsonify({"message": "Email is required.", "status": 400})  # Status in JSON body

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
        current_time = datetime.datetime.now()

        if expires_at > current_time:
            days_left = (expires_at - current_time).days

            # Check if the subscription expires within 3 days
            if days_left <= 3:
                # Handle the case where subscription is expiring soon
                print(f"Subscription for {email} will expire in {days_left} days.")
                return jsonify({
                    "message": "User is currently subscribed.",
                    "expires_at": expires_at,
                    "status": 200,
                    "days_left": days_left,
                    "expires_soon": True  # Subscription is expiring soon
                })

            return jsonify({
                "message": "User is currently subscribed.",
                "expires_at": expires_at,
                "status": 200,
                "days_left": days_left,
                "expires_soon": False  # Subscription is not expiring soon
            })

        else:
            return jsonify({"message": "User's subscription has expired.", "status": 200})

    # Return 409 status in JSON body if no active subscription is found
    return jsonify({"message": "No active subscription found.", "status": 409})
    

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
    print('Starting book ride...')
    user_email = data.get('email')
    user_location = data.get('location_coords')  # User's location as {'latitude': ..., 'longitude': ...}
    destinationDetails = data.get("dest_details")
    destination_location = data.get("dest_coords")
    amount = data.get("amount")
    destText = data.get("destination")

    print(f"Email: {user_email}, Location: {user_location}, DestinationDetails: {destinationDetails}, amount: {amount}, destText: {destText}, Destination_location: {destination_location}")

    available_riders = data.get('allRiders')  # Should be fetched from your database
    rejected_riders = data.get('rejected_riders', [])  # Default to an empty list if not provided
    print(f"Available Riders: {available_riders}, Rejected Riders: {rejected_riders}")

    if not available_riders:
        emit('ride_request_error', {'status': 404, 'message': 'No available riders found'})
        return

    # Find the closest rider, passing rejected_riders if available
    closest_rider = find_closest_rider(user_location=user_location, user_email=user_email, rejected_riders=rejected_riders)
    print(f"Closest rider is: {closest_rider}")

    if closest_rider:
        rider_email = closest_rider['email']
        rider_sids = connected_users.get(rider_email)
        print(f"Closest rider email: {rider_email}")

        if rider_sids:
            # Use the first socket ID from the set to send the message
            rider_sid = next(iter(rider_sids))  # Get one socket ID from the set
            emit('ride_request', {
                'user_email': user_email,
                'location': user_location,
                'rider_email': rider_email,
                'details': destinationDetails,
                'amount': amount,
                'Place': destText,
                'destination': destination_location
            }, to=rider_sid)  # Send request to the specific rider
            emit('ride_request_sent', {'status': 200, 'message': 'Ride request sent to the rider'})
        else:
            print('Rider not found in connected users')
            emit('ride_request_error', {'status': 404, 'message': 'Rider not found in connected users'})
    else:
        emit('ride_request_error', {'status': 404, 'message': 'No suitable rider found'})




# Function to extract username from email
def extract_username(email):
    return re.split(r'@', email)[0]


@socketio.on('accept_ride')
def handle_accept_ride(data):
    user_email = data.get('user_email')
    driver_email = data.get('driver_email')

    # Generate the ride ID (could be used for tracking)
    ride_id = f"{extract_username(driver_email)}_{extract_username(user_email)}"
    
    # Emit to both the user and driver
    print(f"Driver {driver_email} and User {user_email} are being notified about ride {ride_id}")
    
    # Notify the driver (the one who sent the request)
    emit('joined_ride', {
        'ride_id': ride_id,
        'message': f"Joined ride {ride_id}",
        'driver_email': driver_email,
        'email': user_email
    }, to=request.sid)  # Emit back to the driver who initiated the ride request

    # Automatically add the user (rider) to the ride
    if user_email in connected_users:
        print(f"Connected: {connected_users} {user_email}")
        
        # Get one socket ID for the user_email
        try:
            user_sid = next(iter(connected_users.get(user_email)))  # Get one session ID from the set
            print(f"UserSID: {user_sid}")
            
            # Notify the user directly to "automatically" join the ride
            socketio.emit('auto_join_ride', {
                'ride_id': ride_id,
                'message': f"You have automatically joined the ride {ride_id}",
                'driver_email': driver_email
            }, to=user_sid)  # Use the session ID to emit the message directly

        except StopIteration:
            print(f"Error: No session ID found for {user_email}.")
    else:
        print(f"User {user_email} is not connected.")

    print(f"Driver {driver_email} and User {user_email} automatically joined ride {ride_id}")


@socketio.on("start_ride")
def startRide(data):
    try:
        user_email = data.get('user_email')
        driver_email = data.get('driver_email')
        
        if not user_email or not driver_email:
            return jsonify({"Message": "Missing required parameters"}), 400

        # Generate a ride_id
        ride_id = f"{extract_username(driver_email)}_{extract_username(user_email)}"
        ref_id, transaction_id = generate_transaction_and_reference_ids()

        # Get the connection SIDs for both the driver and user
        user_sid = connected_users.get(user_email)
        driver_sid = connected_users.get(driver_email)

        if not user_sid or not driver_sid:
            return jsonify({"Message": "One or both users are not connected"}), 400

        # Check if a ride already exists for this combination
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT status FROM user_rides 
            WHERE ride_id = %s AND driver_email = %s AND email = %s
            ORDER BY created_at DESC LIMIT 1
        """, (ride_id, driver_email, user_email))
        existing_ride = cur.fetchone()

        if existing_ride:
            if existing_ride[0] == 'ongoing':
                return jsonify({"Message": "Ride is already ongoing"}), 400
            else:
                # If the ride is not ongoing, update its status to 'ongoing'
                cur.execute("""
                    UPDATE user_rides 
                    SET status = %s, reference_id = %s 
                    WHERE ride_id = %s AND driver_email = %s AND email = %s
                """, ('ongoing', ref_id, ride_id, driver_email, user_email))
        else:
            # If the ride doesn't exist, create a new one with 'ongoing' status
            cur.execute("""
                INSERT INTO user_rides (email, driver_email, ride_id, reference_id, status) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user_email, driver_email, ride_id, ref_id, 'ongoing'))

        conn.commit()

        # Emit the "ride_started" event to both user and driver
        ride_data = {
            'ride_id': ride_id,
            'driver_email': driver_email,
            'user_email': user_email
        }

        # Emit to user
        socketio.emit("ride_started", ride_data, to=user_sid)
        
        # Emit to driver
        socketio.emit("ride_started", ride_data, to=driver_sid)

        return jsonify({"Message": "Ride started successfully"}), 200

    except Exception as e:
        return jsonify({"Message": f"An error occurred: {str(e)}"}), 500
    
@socketio.on("complete_ride")
def completeRide(data):
    try:
        user_email = data.get('user_email')
        driver_email = data.get('driver_email')
        
        if not user_email or not driver_email:
            return jsonify({"Message": "Missing required parameters"}), 400

        # Generate a ride_id
        ride_id = f"{extract_username(driver_email)}_{extract_username(user_email)}"

        # Get the connection SIDs for both the driver and user
        user_sid = connected_users.get(user_email)
        driver_sid = connected_users.get(driver_email)

        if not user_sid or not driver_sid:
            return jsonify({"Message": "One or both users are not connected"}), 400

        # Check if the ride exists and is ongoing
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT status FROM user_rides 
            WHERE ride_id = %s AND driver_email = %s AND email = %s
            ORDER BY created_at DESC LIMIT 1
        """, (ride_id, driver_email, user_email))
        existing_ride = cur.fetchone()

        if not existing_ride:
            return jsonify({"Message": "Ride does not exist"}), 400

        if existing_ride[0] == 'completed':
            return jsonify({"Message": "Ride is already marked as completed"}), 400

        if existing_ride[0] != 'ongoing':
            return jsonify({"Message": "Cannot complete ride that is not ongoing, current status is {existing_ride[0]}"}), 400

        # Update the ride status to 'completed'
        cur.execute("""
            UPDATE user_rides 
            SET status = %s 
            WHERE ride_id = %s AND driver_email = %s AND email = %s
        """, ('completed', ride_id, driver_email, user_email))

        conn.commit()

        # Emit the "ride_completed" event to both user and driver
        ride_data = {
            'ride_id': ride_id,
            'driver_email': driver_email,
            'user_email': user_email
        }

        # Emit to user
        socketio.emit("ride_completed", ride_data, to=user_sid)
        
        # Emit to driver
        socketio.emit("ride_completed", ride_data, to=driver_sid)

        return jsonify({"Message": "Ride marked as completed successfully"}), 200

    except Exception as e:
        return jsonify({"Message": f"An error occurred: {str(e)}"}), 500
    

# Dictionary to store rejected drivers temporarily for each ride request
rejected_riders = {}

@socketio.on('reject_ride')
def handle_reject_ride(data):
    try:
        # Extract the emails and other details from the data
        print("Rejecting Ride")
        user_email = data.get('user_email')
        driver_email = data.get('driver_email')
        user_location = data.get('user_location')
        destinationDetails = data.get("dest_details")
        destination_location = data.get("dest_coords")
        amount = data.get("amount")
        destText = data.get("destination")
        
        print(f"UserLocation: {user_location}, DriverEmail: {driver_email}, UserEmail: {user_email}")

        # Ensure both emails are provided
        if not user_email or not driver_email:
            return emit('error', {'message': 'Missing user_email or driver_email'})

        # Add the rejecting driver to the rejected riders list
        if user_email in rejected_riders:
            rejected_riders[user_email].append(driver_email)
        else:
            rejected_riders[user_email] = [driver_email]

        # Find the next closest available driver excluding rejected drivers
        next_closest_rider = find_closest_rider(user_location, user_email, rejected_riders[user_email])
        print(next_closest_rider)

        if not next_closest_rider:
            # If no drivers are available, notify the user
            print(f"No available drivers found for user: {user_email}")
            user_sids = connected_users.get(user_email)
            if user_sids:
                for user_sid in user_sids:
                    socketio.emit('no_available_drivers', {
                        'message': 'No available drivers at the moment.',
                        'user_email': user_email
                    }, to=user_sid)
            return jsonify({"message": "No available drivers", "status": 404})

        # Assign the ride to the next closest rider
        new_driver_email = next_closest_rider['email']
        ride_id = f"{extract_username(new_driver_email)}_{extract_username(user_email)}"

        # Get the session ID (sid) of the new driver
        new_driver_sid = connected_users.get(new_driver_email)

        if new_driver_sid:
            # Notify the new driver about the ride request
            socketio.emit('ride_request', {
                'ride_id': ride_id,
                'user_email': user_email,
                'driver_email': new_driver_email,
                'location': user_location,
                'details': destinationDetails,
                'destination': destination_location,
                'amount': amount,
                'destText': destText
            }, to=new_driver_sid)

            # Notify the user that a new driver has been found
            user_sid = connected_users.get(user_email)
            if user_sid:
                socketio.emit('ride_rejected_new_driver', {
                    'ride_id': ride_id,
                    'message': f"A new driver {new_driver_email} has been found for your ride.",
                    'driver_email': new_driver_email,
                    'user_location': user_location,
                    'destinationDetails': destinationDetails,
                    'destination_location': destination_location,
                    'amount': amount,
                    'destText': destText
                }, to=user_sid)

        else:
            # If the new driver is not connected, continue searching or return an error
            return emit('error', {'message': 'New driver is not available at the moment'})

    except Exception as e:
        emit('error', {'message': f'An error occurred: {str(e)}'})



@socketio.on('update_status')
def updateStatus(data):
    user_email = data.get('user_email')
    driver_email = data.get('driver_email')
    ride_id = data.get('ride_id')

    




# When the user receives the invitation, they join the room
@socketio.on("join_the_room")
def join_the_room(data):
    print(f"Joining room: {data}")
    user_email = data.get('user_email')
    driver_email = data.get('driver_email')
    ride_id = f"{extract_username(driver_email)}_{extract_username(user_email)}"


    # User joins the room
    join_room(ride_id)

    # Notify the room that the user has joined
    emit('joined_ride_room', {
        'ride_id': ride_id, 
        'message': f"User joined ride room {ride_id}",
    }, room=ride_id)

    print(f"User joined room {ride_id}")

@socketio.on('endedRide')
def endedTheRide(data):
    driver_email = data.get('driver_email')
    user_email = data.get('user_email')

    if not driver_email or not user_email:
        return

    # Assuming connected_users is a dictionary with driver_email as key and a list of SIDs as value
    driver_sids = connected_users.get(driver_email)

    if driver_sids:
        # Emit the 'endedRide' event to all SIDs linked to the driver_email
        socketio.emit('endedRide', {'user_email': user_email}, to=driver_sids)


@socketio.on('joinRoom')
def handleJoinRoom(room):
    join_room(room)
    emit('message', {'text': f'User has joined the room: {room}'}, room=room)

@socketio.on('sendMessage')
def handleSendMessage(data):
    room = data['room']
    emit('message', data, room=room)  # Send message to all in the room


@socketio.on("get_driver_details")
def getDriverDetails(data):
    driver_email = data.get('driver_email')

    # Check if driver_email exists in the request
    if not driver_email:
        emit('driver_not_found', {
            'message': 'Driver email is missing'
        })
        return

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch driver details from the database
        cur.execute("""
            SELECT car_color, car_photo, driver_photo, driver_with_car_photo, email, gender, id, 
                   license_photo, phone_number, plate_number, plate_photo 
            FROM verificationdetails WHERE email = %s
        """, (driver_email,))

        driver_details = cur.fetchone()  # Fetch one record

        # Log the fetched details
        print(f"Driver Details: {driver_details}")

        # If driver details are found, send them to the client
        if driver_details:
            # Map the result to the schema format
            driver_data = {
                "car_color": driver_details[0],
                "car_photo": driver_details[1],
                "driver_photo": driver_details[2],
                "driver_with_car_photo": driver_details[3],
                "email": driver_details[4],
                "gender": driver_details[5],
                "id": driver_details[6],
                "license_photo": driver_details[7],
                "phone_number": driver_details[8],
                "plate_number": driver_details[9],
                "plate_photo": driver_details[10],
                "status": "success"
            }
            emit("driver_details_sent", driver_data)
        else:
            # If no driver details found, emit 'driver_not_found'
            emit('driver_not_found', {
                'message': 'Driver not found'
            })

    except Exception as e:
        # Handle database or other exceptions
        print(f"Error fetching driver details: {e}")
        emit('server_error', {
            'message': 'An error occurred while fetching driver details'
        })



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