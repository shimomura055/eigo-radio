## 管理ID

KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02(ユーザー承認済みTrial、Trialのみ)。一時ファイル `docs/pm/ACTIVE_TASK_KE2.md` / `docs/pm/RESULT_PACKET_KE2.md`(commitしない)。並行: 別Sonnet 3件(Trial-02 `er039_*`、Task C `er040_*`/`user_test/fixed_shell_champion_trial_01/`、Task B追補 `er038_output/`/`user_test/tts_all_role_style_trial_01/`)→ これらに触れない(`er038_tts_all_spoken_role_style_trial_01.py` はimport/読み取りのみ可)。本タスクの所有: 新規 `er041_key_phrase_advanced_english_explanation_trial_02*.py`(+test)、`er041_output/key_phrase_advanced_english_explanation_trial_02/`、`user_test/kp_advanced_explanation_trial_02/`、新規 `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02_REPORT.md`、`docs/pm/design_key_phrase_advanced_english_explanation_trial_02.md`、delegation_log。**Production code・正式Prompt・CURRENT_SPEC・routing・Production Master Audio Store は一切変更しない**。SSOT 4点は編集権なし。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**(push競合時は `git merge origin/main` のみ、conflictは中断報告)。

## 性質/到達上限Status/禁止事項

- 性質: Trial(Product仕様確認、text優先)。到達上限Status: `REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED`(ユーザー確認前は `USER_DECISION_REQUIRED`、Production配線へ進まない)。
- 費用: 上限¥20(Guardrail。英語解説生成 数call+任意の音声化 約10 segment)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 禁止(ユーザー明示): Key Phrase再選定(Hormuzの既存完成済み5 Key Phraseをそのまま使う、A/BでPhrase完全同一)、Phrase選定ロジックへの変更、記事本文再生成、新仕様の勝手な作成(`KEY-PHRASE-LEVEL-SPEC-TRIAL-01` の既存英語解説仕様・Promptを可能な限り再利用)、新しいFactの追加、日本語訳の直訳的英訳、無意味なTTS再生成、Production Master Store汚染。APIキー本文表示禁止。試聴リンクはGitHub Pages。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02_01.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02_01.md --json-out docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02_01.md_check.json`、結果1行記録。
T-2: 音声化を行う場合のみ `TTS_EXECUTION_MODE=STANDARD` を明示、Trial専用Store(`er041_output/.../master_store/`)、`--budget-jpy` 明示、想定外の大量生成ならAPI実行前STOP。
T-3: 上記「性質」欄の定型文に従う。

## ユーザー指示(原文)

「Task D — Advanced Key Phrase English Explanation Trial。目的: 過去の KEY-PHRASE-LEVEL-SPEC-TRIAL-01 では Key Phrase選定/Standard・Advanced差/Topic Word/解説言語 を同時に変えたため、Phrase選定Prompt v1の失敗によってTrial全体がREJECTされた。今回はPhrase選定ロジックを一切触らず、Advancedで『英語Key Phrase+日本語意味』vs『同じ英語Key Phrase+平易な英語解説』だけを比較する。
対象: Hormuzの既存完成済みKey Phraseをそのまま使う。再選定禁止。同じ5 Key Phraseについて比較。A: 現行(英語Phrase+日本語意味)。B: Advanced候補(英語Phrase+平易な英語解説)。PhraseそのものはA/Bで完全同一。
英語解説仕様: まず KEY-PHRASE-LEVEL-SPEC-TRIAL-01 の既存Trial資産・Prompt・設計を確認。前回決めた英語解説仕様を可能な限りそのまま再利用し、勝手に新仕様を作らない。方向性: Advanced学習者向け/英語のみで理解できる/短い/易しい英語/辞書的すぎない/記事文脈に依存しすぎない/Phraseの意味を自然に説明/新しいFactを足さない/日本語訳を英訳しただけの不自然な文にしない。既存Trialに具体的な長さ・形式・Promptがある場合はそちらを優先。
評価: 各Key Phraseについて Phrase/現行日本語意味/Advanced英語解説候補/必要なら日本語での参考意味 を並べる。評価観点: Advanced学習者に英語だけで意味が伝わるか/説明が難しすぎないか/長すぎないか/Phraseそのものより説明文の方が難しくなっていないか/再利用性があるか/記事固有説明に寄りすぎていないか/意味が正確か。
音声: 今回の目的はProduct仕様確認なのでまずtext確認を優先。ただしコストが軽く、Task BのRole Trial資産を流用できるなら、KEY_PHRASE_EN/KEY_PHRASE_EXPLANATION_EN Roleで音声化した比較も作ってよい。その場合もPhrase選定・記事本文は再生成しない。
過去REJECTとの関係: 過去TrialのREJECT理由はAdvanced英語解説そのものの失敗ではない。主因はPhrase selection Prompt v1(4セットすべてFAIL/想定一致5/20/Topic Word未選択/動詞句偏重/レベル配分不安定)。今回はその失敗要因を完全に除外して解説言語だけをisolated Trialする。
コスト/QCD: 既存artifact再利用、記事再生成禁止、Key Phrase再選定禁止、無意味なTTS再生成禁止、Production Master Store汚染禁止、Production Prompt変更禁止、CURRENT_SPEC変更禁止。
Closeout(12項目): 1 Existing Spec/Prior Trial確認 2 実施内容 3 Candidate 4 成果物 5 品質評価 6 Regression 7 Cost 8 再利用可能性 9 新規発見 10 Trial status 11 USER_DECISION_REQUIRED 12 Production変更ゼロの証拠。ユーザー試聴・確認後にSTOP。」

## Fable補足

- Existing Spec/Prior Trial: `KEY-PHRASE-LEVEL-SPEC-TRIAL-01_REPORT.md`(Grep `英語解説|explanation|Prompt` → 該当範囲。英語解説の仕様[長さ・形式・語彙レベル]とPrompt逐語、REJECT理由がPhrase選定側であることの記載)、関連 `er0*` Trial script(Grep `LEVEL_SPEC|level_spec|explanation` in `er0*.py`)、`CURRENT_SPEC.md` Key Phrase節の日本語意味(`japanese_gloss`/`japanese_gloss_tts`)仕様と「Advanced=英語句+日本語意味」の現行記述、OPEN-221。既存の英語解説PromptがあればそのままB生成に使う(無ければ前回設計の方向性に沿った最小Promptを設計書に逐語で記載し「前回仕様不在のため最小新設(Trial限定)」と明記)。
- 入力: Hormuz Advanced(B1B)の完成済み `keywords_canonicalized.json`(`er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/b1b/` 配下をGlob。5件の `display_phrase`/`japanese_gloss`/`source_sentence`)。
- B生成: 1 call(5件まとめて構造化出力: phrase[同一必須、assertで固定]/english_explanation/word_count/参考日本語意味[任意])。候補は原則1案。品質が明らかに悪い場合のみ2案目(理由記録)。決定論チェック: 語数上限(前回仕様の値、無ければ設計書で根拠付き)、Phrase同一性、解説語彙の難易度(既存CEFR/NGSL語彙リストを流用してPhrase本体より難しい語の比率を算出)、新規Fact混入(source_sentenceに無い固有名詞・数字の有無)。LLM rubric 1 call(評価観点7項目、1〜5+根拠)。
- 音声(任意・軽量): Task Bの `er038_tts_all_spoken_role_style_trial_01.py` のRole style(KEY_PHRASE_EN/KEY_PHRASE_EXPLANATION_EN/KEY_PHRASE_JA)を import で流用し、5 phrase × (A: EN+JA意味 / B: EN+EN解説) を Flash-Lite で音声化(Trial Store、¥5程度)。既存のPhrase音声(Task B/Production)が再利用できれば再生成しない。
- 成果物: `user_test/kp_advanced_explanation_trial_02/index.html`(GitHub Pages: 5 phrase × A/B のtext並列表+指標+音声があれば再生)。push後 `curl -sI https://shimomura055.github.io/eigo-radio/user_test/kp_advanced_explanation_trial_02/index.html` で200確認。
- 判定案: `USER_DECISION_REQUIRED`(ユーザー確認待ち)。Sonnetは `VALIDATED` を自己宣言しない。

## 実行コマンド全文

- `.venv\Scripts\python.exe er041_key_phrase_advanced_english_explanation_trial_02.py --source-dir "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/b1b" --out-dir "er041_output/key_phrase_advanced_english_explanation_trial_02/hormuz" --budget-jpy 20`(引数は実装に合わせ逐語記録)
- 音声化(任意): `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er041_key_phrase_advanced_english_explanation_trial_02.py --audio --source-dir "…/b1b" --out-dir "…/hormuz" --trial-store "er041_output/key_phrase_advanced_english_explanation_trial_02/master_store" --tts-backend speech_metadata_flash_lite --budget-jpy 20`
- `.venv\Scripts\python.exe -m pytest er041_key_phrase_advanced_english_explanation_trial_02_test_01.py -q`(Phrase同一性、語数上限、新規Fact検出、Production Store未使用、正式Prompt定数不変)
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er041*_test_*.py"`
- Production無変更の証拠: `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" "er006_output/master_audio_store_01/" | grep -v er041`(空)

## SSOT追記文

RESULT_PACKETへ文案のみ(REPORT_LEDGER新行、DECISION_LOG、OPEN-221への追記案)。

## Git

- add対象: `er041_*`、`er041_output/.../`(json/md、wav非commit)、`user_test/kp_advanced_explanation_trial_02/`、REPORT、設計書、delegation_log+`_check.json`。SSOT編集権: なし。
- メッセージ: `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02: Hormuz既存5 Key PhraseでA(英語句+日本語意味)vs B(同一英語句+平易な英語解説)のisolated Trial+確認ページ`、trailer `Management-ID: KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02`。`git push origin main`。

## 報告(RESULT_PACKET項目)

ユーザー指定12項目(1 Existing Spec/Prior Trial確認[前回の英語解説仕様・Prompt逐語、REJECT理由の切り分け] 2 実施内容 3 Candidate[5 phrase × A/B のtext表] 4 成果物[Pages URL] 5 品質評価[決定論指標+rubric、ユーザー確認待ち項目] 6 Regression 7 Cost 8 再利用可能性 9 新規発見 10 Status案 11 USER_DECISION_REQUIRED 12 Production変更ゼロの証拠)+STOP有無+SSOT文案+commit hash+raw URL。ユーザー向け表記はStandard/Advanced。
