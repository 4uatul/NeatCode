# NeatCode — AI-Powered Code Refactoring Tool

NeatCode takes your messy code and returns a clean, refactored version with a summary of what changed and why. Started as an academic team project and expanded into a fully deployed AWS application.

**Live Demo:** http://neatcode-app-frontend.s3-website-us-west-1.amazonaws.com

> Warning: The app currently runs over HTTP (not HTTPS). Do not paste sensitive or proprietary code. HTTPS support is on the roadmap.

---

## What It Does

- Paste code or upload a file and get back refactored code instantly
- Explains every change made with a reason
- Gives a one-line summary of what the code does
- **Guard rails** — if you paste random text, a question, or anything that is not code, the app detects it and asks you to try again instead of blindly processing it
- **Feedback section** — rate the refactored output to help improve the tool over time
- Supports: Python, JavaScript, Java, C, C++, C#, PHP, HTML, CSS, Ruby, Swift, JSON, XML

---

## Team

- Atul
- Saif
- Arun

---

## Tech Stack

### Frontend
- **React 18** — UI framework
- **AWS S3** — hosts the built static files
- **AWS CloudFront** — CDN that sits in front of S3 and delivers the app from edge locations closest to the user globally

### Backend
- **Python / Flask** — REST API server
- **Google Gemini AI** — does the actual code refactoring
- **Docker** — packages the Flask app into a container so it runs the same everywhere
- **AWS Elastic Beanstalk** — runs the Docker container on AWS, handles deployments, health checks, and restarts automatically without needing to manage the underlying server directly

---

## Architecture

```
User Browser
     |
     |--[React App]--> AWS CloudFront --> AWS S3 (static files)
     |
     |--[API calls]--> AWS Elastic Beanstalk
                              |
                         Docker Container
                              |
                         Flask (app.py)
                              |
                      Google Gemini AI API
```

---

## How the AI Works

The backend sends your code to Gemini with a strict prompt that tells it to:

- Fix naming conventions (snake_case for Python, camelCase for JS/Java)
- Fix formatting and indentation
- Simplify redundant logic
- Use idiomatic built-ins where appropriate
- Add minimal comments only where logic is non-obvious
- Preserve exact same functionality — no added features, no extra error handling

It returns structured JSON with `refactored_code`, `project_summary`, and `key_changes`.

### Model Fallback Chain

To handle API quota limits, the backend tries models in order and falls back automatically:

```
gemini-2.5-flash          <- primary (best quality)
gemini-2.5-flash-lite     <- fallback 1
gemini-3-flash-preview    <- fallback 2
gemini-3.1-flash-lite     <- fallback 3
gemini-2.0-flash          <- fallback 4
gemini-2.0-flash-lite     <- fallback 5 (highest quota)
```

---

## AWS Deployment

### Backend — Elastic Beanstalk

The Flask app runs inside a Docker container on Elastic Beanstalk.

**Why Elastic Beanstalk?**
EB manages the EC2 instance, networking, health monitoring, and deployments for you. You push code and it handles the rest — no server administration needed. It supports Docker natively so the same container that runs locally runs in production with zero changes.

**Deploy / update backend:**
```bash
cd Backend
eb deploy
```

**Update environment variables:**
```bash
eb setenv GEMINI_API_KEY=your_key PORT=5000
```

**Backend URL:** `http://neatcode-backend-env.eba-pzp7imcu.us-west-1.elasticbeanstalk.com`

---

### Frontend — S3 + CloudFront

The React app is built into static files and uploaded to S3.

**Why S3 + CloudFront?**
After `npm run build`, a React app is just HTML, CSS, and JS files — no server needed to run it. S3 hosts those files cheaply and reliably. CloudFront caches them at edge locations around the world so the app loads fast regardless of where the user is.

**Deploy / update frontend:**
```bash
npm run build
aws s3 sync build/ s3://neatcode-app-frontend
aws cloudfront create-invalidation --distribution-id EVHRD1JS9QDGW --paths "/*"
```

**Frontend URLs:**
- S3 (HTTP): `http://neatcode-app-frontend.s3-website-us-west-1.amazonaws.com`
- CloudFront (HTTPS): `https://d8f2h60tm7vu9.cloudfront.net` — blocked by mixed content until backend gets HTTPS

---

## Running Locally

### Backend
```bash
cd Backend
pip install -r requirements.txt
```

Create a `.env` file in the `Backend/` folder:
```
GEMINI_API_KEY=your_key_here
PORT=5000
```

Then run:
```bash
python app.py
```

### Frontend
```bash
npm install
npm start
```

Frontend runs at `http://localhost:3000`, backend at `http://localhost:5000`.

---

## Project Structure

```
NeatCode/
├── src/                    # React frontend
│   ├── App.js              # Main component
│   ├── components/         # UI components
│   ├── styles/             # CSS styles
│   └── utils/              # Helper functions
├── Backend/
│   ├── app.py              # Flask API server
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Docker config
│   └── .env                # API keys (not committed to git)
├── build/                  # React production build (generated by npm run build)
├── AWS_DEPLOYMENT_GUIDE.md # Full AWS setup reference
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API status and available endpoints |
| GET | `/api/health` | Health check with active model list |
| POST | `/api/refactor` | Refactor code from text input |
| POST | `/api/refactor-file` | Refactor code from uploaded file |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key (required) |
| `PORT` | Port for Flask server (default: 5000) |
| `GEMINI_MODEL` | Primary Gemini model (default: gemini-2.5-flash) |

Never commit your `.env` file. On AWS, set these via `eb setenv` instead.

---

## Supported File Types

`py` `js` `java` `cpp` `c` `cs` `php` `html` `css` `json` `xml` `rb` `swift` `txt`

---

## Roadmap

- [ ] HTTPS on the backend with a custom domain
- [ ] User authentication
- [ ] Refactoring history and saved sessions
- [ ] Wider language support
- [ ] Migrate backend to AWS App Runner for serverless scaling

---

## License

This project started as an academic software engineering course project and has since been expanded and deployed independently.
