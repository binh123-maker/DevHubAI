import re

# Regex patterns for matching semantic categories within content text
WARNING_PATTERNS = [
    r"\b(warning|caution|danger|alert|beware|hold on|important)\b",
    r"^>\s*\[!(warning|caution|danger|error)\]"
]

TIP_PATTERNS = [
    r"\b(tip|note|recommendation|best practice|idea|hint|remember)\b",
    r"^>\s*\[!(tip|note|important|info)\]"
]

DEFINITION_PATTERNS = [
    r"\b(is defined as|refers to|denotes|means|is the process of|is a term for)\b",
    r"^\*\*[^*]+\*\*\s+is\s+",
    r"^\*[^*]+\*\s+is\s+"
]

ALGORITHM_PATTERNS = [
    r"\b(algorithm|pseudocode|step\s+\d+|step\s+[a-zA-Z]+|firstly|secondly|finally)\b",
]

SUMMARY_PATTERNS = [
    r"\b(summary|in conclusion|to sum up|concluding|key takeaway|overall|in brief)\b"
]

EXAMPLE_PATTERNS = [
    r"\b(example|e\.g\.|for instance|for example|illustrates|illustration)\b"
]

QUESTION_PATTERNS = [
    r"^.*\?\s*$",  # Ends with a question mark
    r"^(why|how|what|who|when|where|is|are|can|do|does)\s+.*\?\s*$"
]

ANSWER_PATTERNS = [
    r"^(answer|ans|reply|response|a):\s+",
    r"\b(corresponds to|the solution is|answers the question)\b"
]

class SemanticRules:
    @staticmethod
    def is_warning(text: str) -> bool:
        return any(re.search(pat, text, re.IGNORECASE) for pat in WARNING_PATTERNS)

    @staticmethod
    def is_tip(text: str) -> bool:
        return any(re.search(pat, text, re.IGNORECASE) for pat in TIP_PATTERNS)

    @staticmethod
    def is_definition(text: str) -> bool:
        return any(re.search(pat, text, re.IGNORECASE) for pat in DEFINITION_PATTERNS)

    @staticmethod
    def is_algorithm(text: str) -> bool:
        return any(re.search(pat, text, re.IGNORECASE) for pat in ALGORITHM_PATTERNS)

    @staticmethod
    def is_summary(text: str) -> bool:
        return any(re.search(pat, text, re.IGNORECASE) for pat in SUMMARY_PATTERNS)

    @staticmethod
    def is_example(text: str) -> bool:
        return any(re.search(pat, text, re.IGNORECASE) for pat in EXAMPLE_PATTERNS)

    @staticmethod
    def is_question(text: str) -> bool:
        return any(re.search(pat, text, re.IGNORECASE) for pat in QUESTION_PATTERNS)

    @staticmethod
    def is_answer(text: str) -> bool:
        return any(re.search(pat, text, re.IGNORECASE) for pat in ANSWER_PATTERNS)
