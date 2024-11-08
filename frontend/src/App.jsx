import React, { useState, useEffect } from 'react';
import axios from 'axios';
import io from 'socket.io-client';

// Устанавливаем соединение с сервером WebSocket
const socket = io('http://localhost:5000');

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);

  useEffect(() => {
    // Получение сообщений при загрузке
    axios.get('http://localhost:5000/messages')
      .then(response => {
        setMessages(response.data);
      });

    // Обработчик новых сообщений через WebSocket
    socket.on('new_message', (message) => {
      setMessages(prevMessages => [...prevMessages, message]);
    });

    return () => {
      socket.off('new_message');
    };
  }, []);

  const handleLogin = async () => {
    try {
      const response = await axios.post('http://localhost:5000/login', { username, password });
      if (response.status === 200) {
        setIsLoggedIn(true);
      }
    } catch (error) {
      alert('Login failed');
    }
  };

  const handleRegister = async () => {
    try {
      const response = await axios.post('http://localhost:5000/register', { username, password });
      if (response.status === 201) {
        setIsRegistering(false);
      }
    } catch (error) {
      alert('Registration failed');
    }
  };

  const handleSendMessage = async () => {
    const timestamp = new Date().toLocaleString();
    const messageData = { username, message: newMessage, timestamp };
    
    await axios.post('http://localhost:5000/send_message', messageData);
    setNewMessage('');
  };

  return (
    <div className="App">
      {!isLoggedIn ? (
        <div>
          <h2>{isRegistering ? 'Register' : 'Login'}</h2>
          <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button onClick={isRegistering ? handleRegister : handleLogin}>
            {isRegistering ? 'Register' : 'Login'}
          </button>
          <button onClick={() => setIsRegistering(!isRegistering)}>
            {isRegistering ? 'Go to Login' : 'Go to Register'}
          </button>
        </div>
      ) : (
        <div>
          <h2>Chat</h2>
          <div>
            {messages.map((msg, idx) => (
              <div key={idx}>
                <strong>{msg.username}</strong>: {msg.message} <em>{msg.timestamp}</em>
              </div>
            ))}
          </div>
          <textarea value={newMessage} onChange={(e) => setNewMessage(e.target.value)} placeholder="Write a message..." />
          <button onClick={handleSendMessage}>Send</button>
        </div>
      )}
    </div>
  );
}

export default App;
