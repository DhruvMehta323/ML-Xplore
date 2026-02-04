import React from 'react';
import './ResourceCard.css';

const ResourceCard = ({ resource, onClick }) => {
  const getTags = () => {
    if (!resource.tags) return [];
    return resource.tags.split(',').map(tag => tag.trim()).filter(Boolean);
  };

  const getScoreColor = (score) => {
    if (score >= 0.7) return 'high';
    if (score >= 0.4) return 'medium';
    return 'low';
  };

  return (
    <div className="resource-card card" onClick={onClick}>
      <div className="resource-header">
        <h3 className="resource-title">{resource.title || 'Untitled Resource'}</h3>
        {resource.score !== undefined && (
          <span className={`score-badge ${getScoreColor(resource.score)}`}>
            {(resource.score * 100).toFixed(0)}%
          </span>
        )}
      </div>

      {resource.description && (
        <p className="resource-description">{resource.description}</p>
      )}

      <div className="resource-footer">
        <div className="resource-tags">
          {getTags().map((tag, index) => (
            <span key={index} className="tag">{tag}</span>
          ))}
        </div>
        
        <a 
          href={resource.url} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="resource-link"
          onClick={(e) => e.stopPropagation()}
        >
          Visit →
        </a>
      </div>

      {resource.popularity_score !== undefined && (
        <div className="resource-meta">
          <span className="meta-item">
            🔥 Popularity: {resource.popularity_score.toFixed(2)}
          </span>
        </div>
      )}

      {resource.timestamp && (
        <div className="resource-meta">
          <span className="meta-item">
            🕒 {new Date(resource.timestamp).toLocaleDateString()}
          </span>
        </div>
      )}
    </div>
  );
};

export default ResourceCard;