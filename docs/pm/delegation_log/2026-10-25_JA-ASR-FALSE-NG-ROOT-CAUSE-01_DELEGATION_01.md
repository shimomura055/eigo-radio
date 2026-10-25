JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_01(Task B Phase 1〜2: 原因究明と対策立案。**API 0**。Production file変更禁止。Trial実装(Phase 3)は本委任に含めない=設計・事前登録まで)

## ユーザー指示(2026-10-25、逐語は `docs/pm/delegation_log/2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_USER_06.md` に別agentが保存中。存在すれば参照、無ければ本要点で進め、後で照合)— 要点
目的: **正常な日本語TTS音声がASRの文字起こし誤りで不必要にNGとなり再生成・Human Reviewを発生させる問題を根本的に改善**。本当に発音を間違えた音声を誤ってPASSさせてはならない。対象=Family X/Zの日本語音声共通(Family固有の例外が必要なら理由明示)。
Phase 1 原因究明: 月Std題の3 attempt(台本「月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密」、主ASR転写 #1「月野詩は8000句800本超え」/#2「月の死は八千九百本超」(副Azure「月の詩は8900本超」)/#3「月の氏は8000900本超」、判定 #1 NG_PROTECTED/p1_value_diff、#2 NG_BOTH/secondary_not_accepted、#3 NG_PROTECTED/p1_value_diff)について、実音声・TTS入力・ASR転写・判定ログを再検証。重点: ①「しわ」が詩/死/氏と認識された理由、日本語ASRでのひらがな・漢字・同音表記の扱い、既存の表記違い・同音救済仕様が日本語にも適用される設計か/されない理由、「しわ」と「し」は音として異なるため実際の音素欠落を誤救済しない方法 ②「8,900本」が8000/800本/8000900本と誤変換される原因、数値の正規化・照合処理の妥当性、正しい数字と読み間違えの区別、中核数値保持仕様(v4/J2)や既存数値保護判定との整合 ③既存Production仕様: 日本語ASRのPrimary/Secondaryの役割とPASS条件、日本語特有の同音語・表記ゆれ・数詞正規化、TTS再試行・fallback・Human Review移行条件、過去の同種問題と対策、Family X/Zの共通化の余地。ユーザーが3音声を問題なしと判定した事実を根拠として利用するが、それだけを理由に条件を緩めない。
Phase 2 対策立案: 原因に応じて最も効果的で低コストな対策を設計(候補: 日本語の表記ゆれ・同音語照合改善/数字・助数詞の音声と表記の対応改善/Primary・Secondary判定の組合せ/既存同音救済機構の再利用・拡張/本当に発音が違う場合とASR文字変換だけが違う場合の識別)。**品質基準を下げてNGをPASSにするだけの対策は禁止**。誤PASSを増やさず不要な再生成・HRを減らす。既存機構の改善で解決できるなら新システムを乱立させない。
Phase 3(別委任): 原因分析→修正候補→検証→再評価の自律ループ。正常3音声を必ず含める、過去の日本語ASR不一致例を再利用、負例(本当に発音が誤っている音声)も用意、既存の数値・同音・保護語仕様を壊さない、追加API費用と量産単価影響を測定、有料TTS再生成を避け既存音声・記録を再利用。Opusレビューで誤PASSリスク・数値保護整合・別方式を独立検証。
Phase 4: 有効なら共通適用箇所、retry/fallback/regeneration/resumeでの動作、既存仕様との整合、旧検査の整理、QCD改善を確認。**到達上限VALIDATED、配線はユーザー正式採用後**。
報告順: 原因/対策/検証結果/QCD/Fable・Opus評価/Status/必要なユーザー判断。

## 調査対象(Grep/Readで特定。全文読込は最小限)
- 月run: `er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/a2/`(audit: review_lock_state.json、ASR転写、attempt履歴)、`er011_output/attempt_history.jsonl`(theme=moon_shrinking__run_ms_03)、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`、`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`、`er006_output/pool_pilot_01/evidence_density_ab_01/openai_ja_asr_quality_log.jsonl`、`er006_output/pronunciation_ledger_01/ledger.json`。試聴ページ `user_test/family_x_moon_shrinking_02/hr_title/`(mp3 3本)。
- 判定コード: 日本語ASR cascade(er007系、`ja_asr`でGrep)、`er011_human_review_lock_01.py`、`er020_tts_retry_local_rewrite_01.py`、数値保護(`value_guard`/`p1_value_diff`/`NG_PROTECTED`/`secondary_not_accepted`でGrep)、同音救済(`homophone`/`同音`/`表記`/`reading`でGrep)、TTS Normalizer(数字読み、「なになに」欠陥=OPEN既知)、中核数値v4/J2(`er116_fx_core_numeric_retention_01.py`)。
- 仕様: `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`を「日本語ASR」「ja_asr」「Primary」「Secondary」「同音」「数値保護」「Human Review」でGrep(全文読込禁止)。過去の同種OPEN(番号・結論)を列挙。
- Family Zの日本語音声経路(`er026`/`er063`で日本語ASRを使う箇所)との共通点・差分。

## 成果物(`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/`)
- `ROOT_CAUSE_01.md`: ①②③の事実と原因(証拠パス:行付き)。特に「3 attemptがNGになった判定経路の逐次トレース」(どの検査がどの値でNGにしたか)。表記ゆれ救済が日本語に効かない構造的理由。数値正規化の不具合(「八千九百」→数値化できるか、「8000句800」の分裂、句読点/桁区切り)。
- `EXISTING_SPEC_CHECK_01.md`: 既存仕様・過去対策・OPEN一覧・X/Z差分。
- `DESIGN_01.md`(Phase 2): 対策案(複数、推奨1つ)。各案に: 変更箇所(既存機構のどこ)/誤PASSリスクの分析(どんな真の誤発音をすり抜けさせうるか)/数値保護・同音救済・HRとの整合/X/Z共通化/費用(ASR追加call有無)/実装規模。**読み(かな)レベル照合**(漢字表記差を無視し、音素列で比較。「しわ」vs「し」は不一致として検出)や**数値の読み正規化**(「八千九百本」=8900本)等を含めて検討。
- `PREREGISTERED_CRITERIA_01.md`(Phase 3用): 評価セット設計(正例=月3音声+過去の誤NG事例、負例=本当に読み誤った音声[既存の真NG記録から再利用、無ければ最小限のTTS生成見積]、各件数)、指標(誤NG率・誤PASS率・HR発生率)、合格基準、費用見積(案別)。
- `OPUS_REVIEW_REQUEST_01.md`: 誤PASSリスク・数値保護整合・別方式の可能性の論点(1ページ)。
- `BUDGET_PLAN_01.md`: Phase 3の見積(API call別)。
- OPEN登録: `OPEN_ITEMS.md`に新規OPEN(番号は採番規則に従う。11-8分類付き、Status=INVESTIGATING)1行。`docs/pm/ACTIVE_TASK.md`更新。
- 委任文逐語 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_DELEGATION_01.md`(N=571前後±8、冒頭「JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_01」)。
- Git: 禁止=`git add -A/-u/-f`、amend/rebase/force push/stash/clean/reset/checkout -f/`git checkout -- <file>`。新規ファイル+OPEN_ITEMS 1行のみ `git commit --only`→`git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`[競合は両方残す]→push)。secret grep 0件。並行agent4つ稼働中(SSOTは最後に直前再Read・最小Edit)。

## 報告(`docs/pm/RESULT_PACKET_JAASR1.md`+返答)
原因(①②③、確信度と根拠)/対策案と推奨/Phase 3の評価セット・費用見積/Opusレビュー論点/commit hash・raw URL/RESULT_PACKET 4行。推測は「仮説」と明記し事実と区別。