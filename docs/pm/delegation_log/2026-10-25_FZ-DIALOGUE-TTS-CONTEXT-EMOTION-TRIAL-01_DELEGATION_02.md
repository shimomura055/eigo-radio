FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_02: Opusレビュー(必須M1〜M6、推奨R1〜R4)の反映→事前登録更新→Phase 1a(LLM感情情報の生成1 call、約0.5円)まで。**TTS生成(Phase 1b)は本委任に含めない**(Fableが感情情報8件をレビューしてから別委任で起動=Opus M6)。DEV専用、Production変更禁止。

## 前提
Phase 0成果(commit 47862f875): `docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01/{EXISTING_SPEC_CHECK_01,SELECTION_01,DESIGN_01,PREREGISTERED_CRITERIA_01,OPUS_REVIEW_REQUEST_01,BUDGET_PLAN_01}.md`、`er118_fz_dialogue_context_tts_trial_01.py`(+test 21)、`er118_output/fz_dialogue_context_tts_trial_01/phase0/`、試聴ページ骨格(untracked)。対象8 clip(Adv Magi dialogue全件)。費用上限30円(Trial固有)。

## Fable採否(Opusレビュー、下記全文を `OPUS_REVIEW_01.md` に無改変保存。冒頭にレビュー日2026-10-25・claude-opus-5-5・Fable採否1行追記)
必須M1〜M6=全採用。推奨R1〜R4=採用(R2は同一atempo実装の切出しが可能なら採用、難しければ両方加工前+注記)。任意O1(A/B伏せ切替、決定論のみarm②')=今回は不採用(②の効果確認後に別検討)。arm構成=②ctx×2 take+対照base×1 take(約16円、retry予備込み約19.5円)、3armは同一セッションで連続実行(Phase 1bで)。
<<<OPUS_REVIEW_01
# OPUS_REVIEW_01 — FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 独立技術レビュー(条件A、Phase 1有料実行前)

レビュー者: Opus(読み取り専用。編集・実行・API呼出は0)。対象: DESIGN_01 / SELECTION_01 / PREREGISTERED_CRITERIA_01 / EXISTING_SPEC_CHECK_01 / BUDGET_PLAN_01 / OPUS_REVIEW_REQUEST_01 / `er118_fz_dialogue_context_tts_trial_01.py` / phase0成果物 / INVESTIGATION_01 / ユーザー指示原文。照合のため次のコードも読んだ: `er012_b_family_voices_production_01.py:483-615`、`er002_common.py:94-124`(既存style本文)、`er003_b1_p4c_audio.py:78-100`、`er113_fx_paragraph_chunk_trial_01.py`(sink隔離・protected)、`er011_human_review_lock_01.py`(segment key・lock store)、`er003_v1_n3_01_tts_generate.py:434-`(速度加工の外側ループ)。
Production採用の可否は判断しない。

## 0. 全体判定
**必須修正(M1〜M6)を反映すれば、Phase 1へ進んでよい。設計の見直しまでは不要。**
骨格(Structured SeparationのSTYLE区画への追記、`style_prefix_override`の既存引数を使う、DEV dirへ直接生成、sink隔離、prompt shaの照合)は妥当。ただし次の2点はPhase 1の結論を直接誤らせる欠陥であり、有料実行前に直す必要がある。
- **leakage検出に実害のある見逃しがある**。最も危険な2ケースの両方を検出できない(M1)。
- **中立fallback文が中立ではなく、「平板に読め」という指示になっている**(M2)。
推奨arm構成: **②×2 take+対照base×1 take(BUDGET案C、約16円、retry予備込み約19.5円)。3armは同じ時間帯にまとめて実行する。**

## 1. leakage — 判定: 重大(M1で解消可)
### 1-1 現行の`leakage_check`が見逃す具体例
- **part2_c7**: 本文は`"Please let him still think I'm pretty,"`で末尾が読点。CONTEXTには`"she whispered."`が2回入っている。モデルが続けて「…pretty, she whispered」と読んだ場合、余剰語は2で>3に届かず、専用語にも該当せず、3語連続候補「pretty she whispered」は本文と結合した文字列なのでCONTEXT側に存在しない。**flagged=Falseで通過する。**
- **part2_c2**: 直後のセリフ`Twenty dollars.`(2語)が混入しても通過。
- **話者ラベル**: 「Della: Will you buy my hair?」のように話者名を1語読んでも通過。
- **Productionの長さ検査(本文+15字)**: 「she whispered」(13字)は通過。
- **retryによる隠蔽**: 最終ASRだけを検査すると漏れ率が過小評価される。
- **部分一致**: `g in tgt_str`は単語境界を見ない。
### 1-2 必須修正M1(leakage_check差替え)
- アライメント方式: 本文tokenとASR tokenを`difflib.SequenceMatcher(autojunk=False)`で照合し、insert/replace区間でASR側が余分に持つtokenを抽出。`flagged`=余分token区間長≥2、または余分tokenのいずれかが「CONTEXTにだけある語」に含まれる。`needs_listen`=余分tokenが1つでもある。新Gateではなく観測項目。
- 全attemptを検査(`attempts_log`各`asr_text`)、`leakage_any_attempt`と`leakage_final`を分ける。base armにも適用(期待値0)。
- 単語境界一致(`f" {g} " in f" {s} "`)。
- 長さ補助フラグ: ②の長さ > 1.4×median(①, base) かつ差が+0.6秒超なら`needs_listen`。
### 1-3 必須修正M3(CONTEXT表現)
- 演出文の重複除去: Stage direction行を決定論抽出済み`manner_words`だけの行に置換(例: `Manner words from the narration: whispered, kept returning`)。
- 会話タグを逐語で入れない: 直後の地の文が会話タグ(小文字で始まる5語以下の文、例`she whispered.`)なら逐語で入れず`manner_words`行だけで伝える。
- 前後セリフは英語逐語のまま残すが、TEXTと同じ引用符形式をやめ別発話であることを明記: `Spoken line before (said by Della; not part of this line): Will you buy my hair?`
- 見出しとして読まれないように、「complete story」との混同を防ぐため、HEADで否定。
CONTEXT_HEADの差分:
-CONTEXT FOR THIS ONE LINE (delivery reference only. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
+CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)

## 2. 既存styleとの干渉 — 判定: 修正推奨(実質は必須、M3に含める)
- 既存style本体を変えず追記だけにする方針は妥当。
- 「台本に無い感情を足すな」との関係: TAILで「この行の感情の根拠は物語の地の文である」と明示。
- 見落とされている衝突: LEVEL2「Avoid becoming passive, flat, or overly restrained」「Use a clearly wider vocal range」は、ささやき・静かな告白(part2_c7、part3_c8)と正面衝突。放置するとNO_EFFECTの偽陰性。
- 解決策: 追記文の中で「この行が静かな行であれば汎用指示より静かで遅くてよい。それ以外は汎用指示に従う」という限定的優先順位(追加のみ、①の文字列は不変)。報告で明示。
- 学習教材として真のささやきは避ける: soft/hushed voiceで語は明瞭に。
- 追加音を禁止(sighs, sobs, laughs, audible breaths)。
CONTEXT_TAILの差分:
-Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. Keep the delivery natural and believable: let the feeling described above come through in the voice, without theatrical over-acting and without adding any emotion beyond what is described. Do not read any word of this CONTEXT block.
+Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.

## 3. 感情情報のLLM生成 — 判定: 修正推奨(M2・M6は必須)
### 3-1 検査をすり抜ける経路
- 本文自身を根拠引用にすれば逐語一致は常に成立。引用から飛躍した感情ラベルは決定論では捕捉できない。`has_explicit_cue`はLLMの自己申告。
### 3-2 M2(必須): fallback文を本当に中立にする
- 現行`EMOTION_FALLBACK_STATE`は「…so deliver it plainly」で平板化を指示。NO_EXPLICIT_CUE/DISCARDEDのときは`Speaker's state of mind`行自体を出さない。
### 3-3 M6(必須、費用0): TTS前のFableレビューと強度語の禁止
1. EMOTION_DEVELOPERへ追記(LLM生成前に固定、sha再計算):
+8. Use mild, plain wording for feelings (for example "a little nervous", "quietly hopeful"). Never use intensity words such as despair, devastated, terrified, heartbroken, ecstatic, overjoyed, overwhelmed, hysterical, desperate.
+9. Describe the feeling, not acting instructions: do not write sob, cry, tremble, gasp, sigh, laugh, or similar sound or gesture directions.
+10. At least one evidence quote must come from the narration or another speaker's line, unless the line itself contains an exclamation or question that shows the feeling.
2. 決定論の追加検査: 禁止語(語幹一致)を含めば`DISCARDED`(理由`intensity_word`)。
3. 8件のFableレビューをTTS前に行い`llm/emotion_review.json`に保存。discardは中立(M2)へ。
### 3-4 決定論のみの案との比較: LLM案の維持でよい(0.5円)。②'は任意枠。

## 4. 再利用分離 — 判定: 概ね問題なし(M5と推奨2点)
- review lock store・sink隔離・Master Audio Store・segment_idは問題なし。
- M5(必須): `comparison_valid`を追加(最終採用attemptの`instruction_type`がminimal_fallbackでない かつ prompt shaが期待値一致)。fallback経路の`n_tts_calls`過少計上も記録。`generate_arm`は1 clipのNGで`break`するが、cap・protected diff・STOP以外は記録して続行。
- 推奨: er113のrepo全体mtime走査を流用(除外dir=`er118_output/…`、`user_test/fz_dialogue_context_trial_01`)。`model_version`の記録。

## 5. 交絡と比較設計 — 判定: 修正推奨
1. 対照arm: 必須級。①=既存take+base_t1でn=2、②=ctx_t1+ctx_t2でn=2。
2. モデル更新: baseが検出器。ctx_t1→base_t1→ctx_t2を同一セッションで連続実行。
3. 速度加工前の原音比較は機械比較として妥当。推奨: Production同一実装のatempo加工(ASR再検証なし、API 0)を②・baseに適用し最終相当を試聴の主音声、原音はdev側。難しければ両方加工前+注記。Production Advの加工後ASR再検証で静かな発話が落ちる可能性は未検証の限界として報告。
4. 音量: 試聴の主音声は揃えた音量で正しい。ページ注記「本番でも各セリフの音量は揃えられるため、音量の大小ではなく、声の柔らかさ・息づかい・速さ・抑揚で比べてください」。揃える前のRMSはdev側指標。F0の信頼性注記。

## 6. 評価設計 — 判定: 修正推奨(M4は必須)
M4(必須): Statusは3値(REJECTED/VALIDATED/USER_DECISION_REQUIRED)、`TRIAL_COMPLETE_NO_EFFECT`等は下位ラベル。VALIDATEDの決め方: (d)機械的効果観測を必須条件にしない。提出時点で(a)(b)(c)(e)(f)(g)が成立なら「試聴可能」=**USER_DECISION_REQUIRED(試聴判断待ち)**。ユーザー試聴で改善→VALIDATED(Production採用ではない)、悪化/効果なし→REJECTED。(d)は補助証拠。
期待方向表: clipごとに主指標1つ。part2_c7=揃える前RMS↓/part3_c4=調音話速↓/part3_c8=調音話速↓/part3_c2=調音話速↑/part3_c6=F0中央値↑/part2_c2・c5=方向なし(過剰監視: ②両takeのF0幅>1.5×max(①,base)なら過剰演技疑い)/part2_c4=安定監視(②両takeが①・baseの範囲±20%内)。
「take間差を超える」=完全分離(②の2値がいずれも①の2値より期待方向側)。帰無下1件1/6。方向あり5件のうち3件以上で分離=「効果あり(機械的)」(偶然約3.6%)、1件以下=「機械的には効果なし」、2件=保留。逆向きの完全分離も記録。
試聴ページ: 参考takeを「A' 現行方式の別take」「B' 改善方式の別take」と明記。各カードにLLM出力(話者の状態・場面)の日本語短い要約を添える。任意: A/B伏せ切替。

## 7. 費用 — 問題なし
推奨②×2+base×1=約16円(retry予備込み約19.5円)。任意②'=+約5円(別Trialが合理的)。LLM生成はM6反映後の1 call、sha更新。

## 8. 修正一覧
M1 必須 leakage_checkアライメント方式・全attempt・base適用・単語境界・長さ補助フラグ+test(c7「…pretty, she whispered」、c2「…hair twenty dollars」、話者名1語)/M2 必須 中立fallback時は状態行を出さない/M3 必須 CONTEXT表現(重複除去、会話タグ逐語除外、引用符変更、HEAD/TAIL差分)/M4 必須 事前登録改訂(Status 3値、(d)補助、主指標1つ、完全分離、3/5・1以下)/M5 必須 comparison_valid、NGで中断せず続行/M6 必須 EMOTION_DEVELOPER 8〜10、強度語deny、Fableレビュー(`emotion_review.json`)/R1 推奨 3arm同一セッション、model_version記録/R2 推奨 最終相当音声を試聴主音声/R3 推奨 repo全体mtime走査/R4 推奨 ページ注記・参考take名称・LLM状態の日本語要約/O1 任意 A/B伏せ・②'。
M1〜M6反映後、testをPASSさせ、事前登録を固定し直す。同じ設計内容での再レビューは不要。M3の文言を大きく変える場合だけ再確認。
OPUS_REVIEW_01>>>

## 実施
1. `OPUS_REVIEW_01.md`保存。module改修: M1(leakage_checkアライメント方式・全attempt・base適用・単語境界・長さ補助フラグ)、M2(中立時は状態行省略、「plainly」撤去)、M3(manner_words行、会話タグ逐語除外、前後セリフの表記、HEAD/TAIL差分を**逐語で**適用)、M5(`comparison_valid`、`n_tts_calls`注記、NGで続行)、M6(EMOTION_DEVELOPER 8〜10追記、強度語deny検査、`emotion_review.json`の枠)、R1(連続実行の順序ctx_t1→base_t1→ctx_t2、`model_version`記録)、R2(Production同一のatempo実装の切出し可否を調べ、可能なら最終相当音声の生成関数を追加[API 0]。不可なら理由を記録し両方加工前+注記)、R3(er113のrepo全体mtime走査流用)、R4(ページ注記・参考take名称・LLM状態の日本語要約欄)。testを追加(M1の3例、M2、M3の文言固定、M5、M6 deny)→全PASS。
2. `PREREGISTERED_CRITERIA_01.md`→`_02.md`(M4: Status 3値写像、(d)補助、主指標表、完全分離ルール、3/5・1以下、逆向き記録、leakage定義、comparison_valid、Fable評価手順)。`DESIGN_01.md`改訂履歴。`BUDGET_PLAN_01.md`更新(arm構成=ctx×2+base×1、約16〜19.5円)。**ここまでcommit/push**(LLM・TTS未観測のうちに固定)。
3. Phase 1a: `PHASE1_GO.json`(managed_id、cap_jpy=30、arms=[ctx,base]、承認者=Fable 委任_02、根拠=ユーザー指示30円枠)を作成。日次累計確認(`docs/pm/tools/daily_dev_cost_01.py`)、`tools/stop_scope_check_01.py --managed-id FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01` rc0。**LLM感情情報1 call(gpt-6-luna、8件一括、約0.5円)のみ実行**(`.venv\Scripts\python.exe`)。決定論検査(根拠逐語一致・語数・固有名詞・強度語deny)を適用し、8件の結果(感情・心理状態/場面/返答の仕方、根拠引用、accept/DISCARDED理由)を `llm/emotion_candidates.json` と `EMOTION_CANDIDATES_01.md`(Fableレビュー用: 1件ずつ、英文セリフ・前後文脈の要点・LLM出力・根拠引用・決定論検査結果)に保存。**TTSは実行しない**。
4. `OPEN_ITEMS.md` OPEN-516を1行更新(Opus反映・Phase 1a完了・Fableレビュー待ち)。`docs/pm/ACTIVE_TASK.md`。委任文逐語 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01_DELEGATION_02.md`(冒頭「FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_02」、index 575〜605を走査。`--index -1`不可)。
Git: 禁止=`git add -A/-u/-f`、amend/rebase/force push/stash/clean/reset/checkout -f/`git checkout -- <file>`。対象pathのみ `git commit --only`→`git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`[競合は両方残す]→push)。secret grep 0件。並行agent稼働中。

## 報告(`docs/pm/RESULT_PACKET_FZDC2.md`+返答)
M1〜M6/R1〜R4の反映要点(HEAD/TAIL最終文言、EMOTION_DEVELOPER sha)、test件数、R2の可否、**8件の感情候補を返答に全文転記**(Fableがaccept/discardを判断する)、LLM実費、Phase 1bの起動手順(arm順序・見積)、commit hash・raw URL、RESULT_PACKET 4行。