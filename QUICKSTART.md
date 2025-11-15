# 🚀 InstaFilter - Quick Reference

## Start Servers

### Backend (Terminal 1)
```powershell
cd backend
. .venv\Scripts\Activate.ps1
python app.py
```
**URL:** http://localhost:5000

### Frontend (Terminal 2)
```powershell
cd frontend
npm run dev
```
**URL:** http://localhost:3000

---

## API Quick Reference

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| POST | `/login` | `{username, password}` | `{message: "Login successful"}` |
| POST | `/upload_post` | `{username, image_url, caption}` | `{message: "Post uploaded", post_id}` |
| GET | `/feed/<username>` | - | `{posts: [...]}` |
| GET | `/profile/<username>` | - | `{posts: [...]}` |
| POST | `/like` | `{username, post_id}` | `{likes: 15}` |
| POST | `/comment` | `{username, post_id, text, confirm}` | `{status, message}` or `{message: "Comment posted"}` |
| GET | `/comments/<post_id>` | `?viewer=<username>` | `{comments: [...]}` |

---

## Routes

| Path | Component | Protected | Description |
|------|-----------|-----------|-------------|
| `/login` | LoginPage | ❌ | Login/Register |
| `/feed` | FeedPage | ✅ | View all posts |
| `/profile` | ProfilePage | ✅ | Upload & view own posts |
| `/` | Redirect | - | → `/feed` |

---

## Keyboard Shortcuts (Dev)

| Key | Action |
|-----|--------|
| `Ctrl+C` | Stop server |
| `Ctrl+Shift+C` | Open DevTools |
| `F5` | Reload page |
| `Ctrl+Shift+R` | Hard reload |

---

## Test Users

```
Username: alice    Password: test123
Username: bob      Password: test123
Username: charlie  Password: test123
```

---

## Test Data

### Sample Image URLs
```
https://picsum.photos/600/600?random=1
https://picsum.photos/600/600?random=2
https://picsum.photos/600/600?random=3
```

### Clean Comments
```
"Beautiful photo!"
"Love this!"
"Amazing view 😍"
```

### Toxic Comments (will trigger warning)
```
"You are stupid"
"I hate this"
"This is useless"
```

---

## File Locations

```
d:/Insta-toxic/
├── backend/
│   ├── app.py              ← Main Flask app
│   ├── data.sqlite         ← Database (auto-created)
│   └── requirements.txt    ← Python deps
│
├── frontend/
│   ├── src/
│   │   ├── api.js          ← API calls
│   │   ├── App.jsx         ← Routes
│   │   ├── components/     ← Reusable components
│   │   └── pages/          ← Page components
│   └── package.json        ← Node deps
│
└── README.md               ← Full documentation
```

---

## Common Commands

### Python (Backend)
```powershell
# Activate venv
. .venv\Scripts\Activate.ps1

# Install deps
pip install -r requirements.txt

# Run app
python app.py

# Check Python version
python --version
```

### Node (Frontend)
```powershell
# Install deps
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Check Node version
node --version
```

---

## Troubleshooting Quick Fixes

### Backend won't start
```powershell
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Frontend won't start
```powershell
# Reinstall dependencies
Remove-Item -Recurse -Force node_modules
npm install
```

### Database issues
```powershell
# Delete and restart
Remove-Item backend\data.sqlite
cd backend
python app.py
```

### Clear browser cache
```javascript
// In browser console
localStorage.clear()
location.reload()
```

---

## Environment Variables

### Backend
```powershell
$env:PORT = "5000"           # Flask port
$env:FLASK_DEBUG = "1"       # Debug mode
```

### Frontend
Edit `vite.config.js` for backend URL

---

## Ports

| Service | Port | URL |
|---------|------|-----|
| Backend | 5000 | http://localhost:5000 |
| Frontend | 3000 | http://localhost:3000 |

---

## Model Info

**Name:** `unitary/multilingual-toxic-xlm-roberta`  
**Size:** ~500MB  
**Languages:** English, Hindi, Kannada, Tamil, Telugu, and more  
**First run:** Downloads model (1-2 minutes)  
**Cached:** `~/.cache/huggingface/`

---

## Custom Toxic Words

Edit `backend/app.py`:
```python
CUSTOM_TOXIC_WORDS = {
    "moorka", "mad", "stupid", 
    "hate", "kill", "useless"
    # Add your words here
}
```

---

## Git Commands (Optional)

```powershell
# Initialize repo
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Instagram clone with toxicity detection"

# Add remote
git remote add origin <your-repo-url>

# Push
git push -u origin main
```

---

## Production Checklist

- [ ] Use production database (PostgreSQL/MySQL)
- [ ] Set `FLASK_DEBUG=0`
- [ ] Use WSGI server (Gunicorn)
- [ ] Enable HTTPS
- [ ] Set up CORS properly
- [ ] Build frontend: `npm run build`
- [ ] Serve from CDN/nginx
- [ ] Set environment variables
- [ ] Monitor logs
- [ ] Set up backups

---

## Support

**Documentation:**
- `README.md` - Complete guide
- `SETUP.md` - Startup instructions
- `COMPONENTS.md` - Visual guide
- `backend/README.md` - Backend details
- `frontend/README.md` - Frontend details

**Check:**
1. Both servers running?
2. Correct ports (5000, 3000)?
3. Browser console errors?
4. Backend terminal errors?

---

## Quick Test Workflow

```
1. Start backend → http://localhost:5000
2. Start frontend → http://localhost:3000
3. Browser → http://localhost:3000
4. Login: alice / test123
5. Profile → Upload post
6. Incognito → Login: bob / test123
7. Feed → Like alice's post
8. Comment "stupid" → See warning
9. Confirm → Comment masked
10. Login as alice → See original
```

---

**Happy Coding! 🎉**

**Pro tip:** Keep this file open while developing for quick reference!
