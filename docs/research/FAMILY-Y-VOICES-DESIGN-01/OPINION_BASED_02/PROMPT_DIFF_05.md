# PROMPT_DIFF_05 (委任_24: 新テーマ再現Trialに向けた、コード・Promptの差分と理由。テーマ非依存の一般化に限る)

作成: 2026-10-24。API 0。前回の`PROMPT_DIFF_04.md`の続き。ユーザー原文§2: **今回の題材だけに依存するハードコードや個別Promptを増やさない**。

## 1. 結論(差分の総量)
| 対象 | 変更 | 理由 |
|---|---|---|
| **Voice Prompt(`VOICE_PROMPT_OB2`、考え方A〜D入り)** | **変更0字**(02のものをそのまま使用。testで`VOICE_PROMPT_OB2`の再利用と、runner内に`THINK_BLOCK`が無いことを固定) | 前回run_03までの改善成果を踏襲(ユーザー§5)。テーマ固有のPromptを増やさない |
| `render_persona_ob2`・`OPENING_GUIDE_02`・反復検出 | 変更0(再利用) | 同上 |
| `er110_family_y_opinion_based_01.py`・`_02.py` | **無変更**(`git diff`で0。testで固定) | run_01〜run_03の再現性を保つ |
| **新規** `er110_family_y_opinion_based_03.py`(DEV/Trial専用・未配線) | 追加(約150行) | 02のrunnerは、World frame・Sheet・人物名ラベルをコード内に持つ。別テーマで再現するためには、これらを**データ(`THEME_DATA_02.json`)から読む**形にする必要があった。コードにはテーマ固有の語を一切持たない(testで`再配達`等の語が無いことをGrep固定) |
| 新規データ `THEME_DATA_02.json` | 追加(テーマ固有の情報はすべてここ) | World frame(中心の問い・前提・用語定義5件)、WHO_JA、Persona Sheet 3名 |
| `er110_family_y_opinion_based_01_test_01.py`・`_02_test_01.py`・`er110_family_y_persona_pipeline_01_test_01.py` | 隔離testの許可リストに03とそのtestを追加(各1〜2行。er110_family_y_*_test_01 全8ファイルで156件PASS) | 03は02を`import`して再利用するため、『02を他moduleがimportしない』という隔離testが03を例外として扱う必要がある。03自体もどのProduction runnerからもimportされないことを03のtestで固定 |

## 2. 03が02と違う点(すべてテーマ非依存)
1. `load_theme()`: JSONを読み、`restricted_voice_ids`(権利区分R2+/R3の出典だけが根拠の項目)に01の照合が使う`tbs_only`印を付ける。前回のハードコード`startswith("TBS")`を、データ駆動の汎用版にした。
2. `validate_theme()`: Sheetの必須欄・冒頭の型・`relevant_terms`が定義にあること・経験欄IDの重複を、**有料run前に**検査(不備なら起動せずrc=9)。
3. `patched_ob_03()`: `patched_ob`と同じ差し替え(with内だけ、抜けると復元)。`relevant_terms`による定義の絞り込みは、03内の同形のclosureで行う(02の`SHEETS_02`参照を使わない)。
4. 起動ガードは02と同じ(`--paid`+`BUDGET_APPROVED.json`+run名の許可リスト+再起動不可+出力先は`er110_output/`配下固定)。**承認ファイルは作っていない**。

## 3. 気づき(Fable確認事項。いずれも実装していない)
### 3-1. Voice Prompt規則9(数字・漢数字の数量表現を使わない)と、回数が論点のテーマ
- 再配達は『最初の一回は無料、二回目から有料』のように**回数そのものが論点**。規則9は『調査・統計の数字を捏造しない』ことが本来の目的だが、文面は数量表現全般を禁じる。
- 現在の対処: Sheetの文は回数を数字にせず『くり返し』『最初の不在は大目に見る』と言い換えた(testでSheet全文の数字0、`NUM_RE`該当0を確認)。この範囲ではPromptを変えなくてもR0は成立する見込み。
- 候補(未実装・判断はFable): (a)Promptは変えず、言い換えで通す(推奨。まず1回のR0で確かめる) (b)規則9に『経験欄にある回数の言い回し(最初の、くり返し、何度も)は可』と明確化する(DEV Promptの変更になる。Opus条件の対象か要判断)。**(b)は品質ルール(数字を使わない)の解釈変更**を含むため、独断で入れない(CLAUDE.md共通Charter 1)。
### 3-2. 規則7の例示語
- 規則7に『この前』『ある子が』『友達が』『先生が』という例示語がある(SNSテーマ由来だが、『欄にない人物・出来事を作らない』という一般規則の例示であり、再配達でも害はない)。**変更しない**。
### 3-3. Gateの予算skip閾値が固定(22円)
- `er110_family_y_opinion_based_01.run_pipeline`は、累計22円超でLeakage Gateを`SKIPPED_BUDGET`にする(閾値がコード内の固定値)。前回は23.7円でskipされ、後追いで0.109円かけて確認した。今回も同じ流れの想定(`BUDGET_PLAN_OB_04.md` §4の5)。閾値を上げる変更は、Gateを回避する変更ではないが、**新しい閾値の決定を伴う**ためFable判断(提案: そのまま後追い運用を踏襲)。
### 3-4. `BUDGET_STOP_27`の名前
- 予算停止のコード名`BUDGET_STOP_27`は、cap値が変わっても名前が27のまま(ログ上の呼称)。機能に影響なし、変更しない。

## 4. 撤去・残置した規則・検査・testの識別子
- 撤去: なし(01・02の規則・検査・testは全て残置)。
- 追加: `er110_family_y_opinion_based_03_test_01.py` 23件(下記)。
  - 並び: theme_loads_and_validates / validate_theme_rejects_bad_data / theme_text_has_no_numbers_or_stats / source_ids_exist_and_are_personal_voices / attributes_match_source_labels / stance_basis_matches_persona_claims / personas_are_differentiated / definitions_do_not_leak_into_personas / world_frame_valid_and_theme_scoped / theme_file_matches_generator / runner_code_has_no_theme_specific_words / patch_restores_01_globals / prompts_carry_no_cross_voice_content / happy_path_with_fake_and_restore / budget_cap_applied_from_argument / main_requires_paid_flag...(起動ガード) / no_approval_file_created_and_run_dirs_inside_er110_output / isolation_no_importer / import_has_no_side_effect / 01_02_and_existing_modules_unchanged / docs_reference_only_existing_voice_ids / voices_quotes_exist_in_saved_sources / voice_catalog_invariants
- 残存Grep: 03にテーマ固有語0(`再配達|宅配|配達員|置き配|ロッカー|営業所|有料化|ドライバー`、docstring除く)。
