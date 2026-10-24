# CP_CHECK_01 / 手順書 (FAMILY-X-MOON-SHRINKING-PRODUCTION-01 委任_01、2026-10-24、準備段階=有料API 0)

直近の同種制作『英単語ガチャ』(FAMILY-X-WORD-GACHA-PRODUCTION-01: `docs/research/FAMILY-X-WORD-GACHA-PRODUCTION-01/{CP_CHECK_01,FACT_CHECK_01,BUDGET_PLAN_01,RUNTIME_EVIDENCE_01,CLOSEOUT_01}.md`、`er019_output/word_gacha/`、audio production wiring run)の手順を正とし、同じ正式経路・コマンド列・Gate・試聴ページ形式を踏襲する。**本委任では起動しない(次委任で起動)。**

## §A 着手時の整合確認
| # | 確認事項 | 結果(照合箇所) |
|---|---|---|
| 1 | 正式Production経路 | text=`er019_family_x_entertainment_production_runner_01.py --stage all`(Research→Ledger→B3[決定論annotation producer]→注記契約V1〜V10→W-1 Writer R0-R2→Advanced英訳→Advanced RF→Standard→Standard RF→Review Queue)、audio=`er019_family_x_audio_production_runner_01.py --level both`(plan/scaffold/tts/assemble)。『英単語ガチャ』(`er019_output/word_gacha/run_wg_01/entry_point.json`)・直近Newsと同一経路・同一既定(tts_backend=speech_metadata_flash_lite、style_profile=fx_20261017)。slug=`moon_shrinking`、run=`run_ms_01`。 |
| 2 | 仕様 | CURRENT_SPECの該当節(Family X Production経路W-1/RF、Entertainment、音声構造、KP、PNAP、中核数値丸め)は既配線。本作固有のPrompt/機構/例外は追加しない。`--theme`に確認済み要点と誤解防止を記載(入力準備済み: `er019_output/moon_shrinking/theme.txt`)。 |
| 3 | Key Phrase | A-1・課題②(所有格)=PRODUCTION_WIRED。**課題①X2p'(UDR #179 APPROVED_FOR_PRODUCTION 2026-10-24)は commit `d8fb8f9a4`(委任_35、`er003_key_words_gloss_alignment.py`)でXYZ共通のKP gloss新規生成経路へ配線済み**(新flagなし。`EIGO_KP_GLOSS_ALIGNMENT`は未設定のまま)。本作の正式runはX2p'配線後の仕様で動く(委任文の前提どおり)。 |
| 4 | ASR/TTS/retry/fallback/HR | 現行仕様。ASR数値・時刻修正 commit d6d17562b(OPEN-487)/7d4ec5bc4(OPEN-491)/1d104d711(OPEN-494)は`git merge-base --is-ancestor`でHEAD(`d8fb8f9a4`)に含まれる(下記§D)。『英単語ガチャ』で顕在化したASR同音(gacha->gotcha)はOPEN-498(別管理ID)で独立継続。本作の語彙リスク: lobate scarp / LRO / ShadowCam / megaregolith / Moon等(固有名詞アラーム・PNAPが既存仕様どおり働く)。 |
| 5 | 日次予算 | BUDGET_PLAN_01.md参照(X≤100円)。 |
| 6 | STOP確認 | `tools/stop_scope_check_01.py --managed-id FAMILY-X-MOON-SHRINKING-PRODUCTION-01 --run-dir er019_output/moon_shrinking/run_ms_01` rc=0(`stop_check_00.json`)。 |

## §B 次委任の起動コマンド列(『英単語ガチャ』と同形、`.venv/Scripts/python.exe`)
**各起動の直前に** `.venv/Scripts/python.exe tools/stop_scope_check_01.py --managed-id FAMILY-X-MOON-SHRINKING-PRODUCTION-01 --run-dir er019_output/moon_shrinking/run_ms_01 --out docs/research/FAMILY-X-MOON-SHRINKING-PRODUCTION-01/stop_check_<段>.json`(rc=3なら新規API呼出をせず停止報告)。

| # | 段 | コマンド | 想定 | 備考 |
|---|---|---|---|---|
| 1 | text(全段1起動) | `er019_family_x_entertainment_production_runner_01.py --theme "$(cat er019_output/moon_shrinking/theme.txt)" --slug moon_shrinking --out-dir er019_output/moon_shrinking/run_ms_01 --source-note "ナゾロジー 2026-10-24 https://nazology.kusuguru.co.jp/archives/203095 ; Watters et al. 2026 PSJ 7(10) 239 https://doi.org/10.3847/psj/ae9eae ; FAMILY-X-MOON-SHRINKING-PRODUCTION-01 委任_02(ユーザー指示)" --run-label run_ms_01 --budget-jpy 100 --stage all` | 約10分、約35〜40円 | `--theme "$(cat ...)"`のargv往復は検証済み(1071字一致)。Research→Ledger→B3→W-1 R0-R2→Adv→Std→RF。**終了後にFACT_CHECK_01 §6の禁止表現を本文へgrep(0件確認)**。Ledger VERIFIEDで一次研究(DOI)が根拠になっているか確認 |
| 2 | audio(both) | `er019_family_x_audio_production_runner_01.py --slug moon_shrinking --run run_ms_01 --level both --stage all --budget-jpy 100` | 約25分、約50円 | plan/scaffold/tts/assemble。TTSはrunner内で直列(cooldown 600秒を含む)。**手で並列起動しない** |
| 3 | HR Lock時 | 停止して報告(`approve_regenerate`は**Fable/ユーザー承認の後のみ**、正規関数のみ。Gate緩和・独自判断で解除しない) | — | 『英単語ガチャ』は part3 の gacha->gotcha で HR Lock(Adv)。承認後の再生成は `--stage tts --only-segments <seg>`(1起動) |
| 4 | assemble再実行(HR解決後) | `er019_family_x_audio_production_runner_01.py --slug moon_shrinking --run run_ms_01 --level <a2|b1b> --stage assemble --budget-jpy 100` | 数分、API 0 | Advで `BLOCKED_STYLE_PROFILE_GATE`(LOCAL_REWRITE_RECOVERY等)の場合は `er003_v1_n3_01_assemble.record_human_approval` が**人間承認**を要する(runnerはGateを解除しない)→Fable/ユーザーへ報告 |
| 5 | 試聴ページ | `er019_nws2_final_page_01.py --audio-dir er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_01 --out user_test/family_x_moon_shrinking_01 --tag FAMILY_X_MOON_SHRINKING_PRODUCTION_01 --title-ja "月は少しずつ縮んでいる?"` → commit/push(GitHub Pages公開) | API 0 | Std/Adv切替・通し・パート別・全スクリプト・KP、開発者向け情報なし |
| 6 | page_verify | `er019_nws2_play_verify_01.py --url https://shimomura055.github.io/eigo-radio/user_test/family_x_moon_shrinking_01/index.html --out docs/research/FAMILY-X-MOON-SHRINKING-PRODUCTION-01/page_verify_01.json --expect-adv <Adv秒> --expect-std <Std秒> --tag FAMILY_X_MOON_SHRINKING_PRODUCTION_01` | API 0 | HTTP 200・audio全件再生・seek・KP table・console error 0 が PASS条件 |

- **有料run起動回数**: text 1起動 + audio 1起動(`--stage all`)が基本=合計2起動。HR再生成・assemble再実行は『例外起動』(Fable承認後のみ、各1回)。再起動は委任文が許可した回数のみ。
- **RESTART_STORM回避**: 同一runの起動は最低150秒空ける(300秒窓に3起動で`FAMILY_X/Z_RESTART_STORM`を自行発動する)。データ誤りは起動前にまとめて直す(1つずつ直して再起動しない)。`<run>/STOP`・`RESTART_STORM_LOCK.json`は自分で削除・`--clear-stop`しない(解除はFable/ユーザー)。
- **TTS直列化**: audioは`--level both`でrunnerが内部直列(Std→Advまたはrunner定義順、cooldownはrunnerが待機)。別プロセスでの手動並列TTSは禁止。**並列にできるのは text生成の後の独立作業(試聴ページ準備・SSOT準備など、API/TTSを使わないもの)のみ**。
- **Z(告げ口心臓)との並列**: X text(約10分)とZ writer系は独立ファイル・独立runなので同時起動してよい(同一rate limitに注意。同時TTSはX audioとZ tts_*が重ならないよう、起動時刻をずらす[どちらかのTTSが終わってから次のTTS])。
- **異常**: 自分が起動したprocessが外部から停止された、または原因不明のrc≠0が2回続いた場合は再起動せずSTOP報告。`taskkill //IM python.exe`等は禁止(自分のPIDのみ)。

## §C 原作忠実性ではなく『事実忠実性』チェックポイント(次委任で本文確定後に記入)
FACT_CHECK_01.md §3(数値・期間・根拠)・§5(不確実性6件)・§6(禁止/許容表現)を、確定した Std/Adv 本文とScript表示に機械grep+目視で照合する(`CP_CHECK_02`または本ファイル追記)。最低限: ①『約42〜46m』『推定/見積もり』 ②『ここ数億年(約4億年前から仮定)』 ③『最大約11cm/百万年(一定の速さと仮定)』 ④『750m〜1.1kmの予想との食い違い、理由は未決着』 ⑤『今も続いている可能性(断定なし)』 ⑥禁止表現0件。

## §D 事前チェック(import graph未commit差分、HEAD=`d8fb8f9a4`、2026-10-24 22:1x JST)
- import graph算出: 静的import+文字列によるモジュール参照の推移閉包(roots: `er019_family_x_entertainment_production_runner_01`・`er019_family_x_audio_production_runner_01`・`er_user_listening_page_common_01`・`er019_nws2_final_page_01`・`er019_nws2_play_verify_01`)=**163 module**。`git status --porcelain`でM/D/??のあるもの=`er062_family_z_structure_01.py`(M)のみ(**本委任のZ登録data追加=自分の変更。commit後に解消**)。他agentのX2p'実装差分は着手時(`M er003_key_words_gloss_alignment.py`・`M er003_test_kp_fulltext_wiring_01.py`)に存在したが、**22:05:56にcommit `d8fb8f9a4`として確定済み**(作業ツリーのer003*は clean)。
- 次委任の起動条件: 上記graph内のtracked .pyが全てcommit済みでHEADと一致(`git status --porcelain`でgraph内0件)・STOP/LOCK sentinelなし・`stop_scope_check` rc=0。
- 公開先 `user_test/family_x_moon_shrinking_01/`: 未使用(`ls user_test`/`git ls-files`で0件)。`er019_output/moon_shrinking/run_ms_01`: 未作成(theme.txtのみ準備)。
