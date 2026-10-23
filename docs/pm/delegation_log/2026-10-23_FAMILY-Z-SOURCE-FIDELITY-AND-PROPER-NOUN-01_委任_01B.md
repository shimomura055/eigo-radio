FABLE-DELEGATION-MARKER: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01-委任_01B-20261023

# 委任_01B: Family Z 固有名詞ルール改定(区分B、APPROVED_FOR_PRODUCTION)のSSOT反映・Writer Prompt調整案(Trial用)・2作品テキストTrial(区分C)

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01_委任_01B.md`(N≈325〜335、先頭行MARKER一致確認)。
2. ユーザー指示原文は並行の委任_01Aが `docs/pm/delegation_log/2026-10-23_FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01_USER.md` に保存する(本委任は保存しない。作業前にそのファイルの存在を確認し、無ければ§1要点で進め、DECISION_LOGには「原文所在=同path(01A保存)」と書く)。
3. ACTIVE_TASK.md: 別agent複数が並行中。編集直前に再読込し、「並行タスク: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_01B(固有名詞ルール反映+Trial)」の1行追加のみ。有料生成の直前・直後に同行へ「有料run進行中/終了(時刻)」。
4. 並行する委任_01A(結末欠落の原因調査・設計)とは成果物を分ける。本委任のSSOT範囲: CURRENT_SPEC(Family Z固有名詞方針の節)、DECISION_LOG(ユーザー決定B)、OPEN_ITEMS(固有名詞ルール改定+Trialの新item 1行)、USER_DECISION_REGISTER、REPORT_LEDGER。

## 1. ユーザー決定(逐語・区分B、APPROVED_FOR_PRODUCTION[仕様決定]、Family Zのみ)
> 固有名を使うのは基本的に主人公のみとする。ただし、それ以外に物語の中心人物、展開・結末の理解に重要な人物については、主人公・脇役の区別によらず原作の名前を維持する。

運用上の留意点(原文§5): 主人公のみの原則は維持/名前を残す例外は物語上の重要性が明確な人物に限定/重要性が低い人物は役割名・関係性/First name/Last nameの一方のみという既存方針は維持/固有名詞を増やすこと自体を目的としない/登場回数の多さだけで重要人物と判断しない/物語の重要性をAIが適切に判断できるようWriter Promptを調整/既存の名前検査Gateを無条件に復活させない。
Trial条件(原文§6): 『開いた窓』目標=FramtonとVeraのみ(まず共通ルールのみでVeraが残るか確認。残らなければ理由分析→共通Promptの改善余地評価→作品個別指定でFramton・Veraのみ)/『走れメロス』目標=Melosのみ(他は役割名・関係性。人物関係・因果が理解できなくなる省略・置換は避ける)/Std・Adv双方/過剰使用が生じないこと/新ルール適用結果と作品個別調整の結果を区別/作品固有の名前を共通Promptに埋め込まない/本文以外の工程・Voice設定への影響確認/音声再生成・Production成果物差替え禁止/既存成果の最大再利用・最小費用。
Status管理(原文§9): 改定はAPPROVED_FOR_PRODUCTION(未配線段階ではPRODUCTION_WIREDを宣言しない)。Trial結果を待たずに未検証Prompt案をProductionに採用しない。

## 2. 作業
### B-1. SSOT反映(APPROVED_FOR_PRODUCTION)
- CURRENT_SPEC: Family Zの固有名詞方針の現行記述(「主人公のみ」「First/Last一方のみ」等、Grepで特定: 「固有名」「主人公」「Family Z」「人物名」)を、上記ユーザー決定の逐語で改定(旧記述は履歴として残す)。Status=`APPROVED_FOR_PRODUCTION(2026-10-23、未配線)`。
- DECISION_LOG 1件(原文所在、決定内容、未配線である旨)。OPEN_ITEMS新item(Status=`APPROVED_FOR_PRODUCTION_TRIAL_IN_PROGRESS`)。UDR(判断済み)。REPORT_LEDGER。→ ここで一度commit/push。

### B-2. Writer Prompt調整案(Trial用、Productionは変更しない)
- 現行Z Writer Prompt(R0/R1/R2/std_adjust、`er026_*`/`er062_*`/`er003_v1_translator_briefs/`等をGrep)の固有名詞指示箇所を特定し、**共通ルール文**(作品固有名を含まない。「主人公のみ+物語の中心人物・展開・結末の理解に重要な人物は原作名維持、重要性が低い人物は役割名・関係性、First/Last一方のみ、登場回数で判断しない」)への差替え案を作る。
- Trial実行はProduction Prompt fileを書き換えず、**DEV用のPrompt override**(runnerの既存override機構があればそれを使う。無ければTrial dir側にPromptコピー+環境変数/引数で差替えるDEV専用scriptを書き、Productionからの参照0をGrepで確認)で行う。
- 作品個別指定が必要になった場合のための「作品個別メモ」(story配置の設定、例: `STORY_PROPER_NOUN_KEEP={"the_open_window": ["Framton","Vera"]}`相当)の設計も用意(Trialでは共通ルールのみが失敗した場合にだけ使用)。

### C. 2作品テキストTrial(費用あり・本文のみ・音声なし)
- 事前見積: run_e2e_01のcost_log(writer+std_adjust≈17.76円/作品)を出典に、2作品×(共通ルール1回)=約36円、作品個別調整が必要な場合+約18円/作品。**合計上限100円**。超過見込みならSTOP報告。本日累計(約80円)+本Trialが1,000円内であることを確認。
- 実行: Trial専用run dir(例 `er026_output/family_z_production_e2e_01/<story>/run_pntrial_01`)で、Z runnerのwriter→std_adjust段のみ(seed/原作は既存成果を再利用、音声段は実行しない)。`TTS_EXECUTION_MODE=STANDARD`は無関係だがSTOPセンチネル確認(rc=0)、別agentの有料run(ACTIVE_TASKの各行・`Get-Process python`)と重ならないよう確認。メロスは受入済み公開版の元run(`run_e2e_06`)の原作/seedを再利用。
- 評価(各作品×Std/Adv): 固有名詞の出現一覧(名前・回数・初出箇所)、目標との一致(開いた窓=Framton・Veraのみ/メロス=Melosのみ)、不要な名前の増加有無、役割名・関係性表現の自然さ(人物関係・因果が理解できるか)、語数・構造の既存WARN/Gate結果。**開いた窓では、原作のオチ(Veraが即興の作り話を得意とする種明かし)が本文に含まれるかも観察し記録**(本Trialの目的外だが01Aの参考データ。含めるためのPrompt変更は行わない=未承認)。
- 共通ルールのみで目標未達の場合: 理由分析(Promptのどの指示が効かなかったか)→共通Promptの改善余地を評価(改善案は記録のみ、再Trialは1回まで・上限内)→作品個別指定で再生成(1回)。共通ルール結果と個別調整結果を分けて記録。
- 本文以外への影響確認: speaker roster/Voice割当(`STORY_VOICE_ROSTER`)・plan段の話者判定・KP選定・Preview/Commentへの影響を静的に確認(名前の有無でroster keyが変わらないか等)。音声は生成しない。

### 証跡・SSOT・Git
- `docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/PROPER_NOUN_TRIAL_01.md`(Prompt差分、run dir、固有名詞一覧表、目標達成、個別調整の有無、費用出典、影響確認、Production無変更の証拠)。
- OPEN item Statusを`TRIAL_COMPLETE_*`へ更新(共通ルールのみで達成/個別調整で達成/未達を明記)。REPORT_LEDGER。commitは明示add(本文Trial成果物のうちtext/json/mdのみ)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 3. 禁止
- Production Prompt/コード/音声/成果物/公開ページの変更、音声再生成、作品固有名の共通Promptへの埋め込み、名前検査Gateの復活、未承認のオチ補完Promptの追加、上限超過、別agentの有料runとの並走。

## 4. 報告(docs/pm/RESULT_PACKET_FZSF1B.md、同内容を最終報告で)
(1)SSOT反映結果(CURRENT_SPEC改定箇所・Status) (2)共通ルールPrompt案(差分要約)とoverride方式 (3)Trial結果表(作品×レベル×固有名詞一覧・目標達成・不要増加) (4)共通ルールのみ/個別調整の区別と分析 (5)開いた窓のオチの有無(観察) (6)本文以外への影響 (7)費用(出典) (8)Production無変更の証拠、commit・raw URL + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。