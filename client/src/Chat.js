import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);


  useEffect(() => {
    axios.get('http://localhost:5000/api/prompt_liked_shows', { withCredentials: true })
      .then(response => {
        const serverMessage = { text: response.data.message, source: 'server' };
        setMessages([serverMessage]);
      })
      .catch(error => console.error('Error fetching prompt:', error));
  }, []);

  const handleInputChange = (e) => {
    setInputText(e.target.value);
  };

  const handleSend = async () => {
    const userMessage = { text: inputText, source: 'user' };
    setMessages(messages => [...messages, userMessage]);
    setIsLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/message', { message: inputText }, { withCredentials: true });
      
      const serverReplies = response.data.reply;

      // Iterate over each reply and add it to the messages
      serverReplies.forEach(reply => {
        const replyMessage = { text: reply, source: 'server' };
        setMessages(messages => [...messages, replyMessage]);
    });
    } catch (error) {
      console.error('Error sending response:', error);
    } finally {
      setIsLoading(false); 
    }

    setInputText('');
  };

  return (
    <div className="chat-container">
      <div className="chat-display">
        {messages.map((msg, index) => (
          <div key={index} className={msg.source === 'user' ? 'user-message' : 'server-message'}>{msg.text}</div>
        ))}
        {isLoading && <div className="loading-animation"></div>} {/* Spinner */}
      </div>
      <div className="chat-input">
        <input type="text" value={inputText} onChange={handleInputChange} />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default Chat;
