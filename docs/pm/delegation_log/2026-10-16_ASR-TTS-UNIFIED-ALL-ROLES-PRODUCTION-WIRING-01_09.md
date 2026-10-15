# 委任文 保存(T-0): ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_09

(受領した委任文の全文を、見出し・箇条書きの構造を保って転記。ユーザー指示の引用部は委任文内の逐語引用のまま。)

## 管理ID
`ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_09(**read-only調査・計画**: A-3 U1是正の実装計画、A-4 U2 A2_ONLY例外の成立経緯調査、A-5 43行マトリクスの5区分再整理)。並行: 委任_08(main merge・SSOT更新・Git操作・ACTIVE_TASK更新を担当、worktree `C:\Users\tensh\eigo-radio-crbn`とmain dirで作業)、FCJ 委任_01(Family C JA調査、read-only)、DQI 委任_01(read-only)。**本委任はコード・SSOT・既存ファイルを一切編集せず、Git操作もしない。** 新規作成は下記2ファイル(計画書とRESULT_PACKET_AUW9.md)と委任文保存のみ。衝突なし。

## 性質/到達上限Status/禁止事項
- 性質: 調査・実装計画(Production変更なし)。到達上限Status: `PLAN_READY`(Fableが計画を承認し、Opus条件Cレビュー要否を判断してから委任_10で実装)。
- 禁止: ファイル編集(新規2ファイルと委任文保存を除く)、Git操作、有料API実行(API 0)、`U1_KEEP_C1_SIMILARITY_EXCLUSIONS`等の定数変更、推測で「原文」を創作すること(承認原文は必ずファイル:行で引用)。
- Opus独立技術レビューGate(11-3): 本委任は調査のため非該当。**ただし次委任(U1解放の実装)は条件C候補**なので、Opusに渡せる形で「変更点・影響・誤受理リスク・Regression計画」を計画書にまとめる。
- 時間見込み: 全体60〜90分(U1 30・U2 20・マトリクス 20・報告10)。並列化: 3項目は独立のため順序自由。他3委任と並列実行中。
- 費用/日次: 当日(2026-10-16 JST)既使用=AUW 07/07b 約JPY1.3確認済み(出典 `RUNTIME_EVIDENCE_06.md` §15)、他は未確認/本委任 JPY0/改善見込み 高/承認区分: C(承認済みscope内。ユーザー指示A-3〜A-5)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read、全文Readは構造変更時のみ。G-1: git出力は--porcelain/--stat/--short等で最小化。F-1: 自タスクtranscript退避は不要。T-0: 委任文を本ファイルへ保存しcheck_delegation_prompt.pyを実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。T-2: TTSなし(本委任はTTSなし)。T-3: 費用上限[Cap]なし(API 0)。

## ユーザー指示(原文)
2026-10-16ユーザー指示(全文は委任_08が`docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`へ保存中。存在すればそれを正とする)。本委任に関係する箇所を逐語引用する:

「## A-2. 統一ASR判定の正本
英語・日本語、全Family・全Production Sectionについて以下を基本とする。
1. Primary ASRがPASSなら採用。
2. Primary NGなら、不一致の種類・大きさにかかわらず原則Secondary ASRを実行。
3. Secondary PASSならPASS_WITH_WARNINGとして採用。
4. WARNINGは事後試聴リストに自動登録。事前Human Reviewは不要。
5. 両方NGなら既定のTTS再生成へ進む。
6. 通算3回のTTS生成で不合格なら、承認済みのLocal Rewrite／Human Review経路へ進む。
7. 数値・否定などの明確な重大内容差、独立音声品質QAは維持する。
Melos saidのConnected Speech／M1の合格実績を維持する。
**Primaryの差が大きいという理由だけでSecondaryを省略したり、Secondaryの正当なPASSを拒否したりしない。**

## A-3. 日本語固有名詞・低類似度の除外を是正
現在のU1（REGISTER #83）は、ユーザー正式承認済み統一仕様との不整合として扱う。
現在の固有名詞差・類似度0.4未満等によるSecondary事前除外を調査し、承認済み共通ルールに合わせて是正する。
実行要件：
- 固有名詞差でもPrimary NGならSecondary確認。
- 低類似度でもPrimary NGならSecondary確認。
- Secondaryが原稿を正当に支持すればWARNING付き採用。
- 数値・否定等の保護差、独立QAは例外として維持。
- 既存日本語ASR Validator・Pronunciation Ledgerとの整合確認。
- 過剰救済・誤受理がないことをRegressionで確認。
これは新仕様Trialではなく、**承認済み仕様への実装修正**である。
新たな仕様判断が本当に必要な場合を除き、同じ採否をユーザーへ問い直さない。

## A-4. Local Rewrite後のforce_secondaryを確認
U2（REGISTER #84）について、A2_ONLYの既存例外の意味・成立経緯・品質上の必要性を確認する。
注意：
- A2は従来のStandard相当の処理経路。
- B1系はAdvanced相当。
- Primary NG→Secondaryは両レベル共通の正式仕様。
- `force_secondary`はPrimary PASS時にもSecondary確認を要求する特殊経路であり、通常のSecondary利用とは別。
実施事項：
1. 既存仕様・承認履歴・Production codeを照合する。
2. なぜA2だけに限定されているのか、品質・安全上の根拠を確認する。
3. 今回の統一仕様と矛盾しないか判定する。
4. 不要な旧例外なら、承認済み共通仕様へ整理する。
5. 例外維持が本当に必要なら、理由・適用範囲・影響を報告する。
**Primary PASS時のSecondary強制照合を、根拠なく全レベルへ拡大してはならない。**

## A-5. 残Sectionの実証
43行マトリクスを次の区分で再整理する。
- 実音声で検証済み
- 新規生成が必要だが未検証
- 既存音声の再利用・複製が仕様どおりで、追加ASR不要
- 正式仕様上のN/A
- 別Production不具合で検証不能
特にFamily B A2 narratorの見出し・Hook・Tension・Closingの必要な実音声確認を実施する。
Family C日本語の既存TTS不具合はB案件で扱い、AUWの実装漏れと混同しない。
ただし、全SectionのProduction Wiring受入条件から未確認項目を黙って除外しない。依存関係・未充足条件を明示する。」

## KPI provenance欄
該当なし(本委任はKPI測定なし。計画書内で次委任のRegression KPIの測定経路[frozen=保存済みresults cache replay / fresh=実音声]を区分して書く)。

## Opus台帳更新
Grep `docs/pm/OPUS_FINDINGS_LEDGER.md` で `OF-AUW` を検索し、U1/U2/C1除外/force_secondaryに関係する指摘IDを計画書に列挙(状態遷移は行わない。記載のみ)。

## 事前指定Read一覧
- `er078_asr_unified_judge_01.py` L55-140、`force_secondary`をGrepした該当範囲。
- `er058_output/unified_all_roles_production_wiring_01/DESIGN_02_ADDENDUM_01.md` §11(Grep U1/U2/A2_ONLY)。
- `RUNTIME_EVIDENCE_06.md` §3(15条件表)・§13-10(Y-00 N/A)・43行マトリクスの節。
- `CLOSEOUT_PLAN_07.md` L52-71(15条件最終表)。
- `docs/pm/USER_DECISION_REGISTER_01.md` L163-169(#83〜#87)。
- `OPEN_ITEMS.md`: Grep `OPEN-372 `/`OPEN-371 `/`OPEN-373 `。
- `CURRENT_SPEC.md`: Grep `統一ASR判定仕様`(節全体)、`C1固有名詞`/`類似度0.4`/`force_secondary`/`Local Rewrite後`(該当行±15行)。
- `DECISION_LOG.md`: Grep `2026-10-11`かつ`除外`/`C1`/`類似度`、`force_secondary`/`A2_ONLY`/`LR後v1`(U2成立経緯)。
- `er007_ja_secondary_asr_01.py`(c1_proper_noun/similarity/0.4/force_secondary)、`er006_secondary_asr_01.py`(force_secondary、全repo `force_secondary=True`)。
- Pronunciation Ledger/JA Validator: `pronunciation_ledger`/`er025_`の判定連携箇所。
- 保存データ: `er006_output/master_audio_store_01/`・results cacheのうちJAでNG_EXCLUDED(A4/A5理由)になった件数を集計のみ(代表例3件まで)。

## 事前指定Grep一覧+追記位置
- 全repo `*.py`: `U1_KEEP_C1_SIMILARITY_EXCLUSIONS`/`u1_gated`/`U2_FORCE_SECONDARY_SCOPE`/`force_secondary` 使用箇所一覧(ファイル:行)。
- `er078_*_test_01.py`: `u1`/`U1`/`A5_SIMILARITY`/`A4_C2`/`force_secondary` → α/β分類(α=現行維持を固定するtest→更新対象、β=最終判定の安全性を検証するtest→期待値変更禁止)。
- 追記位置: 既存ファイルへ追記しない。新規 `er058_output/unified_all_roles_production_wiring_01/U1_U2_SECTION_PLAN_09.md` を作成。

## 実行コマンド全文
- 集計(API 0): `.venv\Scripts\python.exe -I` でresults cache/attempt_historyからJAのNG_EXCLUDED件数(理由別)を数える短いscriptをscratchpad(`...\scratchpad\u1_count.py`)に置いて実行。
- test実行は不要(計画のみ)。必要なら netguard plugin付き pytest `-k "u1 or exclusion or force_secondary"` の現状PASS件数のみ。

## SSOT追記文
本委任ではSSOTを編集しない。計画書 §末尾に、次委任で使うDECISION_LOG/CURRENT_SPEC/OPEN_ITEMS追記文案を記す。

## Git
SSOT編集権: なし。Git操作: なし。新規ファイルは未追跡のまま残す。

## 報告(RESULT_PACKET項目) -> `docs/pm/RESULT_PACKET_AUW9.md`
1. T-0結果。
2. U1計画: (a)現行除外ロジックの正確な動作(P1/P2、u1_gated、ファイル:行) (b)2026-10-11承認の除外条件の原文(逐語、ファイル:行)とA-2/A-3との不整合点 (c)最小変更案(定数False+関連test更新+静的監査allowlist影響)と、数値・否定の保護差・独立QA維持/length NG/Pronunciation Ledger・JA Validator整合の保たれ方 (d)誤受理リスク評価 (e)Regression計画(frozen replay API 0 / fresh実音声JA 1〜3 clip見積JPY / 既存test α更新・β不変) (f)Opus条件Cレビュー論点3〜5個。
3. U2調査: A2_ONLY成立経緯(原文 ファイル:行)、A2のLR後v1で force_secondary=True とする根拠、B1に無い理由、統一仕様との関係、結論案(i)維持/(ii)撤廃/(iii)その他のSonnet推奨。全レベル拡大は推奨しない前提。追加費用試算。
4. 43行マトリクス5区分表と、未検証行の実音声取得の実行計画(Family B A2 narrator 見出し/Hook/Tension/Closing含む)。黙って除外していないことの自己確認。
5. 新規発見の独立問題(OPEN候補、記載のみ)。
6. 費用: JPY0。所要時間。
7. 受入記録5項目(当初目的=A-3〜A-5原文逐語/最終成果物/証拠/一致・不一致/判定)。
