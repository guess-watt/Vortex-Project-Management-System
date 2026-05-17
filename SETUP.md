# Django Accounts App Setup

## Installation Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/accounts/auth/register/` - Register new user
- `POST /api/accounts/auth/login/` - Login user (returns JWT tokens)

### User Management
- `GET /api/accounts/users/me/` - Get current user profile
- `PUT/PATCH /api/accounts/users/update_profile/` - Update current user profile
- `GET /api/accounts/users/search/?q=query` - Search users by username or email
- `GET /api/accounts/users/` - List all users (admin)
- `GET /api/accounts/users/{id}/` - Get user by ID
- `PUT/PATCH /api/accounts/users/{id}/` - Update user (admin)
- `DELETE /api/accounts/users/{id}/` - Delete user (admin)

## Request Examples

### Register
```json
POST /api/accounts/auth/register/
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "bio": "Software Developer",
  "role": "member"
}
```

### Login
```json
POST /api/accounts/auth/login/
{
  "email": "john@example.com",
  "password": "securepass123"
}
```

### Update Profile
```json
PUT /api/accounts/users/update_profile/
Authorization: Bearer <access_token>
{
  "bio": "Senior Software Developer",
  "profile_image": "https://example.com/image.jpg"
}
```

### Search Users
```
GET /api/accounts/users/search/?q=john
Authorization: Bearer <access_token>
```

## Authentication

All endpoints except register and login require JWT authentication.

Add to request headers:
```
Authorization: Bearer <access_token>
```

## Settings Changes Applied

- Custom User model: `AUTH_USER_MODEL = 'accounts.User'`
- JWT authentication configured
- REST Framework settings added
- `rest_framework_simplejwt` added to INSTALLED_APPS