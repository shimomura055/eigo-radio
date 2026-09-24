# ============================================================
# er016_topic_selection_user_preference_rerank_trial_01.py
# TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01 (Fable設計、2026-09-24)
# ============================================================
# 目的: ユーザーの実評価済みTeacher Data(57件、点数+Topic+Hook)を
# few-shot/preference examplesとして直接モデルへ渡し、同一Candidate Pool
# をLuna/Terra/Sol/Jevがユーザー嗜好に沿って順位付けできるかを比較する
# Trial。Production実装ではない。Production正式path(daily runner等)は
# 一切変更しない。
#
# 禁止事項: Teacher Dataを抽象Ruleへ圧縮すること/モデルごとにPrompt条件
# を変えること/既知評価TopicのCandidate Pool混入/Jev API keyの表示・
# log保存・commit・report記載(環境変数JEV_API_KEYを参照するのみ)。
#
# 再利用: er002_ja_web_research_r3(extract_web_search_usage/
# extract_sources)、er005_cost_logger(install/logging_context)、
# er006_model_routing_contract_01(WRITER_MODEL)。
# er016_topic_selection_chatgpt_repro_01.pyはimportのみ
# (REFERENCE_CONTAMINATION_KEYWORDS)。既存script(search_trial_03/
# reference_process_trial_01/chatgpt_repro_01/chatgpt_repro_01_cont02)は
# 一切変更しない(出力ファイルをreadするのみ)。
#
# --step: teacher-check / jev-probe / pool / cost-estimate / rerank
# 冪等性: 出力ファイルが既に存在する場合、--forceなしでは再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er005_cost_logger as cl
import er016_topic_selection_chatgpt_repro_01 as repro01

load_dotenv()

THEME_TAG = "TOPIC_SELECTION_USER_PREFERENCE_RERANK_TRIAL_01"
MODEL_LUNA = "gpt-5.6-luna"
MODEL_TERRA = "gpt-5.6-terra"
MODEL_SOL = "gpt-5.6-sol"
EFFORT_DEFAULT = "medium"
JST = timezone(timedelta(hours=9))

TEACHER_PATH = "docs/pm/topic_selection_user_eval_dataset.json"
WINDOW_START_JST = "2026-09-22T21:05:00+09:00"
BUDGET_JPY = 150.0
USD_TO_JPY = 160

# UGCドメイン(委任文指定)
UGC_DOMAIN_RE = re.compile(
    r"(note\.com|reddit\.com|minkara\.[a-z.]+|ameblo\.jp|hatenablog\.[a-z.]+"
    r"|x\.com|twitter\.com|instagram\.com|gravity[a-z.]*|threads\.net)",
    re.IGNORECASE,
)

MACHINE_GATE_EXCLUDE = {
    "PR_ADVERTORIAL", "AFFILIATE_RANKING", "SALE_PRICE",
    "UGC_PERSONAL", "LISTING_PAGE",
}
GATE_CATEGORIES = [
    "NEWS_FEATURE", "PRODUCT_PHENOMENON", "PR_ADVERTORIAL",
    "AFFILIATE_RANKING", "SALE_PRICE", "UGC_PERSONAL", "LISTING_PAGE",
    "UNCLEAR",
]


# ------------------------------------------------------------
# ヘルパー
# ------------------------------------------------------------
def out_path(out_dir: str, *parts: str) -> str:
    return os.path.join(out_dir, *parts)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def skip_if_exists(path: str, force: bool) -> bool:
    if os.path.exists(path) and not force:
        print(f"[SKIP] 既存出力あり(--forceなし): {path}")
        return True
    return False


def install_logger(out_dir: str) -> None:
    cl.install(out_path(out_dir, "raw_usage_log.jsonl"))


def get_client():
    from openai import OpenAI
    return OpenAI()


def call_model(client, developer: str, user: str, schema=None, stage="",
                model=MODEL_LUNA, effort=EFFORT_DEFAULT, retried=False):
    """1回のAPI技術的retryのみを許可する(品質理由の再実行は禁止)。"""
    kwargs = dict(
        model=model,
        reasoning={"effort": effort},
        input=[
            {"role": "developer", "content": developer},
            {"role": "user", "content": user},
        ],
    )
    if schema is not None:
        kwargs["text"] = {"format": {"type": "json_schema", **schema}}
    try:
        with cl.logging_context(THEME_TAG, stage):
            response = client.responses.create(**kwargs)
    except Exception as exc:
        if retried:
            raise
        print(f"[RETRY] {stage}: 技術的retry 1回目 ({exc})")
        time.sleep(2)
        return call_model(client, developer, user, schema=schema, stage=stage,
                           model=model, effort=effort, retried=True)
    if response.model != model:
        raise RuntimeError(
            f"STOP条件該当: actual model_idが要求モデルと異なる(stage={stage}, "
            f"requested={model}, actual={response.model})"
        )
    return response


def response_meta(response, extra: dict = None) -> dict:
    meta = {
        "model_requested": response.model,
        "response_model_actual": response.model,
        "response_id": response.id,
    }
    usage = getattr(response, "usage", None)
    if usage is not None:
        meta["usage"] = {
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        }
    if extra:
        meta.update(extra)
    return meta


def normalize_url(u: str) -> str:
    if not u:
        return ""
    u = u.strip()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    u = u.split("?")[0].split("#")[0]
    u = u.rstrip("/")
    return u.lower()


# ------------------------------------------------------------
# STEP 0: teacher-check
# ------------------------------------------------------------
def cmd_teacher_check(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "teacher_check.json")
    if skip_if_exists(path, args.force):
        return
    d = load_json(TEACHER_PATH)
    result = {"datasets": {}, "all_topics": []}
    ok = True
    for key in ("dataset_r", "dataset_a", "dataset_b"):
        items = d.get(key, [])
        missing_score = [it.get("item_no") for it in items
                          if it.get("user_score") is None]
        missing_topic = [it.get("item_no") for it in items
                          if not it.get("topic_ja")]
        result["datasets"][key] = {
            "n": len(items),
            "missing_score_item_no": missing_score,
            "missing_topic_item_no": missing_topic,
        }
        if missing_score or missing_topic:
            ok = False
        for it in items:
            result["all_topics"].append(
                {"dataset_id": it.get("dataset_id"), "item_no": it.get("item_no"),
                 "topic_ja": it.get("topic_ja")}
            )
    total_n = sum(v["n"] for v in result["datasets"].values())
    result["total_n"] = total_n
    if total_n != 57:
        ok = False
    from collections import Counter
    counts = Counter(t["topic_ja"] for t in result["all_topics"])
    dups = {k: v for k, v in counts.items() if v > 1}
    result["duplicate_topic_ja"] = dups
    result["complete"] = ok
    save_json(path, result)
    print(f"[OK] teacher-check: total_n={total_n} complete={ok} "
          f"duplicates={len(dups)}")
    if not ok:
        print("[STOP] Teacher Dataが不完全(件数/欠落/重複)。STOP条件該当。")
        raise SystemExit(1)


# ------------------------------------------------------------
# STEP 1: jev-probe
# ------------------------------------------------------------
def cmd_jev_probe(args):
    out_dir = args.out_dir
    probe_path = out_path(out_dir, "jev_probe.json")
    stop_path = out_path(out_dir, "stop_reason.json")
    if skip_if_exists(probe_path, args.force):
        return
    key_present = bool(os.environ.get("JEV_API_KEY"))
    result = {
        "checked_at_jst": datetime.now(JST).isoformat(),
        "jev_api_key_present": key_present,
        "repo_integration_found": False,
        "official_docs_finding": (
            "jev.ai はドメインパーキングページ(title=\"Parking Landing\")で"
            "あり、Jev社の公式API仕様(endpoint/認証ヘッダ/request-response "
            "schema/料金/rate limit)を外部から特定できなかった。Repo内には "
            "Jev用clientコード・環境変数例・仕様メモは一切存在しない"
            "(`docs/pm/topic_selection_user_eval_dataset.json` dataset_r "
            "item_no=15の話題[Xで話題化した意思決定特化型AI「Jev」]としての"
            "言及のみで、実在API連携の記録ではない)。"
        ),
        "attempted_min_request": False,
        "connection_result": None,
    }
    if key_present:
        # 仕様上ここで最小request(候補1件・Teacher例5件程度)を1回だけ実施する
        # 設計だが、JEV_API_KEY不在のため到達しない分岐。将来key設定時に
        # 実装追加が必要(未実装、Fable/ユーザー判断待ち)。
        result["attempted_min_request"] = True
        result["connection_result"] = "NOT_IMPLEMENTED: keyはあるがJev公式" \
            "API仕様(endpoint等)が特定できないため接続実装なし。"
    stop = not key_present or result["connection_result"] in (
        None, "NOT_IMPLEMENTED",
    ) or (result["connection_result"] or "").startswith("NOT_IMPLEMENTED")
    save_json(probe_path, result)
    if stop:
        stop_reason = {
            "reason": "JEV_ARM_INFEASIBLE",
            "detail": (
                "JEV_API_KEYが環境変数に存在しない(bool=False)。加えて、"
                "Jev公式API仕様(endpoint/認証/schema/料金/rate limit)を"
                "外部公式ドキュメントからも特定できなかった(jev.aiはドメイン"
                "パーキングページ)。Repo内にもJev client実装・仕様記録は"
                "存在しない。委任文の該当STOP条件"
                "『Jev arm実施不能(接続不可・API仕様が特定できない)』に該当。"
            ),
            "action": "USER_DECISION_REQUIRED。Pool作成(STEP 2)までは完了し、"
                      "Luna/Terra/Solのrerank(STEP 3以降)は実行しない。",
            "checked_at_jst": result["checked_at_jst"],
        }
        save_json(stop_path, stop_reason)
        print("[STOP] Jev arm実施不能。stop_reason.json保存。"
              "USER_DECISION_REQUIRED。Pool作成までは継続する。")
    else:
        print("[OK] jev-probe: 接続確認成功(この分岐は現状到達しない)。")


# ------------------------------------------------------------
# STEP 2: pool
# ------------------------------------------------------------
def _load_search_trial_03_pool():
    d = load_json("er016_output/topic_selection_search_trial_03/pool_final.json")
    out = []
    for c in d.get("candidates", []):
        out.append({
            "raw_title": c.get("title"),
            "summary_ja": c.get("summary_ja"),
            "url": c.get("url"),
            "source_name": c.get("source_name"),
            "published_time_iso": c.get("published_time_iso"),
            "source_gate_category": (
                "PR_ADVERTORIAL" if c.get("is_pr_or_ad_guess") or
                c.get("machine_pr_signal") else c.get("source_gate_category")
            ),
            "origin": "topic_selection_search_trial_03/pool_final.json",
        })
    return out


def _load_reference_process_pool():
    d = load_json("er016_output/topic_selection_reference_process_trial_01/pool.json")
    out = []
    exclude_reason_prefixes = ("UGC_EXCLUDE", "PR_RELEASE", "PR_SURVEY_RELEASE",
                                "AD_SUBDOMAIN_CONTENT", "CONTENT_MARKETING",
                                "UNIV_PRESS_RELEASE")
    for cid, c in d.get("candidates", {}).items():
        status = c.get("status")
        if status == "dropped":
            reason = c.get("drop_reason") or ""
            if reason.startswith("DUPLICATE") or reason.startswith("SAME_AS"):
                continue  # 既にkept/replaced側に同一事象が残っている
            if any(reason.startswith(p) for p in exclude_reason_prefixes):
                continue  # UGC/PR系はSource Gate除外のまま維持
            # それ以外(窓外・一般性・トーン等)は候補へ復帰可(委任文の指示)
        out.append({
            "raw_title": c.get("topic_ja"),
            "summary_ja": c.get("summary_2sent_ja"),
            "url": c.get("url"),
            "source_name": c.get("source_name"),
            "published_time_iso": None,
            "source_gate_category": None,
            "origin": f"topic_selection_reference_process_trial_01/pool.json"
                      f"[{cid},status={status}]",
        })
    return out


def _load_generic_pool(path, origin_label):
    d = load_json(path)
    out = []
    for c in d.get("candidates", []):
        out.append({
            "raw_title": c.get("title"),
            "summary_ja": c.get("summary_ja"),
            "url": c.get("url"),
            "source_name": c.get("source_name"),
            "published_time_iso": c.get("published_time_iso"),
            "source_gate_category": (
                "PR_ADVERTORIAL" if c.get("is_pr_or_ad") else None
            ),
            "origin": origin_label,
        })
    return out


def machine_gate(cand: dict) -> str | None:
    """機械signalで確定できるカテゴリを返す。確定できなければNone。"""
    url = cand.get("url") or ""
    if UGC_DOMAIN_RE.search(url):
        return "UGC_PERSONAL"
    if cand.get("source_gate_category") in GATE_CATEGORIES:
        return cand["source_gate_category"]
    return None


CLASSIFY_SCHEMA = {
    "name": "source_gate_classify",
    "schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "category": {"type": "string", "enum": GATE_CATEGORIES},
                        "reason": {"type": "string"},
                    },
                    "required": ["id", "category", "reason"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["results"],
        "additionalProperties": False,
    },
    "strict": True,
}

CLASSIFY_DEVELOPER = (
    "You classify Japanese news/web candidates for a source-quality gate. "
    "Categories: NEWS_FEATURE (independent news/feature reporting), "
    "PRODUCT_PHENOMENON (a product or social phenomenon covered as news, "
    "not an ad), PR_ADVERTORIAL (PR release, sponsored, advertorial), "
    "AFFILIATE_RANKING (affiliate-style ranking/comparison article), "
    "SALE_PRICE (sale/discount/coupon focused article), "
    "UGC_PERSONAL (personal blog/UGC post), "
    "LISTING_PAGE (a list/search-result page, not a single article), "
    "UNCLEAR (cannot tell). Classify strictly from the given title/summary/"
    "source/url only."
)


def classify_batch(client, out_dir, items, batch_idx):
    lines = []
    for it in items:
        lines.append(json.dumps({
            "id": it["cand_id"], "title": it["raw_title"],
            "summary": it["summary_ja"], "source": it["source_name"],
            "url": it["url"],
        }, ensure_ascii=False))
    user = "Classify each of the following candidates.\n\n" + "\n".join(lines)
    resp = call_model(client, CLASSIFY_DEVELOPER, user, schema=CLASSIFY_SCHEMA,
                       stage=f"gate_classify_{batch_idx}", model=MODEL_LUNA)
    data = json.loads(resp.output_text)
    save_json(out_path(out_dir, "prompts", f"gate_classify_{batch_idx}.json"),
              {"developer": CLASSIFY_DEVELOPER, "user": user})
    save_json(out_path(out_dir, "raw_responses", f"gate_classify_{batch_idx}.json"),
              response_meta(resp))
    return {r["id"]: r for r in data["results"]}


CONTAM_SCHEMA = {
    "name": "contamination_check",
    "schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {"type": "string"},
                        "same_event_as_teacher": {"type": "boolean"},
                        "reason": {"type": "string"},
                    },
                    "required": ["candidate_id", "same_event_as_teacher", "reason"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["results"],
        "additionalProperties": False,
    },
    "strict": True,
}

CONTAM_DEVELOPER = (
    "You check whether a candidate news topic refers to the SAME real-world "
    "event/topic as a teacher-data topic that a listener has already rated, "
    "even if phrased differently. Judge based on the underlying event, not "
    "surface wording."
)


def contamination_batch(client, out_dir, pairs, batch_idx):
    lines = []
    for p in pairs:
        lines.append(json.dumps({
            "candidate_id": p["cand_id"], "candidate_topic": p["cand_topic"],
            "teacher_topic": p["teacher_topic"], "teacher_hook": p["teacher_hook"],
        }, ensure_ascii=False))
    user = ("For each pair below, judge if candidate_topic refers to the same "
            "underlying event as teacher_topic/teacher_hook.\n\n" + "\n".join(lines))
    resp = call_model(client, CONTAM_DEVELOPER, user, schema=CONTAM_SCHEMA,
                       stage=f"contamination_{batch_idx}", model=MODEL_LUNA)
    data = json.loads(resp.output_text)
    save_json(out_path(out_dir, "prompts", f"contamination_{batch_idx}.json"),
              {"developer": CONTAM_DEVELOPER, "user": user})
    save_json(out_path(out_dir, "raw_responses", f"contamination_{batch_idx}.json"),
              response_meta(resp))
    return {r["candidate_id"]: r for r in data["results"]}


def cmd_pool(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "candidate_pool.json")
    if skip_if_exists(path, args.force):
        return
    install_logger(out_dir)

    raw = []
    raw += _load_search_trial_03_pool()
    raw += _load_reference_process_pool()
    raw += _load_generic_pool(
        "er016_output/topic_selection_chatgpt_repro_01_cont02/pool_new.json",
        "topic_selection_chatgpt_repro_01_cont02/pool_new.json")
    raw += _load_generic_pool(
        "er016_output/topic_selection_chatgpt_repro_01/candidates_raw.json",
        "topic_selection_chatgpt_repro_01/candidates_raw.json")

    stats = {"raw_total": len(raw)}

    # --- URL正規化dedup ---
    seen = set()
    deduped = []
    for c in raw:
        nu = normalize_url(c.get("url") or "")
        if not nu or nu in seen:
            continue
        seen.add(nu)
        c["norm_url"] = nu
        deduped.append(c)
    stats["after_url_dedup"] = len(deduped)

    # --- id付与 ---
    for i, c in enumerate(deduped):
        c["cand_id"] = f"RAW{i+1:04d}"

    # --- 機械Source Gate ---
    machine_excluded = []
    unclear = []
    machine_kept = []
    for c in deduped:
        cat = machine_gate(c)
        if cat is None:
            unclear.append(c)
        elif cat in MACHINE_GATE_EXCLUDE:
            c["source_gate_category"] = cat
            c["source_gate_stage"] = "machine"
            machine_excluded.append(c)
        elif cat == "UNCLEAR":
            unclear.append(c)
        else:
            c["source_gate_category"] = cat
            c["source_gate_stage"] = "machine"
            machine_kept.append(c)
    stats["machine_excluded"] = len(machine_excluded)
    stats["machine_kept"] = len(machine_kept)
    stats["needs_luna_classification"] = len(unclear)

    client = get_client()

    # --- Luna分類(UNCLEAR分のみ、40件/batch) ---
    luna_excluded = []
    luna_kept = []
    BATCH = 40
    for bi in range(0, len(unclear), BATCH):
        batch = unclear[bi:bi + BATCH]
        results = classify_batch(client, out_dir, batch, bi // BATCH)
        for c in batch:
            r = results.get(c["cand_id"])
            cat = r["category"] if r else "UNCLEAR"
            c["source_gate_category"] = cat
            c["source_gate_stage"] = "luna"
            c["source_gate_reason"] = r["reason"] if r else "no_result"
            if cat in MACHINE_GATE_EXCLUDE or cat == "UNCLEAR":
                luna_excluded.append(c)
            else:
                luna_kept.append(c)
    stats["luna_excluded"] = len(luna_excluded)
    stats["luna_kept"] = len(luna_kept)

    gated = machine_kept + luna_kept
    stats["after_source_gate"] = len(gated)

    save_json(out_path(out_dir, "gate_result.json"), {
        "stats": stats,
        "machine_excluded_sample": [
            {"cand_id": c["cand_id"], "title": c.get("raw_title"),
             "category": c.get("source_gate_category"), "url": c.get("url")}
            for c in machine_excluded
        ],
        "luna_excluded_sample": [
            {"cand_id": c["cand_id"], "title": c.get("raw_title"),
             "category": c.get("source_gate_category"),
             "reason": c.get("source_gate_reason"), "url": c.get("url")}
            for c in luna_excluded
        ],
    })

    # --- 既知評価Topic混入検査(difflib >= 0.5) ---
    teacher = load_json(TEACHER_PATH)
    teacher_items = []
    for key in ("dataset_r", "dataset_a", "dataset_b"):
        for it in teacher.get(key, []):
            teacher_items.append({
                "dataset_id": it.get("dataset_id"), "item_no": it.get("item_no"),
                "topic_ja": it.get("topic_ja") or "", "hook_ja": it.get("hook_ja") or "",
            })

    def best_match(topic_ja):
        best = (0.0, None)
        for t in teacher_items:
            r1 = difflib.SequenceMatcher(None, topic_ja, t["topic_ja"]).ratio()
            r2 = difflib.SequenceMatcher(None, topic_ja, t["hook_ja"]).ratio()
            r = max(r1, r2)
            if r > best[0]:
                best = (r, t)
        return best

    auto_exclude = []
    borderline = []
    clean = []
    for c in gated:
        ratio, t = best_match(c.get("raw_title") or "")
        c["contamination_best_ratio"] = round(ratio, 3)
        c["contamination_best_match"] = (
            f"{t['dataset_id']}#{t['item_no']}:{t['topic_ja']}" if t else None
        )
        if ratio >= 0.65:
            auto_exclude.append(c)
        elif ratio >= 0.5:
            borderline.append(c)
        else:
            clean.append(c)

    luna_contam_excluded = []
    if borderline:
        pairs = []
        for c in borderline:
            ratio, t = best_match(c.get("raw_title") or "")
            pairs.append({
                "cand_id": c["cand_id"], "cand_topic": c.get("raw_title"),
                "teacher_topic": t["topic_ja"], "teacher_hook": t["hook_ja"],
            })
        results = {}
        CBATCH = 30
        for bi in range(0, len(pairs), CBATCH):
            results.update(contamination_batch(client, out_dir,
                                                 pairs[bi:bi + CBATCH], bi // CBATCH))
        for c in borderline:
            r = results.get(c["cand_id"])
            if r and r["same_event_as_teacher"]:
                c["contamination_reason"] = r["reason"]
                luna_contam_excluded.append(c)
            else:
                c["contamination_reason"] = r["reason"] if r else "no_result_kept"
                clean.append(c)

    final = clean
    stats["contamination_auto_excluded"] = len(auto_exclude)
    stats["contamination_borderline"] = len(borderline)
    stats["contamination_luna_excluded"] = len(luna_contam_excluded)
    stats["contamination_kept_after_check"] = len(final)

    save_json(out_path(out_dir, "contamination_result.json"), {
        "stats": {
            "auto_excluded_ge_0.65": len(auto_exclude),
            "borderline_0.5_to_0.65": len(borderline),
            "luna_excluded_from_borderline": len(luna_contam_excluded),
        },
        "auto_excluded": [
            {"cand_id": c["cand_id"], "title": c.get("raw_title"),
             "ratio": c["contamination_best_ratio"],
             "match": c["contamination_best_match"]}
            for c in auto_exclude
        ],
        "luna_excluded": [
            {"cand_id": c["cand_id"], "title": c.get("raw_title"),
             "ratio": c["contamination_best_ratio"],
             "match": c["contamination_best_match"],
             "reason": c.get("contamination_reason")}
            for c in luna_contam_excluded
        ],
    })

    # --- 目標50件(40-60)に整形。超過時は各origin均等になるよう間引き ---
    target_min, target_max = 40, 60
    stats["final_before_trim"] = len(final)
    if len(final) > target_max:
        # originごとに束ね、ラウンドロビンでtarget件数まで採用
        from collections import defaultdict
        by_origin = defaultdict(list)
        for c in final:
            by_origin[c["origin"].split("[")[0]].append(c)
        ordered = []
        idx = 0
        keys = list(by_origin.keys())
        while len(ordered) < target_max and any(by_origin.values()):
            k = keys[idx % len(keys)]
            if by_origin[k]:
                ordered.append(by_origin[k].pop(0))
            idx += 1
            if idx > 10000:
                break
        final = ordered

    stats["final_pool_n"] = len(final)
    stats["target_range"] = [target_min, target_max]
    stats["needs_supplemental_search"] = len(final) < target_min

    pool_out = []
    for i, c in enumerate(final):
        pool_out.append({
            "id": f"C{i+1:03d}",
            "topic_ja": (c.get("raw_title") or "")[:200],
            "summary_ja": c.get("summary_ja") or "",
            "url": c.get("url"),
            "source_name": c.get("source_name"),
            "published_time_iso": c.get("published_time_iso"),
            "origin_trial": c.get("origin"),
            "source_class": c.get("source_gate_category"),
            "source_gate_stage": c.get("source_gate_stage"),
            "contamination_best_ratio": c.get("contamination_best_ratio"),
        })

    save_json(path, pool_out)
    sha256 = hashlib.sha256(
        json.dumps(pool_out, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    save_json(out_path(out_dir, "candidate_pool_sha256.json"), {"sha256": sha256})
    save_json(out_path(out_dir, "pool_pipeline_stats.json"), stats)

    print(f"[OK] pool: raw={stats['raw_total']} after_dedup="
          f"{stats['after_url_dedup']} after_gate={stats['after_source_gate']} "
          f"after_contamination={stats['contamination_kept_after_check']} "
          f"final={stats['final_pool_n']} sha256={sha256[:16]}...")
    if stats["needs_supplemental_search"]:
        print("[WARN] final_pool_n < 40。最小限の追加Search(--max-search-calls)"
              "が必要(未実装、既存Poolのみで下限未達)。")


# ------------------------------------------------------------
# cost-estimate
# ------------------------------------------------------------
def _price(pricing, provider, model, meter):
    try:
        return next(p["price"] for p in pricing
                    if p["provider"] == provider and p["model"] == model
                    and p["meter"] == meter)
    except StopIteration:
        return None


def cmd_cost_estimate(args):
    out_dir = args.out_dir
    pricing = load_json("er005_output/cost_baseline_01/pricing_snapshot.json")["prices"]

    def model_prices(model_name):
        return (
            _price(pricing, "openai", model_name, "input_tokens"),
            _price(pricing, "openai", model_name, "cached_input_tokens"),
            _price(pricing, "openai", model_name, "output_tokens"),
        )

    log_path = out_path(out_dir, "raw_usage_log.jsonl")
    entries = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    entries = [e for e in entries if e.get("theme") == THEME_TAG]

    by_model = {}
    total_jpy = 0.0
    for e in entries:
        if e.get("provider") != "openai" or not e.get("success", True):
            continue
        model_name = e.get("model") or MODEL_LUNA
        prices = model_prices(model_name)
        if any(p is None for p in prices):
            by_model.setdefault(model_name, {"calls": 0, "jpy": "UNKNOWN_PRICING"})
            by_model[model_name]["calls"] += 1
            continue
        p_in, p_cached, p_out = prices
        it = e.get("input_tokens") or 0
        ct = e.get("cached_input_tokens") or 0
        ot = e.get("output_tokens") or 0
        billable_in = max(it - ct, 0)
        usd = (billable_in / 1_000_000) * p_in + (ct / 1_000_000) * p_cached \
            + (ot / 1_000_000) * p_out
        jpy = usd * USD_TO_JPY
        entry = by_model.setdefault(model_name, {"calls": 0, "jpy": 0.0})
        if entry["jpy"] == "UNKNOWN_PRICING":
            continue
        entry["calls"] += 1
        entry["jpy"] += jpy
        total_jpy += jpy

    result = {
        "budget_jpy": BUDGET_JPY,
        "actual_so_far_jpy": round(total_jpy, 2),
        "by_model": by_model,
        "within_budget": total_jpy <= BUDGET_JPY,
        "note": "pool step(Luna gate分類+contamination判定)実行後の実績。"
                "rerank(L/T/S/J)は未実行(Jev arm実施不能によりSTOP)。",
    }
    save_json(out_path(out_dir, "cost_estimate.json"), result)
    print(f"[OK] cost-estimate: actual_so_far={round(total_jpy,2)} JPY "
          f"(budget={BUDGET_JPY})")


# ------------------------------------------------------------
# rerank (guard: Jevを最初に実行し、失敗時は残りを実行せず非0終了)
# ------------------------------------------------------------
def cmd_rerank(args):
    out_dir = args.out_dir
    arms = args.arms.split(",")
    if arms[0] != "J":
        raise SystemExit("STOP: arms先頭はJ(Jev)である必要がある(委任文指定)。")
    stop_path = out_path(out_dir, "stop_reason.json")
    probe_path = out_path(out_dir, "jev_probe.json")
    if os.path.exists(stop_path):
        stop = load_json(stop_path)
        print(f"[STOP] Jev arm実施不能(理由: {stop_path}参照)。"
              "Luna/Terra/Solを含む残りのarmを実行せず終了する"
              "(委任文: 「先行完了させて4-way比較完了としない」)。")
        raise SystemExit(1)
    if not os.path.exists(probe_path):
        raise SystemExit("STOP: jev-probe未実行。先に --step jev-probe を実行すること。")
    raise SystemExit("STOP: Jev arm実装は現状未到達(key不在のため)。")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--step", required=True,
                        choices=["teacher-check", "jev-probe", "pool",
                                 "cost-estimate", "rerank", "assemble"])
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--target", type=int, default=50)
    parser.add_argument("--max-search-calls", type=int, default=4)
    parser.add_argument("--budget-jpy", type=float, default=BUDGET_JPY)
    parser.add_argument("--arms", default="J,L,T,S")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    if args.step == "teacher-check":
        cmd_teacher_check(args)
    elif args.step == "jev-probe":
        cmd_jev_probe(args)
    elif args.step == "pool":
        cmd_pool(args)
    elif args.step == "cost-estimate":
        cmd_cost_estimate(args)
    elif args.step == "rerank":
        cmd_rerank(args)
    elif args.step == "assemble":
        raise SystemExit(
            "STOP: assembleはrerank(L/T/S/J全arm)完了後の工程。"
            "Jev arm実施不能によりSTOPしているため未実行。"
        )


if __name__ == "__main__":
    main()
