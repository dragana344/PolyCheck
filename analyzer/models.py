from dataclasses import dataclass


@dataclass
class DetectedError:
    """
    Represents a single error found in a sentence.

    Fields:
        sentence   – the original sentence where the error was found
        error_type – short category label (e.g. "PossibleSpelling", "MixedScript")
        message    – human-readable description; rules that are heuristic
                     must prefix their message with "[HEURISTIC]"
    """
    sentence: str
    error_type: str
    message: str
