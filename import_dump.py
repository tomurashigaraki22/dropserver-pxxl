import pymysql
import os

def execute_sql_dump():
    # Database connection using the same credentials from extensions.py
    connection = pymysql.connect(
        host="db.pxxl.pro",
        user="user_4f0d1b7f",
        password="e654ddd650d97b45f1c7e77f6953c2b1",
        db="db_5c68dc69",
        port=51489,
        ssl={'ssl': {'ssl-mode': 'REQUIRED'}}
    )
    
    try:
        cursor = connection.cursor()
        
        # Read the SQL dump file
        with open('/Users/devtomiwa/Desktop/dropserver/dumpfile.sql', 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split the SQL content into individual statements
        # Remove empty statements and comments
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        print(f"Found {len(statements)} SQL statements to execute...")
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    print(f"Executing statement {i}/{len(statements)}...")
                    cursor.execute(statement)
                    connection.commit()
                    print(f"✓ Statement {i} executed successfully")
                except Exception as e:
                    print(f"✗ Error executing statement {i}: {e}")
                    print(f"Statement: {statement[:100]}...")
                    # Continue with next statement instead of stopping
                    continue
        
        print("\n✓ Database import completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()
        print("Database connection closed.")

if __name__ == "__main__":
    print("Starting database import from dumpfile.sql...")
    execute_sql_dump()