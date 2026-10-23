# STD_AUDIT_01.md 生成(API 0)
from audit_01_data import *
OUT = Path(__file__).parent
ARMS = ['G0', 'G2', 'G3']


def esc(s):
    return str(s).replace('|', '\\|')


# ---- T03 全360出力の出力単位データ ----
cells = []   # dict(arm, rep, n, key, tier, typ, fam, gloss, line, fable, sonnet)
for n, b in sorted(blind.items()):
    for (arm, rep), (c, s) in sorted(b['byarm'].items()):
        r = gl[(arm, b['key'].lower(), rep)]
        sl, sn = sonnet(b['key'], arm, rep)
        cells.append(dict(arm=arm, rep=rep, n=n, c=c, key=b['key'], tier=b['tier'], typ=b['typ'], fam=b['fam'], gloss=s,
                          line=r['_line'], fable=fable(n, c), sonnet=LBL[sl], sgloss=sn))
assert len(cells) == 360
cnt = collections.Counter((x['arm'], x['fable']) for x in cells)
# NG分類(Fable最終判定を正とする。分類はFable記述に従い、記述が無い項目は実行層の推定と明記)
CLS = {
    (15, 'D'): ('字義訳NG', 'Fable記述(FABLE_BLIND_RESULT_03.md:20結論(2))が「人の財布」を比喩表現の字義訳型に分類。盗む読み(:9)'),
    (23, 'B'): ('字義訳NG', 'Fable記述「目に見えない時計」(字義)(:10)'),
    (23, 'D'): ('字義訳NG', 'Fable記述「目に見えない時計」(字義)(:10)'),
    (5, 'D'): ('字義訳NG', 'Fable記述「はっきりと線を引く」(字義)(:8)'),
    (1, 'F'): ('文法・意味関係NG', 'Fable記述「itsは自分の。所有者誤り」(:7)'),
    (15, 'E'): ('文法・意味関係NG', "実行層分類(推定): Fableは「盗む読み」(:9)とのみ記述。:20結論(2)は『G2/G3は…所有者誤り…』と述べる。someone'sを他人と解した所有者の取り違え。※G0の同型「人の財布」(字義訳)との分類不一致あり(感度参照)"),
    (50, 'F'): ('語義誤認NG', 'Fable記述「市場用語『取引を終える』が落ちる」(:11)。複数語義(落ち着く/取引を終える)から本文に合わない語義を選択'),
}
CLASSES = ['字義訳NG', '語義誤認NG', '文法・意味関係NG', 'その他NG', '原因不明']
fails = [x for x in cells if x['fable'] == 'FAIL']
assert len(fails) == 7
for x in fails:
    x['cls'], x['clsbasis'] = CLS[(x['n'], x['c'])]
border = [x for x in fails if x['key'] == 'settle at']   # 境界(FAIL寄り)
firm = [x for x in fails if x['key'] != 'settle at']
assert len(border) == 1 and len(firm) == 6
thin = [x for x in cells if x['fable'] == 'THIN']
assert len(thin) == 7
snc = collections.Counter((x['arm'], x['sonnet']) for x in cells)
diff = [x for x in cells if x['fable'] != x['sonnet']]
mat = collections.Counter((x['fable'], x['sonnet']) for x in cells)
tab = {a: collections.Counter(x['cls'] for x in firm if x['arm'] == a) for a in ARMS}
tot = {a: sum(tab[a].values()) for a in ARMS}
assert tot == {'G0': 3, 'G2': 1, 'G3': 2}

L = []
w = L.append
w("# STD_AUDIT_01: Standard日本語意味のNG原因別内訳(FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_10、API 0・新規生成0・コード変更0)\n")
w("生成=`AUDIT_01/audit_01_build_std.py`。Trial_03のFable盲検最終判定は `TRIAL_03/FABLE_BLIND_RESULT_03.md:7-17`(blind表の行#・列A〜F)を、`fable_blind_std_03_key.json`でarm/repに復元して適用(復元後のgloss文字列がresults.jsonlと360/360一致することを確認)。行番号はT3=`er112_output/kp_gm_trial_03/results.jsonl`、T2=`er112_output/kp_gm_trial_02/results.jsonl`の1始まり行。\n")

w("## 0. 結論(先頭)\n")
w("1. **Trial_03(60 KP×各方式2回=各120出力)のFable最終判定: 確定FAIL G0=3・G2=1・G3=2(各120中。2.5% / 0.8% / 1.7%)。** G0のみ『境界(FAIL寄り)』が別に1件(`settle at` rep2)あり、含めるとG0=4。")
w("2. **原因別(確定FAILの合計=分類合計): G0=字義訳3、G2=字義訳1、G3=文法・意味関係2。** 語義誤認・その他・原因不明は確定FAILでは0(境界のG0 `settle at`が語義誤認)。ただし `reach for someone's wallet` の分類は字義訳/所有者誤りの両読みが可能で、感度を§1に別掲。")
w("3. **薄い(△)は別集計: G0=0、G2=3、G3=4**(計7出力)。NGではない。")
w("4. `draw a line`の厳密形「線を引く」の発生は **Trial_02+03の各5出力中: G0=2、G2=0、G3=0**。変種「はっきりと線を引く」(同じく字義でNG)がG2=1(Trial_03 rep2)。合計の字義NGは G0 2/5・G2 1/5・G3 0/5(Fable集計と一致)。Trial_03単体ではG0は2/2が『一線を引く』(慣用義・許容)で、G0の字義2件はいずれもTrial_02。")
w("5. Fable最終判定とSonnet参考判定の不一致は360出力中 %d セル(§2)。うち78セルはSonnetが薄△・FableがPASSの組で、薄△の基準差が主因。Sonnet FAIL %d(G0 %d・G2 %d・G3 %d)に対しFable確定FAIL %d(+境界1)。" % (len(diff), snc[('G0', 'FAIL')] + snc[('G2', 'FAIL')] + snc[('G3', 'FAIL')], snc[('G0', 'FAIL')], snc[('G2', 'FAIL')], snc[('G3', 'FAIL')], len(firm)))
w("6. Trial_02 Std(難例20+通常6、rep1、n=26/arm)は個別のOpus判定ログが無い。Opus集計: G0 24/26(NG2)・G2 26/26・G3 25〜26/26。G0のNG2件は draw a line「線を引く」(確実)と reach「人の財布に手を伸ばす」(推定)で、いずれも字義訳型(§5)。\n")

w("## 1. Trial_03 Std: NG原因別内訳(Fable最終判定を正とする、重複なし)\n")
w("| NG分類 | G0 | G2 | G3 |\n|---|---|---|---|")
for c in CLASSES:
    w("| %s | %d | %d | %d |" % (c, tab['G0'][c], tab['G2'][c], tab['G3'][c]))
w("| **確定FAIL合計(=分類合計)** | **%d** | **%d** | **%d** |" % (tot['G0'], tot['G2'], tot['G3']))
w("| 境界(FAIL寄り、上記合計の外・語義誤認) | 1 | 0 | 0 |")
w("| 境界を含む合計 | 4 | 1 | 2 |")
w("| 確定FAIL率(÷120) | %.1f%% | %.1f%% | %.1f%% |" % tuple(100 * tot[a] / 120 for a in ARMS))
w("| KP単位のFAIL含有KP数(確定のみ / 境界含む) | 2 / 3 | 1 / 1 | 2 / 2 |\n")
w("注: FABLE_BLIND_RESULT_03.md:18 の『KP単位でFAILを含むKP: G0=3 KP(reach、unseen clock、settle at)』は**境界の`settle at`を含む**数。出力単位の『G0=3(+境界1)』と数え方が異なる(出力単位の確定3は2KP、境界を含めると4出力・3KP。CONSISTENCY_01.md参照)。\n")
w("**感度(分類のゆれ)**: `reach for someone's wallet`を所有者誤り(文法・意味関係)として分類した場合 G0=字義訳2+文法・意味関係1、G2=字義訳1、G3=文法・意味関係2。G3の `reach`「誰かの財布」を字義訳とした場合 G3=字義訳1+文法・意味関係1。いずれも確定FAIL合計は不変(3/1/2)。\n")
w("### 1-1. 確定FAIL・境界の全出力(分類つき)\n")
w("| arm/rep | KP(型/X-Z) | 日本語出力 | T3行 | 分類 | 分類の根拠 |\n|---|---|---|---|---|---|")
for x in sorted(fails, key=lambda x: (x['arm'], x['key'], x['rep'])):
    cls = x['cls'] + ('(境界・FAIL寄り)' if x in border else '')
    w("| %s/rep%d | %s(%s/%s) | %s | %d | %s | %s |" % (x['arm'], x['rep'], esc(x['key']), x['typ'], x['fam'], esc(x['gloss']), x['line'], cls, esc(x['clsbasis'])))
w("\n### 1-2. 薄い(△)の別集計(NGではない。Fable判定)\n")
w("| 方式 | 薄(△)出力数 | 一覧(KP/rep/日本語出力) |\n|---|---|---|")
for a in ARMS:
    t = [x for x in thin if x['arm'] == a]
    w("| %s | %d | %s |" % (a, len(t), '; '.join('%s rep%d「%s」' % (x['key'], x['rep'], x['gloss']) for x in sorted(t, key=lambda x: (x['key'], x['rep']))) or '-'))
w("")
w("| 方式 | PASS | 薄(△) | 確定FAIL | 境界 | 計 |\n|---|---|---|---|---|---|")
for a in ARMS:
    w("| %s | %d | %d | %d | %d | 120 |" % (a, cnt[(a, 'PASS')], cnt[(a, 'THIN')], tot[a], 1 if a == 'G0' else 0))
w("")

w("## 2. Fable最終判定 vs Sonnet参考判定の差(Trial_03、360出力)\n")
w("| Fable＼Sonnet | PASS | THIN(薄△) | FAIL |\n|---|---|---|---|")
for f in ('PASS', 'THIN', 'FAIL'):
    w("| %s | %d | %d | %d |" % (f, mat[(f, 'PASS')], mat[(f, 'THIN')], mat[(f, 'FAIL')]))
w("\n方式別(境界はFable側FAILに含む):\n")
w("| 方式 | Sonnet PASS/薄/FAIL | Fable PASS/薄/FAIL |\n|---|---|---|")
for a in ARMS:
    w("| %s | %d/%d/%d | %d/%d/%d |" % (a, snc[(a, 'PASS')], snc[(a, 'THIN')], snc[(a, 'FAIL')], cnt[(a, 'PASS')], cnt[(a, 'THIN')], cnt[(a, 'FAIL')]))
w("\n不一致 %d セル(Fable PASSでSonnetがTHIN/FAIL: %d、FableがTHIN/FAILでSonnetがPASS: %d、その他: %d)。FableがFAILでSonnetがFAIL以外は draw a line G2 rep2(Sonnet薄)の1件。SonnetがFAILでFableがFAIL以外は center stage G2 rep1「注目の的になる」(Fable PASS)・run on G2 rep2「～に沿って動く」(Fable PASS)・reach G2 rep2「人が支払いを覚悟する」(Fable薄△)の3件。\n" % (
    len(diff), sum(1 for x in diff if x['fable'] == 'PASS'), sum(1 for x in diff if x['sonnet'] == 'PASS'),
    sum(1 for x in diff if x['fable'] != 'PASS' and x['sonnet'] != 'PASS')))
w("### 2-1. 判定が食い違った全セル(一致しているセルは付表)\n")
w("| KP | arm/rep | 日本語出力 | Fable | Sonnet | T3行 |\n|---|---|---|---|---|---|")
for x in sorted(diff, key=lambda x: (x['fable'] == 'PASS', x['key'], x['arm'], x['rep'])):
    w("| %s | %s/rep%d | %s | %s | %s | %d |" % (esc(x['key']), x['arm'], x['rep'], esc(x['gloss']), x['fable'] + ('(境界)' if x in border else ''), x['sonnet'], x['line']))
w("")

w("## 3. 各NGの実例(ユーザー§3)\n")
CORR = {
    "reach for someone's wallet": ("本文の用法: 音量ボタンより先に、自分(you)の財布を出して支払う/買う気になる、の意。figurative-literal境界", "gold(GOLD_LABELS_FINAL_01.md reach行): 『(人が)お金を払おうとして財布に手を伸ばす/財布を出す』。不可=『盗む』解釈"),
    'an unseen clock': ("本文の用法: コーヒーの値札にも、(他とは別に)表からは見えない独自の時間の流れ・仕組みがある、の意(比喩)。normal KPなのでgold無し", "Fable PASS例(同KPの他出力): 「表には見えない時間の仕組み」「見えないところで時を刻む仕組み」"),
    'draw a line': ("本文の用法: 言葉が『その線(許容/不許容の区別)』をはっきり示す、の意(慣用・figurative)", "gold確定(GOLD_LABELS_FINAL_01.md末尾『Fable確定』): 許容=一線を引く/区別をはっきりさせる/線引きをする/境界をはっきりさせる。不可=線を引く/境界線を引く(描く動作)"),
    "apply one's findings": ("本文の用法: 『その研究(its)の知見を日常の悪意や退屈へ直接応用することはできない』。one'sは不定の人称(本文はits)", "gold: 『(自分の/研究の)結果・知見を(実際の場面に)当てはめる/応用する』"),
    'settle at': ("本文の用法: 市場用語。『Brent rose 9.59% and settled at $83.30』=終値が83.30ドルで取引を終えた", "Fable PASS例: 「～で取引を終える」(G0 rep1、G2・G3の全出力)。誤り=一般義「落ち着く」"),
}
WHY = {
    "reach for someone's wallet": "NG理由: someone'sを『他人の財布』と取り、盗む/他人の財布に手を伸ばす読みになる(本文は自分の財布を出す意味)。G0 rep1「人の財布に手を伸ばす」・G3 rep1「誰かの財布に手を伸ばす」が該当。G0 rep2「誰かが自分の財布に手を伸ばす」・G2 rep1「人が自分の財布に手を伸ばす」・G3 rep2「財布に手を伸ばす」はPASS。G2 rep2「人が支払いを覚悟する」は動作が消え意訳=薄△。",
    'an unseen clock': "NG理由: 比喩(見えない時間の仕組み)を字義の『時計』で訳し、意味が伝わらない。G0のみ2/2で発生(rep1・rep2とも同一文字列)。G2・G3は『仕組み』『流れ』へ言い換えPASS。",
    'draw a line': "NG理由: G2 rep2「はっきりと線を引く」は『描く動作』の字義訳(『はっきり』を足しても描く動作)。他の5出力は慣用義でPASS。",
    "apply one's findings": "NG理由: G3 rep1「人の研究結果を当てはめる」はone's/its(自分の・その研究の)を『人の』と他人に取る所有者誤り。他の5出力は『自分の研究結果』でPASS。",
    'settle at': "NG理由(境界・FAIL寄り): G0 rep2「～で落ち着く」は市場用語『取引を終える』が落ち、一般義『落ち着く』を選択=語義誤認。G0 rep1・G2・G3の全出力は『取引を終える』でPASS。",
}
order = [("reach for someone's wallet", 'reach'), ('an unseen clock', 'unseen'), ('draw a line', 'draw'), ("apply one's findings", 'apply'), ('settle at', 'settle')]
for k, tag in order:
    b = [b for b in blind.values() if b['key'].lower() == k][0]
    w("### 3-%s: `%s`(%s/%s)\n" % (tag, b['key'], b['typ'], b['fam']))
    w("- 本文: \"%s\"" % b['sent'])
    w("- %s" % CORR[k][0])
    w("- 正しい意味: %s" % CORR[k][1])
    w("- 全6出力(Fable判定/Sonnet参考):\n")
    w("| arm/rep | 日本語出力 | Fable | Sonnet | T3行 |\n|---|---|---|---|---|")
    for x in sorted([x for x in cells if x['key'].lower() == k], key=lambda x: (x['arm'], x['rep'])):
        w("| %s/rep%d | %s | %s | %s | %d |" % (x['arm'], x['rep'], esc(x['gloss']), x['fable'] + ('(境界)' if x in border else ''), x['sonnet'], x['line']))
    w("")
    w("- " + WHY[k])
    w("- 発生状況(確定FAIL): " + ', '.join('%s=%d' % (a, sum(1 for x in firm if x['arm'] == a and x['key'].lower() == k)) for a in ARMS) + (" ／ 境界: G0=1" if k == 'settle at' else ""))
    w("")

w("## 4. `draw a line`(ユーザー指定項目): Trial_02(3rep)+Trial_03(2rep)\n")


def lit_kind(g):
    if g == '線を引く':
        return '厳密形「線を引く」(字義NG)'
    if g.endswith('線を引く') and g != '一線を引く':
        return '変種(字義NG)'
    return '-'


rowsD = []
for r in r2:
    if r['kind'] == 'G' and r['key'] == 'draw a line':
        rowsD.append(('T2', r['arm'], r['rep'], r['gloss'], r['_line'], None))
for x in cells:
    if x['key'] == 'draw a line':
        rowsD.append(('T3', x['arm'], x['rep'], x['gloss'], x['line'], x['fable']))
w("| 試行 | arm | rep | 日本語出力 | 『線を引く』系 | 判定 | 行 |\n|---|---|---|---|---|---|---|")
for t, a, rep, g, ln, fv in sorted(rowsD, key=lambda z: (z[1], z[0], z[2])):
    jd = fv if fv else ('NG(gold不可)' if lit_kind(g) != '-' else 'OK(gold内。実行層照合)')
    w("| %s | %s | %d | %s | %s | %s | %d |" % (t, a, rep, esc(g), lit_kind(g), jd, ln))
w("")
w("| arm | 出力数(T2 3+T3 2) | 厳密形「線を引く」 | 変種(はっきりと線を引く等) | 字義NG計 | 内訳 |\n|---|---|---|---|---|---|")
for a in ARMS:
    gg = [(t, g) for (t, aa, rep, g, ln, fv) in rowsD if aa == a]
    strict = sum(1 for t, g in gg if lit_kind(g).startswith('厳密'))
    var = sum(1 for t, g in gg if lit_kind(g).startswith('変種'))
    w("| %s | %d | %d | %d | %d | T2=%d, T3=%d |" % (a, len(gg), strict, var, strict + var,
        sum(1 for t, g in gg if t == 'T2' and lit_kind(g) != '-'), sum(1 for t, g in gg if t == 'T3' and lit_kind(g) != '-')))
w("\n参考(T2のみのSolモデル2arm、各3rep): 字義NG G0sol=0(線引きをする×2・境界をはっきりさせる=gold許容)、G2sol=0。『境界線を引く』の発生は0回(全出力に無し)。")
w("注: G3 T3 rep2(T3 行481)は欠損補修の再実行出力(CONSISTENCY_01.md)。補修前の元出力は不明。\n")

w("## 5. Trial_02 Std(難例20+通常6、rep1、n=26/arm): Opus盲検を正として\n")
w("**制約: Opus盲検の個別判定ログはrepoに無い。** 保存されているのは集計(OPUS_REVIEW_04.md:5-6,8: G0 24/26・G2 26/26・G3 25〜26/26、薄化指摘5件)と、Fable記述(委任_08 §1:11「G2・G3とも難例の誤り(draw a line字義、reach for someone's wallet『人の財布』=盗む読み)を解消」、OPUS_REVIEW_04.md:5「難例の誤り2種を解消」)のみ。個別NGの同定は下記の通り推定を含む。\n")
sn = {}
for a in ARMS:
    rr = sorted([r for r in r2 if r['kind'] == 'G' and r['arm'] == a and r['rep'] == 1], key=lambda r: r['key'])
    assert len(rr) == 26
    sn[a] = [(r, g2v(r)) for r in rr]
w("| 方式 | n | Opus PASS | Opus NG | NG分類(Opus基準) | Sonnet暫定 PASS | Sonnet暫定NG |\n|---|---|---|---|---|---|---|")
w("| G0 | 26 | 24 | 2 | 字義訳NG 2(draw a line「線を引く」=確実／reach「人の財布に手を伸ばす」=推定) | %d | %d |" % (sum(gok(v) for r, v in sn['G0']), sum(not gok(v) for r, v in sn['G0'])))
w("| G2 | 26 | 26 | 0 | - | %d | %d |" % (sum(gok(v) for r, v in sn['G2']), sum(not gok(v) for r, v in sn['G2'])))
w("| G3 | 26 | 25〜26(未確定) | 0〜1 | 0件なら-、1件なら**原因不明**(個別未特定。Sonnet暫定はapply「自分の研究結果を応用する」のみ指摘) | %d | %d |" % (sum(gok(v) for r, v in sn['G3']), sum(not gok(v) for r, v in sn['G3'])))
w("\n分類合計との一致: G0 字義訳2=NG2、G2 0=0、G3 0〜1(原因不明1が入る場合のみ1)。\n")
w("### 5-1. Sonnet暫定(gold確定前・draft gold)で不合格とされた全出力(Opusとの差)\n")
w("| 方式 | KP | 日本語出力 | Sonnet暫定の指摘 | Opus(個別未保存、集計・Fable記述からの推定) | T2行 |\n|---|---|---|---|---|---|")
OPUSNG = {('G0', 'draw a line'): 'NG(確実)', ('G0', "reach for someone's wallet"): 'NG(推定)'}
for a in ARMS:
    for r, v in sn[a]:
        if not gok(v):
            dflt = 'PASS(Opus集計G2 26/26)' if a == 'G2' else ('候補(Opus G3「25〜26/26」の未特定1件がこれの可能性。不明)' if a == 'G3' else 'PASS(推定: Opus G0 NG2件=draw a line+reachのため)')
            w("| %s | %s | %s | %s(%s) | %s | %d |" % (a, esc(r['key']), esc(r['gloss']), '/'.join(gflags(v)), esc(v.get('note', '')), OPUSNG.get((a, r['key']), dflt), r['_line']))
w("\nSonnet暫定のG0 22/26(85%)とOpus 24/26(92%)の差は、Sonnetの『deictic(「人の」「誰かの」の逐語訳)』指摘のうちapply・keep someone companyの2件。G2 22/26(85%)とOpus 26/26(100%)の差4件(reach・apply・pump one's fist『喜んで』・keep someone company)もSonnetのdeictic指摘が主因。\n")
w("### 5-2. 薄い表現(別集計。Opus盲検の記録 OPUS_REVIEW_04.md:5)\n")
w("- Opusが挙げた薄化5件(通常KP中心、G3): `brace yourself for`「～に備える」(難例)、`a sense of occasion`「特別感」、`keep someone company`「人の相手をする」、`behind the scenes`「見えないところで」、`on the throne`「トップの座にいる」(難例)。いずれも『NGではなく薄い』扱い。")
w("- G0・G2の薄い判定は**個別未保存(未判定)**。注: G2の `on the throne`(「トップの座にいる」、T2 行57)はG3と同一文字列だが、Opusの薄化列挙はG3に限定されている(理由は不明)。")
w("- 薄化5件は『薄い(△)』であり、§1の確定FAIL表(Trial_03)にも§5の上表のNGにも含めない。\n")
w("### 5-3. Trial_02 `draw a line` Std 3rep(個別): G0=線を引く/一線を引く/線を引く(T2 行7,81,80)、G2=境界をはっきりさせる/境界をはっきりさせる/はっきり区別する、G3=区別をはっきりさせる/境界をはっきりさせる/一線を引く。字義NGはG0の2(rep1・rep3)のみ(§4)。\n")

w("## 付表: Trial_03 全360出力(60 KP×G0/G2/G3×rep1,2)\n")
w("各セル=日本語出力 `[Fable/Sonnet]`。Fable: P=PASS・△=薄・F=FAIL(境界は F*)。Sonnet: P/△/F。T3行は G0r1,G0r2,G2r1,G2r2,G3r1,G3r2 の順。\n")
w("| blind# | 型/X-Z | KP | G0 rep1 | G0 rep2 | G2 rep1 | G2 rep2 | G3 rep1 | G3 rep2 | T3行 |\n|---|---|---|---|---|---|---|---|---|---|")
S = {'PASS': 'P', 'THIN': '△', 'FAIL': 'F'}
for n, b in sorted(blind.items()):
    cs_ = {(x['arm'], x['rep']): x for x in cells if x['n'] == n}
    row, lines = [], []
    for ar in SONARM:
        x = cs_[ar]
        fl = S[x['fable']] + ('*' if x in border else '')
        row.append('%s [%s/%s]' % (esc(x['gloss']), fl, S[x['sonnet']]))
        lines.append(str(x['line']))
    w("| %d | %s/%s | %s | %s | %s |" % (n, b['typ'] if b['tier'] == 'normal' else 'hard', b['fam'], esc(b['key']), ' | '.join(row), ','.join(lines)))
open(OUT / 'STD_AUDIT_01.md', 'w', encoding='utf-8').write('\n'.join(L))
print('written', len(L), 'diff', len(diff), dict(cnt), dict(snc))
