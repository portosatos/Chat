import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function ChatList() {
  const [chats, setChats] = useState([]);
  const [chatName, setChatName] = useState('');
  const navigate = useNavigate();

  async function createChat() {
    if (!chatName) {
      console.error('Chat name is required');
      return;
    }

    try {
      const response = await fetch('http://192.168.1.7:5000/chats', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ chat_name: chatName }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Chat created:', data);

      fetchChats();
      setChatName('');
    } catch (error) {
      console.error('Error creating chat:', error);
    }
  }

  async function fetchChats() {
    try {
      const response = await fetch('http://192.168.1.7:5000/chats', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const chats = await response.json();
      console.log('Fetched chats:', chats);
      setChats(chats);
    } catch (error) {
      console.error('Error fetching chats:', error);
    }
  }

  useEffect(() => {
    fetchChats();
  }, []);

  return (
    <div>
      <h1>Chats</h1>
      <input
        type="text"
        value={chatName}
        onChange={(e) => setChatName(e.target.value)}
        placeholder="Enter chat name"
      />
      <button onClick={createChat}>Create Chat</button>
      <ul>
        {chats.map((chat) => (
          <li key={chat.id} onClick={() => navigate(`/chats/${chat.id}`)}>
            {chat.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ChatList;
