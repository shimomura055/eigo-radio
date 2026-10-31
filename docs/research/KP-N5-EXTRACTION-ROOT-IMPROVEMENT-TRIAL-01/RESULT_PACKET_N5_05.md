# RESULT_PACKET N5_05 KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01 委任_05 (2026-10-31) 採用判断用の最終Key Phrase比較
disk_guard=OK(free 59GB)。STOP通知なし(`stop_scope_check_01`rc=0を起動前に複数回確認)。成果物=`COMPARISON_05.md`(冒頭=記事別比較表)。事前登録=`TRIAL_PLAN_05.md`、証跡=`ev05/`、コード=`tools/n5r_*_05.py`。使用モデル=gpt-6-luna(GEN5)・gemini-3.8-flash(VER5)・gpt-6.1-sol(CHK5)=Production既定の最新系。
1. 範囲: Trialで抽出・選定を回した5セル(untidi a2/b1b・melos_a2・moon_b1b・surname_b1b。「24セル」は想定違い)。現行N5=Trial03のN5正式出力(公開済みProduction出力はN5配線前で比較不可)、A案=全rep(30rep)のE2プールにpick_A10(cap10)を再計算(API 0)。display_form・日本語の意味・区分は全て正式N5(GEN5→VER5→CHK5)の実出力(手作業の一般形なし)。
2. 費用: Phase 1見積約40円/Cap 52円(Gate通過: <300円、本日累計521+52<1,000円)→実費**¥38.88**(16 batch・82候補、ledger=ev05/cost_log_g5a/b/c.jsonl)。再現性用の追加抽出は不要(全セルrep>=2)。
3. 観測(担当者の暫定評価を含む): A案は`put away`+`in the way`が21/24rep(現行0/24)、一般形・意味とも正しい。cap7→10の増分は大半が価値中〜低(高評価+0.2件/記事、基礎句動詞+2.1件)、現行選定が平均約3件入れ替わる(`gets heated`[b1b]・`Not so fast`[a2]・moonの現行3件が消える)。再現性は現行と同程度(cap10共通数 a2 6.1/b1b 7.6)。概算+¥3.4/記事セット。GEN5の`oneself`再帰形組立失敗3件(surname、A案固有でない)。
4. 未測定/限界: 下流QA(canonicalization・人称整合・presentable filter・backfill)は両方式とも未適用。現行N5主表はB1 draw 1回。melos/moon/surnameは2repのみ。価値評価は主観。
(1)既存仕様整合: `er138:950-962`(pick)・`:1149`(generalize_verify_check)・`:1266-1294`(pool_and_select)はimport専用で無編集。cap10・A10は`n5r_lib_02.pick_A10`(委任_02)。fixture `n5_trial_replay_fixture_01.json`(配線時にProductionとexact一致確認済み、EVIDENCE_02)。承認済みB1条件4・5/TRIO:136は触れていない。
(2)Production到達経路: 新flag・設定dict・環境変数・起動script/.env変更なし、`n5_pool_fn`不使用。全コードは`docs/research/KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01/tools/`。確認=`git show --name-only`で自分のcommitは当該trial dir・delegation_log原文・OPEN_ITEMS.mdのみ。PRODUCTION_WIREDではない。
(3)失敗終了時の成果物/目的適合: 失敗終了なし(STOP・異常終了0、JSON途切れ0、retry 0)。最終成果物=`COMPARISON_05.md`。目的(ユーザーが具体的Phraseを比較して採否判断できる状態)に適合=記事別5表(区分・display_form・日本語・価値・頻度)+価値比較+N5外+put away/in the way+再現性+付録(全rep頻度・Production参考・N5外実測)。抽出率・残存率の集計のみで完了とはしていない。
(4)撤去・残置: 撤去した規則/検査/testなし(Trial追加のみ)。残置=なし。Grep: 新規識別子`n5r_*_05`はtrial dir内のみ。
判定整合: 重大NG=なし / 主因=cap7→10の増分が中〜低価値に偏る(判断はユーザー) / 是正対象=なし(Trial) / STOP理由=なし / 提示=可
判断候補(分類D=新規判断、A案採否): ①A案採用 ②A案採用+基礎的な易しい句動詞の扱いを同時決定(新仕様候補) ③現行維持 ④E2抽出のみ採用(効果限定)。Status候補=USER_DECISION_REQUIRED継続(OPEN-635追記済み)。
