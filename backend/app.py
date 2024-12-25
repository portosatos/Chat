from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Helper Functions
def sanitize_input(input_str):
    return re.sub(r"[;'\"]", '', input_str)

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = sanitize_input(data.get('username'))
    password = sanitize_input(data.get('password'))

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required.'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Username already exists.'}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User registered successfully.'})


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = sanitize_input(data.get('username'))
    password = sanitize_input(data.get('password'))

    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401

    return jsonify({'success': True, 'userId': user.id, 'message': 'Login successful.'})


@app.route('/create_chat', methods=['POST'])
def create_chat():
    data = request.json
    chat_name = sanitize_input(data.get('chat_name'))

    if not chat_name:
        return jsonify({'success': False, 'message': 'Chat name is required.'}), 400

    new_chat = Chat(name=chat_name)
    db.session.add(new_chat)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Chat created successfully.'})


@app.route('/chats', methods=['GET', 'POST'])
def chats():
    if request.method == 'POST':
        data = request.json
        chat_name = sanitize_input(data.get('chat_name'))

        if not chat_name:
            return jsonify({'success': False, 'message': 'Chat name is required.'}), 400

        new_chat = Chat(name=chat_name)
        db.session.add(new_chat)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Chat created successfully.'})

    chats = Chat.query.all()
    return jsonify([{'id': chat.id, 'name': chat.name, 'created_at': chat.created_at} for chat in chats])


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    chat_id = data.get('chat_id')
    user_id = data.get('user_id')
    content = sanitize_input(data.get('content'))

    if not content or len(content) > 100:
        return jsonify({'success': False, 'message': 'Invalid message content.'}), 400

    new_message = Message(chat_id=chat_id, user_id=user_id, content=content)
    db.session.add(new_message)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Message sent successfully.'})


@app.route('/get_chats', methods=['GET'])
def get_chats():
    chats = Chat.query.all()
    return jsonify([{'id': chat.id, 'name': chat.name, 'created_at': chat.created_at} for chat in chats])


@app.route('/get_messages/<int:chat_id>', methods=['GET'])
def get_messages(chat_id):
    messages = Message.query.filter_by(chat_id=chat_id).all()
    return jsonify([
        {
            'id': message.id,
            'user_id': message.user_id,
            'content': message.content,
            'timestamp': message.timestamp
        } for message in messages
    ])


@app.route('/chats/<int:chat_id>/messages', methods=['GET', 'POST'])
def chat_messages(chat_id):
    if request.method == 'GET':
        messages = db.session.query(
            Message.id,
            Message.content,
            Message.timestamp,
            User.username
        ).join(User, Message.user_id == User.id).filter(Message.chat_id == chat_id).all()

        return jsonify([
            {
                'id': message.id,
                'username': message.username,
                'content': message.content,
                'timestamp': message.timestamp
            } for message in messages
        ])
    
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
        content = sanitize_input(data.get('content'))

        if not content or len(content) > 100:
            return jsonify({'success': False, 'message': 'Invalid message content.'}), 400

        new_message = Message(chat_id=chat_id, user_id=user_id, content=content)
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Message sent successfully.'})


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'joined_at': user.joined_at
    })


@app.route('/chat/<int:chat_id>', methods=['GET'])
def get_chat(chat_id):
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({'success': False, 'message': 'Chat not found.'}), 404

    return jsonify({
        'id': chat.id,
        'name': chat.name,
        'created_at': chat.created_at
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
