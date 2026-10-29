# -*- coding: utf-8 -*-
"""KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_02: KP Human Review 共通核(APPROVED_FOR_PRODUCTION、DESIGN_02参照)。

この核は決定論(API 0)。LLM呼出は注入関数(generate_fn / redundancy_fn)経由でのみ行う。
設計不変条件(DESIGN_02 / Opus M-1〜M-9):
  - <kp_dir>/keywords_canonicalized.json と vocab_confirmed.json と kp_selection_final.json を書けるのは finalize だけ(M-1)。
    候補生成は <kp_dir>/kp_candidates/round_<n>/work/ で行う(canonicalization等の既存関数が書く場所)。
  - 自動確定(UNREVIEWED_AUTO_ADOPTED)は「明示宣言」(read_mode_declaration、単一読取点)が有効なときだけ(M-6)。
    環境変数・設定dict・関数既定値・.envから auto にすることはできない(本moduleは環境変数を一切参照しない)。
  - 再選定は reselect(CLI)だけ。resume/regenerate/外側retry は確定済みreviewを再選定しない(M-3b)。
  - NG registry は run ではなく family+slug+level 単位の共有store(M-5)。
  - 共通核は kind 非依存("kp" / "grammar")。grammar(Part 2文法)は委任_03でProduction配線(er119_grammar_review_01 / er120_part2_wiring_01)。
  - 不在宣言は『個別run・候補sha・roundに紐づく明示宣言』のみ。期限付き/範囲付き(family・日付)宣言は不採用(ユーザー決定2026-10-25、R-7撤去)。
共有関数 sc.run_key_phrases は本moduleから呼ばない/変更しない(A/B/C・Y Trial不変)。
"""
from __future__ import annotations

import datetime
import hashlib
import html as _html
import json
import logging
import os
import re
import time
import unicodedata
from typing import Any, Callable, Optional

_log = logging.getLogger("kp_review")

SCHEMA_CANDIDATES = "kp_candidates_v1"
SCHEMA_REVIEW = "kp_human_review_v1"
SCHEMA_FINAL = "kp_selection_final_v1"

KIND_KP = "kp"
KIND_GRAMMAR = "grammar"   # Part 2文法(委任_03で配線。状態/操作はer119_grammar_review_01、確定recordの署名はer120.grammar_selection_signature)

ST_PENDING = "PENDING_REVIEW"
ST_REVIEWED = "REVIEWED"
ST_AUTO = "UNREVIEWED_AUTO_ADOPTED"
ST_RESELECT = "RESELECTION_REQUESTED"
ST_STALE = "STALE"
ST_NO_CANDIDATE = "NO_CANDIDATE_UNREVIEWED"   # grammar専用: 適格0件で待たずに確定(REVIEWEDではない。M-6)
ST_RESELECT_EXHAUSTED = "RESELECT_EXHAUSTED"   # grammar専用: 全候補をNGにして尽きた(Humanのomit/reextract待ち。自動ZEROにしない)
ST_REEXTRACT_REQUESTED = "REEXTRACT_REQUESTED"  # grammar専用: Humanが再抽出を選んだ(次回起動でStep A'' 1 call)
FORWARD_STATUSES = (ST_REVIEWED, ST_AUTO)
FORWARD_STATUSES_BY_KIND = {"kp": (ST_REVIEWED, ST_AUTO), "grammar": (ST_REVIEWED, ST_AUTO, ST_NO_CANDIDATE)}
GRAMMAR_WAIT_STATUSES = (ST_PENDING, ST_RESELECT, ST_RESELECT_EXHAUSTED, ST_REEXTRACT_REQUESTED, ST_STALE)   # 下流はfail-closed

EXIT_CODE_PENDING = 4          # KP_REVIEW_PENDING(失敗ではなく待機)。ZではRUN_LOCK(rc=4)と共有 -> stdoutの[KP_REVIEW_PENDING]で区別する
PENDING_MARKER = "[KP_REVIEW_PENDING]"

KP_CANDIDATE_MAX = 12            # KP-PHRASE7-WORD5-PRODUCTION-01(2026-10-27 APPROVED_FOR_PRODUCTION): フレーズ最大7(P7)+単語最大5(W5')。旧=8(3+5)
KP_FINAL_MAX = 3
VOCAB_COUNT_MAX = 5
RESELECT_MAX = 2               # 再選定上限(レベル/run)
AUTO_QA_ADVANCE_MAX = 3        # AUTOで確定集合のRedundancy QAがNGのとき、次候補へ繰り上げる上限
LOCK_STALE_SEC = 600

STORE_ROOT = os.path.join("er119_output", "kp_human_review_store_01")   # 共有store(NG registryのみ。宣言はrun dirのkp_review_mode.json)。testはここを差し替える

_AI_BY_PREFIXES = ("fable", "claude", "ai", "sonnet", "opus", "haiku", "agent", "assistant")

SLOT_RULES = {
    KIND_KP: {"kp": {"min": 1, "max": KP_FINAL_MAX}, "vocab": {"min": 0, "max": VOCAB_COUNT_MAX}},
    KIND_GRAMMAR: {"grammar": {"min": 0, "max": 1}},
}
FILE_PREFIX = {KIND_KP: "kp", KIND_GRAMMAR: "grammar"}


# ============================================================
# 例外
# ============================================================
class KpReviewError(RuntimeError):
    """review核の不整合・不正操作(fail-closed)。"""


class KpReviewPending(RuntimeError):
    """Human確認待ち(失敗ではなく待機。rc=4)。pending=[{level,kp_dir,request_md,...}]"""

    def __init__(self, message: str, pending: Optional[list] = None):
        super().__init__(message)
        self.pending = pending or []


class ReviewLockHeld(KpReviewError):
    pass


class ReviewConflict(KpReviewError):
    pass


class KpReviewInconsistent(KpReviewError):
    pass


class KpReviewNotConfirmed(KpReviewInconsistent):
    """Human確認待ち/再選定待ち等で、まだ後段へ進めない状態(失敗ではなく待機。rc=4)。"""


class ConfirmedContentIssue(KpReviewNotConfirmed):
    """CONFIRMED_CONTENT_ISSUE(KP-CONFIRMED-CONTENT-PROTECTION-01 M-3): 確定内容そのものに問題/再確認が必要。AIは黙って変更せずユーザー再確認を待つ(rc=4)。
    依頼書(request_md)の先頭に『確定内容の確認依頼』節を置く。"""

    def __init__(self, message: str, kp_dir: str = "", issue_path: str = ""):
        super().__init__(message)
        self.kp_dir = kp_dir
        self.issue_path = issue_path


class ConfirmedContentIntegrityViolation(KpReviewInconsistent):
    """INTEGRITY_VIOLATION(M-3): 確定レコードと成果物/候補doc/review がずれた(パイプライン不具合・手編集)。STOP(rc=3相当)。復元は明示コマンドのみ。"""


class ConfirmedContentLocked(KpReviewError):
    """ユーザー確定済みの選定を書き換え得る操作(select/reselect/ng/unng/resolve-gloss/declare-absent)の拒否(M-4)。"""


def _kp_text_norm(t):
    """KP英語textの比較用正規化: ハイフン→空白・連続空白の圧縮・前後空白除去・小文字化。None/非文字列はそのまま(従来どおり不一致扱い)。"""
    if not isinstance(t, str):
        return t
    return " ".join(t.replace("-", " ").split()).lower()


def _cc():
    """確定内容保護の共通核(er128)。循環importを避けて遅延import。flagの読取点はer128.protection_enabled()のみ(本ファイルは環境変数を読まない)。"""
    import er128_kp_confirmed_content_01 as cc
    return cc


# ============================================================
# 基本helper
# ============================================================
_JST = datetime.timezone(datetime.timedelta(hours=9))


def _now() -> str:
    return datetime.datetime.now(_JST).isoformat(timespec="microseconds")


def sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def jsha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _write_json_atomic(path: str, obj: Any) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _read_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_text_atomic(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def phrase_key(phrase: str) -> str:
    """er105.phrase_keyと同じ正規化(NFKC・空白正規化・小文字化)。coreを軽くするため再実装せず同式を使う。"""
    p = unicodedata.normalize("NFKC", phrase or "")
    p = p.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'}))
    return re.sub(r"\s+", " ", p).strip().lower()


_POSSESSIVE_RE = re.compile(r"\b(one's|someone's|somebody's|your|his|her|their|my|our|its)\b")


def used_form_key(used_form: str) -> str:
    """R-2: 所有格代名詞(one's/your/his/her/their/my/...)を同じプレースホルダへ正規化したキー。"""
    k = phrase_key(used_form)
    return _POSSESSIVE_RE.sub("<poss>", k)


def _is_subseq_tokens(a: list, b: list) -> bool:
    """aがbの連続部分列か。"""
    if not a or len(a) > len(b):
        return False
    for i in range(len(b) - len(a) + 1):
        if b[i:i + len(a)] == a:
            return True
    return False


def candidate_id_for(selection_phrase: str) -> str:
    return "p_" + hashlib.sha1(phrase_key(selection_phrase).encode("utf-8")).hexdigest()[:10]


def paths(kp_dir: str, kind: str = KIND_KP) -> dict:
    pre = FILE_PREFIX[kind]
    return {
        "candidates": f"{kp_dir}/{pre}_candidates.json",
        "review": f"{kp_dir}/{pre}_human_review.json",
        "lock": f"{kp_dir}/{pre}_human_review.lock",
        "request": f"{kp_dir}/{pre}_human_review_request.md",
        "final": f"{kp_dir}/{pre}_selection_final.json",
        "kp": f"{kp_dir}/keywords_canonicalized.json",
        "vocab": f"{kp_dir}/vocab_confirmed.json",
        "alarm": f"{kp_dir}/redundancy_alarm.json",       # 仕様②: 重複アラームの派生ファイル(再導出可能・書込失敗は確定を止めない)
        "rounds": f"{kp_dir}/kp_candidates",
    }


def candidates_sha256(doc: dict) -> str:
    d = {k: v for k, v in doc.items() if k != "candidates_sha256"}
    return jsha(d)


# ============================================================
# 排他lock + 版番号比較更新(R-3)
# ============================================================
class review_lock:
    """O_EXCLの排他lockファイル。保持中は他者が更新を拒否される(ReviewLockHeld)。stale(LOCK_STALE_SEC超)は引き継ぐ。
    lock_path を渡すとそのpathを使う(共有NG registryの排他。KPと文法で共通の実装)。"""

    def __init__(self, kp_dir: str, kind: str = KIND_KP, who: str = "", *, lock_path: Optional[str] = None):
        self.path = lock_path or paths(kp_dir, kind)["lock"]
        self.who = who
        self.fd = None

    def __enter__(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        for _ in range(2):
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self.fd, json.dumps({"pid": os.getpid(), "who": self.who, "at": time.time()}).encode("utf-8"))
                return self
            except FileExistsError:
                try:
                    age = time.time() - os.path.getmtime(self.path)
                except OSError:
                    continue
                if age > LOCK_STALE_SEC:
                    try:
                        os.remove(self.path)
                    except OSError:
                        pass
                    continue
                raise ReviewLockHeld(f"review更新lockが保持されています({self.path})。並行操作を拒否しました。少し待って再実行してください") from None
        raise ReviewLockHeld(f"review更新lockを取得できません({self.path})")

    def __exit__(self, *exc):
        if self.fd is not None:
            try:
                os.close(self.fd)
            except OSError:
                pass
            try:
                os.remove(self.path)
            except OSError:
                pass
        return False


def load_review(kp_dir: str, kind: str = KIND_KP) -> Optional[dict]:
    p = paths(kp_dir, kind)["review"]
    if not os.path.exists(p):
        return None
    return _read_json(p)


def load_candidates(kp_dir: str, kind: str = KIND_KP) -> Optional[dict]:
    p = paths(kp_dir, kind)["candidates"]
    if not os.path.exists(p):
        return None
    return _read_json(p)


def save_review(kp_dir: str, review: dict, *, expected_revision: Optional[int], kind: str = KIND_KP) -> dict:
    """版番号比較更新+os.replace原子書換。expected_revision=None は新規作成(既存があれば拒否)。呼出側がreview_lockを保持していること。"""
    p = paths(kp_dir, kind)["review"]
    cur = _read_json(p) if os.path.exists(p) else None
    if expected_revision is None:
        if cur is not None:
            raise ReviewConflict("reviewが既に存在します(新規作成を拒否)")
        review["revision"] = 1
    else:
        if cur is None or cur.get("revision") != expected_revision:
            raise ReviewConflict(f"review版番号が一致しません(期待={expected_revision}, 現在={None if cur is None else cur.get('revision')})。"
                                 "他の操作が先に更新しました。statusを確認して再実行してください")
        review["revision"] = expected_revision + 1
    review["kind"] = review.get("kind", kind)
    review["selection_signature"] = selection_signature(review) if review.get("status") in FORWARD_STATUSES_BY_KIND.get(kind, FORWARD_STATUSES) else None
    _write_json_atomic(p, review)
    return review


# ============================================================
# NG registry(family+slug+level の共有store。M-5)とNG照合(R-2)
# ============================================================
def _slugsafe(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s or "x")


def store_ng_path(family: str, slug: str, level: str, kind: str = KIND_KP) -> str:
    """共有NG registryのpath。key=family+slug+level(+kind: grammarはKPとentry形式が違うため別file)。run dirに依存しない=copy-runが自動で引き継ぐ。"""
    suffix = "" if kind == KIND_KP else f"__{_slugsafe(kind)}"
    return os.path.join(STORE_ROOT, "ng", f"{_slugsafe(family)}__{_slugsafe(slug)}__{_slugsafe(level)}{suffix}.json")


def store_lock(family: str, slug: str, level: str, kind: str = KIND_KP, who: str = "") -> review_lock:
    """共有NG registryの書込排他lock(KPと文法で共通の実装。read-modify-writeの競合を防ぐ)。"""
    return review_lock("", kind, who, lock_path=store_ng_path(family, slug, level, kind) + ".lock")


def store_load_ng(family: str, slug: str, level: str, kind: str = KIND_KP) -> list:
    p = store_ng_path(family, slug, level, kind)
    if not os.path.exists(p):
        return []
    return [e for e in (_read_json(p).get("entries") or []) if e.get("active", True)]


def _store_all(family: str, slug: str, level: str, kind: str = KIND_KP) -> dict:
    p = store_ng_path(family, slug, level, kind)
    if os.path.exists(p):
        return _read_json(p)
    return {"schema": "kp_ng_registry_v1", "family": family, "slug": slug, "level": level, "kind": kind, "entries": []}


def store_add_ng(family: str, slug: str, level: str, entry: dict, kind: str = KIND_KP) -> None:
    with store_lock(family, slug, level, kind, "add_ng"):
        doc = _store_all(family, slug, level, kind)
        for e in doc["entries"]:
            if e.get("active", True) and e["candidate_id"] == entry["candidate_id"]:
                return
        e2 = dict(entry)
        e2["active"] = True
        doc["entries"].append(e2)
        _write_json_atomic(store_ng_path(family, slug, level, kind), doc)


def store_remove_ng(family: str, slug: str, level: str, *, candidate_id: str = None, phrase: str = None, reason: str, by: str,
                    kind: str = KIND_KP, sentence_key: str = None) -> list:
    """unng: 理由・記録必須。解除は削除でなくactive=falseとremovedの記録を残す。grammarはsentence_key(正規化済みの文)でも指定できる。"""
    if not (reason or "").strip() or not (by or "").strip():
        raise KpReviewError("unngは --reason と --by が必須です(記録必須)")
    with store_lock(family, slug, level, kind, "remove_ng"):
        doc = _store_all(family, slug, level, kind)
        removed = []
        for e in doc["entries"]:
            if not e.get("active", True):
                continue
            if (candidate_id and e["candidate_id"] == candidate_id) or (phrase and e.get("phrase_key") == phrase_key(phrase)) \
                    or (sentence_key and e.get("sentence_key") == sentence_key):
                e["active"] = False
                e["removed"] = {"at": _now(), "by": by, "reason": reason}
                removed.append(e["candidate_id"])
        if removed:
            _write_json_atomic(store_ng_path(family, slug, level, kind), doc)
        return removed


def make_ng_entry(cand: dict, reason: str, by: str) -> dict:
    return {"candidate_id": cand["candidate_id"], "phrase_key": phrase_key(cand.get("selection_phrase") or ""),
            "used_form_key": used_form_key(cand.get("used_form") or ""), "phrase": cand.get("selection_phrase"),
            "used_form": cand.get("used_form"), "reason": reason, "by": by, "at": _now()}


def match_ng(cand: dict, ng_entries: list) -> Optional[str]:
    """returns "exact"(candidate_id/phrase_key/used_form_keyのいずれか一致) / "similar"(NG句を含む/含まれる、R-2) / None。"""
    cid = cand.get("candidate_id")
    pk = phrase_key(cand.get("selection_phrase") or "")
    uk = used_form_key(cand.get("used_form") or "")
    sim = False
    for n in ng_entries:
        if n.get("candidate_id") == cid or (pk and n.get("phrase_key") == pk) or (uk and n.get("used_form_key") == uk):
            return "exact"
        for a, b in ((uk, n.get("used_form_key") or ""), (pk, n.get("phrase_key") or "")):
            ta, tb = a.split(), b.split()
            if ta and tb and ta != tb and (_is_subseq_tokens(ta, tb) or _is_subseq_tokens(tb, ta)):
                sim = True
    return "similar" if sim else None


def ng_entries_of(review: Optional[dict], family: str = None, slug: str = None, level: str = None) -> list:
    """reviewのng(run内コピー)と共有storeのactive NGの和(candidate_idで重複排除)。"""
    out, seen = [], set()
    src = list((review or {}).get("ng") or [])
    if family and slug and level:
        src += store_load_ng(family, slug, level)
    for e in src:
        if e.get("active", True) and e["candidate_id"] not in seen:
            seen.add(e["candidate_id"])
            out.append(e)
    return out


# ============================================================
# 不在宣言(M-6 / R-7)。mode読取の単一関数 read_mode_declaration
# ============================================================
def _requires_user_ref(by: str) -> bool:
    toks = [t for t in re.split(r"[^a-z]+", (by or "").strip().lower()) if t]
    return bool(toks) and toks[0] in _AI_BY_PREFIXES


def _run_key(run_dir: str) -> str:
    return os.path.normcase(os.path.abspath(run_dir))


def declarations_path(run_dir: str) -> str:
    return os.path.join(run_dir, "kp_review_mode.json")


# 宣言のsource(er120.AUTO_DECLARATION_SOURCESと一致。突合testで固定)
DECLARATION_SOURCES = ("cli_runner_arg", "declare_absent_cli")


def add_declaration(*, run_dirs: list, by: str, reason: str, user_ref: str = "", source: str = "declare_absent_cli",
                    rounds: Optional[list] = None, candidates_sha256: Optional[str] = None) -> list:
    """明示的な不在宣言を記録する(自動確定の唯一の入口)。**個別run・round・候補shaに紐づく宣言のみ**(期限付き/範囲付き宣言は不採用=R-7撤去)。
    declared_by・reasonは必須。AI(Fable等)が宣言する場合はユーザー発言の参照(user_ref)が必須(AIの『不在とみなした』を自動確定の経路にしない)。"""
    if not (by or "").strip():
        raise KpReviewError("不在宣言には --by(宣言者)が必須です")
    if not (reason or "").strip():
        raise KpReviewError("不在宣言には --reason が必須です")
    if _requires_user_ref(by) and not (user_ref or "").strip():
        raise KpReviewError("AIが宣言する場合は --user-ref(ユーザー発言の参照)が必須です(AIの『不在とみなした』を自動確定の経路にしない)")
    if source not in DECLARATION_SOURCES:
        raise KpReviewError(f"宣言のsourceが不正です: {source!r}(許可={DECLARATION_SOURCES})")
    if not run_dirs:
        raise KpReviewError("不在宣言には対象のrun dir(--runs)が必須です(範囲・期限付きの宣言は受け付けません)")
    _cc().guard_declaration(run_dirs)   # M-4: ユーザー確定済みのrunには不在宣言(AUTO)で選定を書き換えない
    rec = {"mode": "auto", "declared_by": by, "declared_at": _now(), "source": source, "reason": reason,
           "user_ref": user_ref or "", "rounds": list(rounds) if rounds else [1],
           "candidates_sha256": candidates_sha256}
    ids = []
    for rd in run_dirs:
        r = dict(rec)
        r["declaration_id"] = "d_" + jsha([rec, _run_key(rd), time.time()])[:12]
        r["scope"] = {"run": _run_key(rd)}
        path = declarations_path(rd)
        doc = _read_json(path) if os.path.exists(path) else {"schema": "kp_review_mode_v1", "declarations": []}
        doc["declarations"].append(r)
        _write_json_atomic(path, doc)
        ids.append(r["declaration_id"])
    return ids


def _decl_valid(d: dict, *, run_dir: str, review: Optional[dict], round_no: int, cands_sha: Optional[str]) -> bool:
    if d.get("mode") != "auto" or not d.get("declared_by") or not d.get("reason"):
        return False
    if d.get("source") not in DECLARATION_SOURCES:
        return False
    if _requires_user_ref(d.get("declared_by")) and not d.get("user_ref"):
        return False
    if (d.get("scope") or {}).get("run") != _run_key(run_dir):
        return False
    if d.get("rounds") and round_no not in d["rounds"]:
        return False
    if d.get("candidates_sha256") and d["candidates_sha256"] != cands_sha:
        return False
    # M-6: Humanの操作(select/reselect/ng/unng/resolve-gloss等)があった時点で、それ以前の宣言は失効する
    last_human = (review or {}).get("last_human_op_at")
    if last_human and d.get("declared_at", "") <= last_human:
        return False
    return True


def read_mode_declaration(run_dir: str, *, level: str = "", review: Optional[dict], round_no: int,
                          cands_sha: Optional[str]) -> Optional[dict]:
    """自動確定モードの**単一読取点**(KP・文法で共通)。有効な宣言があれば下記dict形を返し、無ければNone(=待機)。
    dict形: {mode:"auto", declared_by, declared_at, reason, source∈DECLARATION_SOURCES, user_ref, declaration_id, rounds, candidates_sha256}
    (er120.normalize_modeが受け付ける形)。環境変数・関数引数・設定dict・hooks・既定値は読まない(run dirの宣言ファイルのみ)。"""
    p = declarations_path(run_dir)
    if not os.path.exists(p):
        return None
    try:
        cands = list(_read_json(p).get("declarations") or [])
    except (OSError, ValueError):
        return None
    for d in cands:
        if _decl_valid(d, run_dir=run_dir, review=review, round_no=round_no, cands_sha=cands_sha):
            return {k: d.get(k) for k in ("mode", "declared_by", "declared_at", "reason", "source", "user_ref", "declaration_id",
                                          "rounds", "candidates_sha256")}
    return None


# ============================================================
# 選択の検証(select時とfinalize時で同じ関数。b-3)
# ============================================================
def sel_ids(selection: dict, slot: str) -> list:
    return list((selection or {}).get(slot) or [])


def _cand_map(cands: dict) -> dict:
    return {c["candidate_id"]: c for c in cands.get("candidates") or []}


def _pairs(cands: dict) -> set:
    out = set()
    for c in cands.get("candidates") or []:
        for other in (c.get("flags") or {}).get("redundant_with") or []:
            out.add(frozenset((c["candidate_id"], other)))
    return out


# ---- 仕様① 候補は人間への提示前に品質検査(HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01、ユーザー正式採用2026-10-29)
# 提示集合の唯一の定義: 「提示された候補は、単独で選んでも確定時の候補単位検査(validate_selection / cmd_from_form の ja_gloss_status)を必ず通る」。
# 候補生成(_gate_chain)・HR依頼書(render_request_md)・フォームdata(exporter)・auto_select・ニュアンスpool(er134.presented_pool)はすべてここを通る(二重定義しない)。
# 品質基準(11 QAフィールド・閾値)は変更しない。変えるのは『不合格候補を旗付きで提示→除外して提示しない』だけ。
PRESENTABLE_FILTER_VERSION = "presentable_v1_2026-10-29"
GLOSS_OFFICIAL_GATES = ("ALIGNED", "HUMAN_RESOLVED")          # exporter.gloss_status の official 条件(Production正式経路)と同一
BLOCKER_STAGE = {"qa_fail": "canonicalization_qa", "canonicalization_qa": "canonicalization_qa", "rescue_unverified": "canonicalization_qa",
                 "gloss_hr_pending": "gloss_unresolved", "gloss_not_official": "gloss_unresolved", "not_selectable": "not_selectable"}
PRESENTATION_FILTER_STAGES = ("canonicalization_qa", "gloss_unresolved")     # 生成時にdroppedへ入る段名(補完backfillの対象。GATE_DROP_EXEMPTには入れない)


def presentation_blockers(c: dict) -> list:
    """候補cが『人間に提示してはならない』理由 [(code, 日本語理由)]。空=提示可能。決定論・API 0。
    fail-closed: qa_overall_statusが PASS 以外(欠落・未知値を含む)、救済(canonicalization段)でQA再判定PASS/gloss再整合REALIGNEDが揃わない候補、
    gloss未確定(HR待ち)・正式訳でない候補は提示しない。"""
    out = []
    it = c.get("item") or {}
    fl = c.get("flags") or {}
    if not c.get("human_selectable", True):
        out.append(("not_selectable", "選択不可(Gate不合格)"))
    st = it.get("qa_overall_status")
    if fl.get("qa_fail") or st == "REVIEW_REQUIRED":
        bad = [k for k, v in (it.get("qa") or {}).items() if v == "FAIL"]
        out.append(("qa_fail", "canonicalization QA不合格(REVIEW_REQUIRED)" + (": " + ", ".join(bad) if bad else "")))
    elif st != "PASS":
        out.append(("canonicalization_qa", f"canonicalization QAの判定が確認できない(qa_overall_status={st!r}。未検査候補は提示しない=fail-closed)"))
    rs = c.get("rescue") or it.get("rescue")
    if rs and rs.get("canonicalization"):
        qs, gs = (rs.get("qa") or {}).get("status"), (rs.get("gloss") or {}).get("status")
        if qs != "PASS" or gs != "REALIGNED":
            out.append(("rescue_unverified", f"救済後の表現が未検査(QA再判定={qs} / gloss再整合={gs})。検査未了の候補は提示しない=fail-closed"))
    gate_gloss = (c.get("gates") or {}).get("gloss")
    if fl.get("gloss_hr_pending") or gate_gloss == "HR_PENDING":
        out.append(("gloss_hr_pending", "日本語訳が未確定(gloss HR待ち)"))
    elif not (c.get("japanese_gloss") or "").strip() or gate_gloss not in GLOSS_OFFICIAL_GATES:
        out.append(("gloss_not_official", f"日本語訳が正式でない(gloss gate={gate_gloss!r})"))
    return out


def blocker_stage(blockers: list) -> str:
    codes = [b[0] for b in blockers]
    for k in ("qa_fail", "canonicalization_qa", "rescue_unverified"):
        if k in codes:
            return BLOCKER_STAGE[k]
    return BLOCKER_STAGE[codes[0]]


def presentable_candidates(cands) -> list:
    """提示可能な候補(元の順序・元のdict)。candsは候補doc(dict)またはcandidate listのどちらでも可。"""
    lst = cands.get("candidates") if isinstance(cands, dict) else cands
    return [c for c in (lst or []) if not presentation_blockers(c)]


def excluded_from_presentation(cands) -> list:
    """提示から外した候補 [{candidate_id, ai_rank, used_form, codes, reasons}]。HR依頼書・exporterのdata_warningsに記録する(隠さない)。"""
    lst = cands.get("candidates") if isinstance(cands, dict) else cands
    out = []
    for c in lst or []:
        b = presentation_blockers(c)
        if b:
            out.append({"candidate_id": c.get("candidate_id"), "ai_rank": c.get("ai_rank"), "used_form": c.get("used_form"),
                        "codes": [x[0] for x in b], "reasons": [x[1] for x in b]})
    return out


# ---- 仕様② 意味・用法の重複は『アラームのみ』(確定・音声・組立・Productionを停止しない)。判定(4観点x10ペアLLM)とflags.redundant_withは維持。
ASPECTS = ("meaning_overlap", "usage_context_overlap", "grammatical_teaching_value_overlap", "conceptual_role_overlap")
SLOT_LABEL_JA = {"key_phrase": "Key Phrase(①)", "extra_explanation": "追加解説(②)", "meaning_display": "本文意味(③)"}


def redundancy_alarms(cands: dict, slots: dict, *, source: str = "candidate_qa") -> list:
    """選定された表現同士の重複アラーム(純関数・API 0)。slots={slot名(key_phrase|extra_explanation|meaning_display): [candidate_id]}。
    候補docの redundancy_qa.duplicate_pairs(ai_rank対・4観点・reasoning)から、選定内の対だけを返す。duplicate_pairs無しで flags.redundant_with だけある
    対は reasoning 無し(source=flags_only)で返す。停止条件ではない(情報提供)。"""
    cm = _cand_map(cands)
    rank_to_cid = {c.get("ai_rank"): c["candidate_id"] for c in cm.values()}
    slot_of = {}
    for slot, ids in (slots or {}).items():
        for i in ids or []:
            slot_of.setdefault(i, slot)
    out, seen = [], set()

    def _add(a, b, detail):
        if a not in slot_of or b not in slot_of or a == b:
            return
        key = frozenset((a, b))
        if key in seen:
            return
        seen.add(key)
        ca, cb = cm.get(a, {}), cm.get(b, {})
        out.append({"candidate_id_a": a, "candidate_id_b": b, "used_form_a": ca.get("used_form"), "used_form_b": cb.get("used_form"),
                    "ai_rank_a": ca.get("ai_rank"), "ai_rank_b": cb.get("ai_rank"), "slot_a": slot_of[a], "slot_b": slot_of[b],
                    "slot_label_a": SLOT_LABEL_JA.get(slot_of[a]), "slot_label_b": SLOT_LABEL_JA.get(slot_of[b]),
                    "aspects": {k: (detail or {}).get(k) for k in ASPECTS} if detail else None,
                    "reasoning": (detail or {}).get("reasoning"), "source": source if detail else "flags_only"})
    for p in ((cands.get("redundancy_qa") or {}).get("duplicate_pairs") or []):
        a, b = rank_to_cid.get(p.get("rank_a")), rank_to_cid.get(p.get("rank_b"))
        if a and b:
            _add(a, b, p)
    for pr in sorted(tuple(sorted(x)) for x in _pairs(cands)):
        _add(pr[0], pr[1], None)
    out.sort(key=lambda x: (x["ai_rank_a"] or 0, x["ai_rank_b"] or 0))
    return out


def final_qa_to_alarm(fq: dict, cands: dict) -> dict:
    """確定集合Redundancy QAのNG結果(_run_final_qaの戻り)を ALARM形へ変換して保存用にする(人間選定の確定のみ。AUTOでは使わない)。
    `_run_final_qa`の判定値(REDUNDANCY_NG/ng_pairs)は変えない(AUTO分岐が使う)。判定不能はここへ来ない(KpReviewError=fail-closed)。"""
    cm = _cand_map(cands)
    pairs = []
    for name, r in (fq.get("results") or {}).items():
        if r.get("status") != "REDUNDANCY_NG":
            continue
        for p in r.get("duplicate_pairs") or []:
            pairs.append({"set": name, "rank_a": p.get("rank_a"), "rank_b": p.get("rank_b"), "reasoning": p.get("reasoning"),
                          "aspects": {k: p.get(k) for k in ASPECTS}})
    ng = [list(p) for p in fq.get("ng_pairs") or []]
    for q, (a, b) in zip(pairs, ng):     # _run_final_qaは同順でng_pairsへ積む
        q.update(candidate_id_a=a, candidate_id_b=b, used_form_a=(cm.get(a) or {}).get("used_form"), used_form_b=(cm.get(b) or {}).get("used_form"))
    return {"status": "REDUNDANCY_ALARM", "judged_status": "REDUNDANCY_NG", "nonblocking": True, "key": fq.get("key"),
            "results": fq.get("results"), "alarm_pairs": pairs}


def vocab_enabled(level: str, review: Optional[dict] = None) -> bool:
    """Part 1(単語解説=vocab)を扱うか。Advanced(b1b)は常に、Standard(a2)はreviewに`std_part1`マークがあるときだけ(SLOT-23 委任_04B、
    ユーザー正式決定2026-10-27 Std②=C案・遡及なし)。vocab可否の単一関数(select/auto/最終QA/finalize/消費側検査はすべてここを通る)。"""
    return level == "b1b" or bool((review or {}).get("std_part1"))


def issue_std_part1_mark(review: dict) -> dict:
    """新規KP reviewへ新表示仕様マーク(std_part1)を付与する唯一の関数(KP reviewのみ。grammarは不変)。a2ではvocab(Std Part 1)を有効にし、
    b1bではvocabは元々常に有効なので『新表示仕様の記事』という印としてだけ働く(確定レコードのdisplay_specの導出元)。
    new_reviewから呼ぶ(M14接続済み・委任_05M。新規reviewのみ。既存の確定済み記事は reconsume 明示実行まで不変=遡及なし)。"""
    if review.get("kind", KIND_KP) == KIND_KP:
        review["std_part1"] = True
    return review


def validate_selection(cands: dict, selection: dict, *, level: str, kind: str = KIND_KP, accepted_qa_fail: Optional[list] = None,
                       ng_entries: Optional[list] = None, allow_similar_ng: bool = True, std_part1: bool = False) -> list:
    """returns エラー文のlist(空=合格)。select時とfinalize時の両方で呼ぶ。std_part1=reviewのStdマーク(a2でvocabを許可する)。"""
    errs = []
    cm = _cand_map(cands)
    accepted_qa_fail = set(accepted_qa_fail or [])
    ng_entries = ng_entries or []
    rules = SLOT_RULES[kind]
    chosen_all = []
    for slot, rule in rules.items():
        ids = sel_ids(selection, slot)
        if len(ids) != len(set(ids)):
            errs.append(f"{slot}: 同じ候補が重複して選ばれています")
        if len(ids) > rule["max"]:
            errs.append(f"{slot}: 最大{rule['max']}件です(指定{len(ids)}件)")
        if len(set(ids)) < rule["min"] and not (kind == KIND_KP and slot == "vocab"):
            errs.append(f"{slot}: 最低{rule['min']}件が必要です")
        for i in ids:
            if i not in cm:
                errs.append(f"{slot}: 候補{i}が存在しません")
        chosen_all += [i for i in ids if i in cm]
    if kind == KIND_KP:
        kp, vocab = sel_ids(selection, "kp"), sel_ids(selection, "vocab")
        ven = vocab_enabled(level, {"std_part1": std_part1})
        if vocab and not ven:
            errs.append("vocab(単語解説5件)はAdvanced(b1b)またはStd Part 1マーク付きreviewのみです。このreviewでは指定できません(遡及なし)")
        if ven:
            if not vocab:
                errs.append("vocab: 単語解説(vocab)の選択が必要です(KP3件を含む最大5件)")
            elif not set(kp) <= set(vocab):
                errs.append("vocab: KPに選んだ候補をすべて含めてください(KP ⊂ vocab)")
    # 仕様②(2026-10-29): 意味・用法の重複(Redundancy pair)は選定・確定を拒否しない(アラームのみ=redundancy_alarms)。他の候補単位検査は従来どおり。
    seen = list(dict.fromkeys(chosen_all))
    for i, a in enumerate(seen):
        c = cm.get(a)
        if c is None:
            continue
        if not c.get("human_selectable", True):
            errs.append(f"候補{c['ai_rank']}({c.get('used_form')})は選択できません(Gate不合格)")
        if c.get("flags", {}).get("qa_fail") and a not in accepted_qa_fail:
            errs.append(f"候補{c['ai_rank']}({c.get('used_form')})はcanonicalization QA FAIL(REVIEW_REQUIRED)です。採用するなら --accept-qa-fail {c['ai_rank']} を明示してください")
        if c.get("flags", {}).get("gloss_hr_pending"):
            errs.append(f"候補{c['ai_rank']}({c.get('used_form')})はgloss HR待ちです。resolve-gloss後に選択してください")
        m = match_ng(c, ng_entries)
        if m == "exact":
            errs.append(f"候補{c['ai_rank']}({c.get('used_form')})はNGに指定済みです(選択できません)")
        elif m == "similar" and not allow_similar_ng:
            errs.append(f"候補{c['ai_rank']}({c.get('used_form')})はNG句に類似しています")
    return errs


def auto_eligible_now(c: dict, ng_entries: list) -> bool:
    if not c.get("auto_eligible", False):
        return False
    return match_ng(c, ng_entries) is None


def auto_select(cands: dict, *, level: str, kind: str = KIND_KP, ng_entries: Optional[list] = None,
                excluded_ids: Optional[list] = None, std_part1: bool = False) -> dict:
    """決定論のAUTO規則: auto_eligibleかつNG/類似NGでなく、既採用候補とredundancy pairを持たない候補をai_rank順に走査。
    KP=先頭3、vocab(Advのみ)=先頭5(KPを含む)。不足は不足のまま(数合わせなし)。grammar=先頭1。"""
    ng_entries = ng_entries or []
    excluded = set(excluded_ids or [])
    pairs = _pairs(cands)
    chosen = []
    pool = presentable_candidates(cands) if kind == KIND_KP else (cands.get("candidates") or [])    # 提示集合はKPのみ(文法候補はQA/glossの構造が別=対象外)
    for c in sorted(pool, key=lambda x: x["ai_rank"]):
        cid = c["candidate_id"]
        if cid in excluded or not auto_eligible_now(c, ng_entries):
            continue
        if any(frozenset((cid, x)) in pairs for x in chosen):
            continue
        chosen.append(cid)
    if kind == KIND_GRAMMAR:
        return {"grammar": chosen[:1]}
    kp = chosen[:KP_FINAL_MAX]
    vocab = chosen[:VOCAB_COUNT_MAX] if vocab_enabled(level, {"std_part1": std_part1}) else []
    return {"kp": kp, "vocab": vocab}


def selection_signature(review: dict) -> str:
    if review.get("kind") == KIND_GRAMMAR:   # 突合: 文法の確定recordの署名はer120の単一関数(同一payload)
        import er120_part2_grammar_production_01 as _g
        return _g.grammar_selection_signature(review)
    sel = review.get("selection") or {}
    ng = sorted(f"{e['candidate_id']}|{e.get('phrase_key')}" for e in (review.get("ng") or []) if e.get("active", True))
    payload = {"kind": review.get("kind", KIND_KP), "text_sha256": review.get("text_sha256"),
               "candidates_sha256": review.get("candidates_sha256"),
               "selection": {k: sorted(v) for k, v in sel.items()}, "ng": ng, "status": review.get("status")}
    if review.get("std_part1"):   # マーク付きreviewだけ署名に含める(マーク無し=旧署名のまま不変。遡及なし)
        payload["std_part1"] = True
    return jsha(payload)


# ============================================================
# review生成・操作(CLI/runner共通。lock+版番号)
# ============================================================
def new_review(cands: dict, *, kind: str = KIND_KP, article_key: Optional[dict] = None, prev: Optional[dict] = None) -> dict:
    r = {"schema": SCHEMA_REVIEW, "kind": kind, "level": cands["level"], "text_sha256": cands["text_sha256"],
         "candidates_sha256": cands["candidates_sha256"], "round": cands.get("round", 1), "status": ST_PENDING,
         "revision": 0, "article_key": article_key or (prev or {}).get("article_key"),
         "selection": {}, "accepted_qa_fail": [], "accept_ai_default": False, "accept_ai_shown_candidates_sha256": None,
         "verdicts": {c["candidate_id"]: None for c in cands.get("candidates") or []},
         "ng": list((prev or {}).get("ng") or []), "reselect_count": int((prev or {}).get("reselect_count") or 0),
         "last_human_op_at": (prev or {}).get("last_human_op_at"), "mode_used": None, "final_qa": None,
         "published_selection_signature": (prev or {}).get("published_selection_signature"),
         "history": list((prev or {}).get("history") or []), "selection_signature": None}
    if (prev or {}).get("std_part1") and kind == KIND_KP:   # 既にマーク付きの選び直しround/再生成は継続(新規付与ではない)
        r["std_part1"] = True
    issue_std_part1_mark(r)   # M14接続(SLOT-23 委任_05M): 新規reviewのみ(KPのみ・prevのマーク継承は上で済)。既存記事は reconsume 明示実行まで不変=遡及なし
    r["history"].append({"at": _now(), "event": "candidates_generated", "by": "runner",
                         "detail": {"round": r["round"], "candidates_sha256": r["candidates_sha256"]}})
    return r


def _event(review: dict, event: str, by: str, detail: Optional[dict] = None) -> None:
    review.setdefault("history", []).append({"at": _now(), "event": event, "by": by, "detail": detail or {}})


def _rank_to_cid(cands: dict, ranks: list) -> list:
    by_rank = {c["ai_rank"]: c["candidate_id"] for c in cands.get("candidates") or []}
    out = []
    for r in ranks:
        if r not in by_rank:
            raise KpReviewError(f"番号{r}の候補がありません(表のai_rank)")
        out.append(by_rank[r])
    return out


def op_select(kp_dir: str, *, kp_ranks: list, vocab_ranks: Optional[list] = None, ng: Optional[dict] = None,
              accept_qa_fail: Optional[list] = None, by: str, accept_ai: bool = False, shown_candidates_sha256: Optional[str] = None,
              kind: str = KIND_KP, meaning_display_ids: Optional[list] = None) -> dict:
    """Humanの選択(CLI)。ng={ai_rank: reason}。検証→REVIEWED。PENDING_REVIEW(または確定済みの事後Review)からのみ。
    meaning_display_ids: フォーム経由の③本文意味のcandidate_id(selectionには入らない。重複アラームの対象にだけ含める。仕様②/Opus M6)。"""
    if not (by or "").strip():
        raise KpReviewError("--by(操作者)が必須です")
    with review_lock(kp_dir, kind, by):
        review = load_review(kp_dir, kind)
        cands = load_candidates(kp_dir, kind)
        if review is None or cands is None:
            raise KpReviewError("候補/reviewがありません(まず制作を実行して候補を生成してください)")
        if kind == KIND_KP:
            _cc().guard(kp_dir, "select/--accept-ai")   # M-4: ユーザー確定済みなら拒否(confirm-revise/revokeを案内)
        if review["status"] in (ST_RESELECT, ST_STALE):
            raise KpReviewError(f"status={review['status']}のためselectできません(候補の再生成後に選択してください)")
        if review["candidates_sha256"] != cands["candidates_sha256"]:
            raise KpReviewError("reviewと候補ファイルのcandidates_sha256が一致しません")
        level = review["level"]
        ng = ng or {}
        ng_cids = {}
        for rk, reason in ng.items():
            (cid,) = _rank_to_cid(cands, [rk])
            if not (reason or "").strip():
                raise KpReviewError(f"NG指定には理由が必要です(番号{rk})")
            ng_cids[cid] = reason
        cm = _cand_map(cands)
        # NG登録(run内コピー+共有store)を先に反映して検証に含める
        ak = review.get("article_key") or {}
        new_ng = []
        for cid, reason in ng_cids.items():
            ent = make_ng_entry(cm[cid], reason, by)
            new_ng.append(ent)
        review_ng = list(review.get("ng") or []) + [e for e in new_ng if e["candidate_id"] not in {x["candidate_id"] for x in review.get("ng") or []}]
        if accept_ai:
            if shown_candidates_sha256 != cands["candidates_sha256"]:
                raise KpReviewError("--accept-aiは、表示した候補(candidates_sha256)に対してのみ使えます(未表示の候補への了承は拒否)")
            selection = auto_select(cands, level=level, kind=kind, ng_entries=ng_entries_of({"ng": review_ng}, ak.get("family"), ak.get("slug"), level),
                                    std_part1=bool(review.get("std_part1")))
            accepted_qf = list(accept_qa_fail or [])
        else:
            kp_ids = _rank_to_cid(cands, list(kp_ranks or []))
            v_ids = _rank_to_cid(cands, list(vocab_ranks or [])) if vocab_ranks else []
            if kind == KIND_KP and vocab_enabled(level, review) and vocab_ranks is None:
                raise KpReviewError("このreview(Advanced、またはStd Part 1マーク付き)では --vocab(単語解説。KP3件を含む最大5件)の指定が必要です")
            selection = {"kp": kp_ids, "vocab": v_ids} if kind == KIND_KP else {"grammar": kp_ids}
            accepted_qf = _rank_to_cid(cands, list(accept_qa_fail or []))
        errs = validate_selection(cands, selection, level=level, kind=kind, accepted_qa_fail=accepted_qf,
                                  ng_entries=ng_entries_of({"ng": review_ng}, ak.get("family"), ak.get("slug"), level),
                                  std_part1=bool(review.get("std_part1")))
        if errs:
            raise KpReviewError("選択が検証に失敗しました:\n- " + "\n- ".join(errs))
        # 反映
        prev_status = review["status"]
        review["ng"] = review_ng
        for e in new_ng:
            if ak.get("family"):
                store_add_ng(ak["family"], ak["slug"], level, e)
        selected = set(sum((list(v) for v in selection.values()), []))
        kp_set = set(sel_ids(selection, "kp")) | set(sel_ids(selection, "grammar"))
        verdicts = {}
        ng_all_ids = {e["candidate_id"] for e in review_ng}
        for cid in cm:
            if cid in kp_set:
                verdicts[cid] = "SELECTED_KP" if kind == KIND_KP else "SELECTED"
            elif cid in selected:
                verdicts[cid] = "SELECTED_VOCAB"
            elif cid in ng_all_ids:
                verdicts[cid] = "NG"
            else:
                verdicts[cid] = "NOT_SELECTED"
        review.update(selection=selection, accepted_qa_fail=accepted_qf, accept_ai_default=bool(accept_ai),
                      accept_ai_shown_candidates_sha256=(shown_candidates_sha256 if accept_ai else None),
                      verdicts=verdicts, status=ST_REVIEWED, last_human_op_at=_now(), mode_used=None, final_qa=None)
        _event(review, "select" if not accept_ai else "accept_ai", by,
               {"from": prev_status, "selection": selection, "ng": list(ng_cids), "accepted_qa_fail": accepted_qf})
        if kind == KIND_KP:     # 仕様②: 重複はアラームとして記録するだけ(拒否しない)。新roundの選定は前の選定のアラームを引き継がない(ここで置換)
            alarms = redundancy_alarms(cands, {"key_phrase": sel_ids(selection, "kp"),
                                               "extra_explanation": [i for i in sel_ids(selection, "vocab") if i not in set(sel_ids(selection, "kp"))],
                                               "meaning_display": list(meaning_display_ids or [])})
            review["redundancy_alarms"] = alarms
            if alarms:
                _event(review, "redundancy_alarm", by, {"n": len(alarms), "pairs": [[a["candidate_id_a"], a["candidate_id_b"]] for a in alarms], "blocking": False})
        out = save_review(kp_dir, review, expected_revision=review["revision"], kind=kind)
        invalidate_gloss_snapshot(kp_dir)   # M-2: 選び直し時に未消費のgloss HR snapshot(旧選定)を失効させる
        return out


def op_reselect(kp_dir: str, *, ng: Optional[dict] = None, note: str = "", by: str, kind: str = KIND_KP) -> dict:
    """再選定要求。ng={ai_rank: reason}をNGへ。上限RESELECT_MAX/レベル/run。status=RESELECTION_REQUESTED(次回起動で候補再生成)。"""
    if not (by or "").strip():
        raise KpReviewError("--by(操作者)が必須です")
    with review_lock(kp_dir, kind, by):
        review = load_review(kp_dir, kind)
        cands = load_candidates(kp_dir, kind)
        if review is None or cands is None:
            raise KpReviewError("候補/reviewがありません")
        if kind == KIND_KP:
            _cc().guard(kp_dir, "reselect")   # M-4
        if review["status"] in (ST_RESELECT, ST_STALE):
            raise KpReviewError(f"status={review['status']}です(既に再選定要求済み/無効)")
        if review.get("reselect_count", 0) >= RESELECT_MAX:
            raise KpReviewError(f"再選定の上限({RESELECT_MAX}回/レベル/run)に達しています。Fableへ報告してください(推測で続行しません)")
        cm = _cand_map(cands)
        ak = review.get("article_key") or {}
        for rk, reason in (ng or {}).items():
            (cid,) = _rank_to_cid(cands, [rk])
            if not (reason or "").strip():
                raise KpReviewError(f"NG指定には理由が必要です(番号{rk})")
            ent = make_ng_entry(cm[cid], reason, by)
            if cid not in {e["candidate_id"] for e in review.get("ng") or []}:
                review.setdefault("ng", []).append(ent)
            if ak.get("family"):
                store_add_ng(ak["family"], ak["slug"], review["level"], ent)
            review["verdicts"][cid] = "NG"
        prev = review["status"]
        review.update(status=ST_RESELECT, reselect_count=review.get("reselect_count", 0) + 1, last_human_op_at=_now(),
                      selection={}, mode_used=None, final_qa=None, redundancy_alarms=[])
        _event(review, "reselect", by, {"from": prev, "note": note, "ng": [cid for cid in review["verdicts"] if review["verdicts"][cid] == "NG"]})
        out = save_review(kp_dir, review, expected_revision=review["revision"], kind=kind)
        invalidate_gloss_snapshot(kp_dir)   # M-2
        return out


def op_ng(kp_dir: str, *, ng: dict, by: str, kind: str = KIND_KP) -> dict:
    """候補をNGにする(選択はしない)。以後の宣言は失効する(last_human_op_at更新)。"""
    with review_lock(kp_dir, kind, by):
        review, cands = load_review(kp_dir, kind), load_candidates(kp_dir, kind)
        if review is None or cands is None:
            raise KpReviewError("候補/reviewがありません")
        if kind == KIND_KP:
            _cc().guard(kp_dir, "ng")   # M-4
        cm = _cand_map(cands)
        ak = review.get("article_key") or {}
        for rk, reason in ng.items():
            (cid,) = _rank_to_cid(cands, [rk])
            if not (reason or "").strip():
                raise KpReviewError("NG指定には理由が必要です")
            ent = make_ng_entry(cm[cid], reason, by)
            if cid not in {e["candidate_id"] for e in review.get("ng") or []}:
                review.setdefault("ng", []).append(ent)
            if ak.get("family"):
                store_add_ng(ak["family"], ak["slug"], review["level"], ent)
            review["verdicts"][cid] = "NG"
        review["last_human_op_at"] = _now()
        if review["status"] in FORWARD_STATUSES:
            sel = review.get("selection") or {}
            bad = [cid for cid in sum((list(v) for v in sel.values()), []) if cid in {e["candidate_id"] for e in review["ng"]}]
            if bad:
                review.update(status=ST_PENDING, selection={}, final_qa=None, mode_used=None, redundancy_alarms=[])
                _event(review, "ng_removed_selection", by, {"ids": bad})
        _event(review, "ng", by, {"ids": [_rank_to_cid(cands, [r])[0] for r in ng]})
        return save_review(kp_dir, review, expected_revision=review["revision"], kind=kind)


def op_unng(kp_dir: str, *, rank: Optional[int] = None, phrase: Optional[str] = None, reason: str, by: str, kind: str = KIND_KP) -> list:
    """NG解除。理由・記録必須(R-2)。共有storeとrun内コピーの両方を更新。"""
    with review_lock(kp_dir, kind, by):
        review, cands = load_review(kp_dir, kind), load_candidates(kp_dir, kind)
        if review is None:
            raise KpReviewError("reviewがありません")
        if kind == KIND_KP:
            _cc().guard(kp_dir, "unng")   # M-4
        cid = _rank_to_cid(cands, [rank])[0] if rank is not None else None
        ak = review.get("article_key") or {}
        removed = []
        if ak.get("family"):
            removed = store_remove_ng(ak["family"], ak["slug"], review["level"], candidate_id=cid, phrase=phrase, reason=reason, by=by)
        else:
            if not (reason or "").strip():
                raise KpReviewError("unngは --reason が必須です")
        for e in review.get("ng") or []:
            if (cid and e["candidate_id"] == cid) or (phrase and e.get("phrase_key") == phrase_key(phrase)):
                e["active"] = False
                e["removed"] = {"at": _now(), "by": by, "reason": reason}
                removed.append(e["candidate_id"])
        for r in removed:
            if review["verdicts"].get(r) == "NG":
                review["verdicts"][r] = None
        review["last_human_op_at"] = _now()
        _event(review, "unng", by, {"removed": sorted(set(removed)), "reason": reason})
        save_review(kp_dir, review, expected_revision=review["revision"], kind=kind)
        return sorted(set(removed))


def op_mark_published(kp_dir: str, *, by: str, kind: str = KIND_KP) -> dict:
    """R-5: 公開した時点の確定署名を別保存する。以後の事後Review(AUTO->REVIEWED等)で確定版が変わっても、公開版は自動では差し替えない
    (status/verifyが『公開版と確定版の差』として表示するだけ。差替えは別の明示操作)。"""
    if not (by or "").strip():
        raise KpReviewError("--by(操作者)が必須です")
    with review_lock(kp_dir, kind, by):
        review = load_review(kp_dir, kind)
        if review is None or review["status"] not in FORWARD_STATUSES:
            raise KpReviewError("確定済み(REVIEWED/UNREVIEWED_AUTO_ADOPTED)のreviewだけ公開済みとして記録できます")
        review["published_selection_signature"] = review["selection_signature"]
        _event(review, "mark_published", by, {"selection_signature": review["selection_signature"], "status": review["status"]})
        return save_review(kp_dir, review, expected_revision=review["revision"], kind=kind)


def published_diff(kp_dir: str, kind: str = KIND_KP) -> dict:
    """公開版(published_selection_signature)と現在の確定版の関係。差があっても自動差替えはしない(R-5)。"""
    r = load_review(kp_dir, kind)
    if r is None:
        return {"published": None, "current": None, "differs": False}
    pub, cur = r.get("published_selection_signature"), r.get("selection_signature")
    return {"published": pub, "current": cur, "differs": bool(pub and cur and pub != cur),
            "note": ("公開版と確定版が異なります(自動では差し替えません。差替えは明示操作)" if pub and cur and pub != cur else "")}


GLOSS_HR_SNAPSHOT = "gloss_alignment_pending_result.json"


def invalidate_gloss_snapshot(kp_dir: str) -> Optional[str]:
    """M-2: select/reselect等でHumanが選び直した時点で、未消費のgloss HR snapshot(旧選定を含みうる)を失効させる。"""
    p = f"{kp_dir}/{GLOSS_HR_SNAPSHOT}"
    if os.path.exists(p):
        return archive_if_exists(p, "INVALIDATED")
    return None


def op_resolve_gloss(kp_dir: str, *, rank: int, gloss: str, by: str, kind: str = KIND_KP) -> dict:
    """候補段階のgloss HR解消(既存ga.resolve_glossを再利用)。PENDING_REVIEWの間だけ可。候補sha更新→reviewの候補shaも更新。
    以後の宣言は失効する(last_human_op_at)。HR解消後、その候補は選択可能(AUTO対象になりうる)。"""
    import er003_key_words_gloss_alignment as ga
    with review_lock(kp_dir, kind, by):
        review, cands = load_review(kp_dir, kind), load_candidates(kp_dir, kind)
        if review is None or cands is None:
            raise KpReviewError("候補/reviewがありません")
        _cc().guard(kp_dir, "resolve-gloss")   # M-4
        if review["status"] != ST_PENDING:
            raise KpReviewError(f"resolve-glossはPENDING_REVIEWの間だけ使えます(現在{review['status']})")
        c = next((x for x in cands["candidates"] if x["ai_rank"] == rank), None)
        if c is None:
            raise KpReviewError(f"番号{rank}の候補がありません")
        tmp = f"{kp_dir}/.resolve_gloss_tmp.json"
        doc = {"items": [json.loads(json.dumps(c["item"]))]}
        doc["items"][0]["rank"] = rank
        _write_json_atomic(tmp, doc)
        try:
            ga.resolve_gloss(tmp, rank, gloss, by)
            new_item = _read_json(tmp)["items"][0]
        finally:
            for pth in (tmp, f"{kp_dir}/GLOSS_ALIGNMENT_HUMAN_RESOLUTIONS_01.jsonl"):
                if pth == tmp and os.path.exists(pth):
                    os.remove(pth)
        new_item["rank"] = c["item"].get("rank", rank)
        c["item"] = new_item
        c["japanese_gloss"] = new_item.get("japanese_gloss")
        c["flags"]["gloss_hr_pending"] = False
        c["gates"]["gloss"] = "HUMAN_RESOLVED"
        c["auto_eligible"] = bool(not c["flags"].get("qa_fail") and not c["flags"].get("similar_to_ng"))
        if c.get("rescue"):      # 救済候補(canonicalization段)はgloss再整合/QA再判定が未達ならgloss解決後もauto不可のまま(戻さない)
            import er125_kp_rescue_production_01 as _er125
            c["auto_eligible"] = bool(c["auto_eligible"] and _er125.rescue_auto_ok(c["rescue"]))
        cands = save_candidates(kp_dir, cands, kind)
        review["candidates_sha256"] = cands["candidates_sha256"]
        review["last_human_op_at"] = _now()
        _event(review, "resolve_gloss", by, {"rank": rank})
        save_review(kp_dir, review, expected_revision=review["revision"], kind=kind)
        invalidate_gloss_snapshot(kp_dir)
        return c


# ============================================================
# 候補ファイルの保存(runner/生成側が呼ぶ)
# ============================================================
def archive_if_exists(path: str, tag: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    base, ext = os.path.splitext(path)
    n = 1
    while os.path.exists(f"{base}.{tag}_{n}{ext}"):
        n += 1
    dst = f"{base}.{tag}_{n}{ext}"
    os.replace(path, dst)
    return dst


def save_candidates(kp_dir: str, doc: dict, kind: str = KIND_KP) -> dict:
    doc = dict(doc)
    doc["schema"] = SCHEMA_CANDIDATES
    doc["kind"] = kind
    doc["candidates_sha256"] = candidates_sha256(doc)
    pth = paths(kp_dir, kind)
    _write_json_atomic(pth["candidates"], doc)
    rd = f"{pth['rounds']}/round_{doc.get('round', 1)}"
    _write_json_atomic(f"{rd}/{FILE_PREFIX[kind]}_candidates.json", doc)
    return doc


def retire_final_outputs(kp_dir: str, tag: str) -> list:
    """本文変更(STALE)/再選定時: 旧確定物をSUPERSEDEDへ退避し、後段が旧KPを読めないようにする(M-1の不変条件)。"""
    out = []
    pth = paths(kp_dir)
    for key in ("kp", "vocab", "final"):
        d = archive_if_exists(pth[key], tag)
        if d:
            out.append(d)
    return out


# ============================================================
# finalize(M-8: 確定集合へのRedundancy QA再適用。M-1: 本名ファイルを書けるのはここだけ)
# ============================================================
def _final_items(cands: dict, ids: list) -> list:
    cm = _cand_map(cands)
    items = []
    for n, cid in enumerate(sorted(ids, key=lambda i: cm[i]["ai_rank"]), start=1):
        c = cm[cid]
        it = json.loads(json.dumps(c["item"]))
        it["rank"] = n
        it["candidate_id"] = cid
        it["ai_rank"] = c["ai_rank"]
        items.append(it)
    return items


def _qa_key(sel: dict) -> str:
    return jsha({k: sorted(v) for k, v in sel.items()})


def _run_final_qa(cands: dict, selection: dict, level: str, redundancy_fn: Optional[Callable], std_part1: bool = False) -> dict:
    """確定KP集合(Advはvocab集合も)に対するRedundancy QA。returns {"status","ng_pairs":[(candidate_id_a, candidate_id_b)], "results":{...}}。"""
    res = {"status": "REDUNDANCY_PASS", "ng_pairs": [], "results": {}, "key": _qa_key(selection)}
    sets = [("kp", sel_ids(selection, "kp"))]
    if vocab_enabled(level, {"std_part1": std_part1}) and set(sel_ids(selection, "vocab")) != set(sel_ids(selection, "kp")):
        sets.append(("vocab", sel_ids(selection, "vocab")))
    cm = _cand_map(cands)
    for name, ids in sets:
        if len(ids) < 2:
            res["results"][name] = {"status": "REDUNDANCY_PASS", "skipped": "ペアが無い(2件未満)"}
            continue
        if redundancy_fn is None:
            raise KpReviewError("finalizeにはRedundancy QA関数(redundancy_fn)が必要です(確定集合へのQA再適用=M-8。省略しません)")
        items = _final_items(cands, ids)
        r = redundancy_fn(items, name)
        st = r.get("status")
        res["results"][name] = {"status": st, "duplicate_pairs": r.get("duplicate_pairs") or [], "model_id": r.get("model_id")}
        if st == "REDUNDANCY_NG":
            res["status"] = "REDUNDANCY_NG"
            rank_to_cid = {it["rank"]: it["candidate_id"] for it in items}
            for p in r.get("duplicate_pairs") or []:
                a, b = rank_to_cid.get(p.get("rank_a")), rank_to_cid.get(p.get("rank_b"))
                if a and b:
                    res["ng_pairs"].append((a, b))
        elif st != "REDUNDANCY_PASS":
            raise KpReviewError(f"確定集合のRedundancy QAが判定不能です(status={st}, set={name})。これは『重複』の判定結果ではなく判定器(Redundancy QA)の故障です。"
                                "fail-closedで停止します(選定は保持されます。制作コマンドを同じまま再実行すると判定だけを再試行します)")
    return res


def redundancy_telemetry(review: dict) -> dict:
    """finalizeごとのrun監査(0件でも記録): final_qa status / アラーム件数(候補QA由来+確定集合QA由来) / nonblocking。到達後続stageはrunner側(kp_stage_reached)が追記する。"""
    fq = review.get("final_qa") or {}
    n_final = len(fq.get("alarm_pairs") or [])
    n_cand = len(review.get("redundancy_alarms") or [])
    return {"final_qa_status": fq.get("status"), "final_qa_alarm_pairs": n_final, "candidate_qa_alarm_pairs": n_cand,
            "alarm_count": n_final + n_cand, "nonblocking": True, "review_status": review.get("status"), "filter_version": PRESENTABLE_FILTER_VERSION}


ALARM_SCHEMA = "kp_redundancy_alarm_v1"


def write_alarm_file_safe(kp_dir: str, review: dict, level: str, *, reached: Optional[str] = None) -> Optional[str]:
    """重複アラームの派生ファイル `<kp_dir>/redundancy_alarm.json`(0件でも書く=run監査)。正本は kp_selection_final.json.final_redundancy_qa / review.history。
    書込失敗はwarningログのみ(確定・制作を失敗させない。er078 write_listening_list_safeと同じ思想)。reached=到達した後続stage(runnerが追記)。"""
    try:
        p = paths(kp_dir)["alarm"]
        prev = _read_json(p) if os.path.exists(p) else None
        tel = redundancy_telemetry(review)
        if reached:
            tel["reached_next_stage"] = reached
        elif prev and (prev.get("telemetry") or {}).get("reached_next_stage") and prev.get("selection_signature") == review.get("selection_signature"):
            tel["reached_next_stage"] = prev["telemetry"]["reached_next_stage"]
        fq = review.get("final_qa") or {}
        doc = {"schema": ALARM_SCHEMA, "level": level, "selection_signature": review.get("selection_signature"),
               "blocking": False, "candidate_qa_alarms": list(review.get("redundancy_alarms") or []),
               "final_set_alarms": list(fq.get("alarm_pairs") or []), "telemetry": tel}
        if prev and {k: v for k, v in prev.items() if k != "checked_at"} == doc:
            return p
        doc["checked_at"] = _now()
        _write_json_atomic(p, doc)
        return p
    except Exception as e:   # noqa: BLE001  派生ファイル。確定を止めない
        _log.warning("redundancy_alarm.json write failed (non-blocking): %s: %s", type(e).__name__, e)
        return None



# ---- D8(ユーザー原文§3「アラームを表示・記録」): 重複アラームの表示。正本=redundancy_alarm.json / nuance_redundancy_alarm.json(読取のみ・API 0・非停止)
ALARM_LEVEL_LABEL = {"a2": "Standard", "b1b": "Advanced"}
NUANCE_ALARM_FILENAME = "nuance_redundancy_alarm.json"


def _alarm_kp_candidates(run_dir: str, level: str) -> list:
    return [f"{run_dir}/{level}/key_phrases/redundancy_alarm.json", f"{run_dir}/key_phrases/{level}/redundancy_alarm.json"]     # X / Y,Z の配置


def _alarm_nuance_candidates(run_dir: str, level: str) -> list:
    sds = [f"{run_dir}/{level}/study_text"] + ([f"{run_dir}/study_text"] if level == "b1b" else [])     # X / Y,Z(Advは<run>/study_text)
    return [f"{d}/{NUANCE_ALARM_FILENAME}" for d in sds]


def _alarm_read(paths_: list) -> Optional[dict]:
    for p in paths_:
        try:
            if os.path.exists(p):
                d = _read_json(p)
                if isinstance(d, dict):
                    return d
        except Exception:   # noqa: BLE001  壊れた/読めない派生ファイルは表示を欠くだけ(非停止)
            continue
    return None


def _alarm_pair_key(a: dict) -> tuple:
    return tuple(sorted((str(a.get("used_form_a") or a.get("candidate_id_a")), str(a.get("used_form_b") or a.get("candidate_id_b")))))


def collect_redundancy_alarms(run_dir: str, level: str) -> Optional[dict]:
    """level単位の重複アラーム一覧。記録ファイルが1つも無い(旧run・未確定)=None。pairs=KP/Word/追加解説/本文意味(候補QA+確定集合QA、同一ペアは1件)、nuance=ニュアンス解説。"""
    kp = _alarm_read(_alarm_kp_candidates(run_dir, level))
    nz = _alarm_read(_alarm_nuance_candidates(run_dir, level))
    if kp is None and nz is None:
        return None
    pairs, seen = [], set()
    for a in list((kp or {}).get("candidate_qa_alarms") or []) + list((kp or {}).get("final_set_alarms") or []):
        k = _alarm_pair_key(a)
        if k in seen:
            continue
        seen.add(k)
        pairs.append(a)
    return {"level": level, "kp_recorded": kp is not None, "pairs": pairs, "nuance_recorded": nz is not None,
            "nuance": list((nz or {}).get("alarms") or [])}


def render_redundancy_alarms(run_dir: str, level: str) -> tuple:
    """(text, html)。記録ファイル欠落=("","")(旧run・非停止)。0件でも『重複アラーム 0件』を返す。表示のみ(確定・TTS・組立を止めない)。"""
    try:
        c = collect_redundancy_alarms(run_dir, level)
    except Exception:   # noqa: BLE001
        return "", ""
    if c is None:
        return "", ""
    label = ALARM_LEVEL_LABEL.get(level, level)
    n = len(c["pairs"]) + len(c["nuance"])
    lines, items = [f"{label}: 重複アラーム {n}件"], []
    for a in c["pairs"]:
        sa, sb = a.get("slot_label_a") or "", a.get("slot_label_b") or ""
        asp = a.get("aspects") or {}
        asp_s = " / ".join(f"{k}={v}" for k, v in asp.items() if v)
        why = a.get("reasoning") or "(理由の記録なし)"
        lines.append(f"  - {a.get('used_form_a')}({sa}) x {a.get('used_form_b')}({sb}) 理由: {why}" + (f" [観点: {asp_s}]" if asp_s else ""))
        items.append(f"<li><b>{_html.escape(str(a.get('used_form_a')))}</b>({_html.escape(sa)}) × <b>{_html.escape(str(a.get('used_form_b')))}</b>({_html.escape(sb)})"
                     f"<br>理由: {_html.escape(str(why))}" + (f"<br>観点: {_html.escape(asp_s)}" if asp_s else "") + "</li>")
    for a in c["nuance"]:
        it = a.get("item") or a.get("item_id")
        note = a.get("note") or ""
        lines.append(f"  - ニュアンス解説 x {it} 理由: {note}")
        items.append(f"<li>ニュアンス解説 × <b>{_html.escape(str(it))}</b><br>理由: {_html.escape(str(note))}</li>")
    html_ = f"<h3>{_html.escape(label)}: {n}件</h3>" + (f"<ul>{''.join(items)}</ul>" if items else "<p>重複アラーム 0件</p>")
    return "\n".join(lines), html_


def render_redundancy_alarms_all(run_dir: str, levels: tuple = ("a2", "b1b")) -> tuple:
    """全levelの(text, html)。html=ページ補助情報(本文領域外・全level節の後ろ)に置く事後確認節。全level記録なし=("","")=従来ページとバイト同一。"""
    parts = [(lv, render_redundancy_alarms(run_dir, lv)) for lv in levels]
    parts = [(lv, t, h) for lv, (t, h) in parts if h]
    if not parts:
        return "", ""
    text = "[重複アラーム(選定後の重複。表示・記録のみ。確定/音声/組立は止めません)]\n" + "\n".join(t for _lv, t, _h in parts)
    html_ = ("<section id='post-check'><h2>事後確認(重複アラーム)</h2>"
             "<p>選定したKey Phrase等とニュアンス解説の間に、意味・用法の重なりがある可能性をAIが検知しました。"
             "表示と記録のみで、選定は維持されます(重複の可否は事後に判断してください)。</p>" + "".join(h for _lv, _t, h in parts) + "</section>")
    return text, html_


def finalize_kp(kp_dir: str, *, level: str, redundancy_fn: Optional[Callable] = None, ng_scope: Optional[dict] = None) -> dict:
    """review(REVIEWED/UNREVIEWED_AUTO_ADOPTED)から確定物を書く。idempotent: 署名が同じなら本名ファイルは書き直さない
    (後段のgloss修復・SRC D1・resolve_glossの編集を壊さない)。returns {"review","items","vocab_items","signature","wrote"}。
    仕様②(2026-10-29): Humanの確定が確定集合のRedundancy QAでNGでも差し戻さない(REDUNDANCY_ALARMとして記録し続行)。判定不能のみKpReviewError(fail-closed)。"""
    pth = paths(kp_dir)
    with review_lock(kp_dir, KIND_KP, "finalize"):
        review, cands = load_review(kp_dir), load_candidates(kp_dir)
        if review is None or cands is None:
            raise KpReviewError("finalize: 候補/reviewがありません")
        if review["status"] not in FORWARD_STATUSES:
            raise KpReviewError(f"finalize: status={review['status']}は確定できません(REVIEWED/UNREVIEWED_AUTO_ADOPTEDのみ)")
        if review["candidates_sha256"] != cands["candidates_sha256"]:
            raise KpReviewInconsistent("finalize: reviewと候補のcandidates_sha256が不一致(手編集の疑い)。fail-closed")
        ak = review.get("article_key") or {}
        ng_ent = ng_entries_of(review, ak.get("family"), ak.get("slug"), level)
        sel = review.get("selection") or {}
        _sp1 = bool(review.get("std_part1"))
        errs = validate_selection(cands, sel, level=level, accepted_qa_fail=review.get("accepted_qa_fail"), ng_entries=ng_ent, std_part1=_sp1)
        if errs:
            raise KpReviewInconsistent("finalize: 選択が再検証に失敗しました:\n- " + "\n- ".join(errs))
        # M-8
        fq = review.get("final_qa")
        dirty = review.get("selection_signature") is None
        # キャッシュ(Opus M5): key一致 かつ (PASS または (ALARM かつ AUTOでない))。ALARMは人間選定の確定でのみ保存する形のため、AUTOでは有効としない。
        # ALARM確定後のresume/_try_refinalize(redundancy_fn=None)は有料API 0回で通る。REBOUND時はkeyが選定IDのみ(candidates_shaを含まない)=既存挙動のまま。
        _cache_ok = bool(fq) and fq.get("key") == _qa_key(sel) and (
            fq.get("status") == "REDUNDANCY_PASS" or (fq.get("status") == "REDUNDANCY_ALARM" and review["status"] != ST_AUTO))
        if not _cache_ok:
            dirty = True
            if review["status"] == ST_AUTO:
                excluded = list((review.get("auto_qa_excluded") or []))
                for _ in range(AUTO_QA_ADVANCE_MAX + 1):
                    fq = _run_final_qa(cands, sel, level, redundancy_fn, _sp1)
                    if fq["status"] == "REDUNDANCY_PASS":
                        break
                    # AUTO: 重複ペアの下位(ai_rankが大きい方)を除外して次候補へ繰り上げ、再判定
                    cm = _cand_map(cands)
                    drop = [max(p, key=lambda i: cm[i]["ai_rank"]) for p in fq["ng_pairs"][:1]]
                    excluded += drop
                    review["auto_qa_excluded"] = excluded
                    _event(review, "auto_advance_final_redundancy_ng", "runner", {"excluded": drop})
                    sel = auto_select(cands, level=level, ng_entries=ng_ent, excluded_ids=excluded, std_part1=_sp1)
                    if not sel_ids(sel, "kp"):
                        raise KpReviewError("AUTO: 確定集合のRedundancy QAで採用可能な候補が尽きました(STOP)")
                else:
                    raise KpReviewError(f"AUTO: 確定集合のRedundancy QAが{AUTO_QA_ADVANCE_MAX}回の繰り上げでも解消しません(STOP)")
                review["selection"] = sel
                review["final_qa"] = fq
            else:
                fq = _run_final_qa(cands, sel, level, redundancy_fn, _sp1)
                if fq["status"] != "REDUNDANCY_PASS":
                    # 仕様②(2026-10-29): 人間選定の確定集合が重複NGでも差し戻さない(PENDINGへ戻さない・選定を消さない・確定レコードを変えない)。
                    # アラームとして記録し確定を続行する。判定不能(INVALID等)は_run_final_qaがKpReviewError(fail-closed)=重複ではなく判定器の故障。
                    fq = final_qa_to_alarm(fq, cands)
                    _event(review, "final_redundancy_alarm", "runner", {"pairs": [[p.get("candidate_id_a"), p.get("candidate_id_b")] for p in fq["alarm_pairs"]],
                                                                      "blocking": False})
                review["final_qa"] = fq
        if dirty:
            review = save_review(kp_dir, review, expected_revision=review["revision"])
        sig = review["selection_signature"]
        kp_ids, vocab_ids = sel_ids(review["selection"], "kp"), sel_ids(review["selection"], "vocab")
        items = _final_items(cands, kp_ids)
        vocab_items = _final_items(cands, vocab_ids) if vocab_enabled(level, review) else []
        for it in items + vocab_items:
            if it["candidate_id"] in set(review.get("accepted_qa_fail") or []):
                it["human_accepted_qa_fail"] = True
        # G0(確定内容保護): 成果物を(再)書込みする場合だけ、書く前に確定レコードを作成/照合する。既にfinalize済みのidempotent再実行でレコードが無ければ
        # 旧run扱い(遅延生成しない。M-7)。
        _need = False
        for _p, _k, _adv_only in ((pth["kp"], "kp_selection_signature", False), (pth["vocab"], "kp_selection_signature", True), (pth["final"], "selection_signature", False)):
            if _adv_only and not vocab_enabled(level, review):
                continue
            _d = _read_json(_p) if os.path.exists(_p) else None
            _need = _need or _d is None or _d.get(_k) != sig
        _cc().on_finalize_pre_write(kp_dir, review, cands, level, fresh=_need)
        wrote = []
        cur = _read_json(pth["kp"]) if os.path.exists(pth["kp"]) else None
        if cur is None or cur.get("kp_selection_signature") != sig:
            overall = "PASS" if not any(it.get("human_accepted_qa_fail") for it in items) else "REVIEW_REQUIRED_HUMAN_ACCEPTED"
            _write_json_atomic(pth["kp"], {"items": items, "overall_status": overall, "kp_selection_signature": sig,
                                           "kp_review_status": review["status"]})
            wrote.append("keywords_canonicalized.json")
        if vocab_enabled(level, review):   # vocab_confirmed.jsonを書くのはfinalize_kpだけ(単一writer。両level共通。旧a2のvocab退避renameは撤去)
            curv = _read_json(pth["vocab"]) if os.path.exists(pth["vocab"]) else None
            if curv is None or curv.get("kp_selection_signature") != sig:
                _write_json_atomic(pth["vocab"], {"items": vocab_items, "kp_selection_signature": sig, "kp_review_status": review["status"]})
                wrote.append("vocab_confirmed.json")
        final = {"schema": SCHEMA_FINAL, "level": level, "review_status": review["status"], "selection_signature": sig,
                 "text_sha256": review["text_sha256"], "candidates_sha256": review["candidates_sha256"],
                 "round": review.get("round", 1), "selection": review["selection"],
                 "ng_candidate_ids": sorted(e["candidate_id"] for e in ng_ent), "final_redundancy_qa": review.get("final_qa"),
                 "redundancy_alarms": review.get("redundancy_alarms") or [],
                 "redundancy_telemetry": redundancy_telemetry(review),
                 "mode_used": review.get("mode_used"), "finalized_at": _now()}
        curf = _read_json(pth["final"]) if os.path.exists(pth["final"]) else None
        if curf is None or curf.get("selection_signature") != sig:
            _write_json_atomic(pth["final"], final)
            wrote.append("kp_selection_final.json")
        _cc().on_finalize_post_write(kp_dir, level)   # G0: 書いた成果物が確定レコードと一致すること
        write_alarm_file_safe(kp_dir, review, level)
        return {"review": review, "items": items, "vocab_items": vocab_items, "signature": sig, "wrote": wrote}


# ============================================================
# 消費側の検査(全消費者の入口)
# ============================================================
def has_review(kp_dir: str) -> bool:
    p = paths(kp_dir)
    return os.path.exists(p["review"]) or os.path.exists(p["candidates"])


def _consumer_checks(items: list, *, require_src_contract: bool) -> list:
    """M-9: vocab itemにも既存の消費側検査を適用する(collect_unresolved / select_consumer_unevaluated / Z SRC has_contract)。"""
    problems = []
    import er003_key_words_gloss_alignment as ga
    unres = ga.collect_unresolved({"items": items})
    if unres:
        problems.append(f"gloss HR待ちitemが残っています(rank={[x.get('rank') for x in unres]})")
    uneval = ga.select_consumer_unevaluated(items) if ga.flag_enabled() else ga.select_fulltext_gloss_missing(items)
    if uneval:
        problems.append(f"gloss未評価/未生成itemがあります(rank={[x.get('rank') for x in uneval]})")
    if require_src_contract:
        import er026_family_z_src_posthoc_01 as srcz
        if not srcz.has_contract({"items": items}):
            problems.append("Z SRC D1(source_reference_contract)が未適用のitemがあります")
    return problems


def require_final_consistent(kp_dir: str, *, level: Optional[str] = None, require_src_contract: bool = False,
                             assets_json: Optional[str] = None) -> Optional[dict]:
    """全消費者の入口で呼ぶ(DESIGN c-2)。review/候補が無い旧run=None(旧run互換)。reviewがあるのに不整合ならKpReviewInconsistent(次コマンド付き)。
    (i)statusが前進可 (ii)selection_signature再計算が一致 (iii)keywords_canonicalized.jsonのcandidate_id集合=selection.kp (iv)vocab_confirmed.json=selection.vocab(Adv)
    (v)NG交差0 (vi)vocab itemにも消費側検査(M-9)。
    (vii)G1(確定内容保護): 確定レコードと(候補doc・review・成果物・assets copy[assets_json=Y/Z])の保護フィールド一致(er128.verify_g1)。"""
    pth = paths(kp_dir)
    if not has_review(kp_dir):
        return None
    nxt = "(次の一手: 制作コマンドを再実行して確定させる/ er119_kp_human_review_cli_01.py status --run <run>)"
    review, cands = load_review(kp_dir), load_candidates(kp_dir)
    if review is None or cands is None:
        raise KpReviewInconsistent(f"KP_REVIEW_INCONSISTENT: review/候補ファイルのどちらかが欠落しています{nxt}")
    if review["status"] not in FORWARD_STATUSES:
        raise KpReviewNotConfirmed(f"KP_REVIEW_NOT_CONFIRMED: status={review['status']}。Human確認(select)か明示の不在宣言が必要です{nxt}")
    lv = level or review["level"]
    if selection_signature(review) != review.get("selection_signature"):
        raise KpReviewInconsistent(f"KP_REVIEW_SIGNATURE_MISMATCH: kp_human_review.jsonの署名が不一致(手編集の疑い){nxt}")
    if review["candidates_sha256"] != cands["candidates_sha256"] or candidates_sha256(cands) != cands["candidates_sha256"]:
        raise KpReviewInconsistent(f"KP_CANDIDATES_SIGNATURE_MISMATCH: 候補ファイルが改変されています{nxt}")
    _ven = vocab_enabled(lv, review)
    for p in (pth["final"], pth["kp"]) + ((pth["vocab"],) if _ven else ()):
        if not os.path.exists(p):
            raise KpReviewInconsistent(f"KP_FINAL_MISSING: {p}がありません(確定前、または退避済み){nxt}")
    final = _read_json(pth["final"])
    if final.get("selection_signature") != review["selection_signature"]:
        raise KpReviewInconsistent(f"KP_FINAL_SIGNATURE_MISMATCH: kp_selection_final.jsonがreviewと不一致{nxt}")
    kp_doc = _read_json(pth["kp"])
    sel = review["selection"]
    if sorted(it.get("candidate_id") for it in kp_doc.get("items") or []) != sorted(sel_ids(sel, "kp")):
        raise KpReviewInconsistent(f"KP_SELECTION_MISMATCH: keywords_canonicalized.jsonの候補がreview.selection.kpと一致しません(旧KPの混入の疑い){nxt}")
    if _ven:
        vdoc = _read_json(pth["vocab"])
        if sorted(it.get("candidate_id") for it in vdoc.get("items") or []) != sorted(sel_ids(sel, "vocab")):
            raise KpReviewInconsistent(f"KP_VOCAB_MISMATCH: vocab_confirmed.jsonがreview.selection.vocabと一致しません{nxt}")
        problems = _consumer_checks(vdoc.get("items") or [], require_src_contract=require_src_contract)
        if problems:
            raise KpReviewInconsistent("KP_VOCAB_CONSUMER_CHECK_FAILED: " + " / ".join(problems))
    ak = review.get("article_key") or {}
    ng_ids = {e["candidate_id"] for e in ng_entries_of(review, ak.get("family"), ak.get("slug"), lv)}
    used = set(sel_ids(sel, "kp")) | set(sel_ids(sel, "vocab"))
    if used & ng_ids:
        raise KpReviewInconsistent(f"KP_NG_INTERSECTION: NG候補が確定集合に含まれています({sorted(used & ng_ids)})")
    _cc().verify_g1(kp_dir, lv, review, cands, assets_json=assets_json)
    return review


def part1_items(kp_dir: str) -> list:
    """Part 1(単語解説)の入力の単一アクセサ(M-9)。reviewが存在するならvocab_confirmed.jsonが必須(fail-closed、
    3件へ黙って戻らない)。reviewが無い旧runだけ keywords_canonicalized.json(従来)。KPと同じcandidateのitemは
    後段修復(gloss/SRC)後のKP artifactを正としてoverlayする(rankはvocab側の連番を保つ)。KP側rankで他ファイルと結合しない。"""
    pth = paths(kp_dir)
    if not has_review(kp_dir):
        if not os.path.exists(pth["kp"]):
            raise KpReviewError(f"[STOP][Part 1] {pth['kp']}がありません(KP stage未完了)")
        items = _read_json(pth["kp"]).get("items") or []
        if not items:
            raise KpReviewError(f"[STOP][Part 1] {pth['kp']}のitemsが空です")
        return sorted(items, key=lambda x: x["rank"])
    if not os.path.exists(pth["vocab"]):
        raise KpReviewError(f"[STOP][Part 1] {pth['vocab']}がありません。KP Human Reviewが未確定、または生成漏れです(旧KP3件へは戻しません)")
    vdoc = _read_json(pth["vocab"])
    vitems = sorted(vdoc.get("items") or [], key=lambda x: x["rank"])
    if not vitems:
        raise KpReviewError(f"[STOP][Part 1] {pth['vocab']}のitemsが空です")
    kp_by_cid = {}
    if os.path.exists(pth["kp"]):
        kp_by_cid = {it.get("candidate_id"): it for it in _read_json(pth["kp"]).get("items") or []}
    out = []
    for n, v in enumerate(vitems, start=1):
        base = kp_by_cid.get(v.get("candidate_id"))
        it = json.loads(json.dumps(base if base is not None else v))
        it["rank"] = n   # vocab側の連番(KP側rankは使わない)
        it["candidate_id"] = v.get("candidate_id")
        out.append(it)
    _cc().verify_items_against_record(kp_dir, out, which="part1")   # 確定内容保護(02B 単一アクセサ): ユーザー確定レコードの英語/日本語訳と一致する項目だけ返す
    return out


def verify_selection_matches_outputs(kp_dir: str, *, level: str, tts_results_path: Optional[str] = None,
                                     study_text_json: Optional[str] = None, page_paths: Optional[list] = None,
                                     vocab_page_paths: Optional[list] = None, require_src_contract: bool = False,
                                     gloss_page_paths: Optional[list] = None) -> dict:
    """検証5(DESIGN d): 選定結果=実際に音声化・公開された内容。決定論・API 0。不一致=KpReviewInconsistent。
    確定JSON(review/kp_selection_final) <-> keywords_canonicalized.json <-> TTS結果のkp英語text <-> study_text(Part 1の行) <-> 公開ページHTML。
    reviewが無い旧runは対象外(report={"legacy": True})。"""
    import html as _html
    review = require_final_consistent(kp_dir, level=level, require_src_contract=require_src_contract)
    if review is None:
        return {"legacy": True, "ok": True}
    pth = paths(kp_dir)
    kp_items = sorted(_read_json(pth["kp"]).get("items") or [], key=lambda x: x["rank"])
    problems = []
    if tts_results_path:
        if not os.path.exists(tts_results_path):
            problems.append(f"TTS結果がありません: {tts_results_path}")
        else:
            kps = _read_json(tts_results_path).get("key_phrases") or {}
            want = [it["used_form"] for it in kp_items]
            def _en_text(rank):   # Master Store再利用のrecordは`text`を持たず、runnerが記録する`canonical_text`(再利用時にexpected_text一致を検査済み)が同じ内容を指す
                en = (kps.get(str(rank)) or {}).get("english") or {}
                return en.get("text") if en.get("text") is not None else en.get("canonical_text")
            got = [_en_text(it["rank"]) for it in kp_items]
            if len(kps) != len(kp_items):
                problems.append(f"TTSのKP件数({len(kps)})が確定KP({len(kp_items)})と一致しません")
            if [_kp_text_norm(x) for x in got] != [_kp_text_norm(x) for x in want]:   # ハイフン/空白/大小文字差は同一視(TTS側が`-`→空白に置換したtextを記録するため。語・順序の差は従来どおり不一致)
                problems.append(f"TTSのKP英語text {got} が確定KP {want} と一致しません")
    vocab_items = []
    if vocab_enabled(level, review):
        vocab_items = part1_items(kp_dir)
        if study_text_json:
            if not os.path.exists(study_text_json):
                problems.append(f"study_text(Part 1)がありません: {study_text_json}")
            else:
                rows = _read_json(study_text_json).get("rows") or []
                want_v = [it["used_form"] for it in vocab_items]
                got_v = [r.get("english_expression") for r in rows]
                if got_v != want_v:
                    problems.append(f"Part 1の英語表現 {got_v} が確定vocab {want_v} と一致しません")
    def _page_text(pg):
        with open(pg, encoding="utf-8") as f:
            return _html.unescape(f.read())
    for pg in page_paths or []:   # KPを表示するページ
        if not os.path.exists(pg):
            problems.append(f"公開ページがありません: {pg}")
            continue
        hv = _page_text(pg)
        for it in kp_items:
            if it["used_form"] not in hv:
                problems.append(f"{os.path.basename(pg)}にKP「{it['used_form']}」がありません")
    for pg in vocab_page_paths or []:   # Part 1(単語解説)を表示するページ(訳欄の判断記録が無い間はページに描画されないので、呼出側が渡すかを決める)
        if not os.path.exists(pg):
            problems.append(f"公開ページがありません: {pg}")
            continue
        hv = _page_text(pg)
        for it in vocab_items:
            if it["used_form"] not in hv:
                problems.append(f"{os.path.basename(pg)}にPart 1の表現「{it['used_form']}」がありません")
    if problems:
        raise KpReviewInconsistent("KP_SELECTION_OUTPUT_MISMATCH: " + " / ".join(problems))
    # 確定内容保護 G2(TTS record)・G3(ページHTML/Part 1行)。AND追加・fail-closed(違反=INTEGRITY)。gloss_page_paths=Std日本語訳の表示ページ(省略時はpage_paths)
    _cc().verify_outputs(kp_dir, level, tts_results_path=tts_results_path, study_text_json=study_text_json, page_paths=page_paths,
                         vocab_page_paths=vocab_page_paths, gloss_page_paths=gloss_page_paths)
    return {"legacy": False, "ok": True, "signature": review["selection_signature"], "kp": [it["used_form"] for it in kp_items],
            "vocab": [it["used_form"] for it in vocab_items]}


# ============================================================
# 提示(kp_human_review_request.md)
# ============================================================
def cli_prefix() -> str:
    return "py er119_kp_human_review_cli_01.py"


def _backfill_summary_line(cands: dict) -> str:
    """KP-GATE-DROP-BACKFILL: 補完の発動結果をHR依頼書へ1行で示す(未発動/無効=空文字=従来の依頼書と同一)。"""
    b = cands.get("backfill") or {}
    if not b.get("triggered"):
        return ""
    e = b.get("E") or {}
    added = len(b.get("added") or [])
    st = b.get("status")
    msg = f"- Gate除外 {e.get('total')}件(フレーズ{e.get('phrase')}・単語{e.get('word')})に対し、補完候補 {added}件を末尾に追加しました(補完status: {st})"
    if st != "OK":
        msg += f"。補完は失敗しました({b.get('failure')})。初回候補のみで続行しています"
    elif added < (e.get("total") or 0):
        msg += "。適切な補完候補が不足したため上限未達です(数合わせはしません)"
    return msg


def render_request_md(cands: dict, review: dict, *, run_hint: str, ng_entries: Optional[list] = None) -> str:
    level = cands["level"]
    ng_entries = ng_entries or []
    _ven = vocab_enabled(level, review)
    rec = auto_select(cands, level=level, ng_entries=ng_entries, std_part1=bool(review.get("std_part1")))
    top_kp = {cid for cid in sel_ids(rec, "kp")}
    top_vocab = {cid for cid in sel_ids(rec, "vocab")}
    lines = [f"# KP Human Review 依頼({level}) round {cands.get('round', 1)}", "",
             f"- 状態: {review.get('status')} / candidates_sha256: `{cands['candidates_sha256'][:16]}` / 本文sha: `{cands['text_sha256'][:12]}`",
             "- あなたの作業: KPに使う最大3件" + ("と、単語解説に使う最大5件(KP3件を含む)" if _ven else "") + "を選びます。",
             "- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。", "",
             "| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |", "|---|---|---|---|---|---|---|"]
    bfl = _backfill_summary_line(cands)
    if bfl:
        lines[5:5] = [bfl]      # 見出し直後(箇条書きの末尾)に補完の要約を1行(補完が発動した/失敗したときだけ。未発動は従来のまま)
    for c in sorted(presentable_candidates(cands), key=lambda x: x["ai_rank"]):      # 仕様①: 提示は品質検査を通った候補のみ(除外は下の節に事実を表示)
        cid = c["candidate_id"]
        mark = "KP" if cid in top_kp else ("単語" if cid in top_vocab else "")
        flags = []
        f = c.get("flags") or {}
        if f.get("redundant_with"):
            flags.append("重複(アラームのみ・選んでも止まりません): " + ",".join(str(next((x['ai_rank'] for x in cands['candidates'] if x['candidate_id'] == o), '?')) for o in f["redundant_with"]))
        m = match_ng(c, ng_entries)
        if m == "exact":
            flags.append("NG済み")
        elif m == "similar":
            flags.append("NG句に類似(AUTO対象外)")
        if c.get("origin") == "backfill":
            flags.append("補完候補(Gate除外の代替)")   # KP-GATE-DROP-BACKFILL: 初回候補の末尾に追加された補完分
        if c.get("rescue_note"):
            flags.append(c["rescue_note"])       # 救済(RESCUED)候補: 元の句・救済コード・QA再判定状態
        if (c.get("flags") or {}).get("idiom_exception"):
            flags.append("慣用句例外(" + str(c["flags"]["idiom_exception"]) + ")")
        if not c.get("auto_eligible"):
            flags.append("AUTO対象外")
        cell = lambda s: (s or "").replace("|", "/").replace("\n", " ")   # noqa: E731
        lines.append(f"| {c['ai_rank']} | {mark} | {cell(c.get('used_form'))} | {cell(c.get('japanese_gloss'))} | {cell(c.get('source_sentence'))} | {cell(c.get('reason_ja'))} | {' / '.join(flags)} |")
    d = cands.get("dropped") or []
    if d:
        lines += ["", "## Gateで除外された候補(参考)", ""]
        for x in d:
            lines.append(f"- {x.get('phrase')} : {x.get('stage')} : {' / '.join(x.get('reasons') or [])}")
    ex = excluded_from_presentation(cands)       # 旧doc(qa_fail旗付きで保存済み)をresumeした場合の提示除外。新docでは生成時にdroppedへ入るため通常0件
    if ex:
        lines += ["", "## 提示から除外した候補(品質検査で不適合。選択肢には出していません)", ""]
        for x in ex:
            lines.append(f"- 番号{x['ai_rank']} {x['used_form']} : {' / '.join(x['reasons'])}")
    p = cli_prefix()
    lines += ["", "## 操作(コマンド)", "",
              f"- 状況確認: `{p} status --run {run_hint}`",
              f"- AI推奨を了承: `{p} select --run {run_hint} --level {level} --accept-ai --candidates-sha {cands['candidates_sha256']} --by <名前>`",
              f"- 選択: `{p} select --run {run_hint} --level {level} --kp 1,2,3" + (" --vocab 1,2,3,4,5" if _ven else "") + " [--ng 6:理由] --by <名前>`",
              f"- 選び直し(NG付き): `{p} reselect --run {run_hint} --level {level} --ng 4:理由 --by <名前>`(上限{RESELECT_MAX}回)",
              f"- 不在として進める(明示宣言。このrun・この候補round限り): `{p} declare-absent --runs {run_hint} --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`",
              "", "再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。"]
    return "\n".join(lines) + "\n"


# ============================================================
# 状態一覧(CLI status / 運用)
# ============================================================
def discover_kp_dirs(run_dir: str) -> list:
    """X: <run>/<level>/key_phrases / Z: <run>/key_phrases/<level>。review/候補ファイルのあるdirだけ返す。"""
    out = []
    for lv in ("a2", "b1b"):
        for d in (f"{run_dir}/{lv}/key_phrases", f"{run_dir}/key_phrases/{lv}"):
            if os.path.isdir(d) and has_review(d):
                out.append(d)
    return out


def status_of(kp_dir: str) -> dict:
    review, cands = load_review(kp_dir), load_candidates(kp_dir)
    if review is None:
        return {"kp_dir": kp_dir, "status": "NO_REVIEW" if cands is None else "NO_REVIEW_FILE"}
    return {"kp_dir": kp_dir, "level": review.get("level"), "status": review["status"], "round": review.get("round"),
            "reselect_count": review.get("reselect_count"), "candidates_sha256": review.get("candidates_sha256"),
            "selection": review.get("selection"), "accept_ai_default": review.get("accept_ai_default"),
            "mode_used": review.get("mode_used"), "revision": review.get("revision"),
            "published": published_diff(kp_dir)}


def pending_summary(kp_dir: str, level: str) -> dict:
    return {"level": level, "kp_dir": kp_dir, "request_md": paths(kp_dir)["request"], "status": (load_review(kp_dir) or {}).get("status")}


# ============================================================
# 確定フロー全体(runner共通。LLM呼出は注入関数のみ)
# ============================================================
def ensure_kp_review(kp_dir: str, *, run_dir: str, family: str, slug: str, level: str, text: str,
                     generate_fn: Callable, redundancy_fn: Optional[Callable], run_hint: Optional[str] = None) -> dict:
    """候補生成→(Human確認 or 明示宣言のAUTO)→finalize。
    returns {"state":"FINALIZED","final":{...}} / {"state":"PENDING","pending":{...}} / {"state":"FAILED","status":..,"detail":..}
    generate_fn(round_no, ng_entries) -> {"ok":True,"doc":cands_doc_without_sha} | {"ok":False,"status":"OUTER_RETRY_EXHAUSTED",...}。
    resume(候補sha一致)は再選定せずAPI 0。確定済みreviewは再選定しない(reselectのみ)。"""
    pth = paths(kp_dir)
    os.makedirs(kp_dir, exist_ok=True)
    text_sha = sha256_text(text)
    article_key = {"family": family, "slug": slug, "level": level}
    run_hint = run_hint or run_dir
    cands, review = load_candidates(kp_dir), load_review(kp_dir)
    if cands is not None:
        # R2: 保存済み候補は読み戻し優先(再計算しない)。救済の出所(辞書sha等)が現在値とずれていたらlogだけ残す(停止しない)
        try:
            import er125_kp_rescue_production_01 as _er125
            for d in _er125.provenance_drift(cands.get("rescue_provenance")):
                _log.warning("kp_rescue provenance drift (resume keeps saved candidates): %s", d)
        except Exception as e:   # noqa: BLE001  log専用
            _log.warning("kp_rescue provenance check skipped: %s", type(e).__name__)
    # 候補/reviewの整合(片方だけ・本文変更)
    if cands is not None and review is None:
        raise KpReviewInconsistent("候補ファイルだけがあり、reviewがありません(手動削除の疑い)。fail-closed。状況をFableへ報告してください")
    if cands is not None and cands.get("text_sha256") != text_sha and review is not None:
        # 確定内容保護(M-4/M-8): ユーザー確定済みの選定がある状態で本文が変わった場合は、有料の候補再生成・確定物の退避の前に分岐する。
        # 各確定itemの出典文が新本文に逐語で残る=API 0で候補doc/review署名/レコードを再バインド("REBOUND")、残らない=ISSUEで止める(退避・再生成しない)。
        _rb = _cc().stale_or_rebind(kp_dir, text, text_sha)
        if _rb == "REBOUND":
            cands, review = load_candidates(kp_dir), load_review(kp_dir)
        elif _rb:
            ng_ent0 = ng_entries_of(review, family, slug, level)
            _write_text_atomic(pth["request"], _cc().request_notice(kp_dir) + render_request_md(cands, review, run_hint=run_hint, ng_entries=ng_ent0))
            pend = pending_summary(kp_dir, level)
            pend["reason"] = "confirmed_content_issue"
            return {"state": "PENDING", "pending": pend, "generated": False}
    if cands is not None and cands.get("text_sha256") != text_sha:
        # 本文が変わった(Writer再生成): 旧候補/review/確定物をSUPERSEDEDへ退避しNGは保持して候補を再生成(STALE)
        tag = "SUPERSEDED"
        archive_if_exists(pth["candidates"], tag)
        old_rv = archive_if_exists(pth["review"], tag)
        retire_final_outputs(kp_dir, tag)
        prev = dict(review or {})
        prev["history"] = list(prev.get("history") or []) + [{"at": _now(), "event": "stale_text_changed", "by": "runner",
                                                              "detail": {"old": cands.get("text_sha256"), "new": text_sha}}]
        prev["reselect_count"] = 0
        cands, review = None, None
        carry = prev
    else:
        carry = None
    generated = False
    if cands is None or review is None or review["status"] == ST_RESELECT:
        prev_review = review or carry
        round_no = (review.get("round", 1) + 1) if (review and review["status"] == ST_RESELECT) else 1
        ng_entries = ng_entries_of(prev_review, family, slug, level)
        if review and review["status"] == ST_RESELECT:
            archive_if_exists(pth["candidates"], "SUPERSEDED")
            retire_final_outputs(kp_dir, "SUPERSEDED")
        gen = generate_fn(round_no, ng_entries)
        if not gen.get("ok"):
            return {"state": "FAILED", "status": gen.get("status", "OUTER_RETRY_EXHAUSTED"), "detail": gen}
        doc = dict(gen["doc"])
        doc["level"], doc["text_sha256"], doc["round"] = level, text_sha, round_no
        doc = save_candidates(kp_dir, doc)
        with review_lock(kp_dir, KIND_KP, "runner"):
            if review is not None:   # RESELECTION_REQUESTED -> 新round
                rv = new_review(doc, article_key=article_key, prev=review)
                rv["revision"] = review["revision"]
                rv = save_review(kp_dir, rv, expected_revision=review["revision"])
            else:
                rv = new_review(doc, article_key=article_key, prev=carry)
                rv = save_review(kp_dir, rv, expected_revision=None)
        cands, review, generated = doc, rv, True
    # PENDING: 明示宣言があればAUTO
    if review["status"] == ST_PENDING:
        decl = read_mode_declaration(run_dir, level=level, review=review, round_no=review.get("round", 1),
                                     cands_sha=review["candidates_sha256"])
        if decl is not None:
            ng_ent = ng_entries_of(review, family, slug, level)
            sel = auto_select(cands, level=level, ng_entries=ng_ent, std_part1=bool(review.get("std_part1")))
            if not sel_ids(sel, "kp"):
                raise KpReviewError("AUTO: 採用可能な候補が0件です(OUTER_RETRY_EXHAUSTED相当のSTOP)。Humanが選ぶか再生成が必要です")
            with review_lock(kp_dir, KIND_KP, "runner"):
                review = load_review(kp_dir)
                review.update(status=ST_AUTO, selection=sel, mode_used={"declaration_id": decl.get("declaration_id"),
                                                                       "declared_by": decl.get("declared_by"), "source": decl.get("source"),
                                                                       "reason": decl.get("reason"), "user_ref": decl.get("user_ref")},
                              verdicts={c["candidate_id"]: None for c in cands["candidates"]})
                _event(review, "auto_adopted", "runner", {"declaration_id": decl.get("declaration_id"), "selection": sel})
                review = save_review(kp_dir, review, expected_revision=review["revision"])
        else:
            ng_ent = ng_entries_of(review, family, slug, level)
            _write_text_atomic(pth["request"], _cc().request_notice(kp_dir) + render_request_md(cands, review, run_hint=run_hint, ng_entries=ng_ent))
            return {"state": "PENDING", "pending": pending_summary(kp_dir, level), "generated": generated}
    if review["status"] in FORWARD_STATUSES:
        fin = finalize_kp(kp_dir, level=level, redundancy_fn=redundancy_fn)   # 仕様②: finalizeはKpReviewPendingを送出しない(重複NGは差し戻さない)
        return {"state": "FINALIZED", "final": fin, "generated": generated}
    raise KpReviewError(f"想定外のstatus={review['status']}")


def raise_if_pending(results: dict) -> None:
    """複数レベルの結果をまとめ、1つでもPENDINGなら1回だけKpReviewPendingを送出する(レベル往復を最小化)。"""
    pend = [r["pending"] for r in results.values() if r.get("state") == "PENDING"]
    if pend:
        raise KpReviewPending(f"{PENDING_MARKER} KP Human Review待ち: " + ", ".join(p["level"] for p in pend), pend)
