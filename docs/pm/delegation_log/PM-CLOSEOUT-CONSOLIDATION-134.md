## 管理ID

PM-CLOSEOUT-CONSOLIDATION-134(USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02 成果物のGit記録・Web到達確認・SSOT反映・最終REPORT)
並行タスク衝突確認: 並行タスクなし。本タスクがGit・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを扱う唯一のタスク。

## 性質/到達上限Status/禁止事項

- 性質: Git記録・Web到達確認・SSOT反映・REPORT作成のみ。**API呼び出し禁止、費用¥0**。Production/Trialコード変更禁止。
- 反映する事実(Fable照合済み。各RESULT_PACKETの実値を使い、自己評価で格上げしない):
  - **Family C / Home robots v2**(`docs/pm/RESULT_PACKET_FIX02_FAMILYC.md`): Status=VALIDATED候補(Trial、ユーザー試聴待ち。v1はVALIDATED扱いを取り消し「試聴NG→v2作成」と記録)。Family A正式構成流用(Intro/Outroジングル、Welcome/Preview intro/Key phrases intro/Full story intro、Notification SFX、A2既存pause値)、Key Phrase 5件表示=canonical=TTS=ASR一致(v1不一致の根本原因: 完了マーカーのみでテキスト未照合の再利用ロジックが選定やり直し中の古い音声を流用。Previewも同様)、Mother=Erinome分離(女性的印象はSSOT未記録・試聴で要確認)、Comment 4件(C1導入/C2段落9-10/C3=v1 story_017-018=段落22-23/C4終了後、3件完全一致・C2は「この後/このあと」表記差のみ)、Gate PASS、319.6秒、Story本文sha256一致、テスト38件PASS。費用¥52.20(開発・Trial費。Family C累計¥148.50、予算枠¥133.99を¥14.51超過)。
  - **Trend**(`RESULT_PACKET_FIX02_TREND.md`): A2完成(ユーザー承認の`approve_regenerate()`1回・同一テキスト・同一経路でpoint_two PASS、時間差run記録`trend/audio/a2/point_two_time_variance_run.json`)。A2/B1B両方完成。費用集計バグ(level別二重計上)をローカル補正: **Trend総原価=¥337.55**(従来報告¥334.18/「B1B¥160.16」は誤り、正しくはA2¥93.98・B1B¥69.54+本タスク分)。数値はRESULT_PACKET_FIX02_TRENDの値を正とする。
  - **Discovery**(`RESULT_PACKET_FIX02_DISCOVERY.md`): B1B canonical=2文分割版で確定(QA PASS: diff QA Fact Checker PASS/Ledger Deviation受理/Directional non-blocking)、文の丸ごと脱落は解消したがTTS/ASRの言い回し差(a→one、Japan–United States→Japan/U.S.)で3回不合格→ロック、音声未完成=USER_DECISION_REQUIRED。A2長さ: 本文604語(目安280-420の1.44倍)、CURRENT_SPEC L541「A2全体語数は上限なし・意図的に削らない(DECIDED)」、soft target定数はstaged経路に未配線・配線先でも記録のみ、QAは長さを判定しない、「大幅超過時に明示」運用は未規定、短縮候補は生成せず(¥0)。総原価=**¥606.08**。
  - **Voices**(`RESULT_PACKET_FIX02_VOICES.md`、`_2.md`): 一人称は2026-09-08承認済み正式仕様、2V用Writer templateに指示ブロック欠落=Production不整合→最小修正(`er012_b_family_voices_writer_generic_01.py` 2V template、3V無変更、テスト44件+回帰185件PASS)。再生成r1/r2はFact Safety Gate/Local Rewriteが作動しNG(=OPEN-120の2V実発火evidence)、r3で全QA PASS・記事確定(一人称、pov_check)。音声化完了(Gate PASS、321.1秒、mp3、player `voices/audio/b1_2v_v2/`)。Analytical Leakage残存(voice_b/tension)。Status=**PARTIAL / USER TEST READY(一人称版)**、OPEN-151はPARTIALのまま、PRODUCTION_WIRED禁止。総原価=**¥354.72**(¥185.74+¥76.62+¥92.36)。
  - **OPEN-153追記(ユーザー指示、原文要旨)**: 観測仮説として「今回複数のTTS問題が集中したが恒常的なProduction defectと断定しない」。併記する可能性: TTS run-to-run variance/時間依存の一時的不安定性/特定text shapeとの相互作用/記号・数字・長文等の入力前処理不足/ASR側表記揺れ/Gemini version。当面: 標準=Gemini 2.5 Flash TTS。将来retry候補: Gemini 3.1 Flash TTS(仮イメージ: 2.5で通常生成、NG時のみ3.1をretry候補として検証。正式routingではない、詳細は今後Trialで決める)。比較観点: 品質/ASR一致率/読み飛ばし率/retry率/latency/Production 1生成セット総原価。3.1は2.5よりTTS単価が高いため品質だけで評価せずretry削減込みの総原価で比較。再発例追記: Trend A2 point_two時間差runは通過(揺れは双方向)、Discovery B1B言い回し差(a/one、U.S.)、Family C v1のKey Phrase音声stale問題(TTSではなく再利用ロジック起因と区別して記録)。
  - **OPEN-152**: 保持(Validator改修Trialは今回行わない、Discovery B1は人手選定で完成済み)。
  - **OPEN-120**: 2VでのFact Safety Gate実発火evidence(Voices r1/r2、`comment_fact_safety_evidence.json`)を追記。
  - **CURRENT_SPEC**: B-Family Voices 2Vの「一人称指示ブロック欠落」をProduction不整合の修正として記録(仕様自体は不変、修正日・ファイル・commit)。Family C・A2 length契約は変更しない(A2 length「大幅超過時に完成報告で明示」はユーザー判断待ちとしてOPEN_ITEMS候補に記録、PM_GOVERNANCEへは追加しない)。
  - **なぜ機械QA/Audio Validation/closeoutで「完成」と報告できたか(最終REPORT必須、対象ごと)**: Family C(GateはASR一致+level別required_structureのみ、Family Cはrequired_structure無し、player表示文とTTS inputの照合QAが無い、Comment/Intro/Outroは構造要件に無い、再利用ロジックがテキスト未照合)/Discovery A2長さ(上記)/Voices三人称(Leakage/Contract/Fact Checkerは人称を判定しない)/TTS読み飛ばし・表記揺れ(ASR strict verifierは検出しロックしたが、前段の入力前処理が無く、closeout判定は「Gate PASSまたはロック停止」しか見ない)。各RESULT_PACKETの該当節から根拠(関数・仕様行)を引用。新Validatorは追加しない。
- 禁止: `git add -A`/`.`/`stash`/`clean`/`amend`/`rebase`/`force push`、API呼び出し、Production/Trialコード変更、`.gitignore`変更、`*.wav`のadd、gitignore対象のadd、SSOT全文Read。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文・要点)

> 最終報告は対象ごとに: 修正内容/修正前後/runtime evidence/Audio Validation/player URL/direct audio URL/duration/追加費用/Production 1生成セット総原価/unresolved issue/final status。Family Cは特にComment位置/前後volume/SFX/Mother Voice/Key Phrase text-audio consistency/Intro-Outro-title-pause/Story本文不変確認を明示。最後に今ユーザーが試聴すべきURLだけ再掲。最終REPORTでは必ず、なぜ既存QA/Audio Validation/closeout判定で「完成」と報告できてしまったのかを対象ごとに説明。新Validatorを勝手に追加しない。到達Status: Family C=最大VALIDATED(Production採用禁止)、Trend=A2完成可、Discovery=A2/B1試聴可能まで、Voices=一人称修正・OPEN-151はPRODUCTION_WIREDにしない。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_FIX02_FAMILYC.md`、`RESULT_PACKET_FIX02_TREND.md`、`RESULT_PACKET_FIX02_DISCOVERY.md`、`RESULT_PACKET_FIX02_VOICES.md`、`RESULT_PACKET_FIX02_VOICES_2.md` 各全文(REPORT素材・commit対象候補一覧・「なぜ完成と報告できたか」節)。
2. `OPEN_ITEMS.md`: Grep `^\| OPEN-135|^\| OPEN-147|^\| OPEN-151|^\| OPEN-152|^\| OPEN-153|^\| OPEN-120` → 該当行のみ。
3. `DECISION_LOG.md`: Grep `PM-CLOSEOUT-CONSOLIDATION-133` → 直近エントリ位置と索引行。
4. `CURRENT_SPEC.md`: Grep `OPEN-151|2V|Voices可変|一人称` → B-Family Voices 2V段落の末尾位置のみ。
5. `USER-TEST-AUDIO-COMPLETION-01_REPORT.md`: Grep `^## |^### ` → 章立て(FIX-02 REPORTの構成を揃える)。
6. `er014_output/four_type_observation_01/index.html`: Grep `player|<tr|href=` → リンク更新位置。
7. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- (a) Git 1回目: `git status --porcelain -- er013_output/family_c_episode_trial_09/home_robots_v2 er013_family_c_episode_trial_09b_run.py er013_family_c_episode_trial_09b_test_01.py er012_b_family_voices_writer_generic_01.py er012_b_family_voices_variable_voice_count_test_01.py er014_output/four_type_observation_01 docs/pm` → 各RESULT_PACKETのcommit対象候補に従い明示add(mp3・player・JSON・md・driver・er012変更2件・delegation_log・RESULT_PACKET_FIX02_*、wav除外)→ commit → push(classifierブロック時は同一コマンド最大3回再試行)。
- (b) **Web到達確認(push後)**: `curl.exe -sI`で直接音声(raw.githubusercontent): Family C v2 `er013_output/family_c_episode_trial_09/home_robots_v2/web/family_c_home_robots_trial_09b.mp3`(RESULT_PACKET記載の実ファイル名に合わせる)、Trend A2 `er014_output/four_type_observation_01/trend/audio/a2/web/episode.mp3`、Trend B1B(既存)、Discovery A2(既存)、Voices v2 `.../voices/audio/b1_2v_v2/web/episode.mp3`。player(raw.githack、GET 200・text/html): Family C v2、Trend A2、Trend B1B、Discovery A2、Voices v2。各player内相対参照(episode+先頭3 segment)をHEAD 200で確認。CDN遅延時は60秒待ち最大3回。結果を`docs/pm/web_playback_check_FIX02.json`へ。
- (c) 最終REPORT `USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02_REPORT.md`(新規root): 対象別(Family C/Trend/Discovery/Voices)にユーザー指定項目、「なぜ機械QAで完成と報告できたか」を対象別に、費用表(15-8: Trend訂正値の注記、Family C予算枠超過額)、OPEN-153追記内容、未解決(Discovery B1B音声、A2長さ運用、Family C Mother voice印象、Voices Leakage残存)の「何を試したか/何が残ったか/ユーザーに必要な判断」、Web到達確認結果、**「今ユーザーが試聴すべきURL」再掲**(Family C v2/Trend A2/Trend B1B/Discovery A2/Voices v2の5件、URLのみ)。file:///不記載。
- (d) `index.html`更新(v2 player/Trend A2/Voices v2リンク、Trend総原価訂正)。
- (e) SSOT: `OPEN_ITEMS.md` OPEN-135/147/151/152/153/120末尾追記(上記事実)、新規候補行「A2 length大幅超過時の完成報告明示ルール(未規定、ユーザー判断待ち)」はOPEN-154として登録せず、OPEN-135末尾に候補として記載(ユーザー判断後に登録)。`DECISION_LOG.md`: CONS-133直後に`## PM-CLOSEOUT-CONSOLIDATION-134`(4対象結果、Trial-09 v1のVALIDATED取り消し→v2試聴待ち、Voices 2V Prompt不整合修正、Trend承認付き再生成、Discovery短文化、費用訂正、Open Item追記、commit)+索引1行。`CURRENT_SPEC.md`: B-Family Voices 2V段落末尾に不整合修正記録1段落。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`に音声化run行(Family C v2/Trend A2/Voices v2)。
- (f) ACTIVE_TASK固定ヘッダ更新(管理ID=CONS-134、報告単位Status: Family C v2 VALIDATED候補・試聴待ち/Trend A2・B1B READY/Discovery A2 READY・B1B UDR/Voices PARTIAL / USER TEST READY[一人称版])。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-134.md --json-out docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-134_check.json`
2. 回帰(er012変更の最終確認+Family C tests): `.venv\Scripts\python.exe run_project_regression.py --pattern "er012*_test_*.py"`、`.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_09*_test_*.py"`
3. (a)のgit 1回目(メッセージ: `USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02: Family C v2 episode+Trend A2完成+Discovery B1B短文化+Voices 2V一人称修正・音声化`+trailer)→push。
4. (b)到達確認。
5. (c)(d)(e)(f)→ git 2回目(メッセージ: `PM-CLOSEOUT-CONSOLIDATION-134: FIX-02のSSOT反映+最終REPORT+Web到達確認+OPEN-153追記`+trailer)→push。
6. `git log --oneline -3`、`git status --porcelain | Measure-Object -Line`。
- trailer(両commit末尾、空行の後): `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` / `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`

## SSOT追記文

上記(e)に従い実値で記載。PARTIALをOK/PRODUCTION_WIREDと書かない。VALIDATED候補をVALIDATEDと書かない。未完成をREADYと書かない。

## Git(明示add対象・コミットメッセージ・trailer)

上記3・5のとおり。無関係な既存差分(er006_output/er011_output等)はaddしない。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`(上書き)に: 1) commit hash 2件(full)・push結果、2) Web到達確認表(5 player+5 mp3、StatusCode/Content-Length/Content-Type、相対参照解決)、3) 最終REPORTパス、4) SSOT追記位置、5) 回帰結果、6) 費用表(15-8、Trend訂正注記)、7) 試聴URL 5件、8) T-0結果・事前指定外Read、9) push後残差分要約、10) ACTIVE_TASK更新済み。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥0)
- [x] 並行タスク衝突回避あり(単独)
