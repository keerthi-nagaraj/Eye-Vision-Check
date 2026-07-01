# Vision_app

A comprehensive computer vision application with AI-powered features for color vision testing and face detection. Built with Flask backend, SvelteKit frontend, and integrated with MediaPipe and TensorFlow for advanced vision processing.

## Tech Stack

### Backend
- **Flask** - Python web framework
- **MediaPipe** - Computer vision and ML solutions
- **TensorFlow** - Machine learning framework
- **OpenCV** - Computer vision library
- **SQLite** - Database for data persistence
- **Flask-CORS** - Cross-origin resource sharing
- **bcrypt** - Password hashing for authentication

### Frontend
- **SvelteKit** - Modern web framework with TypeScript
- **TailwindCSS** - Utility-first CSS framework
- **MediaPipe** - Face detection and vision tasks
- **TensorFlow.js** - Client-side ML
- **Chart.js** - Data visualization
- **jsPDF** - PDF generation for reports

## Prerequisites

- Docker and Docker Compose
- Node.js (v18+) and npm (for local development)
- Python 3.8+ (for local development)

## Quick Start with Docker

### 1. Clone and Navigate
```bash
cd Vision_app
```

### 2. Start the Application
```bash
docker-compose up --build
```

### 3. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5001

### 4. Stop the Application
```bash
docker-compose down
```

## Local Development

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start the Flask server
python flask_app.py
```

Backend will run on http://localhost:5000

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on http://localhost:5173

## Project Structure

```
Vision_app/
├── backend/
│   ├── flask_app.py          # Main Flask application
│   ├── database.py           # Database operations
│   ├── vision_pipeline.py    # Computer vision processing
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Backend container configuration
│   └── data/                 # SQLite database storage
├── frontend/
│   ├── src/                  # SvelteKit source code
│   ├── static/               # Static assets
│   ├── package.json          # Node dependencies
│   ├── Dockerfile            # Frontend container configuration
│   └── vite.config.ts        # Vite configuration
├── docker-compose.yml        # Multi-container orchestration
└── README.md                 # This file
```

## Features

- **Color Vision Testing**: Comprehensive Ishihara and tritan color vision tests
- **Face Detection**: Real-time face detection using MediaPipe
- **Computer Vision Pipeline**: Advanced image processing with OpenCV
- **PDF Report Generation**: Generate detailed test reports
- **Data Visualization**: Interactive charts for test results
- **Responsive Design**: Modern UI with TailwindCSS
- **Type Safety**: TypeScript for frontend reliability

## API Endpoints

### Authentication
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `GET /api/users/profile` - Get user profile

### Vision Tests
- `POST /api/tests/submit` - Submit test result
- `GET /api/tests/generate/ishihara` - Generate Ishihara plate
- `GET /api/tests/generate/tritan` - Generate Tritan plate
- `GET /api/tests/generate/hue` - Generate hue spectrum

### Results
- `GET /api/results/` - Get user results
- `GET /api/results/stats` - Get test statistics
- `DELETE /api/results/{id}` - Delete specific result

## Environment Variables

### Backend (.env)
```env
PORT=5000
DATABASE_PATH=/app/data/eyevision.db
FRONTEND_URL=http://localhost:5173
JWT_SECRET=your-secret-key
```

### Frontend
```env
VITE_API_PROXY_TARGET=http://backend:5000
```

## Docker Commands

```bash
# Build and start containers
docker-compose up --build

# Start containers in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

## Development Tips

- Backend changes auto-reload in development mode
- Frontend hot-reloads with Vite
- Database persists in `backend/data/` directory
- Use `docker-compose logs -f [service]` to debug issues
- Clear browser cache if you encounter stale data

## Troubleshooting

### Port Already in Use
```bash
# Kill process using port 5001
lsof -ti:5001 | xargs kill -9

# Kill process using port 5173
lsof -ti:5173 | xargs kill -9
```

### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
rm backend/data/eyevision.db
docker-compose restart backend
```

### Frontend Build Issues
```bash
cd frontend
rm -rf node_modules .svelte-kit
npm install
npm run dev
```

hdfsdgflkjdsgflksdjfhl