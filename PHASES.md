# PSE Linear A — Build Phases (living design)

Status: DESIGN ONLY. No build until "kreni". Ordered by dependency.
See THETA_MODES.md (theta core, readings, likelihoods) and GUI_DESIGN.md (UI, LLM, chat).

0. HARVEST (scraper) — FOUNDATION, nothing runs without it.
   Scrape all Linear A + Linear B material (SigLA, Younger, GORILA, papers); capture provenance +
   interest per source; costly/cheap-signal vetting; feeds the real-evidence clock.
   MINIMAL INPUT SANITIZATION from day one: scraped content + chat are UNTRUSTED and pass through the
   LLM -> prompt-injection surface. Basic sanitization/quarantine here; full Guardian unit in Phase 8.

1. CORPUS NORMALIZATION
   Unify scraped data into a canonical schema: sign-ID (GORILA) -> Linear B phonetic value ->
   context (commodity/number/position), BOTH scripts. The single substrate all engines read.

2. PSE KERNEL
   Core/Boundary/Organelle/Theta unit; action setpoints (SEEK 40 / CARE 30 / BUILD 20 / ORCH 10 /
   VERIFY excursion / peer x0.5); two-clock interaction model; LLR theta update; absorption gate
   (residency + k-independent tablets + MI>=0.70 + resample-stability); SharedLib orchestrator.

3. READING ENGINES
   Structural / lexical / phonetic LLR engines with their null models (permutation / collocation-MI /
   phonotactic-LM). Shared template, type-specific null. Where decipherment progress happens.

4. CALIBRATION (EXPERIMENT-4/5 analog) — HARD GATE.
   Tune eps, delta, MI gate, k, rescaled windows against KNOWN readings (KU-RO, KI-RO, numerals,
   fractions). Must reproduce known wins before ANY downstream output is trusted.

5. SWARM DYNAMICS
   Fission (S1/S2/S3), fusion, peer-collision/dedup (x0.5, both -> SharedLib), pathology/attractor
   detection on the RESIDUAL theta (phase-aware), Physician oversight. Makes it a swarm, not one unit.

6. LLM BINDING (PSE-L layer)
   Provider abstraction: Claude / Mistral / Groq (API) + local GGUF. Language I/O only (refutations,
   prognosis, chat, State-of-Knowledge prose); forbidden-terms + confidence-suppression gates.

7. VERIFY + HYPOTHESES
   Machine self-generates testable hypotheses (non-random prior); VERIFY excursion (spike -> return);
   LLM "what didn't work" refutation reports; human-asked tagging; graveyard.

8. GUARDIANS x2 (full — Section 10 cyber defense + epistemic defense)
   TWO independent Guardian units, one per surface. Both surfaces are the same PSE shape: adversarial
   CAPTURE of the Boundary/Registry (unearned absorption into Core); same SCHIZOID-capture temporal
   guard (low-and-slow implant) covers both.
   (a) EPISTEMIC Guardian: adversary game-form over sources; provenance/interest -> motive-tag on
       FALSE conclusions; cheap-signal red flags; enforce command != evidence. (Motive != falsity.)
   (b) CYBER Guardian (original Sec-10): protect the running system — prompt-injection via scraped
       pages + chat (biggest surface: untrusted text hits the LLM), credential/API-key protection,
       command-channel hijack, low-and-slow payload implant into Core.
   INDEPENDENCE: the two Guardians NEVER communicate directly (Direct Communication Prohibition) —
   they only report to SharedLib. So one cannot corrupt the other, and each (being itself a PSE unit
   that can go narcissistic/schizoid) is cross-checked by the other + the Physician. Each keeps its
   OWN theta in [25,35]. NMap-style anomaly axes + two-tier intervention per Sec 10.

## CONTROL MODEL (confirmed)
- The HUMAN is the sole EXTERNAL authority over SharedLib; that authority is non-overridable (human
  priority). No other human, no unit, can command SharedLib. SharedLib otherwise self-orchestrates
  within its rules.
- ALL units (workers, Guardians, Physician) report to SharedLib via PVP (monitored in real time).
  Units never command each other; SharedLib is the only orchestrator.
- SharedLib CREATES and RETIRES all units as needed (Fission Determinism; a unit cannot self-spawn
  or resist). Guardian recovery = REPLACEMENT, not remediation.
- SharedLib SPAWNS PSE units on demand (3-layer spawn assessment; fresh mission+lifespan each).
- Because human->SharedLib is control over the whole swarm, the CYBER Guardian must protect that
  command channel: hijacking it = hijacking SharedLib.

9. STATE OF KNOWLEDGE
   Read-only living document: probably true / false / uncertain, calibrated, append-only, timestamped,
   traceable to readings. The output-of-record.

10. GUI
    PySide6: screen-measuring shell (size before show), grouped launcher, 10 tabs, persistent chat
    pane (right 25%), shared reading-tab widget, Linear A glyphs (Noto Sans Linear A + GORILA fallback).

11. PACKAGING (.deb)
    Bundle font, .desktop entry, deps (system python3-pyside6 OR PyInstaller) via the PSE Jacobian
    pattern. Shippable.

NOTE: Phase 4 is the credibility gate — until the system reproduces KU-RO/KI-RO from clean data,
nothing downstream is trusted. This is the "smallest useful first step" built in as a gate.
Ordering is by dependency but adjustable.
