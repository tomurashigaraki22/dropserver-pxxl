import math
from extensions.extensions import get_db_connection
from flask import Flask, request, jsonify
from functions.generate_ids import generate_transaction_and_reference_ids


def endRide2():
    try:
        # Extract data from the request form
        ride_id = request.form.get('ride_id')
        driver_email = request.form.get("driver_email")
        user_email = request.form.get('user_email')
        status = request.form.get("status")
        transaction_id, ref_id = generate_transaction_and_reference_ids()

        # Ensure the required fields are provided
        if not ride_id or not driver_email or not user_email or not status:
            return jsonify({"Message": "Missing required parameters"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Check the current status of the ride, ordered by the most recent one
        cur.execute("""
            SELECT status 
            FROM user_rides 
            WHERE ride_id = %s AND driver_email = %s AND email = %s 
            ORDER BY created_at DESC LIMIT 1
        """, (ride_id, driver_email, user_email))
        existing_ride = cur.fetchone()

        if existing_ride:
            # If the ride exists and status is 'ongoing', update it to 'cancelled'
            if existing_ride[0] == 'ongoing':
                cur.execute("""
                    UPDATE user_rides 
                    SET status = %s, reference_id = %s 
                    WHERE ride_id = %s AND driver_email = %s AND email = %s
                """, ('cancelled', ref_id, ride_id, driver_email, user_email))
                conn.commit()
                return jsonify({"Message": "Ride status updated to cancelled"}), 200
            else:
                return jsonify({"Message": f"Ride is not in 'ongoing' status, current status is {existing_ride[0]}"}), 201
        else:
            # If the ride doesn't exist, insert a new record with 'cancelled' status
            cur.execute("""
                INSERT INTO user_rides (email, driver_email, ride_id, reference_id, status) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user_email, driver_email, ride_id, ref_id, 'cancelled'))
            conn.commit()
            return jsonify({"Message": "New ride created with cancelled status"}), 200

    except Exception as e:
        return jsonify({"Message": f"An error occurred: {str(e)}"}), 500


def endRide():
    try:
        # Extract data from the request form
        ride_id = request.form.get('ride_id')
        driver_email = request.form.get("driver_email")
        user_email = request.form.get('user_email')
        status = request.form.get("status")
        ref_id, transaction_id = generate_transaction_and_reference_ids()

        # Ensure the required fields are provided
        if not ride_id or not driver_email or not user_email or not status:
            return jsonify({"Message": "Missing required parameters", "status": 400})

        conn = get_db_connection()
        cur = conn.cursor()

        # Check the current status of the ride
        cur.execute("SELECT status FROM user_rides WHERE ride_id = %s AND driver_email = %s AND email = %s", (ride_id, driver_email, user_email))
        existing_ride = cur.fetchone()

        if existing_ride:
            # If the ride exists and status is 'In Route', update it to 'cancelled'
            if existing_ride[0] == 'ongoing':
                cur.execute("""
                    UPDATE user_rides 
                    SET status = %s, reference_id = %s 
                    WHERE ride_id = %s AND driver_email = %s AND email = %s
                """, ('cancelled', ref_id, ride_id, driver_email, user_email))
                conn.commit()
                return jsonify({"Message": "Ride status updated to cancelled", "status": 200})
            else:
                return jsonify({"Message": f"Ride is not in 'In Route' status, current status is {existing_ride[0]}", "status": 201})
        else:
            # If the ride doesn't exist, insert a new record with 'cancelled' status
            cur.execute("""
                INSERT INTO user_rides (email, driver_email, ride_id, reference_id, status) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user_email, driver_email, ride_id, ref_id, 'cancelled'))
            conn.commit()
            return jsonify({"Message": "New ride created with cancelled status", "status": 200})

    except Exception as e:
        return jsonify({"Message": f"An error occurred: {str(e)}", "status": 500})


def find_closest_rider_main(user_location, user_email, rejected_riders, choice):
    # Get database connection
    conn = get_db_connection()
    cur = conn.cursor()

    # Execute the query to fetch all driver locations except the current user
    cur.execute("""
        SELECT email, longitude, latitude, user_type, driver_type
        FROM location 
        WHERE email != %s
    """, (user_email,))

    locations = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    conn.close()

    # Format the result as a list of dictionaries
    available_riders = [
        {
            'email': row[0],
            'longitude': float(row[1]),  # Convert Decimal to float
            'latitude': float(row[2]),   # Convert Decimal to float
            'user_type': row[3],
            'choice': row[4],
        }
        for row in locations
    ]

    # List to store drivers along with their distance to the user
    riders_with_distance = []
    print(f"Available Riders: {available_riders}")

    # Iterate through the list of available riders (from the DB result)
    for rider in available_riders:
        if rider['user_type'] == 'driver' and rider['email'] not in rejected_riders and rider['choice'] == choice:
            rider_location = (rider['latitude'], rider['longitude'])
            distance = haversine((user_location['latitude'], user_location['longitude']), rider_location)

            # Append rider with their distance to the list
            riders_with_distance.append({
                'email': rider['email'],
                'longitude': rider['longitude'],
                'latitude': rider['latitude'],
                'distance': distance
            })

    # Sort riders by distance from the user (closest to farthest)
    sorted_riders = sorted(riders_with_distance, key=lambda x: x['distance'])

    # Return the closest rider if available, or None
    return sorted_riders[0] if sorted_riders else None



def haversine(coord1, coord2):
    # Radius of the Earth in kilometers
    R = 6371.0
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Distance in kilometers


def find_closest_riders(user_location, user_email, rejected_riders, choice):
    # Get database connection
    conn = get_db_connection()
    cur = conn.cursor()

    # Execute the query to fetch all driver locations except the current user
    cur.execute("""
        SELECT email, longitude, latitude, user_type, driver_type
        FROM location 
        WHERE email != %s
    """, (user_email,))

    locations = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    conn.close()

    # Format the result as a list of dictionaries
    available_riders = [
        {
            'email': row[0],
            'longitude': float(row[1]),  # Convert Decimal to float
            'latitude': float(row[2]),   # Convert Decimal to float
            'user_type': row[3],
            'choice': row[4],
        }
        for row in locations
    ]

    # List to store drivers along with their distance to the user
    riders_with_distance = []
    print(f"Available Riders: {available_riders}")

    # Iterate through the list of available riders (from the DB result)
    for rider in available_riders:
        if rider['user_type'] == 'driver' and rider['email'] not in rejected_riders and rider['choice'] == choice:
            rider_location = (rider['latitude'], rider['longitude'])
            distance = haversine((user_location['latitude'], user_location['longitude']), rider_location)

            # Append rider with their distance to the list
            riders_with_distance.append({
                'email': rider['email'],
                'longitude': rider['longitude'],
                'latitude': rider['latitude'],
                'distance': distance
            })

    # Sort riders by distance from the user (closest to farthest)
    sorted_riders = sorted(riders_with_distance, key=lambda x: x['distance'])

    return sorted_riders


def get_rider_location_by_email(rider_email):
    try:
        # Get database connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Execute the query to fetch the rider's location based on their email
        cur.execute("""
            SELECT email, longitude, latitude
            FROM location
            WHERE email = %s
        """, (rider_email,))

        # Fetch the result
        result = cur.fetchone()

        # Check if a location was found for the rider
        if result:
            # Format the result as a dictionary
            rider_location = {
                'email': result[0],
                'longitude': float(result[1]),  # Convert Decimal to float if needed
                'latitude': float(result[2])    # Convert Decimal to float if needed
            }
        else:
            rider_location = None  # No location found

    except Exception as e:
        # Log the error or handle it as needed
        print(f"Error fetching location for email {rider_email}: {e}")
        rider_location = None

    return rider_location

