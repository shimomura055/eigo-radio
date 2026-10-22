FABLE-DELEGATION-MARKER: KP-AUDIO-NG3-RECORD-FIX-AND-ITN-ANALYSIS-委任_02-20261022

管理ID: FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01 委任_02(OPEN-456 F3)。費用0(API禁止、新規TTS禁止、Production .py/Prompt/仕様の変更禁止)。目的2つ: (A)誤った原因記述のSSOT訂正、(B)Azureの数値整形(ITN: "one's"→"1's")がKP判定へ与える影響の保存データ分析(読み取りのみ)。

## 背景(委任_01の確定事実。`docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01/EVIDENCE_01.md`・`evidence_data_01.json`を読む)
- 合同検証(OPEN-455)のX KP NG 3件(coffee a2/b1b `pump one's fist`、small_bag a2 `novelty minaudière`)は、本番でWhisperが一度も呼ばれていない(NG_BOTH / NG_PROTECTED_DISSENT)。
- 保存wav全12本をlocal faster-whisper small/int8(本番と同設定)で再判定すると、coffee 8本中7本は`one's fist`相当でPASS。`Pump Ones Fest`はcoffee b1b attempt#1の1本のみ。
- Azureはcoffee 8本すべてで`1's fist`(数値整形)。b1b最終#4はPrimary PASS・Azure`1's`→数値保護差でNG_PROTECTED_DISSENT→Whisper不呼出→HR。
- よって、JRE2報告・`RESULT_01.md:65`・OPEN-454観察事項・DECISION_LOG末尾・UDR #153追記にある「coffeeは音声自体が不良(`once fist`等)でゲートの正動作」という記述は、全数再判定では支持されない(音声の聴感判断はユーザー試聴待ち)。

## (A) SSOT訂正(自分の行だけ。`git status`→再Grep→編集→即commit)
1. `docs/research/JOINT-RUNTIME-EVIDENCE-01/RESULT_01.md`の該当行(:65付近)に「訂正(2026-10-22 委任_02): …全数再判定では『音声不良』は支持されず原因未確定。詳細EVIDENCE_01.md」を追記(原文は消さず取り消し線または『旧記述』注記)。
2. `OPEN_ITEMS.md` OPEN-454の観察事項、OPEN-456 F3、`DECISION_LOG.md`末尾のFable受入判定エントリ(KPFTの観察事項部分)、`docs/pm/USER_DECISION_REGISTER_01.md` #153追記、`CURRENT_SPEC.md` KPFTブロック(:1986付近。該当記述がある場合のみ)に、同趣旨の訂正を1行ずつ追記。文言: 「訂正: X KP NG 3件の主因は未確定。本番ではWhisper不呼出(NG_BOTH/NG_PROTECTED_DISSENT)。保存wavのlocal Whisper再判定ではcoffee 8本中7本PASS、Azureは8本すべて`one's`を`1's`と数値整形。『音声自体が不良』は撤回し、ユーザー試聴待ち(OPEN-456 F3、EVIDENCE_01.md)」。
3. 訂正はPM是正(PM_GOVERNANCE 10-2-a)として`docs/pm/REPORT_LEDGER.md`に1行(「Fable報告の誤り訂正: 原因断定の根拠不足」)。

## (B) Azure数値整形の影響分析(読み取りのみ・API 0)
1. 判定器の仕様確認(file:行付き): KP英語判定で、Azure(Secondary)転写はITN後のテキスト(表示形)を使っているか、lexical形も保存されているか(`er006_secondary_asr_01.py`、Azure adapter、`er078_asr_unified_judge_01.py`、`er104_kp_three_asr_vote_01.py`の`value_guard`・protected dissent判定・数値正規化の有無)。「one's」「1's」の比較で、数値保護差(`hyp_drop`/`value diff`)がどう発火するかをコードで追う。既存の数値正規化(spelled-out数↔数字)があるか。
2. 保存データ集計: 保存済みのKP英語判定記録(`er006_output/master_audio_store_01/manifest.json`・評価記録、`er011_output/attempt_history.jsonl`(sidecar除外を考慮)、各run dirの`narration/attempts/*.json`、`review_lock_state.json`、KP3V `stored_audio_reeval_02.json`)から、(i)Azure転写に数字(0-9)が含まれ、期待KPに数字が含まれない件数と、その中でAzure NGとなった件数、(ii)その件数のうち最終判定がHRに至った件数、(iii)期待KPに`one's`/`someone's`/`one`等の語を含むKPの総数とそのAzure NG率。結果は表にし、出典pathと母数を明記。該当0件なら0と書く。
3. 影響見積: 上記から「Azure数値整形が原因でHRに至った可能性のあるKP件数/全KP」を出す(推測と確認済みを分離)。対策候補を**実装せず**列挙(例: Azure lexical形の併用、数値保護差の対象から『期待側に数字が無く、ITNで生じた数字』を除外、Whisperを呼ぶ条件の見直し)。各候補について「承認済み仕様の変更に当たるか(区分)」「追加API」「誤PASSリスク」を1行ずつ。**どれも実施しない。**
4. 成果物: `docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01/AZURE_ITN_IMPACT_01.md`(+集計json)、OPEN-456 F3へ1行、REPORT_LEDGER 1行。

## 共通
- T-0保存 `docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01_委任_02.md`(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、末尾から探索、本文先頭marker `FABLE-DELEGATION-MARKER: KP-AUDIO-NG3-RECORD-FIX-AND-ITN-ANALYSIS-委任_02-20261022` 一致で確定)。
- commit(自分のファイルのみ `git add <file>`)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。
- 報告: `docs/pm/RESULT_PACKET_NG3B.md`に4行+判定整合行。本文: 訂正した箇所一覧、(B)の表と見積、対策候補表(区分付き)、commit hash、raw URL。