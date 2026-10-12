"""Single source of truth for every PSE Linear A constant.

Generalizes the PSE Master Architecture's single human-facing 30/+-5 theta into
ACTION-DEPENDENT setpoints (THETA_MODES.md). theta is expressed as a percentage
[0,100] (30.00 == 0.30 fraction).
"""
from __future__ import annotations

# --- Conservation of Self (hard) ---
SELF_WEIGHT_MIN = 0.50          # theta_s > 0.5 necessary; Other < 50 ALWAYS
OTHER_WEIGHT_MAX = 0.30         # corpus CARE-mode boundary budget (fraction)

# --- Action-dependent theta setpoints (percent). Band is always +-5. ---
THETA_SETPOINTS = {
    "SEEK": 40.0,   # ingest/scrape: max permeability (30+10)
    "CARE": 30.0,   # human-facing anchor
    "BUILD": 20.0,  # assert/produce: protect core (30-10)
    "ORCH": 10.0,   # SharedLib(boss) reaches Core structurally, not via boundary
}
THETA_BAND = 5.0
THETA_CEILING = 45.0            # SEEK 40 +5 = 45 < 50 (self-preservation floor)
PEER_FACTOR = 0.5              # peer-directed theta = 0.5 * current setpoint
VERIFY_EXCURSION_PEAK = 38.0   # VERIFY spikes here, then must RETURN
VERIFY_RETURN_TOL = 3.0        # must come back within this of the pre-excursion baseline

# --- Health / pathology (on RESIDUAL theta = theta - setpoint(current phase)) ---
SIGMA_HEALTHY = (0.015 * 100, 0.03 * 100)   # -> (1.5, 3.0) in percent
SIGMA_SCHIZOID = 0.01 * 100                  # < 1.0 percent over window -> schizoid screen
STABILITY_WINDOW_RESAMPLE = 10000            # resample clock window
STABILITY_WINDOW_REAL = 200                  # real-evidence clock window (tiny corpus!)

# --- Absorption gate (reading earns constitutive status) ---
# TWO CLOCKS: resample (stability) AND real-evidence (genuine support).
ABSORB_RESIDENCY_RESAMPLE = 1000    # bootstrap resamples survived
ABSORB_REAL_EVIDENCE_MIN = 3        # k INDEPENDENT real tablets (anti-overfit wall)
ABSORB_WEIGHT_MIN = 10.0            # theta_e >= 10 (percent) sustained
ABSORB_STABLE_STEPS = 100           # ... for >= this many consecutive resamples
ABSORB_MI_MIN = 0.70               # MI(reading; corpus | null) >= 0.70
ABSORB_RESAMPLE_STABILITY_MAX_SIGMA = 4.0   # sigma(theta_e) across resamples must be below this

# --- LLR update ---
LLR_ETA = 1.0                  # theta_e step size on log-likelihood-ratio
LLR_LOG_RATIO_CLAMP = 6.0      # clamp a single evidence LLR to +-this (robustness)

# --- Peer collision / dedup ---
DEDUP_SIMILARITY = 0.85        # two units' tasks considered redundant above this

# --- Guardian (Section 10) ---
GUARDIAN_THETA_MIN, GUARDIAN_THETA_MAX = 25.0, 35.0
RISK_ELEVATED_T, RISK_CRITICAL_T = 0.35, 0.65
BENIGN, ELEVATED, CRITICAL = 0, 1, 2
CHEAP_SIGNAL_WEIGHT = 0.05     # a bare assertion / motivated claim enters at this weight
COSTLY_SIGNAL_WEIGHT = 0.20    # peer-reviewed / corroborated source

# --- Reading types ---
STRUCTURAL, LEXICAL, PHONETIC = "structural", "lexical", "phonetic"
READING_TYPES = (STRUCTURAL, LEXICAL, PHONETIC)
# confidence hierarchy weights (structural > lexical > phonetic)
TYPE_PRIOR = {STRUCTURAL: 0.50, LEXICAL: 0.33, PHONETIC: 0.17}

# --- LLM providers ---
PROVIDERS = ("claude", "mistral", "groq", "local_gguf")
LOCAL_GGUF_BASE_URL = "http://localhost:1234/v1"   # LM Studio OpenAI-compatible default

# --- Linear A / B Unicode blocks ---
LINEAR_A_UNICODE = (0x10600, 0x1077F)
LINEAR_B_SYLLABARY = (0x10000, 0x1007F)
