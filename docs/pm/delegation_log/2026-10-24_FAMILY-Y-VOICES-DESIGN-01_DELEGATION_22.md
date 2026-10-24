FAMILY-Y-VOICES-DESIGN-01 委任_22(Fableから): 改善R0(run_02a/02b)のFable評価を記録し、残存問題「世界設定の定義がV1の語りへ混入」を是正した1 runを実施し、予算事故の記録・SSOT更新・commit/pushまで行う。

## 0. 前提(読む範囲を絞ること)
- 直前の委任_21成果: `docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_01/{EVAL_SET_02.md,PROVENANCE_02a.md,PROVENANCE_02b.md,BUDGET_LOG_OB_02.md,PROMPT_DIFF_03.md,THEME_DEFINITION_01.md,PERSONAS_04.md}`、code `er110_family_y_opinion_based_02.py`(+test)、出力 `er110_output/family_y_opinion_based_02/sns_age_limit/{run_02a,run_02b}/`。commit 52f872a19。
- ユーザー指示原文: `docs/pm/delegation_log/2026-10-24_FAMILY-Y-VOICES-DESIGN-01_USER_07.md`(§4 自己ループ、§5 予算、§6 報告8項目)と `2026-10-24_PM-FAMILY-Y-BUDGET-CONSOLIDATION-01_USER.md`(Family Y累計上限撤廃・日次1,000円JST一元管理・追加承認なく日次1,000円を超過しない)。
- 10-24日次累計は約390円(BUDGET_LOG_OB_02 §3)。他案件(KP 委任_30、ASR 委任_05)が並行中。本委任の有料支出は下記§2の1 runのみ(上限25円)。**日次1,000円を超える見込みが出たら実行せず報告**。
- 禁止: `git add -A/-u/-f/-N`、amend/rebase/force push/stash/clean/reset --hard/checkout -f。commit前に`git status`でindexを確認し、他agentがstageしたファイルを巻き込まない(`git commit --only -- <paths>`)。wav/raw_usage_log/STOP/sources・`ACTIVE_TASK.md`/`RESULT_PACKET.md`は追跡しない。telemetry等の追跡ファイルが自動書換えされても復元・stageしない(OPEN-490)。`.venv\Scripts\python.exe`を使う。有料runの起動は本委任文に明示した回数(1回)のみ。secret grep 0件。

## 1. Fable評価の記録(0円) → `OPINION_BASED_01/FABLE_EVAL_02.md`を新規作成。以下を逐語で記録し、EVAL_SET_02.mdのFable判定欄にも転記する。
(A) V1新旧盲検(BLIND_KEY_02.jsonを開く前に記入した判定): 甲=葛藤あり(「正直助かる」+結び「すぐには言えない自分もいる」)・冗長でない・最良 / 乙=葛藤が4回反復し冗長(「正直、助かっている」「しんどい時がある」「いや、私の都合では」)・最下位 / 丙=葛藤あり・冗長でない・ただし第6文「アカウントを持たせないことと、使える機能を決めることは、分けて考えたい」が制度設計の口調で人物像からやや浮く。順位 甲>丙>乙。Key開封後: 甲=run_02a、乙=旧R0、丙=run_02b → 新旧比較は新が明確に優位(盲検で一致)。
(B) V2(高校生) 02a/02b: テーマ一言テスト=「アカウント禁止には反対。使いながら安全にする方式を望む」で言える/制度解説文なし/葛藤1か所(自分で考えたい↔悪口・脅しの時は大人に頼りたい)を「そこは、うまく言えない」で受ける流れが自然/監視文0で中心テーマ内。02aの「僕が考えるところまで取り上げられた気がする」は人物の声として良い。判定: 両run PASS。
(B) V3(中学生の子の親) 02a/02b: 一言テスト=「年齢一律でなく、子の力に合わせて段階的に広げたい」で言える/制度解説なし/「べき」0/葛藤なし(許容。USER_07④は葛藤を残す趣旨で全Voiceに葛藤を要求しない)。泳ぐ練習のたとえは出典THREE_d由来で自然。02bは同じたとえが第4文と第8文の2回で軽い反復(repetition_report 0だが目視で重複)、02aは1回。判定: 両run PASS、02aがやや上。
(C) 冒頭型・結び型: 02a/02bとも3種が分かれている(旧R0は結び2種)。PASS。
(D) 出典: 出来事・人物・会話の捏造0。要注意自己告白(02a V1第9文「守りたいから賛成、とすぐには言えない自分もいる」)はTBS-07「助かる」から自然に導かれる迷いの表現でありFableは感情の補いの範囲(捏造でない)と判定。**残存問題(系統的・2/2 run)**: 世界設定の「段階的な制限」「アカウント禁止と機能制限の区別」の定義語がV1の意見として混入(02a V1第7文「成長に合わせて広げる形なら、と思う」、02b V1第6文)。V1経験欄に根拠がなく、V3の主張との重なりを人工的に作っている。USER_07⑤の部分重なり許容には当たるが、出典忠実性の点で出典対応表に載らない意見が残るため是正対象。
(E) USER_07 §4 確認8項目: 1中心テーマ=PASS(V2監視文3→0) / 2 Persona適合=PASS / 3主観性=PASS / 4葛藤=PASS(V1 1か所+結び、V2 1か所) / 5冗長=PASS(反復ペア0。02b V3のたとえ2回は軽微) / 6別人物=PASS / 7忠実性=捏造0、ただし定義混入1文/run(上記D) / 8費用=旧20.2円→02a 20.6円・02b 19.8円、時間199→234/202秒、過度な増加なし。
(F) 総合: 02a>02b>旧R0。改善方針①〜⑤は達成。Fable判定Status(本委任のrun_03の結果で確定): 定義混入が解消されれば **VALIDATED(限定: 1テーマ・同一題材での複数run、Production採用はユーザー判断、OPEN-484の正式経路未整備)**、解消しなければ VALIDATED_LIMITED(残存=定義混入、開示済み)。
(G) 予算事故(委任_21、testの承認ファイル読込バグで実runを2回誤起動、約50.6円、承認45円→実績約91.1円): Fable判断=事故費用として記録・追認(日次1,000円の範囲内、承認枠45円は拡大しない、Scope変更なし)。再発防止はtest側のAPI隔離(`read_cap(path=None)`)に加え、§3の起動ガードを追加する。

## 2. 残存問題の是正Trial(自己ループ、有料run 1回のみ、上限25円)
- 原因: 世界設定(THEME_DEFINITION/世界設定ブロック)の定義文が全Voiceの生成Promptへそのまま渡され、V1がそれを自分の意見として語る。
- 是正方針(Prompt/Sheet側、人物固有のハードコード禁止): 世界設定の定義はVoiceごとの関連欄(その人物の経験欄・主張に対応する範囲)に絞って渡す、または「世界設定の用語は語りの前提として使ってよいが、経験欄に根拠のない意見として語らない」をTHINK_BLOCKに明記する。どちらを採るか(併用可)は`PROMPT_DIFF_04.md`に差分と理由を記録。他Voiceの品質を落とさないこと(V2監視文0、V3の泳ぐたとえ等は維持)。02b V3のたとえ2回については「同じたとえを繰り返さない」程度の一般指示のみ可(回数制限の機械化はしない)。
- 実行: `BUDGET_APPROVED.json`をrun_03用に更新(合計上限25円・1run)、run_03を1回生成。出典照合(luna付番→機械照合→UNMAPPED再生成各Voice1回まで→agent目視)、`PROVENANCE_03.md`、`EVAL_SET_03.md`(EVAL_SET_02と同じ表構成で02a/02b/03を並べる。Fable判定欄は空欄で返す)、`BUDGET_LOG_OB_03.md`(本委任の全支出、台帳はstdout控えも残す)。
- 合格基準(Fableが最終判定するが、agentの事前判定を書く): 定義由来の出典外意見0、捏造0、反復ペア0、V2監視文0、3 Voiceの冒頭/結び型が分かれる、各Voiceの一言テストが言える。

## 3. 起動ガード(0円、安全)
- 実API runは `BUDGET_APPROVED.json` の存在に加え、CLI明示flag(例 `--paid`)または環境変数の明示が必要にする。testからはどちらも与えないことをtestで固定(network/API呼出が起きないことをmonkeypatchで検証)。既存test 20件+追加testをPASSさせる。
- OPEN-493(Y runnerが`er011_output`へ書く)も本委任で修正する: 出力先を`er110_output/`配下に閉じ、testで固定。修正後OPEN-493をCLOSED(FIXED)に更新。

## 4. SSOT・記録(編集前に該当行を再読。他agentと並行のため最小差分)
- `OPEN_ITEMS.md` OPEN-463(Family Y)に委任_22の結果(Fable評価、run_03結果、Status)を追記。OPEN-493更新。
- `DECISION_LOG.md` に(1)Fable評価とStatus判定、(2)予算事故のFable追認(事故費用約50.6円、再発防止=test隔離+起動ガード)を記録。
- `docs/pm/USER_DECISION_REGISTER_01.md` #176: 予算部分は解消済みのまま、Scope選択肢(旧題材再現/6段階iteration)は未回答で維持。新しい判断事項はStatusとして本報告で提示する旨を追記(新規UDR番号は作らない)。
- `CURRENT_SPEC.md` のFamily Y Status行があれば Trial Statusのみ更新(Production仕様には書かない)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FAMILY-Y-VOICES-DESIGN-01_DELEGATION_22.md`(Nは本委任文の先頭「FAMILY-Y-VOICES-DESIGN-01 委任_22」を含むAgent呼出の0始まり通番。jsonlを検索して特定し、保存内容の先頭行が一致することを確認)。
- commit(`--only`で本委任の変更ファイルのみ、index確認後)→`git push origin HEAD:main`。commit messageは「FAMILY-Y-VOICES-DESIGN-01 委任_22: …」。

## 5. RESULT_PACKET.md に書く報告(簡潔)
run_03のR0全文、定義混入の有無(文を引用)、PROVENANCE_03の要注意/偽陽性/捏造件数、EVAL_SET_03の機械指標、費用(run_03実績・本委任合計・10-24日次累計)、起動ガードとOPEN-493の修正内容とtest結果、SSOT更新箇所、commit hash、raw URL一覧、Fable判定が必要な点。