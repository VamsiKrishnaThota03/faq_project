
# FAQ Project

This project is designed to manage FAQs with multilingual support using Django, Django REST Framework, and `django-ckeditor` for WYSIWYG editor integration. It includes automatic translations for FAQs using the `deep-translator` API and implements Redis caching for efficient API responses.

## Table of Contents
1. [Installation Steps](#installation-steps)
2. [API Usage Examples](#api-usage-examples)
3. [Contribution Guidelines](#contribution-guidelines)
4. [Git & Version Control](#git--version-control)
5. [Deployment & Docker Support](#deployment--docker-support)
6. [Future Deployment](#future-deployment)

## Installation Steps

### 1. Clone the repository

Clone the project to your local machine using:

```bash
git clone https://github.com/VamsiKrishnaThota03/faq_project
cd faq-project
```

### 2. Set up a virtual environment

Create a virtual environment and activate it:

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install the required dependencies

Install the project dependencies from the `requirements.txt`:

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `Django==5.1.5`
- `djangorestframework==3.15.0`
- `django-ckeditor==6.1.0`
- `deep-translator==1.5.4`
- `redis==4.5.1`
- `django-redis==5.0.0`
- `flake8==6.0.0`
- `pytest==7.0.0`

### 4. Set up the environment variables

Create a `.env` file in the root directory to store sensitive information such as your **Google API key** and **Redis configuration**. Example:

```ini
GOOGLE_APPLICATION_CREDENTIALS=path/to/google_credentials.json
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

Make sure to replace `path/to/google_credentials.json` with the actual path to your Google API credentials file.

### 5. Run migrations

Make sure the database schema is up to date by running:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run the development server

Start the server:

```bash
python manage.py runserver
```

Your Django app should now be running on `http://127.0.0.1:8000/`.

---

## API Usage Examples

### 1. FAQ API Endpoint

You can interact with the API to get FAQ data by querying the `/api/faqs/` endpoint.

#### Example 1: Get FAQs in English (default)

```bash
GET http://localhost:8000/api/faqs/
```

#### Example 2: Get FAQs in Hindi

```bash
GET http://localhost:8000/api/faqs/?lang=hi
```

#### Example 3: Get FAQs in Bengali

```bash
GET http://localhost:8000/api/faqs/?lang=bn
```

#### Example Response

```json
[
    {
        "id": 1,
        "question": "What is Django?",
        "answer": "Django is a web framework.",
        "question_hi": "डjango क्या है?",
        "question_bn": "ডjango কী?",
        "answer_hi": "Django एक वेब फ्रेमवर्क है।",
        "answer_bn": "Django একটি ওয়েব ফ্রেমওয়ার্ক।"
    }
]
```

---

## Contribution Guidelines

We welcome contributions to the FAQ project! Here’s how you can contribute:

1. Fork the repository.
2. Clone your fork locally.
3. Create a new branch (`git checkout -b feature-xyz`).
4. Implement your changes.
5. Run tests and ensure everything works correctly.
6. Commit your changes with clear commit messages.
7. Push your changes (`git push origin feature-xyz`).
8. Create a pull request.

### Code Style
- Follow **PEP8** guidelines for Python code.
- Ensure that your code passes **flake8** linting:

```bash
flake8 .
```

---

## Git & Version Control

### Commit Message Convention

Use conventional commit messages to keep the history clear and maintainable. Here are some examples:

- **feat**: Add multilingual FAQ model
- **fix**: Improve translation caching
- **docs**: Update README with API examples
- **style**: Format code to comply with PEP8
- **test**: Add unit tests for FAQ model
- **refactor**: Refactor translation function for better performance

### Example:

```bash
git commit -m "feat: Add multilingual FAQ model"
```

---

## Deployment & Docker Support

### Dockerize the Application

#### 1. Create a `Dockerfile`

Create a `Dockerfile` in the root of your project directory:

```Dockerfile
# Use the official Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run Django migrations
RUN python manage.py migrate

# Start the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

#### 2. Create a `docker-compose.yml`

Create a `docker-compose.yml` file:

```yaml
version: '3'

services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=path/to/google_credentials.json
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - redis

  redis:
    image: "redis:alpine"
    ports:
      - "6379:6379"
```

### 3. Build and Run the Docker Containers

```bash
docker-compose up --build
```

This will:
- Build the application Docker image.
- Set up Redis.
- Start the Django server.

You can now access your application at `http://localhost:8000`.

---

## Future Deployment

### Deploy to Heroku (Optional)

1. **Install Heroku CLI**: [Heroku CLI Installation](https://devcenter.heroku.com/articles/heroku-cli)
2. **Login to Heroku**:  
   ```bash
   heroku login
   ```
3. **Create a Heroku app**:  
   ```bash
   heroku create faq-project
   ```
4. **Add Redis to the app**:  
   ```bash
   heroku addons:create heroku-redis:hobby-dev
   ```
5. **Push the code to Heroku**:  
   ```bash
   git push heroku main
   ```
6. **Run migrations on Heroku**:  
   ```bash
   heroku run python manage.py migrate
   ```
7. **Open the app**:  
   ```bash
   heroku open
   ```

---

### **AWS Deployment (Optional)**

1. **Create an EC2 Instance** (Ubuntu recommended).
2. **Install Docker** on EC2.
3. **Deploy the Docker container** on EC2 as per the above Docker setup.
4. **Set up a domain** and connect it to your EC2 instance using Route 53.

---

## Conclusion

You have successfully set up an FAQ management system with multilingual support using **Django**, **Django REST Framework**, and **django-ckeditor**. You've also implemented caching using **Redis**, added automatic translation, and prepared the application for deployment using Docker.

---

Feel free to enhance this further or deploy it to platforms like **Heroku** or **AWS** as per your future plans!
