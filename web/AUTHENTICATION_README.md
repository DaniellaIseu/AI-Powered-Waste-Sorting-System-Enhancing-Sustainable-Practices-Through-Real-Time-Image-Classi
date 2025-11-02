# Authentication Setup Guide

This application uses Auth0 for user authentication. Follow these steps to set up authentication.

## Prerequisites

- An Auth0 account (sign up at [auth0.com](https://auth0.com))
- Python environment with Flask installed

## Setup Steps

### 1. Create Auth0 Application

1. Log in to your [Auth0 Dashboard](https://manage.auth0.com)
2. Navigate to **Applications** → **Applications**
3. Click **Create Application**
4. Choose **Regular Web Applications** as the application type
5. Click **Create**

### 2. Configure Auth0 Application

In your Auth0 application settings:

1. **Allowed Callback URLs**: Add your callback URL
   - Development: `http://localhost:5000/callback`
   - Production: `https://yourdomain.com/callback`

2. **Allowed Logout URLs**: Add your logout URL
   - Development: `http://localhost:5000/`
   - Production: `https://yourdomain.com/`

3. **Allowed Web Origins**: Add your application URL
   - Development: `http://localhost:5000`
   - Production: `https://yourdomain.com`

4. Click **Save Changes**

### 3. Get Auth0 Credentials

From your Auth0 application page, copy:
- **Domain** (e.g., `dev-example.us.auth0.com`)
- **Client ID**
- **Client Secret**

### 4. Configure Environment Variables

1. Copy `env_template.txt` to `.env` in the web folder
2. Fill in your Auth0 credentials:
   ```
   AUTH0_DOMAIN=your-auth0-domain.us.auth0.com
   AUTH0_CLIENT_ID=your-auth0-client-id
   AUTH0_CLIENT_SECRET=your-auth0-client-secret
   SECRET_KEY=your-generated-secret-key
   ```

3. Generate a secure SECRET_KEY:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python app.py
```

Navigate to `http://localhost:5000` and click "Login with Auth0"

## Authentication Flow

1. User clicks **Login**
2. Redirected to Auth0 login page
3. User authenticates (social login, email/password, etc.)
4. Auth0 redirects back to `/callback` with authorization code
5. Application exchanges code for user info
6. User session is created
7. User is redirected to dashboard

## Features

- **Secure authentication** via Auth0
- **Multiple login methods** (social, email, password)
- **User profile management**
- **Session management**
- **Secure logout**

## Troubleshooting

### "Callback URL mismatch" error
- Verify your callback URL in Auth0 matches exactly what's in your code
- Check for trailing slashes

### "Invalid client secret" error
- Verify your `.env` file has the correct Client Secret
- Make sure there are no extra spaces or quotes

### Session not persisting
- Check that SECRET_KEY is set in `.env`
- Verify Flask session configuration

## Security Notes

- Never commit your `.env` file to version control
- Keep your Client Secret secure
- Use HTTPS in production
- Regularly rotate secrets

## Additional Resources

- [Auth0 Documentation](https://auth0.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Authlib Documentation](https://docs.authlib.org/)

