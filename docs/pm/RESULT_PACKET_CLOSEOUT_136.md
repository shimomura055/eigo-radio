# RESULT_PACKET: PM-CLOSEOUT-CONSOLIDATION-136-NEWS-2EP-AND-PN-A2

★★★★報告ここから★★★★

0. **T-0**: 委任文を`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-136-NEWS-2EP-AND-PN-A2.md`へ保存。`check_delegation_prompt.py`結果=`FAIL`(既知パターンと同型: 「範囲(または到達目標Status/禁止事項)」「事前指定Grep一覧+追記位置・更新位置の手順」の独立見出し語が未検出。内容自体は充足、機械判定の見出し語不一致のため非blockingとして続行)。JSON: 同ファイル名`_check.json`。

1. **最終SHAと5本URL**: 最終main=`dd153c7b905f575c30e9497324e61ca00273e424`(RESUME-06`6d088d2e`・PHASE-B-FIX-01`ece38719`を共に祖先に含むこと`git merge-base --is-ancestor`で確認済み)。unified.html変更なしのためこのSHAで確定。
   - Space Weapons A2: `https://rawcdn.githack.com/shimomura055/eigo-radio/dd153c7b905f575c30e9497324e61ca00273e424/user_test/unified.html?src=er014_output/user_test_news_2ep_01/space_weapons/a2/player.html&level=A2&en=The%20New%20Space%20Question%3A%20Is%20the%20Weapon%20in%20Orbit%3F&ja=%E5%AE%87%E5%AE%99%E3%81%AB%E5%85%B5%E5%99%A8%E3%81%AF%E3%81%82%E3%82%8B%E3%81%AE%E3%81%8B%E3%80%81%E3%82%A2%E3%83%A1%E3%83%AA%E3%82%AB%E3%81%8C%E5%88%9D%E3%82%81%E3%81%A6%E5%85%AC%E5%BC%8F%E3%81%AB%E8%AA%8D%E3%82%81%E3%81%9F%E5%87%BA%E6%9D%A5%E4%BA%8B`
   - Space Weapons B1: 上記の`src`を`.../space_weapons/b1b/player.html`・`level=B1`に置換したもの(en/ja同一)。
   - AI Control A2: `https://rawcdn.githack.com/shimomura055/eigo-radio/dd153c7b905f575c30e9497324e61ca00273e424/user_test/unified.html?src=er014_output/user_test_news_2ep_01/ai_control/a2/player.html&level=A2&en=AI%20Is%20Getting%20Stronger.%20But%20What%20Does%20Control%20Really%20Mean%3F&ja=AI%E3%81%AF%E5%BC%B7%E3%81%8F%E3%81%AA%E3%81%A3%E3%81%A6%E3%81%84%E3%82%8B%E3%80%82%E3%80%8C%E5%88%B6%E5%BE%A1%E3%80%8D%E3%81%A8%E3%81%AF%E6%9C%AC%E5%BD%93%E3%81%AF%E4%BD%95%E3%82%92%E6%84%8F%E5%91%B3%E3%81%99%E3%82%8B%E3%81%AE%E3%81%8B`
   - AI Control B1(**RESUME-04の誤り[A2表題流用]を本タスクで是正、B1自身の表題を使用**): `https://rawcdn.githack.com/shimomura055/eigo-radio/dd153c7b905f575c30e9497324e61ca00273e424/user_test/unified.html?src=er014_output/user_test_news_2ep_01/ai_control/b1b/player.html&level=B1&en=AI%20Is%20Getting%20More%20Capable.%20What%20Do%20We%20Actually%20Know%20About%20Control%3F&ja=AI%E3%81%AF%E5%BC%B7%E3%81%8F%E3%81%AA%E3%81%A3%E3%81%A6%E3%81%84%E3%82%8B%E3%80%82%E3%80%8C%E5%88%B6%E5%BE%A1%E3%80%8D%E3%81%A8%E3%81%AF%E6%9C%AC%E5%BD%93%E3%81%AF%E4%BD%95%E3%82%92%E6%84%8F%E5%91%B3%E3%81%99%E3%82%8B%E3%81%AE%E3%81%8B`(ja=はB1が独自Japanese title stageを持たないためA2と同一を流用)
   - Personalized News A2: `https://rawcdn.githack.com/shimomura055/eigo-radio/dd153c7b905f575c30e9497324e61ca00273e424/user_test/unified.html?src=er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/player.html&level=A2&en=The%20News%20You%20See%2C%20and%20the%20News%20You%20Miss&ja=%E8%A6%8B%E3%81%88%E3%81%A6%E3%81%84%E3%82%8B%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9%E3%81%A8%E3%80%81%E8%A6%8B%E3%81%88%E3%81%A6%E3%81%84%E3%81%AA%E3%81%84%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9`

2. **E2E結果表**(Playwright headless Chromium実測、全5本): 全て`error=null`・`paused=false`(4秒後)・60秒seek後も継続再生・KP=5件・Comment box=4件。

| player | currentTime(4s後) | duration(実測) | after seek(60s) |
|---|---|---|---|
| Space Weapons A2 | 3.794s | 365.408s | 61.436s |
| Space Weapons B1 | 3.790s | 382.984s | 61.433s |
| AI Control A2 | 3.824s | 436.123s | 61.424s |
| AI Control B1 | 3.826s | 403.594s | 61.427s |
| Personalized News A2 | 3.826s | 359.264s | 61.426s |

evidence: `docs/pm/closeout_136_e2e/{name}.json`+`.png`(5組)。

3. **unified.html変更**: なし。Personalized News A2は`timelineRender()`の汎用分岐(`isVoicesB1()`/`isFamilyCB1()`いずれにも非該当)を通るため、RESUME-06で追加済みの`.comment` box描画が既に適用されており、実機確認(comment_box_count=4、スクリーンショット)で確定。回帰への追加変更・追加リスクなし。

4. **CURRENT_SPEC.md追記**: 「CEFR-A2 構造・音声仕様」節、`Core Explanatory Logic Preservation`行の直後へ新規行「Topic introのTTS入力(`title_tts`、任意フィールド)」を追加(Status=`PRODUCTION_WIRED`)。`title_tts`未設定時は従来どおり`parts['title']`を使う後方互換設計、表示・canonicalは常に`parts['title']`不変であること、B1側は同等フィールド未実装(A2のみ)であることを明記。

5. **OPEN-163登録**: 「Local Rewrite自動ループの差分QA隙間」。OPEN-141配線のwindow単位diff_qaが`human_review_required=True`へ反転させても、記事全体recheck由来の`major_items`が空だと既存`while major_items and cycle < MAX_REWRITE_CYCLES`(`er003_v1_n3_01_articles_generate.py`等の複数呼び出し元で共通)が継続されず、cycle予算が残っていても`NG_REVIEW_REQUIRED`確定してしまう構造的隙間。AI Control A2(RESUME-04)で実際に発生し手動cycle2/3で解消。優先度=中、期限=量産開始前、Status=`OPEN / DEFERRED(量産開始前)`、関連OPEN-162。

6. **DECISION_LOG行**: `## PM-CLOSEOUT-CONSOLIDATION-136: News 2EP(Space Weapons/AI Control)+Personalized News A2のURL統一・E2E再検証+title_tts SSOT反映+OPEN-163登録`エントリを`## USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-06`エントリの直後・`## 参照元`節の直前に追加。

7. **Sheet投入用3行**:
   - Space Weapons: `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME3.md` 8節を参照(変更なし)。
   - AI Control: 記事タイトル(EN)="AI Is Getting Stronger. But What Does Control Really Mean?"(A2表題、B1は別表題[1節参照])/日本語概要は`docs/pm/RESULT_PACKET_NEWS_2EP_RESUME4.md` 9節を参照/A2 URL=1節/B1 URL=1節。
   - Personalized News A2: 記事タイトル(EN)="The News You See, and the News You Miss"/日本語="見えているニュースと、見えていないニュース"/A2 URL=1節/B1欄="既存B1(2V)player"(`er014_output/four_type_observation_01/voices/audio/b1_2v_v2/`、本タスクでは新規URL生成・既存Sheet掲載有無の確認は未実施)。

8. **Git SHA**: 成果物commit(本タスク分、SSOT+evidence+delegation log+RESULT_PACKET)は本ファイルcommit直後に確定(下記コミット参照)。

9. **API 0証跡**: 本タスクは既存artifactのRead/Grep、Playwright(ローカルCDN GET、課金APIなし)、SSOT編集のみ。`raw_usage_log.jsonl`への新規書き込みなし(TTS/ASR/LLM呼び出し0)。

10. **未決事項/事前指定外Read**: 未決事項は無し(本タスクの範囲内で完結)。事前指定外Read: `er010_ledger_local_rewrite_09.py`(OPEN-163の`MAX_REWRITE_CYCLES`定義元確認のため)、`er003_v1_n3_01_articles_generate.py`/`er003_discovery_focus_staged_production_01.py`等の`while major_items`実装箇所(grep、OPEN-163記述の正確性確認のため)、`er014_output/user_test_news_2ep_01/ai_control/run_pipeline.py`(B1にJapanese title stageが存在しないことの確認のため)。ユーザー試聴・USER_TEST_READY確定・Sheet実投入は引き続きユーザー判断待ち(既存方針を変更せず)。

★★★★報告ここまで★★★★
