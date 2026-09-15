# Paper walkthrough notes

Paper: *Frequency-Adaptive Audio Limiting for Reduced Acoustic Exposure and Loudness Preservation*

Authors: Yashwini Krishna Murthy and Bhavya Shri (VIT Chennai)

This file is a running record of what has been explained so far. New sections are appended only after the previous section is cleared.

---

## 0. Title, abstract, and keywords

### What this paper is, in one line

This is an **experiment**, not a new invention. Known audio tools were pointed at a hearing-dose problem and measured against “turn the volume down.” They lost.

Two different meters score how “big” a sound is:

- **Dose / exposure** (what ITU-T H.870 cares about): A-weighted energy. A-weighting follows an old 40-phon equal-loudness idea and **throws away most bass**. At 40 Hz it is about **−35 dB**.
- **Programme loudness** (broadcast / streaming): ITU-R BS.1770 **LUFS**, which uses **K-weighting**. K-weighting still **counts bass** much more than A-weighting does.

The hypothesis: if those two meters disagree by frequency, maybe some bands can be cut more than others so dose falls while loudness stays. The processor that was built mostly **cut bass** and added fake harmonics. Result: cutting bass dropped LUFS a lot and barely moved the A-weighted number, so the simple flat-gain baseline won on dose.

---

### Title

**Text:** Frequency-Adaptive Audio Limiting for Reduced Acoustic Exposure and Loudness Preservation

**What each phrase means**

- *Frequency-adaptive / frequency-selective limiting:* different frequencies get different gain, not one scalar for the whole signal.
- *Acoustic exposure:* hearing dose, operationally an A-weighted energy number (in this paper: a **digital proxy**, not real ear SPL).
- *Loudness preservation:* keep the programme sounding about as loud, operationally **LUFS**.

**What the title sounds like vs what was done**

- Sounds like: a limiter that lowers hearing dose while keeping things loud.
- What was actually done: a test of whether a 3-band heuristic can do that. **It failed.**

The title is slightly promotional. The abstract is the honest part. You cannot claim, from this title, that you invented frequency-adaptive limiting or that you preserved loudness at lower exposure. Those are hopes. The data rejected them.

---

### Abstract, sentence by sentence

**1. “Conventional personal-audio limiters reduce listening level by applying one gain to every frequency.”**

- Science: \(y[n] = G\, x[n]\) with \(G < 1\). One number scales bass, mids, and treble together.
- Who already did this: classic compressors/limiters (Giannoulis, Massberg, Reiss, 2012); phone/headphone volume caps; H.870 “reduce volume when allowance is used up”; Liang et al. 2023 (DRC for safe listening).
- **Cannot claim:** inventing a limiter, or inventing broadband limiting.

**2. “A-weighted exposure and programme loudness do not weight the spectrum in the same way, so it is reasonable to ask whether cutting some bands more than others can lower an exposure metric at the same loudness.”**

- Science: A-weighting (IEC 61672) ≈ 40-phon Fletcher–Munson / ISO 226 shape; used for occupational/recreational **dose**. LUFS (BS.1770) uses K-weighting for **how loud a mix sounds**. They are not the same filter.
- Who already knew the meters differ: this is standard audio-engineering knowledge (A vs C vs K weighting debates; concert LAeq vs LCeq; broadcast loudness vs SPL).
- **Cannot claim:** discovering that A-weighting and LUFS weight frequency differently.
- **Can ask (this is the paper’s question):** does exploiting that difference beat flat gain? Asking is allowed. A positive answer is what you do **not** have.

**3. “This paper tests that question with a three-band digital processor: a complementary Linkwitz–Riley split at 300 Hz and 4 kHz, a low-band shelf of −12 dB with harmonic fill from 80 to 400 Hz, an A-weighted mid-band compressor, and a mild high-band envelope gain.”**

This sentence lists **the apparatus**, not a new invention. Piece by piece:

| Block | What it is | Already exists |
|---|---|---|
| Linkwitz–Riley 4th-order split at 300 Hz / 4 kHz | Complementary crossover so bands sum flat | Linkwitz 1976; every loudspeaker crossover / multiband compressor |
| Low shelf −12 dB | Cut bass around ~100 Hz | Standard EQ (RBJ/biquad shelf) |
| Harmonic fill 80–400 Hz | Square + cube the sub-bass, keep 2nd/3rd harmonics | Virtual bass / MaxxBass / Gan 2001 — usually to **fake** bass on small speakers, not to save dose |
| A-weighted mid compressor | Compress 300 Hz–4 kHz using an A-weighted envelope | Compressors (Giannoulis); A-weighted detectors in meters; hearing-aid multiband DRC (Kates) |
| High-band envelope gain | Turn down >4 kHz when it is hot | Ordinary envelope limiter / transient control |

**Cannot claim:** any of these blocks, or “a new architecture,” just because they are wired together.

**4. “On 20 clips (16 Freesound recordings and four synthetic signals) we compare the processor with frequency-flat gain under two matching rules.”**

- Experiment design: same audio, two processors, then **force one meter to be equal** and look at the other.
- Matching rules (defined later): matched LUFS, or matched digital \(L_{Aeq}\).
- n = 20 is small; 4 clips are synthetic. Honest, but not a large perceptual study.
- **Cannot claim:** a listening test, a clinical study, or a device evaluation. This is offline DSP on files.

**5. “At matched BS.1770 loudness (LUFS), the proposed system's digital A-weighted \(L_{Aeq}\) proxy is on average 1.17 dB higher than flat gain.”**

This is the **main number**. Positive = proposed is **worse** on dose at the same loudness.

- 1.17 dB is a real, modest gap. On energy, 1 dB is noticeable in a meter; it is not a dramatic “twice as safe” story.
- “Digital \(L_{Aeq}\) proxy” is doing a lot of work: **not** pascals, **not** eardrum SPL, **not** H.870-compliant dose.

**Cannot claim:** lower exposure, safer listening, or beating the baseline.

**6. “The matched-loudness exposure hypothesis is therefore not supported.”**

Plain language: **the idea failed.** This sentence is the most important in the abstract. Keep it. Do not rewrite the paper as a success.

**7. “The gap is largest on bass-heavy material (about +1.6 to +2.7 dB on real bass loops). Vocals, speech, and short transients are essentially tied.”**

- Science: the processor’s big move is cutting sub-bass. Bass loops have a lot of that. Speech/vocals live in the mid band, so the bass shelf barely matters and the two systems look similar.
- **Cannot claim:** the method “works for speech” in a useful dose-saving sense. Tie ≠ win.

**8. “The reason is straightforward: A-weighting already discards most energy near 40 Hz, so removing sub-bass lowers LUFS much more than \(L_{Aeq}\), and flat gain must then cut the midrange to match loudness.”**

This is the **mechanism**, and it is the only intellectually new *explanation* in the front matter.

- Cut 40 Hz → LUFS falls (K-weighting still sees it) → \(L_{Aeq}\) barely moves (A-weighting already ignored it).
- To match LUFS, flat \(G\) turns **everything** down, including 1–4 kHz, which A-weighting **does** count.
- So flat gain’s \(L_{Aeq}\) ends up **lower**.

Intuition that failed: “bass is loud but not in the dose meter, so cut bass.” That would help **loudness at fixed dose** only if you **kept** bass and cut mids. The processor did the opposite.

**Cannot claim:** a new psychoacoustic model. This is applying known A-weighting and K-weighting curves to a specific gain allocation.

**9. “At matched \(L_{Aeq}\) the proposed output is correspondingly quieter.”**

Same fact, flipped. If proposed has higher dose at equal loudness, then at equal dose it must be quieter (for a frequency-flat baseline, the two views differ only by sign). Dual of sentence 5. Not a second experiment.

**10. “All levels in this study are digital-domain proxies, not calibrated ear-level SPL.”**

Required honesty.

- Real H.870 dose needs headphone sensitivity, volume, DRP / diffuse-field correction, often a HATS (IEC 60318-4).
- +94 dB in the code is an arbitrary offset so numbers look like SPL. It is **not** calibration.

**Cannot claim:** hearing protection, WHO/ITU compliance, or “dB SPL.”

---

### Keywords

Audio signal processing · A-weighting · dynamic range compression · frequency-selective limiting · loudness · multiband processing · virtual bass

These name the **libraries you used**, not contributions. Every keyword is a mature literature. Putting them here tells a reviewer which boxes you sit in; it does not make those boxes yours.

---

### Claim checklist for this section

| Tempting claim | Allowed? | Why |
|---|---|---|
| We invented frequency-adaptive limiting | No | Multiband limiters, hearing-aid DRC, patents (e.g. US 9980028) exist |
| We reduced acoustic exposure | No | Mean \(L_{Aeq}\) went **up** at matched LUFS |
| We preserved loudness at lower dose | No | Dual result: quieter at matched dose |
| We tested a reasonable hypothesis on 20 clips | Yes | That is what the abstract actually says |
| Digital numbers ≠ ear SPL | Yes (must keep saying this) | Uncalibrated proxy |

---

### Q: What does A-weighting actually mean?

A frequency filter applied **before** measuring level, so bass and extreme treble count less than mids. IEC 61672 curve, shaped like hearing at a quiet ~40 phon level.

- 40 Hz ≈ −35 dB (almost ignored)
- 100 Hz ≈ −19 dB
- 1 kHz = 0 dB (reference)
- 2–4 kHz = slight boost
- very high treble rolls off

dBA / \(L_{Aeq}\) = energy **after** that filter. H.870 uses it as dose because that number historically correlated with occupational hearing-loss data. It is **not** LUFS and **not** “how loud a club feels.” That is why cutting 40 Hz barely moves this paper’s exposure proxy.

### Q: What does LUFS mean?

**Loudness Units relative to Full Scale** (same as LKFS). ITU-R BS.1770 programme-loudness meter used by broadcast/streaming.

1. Filter with **K-weighting** (gentle high-pass + HF shelf — not A-weighting).
2. Mean-square energy, gated so silence does not dominate.
3. More negative = quieter. Streaming often targets about −14 LUFS.

K-weighting still counts bass much more than A-weighting. Cutting 40 Hz drops LUFS but barely moves \(L_{Aeq}\).

- LUFS = how loud the programme sounds.
- A-weighted \(L_{Aeq}\) = filtered energy for dose.

The experiment matches one and compares the other.

---

### Status (end of front matter)

- Explained: Title, abstract, keywords.
- Questions cleared: A-weighting, LUFS.
- Next: Introduction.

---

## 1. Introduction

### Role of this section

The Introduction does four jobs:

1. Name the **real-world problem** (headphones too loud for too long).
2. Say what **standards already do** (track A-weighted dose, then turn the volume down).
3. Say why a smarter processor *might* help (hearing is frequency-dependent; multiband and virtual bass already exist).
4. State the **question**, the **experiment**, and the **answer** (negative).

It does **not** invent the problem. WHO/ITU already defined it.

---

### Paragraph 1 — the problem and H.870

**“Personal listening devices can deliver high playback levels for long periods.”**

True and documented. Earbuds/phones can exceed occupational-style levels. This is the public-health setup, not a result of this paper.

**Who already found this**

- **Levey, Levey, Fligor (2011):** MP3-player users in cities; estimated exposures often high.
- **Portnuff, Fligor, Arehart (2011):** teenage portable-listening-device use; risk depends on earphone type and volume.
- **WHO World Report on Hearing (2021):** large population at risk from unsafe listening.
- **ITU-T H.870** (with WHO): “safe listening devices” standard.

**“The World Health Organization and ITU-T Recommendation H.870 treat this as a cumulative A-weighted sound-dose problem and give device makers a framework for tracking exposure.”**

H.870’s idea:

- Hearing risk is treated as **dose** = A-weighted sound energy accumulated over a week (Pa²h), not “was this one second too loud.”
- Equal-energy principle: 3 dB louder ≈ half the allowed time.
- Devices should **measure** sound allowance and optionally **limit volume** when 100% is used.

**Cannot claim:** discovering headphone hearing risk, or writing H.870.

**“H.870 specifies how much dose to allow. It does not specify a signal-processing algorithm that should be used when the limit is reached.”**

This is the **gap the paper wants**. H.870 says: when allowance is gone, reduce output to ~80 dBA (adult) or ~75 dBA (child) at the ear, diffuse-field corrected. It does **not** say “use a 3-band limiter” vs “use one gain G.” Default in the standard is **turn the volume down**.

**Caution:** Liang et al. (2023) and patents (e.g. US 9980028) **do** specify algorithms (DRC, TWA limiter, even multiband). So “the standard is silent” is true; “nobody has an algorithm” is **not** true. Related Work later overclaims this a bit.

---

### Paragraph 2 — the usual fix, and why it feels crude

**“The usual engineering response is a broadband limiter or automatic gain control (Giannoulis 2012): when an exposure estimate exceeds a threshold, apply one scalar G < 1 to the whole signal.”**

- Giannoulis, Massberg, Reiss 2012 = the standard **digital compressor tutorial** (AES). Peak/RMS detector → gain computer → apply one gain.
- Same structure as “volume limiter”: one G for all frequencies.

**Cannot claim:** compressors or AGCs.

**“That is easy to implement and it does reduce an A-weighted metric. It is also crude.”**

True: if you scale the whole waveform by G, every weighted RMS (A or K) drops by about \(20\log_{10} G\). Dose goes down. Loudness goes down by the same amount. No clever trade-off.

**“Equal-loudness contours (Fletcher–Munson 1933; ISO 226) show that hearing sensitivity is strongly frequency-dependent, so a flat cut changes bass, midrange, and treble by different perceptual amounts.”**

Science:

- Fletcher & Munson (1933): classic equal-loudness curves. At low SPL, bass must be physically stronger to sound as loud as 1 kHz. At high SPL the curves flatten.
- ISO 226: modern standard version of those contours.

So a flat −6 dB does **not** feel like −6 dB at every frequency. That motivates “maybe cut some bands more.” **Motivation only.** This paper does **not** implement ISO 226 or a loudness model (Zwicker / Moore–Glasberg). It uses LUFS instead.

**Cannot claim:** equal-loudness contours, or a perceptual loudness model.

**“Multiband compression and virtual-bass methods already exist as separate tools. What is missing is a direct test: if those tools are combined into an exposure-oriented limiter, do they beat ‘turn everything down’ when exposure or loudness is matched?”**

This sentence **admits the tools are old** and tries to own only the **test**.

- Multiband DRC: hearing aids (Kates), broadcast, plugins — **exists**.
- Virtual bass: MaxxBass, Gan 2001 — **exists**.
- Combining them for dose vs loudness at **matched** meters: this is the claimed gap.

**Cannot claim:** inventing multiband compression or virtual bass.
**Trying to claim:** the matched comparison. That is the only contribution named in the Introduction.

---

### The research question (the quote)

**“Can frequency-selective gain allocation reduce an A-weighted digital exposure proxy more than conventional broadband attenuation at matched loudness, and preserve quality better at matched exposure?”**

Two hypotheses hidden in one sentence:

- **H2:** same LUFS → is proposed \(L_{Aeq}\) **lower**?
- **H1:** same \(L_{Aeq}\) → is proposed **louder** and/or closer in spectrum (LSD)?

Words that keep you honest:

- *digital exposure proxy* — not ear SPL.
- *matched loudness / matched exposure* — you only compare after forcing one meter equal.

**Cannot claim:** quality, until a listening test exists. The question *asks* about quality; the paper later uses LSD, not MUSHRA.

---

### Paragraph 3 — what you ran, and the contribution sentence

**“We implement three systems on the same audio: the original clip, frequency-flat gain, and a three-band processor.”**

1. Original = reference.
2. Flat gain = H.870-style “turn it down.”
3. Proposed = the 3-band heuristic.

**“We then match either LUFS or the digital \(L_{Aeq}\) proxy and compare the other quantity.”**

That **is** the experiment. Not “we invented a limiter.”

**“The ingredients are not new. The comparison is the contribution.”**

Most important sentence in the Introduction. Keep it forever. If you later claim a new algorithm, you contradict yourself.

---

### Paragraph 4 — the answer, already in the intro

IEEE style: tell the result in the Introduction, do not hide it.

**Negative on the main hypothesis.** +1.17 dB mean (proposed **worse** at matched LUFS). Bass drives it. Speech/vocals ~tie. Reason previewed: budget spent on a band A-weighting barely counts.

Same facts as the abstract. Introduction repeats them so a reviewer does not have to hunt.

---

### Last paragraph — roadmap

Related work → method (heuristic, not optimiser) → implementation → setup → results → limits → conclusion.

“Design heuristic, not a numerical solver” means: you **picked** −12 dB, 300 Hz, 4 kHz by hand. You did **not** solve “minimise \(L_{Aeq}\) subject to LUFS = constant.” **Cannot claim** an optimal or adaptive allocator.

---

### Claim checklist for the Introduction

| Tempting claim | Allowed? |
|---|---|
| Headphones can be too loud; H.870 tracks A-weighted dose | Yes, citing WHO/ITU/Levey/Portnuff |
| H.870 does not pick a DSP algorithm | Yes for the standard; not “no algorithms exist” |
| Equal-loudness contours exist, so flat gain is perceptually uneven | Yes, as motivation only |
| We invented multiband DRC or virtual bass | No |
| We invented an optimal frequency allocator | No (heuristic) |
| The contribution is the matched test | Yes, as a claim of *what you did* |
| Frequency-selective beat flat gain | No — intro already says it lost |

---

### Status (end of Introduction)

- Explained: Title, abstract, keywords; Introduction.
- Questions cleared on front matter: A-weighting, LUFS.
- Next: Related Work.

---

## 2. Related Work

### Role of this section

Tell the reviewer: these four literatures already exist; we only claim a **matched comparison** at the intersection. The gap table is the argument. It is slightly too clean — some missing citations weaken “nobody did frequency allocation for dose.”

---

### 2.1 Exposure control

**Paper says:** H.870 is an A-weighted sound-allowance model. Mapping a digital file to ear pressure depends on headphone sensitivity and volume. Devices respond with volume caps, dose meters, or broadband AGC. They manage **level**, not **which frequencies** keep loudness.

**Science / who**

- **H.870:** weekly dose in Pa²h, A-weighted, ideally diffuse-field corrected at the eardrum reference point. Appendix even discusses estimating dose from the digital signal **if** you know the headphone. Hard problem: same WAV at 50% volume on two earbuds is two different SPLs.
- **Levey 2011, Sulaiman 2013:** epidemiology / survey of PLD use and risk — not DSP papers.
- Device practice: iOS/Android sound allowance, EN 50332 max voltage, parental volume caps.

**Cannot claim:** dosimetry, H.870, volume caps.

**Overclaim to watch:** “These systems do not allocate level across frequency to keep loudness.” True of **H.870 as written** (it wants a volume drop). **Not** true of all prior art:

- **Liang et al., IJERPH 2023:** H.870 dose + speaker frequency response + **DRC** (still mostly broadband level).
- **US 9980028:** headset TWA limiter; can use **multiband companding** to keep loudness while cutting RMS.
- **US 6826515:** headset dosimeter; **explicitly flat gain** so the chosen EQ stays — this is your baseline in patent form.

Cite these later. Right now they are missing.

---

### 2.2 Dynamic range control

**Paper says:** Compressors/limiters are well understood (Giannoulis 2012; Kates 2008). Multiband = one envelope per band, usually for mix balance, broadcast loudness, or hearing-aid audibility — **not** an exposure-vs-loudness test vs flat gain. LUFS (BS.1770) is the loudness stand-in.

**Science / who**

- **Giannoulis et al. 2012:** how a digital compressor is built (detector, gain computer, attack/release). Your mid-band compressor is this recipe with an A-weighted detector.
- **Kates 2008:** hearing-aid DRC — **frequency-specific** gain so soft speech is audible, loud sounds not painful. Same *shape* as multiband limiting, different *goal* (audibility, not H.870 dose vs LUFS).
- **BS.1770:** K-weighting + gating → LUFS. You use it as “loudness.” It is **not** ISO 532 (sones) and **not** a booth loudness match.

**Cannot claim:** compressors, multiband DRC, LUFS, hearing-aid compression.

---

### 2.3 Loudness perception

**Paper says:** ISO 226 and excitation-pattern models (Zwicker; Moore–Glasberg) explain why a flat dB cut is not perceptually flat. Used as **motivation only**. No Zwicker/Moore model in the loop. Operational loudness = integrated LUFS.

**Science / who**

- **ISO 226 / Fletcher–Munson:** equal-loudness contours.
- **Zwicker 1961, Zwicker & Fastl:** critical bands, loudness from excitation pattern (ISO 532-1 related).
- **Moore, Glasberg, Baer 1997; Glasberg & Moore 2002:** more accurate loudness model for steady and time-varying sounds.

A real “preserve loudness, cut dose” optimiser would use one of those (or ISO 532) as the loudness constraint. You did **not**. LUFS is cheaper and standard for *programme* loudness, but it is a **K-weighted energy meter**, not a full loudness model.

**Cannot claim:** a new loudness theory, or that LUFS *is* perceived loudness.

---

### 2.4 Virtual bass

**Paper says:** If the fundamental \(f_0\) is missing, you can still hear pitch at \(f_0\) from the harmonics (residue pitch). Speaker virtual-bass systems synthesise those harmonics when the driver cannot play sub-bass. You use the **same trick backwards**: cut real sub-bass, inject 80–400 Hz harmonics. Residue pitch ≠ preserved bass **loudness**.

**Science / who**

- **Schouten 1940:** residue — pitch of a harmonic complex can sit at the missing fundamental.
- **Terhardt 1974, 1979:** virtual pitch / calculating virtual pitch.
- **Ben-Tzur / MaxxBass 1999; Gan et al. 2001, 2004:** consumer virtual bass (NLD or similar) so laptops/phones *sound* like they have bass.

Your NLD \(a_2 x^2 + a_3 x^3\) is the textbook cheap virtual-bass generator (even- and odd-order harmonics).

**Cannot claim:** residue pitch, virtual bass, or “we preserved bass loudness.” The paper correctly refuses the last one.

**Direction flip is a usage, not an invention:** speakers: add harmonics because physics cannot play 40 Hz. You: remove 40 Hz hoping dose drops and harmonics keep the pitch cue. The DSP is the same family.

---

### 2.5 Gap table

Columns: Exposure, Freq. adaptive, Loudness aim, Bass fill, Matched test.

| Row | Meaning | Fair? |
|---|---|---|
| H.870 dose limit | Tracks dose, no DSP shape, no loudness, no bass fill, no match | Fair |
| Broadband limiter | Reduces level, not frequency-selective; loudness falls as a side effect; this is the **baseline** | Fair |
| Multiband DRC / HA | Frequency-selective; loudness/audibility sometimes; bass fill rare; matched dose-vs-LUFS test rare | Mostly fair; “Rare” is doing a lot of work |
| Virtual bass | Not a dose tool; bass-only loudness; no matched dose test | Fair |
| This work | Digital **proxy**, yes freq, yes LUFS aim, yes bass fill, yes matched test | Fair as a description of *what you ran* |

**Claimed gap:** pieces exist separately; little evidence the combo beats flat gain at equal dose **or** equal loudness.

**What you may own:** that specific **matched** comparison on music with LUFS vs digital \(L_{Aeq}\).

**What you may not own:** “first frequency-selective dose limiter” (patents), “first to combine multiband + virtual bass” (engineering practice), “first H.870 processor.”

**Missing rows you should add later:** Liang 2023, US 9980028, Fathima 2026 (multi-band hearing protection). They do not kill the matched-LUFS-vs-\(L_{Aeq}\) experiment, but they kill a sloppy “nobody allocates by frequency for exposure” sentence.

---

### Claim checklist for Related Work

| Tempting claim | Allowed? |
|---|---|
| We reviewed four existing toolboxes | Yes |
| H.870 does not define a 3-band limiter | Yes |
| No published algorithm touches frequency and dose | No — patents / Liang / HPDs |
| Ingredients are known; the match is the gap | Yes, if you cite the closer neighbours |
| Residue pitch = bass loudness preserved | No — paper already denies this |

---

### Status (end of Related Work)

- Explained: Title, abstract, keywords; Introduction; Related Work.
- Next: Proposed Method.

---

## 3. Proposed Method

### Role of this section

Describe the **apparatus** (the 3-band heuristic). It is **not** an invention section. Every block is a known DSP recipe. The design *intent* is: cut energy that A-weighting counts more than LUFS. The actual low-band choice does the **opposite**. The paper already names that as the failure mode.

---

### 3.1 Design objective

**Baseline (exists everywhere):**
\[
y[n] = G\, x[n], \quad G < 1
\]
One scalar. A-weighted RMS and LUFS both drop by about \(20\log_{10} G\). No frequency trade-off.

**Intended trade-off:** a frequency-dependent gain so that **at the same loudness**, A-weighted digital \(L_{Aeq}\) is **lower** than with flat \(G\). That means: cut frequencies where \(w_A(f)\) is large relative to K-weighting / loudness.

**Named failure mode (this is what actually happened):** cut frequencies that A-weighting **already ignores** (sub-bass). Then you lose LUFS and barely save dose.

**“Heuristic, not a solver.”** You did not run: minimise \(L_{Aeq}\) subject to LUFS = constant. You picked fixed bands and gains by hand. **Cannot claim** optimal, adaptive-in-the-optimisation-sense, or “frequency allocation algorithm” as a solved problem.

---

### 3.2 Architecture

Split at **300 Hz** and **4 kHz**, process three bands, sum, peak ceiling −1 dBFS:
\[
y = y_L + y_M + y_H
\]

Why those cutoffs (prototype, not listening-test optimised):

- **Low (<300 Hz):** sub-bass / kick / bass guitar fundamentals.
- **Mid (300 Hz–4 kHz):** speech, vocals, most musical energy; also where A-weighting is near 0 dB or slightly up.
- **High (>4 kHz):** cymbals, sibilance, transients.

**Cannot claim:** the idea of a 3-way split, or that 300 Hz / 4 kHz are scientifically special. They are round numbers.

Block diagram: LR4 crossover → (low shelf + NLD harmonics) / (A-weighted compressor) / (envelope gain) → sum → peak limiter.

Peak ceiling at −1 dBFS is ordinary “don’t clip the DAC” limiting (true-peak/ceiling limiters in every DAW). **Cannot claim.**

---

### 3.3 Low band (this is the block that decides the paper)

**Shelf:** −12 dB around 100 Hz. Linear gain \(\beta = 10^{-12/20} \approx 0.25\). Standard RBJ/biquad low shelf. Bass is turned down to ~1/4 amplitude.

**Harmonic fill (virtual bass):** isolate sub-bass \(x_{\mathrm{sub}}\), then a **memoryless nonlinearity**
\[
x_{\mathrm{NLD}}[n] = a_2\, x_{\mathrm{sub}}^2[n] + a_3\, x_{\mathrm{sub}}^3[n]
\]
with \(a_2=0.8\), \(a_3=0.35\). Square → even harmonics (2, 4, …). Cube → odd harmonics (3, 5, …). Then band-pass **80–400 Hz** and mix back.

**Why 80–400 Hz:** an earlier 160–300 Hz window missed \(2f_0\) and \(3f_0\) for a 40 Hz fundamental (80 Hz and 120 Hz). Wider window so a 40 Hz tone actually produces those harmonics. That is an implementation fix, not a new theory.

**Science:** Schouten/Terhardt residue pitch; Gan/MaxxBass NLD virtual bass. Same mechanism, opposite product goal (they *add* bass impression for small speakers; you *remove* physical bass and hope harmonics keep a pitch cue).

**Paper’s own warning:** residue pitch ≠ preserved bass **loudness**. Harmonics can make you still *identify* “there is a bass note.” They do not put the missing 40 Hz energy back into LUFS or into the ear as loudness.

**Cannot claim:** low shelf, NLD, virtual bass, or loudness-preserving bass.

**Why this block is the plot twist:** 40 Hz is ~−35 dB on A-weighting. Cutting it barely moves \(L_{Aeq}\) and **does** move LUFS. This is the failure mode named in 3.1, implemented on purpose because equal-loudness intuition says “bass is less dangerous / less audible at low phon.” That intuition fights **A-weighted dose**.

---

### 3.4 Mid band

A-weighted envelope compressor on 300 Hz–4 kHz only.

1. Filter mid signal with IEC 61672 A-weighting (bilinear IIR at 48 kHz, 0 dB at 1 kHz).
2. Envelope \(e[n]\) (attack 5 ms, release 50 ms).
3. Level: \(L[n] = 20\log_{10}(e+\varepsilon) + 94\).
4. If \(L\) exceeds target 78, apply ratio \(R=4\):
\[
g_M[n] = 10^{-(1-1/R)\max(L-L_{\mathrm{tgt}},0)/20}
\]
Classic compressor identity: overshoot in dB is reduced by \((1-1/R)\). At 4:1, 4 dB over threshold → 3 dB of gain reduction.

**94 and 78 are uncalibrated.** Same fake offset as the dose proxy. Target 78 is “when our fake dBA exceeds 78, start compressing.” It is **not** 78 dB SPL at the eardrum.

Attack/release 5/50 ms: typical “fast-ish” compressor. Hearing-aid and mix compressors use the same knobs (Kates; Giannoulis).

A-weighting IIR tracks the analog curve well inside 300 Hz–4 kHz (<0.2 dB). Warps above ~8 kHz because bilinear transform; that region is **not** used for this detector. Good engineering note, not novelty.

**Cannot claim:** A-weighting filter, feed-forward compressor, or mid-band DRC.

**What this block would have been *for* if the hypothesis were aligned:** mids are where \(w_A(f)\) is large, so compressing mids **does** lower \(L_{Aeq}\). Ablation later shows mid-only moves dose on speech/vocals. The low shelf still dominates the LUFS disaster.

---

### 3.5 High band

Above 4 kHz:
\[
y_H = x_H \cdot \frac{1}{1+\gamma \max(0, E-T_H)}
\]
\(\gamma=0.5\), \(T_H=-12\) dBFS. When the envelope is below threshold, gain = 1. When it is above, gain < 1 (soft). “Transient-aware” just means: fast envelope, so clicks/cymbals get ducked.

**Cannot claim:** envelope limiting. Paper says it is **not** a validated perceptual model. Results later: this band almost never engages on the corpus. So the experiment is really **low shelf vs flat gain**, plus a bit of mid compression.

---

### 3.6 Crossover reconstruction

**Problem with naive splits:** independent Butterworth low / band / high are **not** magnitude-complementary. Near 300 Hz and 4 kHz the sum can peak (paper: a quiet 440 Hz tone went up 19.7% with the old bank).

**Fix:** cascaded 4th-order **Linkwitz–Riley** (two Butterworths in series per split) so each crossover is −6 dB at fc and the two sides sum to **flat / allpass**. Allpass compensation on the low path at the upper split so all three bands share delay. Linkwitz 1976; used in every speaker crossover and many multiband compressors.

Fig. 2: LR sum at 0 dB vs old Butterworth peaks. This is **verification that an earlier bug was fixed**, not a contribution. **Cannot claim** Linkwitz–Riley crossovers.

Fig. 3: 40/50/60/80 Hz tones after shelf + harmonics — 2nd and 3rd harmonics present for 40 Hz. Checks the 80–400 Hz window. Not evidence of loudness.

Fig. 4: digital A-weighting vs IEC curve. Mid detector band is accurate; 40 Hz ≈ −35 dB is the mechanism of the main result.

---

### Claim checklist for Method

| Tempting claim | Allowed? |
|---|---|
| We specified a 3-band heuristic toward a dose/loudness trade-off | Yes (as a *design*, not as a success) |
| LR4, shelves, NLD virtual bass, A-weighted compressor, envelope limiter | No — all standard |
| 300 Hz / 4 kHz / −12 dB / ratio 4 are optimal | No — prototype, not searched |
| We solve min dose s.t. loudness | No — explicit non-solver |
| Harmonics preserve bass loudness | No — paper denies it |
| Complementary crossover is new | No — Linkwitz 1976; you fixed your own earlier Butterworth bug |

---

### Status (end of Proposed Method)

- Explained: Title, abstract, keywords; Introduction; Related Work; Proposed Method.
- Next: Implementation.

---

## 4. Implementation

### Role of this section

Prove the processor is a **real, causal, streamable DSP**, not a non-causal offline trick, and list the default knobs. Reviewers use this to reproduce. It is **engineering hygiene**, not a contribution.

Code lives in `exposure_dsp/` (`proposed.py`, `crossover.py`, `aweighting.py`, `metrics.py`, …). Listings are correctly omitted from the IEEE paper.

---

### Sample rate and stack

**48 kHz, Python, numpy/scipy, offline.**  
48 kHz is the usual audio-research rate (covers 20 kHz bandwidth). Offline = process whole files, not a phone/DSP chip. **Cannot claim** a device, real-time product, or new software framework. scipy IIR/biquads are standard.

---

### Causal filters + SOS state

**Causal:** output at time \(n\) depends only on current and past samples, not the future. Required if you ever ran this on a stream (headphones). Non-causal “filtfilt” (forward–backward) would have zero phase but **cannot** run live; you did not use that.

**Second-order sections (SOS):** IIR filters factored into biquads so they stay numerically stable. State (delay registers) is **carried across blocks**, so chopping audio into hops does not reset the filter and click.

This is DSP 101 (Oppenheim/Schafer; any real-time audio plugin). **Cannot claim.**

---

### Hop size 256, streamable

256 samples at 48 kHz ≈ **5.3 ms** per hop. The processor reads a hop, splits bands, processes, writes a hop. `process_block` / `flush` in `proposed.py` implement this.

**Check:** 2 s test signal processed in **240-sample blocks** vs **one whole-file call** → max absolute sample difference **0.0**. Meaning: block boundaries do not change the output. It is actually streamable, not “streamable if you ignore edge effects.”

That check is why the negative result cannot be blamed on “you processed it wrong in chunks.” Good. Still not novelty — it is a unit test written into the paper.

---

### Peak ceiling −1 dBFS, no makeup gain

After summing bands, a limiter caps peaks at −1 dBFS so the file does not clip (0 dBFS = digital full scale; a little headroom is normal).

**“Never renormalises a quiet block back toward full scale.”**  
Some naive normalisers do: if a hop is quiet, turn it up so the hop peaks at 0 dB. That would **undo** dose reduction and make loudness jump hop-to-hop. You forbid that. The ceiling only turns **down** overs; it does not turn **up** quiet audio.

Ordinary limiter behaviour. **Cannot claim.** Important so a reviewer does not think you secretly boosted.

---

### Default parameters (Table II)

| Knob | Value | Plain meaning |
|---|---|---|
| Sample rate | 48 kHz | Standard |
| Crossover | LR4, 300 Hz / 4 kHz | Two splits, complementary |
| Sub-bass shelf | −12 dB near 100 Hz | The failure-mode knob |
| Harmonic band | 80–400 Hz, \(a_2=0.8\), \(a_3=0.35\) | NLD mix |
| Mid target / ratio | 78 / 4:1 | Fake-dBA compressor |
| Mid attack / release | 5 ms / 50 ms | Fast-ish |
| High threshold / \(\gamma\) | −12 dBFS / 0.5 | Mild duck |
| Output ceiling | −1 dBFS | Anti-clip |

These are **defaults**, not fitted to listeners. Later limitations repeat that. **Cannot claim** they are optimal.

---

### What this section is for, scientifically

Together with Figs 2–4 (flat crossover, harmonics present, A-weighting curve OK), Implementation lets you say in Results: **the negative result is a metric mismatch, not a coding bug.** That is the only intellectual use of this section.

---

### Claim checklist for Implementation

| Tempting claim | Allowed? |
|---|---|
| We implemented a causal streamable 3-band processor in Python | Yes, as a *reproducibility* statement |
| Block vs whole-file match of 0.0 | Yes, as a *verification* |
| Real-time hearing-protection device | No — offline Python |
| New DSP numerical method | No |
| Parameters are perceptually optimal | No |

---

### Status (end of Implementation)

- Explained: Title, abstract, keywords; Introduction; Related Work; Proposed Method; Implementation.
- Next: Experimental Setup.

---

## 5. Experimental Setup

### Role of this section

Define a **fair fight**: same files, proposed processor vs “turn everything down,” after forcing **one** meter to be equal. Then the other meter is the score. Also: what you measure, what you played, what you hypothesised, and what you did **not** do (listening test).

---

### 5.1 Three systems

Every clip goes through:

1. **Original** — no processing. Reference for “how much did we change the spectrum” (LSD).
2. **Frequency-flat gain** — one scalar \(G\) on the whole waveform. This **is** “turn everything down.” It is the H.870-style / Giannoulis-style baseline.
3. **Proposed** — the 3-band heuristic at Table II defaults. Not tuned per clip.

**Rejected extra baseline:** an A-weighted **broadband compressor** (same family as the mid band, but on the full signal), with its threshold searched so its \(L_{Aeq}\) or LUFS matches. On many clips it **never engaged** (fake dBA never crossed the default target). An idle compressor is not “turn it down”; it is “do nothing.” So the paper compares against **static** \(G\), which always does something. Fair. **Cannot claim** you beat a working AGC — you did not use one that was always on.

---

### 5.2 Matching (the actual experiment)

After running proposed, pick \(G\) for the flat system so that **one** number matches:

- **Matched exposure:** flat output has the same digital \(L_{Aeq}\) proxy as proposed (within ~0.01–0.05 dB).
- **Matched loudness:** flat output has the same integrated LUFS as proposed (`pyloudnorm` / BS.1770).

Then look at the **other** number.

**Why this is the right comparison:** without matching, “proposed has lower \(L_{Aeq}\)” could just mean “we turned it down more.” Matching asks: *at the same loudness, who has less dose?* and *at the same dose, who is louder?*

**Critical fact:** for **frequency-flat** \(G\), both meters move by about \(20\log_{10} G\). So the two matching rules are **not two independent experiments**. They are the same difference, opposite sign:

- If at equal LUFS, proposed \(L_{Aeq}\) is **+1.17 dB** vs flat, then at equal \(L_{Aeq}\), proposed LUFS is **−1.17 dB** vs flat.

The paper says this explicitly. The interesting part is **the sign** and **which genres** produce it — not “we ran two studies.”

**Cannot claim:** two separate confirmations of the same finding.

---

### 5.3 Metrics

**Digital \(L_{Aeq}\) proxy**
\[
L_{Aeq}^{\mathrm{proxy}} = 20\log_{10}\mathrm{RMS}\{w_A * x\} + 94
\]
A-weight, then RMS, then add **94**. 94 is a developer offset (full-scale sine looking “about 94”). **Not** pascals, **not** an ear simulator, **not** H.870 CSD. **Cannot claim** dB SPL or hearing dose in Pa²h.

**Loudness:** integrated LUFS (BS.1770). Standard programme meter. **Not** a listener saying “these two are equally loud in a booth.” **Not** ISO 532 sones.

**LSD (log-spectral distance):** Welch power spectra of processed vs original, RMS of dB differences per bin. Objective “how much did the spectrum move.” Used in speech coding papers as a distortion number. **Not** quality, **not** MUSHRA, **not** PEAQ. Smaller LSD ≠ “sounds better” (a tiny overall volume change can have small LSD; a mid-only cut can have small LSD but wreck vocals subjectively — or the reverse).

---

### 5.4 Material

\(n=20\), 48 kHz mono:

- 16 Freesound CC recordings (IDs listed): bass loops, drums, choir, vocal, speech, cymbals.
- 4 **synthetic** clips built in code (bass-heavy, speech-like, transient, mixed).

Synthetics are labelled; conclusions also given on the 16 real files alone (mean gap 1.17 → 0.92 dB, **same sign**). Good. Still a **small, convenience corpus**, not a standard test set (no EBU SQAM, no MUSDB, no formal speech corpus). **Cannot claim** “all music” or a representative survey of listening.

---

### 5.5 Hypotheses

- **H2 (matched loudness):** at equal LUFS, proposed \(L_{Aeq}\) **<** flat. This is the **main** claim the title hopes for.
- **H1 (matched exposure):** at equal \(L_{Aeq}\), proposed is **louder** (higher LUFS) and/or **closer** to original in LSD.

H1 and H2 are duals for the LUFS/\(L_{Aeq}\) pair when the baseline is flat. LSD is the only part of H1 that is not a strict dual.

**Cannot claim** either hypothesis from the *setup*; Results reject both as stated (LSD mixed, not a win).

---

### 5.6 Listening notes

No MUSHRA, no PEAQ, no listener scores. WAVs exist for informal listening. A proper test would lock playback volume, randomise order, rate quality / bass / clarity / loudness.

Until then, **quality claims are not allowed.** LUFS ≠ “sounds as loud.” LSD ≠ “sounds as good.”

---

### Claim checklist for Setup

| Tempting claim | Allowed? |
|---|---|
| We defined a matched-meter comparison vs flat gain | Yes |
| We evaluated a real AGC that always engages | No — idle compressor dropped |
| 94 offset is ear SPL | No |
| LUFS is booth-matched loudness | No |
| LSD is perceived quality | No |
| n=20 covers listening in general | No |
| Two matching rules are two experiments | No — dual views |

---

### Status (end of Experimental Setup)

- Explained: through Experimental Setup.
- Next: Results.

---

## 6. Results

### Role of this section

Report the fight. **H2 loses. H1 loses as a loudness claim.** Explain *why* with the A vs K weighting mismatch. Ablation shows the low shelf is the culprit. A mid-band sweep is a side characterisation, not the main result.

Sign convention (easy to get backwards):

- **\(\Delta L_{Aeq}\)** at matched LUFS = proposed minus flat. **Positive = proposed has more dose = worse.**
- **\(\Delta\)LUFS** at matched \(L_{Aeq}\) = proposed minus flat. **Negative = proposed quieter.** For a flat baseline these two are negatives of each other.

---

### 6.1 Matched loudness: the main test (H2)

Fig. 5: per clip, proposed \(L_{Aeq}\) − flat \(L_{Aeq}\) at **equal LUFS**.

| Aggregate | Value |
|---|---|
| Mean \(n=20\) | **+1.17 dB** |
| Median | +0.61 dB |
| 16 Freesound only | +0.92 dB |
| Worse by >0.05 dB | 12 clips |
| Tie within 0.05 dB | 6 clips |
| Slightly better | 2 clips (female vocal −0.07, command speech −0.12) |

**H2 is not supported.** At the same programme loudness, the 3-band system has a **higher** digital dose proxy than turning everything down.

**By genre**

- Six real bass/drum loops: **+1.59 to +2.67 dB** (mean +1.98). This is where you lose.
- Speech, choir, vocal, cymbals as a group: about **+0.28 dB** (near tie).
- Synthetic bass / mixed: **+4.91 / +3.87 dB** — they were built with strong 40–50 Hz, so they **inflate the mean** but do not **create** the finding (real bass loops already go the same way).

The two tiny wins are mid-heavy clips where the **mid compressor** actually works and the bass shelf barely matters. They are not a “speech mode success”; they are −0.1 dB noise-level edges.

**Cannot claim:** lower exposure at matched loudness; a method that “works on vocals.”

Per-clip table: \(\Delta L_{Aeq} = -\Delta\)LUFS on every row (flat baseline dual). LSD proposed mean 0.49 vs flat 0.40 — flat is closer to original on average.

---

### 6.2 Why the proxy moves the wrong way (the science)

Fig. 6: for proposed vs original, plot LUFS drop vs \(L_{Aeq}\) drop.

- If the two meters agreed, points would sit on the 1:1 line.
- **Bass clips sit far to the right:** LUFS down 2–5 dB, \(L_{Aeq}\) barely moves.
- Speech/cymbals sit near the origin (processor did little).

**Mechanism (this is the paper’s real finding):**

1. A-weighting at 40 Hz ≈ **−35 dB**. That energy was almost gone from the dose meter *before* you processed.
2. BS.1770 **K-weighting** does **not** dump 40 Hz that hard, so LUFS **notices** the −12 dB shelf.
3. Low shelf does what it was told: remove sub-bass. LUFS falls. \(L_{Aeq}\) does not.
4. To match LUFS, flat \(G\) must apply that same loudness cut to the **whole** spectrum, including **1–4 kHz**, which A-weighting **does** count.
5. Therefore flat \(L_{Aeq}\) falls **further**. Proposed looks worse on dose at equal LUFS.

One-line: **you spent the loudness budget on a band the dose filter already ignores.** “Cheap bass cuts” are the wrong allocation for an A-weighted objective.

**Not a bug:** crossover sums flat (Fig. 2), 40 Hz harmonics exist (Fig. 3), stream = whole-file (Implementation). Metric mismatch, not DSP failure.

**Cannot claim:** a new weighting theory (A vs K is known). **Can claim:** this *allocation* hits that known mismatch, measured on this corpus.

---

### 6.3 Matched exposure: H1 (dual + LSD)

Fig. 7 left: at equal digital \(L_{Aeq}\), proposed is **quieter by 1.17 dB LUFS** on average. Opposite sign of Fig. 5, as predicted. **H1 fails as loudness preservation.** At the same A-weighted proxy, flat gain keeps more LUFS than cutting sub-bass.

Fig. 7 right / table: LSD vs original at that match.

- Mean LSD: proposed **0.49 dB**, flat **0.40 dB**. Flat closer on average (on bass, flat barely moves, so LSD is tiny).
- Where mid compressor *does* bite (female vocal, command speech): flat of the same \(L_{Aeq}\) drop smears the **whole** spectrum (LSD 1.40 and 1.69) vs band-limited proposed (0.57 and 0.67). So proposed is **not uniformly worse** on LSD; it avoids the biggest broadband shifts.

**Cannot read LSD as quality.** Paper says so. No listening test.

---

### 6.4 Ablation (which knob caused the loss)

Enable bands one at a time; mean change vs original (not vs matched flat gain — different comparison).

- **Crossover only:** no level change (sum is allpass). Good.
- **Mid only:** moves \(L_{Aeq}\) on speech/vocals; does little on bass. This is the *dose-relevant* band.
- **+ Low band:** this is what **drops LUFS**. The disagreement is born here.
- **+ High band:** almost nothing; transients rarely crossed −12 dBFS. High path is unused on this set.
- **Full ≈ mid+low.**

**Default DRC** in that figure is a full-band A-weighted compressor at the default target, **not** the LUFS-matched flat gain of Fig. 5. Do not mix those two baselines.

**Punchline:** the block that was supposed to be the advantage (bass cut + harmonics) is the block that produces the exposure/loudness disagreement.

---

### 6.5 Mid-band target/ratio sweep

One synthetic six-tone-plus-noise clip. Lower target / higher ratio → lower \(L_{Aeq}\) proxy, higher LSD. Expected compressor behaviour (more squash, more spectral change).

Default 78 / 4:1 is a mild operating point (−0.83 dB proxy, LSD 0.88 on that debug signal). **Not** the main result, **not** perceptual quality. Only shows the mid compressor is not stuck.

---

### Claim checklist for Results

| Tempting claim | Allowed? |
|---|---|
| H2 supported (lower dose at equal LUFS) | **No** — +1.17 dB |
| H1 supported (louder at equal dose) | **No** — −1.17 LUFS |
| Failure is concentrated in bass | Yes |
| Mechanism is A-weighting vs K-weighting on the low shelf | Yes (interpretation of *your* test) |
| Implementation bug | No — checks contradict that |
| Better quality (LSD mixed, no listeners) | No |
| High band is an important contribution | No — unused |
| Sweep proves a good compressor setting | No — one synthetic clip |

---

### Status (end of Results)

- Explained: through Results.
- Next: Limitations.

---

## 7. Limitations

### Role of this section

A list of **claims you are forbidden to make**, written by you on purpose so a reviewer cannot say you oversold. Every sentence here is a fence around the Results.

---

**“This study compares two digital processing rules.”**  
You compared proposed vs flat \(G\) on files. Not a clinical trial, not a product vs product, not humans over weeks of listening.

**“It does not show prevention of hearing loss, and it does not report ear-level SPL.”**  
No audiograms, no TTS/PTS, no dummy-head pascals. **Cannot claim** “safer for hearing,” WHO compliance, or dB SPL. The whole dose story is a **proxy**.

**“The \(L_{Aeq}\) figures use an uncalibrated offset.”**  
The +94. A real H.870 number needs: this earphone, this volume, **IEC 60318-4 occluded-ear simulator** (HATS / coupler), then DRP-to-diffuse-field correction. Even that is a plastic ear, not *your* ear. **Cannot claim** calibrated dose.

**“LUFS is a standard loudness meter, not a booth loudness match.”**  
Nobody sat in a room and said “these two are equally loud.” Matching LUFS ≠ matching perceived loudness, especially for bass (exactly where you fail). **Cannot claim** listeners heard them as equally loud.

**“Band edges, shelf depth, and compressor constants were not searched over listeners.”**  
300 Hz, 4 kHz, −12 dB, ratio 4, target 78: prototype. Maybe other knobs would look better. You did not show this is the best 3-band design — you showed **this** design loses. **Cannot claim** “frequency-selective limiting fails” in general; only **this bass-first heuristic** vs flat gain.

**“No Zwicker or Moore–Glasberg model is in the loop.”**  
Loudness in the experiment is LUFS only. A true loudness model might score bass differently. **Cannot claim** you tested psychoacoustic loudness.

**“No PEAQ or MUSHRA scores were collected.”**  
No objective perceptual quality metric, no listening test. LSD stays a spectrum distance. **Cannot claim** quality, transparency, or “sounds better on vocals.”

**“The high band did little on this set, so the experiment mainly contrasts a low-shelf-plus-harmonics path with flat gain.”**  
You advertised a 3-band processor. Empirically it is a **bass shelf (+ harmonics)** vs flat \(G\), with a bit of mid compression on speech. **Cannot claim** a full 3-way “adaptive limiter” was tested.

**“Four synthetic clips are in the mean; removing them lowers the gap from 1.17 dB to 0.92 dB and does not reverse the sign.”**  
Honesty about inflation. The conclusion **survives** without synthetics. Good. Still \(n=16\) real files is small.

---

### Claim checklist for Limitations

These are not optional. If the abstract or conclusion contradicts this section, reviewers will cite it against you.

| Claim | Blocked by this section |
|---|---|
| Hearing protection / safer listening | Yes |
| Ear-level dB SPL / H.870 dose | Yes |
| Equal perceived loudness | Yes |
| Optimal or general frequency-selective limiter | Yes |
| Better quality | Yes |
| Three-band system fully exercised | Yes (high unused) |
| Synthetics created a fake result | No — sign survives without them |

---

### Status (end of Limitations)

- Explained: through Limitations.
- Next: Conclusion (last section of the paper).

---

## 8. Conclusion

### Role of this section

Restate the **question**, the **number**, the **mechanism**, the **design rule**, and the **next experiment**. It must not grow new claims that Results/Limitations already forbade. This draft stays aligned: it reports a **loss** and a **rule**, not a winning limiter.

---

**“We asked whether a three-band, perceptually motivated limiter could reduce a digital A-weighted exposure proxy more than turning the whole signal down, at the same LUFS.”**

Repeats H2 in one sentence. Words that keep you honest: *digital*, *proxy*, *same LUFS*. “Perceptually motivated” only means ISO 226 / virtual bass *inspired* the knobs — not that a loudness model ran.

**“On 20 clips it did not: the proposed proxy was 1.17 dB higher on average, and 1.6 to 2.7 dB higher on real bass loops.”**

The answer. Mean loss; bass is where it hurts. **Cannot spin this as a success.**

**“Vocals, speech, and short transients were a tie.”**

Processor barely did the bass thing there, so it did not beat flat gain either. Tie ≠ “works for speech.”

**“Cutting sub-bass spends loudness on a band that A-weighting already ignores, so a flat gain that matches LUFS wins on \(L_{Aeq}\).”**

The mechanism, compressed. This is the sentence a reader should remember.

**“The useful outcome is that comparison.”**

Contribution restated: **not** a new DSP block, **the test** (and the negative answer). Matches Introduction: *ingredients are not new; the comparison is the contribution.*

**“If an A-weighted dose limit is the constraint, frequency-selective bass cuts are a poor allocation; any later design should spend attenuation where \(w_A(f)\) is large, or replace A-weighting with a metric that actually tracks the intended risk.”**

This is a **design rule**, not a demonstrated new system.

- *If A-weighting is the constraint* — H.870-style. Then do **not** spend the cut on ~40 Hz.
- *Spend attenuation where \(w_A(f)\) is large* — roughly **1–4 kHz**. You **did not test** that allocator. It is a recommendation from the failure, not a result.
- *Or replace A-weighting* — if you care about bass energy as risk, C/Z-weighting or ear-canal energy might be the dose metric; then bass cuts could make sense. Also untested here.

**Can claim:** *this* bass-first heuristic is a poor allocation for an A-weighted proxy.  
**Cannot claim:** you already built the better mid-cut limiter, or that A-weighting is the wrong legal standard.

**“Calibrated ear-simulator measurements and a locked-volume listening test remain the next experimental step.”**

Points at Limitations: IEC 60318-4 + MUSHRA-style test with volume locked. Until that exists, no SPL and no quality. Correct ending.

---

### What the conclusion is allowed to be

| Sentence type | In this conclusion? | OK? |
|---|---|---|
| We asked H2 | Yes | Yes |
| We lost (+1.17 dB; worse on bass) | Yes | Yes |
| Mechanism: A-weighting ignores the cut band | Yes | Yes |
| The comparison is the contribution | Yes | Yes |
| Design rule for the *next* algorithm | Yes, as advice | Yes, if not sold as a result |
| We reduced exposure / preserved loudness | No | Would be illegal given Results |
| We protect hearing | No | Would contradict Limitations |

---

### Whole-paper recap (now that every section is done)

1. **Question:** can frequency-selective gain beat “turn it down” on digital \(L_{Aeq}\) at matched LUFS?
2. **Apparatus:** known blocks (LR4, bass shelf, virtual-bass NLD, A-weighted compressor). Heuristic, not a solver.
3. **Fight:** proposed vs flat \(G\), match one meter, read the other (duals).
4. **Score:** H2 no, H1 no (as loudness). Bass-driven. A vs K mismatch.
5. **What is yours:** that matched comparison and the allocation lesson.
6. **What is not yours:** the DSP ingredients, H.870, loudness theory, virtual bass, a winning limiter, hearing safety.

---

### Status

- Explained: **entire paper** (title/abstract through Conclusion).
- Notes file is complete for the walkthrough. Further Qs can still be appended.
- There is no next *section*. Next work, if you want it, is the mid-cut follow-up experiment — not more of this draft’s text.

---

