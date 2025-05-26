from extensions.extensions import get_db_connection

def database_schemas():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        # cur.execute("TRUNCATE TABLE location")
        # cur.execute("TRUNCATE TABLE pushtoken")
        # cur.execute("TRUNCATE TABLE driver_location")
        # cur.execute("TRUNCATE TABLE userauth")
        # cur.execute("TRUNCATE TABLE verificationdetails")
        # cur.execute("TRUNCATE TABLE messages")
        # cur.execute("TRUNCATE TABLE subscriptions")
        # cur.execute("TRUNCATE TABLE user_rides")
        # cur.execute("TRUNCATE TABLE driver_rides")
        # cur.execute("SET FOREIGN_KEY_CHECKS = 1")

        # In the database_schemas() function, update the call_tokens table creation:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS call_tokens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                token VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_expired BOOLEAN DEFAULT FALSE
            )
        """)

        cur.execute("""
            ALTER TABLE call_tokens
            ADD COLUMN channel_name VARCHAR(255) NOT NULL
        """)

        # Create tables if they do not exist
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
            CREATE TABLE IF NOT EXISTS pushtoken (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                token VARCHAR(255) DEFAULT NULL
            );
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
        
        # Create userauth table if it does not exist
        cur.execute(""" 
            CREATE TABLE IF NOT EXISTS userauth (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(80) NOT NULL,
                password VARCHAR(80) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_type VARCHAR(80) NOT NULL
            )
        """)
        # Check if columns already exist before adding them
        cur.execute("SHOW COLUMNS FROM userauth")
        existing_columns = [column[0] for column in cur.fetchall()]

        if 'phone_number' not in existing_columns:
            cur.execute("ALTER TABLE userauth ADD COLUMN phone_number VARCHAR(80) NOT NULL")

        if 'user_type' not in existing_columns:
            cur.execute("ALTER TABLE userauth ADD COLUMN user_type VARCHAR(80) NOT NULL DEFAULT 'user'")

        if 'balance' not in existing_columns:
            cur.execute("ALTER TABLE userauth ADD COLUMN balance INT NOT NULL DEFAULT 0")

        if 'age' not in existing_columns:
            cur.execute("ALTER TABLE userauth ADD COLUMN age INT NOT NULL DEFAULT 18")

        if 'gender' not in existing_columns:
            cur.execute("ALTER TABLE userauth ADD COLUMN gender VARCHAR(80) NOT NULL DEFAULT 'Male'")

        cur.execute(""" 
            CREATE TABLE IF NOT EXISTS verificationdetails(
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(80) NOT NULL,
                phone_number VARCHAR(255) NOT NULL,
                gender VARCHAR(80) NULL,
                plate_number VARCHAR(80) NOT NULL,
                driver_photo VARCHAR(255),
                license_photo VARCHAR(255),
                car_photo VARCHAR(255),
                plate_photo VARCHAR(255),
                car_color VARCHAR(80),
                driver_with_car_photo VARCHAR(255),
                status VARCHAR(80) NOT NULL DEFAULT 'pending'
            );
        """)

        cur.execute("""ALTER TABLE verificationdetails
            MODIFY COLUMN gender VARCHAR(80) DEFAULT NULL;
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                receiver_email VARCHAR(255) NOT NULL,
                unique_identifier VARCHAR(255) NOT NULL,
                message VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            ALTER TABLE messages
            ADD COLUMN isRead BOOLEAN DEFAULT FALSE
        """)
        cur.execute(""" 
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(80) NOT NULL,
                transaction_id VARCHAR(100) NOT NULL,
                reference_id VARCHAR(100) NOT NULL,
                months_paid INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)        
        cur.execute(""" 
            CREATE TABLE IF NOT EXISTS user_rides (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(80) NOT NULL,
                driver_email VARCHAR(80) NOT NULL,
                ride_id VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(80) NOT NULL DEFAULT 'ongoing',
                reference_id VARCHAR(255) NOT NULL
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
        print(f"Exception occurred: {str(e)}")
