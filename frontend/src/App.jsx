import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Register from './components/Register';
import Login from './components/Login';
import ChatList from './components/ChatList';
import Chat from './components/Chat';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/chats" element={<ChatList />} />
        <Route path="/chats/:chatId" element={<Chat />} />
      </Routes>
    </Router>
  );
}

export default App;
