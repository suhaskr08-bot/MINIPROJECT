# Backend Service

Flask API providing user login/auto-signup, post uploads, feeds, profiles, and toxicity-aware commenting with multilingual model + custom word list.

## Features
- POST /login auto-creates account if username not found.
- POST /upload_post stores post (image URL + caption).
- GET /feed/<username> shows posts from other users.
- GET /profile/<username> shows user's own posts.
- POST /comment performs toxicity analysis using `unitary/multilingual-toxic-xlm-roberta` and custom transliterated Kannada word list, warns before posting toxic content.
- POST /analyze returns combined toxicity analysis (Hugging Face model + 7-category rule-based checker) with dominant category and score.
- GET /comments/<post_id>?viewer=<username> returns comments with masking logic.
	- Only the comment author sees the original unmasked text and receives toxicity details (score, category, reasons). Others see masked text where custom toxic words are replaced and no toxicity metadata.
- Masking: author always sees original; others see `masked_text` for toxic comments.

## Install (Windows PowerShell)

```powershell
# From repo root
cd backend
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

> Note: First comment request invoking model may download weights (~hundreds MB). Ensure internet access.

## Run
```powershell
python app.py
```
App listens on http://127.0.0.1:5000

## Sample Requests

```powershell
# Login (create or authenticate)
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/login -ContentType 'application/json' -Body '{"username":"alice","password":"pw123"}'

# Upload post
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/upload_post -ContentType 'application/json' -Body '{"username":"alice","image_url":"http://img","caption":"Hello"}'

# Feed
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:5000/feed/alice

# Profile
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:5000/profile/alice

# Toxicity pre-check (will warn if toxic)
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/comment -ContentType 'application/json' -Body '{"username":"alice","post_id":1,"text":"You are stupid"}'

# Confirm posting after warning
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/comment -ContentType 'application/json' -Body '{"username":"alice","post_id":1,"text":"You are stupid","confirm":true}'

# Get comments (alice viewing)
Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:5000/comments/1?viewer=alice'

# Pure analysis (combined model + rules)
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/analyze -ContentType 'application/json' -Body '{"text":"You\'re stupid 😒"}'
```

### /analyze Response

```json
{
	"text": "You're stupid 😒",
	"toxicity": "toxic",
	"toxicity_score": 0.85,
	"category": "insults"
}
```
Notes:
- `toxicity_score` is a combined score from the multilingual model and the rule-based checker.
- `category` is the dominant category from: insults, sarcasm, harassment, profanity, body_shaming, disrespect_emojis, indirect_negative.
- Additional debugging details are included under a `debug` key for introspection (not required by clients).
 - In `/comments`, toxicity details are only returned to the author viewing their own comment; other viewers only receive masked/plain text.
```

## Environment Variables
- `PORT`: override default 5000

## Notes
- SQLite database stored at `backend/data.sqlite`.
- Model scoring threshold heuristic: label begins with "toxic" and score >= 0.60 or custom word hit.
- Masking only replaces custom word list matches (model doesn't provide token spans).

## Future Improvements
- Add JWT or session-based auth.
- Expand custom word list & allow admin updates.
- Add pagination to feed/comments.
- Cache model pipeline globally with concurrency-safe lock.
