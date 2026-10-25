FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_13(Part 1「Vocabulary & Expressions」案α APPROVED_FOR_PRODUCTION → Production Wiring Phase 0: 既存経路調査・配線設計・Opus条件Aレビュー依頼書・test準備。**本委任ではProduction fileを編集しない**)。あなたはsonnet-worker。Fable(PM)からの委任。

## 0. ユーザー決定(2026-10-25、統合指示。原文全文は並行agent(委任_12)が`docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_05.md`へ保存する。Part 1該当部を以下に逐語)
- Trial-04案α(英語表現のみを別LLMに渡して解説を生成する方式)を**正式採用。Status=APPROVED_FOR_PRODUCTION**。Family X/Zの対象Production経路へ配線し、検証を完了させPRODUCTION_WIREDまで進める。未承認の追加改善・品質基準変更は行わない。
- 採用仕様: Key Phraseの英語表現のみを解説担当の独立LLMへ渡す/本文中の意味に過度に引きずられず一般的・中核的な意味から説明/必要に応じて一般的な使用場面・自然な組み合わせ・類義表現との違い/正確で実用的/本文固有の用法を一般的意味として扱わない/存在しない用法・根拠のない頻度断定・水増しを避ける。`at a moment's notice`の軽微な即応性寄りは把握済み(これだけを理由の追加Trial不要)。既存の品質検査・意味整合性確認は維持。
- Production配線: Trial-04案αのPrompt・入力条件・モデル構成を基本に反映/TrialとProductionの仕様差分を確認/**Key Phrase確定後に解説を生成**/解説LLMへ本文・本文中の日本語意味など分離した情報を再投入しない/ユーザー向け出力=確定済みKey Phrase+本文中の意味+本文引用英文+日本語訳+解説の組合せ/既存のKey Phrase選定・日本語意味確定工程を不要に変更しない。
- **注意: Trial-04で未解決だった「本文引用英文の日本語訳」の生成元を、既存仕様・正式経路で再調査**。既存の承認済み方式で解決可能ならそれを利用。新しい品質仕様や追加の有料生成工程が必要なら、QCD影響とともにユーザー判断へ上げる(未承認の新仕様を暗黙に採用しない)。
- 受入条件(全て満たしたFamilyのみPRODUCTION_WIRED): 1 X/Zそれぞれの正式経路への配線 2 retry/fallback/regeneration/resume整合 3 本文・KP変更時の再生成制御 4 正式runtimeでの実際の発火証拠 5 使用モデル・Prompt・入力・routingの証拠 6 必須Validator/Regression/Integration Test PASS 7 既存Production仕様との整合・Dangling Reference不存在 8 CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS更新 9 Git反映・Fable独立受入。コード実装やDEVテストだけで完了扱いしない。
- 「Part 1の正式採用は、そのために必要な新しい未承認仕様の採用まで包括承認するものではない」。他の進行中X/Z開発を不合理に停止させない。量産単価70円目標を維持し追加原価を計測。

## 1. Fableの運用判断
- Production経路に新しいLLM呼出工程を追加する=新しい処理フロー→**Opus条件A必須レビューを実装前に行う**。本委任はPhase 0(設計)まで。実装は次委任(Opusレビュー後)。
- 並行agent: 委任_12(Part 2 Trial-07、同じdocsディレクトリに`*_07*`を書く。あなたは`PART1_WIRING_*`のみ)/ FZ-SOURCE-ESSENCE 委任_04(Z Production配線+run_sf_prod_02実行中。`er062_*`/`er026_*`等のZ Production moduleを編集・commit中の可能性→**Production fileは読取専用**、未commit差分があれば記録)/ FX-CORE-NUMERIC(er115 DEV)/ FZ-NARRATION-CHUNK(DEV)/ Family Y音声化(er110 Trial)。SSOT編集は直前再Read・最小Edit・衝突時再適用。
- API 0(無料調査・設計のみ)。無料処理は`py`。

## 2. 調査(読むもの、必要箇所のみ)
- Trial-04正本: `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/{DESIGN_04,PROMPT_04,PREREGISTERED_CRITERIA_04,EVAL_04,COMPARISON_04,ADOPTION_NOTE_04,OPUS_REVIEW_02,OPUS_REVIEW_03,run_trial_04.py,INPUT_04.json,OUTPUT_04_*_r1_USER.md}`(案αのPrompt全文・入力=KP英語表現のみ・モデル=gpt-6-luna・出力形式・費用/セット・`japanese_gloss`の扱い・「本文引用英文の日本語訳」の未解決点の記述)。
- Production経路(X/Z共通KP段): `er003_v1_n3_01_scaffold_generate.run_key_phrases(kp_backend="fulltext_p2")`、`er003_key_words_gloss_alignment.py`(`japanese_gloss` :95付近、X2p' meaning_stage)、`sc.run_key_phrase_canonicalization`(hook)、KP音声`xr._generate_key_phrase_segments_b1`、Part 1(語彙解説)の現行生成箇所とページ描画(X: `er019_*`/news runner・page生成、Z: `er026_family_z_fiction_production_runner_01.py`の`support`/`kp`/`pages` stage、`er062_family_z_structure_01.py`)。現行Part 1の「解説」文がどのLLM・どのPromptで生成されているか(Trial-02/03の03d方式が配線済みか、それ以前の方式か)を特定し、置換対象を確定。
- 「本文引用英文の日本語訳」の生成元: 現行Productionで本文引用英文(KPを含む文)の日本語訳がどこで作られているか(Writer日本語原文との対応/gloss/別生成)。Trial-04で未解決だった点を既存仕様で解決できるかを判定。
- retry/fallback/regeneration/resume: X/Zそれぞれの再実行経路(regenerate、resume、Local Rewrite後のKP再確定、HR Lock)でKP確定後の解説生成がどう再実行されるか。KP変更検知のキー(KP文字列sha等)。
- 費用: Trial-04案αの実測(4 call/セット0.458円のうちPart 1分)と、Production採用時の追加原価/セット。モデル選定=Trial-04と同じgpt-6-luna(最新世代原則との整合を記載)。
- SSOT: `CURRENT_SPEC.md`はPart 1/Key Phrase/学習解説/gloss関連節をGrep(全文読込禁止)、`OPEN_ITEMS.md`はOPEN-497・OPEN-484行、`DECISION_LOG.md`はTrial-04/UDR #196関連をGrep、`docs/pm/USER_DECISION_REGISTER_01.md`の#185/#196。

## 3. 成果物(`docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/`)
- `PART1_WIRING_SPEC_CHECK_01.md`: 現行Part 1生成の正本(ファイル:行)、X/Zの経路図(初回・retry・regeneration・resume・Local Rewrite後)、KP確定点、ページ描画点、現行の品質検査(意味整合性確認等)の所在、TrialとProductionの仕様差分表(Prompt・入力・モデル・出力形式・表示名「解説」・gloss併記)。
- `PART1_WIRING_DESIGN_01.md`: 配線設計。(a)実装箇所と関数(新規module推奨: 例`er003_kp_general_explanation_01.py`=KP英語表現のみを入力とする純関数+呼出点をX/Z共通KP段のKP確定直後に1箇所)、(b)入力隔離の保証(本文・日本語意味を渡さないことをコード構造とtestで保証)、(c)出力の組合せ(確定KP・本文中の意味・本文引用英文・日本語訳・解説)、(d)再生成制御(KP集合のsha/表現文字列が変わった時だけ再生成、resume時は保存済み結果を再利用、regeneration/Local Rewrite後にKPが変わればやり直し)、(e)retry/fallback(LLM失敗時の既存retry枠・fallback=従来方式へ戻すか空欄か—**既存仕様に従い、新しい挙動が必要ならユーザー判断事項として分離**)、(f)runtime evidence(model_id・prompt sha・入力sha・routing・before/after解説をauditへ記録)、(g)Validator/Regression/Integration test計画(入力隔離test、X/Z E2E 1記事ずつの発火証拠取得計画と費用見積)、(h)Dangling Reference対策(旧Part 1生成コード・Prompt・testの撤去要否一覧)、(i)CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS更新案(新規OPEN項目案、11-8分類)、(j)追加原価/セットと処理時間、(k)「本文引用英文の日本語訳」の結論(既存方式で解決可/新工程が必要→ユーザー判断事項として分離しQCD影響を記す)。
- `PART1_WIRING_OPUS_REVIEW_REQUEST_01.md`: 条件Aレビュー依頼書(論点: 入力隔離の保証、再生成制御とresume整合、retry/fallbackの既存仕様整合、X/Z両経路の一貫性、Dangling Reference、費用、日本語訳の生成元の扱い)。
- test雛形(Production未編集): `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/part1_wiring_tests_draft_01.py`(入力隔離・再生成制御・出力組合せのtest案、実装後に正式test fileへ移す)。
- `docs/pm/RESULT_PACKET_FZST13.md`、`docs/pm/ACTIVE_TASK.md`自行(gitignore)。
- SSOT: 本委任では**UDR/OPEN/DECISION_LOGへ「APPROVED_FOR_PRODUCTION(配線設計中・未配線)」の事実を最小追記**(OPEN-497行または新規OPEN項目案を起票—新規起票なら11-8分類必須、「承認済み・未配線、PRODUCTION_WIREDと呼ばない」を明記)。CURRENT_SPECの本文変更は実装委任で行う。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 529 --out docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_13.md`(冒頭「FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_13」で照合、不一致なら±5)。`check_delegation_prompt.py`はFAIL想定(非blocking)。
- Git: `git status`→対象pathのみadd(`-A/-u/-f/-N`禁止)→`git diff --cached --name-status`(Production fileが含まれていないことを確認)→`git commit --only -- <path…>`→`git push origin HEAD:main`。secret grep 0件。

## 4. 報告(Fableへ)
(1)現行Part 1生成の正本と置換対象(X/Z別) (2)TrialとProductionの仕様差分表 (3)配線設計要点(a)〜(k) (4)「本文引用英文の日本語訳」の結論(既存方式で可/ユーザー判断が必要) (5)ユーザー判断が必要な事項の有無(fallback挙動・新工程等。無ければ「なし」) (6)実装委任の見積(作業量・E2E発火証拠の費用) (7)変更ファイル・commit・raw.githubusercontent.com URL (8)RESULT_PACKET 4行+「判定整合: 重大NG= / 主因= / 是正対象= / STOP理由= / 提示=」1行。