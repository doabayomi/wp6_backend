import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import re
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

app = Flask(__name__)
CORS(app)
# Configure the PostgreSQL database
# Replace 'your_user', 'your_password', 'your_host', 'your_port', and 'your_database'
# with your actual PostgreSQL credentials.
# Example for a local PostgreSQL: 'postgresql://user:password@localhost:5432/mydatabase'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/your_database')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fullname = db.Column(db.String(120), unique=False, nullable=False)
    password_hash = db.Column(db.String(278), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

    # Set password hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check password hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- Database Initialization (Run once to create tables) ---
# To create tables, you would run this Python script directly or
# open a Python shell and run `from app import db; db.create_all()`
# For this simple example, we'll create it directly if it doesn't exist
with app.app_context():
    db.create_all()

# Utility function to validate email format
def is_valid_email(email):
    # Basic regex for email validation
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# --- Signup Route ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    fullname = data.get('fullname')

    if not email or not password:
        return jsonify({'message': 'Email and password are required!'}), 400

    if not fullname:
        return jsonify({'message': 'Full name is required'}), 400

    if not is_valid_email(email):
        return jsonify({'message': 'Invalid email format!'}), 400

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User with this email already exists!'}), 409

    # Create new user
    new_user = User(email=email, fullname=fullname)
    new_user.set_password(password) # Hash the password

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'message': 'An error occurred during registration.', 'error': str(e)}), 500

# --- Login Route ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required!'}), 400

    # Find the user by email
    user = User.query.filter_by(email=email).first()

    # Check if user exists and password is correct
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password!'}), 401

    return jsonify({
    'message': 'Login successful!',
    'fullname': user.fullname
    }), 200

# To run the app
if __name__ == '__main__':
    app.run(debug=True) # Set debug=False in production
