from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from flask_cors import CORS  # Импортируем CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Настройки базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Включаем CORS для всех доменов, а также для сокетов
# Здесь мы разрешаем доступ как с localhost, так и с вашего внешнего IP
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://172.19.218.55:5173"])

# Настройка CORS для SocketIO
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5173", "http://172.19.218.55:5173"])

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
    try:
        data = request.get_json()

        # Проверяем наличие обязательных данных
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Missing username or password'}), 400

        username = data['username']
        password = generate_password_hash(data['password'])

        # Проверяем, существует ли уже пользователь с таким именем
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'User already exists'}), 400

        # Создаем нового пользователя
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': f'Error during registration: {str(e)}'}), 500

# Логин пользователя
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']

        # Находим пользователя по имени
        user = User.query.filter_by(username=username).first()

        # Проверяем пароль
        if user and check_password_hash(user.password, password):
            return jsonify({'message': 'Login successful'}), 200
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': f'Error during login: {str(e)}'}), 500

# Получение сообщений
@app.route('/messages', methods=['GET'])
def get_messages():
    try:
        messages = Message.query.all()
        return jsonify([{'username': msg.username, 'message': msg.message, 'timestamp': msg.timestamp} for msg in messages])
    except Exception as e:
        return jsonify({'error': f'Error getting messages: {str(e)}'}), 500

# Добавление нового сообщения
@app.route('/send_message', methods=['POST'])
def send_message():
    try:
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
    except Exception as e:
        return jsonify({'error': f'Error sending message: {str(e)}'}), 500

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
    socketio.run(app, host='0.0.0.0', port=5000)  # Запуск на всех интерфейсах
