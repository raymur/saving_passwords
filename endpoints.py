import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


app = Flask(__name__)

db_username = os.environ['DB_USER']
db_password = os.environ['DB_PASS']
db_hostname = os.environ['DB_HOST'] or 'localhost:5432'
db_name = os.environ['DB_NAME'] or 'backend'

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_username}:{db_password}@{db_hostname}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable overhead tracking

db: SQLAlchemy = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)

class Hasher:
    def __init__(self):
        self.ph = PasswordHasher()
  
    def get_hash(self, password):
        return  self.ph.hash(password)        
        
    def is_valid(self, password, hash):
        try:
            result = self.ph.verify(hash, password)
            if result:
                if self.ph.check_needs_rehash(hash):
                    # rehash password
                    pass
                return True
            return False
        except VerifyMismatchError as vme:
            return False
        



@app.route('/ping')
def ping():
    return "pong"

@app.route('/create_user', methods=['POST'])
def create_user():
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username is None or password is None:
        return jsonify({"error": "Both 'username' and 'password' are required"}), 400
    
    hashed_password = Hasher().get_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify('added user')

@app.route('/validate_user', methods=['POST'])
def validate_user():
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username is None or password is None:
        return jsonify({"error": "Both 'username' and 'password' are required"}), 400
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 400
    hashed_password = user.password
    result = Hasher().is_valid(password, hashed_password)
    if not result:
        return jsonify({"error": "Invalid password"}), 400
    return jsonify({"success": "Valid password"}), 200
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)