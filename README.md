# PaperScout

PaperScout is a tool that helps researchers find and summarize academic papers from arXiv. It uses AI to generate concise summaries of papers based on your research query.

## Features

- Search arXiv for relevant papers
- Generate AI-powered summaries of papers
- Real-time status updates and progress tracking
- Both CLI and web interface available
- Support for multiple LLM providers (OpenAI, Google, Anthropic)

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Poetry (Python package manager)
- npm or yarn

## Setup

### 1. Clone the repository

```bash
git clone [<repository-url>](https://github.com/Sachin-2007/scientific-paper-scout.git)
cd paperscout
```

### 2. Backend Setup

1. Install Poetry if you haven't already:
```bash
# Windows
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Linux/Mac
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install backend dependencies:
```bash
cd scout
poetry install
```

3. Create a `.env` file in the `scout` directory with the following variables:
```env
# Required: Choose one of the following providers
LLM_PROVIDER=openai  # Options: openai, google, anthropic

# Required: Model name for the chosen provider
LLM_MODEL=gpt-4-turbo-preview  # For OpenAI
# LLM_MODEL=gemini-pro  # For Google
# LLM_MODEL=claude-3-opus-20240229  # For Anthropic

# Required: API key for the chosen provider
LLM_API_KEY=your-api-key-here
```

### 3. Frontend Setup

1. Navigate to the frontend directory:
```bash
cd scout-ui
```

2. Install frontend dependencies:
```bash
npm install
```

## Running the Application

### 1. Start the Backend Server

In the scout directory:
```bash
poetry run python app.py
```

The backend server will start on `http://localhost:8000`.

### 2. Start the Frontend Development Server

In a new terminal, navigate to the frontend directory:
```bash
cd scout-ui
npm run dev
```

The frontend will be available at `http://localhost:5173`.

### 3. Using the CLI

You can also use the command-line interface:
```bash
# From the scout directory
poetry run python main.py
```

Follow the interactive prompts to:
1. Enter your research query
2. Specify the number of papers to process
3. View the results

## Usage

### Web Interface

1. Open `http://localhost:5173` in your browser
2. Enter your research query in the search box
3. Adjust the number of papers to process (default: 3)
4. Click "Search" to start the process
5. View the results as they appear

### CLI Interface

1. Run the CLI tool
2. Enter your research query when prompted
3. Specify the number of papers to process
4. View the results in your terminal

## Environment Variables

The following environment variables are required in the `.env` file:

- `LLM_PROVIDER`: The AI provider to use
  - `openai`: Use OpenAI's models
  - `google`: Use Google's models
  - `anthropic`: Use Anthropic's models

- `LLM_MODEL`: The specific model to use
  - OpenAI: `gpt-4-turbo-preview`, `gpt-3.5-turbo`, etc.
  - Google: `gemini-pro`, etc.
  - Anthropic: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, etc.

- `LLM_API_KEY`: Your API key for the chosen provider

## Troubleshooting

1. If you get a "Module not found" error:
   - Make sure you're using Poetry's virtual environment
   - Run `poetry install` to ensure all dependencies are installed

2. If the frontend can't connect to the backend:
   - Ensure both servers are running
   - Check that the backend is running on port 8000
   - Verify CORS settings in the backend

3. If you get API errors:
   - Verify your API key is correct
   - Check that you have sufficient credits/quota
   - Ensure you're using a supported model
