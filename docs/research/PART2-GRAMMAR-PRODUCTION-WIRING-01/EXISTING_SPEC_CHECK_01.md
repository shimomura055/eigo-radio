# EXISTING_SPEC_CHECK_01(Part 2「Grammar & Sentence Structure」+ Trial-08選定方式 Production化の既存仕様確認)

管理ID: PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_01 / 日付: 2026-10-25 / API 0・runner無改変
ユーザー決定の根拠: `docs/pm/delegation_log/2026-10-25_PART2-GRAMMAR-PRODUCTION-WIRING-01_USER.md`(APPROVED_FOR_PRODUCTION: Part 2文法解説+Trial-08構文選定方式。Tier内順位改善・HIGH判定安定化・OTHER拡張は承認対象外)。委任文逐語=`..._DELEGATION_01.md`。

## 1. 「承認済み仕様」として固定する規則(Trial-07/08の逐語。移植先=`er120_part2_grammar_production_01.py`)
| 規則 | 出所(Trial、file:line) | Production module側 | 固定方法(test) |
|---|---|---|---|
| Step A'' 抽出Prompt(1文差替版) | `run_trial_08.py:17-19` `STEPA8 = STEPA7.replace(OLD_LINE, NEW_LINE)`、`run_trial_07.py:42` `STEPA7` | `STEPA_PROMPT`(sha256 `51912fe1e2428c347c09969f2f3e8831c73782d5669921e6508c15de8855e15c`、5217字) | `test_A1`(byte一致)・`test_A2`(Trial-08有料呼出5作品11 callの`prompt_sha256`==本moduleの完成prompt sha) |
| Step B 解説Prompt | `run_trial_04.py:128` `STEPB`、`:171` `stepb_prompt`(Trial-07 Step Bも同一) | `STEPB_PROMPT`(sha256 `59588b5961e88d1be052e9ae5045ed90ca243546d6996027b60336e3083b591c`、1087字) | `test_A1`・`test_A3`(Trial-07有料Step B 7件の`prompt_sha256`を保存選定から再現) |
| 分類・優先順位・定数 | `run_trial_07.py:35-40`(STRONG/MID/PRIORITY/TARGETS/FRONT_OK) | 同名定数 | `test_A4` |
| eligible7(基礎のみ除外・OTHER除外・材料欄・TV=HIGH+`teaching_value_ja`・中クラス`misread_*`逐語・FRONT`front_kind`・ELL`omitted_words`) | `run_trial_07.py:185` | `eligible7` | `test_B2`(29標本のTier表一致) |
| 倒置の扱い(Tier1=INV以外の適格/Tier2=適格なINV/Tier3=0件) | `run_trial_08.py:24` `select_tiered` | `select_tiered`(Trial同一)+`rank_eligible`(HR用の順位付き全list。先頭は常に`select_tiered`と一致) | `test_B2`(29標本で選定一致)・`test_B3`(代表8作品表) |
| 逐語解決・段落境界連結再解決・単一span検証・前後文 | `run_trial_04.py:203,214`、`run_trial_06.py:89-103`、`run_trial_07.py:110,141,150` | `resolve_verbatim/resolve6/resolve7/verify_single_span/local_context/parse_candidates` | `test_B2`(features一致)・`test_E1`(open_window r2連結回帰) |
| 最大1件・0件許容・0件文面 | `run_trial_07.py:195`、`run_trial_04.py:193` `ZERO_P2` | 最終採用1件(HR前の候補listは順位付き複数)・`ZERO_P2`同一 | `test_A4`・`test_D6` |
| モデル・API形式 | `run_trial_07.py:make_real_llm`(`gpt-6-luna`・`responses.create`・`max_output_tokens` A=13000/B=6000・userメッセージのみ) | `MODEL=routing.SUPPORT_MODEL`、`MAXOUT_EXTRACT=13000`、`MAXOUT_EXPLAIN=6000` | `test_A4`・`test_P5` |
| 日本語訳(T1) | Trial-08 `run_translate_08.py`(T1 module読み取り利用) | `er003_kp_source_sentence_ja_01.generate_translations`を再利用(Part 1と同一工程) | `test_D1`・`test_D7` |

## 2. 対象レベル(事実確認)
- Step A''/Step Bのどちらも**Advancedのみ**。根拠: `STEPA7`冒頭「下の英語本文(**Advancedレベル**)」(`run_trial_07.py:42`)、`# 作品・レベル` 「レベル: Advanced」(Prompt本文)。Trial-07/08の8作品の本文は、Family X Advanced既存`b1b/article.md`(`SRC7["boredom"]`、`run_trial_07.py:17`)、Family Z Writer r2(Advanced, `SRC7["melos"]`)、およびTrial-04以来の既存Advanced本文。Standard(a2)本文でのTrial実績は**ゼロ**。
- **結論: Production適用レベル=Advanced(b1b)のみ**(Part 1も同じ。`PART1_WIRING_DESIGN_01.md` §0「Standardへは拡張しない=新仕様」、CURRENT_SPEC:2039)。Standard(a2)へ広げるのはTrialと異なる条件=新仕様のため行わない(`er120`の`LEVEL="Advanced"`、`test_P5`)。必要ならユーザー判断候補だが現時点で要求なし(実害なし)。

## 3. 正式初回経路・後続経路・配置位置(読み取りのみ。runnerは変更しない)
| Family | 本文(入力) | 配置位置(Part 2) | retry/regen/resume | 備考 |
|---|---|---|---|---|
| **Z** | Writer r2 → `canonical_article_text(w62.rd(_level_text_path(ctx,"b1b")))`(`er026:1287,1855`)。`.split("\n\n")`が`run_trial_07`の本文段落と一致(melos r2で29段落・完全一致を確認) | `stage_kp`(`er026:1693`)の`kp_part1_ja_b1b`(`:1785`)と`_assemble_study_rows`(`:1786`)の近傍。**Part 2はKP非依存(入力=本文のみ)**なので、`stage_kp`外の新stage(`part2_b1b`)にして`kp`と並列・TTS前、が最短。`stage_pages`(`:2058`)でPart 1 blockの直後に描画 | `ensure_stage`(provenance・`--regenerate-stage`)、`E2E_KP_EXTRA_REGEN_NAMES`(`:1135`)。**本文変更はWriter r2再生成(`DEPENDENTS` `er062:64` `"r2":["std_adjust","plan_b1b","kp_b1b"]`)に連動**するため、Part 2は`r2`の従属に加える必要がある(Part 1は表現のみ入力で不要だったが、Part 2は本文入力) | KP完了を待たず並列にできる(独立) |
| **X** | `{source_dir}/b1b/article.md`(`er019:480,561`)。`# `タイトル段落・本文段落・`## In one line`(`paragraphs_from_article_md`が除外。Trial `SRC7["boredom"]`と同一処理、`test_E7`) | scaffold b1bのKP PASS後(`er019:700-717`の`part1`ブロック隣)、または独立。再実行用`--stage study_text`(`:584`)の拡張、または専用stage | X resolverは署名一致で再利用/不一致で自動再生成(Part 1と同型)。`kp_part1_failed.json`と同型の専用marker | 旧構造(`###`見出し混在)の記事2/26あり=段落として扱うだけ(Trial同一挙動) |
| **Y** | **正式Production入口なし**(`er110_family_y_*`はDEV/Trial専用、`y_entry_point.json`に`production_reachable=False`: `er110_family_y_audio_trial_01.py:176`。OPEN-484:999) | 配線不可(入口が無い)。新設は新仕様(禁止) | — | 安全に準備できる部分=**moduleがFamily非依存**(入力=本文段落+label。Family分岐・runner参照なし。`test_P2`)。Y Production化時の必須受入条件をOPEN-484へ追記する |
| A/B/C(strategy_l) | — | 非適用(27-7) | — | module未参照を次委任でtest固定 |

## 4. 既存仕様との整合(照合した箇所)
- Part 1配線パターン: `er003_kp_general_explanation_01.py`(routing process分離・Prompt逐語コピー+sha・技術retry1回・model不一致STOP・`audit`・`require_fresh_*`・`render_html_block`・`STUDY_CSS`)。`PART1_WIRING_DESIGN_01.md` §2〜§9,§13〜§15。本moduleは同型(別process名で原価を分離)。
- routing: `er006_model_routing_contract_01.py:130,133`(Part 1の2 process)と同様に新2 process(`STUDY_TEXT_GRAMMAR_EXTRACT`/`STUDY_TEXT_GRAMMAR_EXPLAIN`)を`SUPPORT_MODEL`へ登録する**必要**(次委任。本委任は新規ファイルのみのため`er006`無変更。登録前は`routing.require_model`が`ModelContractViolation`=fail-closed、`test_P1`)。
- KP HR設計: `KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/DESIGN_01.md` §k(`kind="grammar"`、TOP2=`select_tiered`順の先頭2件・追加LLM callなし、AUTO=TOP1、適格0=Part 2コーナー扱い)。本moduleの`review_request()`/`select_from_candidates()`/`reselect_candidates()`がその接続面(er119の実装は並行agentが担当)。
- 既存SSOT: `OPEN-497`(Trial-07/08)、`OPEN-512`(Part 1 PRODUCTION_WIRED)、`OPEN-518`(KP HR)、`OPEN-484`(Y)。`CURRENT_SPEC.md:1703,2039`=Part 1 Status節(Part 2は未記載=PRODUCTION_WIRED時に追記)。

## 5. 発見した「Trial→Production」の差分(仕様逸脱ではなく、Production化に必須の最小の安全側差分)
| # | Trial | Production module | 理由 |
|---|---|---|---|
| D-1 | `parse_error`→`features=[]`のまま保存(=0件扱い) | 応答不正は技術retry1回→`Part2Error`(fail-closed)。**パース不能を「0件」にしない** | 0件は「適格なし」の正当な結果であり、失敗の隠蔽は禁止(安全≠成功)。`test_D9` |
| D-2 | 選定は先頭1件 | 全適格を順位付きlist化(先頭=Trialの1件)。最終採用は1件のまま | ユーザー決定④(HR: TOP1/TOP2)に必要。順序は`select_tiered`と同一(`test_B2`) |
| D-3 | Step B出力は構造検査なし | 見出し構造(必須3見出し・順序)・日本語含有・ページ非表示語を検査、違反は技術retry→STOP | Part 1 §14-4と同型の構造検査。品質判定の新設ではない |
| D-4 | Step Bに参考訳なし(KP一致時のみ`ref_ja`) | T1訳を`ref_ja`(参考訳)としてStep Bに渡す(Prompt本文は不変。`STEPB`に「参考訳が渡されている場合は…」は既存) | 委任文(T1訳)・Part 1との訳の一貫性。Part 1で訳済みの同一英文はAPI 0で再利用 |
| D-5 | 見出し「## Part 2. Grammar & Sentence Structure」 | 節見出しにPart番号を出さない(`Grammar & Sentence Structure`) | Part 3/4未採用の番号参照=Dangling防止(Part 1と同じ規約、`PART1_WIRING_DESIGN_01.md` §4) |
| D-6 | 0件時: `ZERO_P2`文面を載せたPart 2節 | 同じ文面を載せる(Trial同一) | KP HR設計§kは「コーナーなし」と記述するが、Trial実出力(`OUTPUT_07_*_USER.md`)は文面表示。Trialを正としModule既定は文面表示。要整合はFable照合(B: 承認範囲内で自己解決) |

## 6. 判断候補の仕分け(PM_GOVERNANCE 27-3)
- **なし(D=真に新しい判断は検出されず)**。D-1〜D-6はいずれもB(承認範囲内で自己解決、ユーザー決定の機能を実現する最小の安全側差分)。
- 注意(C=現タスク外・親案件): Human不介入時のTOP1自動採用を「明示宣言(auto)のみ」とするか否かはKP HR親案件(`DESIGN_01` 原則3)で決まる。本moduleは`mode`引数(`wait`既定/`auto`)で受けるだけで、既定の挙動を決めない。
