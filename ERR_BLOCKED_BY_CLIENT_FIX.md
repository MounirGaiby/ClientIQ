# 🛠 ERR_BLOCKED_BY_CLIENT Troubleshooting Guide

## 📋 Quick Fix Steps

### 1. **Disable Browser Extensions (Recommended)**
```
1. Open browser settings
2. Go to Extensions/Add-ons
3. Temporarily disable:
   - Ad blockers (uBlock Origin, AdBlock Plus)
   - Privacy extensions (Ghostery, Privacy Badger)
   - Security extensions
   - VPN extensions
4. Refresh the login page
```

### 2. **Try Incognito/Private Mode**
```
- Chrome: Ctrl+Shift+N (Cmd+Shift+N on Mac)
- Firefox: Ctrl+Shift+P (Cmd+Shift+P on Mac)
- Safari: Cmd+Shift+N
- Edge: Ctrl+Shift+N
```

### 3. **Whitelist the Domain**
If using uBlock Origin or similar:
```
1. Click the extension icon
2. Click the power button to disable for this site
3. Add *.localhost to whitelist
4. Refresh the page
```

## 🔧 Technical Fixes Applied

### Django CORS Configuration
```python
# Added to settings_simple.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://acme.localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
```

### Next.js API Proxy Routes
```
✅ /api/auth/login -> Django /api/v1/auth/login/
✅ /api/auth/me -> Django /api/v1/auth/me/
✅ /api/auth/refresh -> Django /api/v1/auth/refresh/
```

### Email-to-Username Mapping
```typescript
const emailToUsername = {
  'admin@acmecorp.com': 'acme_admin',
  'sarah.johnson@acmecorp.com': 'sarah_manager',
  'mike.wilson@acmecorp.com': 'mike_user',
  'emily.davis@acmecorp.com': 'emily_user'
};
```

## 🔍 How It Works

### The Authentication Flow:
1. **User enters email**: `admin@acmecorp.com`
2. **Email mapped to username**: `acme_admin`
3. **Request sent via proxy**: Frontend → Next.js API → Django
4. **Django authenticates**: Username/password validation
5. **JWT tokens returned**: Access & refresh tokens
6. **User logged in**: Tokens stored, user data fetched

### Why This Fixes ERR_BLOCKED_BY_CLIENT:
- **No direct API calls**: Uses Next.js proxy instead
- **Same-origin requests**: Frontend calls its own API routes
- **Proper CORS headers**: Django configured for cross-origin
- **Extension-friendly**: Proxied requests bypass common blocking

## 🧪 Test the Fix

### 1. Quick Test (CLI)
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"acme_admin","password":"AcmeAdmin123!"}'
```

### 2. Browser Test
1. Go to `http://acme.localhost:3000/login`
2. Enter: `admin@acmecorp.com` / `AcmeAdmin123!`
3. Should see successful login

### 3. Debug Console
```javascript
// Check if proxy is working
fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'acme_admin',
    password: 'AcmeAdmin123!'
  })
}).then(r => r.json()).then(console.log);
```

## 🆘 If Still Not Working

### Alternative Browsers
- Try different browsers (Chrome, Firefox, Safari, Edge)
- Use browser with no extensions installed

### Network Issues
```bash
# Check if ports are accessible
curl http://localhost:3000/api/auth/login
curl http://localhost:8000/api/v1/auth/login/
```

### Reset Browser Data
```
1. Clear cookies and site data for localhost
2. Clear browser cache
3. Restart browser completely
```

### Development Mode
```bash
# Start with fresh servers
pkill -f "next\|python.*manage.py"
cd /root/projects/ClientIQ
source .venv/bin/activate
cd backend && python manage.py runserver 0.0.0.0:8000 &
cd ../frontend && npm run dev &
```

## 📞 Still Need Help?

Check the browser's Developer Tools:
1. **Network tab**: See if requests are being made
2. **Console tab**: Look for specific error messages
3. **Application tab**: Check if tokens are stored

The system should now work with most browser configurations! 🎉
