"""
Lightweight toxicity analysis module for Flask apps.

Provides:
- Curated toxic lexicons grouped by category (no explicit slurs)
- Fast rule-based checker (lowercase, punctuation strip, exact + partial match)
- Optional Hugging Face model merge (score only; safe fallback)
- Public function: analyze_text(text: str) -> dict

Contract:
- If toxic (model OR rules):
  {
    "status": "warning",
    "type": "<category>",
    "score": <float>,      # model score or 0.0 if model not used/ready
    "message": "This comment may be toxic",
    "matched_words": [..]  # optional (present only when rule-based matched)
  }
- If clean: { "status": "clean" }

Production-safety:
- No blocking model load; model is lazy and optional.
- No explicit slurs in bundled lists; uses generic and mild/strong non-slur terms.
- Readable, modular structure with clear separation of concerns.
"""
from __future__ import annotations

import re
import threading
from typing import Dict, List, Optional, Set, Tuple

try:
    # transformers is optional at runtime; we handle absence gracefully
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    AutoTokenizer = None  # type: ignore
    AutoModelForSequenceClassification = None  # type: ignore
    pipeline = None  # type: ignore

# -----------------------------
# Curated Lexicons (no slurs)
# -----------------------------
# Note: Includes mild and strong variants, Indian regional (Kannada, English translit),
# abbreviations, and hostile phrases. Avoids explicit slurs by design.

LEXICONS: Dict[str, Set[str]] = {
    # Swearing/obscene language (non-slur, general profanity)
    "profanity": {
        "wtf", "wth", "damn", "hell", "crap", "bs", "b.s", "bloody",
        "screw", "screwed", "screwoff", "piss", "pissed", "pissing",
        "freak", "freaking", "freakin", "holyshit", "holycrap",
        "shit", "bullshit", "bullcrap", "frick", "fricking",
        "sucks", "suck", "suckish", "sucky",
        "stfu", "gtfo", "omfg", "lmao", "lmfao",
    },
    # Insults (non-identity), name-calling
    "insults": {
        "stupid", "idiot", "dumb", "moron", "loser", "pathetic", "useless",
        "trash", "garbage", "clown", "joker", "fake", "toxic",
        "nonsense", "fool", "slow", "brainless", "mindless",
        # Kannada/English translit (non-slur)
        "moorka",  # fool
        "huchcha",  # mad/crazy
        "kalla",    # liar/thief (contextual)
        "ketta",    # bad/mean
    },
    # Directed harassment / bullying phrases
    "harassment": {
        "shut up", "shutup", "go away", "get lost", "nobody likes you",
        "no one likes you", "stop talking", "stop embarrassing yourself",
        "you are a joke", "you are trash", "disgrace",
        "report you", "cancel you", "ruin you",
    },
    # Body shaming (non-identity-specific)
    "body_shaming": {
        "ugly", "disgusting", "gross", "fat", "fatty", "skinny",
        "hideous", "repulsive",
    },
    # Hate (conceptual terms; no slurs)
    "hate": {
        "hate", "hateful", "racist", "racism", "bigot", "bigotry",
        "sexist", "misogynist", "xenophobe", "xenophobic", "homophobic",
        "intolerant", "discriminatory",
    },
    # Slang/abbreviations (general internet slang; not necessarily toxic by itself)
    "slang": {
        "lol", "lmao", "rofl", "smh", "idgaf", "idc", "bruh", "bro",
        "kys",  # often used toxically; keep flagged here
        "ez", "noob", "rekt", "owned",
        # Kannada/English colloquial
        "maga",  # dude/bro (can be neutral, but often used sharply)
        "sakka",  # lame/weak
    },
    # Disrespect/hostile emojis
    "emojis": {
        "🙄", "😒", "😏", "🤢", "🤮", "😤", "😬", "💩", "🖕",
    },
}

# Fast lookups and simple category priority
ALL_TERMS: Set[str] = set().union(*LEXICONS.values())
CATEGORY_PRIORITY: List[str] = [
    "hate", "harassment", "profanity", "insults", "body_shaming", "slang", "emojis"
]

# For partial matches like "sucks" ~ "suck", "freaking" ~ "freak"
STEM_CANDIDATES: Set[str] = {
    term for term in ALL_TERMS if 3 <= len(term) <= 6 and term.isalpha()
}

_WORD_RE = re.compile(r"[\w']+")
_PUNCT_RE = re.compile(r"[\u2000-\u206F\u2E00-\u2E7F\\'!\"#$%&()*+,\-./:;<=>?@[\\]^_`{|}~]")


def _normalize(text: str) -> Tuple[str, List[str]]:
    t = (text or "").strip().lower()
    # Keep emojis for separate pass; strip punctuation for tokens
    t_no_punct = _PUNCT_RE.sub(" ", t)
    tokens = [tok for tok in _WORD_RE.findall(t_no_punct) if tok]
    return t, tokens


def _rule_check(text: str) -> Tuple[bool, Optional[str], Set[str]]:
    """Return (is_toxic, category, matched_words).
    - exact match on tokens and emojis in raw text
    - partial match: token startswith/endswith core term (len>=3)
    - counts by category and selects highest with priority tie-break
    """
    raw, tokens = _normalize(text)
    matched_by_cat: Dict[str, Set[str]] = {k: set() for k in LEXICONS.keys()}

    token_set = set(tokens)
    # 1) Exact token matches
    for cat, terms in LEXICONS.items():
        exact = token_set.intersection(terms)
        matched_by_cat[cat].update(exact)

    # 2) Phrase/emoji/raw contains checks
    for cat, terms in LEXICONS.items():
        for term in terms:
            if " " in term or any(ch for ch in term if ch in {"🙄", "😒", "😏", "🤢", "🤮", "😤", "😬", "💩", "🖕"}):
                if term in raw:
                    matched_by_cat[cat].add(term)

    # 3) Partial/stem matches on tokens
    for tok in tokens:
        for stem in STEM_CANDIDATES:
            if stem in tok and stem in ALL_TERMS:
                # Identify the category(ies) that include this stem
                for cat, terms in LEXICONS.items():
                    if stem in terms:
                        matched_by_cat[cat].add(stem)

    # Count and pick best category
    cat_counts = {cat: len(terms) for cat, terms in matched_by_cat.items() if terms}
    if not cat_counts:
        return False, None, set()

    # Max by count, then by priority order
    top_count = max(cat_counts.values())
    candidates = [cat for cat, c in cat_counts.items() if c == top_count]
    candidates.sort(key=lambda c: CATEGORY_PRIORITY.index(c))
    best_cat = candidates[0]
    matched = matched_by_cat[best_cat]
    return True, best_cat, matched


# -----------------------------
# Optional HF model integration
# -----------------------------
_HF_LOCK = threading.Lock()
_HF_PIPELINE = None


def _ensure_model() -> Optional[object]:
    global _HF_PIPELINE
    if _HF_PIPELINE is not None:
        return _HF_PIPELINE
    if pipeline is None or AutoTokenizer is None or AutoModelForSequenceClassification is None:
        return None
    with _HF_LOCK:
        if _HF_PIPELINE is not None:
            return _HF_PIPELINE
        try:
            tok = AutoTokenizer.from_pretrained("unitary/multilingual-toxic-xlm-roberta")
            mdl = AutoModelForSequenceClassification.from_pretrained("unitary/multilingual-toxic-xlm-roberta")
            _HF_PIPELINE = pipeline("text-classification", model=mdl, tokenizer=tok, truncation=True)
        except Exception:
            _HF_PIPELINE = None
    return _HF_PIPELINE


_MODEL_TO_CATEGORY = {
    # Common label mappings
    "insult": "insults",
    "threat": "harassment",
    "obscene": "profanity",
    "toxic": "harassment",          # default bucket for generic toxic
    "severe_toxic": "harassment",
    "identity_hate": "hate",
    "hate": "hate",
    "sexual_explicit": "profanity",
}


def _model_predict(text: str) -> Tuple[Optional[str], float]:
    clf = _ensure_model()
    if clf is None:
        return None, 0.0
    try:
        out = clf(text)
        # Handle both top-1 and top_k outputs
        if isinstance(out, list) and out:
            first = out[0]
            if isinstance(first, dict) and "label" in first:
                label = str(first.get("label", "")).lower().strip()
                score = float(first.get("score", 0.0) or 0.0)
                return label, score
            if isinstance(first, list) and first:
                label = str(first[0].get("label", "")).lower().strip()
                score = float(first[0].get("score", 0.0) or 0.0)
                return label, score
    except Exception:
        pass
    return None, 0.0


# -----------------------------
# Public API
# -----------------------------

def analyze_text(text: str) -> Dict[str, object]:
    """Analyze a text for toxicity using rules + (optional) model.

    Returns minimal contract.
    - status: "warning" or "clean"
    - message: present only when warning
    - type: category when warning
    - score: model score (0..1) or 0.0 when model not used/ready
    - matched_words: optional list of matched toxic words (rules)
    """
    text = (text or "").strip()
    if not text:
        return {"status": "clean"}

    # Rule-based
    rule_flag, rule_cat, matched = _rule_check(text)

    # Model-based
    model_label, model_score = _model_predict(text)
    model_cat: Optional[str] = None
    if model_label:
        model_cat = _MODEL_TO_CATEGORY.get(model_label, None)

    toxic_by_model = bool(model_cat) and model_score >= 0.60
    toxic_by_rules = bool(rule_flag)

    if toxic_by_rules or toxic_by_model:
        chosen_cat = rule_cat or model_cat or "harassment"
        result: Dict[str, object] = {
            "status": "warning",
            "type": chosen_cat,
            "score": round(float(model_score if toxic_by_model else 0.0), 3),
            "message": "This comment may be toxic",
        }
        if matched:
            result["matched_words"] = sorted(matched)
        return result

    return {"status": "clean"}
