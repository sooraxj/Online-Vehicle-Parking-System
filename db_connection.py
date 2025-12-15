import mysql.connector

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Default XAMPP MySQL user
        password="",  # Default password for XAMPP
        database="vehicle"  # Replace with your database name
    )
