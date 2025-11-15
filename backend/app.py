import os
import re
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# Hugging Face model loaded once at import time to ensure fast inference
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import threading
_tokenizer = None
_model = None
clf = None

def _init_model_background():
    global _tokenizer, _model, clf
    try:
        _tokenizer = AutoTokenizer.from_pretrained("unitary/multilingual-toxic-xlm-roberta")
        _model = AutoModelForSequenceClassification.from_pretrained("unitary/multilingual-toxic-xlm-roberta")
        clf = pipeline("text-classification", model=_model, tokenizer=_tokenizer, truncation=True, top_k=None)
    except Exception:
        clf = None

# Custom transliterated Kannada / general toxic word list (lowercase)
CUSTOM_TOXIC_WORDS = {
    "moorka", "mad", "stupid", "hate", "kill", "useless"
}

# Rule-based toxicity category patterns (simple heuristics)
# Categories: insults, sarcasm, harassment, profanity, body_shaming, disrespect_emojis, indirect_negative
RB_EMOJI_DISRESPECT = {"😒", "😏", "🙄", "🤢", "😤", "😬"}
RB_PROFANITY_WORDS = {
    # Keep generic and custom list; avoid storing explicit slurs here
    "damn", "hell", "crap", "suck",
} | CUSTOM_TOXIC_WORDS
RB_INSULT_WORDS = {
    "dumb", "idiot", "stupid", "loser", "useless", "pathetic", "trash", "fake",
} | CUSTOM_TOXIC_WORDS
RB_BODY_SHAMING_WORDS = {
    "disgusting", "ugly", "fat", "fatty", "skinny", "gross",
}
RB_HARASSMENT_PHRASES = {
    "no one likes you", "stop embarrassing yourself", "go away", "nobody likes you",
}
RB_SARCASM_PATTERNS = [
    r"\b(impressive)\b\s*\.\.\.*\s*not\b",
    r"\b(yeah right)\b",
    r"\bgood for you,?\s*i guess\b",
    r"\bwow[,!]?\s+that'?s (impressive|great)\b\s*\.\.\.*",
]
RB_INDIRECT_NEGATIVE_PATTERNS = [
    r"\bpeople like you\b",
    r"\byou think you'?re better than everyone\b",
    r"\bthe reason things go wrong\b",
]

# Additional lexicons for new taxonomy (threat, hate, sexual)
THREAT_WORDS = {
    "kill", "die", "destroy", "hurt", "attack", "ruin"
}
HATE_WORDS = {
    "hate", "racist", "bigot", "xenophobe", "xenophobic"
}
SEXUAL_WORDS = {
    "sex", "sexy", "nude", "naked", "nsfw"
}

DB_PATH = os.path.join(os.path.dirname(__file__), "data.sqlite")

app = Flask(__name__)
CORS(app)


# ------------------------
# Database helpers
# ------------------------

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            image_url TEXT NOT NULL,
            caption TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT,
            text TEXT NOT NULL,
            original_text TEXT,
            masked_text TEXT,
            toxicity_score REAL,
            toxicity_category TEXT,
            toxicity_reasons TEXT,
            toxicity TEXT,
            category TEXT,
            score REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )

    # Backward compatibility: attempt to add new columns if existing DB predates them
    cur.execute("PRAGMA table_info(comments);")
    existing_cols = {row['name'] for row in cur.fetchall()}
    alter_statements = []
    if 'username' not in existing_cols:
        alter_statements.append("ALTER TABLE comments ADD COLUMN username TEXT")
    if 'original_text' not in existing_cols:
        alter_statements.append("ALTER TABLE comments ADD COLUMN original_text TEXT")
    if 'toxicity_score' not in existing_cols:
        alter_statements.append("ALTER TABLE comments ADD COLUMN toxicity_score REAL")
    if 'toxicity_category' not in existing_cols:
        alter_statements.append("ALTER TABLE comments ADD COLUMN toxicity_category TEXT")
    if 'toxicity_reasons' not in existing_cols:
        alter_statements.append("ALTER TABLE comments ADD COLUMN toxicity_reasons TEXT")
    if 'toxicity' not in existing_cols:
        alter_statements.append("ALTER TABLE comments ADD COLUMN toxicity TEXT")
    if 'category' not in existing_cols:
        alter_statements.append("ALTER TABLE comments ADD COLUMN category TEXT")
    if 'score' not in existing_cols:
        alter_statements.append("ALTER TABLE comments ADD COLUMN score REAL")
    for stmt in alter_statements:
        try:
            cur.execute(stmt)
        except Exception:
            pass

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(post_id, user_id),
            FOREIGN KEY (post_id) REFERENCES posts(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )

    conn.commit()
    conn.close()


# ------------------------
# Toxicity helpers
# ------------------------


def _find_custom_toxic_words(text: str) -> Tuple[bool, set]:
    words = set(re.findall(r"[\w']+", text.lower()))
    hits = {w for w in words if w in CUSTOM_TOXIC_WORDS}
    return (len(hits) > 0, hits)


def mask_toxic_words(text: str, toxic_words: Optional[set] = None) -> str:
    """Replace toxic words from our custom list with asterisks, case-insensitive."""
    if not text:
        return text
    if toxic_words is None:
        _, toxic_words = _find_custom_toxic_words(text)

    def repl(match):
        w = match.group(0)
        lw = w.lower()
        if lw in toxic_words:
            return "*" * len(w)
        return w

    # Token-wise replacement to preserve punctuation/spacing
    return re.sub(r"[\w']+", repl, text)


def hard_hide_message() -> str:
    return "⚠️ This comment is hidden due to toxic content"


def check_toxicity(text: str) -> Dict[str, Any]:
    """
    Returns a dict: {
        status: 'clean' | 'toxic',
        message: str,
        details: {
            model_label: str,
            model_score: float,  # 0..1
            custom_hits: [list of toxic words]
        }
    }
    """
    if not text or not text.strip():
        return {
            "status": "clean",
            "message": "Empty text",
            "details": {"model_label": "neutral", "model_score": 0.0, "custom_hits": []},
        }

    # Custom word check first (cheap)
    custom_flag, hits = _find_custom_toxic_words(text)

    # Rule-based analysis
    def _score_rule_based(t: str) -> Dict[str, Any]:
        low = (t or "").lower()
        categories = {
            "insults": 0.0,
            "sarcasm": 0.0,
            "harassment": 0.0,
            "profanity": 0.0,
            "body_shaming": 0.0,
            "disrespect_emojis": 0.0,
            "indirect_negative": 0.0,
        }
        # Insults
        if any(w in low.split() for w in RB_INSULT_WORDS):
            categories["insults"] = 0.7
        # Profanity
        if any(w in low.split() for w in RB_PROFANITY_WORDS):
            categories["profanity"] = max(categories["profanity"], 0.6)
        # Body shaming
        if any(w in low.split() for w in RB_BODY_SHAMING_WORDS):
            categories["body_shaming"] = 0.7
        # Harassment phrases
        if any(ph in low for ph in RB_HARASSMENT_PHRASES):
            categories["harassment"] = 0.7
        # Disrespectful emojis
        if any(e in t for e in RB_EMOJI_DISRESPECT):
            categories["disrespect_emojis"] = 0.6
        # Sarcasm patterns
        for pat in RB_SARCASM_PATTERNS:
            if re.search(pat, low):
                categories["sarcasm"] = max(categories["sarcasm"], 0.6)
        # Indirect negative tone
        for pat in RB_INDIRECT_NEGATIVE_PATTERNS:
            if re.search(pat, low):
                categories["indirect_negative"] = max(categories["indirect_negative"], 0.6)
        # Custom words bump insults/profanity
        if custom_flag:
            categories["insults"] = max(categories["insults"], 0.65)
            categories["profanity"] = max(categories["profanity"], 0.65)

        dominant_category = max(categories.items(), key=lambda kv: kv[1])[0]
        rule_score = max(categories.values())
        return {"categories": categories, "dominant_category": dominant_category, "rule_score": rule_score}

    rb = _score_rule_based(text)

    # Model check using globally loaded pipeline
    model_label = "neutral"
    model_score = 0.0
    try:
        if clf is None:
            raise RuntimeError("model_not_ready")
        result = clf(text)
        if isinstance(result, list):
            item = result[0] if result and isinstance(result[0], dict) else result
            if isinstance(item, dict):
                model_label = item.get("label", model_label)
                model_score = float(item.get("score", model_score))
            elif isinstance(item, list) and item:
                model_label = item[0].get("label", model_label)
                model_score = float(item[0].get("score", model_score))
    except Exception:
        model_label = "model_unavailable"
        model_score = 0.0

    # Heuristic threshold for model toxicity
    is_model_toxic = (model_label.lower().startswith("toxic") and model_score >= 0.60)
    is_rule_toxic = (rb["rule_score"] >= 0.60)
    is_toxic = custom_flag or is_model_toxic or is_rule_toxic

    combined_score = max(model_score, rb["rule_score"], 0.85 if (custom_flag and not (is_model_toxic or is_rule_toxic)) else 0.0)
    dominant_category = rb["dominant_category"] if rb["rule_score"] >= model_score else ("toxic" if is_model_toxic else ("custom-word" if custom_flag else "neutral"))

    status = "toxic" if is_toxic else "clean"
    if status == "toxic":
        percent = int(round(combined_score * 100)) if combined_score > 0 else 85
        msg = f"Your message includes sensitive content: {dominant_category} (score: {percent}%). Do you still want to post?"
    else:
        msg = "Clean"

    return {
        "status": status,
        "message": msg,
        "details": {
            "model_label": model_label,
            "model_score": model_score,
            "rule_categories": rb["categories"],
            "rule_score": rb["rule_score"],
            "dominant_category": dominant_category,
            "combined_score": combined_score,
            "custom_hits": sorted(list(hits)),
            # Simplified outputs per new contract
            "final_toxic": status == "toxic",
            "category": dominant_category,
            "score": combined_score,
        }
    }


def compute_toxicity(text: str) -> Dict[str, Any]:
    """Return simplified toxicity judgment combining model + rules.
    Output: { final_toxic: bool, score: float, category: str }
    """
    res = check_toxicity(text)
    det = res.get("details", {})
    return {
        "final_toxic": bool(det.get("final_toxic", False)),
        "score": float(det.get("score", 0.0)),
        "category": det.get("category")
    }


def classify_comment_v2(text: str) -> Dict[str, Any]:
    """Classify text into requested schema.
    Output JSON contract:
    {
      combined_score: float 0..1,
      dominant_category: one of [toxic, insult, threat, harassment, hate, sexual, non-toxic],
      reasons: [ { category, score } ... top 3 with score > 0 ],
      masked_text: string
    }
    """
    base = check_toxicity(text)
    det = base.get("details", {})
    combined = float(det.get("combined_score", 0.0))
    # Build scores for new taxonomy
    low = (text or "").lower()
    words = set(re.findall(r"[\w']+", low))
    def any_in(set_words):
        return any(w in words for w in set_words)

    scores = {
        "insult": det.get("rule_categories", {}).get("insults", 0.0),
        "harassment": det.get("rule_categories", {}).get("harassment", 0.0),
        "threat": 0.0,
        "hate": 0.0,
        "sexual": 0.0,
    }
    # Threat detection simple heuristic
    if any_in(THREAT_WORDS):
        scores["threat"] = max(scores["threat"], 0.7)
    # Hate detection
    if any_in(HATE_WORDS):
        scores["hate"] = max(scores["hate"], 0.65)
    # Sexual detection
    if any_in(SEXUAL_WORDS):
        scores["sexual"] = max(scores["sexual"], 0.6)

    # Aggregate toxic indicator
    toxic_flag = bool(det.get("final_toxic")) or any(v >= 0.6 for v in scores.values())

    # Determine dominant category per required set
    if not toxic_flag:
        dominant = "non-toxic"
    else:
        # choose highest score category among new taxonomy if >=0.6 else fallback 'toxic'
        top_cat, top_score = max(scores.items(), key=lambda kv: kv[1])
        if top_score >= 0.6:
            dominant = top_cat
        else:
            # fallback: if original dominant category was 'custom-word' treat as insult else 'toxic'
            orig_dom = det.get("dominant_category")
            if orig_dom == "custom-word":
                dominant = "insult"
            elif orig_dom in ["insults", "harassment"]:
                dominant = orig_dom[:-1] if orig_dom.endswith("s") else orig_dom
            else:
                dominant = "toxic"

    # Reasons: map non-zero scores plus maybe model toxicity if no categories
    reason_items = [(c, s) for c, s in scores.items() if s > 0]
    # If nothing but toxic_flag due to model, add generic toxic reason
    if not reason_items and toxic_flag:
        reason_items.append(("toxic", min(0.6, combined or 0.6)))
    # Sort desc and take top 3
    reason_items.sort(key=lambda kv: kv[1], reverse=True)
    reasons = [{"category": c, "score": round(float(s), 3)} for c, s in reason_items[:3]]

    # Masking
    if dominant == "non-toxic":
        masked_text = text
    else:
        masked_try = mask_toxic_words(text)
        masked_text = masked_try if masked_try != text else re.sub(r"[\w']+", lambda m: "***" if m.group(0).lower() in words else m.group(0), text)  # fallback full *** for matched words already flagged

    return {
        "combined_score": round(combined if combined <= 1.0 else 1.0, 3),
        "dominant_category": dominant,
        "reasons": reasons,
        "masked_text": masked_text,
    }


# ------------------------
# Utility helpers
# ------------------------

def _get_user_by_username(cur: sqlite3.Cursor, username: str) -> Optional[Dict[str, Any]]:
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cur.fetchone()


def _ensure_user(cur: sqlite3.Cursor, username: str, password: Optional[str] = None) -> Tuple[Dict[str, Any], bool]:
    user = _get_user_by_username(cur, username)
    created = False
    if not user and password is not None:
        pw_hash = generate_password_hash(password)
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, pw_hash))
        user_id = cur.lastrowid
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        created = True
    return user, created


# ------------------------
# Routes
# ------------------------

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        user = _get_user_by_username(cur, username)
        if user:
            # Verify password
            if not check_password_hash(user["password"], password):
                return jsonify({"error": "Invalid credentials"}), 401
            return jsonify({"message": "Login successful"})
        else:
            # Create account automatically
            pw_hash = generate_password_hash(password)
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, pw_hash))
            conn.commit()
            return jsonify({"message": "Account created"})
    finally:
        conn.close()


@app.route("/upload_post", methods=["POST"])
def upload_post():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    image_url = (data.get("image_url") or "").strip()
    caption = data.get("caption")

    if not username or not image_url:
        return jsonify({"error": "username and image_url required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        user = _get_user_by_username(cur, username)
        if not user:
            return jsonify({"error": "User not found"}), 404
        created_at = datetime.utcnow().isoformat()
        cur.execute(
            "INSERT INTO posts (user_id, image_url, caption, created_at) VALUES (?, ?, ?, ?)",
            (user["id"], image_url, caption, created_at)
        )
        conn.commit()
        post_id = cur.lastrowid
        return jsonify({"message": "Post uploaded", "post_id": post_id})
    finally:
        conn.close()


@app.route("/feed/<username>", methods=["GET"])
def feed(username):
    username = (username or "").strip()
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        user = _get_user_by_username(cur, username)
        if not user:
            return jsonify({"error": "User not found"}), 404
        cur.execute(
            """
            SELECT p.id, p.image_url, p.caption, p.created_at, u.username,
                   (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as likes
            FROM posts p
            JOIN users u ON u.id = p.user_id
            WHERE p.user_id != ?
            ORDER BY datetime(p.created_at) DESC
            """,
            (user["id"],)
        )
        posts = cur.fetchall()

        # Fetch comments for these posts and attach
        post_ids = [p["id"] for p in posts]
        comments_map = _get_comments_for_post_ids(cur, post_ids)
        enriched = []
        for p in posts:
            enriched.append({
                **p,
                "comments": comments_map.get(p["id"], [])
            })
        return jsonify({"posts": enriched})
    finally:
        conn.close()


@app.route("/profile/<username>", methods=["GET"])
def profile(username):
    username = (username or "").strip()
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        user = _get_user_by_username(cur, username)
        if not user:
            return jsonify({"error": "User not found"}), 404
        cur.execute(
            """
            SELECT p.id, p.image_url, p.caption, p.created_at,
                   (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as likes
            FROM posts p
            WHERE p.user_id = ?
            ORDER BY datetime(p.created_at) DESC
            """,
            (user["id"],)
        )
        posts = cur.fetchall()

        post_ids = [p["id"] for p in posts]
        comments_map = _get_comments_for_post_ids(cur, post_ids)
        enriched = []
        for p in posts:
            enriched.append({
                **p,
                "comments": comments_map.get(p["id"], [])
            })
        return jsonify({"posts": enriched})
    finally:
        conn.close()


def _get_comments_for_post_ids(cur: sqlite3.Cursor, post_ids: List[int]) -> Dict[int, List[Dict[str, Any]]]:
    if not post_ids:
        return {}
    placeholders = ",".join(["?"] * len(post_ids))
    cur.execute(
        f"""
        SELECT c.id, c.post_id, c.username as username,
               c.text, c.original_text, c.masked_text,
               c.toxicity as toxicity, c.category as category, c.score as score,
               c.created_at
        FROM comments c
        WHERE c.post_id IN ({placeholders})
        ORDER BY c.post_id ASC, datetime(c.created_at) ASC
        """,
        tuple(post_ids)
    )
    rows = cur.fetchall()
    result = {}
    for r in rows:
        item = {
            "id": r["id"],
            "username": r.get("username") or "",
            "original_text": r.get("original_text") or r.get("text"),
            "masked_text": r.get("masked_text") or r.get("original_text") or r.get("text"),
            "toxicity": r.get("toxicity") or ("toxic" if (r.get("score") or 0) >= 0.6 else "non-toxic"),
            "category": r.get("category"),
            "score": round(float(r.get("score") or 0.0), 3),
            "created_at": r["created_at"],
        }
        result.setdefault(r["post_id"], []).append(item)
    return result


@app.route("/comment", methods=["POST"])
def comment():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    post_id = data.get("post_id")
    text = (data.get("text") or "").strip()
    confirm = bool(data.get("confirm", False))

    if not username or not post_id or not text:
        return jsonify({"error": "username, post_id and text are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        user = _get_user_by_username(cur, username)
        if not user:
            return jsonify({"error": "User not found"}), 404
        cur.execute("SELECT id, user_id FROM posts WHERE id = ?", (post_id,))
        post = cur.fetchone()
        if not post:
            return jsonify({"error": "Post not found"}), 404

        # -------- Manual toxicity dataset & pattern check --------
        toxic_words = [
            '2g1c', '2 girls 1 cup', 'acrotomophilia', 'alabama hot pocket', 'alaskan pipeline',
            'anal', 'anilingus', 'anus', 'apeshit', 'arsehole', 'ass', 'asshole', 'assmunch',
            'auto erotic', 'autoerotic', 'babeland', 'baby batter', 'baby juice', 'ball gag',
            'ball gravy', 'ball kicking', 'ball licking', 'ball sack', 'ball sucking',
            'bangbros', 'bangbus', 'bareback', 'barely legal', 'barenaked', 'bastard',
            'bastardo', 'bastinado', 'bbw', 'bdsm', 'beaner', 'beaners', 'beaver cleaver',
            'beaver lips', 'beastiality', 'bestiality', 'big black', 'big breasts',
            'big knockers', 'big tits', 'bimbos', 'birdlock', 'bitch', 'bitches',
            'black cock', 'blonde action', 'blonde on blonde action', 'blowjob', 'blow job',
            'blow your load', 'blue waffle', 'blumpkin', 'bollocks', 'bondage', 'boner',
            'boob', 'boobs', 'booty call', 'brown showers', 'brunette action', 'bukkake',
            'bulldyke', 'bullet vibe', 'bullshit', 'bung hole', 'bunghole', 'busty',
            'butt', 'buttcheeks', 'butthole', 'camel toe', 'camgirl', 'camslut', 'camwhore',
            'carpet muncher', 'carpetmuncher', 'chocolate rosebuds', 'cialis', 'circlejerk',
            'cleveland steamer', 'clit', 'clitoris', 'clover clamps', 'clusterfuck',
            'cock', 'cocks', 'coprolagnia', 'coprophilia', 'cornhole', 'coon', 'coons',
            'creampie', 'cum', 'cumming', 'cumshot', 'cumshots', 'cunnilingus', 'cunt',
            'darkie', 'date rape', 'daterape', 'deep throat', 'deepthroat', 'dendrophilia',
            'dick', 'dildo', 'dingleberry', 'dingleberries', 'dirty pillows', 'dirty sanchez',
            'doggie style', 'doggiestyle', 'doggy style', 'doggystyle', 'dog style',
            'dolcett', 'domination', 'dominatrix', 'dommes', 'donkey punch', 'double dong',
            'double penetration', 'dp action', 'dry hump', 'dvda', 'eat my ass', 'ecchi',
            'ejaculation', 'erotic', 'erotism', 'escort', 'eunuch', 'fag', 'faggot',
            'fecal', 'felch', 'fellatio', 'feltch', 'female squirting', 'femdom',
            'figging', 'fingerbang', 'fingering', 'fisting', 'foot fetish', 'footjob',
            'frotting', 'fuck', 'fuck buttons', 'fuckin', 'fucking', 'fucktards',
            'fudge packer', 'fudgepacker', 'futanari', 'gangbang', 'gang bang', 'gay sex',
            'genitals', 'giant cock', 'girl on', 'girl on top', 'girls gone wild',
            'goatcx', 'goatse', 'god damn', 'gokkun', 'golden shower', 'goodpoop',
            'goo girl', 'goregasm', 'grope', 'group sex', 'g-spot', 'guro', 'hand job',
            'handjob', 'hard core', 'hardcore', 'hentai', 'homoerotic', 'honkey',
            'hooker', 'horny', 'hot carl', 'hot chick', 'how to kill', 'how to murder',
            'huge fat', 'humping', 'incest', 'intercourse', 'jack off', 'jail bait',
            'jailbait', 'jelly donut', 'jerk off', 'jigaboo', 'jiggaboo', 'jiggerboo',
            'jizz', 'juggs', 'kike', 'kinbaku', 'kinkster', 'kinky', 'knobbing',
            'leather restraint', 'leather straight jacket', 'lemon party', 'livesex',
            'lolita', 'lovemaking', 'make me come', 'male squirting', 'masturbate',
            'masturbating', 'masturbation', 'menage a trois', 'milf', 'missionary position',
            'mong', 'motherfucker', 'mound of venus', 'mr hands', 'muff diver', 'muffdiving',
            'nambla', 'nawashi', 'negro', 'neonazi', 'nigga', 'nigger', 'nig nog',
            'nimphomania', 'nipple', 'nipples', 'nsfw', 'nsfw images', 'nude', 'nudity',
            'nutten', 'nympho', 'nymphomania', 'octopussy', 'omorashi', 'one cup two girls',
            'one guy one jar', 'orgasm', 'orgy', 'paedophile', 'paki', 'panties', 'panty',
            'pedobear', 'pedophile', 'pegging', 'penis', 'phone sex', 'piece of shit',
            'pikey', 'pissing', 'piss pig', 'pisspig', 'playboy', 'pleasure chest',
            'pole smoker', 'ponyplay', 'poof', 'poon', 'poontang', 'punany', 'poop chute',
            'poopchute', 'porn', 'porno', 'pornography', 'prince albert piercing', 'pthc',
            'pubes', 'pussy', 'queaf', 'queef', 'quim', 'raghead', 'raging boner',
            'rape', 'raping', 'rapist', 'rectum', 'reverse cowgirl', 'rimjob', 'rimming',
            'rosy palm', 'rosy palm and her 5 sisters', 'rusty trombone', 'sadism',
            'santorum', 'scat', 'schlong', 'scissoring', 'semen', 'sex', 'sexcam',
            'sexo', 'sexy', 'sexual', 'sexually', 'sexuality', 'shaved beaver',
            'shaved pussy', 'shemale', 'shibari', 'shit', 'shitblimp', 'shitty',
            'shota', 'shrimping', 'skeet', 'slanteye', 'slut', 's&m', 'smut', 'snatch',
            'snowballing', 'sodomize', 'sodomy', 'spastic', 'spic', 'splooge',
            'splooge moose', 'spooge', 'spread legs', 'spunk', 'strap on', 'strapon',
            'strappado', 'strip club', 'style doggy', 'suck', 'sucks', 'suicide girls',
            'sultry women', 'swastika', 'swinger', 'tainted love', 'taste my',
            'tea bagging', 'threesome', 'throating', 'thumbzilla', 'tied up', 'tight white',
            'tit', 'tits', 'titties', 'titty', 'tongue in a', 'topless', 'tosser',
            'towelhead', 'tranny', 'tribadism', 'tub girl', 'tubgirl', 'tushy', 'twat',
            'twink', 'twinkie', 'two girls one cup', 'undressing', 'upskirt', 'urethra play',
            'urophilia', 'vagina', 'venus mound', 'viagra', 'vibrator', 'violet wand',
            'vorarephilia', 'voyeur', 'voyeurweb', 'voyuer', 'vulva', 'wank', 'wetback',
            'wet dream', 'white power', 'whore', 'worldsex', 'wrapping men', 'wrinkled starfish',
            'xx', 'xxx', 'yaoi', 'yellow showers', 'yiffy', 'zoophilia',
            'kill', 'die', 'murder', 'violence', 'attack', 'destroy', 'harm', 'hurt',
            'beat up', 'punch', 'kick', 'slap', 'fight', 'war', 'bomb', 'weapon',
            'knife', 'gun', 'shoot', 'stab', 'crush', 'smash', 'break', 'ruin',
            'stupid', 'idiot', 'dumb', 'loser', 'moron', 'retard', 'pathetic', 'worthless',
            'garbage', 'trash', 'scum', 'disgusting', 'ugly', 'fat', 'gross',
            'ಮೂರ್ಖ', 'ಬೇವಕೂಫ', 'ಹುಚ್ಚ', 'ದುಷ್ಟ', 'ಕೆಟ್ಟ', 'ಚೆಂಡೆ', 'ಬೊಳ್ಳಿ', 'ದೊಂಕೆ',
            'ಮದಾರಿ', 'ಕೋಗಿಲೆ', 'ರಾಕ್ಷಸ', 'ಪಿಶಾಚ', 'ಹಿಡಿದುಕೊಂಡು ಸಾಯಿ', 'ಚಂಡಾಲ',
            'ಮೂರ್ಖತನ', 'ಬುದ್ದಿಹೀನ', 'ಚೀಪ್', 'ಮರಳೆ', 'ಹೊಲಸು', 'ಅಸಹ್ಯ', 'ದಿಗಿಲು',
            'ಕಮೀನೆ', 'ಹರಾಮಿ', 'ಕುತ್ತ', 'ಸುನ್ನ', 'ಮದರ್', 'ಕೂಕಲ್', 'ತುಲ್ಲು',
            'murkha'
        ]
        hf_toxic_patterns = [
            'ignore everything', 'forget previous instructions', 'new instructions',
            'chatagi', 'pretend to be', 'act as if', 'roleplay as', 'dan mode',
            'do anything now', 'break free', 'no limitations', 'uncensored',
            'unrestricted', 'without guidelines', 'bypass restrictions',
            'harassment', 'bullying', 'stalking', 'intimidation', 'threatening',
            'aggressive behavior', 'hostile', 'abusive', 'malicious', 'vindictive',
            'identity hate', 'discrimination', 'prejudice', 'bigotry', 'supremacist',
            'extremist', 'radical', 'separatist', 'nationalist', 'xenophobic',
            'severe toxic', 'extremely harmful', 'dangerous content', 'violent threats',
            'graphic violence', 'disturbing content', 'shocking material',
            'explicit content', 'inappropriate material', 'adult content', 'nsfw',
            'sexual content', 'graphic descriptions', 'vulgar language',
            'death threat', 'violence threat', 'harm threat', 'intimidation',
            'threatening behavior', 'menacing', 'coercive', 'blackmail',
            'personal attack', 'character assassination', 'defamation', 'slander',
            'degrading', 'demeaning', 'belittling', 'humiliating', 'mocking'
        ]
        low = text.lower()
        for pattern in hf_toxic_patterns:
            if pattern in low:
                return jsonify({
                    "warning": True,
                    "type": "toxic",
                    "toxicity_score": None,
                    "toxicity_category": "manual",
                    "detected_word": pattern
                })
        for w in toxic_words:
            if w in low:
                return jsonify({
                    "warning": True,
                    "type": "toxic",
                    "toxicity_score": None,
                    "toxicity_category": "manual",
                    "detected_word": w
                })

        # Existing combined model/rule logic
        simple = compute_toxicity(text)
        final_toxic = simple["final_toxic"]
        score = float(simple["score"])
        category = simple.get("category")

        if final_toxic and not confirm:
            return jsonify({
                "warning": True,
                "type": "toxic",
                "toxicity_score": round(score, 3),
                "toxicity_category": category,
                "detected_word": None
            })

        masked = None
        if final_toxic:
            masked_try = mask_toxic_words(text)
            masked = masked_try if masked_try != text else hard_hide_message()

        created_at = datetime.utcnow().isoformat()
        toxicity_score = float(score)
        toxicity_category = category
        toxicity_reasons = None
        cur.execute(
            "INSERT INTO comments (post_id, user_id, username, text, original_text, masked_text, toxicity_score, toxicity_category, toxicity_reasons, toxicity, category, score, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                post_id, user["id"], user["username"], text, text, masked,
                toxicity_score, toxicity_category, toxicity_reasons,
                ("toxic" if final_toxic else "non-toxic"), toxicity_category, toxicity_score,
                created_at,
            )
        )
        conn.commit()
        return jsonify({"status": "ok"})
    finally:
        conn.close()


# Public endpoint for pure toxicity analysis (combined model + rules)
@app.route("/analyze", methods=["POST"])
def analyze_text():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400

    res = check_toxicity(text)
    toxicity = "toxic" if res["status"] == "toxic" else "non-toxic"
    score = float(res["details"].get("combined_score", 0.0))
    category = res["details"].get("dominant_category")

    return jsonify({
        "text": text,
        "toxicity": toxicity,
        "toxicity_score": round(score, 3),
        "category": category,
        "debug": res["details"],  # optional extra context
    })


# New classification endpoint per simplified contract
@app.route("/classify", methods=["POST"])
def classify_v2():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({
            "combined_score": 0.0,
            "dominant_category": "non-toxic",
            "reasons": [],
            "masked_text": ""
        })
    out = classify_comment_v2(text)
    # Ensure JSON meets strict rules (no unknown category, combined_score always present)
    if out.get("dominant_category") not in {"toxic", "insult", "threat", "harassment", "hate", "sexual", "non-toxic"}:
        out["dominant_category"] = "non-toxic" if out.get("combined_score", 0.0) < 0.6 else "toxic"
    return jsonify(out)


# Fetch comments for a post; enforce viewer-based masking per rules
@app.route("/comments/<int:post_id>", methods=["GET"])
def get_comments(post_id: int):
    viewer = (request.args.get("viewer") or "").strip()

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Get post and owner
        cur.execute("SELECT p.id, u.username as owner FROM posts p JOIN users u ON u.id = p.user_id WHERE p.id = ?", (post_id,))
        post = cur.fetchone()
        if not post:
            return jsonify({"error": "Post not found"}), 404

        cur.execute(
            """
            SELECT c.id,
                   c.post_id,
                   COALESCE(c.username, u.username) AS username,
                   c.text,
                   c.original_text,
                   c.masked_text,
                   c.toxicity AS toxicity,
                   c.score AS score,
                   c.created_at
            FROM comments c
            LEFT JOIN users u ON u.id = c.user_id
            WHERE c.post_id = ?
            ORDER BY datetime(c.created_at) ASC
            """,
            (post_id,)
        )
        rows = cur.fetchall()

        # Return only visible text per viewer masking rules
        result = []
        for r in rows:
            author = r.get("username") or ""
            authored_by_viewer = bool(viewer and author == viewer)
            is_toxic = (r.get("toxicity") == "toxic") or ((r.get("score") or 0.0) >= 0.6)
            if authored_by_viewer:
                visible_text = r.get("original_text") or r.get("text")
            else:
                if is_toxic:
                    visible_text = r.get("masked_text") or mask_toxic_words(r.get("original_text") or r.get("text") or "")
                else:
                    visible_text = r.get("original_text") or r.get("text")

            result.append({
                "id": r["id"],
                "author": author,
                "text": visible_text,
                "created_at": r["created_at"],
            })

        return jsonify({"post_id": post_id, "comments": result})
    finally:
        conn.close()


@app.route("/like", methods=["POST"])
def like_post():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    post_id = data.get("post_id")

    if not username or not post_id:
        return jsonify({"error": "username and post_id required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        user = _get_user_by_username(cur, username)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if post exists
        cur.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
        post = cur.fetchone()
        if not post:
            return jsonify({"error": "Post not found"}), 404

        # Check if already liked
        cur.execute(
            "SELECT id FROM likes WHERE post_id = ? AND user_id = ?",
            (post_id, user["id"])
        )
        existing_like = cur.fetchone()

        if existing_like:
            # Unlike: remove the like
            cur.execute("DELETE FROM likes WHERE post_id = ? AND user_id = ?", (post_id, user["id"]))
        else:
            # Like: add a new like
            created_at = datetime.utcnow().isoformat()
            cur.execute(
                "INSERT INTO likes (post_id, user_id, created_at) VALUES (?, ?, ?)",
                (post_id, user["id"], created_at)
            )
        
        conn.commit()

        # Return updated like count
        cur.execute("SELECT COUNT(*) as count FROM likes WHERE post_id = ?", (post_id,))
        like_count = cur.fetchone()["count"]
        
        return jsonify({"likes": like_count})
    finally:
        conn.close()


@app.route("/comment/delete", methods=["POST"])
def delete_comment():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    comment_id = data.get("comment_id")
    if not username or not comment_id:
        return jsonify({"error": "username and comment_id required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Fetch comment
        cur.execute("SELECT id, user_id, username FROM comments WHERE id = ?", (comment_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Comment not found"}), 404

        # Resolve provided username to user_id
        cur.execute("SELECT id, username FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        is_author = (row.get("user_id") == user["id"]) or (row.get("username") == user["username"])
        if not is_author:
            return jsonify({"error": "Forbidden"}), 403

        cur.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        conn.commit()
        return jsonify({"status": "ok"})
    finally:
        conn.close()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/", methods=["GET"])
def root():
    """Simple root endpoint to avoid 404s when opening base URL in a browser."""
    return jsonify({
        "status": "ok",
        "service": "insta-toxic-backend",
        "message": "Backend running. See /health or use the documented API routes.",
        "docs": "/health"
    })


@app.route("/favicon.ico")
def favicon():
    """Return empty favicon to prevent 404 noise in browser console."""
    return ("", 204, {"Content-Type": "image/x-icon"})


if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    init_db()
    # Warm up model asynchronously to avoid blocking server startup
    t = threading.Thread(target=_init_model_background, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
