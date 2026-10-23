# CONSISTENCY_01.md 生成(API 0)
from audit_01_data import *
OUT = Path(__file__).parent
ARMS = ['G0', 'G2', 'G3']
H = set(HARD20)
L = []
w = L.append


def esc(s):
    return str(s).replace('|', '\\|')


# ---- 再計算 ----
cells = []
for n, b in sorted(blind.items()):
    for (arm, rep), (c, s) in sorted(b['byarm'].items()):
        sl, sn = sonnet(b['key'], arm, rep)
        cells.append(dict(arm=arm, rep=rep, n=n, key=b['key'], tier=b['tier'], gloss=s, fable=fable(n, c), sonnet=LBL[sl]))
fc = collections.Counter((x['tier'], x['arm'], x['fable']) for x in cells)
sc = collections.Counter((x['tier'], x['arm'], x['sonnet']) for x in cells)
E0G0 = [r for r in r2 if r['arm'] == 'E0@G0']
n_s_ng = [r for r in E0G0 if flags(e3(r))]
reasons = collections.Counter(f for r in n_s_ng for f in flags(e3(r)))
n30set = set(n30)


def stat(sel):
    return sum(p3(e3(r)) for r in sel), len(sel)


e0_50 = [r for r in r2 if r['arm'] == 'E0@G0' and r['rep'] == 1 and r['key'] in H] + [r for r in r2 if r['arm'] == 'E0@prod' and r['rep'] == 1 and r['key'] in n30set]
arm50 = {a: [r for r in r2 if r['arm'] == a and r['rep'] == 1 and (r['key'] in H or r['key'] in n30set)] for a in ('E1', 'E1c', 'E4')}
gs = {a: [r for r in r2 if r['kind'] == 'G' and r['arm'] == a and r['rep'] == 1] for a in ARMS}
g_ok = {a: sum(gok(g2v(r)) for r in gs[a]) for a in ARMS}
e0g3_hard22 = [r for r in r2 if r['arm'] == 'E0@G3' and r['key'] in H]
e0g3_sum22 = [r for r in r2 if r['arm'] == 'E0@G3' and r['rep'] == 1 and (r['key'] in H or r['key'] in ('behind the scenes', 'think up'))]
e0g2_hard22 = [r for r in r2 if r['arm'] == 'E0@G2' and r['key'] in H]
# T2 G0 hard glosses vs T3 同一文字列
allg = collections.defaultdict(set)
for x in cells:
    allg[(x['key'].lower(), x['gloss'])].add((x['arm'], x['rep'], x['fable']))
k2 = collections.defaultdict(set)
for r in r2:
    k2[r['arm']].add(r['key'].lower())
all2 = set().union(*k2.values())
all3 = set(b['key'].lower() for b in blind.values())

w("# CONSISTENCY_01: 集計の整合性・信頼性(FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_10、API 0・新規生成0・コード変更0)\n")
w("生成=`AUDIT_01/audit_01_build_cons.py`(読み取り専用)。T2=`er112_output/kp_gm_trial_02/`、T3=`er112_output/kp_gm_trial_03/`。\n")
w("## 0. 結論(先頭)\n")
w("1. **過去報告の主要数値は、再計算でほぼ再現できた**(E0 78%/E1 80%/E4 86%、G3 96%/G0 85%、Sonnet参考 FAIL 4/3/2、draw a line 字義 2/5・1/5・0/5)。数字そのものの誤りは見つからなかった。")
w("2. **問題は『数字』ではなく『判定者・基準・母集団が数値ごとに異なる』点**。同じ『合格率』でも、(a)Sonnet暫定Judge(gold確定前) (b)Opus盲検(確定gold) (c)Fable盲検 (d)実行層目視 が混在し、特に **Adv: 同一の60出力がSonnet暫定45/60(75%)・Opus確定59/60(98%)** と14件食い違う。")
w("3. **混在が残る過去報告箇所**: TRIAL_RESULT_02.md:17,38,41,65(『G3 96%/G0 85%』『E0 78%/E4 86%』をgold確定前のまま本文に残置、:8の注記のみで上書きされていない)、RESULT_PACKET_KPGM7.md:3(同)、RESULT_PACKET_KPGM8.md:20(『96% vs 85%』)。")
w("4. **FableのKP単位『G0=3 KP』は境界の`settle at`を含む数**で、出力単位『G0=3(+境界1)』の確定3は2KP。数え方が異なる。")
w("5. **独立KP数と再生成回数**: Trial_02は独立KP 75(難例20+通常55)、Trial_03は60(難例20=T2と同一入力+新規通常40)、両Trial通算の独立KPは115。『60出力』『120出力』は独立サンプル数ではなく、同一KPの再生成・方式違いを含む(§3)。")
w("6. **欠損補修1件(T3 G3 `draw a line` rep2)は再実行であり、元の出力は不明**。集計は再実行出力を使用(選択バイアスなし)。影響範囲=G3の`draw a line`字義0/5(§4)。")
w("7. **個別判定ログが保存されていない判定**: Opus盲検(T2 Std/Adv)の全個別判定。保存は集計のみ。個別の同定にはFable記述と推定を要した(推定は本文で明記)。\n")

w("## 1. 判定者・基準の照合表(どの数字がどの判定者・どの基準か)\n")
w("| 判定者 | 基準 | 対象 | 個別判定の保存 | 備考 |\n|---|---|---|---|---|")
w("| Sonnet暫定Judge(claude-sonnet-5-5) | draft gold(GOLD_LABELS_DRAFT_01)または基準なし。E3: sense_ok/core/single(+over_general)、G: sense_ok/literal/deictic等 | T2 全行(Std 26×arm、Adv 全arm)、T3 gloss(参考値)、`judge/sonnet/cache.jsonl` | **保存あり**(442 id、T2) | gold確定前の暫定。coreを厳しく判定(§2-3) |")
w("| Sol Judge(gpt-6.1-sol) | 同上 | T2 重複行(kappa算出用) | 保存あり(64 id) | kappa 0.23(TRIAL_RESULT_02.md:54) |")
w("| Opus盲検(任意レビュー) | 確定gold(GOLD_LABELS_FINAL_01)。盲検は部分的(OPUS_REVIEW_04.md:11 BE-09) | T2 難例Adv(E0@G0 60等)、Std 26/arm | **集計のみ**(OPUS_REVIEW_04.md:5-8) | 個別NGの同定はFable記述(委任_08 §1、委任_10 §1)に依存 |")
w("| Fable盲検 | 難例=GOLD_LABELS_FINAL_01、通常=本文用法とフレーズ全体の意味 | T3 Std 360出力 | 全セル保存(FABLE_BLIND_RESULT_03.md:7-17、PASS以外のみ列挙) | 最終判定。境界1件あり |")
w("| 実行層Sonnet目視 | 数値基準なし | T3 E0 120説明(通常40×3) | 報告のみ(TRIAL_RESULT_03.md:54)。個別ログなし | 独立Judgeではない |\n")

w("## 2. 過去報告の数値と確定値の対応\n")
w("| # | 過去報告の数値 | 出所 | 判定者・基準 | 本監査の再計算 | 確定/最新の判定 | 差・混在の説明 |\n|---|---|---|---|---|---|---|")
a, b = stat(e0_50)
w("| 1 | E0 78%% / E1 80%% / E4 86%%(Adv PASS3、n=50) | TRIAL_RESULT_02.md:38-41、RESULT_PACKET_KPGM7.md:3 | Sonnet暫定、draft gold、E3 sense_ok&core&single、難例20(rep1)+通常30(rep1) | E0 %d/%d、E1 %d/50、E1c %d/50、E4 %d/50(全て一致) | 難例Advの確定: Opus E0@G0 59/60・E1 58/60・E1c 21/22・E4 21/22(OPUS_REVIEW_04.md:6)。通常30のgoldは無い | **母集団が異なり直接比較不可**。E0の78%%は難例15/20+通常24/30の混合。確定goldでは難例の全armが上限で、E4の+8ptはcore判定のSonnet雑音の範囲(OPUS_REVIEW_04.md:6『Advの差はJudge雑音』)。TRIAL_RESULT_02.md:8-13の0-Aで追記済みだが:38-41の本文は暫定のまま |" % (a, b, stat(arm50['E1'])[0], stat(arm50['E1c'])[0], stat(arm50['E4'])[0]))
w("| 2 | G3 96%% vs G0 85%%(Std、n=26 rep1) | TRIAL_RESULT_02.md:17,65、RESULT_PACKET_KPGM7.md:3、RESULT_PACKET_KPGM8.md:20 | Sonnet暫定 G judge(sense_ok&!literal&!deictic) | G0 %d/26、G2 %d/26、G3 %d/26(一致) | Opus確定: G0 24/26、G2 26/26、G3 25〜26/26(OPUS_REVIEW_04.md:5) | G0の22→24は、Sonnetのdeictic指摘2件(apply・keep someone company)がOpusでは不問だったためと推定(個別ログ無し)。G2のSonnet85%%→Opus100%%。**G3優位はOpusでも残る(G0 -2件)が+4〜8pt**、Sonnet暫定の+11ptより小。さらにTrial_03(Fable)では同等域に縮小 |" % (g_ok['G0'], g_ok['G2'], g_ok['G3']))
w("| 3 | 59/60(Adv E0@G0 難例) | OPUS_REVIEW_04.md:6、TRIAL_RESULT_02.md:9 | Opus盲検、確定gold | Sonnet暫定は同60出力で%d/60(75%%)。不良項目別(複数計上): sense=%d・core=%d・single=%d | Opus 59/60(NGは reach rep1 の1件) | **同一60出力で暫定45と確定59が14件食い違う**。主因=core(研究/vehicles/acceptable等の限定混入)を暫定は不良とし、確定goldの『英語の許容範囲』ではPASS。carry the load rep1,2(字義)はgold確定で字義も許容に。個別の食い違い出力はADV_AUDIT_01.md付表AのSonnet暫定列 |" % (60 - len(n_s_ng), reasons['sense'], reasons['core'], reasons['single']))
w("| 4 | 120件で伝染0 | RESULT_PACKET_KPGM8.md:7、TRIAL_RESULT_03.md:16,54 | 実行層Sonnet目視 | rep1 gloss 120中、Fable盲検でStd誤り=1(G0 an unseen clock)・薄2 | Fable結論(4)『Trial_03 E0引き継ぎ0件』(FABLE_BLIND_RESULT_03.md:20) | **分母は120でなく1**(ADV_AUDIT_01.md §4)。独立Judge無し・gold無し |")
w("| 5 | FAIL G0=3 / G2=1 / G3=2(各120) | FABLE_BLIND_RESULT_03.md:18、RESULT_PACKET(UDR #171等) | Fable盲検最終 | 出力単位: G0=3(+境界1)、G2=1、G3=2(一致) | 同左 | **KP単位『G0=3 KP』は境界settle atを含む**。確定のみなら2KP。境界を含む出力は4 |")
w("| 6 | Sonnet参考 FAIL G0 4 / G2 3 / G3 2(全体)、難例 1/1/2、通常 3/2/0 | TRIAL_RESULT_03.md:12,27-29、RESULT_PACKET_KPGM8.md:6 | Sonnet参考(3値) | 全体 %d/%d/%d、難例 %d/%d/%d、通常 %d/%d/%d(一致) | Fable: 全体 3(+1)/1/2、難例 %d/%d/%d、通常 %d(+1)/%d/%d | Sonnetの『G0固有のFAIL: 字義訳(unseen clock)と誤用(settle at)』『G2/G3のFAIL: center stage・run on』のうち、Fableは center stage・run on をPASS、settle at を境界。**Sonnet FAILとFable FAILは一致しない**(STD_AUDIT_01.md §2) |" % (
    sc[('hard', 'G0', 'FAIL')] + sc[('normal', 'G0', 'FAIL')], sc[('hard', 'G2', 'FAIL')] + sc[('normal', 'G2', 'FAIL')], sc[('hard', 'G3', 'FAIL')] + sc[('normal', 'G3', 'FAIL')],
    sc[('hard', 'G0', 'FAIL')], sc[('hard', 'G2', 'FAIL')], sc[('hard', 'G3', 'FAIL')],
    sc[('normal', 'G0', 'FAIL')], sc[('normal', 'G2', 'FAIL')], sc[('normal', 'G3', 'FAIL')],
    fc[('hard', 'G0', 'FAIL')], fc[('hard', 'G2', 'FAIL')], fc[('hard', 'G3', 'FAIL')],
    fc[('normal', 'G0', 'FAIL')] - 1, fc[('normal', 'G2', 'FAIL')], fc[('normal', 'G3', 'FAIL')]))
w("| 7 | 薄△率(通常40) G0 28%% / G2 25%% / G3 29%% | TRIAL_RESULT_03.md:13,28、RESULT_PACKET_KPGM8.md:6 | Sonnet参考 | Sonnet 通常80出力中の薄△: G0 %d・G2 %d・G3 %d | Fable 通常40の△: G0 %d・G2 %d・G3 %d(全120中△は G0 0/G2 3/G3 4) | **薄△の基準が判定者で大きく異なる**(Sonnetは広く付与=TRIAL_RESULT_03.md:70。Fableは7出力のみ)。Sonnetの率を方式間比較に使うのは可、絶対値は不可 |" % (
    sc[('normal', 'G0', 'THIN')], sc[('normal', 'G2', 'THIN')], sc[('normal', 'G3', 'THIN')], fc[('normal', 'G0', 'THIN')], fc[('normal', 'G2', 'THIN')], fc[('normal', 'G3', 'THIN')]))
w("| 8 | draw a line 字義 G0 2/5・G2 1/5・G3 0/5 | FABLE_BLIND_RESULT_03.md:19、TRIAL_RESULT_03.md:13,45 | Fable(T3)+gold(T2)の合算 | 厳密形『線を引く』G0 2・G2 0・G3 0、変種『はっきりと線を引く』G2 1(STD_AUDIT_01.md §4) | 同左 | 一致。ただし**G0の2件は全てT2、G2の1件は全てT3**。T3単体ではG0 0/2・G2 1/2。『Sonnet参考値』(TRIAL_RESULT_03.md:13)の記述だが実際はFable判定と同結論 |")
w("| 9 | Adv E0@G2/G3『22/22』 | OPUS_REVIEW_04.md:6、TRIAL_RESULT_02.md:9 | Opus盲検 | 難例22(20+draw a line rep2,3)でSonnet暫定PASS3: E0@G2 %d/22・E0@G3 %d/22。summary_02.json(E0@G2 19/22・E0@G3 17/22)は『難例20+通常2KP』の別母集団(再計算 %d/22) | Opus 22/22(内訳未記録) | **Opusの22とsummary_02.jsonの22は母集団が異なる可能性**(Opus側の内訳が未記録のため確定不能)。TRIAL_RESULT_02.md:39(E0@G2 19/22 / E0@G3 17/22)はsummary_02.json基準 |" % (stat(e0g2_hard22)[0], stat(e0g3_hard22)[0], stat(e0g3_sum22)[0]))
w("| 10 | Std/Adv用法矛盾 G0+E0@G0 4件・G3+E0@G3 0件 | OPUS_REVIEW_04.md:8 | Opus盲検、難例 | 個別未保存。Sonnet暫定の矛盾(kind P)はG0 3/20(TRIAL_RESULT_02.md:§3) | Opus 4件 | 暫定3→確定4で増加(基準違い)。ADV_AUDIT_01.md §4の『Std誤り入力5件中、NG1+非波及4』とOpus 4件の一致は**推定** |")
w("| 11 | Std G0 24/26・G2 26/26・G3 25〜26/26 | OPUS_REVIEW_04.md:5(委任_08) | Opus盲検、確定gold | - | 同左 | G3の『25〜26』は未確定(個別未特定)。G0 NG2件の同定は推定(STD_AUDIT_01.md §5) |")
w("| 13 | 『Adv説明Promptは現行維持で十分(Opus盲検・Trial_03 E0引き継ぎ0件・矛盾0件)』 | FABLE_BLIND_RESULT_03.md:20 結論(4) | 根拠が3種(Opus難例59/60、T3目視の引き継ぎ0件、T3目視の矛盾0件) | 3根拠は判定者・母集団・基準が全て異なる | - | **Opusが同じ報告内で『Std/Adv矛盾 G0+E0@G0 4件』を報告**(OPUS_REVIEW_04.md:8)。『矛盾0件』はG3+E0@G3(Opus)とT3通常40(目視、正式Judge無し)に限る。T3の『矛盾0』には独立確認が無い |")
w("| 12 | E0 / Adv 自己一致 約65%(E0@G0 13/20、E1 12/20) | TRIAL_RESULT_02.md:45 | Sonnet暫定 | - | Opus確定では上限付近のため無意味化 | 暫定の自己一致は暫定基準(core)に依存 |\n")
w("(Fableのユーザー向け報告で使った数値について: 委任_10 §2 T-3が列挙した6項目[#1,#2,#3,#4,#5,#8]は上表のとおり。Fableのユーザー向け報告そのものの文面はrepo内に保存されておらず、原文との逐語照合は**未確認**。)\n")

w("### 2-1. #3 の補足: Sonnet暫定45/60とOpus確定59/60の差(同一の60出力)\n")
w("| 項目 | 件数 |\n|---|---|")
w("| Sonnet暫定 PASS3 | %d |" % (60 - len(n_s_ng)))
w("| Sonnet暫定 不合格 | %d(うちOpus確定でもNG: 1=reach rep1) |" % len(n_s_ng))
w("| 不良項目別(複数計上) | sense_ok=0: %d / core=0: %d / single=0: %d |" % (reasons['sense'], reasons['core'], reasons['single']))
w("| 暫定→確定でNG→PASS | %d |" % (len(n_s_ng) - 1))
w("| 確定→暫定でPASS→NG | 0 |\n")
w("暫定不良の全出力はADV_AUDIT_01.md付表A『Sonnet暫定』列に出力ごとに表示。\n")

w("### 2-2. #2 の補足: Trial_02 G0 難例glossをTrial_03のFable盲検と同一文字列で照合\n")
w("| KP | T2 G0 gloss | T3で同一文字列が出た出力(arm,rep,Fable判定) |\n|---|---|---|")
for r in sorted([r for r in r2 if r['kind'] == 'G' and r['arm'] == 'G0' and r['rep'] == 1], key=lambda r: r['key']):
    hit = sorted(allg.get((r['key'].lower(), r['gloss']), []))
    w("| %s | %s | %s |" % (esc(r['key']), esc(r['gloss']), '; '.join('%s/rep%d=%s' % h for h in hit) if hit else '(T3に同一文字列なし=個別未判定)'))
w("")

w("## 3. 独立KP数と再生成回数(正確な区別)\n")
w("| Trial | 項目 | 独立KP数 | 方式×rep | 出力数(行) | 備考 |\n|---|---|---|---|---|---|")
w("| T2 | Std G0 / G2 / G3 | 26(難例20+通常6)。draw a lineのみ3rep | 各3方式×rep1(+draw a line rep2,3) | 各28行 | 判定対象n=26はrep1。Sol arm(G0sol 14行、G2sol 3行)は難例の一部のみ |")
w("| T2 | Adv E0@G0 | 20(難例) | rep1〜3 | 60 | gloss入力は22サンプル(§ADV_AUDIT_01) |")
w("| T2 | Adv E0@G2 / E0@G3 | 各26(難例20+通常6) | rep1(+draw a line rep2,3) | 各28 | |")
w("| T2 | Adv E0@prod | 55(通常) | rep1 | 55 | Production gloss入力。今回の対象外 |")
w("| T2 | Adv E1 / E1c / E4 | 75 / 75 / 50(難例20+通常) | rep1(難例は一部rep1〜3) | 115 / 77 / 52 | |")
w("| T2 | 全体 | **%d**(難例20+通常55) | | 516行 | |" % len(all2))
w("| T3 | Std G0/G2/G3 | 60(難例20=T2と同一入力・同一KP+新規通常40) | 各3方式×rep1,2 | 各120(計360) | 難例20はT2と**同一KP・同一入力文**だが**新規生成**(T2出力の再利用なし) |")
w("| T3 | Adv E0@G0/G2/G3 | 40(通常のみ) | rep1のみ | 各40(計120) | gloss入力はStd rep1のみ |")
w("| T3 | 全体 | 60 | | 480行(有効)+断片1(行203) | |")
w("| T2∪T3 | 通算独立KP | **%d**(T2 %d + T3新規 %d。重複 %d=難例20) | | | |\n" % (len(all2 | all3), len(all2), len(all3 - all2), len(all2 & all3)))
w("用語: 『60出力』=難例20KP×3回(T2 E0@G0)、『120出力』=通常40KP×3方式×1回(T3 E)または60KP×2rep(T3 Std 各方式)。いずれも**独立サンプルではなく、同一KPが複数回・複数方式で出現する**。たとえば T3 Std G0 120出力=60KP×2rep。したがって『FAIL 3/120』の3は独立3KPではなく、KP単位では2KP(確定)。\n")

w("## 4. 重複・再実行・欠損補修の集計への影響\n")
w("| 事象 | 事実 | 集計への影響 |\n|---|---|---|")
w("| T3 results.jsonl 行203 | JSONとして不正な断片(`_cost_jpy\": 0.0315, \"n_in_call\": 1}`)。元の行の同定は断片自体からは不能(コスト0.0315円のみ)。『G3 draw a line rep2』と報告されているが、断片からは確認不能 | 有効行=480(G 360=60KP×3方式×2rep、E 120)で欠落なし。断片は集計に入らない |")
w("| T3 G3 `draw a line` rep2 の再実行 | results.jsonl 行481(`call_cost_jpy` 0.061円、gloss「区別をはっきりさせる」、candidates=[一線を引く,区別をはっきりさせる,境界をはっきりさせる])。TRIAL_RESULT_03.md:§6『同入力・同Promptで1回だけ再実行(出力を見て選んだ再実行ではない)』 | **元の出力は不明**。G3 draw a line 字義0/5 の5のうち1は再実行出力。選択バイアスは無い(1回のみ・結果依存でない)が、元の出力が字義であった可能性を排除できない=G3 0/5 は『再実行込みの0/5』 |")
w("| 台帳の断片補正 | T3 paid_calls.jsonl 行278(G2、cost 0.1446円の補正行)。T2 paid_calls.jsonl 行358(断片2を除去、0.0251円補正) | 費用の合計のみに影響。results.jsonlの出力数・判定には無関係 |")
w("| T2 results.jsonl | 516行・不正行0・(kind,arm,key,rep)の重複0 | なし |")
w("| T3 results.jsonl | 有効480行・(kind,arm,key,rep)の重複0 | なし |")
w("| 同一文字列の複数出力 | 例: G0 `an unseen clock`「目に見えない時計」はrep1・rep2とも同一文字列。Fable盲検は出力ごとにFAIL(2件)としてカウント | 『FAIL G0=3』の内訳は異なる誤り文字列2種(人の財布×1、目に見えない時計×2)。独立な誤りの種類としては2。出力単位で数えるのが妥当だが、率の分母は『独立なサンプル』ではない |")
w("| Sonnet Judgeの重複排除 | 同一(key,sent,gloss)を1行に集約(T3 158行、T2 442 id)。出力単位への展開はdetail表で実施 | 出力単位集計に影響なし(detail表は出力ごと) |")
w("| T2 `draw a line` rep2,3 の後追加 | results.jsonl 行80-85(G)・89-101(Sol)・103,113,127等(E0@G0)・483-486(E0@G2/E0@G3)(追加rep) | `draw a line`のみ3rep。KP単位集計(n=26/50)はrep1のみ使用 |")
w("| T3難例20のT2再利用 | なし(新規生成) | T2とT3の難例Stdは独立サンプル。ただし**同一KP・同一文**なので、同KPの結果は2Trialで相関しうる |\n")

w("## 5. 推定にとどまるもの・不明なもの(一覧)\n")
w("| 項目 | 状態 | 理由・根拠 |\n|---|---|---|")
w("| Opus Std G0 NG2件の同定(draw a line・reach) | **推定**(draw a lineは確実) | 個別ログ無し。OPUS_REVIEW_04.md:5『難例の誤り2種を解消』+委任_08 §1:11の記述 |")
w("| Opus Std G3『25〜26』の未特定1件 | **不明** | 個別ログ無し。Sonnet暫定の指摘はapplyのみ(候補) |")
w("| Opus Adv 59/60のNG行の同定(reach rep1) | Fable記述(委任_10 §1)に依存。実行層gold照合でも該当1件 | 個別ログ無し |")
w("| Opus『Std/Adv矛盾 G0 4件』の内訳 | **不明**(推定: draw a line rep1,3 と reach rep2,3) | 個別ログ無し。Std誤り入力5件中のAdv非波及4件と件数一致 |")
w("| Opus E0@G2/E0@G3『22』の母集団 | **不明** | 難例20+draw a line rep2,3 か 難例20+通常2KP か未記録 |")
w("| T3 E0の『伝染0』の独立確認 | **未実施** | 独立Judge(kind P/C)未実施。ADV_AUDIT_01.md §5 |")
w("| `an unseen clock` G0のAdv出力が字義を引き継いだか | 実行層目視で『引き継がず』。**Fable確認推奨** | \"hidden sense of time\"の『sense of time』は『時計』の抽象化であり、正しい意味(時間の仕組み)に近いが、G2/G3の\"hidden process\"より曖昧 |")
w("| Std薄(△)の方式別評価(T2) | 未判定 | Opusは薄化をG3の5件のみ列挙。G0/G2の個別薄判定なし |")
w("| 通常KPの『正しい意味』 | goldが無い | 通常KP(T3の40、T2の6)の基準=Fable盲検の本文用法判断 |")
w("| PROMPT_SHA256のresults記録 | 無し | ADV_AUDIT_01.md §1。Prompt同一性は実行時にimportされたコードに依存 |")
w("| 費用 | 本監査はAPI 0。Trial費用の再集計はせず | - |\n")

w("## 6. 規則整合の注記\n")
w("- 本監査は集計・報告のみで、既存script・Prompt・Production・er112コードの変更0、新規生成0、API呼出0。新規ファイルは`AUDIT_01/`配下の読み取り専用集計script(audit_01_*.py)とmdのみ。")
w("- 『古い暫定Judge判定と確定判定を混在させない』要請に対し、本監査の各表は判定者・基準を列に明記した。TRIAL_RESULT_02.md:17,38,41,65 等の暫定値本文は既存文書であり、本監査では書き換えていない(§0-3に該当箇所を列挙)。")
open(OUT / 'CONSISTENCY_01.md', 'w', encoding='utf-8').write('\n'.join(L))
print('written', len(L))
