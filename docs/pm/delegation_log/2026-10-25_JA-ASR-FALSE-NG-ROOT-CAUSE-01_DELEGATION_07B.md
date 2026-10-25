管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07B(②B-light: 原因究明・対策設計・事前登録・API 0 Trial・Opusレビュー依頼文。**Production変更0・有料API 0**[保存済み転写で評価。追加の有料Trialが必要な場合は見積のみ出して本委任では実行しない])。並行して委任_07A(別agent)が③OPEN-517 F1+F2のProduction適用(`er078_*`/`er007_*`/ADDENDUM/CURRENT_SPEC/OPEN-517/523/524)を担当=それらは**読むだけ・編集禁止**。本委任の所有: `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/B_LIGHT_*`(docs・proto・eval)、OPEN-515(②の追記)、新規OPEN(必要時)、delegation_log 07B。

## 0. ユーザー承認(2026-10-25「日本語ASR誤判定の包括的根本対策｜①v2・②B-light・③既存誤PASS是正」。原文は07Aが`..._USER_02.md`へ保存中。存在すれば読む)
②B-light: 原因究明・対策設計・Trialを承認。Azure Secondaryの認識結果を安全に活用する方式を検証。UDR #136との整合を確認し、UDR #136の承認条件や合格基準の変更は別途ユーザー承認。設計観点7点: (1)Primary/Secondaryのどの情報を採用するか (2)数値そのものの一致をどう保証 (3)数値以外の読みの正確性をどう保証 (4)不規則読みの扱い (5)Primary/Secondary矛盾時の安全処理 (6)既存同音異字救済仕様との整合 (7)誤NG削減効果と誤PASS増加リスク。**Azureが数字を正しく認識しただけで無条件にPASSさせない**。受入: 8,900↔89,000区別・しわ↔すわ区別・みっか↔さんにち必要に応じ区別・既存負例に悪影響なし・正常な月題の救済・正しい音声を不要にNGにしない・Secondary利用時も安全性維持・Gate/retry/resume整合・X/Y/Z共通。自律改善ループ(原因→対策→Trial→評価→再検討)、効果の薄い方式を繰り返さない、Status上限VALIDATED、VALIDATEDでもProduction採用は自動開始しない。

## 1. 読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(本案件節のみ)、`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/{ROOT_CAUSE_01,EXISTING_SPEC_CHECK_01,DESIGN_01(B-light保留の経緯・A4(b)),DESIGN_02,EVAL_01,EVAL_02,EVAL_03,TRIAL_RESULT_01,OPUS_REVIEW_01,OPEN517_DESIGN_02,OPEN517_EVAL_02}.md`、`proto_reading_compare_02.py`(v2)、`proto_value_gate_fix_04.py`、`phase3_run/usage_log.jsonl`(Phase 3実転写: 月題A1 Azure・A2 OpenAI×3・A3 Azure flip・N-3 30clip・O1)、`n3_clips_01.json`、UDR #136(DECISION_LOG/OPEN_ITEMSでGrep: 承認条件・合格基準の逐語)、CURRENT_SPEC L2865(Secondary値等価)・L2179/L2856(SCG安全条件)、`er007_ja_secondary_asr_01.py`(Secondary判定・`_ja_value_form`・C2等の受理条件)、`er078_asr_unified_judge_01.py`(P1→P3の流れ、DEMOTE/AMBIGUOUS)、`er078_asr_value_guard_01.py`、Variant Layer/同音異字救済(`er007_ja_asr_validator_01.py`)、HR Lock・retry cascade(`er006_output/audio_retry_cascade_prod_01`系の仕様Grep)。

## 2. 作業
A. `B_LIGHT_ROOT_CAUSE_01.md`: 月題型(数詞崩れ×同音異字)でSecondary(Azure)が値を正しく書くのに救済されない正確な理由(R4=Secondary acceptに値等価がない/読み不一致「月野市」「杉野氏」/C2規則等)を、保存済み転写(A1/A3 Azure、A2 OpenAI×3)で逐語トレース。UDR #136の承認条件(逐語)と、どの条件がB-lightと接触するかを表に。
B. `B_LIGHT_DESIGN_01.md`: 観点7点に答える方式案(候補を2〜3案比較し1案を推奨)。必須要件: (i)値はatom単位でPrimary/Secondary双方と原稿を照合し、**Secondaryの値一致だけでPASSにしない**(Primaryの読み一致部分+Secondaryの値一致の「組合せ」で原稿全体を被覆する等) (ii)数値以外の読みは既存のPrimary読み照合/Variant Layerの承認済み規則で保証、未被覆部分が残ればNG (iii)不規則読み(v2の`is_irregular_sig`除外)を継承 (iv)Primary/Secondaryで値が矛盾したらNG_PROTECTED (v)同音異字救済との整合(Candidate E=OPEN-333は使わない) (vi)しわ↔すわ・8,900↔89,000・みっか↔さんにちが通らないことを設計段階で示す (vii)F1+F2(07A適用後)との整合=最終ANDゲートは常に通す。出力は新class(例`JA_SECONDARY_VALUE_PRIMARY_READING_COMPOSITE`)+PASS_WITH_WARNING、HR Lock/retry/resumeへの影響、X/Y/Z共通経路での位置。UDR #136の変更要否を明確化(不要なら「既存条件内」の根拠、必要なら変更前後の条件・必要性・品質影響をユーザー判断事項として整理)。
C. `B_LIGHT_PREREGISTERED_01.md`: 合格基準(増分誤PASS 0: N-1 150+N-3 30+合成負例[8,900↔89,000・しわ↔すわ・さんにち・Secondaryだけ正しい/Primaryだけ正しい/両方違う等]、回帰0、月題12転写の救済率[目標: attempt1〜3の正常音声を安定して救済]、Melos副作用0、Status写像3値)。
D. `b_light_proto_01.py`(DEV、Production関数はimportのみ)+test、`eval_b_light_api0_01.py`(保存済み転写: Primary×Secondaryの対が揃っている件を列挙=A1/A3 AzureとA2 OpenAI、N-3のAzure結果があるもの、P-4実attemptでSecondary記録があるもの。対が無い件は「評価不能」として件数明記)。2回実行で決定的。`B_LIGHT_EVAL_01.md`(結果・Status候補の機械写像・限界)。
E. 追加の有料Trialが必要な場合(例: N-3 30clipのAzure転写が未取得なら約数円): 見積・対象・目的を`B_LIGHT_BUDGET_PLAN_01.md`に書くのみ(実行しない。Fableが判断)。
F. `OPUS_REVIEW_REQUEST_01_BLIGHT.md`(条件A: 新しい判定フロー。論点: 安全性・UDR #136整合・F1/F2との整合・過適合・X/Y/Z影響)。
G. SSOT: OPEN-515に②の進捗を最小追記(直前再Read・最小Edit・バックアップ。07A・他agent並行編集中)。CURRENT_SPEC変更なし。
H. Git: 対象pathのみ→`git commit --only`または一時index→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告)。禁止: `git add -A/-u`・amend・rebase・force・stash・reset --hard。secret grep 0件。
I. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_DELEGATION_07B.md`(Nは600前後、先頭「管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07B」を594〜645で走査)。

## 3. 禁止
Production code変更(`er078_*`/`er007_*`は07A所有)、有料API、UDR #136の変更、v1/v2/v4 protoの変更、Candidate Eの利用拡大。

## 4. 報告(RESULT_PACKET_JAASR7B.md+口頭要約)
根本原因(逐語トレース)、UDR #136との接触点と変更要否、推奨方式と却下案の理由、API 0評価結果(増分誤PASS/回帰/月題救済率/評価不能件数)、Status候補、有料Trial要否と見積、Opus依頼文所在、費用0円、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3)。