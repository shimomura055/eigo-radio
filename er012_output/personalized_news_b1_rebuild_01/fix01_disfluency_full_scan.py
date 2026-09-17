# ============================================================
# er012_output/personalized_news_b1_rebuild_01/fix01_disfluency_full_scan.py
# 管理ID: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01-FIX-01
# ============================================================
# 目的: 委任文5節(a)「local faster-whisper verbatim(er008_disfluency_qa_18.
# transcribe_verbatim)で全segmentの語単位転写→canonicalとの欠落/重複検出」を、
# 14記事固有segment全件(topic_intro/preview/comment_1-4/point_one_heading/
# point_two_heading/point_one/point_two/full_story_part1/full_story_part2/
# tension_reflection/in_one_line)に対して実施する(パイプライン内で既に
# disfluency_qa=Trueだったsegmentも含め、全件を対象に再確認)。
from __future__ import annotations

import json
import sys

sys.path.insert(0, ".")
import er008_disfluency_qa_18 as qa

NARRATION_DIR = "er012_output/personalized_news_b1_rebuild_01/audio/b1_2v_fix01/b1b/narration"
OUT_PATH = "er012_output/personalized_news_b1_rebuild_01/audio/b1_2v_fix01/b1b/audit_fix01/disfluency_full_scan.json"

SEGMENTS = [
    "topic_intro", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
    "point_one_heading", "point_two_heading", "point_one", "point_two",
    "full_story_part1", "full_story_part2", "tension_reflection", "in_one_line",
]

CANONICAL = {
    "topic_intro": "Today's topic is One Feed, Two Very Different Experiences.",
    "preview": ("This episode looks at why the same personalized news feed can feel helpful to one "
                "reader and troubling to another. We will explore the balance between getting relevant "
                "news quickly and seeing how the feed shapes what appears. By the end, you will be able "
                "to ask a clearer question: what does personalization give us, and what might it hide?"),
    "comment_1": "As you listen, notice what each person values and what each person worries about.",
    "comment_2": ("Now, listen to different voices speak about this question from their own experience. "
                  "Each voice will offer a different view."),
    "comment_3": ("You have now heard two different experiences of a personalized news feed. Rather than "
                  "deciding which view is right, let us ask why the same situation can feel different to "
                  "different people. The next section looks more closely at that question."),
    "comment_4": ("So the question is not only who is right. We can also ask what makes the same "
                  "situation feel helpful to one person and restrictive to another."),
    "point_one_heading": "One Voice: The reader who relies on his personalized feed.",
    "point_two_heading": "Another Voice: The reader who worries her feed is closing in.",
    "point_one": ("On my commute, I open Google News’s “For you” page and find stories about "
                  "subjects I follow. The feed can also reflect my activity on Google services and YouTube. "
                  "I can ask for more or fewer similar stories, or hide a source. That gives me some "
                  "control. I am busy, and personalization gives me a quick, relevant path through a huge "
                  "amount of news. Sometimes it even feels less biased than a human editor. I do not want "
                  "to sort through everything myself."),
    "point_two": ("Some mornings, I scroll through my feed and notice the pattern: another post with the "
                  "same kind of argument, then another. I want to know why these stories are in front of "
                  "me, but I cannot see the full rules behind the ranking. I keep thinking about how "
                  "platforms can adjust it around engagement and advertising goals. I cannot change those "
                  "deeper settings myself. I want news that helps me understand views unlike my own, not "
                  "only views that already fit. If my window on the world is narrowing, I may notice only "
                  "after it has happened."),
    "full_story_part1": ("On a morning commute, one reader opens a feed and finds stories that fit the "
                         "few minutes he has. Later, another scrolls through a feed and notices the same "
                         "kinds of views appearing again and again."),
    "full_story_part2": ("Both use systems that rank news based on past interests and behavior. The "
                         "question is not simply whether personalized news is good or bad. It is what "
                         "each person gains—and fears losing."),
    "tension_reflection": ("Both readers want what they see to help them understand the world and manage "
                           "daily life. Neither is simply wrong. But the stakes are different: one is "
                           "trying to keep up with relevant news in limited time; the other fears being "
                           "quietly locked into a narrow view. The same kind of ranking feels like choices "
                           "and settings to one, but hidden rules to the other. One feels some power to "
                           "adjust it, while the other feels forced to accept the deeper system."),
    "in_one_line": ("The deeper issue is not only what appears in a feed. It is whether convenience can "
                    "feel like control when the path to those choices is partly hidden. Personalized news "
                    "becomes a question of place: is the reader shaping what appears, or riding a route "
                    "set elsewhere? The tension is between access and visibility, not simply good and bad "
                    "news."),
}


def word_count(text: str) -> int:
    return len(text.split())


def main() -> None:
    results = {}
    for name in SEGMENTS:
        wav_path = f"{NARRATION_DIR}/{name}.wav"
        words = qa.transcribe_verbatim(wav_path, language="en")
        reps = qa.detect_adjacent_word_repetition(words)
        transcript = " ".join(w["text"] for w in words).strip()
        canon = CANONICAL[name]
        results[name] = {
            "wav_path": wav_path,
            "asr_word_count": len(words),
            "canonical_word_count": word_count(canon),
            "adjacent_repetition_count": len(reps),
            "adjacent_repetitions": reps,
            "transcript": transcript,
        }
        print(f"[FIX-01-DISFLUENCY-SCAN] {name}: asr_words={len(words)} canonical_words={word_count(canon)} "
              f"repeats={len(reps)}")
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"[FIX-01-DISFLUENCY-SCAN] DONE -> {OUT_PATH}")


if __name__ == "__main__":
    main()
