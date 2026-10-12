# PSE Linear A — Theta Setpoint Model (living design)

Status: DESIGN ONLY. No build until "kreni".
Context: PSE swarm applied to Linear A decipherment. This file specifies how theta
(other-directed compute %) behaves per ACTION, generalizing the corpus's single
human-facing 30/±5 to a set of action-dependent setpoints.

## Core principle
theta setpoint = f(action) = "how much this action requires the environment to change me."
- Seeking → shrink self → theta UP (let the world in).
- Building → grow self → theta DOWN (resist change, protect core).
It is a property of the ACTION, not of the agent. One agent slides its setpoint across
a work cycle.

## Setpoints (band is always ±5)
| mode          | central θ | band     | rationale |
|---------------|-----------|----------|-----------|
| SEEK / ingest | 40        | [35,45]  | max permeability; absorb evidence |
| CARE (human)  | 30        | [25,35]  | bounded care; the anchor (from corpus) |
| BUILD / assert| 20        | [15,25]  | close up, protect core while producing |
| ORCHESTRATION | 10        | [5,15]   | SharedLib (boss) reaches Core structurally, not via boundary |

Mnemonic symmetry: SEEK = 30+10, BUILD = 30−10 (mirrors around the human anchor).

## Hard ceiling
theta_s > 0.5 is necessary (below = identity dissolution) → Other < 50 ALWAYS.
So no central value above ~45 (SEEK at 40 → +5 = 45, safe). 40 is the max setpoint.

## Peer is a MODIFIER, not a mode
Peer-directed theta = 0.5 × (current mode's central value).
Derives the corpus's COLLABORATIVE_BUDGET = 0.15 as the CARE-mode case (0.5 × 30).
Generalizes: SEEK→peer 20, CARE→peer 15, BUILD→peer 10, ORCHESTRATION→peer 5.
Meaning: permeability to a peer tracks how open you currently are, halved (peer ≠ human).

## Phase-aware fission detection (required)
An agent cycling SEEK(40)→BUILD(20)→report(10) oscillates by phase. The fission
detector must NOT read this as Scenario-1 aspectual incoherence.
Fix: test the RESIDUAL, not raw theta.
    theta_residual = theta_observed − setpoint(current_action_phase)
Run S1/pathology tests (MI, sigma, mu) on theta_residual. Requires the agent's
PHASE TIMELINE (which setpoint was active when). Real S1 = residual itself is bimodal
w.r.t. an EXTERNAL user mode.

## Sixth mode (CONCLUDED): VERIFY
Not a flat setpoint — a controlled excursion (engage-then-return).
Per No-Immunity: to test a reading honestly the agent must let it genuinely move it
(theta spikes ~35-40), then health = the RETURN to baseline.
- returns → reading did not survive (healthy skeptic).
- does not return → reading is real (legit absorption) OR agent was seduced (overfit)
  → flag for external check.
This is the anti-overfitting engine and the Empathic-Infection→self-healing cycle
applied to candidate readings.
Alt candidate for sixth: INWARD/CONSOLIDATE (self-reorganization of registry, lowest
theta, mirror of SEEK).

## ENTITY & UPDATE MODEL (CONCLUDED)

### Other = candidate reading (role-dependent)
- decipherment worker (PRIMARY): Boundary registers a **candidate reading** =
  (target, proposed_value, scope, evidence). Absorption = reading earns constitutive status.
- harvest/scraper (Guardian-style): Boundary registers a **source**; absorption =
  source earns trust via costly-signal history.
- hypothesis-language ("Minoan = Luwian"): DOES enter the Boundary as a TRANSIENT entity,
  engaged via the VERIFY excursion — precisely so the system (via its bound LLM) can
  generate a solid domain-language explanation of WHY it fails. Normal product = a
  documented refutation (negative result harvested to SHARED_LIB.accumulated_knowledge;
  protects the swarm from re-absorbing debunked ideas). It passes THROUGH (engaged, then
  rejected as transient, w->0); it is NOT routinely absorbed.
  PERMANENT organelle-absorption of a hypothesis-language stays the rare, fully-gated,
  human-confirmed event — a whole agent captured by one language theory IS the enmeshment
  pathology ("went native on Luwian"). Entering to refute != being absorbed.
  Boundary-entity (transient) vs organelle (permanent) is the distinction; do not conflate.
  Aggregate stance over hypotheses (which family the evidence favors) = Seldon macro level.

### Interaction = one bootstrap-resample test of a reading (TWO CLOCKS)
Fixed corpus (~1,400) cannot feed PSE windows; bootstrap is the correct tool for small n.
- real-evidence clock: increments only on genuinely new evidence (new tablet/source). Scarce.
- resample clock: increments per bootstrap draw. Unlimited. Drives theta variance = stability.
- Absorption requires BOTH: reading rests on >= k INDEPENDENT real tablets AND holds across
  resamples. Resample-volume alone = the Opening-Spiral overfit trap.
- sigma(theta_e) across resamples = reading robustness (attractor shape).

### Interaction types (full list)
- READING x RESAMPLE (primary theta driver): one bootstrap-resample test of a reading, as above.
- REAL-EVIDENCE ENCOUNTER: scraper delivers a genuinely new tablet/source; increments the
  real-evidence clock (scarce).
- HYPOTHESIS ENGAGEMENT (VERIFY): a language-hypothesis enters the boundary, is engaged, and
  (usually) yields an LLM refutation-explanation harvested to SHARED_LIB.
- PEER COLLISION / DEDUP: unit A discovers via peer contact that unit B already did/does task T.
  Handshake runs at PEER theta = 0.5 x current setpoint. They do NOT both do T (avoid a wasteful
  all-pay contest); BOTH return to SHARED_LIB; the redundant unit is harvested (contribution +
  termination, or Null-State death). SHARED_LIB records the dedup to prevent future collisions on T.

### theta formula = log-likelihood-ratio, reading vs null
    theta_e(r)_{t+1} = clip[ theta_e(r)_t + eta * log( P(evidence_t | r) / P(evidence_t | null) ) ]
- evidence_t = the resample draw at step t.
- revision magnitude = the (signed) LLR; support raises theta_e, disconfirmation lowers it.
- null-margin = the denominator P(.|null); anchors theta to statistical honesty.
- absorption MI gate: MI(reading; corpus | null) >= 0.70 (corpus's MI(psi;C)>=0.70).
- GLOBAL theta = sum of theta_e over active readings, capped at the mode setpoint.
  => setpoint = the boundary budget of that action (SEEK 40%, BUILD 20%, ...).
     Corpus's sum(alpha)<=0.30 is just the CARE-mode special case.

## DATA REALITY (foundational)
There is NO local seed corpus. ALL Linear A evidence must be scraped from the internet; the
HARVEST layer is the foundation (Phase 0), not a secondary layer.
- real-evidence clock starts at 0; fed entirely by the scraper.
- source costly/cheap-signal vetting is load-bearing (garbage sources -> garbage corpus).
- build order once "kreni": scraper FIRST, then workers can resample/read.
- known targets: SigLA (sigla.phis.me), John G. Younger's Linear A texts, GORILA refs,
  academic papers.

## LIKELIHOOD MODELS per reading type (CONCLUDED)
Same LLR everywhere; only the EVIDENCE CHANNEL and NULL MODEL differ.
    theta_e(r) += eta * log( P(evidence_t | r) / P(evidence_t | null) )

STRUCTURAL (strongest, language-free). e.g. W = summation marker (KU-RO).
  evidence_t = a resampled accounting tablet w/ W; does the arithmetic hold?
  P(e|r) = 1 - eps   (eps = damage/scribal-error rate ~0.05-0.15)
  P(e|null) = pi_0 = P(any word's neighbor coincidentally = sum), COMPUTED by permutation
    (shuffle which word is "W" across corpus, measure coincidence rate ~0.01-0.03).
  => LLR_+ ~ log(0.9/0.02) ~ +3.8 per confirming tablet; miss ~ log(0.1/0.98) ~ -2.3.
  KEY: the null IS the resample distribution under label-shuffling. Same bootstrap gives
  both stability and null. This is how KU-RO was actually deciphered.

LEXICAL (collocation / MI). e.g. W means "wine" (semantic class, not position).
  evidence_t = a resampled occurrence of W; which logogram/context co-present.
  P(L present | W,r) = q_r (~0.7-0.9 if W really tags logogram L)
  P(L present | null) = b_L (base rate of L, e.g. 0.05)
  => LLR = log(q_r/b_L) when L present (~+2.8); log((1-q_r)/(1-b_L)) when absent.
  This is literally pointwise-MI accumulation -> feeds the MI(reading;corpus|null)>=0.70 gate.
  CAVEAT: common logograms co-occur with everything (high b_L -> small LLR, self-protecting).
  Cross-linguistic cognate match = WEAK, prior-dependent (spurious-cognate risk) -> down-weight;
  lean on internal collocation.

PHONETIC (phonotactic regularity, weakest, highest overfit). e.g. Linear-A-only sign S = /va/.
  evidence_t = a resampled word with S; phonotactic plausibility of the transliteration under a
    phonotactic LM TRAINED ON SECURELY-VALUED (Linear-B-shared) signs.
  P(e|r) = LM(word | S->/va/)
  P(e|null) = E_v[LM(word | S->v)]  (marginalize over random value v for S)
  => LLR = log( LM(word|S=/va/) / avg over v ). Positive iff /va/ makes the word more regular
  than a random value. Needs many words + cross-checks; MOST VERIFY excursions.

HIERARCHY & INTERDEPENDENCE: confidence structural > lexical > phonetic; they bootstrap each
other (Ventris order: grid/structure -> phonetic -> lexical). Null models of later types are
CONDITIONED on already-absorbed earlier readings (Registry filling sharpens the next layer's null).

## Open decisions (remaining)
(none blocking — theta core design complete. Next: scraper architecture Phase 0, on "kreni".)
