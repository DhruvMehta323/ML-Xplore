import React, { useState, useEffect } from 'react';
import { historyAPI } from '../api';
import ResourceCard from '../components/ResourceCard';
import './History.css';

const History = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await historyAPI.get();
      setHistory(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const handleResourceClick = (resource) => {
    window.open(resource.url, '_blank');
  };

  return (
    <div className="history-page">
      <div className="history-container">
        <div className="history-hero">
          <h1 className="history-title gradient-text">Your History</h1>
          <p className="history-subtitle">
            Resources you've recently explored
          </p>
        </div>

        {error && <div className="error-message">{error}</div>}

        {loading && (
          <div className="loading-state">
            <div className="loading"></div>
            <p>Loading your history...</p>
          </div>
        )}

        {!loading && history.length === 0 && (
          <div className="empty-state">
            <span className="empty-icon">📚</span>
            <h3>No history yet</h3>
            <p>Start searching and clicking on resources to build your history</p>
          </div>
        )}

        {!loading && history.length > 0 && (
          <div className="history-section">
            <div className="history-header">
              <h2>{history.length} Recent Resources</h2>
              <button className="btn btn-secondary" onClick={fetchHistory}>
                <span>🔄</span> Refresh
              </button>
            </div>
            <div className="history-timeline">
              {history.map((item, index) => (
                <div key={index} className="history-item">
                  <div className="history-marker"></div>
                  <div className="history-content">
                    <ResourceCard
                      resource={item}
                      onClick={() => handleResourceClick(item)}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="history-info">
          <h3>💡 About Your History</h3>
          <p>
            Your browsing history helps us understand your interests and provide better recommendations. 
            Every resource you click on is automatically added to your history.
          </p>
        </div>
      </div>
    </div>
  );
};

export default History;