MARKER: ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_05 (2026-10-24, Fable→sonnet-worker)

# 管理ID: ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_05(OPEN-487 案A実装→gate→Production反映 / OPEN-491 是正 / OPEN-489 Fable受入記録 / sonnet-worker.md 1行追記。API 0・新規TTS 0)

## Fable判断
- **OPEN-489**: 委任_04の修正(562e39c21)をFable受入=**PRODUCTION_WIRED**(根拠: TEST_MATRIX_03 152件 期待不一致12→0、replay 5,330対 全層変化0[Family別0]、保存entry再判定変化0、各層1ブロック、flag無し)。OPEN_ITEMS/DECISION_LOGに記録。
- **OPEN-487**: 真因=一次分類の `despaced()` が数字-数字境界の空白まで消し `1:30`(=`1 30`)と `130` を分かち書き差として一致させる契約違反。**案A採用**(数字-数字境界の空白のみ残す、約12行・1module・flag無し)。Opus必須レビューは不要と判定(新構造でなく既存契約への是正、受理面の縮小のみ、replay最終judge PASS→NG 0。11-3の不要例に該当)。開示: `At 1030`↔`At 10:30` 等の偶然一致がPrimary分類でNGになるが、X/Zは承認済みer109同音規則が救済(`xz.decision` True確認済み)、A/B/C Legacyは非救済(保存corpusに該当0件、合成のみ)→OPEN_ITEMS・CURRENT_SPECに明記。
- **OPEN-491**(`one hundred and ten`→`one hundred and 10` 部分数字化でp1_value_diff): F-1と同型。er021/er006の2ブロックで同じgateを通して是正(別commit)。
- **sonnet-worker.md**: Fable権限で次の1行を「報告ルール」節へ追記することを承認: 「新規OPEN登録時は『修正へ進む/ユーザー判断要/実害なし』の分類を必ず付し、修正へ進む場合は同一委任内で着手するか次委任案を書く(2026-10-24ユーザー指示、PM_GOVERNANCE 11-8)」。

## 作業
 1. OPEN-487 案A実装(`er006` `despaced()` と冠詞除外despace): proto_487Aを基に実装、test追加(`1:30 people`↔`one hundred thirty people` NG、`1 30`↔`130` NG、`10:30`↔`1030` はX/Zでer109 RESCUE PIN・LegacyでNG PIN、複合語の分かち書き差 `web site`↔`website` 等は従来どおりPASS維持、数字を含まない語の分かち書きは不変)。TEST_MATRIX_487_01(56件)+TEST_MATRIX_03(152件)で期待不一致0、replay 5,330対で最終judge PASS→NG 0・分類層の変化は開示パターンのみ(件数・Family別)。全回帰(本環境の依存欠落は前回同様、失敗IDの前後一致で判定)。runtime evidence: X/Z保存entryの正式再判定で変化0、合成 `1:30 people` の誤PASS解消。
 2. OPEN-491 是正(別commit): er021/er006の「scale語+and+1桁数字」を合成数として読む、gate(matrix・replay 0・負例維持)、test、evidence。
 3. SSOT: OPEN-487 FIXED→Fable受入は本委任の結果をFableが見て判定(「FIXED_PENDING_FABLE」)、OPEN-489 PRODUCTION_WIRED(Fable受入)、OPEN-491 FIXED_PENDING_FABLE、OPEN-488 対応不要(委任_04記録済み・再評価トリガ)。CURRENT_SPEC(数値正規化/分類層のdespace契約に「数字-数字境界は保持」を既存書式で追記、Legacy非救済の開示)。DECISION_LOG(Fable判断: 489受入、487案A採用・Opus不要の理由、491)。
 4. `.claude/agents/sonnet-worker.md` に上記1行を追記。
 5. 委任文逐語保存 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_ASR-TIME-NUMERAL-EQUIVALENCE-01_委任_05.md`(先頭MARKER一致、0始まり)。commit前に `git status` でindex確認→`git commit --only -- <paths>`(487=1 commit、491=1 commit、SSOT=1 commit。`git add -A/-u/-f/-N`禁止、secret grep 0件)→`git push origin HEAD:main`。OPEN-490の追跡ファイル自動追記は復元・stageしない。
 6. 報告 `docs/pm/RESULT_PACKET_ATN5.md`: 487(原因・修正・matrix・replay・回帰・evidence・開示・commit)、491(同)、489受入記録、sonnet-worker.md追記、4行、判定整合行、使用モデル(LLM呼出0)。