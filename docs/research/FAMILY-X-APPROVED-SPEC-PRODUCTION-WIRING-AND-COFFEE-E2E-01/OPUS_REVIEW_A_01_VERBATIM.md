# FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 Opus独立レビュー所見(条件A)

読み取り専用で実施した。編集・テスト実行・API呼び出しはしていない。設計書(WIRING_DESIGN_01.md全文、SPEC_WIRING_MATRIX_01 X28-X30)をコード現物と突き合わせた。照合したのは SP(style_profile)L40-617、AR(audio runner)L440-720 / 811-1120 / 1180-1405 / 1616-1638 / 2219-2250 / 2486-2644、MS L25-205、SN L40-290、repro01 L677-848、ADV L535-614、STD L486-565、LR L124-170 / 362-752、er063 L110-219 / 691-729、ユーザー原文(delegation_log …_USER.md L60-169)、CURRENT_SPEC L1203-1251。

---

### FXPW-R-01 [高] K2 fallback音声が「K2」keyでStoreに保存される(Prompt SHAと実音声が食い違う)
- **該当箇所**: 設計§B-2「K2 fallback識別(N5)」、repro01:824-832、MS:166-182
- **問題**:
  - 確認した事実: `generate_key_phrase_component_verified` の2段目は `KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION`(=旧 MINIMAL prefix + lock suffix)である。K2を primary に差し替えても、fallback で通った音声は K2 ではなく旧MINIMAL系のStyleで作られる。
  - 一方 Store は status=OK なら、K2 の sha12 を含む key(`…_k2` / `v2_margin030+k2.<sha12>`)で登録する。
  - その結果、旧Style系の音声が「K2」として別記事へ再利用される。これはユーザー原文「Role・Style ID・version・Prompt SHAを整合させる」(L117)と構造的に食い違う。
  - 設計案の `qa_evidence.fallback_used` 追加と M3 warning は「事後に分かる」だけで、誤再利用そのものは防がない。
  - 設計書は代替案を「生成後にしか分からず構造上不可」として退けているが、これは誤り。
- **推奨**: 既存の EQUALITY_FIELDS にある `instruction_path` を使い、key を2つに分ける。
  - `ensure_key_phrase_english_component_styled` の中で次の2段にする。
    1. key A(`instruction_path="primary"`)で `get_or_generate`。generate_fn は K2 primary の2回のみ。
    2. 1が非OKなら key B(`instruction_path="english_lock_fallback"`、version に ENGLISH_LOCK 文言の sha12)で `get_or_generate`。generate_fn は ENGLISH_LOCK の2回。
  - MS は無変更で済む。A/B/C の key も不変。
  - Family Z の `_kp_en_two_stage` と同じ構成で strict を直接呼べば、repro01 への `primary_style_override` 追加も不要になる。その場合、review_lock の会計(`@guarded_generate` 1回・slot_offset 0/2・total 4)は外側の wrapper で維持する。
  - 最低限の代替: 設計案のまま進めるなら、`fallback_used=True` の entry は styled wrapper が事前に manifest を見て再利用しない。ただしこれは MS の内部への依存になり、非推奨。
- **ユーザー判断**: No。承認済み4回構成の中での実装方式の選択である。ただし「K2が通らないとき旧MINIMAL+LOCKで代替する」という挙動は、報告で事実として明記すべき。

### FXPW-R-02 [高] M3/M4 の新KP role の判定が未規定のままだと、再利用のたびにBLOCKするか、fallbackを素通しする
- **該当箇所**: 設計§A-1(N3)・§B-2・§D末尾、SP:416-449 / 482-534、MS:153・177
- **問題**:
  1. **KP_EN**: 汎用の `evaluate_segment_evidence` は英語roleに final style record(top-level `style_prefix` または `attempts_log`)を要求する。しかし Store の `qa_evidence` は attempts_log を保存しない(MS:177)。
     - そのため Store 再利用の entry は必ず `FINAL_STYLE_RECORD_MISSING` になり、BLOCK される。
     - さらに fallback 生成の entry は final style が ENGLISH_LOCK になるので `FINAL_STYLE_SHA_MISMATCH` で BLOCK され、設計の「warning扱い」と矛盾する。
     - 設計§Dは「base sha+Store key version照合」とだけ書き、汎用の final style 判定を外すことを明記していない。
  2. **KP_JA_MEANING(P8-KP)**: SUPPORT_JA には `fallback_used is not False → JA_FALLBACK_USED_OR_UNKNOWN` の分岐がある(SP:515-517)。KP_JA_MEANING への同等の分岐は設計に無い。base sha は runner が付ける「意図」にすぎないため、Style を落とした fallback が M3 を素通りする。
  3. M3 の戻り値に `warnings` を新しく設ける点と、runner(AR:1634)が status しか見ない点の扱いが未記載。
- **推奨**: role 別の判定表を設計に追記する。
  - KP_EN: base sha と `master_audio_key.style_instruction_id/version`(R-01採用時は `instruction_path` も)で判定する。final style 判定は、新規生成かつ非fallbackのときだけ適用する。
  - KP_JA_MEANING: base sha と `fallback_used is False` を必須にする。
  - KP_EXPLANATION_EN(P7): 現行の P3 と同じ判定でよい。
  - test: Store 再利用の K2 entry が PASS すること。fallback entry が warning(R-01採用時は key で識別)になること。P8-KP の fallback が BLOCK されること。
- **ユーザー判断**: No(既存Gateを新roleへ当てはめるだけ)。

### FXPW-R-03 [高] In One Line 文数Validatorを非ブロッキングにすると、ユーザー原文「1文を許容する旧経路を残さない」と整合しない
- **該当箇所**: 設計§C-5、ユーザー原文 L101・L103
- **問題**:
  - Prompt から「1文」は消えるが、LLM が1文(または4文)を返した場合、Production は `[WARN]` を出すだけで TTS・完成まで進む。つまり1文の In One Line を受け入れる経路が残る。
  - Coffee E2E だけ STOP 条件にする運用は、E2E の受入が Production 挙動より厳しいという二重基準になる。今後の全記事の保証にならない。
- **推奨**: 自動の再生成(新しいretry機構)は入れず、文数が {2,3} 以外なら Writer stage の出力時点で fail-closed STOP(TTS前、人間判断/再実行待ち)にする。Std は「Adv と文数が一致しない」も同じ扱いにするか、少なくとも WARN にする。カウンタの誤判定で誤STOPしないよう、略語・`$`始まり・引用符の test を厚くする。
- **ユーザー判断**: 条件付き。ユーザー原文§4(「残さない」)で既に決まっているとFableが判断できるならNo。Blocking QA条件の新設とみなすならYesとし、「WARNのみ/STOP」の2択を1問で提示する。推奨はSTOP。

### FXPW-R-04 [中] Local Rewrite 案L1の前提「A/B/CのIn One Lineは1文」は事実誤り。共有moduleへの適用範囲の確認が必要
- **該当箇所**: 設計§C-4、LR:629-661 / 686-752、CURRENT_SPEC:583
- **問題**:
  1. CS:583 の DECIDED では、A/B/C の In One Line は「中心1文+補足2文程度」の複数文である。「A/B/Cは1文のまま保たれるので不変」という根拠は成り立たない。L1 は A/B/C/Z 共通の `run_local_rewrite_recovery` を厳しくする挙動変更になる(採用候補が減り、Human Review が増えうる)。ユーザー制約「勝手に対象を拡張せず、互換性維持と変更範囲を確認」に該当する。
  2. カウンタの置き場が EFAM(Family X の runner)になっている。共有の er020 から EFAM を import すると依存が逆向きになり、循環 import のリスクがある。
  3. `seven_gates` / `all_seven_gates_pass` という名前・件数を前提にした既存 test や集計が壊れうる。
- **推奨**:
  - L1 は Family X だけで有効にする。Family X runner だけが設定する contextvar(既存の `secondary_run_scope` と同じ方式)で判定するのが最小。
  - カウンタは中立の小 module(または er020 内)に置き、EFAM はそれを import する。
  - gate は別キー(例 `8_sentence_count_unchanged`)で追加し、既存キーの意味は保つ。
- **ユーザー判断**: No(Family X に限定すれば A/B/C は不変)。全Familyに適用するなら、A/B/C 影響の報告が必要。

### FXPW-R-05 [中] In One Line の Prompt 文面: 大筋は承認済み仕様の実装の範囲だが、1か所に新しい「教訓・助言」を誘発するリスクがある
- **該当箇所**: 設計§C-1 / §C-2
- **評価**:
  - (a) 3文にする基準(理由条件、上限3、「詳細追加のための3文目」は禁止): ユーザー原文 L107 で「設計して報告」と委ねられており(#97)、新しい編集方針には当たらないと判断する。ただし例示の hedge(may / not always / at least)はニュース記事に頻出するので、3文が「必要時のみ」を超えて増えるおそれがある。Coffee E2E とその後の数記事で文数分布を観測項目にする。
  - (b) 「12-18 words」の撤去と「1文あたり12-22 words(not a strict rule)」: Trial v3 の実測値に由来する非拘束の目安で、許容範囲。ただし旧目安は「Trial-only」ラベル付きだったので、Production の目安として新設した事実を報告に明記する。
  - (c) 「using only what the article already says」: 既存の新事実禁止を補強するもので妥当。
  - **問題点**: 「its meaning or implication **for the listener**」は二人称の助言(「コーヒー好きなら…」)や教訓を誘いやすく、直後の「new conclusion, or lesson」禁止と緊張関係にある。
  - (d) Std への1文追加: 承認仕様の運搬として妥当。Std Prompt には「average 9-11 words / Split long clauses」があり、2文→3〜4文に分割される経路があるため、むしろ必要。
  - `_M1_REQ_ANCHOR` を一字一句保持すること、M1 経路(Production では常時)が新テンプレートから派生することは整合している。
- **推奨**:
  - 「for the listener」は削り、「its meaning or why it matters, as the article states it」等の中立表現にする。
  - Std の継承は R-03 の Validator で検査する。
  - 撤去後の Grep 対象に `ONE short` と `single most important` を追加する。Trial module の er045 は対象外でよい。
- **ユーザー判断**: No(#97 の「設計して報告」の範囲)。報告で文面と基準を提示すること。

### FXPW-R-06 [中] Family Z 非影響の根拠が不完全(推移的importを見落としている)
- **該当箇所**: 設計§A-4、AR:60、er063:718
- **問題**: Z は `x_runner.generate_key_phrase_explanation_en_verified` を lazy import する。x_runner は module の先頭で `er019_family_x_style_profile_01` を import しており、import 時に `_verify_constants()` が走る。新しく追加する4定数の sha/長さに誤りがあれば、Z の KP 解説生成が `StyleProfileStop` で落ちる。「Z は X profile を import しない」という記述は直接 import についてだけ正しい。
- **推奨**: Z の test に「x_runner の import と `generate_key_phrase_explanation_en_verified` の mock 呼び出しが成功する」smoke を追加する。設計書の根拠記述も訂正する。
- **ユーザー判断**: No。

### FXPW-R-07 [中] 「CLI指定を忘れても自動適用」は `--style-profile` についてだけ成立する
- **該当箇所**: 設計§A-2、AR:2219(`--tts-backend` の既定値=structured_separation)、SP:350-351
- **問題**:
  1. `--tts-backend` を付け忘れると、profile=default で tts stage が STOP する(fail-closed)。誤Styleにはならないが「自動適用」でもない。
  2. 旧記録(n01 等)が残る out_dir を同じ slug/run で使うと、CLI 未指定でも旧Styleで黙って進む。resume としては正しいが、新記事のつもりでの誤用を検知できない。
- **推奨**:
  - `source=="record"` かつ profile が `DEFAULT_NEW_RUN_PROFILE` でないときは、目立つ `[WARN][STYLE-PROFILE] 旧profileでresume中` を出す。
  - Coffee E2E の手順に「tts の前に `audit/style_profile.json` の profile_id==fx_20261016 を確認」を必須の前提条件として入れる。
  - 選択肢として、Family X runner に限り `--tts-backend` の既定値を承認済み backend にする案がある(Family X は flash-lite 統一が承認済み)。採るかどうかはFableが既存testへの影響を見て判断する。
- **ユーザー判断**: No。

### FXPW-R-08 [中] test計画の抜け
- **該当箇所**: 設計§F / A-5 / B-4 / C-5
- **追加すべき test**:
  1. main() 単位で CLI を指定しない test(`--stage plan --tts-backend speech_metadata_flash_lite`、`--style-profile` なし)。entry_point の `style_profile_source` と record の6role、`style_profile_plan.roles_sha256` を確認する。
  2. 旧 n01 / `coffee_n01_r2_p3_e1` 記録の out_dir で resume したとき、KP 英語が従来の `ensure_key_phrase_english_component` を通り(K2 key を使わず)、KP日本語意味が J3 のままであること。
  3. `--only-segments kp1_english` 等での再生成時に profile と K2 key が同一であること。
  4. `_generate_key_phrase_segments_a2` は現状 `style_profile` 引数を持たない(AR:1355)。この引数の受け渡し(threading)の test。
  5. R-02 の Store 再利用 entry に対する M3 PASS。
  6. R-06 の Z smoke。
  7. R-04 の L1 が A/B/C の文脈では不発であること。
  8. `qa_evidence.fallback_used` の既存 consumer 確認。Production の複数 module(er003_v1_n3_01_tts_generate.py、crosslevel_common、voice01 等)が `fallback_used` を参照している。KP 英語の再利用 entry を読む consumer が無いことは**未確認**であり、Grep と test で確定させる。
- **ユーザー判断**: No。

### FXPW-R-09 [低] 日本語roleの M4 は「意図」の sha しか見ず、再利用 entry にも現行の sha が再び付く
- **該当箇所**: AR:1293-1295、validation_inheritance:183-186
- **問題**: `is_untouched_entry` が除外するのは skip・引継ぎ・持ち越しだけである。そのため `reused_from_previous_run` の entry にも、現行profileの base sha が再び付く。fx は migrate 不可なので現時点では到達しない。ただし将来、上位集合への migrate で日本語role(SUPPORT_JA / KP_JA_MEANING)を追加すると、旧音声が M3 を素通りしうる。
- **推奨**: 設計に既知の制約として記録する。将来の migrate 設計時に「追加roleの cache 再利用を禁止する」ことを条件にする。
- **ユーザー判断**: No。

### FXPW-R-10 [低] 「P8」という名称が残り、KP 用 P8 と混同しやすい
- **該当箇所**: AR:1637(BLOCK 理由「P8対象segmentがP8で生成されていません」)、SP:597 / 614(`compute_ledger_hits` の既定値 P8_TEXT、キー `augmented_startswith_p8`)、SP:509
- **推奨**: 違反名の変更(設計§G(b))と同時に、AR:1637 の文言も「profile対象segment」へ直す。互換キーは残し、コメントで「Full Story用の旧P8」と明示する。
- **ユーザー判断**: No。

### FXPW-R-11 [低] Std の PD06 は「A2減速instructionを連結せず逐語で使い、生成後に6%減速」とする方式を報告で明示すべき
- **該当箇所**: 設計§A-1(`std_append_slower_instruction=False`)、CS:1238(「適用方式はWiring設計で確定要」)、ユーザー原文「6%減速は維持しPD06との併用を実証」
- **評価**: N01 の前例(2026-10-13承認)を踏襲したもので妥当。ただし PD06 には速度を落とす語句が無いため、Std の遅さは6%後処理だけで決まる。
- **推奨**: 報告に方式を明記し、試聴の確認項目にする。
- **ユーザー判断**: No(前例の踏襲)。

### FXPW-R-12 [低] `FAMILY_X_VARIABLE_ROLE_STYLE_VERSION` を bump するかどうかが未記載
- **該当箇所**: AR:466
- **評価**: 新しい out_dir では cache が無い。旧 out_dir は profile が固定されている。そのため bump は不要と判断する(bump すると旧 out_dir の resume で全面再生成になり、費用が増える)。
- **推奨**: 「bumpしない」とその理由を設計書に1行書いておく。
- **ユーザー判断**: No。

---

### 論点ごとの結論
1. **既定profileの切替**: 旧 out_dir は固定記録が優先されるため、resume・再生成は旧profileのまま正しく動く(SP:339-345)。M2 の「run state あり・記録なし→STOP」も維持される。M3/M4 の新role対応は R-02 の追記が前提。Family Z の根拠は R-06 で補強が必要。
2. **Master Audio Store**: Store を使うのは6roleのうち KP_EN だけ(残り5roleは run 単位で、固定記録と M3/M4 で守られる)ので、key の変更は KP_EN だけでよい。`style_instruction_id` の分離と version への sha12 埋め込みで、旧Style音声へヒットすることは構造的に防げる。ただし逆向き(fallback音声が K2 として保存されて再利用される)は防げない(R-01)。`fallback_used` の additive 追加の副作用は未確認(R-08-8)。
3. **共有module**: `primary_style_override=None` を既定にすれば、A/B/C のバイト同一性は保てる見込み(golden test 必須)。R-01 案を採れば repro01 の変更自体が不要になる。L1 は A/B/C へ波及するため Family X に限定する(R-04)。
4. **In One Line**: R-03(ブロッキング化)と R-05(文言修正)が条件。§C-3 の経路網羅は概ね妥当。`--regenerate-stage writer` 後は運用注記で足りるが、U-1 STOP は Production の正式経路で発火が未観測(CS:1201)なので、E2E で確認する。N8(句読点だけの変更で2文→1文)は L1 で捕捉できる。
5. **撤去と残置**: 妥当。`default_new_run_n01` の撤去、旧profileと `open243_m1_enabled` の死コード残置(M1 は Production で常時有効)はいずれも問題ない。
6. **承認範囲の拡大**: E1/R2 の既定化(#100)、Hook 廃止(#98)、P7/PD06 の正本(#96)はいずれもユーザー原文に根拠がある。ユーザー原文に無い追加は、In One Line の「for the listener」(R-05)と、L1 の A/B/C への波及(R-04)の2点。それ以外に要約による範囲の拡大は見当たらない。

### 総評: 条件付き可
実装に進む前、または実装と同時に満たすべき条件は次のとおり。
1. R-01: K2 fallback 音声を key で分離する(`instruction_path`)。採らない場合は、その理由と残るリスクを明記する。
2. R-02: role 別の M3/M4 判定表を設計に追記する(KP_EN の final style 判定の扱い、KP_JA_MEANING の fallback 検査)。
3. R-03: 文数Validator を fail-closed にするかどうかを決める(Fableが判断できなければ、ユーザーに1問で確認)。
4. R-04: L1 を Family X だけで有効にし、カウンタを中立moduleへ移す。
5. R-05: 「for the listener」を修正する。
6. R-06 / R-08: test を追加する(main() 単位でCLI未指定、旧 out_dir の resume、Z の推移的 import、Store 再利用時の M3、`fallback_used` consumer の確認)。

R-07、R-09〜R-12 は実装時に反映すればよく、ブロッカーではない。Production 採用の可否はこのレビューの対象外で、人間ユーザーだけが判断する。

参照ファイル:
- C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01\WIRING_DESIGN_01.md
- C:\Users\tensh\eigo-radio\er019_family_x_style_profile_01.py
- C:\Users\tensh\eigo-radio\er019_family_x_audio_production_runner_01.py
- C:\Users\tensh\eigo-radio\er006_master_audio_store_01.py
- C:\Users\tensh\eigo-radio\er006_audio_cost_pilot_02_shared_narration.py
- C:\Users\tensh\eigo-radio\er003_v1_repro01_main_generate.py
- C:\Users\tensh\eigo-radio\er020_tts_retry_local_rewrite_01.py
- C:\Users\tensh\eigo-radio\er003_v1_n3_01_advanced_adaptation_generate.py
- C:\Users\tensh\eigo-radio\er003_v1_n3_01_standard_a2_generate.py
- C:\Users\tensh\eigo-radio\er063_family_z_audio_01.py
- C:\Users\tensh\eigo-radio\er019_family_x_validation_inheritance_01.py