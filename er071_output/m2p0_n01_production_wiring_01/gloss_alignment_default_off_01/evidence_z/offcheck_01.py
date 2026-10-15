"""KGA2 既定OFF: X/Z正式runnerの既定設定確認(API呼出0、env未設定で起動すること)。"""
import inspect, json, os, sys
sys.path.insert(0, os.getcwd())
assert "EIGO_KP_GLOSS_ALIGNMENT" not in os.environ
import er003_key_words_gloss_alignment as ga
import er019_family_x_audio_production_runner_01 as x
import er026_family_z_fiction_production_runner_01 as z
out = {"env_EIGO_KP_GLOSS_ALIGNMENT": os.environ.get("EIGO_KP_GLOSS_ALIGNMENT"),
       "GLOSS_ALIGNMENT_ENABLED": ga.GLOSS_ALIGNMENT_ENABLED, "GLOSS_ALIGNMENT_MODE": ga.GLOSS_ALIGNMENT_MODE,
       "preflight_default": ga.preflight(),
       "X_run_theme_scaffold_gloss_alignment_mode_default": inspect.signature(x.run_theme_scaffold).parameters["gloss_alignment_mode"].default,
       "Z_E2EContext_gloss_alignment_mode_default": z.E2EContext.__dataclass_fields__["gloss_alignment_mode"].default,
       "Z_cli_has_gloss_option": "gloss" in z.build_parser().format_help().lower(),
       "X_cli_has_gloss_option": "gloss" in x.build_arg_parser().format_help().lower()}
ctx = z.E2EContext(story_key="melos", slug="x", run="r", mode="dry-run")
out["Z_kp_fn_default_is_plain_outer_retry"] = z._kp_fn_for_ctx(ctx).__name__ if hasattr(z._kp_fn_for_ctx(ctx), "__name__") else str(z._kp_fn_for_ctx(ctx))
r = ga.align_glosses({"items": [{"rank": 1}]}, "a", lambda m: (_ for _ in ()).throw(AssertionError("API must not be called")))
out["align_glosses_default_status"] = r["status"]
print(json.dumps(out, ensure_ascii=False, indent=1))
