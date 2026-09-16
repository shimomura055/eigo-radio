管理ID: USER-TEST-WEB-AUDIO-EXPORT-01

1. T-0: FAIL(reason: コマンドブロック内の```区切り行を「引数/絶対パス欠落」と誤検知する既知の誤検知パターン。必須キーワード8/8・固定ブロックE-1/D-1/G-1/F-1/T-1は全てOK。作業は継続、`docs/pm/delegation_log/USER-TEST-WEB-AUDIO-EXPORT-01_check.json`に記録済み)。

2. 6対象(householdはA2/B1で計7 episode):
| 対象 | 元WAV | 一意確定根拠 | episode.mp3 | サイズ/長さ | segment export | raw URL |
|---|---|---|---|---|---|---|
| Young travelers A2 | a2/rerun_01/a2/assembled/...A2_FAMILY_A_COMPLETION...wav | player.html file:///参照が単一候補 | `a2/rerun_01/web/episode.mp3` | 4,006,128B / 359.8s | 24件 | 206 |
| Young travelers B1 | b1b/assembled/...B1B_FAMILY_A_COMPLETION...wav | 同上 | `b1b/kp5_regen_and_completion_01/web/episode.mp3` | 3,846,168B / 337.3s | 27件 | 206 |
| Refrigerator A2 | household.../a2/assembled/...A2_HOUSEHOLD...wav | 同上(共通player内A2/B1両方参照) | `household.../web/episode_a2.mp3`(命名変更、下記参照) | 3,583,656B / 330.0s | 24件 | 206 |
| Refrigerator B1 | household.../b1b/assembled/...B1B_HOUSEHOLD...wav | 同上 | `household.../web/episode_b1.mp3`(命名変更) | 3,501,696B / 302.5s | 27件 | 206 |
| Free-address A2 | .../a2/assembled/B_Family_A2_Production_Wiring_01.wav | player.html file:///参照が単一候補 | `.../web/episode.mp3` | 3,984,696B / 350.5s | 29件 | 206 |
| Free-address B1 | .../b1b/assembled/B_Family_Production_Phase1_B1B.wav | 同上 | `.../web/episode.mp3` | 3,546,792B / 305.1s | 28件 | 206 |
| AI hiring B1 3V | .../b1b/assembled/B_Family_3V_Audio_Trial_01_B1B.wav | 同上 | `.../web/episode.mp3` | 4,229,736B / 356.6s | 30件 | 206 |

household_unified_final_candidate_01は単一player.htmlがA2/B1両方のepisode wavを参照するため、`web/episode.mp3`単独では一意に決められない。委任文の「ファイル名:episode全文は原則web/episode.mp3」の「原則」に基づき`web/episode_a2.mp3`/`web/episode_b1.mp3`の2ファイルへ変更(逸脱を明記)。web_delivery.json等の裏付けファイルは6対象とも存在せず、player.html直接参照(file:///単一候補)のみで一意確定。

3. 作成Repo path: episode 7件(Refrigerator分2件含む)+segment 189件+`export_manifest.json` 6件(household分は1つのmanifestにA2/B1両方の53エントリを記録)。commit差分は計204ファイル追加。

4. commit SHA `56ed8bf627f4fa8e204fbadd3d06adaa5ac2cda1`、`git push origin main`成功(`a9fadf34..56ed8bf6 main -> main`)。

5. 未対応対象: なし(STOP該当0件、6対象全てepisode+segmentともexport完了。再生成は一切行っていない)。

6. TTS/API 0件証跡: 変換スクリプト(`export_web_audio_01.py`、スクラッチパッドのみ・repo未配置)のimportは`os, re, hashlib, json, soundfile`のみ(genai/openai/requests/er0*系productionモジュールなし)。player.html/SSOT/Productionコード無変更証跡: `git show --stat 56ed8bf6`に`player.html`/`.wav`が0件、`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`変更なし。既存の未commit差分(`er011_output/attempt_history.jsonl`等4件、本タスク以前からのM)は`git status --porcelain`上も引き続きMのまま(本commitに含まれず)。

7. 事前指定外Read: なし(全て事前指定Read/Grep一覧の範囲内で実施)。

備考: ユーザー向け表記は「B1」に統一(内部pathの`b1b`はそのまま)。
