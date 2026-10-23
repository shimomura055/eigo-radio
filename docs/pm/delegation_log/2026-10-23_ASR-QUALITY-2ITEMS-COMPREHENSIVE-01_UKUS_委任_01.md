FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-UKUS-委任_01-ROOTCAUSE-DESIGN-20261023

# 委任_01(②英米綴り): 原因究明+包括対策設計(Opusレビュー前まで)。read-only+設計文書。Production/Prompt/flag変更0。API費用0(必要なら≤10円、理由記録)。

## 背景(ユーザー新指示、2026-10-23)
『開いた窓』Adv結末文 `speciality` をASRが米綴り `specialty` と転写→NG 2回→局所書き換えで `forte` に変更された件について、ユーザーは「正当な英米表記の違いによってNG・不要な再生成・脚本変更が発生しないよう包括的に対策。speciality/specialtyの個別ペア登録だけで解決しない」と指示。Scope=原因究明・包括対策設計・Opusレビュー・Trial実装・反復検証・Fable独立評価まで(VALIDATED止まり、Production配線未承認)。Family X/Z共通。Trial回数で止めない自律改善ループ。『開いた窓』音声は保全。原文は①agent(管理ID …-PN)が `docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER.md` へ保存する(数分待って読む。未着なら自分でjsonlの最新userメッセージ「# Claude Code / Fableへの指示 ## ASR品質問題2件の根本対策」を同パスへ保存、衝突時は①側を正とする)。

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_UKUS_委任_01.md`(直近保存index 340のあと5〜6件、先頭MARKER一致で特定)。
2. ACTIVE_TASK.md: 並行agent(FAMILY-X 委任_02、FAMILY-Y 委任_05、①PN agent)。自分の行のみ。TTSなし。
3. OPEN_ITEMS新規行(…-01 ②英米綴り、Status=ROOT_CAUSE_DESIGN_IN_PROGRESS)。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 1. 原因究明(証拠付き、file:line)
- 現行の判定連鎖: er006 Primary/Secondary ASR判定、er078 judge、er109 同音・異表記救済v1(`er109_asr_orthographic_equivalence_01.py:12-17` 音素列交差のみ同値・許容辞書は記号/略語のみ、X/Z scope、PASS_WITH_WARNING経路)、kp_vote_check、retry→cooldown→Local Rewrite(`speciality`→`forte`になった経路と判断基準: どの段で「書き換え」が選ばれたか、Whisper等3rd ASRの有無)、`audio_text_deviation`監査、ページ表示=原稿。
- 「なぜ speciality/specialty が救済されなかったか」を er109設計(WIRING_DESIGN_03、OPUS_REVIEW_COND_A_WIRING_02、ASR-HOMOPHONE…RUNTIME_EVIDENCE)の設計範囲と照合し、設計上の前提の欠落(音素厳密一致主義/英米異綴りカテゴリの不在/ASR出力正規化の不在)として特定。
- 定量(API 0): 保存ASR転写データ(12,506ペア/4,032ペア/HR queue、今日のX/Z run含む)で、英米綴り差が原因のNG・retry・LR・HR Lockを検出(英米異綴り辞書で機械抽出)。件数・割合・代表例・それにより発生した不要retry/LRの費用推定。
- 過去Trial(ASR-HOMOPHONE包括対策、`three↔3:00` fail-closed修正、OPEN-459)との整合。

## 2. 包括対策の設計(DESIGN_01、推奨1案+代替)
目標: 正当な英米表記差(綴り体系の差: -ise/-ize, -our/-or, -re/-er, -ll-/-l-, -ogue/-og, -ence/-ense, ae/oe, speciality/specialty, aluminium/aluminum, jewellery/jewelry, programme/program, grey/gray 等、および不規則対)をPrimary/Secondary双方で正規化・同値扱いし、NG・不要retry・LR・HR Lockを発生させない。一方、意味・発音の異なる語(例: practise/practice は同値だが、ensure/insure、advice/advise、dependent/dependant 等の意味差・発音差の扱い)は誤PASSしない。
検討要素: (a)辞書ベース(オープンな英米対応表の候補とライセンス、オフライン同梱)+(b)規則ベース(接尾辞変換)+(c)音素一致/近接の安全条件(既存er109の音素列照合と組み合わせ、発音が異なる対は同値にしない or PASS_WITH_WARNING)+(d)ASR側の出力正規化(判定前に両者をUS正規形へ写像)か、er109の同値層拡張か(構造の選択理由)。TTS側(脚本を米綴りに統一する前処理)は**本文変更にあたるため不採用理由を明記**(ページ表示との整合も)。適用点=X/Z scope内(`er109_xz_scope_01` 再利用)、A/B/C凍結(§27-3)厳守。費用=API 0が原則(辞書・規則)。
- 既存機構との整合: er109 v1のfail-closed原則(`three↔3:00`で学んだ偽同値の排除)、kp_vote_check(KP英語3-ASR投票)、PASS_WITH_WARNING集計、HR Lock経路残置。
- 検証計画: 正常系(代表英米対≥50組の両方向)、異常系(意味差対・近似綴りの別語≥30組を同値にしない)、境界(固有名詞と同形: Grey/Gray人名、Centre地名)、保存データの再判定でPASS→NG 0・NG→PASSの全件目視分類、一般化(辞書外の規則対)。成功基準(数値)案、撤去/縮小すべき旧規則の明示。
- 『開いた窓』c12の再判定シミュレーション(保存転写に対して対策後はPASSになるか、API 0)。

## 3. 成果物
`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/UKUS/{ROOT_CAUSE_01,DESIGN_01,OPUS_REVIEW_REQUEST_01}.md`。commit/push(明示add、secret_scan hits=0)。

## 4. 禁止
Production/Prompt/flag/閾値変更、er109 pair個別追加、脚本変更、run_sf_prod_01のstage実行、Trial実装(Opusレビュー後の次委任)、①側ファイルの編集。

## 5. 報告(docs/pm/RESULT_PACKET_ASRQ_UKUS1.md)
(1)根本原因と既存仕様が機能しなかった理由 (2)定量(件数・不要retry/LR費用) (3)推奨案の仕組み・代替・比較表 (4)安全条件・誤PASS対策 (5)費用・時間見込み (6)検証計画と成功基準 (7)Opus論点 (8)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。