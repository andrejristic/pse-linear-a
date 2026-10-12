# PSE Linear A — GUI Design (living design)

Status: DESIGN ONLY. No build until "kreni".
Stack: PySide6, packaged as .deb (reuse the PSE Jacobian packaging pattern that works).

## Screen-measuring (REQUIRED): size to the screen BEFORE showing
Measure the screen the app opens on (pick the one under the cursor for multi-monitor),
then size/center before show().

    from PySide6.QtGui import QGuiApplication, QCursor
    screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
    avail  = screen.availableGeometry()        # excludes taskbar/panels
    dpr    = screen.devicePixelRatio()         # HiDPI
    w = max(1024, min(1600, int(avail.width()  * 0.90)))
    h = max(640,  min(1000, int(avail.height() * 0.90)))
    ui_scale = max(0.85, min(1.5, avail.width()/1920))   # scales fonts/margins
    win.resize(w, h)
    win.move(avail.x()+(avail.width()-w)//2, avail.y()+(avail.height()-h)//2)

Also: setHighDpiScaleFactorRoundingPolicy(PassThrough) before QApplication;
connect windowHandle().screenChanged to re-fit when dragged to another monitor.

## Tabs (10, opened from a launcher menu)
0. Overview   — "how close are we": absorbed readings by type, confidence over time, top candidates
1. Corpus     — scraped inscriptions for BOTH scripts: Linear A (target) + Linear B (deciphered
                anchor/scaffold). Sign string + transliteration + provenance + source trust badge.
                Linear B is first-class (shared signs -> phonetic values, KU-RO formats, the source
                of the phonotactic LM); it too has open/disputed readings that can be examined.
2. Structural — reading engine (shared template)
3. Lexical    — reading engine (shared template)
4. Phonetic   — reading engine (shared template)
5. Swarm / theta — live theta monitor, setpoint modes, pathology/attractor, fission + peer-collision events
6. Hypotheses — machine SELF-GENERATES testable hypotheses (non-random prior), self-investigates (VERIFY),
                self-writes "what didn't work" refutation reports. Human may also ask -> tagged source=human
                (human-asked prioritized, A5). Each hypothesis names its origin (machine vs human).
                FALSE/refuted conclusions get a MOTIVE tag: which neighboring group (and its modern
                descendants) would benefit economically/politically from the conclusion being accepted.
                Maps to the Guardian adversary-model (interest-alignment = a cheap-signal red flag,
                like a spoofed header -> down-weight). HONEST LIMIT: motive != falsity (no genetic
                fallacy). The tag RAISES the VERIFY bar and EXPLAINS why a debunked idea socially
                persists; it never rejects a claim on who said it. Scraper supplies the provenance +
                interest mapping. Tag lives mostly on already-refuted items.
7. Harvest    — scraper status, sources + costly/cheap trust scores, real-evidence clock
8. SharedLib  — Registry (absorbed readings), audit log, human-review queue
9. State of Knowledge — READ-ONLY living document, regenerated on every VERIFIED learning event:
                what is probably TRUE / probably FALSE / uncertain about Linear A. Human views, cannot edit.
                Calibrated & conditional (I-4/I-6, never "Linear A says X"). Append-only + timestamped
                (audit): every regeneration logged -> evolution of the knowledge state is visible.
                Each claim links to the supporting readings/evidence (traceability).

## LAUNCHER (grouped by data-flow pipeline, laid out left->right)
  INPUT/EVIDENCE   -> READING ENGINES        -> SWARM/CONTROL          -> OUTPUT
    Harvest (7)         Structural (2)            Swarm/theta (5)          Overview (0)
    Corpus (1)         Lexical (3)               SharedLib (8)            State of Knowledge (9)
                       Phonetic (4)              Hypotheses (6)
Default landing tab = Overview. The launcher doubles as a system diagram (evidence in ->
readings form -> swarm governs -> knowledge out).

## State of Knowledge = SEPARATE from Overview (resolved)
Overview = live-metrics cockpit (ephemeral, continuous). State of Knowledge = calibrated prose
manuscript (read-only, append-only, versioned, regenerated only on VERIFIED learning events).
Different medium, purpose, and lifecycle -> two tabs, not one.

## CHAT INTENT-SPLIT = hybrid (resolved): friction ~ blast radius
- advisory (question): default, zero friction.
- source ingestion: auto, but tagged + cheap-signal (low weight, can't harm); per-message
  "use as source" toggle.
- command: the only irreversible channel (spawns agents / mutates swarm) -> NEVER executed
  silently. Auto-classified but STAGED: show parsed intent -> require confirm. Explicit `/cmd`
  forces instruction intent but still shows parsed intent before executing.
- transparency: the machine displays its classification label on every human message.

## SCRAPER REQUIREMENTS (captured for Phase 0)
Beyond harvesting inscriptions, the scraper must:
- gather BOTH Linear A and Linear B material (B = the securely-read anchor).
- capture per-claim PROVENANCE + INTEREST mapping (publisher, affiliation, nationality, agenda)
  so conclusions can be flagged when they align with a source's economic/political interest
  (feeds the Hypotheses motive-tag + Guardian adversary-model). Motive-alignment = cheap-signal
  red flag only; it never decides truth.

## LLM BINDING (bound at the PSE-L layer only)
One provider interface, 4 backends: Claude (Anthropic API), Mistral (API), Groq (API),
local GGUF (llama.cpp, path on machine). Model configurable per provider (confirm exact Claude
model IDs at build via the claude-api skill; suggest stronger for synthesis, cheaper/local for bulk).
The LLM does LANGUAGE only (hypotheses, refutations, chat advisory, State-of-Knowledge prose, prognosis).
It does NOT replace the quantitative engines (structural/lexical/phonetic = the LLR math).
Corpus principle: PSE-L generator is the only place natural language is produced.

## CHAT PANE (right 25% of window, persistent across all tabs) — three roles
1. ADVISOR: human asks about Linear A; LLM answers (RAG over Registry/corpus). This is the CARE
   channel -> theta=30 (human anchor).
2. SOURCE INGESTION: relevant conversation mined as evidence for BOTH Linear A AND Linear B,
   tagged source=human-conversation (relevance-gated, not every line). Human conversation is an
   ADDITIONAL source (not the only one — all evidence is scraped); still cheap-signal weight.
3. COMMAND CHANNEL: human instructions route FIRST to SharedLib, which executes them per the Master
   Architecture (spawns PSE agents, etc.).

## GOVERNANCE INVARIANT: command authority != evidential authority
The human COMMANDS the swarm (boss level, via SharedLib) but CANNOT shortcut the evidence gates.
- instruction (command) = authoritative; SharedLib executes it.
- assertion about content ("I think it's Luwian") = a CHEAP-SIGNAL source only; enters low-weight,
  tagged, passes the same gates as any source.
So the operator cannot (even unintentionally) bias the corpus toward a pet theory. This is the
corpus-level guard against enmeshment.

## Shared reading-tab template (tabs 2-4: one widget, three instances)
  LEFT   candidate list, sort by theta_e, color = attractor health
  CENTER theta_e(r) trajectory + band(±5) + setpoint line + running LLR ledger
         + two clocks (real-evidence / resample) + VERIFY excursion marker
  RIGHT  NULL PANEL (type-specific):
           structural -> shuffle/permutation histogram w/ observed statistic marked
           lexical    -> collocation vs base-rate bars (MI)
           phonetic   -> phonotactic LM scores + alternative value candidates
  BOTTOM absorption gate (all must be green): residency, k-independent tablets,
         MI>=0.70, resample-stability
Same code as the formula: same LLR engine, only the null panel swaps by type.

## Glyphs
Linear A Unicode block U+10600-U+1077F. Render real glyphs with Noto Sans Linear A;
fallback to GORILA sign-numbers (AB01...) if font missing. Bundle the font in the .deb.

## Packaging
.deb via the PSE Jacobian pattern (system python3-pyside6 dep OR PyInstaller-bundle wrapped
in dpkg-deb) + .desktop entry + icon. Copy exactly what shipped for Jacobian.
