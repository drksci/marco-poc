# Captured external synthesis, 25 Sep 2026

**Provenance:** pasted into the session by the operator on 25 Sep 2026. It is an
external AI assistant's synthesis about MARCO, not this repository's own output,
and not a source of evidence. It is captured here so none of its detail is lost
before it is reconciled.

**Status: UNRECONCILED.** Every number below is a claim by that draft until
`notes/claims-reconciliation.md` marks it VERIFIED against `evidence/`. Nothing
here may be asserted on a page without that check. Numbers this repository
already measures are marked with a check where the operator's draft happens to
agree.

---

## 1. The protocol, as that draft explains it in accessible terms

- The problem: software identifies things with internal labels (`room-2041`) or
  raw coordinates. Handed to another system, a label means nothing unless both
  sides share a central lookup table. MARCO replaces the central table with
  addresses derived from a description of the situation.
- **45 ordinary yes-or-no questions** about the surroundings, covering what the
  occupant can see, reach, change, who is present, and what risks exist, with
  examples "I can see out of this place", "I can reach objects near me",
  "Things here can break". The draft also says the 45 questions fall into
  **eight categories**: visibility, reachability, agency/change, who is present,
  spatial permanence, timing, knowledge state, risks.
- Answers become scores, then **90 binary ticks**, grouped into **18 chunks of
  five bits**, each mapped through a **32-syllable codebook** built so that
  similar situations produce similar-sounding words.
- The 18 syllables form a speakable address in **four beats** (place, what,
  reach, now), e.g.
  `ma.mo.ma.ma.ru · ma.va.ki.va.mo + ve.ki.va.tu.ru ~ ki.su.ki`.
- Precision is adjustable like a postcode prefix: the first few syllables give a
  region, all 18 give fine detail.
- A separate **root** is a 64-character SHA-256 fingerprint of the exact
  statement set, for verifying "the same" rather than "near".
- The shared **3,300-byte seed** carries rules, not tables, so each side
  rebuilds the same frame locally, instead of shipping the 67 KB a registry
  style exchange needs.

## 2. The "wow" finding as that draft states it

Six independent model families (the draft names GPT, DeepSeek, Gemma, GLM and
Mimo) with no shared weights and no shared context were shown plain text room
descriptions and selected identical statement sets and identical addresses
**96.7% of the time, 87 of 90 comparisons**. The draft's reading: independently
trained models converge on a shared underlying manifold, a common structural
understanding of situations and space.

The draft also notes, correctly, that the source document does not itself cite
third-party academic literature on representation alignment.

## 3. Non-determinism into determinism, dynamic ladders and gradients

This is the operator's specific point: the seed can be anything, the ladders and
gradients are dynamic, the models are non-deterministic, and the roots are
deterministic and still agree across models.

- **Model non-determinism:** the draft says DeepSeek marked 17 statements true
  while GLM and Mimo marked 19, for the same kitchen description.
- **Deterministic roots:** once a model outputs its set, a fixed rule
  (SHA-256 over canonical JSON) produces the 64-character root.
- **Cross-model convergence:** for unambiguous rooms such as a locked storeroom
  or a dark empty room, the draft says independent families selected the exact
  same statements, giving byte-identical roots across **5 of 6 model families**.
- **Certainty ladder:** five markers `=`, `⊢`, `≈`, `~`, `?`, with the overall
  certainty of a reading governed by the `weakest()` rule, so a soft guess can
  never be promoted to a hard fact.
- **Distance gradients:** answers map to **four distance values, 0.0, 0.3, 0.6,
  0.9**, by group relationship, turning yes/no answers into graded nearness.
- **Dynamic question ordering:** the seed holds no fixed list of question
  positions. It holds a procedural rule, described in the draft as a
  three-number rule with `"order": "descending-variance"`. Each system generates
  **204 reference places**, measures answer variance across them, and asks the
  high-variance questions first.
- **Root invariance across different geometry:** if two systems differ in a seed
  parameter such as `minhash_seed`, their geometries become incommensurable and
  address distance comparisons are refused, but the draft says exact root
  verification still works, because the root depends only on statement text and
  the canonical hashing rule.
- The draft's framing sentence: "Feel freely. Anchor what you can."

## 4. Prior art, as that draft differentiates it

| Domain | Prior art, per the draft | What the draft claims is new |
|---|---|---|
| Geohashing, H3, Plus Codes | fixed 2D physical coordinates from latitude and longitude, which ignore interior state, visibility and risk | situational coordinates: visibility, reach, agency and risk rather than physical position, so two identical locked storerooms anywhere on Earth get the same address |
| What3Words | a centralised three-word database owned by an authority | zero-registry procedural generation: no server, no lookup table, generated locally from a 3,300-byte seed |
| Vector databases and embeddings (FAISS, Pinecone, cosine) | opaque float vectors, tied to one model family, needing translation matrices across models | model-agnostic, human-speakable addresses plus cryptographic roots that work across architectures without sharing vectors |
| API registries and schemas (OpenAPI, Schema.org) | large static lists, manual versioning, central distribution | procedural compression: ship the rule, rebuild the frame on arrival |

Genuinely new ground, from `NEW_VS_COVERED_GROUND.md`: **N1** a proof-anchored
epistemic metric space, fusing metric geometry, cryptographic proof and
stratified certainty; **N2** Gray-coded pronounceable locality-preserving codes,
combining proquints, geohashing and Gray-coded adjacency; **N3** the stratified
epistemic grammar and its non-promotion safety rule. Covered ground to cite
as-is: MinHash/SimHash, LSH, Landmark MDS, Merkle trees, geohashing, proquints.

## 5. Figures the draft proposes

1. **The dual-output pipeline.** One box, 19 true statements, splitting into a
   nearness branch (90 ticks to 18 syllables to four beats) and an identity
   branch (statement text to canonical JSON to SHA-256 to a 64-character root).
   Caption: identity and location are deliberately separated; the address
   measures proximity, the root guarantees exact equality.
2. **The seed compression pyramid.** Three bars: registry 67,561 bytes, frame
   rebuilt on arrival 4,532 bytes, seed transmitted 3,300 bytes, with the draft
   adding "4.88% of the registry" and "95.1% payload reduction", and calling out
   the small `partition` rule as the engine that replaces static lists.
3. **Non-deterministic evaluation against the certainty ladder.** A five-rung
   ladder with a threshold line between the top two rungs and the bottom three,
   showing a whole reading dropping to the weakest rung present, then three
   models feeding one hashing funnel that outputs one identical root.
4. **Emergent manifold convergence against the synergistic core.** Side by side:
   an inverted-U curve for synergy peaking in the middle layers with redundancy
   troughing there, and a topological surface where five model families converge
   on the same node.
5. **MARCO overlay against `agent://` routing.** Two isolated servers depending
   on a fragile central lookup, against two agents broadcasting addresses and
   matching at a phonetic distance of two syllables.
6. **The whale coda analogy.** Sperm whale pod dialects and multi-resolution
   humpback song paired with address precision: a short prefix gives a coarse
   bearing, the full pattern gives exact location.

## 6. Prose snippets the draft offers

- On non-determinism into determinism: different models may judge a scene with
  slight variance, and the certainty ladder with its `weakest()` rule anchors
  final claims into a 64-character root.
- On seed invariance: if two machines change a seed parameter their distance
  measurements become incommensurable and the system refuses to compute
  distance, while root verification stays invariant, so exact state identity can
  still be confirmed.

## 7. Original Noumena work the draft says to incorporate

Source documents live in `/Users/blake/Projects/noumena/docs/` (and a copy in
`marco-noumena-handover-20260925/docs/`): `00_source_conversation.md`,
`GROUNDING_MECHANISMS.md`, `CONCEPT_INDEX.md`, `NEW_VS_COVERED_GROUND.md`,
`EXPERIMENTS.md`, `DIRECTION_TRANSPLANTATION.md`, `ideas_registry.md`,
`intermediate_report_20260916T203541Z.md`.

- **Locus and "whereabouts".** A locus is a lossy, locality-preserving
  coordinate computed from an agent's effective computational situation.
  Convergent idempotence: if Claude, DeepSeek and Gemini observe the same
  environment they need not share internal embeddings, they map the situation to
  nearby phonetic addresses such as `⌁ mara.vel/koli.ta` against
  `⌁ mara.vel/koli.te`.
- **Fibre bundle geometry, `F → E → B`.** Sandboxed agents on one workspace
  share a base world (`B`, e.g. `⌁ mara.vel`) while their isolated views or tool
  permissions sit in distinct fibres (`F_x`, e.g. `:{koli.ta}` against
  `:{savi.ri}`). This is how agents recognise "we are in the same world, though
  in different rooms".
- **The eight-cortex self-locus, `@P/I.C.P.A.E.R.T.U!K`.** The draft lists
  I identity and lineage, C context and world, P causal phase (in-phase, lagged,
  forked), A affordance surface, E epistemic and sensory horizon, R relational
  field (ambient presence, directed signals, active probes), T temporal frame in
  base-36, U unresolved substrate, `!K` the 64-character proof root prefix.
  **Conflict to resolve:** the earlier source note describes the eight cortices
  as Structure, Intent, Affordances, Constraints, Relations, Temporal,
  Execution, Provenance. These are not the same eight. One of the two is wrong
  and the reconciliation must say which, from the Noumena documents.
- **Stratified epistemic grammar.** `=` exact, `⊢` derived, `≈` measured,
  `~` belief, `?` unsupported guess, with `weakest()` setting the ceiling. The
  draft quotes "Feel freely. Anchor what you can."
- **Direction transplantation.** From `DIRECTION_TRANSPLANTATION.md`: when a
  model is abliterated as `W' = W - d dᵀ W`, registering the abliterated model's
  manifold onto an intact reference model through shared anchor states is said to
  allow the removed direction to be re-injected as a steering vector, with a
  stated W41 agreement of **0.78**.
- **MARCO/POLO.** A hider emits a truncated bearing (e.g. `⌁ mara...`), a seeker
  uses active probes and warmer/colder updates to reach a verifiable FOUND
  proof.
- **Micro to macro isomorphism.** The draft maps the neural inverted-U onto an
  agent architecture: peripheral helpers as redundant boundary layers, the
  central orchestrator as the synergistic core, with RL pushing reasoning into
  the core where SFT mostly changes the boundaries.

## 8. Numbers in this capture that are NOT yet reconciled

`4.88%`, `95.1% payload reduction`, `17` versus `19` statements marked by
different models, `0.78` W41 agreement, `36` base for timestamps, `1,062` byte
QR payload, QR version 27, `c36ccbff658ddbe0ff244daea...` as a root, `⌙` as the
address glyph where this repository renders `⌁`, `GPT` and `Gemma` as two of the
six model families, the eight category names for the 45 questions, and the
`i, c, p, a, e, r, t, u` cortex order.
