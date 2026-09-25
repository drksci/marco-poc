# From whale vocalisation topology to a predictive neural map

## 1. The problem, stated honestly

A vocalisation and a neural response are not naturally expressed in the same vocabulary. A field biologist may describe a sperm-whale coda as `5R` or `1+1+3`, report its tempo and inter-click intervals, and place it within a behavioural context. A neurophysiologist may describe the response to that sound as spike rate, latency, a trajectory through population activity, or a change in fMRI BOLD. These are valid descriptions of different observables, not two names for one coordinate.

The MARCO analogy is therefore structural, not semantic. In MARCO, an agent declares landmarks such as `cap/reachable/git` or `perm/is/read-only`; a shared frame converts those declarations into distances, a coarse-to-fine address, and a separate exact identity. For whale work, the recording supplies measurable acoustic features rather than self-declared landmarks, and neural activity supplies a second observation space. The proposed bridge is a learned correspondence between the two spaces. Neither space is thereby made authoritative, and neither address is a meaning.

MARCO's useful lesson is separation of objects. Its 3,300-byte primer expands deterministically to 45 statements, a 32-entry pronounceable codebook, and an axis order derived from variance over 204 named places. A report marks each landmark with `=` (cryptographic/rank 5), `⊢` (deterministic/4), `≈` (measured/3), `~` (interpretation/2), or `?` (hypothesis/1); only `=` and `⊢` anchor claims, and a locus takes the weakest marker. Distances are quantised to 0.0, 0.3, 0.6, or 0.9; 45 four-way axes become 90 bits, Gray-decoded into a 32-entry adjacent-phoneme codebook. The resulting pronounceable coordinate is a location-like object. A SHA-256 commitment is deliberately separate: exact equality without adjacency.

That separation transfers cleanly. A whale phrase address would be descriptive and neighbourhood-preserving; a recording checksum would identify an exact file or observation set while destroying neighbourhood. A neural prediction would be a third object: an empirical estimate of response, not a decoded message. **Established:** this distinction is implemented and measured in MARCO. **Speculative:** that it will be useful for cetacean neurobiology.

MARCO's reported behaviour gives concrete expectations, not biological evidence: Spearman rho is 0.9286 between known ground-truth distance and rendered-coordinate Hamming distance over all 15 pairs of six test worlds, against a shuffled null of +0.0002 (sd 0.2704); the nearest pair of places sits at Hamming 9 and the furthest at 26. A question-selecting generator resolves any of 204 places in 17.8 questions, near the log2(204) ≈ 7.67 information floor. The landmarks, codebook and population together would cost 67,561 bytes to ship, 20.47 times the seed, and none of it is transmitted. These numbers validate a topology-preserving protocol, not a whale code or a neural theory.

## 2. Established, contested, and speculative

### Sperm whales

**ESTABLISHED.** Sperm-whale codas are stereotyped click sequences, roughly 3–40 clicks long, whose inter-click intervals define rhythm. Relative timing is commonly notated in forms such as `5R` and `1+1+3` (Rendell & Whitehead 2003, *Proceedings of the Royal Society B* 270:225–231, [doi:10.1098/rspb.2002.2239](https://doi.org/10.1098/rspb.2002.2239)). Codas overlap and are matched in interaction (Schulz et al. 2008, *Animal Behaviour* 76:1977–1988, [doi:10.1016/j.anbehav.2008.07.032](https://doi.org/10.1016/j.anbehav.2008.07.032)). Identity cues occur at unit, individual, and clan levels (Gero, Whitehead & Rendell 2016, *Royal Society Open Science* 3:150372, [doi:10.1098/rsos.150372](https://doi.org/10.1098/rsos.150372)). Antunes et al. (2011, *Animal Behaviour* 81:723–730, [doi:10.1016/j.anbehav.2010.12.019](https://doi.org/10.1016/j.anbehav.2010.12.019)) provide additional acoustic and social analysis.

**ESTABLISHED, WITH A LIMITED CLAIM.** Sharma et al. (2024, *Nature Communications* 15:3617, [doi:10.1038/s41467-024-47221-8](https://doi.org/10.1038/s41467-024-47221-8)) report contextual and combinatorial structure. Context-sensitive features called **rubato** and **ornamentation** are systematically controlled and imitated across whales; these combine with context-independent **rhythm** and **tempo**, producing nearly an order of magnitude more distinguishable codas. The paper does **not** claim semantics, syntax, or that codas are a language. The popular “codas are a language” framing is not supported by that primary source.

**CONTESTED.** It remains open what the additional distinguishability does socially: recognition, coordination, turn-taking, affective modulation, or something else. A structured acoustic repertoire is not evidence of compositional meaning. **SPECULATIVE:** a MARCO-like address could organise this repertoire without deciding among those functions.

### Humpbacks and dolphins

**ESTABLISHED.** Humpback song has a nested hierarchy of phrase → theme → song → song session (Payne & McVay 1971, *Science*, [doi:10.1126/science.173.3997.585](https://doi.org/10.1126/science.173.3997.585)). Songs are culturally transmitted and can undergo population-level revolutions (Noad et al. 2000, *Proceedings of the Royal Society B*, [doi:10.1098/rspb.2000.1271](https://doi.org/10.1098/rspb.2000.1271); Garland et al. 2011, *Proceedings of the Royal Society B*, [doi:10.1098/rspb.2011.0630](https://doi.org/10.1098/rspb.2011.0630)). **CONTESTED:** the behavioural hierarchy does not establish a linguistic grammar or referential semantics.

**ESTABLISHED.** Bottlenose-dolphin signature whistles are individually distinctive learned contours, used as vocal labels and copied or addressed (Janik et al. 2013, *PNAS*, [doi:10.1073/pnas.1304459110](https://doi.org/10.1073/pnas.1304459110)). They are the strongest referential-label analogue here, but they are not demonstrated to be words. **SPECULATIVE:** their contour space could be a useful test case for an acoustic address; that would still not be translation.

### Where neural decoding genuinely exists

**ESTABLISHED.** In bats, single-unit auditory-cortex recordings include neurons tuned to echo delay and velocity, yielding range-like maps. In zebra finches, single-unit auditory-forebrain responses encode conspecific song and tutor familiarity. In marmosets, single-unit A1 activity tracks self-generated vocal feedback (Eliades & Wang 2008, *Journal of Neuroscience*). In macaques, voice-selective temporal cortex has been studied with fMRI and single-unit recording (Petkov et al. 2008, *Neuron*).

**ESTABLISHED.** Cetacean neural data of this kind does not exist: there are no chronic implanted single-unit or ECoG recordings in wild cetaceans. Ethics, permits, animal size, immersion, and cetacean neuroanatomy make the bat/songbird/marmoset paradigm unavailable. Non-invasive auditory evoked potentials and behavioural psychoacoustics exist; for the proposed question, that is the ceiling. Any claim of a whale phrase-to-neuron map is therefore **SPECULATIVE** until a lawful, interpretable neural measurement exists.

## 3. The mapping, built from the ground up

### Step A — Define a phrase vector

For each isolated coda or humpback phrase, construct a vector with **18 dimensions** measured from a calibrated recording. The first dimension is unit count (click count for codas, or segmented syllable/event count for a phrase). Dimensions 2–6 are the first five inter-unit intervals, represented in milliseconds and also normalised by phrase duration; shorter phrases are padded with an explicit missing-value mask. Dimension 7 is median tempo (events per second). Dimensions 8–10 are rubato: mean signed deviation from a nominal timing grid, its standard deviation, and the maximum absolute deviation. Dimensions 11–14 are spectral-centroid trajectory at four equally spaced temporal landmarks. Dimensions 15–16 are bandwidth at the same two aggregate windows (early and late). Dimensions 17–18 are ornamentation flags or scores: presence and count/intensity of non-rhythmic spectral events. For longer songs, retain phrase boundaries and add session-level metadata separately rather than allowing duration to masquerade as phrase structure.

A concrete measurement pipeline is: detect click or syllable onsets; estimate inter-unit intervals; infer tempo from the robust median interval; fit the nominal grid; calculate rubato residuals; compute short-time Fourier transforms; summarise centroid and bandwidth at fixed temporal landmarks; and annotate ornamentation with a preregistered detector plus confidence. **ESTABLISHED:** these are measurable acoustic quantities. **SPECULATIVE:** that this 18-dimensional representation is the biologically relevant one. Every feature needs held-out reliability estimates, because microphone placement, propagation, overlap, and detector error can dominate small differences.

### Step B — Replace declared landmarks with spectral anchors

MARCO's 45 hand-declared landmarks become a fixed set of **K = 64 spectral anchors**. Each anchor is either a reference phrase or a reference template in the 18-dimensional, standardised feature space. Choose them before neural fitting by k-means++ over a training corpus, repeated 100 times with the lowest held-out distortion retained, or by hand-picked exemplars spanning unit count, tempo, timing shape, and ornamentation. Store the exact exemplars and preprocessing parameters.

For phrase vector x and anchor a_k, define d_k as a weighted distance: robust-scaled Euclidean distance for continuous features, dynamic-time-warping distance for trajectories, and Hamming distance for flags, with weights learned only inside training folds. Quantise d_k into four bins analogous to MARCO's 0.0, 0.3, 0.6, and 0.9, but calibrate thresholds on training data. Poor anchors are a known failure mode: redundant anchors collapse dimensions; outliers make every phrase appear far away; population- or context-specific anchors encode recording conditions rather than vocal structure. **CONTESTED:** no single metric is justified a priori.

### Step C — Build a coarse-to-fine phrase address

Partition the 64-distance vector hierarchically into four branches per axis, yielding 128 bits before any codebook rendering. Order axes by discriminative power measured only on training folds. This order matters more here than in a descriptive demo: the first axis should probably be unit count or tempo, not spectral centroid, but that is a hypothesis to test. Gray-decode the quantised path into a pronounceable address using the same 32-entry adjacent-phoneme codebook and one-phoneme-per-bit adjacency principle. The address should be treated as a stable neighbourhood label, not a name for a behavioural category.

### Step D — State the predictive hypothesis formally

Let q(x) be the phrase address, represented as a real-valued bit or branch vector after calibration, and let y be a neural response vector (for example, binned firing rates, latency features, or a low-dimensional population trajectory). The primary hypothesis is:

\[
\exists W,b:\quad \hat y = Wq(x)+b,
\]

such that prediction on held-out phrases exceeds a preregistered null and generalises across recording sessions, individuals, and contexts. Candidate nonlinear extensions may be tested only after this linear baseline. This is a **SPECULATIVE hypothesis with no cetacean neural data behind it**. A successful W would mean that the address preserves information useful for predicting measured response; it would not mean that the address is a neural code or that the animal computes MARCO.

### Step E — Brute-force search

A deliberately broad search might vary 64-anchor sets (10^3 candidate sets after clustering and exemplar sampling), six feature metrics, five quantisation schemes, four axis-ordering rules, and three response alignments: approximately 10^3 × 6 × 5 × 4 × 3 = **360,000 topological candidates**. For each, fit W by ridge regression over 20 logarithmically spaced penalties; additionally fit CCA, and, where dimensions are matched, orthogonal Procrustes. That is 7.2 million fitted candidates before permutations. The objective is held-out neural prediction: cross-validated correlation, mean-squared error, and representational dissimilarity alignment, combined only after a predeclared primary metric.

This is not a licence to select the prettiest coordinate. Use nested cross-validation: inner folds select anchors, metrics, quantisation, axis order, and penalty; outer folds estimate performance on phrases and sessions never used for selection. Search multiplicity is part of the null distribution, not an afterthought. A candidate that wins 7.2 million trials by chance has not discovered a map.

```text
recording ──> segmentation ──> 18-D phrase vector ──> 64 anchors ──> distances
   │                 │                                      │
   └─ quality/null ──┴─ held-out preprocessing ─────────────┘
                                      │
                         quantise + ordered partition
                                      │
                           Gray/codebook phrase address
                                      │
 neural window ──> response vector ──> ridge / CCA / Procrustes ──> prediction
      │                    │                  │                    │
      └─ temporal shuffle ──┴─ label permutation ─┴─ nested CV ──────┘
                                      │
                         known-answer + decoy + multiple-comparison correction
```

## 4. Controls, and why this is the hard part

The canonical tools are well established. Canonical correlation analysis (CCA) originates with Hotelling (1936). Orthogonal Procrustes provides a constrained alignment (Schönemann 1966, *Psychometrika*, [doi:10.1007/BF02289451](https://doi.org/10.1007/BF02289451)). Representational similarity analysis (RSA) compares dissimilarity structures rather than pretending that coordinates are directly commensurate (Kriegeskorte et al. 2008, *Frontiers in Human Neuroscience*, [doi:10.3389/neuro.01.1.1.004.2008](https://doi.org/10.3389/neuro.01.1.1.004.2008)). Encoding models predict neural measurements from stimulus features (Naselaris et al. 2011, *NeuroImage*, [doi:10.1016/j.neuroimage.2010.07.073](https://doi.org/10.1016/j.neuroimage.2010.07.073)); semantic encoding maps illustrate the ambition and the assumptions (Huth et al. 2016, *Nature*, [doi:10.1038/nature17637](https://doi.org/10.1038/nature17637)).

The central warning is sample-size collapse. CCA can produce near-perfect in-sample correlation when predictor and response dimensions approach the number of samples. A few hundred phrases against a population response containing thousands of neurons is exactly the regime in which a spurious mapping is easy to find: flexible projections can align noise, especially after searching anchors, metrics, alignments, and penalties. Dimensionality reduction does not automatically cure this; if the reduction is selected using all trials, the leakage merely moves upstream.

Circular analysis or double-dipping is the same error in another form: selecting features or coordinates because they fit the neural data and then evaluating them on those same data (Kriegeskorte et al. 2009, *Nature Neuroscience*, [doi:10.1038/nn.2303](https://doi.org/10.1038/nn.2303)). The phrase address must be frozen before the test fold, and neural preprocessing must not use held-out labels.

Required controls are concrete:

1. **Permutation null over phrase labels.** Randomly reassign phrase identities to neural windows, rerun the complete search, and retain the maximum score per permutation. The null must include the same 360,000-candidate topology search.
2. **Temporal-alignment shuffle.** Shift or permute the phrase relative to the neural window while preserving autocorrelation and trial counts. A mapping that survives arbitrary misalignment is probably exploiting session structure.
3. **Cross-validated held-out phrases.** Report only outer-fold predictions, with held-out individuals or sessions where possible; never report in-sample CCA correlation as evidence.
4. **Known-answer case.** Generate synthetic phrase vectors, choose a hand-built W with known noise, and confirm recovery, calibration, and expected degradation as noise rises.
5. **Decoy.** Pair the phrase set with an unrelated neural dataset and require the pipeline to report no mapping above the corrected null.
6. **Held-out anchors.** Fit anchors on one corpus partition and evaluate addresses using anchors never selected from the test phrases.
7. **Multiplicity correction.** Correct across all candidate topology and model searches, preferably by maximum-statistic permutation or a preregistered family-wise procedure.

The governing rule is severe: **in a space like this, the metric is more likely to be wrong than the model. Any reported mapping must survive a null with identical information content.** A high rho, a clean visual trajectory, or an intelligible phonetic address is not a control.

## 5. What would make this real rather than decorative

**Milestone 0 — synthetic recovery, no whales.** Create phrase spaces with known anchors, known axis order, known quantisation, and known W. Falsifier: the pipeline cannot recover W or its out-of-sample performance collapses under realistic noise. Vary sample size until the CCA failure becomes visible; publish the curve.

**Milestone 1 — bird neural data.** Use zebra-finch song features and auditory-forebrain responses, with tutor familiarity as a known behavioural/neural contrast. Falsifier: the method fails to distinguish known song classes or cannot beat a simple spectrotemporal baseline under held-out birds/sessions. This tests the full measurement-to-neural pipeline where recordings exist.

**Milestone 2 — bat neural data.** Use echolocation parameters and auditory-cortex single-unit responses, including delay and velocity tuning. Falsifier: a MARCO-like topology performs no better than shuffled addresses or cannot recover a range-like response manifold. This tests whether anchors and coarse-to-fine order preserve a known physical variable.

**Milestone 3 — marmoset vocal feedback.** Apply the method to self-generated vocalisations and A1 activity, using the Eliades & Wang 2008 setting. Falsifier: no held-out prediction beyond acoustic energy, onset, and motor-corollary baselines. This tests active feedback rather than passive stimulus response.

**Milestone 4 — cetacean behaviour without neurons.** Build stable coda and song addresses from independently recorded populations; test identity, context, overlap, matching, cultural change, and cross-site robustness. Falsifier: addresses fail to replicate under microphone, recorder, location, or individual hold-out. This is useful topology engineering, but not a neural map.

**Milestone 5 — non-invasive cetacean physiology, if ethically and technically justified.** Pair controlled acoustic presentation with auditory evoked potentials or other permitted non-invasive measures. Falsifier: no reproducible phrase-conditioned response after correcting for loudness, timing, movement, and subject identity. Even success would establish prediction of a measured evoked signal, not cortical semantics.

At every milestone, compare the MARCO address with raw acoustic features, a standard spectrogram embedding, a simple timing model, and a randomly generated topology with equal information content. The address earns its complexity only if it generalises better or is demonstrably more robust.

## 6. Limits

Nothing in this proposal can establish that a coda or song phrase has meaning. A predictive acoustic-to-neural map would not identify a referent, intention, or semantic composition. It would be an encoding model: signal in, measured response out. A good predictor is not a dictionary.

A locus, phrase address, or neural coordinate is descriptive and never authoritative. MARCO's epistemic ladder makes this explicit: interpretation and hypothesis cannot anchor a claim. In a whale application, even a highly repeatable acoustic feature should not be promoted to a behavioural landmark without independent evidence, and an inferred neural association should remain a hypothesis until it survives held-out subjects, temporal shuffles, decoys, and search-corrected nulls.

The strongest defensible outcome is therefore modest: a reproducible, topology-preserving description of vocal signals, plus a rigorously tested prediction of a particular neural measurement where such data exist. For cetaceans today, the first object is feasible; the second is not established. The distance between them is precisely the scientific problem, not a gap that a pronounceable coordinate can rhetorically close.
