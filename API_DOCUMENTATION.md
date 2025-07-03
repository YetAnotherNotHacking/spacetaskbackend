# SpaceTask API Documentation

This document provides detailed information about all available endpoints in the SpaceTask API, including request/response formats and examples.

## Table of Contents
- [Authentication](#authentication)
- [Users](#users)
- [Tasks](#tasks)
- [Task Submissions](#task-submissions)
- [Notifications](#notifications)
- [Media](#media)

## Authentication

### POST /signup
Create a new user account. Users start with 200 coins.

**Request Body:**
```json
{
    "username": "string",
    "email": "string",
    "password": "string"
}
```

**Response (200 OK):**
```json
{
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "coin_balance": 200,
        "created_at": "timestamp"
    },
    "token": "string"
}
```

### POST /login
Authenticate user and get access token.

**Request Body:**
```json
{
    "email": "string",
    "password": "string"
}
```

**Response (200 OK):**
```json
{
    "token": "string",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "coin_balance": "integer",
        "created_at": "timestamp"
    }
}
```

### GET /me
Get current user information. Requires authentication.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "coin_balance": "integer",
        "created_at": "timestamp"
    }
}
```

## Users

### GET /users/{user_id}
Get user profile information.

**Response (200 OK):**
```json
{
    "user": {
        "id": "integer",
        "username": "string",
        "created_at": "timestamp"
    }
}
```

### GET /users/{user_id}/tasks
Get tasks created by a specific user.

**Response (200 OK):**
```json
{
    "tasks": [
        {
            "id": "integer",
            "title": "string",
            "description": "string",
            "label": "string",
            "completion_criteria": "string",
            "bounty_amount": "integer",
            "latitude": "float",
            "longitude": "float",
            "location_name": "string",
            "status": "string",
            "created_at": "timestamp",
            "creator_username": "string"
        }
    ],
    "count": "integer"
}
```

### GET /users/{user_id}/completions
Get tasks completed by a specific user.

**Response (200 OK):**
```json
{
    "completions": [
        {
            "id": "integer",
            "title": "string",
            "description": "string",
            "label": "string",
            "completion_criteria": "string",
            "bounty_amount": "integer",
            "latitude": "float",
            "longitude": "float",
            "location_name": "string",
            "status": "string",
            "created_at": "timestamp",
            "creator_username": "string",
            "submitted_at": "timestamp",
            "image_url": "string"
        }
    ],
    "count": "integer"
}
```

### GET /users/leaderboard
Get user leaderboard ordered by coins, task completions, and username.

**Query Parameters:**
- `limit` (optional): Number of users to return (default: 10, max: 100)

**Response (200 OK):**
```json
{
    "leaderboard": [
        {
            "id": "integer",
            "username": "string",
            "coin_balance": "integer",
            "completed_tasks": "integer"
        }
    ],
    "count": "integer"
}
```

## Tasks

### POST /tasks
Create a new task. Requires authentication.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
    "title": "string",
    "description": "string",
    "label": "string",
    "completion_criteria": "string",
    "bounty_amount": "integer",
    "latitude": "float",
    "longitude": "float",
    "location_name": "string (optional)"
}
```

**Response (201 Created):**
```json
{
    "task": {
        "id": "integer",
        "title": "string",
        "description": "string",
        "label": "string",
        "completion_criteria": "string",
        "bounty_amount": "integer",
        "latitude": "float",
        "longitude": "float",
        "location_name": "string",
        "status": "string",
        "created_at": "timestamp",
        "creator_username": "string"
    }
}
```

### GET /tasks
List tasks with optional filtering.

**Query Parameters:**
- `limit` (optional): Number of tasks to return (default: 50)
- `offset` (optional): Number of tasks to skip (default: 0)
- `status` (optional): Filter by task status (default: "active")

**Response (200 OK):**
```json
{
    "tasks": [
        {
            "id": "integer",
            "title": "string",
            "description": "string",
            "label": "string",
            "completion_criteria": "string",
            "bounty_amount": "integer",
            "latitude": "float",
            "longitude": "float",
            "location_name": "string",
            "status": "string",
            "created_at": "timestamp",
            "creator_username": "string"
        }
    ],
    "count": "integer"
}
```

### GET /tasks/{task_id}
Get detailed information about a specific task.

**Response (200 OK):**
```json
{
    "task": {
        "id": "integer",
        "title": "string",
        "description": "string",
        "label": "string",
        "completion_criteria": "string",
        "bounty_amount": "integer",
        "latitude": "float",
        "longitude": "float",
        "location_name": "string",
        "status": "string",
        "created_at": "timestamp",
        "creator_username": "string"
    }
}
```

### PATCH /tasks/{task_id}
Update a task. Only the task creator can update their tasks. Requires authentication.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body (all fields optional):**
```json
{
    "title": "string",
    "description": "string",
    "label": "string",
    "completion_criteria": "string",
    "bounty_amount": "integer",
    "status": "string"
}
```

**Response (200 OK):**
```json
{
    "task": {
        "id": "integer",
        "title": "string",
        "description": "string",
        "label": "string",
        "completion_criteria": "string",
        "bounty_amount": "integer",
        "latitude": "float",
        "longitude": "float",
        "location_name": "string",
        "status": "string",
        "created_at": "timestamp",
        "creator_username": "string"
    }
}
```

### DELETE /tasks/{task_id}
Delete a task. Only the task creator can delete their tasks. Requires authentication.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (204 No Content)**

## Task Submissions

### POST /tasks/{task_id}/submit
Submit proof of task completion. Requires authentication.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
    "image_url": "string",
    "note": "string (optional)"
}
```

**Response (201 Created):**
```json
{
    "submission": {
        "id": "integer",
        "task_id": "integer",
        "submitter_id": "integer",
        "image_url": "string",
        "note": "string",
        "status": "pending",
        "submitted_at": "timestamp"
    }
}
```

### GET /tasks/{task_id}/submissions
View submissions for a task. Only the task creator can view submissions. Requires authentication.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
    "submissions": [
        {
            "id": "integer",
            "task_id": "integer",
            "submitter_id": "integer",
            "submitter_username": "string",
            "image_url": "string",
            "note": "string",
            "status": "string",
            "submitted_at": "timestamp",
            "reviewed_at": "timestamp"
        }
    ],
    "count": "integer"
}
```

### POST /tasks/{task_id}/submissions/{submission_id}/accept
Accept a submission and transfer coins. Only the task creator can accept submissions. Requires authentication.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
    "submission": {
        "id": "integer",
        "task_id": "integer",
        "submitter_id": "integer",
        "status": "accepted",
        "reviewed_at": "timestamp"
    },
    "transaction": {
        "id": "integer",
        "from_user_id": "integer",
        "to_user_id": "integer",
        "amount": "integer",
        "transaction_type": "task_completion",
        "task_id": "integer",
        "created_at": "timestamp"
    }
}
```

## Notifications

### POST /notifications/register
Register a device for push notifications. Requires authentication.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
    "device_token": "string",
    "platform": "string (ios/android)"
}
```

**Response (200 OK):**
```json
{
    "success": true
}
```

### GET /tasks/nearby
Get tasks near a location (used for push notifications).

**Query Parameters:**
- `lat`: Latitude (float)
- `lng`: Longitude (float)
- `radius`: Search radius in kilometers (float, optional, default: 5.0)

**Response (200 OK):**
```json
{
    "tasks": [
        {
            "id": "integer",
            "title": "string",
            "description": "string",
            "label": "string",
            "bounty_amount": "integer",
            "latitude": "float",
            "longitude": "float",
            "location_name": "string",
            "distance": "float (in km)"
        }
    ],
    "count": "integer"
}
```

## Media

### POST /upload
Upload an image. Returns a URL that can be used in task submissions. Requires authentication.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <image file>
```

**Response (200 OK):**
```json
{
    "url": "string"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "error": "string (description of what went wrong)"
}
```

### 401 Unauthorized
```json
{
    "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
    "error": "You don't have permission to perform this action"
}
```

### 404 Not Found
```json
{
    "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal server error"
}
``` 