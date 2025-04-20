# Technical Assignment - Task Management API



## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/CodeTerminator007/assesment_selteq.git

cd assesment_selteq
```

2. Start the services:
```bash
docker-compose up -d --build
```

3. The system will automatically:
   - Run database migrations
   - Create admin user (admin@admin.com / admin)
   - Create sample task
   - Start all services

4. To run the tests:
```bash
# Inside the Docker container
docker-compose exec web python manage.py test tasks.tests -v 2
```
5. To run the Log Tasks command:
```bash
# Inside the Docker container
docker-compose exec web python manage.py log_tasks
```


## Technical Requirements Implemented

1. **Authentication**
   - JWT (JSON Web Token) implementation
   - Token expiry: 5 minutes
   - Refresh token validity: 1 day

2. **Task Management**
   - Create, Read, Update, Delete (CRUD) operations
   - User-specific task isolation
   - Last 4 tasks display in list view

3. **Raw SQL Implementation**
   - Custom endpoint for title-only updates
   - Raw SQL query for task retrieval
   - SQL injection protection

4. **Background Tasks**
   - Celery with Redis as message broker and result backend
   - Periodic task execution (Celery Beat)
   - Task status monitoring

5. **Docker Integration**
   - Multi-container setup
   - MySQL database
   - Redis message broker
   - Automatic initialization

6. **Testing**
   - Comprehensive test suite
   - JWT authentication tests
   - Task management tests
   - Raw SQL operations tests



## API Endpoints

### Authentication
```
POST   /api/token/          - Obtain JWT token pair
POST   /api/token/refresh/  - Refresh access token
```

### Task Management
```
GET    /api/tasks/          - List tasks (last 4)
POST   /api/tasks/          - Create new task
GET    /api/tasks/{id}/     - Retrieve task
DELETE /api/tasks/{id}/     - Delete task
```

### Raw SQL Operations
```
GET    /api/tasks/{id}/raw_retrieve/     - Raw SQL task retrieval
PUT    /api/tasks/{id}/raw_update_title/ - Raw SQL title update
```


## Testing the API

1. Get JWT Token:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

2. Create Task:
```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "duration": "02:00:00"
  }'
```

3. Update Task Title (Raw SQL):
```bash
curl -X PUT http://localhost:8000/api/tasks/1/raw_update_title/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

4. List Tasks (Last 4):
```bash
curl -X GET http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

5. Delete Task:
```bash
curl -X DELETE http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

6. Raw SQL Task Retrieval:
```bash
curl -X GET http://localhost:8000/api/tasks/1/raw_retrieve/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```   

7. Raw SQL Task Title Update:
```bash
curl -X PUT http://localhost:8000/api/tasks/1/raw_update_title/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

