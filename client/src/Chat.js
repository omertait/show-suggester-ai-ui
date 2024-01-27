import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);


  useEffect(() => {
    axios.get('http://localhost:5000/api/prompt_liked_shows', { withCredentials: true })
      .then(response => {
        
        const serverReply = response.data.reply[0];

        setMessages([{ type: serverReply.type, content: serverReply.content, source: 'server' }]);

      })
      .catch(error => console.error('Error fetching prompt:', error));
  }, []);

  const handleInputChange = (e) => {
    setInputText(e.target.value);
  };

  const handleSend = async () => {
    const userMessage = { type: 'text', content: inputText, source: 'user' };
    setMessages(messages => [...messages, userMessage]);
    setIsLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/message', { message: inputText }, { withCredentials: true });
      
      const serverReplies = response.data.reply;

      // Iterate over each reply and add it to the messages
      serverReplies.forEach(reply => {
        const replyMessage = { type: reply.type, content: reply.content, source: 'server' };
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
      {messages.map((msg, index) => {
        console.log(index);
        let messageClass = msg.source === 'user' ? 'user-message' : 'server-message';
        if (msg.type === 'error') {
          messageClass += ' error-message'; 
        }

        return msg.type === 'text' || msg.type === 'error' ? (
          <div key={index} className={messageClass}>{msg.content}</div>
        ) : (
          <img key={index} src={msg.content} className="chat-image" />
        );
      })}
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
