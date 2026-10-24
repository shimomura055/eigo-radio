# 委任文(Fable→sonnet-worker)
管理ID: FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 委任_01(Phase 1: 既存仕様調査+Trial設計+無料で先行できる準備。**API 0円**。有料TTS/ASRはPhase 2=Opus条件Aレビュー後のFable Goまで開始禁止)
Family: Xのみ / 記事: 『英国の電車マナー』uk_train_speaker_playback / レベル: Advanced(A2)のみ / Production変更: 禁止

## 0. ユーザー原文(2026-10-25、逐語。まず `docs/pm/delegation_log/2026-10-25_FX-PARAGRAPH-CHUNK-TTS-TRIAL-01_USER.md` に以下を一字一句そのまま保存すること)

```
# Claude Code指示｜Family X 段落単位TTS Chunk分割Trial

## 1. 最初に伝える承認事項

**Family X『英国の電車マナー』Standard／Advancedの最終版は、ユーザー試聴PASS・正式承認済みです。**

対象：
https://shimomura055.github.io/eigo-radio/user_test/uk_train_speaker_playback_e2e_02/index.html

記事の完成承認として、必要なSSOT・DECISION_LOG・OPEN_ITEMSのCloseoutを行ってください。

今回の新Trialとは独立した判断です。完成版を変更・再生成しないでください。

## 2. 新Trialの目的

Family Xの本文音声について、現行の「本文1・2・3それぞれを1つのChunkとしてTTS生成する方式」を、**各本文内の段落ごとにChunkを分けて生成する方式**と比較します。

目的は以下の2点です。

1. 音声品質（自然さ・抑揚・発音など）が改善するか。
2. 発話速度がゆっくりになるか。

ただし、品質を犠牲にした減速は評価しません。

## 3. 対象・範囲

- Family：Xのみ
- 記事：『英国の電車マナー』
- レベル：**Advancedのみ**
- 比較対象：ユーザー承認済みの現行完成音声
- Trial方式：本文1・2・3の内部を段落単位でChunk分割
- Production変更：禁止

本文1・2・3という大きな構造、およびComment／In One Line等の既存構造は維持してください。

変更するのは、本文内部のTTS生成単位のみです。

## 4. Family Aの既存音量調整・接続方式の調査と適用

過去のFamily Aで、音声のつなぎ目が不自然にならないように音量調整などを行っていたはずです。

Repo・CURRENT_SPEC・過去のTrial／Production実装を確認し、以下を調査してください。

- どのような音量調整・音声接続処理が存在するか
- どの方式が現在の正式Production仕様か
- 段落単位Chunk分割に再利用できるか
- 既存の処理を再利用する際の注意点

**利用可能な承認済み方式を、今回のTrialへ適用してください。**

単純に音量だけを揃えればよいと決めつけず、段落境界のポーズ、音量差、接続の自然さを確認します。

新たな独自の音声加工方式は原則導入しないでください。

## 5. A/B比較条件

**A：現行Production方式**

- 本文1・2・3をそれぞれ1 Chunkで生成
- 承認済みの完成音声を再利用

**B：段落単位Chunk方式**

- 本文1・2・3の各内部段落を独立ChunkとしてTTS生成
- 元の文章、Voice、TTSモデル、速度Prompt、Style等はAと同じ
- Family Aの既存接続・音量調整方式を適用

段落分割以外の条件はできる限り固定し、差異がある場合は記録してください。

## 6. 検証・評価

### ① 音声品質

- 発音の正確性
- 抑揚・リズムの自然さ
- 声質・話し方の一貫性
- Chunk接続時の不自然な変化
- 文章や段落全体としての聞きやすさ

### ② 速度

- 本文1・2・3それぞれの発話WPM
- 本文全体のWPM
- 無音時間とポーズの変化
- 実際の発話速度と、ポーズ増加による見かけ上の減速を区別

### ③ QCD

- 音声生成費用の増減
- TTS呼出回数
- 生成・検査所要時間
- 再生成・ASR検査への影響
- Production採用した場合の量産単価への影響

品質基準は既存の承認済み仕様を適用し、今回独自の基準を無断追加しないこと。

## 7. Trial成果物

**ユーザーが直接A/B試聴比較できるページ**を作成してください。

最低限、以下を含めます。

- A：現行Production版
- B：段落Chunk版
- 本文1・2・3の個別比較再生
- 本文全体の比較再生
- WPM・ポーズ・音声品質・費用の比較結果

既存の試聴ページ構造をできる限り再利用し、ページ開発に不要な工数をかけないでください。

## 8. 進行・STOP条件

- 既存仕様の確認とTrial準備は並列化する。
- Trial専用経路で実施し、ProductionのPrompt・コード・完成音声を変更しない。
- 既存の品質Gateと安全条件を守る。
- 不具合は承認範囲・予算内で自律的に修正・検証する。
- 不要な追加Trial・磨き込みは行わない。
- 開発費は既存の日次予算・個別承認枠を遵守する。
- 新仕様採用、Production配線、重大なQCDトレードオフはユーザー承認を必須とする。

## 9. 最終報告

Fableによる独立評価を行い、以下を簡潔に報告してください。

1. 段落単位Chunk化によって音質は改善したか。
2. 発話速度は遅くなったか。
3. 接続・音量の不自然さは発生したか。
4. Family Aのどの既存方式を再利用したか。
5. 費用・処理時間はどれだけ変化したか。
6. A/B試聴URL
7. Trial Closeout Status（VALIDATED／REJECTED／USER_DECISION_REQUIRED）

Trial成功時もProduction採用へ自動移行しないこと。

**最終目的は、ユーザーが実際に音声を比較し、段落単位Chunk方式の採否を判断できる状態にすることです。**
```

§1(記事BのCloseout)は別agent(FAMILY-X-NEWS-2ARTICLES-E2E-02 委任_04)が並行実施中。本委任では扱わない。

## 1. Fableが把握している前提(鵜呑みにせず確認)
- 比較対象A=承認済み完成音声: `er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02/a2/`(assembled/Family_X_Audio_A2_UK_TRAIN_SPEAKER_PLAYBACK.wav、segment wav、`tts_generation_results.json`等)。**このディレクトリ配下は一切変更しない(読み取り・コピーのみ)。**
- Family A音量調整の正式仕様: `CURRENT_SPEC.md:2099`(scalar RMS基準、`er003_v1_n3_01_assemble.py::apply_a2_gain`/`apply_b1_gain`、`compute_gain_for_target_rms(max_peak=0.95)`、Previewのみgain=1.0)、`CURRENT_SPEC.md:2133`(A2のmandatory post-process=silence trim[各TTS生成関数内部]・Assembly時gain正規化・A2 6% slowdown invariant gate)。他にsegment間無音(gap)仕様、クロスフェード有無、Family X audio runner `er019_family_x_audio_production_runner_01.py` がどれを継承しているかを調査すること。
- Family Xの本文segment名(full_story_part1/2/3等)、段落区切りの所在(本文md/JSON内の改行構造)、Advの速度指示(Prompt内の速度文言・後処理slowdownの有無)、Voice/モデル/Style設定は `tts_generation_results.json`・runner・`er019_output/.../uk_train_speaker_playback/run_nws_02` 系のtext成果物から確定する。
- 既存の速度計測: WPM計測/速度Gate関連の既存実装(例: SHORT-CLIP-SPEED-GATE-01 `docs/research/SHORT-CLIP-SPEED-GATE-01/`、er006系の速度計測、`CURRENT_SPEC.md`の「WPM」Grep)を再利用する。発話WPM(無音除外の articulation rate)と総WPM(無音込み)を分けて測れる既存手段があるか確認。
- 既存ASR検査(Audio Validation Gate、er006 secondary ASR、local faster-whisper)をDEV経路から呼べるか・Production store/telemetry(master_audio_store manifest、reuse_telemetry、raw_usage_log等)を汚染しない呼び方を確認(OPEN-490: 全回帰等のtelemetry書換えをstageしない)。
- 既存試聴ページ構造: `user_test/uk_train_speaker_playback_e2e_02/index.html`、A/B比較形式の先例 `docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/`(比較試聴ページ)や `user_test/family_y_trial_01/index.html`。
- Existing Spec / Prior Trial Check Gate(PM_GOVERNANCE 21節): 段落/文単位chunk化・chunk結合の過去Trialの有無を `DECISION_LOG.md`/`DECISION_LOG_HISTORY.md`/`OPEN_ITEMS.md`/`OPEN_ITEMS_HISTORY.md`/`docs/research/` でGrep(キーワード例: chunk, 段落, paragraph, 分割, split, concat, crossfade, gap)し、A(既存仕様あり)/B(過去Trialあり・未採用)/C(新規)に分類。過去不採用方式の無断再導入禁止。

## 2. Phase 1 成果物(すべて `docs/research/FX-PARAGRAPH-CHUNK-TTS-TRIAL-01/` 配下、API 0)
1. `EXISTING_SPEC_CHECK_01.md`: §4の調査結果(存在する音量調整・接続処理の一覧/現在の正式Production仕様/段落Chunkへ再利用可否/注意点)、21節A/B/C分類、Family X Adv経路が現に適用している後処理の一覧(関数名・ファイル:行)。
2. `DESIGN_01.md`: Trial設計。
   - DEV専用script(新規、例 `er113_fx_paragraph_chunk_trial_01.py`、Production moduleのimportは可だがProduction fileの編集・Production出力dirへの書込みは不可。出力は `er113_output/fx_paragraph_chunk_trial_01/`)。
   - 段落分割規則(本文1・2・3の内部段落=本文テキストの空行区切り等、根拠を示す)、各chunkのTTS入力(Prompt/Voice/モデル/Style/速度指示はAと同一であることをA側の記録から逐一対応表で示す。差異が不可避なら列挙)。
   - 接続方式: 承認済みFamily A/X方式の再利用(gain正規化の適用単位・silence trim・段落境界ポーズの秒数は既存仕様から選ぶ。既存仕様に段落間ポーズの定義がない場合は、既存のsegment間gap等の候補を挙げ、採用案と理由を明記。独自の新加工は導入しない)。
   - 評価計画: ①品質=既存Gate(ASR一致・Repetition QA等、Adv本文に現に適用されるもの)をB各chunkと結合後本文に適用+人間試聴用の観点リスト(ユーザー原文§6①)。②速度=本文1/2/3と本文全体のWPM(発話WPM/総WPM)、無音合計・ポーズ数・分布のA/B比較、見かけ減速の分離。③QCD=TTS呼出回数・費用・所要時間・ASR検査回数の増減、量産単価への換算。
   - 予算: Phase 2見積(TTS call数×単価、ASR費用。出典のある単価のみ)。上限はFableが50円で設定(300円以下=自律枠)。有料run起動回数・同一run起動間隔150秒以上・TTS直列化flagの尊重・RESTART_STORM(5分3回)遵守を設計に明記。
   - A/B試聴ページ設計: `user_test/fx_paragraph_chunk_trial_01/index.html`(既存ページ構造再利用。A/Bの本文1・2・3個別+本文全体、比較表)。mp3は `user_test/` 配下のみ追跡可。
   - 撤退条件・STOP条件・Production不変の保証方法(DEV script以外の差分0をcommit前に `git status` で確認)。
3. `OPUS_REVIEW_REQUEST_01.md`: 条件A(新しい処理フロー設計)レビュー依頼。論点を絞る: (a)接続・音量方式の選択が承認済み仕様の正しい再利用か、(b)A/B条件の同一性(段落分割以外固定)が担保されるか、(c)WPM・ポーズ計測が「実発話速度」と「ポーズ増による見かけ減速」を分離できるか、(d)既存Gateの適用でProduction store/telemetryを汚染しないか、(e)過去Trial/不採用方式の再導入がないか。テンプレ `docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md` があれば従う。
4. 無料で先行できる準備(並列化原則): A側の計測(A本文1/2/3 wavのWPM・無音・ポーズ計測、ローカル処理のみ)、段落分割器+結合器の実装とunit test(TTSを呼ばない部分)、ページ雛形、費用台帳 `BUDGET_LOG_01.md`(Phase 1=0円)。**有料API呼出は一切しない**(Gemini/OpenAI TTS、OpenAI ASR等。ローカルfaster-whisperは無料だが、Production storeに書き込む経路は使わない)。
5. SSOT: `OPEN_ITEMS.md` に新規OPEN登録(11-8分類必須。種別=Trial、Status=TRIAL_DESIGN_PENDING_OPUS_A、DEV専用・Production変更0・`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`付与なし)、`DECISION_LOG.md` に着手記録1件、`docs/pm/ACTIVE_TASK.md` 固定ヘッダに本管理IDの行を1行追加(**並行agentが同時編集中。編集直前に再Readし、自行のみ最小Edit。他行は触らない**)。SSOT編集は編集前にscratchpadへバックアップ、編集後 `git diff --stat -- <file>` で異常な大量差分がないことを確認。
6. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 497 --out docs/pm/delegation_log/2026-10-25_FX-PARAGRAPH-CHUNK-TTS-TRIAL-01_DELEGATION_01.md`。抽出結果の冒頭が本委任文(「管理ID: FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 委任_01」)と一致するか確認し、不一致なら index 494〜499 を順に試す(`--index -1`は不可)。
7. Git: `git status` → 対象pathのみ `git add <path>`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status` で意図外D/Aなし・secret grep 0件・Production file差分0を確認 → `git commit --only -- <path…>` → `git push origin HEAD:main`。他agentの差分が同一SSOTファイルに混在する場合はHEAD blob+自分の変更のみの一時index方式で自分の変更だけをcommit。wav/raw_usage_log/STOP/lock/ACTIVE_TASK/RESULT_PACKETは追跡しない。
8. 報告: `docs/pm/RESULT_PACKET_FXPC1.md`。内容=①§4調査の要約(Family Aのどの方式が正式仕様で、何を再利用するか)、②21節A/B/C分類結果、③A側実測(WPM・無音)、④Phase 2設計の要点と見積、⑤OPUS_REVIEW_REQUEST_01.mdの所在、⑥変更ファイル・commit hash、⑦`check_delegation_prompt.py`結果、⑧費用(0円)・問題点。**Phase 1完了時点でSTOPし、Phase 2(有料生成)は開始しない。**

## 3. 禁止・注意
- Production code/Prompt/flag/閾値の変更、Production出力dir・store・manifest・telemetryへの書込み、承認済み完成音声・公開ページ(`uk_train_speaker_playback_e2e_02`)の変更。
- 新しい独自音声加工(独自クロスフェード・独自EQ・独自ラウドネス規格等)の導入。既存承認方式の再利用に限る。
- 品質基準の無断追加。評価は既存承認済みGate+ユーザー原文§6の観点。
- 使用モデル: Trial B側のTTSモデルはA側と同一(最新モデル原則の例外理由=「A/B条件同一性のため」と記録)。評価・計測に生成AIを使う場合は最新世代を使い報告にモデル名を記載。
- `.venv\Scripts\python.exe` を使用。自PID以外のprocess終了禁止。