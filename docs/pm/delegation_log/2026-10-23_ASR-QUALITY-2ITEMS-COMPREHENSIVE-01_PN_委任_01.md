FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-PN-委任_01-ROOTCAUSE-DESIGN-20261023

# 委任_01(①固有名詞): 原因究明+包括対策設計(Opusレビュー前まで)。read-only+設計文書。Production/Prompt/flag変更0。API費用0(必要なら≤10円、理由記録)。

## 背景(ユーザー新指示、2026-10-23)
ユーザーは『開いた窓』の `Bertie→Birdie` HR Lockについて「個別の台帳登録で済ませる問題ではない。固有名詞を認識・分類する仕組み自体を根本から見直す」と指示。Scope=原因究明・包括対策設計・Opusレビュー・Trial実装・反復検証・Fable独立評価まで(VALIDATED止まり、Production配線未承認)。Family X/Z共通適用。Trial回数で止めない自律改善ループ。『開いた窓』停止中音声は保全し、個別登録はしない。詳細は原文を保存して読むこと(下記T-0)。並行して②英米綴り(別agent、管理ID ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-UKUS)が走る。

## T-0
1. **ユーザー指示原文を逐語保存**: 本セッションjsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl` の最新 user メッセージ(「# Claude Code / Fableへの指示 ## ASR品質問題2件の根本対策 — 原因究明・包括改善・反復Trial」で始まる)を `docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER.md` へ保存(extractツールの `--role user` 相当、無ければjsonlから該当textを抜き出す。改変禁止)。②agentも参照するので最初にcommit/push。
2. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <同jsonl> --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_PN_委任_01.md`(直近保存index 340=FZSF委任_06、その後4〜5件。先頭MARKER一致で特定)。
3. ACTIVE_TASK.md: 並行agent(FAMILY-X-NEWS-2ARTICLES-E2E-02 委任_02、FAMILY-Y 委任_05、②UKUS agent)。自分の行のみ追加。本委任にTTSなし。
4. SSOT初期反映(自分の行のみ、即commit): OPEN_ITEMS新規行(ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ①固有名詞、Status=ROOT_CAUSE_DESIGN_IN_PROGRESS)、OPEN-465へ「Phase 4はユーザー指示(2026-10-23)により包括対策の検証・採用判断まで保留。停止中音声(run_sf_prod_01 a2/b1b narration 37+36 OK clip)保全、Bertie個別登録・speciality個別例外は行わない」を追記、UDR: Fableが先に提示した2判断(Bertie個別登録/forte受入)は本指示で**上書き(判断済み=個別対応しない)**として記録。

## 1. 原因究明(証拠付き、file:line)
- 現行PNAP(`er103_proper_noun_alarm_policy_01.py`: P-01〜P-15、`_noun_checks`、証拠源=Ledger surfaces :697-712、P-02引用符直後/文頭規則 :167-232、一般語ブロックzipf≥4.0、類似度閾値)、Ledger(`er006_pronunciation_ledger_01.py`、A/B/C階層、承認CLI)、判定連鎖(er006 Primary/Secondary、er078 judge、NG_BOTH→HR Lock、`er019_family_x_validation_inheritance_01.py:349-352` 継承再評価がPASS_WITH_PRONUNCIATION_ALARM起点のみ)、X側の固有名詞供給源(Research Ledger/B3のentity、`kp`、Seed/`key_roles`[Z])、TTS発音供給(Khaite型)。
- 「なぜBertieが固有名詞と認識されなかったか」を、設計時の想定(IMPLEMENTATION_DESIGN_01 §該当、Opus所見OF-PNAP-P-01〜15、Stage 2 Trial)と照合し、**設計上の前提の欠落**(証拠源が人手台帳のみ/大文字始まり証拠の除外規則/本文由来の実体抽出が無い等)として特定。
- 定量: 保存データ(HR queue 88イベント校正セット、4,032ペアON/OFF差分、X英語本文HR→アラーム260、今日のX/Z run含む)から「未登録固有名詞が原因のNG_BOTH/HR Lock」の件数・割合と、固有名詞カテゴリ(人名/地名/組織/作品/ブランド/商品)別の分布を集計(API 0)。
- 過去のStage 2 Trial結論(判定側改善REJECTED/TTS入力側供給VALIDATED条件付き)との整合: 今回の対策が「判定側」のどこを変えるのか、過去REJECTEDの理由(現行TTSの実誤読が主因)と矛盾しないかを明示。

## 2. 包括対策の設計(DESIGN_01、推奨1案+代替)
目標: 台帳事前登録に依存せず本文中の固有名詞を高網羅で検出し、承認済み発音救済(アラーム記録のみで停止しない)が登録済み/未登録双方で機能する。ただし固有名詞と認識しただけで異なる発音を無条件PASSさせない(既存の類似度・一般語ブロック・安全条件維持)。
検討すべき要素(採否は設計者判断、各々の誤PASSリスク・費用・処理時間を比較):
- 本文由来の実体抽出層(run単位1回): 決定論(大文字・CMU人名/地名辞書・役割語・引用符内/文頭を除外しない文脈規則)+必要ならLLM NER 1回/記事(gpt-6-luna等、見積円/記事)。出力=run-scoped「本文実体表」(カテゴリ・出典位置・確度)。
- 既存の供給源の統合: Z Seed `key_roles`/`source_essentials`/`STORY_MAIN_CHARACTER`、X Research Ledger entity/B3、KP。
- PNAP証拠源の拡張: Ledger surfaces + 本文実体表(C階層=自動検出・発音注入なし・ASR受理証拠のみ)。Ledger人承認フローは維持(B階層以上のTTS注入は従来どおり)。
- 安全条件: 類似度閾値、同音/表記揺れ/実誤発音の区別(音素距離、Secondary一致、複数attempt一貫性)、カテゴリ別の受理条件、既存一般語ブロック、HR Lock経路の残置、誤PASS上限。
- Family X/Z両方の配線点(DEV Trialでは正式経路を変更せず、保存転写・保存音声・判定関数の再評価で検証)。
- 費用・時間: 追加API≤目標(例: ≤0.5円/記事セット)、70円目標との整合。
- 検証計画: 正常系(Bertie含む未登録固有名詞の受理)、異常系(実誤発音の不受理)、境界(一般語と同形の人名 Bill/Mark/Rose、引用符・文頭、複合名)、一般化(保存データの登録済み語を伏せて未登録扱いにするleave-one-out評価)、カテゴリ別、偽PASS率。
- 成功基準(数値)案と、撤去/縮小すべき旧規則(P-02の一部等)の明示。

## 3. 成果物
`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/{ROOT_CAUSE_01,DESIGN_01,OPUS_REVIEW_REQUEST_01}.md`。OPUS_REVIEW_REQUESTは論点(抜け漏れ・誤PASSリスク・改善余地・過去REJECTEDとの整合・費用)を絞って書く。commit/push(明示add、secret_scan hits=0)。

## 4. 禁止
Production/Prompt/flag/閾値/Ledger変更、`upsert`/`--apply`、HR Lock解除、run_sf_prod_01のstage実行、個別登録、Trial実装(Opusレビュー後の次委任)、②側ファイルの編集。

## 5. 報告(docs/pm/RESULT_PACKET_ASRQ_PN1.md)
(1)根本原因と既存仕様が機能しなかった理由 (2)定量(件数・カテゴリ分布) (3)推奨案の仕組み・代替案・比較表 (4)安全条件・誤PASS対策 (5)費用・時間見込み (6)検証計画と成功基準 (7)Opus論点 (8)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。