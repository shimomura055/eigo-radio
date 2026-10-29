# HR到達経路(新形式・PM_GOVERNANCE 30節): 藪の中 Advanced `full_story_part3_c6`(武弘の証言・Puck・91語) — FZ-DIALOGUE-LR-ADOPTION-01 委任_03 E1(2026-10-29)

## 区分(30-3): **(A) 既存の承認済みProductionルートを正常に通過した結果のHuman Review**(今回は新仕様=ZセリフLR正式採用の6回フローを実走し、LR発動・④⑤⑥まで消費した後のHR)。未実行の承認済み救済工程・経路不具合による到達ではない(ただし下記『副次発見2件』は是正済み/登録済み)。

## 1. 対象
藪の中(Family Z) Advanced、武弘の証言 `full_story_part3_c6`(Voice=Puck、91語)の本文音声。run=`er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01`、level=b1b。

## 2. 適用ルート(承認済み)
ZセリフLR正式採用(原文§2、CURRENT_SPEC『統一仕様』Z_DLG_CTX行・8区分一覧#3): ①ctx②ctx→180秒→③従来Dialogue→LR(最大1回)→④ctx⑤ctx→180秒→⑥従来Dialogue→HR(最大TTS6・LR1・待機2)。実装=`er122_fz_ctx_policy_01.py`(state v2 phase B1/LR/B2)、`er063_family_z_audio_01.py`(`_dialogue_ctx_flow` 外側guard)、`er127_tts_block_policy_01.py:114`(Profile Z_DLG_CTX)、`er129_lr_display_reflection_01.py`(確定内容の事前保護)。#1〜#3は旧仕様下で消費済み→移行tool(`fz_dialogue_lr_resume_01.py --apply`)で state v2(phase=LR)・Lock=REGENERATE_APPROVED(cumulative 3)へ正規移行(原文§3参照を記録)。

## 3. 通過工程(時系列。`b1b/audit/dialogue_ctx_attempt_state.json` attempts、`cost_log.jsonl`、`er011_output/attempt_history.jsonl`)
| # | 時刻(JST) | 経路 | 方式 | 判定 | 費用 |
|---|---|---|---|---|---|
| ①〜③ | 14:55-15:01(消費済み・再実行0) | 通常/再試行/Fallback | ctx/ctx/従来Dialogue(180秒待機実施済み) | ①ASR NG_BOTH(`and unseen hand`)/②減速後再検証NG_BOTH(`I sink`)/③ASR PASSだがrepetition QA d'短lag 0.73s>0.6sでflagged | 累計¥122.02(移行前) |
| 移行 | 18:23:08 | M7 tool apply | state v2/phase=LR/Lock REGENERATE_APPROVED | 前提C0-C14全OK | 0 |
| LR | 18:24:31-45 | **LR(最大1回)** | 入力=#1(an→and)。#2はNG span『my chest i sank for ever into the darkness』が確定Vocab(sank for ever等)と重なり除外(OVERLAPS_CONFIRMED_CONTENT, T1/T2)=事前保護どおり | 候補選定: `An unseen hand`→**`Some unseen hand`**(7 Gate全PASS、1語変更、確定「sank for ever」「on soft feet」不変) | gpt-6-luna 2呼出 ¥0.47 |
| ④ | 18:24:45-18:25:42 | LR後ctx 1回目(block depth1, ordinal1) | ctx(Puck、style sha 3eb5d8ba…=B1と同一) | ASR PASS_WITH_WARNING(NORMALIZED_MATCH)だが repetition QA **method_d'短lag run長0.68s>0.6sでflagged**(method_a n-gram非flag)→不合格 | TTS ¥3.64+ASR ¥0.18 |
| ⑤ | 18:25:42-18:26:34 | ctx 2回目(待機0) | ctx | ASR NG_BOTH(TRUE_CONTENT_MISMATCH: 『I **sunk** forever』=`sank`→`sunk`の読み崩れ。Azure Secondaryも不合格) | TTS ¥3.30+ASR ¥0.17+Azure ¥1.73 |
| 待機 | 18:26:34-18:29:34 | 180秒(2回目) | - | 実測180秒 | 0 |
| ⑥ | 18:29:34-18:30:25 | 従来Dialogue Fallback(Puck、ctx除外) | legacy | ASR NG_BOTH(『But **he** fled』=`she`→`he`の読み誤り。Secondary不合格) | TTS ¥3.08+ASR ¥0.16+Azure ¥1.66 |
| 終端 | 18:30:25 | 通算TTS 6到達→TERMINAL_NG→STOPPED | Lock=HUMAN_REVIEW_REQUIRED(cumulative_tts_attempts=6)、HRQ 1行(`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`、重複抑止行1)、rc=2 | | E1合計 **¥14.38**(累計¥136.40) |

LR Before/After(変更箇所): `…Then someone crept towards me on soft feet. **An** unseen hand quietly drew the dagger from my chest. …` → `**Some** unseen hand`。変更理由=#1転写で`An unseen`が`and unseen`と読まれる(an→and)ASR誤認回避のための1語変更(意味・事実・人物像は不変、確定KP/Vocabは不変)。対象音声区間=武弘の証言(Puck)後半、"on soft feet" 直後の1文。最終採用=なし(HR)。

## 4. 救済処理の発動・非発動
再試行=②⑤で発動、Fallback=③⑥で発動、LR=**発動**(1回、再入禁止を維持)、180秒待機=2回とも実施。非発動の救済なし。上限(通算TTS 6・LR 1・待機 2)に到達。

## 5. HRに至った直接原因
(a) ④はASR合格(PASS_WITH_WARNING)・repetition QAのみd'短lag 0.68s(閾値0.6s)で不合格、(b) ⑤⑥は実際の読み誤り(sank→sunk / she→he)でASR NG。③(0.73s)と④(0.68s)はいずれも**ASR合格・d'のみ超過**で、OPEN-594(method_d' Algieba偽陽性疑い)と同型。Gate閾値の変更はユーザー承認事項のため未適用。

## 6. 残っている自動救済
なし(通算上限到達。再生成は人間のapprove_regenerate 1回限り=`er011_human_review_lock_01.py:475`)。

## 7. ユーザーに判断してほしいこと
(a) 音声採用: ③(旧)または④のどちらかを聴いて採用(いずれもASR合格・d'のみflag)するか、(b) 再生成1回の承認(次サイクル: ①〜⑥の新6回、概算¥15〜19)か、(c) OPEN-594(d'閾値・偽陽性)の判断。HR聴取ページは新規作成可(3+3試行分)。

## 副次発見(委任_03、是正/登録済み)
1. **確定内容事前保護が過剰だった(是正済み)**: `er129.level_facts`が引用clip本文を文末記号なしで末尾に足し、KP一覧entryと1文に結合 → 確定語句を含む偽の『出典文』となり、Std/Adv dialogue clip多数が偽T2で『LR不可』になる(Std 8/8 clip、Adv一部)。藪の中c6は文末が`."`で終わるため非該当(E1に影響なし)。`_level_text_from`(台帳と同一関数)で群の境界を文境界化して是正、test追加(er122_fz_ctx_policy_lr2_test_01.py)。
2. **LR候補が二重引用符になる(是正済み)**: LR候補生成Prompt(`er020.build_candidate_gen_prompt`)が原文を`"…"`で囲むため、引用符で囲まれたZセリフ原文では候補が`""…""`になる(E1 c6のTTS入力・ASR正解も二重引用符のまま④⑤⑥を実行)。共有Promptは無変更のまま、Z限定の`er129.make_candidate_filter`で原文と同形へ戻す(語列は不変、音声・Gateへの影響は観測されず=④の読み誤りは別原因)。

## 追補(委任_04, 2026-10-29): HR試聴ページと採用時の扱い(API 0)
試聴ページ=`user_test/family_z_in_a_grove_hr_03/`(③従来・④LR後ctx・⑤⑥ASR NG参考。attempt file対応=③=attempt4/④=attempt5/⑤=attempt6/⑥=attempt7。音声は`b1b/narration/attempts/`のwavを96kbps mp3化。生成script=`tools/build_hr_page_03.py`)。

**③採用と④採用の違い(1段落)**: ③(LR前本文・従来Dialogue)を採用すると、表示本文=原文のまま不変(An unseen hand)、TTS入力=原文、ASR原稿(期待テキスト)=原文で、既存の個別Human Approval(`er121_e1_hr_adopt_r0_01.py`方式=`asm.record_human_approval`+Lock RESOLVED/HUMAN_APPROVED+narration/*.wav置換+`HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG`=真[er020:905,921: 期待テキストは常に原文])を適用でき、LR採用台帳はdepth=0(LRなし採用、`human_superseded_lr`真=LR後の音声は不採用)になる。④(LR後本文・ctx)を採用すると、音声はLR後本文(Some unseen hand)で生成済みのため、Article表示本文はLR後本文(`audio_text_deviation.audio_text_after`)へ反映され、候補ページにLR Before/After(赤字「An→Some」)が付き、TTS入力・ASR原稿もLR後本文になる(フラグは立てない=期待テキストはer020:924以降のLR後文を参照)。LR採用台帳(er129)はdepth=1・ordinal=1(block depth1の1回目)で記録される。**採用手順の適用可否**: 既存`hr_adopt_01.py`は`a2`(Std)固定・segmentがcomment_3/part1_c3のみ・attempt番号=file番号(1〜3)前提のため**そのままでは適用不可**(Adv=`b1b`、c6は通算file番号がattempt4/5)。③採用はer121方式の`--level b1b --segment full_story_part3_c6`が最短、④採用は(i)wav置換(attempt5)+Lock RESOLVED/HUMAN_APPROVED+record_human_approval(key=canonical_text)に加え(ii)entryのtext/`audio_text_deviation`をLR後本文へ・フラグ非設定・LR台帳depth=1、(iii)dialogue_ctx_attempt_state(TERMINAL_NG)とHRQ行は履歴として維持、が必要で、c6専用adopt scriptを次委任で作る(TTS/ASR 0、ユーザー採用発言fileにsegment名が必須=AI/Fableは代行しない)。完成stage前に表示§6(候補ページのLR Before/After赤字・Fallback濃い青)をページ生成後に確認する。
