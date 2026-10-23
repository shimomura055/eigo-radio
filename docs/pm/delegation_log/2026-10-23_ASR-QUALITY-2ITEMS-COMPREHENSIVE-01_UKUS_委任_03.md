FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-UKUS-委任_03-WIRING-DESIGN-20261023

# 委任_03(②UKUS): APPROVED_FOR_PRODUCTION(ユーザー承認2026-10-23、UDR #168)を受けたProduction配線設計(Opus条件Cレビュー前まで)。設計のみ、コード変更0、API 0。

## 背景
ユーザーは ①RET(OPEN-472)・②UKUS(OPEN-471)のX/Z共通Production採用を承認、到達目標=X/Z双方PRODUCTION_WIRED、必須受入条件9項目。原文は①agent(…-PN-委任_03)が `docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER_02.md` へ保存する(数分待って読む。未着なら自分でjsonlの最新userメッセージ「# 指示｜ASR品質改善2件のProduction Wiring…」を同パスへ保存、衝突時は①側を正)。『開いた窓』c12は採用後に原稿 `speciality` で再生成(④)。

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_UKUS_委任_03.md`(index 361以降、先頭MARKER一致)。
2. ACTIVE_TASK自分の行のみ(並行: PN-委任_03、PERPLEXITY-401、FAMILY-Y 委任_08[有料run中の可能性、pythonプロセスをkillしない])。OPEN-471 Status=`APPROVED_FOR_PRODUCTION(2026-10-23 UDR #168)_WIRING_DESIGN_IN_PROGRESS`。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 設計(`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/UKUS/WIRING_DESIGN_01.md` + `OPUS_REVIEW_REQUEST_02.md`)
Trial成果(`er111_ukus_spelling_trial_01.py`、`er111_ukus_pairs_v1.json`、DESIGN_02、OPUS_REVIEW_01 OF-UKUS-01〜14、TRIAL_RESULT_01)を正式経路へ移す設計。
1. **配線点(file:line)**: er109本体 `evaluate` のopcodeループ(`er109_asr_orthographic_equivalence_01.py:729-761`)への位置別対照合の統合(OF-01方式)、`SpanRecord(rule="ukus_spelling_variant")`、`LAYER_VERSION` 更新とX/Z golden再作成(OF-07(c))、`er109_xz_scope_01` の `_evaluate_cached` LRU/version一致(:97-101,:131)、既存hook(Primary tail/`_secondary_accept`、er078 judge P-06 span unlock[UKUS spanは数値・否定を含まないことの保証]、Secondary pre-check、`kp_vote_check_v1`/er104 KP投票、er019継承再判定、er078 Store reuse guard `ortho_contributed`)が自動で新層を通ることの確認、retry/fallback/regen/resume、HR Lock経路残置。
2. **固定対表の同梱**: `er109_ukus_pairs_v1.json`(Production名へ改名、許諾文・入力hash・denylist・AMB方向・Tier-2 inactive)、ロード方式(1回/process)、辞書更新手順(ビルドscriptの位置づけ=開発ツール)。
3. **flag設計**: 単一定数(`UKUS_SPELLING_EQUIVALENCE_ENABLED=True` 既定ON、run scope内のみ、A/B/C・単体従来どおり)。`ORTHOGRAPHIC_EQUIVALENCE_ENABLED` との関係(親flag OFFなら本層も不活性)。
4. **DEV依存0**: Productionから `er111_*` をimportしない。`er111_ukus_*` はTrial資料として残置または撤去、許可リスト整理。
5. **安全条件(受入条件7)**: PASS→NG 0の構造保証(既存PASSは早期return)、entity token除外(①RETの実体表が利用可能なら読み取り専用で共有、無ければcanonical側の大文字/CMU-OOV判定)、`pron_differs` 監査フィールド、warningsに入れない。
6. **test計画**: 既存er109 test(27+golden)、er109_xz_isolation、新規(位置別照合・AMB方向・固有名詞除外・Tier-2非活性・version)、保存6,137行再判定test(PASS→NG 0)の回帰化、必須Regression。
7. **runtime evidence計画**: Z=『開いた窓』c12を原稿 `speciality` で再生成(LR上書きの解除手順: 当該clipのLR state/`audio_text_deviation`をリセットし canonical で再TTS→ASRが `specialty` でも `ukus_spelling_variant` PASS、HR 0、Store登録、`pron_differs` 記録)。X=UK綴りを含む既存X segment(例 `defence` を含むrun)の再生成1〜2clip、またはX正式経路での保存転写再判定evidence(API 0)+1clip実TTS。費用見込み≤10円。
8. **①RETとの順序・競合**: 同一ファイル(er109_xz_scope、er078、test)を触る箇所の切り分け、commit順(②先→①、または独立)、両方ONでの相互作用test(実体tokenは②対象外)。
9. **撤去**: Trial複製、旧DESIGN_01方式の記述、許可リスト、`BR_AM_SPELLING_PAIRS` は凍結残置(A/B/C)。
Opus論点(条件C): hook自動伝播の確認漏れ、LAYER_VERSION/golden更新の副作用、entity除外の実装位置、c12 LR解除手順の安全性、①との干渉。

## 禁止
コード変更、Production実行、有料run、`er111_*`変更、①側ファイル編集。

## 報告(docs/pm/RESULT_PACKET_ASRQ_UKUS3.md)
(1)配線点表 (2)flag/隔離 (3)対表同梱 (4)test/evidence計画と費用 (5)①との競合整理 (6)Opus論点 (7)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=なし」。