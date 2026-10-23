# STRUCTURE_01 判定構造の棚卸し(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_01、API 0、Production変更0)

調査日 2026-10-24、HEAD=022792e31。時刻・年号・通常数値が『文字列 / atom / kind』のどれに、どの関数で変換されるかを、原稿→最終Gateの順に示す。行番号は現行HEAD。

## 1. 経路図(英語ASR、X/Z/A/B/C共通。Primary転写1本の場合)

```
[原稿 script]
  │ ①TTS入力の数字化  er003_v1_n3_01_tts_generate.py:973 tts_safe_number_words_en
  │    two..twelve のみ 算用数字化(`ten thirty`→`10 thirty`、`one`/`thirty`/`forty`は不変)。本文・Preview等は tts_safe_news_en(:1005)、
  │    Key Phrase(KP)英語は tts_safe_kp_en(:1018、数字化なし=語形のまま)。Z=er063_family_z_audio_01.py:806-810、X=er019_family_x_audio_production_runner_01.py:973,1008。
  │    この数字化後テキストが canonical_text(=ASR比較の基準)になる。TTSは数字でも語でも同じ発音。
  ▼
[TTS音声] → [Primary ASR(OpenAI) 転写 / 必要時 Secondary ASR(Azure) 転写 / KPのみ Whisper第3票]
  │   ASRは時刻を 『10:30』『10 30』『ten-thirty』『ten thirty』『1030』など自由な表記で返す
  ▼
[②一次分類] er006_secondary_asr_01.py adapter → er006_preprod_hardening_01_validation.py:1324 classify_asr_match(canon, asr, role)
  │  (a) Tier1 early-exit :1376  → er021_en_asr_semantic_equivalence_production_01.py:635 tier1_numeric_equivalence
  │        両側を _tier1_atoms(:394)で atom列にし、全一致(or 句読点のみのdiff局所吸収)ならPASS。role=5role(FULL_STORY/COMMENT/PREVIEW/TOPIC_INTRO/IN_ONE_LINE)のみ。
  │        PASS時の根拠 basis=TIER1_NUMERIC_EQUIVALENCE(er006_secondary_asr_01.py:776 _equivalence_basis_of)=『承認済み根拠』= 最終Gateをskip(er078_asr_unified_judge_01.py:68-73,526-530)
  │  (b) Tier1不一致なら _classify_asr_match_core(:1112) → normalize_numeric(:376) 9手順。数詞語→数字は :296 _convert_cardinal_words
  │        (2026-10-23 commit b5138e452で『一の位/10-19語 → 十の位/10-19語』の境界で語列を分割=`ten thirty`→`10 30`、`10:30`→`10 30`)。
  │        `:`・空白を除去する despaced(:496)一致(:1140)も NORMALIZED_MATCH で通す(=『10 30』≡『1030』≡『10:30』が文字列として一致)
  ▼
[③統一Judge] er078_asr_unified_judge_01.py unified_judge(:441)
  │  _protected(:355-357) → er078_asr_value_guard_01.py value_guard → _guard_en(:488)  ★最終ANDゲートの値判定(数値の意味比較)
  │    原稿/転写を _en_sequence(:352) で Atom列化: ここで er021._tier1_atoms を再利用(_en_atom_text:339で複合序数・`60 %`のみ前処理)
  │    atom種別 = num / time / literal。SequenceMatcherでatom列をdiff → opcode毎に _compare_pair(:376)(同kind・同値・同形なら EQUAL、値違い DIFF、kind違い UNKNOWN)
  │    『数値2atom隣接 vs time1atom』だけ _clock_pair(:531-541, commit e0eb13ab4)で EQUAL(hour*100+minute一致・分10-59・am/pm無し)
  │  最終Gateの作用: Primary PASS後 **DIFFだけ**がNG_PROTECTED(:541-545)。UNKNOWNは止めない(PASS)。AMBIGUOUSはSecondaryへ降格(:548)。
  │    Primary NGのとき DIFFなら Secondary不呼出で NG_PROTECTED(P1、:583前後)。Secondary転写も同じ vg を通す(:642,688-692)。
  │    basisが承認済み(Tier1等)なら最終Gate自体をskip(:529)→ Tier1が値を等価と判定した対は value_guardを一度も通らない。
  ▼
[④同音救済 er109] er109_xz_scope_01.py:146 decision → er109_asr_orthographic_equivalence_01.py(:276 time=`\d{1,2}:\d{2}`、:305-326 裸hour↔`o'clock`のみ同値、`three`↔`3:00`は非同値)
  │  X/Z run-scope内のみ。既存層がすべて不合格のときだけ最後に評価。DIFF/否定のspan解除に限り最終Gateを緩める(P-06)
  ▼
[⑤HR Lock / 次slot / 再生成]  PASS以外=次slot→最終slot後 HR Lock(er011_human_review_lock_01.py)
[再利用・resume] er078_reuse_value_guard_01.py:32 guard_entry、er019_family_x_validation_inheritance_01.py:256 rejudge_with_current_judge、er006_master_audio_store_01.py:126
  → いずれも保存転写を同じ unified_judge で再判定する(判定ロジックは単一。再実行しても同じ構造を通る)
```

## 2. 数値・時刻・年号の表現変換表(同じ入力が層ごとに別kindになる)

| 入力 | ①TTS数字化後 | ②normalize_numeric(:376) | ③_tier1_atoms(er021:394) | ③_en_sequence(vg) |
|---|---|---|---|---|
| 原稿 `ten thirty` | `10 thirty` | `10 30` | (canon側が`10 thirty`の場合) num10, num30 | num10, num30 |
| 純語形 `ten thirty`(KP等) | 不変 | `10 30` | **number 1030**(`_parse_bare_number_run`:249 → 2つの2桁グループ=年のペア読み 10*100+30) | num 1030 |
| ASR `10:30` | - | `10:30`→`10 30` | **time 1030**(`_TIME_RE`:405) | time 1030 |
| ASR `10 30` | - | `10 30` | num10, num30 | num10, num30 |
| ASR `1030` | - | `1030` | **number 1030** | num 1030 |
| ASR `ten-thirty`/`ten thirty` | - | `10 30` | number 1030(語形) | num 1030 |
| `twenty twenty`/`nineteen ninety` | `two..twelve`以外は不変 | `40` / `19 90`(分割境界は ones→tens/teens のみなので twenty twenty は合算40) | **number 2020 / 1990**(年ペア読み) | num 2020/1990 |
| `two thirty` | `2 thirty` | `2 30` | (純語形)**literal two + num 30**(`_split_into_two_digit_groups`:192が単独一桁語+n>1でNone) | literal, num30 |
| `one thirty` | 不変(oneは数字化しない) | `1 30`(単独`one`は変換しない規則[:313]だが分割後chunkは数字化) | literal one + num 30(実測) | literal, num30 |

→ 同一の発音『ten thirty』が **number 1030(年) / time 1030 / num10+num30(2atom) / literal+num** の4通りに変換され、層間で整合していない。

## 3. 層ごとの責務重複(根本原因の所在)
1. **隣接数詞語の読みを決める箇所が3つ別々に存在**する: (i) er006 `_convert_cardinal_words`(分割して2数字)、(ii) er021 `_parse_bare_number_run`(年ペア読み=桁連結1つの数)、(iii) er021 `_try_spoken_time` + vg `_clock_pair`(am/pm付き or 2atom→time)。(i)(ii)は互いに矛盾(`ten thirty`が 10 30 と 1030)。
2. 最終Gateの作用が非対称: Tier1がPASS判定した対はGate自体をskip、Tier1不一致の対はvalue_guardで**DIFFのみ**が止める。そのため `ten thirty`↔`1030` は Tier1が(年読みで)等価としてGateを通らず PASS、一方 `10 thirty`↔`ten thirty`(数字化canon vs 語形ASR)は Tier1不一致→vgでDIFF→NG。
3. canonical側の形は経路で変わる: 本文/Preview等=数字化後(`10 thirty`)、KP英語=語形のまま(`ten thirty`)、`one thirty`は数字化されず語形。ASR側は常に自由表記。つまり **canon={数字化後, 語形} × ASR={10:30, 10 30, ten thirty, ten-thirty, 1030}** の全組合せを判定する必要がある。

## 4. X/Z差・retry/fallback/regeneration/resume
- X(`er019_family_x_audio_production_runner_01.py`)・Z(`er063_family_z_audio_01.py`)は同じ adapter(`er006_secondary_asr_01.py`)→ 同じ unified_judge → 同じ er021/er078 を使う。経路差は TTS入力生成(本文=`tts_safe_news_en`、KP=`tts_safe_kp_en`)の選択だけで、判定コードは共通1箇所(er021 `_tier1_atoms` / er078 `_guard_en`)。A/B/Cも同じ共有module(27-7: A/B/C自体の開発・是正は対象外、波及は同方向の改善のみ)。
- er109(同音救済)はX/Z run-scope限定で、既存層の後ろ。時刻に対する同音規則は `1030`↔`10:30`(両方を『ten thirty』読みとする)と裸hour↔`o'clock`のみ(実測: `er109_probe_baseline_01.txt`。`ten thirty`↔`1030` は救済されない)。本件の修正はer109に触れない。
- retry/fallback/regeneration/resume: 各attemptは classify_asr_match → unified_judge を毎回再実行(slot毎)。Secondary(Azure)転写も同じ vg を通る。再利用(Store/inheritance/rejudge)も保存転写を同じ judge で再判定するため、判定ロジックを共通module側で直せば全経路(再利用・resume含む)に同時に効く。逆に言うと、**修正後は過去にPASSした保存entryが再判定でNGになり得る**(`ten thirty`↔`1030`型のみ。replay 5,330対ではPASS→NG 0件)。
