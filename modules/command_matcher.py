# modules/command_matcher.py
# Fuzzy-matches recognized ASR text to known VISION commands.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rapidfuzz import fuzz, process

# ---------- Known trigger phrases ----------
TRIGGER_PHRASES = {
    "describe":     ["describe", "what do you see", "what is in front of me",
                     "what is around me", "scene", "look around"],
    "distance":     ["distance", "how far", "what is ahead", "how close"],
    "stop":         ["stop", "cancel", "never mind", "quit search"],
    "left":         ["what is on my left", "what is to my left", "left side"],
    "right":        ["what is on my right", "what is to my right", "right side"],
    "closest":      ["what is closest", "what is nearest", "closest object",
                     "nearest object", "what is closest to me"],
    "path_clear":   ["is the path clear", "is it safe to walk", "is it clear ahead",
                     "can i walk forward", "is the way clear"],
    "repeat":       ["repeat", "say that again", "what did you say",
                     "repeat that", "again"],
    "battery":      ["battery", "battery status", "system status",
                     "how much battery", "power level"],
    "count":        ["how many", "count"],
    "read":         ["read", "read text", "read sign", "what does it say",
                     "read that", "what is written"],
    "help":         ["help", "what can you do", "commands", "what can i say",
                     "list commands", "what commands"],
}

# ---------- All 80 COCO class names ----------
COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train",
    "truck", "boat", "traffic light", "fire hydrant", "stop sign",
    "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep",
    "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
    "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard",
    "sports ball", "kite", "baseball bat", "baseball glove", "skateboard",
    "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork",
    "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "couch", "potted plant", "bed", "dining table", "toilet", "tv",
    "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave",
    "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase",
    "scissors", "teddy bear", "hair drier", "toothbrush"
]

# ---------- Aliases for natural spoken variants ----------
COCO_ALIASES = {
    "people":      "person",
    "man":         "person",
    "woman":       "person",
    "human":       "person",
    "phone":       "cell phone",
    "phones":      "cell phone",
    "mobile":      "cell phone",
    "television":  "tv",
    "sofa":        "couch",
    "table":       "dining table",
    "plant":       "potted plant",
    "fridge":      "refrigerator",
    "motorbike":   "motorcycle",
    "aeroplane":   "airplane",
    "mug":         "cup",
    "bag":         "handbag",
}

FUZZY_MATCH_THRESHOLD = 70
DID_YOU_MEAN_THRESHOLD = 50

HELP_TEXT = (
    "Available commands: "
    "Say Find, followed by an object name to search for it. "
    "Say Describe or What do you see for a scene description. "
    "Say Distance or How far for distance to nearest object. "
    "Say What is closest to me for the nearest object. "
    "Say Is the path clear to check if it is safe ahead. "
    "Say What is on my left or right for directional awareness. "
    "Say How many, followed by an object to count them. "
    "Say Read to read any visible text. "
    "Say Battery for battery status. "
    "Say Repeat to hear the last announcement again. "
    "Say Stop or Cancel to return to normal detection mode. "
    "Say Help to hear this list again."
)


def resolve_class(text):
    """
    Resolves natural spoken words to COCO class names.
    Checks aliases first, then fuzzy matches against COCO_CLASSES.
    """
    text = text.lower().strip()
    if text in COCO_ALIASES:
        return COCO_ALIASES[text]
    match = process.extractOne(text, COCO_CLASSES, scorer=fuzz.WRatio)
    if match and match[1] >= FUZZY_MATCH_THRESHOLD:
        return match[0]
    return None


class CommandMatcher:
    def __init__(self):
        self._all_triggers = []
        for intent, phrases in TRIGGER_PHRASES.items():
            for phrase in phrases:
                self._all_triggers.append((phrase, intent))

    def match(self, text):
        text = text.lower().strip()
        result = {
            "intent": None,
            "target": None,
            "raw": text,
            "did_you_mean": None
        }

        # --- "find [object]" ---
        if text.startswith("find "):
            target_text = text[5:].strip()
            resolved = resolve_class(target_text)
            if resolved:
                result["intent"] = "find"
                result["target"] = resolved
            else:
                match = process.extractOne(target_text, COCO_CLASSES, scorer=fuzz.WRatio)
                if match and match[1] >= DID_YOU_MEAN_THRESHOLD:
                    result["did_you_mean"] = f"find {match[0]}"
            return result

        # --- "how many [object]" ---
        if "how many" in text:
            remaining = text.replace("how many", "").strip()
            if remaining:
                resolved = resolve_class(remaining)
                if resolved:
                    result["intent"] = "count"
                    result["target"] = resolved
                    return result
            result["intent"] = "count"
            result["target"] = None
            return result

        # --- fuzzy match against trigger phrases ---
        phrase_list = [p for p, _ in self._all_triggers]
        match = process.extractOne(text, phrase_list, scorer=fuzz.WRatio)

        if match and match[1] >= FUZZY_MATCH_THRESHOLD:
            matched_phrase = match[0]
            for phrase, intent in self._all_triggers:
                if phrase == matched_phrase:
                    result["intent"] = intent
                    break
        elif match and match[1] >= DID_YOU_MEAN_THRESHOLD:
            result["did_you_mean"] = match[0]

        return result

    def get_help_text(self):
        return HELP_TEXT


# ---------- Standalone test ----------
if __name__ == "__main__":
    matcher = CommandMatcher()

    tests = [
        "find bottle",
        "find bottel",
        "how many people",
        "how many chairs",
        "describe",
        "what do you see",
        "how far is it",
        "stop",
        "what is on my left",
        "what is closest to me",
        "is the path clear",
        "repeat",
        "battery",
        "read",
        "help",
        "what can you do",
        "find zzzxxx",
    ]

    for t in tests:
        r = matcher.match(t)
        print(f"Input: '{t}'")
        print(f"  intent={r['intent']} target={r['target']} did_you_mean={r['did_you_mean']}")
        print()
