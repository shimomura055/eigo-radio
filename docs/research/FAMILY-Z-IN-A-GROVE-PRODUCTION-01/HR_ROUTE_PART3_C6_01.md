# HR到達経路: 藪の中 Advanced `full_story_part3_c6`(武弘の証言・Puck・91語) — FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_16(2026-10-29)

ユーザー確認指示原文=`docs/pm/delegation_log/2026-10-29_FAMILY-Z-IN-A-GROVE-PRODUCTION-01_USER_CHECK_01.md`。API呼出0・追加費用0(既存ログのみ照合)。

## 結論
**(A) 既存の承認済みProductionルートを正常に通過した結果のHuman Review。** 未実行の承認済み救済工程なし、経路上の不具合なし。Fallbackは#3として実際に発動した。LRはこのclipの承認済み仕様上「対象外(未配線)」で、発動しないのが正しい。

## 1. 承認済み仕様(照合)
- Z本文dialogue(Std=a2・Adv=b1b)のTTS: 1回目=文脈・感情付き(ctx)→NGなら2回目=ctx(待機0)→2回目NG後に**180秒**→3回目=従来方式(Fallback、`style_prefix_override=None`、文脈完全除外)。総3回、4回目なし。3回NG→STOPPED→Review Lock(HUMAN_REVIEW_REQUIRED)→STOP(rc=2)。根拠=`CURRENT_SPEC.md:1652`(旧600秒記述は履歴、待機は1657=統一後の180秒が正)、`CURRENT_SPEC.md:3165-3178`(Z_DLG_CTX表、3178「Zセリフは文脈・感情Style2回→180秒→従来Dialogue 1回(LRなし・計3回。OPEN-528 Deferred(1)=LR新設せず確定)」)、実装 `er122_fz_ctx_policy_01.py:32`(MAX_TOTAL_ATTEMPTS=3)・`:42-45`(180秒)、`er127_tts_block_policy_01.py:114`(`Z_DLG_CTX`: lr=False, max_tts=3, max_waits=1)、`er063_family_z_audio_01.py:925-965`(`generate_dialogue_ctx`)、`er011_human_review_lock_01.py:81`(PRODUCTION_MAX_TTS_ATTEMPTS=3)。
- 「NG」の定義=既存のASR判定(Primary→Azure Secondary)・disfluency・repetition QA(method_d'閾値0.6秒、`er011_open121_repetition_qa_production_01.py:310`)の採否そのもの。Advは減速(adv_dialogue_fast6後の再検証)を含み、外側ループ(`er003_v1_n3_01_tts_generate.py:503-552`)が通算3回を共有。
- LR(Local Rewrite): 配線されるのは英語narrator/本文系(EN_LR_STD/EN_LR_ADV: ③NG後に最大1回、書換え後に同じ3回ブロック再実行)。**Z dialogue(Z_DLG_CTX/Z_DLG_LEGACY)は`lr=False`**(`er127:114-115`)。「LRなし部位へ独断でLRを追加しない」(`CURRENT_SPEC.md:3176`)。LR新設は新仕様=別承認事項。
- 未実施の承認済み救済: なし(下記)。method_d'(短lag)にはlocal ASR確認(OPEN-128先例型)の救済は未配線(method_dのみ`local_asr_confirmation`あり、`er011_open121...:177,290-305`)。これはOPEN-594(閾値/Gate変更=ユーザー判断待ち)であり、未実行の承認済み工程ではない。

## 2. 時系列(JST 2026-10-29、`b1b/audit/dialogue_ctx_attempt_state.json` cycle2、`er011_output/attempt_history.jsonl`、`run_sf_prod_01/cost_log.jsonl`)
| # | 開始〜終了 | 経路 | 方式(送信実測) | 判定 | 費用概算 |
|---|---|---|---|---|---|
| 旧 | 08:26(cycle1) | 旧plan(6語の別内容) | ctx | DONE_OK(本文/policy/ctx style変更でstate_mismatch→新規cycle2。通算に数えない) | - |
| #1 | 14:55:44-14:56:43 | 通常生成(Z_DLG_CTX 1回目) | ctx(Puck、input_tokens 976) | Primary=ASR_VALIDATION_UNCERTAIN(「and unseen hand」の読み崩れ)→Azure Secondary=TRUE_CONTENT_MISMATCH(「I sink」)→**NG_BOTH**(`secondary_not_accepted`) | TTS約¥4+Azure ¥1.82 |
| #2 | 14:56:43-14:57:41 | 再試行(2回目ctx、待機0) | ctx(Puck、976) | 1次ASR PASS(NORMALIZED_MATCH)・repetition QA非flag(d'=0.5s<0.6s)→**Adv 6%減速後の再検証**(14:57:47 OpenAI「I sink forever」=TRUE_CONTENT_MISMATCH→14:58:06 Azure「dogger」「I sank」=TRUE_CONTENT_MISMATCH)=**NG_BOTH(減速後終端NG)** | TTS約¥4.4+ASR+Azure |
| 待機 | 14:58:06-15:01:06 | 180秒cooldown(実測179.941秒、`CTX_COOLDOWN_BEFORE_FALLBACK`) | - | - | 0 |
| #3 | 15:01:06-15:01:54 | **Fallback(3回目、従来方式)**: `tts_mode=legacy_fallback`、文脈除外(input_tokens 554、ctx prompt無し) | 従来Dialogue | ASR PASS(NORMALIZED_MATCH)だが repetition QA **method_d'短lag run長0.73s>0.6s で flagged**(method_a ngram・long-lag非flag) → 不合格 | TTS約¥3.7+ASR |
| 終端 | 15:01:54 | 通算3回到達→TERMINAL_NG→STOPPED→Review Lock `HUMAN_REVIEW_REQUIRED`(`b1b/audit/review_lock_state.json`)→`FamilyZTtsClipFailedStop` rc=2 | - | 4回目は構造的に不可(budget_left<=0、`er063:933-940`) | 3試行合計約¥15 |

## 3. ①Fallback / ②LR への回答
- ①: 承認済みFallback=3回目の従来方式。**実際に発動した(#3)**。#1=通常生成、#2=再試行(ctx同一)、#3=Fallback。180秒待機も実施済み。発動しなかった処理はない(4回目は仕様上存在しない)。
- ②: このclipはdialogue(Z_DLG_CTX)でLR対象外。LRの発動条件=EN_LR系(narrator・本文系)で③NG後。入力・出力=該当なし(未発動が正しい)。LRなし部位へLRを追加するのは新仕様で、承認なしに実装・実行できない。

## 4. 判定
- 承認済みルート(ctx→ctx→180秒→Fallback、通算3回、減速後再検証、Azure二次ASR、repetition QA、Review Lock)を順序・回数・待機とも仕様どおり通過した。runtime上の実送信(model/voice=Puck/input_tokens差)とログが仕様と一致。経路上の不具合・未実行の承認済み救済工程は**なし**。→ **(A)**。HR要求は妥当。
- 補足観察(不具合ではない): (i) Z dialogue終端はROW_MAPPING_01表どおり「Lock→HR/STOP」でHRQ(human_review_queue.jsonl)行は書かない(register_terminal_hr未呼出。part1_c3も同様)。(ii) 判定はASR誤認(sink/sank、dogger)・d'声質自己類似の偽陽性の疑いがある(OPEN-594)が、これはGate閾値/ASR基準の問題で、変更はユーザー承認事項。未適用。
- 残る自動救済手段: **なし**(試行上限到達。再生成は人間の明示承認1回限り=`er011_human_review_lock_01.py:475 approve_regenerate`)。

## 5. 新ルール(`PM_GOVERNANCE.md` 30節)に沿ったHR報告文(Fable→ユーザー提示用)
1. 対象: 藪の中(Family Z) Advanced、武弘の証言 `full_story_part3_c6`(Puck、91語)の本文音声。
2. 適用ルート: Z dialogue 文脈・感情付きTTS+Fallback(CURRENT_SPEC:1652/3165-3178。ctx→ctx→180秒→従来方式、総3回、LRなし)。
3. 通過工程と判定: 上記時系列表(#1 NG_BOTH / #2 減速後再検証NG_BOTH / #3 ASR PASSだがrepetition QA d'のみflag)。
4. 救済: 再試行=#2発動、Fallback=#3発動(180秒待機実施)、LR=対象外(Z dialogueは未配線、新設は別承認)で非発動。
5. 直接原因: 通算3回上限での不合格(#1/#2はASR判定、#3はrepetition QA d'短lag 0.73s>0.6s)。
6. 残る自動救済: なし。
7. ご判断いただきたいこと: 3試行の音声(HRページ`user_test/family_z_in_a_grove_hr_02/`)を聴き、(a)いずれかを採用、または(b)再生成1回を承認(数円〜¥6)。
区分: **既存ルートを正常に通過した結果のHuman Review(不具合・未実行工程ではない)**。
