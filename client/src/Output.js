import React, { useState } from 'react';
import './App.css';

const Output = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [movies, setMovies] = useState([]); // This should be fetched from an API
  const [minMatchPercentage, setMinMatchPercentage] = useState(0);

  const exampleMovies = [
    {
      title: "Inception",
      matchPercentage: 98,
      thumbnail: "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_.jpg"
    },
    {
      title: "The Matrix",
      matchPercentage: 95,
      thumbnail: "https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg"
    },
    {
      title: "Interstellar",
      matchPercentage: 93,
      thumbnail: "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_.jpg"
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

  const filteredMovies = exampleMovies.filter(movie => movie.matchPercentage >= minMatchPercentage);

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
          {filteredMovies.map((movie, index) => (
            <div key={index} className="movie-card">
              <img src={movie.thumbnail} alt={movie.title} className="movie-thumbnail" />
              <div className="movie-info">
                <h3>{movie.title}</h3>
                <p>{movie.matchPercentage}% Match</p>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
};

export default Output;
