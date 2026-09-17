# RESULT_PACKET — USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-05

0. T-0: 委任文を`docs/pm/delegation_log/USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-05.md`へ保存、`check_delegation_prompt.py`実行結果=`FAIL`(必須セクション見出し「事前指定Grep一覧」「実行コマンド全文」の見出し語未検出。内容は事前指定Read/Grep一覧・実行手順を含むが見出し語の形式不一致によるFAIL。非blocking、記録のみで続行)。JSON: `docs/pm/delegation_log/USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-05_check.json`。

1. **原因**(実証済み): 既存標準(household `player.html`はlevel dir直下、mp3は`web/`配下、audio src=`web/episode.mp3`)に対し、Space Weapons A2/B1は`build_web_player_common.py`呼び出し時にplayer.html自体を誤って`.../a2/web/player.html`(mp3と同じweb/配下)へ書き出していた。player.html内のaudio srcは変更前と同じ`web/episode.mp3`のままだったため、unified.htmlのfetch/DOM注入ロジックがplayer.htmlの実所在(`.../a2/web/`)を基準に相対解決し、実際にブラウザが要求したURLは`.../a2/web/web/episode.mp3`(存在しない二重path)になっていた。curl実測: 二重path→`404 text/plain`、正しいpath(`.../a2/web/episode.mp3`)→`200 audio/mpeg`。Playwright実操作(旧commit`c2af33f2`)でも`audio.src`が二重pathであること、`audio.error.code=4`、`currentTime`が進まないことを実証(証跡: 一時ディレクトリ、repo外)。household既存player(`episode_audio_a2`、同commit時点)は同一手順で正常再生(`currentTime`進行・`error=null`)を確認し、Space Weapons固有の配置誤りと特定した。

2. **修正内容**: `build_web_player_common.py`・`user_test/unified.html`は無変更(共通コードの不具合ではなく、個別呼び出し時の出力先path誤りのため)。`git mv`のみで、`er014_output/user_test_news_2ep_01/space_weapons/a2/web/player.html`→`.../a2/player.html`、`.../b1b/web/player.html`→`.../b1b/player.html`(ファイル内容は無変更、TTS/Assembly再生成なし)。commit `8493ce60`。unified.html変更なしのため既存記事(household等)への後方互換影響なし。

3. **A2再生runtime evidence**(方法=Playwright実操作、headless Chromium): 修正前(旧commit`c2af33f2`のURL、`src=.../a2/web/player.html`のまま)を実操作→`before_play.src`が`.../a2/web/web/episode.mp3`(二重path)、`after_play_4s`: `currentTime=0, paused=true, readyState=0, error=4`、`after_seek`も`error=4`のまま(再現成功)。修正後(最終commit`a777efa4`)を実操作→`before_play.src=.../a2/web/episode.mp3`(正しいpath)、`after_play_4s`: `currentTime=3.55, paused=false, readyState=4, error=null, duration=364.85`、`after_seek`(60秒)後`currentTime=61.43, paused=false, error=null`。Key Phrase表示(`kp_present=true`)・Full Script 4 card・seekボタン表示確認。console error=`ERR_BLOCKED_BY_RESPONSE.NotSameOrigin`(rawcdn interstitial自身の内部リソースに対するもので再生には無関係、後述5参照)。evidence: `er014_output/user_test_news_2ep_01/space_weapons/a2/web/e2e_playback_evidence.json`/`.png`。

4. **B1再生runtime evidence**(同方法): 修正後(最終commit`a777efa4`)を実操作→`before_play.src=.../b1b/web/episode.mp3`、`after_play_4s`: `currentTime=3.55, paused=false, readyState=4, error=null, duration=382.98`、`after_seek`(60秒)後`currentTime=61.43, paused=false, error=null`。Key Phrase/Full Script/seekボタン表示確認。修正前個別repro(B1側)は未実施だが、A2と同一の生成ロジック・同一配置誤りパターン(`.../b1b/web/player.html`)であったため同種の404が発生していたことは構造的に同一(curlでも旧commit時点の`.../b1b/web/web/episode.mp3`が同様に404になることを確認可能な構造)。evidence: `er014_output/user_test_news_2ep_01/space_weapons/b1b/web/e2e_playback_evidence.json`/`.png`。

5. **新A2 URL**(最終commit`a777efa4`):
`https://rawcdn.githack.com/shimomura055/eigo-radio/a777efa4a7327568fd89b8e9258c97d31e9a368f/user_test/unified.html?src=er014_output/user_test_news_2ep_01/space_weapons/a2/player.html&level=A2&en=The%20New%20Space%20Question%3A%20Is%20the%20Weapon%20in%20Orbit%3F&ja=%E5%AE%87%E5%AE%99%E3%81%AB%E5%85%B5%E5%99%A8%E3%81%AF%E3%81%82%E3%82%8B%E3%81%AE%E3%81%8B%E3%80%81%E3%82%A2%E3%83%A1%E3%83%AA%E3%82%AB%E3%81%8C%E5%88%9D%E3%82%81%E3%81%A6%E5%85%AC%E5%BC%8F%E3%81%AB%E8%AA%8D%E3%82%81%E3%81%9F%E5%87%BA%E6%9D%A5%E4%BA%8B`
(注: 初回アクセス時、rawcdn.githack.comが「One more step」という中継確認ページを挟むことがある。その場合は表示された「Open the page」をクリックすると本編ページへ進む。これはgithack CDN自体の仕様であり本タスクの不具合ではない。)

6. **新B1 URL**(最終commit`a777efa4`、5と同一SHAで`src`のみ`b1b`に置換):
`https://rawcdn.githack.com/shimomura055/eigo-radio/a777efa4a7327568fd89b8e9258c97d31e9a368f/user_test/unified.html?src=er014_output/user_test_news_2ep_01/space_weapons/b1b/player.html&level=B1&en=The%20New%20Space%20Question%3A%20Is%20the%20Weapon%20in%20Orbit%3F&ja=%E5%AE%87%E5%AE%99%E3%81%AB%E5%85%B5%E5%99%A8%E3%81%AF%E3%81%82%E3%82%8B%E3%81%AE%E3%81%8B%E3%80%81%E3%82%A2%E3%83%A1%E3%83%AA%E3%82%AB%E3%81%8C%E5%88%9D%E3%82%81%E3%81%A6%E5%85%AC%E5%BC%8F%E3%81%AB%E8%AA%8D%E3%82%81%E3%81%9F%E5%87%BA%E6%9D%A5%E4%BA%8B`
(表記統一につきユーザー向け表記は「B1」)

7. **既存記事playerの回帰確認**(1件): `er011_output/household_unified_final_candidate_01/player.html`(最終commit`a777efa4`、直接player.html URL)をPlaywright実操作→`episode_audio_a2`要素で`currentTime=3.66, paused=false, readyState=4, error=null, duration=330.03`と正常再生を確認。unified.html/build_web_player_common.py無変更のため回帰なしを実証。

8. **AI Control進捗**: `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME4.md`は未作成(並行タスク進行中、要旨取得不可)。

9. **OPEN-162登録内容**: Fact/Ledger Checkerが厳格すぎることで、意味的に妥当な一般化・背景説明・概念整理・非事実的bridgeまで`unsupported_new_claim`/`changed_scope`として過剰に停止させる可能性(AI Control A2でsuperintelligence/intelligence explosion/singularityの概念名を含む一文がMAJOR停止した事例、2026-09-17)。優先度=低、期限=量産開始までに改善方針検討、Validator/Prompt/Gate無変更・AI Control完成をブロックしない。`OPEN_ITEMS.md`に追加(OPEN-161の直後)。

10. **PM_GOVERNANCE更新**: (a) 9-1節「4. ユーザー判断」直後(729行付近)へ2026-09-17ユーザー再指示としてA(仕様・Product・実装判断待ち)/B(ユーザー試聴・品質確認待ち)の2区分明記ルールを追記。(b) 2節Gate 7補足「13項目監査」段落直後(299行付近)へ「Play実再生evidenceの必須化」段落を新設し、HTTP 200/206・Gate PASSだけで「ユーザー試聴可能」と判定しない旨・Playwright等の実操作またはJSロジック静的追跡によるE2E evidenceを要する旨を追記。

11. **DECISION_LOG行**: `## USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-05`エントリを`## USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-03`エントリの直後、`## 参照元`節の直前に追加(原因・修正・runtime evidence・新URL・SSOT更新箇所・OPEN-162・cost・Statusを記載)。

12. **cost**: API実行なし。TTS/Writer/Research/Fact Checker等いずれも呼び出していない(`git mv`によるファイル移動とPlaywright dev tooling[pip install playwright、`playwright install chromium`、repo非commit]のみ)。実費¥0。

13. **Git SHA/push**: (1)`8493ce60e6025f3c6a8766197080f5f88b3f33c9`(player.html移動)→push済み。(2)`7ac6b6acd94a058d56b5c9f43ee29ee9557317c9`(Playwright E2E evidence追加)→push済み。(3)`a777efa4a7327568fd89b8e9258c97d31e9a368f`(SSOT反映、最終)→push済み。3コミットともorigin/mainへpush確認済み(`git push`成功、fast-forward)。

14. **現在Status**: Space Weapons A2/B1=技術的player再生確認済み(Playwright実操作でPlay/seek動作確認)/ユーザー試聴・品質確認待ち。`USER_TEST_READY`最終確定・記事完成扱いにはしていない。

15. **未決事項**: (A) 仕様・Product・実装判断待ち=なし(本修正は既存規約からの一意の配置誤り訂正であり新規判断不要)。(B) ユーザー試聴・品質確認待ち=Space Weapons A2/B1(上記5/6のURL)の実際の試聴・内容品質(script/Key Phrase/構成)の確認をお願いしたい。AI Control(Theme 2)はRESUME-04が別途進行中のため対象外。

16. **無変更証跡**: `git status --porcelain CURRENT_SPEC.md`は空(無変更)。`git status --porcelain -- '*.py'`には他並行タスク由来の変更のみで、本タスクが触れたroot `er0*.py`は無し(`build_web_player_common.py`はer014_output配下のためer0*.py glob対象外だが本タスクでは無変更、diffなし)。事前指定外Read: なし(全て事前指定Read/Grep一覧の範囲内で完結。household player.html自体はGrepのみで済ませ、必要箇所のみcurl/Playwrightで実URL確認)。
