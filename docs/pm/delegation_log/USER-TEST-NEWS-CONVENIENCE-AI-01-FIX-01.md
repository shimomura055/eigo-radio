## 管理ID

`USER-TEST-NEWS-CONVENIENCE-AI-01-FIX-01`(Fable受入照合による差し戻し1回目)。報告は`docs/pm/RESULT_PACKET_NEWS_CONVENIENCE_AI_01.md`を累積更新(前回の★ブロックを保持しつつ、末尾に「## FIX-01」節を追加し、最終★ブロックが累積Full Reportになるよう再構成)。一時ファイル`docs/pm/ACTIVE_TASK_NEWS_CONVENIENCE_AI_01.md`を継続使用。現在main=origin/main=`a1d915b9`(要fetch確認)。

## 並行Agent注意(重要)

`B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01`のsonnet-workerが並行実行中(`er012_*`、`er012_output/**`、`er014_output/four_type_observation_01/**`、SSOT追記)。前回同様、**TTS/ASR/Pronunciation Ledger登録の前に`docs/pm/locks/audio_stage.lock`を作成**(他タスクのlockがあれば60秒pollで最大60分待機)、音声段階後に削除、lockはcommitしない。SSOT編集は最後にまとめ、直前に`git fetch origin`→`git merge origin/main --no-edit`→編集→即commit→push。conflict時は自力解決せずSTOP。`er012_*.py`・`user_test/*.html`・Production module(`er003_*`等)は変更しない。

## Fableが発見した是正必要点(ユーザー試聴前に直す。今日=2026-09-17)

**(1) 時制・事実の誤り(Fact Checker `REVIEW_REQUIRED`は今回は真陽性)**: Ledgerでは「レモンタルト(ピクルス風味)」は**2026-09-29発売予定**、「おいものカヌレ」は**2026-09-22発売予定**で、いずれも本日時点で未発売。しかし記事は既発売として書いている。
- A2 `article.md` L13「So this was a regional launch, not a nationwide or permanent product.」(未来の発売を過去形)、L21「The product launched across Japan in September 2026, but it was quantity-limited.」(**未発売を発売済みと断定=事実誤り**)。L11「Lawson scheduled... It was planned for...」は許容範囲だが自然な未来表現(is scheduled / will be sold)へ揃えてよい。
- B1 `article.md` L15「It was a regional launch, not evidence of...」(同上)、L19「"Oimo no Canele — with Caramel Sauce" launched nationwide on September 22, 2026, as a limited-quantity product.」(**事実誤り**)。
→ Ledgerに沿った最小修正(例: "is scheduled to go on sale on September 22, 2026, nationwide, in limited quantities" / "This will be a regional launch, not a nationwide or permanent product")。新Factは追加しない。「非恒久(not permanent)」はLedgerに直接根拠がなければ削る(Fact Checker A2指摘)。

**(2) A2の1文が32語**(L13「But it shows one way some major Japanese convenience-store chains are using AI around food: a computer can suggest a starting idea, while people decide whether it belongs on the shelf.」)。本記事の最重要条件(音声だけで理解できる簡単さ)とA2仕様(最長18語、CURRENT_SPEC L539-542)に反するため、2〜3文に分割(各≤18語、平易語)。他にも18語超の文があれば同様に分割(A2のみ。B1は最長22語で範囲内、変更不要)。

**(3) B1 `parts.json` part1冒頭に「## Main Story」が混入**し、そのままTTS入力text(`audit/tts_generation_results.json` L416)になっている(OPEN-165)。ASRに"Main Story"は出ていないが、canonicalと入力の不整合、player script表示への混入の恐れがある。→ `parts.json`(および同じcanonicalを持つ全artifact)から見出し行を除去(artifact側の修正のみ。`split_article_text()`のProduction修正はOPEN-165でユーザー判断待ちのまま)。B1 `article.md`の`## Main Story`見出し自体は記事構造として残してよいが、canonical本文には含めない。

## 手順

1. **Local Rewrite正式経路**(`er010_ledger_local_rewrite_09`、diff QA[OPEN-141]付き)で(1)(2)を実施。経路が「Ledger逸脱の修正」専用で時制修正・文分割に使えない場合は、最小限の手動編集+同経路のdiff QA相当(変更文のみの差分一覧・語数・Ledger照合)を報告に載せる。変更後、A2/B1とも**Ledger Deviation Check再実行**(`LEDGER_COMPLIANT`必須)+**Fact Checker再実行1回**(時制指摘が解消したことの確認。REVIEW_REQUIREDが残る場合はその理由を報告、advisory扱いは既存仕様どおり)。
2. 変更文を含む全artifactを同期: `article.md`、`parts.json`、A2 `a2_support_texts.json`等、Preview/Comment(scaffold出力)に誤時制や変更文の引用があれば該当textのみ再生成(正式scaffold経路)。Key Phraseは変更文由来のものがあれば存在確認(消えた場合のみ共通経路で再選定、B1→A2流用禁止)。
3. **Pronunciation Ledger登録**: "Oimo no Canele"(日本語「おいものカヌレ」、ローマ字読み /oimo no kanɯɾe/ 相当、"canelé" /ˌkænəˈleɪ/)をLedger正式経路で登録(cache hit時は再調査不要)し、Secondary ASRで`ledger_phrases`に明示的に渡す(OPEN-159回避、`phrase_list_used=true`を証跡化)。"Lawson"/"FamilyMart"も必要なら同様。
4. **影響segmentのみ再TTS**(正式経路、cascade Secondary+Phrase Listまで。TTS再生成条件はcanonical変更=正当): 想定=A2 `full_story_part2`(または該当part)・`point_two`、B1 `full_story_part1`(見出し除去+語順問題の再確認)・`point_two`(または該当part)、変更したPreview/Comment。無関係segmentは再生成しない。既存Human Review Lock中segmentは`approve_regenerate()`で承認記録(canonical変更による再生成=ユーザー承認不要の正式手順、Human Approval[現音声の承認]は記録しない)。
5. cascade後もUNCERTAIN/STOPPEDが残る場合: 新canonicalでHuman Review確認ページJSONを更新(PM_GOVERNANCE 9-12、raw mp3禁止、pronunciation_info必須、Playwright E2E)、該当レベルはSTOP。B1「Then Lawson」語順問題が再発した場合も同様。
6. 全segment解消したレベル: Assembly(Gate、override禁止)→player(`build_web_player_common.py`、記事dir root)→`user_test/unified.html`形式URL→Playwright E2E(evidence保存)→Sheet行。B1 playerのscriptに"## Main Story"が表示されないことを確認。
7. 情報密度チェック再計測(A2/B1: 語数・平均/最長文長・数字出現数・難語・論点数)を報告。
8. SSOT: `DECISION_LOG.md`に`## USER-TEST-NEWS-CONVENIENCE-AI-01-FIX-01`エントリ(Fable受入照合で発見した3点と是正結果)。`OPEN_ITEMS.md` OPEN-162行へ「本件ではFact Checker REVIEW_REQUIRED[時制]が真陽性だった」観測を1行追記、OPEN-165行へ「artifact側で見出し除去し対応、Production修正は据え置き」を追記。`ARTIFACT_REGISTRY.md`のA2/B1行更新。明示add、wav禁止、mp3可。commit分割可、trailer `Task-ID: USER-TEST-NEWS-CONVENIENCE-AI-01-FIX-01`。
9. **費用上限¥100**(Local Rewrite/Deviation/Fact Checker≈¥20、TTS4〜6 segment≈¥30、ASR≈¥10目安)。`er005_cost_logger.install()`を最初に呼び計測漏れを防ぐ。超過見込みならSTOP。

## STOP条件

費用¥100超見込み/再生成後もHuman Review必要(該当レベルのみSTOP、他は完了まで)/Ledger Deviation非COMPLIANT/新仕様判断が必要/git conflict。承認代行禁止。

T-0: 委任文を`docs/pm/delegation_log/USER-TEST-NEWS-CONVENIENCE-AI-01-FIX-01.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録(FAILでも継続)。事前指定Read: 前回RESULT_PACKET、driver、両`article.md`/`parts.json`、`audit/fact_check*.json`、`er010_ledger_local_rewrite_09.py`(API)、Space Weapons regenスクリプト、`docs/pm/closeout_136_e2e/`。事前指定外Readは理由付き報告。

## 報告項目(累積★ブロック内に「FIX-01」として追加)

F0.T-0 F1.変更文一覧(before→after、A2/B1、語数) F2.Ledger Deviation/Fact Checker再実行結果 F3.Preview/Comment/Key Phrase同期結果 F4.Ledger登録内容(surface/hint/source) F5.再TTS結果(segment別attempt/分類/cascade/phrase_list_used) F6.Human Review残(あれば確認ページURL+E2E) F7.Assembly/Gate/duration F8.A2 URL/B1 URL+E2E evidence F9.Sheet行 F10.情報密度再計測 F11.cost F12.Git SHA F13.SSOT F14.ユーザー判断 A/B F15.無変更証跡/lock記録/事前指定外Read。
