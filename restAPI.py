from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy import text, create_engine, Column, Integer, String, MetaData, Table, BigInteger
from sqlalchemy.exc import IntegrityError

import bleach

load_dotenv()

db_username = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_hostname = os.getenv('DB_HOST')
db_name = os.getenv('DB_DATABASE')
db_port = os.getenv('DB_PORT')
CONNECTION = f'mysql+pymysql://{db_username}:{db_password}@{db_hostname}/{db_name}'

def create_db():
    _engine = create_engine(CONNECTION)
    metadata = MetaData()
    _users_table = Table(
        'registered',
        metadata,
        Column('ID', INTEGER(unsigned=True), primary_key=True, autoincrement=True),
        Column('Username', String(23), unique=True, nullable=False),
        Column('Password', String(32), nullable=False),
        Column('Email', String(39), nullable=False),
        Column('discord_id', BigInteger, nullable=False),
    )
    metadata.create_all(_engine)
    return

create_db()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = CONNECTION
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class registered(db.Model):
    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    username = db.Column(db.String(23), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(39), nullable=False)
    discord_id = db.Column(INTEGER(20, unsigned=True), nullable=False)

@app.route('/register/', methods=['POST'])
def register():
    data = request.get_json()

    username = bleach.clean(data['username'], tags=[], attributes={}, strip=True)
    password = bleach.clean(data['password'], tags=[], attributes={}, strip=True)
    email = bleach.clean(data['email'], tags=[], attributes={}, strip=True)
    discord_id = data['discord_id']

    user_taken = registered.query.filter_by(username=username).first()
    if user_taken:
        return {'error': 'Username is already taken.'}, 404

    new_user = registered(username=username, password=password, email=email, discord_id=discord_id)
    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'error': 'Failed to create user. Please try again.'}, 500
    return {'username': f'You have been registered {new_user.username}'}, 201

@app.route('/user/<int:discord_id>', methods=['GET'])
def get_user(discord_id):
    row = registered.query.filter_by(discord_id=discord_id).first()
    if row:
        return {'username': row.username, 'email': row.email}, 200
    return {'message': 'User not found'}, 404

if __name__ == '__main__':
    app.run(port=db_port)
