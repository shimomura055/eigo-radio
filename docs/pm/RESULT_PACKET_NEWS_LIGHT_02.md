# RESULT_PACKET — USER-TEST-NEWS-LIGHT-TOPIC-01-RESUME-02(累積Full Report)

★★★★報告ここから★★★★

0. **T-0**: 委任文を`docs/pm/delegation_log/USER-TEST-NEWS-LIGHT-TOPIC-01-RESUME-02.md`へ保存。`check_delegation_prompt.py`実行結果=`FAIL`(前回`RESUME-01`と同型: 「事前指定Grep一覧」を独立見出しで検出できず[Read一覧に統合記載]、「期限/到達目標Status」「実行コマンド全文」の独立見出しも本委任文はプロセス記述中心のため未検出。内容自体はRead対象・SSOT・Git・報告項目を全て含む。non-blockingとして続行)。JSON: 同ファイル`_check.json`。

## 前回到達点の要約(`docs/pm/RESULT_PACKET_NEWS_LIGHT_01.md`)

記事A2(448語)/B1(384語)は完成済み(Fact Checker/Ledger Deviation/Key Phrase全てPASS相当)。音声はA2`full_story_part2`(Toteme/Kallmeyerブランド名、`ASR_VALIDATION_UNCERTAIN`)とB1`point_one`("only"脱落、`STOPPED`)の2segmentがHuman Review Lockで滞留、Assembly未実行のままSTOPしていた。cost実測¥173.47。

## B1 `point_one`("only"脱落)

1. **時間をあけた再TTS(Step1)**: `approve_regenerate()`で承認後、Production経路(`generate_news_narration_wide_margin`)で3attempt再TTS。**3attemptとも"only"脱落**(classification=`TRUE_CONTENT_MISMATCH`、verified=false)。累計6attempt(前回3+今回3)全て同一箇所で失敗。
2. **"only"が実際に発音されたか**: されていない。Primary ASR 3回とも"only"欠落、独立したlocal faster-whisper verbatim(`er008_disfluency_qa_18.transcribe_verbatim`)でも欠落を確認(`only_present_in_local_verbatim=false`)。
3. **ASR結果**: 3attemptとも"...visual or occasion pieces, with room for a few essentials..."(onlyなし)。
4. **canonical変更(Step2)**: ユーザー承認済みのとおり"only"→"just"へ最小変更(`article.md`/`parts.json`のみ同期、意味変化なし)。
5. **Ledger/QA結果**: Ledger Deviation Check(hook_aware=True)再実行、`overall_status=LEDGER_COMPLIANT`(MINOR 2件、既存傾向と同種、MAJORなし)。Fact Checkerは再実行せず(数値・事実変更なし、指示どおり)。
6. **final segment status**: Step2の**1attempt目でNORMALIZED_MATCH・verified=true**(Primary ASR/local verbatimとも"just"の存在を確認)。`review_lock_state.json`=`RESOLVED`。Assembly実行(325.734秒、peak=0.73052、clippingなし)、Audio Validation Gate **PASS**(override無し)。
7. **player URL+E2E evidence**: `https://rawcdn.githack.com/shimomura055/eigo-radio/e858649a/user_test/unified.html?src=er014_output/user_test_news_light_01/tiny_bags/b1b/player.html&level=B1&en=Are%20Tiny%20Bags%20Really%20Back%3F%20Fashion%27s%20Answer%20Comes%20With%20a%20Catch&ja=%E5%B0%8F%E3%81%95%E3%81%84%E3%83%90%E3%83%83%E3%82%B0%E3%81%AF%E6%9C%AC%E5%BD%93%E3%81%AB%E6%B5%81%E8%A1%8C%E3%81%97%E3%81%A6%E3%81%84%E3%82%8B%E3%81%AE%E3%81%8B%E3%80%81%E3%83%95%E3%82%A1%E3%83%83%E3%82%B7%E3%83%A7%E3%83%B3%E3%81%AE%E7%AD%94%E3%81%88%E3%81%AF%E4%B8%80%E7%AD%8B%E7%B8%84%E3%81%A7%E3%81%AF%E3%81%84%E3%81%8B%E3%81%AA%E3%81%84`。実ブラウザE2E(Playwright、headless Chromium): Play開始→4秒後currentTime=3.88秒(`error=null`/`duration=325.73s`/`readyState=4`)→60秒seek成功→Key Phrase5件・Comment box4件表示確認。evidence: `er014_output/user_test_news_light_01/tiny_bags/b1b/e2e/e2e_evidence.json`+`b1_unified.png`。

## A2 `full_story_part2`(Toteme/Kallmeyer)

1. **Totemeの正しい発音**: 確定不能(Pronunciation Ledger、Perplexity調査、confidence=`low`)。一次情報源[本人音声]なし、二次情報源で"TOH-taym"/"TOH-tem"系の案内が併存。
2. **Toteme IPA**: `ˈtoʊ.teɪm ~ ˈtoʊ.tɛm`(alternate: TOH-tuh-m / TOH-teem)。
3. **Kallmeyerの正しい発音**: 同じくconfidence=`low`(一次情報源なし)だが、Secondary ASR(Phrase List付き)が2回とも綴り完全一致で聞き取れたため、TTSの発音自体は安定・妥当と判断できる。
4. **Kallmeyer IPA**: `ˈkæl.maɪ.ər`(alternate: /ˈkɑːl.maɪ.ər/, /ˈkæl.meɪ.ər/)。
5. **source**: 両entryとも`er006_output/pronunciation_ledger_01/ledger.json`(surface="toteme"/"kallmeyer"、entity_type="cascade_unresolved_entity"、updated_at=2026-09-17、howtopronounce.com/howtosayguide.com等の二次情報源リスト、全文はledger.json参照)。
6. **Primary ASR結果**: 2回とも"Toteme"を"Totem"、"Kallmeyer"を"Kolmeyer"/"Commeire"と誤認(Phrase List非対応のため不変)。
7. **Secondary ASR結果**: 明示的に`ledger_phrases=[Prada,Loewe,Miu Miu,Valentino,Celine,Altuzarra,Toteme,Stella McCartney,Kallmeyer,Chanel,Bottega Veneta]`を渡し(OPEN-159回避、`phrase_list_used=true`を確認)2回実行。**Kallmeyerは2回とも綴り完全一致で解決**。**Totemeは2回とも"Totem"のまま未解決**。独立したlocal faster-whisper verbatim(無料)でも"Totem"。計5系統(Primary×2/Secondary×2/local×1)全てTotemeのみ未解決。
8. **final判断**: **(b)** Secondaryを尽くしても未解決だが、Kallmeyerは正しい発音が確認でき、Totemeは低confidenceながら根拠のある読み方(TOH-tem系)をしている可能性が高い一方、確定的な一次情報源が無いため断定できない。Human Review確認ページを作成しユーザー判断へ委ねる(承認代行なし、Assembly未実行のままSTOP)。
9. **Human Review確認ページ**: `https://rawcdn.githack.com/shimomura055/eigo-radio/e858649a/user_test/human_review.html?src=er014_output/user_test_news_light_01/tiny_bags/a2/human_review/full_story_part2_review.json`(新規`user_test/human_review.html`、query param`src`方式、`unified.html`は無変更)。実ブラウザE2E: Play開始→3秒後currentTime=2.99秒(`error=null`)、canonical script表示・`<mark>`ハイライト2件(Toteme/Kallmeyer)確認。evidence: `er014_output/user_test_news_light_01/tiny_bags/a2/human_review/e2e_evidence.json`+`e2e_screenshot.png`(console上に無関係な`ERR_BLOCKED_BY_RESPONSE.NotSameOrigin`警告1件あり、ページ機能・音声再生には影響なし)。
10. **raw mp3リンクを使っていないこと**: 確認済み。ユーザーへ提示するのは上記確認ページURLのみ、mp3(`a2/human_review/full_story_part2.mp3`)は確認ページ内の`<audio>`要素からのみ相対参照。
11. **Assembly/Gate/player URL(解消時)**: 未解消のため未実行。ユーザー判断後に着手。

## 共通

12. **Sheet投入用情報**: 記事タイトル(English)="Are Tiny Bags Back? Fashion's Answer Is More Complicated"(A2代表)、記事タイトル(日本語)="小さいバッグは本当に流行しているのか、ファッションの答えは一筋縄ではいかない"、記事の概要(日本語)=前回`RESULT_PACKET_NEWS_LIGHT_01.md`2項参照(小型・大型バッグの二極化)、ノーマル(A2)=未完成のためURL空欄、Advanced(B1)=上記7項のURL、備考="最新ニュース(ライト系)"。**A2未完成のためSheet投入は保留**。
13. **cost実測(内訳)**: 本タスク(`audio_fix/raw_usage_log_audio_fix.jsonl`)分=¥6.78(openai_asr ¥0.80、gemini_batch[TTS] ¥4.97、openai[deviation check] ¥1.01、azure[Secondary ASR]はpricing_snapshot未収載のため¥0扱い)。前回¥173.47と合算で**約¥180.25**、上限¥300に対し余裕あり。
14. **PM_GOVERNANCE 9-12/CURRENT_SPEC注記の反映箇所**: `docs/pm/PM_GOVERNANCE.md`9-12節(新設、「## 10. commit / push運用」直前)+変更履歴節末尾1行。委任文では「9-9」指定だったが既存(2026-09-13)のため次の空き番号9-12へ採番(理由を9-12節と変更履歴に明記)。`CURRENT_SPEC.md`「Human Review Route」行末尾に参照注記1行追加(仕様本文は無変更)。
15. **DECISION_LOG/OPEN_ITEMS/ARTIFACT_REGISTRY**: `DECISION_LOG.md`に`## USER-TEST-NEWS-LIGHT-TOPIC-01-RESUME-02`エントリ追加(`## 参照元`直前)。`OPEN_ITEMS.md`OPEN-159行へ「Toteme/Kallmeyer実例(caseを直してもTotemeは解決しなかった)」を追記(新規Open Item化はせず)。`ARTIFACT_REGISTRY.md`News-familyセクションへTiny Bags B1(完成)/A2(未完成、Human Review確認ページURL付き)の2行を追加。
16. **Git SHA**: 成果物+SSOT一式をpush済み。人力レビュー用主要SHA: `8be0ed8e`(B1完成+A2診断+Human Reviewページ初版+PM_GOVERNANCE 9-12)、`e858649a`(human_review.htmlの相対パス解決bug修正、E2E確認済みURLはこのSHA使用)、最終SSOT反映commitのSHAは本ファイルの末尾に追記する。
17. **ユーザー判断**:
    - (A) 仕様・Product・実装判断待ち: なし(既存Production正式retry/Gate/Human Review経路の範囲内)。
    - (B) ユーザー試聴・品質確認待ち: **B1**=上記7項のplayer URLで試聴しPASS/NG判断。**A2**=上記9項のHuman Review確認ページでTotemeの読みを聴取し「許容/再生成/その他」を判断(判断後、許容ならAssembly実行、再生成なら追加タスクとして依頼)。
18. **無変更証跡/事前指定外Read**: `git status --porcelain er0*.py CURRENT_SPEC.md OPEN_ITEMS.md user_test/unified.html`のうち、`er0*.py`(Production module本体)は無変更(新規Trial scriptは`er014_output/user_test_news_light_01/tiny_bags/audio_fix/`配下のみ)。`user_test/unified.html`は無変更(新規`user_test/human_review.html`のみ追加・後日1回だけbug修正)。`CURRENT_SPEC.md`/`OPEN_ITEMS.md`は本タスクの指示どおりの範囲のみ変更。事前指定外Read: なし(事前指定のRead対象[driver/前回RESULT_PACKET/human_review_queue.jsonl/er006_secondary_asr_01.py/er006_pronunciation_ledger_01.py/er011_human_review_lock_01.py/Space Weapons regenスクリプト/docs/pm/closeout_136_e2e/PM_GOVERNANCE該当節]の範囲内で完結)。

★★★★報告ここまで★★★★
