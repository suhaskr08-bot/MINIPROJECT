# InstaFilter Frontend

A modern, responsive Instagram-like React application with toxicity filtering for comments.

## Features

### 🔐 Authentication
- Login/Register page with automatic account creation
- Username stored in localStorage for session persistence
- Protected routes requiring authentication

### 📱 Feed Page
- View posts from all other users
- Like posts with real-time count updates
- Comment on posts with toxicity detection
- Toxicity warning modal for sensitive content
- Responsive single-column layout

### 👤 Profile Page
- Upload new posts (image URL + caption)
- View your own posts in a responsive grid (2 cols mobile, 3 cols desktop)
- Post count display

### 🎨 UI/UX
- Instagram-inspired design with Tailwind CSS
- Mobile-first responsive layout
- Gradient color scheme (purple, pink, blue)
- Smooth transitions and hover effects
- Fixed navbar with icons

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool & dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first styling

## Setup Instructions

### Prerequisites
- Node.js 16+ installed
- Backend server running on http://localhost:5000

### Installation (Windows PowerShell)

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will open at http://localhost:3000

### Build for Production

```powershell
npm run build
```

Built files will be in the `dist/` folder.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Navbar.jsx           # Top navigation bar
│   │   ├── ProtectedRoute.jsx   # Auth wrapper component
│   │   ├── PostCard.jsx         # Individual post with likes/comments
│   │   └── ToxicityModal.jsx    # Warning modal for toxic comments
│   ├── pages/
│   │   ├── LoginPage.jsx        # Login/Register page
│   │   ├── FeedPage.jsx         # Main feed view
│   │   └── ProfilePage.jsx      # User profile with upload
│   ├── utils/
│   │   └── auth.js              # LocalStorage auth helpers
│   ├── api.js                   # Axios API service layer
│   ├── App.jsx                  # Root component with routes
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles + Tailwind
├── index.html
├── package.json
├── vite.config.js               # Vite config with proxy
├── tailwind.config.js           # Tailwind theme config
└── postcss.config.js
```

## API Integration

All API calls go through `src/api.js`:

- `authAPI.login(username, password)`
- `postAPI.getFeed(username)`
- `postAPI.getProfile(username)`
- `postAPI.uploadPost(username, image_url, caption)`
- `postAPI.likePost(username, post_id)`
- `commentAPI.postComment(username, post_id, text, confirm)`
- `commentAPI.getComments(post_id, viewer)`

### Proxy Configuration
Vite proxies `/api/*` requests to `http://localhost:5000` (see `vite.config.js`).

## Key Features Explained

### Toxicity Detection Flow
1. User submits a comment
2. Backend analyzes text using ML model + custom word list
3. If toxic:
   - Modal shows warning with score
   - User can confirm or cancel
   - If confirmed, comment is posted with masking
4. If clean:
   - Comment posted immediately

### Comment Masking
- Commenter always sees their original text
- Others see masked version (toxic words replaced with `*`)
- Backend handles masking logic via `/comments/<post_id>?viewer=<username>`

### Like Toggle
- Click heart to like/unlike
- Color changes to red when liked
- Count updates in real-time

## Development Tips

### Hot Reload
Vite provides instant hot module replacement. Changes appear immediately without full page refresh.

### Styling with Tailwind
Use utility classes directly in JSX:
```jsx
<div className="bg-gradient-to-r from-insta-purple to-insta-pink text-white">
```

Custom colors defined in `tailwind.config.js`:
- `insta-pink`: #E1306C
- `insta-purple`: #C13584
- `insta-blue`: #405DE6

### Error Handling
All API calls include try-catch blocks with user-friendly error messages displayed in red alert boxes.

## Troubleshooting

### Backend Connection Issues
- Ensure backend is running on port 5000
- Check CORS is enabled in Flask (Flask-CORS)
- Verify API endpoint URLs in `src/api.js`

### Build Errors
If you see Tailwind errors during build, ensure PostCSS is configured correctly.

### Login Not Persisting
Clear localStorage and try again:
```javascript
localStorage.clear()
```

## Future Enhancements
- Edit/delete posts
- User profile pictures
- Search functionality
- Notifications
- Dark mode
- Image upload (not just URLs)
- Pagination for feed

## License
MIT
