# VERIFY_01 受入材料(委任_03、assemble BLOCK時点の中間版。最終版は承認後のページ公開で完成させる)
## 確定内容の逐語一致(20件)
- payload(`payloads/ai_island_temple__{a2,b1b}__user_confirmed_01.json`)の10件×2 levelと確定record(`<run>/{lv}/key_phrases/confirmed_selection.json`)の items+unconsumed: candidate_id集合一致、区分・ja_gloss不一致 0(KP_CONFIRM_02)。
- 下流artifact: KP artifact(`keywords_canonicalized.json`) Std①3件/Adv①3件が record cat1と英語・訳とも一致(順序含む)。TTS結果のKP音声(Std english+japanese_meaning)も同一テキスト。Adv Part 1(`part1_vocabulary_expressions.json`)5行の英語・訳・順序が record items(①3+②2)と一致(carry over/call on/take a detour/card to play/obstacle)。
- `unconsumed[]`(黙って捨てない): Std ③5件+Std②2件、Adv ③5件。完成版ページに「③・Std②は後続反映予定」注記を入れる(builder実装済み、未公開)。
- 文法: Std/Adv 0件確定(`confirmed_grammar.json` count=0、`part2_result.json` status=ZERO)。
## 本文
article.md sha256 Std `90c66293…c5f10`/Adv `a2951b9b…89768`=承認済み(scaffold_article_sha256.json・run_ai_01・kp75と一致)。本文・KP再生成 0。
## Gate
tts: Std 19/19・Adv 18/18 OK、HR Lock 0、KP音声(Std english/japanese_meaning/Adv english/explanation/phrase_repeat)全OK、PASS_WITH_WARNING等は `pass_with_warning_listening_list.json`。assemble: **M3 Style Gate BLOCK**(両level `full_story_part1_k2`、HR_FULL_STORY_PART1_K2_01.md)。player: 確定<->KP artifact<->TTS<->study_textの整合検査(G1〜G4相当)通過(rc=0)。
## 未完(承認待ち)
最終音声(assemble)・最終試聴ページ・ページ標準検査・公開HTTP確認。
