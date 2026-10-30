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

Part 2(文法)の操作(kind="grammar"。**--level必須**[b1b=Advanced / a2=Standard。pathや先頭dirから推定しない]。API 0。再抽出は次回起動でStep A'' 1 call):
  py er119_kp_human_review_cli_01.py grammar-show --run <run_dir> --level b1b
  py er119_kp_human_review_cli_01.py grammar-select --run <run_dir> --level b1b --choice pick --ids <id>(Top1/Top2のどちらか1件。2件同時選択は禁止) [--accept-ai(AI推奨Top1の了承)] [--reason <理由>] --candidates-sha <表示sha> --by <名前>
  py er119_kp_human_review_cli_01.py grammar-select --run <run_dir> --level b1b --choice top1 --accept-ai --candidates-sha <表示sha> --by <名前>
  py er119_kp_human_review_cli_01.py grammar-select --run <run_dir> --level b1b --choice top2|reselect|omit|reextract --reason <理由> --candidates-sha <表示sha> --by <名前>
  py er119_kp_human_review_cli_01.py grammar-ng --run <run_dir> --level b1b --rank N --reason ... --by ...
  py er119_kp_human_review_cli_01.py grammar-unng --run <run_dir> --level b1b --sentence "<英文>"|--candidate-id <id> --reason ... --by ...
  py er119_kp_human_review_cli_01.py grammar-accept-translation --run <run_dir> --level b1b --candidate-id <id>[,<id>] --user-ref <ユーザー発言のdelegation_logパス> --by <名前> [--reason ...]
      (Part 1の訳とStep Bの【日本語訳】の食い違いISSUEを、ユーザー了承として記録して解消する。--user-ref必須・記録が残る・再送は冪等)
  py er119_kp_human_review_cli_01.py grammar-pregen --run <run_dir> --level b1b [--ids <id>[,<id>]] [--managed-id <ID>]
      (解説の事前生成。**有料**[Step B 約0.3円/件、AI評価Top1/Top2の2候補分だけ]。未生成分だけ作り、signature一致は再利用[API 0]。旧 --all-candidates[全候補opt-in]は2026-10-27撤去)
  (status は KP と文法の両方を表示。不在宣言 declare-absent はKPと文法の両方に効く[このrun・この候補round限り])

番号=kp_human_review_request.mdの表の「番号」(ai_rank)。直接 kp_human_review.json を手編集すると署名不一致で全消費者がSTOPする。
"""
from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import os
import sys

import er119_grammar_review_01 as gr
import er119_kp_human_review_01 as rv
import er120_part2_grammar_production_01 as g
import er120_part2_wiring_01 as p2w


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
    p.add_argument("--accept-qa-fail", default="", help="旧候補doc(仕様①より前に旗付きで保存されたQA不合格候補)の救済専用。新docではQA不合格候補は提示されない")
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
    def gcommon(p):
        p.add_argument("--run", required=True, help="run dir")
        p.add_argument("--level", required=True, choices=("a2", "b1b"), help="b1b=Advanced / a2=Standard(必須。先頭dirやpathから推定しない)")
    p = sub.add_parser("grammar-show")
    gcommon(p)
    p = sub.add_parser("grammar-select")
    gcommon(p)
    p.add_argument("--choice", required=True, choices=("pick", "top1", "top2", "omit", "reselect", "reextract"),
                   help="pick=--idsで1件を選ぶ(2件同時選択は禁止。適切な候補が無ければomit=0件)。top1/top2=pickの単件ショートカット。提示はAI評価Top1/Top2のみ")
    p.add_argument("--ids", default=None, help="--choice pick のとき: 候補id(1件。Top1/Top2のどちらか。2件は拒否される)")
    p.add_argument("--candidates-sha", required=True, help="表示した候補のcandidates_sha256(古い候補への操作を拒否する)")
    p.add_argument("--reason", default="", help="AI推奨(Top1)以外のpick・top2/reselect/omit/reextractは必須")
    p.add_argument("--accept-ai", action="store_true", help="AI推奨(Top1)の了承。--choice top1 または pick(--idsがAI推奨1件)のときだけ")
    p.add_argument("--by", required=True)
    p = sub.add_parser("grammar-ng")
    gcommon(p)
    p.add_argument("--rank", type=int, required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--by", required=True)
    p = sub.add_parser("grammar-unng")
    gcommon(p)
    p.add_argument("--sentence", default=None)
    p.add_argument("--candidate-id", default=None)
    p.add_argument("--reason", required=True)
    p.add_argument("--by", required=True)
    p = sub.add_parser("grammar-accept-translation", help="Part 1訳とStep B訳の食い違いISSUEをユーザー了承として記録する")
    gcommon(p)
    p.add_argument("--candidate-id", required=True, help="ISSUEに記録された候補id(カンマ区切りで複数可)")
    p.add_argument("--user-ref", required=True, help="ユーザー了承の発言原文を保存したファイル(delegation_logのpath)。存在しないpathは拒否")
    p.add_argument("--by", required=True)
    p.add_argument("--reason", default="", help="省略時は『ユーザーが食い違いを了承(--user-refの発言)』を記録")
    p = sub.add_parser("grammar-pregen", help="文法解説の事前生成(有料: Step B約0.3円/件)。AI評価Top1/Top2の2候補分だけ。未生成分だけ作る(旧 --all-candidates は撤去)")
    gcommon(p)
    p.add_argument("--ids", default=None, help="対象の候補id(カンマ区切り)。核(pregen_stage)がids指定に未対応の版では拒否する(黙って全件生成しない)")
    p.add_argument("--managed-id", default="GRAMMAR-PREGEN-ALL-LEVELS-01", help="STOP適用範囲チェックの管理ID(有料操作の前に必ず確認する)")
    p = sub.add_parser("confirm", help="人間可読の選定結果(+照合コード)から復元して確定内容保護へ渡す(委任_07R。実体はer128_form_readable_restore_01)")
    p.add_argument("--from-readable", required=True, help="貼付テキストのfile。--dry-runで復元payloadと照合結果のみ出力")
    p.add_argument("--run", required=True)
    p.add_argument("--level", required=True, choices=("a2", "b1b"))
    p.add_argument("--by", default=None)
    p.add_argument("--user-ref", default="")
    p.add_argument("--grammar-pending", action="store_true")
    p.add_argument("--actor", default="user", choices=("user", "evidence"))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--data-dir", default=None)
    p = sub.add_parser("declare-absent")
    p.add_argument("--runs", required=True, help="カンマ区切りのrun dir(個別run宣言。範囲・期限付きの宣言は受け付けない)")
    p.add_argument("--rounds", default="1", help="宣言が効く候補round(既定=1。再選定後のroundは別途明示宣言)")
    p.add_argument("--candidates-sha", default=None)
    p.add_argument("--reason", required=True)
    p.add_argument("--by", required=True)
    p.add_argument("--user-ref", default="", help="ユーザー発言の参照。by がAI(Fable/Claude等)の場合は必須")
    return ap


def _split(v) -> list:
    return [x.strip() for x in (v or "").split(",") if x.strip()]


def _grammar_dir(run: str, level: str) -> str:
    """そのlevelの文法study dir。levelは必須(先頭dir/pathからの推定はしない)。無い/曖昧/level不一致はエラー(次の一手つき)。"""
    dirs = gr.discover_dirs(run, level)
    if not dirs:
        raise rv.KpReviewError(f"{run}に level={level} の文法(Part 2)のreview/候補が見つかりません。次の一手: 制作コマンドを実行して候補を生成してください"
                               f"(状況確認: py er119_kp_human_review_cli_01.py status --run {run})")
    if len(dirs) > 1:
        raise rv.KpReviewError(f"level={level} の文法study dirが複数あります({dirs})。どれか1つにしてください(先頭を黙って選びません)")
    return dirs[0]


def _stop_guard(run: str, managed_id: str) -> None:
    """有料操作の前のSTOP適用範囲チェック(tools/stop_scope_check_01.py の check)。適用があれば有料呼出をせず拒否する(rc=2。解除はFable/ユーザーのみ)。"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools", "stop_scope_check_01.py")
    spec = importlib.util.spec_from_file_location("stop_scope_check_01", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    res = mod.check([managed_id], run)
    if res["stop"]:
        raise rv.KpReviewError(f"STOP適用中のため有料のgrammar-pregenを実行しません: {res['applicable']}。STOPの解除はFable/ユーザーのみです")


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
        if a.cmd == "confirm":   # 薄い委譲(復元・照合・確定はer128_form_readable_restore_01 -> er128 cmd_from_form。ここでは検証しない)
            import er128_form_readable_restore_01 as fr
            if a.data_dir is None:
                a.data_dir = fr.DEFAULT_DATA_DIR
            return fr.run_confirm(a)
        if a.cmd.startswith("grammar-"):
            gd = _grammar_dir(a.run, a.level)
            if a.cmd == "grammar-show":
                doc, review = gr.load_candidates(gd), gr.load_review(gd)
                print(gr.render_request_md(doc, review, run_hint=a.run, study_dir=gd))
                return 0
            if a.cmd == "grammar-select":
                ids = _split(a.ids)
                if a.choice == "pick" and not ids:
                    raise rv.KpReviewError("--choice pick には --ids <id>[,<id>] が必要です(0件にするなら --choice omit --reason ...)")
                if a.choice != "pick" and ids:
                    raise rv.KpReviewError("--ids は --choice pick のときだけ指定できます(top1/top2は単件ショートカット)")
                review = gr.op_decide(gd, choice=a.choice, candidates_sha256=a.candidates_sha, reason=a.reason, by=a.by, accept_ai=a.accept_ai, ids=(ids or None))
                _print({"status": review["status"], "selection": review.get("selection"), "revision": review["revision"],
                        "next": ("再抽出が要求されました。制作コマンドを同じまま再実行すると候補を再抽出します(Step A'' 1 call)" if review["status"] == rv.ST_REEXTRACT_REQUESTED
                                 else "制作コマンドを同じまま再実行してください(finalize→後続が進みます)")})
                return 0
            if a.cmd == "grammar-ng":
                review = gr.op_ng(gd, rank=a.rank, reason=a.reason, by=a.by)
                _print({"status": review["status"], "next": f"候補listが更新されました。制作コマンドを再実行して解説を事前生成してから、grammar-show --run {a.run} --level {a.level} で再確認してください"})
                return 0
            if a.cmd == "grammar-unng":
                _print({"removed": gr.op_unng(gd, sentence=a.sentence, candidate_id=a.candidate_id, reason=a.reason, by=a.by),
                        "note": "現在の候補listには戻りません(次の新規抽出/reextractから効きます)"})
                return 0
            if a.cmd == "grammar-accept-translation":
                if not os.path.exists(a.user_ref):
                    raise rv.KpReviewError(f"--user-ref のファイルが存在しません: {a.user_ref}(ユーザー了承の発言原文を保存したdelegation_logのpathを指定してください)")
                ids = _split(a.candidate_id)
                added = gr.op_accept_translation_diff(gd, ids=ids, by=a.by, user_ref=a.user_ref,
                                                      reason=(a.reason or "ユーザーがPart 1訳とStep B訳の食い違いを了承(--user-refの発言)"))
                _print({"accepted_now": added, "already_recorded": [i for i in ids if i not in added],
                        "next": "制作コマンドを同じまま再実行してください(finalize→後続が進みます)。別の文法を選ぶ/省略する場合は grammar-select"})
                return 0
            if a.cmd == "grammar-pregen":
                ids = _split(a.ids)
                if ids and "ids" not in inspect.signature(p2w.pregen_stage).parameters:
                    raise rv.KpReviewError("この版の核(er120_part2_wiring_01.pregen_stage)は --ids に未対応です。--ids を外して実行してください"
                                           "(未生成分だけ作られ、signature一致の解説は再利用[API 0]されます)")
                _stop_guard(a.run, a.managed_id)
                kw = {"ids": ids} if ids else {}
                nxt = f"py er119_kp_human_review_cli_01.py grammar-pregen --run {a.run} --level {a.level}"
                res = p2w.pregen_stage(gd, level=a.level, next_command=nxt, run_hint=a.run, **kw)
                _print({"generated": res["generated"], "reused": res["reused"], "skipped_over_cap": res["skipped_over_cap"], "confirmed": res["confirmed"],
                        "next": (f"py er119_kp_human_review_cli_01.py grammar-show --run {a.run} --level {a.level} でTop1/Top2の解説を確認し、grammar-select で1件選んでください(適切なものが無ければomit)"
                                 if not res["confirmed"] else "制作コマンドを同じまま再実行してください")})
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
                    "redundancy_alarms": review.get("redundancy_alarms") or [], "redundancy_alarm_nonblocking": True,      # 仕様②: 重複はアラームのみ(止まらない)
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
    except (rv.KpReviewError, rv.KpReviewPending, ValueError, g.Part2Error, rv._cc().CliError) as e:
        print(f"[KP_REVIEW_CLI][REFUSED] {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(run())
