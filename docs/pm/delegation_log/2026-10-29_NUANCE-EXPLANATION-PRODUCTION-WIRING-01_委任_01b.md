Fableからの委任_01b(管理ID: NUANCE-EXPLANATION-PRODUCTION-WIRING-01。ニュアンス解説Promptの品質Trial。Offline・Production変更なし・費用上限¥10)。本プロンプト全文を `docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_委任_01b.md` に逐語保存してから開始。`tools/stop_scope_check_01.py --managed-id NUANCE-EXPLANATION-PRODUCTION-WIRING-01 --run-dir docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01 --out docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/stop_check_01b.json`(rc=3で停止。有料呼出前にも再実行)。

## 正本
ユーザー原文=`docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_USER.md`(並行Workerが数分内に保存。着手後に必ず全文読む)。要点: 最大1件/英語表現の微妙な意味の違い・語感・文脈による印象差など学習価値のある内容/**KP・Word(最大5件、HR確定)と学習上の焦点が重複したらNG**(文字列一致ではなく焦点で判定。表現が文中に出るだけは可、実質同じ内容を教えるなら重複)/価値のある候補がなければ0件/過去Trial Promptを無検証でProduction採用しない/Part 4等は導入しない。

## やること
1. 素材: `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/`のTrial-01〜04 Part 3 Prompt・出力・Fable評価(`FABLE_EVAL_01.md:8`「揺れ・弱」等)を読み、弱点を3点以内に要約。
2. 改良Prompt v1(日本語解説、英語表現と本文引用+和訳、焦点を1行で明示、KP/Wordとの差別化を生成時に指示、候補なし可、長さ目安=Part 1の1項目相当)。モデル=本番ライン既定(`er019`等の`_a2_support_model()`相当=gpt-6-luna。評価用途の最新原則とは別、Charter 25節)。
3. 対象記事(既存完成本文を再利用、公開物は変更しない): X『AI島』Std/Adv、X『Paycheck Personality』Std/Adv、Z『告げ口心臓』Std/Adv、Y既存完成記事1本(存在すればStd/Adv)。各レベルでHR確定済みKP/Word(confirmed_*.json等。無ければ候補JSONの上位5件を暫定と明記)を入力に渡す。
4. 各対象で候補を1回生成(retryなし)→**重複検査**(2段: 構造=焦点語句がKP/Wordと同一/LLM判定=学習上の焦点が同じか、理由付き)→結果表(記事|レベル|候補表現|焦点|重複判定|理由|学習価値の自己評価)。費用は呼出ごとに記録(合計¥10以内、超過見込みで停止)。
5. 失敗例・弱点の分析(0件が妥当なケース、重複しがちなパターン、Part 1「類義語との違い」観点との役割分担)。必要なら改良v2を1回だけ(同一対象の再生成は最大1回)。
6. 成果物: `docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/PROMPT_TRIAL_01.md`(Prompt全文・結果表・候補本文全文・重複検査結果・費用)+`prompt_trial_01.json`(候補JSON。並行01aの設計§3 schemaが先にcommitされていればそれに合わせる。未commitなら自分の暫定schemaで出し、フィールド名を明記)。Trial用scriptは`docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/tools/`に置く(Productionコード・Prompt・既存出力は編集しない)。
7. `docs/pm/RESULT_PACKET_NXW1b.md`(整合/未承認機能/成果物と目的適合/判断候補/費用実績/commit、`判定整合:`行)。commit=自分のdocs・tools・委任文のみ明示`git add`→push(index.lock衝突は数秒待って再試行)。ACTIVE_TASKは触らない(01aが(O)行を更新)。最終回答は短く(対象数・候補件数・重複NG件数・費用・commit)。

## 範囲(11-8)
範囲内=Trial生成・評価・記録。範囲外=Productionコード/Prompt変更、公開記事変更、2件以上の選定、Part 4、Family A/B/C。判断(採用可否)はFable。
