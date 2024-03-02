import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
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
          <Link to="/Chat">Chat</Link>
          <Link to="/Shows">Shows</Link>
        </nav>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/Chat" element={<Chat />} />
          <Route path="/Shows" element={<Output />} />
        </Routes>
      </Router>
    );
    
};

export default App;
