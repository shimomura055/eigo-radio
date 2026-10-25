# OPUS_REVIEW_REQUEST_01 — 独立技術レビュー依頼(FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01、Phase 1有料実行前)

条件: PM_GOVERNANCE 11-3 条件A(新しい処理フロー/構造の設計)。レビュー対象は設計(`DESIGN_01.md`)・DEV実装(`er118_fz_dialogue_context_tts_trial_01.py`+test)・事前登録(`PREREGISTERED_CRITERIA_01.md`)・予算(`BUDGET_PLAN_01.md`)。有料実行(LLM 1 call+TTS 8〜24 call)は本レビュー後にFableが`PHASE1_GO.json`で開始する。Production採用はスコープ外。

## 背景(3行)
Z『賢者の贈り物』のセリフTTSは、1セリフ+全dialogue共通の汎用style(ナレーション用の長文)のみをTTSへ渡す(先行調査 INVESTIGATION_01)。②案はStructured SeparationのSTYLE区画に、話者の感情・場面・前後の会話・地の文の演出語を足し、TEXT区画は当該セリフのみとして、感情・抑揚・臨場感が変わるかを①(現行)と比較する。①②の差はCONTEXT追記のみ。

## 論点(それぞれに『判定: 妥当/要修正/不足』と代替案を求める)

1. **CONTEXT注入でのleakageリスク**: STYLE区画に英文の前後セリフ・地の文・演出語(`she whispered.`等)を入れると、モデルが読み上げる(特に短いセリフ、`Twenty dollars.`のような2語)危険がある。現設計の防御: (i) CONTEXT冒頭・末尾で「読まない」を二重に明記 (ii) 対象セリフ本文はCONTEXTに入れない (iii) 生成後の決定論検査 `leakage_check`(語数超過>3/CONTEXT専用語/CONTEXT文との3-5語連続一致)。Productionの長さ検査(本文+15字)は小さな混入を通す点も踏まえ、**検出が不足しないか**(例: 混入が短い単語1〜2語、或いは本文の語と一致する語のみ)、`surplus_words>3`のしきい値は妥当か。前後セリフは英語のまま(引用符つき)渡して良いか、それとも話者ラベル付き要約等にすべきか。
2. **「誇張しない」と既存style『台本に無い感情を足すな』『表情豊かに』の矛盾の扱い**: ①②で既存styleは**無変更**(交絡を避けるため)。既存styleには「Give the narration a noticeably animated, emotionally present, expressive delivery」と「Do not add excitement, sadness, urgency, or drama that is not supported by the words」「Do not … exaggerate feelings that are not present in the script」が共存する。②のCONTEXTは『感情の根拠をscript側に与える』ことで「not supported by the words」の条件を満たす狙い。CONTEXT_TAILで「theatrical over-actingなし、記載の感情を超えない」と書いた。この**同居は矛盾せず機能するか**。①②でstyleを共通のまま追記だけにする設計は妥当か(既存styleを②でだけ弱める等の変更は交絡が増えるため不採用)。
3. **感情情報のLLM生成の創作リスクと根拠検査**: gpt-6-luna 1 callで感情・場面・反応を生成し、(a)根拠引用の原文逐語一致 (b)語数上限 (c)文脈原文に無い固有名詞の排除 (d)`has_explicit_cue=false`は中立fallback、で創作を抑える(`validate_emotion_items`)。LLMが原文に根拠のある引用を付けつつ、**引用から飛躍した感情**(例: `she whispered`→『絶望』)を作る危険は検査で捕捉できない。許容するか、追加検査(例: 感情語を許可語彙に限定する、引用と感情語の対応表)が必要か。Madame(感情明記なし)がfallbackになることを期待する設計は妥当か。LLMを使わず決定論のみ(演出語+場面)にする代替案との比較(費用0.5円/再現性)。
4. **再利用分離の確実性**: Productionの`build_reuse_key`はdialogueのstyle hashがNone(`er063:798-814`、`style_text_for`がdialogueで常にNone)。本Trialは (i) Production再利用経路(`run_tts_stage`/cached_entry)を呼ばず `generate_voice_body_wide_margin` を直接呼ぶ (ii) ①は`*_original.wav`の読み取りのみ (iii) ②出力はDEV dir、before/after sha256 snapshotで保護対象の不変を確認 (iv) Trial識別keyにstyle_sha256を含める、で分離する。**漏れ**(例: attempt履歴/Ledger/telemetry等の副作用sink、`review_lock`のsegment_key衝突でHRロックを①のclipに作る等)が無いか。`redirect_production_sinks`の隔離範囲(er113実績あり)で十分か。
5. **①②の交絡要因**: (i) ①は過去take、②は新規take → take揺れとStyle効果の分離不能。対照arm(同一styleの新規take、約4.7円)を提案しているが妥当か、**2 take**(②)と組合せで最小構成は何か。(ii) ①の実行時request記録が無く、modelの更新有無が不明。(iii) 比較対象を速度加工前の原音(`*_original.wav`)にしているが、最終音声の聴き味評価として十分か。(iv) 音量は同一target_rms(0.08425)へ個別gainで揃えるが、『ささやき=小音量』の表現は組立で平準化される(先行調査 §3)。この点を評価でどう扱うか(ユーザー試聴の観点に『音量の大小で表現する演出は組立で消える』と注記すべきか)。

## 追加の確認依頼(任意)
- `capture_tts_requests`(`make_batch_tts_call_fn`の一時差替え+`TTS_EXECUTION_MODE=STANDARD`の局所設定)は、Production設定を暗黙にONにするものではないが、副作用や漏れの観点で問題ないか。
- 対象8件の選定(Adv全dialogue)、カテゴリ網羅、`NEIGHBOR_MAX_CLIP_DISTANCE=4`/`TIMESKIP_NARRATION_WORDS=40`の決定論ルールは妥当か。
- 事前登録の『期待方向表』が結果を誘導・過剰解釈しないか。

## 添付(同ディレクトリ・リポジトリ内)
`EXISTING_SPEC_CHECK_01.md` / `SELECTION_01.md` / `DESIGN_01.md` / `PREREGISTERED_CRITERIA_01.md` / `BUDGET_PLAN_01.md` / `er118_fz_dialogue_context_tts_trial_01.py`(+`_test_01.py`) / `er118_output/fz_dialogue_context_tts_trial_01/phase0/`(selection.json, style_example_part2_c7.json) / 先行調査 `docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-INVESTIGATION-01/`。
