import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import Search from './pages/Search';
import Recommendations from './pages/Recommendations';
import History from './pages/History';
import Admin from './pages/Admin';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" />;
};

// Landing Page Component
const Home = () => {
  const token = localStorage.getItem('token');
  
  if (token) {
    return <Navigate to="/search" />;
  }

  return (
    <div className="home-page">
      <div className="home-container">
        <div className="home-hero">
          <h1 className="home-title">
            <span className="gradient-text">ML Resource Discovery</span>
          </h1>
          <p className="home-subtitle">
            Your intelligent platform for discovering machine learning resources
          </p>
          <div className="home-features">
            <div className="feature-card">
              <span className="feature-icon">🔍</span>
              <h3>Smart Search</h3>
              <p>Find ML resources using advanced TF-IDF search algorithms</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">⭐</span>
              <h3>Personalized</h3>
              <p>Get recommendations tailored to your interests and preferences</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">📊</span>
              <h3>Ranked Results</h3>
              <p>Resources ranked by relevance and popularity using PageRank</p>
            </div>
          </div>
          <div className="home-cta">
            <a href="/register" className="btn btn-primary btn-large">
              Get Started
            </a>
            <a href="/login" className="btn btn-secondary btn-large">
              Sign In
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/search"
              element={
                <ProtectedRoute>
                  <Search />
                </ProtectedRoute>
              }
            />
            <Route
              path="/recommendations"
              element={
                <ProtectedRoute>
                  <Recommendations />
                </ProtectedRoute>
              }
            />
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <History />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute>
                  <Admin />
                </ProtectedRoute>
              }
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;