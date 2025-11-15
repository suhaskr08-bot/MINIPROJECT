# 🌟 InstaFilter - Instagram-like Social Media with Toxicity Detection

A full-stack social media application featuring Instagram-like UI with intelligent toxicity filtering for comments using multilingual ML models.

## 📋 Project Overview

**Backend:** Flask REST API with SQLite database  
**Frontend:** React + Vite + TailwindCSS  
**AI/ML:** Hugging Face Transformers (multilingual-toxic-xlm-roberta)

### Key Features
- 🔐 Auto-create accounts on first login
- 📸 Upload posts with image URLs
- ❤️ Like/unlike posts with real-time counts
- 💬 Comment system with toxicity detection
- ⚠️ Warning modals for sensitive content
- 🎭 Comment masking (author sees original, others see masked)
- 📱 Fully responsive Instagram-inspired design

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+**
- **Node.js 16+**
- Internet connection (for first-time model download)

### 1️⃣ Setup Backend

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
. .venv/Scripts/Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run backend server
python app.py
```

Backend runs at: **http://localhost:5000**

### 2️⃣ Setup Frontend

Open a **new terminal window**:

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs at: **http://localhost:3000**

---

## 📁 Project Structure

```
Insta-toxic/
├── backend/
│   ├── app.py              # Flask API with all endpoints
│   ├── requirements.txt    # Python dependencies
│   ├── data.sqlite         # SQLite database (auto-created)
│   └── README.md          # Backend documentation
│
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── utils/          # Auth helpers
│   │   └── api.js          # API service layer
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── README.md          # Frontend documentation
│
└── README.md              # This file
```

---

## 🔌 API Endpoints

### Authentication
- `POST /login` - Login or auto-create account

### Posts
- `POST /upload_post` - Upload a new post
- `GET /feed/<username>` - Get posts from other users
- `GET /profile/<username>` - Get user's own posts
- `POST /like` - Toggle like on a post

### Comments
- `POST /comment` - Post comment (with toxicity check)
- `GET /comments/<post_id>?viewer=<username>` - Get comments with masking

### Health
- `GET /health` - Health check
- `GET /` - API info

---

## 🧠 How Toxicity Detection Works

1. **Model:** Uses `unitary/multilingual-toxic-xlm-roberta`
   - Supports English, Kannada, Hindi, Tamil, and more
   - Detects toxic content with confidence scores

2. **Custom Word List:** Checks for transliterated Kannada words:
   - `["moorka", "mad", "stupid", "hate", "kill", "useless"]`

3. **Flow:**
   - User submits comment
   - Backend analyzes with model + custom list
   - If toxic → warning modal appears
   - User can confirm or cancel
   - If confirmed → saved with masked version

4. **Masking Logic:**
   - Author always sees original text
   - Others see masked version (toxic words replaced with `*`)

---

## 🎨 Frontend Pages

### Login Page (`/login`)
- Username + password inputs
- Auto-creates account if username doesn't exist
- Redirects to feed on success

### Feed Page (`/feed`)
- View posts from all other users
- Like/unlike with heart icon
- Add comments with toxicity detection
- Real-time updates

### Profile Page (`/profile`)
- Upload new posts (image URL + caption)
- View your posts in grid layout
- Responsive: 2 columns (mobile), 3 columns (desktop)

---

## 🛠️ Tech Stack

### Backend
- **Flask** - Web framework
- **Flask-CORS** - CORS handling
- **SQLite** - Database
- **Transformers** - Hugging Face ML models
- **PyTorch** - Model inference
- **Werkzeug** - Password hashing

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **React Router** - Routing
- **Axios** - HTTP client
- **Tailwind CSS** - Styling

---

## 📊 Database Schema

### users
- `id` (PK), `username` (unique), `password` (hashed)

### posts
- `id` (PK), `user_id` (FK), `image_url`, `caption`, `created_at`

### comments
- `id` (PK), `post_id` (FK), `user_id` (FK), `text`, `masked_text`, `created_at`

### likes
- `id` (PK), `post_id` (FK), `user_id` (FK), `created_at`
- Unique constraint on `(post_id, user_id)` for toggle behavior

---

## 🧪 Testing the App

1. **Start both servers** (backend on 5000, frontend on 3000)

2. **Open browser:** http://localhost:3000

3. **Create account:**
   - Enter username: `alice`, password: `test123`
   - Click "Login / Create Account"

4. **Upload a post:**
   - Go to Profile page
   - Enter image URL: `https://picsum.photos/600/600?random=1`
   - Caption: "My first post!"
   - Click "Upload Post"

5. **Test in another browser/incognito:**
   - Login as `bob` / `test123`
   - You'll see Alice's post in your feed
   - Try liking it
   - Add a clean comment: "Nice photo!"
   - Try a toxic comment: "You are stupid"
   - See the warning modal appear

6. **Verify masking:**
   - Bob sees masked version of toxic comments
   - Alice (author) sees original text

---

## ⚙️ Configuration

### Backend Port
Change in `backend/app.py` or set environment variable:
```powershell
$env:PORT = "8000"
python app.py
```

### Frontend Proxy
Edit `frontend/vite.config.js` to change backend URL:
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:5000',  // Change this
    ...
  }
}
```

### Custom Toxic Words
Edit `CUSTOM_TOXIC_WORDS` set in `backend/app.py`:
```python
CUSTOM_TOXIC_WORDS = {
    "moorka", "mad", "stupid", "hate", "kill", "useless",
    # Add your custom words here
}
```

---

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000
# Kill it
taskkill /PID <PID> /F
```

**Model download fails:**
- Ensure internet connection
- First comment may take 1-2 minutes to download model (~500MB)
- Check Hugging Face status: https://status.huggingface.co

**Database locked:**
```powershell
# Delete and restart
rm backend/data.sqlite
python backend/app.py
```

### Frontend Issues

**npm install fails:**
```powershell
# Clear cache and retry
npm cache clean --force
rm -r node_modules
npm install
```

**Blank page after login:**
- Check browser console for errors
- Verify backend is running and accessible
- Clear localStorage: `localStorage.clear()` in console

**CORS errors:**
- Ensure Flask-CORS is installed
- Check backend console for request logs

---

## 🚀 Production Deployment

### Backend
1. Use production WSGI server (Gunicorn, uWSGI)
2. Switch to PostgreSQL/MySQL for production
3. Add environment-based config
4. Enable HTTPS
5. Set up model caching

### Frontend
```powershell
cd frontend
npm run build
# Serve dist/ folder with nginx or similar
```

---

## 📝 Future Enhancements

- [ ] Image upload (not just URLs)
- [ ] User profile pictures
- [ ] Edit/delete posts
- [ ] Search users/posts
- [ ] Notifications
- [ ] Dark mode
- [ ] Pagination
- [ ] Direct messaging
- [ ] Stories feature
- [ ] Video support

---

## 📄 License

MIT License - Feel free to use this project for learning or commercial purposes.

---

## 🙏 Acknowledgments

- **Unitary AI** - For the multilingual toxic comment classifier model
- **Instagram** - For UI/UX inspiration
- **Hugging Face** - For the Transformers library

---

## 📞 Support

For issues or questions:
1. Check the READMEs in `backend/` and `frontend/` folders
2. Review error messages in browser console and terminal
3. Ensure both servers are running on correct ports

---

**Happy Coding! 🎉**
