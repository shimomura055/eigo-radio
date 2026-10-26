## 管理ID

KP-GATE-EXCLUSION-RESCUE-DESIGN-01 委任_02(Opus条件Aレビュー反映=DESIGN_02作成+Opus原文保存+SSOT転記、API 0、JPY0)。並行Agent: FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01(所有=`docs/research/FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01/**`、`er121_output/family_y_voice_pause_trial_01/**`、`user_test/family_y_voice_pause_trial_01/**`、RESULT_PACKET_YVP1)、CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01(所有=`docs/research/CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01/**`、chunk関連code/test、RESULT_PACKET_CHK1)。両者はSSOT本体を編集しない。**本委任がSSOT編集権(OPEN_ITEMS/DECISION_LOG/OPUS_FINDINGS_LEDGER/USER_DECISION_REGISTER/ACTIVE_TASK)を持つ唯一のAgent**(8-Y直列化)。CURRENT_SPEC/REPORT_LEDGERは本委任では編集しない。

## 性質/到達上限Status/禁止事項

- 性質: 設計反映+SSOT転記のみ。Production code/Prompt/Gate変更禁止。有料API 0。AI島run_ai_01のHR候補は未確定のまま保全(status以外のCLI実行禁止)。
- 到達上限Status: 本管理ID=DESIGN_DONE_USER_DECISION_PENDING(Fableが`USER_DECISION_REQUIRED`で報告)。
- 禁止: Git禁止操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・`reset --hard`・`checkout -f`・`git checkout -- <file>`)。共有SSOT(DECISION_LOG/USER_DECISION_REGISTER)はworktreeに他agent由来のCRLF全行差分・stale差分があるため、**HEAD blob+自分のhunkのみ**でcommitする(一時index+`git commit-tree`、または`git commit --only`で自hunkだけになることを`git diff --cached --stat`で確認。全行差分を含むcommitは禁止)。
- Opus独立技術レビューGate(11-3): 条件A実施済み(本委任はその反映)。Fable照合結果: Claude案(DESIGN_01)とOpusは「段階1採用推奨・2c保留・救済候補AUTO不可既定」で一致。Opus M1〜M6・R1〜R4は設計の穴の是正であり、既存のユーザー承認内容を変えず新Product原則も加えないため**Fable判断で全件設計へ採用**する(11-3: 次工程へ進めてよい条件を満たす)。Production配線・段階1の採否・段階2・AI島HRへの救済追加は従来どおりユーザー判断。
- 修正範囲の線引き(11-8): 救済フロー全体=範囲外(新方式、ユーザー判断。Opus(A)もこの判定)。guard次トークン条件のCURRENT_SPEC記録漏れ=範囲内の文書是正(OPEN-530、本委任では起票のみ)。
- 時間見込み: 40〜60分。並列化: 案件A/Bと並列。
- 費用/日次: 当日(JST 2026-10-26)既使用JPY約123+案件A進行中(Cap 150、実費は別途)/本委任JPY0/承認区分: C。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。(本委任はTTSなし)
T-3: Capなし(JPY0)。有料API呼出が必要と判明したら実行せずSTOP。

委任文保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 633 --out docs\pm\delegation_log\2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-01_DELEGATION_02.md`(先頭が「## 管理ID」+「KP-GATE-EXCLUSION-RESCUE-DESIGN-01 委任_02」でなければ630〜645を順に試す)。同じtoolで`--index 632`付近のOpus依頼(prompt先頭「## 管理ID\nKP-GATE-EXCLUSION-RESCUE-DESIGN-01 Opus独立技術レビュー」)も`docs\pm\delegation_log\2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-01_OPUS_REQUEST_01.md`へ保存(見つからなければindex 629〜645を走査し、見つからない場合はその旨記録)。check_delegation_promptは委任_02分のみ実行。

## ユーザー指示(原文)

本管理IDのユーザー原文=`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-01_USER.md`(保存済み、再掲しない)。要点: 「今回は調査・設計のみ承認。Productionコード・Prompt・Gateの変更は禁止。新規有料Trialは禁止。現行のAI島記事のHuman Review候補は未確定のまま保全する。設計案の採用・Production Wiringはユーザー判断後に行う。完了時のStatusはUSER_DECISION_REQUIRED」。

## Opusレビュー原文(逐語。`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/OPUS_REVIEW_01.md`へ一字も変えず保存。先頭に`# OPUS_REVIEW_01(条件A、2026-10-26、read-only、JPY0。以下Opus所見の逐語)`の1行を付ける)

## KP-GATE-EXCLUSION-RESCUE-DESIGN-01 Opus独立技術レビュー(条件A、read-only、JPY0)

### 前提
- 新しい処理フローを共通核へ入れる設計なので、条件Aに該当すると判断した。
- 段階1の骨格(revert(表層形へ戻す)と、validator(機械的な検査関数)の再適用)は妥当。
- ただし、救済された候補が「HRを経ない経路」へ漏れる点と、glossとQAが古いまま残る点に穴がある。この2点は実装前に必ず塞ぐ必要がある(M2〜M4)。

### 論点別の所見

**論点1 本文対応: 段階1は問題なし。2cはユーザー判断要(保留に賛成)**
- (b) revertは本文対応を保つ。`er003_key_words_canonicalization.py:599` の「無変更=常に安全」の経路そのものなので、対応関係を失わない。
- (a) 再導出は、M1の制限を付ければ対応を保つ。
- (c) 2cについて。HR選択と`auto_eligible=False`は必要だが、それだけでは足りない。もし将来採用するなら、HR表に元の6語句と元の本文の文を必ず並べて出すこと、さらに否定・程度を表す語(`too/not/never/no/only/hardly`等)を削る部分列を決定論で禁止すること、の2点を追加する必要がある。今回は保留のままでよい。

**論点2 Rule7との整合: 要修正(M1、M6)**
- revertは受理面を広げない。設計意図の`er105:575`(V+名詞は基本形化せず表層形のまま)をむしろ忠実に実装する形になっている。現行実装は、LLMが基本形化を試みて失敗するとitemごと落としており、ここが意図とずれている。
- 穴は再導出のほうにある。`DESIGN_01.md:22-23` は「許可表の1対1置換の全組合せ」を列挙するとしている。validator自体の受理面は変わらないが、validatorはLLMの意味判断の後ろに置く「安全枠」として作られている。全組合せを機械的に列挙すると、LLMが一度も提案していない形が採用され得る。
  - 例1: `hoped for`→`hop for`。`_verb_base_candidates`(`er105:637-643`)はstem(語幹)とstem+eの両方を作る。どちらもCMU辞書の実在語なので、CMUでは区別できない。
  - 例2: `takes notes`→`takes note`。`er105:689` の句末の単数化は、guardなしで通る。
  - 「LLM案に最も近い案を採用」はLLM案と位置がそろわない場合に機能せず、同点時の規則もない。
- `role_ok_poss`について。救済処理の中の判定で空集合を渡すと、受理が広がるのではなく狭まる。ただし最終validator(`er003:697`、`_role_ok_poss_of(item)`)と判定がずれると、「救済したのにINVALID」が起きる(M6)。
- `_token_pair_ok`のguardはkey側の次トークンを見ている(`er105:664`)。そのため、LLMが提案していない人称置換(例: `him`→`someone`)を再導出が自分で作ると、それがguardを通してしまう経路がある。これもM1で塞がる。

**論点3 重複・順位・NG: 要修正(M5)**
- 順位の扱いは正しい。救済されたitemは`live`から外れないので、`ai_rank`(`er119_kp_candidates_01.py:309`)は自然に元の位置になる。
- NGは、`match_ng`がselection_phraseとused_formの両方を見る既存の仕組み(`er119:288-293`)で足りる。
- `_containment`の再適用とoverflowの再適用は実質不要(何もしない処理)。救済後の句がdisplayの窓の中に収まるため。記述を「不要」に直すのが正確。
- 問題は`DESIGN_01.md:67`の「外側retryの条件を緩めも厳しくもしない」という記述。これは事実と違う。
  - 救済に成功した句は`gate_dropped`から消える(`er119:329`)。
  - そのため「AUTO可<3」のときにretryが発動しなくなる。AUTO可を3件以上に届かせるための再挑戦の機会が減り、承認済みM-7(c)の挙動が意味的に変わる。

**論点4 LLMの範囲: 要修正(M3、M4)**
- 新Promptが必要なのは2cだけ、という判断は正しい。
- ただし「段階1はLLM 0」とは言い切れない。gloss再整合は「最終KPに表示候補にない語が含まれる場合だけ」動く(`er003_v1_n3_01_scaffold_generate.py:523`)。
  - revertの場合は対象が0件になるので、LLMが自分のkey向けに作ったglossがそのまま残る。例: `hold out one's hands`の「両手を差し出す」が、`hold out`/`held out`に付いたまま残る。
  - 設計書§7の「a2はgloss 1 call」という記述とも矛盾している。
- QAについて。`qa_meaning_or_usage_unchanged`などは、救済前のkeyに対する判定である。
  - `auto_eligible=False`があればAUTO採用は防げる。しかしHR表にPASSと表示されると、ユーザーを誤らせる。
  - roles処理の先例(`er105:988`)のようにQAをPASSへ上書きする処理は、救済には入れないこと。

**論点5 X/Y/Z共通核: 要修正(M2)**
- (i) rolesの後に置く順序は妥当。
- (ii) A/B/Cは`is_fulltext`が偽なので無影響(`scaffold:502-505`)。
- (iii) Z限定のSRC D1/人称整合は、救済後のitemにも通常どおり適用される(`er119:271-282`)。
- (iv) Yの正式経路が未存在でも、共通moduleとしては問題ない。
- 重大な副作用がある。このhookは`is_fulltext`だけで有効になる。そのため、HRを経ない経路にも効いてしまう。
  - 該当経路: `run_key_phrases`→`run_kp_with_outer_retry`(`scaffold:729,883-888`)、およびZの`run_kp_with_outer_retry_fulltext`(`er062_family_z_writer_01.py:1364-1373`)。
  - これらの経路では、救済された表層形KPが旗もHRもないまま`keywords_canonicalized.json`に確定する。

**論点6 見落とし・過剰制約: 推奨(R1〜R4)**
- `lexical have`を2eに回したこと、救済候補を一律AUTO不可にしたことは、いずれも過剰な制約ではない。

### (A)〜(D)

**(A) 段階1を「受理面を広げない」と呼んでよいか**
- revertと、M1で制限した再導出に限れば、そう呼んでよい。受理されるのは「validator通過」かつ「LLM提案の部分集合」なので、現行より狭い。
- ただし11-8では範囲外と判定する。新しい後処理工程であり、Productionの出力(HR候補の集合、表示)を意味的に変えるため。同型の先例もユーザー承認(UDR #173②)を経ている。
- 進め方の意見:
  - 保存済みparsed応答を使ったoffline DEV実装と再生検証は、Fable判断で先に進めてよい。
  - Production配線はユーザー承認(OI-1)を得てから。または承認済みの限定例外(既定OFFのflag)の範囲内で行う。

**(B) `auto_eligible=False`既定は過剰制約か**
- 段階1では過剰ではない。QAとglossが古いまま残る以上、妥当な既定値。
- revertだけのitem(key==display)については、実データが蓄積した後にAUTO可へ緩める余地がある。ただしそれはユーザー判断事項。

**(C) 見落としているGate除外経路**
1. `cmu_post_canon`による除外(`er119:264-266`)。救済はvalidateの前に置かれるので、ここで落ちる句は救済されない。displayへrevertすれば救える可能性がある(revert後にCMUの再検査は必須)。
2. 外側retry発動時の「候補一覧ごとの置き換え」(`er119:334-341`、`dropped_all=[]`)。Gateを通過済みの良い候補まで捨てる、最大の破棄経路。棚卸しの対象外になっている。
3. canonicalization段の非Rule7の構造違反。具体的には、OF-X1(左端条件)違反(`er003:600-605`)、canon段で語数>5、LLMが有限助動詞を混入させたケース。revertで救えるのに、トリガーが「Rule7(基本形化)」に限定されている。
4. call1の選定段のgate失敗(`sc.run_key_phrase_selection`内のretry)。句は記録されずに消える。

**(D) M(必須修正)/R(推奨)一覧**
- M1: 再導出は「display窓の中で、各tokenを{display側の語, LLMがその位置に出した語}のどちらかから選ぶ」だけに限定する。`_verb_base_candidates`や単数化表から新しい語形を生成しない。同点時は決定論で決め、迷う場合はrevertを優先する。source_spanへの拡張は再導出の対象にしない。
- M2: 救済の有効化をer119の`generate_candidates`経路だけに限定する(canon_fnへ明示引数を渡す方式で、既定OFF)。HRを経ない経路(`scaffold:883-888`、`er062:1364-1373`)では出力がバイト同一であることをtestで固定する。あるいは、それらの経路がProductionで使われていないことを証拠で示す。
- M3: 救済したrankについてはgloss再整合を強制する(`align_glosses(only_ranks=)`)。再整合できなければ`gloss_hr_pending`の旗を付ける。費用はa2実績の約0.5円/件。「LLM 0」の記述を訂正する。
- M4: LLMのqa_*欄は上書きしない。`gates.canonicalization="RESCUED_QA_NOT_REJUDGED"`を付け、HR表では「QA未再判定」と表示する(PASSとは表示しない)。
- M5: 外側retryの条件を現行と同一に保つ。救済された句はretryのトリガー判定上は「gate_dropped相当」として数え、累積除外リストには入れない。現行と異なる挙動を採るなら、OI-1で「挙動変更」として明示してユーザーに諮る。
- M6: 救済処理の中のvalidator呼出は、最終Gateと完全に同じ引数で行う。具体的には`canonicalization_view_items`のspan、`original_span`、`allow_inflection_normalization=_is_ft`、`role_ok_poss=_role_ok_poss_of(item)`。rolesがUNVERIFIED/NO_WINDOWの場合は、一般形の所有格tokenをdisplay側の語へ戻す。元の除外理由は`rescue.before.reasons`に保存する。
- R1: トリガーを「LLMのkeyが原因の構造違反全般」と「cmu_post_canon」に広げる。救済手段はrevertのみとする(受理面は不変)。
- R2: 2cを将来採用する場合は、否定・程度語の削除を決定論で禁止し、HR表に元の句と本文の文を併記することを条件にする。
- R3: 外側retryによる候補一覧の置き換え、およびcall1選定のretryで消えた句を、`dropped`とinventoryへ記録する(観測のみ。救済はしない)。
- R4: 検証にtestを3つ追加する。(1) 実在語だが誤った基本形(`hoped`→`hop`)を採用しないこと、(2) HRを経ない経路が分離されていること、(3) 救済ありとなしで外側retryの発動回数が同一であること。

### 参照ファイル
- `C:\Users\tensh\eigo-radio\docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-01\DESIGN_01.md`(:22-23、:67)
- `C:\Users\tensh\eigo-radio\er105_kp_fulltext_selector_01.py`(:575、:637-643、:664、:689、:976-978、:988)
- `C:\Users\tensh\eigo-radio\er119_kp_candidates_01.py`(:264-266、:288-305、:329-341)
- `C:\Users\tensh\eigo-radio\er003_v1_n3_01_scaffold_generate.py`(:502-507、:523、:729、:883-888)
- `C:\Users\tensh\eigo-radio\er062_family_z_writer_01.py`(:1364-1373)
- `C:\Users\tensh\eigo-radio\er003_key_words_canonicalization.py`(:599-620、:697)

### 要約
revertは承認済みの設計意図(`er105:575`)に沿っており、受理面を広げない。
ただし再導出の全組合せ列挙は、LLMが提案していない誤った基本形を生む。LLM提案の部分集合に制限する必要がある(M1)。
救済のhookはHRを経ない経路にも効いてしまう(M2)。glossとQAは救済前のkeyのまま残る(M3、M4)。外側retryの条件は実際には変わる(M5)。
受理面は不変だが、新しい処理方式のため11-8では範囲外と判定する。offline DEV検証はFable判断で進め、Production配線はユーザー承認後にする。
2cの保留と、救済候補を既定でAUTO不可とすることには賛成する。

(Opus原文ここまで)

## Fable決定(DESIGN_02へ反映する内容)

- M1〜M6: 全件採用。DESIGN_02の段階1定義を「revert(表層形へ戻す)+M1制限付き再導出(display窓内で各tokenを{display側の語, LLMがその位置に出した語}から選ぶのみ・新語形生成なし・同点はrevert優先)」に改める。M2(er119 `generate_candidates`経路限定・明示引数・既定OFF、HRを経ない経路のバイト同一test)、M3(救済rankのgloss再整合強制+`gloss_hr_pending`旗、「段階1はLLM 0」を「救済成立時にgloss再整合call 約0.5円/件[出典: a2実測0.526〜0.563円]」へ訂正)、M4(`RESCUED_QA_NOT_REJUDGED`、HR表「QA未再判定」)、M5(外側retryトリガー判定では救済句を`gate_dropped`相当として数える=現行挙動維持、累積除外には入れない)、M6(最終Gateと同一引数、`rescue.before.reasons`保存)。
- R1: 採用(トリガーを「LLM keyが原因の構造違反全般+cmu_post_canon」へ拡張、手段はrevertのみ)。R2: 採用(2cの採用条件として記録、2cは保留のまま)。R3: 採用(観測のみ)。R4: 採用(test 3件を実装時必須に)。
- Opus(C)の除外経路1〜4をEXCLUSION_PATTERNS_01に「棚卸し対象外だった経路」として追記(件数は分かる範囲、不明は「未集計」)。
- 11-8判定: 救済フロー全体=範囲外(ユーザー判断)。Opus(A)の「offline DEV実装はFable判断で先行可」は記録するが、ユーザー原文「今回は調査・設計のみ承認」により**本案件では実装しない**(ユーザー判断後)。
- 不要な再適用(`_containment`/overflow)は「実質不要」と記述修正。

## 事前指定Read一覧

1. `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/DESIGN_01.md` 全文(改訂元)。
2. `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/EXCLUSION_PATTERNS_01.md` §1-§2(追記位置特定)。
3. `docs/pm/RESULT_PACKET_KPRS1.md` (6)(12)とSSOT追記文案節(OPEN-529/530文案)。
4. `docs/pm/OPUS_FINDINGS_LEDGER.md` 先頭30行(表書式)+Grep `OF-FZFE-M-1`(直近の行書式を倣う)。
5. `OPEN_ITEMS.md` Grep `OPEN-528`(末尾行の書式・追記位置)、Grep `OPEN-526`(関連行に1文追記: 「KP候補数案A/B/C+救済方式OPEN-529を併せて判断」)。
6. `DECISION_LOG.md` 先頭40行(ヘッダーチェーン・最新エントリ書式)。
7. `docs/pm/USER_DECISION_REGISTER_01.md` Grep `OPEN-528`(UDR行書式)。
8. `docs/pm/PM_BRIEF.md` Grep `ACTIVE_TASK固定ヘッダ`→書式節。

## 事前指定Grep一覧+追記位置・更新位置の手順

- OPEN_ITEMS.md: 最大番号確認(Grep `OPEN-5[2-9][0-9]`)→OPEN-529(救済方式、11-8=ユーザー判断要)・OPEN-530(guard記録漏れ、11-8=修正へ進む・範囲内文書是正)をRESULT_PACKET_KPRS1の文案を基に、Opus反映(M1〜M6/R1〜R4採用・DESIGN_02)を1文加えて末尾の対応区分(POST_USER_VALIDATION)へ追記。OPEN-526行末尾に関連1文追記。
- DECISION_LOG.md: 新規エントリ1件「2026-10-26 | KP-GATE-EXCLUSION-RESCUE-DESIGN-01 委任_02(Fable決定) | Opus条件Aレビュー(M1〜M6・R1〜R4)を全件設計へ採用しDESIGN_02へ反映。救済フロー=11-8範囲外(ユーザー判断)、段階1の採否・Production配線・段階2・AI島HR救済追加はユーザー判断待ち。実装0・API 0。」をヘッダーチェーン/索引の既存書式に従い追加(直近エントリの書式を倣う)。
- OPUS_FINDINGS_LEDGER.md: OF-KPRS-M1〜M6、OF-KPRS-R1〜R4(計10行)をRAISED→FABLE_DECIDED(採用)で追加。出典=`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/OPUS_REVIEW_01.md`。
- USER_DECISION_REGISTER_01.md: UDR区分へ「OPEN-529: KP Gate除外救済方式 段階1採否/段階2項目別/AI島HRへの救済追加要否(2026-10-26報告予定)」1行追加。
- ACTIVE_TASK.md: 固定ヘッダで上書き(管理ID=KP-GATE-EXCLUSION-RESCUE-DESIGN-01 委任_02完了/並行=FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01(有料Trial中、Cap150)・CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01(監査中、API 0)/UDR-blocking=OPEN-526・527・528・529/当日費用=2026-10-26 約123+案件A実費(未確定)/1,000)。

## 実行コマンド全文

- 保全確認(作業後1回): `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01`(a2/b1b=PENDING_REVIEW・selection{}のまま)。
- 共有SSOTのhunk限定commit例(DECISION_LOG): 変更後に`git diff --stat -- DECISION_LOG.md`で全行差分が出る場合、`git show HEAD:DECISION_LOG.md > %TEMP%\dl_head.md`→自分の追記だけをHEAD版へ適用した一時ファイルを作り`git hash-object -w`→`git update-index --cacheinfo 100644,<blob>,DECISION_LOG.md`→`git diff --cached --stat`で自hunkのみを確認→commit。OPEN_ITEMS.md/OPUS_FINDINGS_LEDGER.md/USER_DECISION_REGISTER_01.mdも同様に確認(worktreeに他差分があればHEAD blob方式)。
- secret grep: `git diff --cached | findstr /R /C:"sk-[A-Za-z0-9]" /C:"AIza[A-Za-z0-9_-]" /C:"BEGIN PRIVATE KEY"`(0件。delegation_log内の検索コマンド文面は除外して判断)。

## SSOT追記文

上記Grep節に記載(文案はRESULT_PACKET_KPRS1の文案+Opus反映1文)。CURRENT_SPECは編集しない(OPEN-530の文書是正はユーザー報告後の別委任)。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: あり(OPEN_ITEMS.md/DECISION_LOG.md/docs/pm/OPUS_FINDINGS_LEDGER.md/docs/pm/USER_DECISION_REGISTER_01.md)。CURRENT_SPEC.md/REPORT_LEDGER.md/PM_GOVERNANCE.md=なし。
- 明示add: `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/{OPUS_REVIEW_01,DESIGN_02}.md`、`EXCLUSION_PATTERNS_01.md`(追記)、`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-01_{DELEGATION_02,OPUS_REQUEST_01}.md`+`_DELEGATION_02.md_check.json`、上記SSOT 4ファイル(自hunkのみ)。ACTIVE_TASK/RESULT_PACKETはgitignored。
- commit: `git commit --only <paths…> -m "KP-GATE-EXCLUSION-RESCUE-DESIGN-01 委任_02: Opus条件Aレビュー(M1〜M6/R1〜R4)をDESIGN_02へ反映+OPEN-529/530起票・DECISION_LOG・Opus台帳(API 0)"`(共有SSOTはHEAD blob方式なら`commit-tree`でも可。いずれも自hunkのみ)→`git push origin HEAD:main`(non-fast-forwardは`git fetch origin`→`git merge --no-edit origin/main`→再push。競合は両方残してSTOP)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_KPRS2.md`: (0)T-0結果・抽出index (1)DESIGN_02の変更点一覧(M/R番号対応) (2)EXCLUSION_PATTERNS_01追記内容(経路1〜4) (3)SSOT各ファイルの追記行(行番号・全文)と自hunk限定commitの証拠(`git diff --cached --stat`) (4)保全証拠(status) (5)commit/push・raw URL (6)ユーザー向け判断候補の最終整理(Fableが報告に使う形: ①段階1[revert+M1制限再導出、HR旗、AUTO不可、gloss再整合約0.5円/件]の採否と、採用時のProduction配線承認 ②段階2の項目別[2a guard限定詞補完・2a'過去形表補完・2b 副詞前の原形化(`study separately`を通す)・2e lexical have・2c AI短縮(保留推奨)・2d スロット一般化(非推奨)] ③AI島a2 HRへ`studied separately`(表層形)を救済追加するか[必要手順と約0.5〜0.6円]、④guard次トークン条件のCURRENT_SPEC追記(範囲内・0円、Fable判断で実施予定)) (7)Fable向け懸念。最終行に要約10行以内。