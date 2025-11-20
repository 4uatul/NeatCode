import React, { useState } from 'react';
import './styles/App.css';

// Simple inline components to avoid import issues
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

const Header = () => {
  return (
    <header>
      <h1>NeatCode - Code Refactor Tool</h1>
      <p className="subtitle">Paste your code or upload a file to refactor</p>
    </header>
  );
};

function App() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('auto');
  const [fileName, setFileName] = useState('No file selected');
  const [refactoredCode, setRefactoredCode] = useState('');
  const [isRefactoring, setIsRefactoring] = useState(false);
  const [showOutput, setShowOutput] = useState(false);

  const sampleCode = `function calculateTotal(items) {
    var total = 0;
    for (var i = 0; i < items.length; i++) {
        total = total + items[i].price;
    }
    return total;
}

var items = [
    {name: 'Apple', price: 1.50},
    {name: 'Banana', price: 0.75},
    {name: 'Orange', price: 2.00}
];

console.log('Total: $' + calculateTotal(items));`;

  const handleTryMe = () => {
    setCode(sampleCode);
    setLanguage('javascript');
  };

  const handleRefactor = () => {
    const trimmedCode = code.trim();
    
    if (trimmedCode === '') {
      alert('Please enter or upload some code to refactor.');
      return;
    }
    
    setIsRefactoring(true);
    
    setTimeout(() => {
      const languageName = language === 'auto' ? 'auto-detected' : language;
      const result = `// Refactored code (${languageName})
// This is a simulation - a real tool would provide actual refactoring

${code}

// Refactoring completed
// Code has been optimized for readability and maintainability`;
      
      setRefactoredCode(result);
      setShowOutput(true);
      setIsRefactoring(false);
    }, 1500);
  };

  const copyToClipboard = () => {
    const textToCopy = refactoredCode;
    
    if (textToCopy.trim() === '') {
      alert('No code to copy!');
      return;
    }
    
    navigator.clipboard.writeText(textToCopy)
      .then(() => {
        alert('Code copied to clipboard!');
      })
      .catch(err => {
        console.error('Failed to copy: ', err);
        alert('Failed to copy code to clipboard');
      });
  };

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      const file = e.target.files[0];
      setFileName(file.name);
      
      const extension = file.name.split('.').pop().toLowerCase();
      const languageMap = {
        'js': 'javascript', 'py': 'python', 'java': 'java', 'cpp': 'cpp',
        'c': 'cpp', 'cs': 'csharp', 'php': 'php', 'html': 'html',
        'css': 'css', 'sql': 'sql', 'rb': 'ruby', 'swift': 'swift'
      };
      
      if (languageMap[extension]) {
        setLanguage(languageMap[extension]);
      }
      
      const reader = new FileReader();
      reader.onload = (e) => {
        setCode(e.target.result);
      };
      reader.readAsText(file);
    } else {
      setFileName('No file selected');
    }
  };

  return (
    <div className="layout">
      <ExplanationPanel />
      
      <div className="container">
        <Header />
        
        <div className="main-content">
          <div className="try-me-section">
            <p><i className="fas fa-lightbulb"></i> <strong>Try it out:</strong> Click the button below to load a sample JavaScript code</p>
            <button className="try-me-btn" onClick={handleTryMe}>
              <i className="fas fa-play"></i>
              Try Me - Load Sample Code
            </button>
          </div>
          
          <div className="input-section">
            <div className="input-header">
              <h2>Input Code</h2>
              <div className="language-selector">
                <label htmlFor="language-select"><i className="fas fa-code"></i> Language:</label>
                <select 
                  id="language-select" 
                  value={language} 
                  onChange={(e) => setLanguage(e.target.value)}
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
              onChange={(e) => setCode(e.target.value)}
            />
            
            <div className="file-upload">
              <label htmlFor="file-input" className="file-label">
                <i className="fas fa-file-upload"></i>
                Upload Code File
              </label>
              <input 
                type="file" 
                id="file-input" 
                className="file-input" 
                accept=".txt,.js,.py,.java,.cpp,.c,.cs,.php,.html,.css,.json,.xml,.rb,.swift"
                onChange={handleFileChange}
              />
              <span className="file-name">{fileName}</span>
            </div>
          </div>
          
          <div className="actions">
            <button 
              className="refactor-btn" 
              onClick={handleRefactor}
              disabled={isRefactoring}
            >
              {isRefactoring ? (
                <>
                  <i className="fas fa-spinner spinner"></i>
                  Refactoring...
                </>
              ) : (
                <>
                  <i className="fas fa-magic"></i>
                  Refactor Code
                </>
              )}
            </button>
          </div>

          {showOutput && (
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
          )}
        </div>
        
        <footer>
          <p>NeatCode - Code Refactor Tool &copy; 2025 | Clean, efficient, and beautiful code refactoring</p>
        </footer>
      </div>
    </div>
  );
}

export default App;