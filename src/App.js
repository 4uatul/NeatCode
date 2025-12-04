import React, { useState } from 'react';
import './styles/App.css';

const Header = () => {
  return (
    <header className="main-header">
      <h1>NeatCode - Code Refactor Tool</h1>
      <p className="subtitle">AI-powered code refactoring for cleaner, better code</p>
    </header>
  );
};

const HowItWorksSection = () => {
  return (
    <section className="how-it-works">
      <h3><i className="fas fa-info-circle"></i> How It Works?</h3>
      <div className="steps-container">
        <div className="step-card">
          <p>Paste messy code or drop a file</p>
        </div>
        <div className="step-arrow">→</div>
        <div className="step-card">
          <p>Gemini AI refactors it instantly</p>
        </div>
        <div className="step-arrow">→</div>
        <div className="step-card">
          <p>Get cleaner, readable code</p>
        </div>
      </div>
      <p className="cta-text">New here? Click "Try Me - Load Sample Code" to see the magic happen!</p>
    </section>
  );
};

function App() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('auto');
  const [fileName, setFileName] = useState('No file selected');
  const [refactoredCode, setRefactoredCode] = useState('');
  const [projectSummary, setProjectSummary] = useState('');
  const [keyChanges, setKeyChanges] = useState([]);
  const [isRefactoring, setIsRefactoring] = useState(false);
  const [showOutput, setShowOutput] = useState(false);

  const sampleCode = `// Bad code example - needs refactoring!
function calc(x) {
    var t = 0;
    var i = 0;
    while (i < x.length) {
        if (x[i].p) {
            t = t + x[i].p;
        }
        i = i + 1;
    }
    return t;
}

function d(amt) {
    var disc = 0;
    if (amt > 100) {
        disc = amt * 0.2;
    } else if (amt > 50) {
        disc = amt * 0.1;
    } else {
        disc = 0;
    }
    return disc;
}

var stuff = [
    {n: 'laptop', p: 999.99, q: 1},
    {n: 'mouse', p: 25.50, q: 2},
    {n: 'keyboard', p: 75.00, q: 1}
];

var x = calc(stuff);
var y = d(x);
var z = x - y;

console.log('Total: ' + x);
console.log('Discount: ' + y);
console.log('Final: ' + z);`;

  const handleTryMe = () => {
    setCode(sampleCode);
    setLanguage('javascript');
  };

  const handleRefactor = async () => {
    const trimmedCode = code.trim();

    if (trimmedCode === '') {
      alert('Please enter or upload some code to refactor.');
      return;
    }

    setIsRefactoring(true);

    try {
      const response = await fetch('http://localhost:5000/api/refactor', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: trimmedCode })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error + (data.details ? ': ' + data.details : ''));
      }

      setRefactoredCode(data.refactoredCode || 'No refactored code returned');
      setProjectSummary(data.projectSummary || '');
      setKeyChanges(data.keyChanges || []);
      setShowOutput(true);
    } catch (error) {
      console.error('Error refactoring code:', error);
      alert(`Failed to refactor code: ${error.message}\n\nMake sure the backend server is running on http://localhost:5000`);
    } finally {
      setIsRefactoring(false);
    }
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
    <div className="app-container">
      <Header />
      <HowItWorksSection />

      <div className="split-layout">
        {/* Left Panel - Input */}
        <div className="left-panel">
          <div className="panel-header">
            <h2><i className="fas fa-code"></i> Input Code</h2>
            <button className="try-me-btn" onClick={handleTryMe}>
              <i className="fas fa-play"></i>
              Try Me - Load Sample Code
            </button>
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
              Upload File
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

        {/* Right Panel - Output */}
        <div className="right-panel">
          <div className="panel-header">
            <h2><i className="fas fa-check-circle"></i> Refactored Code</h2>
            {showOutput && (
              <button className="copy-btn" onClick={copyToClipboard}>
                <i className="far fa-copy"></i>
                Copy
              </button>
            )}
          </div>

          {showOutput ? (
            <div className="output-container">
              {projectSummary && (
                <div className="project-summary">
                  <h3><i className="fas fa-info-circle"></i> Project Summary</h3>
                  <p>{projectSummary}</p>
                </div>
              )}

              <div className="code-output">{refactoredCode}</div>

              {keyChanges && keyChanges.length > 0 && (
                <div className="key-changes">
                  <h3><i className="fas fa-list-ul"></i> Key Changes</h3>
                  <ul>
                    {keyChanges.map((item, index) => (
                      <li key={index}>
                        <strong>{item.change}</strong>
                        <p>{item.reason}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="code-placeholder">
              <i className="fas fa-arrow-left"></i>
              <p>Refactored code will appear here</p>
              <p className="hint">Click "Refactor Code" to see the magic!</p>
            </div>
          )}
        </div>
      </div>

      <footer>
        <p>NeatCode &copy; 2025 | AI-powered code refactoring</p>
      </footer>
    </div>
  );
}

export default App;