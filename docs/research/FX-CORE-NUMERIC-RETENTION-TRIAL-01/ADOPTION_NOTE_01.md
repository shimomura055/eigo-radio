# ADOPTION_NOTE_01 (Production採用する場合の必要作業・影響範囲。**未承認・参考**。Trial結果は`TRIAL_RESULT_01.md`。委任_03で更新、2026-10-25)

Status(Sonnet所見): 採用判断前。月・コーヒー型(数値が答えの記事)では事前登録基準を満たしたが、ig_nobel型(B3がStorylineに数値を入れない記事)では必要数値を守れない(`PHASE2_RESULT_01.md`)。以下は「採用する場合」に必要になる作業の整理であり、採用推奨ではない。

## 1. 変更が必要になるファイル(Family X専用。Z/Yは到達させない)
| 機能 | 変更候補ファイル | 分類 |
|---|---|---|
| **B3追記ブロックv2**(Storylineに『答えそのものの値』<=2。比較相手は言葉で。`er115.B3_ADDENDUM_V2`) | `er019_family_x_storyline_b3_fact_selection_01.py`(`USER_PROMPT_TEMPLATE`の追記)またはrunnerのextra_note | J1: B3 Promptの意味的変更=ユーザー承認事項 |
| M1検査(Storyline数値の検証・B3再実行1回)・E導出(`derive_E`) | 新module+`er019_family_x_entertainment_production_runner_01.py`のB3段後 | 新規 |
| **印の付け替えO-2'**(E非空のとき、非Eで同単位系の中核数値を【周辺数値】へ。`plan_o2prime`/`swap_marks`/`filter_overlay`) | `er053_family_x_factlock_ja_writer_01.py`の`run_w1_writer`(news欄/Facts文字列のメモリ上のみ。注記済みB3ファイル・manifest shaは不変) | **規則5の運用変更**(中核数値=Writerが使ってよい、に『E非空なら同単位系の非Eは使わない』が加わる)=ユーザー承認事項。`derive_ranks`・規則5の文言は変更不要 |
| 範囲値正規化(入力側R4) | `er053_family_x_factlock_ja_writer_01.py`の`run_w1_writer`(ニュース欄・テーマ行) | J2(承認済み規則同士の矛盾の是正) |
| 範囲値正規化(**出力側**R1/R2) | `er053_family_x_factlock_ja_writer_01.py`の`astra_stage` | J2: **Gateより前の決定論の後処理だが正本のR1/R2本文を書き換える**(`normalize_tilde_placeholder_ja`はTTS用の使い捨てコピーのみ)。Opus条件付き安全判断(`OPUS_REVIEW_02.md` (c))。Production採用時は条件A/Cの再レビュー+ユーザー承認。記号QAのSTOPを避けるため必須(実測)。**採用しない場合でも下記OPEN(別件)の欠陥は残る** |
| 保持Gate(R0/R1/R2)・段限定再実行・STOP | `er053_family_x_factlock_ja_writer_01.py` | J3: STOP→HRの既定をユーザー判断 |
| **新規数値検出M2**(R1/R2出力のうちR0本文・ニュース欄に無い数値。`new_numbers`) | 同上 | 保持Gateと同じ再実行枠(1回)を共有、解消しなければSTOP。LLM追加call 0 |
| 較正済み照合・単位言い換え表 | 新module(`match_core`/`dimension_of`) | 新規 |
| 計測(選定数/必要数/掲載数/不要数/付け替え掲載/新規数値) | `er114`/`er115` | 運用ツール |
| CURRENT_SPEC.md / DECISION_LOG.md / OPEN_ITEMS.md | 規則5(許可のみ→Eは必須、E非空なら同単位系の非Eは周辺扱い)、B3契約、範囲値規則 | ドキュメント |
- **撤退(revert)**: 上記は追記型・flag/既定OFF(採用時は単一flag読取関数)で、OFF時にProductionと入力バイト一致(`test_o2prime_off_is_byte_identical_and_writes_nothing`等)を保つ設計。撤退は`git revert`で済み、既存公開記事は不変(再生成しない限り)。

## 2. 影響範囲・確認事項
- B3 PromptファイルはFamily Xの名前だがY Trial(`er036_family_y_voice_structure_trial_01.py:33`ほか)から多数importされている(Opus所見)。Productionに入れる場合は、Y/ZのProduction経路が`USER_PROMPT_TEMPLATE`/`selected_storyline`を使っていないことのGrepをIsolation testに含める。
- 月のProduction再実行は採用判断後(未承認)。
- Isolation test(採用時): (a)OFF時`build_r0_prompt`バイト一致、(b)Z/Yのimport・参照0のGrep、(c)flag未設定でAPI呼出0・出力不変(DefaultOffIsolation型)、(d)起動script/.envで暗黙にONにしない、(e)O-2'がOFF時にnews欄を変更しない・ON時もB3注記ファイルのshaが不変。
- 量産単価増分: `TRIAL_RESULT_01.md` 委任_03更新 §4(点推定0円、保守的上限約6〜7円/記事)。HR増加量はSTOP率(Phase 1/1b/2のGate由来STOP 0/8チェーン)。
- **X専用の確認**: Family Z(英語学習解説)・Yの経路にB3追記・E・Gate・O-2'を到達させない。

## 3. 採用前に残る課題(委任_03結果より)
1. **Storylineが数値を要さない記事型(ig_nobel型)**: B3が4/4標本でStorylineに数値を入れず、E=∅で必要数『3倍超』が最終本文から欠落した(現行版にはあった)。選択肢: (a)R5案=B3 JSONに`answer_numbers`欄を追加、(b)Storyline数値が空のときにFact見出し数値を決定論で選ぶ(重複選定システム化のリスク)、(c)この記事型は対象外として限定採用+ユーザーに必要数値の範囲を確認。いずれも新仕様(未Trial)。
2. O-2'は単位系で一律に下げる鈍い規則(任意の長さ系数値も下がる。月・コーヒーでは必要数に影響なし)。比較が答えの記事は、B3がStorylineに比較の2値を入れたとき(coffee p3)に両方Eに入り救われたが、B3がどちらか1つしか入れなかった場合の副作用は未検証(coffee p2はE=∅)。
3. n小(フルチェーン8本、B3 15本、記事は月・コーヒー・イグ・ノーベル賞。semiconductor_earningsは未実施)。
4. 範囲値の波ダッシュ欠陥はProduction既存問題(OPEN別件)。J2採用の有無と独立にユーザー判断対象。

## 4. 【委任_04追記】R5(`reader_must_hear_numbers`欄)を採用する場合の必要作業(**未承認・参考**。詳細`DESIGN_04.md`)
- B3 schema変更: `er019_family_x_storyline_b3_fact_selection_01.py`の`STORYLINE_B3_JSON_SCHEMA`に`reader_must_hear_numbers`(配列、required)を追加+`validate_selection_output`・出力保存(`fact_selection_evidence.json`)・USER_PROMPT_TEMPLATEの追加指示(v4文)=**Production B3の意味的変更(J1、ユーザー承認事項)**。Opus条件C(Production採用提案前)。Y Trialが同moduleをimportしているため、Y/Zへ到達しないことのGrep・Isolation testが必要。
- E導出: `derive_E_r5`(欄→従来M1と同じ写像規則)をrunnerのB3段後へ。欄とStorylineの不一致=欄優先・記録のみ(事前登録)。
- Writer契約: 現状は【中核数値】印・保持Gate・O-2'のみでR0 Promptは不変。ig_nobelでは欄の数値がR0初稿に自然に入った(Gate発火0)が、保証ではなくGate(R0/R1/R2直後の決定論検査+既存の再生成枠)が最終防御。
- X専用・既定OFFの単一flag・撤退=revert。月のProduction再実行は採用判断後。
- **採用前の未解決**: (1)過剰選定(semi: 実績+見通しの対を欄に入れ事前登録表で不要+1、1標本)の再現性と対策(指示文の追加修正は未実施・見込みは中)、(2)月・コーヒーのR5回帰(未実施)、(3)B3のFact選定が標本ごとに変わるため必須/不要の判定基準が記事構成に依存する点の運用定義(ユーザー判断候補)、(4)n小(R5 B3 6本、チェーン2本)。

## 5. 【委任_05追記・Closeout】Production採用する場合の設計・受入条件案・量産単価(**未承認・参考**。Trial結果=`PHASE4_RESULT_01.md`・`TRIAL_RESULT_01.md`)
Status候補=VALIDATED(Sonnet所見、最終Fable)。ユーザー正式承認なしにProductionへ配線しない。
### 5-1. 量産単価増分(実測ベース、n小)
- 追加LLM call 0。B3の出力フィールド追加によるトークン増はほぼ検出不能(v4のB3再実行なし時: 8.1〜12.9円、委任_03のv2平均10.9円・Production参照12.07円と同水準)。chain(R0〜EN)は標本11〜13円(委任_03のB/s1 12.1円と同等)。
- 増分の主因=**M1によるB3再実行**: v4の全9標本(r5b1,r5b2,r5s2,r6×6)で3/9(半導体2/2が1回目に217億ドルを欄へ、コーヒー1本が周辺数値0.6%)。1回あたり約13円 → 期待増分=3/9×約13円≒**約4円/記事**(95%信頼幅は広い。0〜約8円)。70円目標に対し約6%。保持Gate再生成(R0〜R2)は9標本中0。
- 改善余地(Prompt変更を伴うため別承認): 半導体で1回目に217億ドル(見通し側の値)を欄へ入れる傾向への対策(v4の『比較の相手側の値は入れない』の強調等)はM1再実行を減らす可能性があるが、今回は指示文を触らない方針(ユーザー原文§6)のため未実施。
### 5-2. 採用時の設計(要素と役割。実装は未承認)
1. **B3 schemaの欄追加**(`reader_must_hear_numbers`、<=2、空可)+v4指示文(5観点の整理版、記事固有語なし)。
2. **E=欄**(従来Storyline由来から変更)。欄とStorylineの不一致は欄優先・記録のみ。
3. **保持Gate**(R0/R1/R2直後の決定論検査、不足時は既存の再生成枠で1回)。今回の再生成発動0。
4. **O-2'**(Eと同単位系の非E中核数値を周辺扱い、本文に出さない)。今回の発動: 月1/2(750)、コーヒー2本中c1(3%)・c2(8.7%)、半導体2/2(54%)。
5. **M2**(R1/R2の新規数値検出)。今回の新規数値0。
6. **J2**(範囲値の波ダッシュ出力側正規化)。OPEN-509(ユーザー判断要、UDR #195のまま)に依存。DEVのみ継続。
7. **M1**(欄の周辺数値検査+B3再実行1回)。B3の1回目の過剰選定の是正に実際に効いた(6本中3本)。
### 5-3. Production配線時の受入条件案(新仕様のためユーザー判断)
(1)B3 Prompt/schema/Writer契約の変更範囲をFamily X専用に限定し、Z/Yへ到達させない。(2)単一flag・既定OFF・DefaultOffIsolation test(flag未設定でAPI呼出0・出力不変)。(3)導入後の最初の数記事で、欄の数値・保持・不要数値・文章をFableが全文で確認(固定表の合否ではなく切り口基準)。(4)B3再実行率・費用増の実績を記録し、約8円/記事を超える場合は再評価。(5)Opus条件C(Production採用提案前)のレビュー。
### 5-4. Opus条件C依頼書の骨子
- 論点: 方式のProduction採用の可否(B3 schema変更・E=欄・Gate/O-2'/M2/J2の配線)。根拠=`TRIAL_RESULT_01.md`(委任_05更新)、`PHASE4_RESULT_01.md`、`COMPARISON_05.md`。
- 観点: (a)欄の必要性判断がB3 LLMの毎回の判断に依存する(固定規則でない)ことの品質リスク、(b)M1再実行に依存した是正が効かないケース(見通し値が選定Factの核数値)の残存、(c)J2/OPEN-509の扱い、(d)n=型あたり1〜2の統計的な弱さ、(e)ZやYへの波及なしの確認、(f)撤退条件(revert単位)。
- 不要例: 文章の表現調整、Writer Promptの全面変更。
