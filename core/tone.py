import re

LEXICON = {
    "frustrated": ["frustrated", "annoyed", "ugh", "stupid", "broken", "won't work",
                   "doesn't work", "again", "still not", "hate", "useless", "damn",
                   "come on", "seriously", "why won't"],
    "happy": ["great", "awesome", "love", "nice", "perfect", "thanks", "thank you",
              "cool", "amazing", "yay", "excellent", "brilliant", "wonderful"],
    "sad": ["sad", "tired", "exhausted", "down", "unhappy", "depressed", "lonely",
            "miss", "upset", "hard day"],
    "stressed": ["stressed", "overwhelmed", "deadline", "too much", "can't keep up",
                 "anxious", "worried", "panic", "urgent", "no time"],
    "angry": ["angry", "furious", "mad", "rage", "pissed", "fed up", "sick of"],
    "curious": ["how does", "what is", "why", "wonder", "curious", "explain",
                "tell me about", "what's the difference"],
}

TONE_EMOJI = {
    "frustrated": "😤", "happy": "😊", "sad": "😔", "stressed": "😰",
    "angry": "😠", "curious": "🤔", "neutral": "🙂",
}

ADAPT_PREFIX = {
    "frustrated": "I hear you — let's sort this out. ",
    "stressed": "No problem, I'll keep this quick. ",
    "sad": "I'm on it. ",
    "angry": "Got it, let's fix this. ",
    "happy": "",
    "curious": "",
    "neutral": "",
}


def detect(text):
    text = (text or "").lower()
    scores = {}
    for tone, words in LEXICON.items():
        score = 0
        for w in words:
            if " " in w:
                if w in text:
                    score += 2
            elif re.search(r"\b" + re.escape(w) + r"\b", text):
                score += 1
        if score:
            scores[tone] = score

    if "!" in text:
        for t in ("frustrated", "angry", "happy"):
            if t in scores:
                scores[t] += 1

    if not scores:
        return "neutral", 0.0

    tone = max(scores, key=scores.get)
    confidence = min(scores[tone] / 4.0, 1.0)
    return tone, confidence


def emoji(tone):
    return TONE_EMOJI.get(tone, "🙂")


def adapt(tone, reply):
    return ADAPT_PREFIX.get(tone, "") + reply
