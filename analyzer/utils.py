"""
Shared algorithms used by multiple language rules.
Kept here so every language module can import them without circular deps.
"""


def levenshtein(a: str, b: str) -> int:
    """
    Classic iterative Levenshtein distance (edit distance).
    O(len(a) * len(b)) time, O(len(b)) space.
    Works on any Unicode string, so Cyrillic / Latin / mixed input is fine.
    """
    if len(a) < len(b):
        a, b = b, a

    if len(b) == 0:
        return len(a)

    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(
                prev[j + 1] + 1,   # deletion
                curr[j] + 1,       # insertion
                prev[j] + (ca != cb),  # substitution
            ))
        prev = curr

    return prev[-1]
