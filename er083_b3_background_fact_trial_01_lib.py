# -*- coding: utf-8 -*-
"""er083_b3_background_fact_trial_01_lib.py
FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01 委任_01(Phase A、2026-10-19)。Trial専用harness(DEV/Trial path)。

目的: B3(Production)の既存選定 -- DEVELOPER_MESSAGE・4テスト・「採用Fact下限2件」・再評価note・JSON schema -- を
**不変のまま**、ユーザー2026-10-19指示の補助判断
  「選んだストーリーを最低限理解するために不可欠な背景情報が欠けていないかを確認し、不足している場合に限ってFactを追加する」
を、Promptへの**追記**として候補(C1/C2/C3)化し、Baseline(追記なし=Production同一Prompt)と同条件で比較する。

Production非変更の方式(D-1):
  - Productionの `b3.run_storyline_b3_selection`(技術retry・下限2件の再評価・B3MinFactsStop)を**そのまま呼ぶ**。
  - 候補文は `AppendNoteClient`(clientのproxy)が、各 `responses.create` のuser入力末尾へ追記する。Productionコードは1文字も触らない。
    Baseline は追記が空文字 = Productionと**バイト同一のPrompt**(testで機械証明)。
  - 追加Factは `selected_fact_ids` に含め、reasonの先頭「【背景補完】」で区別する(schema・producer・Writer契約は不変)。
    背景確認の記録は recheck_note 先頭「【背景確認】」(Production側のrecheck_noteは6件以上のときのみ必須のsoft検査で、他の用途はない)。
  - 出力は `er083_output/` 配下のみ。`run_mey_01` 配下へは書かない(読取のみ)。Production runner・producer・契約・Writerは変更しない。
禁止: Production flag新設・既定値変更・runner配線・有料API(dry-runは0)。
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shutil
import time
from types import SimpleNamespace

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er012_e_family_entertainment_two_level_runner_01 as efam
import er019_family_x_storyline_b3_fact_selection_01 as b3
import er053_b3_deterministic_producer_01 as annot

TRIAL_ID = "FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01"
THEME_TAG = "FAMILY_X_B3_BACKGROUND_FACT_TRIAL_01"
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.path.join(ROOT, "er083_output", "b3_background_fact_trial_01")
PRODUCTION_MEY_RUN = os.path.join(ROOT, "er019_output", "middle_east_yemen_saudi", "run_mey_01")
DEFAULT_ARTICLE = "middle_east_yemen_saudi"
CANDIDATE_NAMES = ("baseline", "C1", "C2", "C3")

# 実測単価(JPY、出典 run_mey_01/cost.json by_stage_jpy: storyline_b3=20.287[B3 3回分の履歴], MEY_REGEN_02 B3 1回=約7.6, w1_r0+r1+r2=約40.5)。
# 委任文F-1記載の見積単価。予算guard(1callごと)にはB3 1回=7.6を使う。
EST_B3_CALL_JPY = 7.6
EST_W1_CHAIN_JPY = 14.6
TRIAL_FABLE_FRAME_JPY = 150.0

# ---------------------------------------------------------------------------
# 候補文(一般化された文言のみ。固有事例・特定Fact IDを含まない。assert_generalized で機械確認)
# ---------------------------------------------------------------------------
COMMON_GUARD = """\

【共通の注意(背景補完)】
- 追加してよいのは、Full Ledgerに実在するfact_idのうち、その前提をFact自身の記述として直接述べているFactだけです。Ledgerに書かれていない事実を、推測・創作・補完してはいけません。
- 関与している主体の帰属(誰が)、動機・理由(なぜ)、背景(それまでの経緯・状況)は別のものです。あるFactが述べているのがそのうちの一つだけなら、他の二つの裏付けとして扱ってはいけません。また、別の出来事を述べたFactから、このStorylineの出来事の関与主体や動機を推定して結び付けてはいけません。
- 補足として便利、詳しくなる、面白い、数字がある、というだけのFactの追加、ニュース全体の網羅、背景の詳細な解説は目的ではありません。追加するFactは、Storylineの焦点・筋・読み味を変えないものに限ります。
- 追加の上限は最大2件です。追加によって採用数が6件以上になる場合は、従来どおりrecheck_noteへ検討内容も記載してください。
- 追加したFactは selected_fact_ids と fact_tests(decision="selected")に含め、そのreasonの先頭に「【背景補完】」を付けて、「このFactが無いと何が理解できないか」を1文で書いてください。追加しなかったFactのreasonに【背景補完】は付けません。
- 背景確認の結果は、recheck_noteの先頭に「【背景確認】」を付けて1〜3文で必ず記録してください(追加不要 / 追加(fact_idと理由) / 不足(何が足りず、Ledger内に直接述べるFactが無い))。採用数が5件以下でも記入してかまいません。この場合、上の「5件以下の場合はnull」の指示より優先します。
- 「【背景補完】」で採用するFactには、4テストの「原則除外」の目安(YES/NOの組み合わせ)は適用しません(4テストの回答自体は事実に即して記入してください)。"""

C1_SPECIFIC = """\

【背景補完の確認(補助指示・候補C1)】
上記1〜5の選定(中心Storylineの決定、4テストの適用、採用/除外の決定)を、これまでの指示どおり先に完了してください。この補助確認のために、決定済みのStorylineと採用Factを変更してはいけません(この確認でストーリーの焦点を動かさない)。
そのうえで、次の1点だけを自問してください。
「決定したStorylineと採用Factだけを読む初見の読者は、そのStorylineを最低限理解するために不可欠な前提(例: その出来事に関与している主体が誰か、その出来事が何の流れの一部か)を欠いていないか」
- 欠いていない場合: 何も追加しません。これが既定です。
- 欠いている場合に限り、Full Ledgerから、その前提を直接述べているFactを原則1件(最大2件)だけ追加採用してよい。
- 欠いているが、Ledgerにその前提を直接述べるFactが無い場合: 何も追加しません。"""

C2_SPECIFIC = """\

【背景補完の確認(補助指示・候補C2)】
Test1〜4(定義・判定は変更しません)に加えて、全Factに次の第5のテストも適用してください。
Test5: そのFactが無いと、選んだStorylineを初見の読者が最低限理解できなくなるか(背景の不可欠性)。Storylineの理解に不可欠な前提(例: その出来事に関与している主体が誰か、その出来事が何の流れの一部か)を、Fact自身の記述として直接述べている場合のみYES。補足として便利・詳しくなる・面白いだけならNO。
- Storylineはこれまでどおり先に決定し、Test5はそのStorylineを変えずに適用してください。
- fact_testsのJSON schemaにTest5の欄はありません。Test5=YESのFactは、reasonの先頭に「【背景補完】」を付けてください(下の記載ルール)。Test5=NOのFactには何も付けません。
- Test5=YESのFactは、Test1〜4で「原則除外」となる場合でも採用してかまいません。ただし、Test5=YESで追加採用してよいのは、Test1〜4で採用したFactだけではStorylineを最低限理解できない場合に限ります。
- Test5=YESのFactがLedgerに無い場合: 何も追加しません。"""

C3_SPECIFIC = """\

【背景補完の確認(補助指示・候補C3)】
上記1〜5の選定を先に完了し、決定済みのStorylineと採用Factはこの確認のために変更しないでください。
そのうえで、決定したStorylineを初見で読んだ読者が最初に抱く素朴な疑問を、そのStorylineが自然に抱かせるものに限り、最大2つ挙げてください(型の例: 「誰が(何が)関わっているのか」「なぜそうなったのか」「これは何の流れの一部なのか」。Storylineが触れていない話題についての疑問を作ってはいけません)。
各疑問について、採用Factだけで答えられるかを確認します。
- 採用Factだけで答えられる: 何も追加しません。
- 答えられず、Full Ledgerのfact自身がその疑問に直接答えている: そのFactを疑問ごとに1件まで追加採用してよい。
- 答えられず、Ledgerにも直接答えるFactが無い: 何も追加せず、その疑問を「Ledger内に回答なし」として記録します(推測で答えない)。
- recheck_note(【背景確認】)には、挙げた疑問ごとに「疑問 / 採用Factで回答済 / 追加Fact(fact_id)で回答 / Ledger内に回答なし」を書いてください。"""

CANDIDATE_NOTES = {
    "baseline": "",
    "C1": C1_SPECIFIC + "\n" + COMMON_GUARD,
    "C2": C2_SPECIFIC + "\n" + COMMON_GUARD,
    "C3": C3_SPECIFIC + "\n" + COMMON_GUARD,
}

# 仕様文に含めてはならない固有事例(評価条件であり仕様文ではない。ユーザー§3)。Fact ID形式も禁止(誘導防止)。
BANNED_SPEC_TERMS = (
    "フーシ", "サウジ", "イエメン", "中東", "リヤド", "アブハ", "ダンマーム", "空港", "国連", "GACA", "ミサイル", "アラムコ",
    "攻撃", "紛争", "戦闘", "和平", "石油", "エネルギー",
)
BANNED_SPEC_REGEX = re.compile(r"(?<![A-Za-z0-9])F[0-9]{2}(?![0-9])")


def sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def note_sha(candidate: str) -> str:
    return sha256_text(CANDIDATE_NOTES[candidate])


def assert_generalized(note: str) -> list:
    """仕様文(候補追記)に固有事例・Fact IDが混入していないか。混入した語のリスト(空=OK)。"""
    hits = [t for t in BANNED_SPEC_TERMS if t in note]
    hits += BANNED_SPEC_REGEX.findall(note)
    return hits


def generalization_report() -> dict:
    return {c: assert_generalized(n) for c, n in CANDIDATE_NOTES.items()}


# ---------------------------------------------------------------------------
# 予算
# ---------------------------------------------------------------------------
class BudgetStop(RuntimeError):
    pass


def _jsonl(path: str) -> list:
    if not os.path.isfile(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                out.append(json.loads(ln))
    return out


def append_jsonl(path: str, row: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


TRIAL_THEMES = (THEME_TAG, "FAMILY_X_FACTLOCK_W1_PRODUCTION_01")   # B3候補 + 下流W-1 probe(Production Writerのtheme tag)


def cost_summary(log_path: str, theme: str | None = None) -> dict:
    """cost_log.jsonl(er005 cost logger形式)からJPYを集計。LLM(openai)のみ(web_searchは本Trialで使わないがwebsearch込み式を流用)。
    dry_run_stub行は実費0として別計上。"""
    price = efam._load_pricing()
    total, real_calls, stub_calls, by_stage = 0.0, 0, 0, {}
    for rec in _jsonl(log_path):
        if rec.get("theme") not in ((theme,) if theme else TRIAL_THEMES):
            continue
        if rec.get("dry_run_stub"):
            stub_calls += 1
            continue
        model = rec.get("model_id") or rec.get("model")
        if not (rec.get("provider") == "openai" and model):
            continue
        usd = ((rec.get("input_tokens") or 0) * price("openai", model, "input_tokens") / 1e6
               + (rec.get("output_tokens") or 0) * price("openai", model, "output_tokens") / 1e6
               + efam.web_search_call_usd(rec, price))
        jpy = usd * efam.USD_JPY
        total += jpy
        real_calls += 1
        st = str(rec.get("stage") or "UNTAGGED")
        by_stage[st] = round(by_stage.get(st, 0.0) + jpy, 3)
    return {"total_jpy": round(total, 3), "real_api_calls": real_calls, "stub_calls": stub_calls, "by_stage_jpy": by_stage}


class BudgetGuard:
    """呼出前に (これまでの実費 + 次の1call見込み) が budget_jpy 以内か判定。dry-runではAPIを呼ばないので常に通る。"""

    def __init__(self, log_path: str, budget_jpy: float, est_call_jpy: float, dry_run: bool):
        self.log_path, self.budget, self.est, self.dry = log_path, float(budget_jpy), float(est_call_jpy), dry_run

    def check(self, label: str) -> dict:
        if self.dry:
            return {"dry_run": True}
        spent = cost_summary(self.log_path)["total_jpy"]
        if spent + self.est > self.budget:
            raise BudgetStop(f"[STOP_BUDGET] {label}: spent={spent} + est_next_call={self.est} > budget={self.budget}")
        return {"spent": spent, "est_next": self.est, "budget": self.budget}


# ---------------------------------------------------------------------------
# 候補文を各callのuser入力末尾へ追記するproxy(Production関数はそのまま呼ぶ)
# ---------------------------------------------------------------------------
class AppendNoteClient:
    """`client.responses.create(**kw)` を中継し、kw["input"][-1](user message)の末尾へ note を追記する。
    note が空なら入力を一切変更しない(Baseline=Productionとバイト同一)。各callのprompt shaを記録する。"""

    def __init__(self, inner, note: str, guard: BudgetGuard | None = None, label: str = "b3"):
        self._inner, self._note, self._guard, self._label = inner, note or "", guard, label
        self.calls: list = []
        self.responses = SimpleNamespace(create=self._create)

    def _create(self, **kw):
        if self._guard is not None:
            self._guard.check(f"{self._label}#{len(self.calls) + 1}")
        inp = [dict(m) for m in kw["input"]]
        if self._note:
            if inp[-1].get("role") != "user":
                raise RuntimeError("[STOP] AppendNoteClient: 最終入力がuser messageでない")
            inp[-1]["content"] = inp[-1]["content"] + self._note
        kw2 = dict(kw)
        kw2["input"] = inp
        self.calls.append({
            "model": kw.get("model"), "reasoning": kw.get("reasoning"),
            "schema_name": kw["text"]["format"]["name"],
            "developer_sha256": sha256_text(inp[0]["content"]) if inp[0].get("role") == "developer" else None,
            "user_prompt_sha256": sha256_text(inp[-1]["content"]), "user_prompt_chars": len(inp[-1]["content"]),
            "user_prompt": inp[-1]["content"],
        })
        return self._inner.responses.create(**kw2)


# ---------------------------------------------------------------------------
# 出力分析(機械抽出のみ。内容の善し悪し=rubricはSonnet盲検評価)
# ---------------------------------------------------------------------------
SUPP_PREFIX = "【背景補完】"
CONFIRM_PREFIX = "【背景確認】"


def analyze_selection(parsed: dict, ledger_text: str, baseline_ids: list | None) -> dict:
    fts = parsed.get("fact_tests") or []
    selected = list(parsed.get("selected_fact_ids") or [])
    supp = [ft["fact_id"] for ft in fts if ft.get("decision") == "selected" and (ft.get("reason") or "").lstrip().startswith(SUPP_PREFIX)]
    note = (parsed.get("recheck_note") or "").strip()
    out = {
        "selected_fact_ids": selected,
        "excluded_fact_ids": [ft["fact_id"] for ft in fts if ft.get("decision") != "selected"],
        "supplement_fact_ids": supp,
        "supplement_reasons": {ft["fact_id"]: ft["reason"] for ft in fts if ft["fact_id"] in supp},
        "n_supplement": len(supp),
        "supplement_over_cap_2": len(supp) > 2,
        "supplement_not_in_selected": [i for i in supp if i not in selected],
        "background_confirm_note": note if note.startswith(CONFIRM_PREFIX) else None,
        "background_confirm_note_present": note.startswith(CONFIRM_PREFIX),
        "n_selected": len(selected),
        "verified_selected_n": b3.count_selected_verified(selected, ledger_text),
        "min2_satisfied": b3.count_selected_verified(selected, ledger_text) >= b3.MIN_VERIFIED_SELECTED_DEFAULT,
        "selected_storyline": parsed.get("selected_storyline"),
    }
    if baseline_ids is not None:
        out["added_vs_baseline"] = [i for i in selected if i not in baseline_ids]
        out["removed_vs_baseline"] = [i for i in baseline_ids if i not in selected]
        out["added_without_supplement_marker"] = [i for i in out["added_vs_baseline"] if i not in supp]
        out["baseline_ids"] = list(baseline_ids)
    return out


# ---------------------------------------------------------------------------
# 1候補の実行(Production関数をそのまま呼ぶ)
# ---------------------------------------------------------------------------
def prod_prompt_shas() -> dict:
    return b3.prompt_shas()


def read_text(p: str) -> str:
    with open(p, encoding="utf-8") as f:
        return f.read()


def write_text(p: str, s: str) -> None:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:   # Production save_textと同じ既定改行(brief等をbyte同一に)
        f.write(s)


def write_json(p: str, o) -> None:
    write_text(p, json.dumps(o, ensure_ascii=False, indent=2))


def assert_under_out_root(path: str, out_root: str) -> None:
    ap, ro = os.path.abspath(path), os.path.abspath(out_root)
    if os.path.commonpath([ap, ro]) != ro:
        raise RuntimeError(f"[STOP] 出力先が {ro} 配下でない: {ap}")
    if os.path.commonpath([ap, os.path.abspath(PRODUCTION_MEY_RUN)]) == os.path.abspath(PRODUCTION_MEY_RUN):
        raise RuntimeError(f"[STOP] Production run_mey_01配下への書込みは禁止: {ap}")


def baseline_ids_from_production(run_dir: str = PRODUCTION_MEY_RUN) -> list:
    ev = json.loads(read_text(os.path.join(run_dir, "storyline_b3", "fact_selection_evidence.json")))
    return list(ev["selected_fact_ids"])


def run_candidate(client, *, candidate: str, topic: str, ledger_text: str, cand_dir: str, out_root: str,
                  baseline_ids: list | None, budget_jpy: float, cost_log: str, dry_run: bool) -> dict:
    """1候補=Production `run_storyline_b3_selection` を1回(技術retry/再評価は既存ロジック)。
    out(cand_dir): research_ledger/verified_fact_ledger.txt, storyline_b3/{full_ledger,selected_brief.md,fact_selection_evidence,runtime_evidence}.json、
    producer出力(selected_brief_annotated.md 等)、trial_meta.json。"""
    if candidate not in CANDIDATE_NOTES:
        raise ValueError(f"unknown candidate {candidate}")
    assert_under_out_root(cand_dir, out_root)
    note = CANDIDATE_NOTES[candidate]
    hits = assert_generalized(note)
    if hits:
        raise RuntimeError(f"[STOP] 候補{candidate}の仕様文に固有事例/Fact IDが混入: {hits}")
    b3_model = routing.require_model("FAMILY_X_STORYLINE_B3", routing.PROCESS_MODEL_MAP["FAMILY_X_STORYLINE_B3"])
    guard = BudgetGuard(cost_log, budget_jpy, EST_B3_CALL_JPY, dry_run)
    proxy = AppendNoteClient(client, note, guard, label=f"b3:{candidate}")
    stage_dir = os.path.join(cand_dir, "storyline_b3")
    os.makedirs(stage_dir, exist_ok=True)
    write_text(os.path.join(cand_dir, "research_ledger", "verified_fact_ledger.txt"), ledger_text)
    t0 = time.time()
    status, stop_record, selection = "OK", None, None
    try:
        with cl.logging_context(THEME_TAG, f"b3_{candidate}"):
            selection = b3.run_storyline_b3_selection(
                proxy, topic, ledger_text, model=b3_model, effort=vfl01.REASONING_EFFORT,
                min_verified_selected=b3.MIN_VERIFIED_SELECTED_DEFAULT)
    except b3.B3MinFactsStop as stop:
        status, stop_record = "B3_MIN2_STOP:" + str(stop.record.get("reason")), stop.record
        write_json(os.path.join(stage_dir, "b3_min2_stop_record.json"), stop.record)
    if selection is not None and not str(selection.get("model") or "").startswith(b3_model):
        raise RuntimeError(f"[STOP] B3段の返却modelが{b3_model}で始まらない: {selection.get('model')!r}")
    meta = {
        "trial_id": TRIAL_ID, "candidate": candidate, "dry_run": dry_run, "status": status,
        "model_requested": b3_model, "effort": vfl01.REASONING_EFFORT, "topic": topic,
        "candidate_note_sha256": sha256_text(note), "candidate_note_chars": len(note),
        "production_prompt_shas": prod_prompt_shas(), "reeval_note_sha256": b3.reeval_note_sha(),
        "calls": [{k: v for k, v in c.items() if k != "user_prompt"} for c in proxy.calls],
        "wall_seconds": round(time.time() - t0, 2), "stop_record": stop_record,
        "ledger_sha256": sha256_text(ledger_text), "generalization_hits": hits,
    }
    if selection is not None:
        parsed = selection["parsed"]
        ledger_ids = selection["ledger_fact_ids"]
        write_json(os.path.join(stage_dir, "full_ledger.json"), b3.build_full_ledger_record(topic, ledger_text, ledger_ids))
        write_text(os.path.join(stage_dir, "selected_brief.md"), b3.build_selected_brief_markdown(selection))
        # Production runner(run_storyline_b3)と同一キーのevidence(producer入力契約。Trial固有情報は trial_meta.json へ分離)
        write_json(os.path.join(stage_dir, "fact_selection_evidence.json"), {
            "selected_storyline": parsed["selected_storyline"], "full_ledger_fact_ids": ledger_ids,
            "fact_tests": parsed["fact_tests"], "selected_fact_ids": parsed["selected_fact_ids"],
            "selected_fact_brief_text": parsed["selected_fact_brief"], "recheck_note": parsed["recheck_note"],
            "soft_warnings": selection["soft_warnings"], "min2_policy": selection["min2_policy"]})
        write_json(os.path.join(stage_dir, "runtime_evidence.json"), {
            "model_id_actual": selection["model"], "response_id": selection["response_id"],
            "latency_seconds": selection["latency_seconds"], "attempts": selection["attempts"],
            "retried": selection["retried"], "prompt_shas": selection["prompt_shas"], "attempts_log": selection["attempts_log"]})
        produced = annot.produce_annotated_b3(cand_dir)       # Production producerをそのまま(決定論・LLM 0)
        meta["analysis"] = analyze_selection(parsed, ledger_text, baseline_ids)
        meta["min2_policy"] = selection["min2_policy"]
        meta["soft_warnings"] = selection["soft_warnings"]
        meta["producer"] = {"annotated_md_sha256": produced["annotated_md_sha256"], "n_facts": produced["n_facts"],
                            "rules_sha256": produced["rules_sha256"]}
        meta["model_returned"] = selection["model"]
        meta["response_id"] = selection["response_id"]
        meta["b3_latency_seconds"] = selection["latency_seconds"]
    write_json(os.path.join(cand_dir, "trial_meta.json"), meta)
    return meta


# ---------------------------------------------------------------------------
# dry-run用 StubClient(API 0)。Baselineは保存済みProduction選定を再現し、候補は合成の補完行を追加して解析経路を通す
# ---------------------------------------------------------------------------
class StubB3Client:
    """OpenAI Responses互換の最小stub。保存済みrun_mey_01のB3出力から応答を合成する。**合成応答であり実LLM結果ではない**。"""

    def __init__(self, stored_evidence: dict, stub_usage_log: str, synthetic_supplement_id: str | None = None):
        self.ev = stored_evidence
        self.log = stub_usage_log
        self.supp = synthetic_supplement_id
        self.n = 0
        self.prompts: list = []
        self.responses = SimpleNamespace(create=self._create)

    def _create(self, **kw):
        self.n += 1
        prompt = kw["input"][-1]["content"]
        self.prompts.append(prompt)
        parsed = {
            "selected_storyline": self.ev["selected_storyline"],
            "fact_tests": json.loads(json.dumps(self.ev["fact_tests"])),
            "selected_fact_ids": list(self.ev["selected_fact_ids"]),
            "selected_fact_brief": self.ev["selected_fact_brief_text"],
            "recheck_note": self.ev.get("recheck_note"),
        }
        if "【背景補完の確認" in prompt and self.supp:        # 候補文あり: 合成の補完1件(解析経路の検証用)
            for ft in parsed["fact_tests"]:
                if ft["fact_id"] == self.supp:
                    ft["decision"] = "selected"
                    ft["reason"] = SUPP_PREFIX + "[stub合成] 解析経路の検証用。実LLM出力ではない。"
            parsed["selected_fact_ids"].append(self.supp)
            parsed["recheck_note"] = CONFIRM_PREFIX + "[stub合成] 追加1件。"
        elif "【背景補完の確認" in prompt:
            parsed["recheck_note"] = CONFIRM_PREFIX + "[stub合成] 追加不要。"
        text = json.dumps(parsed, ensure_ascii=False)
        in_tok, out_tok = len(prompt) // 2, 1800
        append_jsonl(self.log, {"theme": THEME_TAG, "stage": "dry_run_stub", "provider": "openai", "api": "responses.create",
                                "model_id": kw["model"], "attempt_number": self.n, "success": True,
                                "usage_source": "SYNTHETIC_DRYRUN_STUB", "input_tokens": in_tok, "output_tokens": out_tok,
                                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(), "dry_run_stub": True})
        return SimpleNamespace(output_text=text, model=kw["model"], id=f"stub_resp_{self.n}",
                               usage=SimpleNamespace(input_tokens=in_tok, output_tokens=out_tok))
