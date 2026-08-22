# Master Audio Reuse Audit — N3/Pool Production Pipeline

Scope: `er003_b1_p9a_audio.py`, `er003_v1_n3_01_articles_generate.py`, `er003_v1_n3_01_scaffold_generate.py`,
`er003_v1_n3_01_assemble.py`, `er003_v1_n3_01_tts_generate.py`, `er006_pool_pilot_01_audio.py`,
`er006_pool_pilot_01_topics.py`, `er003_v1_sing01_voice01_generate.py`, `er003_v1_sing01_news_tail_fix.py`,
`er003_v1_sing01_point_headings_aoede.py`, `er003_v1_crosslevel_audio_02_common.py`.

Evidence base: source code (read directly, not inferred), the timeline/audit JSON produced by three real
Pool Pilot production runs (`pool_benches`, `pool_subscriptions`, `pool_startups`, plus the `pool_benches_luna`
comparison run) under `er006_output/pool_pilot_01/`, and direct duration/byte-size checks on the actual `.wav`
files referenced by the code. **Read-only audit — no files modified, no paid API calls made.**

---

## 1. Headline numbers

| Metric | Value |
|---|---|
| Distinct spoken-text TTS segments per topic (B1+A2 pair) | **66** (32 in B1, 34 in A2) |
| Of those, Category A — fully fixed text, already reused via file-copy (not regenerated) | **19** (9 in B1, 10 in A2) |
| Of those, Category C — content-dependent, must be freshly synthesized every episode | **47** (23 in B1, 24 in A2) |
| Category A segment-count share already avoided today | **19 / 66 ≈ 29%** |
| Category A TTS-origin audio duration per episode | B1 ≈ 13.6 s / 351.5 s total (≈3.9%); A2 ≈ 13.6 s / ≈365 s total (≈3.7%) |
| + external mp3 (Intro/Notification/Point-cue/Outro, never TTS, already reused) | ≈26.6 s/episode more |
| **Combined already-static share of a typical episode** | **≈11% of runtime is non-regenerated audio today** |
| New Category-B opportunity found: exact-duplicate Key Phrase text reused across B1↔A2 of the *same* topic, same voice/model/style (code-verified identical path) | **4 exact duplicates found across the 3 real topics audited** (≈1.3/topic) → projects to **≈27–40 avoidable kp TTS calls/day** at 20–30 topics/day |
| Real drift already found in the "already reused" Category A pool | `welcome.wav` differs in duration (2.111s vs 2.561s) and byte size between the two source directories that both currently feed identical spoken text into different episodes — see §5 |

**Bottom line:** the pipeline already gets roughly **29% of its fixed-text segments for free** via an ad-hoc
file-copy mechanism, but that mechanism has **no verification, no schema, and has already silently drifted once**
(§5). The realistic *incremental* saving from formalizing this into a governed Master Audio Key system is modest
in raw seconds (content-dependent narration — Full Story, Points, Comments, Preview — dominates episode runtime
and is inherently non-reusable), but it removes a real correctness risk and captures a handful of previously
invisible cross-level duplicate-generation cases per topic.

Full detail follows.

---

## 2. Segment inventory and classification

### 2.1 B1 episode (`er003_v1_n3_01_tts_generate.py::generate_b1_segments`, `er003_v1_n3_01_assemble.py::build_b1_timeline`)

| # | Segment | Spoken text | Voice | Model | Category | Currently regenerated via live TTS? |
|---|---|---|---|---|---|---|
| 1 | Intro | (external mp3, no words) | — | — | A (external asset) | No — mp3 file, never TTS |
| 2 | Welcome | "Welcome to English Your Way." | Charon | `gemini-2.5-pro-preview-tts` | **A** | No — copied from `B1_SHARED_SOURCE_DIR` if not already present |
| 3 | Topic intro | `"Today's topic is {article title}."` | Charon | `gemini-2.5-pro-preview-tts` | **C** (wrapper not decomposed — see §4) | Yes, every episode |
| 4 | Notification 1/2/3 | (external mp3, no words) | — | — | A (external asset) | No, reused 3×/episode from one file |
| 5 | Preview intro | "Here's a quick preview." | Charon | `gemini-2.5-pro-preview-tts` | **A** | No — shared copy |
| 6 | Preview | LLM-written English preview text | Charon | `gemini-2.5-pro-preview-tts` | C | Yes |
| 7 | Key phrases intro | "Here are today's key phrases." | Charon | `gemini-2.5-pro-preview-tts` | **A** | No — shared copy |
| 8 | Number word (×5, "One."… "Five.") | Fixed | Charon | `gemini-2.5-pro-preview-tts` | **A** | No — shared copy (`num_one_charon.wav` … `num_five_charon.wav`) |
| 9 | Key Phrase English component (×5) | The key phrase itself | Aoede | `gemini-2.5-pro-preview-tts` | C | Yes (reused 2× *within* the same episode via `np.concatenate`, per existing design) |
| 10 | Key Phrase Japanese meaning (×5) | Japanese gloss | Charon | `gemini-3.1-flash-tts-preview` | C | Yes |
| 11 | Full story intro | "Now, the full story." | Charon | `gemini-2.5-pro-preview-tts` | **A** | No — shared copy |
| 12 | Comment 1–4 | LLM-written bridge/commentary text | Charon | `gemini-2.5-pro-preview-tts` | C | Yes |
| 13 | Full Story Part 1/2 | Article body | Aoede | `gemini-2.5-pro-preview-tts` | C | Yes |
| 14 | Point Notification cue (×2) | (external mp3, no words) | — | — | A (external asset) | No — same file both times |
| 15 | Point One/Two semantic heading | Article's own H3 heading text | Aoede | `gemini-2.5-pro-preview-tts` | C | Yes |
| 16 | Point One/Two body | Article body | Aoede | `gemini-2.5-pro-preview-tts` | C | Yes |
| 17 | In One Line | LLM-written closing line | Aoede | `gemini-2.5-pro-preview-tts` | C | Yes |
| 18 | Outro | (external mp3, no words) | — | — | A (external asset) | No |

B1 live-TTS segment count (Category C only): **23** (topic_intro, preview, comment_1-4, point_one_heading,
point_two_heading, full_story_part1, full_story_part2, point_one, point_two, in_one_line, kp1-5_en, kp1-5_ja).
B1 Category A TTS-origin segments (already not regenerated): **9** (welcome, preview_intro, key_phrases_intro,
full_story_intro, num_one…num_five).

### 2.2 A2 episode (`generate_a2_segments`, `build_a2_timeline`)

Same structure, with two differences: (a) A2 has an extra fixed segment, **"Point explanation" = "ポイント解説"**
(Japanese, fixed, Category A, spoken once before the Preview — B1 has no equivalent), and (b) A2 carries its own
**Japanese title** per article (`JAPANESE_TITLES` dict in `er003_v1_n3_01_tts_generate.py`) — content-dependent,
Category C. A2's shared Category-A segments (welcome/preview_intro/point_explanation/key_phrases_intro/
full_story_intro/num_one…five) are read directly from `A01_NARRATION_DIR` = `er003_output/b1_p9a/A01/narration`
— i.e. the **same nominal text is shared service-wide across both B1 and A2**, not just within a level.

A2 live-TTS segment count (Category C): **24** (topic_intro, japanese_title, preview, comment_1-4,
point_one_heading, point_two_heading, full_story_part1, full_story_part2, point_one, point_two, in_one_line,
kp1-5_en, meaning_1-5).
A2 Category A TTS-origin segments: **10** (welcome, preview_intro, point_explanation, key_phrases_intro,
full_story_intro, num_one…num_five).

### 2.3 Category A — fully-fixed segment text (exact strings, source: `er003_v1_sing01_voice01_generate.py` and `er003_v1_crosslevel_audio_02_common.py`)

| Text | Language | Voice | Frequency/episode | Frequency/day (20–30 topics → 40–60 episodes) | Actually regenerated via TTS? |
|---|---|---|---|---|---|
| "Welcome to English Your Way." | en | Charon | 1 | 40–60 (shared file, would be 1 physical TTS call if never cached) | No (copied) |
| "Here's a quick preview." | en | Charon | 1 | 40–60 | No (copied) |
| "Here are today's key phrases." | en | Charon | 1 | 40–60 | No (copied) |
| "Now, the full story." | en | Charon | 1 | 40–60 | No (copied) |
| "One." / "Two." / "Three." / "Four." / "Five." | en | Charon | 5 | 200–300 | No (copied) |
| "ポイント解説" (Point explanation) | ja | (A2 only) | 1 (A2 only) | 20–30 | No (copied) |

These are the only segments in the current codebase where the **spoken text is byte-for-byte identical across
every episode regardless of topic or level**. Historical note: an earlier iteration (`er003_v1_sing01_voice01_generate.py`,
`jobs_english`) also had fixed `"Point One."` / `"Point Two."` narration — this is **superseded** by
`ER-003-POINT-NOTIFICATION-01` (documented in `er003_v1_n3_01_scaffold_generate.py`), which replaced the spoken
number with the Point-Notification mp3 cue + the article's own semantic heading. Not counted in the current
inventory.

### 2.4 Category B — conditionally-fixed (wrapper phrases around variable content)

None of the wrapper phrases in the current code are **actually decomposed** into a fixed-prefix + variable-suffix
pair at the TTS-call level — every "Category B–shaped" text (e.g. `topic_intro`) is synthesized as a single
whole-sentence TTS call, so today it behaves as Category C even though part of its text is constant. This is
the clearest architectural gap and the main Category-B opportunity:

| Segment | Fixed wrapper | Variable part | Voice(s) | Why it's not yet Category B in practice |
|---|---|---|---|---|
| Topic intro | `"Today's topic is "` / trailing `"."` | Article title | B1: Charon · A2: Aoede (different voice per level — cannot share one master across levels) | Whole sentence generated as one TTS call; fixed prefix re-synthesized every time |
| A2 Japanese title lead-in | none found — `japanese_title` is generated as a bare title with no fixed wrapper | — | — | N/A |

If implemented, the fixed prefix could be pre-mastered **once per (level, voice)** — i.e. 2 masters total (B1/Charon,
A2/Aoede) — and only the variable title portion would need a short per-episode TTS call, spliced after the
fixed-prefix master. Not implemented in this audit; flagged as a proposal only, per the task constraints.

### 2.5 Category C confirmation

All of: Preview, Comment 1–4, Full Story Part 1/2, Point One/Two heading, Point One/Two body, In One Line, the
Key Phrase word/phrase itself, and (A2) the Japanese title, are LLM-generated per article and are correctly
excluded from any reuse proposal.

---

## 3. Quantified reuse potential (real production data)

Source: `er006_output/pool_pilot_01/{pool_benches,pool_subscriptions,pool_startups,pool_benches_luna}/{b1b,a2}/audit/timeline.json`.

| Episode | Total duration | Category-A TTS-origin duration (welcome/preview_intro/key_phrases_intro/full_story_intro/point_explanation/num_one-five, embedded in KP blocks) | Category-A share |
|---|---|---|---|
| pool_benches / b1b | 351.5 s | ≈13.6 s | 3.9% |
| pool_benches / a2 | 357.2 s | ≈13.6 s | 3.8% |
| pool_subscriptions / b1b | 349.2 s | ≈13.6 s | 3.9% |
| pool_subscriptions / a2 | 365.2 s | ≈13.6 s | 3.7% |
| pool_startups / b1b | 328.8 s | ≈13.6 s | 4.1% |
| pool_startups / a2 | 371.7 s | ≈13.6 s | 3.7% |
| **Average** | **353.9 s (≈5.9 min)** | **≈13.6 s** | **≈3.9%** |

Adding the external mp3 assets that are already reused with zero TTS cost (Intro 10.7s, Notification×3 = 6.1s,
Point-Notification×2 = 3.6s, Outro 6.1s ≈ 26.6s total, not TTS-generated so not counted in "TTS reduction," but
relevant context) — **≈11.3% of a typical episode's runtime is already static, non-regenerated audio**. The
remaining ≈89% is Full Story / Points / Comments / Preview / Key Phrase content — inherently content-dependent
and correctly out of scope for any reuse layer.

### 3.1 TTS API call volume, current state

| | Per topic (B1+A2 pair) | Per day (20–30 topics → 40–60 episodes) |
|---|---|---|
| Total distinct spoken-text segments | 66 | 1,320–1,980 |
| Category A (already avoided via ad hoc copy, 0 live TTS calls) | 19 | 380–570 |
| Category C (live TTS call every time, unavoidable today) | 47 | 940–1,410 |
| **Segment-count share already avoided** | **29%** | **29%** |

### 3.2 Newly identified incremental opportunity (not yet captured by any existing mechanism)

**Cross-level exact-duplicate Key Phrases.** `repro01.generate_key_phrase_component_verified()` is called with
identical parameters (voice=Aoede, same model, same style path) for both the B1 and A2 Key Phrase English
component — the *only* thing that can differ between the two calls is the phrase text itself. Checking the three
real topics' `keywords_canonicalized.json` files for exact `used_form` string matches between b1b and a2 of the
**same topic**:

| Topic | Exact duplicate Key Phrase (B1 == A2, same voice/model/style) |
|---|---|
| pool_benches | "hostile architecture" |
| pool_subscriptions | "sludge" |
| pool_startups | "network effect", "blitzscaling" |

4 exact duplicates across 3 topics (≈1.3/topic). Near-misses that were **correctly excluded** because the text
differs (per the task's exact-match-only constraint): "become like a porch" vs "like a porch"; "dark pattern" vs
"dark patterns". At 20–30 topics/day this projects to **≈27–40 avoidable Key Phrase English-component TTS calls
per day**, each ~1–2.5s of audio (based on observed `kp*_en.wav` file sizes), i.e. roughly 30–60 seconds/day of
redundant TTS generation that is currently 100% safe to dedupe (identical voice, model, and style-instruction
already verified by code inspection, not just string matching — satisfying the task's "only when level/speaker/
voice/style-instruction also match" requirement).

**No cross-topic (different news story) exact Key Phrase duplicates were found** in the 3-topic sample audited —
this is expected at small scale; the user's hypothetical examples ("network effects", "market share",
"subscription model") did not literally recur verbatim across *different* topics here, only within the same
topic across its two levels.

### 3.3 Net reduction estimate

- **Already realized today** (fragile, ungoverned): 19/66 ≈ 29% of segments, ≈3.9% of episode duration.
- **Incremental, newly identified, safe to add**: ≈1.3 duplicate Key Phrase calls/topic (≈2% of the 66
  per-topic segments) — small in aggregate because the dominant cost (Full Story, Points, Comments, Preview) is
  irreducibly content-dependent.
- **Architectural opportunity requiring implementation work** (topic-intro wrapper decomposition): would not
  reduce call *count* (still 1 title-only call per episode) but would cut the TTS-generated duration of that
  segment by roughly the fixed-prefix's share (~40–50% of "Topic intro"'s 5–6s, i.e. ~2–3s × 40–60 episodes/day
  ≈ 80–180s/day).
- **Combined realistic ceiling once governed**: roughly **30–33% of segment-level TTS calls avoided**, and
  **≈4–6% of total TTS-generated audio duration** avoided — modest in proportion to full episode runtime, but
  meaningful in absolute TTS spend at 40–60 episodes/day, and it eliminates a real correctness risk that already
  exists today (§5).

---

## 4. Same-Key-Phrase reuse across different topics

`er006_pool_pilot_01_topics.py` contains only `TOPIC_JA` — Japanese background-research briefs for the writer/LLM,
not the canonical Key Phrase text itself (that's chosen later by the LLM key-phrase selector, per-article, and
lands in `keywords_canonicalized.json`). So this file itself shows no overlapping Key Phrase strings — the
actual overlaps had to be checked at the `keywords_canonicalized.json` level (see §3.2). Findings:

- Within the 3 real topics audited, exact-string overlap only occurred **between the B1 and A2 version of the
  same topic**, never between two different topics.
- At full scale (20–30 topics/day drawn from a wider Pool-topic catalog than just these 3), cross-topic exact
  matches ("network effects" recurring in an unrelated startup story next week, etc.) are plausible but were not
  observed in this sample — recommend the Master Audio Key system's lookup be topic-agnostic (keyed on text+voice+
  model+style+level, not on topic id) so it opportunistically catches such matches whenever they occur, rather
  than trying to predict them in advance.

---

## 5. A real drift already found (motivating finding for the schema)

`er003_v1_n3_01_assemble.py` for B1 reads shared narration from files named `{name}_charon.wav` inside each
theme's own narration directory, populated by `copy_b1_shared_assets()` copying from
`er003_output/b1redesign_audio_01/IRAN01/narration/` (`B1_SHARED_SOURCE_DIR`). A2, however, reads the same
nominal segments directly from `er003_output/b1_p9a/A01/narration/{name}.wav` (`A01_NARRATION_DIR`) — a
**different directory, different filename convention, and a different original TTS generation run**, dated over
a week apart (Aug 7 vs Aug 16).

Direct comparison of the two files that are both supposed to say "Welcome to English Your Way.":

| File | Duration | Size |
|---|---|---|
| `er003_output/b1_p9a/A01/narration/welcome.wav` (feeds A2) | 2.111 s | 101,370 bytes |
| `er003_output/b1redesign_audio_01/IRAN01/narration/welcome_charon.wav` (feeds B1) | 2.561 s | 122,970 bytes |

These are **two independently-generated recordings of the same fixed text**, not the same audio reused — a
~0.45s / 21% duration difference. (By contrast, `preview_intro.wav` in both locations happens to match exactly
— 1.451s, 69,690 bytes — but there is no mechanism currently *guaranteeing* that; it appears to be coincidental
file reuse from a shared origin at some point in the project's history, not verified equality.) This is exactly
the class of silent drift a Master Audio Key system with content-hash verification is meant to catch — under the
current ad hoc copy-if-not-exists pattern, nothing would detect or flag this kind of mismatch, and B1/A2 listeners
are currently hearing measurably different "Welcome" audio despite the spec intent being one canonical greeting.

---

## 6. Proposed Master Audio Key schema

A `master_audio_id` should be a stable hash over a structured key, not a free-form string, so equality can be
checked mechanically rather than by convention. Proposed fields:

```
MasterAudioKey = {
  "schema_version":            str,   # versions this key structure itself
  "language":                  str,   # "en" | "ja"
  "level":                     str | null,  # "B1" | "A2" | null (service-level, shared across both — e.g. Welcome)
  "speaker_voice":              str,   # e.g. "Charon", "Aoede" (exact TTS voice name)
  "tts_model_id":               str,   # e.g. "gemini-2.5-pro-preview-tts", "gemini-3.1-flash-tts-preview"
  "style_instruction_id":       str,   # identifies WHICH instruction template was used
  "style_instruction_version":  str,   # version/hash of that template's content
  "instruction_path":           str,   # "primary" | "minimal_fallback" (fallback prompts differ from primary — must not silently reuse across the two)
  "canonical_text_hash":        str,   # sha256 of the exact spoken text string (post reading-safety normalization, e.g. fraction/number-word substitution — the ACTUAL string sent to the TTS API, not the display text)
  "canonical_text_preview":     str,   # first ~60 chars, for human debugging only, not part of the hash
  "audio_processing_version":   str,   # trim policy (e.g. safety_margin_seconds value), resample target, gain/normalization method version — all bundled as one version string
  "sample_rate":                int,
  "channels":                   int,
  "created_at":                 str,   # ISO timestamp of when this master was generated
  "source_article_id":          str | null,  # for audit trail only, NOT part of equality — a service-level master must not be tied to one article's output directory (see §5 finding)
}
master_audio_id = sha256(json.dumps({k: v for k, v in MasterAudioKey.items() if k not in EQUALITY_EXCLUDED_FIELDS}, sort_keys=True))
# EQUALITY_EXCLUDED_FIELDS = {"canonical_text_preview", "created_at", "source_article_id", "schema_version"}
```

Two audio requests are safely interchangeable **only if every field except the explicitly-excluded audit-only
fields matches exactly**. `level` is nullable specifically to model the real service-level-shared case (Welcome,
Preview intro, etc. — currently shared across B1 and A2, per §2.2) versus level-specific segments (Point
explanation, A2-only).

### 6.1 Invalidation rules

| Change | Must invalidate? | How the schema detects it |
|---|---|---|
| Voice/speaker change (e.g. Charon → Aoede) | Yes | `speaker_voice` differs |
| TTS model change (e.g. `gemini-2.5-pro-preview-tts` → newer) | Yes | `tts_model_id` differs |
| Style-instruction content change (even same template name, edited wording) | Yes | `style_instruction_version` differs (must be a content hash, not a manually-bumped counter, to prevent forgetting to bump it) |
| Switch between primary instruction and minimal-fallback instruction | Yes | `instruction_path` differs — **critical**: the code shows fallback paths exist precisely because the primary instruction sometimes fails; a master generated via fallback must never silently satisfy a request expecting the primary path's tone, since they are different instructions even for the same text/voice/model |
| Spoken text change (any character, including reading-safety normalization output) | Yes | `canonical_text_hash` differs — must hash the *post-normalization* TTS input text (after number-word/curly-quote/fraction substitutions), not the pre-normalization "canonical_text" field the code already tracks separately, because two canonical texts that normalize to the same TTS input ARE safely reusable, and identical canonical texts that normalize differently (rare, but possible if normalization rules change) are NOT |
| Speed/pacing change | Yes | Not explicitly a current variable in this codebase (no speed parameter found), but should be added as its own field (`speed_factor` or similar) the moment pacing control is introduced, defaulting to a fixed value today so existing masters aren't invalidated retroactively |
| Audio normalization/gain change | Partially — see note | The current gain stage (`compute_gain_for_target_rms` in `er003_b1_p9a_audio.py`) is applied **per-episode at assembly time**, against an episode-specific target RMS anchored to that episode's own Preview/Full-Story audio — so the *master* itself should be stored **pre-gain** (raw trimmed TTS output), and gain applied fresh at assembly time regardless of caching. `audio_processing_version` should therefore track only trim/resample policy, not gain, since gain is inherently per-episode and not part of what's cached |
| Trim policy change (e.g. `safety_margin_seconds` 0.08 vs 0.20 vs 0.35, seen varying by segment type in the code) | Yes | `audio_processing_version` differs — the audit shows this value already varies by call site (Key Phrase components use 0.20s, News narration uses 0.35s, generic default 0.08s), so this must be captured, not assumed constant |
| Sample rate / channel layout change (e.g. future move away from 24kHz mono TTS output or 48kHz stereo assembly target) | Yes | `sample_rate`/`channels` differ |
| Level change (B1 wrapper vs A2 wrapper using different voice per §2.4) | Yes (already covered) | `level` + `speaker_voice` differ together |
| Source article's own output directory being regenerated/deleted (the §5 finding) | N/A — this is a **process** risk, not a key-field risk | Mitigated only by *not* storing masters inside any single article's own output directory; the schema's `source_article_id` field must be advisory/audit-only, and the actual master audio store must live in a directory with its own lifecycle, independent of any one article's regeneration |

### 6.2 Practical implication for this codebase specifically

Two concrete fixes fall directly out of the schema, without touching spoken text/voice/tone/spec:
1. Stop treating `er003_output/b1_p9a/A01/narration/` as the de facto shared-asset store — it is article A01's
   own output directory and has already drifted from the nominally-equivalent IRAN01 copy (§5). A dedicated
   master-audio store, addressed only by `master_audio_id`, removes this ambiguity.
2. Add a lookup-before-generate step keyed on the schema above immediately before each of the 5 Category-A
   TTS-origin calls and the 10 Key Phrase English-component calls per topic — the latter is where the §3.2
   cross-level duplicates would be caught automatically.

---

## 7. Constraints honored

No episode structure, B1/A2 spec, Support content, voice choice, tone, pacing, TTS speaker, or spoken text was
proposed to change. No implementation was made — this document is audit + design proposal only, per the task's
explicit instruction to defer implementation pending approval. No paid API calls were made; all figures come from
static source-code reading and existing on-disk audit artifacts from prior production runs.
