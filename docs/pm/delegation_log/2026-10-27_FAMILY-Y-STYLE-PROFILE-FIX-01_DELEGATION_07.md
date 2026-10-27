## 管理ID

FAMILY-Y-STYLE-PROFILE-FIX-01 委任_07(ユーザー正式決定2026-10-27「Family Y再配達記事Closeout+Style継承Production Wiring完了確認」の第1段: (1)OPEN-537 Style継承のPRODUCTION_WIRED到達状況の照合(read-only、既存evidence再利用、有料検証なし)、(2)`_03` Std/Advユーザー最終試聴PASSの正式記録、(3)Voice説明文の承認文言への差替えと、開発用Chunk境界マーカー`⏸`表示仕様(X/Y/Z共通・開発用限定)の**現状棚卸し+設計**、(4)`_03`公開ページの表示修正(**生成元がresearch tool(`tools/build_page_0N.py`等)の場合のみ本委任で実施**。Production builder(`er121_family_y_audio_01.py`/`er063`/`er019_*page*`/`er_user_listening_page_common_01.py`)は並行Agentが編集中のため本委任では編集せず委任_08へ)。API 0・JPY0)。並行Agent: GRAMMAR-PREGEN-ALL-LEVELS-01 委任_03(X/Y/Z runner・ページbuilder・common builderを編集中)、委任_04(er128/CLI/exporter)。これらのファイルは編集しない(読むのは`git show origin/main:<path>`)。あなたの所有=`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{WIRED_CHECK_01,USER_APPROVAL_03,CLOSEOUT_PLAN_01,CHUNK_MARKER_INVENTORY_01,CHUNK_MARKER_DESIGN_01,VERIFY_05}.md`、`tools/build_page_0N.py`(research tool、該当する場合)、`user_test/family_y_production_redelivery_fee_03/index.html`(表示修正のみ、音声・本文・KP不変)、`docs/pm/delegation_log/2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_{USER_04,DELEGATION_07}.md`(+check.json)、`docs/pm/RESULT_PACKET_YSP7.md`(gitignore、`-f`禁止)。SSOT編集権なし。pathspec付きcommit(他Agentのstage分を巻き込まない)。

## 性質/禁止

- 性質: 受入照合+Closeout記録+表示修正(表示修正は承認済み文言・表示仕様への追従、品質基準変更なし)。到達上限=照合完了+`_03`表示修正(tool経由の場合)+設計。
- 禁止: 音声再生成・再試聴要求、Style/Voice/Fallback仕様の変更、Chunk分割・ポーズ長・音声生成仕様の変更、表示修正と無関係な記事改変、Production builder編集(委任_08)、有料実行、禁止Git操作(`add -f`/`pull --rebase`/pathspecなしcommit)。
- 時間見込み: 約2h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。ユーザー原文(下記)を`..._USER_04.md`へ逐語保存。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_07.md` をN=723から順に試し、先頭「## 管理ID」+「FAMILY-Y-STYLE-PROFILE-FIX-01 委任_07」のものを採用。

## ユーザー指示(原文・逐語)

# Claude Code指示｜Family Y再配達記事Closeout＋Style継承Production Wiring完了確認

## 1. ユーザー正式決定

対象：Family Y「宅配の再配達は有料にすべきか？」Standard／Advanced、およびFamily Yの正式Production音声経路。

以下を正式決定として受領してください。

**A. 再配達記事**

- Standard／Advancedともにユーザー最終試聴PASS・正式承認。
- 現行完成版 `_03` の音声・本文・Key Phrase・学習内容を承認。
- 表示修正に伴う音声再生成・再試聴は不要。

完成版：
https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_03/index.html

**B. Voice説明文**

以下の文言を正式採用する。

「Voice 1〜3は実在人物の発言をそのまま再現したものではなく、実際に投稿された意見をもとに、AIが編集・再構成したものです。」

- 今回の再配達記事に反映。
- Family Y共通の説明文として使用。
- 将来のアプリ表示でも同じ文言を使用する。
- 旧文言が正式Productionのテンプレート・公開ページ生成処理に残らないよう整合を確認。
- 実際の投稿意見に基づいて制作した記事に適用し、根拠のない出典主張を生成しない。

**C. 開発用Chunk境界マーカー**

- 実際のTTS Chunk分割境界だけを `⏸` で表示する。
- 秒数・タイムスタンプ・説明文は不要。
- ASRなどで検出した通常の音声ポーズは表示しない。
- **開発段階のユーザー確認用表示に限定する。**
- 量産時のエンドユーザー向けスクリプト・公開コンテンツ・将来のアプリには表示しない。
- X/Y/Z共通の表示仕様とする。
- 実際のChunk分割・追加ポーズ長・音声生成仕様は変更しない。

今回の再配達記事について、技術的なポーズ表示 `⏸0.70s@0:39.0` 等を撤去し、実際のChunk境界がある箇所だけ簡単な目印に置き換える。

表示修正のみのため、承認済み音声の再生成・再試聴は行わない。

## 2. OPEN-537｜Style継承のProduction Wiring確認【重要】

Family Yの音声StyleがFamily Xの承認済みStyleを継承していなかった不具合について、**PRODUCTION_WIREDの到達状況を改めて確認してください。**

既知の事実：

- 修正実装：commit `3af84a499`
- Y runnerが承認済みStyle profile `fx_20261017` を継承
- 課金前のStyle固定記録
- Style不一致を停止させるfail-closed Gate
- Style関連テスト37件PASS
- 再配達 `_03` の正式音声でStandard 18/18、Advanced 15/15のStyle一致
- `_03` はユーザー最終試聴PASS

ただし、直近のCURRENT_SPECでは、Y経路のPRODUCTION_WIRED判定は別途Fableが実施する旨の記述が残っており、最終受入・Closeoutは未確認です。

### 実施内容

まず、CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／PM_GOVERNANCE／関連Git commit／runtime evidence／Fable受入記録を照合する。

**すでにPRODUCTION_WIREDなら：**

- Fable正式判定の証拠と日付を提示。
- OPEN-537のStatus、CURRENT_SPEC、DECISION_LOG、Git反映を確認。
- 記録漏れや古い「未完了」記述があれば是正。
- 重複した再実装・有料検証は行わない。

**まだPRODUCTION_WIREDでなければ：**

既存の承認済み作業範囲内で不足項目を解消し、PRODUCTION_WIREDまで進める。

確認条件：

1. Family Yの正式初回Production音声経路で `fx_20261017` が既定適用される。
2. Standard／Advancedの全対象部位で承認済みStyleと実際のStyleが一致する。
3. Style不一致時にfail-closed Gateが機能する。
4. retry／fallback／regeneration／resumeで承認済みStyle仕様が維持される。
5. DEV／Trial専用経路ではなく、正式runnerでのruntime evidenceがある。
6. actual model_id、routing、Style profile、Style実測記録を確認。
7. 必須Regression／Validator／Integration TestがPASSする。
8. SSOT／Git反映とFable独立受入を完了する。

今回の再配達 `_03` の実測証拠を優先して再利用し、既に満たした項目のために音声を再生成しないこと。

未確認項目があれば、その項目だけ必要十分な検証を行う。

**完成記事のユーザー試聴PASSをもって、Style継承機能のPRODUCTION_WIREDを自動認定しないこと。**

また、音声Styleの新たな変更・Voice変更・未承認のFallback仕様変更は行わない。

## 3. Family Y再配達記事のCloseout

以下を実施する。

1. `_03` のStandard／Advancedユーザー最終試聴PASSを正式記録。
2. 承認済みVoice説明文へ修正。
3. 開発用スクリプトのChunk境界表示を是正。
4. 正式公開ページ・今後のページ生成テンプレートとの整合を確認。
5. 音声ファイル・本文・KP・文法解説などの承認済み内容が不変であることを検証。
6. 必要な公開検査・Git反映・SSOT更新を完了。
7. Fableが表示修正・Closeoutを受入評価。

表示修正と無関係な記事改変は禁止する。

将来アプリ向けの文言は仕様として記録するが、今回のScopeにアプリ開発そのものは含めない。

## 4. X/Y/Z共通のChunk境界表示

開発用スクリプト表示について、Family X/Y/Zの既存生成経路を確認し、今回の承認済み表示仕様に統一する。

- 実際のChunk分割境界にのみ `⏸` を表示。
- 音声解析上のポーズとは区別。
- 開発／ユーザー確認用の表示と、エンドユーザー向け量産表示を分離。
- エンドユーザー公開物へのマーカー混入を防止。
- 不要になった旧表示処理・旧テストを整理。

全Familyで検証するが、既存の音声生成・Chunk分割方式そのものは変更しない。

## 5. QCD・実行方針

優先順位：**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- 独立したStyle受入確認、表示修正、SSOT確認は原則並列化。
- 既存evidence・テストを最大限再利用。
- 不要なAPI実行・TTS再生成・再試聴を禁止。
- 承認済み範囲内の不具合は原因究明から修正・検証まで自律実施。
- 日次開発費1,000円（JST）と個別承認枠を遵守。
- ユーザー未承認の新仕様・品質基準変更、重大なblocker、予算超過はSTOPして報告。
- 必要十分な品質に到達した時点で完了する。

## 6. 最終報告

以下の順に簡潔に報告してください。

1. **OPEN-537の最終Status：PRODUCTION_WIRED到達有無**
2. Style継承の正式runtime evidence・Fable受入結果
3. 再配達 `_03` のユーザー承認記録・Closeout結果
4. Voice説明文の正式反映結果
5. X/Y/Z共通Chunk境界表示の修正・公開検証結果
6. QCD実績
7. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Git更新結果
8. 残る未解決事項（ある場合のみ）

**完了条件：OPEN-537の正式Production Wiringを証拠付きでCloseoutし、再配達記事の承認・表示修正・公開反映を完了すること。**

既に完了済みの作業は重複実行せず、未完了部分だけを補完してください。

(原文ここまで)

## 実施事項

1. **WIRED照合(`WIRED_CHECK_01.md`)**: 確認条件1〜8を、既存証拠(commit 3af84a499/d2d68194d/b9be75ef4/01e7d02ec、`er121_family_y_style_profile_test_01.py` 37件、`run_style_fix_01/audit/{style_profile.json,style_actual_vs_approved.json}`(Std 18/18・Adv 15/15)、`REGEN_RESULT_02`/`VERIFY_04`、OPEN-535 guard、TTS統一(OPEN-540)のY evidence(retry/fallback/resumeでStyle維持)、KCP3 Y evidence(現行runnerコピーでgate通過))で項目別に「充足/不足(根拠ファイル:行)」。不足項目があれば**API 0で可能な検証(test/既存記録)**で補い、有料が必要なら実行せず見積のみ報告。Fableが判定するための材料として、各項目の証拠日付・commit・pathを表に。SSOTの古い「未判定/判断待ち」記述(CURRENT_SPEC Y Style節、OPEN-537/539、USER_DECISION_REGISTER)を列挙し是正文案を用意。
2. **ユーザー承認記録(`USER_APPROVAL_03.md`)**: `_03` Std/Adv最終試聴PASS(USER_04 §1-A)、承認対象sha(std_full.mp3/adv_full.mp3/本文/KP/学習内容)、承認日時、原文path。記事Closeout=「承認済み・表示修正のみ残」。
3. **Voice説明文**: 旧文言の所在をGrep(`er121_family_y_audio_01.py`/`er121_family_y_runner_01.py`/テンプレート/`user_test/family_y_*`/CURRENT_SPEC/Y設計doc、Grep `Voice 1〜3|実在|投稿|再構成|編集`)で棚卸し(`CLOSEOUT_PLAN_01.md`)。`_03/index.html`の文言を承認文言へ差替え(本委任、静的ページ)。Production template側は委任_08(ファイル:行を明記)。「根拠のない出典主張を生成しない」条件=実投稿に基づく記事にのみ適用する判定条件(既存のY記事メタ(`opinion_based`/THEME_DATA)で判別可能かを確認)。
4. **Chunk境界マーカー(`CHUNK_MARKER_INVENTORY_01.md`/`CHUNK_MARKER_DESIGN_01.md`)**: X/Y/Zで開発用スクリプト表示に出るポーズ/chunk表示(`⏸0.70s@0:39.0`等)の生成元(ファイル:行)、その情報源(実Chunk分割境界=`er122`/chunk policyの境界記録 vs ASR/音声解析の長停止検出)を区別して棚卸し。設計: 実Chunk境界のみ`⏸`(秒数・説明なし)、ASRポーズ非表示、**開発/確認用ページ(`user_test/`配下の試聴ページ)に限定**しエンドユーザー公開物(量産スクリプト・将来アプリ用出力)には出さない分離方法(builderの`audience=dev|public`相当の既存機構があればそれを使う)、X/Y/Z共通化の配線点、旧表示処理・旧testの撤去一覧、検証方法(公開物にマーカー0件のtest)。実装は委任_08。`_03/index.html`については、生成元がresearch tool(`tools/build_page_04.py`等)なら本委任でtoolを修正して再生成(音声・本文・KP不変をsha比較で証明=`VERIFY_05.md`)、Production builder由来なら委任_08。
5. 公開検証(`_03`修正時): HTTP 200、音声sha不変、本文/KP/学習内容のテキスト不変(マーカーと説明文以外のdiff 0)。

## 事前指定Read一覧

- `docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{DESIGN_02,IMPLEMENTATION_01,REGEN_RESULT_02,VERIFY_03,VERIFY_04,BUILD_04,HR_APPROVAL_STD_PREVIEW_01}.md`、`tools/build_page_03.py`/`build_page_04.py`(あれば)、`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/EVIDENCE_Y_01.md`(Style維持の記録 Grep `style|fx_20261017`)、`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/EVIDENCE_Y_02.md`
- `er121_family_y_runner_01.py`(origin/main: Grep `Y_APPROVED_STYLE_PROFILE|resolve_run_profile|style_profile|fx_20261017` ±5)、`er121_family_y_audio_01.py`(origin/main: Grep `Y_ROLE_COVERAGE|style_actual|Voice 1|実在|⏸|pause|chunk` ±5)、`er063_family_z_audio_01.py`/`er019_*page*`/`er_user_listening_page_common_01.py`(origin/main: Grep `⏸|pause_marker|long_pause|chunk_boundary` ±5)、`er122_*`(chunk境界記録: Grep `boundary|chunk_index` ±5)
- SSOT Grep: `CURRENT_SPEC.md` `fx_20261017|Y Style|Style profile|Family Y.*Style` ±5、`OPEN_ITEMS.md` `OPEN-537|OPEN-539|OPEN-415` ±2、`DECISION_LOG.md` `Style profile|OPEN-537` ±2、`docs/pm/USER_DECISION_REGISTER_01.md` `YRF|537` ±2
- `user_test/family_y_production_redelivery_fee_03/index.html`(Grep `⏸|Voice 1|実在` ±2)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_07.md --json-out ...\_check.json`
- test(API 0): `.venv\Scripts\python.exe run_project_regression.py --pattern "er121_family_y_style_profile_test_01.py"`、`--pattern "er121_family_y_hr_approval_guard_test_01.py"`
- 公開確認(修正時): `Invoke-WebRequest <URL>` → 200、`Get-FileHash`で音声sha不変
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_YSP7.md`にOPEN-537(Fable判定用の充足表+WIRED/未達の文案両方)、OPEN-539(ユーザー承認・Closeout)、CURRENT_SPEC(Y Style節の是正文案、Voice説明文の正式文言、Chunk境界マーカー表示仕様(開発用限定・X/Y/Z共通))、DECISION_LOG(ユーザー決定A/B/C)、USER_DECISION_REGISTER文案。

## Git

- commit message: `FAMILY-Y-STYLE-PROFILE-FIX-01 委任_07: Style継承WIRED照合(既存evidence再利用、API 0)+_03ユーザー承認記録+Voice説明文/Chunk境界マーカーの棚卸し・設計(+_03表示修正[tool経由の場合])`。trailer: `Delegation: FAMILY-Y-STYLE-PROFILE-FIX-01/07`。push。

## 報告

`docs/pm/RESULT_PACKET_YSP7.md`: (0)T-0、(1)確認条件1〜8の充足表(証拠・日付・commit)、(2)SSOTの古い記述一覧と是正文案、(3)承認記録、(4)Voice説明文の所在・`_03`反映結果、(5)Chunk境界マーカーの棚卸し・設計・`_03`反映結果(または委任_08引継ぎ)、(6)判断候補、(7)必須4行+「判定整合: 重大NG=<なし|あり>」、(8)SSOT文案、commit hash・raw URL。末尾10行要約。