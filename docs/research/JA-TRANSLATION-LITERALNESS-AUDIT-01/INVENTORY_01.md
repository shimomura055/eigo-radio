# 調査③ 棚卸し (INVENTORY_01)

管理ID=JA-TRANSLATION-LITERALNESS-AUDIT-01 / 委任_01B / 2026-10-31。調査のみ・API 0・LLM呼出0・SSOT編集0。根拠は origin/main(013d0fab2)のsparse worktreeのコード読取と、公開済み10記事の `article.json`(`ev01/pairs_all_01.jsonl`に全件抽出)。Family X/Y/Z × Std/Adv で「英語に対応する日本語訳」が表示される箇所を列挙する(説明文そのものは除外し、解説に埋め込まれた対訳は別行)。

## 0. 結論(先に)
1. 日本語訳の「出所」は4系統: (a)X=R2日本語台本をそのまま訳として表示(`approved_ja_manuscript`)、(b)Y=Voiceの日本語原稿をそのまま表示(`approved_ja_original_in_dev_page`)、(c)End Userページ生成時に英文からLLM翻訳(`generated`、Z本文+X/Y Advの補助部分+X Std In One Line)、(d)学習項目(KP/Word/文法/語彙)はそれぞれの専用生成工程。
2. **(a)(b)は「英語を日本語に訳した」ものではなく、「日本語が先にあり、英語がその忠実英訳(Adv)→簡易化(Std)」という逆向き**(X: `er012_e_family_entertainment_two_level_runner_01.py:395`、Y: `er121_family_y_runner_01.py:388-400`)。画面ではこの日本語原稿が「英語の訳」として並ぶ。
3. **StdとAdvで同じ日本語原稿を共有**(X: revision2.md、Y: 同一Voice原稿)。英文はStdがAdvから簡易化され文が分割されるため、Stdでは英文N文↔日本語1文の統合が構造的に起きる(実データ: COMPARISON_01)。
4. **配線漏れ(検査の適用範囲の非対称)**: 対訳照合(LLM校閲・数値照合・文結合検査)は`generated`にだけあり、`approved_*`には無い。詳細は§2。

## 1. 棚卸し表(22行)
列: 生成元 / 生成方式・module / 適用Prompt(意訳・要約を許す文言の有無) / 検査 / 正式Production経路 / 適用Family・Level / `ja_source`値。file:lineは origin/main(013d0fab2)基準。

| # | 表示箇所(訳種別) | 生成元 | 生成方式・module(file:line) | 適用Prompt(file:line)/意訳許容文言 | 検査方式(file:line) | 正式Production経路(hook) | 適用Family/Level | `ja_source` |
|---|---|---|---|---|---|---|---|---|
| 1 | **X Std 本文(Full Story Part1-3)** | R2日本語台本(翻訳ではない) | 日本語Writer Original→R1→R2: `er019_family_x_ja_writer_o_r1_r2_01.py`(冒頭1-25)。表示側は`er135_enduser_page_01.py:614 load_x_manuscript`/`:631 attach_translations`(同一段落listをStd/Advに付与)/`:1804 find_x_ja_manuscript`(revision2>revision1>original)。英文=Adv英文からの簡易化`er003_v1_n3_01_standard_a2_generate.py:541 generate_family_x_standard_a2_no_heading` | JA台本=娯楽性を高める改稿(R1/R2、翻訳ではない)=**そもそも対訳規範なし**。英文側Std=v5簡易化Prompt | `attach_translations :636-639`(`ENDUSER_JA_PARAGRAPH_MISMATCH`)は**段落数一致のみ**(不一致=STOP)。文単位の対訳照合なし。連動ハイライトの`ja_align`(`er135_enduser_align_01.py:36-60` PARAMS: cos>=0.50等)は**対応づけであって忠実性検査ではない**(不成立の群はnull=訳非表示、`:607-619`) | `er019_family_x_listening_page_01.py:258-262 build_enduser_after_page`→`eu.hook_run(…ja_manuscript=find_x_ja_manuscript())` | X Std | `approved_ja_manuscript` |
| 2 | **X Adv 本文** | 同上(Stdと**同一**のR2台本) | 英文=R2の忠実英訳: `er012_e_family_entertainment_two_level_runner_01.py:395`→`er003_v1_n3_01_advanced_adaptation_generate.py:522-560 FAMILY_X_FAITHFUL_TRANSLATION_INSTRUCTION` | 英訳側: 「staying as close to the original as natural English allows」「Do not add/remove any fact…same paragraph structure」(:522-535)=忠実方針。JA側は上記1と同じ | 同上。英訳の段落数のみ`er012_e_family_entertainment_two_level_runner_01.py:282 _family_x_ensure_split_or_paragraph_retry`で検査。旧Fact Checker撤去済み(CURRENT_SPEC.md:1405付近、2026-10-10) | 同上 | X Adv | `approved_ja_manuscript` |
| 3 | **Y Std 本文(Voice発言)** | Voice日本語原稿(dev page内、翻訳ではない) | JA: Voice生成`er121_prompts/voice_generate_02.txt`。結合: `er135_enduser_page_01.py:644-657`(ja_blocks→`split_y_article`と空白除去一致検査)。英文=Advから簡易化`er121_family_y_runner_01.py:396-400`→`er003_v1_n3_01_standard_a2_generate.py:541` | Voice生成Prompt=「話者の語り」を生成(翻訳ではない) | `_ws(ysegs[sid]) != _ws(paras)`(承認済み原稿との**同一性**のみ、`:650-655 ENDUSER_JA_MISMATCH`)。対訳照合なし。`check_y_article`(`er121_family_y_structure_01.py:274`)=段落数・行数の構造契約のみ | `er121_family_y_runner_01.py:1383-1395 _build_enduser_page`(`y_article_ja=_ja_path`) | Y Std | `approved_ja_original_in_dev_page` |
| 4 | **Y Adv 本文** | 同上(Stdと同一原稿) | 英文=忠実英訳`er121_family_y_runner_01.py:388-394`→`generate_family_x_faithful_translation`(:522-560) | 同2 | 同3 | 同3 | Y Adv | `approved_ja_original_in_dev_page` |
| 5 | **Z Std 本文** | 英文からLLM翻訳(End User生成時) | `er135_enduser_page_01.py:839 generate_missing_translations`→`er135_enduser_translate_01.py:491 translate_part`(文ID付き、段落=fail-closed、cache `ja_generated.json`) | `er135_enduser_translate_01.py:38-48 TRANSLATE_HEAD`: 「意味を正確に訳す。意味を変えず、**情報の追加・省略をしない**。平易で読みやすい自然な日本語」**意訳・要約を許す文言なし**。番号1つに訳1つ(統合禁止)(:43) | 数値照合`:259`、構造検査`:291`(文結合疑い`_terminals_ja>_en+1`)、**LLM対訳校閲**`:56-67 VERIFY_HEAD`+`:375 parse_verify`(意味反転/数値/固有名/欠落・追加で不合格→1回再翻訳→fail-closed) | `er026_family_z_fiction_production_runner_01.py:2778-2788 _build_enduser_page`→`hook_run(…"z")` | Z Std | `generated` |
| 6 | **Z Adv 本文** | 同上 | 同5 | 同5 | 同5 | 同5 | Z Adv | `generated` |
| 7 | X Std In One Line | 英文からLLM翻訳 | `generate_missing_translations`(:839) | 同5 | 同5 | 同1のhook(`hook_run`既定`translate_llm=AUTO`) | X Std | `generated` |
| 8 | X Adv In One Line | 同上 | 同上 | 同5 | 同5 | 同1 | X Adv | `generated` |
| 9 | Adv Preview(X/Y/Z) | 同上 | 同上。asset rev01-h以降でPreviewを描画(`er135_enduser_rules_01.py:22 ASSET_TRANSLATION_KINDS`) | 同5 | 同5 | 各Family hook | X/Y/Z Adv | `generated` |
| 10 | Adv Comment 1〜4(X/Y/Z) | 同上 | 同上 | 同5 | 同5 | 各Family hook | X/Y/Z Adv | `generated` |
| 11 | Std KP「日本語の意味」(`kp_ja`) | KP選定段のLLM(japanese_gloss)→最終KP基準で再整合 | `er003_key_words_gloss_alignment.py`(冒頭1-30、再整合は`MAX_GLOSS_ALIGNMENT_ATTEMPTS=2`)。選定Prompt`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt` | `:17`「短く自然な日本語グロス」`:19`「**直訳調**…過度に硬い…を避け」`:21`「平易な言い換えだけの一文」=**言い換え(意訳)を許す/促す文言あり** | 同ファイル構造検査+gloss再整合(括弧禁止等)。語義と英文の対訳照合なし | X/Y/Z各runner(KP段) | X/Y/Z Std | (なし。`kp_ja`) |
| 12 | 「覚えておきたい表現」本文下線gloss(`glossary`)、dev pageの`lk-meaning` | 11と同じ`japanese_gloss`/③本文中の意味pool | `er135_enduser_page_01.py:711 build_glossary`(語形吸収で下線に対応づけ) | 11に同じ | 対応度`_gl_score`>=0.8(`:680 _gl_score`/`:693 _term_in_display_body`)。訳の忠実性は見ない | End User生成 | X/Y/Z Std+Adv | (なし。`glossary`) |
| 13 | Vocabulary & Expressions「本文中の意味」(見出し語の訳) | 11と同じgloss | 同12。`er128_kp_confirmed_content_01.py`でユーザー確定値を保護 | 11に同じ | 確定値保護(変更検出)のみ | X/Y/Z | X/Y/Z Std+Adv(既公開の一部Stdは0件、G7) | (なし) |
| 14 | Vocabulary「本文の英文」↔「日本語訳」(T1訳) | 本文引用英文のLLM翻訳 | `er003_kp_source_sentence_ja_01.py:267 generate_translations`/`:318 generate_for_kp_items`。hook: X `er019_family_x_audio_production_runner_01.py:607`、Y `er121_family_y_runner_01.py:831`、Z `er026_family_z_fiction_production_runner_01.py:2515` | `:29-35 PROMPT_HEAD`: 「自然な日本語に訳」「**意訳しすぎず、情報の追加・省略をしない**」 | `:188 check_ja`(構造のみ: 空/短い/英字優位/禁止パターン)。**意味照合なし** | 3Family共通 | X/Y/Z Std+Adv | (なし。vocab) |
| 15 | Vocabulary「解説」内の対訳・例文訳 | 解説LLM(`kp_general_explanation`) | `er003_kp_general_explanation_01.py` | 「解説」Prompt(自然な日本語での解説)。対訳はコロケーション例の補助 | ページ禁止パターン`PAGE_FORBIDDEN_RE`のみ | 3Family共通 | X/Y/Z | (なし) |
| 16 | Grammar「対象となる本文英文」↔「日本語訳」 | 文法StepB(解説LLM)自身の訳 | `er120_part2_grammar_production_01.py:1033-1164`(Step B自身の【日本語訳】を表示=M-1)。`:1118`参考訳(T1 pool)一致時のみ`ref_ja`渡し | `:125-141 STEPB_PROMPT`: 「**日本語訳(自然な訳)**」「参考訳があれば矛盾させない」。**情報の追加・省略禁止の文言なし**(T1の`:29-35`より弱い) | 構造検査`Part2StructureError :1085`、Part1訳との食違い検査`:1909`(Opus O-1) | `er120_part2_wiring_01.py`をX/Y/Z各runnerが呼ぶ(X `er019_family_x_audio_production_runner_01.py:769/806/838`、Y `er121_family_y_runner_01.py:328`、Z) | X/Y/Z Std+Adv(0件はコーナー非表示、2026-10-29決定) | (なし) |
| 17 | Grammar「文法・構文の仕組み」「意味・ニュアンス」内の対訳 | 同16 | 同16 | 同16 | 同16 | 同16 | X/Y/Z | (なし) |
| 18 | タイトル(`title_ja` と `topic_en`) | dev pageのjtitle(日本語)とtopic intro(英語) | `er135_enduser_page_01.py:377-389` | 題の日英は別生成(日本語題=Writer、英題=忠実英訳Title) | なし(整合検査なし) | 各hook | X/Y/Z | (title_ja) |
| 19 | dev page(開発者向け)のKP表・③下線gloss・Vocab/Grammarコーナー | 11/12/13/14/16と同一データ | dev `index.html`に直接生成(End Userはここから派生) | 同上 | `verify_consistency`はdev と End Userのsha一致=**同一性**のみ | 各runner | X/Y/Z | - |
| 20 | **英語対応なしの日本語のみ表示**(参考。今回の「対訳」の対象外): Std Welcome/Intro/Outro/Preview/Comment 1〜4/日本語タイトル、Y Voice紹介(notice) | 日本語Writer/固定文 | 各Family text段 | - | - | - | X/Y/Z Std | - |
| 21 | Adv KP「英語での解説」 | 英語定義(日本語訳ではない) | KP | - | - | - | X/Y/Z Adv | (対象外) |
| 22 | Z「藪の中」(`z_in_a_grove_01`)の本文訳 | **未生成**(旧スナップショット。`article.json`に`ja`なし、`generated_translation.parts=0`) | 再produceが未実施 | - | - | - | Z Std+Adv | (なし) |

## 2. 配線漏れ(共通仕様が一部の出所/Familyにしか適用されていない箇所)
判定基準: 同じ「英語↔日本語訳」の表示に対して、ある検査・規範が一部にしか掛かっていないもの。

| ID | 内容 | 根拠 | 区分 |
|---|---|---|---|
| **G1** | **対訳照合(LLM校閲+数値照合+文結合検査)が`generated`にのみあり、`approved_ja_manuscript`(X本文)・`approved_ja_original_in_dev_page`(Y本文)には無い**。X/Y本文は(a)段落数一致、(b)承認済み原稿との同一性(Y)だけで、日本語が英文に対応しているかを一切検査しない。実データでの問題はこの2系統に集中(COMPARISON_01: 本文でapproved 27%前後/generated 0%) | 検査関数は`translate_part`内のみ(`er135_enduser_translate_01.py:259,291,375,491`)。`attach_translations`(`er135_enduser_page_01.py:631-657`)は呼ばない | **配線漏れ(検査の出所間非対称)** |
| **G2** | Std/Adv英文が別構造なのに**日本語は共通の1原稿**。Std英文はAdvの簡易化(文分割増)だが、日本語は無改変で並置される | `attach_translations`が同一`manus["paragraphs"]`を両Levelへ付与(`:631-645`)。実データ: X/YでStd・Adv間「JA同一=True、EN同一=False」。EN文数 Std 214 / Adv 175 / JA 188 (X) | **設計上の非対称(仕様と実態の乖離)** |
| **G3** | 規範の強さが訳種別で不統一: 学習項目の語句訳は「直訳調を避け平易な言い換え」(#11)、T1訳は「意訳しすぎず…」(#14)、文法StepBは「自然な訳」のみで情報保持の文言なし(#16)、End User生成訳は「情報の追加・省略をしない」(#5)。日本語として自然でありながら英文の情報・構造を保持する、という統一規範は存在しない | 各Prompt行(上表) | **共通仕様の欠落**(配線漏れ+仕様未定義) |
| G4 | `find_x_ja_manuscript`のフォールバック: revision2 > revision1 > **original**。R2が無いと、ユーザーが承認した改稿とは別の台本が「訳」として出る(現行5記事は全て`revision2.md`=発現なし。潜在リスク) | `er135_enduser_page_01.py:1804-1810`、`build_info.ja_manuscript.name`(origin/mainの5記事とも`revision2.md`) | 潜在(現状は発現なし) |
| G5 | `ja_align`が不成立の群は日本語非表示(安全側null)。Stdでは英文のみ表示される文が存在する(今回の抽出で32群/Std X 28・Std Y 4) | `er135_enduser_align_01.py:607-619`、`pairs_all_01.jsonl`の`unaligned` | 仕様どおり(ユーザー決定済みの安全側)。未表示を「訳が合っている」とは扱わない |
| G6 | 既公開`z_in_a_grove_01`の本文訳が無い(旧版。`generated_translation.parts=0`)。同じZの`melos_r3`/`yuki_onna`は生成済み | origin/main `user_test/family_z_in_a_grove_01/enduser/build_info.json` | **既公開のstale**(再produce未実施。API費用を伴う修正は今回の範囲外) |
| G7 | 既公開のY `redelivery_fee_03` Std、Z `melos_r3` StdにVocab/Grammar(Std Part1/2)が0件 | `article.json` `vocab=0, grammar=0` | 配線漏れではない(Std拡張[SYNC-26]は新規記事から、CURRENT_SPEC.md:2090)。世代差として記録 |

配線漏れとして確定=**G1・G2・G3の3件**(G4は潜在、G5-G7は仕様どおり/世代差/stale)。

## 3. 調査で確認した事実と未確認事項
- 確認: 上表のfile:lineは全てorigin/main(013d0fab2)で読取済み。公開済み10記事の`article.json`で`ja_source`値・件数・`ja_align`を全件抽出(1,164ユニット)。
- 未確認: (a)R2台本が生成された当時のPrompt原文(`er015_news_iterative_entertainment_trial_01.REVISION_INSTRUCTIONS`)の逐語確認(今回はmodule冒頭の記述のみ)。(b)Yの`voice_generate_02.txt`がVoiceの日本語を英訳しやすい形で書かせているか。(c)ユーザー原文は`docs/pm/delegation_log/2026-10-31_JA-TRANSLATION-LITERALNESS-AUDIT-01_USER.md`で確認済み(§5の棚卸し項目を全て含む)。
