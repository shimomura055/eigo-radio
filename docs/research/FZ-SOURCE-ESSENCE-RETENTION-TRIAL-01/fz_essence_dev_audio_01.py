# -*- coding: utf-8 -*-
"""FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_02 Phase 1c: Adv音声化のDEV呼び出しwrapper(Trial専用)。

Production runner(er026_family_z_fiction_production_runner_01.py)を **ファイル無変更のままimportし、メモリ上でのみ**
(1) 出力root/seed dir/pages dirをDEVへ差替え (2) LEVELSをAdvのみ(b1b)へ限定 して `main()` を呼ぶ。
既存の正式TTS/Gate/Assembly経路・STOP/予算guard・retry/fallbackはそのまま働く(迂回なし)。公開ページ(user_test/family_z_*)には書かない。
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import er026_family_z_fiction_production_runner_01 as R   # noqa: E402  (import only)

DEV_ROOT = "er026_output/family_z_dev_trials/fz_essence_01"
DEV_SEEDS = {"the_tell_tale_heart": "docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/dev_seed/the_tell_tale_heart"}


def install(story: str):
    pages = f"{DEV_ROOT}/{story}/pages_trial"
    R.E2E_RUN_ROOT = DEV_ROOT
    orig_post = R.E2EContext.__post_init__

    def post(self):
        orig_post(self)
        self.run_root = DEV_ROOT
        self.pages_dir = pages

    R.E2EContext.__post_init__ = post
    seed = DEV_SEEDS[story]
    R.E2EContext.seed_dir = property(lambda self: seed)
    R.LEVELS = ("b1b",)


if __name__ == "__main__":
    story = "the_tell_tale_heart"
    install(story)
    sys.exit(R.main(sys.argv[1:]))
