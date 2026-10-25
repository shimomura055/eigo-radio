FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_18: 英語学習解説 Part 2(Grammar & Sentence Structure)「倒置優先順位変更」Trial-08(DEV/Trial専用。Production採用・配線禁止。Production file変更禁止)

## ユーザー指示(2026-10-25、逐語はStep 0で保存)— 要点
目的: Trial-07で8作品中4作品が倒置(INV)になった偏りを改善。**倒置の優先順位を下げ、倒置以外に学習価値の高い構文がない場合に倒置を選ぶ方式**を検証。目的は文法種類の機械的な増加ではなく「学習者にとって最も解説する価値のある英文を選ぶ」こと。
選定優先順位(ユーザー承認済みTrial仕様): 第1優先=倒置以外の学習価値が高い構文(複雑な修飾関係/長い主語・節構造/分詞構文・付帯状況/比較・強調構文/その他、読解時に構造の取り違えが起きやすく解説価値のある文。例示であり分類を限定しない) → 第2優先=学習価値のある倒置(倒置以外に十分な候補がなければ選んでよい。単純な倒置で価値が低ければ無理に選ばない) → 第3=0件。
維持する既存仕様: 最大1件/価値がなければ0件/`Before A, B`等の基本構文を文頭にあるだけで選ばない/本文に存在する英文のみ/引用の不正連結・改変防止/件数合わせ・多様性確保のために価値のない文を選ばない。**倒置を一律除外しない**。
対象: Trial-07と同じ8作品(開いた窓/イグ・ノーベル賞2026/賢者の贈り物/猿の手/告げ口心臓/二十年後/退屈と攻撃性/走れメロス)、**Trial-07で使った本文を再利用**(告げ口心臓もTrial-07本文。Production最新版への適用確認は別扱い)。
Step A: 既存Trial-07選定処理を基盤に、候補抽出・学習価値判定の既存機構は維持し、倒置の順位のみ下げる。まず既存Trial-07データの再評価で検証できる範囲を確認。**既存データに候補の欠落がある場合は必要な範囲で再選定**。新旧の差のうち優先順位変更以外の要因による差を区別。
Step B: 選定結果の比較が主目的(新しい解説全文の生成は必須範囲外)。各作品: 何が選ばれたか/なぜ/Trial-07との違い/倒置以外を選んだ場合に学べる文法/倒置が残った場合に他に十分な候補がなかったか/0件の妥当性。旧倒置4作品(開いた窓・賢者の贈り物・猿の手・告げ口心臓)は重点確認。
評価基準(事前固定、6点): 1.倒置以外の適格候補を適切に優先できたか 2.学習価値の低い文を無理に選んでいないか 3.倒置を残すべき作品で適切に残せたか 4.解説価値のある文の見落としがないか 5.最大1件・0件許容 6.引用の逐語一致。過去Trialの事前登録結果を書き換えない。
QCD: 不要な追加Trial・Prompt改善反復禁止。既存データ再利用と並列化で最短。有料API実行は承認済み予算枠内(下記)。Status=VALIDATED/REJECTED/USER_DECISION_REQUIRED。
報告必須: 8作品の新旧比較表(作品/Trial-07選定/今回の選定/学習できる文法/評価)+各作品の新選定英文全文・日本語訳・選定理由+倒置→別構文へ変わった作品の学習価値改善の具体説明。長い場合は閲覧用1ファイル。最後にFable独立評価(欄を空けておく)/品質の改善・悪化/実費と量産単価影響/Status/正式採用に向け必要なユーザー判断。

## 既存資産(必ず先に読む)
`docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/{DESIGN_07,PREREGISTERED_CRITERIA_07,EVAL_07,EVAL_07B,COMPARISON_07,ADOPTION_NOTE_07,PART2_TRIAL07_RESULTS_01,BUDGET_LOG_01}.md`、`run_trial_07.py`/`analyze_07.py`/`test_trial_07.py`/`posthoc_07.py`、`OUTPUT_07_*`(候補一覧・クラス・teaching_value・resolve7/verify_single_span結果)。Trial-07の選定=決定論(強クラスINV/CLEFT/CMP優先、最大1件、`teaching_value`、FRONT細分類、ELL限定)。

## 予算(Fable確認済み・指示)
- 案件累計上限50円(BUDGET_LOG_01.md:110)。Trial-07累計6.5366円(上限12円)。本委任のAPI上限=**12円**(案件累計50円内で収まることを着手時にBUDGET_LOGで確認。超える見込みなら有料実行前にSTOPして見積を報告)。
- API 0で済む作業(既存候補データの再ランキング、既存03d訳・Trial-07訳の再利用)を最優先。有料は(a)候補欠落の再抽出(Trial-07と同一モデル・同一Prompt、優先順位の指示だけ差替え=比較条件の同一性。最新モデル原則との関係を報告に明記)、(b)新選定文の日本語訳(既存訳が無い文のみ。T1 module `er003_kp_source_sentence_ja_01.py` の関数を読み取り利用、約0.03円/文、またはTrial-07と同じ訳工程)。費用guardは予約方式(Trial-06/07と同じ)。

## 実施
Step 0: ユーザー指示原文を逐語保存。jsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl` の role=user、冒頭「# Claude Codeへの指示｜英語学習解説 Part 2 倒置優先順位変更Trial」→ `docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_08.md`(`py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <path> --role user --index N --out ...`。user抽出に非対応なら`py`で直接走査しtextを無変更で書き出す)。
Step 1(API 0): `DESIGN_08.md`(優先順位の実装: Tier1=INV以外の適格候補[teaching_value閾値はTrial-07と同一]、Tier2=INV適格、Tier3=0件。Tier内の順位はTrial-07の既存ルールを維持。「倒置一律除外ではない」ことをコードで表現)と `PREREGISTERED_CRITERIA_08.md`(上記6基準+各作品の「許容集合」はTrial-07の事前登録を書き換えず、新たに今回用を定義。Trial-07の候補データから作る場合はその旨)。実行前にcommit。
Step 2(API 0優先): `run_trial_08.py`/`analyze_08.py`/`test_trial_08.py`。Trial-07の候補データ(全候補・クラス・teaching_value)に新順位を適用し8作品を再選定。**候補欠落の判定**: Trial-07抽出Promptが強クラス優先で候補を絞っていた/候補数上限があった等、非INV候補が欠落し得る根拠を調べ、作品ごとに「既存データで検証可/再抽出要」を判定。再抽出が必要な作品のみ再抽出(予算条件内)。resolve7+verify_single_span(逐語一致・単一段落内)を必ず通す。
Step 3: 新選定文の日本語訳(既存訳があれば再利用、無ければ上記(b))。
Step 4: `EVAL_08.md`(6基準の判定・作品別)、`COMPARISON_08.md`(新旧差の要因分解: 優先順位変更による差/候補再抽出による差/その他)、`PART2_TRIAL08_RESULTS_01.md`(**ユーザー閲覧用**: 冒頭に必須の比較表[作品/Trial-07選定/今回の選定/学習できる文法/評価]、各作品節=新選定英文全文・日本語訳・選定理由・Trial-07との違い・学べる文法・倒置が残った場合の他候補の有無・0件の妥当性、旧倒置4作品は重点、Fable独立評価欄は空欄、品質の改善/悪化、実費と量産単価影響、Status候補、正式採用に向け必要なユーザー判断候補)、`ADOPTION_NOTE_08.md`、`BUDGET_LOG_01.md`追記。
Step 5: SSOT=`OPEN_ITEMS.md` OPEN-497(Part 2)に1行追記のみ(Trial-08実施・Status候補・証跡パス。11-8分類付き。**最後に直前再Read・最小Edit**。並行agentがOPEN_ITEMSを編集中)。CURRENT_SPEC/DECISION_LOGは変更しない(Trial段階)。`docs/pm/ACTIVE_TASK.md`更新(gitignore)。
Step 6: 委任文逐語 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <同jsonl> --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_18.md`(N=561前後±8、冒頭「FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_18」で照合。`--index -1`不可)。
Step 7 Git: 作業ブランチ`work/post-merge-01`(origin/mainとmerge済みHEAD `658256c6b`以降)。並行agent2つが稼働中。`git add -A/-u/-f`、amend/rebase/force push/stash/clean/reset/checkout -f/`git checkout -- <file>`禁止。自分の新規ファイル+OPEN_ITEMSの1行のみ対象pathでcommit(`git commit --only -- <paths>`)。`git push origin HEAD:main`がnon-fast-forwardなら `git fetch`→`git merge --no-edit origin/main`(競合は両方残して解消、他案件の成果を破棄しない)→push。secret grep 0件。

## 報告(`docs/pm/RESULT_PACKET_FZST18.md`+返答)
- 残枠確認結果、実費(call別)、再抽出した作品と理由。
- 8作品比較表(返答にも転記)、作品別の新選定英文全文・訳・理由(返答では要点、全文はRESULTS_01へ)。
- 6基準の判定、新旧差の要因分解。
- Status候補とユーザー判断候補。
- 変更ファイル・commit hash・raw URL(特に `PART2_TRIAL08_RESULTS_01.md`)。
- RESULT_PACKET 4行(既存仕様整合/未承認機能の既定値/失敗終了時の成果物/撤去・残置)。
判断を要する点(予算超過見込み・仕様の曖昧さ)は推測で進めず報告で止める。