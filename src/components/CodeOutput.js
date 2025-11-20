import React from 'react';

const CodeOutput = ({ refactoredCode, copyToClipboard }) => {
  return (
    <div className="output-section">
      <div className="output-header">
        <h2>Refactored Code</h2>
        <button className="copy-btn" onClick={copyToClipboard}>
          <i className="far fa-copy"></i>
          Copy to Clipboard
        </button>
      </div>
      <div className="code-output">{refactoredCode}</div>
    </div>
  );
};

export default CodeOutput;