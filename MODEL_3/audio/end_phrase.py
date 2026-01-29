import re

# Define END PHRASES (session termination commands)
def EndPhrases(wake_word):
    end_phrases = [
        # English
        "bye",
        "bye bye",
        "goodbye",
        "good night",
        "see you",
        "see you later",
        "stop",
        "close",
        "exit",
        "quit",
        "end",
        "okay bye",
        "that's all",
        "that's all, thanks",
        "we're done",
        
        # German
        "tschüss",
        "tschuess",
        "auf wiedersehen",
        "auf wiedersehn",
        "ciao",
        "mach's gut",
        "machts gut",
        "beenden",
        
        # Wake word specific
        f"bye {wake_word}",
        f"stop {wake_word}",
        f"close {wake_word}",
        f"exit {wake_word}",
        f"tschüss {wake_word}",
    ]

    # Join phrases into a single alternation pattern, escaping them to avoid regex issues
    joined = "|".join(re.escape(p) for p in end_phrases)

    # Compile once: match any full phrase (word boundaries), case-insensitive
    _end_re = re.compile(rf"\b({joined})\b", flags=re.IGNORECASE)
    
    return _end_re
