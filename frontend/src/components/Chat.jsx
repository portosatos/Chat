import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

function Chat() {
  const { chatId } = useParams();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    const fetchMessages = async () => {
      const response = await fetch(`http://192.168.1.7:5000/chats/${chatId}/messages`);
      const data = await response.json();
      setMessages(data);
    };
    fetchMessages();
  }, [chatId]);

  const sendMessage = async () => {
    const userId = localStorage.getItem('userId'); // Получаем userId из localStorage
    if (!userId) {
      alert('You must be logged in to send a message');
      return;
    }
  
    if (newMessage.trim() !== '' && newMessage.length <= 100) {
      const response = await fetch(`http://192.168.1.7:5000/chats/${chatId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: newMessage, user_id: userId }), // Use user_id here
      });
      const data = await response.json();
      if (data.success) {
        setMessages([...messages, data]);
        setNewMessage('');
      } else {
        alert(data.message);
      }
    } else {
      alert('Message must be non-empty and less than 100 characters.');
    }
  };
  

  return (
    <div>
      <h1>Chat</h1>
      <div>
        {messages.map((msg, index) => (
          <div key={index}>
            <strong>{msg.username}:</strong> {msg.content} <em>{msg.timestamp}</em>
          </div>
        ))}
      </div>
      <input
        type="text"
        value={newMessage}
        onChange={(e) => setNewMessage(e.target.value)}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default Chat;
