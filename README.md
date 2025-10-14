# AI Code Refactoring Assistant

An intelligent web application that uses AI to automatically refactor and improve source code.

## Team Members

- Atul
- Saif
- Arun

## Project Overview

This application helps developers improve their code by using AI to refactor it. Users can paste code or upload files, and receive a cleaner, more maintainable version along with explanations of the changes.

This is a team project following Agile methodology for a software engineering course.

## Features (In Development)

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
- Supported file types: .py, .js, .java, .cpp, .c, .txt
- Maximum file size: 16MB

## License

This project is for educational purposes as part of a software engineering course.
