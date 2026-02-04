import React, { useState, useEffect } from 'react';
import { recommendationsAPI, historyAPI } from '../api';
import ResourceCard from '../components/ResourceCard';
import './Recommendations.css';

const Recommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await recommendationsAPI.get();
      setRecommendations(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  const handleResourceClick = async (resource) => {
    try {
      await historyAPI.add(resource.url);
      window.open(resource.url, '_blank');
    } catch (err) {
      console.error('Failed to add to history:', err);
    }
  };

  return (
    <div className="recommendations-page">
      <div className="recommendations-container">
        <div className="recommendations-hero">
          <h1 className="recommendations-title gradient-text">
            Personalized for You
          </h1>
          <p className="recommendations-subtitle">
            Resources tailored to your interests and preferences
          </p>
          {user.preferences && (
            <div className="user-preferences">
              <span className="preferences-label">Your interests:</span>
              <div className="preferences-tags">
                {user.preferences.split(',').map((pref, index) => (
                  <span key={index} className="tag">{pref}</span>
                ))}
              </div>
            </div>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}

        {loading && (
          <div className="loading-state">
            <div className="loading"></div>
            <p>Loading your recommendations...</p>
          </div>
        )}

        {!loading && recommendations.length === 0 && (
          <div className="empty-state">
            <span className="empty-icon">⭐</span>
            <h3>No recommendations yet</h3>
            <p>Start searching and interacting with resources to get personalized recommendations</p>
          </div>
        )}

        {!loading && recommendations.length > 0 && (
          <div className="recommendations-section">
            <div className="recommendations-header">
              <h2>Top {recommendations.length} Recommendations</h2>
              <button className="btn btn-secondary" onClick={fetchRecommendations}>
                <span>🔄</span> Refresh
              </button>
            </div>
            <div className="recommendations-grid">
              {recommendations.map((resource, index) => (
                <ResourceCard
                  key={index}
                  resource={resource}
                  onClick={() => handleResourceClick(resource)}
                />
              ))}
            </div>
          </div>
        )}

        <div className="recommendations-info">
          <h3>How Recommendations Work</h3>
          <div className="info-grid">
            <div className="info-card">
              <span className="info-icon">🎯</span>
              <h4>Preference Matching</h4>
              <p>We match resources with your selected interests and preferences</p>
            </div>
            <div className="info-card">
              <span className="info-icon">🔥</span>
              <h4>Popularity Scoring</h4>
              <p>Resources are ranked based on their popularity and relevance</p>
            </div>
            <div className="info-card">
              <span className="info-icon">📊</span>
              <h4>Smart Algorithm</h4>
              <p>Our algorithm combines multiple factors to find the best matches</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Recommendations;