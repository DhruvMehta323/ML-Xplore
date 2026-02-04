import React, { useState } from 'react';
import { searchAPI, historyAPI } from '../api';
import ResourceCard from '../components/ResourceCard';
import './Search.css';

const TAG_OPTIONS = [
  'dataset',
  'model',
  'article',
  'research paper',
  'documentation',
  'code',
];

const Search = () => {
  const [query, setQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setError('');
    setLoading(true);
    setSearched(true);

    try {
      const response = await searchAPI.search(query, selectedTags);
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTagToggle = (tag) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
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
    <div className="search-page">
      <div className="search-container">
        <div className="search-hero">
          <h1 className="search-title gradient-text">Discover ML Resources</h1>
          <p className="search-subtitle">
            Search through thousands of curated machine learning resources
          </p>
        </div>

        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-wrapper">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              className="search-input"
              placeholder="Search for datasets, models, papers, tutorials..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? <span className="loading"></span> : 'Search'}
            </button>
          </div>

          <div className="tag-filter">
            <span className="filter-label">Filter by type:</span>
            <div className="tag-options">
              {TAG_OPTIONS.map(tag => (
                <button
                  key={tag}
                  type="button"
                  className={`tag-option ${selectedTags.includes(tag) ? 'active' : ''}`}
                  onClick={() => handleTagToggle(tag)}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </form>

        {error && <div className="error-message">{error}</div>}

        {loading && (
          <div className="loading-state">
            <div className="loading"></div>
            <p>Searching resources...</p>
          </div>
        )}

        {!loading && searched && results.length === 0 && (
          <div className="empty-state">
            <span className="empty-icon">🔍</span>
            <h3>No results found</h3>
            <p>Try adjusting your search query or filters</p>
          </div>
        )}

        {!loading && results.length > 0 && (
          <div className="results-section">
            <div className="results-header">
              <h2>Found {results.length} resources</h2>
            </div>
            <div className="results-grid">
              {results.map((resource, index) => (
                <ResourceCard
                  key={index}
                  resource={resource}
                  onClick={() => handleResourceClick(resource)}
                />
              ))}
            </div>
          </div>
        )}

        {!searched && (
          <div className="search-tips">
            <h3>💡 Search Tips</h3>
            <ul>
              <li>Use specific keywords like "neural networks" or "computer vision"</li>
              <li>Filter by resource type to narrow your results</li>
              <li>Try different combinations of keywords</li>
              <li>Click on any result to visit and it will be added to your history</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default Search;