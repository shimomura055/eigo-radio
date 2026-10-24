# ROOT_CAUSE_01: 『告げ口心臓』Advanced 一人称→三人称化の根本原因(FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_01 Phase 0)

作成: 2026-10-25 / API 0・LLM呼出0・Production変更0(読み取りのみ。`run_sf_prod_01`配下は無変更)
対象run: `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01/`(以下 `$R`)
ユーザー原文: `docs/pm/delegation_log/2026-10-25_FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01_USER.md`

## 0. 結論(先に)
1. **語り口が変わった工程 = R1(`FAMILY_Z_WRITER_ADV_R1`)**。R0は一人称、R1で三人称へ反転、R2は三人称のまま、Adv最終=R2(sha一致)。Stdは入力が三人称なのに一人称へ戻って出力された(設計でなく偶然)。**StdとAdvで人称が食い違う記事**になっている。
2. **直接原因 = `REVISE_USER_TMPL`(`er062_family_z_writer_01.py:139-142`)の固定文言 "in third person"(141行)**。R1/R2のPromptに全作品共通で埋め込まれ、Seedの一人称指定と**直接矛盾**する命令がPromptの最後(出力直前)に置かれていた。
3. **構造上の根因(上流設計の欠落)**: (a)語り口(人称・語り手の立場)を**Seedのどの構造欄も持たない**(`source_essentials`のスキーマ=ending_reveal/setups_and_payoffs/key_roles/key_causality/free_to_cutのみ。語り口は自由文`conversion_plan`にだけ有る) (b)その`conversion_plan`は**R0にしか渡らない**(設計意図: R1/R2へSeed全文を渡すとアンカリングする=COMPREHENSIVE_DESIGN_02 §3-5)。つまり**R1/R2/Stdへの情報伝達経路(=essentials)に語り口が載っていなかった**。(c)これまで全Z作品(メロス・猿の手・開いた窓・二十年後・賢者の贈り物)は原作も三人称だったため、固定文言の矛盾が顕在化しなかった(潜在不具合。本作が初の一人称Z作品)。
4. 既存の原作忠実性対策(修正版B)が防げなかった理由 = 対策の対象が「結末・伏線・因果・人物」で、**語り口を対象外にした設計**だったため(§3-(5))。さらにFable CPチェックリスト(機械生成)にも語り口の行が無く、`SOURCE_FIDELITY_CHECK_01.md`は冒頭に「Std、一人称」「Adv、三人称」と事実を記しながら、12行の照合表に語り口の行が無かった。

## 1. 人称の実測(決定論集計。ダイアログ"…"除外、語単位)
Std/Adv最終本文の特定: `$R/writer/provenance.json`の`adv_final_sha256=9a3e949c…`は`writer/r2.md`のsha256と一致、`std_sha256=3fe1cbdb…`は`writer/std.md`と一致。`audio_text_deviations=[]`(音声はこの本文どおり)。

| 本文 | 一人称語(I/my/me等) | 三人称語(he/his/him/they等) | 語数 | 判定 |
|---|---|---|---|---|
| 原作(`er026_seeds/the_tell_tale_heart/story.md`) | 173 | 69 | 2107 | 一人称 |
| r0(Adv初稿) | 43 | 23 | 413 | **一人称** |
| r1 | 0 | 53 | 418 | **三人称** |
| r2(=Adv最終) | 0 | 51 | 415 | **三人称**(ユーザー試聴NGの本文) |
| std(=Std最終) | 41 | 26 | 417 | **一人称**(入力r2は三人称) |

聞き手への呼びかけ"you"の出現数: r0=4 / r1=0 / r2=0 / std=1。三人称語の残りは老人・警官を指す語(r1/r2の一人称語0が語り手の反転を示す)。
他のZ作品(`the_gift_of_the_magi`/`the_monkeys_paw`/`the_open_window`/`after_twenty_years`/`melos`)は原作・r0〜std・最終とも三人称(一人称語0〜1)。**『告げ口心臓』が唯一の一人称Z作品**=今回の問題は同作固有ではなく、一人称作品に対するZ経路の構造欠陥。

## 2. 段別追跡(原作→Seed→Writer→レベル別→最終)
| 段 | 入力(実物) | 出力の人称 | 根拠(ファイル:行) |
|---|---|---|---|
| 原作 | Gutenberg #2148 | 一人称"I"+聞き手"you" | `er026_seeds/the_tell_tale_heart/story.md`冒頭 |
| Seed | `seed.json`の`conversion_plan` | **一人称を明示**: 「Keep ... the first-person voice ... do not change the narrator into a third person」「let the narrator keep addressing the listener ('you')」「refer to them as I, the old man, and the officers」 | `er026_output/family_z_production_e2e_01/the_tell_tale_heart/seed/seed.json:22` |
| Seed(構造欄) | `source_essentials` | 語り口の欄なし。人称が出るのは`key_roles[0].role`の1句"the unnamed first-person speaker"のみ(役割説明であり指示ではない) | `seed.json:47` |
| R0 Prompt | `$R/writer/r0_prompt.txt` | conversion_plan全文が入る(**20行目に一人称指示**。seed_elementsは三人称の要約文だが影響せず) | `r0_prompt.txt:7-20` |
| R0 出力 | `writer/r0.md` | **一人称**("You fancy me mad. But I am only nervous…")。呼びかけ4か所、"I almost laughed at my own care"、"I knew that sound. It was terror."、"Could you have borne those smiles?" | `r0.md:3,11,15,19,49` |
| R1 Prompt | `writer/r1_prompt.txt` | 本文r0(一人称)+**55行目「…about 330-470 words, **in third person**, and only the narrator (who stays unnamed, as in the original) may have a personal name.」**+Must-keep。**conversion_plan/seed全文は渡らない** | `r1_prompt.txt:55,57-65` |
| **R1 出力** | `writer/r1.md` | **三人称へ反転**。語り手は"the old man's housemate"という**LLMが新造した呼称**に変わった。"you"全消失 | `r1.md:3-5` |
| R2 Prompt | `writer/r2_prompt.txt` | 本文r1(三人称)+同一固定文言 | `r2_prompt.txt`(末尾のMust-keep直前の段落) |
| R2 出力 | `writer/r2.md` | 三人称のまま。**Adv最終** | sha一致(§1) |
| std Prompt | `writer/std_adjust_prompt.txt` | 入力=r2(三人称)。人称指示は**無い**(`STD_PROMPT_HEAD/TAIL`に人称の記述なし)。Must-keep 23行目の"unnamed first-person speaker"が唯一の人称語 | `std_adjust_prompt.txt:23,45-87` |
| std 出力 | `writer/std.md` | **一人称へ復帰**(偶然。三人称入力を一人称で出した理由は、23行目の語句が引力になった可能性が高い=推測。指示ではないため再現性なし) | `std.md:3` |

生成時刻(UTC、`provenance.json`): r0 13:29:24 / r1 13:29:59 / r2 13:30:31 / std_adjust 13:31:37。モデルは全段`gpt-6.1-sol` effort=high。writer段の再生成記録なし(`regenerations`はkp_a2のみ)。

## 3. ユーザー要求§3の5問への回答
**(1) どの工程で語り口が変わったか**: R1。R0=一人称(43/23)、R1=三人称(0/53)。R2は維持、Std調整で一人称へ復帰(Adv/Std食い違い)。

**(2) なぜ変更が行われたか**: R1のPrompt末尾に「in third person」が明示命令として入っていたため(`r1_prompt.txt:55`)。LLMはその命令に従い、Must-keepの「key people: narrator ... refer to this person by role or relationship, without a name」から呼称が必要になり、"the old man's housemate"(老人の同居人)という語り手呼称を作った(`r1.md:3`)。LLMの逸脱ではなく、Promptの命令どおりの出力。

**(3) 既存仕様・Promptのどこに問題があるか**:
- `er062_family_z_writer_01.py:139-142` `REVISE_USER_TMPL`の"in third person"(141行)。起源は共通Trial②のR1/R2文言(三人称原作のメロスに最適化)。`build_revise_prompt`(533-541行)が作品別に差し替えるのは`{main_character}`(`STORY_MAIN_CHARACTER`、527-530行)のみで、人称は差し替え不能。`STORY_MAIN_CHARACTER["the_tell_tale_heart"]`(530行)は名前問題にだけ配慮し、人称は見落とされた。
- 承認済みSeed(`conversion_plan`:「do not change the narrator into a third person」)とR1/R2の固定命令が**同じ記事の生成チェーン内で矛盾**(PM_GOVERNANCE 21節 入口6=承認済み文言との矛盾に相当)。
- `_render_essentials_block`(403-433行)・`validate_source_essentials`(447-491行): 語り口の欄が無いため、Seed承認(seed_check)でも検出できない。

**(4) 語り口以外の重要要素も失われる設計になっていないか**: **なっている**。r0→r2/Std実物の比較(語り口と結びついた心理表現が脱落):

| r0にあった要素(原作の面白さの核) | r2(Adv) | std | 失われる設計上の理由 |
|---|---|---|---|
| 聞き手への呼びかけ"you"("You fancy me mad"、"You understand?"、"Could you have borne those smiles?") | 全消失(0) | 1か所のみ | 一人称が失われると呼びかけが成立しない。essentialsに欄が無い |
| 語り手の余裕・自己満足の狂気("I almost laughed at my own care") | 消失 | 消失 | `free_to_cut`に「narrator's repeated arguments that he is wise and cunning」があり、R1の"more engaging story"で自己陶酔の描写全般が圧縮された |
| 老人の恐怖を理解しながら聞く心理("I knew that sound. It was terror.") | "From the bed came a small groan of terror."(語り手の理解が消え客観描写化) | "A small cry of fear came from his bed."(同) | 心理の主体が失われると内面の確信が外面描写へ置換される |
| 警官への被害妄想の断定("They heard it. They knew.") | "But they knew. They must know."(推測形に緩む) | "they knew"(維持) | 同上 |

維持された要素(出来事・結末): 出来事の順序、vulture eye、7夜、8夜目、心臓音、自白の最終行はr0〜stdの全てに存在(`SOURCE_FIDELITY_CHECK_01.md`の12項目は維持)。したがって**essentialsが守る対象にしていたもの(出来事・伏線・結末)は守られ、守る設計に入っていなかったもの(語り口・語り手の心理の質)が失われた**、が正確な診断。essentialsの`tone`欄(任意1項目)はOpusレビュー所見として`COMPREHENSIVE_DESIGN_02.md:26`に「任意で可」とあったが、スキーマ・描画(`_render_essentials_block`)には実装されなかった。

**(5) 既存の原作忠実性対策がなぜ防げなかったか**:
- 設計対象: 修正版B(`APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`、2026-10-23)は『開いた窓』のオチ脱落の再発防止として設計され、守る項目を「結末・種明かし・伏線回収・主要人物の役割/関係/動機・重要因果」に限定した(`COMPREHENSIVE_DESIGN_02.md` §1、ユーザー原文§4)。語り口は項目外。
- 伝達経路: conversion_plan(語り口を持つ唯一の場所)はR0のみに入り、R1/R2/Stdにはessentialsだけが渡る(`COMPREHENSIVE_DESIGN_02.md` §3-5)。essentialsに語り口が無いので、R1/R2は固定文言だけに従った。
- 確認工程: 機械生成の`writer/cp_checklist.md`は8行(ending_reveal/withhold/setup×2/key_role×3/key_causality)で語り口の行が無い。`CP_CHECK_01.md` §C③(語り手=名なし・一人称)は「最低限の項目」として挙げられていたが、チェックリスト生成(`build_cp_checklist`、`er062_family_z_writer_01.py:817`)に反映されなかった。`SOURCE_FIDELITY_CHECK_01.md`の目視照合表(12行)にも語り口の行が無く、冒頭の対象行に「Std、一人称」「Adv、三人称」と事実を記しただけで判定されなかった。なお`cp_checklist.md`の引用欄(r0〜std)は全て空欄のまま(CP記入の記録は`SOURCE_FIDELITY_CHECK_01.md`が代替)。
- 結論: 守る対象の定義(スキーマ)に語り口が無く、伝達・確認の全経路がそれに従った。**検出機構の不足ではなく、上流のスキーマ欠落**が原因(ユーザー指示§4と整合: Validator追加でなくSeed/Writer契約で解決すべき)。

## 4. 下流構造(Voice割当・会話生成器)は一人称独白と整合している
- 話者設定: `er062_family_z_structure_01.py:316-318`(`STORY_SPEAKER_CONFIG["the_tell_tale_heart"].attr_roster_text/attr_caution_text`)は「この物語は一人称の語り手」を前提に書かれ、語り手本人の台詞は narrator(Aoede)が読む設計。話者表(`$R/speaker_table.md`)でも、三人称化した**Adv**の自白台詞q21_1/q21_2の根拠欄が「The first-person narrator screams ...」と一人称前提のまま=**Adv本文が構造の前提と食い違っていた証拠**。
- 会話の少なさ: 台詞は老人の"Who's there?"1件のみ(old_man=Algieba、`speaker_table.md`)。Voice構造は「語り手+人物」だが、人物台詞が少ない作品でも成立する(narratorが地の文と語り手本人の台詞を担当)。人称を変える誘因は**Voice構造・会話生成器にはなく**、人称反転はWriter段(R1 Prompt 55行目)のみが原因。
- 結論: 一人称Advを生成しても、Voice割当・plan・ttsの構造変更は不要(Stdが既に一人称で plan/support/kp/tts_a2/gate/assemble を通過した実績: `e2e_stage_log.jsonl`)。

## 5. 21節 既存資産照合(A/B/C)
| 論点 | 分類 | 根拠 |
|---|---|---|
| 「in third person」固定文言とSeed一人称指定の矛盾 | **A(既存承認仕様と実装の矛盾=不具合。PM_GOVERNANCE 11-8)** | Seed `conversion_plan`(承認済み)、`SOURCE_CHECK_01.md`:13(語り手=一人称・名なし)、`CP_CHECK_01.md` §C③。新仕様でなく是正対象 |
| 語り口をessentialsへ載せるスキーマ拡張 | **C(本当に新規。ただし改善Trialはユーザー承認済み=2026-10-25)** | 過去の`source_essentials`に語り口欄なし。`tone`はOpus所見止まりで未実装(`COMPREHENSIVE_DESIGN_02.md:26`) |
| 過去Trialとの重複 | **B該当なし** | `DECISION_LOG.md`/`DECISION_LOG_HISTORY.md`/`OPEN_ITEMS.md`/`OPEN_ITEMS_HISTORY.md`/`CURRENT_SPEC.md`/`docs/research/FAMILY-Z-*`を「人称/一人称/三人称/視点/語り手/narrator/POV」でGrep。Hit=(i)Family B Voices(`EDITORIAL-B-FAMILY-VOICES-*`: 記事の一人称"I"機械保証・三人称版Voice A/B、DECISION_LOG_HISTORY.md:319-453付近、CURRENT_SPEC.md:672-707)=別Family・別目的 (ii)KP人称一般化(`generalize_person_dependent_reference`、CURRENT_SPEC.md:1633-1635,1972。Key Phraseの"my"→"someone's")=別機構 (iii)Z各作品CP/SOURCE_CHECKの「三人称」は変換方針の記述のみ。**Z本文の語り口(人称)維持を扱った過去Trial/不採用方式は0件**。一人称→三人称の機械変換はB Voices Trial-07(DECISION_LOG_HISTORY.md:433)にあるが、本件は逆(変換しない)で目的が異なる |
| 過去不採用方式の再導入 | なし | 本設計はValidator/LLM検査/retryを追加しない(DESIGN_01.md)。撤去済み意味保持Validator(er061)に相当するものも作らない |

## 6. 反証の整理
- 「LLMが偶然三人称化した」→反証: 三人称は`r1_prompt.txt:55`で**指示された**出力であり、"housemate"もMust-keepの呼称指示と整合して説明できる。Pure再生成による再現確認は有料のためPhase 0では行わない(API 0)。Phase 1で固定文言を差し替えた対照条件と比較して再現確認する。
- 「R0の時点で既に三人称寄りだった」→反証: `r0.md`は一人称(43/23)。
- 「Stdが一人称なのはStd調整Promptが人称を指示したから」→反証: `STD_PROMPT_HEAD/TAIL`(`er062_family_z_writer_01.py`、Std Prompt実物`std_adjust_prompt.txt`)に人称記述なし。偶然(Must-keepの"first-person speaker"語句の影響が最有力、推測)。

## 訂正(2026-10-25 委任_02、Opus条件A見落とし1・2の反映)
- **§5「過去Trial 0件」は不正確**。`er055_family_z_d_predictive_validation_trial_01.py:135-143`の`NEUTRAL_CONVERSION_PLAN`に汎用文「Keep the original point of view (first person if the original is first person, third person if it is third person)」がある(21節B: **Trial内の汎用文言の先例**。不採用判断の記録ではなく、raw-textモードのconversion planに作品非依存で人称維持を書く試み)。今回のアーム(ii)(Seed欄なしの汎用置換)の対照として使う。
- **寄与要因の追加(見落とし1)**: `_render_essentials_block`(`er062_family_z_writer_01.py:424`)は`keep_name=false`の人物すべてに「refer to this person by role or relationship, without a name」と描画する。語り手が一人称の作品ではこれが「外から呼称で描け」という指示として働き、"in third person"と合わさって"the old man's housemate"を生んだと読むのが自然(推定。1aアーム(iii)でNarration行をKey people行より前に置く対処の検証対象)。
- 固定文言の由来: `er059_melos_sol_b3z_trial_01.py:83-87`(Family X W-1文言をメロスA2用に最小変更)。三人称作品ではR0が三人称を書くため念押しにすぎず、外しても挙動はほぼ変わらない見込み(Phase 2で確認)。
