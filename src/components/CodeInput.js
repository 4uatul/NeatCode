import React from 'react';

const CodeInput = ({ code, setCode, language, setLanguage }) => {
  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  const handleCodeChange = (e) => {
    setCode(e.target.value);
  };

  return (
    <div className="input-section">
      <div className="input-header">
        <h2>Input Code</h2>
        <div className="language-selector">
          <label htmlFor="language-select"><i className="fas fa-code"></i> Language:</label>
          <select 
            id="language-select" 
            value={language} 
            onChange={handleLanguageChange}
          >
            <option value="auto">Auto-detect</option>
            <option value="javascript">JavaScript</option>
            <option value="python">Python</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
            <option value="csharp">C#</option>
            <option value="php">PHP</option>
            <option value="html">HTML</option>
            <option value="css">CSS</option>
            <option value="sql">SQL</option>
            <option value="ruby">Ruby</option>
            <option value="swift">Swift</option>
          </select>
        </div>
      </div>
      
      <textarea 
        className="code-input" 
        placeholder="Paste your code here..."
        value={code}
        onChange={handleCodeChange}
      />
    </div>
  );
};

export default CodeInput;