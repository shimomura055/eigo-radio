# -*- coding: utf-8 -*-
"""PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_03: Part 2(Grammar & Sentence Structure)のX/Z runner共通の接続層。決定論部分はAPI 0。

moduleの責務分担:
  er120_part2_grammar_production_01 : Part 2の中身(Prompt・候補・選定規則・Step B・fail-closed検査)。無改変
  er119_grammar_review_01           : 文法Human Review(kind="grammar")の状態・操作(er119共通核に接続)
  本module                          : runner(er019/er026)から呼ぶ薄い層。候補段階(抽出)/finalize段階(Step B)/使う側の検査/ページ描画/統合依頼書

段階(DESIGN_02 §4):
  candidate_stage : 本文確定直後・KP候補生成と同じ待機点の前に実行(Step A''。resumeはAPI 0)。未確定ならPENDINGを返す
  finalize_stage  : Part 1(T1訳)確定後・確定済みの文法reviewから Step B(再抽出なし)。待機系はPart2PendingReviewで出力を書く前に抜ける
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

CAND_STAGE = "part2_cand_b1b"
FINAL_STAGE = "part2_b1b"
RESULT_PATH = lambda study_dir: f"{study_dir}/{g.RESULT_FILENAME}"   # noqa: E731
PENDING_MARKER = rv.PENDING_MARKER


class Part2NotConfirmed(g.Part2Stale):
    """文法のHuman確認待ち/再選定中/再抽出待ち(失敗ではなく待機。rc=4)。Part2Staleを継承するので『前進不可』としてfail-closedにもなる。"""

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


# ============================================================
# 段階A: 候補抽出+待機/自動確定の評価
# ============================================================
def candidate_stage(study_dir: str, *, run_dir: str, family: str, slug: str, paragraphs: list, label: str, run_hint: Optional[str] = None,
                    extract_call_fn: Optional[Callable] = None, client=None, budget_guard: Optional[Callable] = None,
                    force_extract: bool = False) -> dict:
    return _translate_cc(lambda: gr.ensure_grammar_review(study_dir, run_dir=run_dir, family=family, slug=slug, paragraphs=paragraphs, label=label, run_hint=run_hint,
                                                          extract_call_fn=extract_call_fn, client=client, budget_guard=budget_guard, force_extract=force_extract))


def cand_input_sha(study_dir: str, paragraphs: list, label: str, prov_entry: Optional[dict] = None) -> str:
    """Z/Y `part2_cand_b1b` のinput_sha(来歴照合用)。通常は g.cand_stage_input_sha(本文sha+label+抽出signature[Prompt・model])。
    ユーザー確定済みの文法(KP-CONFIRMED-CONTENT-PROTECTION-01 M6)があり、候補docの本文shaが現本文と一致する場合に限り、Prompt/model/routingだけの変更で
    来歴が親sha不一致STOPにならないよう、記録済みの入力shaを据え置く(確定済みの文法は再抽出しない。--regenerate-stage part2_cand_b1b はrevoke必須で拒否されるため、
    据え置かないと解消できないSTOPになる)。本文が変わった場合・確定が無い場合は従来どおり。"""
    sha = g.cand_stage_input_sha(paragraphs, label)
    if prov_entry is not None and prov_entry.get("input_sha256") != sha:
        doc = gr.load_candidates(study_dir)
        if doc is not None and doc.get("text_sha256") == g.text_sha256(paragraphs) and _translate_cc(lambda: _cc().grammar_state(study_dir)) is not None:
            return prov_entry["input_sha256"]
    return sha


def cand_marker(study_dir: str, paragraphs: list, label: str) -> str:
    """Z `part2_cand_b1b` stageの凍結出力(来歴用marker。reselectで候補docが変わってもこのmarkerは変わらない)。"""
    return json.dumps({"stage": CAND_STAGE, "input_sha256": g.cand_stage_input_sha(paragraphs, label), "text_sha256": g.text_sha256(paragraphs),
                       "label": label, "extract_signature": g.extract_signature(paragraphs, label), "note": "候補docと確定は grammar_candidates.json / grammar_human_review.json"},
                      ensure_ascii=False, indent=2)


# ============================================================
# 段階B: finalize(Step B。再抽出なし)
# ============================================================
def _replay_inputs(review: dict):
    """確定recordから er120.finalize_part2 に渡す (review=決定dict|None, mode='wait'|宣言dict) を復元する。"""
    st = review["status"]
    if st == rv.ST_AUTO:
        return None, review["mode_declaration"]
    if st == rv.ST_NO_CANDIDATE:
        return None, "wait"
    d = review.get("decision")
    if not d:
        raise g.Part2Stale("Part 2の確定recordにdecisionがありません(手編集の疑い)")
    return dict(d), "wait"


def finalize_stage(study_dir: str, *, paragraphs: list, label: str, ref_ja_pool: Optional[dict] = None, explain_call_fn: Optional[Callable] = None,
                   client=None, budget_guard: Optional[Callable] = None, write: bool = True) -> dict:
    """確定済みの文法reviewから part2_result.json(+md)を作る(write=Falseなら保存せずresultを返す。Zはensure_stageが保存する)。Step A''は呼ばない(_no_extract)。Step B 0/1 call(resumeで一致すれば0)。
    待機系statusなら Part2PendingReview(出力ファイルを書く前に抜ける)。返り値: {"result","status","reused","review"}"""
    pth = gr.paths(study_dir)
    doc, review = gr.load_candidates(study_dir), gr.load_review(study_dir)
    if doc is None or review is None:
        raise g.Part2Stale("文法の候補/reviewがありません(候補抽出stageが未実行)")
    if review["status"] not in rv.FORWARD_STATUSES_BY_KIND[rv.KIND_GRAMMAR]:
        raise g.Part2PendingReview(review["status"], g.review_request(doc), doc)
    if review["candidates_sha256"] != doc["candidates_sha256"] or review["text_sha256"] != doc["text_sha256"]:
        raise g.Part2Stale("文法の確定が現在の候補docに対するものではありません")
    dec, mode = _replay_inputs(review)
    cached_result = g.load_json(RESULT_PATH(study_dir))
    # 確定内容保護(M6): ユーザー確定済みの文法(confirmed_grammar.json)があれば、凍結した解説を使い再抽出・再解説(LLM)をしない。
    # 凍結がまだ無く、フォームで解説全文を見せていた(explanation_status=provided)場合は、その全文を凍結値にする(Step Bを呼ばない)。
    fz = None
    cc = _cc()
    sel0 = g.select_from_candidates(doc, dec, mode)
    if sel0.get("status") == "SELECTED":
        fz = _translate_cc(lambda: cc.load_frozen_grammar(study_dir) or cc.freeze_from_sidecar(study_dir, sel0["candidate"]))
        if fz is not None:
            msg = cc.pool_ref_ja_issue(study_dir, fz, g.lookup_ref_ja(sel0["candidate"]["sentence"], ref_ja_pool))
            if msg:
                raise Part2NotConfirmed(msg, [])
    out = g.finalize_part2(paragraphs, label, candidates_doc=doc, review=dec, mode=mode, cached_result=cached_result, ref_ja_pool=ref_ja_pool,
                           explain_call_fn=explain_call_fn, client=client, budget_guard=budget_guard, ng=(), prior_history=None, frozen=fz)
    rec = out["review_record"]
    if rec["selection_signature"] != review["selection_signature"]:   # 突合: 保存した確定recordとer120が再導出した署名は一致するはず
        raise g.Part2Stale("文法の確定recordの署名が、er120の再導出と一致しません(手編集またはcodeの不整合)。fail-closed")
    res = out["result"]
    if fz is None:   # 通常の検査を通った今回のStep B結果を凍結(確定レコードのある文法のみ。出所=stepB_generated_frozen)
        _translate_cc(lambda: cc.freeze_part2_result(study_dir, res))
    _translate_cc(lambda: cc.verify_part2(study_dir, res))   # G4
    reused = bool(res.get("reused_from_previous_run"))
    if write:
        if not reused or not os.path.exists(RESULT_PATH(study_dir)):
            g.write_artifacts(study_dir, None, res)
        elif not os.path.exists(f"{study_dir}/{g.PART2_FILE_STEM}.md"):
            g.write_artifacts(study_dir, None, res)
    return {"result": res, "status": out["status"], "reused": reused, "review": review}


def write_md(study_dir: str, result: dict) -> str:
    """study_text/ のPart 2 markdown(決定論の描画)。Zはresult JSONをensure_stageが書くため、mdだけここで書く。"""
    os.makedirs(study_dir, exist_ok=True)
    path = f"{study_dir}/{g.PART2_FILE_STEM}.md"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(g.render_markdown(result))
    return path


# ============================================================
# 使う側の入口検査
# ============================================================
def load_state(study_dir: str):
    return gr.load_candidates(study_dir), gr.load_review(study_dir), g.load_json(RESULT_PATH(study_dir))


def artifacts_exist(study_dir: str) -> bool:
    return any(os.path.exists(p) for p in (gr.paths(study_dir)["candidates"], gr.paths(study_dir)["review"], RESULT_PATH(study_dir)))


def require_final(study_dir: str, paragraphs: list, label: str, *, next_command: str, where: str = "", ref_ja_pool: Optional[dict] = None) -> dict:
    """TTS/assembly/pages/player/公開ページ builder の入口。未確定=Part2NotConfirmed(待機)、無い/古い/不整合=Part2Stale(STOP)。resultを返す。"""
    doc, review, result = load_state(study_dir)
    w = f"[{where}] " if where else ""
    if doc is None and review is None and result is None:
        raise g.Part2Stale(f"{w}Part 2 artifactがありません(文法の候補抽出・確定が未実行)。次の一手: {next_command}")
    if review is not None and review.get("status") in rv.GRAMMAR_WAIT_STATUSES:
        raise Part2NotConfirmed(f"{w}{PENDING_MARKER} Part 2(文法)のHuman確認が必要です: status={review.get('status')}。依頼書: {gr.paths(study_dir)['request']}。"
                                f"次の一手: {next_command}",
                                [gr.pending_summary(study_dir, review)])
    cc = _cc()
    fz = _translate_cc(lambda: cc.load_frozen_grammar(study_dir))   # 確定レコードのある文法で凍結済みなら signature の代わりに frozen:<sha> で判定(M6)
    g.require_fresh_part2(result, paragraphs, label, next_command=next_command, where=where, candidates_doc=doc, grammar_review=review,
                          ref_ja_pool=(None if fz is not None else ref_ja_pool), frozen=fz)
    if fz is not None:
        if ref_ja_pool is not None and result.get("status") == "SELECTED":   # 参考訳poolが凍結時の訳と異なる場合のみISSUE(再生成しない)
            msg = cc.pool_ref_ja_issue(study_dir, fz, g.lookup_ref_ja(result["selection"]["sentence"], ref_ja_pool))
            if msg:
                raise Part2NotConfirmed(f"[{where}] {msg}" if where else msg, [])
    else:
        _translate_cc(lambda: cc.freeze_part2_result(study_dir, result))   # 通常の検査を通った結果を凍結(確定レコードがある文法のみ)
    _translate_cc(lambda: cc.verify_part2(study_dir, result))   # G4: 確定した文法・解説全文との一致
    return result


def verify_outputs(study_dir: str, paragraphs: list, label: str, *, next_command: str, where: str = "", ref_ja_pool: Optional[dict] = None,
                   md_path: Optional[str] = None, html_text: Optional[str] = None) -> None:
    """R-3: 確定 <-> part2_result.json <-> study_text/*.md <-> 公開HTML の一致(kind="grammar")。不一致=Part2Stale。"""
    doc, review, result = load_state(study_dir)
    md_text = None
    if md_path is not None:
        with open(md_path, encoding="utf-8") as f:
            md_text = f.read()
    cc = _cc()
    fz = _translate_cc(lambda: cc.load_frozen_grammar(study_dir))
    g.verify_selection_matches_outputs(kind="grammar", paragraphs=paragraphs, label=label, candidates_doc=doc, grammar_review=review, result=result,
                                       md_text=md_text, html_text=html_text, next_command=next_command, where=where,
                                       ref_ja_pool=(None if fz is not None else ref_ja_pool), frozen=fz)
    _translate_cc(lambda: cc.verify_part2(study_dir, result))   # G4


# ============================================================
# Part 1(T1訳)からの参考訳pool・ページ描画(R-1/R-2: 描画はcompose_study_htmlの1関数だけ)
# ============================================================
def part1_ref_ja_pool(vocab_items: list, ja_doc: Optional[dict]) -> dict:
    """{本文引用英文: Part 1のT1訳}。Step Bの参考訳(ref_ja)として、英文が一致(_qn正規化の完全一致)したときだけ渡される。ja_doc無し=空pool。"""
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


def compose_page_html(part1_html: str, result: dict) -> str:
    """ページに載せるstudy HTML(Part 1ブロック直後にPart 2)。X player・X公開builder・Z build_pagesの全てがこの関数だけを通る(R-2)。"""
    return g.compose_study_html(part1_html, result)


def public_study_html(audio_dir: str, article_text: str, *, next_command: str = "--stage study_text") -> str:
    """X公開ページ/試聴ページ生成scriptが呼ぶ共通関数(R-2。Part 1+Part 2を1か所で描画)。入力=Production runnerのaudio出力dir(`<audio_dir>/b1b/...`)と
    確定済みの本文(article.md全文)。Part 1の入力は part1_items(vocab_confirmed.json。KP3件ではなく最大5件)。Part 2は確定・最新性・結果の一致を確認してから描画する。
    未確定=Part2NotConfirmed(待機)、無い/古い=Part2Stale / KpGeneralExplanationError(ページを作らない)。"""
    import er003_kp_general_explanation_01 as p1
    b = f"{audio_dir}/b1b"
    items = _cc().load_verified_items(f"{b}/key_phrases", level="b1b", which="part1")   # 確定内容保護の単一アクセサ(G1を通し、Part 1入力が確定レコードと一致することを確認してから返す)
    ja_path = f"{b}/key_phrases/kp_source_sentence_ja.json"
    ja_doc = g.load_json(ja_path) if os.path.exists(ja_path) else None
    paragraphs, label = g.paragraphs_from_article_md(article_text), label_for(article_text)
    # Part 2の確定(待機/STOPの理由が先に分かる)→Part 1の描画の順。どちらかが欠けたらページを作らない
    result = require_final(f"{b}/study_text", paragraphs, label, next_command=next_command, where="x_page",
                           ref_ja_pool=part1_ref_ja_pool(items, ja_doc))
    part1_html = p1.study_html_for_audio_dir(audio_dir, items=items)
    return compose_page_html(part1_html, result)


# ============================================================
# 統合依頼書(KP+文法を1つ・rc=4を1回)は er119_kp_wiring_01.write_unified_request / pending_banner(er119側で満たす。DESIGN_02 §3 ⑤)
# ============================================================
def pending_banner(pending: list, *, restart_command: str, run_dir: Optional[str] = None) -> str:
    import er119_kp_wiring_01 as kpw
    return kpw.pending_banner(pending, restart_command=restart_command, run_dir=run_dir)
