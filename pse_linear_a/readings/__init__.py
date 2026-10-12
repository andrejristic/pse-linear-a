from .base import Reading, ReadingEngine, run_reading
from .structural import StructuralEngine
from .lexical import LexicalEngine
from .phonetic import PhoneticEngine

ENGINES = {"structural": StructuralEngine, "lexical": LexicalEngine, "phonetic": PhoneticEngine}
__all__ = ["Reading", "ReadingEngine", "run_reading", "StructuralEngine",
           "LexicalEngine", "PhoneticEngine", "ENGINES"]
