# RESULT_PACKET JA-GLOSS-QUALITY-ALARM-TRIAL-01 委任_01 (2026-10-31)

要約: ユーザー決定をSSOT反映(commit 5434d470a、origin/main push済み)。現状調査・検証セット(115件)・方式7種の設計比較・HR警告表示試作の設計・Trial事前登録を作成。API費用¥0.298(Cap ¥15、probe 4 call、gpt-6-luna)。Production変更0。OPEN-636(INVESTIGATING)。本格Trial・DEV試作の実装は委任_02(Cap提案¥45)。

## 成果物(docs/research/JA-GLOSS-QUALITY-ALARM-TRIAL-01/)
CURRENT_STATE_01.md / EVAL_SET_01.md(+eval_set/{items,articles,batches,summary}.json・ITEM_LIST.md) / DESIGN_OPTIONS_01.md / HR_UI_MOCK_DESIGN_01.md / TRIAL_PLAN_01.md / tools/{build_eval_set_01,probe_01}.py / probe_01/(ledger.json+4出力)

## 検証セット(115件)
| 層 | dev | held-out | 計 |
|---|---|---|---|
| T1 ユーザー指摘/HR修正(問題確定) | 4 | 4 | 8(6表現、すべてX) |
| T3 合成誤訳(問題確定) | 12 | 10 | 22 |
| T2 HR承認済み・修正なし(正常・推定) | 38 | 33 | 71 |
| T4 判断が割れる(保留・Fable裁定) | 7 | 7 | 14 |
問題30(目標>=25)・正常71(>=60)・T1 8(>=8)・held-out 54/115=47%(>=40%、記事単位分割)。X/Y/Zを両splitに含む。T1にY/Zなし(限界)。バッチ41(同表現の重複回避のview A/B)。

## 方式(gpt-6-lunaのみ。判定は書かない)
M1 文脈直接照合(1項目1call、基準線、¥0.88/セット) / M2 level一括検査(2call、¥0.35) / M3 意味一致と自然さの分離検査(¥0.5) / M4 severity・confidence・category閾値の後処理(API追加0) / M5 警告候補のみ強制比較で追加判定(¥0.47) / M6 現訳を見せない盲検再生成→比較(¥0.6) / M7 生成時メタ情報併用の一括検査(M2+5%、独立性低下のためablation)。バッチ化でM1→M2約60%削減。

## 費用・時間
- 運用時追加費用: M2 ¥0.35/セット(¥70の0.5%)〜M6 ¥0.6。処理時間 10〜35秒(HR待ち前の非同期、クリティカルパス外)。
- Trial費用見積¥35.6+予備25%=**Cap提案¥45**(止め線¥36)。
- 使用費用: **¥0.298**(probe 4 call、gpt-6-luna、`probe_01/ledger.json`)。

## 重要な発見(設計入力)
1. **有病率問題**: ラベル付きセットは問題26%で実運用(推定3〜10%)より高い。Precisionは有病率に強く依存し、r=0.8で80%を満たすにはFPRが 5%有病率で1.0%以下 が必要。ラベル付きPrecisionだけでは運用の的中率を過大評価する。→ 実HR候補261件(27ファイル)を未ラベル運用プールとして検査し、警告項目のみブラインド裁定してPrecisionを実有病率で測る設計(TRIAL_PLAN_01 §2-1)。
2. probe(評価ではない): 合成誤訳2/2はmajor・highで検出。正常訳`clutter`にminor警告(確信medium/high=好み的誤警告の兆候)。verdict『結論』はmediumで警告(提案は『判決』)、lowでは警告なし=effortで挙動が変わる。strict JSON schemaは4/4遵守。

## 判断候補(いずれも現時点で新規ユーザー判断は不要=Fable裁定範囲。既判断[モデル限定・B3不採用・Precision80〜90%目標]は再質問せず)
1. Precisionの主指標を運用プール(P-a)とするか(原文§2「警告したもののうち本当に問題があった割合」に最も忠実、docs/pm/delegation_log/2026-10-31_JA-GLOSS-QUALITY-ALARM-TRIAL-01_USER.md:23,31)。分類=B(承認範囲内、Fable裁定)。
2. 重大誤訳ガード「major検出率>=85%」の事前登録確定(同:27「極端に絞って重大な誤訳を大量に見逃す方式は望ましくない」)。分類=B。
3. 委任_02のCap ¥45の設定(委任_01のCap ¥15超過。7-7により案件見積300円以下かつ日次1,000円内は自律)。分類=B。
4. 運用時の追加費用の許容上限(ユーザー未指定)。Trial後の採用判断時にユーザーへ提示(今は不要)。分類=C(現タスクと独立、後続)。
停止条件: T1<5は非該当(T1=8)、SSOT conflictなし、Cap到達なし。

## RESULT_PACKET 4行
(1) 既存仕様整合: 訳生成Prompt/仕様は不変(er003_key_words_gloss_alignment.py:152-156、CURRENT_SPEC.md:2892 X2p'を維持。ユーザー決定2)。HR画面の表示専用・署名外の先例(難易度表示、重複アラームは非blocking: er119_kp_human_review_01.py:575-630,1205、user_test/selection_form_v3/form_logic.js)と整合する設計。確定訳の保護(er128_kp_confirmed_content_01.py:91)に触れない。CURRENT_SPEC不変(Trial段階)。
(2) 未承認機能の既定値: Productionに入る未承認機能なし。新flag追加0・Production経路ファイル変更0(`git diff --stat`で er003_*/er119_*/er128_*/user_test/selection_form_v3/ 無変更)。DEV UIは委任_02で別dir。
(3) 失敗終了時の最終成果物: 停止なし(正常終了)。最終成果物=上記dir。ユーザー原文(アラーム機構の設計・Trial計画)への適合=設計・計画・検証セット・少額probeまで(本格Trial・DEV試作は委任_02、原文§7の到達範囲内)。実測Precision/Recallは未取得(本委任の範囲外)。
(4) 撤去・残置: 撤去した規則/検査/testなし(新規追加のみ)。OPEN-630のB3をREJECTEDへ更新(旧「条件付きVALIDATED」記述を残置し、決定前のTrial記録と明記)。Grep: `OPEN_ITEMS.md` OPEN-630行に「案B3=REJECTED」、`docs/research/JA-GLOSS-NUANCE-01/TRIAL_01.md` §9。

判定整合: 重大NG=なし / 主因=なし / 是正対象=なし / STOP理由=なし / 提示=可

## Git
commit/push: 1/2 = 5434d470a(SSOT反映+原文保存)。2/2(成果物)はfinal messageに記載。
