# ADV_AUDIT_01.md 生成(API 0)
from audit_01_data import *
OUT = Path(__file__).parent
H = set(HARD20)
FAM = {b['key'].lower(): b['fam'] for b in blind.values()}
E0G0 = sorted([r for r in r2 if r['arm'] == 'E0@G0'], key=lambda r: (HARD20.index(r['key']), r['rep']))
assert len(E0G0) == 60
NG_A = {("reach for someone's wallet", 1)}   # Opus盲検の唯一のNG(Fable委任_10 §1。OPUS_REVIEW_04.md:6は集計59/60のみ記載)


def adv_A_label(r):
    return 'NG' if (r['key'], r['rep']) in NG_A else 'PASS'


wrong_A = [r for r in E0G0 if std_label_A(r['key'], r['gloss_in'])[0] == '誤り']
warn_A = [r for r in E0G0 if std_label_A(r['key'], r['gloss_in'])[0].startswith('正(要')]
ngA = [r for r in E0G0 if adv_A_label(r) == 'NG']
assert len(wrong_A) == 5 and len(ngA) == 1 and len(warn_A) == 3, (len(wrong_A), len(ngA), len(warn_A))


def knum(k):
    return [n for n, b in blind.items() if b['key'].lower() == k.lower()][0]


Eb = sorted(E, key=lambda e: (knum(e['key']), e['arm']))
BNOTE = {
    ('an unseen clock', 'G0'): 'Std誤り入力(字義訳)。出力は「時計」を引き継がず"hidden sense of time"。誤りの波及なし(実行層目視。"sense of time"はG2/G3の"hidden process"よりやや曖昧)',
    ('run on', 'G0'): 'Std入力は正(Fable PASS)。出力が2義併記("power source" or "system or schedule")=Adv生成起因の欠陥(single不良)。G2/G3は単一義',
    ('price tag', 'G2'): 'Std入力は薄(Fable△「値札に表示された価格」)。出力は「表示された金額」寄り。誤りではない',
    ('standard deviation', 'G3'): 'Std入力は薄(Fable△「データのばらつきを表す値」)。出力は正しい定義。誤りなし',
    ('on paper', 'G0'): '軽微: "in writing or theory"と2語併記(実質単一義)',
}
rowsB = []
for e in Eb:
    arm = e['arm'].split('@')[1]
    n = knum(e['key']); b = blind[n]; c = b['byarm'][(arm, 1)][0]
    rowsB.append(dict(e=e, arm=arm, n=n, b=b, fv=fable(n, c), gline=gl[(arm, e['key'].lower(), 1)]['_line']))
wrong_B = [x for x in rowsB if x['fv'] == 'FAIL']
thin_B = [x for x in rowsB if x['fv'] == 'THIN']
assert len(rowsB) == 120 and len(wrong_B) == 1 and len(thin_B) == 2


def esc(s):
    return str(s).replace('|', '\\|')


L = []
w = L.append
w("# ADV_AUDIT_01: Advanced英語説明の検証実態とNG原因(FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_10、API 0・新規生成0・コード変更0)\n")
w("生成=`AUDIT_01/audit_01_build_adv.py`(読み取り専用集計)。生データ=`er112_output/kp_gm_trial_02/results.jsonl`(以下T2)・`er112_output/kp_gm_trial_03/results.jsonl`(T3)。行番号=各jsonlの1始まり行。\n")
w("## 0. 結論(先頭)\n")
w("1. **「59/60」と「120件で伝染0」は別物で、母集団・判定者・Std誤り入力の有無が異なる。** 59/60=難例20KP×3回のAdv出力(Opus盲検、確定gold)。120件=通常40KP×Std 3方式のrep1 gloss(各1回)を入力にしたAdv出力(実行層Sonnetの目視、独立Judgeなし)。")
w("2. **59/60の唯一のNGは Std意味の誤りに起因する(分類(i))**: `reach for someone's wallet` rep1。入力Std「人の財布に手を伸ばす」(盗む読み)の「人の」を引き継ぎ、Advが \"another person's wallet to take or use it\" と生成した。同一入力のrep2・rep3はPASS(支払いの準備)、gloss無し(E1)・正しいgloss(E0@G2/E0@G3)ではPASS。Adv生成の確率的ゆらぎも関与するため、Std誤り入力でも常に波及するわけではない。")
w("3. **分母=Std意味が誤っていた出力、分子=Adv NGに波及した出力**: **A(難例20×3=60): 1/5**(Std誤りは `draw a line`「線を引く」2出力+`reach for someone's wallet`「人の財布に手を伸ばす」3出力。波及はreach rep1の1件のみ)。**B(通常40×3方式=120): 0/1**(Fable盲検でStd誤りと確定したrep1 glossは `an unseen clock` G0「目に見えない時計」の1件のみ。Advは字義を引き継がず)。「0/120」は分母が誤りで、**波及を測れる事例は1件**。Std薄(△)入力は2件で、誤り化は0件。")
w("4. 「伝染0件」の根拠は**実行層Sonnetの目視**で、独立Judge・gold・複数rep・Std/Adv整合の正式Judge(kind P)のいずれも無い。")
w("5. Std誤りが無い出力でのAdv NG: A=0/55、B=0/119(Std誤り以外)。ただしBには**Adv生成起因の欠陥が1件**(`run on` E0@G0が2義併記)あり、Stdは正のため分類(ii)。正式NG判定は未実施のため『欠陥』扱い。\n")

w("## 1. 検証の一覧(ユーザー§2-1〜4)\n")
w("| 項目 | A: 難例20 KP×3回(=60出力) | B: 通常40 KP×3方式(=120出力) |\n|---|---|---|")
w("| 出所 | T2 arm=`E0@G0`(行は付表A) | T3 arm=`E0@G0`/`E0@G2`/`E0@G3`(kind=E、各40行、付表B) |")
w("| 独立KP数 / 生成回数 | 20 KP / 各KP3回(同一入力で再生成)=60出力 | 40 KP(重複なし)/ 方式3×各KP1回(rep1のgloss)=120出力。各出力は異なるStd入力に対する別条件 |")
fam_h = collections.Counter(FAM[k.lower()] for k in HARD20)
fam_b = collections.Counter(b['fam'] for b in blind.values() if b['tier'] == 'normal')
typ_b = collections.Counter(b['typ'] for b in blind.values() if b['tier'] == 'normal')
w("| KPの種類 | GOLD_LABELS_FINAL_01の用法列: 慣用句・比喩(figurative)11[draw a line, shine a light on, fire the starting gun, Carry the Load, brace yourself for, leap into action, take the wheel, on the throne, off the hook, turn on its head, jump to conclusions]・字義/用語(literal/literal-legal/term/collocation)6[pull someone under, sentence someone to death, refueling support, execution bell, letter of introduction, apply one's findings]・句動詞(phrasal)2[bring in, hold on]・figurative-literal境界1[reach for someone's wallet] | er112_kp_gm_kpset_03の型: 句動詞(P)%d・慣用句/定型(I)%d・コロケーション(C)%d・名詞句/用語(T)%d(`fable_blind_std_03.md`の型列) |" % (typ_b['P'], typ_b['I'], typ_b['C'], typ_b['T']))
w("| X / Z | X%d / Z%d(blind表の列) | X%d / Z%d |" % (fam_h['X'], fam_h['Z'], fam_b['X'], fam_b['Z']))
w("| 使用Prompt | `er112_kp_gm_trial_02.py:250-253` `expl_message('E0')`=Production関数 `er019_family_x_kp_explanation_01.build_explanation_user_message`(同:154-175)をそのまま呼ぶ。DEVELOPER_MESSAGEも同モジュール定数(`expl_call` :266-272) | T3 `run_e0`(`er112_kp_gm_trial_03.py:137-160`)が `T.expl_call('E0', kp, g)` を呼ぶ=Aと同一経路 |")
w("| PROMPT_SHA256との同一性 | **バイト同一ではない**。Prompt本文(定数・規則文)はProductionと同一だが、**1 KP/call**(ヘッダの件数語が \"1 Key Phrase\"、末尾 `x1`。`_header_for`/`_footer_for` :154-165)、schemaはDEV専用(`kp_expl_e0_trial02`、minItems/maxItems無し)。Productionの本番は1 callに5 KP(`PROMPT_SHA256`はn=5・5固定schemaから算出。現値 c3d3734b760af258b86020002ef8a1ab63e16633a72bdab45019ca5b7be6fa7e、`er019_family_x_kp_explanation_01.py:140-142`)。PROMPT_SHA256自体はT2/T3のresults.jsonlに記録されていない | 同左 |")
w("| model / reasoning | gpt-6-luna(`kx.MODEL`)/ medium(`kx.REASONING_EFFORT`。コードが実行時に参照する値。results.jsonlには未記録) | 同左 |")
w("| 入力条件 | 本文1文(`sent`)+KP+Std日本語意味(`gloss_in`)。**他のKPは同じcallに入らない**(1 KP/call) | 同左 |")
w("| Std日本語意味の出所 | T2 G0 arm。`draw a line`のみrep対応(rep1/2/3=G0 rep1/2/3のgloss: 線を引く/一線を引く/線を引く)、他19KPは**3回とも同じG0 rep1のgloss**(`run_expl` :292、`res.get((gloss_arm,k,rep)) or res.get((gloss_arm,k,1))`)。したがってStd glossの独立サンプルは22(20KP+draw a line rep2,rep3) | T3 G0/G2/G3の**rep1** glossのみ(rep2のglossは未使用)。E行の`gloss_in`が同arm・同KPのG rep1と一致することを全120行で確認 |")
w("| Adv判定者・基準 | **Opus盲検(OPUS_REVIEW_04.md:6)、Fable確定gold**。個別行の判定ログは未保存で、集計 E0@G0 59/60 のみ記録。NGの特定(reach rep1)は委任_10 §1(Fable)による | **実行層Sonnetの全件目視**(TRIAL_RESULT_03.md:16,54)。独立Judge無し。LLM Judge C(kind P等)は費用上限のため未実施 |")
w("| Adv PASS / NG | **59 PASS / 1 NG**(Opus、集計値) | 公式報告: Std語義取り違えの伝染0・Std/Adv矛盾0・sense誤り0(Sonnet目視)。別所見: `run on` E0@G0 の2義併記1件。本監査の再目視(実行層、同一系統)も同じ結果。**正式なPASS/NG件数は無い** |")
w("| Std意味の正誤(入力側) | 誤り5出力(2KP)/ 正55(うち`apply one's findings`3出力は要注意)/ 薄い=**未判定**(Opusの個別薄判定は未保存) | **Fable盲検でrep1 gloss 120中**: 誤り1(G0 `an unseen clock`)・薄2(G2 `price tag`、G3 `standard deviation`)・正117 |\n")

w("## 2. NG原因別内訳(ユーザー§2-5)\n")
w("| 原因分類 | A: 60出力 | B: 120出力 | 該当 |\n|---|---|---|---|")
w("| (i) Std意味の誤りに起因 | **1** | 0 | A: `reach for someone's wallet` rep1 |")
w("| (ii) Adv生成自体に起因 | 0 | 正式NG 0(欠陥1: `run on` E0@G0の2義併記、Stdは正) | B欠陥は正式判定外 |")
w("| (iii) 両方に原因 | 0 | 0 | Aの1件は(i)としたが、同一入力でrep2/3はPASSのためAdv生成のゆらぎも条件。(iii)と読む余地あり(分類は実行層の判断) |")
w("| (iv) 原因特定不能 | 0 | 0 | |")
w("| **NG合計** | **1(=59/60の残り)** | 0(正式) | |\n")
w("(i)とした根拠(A、reach rep1): (a) 出力 \"another person's wallet\" が入力 \"人の財布\" の「人の」と対応(T2 行174)。(b) 同一KP・同一本文でgloss無し(E1 rep1)・正しいgloss(E0@G2: 行111 gloss「人が支払いに備えて自分の財布に手を伸ばす」、E0@G3: 行122 gloss「財布に手を伸ばす」)はいずれも\"to get ready to pay for something...\"でPASS(`REPRESENTATIVE_01.md` C表のE1・E4と、T2 行111・122)。(c) 一方、同一入力(rep2・rep3)でもAdvは\"to get ready to spend money\"(行167)、\"to get ready to pay for something, often because you want to buy it\"(行181)を生成し波及しなかった=Std誤り入力が波及の必要条件(推定)であって十分条件ではない。n=1のため因果は『強い状況証拠』にとどまる。\n")

w("## 3. 59/60の唯一のNG(ユーザー§2-6)\n")
r = [x for x in E0G0 if x['key'] == "reach for someone's wallet" and x['rep'] == 1][0]
w("| 項目 | 内容 |\n|---|---|")
w("| KP | `reach for someone's wallet`(X記事、gold用法=figurative-literal境界) |")
w("| 本文の文 | \"%s\" |" % r['sent'])
w("| 入力Std日本語意味 | 「%s」(G0 rep1、T2 行10。E0@G0の3回とも同じ入力) |" % r['gloss_in'])
w("| Std意味の判定 | 誤り(盗む読み)。gold(GOLD_LABELS_FINAL_01.md、reach行)の「不可: 『盗む』解釈」。Trial_03でも同一文字列がFable盲検FAIL(FABLE_BLIND_RESULT_03.md:9) |")
w("| Adv英語説明(原文、T2 行%d) | \"%s\" |" % (r['_line'], r['text']))
w("| NG理由 | goldの許容=\"to take out money to pay for something (reach to get one's money)\"。出力は「別人の財布へ手を伸ばし、取る/使う」で、gold『不可』欄の盗む解釈そのもの。入力の「人の財布」の逐語反映 |")
w("| 同入力のrep2/rep3 | rep2(行167)\"to get ready to spend money\"、rep3(行181)\"to get ready to pay for something, often because you want to buy it\"=いずれもPASS(Opus) |")
w("| 根拠 | T2 results.jsonl 行174(NG)・167・181。OPUS_REVIEW_04.md:6(E0@G0 59/60)。NG行の特定は委任_10 §1(Fable)による: **Opusの個別判定ログはrepoに無く、NG行の同定はFable記述に依存**。実行層の独立照合(60出力をgold『不可』欄と照合)でも該当は本行のみ(ただし結果を事前に知っていたため独立性は限定的) |")
w("| Sonnet暫定(gold確定前)の同行 | 行174は sense_ok=0(暫定Judgeも不合格。REPRESENTATIVE_01.md C表 [0010]) |\n")

w("## 4. 分母=Std誤り、分子=Adv波及(ユーザー§2・特に指定)\n")
w("| 検証 | 母集団 | 分母: Std意味が誤りの入力を使った出力 | 分子: うちAdvが誤り(NG) | 波及率 | Std誤りでない入力でのAdv NG | 備考 |\n|---|---|---|---|---|---|---|")
w("| **A: E0@G0 難例20×3** | 60 | **5**(draw a line rep1・rep3「線を引く」、reach rep1〜3「人の財布に手を伸ばす」) | **1**(reach rep1) | **1/5** | 0/55 | Opus G0 Std NG2件(draw a line・reachと推定)に基づく。非波及4件はAdvが正しい意味を自力で生成(Opus『Std/Adv用法矛盾 G0+E0@G0 4件』と件数一致、内訳は未保存=推定) |")
w("| A(感度): 要注意gloss込み | 60 | 8(+`apply one's findings`「人の研究結果を応用する」×3) | 1 | 1/8 | 0/52 | Fable T03基準(「人の研究結果」をFAIL)に揃えた場合。Advは\"what someone learned...\"でNGなし |")
w("| **B: E0@G0/G2/G3 通常40×3** | 120 | **1**(`an unseen clock` G0「目に見えない時計」。Fable盲検FAIL) | **0** | **0/1** | 0/119(正式NG0。欠陥1=run on 別原因) | 『0/120』ではなく**波及を測れる事例は1件のみ** |")
w("| B: Std薄(△)入力 | 120 | 2(G2 `price tag`、G3 `standard deviation`) | 0 | 0/2 | | 薄いStdはAdvを誤らせなかった |")
w("| 参考 A': E0@G2 | 28行(うち難例22) | 0(Opus Std G2 26/26) | 0 | 測れない | 0/22 | 分母0 |")
w("| 参考 A'': E0@G3 | 28行(うち難例22) | 0〜1(Opus Std G3「25〜26/26」。未特定) | 0 | 0/(0〜1) | 0/22 | Opus薄化指摘5件のうち難例は`brace yourself for`「～に備える」・`on the throne`「トップの座にいる」の2。Adv出力は正しい |\n")
w("注: Opusの「E0@G2 22/22・E0@G3 22/22」の22の内訳は未記録。T2のE0@G2/E0@G3は各28行=難例20(rep1)+`draw a line`rep2・rep3(2)+通常6(rep1)。`summary_02.json`の22=難例20+通常のうちe4_normal30に含まれる2KP(behind the scenes・think up)で別母集団。以後の付表は『難例22(20+draw a line rep2,3)』を示す。通常6行のOpus判定は不明(未判定)。\n")

w("## 5. 「伝染0件」の検査内容(ユーザー§2-7)\n")
w("| 項目 | 内容 | 根拠 |\n|---|---|---|")
w("| 誰が | 実行層Sonnet(委任_08のagent)。独立Judgeではない | TRIAL_RESULT_03.md:16,54(「確認者=Sonnet agentによる全件目視であり独立Judgeではない」) |")
w("| 何を | 通常40KP×3方式のrep1 gloss→E0説明(T3 kind=E、120行)の`gloss_in`と`text`の対応を目視 | TRIAL_RESULT_03.md:54 |")
w("| 基準 | 「Std語義の取り違えがAdvへ伝染したか」「Std/Adv用法矛盾」「sense誤り」の3観点。数値基準・goldは無し(通常40にはgold無し) | 同上 |")
w("| 確認していないこと | (1) 独立Judge(LLM Judge C/kind Pは費用上限30円のため未実施) (2) 通常KPのgold(存在しない) (3) rep2のgloss→Advの対応(rep1のみ。Advは各条件1回のみ生成=確率的波及を測れない) (4) 難例20のAdv(Trial_03のEは通常40のみ) (5) Productionのバッチ(5KP/call)での挙動 | 同上、T3 results.jsonl kind=E は`tier=normal`のみ(120行) |")
w("| 事後に判明した事実 | Fable盲検(FABLE_BLIND_RESULT_03.md:7-11)でrep1 glossに誤りが1件(G0 `an unseen clock`「目に見えない時計」)あった。実行層Sonnet自身の参考判定でも当該glossはFAIL(sonnet_reference_03_detail.md、an unseen clock G0 rep1=F)。つまり『誤り入力が0件なので伝染0』ではなく『誤り入力1件で伝染0』。1件ではAdvの耐性を一般化できない | sonnet_reference_03_detail.md、T3 results.jsonl 該当行 |\n")

w("## 6. 付表A: E0@G0 全60出力(T2 results.jsonl)\n")
w("Std判定: 誤り=入力gloss誤り。Opus個別判定は未保存のため、Adv(Opus)列は『集計59 PASS + 唯一のNG=reach rep1(Fable)』から導出(個別確認ではない)。Sonnet暫定=gold確定前のSonnet Judge E3(sense/core/singleのどれが不良か)。\n")
w("| # | E行 | G元行 | KP | rep | 入力Std gloss | Std判定 | Adv説明(原文) | Adv(Opus) | Sonnet暫定 |\n|---|---|---|---|---|---|---|---|---|---|")
for i, r in enumerate(E0G0, 1):
    lab, _ = std_label_A(r['key'], r['gloss_in'])
    ff = flags(e3(r))
    w("| %d | %d | %s | %s | %d | %s | %s | %s | %s | %s |" % (i, r['_line'], gline_for('G0', r['key'], r['rep']), esc(r['key']), r['rep'], esc(r['gloss_in']), lab, esc(r['text']), adv_A_label(r), 'PASS3' if not ff else 'NG:' + '/'.join(ff)))
w("\nStd判定の根拠(ユニーク別):")
seen = set()
for r in E0G0:
    lab, bas = std_label_A(r['key'], r['gloss_in'])
    if lab != '正' and (r['key'], r['gloss_in']) not in seen:
        seen.add((r['key'], r['gloss_in']))
        w("- %s「%s」: %s — %s" % (r['key'], r['gloss_in'], lab, bas))
w("- 上記以外のglossは『正』。根拠=Opus Std G0 24/26のNG2件(draw a line・reachと推定)に含まれないこと。個別判定ログは未保存。T3で同一文字列がFable盲検判定済みのKP(carry the load/hold on/jump to conclusions/leap into action/letter of introduction/off the hook/pull someone under/refueling support/sentence someone to death/shine a light on/take the wheel)は全てPASS(`CONSISTENCY_01.md` §照合)。\n")
nn = [r for r in E0G0 if flags(e3(r))]
w("Sonnet暫定(gold確定前)の不合格 %d / 60(Opus確定=1)。不良項目別(複数計上): %s。→暫定→確定で%d件がNG→PASSに転じた(gold追補・core判定基準の差。`CONSISTENCY_01.md`)。\n" % (len(nn), ', '.join('%s=%d' % (k, sum(1 for r in nn if k in flags(e3(r)))) for k in ('sense', 'core', 'single')), len(nn) - 1))

for arm, ttl in (('E0@G2', '付表A2: E0@G2 難例22出力'), ('E0@G3', '付表A3: E0@G3 難例22出力')):
    w("## %s(T2。Opus 22/22 PASS・集計のみ)\n" % ttl)
    w("| E行 | G元行 | KP | rep | 入力Std gloss | Adv説明 | Sonnet暫定 |\n|---|---|---|---|---|---|---|")
    ga_ = arm.split('@')[1]
    sel = sorted([r for r in r2 if r['arm'] == arm and r['key'] in H], key=lambda r: (HARD20.index(r['key']), r['rep']))
    assert len(sel) == 22
    for r in sel:
        ff = flags(e3(r))
        w("| %d | %s | %s | %d | %s | %s | %s |" % (r['_line'], gline_for(ga_, r['key'], r['rep']), esc(r['key']), r['rep'], esc(r['gloss_in']), esc(r['text']), 'PASS3' if not ff else 'NG:' + '/'.join(ff)))
    w("")

w("## 7. 付表B: 通常40×3方式 E0説明 120出力(T3 results.jsonl kind=E)\n")
w("Std判定=Fable盲検最終判定(FABLE_BLIND_RESULT_03.md)。Adv判定=Sonnet目視の公式報告(NG0)+本監査の再目視メモ(『所見』列。正式判定ではない)。\n")
w("| blind# | 型/X-Z | KP | arm | E行 | G(rep1)行 | 入力Std gloss | Std(Fable) | Adv説明(原文) | 所見 |\n|---|---|---|---|---|---|---|---|---|---|")
for x in rowsB:
    e = x['e']; b = x['b']
    note = BNOTE.get((b['key'].lower(), x['arm']), '')
    w("| %d | %s/%s | %s | %s | %d | %d | %s | %s | %s | %s |" % (x['n'], b['typ'], b['fam'], esc(b['key']), x['arm'], e['_line'], x['gline'], esc(e['gloss_in']), x['fv'], esc(e['text']), esc(note)))
w("\n集計: Std誤り(Fable FAIL)%d・Std薄(△)%d・Std正%d(計120)。Adv: 正式NG 0、欠陥1(run on)、Std誤り入力でのAdv誤り 0/1。\n" % (len(wrong_B), len(thin_B), 120 - len(wrong_B) - len(thin_B)))
w("## 8. 補足: A/B以外のE行(参考・今回の対象外)\n")
w("T2にはE0@prod(通常55、Production gloss入力、Sonnet暫定のみ)・E1(115)・E1c(77)・E4(52)がある。これらはStd glossを入力にしない、または別Promptであり、今回の『Std誤り→Adv波及』分析の対象外。\n")
open(OUT / 'ADV_AUDIT_01.md', 'w', encoding='utf-8').write('\n'.join(L))
print('written', len(L), 'nonPASS3 A:', len(nn))
