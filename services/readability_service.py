import re


def _split_s(text):
    return [x for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x]


def _split_w(text):
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text)


def _syll(w):
    w = w.lower()
    vowels = "aeiouy"
    c = 0
    pv = False
    for ch in w:
        v = ch in vowels
        if v and not pv:
            c += 1
        pv = v
    if w.endswith("e") and c > 1:
        c -= 1
    return max(1, c)


def analyze_readability(text: str):
    s = _split_s(text)
    w = _split_w(text)
    syl = sum(_syll(x) for x in w) if w else 0
    if s and w:
        fre = 206.835 - 1.015 * (len(w) / len(s)) - 84.6 * (syl / len(w))
        fk = 0.39 * (len(w) / len(s)) + 11.8 * (syl / len(w)) - 15.59
    else:
        fre = fk = 0.0
    sug = []
    if s and (len(w) / len(s)) > 20:
        sug.append("Shorten long sentences: aim for 12–16 words per sentence.")
    if any(len(x) >= 13 for x in w):
        sug.append("Replace long words with simpler alternatives when possible.")
    if fre < 60:
        sug.append("Use bullets and plain language to improve readability.")
    return {
        "flesch_reading_ease": round(fre, 2),
        "flesch_kincaid_grade": round(fk, 2),
        "sentences": len(s),
        "words": len(w),
        "syllables": syl,
        "suggestions": sug,
    }
