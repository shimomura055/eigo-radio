# TRIAL_RESULT_03: 最小化条件を現行Production経路へ組み込む比較Trial(Luna、同一14本文・同一shortlist)

管理ID: FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03 委任_01 / 2026-10-22 / Trial専用(Production無変更) / 到達: TRIAL_DONE_PENDING_FABLE
Excel: `docs/research/FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03/KP_MIN_PRODPATH_COMPARISON_03.xlsx`(Sheet1 KP横並び/Sheet2 品質・遵守・語数/Sheet3 評価詳細/Sheet4 費用・条件・Prompt全文)

## 1. 結論(最小化は改善したか)
**事前指定の合格基準を満たさず、現行Production経路への第3条追加は改善とは言えない(推奨=現状維持)。**
- 語数は小さく短縮(ペア12単位x60件、選定直後 2.167->2.033語、4語の表現 4件->0件)。ただし現行Production経路は元々平均約2.1語で、短縮余地が小さい。
- 一方、Arm Bは**最終KP生成に失敗した単位が2/14**(canonicalization INVALID、Arm Aは0/14)。評価のV(学習価値)・E(易しさ排除)は下がり、C/U/S/X(最小化観点)は実質同等(差は評価のぶれの範囲)。
- 判定: (a)遵守率(最終成功率)=B劣る (b)語数短縮=達成(小) (c)C/U/S/X上回り=達成せず(span版+0.08、final版0.00) (d)V/E/N非低下=達成せず(下がった)。

## 2. 遵守・語数(機械検証、API 0)
| 指標 | 既存Production | Arm A(現行) | Arm B(+第3条) |
|---|---|---|---|
| 最終KP成功(5件) | 14/14 | 14/14 | **12/14**(B_Standard・D_Standard=Canonicalization INVALID) |
| 5語超(display/key) | 0/0 | 0/0 | 0/0 |
| 本文span不在 / 重複 | - | 0 / 0 | 0 / 0 |
| 平均語数 選定直後(全成功単位) | 2.157 | 2.143 (70件) | 2.000 (65件) |
| ペア12単位 平均語数 選定直後 / canonical後 / 本文span | - | 2.167 / 2.217 / 2.117 | 2.033 / 2.117 / 2.017 |
| ペア12単位 語数分布(1/2/3/4/5) | - | 10/34/12/4/0 | 9/40/11/0/0 |
| Redundancy retry発火単位 | - | 2 | 2 |
| Strategy L fallback | - | 1(E_Standard、db_hybrid selector INVALID) | 0 |
- 現行再現性: Arm Aと既存Production KPの本文span一致は43/70(61%)。同一プロンプト・同一shortlistでもLLM非決定性により約4割が入れ替わる。A-B一致は45/60(75%)。**B vs Aの差(語数-0.13、評価差0.1前後)はこの揺らぎと同程度で、効果の有無を断定できない。** 評価にも同じ揺らぎがあり、n=60/arm、評価者1系統。
- 本文一致(source span)はProductionの候補ID契約により構造的に100%で、第3条はこの安全装置に影響しない。
- **Arm Bの失敗2件の機構**: Bが「最短形」として代名詞を含む断片(`just my personality`、`use its results directly to`)を選び、canonicalizationの一般化(my->someone's等)がRule7(source_span内の連続性)で不合格になった(2回目試行も同型)。**短縮圧力が『一般化しにくい断片』の選定を増やす副作用**。Productionでは最終KP欠落=下流停止/Human Review側に送られる。
- 副次の発見(要報告、本Trialでは未修正): D_Standard(Arm B)で、Redundancy retryの2回目attemptのcanonicalizationがINVALIDになると、`keywords_canonicalized.json`には**1回目attempt(Redundancy NG判定済み)の旧KPが残ったまま**、戻り値statusだけがINVALIDになる(stale_disk_items=5)。runner(er019:411-414)は戻り値statusを出力するのみで、後段が当該ファイルを読む設計か要確認。Trialではディスクの残骸を採用せず失敗として集計(`validation.json`)。

## 3. 独立評価(claude-sonnet-5-5、TRIAL-02と同rubric、A/B匿名同一バッチ、各60件。V/E/N=前回と同尺度、C/U/S/X=TRIAL-02と同尺度)
| 対象 | arm | V | E | N | C | U | S | X | padding set |
|---|---|---|---|---|---|---|---|---|---|
| 本文span(Trial①と同形) | A | 1.050 | 1.000 | 1.717 | 1.633 | 1.950 | 1.800 | 1.767 | 11/12 |
| | B | 0.983 | 0.883 | 1.767 | 1.633 | 1.933 | 1.850 | 1.817 | 12/12 |
| canonical後key_phrase(最終) | A | 0.967 | 1.000 | 1.850 | 1.600 | 1.867 | 1.817 | 1.867 | 7/12 |
| | B | 0.900 | 0.917 | 1.833 | 1.583 | 1.867 | 1.800 | 1.900 | 11/12 |
- C/U/S/X合計(span): A 7.150 / B 7.233、final: 7.150 / 7.150。V/E/N合計(span): 3.767 / 3.633、final: 3.817 / 3.650。単位ごとのB>A / B<A / 同点はVが(span・final共通)3/6/3、Eがspan 2/6/4・final 2/5/5。いずれもぶれの範囲で『B優位』の証拠はなく、V/Eがやや下がる方向。
- 評価者は前回主評価と同じSonnet 5.5のみ1系統(費用のためSolは省略)。前回との比較可能性: V/E/N文言・採点基準は同一。ただし前回は5モデル混在のセット、今回は2セットの匿名比較で、絶対値の直接比較はしない。canonical後版はrubric条件1のみ「原形化後の見出し形」に読み替えて採点。

## 4. 例示追跡・Trial②との参考比較
- `think up what happens next`: 既存Production・Arm A・Arm Bすべて`think up`(C_Standard/C_Advanced)=第3条なしで既に最短。
- `formal agreements with their creators` / `alone caused the different results`: 現行経路ではいずれのarm・既存Productionにも選定されず追跡不能(shortlist候補の選択肢に該当形が選ばれない)。
- Trial②(Luna全文渡し+新Prompt、自由抽出、平均3.14語)との参考比較: 現行Production経路は候補一覧から選ぶ方式のため、第3条なしでも本文span平均約2.1語。尺度・方式が異なるため優劣比較しない(Production経路は短縮余地が小さい)。

## 5. 費用・量産原価への影響(実測)
| 項目 | 見積(実行前) | 実費 |
|---|---|---|
| 選定チェーン(Luna: 選定+canonicalization+gloss+Redundancy QA)Arm A / Arm B | 34〜56円(2arm) | **16.29円 / 16.54円**(53 / 55 OpenAI呼出) |
| 独立評価(Sonnet 5.5、24呼出) | 25〜45円 | **42.83円** |
| **Trial合計** | 60〜100円(Cap150) | **75.67円** |
- 1単位(1レベル)当たり全工程: A 1.164円 / B 1.182円。選定のみ(最終attempt): A 0.418円 / B 0.446円(+6.7%、推論出力増)。
- **量産原価影響(Arm B - Arm A): 1記事セット(2レベル)当たり 選定+0.056円、KP全工程+0.036円**(70円/セット目標に対し無視できる、増減もノイズ範囲)。
- 当日累計: 約799.5(PNPS9) + 75.67 = 約875円(日次1,000円内)。初回起動時の事故で、応答前に終了したLuna選定呼出が最大8件あり得て、課金済みなら約3円以下(usage log 0件で上記に含まず)。
- 出典: `er102_output/kp_min_prodpath_trial_03/cost_summary.json`、`usage_A.jsonl`/`usage_B.jsonl`(er005_cost_logger)、`paid_calls.jsonl`(評価)。

## 6. 限界
1回の実行(各arm1回)のためLLM非決定性を分離できない(A-Prod一致61%が示す揺らぎ)。評価者1系統・n=60/arm。第3条の挿入位置は現行templateの「1〜5語」段落直後(「5語以内」「学習価値」の文言が現行にないため)で、太字・番号は付していない(別位置・別文言の影響は未検証)。Arm AのE_StandardだけStrategy L fallbackで、同一単位のA/Bはfreeな条件差を含む。選定はshortlist候補の表層形に拘束されるため、Promptで短縮できる範囲は候補の選択に限られ(canonicalizationの原形化は別工程)、自由抽出のTrial①と同程度の短縮は原理的に出にくい。

## 7. Fable独立評価・Trial終了Status(2026-10-22)
- 分類: **`REJECTED`**(現行Production経路のKP選定Promptへの最小化条件(第3条)追加は不採用)。
- 根拠: (1)現行経路(候補DB照合方式)の出力は元々短く(平均2.17語、4語4件/60、5語超0)、第3条での短縮は平均-0.13語と小さい。(2)一方で短縮圧力により代名詞を含む断片(例`just my personality`)が選ばれ、原形化・一般化(canonicalization)が2/14単位で失敗し、最終KPが得られなかった(現行は14/14)。(3)評価の学習価値V・易しさ除外Eは低下、最小化観点は同等。(4)費用差は+0.036円/セットで無視できるが、品質面で利点がない。(5)ユーザー例示`think up what happens next`は現行Production経路で既に`think up`が選ばれており、他2例は現行経路では選定対象にならない。**先行Trial(全文渡し方式)で見えた「長く焦点のぼやけたKey Phrase」は、現行Productionの方式では元々ほぼ発生していない**。
- 読み方の注意: Arm Aと既存Production KPの一致は61%、A-B間75%で、LLMの非決定性による入れ替わりが約3〜4割ある。各arm 1回実行のため、小さな差は揺らぎと区別できない(本結論は「改善の証拠がない+失敗増」に基づく)。
- Closeout: Production/Prompt/Validator無変更。追加のPrompt案(第3条をcanonicalization側へ/代名詞断片の但し書き)は改善見込み低〜中のため起票しない(ユーザーが望む場合のみ)。
- 逸脱記録: STOP確認結果を見る前の有料process起動(即kill、<=約3円、PM_GOVERNANCE 26節の手順逸脱)。原因=手順順序の誤り。再発防止=runner側でSTOP確認のrc!=0なら起動しないガードを`er102`等のTrial runnerに入れるのではなく、委任文T-3/26節の手順を厳守(記録のみ)。なお当時のSTOP_ALL一時出現(rc=3)の原因はtest由来と判明(`FOLLOWUPS_01.md` B2)。

## 8. ユーザー判断
不要(現状維持=Prompt無変更。ユーザーが別案の検討を望む場合のみ指示を受ける)。

(委任_01時点の旧「分類候補/判断候補」は上記7・8に置換。副次発見2件の確認結果=`FOLLOWUPS_01.md`。)
