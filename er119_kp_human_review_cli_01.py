# -*- coding: utf-8 -*-
"""KP Human Review CLI(決定論・API 0)。Humanが候補からKP/単語解説を選ぶ・NGにする・選び直す・不在を明示宣言する。

  py er119_kp_human_review_cli_01.py status --run <run_dir>
  py er119_kp_human_review_cli_01.py show --run <run_dir> --level b1b
  py er119_kp_human_review_cli_01.py select --run <run_dir> --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] [--accept-qa-fail 7] --by <名前>
  py er119_kp_human_review_cli_01.py select --run <run_dir> --level a2 --accept-ai --candidates-sha <表示されたsha> --by <名前>
  py er119_kp_human_review_cli_01.py select --run <run_dir> --level b1b --from-json sel.json
  py er119_kp_human_review_cli_01.py reselect --run <run_dir> --level b1b --ng 4:理由 --by <名前>
  py er119_kp_human_review_cli_01.py ng|unng|resolve-gloss|mark-published ...
  py er119_kp_human_review_cli_01.py declare-absent --runs <dir>[,<dir>] --reason ... --by ... [--user-ref ...]

Part 2(文法)の操作(kind="grammar"。API 0。再抽出は次回起動でStep A'' 1 call):
  py er119_kp_human_review_cli_01.py grammar-show --run <run_dir>
  py er119_kp_human_review_cli_01.py grammar-select --run <run_dir> --choice top1 --accept-ai --candidates-sha <表示sha> --by <名前>
  py er119_kp_human_review_cli_01.py grammar-select --run <run_dir> --choice top2|reselect|omit|reextract --reason <理由> --candidates-sha <表示sha> --by <名前>
  py er119_kp_human_review_cli_01.py grammar-ng --run <run_dir> --rank N --reason ... --by ...
  py er119_kp_human_review_cli_01.py grammar-unng --run <run_dir> --sentence "<英文>"|--candidate-id <id> --reason ... --by ...
  (status は KP と文法の両方を表示。不在宣言 declare-absent はKPと文法の両方に効く[このrun・この候補round限り])

番号=kp_human_review_request.mdの表の「番号」(ai_rank)。直接 kp_human_review.json を手編集すると署名不一致で全消費者がSTOPする。
"""
from __future__ import annotations

import argparse
import json
import sys

import er119_grammar_review_01 as gr
import er119_kp_human_review_01 as rv
import er120_part2_grammar_production_01 as g


def _parse_ng(items: list) -> dict:
    out = {}
    for s in items or []:
        if ":" not in s:
            raise rv.KpReviewError(f"--ngは『番号:理由』の形式です(指定: {s!r})")
        n, reason = s.split(":", 1)
        out[int(n.strip())] = reason.strip()
    return out


def _ints(s: str) -> list:
    return [int(x) for x in (s or "").replace(" ", "").split(",") if x != ""]


def _kp_dir_for(run: str, level: str) -> str:
    for d in rv.discover_kp_dirs(run):
        r = rv.load_review(d)
        if r and r.get("level") == level:
            return d
    raise rv.KpReviewError(f"{run}に level={level} のKP review/候補が見つかりません(制作を実行して候補を生成してください)")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, level=True):
        p.add_argument("--run", required=True, help="run dir(X: er019_output/.../<slug>__<run>、Z: er026_output/.../<slug>/<run>)")
        if level:
            p.add_argument("--level", required=True, choices=("a2", "b1b"))
    p = sub.add_parser("status")
    common(p, level=False)
    p = sub.add_parser("show")
    common(p)
    p = sub.add_parser("select")
    common(p)
    p.add_argument("--kp", default="")
    p.add_argument("--vocab", default=None)
    p.add_argument("--ng", action="append", default=[])
    p.add_argument("--accept-qa-fail", default="")
    p.add_argument("--accept-ai", action="store_true")
    p.add_argument("--candidates-sha", default=None, help="--accept-ai時: 表示した候補のcandidates_sha256(未表示候補への了承を拒否する)")
    p.add_argument("--from-json", default=None)
    p.add_argument("--by", default=None)
    p = sub.add_parser("reselect")
    common(p)
    p.add_argument("--ng", action="append", default=[])
    p.add_argument("--note", default="")
    p.add_argument("--by", required=True)
    p = sub.add_parser("ng")
    common(p)
    p.add_argument("--ng", action="append", required=True)
    p.add_argument("--by", required=True)
    p = sub.add_parser("unng")
    common(p)
    p.add_argument("--rank", type=int, default=None)
    p.add_argument("--phrase", default=None)
    p.add_argument("--reason", required=True)
    p.add_argument("--by", required=True)
    p = sub.add_parser("mark-published")
    common(p)
    p.add_argument("--by", required=True)
    p = sub.add_parser("resolve-gloss")
    common(p)
    p.add_argument("--rank", type=int, required=True)
    p.add_argument("--gloss", required=True)
    p.add_argument("--by", required=True)
    p = sub.add_parser("grammar-show")
    common(p, level=False)
    p = sub.add_parser("grammar-select")
    common(p, level=False)
    p.add_argument("--choice", required=True, choices=("top1", "top2", "omit", "reselect", "reextract"))
    p.add_argument("--candidates-sha", required=True, help="表示した候補のcandidates_sha256(古い候補への操作を拒否する)")
    p.add_argument("--reason", default="", help="top2/reselect/omit/reextractは必須")
    p.add_argument("--accept-ai", action="store_true", help="AI推奨(TOP1)の了承。--choice top1 のときだけ")
    p.add_argument("--by", required=True)
    p = sub.add_parser("grammar-ng")
    common(p, level=False)
    p.add_argument("--rank", type=int, required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--by", required=True)
    p = sub.add_parser("grammar-unng")
    common(p, level=False)
    p.add_argument("--sentence", default=None)
    p.add_argument("--candidate-id", default=None)
    p.add_argument("--reason", required=True)
    p.add_argument("--by", required=True)
    p = sub.add_parser("declare-absent")
    p.add_argument("--runs", required=True, help="カンマ区切りのrun dir(個別run宣言。範囲・期限付きの宣言は受け付けない)")
    p.add_argument("--rounds", default="1", help="宣言が効く候補round(既定=1。再選定後のroundは別途明示宣言)")
    p.add_argument("--candidates-sha", default=None)
    p.add_argument("--reason", required=True)
    p.add_argument("--by", required=True)
    p.add_argument("--user-ref", default="", help="ユーザー発言の参照。by がAI(Fable/Claude等)の場合は必須")
    return ap


def _print(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def run(argv=None) -> int:
    ap = build_parser()
    a = ap.parse_args(argv)
    try:
        if a.cmd == "status":
            dirs = rv.discover_kp_dirs(a.run)
            rows = [rv.status_of(d) for d in dirs]
            grows = [gr.status_of(d) for d in gr.discover_dirs(a.run)]
            _print({"run": a.run, "levels": rows, "grammar": grows,
                    "pending": [r["level"] for r in rows if r.get("status") == rv.ST_PENDING],
                    "grammar_pending": [r["study_dir"] for r in grows if r.get("status") in rv.GRAMMAR_WAIT_STATUSES]})
            return 0
        if a.cmd.startswith("grammar-"):
            gdirs = gr.discover_dirs(a.run)
            if not gdirs:
                raise rv.KpReviewError(f"{a.run}に文法(Part 2)のreview/候補が見つかりません(制作を実行して候補を生成してください)")
            gd = gdirs[0]
            if a.cmd == "grammar-show":
                doc, review = gr.load_candidates(gd), gr.load_review(gd)
                print(gr.render_request_md(doc, review, run_hint=a.run))
                return 0
            if a.cmd == "grammar-select":
                review = gr.op_decide(gd, choice=a.choice, candidates_sha256=a.candidates_sha, reason=a.reason, by=a.by, accept_ai=a.accept_ai)
                _print({"status": review["status"], "selection": review.get("selection"), "revision": review["revision"],
                        "next": ("再抽出が要求されました。制作コマンドを同じまま再実行すると候補を再抽出します(Step A'' 1 call)" if review["status"] == rv.ST_REEXTRACT_REQUESTED
                                 else "制作コマンドを同じまま再実行してください(finalize→後続が進みます)")})
                return 0
            if a.cmd == "grammar-ng":
                review = gr.op_ng(gd, rank=a.rank, reason=a.reason, by=a.by)
                _print({"status": review["status"], "next": "候補listが更新されました。依頼書(grammar-show)を再確認してください"})
                return 0
            if a.cmd == "grammar-unng":
                _print({"removed": gr.op_unng(gd, sentence=a.sentence, candidate_id=a.candidate_id, reason=a.reason, by=a.by),
                        "note": "現在の候補listには戻りません(次の新規抽出/reextractから効きます)"})
                return 0
        if a.cmd == "declare-absent":
            runs = [x.strip() for x in (a.runs or "").split(",") if x.strip()]
            ids = rv.add_declaration(run_dirs=runs, by=a.by, reason=a.reason, user_ref=a.user_ref,
                                     rounds=_ints(a.rounds), candidates_sha256=a.candidates_sha)
            _print({"declared": ids, "note": "宣言は、この後のHuman操作(select/reselect/ng/unng/resolve-gloss)で失効します。再選定後のroundには効きません。"})
            return 0
        kp_dir = _kp_dir_for(a.run, a.level)
        if a.cmd == "show":
            cands, review = rv.load_candidates(kp_dir), rv.load_review(kp_dir)
            ak = review.get("article_key") or {}
            print(rv.render_request_md(cands, review, run_hint=a.run,
                                       ng_entries=rv.ng_entries_of(review, ak.get("family"), ak.get("slug"), a.level)))
            return 0
        if a.cmd == "select":
            kp_ranks, vocab_ranks, ng, qf, by = _ints(a.kp), (_ints(a.vocab) if a.vocab is not None else None), _parse_ng(a.ng), _ints(a.accept_qa_fail), a.by
            if a.from_json:
                with open(a.from_json, encoding="utf-8") as f:
                    j = json.load(f)
                kp_ranks, vocab_ranks = list(j.get("kp") or []), (list(j["vocab"]) if "vocab" in j else None)
                ng = {int(k): v for k, v in (j.get("ng") or {}).items()}
                qf = list(j.get("accept_qa_fail") or [])
                by = by or j.get("by")
            if not by:
                raise rv.KpReviewError("--by(操作者)が必須です")
            review = rv.op_select(kp_dir, kp_ranks=kp_ranks, vocab_ranks=vocab_ranks, ng=ng, accept_qa_fail=qf, by=by,
                                  accept_ai=a.accept_ai, shown_candidates_sha256=a.candidates_sha)
            _print({"status": review["status"], "selection": review["selection"], "revision": review["revision"],
                    "next": "制作コマンドを同じまま再実行してください(finalize→後続が進みます)"})
            return 0
        if a.cmd == "reselect":
            review = rv.op_reselect(kp_dir, ng=_parse_ng(a.ng), note=a.note, by=a.by)
            _print({"status": review["status"], "reselect_count": review["reselect_count"],
                    "next": "制作コマンドを同じまま再実行すると候補が再生成されます(NG句は復活しません)。RESTART_STORM防止のため、前回起動から数分あけてください"})
            return 0
        if a.cmd == "ng":
            review = rv.op_ng(kp_dir, ng=_parse_ng(a.ng), by=a.by)
            _print({"status": review["status"], "ng": [e["candidate_id"] for e in review["ng"] if e.get("active", True)]})
            return 0
        if a.cmd == "unng":
            _print({"removed": rv.op_unng(kp_dir, rank=a.rank, phrase=a.phrase, reason=a.reason, by=a.by)})
            return 0
        if a.cmd == "mark-published":
            r = rv.op_mark_published(kp_dir, by=a.by)
            _print({"published_selection_signature": r["published_selection_signature"], "note": "公開版の署名を記録しました(以後の事後Reviewでも自動差替えはしません)"})
            return 0
        if a.cmd == "resolve-gloss":
            c = rv.op_resolve_gloss(kp_dir, rank=a.rank, gloss=a.gloss, by=a.by)
            _print({"resolved": c["candidate_id"], "japanese_gloss": c["japanese_gloss"]})
            return 0
    except (rv.KpReviewError, rv.KpReviewPending, ValueError, g.Part2Error) as e:
        print(f"[KP_REVIEW_CLI][REFUSED] {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(run())
