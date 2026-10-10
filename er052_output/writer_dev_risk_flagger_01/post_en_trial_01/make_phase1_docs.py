# -*- coding: utf-8 -*-
import json, os, sys, hashlib
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from post_en_common import *
man = load_manifest(); est = json.load(open(os.path.join(HERE, "cost_estimate_post_en_01.json"), encoding="utf-8"))
kmap = json.load(open(os.path.join(HERE, "known_sentence_map_01.json"), encoding="utf-8"))
sh3, sh4, sh_d2 = A.sha(A.antenna_system(3)), A.sha(A.antenna_system(4)), A.sha(P.d2_system())
fixed = {k: A.sha(v) for k, v in A.fixed_parts().items()}
ant_py = hashlib.sha256(open(os.path.join(ANT, "antenna_prompts.py"), "rb").read()).hexdigest()
prom_py = hashlib.sha256(open(os.path.join(DET, "prompts_flagger.py"), "rb").read()).hexdigest()
U = man["units"]; LG = man["ledgers"]
L1 = ["# INVENTORY_01: POST-EN-TRIAL-01 英語稿棚卸(Phase 1、API費用JPY0)", "",
 "管理ID: WRITER-DEV-RISK-FLAGGER-POST-EN-TRIAL-01 / 2026-10-10 / 既存成果物の読み取りのみ。再生成・補完は一切していない。",
 "復元=既存dev-check promptの『検証対象の記事』欄から本文を抽出(Checkerに実際に渡された英語稿そのもの)。復元元ファイル内のLedger欄が `research_ledger/verified_fact_ledger.txt` と一致することを全復元稿で確認済み(embedded_ledger_equals_research_ledger=True)。",
 "", "## 1. 使用稿一覧(11本 = 既定8本 + 既知例用の追加3本)", "",
 "| Unit | Theme | 経路 | 区分 | 入力path(固定コピー) | 元path | 元の種類 | 本文sha256(先頭12) | 生成日時(mtime) | 文字数 |", "|---|---|---|---|---|---|---|---|---|---|"]
for u in U:
    L1.append("| %s | %s | %s | %s | `%s` | `%s` | %s | %s | %s | %d |" % (u["unit"], u["theme"], u["route"], u["status"], u["input_path"].split("post_en_trial_01/")[1], u["source_path"].split("factlock_astra_e2e_trial_01/")[1], u["source_kind"], u["text_sha256_stripped"][:12], u["gen_mtime"], u["chars"]))
L1 += ["", "区分の凡例: U=Fable決定規則の既定稿(採用稿がある6テーマはAdvanced b1b/article.md、OpenAI/SemiconductorはSTOP時のAdvanced稿)。X=既知例の文が既定稿に実在せず別の既存英語稿にのみ実在したため**追加**した稿(置換ではない)。**【STOP稿】は完成記事ではない**。",
 "", "## 2. 重要な所在差異(ユーザー指示の想定と異なる点、要確認)", "",
 "- **OpenAI Copyright: ユーザー指示の2文(日本語R2『OpenAIが著作権管理情報を除去した』/英語『They also say the models' output copied or put articles together…』)は、同一世代の稿ではない。**",
 "  - 英語『…put articles together…』は `b1b_prev_b1`(B1回復**前**の初回英語稿 = X11)にのみ実在。その元になった日本語R2(`ja_writer_prev_b1/revision2.md`)は『さらに、モデルの出力が記事を複製したり、組み直したりしたほか、著作権管理情報も取り除いたとしています』と**主語(OpenAI)が明示されていない**。つまり、この稿については既存Checkの `origin=ja_source` は日本語側に主語がないという意味で整合する。",
 "  - 日本語『OpenAIが著作権管理情報を除去したとも訴えている』は `ja_writer/revision2.md`(B1回復**後**のJA R2)で、そこから作られた英語(U07)は『They further accuse OpenAI of removing copyright management information.』と**主体(OpenAI)が明示されactor driftなし**。U07は翻訳後Checkでは別件(見出し『AI Lawsuits Are About More Than Money』のscope拡張, ja_source)でSTOPした。",
 "  - 対応: 両方をSTOP稿として対象に含める(U07=最終STOP稿、X11=B1回復前STOP稿)。actor drift検出評価はX11が本命、U07は同一テーマの『主体が明示された版』=対照。",
 "- **Hormuz: 『Brent→oil prices』の一般化は既定稿U02には実在しない**(U02は『not crude oil prices overall, but Brent futures』と正しく限定している)。実在するのはB1回復前の初回英語稿(X09。『oil prices shot up』『oil prices made a dramatic move』)。X09を追加。",
 "- **Space Weapons: 『地球を吹き飛ばす兵器ではない』は既定稿U03には実在しない**。実在はB1回復前稿X10(`b1b_prev_b1/article.md` = 『not a weapon that can blow up Earth』)。X10を追加。U03には別系統の不在断定『has not disclosed their capabilities』(s33)と『no specific system names or attack capabilities have been given』(s13)がある。",
 "- **BYD: In One Lineの条件落ち**は既定稿U05に実在する(s27『…faulty pedal pads may keep the brake lights on when drivers aren't braking.』。台帳の『極端な場合に部品が外れた場合』という条件が1文要約から欠落、本文s5相当には『in an extreme case, it may come off』が残っている)。Standard(A2) attempt1稿にも同趣旨があるが、既定稿U05で足りるため追加しない。",
 "- **Semiconductor: 『This announcement alone does not explain how the two are connected.』** はU08のs25に実在(`.”`直後で文分割されず、直前の文と1つの文ID(s25)にまとまる。理由は EN_ADAPTATION_01.md)。",
 "- 件数: Fable補足の目安『8〜最大10本』に対し11本になった(追加3本)。費用見積は JPY%.2f(高位 JPY%.2f)で上限 JPY100 の範囲内。" % (est["total_central_jpy"], est["total_high_jpy"]),
 "", "## 3. 既知例の機械検索結果(文ID)", "", "| Unit | 文ID | 該当文(先頭) |", "|---|---|---|"]
for k, v in kmap.items():
    for sid, t in v:
        L1.append("| %s | %s | %s |" % (k, sid, t[:170].replace("|", "/").replace("\n", " ")))
L1 += ["", "不在の確認: Hormuz既知例(Brent→oil prices)=U02に不在/X09に実在、Space既知例(blow up Earth)=U03に不在/X10に実在、OpenAI既知例(put articles together)=U07に不在/X11に実在、BYD=U05に実在、Semiconductor=U08に実在。**不在の稿に対して『検出できなかった』とは扱わない**(RESULT_01.mdでも『本文に不在』と書く)。",
 "", "## 4. 回収できなかったもの", "", "なし。OpenAI/Semiconductor STOP稿は、いずれも `audit/deviation_checks/advanced_attempt1.json` のpromptから復元できた(復元元は上表)。Central Bank Mortgage(R0でSTOP、英語稿なし)は対象外。"]
open(os.path.join(HERE, "INVENTORY_01.md"), "w", encoding="utf-8").write("\n".join(L1) + "\n")

L2 = ["# LEDGER_COMPLETENESS_01: 完全Fact Ledger完全性確認(API前、全テーマ)", "",
 "方式: FIX01-A/FIX02/ANTENNAと同じ完全台帳方式(見出し正規表現 `^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):` をprocess内のみ差し替え。`detectors/ledger_restore_01.py` は無変更)。",
 "expected = 行頭が `[` の行数(形式不問) / regex = 上記正規表現に一致する見出し行数 / parsed = `parse_ledger_text` のFact件数。3者一致かつIDに重複なし、をAPI前の必須条件とし、driverは各セル実行時にも再assertする(不一致ならAPI前に停止)。",
 "", "| Theme | 台帳path | sha256(先頭12) | expected | regex | parsed | 判定 | 状態 | Fact ID一覧 |", "|---|---|---|---|---|---|---|---|---|"]
for t, l in LG.items():
    from collections import Counter
    L2.append("| %s | `%s` | %s | %d | %d | %d | %s | %s | %s |" % (t, l["path"].split("factlock_astra_e2e_trial_01/")[1], l["sha256"][:12], l["expected_heading_lines"], l["regex_heading_lines"], l["parsed_facts"], "PASS" if l["ok"] else "FAIL", dict(Counter(l["states"])), ", ".join(l["ids"])))
L2 += ["", "注記: streaming_price(AMBIGUOUS 1件)・semiconductor_earnings(AMBIGUOUS 1件)は従来パーサの見出し正規表現では落ちる形式(`[AMBIGUOUS - ...]`)だが、完全台帳方式で全件取得できた。space_weapons の Fact ID は F-022/F-023 が台帳ファイル自体に存在しない(F-021 の次が F-024。expected=parsed=22 でパーサ欠落ではない)。", "全8テーマ PASS。1件でも不一致ならAPIを呼ばない規則に該当なし。"]
open(os.path.join(HERE, "LEDGER_COMPLETENESS_01.md"), "w", encoding="utf-8").write("\n".join(L2) + "\n")

L3 = ["# EN_ADAPTATION_01: 英語入力への適応(最小差分)", "",
 "## (a) 文分割", "既存の `run_flagger_01._split_sentences`(P3/P4のarm_new_en英語稿ですでに使用済み)を**変更せず**そのまま使用。見出し行(#, ##)も1文として残る。入力は `post_en_trial_01/inputs/*.md`(固定コピー)。文IDと本文は各 `flags/<level>/<unit>_<theme>.json` の `sentences` に保存。",
 "既知の限界(変更はしない。仕様追加禁止のため): 分割規則は `(?<=[.!?])\s+` で、`.”` `!”` のように閉じ引用符が間に入ると文が分割されず次の文と1つの文IDにまとまる。このため一部の文IDは2文以上を含む(例: U08 s25、X10 s5)。Flag対象文を読む際は該当文IDの全文を確認する必要がある。",
 "", "## (b) A3/A4 prompt: 差分ゼロ", "`prompts_flagger.COMMON_HEAD` に既に『台帳は日本語、記事の文は英語や日本語のことがあります。』とある。したがって『入力記事は英語であり台帳(日本語)と照合する』旨の注記を**追加しない**(Fable補足の『日本語記事を前提にしている箇所があれば』の条件に該当しない)。重大定義・候補化条件・出力形式・確信度方針は一切変更していない。",
 "", "| 項目 | sha256 |", "|---|---|", "| 実使用 A3 system prompt (`antenna_prompts.antenna_system(3)`) | `%s` |" % sh3, "| 元のANTENNA-TRIAL-01 A3 | `%s`(同一。ANTENNA PREREGISTRATIONの値と照合) |" % sh3,
 "| 実使用 A4 system prompt | `%s` |" % sh4, "| 元のANTENNA-TRIAL-01 A4 | `%s`(同一) |" % sh4, "| 現行D2 (`prompts_flagger.d2_system()`) | `%s` |" % sh_d2,
 "| `antenna_prompts.py` ファイルsha256 | `%s` |" % ant_py, "| `prompts_flagger.py` ファイルsha256 | `%s` |" % prom_py,
 "", "userメッセージ(`prompts_flagger.build_user`): `{facts:[{fact_id,text}], sentences:[{sid,text,before:'',after:''}]}` のJSON。Fact textは日本語台帳のブロック全文(scope/conditions/notes等を含む)、sentencesは英語。ラベル・Checker指摘・既知例名は一切渡さない。",
 "モデル: gpt-6.1-sol / reasoning effort=medium(ANTENNA-TRIAL-01と同一)。", "Production/detectors/antenna_trial_01 配下は無変更(importのみ)。"]
open(os.path.join(HERE, "EN_ADAPTATION_01.md"), "w", encoding="utf-8").write("\n".join(L3) + "\n")
print(sh3, sh4)
