# 🔐 Auth0 Authentication - Waste Sorter (Web)

The web dashboard relies exclusively on **Auth0** for authentication. There is no local username/password database, Firebase dependency, or hybrid flow – everything delegates to Auth0’s hosted login page.

## 🚀 Quick Start

1. **Install dependencies**
   ```bash
   cd web
   pip install -r requirements.txt
   ```

2. **Create a `.env` file**
   ```bash
   cp env_template.txt .env
   ```
   Fill in the Auth0 values from your Auth0 tenant:
   ```ini
   AUTH0_DOMAIN=your-domain.auth0.com
   AUTH0_CLIENT_ID=your-client-id
   AUTH0_CLIENT_SECRET=your-client-secret
   SECRET_KEY=your-secure-flask-secret
   ```

3. **Run the Flask app**
   ```bash
   python app.py
   ```

4. **Login flow**
   - User hits `http://localhost:5000`
   - Clicks the “Continue with Auth0” button
   - Auth0 hosts the login / signup experience
   - Auth0 redirects back to `/callback`
   - Successful logins store the Auth0 user profile in the Flask session

## 🔧 Implementation Notes

- `auth0_manager.py` wraps Auth0’s OpenID Connect flow using `authlib`.
- Routes protected with `@login_required` ensure the user is in session.
- There is **no** local database or role management logic – manage roles in the Auth0 dashboard if you need them.
- `logout()` clears the local session and redirects to Auth0’s universal logout.

## 📁 Key Files

- `app.py` – Flask routes (`/`, `/login`, `/callback`, `/dashboard`, `/upload`, `/admin`, `/logout`)
- `auth0_manager.py` – Auth0 OAuth client wrapper
- `templates/` – Tailwind-based pages for index, login, dashboard, admin, upload
- `env_template.txt` – Auth0 configuration placeholders

## ✅ Security Checklist

- Keep `SECRET_KEY` private and random
- Never commit `.env` files
- Configure allowed callback/logout URLs in Auth0
- Use HTTPS in production

## 📱 Mobile App Authentication

The mobile app uses separate API endpoints that work independently of the web OAuth flow:

- **`POST /api/login`** - Authenticate with email/password
- **`POST /api/register`** - Create new user account

These endpoints use:
- Auth0 **Resource Owner Password Grant** for login
- Auth0 **Management API** for user registration

### Mobile Auth Setup

1. **Enable Resource Owner Password Grant in Auth0:**
   - Go to Auth0 Dashboard → Applications → Your App → Settings
   - Scroll to "Advanced Settings" → "Grant Types"
   - Enable "Password" grant type
   - Click "Save Changes"

2. **Enable Management API (for user registration):**
   - The Management API is automatically available
   - No additional setup needed (uses client credentials)

3. **Mobile endpoints format:**

   **Login:**
   ```json
   POST /api/login
   {
     "email": "user@example.com",
     "password": "password123"
   }
   ```

   **Register:**
   ```json
   POST /api/register
   {
     "email": "user@example.com",
     "password": "password123",
     "name": "John Doe"  // optional
   }
   ```

   **Response:**
   ```json
   {
     "access_token": "...",
     "id_token": "...",
     "user": {
       "sub": "auth0|...",
       "name": "John Doe",
       "email": "user@example.com",
       "picture": null
     }
   }
   ```

### Important Notes

- Mobile authentication uses **username/password** flow (different from web OAuth)
- Both systems share the same Auth0 user database
- Users created via mobile can login on web (and vice versa)
- The web OAuth flow (`/login`, `/callback`) remains unchanged

## 🔮 Future Ideas

- Hook Auth0 roles/app_metadata to control access to the admin dashboard
- Connect Auth0 Management API for richer user insights
- Replace the mock classification UI with the real ML model when it’s ready

Your web app now uses a clean, single-auth provider setup powered by Auth0. 🎉

