import React, { useState, useEffect } from 'react';
import { adminAPI } from '../api';
import './Admin.css';

const Admin = () => {
  const [stats, setStats] = useState(null);
  const [resources, setResources] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('stats');

  useEffect(() => {
    fetchStats();
  }, []);

  useEffect(() => {
    if (activeTab === 'resources') {
      fetchResources();
    }
  }, [activeTab, page]);

  const fetchStats = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await adminAPI.getStats();
      setStats(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  const fetchResources = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await adminAPI.getResources(page, 20);
      setResources(response.data.resources);
      setTotalPages(response.data.total_pages);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load resources');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-page">
      <div className="admin-container">
        <div className="admin-hero">
          <h1 className="admin-title gradient-text">Admin Dashboard</h1>
          <p className="admin-subtitle">
            System statistics and resource management
          </p>
        </div>

        <div className="admin-tabs">
          <button
            className={`tab-btn ${activeTab === 'stats' ? 'active' : ''}`}
            onClick={() => setActiveTab('stats')}
          >
            📊 Statistics
          </button>
          <button
            className={`tab-btn ${activeTab === 'resources' ? 'active' : ''}`}
            onClick={() => setActiveTab('resources')}
          >
            📚 Resources
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {activeTab === 'stats' && (
          <div className="stats-section">
            {loading ? (
              <div className="loading-state">
                <div className="loading"></div>
                <p>Loading statistics...</p>
              </div>
            ) : stats ? (
              <>
                <div className="stats-grid">
                  <div className="stat-card">
                    <span className="stat-icon">📑</span>
                    <h3 className="stat-value">{stats.total_resources.toLocaleString()}</h3>
                    <p className="stat-label">Total Resources</p>
                  </div>
                  <div className="stat-card">
                    <span className="stat-icon">🔗</span>
                    <h3 className="stat-value">{stats.total_links.toLocaleString()}</h3>
                    <p className="stat-label">Total Links</p>
                  </div>
                  <div className="stat-card">
                    <span className="stat-icon">👥</span>
                    <h3 className="stat-value">{stats.total_users.toLocaleString()}</h3>
                    <p className="stat-label">Total Users</p>
                  </div>
                  <div className="stat-card">
                    <span className="stat-icon">👆</span>
                    <h3 className="stat-value">{stats.total_interactions.toLocaleString()}</h3>
                    <p className="stat-label">Total Interactions</p>
                  </div>
                </div>

                {stats.tag_distribution && stats.tag_distribution.length > 0 && (
                  <div className="tag-distribution">
                    <h3>Top Resource Categories</h3>
                    <div className="distribution-bars">
                      {stats.tag_distribution.map((item, index) => {
                        const maxCount = Math.max(...stats.tag_distribution.map(i => i.count));
                        const percentage = (item.count / maxCount) * 100;
                        return (
                          <div key={index} className="distribution-item">
                            <div className="distribution-label">
                              <span className="tag">{item.tag || 'general'}</span>
                              <span className="distribution-count">{item.count}</span>
                            </div>
                            <div className="distribution-bar">
                              <div 
                                className="distribution-fill" 
                                style={{ width: `${percentage}%` }}
                              ></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </>
            ) : null}
          </div>
        )}

        {activeTab === 'resources' && (
          <div className="resources-section">
            {loading ? (
              <div className="loading-state">
                <div className="loading"></div>
                <p>Loading resources...</p>
              </div>
            ) : (
              <>
                <div className="resources-table-container">
                  <table className="resources-table">
                    <thead>
                      <tr>
                        <th>Title</th>
                        <th>Tags</th>
                        <th>Popularity</th>
                        <th>Last Crawled</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resources.map((resource, index) => (
                        <tr key={index}>
                          <td className="title-cell">
                            <div className="title-wrapper">
                              <span className="resource-title-text">
                                {resource.title || 'Untitled'}
                              </span>
                              <span className="resource-url">{resource.url}</span>
                            </div>
                          </td>
                          <td>
                            <div className="table-tags">
                              {resource.tags && resource.tags.split(',').slice(0, 2).map((tag, i) => (
                                <span key={i} className="tag">{tag.trim()}</span>
                              ))}
                            </div>
                          </td>
                          <td>{resource.popularity_score?.toFixed(2) || '0.00'}</td>
                          <td>{new Date(resource.last_crawled).toLocaleDateString()}</td>
                          <td>
                            <a
                              href={resource.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="view-link"
                            >
                              View →
                            </a>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {totalPages > 1 && (
                  <div className="pagination">
                    <button
                      className="btn btn-secondary"
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      ← Previous
                    </button>
                    <span className="page-info">
                      Page {page} of {totalPages}
                    </span>
                    <button
                      className="btn btn-secondary"
                      onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                    >
                      Next →
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Admin;