# SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_02C(2026-10-30、ユーザー指示 APPROVED_FOR_PRODUCTION・到達目標PRODUCTION_WIRED):
# Vocabulary & Expressions の掲載項目すべて(確定③項目=vocab_confirmed.json、KP3件+②追加解説)に英語音声を付ける生成側の共通module。
#   DESIGN_01.md 4節 / Opus M6(掲載項目は全件音声必須=fail-closed) / M7(KP項目も単体mp3)。
# 方針:
#   - KPと重複する項目: 既存の`kp{rank}_en.wav`(KP stageで生成・検証・Gate済み)を単体mp3へ変換して再利用する。TTS 0・既存KP音声は再生成しない。
#   - ②追加解説(KPでない項目): 役割`vocab_extra_english`で、KP英語と同一の`_generate_or_reuse_kp`+`_kp_english_generate_fn`(KP3V 3-ASR多数決・
#     Master Audio Store key・既存retry/fallback)を通して`vocab_extra_<n>_en.wav`を生成する(新stageなし。Z=er063は`generate_or_reuse_z`+KP英語generator)。
#     同じ英語表現がStoreにあればStore hit=生成0(KP音声再利用優先)。結果は`tts_generation_results.json`のtop-level`vocab_extra`
#     ({"v<n>": {"vocab_extra_english": entry}})に保存し、既存Gate(`asm.verify_episode_audio_validation_gate`)が`kpv<n>_vocab_extra_english`として
#     同じ規則(OK/HUMAN_APPROVED以外はEPISODE_BLOCKED)で検査する=失敗は黙って「音声なし掲載」にならない。
#   - 公開用の単体mp3と索引`vocab_audio.json`は`export_level()`が作る。1件でも欠落/不正なら`complete=false`+`VocabAudioIncomplete`(fail-closed)。
#   - article.json(`enduser_article_v1`)への加法フィールド`levels[lv].vocab[i].audio`は`apply_to_article()`が付与する(全件必須)。
# 本moduleは新flagを持たない(量産経路の承認済み仕様=全掲載項目の音声。Prompt・閾値・Style・retry上限は不変)。
import hashlib
import json
import os
import re
import shutil
import subprocess
import wave

ROLE = "vocab_extra_english"
RESULTS_KEY = "vocab_extra"
SCHEMA_VERSION = "vocab_audio_v1"
LEVEL_TO_ARTICLE_KEY = {"a2": "std", "b1b": "adv"}


class VocabAudioIncomplete(RuntimeError):
    """掲載項目に音声が揃っていない(fail-closed)。"""


def _sha_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _norm(s) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s']", " ", (s or "").lower())).strip()


def _term_of(it: dict) -> str:
    return it.get("used_form") or it.get("display_phrase") or it.get("key_phrase") or ""


def find_kp_dir(level_dir: str, level: str) -> str | None:
    """確定Vocabulary(vocab_confirmed.json)の置き場を返す(無ければNone=Part 1対象外/旧run)。
    X=`<level_dir>/key_phrases`、Y/Z=`<run>/key_phrases/<level>`(`<level_dir>/key_phrases`はKP assets copyのみ)。両方を順に探す=
    置き場の違いで②追加音声が黙って0件になる事故を防ぐ。"""
    run_dir = os.path.dirname(level_dir.rstrip("/\\"))
    for d in (f"{level_dir}/key_phrases", f"{run_dir}/key_phrases/{level}"):
        if os.path.exists(f"{d}/vocab_confirmed.json"):
            return d
    return None


def load_level_vocab(kp_dir: str) -> list:
    """掲載Vocabulary項目(Part 1の入力と同じ単一アクセサ)。vocab_confirmed.jsonが無い旧runは[](=KP音声のみで別扱い)。
    確定内容保護(verify_items_against_record)を通る=確定recordと一致する項目だけ。"""
    if not os.path.exists(f"{kp_dir}/vocab_confirmed.json"):
        return []
    import er119_kp_human_review_01 as hr
    return list(hr.part1_items(kp_dir))


def split_vocab(vocab_items: list, kp_items: list) -> list:
    """各掲載項目をKP重複(kp_rank有)/②追加(kp_rank=None)に分ける。照合=candidate_id、無ければ正規化used_form。"""
    by_cid = {it.get("candidate_id"): it for it in kp_items if it.get("candidate_id")}
    by_norm = {_norm(_term_of(it)): it for it in kp_items}
    out = []
    for i, v in enumerate(vocab_items, start=1):
        k = by_cid.get(v.get("candidate_id")) or by_norm.get(_norm(_term_of(v)))
        out.append({"vocab_index": v.get("rank", i), "candidate_id": v.get("candidate_id"), "term": _term_of(v),
                    "item": v, "kp_rank": (k.get("rank") if k is not None else None)})
    return out


def extra_wav_name(n) -> str:
    return f"vocab_extra_{n}_en.wav"


def extras_of(split: list) -> list:
    return [s for s in split if s["kp_rank"] is None]


def stopped_entry(term: str, reason: str) -> dict:
    return {"status": "STOPPED", "reason": reason, "canonical_text": term, "text": term, "approval_required": True}


def generate_extras(extras: list, narration_dir: str, cached: dict | None, *, reuse_fn, gen_factory, seg_context,
                    blocked_reason: str | None = None) -> dict:
    """②追加項目の英語音声を生成/再利用する(X/Y共通。reuse_fn=runnerの`_generate_or_reuse_kp`、gen_factory(text, wav)->generate_fn)。
    戻り値: {"v<n>": {ROLE: entry}}。resume時は前回resultsのOK entryを`_generate_or_reuse_kp`の再利用ガード(値ガード・KP3V再利用ゲート)経由で
    再利用する(API 0)。blocked_reasonがあれば(KP gloss HR待ち等)生成せず全件STOPPED entryを書く(Gateでblock。0 API call)。"""
    cview = {"key_phrases": (cached or {}).get(RESULTS_KEY) or {}, "style_version": (cached or {}).get("style_version")}
    out = {}
    for ex in extras:
        n, text = ex["vocab_index"], ex["term"]
        wav = f"{narration_dir}/{extra_wav_name(n)}"
        if blocked_reason:
            entry = stopped_entry(text, blocked_reason)
        else:
            with seg_context(f"vocab_extra{n}_english"):
                entry = reuse_fn(cview, f"v{n}", ROLE, wav, gen_factory(text, wav), expected_text=text)
            entry["canonical_text"] = text
        entry["vocab_index"] = n
        entry["candidate_id"] = ex.get("candidate_id")
        out[f"v{n}"] = {ROLE: entry}
    return out


# ---------------- export(公開用単体mp3 + 索引) ----------------
def _ffmpeg() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        w = shutil.which("ffmpeg")
        if not w:
            raise VocabAudioIncomplete("ffmpegが見つかりません(単体mp3を作れない=fail-closed)")
        return w


def _wav_seconds(p) -> float:
    with wave.open(p, "rb") as w:
        return w.getnframes() / float(w.getframerate())


def _mp3_seconds(p) -> float:
    o = subprocess.run([_ffmpeg(), "-hide_banner", "-i", str(p)], capture_output=True, text=True, errors="replace").stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", o)
    if not m:
        raise VocabAudioIncomplete(f"mp3の長さを取得できません: {p}")
    return round(int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]), 3)


def _wav_to_mp3(wav: str, mp3: str) -> None:
    os.makedirs(os.path.dirname(mp3), exist_ok=True)
    tmp = mp3 + ".tmp.mp3"
    r = subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", wav, "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "96k", tmp],
                       capture_output=True, text=True, errors="replace")
    if r.returncode != 0 or not os.path.exists(tmp):
        raise VocabAudioIncomplete(f"mp3変換に失敗: {wav}: {r.stderr[-200:]}")
    os.replace(tmp, mp3)


def _gate_ok(entry, seg_key: str, approvals: dict) -> tuple:
    import er003_v1_n3_01_assemble as asm
    st = asm._segment_gate_status(entry, seg_key, approvals)
    return st in asm.AUDIO_GATE_ALLOWED_STATUSES, st


def _read_meta_sha(out_dir: str, n):
    p = f"{out_dir}/vocab_audio.json"
    if not os.path.exists(p):
        return None
    try:
        for it in json.load(open(p, encoding="utf-8")).get("items") or []:
            if it.get("vocab_index") == n:
                return it.get("wav_sha256")
    except Exception:
        return None
    return None


def export_level(level_dir: str, kp_dir: str, level: str, out_dir: str | None = None, *, strict: bool = True) -> dict:
    """掲載Vocabulary全件の単体mp3(`<out_dir>/vocab_<level>_<n>.mp3`)と索引`<out_dir>/vocab_audio.json`を作る(API 0・ffmpegのみ)。
    各項目: KP重複=既存`narration/kp<rank>_en.wav`(results key_phrases[rank].english)、②=`vocab_extra_<n>_en.wav`(results vocab_extra)。
    entryがGate許可状態(VALIDATED/HUMAN_APPROVED)・wav実在・entry.sha256==実wavのときだけmp3化。1件でも欠けたらcomplete=false(strict=Trueなら送出)。"""
    out_dir = out_dir or f"{level_dir}/vocab_audio"
    narration = f"{level_dir}/narration"
    rp = f"{level_dir}/audit/tts_generation_results.json"
    res = json.load(open(rp, encoding="utf-8")) if os.path.exists(rp) else {}
    ap = f"{level_dir}/audit/human_approved_segments.json"
    approvals = json.load(open(ap, encoding="utf-8")) if os.path.exists(ap) else {}
    kp_doc = json.load(open(f"{kp_dir}/keywords_canonicalized.json", encoding="utf-8")) if os.path.exists(f"{kp_dir}/keywords_canonicalized.json") else {"items": []}
    kp_items = kp_doc.get("items") or []
    vocab = load_level_vocab(kp_dir)
    if not vocab:   # vocab_confirmed.jsonが無い(Part 1対象外のlevel・旧run)=End User Vocabularyなし。何も書かない。
        return {"schema": SCHEMA_VERSION, "level": level, "skipped": "vocab_confirmed.json無し", "complete": True, "errors": [], "items": []}
    split = split_vocab(vocab, kp_items)
    items, errors = [], []
    for s in split:
        n = s["vocab_index"]
        if s["kp_rank"] is not None:
            r = s["kp_rank"]
            entry = ((res.get("key_phrases") or {}).get(str(r)) or {}).get("english")
            seg_key, wav, source = f"kp{r}_english", f"{narration}/kp{r}_en.wav", "kp_reuse"
        else:
            entry = ((res.get(RESULTS_KEY) or {}).get(f"v{n}") or {}).get(ROLE)
            seg_key, wav = f"kpv{n}_{ROLE}", f"{narration}/{extra_wav_name(n)}"
            e_ = entry or {}   # 由来: resume再利用(同runの前回results) / Master Audio Store hit(他runの同一英語表現) / 新規生成
            source = ("vocab_extra_resume_reused" if e_.get("reused_from_previous_run")
                      else "vocab_extra_store_reused" if e_.get("reused") is True else "vocab_extra_generated")
        rec = {"vocab_index": n, "candidate_id": s["candidate_id"], "term": s["term"], "source": source, "seg_key": seg_key}
        ok, st = _gate_ok(entry, seg_key, approvals)
        rec["gate_status"] = st
        if not ok:
            errors.append(f"{seg_key}={st}")
        elif not os.path.exists(wav):
            errors.append(f"{seg_key}=WAV_MISSING({os.path.basename(wav)})")
        elif entry.get("sha256") and entry["sha256"] != _sha_file(wav):
            errors.append(f"{seg_key}=WAV_SHA_MISMATCH")
        else:
            mp3 = f"{out_dir}/vocab_{level}_{n}.mp3"
            wsha = _sha_file(wav)
            if not (os.path.exists(mp3) and _read_meta_sha(out_dir, n) == wsha):
                _wav_to_mp3(wav, mp3)
            dur = _mp3_seconds(mp3)
            if dur <= 0:
                errors.append(f"{seg_key}=EMPTY_AUDIO")
            else:
                rec.update({"file": f"audio/vocab_{level}_{n}.mp3", "mp3": os.path.basename(mp3), "dur": dur, "sha256": _sha_file(mp3),
                            "wav_sha256": wsha, "tts_status": entry.get("status"), "wav_duration": round(_wav_seconds(wav), 3)})
        items.append(rec)
    doc = {"schema": SCHEMA_VERSION, "level": level, "complete": not errors and bool(items), "errors": errors, "items": items}
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/vocab_audio.json", "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    if strict and not doc["complete"]:
        raise VocabAudioIncomplete(f"Vocabulary音声が揃っていません(level={level}): {errors or '掲載項目0'}。音声欠落のまま掲載しません(fail-closed)。"
                                   "該当項目を再生成するか、Human Review承認後に再実行してください。")
    return doc


def assert_results_complete(level_dir: str, kp_dir: str) -> None:
    """確定Vocabularyの②追加項目すべてに`vocab_extra`のentryがあること(生成段が走っていない旧results/欠落をAssembly前に止める=fail-closed)。
    entryの状態(STOPPED等)は既存Gate(asm.verify_episode_audio_validation_gate)が検査する。vocab_confirmed.json無し=対象外。"""
    vocab = load_level_vocab(kp_dir)
    if not vocab:
        return
    kp_p = f"{kp_dir}/keywords_canonicalized.json"
    kp_items = (json.load(open(kp_p, encoding="utf-8")).get("items") or []) if os.path.exists(kp_p) else []
    rp = f"{level_dir}/audit/tts_generation_results.json"
    res = json.load(open(rp, encoding="utf-8")) if os.path.exists(rp) else {}
    missing = [f"kpv{ex['vocab_index']}_{ROLE}=MISSING({ex['term']})" for ex in extras_of(split_vocab(vocab, kp_items))
               if not ((res.get(RESULTS_KEY) or {}).get(f"v{ex['vocab_index']}") or {}).get(ROLE)]
    if missing:
        raise VocabAudioIncomplete(f"Vocabulary追加解説の英語音声がresultsにありません: {missing}。TTS段(tts_*)を再実行してください"
                                   "(既存OK segmentは再利用=API 0、追加項目だけ生成/Store再利用)。音声なしのまま組立・掲載しません(fail-closed)。")


def gate_hook(level_dir: str, kp_dir: str | None, level: str) -> dict:
    """各runnerのGate通過直後に1回呼ぶ共通hook: (1)追加項目の欠落をSTOP (2)公開用単体mp3+vocab_audio.jsonをexport(API 0・非strict)。
    kp_dir=Noneなら`find_kp_dir`で解決(X/Y)。vocab_confirmed.json無し=対象外(何も書かない)。"""
    kp_dir = kp_dir or find_kp_dir(level_dir, level)
    if kp_dir is None:
        return {"schema": SCHEMA_VERSION, "level": level, "skipped": "vocab_confirmed.json無し", "complete": True, "errors": [], "items": []}
    assert_results_complete(level_dir, kp_dir)
    return export_level(level_dir, kp_dir, level, strict=False)


# ---------------- article.json(enduser_article_v1)への加法フィールド ----------------
# levels[std|adv].vocab[i].audio = {"kind": "standalone", "file": "audio/vocab_<a2|b1b>_<n>.mp3", "dur": <秒,>0>, "sha256": <mp3 sha256 hex64>}
def audio_field(rec: dict) -> dict:
    return {"kind": "standalone", "file": rec["file"], "dur": rec["dur"], "sha256": rec["sha256"]}


def apply_to_article(article: dict, docs_by_level: dict) -> dict:
    """article['levels'][std|adv]['vocab'][i]['audio'] を付与する。docs_by_level={'a2': vocab_audio.json内容, 'b1b': ...}。
    掲載項目(heading)に対応する音声が無い/completeでない場合はVocabAudioIncomplete(fail-closed。音声なし掲載を作らない)。"""
    for lv, akey in LEVEL_TO_ARTICLE_KEY.items():
        L = (article.get("levels") or {}).get(akey)
        if not L or not L.get("vocab"):
            continue
        doc = docs_by_level.get(lv)
        if not doc or not doc.get("complete"):
            raise VocabAudioIncomplete(f"{akey}: vocab_audio.jsonが無い/completeではありません")
        by = {_norm(r["term"]): r for r in doc["items"] if r.get("file")}
        for v in L["vocab"]:
            r = by.get(_norm(v.get("heading")))
            if r is None:
                raise VocabAudioIncomplete(f"{akey}: 掲載項目'{v.get('heading')}'に対応する音声がありません")
            v["audio"] = audio_field(r)
    return article


def validate_article(article: dict, public_dir: str | None = None) -> list:
    """全掲載vocab項目にaudioがあること(+public_dir指定時はfile実在・sha)。違反リストを返す(空=OK)。"""
    bad = []
    for akey, L in (article.get("levels") or {}).items():
        for i, v in enumerate((L or {}).get("vocab") or []):
            a = v.get("audio")
            if (not isinstance(a, dict) or a.get("kind") != "standalone" or not a.get("file") or not (a.get("dur") or 0) > 0
                    or not re.fullmatch(r"[0-9a-f]{64}", a.get("sha256") or "")):
                bad.append(f"{akey}.vocab[{i}]({v.get('heading')})=AUDIO_MISSING_OR_INVALID")
                continue
            if public_dir is not None:
                p = os.path.join(public_dir, a["file"])
                if not os.path.exists(p) or _sha_file(p) != a["sha256"]:
                    bad.append(f"{akey}.vocab[{i}]({v.get('heading')})=AUDIO_FILE_MISSING_OR_SHA_MISMATCH")
    return bad


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Vocabulary単体mp3+索引をexport(API 0)")
    ap.add_argument("--level-dir", required=True)
    ap.add_argument("--kp-dir", required=True)
    ap.add_argument("--level", required=True, choices=["a2", "b1b"])
    ap.add_argument("--out-dir")
    a = ap.parse_args(argv)
    try:
        d = export_level(a.level_dir, a.kp_dir, a.level, a.out_dir)
    except VocabAudioIncomplete as e:
        print(f"[STOP] {e}")
        return 4
    print(json.dumps({"complete": d["complete"], "items": len(d["items"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
