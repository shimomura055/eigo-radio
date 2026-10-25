FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_01(Phase 0: 既存仕様確認・対象セリフ選定・改善方式(文脈+感情)の設計・DEV実装・試聴ページ骨格。**API 0**。有料生成はPhase 1(別委任、Opusレビュー後)。Production file/Prompt/flag/再利用仕様の変更禁止)

## ユーザー指示(2026-10-25、逐語はStep 0で保存)— 要点
- 目的: Family Z『賢者の贈り物』のセリフ音声で、①現行方式(セリフ本文+既存Voice+既存汎用Style)と②改善方式(①と同一本文・Voice・TTSモデル・生成設定を維持し、Style情報に「話者の感情・心理状態/場面の状況/直前・直後の会話(原則1〜2セリフ)/地の文の演出情報/相手の発言への反応」を追加)を比較し、自然さ・臨場感・感情表現が改善するか検証。Q>D>C。Production採用・実装は対象外、到達上限VALIDATED。
- 対象: 代表的なセリフ8〜12件(Della/Jim両方、喜び・驚き/悲しみ・不安/ためらい・戸惑い/ささやき・静かな発言/感情が変化する場面/相手の発言を受けた返答を可能な範囲で網羅。機械的網羅で不自然に増やさない)。比較は同じ英文・同じVoice。
- ②の条件: 文脈・感情情報は原文と場面から妥当に導ける範囲/原作にない感情・演技を創作しない/本文英文は変更しない/読み上げ対象は当該セリフのみ(文脈・演出指示を発話させない)/朗読として自然、大げさな演劇表現を求めない/①②の違いは文脈・感情情報の追加のみ。感情・文脈情報の作成方法はClaude/Fableが設計、既存の文章・構造化データを最大限活用し不要なLLM呼出を避ける。
- Step 1: CURRENT_SPEC、先行調査 `docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-INVESTIGATION-01/{INVESTIGATION_01,EVIDENCE_01}.md`、OPEN-511、現行TTS Prompt・Voice設定、既存音声・再利用仕様を確認。**特に「Dialogue音声の再利用キーにStyle hashが含まれない問題」**: ②の新Styleで①の保存済み音声が再利用されるのを防ぐ(Productionの再利用仕様は変更せず、Trial内で確実に区別する方法)。
- Step 2: 各セリフに話者/英文/直前・直後の文脈/場面の状況/想定する感情・演出/選定理由を記録。
- Step 3: ①は既存音声が有効なら再利用、②は新規生成、1セリフ=1 TTS call維持、試聴時の音量条件統一、交絡回避、**②のStyle追加情報が実際のTTSリクエストに渡った証拠を保存**。
- Step 4: 本文が正確に発話/余分な文脈を読み上げていない/不自然な間・過度な演技・発音悪化なし/ASR・既存品質検査との整合/場面・人物像との整合。
- 試聴ページ: 8〜12件を一覧、各セリフに日本語の場面説明/英文/話者/①再生/②再生をワンクリックで聞き比べ、可能なら前後の会話も表示。開発者向け詳細は非表示。
- 評価基準: 感情表現/抑揚/会話の自然さ/演出/聞き取りやすさ/安定性。Fableが①②を独立評価、最終はユーザー試聴。新たな必須Gateや数値Gateを作らない。
- **追加API費用上限30円**(Trial固有、他案件の予算流用不可)。超過見込みはSTOP。既存音声・データ再利用、並列化。将来の量産単価影響を概算。
- 報告: 試聴URL/対象一覧と選定理由/①②の具体的Style Promptと文脈情報/Fable比較評価/発話正確性・生成条件・再利用分離の確認/実費と単価影響/Statusと判断事項/SSOT・Git。
- STOP: 30円超過/Production仕様変更が必要/本文・Voice変更が不可避/有効な比較が成立しない/重大問題/範囲外の新方式。

## Phase 0でやること(すべてAPI 0)
Step 0: ユーザー指示原文を逐語保存: jsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl` role=user、冒頭「# Claude Codeへの指示\n## Family Z セリフTTS 文脈・感情表現 比較Trial」→ `docs/pm/delegation_log/2026-10-25_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01_USER.md`(`py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <path> --role user --index N --out ...`。非対応なら`py`で直接走査しtextを無変更で書き出す)。
Step 1: `docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01/EXISTING_SPEC_CHECK_01.md`: 先行調査の結論(TTS入力=1セリフ+汎用style、Structured Separation `build_tts_prompt`(`er003_b1_p4c_audio.py:78-100`)、dialogue style=`er002_common.build_style_prefix()` sha add26d27…、reuse_keyのstyle hash欠落(`er063:738-750`)、組立gain平準化、model `gemini-2.5-pro-preview-tts`、Voice割当=`the_gift_of_the_magi/run_sf_prod_01/voice_assignment.json`)、既存Magi音声の所在(Adv b1b dialogue 8 clip、Std a2のdialogue clip数と所在、wav path、ASR結果)、Master Audio Store/再利用の仕組みとTrialでの分離方法(DEV専用出力dir、Production reuse関数を呼ばない、新規生成wavをStoreに登録しない)。
Step 2: `SELECTION_01.md`: Adv(b1b)を主、必要ならStd(a2)から補い**8〜12件**。各件: clip id/話者/Voice/英文/直前・直後のclip本文(地の文含む)/場面の状況(日本語)/想定する感情・演出(原文の根拠を引用)/選定理由/網羅カテゴリ。既存①音声のpath・sha256・ASR結果・gain値。
Step 3: `DESIGN_01.md`+DEV module `er118_fz_dialogue_context_tts_trial_01.py`(+test): 
 - ②のStyle構成: 既存汎用style(①と同一文字列)+追記ブロック「CONTEXT(読み上げ禁止)」: 話者名と感情・心理状態(1〜2文、根拠付き)/場面(1文)/直前1〜2セリフ・直後1セリフの英文(話者付き)/演出語(地の文の逐語: "she whispered"等)/相手の発言への反応の仕方(1文)。Structured SeparationのSTYLE区画に置き、TEXT TO SPEAKは当該セリフのみ。「CONTEXT内の文は読まない」指示を明記。朗読として自然・誇張しない指示。
 - 感情・文脈情報の作成方法: **決定論抽出を基本**(前後clipはsegment_planから、演出語は当該セリフ前後の地の文から正規表現で動詞句抽出)+感情・心理状態の1〜2文は **LLM 1 call(全対象セリフ一括、gpt-6-luna、JSON、根拠引用必須、約0.3〜0.5円)** で作成し、根拠引用が原文と逐語一致しない項目は破棄(創作防止)。Fable/Sonnetの手書きは使わない(再現性のため)。設計書にPrompt全文(sha)。
 - 生成: 1セリフ=1 call、model/voice/speech config/temperature等は①の実行記録と同一(確認方法を書く)。②は各セリフ1 take(予算が許せば2 take目は任意、Phase 1でFable判断)。**実際に送ったprompt全文・style sha・request configをJSONで保存**(Productionが保存しない点を補う)。
 - 検証: 既存の英語ASR検査(Productionが使うもの)を②に適用→本文逐語一致、CONTEXT語の混入(leakage)検出、長さ・RMS・F0範囲(可能なら`measure`系既存DEV実装再利用)、無音の長さ。①と②をtarget RMSに統一してmp3化。
 - 試聴ページ: `user_test/fz_dialogue_context_trial_01/index.html`(noindex、各セリフ=カード: 日本語場面説明/話者/英文/前後の会話(折りたたみ)/①再生ボタン/②再生ボタン(同じ行、ワンクリック切替)。開発者情報は別ファイル `dev_details.html` へ)。Phase 0ではページ生成コードとダミーなしの骨格まで。
 - 費用見積: TTS ②生成 n件×約0.28円、ASR n件、LLM 1 call、合計(1 take/2 take)。上限30円。
Step 4: `PREREGISTERED_CRITERIA_01.md`(評価6項目の見方、Fable評価の手順[機械指標+ASR+leakage。聴感はユーザー]、Status判定の考え方: VALIDATED=②が本文正確・leakage 0・発音悪化なしで、機械指標/ASR上「文脈に応じた変化」が観測され、ユーザー試聴で判断可能な状態)、`OPUS_REVIEW_REQUEST_01.md`(論点: CONTEXT注入でのleakageリスク/「誇張しない」とstyle既存文「台本に無い感情を足すな」の矛盾の扱い/感情情報のLLM生成の創作リスクと根拠検査/再利用分離の確実性/①②の交絡要因)、`BUDGET_PLAN_01.md`。
Step 5: OPEN登録: `OPEN_ITEMS.md` に新規OPEN(採番規則、11-8分類、Status=TRIAL_PHASE0)1行+OPEN-511に「Trial開始」1行。`docs/pm/ACTIVE_TASK.md`。委任文逐語 `...extract... --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01_DELEGATION_01.md`(N=580前後±10、冒頭「FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_01」)。
Git: 禁止=`git add -A/-u/-f`、amend/rebase/force push/stash/clean/reset/checkout -f/`git checkout -- <file>`。新規ファイル+OPEN_ITEMS行のみ `git commit --only`→`git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`[競合は両方残す]→push)。secret grep 0件。並行agent複数稼働中(SSOTは最後に直前再Read・最小Edit)。

## 報告(`docs/pm/RESULT_PACKET_FZDC1.md`+返答)
選定一覧(8〜12件、カテゴリ付き)/②Style追記ブロックの全文例(1件)/感情情報の作成方法/再利用分離の方法/費用見積(1 take・2 take)/Opusレビュー論点/commit hash・raw URL/RESULT_PACKET 4行。有料実行はしない(Phase 1でFable判断)。