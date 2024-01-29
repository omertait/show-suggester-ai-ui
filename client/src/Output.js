import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const Output = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [movies, setMovies] = useState([]); // This should be fetched from an API
  const [minMatchPercentage, setMinMatchPercentage] = useState(0);
  const [activeMovie, setActiveMovie] = useState(null);

  useEffect(() => {
    const fetchShows = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/shows');
        setMovies(response.data); // Assuming the response data is the array of shows
      } catch (error) {
        console.error('Error fetching new shows:', error);
      }
    };

    fetchShows();
  }, []);

  const exampleMovies = [
    {
      Title: "Inception",
      matchPercentage: 98,
      Image: "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_.jpg"
    },
    {
      Title: "The Matrix",
      matchPercentage: 95,
      Image: "https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg"
    },
    {
      Title: "Interstellar",
      matchPercentage: 93,
      Image: "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_.jpg"
    },
    // Add more movies as needed
  ];

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleMatchPercentageChange = (e) => {
    setMinMatchPercentage(e.target.value);
  };

  const searchMovies = () => {
    // Implement search logic or API call here
  };

  const filteredMovies = movies.filter(movie => movie?.matchPercentage ? movie?.matchPercentage >= minMatchPercentage : movie);
  
  return (
    <div className="app">
      <header className="app-header">
        <input 
          type="text" 
          className="search-bar"
          placeholder="Search movies or shows" 
          value={searchTerm} 
          onChange={handleSearchChange} 
        />
        <button className="search-button" onClick={searchMovies}>Search</button>
      </header>
      <div className="filter-bar">
        <label htmlFor="match-percentage">Match Percentage: {minMatchPercentage}%</label>
        <input 
          type="range" 
          id="match-percentage"
          min="0" 
          max="100" 
          value={minMatchPercentage} 
          onChange={handleMatchPercentageChange} 
        />
      </div>
      <main>
        <div className="recommendations">
          {/* Recommendations logic goes here */}
        </div>
        <div className="movie-grid">
          {
          filteredMovies.map((movie, index) => (
            <div
            key={index} 
            className={`movie-card ${activeMovie === movie ? 'active' : ''}`}
            
            >
              <img src={movie.Image} alt={movie.Title} className="movie-thumbnail" onClick={() => setActiveMovie(movie)}/>
              <div className="movie-info">
                <h3>{movie.Title}</h3>
                {movie.matchPercentage ? <p>{movie.matchPercentage}% Match</p> : <p>New movie</p>}
                {activeMovie === movie && (
                  <div className="movie-details">
                    <p className="movie-description">{movie.Description}</p>
                    <button className="close-btn" onClick={() => setActiveMovie(null)}>X</button>
                  </div>
                )}
              </div>
              
            </div>
            
          ))}
          
          
        </div>
      </main>
    </div>
  );
};

export default Output;
