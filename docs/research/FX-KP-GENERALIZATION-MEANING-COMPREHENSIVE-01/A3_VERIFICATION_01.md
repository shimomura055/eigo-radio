# A-3 v3(Advanced英語説明Prompt補正)追加検証 結果(委任_04、2026-10-23)

結論(先頭): **Closeout案=USER_DECISION_REQUIRED(改善と悪化が拮抗)。Fable向け推奨材料=現行Prompt維持(A-3 v3は本番採用しない)寄り。** 総合合格率は 現行72% vs v3 73%(差なし)、「記事固有の条件混入なし(core)」は 82%→89%と改善、一方「本文中の意味との一致(sense_ok、2者Judge両方OK)」は 96%→92%へ微悪化。Production/Prompt変更0、追加費用 **8.04円**(目標10円・上限20円以内)。

## 1. 設計(委任_04のFable指定どおり、v3固定・新たなPrompt案なし)
- **再利用(API 0)**: 委任_02 Trialの`a1gE0`(現行Production説明Prompt)vs`a1gE3`(A-3 v3、説明Promptの"Additional rules"末尾2行追加)、難例14KP×3回=各42行とその2系統Judge結果(E2)を再集計(`reuse_table_01.py`)。
- **追加生成**: 既存Production run由来の**正常KP 25件**(Family X 20・Z 5。`er019_output/.../b1b`・`er026_output/.../b1b`の`keywords_canonicalized.json`のused_form/source_sentence/japanese_glossをそのまま入力=replay入力あり)を、`gpt-6-luna`(本番同一model)・同一dispatcherで 現行 vs v3 を各2回=計100行(unique 78行)、説明call 44回。
  - 種別(25件の主分類): 慣用句/比喩 7(off the hook, jump to conclusions, shock someone's wallet, take the wheel, play a part, in the spotlight, leap into action)・句動詞 6(turn out, think up, bring in, mix up, come first, hold on)・名詞句/複合名詞 5(time lag, former self, refueling support, letter of introduction, execution bell)・数量/程度表現 2(small positive link, all the same kind)・コロケーション/前置詞句 4(apply one's findings, take turns, at a moment's notice, behind price increases)・単語 1(abandon)。
  - 既存Trialの難例14KP(draw a line等、成句・比喩・動詞句中心)と合わせ**計38KP**(同一key+同一文は合算)。
- **Judge**: 2系統 `claude-sonnet-5-5` + `gpt-6.1-sol`(前回Trial同一系統、いずれも最新世代)、E2(sense_ok=本文での意味と一致 / core=記事固有の条件・目的を足さず中心義のみ / single=意味1つ)を新規unique 78行に**2系統とも**実施(1系統+不一致のみ2系統目より、全件2系統の方が費用内で偏りを避けられると判断。1行約0.045円)。armラベルは非開示(blind)。**PASS=2系統とも3項目OK**。加えてSonnet(本agent)目視。
- **判定基準(DESIGN_02 §4)**: 悪化=意味から外れる/不自然/曖昧化、記事固有混入率(core)、VALIDATED目安=悪化がbaseline以下かつ改善が有意、REJECTED=悪化が上回る、拮抗=USER_DECISION。数値は方向判断(±1件)。
- **KP別分類**: KPごとにarm別PASS率差(2Judge別に算出)。両Judgeが同方向に>0.2差=改善/悪化、一方が上がり他方が下がる=判断分かれ、それ以外=維持。n=2〜3のため1行1Judgeの揺れで「悪化」と出ることがある(下記ノイズ床)。

## 2. 集計(行単位、すべて2系統Judge結果)
| 集合 | arm | n行 | PASS(両Judge) | sense_ok(両) | core(両)=記事固有混入なし | single(両) | 平均語数 |
|---|---|---|---|---|---|---|---|
| 新規正常25KP | 現行(E0) | 50 | 40/50 (80%) | 48/50 (96%) | 42/50 (84%) | 46/50 (92%) | 9.3 |
| 新規正常25KP | A-3 v3(E3) | 50 | 40/50 (80%) | 47/50 (94%) | 47/50 (94%) | 46/50 (92%) | 8.4 |
| 難例14KP(再利用) | 現行 | 42 | 26/42 (62%) | 40/42 (95%) | 33/42 (79%) | 36/42 (86%) | 9.8 |
| 難例14KP(再利用) | v3 | 42 | 27/42 (64%) | 38/42 (90%) | 35/42 (83%) | 36/42 (86%) | 8.8 |
| **合計** | 現行 | 92 | **66/92 (72%)** | 88/92 (96%) | 75/92 (82%) | 82/92 (89%) | 9.5 |
| **合計** | v3 | 92 | **67/92 (73%)** | 85/92 (92%) | 82/92 (89%) | 82/92 (89%) | 8.6 |

(参考: 1Judgeずつ。合計のsonnet PASS 現行76%→v3 78%、sol PASS 87%→89%。新規25KPのみでは sonnet 84%→84%、sol 86%→94%。)

**KP単位の分類(38KP)**:
| 集合 | 改善 | 悪化 | 維持 | 判断分かれ |
|---|---|---|---|---|
| 新規正常25KP | 5 | 5 | 13 | 2 |
| 難例13KP(同一key+同一文を合算) | 2 | 1 | 9 | 1 |
| 計38KP | **7 (18%)** | **6 (16%)** | 22 (58%) | 3 (8%) |

**ノイズ床**: 同一armを2〜3回生成した際にPASSがぶれるKP数は 現行 新規6/25・難例7/13、v3 新規6/25・難例6/13(同程度)。新規25KPの「悪化」5件のうち4件は『1回・1Judgeだけの不合格』で、現行の揺れの範囲と区別しにくい。sense_ok(意味一致)が2Judgeの**片方でも**不合格になった行は 現行4→v3 7(新規 2→3: bring in / hold on / letter of introduction が各1行増、take the wheel・at a moment's noticeが現行側に各1行、難例 2→4: Carry the Load 2行・reach for someone's wallet 等)。

## 3. 観点別(i)〜(iv)
- (i)本文中の意味との一致: v3がやや**悪い**(sense_ok 両Judge 96%→92%。新規25KPでは 96%→94%)。『中心義・最も一般的な用法』の指示が、本文の用法(例: bring in=持ち込む)から離れた一般義へ寄る事例を生む。
- (ii)記事固有条件の混入(core): v3が**良い**(82%→89%、新規25KPでは 84%→94%)。apply one's findings(研究結果に限定)・execution bell(執行直前という限定)・leap into action(『行動が必要なとき』)・draw a line(『許容できることの限界』)など。
- (iii)過度な語義限定: 現行は『特定対象・場面への限定』(refueling support→vehicles、apply findings→研究由来)が散見。v3は限定が減る一方、refueling supportでは『飛行中の航空機』という別の限定を生む例が残る。専用の「narrow」Judgeは費用上実施せず、core項目とSonnet目視で代替。
- (iv)説明の自然さ: v3は平均8.6語で簡潔。不自然な出力・形式崩れ(QA不合格・パース失敗・retry)は新規100行・44callで **0件**(全行status=OK、retried=False)。ただし letter of introductionの「a letter that tells someone who another person is」のように、簡潔化で意味が曖昧になる例がある。

## 4. 代表例(原文付き。Judge noteは要約)
**改善(7KP中の代表)**
1. **apply one's findings**(新規): 本文「We can't apply its findings directly to everyday meanness or boredom that lasts a long time」 現行 r1 `to use the results of research in another situation`(両Judge: 研究/別場面に限定)・r2 `to use what someone has learned from research in another situation`(同) → v3 `to use what someone has learned or discovered in a particular situation` / `to use what one has learned in a particular situation`(両Judge 3項目OK)。現行0/2→v3 2/2。
2. **draw a line**(難例、ユーザー例): 本文「The words draw that line simply」 現行 `to set a clear limit on what is acceptable`(3回中2回が条件混入)→ v3 `to make a clear distinction between two things` / `to show where one thing ends and another begins` / `to set a limit or show a clear difference`。現行0/3→v3 2/3(1回は意味併記で両Judgeが不合格)。
3. **execution bell**(新規): 本文「At the city gates, the execution bell rang.」 現行r1 `a bell used to signal that an execution is about to take place`(用途/直前の限定を両Judgeが指摘)→ v3 `a bell that signals an execution`(両Judge OK)。1/2→2/2。
4. 他: leap into action(`…when action is needed`→`to start doing something immediately`)、take the wheel(現行r2が『車を運転する』字義に寄る→v3は2/2で比喩義)、rise above the other voices。

**悪化(6KP中の代表)**
1. **bring in**(新規): 本文「Of course, you can't bring in just anything you like」 現行 `to introduce or include something in a place, group, or situation`(2/2 OK)→ v3 r2 `to introduce or start using something`(sol: 『本文では持ち込む意味』=意味ずれ)。2/2→1/2。
2. **letter of introduction**(新規): 本文「He turned his letter of introduction between his fingers」 現行 `a letter that presents someone to another person and explains who they are` 2/2 → v3 r2 `a letter that tells someone who another person is`(sonnet: 紹介状の意味とずれ)。2/2→1/2。
3. **hold on**(新規): 本文「But hold on before reaching that conclusion」 現行 `to pause and wait before doing or deciding something` 2/2 → v3 r2 `to wait for a short time`(sonnet: 『制止して待つ』でなく単なる短時間の待機に薄まる)。
4. 他: in the spotlight(v3 `to be receiving a lot of attention`、sonnetが受動寄りと指摘)、small positive link(v3 r2『同方向に変化』に限定との指摘)、pull someone under(難例、現行1/3→v3 0/3: coreが両者とも不安定)。

**判断分かれ(3KP)**
1. **shine a light on**(難例): 現行 `to help people notice or understand something`(sol: 気づく/理解の併記)、v3 `to make people notice or understand something`(solが3/3で併記を指摘、sonnetは3/3 OK)。sonnet=改善/sol=悪化。
2. **shock someone's wallet**(新規): 現行r1 `to cost someone much more than they expect` は両OK、r2 `…surprised or worried…`は併記指摘。v3 `to surprise someone because something costs a lot`(sonnet: 『値段限定が表現外』、solはOK)。
3. **refueling support**(新規): 現行『vehicles/移動継続』の限定、v3『飛行中の航空機』の限定(solは両者を不合格、sonnetはv3の1/2をOK)。限定の種類が変わるだけで、改善とも悪化とも言えない。

## 5. 既存Production(現行Prompt)との品質比較
- 全体PASS(2系統とも合格)は 72% vs 73% で**実質同等**(差1行)。同一armの再生成ぶれと同程度。
- v3の効果は『記事固有条件の混入を減らす』(core +7pt)に限られ、代わりに『本文用法から離れた一般義への寄り』(sense_ok −4pt)が出る。
- 平均語数は約1語短い(9.5→8.6)。ユーザー例のdraw a lineは改善(2/3)するが、新規正常KPで同種の明確な改善は apply one's findings / execution bell / leap into action / take the wheel 程度。

## 6. Closeout案と推奨材料
- **Closeout案: USER_DECISION_REQUIRED**(DESIGN_02の基準で『悪化がbaseline以下かつ有意な改善』は満たさず、『悪化が上回る』にも該当しない拮抗: 改善7 vs 悪化6、判断分かれ3)。
- **推奨材料(Fable向け): 採用しない(現行説明Prompt維持、A-1のみ先行配線)寄り。** 理由: (1)総合PASSに差がない、(2)sense_ok(本文での意味との一致)が悪化方向(片方のJudgeでも意味ずれを指摘した行が4→7)で、品質の主項目を損なう側のリスクがある、(3)採用すれば`PROMPT_SHA256`(承認済みB仕様の逐語性の機械証拠)が変わる仕様変更になる、(4)改善効果が『記事固有条件の混入』型に限られる。
- **採用する場合の条件**: bring in型(本文の用法を一般義が上書きする)悪化を許容する判断と、Trial-02逐語性検査(PROMPT_SHA256)の更新。採用はユーザーの正式判断のみ(VALIDATED相当でも無断採用しない)。
- OPEN-476(bound→bind)は対象外(DEFERRED維持)。

## 7. 残存リスク・限界
- 1KPあたり2〜3回のみ。1行の揺れ(特に1Judge不合格)が分類を動かす。検定が成立する標本ではなく方向判断(DESIGN_02 §4『数値は方向判断』)。
- Judge自体の粗さ(両Judgeの判定が割れる: sonnet PASS 76〜78%、sol 87〜89%)。Sonnet目視は代表例の確認で、全行の人手採点ではない。
- 新規25KPは『既存run由来の1〜4件/call』で、本番(1runの全KPを1callで生成)とバッチ構成が異なる(両armで同一)。語義方針の差を測る目的への影響は小さいと判断。
- 現行arm=承認済みProduction説明Promptのreplayで、過去run実物の説明記録とは別標本。
- reach for someone's wallet・Carry the Loadは現行でもsense_okが不安定で、v3でも改善しない。Carry the Loadはsense_ok(両Judge)が 3/3→1/3 に低下(『持っていくもの』への寄り)だが、PASS数は同じため上の分類では『維持』。

## 8. 費用(出典: `er112_output/kp_gm_trial_01/a3_verify/paid_calls.jsonl`)
- 説明生成(gpt-6-luna) 44 call: 0.993円 / Judge sonnet 3.578円 + sol 3.472円(E2、unique 78行×2系統) / **計 8.042円**(目標10円・上限20円以内)。委任_02のTrial費用(約69円/80円Cap)とは別に計上する追加費用。

## 9. 証跡
`er112_output/kp_gm_trial_01/a3_verify/`: `reuse_table_01.py`・`gen_a3_verify_01.py`・`judge_a3_verify_01.py`・`analyze_a3_verify_01.py`/`analysis_out_01.txt`(KP別全出力・Judge note)・`all_rows_judged_01.json`・`kp_classification_01.json`・`runs/`(arm別生成物)・`paid_calls.jsonl`・`production_hash_unchanged.json`(Production module hash 開始=終了、unchanged=true)・`stop_check.json`(rc=0)。Judge cacheは既存`judge/{sonnet,sol}/cache.jsonl`に追記(同一行hashは再利用)。
- Production/Prompt/テンプレート/flag変更 0。記事B成果物変更 0。
