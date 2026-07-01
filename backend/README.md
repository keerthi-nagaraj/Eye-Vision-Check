# Color Vision Test Backend API - Flask + SQLite

A Flask backend with SQLite database storage for the Color Vision Test application.

## Features

- **Flask**: Lightweight Python web framework
- **SQLite**: Local database for development and persistence
- **Authentication**: Cookie-based session authentication
- **API Routes**: RESTful endpoints for tests, results, and users
- **Computer Vision**: OpenCV/MediaPipe/TensorFlow integration

## Quick Start with Flask

### 1. Configure Backend
```bash
# Copy environment template
cp .env.example .env
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Server
```bash
python flask_app.py
```

## API Endpoints

### Authentication
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `POST /api/users/logout` - Logout user
- `GET /api/auth/me` - Get logged-in user profile

### Tests
- `POST /api/tests/submit` - Submit test result
- `GET /api/tests/generate/ishihara` - Generate Ishihara plate
- `GET /api/tests/generate/tritan` - Generate Tritan plate
- `GET /api/tests/generate/hue` - Generate hue spectrum

### Results
- `GET /api/results/` - Get user results
- `GET /api/results/stats` - Get test statistics
- `DELETE /api/results/{id}` - Delete specific result

## Environment Variables

The backend reads configuration from `.env`.

```env
PORT=5000
DATABASE_PATH=/app/data/eyevision.db
FRONTEND_URL=http://localhost:5173
JWT_SECRET=your-secret-key
```

## Production

### Environment Setup:
1. Use a strong `JWT_SECRET`
2. Set `FRONTEND_URL` to your frontend URL
3. Ensure `DATABASE_PATH` is writable by the app

### Production Commands:
```bash
pip install -r requirements.txt
python flask_app.py
```

## Development

```bash
pip install -r requirements.txt
python flask_app.py
```

## Response Format

Successful responses generally return:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

Error responses generally return:

```json
{
  "success": false,
  "message": "Error description"
}
```
