# Buddy - Smart Daily Planner  **[▶️ Live Demo](https://buddy-lime.vercel.app)** | 📖 **[API Docs](https://web-production-6e4cd.up.railway.app/docs)**

A full-stack web application for managing daily activities, tracking progress, and staying informed with weather, news, and stock updates.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- **Activity Management** - Create, edit, delete, and track daily activities
- **Progress Tracking** - Mark activities as done, missed, partial, or rescheduled
- **Weather Integration** - Real-time weather data for major cities
- **News Feed** - Top headlines across multiple categories
- **Stock Market** - Track your watchlist and market indices
- **Weekly Analytics** - Visualize completion rates, streaks, and insights
- **Smart Suggestions** - Context-aware recommendations based on weather and patterns

## Tech Stack

### Backend
- Python 3.10+
- FastAPI
- SQLAlchemy (SQLite)
- Pydantic

### Frontend
- React 18
- Tailwind CSS
- Axios
- React Router
- Lucide Icons

### APIs
- OpenWeatherMap (Weather)
- NewsAPI (News)
- Alpha Vantage (Stocks)

## Project Structure
```
buddy/
├── api/                    # FastAPI backend
│   ├── main.py            # API entry point
│   └── routers/           # API endpoints
│       ├── activities.py
│       ├── analytics.py
│       ├── dashboard.py
│       ├── news.py
│       ├── stocks.py
│       ├── settings.py
│       └── weather.py
├── src/                    # Core Python modules
│   ├── config/            # Configuration management
│   ├── core/              # Business logic
│   ├── models/            # Database models
│   ├── services/          # External API services
│   └── utils/             # Helper functions
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   └── services/      # API client
│   └── package.json
├── data/                  # SQLite database
├── requirements.txt       # Python dependencies
└── README.md
```

## Getting Started

### Quick Start (Live Version)

Try Buddy right now without installation: **[Open Buddy Live](https://buddy-lime.vercel.app)**

Everything works out of the box! No setup needed.

### Local Development Setup

If you want to run it locally...
[rest of installation section stays the same]

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- npm

### 1. Clone the repository
```bash
git clone https://github.com/LashaJaparidze15/Buddy.git
cd Buddy
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.models import init_db; init_db()"
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Configure API Keys

Create a `.env` file in the project root:
```env
WEATHER_API_KEY=your_openweathermap_key
NEWS_API_KEY=your_newsapi_key
STOCKS_API_KEY=your_alphavantage_key
```

Get free API keys from:
- Weather: https://openweathermap.org/api
- News: https://newsapi.org
- Stocks: https://www.alphavantage.co

## Running the Application

### Online (No Installation Required)

Visit: **https://buddy-lime.vercel.app**

All features work immediately with live API integration.

### Locally (Development)
...
### Start Backend Server
```bash
# From project root with venv activated
python -m uvicorn api.main:app --reload
```

Backend runs at: http://localhost:8000

### Start Frontend Server
```bash
# From frontend directory
cd frontend
npm run dev
```

Frontend runs at: http://localhost:5173

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usage

### Activities

- **Add Activity**: Click "Add Activity" button, fill in details
- **Mark Complete**: Click the circle icon next to an activity
- **Delete**: Click the trash icon
- **Filter**: Use Today/Week/All tabs

### Settings

- Select your city from the dropdown
- Choose temperature units (Celsius/Fahrenheit)
- Settings are saved locally

### Analytics

- View weekly completion rates
- Track streaks and patterns
- Compare week-over-week progress

## CLI Tool

Buddy also includes a command-line interface:
```bash
# Initialize database
python buddy.py init

# Add activity
python buddy.py add "Morning Run" --time 06:30 --category Health

# List activities
python buddy.py list

# Generate daily report
python buddy.py report

# View analytics
python buddy.py analytics
```

## Deployment

Buddy is deployed on:

- **Frontend:** [Vercel](https://vercel.com) - https://buddy-lime.vercel.app
- **Backend:** [Railway](https://railway.app) - https://web-production-6e4cd.up.railway.app
- **API Documentation:** https://web-production-6e4cd.up.railway.app/docs

The app is live 24/7 and fully functional!

## Screenshots

### Dashboard
Clean overview of weather, activities, and suggestions.

### Activities
Full-width table with filtering and quick actions.

### Analytics
Visual progress tracking with charts and insights.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenWeatherMap](https://openweathermap.org/) for weather data
- [NewsAPI](https://newsapi.org/) for news headlines
- [Alpha Vantage](https://www.alphavantage.co/) for stock data
- [Lucide](https://lucide.dev/) for icons
```
