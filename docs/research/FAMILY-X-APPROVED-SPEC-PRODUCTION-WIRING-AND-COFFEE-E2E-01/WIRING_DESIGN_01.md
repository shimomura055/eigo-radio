# WIRING_DESIGN_01(FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_01、2026-10-16、実装前設計書・JPY0)

**状態**: 設計のみ。Production code/Prompt/閾値は一切変更していない。**Opus条件A(新しい処理フロー: 既定Style profile・Master Audio Store key・IOL文数の全経路変更)の独立技術レビュー前**。Fable照合→Opusレビュー後に実装へ進む。
**位置づけ**: 全仕様はユーザー承認済み(`APPROVED_FOR_PRODUCTION`)の**実装設計**であり、新仕様ではない。文数方針・Style採否を再びTrialに戻さない(ユーザー指示§4)。新しい編集方針が必要になった箇所は「**STOP候補**」と明記する(本設計では§Cの3点を「STOP候補ではないがFable確認事項」として列挙)。
**設計原則**: 既存の`SP`(profile/M2/M3/M4/M5/固定記録)・`MS`・既存retry/fallback機構を最大限再利用し、新規機構は作らない。共有module(A/B/C/Z が使用)の変更は「**既定引数=現行挙動のバイト同一**」の追加のみ。

---

## §A 既定Style profile

### A-1. 新profile `PROFILE_FX_20261016 = "fx_20261016"`

`SP`へ追加(既存定数・既存profileは**不変**=既存out_dirの固定記録がresume時に現行定義と照合されるため、編集禁止)。

| role | segment/対象 | level | style 定数(新規/再利用) | text sha256(再計算一致) | 長さ | 正本 |
|---|---|---|---|---|---|---|
| `FULL_STORY`(Std/Adv part1-3) | `full_story_part1/2/3` | a2,b1b | **新`PD06_TEXT`**(`std_append_slower_instruction=False`: 逐語+生成後6%減速) | `3a680861e4d9d1bc46ddba4dc1fc91f26c68f9f9c5e5e450a85fcba7fda43c2d` | 177 | `er057_output/pace_trial_02/prompts/prompts_pace_02.md:70-82`(PD6) |
| `SUPPORT_JA`(Std Preview/Comment1-4) | `preview,comment_1..4` | a2 | 既存`R2_TEXT`(`SP:60`) | `625826c1187b6381fe36ff444f1f568fc1f68d639d6a6a8931e728463692252f` | 168 | `er057_output/ja_aoede_style_trial_02/prompts/prompts_R.md` `## R2` |
| `PREVIEW`(Adv Preview) | `preview` | b1b | 既存`E1_TEXT`(`SP:95`) | `8862317ff76693ff519ddfa956260a8cce2d540763333b54096b63161d84f641` | 68 | `er057_tone_trial_tts_gen_01.py` `SPECS["E"]["E1"]` |
| `KP_EXPLANATION_EN`(Adv KP英語解説音声) | `kp{rank}_explanation` | b1b | **新`P7_TEXT`** | `0518000694e31ef7de6602401b7fa9abd3beb45654e95714817930582020b9fc` | 136 | `er080_coffee_kp_pacing_trial_01.py:35` p7(**#96判断済み**) |
| **新** `KP_EN`(KP英語音声) | `kp{rank}_english` | a2,b1b | **新`K2_TEXT`** | `9d905cfe6c040cd001c4e7877327044f540a72bd315776f2c297e0f58f7aea42` | 332 | `er057_tone_trial_kp_ja_gen_01.py:38-39`(B_SPECS["K2"])+`:33`(B_GUARD)。Family Z `_K2`(`er063…:120`)と一致 |
| **新** `KP_JA_MEANING`(Std KP日本語意味) | `kp{rank}_japanese_meaning` | a2 | **新`P8_KP_JA_TEXT`** | `b12c8721eab8434b78d129c93491c0a826f229f4528e024d58de960e1ad191e7` | 93 | `er057_std_kp_ja_style_trial_02.py:25` P8 |

- **P8名称衝突の分離**: 既存`P8_TEXT`(`SP:48`、402文字、Full Story旧候補・Aoede Trial-03)は**変更せず**(`coffee_p8`/`coffee_final_v5`の固定記録が参照)。KP用は**別定数名`P8_KP_JA_TEXT`・別role名`KP_JA_MEANING`**。`_verify_constants`(`SP:196`)へ4定数(PD06/P7/K2/P8_KP)を追加=import時にsha/長さ不一致で即STOP。さらに**ソース突合test**(Trial正本ファイルをAST/正規表現で読み、定数と逐語比較)を置き、定数が正本から離れないことを固定。
- 新role追加に伴う構造拡張(**N3**): KPは`segments`でなく`key_phrases[rank].{english,japanese_meaning,explanation}`。`ROLE_SEGMENTS`には入れず、新テーブル`ROLE_KP_RESULT_KEY = {KP_EN:"english", KP_JA_MEANING:"japanese_meaning", KP_EXPLANATION_EN:"explanation"}`を追加し、`_gate_targets`(`SP:463`)がKP role全般を`key_phrases`から走査するよう一般化(現行はKP_EXPLANATION_ENのみ個別分岐)。`ROLE_LEVELS`へ`KP_EN:(a2,b1b)`、`KP_JA_MEANING:(a2,)`。`_PROFILES_RECORDING_LEVELS`へ新profileを追加(記録にlevelsを含める)。

### A-2. `DEFAULT_NEW_RUN_PROFILE`切替

`SP:110`を`PROFILE_FX_20261016`へ。**意味**: 新規out_dir・CLI未指定・`tts_backend=speech_metadata_flash_lite`のとき、`resolve_run_profile`(`SP:323`)が新profileを選び固定記録を作る。既存の安全装置はそのまま: (1)固定記録があれば記録優先(CLI食い違いは課金前STOP)、(2)既存run state(Review Lock/人間承認/TTS結果)があるのに記録が無いout_dirは課金前STOP(`--style-profile default`でresume)、(3)legacy backendでは従来どおりdefault(M5、新profileは適用不可)。`source`文字列`"default_new_run_n01"`(`SP:~362`)は`f"default_new_run_{DEFAULT_NEW_RUN_PROFILE}"`相当へ(既存testの期待値更新が必要)。

**CLI指定忘れでも承認済みStyleが自動適用**される条件: 新規out_dir+`--tts-backend speech_metadata_flash_lite`(E2Eコマンドに必須。legacyのままではtts stageが`assert_production_tts_backend`[`AR:2263`]で課金前STOP=fail-closed)。N7: legacy backendで`plan/scaffold`を回すとprofile記録が作られない(textのみ・TTS前にSTOP)ため実害なしだが、runnerが`source=default_no_record_legacy_backend`のとき目立つ`[WARN]`を1行出す(任意・非機能)。

### A-3. 旧profileの扱い

| profile | 扱い |
|---|---|
| `default` | 不変。既存run resume用 |
| `coffee_p8` / `coffee_final_v5` / `n01` / `coffee_n01_r2_p3` / `coffee_n01_r2_p3_e1` | **不変・残置**(既存out_dirの固定記録検証に必要)。定義直前に`# 非推奨(2026-10-16以降、新規runの既定はfx_20261016)`のコメントのみ追記。選択肢(`choices`)にも残す |
| `fx_20261016` | 新既定 |

`migrate_record`(`SP:549`)は「移行先が移行元の上位集合かつ既存roleのshaが一致」でのみ許可。`n01`/`coffee_n01_r2_p3_e1`→`fx_20261016`は**FULL_STORY(N01→PD06)とP3→P7が変わるため不可**(正しい挙動。既存out_dirは移行せず新out_dirで作り直す)。

### A-4. Family Z非影響の保証

- `er063_family_z_audio_01.py`は`er019_family_x_style_profile_01`をimportしない(Grep: 参照は`:139`のコメントのみ)。Style定数は自前保持(`_K2/_M2/_N01/_R2/_E1`と`_STYLE_SHA256`)。
- Zが使うXコード: `x_runner.generate_key_phrase_explanation_en_verified`(`er063…:718`、`AR:727`)のみ。**シグネチャ・挙動を変えない**。
- Zが使う共有: `LR`(`er063…:628,795`)、`MS`は未使用(Z grep: `store.`なし)。→ `LR`の変更は§Cのとおり**IN_ONE_LINEセグメントの文数不変検査**のみで、Zは`in_one_line`セグメントを持たない(`er063…:1285`「In One Lineなし」)。
- test: (1)`er063_family_z_audio_01.py`のASTに`er019_family_x_style_profile_01`のimportが無いこと、(2)`FAMILY_Z_ROLE_STYLE`の各text shaが現行と一致(既存`er063_family_z_audio_01_test_01.py`/`_n01_test_01.py`を実行して従来PASSを維持)、(3)`generate_key_phrase_explanation_en_verified`のシグネチャ固定test。
- Family A/B/C: `generate_key_phrase_component_verified`(`er003_v1_repro01_main_generate.py:779`)と`ensure_key_phrase_english_component`(`SN:246`)は**追加引数のみ・既定=現行**(§B)。golden test(既存KP key・MINIMAL style・戻り値keyが変わらない)で固定。

### A-5. CLI未指定時の自動適用test案

1. `resolve_run_profile(tmp_new_dir, None, write=True, tts_backend="speech_metadata_flash_lite")`→`("fx_20261016", ...)`、`audit/style_profile.json`の`roles`が6role・sha一致、`verify_record`通過。
2. 上記を2回目呼出(resume)→`source="record"`、CLI食い違い(`--style-profile n01`)→`StyleProfileStop`。
3. tmp_dirに`audit/review_lock_state.json`があり記録なし・CLI未指定→課金前STOP(`--style-profile default`で通る)。
4. `tts_backend="structured_separation"`+CLI未指定→`default_no_record_legacy_backend`(新profile不適用)。
5. runner結合(mock): `generate_family_x_b1_segments(style_profile="fx_20261016")`/`_a2_`を、TTS関数をmockして呼び、`style_prefix_override`が各segmentのprofile textで始まること(Preview=E1、Full Story=PD06、Std Preview/Comment=R2、KP英語=K2、KP日本語意味=P8_KP、KP解説=P7)、`style_profile`記録が全KP entryに付くこと。

---

## §B Master Audio Store

### B-1. 現状の確認(再確認、`MS`/`SN`)

- `EQUALITY_FIELDS`(`MS:35-38`)= language/level/speaker_voice/tts_model_id/style_instruction_id/style_instruction_version/instruction_path/canonical_text_hash/audio_processing_version/sample_rate/channels。**Prompt shaは含まない**。`master_audio_id = sha256(json(EQUALITY_FIELDS))[:24]`(`MS:73-75`)。
- Storeを使うのはshell固定音声(`SN:231,241`)とKP英語(`SN:266`)のみ(`get_or_generate`呼出元の全Grep)。Full Story/Preview/Comment/KP日本語意味/KP解説は**run単位でStore不使用**=旧Style音声の誤再利用リスクはStoreではなく`audit/style_profile.json`固定記録(M2)+`_generate_or_reuse*`のcanonical_text/`style_version`ガードで管理されている。
- 現行KP英語key: `style_instruction_id="key_phrase_english_component"`、`version=KEY_PHRASE_TRIM_POLICY_VERSION="v2_margin030"`(`SN:58,263-264`)。これはStyleでなくtrim policyを表すだけで、style(MINIMAL)を区別しない。

### B-2. 割当案(K2)

| 項目 | 値 |
|---|---|
| `style_instruction_id` | **`key_phrase_english_component_k2`**(旧`key_phrase_english_component`と別) |
| `style_instruction_version` | **`v2_margin030+k2.9d905cfe6c04`**(= `KEY_PHRASE_TRIM_POLICY_VERSION` + `+k2.` + K2 sha256先頭12桁) |
| `instruction_path` | `primary`(不変) |
| その他field | 不変(language=en, voice=Aoede, tts_model_id=flash-lite, level=None, sample_rate=24000) |

- **判定ロジック**: key構成自体にshaを含められないため、`version`文字列にsha先頭を埋め込む。→ (1)K2の文言が1文字でも変われば`version`が変わり新`master_audio_id`=自動的に旧音声を再利用しない。(2)旧`key_phrase_english_component`系entry(MINIMAL style)とはidが異なり**ヒットしない**=旧Style音声の誤再利用は構造的に起きない。Std/Adv間はlevel=Noneで従来どおりK2音声を共用。
- **K2 fallback識別(N5)**: K2 primary(2回)失敗→既存ENGLISH_LOCK(2回)で通った音声は`fallback_used=True`だが、Storeの`qa_evidence`(`MS:177`)は`fallback_used`を保存せず、reuse時に復元できない=「K2」として別記事へ再利用され、M3が検知できない。**対策案(推奨)**: `MS:177`の`qa_evidence`へ`"fallback_used": r.get("fallback_used")`を**追加のみ**(1行、additive)。reuse時は`result.update(qa_evidence)`(`MS:153`)で復元される。A/B/C新規entryにも同キーが付くが、AR/ASRの既存consumerは`fallback_used`をKP英語entryから読んでおらず影響なし(要test)。**代替**(共有module不変): fallback結果は`style_instruction_id`をさらに`..._k2_fallback`に切替えて保存する(生成後にしか分からず、get_or_generateの構造上不可)=非推奨。Opus確認事項。
- **M3/M4の扱い**: KP_ENは(a)`style_profile.style_base_sha256==K2 sha`、(b)`master_audio_key.style_instruction_version`が`+k2.<sha12>`を含む、を必須とし、(c)`fallback_used=True`は**WARNING(非ブロッキング、gate出力`warnings`と最終報告に列挙)**。理由: ENGLISH_LOCK fallbackは2026-09-01ユーザー決定の4回構成(承認済み安全機構)の一部で、BLOCK化は新しいBlocking QA条件(仕様追加)に当たる。BLOCK化したい場合はユーザー判断事項(本設計の推奨は非ブロッキング)。

### B-3. 追加実装(最小)

1. `er003_v1_repro01_main_generate.py:779 generate_key_phrase_component_verified`に**`primary_style_override: str | None = None`**を追加。`None`=現行(`KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`)。指定時は1段目(最大`KEY_PHRASE_MINIMAL_MAX_ATTEMPTS`=2)のstyleのみ差替え、2段目(ENGLISH_LOCK×2)・ASR/disfluency/margin/cascadeは不変。**Family Zの`_kp_en_two_stage`(`er063…:691-728`)と同一構成**。
2. `SN`へ`ensure_key_phrase_english_component_styled(used_form_tts_safe, out_path, *, style_text, style_id, style_sha256, tts_backend)`を新設(既存`ensure_key_phrase_english_component`は無変更)。key=B-2、generate_fn=1.を呼ぶ。
3. `AR`の`_generate_key_phrase_segments_b1`(`AR:1068`)/`_a2`(`AR:1385`)で、profileに`KP_EN`overrideがある場合のみ2.を、無い場合(`default`等)は従来関数を呼ぶ(分岐1か所)。

### B-4. regression test案

1. 旧key不変(golden): `ensure_key_phrase_english_component`が組むkeyの`master_audio_id`が現行実manifestのKP entry(`manifest.json`内`key_phrase_english_component`系)と一致すること(A/B/C不変)。
2. 新keyは旧keyと異なる`master_audio_id`。K2 sha変更(monkeypatch)で`version`/`master_audio_id`が変わる。
3. mock `generate_fn`で: 同一text・同一K2→2回目`reused=True`(TTS 0 call)、旧style由来entryがあってもヒットしない(`reuse_telemetry`に`reused`なし)。
4. `qa_evidence.fallback_used`の保存・reuse時復元(additive、既存entryは欠落でも例外なし)。
5. `primary_style_override=None`の呼出が現行とバイト同一(`style_prefix_override`引数列・attempt数)。
6. M3: KP_ENでversionにk2 sha無し/`style_profile`欠落→violation、`fallback_used`→warning(非ブロッキング)。

---

## §C In One Line(基本2文・必要時のみ3文)

### C-1. 新Prompt文面案(`ADV:551 FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE`の全面置換、全文)

置換前の要点(撤去対象): `Write ONE short, natural sentence`、`- Exactly one sentence.`(`:558`)、`- Do not pack in multiple separate points; focus on the single most important point or twist`、`(Trial-only guidance, not a strict rule): aim for one main clause with at most one subordinate clause, roughly 12-18 words.`(`:564-567`)、`Output only the sentence itself`。
**保持必須**: `- Do not add any new fact, conclusion, or lesson that is not already stated in the article below.\n`(=`_M1_REQ_ANCHOR`、`ADV:589`。M1(a)入力欄は`.replace`でこの行の直後に要件行を挿入するため、**一字一句変えない**。`assert TEMPLATE_M1 != TEMPLATE`も維持)。`{article_text}`差込と`[Article]`ブロックも維持。

```
Below is a finished English news feature article (already translated from Japanese, no section headings). Write the closing "In one line" summary of the story: normally TWO short, natural sentences, in a way a listener can understand by hearing them just once.

Requirements:
- Normally exactly two sentences. Sentence 1 states the core of the story (what happened, or the surprising point). Sentence 2 gives its meaning or implication for the listener and closes the summary naturally, using only what the article already says.
- Use a third sentence only when it is needed: only when the article states an important condition, limit, or hedge (for example "may", "not always", "at least") or a second essential point that cannot be added to sentence 1 or 2 without making it hard to follow by listening once. Never write more than three sentences, and never add a third sentence just to add detail.
- Each sentence must be understandable on a single listen: one main idea per sentence, short and natural.
- Do not add any new fact, conclusion, or lesson that is not already stated in the article below.

As a rough guide only (not a strict rule): aim for one main clause with at most one subordinate clause in each sentence, roughly 12-22 words per sentence.

Output only the sentences themselves, one after another on a single line, nothing else (no quotation marks, no numbering, no label like "In one line:", no Markdown heading markup).

[Article]
{article_text}
```

**設計根拠(新編集方針を追加していない確認)**:
- 「1文目=記事の核心、2文目=意味・示唆で自然に締める」「必要なら3文」は2026-10-12のユーザー決定と、2026-10-16 09:00/正式指示§2・§4の逐語(`IN_ONE_LINE_REWRITE_01.md`冒頭、CS:1203小節)。本文面はそれを文章化しただけ。
- 「意味・示唆」が既存の「新しい結論・教訓を追加しない」と矛盾しないよう、2文目に「**using only what the article already says**」を付けた(承認済みTrial原稿のS2は記事段落9の事実=hedge+他費用で構成されている、`IN_ONE_LINE_REWRITE_01.md`事実対応表)。
- **「12-18 words」の判断**: **撤去**(1文全体の目安であり、2文化すると1文あたり6〜9語に圧縮して矛盾するため)。同位置に**1文あたり「12-22 words」の目安**を置く。根拠: 承認Trial v3の実測=Std 16/15語、Adv 19/21語(`IN_ONE_LINE_REWRITE_01.md`難易度チェック表)。「Trial-only guidance」という本番に不適切なラベルも撤去し、強い規則でない旨(`not a strict rule`)は保持。Validatorの閾値ではない(Promptの目安のみ)。
- **3文にする基準(具体)**: (a)記事が重要な条件・限定・hedge(例: may / not always / at least)を述べていて、それを1〜2文目に入れると聞き取りが困難になる場合、または(b)記事の核心が2つあり1文に押し込めない場合に限る。上限3文。「詳細を足すためだけの3文目」は禁止。→ 数値の閾値ではなく**理由条件**であり、新しい編集方針ではなく承認済み「必要な場合のみ3文」の運用定義。**この定義が「新しい編集方針」に当たるとFable/Opusが判断する場合はここで設計を止めSTOP**(私の判断では該当しない)。
- 内容品質要件(指示§4「要点・意味・示唆を自然に伝える」): 上記Requirements 1〜3で担保(核心→意味・示唆、聞き取り1回、1文1論点)。

### C-2. Standard継承(`STD:506`)

Stdの`## In one line`はAdvanced英文から**LLMが再執筆**する(コピーではない。`STD:522`は「Markdown構造を保て」のみで文数指示なし=FXWA既知#9)。**1文追加(提案)**: `STD:522`の`Keep the same Markdown structure (...); do not add or remove sections.`の直後に次の1文を加える:

> `Keep the "In one line" section at the same number of sentences as in the article below (normally two), each as a short A2 sentence; do not merge it into one sentence.`

これはAdv IOLの文数をStdへ継承させる**承認済み仕様の運搬**であり新編集方針ではない(Fable確認事項。Std Prompt変更のためOpus確認対象)。`er019_family_x_new_structure_wiring_01_test_01.py:307`(`STANDARD_A2_NEW_VOCAB_BLOCK`がPromptに含まれること)等の既存testは影響なし。

### C-3. 適用経路一覧

| 経路 | 使用Prompt/関数 | 本設計での扱い |
|---|---|---|
| Adv初回 | `EFAM:327 _advanced_in_one_line`→`ADV:742 generate_family_x_in_one_line`→`build_family_x_in_one_line_prompt`(M1: ja_text+Ledger常時) | 新template(C-1) |
| Adv段落retry再生成 | `EFAM:~371`(`_advanced_paragraph_retry_regen`内で同関数を再呼出) | 同上(同一関数経由=自動) |
| `--regenerate-stage advanced` | `ER`→`efam.run_writer_stage(only=advanced)` | 同上 |
| Std初回/段落retry/`--regenerate-stage standard` | `STD.generate_family_x_standard_a2_no_heading`(`build_family_x_no_heading_prompt`) | C-2の1文追加 |
| `--regenerate-stage writer`後 | JA再生成→Adv/Stdは別stage実行が必要(U-1) | 運用注記のみ(自動化しない) |
| Local Rewrite(TTS ASR NG回復) | `LR:158`ラベル+候補生成(元文verbatim+spanのみ置換、`LR:367-392`) | C-4 |
| TTS resume | IOL textを再生成しない(`parts.json`のtextを使用) | 影響なし |
| Comment4 | `AP:201-203,234-237`(「1文とは限りません」) | **変更不要**(FXWA §14-2 #3。2文化後も整合) |

### C-4. Local Rewrite(`LR:158`)

- 現状: 候補は「segment全文をverbatim+span置換」と強制され、局所性はtoken比較(`check_locality` `LR:~495-`)。**【新規N8】tokenizeは`normalize_text`でpunctuationを落とす**(`er006_preprod_hardening_01_validation.py:451-452`)ため、句点→読点等の**句読点のみの変更で文を結合する候補**は局所性検査をすり抜けうる(=2文IOLが1文に潰れる経路)。
- **案L1(推奨)**: `LR`の候補採否(`check_locality`の隣、`criterion6/7`と同層)に**`sentence_count_unchanged`**を追加。`resolve_narrative_role(segment_id)=="IN_ONE_LINE"`のときだけ、元text/候補textの文数(§C-5の関数)が一致しない候補を不採用。ラベル`LR:158`は不変。→ 共有moduleだが**厳格化のみ**(文数を変える候補を落とすだけ。A/B/Cの1文IOLは1文のまま保たれるため既存挙動は事実上不変、Zは`in_one_line`を持たない)。
- **案L2**: ラベルを`In One Line (the closing summary of the episode; keep its number of sentences)`へ(中立表現)。A/B/C/Z全員の同role Promptが変わる。
- 推奨=L1(Promptを変えず検査で担保)。ユーザー指示§4の「Local Rewriteにも適用」はL1で満たす(文数保持test付き)。

### C-5. 文数Validator案

- 関数: `count_in_one_line_sentences(text:str)->int`(Family X専用の純関数。置き場=`EFAM`)。分割規則: `(?<=[.!?])["')\]]*\s+(?=["'(\[]?[A-Z0-9])`、略語保護(`U.S.`/`Mr.`/`Mrs.`/`Dr.`/`Inc.`/`vs.`/`e.g.`/`i.e.`/`No.`/`St.`)、小数点保護。
- 運用: **非ブロッキング・記録+警告のみ**(既存QA構造[RFが非ブロッキング、structure splitのみBlocking]に合わせる)。`writer_run_summary.json`の`advanced.in_one_line`/`standard.in_one_line`に `{sentence_count, spec_ok: count in {2,3}, model_id_actual, response_id, prompt_sha256, usage}` を保存(**N2の解消**: 現行は`iol_result`を破棄、`EFAM:373-374`)。`spec_ok=false`は`[WARN][IOL-SPEC]`を標準出力へ。2〜3は仕様そのもの(「基本2文、必要な場合のみ3文」)であり新閾値ではない。
- 自動再生成(IOLのみ1回)は**新retry機構**となるため本設計では**採用しない**(Fable/Opus判断事項、非推奨)。Coffee E2E受入では`spec_ok=false`をSTOP条件として扱う(COFFEE_E2E_PLAN)。
- test案: (1)template: `Exactly one sentence`/`12-18 words`/`Trial-only`が含まれない・`_M1_REQ_ANCHOR`を含む・M1変種が従来どおり組み立てられる。(2)カウンタ: 2文/3文/1文/略語(U.S.)/引用符/数値(3.5)/改行。(3)evidenceキー(fake clientで`_run_writer_stage_once`、API 0)。(4)Std prompt文(C-2)包含。(5)`LR`文数検査: 句読点のみで2文→1文にする候補が不採用。(6)`parts.json`の`in_one_line`が複数文でも`split_family_x_article_text_v2`がOK(`in_one_line`は`(.+)` DOTALL、`scaffold_generate.py:211-212`)。

---

## §D retry / fallback / regeneration / resume 整合

| 経路 | Style/profileの解決 | 同一性の確認方法 |
|---|---|---|
| 初回 | `resolve_run_profile`→固定記録(`audit/style_profile.json`)→`_role_style(role)`(`resolve_role_style`)をsegment生成ごとに1回評価 | A-5 test 5(mock TTSでstyleを捕捉) |
| TTS内retry(同一関数内attempt) | 同じclosureの`style_prefix_override`を各attemptに渡す(`generate_*_verified*`) | mockで3attempt分のstyle引数が同一 |
| fallback `minimal_fallback`/Std fallback/`local_rewrite_recovery` | 該当segmentはM3でBLOCK(人間承認なし)=黙って別Styleで完成しない | 既存M3 test+KP role追加分 |
| KP英語 K2→ENGLISH_LOCK | 承認済み4回構成。`fallback_used`記録→M3**warning**(B-2) | B-4 test 6 |
| `--only-segments`再生成 | profile記録から再解決。非選択segmentは検証済みentryを引継ぎ(`validation_inheritance`、証拠なしはBLOCK) | 既存test+新role |
| resume(同一out_dir) | 固定記録が正。CLI不一致はSTOP。記録無し+既存run stateはSTOP | A-5 test 2,3 |
| `--scaffold-only kp`(KP text再生成) | textのみ(Style無関係)。KP音声は次のtts stageで同profileで生成 | 結合test |
| text系 `--regenerate-stage storyline_b3/writer/advanced/standard` | profile無関係。routing/Promptは初回と同一関数(FXWA PC§2経路表)。IOLは§C-3 | §C test、`runtime_evidence`のsha比較 |
| KP音声のStore reuse | key(B-2)が同一のときのみ。旧Style由来はヒットしない | B-4 test 2,3 |
| 旧out_dir(`n01`記録等) | 記録に従いresume=旧Styleのまま完走(新profileへ黙って切替わらない) | A-5 test 2 |

M4(evidence)判定にKP role追加: `evaluate_segment_evidence`をKP roleでも呼べるよう、base sha(`style_profile.style_base_sha256`)+(K2のみ)Store key versionのsha12照合。日本語KP_JA_MEANINGはSUPPORT_JAと同じく**base shaのみ**(日本語は発音hint追記が無い、`SP:~433`)。最終送信styleはraw_usage_log/attemptsのinstruction_textで実測(従来どおり)。

---

## §E Hook廃止

- **コード**: Production経路にHook stageは存在しない(`ER`/`EFAM`/`W1`/`ADV`/`STD`へ`hook`をGrep=0件、`AR`は無関係な「生成完了hook」コメントのみ)。→ **撤去対象コード無し**。
- **SSOT(追記のみ、本委任で実施)**: `OPEN_ITEMS.md` OPEN-176(`:357`)に行内追記「【2026-10-16ユーザー判断】廃止(R2 Title表示は維持)。本管理IDで反映」(closeは実装完了後=Fable判断)。`DECISION_LOG.md`の`NEWS-HOOK-POLICY-DECISION-01`エントリ(`:9418`ほか`:490,9400,9414`)は**履歴のまま**保持し、委任_01エントリで「廃止(2026-10-16)」へのリンクを追記。`CURRENT_SPEC.md:1203`小節末尾へ追補。`USER_DECISION_REGISTER_01.md` #98=判断済み。
- **維持**: R2 Title正式表示(`AR:141 derive_japanese_title`、試聴ページの表題)。Luna Hook生成・Side output保存・比較観測蓄積は行わない(既に行っていない)。
- **Dangling検査**: Hook言及が残る箇所=SSOTの履歴記述のみ(コード0)。OPEN-176は「蓄積項目」が観測不能になるが、廃止決定により蓄積の必要が無くなる。

---

## §F test計画

承認済み仕様のため**既定ON**(DefaultOff隔離test不要)。ただし「新しい経路が既存の他Family・既存out_dirに影響しない」ことを回帰で固定する。

| 区分 | test | 件数見込み |
|---|---|---|
| unit | profile定数(sha/長さ/WPM語なし/ソース突合)、role・level、`resolve_role_style`、既定解決(A-5 1-4)、record verify/migrate不可、P8混同防止(`P8_TEXT!=P8_KP_JA_TEXT`、role名分離) | 約25 |
| unit | M3/M4 KP拡張(violation/warning)、`_gate_targets`一般化 | 約12 |
| unit | Store(B-4 1-6)、`primary_style_override=None`のバイト同一 | 約10 |
| unit | IOL(C-5 1-6)、Std prompt文、LR文数検査 | 約15 |
| regression | 既存: `er019_family_x_style_profile_01_test_01.py`/`_n01_test_01.py`/`_migration_01_test_01.py`(既定値変更に伴う期待値更新のみ)、`er006_master_audio_store_01_test.py`、`er019_family_x_new_structure_wiring_01_test_01.py`、`er012_e_family_entertainment_two_level_runner_test_01.py`、`er063_family_z_audio_01_test_01.py`/`_n01_test_01.py`、AUW中核(`er078_*`、`er058_*`)、`er053_c2_old_checker_removal_test_01.py` | 既存全PASSを確認 |
| integration(API 0) | `--stage plan`をseed記事で実行(`style_profile_plan`にfx profile)、`generate_family_x_b1/a2_segments`をmock TTSで実行しstyle捕捉(A-5 5)、`_run_writer_stage_once`をfake clientで実行しevidence確認 | 約6 |
| 有料evidence | 実装後のsmoke(任意・少額): K2/P8_KP/P7の各1clip生成+M4 pass(推定JPY1以下)。**本番E2E(Coffee)が実走evidenceを兼ねる**ため必須ではない | 任意 |

---

## §G 影響範囲・リスク・撤去対象(Charter原則8)

**影響範囲**: Family Xの全新規run(既定profile、IOL、KP音声)。他Family: 共有関数への追加引数/1行追加のみ(既定=現行)。既存out_dirのresume: 固定記録に従い不変。

**リスクと緩和**
1. 新KP Style(K2)の通過率低下→ENGLISH_LOCK fallback増/コスト増: 4回構成は不変、`fallback_used`を記録しwarning列挙。COFFEE_E2E_PLANで観測。
2. 共有module変更(`repro01`/`SN`/`MS`/`LR`): 既定引数で現行バイト同一+golden test。Opus確認。
3. IOLが2〜3文になりTTS時間/ASR量が増える(微増)。Comment4は文数非依存。
4. Std Prompt1文追加でStd出力が微変動: Std verbatimsha testは無い(確認済み: Std promptのsha固定testなし)。Opus確認。
5. PD06にはN01の"a little slower"相当が無く、Stdの遅さは6%減速のみ。Advの速度変化は試聴確認項目(FXWA §14-4)。
6. P8名称衝突: 定数名・role名・testで分離。
7. `DEFAULT_NEW_RUN_PROFILE`切替に伴い既存testの期待値(`default_new_run_n01`等)更新が必要。

**撤去する旧ルール**: (a)`ADV:558` `- Exactly one sentence.`、`:559`の"focus on the single most important point"(IOL1文前提)、`:564-567`の"Trial-only guidance…12-18 words"。(b)SP/AR内の`M3`違反名`ADV_STYLE_PREFIX_NOT_P8_PREFIXED`は意味が一般的なので**名称のみ**`..._NOT_PROFILE_PREFIXED`へ(任意、testを同時更新)。(c)`default_new_run_n01`の固定文字列。
**残置(今回撤去しない)**: N01/P3等の旧profile定数と`coffee_*`profile(既存out_dirのresume検証に必要)、`open243_m1_enabled`死コード(`ADV`、別委任)、`ja_writer_o_r1_r2`孤立コード(別委任)。
**撤去後Grep(実装時)**: `Exactly one sentence`、`12-18 words`、`Trial-only guidance`、`default_new_run_n01`、`one-line summary`(LR残置は意図的)、AR内で`_role_style_ja()`がKP japanese_meaningに渡されている箇所(P8_KP化後は0件であること)。

**STOP候補**: なし。Fable確認事項3点: (1)3文基準の文言(§C-1)が新編集方針に当たらないか、(2)Std Prompt1文追加(§C-2)、(3)K2 fallbackをwarning(非ブロッキング)とする点(§B-2)。いずれも「ユーザー承認済み仕様の運搬/実装」であり、ユーザー判断事項ではないと判断。

---

## §H 変更ファイル一覧とおおよその行数

| ファイル | 変更内容 | 増減(行) |
|---|---|---|
| `er019_family_x_style_profile_01.py` | 定数4+検証、role2、`ROLE_KP_RESULT_KEY`、新profile、既定切替、M3/M4のKP一般化、source文字列、旧profile非推奨コメント | +120 / -10 |
| `er019_family_x_audio_production_runner_01.py` | KP音声の3経路(K2/P8_KP/P7)でprofile解決、KP entryへ`style_profile`記録、legacy backend警告1行 | +70 / -10 |
| `er006_audio_cost_pilot_02_shared_narration.py` | `ensure_key_phrase_english_component_styled`新設 | +30 |
| `er003_v1_repro01_main_generate.py` | `generate_key_phrase_component_verified`に`primary_style_override`(既定None) | +8 |
| `er006_master_audio_store_01.py` | `qa_evidence`へ`fallback_used`(additive) | +1 |
| `er003_v1_n3_01_advanced_adaptation_generate.py` | IOL template置換 | +14 / -16 |
| `er003_v1_n3_01_standard_a2_generate.py` | Std prompt 1文追加 | +2 |
| `er012_e_family_entertainment_two_level_runner_01.py` | `count_in_one_line_sentences`、IOL/英訳/Stdのevidence(model/response_id/prompt_sha256/sentence_count)、`[WARN][IOL-SPEC]` | +60 |
| `er020_tts_retry_local_rewrite_01.py` | IN_ONE_LINE文数不変検査(案L1) | +15 |
| テスト(新規/更新) | §F | +約600 |
| SSOT | CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REGISTER/REPORT_LEDGER | 追記のみ |

合計: production約+320/-35行、test約+600行。実装は並列化可能(独立トラック: ①profile+M3/M4、②Store+KP K2経路、③IOL+evidence+LR)。①②は`AR`の同一関数を触るため直列、③は独立。

---

## §I Opus条件Aレビュー依頼事項(Fable向け)

1. 既定profile切替(§A)と旧out_dirのresume安全性(M2/M3/固定記録の網羅性)。
2. Store key設計(§B-2: `id`分離+`version`にsha12)と`qa_evidence.fallback_used`のadditive追加。K2 fallbackをwarningとする判断。
3. 共有moduleの追加引数(`primary_style_override`)が A/B/C を変えないこと。
4. IOL文面(§C-1)、「12-22 words」目安、3文基準、Std 1文追加(§C-2)、LR L1(§C-4)、非ブロッキングValidator(§C-5)。
5. M3/M4のKP拡張(N3)で、新roleがGateの検査対象から漏れないこと。
