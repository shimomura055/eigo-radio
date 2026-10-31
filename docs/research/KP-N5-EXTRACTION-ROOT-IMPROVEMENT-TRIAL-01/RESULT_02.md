# RESULT_02 KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01 委任_02(2026-10-31)

事前登録=`TRIAL_PLAN_02.md`(v2)・`TRIAL_PLAN_03.md`(Phase 3)・`TRIAL_PLAN_04.md`(Phase 3b)。Opus条件Aレビュー=`OPUS_REVIEW_01.md`。証跡=`ev02/`(rep_*.json=各反復の抽出・プール・SEL・pick、eval_*.json/summary_all.md=集計、ctl_*.json=対照、gen_cache_*.json=対象表現のGEN5/VER5/CHK5、cost_log_*.jsonl=費用台帳)。コード=`tools/n5r_*_02.py`(Trial専用、Production無編集)。
使用モデル: `gpt-6-luna`(B1/E1/E2/SEL/GEN5/rerank/slate=Production既定の最新系)、VER5=`gemini-3.8-flash`、CHK5=`gpt-6.1-sol`(いずれもProduction既定routing。評価目的で旧/下位モデルは不使用)。

## 1. 結論

**最低達成条件(`put away`と`in the way`の両方が、抽出され・意味が正しく・最終7件に同一反復で残る、≥7/8反復)を満たす回数非依存の方式は、試行した全アーム(15アーム、計30反復)で見つからなかった。** Status候補=**USER_DECISION_REQUIRED**(事前登録規則TRIAL_PLAN_02 §5-3。REJECTEDにしない)。

- 達成した部分: **(a)抽出**=網羅列挙E2・辞書E5・E6でプールに両表現が**8/8**(現行B1は0/8)。(b)**意味**=対象表現のGEN5→VER5→CHK5結果は正しい(下表§4。`put away`→`put something away`「物を片づけて収納する」、`in the way`→「邪魔になって」)。
- 未達の部分: **(c)最終7件への同時残存**。pick-level両表現同時残存(最終残存の必要条件)は最良でも A10 4/8、A7' 2〜3/8、A9 3/8、A13 3/8、A4d 0〜2/8、A3ref(出現回数、参考)0〜3/8。全アーム<7/8。したがって段階評価規則(TRIAL_PLAN_02 §2-9)により最終残存(CHK5後)も不合格が確定。
- 原因: cap 7内の順位付けの問題。`put away`は易しい句動詞(SEL難易度easy)、`in the way`は固定表現(upper/easy)で価値の種類が違い、1つの順位付けで両立しない。型昇格(R1/R1d)は`put away`を8/8残すが`in the way`を落とし、価値rerank(A7')は`in the way`を残す回があるが`put away`を落とす回があり、**rerank自体の再現性も低い**(A7'の`in the way`残存は fresh1回目8/8→2回目4/8)。出現回数昇格(参考A3ref)も解決しない。cap感度(API 0、R1d、untidi 24反復): cap 7=4/24、cap 10=18/24(75%)、cap 15=22/24(92%)=**7/8(87.5%)に届くには cap約15が必要**。

## 2. 根本原因(確度)

| 層 | 原因 | 確度 | 証拠 |
|---|---|---|---|
| 1 抽出 | 網羅列挙の指示文が主因。件数枠は副次。条件4・5は`in the way`/`in sight`の主因 | **高**(2×2対照で分離) | `ev02/ctl_ext_untidi_b1b.json`: 網羅列挙文面@14=`put away` 3/3・`in the way` 3/3、価値中立L1文面@40=`put away` 2/3、L1@30(重複回避文なし)=1/3、網羅列挙@40+重複回避文=3/3。重複回避文は影響なし(H7棄却) |
| 2 選定 | **cap 7内の順位基準**。(i)難易度順は易しい句動詞を後ろに回す (ii)昇格しても同順位内はpool入力順(P7→LLM出力順)で、upperの`in the way`がLLM出力順で押し出される (iii)価値の種類が異なる2表現を単一の順位に載せられない | **高**(多アーム・fresh再現) | R0d(決定論tie)でも0/16、R1d(型昇格)=`put away`は常時、`in the way`は rank 6〜20位(untidi 24反復、R1d順位) |

## 3. 比較案と推奨方式(Fable判定用の表。自分の推奨は「候補」)

pick-level両表現同時(S3必要条件)。N=各8反復(P1=Phase 1、P3=Phase 3、P3b=Phase 3b。fresh draw)。詳細=`ev02/summary_all.md`・`eval_p1/p3/p4_pick.json`。

| アーム | 層1/層2 | 両表現同時 | put away | in the way | 回数使用 | 備考 |
|---|---|---|---|---|---|---|
| A0 現行B1 | B1/R0 | 0/8 ×3回 | 0/8 | 1〜3/8 | なし | ベースライン。プール両表現 0/8 |
| A1 E1 | 条件4・5置換@30/R0 | 0/8 | 1/8 | 5/8 | なし | プール両表現5/8 |
| A2/A2d | E2/R0, R0d | 0/8 | 0〜2/8 | 4〜5/8 | なし | 決定論tieだけではA2と同じ(0/8) |
| A4/A4d | E2/型昇格 | 2/8, 0/8, 2/8 | 8/8 | 0〜2/8 | なし | `put away`は安定、`in the way`落ち |
| A5 辞書seed | E5/R0 | 0/8 | 0/8 | 6/8 | なし | LLM抽出0。プール両表現8/8 |
| A6' E2+E5差分+rerank | E6/RR | 1/8 | 3/8 | 2/8 | なし | SEL入力50件・N4一致0.859(基準0.862に僅差未達) |
| A7' E2+rerank | E2/RR | 2/8, 3/8, 3/8 | 2〜5/8 | 2〜8/8 | なし | 再現性低(rerankの揺れ) |
| A8 予約枠k=2 | E2/R5 | 0/8 | 8/8 | 0/8 | なし | |
| A9 slate選定(LLM 1 call) | E2/集合選定 | 3/8 | 8/8 | 3/8 | なし | N2平均1.75(A0 1.25) |
| **A10 区間分散(API 0)** | E2/区間7分割 | **4/8**(最良) | 4/8 | 7/8 | なし | 内容は見出し除く本文を7区間に分け各区間の最良を採用。HR選定12/12 |
| A12 見出し句除外+R1d | E2/R1d | 2/8 | 8/8 | 2/8 | なし | |
| A13 順位統合RRF(R1d×rerank) | E2/RRF(k=60固定) | 3/8 | 6/8 | 5/8 | なし | Phase 3b |
| 参考A3ref | E2/出現回数昇格 | 0/8, 3/8 | 8/8 | 0〜3/8 | **あり(参考、TRIO:136と衝突)** | 出現回数でも解決しない |

**推奨候補(Fable判定用・自分の推奨は候補)**: 回数非依存の単一アームでVALIDATED候補は無い。次の方針選択をユーザー判断へ(判断候補、分類D=新規判断):
1. 最低達成条件の再定義: 「同一反復で両表現がcap 7内に残る」を満たす一般則は存在しない可能性が高い(本実験のcap感度)。cap 7を変えずに、**易しい句動詞専用レーン(cap 7の外または内の予約枠)**を新設する案は`put away`型には効くが`in the way`型(固定表現)は別問題(要UI/HR提示数への影響の判断)。
2. cap(7)の引上げ(P6): R1d順で cap約15が必要(HR提示数・選定UI・ER-119 HR flowへ波及。承認済み仕様の変更)。
3. 出現回数の利用(R2系): **参考A3refでも未達**であり、TRIO:136/:186の撤回・変更を要するため推奨しない。
4. 抽出改善(E2など)のみを先行採用: プールには両表現が入る(S1 8/8)が最終7件に残らない=ユーザー目的(最終候補まで残す)を単独では満たさない。HR選定の残存(N3b)・易しい表現増加(N2)の副作用は軽微だが、効果もpick規則を変えない限り限定的(`put away`は 0〜2/8、`in the way`は 4〜5/8、現行は 0/8, 1〜3/8)。

## 4. 再現性・最終残存

- 最終残存(CHK5通過後・下流QA前)は、段階評価規則(TRIAL_PLAN_02 §2-9)により、pick-level S3<7/8のアーム全てで不合格確定のため、**全アームの最終7件へのGEN5/VER5/CHK5は実行していない**(費用管理。A0の全件GENも同様に未実行=TRIAL_PLAN_02 §2-9の「A0は常に実行」からの逸脱。A0は`put away`をプールに入れないためS3が構造的に0で、判定に影響しない。逸脱として記録)。
- **S2(意味)**: 対象表現のみGEN5→VER5→CHK5(`ev02/gen_cache_untidi_*.json`、各≤7件batch):

| 記事 | span | 一般形 | 日本語 | CHK5 relation |
|---|---|---|---|---|
| untidi_b1b | put away / put it away / putting something away | put something away | 物を片づけて収納する | FRAME_SHIFT(修正採用)/SAME/SAME |
| untidi_b1b | in the way / something in the way | 同左 | 邪魔になって / 邪魔になるもの | SAME / SAME |
| untidi_a2 | put it away | put something away | 物を所定の場所にしまう | SAME |
| untidi_a2 | in the way | in the way | 邪魔になり、物事の進行を妨げて | SAME |
| untidi_a2 | something in the way | something in the way(本文形へrevert) | 邪魔になるもの、妨げ | VER5=FIX→revert(CHK5 relation=None) |
| untidi_a2 | in sight / leave it out | in sight / leave something out | 視界に入って、見える状態に / 物をしまわず外に出したままにする | SAME |

 全てgloss正しい(担当者が本文を読んで確認)。S2は達成(対象100%)。ただし`put away`のFRAME_SHIFT→修正の1件と`something in the way`(Std)のrevert経路はCHK5が単純なSAMEではない(記録)。
- 反復: Phase 1 8反復(untidi_b1b 5・untidi_a2 3)、Phase 3 fresh 8反復(4+4)+held-out 6反復(surname_b1b/moon_b1b/melos_a2 各2)、Phase 3b fresh 8反復(4+4)。held-outは`put away`/`in the way`の対象が無い記事(0/6)で、側作用(下記)にのみ使用。

## 5. 副作用・回帰(pick-level、`ev02/eval_p*_pick.json`、基準はTRIAL_PLAN_02 §4)

| ID | 結果 | 判定 |
|---|---|---|
| N1 本文に無い表現 | 全アームのpickは`collect_pool`の本文一致・既存Gateを通過(0件) | 満たす |
| N2 易しい表現(相対、A0平均+1.0以内) | A2系/A4系/A10/A12/A13 ≤0.62、A9 1.75、A7' 1.25〜1.62(A0 0.88〜1.25) | 全アーム満たす |
| N3 他KPの押し出し | (a)A0最終7件との差: 全アーム平均3〜4.5件(基準≤2件)=**全アーム不合格**。理由=cap 7内で新規入場が3件以上(A2系のプール変更だけで3.4件)。(b)HR選定残存: untidiの2項目 12/12(A9 10/12、A7' 11/12) | (a)不合格 |
| N4 SEL安定性 | 同一プールSEL3回: cls/keep一致 A0=0.911・E2=0.912(基準0.862=平均−5pt)、difficultyは 0.689/0.895。共通候補一致: P1 A1 0.915、A2系 0.913、A5 0.888、A6' 0.859(不合格)、P3 0.929(untidi)・0.893(held-out) | A6'以外は満たす |
| N5 意味不適切 | GENは対象表現のみ(未評価) | 未測定 |
| N6 費用/時間(A0比、serial合計) | E2系 +¥0.41〜0.44/level・+38〜51秒、rerank/slate/RRF系 +¥0.50〜0.54・+49〜62秒 | 費用は満たす(≤+¥1.5)、時間は+40秒を超過(P7呼出と並列化できれば隠れる) |
| N7 retry負荷 | 全240呼出中 JSON途切れ再試行1件(0.4%、E2の1回)。SEL(最大50件)で途切れなし | 満たす |

報告項目(判定外): タイトル由来句(`Now in Session`)混入 A0 0.5/level→A12 0.0。`leave out`の最終7件残存は全アームで0(S5)。`in sight`はA0 2〜4/8、A9 5/8、A3ref 4/8。held-out(6反復): 全E2系アームで入場3.2件/level、N2≤0.33(A7' 1.33)、タイトル混入0。S4(価値判定、伏せリスト)は、S3不達で判定に影響しないため**実行せず**(段階評価の費用管理。TRIAL_PLAN_02 §7の手順は未使用)。

## 6. QCD影響

- **費用**: Trial実費=¥68.87(Cap ¥130/止め線¥120、進捗報告点¥45は Phase 3で通過、¥85は未到達)。内訳の概算: Phase 1(8反復+対照)≈¥31.5(含む2×2対照約¥3.5+同一プールSEL約¥1.2)、Phase 3(14反復)≈¥19、対象表現GEN約¥5.4、Phase 3b(8反復)≈¥12.6。量産への追加(採用した場合): E2系 +約¥0.4/level(+約¥0.8/記事セット=70円目標の約1.2%)、rerank/slate/RRF系 +約¥0.5/level(+約¥1.0/記事セット、約1.4%)。いずれも最低達成条件を満たさないため採用提案はしない。
- **処理時間**: E2系 +約38〜51秒/level(E2抽出が長い。P7呼出と並列化できれば隠れる)、rerank/slate/RRF +約10秒。
- **retry**: 増加なし(0.4%)。

## 7. StatusとProduction変更0の証明

- Status候補=**USER_DECISION_REQUIRED**(OPEN-635)。未承認・Trial・Production無配線・既定OFFの新flagも無し(PRODUCTION_WIREDではない)。
- Production module/Prompt/閾値/Gate無編集: `git diff --name-only cd49297ae HEAD`(委任_02開始時の基点から)で変更は`docs/research/KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01/`配下と`OPEN_ITEMS.md`のみ(RESULT_PACKETのcommit時に最終確認)。Family A/B/C不使用。`n5_pool_fn`不使用、flag・.env変更なし。

## 8. 採用判断に必要な事項(承認済み仕様との差分、R-10)

TRIAL_PLAN_02 §8の表のとおり: (a)B1条件4・5の置換/撤去、E2網羅列挙(`er138:308-310`、2026-10-22逐語) (b)N5 pick順位規則の変更(R0d/R1/R1d/R5/A10/RRF、`er138:950-962`、2026-10-30承認) (c)rerank/slate段の追加(新工程) (d)出現回数の利用(参考A3ref、TRIO原文`docs/pm/delegation_log/2026-10-31_LEARNING-ITEM-QUALITY-TRIO-01_USER.md`:136・:186の撤回・変更が必要) (e)E5辞書seed(新工程)。**加えて本結果から**(f)cap 7の変更(P6)は R1d順で約15が必要=HR提示数・選定UIへ波及。いずれもユーザー判断。

## 9. 限界・逸脱の記録

- 限界: 最終残存はCHK5通過後・下流QA(canonicalization QA/人称整合/presentable filter、OPEN-633)前(さらに本Trialは最終GENをpick-level S3不達のため大半で未実行)。fixtureのP7はQA通過後。held-outに対象表現・公開HR選定が無い。反復N=8は粗い(A7'のrerankは再現性が低いことを観測)。S4は未実行。
- 逸脱(事前登録からの): ①A0の全件GEN5/VER5/CHK5を未実行(§4) ②Phase 1の2プロセス起動間隔: proc1→proc2の起動が78秒(規則150秒以上)。Phase 3の2プロセスも約90秒。API rate・cost logへの影響なし(JSON途切れ0〜1件) ③Phase 3/3bは結果観測後に追加の事前登録(TRIAL_PLAN_03/04、いずれも実行前にcommit・push済み)で実施、既存基準は不変 ④held-outはPhase 3(p3モード)のみ実行(Phase 3bのA13は不合格のため未実行)。
- 新規OPEN: なし(OPEN-635の更新のみ)。分類=ユーザー判断要。
