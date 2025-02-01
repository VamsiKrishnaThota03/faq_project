Sample Images:
![Screenshot at 10:52:01 PM](images/Screenshot%202025-02-01%20at%2010.52.01%20PM.png)

![Screenshot at 10:58:05 PM](images/Screenshot%202025-02-01%20at%2010.58.05%20PM.png)

![Screenshot at 11:03:22 PM](images/Screenshot%202025-02-01%20at%2011.03.22%20PM.png)


# FAQ Project

This project is designed to manage FAQs with multilingual support using Django, Django REST Framework, and `django-ckeditor` for WYSIWYG editor integration. It includes automatic translations for FAQs using the `deep-translator` API and implements Redis caching for efficient API responses.

## Table of Contents
1. [Installation Steps](#installation-steps)
2. [API Usage Examples](#api-usage-examples)
3. [Contribution Guidelines](#contribution-guidelines)

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

I welcome contributions to the FAQ project! Here’s how you can contribute:

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


