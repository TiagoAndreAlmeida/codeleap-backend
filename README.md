# CodeLeap Backend Challenge

This is a robust, scalable, and secure Django-based API for a social media platform, featuring Firebase Authentication, PostgreSQL database, and Docker containerization.

**Live API:** [https://codeleap-api.upafiliado.com.br/](https://codeleap-api.upafiliado.com.br/)

## 🚀 Features

- **Firebase Authentication**: Integrated with Google Login. The backend validates tokens and automatically provisions users.
- **Social Core**: Complete CRUD for Posts and Comments.
- **Interactions**: Atomic "Like" system with high-concurrency safety.
- **Performance**: Denormalized counters (`likes_count`, `comments_count`) using `F()` expressions to ensure database efficiency.
- **Soft Delete**: Posts and comments are never physically deleted from the database.
  - **Reasoning**: This ensures data integrity and preserves historical records for auditing, analytics, and legal compliance (e.g., investigating reported content or fulfilling legal requests). Items are simply filtered out from the API results via the `deleted=True` flag.
- **Ownership Security**: Strict permissions ensuring only authors can modify their content.
- **Scalable Pagination**: Global pagination set to 10 items per page.
- **Dockerized**: Ready for development and production with Docker Compose.
- **Full Test Suite**: Comprehensive unit tests with Firebase mocking.

---

## ⚡ Database Optimization

To ensure high performance and scalability under heavy load, several optimization techniques were applied:

- **Denormalized Counters**: `likes_count` and `comments_count` are stored directly on the `Post` model. This eliminates the need for expensive `COUNT(*)` queries during feed listing, resulting in `O(1)` read performance for these metrics.
- **Atomic F() Expressions**: All counter updates use Django's `F()` expressions. This ensures that increments and decrements happen at the database level (SQL), preventing race conditions and ensuring data consistency even with multiple concurrent requests.
- **Composite Indexing**: 
  - A composite index was added for `[post_id, created_datetime]` in the `Comment` model to ensure that fetching paginated comments for a specific post is near-instant.
  - A unique index for `[user_id, post_id]` in the `Like` model ensures database-level integrity and fast lookup for like states.
- **Soft Delete Filtering**: Optimized queries ensure that deleted items are filtered out efficiently at the database level.

---

## 🛠️ Tech Stack

- **Backend**: Django 6.0+, Django REST Framework (DRF)
- **Database**: PostgreSQL 16
- **Auth**: Firebase Admin SDK
- **DevOps**: Docker, Docker Compose
- **Testing**: Django APITestCase (Unit Testing)

---

## ⚙️ Setup Instructions

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.12 (if running locally)

### 2. Environment Variables
Copy the template and fill in your credentials:
```bash
cp .env.example .env
```

### 3. Firebase Configuration
1. Go to your **Firebase Console** -> **Project Settings** -> **Service Accounts**.
2. Click **Generate new private key** and download the JSON file.
3. Rename it to `firebase-service-account.json` and place it in the **root directory** of this project.

### 4. Running with Docker (Recommended)
Build and start the containers:
```bash
docker-compose up --build
```
The API will be available at `http://localhost:8000/api/v1/careers/`.

---

## 📖 API Documentation

### Authentication
All requests (except Admin) require a Firebase ID Token in the header:
`Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>`

### Main Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/api/v1/careers/` | List all posts (paginated). |
| **POST** | `/api/v1/careers/` | Create a new post. |
| **PATCH** | `/api/v1/careers/{id}/` | Update your own post. |
| **DELETE** | `/api/v1/careers/{id}/` | Soft delete your own post. |
| **POST** | `/api/v1/careers/{id}/like/` | Toggle like/unlike on a post. |
| **GET** | `/api/v1/careers/{id}/comments/` | List comments for a post. |
| **POST** | `/api/v1/careers/{id}/comments/` | Add a comment to a post. |
| **PATCH** | `/api/v1/comments/{id}/` | Edit your own comment. |
| **DELETE** | `/api/v1/comments/{id}/` | Soft delete your own comment. |

---

## 🧪 Running Tests

To run the full test suite (including Firebase auth mocks):
```bash
# Inside Docker
docker-compose exec web python manage.py test

# Locally
python manage.py test
```

---

## 🔒 Security Notes
- `DEBUG` should be set to `False` in production.
- `CORS_ALLOW_ALL_ORIGINS` is enabled for development but should be restricted in production.
- The `firebase-service-account.json` and `.env` files are ignored by Git for your safety.
