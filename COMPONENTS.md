# 🎨 InstaFilter - Visual Component Guide

## 📱 App Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      LOGIN PAGE                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │         🎨 InstaFilter                              │     │
│  │   Share moments, filter toxicity                    │     │
│  │                                                      │     │
│  │   ┌────────────────────────────────────────┐       │     │
│  │   │ Username: [____________]               │       │     │
│  │   │ Password: [____________]               │       │     │
│  │   │                                        │       │     │
│  │   │ [  Login / Create Account  ]          │       │     │
│  │   └────────────────────────────────────────┘       │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  New user? Just enter details → Auto-create account!         │
└─────────────────────────────────────────────────────────────┘
                           ↓ (Login Success)
┌─────────────────────────────────────────────────────────────┐
│                    NAVBAR (Fixed Top)                        │
│  ┌────────────────────────────────────────────────────┐     │
│  │ InstaFilter     [🏠 Feed] [👤 Profile] [🚪 Logout] │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        FEED PAGE                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │  👤 alice                                          │     │
│  │  ┌──────────────────────────────────────────┐     │     │
│  │  │                                          │     │     │
│  │  │         [Post Image 600x600]            │     │     │
│  │  │                                          │     │     │
│  │  └──────────────────────────────────────────┘     │     │
│  │  ❤️ 💬                                            │     │
│  │  15 likes                                         │     │
│  │  alice: Beautiful sunset! 🌅                     │     │
│  │                                                    │     │
│  │  bob: Amazing photo!                              │     │
│  │  charlie: Love it!                                │     │
│  │                                                    │     │
│  │  [Add a comment...] [Post]                        │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │  👤 bob                                            │     │
│  │  ┌──────────────────────────────────────────┐     │     │
│  │  │         [Post Image]                     │     │     │
│  │  └──────────────────────────────────────────┘     │     │
│  │  ❤️ 💬                                            │     │
│  │  8 likes                                          │     │
│  │  bob: Check out this view!                        │     │
│  │  ...                                              │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     PROFILE PAGE                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │  👤  alice                                         │     │
│  │      12 posts                                      │     │
│  │                                                    │     │
│  │  Upload New Post                                  │     │
│  │  ┌─────────────────────────────────────────┐     │     │
│  │  │ Image URL: [____________________]       │     │     │
│  │  │ Caption: [_______________________]      │     │     │
│  │  │          [_______________________]      │     │     │
│  │  │          [_______________________]      │     │     │
│  │  │                                         │     │     │
│  │  │        [  Upload Post  ]                │     │     │
│  │  └─────────────────────────────────────────┘     │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  Your Posts                                                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                       │
│  │ [Image] │ │ [Image] │ │ [Image] │                       │
│  └─────────┘ └─────────┘ └─────────┘                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                       │
│  │ [Image] │ │ [Image] │ │ [Image] │                       │
│  └─────────┘ └─────────┘ └─────────┘                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│               TOXICITY WARNING MODAL                         │
│  ┌────────────────────────────────────────────────────┐     │
│  │  ⚠️  Content Warning                               │     │
│  │                                                    │     │
│  │  Your message includes sensitive content:         │     │
│  │  toxic (score: 85%). Do you still want to post?  │     │
│  │                                                    │     │
│  │  [  No, Cancel  ]   [  Yes, Post Anyway  ]       │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Color Scheme

```css
Primary Colors:
- insta-pink:   #E1306C  /* ████ */
- insta-purple: #C13584  /* ████ */
- insta-blue:   #405DE6  /* ████ */

Background:
- bg-gray-50:   #fafafa  /* Light background */
- white:        #ffffff  /* Cards */

Text:
- gray-900:     #111827  /* Primary text */
- gray-700:     #374151  /* Secondary text */
- gray-400:     #9CA3AF  /* Placeholder */

Gradients:
- Logo/Buttons: purple → pink
- Profile pics: purple → pink (diagonal)
```

---

## 📐 Responsive Breakpoints

```
Mobile:      < 768px   (1 column, full width)
Tablet:      768-1024px (2 columns)
Desktop:     > 1024px   (3 columns, centered)

Feed:        Single column (max-w-2xl centered)
Profile:     Grid (2 cols mobile → 3 cols desktop)
```

---

## 🔄 Component Relationships

```
App.jsx
├── BrowserRouter
│   ├── Routes
│   │   ├── /login → LoginPage
│   │   ├── /feed → ProtectedRoute → Navbar + FeedPage
│   │   │                              ├── PostCard (multiple)
│   │   │                              │   ├── Comments
│   │   │                              │   └── ToxicityModal
│   │   ├── /profile → ProtectedRoute → Navbar + ProfilePage
│   │   └── / → Redirect to /feed
```

---

## 🎯 User Interaction Flow

### 1. First Visit
```
Browser → LoginPage
    ↓ Enter username + password
    ↓ Click "Login / Create Account"
API Call: POST /login
    ↓ Success
Save username to localStorage
    ↓
Redirect to /feed
```

### 2. Viewing Feed
```
FeedPage loads
    ↓
API Call: GET /feed/alice
    ↓ Returns posts from bob, charlie, etc.
Render PostCard for each post
    ↓
PostCard loads
    ↓
API Call: GET /comments/{post_id}?viewer=alice
    ↓ Returns comments (masked if toxic)
Display comments
```

### 3. Liking a Post
```
User clicks ❤️
    ↓
API Call: POST /like {username, post_id}
    ↓ Backend toggles like (add or remove)
    ↓ Returns new like count
Update UI: Change color, update count
```

### 4. Commenting (Clean)
```
User types: "Nice photo!"
    ↓ Clicks "Post"
API Call: POST /comment {username, post_id, text, confirm: false}
    ↓ Backend checks toxicity
    ↓ Result: clean
    ↓ Returns: {message: "Comment posted"}
Refresh comments list
```

### 5. Commenting (Toxic)
```
User types: "You are stupid"
    ↓ Clicks "Post"
API Call: POST /comment {username, post_id, text, confirm: false}
    ↓ Backend checks toxicity
    ↓ Result: toxic
    ↓ Returns: {status: "warning", message: "..."}
Show ToxicityModal
    ↓
User clicks "Yes, Post Anyway"
    ↓
API Call: POST /comment {username, post_id, text, confirm: true}
    ↓ Backend saves with masking
    ↓ Returns: {message: "Comment posted"}
Refresh comments list
```

### 6. Uploading Post
```
ProfilePage → Upload form
    ↓ Enter image URL + caption
    ↓ Click "Upload Post"
API Call: POST /upload_post {username, image_url, caption}
    ↓ Backend saves to database
    ↓ Returns: {message: "Post uploaded", post_id: 123}
Show success message
Refresh profile posts grid
```

---

## 🗂️ Data Flow

```
Frontend              Backend              Database
────────              ───────              ────────
localStorage.username
     ↓
API calls with
username in body
                  ↓
              Verify user exists
                  ↓
                         users table
                         posts table
                         comments table
                         likes table
                  ↓
              SQLite queries
                  ↓
              Return JSON
     ↓
Update React state
     ↓
Re-render components
```

---

## 🔐 Auth Flow

```
No localStorage     Has localStorage
      ↓                    ↓
Visit any route      Visit any route
      ↓                    ↓
ProtectedRoute       ProtectedRoute
checks auth          checks auth
      ↓                    ↓
Not authenticated    Authenticated
      ↓                    ↓
Redirect /login      Show Navbar + Page
```

---

## 🧪 Testing Checklist

### ✅ Authentication
- [ ] New user can create account
- [ ] Existing user can login
- [ ] Wrong password shows error
- [ ] Logout clears session
- [ ] Protected routes redirect to login

### ✅ Posts
- [ ] Upload post with image URL
- [ ] Upload post with caption
- [ ] See other users' posts in feed
- [ ] See own posts in profile
- [ ] Posts show in chronological order

### ✅ Likes
- [ ] Like a post (heart turns red)
- [ ] Unlike a post (heart turns gray)
- [ ] Like count updates correctly
- [ ] Multiple users can like same post

### ✅ Comments (Clean)
- [ ] Post clean comment
- [ ] Comment appears immediately
- [ ] Comment shows under post
- [ ] Multiple comments display correctly

### ✅ Comments (Toxic)
- [ ] Post toxic word → Warning modal
- [ ] Click "No, Cancel" → Comment discarded
- [ ] Click "Yes, Post Anyway" → Comment saved
- [ ] Author sees original text
- [ ] Others see masked text (****)

### ✅ UI/Responsiveness
- [ ] Mobile view (< 768px)
- [ ] Tablet view (768-1024px)
- [ ] Desktop view (> 1024px)
- [ ] Navbar fixed at top
- [ ] Smooth transitions
- [ ] Loading states
- [ ] Error messages

---

## 🎉 Success!

Your complete Instagram clone with AI toxicity detection is ready!

**Key Achievements:**
- ✅ Full-stack application (Flask + React)
- ✅ Real-time interactions
- ✅ ML-powered content moderation
- ✅ Professional Instagram-like UI
- ✅ Fully responsive design
- ✅ Complete documentation

**Have fun building and experimenting! 🚀**
