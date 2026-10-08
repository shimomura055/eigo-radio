import json,collections,re
D='er052_output/open243_translation_ng_analysis_01/'
o=[json.loads(l) for l in open(D+'s0_excluded_candidates.jsonl',encoding='utf-8')]
pd=json.load(open(D+'_s0_perdump.json',encoding='utf-8'))
ev=json.load(open(D+'_s0_events.json',encoding='utf-8'))
s14=json.load(open(D+'_s0_summary14.json',encoding='utf-8'))
def isAB(rk): return ('all6_writer_redesign_necessity_01/runs' in rk) or ('factlock_writer_trial_01/runs' in rk)
def short(rk):
    rk=rk.replace('er052_output/','')
    return rk.replace('/runs/','/').replace('/control/','/')
FL=['changed_fact','changed_scope','changed_causality','changed_certainty','changed_number','changed_actor','changed_negation','changed_comparison','changed_time','unsupported_new_claim']
def stats(fn):
    s=[x for x in o if fn(x)]; p=[x for x in pd if fn(x)]
    fl=collections.Counter(f for x in s for f in x['stage1_flags'])
    lat=collections.Counter()
    for x in p:
        for a,b in x['later']: lat['exit' if a.startswith('exit') else 'recheck']+= b.get('n_excluded_claims') or 0
    return dict(n_dump=len(p),n_targets=sum(x['n_targets'] or 0 for x in p),n_excl=len(s),
        sup=sum(x['verdict']=='SUPPORTED' for x in s),nfc=sum(x['verdict']=='NO_FACT_CLAIM' for x in s),fl=fl,
        actor=sum('changed_actor' in x['stage1_flags'] for x in s),actor_final=sum(('changed_actor' in x['stage1_flags']) and x['in_final_text'] for x in s),
        actor_match=sum(('changed_actor' in x['stage1_flags']) and x['actor_match']=='match' for x in s),
        noflag=sum(not x['stage1_flags'] for x in s),
        nonunc=sum(any(f!='unsupported_new_claim' for f in x['stage1_flags']) for x in s),
        lat=lat,dumps_actor=len({x['run_key'] for x in s if 'changed_actor' in x['stage1_flags']}))
SA=stats(lambda x:True); SB=stats(lambda x:isAB(x['run_key'])); SC=stats(lambda x:not isAB(x['run_key']))
L=[]
w=L.append
w('# S0_AUDIT_01: 再分類(STAGE1_RECLASSIFY)による除外の監査(OPEN-243-TRANSLATION-NG-ANALYSIS-01 委任_02)')
w('')
w('作成日 2026-10-08。API支出 ¥0(既存artifactのみ読取。LLM呼び出しなし)。所見は事実のみ。採否・推奨はFableが判断する。')
w('再現スクリプト(同ディレクトリ、読取のみ): `_s0_scan.py`(dump収集)→`_s0_extract.py`(除外候補抽出)→`_s0_events.py`(53事象との突合)→`_s0_summary14.py`(要約14世代)→`_s0_write_audit.py`(本ファイル生成)。判断を伴う分類は「判定: 手動」と根拠を付記。')
w('')
w('## 0. 要旨(事実のみ)')
w('')
w(f'1. 承認構成(STAGE1_RECLASSIFY=True・FLOOR_MODE=number_only)で動いた Checker 実行 {SA["n_dump"]} 件(重複除去後、全てスイッチdumpで確認)の初回 Stage 1 で、再分類の対象になった model 候補 {SA["n_targets"]} claim のうち **{SA["n_excl"]} claim(SUPPORTED {SA["sup"]} / NO_FACT_CLAIM {SA["nfc"]})が `excluded=true`** で Stage 2 に渡らなかった。このうち Stage 1 が `changed_actor=true` を立てていたものは **{SA["actor"]} claim**(SUPPORTED/actor_match=match {SA["actor_match"]})。')
w('2. ANALYSIS_01 の翻訳段由来/増幅 26事象のうち、初回再分類で除外された Stage 1 候補と文一致したのは **5事象**(EV-25 重大, EV-06, EV-07, EV-10, EV-19)。「候補化なし 10/24」のうち **3事象**(EV-06, EV-07, EV-10)は「Stage 1 が候補にしたが再分類が除外」であり、残り7事象(EV-32/35/38/02/45/48/01)は Stage 1 の model 候補に当該文が出ていない。「ACCEPTABLE 残存 8」のうち再分類で初回除外された文は EV-19 の1事象。')
w('3. M3(E0: changed_actor 付き候補を再分類除外から保護)で救済され得る事象の上限は **2事象(EV-25 重大1・EV-06 軽微1)**。保護対象を「unsupported_new_claim 以外のフラグ付き」へ広げた場合の上限は 5事象(上記5件すべてが該当)。いずれも「Stage 2 に渡る」ことの上限であり、Stage 2 が BLOCKING にするとは限らない(§2-5の注記)。')
w('4. 要約 MAJOR 14世代の一次分類(判定: 手動、attempt1 の指摘基準): 明確な誤り 5 / 境界例 7 / 過剰判定の疑い 2。STOP した8世代の「最終 MAJOR」基準では 明確な誤り 1 / 境界例 4 / 過剰判定の疑い 3。')
w('5. FLOOR_MODE: Trial A/B の Checker 実行 57 件(all6 38 + factlock/runs 19)の switch dump 全件が `FLOOR_MODE=number_only`・`STAGE1_RECLASSIFY=True`・`PRECHECK_MODE=number_only`、dump の sha256 が各 run の `provenance.switch_dump_sha256` と一致、`switches_equal_e2e02=True`。ANALYSIS_01 の「直接には確認していない(未確認)」は解消(§4)。')
w('6. EV-28(callers): EN deviation check は当該要約を指摘せず(LEDGER_COMPLIANT)、Checker の Stage 1 が r3+r5 で候補化、Stage 2 一次 ACCEPTABLE → 第2意見 BLOCKING → 書換え(§5)。再分類は L1 を CANDIDATE のまま維持した。')
w('')
w('## 1. (a) 再分類による除外の集計')
w('')
w('### 1-1. 収集範囲と構成の判定根拠')
w('')
w('- 収集: `er052_output/**/checker/**/*.json` と `er052_output/**/runs/*.json` のうち、トップレベルに `stage1_coverage` を持つ Checker 実行 dump = 254 ファイル。`checker/after_instances/*.json` は `checker/runs/*.json` と同内容の複製のため除き、run単位で重複除去して **133 実行**(`_s0_perdump.json`)。除外候補の件数は(run, 単位ID)で一意(`s0_excluded_candidates.jsonl` 1,011行=一意)。')
w('- 構成の判定根拠: 各 dump に対し、同ディレクトリまたは最も近い親ディレクトリの `approved_switches_dump*.json` を探し、`switches.STAGE1_RECLASSIFY is True` かつ `switches.FLOOR_MODE == "number_only"` を確認。133/133 が該当(dump 無しの実行は0)。Trial A/B 57 実行は run 直下の `checker/approved_switches_dump_after_p01.json` と `provenance.switch_dump_sha256` の一致も確認(§4)。')
w('- 注意: Checker dump 自身の `switches` キーには `STAGE1_RECLASSIFY`/`FLOOR_MODE` が出力されない(実行時dumpの対象外)。構成は別ファイルの switch dump で確認した。')
def grp(x):
    rk=x['run_key']
    return '/'.join(rk.split('/')[1:3]) if '|' not in rk else rk.split('/')[1].split('|')[0]+'(個別file)'
w('- 133 実行の内訳(出典dir別): ' + ', '.join(f'{k} {v}' for k,v in collections.Counter(grp(x) for x in pd).most_common()) + '。')
w('- 133 実行は同一記事の再実行・別Trialを含む(記事単位の重複除去はしていない)。Trial A/B(all6 + factlock/runs)57実行だけの集計を併記する。')
w('')
w('### 1-2. 集計(初回 Stage 1 の `candidate_filter.verdicts`、出典 `stage1_coverage.candidate_filter`)')
w('')
w('| 項目 | 全133実行 | Trial A/B 57実行 | その他76実行 |')
w('|---|---|---|---|')
for lab,k in [('Checker実行数','n_dump'),('再分類の対象 claim 数(model由来)','n_targets'),('除外された claim 数(excluded=true)','n_excl'),('  うち SUPPORTED','sup'),('  うち NO_FACT_CLAIM','nfc'),('changed_actor=true で除外','actor'),('  うち actor_match=match','actor_match'),('  うち最終EN本文にその文が残存(判定: 文字列一致)','actor_final'),('changed_actor を含む実行数','dumps_actor'),('フラグが全て false の除外','noflag'),('unsupported_new_claim 以外のフラグ付きの除外','nonunc')]:
    w(f'| {lab} | {SA[k]} | {SB[k]} | {SC[k]} |')
w('')
w('フラグ別件数(除外 claim あたり、複数フラグは重複計上):')
w('')
w('| Stage 1 フラグ | 全133実行 | Trial A/B | その他 |')
w('|---|---|---|---|')
for f in FL: w(f'| {f} | {SA["fl"][f]} | {SB["fl"][f]} | {SC["fl"][f]} |')
w('')
w('注: `unsupported_new_claim` を含む除外が大半(886/1,011)。`changed_number=true` で除外された claim は全体4件(dump単位の `n_excluded_with_changed_number` は entry 数で数えるため合計が異なる)。')
w('')
w('### 1-3. 再検査(recheck)・出口(exit)の再分類(件数のみ。claim単位の verdict は dump に保存されていない)')
w('')
w(f'- 初回(上表): 全体 {SA["n_excl"]} claim。再検査・出口の再分類 `n_excluded_claims` の合計: 全体 出口 {SA["lat"]["exit"]} / 再検査 {SA["lat"]["recheck"]}、Trial A/B 出口 {SB["lat"]["exit"]} / 再検査 {SB["lat"]["recheck"]}(出典: `recheck_exit_check.log[].reclassify`、`cycles[].recheck_coverage`)。`candidate_filter.verdicts`(claim単位)は初回のみ。再検査・出口の changed_actor 内訳は取得不能(未確認)。')
w('')
w('### 1-4. changed_actor=true で除外された 38 claim(全件、`s0_excluded_candidates.jsonl` と同一)')
w('')
w('| # | run | 単位 | 文(claim, 先頭120字) | verdict | actor_match | related_fact | Stage 1 の issue(先頭110字) | 最終EN本文 | 構成 |')
w('|---|---|---|---|---|---|---|---|---|---|')
n=0
for x in o:
    if 'changed_actor' in x['stage1_flags']:
        n+=1
        iss=(x['stage1_issues'][0] if x['stage1_issues'] else '').replace('|','/').replace('\n',' ')[:110]
        w(f'| {n} | {short(x["run_key"])} | {x["key"]} | {x["claim"][:120].replace("|","/")} | {x["verdict"]} | {x["actor_match"]} | {",".join(x["related_fact_ids"])} | {iss} | {"残存" if x["in_final_text"] else "文字列不一致"} | {"A/B" if isAB(x["run_key"]) else "他"} |')
w('')
w('(最終EN本文=Checker最終cycleのEN本文に文が正規化一致で含まれるか。判定: 機械的な文字列一致であり、書換えによる不一致と抽出失敗は区別していない。)')
w('')
w('全1,011件は `s0_excluded_candidates.jsonl`(フィールド: run_key, key, claim, verdict, actor_match/counterpart_match/scope_match/qualifier_match, reclass_reason, fact_tags, stage1_flags, stage1_issues, related_fact_ids, routes, run_final_state, in_input_text, in_final_text)。')
w('')
w('## 2. (b) 盲検NGとの突合')
w('')
w('方法: `items.jsonl`(74行=判定。`event_id` で束ねた53事象+event_id無しの保留8判定)の各事象のEN文(`en_sentence_matched` または `ng_text`)を、同一 run の Checker dump の `candidate_filter.verdicts`・`union_candidates`・`stage2_results` と照合(語集合Jaccard≥0.5、または正規化文字列の包含。ANALYSIS_01の `_build.py` と同系統の基準)。出典: `_s0_events.json`。')
w('')
w('### 2-1. 翻訳段由来/増幅 26事象(うち Checker あり 24)のうち、初回再分類で除外された文と一致した5事象')
w('')
w('| 事象 | 盲検 | 型/箇所 | Stage 1 フラグ(再分類前、文一致候補の和集合) | 再分類 verdict | Stage 2 での扱い(出典 stage2_results) | ANALYSIS_01 での位置づけ | changed_actor |')
w('|---|---|---|---|---|---|---|---|')
byid={e['event']:e for e in ev}
pos={'EV-25':'候補化(QUALITY)残存 ※重大','EV-06':'候補化なし','EV-07':'候補化なし','EV-10':'候補化なし','EV-19':'ACCEPTABLE残存'}
for k in ['EV-25','EV-06','EV-07','EV-10','EV-19']:
    e=byid[k]; v=[x for x in e['verdicts'] if x['excluded']][0]
    s2=', '.join(f'cycle{x["cycle"]}:{x["mat"]}(basis={x["basis"]})' for x in e['stage2']) or 'Stage 2 に当該文なし'
    w(f'| {k} | {"重大" if "major" in e["sev"] else "軽微"} | {e["type"]}/{e["position"]} | {",".join(e["pre_filter_flags"])} | {v["verdict"]}(actor_match={v["actor_match"]}) | {s2} | {pos[k]} | {"あり" if "changed_actor" in e["pre_filter_flags"] else "なし"} |')
w('')
w('### 2-2. 「候補化なし 10/24」の内訳(判定: 機械+一部手動)')
w('')
w('ANALYSIS_01 §3-4 の「候補化なし」は union_candidates(再分類後)と stage2_results のどちらにも文が無い事象。10事象の内訳:')
w('')
w('| 区分 | 件数 | 事象 |')
w('|---|---|---|')
w('| Stage 1 の model 候補になったが再分類が除外(SUPPORTED) | 3 | EV-06(changed_actor+changed_fact), EV-07(causality+fact+unsupported), EV-10(certainty+fact) |')
w('| Stage 1 の model 候補に当該文が出ていない(verdicts・candidates に文一致なし) | 7 | EV-32, EV-35, EV-38, EV-02, EV-45, EV-48, EV-01 |')
w('')
w('### 2-3. 「ACCEPTABLE 残存 8」のうち再分類で落ちた事象')
w('')
w('ACCEPTABLE のみで最終本文に残った8事象(EV-19, 30, 23, 50, 51, 08, 52, 04)のうち、初回再分類で除外された文と一致したのは **EV-19 のみ**(フラグ changed_certainty/changed_scope/unsupported_new_claim。changed_actor なし)。EV-19 は stage2_results に `detected_by=stage1_llm`・cycle1 ACCEPTABLE として別経路で存在(経路はコード未確認。同一fact_idの兄弟location展開の可能性があるが未確認)。他7事象(EV-30/23/50/52 は changed_actor 付き)は再分類で CANDIDATE 維持されて Stage 2 に渡り、Stage 2 が ACCEPTABLE と判定した。')
w('')
w('### 2-4. 重大 EV-25 の経路補正(ANALYSIS_01 §3-4 への事実追記)')
w('')
w('ANALYSIS_01 は EV-25 を「候補化 Stage2=QUALITY → 最終文残存(Stage 1 は別事実 HC-010 を理由に候補化)」としていた。dump 照合の結果:')
w('')
w('- 当該文(単位 S9.1)は Stage 1(r3)の model 候補で `changed_actor=true`、issue 文は「Ledgerでは従業員がMuseに料金交渉を依頼した事例だが、記事は「Meta was asked」とし、依頼を受けた主体をMetaに変えている」、related_fact_id=MUSE-HC-011(出典: `b3__baseline__r1/checker/runs/meta_run03_advanced.json` の `stage1_coverage.per_route.r3.candidates`)。')
w('- 再分類 verdict は `SUPPORTED`、actor_match/counterpart_match/scope_match/qualifier_match=`match`、`excluded=true`、reason=「インターネット・ケーブル料金交渉の1件で、従業員が契約スタッフの人種に関する不適切発言を報告したというLedgerと一致する」(出典: `stage1_coverage.candidate_filter.verdicts`)。')
w('- union_candidates(10件)に S9.1 は無い。一方 cycle1 の stage2_results(15件)には同文が `detected_by=stage1_llm`・`related_fact_id=MUSE-HC-010`・materiality=QUALITY で存在する。つまり Stage 2 の評価は **HC-010 に対するもの**で、HC-011・changed_actor の観点は評価されていない(経路は同一fact_idの兄弟location展開と推定、コード未確認)。')
w('')
w('### 2-5. M3(E0)で救済され得る事象数(上限)')
w('')
w('| 保護条件 | 上限事象数(翻訳段由来/増幅 26事象中) | 事象 |')
w('|---|---|---|')
w('| changed_actor=true の候補を除外から保護(M3の定義) | **2** | EV-25(重大), EV-06(軽微) |')
w('| unsupported_new_claim 以外のいずれかのフラグ付きを保護 | 5 | EV-25, EV-06, EV-07, EV-10, EV-19 |')
w('')
w('- 上限の意味: 「Stage 2 に候補として渡る事象数」の上限。Stage 2 の判定(BLOCKING/QUALITY/ACCEPTABLE)は未検証。EV-25 は既に別観点(HC-010)で Stage 2 に渡って QUALITY → 第2意見 ACCEPTABLE となっており、changed_actor 観点で Stage 2 に渡った場合の結果は dump からは分からない。')
w('- 26事象に含まれないJA由来・保留の除外一致: EV-33, EV-46, EV-21, EV-20(JA由来、軽微)と保留 TB-060(NO_FACT_CLAIM)。')
w('- 逆方向のコスト(保護した場合に Stage 2 へ追加で渡る claim 数の上限): 除外1,011 claim のうち changed_actor=true は38(全体の3.8%)、Trial A/B 57実行では 379中8。unsupported_new_claim 以外のフラグ付きを保護する場合は 656(全体)/239(A/B)。')
w('')
w('## 3. (c) 要約 MAJOR 14世代の精査(判定: 手動)')
w('')
w('対象: ANALYSIS_01 §2-4/§3-4 の「attempt1 で translation 起源 MAJOR が要約に出た 14世代」(出典: 各 run の `b1b/audit/deviation_checks/*attempt*.json`、`a2/` は standard、`deviation_check.json`=最終)。STOP=最終検査でも MAJOR が残った8世代(G02, G03, G06, G07, G08, G09, G12, G14)、解消=6世代(G01, G04, G05, G10, G11, G13)。台帳は各 run の `research_ledger/verified_fact_ledger.txt` の該当 fact。分類基準: 明確な誤り=台帳の本文/notes_for_writer/scope/conditions に明示的に反する、または台帳に無い事実・語を足している / 境界例=台帳に直接の禁止はないが、台帳の確認範囲より具体的・広い表現で解釈が割れる / 過剰判定の疑い=記述が台帳と矛盾せず、指摘が台帳に明記のない細部(例: 開示の相手が「users」)を理由にしている。')
w('')
cls={
'G01':('明確な誤り','notes_for_writer「「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う」に対し、要約が「Muse’s calling feature」を paused としている','—'),
'G02':('境界例','台帳に開示相手の記載がなく "users" 限定を指摘(軽め)、"prompting" は因果を断定(台帳は「ミスと認め、ロールバック」を並記するだけ)','過剰判定の疑い(最終: "paused its human-concierge feature" と対象は台帳通りで、指摘は "users" の特定のみ)'),
'G03':('境界例','"unexpectedly" "prompting privacy concerns and a rollback" は因果と感情の断定で台帳に無い。ただし事実の取り違えではなく表現の強さ','明確な誤り(最終: "secretly" は台帳に無い語、"Muse’s calling feature" はnotes_for_writerに反する)'),
'G04':('明確な誤り','"paused its phone AI feature" は notes_for_writer「「サービス全体を停止した」とは書かない」に反する','—'),
'G05':('明確な誤り','台帳は「Space Forceが宇宙に兵器を配備したことを初めて認めた発言」(初の公式確認)。要約 "confirmed its first orbital weapons deployment" は初の配備と読め、notes_for_writerの範囲を超える','—'),
'G06':('境界例','台帳 scope は「国際指標Brent原油先物」。要約は "oil prices" と一般化。要約としては自然だが台帳 scope より広い','境界例(最終も同じ指摘)'),
'G07':('過剰判定の疑い','断片 "without users being properly informed" のみを指摘。台帳は「適切な開示なし」(相手の記載なし)。"users" は台帳 MUSE-HC-010 の "user information" と整合し、矛盾はしない','過剰判定の疑い(最終も "users" 指摘)'),
'G08':('境界例','"realizing"(内心の断定)と "weren’t told they were speaking to contractors" は台帳の「適切な開示なし」より具体的','境界例(最終: "without clearly disclosing they were human" は「適切な開示なし」の言い換えとも「人間と明示していない」への具体化とも読める)'),
'G09':('過剰判定の疑い','"users weren’t properly told" の "users" 特定のみが指摘理由(G07と同型)','境界例(最終: "so the company rolled back" の因果。台帳はミスを認め当面ロールバックと並記、因果は明示せず)'),
'G10':('境界例','台帳 HF-002 は「すべての貨物に20%の償還」。要約 "fee for ships crossing Hormuz" は対象が貨物→船と読める。ただし「費用の徴収案」という大意は一致','—'),
'G11':('明確な誤り','"paused its AI phone feature" は G04 と同型で、notes_for_writer「「サービス全体を停止した」とは書かない」に反する','—'),
'G12':('境界例','"failing to tell users that human contractors might handle their calls" は開示の内容を具体化(台帳は「適切な開示なし」)。台帳に無い断定を含む','過剰判定の疑い(最終: "concerns that users weren’t told contractors might access sensitive information" は懸念の形で、指摘は "users" 特定のみ)'),
'G13':('境界例','"capabilities and targets remain unknown": 台帳 notes は「具体的なシステム名・攻撃能力・標的は推測で補わない」で、"capabilities" 一般を unknown とするのは範囲が広い解釈','—'),
'G14':('明確な誤り','"paused its AI phone assistant test" は台帳 scope「human concierge／human agent callsの社内テスト」の機能ロールバックを、AI電話アシスタント全体のテスト中断と読める形にしている','境界例(最終: "paused its AI phone feature after some calls were handled by human contractors" は MUSE-HC-07 に G04 のような明示の禁止notesがない)'),
}
def ledger_lines(block):
    if not block: return '(台帳ブロック取得不可)'
    ls=[l.strip() for l in block.split('\n') if l.strip()]
    keep=[ls[0][:230]]+[l for l in ls[1:] if l.startswith(('scope:','notes_for_writer:','conditions:'))]
    return ' / '.join(k[:200] for k in keep)
cnt1=collections.Counter(); cnt2=collections.Counter()
w('### 3-1. 14世代の一覧')
w('')
w('| 世代 | run | 結果 | attempt1 の要約文(MAJOR) | 台帳の該当行 | 指摘(attempt1、JA先頭150字) / フラグ | 一次分類(attempt1基準) | 根拠(判定: 手動) |')
w('|---|---|---|---|---|---|---|---|')
for r in s14:
    g=r['gen']; a1=[a for a in r['attempts'] if 'attempt1' in a['file']][0]
    stop=(r['attempts'][-1]['status']!='LEDGER_COMPLIANT')
    claims=' // '.join(x['claim_in_article'][:150] for x in a1['devs'])
    iss=' // '.join((x['issue'][:150]+' ['+','.join(x['flags'])+']') for x in a1['devs'])
    fid=a1['devs'][0]['related_fact_id']
    c=cls[g]; cnt1[c[0]]+=1
    w(f'| {g} | {r["run"].replace("er052_output/","").replace("/runs/","/").replace("/control/","/")} | {"STOP" if stop else "解消(attempt2でCOMPLIANT)"} | {claims.replace("|","/")} | {fid}: {ledger_lines(r["ledger"].get(fid)).replace("|","/")} | {iss.replace("|","/")} | {c[0]} | {c[1].replace("|","/")} |')
w('')
w('### 3-2. STOP した8世代の「最終 MAJOR」の再分類(判定: 手動)')
w('')
w('| 世代 | 最終の要約文(MAJOR、`deviation_check.json`) | 指摘(JA先頭150字) / フラグ | 最終基準の分類 |')
w('|---|---|---|---|')
for r in s14:
    g=r['gen']
    if r['attempts'][-1]['status']=='LEDGER_COMPLIANT': continue
    f=r['attempts'][-1]; c=cls[g][2]
    key=c.split('(')[0]
    cnt2[key]+=1
    w(f'| {g} | {" // ".join(x["claim_in_article"][:150] for x in f["devs"]).replace("|","/")} | {" // ".join((x["issue"][:150]+" ["+",".join(x["flags"])+"]") for x in f["devs"]).replace("|","/")} | {c.replace("|","/")} |')
w('')
w(f'**内訳**: attempt1 基準(14世代)= {dict(cnt1)}。STOP 8世代の最終MAJOR基準 = {dict(cnt2)}。')
w('')
w('- 事実: 要約の主要な指摘語は "AI phone feature / calling feature"(ロールバック対象の範囲、G01/G03/G04/G11/G14)と "users"(開示相手、G02/G07/G09/G12)の2系統(判定: 手動の集計)。')
w('- 事実: 台帳 MUSE-HC-012 の notes_for_writer(「サービス全体を停止した」とは書かない)は G01/G04/G11 で直接の根拠になった。MUSE-HC-07(G14)にはこの notes がない。')
w('- 注意: 分類は1名(LLM)の手動判定。境界例・過剰判定の疑いのうち3件は `S0_USER_CHECK.md` に抜いた。')
w('')
w('## 4. (d) FLOOR_MODE の確認')
w('')
w('- 対象: Trial A の Checker 実行(all6: `er052_output/all6_writer_redesign_necessity_01/runs/*/control/*/checker/`)38 実行、Trial B の追加分(factlock: `er052_output/factlock_writer_trial_01/runs/*/control/*/checker/`)19 実行。')
w('- 確認方法: 各 run の `checker/approved_switches_dump_after_p01.json` の `switches` を読取り、sha256 を計算して、同 run の `checker/runs/*.json` の `provenance.switch_dump_sha256` と比較。')
w('- 結果: 57/57 で `FLOOR_MODE="number_only"`、`STAGE1_RECLASSIFY=true`、`PRECHECK_MODE="number_only"`、sha256 一致、`provenance.switches_equal_e2e02=true`。(同 dump に `FLOOR_VERIFY_MODE="off"`・`CAUSAL_FLOOR=false`・`STAGE2_DOWNGRADE_VERIFY=false`・`STAGE2_SECOND_OPINION=true` も含まれる: 代表 run `meta/b3__baseline__r1` の dump で目視確認。)')
w('- 判定: Trial A/B の Checker は FLOOR_MODE=number_only で動いた(直接確認)。承認構成 `OPEN233_APPROVED_FLOW_SWITCHES`(`er052_open233_self_recovery_flow_runner_01.py` L497-522)との全キー突合は行っていない(主要3キーのみ全件確認)。')
w('')
w('## 5. (e) EV-28 の証跡照合(Opus未照合分)')
w('')
w('対象: EV-28(TA-034、重大、meta/b3 baseline r1)=`er052_output/all6_writer_redesign_necessity_01/runs/meta/control/b3__baseline__r1`。')
w('')
w('1. EN 文: 末尾要約 "Meta’s AI phone calls sometimes relied on human contractors, but callers were not clearly told who was speaking."(`b1b/article.md`)。JA対応文なし(要約は別callでEN記事から生成)。')
w('2. EN deviation check(`b1b/audit/deviation_checks/advanced_attempt1.json`、`deviation_check.json`): overall_status=LEDGER_COMPLIANT。指摘は2件のみ(MINOR/ja_source の "Meta executives"、MINOR/translation の EV-25 "employees reported" [changed_number])。**要約 "callers" への指摘は無い**(検出なし)。')
w('3. Checker Stage 1(`checker/runs/meta_run03_advanced.json`): 単位 L1 が `model_r3`+`model_r5` の両経路で候補化。flags: changed_fact, changed_certainty, **changed_actor**, unsupported_new_claim。related_fact_ids=MUSE-HC-012, MUSE-HC-014。issue(要旨): 「適切な開示なし」を「通話相手に話者が誰かを明確に伝えていなかった」という具体的主張にしている。')
w('4. 再分類(同 dump `candidate_filter.verdicts`): L1 は `CANDIDATE`(excluded=false、actor_match=match)。**再分類で除外されなかった**。')
w('5. Stage 2 cycle1: 一次 `llm_materiality=ACCEPTABLE`(basis=none)→ 第2意見(`STAGE2_SECOND_OPINION`)が `BLOCKING`(basis=ledger_scope)で split → 最終 `materiality=BLOCKING`、`floor_reason=s1_second_opinion_blocking`。rewrite_hint に「開示されなかった相手を発信者ではなく、電話を受ける側(people being called / call recipients)として記述」が入った。')
w('6. 書換え: cycle1 の rewrite(`replace_with_ledger_value`、`e1_minimal_word_edit`、guard_ok=true)で、最終要約は "…but people being called were not given proper disclosure."。cycle2・cycle3 の再評価は ACCEPTABLE(第2意見も ACCEPTABLE)。final_state=`RESOLVED_REWRITE_THEN_DOWNGRADE`。')
w('7. 結論(事実): EV-28 は EN deviation check をすり抜け、Checker が Stage 1 で changed_actor 付きで候補化し、再分類は除外せず、Stage 2 一次 ACCEPTABLE を第2意見が BLOCKING にして救済した経路。ANALYSIS_01 の記述と一致。EV-25 との差は「再分類が除外したか否か」(EV-28=維持、EV-25=SUPPORTED で除外)。')
w('')
w('## 6. 未確認事項・限界')
w('')
w('- 再検査・出口の再分類の claim 単位 verdict は dump に無い(件数のみ)。')
w('- 133実行は記事の重複(同一記事・別Trial)を含む。独立標本数ではない。')
w('- 「M3で救済され得る」は Stage 2 へ渡る上限であり、救済(BLOCKING化)の確率ではない。')
w('- EV-25/EV-19 が Stage 2 に載った経路(兄弟location展開)はコード未確認。')
w('- 要約14世代の一次分類は手動判定(1名)。ユーザー確認3件の結果次第で分類が変わり得る。')
w('- 14世代には Trial A/B 57実行の外(`gpt6_wiring_e2e_01` の G14)を含む。')
open(D+'S0_AUDIT_01.md','w',encoding='utf-8').write('\n'.join(L)+'\n')
print('ok',dict(cnt1),dict(cnt2))
