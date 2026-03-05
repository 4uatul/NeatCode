import React, { useState } from 'react';
import emailjs from '@emailjs/browser';
import './styles/App.css';

// Replace these with your keys from emailjs.com
const EMAILJS_SERVICE_ID  = 'service_g8ufu3q';
const EMAILJS_TEMPLATE_ID = 'template_5dldl2f';
const EMAILJS_PUBLIC_KEY  = 'tZTiMy7Y4TE_oNjMa';

const Navbar = () => (
  <nav className="navbar">
    <div className="navbar-brand">
      <div className="navbar-logo">
        <i className="fas fa-code"></i>
      </div>
      <span className="navbar-title">Neat<span>Code</span></span>
    </div>
    <span className="navbar-badge">Powered by Gemini AI</span>
  </nav>
);

const HowItWorks = ({ activeStep }) => (
  <div className="how-it-works">
    {[
      { n: 1, label: 'Paste or upload code' },
      { n: 2, label: 'Gemini AI refactors it' },
      { n: 3, label: 'Get clean, readable code' },
    ].map(({ n, label }, i, arr) => (
      <React.Fragment key={n}>
        <div className={`step ${activeStep >= n ? 'step-active' : ''} ${activeStep === n ? 'step-current' : ''}`}>
          <div className="step-number">
            {activeStep > n ? <i className="fas fa-check"></i> : n}
          </div>
          <div className="step-label">{label}</div>
        </div>
        {i < arr.length - 1 && (
          <div className={`step-connector ${activeStep > n ? 'connector-active' : ''}`} />
        )}
      </React.Fragment>
    ))}
  </div>
);

const sampleCode = `# bad code lol
def c(l):
 t=0
 for i in range(len(l)):
  t=t+l[i]
 return t

def   chk(x,y,z):
 if x>0:
  if y>0:
   if z>0:
    return True
   else:
    return False
  else:
   return False
 else:
  return False

MyList=[5,3,8,1,9,2]
TOTAL=c(MyList)
print("total is"+str(TOTAL))
avg=TOTAL/len(MyList)
print("avg is"+str(avg))`;

const LANGUAGE_MAP = {
  js: 'javascript', py: 'python', java: 'java', cpp: 'cpp',
  c: 'cpp', cs: 'csharp', php: 'php', html: 'html',
  css: 'css', sql: 'sql', rb: 'ruby', swift: 'swift',
};

function FeedbackBox() {
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');
  const [status, setStatus] = useState('idle'); // idle | sending | sent | error

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    setStatus('sending');

    emailjs.send(
      EMAILJS_SERVICE_ID,
      EMAILJS_TEMPLATE_ID,
      { from_name: name || 'Anonymous', message },
      EMAILJS_PUBLIC_KEY
    ).then(() => {
      setStatus('sent');
      setName('');
      setMessage('');
    }).catch(() => setStatus('error'));
  };

  return (
    <section className="feedback-section">
      <div className="feedback-inner">
        <div className="feedback-header">
          <i className="fas fa-comment-dots"></i>
          <div>
            <h3>Share your feedback</h3>
            <p>Help us improve NeatCode</p>
          </div>
        </div>

        {status === 'sent' ? (
          <div className="feedback-success">
            <i className="fas fa-circle-check"></i>
            <span>Thanks! Your feedback was sent.</span>
          </div>
        ) : (
          <form className="feedback-form" onSubmit={handleSubmit}>
            <input
              className="feedback-input"
              type="text"
              placeholder="Your name (optional)"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <textarea
              className="feedback-textarea"
              placeholder="What do you think? Bugs, ideas, complaints..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              required
              rows={3}
            />
            {status === 'error' && (
              <p className="feedback-error">Failed to send. Please try again.</p>
            )}
            <button className="btn btn-primary feedback-submit" type="submit" disabled={status === 'sending'}>
              {status === 'sending'
                ? <><i className="fas fa-spinner spinner"></i> Sending…</>
                : <><i className="fas fa-paper-plane"></i> Send Feedback</>}
            </button>
          </form>
        )}
      </div>
    </section>
  );
}

function App() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('auto');
  const [fileName, setFileName] = useState('');
  const [refactoredCode, setRefactoredCode] = useState('');
  const [projectSummary, setProjectSummary] = useState('');
  const [keyChanges, setKeyChanges] = useState([]);
  const [isRefactoring, setIsRefactoring] = useState(false);
  const [showOutput, setShowOutput] = useState(false);
  const [copied, setCopied] = useState(false);
  const [guardMessage, setGuardMessage] = useState('');

  const handleTryMe = () => {
    setCode(sampleCode);
    setLanguage('python');
  };

  const handleRefactor = async () => {
    if (!code.trim()) {
      alert('Please enter or upload some code to refactor.');
      return;
    }

    setIsRefactoring(true);
    try {
      const response = await fetch('http://localhost:5000/api/refactor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code.trim() }),
      });

      const data = await response.json();

      if (data.notCode) {
        setGuardMessage(data.message);
        setShowOutput(false);
        return;
      }

      if (!response.ok || data.error) throw new Error(data.error + (data.details ? ': ' + data.details : ''));

      setGuardMessage('');
      setRefactoredCode(data.refactoredCode || 'No refactored code returned');
      setProjectSummary(data.projectSummary || '');
      setKeyChanges(data.keyChanges || []);
      setShowOutput(true);
    } catch (error) {
      alert(`Failed to refactor: ${error.message}\n\nMake sure the backend is running on http://localhost:5000`);
    } finally {
      setIsRefactoring(false);
    }
  };

  const copyToClipboard = () => {
    if (!refactoredCode.trim()) return;
    navigator.clipboard.writeText(refactoredCode).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setFileName(file.name);
    const ext = file.name.split('.').pop().toLowerCase();
    if (LANGUAGE_MAP[ext]) setLanguage(LANGUAGE_MAP[ext]);
    const reader = new FileReader();
    reader.onload = (ev) => setCode(ev.target.result);
    reader.readAsText(file);
  };

  return (
    <div className="app-container">
      <Navbar />

      <section className="hero">
        <div className="hero-eyebrow">
          <i className="fas fa-sparkles"></i>
          AI-Powered Refactoring
        </div>
        <h1>Write <span className="gradient-text">cleaner code</span>,<br />effortlessly.</h1>
        <p>Paste your messy code and let Gemini AI transform it into clean, readable, production-ready code.</p>
      </section>

      <HowItWorks activeStep={showOutput ? 3 : isRefactoring ? 2 : code.trim() ? 1 : 0} />

      <main className="workspace">
        {/* ── Input Panel ── */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <div className="panel-dots">
                <div className="panel-dot red"></div>
                <div className="panel-dot yellow"></div>
                <div className="panel-dot green"></div>
              </div>
              <i className="fas fa-code"></i>
              Input Code
            </div>
            <div className="panel-actions">
              <select
                className="lang-select"
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
              <button className="btn-try" onClick={handleTryMe}>
                <i className="fas fa-play"></i>
                Try Sample
              </button>
            </div>
          </div>

          <div className="code-editor-wrap">
            <textarea
              className="code-textarea"
              placeholder="// Paste your code here..."
              value={code}
              onChange={(e) => setCode(e.target.value)}
              spellCheck={false}
            />
          </div>

          <div className="panel-footer">
            <div className="file-upload-area">
              <label htmlFor="file-input" className="file-upload-btn">
                <i className="fas fa-folder-open"></i>
                Open File
              </label>
              <input
                type="file"
                id="file-input"
                className="file-input"
                accept=".txt,.js,.py,.java,.cpp,.c,.cs,.php,.html,.css,.json,.xml,.rb,.swift"
                onChange={handleFileChange}
              />
              {fileName && <span className="file-name-text">{fileName}</span>}
            </div>

            <button
              className="btn btn-primary"
              onClick={handleRefactor}
              disabled={isRefactoring}
            >
              {isRefactoring ? (
                <><i className="fas fa-spinner spinner"></i> Refactoring…</>
              ) : (
                <><i className="fas fa-magic"></i> Refactor Code</>
              )}
            </button>
          </div>
        </div>

        {/* ── Output Panel ── */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <div className="panel-dots">
                <div className="panel-dot red"></div>
                <div className="panel-dot yellow"></div>
                <div className="panel-dot green"></div>
              </div>
              <i className="fas fa-check-circle"></i>
              Refactored Output
            </div>
            {showOutput && (
              <button className="btn btn-ghost" onClick={copyToClipboard}>
                <i className={copied ? 'fas fa-check' : 'far fa-copy'}></i>
                {copied ? 'Copied!' : 'Copy'}
              </button>
            )}
          </div>

          {guardMessage ? (
            <div className="guard-message">
              <div className="guard-icon"><i className="fas fa-triangle-exclamation"></i></div>
              <p className="guard-title">Not a code input</p>
              <p className="guard-body">{guardMessage}</p>
            </div>
          ) : showOutput ? (
            <div className="output-content">
              {projectSummary && (
                <div className="summary-banner">
                  <i className="fas fa-info-circle"></i>
                  <p>{projectSummary}</p>
                </div>
              )}

              <div className="code-output">{refactoredCode}</div>

              {keyChanges.length > 0 && (
                <div className="key-changes">
                  <div className="key-changes-title">
                    <i className="fas fa-list-ul"></i>
                    Key Changes
                  </div>
                  {keyChanges.map((item, i) => (
                    <div className="change-item" key={i}>
                      <div className="change-dot"></div>
                      <div className="change-body">
                        <strong>{item.change}</strong>
                        <p>{item.reason}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="output-placeholder">
              <div className="placeholder-icon">
                <i className="fas fa-wand-magic-sparkles"></i>
              </div>
              <p>Refactored code will appear here</p>
              <span className="hint">Click "Refactor Code" to get started</span>
            </div>
          )}
        </div>
      </main>

      <FeedbackBox />

      <footer className="app-footer">
        NeatCode &copy; 2026 &mdash; AI-powered code refactoring
      </footer>
    </div>
  );
}

export default App;
