import React from 'react';

const ExplanationPanel = () => {
  return (
    <aside className="explanation-panel">
      <h3><i className="fas fa-info-circle"></i> How It Works</h3>
      
      <div className="explanation-section">
        <h4>1. Code Analysis</h4>
        <p>Our tool analyzes your code to identify patterns, inefficiencies, and areas for improvement.</p>
      </div>
      
      <div className="explanation-section">
        <h4>2. Smart Refactoring</h4>
        <p>Applies best practices and modern coding standards to optimize your code structure.</p>
      </div>
      
      <div className="explanation-section">
        <h4>3. Quality Check</h4>
        <p>Validates the refactored code to ensure it maintains functionality while improving readability.</p>
      </div>
      
      <div className="explanation-section">
        <h4>4. Get Results</h4>
        <p>Review your improved code with better naming, structure, and documentation.</p>
      </div>
    </aside>
  );
};

export default ExplanationPanel;