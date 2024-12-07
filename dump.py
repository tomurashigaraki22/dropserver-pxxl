import pymysql
import os

# Database connection details
host = "dropdatabase-drop.l.aivencloud.com"
port = 17576
user = "avnadmin"
password = "AVNS_Qq4sDCTSQFg2EbiHweg"
database = "defaultdb"
ssl_ca = "./ca-cert.pem"  # Path to your CA certificate
dump_file = "dumpfile.sql"  # Output file for the dump

# Establishing a connection to MySQL
connection = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database,
    ssl={'ca': ssl_ca}
)

cursor = connection.cursor()

# Get all the table names
cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()

# Open the dump file
with open(dump_file, "w") as file:
    # Loop over each table
    for (table,) in tables:
        # Get table structure (CREATE statement)
        cursor.execute(f"SHOW CREATE TABLE {table};")
        create_table_stmt = cursor.fetchone()[1]
        file.write(f"{create_table_stmt};\n\n")

        # Get all rows from the table
        cursor.execute(f"SELECT * FROM {table};")
        rows = cursor.fetchall()

        # Write the insert statements for each row
        for row in rows:
            insert_stmt = f"INSERT INTO {table} ({', '.join([str(col) for col in row])}) VALUES ({', '.join([repr(value) for value in row])});"
            file.write(f"{insert_stmt}\n")

# Close the connection
cursor.close()
connection.close()

print(f"Database dump saved to {dump_file}")
