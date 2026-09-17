## 管理ID

`PM-CLOSEOUT-CONSOLIDATION-136-NEWS-2EP-AND-PN-A2`(対象報告単位: `USER-TEST-NEWS-2EP-COMPLETION-01`[RESUME-03〜06]、`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01`[PHASE-B/FIX-01])。現在main=`dd153c7b`以降。報告は`docs/pm/RESULT_PACKET_CLOSEOUT_136.md`(新規)へ。

**並行タスクあり**: `USER-TEST-NEWS-LIGHT-TOPIC-01`(er014_output/user_test_news_light_01配下、音声stage→player→DECISION_LOG編集→commit)が実行中。ルール: (1)`er014_output/user_test_news_light_01/`・共有音声store・root `er0*.py`のロジックには触れない。本タスクはSSOT/docs/URL検証/軽微plumbingのみ、**API・TTS実行0**。(2)SSOT編集・git操作は`git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/PM_GOVERNANCE.md`で自分以外の未commit変更が無いことを確認してから(あれば5分間隔で最大30分待つ)。commit前に`git fetch origin`→`git merge origin/main --no-edit`(rebase/force push禁止、競合時STOP)。全文Write禁止。`docs/pm/ACTIVE_TASK.md`は最後に1回固定ヘッダで上書き。

## 目的(Fable自律判断によるcloseout整合、ユーザー判断不要事項のみ)

1. **URL統一・E2E再検証**: 最終SHA(fetch後のorigin/main、少なくとも`dd153c7b`以降でunified.htmlのComment box表示[RESUME-06]を含む)で、以下5本のrawcdn unified.html URLを生成し、Playwright(headless Chromium)で各URLのPlay→`currentTime`進行/`paused=false`/`error=null`/seek/Key Phrase表示/**Comment box表示の有無**を確認、evidence JSON(+png)を`docs/pm/closeout_136_e2e/`へ保存(小サイズ)。
   - Space Weapons A2/B1(`er014_output/user_test_news_2ep_01/space_weapons/{a2,b1b}/player.html`)
   - AI Control A2/B1(`.../ai_control/{a2,b1b}/player.html`)。**B1の`en=`はB1自身の表題 "AI Is Getting More Capable. What Do We Actually Know About Control?" を使う**(RESUME-04ではA2表題が入っていた)。`ja=`はB1の日本語タイトル(B1 player/parts.jsonの日本語タイトルを確認して使用。A2と同一ならそのまま)。
   - Personalized News A2(`er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/player.html`、level=A2、en="The News You See, and the News You Miss"、ja="見えているニュースと、見えていないニュース")。**Voices A2の表示分岐でComment boxが適用されているか確認**。適用されていない場合、`user_test/unified.html`の該当分岐へRESUME-06と同じ`.comment` box描画を最小追加(他分岐・既存記事の表示を壊さないこと、household/Space Weaponsで回帰確認)。適用に大きな改修が必要ならunified.htmlは触らず報告のみ。
2. **SSOT整合(Dangling Reference解消)**:
   - `CURRENT_SPEC.md`: RESUME-06で`er003_v1_n3_01_tts_generate.py::generate_a2_segments()`に追加された任意フィールド`parts["title_tts"]`(TTS入力専用、表示・canonical不変、未設定時は従来どおり`title`、Key Phraseの`japanese_gloss`/`japanese_gloss_tts`分離と同型)を、「CEFR-A2構造・音声仕様」節のTopic intro/日本語タイトル関連行または適切な行へ**追記**(Status=`PRODUCTION_WIRED`、根拠=USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-06、後方互換・regression 2896件PASS)。B1側(`generate_b1_segments`相当)に同等フィールドが無い場合は「A2のみ実装、B1は未対応(必要時に同型で追加)」と明記。
   - `OPEN_ITEMS.md`: **OPEN-163**新規登録: 「Local Rewrite自動ループの差分QA隙間: OPEN-141配線の差分QA(対象文±1文)が`human_review_required=True`へ反転させても、全体recheck由来の`major_items`が空だと`while major_items and cycle < MAX_REWRITE_CYCLES`が継続せず、cycle予算が残っていても`NG_REVIEW_REQUIRED`確定する(AI Control A2、2026-09-17、RESUME-04で手動cycle2/3により解消)。優先度=中、期限=量産開始前。改善案候補: diff_qa由来のhuman_review項目もループ継続条件へ含める(Production変更、ユーザー承認後)。関連OPEN-162」。Status=`OPEN / DEFERRED(量産開始前)`。書式はOPEN-159〜162に合わせる。
   - `DECISION_LOG.md`: 本IDエントリ(URL統一・E2E再検証結果・title_tts SSOT反映・OPEN-163登録・unified.html Comment box適用範囲)。
3. **報告用集約**: 5本の最終URL、Sheet投入用3行(Space Weapons/AI Control/Personalized News A2[Voices系、B1は既存`er014_output/four_type_observation_01/voices/audio/b1_2v_v2/`のplayerが既にSheet掲載済みか不明のため、A2欄のみ記入しB1欄は「既存B1(2V)player」とURLがあれば記載])。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1/D-1/G-1/F-1は従来どおり(`docs/pm/PM_GOVERNANCE.md`該当節参照、Read/Grep最小化・Diff優先・重複作業回避)。T-1: 事前指定外Readは理由を1行記録。T-0: 委任文を`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-136-NEWS-2EP-AND-PN-A2.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録(FAILでも継続)。

## 事前指定Read/Grep一覧

- `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME4.md` 8-9節、`RESULT_PACKET_NEWS_2EP_RESUME6.md` 4-6節、`RESULT_PACKET_PN_A2_PHASE_B_FIX1.md` 5-6節
- `user_test/unified.html`: Grep `isVoicesB1|isFamilyCB1|timelineRender|\.comment|Comment`
- `er014_output/user_test_news_2ep_01/ai_control/b1b/parts.json`: Grep `title|japanese`
- `er003_v1_n3_01_tts_generate.py`: Grep `title_tts`(追加箇所の行番号のみ)
- `CURRENT_SPEC.md`: Grep `^## CEFR-A2構造|日本語タイトル|Topic intro|topic_intro`(追記位置)、`OPEN_ITEMS.md` L304-312(OPEN-159〜162書式)、`DECISION_LOG.md`: Grep `^## USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-06`
- `docs/pm/PM_BRIEF.md` L135-159

## 実行コマンド全文

1. `git fetch origin` → `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/PM_GOVERNANCE.md`で並行タスク以外の未commit差分が無いことを確認。
2. `git merge-base --is-ancestor <RESUME-06 SHA> HEAD` / `<PHASE-B-FIX-01 SSOT SHA> HEAD`で最終SHAの祖先関係を確認。
3. Python(`.venv/Scripts/python.exe`)+Playwright(sync API、headless Chromium)で5本のrawcdn unified.html URLに対しPlay/4秒待機/60秒seek/Key Phrase・Comment box DOM件数を取得し、`docs/pm/closeout_136_e2e/<name>.json`+`.png`へ保存。
4. `CURRENT_SPEC.md`/`OPEN_ITEMS.md`/`DECISION_LOG.md`をEdit toolで追記(Write全文禁止)。
5. `docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-136-NEWS-2EP-AND-PN-A2.md --json-out <同名>_check.json`を実行。
6. `git add`(対象ファイルのみ明示)→`git commit`→`git push`。

## Git

明示add(closeout_136_e2e/、unified.html[変更時]、CURRENT_SPEC/OPEN_ITEMS/DECISION_LOG、delegation_log、RESULT_PACKET)。メッセージ`PM-CLOSEOUT-CONSOLIDATION-136: News 2EP+PN A2のURL統一・E2E再検証+title_tts SSOT反映+OPEN-163登録`、trailer `Task-ID: PM-CLOSEOUT-CONSOLIDATION-136-NEWS-2EP-AND-PN-A2`。push。URLは成果物commit(unified.html変更があればそのcommit、無ければ現行最終SHA)で確定し、RESULT_PACKETに記載。

## 報告(`docs/pm/RESULT_PACKET_CLOSEOUT_136.md`)

0. T-0 1. 最終SHAと5本URL(全文) 2. E2E結果表(5本: currentTime/paused/error/seek/KP/Comment box) 3. unified.html変更の有無・内容・回帰 4. CURRENT_SPEC追記行 5. OPEN-163登録内容 6. DECISION_LOG行 7. Sheet投入用3行 8. Git SHA 9. API 0証跡 10. 未決事項/事前指定外Read。ユーザー向け表記は「B1」に統一。
