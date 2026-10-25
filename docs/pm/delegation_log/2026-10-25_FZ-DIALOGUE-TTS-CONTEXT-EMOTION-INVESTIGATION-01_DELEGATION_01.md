# 委任文(Fable→sonnet-worker)
管理ID: FZ-DIALOGUE-TTS-CONTEXT-EMOTION-INVESTIGATION-01 委任_01(Family Z セリフTTSの文脈・感情表現 read-only調査。**API 0円、Production/Prompt変更0、新規TTS 0、Trial 0**)

## 0. 最初に
- ユーザー原文を `docs/pm/delegation_log/2026-10-25_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-INVESTIGATION-01_USER.md` に以下を一字一句そのまま保存。

```
# Claude Code指示｜Family Z セリフTTSの文脈・感情表現調査

## 1. 目的

Family Zのセリフ音声について、現行Productionで**前後の会話・場面・登場人物の感情がTTS生成にどの程度反映されているか**を調査してください。

背景として、現在は登場人物のセリフを個別Chunkとして生成していると理解しています。

この方式では、各セリフが前後の文脈から切り離され、感情の変化や会話の掛け合いを十分に表現できていない可能性があります。

まずは実際のProduction仕様・コード・実行記録を確認してください。

## 2. 調査事項

### ① TTSに渡す情報

セリフ1件を生成する際、実際にTTSへ渡している情報を確認してください。

- 当該セリフの英文
- 話者・Voice ID
- Dialogue Style／TTS Prompt
- 直前・直後のセリフ
- 地の文や場面の状況
- 登場人物の感情・心理状態
- 会話全体の流れ

**各項目について、渡している／渡していないを明確にしてください。**

特に、当該セリフ以外の文章がTTSモデルへ入力されているかを確認してください。

### ② 感情表現の仕組み

現行Productionで、次のような表現をどう制御しているか調査してください。

- 怒り・恐怖・喜び・悲しみ
- 驚き・ためらい・皮肉
- 相手への問いかけ・返答
- 同じ人物の場面による感情変化

具体的な制御が存在しない場合は、その旨を明示してください。

単にVoiceを割り当てていることと、感情を制御していることを混同しないでください。

### ③ セリフの分割・生成・組立

現行Productionの処理を確認してください。

- セリフChunkをどの単位で分割しているか
- 同じ話者の連続セリフはまとめられるか
- 別の場面に登場する同一Voiceのセリフは個別生成か
- TTS生成時の文脈と、最終的な音声組立時の前後関係
- retry／再生成時にも同じ情報が渡されるか

### ④ 実際のProduction証拠

『開いた窓』『賢者の贈り物』など、既存Family Zの正式実行記録から代表的なセリフを確認してください。

可能なら次の3例を選んでください。

1. 感情が強いセリフ
2. 相手への返答・掛け合い
3. 同じ人物の感情が変化する場面

それぞれ、**実際にTTSへ送られた入力内容**を確認し、文脈・感情情報の有無を報告してください。

コード上の想定とruntime evidenceは区別してください。

## 3. 評価してほしいこと

以下を明確にしてください。

**A. 現行方式のままで、前後の会話・感情を反映できる設計になっているか。**

**B. 反映できている場合、具体的にどの情報によって実現しているか。**

**C. 反映できていない場合、その理由は何か。**

**D. 同一Voiceのセリフを一括生成して後から分割する方式は、この問題の改善に有効か。**

Dについては、一括生成だけで文脈・感情の問題が解決するとは限らないため、効果と限界を区別してください。

既存機構を再利用できる可能性も確認してください。

## 4. Scope・QCD

今回は**read-only調査**です。

- Production変更なし
- Prompt変更なし
- 新規TTS生成なし
- 追加Trialなし
- 新しい仕様の正式採用なし

既存Repo・CURRENT_SPEC・実行ログ・保存済み音声成果物を利用し、原則API費用0円で調査してください。

Fableによる報告内容の照合を行い、推測と確認済み事実を区別してください。

## 5. 最終報告

以下の順に簡潔に報告してください。

1. **結論：セリフTTSは文脈・感情を把握しているのか**
2. TTSへ渡す情報の一覧
3. 実際のProduction入力例
4. 感情制御の現行仕様
5. 現行方式の問題と影響範囲
6. 同一Voice一括生成方式の有効性・限界
7. 改善が必要な場合の選択肢とQCD比較
8. 根拠となるコード・runtime evidence・関連仕様

**重要：調査結果を受けた改善TrialやProduction変更は、別途ユーザー判断とします。**

技術的な細部だけでなく、英語学習ラジオとしての会話の自然さ・感情表現にどの程度影響するか、PM判断できる形で報告してください。
```

- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 520 --out docs/pm/delegation_log/2026-10-25_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-INVESTIGATION-01_DELEGATION_01.md`。冒頭が「管理ID: FZ-DIALOGUE-TTS-CONTEXT-EMOTION-INVESTIGATION-01 委任_01」と一致するか確認、不一致なら index 517〜523 を順に試す(`--index -1`不可)。

## 1. 調査の当たり(鵜呑みにせず実物で確認)
- Family Z正式経路: `er026_family_z_fiction_production_runner_01.py`(plan/support/tts_b1b/tts_a2段、clip単位)、`er062_family_z_structure_01.py`(話者割当・Dialogue分割・決定的Voice割当)、Z会話生成器(OPEN-479でsegment_id未渡しの修正履歴あり)、Family Z Dialogue速度仕様v2(FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01)、Z Voice正式表(FAMILY-Z-VOICE-PRODUCTION-WIRING-01)、TTS呼出の共通層(`er003_v1_sing01_news_tail_fix.py` 系の生成関数、style_prefix、Gemini TTSのPrompt組立)、発音resolver(er025)のstyle prefix注入。CURRENT_SPECを「Family Z」「Dialogue」「Voice」「style」「感情」「emotion」「tone」でGrep。
- runtime evidence: 『開いた窓』`er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01/`、『賢者の贈り物』同配下の正式run、『猿の手』『二十年後』。各clipの`tts_generation_results.json`/prompt dump/style_prefix記録/provenanceから、**実際にTTSへ送られた入力全文**(本文+style prefix+その他)を取り出す。保存されていない場合は「保存なし(コード上の組立から再構成)」と明記し、コード想定とruntime evidenceを区別。
- 過去Trial/仕様の照合(21節): 感情・文脈注入に関する過去Trial(Family B Voices、Family Y Persona/Voice Trial、Z Voice設計のOPUS_REVIEW等)で「セリフ前後文脈をTTSへ渡す」「感情タグ」「一括生成→分割」が検討・不採用になっていないか(`DECISION_LOG*.md`/`OPEN_ITEMS*.md`/`docs/research/FAMILY-Z-*`/`FAMILY-Y-*`/`FAMILY-B-*`をGrep)。

## 2. 作業(API 0)
A. `docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-INVESTIGATION-01/INVESTIGATION_01.md`: ユーザー原文§2①〜④を項目ごとに「渡している/渡していない/条件付き」+根拠(file:行、runtime evidence path)で表にする。§3 A〜Dに回答(Dは効果と限界を分け、既存機構[例: X段落Chunk Trialの結合処理、C/Zのclip接続、Family Yの複数Voice生成]の再利用可能性を記す)。§5-7の選択肢(例: (1)現状維持 (2)style prefixに前後1〜2セリフと感情ヒントを注入 (3)同一話者連続セリフのまとめ生成 (4)場面単位の一括生成→分割[ASR整列で切る]等)をQCD(品質見込み/量産単価増分/処理時間/実装規模/リスク[ASR Gate・HR Lock・再生成単位の増大])で比較。**推奨は付けてよいが採用判断はユーザー**。英語学習ラジオとしての会話の自然さへの影響度を、3例の実音声(保存済みwav/mp3)を聴ける範囲で所見(機械指標があれば併記、なければ「人手試聴必要」と明記)。
B. 3例の選定(『開いた窓』『賢者の贈り物』等から: 感情が強いセリフ/返答・掛け合い/同一人物の感情変化)と、それぞれの「実際のTTS入力全文」「前後のclip」「Voice/Style」「生成結果(Gate・retry)」を `EVIDENCE_01.md` に逐語で記録。
C. 推測と確認済み事実を明確に分ける(各記述に[確認済み: path]または[推測]を付す)。
D. SSOT: `OPEN_ITEMS.md` に新規OPEN(種別=調査、11-8分類、Status=INVESTIGATED_PENDING_FABLE)、`DECISION_LOG.md` 1件、`docs/pm/ACTIVE_TASK.md` 自行(並行agent多数: FX-CORE-NUMERIC 委任_04、FAMILY-Z-STUDY-TEXT 委任_10、FX/FZ-CHUNK 委任、FZ-SOURCE-ESSENCE。編集直前に再Read・最小Edit・衝突時再試行)。SSOT編集前にscratchpadへバックアップ、編集後 `git diff --stat -- <file>` 確認。`py`使用。
E. Git: `git status` → 対象pathのみ `git add`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status`(意図外D/Aなし・secret 0件・Production file差分0) → `git commit --only -- <path…>` → `git push origin HEAD:main`。
F. 報告 `docs/pm/RESULT_PACKET_FZDTC1.md`: ユーザー原文§5の1〜8の順で簡潔に(結論を最初に)。変更ファイル・commit、`check_delegation_prompt.py`結果、問題点。raw URL(INVESTIGATION_01.md、EVIDENCE_01.md)。

## 3. 禁止
Production code/Prompt/flag/Seed変更、TTS/LLM/Web等の有料呼出、Trial実施、新仕様の採用提案をSSOTへ仕様として書くこと(選択肢の比較に留める)、他agentのrun dirへの書込み、自PID以外のprocess終了。