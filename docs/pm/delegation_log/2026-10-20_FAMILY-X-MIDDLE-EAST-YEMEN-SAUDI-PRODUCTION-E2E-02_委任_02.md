# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_02(Std comment_2 `HUMAN_REVIEW_REQUIRED` のPM_GOVERNANCE 14節手順[既存仕様reconcile→原因切り分け→failure mode一般化]+残CP[Ledger外描写・日付突合]+人間試聴用ページ準備+main反映)。並行agentなし。

## 前委任のQDC/受入記録(委任_01)
- 当初目的: ユーザー決定③=現行Production仕様で攻撃主体を含む中東記事を音声完成・試聴ページ公開まで。
- 結果: Research試行1(run_mey_02)でB3が攻撃主体Fact(YSA-20261020-01、連合軍報道官発表としてフーシ派のミサイル)を採用、Writer反映あり(Adv/Std)。Adv音声は完成(294.12s)。**Std comment_2がAUWで3回`TRUE_CONTENT_MISMATCH/NG_BOTH`→`review_lock_state=HUMAN_REVIEW_REQUIRED`、assemble `BLOCKED_STYLE_PROFILE_GATE`でSTOP**。実費JPY55.87(text 32.514/audio 23.36)。当日累計569.11。
- 証拠: `docs/research/FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02/E2E_PLAN_02.md` §0〜§8、`er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_mey_02/a2/audit/`。
- 不一致: 完成音声・試聴ページ未達(Std未assemble)。受入判定=未完(ACCEPTED不可)。判定整合: 重大NG=なし/主因=Std comment_2 JA ASR不一致(「タイフーン機」→一次「台風機/台風期」・二次「大奮期/台風期」)/是正対象=Std comment_2/STOP理由=HR Lock+M3 Gate/提示=未。

## 性質/到達上限Status/禁止事項
- 性質: 調査・記録・試聴準備。**HR Lockの解除・`approve_regenerate`・`record_human_approval`・review_lock_state編集は禁止**(解除は人間ユーザーのみ)。コード・Prompt・閾値・辞書/発音ledgerの変更禁止(候補として報告のみ)。新規TTS/ASR/LLM呼出禁止(費用JPY0。例外: 下記D-3の既存offline判定関数の再実行はAPI不要の範囲のみ)。
- 到達Status: `STD_COMMENT2_HR_CAUSE_ISOLATED_LISTENING_PAGE_READY`。
- 費用/日次: JPY0(当日既使用569.11、出典RESULT_PACKET_MEY2/daily_dev_cost)。
- Opus独立技術レビューGate: 非該当(調査のみ)。11-8修正範囲: 範囲外=受理面・閾値・方式の新設/拡大(例: 読み同値の新Tier追加・閾値緩和・辞書登録)。範囲内=承認済み仕様文と実装の乖離の是正(本委任では是正せず、該当有無の判定材料を報告)。
- 時間見込み: 60分(A 20/B 15/C 15/D 10)。A〜Dは独立なので順序自由、Cのページ生成とA/Bは並行可。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を`docs/pm/delegation_log/2026-10-20_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02_委任_02.md`へ逐語保存(打ち直し禁止。`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <上記path>`、Nは本委任文[管理IDに「E2E-02 委任_02」を含む最新]。直前indexにPM-GIT-PUSH-TARGET-CORRECTION-01[186]があるので取り違えない)し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file <上記path> --json-out <上記path>_check.json`を実行、結果をRESULT_PACKETへ1行。併せて未commitの `docs/pm/delegation_log/2026-10-20_PM-GIT-PUSH-TARGET-CORRECTION-01_委任_01.md`(+`_check.json`)も本委任のcommitに含める。
T-2: 新規TTSなし(将来のresumeは`TTS_EXECUTION_MODE=STANDARD`明示が前提と報告に記す)。

## 作業
### A. 既存仕様reconcile(14節 step2)+11-8不具合判定材料
1. Std(JA)コメントのAUW/ASR cascade正式仕様を特定: `CURRENT_SPEC.md`をGrep(`ja_asr|JA ASR|日本語.*ASR|SUPPORT_JA.*ASR|JA_FALLBACK|NORMALIZED_MATCH|読み|カタカナ|かな正規化|secondary_not_accepted|NG_BOTH`)し、該当節の行範囲のみRead。実装は`er007_output/ja_asr_cascade_01/`に対応するmodule(Grep `ja_asr_cascade` で特定)と、今回の判定を出した関数(`a2/audit/`内のjudge json の`reason`/`tier`キーから逆引き)。
2. 問い: 承認済み仕様に「漢字/カタカナの読み同値(例: 台風機≒タイフーン機)」を受理するTierや正規化が**存在するか**。(a)存在し発火すべきなのに発火していない→11-8範囲内の是正候補(仕様文:行と実装:行を併記)/(b)存在しない→受理面の新設=範囲外(ユーザー判断)。Family Zで同種(固有名詞のASR表記揺れ)に対し既に判断済みの事項(REGISTER #52 M1 OOV除外、#120 A/A' REJECTED、OPEN-371 P1辞書UDR)との関係を1段落で整理(同じ問題なら再質問しない材料)。
3. 二次ASR(Azure ja-JP)にPhrase List注入が正式配線されているか(`er006_secondary_asr_01.py` のPhraseList構築が台本語[カタカナ語]を含むか、JA経路でも適用されるか、`AZURE_PHRASE_LIST_WEIGHT=2.0`がJAにも効くか)を確認し、今回のaudit(`azure_phrase_list`/`azure_phrase_list_weight`キー)の実値を記録。
### B. 原因切り分け(14節 step3)+一般化(step4)
1. comment_2の3 attemptについて: wav path・期待文・一次/二次転写全文・差分位置・judge理由を表にする。「フーシ派」以降が全一致なら、差分は「タイフーン機」のみかを確定。
2. 3回のTTS音声が同一か(sha/長さ)・ASR転写が3回とも「taifū-ki」読みであることから「音声は正しく読まれている蓋然性」を評価(断定しない。試聴はユーザー)。
3. failure mode一般化: 「台本中のカタカナ外来語が、ASRで同音の漢字語へ正書化される」ケースの既往(他runのhuman_review_queue/pass_with_warning/attempt_historyをGrep `台風|タイフーン|カタカナ|kanji|katakana`)と件数。
4. 今回のStd comment_2本文「タイフーン機」はS3 SUPPORT_JAのscaffoldが生成した文。ユーザーが理解しやすい日本語か(「タイフーン戦闘機」等の方が自然か)も所見として1行(変更はしない)。
### C. 人間試聴用ページ準備(HR解除判断はユーザー。ページは判断材料)
1. `user_test/middle_east_yemen_saudi_e2e_02/hr_comment_2/index.html` を作成: comment_2の3 attempt wav(既存Pages運用に従いuser_test配下へコピー。サイズを記録)、期待文、一次/二次ASR転写、差分ハイライト、Adv完成音声(assembled wav、Pages配信可能なサイズか確認。大きければmp3変換は既存scriptがある場合のみ使用、なければwavのまま)と記事全文(Adv/Std本文、Std comment全文、Key Phrases)。既存`er019_mey_page_02.py`を流用し、HRセクションを追加した`er019_mey_hr_page_02.py`として作成。
2. commit/push(下記)後、`https://shimomura055.github.io/eigo-radio/user_test/middle_east_yemen_saudi_e2e_02/hr_comment_2/index.html` のHTTP200と再生確認(`er019_mey_play_verify_02.py`流用、evidence json保存)。
### D. 残CP+解除後の手順書
1. 残CP(E2E-01 §14と同観点): b1b/a2本文の固有名詞・場面・数字をLedgerと突合(Ledger外の具体描写件数、帰属、本文中の日付明示の有無)。Std s11「The Houthis had fired it toward Riyadh.」(RF候補)について、直前文の帰属が文脈上かかるか、Advの同文と比較して1段落。
2. 解除後の手順書(実行しない): ユーザー承認→`record_human_approval`(`er003_v1_n3_01_assemble.py:96`相当の正規経路、Family X側の実在関数をGrep `record_human_approval|human_approved_segments`で特定)→`TTS_EXECUTION_MODE=STANDARD .venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug middle_east_yemen_saudi --run run_mey_02 --level a2 --stage tts --budget-jpy 70`(resume、差分のみか確認)→`--stage assemble --level both`→`--stage player`→`er019_mey_page_02.py`→Playwright。各stepの見積費用(数円の根拠)。代替案(ユーザー判断用、実行しない): (ア)承認して続行/(イ)comment_2のみ既存scaffold再生成経路があれば文言再生成(存在有無と承認要否を明記)/(ウ)11-8範囲内是正が成立する場合の是正案(A-2が(a)のときのみ)。
3. `E2E_PLAN_02.md`に§9(本委任の調査結果・CP・手順書)を追記。
### E. Git
- `git status --porcelain`→明示add(T-0 2ファイル+GITFIX委任文2ファイル+`er019_mey_hr_page_02.py`+`user_test/middle_east_yemen_saudi_e2e_02/hr_comment_2/`+E2E_PLAN_02.md+evidence json)。`git add -A/-u`・stash・amend禁止。secret scan hits=0。
- **push先はmain**: `git push origin HEAD:main`(force禁止。現在origin/main=252d0c3be、ローカルはその先に0b917eb44/dfb80e2feがあるためfast-forward)。pushed後 `git log --oneline -1 origin/main` 記録。`origin/work/post-merge-01`は触らない。
- raw URL列挙。

## 事前指定Read/Grep一覧
- `docs/research/FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02/E2E_PLAN_02.md` §4〜§8(Grep `^## ` で位置特定)。
- `docs/pm/RESULT_PACKET_MEY2.md` 全文(自分の前委任報告、短い)。
- `er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_mey_02/a2/audit/` 配下: comment_2関連json(Glob `*comment_2*`、`review_lock*`、`pass_with_warning_listening_list.json`)。
- `CURRENT_SPEC.md`: 上記Grepパターン→該当節のみ。全文Read禁止。
- `docs/pm/PM_GOVERNANCE.md`: Grep `^### 11-8|^## 14` → 各節のみ。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `^- #(52|116|120)\(`。`OPEN_ITEMS.md`: Grep `^OPEN-371 \|`(行頭400字)。
- `er006_secondary_asr_01.py`: Grep `PhraseList|phrase_list|ja-JP|language` → 該当行±15。
- `er019_mey_page_02.py`/`er019_mey_play_verify_02.py`: 全文。
- `docs/research/FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01/E2E_PLAN_01.md` L139-141(前回CP観点)。

## 報告(docs/pm/RESULT_PACKET_MEY3.md 上書き)
1. A-2の判定材料((a)/(b)いずれか、仕様文:行・実装:行)、Family Z既決事項との関係。2. B表と一般化所見。3. 試聴ページURL・HTTP200・再生evidence。4. 残CP結果(Ledger外描写件数・日付・s11所見)。5. 解除後手順書と費用見積・代替案(判断候補として)。6. commit/push(main)・raw URL。7. T-0結果・費用JPY0確認。USER_DECISION_REQUIREDラベルは付けない。