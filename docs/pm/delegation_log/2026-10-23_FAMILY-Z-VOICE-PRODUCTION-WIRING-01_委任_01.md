FABLE-DELEGATION-MARKER: FAMILY-Z-VOICE-PRODUCTION-WIRING-01-委任_01-20261023

# 委任: Family Z 登場人物Voice 正式採用(APPROVED_FOR_PRODUCTION)のProduction配線 + 『開いた窓』音声制作完成

## 0. 先に行うこと(T-0)
1. 本委任文の逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-VOICE-PRODUCTION-WIRING-01_委任_01.md`。Nは最新index付近(約305〜315)から、先頭行が上記MARKERと一致するものを探して確定する(一致確認を報告に記す)。
2. ユーザー指示原文(下記§1)を `docs/pm/delegation_log/2026-10-23_FAMILY-Z-VOICE-PRODUCTION-WIRING-01_USER.md` に逐語保存する。
3. `docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md` に従い `check_delegation_prompt.py` で本委任文を検証し結果をRESULT_PACKETに記録。
4. `docs/pm/ACTIVE_TASK.md` を固定ヘッダ書式(`docs/pm/PM_BRIEF.md`「ACTIVE_TASK固定ヘッダ」)で上書き(管理ID=FAMILY-Z-VOICE-PRODUCTION-WIRING-01 委任_01)。既存の並行タスク行(OPEN-457 2記事試聴待ち / OPEN-459 AHOユーザー判断待ち)は残す。

## 1. ユーザー指示原文(2026-10-23、逐語)
```
Family Z Voice選定について、最終決定を以下のとおり通知します。

## 1. 正式採用Voice(確定)

| 順位 | 男性Voice | 女性Voice |
|---|---|---|
| 1 | Algieba | Zephyr |
| 2 | Schedar | Kore |
| 3 | Fenrir | Leda |
| 4 | Orus | Sulafat |
| 5 | Puck | Erinome |

※女性2位・3位を入れ替えました。「Kora」は既存候補名の「Kore」と解釈しています。

**Status:APPROVED_FOR_PRODUCTION**

## 2. Production反映指示

- Family Zの登場人物用Voiceとして男女各5名を正式登録。
- 男女それぞれ上記順位で割り当て、6人目以降は循環。
- 同一人物は作品全体で同一Voiceを維持。
- Narrator=Aoede、Advanced補助=Charonは従来どおり別枠。
- 『開いた窓』のMrs. Sappletonを含め、登場人物のVoice割当を更新。
- 『走れメロス』についても新仕様との整合を確認。

## 3. 完了条件

正式Production経路に反映し、必要なテスト・runtime evidence・retry/resume整合・SSOT/Git更新まで確認してください。

『開いた窓』は既存の制作成果を再利用し、不要な再生成を避けて音声制作・QA・試聴ページ完成まで進めてください。

品質を維持しながら最速・低コストで実施してください。

**PRODUCTION_WIREDの条件をすべて満たした時点で、結果を報告してください。**

追加のVoice選定Trialやユーザー判断は不要です。新たな仕様変更が必要な場合のみ判断を求めてください。
```
(原文の全角括弧等は上記のとおり。保存時はこのブロックをそのまま使う。)

## 2. 背景(Fableが確認済み、再調査不要。出典: docs/pm/RESULT_PACKET_FZVS_RECAP.md)
- 候補Trial: FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01(OPEN-430、`docs/research/FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01/`)。ユーザー判断 #131(Voice名)・#129(Mrs. Sappleton)が本指示で**判断済み**になった。
- 割当方針は既決(2026-10-21ユーザー指示 U:§4、`docs/pm/delegation_log/2026-10-21_FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01_USER.md`): 男性・女性独立に**登場順**で1人目→順位1、2人目→順位2…、超えたら循環。同一人物は作品全体で同一Voice。Narrator=Aoede、Adv補助=Charonは登場人物用から除外。作品ごとの選び直し不要。
- 現状のProduction config: `er062_family_z_structure_01.py:40 STORY_SPEAKER_CONFIG`。melos={narrator:Aoede, melos:Algieba(PROVISIONAL_UNAPPROVED), selinuntius:Erinome, dionysius:Charon}(:58-63)。the_open_window={narrator:Aoede, framton:Algieba, vera:Erinome, mrs_sappleton:None(fail-closed), men:Charon}(:94-100)。新Voice(Schedar/Fenrir/Orus/Puck/Kore/Leda/Zephyr/Sulafat)は未登場。循環割当は未配線。
- 『開いた窓』: 割当後に`STORY_SPEAKER_CONFIG`反映→`--stage all`同run resume の方針(UDR #?:299 参照、`docs/pm/USER_DECISION_REGISTER_01.md`で「開いた窓」「resume」をGrep)。既存runディレクトリ・完了段階は貴方が確認する(`er026_output/family_z_production_e2e_01/the_open_window/` 配下を想定。実在pathはGrep/Globで確定)。
- Master Audio Storeは text+voice 等をkeyに再利用される(`er006_master_audio_store_01.py`)。Voiceが変わらないclip(Narrator Aoedeの朗読、Voice不変の登場人物)は再利用され、Voiceが変わるclipのみ生成される。Storeのmanifest書込は非atomicのため、**TTS段を他runと並行させない**(現在他の有料runは走っていない。開始前に`git status`とプロセス確認)。
- 本日(2026-10-23 JST)の開発費累計は0円、日次上限1,000円。本案件はFable自律枠(7-7: 見積300円以下)。**開始前に『開いた窓』音声制作の費用見積を出し、300円超の見込みならTTSを開始せずSTOPして報告**。
- Family Zの直近runtime参照: melos `run_jre_01`(`er026_output/family_z_production_e2e_01/melos/run_jre_01/`)、受入済みpage `user_test/family_z_melos_02/`(**上書き禁止**)。KPはKPFT(fulltext P2)・KP3V・CMU gateがZにも配線済み(OPEN-451/454/458 PRODUCTION_WIRED)。PNAPはZ配線済み(発火未観測)。

## 3. 範囲(やること)
### A. 仕様の実装(Production、Family Z)
1. **正式Voice表の登録**: Family Z登場人物用 男性5(Algieba, Schedar, Fenrir, Orus, Puck)/女性5(Zephyr, Kore, Leda, Sulafat, Erinome)を順位付きで、Family Z構造module(`er062_family_z_structure_01.py`想定)に定数として登録。Narrator=Aoede・Adv補助=Charonは別枠のまま(登場人物用プールに含めない)。
2. **割当規則の実装**: 男女独立・登場順・循環(6人目→順位1)の決定的な割当関数。入力=作品の登場人物roster(性別+登場順)、出力=人物→Voice。同一人物は作品全体で同一Voice。性別・登場順はrosterに**明示データ**として持たせる(名前からの推測・LLM判定はしない)。割当結果はrun metadata(例: `voice_assignment.json`)に残し、resume時に再計算しても同一になること(決定的)。
3. **STORY_SPEAKER_CONFIGの扱い**: 既存の固定値方式を、上記割当関数からの導出に置き換える(または導出結果で更新する)。どちらにするかは既存のTTS/plan経路(fail-closed含む)への影響が最小な方を選び、理由を報告。`PROVISIONAL_UNAPPROVED`コメントは撤去。Charonを登場人物に割り当てている箇所(the_open_window `men`)は新規則で男性プールへ。
4. **『開いた窓』の割当**: rosterの性別・登場順を本文(既存scaffold/台本)から確定し、割当関数で決定。想定(貴方が本文で確認して確定すること): Framton Nuttel=男性、Vera=女性、Mrs. Sappleton=女性、men(狩猟から戻る男たち)=男性グループ。登場順は本文の初出順。結果と根拠(初出のsegment id)を報告。
5. **『走れメロス』整合確認(読取・報告のみ)**: 新規則を適用した場合の割当(melos/selinuntius/dionysiusの性別・登場順→Voice)と現状(Algieba/Erinome/Charon)の差分、差分を解消する場合の再生成対象clip数・費用見積を算出して報告。**メロスの音声・受入済みpageは変更しない**(2026-10-21 U:§7「メロス完成版は変更しない」)。configの導出方式へ移行する場合、melosの現行Voice値が意図せず変わらないよう、作品単位のpin(既存確定値を固定する明示項目、理由コメント付き)で保護し、testで固定する。
6. **テスト**: 割当関数(順位・循環・同一人物同一Voice・男女独立・Narrator/Charon非混入・決定性)、the_open_windowの期待割当、melos pin、Mrs. Sappleton=None fail-closedの撤去確認、既存Zテストの回帰。
7. **retry/resume/Store整合**: 既存runのresume時に旧Voice(例 vera=Erinome)で生成済みclipが混在しないこと(Voiceが変わった人物のclipは再生成されること/Store再利用keyにvoiceが含まれることを確認)。旧Voice clipが成果物に残る場合はSTALE退避(削除ではなく退避)。

### B. 『開いた窓』音声制作完成
1. 既存成果(本文・scaffold・KP・Aoede朗読clip・Voice不変の登場人物clip等)を最大限再利用し、同run resume(または最小の新run)でStd/Advの音声制作→QA(既存Gate: ASR Validation/KP3V/HR Lock等)→assembly→試聴ページ生成。
2. Pages: 新ディレクトリ(例 `user_test/family_z_open_window_01/`)。`family_z_melos_02`・`family_z_melos_jre_01`は上書き禁止。公開後にHTTP 200・実再生検証(Playwright、既存`er019_nws_play_verify_01.py`等の再利用可)。
3. 有料run規約: `TTS_EXECUTION_MODE=STANDARD`、STOPセンチネル確認(rc=0)、**有料runの再起動禁止**(PM_GOVERNANCE 26節)、HR Lock/STOP迂回禁止。HR Lockに到達したら迂回せず、該当segment・理由・選択肢を報告(それ自体は失敗ではない)。
4. 費用: 事前見積(§2のとおり300円超ならSTOP)、実費は`raw_usage_log`/runner `spent_jpy`から出典付きで集計。

### C. SSOT/Git
- CURRENT_SPEC: Family Z Voice節(Grepで該当節を特定)に正式Voice表・割当規則・Status(配線後にPRODUCTION_WIRED)を記載。旧記述(PROVISIONAL/未割当/「#131待ち」)を置換。
- DECISION_LOG: ユーザー決定(APPROVED_FOR_PRODUCTION、2026-10-23、原文所在)+配線エントリ。
- OPEN_ITEMS: OPEN-430をPRODUCTION_WIRED(配線完了時)へ。『開いた窓』関連item(Grepで特定)を更新。新規残件があれば起票。
- USER_DECISION_REGISTER: #131・#129を判断済みへ(決定内容を転記)。
- REPORT_LEDGER 1行。
- commit/push: 変更ファイルのみ明示`git add`(`-A/-u/-f`禁止)。amend/rebase/force push/stash/clean/reset --hard/checkout -f 禁止。`git push origin HEAD:main`。push前に secret_scan `--staged` hits=0。commitは論理単位で分ける(実装+test / 開いた窓run+pages / SSOT)。wav等gitignore対象はpushしない(mp3のみ)。

## 4. Fable判断・制約
- 本件はユーザーのAPPROVED_FOR_PRODUCTIONに基づく配線であり、新Trial・新Voice候補・ユーザー判断の追加は不要。**新たな仕様変更が必要になった場合のみ**STOPして報告(例: 登場人物の性別が本文から確定できない/グループ発話の扱いが既存仕様にない等。その場合も、既存仕様で解決できる案を先に探す)。
- Opus条件Aレビュー: Fable判断では「設定表+決定的な割当関数+config導出」の範囲なら不要。**ただし**、実装にあたりTTS/plan/resumeの処理フロー自体の変更(例: Voice解決のタイミング変更、Storeのkey変更、segment分割変更)が必要と判明したら、実装前にその設計をRESULT_PACKETで報告してFable判断を仰ぐ(その時点で一旦停止)。
- 品質基準は既存の承認済みGateのまま。引き上げ・引き下げ禁止。
- Production採用はユーザー承認済みだが、`PRODUCTION_WIRED`宣言はFableが受入後に行う。貴方の報告ではStatus候補として提示する。
- 推測で発音・音声品質の正否を断定しない。runtime事実と推測を分ける。
- 他agentは走っていないが、commit前に`git status`で他人のstaged fileを巻き込まないこと。

## 5. 受入条件(PRODUCTION_WIREDの条件)
1. 正式Voice表・割当規則がFamily Z Production経路に実装され、the_open_windowの割当がrun metadataとして記録されている。
2. 『開いた窓』Std/Advの音声がQA Gateを通過(またはHR Lock到達箇所が明示)し、試聴ページが公開・実再生検証済み。
3. 新規テスト+既存Zテスト全PASS、全体回帰で自分起因の新規失敗0(`run_project_regression.py`は単独実行、pytest系は別枠)。
4. resume/Store整合の確認(旧Voice clip混在なし)が証拠付き。
5. melos整合確認の結果(差分・費用見積)が報告され、melos成果物は無変更。
6. SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/UDR/REPORT_LEDGER)更新・commit/push済み。
7. 費用が出典付きで報告され、300円以内(超過見込み時は事前STOP済み)。

## 6. 報告(docs/pm/RESULT_PACKET_FZVW.md に書き、同内容を最終報告で返す)
(1)Status候補(X/Zの区別は不要、Family Zのみ) (2)実装内容(ファイル:行、割当関数、config方式と選定理由) (3)『開いた窓』割当結果(人物・性別・初出segment・Voice) (4)runtime evidence(run dir、再利用clip数/新規生成clip数、QA結果、HR到達、Pages URL+再生検証) (5)テスト・回帰数値 (6)resume/Store整合 (7)melos整合確認(差分表・再生成対象数・費用見積、無変更の確認) (8)費用(出典) (9)commit hash・raw URL一覧・SSOT更新箇所 (10)未解決・残件・判断候補(新仕様変更が必要な場合のみ) + RESULT_PACKET 4行(既存仕様整合/未承認機能の既定値/失敗終了時の最終成果物・目的適合/撤去・残置) + 「判定整合: 重大NG=あり/なし」。
原文(§1)からの目的の逐語引用を(3)の冒頭に置く。