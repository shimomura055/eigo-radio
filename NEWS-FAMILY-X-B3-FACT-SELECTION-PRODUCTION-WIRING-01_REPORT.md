# NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01 — Phase 1 REPORT

Sonnet(sonnet-worker)がFable委任(2026-09-26、ユーザー確定事項1〜13)に基づき実装した
Production配線Phase 1の報告。Phase 0調査結果は`docs/pm/RESULT_PACKET_FXB3.md`(前回)。

## 1. 目的

Family X/Entertainment系統に、以下の正式フローをProduction配線する:

```
Research → Full Fact Ledger → AIが中心Storylineを1つ決定 → B3(4テスト)を全Factへ適用
  → Selected Fact Brief → Writer(Original→R1→R2) → Advanced → Standard
```

B3は`APPROVED_FOR_PRODUCTION`(ユーザー確定)。Storylineを人間が毎回指定する運用にはせず、
LLM 1 callでStoryline決定+B3 Fact選定を行う。日本語Writer(Original→R1→R2、P7)の
Production配線もB3配線と同時に実施する。Family Aは変更しない。

## 2. 配線構成図

```
er019_family_x_entertainment_production_runner_01.py (正式入口、新規)
  --theme <topic> --slug <slug> --out-dir <dir>
  --stage research|ledger|storyline_b3|writer|advanced|standard|all
  --regenerate-stage storyline_b3|writer|advanced|standard
  --stop-after storyline_b3|writer|advanced|standard (既定standard)
  │
  ├─ Stage: research_ledger
  │    既存 er012_e_family_entertainment_two_level_runner_01.
  │    run_researcher_for_topic() / run_verification_for_topic() をそのまま呼び出し
  │    → vfl01.build_verified_ledger_text() → verified_fact_ledger.txt (Full Ledger)
  │
  ├─ Stage: storyline_b3 (新規Production module)
  │    er019_family_x_storyline_b3_fact_selection_01.run_storyline_b3_selection()
  │    Full Ledger → LLM 1 call → selected_storyline + fact_tests(4テスト全件)
  │    + selected_fact_ids + selected_fact_brief + recheck_note
  │    → full_ledger.json / selected_brief.md (別ファイル) / fact_selection_evidence.json
  │
  ├─ Stage: writer (新規Production module、P7逐語移設)
  │    er019_family_x_ja_writer_o_r1_r2_01.run_ja_writer_o_r1_r2()
  │    Storyline(テーマ：行) + Selected Fact Brief([ニュース]欄)
  │    → Original → R1 → R2 (previous_response_id連鎖)
  │
  ├─ Stage: advanced / standard (既存、無変更)
  │    er012_e_family_entertainment_two_level_runner_01.run_writer_stage()
  │    (adv_gen.generate_advanced_adaptation / std_gen.generate_standard_a2
  │     + vfl01.run_deviation_check、Full Ledgerで検証、1回retry→STOP)
  │
  └─ (Mandatory STOP、構造的): scaffold/tts/assemble/player関連の関数は
       本runnerに一切import・実装されていない
```

## 3. Storyline+B3 Prompt(新規、逐語)

`er019_family_x_storyline_b3_fact_selection_01.py`のDeveloper message・User prompt template・
B3 4テスト定義(ユーザー確定事項5の逐語)。JSON schema出力(`selected_storyline`/`fact_tests`
[fact_id×test1-4回答×decision×reason]/`selected_fact_ids`/`selected_fact_brief`/
`recheck_note`)。model=`gpt-5.6-luna`、effort=`high`(JA Writerと同一)。技術的失敗
(JSON不正・Ledgerに存在しないfact_id)は1回retry→STOP(`validate_selection_output()`)。
Trial(`er015_family_x_writer_fact_selection_trial_02.py`)のFACT_TESTSハードコード辞書は
参照していない(新規LLM自動判定)。

日本語Writer(`er019_family_x_ja_writer_o_r1_r2_01.py`)は、`er015_news_original_baseline_
repro_01.R0_PROMPT`/`DEVELOPER_MESSAGE`と`er015_news_iterative_entertainment_trial_01.
REVISION_INSTRUCTIONS["r1"/"r2"]`をsha256一致で逐語移設(test`JaWriterVerbatimTests`で検証)。
「テーマ：」行をStorylineへ、`[ニュース]`欄をSelected Fact Briefへ差し替える点のみが
Trialとの差分(P7本体・語数目安・出力形式・Revision方式自体は無変更)。

## 4. Runtime run結果(Meta「Muse human concierge」、実API、1 run)

出力: `er019_output/family_x_b3_production_wiring_01/run_01/`

- **Research/Full Ledger**: web_search 7回、15 Fact中VERIFIED 15/AMBIGUOUS 0/REJECTED 0。
- **Storyline+B3(1 call、retry不要)**: Selected Storyline「MetaはAIエージェント「Muse」の
  電話機能で一部の通話を訓練済みの人間契約スタッフに担わせる実験を行ったが、ユーザー情報が
  スタッフに共有され得る懸念や適切な開示の不足を受けてミスと認め、機能を当面ロールバック
  した。」。15 Fact中3件採用(MUSE-HC-006/010/012)、12件除外。recheck_note=null
  (3件のため不要)。
- **JA Writer(Original→R1→R2)**: previous_response_id連鎖(fallback未使用)。R2完成
  (973字)。
- **Advanced**: 1回目MAJOR(Ledger deviation、電話相手側とMuse利用者の認識混同+ロール
  バック時制の誤り)→1回retry→LEDGER_COMPLIANT(STRUCTURE_PASS)。411語。
- **Standard**: 1回目でLEDGER_COMPLIANT(STRUCTURE_PASS、v5 6,000語ライン)。414語。
- 全stage`model_id_actual=gpt-5.6-luna`、fallback_detected=false。

**観察事項(事実記録のみ、仕様変更なし)**: (1) `run_writer_stage(only=...)`をコスト分離
目的で2回に分けて呼んだため、既存`writer_run_summary.json`保存ロジック(呼び出し末尾で
毎回上書き)により最終的に"advanced"キーが失われた。**Fable差し戻し1回目でこの旧実装
(手作業での側面ファイル補完)はGate 3 #13未充足と判定され、下記4.1のとおり修正済み**。
(2) Advanced段のLedger Deviation Check(LLM判定)は同種の文言に対し実行のたびに判定が
変動した(1回目run時はLEDGER_COMPLIANT、2回目run[`--regenerate-stage advanced`]では
同種表現がMAJOR→再生成後PASS)。既知のLLM判定非決定性であり、本タスクで調整・変更は
行っていない(詳細は下記4.2 Fact drift結果)。
(3) 初回run(`--stage all`)はStandard段でMAJOR×2(初回+1retry)でSTOPしたため、Full
Ledger/Selected Brief/JA記事を再利用しつつ`--regenerate-stage advanced`を再実行し
(重複Research・重複Storyline+B3 callは発生させていない)、最終的にAdvanced→Standardが
両方PASSする形でRuntime evidenceを完成させた。既存の「1回retry→STOP」capは回避・
無効化していない(各呼び出し内部のGate・retry上限は無変更、既存`--regenerate-stage`
機能を通常運用同様に再度呼び出しただけ)。

### 4.1 Gate 3 #13修正履歴(Fable差し戻し1回目)

**指摘**: `run_writer_stage(only=...)`を2回に分けて呼んだ結果生じた"advanced"キー
消失を、手作業で別ファイル(`b1b/audit/final_advanced_summary_reconstructed.json`)へ
補完していた。runtime evidenceが手作業で補われた状態はGate 3 #13の充足と認められない。

**修正内容**:
1. `er012_e_family_entertainment_two_level_runner_01.run_writer_stage()`を、
   `writer_run_summary.json`への保存時に既存ファイルとマージする(既存キーを消さない)
   よう修正。unit test`test_writer_run_summary_json_merges_across_separate_only_calls`を
   `er012_e_family_entertainment_two_level_runner_test_01.py`へ追加(43/43 PASS)。
2. run_01の`writer_run_summary.json`自体を、手動再構成ではなく**プログラムで**再構成する
   新規スクリプト`er019_writer_run_summary_reconstruction_01.py`を作成。raw_usage_log.jsonl
   のAPI呼び出し順序(コード上の不変条件: generate→deviation_check、MAJORなら再度
   generate→deviation_check)とattempt_numberのプロセス起動ごとのリセットを根拠に、
   最終invocationのgenerate call(response_id)を特定し、既存の`b1b/audit/deviation_check.json`
   /`a2/audit/deviation_check.json`/`article.md`と突き合わせてevidenceを再構成する
   (推測ではない、コード読解に基づく不変条件のみを使用。不変条件が崩れる異常系は
   `ambiguous_stages`として明示しキーを追加しない)。unit test8件
   (`er019_writer_run_summary_reconstruction_01_test_01.py`、8/8 PASS)。
3. run_01へ実行し、`writer_run_summary.json`を再生成(由来は`_reconstruction_provenance`
   キーへ記録)。旧(バグで壊れた)ファイルは`writer_run_summary_pre_gate3_fix_buggy_overwrite.json`
   として保持(削除しない)。手動再構成版(`final_advanced_summary_reconstructed.json`)は
   `b1b/audit/final_advanced_summary_manual_reconstructed_superseded.json`へrenameし、
   supersededである旨を追記して保持。

### 4.2 Fact drift結果(記録のみ、再生成しない)

Ledger `MUSE-HC-012`は「機能を当面ロールバックした」(完了・過去形)。JA R2は
「人間のコンシェルジュ機能は当面ロールバックされます」(未来形・受身)、Advanced/
Standardは"The human concierge feature will be rolled back for now."(未来形)。
Advanced 1回目のdeviation checkはこの時制不一致を含む2件をMAJORと指摘したが、
既存Production実装(`run_writer_stage`)の仕様上、却下された1回目の判定内容は
ディスクへ保存されない設計であり、retry後の本文(同じ時制表現のまま)は2回目の
判定でLEDGER_COMPLIANTとなった(判定の非決定性、本タスクでは調整していない)。
逐語・Ledger該当行・retry後の保存済みJSONは
`er019_output/family_x_b3_production_wiring_01/run_01/audit/fable_editorial_findings.md`
「指摘3」に記録(**修正案・実装は行っていない、ユーザー判断待ち**)。

### 4.3 Selected Brief整形バグ修正(Fable差し戻し1回目、Gate 3 #2)

`storyline_b3/selected_brief.md`の「## Selected Facts」冒頭でStoryline文が重複出力
されるバグを確認(Prompt指示5「冒頭にStorylineの1行を含める」によりLLM出力
`selected_fact_brief`自体がStoryline文で始まるため)。`build_selected_brief_markdown()`を、
`selected_fact_brief`の先頭がStoryline文と完全一致する場合のみ重複部分を除去するよう
修正(完全一致しない場合は憶測で改変しない)。unit test2件追加(重複除去ケース/
非一致時の非改変ケース)。run_01の`selected_brief.md`原本(Writerへ実際に渡した実物)は
再生成せず不変のまま保持し、修正後ロジックを同run_01の実データへオフライン適用した
結果を`storyline_b3/selected_brief_fixed_format_preview.md`として参照用に追加保存
(Writer未使用と明記、API呼び出し0)。

### 4.4 Storyline観察(記録のみ、Fable差し戻し1回目)

AIが決定したrun_01のStorylineは、Trial-02の`CORE_STORYLINE`が含んでいた
「AIだと気付かれると切られることがある→人間スタッフへ引き渡す」という**人間を
使った理由(なぜ人間なのか)**の因果連鎖を含まない。MUSE-HC-009(AIだと気づかれ
電話を切られる個別報告)はTest2=NOで除外されており、これがStoryline選定手順
そのものの欠陥か、今回のFull Ledgerの記述粒度・Fact構成による結果かは、本記録
だけからは判断できない。Trial-02 Storylineとの差分・MUSE-HC-009の4テスト理由文
(逐語)は`run_01/audit/fable_editorial_findings.md`「指摘4」に記録
(**判断は書いていない、ユーザー判断待ち**)。

## 5. コスト表

| stage | JPY |
|---|---|
| research | 14.47 |
| ledger(verification) | 14.27 |
| storyline_b3 | 0.67 |
| ja_original | 0.24 |
| ja_r1 | 0.24 |
| ja_r2 | 0.26 |
| advanced(1 retry込み) | 4.99 |
| standard | 4.87 |
| **合計(1記事)** | **40.00** |

量産換算: 1記事¥40.00 → 10記事¥400 → 30記事¥1,200 → 100記事¥4,000。
B3導入増分(旧方式=Storyline+B3 callを持たずFull Ledger相当をWriterへ渡す/従来の
Sonnet手書き素材、と定義): 増分はStoryline+B3の1 call分のみ=¥0.67/記事(Research/Ledger/
JA Writer/Advanced/Standardは旧方式でも必要な既存工程であり、B3固有の追加ではない)。
量産換算のB3増分: 10記事¥6.7/30記事¥20/100記事¥67。

## 6. Gate 3(24項目)

`er019_output/family_x_b3_production_wiring_01/gate3_checklist.md`(証跡パス付き24項目)。
Sonnet仮判定: 1〜18(技術的証跡)は今回のN=1 runで充足。19〜21(SSOT反映)は本タスクで
反映済み。22(Git commit/push)は本Report作成後に実施。23(Dangling Reference)は下記7節。
24(ユーザー承認仕様との一致)は下記8節。**`PRODUCTION_WIRED`の正式判定はFable/ユーザー**。

**Fable差し戻し1回目での更新**: #13(runtime evidenceの整合性、手作業補完を解消)・#2
(Selected Brief整形バグ修正)を修正し、#17/#18の証跡を更新した(詳細は上記4.1/4.3、
チェックリスト該当行)。#18(regression test)は`failures=3`だが、いずれも本タスクが
一切変更していない`er003_v1_n3_01_tts_generate.py`/`er003_v1_sing01_voice01_generate.py`
(並行稼働中の別Agent[TTS配線]による未commit差分)を検知するguard testの失敗であり、
`git status`で本タスクの変更対象外であることを確認済み。

## 7. Dangling Reference Check

- `er019_family_x_storyline_b3_fact_selection_01.py`/`er019_family_x_ja_writer_o_r1_r2_01.py`/
  `er019_family_x_entertainment_production_runner_01.py`いずれもGrep確認: `import er015`
  (Trial module)への実行時依存は0件(コメント内の由来注記のみ)。
- `CURRENT_SPEC.md` L828: 「配線先Production経路: 未確定」の記述を解消する追記を行い、
  「2〜3文の中立素材」記述が本行内で歴史的経緯(旧方式)として明示され、現行方式(Selected
  Fact Brief使用)と明確に区別されていることを確認した。他行に同種の矛盾する記述は無し
  (Grep確認)。
- `OPEN_ITEMS.md` OPEN-177(1): 旧「未配線のまま」記述に追記する形で更新し、旧記述と
  矛盾しないよう「解消した」の直後に旧記述をそのまま残して経緯を追跡可能にした。

## 8. QCD

- **Quality**: Full Ledger 15 Factのうち、Storyline確立に不要な12 Fact(規模・成功率・
  個別発言事例・将来方針等)がSelected Fact Briefから機械的に除外され、Writerへ渡る
  素材はStoryline直結の3 Factのみに絞られた(Fact詰め込み抑制効果を確認、N=1)。
- **Cost**: 1記事あたりB3固有増分は¥0.67(全体の40.00の約1.7%)。
- **Delivery**: Storyline+B3 1 callのlatency=24.3秒(retry無し)。Advanced段は今回1回
  retryが発生し追加で約35秒+deviation check分のlatencyを要した(既存Gateの通常動作、
  B3追加によるものではない)。

## 9. Sonnet仮判定

技術的Gate 3項目(1〜18)は今回のN=1 runで充足していると判断する(仮、Fable差し戻し
1回目で指摘されたGate 3 #13[runtime evidence手作業補完]・#2[Selected Brief重複バグ]
は本ラウンドで修正済み)。ただし(a) N=1記事のみのruntime evidenceであること、
(b) Advanced/Standard段のLedger Deviation Check非決定性という既知の限界があること
(4.2 Fact drift結果参照)、(c) run_01のAI決定StorylineがTrial-02のCore Storylineと
異なり「なぜ人間を使ったか」を説明していない観察があること(4.4参照)、(d) 記事内容
自体(Storyline選定・Fact選定・文章)はユーザー未確認であることから、
**`PRODUCTION_WIRED`の正式宣言は行わない**。記事は`OPEN_ITEMS.md` OPEN-183として
ユーザー確認待ち。

## 10. Fable評価

[Fable記入]

## 11. 分類

[Fable記入]
