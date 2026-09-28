## 管理ID

FAMILY-Y-VOICE-STRUCTURE-TRIAL-01(ユーザー承認済みTrial)。一時ファイル `docs/pm/ACTIVE_TASK_FY1.md` / `docs/pm/RESULT_PACKET_FY1.md`(commitしない)。並行衝突: 別Sonnetが Flash-Lite(`er003_v1_*`、`er006_audio_cost_pilot_02_*`、`er019_family_x_audio_production_runner_01.py`、`er033_*`、`user_test/flash_lite_*`)と KP 4+1(`er003_key_words_*`、`er030_*`、`er035_*`、prompt template `b1_p2_keywords_l_prompt_template.txt`)を編集中 → これらは編集しない。SSOT 4点(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`)と `docs/pm/PM_GOVERNANCE.md` は**本タスクに編集権なし**(追記文案をRESULT_PACKETへ)。本タスクの所有: 新規 `er036_family_y_voice_structure_trial_01*.py`(+test)、`er036_output/family_y_voice_structure_trial_01/`、新規 `FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_REPORT.md`、`docs/pm/design_family_y_voice_structure_trial_01.md`、delegation_log。**既存のFamily X / Family B / 共有moduleのコード・Promptは一切変更しない(import・関数呼び出しによる流用のみ)**。

## 性質/到達上限Status/禁止事項

- 性質: Trial(Production実装なし)。到達上限Status: `REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED` のいずれか(Sonnetは判定案を出すのみ、最終はFable/ユーザー)。Trial結果が良好でも `APPROVED_FOR_PRODUCTION` へ進めない。
- 費用: 上限¥40(Guardrail、テキスト生成のみ、**TTS/ASRは実行しない**)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 禁止(ユーザー明示): Production正式pathへの配線/Family Y専用Revision仕様の新設(R1→R2はFamily Xの既存スクリプト・Prompt・処理をそのまま使う)/Trial結果を根拠にProduction採用を独自判断/新しい改善案の追加Trial/周辺仕様のついで修正/Family Y専用の別名称の新設(Family Xに同等概念があればその正式名称に統一)/機械的な禁止語リスト/賛成・反対・中立の機械的割り当て。新規記事テーマの選定はしない(下記の既存記事を使う)。`git add -A` 禁止、履歴書き換え禁止、APIキー本文の表示禁止。新仕様候補・追加改善案を発見しても実装せず報告してSTOP。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を `docs/pm/delegation_log/2026-09-28_FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_01.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_01.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_01.md_check.json` を実行、結果1行記録。
T-2: TTSなし(本Trialはテキストのみ)。
T-3: 上記「性質」欄の定型文に従う。

## ユーザー指示(原文)

「Family Yの改善Trialを実施してください。目的: Family Yで現在見えている以下の課題を改善できるか確認する。- VoiceがFactを言い直してしまう - 後半ほど抽象論に寄りやすい - Voice同士の差が弱くなる - Voiceが独立した『人の発言』ではなく、記事解説の一部に聞こえる。今回の基本思想: Factは本文が担当する。Voiceは『反応・視点・懸念・経験則』を担当する。ただしVoiceにも話すためのFactは必要なので、全Factを渡すのではなく、各Voiceに必要最小限のFactだけを割り当てる。
まず確認すること: Family Xに以下と同等の既存概念・正式名称があるか確認。- News全体から本質的なFactのみ抽出する仕組み - Writerへ渡すFact数を絞る仕組み - R1→R2のEntertainment性向上Revision。同じ概念が既にFamily Xにある場合、Family Yだけ別名称を作らず、Family Xの正式名称に統一。R1→R2はまずFamily Xと同じ既存スクリプト/Prompt/処理をそのまま使ってTrial。Family Y専用Revision仕様を最初から新設しない。
Trial設計(Writerの前段): 1. Fact Selection(Family Xの既存正式名称・仕組みがあればそれを使用。News全体から本当に必要なFactだけを抽出、記事全体Writerへ渡すFact数も制限) 2. Voice Fact Assignment(各Voiceに必要なFactのみ。原則1 Voice=Fact 1件、必要な場合のみ最大2件。全Factを全Voiceへ渡さない) 3. Voice Angle / Stakeholder(各Voiceについて、どのFactを材料にするか/誰の立場・Stakeholderか/何を見るAngleかを先に定める。例: Voice 1→Fact A/利用者視点、Voice 2→Fact B/運営側視点、Voice 3→Fact A+B/実務・公平性視点。文章構成は固定せず、Writerの自由度は残す) 4. Voice Writer(VoiceはFactを再説明しない。Factはcontextとして利用するがscriptとして読み直さない。『According to the report...』『The company said...』『The study found...』のようなFact紹介から始める方向へ寄せない。Voiceは反応・懸念・期待・経験則・具体的なStakeholder視点から話す。Fact is context, not script.) 5. 抽象化防止(各Voiceは最後まで具体的なStakeholder/状況を持つ。society/trust/the future/technology in general等の大きな抽象論へ逃げない。ただし機械的な禁止語リストにはしない。内容上必要なら使用可) 6. Voice重複チェック(既存Family B/Voice系にVoice diversity・役割重複防止・perspective分離等の既存仕様がないか必ず確認。あれば新しく重複実装せず流用/拡張。確認したい重複: 同じFactに依存しすぎていないか/同じ懸念を言っていないか/同じAngleになっていないか/同じ結論に着地していないか。賛成・反対・中立を機械的に作る必要はない) 7. R1→R2 Revision(まずR1として記事全体を完成。全記事完成後にFamily Xと同じ既存R1→R2 Revisionを適用。R2ではFact追加ではなく、人間らしい反応/自然な言い回し/少し意外な視点/Voiceごとの温度差/Entertainment性が改善するかを見る)。
Trialで確認したいこと(R1/R2比較): 1 VoiceによるFact言い直しが減ったか 2 Voice同士の差が明確になったか 3 後半の抽象論化が減ったか 4 『記事解説』ではなく『人の発言』に聞こえるか 5 Factを絞ったことで情報不足になっていないか 6 Fact Assignment+Angle先決めがWriterの自然さを損ねていないか 7 Family Xと同じR1→R2 RevisionがFamily Yにも有効か 8 既存Family BのVoice diversity仕様との重複/競合がないか。
報告: 使用した記事/Family Xから流用した正式名称・仕組み/Family Bから流用した既存Voice重複対策の有無/R1/R2/R1→R2で何が変わったか/4つの当初課題それぞれの改善状況/新しく発見した問題/QCD上の懸念/Trial終了status。」

## Fable補足(Existing Spec Check・前提)

- Family体系(`CURRENT_SPEC.md`:1325-1362): Active=X/Y/Z、**Family Yは将来Voices系を想定した別Familyで着手済み実装なし**。Family B(Voices)はlegacy(read-only参照可、コード変更不可)。本TrialはユーザーがFamily Yとして明示承認したTrialであり、`er036_*` の**Trial専用script**として実装する(Family Bのrunner `er012_*` を変更しない)。
- 使用記事: **新規テーマは選ばない**。既存Family B Voices記事のうち、元News/Fact資料と3 Voice構成の出力が揃っている記事(候補: `er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/`「When AI Helps Choose Who Gets Hired」。Glob `er012_output/**/ai_hiring*` で他レベルの有無を確認)を使う。**1記事・1レベル**(既存出力が両レベルにあればAdvanced[B1]、無ければ存在するレベル)で実施し、既存のFamily B出力を「Before(現行)」、Trial R1/R2を比較対象とする。
- Family X正式名称の確認先: `CURRENT_SPEC.md` Family X節(Grep `Family X` `Fact` `R1` `R2` `Entertainment`)、`er019_family_x_ja_writer_o_r1_r2_01.py`(JA Writer O R1/R2)、`er019_family_x_*` のFact抽出/絞り込み(Grep `fact` -i in `er019_*.py`、`NEWS-FAMILY-X-*_REPORT.md`)。Family Xの英語本文Writer側のR1→R2があるか(Grep `r1|r2|revision` -i in `er019_*.py` `er003_v1_n3_01_articles_generate.py`)。存在する正式名称をそのまま使い、設計書に「Family X正式名称 → 本Trialでの使用箇所」の対応表を載せる。**Family XにR1→R2が英語本文向けに存在せずJA向けのみの場合、そのPrompt/処理をそのまま英語Voiceへ適用できるかを確認し、できない場合はSTOP(USER_DECISION_REQUIRED: 流用不能の理由と選択肢)**。
- Family B既存Voice仕様の確認先: `CURRENT_SPEC.md` B-Family(Voices)節(Grep `Voices` `diversity` `perspective` `役割`)、`er012_*.py`(Grep `diversity|perspective|stance|role` -i)、`docs/pm/delegation_log/B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-REVIEW-01.md`(既存レビュー)、`B-FAMILY-*_REPORT.md`。既存の重複防止・多様性QAがあれば関数呼び出しで流用(変更せず)。
- Fact Selection→Voice Fact Assignment→Angle/Stakeholderの「前段」は、**LLM 1 callの構造化出力(JSON)**で作る(Fact一覧[本文Writer用、上限は Family X の既存制限値があればそれ、無ければ設計書で根拠付きに提案し数値をFable判断として記録]、各Voiceの fact_ids[1件、最大2件]/stakeholder/angle)。Writer Promptはこの割当をcontextとして渡し、「Fact is context, not script」「Fact紹介で始めない」「最後まで具体的なStakeholder/状況を持つ」を**方針文として**記述(禁止語リストにしない)。
- 評価: R1/R2それぞれについて、8確認項目を (a) 決定論的指標(各Voice冒頭のFact紹介型開始の有無、Voice間のfact_ids重複、抽象語の出現位置[後半集中か、参考指標として]、語数)と (b) LLM評価1 call(rubric: 4課題×Before/R1/R2、1〜5点+根拠引用)の両方で記録。判定案は「Before→R1→R2」の比較で示し、Sonnetは `VALIDATED` を自己宣言しない。

## 事前指定Read一覧

- `CURRENT_SPEC.md`: Family X節(Grep `## Family X` → 節範囲)、B-Family(Voices)節(Grep `B-Family` → 節範囲)、Family Z節の「Family Y」言及(:1190-1200)
- `er019_family_x_ja_writer_o_r1_r2_01.py`: R1/R2の関数・Prompt定義(Grep `def |PROMPT|R2` → 該当範囲)
- Family X Fact抽出/絞り込み: Grep結果の該当関数のみ
- `er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/a2/article.md`、`parts.json`、`audit/writer_result.json`(既存Before出力と入力Fact)
- `er012_*.py` のVoice diversity関連関数(Grep → 該当範囲)
- `docs/pm/delegation_log/B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-REVIEW-01.md`

## 事前指定Grep一覧+追記位置・更新位置の手順

- 上記「Fable補足」のGrep群。結果を設計書 `docs/pm/design_family_y_voice_structure_trial_01.md` §1(Existing Spec Check: 分類A/B/C、Family X正式名称対応表、Family B既存Voice仕様と流用箇所)に記載してからTrial実装に進む。
- Trial script `er036_family_y_voice_structure_trial_01.py`: 入力(既存記事のFact資料)→前段1 call→本文+Voice Writer(既存Family BのWriter呼び出しが流用可能なら流用、不可なら最小のWriter callをTrial内に実装[Family B Prompt方針部を引用])→R1保存→Family X既存R1→R2処理をそのまま呼び出し→R2保存→評価(決定論+LLM 1 call)→`summary.json`/`summary.md`。
- Dangling Reference Check: Grep `er036_|family_y_voice_structure` 全体。

## 実行コマンド全文

- `.venv\Scripts\python.exe er036_family_y_voice_structure_trial_01.py --source-dir "er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2" --level b1 --out-dir "er036_output/family_y_voice_structure_trial_01/ai_hiring_3v" --budget-jpy 40`(レベル・引数名は実装に合わせ、実行したコマンドを逐語記録。既存出力がA2のみならA2)
- 単体test(¥0、mock): `.venv\Scripts\python.exe -m pytest er036_family_y_voice_structure_trial_01_test_01.py -q`(前段JSONの構造検証[1 Voice=fact 1〜2件、全Voice同一fact集合の禁止]、Fact紹介型開始の検出器、R1→R2呼び出しがFamily X既存関数であることのassert)
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er036*_test_*.py"`

## SSOT追記文

RESULT_PACKETへ文案のみ: REPORT_LEDGER新行(FAMILY-Y-VOICE-STRUCTURE-TRIAL-01、Trial、Status案)、DECISION_LOG(Trial実施記録、ユーザー指示原文要旨、Status案、Production採用は未決)、OPEN_ITEMS(新発見問題があれば候補のみ)。CURRENT_SPECは変更しない(Trialのため)。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `er036_*`、`er036_output/family_y_voice_structure_trial_01/`(json/md)、REPORT、設計書、delegation_log+`_check.json`。他Agent差分・SSOTは一切addしない。SSOT編集権: なし。
- メッセージ: `FAMILY-Y-VOICE-STRUCTURE-TRIAL-01: Fact Selection/Voice Fact Assignment/Angle先決め+Family X既存R1→R2流用のVoice構造改善Trial(1記事、R1/R2比較)`、trailer `Management-ID: FAMILY-Y-VOICE-STRUCTURE-TRIAL-01`。`git push origin main`。

## 報告(RESULT_PACKET項目)

T-0結果/使用した記事・レベル/Family Xから流用した正式名称・仕組み(対応表)/Family Bから流用した既存Voice重複対策の有無/前段の割当結果(Voiceごとのfact_ids・stakeholder・angle)/R1全文path+要約/R2全文path+要約/R1→R2で何が変わったか(diff要約)/4課題それぞれの改善状況(Before→R1→R2、決定論指標+LLM評価)/8確認項目の結果表/新しく発見した問題/QCD上の懸念(cost実測・call数・所要時間・Production化時の追加call数)/Trial終了status案(REJECTED/VALIDATED/USER_DECISION_REQUIRED)と根拠/新仕様候補・追加改善案(実装せず列挙)/commit hash/raw URL。ユーザー向け表記はStandard/Advanced。
