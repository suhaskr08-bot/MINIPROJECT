# InstaFilter Startup Guide

## 🚀 Quick Start (Windows PowerShell)

### Terminal 1 - Backend
```powershell
cd backend
. .venv\Scripts\Activate.ps1
python app.py
```
Wait for: `Running on http://127.0.0.1:5000`

### Terminal 2 - Frontend
```powershell
cd frontend
npm run dev
```
Wait for: `Local: http://localhost:3000`

### Open Browser
Navigate to: http://localhost:3000

---

## ✅ First Time Setup

### Backend Setup (One-time)
```powershell
cd backend
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend Setup (One-time)
```powershell
cd frontend
npm install
```

---

## 🧪 Quick Test Flow

1. **Login/Register:**
   - Username: `testuser`
   - Password: `password123`
   - Click "Login / Create Account"

2. **Upload Post (Profile page):**
   - Image URL: `https://picsum.photos/600/600`
   - Caption: "Test post"
   - Click "Upload Post"

3. **Test in another browser (incognito):**
   - Login as different user: `user2` / `password123`
   - View feed - see testuser's post
   - Like the post (heart turns red)
   - Comment: "Nice!" (clean - posts immediately)
   - Comment: "You are stupid" (toxic - shows warning)

4. **Verify masking:**
   - Login back as `testuser`
   - See your original comment
   - Other users see masked version

---

## 📦 Project Files Created

### Backend (d:/Insta-toxic/backend/)
- ✅ app.py - Flask API with 8 endpoints
- ✅ requirements.txt - Python dependencies
- ✅ __init__.py - Package marker
- ✅ README.md - Backend docs
- ✅ data.sqlite - Auto-created on first run

### Frontend (d:/Insta-toxic/frontend/)
- ✅ src/api.js - API service layer
- ✅ src/utils/auth.js - Auth helpers
- ✅ src/App.jsx - Root component
- ✅ src/main.jsx - Entry point
- ✅ src/index.css - Global styles
- ✅ src/components/
  - Navbar.jsx
  - ProtectedRoute.jsx
  - PostCard.jsx
  - ToxicityModal.jsx
- ✅ src/pages/
  - LoginPage.jsx
  - FeedPage.jsx
  - ProfilePage.jsx
- ✅ index.html
- ✅ package.json
- ✅ vite.config.js - Dev server + proxy
- ✅ tailwind.config.js - Custom colors
- ✅ postcss.config.js
- ✅ .gitignore
- ✅ README.md - Frontend docs

### Root
- ✅ README.md - Complete project documentation

---

## 🎯 Features Implemented

### ✅ Backend Features
- [x] POST /login - Auto-create accounts
- [x] POST /upload_post - Upload posts
- [x] GET /feed/<username> - Get other users' posts
- [x] GET /profile/<username> - Get user's posts
- [x] POST /like - Toggle likes
- [x] POST /comment - Comment with toxicity check
- [x] GET /comments/<post_id> - Fetch comments with masking
- [x] SQLite database with 4 tables
- [x] Password hashing (werkzeug)
- [x] Toxicity detection (Hugging Face + custom words)
- [x] Comment masking logic
- [x] CORS enabled

### ✅ Frontend Features
- [x] Login/Register page
- [x] Feed page with post cards
- [x] Profile page with upload form
- [x] Navbar with navigation
- [x] Protected routes
- [x] Like/unlike functionality
- [x] Comment system
- [x] Toxicity warning modal
- [x] Responsive design (mobile-first)
- [x] Instagram-inspired UI
- [x] Real-time like count updates
- [x] Error handling with user-friendly messages
- [x] Loading states
- [x] LocalStorage session management

---

## 🔧 Troubleshooting

### Backend won't start
```powershell
# Check if port 5000 is free
netstat -ano | findstr :5000

# If occupied, kill the process
taskkill /PID <PID_NUMBER> /F
```

### Frontend won't start
```powershell
# Clear node_modules and reinstall
Remove-Item -Recurse -Force node_modules
npm install
```

### Can't login
- Check backend terminal for errors
- Verify backend is running on port 5000
- Open browser DevTools > Network tab
- Look for failed requests

### Images not loading
- Check image URLs are valid and accessible
- Use placeholder images: `https://picsum.photos/600/600`

### Toxicity model download stuck
- First comment takes 1-2 minutes to download model
- Check internet connection
- Backend logs show download progress
- Model cached after first download

---

## 📝 Next Steps

1. ✅ Backend complete with all endpoints
2. ✅ Frontend complete with all pages
3. ✅ Documentation complete
4. 🎯 Test the full flow
5. 🎯 Deploy to production (optional)

---

## 🎉 You're All Set!

Your Instagram-like social media app with AI-powered toxicity detection is ready to use!

**Enjoy building and experimenting! 🚀**
