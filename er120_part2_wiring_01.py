# -*- coding: utf-8 -*-
"""PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_03 / GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02: Part 2(Grammar & Sentence Structure)のX/Y/Z runner共通の接続層。決定論部分はAPI 0。

moduleの責務分担:
  er120_part2_grammar_production_01 : Part 2の中身(Prompt・候補・選定規則・Step B・fail-closed検査)。Prompt/閾値は無変更
  er119_grammar_review_01           : 文法Human Review(kind="grammar")の状態・操作(er119共通核に接続)
  本module                          : runner(er019/er026/er121)から呼ぶ薄い層。候補段階(抽出)/事前生成段階(全候補のStep B)/finalize段階(LLM 0)/使う側の検査/ページ描画/フォーム用データ

段階(全level共通。levelは必須引数 'b1b'=Advanced / 'a2'=Standard。契約=docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/SCHEMA_CONTRACT_01.md):
  candidate_stage : 本文確定直後に実行(Step A''。resumeはAPI 0)。未確定ならPENDINGを返す
  pregen_stage    : 候補抽出の直後・待機(rc=4)の前に実行(**Step Bの唯一の呼出点**。全候補<=8を直列に事前生成。失敗はpart2_failed.json+STOP、再開は未生成分のみ)
  finalize_stage  : 確定後。**LLM 0 call**(事前生成物/凍結値から決定論で組立。無ければfail-closed)。legacy(review v1かつresult v1の既存run)は再利用のみ
  require_final   : 使う側(TTS/assembly/pages/player/公開ページ)の入口。無い/古い/未確定はfail-closed

KPと文法のpendingは1つの review_request.md にまとめ、rc=4を1回にする(M-3)。
"""
from __future__ import annotations

import json
import os
from typing import Callable, Optional

import er119_grammar_review_01 as gr
import er119_kp_human_review_01 as rv
import er120_part2_grammar_production_01 as g

RESULT_PATH = lambda study_dir: f"{study_dir}/{g.RESULT_FILENAME}"   # noqa: E731
PENDING_MARKER = rv.PENDING_MARKER


class Part2NotConfirmed(g.Part2Stale):
    """文法のHuman確認待ち/再選定中/再抽出待ち/Part 1訳との食い違いISSUE(失敗ではなく待機。rc=4)。Part2Staleを継承するので『前進不可』としてfail-closedにもなる。"""

    def __init__(self, message: str, pending: Optional[list] = None):
        super().__init__(message)
        self.pending = pending or []


def _cc():
    """確定内容保護の共通核(er128)。遅延import(循環回避)。flagの読取点は er128.protection_enabled() のみ。"""
    return rv._cc()   # er119共通核の遅延import口を使う(A/B/C・共有moduleがer128を直接importしない隔離規約)


def _translate_cc(fn):
    """er128の例外をPart 2の既存例外体系へ写す: INTEGRITY=Part2Stale(STOP)、ISSUE=Part2NotConfirmed(待機 rc=4)。確定内容は変更しない。"""
    try:
        return fn()
    except rv.ConfirmedContentIntegrityViolation as e:
        raise g.Part2Stale(str(e)) from e
    except rv.ConfirmedContentIssue as e:
        raise Part2NotConfirmed(str(e), []) from e


def label_for(text_or_title: str) -> str:
    """Step A''のlabel(作品名/タイトル。1行)。本文先頭の `# ` 行、無ければ与えられた文字列の1行目。"""
    for ln in (text_or_title or "").splitlines():
        ln = ln.strip()
        if ln.startswith("# "):
            return ln[2:].strip() or "Untitled"
    first = (text_or_title or "").strip().splitlines()[0].strip() if (text_or_title or "").strip() else ""
    return first or "Untitled"


def stage_names(level: str) -> dict:
    """stage台帳(Y/Z)用の名前。cand=候補抽出 / expl=解説事前生成 / final=finalize(LLM 0)。旧b1b名(part2_cand_b1b/part2_b1b)と同一。"""
    g.level_name(level)
    return {"cand": f"part2_cand_{level}", "expl": f"part2_expl_{level}", "final": f"part2_{level}"}


def study_dir_for(family: str, out_dir: str, level: str) -> str:
    """level別のstudy dir(単一関数)。X: <out>/<level>/study_text / Y,Z: Adv=<out>/study_text(既存)・Std=<out>/a2/study_text。"""
    g.level_name(level)
    f = (family or "").lower()
    if f == "x":
        return f"{out_dir}/{level}/study_text"
    if f in ("y", "z"):
        return f"{out_dir}/study_text" if level == "b1b" else f"{out_dir}/a2/study_text"
    raise g.Part2InputError(f"familyは x|y|z のいずれか: {family!r}")


# ============================================================
# 段階A: 候補抽出+待機/自動確定の評価
# ============================================================
def candidate_stage(study_dir: str, *, level: str, run_dir: str, family: str, slug: str, paragraphs: list, label: str, run_hint: Optional[str] = None,
                    extract_call_fn: Optional[Callable] = None, client=None, budget_guard: Optional[Callable] = None,
                    force_extract: bool = False) -> dict:
    """候補抽出。**この後・待機(rc=4)に入る前に pregen_stage を通すこと**(candidate_and_pregen_stage が両方を行う)。"""
    return _translate_cc(lambda: gr.ensure_grammar_review(study_dir, level=level, run_dir=run_dir, family=family, slug=slug, paragraphs=paragraphs, label=label,
                                                          run_hint=run_hint, extract_call_fn=extract_call_fn, client=client, budget_guard=budget_guard,
                                                          force_extract=force_extract))


def cand_input_sha(study_dir: str, paragraphs: list, label: str, prov_entry: Optional[dict] = None) -> str:
    """Y/Z `part2_cand_<level>` のinput_sha(来歴照合用)。通常は g.cand_stage_input_sha(本文sha+label+抽出signature[Prompt・model])。
    ユーザー確定済みの文法(KP-CONFIRMED-CONTENT-PROTECTION-01 M6)があり、候補docの本文shaが現本文と一致する場合に限り、Prompt/model/routingだけの変更で
    来歴が親sha不一致STOPにならないよう、記録済みの入力shaを据え置く(確定済みの文法は再抽出しない。--regenerate-stage part2_cand_<level> はrevoke必須で拒否されるため、
    据え置かないと解消できないSTOPになる)。本文が変わった場合・確定が無い場合は従来どおり。"""
    sha = g.cand_stage_input_sha(paragraphs, label)
    if prov_entry is not None and prov_entry.get("input_sha256") != sha:
        doc = gr.load_candidates(study_dir)
        if doc is not None and doc.get("text_sha256") == g.text_sha256(paragraphs) and _translate_cc(lambda: _cc().grammar_state(study_dir)) is not None:
            return prov_entry["input_sha256"]
    return sha


def cand_marker(study_dir: str, paragraphs: list, label: str, *, level: str) -> str:
    """Y/Z `part2_cand_<level>` stageの凍結出力(来歴用marker。reselectで候補docが変わってもこのmarkerは変わらない)。"""
    return json.dumps({"stage": stage_names(level)["cand"], "input_sha256": g.cand_stage_input_sha(paragraphs, label), "text_sha256": g.text_sha256(paragraphs),
                       "label": label, "extract_signature": g.extract_signature(paragraphs, label), "note": "候補docと確定は grammar_candidates.json / grammar_human_review.json"},
                      ensure_ascii=False, indent=2)


# ============================================================
# 段階A2: 全候補のStep B事前生成(Step Bの唯一の呼出点)
# ============================================================
def _selected_ids_of(review: dict) -> list:
    sel = review.get("selection") or {}
    if review.get("schema") == g.SCHEMA_REVIEW_V2:
        return list(sel.get("candidate_ids") or [])
    cid = sel.get("candidate_id")
    return [cid] if cid else []


def _resolve_failed_record(study_dir: str) -> None:
    fp = f"{study_dir}/{g.FAILED_FILENAME}"
    if os.path.exists(fp):
        os.replace(fp, fp.replace(".json", ".resolved.json"))   # 成功したら失敗記録は解決済みへ退避(削除しない)


def pregen_stage(study_dir: str, *, level: str, next_command: str, run_hint: Optional[str] = None, explain_call_fn: Optional[Callable] = None, client=None,
                 budget_guard: Optional[Callable] = None) -> dict:
    """候補ごとに解説を事前生成(直列・PREGEN_MAX=2=Top1/Top2のみ・signature一致で再利用=API 0・原子的更新)。失敗=part2_failed.json(stage=part2_expl_<level>)+例外(STOP rc=3。
    成功分は保持され、再開は未生成分のみ)。**不完全なまま待機(rc=4)/フォームへ進まない**。
    - 未確定のreview: 全候補(Top1/Top2=先頭PREGEN_MAX件)。source=pregen(ユーザー提示対象)
    - 確定済みのreview(v1進行中run・auto採用[TOP1のみ]・確定済み): 選定済みidだけ。source=stepB_generated(ユーザー未閲覧)。凍結値のある候補は生成しない
    - 候補0件・選定0件でも空の事前生成物を書く(「事前生成を通った」印。v2成果物があるのに無い場合はINTEGRITY)
    """
    doc, review = gr.load_candidates(study_dir), gr.load_review(study_dir)
    if doc is None or review is None:
        raise g.Part2Stale("文法の候補/reviewがありません(候補抽出stageが未実行)")
    g.check_doc_level(doc, level)
    ex0 = gr.load_explanations(study_dir)
    confirmed = review["status"] in rv.FORWARD_STATUSES_BY_KIND[rv.KIND_GRAMMAR]
    ids, source = None, "pregen"
    if confirmed:
        source = "stepB_generated"
        ids = _selected_ids_of(review)
        fz = _frozen_loaded(study_dir) or []
        have = {f.get("candidate_id") for f in fz}
        ids = [i for i in ids if i not in have]
    try:
        ex, st = g.pregen_explanations(doc, ex0, level=level, ids=ids, source=source, call_fn=explain_call_fn, client=client, budget_guard=budget_guard,
                                       on_progress=lambda e: g.write_explanations(study_dir, e))
    except (g.Part2Error, g.Part2InputError) as exc:
        g.write_failed_record(study_dir, exc, next_command=next_command, stage=stage_names(level)["expl"])
        raise
    strip = lambda e: {k: v for k, v in (e or {}).items() if k != "written_at"}   # noqa: E731
    if strip(ex) != strip(ex0):
        g.write_explanations(study_dir, ex)
    ok_ids = ids if confirmed else None
    g.validate_explanations(ex, doc, level=level, next_command=next_command, ids=ok_ids)
    _resolve_failed_record(study_dir)
    if not confirmed:
        gr.write_request_for_state(study_dir, doc, review, level=level, run_hint=run_hint or study_dir)   # 解説全文付きの依頼書へ更新(古い/未完成の依頼書を残さない)
    return {"explanations": ex, "generated": st["generated"], "reused": st["reused"], "skipped_over_cap": list(ex.get("skipped_over_cap") or []), "confirmed": confirmed}


def candidate_and_pregen_stage(study_dir: str, *, level: str, run_dir: str, family: str, slug: str, paragraphs: list, label: str, next_command: str,
                               run_hint: Optional[str] = None, extract_call_fn: Optional[Callable] = None, explain_call_fn: Optional[Callable] = None, client=None,
                               budget_guard: Optional[Callable] = None, force_extract: bool = False) -> dict:
    """候補抽出 -> 事前生成 を1回で行う(adapter用の推奨入口)。待機(rc=4)の判断は戻り値のstateで(事前生成完了後)。"""
    res = candidate_stage(study_dir, level=level, run_dir=run_dir, family=family, slug=slug, paragraphs=paragraphs, label=label, run_hint=run_hint,
                          extract_call_fn=extract_call_fn, client=client, budget_guard=budget_guard, force_extract=force_extract)
    pre = pregen_stage(study_dir, level=level, next_command=next_command, run_hint=run_hint or run_dir, explain_call_fn=explain_call_fn, client=client,
                       budget_guard=budget_guard)
    return dict(res, pregen=pre)


# ============================================================
# 凍結値(KCP M6)の読み出し: list[item]として扱う。KCPがv2(items[])を実装済みならそれを使い、v1(単一)のみの間は1件のみ許可し、複数はfail-closed
# ============================================================
def _frozen_loaded(study_dir: str) -> Optional[list]:
    """凍結値(読み出しのみ。凍結の新規作成はしない)。無い/確定レコード無し=None。"""
    cc = _cc()
    fn = getattr(cc, "load_frozen_grammar_items", None)
    if fn is not None:
        return _translate_cc(lambda: fn(study_dir))
    fz = _translate_cc(lambda: cc.load_frozen_grammar(study_dir))
    if fz is None:
        return None
    return list(fz["items"]) if isinstance(fz, dict) and isinstance(fz.get("items"), list) else [fz]


def _ex_excluding_frozen(ex: Optional[dict], frozen: Optional[list], review: Optional[dict] = None) -> Optional[dict]:
    """M6(確定した文法はmodel/Prompt変更で失効しない): 凍結(確定)済みの候補の事前生成物itemは explain_signature(model依存)の検査対象から外す
    (凍結候補の正は frozen:<sha>=g.require_fresh_part2 / build_result_v2 側)。凍結(=ユーザー確定)がある場合は、確定後は使われない非選択候補(Top2等)の
    提示用itemも同様に対象外(確定後にmodelが変わっても、使われないitemのsignatureでStaleにしない)。
    元のexplanations_sha256(書換え検知)は先に全itemで検証し、除外後の集合に対して再計算した値で置き換える。凍結が無ければexをそのまま返す(挙動不変=保護OFF対照)。"""
    fz_ids = {f.get("candidate_id") for f in frozen or [] if isinstance(f, dict)}
    if not ex or not fz_ids or ex.get("schema") != g.SCHEMA_EXPLANATIONS:
        return ex
    items = ex.get("items") or []
    if ex.get("explanations_sha256") != g.explanations_digest(items):
        raise g.Part2Stale("文法解説の事前生成物のexplanations_sha256が一致しません(書換えの疑い)")
    sel_ids = set(_selected_ids_of(review)) if review else set()
    kept = [i for i in items if i.get("candidate_id") not in fz_ids and (not sel_ids or i.get("candidate_id") in sel_ids)]
    if len(kept) == len(items):
        return ex
    return dict(ex, items=kept, explanations_sha256=g.explanations_digest(kept))


def _frozen_for_selected(study_dir: str, selected: list) -> Optional[list]:
    """選定候補の凍結値を返す。凍結が無く、フォームで解説全文を見せていた(explanation_status=provided)場合は、その全文を凍結値にする(Step Bを呼ばない)。
    確定レコード(KCP)が無ければNone。KCPがv1のみの間に複数の選定がある場合はPart2Stale(fail-closed。委任_03/04でKCP v2を実装)。"""
    cc = _cc()
    if _translate_cc(lambda: cc.grammar_state(study_dir)) is None:
        return None
    fn_items = getattr(cc, "load_frozen_grammar_items", None)
    if fn_items is not None:
        cur = _translate_cc(lambda: fn_items(study_dir))
        if cur is None:
            fn_freeze = getattr(cc, "freeze_from_sidecar_items", None)
            if fn_freeze is not None:
                cur = _translate_cc(lambda: fn_freeze(study_dir, selected))
        return cur
    if len(selected) > 1:
        raise g.Part2Stale("確定内容保護(KCP)が複数の文法の凍結にまだ対応していません(load_frozen_grammar_items未実装)。fail-closed。委任_03/04でKCPを複数item化してください")
    if not selected:
        return None
    fz = _translate_cc(lambda: cc.load_frozen_grammar(study_dir) or cc.freeze_from_sidecar(study_dir, selected[0]))
    return [fz] if fz is not None else None


def _v1_view(result: dict) -> dict:
    """KCPのv1関数(verify_part2/freeze_part2_result)へ渡す単件形。0件/1件のみ。"""
    items = g.result_items(result)
    if len(items) > 1:
        raise g.Part2Stale("確定内容保護(KCP)が複数の文法の検証にまだ対応していません。fail-closed。委任_03/04でKCPを複数item化してください")
    if not items:
        return {"status": result.get("status"), "selection": result.get("selection")}
    it = items[0]
    return {"status": "SELECTED", "selection": it["selection"], "explanation_md": it["explanation_md"], "translation_ja": it["translation_ja"], "sections": it["sections"],
            "ref_ja": it.get("ref_ja")}


def _cc_verify_and_freeze(study_dir: str, result: dict, *, frozen: Optional[list], freeze: bool) -> None:
    """G4: 結果が確定した文法・解説全文と一致すること(確定レコード無し=何もしない)。freeze=True かつ凍結が無ければ、通常の検査を通った今回の結果を凍結(出所=stepB_generated_frozen)。"""
    cc = _cc()
    fn_verify = getattr(cc, "verify_part2_items", None)
    fn_freeze = getattr(cc, "freeze_part2_result_items", None)
    if fn_verify is not None:
        if freeze and frozen is None and fn_freeze is not None:
            _translate_cc(lambda: fn_freeze(study_dir, result))
        _translate_cc(lambda: fn_verify(study_dir, result))
        return
    if _translate_cc(lambda: cc.grammar_state(study_dir)) is None:
        return
    view = _v1_view(result)
    if freeze and frozen is None:
        _translate_cc(lambda: cc.freeze_part2_result(study_dir, view))
    _translate_cc(lambda: cc.verify_part2(study_dir, view))


def _check_translation(study_dir: str, result: dict, ref_ja_pool: Optional[dict], *, level: str, frozen: Optional[list]) -> None:
    """Opus O-1: Part 1訳(参考訳pool)とStep B訳の食い違い(凍結の有無に関係なく)はISSUE(rc=4)。解消手段=別候補を選ぶ/省略、またはユーザー了承(op_accept_translation_diff)。"""
    issues = g.translation_issues(result, ref_ja_pool, gr.load_translation_acks(study_dir))
    if not issues:
        return
    path = gr.write_translation_issue(study_dir, issues, level=level)
    fz_by = {f.get("candidate_id"): f for f in frozen or []}
    for i in issues:   # 凍結済み(KCP確定)の候補は、KCP側のISSUE(確定内容の再確認)にも記録する
        if i["candidate_id"] in fz_by:
            _translate_cc(lambda: _cc().pool_ref_ja_issue(study_dir, fz_by[i["candidate_id"]], i["part1_ja"]))
    ids = ", ".join(i["candidate_id"] for i in issues)
    raise Part2NotConfirmed(
        f"Part 1の日本語訳と、文法解説の【日本語訳】が食い違っています({ids})。確定した解説を黙って作り直しません。詳細: {path}。"
        "解消手段: (a)別の文法を選ぶ/省略する(grammar-select)、(b)ユーザーが了承して現状のまま進める(op_accept_translation_diff。--user-ref必須・記録が残る)", [])


# ============================================================
# 段階B: finalize(LLM 0 call)
# ============================================================
def _replay_inputs(review: dict):
    """確定recordから er120.finalize_part2(_v2) に渡す (review=決定dict|None, mode='wait'|宣言dict) を復元する。"""
    st = review["status"]
    if st == rv.ST_AUTO:
        return None, review["mode_declaration"]
    if st == rv.ST_NO_CANDIDATE:
        return None, "wait"
    d = review.get("decision")
    if not d:
        raise g.Part2Stale("Part 2の確定recordにdecisionがありません(手編集の疑い)")
    return dict(d), "wait"


def _is_legacy_postselect(review: dict, result: Optional[dict]) -> bool:
    """旧「選定後にStep B」で作られた既存run: review v1 **かつ** result v1 の両方が揃うときだけ。v2成果物が一部でもある場合は含めない(Opus O-3: 事前生成物の欠落で旧経路へ落とさない)。"""
    return bool(review.get("schema") == g.SCHEMA_REVIEW and result and result.get("schema") == g.SCHEMA_RESULT)


def _check_integrity(study_dir: str, review: dict, result: Optional[dict], ex: Optional[dict]) -> None:
    v2_art = (review.get("schema") == g.SCHEMA_REVIEW_V2 and review["status"] in rv.FORWARD_STATUSES_BY_KIND[rv.KIND_GRAMMAR]) \
        or bool(result and result.get("schema") == g.SCHEMA_RESULT_V2)
    if v2_art and ex is None:
        raise g.Part2IntegrityError("INTEGRITY: 文法のv2成果物(確定/結果)があるのに事前生成物(grammar_explanations.json)がありません"
                                    "(copy-runでの欠落または手動削除の疑い)。旧経路・再生成へは落とさず停止します。状況をFableへ報告してください")


def finalize_stage(study_dir: str, *, level: str, paragraphs: list, label: str, ref_ja_pool: Optional[dict] = None, write: bool = True) -> dict:
    """確定済みの文法reviewから part2_result.json(+md)を作る(write=Falseなら保存せずresultを返す。Zはensure_stageが保存する)。**LLM 0 call**(引数にLLM関数を持たない)。
    解説は 凍結値 > 事前生成物 の順に引き、無ければPart2Stale(その場でStep Bを呼ばない)。legacy(review v1かつresult v1)は既存resultの再利用のみ。
    待機系statusなら Part2PendingReview(出力ファイルを書く前に抜ける)。Part 1訳との食い違い=Part2NotConfirmed(rc=4)。返り値: {"result","status","reused","review","path"}"""
    doc, review = gr.load_candidates(study_dir), gr.load_review(study_dir)
    if doc is None or review is None:
        raise g.Part2Stale("文法の候補/reviewがありません(候補抽出stageが未実行)")
    g.check_doc_level(doc, level)
    if review["status"] not in rv.FORWARD_STATUSES_BY_KIND[rv.KIND_GRAMMAR]:
        raise g.Part2PendingReview(review["status"], g.review_request(doc), doc)
    if review["candidates_sha256"] != doc["candidates_sha256"] or review["text_sha256"] != doc["text_sha256"]:
        raise g.Part2Stale("文法の確定が現在の候補docに対するものではありません")
    dec, mode = _replay_inputs(review)
    cached_result = g.load_json(RESULT_PATH(study_dir))
    if _is_legacy_postselect(review, cached_result):
        out = _finalize_legacy_v1(study_dir, doc, review, dec, mode, cached_result, level=level, paragraphs=paragraphs, label=label, ref_ja_pool=ref_ja_pool)
        out["path"] = "legacy_v1"
    else:
        ex = gr.load_explanations(study_dir)
        _check_integrity(study_dir, review, cached_result, ex)
        sel0 = g.select_from_candidates_v2(doc, dec, mode)
        selected = g.order_by_text(sel0.get("selected") or [])
        fz = _frozen_for_selected(study_dir, selected) if sel0.get("status") == "SELECTED" else None
        if ex is not None:
            g.validate_explanations(_ex_excluding_frozen(ex, fz, review), doc, level=level, next_command="解説の事前生成stageを実行してください", require_complete=False)
        out2 = g.finalize_part2_v2(paragraphs, label, level=level, candidates_doc=doc, review=dec, mode=mode, explanations=ex, cached_result=cached_result,
                                   frozen_items=fz, prior_history=None, record_schema=review.get("schema"))
        rec = out2["review_record"]
        if rec["selection_signature"] != review["selection_signature"]:   # 突合: 保存した確定recordとer120が再導出した署名は一致するはず
            raise g.Part2Stale("文法の確定recordの署名が、er120の再導出と一致しません(手編集またはcodeの不整合)。fail-closed")
        res = out2["result"]
        _check_translation(study_dir, res, ref_ja_pool, level=level, frozen=fz)
        _cc_verify_and_freeze(study_dir, res, frozen=fz, freeze=True)   # 通常の検査を通った今回の結果を凍結(確定レコードのある文法のみ)+G4
        out = {"result": res, "status": out2["status"], "reused": bool(res.get("reused_from_previous_run")), "review": review, "path": "v2"}
    if write:
        res = out["result"]
        if not out["reused"] or not os.path.exists(RESULT_PATH(study_dir)):
            g.write_artifacts(study_dir, None, res)
        elif g.render_markdown(res) and not os.path.exists(f"{study_dir}/{g.PART2_FILE_STEM}.md"):   # 0件=mdを書かない(固定文面なし)。mdが必要な結果だけ補完
            g.write_artifacts(study_dir, None, res)
        elif not g.render_markdown(res):
            g.retire_part2_md(study_dir)   # 0件なのに以前のmd(旧固定文面など)が残っていれば退避(削除しない。M-6)
    return out


def _finalize_legacy_v1(study_dir, doc, review, dec, mode, cached_result, *, level, paragraphs, label, ref_ja_pool) -> dict:
    """旧フロー(選定後Step B)で作られた既存run(review v1かつresult v1)の再利用。Step Bは呼ばない(一致しなければPart2Stale)。"""
    cc = _cc()
    fz = None
    sel0 = g.select_from_candidates(doc, dec, mode)
    if sel0.get("status") == "SELECTED":
        fz = _translate_cc(lambda: cc.load_frozen_grammar(study_dir) or cc.freeze_from_sidecar(study_dir, sel0["candidate"]))
        if fz is not None:
            msg = cc.pool_ref_ja_issue(study_dir, fz, g.lookup_ref_ja(sel0["candidate"]["sentence"], ref_ja_pool))
            if msg:
                raise Part2NotConfirmed(msg, [])
    out = g.finalize_part2(paragraphs, label, level=level, candidates_doc=doc, review=dec, mode=mode, cached_result=cached_result, ref_ja_pool=ref_ja_pool,
                           ng=(), prior_history=None, frozen=fz)
    rec = out["review_record"]
    if rec["selection_signature"] != review["selection_signature"]:
        raise g.Part2Stale("文法の確定recordの署名が、er120の再導出と一致しません(手編集またはcodeの不整合)。fail-closed")
    res = out["result"]
    if fz is None:
        _translate_cc(lambda: cc.freeze_part2_result(study_dir, res))
    _translate_cc(lambda: cc.verify_part2(study_dir, res))   # G4
    return {"result": res, "status": out["status"], "reused": bool(res.get("reused_from_previous_run")), "review": review}


def write_md(study_dir: str, result: dict) -> str:
    """study_text/ のPart 2 markdown(決定論の描画)。Zはresult JSONをensure_stageが書くため、mdだけここで書く。
    0件(描画が空)はmdを書かない(固定文面・プレースホルダーを残さない)。以前のmdが残っていれば退避する(削除しない)。戻り=mdのpath(0件はNone)。"""
    os.makedirs(study_dir, exist_ok=True)
    path = f"{study_dir}/{g.PART2_FILE_STEM}.md"
    text = g.render_markdown(result)
    if not text:
        g.retire_part2_md(study_dir)
        return None
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


# ============================================================
# 使う側の入口検査
# ============================================================
def load_state(study_dir: str):
    return gr.load_candidates(study_dir), gr.load_review(study_dir), g.load_json(RESULT_PATH(study_dir))


def artifacts_exist(study_dir: str) -> bool:
    return any(os.path.exists(p) for p in (gr.paths(study_dir)["candidates"], gr.paths(study_dir)["review"], RESULT_PATH(study_dir)))


def require_final(study_dir: str, paragraphs: list, label: str, *, level: str, next_command: str, where: str = "", ref_ja_pool: Optional[dict] = None) -> dict:
    """TTS/assembly/pages/player/公開ページ builder の入口。未確定=Part2NotConfirmed(待機)、無い/古い/不整合=Part2Stale(STOP)。v2成果物があるのに事前生成物が無い=INTEGRITY。resultを返す。"""
    doc, review, result = load_state(study_dir)
    w = f"[{where}] " if where else ""
    if doc is None and review is None and result is None:
        raise g.Part2Stale(f"{w}Part 2 artifactがありません(文法の候補抽出・確定が未実行)。次の一手: {next_command}")
    g.check_doc_level(doc, level)
    if review is not None and review.get("status") in rv.GRAMMAR_WAIT_STATUSES:
        raise Part2NotConfirmed(f"{w}{PENDING_MARKER} Part 2(文法)のHuman確認が必要です: status={review.get('status')}。依頼書: {gr.paths(study_dir)['request']}。"
                                f"次の一手: {next_command}",
                                [gr.pending_summary(study_dir, review)])
    cc = _cc()
    if review is not None and _is_legacy_postselect(review, result):
        fz1 = _translate_cc(lambda: cc.load_frozen_grammar(study_dir))   # 確定レコードのある文法で凍結済みなら signature の代わりに frozen:<sha> で判定(M6)
        g.require_fresh_part2(result, paragraphs, label, next_command=next_command, where=where, candidates_doc=doc, grammar_review=review,
                              ref_ja_pool=(None if fz1 is not None else ref_ja_pool), frozen=fz1)
        if fz1 is not None:
            if ref_ja_pool is not None and result.get("status") == "SELECTED":   # 参考訳poolが凍結時の訳と異なる場合のみISSUE(再生成しない)
                msg = cc.pool_ref_ja_issue(study_dir, fz1, g.lookup_ref_ja(result["selection"]["sentence"], ref_ja_pool))
                if msg:
                    raise Part2NotConfirmed(f"[{where}] {msg}" if where else msg, [])
        else:
            _translate_cc(lambda: cc.freeze_part2_result(study_dir, result))   # 通常の検査を通った結果を凍結(確定レコードがある文法のみ)
        _translate_cc(lambda: cc.verify_part2(study_dir, result))   # G4: 確定した文法・解説全文との一致
        return result
    ex = gr.load_explanations(study_dir)
    if review is not None:
        _check_integrity(study_dir, review, result, ex)
    fz = _frozen_loaded(study_dir)
    if ex is not None and doc is not None:
        g.validate_explanations(_ex_excluding_frozen(ex, fz, review), doc, level=level, next_command=next_command, require_complete=False)
    g.require_fresh_part2(result, paragraphs, label, next_command=next_command, where=where, candidates_doc=doc, grammar_review=review, frozen=fz, explanations=ex)
    _check_translation(study_dir, result, ref_ja_pool, level=level, frozen=fz)
    _cc_verify_and_freeze(study_dir, result, frozen=fz, freeze=True)
    return result


_LOAD_NUANCE = object()   # verify_outputsのnuance既定=study_dirのnuance_result.jsonを読む(ページ合成と同じ入力を検証する)


def nuance_for_display(study_dir: str, *, level: Optional[str] = None) -> Optional[dict]:
    """ページ合成・検証が読むニュアンス解説の確定結果(`<study_dir>/nuance_result.json`)。ファイルが無い=None(LEGACY/未実施=ニュアンス解説なし)。
    読めない(壊れたJSON)・dictでない・levelキーが当該levelと食い違う=Part2Stale(採用済みの人間判断を黙って非表示にしない)。
    finalize(結果ファイルを作る工程。LLM 0)と、HR未確定時の待機(rc=4)はer134/runner接続(委任_02C)の責務。本関数は読むだけ。"""
    path = f"{study_dir}/{g.NUANCE_RESULT_FILENAME}"
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            res = json.load(f)
    except (OSError, ValueError) as e:
        raise g.Part2Stale(f"ニュアンス解説の確定結果({path})を読めません: {e}。次の一手: 結果ファイルを確認/finalizeを再実行") from e
    if not isinstance(res, dict):
        raise g.Part2Stale(f"ニュアンス解説の確定結果({path})がオブジェクトではありません")
    lk = res.get("level_key")
    if level is not None and lk is not None and lk != level:
        raise g.Part2Stale(f"ニュアンス解説の確定結果({path})のlevel_key={lk!r}が当該level({level})と一致しません(Std/Advの取り違え)")
    return res


def expected_block_counts(study_dir: str, *, level: Optional[str] = None) -> dict:
    """節に出るべきブロック数(runnerのpage_verifyが使う単一の期待値。文法=0または1 / ニュアンス=0または1)。"""
    result = g.load_json(RESULT_PATH(study_dir))
    nuance = nuance_for_display(study_dir, level=level)
    return {"grammar_blocks": g.expected_grammar_blocks(result), "nuance_blocks": g.expected_nuance_blocks(nuance)}


def verify_outputs(study_dir: str, paragraphs: list, label: str, *, level: str, next_command: str, where: str = "", ref_ja_pool: Optional[dict] = None,
                   md_path: Optional[str] = None, html_text: Optional[str] = None, nuance=_LOAD_NUANCE) -> dict:
    """R-3/O-6: 確定 <-> part2_result.json <-> study_text/*.md <-> **当該levelの節のHTML** の4者一致(kind="grammar")。
    html_textは共有builderの『当該levelの<section>』だけを渡す(ページ全体ではない)。節内の文法ブロックが期待数(SELECTED=1 / 0件=0)で、決定論の描画と一致すること。
    levelを取り違えたブロック(Std結果がAdv節にある等)は描画不一致でPart2Staleになる。
    0件の期待は『md不在』(M-6: 旧固定文面の0件mdは先に`.legacy_zero_p2.md`へ退避して検証する)。ニュアンス解説は節単位で検証する(M-7: 件数・描画一致・ページ非表示語)。
    戻り値=節の期待ブロック数 {"grammar_blocks","nuance_blocks"}(runnerのpage_verifyが数えた件数と突き合わせる)。"""
    doc, review, result = load_state(study_dir)
    g.check_doc_level(doc, level)
    if nuance is _LOAD_NUANCE:
        nuance = nuance_for_display(study_dir, level=level)
    md_text = None
    if md_path is not None:
        if result is not None and result.get("status") != "SELECTED" and os.path.normpath(md_path) == os.path.normpath(f"{study_dir}/{g.PART2_FILE_STEM}.md"):
            g.retire_part2_md(study_dir, only_legacy=True)   # M-6: 既存0件runの旧md(旧固定文面とバイト一致するものだけ)を決定論で退避してから検証(削除しない)
        if os.path.exists(md_path):
            with open(md_path, encoding="utf-8") as f:
                md_text = f.read()
        else:
            md_text = ""   # md不在=空(0件の期待。SELECTEDで不在なら描画不一致でPart2Stale)
    _verify_grammar_outputs(study_dir, doc, review, result, paragraphs, label, level=level, next_command=next_command, where=where,
                            ref_ja_pool=ref_ja_pool, md_text=md_text, html_text=html_text)
    if html_text is not None:
        g.verify_nuance_in_section(nuance, html_text, next_command=next_command, where=where)
    return {"grammar_blocks": g.expected_grammar_blocks(result), "nuance_blocks": g.expected_nuance_blocks(nuance)}


def _verify_grammar_outputs(study_dir, doc, review, result, paragraphs, label, *, level, next_command, where, ref_ja_pool, md_text, html_text) -> None:
    cc = _cc()
    legacy = review is not None and _is_legacy_postselect(review, result)
    ex = gr.load_explanations(study_dir)
    if review is not None and not legacy:
        _check_integrity(study_dir, review, result, ex)
    if legacy:
        fz = _translate_cc(lambda: cc.load_frozen_grammar(study_dir))
        g.verify_selection_matches_outputs(kind="grammar", paragraphs=paragraphs, label=label, candidates_doc=doc, grammar_review=review, result=result,
                                           md_text=md_text, html_text=html_text, next_command=next_command, where=where,
                                           ref_ja_pool=(None if fz is not None else ref_ja_pool), frozen=fz, section_scoped=True)
        _translate_cc(lambda: cc.verify_part2(study_dir, result))   # G4
        return
    fzl = _frozen_loaded(study_dir)
    g.verify_selection_matches_outputs(kind="grammar", paragraphs=paragraphs, label=label, candidates_doc=doc, grammar_review=review, result=result,
                                       md_text=md_text, html_text=html_text, next_command=next_command, where=where, frozen=fzl, explanations=ex, section_scoped=True)
    _cc_verify_and_freeze(study_dir, result, frozen=fzl, freeze=False)   # G4


# ============================================================
# フォーム / KCP from-form 向けデータ(API 0の純関数。fail-closed)
# ============================================================
def form_grammar_bundle(study_dir: str, *, level: str) -> dict:
    """フォームexporter用の文法データ。事前生成が不完全・part2_failed.jsonあり・explanations不整合なら**データを出さずエラー**(Part2Stale)。
    items: 候補rank順(AI推奨=rank1)。契約=SCHEMA_CONTRACT_01 §5。"""
    doc = gr.load_candidates(study_dir)
    if doc is None:
        raise g.Part2Stale("文法の候補docがありません(候補抽出stageが未実行)。フォームの文法データを作れません")
    g.check_doc_level(doc, level)
    cands = doc["candidates"][:g.PREGEN_MAX]
    if not cands:
        return {"level": level, "grammar_status": "no_candidates_found", "n_not_generated": 0, "items": []}
    try:
        ex = gr.require_explanations(study_dir, doc, level=level)
    except rv.KpReviewError as e:
        raise g.Part2Stale(str(e)) from e
    by_ex = {it["candidate_id"]: it for it in ex["items"]}
    items = [{"id": c["candidate_id"], "candidate_id": c["candidate_id"], "level": doc["level"], "title": c["construct_ja"],
              "explanation_full": by_ex[c["candidate_id"]]["explanation_md"], "explanation_status": "provided",
              "explanation_sha256": by_ex[c["candidate_id"]]["explanation_sha256"], "example": c["sentence"], "rank": c["rank"],
              "ai_recommended": c["rank"] == 1, "para": c["para"], "feature_class": c["feature_class"]} for c in cands]
    return {"level": level, "grammar_status": "candidates_available", "n_not_generated": max(0, len(doc["candidates"]) - len(cands)), "items": items}


def form_nuance_bundle(study_dir: str, *, level: str, kp_cands: dict) -> Optional[dict]:
    """フォームexporter用のニュアンス解説データ(API 0・read-only)。仕様マーク(nuance_spec.json)なし=None(既存記事・LEGACY: フォームデータにnuance関連キーを出さない=従来とバイト同一)。
    マークあり: nuance_candidate.json(N1がHR提示前に書く)から{"nuance_spec","nuance"|"nuance_note_ja"}を返す。
    **データを出さずエラー(Part2Stale)**: 候補docが無い/level不一致/(候補ありで)提示poolまたはKP候補doc(candidates_sha256。HR提示時の鮮度のみ)が現在と不一致/重複判定がpassでない。
    FAILED_TECHNICAL(技術失敗)は本物の0件と区別して表示する(R-5)。revoke後の再確定時は旧採否を previous_decision に載せる(R-11。フォームの既定表示のみ。明示送信は必須)。"""
    g.level_name(level)
    cc = _cc()
    if not os.path.exists(f"{study_dir}/{cc.FILE_NUANCE_SPEC}"):
        return None
    doc = g.load_json(f"{study_dir}/{cc.FILE_NUANCE_CANDIDATE}")
    if doc is None:
        raise g.Part2Stale("ニュアンス解説の仕様マークはありますが候補doc(nuance_candidate.json)がありません(N1未実行)。フォームのニュアンスデータを作れません")
    if doc.get("level_key") not in (None, level):
        raise g.Part2Stale(f"nuance_candidate.json のlevel_key={doc.get('level_key')!r} が --level {level} と一致しません")
    status = doc.get("status")
    spec = {"version": "nuance_v1", "max_select": 1, "allow_zero": True, "presented": False, "candidate_status": status}
    if status != "CANDIDATE":
        if status == "FAILED_TECHNICAL":
            kind = (doc.get("failed_technical") or {}).get("kind") or "unknown"
            note = (f"ニュアンス解説の候補なし（技術失敗: {kind}）。本物の0件ではありません。制作コマンドを同じまま再実行するとHR送信前に1回だけ自動で再試行されます"
                    f"（それでも失敗する場合は --regenerate-stage nuance_cand_{level}）。このまま送信するとニュアンス解説なしで確定します")
        else:
            note = "ニュアンス解説の候補はありません"
        return {"nuance_spec": spec, "nuance_note_ja": note}
    cand = doc.get("candidate")
    need = ("expression", "focus", "explanation_ja", "quote_en", "quote_ja", "candidate_sha256")
    if not isinstance(cand, dict) or any(not str(cand.get(k) or "").strip() for k in need):
        raise g.Part2Stale("nuance_candidate.json の候補本文が不完全です(必須項目の欠落)。フォームに出しません")
    basis = doc.get("kp_word_basis") or {}
    if basis.get("candidates_sha256") != kp_cands.get("candidates_sha256"):
        raise g.Part2Stale("ニュアンス候補が、現在のKP/Word候補docとは別の候補集合に対して作られています(candidates_sha256不一致。HR提示時の鮮度確認)。ニュアンス候補を作り直してください")
    if basis.get("pool_identity_sha") != cc.nuance_pool_identity_sha(kp_cands):
        raise g.Part2Stale("ニュアンス候補の比較pool(pool_identity_sha)が現在のKP/Word提示poolと一致しません。ニュアンス候補を作り直してください")
    gts = cc._nuance_text_sha_of_grammar(study_dir)
    if gts is not None and doc.get("text_sha256") not in (None, gts):
        raise g.Part2Stale("ニュアンス候補の本文sha(text_sha256)が現在の本文と一致しません。ニュアンス候補を作り直してください")
    oc = cand.get("overlap_check") or {}
    if oc.get("verdict") != "pass":
        raise g.Part2Stale(f"ニュアンス候補の重複判定がpassではありません(verdict={oc.get('verdict')!r})。HRに出せません")
    nuance = {"id": cc.nuance_id_of(cand), "candidate_sha256": cand["candidate_sha256"], "expression": cand["expression"], "focus": cand["focus"],
              "explanation_ja": cand["explanation_ja"], "quote_en": cand["quote_en"], "quote_ja": cand["quote_ja"],
              "pool_conflicts": list(cand.get("pool_conflicts") or []), "shared_terms": list(cand.get("shared_terms") or []),
              "grammar_conflicts": list(cand.get("grammar_conflicts") or []), "overlap_summary_ja": oc.get("reason") or ""}
    prev = cc.previous_nuance_decision(study_dir)
    if prev and prev.get("candidate_sha256") == cand["candidate_sha256"]:
        nuance["previous_decision"] = {"adopted": "adopt", "rejected": "reject"}[prev["decision"]]
    spec["presented"] = True
    return {"nuance_spec": spec, "nuance": nuance}


def form_grammar_items(study_dir: str, *, level: str) -> list:
    return form_grammar_bundle(study_dir, level=level)["items"]


# ============================================================
# Part 1(T1訳)からの参考訳pool・ページ描画(R-1/R-2: 描画はcompose_study_htmlの1関数だけ)
# ============================================================
def part1_ref_ja_pool(vocab_items: list, ja_doc: Optional[dict]) -> dict:
    """{本文引用英文: Part 1のT1訳}。Part 1訳と文法解説の訳の食い違い検査(ISSUE)に使う。ja_doc無し=空pool。"""
    if not ja_doc:
        return {}
    import er003_kp_source_sentence_ja_01 as ja
    by_rank = ja.translations_by_rank(ja_doc)
    pool = {}
    for it in ja.sorted_items(vocab_items):
        t = by_rank.get(it["rank"])
        if t:
            pool[ja.strict_sentence(it)] = t
    return pool


def compose_page_html(part1_html: str, result: dict, *, nuance) -> str:
    """ページに載せるstudy HTML(Part 1 -> Part 2文法 -> ニュアンス解説。該当しないブロックは出さない)。X player・X公開builder・Y/Z build_pagesの全てがこの関数だけを通る(R-2)。
    **nuanceは既定値なしの必須keyword**(R-6: 渡し漏れによる黙った欠落を構造で防ぐ)。ニュアンス解説なし(LEGACY/未実施)は明示的に`nuance=None`、通常は
    `nuance_for_display(study_dir, level=…)`の戻りを渡す。"""
    return g.compose_study_html(part1_html, result, nuance)


def _part1_enabled(audio_dir: str, level: str) -> bool:
    """Part 1(単語解説)を載せるか(D-F1是正)。Advanced(b1b)=常に / Standard(a2)=確定レコードにdisplay_spec(新表示仕様=Std Part 1=①+②)がある記事だけ
    (er128.display_spec_of=flag非経由・書込なし。display_spec無しのa2=従来どおりPart 1なし=遡及なし)。X runnerのpart1_enabledと同一規則。"""
    return level == "b1b" or bool(_cc().display_spec_of(audio_dir, level))


def public_study_html(audio_dir: str, article_text: str, *, level: str, next_command: str = "--stage study_text") -> str:
    """X公開ページ/試聴ページ生成scriptが呼ぶ共通関数(R-2)。入力=Production runnerのaudio出力dir(`<audio_dir>/<level>/...`)と確定済みの本文(article.md全文)。
    **levelは必須**(両levelのブロックが揃うことは呼出側が両levelで呼んで検査する)。b1b: Part 1(vocab_confirmed.json)+Part 2 / a2: display_spec付きはPart 1(①+②)+Part 2、無しはPart 2のみ(遡及なし)。
    未確定=Part2NotConfirmed(待機)、無い/古い=Part2Stale / KpGeneralExplanationError(ページを作らない)。"""
    g.level_name(level)
    b = f"{audio_dir}/{level}"
    paragraphs, label = g.paragraphs_from_article_md(article_text), label_for(article_text)
    if _part1_enabled(audio_dir, level):
        import er003_kp_general_explanation_01 as p1
        items = _cc().load_verified_items(f"{b}/key_phrases", level=level, which="part1")   # 確定内容保護の単一アクセサ(G1を通し、Part 1入力が確定レコードと一致することを確認してから返す)
        ja_path = f"{b}/key_phrases/kp_source_sentence_ja.json"
        ja_doc = g.load_json(ja_path) if os.path.exists(ja_path) else None
        pool = part1_ref_ja_pool(items, ja_doc)
    else:
        items, pool = None, {}
    # Part 2の確定(待機/STOPの理由が先に分かる)→Part 1の描画の順。どちらかが欠けたらページを作らない
    result = require_final(f"{b}/study_text", paragraphs, label, level=level, next_command=next_command, where=f"x_page_{level}", ref_ja_pool=pool)
    if items is not None:
        part1_html = p1.study_html_for_audio_dir(audio_dir, items=items, level=level)
    else:
        part1_html = ""
    return compose_page_html(part1_html, result, nuance=nuance_for_display(f"{b}/study_text", level=level))


# ============================================================
# 統合依頼書(KP+文法を1つ・rc=4を1回)は er119_kp_wiring_01.write_unified_request / pending_banner(er119側で満たす。DESIGN_02 §3 ⑤)
# ============================================================
def pending_banner(pending: list, *, restart_command: str, run_dir: Optional[str] = None) -> str:
    import er119_kp_wiring_01 as kpw
    return kpw.pending_banner(pending, restart_command=restart_command, run_dir=run_dir)
