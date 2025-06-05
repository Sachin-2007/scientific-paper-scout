# PaperScout

PaperScout is a tool that helps researchers find and summarize academic papers from arXiv using AI.

## Features

* Search arXiv for relevant papers
* Generate AI-powered summaries
* Real-time status updates
* Web interface and CLI support
* Multiple LLM providers (OpenAI, Google, Anthropic)

## Prerequisites

* Python 3.8+
* Node.js 16+
* pip
* npm

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Sachin-2007/scientific-paper-scout.git
cd scientific-paper-scout
```

2. Backend Setup:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
pip install -r requirements.txt
```

3. Create `.env` file in `scout` directory:
```env
LLM_PROVIDER=openai  # openai, google, or anthropic
LLM_MODEL=gpt-4-turbo-preview  # model name for chosen provider
LLM_API_KEY=your-api-key-here
```

4. Frontend Setup:
```bash
cd scout-ui
npm install
```

## Running the Application

1. Start Backend:
```bash
cd scout
# Make sure your virtual environment is activated
python app.py
```

2. Start Frontend:
```bash
cd scout-ui
npm run dev
```

3. Access the web interface at `http://localhost:5173`

## CLI Usage

```bash
cd scout
# Make sure your virtual environment is activated
python main.py
```

Follow the prompts to:
1. Enter research query
2. Specify number of papers
3. View results

## Environment Variables

Required in `.env`:
* `LLM_PROVIDER`: AI provider (openai, google, anthropic)
* `LLM_MODEL`: Model name for chosen provider
* `LLM_API_KEY`: API key for provider
