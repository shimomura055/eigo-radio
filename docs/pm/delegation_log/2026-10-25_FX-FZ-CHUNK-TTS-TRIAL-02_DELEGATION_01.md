# 委任文(Fable→sonnet-worker)
管理ID: FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 委任_03(Family X: 段落Chunk 0.2秒版B0.2を既存chunk音源の再組立のみで作成→試聴ページ更新、TTS 0・API 0) + FZ-NARRATION-CHUNK-TTS-TRIAL-01 委任_01(Family Z: 長い地の文のChunk分割Trial Phase 0=既存分割構造の調査+設計+Opus条件Aレビュー依頼書、API 0。有料生成は次委任)
Status: 両FamilyともTrial継続(ユーザー承認2026-10-25)。APPROVED_FOR_PRODUCTIONではない。Production配線禁止。

## 0. 最初に
- ユーザー原文を `docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-TRIAL-02_USER.md` に以下を一字一句そのまま保存(両管理IDから参照)。

```
# Claude Code指示｜Family X／Z TTS Chunk分割 追加比較Trial

## 1. ユーザー決定・Status

ユーザーは以下を承認しました。

**Family X**
- 段落Chunk分割のTrialを継続する。
- 前回の追加ポーズ0.5秒を**0.2秒に変更**して再出力する。
- 0.2秒版の比較試聴を行う。
- Production正式採用・配線は現時点では行わない。

**Family Z**
- 地の文が長く続く箇所を適切に分割する方式をTrialする。
- 既存のセリフ・話者切替の分割は維持する。
- 追加Chunk間のポーズは0.2秒を使用する。
- Family Xとあわせて比較試聴し、正式採否を判断する。

**両FamilyともStatusはTrial継続。APPROVED_FOR_PRODUCTIONではありません。**

## 2. Family X｜0.2秒版の作成

対象：『英国の電車マナー』Advanced本文。

既存の段落Chunk Trial成果物・音声・組立処理を最大限再利用してください。

### 実施内容

1. 前回のB方式（段落分割＋0.5秒ポーズ）の追加ポーズを0.2秒へ変更する。
2. 既存Chunk音声を再利用できる場合、TTS再生成は行わず、接続部分のみ再組立する。
3. A（現行）、B0（追加ポーズなし）、新B0.2（0.2秒）を比較可能にする。
4. 旧B（0.5秒）も必要なら参考として残す。
5. 新B0.2の速度・ポーズ・接続品質を確認する。

### 受入条件

- 段落単位のChunk構造を維持。
- 追加ポーズが指定どおり0.2秒。
- 既存TTS音源を不要に再生成しない。
- 音声欠落・二重再生・不自然な接続がない。
- 声質・抑揚の差異を試聴で確認できる。
- 既存Productionには変更を加えない。

## 3. Family Z｜長い地の文のChunk分割Trial

### 目的

Family Zでは、セリフがなく地の文が長く続く場合、TTSの読み上げが速くなりやすい問題があります。

Family Xの段落Chunk方式を参考にしつつ、**文学作品の語り・テンポ・緊張感を維持したまま、長い地の文の発話速度を改善できるか**を検証してください。

### 基本方式

1. 既存のDialogue／話者切替処理を確認し、再利用する。
2. 既にセリフ境界で分割されている箇所は原則変更しない。
3. 地の文が長く続く区間のみ、追加のChunk分割対象とする。
4. 段落・文のまとまり・意味・場面の自然な切れ目を優先する。
5. 文や引用・セリフの途中で不自然に切らない。
6. 追加した地の文Chunk間には0.2秒のポーズを使用する。
7. 既存の音量正規化・無音trim・音声結合方式を再利用する。

### 分割粒度

単純に固定文字数や一律の秒数で切るのではなく、既存のDialogue分割構造と文章のまとまりを踏まえて判断してください。

細かく分割しすぎると、声質や抑揚が不自然になり、物語の連続性を損なう可能性があります。

一方、長すぎるChunkを残すと速度改善が得られません。

**品質と減速効果を両立する必要十分な分割方法**を検討してください。

## 4. Family ZのTrial対象

まず既存の完成作品から、長い地の文が存在する箇所を選定してください。

『告げ口心臓』を優先候補とします。理由は、一人称独白が長く続き、速さと語りの自然さを検証しやすいためです。

ただし、現在別案件として進行している**原作本質保持・案AのProduction Wiringと正式再生成を妨げない**こと。

- 進行中の正式Production経路へ未承認のChunk方式を混入させない。
- 正式再生成の成果物を再利用できる場合は再利用する。
- 並行作業によるファイル競合や音声Storeの衝突を防ぐ。
- 必要なら、地の文中心の別のFamily Z作品も比較対象とする。

新しい作品を作る必要はありません。

## 5. A/B比較・品質検証

Family Zでは、原則として同じ本文・Voice・TTS Style・モデル・生成条件で比較してください。

- A：現行Chunk構成
- B：長い地の文を追加分割＋0.2秒ポーズ

確認事項：

**① 発話速度**
- 全体WPM
- 無音を除いた実発話WPM
- 追加ポーズによる時間増と、発話そのものの減速を区別
- 生成take間のばらつきも考慮

**② 音声品質**
- 声質・抑揚の一貫性
- Chunk境界の音量差
- 不自然な無音・間延び
- 欠落・重複・接続異常
- ASR・既存音声Gate

**③ 物語品質**
- セリフや話者切替の自然さ
- 語りの流れ
- 心理描写の連続性
- 緊張感・没入感
- 一人称独白の自然さ

特に『告げ口心臓』では、語りの迫力や心理的緊張を損なわないことを重視してください。

機械指標だけで「音質改善」と断定せず、ユーザー試聴が必要な項目を明確にしてください。

## 6. 比較試聴ページ

X・Zとも、技術者でないユーザーが容易に比較できるページを用意してください。

**Family X**
- 現行A
- 段落Chunk・追加ポーズなし（B0）
- 段落Chunk・追加ポーズ0.2秒（新B0.2）

**Family Z**
- 現行A
- 地の文Chunk分割・追加ポーズ0.2秒（B）

各方式について、比較対象区間と可能な範囲で全体を試聴できるようにしてください。

比較条件・対象区間を明示し、開発者向けの詳細情報を過度に表示しないこと。

X・Zの試聴リンクをまとめて提出してください。

## 7. QCD・実行方針

品質 ＞ 速度 ＞ 量産単価 ≫ 開発費。

- 既存のFamily A／X／Z音声処理を再利用する。
- 新しい独自音声加工やValidatorを安易に追加しない。
- Xは既存音源の再組立を優先し、不要なTTS費用を発生させない。
- Zは品質検証に必要な最小限のTTS生成に絞る。
- 独立作業は並列化する。
- 既存の開発予算・STOP条件を遵守する。
- 追加費用と、Production採用した場合の量産単価増分を分けて報告する。
- 改善効果が十分に確認できたら追加の磨き込みをせずTrialを終了する。

## 8. PM Gate・STOP条件

今回承認されたのは**比較Trialと試聴用成果物の作成まで**です。

以下は禁止します。

- X／ZのChunk方式を正式Productionへ配線すること
- 未承認の速度・ポーズ仕様を正式採用すること
- 別案件のFamily Z原作本質保持Production作業へTrial方式を混入させること
- 追加の音声品質基準を独断で正式仕様化すること

承認Scope内の技術的不具合は自律的に解決してください。

Trial終了時は、VALIDATED／REJECTED／USER_DECISION_REQUIREDのいずれかに分類してください。

## 9. 最終報告

以下を簡潔に報告してください。

1. Family Xの0.2秒版作成結果
2. Family Zで選定した作品・区間と分割方法
3. X／Zそれぞれの速度比較（全体WPM・実発話WPM）
4. ポーズ・音量・声質・接続品質
5. セリフ／地の文／原作の語りへの影響
6. X／Zの比較試聴URL
7. Trial実費・量産単価・処理時間への影響
8. Fable独立評価
9. Trial Closeout Statusと残存課題
10. SSOT／Git反映状況

**最終判断は、ユーザーがX・Zの比較音声を試聴した後に行います。**

Production採用判断を先取りしないでください。
```

- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 518 --out docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-TRIAL-02_DELEGATION_01.md`。冒頭が「管理ID: FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 委任_03」と一致するか確認、不一致なら index 516〜521 を順に試す(`--index -1`不可)。

## Part A. Family X 0.2秒版(API 0・TTS 0)
- 資産: `er113_fx_paragraph_chunk_trial_01.py`(B_r1の10 chunk wav、RMS正規化・固定無音concat・ヘッドルーム弁の組立関数)、`er113_output/fx_paragraph_chunk_trial_01/`、`user_test/fx_paragraph_chunk_trial_01/`、`DESIGN_01.md`、`TRIAL_RESULT_01.md`、`measure_01.json`。
- 作業: B_r1の既存chunk wavから、段落間追加無音0.2秒でpart1/2/3・本文全体・Advanced通しを再組立(B0.2_r1)。TTS/ASRは呼ばない。同一計測法(M4分解、total/articulation WPM、境界音量差、欠落・二重の整列検知[ローカルfaster-whisperのみ])で計測し `measure_02.json`・`TRIAL_RESULT_02.md`(0.2秒版の速度・ポーズ・接続)。
- ページ更新: 主表示をA(現行)/B0(追加なし)/B0.2(新)に変更し、旧B(0.5秒)とA_r2/B_r2は折りたたみ参考。比較条件・対象区間を明示、開発者向け詳細は折りたたみ。mp3を追加(`user_test/fx_paragraph_chunk_trial_01/audio/B02_*.mp3`)。公開後HTTP 200確認。
- 保護store・承認済み音声・公開版 `uk_train_speaker_playback_e2e_02` 不変(sha比較)。

## Part B. Family Z 長い地の文Chunk分割 Phase 0(API 0)
- 調査 `docs/research/FZ-NARRATION-CHUNK-TTS-TRIAL-01/EXISTING_SPEC_CHECK_01.md`: Family Z正式経路のsegment分割構造(`er026_family_z_fiction_production_runner_01.py`のplan/support/tts_b1b/tts_a2段、`er062_family_z_structure_01.py`の話者割当・Dialogue分割、clip単位、clip間gap[C/Z先例0.5秒等]、決定的Voice割当、速度仕様v2[Std 6%後処理等]、音量正規化・trim・結合関数)。『告げ口心臓』現行run(`run_sf_prod_01`)のclip一覧(clip長・語数・話者・地の文/セリフ)から「長い地の文clip」を定量把握(例: 語数・秒数の分布、最長clip)。他候補作品(猿の手・二十年後)の地の文clip分布も比較。21節A/B/C分類(過去の分割Trial、P6B不採用との関係)。
- 設計 `DESIGN_01.md`:
  - 分割規則: 既存Dialogue/話者切替境界は不変。地の文clipのうち閾値(語数または秒数、既存分布から根拠づけ)を超えるものだけを、段落境界>文のまとまり(場面の切れ目)>文境界の優先で分割。文・引用の途中では切らない。固定文字数の一律分割はしない。分割後chunk間の追加無音=0.2秒(ユーザー指定)。既存のRMS正規化・trim・結合・ヘッドルーム弁を再利用。
  - A/B条件: 同一本文・Voice・Style・モデル・速度仕様。A=現行clip構成、B=長い地の文のみ追加分割+0.2秒。
  - **対象本文の選択と並行案件との競合回避(重要)**: 『告げ口心臓』は別案件(FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_03/04)で案A配線後に正式再生成(新run)が予定されている。本Trialは(i)正式再生成完了後にその新Adv本文・音声を**読み取り専用で再利用**してA/Bを行う(推奨、同一本文・一人称)、(ii)待てない場合はTrial 1b_s1のAdv(`er026_output/family_z_dev_trials/fz_essence_01/the_tell_tale_heart/1b_s1`、音声1cあり)をAとして使う、の2案を比較し推奨を記す。いずれもProduction run dir・Production store・公開ページには書き込まず、出力は `er026_output/family_z_dev_trials/fz_narration_chunk_01/` に限定。TTS直列化flagを尊重し、別案件のTTSと並走しない運用を設計に明記。
  - 計測・評価: ユーザー原文§5の①②③(③は人手試聴項目として明示)、X Trialと同じM4分解・境界音量差・整列検知。
  - 費用: B側の分割対象clipのみTTS再生成(地の文の長いclip数×…、出典=run_sf_prod_01 cost/tts実績)。Fable上限=30円。
  - 試聴ページ設計 `user_test/fz_narration_chunk_trial_01/index.html`(現行A/B、比較区間+全体)。
- `OPUS_REVIEW_REQUEST_01.md`(条件A): 論点=(a)分割閾値・優先順の根拠と文学的連続性への影響、(b)既存Dialogue分割・Voice割当・速度仕様v2との整合、(c)A/B同一性、(d)Production非汚染と並行案件との競合回避、(e)P6B不採用方式との関係、(f)費用対効果。
- SSOT: `OPEN_ITEMS.md` に新規OPEN(FZ-NARRATION-CHUNK、種別Trial、分類必須、Status=TRIAL_DESIGN_PENDING_OPUS_A)、OPEN-506に委任_03(0.2秒版)を追記、`docs/pm/USER_DECISION_REGISTER_01.md` #191を「判断済み(2026-10-25、0.2秒版再出力+Z地の文Trial継続、採用判断はX/Z比較試聴後)」に更新、`DECISION_LOG.md` 1件、`docs/pm/ACTIVE_TASK.md` 自行2行(並行agent: FX-CORE-NUMERIC 委任_04、FZ-SOURCE-ESSENCE 委任_03、FAMILY-Z-STUDY-TEXT 委任_10。編集直前に再Read・最小Edit・衝突時再試行)。SSOT編集前にscratchpadへバックアップ、編集後 `git diff --stat -- <file>` 確認。`py`使用。
- Git: `git status` → 対象pathのみ `git add`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status`(意図外D/Aなし・secret 0件・Production file差分0、公開mp3は`user_test/`配下のみ) → `git commit --only -- <path…>` → `git push origin HEAD:main`。
- 報告 `docs/pm/RESULT_PACKET_FXPC3.md`: ①X 0.2秒版の計測(A/B0/B0.2/旧B表)、接続品質、ページURL、②Z調査結果(長い地の文clipの分布、候補作品)、③Z設計要点・対象本文の推奨・費用見積、④OPUS_REVIEW_REQUEST_01.mdの所在、⑤変更ファイル・commit、⑥`check_delegation_prompt.py`結果、⑦問題点。**Z有料生成は開始しない。**

## 禁止
Production code/Prompt/flag変更、承認済み音声・公開版の変更、Production run dir/store/telemetryへの書込み、X/Z Chunk方式の正式配線、独自音声加工・Validator追加、X側TTS再生成、Z側有料呼出(Phase 0)、別案件(FZ-SOURCE-ESSENCE)のファイル・runへの干渉、自PID以外のprocess終了。