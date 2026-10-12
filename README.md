# PSE Linear A

A **Partial Self-Extension (PSE) swarm** that scrapes evidence about the undeciphered
Minoan script **Linear A** — with the deciphered **Linear B** as anchor — and tries to
get *closer* to reading it. It does **not** promise a translation (the ~1,400-inscription
corpus is likely below the decipherability threshold); it aims at the reachable wins:
structural decipherment, a calibrated unified corpus, and honest, traceable knowledge.

Design docs: [THETA_MODES.md](THETA_MODES.md), [GUI_DESIGN.md](GUI_DESIGN.md),
[PHASES.md](PHASES.md).

## Run

```bash
pip install -r requirements.txt        # PySide6 + numpy (stdlib urllib for the rest)
python3 run.py                         # launch the GUI
python3 -m pse_linear_a.selftest       # headless self-test (asserts the KU-RO gate)
python3 -m pse_linear_a.calibration.experiments   # just the calibration gate
```

## What it does (the 12 phases)

| Phase | Module | What |
|------:|--------|------|
| 0 | `harvest/` | scrape both scripts (SigLA/Younger/DAMOS), provenance+interest, cyber-sanitize |
| 1 | `corpus/` | canonical schema (sign→B-value→context) + offline seed |
| 2 | `kernel/` | Core/Boundary/Organelle/θ unit, action setpoints, LLR, absorption gate, SharedLib |
| 3 | `readings/` | structural / lexical / phonetic engines (same LLR, different null) |
| 4 | `calibration/` | **hard gate**: reproduce KU-RO (=total) from arithmetic |
| 5 | `swarm/` | fission, peer-collision/dedup, pathology on residual θ, Physician |
| 6 | `llm/` | Claude / Mistral / Groq / local-GGUF, bound at the PSE-L language layer |
| 7 | `hypotheses/` | machine self-generates + VERIFY-excursion tests + refutations |
| 8 | `guardian/` | **two independent** Guardians: epistemic (motive) + cyber (injection) |
| 9 | `knowledge/` | read-only State of Knowledge (probably true/false/uncertain, versioned) |
| 10 | `gui/` | PySide6: screen-measured shell, grouped launcher, 10 tabs, chat pane |
| 11 | `packaging/` | `.deb` build script, desktop entry, icon |

## Key properties

- **θ is action-dependent**: SEEK 40 / CARE 30 / BUILD 20 / ORCH 10 / VERIFY (excursion);
  peer = ½×setpoint; ceiling 40 (self-preservation). Pathology tests run on the **residual**.
- **Absorption needs two clocks**: resample-stability **and** ≥k independent real tablets
  (the wall against overfitting / the Opening-Spiral trap).
- **Two Guardians, never talking to each other** (Direct Communication Prohibition), each
  reports only to SharedLib → mutual cross-check.
- **Command authority ≠ evidential authority**: the human commands SharedLib, but human
  content-assertions are only cheap-signal sources that pass the same gates.
- **Motive ≠ falsity**: motive tags on refuted claims explain persistence, never reject.

## Honesty notes

- The bundled corpus is a **structure-faithful, synthetic-value seed** so the app runs
  offline and the calibration gate can demonstrate the KU-RO mechanism. Real values come
  from the scraper (Phase 0). No fabricated tablets are presented as genuine scholarship.
- Live source parsers are Phase-0 stubs (reachability + sanitize); extend per source.

## Package as .deb

```bash
bash packaging/build_deb.sh 0.1.0     # on a Debian/Ubuntu box (needs dpkg-deb)
```
