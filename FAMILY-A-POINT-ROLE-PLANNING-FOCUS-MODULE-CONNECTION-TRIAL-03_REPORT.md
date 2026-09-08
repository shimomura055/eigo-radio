# FAMILY-A-POINT-ROLE-PLANNING-FOCUS-MODULE-CONNECTION-TRIAL-03 報告書

管理ID: FAMILY-A-POINT-ROLE-PLANNING-FOCUS-MODULE-CONNECTION-TRIAL-03(Lane A)。
**Trial(接続設計の検証)。Production/Prompt/SSOT編集・Git操作は一切行って
いない。monkeypatch・グローバル書き換えなし。TTSは実行していない。**
並列稼働中のLane B(`er012_*`、`er003_v1_n3_01_articles_generate.py`辞書1行
配線)・Lane B Fact帰属Trialの成果物は参照していない。`docs/pm/ACTIVE_TASK.md`
/`RESULT_PACKET.md`は編集していない。

ユーザー決定根拠: 2026-09-09 A-UDR-11(`FAMILY-A-DAILY-NEWS-FOCUS-LAYER-
COMPARISON-TRIAL-02_REPORT.md`§3観察3で判明した「Point Role Planningへ
`editorial_type_module_block`が届いていない」問題の接続設計を検証する。
最大Status=VALIDATED、USER_DECISION_REQUIRED発生時はSTOP)。

新規ファイル(いずれもTrial、Production未編集):
- `er011_point_role_planning_focus_connection_trial_03.py`
- `er011_point_role_planning_focus_connection_trial_03_cost_compute.py`
- `er011_output/point_role_planning_focus_connection_trial_03/`(生成物一式)

---

## 1. 経路の途切れ箇所(呼び出しチェーン)

```
run_writer_for_theme (er006_pool_pilot_01_writer.py 28-111行)
  -> gen.resolve_editorial_type_module_block(editorial_mode) -> EB
  -> gen.build_common_block(..., editorial_type_module_block=EB)
       EBはCOMMON_BLOCK_TEMPLATE内{editorial_type_module_block}へ挿入
  -> gen.build_prompt(common_block, instruction) -> prompt(EB含む)
  -> gen.run_one_pattern(client, theme_id, label, prompt, ...)
       ※シグネチャにEBを渡す引数が無い。promptという「焼き込み済み文字列」
       としてのみEBが渡る
       -> point_planning.run_point_role_planning(client, topic,
          verified_ledger_text, model, reasoning_effort)
            **途切れ箇所**。topicとverified_ledger_textしか受け取らず、
            EBを一切参照しない(er011_point_role_value_planning_01.py
            124-145行、ROLE_PLANNING_PROMPT_TEMPLATE 72-117行にEB用
            placeholderが存在しない)
       -> point_planning.build_role_planning_block(role_plan_result)
       -> gen._generate_and_compress_article(..., prompt_with_plan, ...)
```

EB自体は最終Writer本文生成promptには届くが、Point One/Twoの「役割」を計画
する専用LLM呼び出し(Point Role Planning)はEBを一切知らないまま独立に役割
を決め、その計画がWriterへ強い指示として追記されるため、EBが要求する役割
優先順位(major_daily_newsのmechanism/beyond-the-headline factor/
limitation)がPoint Role Planningの決定に反映されない。

Diagnostic Full Retry(Point Overlap/Value QA NG時、最大2回)はPoint Role
Planningを毎回再実行するため同じ接続が必要。Local Rewrite Loop(Ledger
Deviation MAJOR時の局所文修正)はPoint Role Planningを再実行しないため
対象外。Human Review再生成は内部的に`run_one_pattern`を最初から再度呼ぶ
だけで独立経路が無いため、初回経路の接続修正で自動的にカバーされる。

---

## 2. 設計案比較

単一の接続メカニズム(`run_point_role_planning`へ新規optional引数
`point_role_hint_block`(既定`""`)を追加し、Role Planning prompt内
「【Verified Fact Ledger】...」と「Point One・Point Twoそれぞれについて」の
間へ挿入。既定`""`ならバイト単位で production版と完全同一)を実装し、渡す
内容だけで案を切り替えた。

| 観点 | (a) Focus Module直接注入 | (b) Mode別Point Role候補リスト(推奨) | (c) 併用 |
|---|---|---|---|
| 後方互換(既定値でバイト不変) | Yes | Yes | Yes |
| Trend Synthesis非影響 | Yes(hint=""で不変維持可) | Yes | Yes |
| Diagnostic Full Retryでの引き継ぎ | Yes(同じ引数を渡すだけ) | Yes | Yes |
| Dangling Reference | なし | なし(EDITORIAL_TYPE_MODULE_BLOCKS辞書と独立) | なし |
| 実装規模 | 最小 | 最小+新規hint定数1個 | 最小+新規hint定数1個 |
| Role Planning promptの長さ/ノイズ | 大(Focus Module全文、Main Story向けの長い指示が混入) | 小(役割候補のみの短文、schema呼び出しの性質に合う) | 最大 |
| 意味的整合性 | Main Storyと同一文言だが目的外指示(engagement等)も混入し得る | Role Planningの出力項目(role)に直接対応する情報のみ | 両方の利点、費用微増 |

**推奨: (b)**。Role Planningは6項目のJSON schema出力に特化した小さい呼び
出しであり、Main Story向けの長いnarrative指示をそのまま混入させるより、
役割候補という直接対応する情報だけを渡す方がノイズが少ない。(c)は安全側
に振れるが費用・prompt長が増えるため、(b)単独の効果が不十分な場合の拡張
候補として温存する。

---

## 3. Trial実装(Production無変更)

`er011_point_role_planning_focus_connection_trial_03.py`。

- **import・無変更で再利用**: `er003_v1_n3_01_articles_generate`(`prod_gen`)
  の`build_common_block`/`build_prompt`/`resolve_editorial_type_module_block`
  /内部helper(`_generate_and_compress_article`/`compute_metrics`/
  `run_point_overlap_qa_and_regenerate`等)、`er011_point_role_value_
  planning_01`(`point_planning`)の`build_role_planning_block`/
  `run_point_value_qa`/JSON schema/例外クラス、他依存モジュール一式。
  `er011_daily_news_focus_layer_comparison_trial_02`(既存VALIDATED
  Trial)の`MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK`もそのままimport。
- **コピー・改変(Trial限定)**: `run_one_pattern_connected`
  (`er003_v1_n3_01_articles_generate.run_one_pattern`809-1214行のコピー、
  変更点は関数名・新規引数`point_role_hint_block`追加・Point Role Planning
  呼び出し2箇所の置換・bare参照への`prod_gen.`修飾のみ)、
  `run_point_role_planning_connected`+`ROLE_PLANNING_PROMPT_TEMPLATE_
  CONNECTED`(`er011_point_role_value_planning_01.run_point_role_planning`
  124-145行+`ROLE_PLANNING_PROMPT_TEMPLATE`72-117行のコピー、変更点は
  新規placeholder追加のみ)。

**単体テスト(APIなし、3件、いずれもPASS)**:
- `test_default_hint_is_byte_identical_to_production`: `point_role_hint_
  block=""`時、Trial版templateの出力(1239文字)がproduction版
  `point_planning.ROLE_PLANNING_PROMPT_TEMPLATE`の出力(1239文字)と
  **バイト単位で完全一致**。
- `test_trend_synthesis_unaffected_when_hint_empty`: Trend Synthesis
  相当でも`point_role_hint_block=""`のままならRole Planning promptは
  production既存運用とバイト一致(併せて`build_common_block`が
  `editorial_mode="trend_synthesis"`指定時のみ差分を持つ既存挙動も再確認)。
- `test_option_a_hint_equals_editorial_type_module_block`: 案(a)が同一
  接続メカニズムで実現できることを確認。

---

## 4. 最小runtime検証(推奨案(b)、major_daily_news相当、Hanshin Ledger固定)

`point_role_hint_block`へ、Trial-02のFocus Module本文が既に言及する
「mechanism/beyond-the-headline factor/limitation」をそのまま転記した
短文(`MAJOR_DAILY_NEWS_POINT_ROLE_HINT_BLOCK`)を渡し、A2/B1B各1本を生成
(TTSなし、text-onlyまで)。

| | B1B | A2 |
|---|---|---|
| status | **OK** | NG_REVIEW_REQUIRED(Point Two overlap 2/2上限到達) |
| fact_verdict | PASS | (未到達) |
| ledger_status | LEDGER_COMPLIANT(deviation 0) | (未到達) |
| directional_fact_precheck | PASS | (未到達) |
| retry回数 | 1/2 | 2/2 |

**Point Role Planning出力への反映(役割候補が実際に反映されたか)**:
B1B・A2いずれも、最終採用されたrole文言が候補セットの語彙をほぼそのまま
反映した:
- B1B: Point One role = "the specific late-offense **mechanism**"、
  Point Two role = "distinguish Hiroshima's isolated scoring... **while
  clarifying what the game record does not establish**"(limitation)
- A2: Point One role = "An additional **contributing factor beyond the
  headline** is Hanshin's late offensive depth"、Point Two role =
  "The outcome **mechanism** was not just Hanshin's scoring but the
  containment of Hiroshima's offense"

生成された記事本文もこれと一致(B1B見出し: "More than one hitter finished
the job" / "Hiroshima's response stayed narrow"、本文に"stopping short of
saying what the players felt"というlimitation表現あり)。**接続は意図どおり
機能した**(Point Role Planningの決定に、Focus Moduleが示す役割優先順位が
反映された)。

**A2のNG_REVIEW_REQUIREDについて**: Point Two(limitation役、Ihara/five
innings/Montero語彙)がMain Storyと語彙的に重複し2回のDiagnostic Full
Retryでも解消せず。これはTrial-02のA2 focus条件でも同じ語彙クラスタで観測
済みの既存パターンであり、既存の安全装置(Point-only regeneration無効化、
retry上限2回)がそのまま作動しただけで、本Trialが新たに発生させた失敗
モードではない。役割接続自体の成否とは別軸の既知の残存論点として記録する
(A-UDR-13の対象、本Trialでは混同しない)。

費用: ¥12.0(実測、22 calls、`er011_output/point_role_planning_focus_
connection_trial_03/cost_summary.json`)。上限¥40以内。

---

## 5. Trend Synthesis非影響の確認

推奨案(b)を`editorial_mode="trend_synthesis"`相当で通す場合、本Trialでは
`point_role_hint_block=""`(空、A-UDR-11付随決定どおり不変維持)とする。
§3のunit testで、この場合のRole Planning promptがproduction既存Trend
Synthesis運用時のものとバイト一致することを確認済み(Trend側のLLM実行は
実施していない)。

---

## 6. Gate 4 / Gate 1分類 / Production配線案(実装しない)

**Gate 4**: PASS。Trial-only仕様への依存なし、Production関数(`build_
common_block`/`build_prompt`/`resolve_editorial_type_module_block`/
`EDITORIAL_TYPE_MODULE_BLOCKS`/`run_point_role_planning`本体/
`ROLE_PLANNING_PROMPT_TEMPLATE`本体)は無編集(grep差分なし、import
only)。コピーした2関数の変更範囲・理由は§3に明記。monkeypatch・
グローバル書き換えなし。Lane B成果物は参照していない。

**Gate 1分類: VALIDATED**(接続設計(b)が既定値バイト不変・Trend
Synthesis不変・retry経路引き継ぎ・Dangling Referenceなしの全条件を満たし、
runtime検証でPoint Role Planning出力への反映を確認できたため)。ただし
A2の既存overlap論点(§4)は本Trial範囲外の別課題として残る。

**Production配線案(実装しない、次段階でのユーザー判断用)**:
- `er003_v1_n3_01_articles_generate.py`: `ROLE_PLANNING_PROMPT_TEMPLATE`
  へ`{point_role_hint_block}`placeholder追加、`run_point_role_planning`
  (`er011_point_role_value_planning_01.py`)へ同名引数追加、`run_one_
  pattern`のシグネチャへ`point_role_hint_block: str = ""`追加、2箇所の
  呼び出しへ引き継ぎ。
- `er006_pool_pilot_01_writer.py`: `run_writer_for_theme`に、`editorial_
  type_module_block`解決時と対で`point_role_hint_block`をmode別に解決
  する仕組み(例: 新規`POINT_ROLE_HINT_BLOCKS`辞書、fail-closed)を追加し、
  `run_one_pattern`呼び出しへ引き継ぐ。
- 回帰テスト案: (1) 既定値(mode=None)でbaseline記事のprompt/出力が既存と
  バイト一致すること、(2) `editorial_mode="trend_synthesis"`時に新規
  hintが空のままRole Planning promptが既存と一致すること、(3) `major_
  daily_news`相当を新規登録する場合のみ、本Trialのrole反映結果を再現
  できること。

---

## 7. 費用・新規ファイル一覧

- 費用: ¥12.0(実測、上限¥40以内)。TTS/ASR未実行。
- 新規ファイル: `er011_point_role_planning_focus_connection_trial_03.py`、
  `er011_point_role_planning_focus_connection_trial_03_cost_compute.py`、
  `er011_output/point_role_planning_focus_connection_trial_03/`(unit_test_
  results.json、raw_usage_log.jsonl、cost_summary.json、connected/{a2,b1b}
  以下の生成物一式)。
- `FAMILY-A-POINT-ROLE-PLANNING-FOCUS-MODULE-CONNECTION-TRIAL-03_REPORT.md`
  (本ファイル)。

Git操作・Production/Prompt/SSOT編集は一切行っていない。
