from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import emit, join_room, leave_room, SocketIO
from extensions.extensions import get_db_connection, socketio, app, mysql, mail
from flask_mail import Message
from extensions.db_schemas import database_schemas
from functions.auth import userSignup, login, verifyEmail, changePassword, get_balance, add_to_balance, driverLogin, driverSignup, checkVerificationStatus, uploadVerificationImages, saveLinksToDB
from functions.riders import haversine, find_closest_riders, endRide, endRide2, get_rider_location_by_email
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

@app.route("/get_connected_users", methods=["GET", "POST"])
def getusersthen():
    serializable_connected_users = {k: str(v) for k, v in connected_users.items()}
    serializable_rider_sockets = {k: str(v) for k, v in rider_sockets.items()}

    return jsonify({'message': serializable_connected_users, 'rider': serializable_rider_sockets})


@app.route("/alter-table", methods=["GET"])
def alterTable():
    try:
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM location
        """)
        # Execute the ALTER TABLE queries to add new column

        


        # Commit the changes
        conn.commit()

        # Close the cursor and connection
        cur.close()
        conn.close()

        return jsonify({"Message": "Columns added successfully"}), 200

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
def uploadImagess():
    print("Uploading images")
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
    transaction_id, reference_id = generate_transaction_and_reference_ids()  # Assuming you have this function
    months_paid = int(request.form.get('months_paid', 0))  # Convert to int with a default of 0

    # Validate inputs
    if not email or not transaction_id or not reference_id or months_paid <= 0:
        return jsonify({"message": "Invalid input parameters.", "status": 400})

    try:
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Calculate the expiration date
        expiration_date = calculate_expiration_date(months_paid)

        # Debugging output
        print("Email:", email)
        print("Transaction ID:", transaction_id)
        print("Reference ID:", reference_id)
        print("Months Paid:", months_paid)
        print("Expiration Date:", expiration_date)

        # Insert the subscription into the database
        cur.execute("""
            INSERT INTO subscriptions (email, transaction_id, reference_id, months_paid, expires_at) 
            VALUES (%s, %s, %s, %s, %s)
        """, (email, transaction_id, reference_id, months_paid, expiration_date))

        conn.commit()

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}", "status": 500})

    return jsonify({"message": "Subscription created successfully.", "expires_at": expiration_date, "status": 201})


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


@app.route('/get-ridess', methods=['GET'])
def get_ridess():
    user_email = request.args.get('email')
    print(f"User_emial: {user_email}")

    if not user_email:
        return jsonify({"error": "Email parameter is required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Query to fetch rides where the user's email matches either email or driver_email
        cur.execute("""
            SELECT *
            FROM user_rides
            WHERE email = %s OR driver_email = %s
        """, (user_email, user_email))

        rides = cur.fetchall()

        # Format the result as a list of dictionaries
        rides_list = [
            {
                'id': row[0],
                'email': row[1],
                'driver_email': row[2],
                'ride_id': row[3],
                'created_at': row[4].isoformat(),  # Convert datetime to string
                'status': row[5],
                'reference_id': row[6]
            }
            for row in rides
        ]

        # Close the cursor and connection
        cur.close()
        conn.close()

        return jsonify({"rides": rides_list, "status": 200}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



    

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
        user_type = data.get("type")  # Make sure 'type' is provided correctly
        choice = data.get('choice')
        print(f"Updating Location For {user_type} {email} {choice}")

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
                SET longitude = %s, latitude = %s, driver_type = %s 
                WHERE email = %s
            """, (longitude, latitude, choice, email))  # Corrected order here
        else:
            # Insert a new record for the email if it doesn't exist
            if user_type:
                cur.execute(""" 
                    INSERT INTO location (email, longitude, latitude, user_type, driver_type) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (email, longitude, latitude, user_type, choice))
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
            SELECT email, longitude, latitude, user_type, driver_type
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
                'choice': row[4],
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
    choice = data.get("choice")
    phone_no = data.get("phone_no")
    user_email = data.get('email')
    user_location = data.get('location_coords')  # User's location as {'latitude': ..., 'longitude': ...}
    destinationDetails = data.get("dest_details")
    destination_location = data.get("dest_coords")
    amount = data.get("amount")
    destText = data.get("destination")

    print(f"Email: {user_email}, Location: {user_location}, DestinationDetails: {destinationDetails}, amount: {amount}, destText: {destText}, Destination_location: {destination_location}")

    rejected_riders = data.get('rejected_riders', [])  # Default to an empty list if not provided

    # Find the closest riders, sorted from closest to farthest
    sorted_riders = find_closest_riders(user_location=user_location, user_email=user_email, rejected_riders=rejected_riders, choice=choice)
    print(f"Sorted riders from closest to farthest: {sorted_riders}")

    if not sorted_riders:
        emit('ride_request_error', {'status': 404, 'message': 'No available riders found'})
        return

    # Try to find the first connected rider in the sorted list
    for rider in sorted_riders:
        rider_email = rider['email']
        rider_sids = connected_users.get(rider_email)
        print(f"Checking rider email: {rider_email}")

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
                'destination': destination_location,
                'phone_no': phone_no
            }, to=rider_sid)  # Send request to the specific rider
            emit('ride_request_sent', {'status': 200, 'message': 'Ride request sent to the rider'})
            return  # Exit after successfully sending the request to a connected rider
        else:
            print(f"Rider {rider_email} not found in connected users, moving to the next rider.")

    # If no connected rider was found
    print('No connected riders found')
    emit('ride_request_error', {'status': 404, 'message': 'No connected riders found'})
    return




# Function to extract username from email
def extract_username(email):
    return re.split(r'@', email)[0]


@socketio.on('accept_ride')
def handle_accept_ride(data):
    user_email = data.get('user_email')
    driver_email = data.get('driver_email')
    ride_reference, tx_reference_id = generate_transaction_and_reference_ids()

    # Generate the ride ID (could be used for tracking)
    ride_id = f"{extract_username(driver_email)}_{extract_username(user_email)}"
    
    # Emit to both the user and driver
    print(f"Driver {driver_email} and User {user_email} are being notified about ride {ride_id}")
    
    # Notify the driver (the one who sent the request)
    emit('joined_ride', {
        'ride_id': ride_id,
        'message': f"Joined ride {ride_id}",
        'driver_email': driver_email,
        'email': user_email,
        'ride_reference': ride_reference
    }, to=request.sid)  # Emit back to the driver who initiated the ride request

    # Automatically add the user (rider) to the ride
    if user_email in connected_users:
        print(f"Connected: {connected_users} {user_email}")
        
        # Get one socket ID for the user_email
        try:
            user_sid = next(iter(connected_users.get(user_email)))  # Get one session ID from the set
            print(f"UserSID: {user_sid}")
            driver_location = get_rider_location_by_email(rider_email=driver_email)
            
            # Notify the user directly to "automatically" join the ride
            socketio.emit('auto_join_ride', {
                'ride_id': ride_id,
                'message': f"You have automatically joined the ride {ride_id}",
                'driver_email': driver_email,
                'driver_location': driver_location,
                'ride_reference': ride_reference
            }, to=user_sid)  # Use the session ID to emit the message directly

        except StopIteration:
            print(f"Error: No session ID found for {user_email}.")
    else:
        print(f"User {user_email} is not connected.")

    print(f"Driver {driver_email} and User {user_email} automatically joined ride {ride_id}")

@app.route("/start_ride", methods=["POST"])
def start_ride():
    try:
        data = request.get_json()
        user_email = data.get('user_email')
        driver_email = data.get('driver_email')

        if not user_email or not driver_email:
            print(f"Missing parameters: {user_email} {driver_email}")
            return jsonify({"Message": "Missing required parameters"}), 400

        # Generate a ride_id and transaction details
        ride_id = f"{extract_username(driver_email)}_{extract_username(user_email)}"
        ref_id, transaction_id = generate_transaction_and_reference_ids()

        # Get SIDs for user and driver
        user_sids = connected_users.get(user_email)
        driver_sids = connected_users.get(driver_email)

        # Validate SID connections for both user and driver
        if not user_sids or not driver_sids:
            print(f"User or driver not connected. User SID: {user_sids}, Driver SID: {driver_sids}")
            return jsonify({"Message": "One or both users are not connected"}), 400

        # Database operations: check or create ride record
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT status FROM user_rides 
            WHERE ride_id = %s AND driver_email = %s AND email = %s
            ORDER BY created_at DESC LIMIT 1
        """, (ride_id, driver_email, user_email))
        existing_ride = cur.fetchone()

        ride_data = {
            'ride_id': ride_id,
            'driver_email': driver_email,
            'user_email': user_email,
            'ref_id': ref_id,
        }

        if existing_ride and existing_ride[0] == 'ongoing':
            print(f"Ride is already ongoing: {existing_ride}")
            user_sid = next(iter(connected_users.get(user_email)))
            if user_sid:
                socketio.emit("ride_started", ride_data, to=user_sid)
                print(f"Emitted to user SID: {user_sid}")
            else:
                print(f"User SID for {user_email} not found in connected users.")

            # Emit to driver
            driver_sid = next(iter(connected_users.get(driver_email)))
            if driver_sid:
                socketio.emit("ride_started", ride_data, to=driver_sid)
                print(f"Emitted to driver SID: {driver_sid}")
            else:
                print(f"Driver SID for {driver_email} not found in connected users.")
            return jsonify({"Message": "Ride is already ongoing"}), 400
        elif existing_ride:
            # Update status if ride exists but is not ongoing
            cur.execute("""
                UPDATE user_rides 
                SET status = %s, reference_id = %s 
                WHERE ride_id = %s AND driver_email = %s AND email = %s
            """, ('ongoing', ref_id, ride_id, driver_email, user_email))
        else:
            # Create a new ride record
            cur.execute("""
                INSERT INTO user_rides (email, driver_email, ride_id, reference_id, status) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user_email, driver_email, ride_id, ref_id, 'ongoing'))

        conn.commit()

        # Emit "ride_started" event to both user and driver
        

        # Emit to user
        user_sid = next(iter(connected_users.get(user_email)))
        if user_sid:
            socketio.emit("ride_started", ride_data, to=user_sid)
            print(f"Emitted to user SID: {user_sid}")
        else:
            print(f"User SID for {user_email} not found in connected users.")

        # Emit to driver
        driver_sid = next(iter(connected_users.get(driver_email)))
        if driver_sid:
            socketio.emit("ride_started", ride_data, to=driver_sid)
            print(f"Emitted to driver SID: {driver_sid}")
        else:
            print(f"Driver SID for {driver_email} not found in connected users.")

        return jsonify({"Message": "Ride started successfully"}), 200

    except Exception as e:
        print(f"Error in start_ride: {str(e)}")
        return jsonify({"Message": f"An error occurred: {str(e)}"}), 500


@socketio.on("ride_destination_reached")
def rideDestReached(data):
    try:
        user_email = data.get('user_email')

        if not user_email:
            print("Missing user_email")
            return {"Message": "Missing required params"}, 400

        # Retrieve the user's socket IDs from the connected users dictionary
        user_sids = connected_users.get(user_email)
        
        # Check if the user is connected
        if user_sids:
            for sid in user_sids:
                # Emit a "destination_reached" event to the user
                socketio.emit("destination_reached", {"Message": "Destination has been reached"}, to=sid)
            return {"Message": "Notification sent to user"}, 200
        else:
            print(f"No active connections for user: {user_email}")
            return {"Message": "User not connected"}, 404
    except Exception as e:
        print(f"Error in rideDestReached: {e}")
        return {"Message": "Internal server error"}, 500


@socketio.on("arrived_customer")
def arrivedCustomerLocation(data):
    try:
        user_email = data.get("user_email")
        driver_email = data.get("driver_email")

        if not user_email or not driver_email:
            print(f"Missing one of the params: user_email={user_email}, driver_email={driver_email}")
            return {"Message": "Missing required params"}, 400
        
        user_sids = connected_users.get(user_email)
        if user_sids:
            for sid in user_sids:
                socketio.emit("reached_customer", {"Message": "Driver has arrived at your location"}, to=sid)
            return {"Message": "Notification sent to all connected instances of user"}, 200
        else:
            print(f"No active connections for user: {user_email}")
            return {"Message": "User not connected"}, 404
    except Exception as e:
        print(f"Error in arrivedCustomerLocation: {e}")
        return {"Message": "Internal server error"}, 500




@socketio.on('initiateCall')
def handle_initiate_call(data):
    try:
        # Extract required data
        calling = data.get('calling')
        caller = data.get("caller")
        callId = data.get("callId")


        # Check if necessary data is provided
        if not calling or not caller or not callId:
            print("Missing required fields in 'initiateCall' data.")
            return {"status": "error", "message": "Missing required fields"}, 400

        # Retrieve the receiver's session IDs
        receiver_sids = connected_users.get(calling)
        
        if not receiver_sids:
            print(f"No active session found for user: {calling}")
            return {"status": "error", "message": "Receiver not connected"}, 404

        # Emit the incoming call event to each session ID of the receiver
        sid = next(iter(receiver_sids))
        socketio.emit("incomingCall", {
            "callId": callId,
            "caller": caller
        }, to=sid)
        print(f"Incoming call sent to {calling} (session ID: {sid})")

        # Success response after all emits are sent
        return {"status": "success", "message": "Call initiated"}, 200

    except Exception as e:
        # Log and return in case of any exception
        print(f"Error in 'handle_initiate_call': {e}")
        return {"status": "error", "message": str(e)}, 500



@socketio.on('answerCall')
def handle_answer_call(data):
    receiver_socket_id = connected_users.get(data['to'])
    sid = next(iter(receiver_socket_id))
    if receiver_socket_id:
        socketio.emit('callAnswer', {'answer': data['answer']}, to=sid)  # Notify caller
        print(f'Call answered by {data["to"]}')

@socketio.on('iceCandidate')
def handle_ice_candidate(data):
    print(f"Data: {data}")
    receiver_socket_id = connected_users.get(data['to'])  # Get receiver from data

    if receiver_socket_id:
        for sid in receiver_socket_id:
            print(f"ice candidate: {receiver_socket_id}")
            socketio.emit('iceCandidates', {'candidate': data['candidate']}, to=sid)  # Send ICE candidate
        print(f'ICE candidate sent to {data["to"]}')
    else:
        print(f"No active connection found for {data['to']}. ICE candidate not sent.")


@socketio.on('callResponse')
def handle_call_response(data):
    if data['accept']:
        # Call accepted logic (e.g., create a connection)
        print('Call accepted')
    else:
        # Call rejected logic
        print('Call rejected')


    
@socketio.on("start_ride")
def startRide(data):
    try:
        user_email = data.get('user_email')
        driver_email = data.get('driver_email')
        
        if not user_email or not driver_email:
            print(f"Missing parameters: {user_email} {driver_email}")
            return {"Message": "Missing required parameters"}, 400

        # Generate a ride_id and transaction details
        ride_id = f"{extract_username(driver_email)}_{extract_username(user_email)}"
        ref_id, transaction_id = generate_transaction_and_reference_ids()

        # Get SIDs for user and driver
        user_sids = connected_users.get(user_email)
        driver_sids = connected_users.get(driver_email)

        # Validate SID connections for both user and driver
        if not user_sids or not driver_sids:
            print(f"User or driver not connected. User SID: {user_sids}, Driver SID: {driver_sids}")
            return {"Message": "One or both users are not connected"}, 400

        # Database operations: check or create ride record
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT status FROM user_rides 
            WHERE ride_id = %s AND driver_email = %s AND email = %s
            ORDER BY created_at DESC LIMIT 1
        """, (ride_id, driver_email, user_email))
        existing_ride = cur.fetchone()

        ride_data = {
            'ride_id': ride_id,
            'driver_email': driver_email,
            'user_email': user_email,
            'ref_id': ref_id,
        }

        if existing_ride and existing_ride[0] == 'ongoing':
            print(f"Ride already ongoing: {existing_ride}")
            user_sid = next(iter(connected_users.get(user_email)))
            print(user_sid)
            if user_sid:
                socketio.emit("ride_started", ride_data, to=user_sid)
                print(f"Emitted to user SID: {user_sid}")
            else:
                print(f"User SID for {user_email} not found in connected users.")

            # Emit to driver
            print()
            driver_sid = next(iter(connected_users.get(driver_email)))
            print(driver_sid)
            if driver_sid:
                socketio.emit("ride_started", ride_data, to=driver_sid)
                print(f"Emitted to driver SID: {driver_sid}")
            else:
                print(f"Driver SID for {driver_email} not found in connected users.")
            return {"Message": "Ride is already ongoing"}, 400
        elif existing_ride:
            # Update status if ride exists but is not ongoing
            cur.execute("""
                UPDATE user_rides 
                SET status = %s, reference_id = %s 
                WHERE ride_id = %s AND driver_email = %s AND email = %s
            """, ('ongoing', ref_id, ride_id, driver_email, user_email))
        else:
            # Create a new ride record
            cur.execute("""
                INSERT INTO user_rides (email, driver_email, ride_id, reference_id, status) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user_email, driver_email, ride_id, ref_id, 'ongoing'))

        conn.commit()

        # Emit "ride_started" event to both user and driver
        

        # Emit to user
        user_sid = next(iter(connected_users.get(user_email)))
        print(user_sid)
        if user_sid:
            socketio.emit("ride_started", ride_data, to=user_sid)
            print(f"Emitted to user SID: {user_sid}")
        else:
            print(f"User SID for {user_email} not found in connected users.")

        # Emit to driver
        print()
        driver_sid = next(iter(connected_users.get(driver_email)))
        print(driver_sid)
        if driver_sid:
            socketio.emit("ride_started", ride_data, to=driver_sid)
            print(f"Emitted to driver SID: {driver_sid}")
        else:
            print(f"Driver SID for {driver_email} not found in connected users.")

        return {"Message": "Ride started successfully"}, 200

    except Exception as e:
        print(f"Error in startRide: {str(e)}")
        return {"Message": f"An error occurred: {str(e)}"}, 500

    
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
        choice = data.get("choice")
        
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
        next_closest_rider = find_closest_riders(user_location, user_email, rejected_riders[user_email], choice)
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
    driver_sids = next(iter(connected_users.get(driver_email)))

    if driver_sids:
        # Emit the 'endedRide' event to all SIDs linked to the driver_email
        socketio.emit('endedRide', {'user_email': user_email}, to=driver_sids)


@socketio.on('joinRoom')
def handleJoinRoom(room):
    join_room(room)
    emit('newRoomMember', {'text': f'User has joined the room: {room}'}, room=room)

@app.route('/get-messages', methods=['POST'])
def get_messages():
    conn = get_db_connection()
    ride_reference = request.form.get('ride_reference')  # Retrieve ride_reference from FormData

    if not ride_reference:
        return jsonify({"error": "ride_reference is required", "status": 400})

    try:
        cur = conn.cursor()  # Using cur instead of conn.cursor() context manager
        cur.execute("""
            SELECT email, receiver_email, message, created_at 
            FROM messages 
            WHERE unique_identifier = %s 
            ORDER BY created_at ASC
        """, (ride_reference,))
        messages = cur.fetchall()
        
        # Format messages into JSON
        formatted_messages = [
            {
                "sender": message[0],  # email
                "receiver": message[1],  # receiver_email
                "message": message[2],  # message
                "timestamp": message[3].strftime('%Y-%m-%d %H:%M:%S')  # created_at
            }
            for message in messages
        ]
        
        return jsonify({"messages": formatted_messages, "status": 200})
    except Exception as e:
        print("Error retrieving messages:", e)
        return jsonify({"error": "Failed to retrieve messages", "status": 500})

@socketio.on('sendMessage')
def handleSendMessage(data):
    print("Received data:", data)  # Log the received data

    room = data['room']
    receiver = data['receiver']
    message = data['message']
    sender = data['sender']
    ride_reference = data['ride_reference']
    conn = get_db_connection()
    cur = conn.cursor()

    # Insert the message into the database
    try:
        cur.execute("""
            INSERT INTO messages (email, receiver_email, unique_identifier, message)
            VALUES (%s, %s, %s, %s)
        """, (sender, receiver, ride_reference, message))
        conn.commit()
        print("Message saved to database.")
    except Exception as e:
        print("Error saving message to database:", e)
        conn.rollback()

    # Get the socket IDs of the receiver and sender from the connected_users dictionary
    sid_receiver = connected_users.get(receiver)
    sid_sender = connected_users.get(sender)

    # Emit the message to the receiver if they are connected
    if sid_receiver:
        sid_receiver_send = next(iter(sid_receiver))  # Assuming sid_receiver is a set or list of socket IDs
        socketio.emit("message_received", {
            "message": message,
            "sender": sender,
        }, to=sid_receiver_send)

    # Emit the message to the sender for confirmation or feedback, if they are connected
    if sid_sender:
        sid_sender_send = next(iter(sid_sender))
        socketio.emit("message_received", {
            "message": message,
            "sender": sender,
        }, to=sid_sender_send)

    emit("message", {
        "message": message,
        "sender": sender
    }, room=room)




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






### admin Side


@app.route("/getusercount", methods=["GET", "POST"])
def getNoUsers():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Query to count the number of users
        cur.execute("""
            SELECT COUNT(*) FROM userauth
        """)
        
        # Fetch the result
        result = cur.fetchone()
        user_count = result[0] if result else 0

        # Close the connection
        cur.close()
        conn.close()

        # Return the user count as JSON
        return jsonify({"number_of_users": user_count}), 200

    except Exception as e:
        # Handle exceptions and return error
        return jsonify({"error": str(e)}), 500

@app.route("/getNumberofdrivers", methods=["GET", "POST"])
def getNoDrivers():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Query to count the number of users with user_type 'driver'
        cur.execute("""
            SELECT COUNT(*) FROM userauth WHERE user_type = %s
        """, ('driver',))

        # Fetch the result
        result = cur.fetchone()
        driver_count = result[0] if result else 0

        # Close the connection
        cur.close()
        conn.close()

        # Return the driver count as JSON
        return jsonify({"number_of_drivers": driver_count}), 200

    except Exception as e:
        # Handle exceptions and return error
        return jsonify({"error": str(e)}), 500

@app.route("/getnumberofusers", methods=["GET", "POST"])
def getNoRegularUsers():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Query to count the number of users with user_type 'user'
        cur.execute("""
            SELECT COUNT(*) FROM userauth WHERE user_type = %s
        """, ('user',))

        # Fetch the result
        result = cur.fetchone()
        user_count = result[0] if result else 0

        # Close the connection
        cur.close()
        conn.close()

        # Return the user count as JSON
        return jsonify({"number_of_regular_users": user_count}), 200

    except Exception as e:
        # Handle exceptions and return error
        return jsonify({"error": str(e)}), 500
    
@app.route("/getSubscribedDriversInfo", methods=["GET"])
def getSubscribedDriversInfo():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Query to count the number of subscribed drivers and calculate total revenue
        cur.execute("""
            SELECT COUNT(*), SUM(months_paid * 1000) as total_revenue FROM subscriptions
        """)  # Assuming 1000 is the subscription cost per month

        result = cur.fetchone()
        driver_count = result[0] if result else 0
        total_revenue = result[1] if result else 0

        # Close connection
        cur.close()
        conn.close()

        # Return the result as JSON
        return jsonify({
            "subscribed_drivers": driver_count,
            "total_revenue": total_revenue
        }), 200

    except Exception as e:
        # Handle exceptions and return error
        return jsonify({"error": str(e)}), 500


def send_status_update_email(recipient_email, new_status):
    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verification Status Update</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #fff;
                font-family: Arial, sans-serif;
            }}
            .container {{
                width: 100%;
                padding: 20px;
                background-color: #F27E05;
            }}
            .content {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #fff;
                border-radius: 5px;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                color: #000;
                font-size: 24px;
                margin-bottom: 10px;
            }}
            p {{
                color: #333;
                font-size: 16px;
                line-height: 1.5;
            }}
            .status {{
                font-weight: bold;
                font-size: 18px;
            }}
            .footer {{
                margin-top: 20px;
                font-size: 14px;
                color: #555;
            }}
            a {{
                color: #F27E05;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <h1>Verification Status Update</h1>
                <p>Dear User,</p>
                <p>Your verification status has been updated.</p>
                <p class="status">New Status: <strong>{new_status}</strong></p>
                <p>Thank you for your patience.</p>
                <p>Best regards,<br>The Team</p>
                <div class="footer">
                    <p>For any inquiries, please contact us at <a href="mailto:support@example.com">support@example.com</a></p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    msg = Message("Update Status On Verification", recipients=[recipient_email])
    msg.html = html_body
    mail.send(msg)

@app.route('/updateVerificationStatus/<string:email>', methods=['POST'])
def update_verification_status(email):
    try:
        data = request.get_json()
        new_status = data['status']

        conn = get_db_connection()
        cur = conn.cursor()

        # Update the status in the database
        cur.execute("UPDATE verificationdetails SET status = %s WHERE email = %s", (new_status, email))
        conn.commit()

        # Send email notification
        send_status_update_email(email, new_status)

        cur.close()
        conn.close()

        return jsonify({"message": "Status updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/getRides', methods=['GET'])
def get_rides():
    try:
        # Establish connection to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # SQL query to fetch all rides
        cursor.execute("""
            SELECT id, email, driver_email, ride_id, created_at, status, reference_id 
            FROM user_rides
        """)
        
        # Fetch all results
        rides = cursor.fetchall()
        
        # Convert the fetched rides into a list of dictionaries (array of objects)
        ride_list = []
        for ride in rides:
            ride_list.append({
                'id': ride[0],
                'email': ride[1],
                'driver_email': ride[2],
                'ride_id': ride[3],
                'created_at': ride[4],
                'status': ride[5],
                'reference_id': ride[6]
            })
        
        # Close database connection
        cursor.close()
        conn.close()
        
        # Return the rides data as JSON
        return jsonify({'rides': ride_list}), 200
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/getUsers', methods=['GET'])
def get_users():
    try:
        # Establish connection to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query to fetch all user data except password
        cursor.execute("""
            SELECT id, email, phone_number, created_at, user_type, balance, age, gender 
            FROM userauth
        """)

        # Fetch all results
        users = cursor.fetchall()

        # Restructure the fetched data into an array of dictionaries
        result = []
        for user in users:
            result.append({
                'id': user[0],
                'email': user[1],
                'phone_number': user[2],
                'created_at': user[3],
                'user_type': user[4],
                'balance': user[5],
                'age': user[6],
                'gender': user[7]
            })

        # Close database connection
        cursor.close()
        conn.close()

        return jsonify({'users': result}), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500



@app.route('/deleteUser', methods=['DELETE'])
def delete_user():
    try:
        # Get the email from the request body
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required to delete a user'}), 400

        # Establish connection to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query to delete user by email
        cursor.execute("DELETE FROM userauth WHERE email = %s", (email,))

        # Commit the transaction
        conn.commit()

        # Close database connection
        cursor.close()
        conn.close()

        return jsonify({'message': f'User with email {email} has been deleted successfully'}), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500




@app.route("/getVerificationDetails", methods=["GET"])
def getVerificationDetails():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Query to fetch all details from verificationdetails
        cur.execute("SELECT * FROM verificationdetails")

        # Fetch all rows
        details = cur.fetchall()

        # Define the keys (table column names)
        keys = [
            "id", "email", "phone_number", "gender", "plate_number", "driver_photo",
            "license_photo", "car_photo", "plate_photo", "car_color", "driver_with_car_photo",
            "status"
        ]

        # Format the data into an array of dictionaries
        verification_data = [dict(zip(keys, row)) for row in details]

        # Close the connection
        cur.close()
        conn.close()

        # Return the result as JSON
        return jsonify({"verificationdetails": verification_data}), 200

    except Exception as e:
        # Handle exceptions
        return jsonify({"error": str(e)}), 500



### end of admin side



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