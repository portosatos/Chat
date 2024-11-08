from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from flask_cors import CORS  # Импортируем CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Включаем CORS для всех доменов, а также для сокетов
CORS(app, supports_credentials=True)

# Настройка CORS для SocketIO
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173")  # Разрешаем CORS для конкретного порта фронтенда

# Модели базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.String(120), nullable=False)

# Регистрация нового пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = generate_password_hash(data['password'])
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400
    
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

# Логин пользователя
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password):
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

# Получение сообщений
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.all()
    return jsonify([{'username': msg.username, 'message': msg.message, 'timestamp': msg.timestamp} for msg in messages])

# Добавление нового сообщения
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    username = data['username']
    message = data['message']
    timestamp = data['timestamp']
    
    new_message = Message(username=username, message=message, timestamp=timestamp)
    db.session.add(new_message)
    db.session.commit()
    
    # Отправка нового сообщения через WebSocket
    socketio.emit('new_message', {'username': username, 'message': message, 'timestamp': timestamp})
    
    return jsonify({'message': 'Message sent'}), 201

# WebSocket обработка сообщений
@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

if __name__ == '__main__':
    # Создание базы данных и таблиц внутри контекста приложения
    with app.app_context():
        db.create_all()  # Создаст базы данных
    socketio.run(app, host='0.0.0.0', port=5000)
