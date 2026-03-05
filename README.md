# AI Code Refactoring Assistant

An intelligent web application that uses AI to automatically refactor and improve source code.

## Team Members

- Atul
- Saif
- Arun

## Project Overview

This application helps developers improve their code by using AI to refactor it. Users can paste code or upload files, and receive a cleaner, more maintainable version along with explanations of the changes.

This is a team project following Agile methodology for a software engineering course.

## Features

- Text input for code submission
- File upload capability
- AI-powered code refactoring using Google Gemini API
- Side-by-side comparison of original and refactored code
- Explanation of changes made

## Technology Stack

**Frontend:**
- HTML, CSS, JavaScript

**Backend:**
- Python
- Flask

**AI:**
- Google Gemini API

## Project Structure
```
code-refactoring-app/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── .env
│   └── venv/
├── frontend/
│   └── index.html
└── uploads/
```

## Installation

### Prerequisites
- Python 3.8+
- Git
- Google Gemini API key

### Setup Steps

1. Clone the repository
```bash
git clone https://github.com/your-username/code-refactoring-app.git
cd code-refactoring-app
```

2. Set up backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create .env file in backend folder
```
GEMINI_API_KEY=your_api_key_here
PORT=5000
```

4. Run the application
```bash
python app.py
```

5. Open frontend/index.html in your browser

## Usage

1. Open the application in your browser
2. Paste your code or upload a file
3. Click "Refactor Code"
4. View the improved code and explanation

## Development Timeline

- **Sprint 1 (Weeks 3-4):** Basic UI and backend setup
- **Sprint 2 (Weeks 5-7):** AI integration
- **Sprint 3 (Weeks 8-9):** Polish and explanations
- **Sprint 4 (Weeks 10-11):** Testing and final demo

## Current Status

Currently in active development. Core features are functional but undergoing testing and refinement.

## Contributing

This is a class project. Team members should:
1. Create a feature branch for new work
2. Commit changes regularly with clear messages
3. Test before pushing to main branch

## Notes

- Keep your API key secure - never commit .env file
- Supported file types: .txt,.js,.py,.java,.cpp,.c,.cs,.php,.html,.css,.json,.xml,.rb,.swift

## License

This project is for educational purposes as part of a software engineering course.



Starting the Application
1. Backend (Flask API)
Navigate to the Backend directory and run:


cd Backend
python -m pip install -r requirements.txt
python app.py
The backend will start on http://0.0.0.0:5000 (accessible at http://localhost:5000)

2. Frontend (React App)
In a separate terminal, from the root directory run:


npm install
npm start
The React app will start on http://localhost:3000

What This Application Does
This is a code refactoring tool that:

Takes code input (via text or file upload)
Uses Google's Gemini AI to analyze and refactor the code
Returns improved code with explanations of changes
Supports multiple programming languages (JS, Python, Java, C++, etc.)