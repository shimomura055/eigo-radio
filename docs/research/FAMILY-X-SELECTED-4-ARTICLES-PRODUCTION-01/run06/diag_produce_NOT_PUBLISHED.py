# DIAGNOSTIC ONLY (not published): proper_nouns = KP expressions only (title Title-Case words removed).
import sys
sys.path.insert(0, "C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/7eda59a9-ca6c-4f6c-9eb5-2b973c0ca046/scratchpad/fx06")
import er135_enduser_page_01 as E
orig = E.proper_nouns_for_run
def patched(run_dir, family, rows_by_level=None, meta=None):
    m = dict(meta or {}); m["topic_en"] = ""
    return orig(run_dir, family, rows_by_level, m)
E.proper_nouns_for_run = patched
sys.exit(E.main(sys.argv[1:]))
