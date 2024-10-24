from dotenv import load_dotenv
import os
import pymysql
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mysqldb import MySQL
from engineio.payload import Payload

load_dotenv()
app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465  # SMTP Port for SSL
app.config["MAIL_USE_SSL"] = True  # Enable SSL
app.config["MAIL_USE_TLS"] = False  # No need for TLS if using SSL
app.config["MAIL_USERNAME"] = "noreply.dropapp@gmail.com"  # Your email username
app.config["MAIL_PASSWORD"] = "iaik logl kifo tzzw"  # Your email password
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")  # Default sender email address

# Initialize SocketIO with Eventlet
Payload.max_decode_packets = 500
socketio = SocketIO(app, max_http_buffer_size=10**7, async_mode='gevent')  # Use Eventlet as async mode
db = SQLAlchemy(app)
mysql = MySQL(app)
mail = Mail(app)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

def get_db_connection():
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT")),
        ssl={'ssl': {'ssl-mode': os.getenv('DB_SSL_MODE')}}
    )
    return connection

