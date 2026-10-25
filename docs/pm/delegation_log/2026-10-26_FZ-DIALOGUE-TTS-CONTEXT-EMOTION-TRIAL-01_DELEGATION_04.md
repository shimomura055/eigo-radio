管理ID: FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_04(2026-10-26 JST、ユーザー指示による追加比較Trial=追加2作品。本委任=Phase 0(作品・セリフ選定+設計差分+費用計画)+Phase 1a(感情情報LLM 1〜2 call)。TTS生成(Phase 1b)はFable感情レビュー後の委任_05)。報告先 `docs/pm/RESULT_PACKET_FZDC4.md`(新規)。あなたはsonnet-worker、委任元Fable。本委任文を `check_delegation_prompt.py` で検証し結果をRESULT_PACKETに記録。

## 0. 並列注意(重要)
別agent(FAMILY-Y-PRODUCTION-LAUNCH-01 委任_09)が同時稼働中で、`docs/pm/ACTIVE_TASK.md`・`OPEN_ITEMS.md`・`CURRENT_SPEC.md`・`DECISION_LOG.md`・`docs/pm/REPORT_LEDGER.md`・`docs/pm/USER_DECISION_REGISTER_01.md`・`er121_*`・`user_test/family_y_*`を所有している。**本委任ではこれら共有ファイルを編集しない**(SSOT更新は委任_05でまとめて行う)。あなたの書込先は `docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01/`・`er118_*`・`er118_output/`・`docs/pm/delegation_log/2026-10-26_FZ-*`・`docs/pm/RESULT_PACKET_FZDC4.md` のみ。gitは対象pathのみ `git commit --only <paths>`(index.lock競合時は30秒待って再試行、3回失敗なら未commitのまま報告)。他agentのプロセス・一時fileに触れない。

## 1. ユーザー指示(2026-10-26)— 逐語で保存
次の原文を**一字も変えず** `docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01_USER_02.md` に保存する(先頭に「ユーザー指示原文(2026-10-26、Fable経由で逐語保存)」の1行を付けてよい):

```
# Family Z｜セリフTTS文脈・感情付与 追加比較Trial

## 1. 目的

『賢者の贈り物』で実施したセリフTTSの文脈・感情付与Trialについて、ユーザー試聴では現行方式との差が分かりづらかった。

追加2作品で同様の比較を実施し、前後の文脈や登場人物の感情をTTSへ渡すことで、セリフの自然さ・感情表現が実際に改善するか検証してください。

**今回は追加Trialのみ承認します。Production採用・仕様変更は承認していません。**

## 2. 対象作品・セリフ選定

- Family Zの既存作品から追加2作品を選定。
- 原則として既存の確定済み本文・Voiceを利用。
- 感情変化、緊張、驚き、怒り、不安、喜びなど、文脈が音声表現に影響しそうなセリフを優先。
- 各作品6〜10セリフ程度を目安とし、極端に短いセリフばかりにならないようにする。
- 感情や場面が異なる複数のセリフを含め、特定の感情だけに偏らせない。

対象作品の選定はClaudeに委任します。選定理由を記録してください。

## 3. 比較条件

前回Trialと同じ基本方式を使用します。

**A：現行Production方式**
- 文脈・感情の追加指示なし。

**B：文脈・感情付与方式**
- 話者の感情、場面、前後の会話、必要な地の文の情報をStyle指示に追加。

比較では本文・Voice・TTSモデル・速度等を揃え、文脈・感情指示の有無以外を原則変更しないでください。

各条件2takeを基本とします。

既存Trial音声・保存済み成果物を再利用できる場合は活用し、不要なAPI生成を避けてください。

## 4. 評価

以下を確認してください。

1. 文脈・感情に沿った声の抑揚・演技が改善したか。
2. 自然さが向上したか。過剰演技や不自然な表現がないか。
3. ASRによる本文一致、読み飛ばし・言い直し・文脈情報の音声混入がないか。
4. 同じ条件の2takeで効果が安定しているか。
5. 改善が見られたセリフと見られなかったセリフに、どのような特徴があるか。

前回の事前登録評価基準は結果に合わせて緩めないでください。追加分析を行う場合は元の判定と区別してください。

機械指標だけで主観的な音声品質を最終決定せず、ユーザー試聴による比較判断を残してください。

## 5. 試聴ページ

追加2作品について、ユーザーがA/Bを簡単に聴き比べられるページを制作してください。

- 作品・セリフごとにA/B各2takeを掲載。
- 該当セリフ本文と場面・感情の簡潔な説明を併記。
- 可能なら前後の文脈も確認できるようにする。
- どの条件が改善版かを明示。
- 『賢者の贈り物』の既存Trial結果とも比較できるようにする。

## 6. 費用・進め方

- **今回の追加Trial予算上限：30円。**
- この上限は追加2作品の合計とする。
- 上限内でのセリフ数・再利用・生成回数の最適化はClaudeに委任。
- 上限内で有効な比較が難しい場合は、予算を超えずに必要な調整を行う。品質を維持できない場合は報告する。
- 独立作業は並列化し、不要な待機や日付分割を避ける。

## 7. 完了条件・報告

- 追加2作品のA/B試聴ページを公開。
- 比較結果、ASR・安全性検査、実費を報告。
- 前回『賢者の贈り物』も含む3作品で、効果の有無と傾向を整理。
- Fable独立評価を実施。
- Trial終了時はREJECTED／VALIDATED（限定）／USER_DECISION_REQUIREDの適切なStatusで管理。
- CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS等、必要なSSOT記録とGit反映を行う。

**STOP条件：** 予算上限超過、重大な品質・安全問題、承認外の仕様変更が必要な場合。

本Trialの結果が良好でも、Productionへの配線は行わず、ユーザーによる試聴・正式採用判断を待ってください。
```

## 2. 前提(既存成果物。全文読込は必要箇所のみ)
- 前回Round 1: OPEN-516(OPEN_ITEMS.md該当行)、`docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01/{DESIGN_01,PREREGISTERED_CRITERIA_02,OPUS_REVIEW_01,EVAL_01,TRIAL_RESULT_01,BUDGET_LOG_01,EMOTION_CANDIDATES_01,SELECTION_01}.md`、DEV専用script `er118_fz_dialogue_context_tts_trial_01.py`(+test)、出力 `er118_output/fz_dialogue_context_tts_trial_01/`、試聴ページ `user_test/fz_dialogue_context_trial_01/index.html`。Round 1実費10.07円=26 TTS call(ctx×2 take+base×1 take、①=Production既存clipを読取専用で再利用)+感情LLM gpt-6-luna 1 call 0.0975円。
- Fableの位置づけ: Round 1の機械判定=事前登録02どおりREJECTED相当(主指標1/5、(e)2語clipで不成立)、ユーザー試聴=「差が分かりづらい」(上記原文§1)。本Roundは**同一方式・同一事前登録基準(PREREGISTERED_CRITERIA_02)の追加検証**であり、設計の新規構造はないためOpus条件Aは既存OPUS_REVIEW_01を再利用(新しい処理フローを追加する場合は実装前に止めて報告)。到達上限=VALIDATED(限定)。Production配線・既存Prompt/閾値/reuse key等の変更は禁止。
- 調査OPEN-511の作品別セリフ比率: Open Window/After Twenty Years約49%・Monkey's Paw約25%・Melos約20%・Magi約13-16%・Tell-Tale Heart約0%。

## 3. 作業
A. 選定(`SELECTION_02.md`新規): Family Zの既存確定作品(Production完走・公開済み・本文確定)から2作品を選定。基準=ユーザー原文§2(感情変化・緊張・驚き・怒り・不安・喜び等の多様性、6〜10セリフ/作品、極短セリフ偏重回避=目安として語数4語以上を主体とし、2語以下は各作品1件以下)。候補作品ごとに「対象level(Adv/Std等)・Voice・dialogue clip数・候補セリフ一覧(本文・話者・直前直後の文脈・想定される感情)・選定理由/不選定理由」を記録。Round 1と同じく既存Production clip(①)が再利用可能であること(wav/ASR記録が存在)を確認してから確定。
B. 費用計画(`BUDGET_PLAN_02.md`新規): 上限30円=2作品合計。Round 1実測(TTS≈0.39円/call)から、セリフ数×3 call(ctx t1/t2+base t1)+感情LLM+retry予備(10%)で見積り、**30円以内に収まるセリフ数を確定**(例: 計14〜16セリフ前後が目安。見積が超える場合はセリフ数を減らす。予算分割・日付分割による回避禁止)。A条件は「①Production既存clip(take1相当・API 0)+base_t1(新規)」で2 take、B条件はctx_t1/ctx_t2。追加TTSを減らせる再利用があれば明記。Cap guard=`PHASE1_GO.json`方式を踏襲(cap_jpy=30、Round 1分と分離した新出力dir `er118_output/fz_dialogue_context_tts_trial_02/`)。
C. 設計差分(`DESIGN_02.md`新規、短く): Round 1 DESIGN_01からの差分のみ(対象作品・出力dir・ページ構成=2作品+賢者Round 1結果への相互リンク/同一ページ内比較・前後文脈表示)。er118 scriptの変更は「作品/level/出力dirをパラメータ化」「ページに前後文脈と賢者Round 1へのリンクを表示」の範囲に限定し、生成関数・Style追記方式・CONTEXT区画の書式・leakage検査・ASR検査・分離条件は**無変更**。test更新してPASS(API 0、network遮断harness `netblock_harness_01/sitecustomize.py`下)。
D. Phase 1a(有料、感情情報LLM): 事前に `py tools/stop_scope_check_01.py --managed-id FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 --run-dir er118_output/fz_dialogue_context_tts_trial_02 --out er118_output/fz_dialogue_context_tts_trial_02/stop_check_委任_04.json`(rc=3なら停止)。`PHASE1_GO.json`(cap_jpy=30、scope=Phase 1a、approved_by="Fable(委任_04、ユーザー2026-10-26追加Trial承認30円)")を作成し、Round 1と同じ手順(gpt-6-luna、EMOTION_DEVELOPER rule・根拠引用の逐語一致検査・強度語deny)で2作品分の感情・場面情報を生成(1作品1 call、計2 call以内)。結果を `EMOTION_CANDIDATES_02.md` に(ACCEPTED/NO_EXPLICIT_CUE/DISCARDED、根拠引用付き)。**TTS生成(gen-session)は実行しない**(Fableの感情レビュー後、委任_05)。有料runは `.venv\Scripts\python.exe`、cost_log記録を有効化し実費を `BUDGET_LOG_02.md` に記録(未記録なら「未確認」、推定値を費用表に使わない)。
E. 試聴ページ雛形: `user_test/fz_dialogue_context_trial_02/index.html` の生成ロジック(R4踏襲、noindex、PAGE_NOTICE、A/B各2take、本文+場面感情説明+前後文脈、改善版の明示、賢者Round 1ページへのリンク)を実装しtestで確認(音声未生成のため公開はしない)。
F. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01_DELEGATION_04.md`(Nは613前後、`--index -1`不可。「委任_04」「RESULT_PACKET_FZDC4」を含むものを探す)。
G. Git: secret grep 0件、対象pathのみ(§0の制約)、`git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP)。禁止: `git add -A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f、`git checkout -- <file>`。wav/raw_usage_log/STOP/lock/PHASE1_GO/RESULT_PACKETは不追跡。

## 4. 禁止・境界
- Production file/Prompt/閾値/reuse key/Gateの変更禁止。新flag追加禁止。DEV専用経路のみ。
- 有料は本委任で感情LLM 2 call以内(目安0.2円)。TTS生成禁止。
- 事前登録基準(PREREGISTERED_CRITERIA_02)は変更しない。追加分析指標を提案する場合は「追加分析(事前登録外)」として別節に書く。
- 選定でユーザー判断は求めない(選定はユーザーが委任済み)。

## 5. 報告(RESULT_PACKET_FZDC4.md: 現在の状態/何をやったか/何が分かったか/何が残ったか/ユーザー判断候補/補足)
必ず含める: (1)選定2作品と理由(不選定理由含む)・セリフ一覧(語数・想定感情・話者)、(2)費用計画(セリフ数・call数・見積・30円内の根拠)と本委任実費・日次累計、(3)感情候補の件数(ACCEPTED/NO_EXPLICIT_CUE/DISCARDED)とレビュー用一覧の所在、(4)er118変更差分とtest結果(API 0確認)、(5)委任_05(TTS生成→解析→ページ公開→3作品横断整理→SSOT)の実行コマンド案と所要見込み、(6)commit hash・push結果・raw.githubusercontent.com URL。