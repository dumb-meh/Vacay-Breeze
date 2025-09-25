# Vacay Breeze AI 🌴

**An AI-powered travel planning companion that creates personalized vacation experiences**

Vacay Breeze AI is a sophisticated FastAPI-based microservice that leverages artificial intelligence to generate personalized travel suggestions and regenerate travel plans based on user preferences and requirements.

## ✨ Features

- **🤖 AI-Powered Suggestions**: Get intelligent travel recommendations based on your preferences
- **🔄 Plan Regeneration**: Modify and regenerate existing travel plans with new requirements
- **🏨 Accommodation & Activity Planning**: Comprehensive suggestions for hotels, activities, and experiences
- **🍽️ Food & Amenities**: Personalized recommendations for dining and amenities
- **⚡ Fast & Scalable**: Built with FastAPI for high performance
- **🐳 Docker Ready**: Containerized with Docker and nginx reverse proxy
- **📚 API Documentation**: Auto-generated interactive API docs

## 🏗️ Architecture

```
Vacay Breeze AI
├── FastAPI Application (Port 9073)
├── Nginx Reverse Proxy (Port 9074)
├── AI Suggestion Service
├── Plan Regeneration Service
└── Health Monitoring
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key (or compatible AI service)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Vacay-Breeze
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   
   Configure your `.env` file with required API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   # Add other required environment variables
   ```

### 🐳 Docker Deployment (Recommended)

```bash
# Build and start all services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

The application will be available at:
- **API**: http://localhost:9074
- **Documentation**: http://localhost:9074/docs
- **ReDoc**: http://localhost:9074/redoc

### 🐍 Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python main.py
   ```

3. **Access the API**
   - API: http://localhost:9073
   - Documentation: http://localhost:9073/docs

## 📖 API Endpoints

### Health Checks
- `GET /` - Root endpoint with welcome message
- `GET /health` - Service health status

### AI Services
- `POST /ai_suggestion` - Generate AI-powered travel suggestions
- `POST /regenerate_plan` - Regenerate existing travel plans

## 🔧 API Usage Examples

### Generate AI Travel Suggestions

```bash
curl -X POST "http://localhost:9074/ai_suggestion" \
  -H "Content-Type: application/json" \
  -d '{
    "total_adults": 2,
    "total_children": 0,
    "destination": "Paris, France",
    "location": "Europe",
    "departure_date": "2024-06-15",
    "return_date": "2024-06-22",
    "amenities": ["wifi", "pool", "gym"],
    "activities": ["museums", "restaurants", "sightseeing"],
    "pacing": ["relaxed"],
    "food": ["local cuisine", "fine dining"],
    "special_note": "Celebrating anniversary"
  }'
```

### Regenerate Travel Plan

```bash
curl -X POST "http://localhost:9074/regenerate_plan" \
  -H "Content-Type: application/json" \
  -d '{
    "total_adults": 2,
    "total_children": 1,
    "destination": "Tokyo, Japan",
    "location": "Asia",
    "departure_date": "2024-07-10",
    "return_date": "2024-07-17",
    "amenities": ["family-friendly", "wifi"],
    "activities": ["cultural sites", "theme parks"],
    "pacing": ["moderate"],
    "food": ["kid-friendly", "authentic Japanese"],
    "special_note": "Family trip with 8-year-old"
  }'
```

## 📁 Project Structure

```
Vacay-Breeze/
├── app/
│   ├── core/
│   │   └── config.py                
│   └── services/
│       ├── ai_suggestion/
│       │   ├── ai_suggestion.py     
│       │   ├── ai_suggestion_route.py 
│       │   └── ai_suggestion_schema.py 
│       └── regenerate_plan/
│           ├── regenerate_plan.py   
│           ├── regenerate_plan_route.py 
│           └── regenerate_plan_schema.py 
├── nginx/
│   └── nginx.conf                   
├── docker-compose.yml              
├── Dockerfile                   
├── main.py                       
├── requirements.txt                
└── README.md                     
```

## 🛠️ Development

### Adding New Services

1. Create a new service directory under `app/services/`
2. Implement the service logic, routes, and schemas
3. Register the router in `main.py`

### Testing

```bash
# Run with development reload
uvicorn main:app --reload --host 0.0.0.0 --port 9073
```

### Environment Variables

Key environment variables to configure:

- `OPENAI_API_KEY`: OpenAI API key for AI services
- `DEBUG`: Enable debug mode (default: False)
- `API_HOST`: API host (default: 0.0.0.0)
- `API_PORT`: API port (default: 9073)

## 🔒 Security Features

- CORS middleware configured for cross-origin requests
- Environment-based configuration
- Docker containerization with health checks
- Nginx reverse proxy for additional security layer

## 🚦 Monitoring & Health Checks

The application includes built-in health check endpoints and Docker health checks:

```bash
# Check application health
curl http://localhost:9074/health

# Docker health status
docker-compose ps
```
