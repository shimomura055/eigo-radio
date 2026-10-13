# DIAG_01: Meta Advanced `no way` 単独切り出しの発生段階の特定 (JPY0、既存成果物のみ、LLM呼出なし)
管理ID: FAMILY-X-KP-NO-WAY-MINIMAL-FIX-TRIAL-01 委任_01 / 2026-10-13 / Trial専用 / 採用判断なし
再現可能な根拠: `offline_check_01.json`(`origin_stage`, `case_b_validator_check`, `canonicalization_rule_checks`)、`er064_kp_noway_01_offline.py`。

## 1. 結論(どの段階で起きたか)
`no way` 単独は **単一の段階の不具合ではなく、(i)候補供給が辞書見出し形の最小単位を渡し、(iii)選定Promptが「最小の語句へ抽出」を求め、(iv)後段のどのgateも「構文の一部で単独では不十分」を検知しない**、という3層の組合せで起きた。選定LLM自身は構文全体を認識していた(下記 3-(iii))。

## 2. 事実(段階別)
### (i) 機械抽出
- 候補 `C7 "no way"` は Wiktionary 見出し(`evidence: wiktionary[idiom]`, match_kind=`exact`, `fragment_risk: false`)。`er064_output/kp_integrated_opt_01/round1/shortlists_r1.json` articles.meta_adv.M0/M2.candidates、`runs/meta_adv_M2P0_run1/selector_prompt.txt` L46(`C7`)・L62(`S14`)。M0(Phase2基準)にも同一形で存在 = M2の拡張による新規混入ではない。
- 拡張形は候補に無い: Wiktionary照会snapshot(`er064_output/kp_extraction_selection_opt_01/phase1_a/wiktionary_snapshot_01.json`)で `had no way`/`no way to`/`way to`/`way to know` はいずれも hit=False(`have no way`は照会されていない)。meta_adv M2の shortlist に `no way` を含む長い候補はゼロ(`longer_variants_in_shortlist: []`)。
- 本文: `S14: "...users had no way to know whether they were talking to AI or a person"`(occ=1)。辞書見出し `no way`(「絶対にだめ/ありえない」の意が主)と、本文での用法 `have no way to V`(手段がない)は別用法。M2P3 run2 の選定理由欄にも「『絶対にいやだ』などの用法もあるため、ここでは『手段がない』という意味を文脈から選ぶ必要がある」とある。
### (ii) 包含・cap15・fragment_risk
- 包含: `no way` を含む大きい候補が無いため Tier-H/S の `contains:`/`contained_in:` 注釈は付かない。
- `fragment_risk`(`er064_kp_opt_01_upstream_core.py` L329-352): 「辞書未登録 かつ 先頭が閉クラス語」の複数語だけが対象。`no` は `FRAG_START` に無く、さらに辞書登録済みは常に免除(`fragment_risk("no way", registered=True/False)` = どちらも False を実測)。よってこの規則の守備範囲外。
- cap15(phrase枠)は影響していない(候補は枠内)。
### (iii) 選定LLMの理由(Round1 M2P0 run1/run2、M2P3 run1/run2 の raw_selected_items)
- M2P0 run1: `display_phrase: "no way"`, **`surface_echo: "had no way to know"`**, `normalization_type: idiom_core`, `normalization_note: "本文の語句から慣用表現の核を抽出"`, `listening_difficulty_reason: "「方法がない」という意味を、続く不定詞と合わせて素早く処理する必要があります。"` = **構文全体(`had no way to know`)を認識したうえで、Promptの「学ぶべき最小の単語・句・コロケーションへ抽出」に従い核だけに縮めた**。理由欄自身が「続く不定詞と合わせて」と依存を認めている。
- P0 Prompt 3行目に「その箇所をコピーするのではなく、学ぶべき最小の単語・句・コロケーションへ抽出してください」。P0にある「単独で意味が成立する句を選ぶ」規則は数値の穴埋め句限定の文言(「ソロ旅行を～％とする」)で、構文断片には及ばない。
- 頻度(Round1-2 + Phase2、全139 job中): 裸の `no way` 選定 8件 = Phase2 C0(=M0P0相当)3/3、M2P0 2/2、M2P3 2/2、Phase2 C2 1。拡張した選定は M2P5 run2 の `no way to know` の1件のみ、M2P5 run1 は `no way` 自体を選ばず。
### (iv) Validator・canonicalization・Redundancy
- 選定gate(`validate_min_unit_selection`, `er003_key_words_min_unit.py`): 1〜5語・有限助動詞・括弧・日本語グロス等の形式検査のみ。**display_phraseが本文に逐語であることも、単独で意味が成立するかも検査しない**。`candidate_mismatch_suspected` は telemetry のみで非ブロッキング(`er030_..._source_reference_contract_01.py` L380-400)。
- canonicalization(`er003_key_words_canonicalization.py` L375-413, Rule7): key_phraseがdisplay_phraseと**無変更なら常に通る**。変更するなら source_span(=候補 `no way`)内の連続部分文字列に限る。つまり **canonicalization段で `no way`→`no way to know` に直すことは設計上できない**(実例: Phase2 C0 run1 は canon LLM が `no way to know` へ拡張し **Rule7 で INVALID**、`analysis_r1.md` L149/L194; offline再現 `canonicalization_rule_checks` A)。拡張が通るのは選定段で display_phrase を拡張し canon が無変更にする場合のみ(同 B: PASS)。
- Redundancy QA: LLM判定でありオフラインでは検証不能(`no way` 単独は Redundancy PASS を全runで確認)。

## 3. 案B `have no way to know` は既存Validatorでは通らない(重要)
- `er003_key_words_min_unit.py` L260-261/L339、`er003_key_words_canonicalization.py` L413: 有限助動詞 `is/are/was/were/has/have/had/will/would/can/could/should/may/might/must` を display_phrase / key_phrase に含めると INVALID。**`have` も該当**。
- 実gate経路(FakeClient、LLM呼出0)で実測(`offline_check_01.json` case_b_validator_check):
  | display_phrase | 選定gate | Rule7(無変更) | 本文に逐語 |
  |---|---|---|---|
  | `no way`(現状) | PASS | PASS | あり |
  | `no way to know` | PASS | PASS | あり(S14に連続して存在) |
  | `no way to` | PASS | PASS | あり |
  | `no way to know whether` | PASS | PASS | あり |
  | `have no way to know` | **INVALID(有限助動詞)** | INVALID | なし(本文は `had`) |
  | `had no way to know` | **INVALID(有限助動詞)** | INVALID | あり |
  | `have no way` | **INVALID(有限助動詞)** | INVALID | なし |
  | `no way to know whether they` | INVALID(6語) | INVALID | あり |
- したがって「B」の成立形は **`have`/`had` を含まない `no way to know`(4語)** に限られる。Prompt側で「基本形へ直せ」(P0の既存文言)に従うと `have no way to know` を出してINVALIDになる危険があり、改善案はこれを明示的に避ける必要がある(`design_diff_01.md`)。

## 4. 同型の「構文の一部の切り出し」(一般化の根拠)
| 型 | 例(既存run) | 状況 |
|---|---|---|
| 辞書登録の最小形が構文の核だけを切る | meta_adv `no way`(後続 `to know`) | 今回。裸8件 |
| 候補が断片で、LLMが動詞を補って回復 | coffee_std 候補 `prices up` → display `push prices up` | M0P0/M2P0/M2P3 各3/3、M2P5 5/5。**Rule7は無変更なら通るので拡張可能であることの実例**(同種の拡張は `show up in prices`・`come with costs`・`take care of`・`refuse to stay down` でも観測) |
| 閉クラス語始まり/前置詞句の断片 | meta_std `other end`(原文 `on the other end of the call`) → display `the other end`(M2P0 2/2)/`on the other end`(M2P3 2/2、M2P5 1/2) | 断片が残る(`of the call` が無い) |
| 助動詞/閉クラス始まり(KP-OPT・Round3の既知) | `been behind`、`in the ring` | `round3/ROUND3_REPORT_01.md` §7 |
- 一般化指標は特定語を使わない(`er064_kp_noway_01_analyze.py: classify_construction_fragment`)。ただし偽陽性が多い参考指標(対照で coffee_adv 3, hormuz 2-4, meta_adv 4: `show up in`等の自然な句動詞も拾う)。主指標は評価専用の `no way` 単独率。

## 5. 限界
- 発生段階は既存run(meta_adv M2P0 n=2、M2P3 n=2、M2P5 n=2、Phase2 C0 n=3)の事実に基づく。n小。選定LLMの内部過程は reasoning 本文ではなく出力欄(normalization_note/selection_reason/listening_difficulty_reason)から推定。
- Redundancy QA・canonicalization LLM の挙動はオフラインでは不可(有料run時にのみ観測)。
