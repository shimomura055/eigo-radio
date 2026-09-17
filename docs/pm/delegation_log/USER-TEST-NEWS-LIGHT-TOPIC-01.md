## 管理ID

`USER-TEST-NEWS-LIGHT-TOPIC-01`。現在main=`5740f747`以降。報告は`docs/pm/RESULT_PACKET_NEWS_LIGHT_01.md`(新規、累積Full形式)へ。

**並行タスクあり(衝突回避ルール)**: `USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-04`(AI Control音声)、`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01`、`USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-06`(Space Weapons A2タイトルTTS+B1表示修正、`user_test/unified.html`編集)が順次実行中。(1)**本タスクの音声stage(TTS/ASR/Assembly/Gate=共有store書き込み)は、marker `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME6.md` が存在するまで開始しない**(5分間隔で最大180分。超過時は記事stage完了までで停止し「音声stage待ち」と報告)。記事stage(Research/Ledger/Writer/QA/Scaffold text/Key Phrase選定/日本語タイトル)はOpenAIのみで即実行可。(2)`user_test/unified.html`・`build_web_player_common.py`・root `er0*.py`・他タスクの出力dirは変更しない(RESUME-06がunified.htmlのComment区切り表示を修正中。本タスクのplayerはその修正済みunified.htmlで表示確認する)。(3)SSOT編集(DECISION_LOG)・git操作は最後にまとめ、`git status --porcelain DECISION_LOG.md OPEN_ITEMS.md CURRENT_SPEC.md docs/pm/PM_GOVERNANCE.md user_test/unified.html`で自分以外の未commit変更が無いことを確認(あれば5分間隔で最大30分待つ)。commit前に`git fetch origin`→`git merge origin/main --no-edit`(rebase/force push禁止、競合時STOP)。全文Write禁止。`docs/pm/ACTIVE_TASK.md`は最後に1回だけ固定ヘッダで上書き(他タスク状態保持)。

## 性質/到達Status/禁止事項

- 性質: News系ユーザーテスト用に、ライトで俗的な話題「小さいバッグがまた流行?」(仮題 "Are Tiny Bags Back?"、Research結果に基づき自然なNewsタイトルへ調整可)を、**通常News正式Production経路**(Space Weaponsと同一: Research 1回→Verified Fact Ledger→A2/B1をLedgerから直接独立生成→QA→Scaffold→Key Phrase→TTS→Assembly→Audio Validation Gate→player)でA2/B1完成させ、ユーザー試聴用URLまで到達する。
- 到達Status: 「技術的再生確認済み/ユーザー試聴・品質確認待ち」まで(`USER_TEST_READY`確定はユーザー試聴OK後)。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`変更禁止。
- 禁止: B1→A2翻案、Research/TTSの無意味な再実行、Prompt改善Trial、Productionコード改修、Gate緩和、Human Approvalの代行(ただし下記の既知誤検知クラスの扱い参照)、`git add -A`/`stash`/`amend`/`rebase`/`force push`、wavのcommit。
- コスト: 標準pipeline(Research+A2/B1+音声)で¥250〜400想定。retry等で**¥600**を超える見込みならSTOP。

## ユーザー指示(原文要旨、忠実転記)

### 1. テーマ
仮テーマ "Are Tiny Bags Back?"(Research結果に基づき自然なNewsタイトルへ調整可)。日本語イメージ「小さいバッグがまた流行?」。**タイトルで「流行している」と断定できるかはResearchで確認**。
### 2. 狙い
硬いNews(AI/宇宙安全保障/政策/社会問題)ではなく、**ファッション・消費・ライフスタイル寄りの気軽に聞けるNews**。「ただのゴシップ」にはせず、なぜ小さいバッグが再び注目されているのか/実用性よりアクセサリー性か/大きなバッグとの二極化があるか/有名人やFashion Weekの影響/荷物を減らす・minimalismとの関係、などResearchで裏付けられる範囲から記事の軸を決める。
### 3. Research方針
最新情報をResearch。優先: Vogue/ELLE/Harper's Bazaar/Marie Claire/major fashion publications/Fashion Week coverage/credible retail・trend sources。ブランド・著名人の具体例は可だがcelebrity gossip中心にしない。**「tiny bags are back」という結論ありきでResearchしない**(mini bagsが戻っている/large bagsも同時に強い/特定ブランド・ランウェイだけの現象/celebrity styling中心、等の可能性)。Verified Fact Ledgerに基づき最も正確で面白い切り口を選ぶ。
### 4. Article
A2/B1をそれぞれLedgerから直接生成(翻案なし)。商品カタログにしない。最低限 Hook/最近何が起きているか/具体例/背景・理由/反対側または別トレンド/In One Line の流れ。
### 5. 避けること
「全員がtiny bagを使っている」等の過度な一般化/1人のcelebrityだけを根拠にtrend認定/ブランド宣伝記事化/商品価格の羅列/「minimalismが原因」等の根拠なき因果/「Gen Zが〜」等Ledgerにない世代一般化/「経済不安で流行」等の安易な因果/trend sourceが弱い状態での「大流行」断定。
### 6. Key Phrase: A2はA2本文、B1はB1本文から、既存共通selection/canonicalization経路。
### 7. 日本語タイトル: 記事生成時にconfig/引数で供給(固定辞書追加前提にしない)。英語タイトルの自然な日本語化、新Factを足さない。
### 8. Scaffold/Comment/Preview: 既存News正式Production仕様。Preview/Key Phrase/Comments/Full Story/In One Lineまで完成。
### 9. TTS/Audio: 正式経路(TTS/ASR/Human Review Lock/retry・fallback・regeneration/Assembly/Audio Validation Gate)完走。**既知のplayer配置問題を再発させない**(player.htmlは記事dir直下、相対path `web/episode.mp3`が正しく解決)。HTTP statusではなく**実ブラウザ(Playwright headless Chromium)でPlay操作**: Play開始/currentTime進行/seek/script表示/Key Phrase表示/audio errorなし をE2E evidence(JSON+png)として保存。
### 10. ユーザーテストページ: 既存unified page形式。全体Play/Preview・Commentを含む全script表示/効果音等はscriptから除外/Key Phrase EN+日本語意味/**Commentと本文が視覚的に明確に分離**(Space Weapons B1で指摘された引っ付き表示を再発させない。RESUME-06でunified.html側に区切りが入る予定。本タスクのE2E確認時にスクリーンショットで分離を確認し、分離していなければ報告[unified.htmlは本タスクでは変更しない])。
### 11. 自律判断: 上位方針から一意/ネガほぼ無/低risk/追加コスト目安¥100以内/大きな時間消費なし なら逐一UDRにせず判断して進める。
### 12. STOP条件(以下のみ): Researchから「tiny bags are back」というテーマ自体が成立しない/信頼できるFactが不足/新Product仕様判断が必要/Production正式pathに欠落/Fact・Ledgerが正式retryでも解消不能/ASRで実質的誤読/playerが正式構成で再生不能/¥100を大きく超える追加コスト(上記¥600基準)/既存承認仕様の変更が必要。軽微なplumbing/config/path/regressionは自律対応可。
### 13. 期待成果物: A2 article/B1 article/Verified Fact Ledger/Fact・Deviation QA/Scaffold/Key Phrase/日本語タイトル/A2 audio/B1 audio/Assembly・Gate PASS/A2・B1 user-test page/browser E2E再生証跡/URL/Sheet投入用情報/SSOT/commit・push。

## Fableからの補足(既存経路・既知事項)

- 正式経路の実装例: `er014_output/user_test_news_2ep_01/space_weapons/run_pipeline.py`(Research→Ledger→A2/B1→QA→Scaffold→TTS→Assembly→Gate、Production module呼び出しのみ)と`ai_control/run_pipeline.py`。本タスクは`er014_output/user_test_news_light_01/tiny_bags/run_pipeline.py`として複製し、TOPIC/THEME_ID/BASE_DIR/日本語タイトルconfigのみ差替え(Prompt本文無変更)。Researcherのtopic引数に上記§2〜3・§5の観点(結論ありきにしない、fashion publications優先、避けること)を**既存build_researcher_promptのtopic引数として渡す範囲**で反映。
- Ledger Deviationで「Ledgerに無い一般化・概念名」がMAJAORになった場合(Space Weapons/AI Controlの前例): 既存Local Rewrite(最大3 cycle)→Diagnostic Full Retry 1回の正式経路内で、Ledger語彙の範囲へ収める(Fable判断済みの扱い、OPEN-162参照)。それでも未解消ならSTOP。
- 音声Human Review Lock: ASRが`EXACT_MATCH`/`NORMALIZED_MATCH`で本文一致しているのにrepetition/disfluency QAのみで停止した場合(OPEN-160/161の既知誤検知クラス)は、**News 2EP限定の事前承認は本タスクには適用されない**ため、承認代行せず当該segmentをmp3 exportしてSTOP報告(固有名詞・数値誤読/UNCERTAINも従来どおりSTOP)。ただし正式retry policy内のTTS再生成は可。
- player生成: `er014_output/user_test_news_2ep_01/build_web_player_common.py`をimportして使用可(変更禁止)。**player.htmlの出力先は記事dir直下**(`.../tiny_bags/a2/player.html`、`.../tiny_bags/b1b/player.html`)、`web/episode.mp3`+segmentsは`web/`配下。RESUME-05の修正経緯: `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME5.md` 1-3節。
- URL形式: `https://rawcdn.githack.com/shimomura055/eigo-radio/<FINAL_SHA>/user_test/unified.html?src=er014_output/user_test_news_light_01/tiny_bags/<a2|b1b>/player.html&level=<A2|B1>&en=<URL_ENCODED_EN>&ja=<URL_ENCODED_JA>`。CDN反映遅延は60秒×最大5回。E2E手順はRESUME-05と同じ(Playwrightは`.venv`導入済み想定)。
- 語数報告義務: 各本文語数、280未満/500超は明記。B1 Fact Checker `REVIEW_REQUIRED`はER-010-NO9どおりnon-blocking advisory。
- Sheet投入用行: 記事タイトル(English)/記事タイトル(日本語)/記事の概要(日本語、2〜3文)/ノーマル(A2)=URL/Advanced(B1)=URL/備考=最新ニュース(ライト系)。
- SSOT: DECISION_LOGに本IDエントリ(テーマ採用理由・Research実態・タイトル決定・QA・音声・E2E・cost・Status)。OPEN_ITEMS/CURRENT_SPEC/PM_GOVERNANCE無変更(独立した新問題を発見した場合は報告、低risk・低costなら同時解消可)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)
E-1: 同一ファイル再読禁止。D-1: Grep→該当行範囲Read(自作driverの複製元は全文可)。G-1: git出力最小化。F-1: transcript退避不要。T-1: 事前指定外Readは理由をRESULT_PACKETに1行記録。T-0: 委任文を`docs/pm/delegation_log/USER-TEST-NEWS-LIGHT-TOPIC-01.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録(FAILでも継続)。

## 事前指定Read/Grep一覧
- `er014_output/user_test_news_2ep_01/space_weapons/run_pipeline.py`全文、`ai_control/run_pipeline.py`(差分箇所のみ)、`build_web_player_common.py`(関数signatureのみ)
- `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME5.md` 1-4節、`docs/pm/RESULT_PACKET_NEWS_2EP_RESUME3.md` 7-8節(URL/Sheet書式)
- `CURRENT_SPEC.md`: L796-860(通常News Reference仕様)、Grep `^## Key Phrase$|^## Preview$`→該当節冒頭
- `DECISION_LOG.md`: Grep `^## USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-0[3-6]`(直近書式)、`docs/pm/PM_BRIEF.md` L135-159

## 実行コマンド全文
1. `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-NEWS-LIGHT-TOPIC-01.md --json-out docs\pm\delegation_log\USER-TEST-NEWS-LIGHT-TOPIC-01.md_check.json`
2. `mkdir -p er014_output/user_test_news_light_01/tiny_bags`(driver複製先)
3. `.venv\Scripts\python.exe er014_output\user_test_news_light_01\tiny_bags\run_pipeline.py --stage research`
4. `.venv\Scripts\python.exe er014_output\user_test_news_light_01\tiny_bags\run_pipeline.py --stage article`
5. `.venv\Scripts\python.exe er014_output\user_test_news_light_01\tiny_bags\run_pipeline.py --stage audio`(marker確認後)
6. `.venv\Scripts\python.exe er014_output\user_test_news_light_01\tiny_bags\run_pipeline.py --stage player`
7. Playwright E2E script(`.venv\Scripts\python.exe`経由、evidence JSON+png出力)
8. `git add <個別ファイル>` → `git commit -m "..."` → `git fetch origin` → `git merge origin/main --no-edit` → `git push origin main`

## 手順
1. T-0。2. driver複製・config設定(日本語タイトルは英語タイトル確定後に自然な直訳へ更新)。3. Research→Verification→Ledger(1回)。**Ledgerでテーマが成立するか判定**(「mini bags復活」を裏付けるVERIFIED factが十分か/むしろ二極化やランウェイ限定か)→成立しない場合はSTOP。成立する場合、Ledgerに即した切り口とタイトルを決定(断定可否をLedgerで判断、例: "Are Tiny Bags Back?"の疑問形は断定を避けられる)。4. A2/B1生成→Fact Checker/Ledger Deviation/Local Rewrite→Cross-level整合(目視、矛盾なし明記)→Scaffold→Key Phrase 5件→日本語タイトル。5. marker確認→音声stage(A2→B1)。6. player 2本(記事dir直下)+web export。7. Git成果物commit(明示add、wav除外)→push→最終SHAでURL 2本→E2E再生確認(Playwright、evidence JSON+png、Comment区切りのスクリーンショット確認)。8. Sheet投入用1行。9. SSOT(衝突回避ルール)→RESULT_PACKET/ACTIVE_TASK commit→push。メッセージ`USER-TEST-NEWS-LIGHT-TOPIC-01: ライトNews「小さいバッグ」A2/B1完成(Research→Ledger→記事→音声→player→E2E)`、trailer `Task-ID: USER-TEST-NEWS-LIGHT-TOPIC-01`。

## SSOT追記文
DECISION_LOGに`## USER-TEST-NEWS-LIGHT-TOPIC-01`エントリを追記(テーマ採用理由・Research実態・タイトル決定・QA・音声・E2E・cost・Status)。OPEN_ITEMS/CURRENT_SPEC/PM_GOVERNANCEは無変更(独立した新問題を発見した場合は報告のみ、低risk・低costなら同時解消可)。

## Git(明示add対象・コミットメッセージ・trailer)
明示add対象: `er014_output/user_test_news_light_01/tiny_bags/**`(wav除外)、`DECISION_LOG.md`、`docs/pm/RESULT_PACKET_NEWS_LIGHT_01.md`、`docs/pm/ACTIVE_TASK.md`、`docs/pm/delegation_log/USER-TEST-NEWS-LIGHT-TOPIC-01.md*`。
コミットメッセージ: `USER-TEST-NEWS-LIGHT-TOPIC-01: ライトNews「小さいバッグ」A2/B1完成(Research→Ledger→記事→音声→player→E2E)`
trailer: `Task-ID: USER-TEST-NEWS-LIGHT-TOPIC-01`

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_NEWS_LIGHT_01.md`(★★★★報告ここから/ここまで★★★★)
0. T-0 1. 実際に採用した記事タイトル(EN/JA)と決定理由 2. Researchから見えた「tiny bag trend」の実態(Ledgerが裏付ける範囲での要約、断定可否) 3. A2/B1の記事要旨(各3行)+語数 4. Ledger件数(VERIFIED/AMBIGUOUS/REJECTED) 5. QA結果(Fact Checker/Ledger Deviation/Local Rewrite回数/Cross-level) 6. Audio(segment数、Human Review Lock有無、Assembly duration/peak/clipping、Gate) 7. browser E2E再生結果(A2/B1: 数値・path、Comment区切りの確認) 8. A2 URL 9. B1 URL 10. Sheet投入用情報 11. cost(実測、内訳) 12. model/routing 13. Git SHA 14. SSOT(DECISION_LOG行、無変更証跡) 15. ユーザー判断(A: 仕様判断待ち/B: 試聴・品質確認待ち[URL提示後]) 16. 未決事項 17. 無変更証跡(`git status --porcelain er0*.py CURRENT_SPEC.md OPEN_ITEMS.md user_test/unified.html`が空)/事前指定外Read(理由付き)。ユーザー向け表記は「B1」に統一。
