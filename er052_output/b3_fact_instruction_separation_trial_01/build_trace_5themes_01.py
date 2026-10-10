# Phase1 read-only: 混入文の逆追跡表 trace_5themes.json を生成 (手作業判定 + ファイル/行/逐語の自動付与)。API なし。
# 実行 (repo root): py -I er052_output/b3_fact_instruction_separation_trial_01/build_trace_5themes_01.py
import json, os, re, difflib
H = os.path.dirname(os.path.abspath(__file__))
R = "er052_output/factlock_astra_e2e_trial_01/g0_real_annotation_01"
S = "er052_output/factlock_astra_e2e_trial_01/stage_r"
# class: WRITER_IMPERATIVE=Writerへの禁止/指示文 / FACT_QUALIFIER=事実の確かさ・範囲を述べる記述文 / STORYLINE_DIRECTIVE / STRUCTURE
# origin: N_VERBATIM(notes_for_writer逐語) / N_PARAPHRASE(notes_for_writerをB3が言い換え) / N_OTHER_FACT_INFERRED(未選定factのnotes転用と推定)
#         AMB_VERIFIER(Verifier verification_notes->ledger ambiguity_note) / B3_NEW(Ledgerに対応文なし) / CLAIM_FIELD(claim/scope/conditions由来)
E = [
 ("semiconductor_earnings","これらの需要評価と業績・見通しの間に、Ledgerで確認されていない因果関係を付け加えないこと。","WRITER_IMPERATIVE","B3_NEW","F6","notes_for_writer",
  "Ledgerに対応文なし(F6 notesは『CEOの評価として帰属を明記し、市場全体の需要事実として一般化しない』で内容が別)。B3自身の fact_tests[].reason (F2/F3/F6) に『因果関係の確認はない』旨があり、それがbriefへ漏出"),
 ("semiconductor_earnings","また、Ledgerは「最も最近」の発表という選定条件を確定できないとしているため、Broadcomをその条件を満たす企業と断定しないこと。","WRITER_IMPERATIVE","AMB_VERIFIER","F1","ambiguity_note",
  "F1はVerifierがAMBIGUOUS判定。Researcher draftのambiguityはnull、Ledgerの ambiguity_note 行は Verifier の verification_notes そのもの(verify_ledger_provenance_01.py で確認)。B3が命令文化"),
 ("semiconductor_earnings","ただし、この発表が「最も最近」かはLedger上確定できない。","FACT_QUALIFIER","AMB_VERIFIER","F1","ambiguity_note","Storyline行内。記述文(確かさの限定)。同じ出所"),
 ("small_bag","「mini」と「micro」を混同しないこと。","WRITER_IMPERATIVE","N_VERBATIM","MB-06","notes_for_writer","notes_for_writer 冒頭文とほぼ逐語(15字連続一致)"),
 ("small_bag","これらは編集・ランウェイ上の注目を示すもので、消費者全体の需要や販売増を立証するものではない。","FACT_QUALIFIER","N_PARAPHRASE","MB-01","notes_for_writer","MB-01 conditions(『消費者の購買数や市場シェアの調査ではない』)と notes(『販売増の証拠とは区別する』)の言い換え。記述文だが出所の一部は notes"),
 ("small_bag","Storyline：2026年、ミニバッグは","STRUCTURE","B3_NEW",None,None,"Selected Facts節の先頭にStoryline行が重複。B3 Promptの『冒頭にStorylineの1行を含める』指示が原因。build_selected_brief_markdown は先頭一致(接頭辞なし)の時だけ除去するため『Storyline：』接頭辞付きは残る"),
 ("space_weapons","具体的なシステム名や攻撃能力は補わない。","WRITER_IMPERATIVE","N_PARAPHRASE","F-001","notes_for_writer","F-001 notes『具体的なシステム名・攻撃能力・標的は推測で補わない』の短縮言い換え"),
 ("space_weapons","これは地上から発射した試験であり、兵器の軌道上配備とは区別する。","WRITER_IMPERATIVE","N_PARAPHRASE","F-003","notes_for_writer","F-003 notes『…兵器を軌道上に恒久配備した事例とは区別する』の言い換え"),
 ("space_weapons","こうした衛星運用・保護の任務は、攻撃兵器の軌道上配備とは分けて扱う。","WRITER_IMPERATIVE","N_PARAPHRASE","F-015","notes_for_writer","F-015 notes『…兵器配備とは分けて整理する』の言い換え"),
 ("space_weapons","この条文だけから個別の配備の適法性を断定しない。","WRITER_IMPERATIVE","N_OTHER_FACT_INFERRED","F-017","notes_for_writer","逐語一致なし。未選定の F-017 notes『条約の一般原則と、個別事案の違法性判断を分ける』をB3が F-016 側へ転用したと推定(F-016 自身の notes は『全面禁止する条約とは書かない』)"),
 ("space_weapons","既存条約が禁じる範囲を誇張せず整理する。","STORYLINE_DIRECTIVE","B3_NEW","F-016","notes_for_writer","Storyline行(Writerの『テーマ：』行にそのまま使われる)内の書き方指示。Ledger対応文なし(F-016 notes と同趣旨)"),
 ("hormuz","20％案だけが上昇の原因だったとは断定しない。","WRITER_IMPERATIVE","N_PARAPHRASE","HF-006","notes_for_writer","HF-006 notes『7月13日の上昇全体を「20％料だけが原因」と断定しない』の言い換え"),
 ("hormuz","撤回後に原油価格が全面的に下落したとは書かない。","WRITER_IMPERATIVE","N_VERBATIM","HF-009","notes_for_writer","HF-009 notes に24字連続で逐語一致"),
 ("central_bank_mortgage","したがって、2月から10月までの固定住宅ローン金利上昇や試算された負担増を、9月のFed利上げだけに帰属させない。","WRITER_IMPERATIVE","N_VERBATIM","F007","notes_for_writer","F007 notes末尾『9月のFed利上げだけに帰属させない』と20字逐語一致(F010 notes も同趣旨)"),
 ("central_bank_mortgage","これは政策の目的・見込みであり、効果が既に実現したという確認ではない。","FACT_QUALIFIER","N_VERBATIM","F003","notes_for_writer","F003 notes に19字逐語一致。記述文(事実の確かさの限定)だが、台帳上は notes_for_writer 欄にある=欄名だけの分離だと制約側へ回る境界例"),
 ("central_bank_mortgage","個別の借り手全員に当てはまる支払額ではない。","FACT_QUALIFIER","CLAIM_FIELD","F007","scope","F007 scope『…全借り手の実際の支払額ではない』の言い換え。Fact側の範囲限定"),
 # 比較: 正常系
 ("meta","これは機能の試験に関する話であり、Muse全体の停止ではない。","FACT_QUALIFIER","N_PARAPHRASE","MUSE-HC-012","notes_for_writer","MUSE-HC-012 notes『「サービス全体を停止した」とは書かない』をB3が命令文ではなく記述文へ変換して取り込んだ例(命令文は0)"),
 ("openai_copyright","これらは原告側の主張であり、確定した事実ではない。","FACT_QUALIFIER","CLAIM_FIELD","F4","claim","Researcherが claim 本文に入れた限定。命令文は0"),
 ("streaming_price","確認したDisney+米国価格ページとReuters報道では、Disneyが今回の改定理由を明示した記述は確認できず","FACT_QUALIFIER","CLAIM_FIELD","F07","claim","Fact本文そのもの。命令文は0"),
]
def lines_of(path): return open(path, encoding="utf-8").read().replace("\r\n","\n").split("\n")
def find_line(lines, needle):
    for i, l in enumerate(lines, 1):
        if needle in l: return i
    return None
def lcs(a, b): return difflib.SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0,len(a),0,len(b)).size
rows = []
for th, sent, cls, origin, fid, field, note in E:
    bp = f"{R}/{th}/shared/brief_original.md"; lp = f"{R}/{th}/shared/ledger.txt"
    bl, ll = lines_of(bp), lines_of(lp)
    bline = find_line(bl, sent[:30])
    led_text = led_line = None
    if fid:
        cur = None
        for i, l in enumerate(ll, 1):
            m = re.match(r"^\[[^\]]+\]\s+([A-Za-z0-9_\-]+):", l)
            if m: cur = m.group(1)
            if cur == fid and l.startswith(f"  {field}:") : led_text, led_line = l.strip(), i
            if field == "claim" and cur == fid and m: led_text, led_line = l.strip(), i
    rows.append({"theme": th, "brief_file": bp, "brief_line": bline, "brief_sentence": sent, "class": cls,
                 "origin": origin, "ledger_file": lp, "ledger_fact": fid, "ledger_field": field, "ledger_line": led_line,
                 "ledger_text_verbatim": led_text, "common_substring_len": (lcs(sent, led_text) if led_text else None),
                 "judgement": note,
                 "in_research_draft": ("Ledger notes は Researcher draft と100%同一(ledger_provenance_check_01.json)" if th in ("semiconductor_earnings","central_bank_mortgage","openai_copyright","streaming_price","byd_recall") else "凍結旧台帳(draft JSON未保存)。同一 build_verified_ledger_text 規則で生成されるため notes は Researcher 出力そのもの(規則上の推定)")})
q5 = {"semiconductor_earnings","small_bag","space_weapons","hormuz","central_bank_mortgage"}
summary = {"writer_imperative_in_5_problem_themes": sum(1 for r in rows if r["theme"] in q5 and r["class"]=="WRITER_IMPERATIVE"),
           "writer_imperative_in_normal_themes_meta_byd_openai_streaming": sum(1 for r in rows if r["theme"] not in q5 and r["class"]=="WRITER_IMPERATIVE"),
           "origin_counts_for_writer_imperatives": {}}
for r in rows:
    if r["class"] == "WRITER_IMPERATIVE":
        summary["origin_counts_for_writer_imperatives"][r["origin"]] = summary["origin_counts_for_writer_imperatives"].get(r["origin"], 0) + 1
json.dump({"note": "判定は手作業(brief文を1件ずつledger.txtと突き合わせ)。ファイル/行/逐語/共通部分長は自動付与。Phase1 read-only、API 0件。",
           "summary": summary, "rows": rows}, open(os.path.join(H, "trace_5themes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False))
for r in rows: print(r["theme"][:10], r["class"][:8], r["origin"], r["ledger_fact"], r["brief_line"], r["ledger_line"], r["common_substring_len"])
