# OPUS_REVIEW_REQUEST_01_BLIGHT(Opus独立レビュー依頼文。条件A=新しい判定フロー。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07B、2026-10-25)
依頼元: Fable(sandwich-pm)。依頼先: Opus独立技術レビュー(PM_GOVERNANCE 11-3 条件A)。**Opusは本依頼書の記述を鵜呑みにせず、下記の一次資料とコードを自分で読んで判断すること。** Sonnet側の自己評価・Status候補は参考情報であり判断材料ではない。
## 1. 対象
日本語ASRの『Primaryの読み一致+Secondary(Azure)の値一致』複合判定(②B-light、案β)の設計と試作。Production未配線・未採用。
一次資料: `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/` の `B_LIGHT_ROOT_CAUSE_01.md`、`B_LIGHT_DESIGN_01.md`、`B_LIGHT_PREREGISTERED_01.md`、`B_LIGHT_EVAL_01.md`、`b_light_proto_01.py`(sha256 `5b715f8e…`)、`b_light_proto_01_test_01.py`、`eval_b_light_api0_01.py`(+`.out.txt/.json`)。関連: `proto_reading_compare_02.py`(v2)、`proto_value_gate_fix_04.py`(F1+F2、07A適用中)、`er078_asr_unified_judge_01.py`(P1: pin版567-568行)、`er007_ja_secondary_asr_01.py`(`_secondary_accept` 643行)、UDR #136逐語(`docs/pm/delegation_log/2026-10-22_ASR-THREE-WAY-COMPARISON-TRIAL-01_DECISION_USER.md`)、ユーザー原文(`..._USER_02.md`)。
## 2. レビュー論点(順に答えてほしい)
1. **安全性**: (a)`composite_judge`が『Secondaryの値だけでPASS』になっていないか(Primary読み被覆+Primary値の非矛盾が本当に必須か)。(b)断片説明(F-A/F-B)の誤受理経路: 実音声が`8,000,900`等であってもAzureが台本値を返せばPASSする残余リスクの評価。位取り条件(前断片の末尾0≥後断片の桁数)・カンマ/万の除外は十分か。**他の桁パターンで偽の説明が成立する例**を作れるか(例: 1,500と1000500、1,200と1000200)。(c)Azureの台本値追従(誤って台本通りの値を返す)確率の見積としてN-3の0/3は十分か。(d)否定・不規則読み・A7・C2の取りこぼし。
2. **UDR #136整合**: ROOT_CAUSE_01 §5の表(条件1〜5・§3、2026-10-11安全条件、CURRENT_SPEC L2179/L2856/L2865)の接触判定が妥当か。『β=#136の変更不要』は正しいか。γ(Whisper第3票)・δ(Secondary読み受理)の接触判定は妥当か。
3. **F1/F2との整合**: 07Aが適用するF1(READING_MATCHの最終値ゲートskip撤去)・F2(かな数詞統一)との順序・重複・矛盾。βがF1の安全意図(値の最終確認)を弱めていないか。F1適用で月題a3再転写#2(`月のシワ、8000九百本超`)がNG化する事実(評価§2)の扱い。
4. **過適合**: 設計根拠の断片連結崩れは月題の2転写のみ(n=2)。ルールが月題に合わせ込まれていないか。汎化確認(T1: `B_LIGHT_BUDGET_PLAN_01.md`)の設計は妥当か。βを採用提案する前に何が最低限必要か。効果が狭いなら別方式へ切り替えるべきか(Fableの再計画材料)。
5. **X/Y/Z影響**: 共通経路(`er007_ja_secondary_asr_01`→`unified_judge`)での配線フック3点(P1緩和・F1最終ゲート降格・P3許容集合)の妥当性、HR Lock/retry/resume(再利用guardがPrimary転写のみで再判定する問題)、A/B/C非対象、flag設計(11-7限定例外の5条件)。
6. **評価の妥当性**: 事前登録の基準(1a〜1d・2〜7)と、最悪ケース被覆(Secondary=原稿)・合成負例55件・実履歴43対・N-3の組合せで、増分誤PASSの検出力が足りるか。比較基準をpin commit(`89b630bd1`)のスナップショットにした設計は適切か。
7. 見落とし・より良い代替(例: 位取り断片の説明を使わず『2エンジンの値矛盾=NG』に徹し、数詞崩れはTTS側/Writer側で避ける案、Primary再転写の多数決[JA ASR再試行は4段廃止の既決]、Azure用の数値フォーマット指定等)。
## 3. 出力してほしい形
必須修正(M-番号)/推奨(R-番号)/不要(承認)を分け、各所見に根拠(ファイル:行または再現手順)を付ける。Production採用の可否判断は不要(採用はユーザー専決)。VALIDATEDで足りるかの所見のみ欲しい。
## 4. 制約(Opusへの注意)
API呼出・Production変更は不要(読み取り+API 0のスクリプト実行のみ)。`er078_*`/`er007_*`は07Aが並行編集中=作業ツリーの現状ではなくpin commitのスナップショットで評価している点に注意。
