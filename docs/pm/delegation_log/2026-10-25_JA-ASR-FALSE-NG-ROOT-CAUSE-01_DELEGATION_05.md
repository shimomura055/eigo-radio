管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_05(OPEN-517「既存Productionの誤PASS=承認済み安全条件との矛盾」の是正設計+DEV実装+API 0検証。**Production変更0・有料API 0**。Production適用はFable/ユーザー判断後の別委任)。

## 先にFable判断の転記
- v2(sha bcb042c6…)=**VALIDATED(限定: 安全性[増分誤PASS 0/180・回帰0]は確認。月題救済効果は限定的[12転写中1件]。未知データでの汎化は未確認)**。Task B(ユーザー原文USER_06)の到達上限VALIDATEDに到達。Phase 4(Production適用)はユーザー判断。`TRIAL_RESULT_01.md`のStatus欄・`EVAL_03.md`・OPEN-515へ「Fable(2026-10-25 委任_05転記)」として記載。
- OPEN-517は「承認済み安全条件(値・否定の最終確認)との矛盾の是正」として設計・API 0検証まで自律で進め、Production適用前にOpus軽量レビュー+ユーザー報告を行う。

## 読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(本案件節のみ)、`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/{DESIGN_02(§3 OPEN-517是正案),EVAL_03,open517_value_gate_probe_01.py}`、`er007_ja_asr_validator_01.py`(:441,502 PHONETIC_MATCH生成)、`er007_ja_secondary_asr_01.py`(:427,603 READING_MATCH)、`er078_asr_unified_judge_01.py`(:68-73,526-530 最終ANDゲートskip)、`er078_asr_value_guard_01.py`(`is_irregular_sig`等)、CURRENT_SPEC/SCGの「値・否定の最終確認」安全条件(Grep: L2179/L2856/L2865付近、`PHONETIC_MATCH`、`READING_RESOLVED_MATCH`)、Variant Layer Candidate E(漢字候補総当たり)の承認記録(DECISION_LOG Grep)、OPEN-517。

## 作業(すべてDEV/proto、Production file無変更)
A. `OPEN517_DESIGN_01.md`: (1)矛盾の定義=`PHONETIC_MATCH`/`READING_RESOLVED_MATCH`のPASSが最終ANDゲートの値ガードDIFF・否定差の確認をskipしている箇所と、承認済み安全条件の逐語引用。(2)是正案=READING系PASSにも値ガードDIFF・否定差を常に適用。ただし数詞でない「一番/一部/一方/一度/一緒…」等の序数・慣用語を値ガードの対象から除外する規則(既存の`is_irregular_sig`・数詞辞書との整合、閉集合か汎用規則か)。(3)N3-07型(Candidate Eの近音PASS)は値ガードで検出不能=別件として承認範囲の確認結果(Candidate Eが承認済み仕様かをDECISION_LOGで確認)と対応方向のみ記載。(4)影響範囲(X/Z/Y共通か、HR Lockとの関係、retry/cascadeの挙動変化)。(5)事前登録`OPEN517_PREREGISTERED_01.md`(増分誤NG=正常attemptのNG化0件を必須、既知負例のNG化件数、回帰)。
B. `proto_value_gate_fix_01.py`(DEV、Production関数はimportのみ・複製禁止)+test。保存済み転写(P-4実attempt 133・N-1・N-3・Phase 3転写)でAPI 0再評価`eval_open517_api0_01.py`: 現行→是正後の判定差分を全件表で。`comment_4_attempt1`「いちばん↔一番」が誤NGにならないこと、N3-02型(89,000 vs 8,900)・`三日間/三日目`・`3~5日/35日`がNGになること、正常attemptのNG化0を確認。2回実行で決定論性。
C. `OPUS_REVIEW_REQUEST_01_OPEN517.md`(軽量レビュー用: ゲートの意味変更の妥当性・除外規則の安全性・取りこぼし)。
D. SSOT: OPEN-515(v2 VALIDATED限定)・OPEN-517(設計・検証結果)更新。直前再Read・最小Edit・バックアップ(他agent並行編集中)。CURRENT_SPEC変更なし。
E. Git: 対象pathのみadd→`git commit --only`→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告)。禁止: `git add -A/-u`・amend・rebase・force・stash・reset --hard。secret grep 0件。
F. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_DELEGATION_05.md`(Nは587前後、先頭「管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_05」を580〜615で走査)。

## 禁止
Production code変更、有料API、v1/v2 protoの変更、B-light/Azure併用の実装(ユーザー判断)。

## 報告(RESULT_PACKET_JAASR5.md+口頭要約)
矛盾の定義と該当箇所、是正案と除外規則、API 0再評価の差分(正常NG化0か/負例NG化件数/回帰)、Candidate E承認確認の結果、Production適用に必要な作業・影響・見積、費用0円、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3)。