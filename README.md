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

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd spacetaskbackend
   ```

2. **Install dependencies**
   ```bash
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
├── api.py                 # Main Flask application
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
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
- `PORT`: Server port (default: 5000)
- `DEBUG`: Enable debug mode

## Security

- Passwords are hashed with bcrypt
- JWT tokens for authentication
- File upload validation and resizing
- SQL injection protection with parameterized queries
- CORS enabled for cross-origin requests

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

## API Usage Examples

### Create Account
```bash
curl -X POST http://localhost:5000/api/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure123"
  }'
```

### Create Task
```bash
curl -X POST http://localhost:5000/api/tasks \
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
curl -X POST http://localhost:5000/api/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@proof.jpg"
```

## License

This project is licensed under the MIT License. 