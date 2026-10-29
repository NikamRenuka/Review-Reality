"""Find which product aspects (battery life, screen, price, ...) each sentence talks about.

Method: keyword rules. Each aspect has a list of words or short phrases.
A sentence "mentions" an aspect if it contains one of them.
The lists came from the data: we looked for words that appear much more
often in 1-2 star reviews than in 4-5 star reviews (see docs/METHODOLOGY.md).
Keyword rules are simple and easy to check, but they miss some wording and
sometimes match the wrong meaning, so we always show example sentences.
"""
import re

ASPECTS = {
    "Battery life": [
        r"battery life", r"batteries? (?:die|died|dies|dying|drain\w*)", r"short life", r"drain(?:s|ed|ing)?",
        r"last(?:s|ed)? (?:only |about |just |less than )?(?:a |an |\d+ )?(?:few )?(?:minutes?|hours?|days?|weeks?|months?)",
        r"(?:don'?t|didn'?t|doesn'?t|do not|did not|does not|not) last", r"hold(?:s|ing)? (?:a |its )?charge",
        r"die(?:s|d)? (?:so |very |too |really )?(?:fast|quick|quickly|soon)", r"run(?:s)? out",
    ],
    "Leaking": [r"leak(?:s|ed|ing|age)?", r"acid", r"corro(?:sion|ded|de)"],
    "Defects & failures": [
        r"dead on arrival", r"\bdoa\b", r"bad batch", r"defective", r"(?:didn'?t|did not|doesn'?t|does not|won'?t) work",
        r"stopped working", r"quit working", r"broke(?:n)?", r"(?:were|was|arrived|came) dead", r"dead (?:out of|in) the (?:box|package)",
    ],
    "Charging & ports": [r"charg(?:er|ing|es)", r"charge port", r"\bport\b", r"\busb\b", r"\bcable\b", r"take(?:s)? forever to charge"],
    "Speed & performance": [
        r"\bslow(?:er|ly|ness)?\b", r"\blag(?:s|gy|ging)?\b", r"freez(?:e|es|ing)", r"froze(?:n)?", r"crash(?:es|ed|ing)?",
        r"sluggish", r"buffer(?:s|ing)?", r"processor", r"takes forever",
    ],
    "Screen & display": [r"screen", r"display", r"resolution", r"glare", r"bright(?:ness)?", r"backlight"],
    "Sound & audio": [r"\bsound\b", r"audio", r"volume", r"\bbass\b", r"\bloud(?:er|ness)?\b", r"speaker quality"],
    "Connectivity & setup": [
        r"wi-?fi", r"bluetooth", r"connect(?:s|ed|ing|ion|ivity)?", r"set ?up", r"\bpair(?:ing|ed)?\b", r"network", r"internet",
    ],
    "Voice assistant": [
        r"\balexa\b", r"voice (?:command|recognition|control|assistant)",
        r"(?:doesn'?t|does not|didn'?t|did not|can'?t|cannot|won'?t) (?:always )?understand", r"understands? (?:me|my|what|you)",
        r"answer(?:s|ed)? (?:my |your |any |most |all )?questions",
    ],
    "Apps & content": [r"\bapps?\b", r"google play", r"play store", r"netflix", r"youtube", r"\bcontent\b", r"games?"],
    "Ads & special offers": [r"\bads\b", r"advert\w*", r"special offers", r"lock ?screen"],
    "Price & value": [r"\bprice\b", r"\bvalue\b", r"\bmoney\b", r"\bcost(?:s)?\b", r"expensive", r"\bcheap(?:er)?\b", r"worth", r"\bdeal\b"],
    "Support & returns": [r"return(?:ed|ing)?", r"refund", r"warranty", r"customer (?:service|support)", r"\bsupport\b", r"replace(?:d|ment)?"],
    "Remote": [r"\bremote\b"],
    "Build & durability": [r"flimsy", r"sturdy", r"durab\w+", r"plastic", r"crack(?:ed|s)?", r"build quality", r"well (?:made|built)", r"cheaply made"],
    "Kids & parental controls": [r"\bkids?\b", r"child(?:ren)?", r"parental", r"freetime", r"grand(?:son|daughter|kids?)"],
    "Storage & memory": [r"storage", r"memory", r"sd card", r"\d+ ?gb\b"],
}

# Aspects that describe the device a product is used in, not the product itself.
# Example: "the batteries in my remote died" is about battery life, not about a remote.
NOT_RELEVANT = {
    "Batteries": {
        "Remote", "Screen & display", "Apps & content", "Voice assistant", "Ads & special offers",
        "Storage & memory", "Kids & parental controls", "Sound & audio", "Connectivity & setup",
    },
}


def is_relevant(aspect, category):
    return aspect not in NOT_RELEVANT.get(category, set())


_PATTERNS = {aspect: re.compile("|".join(f"(?:{word})" for word in words), re.IGNORECASE) for aspect, words in ASPECTS.items()}
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+|\n+")


def split_sentences(text):
    """Split review text into sentences (simple rule: split after . ! ? or at line breaks)."""
    if not isinstance(text, str):
        return []
    return [s.strip() for s in _SENTENCE_END.split(text) if len(s.strip()) > 2]


def find_aspects(sentence):
    """Return the list of aspects a sentence mentions (can be empty)."""
    return [aspect for aspect, pattern in _PATTERNS.items() if pattern.search(sentence)]
