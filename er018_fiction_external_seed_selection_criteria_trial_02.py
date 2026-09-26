# ============================================================
# er018_fiction_external_seed_selection_criteria_trial_02.py
# 管理ID: FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02
# ============================================================
# 目的: er018_fiction_external_story_seed_trial_01.py (Trial-01) で明らかに
# なった問題(候補選定がweb_search要約のみに基づき、実際の一次テキストを
# 読まずにStory Seed化していたため、生成されたStoryが一次テキストの内容と
# ほとんど無関係になるケースがあった -- 例: "The Open Gate")を踏まえ、本
# Trialでは:
#   (1) 一次テキストを実際にHTTP GET(直接fetch)で取得できることを必須Gateとし、
#       Sonnetが人手で実際に読んでから候補を再評価する(web_searchでの要約は
#       候補発見の補助に留め、Seed化の根拠にしない)。
#   (2) 4系統(01_life_history/02_historical/03_japanese_lit/04_world_lit)の
#       うち、前回採用作(Kind Lodge等)は再生成しない。
#   (3) Seed化は「オリジナル感のための機械的改変」を強制せず、忠実な再話・
#       現代化を許容する(尺調整のための簡略化のみ明記)。
#
# 本スクリプトが担当する範囲は Seed化(S-3)とStory本文生成(S-4)のみ。
# 候補調査・一次テキスト確認・権利確認(S-1/S-2)はSonnetがrequestsで直接
# 実施し、その結果(source_brief)を手動でselection.json相当として本スクリプト
# へ渡す(SEEDS辞書、下記)。API課金を伴う候補探索web_searchは本Trialでは
# 使用していない(直接HTTP GETのみ、$0)。
#
# Status: Trial専用、未承認draft実装(APPROVED_FOR_PRODUCTIONではない)。
# 到達上限: VALIDATED。Production Fiction仕様への反映は本タスクの対象外。
#
# 実行方法(root直下):
#   .venv/Scripts/python.exe er018_fiction_external_seed_selection_criteria_trial_02.py \
#       --out-dir er018_output/fiction_external_seed_selection_criteria_trial_02 \
#       --step seed --budget-jpy 60
#   ...--step story --budget-jpy 60
#   ...--step assemble
# ============================================================
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er003_v1_en_direct_vfl_01_generate as vfl01  # get_client()のみ再利用
import er018_fiction_story_dna_e_axis_redesign_01 as e_axis  # 共通ヘルパー再利用(read-only import)

load_dotenv()

THEME_TAG = "FICTION_EXTERNAL_SEED_SELECTION_CRITERIA_TRIAL_02"
MODEL_LUNA = routing.WRITER_MODEL  # "gpt-5.6-luna"
USD_JPY = e_axis.USD_JPY
PRICING_SNAPSHOT_PATH = e_axis.PRICING_SNAPSHOT_PATH

# ------------------------------------------------------------
# 5本のStory Seed対象(4系統、前回採用作は含まない)。
# source_briefはSonnetが実際に一次テキストをHTTP GETで取得し、自分の言葉で
# 書いたもの(引用の丸写しではない)。rights_statusは実際にfetchしたURL・
# 確認文言・確認日付。
# ------------------------------------------------------------
SEEDS = [
    {
        "key": "01_life_history_1",
        "label_en": "Real-life memoir / oral history",
        "label_ja": "実話・人生談",
        "title": "The water-pump moment (Helen Keller, \"The Story of My Life\")",
        "source_url": "https://www.gutenberg.org/ebooks/2397.txt.utf-8",
        "rights_status_quote": "Public domain in the USA. / \"This eBook is for the use "
                                 "of anyone anywhere in the United States and most other "
                                 "parts of the world at no cost and with almost no "
                                 "restrictions whatsoever.\"",
        "confirmed_date": "2026-09-26",
        "source_brief": (
            "This is a real, famous scene from Helen Keller's own autobiography (Project "
            "Gutenberg #2397, fetched and confirmed directly). Helen, deaf and blind since "
            "infancy, has just spent weeks learning to imitate finger-spelled words without "
            "understanding that they are words at all -- to her it is just a finger game. "
            "She keeps confusing the spelled words for \"mug\" and \"water.\" Frustrated, she "
            "seizes her new doll and smashes it on the floor, feeling only a child's blank "
            "satisfaction, no guilt. Her teacher then leads her outside to the well-house, "
            "puts one of Helen's hands under the pump's cold running water, and spells "
            "\"w-a-t-e-r\" into her other hand -- first slowly, then fast. Suddenly something "
            "clicks: Helen understands for the first time that the motions in her hand ARE "
            "the thing flowing over her other hand, that everything has a name, that this is "
            "language. She describes it as her soul waking up. Walking back to the house she "
            "learns many more words that same day, and when she reaches the hearth and finds "
            "the pieces of the broken doll, she feels real remorse and tries to put it back "
            "together -- for the first time in her life."
        ),
        "conversion_plan": (
            "Do NOT invent a different, generic scenario -- this is a real historical scene "
            "and should be kept as a faithful, simplified retelling of it, not converted into "
            "an unrelated modern situation. Keep the historical setting (a water pump / "
            "well-house, a rag doll) because it is part of what actually happened and is not "
            "an obstacle to A2 simplification. Tell it in the first person as Helen. Per this "
            "family's naming rule, only the protagonist may have a personal name (Helen); "
            "refer to the teacher as \"my teacher\" rather than by name. You may simplify or "
            "compress the surrounding chapter material (the weeks of meaningless finger-"
            "spelling before this scene, later chapters) but keep the core sequence intact: "
            "frustration -> breaking the doll -> the pump -> the word \"water\" suddenly "
            "meaning something -> walking back and learning more words -> finding the broken "
            "doll and feeling sorry. Around 300-350 words, first person, present-tense inner "
            "experience is fine."
        ),
    },
    {
        "key": "02_historical_1",
        "label_en": "Real historical anecdote",
        "label_ja": "実話・歴史的逸話",
        "title": "The lion attack (David Livingstone, \"Missionary Travels and Researches "
                 "in South Africa\")",
        "source_url": "https://www.gutenberg.org/ebooks/1039.txt.utf-8",
        "rights_status_quote": "Public domain in the USA. (Project Gutenberg ebook #1039)",
        "confirmed_date": "2026-09-26",
        "source_brief": (
            "This is a real, famous first-person account from David Livingstone's own "
            "memoir (Project Gutenberg #1039, fetched and confirmed directly). While hunting "
            "lions that were attacking a village's cattle with local men, Livingstone shoots "
            "a lion from about thirty yards and believes it is dead; while he is reloading, "
            "the lion suddenly springs on him from a height, catches his shoulder, and they "
            "fall to the ground together. The lion shakes him \"as a terrier dog does a rat\" "
            "-- and Livingstone notices, almost clinically, that the shock produces a strange "
            "dreamy calm with no pain and no terror, though he is fully conscious of "
            "everything happening (he compares it to a patient under chloroform who can see "
            "the operation but not feel the knife). The lion then turns to attack the man who "
            "is trying to shoot it (his gun misfires), then attacks a third man who tries to "
            "spear it, and only then finally dies from the earlier gunshot wounds. Livingstone "
            "is left with a permanently damaged arm (eleven tooth wounds, crushed bone) that "
            "affects him for the rest of his life."
        ),
        "conversion_plan": (
            "Keep this as a faithful, simplified retelling of the real event, first person, "
            "historical setting intact (hunting an attacking lion near a village, with local "
            "hunters). Do not invent an unrelated modern scenario. Per the naming rule, the "
            "unnamed first-person narrator does not need a personal name (the original text "
            "itself does not dwell on names); refer to the other men only by role (\"one of "
            "the men\", \"another hunter\") rather than by their real names (Mebalwe, etc.). "
            "Keep the core sequence: the hunt, the first shot, the sudden second attack while "
            "reloading, the strange calm during the attack (this psychological detail is the "
            "emotional core of the piece and should not be cut), the lion turning on the other "
            "men, its death, and the lasting injury. Around 300-350 words, first person."
        ),
    },
    {
        "key": "03_japanese_lit_1",
        "label_en": "Japanese literature (public domain)",
        "label_ja": "日本文学(青空文庫)",
        "title": "羅生門 Rashomon (Ryunosuke Akutagawa)",
        "source_url": "https://www.aozora.gr.jp/cards/000879/files/127_15260.html",
        "rights_status_quote": "Aozora Bunko hosts this work with full public-domain "
                                 "download files (txt/ebk/XHTML); author Ryunosuke Akutagawa "
                                 "died 1927-07-24 (card metadata), far past Japan's copyright "
                                 "term, matching Aozora's own stated policy that expired-"
                                 "copyright works require no permission to use.",
        "confirmed_date": "2026-09-26",
        "source_brief": (
            "This is Akutagawa's famous short story (Aozora Bunko, fetched and confirmed "
            "directly). A servant, just dismissed by his master in a famine- and disaster-"
            "stricken city, stands under the ruined Rashomon gate at dusk, undecided between "
            "starving honestly or becoming a thief. He climbs into the gate's tower (used to "
            "dump unclaimed corpses) to shelter for the night and finds an old woman pulling "
            "out the hair of a dead woman's corpse, strand by strand, to make a wig to sell. "
            "Disgusted, he draws his sword and confronts her. She begs him not to report her, "
            "explaining that the dead woman herself used to sell dried snake meat as dried "
            "fish to survive, and that she believes the dead woman would forgive her for doing "
            "something similarly necessary to live. Hearing this, the servant's hesitation "
            "vanishes -- he decides that if survival justifies her theft, it justifies his own "
            "-- and he strips the old woman of her clothes to sell, kicks her down, and "
            "vanishes into the night, becoming exactly the kind of person he had been afraid "
            "to become."
        ),
        "conversion_plan": (
            "Keep this as a faithful, simplified retelling of the real story -- the ruined "
            "gate, the famine-stricken city, and the corpse-filled tower are essential to the "
            "mood and moral logic, not obstacles to simplify away. No modernization needed. "
            "Neither character has a personal name in the original (\"the servant\", \"the old "
            "woman\"); keep it that way, which already matches this family's naming rule. Keep "
            "the core sequence: the servant's hesitation, discovering the old woman at her "
            "grim task, her justification, and his final choice to become a thief himself. "
            "You may simplify the historical/geographic scene-setting at the very start. "
            "Third person is fine (the original is third person). Around 300-350 words."
        ),
    },
    {
        "key": "03_japanese_lit_2",
        "label_en": "Japanese literature (public domain)",
        "label_ja": "日本文学(青空文庫)",
        "title": "走れメロス Run, Melos! (Osamu Dazai)",
        "source_url": "https://www.aozora.gr.jp/cards/000035/files/1567_14913.html",
        "rights_status_quote": "Aozora Bunko hosts this work with full public-domain "
                                 "download files; author Osamu Dazai died 1948-06-13 (card "
                                 "metadata), and Aozora's own guide states that works whose "
                                 "copyright has expired require no permission to use.",
        "confirmed_date": "2026-09-26",
        "source_brief": (
            "This is Dazai's famous short story (Aozora Bunko, fetched and confirmed "
            "directly), itself a retelling of a much older legend. Melos, a shepherd, is "
            "arrested in a city ruled by a tyrant who has been executing people he merely "
            "suspects of disloyalty, without trial. Melos denounces the tyrant to his face "
            "and is sentenced to death, but asks for three days' delay to go home and let his "
            "sister marry, leaving his best friend as a hostage who will be executed in his "
            "place if Melos does not return in time. Melos rushes home, sees the wedding "
            "through, and races back -- but is stopped by a flooded river, then by bandits, "
            "and finally collapses from exhaustion and despair, briefly tempted to simply give "
            "up and let his friend die in his place. He revives by drinking from a spring, "
            "recommits to keeping his promise out of trust rather than mere duty, and runs the "
            "final distance as the sun is setting, arriving just as the execution is about to "
            "begin. The friend, who never doubted him, is released; the tyrant, moved by their "
            "mutual trust, is changed by what he has witnessed."
        ),
        "conversion_plan": (
            "Keep this as a faithful, simplified retelling of the real story -- the kingdom/"
            "tyrant setting is essential to the stakes (an execution, not a minor deadline) "
            "and does not need modernizing. Per the naming rule, only the protagonist keeps a "
            "personal name (Melos); refer to the other two men as \"his friend\" and \"the "
            "king\"/\"the ruler\" rather than by their original names. Keep the core race-"
            "against-time sequence and, especially, the moment of despair and temptation to "
            "give up partway through, and the moment of recommitment -- these are the "
            "emotional core, not just plot mechanics. You may compress or drop minor obstacles "
            "(exact number of river/bandit episodes) as long as the shape (obstacles -> near-"
            "collapse -> renewed resolve -> arriving just in time) survives. Around 300-350 "
            "words, third person is fine."
        ),
    },
    {
        "key": "04_world_lit_1",
        "label_en": "World literature (public domain)",
        "label_ja": "世界文学",
        "title": "The Bet (Anton Chekhov)",
        "source_url": "https://www.gutenberg.org/ebooks/55283.txt.utf-8",
        "rights_status_quote": "Public domain in the USA. (Project Gutenberg ebook #55283, "
                                 "\"The Bet and Other Stories\" by Anton Tchekhov)",
        "confirmed_date": "2026-09-26",
        "source_brief": (
            "This is Chekhov's famous short story (Project Gutenberg #55283, fetched and "
            "confirmed directly). At a party fifteen years ago, a banker argued that capital "
            "punishment is more humane than life imprisonment; a young lawyer disagreed and, "
            "in a reckless argument, bet the banker two million rubles that he could survive "
            "fifteen years of total solitary confinement (in a garden lodge, with books, wine, "
            "and an organ, but no human contact) rather than be executed. The lawyer moves "
            "into the lodge that night. Over fifteen years his reading changes dramatically "
            "-- light novels, then classics and languages, then, in the final years, the "
            "Gospels and philosophy/religious texts -- while the banker, now old and ruined by "
            "bad investments, realizes paying the bet will finish him financially and secretly "
            "plans to kill the lawyer the night before the deadline to avoid paying. When the "
            "banker sneaks in to do it, he finds the lawyer asleep at his desk, aged and "
            "thin, with a letter he has written: the letter renounces the two million rubles "
            "entirely, saying his fifteen years of reading have taught him to despise the "
            "worldly goods he once bet everything on, and that he will deliberately leave five "
            "hours before the deadline to void the bet on his own terms. Ashamed, the banker "
            "leaves without harming him; the next morning the watchman confirms the lawyer has "
            "indeed climbed out and vanished."
        ),
        "conversion_plan": (
            "Keep this as a faithful, simplified retelling of the real story -- the wager and "
            "the isolation are the entire point and should not be modernized into something "
            "like a reality-TV concept, since that would change what the ending means. Neither "
            "character has a personal name in the original (\"the banker\", \"the lawyer\"); "
            "keep it that way, which already matches this family's naming rule. You may "
            "heavily compress the fifteen years (a few sentences moving through phases of what "
            "he read/became) as long as the shape survives: the reckless bet, the long "
            "isolation and the lawyer's inner transformation, the banker's plan to murder him "
            "to avoid paying, discovering the letter instead, and the lawyer's voluntary, "
            "principled forfeit. Third person is fine (the original is third person). Around "
            "300-350 words."
        ),
    },
]


# ------------------------------------------------------------
# S-3 Story Seed化(系統ごと1 call、json_schema strict)。SEED_JSON_SCHEMA/
# SEED_DEVELOPER_MESSAGE/SEED_USER_TEMPLATEはTrial-01から意味を変えずに再掲
# (Trial-01と手法を揃えて比較可能にするため)。
# ------------------------------------------------------------
SEED_DEVELOPER_MESSAGE = (
    "You help an English-learning magazine's Fiction team turn a real, rights-cleared "
    "source into a reusable \"Story Seed\": an abstraction that keeps the elements needed "
    "to write a new short-story version of the SAME real event, and explicitly discards "
    "only what does not fit a short A2-level piece (minor subplots, excess names, excess "
    "historical/technical detail). Unlike a from-scratch fictional story, this is not "
    "supposed to be a totally new, unrelated plot -- it should still recognizably be a "
    "retelling of the real source event. This is not a summary for readers -- it is an "
    "internal planning document. Do not quote long passages from the source; describe "
    "things in your own words."
)

SEED_USER_TEMPLATE = """[Source brief -- written by the editor, in their own words, not quoted from
the original]
{source_brief}

[Conversion plan -- written by the editor]
{conversion_plan}

[Task -- produce a Story Seed]
1. original_summary: 3 to 5 sentences, in your own words, summarizing what actually
   happened/what the source is about.
2. seed_elements: up to 6 short bullet-style strings -- the elements that must carry over
   into the new story so that it is still recognizably a retelling of this real event
   (key situation, turning point, emotional core, any detail the conversion plan says must
   not be cut).
3. discarded_elements: short strings -- proper names, minor subplots, or excess period/
   technical detail that should be simplified away or dropped for an A2-level short piece.
4. conversion_plan: 2 to 4 sentences describing how to turn this into an English-learning
   short story: whether to keep or modernize the setting, first-person or third-person,
   and roughly how long/what level (use the editor's conversion plan above as the basis,
   restated in your own words)."""

SEED_JSON_SCHEMA = {
    "name": "fiction_external_story_seed",
    "schema": {
        "type": "object",
        "properties": {
            "original_summary": {"type": "string"},
            "seed_elements": {
                "type": "array", "minItems": 2, "maxItems": 6,
                "items": {"type": "string"},
            },
            "discarded_elements": {
                "type": "array", "minItems": 1, "maxItems": 6,
                "items": {"type": "string"},
            },
            "conversion_plan": {"type": "string"},
        },
        "required": [
            "original_summary", "seed_elements", "discarded_elements",
            "conversion_plan",
        ],
        "additionalProperties": False,
    },
    "strict": True,
}


def call_seed(client, seed_spec: dict) -> dict:
    stage = f"seed_{seed_spec['key']}"
    user_message = SEED_USER_TEMPLATE.format(
        source_brief=seed_spec["source_brief"],
        conversion_plan=seed_spec["conversion_plan"],
    )
    kwargs = dict(
        model=MODEL_LUNA,
        reasoning={"effort": "medium"},
        input=[
            {"role": "developer", "content": SEED_DEVELOPER_MESSAGE},
            {"role": "user", "content": user_message},
        ],
        text={"format": {"type": "json_schema", **SEED_JSON_SCHEMA}},
    )
    with cl.logging_context(THEME_TAG, stage):
        response = client.responses.create(**kwargs)
    if response.model != MODEL_LUNA:
        raise RuntimeError(
            f"STOP条件該当: actual model_idが要求モデルと異なる(stage={stage}, "
            f"requested={MODEL_LUNA}, actual={response.model})")
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError(f"{stage}: 応答が空です")
    parsed = json.loads(text)
    return {"parsed": parsed, "user_message": user_message, "model": response.model,
            "response_id": response.id}


def step_seed(out_dir: str, budget_jpy: float) -> None:
    log_path = f"{out_dir}/raw_usage_log.jsonl"
    cl.install(log_path)
    budget_guard("start_seed", out_dir, log_path, budget_jpy)
    client = vfl01.get_client()

    for seed_spec in SEEDS:
        sys_dir = f"{out_dir}/stories/{seed_spec['key']}"
        result = call_seed(client, seed_spec)
        seed = dict(result["parsed"])
        seed["rights_status"] = {
            "url": seed_spec["source_url"],
            "confirmation_quote": seed_spec["rights_status_quote"],
            "confirmed_date": seed_spec["confirmed_date"],
        }
        seed["title"] = seed_spec["title"]
        e_axis.save_json(f"{sys_dir}/seed.json", seed)
        e_axis.save_json(f"{sys_dir}/seed_api_meta.json", {
            "developer_message": SEED_DEVELOPER_MESSAGE,
            "user_message": result["user_message"], "model": result["model"],
            "response_id": result["response_id"],
        })
        print(f"[step_seed][{seed_spec['key']}] DONE.")
        budget_guard(f"after_seed_{seed_spec['key']}", out_dir, log_path, budget_jpy)

    print("[step_seed] ALL DONE.")


# ------------------------------------------------------------
# S-4 Story本文生成(Trial-01のSTORY_PROMPT_TEMPLATEを逐語で再利用)
# ------------------------------------------------------------
STORY_PROMPT_TEMPLATE = """[Story Seed -- inspired by a real, rights-cleared source, freely reimagined;
this is NOT a summary to reproduce, just raw material]
{seed_elements_block}

[How to convert it]
{conversion_plan}

[Common principles for this story family]
{common_principles}

[Your single job]
Write a short story inspired by the Story Seed above. Make a reader genuinely feel \
something, want to keep reading, and feel some excitement and a little tension along \
the way. Do not follow any fixed structure, fixed number of scenes, fixed number of \
emotional turns, or a fixed ending shape -- choose whatever narrative shape makes THIS \
Story Seed land most strongly. Do not just retell the original source with no changes at \
all, but also do not force superficial changes for their own sake -- a faithful, simplified \
retelling of the real event is welcome here.

[Characters -- keep it simple]
Use 1 or 2 characters as the core of the story; {max_characters} at the absolute most \
if truly needed. Only the main character (the protagonist) may be given a personal \
name. Every other person should be referred to through their relationship to the main \
character (for example: her mother, his father, her friend, their daughter, his \
neighbor) instead of a separate name. Do not add named characters that are not \
necessary for the story.

[Length and level]
- Write for an A2-level English learner: short, clear sentences, common vocabulary, \
simple hedging like "might"/"could"/"If ... , ...".
- Target length for the reader-facing text is about {word_target} words (roughly \
{range_low}-{range_high} words is fine).

[Listening-friendliness -- an editorial goal, not a hard rule]
This article will also be listened to as audio. Try to keep it easy for a listener to \
follow: avoid introducing more named people than necessary, avoid jumping between many \
different times or places, avoid long strings of abstract explanation, and try to keep \
it reasonably clear at each point whose perspective the reader/listener is in.

Write the article now. Do not add a title unless it helps the story -- if you do, keep \
it short."""


def build_story_prompt(seed: dict) -> str:
    seed_elements_block = "\n".join(f"- {e}" for e in seed["seed_elements"])
    return STORY_PROMPT_TEMPLATE.format(
        seed_elements_block=seed_elements_block,
        conversion_plan=seed["conversion_plan"],
        common_principles=e_axis.COMMON_PRINCIPLES,
        max_characters=e_axis.MAX_CHARACTERS, word_target=e_axis.WORD_TARGET,
        range_low=e_axis.WORD_ACCEPTABLE_RANGE[0],
        range_high=e_axis.WORD_ACCEPTABLE_RANGE[1],
    )


def step_story(out_dir: str, budget_jpy: float) -> None:
    log_path = f"{out_dir}/raw_usage_log.jsonl"
    cl.install(log_path)
    budget_guard("start_story", out_dir, log_path, budget_jpy)
    client = vfl01.get_client()

    for seed_spec in SEEDS:
        sys_dir = f"{out_dir}/stories/{seed_spec['key']}"
        seed = e_axis.load_json(f"{sys_dir}/seed.json")
        story_model = routing.require_model_or_override(
            "A2_WRITER", routing.WRITER_MODEL,
            override_reason="FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02: 外部Public "
                             "Domainソースをprimary-text確認済みでSeed化した短編生成に"
                             "A2_WRITER Approved Model(Luna)を転用(新規process未定義、"
                             "コスト影響なし、DEV/Trial限定)")
        prompt = build_story_prompt(seed)
        e_axis.save_text(f"{sys_dir}/story_prompt.txt", prompt)

        def _call():
            with cl.logging_context(THEME_TAG, f"story_{seed_spec['key']}"):
                return e_axis.generate_story(client, story_model, "high", prompt)

        story_result, attempts = e_axis.call_with_retry(_call, max_attempts=2)
        e_axis.save_text(f"{sys_dir}/story.md", story_result["raw_text"].strip() + "\n")
        e_axis.save_json(f"{sys_dir}/api_meta.json", {
            "model": story_result["model"], "response_id": story_result["response_id"],
            "effort": "high", "attempts": attempts,
        })
        word_count = len(story_result["raw_text"].split())
        print(f"[step_story][{seed_spec['key']}] DONE. word_count={word_count} "
              f"model={story_result['model']}")
        budget_guard(f"after_story_{seed_spec['key']}", out_dir, log_path, budget_jpy)

    print("[step_story] ALL DONE.")


# ------------------------------------------------------------
# 費用計算(Luna token費用のみ。本Trialではweb_search未使用)
# ------------------------------------------------------------
def load_pricing() -> dict:
    with open(PRICING_SNAPSHOT_PATH, encoding="utf-8") as f:
        snapshot = json.load(f)
    prices = {}
    ws_price = None
    for entry in snapshot["prices"]:
        if entry.get("model") == "gpt-5.6-luna":
            prices[entry["meter"]] = entry["price"]
        if entry.get("meter") == "web_search_call":
            ws_price = entry["price"]
    prices["web_search_call"] = ws_price
    return prices


def compute_cost_jpy(log_path: str) -> dict:
    if not os.path.exists(log_path):
        return {"total_usd": 0.0, "total_jpy": 0.0, "record_count": 0}
    pricing = load_pricing()
    total_usd = 0.0
    record_count = 0
    ws_call_total = 0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("theme") != THEME_TAG:
                continue
            record_count += 1
            if not rec.get("success", True):
                continue
            ws_calls = rec.get("web_search_call_count") or 0
            ws_call_total += ws_calls
            if pricing.get("web_search_call"):
                total_usd += (ws_calls / 1000) * pricing["web_search_call"]
            if rec.get("model_id") != "gpt-5.6-luna":
                continue
            input_tokens = rec.get("input_tokens") or 0
            cached = rec.get("cached_input_tokens") or 0
            output_tokens = rec.get("output_tokens") or 0
            non_cached_input = max(input_tokens - cached, 0)
            total_usd += (non_cached_input / 1_000_000) * pricing["input_tokens"]
            total_usd += (cached / 1_000_000) * pricing["cached_input_tokens"]
            total_usd += (output_tokens / 1_000_000) * pricing["output_tokens"]
    return {
        "total_usd": round(total_usd, 6), "total_jpy": round(total_usd * USD_JPY, 2),
        "record_count": record_count, "web_search_call_total": ws_call_total,
    }


def budget_guard(stage_label: str, out_dir: str, log_path: str, hard_cap_jpy: float) -> dict:
    cost = compute_cost_jpy(log_path)
    print(f"[budget_guard][{stage_label}] 累計={cost['total_jpy']} JPY (上限{hard_cap_jpy})")
    if cost["total_jpy"] > hard_cap_jpy:
        raise RuntimeError(
            f"[budget_guard][{stage_label}] 累計{cost['total_jpy']} JPYが上限"
            f"{hard_cap_jpy} JPYを超過しました。STOP(以降のAPI呼び出しは行わない)。")
    return cost


# ------------------------------------------------------------
# Step: assemble
# ------------------------------------------------------------
def step_assemble(out_dir: str) -> None:
    parts = [
        "# FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02 -- stories_all.md\n",
        "Trial専用、Production採用ではない。最大Status: VALIDATED。\n",
    ]
    for seed_spec in SEEDS:
        sys_dir = f"{out_dir}/stories/{seed_spec['key']}"
        seed = e_axis.load_json(f"{sys_dir}/seed.json")
        story = e_axis.load_text(f"{sys_dir}/story.md")
        parts.append(f"\n## {seed_spec['key']} -- {seed_spec['label_en']} "
                      f"({seed_spec['label_ja']})\n")
        parts.append(f"**Source**: {seed_spec['title']} -- {seed_spec['source_url']}\n")
        parts.append(f"**Rights**: {seed['rights_status']['confirmation_quote']} "
                      f"(confirmed {seed['rights_status']['confirmed_date']})\n")
        parts.append(f"**Seed elements**: {'; '.join(seed['seed_elements'])}\n")
        parts.append("```\n" + story.strip() + "\n```\n")
    e_axis.save_text(f"{out_dir}/stories_all.md", "\n".join(parts))

    log_path = f"{out_dir}/raw_usage_log.jsonl"
    final_cost = compute_cost_jpy(log_path)
    e_axis.save_json(f"{out_dir}/cost.json", final_cost)
    print(f"[step_assemble] DONE -> {out_dir}/stories_all.md, cost={final_cost}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--step", required=True,
                         choices=["seed", "story", "assemble"])
    parser.add_argument("--budget-jpy", type=float, default=60.0)
    args = parser.parse_args()

    if args.step == "seed":
        step_seed(args.out_dir, args.budget_jpy)
    elif args.step == "story":
        step_story(args.out_dir, args.budget_jpy)
    elif args.step == "assemble":
        step_assemble(args.out_dir)


if __name__ == "__main__":
    main()
