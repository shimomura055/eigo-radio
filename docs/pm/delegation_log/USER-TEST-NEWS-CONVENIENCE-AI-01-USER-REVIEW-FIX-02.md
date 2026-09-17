## 管理ID

`USER-TEST-NEWS-CONVENIENCE-AI-01-USER-REVIEW-FIX-02`。報告は`docs/pm/RESULT_PACKET_NEWS_CONVENIENCE_AI_01.md`を累積更新(既存★ブロックの末尾に「## FIX-02」節を追加、最終★ブロックが累積Full Reportになる形)。一時ファイル`docs/pm/ACTIVE_TASK_NEWS_CONVENIENCE_AI_01.md`継続。現在main=origin/main=`fcb14d23`(要fetch確認)。**並行Agentなし(本タスク単独)**。`docs/pm/locks/audio_stage.lock`は原子的作成(`open(path,"x")`)で取得し終了時に削除(PM_GOVERNANCE 8節追記済みルール)。

## ユーザー正式判断(2026-09-17、そのまま実行)

### B1(`full_story_part1`)
記事全体は**OK/承認**。ただし表示script「Lawson then planned a sale of the finished product.」に対し、ユーザーが聞いた音声は「Then Lawson planned a sale of the finished product.」。
**方針(ユーザー承認済み)**: まず実audio/ASR evidence(FIX-01再生成後の`audit/tts_generation_results.json`・cascade転写・local faster-whisper verbatim[`er008_disfluency_qa_18.transcribe_verbatim`、無料]で再確認)。実音声が"Then Lawson planned..."と確認できれば、**音声を正としてscript/canonical側を"Then Lawson planned a sale of the finished product."へ最小修正**(`article.md`/`parts.json`/canonical保持箇所/player script)。TTS再生成不要、内容の追加変更禁止、当該文のみ。Ledger意味整合(語順のみ、事実不変)を確認、player再build(`build_web_player_common.py`、記事dir root)、Playwright E2Eでscript表示が新文言であること+再生確認。実audioがユーザー報告と異なる場合のみSTOP報告(修正しない)。B1について再試聴要求不要、Status=ユーザー品質承認済み(語順整合修正のみ)。

### A2 `point_two`
- `AI while` = **USER APPROVED**(現音声許容、修正対象外)。
- `Canele` = **USER APPROVED**(不必要に変更しない)。
- `Oimo no` = **USER REJECTED / REGEN REQUIRED**(ユーザー実聴では"Yomono no"のように聞こえ、「お芋」相当の読みに聞こえない)。
- **B1版`point_two`の"Oimo"実読はユーザー確認済みでOK** → referenceとして使ってよい。

**再生成方針**: 対象は`point_two`のみ(記事全体・他segment再生成禁止)。手順:
1. B1 `point_two`の正常な"Oimo"読みを確認(B1 wav/ASR転写/local verbatim。B1のTTS呼び出し条件[voice/style/instruction/Ledger hint使用有無]も記録し、A2との差を特定)。
2. Pronunciation Ledger(登録済み"Oimo no Canele"、hint "oh-EE-moh noh kah-nuh-LAY")/pronunciation supportを利用。TTS Pronunciation Hint注入(`er006_pronunciation_tts_injection_01.augment_style_prefix_with_pronunciation`)はCURRENT_SPEC L1276で`NOT_WIRED(TTS生成側)`のため、**Production TTS経路への新規配線はしない**。使えるのは既存経路内の手段(Ledger→Secondary ASR Phrase List、既存retry/fallback、A2既存のstyle/instruction)のみ。B1側で効いている条件がA2経路にも既存で存在するならそれを使う。新規配線が必要と判断した場合はSTOP(新Product判断)。
3. `approve_regenerate()`で承認記録(ユーザーREGEN REQUIRED)→A2 `point_two`を正式経路で再TTS(Production attempt上限内)。
4. Primary ASR → Secondary ASR(Phrase List明示、`phrase_list_used=true`)。
5. "Oimo no Canele"の読み確認: ASR転写+local verbatim+B1 referenceとの比較(可能なら両wavの該当区間の転写比較)。「お芋」相当(/oi.mo/、"OH-ee-mo")に読めているかを根拠付きで判定。
6. "AI while"を含む他部分に新しい不整合がないことを確認(AI whileの転写ゆれ自体は許容済み)。
7. 自動検証で十分に確定(cascade should_pass、かつOimo読みが根拠付きで妥当)→Human Review Lock close→Assembly(Gate、override禁止)→player→`user_test/unified.html`形式URL→Playwright E2E→Sheet行確定→ARTIFACT_REGISTRY/DECISION_LOG/OPEN_ITEMS/Git。
8. 発音不確実性が残る場合のみ新Human Review確認ページ(9-12: raw mp3禁止/ブラウザ再生/canonical script/"Oimo no Canele" highlight/正しい発音情報/IPA・learner cue/Primary・Secondary ASR/**B1 referenceとの差**/確認ポイント、E2E後にURL提示)。承認代行禁止。

## STOP条件
B1実audioがユーザー報告と一致しない/Oimo再生成後も正しい読みにならない(attempt上限)/Secondaryまで回しても発音未確定(→確認ページ作成後STOP)/再生成により別の内容不一致/新Product判断が必要(例: TTS Hint配線)/費用¥100超/git conflict。

## SSOT/Git
`DECISION_LOG.md`: `## USER-TEST-NEWS-CONVENIENCE-AI-01-USER-REVIEW-FIX-02`(B1ユーザー承認+語順script修正、A2 point_two判断内訳[AI while/Canele承認、Oimo REGEN]、再生成結果、Status)。`OPEN_ITEMS.md`: OPEN-159へ「日本語ローマ字商品名のTTS読み(Oimo→Yomono型)」観測を追記(新規Open Item化はFable判断のため、追記のみ)。`ARTIFACT_REGISTRY.md`: A2/B1行更新。ユーザーテスト記事一覧(CLOSEOUT-03で確認した管理表があれば)へ追加/更新。明示add、wav禁止、mp3可、fetch→merge、trailer `Task-ID: USER-TEST-NEWS-CONVENIENCE-AI-01-USER-REVIEW-FIX-02`。`er005_cost_logger.install()`を最初に呼ぶ。

## 事前指定Read一覧

本RESULT_PACKET(FIX-01節)、`fix_01_pipeline.py`、両`parts.json`/`article.md`、`audit/tts_generation_results.json`(A2/B1)、`audit_fix_01/retts_*_result.json`、`er006_pronunciation_ledger_01.py`、`er003_v1_n3_01_tts_generate.py`(A2/B1 point_two生成関数と条件差)、`docs/pm/RESULT_PACKET_NEWS_LIGHT_03.md`(記事一覧・Human Approval手順の先例)、`docs/pm/closeout_136_e2e/`。事前指定外Readは理由付き報告。

## 事前指定Grep一覧

T-0: 委任文を`docs/pm/delegation_log/USER-TEST-NEWS-CONVENIENCE-AI-01-USER-REVIEW-FIX-02.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録(FAILでも継続)。

## 実行コマンド全文

- `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs/pm/delegation_log/USER-TEST-NEWS-CONVENIENCE-AI-01-USER-REVIEW-FIX-02.md --json-out docs/pm/delegation_log/USER-TEST-NEWS-CONVENIENCE-AI-01-USER-REVIEW-FIX-02.md_check.json`

## 報告項目(「FIX-02」節、★ブロック内)
B1: G1.実audio確認結果(ASR転写/local verbatim) G2.script修正前後 G3.audio/script一致 G4.player再build+E2E G5.final status
A2: G6.Oimo再生成attempt(回数/分類) G7.B1 referenceとの比較(TTS条件差+転写差) G8.Primary/Secondary ASR(phrase_list_used) G9.final pronunciation判定(根拠) G10.AI while維持確認 G11.Assembly/Gate(duration/peak/clipping) G12.player URL G13.E2E evidence G14.Human Review残(あれば確認ページURL)
共通: G15.Sheet行/記事一覧 G16.SSOT/Git SHA G17.cost G18.ユーザー判断 A/B(未解決がなければTiny Bags/Convenience AIとも「なし」、A2完成playerは最終確認用として提示) G19.無変更証跡/lock記録/事前指定外Read。
