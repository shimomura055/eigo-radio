# B7_PUBLISHED_ARTICLES_01: AI島(UD-2適用)・Word Gacha Adv・猿の手Std の候補ページ+最終Human報告、メロス=発動なし確認(委任_12 / Phase B B7、API 0)

管理ID: LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01。委任文=`docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_委任_12.md`。前提=統合配線commit 4475cebf8(`BWIRE_INTEGRATED_WIRING_01.md`)。費用=有料API 0(再TTS・再生成・LLM呼出なし。AI島runのcost.json累計36.94円は前後で不変)。公開dirは不変(`git status`でuser_test既存公開dirの変更0)。

## 0. 結論
| 記事 | 結果 | 候補ページ(`user_test/`、公開差替えなし) | 最終Human報告(`final_human_report/`) |
|---|---|---|---|
| X AI島 Std/Adv | M3再評価=**PASS+LR_APPLIED警告**(Std/Adv各k2)→三者一致Gate PASS→assemble OK→候補ページ(page_verify local PASS)。LR赤=Std 1・Adv 1(各行に本文赤+前後注記、事後試聴リストにも赤行)、⏸=各5(実chunk境界と一致) | `family_x_ai_island_form_01_candidate_b7_01/index.html` | `X/ai_island_temple/run_form_prod_01/{standard,advanced}.html` |
| X Word Gacha Adv | 公開版とのvisible text差=**`you've`→`you have` 1語のみ**。LR赤1(part3)。page_verify local PASS | `family_x_word_gacha_01_candidate_b7_01/index.html` | `X/word_gacha/run_wg_01/{standard,advanced}.html` |
| Z 猿の手 Std | 公開版とのvisible text差=**`guest`→`visitor` 1語+旧『Local Rewrite採用』注記の撤去**のみ。LR赤1(`full_story_part1_c10`)。page_verify local PASS(index/standard/advanced、audio 35/50/53再生OK) | `family_z_monkeys_paw_01_candidate_b7_01/{index,standard,advanced}.html` | `Z/the_monkeys_paw/run_sf_prod_01/{standard,advanced}.html` |
| Z メロス_02(run_e2e_06) | LR 0・Fallback 0・不一致なし=発動なし(parity Gate OK) | 候補なし(変更なし) | `Z/melos/run_e2e_06/{standard,advanced}.html` |
| Z 告げ口心臓 | 変更なし | なし | 委任_09生成済み(`Z/the_tell_tale_heart/run_reselect_01/`)を再利用(再生成して差分0を確認) |

URL(push後。公開は`user_test/`と`final_human_report/`をGitHub Pagesで配信): `https://shimomura055.github.io/eigo-radio/<パス>`。

## 1. AI島(run_form_prod_01、特別扱いコードなし)
手順(すべて配線済み正式経路、記録の手書き変更なし):
1. stop_scope_check rc=0。`er019_family_x_audio_production_runner_01.py --slug ai_island_temple --run run_form_prod_01 --stage assemble --level both`(1起動、TTS/LLMなし。累計費用36.94円不変)。stdout=`[WARN][STYLE-PROFILE][M3] a2/b1b full_story_part1_k2: LR_APPLIED`。
2. 旧記録(`BLOCKED_STYLE_PROFILE_GATE`、STD_FALLBACK_USED_OR_UNKNOWN+LOCAL_REWRITE_RECOVERY)は`B7_evidence/ai_island_pre_block_records/`に退避。新記録=`run_summary_assemble.json` status=OK(Std 330.74秒/Adv 308.87秒)、`style_profile_gate.json` status=PASS・blocked=[]・warnings=[LR_APPLIED(AIs→AI agents / AI systems)]。
3. 三者一致Gate(er132 `assemble_gate_summary`)=PASS(Std/Adv)。表示本文=TTS入力=ASR正解(overlay後)。LR clip=`full_story_part1_k2`(parts.json:part1、PASS、overlap T1/T2/T3=PASS・hits0=確定KP/KW/文法と**非干渉**)。
4. 既存LR後音声を使用(narration wav sha全体=assemble前後で`ee869ed5…`不変。再TTSなし)。assembled wav sha: Std `bfdc65dd0dd6e6d3`/Adv `71c3f1a96719c3fb`。LR clip wav sha: Std `2a5d0fc5bbde1c60`/Adv `6f53f1d536a50259`。
5. 候補ページ=標準builder `er019_family_x_listening_page_01.py`(check_page(public)・G3ハイライト・Part1/Part2一致を内蔵PASS)。`page_verify`=`B7_evidence/page_verify_ai_island_candidate.json`(HTTP200・audio 47/47再生・console error 0・4xx 0・file scheme 0・旧注記0)。
6. 学習項目(KP/KW 各10件・文法0件、confirmed_selection)・解説・`in_one_line`(`AIs`残存=C、UD-2範囲どおり)は不変(confirmed_selectionはgit差分なし)。LRは該当英文箇所1語のみ。hr_02のHR Lock=全RESOLVED(Std 22/Adv 19、未解決0)。hr_02 Q1はUD-2(判断済み)で置換済み。`user_test/family_x_ai_island_form_01/{hr_01,hr_02}.html`は旧HRパケット(superseded、削除せず)。
7. 最終Human報告(`er131`、`--family X --level both --slug ai_island_temple`): Std=LR 1(`AIs`→`AI agents`)/Adv=LR 1(`AIs`→`AI systems`)・Fallback 0。Advの KP解説等5単位は「採用take記録なし」(er129のUNKNOWN。final_adoption配線前のrunの既知制約、再TTSなしでは解消しない)。再生成して既存commit済み資料と差分0。

## 2. 見つけた不具合と是正(B-wire由来、同一委任内で修正)
**⏸欠落(LR chunkの直後の境界)**: AI島候補ページの初回生成で⏸がStd/Adv各4個(plan境界は各5)になった。原因=`chunk_plan`のchunk本文は原文(`AIs`)のままで、表示本文はoverlay後(`AI agents`)のため、LR chunk(`full_story_part1_k2`)の直後の境界が`_find_chunk`で見つからず無表示になっていた(推定位置は出さない設計のため警告もなし)。是正: `er132.chunk_texts_overlaid(ledger, plan)`を追加(chunk_idが一致するLR clipだけ表示本文と同じoverlayを通す。LR 0=従来と同一)。配線=X `er019_family_x_listening_page_01.py:127`・Y `er121_family_y_audio_01.py:1554`。test2件追加(`er132_..._test_01.py`: 修正前に1個欠落することと修正後に全境界が出ることを実証、LRなし=同一)。修正後AI島=⏸Std 5/Adv 5=plan境界と一致。
- **未修正(同時進行workerのファイルに触れない指示のため)**: Z `er063_family_z_audio_01.py:2539・2646`(Z `_user_page_rows`/`build_page_rows`のchunk_texts)に同型の欠落が潜在。本記事3件(猿の手・メロス_02・告げ口心臓reselect_01)はchunk planなし/LR 0で**影響なし**。分類=修正へ進む(告げ口心臓Voice修正worker完了後、`_er132.chunk_texts_overlaid(_lr, plan)`の2行置換+test)。
- 併せて軽微修正: `er019_family_x_fx_20261016_wiring_01_test_01.py`のreaders allowlistへer129/er131追記(委任_11 §7(b))、K2 store利用者listへ`er127_final_adoption_b1_test_01.py`追記(同test既存失敗)、`er129`のu8許可リストへ当該test追記、`er132 test`の公開ページ走査から`_candidate_`dirを除外(候補ページは公開前確認用で注記が仕様どおり出るため)。

## 3. Word Gacha Adv / 猿の手Std(旧per-article builderの実状と対処)
公開版はPart 1/Part 2導入前に作られたページ(Part 1ブロックなし)で、現行の標準builder(Part 1/Part 2をfail-closedで要求)・`er026 stage_pages`は、Part 1生成にLLMが要るため(API 0制約)通らない。公開版と同じ入力で統合配線済み表示部品を重ねるため、一回限りのtoolをB7用に追加した(Production codeは不変):
- `tools/b7_legacy_candidate_page_01.py`(X: 公開版生成scriptの`er019_nws2_final_page_01`+er132 overlay+er133表示。`--no-overlay`で配線なし再現=**公開版とbyte一致を実証**。その上でoverlayを有効にして候補を生成)
- `tools/b7_z_candidate_pages_01.py`(Z: 統合配線済み`er063.build_pages`を、公開版と同じ入力=study_htmlなしで直接呼ぶ。run dirは読取専用)
- `tools/b7_local_page_verify_01.py`(X候補index.htmlのlocal Playwright検証)。Zは既存`er063_family_z_page_verify_01.py --local`。
差分証跡(`B7_evidence/`): Word Gacha=visible text diff `you’ve`→`you have`のみ(`visible_text_diff_word_gacha_index.txt`)。HTML上の追加物=凡例1行+LR赤span+前後注記(`rpt-notes`)のみ(`diff_html_01.py`)。音声mp3は公開版と**全47件byte同一**。猿の手=index/advanced: `guest`→`visitor`のみ(advanced: 差0=LRなし)、standard: +旧注記撤去(`visible_text_diff_monkeys_paw_*.txt`)。音声mp3は公開版と**全107件byte同一**。
- Word Gacha: 公開run(run_wg_01)にchunk planなし(分割なし)=⏸なし。猿の手: chunk planなし=⏸なし。
- 猿の手Stdの「採用take UNKNOWN」は最終Human報告(er131)に「記録なし」として表示される(Z旧runはstyle_actual記録なし)。**試聴ページ側にはFallbackの色・注記は出ない**(UNKNOWNは発動の証拠がないため。er133の仕様どおり)。
- 三者一致Gate(X `assemble_gate_summary`/Z `z_assemble_gate`): Word Gacha Std/Adv=PASS、猿の手Std=OK(`full_story_part1_c10` PASS)/Adv=OK(LR 0)、メロス_02 Std/Adv=OK。

## 4. 照合表
| 項目 | AI島 Std | AI島 Adv | Word Gacha Adv | 猿の手 Std |
|---|---|---|---|---|
| 変更前(公開/TTS前) | `The AIs sent…`(本文) | 同(`AIs`) | `If you’ve felt…`(公開) | `After their guest left…`(公開) |
| 変更後(表示=TTS入力=ASR正解) | `The AI agents sent…` | `The AI systems sent…` | `If you have felt…` | `After their visitor left…` |
| LR clip | full_story_part1_k2 | 同 | full_story_part3 | full_story_part1_c10 |
| 音声(clip wav sha) | 2a5d0fc5bbde1c60 | 6f53f1d536a50259 | a6a9558cb3b5ab3a | ca02fcab026bcf8d |
| assembled wav sha | bfdc65dd0dd6e6d3 | 71c3f1a96719c3fb | 2f75eacf63d1e1e0 | bd37b99711a9a648 |
| ASR基準 | LR後の英文(不変) | 同 | 同 | 同 |
| 学習項目 | 不変(KP/KW各10・文法0) | 不変 | 不変(確定KP 3件) | 不変(旧run、確定記録なし) |
| T1/T2/T3 | PASS(干渉なし) | PASS | T1/T2=SKIPPED(確定選定なし)、T3 PASS | 同左 |
| ユーザー承認記録 | UD-2(判断済み 2026-10-28原文§4) | 同 | UDR #183 (a)(2026-10-24)+UD-1 | 注記公開済み(旧)→UD-1で本文反映(記事単位の差替え承認待ち) |
| 注記 | LR赤+前後注記(最終確認資料のみ) | 同 | 同 | 旧注記撤去→共通部品の赤注記 |

## 5. 承認待ち(判断候補。公開差替えはしていない)
- Word Gacha Adv・猿の手Stdの公開差替え(`user_test/family_x_word_gacha_01`・`family_z_monkeys_paw_01`を候補dirの内容へ)=記事単位のユーザー承認待ち(Opus (d)の既公開2件運用どおり)。分類=D(記事単位の承認、UD-1原文に差替え個別承認の記述はないが既公開本文の変更を伴う)。
- AI島候補ページの公開(UD-2適用版の初公開、既存の`family_x_ai_island_form_01`はHRパケットのみで試聴ページ未公開)=ユーザー試聴待ち(試聴PASSは未取得)。
- 新規OPEN候補: (a)Z chunk text overlay(§2、修正へ進む、告げ口心臓Voice worker完了後) (b)runner `_build_level_table`(`er019_family_x_audio_production_runner_01.py:3185,3226-3229`)は⏸を`audience==dev`のplayer_dev.htmlだけに出す旧規則のまま(試聴ページ=標準builderは全audienceで⏸、runnerのplayer.htmlは開発出力で報告資料ではない。実害なし→次委任でaudience規則撤去を検討) (c)`er132` test `test_public_page_scan_*`は同時進行workerのFenrir公開ページ(`family_z_tell_tale_heart_fenrir_01`のENGLISH_LOCK表示)を走査して失敗(本委任起因ではない。実害なし、同worker/次委任で更新)。

## 6. test
- 追加: er132 chunk_texts_overlaid 2件。変更後の再実行: er132 50 PASS+1 FAIL(上記(c): 候補dir除外後に残る失敗はFenrir公開ページの走査のみ)、er133/er131/er129/er130/page_audience/learning_highlight/y_highlight 187 PASS、X highlight/std_chunk/Y page_pause/Y audio_chunk/Y highlight 96 PASS(1 skip)、er019_fx wiring 72 PASS。
- 費用: API 0(再TTS・LLM・ASR呼出なし)。
