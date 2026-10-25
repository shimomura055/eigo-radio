"""FAMILY-Z-TELL-TALE-HEART-KP-FIX-01: Std(a2) KP#2のみをユーザー指示で差し替える一回限りのdriver(DEV/個別修正用、Production runner無改変)。

方式: Z runnerの正式経路(main)をそのまま使い、KP選定段(_kp_fn_for_ctx)だけを固定選定へ差し替える。固定選定はer105の
run_fulltext_selection(make_call_fn注入)を通すため、本文連続一致/5語以内/重複/旧形式/CMU語彙の機械検証と、後段の
canonicalization・gloss再整合・Redundancy QA・SRC D1・TTS/ASR Gate・組立・pagesは正式経路のまま走る。
固定選定はa2のみ(b1bは再選定させない)。Production経路・既定動作は変更しない。
"""
import functools, json, sys
sys.path.insert(0, ".")
import er026_family_z_fiction_production_runner_01 as runner
import er105_kp_fulltext_selector_01 as ft

FIXED = {"a2": ["made my blood turn cold", "louder and louder", "went on talking"]}


def _fixed_make_call_fn(phrases):
    raw = json.dumps({"items": [{"phrase": p, "word_count": len(p.split())} for p in phrases]}, ensure_ascii=False)

    def make_call_fn(_msg):
        return lambda: (raw, "gpt-6-luna", "fixed_selection_by_user_instruction_2026-10-25")
    return make_call_fn


def _kp_fn_for_ctx(ctx):
    w62 = runner._m().w62

    def fn(text, kp_dir, article_id, source_level, process=None, **kw):
        if source_level != "A2":
            raise RuntimeError(f"固定選定はa2専用です(source_level={source_level!r})。b1bは再選定しない")
        sel = functools.partial(ft.run_fulltext_selection, make_call_fn=_fixed_make_call_fn(FIXED["a2"]))

        def select_fn(text_, kp_dir_, article_id_, source_level_, process=None, diagnostic_note=None, **k):
            return sel(text_, kp_dir_, article_id_, source_level_, process=process, diagnostic_note=diagnostic_note)
        return w62.run_kp_with_outer_retry_fulltext(text, kp_dir, article_id, source_level, process=process, select_fn=select_fn)
    return fn


runner._kp_fn_for_ctx = _kp_fn_for_ctx
if __name__ == "__main__":
    sys.exit(runner.main(sys.argv[1:]))
