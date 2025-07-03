# SpaceTask Backend

A location-based task completion app where users can create tasks with bounties and others can complete them for rewards.

## Features

- **User Authentication**: JWT-based authentication with signup/login
- **Task Management**: Create, view, update, and delete location-based tasks
- **Coin System**: Users start with 200 coins, earn coins by completing tasks
- **Image Upload**: Upload proof images for task completion
- **Location-based**: Find tasks near your location
- **Bounty System**: Task creators set bounty amounts, completers get bounty + 10 base coins

## API Endpoints

### Authentication
- `POST /api/signup` - Create account with 200 starting coins
- `POST /api/login` - Authenticate and get JWT token
- `GET /api/me` - Get current user info

### Tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks` - List all tasks
- `GET /api/tasks/:id` - Get task details
- `PATCH /api/tasks/:id` - Update task (owner only)
- `DELETE /api/tasks/:id` - Delete task (owner only, if no submissions)
- `GET /api/tasks/nearby?lat=...&lng=...` - Get nearby tasks

### Task Completion
- `POST /api/tasks/:id/submit` - Submit proof for task completion
- `GET /api/tasks/:id/submissions` - View submissions (owner only)
- `POST /api/tasks/:id/submissions/:submissionId/accept` - Accept submission

### Users
- `GET /api/users/:id` - View user profile
- `GET /api/users/:id/tasks` - View tasks created by user
- `GET /api/users/:id/completions` - View tasks completed by user

### File Upload
- `POST /api/upload` - Upload image file

### Notifications
- `POST /api/notifications/register` - Register device for push notifications

## Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd spacetaskbackend
   ```

2. **Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:5000`

### Docker Deployment

#### Quick Start with Docker Compose

1. **Clone and build**
   ```bash
   git clone <repository-url>
   cd spacetaskbackend
   ```

2. **Run with Docker Compose**
   ```bash
   # Development
   docker-compose up -d

   # Production with environment variables
   export SECRET_KEY="your-production-secret-key"
   export JWT_SECRET="your-production-jwt-secret"
   export BASE_URL="https://yourdomain.com"
   docker-compose -f docker-compose.prod.yml up -d
   ```

The API will be available at `http://localhost:8000`

#### Docker Commands

```bash
# Build the image
docker build -t spacetask-backend .

# Run the container
docker run -d \
  --name spacetask \
  -p 8000:8000 \
  -e SECRET_KEY="your-secret-key" \
  -e JWT_SECRET="your-jwt-secret" \
  -v spacetask_data:/app/data \
  -v spacetask_uploads:/app/uploads \
  spacetask-backend

# View logs
docker logs spacetask

# Stop and remove
docker stop spacetask
docker rm spacetask
```

#### Production Deployment with Nginx

For production with SSL and reverse proxy:

```bash
# Run with nginx reverse proxy
docker-compose -f docker-compose.prod.yml --profile with-nginx up -d
```

#### Environment Variables for Docker

Create a `.env` file for production:

```bash
SECRET_KEY=your-very-secure-secret-key-here
JWT_SECRET=your-very-secure-jwt-secret-here
BASE_URL=https://yourdomain.com
DEBUG=False
```

## Project Structure

```
spacetaskbackend/
├── api/                    # API endpoint blueprints
│   ├── auth.py            # Authentication endpoints
│   ├── tasks.py           # Task management endpoints
│   ├── submissions.py     # Task submission endpoints
│   ├── upload.py          # File upload endpoints
│   ├── notifications.py   # Notification endpoints
│   └── users.py           # User profile endpoints
├── services/              # Business logic services
│   ├── database.py        # Database operations
│   ├── auth.py            # Authentication service
│   ├── email.py           # Email service
│   └── upload.py          # File upload service
├── uploads/               # Uploaded files directory
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
├── Dockerfile            # Docker container definition
├── docker-compose.yml    # Docker Compose for development
├── docker-compose.prod.yml # Docker Compose for production
├── nginx.conf            # Nginx reverse proxy configuration
└── README.md             # This file
```

## Database Schema

The app uses SQLite with the following tables:

- **users**: User accounts with coin balances
- **tasks**: Location-based tasks with bounties
- **task_submissions**: Proof submissions for tasks
- **notifications**: Device tokens for push notifications
- **transactions**: Coin transfer history

## Configuration

Key environment variables:

- `SECRET_KEY`: Flask secret key
- `JWT_SECRET`: JWT signing secret
- `DATABASE_PATH`: SQLite database file path
- `UPLOAD_FOLDER`: Directory for uploaded files
- `BASE_URL`: Base URL for file serving
- `PORT`: Server port (default: 5000, Docker: 8000)
- `DEBUG`: Enable debug mode

## Security

- Passwords are hashed with bcrypt
- JWT tokens for authentication
- File upload validation and resizing
- SQL injection protection with parameterized queries
- CORS enabled for cross-origin requests
- Docker security: non-root user, read-only filesystem, resource limits

## Coin System

- Users start with 200 coins upon signup
- Task creators set bounty amounts (deducted from their balance)
- Task completers receive bounty + 10 base coins
- Server-side validation ensures coin integrity

## Development

To run in development mode:

```bash
export DEBUG=True
python main.py
```

The API will reload automatically when files change.

## Production Deployment

### Docker (Recommended)

1. **Build and deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Set up SSL** (optional, with nginx)
   - Configure SSL certificates
   - Update nginx.conf for HTTPS
   - Use Let's Encrypt for free SSL

3. **Monitor**
   ```bash
   docker-compose logs -f spacetask-backend
   ```

### Manual Deployment

1. **Set up server** (Ubuntu/Debian)
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx
   ```

2. **Deploy application**
   ```bash
   git clone <repository-url>
   cd spacetaskbackend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure systemd service**
   ```bash
   sudo cp spacetask.service /etc/systemd/system/
   sudo systemctl enable spacetask
   sudo systemctl start spacetask
   ```

4. **Configure nginx reverse proxy**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/spacetask
   sudo ln -s /etc/nginx/sites-available/spacetask /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

## API Usage Examples

### Create Account
```bash
curl -X POST http://localhost:8000/api/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure123"
  }'
```

### Create Task
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean up park",
    "description": "Remove litter from Central Park",
    "completion_criteria": "Photo of clean area",
    "bounty_amount": 50,
    "latitude": 40.7829,
    "longitude": -73.9654,
    "location_name": "Central Park, NYC"
  }'
```

### Upload Image
```bash
curl -X POST http://localhost:8000/api/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@proof.jpg"
```

## License

This project is licensed under the MIT License. 