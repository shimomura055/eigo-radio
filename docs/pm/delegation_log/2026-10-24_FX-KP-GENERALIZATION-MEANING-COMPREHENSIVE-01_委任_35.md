管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_35 — Key Phrase日本語意味 X2p'(本文での語義を確定してから訳す方式)の XYZ共通 Production Wiring + 記事B『英国の電車マナー』(uk_train_speaker_playback)最終版再提出。

## 0. ユーザー正式決定(2026-10-24、本委任の根拠。逐語は手順1で保存)
- **X2p' を Family X/Y/Z 共通仕様として正式採用。Status=APPROVED_FOR_PRODUCTION**(UDR #179 の回答。選択肢A-1/A-2ではなく「XYZ共通」)。目的=`draw a line`→「線を引く」型の字義訳防止。
- 改良Promptの追加Trial・再採否判断は不要。Trial_06の軽微なTHINはユーザーが実例確認のうえ許容済み。ただし意味の誤り・不自然な訳を新たに許容するものではない。
- 既存のKP選定・一般化(A-1)・所有格一般化(②)・gloss再整合(UDR #60)は維持(別仕様。壊さない・重複させない)。
- Family共通処理は共有化、Family別重複実装禁止。Trial専用Prompt/DEV経路(er112)への暗黙参照禁止。
- Family Yは正式Production入口が未完成なら共通実装しても `PRODUCTION_WIRED` と判定しない。理由と必要対応をOPEN_ITEMSへ明記。Y全体の新規Production構築を今回開始しない。
- 承認済み品質を満たした時点で検証終了。追加Trial・磨き込み禁止。新品質基準・追加仕様の独断導入禁止。
- 費用: Trial_06実測+0.44円/記事セットの水準から不必要に増えないことを確認。
- 記事B: X2p' Wiring完了後、承認済み仕様でKP修正+必要部分のみ音声・表示更新→Std/Adv最終版再提出。修正対象外の完成済み音声・本文は再生成しない。ユーザー最終試聴PASSは別判断(自動承認しない)。

## 1. まず行うこと(API 0)
1. ユーザー原文を逐語保存: `docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_10.md`。抽出は `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role user ...`(indexは末尾付近。本文は「# Claude Codeへの指示\n## Key Phrase日本語意味 X2p' — XYZ共通Production Wiring」で始まる。toolが対応しない場合はjsonlをgrepして該当userメッセージ本文を一字も変えずに保存)。本委任文も `..._委任_35.md` に保存(`--role assistant --tool-use-name Agent --tool-input-field prompt --index <最新>`、保存後に先頭行が本委任文と一致することを確認)。
2. 設計正本 `docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/WIRING_DESIGN_07.md` を全文読み、これに従って実装する(G-1〜G-9、§3混在batch 2 call分割、§4方式P' NewGenMessage、§5 prior/rules_fulltext、§6 flag新設なし・撤退=単一commitのrevert、§7 Z repair非適用+監視1項目、§8 監視指標、§9 WC-01〜12、§10 runtime evidence、§11 CURRENT_SPEC更新)。Prompt文面の正=`er112_kp_gm_trial_06.build_x_message06`(X2p'、Trial_06で実測した文面を**無変更**で移植。改良しない)。参照: `TRIAL_06/TRIAL_RESULT_06.md`、`ADOPTION_PROPOSAL_02.md`、`OPUS_REVIEW_08.md`(OF-KP2-04〜07)。
3. 整合確認(ユーザー§2): CURRENT_SPEC(KP gloss再整合節 1970-1979・2785-2793付近、A-1/②の節)、DECISION_LOG(UDR #169/#173/#179関連)、OPEN-467/474/484、Productionコード(`er003_key_words_gloss_alignment.py`、`er003_v1_n3_01_scaffold_generate.py:525付近`、`er026_family_z_fiction_production_runner_01.py:1447/1552付近`)。A-1(見出し語一般化)/②(所有格一般化、canonicalization段)/gloss再整合(欠落・人称)/X2p'(新規生成glossの意味確定)が別責務であり、X2p'が前3者の経路・出力を変えないことを明記(短い整合表 `CP_CHECK_35.md`)。**Family Y**: 正式Production入口(量産runner)の有無を確認(OPEN-484の記載を再確認)。
4. 作業ツリー確認: `git status`で `CURRENT_SPEC.md` が未commit修正(M)になっている。`git diff CURRENT_SPEC.md`で内容を確認し、他案件の差分なら触らず報告(自分の変更と混ぜない)。Production runの前に、本件import graph(er003_key_words_gloss_alignment.py・scaffold・er026・er019 runner群)に未commit変更がないことを確認して記録。

## 2. Production実装(WIRING_DESIGN_07に従う)
- 変更は `er003_key_words_gloss_alignment.py`(共通module、X/Z/Y共有)に閉じる。既存builder/schema/developer/定数は一字も変えない(byte-identical)。Productionは`er112`をimportしない(golden fixtureはDEV出力をtest側にcommit)。
- 新規test `er003_test_kp_gloss_meaning_stage_01.py` にWC-01〜WC-12。既存gloss alignment test群4本は無変更で全PASS。全回帰(`.venv\Scripts\python.exe -m pytest -q`等、既定の方法)で failed/errors の自分起因0を記録(他agent起因は列挙のみ)。
- retry/fallback/regeneration/resume整合(ユーザー§3-2): attempt上限2・prior再掲・unresolved→HR・暗黙フォールバックなし・混在batch(resume時のgloss有item)を2 callで処理、を実装とtestで確認。
- 後続工程整合(§3-3): 新3欄(`meaning_in_text_en`/`naive_ja`/`naive_ja_conveys`)はTTS・表示・validatorへ出さず記録のみ。Validator(括弧・算用数字・人称・qa・mapping)は新経路でも同一に働くこと。
- **Production挙動変更は単一commit**(コード+test+golden fixture)。commit messageに「Production挙動変更を含む単一commit、撤退=git revert」を明記。revert予行(§6: `git revert --no-commit`→WC-01+関連test PASS→`git revert --abort`)を実施して記録。他の変更(SSOT・記事B成果物・docs)は別commit。
- Git禁止: `git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f。commitは `git status`→対象pathのみ `git add`→`git diff --cached --name-status`で意図しないD/Aなし確認→`git commit --only -- <path…>`。push=`git push origin HEAD:main`。secret grep 0件。

## 3. Runtime evidence(正式経路、X/Z。新規本文生成・本文TTS 0)
- **X**: 記事B `uk_train_speaker_playback`(er019 Production run、場所はOPEN-467/ACTIVE_TASK参照)の正式KP段(`scaffold.run_key_phrase_canonicalization`経由の正式re-run/resume経路)でStd/Adv双方のglossを新経路で再生成する。これがX runtime evidence兼記事B修正。actual model_id、Prompt sha/Version、`meaning_stage`、入力本文と出力の対応、所要時間、費用を記録。
- **Z**: 過去Z Production記事(例: `er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01` または『賢者の贈り物』)の本文+`original_items`を**公開物に触れないコピーrun dir**へ注入し、`er026` stage_kp の正式KP段でgloss=nullから新経路で生成。Z repairが現行builderのまま(新経路0回)であることも確認。
- 共通: 混在batchの2 call(合成入力)、型喪失→INVALID→HR安全停止、A/B/C形入力で新経路0、を正式module経由で確認(API 0で可能なものはfake clientで)。
- **Y**: 共通module経由の到達性(DEV/Trial経路 `er110_*`がer003 gloss alignmentを通るか)を確認し記録。正式入口が未存在なら `Y=COMMON_IMPLEMENTED_NOT_PRODUCTION_WIRED` と表記。
- `docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/PROD_WIRING_EVIDENCE_09.md` に: 正式入口・実行経路/actual model_id/Prompt version・sha/入出力対応/発火evidence/test・全回帰結果/retry・fallback・resume整合/Family別Status(X/Z/Y)/実測単価(KP単位・記事セット換算、Trial_06の0.0704円/KPと比較)/所要時間/監視指標の新基準案(§8: 費用=実測p95×1.3、所要=実測p95×1.5。**提案として記録、CURRENT_SPECの基準変更はFable/ユーザー確認後**)。

## 4. 品質検証(ユーザー§4。過去成果物を最大限再利用、追加Trial禁止)
- 記事BのStd/Adv新glossを全KP列挙(旧→新)。`draw a line`が本文の意味に沿う訳になっていること。字義が正解のKPを比喩化していないこと。意味の誤り・不自然な訳が無いこと(あれば**そのKPのみ**既存retry上限内で再試行し、それでも残ればHR扱いで報告。Prompt改変禁止)。
- Z evidence runの新glossも同様に列挙し、既存Production gloss(公開中)との差を示す(Regression観点。公開物は差し替えない)。
- Trial_06既存成果(TRIAL_RESULT_06/AGREE_06_FINAL)を再利用し、新規LLM評価callは行わない。
- `QUALITY_CHECK_35.md`に表で記録(Fableが独立受入で読む)。

## 5. 記事B最終版再提出
- 新glossのうち**テキストが変わったKPの日本語glossクリップだけ**TTS再生成(英語KPクリップ・本文音声・既存承認済みsegmentは再生成しない。`human_approved_segments`・Style Gate記録を壊さない)。既存の正式TTS段・Gate(ASR/速度/HR Lock)・assemble・pages・page_verifyを正式経路で1起動ずつ(同一run起動間隔150秒以上、RESTART_STORM回避、TTS直列化flag尊重、STOP/HR Lock迂回禁止。HR Lockが出たら停止して報告=approve_regenerateはFable権限)。
- 切替ページ(`user_test/family_x_uk_train_speaker_playback_*/`既存)を更新、公開URL(Std/Adv)でpage_verify PASSを記録。Status=`USER_LISTENING_PENDING`(自動承認しない)。

## 6. SSOT・記録
- `CURRENT_SPEC.md`: WIRING_DESIGN_07 §11の文言を**適用範囲つき**で追記(XYZ共通の新規生成gloss/Z repair・混在legacy側・A/B/Cは従来原則併存)。Y=共通実装済み・正式入口未存在の注記。
- `DECISION_LOG.md`: UDR #179回答(X2p' XYZ共通採用=APPROVED_FOR_PRODUCTION、2026-10-24)、Production Wiring実施、X/Z=`WIRED_PENDING_FABLE`(PRODUCTION_WIREDの表記はFable受入後)、Y=未配線理由。Fable判断の記録: 「WIRING_DESIGN_07はOPUS_REVIEW_08(条件C)の必須修正OF-KP2-04〜07を反映した改訂であり、Opus自身の指示に沿う変更のため追加の実装前Opusレビューは不要と判断(11-3 重複レビュー回避)」。
- `OPEN_ITEMS.md`: OPEN-474(①字義訳)=採用済み・配線状況、OPEN-467(記事B)=最終版再提出済み・USER_LISTENING_PENDING、OPEN-484(Y)=X2p'も同じ未配線事由で追記(新規OPENが必要なら分類必須)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: #179を判断済みへ。
- 費用台帳 `TRIAL_06/BUDGET_LOG_T6_01.md` に続けて本委任分(cost logger `install`を忘れない)。
- `docs/pm/ACTIVE_TASK.md`: 委任_35行を追加(Status/有料run/原文/委任文/報告)。
- `docs/pm/RESULT_PACKET_KPGM35.md` に報告(ユーザー§9の順序で下書き: 1.X/Y/Z最終Status 2.実装内容 3.runtime evidence・test 4.字義訳改善と既存品質影響 5.実測費用・量産単価影響 6.記事B試聴URL 7.(Fable記入欄) 8.SSOT/Git・残Open Item。加えて: 逸脱・事故・HR Lock・他agent起因の失敗・未解決事項)。

## 7. 制約
- 予算上限: 本委任 **25円**(gloss call X 2 level+Z 2 level+記事B JA clip TTS数クリップ想定)。KP案件累計上限500円(現在約316円)。日次1,000円(10-24把握分約642円)。超過見込みなら起動前に停止して報告。
- `.venv\Scripts\python.exe`を使う。他プロセス終了禁止。並行でOpus(read-only)が`docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/`を読んでいる(競合なし)。
- 既存Gate・HR Lock・STOP・approve_regenerateの迂回禁止。Trial専用Prompt(er112)の改良禁止。本作固有Prompt新設禁止。
- 解決できない技術問題は原因・試行・代替案を付けて報告(STOP条件: HR Lock、予算超過見込み、`draw a line`が新経路でも字義訳のまま、既存test破壊で自分起因が解消できない、Production import graphに他agentの未commit差分がある)。