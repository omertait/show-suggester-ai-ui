import React,{ useState , useEffect} from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import {server_path} from "./config"
import Home from './Home';
import Chat from './Chat';
import Output from './Output';
import './App.css';



const App = () => {
  
    // const [serverResponse, setServerResponse] = useState('');
  
    // useEffect(() => {
    //   fetch(server_path+'/api/test')
    //     .then(response => response.json())
    //     .then(data => setServerResponse(data.messages))
    //     .catch(error => console.error('Error fetching data: ', error));
    // }, []);

     return (
      
      <Router>
        <nav>
          <Link to="/">Home</Link>
          <Link to="/chat">Chat</Link>
          <Link to="/movies">Movies</Link>
        </nav>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/movies" element={<Output />} />
        </Routes>
      </Router>
    );
    
};

export default App;
