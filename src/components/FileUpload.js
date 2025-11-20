import React from 'react';

const FileUpload = ({ fileName, setFileName, setCode, setLanguage }) => {
  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      const file = e.target.files[0];
      setFileName(file.name);
      
      const extension = file.name.split('.').pop().toLowerCase();
      detectLanguageFromExtension(extension);
      
      const reader = new FileReader();
      reader.onload = (e) => {
        setCode(e.target.result);
      };
      reader.readAsText(file);
    } else {
      setFileName('No file selected');
    }
  };

  const detectLanguageFromExtension = (ext) => {
    const languageMap = {
      'js': 'javascript',
      'py': 'python',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'cpp',
      'cs': 'csharp',
      'php': 'php',
      'html': 'html',
      'css': 'css',
      'sql': 'sql',
      'rb': 'ruby',
      'swift': 'swift'
    };
    
    if (languageMap[ext]) {
      setLanguage(languageMap[ext]);
    }
  };

  return (
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
  );
};

export default FileUpload;