# EVIDENCE_SOURCE_CHECK_01 evidence元runの実現性確認(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02S、read-only、API 0)

問い: 現行runner世代で「Std/Adv本文・音声・pagesが揃い、kp stage以降を再実行しても本文TTSを再生成せず(KP音声も再生成せず)pagesまで到達できるrun」はFamily別にあるか。結論=**X・Y・Zとも「copy-run + 文法関連stageのみ + pages再生成」で到達できる元runがある**。ただしZのStd非0は元runに無く、別途の経路が要る(§3)。
調査方法=`Get-ChildItem`相当のdir/artifact存在確認と`cost_log.jsonl`/`raw_usage_log.jsonl`/`e2e_stage_log.jsonl`の読取のみ(スキャンscript=scratch、結果は本表)。runtime実行は未実施(新runner実装は並行委任_02で作業中のため、「TTS再生成なし」はartifact状態と既存stage構造からの判定。**実測は実装後のcopy-run前go/no-go確認で行う**=EVIDENCE_PLAN_02 §5)。

## 1. 元run候補の状態(全runで real STOP/STOP_ALL/STOP_NOTICE sentinel 0件。`stop_scope_check_01` rc=0)
音声=narration内wav数/MB(a2|b1b)。asm=assembled(X/Y)/assembly(Z)。Adv/Std候補=`grammar_candidates.json`の既存Adv候補数と(A)実測のStd候補数。
| Family | 元run(`er*_output/`下) | 音声 a2 \| b1b | asm | pages | KP確定 | Part 2(Adv) | Adv候補 | Std候補(本計測) | 確定内容保護rec | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| X | `family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1`(10-25、174MB) | 48/34MB \| 54/30MB | 両level | `player.html` | `kp_human_review.json` 2level(REVIEWED) | REVIEWED・SELECTED | **2** | **1**(r1 a2実測、T2 INV。揺れあり) | なし | **推奨(X)** |
| X | 同 `part2_hr_evidence_01__run_r2`(同一記事) | 47\|61 | 両level | なし | kpmode=auto宣言 | UNREVIEWED_AUTO_ADOPTED | **4** | 1(同一a2 sha) | なし | 予備(Adv N=4の確認用。pagesは`player`stageで生成要) |
| X | `manga_ai_chat_byus__run_byus_01`/`moon_shrinking__run_ms_03` | 59\|50 / 54\|40 | 両level | `player.html` | HR記録なし(旧世代) | byus: なし / ms_03: study_textあり | - | 未計測 | なし | 不採用(KP/Part 2とも旧世代で再選定=KP音声再生成の恐れ) |
| Y | `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01`(10-27、224MB、`style_profile.json`あり=fx_20261017) | 76/62MB \| 45/25MB | 両level | `pages/` | kp_human 2level+`kp_review_mode.json`(auto) | UNREVIEWED_AUTO_ADOPTED・SELECTED | **2** | **2**(実測 CMP+HEAVY) | なし | **推奨(Y)** |
| Y | 同 `run_kcp3_ev_y_02`(`style_profile`あり) | 同上 | 両level | `pages/` | 同上 | 同上 | 2 | 2 | あり(`confirmed_selection.json`+resolved issue) | 予備(保護recが既にある状態の確認用) |
| Y | `redelivery_fee/run_01`・`run_voice_puck_ev_01`・`sns_age_limit/run_01` | - | 両level | `pages/` | - | run_01/voice_puck: auto | 2 / 2 / (Part 2なし) | 2 / 2 / 2 | なし | **不採用**: `style_profile.json`なし。`tts_a2`が旧run前提でSTOPする(EVIDENCE_Y_01 b')=TTS再生成/STOPのリスク |
| Z | `melos/run_p2_evidence_r3`(10-25、295MB) | 30MB(111)\|29MB(112) | 両level | `pages_evidence/` | `kp_human_review.json`(b1bのみ。a2側の確定記録形態は未確認) | REVIEWED・SELECTED | **1** | **0**(melos std、4 call全て0=安定) | なし | **推奨(Z Adv非0/Std 0)** |
| Z | `melos/run_p2_evidence_r4` | 同 | 両level | `pages_evidence/` | kp_review_mode.json(auto) | **ZERO**(NO_CANDIDATE_UNREVIEWED) | **0** | 0 | なし | **推奨(Z 0件セル/Adv 0件)** |
| Z | `melos/run_kcp3_ev_z_01` | 同 | 両level | `pages_evidence/`,`pages_ev/` | 同 | SELECTED | 1 | 0 | あり、**未解決`confirmed_content_issue.json`(INTEGRITY_VIOLATION、改ざんtest残置)** | **不採用**(Gate blockの残置) |
| Z | `the_gift_of_the_magi/run_sf_prod_01`(33.2JPY完走、158MB) | 29\|23MB | 両level | pages dir無(`page_verify_public.json`あり) | HR記録なし(KP auto時代) | **study_textなし(旧世代)** | - | **1**(Magi実測 POSTMOD) | なし | Z Std非0の候補(§3、追加stage要) |
| Z | `after_twenty_years/run_sf_prod_01`(47.9JPY完走、167MB) | 33\|25MB | 両level | 同上 | 同上 | なし | - | **1**(The Promise実測 CMP) | なし | Z Std非0の候補(同上) |
| Z | `the_open_window/run_sf_prod_01` / `the_monkeys_paw/run_sf_prod_01` | - | 両level | - | - | なし | - | 0 / 0 | なし | 不採用(Std 0) |

## 2. 「TTS再生成なし」の判定根拠(Family別)
- **X**: runnerのstage=plan/scaffold/study_text/tts/assemble/player/all(`er019_family_x_audio_production_runner_01.py` argparse)。文法は音声に影響しない(CURRENT_FLOW_01 §4)。`--stage study_text --level both`(Std候補+Adv再利用+事前生成)→確定→`--stage player`はTTS API 0。r1は`review_lock_state`が全segment RESOLVED、`kp_human_review.json`が2level分あり、KP確定が既にある=kp stageをregenerateしなければKP音声は据置。**制約**: Xは来歴ledgerがなく`--stage study_text`が唯一の再実行点(CURRENT_FLOW_01 §3)。
- **Y**: `STAGES`は`seed_check,text,translate,support,kp,tts_b1b,tts_a2,gate,assemble,pages,page_verify`(`er121_family_y_runner_01.py:34`)。DEPENDENTS(:47-52)で`kp_a2→tts_a2`、`kp_b1b→tts_b1b`、`translate_a2→tts_a2`。**新しいStd Part 2 unit(`part2_cand_a2`相当)が`tts_*`の親にならない設計であること**が必要条件(文法は音声に影響しない)。この条件は実装(並行委任_02)の成果物なので、実装後のgo/no-go(§5 step 0)で`_stage_precheck`の入力shaが据置であることを確認する。style_fix runはstyle_profileあり・Gate/assemble/pages/page_verify実績あり(`e2e_stage_log.jsonl`)。
- **Z**: 前例あり。`melos/run_p2_evidence_r3`は`e2e_stage_log.jsonl`で`kp`→`gate`→`assemble`→`pages`→`page_verify`を**追加費用0**で完走(gate以降のspent_jpy_cumulative不変=5.6802のまま)。KCP委任_02Bも`--stages kp --mode real`→`--stages provision_shell,gate,assemble,pages,page_verify`を**1起動**で実施済み(OPEN-480。provision_shell欠落でRESTART_STORMを自行発動するため)。

## 3. 到達できない(またはリスクのある)セルとその費用見積
| 対象 | 状況 | 追加で要る作業 | 費用見積(根拠) |
|---|---|---|---|
| **Z Std非0** | melos Stdは候補0で安定(4 call全て0)。Std候補>0のMagi/The Promiseは**Part 2未導入世代**でstudy_text・KP HR記録なし | (i)copy-runで`--stage kp --mode real`(KP resume or 再選定+Part 1 T1+Part 2 Adv/Std候補+事前生成)→`--stages provision_shell,gate,assemble,pages,page_verify`。KPが据置できればTTS再生成なし | **下限JPY1.5-2**(Std A'' 0.34+Step B 0.11+Adv A'' 0.3+Step B 0.11+Part 1 約0.5。KP据置) / **上限JPY約12**(KP再選定1.1〜3.3[Z kp実測 COST_01 3.30/13 call]+KP音声の再生成。1level約10 segment x Y実測¥0.29/行=約¥3/level。ただしGate G2が許す確定表現に限る) |
| 同(本文含む完全再実行) | copyでなく正式runnerをwriter〜pagesまで走らせる場合 | writer〜TTS全て | Magi完走実績JPY33.2、The Promise JPY47.9(`e2e_stage_log.jsonl`最終`spent_jpy_cumulative`、うちTTS 約JPY19-30) |
| X 到達不能となった場合の代替 | r1 copyがxの再実行点(`study_text`)で不整合なら | scaffoldから実行 | r1の累計JPY18.1(scaffold+TTS)、byus累計JPY53.1(`compute_cost_jpy_so_far`) |
| Y 到達不能となった場合 | style_fix copyで`tts_a2`が再生成を要求する場合 | `tts_b1b`,`tts_a2` | style_fix TTS累計JPY32.1(両level) / `sns_age_limit/run_01`全体JPY82.7 |
| Z 2件採用 | **Zの候補数は全記事で最大1件**(Adv 0-1、Std 0-1) | 実証不可 | mock/unitのみ(runtime未観測と明記) |

## 4. 2件採用を実証できる経路(候補>=2)
- **Y Std(style_fix a2: 候補2、CMP+HEAVY)** と **Y Adv(候補2)** = 同一copy-runで両level。
- **X Adv(r1: 候補2。r2: 候補4)**。X Stdは揺れが大きく(AI島1→3、UK列車2、r1 a2は1)、**r1のStdで2件は保証できない**=2件採用はX AdvとY Std/Advで実証。
- Zは候補最大1のため2件採用はruntime不可。

## 5. 判断に使う事実の要約
- 6セルのうちruntimeで非0を狙えるのは X Std(1以上が4/4記事)、X Adv(2)、Y Std(2)、Y Adv(2)、Z Adv(1、melos r3)。**Z Stdは元runに非0の素材がなく、§3の追加作業(下限約JPY2 / 上限約JPY12)が要る。**
- 0件セル: Z Std(melos)・Z Adv(r4)は元runそのままでruntime観測可能(0件→ZERO/NO_CANDIDATE_UNREVIEWED)。
- 「KP音声のみ再生成」が必要になるのは、KPを再選定(`--regenerate-stage kp`)する場合のみ。本計画はKPを据置(再選定しない)方針のため通常0。
