# AUDIT_SUMMARY_01: Key Phrase意味・説明品質Trialの検証実態とNG原因(FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_10)

API 0・新規生成0・Production変更0・既存コード変更0。調査・集計・報告のみ(採用判断・改善提案なし。UDR #171は保留)。
詳細=`ADV_AUDIT_01.md`(付表に全60+44+120出力)・`STD_AUDIT_01.md`(付表に全360出力)・`CONSISTENCY_01.md`。集計script=`AUDIT_01/audit_01_*.py`(読み取り専用)。
略記: T2=`er112_output/kp_gm_trial_02/results.jsonl`、T3=`er112_output/kp_gm_trial_03/results.jsonl`(行=1始まり)。

## 結論(先頭)

1. **「59/60」の唯一のNGはStd日本語意味の誤りに起因する**: `reach for someone's wallet` rep1。Std「人の財布に手を伸ばす」(盗む読み)の「人の」をAdvが引き継ぎ "another person's wallet to take or use it" と生成(T2 行174、入力gloss=T2 行10)。同じ入力のrep2・rep3はPASS。
2. **Std誤り→Adv波及の件数(分母=Std誤り入力、分子=Adv NG)**: 難例A **1/5**(Std誤り5出力のうち波及1)。通常B **0/1**(「0/120」ではなく、波及を測れる事例は1件)。Std薄(△)入力は2件、波及0。
3. **「伝染0件」は実行層Sonnetの目視**で、独立Judge・gold・複数rep・正式なStd/Adv整合Judgeは無い。確認していない項目は明記(§5)。
4. **Std(Fable最終判定、各方式120出力)の確定FAIL: G0=3(字義訳3)、G2=1(字義訳1)、G3=2(文法・意味関係2)**。G0のみ別に境界1(`settle at`、語義誤認)。薄い(△)は別集計でG0=0/G2=3/G3=4。
5. 過去報告の数字は再計算で**ほぼ再現**したが、**判定者・基準・母集団が数値ごとに異なる**。同一の60出力がSonnet暫定45/60・Opus確定59/60。暫定値本文がTRIAL_RESULT_02.mdに残置(§6)。
6. **個別判定ログが保存されていないのはOpus盲検**(集計のみ)。そのためOpus基準の一部(Std G0 NGの同定等)は推定を含み、本文で明記した。

## 1. 検証全体の一覧

| 検証 | 独立KP数 | 生成回数・出力数 | 条件 | 結果 | 判定者 | 根拠 |
|---|---|---|---|---|---|---|
| T2 Std(G0/G2/G3) | 26(難例20+通常6) | 各28出力(判定対象はrep1の26。`draw a line`のみ3rep) | gpt-6-luna、現行(G0)/用法先決め(G2)/定訳・案選択(G3) | Opus PASS: G0 24/26・G2 26/26・G3 25〜26/26 | Opus盲検(**個別ログ無し・集計のみ**) | OPUS_REVIEW_04.md:5 |
| **A: T2 Adv E0@G0** | 20(難例) | **60**(各KP3回) | 現行Adv Prompt、luna、1KP/call、入力=本文1文+KP+G0のStd日本語意味 | **59 PASS / 1 NG** | Opus盲検(確定gold) | OPUS_REVIEW_04.md:6、T2 行174(NG) |
| T2 Adv E0@G2/E0@G3 | 難例20+draw a line rep2,3 | 各22(母集団未特定) | 同上(入力=G2/G3のStd) | 各22/22 PASS | Opus盲検 | OPUS_REVIEW_04.md:6 |
| T3 Std(G0/G2/G3) | 60(難例20=T2と同一KP・新規生成+新規通常40) | 各120(60KP×2rep)=計360 | gpt-6-luna | 確定FAIL 3/1/2(+境界1)、薄△ 0/3/4 | Fable盲検(最終) | FABLE_BLIND_RESULT_03.md:7-18 |
| **B: T3 Adv E0@G0/G2/G3** | 40(通常のみ) | **120**(3方式×rep1) | 現行Adv Prompt、luna、1KP/call、入力=各方式のStd rep1 gloss | 公式: 伝染0・矛盾0・sense誤り0。欠陥1(run on 2義併記) | 実行層Sonnet目視(独立Judgeなし) | TRIAL_RESULT_03.md:16,54 |

Prompt同一性: 本文はProduction(`er019_family_x_kp_explanation_01.py:54-85,164-178`)と同一だが **1KP/call(ヘッダ"1 Key Phrase"・`x1`)で、n=5固定のPROMPT_SHA256(`c3d3734b…`、同:142)とはバイト同一ではない**。PROMPT_SHA256はresultsに未記録。KPの種類: 難例20=慣用句・比喩11/字義・用語6/句動詞2/境界1、X16・Z4。通常40=句動詞10・慣用句/定型11・コロケーション11・名詞句/用語8、X30・Z10。

## 2. Advanced NG原因別内訳

| 原因分類 | A(60出力) | B(120出力) | 根拠 |
|---|---|---|---|
| (i) Std意味の誤りに起因 | **1**(reach for someone's wallet rep1) | 0 | A: T2 行174。同入力rep2(行167)・rep3(行181)はPASS、E1/E4/E0@G2/E0@G3(行111,122)でもPASS |
| (ii) Adv生成自体に起因 | 0 | 正式NG 0。欠陥1(`run on` E0@G0の2義併記、Stdは正) | B: T3 行426 |
| (iii) 両方 | 0 | 0 | Aの1件は同入力でrep2/3がPASSのためAdv生成のゆらぎも条件。(iii)と読む余地(実行層の分類は(i)) |
| (iv) 特定不能 | 0 | 0 | |
| **NG合計** | **1(59/60の残り)** | 0(正式) | OPUS_REVIEW_04.md:6 |

## 3. Standard G0/G2/G3別・NG原因別内訳(Trial_03、Fable最終判定、各120出力)

| NG分類 | G0 | G2 | G3 |
|---|---|---|---|
| 字義訳NG | 3 | 1 | 0 |
| 語義誤認NG | 0 | 0 | 0 |
| 文法・意味関係NG | 0 | 0 | 2 |
| その他NG | 0 | 0 | 0 |
| 原因不明 | 0 | 0 | 0 |
| **確定FAIL合計(=分類合計)** | **3(2.5%)** | **1(0.8%)** | **2(1.7%)** |
| 境界(FAIL寄り、合計の外。語義誤認) | 1(`settle at` rep2) | 0 | 0 |
| 薄い(△、別集計) | 0 | 3 | 4 |

根拠: FABLE_BLIND_RESULT_03.md:7-17(FAIL/△のセル)をkey(`fable_blind_std_03_key.json`)でarm/repに復元。FAILのT3行: G0=行60・177(unseen clock)・行2(reach)、境界=行191(settle at)、G2=行212(draw a line)、G3=行61(apply)・行29(reach)。分類はFable記述に従ったが、G3 reach「誰かの財布」は分類記述が無く**実行層の推定**(所有者誤り)。`reach for someone's wallet`は字義訳/所有者誤りの両読みが可能で、所有者誤りに統一した感度でも合計は不変(3/1/2)。薄い(△): G2=price tag・reach rep2・standard deviation、G3=brace・on the throne・standard deviation×2(STD_AUDIT_01.md §1-2)。

Trial_02 Std(Opus基準、n=26/方式): G0 NG2(字義訳2: draw a line=確実、reach=推定)・G2 0・G3 0〜1(未特定=原因不明扱い)。個別ログ無し(STD_AUDIT_01.md §5)。

`draw a line`「線を引く」の発生(Trial_02の3rep+Trial_03の2rep=各5出力):

| 方式 | 厳密形「線を引く」 | 変種「はっきりと線を引く」 | 字義NG計 | 出力の所在 |
|---|---|---|---|---|
| G0 | **2** | 0 | 2/5 | T2 行7(rep1)・行80(rep3)。T3は2/2が「一線を引く」(慣用義・許容) |
| G2 | 0 | **1** | 1/5 | T3 行212(rep2)。T2は境界をはっきりさせる×2・はっきり区別する |
| G3 | 0 | 0 | 0/5 | T2は区別をはっきりさせる/境界をはっきりさせる/一線を引く。T3行481は欠損補修の再実行出力 |

(「境界線を引く」の発生は0回。全21出力の一覧=STD_AUDIT_01.md §4。)

## 4. 代表的なNGの実例

| KP | 本文での意味 | 実際の日本語出力 | 正しい意味 | NG理由 | G0/G2/G3の発生 |
|---|---|---|---|---|---|
| reach for someone's wallet | "That's enough to make you reach for your wallet before the volume button"=自分の財布を出して支払う/買う気になる | G0 rep1「人の財布に手を伸ばす」(T3 行2)、G3 rep1「誰かの財布に手を伸ばす」(行29) | お金を払おうとして財布に手を伸ばす/財布を出す(gold)。不可=盗む解釈 | someone'sを他人の財布と取り盗む読み(分類: G0=字義訳、G3=所有者誤り[推定]) | G0 1(rep1)、G2 0(rep2は「人が支払いを覚悟する」=薄△)、G3 1(rep1) |
| an unseen clock | "A coffee price tag may have an unseen clock of its own"=表からは見えない独自の時間の仕組み(比喩) | G0 rep1・rep2「目に見えない時計」(T3 行60,177) | 表には見えない時間の仕組み 等(同KPのFable PASS例) | 比喩を字義の「時計」で訳した | G0 2/2、G2 0、G3 0 |
| draw a line | "The words draw that line simply"=許容/不許容の区別をはっきり示す | G2 rep2「はっきりと線を引く」(T3 行212)、T2 G0 rep1・rep3「線を引く」(行7,80) | 一線を引く/区別をはっきりさせる/線引きをする/境界をはっきりさせる(gold確定) | 「描く動作」の字義訳 | 字義NG: G0 2、G2 1、G3 0(各5出力) |
| apply one's findings | "We can't apply its findings directly…"=その研究の知見を当てはめる | G3 rep1「人の研究結果を当てはめる」(T3 行61) | (自分の/研究の)結果を当てはめる・応用する | its/one'sを「人の」と他人に取る所有者誤り | G0 0、G2 0、G3 1 |
| settle at(境界) | "Brent rose 9.59% and settled at $83.30"=終値が～で終わった | G0 rep2「～で落ち着く」(T3 行191) | ～で取引を終える | 市場用語の語義が落ち一般義を選択(FAIL寄りの境界) | G0 1(境界)、G2 0、G3 0 |
| Adv: reach rep1 | 上記reach | Adv "to move your hand toward another person's wallet to take or use it"(T2 行174、入力「人の財布に手を伸ばす」=T2 行10) | to get ready to pay for something | gold不可の盗む解釈。入力の「人の」の逐語反映 | 59/60の唯一のNG |

## 5. Std誤りがAdvに波及した件数と根拠

| 検証 | 分母: Std誤り入力の出力 | 分子: うちAdv NG | 波及率 | 根拠 |
|---|---|---|---|---|
| **A: E0@G0 難例20×3** | **5**(draw a line rep1・rep3「線を引く」/reach rep1〜3「人の財布に手を伸ばす」) | **1**(reach rep1) | **1/5** | T2 行127,113(draw a line E)・行174,167,181(reach E)。Std誤りの同定: GOLD_LABELS_FINAL_01.md(draw a line不可欄)、Opus Std G0 24/26(NG2件)、FABLE_BLIND_RESULT_03.md:9(reach同一文字列FAIL) |
| A(感度: 「人の研究結果を応用する」×3を誤りに含めた場合) | 8 | 1 | 1/8 | Fable T3はG3の同型「人の研究結果を当てはめる」をFAIL(FABLE:7)。Opus G0のNG2件には含まれない(推定) |
| **B: E0@G0/G2/G3 通常40×3** | **1**(`an unseen clock` G0「目に見えない時計」) | **0** | **0/1** | T3 行412(E)=入力は行60。出力 "a hidden sense of time…" は「時計」を引き継がず(実行層目視。Fable確認推奨) |
| B: Std薄(△)入力 | 2(G2 price tag・G3 standard deviation) | 0 | 0/2 | T3 行409,437 |
| 参考: E0@G2 / E0@G3(難例22) | 0 / 0〜1 | 0 / 0 | 測れない / 0/(0〜1) | OPUS_REVIEW_04.md:5-6(Std G2 26/26、G3 25〜26/26、Adv 22/22) |

Std誤りでない入力でのAdv NG: A 0/55(Opusの59/60の残りが全てPASS)、B 0/119(正式NGなし)。Bの欠陥1(`run on`)はStdが正のため波及ではない(T3 行426)。Opusの「Std/Adv用法矛盾 G0+E0@G0 4件」はAの「Std誤り入力5件中、波及1・非波及4」と件数が一致するが、内訳は未保存のため**推定**。

## 6. 未判明事項・集計上の限界

- **Opus盲検の個別判定ログが無い**(集計のみ): 59/60のNG行、Std G0 NG2件、G3「25〜26」の未特定1件、Std/Adv矛盾4件の内訳、E0@G2/G3「22」の母集団、薄化判定(G0/G2)。
- **Bの「伝染0」は実行層Sonnetの目視**。独立Judge(kind P/C)・gold・rep2の確認・Productionの5KP/callでの確認なし。Adv出力の再目視(本監査)は同系統で独立性なし。
- **通常KPにgoldが無い**。通常40(T3)・通常6(T2)の「正しい意味」はFable盲検の本文用法判断のみ。
- **PROMPT_SHA256**はresultsに未記録。DEVのE0は1KP/callでProduction(5KP/call)と同一条件ではない。
- **欠損補修**: T3 G3 `draw a line` rep2は再実行(T3 行481、元の出力は不明、行203に断片)。G3の字義0/5は再実行込み。
- **同一KPの再生成**: 60/120出力は独立サンプルでなく、独立KP数はT2 75・T3 60・通算115(難例20はT2・T3で同一KP)。FAIL 3/120(G0)は確定2KP(境界含め3KP)。
- **判定者の差**: Sonnet参考とFable最終は83/360セルで不一致(78セルはSonnetの薄△とFable PASS)。Sonnet FAIL 9に対しFable確定FAIL 6(+境界1)。
- **過去報告の暫定値の残置**: TRIAL_RESULT_02.md:17,38,41,65 / RESULT_PACKET_KPGM7.md:3 / RESULT_PACKET_KPGM8.md:20 に、gold確定前のSonnet基準(E0 78%/E4 86%、G3 96%/G0 85%)が本文として残る(:8の注記のみ)。FABLE_BLIND_RESULT_03.md:18の「G0=3 KP」は境界を含む。
- **分類の幅**: `reach for someone's wallet`は字義訳/所有者誤りの両読みが可能(合計は不変)。`settle at`は確定FAIL合計の外に別掲。
- **本監査の範囲外**: Trial_01・probe-03、Trial_02のE0@prod/E1/E1c/E4(Std glossを入力にしない/別Prompt)、Productionコード・配線。

## Fable確定(2026-10-23、上の推定・暫定表記は残す。詳細=FABLE_VERIFICATION_01.md)

- Std確定FAIL: G0=3(字義訳2[unseen clock×2]+文法・意味関係1[reach])/G2=1(字義訳1[draw a line])/G3=2(文法・意味関係2[apply、reach])。語義誤認・その他・原因不明は各0。`settle at`(G0 rep2)は境界ではなく△(NGではない)に確定。△: G0=1/G2=3/G3=4。
- 「0/120伝染」は分母の誤り。正=誤りgloss入力1件中0件、薄い入力2件中0件。Std誤り→Adv波及は難例1/5(約2割)、通常0/1。「59/60」はOpus確定gold基準、Sonnet暫定は45/60。
- 未判明のまま残す: Opus個別判定ログ無し/Std G3「25〜26/26」の未特定1件/E0@G2・G3「22」母集団の厳密同定/Trial_03 G3 draw a line rep2は欠損補修の再実行出力/DEV E0は1KP/callでProduction(5KP/call)とバイト同一ではない(PROMPT_SHA256未記録)/「伝染0」は実行層目視のみ。

## Fable訂正(2026-10-23、ユーザー指摘反映)
所有者誤りNGと分類した3出力(Trial_03: G0 reach「人の財布」、G3 reach「誰かの財布」、G3 apply「人の研究結果」)は、見出し語(`reach for someone's wallet` / `apply one's findings`)に忠実な訳であり**NGから外す**。「見出し語の人称placeholder不整合(生成器の誤りではない)」として別掲。Std確定NGは G0=2(an unseen clock×2、字義訳)・G2=1(draw a line字義訳)・G3=0。Adv 59/60の唯一のNG(reach rep1 "another person's wallet")も見出し語に忠実で、Std意味生成の誤りに起因するAdv NGは0件。詳細: `FABLE_VERIFICATION_02.md`、見出し語の出所と規定: `HEADWORD_PLACEHOLDER_01.md`。上表・本文の旧分類(所有者誤り、Std誤り→Adv波及1/5)は元記録として残す。
