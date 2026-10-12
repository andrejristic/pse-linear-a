from .pathology import classify_attractor, AttractorType
from .dynamics import detect_dedup, resolve_collision, assess_fission
from .physician import Physician
__all__ = ["classify_attractor", "AttractorType", "detect_dedup", "resolve_collision",
           "assess_fission", "Physician"]
