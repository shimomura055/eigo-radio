FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-PN-委任_02-TRIAL-IMPL-VERIFY-20261023

# 委任_02(①固有名詞): Opus条件Aレビュー反映→Run Entity Table(RET)のDEV/Trial実装→検証SC-1〜9(+修正)→自律改善ループ→Fable評価資料。Production/Prompt/flag/閾値/Ledger変更0。API費用上限30円(NER gpt-6-luna、理由・出典記録)。

## 前提読込
`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/{ROOT_CAUSE_01,DESIGN_01,OPUS_REVIEW_REQUEST_01}.md`、`docs/pm/RESULT_PACKET_ASRQ_PN1.md`、ユーザー原文 `docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER.md`(§3自律改善ループ・§4①受入条件・§5境界)。

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_PN_委任_02.md`(index 347以降、先頭MARKER一致)。
2. **Opusレビュー本文を保存**: 下記所見を `docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/OPUS_REVIEW_01.md` に保存(Fable転記と明記)。
3. ACTIVE_TASK自分の行のみ(並行: ②UKUS agent=Trial実装中。同dirの `UKUS/` と `er111_ukus_*` は触らない)。OPEN_ITEMS: 仮ID `OPEN-ASRQ-PN` を正式採番(git status→再Grep→②側が採番済みならその次番号→自分の行のみ即commit)。Perplexity 401は別OPEN行(基盤不全、環境確認=ユーザー/運営)として起票。

## Fable判定(記録用)
Opus総合判定=「必須修正後にTrial実装可、再設計不要」。方向は実質一致(RC-1〜4、RET、受理境界不変、P-02残置、Iran/Mark型ブロック維持、音素ゲート不採用、HR Lock済み4clipは採用後再生成)。対立点4つ(2シグナルの実態=LLM単独/集合ではなく出現位置に紐づけ/SC-5 parityはトートロジー/作品名中の低頻度一般語)はいずれも誤PASS防止の技術修正でProduct原則変更ではない→**Fable判断でTrial実装へ進む**。区分: LLM NER新証拠源+G3変更は「新仕様候補」(Opus OF-PN2-12)として扱い、採用はユーザー判断(VALIDATED止まり)。RET-3は11-7限定例外の対象外になる可能性が高い(将来は VALIDATED→ユーザー正式採用→Production実装の経路)。

## Opus所見(逐語要約)
- OF-PN2-01[必須] 証拠は語の集合(bag)でなく「実体の出現位置」に紐づける。`ledger_surface_tokens`(er103:697-712)は語集合化するため複数語実体中の一般語(Will/University/Said)が記事全体で証拠化し、固有名詞混在句のdiffやRET-3で通る。修正: (i)表から証拠を付けるのは非一般語tokenと実体内部イニシャルのみ (ii)Primary diffのcanonical句が当該segmentのcanonical_text内の実体出現範囲に連続して含まれる場合のみ証拠付与 (iii)実体がそのsegmentに出現しなければ証拠なし。
- OF-PN2-02[必須] RET-3厳密化: 現行G3(er103:358-366)は `c_set & noun_tokens` 交差条件。語集合判定だと別実体tokenの偶然隣接(`Reicher will`→`riker well`)を通す。Secondary合成spanは `by_canon_s` に入らずP-03(:394-397)を経由しない。修正: (i)Secondary spanが当該位置で連続する1実体出現(または区切り語なし隣接複数実体)とtoken単位一致 (ii)spanがPrimary diffの固有名詞tokenを全て含む (iii)合成spanにも `_noun_checks` とP-03適用。負例test: 隣接実体の一般語token、機能語(the/and)巻き込み、数値・否定語巻き込み、`melos drank`。補足: C類16件中10件は同一segment(pool_n5_cafes L. Mimoun)再試行で実質母数は数件。
- OF-PN2-03[必須] 「2シグナル」の実態: confirmed=「LLM∧大文字一貫性∧決定論大文字出現」だが後2つは独立でない(1回出現語は必ず真)→Bertie型は実質LLM単独。修正: 独立裏付けなし(宣言なし・文中大文字なし・CMU収録)のentryは、2回の独立call(prompt変更or温度違い)一致時のみconfirmed。Std/Adv統合1callなら計2callで≤0.1円。記述も実態に合わせる。
- OF-PN2-04[必須] 作品名・スローガン・一般名詞句中の低頻度一般語(The Crimson Petal の petal→pedal)を証拠化しない。修正: CMU収録tokenに表証拠を付けるカテゴリは person/place/organization のみ。work_title/other_named はCMU未収録tokenのみ(=cmu_oov同等)。brand_product はCMU収録可だがSC-3で別集計。
- OF-PN2-05[必須] 表の入力は「実際にTTSへ渡るsegment canonical textの和集合」(対象roleはPREVIEW/TOPIC_INTRO/IN_ONE_LINE/COMMENT含む er103:89、canonicalは供給後tts_input er019:353-358)。planの対象role(KP/JA/HEADING除外)全canonicalの和集合にNER、逐語検証はsegmentごとに供給前後の両textで、正規化ずれ(引用符向き・数字展開)をtest固定。
- OF-PN2-06[必須] 継承再判定(er019:349-366→er103:724 正式Ledgerのみ)とLocal Rewriteで揺れない設計: 表sha不一致で表なし(DESIGN_01:48)だとLR毎に他segmentの受理が戻り再生成費用発生。修正: (i)アラームblockに受理に使った実体entry(surface/tokens/category/grade)を保存し、再判定ではそのsegment textへの逐語出現のみ確認して再利用(表sha一致不要) (ii)LRでは表を作り直さず変更segmentのみNERして和集合に追加(減らない) (iii)再判定経路ではLLMを呼ばない。SCに追加。
- OF-PN2-07[必須] SC-5 parityはトートロジー(誤PASS証明にならない)。SC-5は実装同値testとして残し、別に「D1で新規受理となった全件+Stage 2実誤読データ(複数ASRが揃って別語)を人がadjudication→意味が変わる受理・一般語誤読受理=0」をSCに。SC-2 recallは表が実際に必要な層(CMU収録・非一般語・文中大文字なし)で層別≥0.90。SC-4はユニーク(text,名前)単位も併記。SC-9にJaccardに加え「3回構築の和集合でも非固有名詞への証拠付与0」。
- OF-PN2-08[推奨] 「区別」は関門でなくアラームのラベル(音素距離帯/P・S両ASRが同じ別語か/ASR語zipf 3.5〜4.0境界付近)で応え試聴優先度に使う。カテゴリ別閾値は入れない。wordfreq version固定、境界付近受理を集計。
- OF-PN2-09[推奨] (i)X英語出典メタデータ(記事題名・人名)が保存されていれば宣言型R2として使う (ii)R_GENERAL_WORDで止まった person/place を件数記録 (iii)日本語由来ローマ字名はOOV処理で可、Tokyo/Japan等は許容 (iv)小文字始まりブランド(iPhone/eBay)は対象外と明記 (v)KP/ja_readingはG0除外で問題なし。
- OF-PN2-10[推奨] Std/Adv統合1call(2call合意でも約0.06円)。構築は脚本確定直後に並行。run単位保持は `_RUN_SCOPE` 同様process内状態、finallyで必ず解除。
- OF-PN2-11[推奨] TrialでG3を複製する場合はer103該当関数sourceのhash照合drift guard test。`evaluate_alarm_eligibility` は `enabled=True` 明示・scope未設定(er103:319-322)。将来配線: RET-2は11-7限定例外可、RET-3は既存G3直接変更で対象外の可能性→VALIDATED→ユーザー採用→Production実装経路。②UKUSとの境界整合、表共有は読み取りのみ。
- OF-PN2-12[情報] Stage 2 REJECTEDは「発音正否判定方式」で本案と矛盾なし。新規受理の多くは実誤読がアラーム付き受理になる→承認済み方針範囲内であることを最終報告で明示。P-02縮小せず同意。HR Lock済み4clipは採用後再生成。NG_BOTH起点の再評価拡張はHR Lock解除を伴う仕様変更で先送り同意。Perplexity 401は別OPEN追跡。
- OF-PN2-13[情報] 費用0.05〜0.1円/記事セット。Std/Adv統合が最も効果大。モデル比較はSC-3/SC-9達成を条件に。

## 1. 設計更新
`DESIGN_02.md`(OF反映差分表、SC改訂版、2シグナル→「独立裏付けまたは2call合意」へ記述修正、カテゴリ別規則、位置紐づけ、OF-06の保存/再利用設計、将来配線区分)。

## 2. Trial実装(DEV専用)
- `er111_pn_entity_table_trial_01.py`(構築: 決定論スキャン+Z Seed key_roles/STORY_MAIN_CHARACTER宣言+LLM NER[gpt-6-luna、Std/Adv統合1call+独立裏付けなしentryは2call目で合意]+逐語検証[供給前後]+題名/長句除去+カテゴリ規則+格付け)、`er111_pn_trial_evaluate_01.py`(Trial用wrapper: 位置紐づけ証拠付与→`evaluate_alarm_eligibility(enabled=True)`、RET-3厳密版はG3複製+drift guard)、test `er111_pn_entity_table_trial_01_test_01.py`(負例含む)。
- er103/er006/er019/val/runner無変更、import方向はTrial→Productionのみ、AST testで正式経路からの未参照を固定。11-7 flagは作らない。
- アラームラベル(OF-08)を表示用に付与(受理境界は不変)。

## 3. 検証(SC-1〜9改訂版)。結果json・集計mdを `TRIAL_01/`
- データ: HR queue 88(現行Ledger/Ledger全除外)、保存4,032ペア(英語3,041)、本文22本+直近X/Z run(『開いた窓』run_sf_prod_01のcanonical/保存転写含む=API 0でBertie c14/part3_c2のStd/Adv 4clipが対策後に受理となるか)、合成コーパス(カテゴリ別: person/place/organization/brand/work_title、Bertie型=CMU収録人名×文頭/引用直後、負例=文頭一般語/題名/一般名詞句/`petal→pedal`型実誤読)、失敗注入(LLM失敗・timeout・不正JSON)。
- adjudication(OF-07): 新規受理全件を一覧化し、Fableが最終目視できるよう canonical/Primary/Secondary/カテゴリ/ラベル を表にする(Sonnetの一次分類+根拠)。
- **自律改善ループ**: SC未達なら原因分析→宣言源拡充/2回目call設計/カテゴリ限定の順で前提から見直し→再検証。`ITERATION_LOG_01.md` に反復ごとの変更・改善・未達を記録。見込みがなくなった場合のみ停止報告。

## 4. Fable評価資料
`TRIAL_RESULT_01.md`: 最終報告9項目のうち①の1〜7を数値で(改善前後比較はHR queue再評価の表、新規受理のadjudication結果、残存リスク=zipf境界依存/pron_differs相当/実誤読のアラーム付き受理が方針範囲内である説明、X/Z適用範囲、費用・時間)。VALIDATED自己宣言はしない。

## 5. SSOT・Git
OPEN行Status、DECISION_LOG(Fable判断: Opus反映→Trial実装、新仕様候補区分)、REPORT_LEDGER。明示add、secret_scan hits=0、`git push origin HEAD:main`。全回帰は最後に単独実行し分類。

## 6. 禁止
Production/Prompt/flag/閾値/Ledger/golden変更、`upsert`/`--apply`、HR Lock解除、run_sf_prod_01のstage実行・音声変更、TTS実行、②UKUS側ファイル編集、API上限30円超過、VALIDATED自己宣言。

## 7. 報告(docs/pm/RESULT_PACKET_ASRQ_PN2.md)
(1)OF反映状況表 (2)実装構成 (3)SC-1〜9結果表(基準/実測/判定) (4)『開いた窓』4clipの机上再判定 (5)新規受理adjudication要約 (6)反復履歴 (7)残存リスク (8)費用(出典)・時間 (9)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。