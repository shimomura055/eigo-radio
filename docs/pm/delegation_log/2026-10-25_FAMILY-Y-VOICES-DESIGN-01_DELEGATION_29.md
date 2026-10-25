FAMILY-Y-VOICES-DESIGN-01 委任_29: Family Y Closing生成方式の一般化Trial(テーマ+3 Voiceだけを入力し、AIが自ら切り口を発見してTension+Closingを書く共通方式。DEV/Trial専用、Production配線禁止、到達上限VALIDATED)

## ユーザー指示(2026-10-25、逐語はStep 0で保存)— 要点
- 目的: 記事ごとの人手による切り口設計なしで自律生成できる方式。案A/B/Cは「切り口をClaudeが詳細設計してから渡した」ためProduction量産工程として不適切。**目標=テーマと3人のVoiceを入力するだけで、AIが独自に新しい視点を発見し、学習ラジオにふさわしいClosingを生成**。
- 入力: 記事のテーマ・論点/3人のPersona情報/3人のVoice本文/既存Research・Fact等の共通情報。**特定テーマ専用の切り口や結論を人間が補足しない**。
- 生成AIに求める判断: (1)3人の発言に隠れた共通点・相違点・矛盾・意外性 (2)並べただけでは気づきにくい新しい見方 (3)その見方でテーマをどう深められるか (4)聞き手が自分の経験に引きつけて考えられる具体的な問い → 最も面白く考える価値のある切り口を選びTension+Closingを書く。
- 品質原則: 3人の意見を順に要約して終わらない/「人によって意見が違う」で終わらない/勝敗を決めない/Voiceと矛盾しない/新しい事実・制度を創作しない/説教・道徳的一般論・美辞麗句を避ける/ラジオで一度聞いて理解できる/最後は聞き手の思考を促す具体的な問い/既存Closingの分量・構成バランス維持(約200字)。
- 案A/B/Cの位置づけ: 良いClosingに必要な思考の**具体例**(A=日常的な言葉・前提を問い直す、B=解決策が何を変えられて何を変えられないか、C=対立の奥の共通点や歩み寄りの限界)として参考にするが、**3パターンから選ぶ仕組みにしない**。出力を制約する分類ではない。**今回の記事専用の表現・人物設定・論点を一般化Promptに埋め込まない**。
- Trial設計: ①『宅配の再配達』で、同じ日本語Voice本文を入力し切り口を事前指定せずに生成、既存案A/B/Cと品質比較(新しい視点・Voice踏まえ・要約でない・考えを深める・自然で面白い。異なる切り口でも品質が高ければ積極評価) ②『SNSの年齢制限』(既存テーマ)でも**同じPrompt・同じ工程**で生成(テーマ情報とVoiceの差替えのみ。記事ごとのPrompt修正・切り口手動設計禁止)。2テーマは並列実行可 ③Fable独立評価(両テーマで新視点発見/特定論点・パターンへの偏りなし/Voiceから自然に導かれる/日本語として分かりやすく面白い/手動設計なしで再現)。同じPromptからの結果の安定性も費用対効果の範囲で確認。**生成Closing全文を必ず掲載**。
- 既存仕様との整合: Y合意構成(Lead/V1/V2/V3/Tension+Closing)、人物紹介・AI編集アナウンス音声廃止・In One Line廃止は維持。変更対象はTension+Closingの生成方式のみ。既存Leakage Gate、特に `leak_tension_reverts_to_research` が新しい論点を不適切にFAILにする可能性→既存の承認意図を確認し、必要なら変更候補として報告。Trial中の調整はDEV内、Production仕様を無断変更しない。
- QCD: 既存3案・Voice本文・Research再利用/独立作業並列/記事全文再生成・英訳・音声化しない/**既存承認予算枠で実施可能な範囲を確認し、範囲外の有料API実行は事前承認**/失敗時は原因分析と効果の見込みある改善検討(新仕様・範囲の無断追加禁止)。
- 報告: A.一般化Prompt(全文/入力データ種類/切り口発見・選定の仕組み/記事固有指示の混入なしの確認) B.結果表(評価項目×[宅配の再配達|SNSの年齢制限]: AIが発見した切り口/Closing全文/3人のVoiceとの整合/新しい発見・面白さ/聞きやすさ/Fable評価) C.QCD(生成コストと量産単価見込み/実行時間/失敗時再生成の必要性/既存方式との品質比較) D.Status(VALIDATED/REJECTED/UDR)/未解決/共通方式としての採用可否のFable推奨。
- STOP: 人間が記事固有の切り口を決めなければ品質が成立しない場合は方式の課題として報告(手動設計で成功扱いにしない)/重大品質問題・範囲外仕様変更・予算超過見込み/正式採用前の配線禁止。**成功条件=テーマが変わっても3人のVoiceからAI自身が魅力的なTension+Closingを生成できること。**

## 既存資産(先に読む)
`docs/research/FAMILY-Y-VOICES-DESIGN-01/REDELIVERY_REVISION_01/{REVISION_SCRIPT_01,DESIGN_01,EVAL_01,BUDGET_LOG_01}.md`、`er110_family_y_redelivery_revision_01.py`(切り口パラメータ付きPrompt・Closing生成・Gate呼出・書き換えPromptの実装)、`er110_output/family_y_redelivery_audio_01/revision_01/`(案A/B/C、closing_A_v1、gate結果)、THEME_DATA_02.json/THEME_DEFINITION_02、`er110_family_y_persona_text_trial_01.py`/`er110_family_y_text_trial_01.py`(Leakage Gate判定器・`leak_tension_reverts_to_research`の定義と承認意図=OPINION_BASED_01配下の設計・Opusレビュー・ユーザー承認記録をGrep)、『SNSの年齢制限』の既存テーマデータ・Persona・Voice本文(`docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_01/`配下、`er110_output/`配下をGlob/Grepで特定。見つからなければ報告)。

## 予算(Fable指示)
- Phase 0(設計・Prompt・Gate確認・費用見積)はAPI 0。
- 着手時に `BUDGET_LOG`(REDELIVERY_REVISION_01/BUDGET_LOG_01.md、OPINION_BASED_01/BUDGET_LOG_OB_02.md等)で、FAMILY-Y-VOICES-DESIGN-01の**現在有効な承認枠と残額**を確認し報告に書く(委任_28の枠40円は31.65円消費→残約8.35円)。
- 想定: 生成=gpt-6.1-sol(最新世代最上位系、委任_28と同一)、1生成≈3〜6円(効果effort=highの実績から見積)、Gate判定=gpt-6-luna 約0.1〜0.5円/回。計画=2テーマ×2生成(安定性確認の最小)=4生成+Gate ≈ 15〜25円。
- **残額内で収まる部分のみ有料実行可**。収まらない場合は **Phase 0完了後に有料実行前でSTOP**し、費用見積(テーマ別・call別・安定性確認の有無で2案)を報告(Fableがユーザーへ承認を求める)。Phase 0の成果物(Prompt全文・設計・Gate分析・見積)はその時点でcommit/pushして報告。

## 実施
Step 0: ユーザー指示原文を逐語保存。jsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl` role=user、冒頭「# Claude Codeへの指示｜Family Y Closing生成方式の一般化Trial」→ `docs/pm/delegation_log/2026-10-25_FAMILY-Y-VOICES-DESIGN-01_USER_11.md`(`py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <path> --role user --index N --out ...`。user抽出非対応なら`py`で直接走査しtextを無変更で書き出す)。
Phase 0(API 0、`docs/research/FAMILY-Y-VOICES-DESIGN-01/CLOSING_GENERAL_01/`配下):
 - `EXISTING_SPEC_CHECK_01.md`: Y構成・Closing分量・Leakage Gate各項目(特に`leak_tension_reverts_to_research`の判定文・承認意図・委任_28での誤FAIL事例)・THEME_DATAの構造・SNS年齢制限テーマの入力データ所在。
 - `DESIGN_01.md`+Prompt全文(`prompt_closing_general_01.txt`として別ファイル保存、sha256記録): 入力=テーマ・論点+Persona 3+Voice本文3+共通Research/Fact(あれば)。AIに(1)〜(4)の分析を**構造化出力(分析→候補切り口複数→選定理由→Closing本文)**で行わせ、最終的にClosing本文のみを採用する設計を基本とする(分析過程は評価・監査用に保存)。品質原則を一般的な禁止・要求として記述。案A/B/Cは「思考の例」として**抽象化した形でのみ**(宅配固有の語・人物・論点を含めない)例示するか、例示なしで行くかを設計判断し理由を書く。**記事固有語の混入検査**(宅配・再配達・不在票・ロッカー・ドライバー・SNS・年齢等のテーマ語がPrompt本文に含まれないことをtestで固定)。
 - 安定性・比較の計画: 各テーマ2生成(温度等は既存と同一)。Gate: 既存Leakage Gateを**DEVで実行し結果を記録**(FAILでも本文を書き換えて切り口を失わせない。FAIL理由を分析し、Gate側の課題か本文の課題かを分類)。
 - `OPUS_REVIEW_REQUEST_01.md`: Fableが別途Opusレビューに回す論点(Promptの一般性・切り口発見の仕組み・偏りリスク・Gate整合)を1ページに。
 - `BUDGET_PLAN_01.md`: 残枠確認結果と見積(2案)。
 - ここまでをcommit/push(下記Git)し、**残枠不足ならここでSTOPして報告**。
Phase 1(残枠内の場合のみ): DEV module `er110_family_y_closing_general_trial_01.py`(+test: Prompt sha固定・記事固有語0・入力隔離・予約方式費用guard・`--paid`+BUDGET_APPROVED.json無しで副作用0)。2テーマ並列(同一Prompt、入力差替えのみ)×2生成。Gate実行・記録。出力=`er110_output/family_y_closing_general_01/<theme>/gen_{1,2}/`(分析JSON・Closing本文・Gate結果・cost)。
Phase 2: `EVAL_01.md`(Sonnet所見: 両テーマの切り口・Voice整合・要約でないか・問いの具体性・聞きやすさ・案A/B/Cとの比較・安定性・Gate結果の分類)、`TRIAL_RESULT_01.md`(**ユーザー閲覧用**: A.Prompt全文/入力種類/仕組み/固有語混入なし確認、B.評価表[評価項目×2テーマ、Closing全文を表内または直下に全文掲載、Fable評価欄は空欄]、C.QCD、D.Status候補・未解決・推奨)、`BUDGET_LOG_01.md`。
SSOT: `OPEN_ITEMS.md` OPEN-463(またはY関連の該当OPEN)に1行追記のみ(**最後に直前再Read・最小Edit**。並行agentが編集中)。CURRENT_SPEC/DECISION_LOGは変更しない。`docs/pm/ACTIVE_TASK.md`更新(gitignore)。
委任文逐語: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <同jsonl> --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Y-VOICES-DESIGN-01_DELEGATION_29.md`(N=562前後±8、冒頭「FAMILY-Y-VOICES-DESIGN-01 委任_29」で照合。`--index -1`不可)。
Git: 作業ブランチ`work/post-merge-01`(origin/mainとmerge済み)。並行agent2つ稼働中。`git add -A/-u/-f`、amend/rebase/force push/stash/clean/reset/checkout -f/`git checkout -- <file>`禁止。自分の新規ファイル+OPEN_ITEMS 1行のみ対象pathでcommit(`git commit --only -- <paths>`)。pushがnon-fast-forwardなら `git fetch`→`git merge --no-edit origin/main`(競合は両方残す)→push。secret grep 0件。有料runは`.venv\Scripts\python.exe`、無料処理は`py`。

## 報告(`docs/pm/RESULT_PACKET_FYT29.md`+返答)
Phase 0でSTOPした場合: 残枠・見積2案・Prompt全文の所在・Gate分析の要点。完了した場合: 上記A〜Dを返答にも要約(Closing全文は返答に必ず転記)、実費(call別)、commit hash・raw URL(特に`TRIAL_RESULT_01.md`)、RESULT_PACKET 4行(既存仕様整合/未承認機能の既定値/失敗終了時の成果物/撤去・残置)。判断を要する点は推測で進めず報告で止める。