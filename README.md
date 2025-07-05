# Docker Setup Instructions

## Prerequisites
1. Install Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Make sure Docker is running

## Project Structure
```
your-project/
├── docker-compose.yml
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── package.json
│   └── ... (Next.js files)
└── backend/
    ├── Dockerfile
    ├── .dockerignore
    ├── requirements.txt
    ├── main.py
    └── ... (FastAPI files)
```

## Setup Steps

### 1. Create the Docker files
- Place the `docker-compose.yml` in your project root
- Create `Dockerfile` in both `/frontend` and `/backend` directories
- Create `.dockerignore` files in both directories
- Ensure your backend has a `requirements.txt` file

### 2. Build and run the application
```bash
# From your project root directory
docker-compose up --build
```

### 3. Access your applications
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Database: localhost:5432

## Common Commands

### Start the application
```bash
docker-compose up
```

### Start in background (detached mode)
```bash
docker-compose up -d
```

### Stop the application
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs
docker-compose logs backend  # Just backend logs
docker-compose logs frontend # Just frontend logs
```

### Rebuild containers
```bash
docker-compose up --build
```

### Run commands in containers
```bash
# Execute commands in running containers
docker-compose exec backend python manage.py migrate
docker-compose exec frontend npm install new-package
```

### Clean up (remove containers, networks, volumes)
```bash
docker-compose down -v
```

## For Your Friend

Your friend only needs to:
1. Install Docker Desktop
2. Clone the repository
3. Run `docker-compose up --build`

That's it! No need to install Python, Node.js, or any dependencies locally.

## Tips

- The `volumes` in docker-compose.yml enable hot reloading - changes to your code will automatically restart the services
- Environment variables can be customized in the docker-compose.yml file
- The database data persists in a Docker volume, so it won't be lost when containers stop
- Use `docker-compose logs -f` to follow logs in real-time