## 管理ID

`USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01-FIX-01`(ユーザー試聴Feedback修正)。報告は`docs/pm/RESULT_PACKET_PN_B1_REBUILD_01.md`を累積更新(末尾に「## FIX-01」節、最終★ブロックが累積Full Report)。一時ファイル`docs/pm/ACTIVE_TASK_PN_B1_REBUILD_01.md`継続。現在main=origin/main=`1b51d2f1`(要fetch確認)。**並行Agentなし**。`docs/pm/locks/audio_stage.lock`を原子的作成で取得し終了時に削除。`er005_cost_logger.install()`を最初に呼ぶ。**予算: 本管理ID累計上限¥500(ユーザー更新済み。既使用¥361.22、残≈¥139)。超過見込みならSTOP。**

## 現在Status: `GATE_PASS → USER_DECISION_REQUIRED`。ユーザー試聴の結果、修正要。**修正・全Gate通過後もSonnet/Fableは`USER_TEST_READY`にしない**(到達=`GATE_PASS → USER_DECISION_REQUIRED`、新試聴URLを出してSTOP)。

対象: `er012_output/personalized_news_b1_rebuild_01/`(記事=`b1_2v_new_theme_r8_attempt1/article.md`系canonical、音声=`audio/b1_2v/`)。**Standard(A2)は変更禁止**(`er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/`のsha256一覧before/afterで差分なしを証跡化)。

## ユーザー指示(そのまま実行)

### 1. 人物設定・代名詞の整合(Voice A=男性、Voice B=女性)
- Hook: 「…fit the few minutes **she** has.」→「…fit the few minutes **he** has.」
- Voice A heading: 「The reader who relies on **her** personalized feed.」→「…on **his** personalized feed.」
- Voice B heading: 「The reader who worries her feed is closing in.」=**変更しない**。
- 単純置換で終わらせず、Hook→Voice A→Voice B全体で「一人目=男性、二人目=女性」の代名詞・人物参照が自然に整合することを確認(冒頭のheが一人目男性を指し、Voice A男性へ自然につながる)。人物関係が分かりにくい場合のみ、意味を変えない最小限のmanual wording adjustment可(新Product仕様にしない)。

### 2. Voice A本文の削除
現行: 「Sometimes it even feels less biased than a human editor. I worry I may miss something important, but I do not want to sort through everything myself.」
削除対象=**「I worry I may miss something important, but」全体**(butだけの削除ではない。「I worry I may miss something important.」を残さない)。基本修正後: 「Sometimes it even feels less biased than a human editor. I do not want to sort through everything myself.」つながりが不自然なら意味・立場を変えない範囲でmanual wording adjustment可。Voice Aの便利さ支持の立場不変、新claim追加なし、Research/Ledger claim変更なし。

### 3. Script整合
修正後canonicalを基準に、`article.md`/`parts.json`/scaffold・support texts/Comment・Preview/Key Phrase側の引用/player表示/ASR対象/artifactに旧文言「I worry I may miss something important, but」および旧代名詞「she has」「her personalized feed」(Voice A関連)が残っていないことをgrepで証跡化(Voice Bの「her feed」は維持)。修正後の記事に対し、既存Validator(Analytical Leakage Check 2V 7項目・Ledger Deviation Checker)をoffline再実行し、修正がGateと整合することを確認(Writer再生成はしない。Fact Checkerは事実変更なしのため不要)。Comment/PreviewがVoice Aの旧文言を引用している場合のみ該当textを正式scaffold経路で再生成。

### 4. 全TTS再生成(既存音声流用禁止)
ユーザーは指摘箇所以外でもプツッという機械音/一瞬の音切れ/不自然さ/品質ばらつきを複数確認。→ Advancedの**全segment(14: topic_intro/preview/comment_1-4/point_one_heading/point_two_heading/point_one/point_two/full_story_part1/full_story_part2/tension_reflection/in_one_line)+Key Phrase音声(EN/JA)**を、修正後canonicalで正式Production音声経路(前回と同じ`er012_personalized_news_b1_rebuild_01_audio.py`=Production量産関数呼び出し)で再生成。出力は新dir(`audio/b1_2v_fix01/`)にして旧音声は履歴保持。Voice assignment維持: Voice A=Algieba(男性)、Voice B=Erinome(女性)、voice変更なし。Master Audio Storeの共通ナレーション(Welcome/Outro等)は仕様上再利用されるが、記事固有segmentは全て新規生成であることを`tts_generation_results.json`で証跡化。

### 5. 全TTS再生成後のQA(API成功=PASSにしない)
全segmentについて: 生成成功/ASR validation(cascade)/Script⇔Audio一致/sentence欠落なし/重複読みなし/不自然な無音なし/click・pop・プツッ音なし/segment境界の不自然な切断なし/声質の急変なし/音量の不自然な揺れなし/clippingなし。
**機械的QA手段**(新Production仕様にしない、記事dir配下の監査スクリプト可): (a)local faster-whisper verbatim(`er008_disfluency_qa_18.transcribe_verbatim`)で全segmentの語単位転写→canonicalとの欠落/重複検出、(b)波形解析: 各segment・assembled episodeについて、連続サンプル間の急峻な振幅不連続(click/pop候補: 例えば1ms未満で±0.3以上のジャンプ)、無音区間(>1.5秒)の位置、segment境界前後50msのRMS急変、区間RMSの偏差(音量揺れ)を算出しJSON化(`audit_fix01/audio_qa.json`)、閾値超過箇所は時刻・segment名を列挙し実聴確認(Sonnetが該当区間wavを切り出し、転写・波形で異常有無を判定)。(c)重点確認: A「I do not want to sort through everything myself.」のdo/not/want接続部(音切れ・pop・不自然な間・発音崩れなし)、B 直前文「Sometimes it even feels less biased than a human editor.」との接続、C Hookの「he has」、D Voice A headingの「his」、E Voice Bが女性(Erinome)で維持。異常が残るsegmentは正式retry(attempt上限内)で再生成。**全再生成後も複数箇所で異音・切断が残ればSTOP**。

### 6. Gate再実行
TTS→ASR→Assembly(clipping、headroom)→Audio Validation Gate→player.html→`user_test/unified.html?...&level=B1&en=<タイトル>&ja=<日本語タイトル>`(新SHA)→`docs/pm/tools/user_test_page_e2e_check.py`(5項目)+seek+error=null+script表示一致(新文言を含み旧文言を含まない)+Advanced表示+layout崩れなし(screenshot)。HTTP 200のみ不可。

### 7. SSOT/Git
`DECISION_LOG.md`: `## USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01-FIX-01`(ユーザー試聴Feedback全文要旨、修正前後、全TTS再生成、QA結果、Status)。**併せて「本管理IDの予算上限を¥400→¥500へ更新(2026-09-17ユーザー決定、+¥100)」を記録**。`ARTIFACT_REGISTRY.md`: PN B1(新版)行を新URL・Status`GATE_PASS(USER_DECISION_REQUIRED、再試聴待ち)`へ更新。`OPEN_ITEMS.md`: 新規blocking issueがある場合のみ。`CURRENT_SPEC.md`: **変更禁止**(今回の修正はartifactのFeedback修正、OPEN-167等の未承認仕様を暗黙採用しない)。Dangling Reference Check: 使用する仕様/validator/Production pathが正式仕様として存在、retry/fallbackだけに新原則を追加しない、Writer/TTS/validator/retry間の不整合なし、を確認・報告。Git: 明示add、`git add -A`禁止、wav禁止、mp3可、fetch→merge、trailer `Task-ID: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01-FIX-01`。

## STOP条件
Script修正に新Product判断が必要/Voice A・Bの立場自体を変える必要/Ledger claim変更が必要/全TTS再生成後も複数箇所で異音・切断残存/voice変更が必要/A2への影響が避けられない/新blocking issue/予算¥500超過見込み/git conflict。それ以外(軽微なwording adjustment、TTS再試行、Assembly・E2E再実行)は自律で進める。承認代行禁止。

T-0: 委任文を`docs/pm/delegation_log/USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01-FIX-01.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録(FAILでも継続)。事前指定Read: 本RESULT_PACKET、`er012_personalized_news_b1_rebuild_01_audio.py`、r8記事・`audio/b1_2v/b1b/parts.json`・`tts_generation_results.json`・`audio_validation.json`、`er008_disfluency_qa_18.py`(transcribe_verbatim)、`er003_v1_n3_01_assemble.py`(headroom/clipping)、`docs/pm/tools/user_test_page_e2e_check.py`、PM_GOVERNANCE 9-12・Gate 7(n)。事前指定外Readは理由付き報告。

## 報告項目(「FIX-01」節、★ブロック内、必須20項目)
1.Hook修正前→後 2.Voice A heading修正前→後 3.Voice B heading無変更の証跡 4.Voice A本文の削除前全文 5.削除対象 6.修正後全文 7.manual wording adjustmentの有無・理由 8.男性Voice A/女性Voice Bの人物整合確認(Hook→A→B) 9.全TTS再生成segment数(+Key Phrase音声数、Master Store再利用分の内訳) 10.使用voice 11.「do not want」箇所の再検証結果(転写・波形・実聴) 12.click/pop/音切れQA結果(手法・閾値・検出箇所・処置) 13.ASR結果(segment別) 14.Assembly/Gate(duration/peak/clipping) 15.Browser E2E 16.A2無変更証拠 17.Git SHA/SSOT(予算¥500記録含む)/Dangling Reference Check 18.新Advanced試聴URL 19.未解決事項 20.USER_DECISION_REQUIRED一覧(B: 再試聴)+cost実測。
