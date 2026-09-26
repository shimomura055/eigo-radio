# TTS-COOLDOWN-LOCAL-REWRITE-TRIAL-01

DEV/Trial(最大分類VALIDATED)。cool-down・Local Rewrite・Connected Speech
role taxonomy拡大は、いずれもProduction未配線(APPROVED_FOR_PRODUCTIONなし)。

## 要点(6行)

1. Family X comment_4 canonical("...Now, let's bring the main point
   together.")を新規harness(`er020_tts_cooldown_local_rewrite_trial_01.py`)
   で実TTS/実ASRを使い再実行し、attempt1・attempt2(即時)・attempt3
   (10分固定cool-down後、実測gap 611秒)の3回連続で同一のASR誤認識
   (point→points)によるNG(ASR_VALIDATION_UNCERTAIN)を再現した。
2. Local Rewrite(Luna)がNG span("point"→"idea")のみを書き換え
   (unchanged_ratio harness算出0.96)、局所QA(Luna)がPASS、再TTS
   (attempt5)がNORMALIZED_MATCHでPASSし、**最終的にHUMAN_REVIEW到達前に
   解決した(final_status=RESOLVED_BY_LOCAL_REWRITE)**。
3. 実装・実行中に自分で発見したharness側バグ2件を修正し、回帰テストとして
   固定した: (a) `generate_charon_english`のSTOPPED-fallthrough分岐は
   トップレベル辞書にasr_text等を含まないため誤ってNoneになっていた、
   (b) 独自の単語分割正規表現が曲線アポストロフィ(’)を単語構成文字に
   含めず、本当のNG原因(point/points)より先に無関係な字形差
   (let’s/let's)を誤検出していた(既存`classify_asr_match`と同じ
   `tokenize()`を呼ぶよう修正)。後者のバグにより最初のLocal Rewrite
   (旧attempt4)は誤ったspanを書き換えてしまい、修正後に正しいspanで
   やり直した(旧attempt4の記録は
   `local_rewrite_attempt4_span_bug_archive/`に保存、削除していない)。
4. Connected Speech Equivalence Layer(OPEN-122本体)をspan単位で直接
   呼んだ結果は`NOT_A_PHONEME_PREFIX_DROP`(would_rescue=False)であり、
   既存reconファイルの結論と実行時evidenceで一致した(comment_4の
   point/points差は、Production未配線という理由以前に、この層の想定
   形状[phoneme drop]自体に合致しない)。
5. Connected Speech role taxonomy(NARRATIVE_ENGLISH/HEADING_READOUT/
   KEY_PHRASE)を設計・データ化したが、現在の実配線はrole単位ではなく
   関数+明示フラグ単位であることを再確認・記録した(Production未配線)。
6. 実コスト合計¥4.66(budget¥20の23%、TTS実attempt5回・Luna呼び出し2回)。
   git commit・pushはユーザーのGit運用ルールに従い自動実行する。

---

## 1. 目的

ユーザー正式決定のTrial仕様(`docs/pm/ACTIVE_TASK_TC.md`初期版に転記した
逐語)を実行し、以下を実データで検証する:
- 英語TTS品質NG時の新しいretry順序(attempt1→即時attempt2→10分固定
  cool-down→attempt3→Local Rewrite→局所QA→再TTS)が実際に機能するか。
- Local Rewriteが「全文書き換えではなく、最小限のspanのみ」であることを
  機械的に検証できるか(unchanged_ratio閾値)。
- Connected Speech Equivalence Layerのrole based適用設計(Production未
  配線)と、comment_4の実際の救済可否。

Production正式経路(`er003_v1_sing01_voice01_generate.py`、
`er011_human_review_lock_01.py`、`er007_*`、`er019_*`)は無変更
(read-onlyでimportし、Review Lockデコレータの外側`.__wrapped__`のみ呼ぶ)。

## 2. 仕様

対象1件: Family X comment_4 canonical(`er019_output/family_x_pointless_
trial_01/meta/b1b/audit/tts_generation_results.json`から取得、role=
Comment[Story Recovery + Bridge to In One Line]、2026-09-26の実Family X
本番runで既にHUMAN_REVIEW_REQUIRED[ASR_VALIDATION_UNCERTAIN x3]へ到達
済み)。

- attempt1→NGなら即時attempt2→NGなら10分固定cool-down(実sleep)→
  attempt3→NGならLocal Rewrite(span限定)→局所QA PASS後のみ再TTS。
- attemptごとの記録項目: segment/canonical text/attempt番号/timestamp/
  gap秒/model/voice/route/TTS input sha256/ASR text/classification/
  PASS-NG/Human intervention(常にfalse)。
- 上限: budget-jpy 20、総TTS attempt上限12(dry-runで事前表示)。
  TTS_EXECUTION_MODE=STANDARD固定・BATCH禁止。
- Production module変更禁止・Human介入禁止(git diff・
  human_intervention:falseで機械確認)。

## 3. 対象と再現状況

対象: comment_4 canonical
`"The service looked like AI, but the work behind it was not always
done by AI alone. Now, let's bring the main point together."`

attempt1で即座に再現(ASR側が一貫して"point"を"points"と聞き取り、
classify_asr_match()が`ASR_VALIDATION_UNCERTAIN`[内容語差なし・ratio
がPASS閾値未満]と判定)。attempt1がPASSしなかったため、②の過去例
追加(最大2件)は不要と判断し実施しなかった(historical_examples_used=
null)。

## 4. attempt結果表(gap秒で10分待機を実証)

| attempt | timestamp(JST) | gapから前attempt(秒) | route | classification | PASS/NG | ASR text(要約) |
|---|---|---|---|---|---|---|
| 1 | 2026-09-26T12:00:55 | - | english_style_prefix | ASR_VALIDATION_UNCERTAIN | NG | "...main **points** together." |
| 2 | 2026-09-26T12:01:06 | **11.0**(即時) | english_style_prefix | ASR_VALIDATION_UNCERTAIN | NG | "...main **points** together." |
| 3 | 2026-09-26T12:11:17 | **611.0**(cool-down実測600.004秒+attempt3自体の生成時間) | english_style_prefix | ASR_VALIDATION_UNCERTAIN | NG | "...main **points** together." |
| 5(訂正後最終) | 2026-09-26T12:18:54 | - | english_style_prefix | NORMALIZED_MATCH | **PASS** | "...main **idea** together." |

10分待機の実証: attempt2→attempt3のgapは611.0秒(要求cool-down 600秒 +
実測`cooldown_actual_seconds`=600.004秒 + attempt3自体のTTS/ASR実行時間
約10秒)。`time.sleep`を実際に実行し、timestampの差分でも裏付けた
(短縮なし)。詳細: `er020_output/tts_cooldown_local_rewrite_trial_01/
run_summary.json`・`attempt_log.jsonl`・`attempt_summary.md`。

## 5. Local Rewrite前後(逐語)と局所QA結果

### 5.1 NG span特定(訂正後、正しいspan)
- `canonical_span_with_context`: "bring the main point together"
- `asr_span_with_context`: "bring the main points together"
- `canonical_changed_words`: ["point"] / `asr_changed_words`: ["points"]

### 5.2 Local Rewrite(Luna、model=gpt-5.6-luna)
- 書き換え前(全文): "The service looked like AI, but the work behind it
  was not always done by AI alone. Now, let's bring the main **point**
  together."
- 書き換え後(全文): "The service looked like AI, but the work behind it
  was not always done by AI alone. Now, let's bring the main **idea**
  together."
- `changed_span_before`="point" / `changed_span_after`="idea"
- unchanged_ratio: LLM自己申告0.9583 / harness独立算出0.96(語単位diff)
  → 閾値0.7以上のため`is_local_not_full_rewrite=True`(全文書き換えでは
  ないと機械的に確認)。

### 5.3 局所QA(Luna、別call)
`pass: true`、理由4件(意味保持["main idea"が"main point"と同義]/role
[Comment→In One Lineへのbridge]維持/矛盾なし/前後接続が自然)。

詳細JSON: `er020_output/tts_cooldown_local_rewrite_trial_01/
local_rewrite/{span.json, rewrite_prompt.txt, rewrite_result.json,
local_qa_result.json}`。

### 5.4 逸脱記録(実行時に発見・修正したharnessバグ、旧attempt4)
最初の実行では、harness独自の単語分割正規表現が曲線アポストロフィ(’)を
単語構成文字に含めなかったため、identify_ng_span()が本当のNG原因
(point/points)より先に無関係な字形差("let's" canonical="let’s" vs
ASR="let's")を最初の不一致として誤検出した。この誤ったspanに基づく
Local Rewriteは"let's"→"let us"に変更し、局所QA自体はPASSしたが、
再TTS(旧attempt4)のASR照合を書き換え前の古いcanonical_textと比較する
別のバグ([対比誤り]書き換え後textと比較すべきところを書き換え前textと
比較していた)もあり、見かけ上NGと誤表示された。両バグを
`asr_validation.tokenize()`(classify_asr_matchが使う正規化と同一)の
直接呼び出しと、比較対象を`rewrite["rewritten_segment"]`へ修正すること
で解消し、17件の回帰テストとして固定した(詳細は
`er020_tts_cooldown_local_rewrite_trial_01_test_01.py`の
`SingleAttemptFieldExtractionTest`/`NgSpanTest.
test_identify_ng_span_ignores_curly_vs_straight_apostrophe`)。旧
attempt4の生データは削除せず
`er020_output/tts_cooldown_local_rewrite_trial_01/
local_rewrite_attempt4_span_bug_archive/`に保存した。

## 6. 再TTS結果

attempt5(訂正後、正しいspanに基づく再TTS): ASR text="The service looked
like AI, but the work behind it was not always done by AI alone. Now
let's bring the main idea together."、classification=
NORMALIZED_MATCH(表記正規化後に一致)、PASS=True。
`final_status=RESOLVED_BY_LOCAL_REWRITE`(Human Review到達前に解決)。

## 7. Connected Speech role方式の設計と適用範囲表

`er020_tts_cooldown_local_rewrite_trial_01.py`にrole taxonomy
(`ROLE_TAXONOMY`: NARRATIVE_ENGLISH={full_story_part1-3, comment_1-4,
preview, topic_intro, in_one_line} / HEADING_READOUT={point_one_heading,
point_two_heading} / KEY_PHRASE={kp_en_component})と、現在の実配線
(`CURRENT_WIRING_BY_SEGMENT`、関数+明示フラグ単位)を分離してデータ化した
(Production未配線、`connected_speech_role_taxonomy.md`に出力)。

同じNARRATIVE_ENGLISH roleでも、comment_1-4/preview/topic_intro/
in_one_lineは`voice01.generate_charon_english()`(equivalence layer引数
自体が存在しない関数)経由のためFalse、full_story_part1-3は
`news_tail_fix.generate_news_narration_wide_margin()`(引数あり・
呼び出し側True)経由のためTrue、という「role単位ではなく関数単位」の
実態を、テスト(`test_current_wiring_is_finer_grained_than_role`)で
固定した。

comment_4のspan("bring the main point together" vs "bring the main
points together")を、OPEN-122 Equivalence Layer本体
(`er011_connected_speech_equivalence_layer_production_01.
classify_connected_speech_equivalence`)へ直接渡した結果は
`NOT_A_PHONEME_PREFIX_DROP`(would_rescue=False)。docs/pm/
recon_connected_speech_scope_01.md 4節の結論(Production未配線という
理由以前に、この層が想定する「phoneme drop」形状自体に一致しない)を、
本Trialのharnessで独立に実行時evidenceとして再確認した。

## 8. 既存即時retryとの比較所見

既存Production cascade(`generate_charon_english`内蔵、max_attempts=3・
待機なし・連続実行)は、同一のASR誤認識signatureに対しattempt1-3のいずれも
NGで打ち切っていた(実データ、2026-09-26のFamily X本番run)。本Trialの
harnessでも、10分の待機を挟んでも(attempt3)同一のASR誤認識が再現し、
「時間を空けるだけ」ではこの種の語彙起因ASR誤認識は解決しないことを
実データで示した(`TTS-RETRY-COOLDOWN-HYPOTHESIS-ANALYSIS-01_REPORT.md`
の既存知見と整合)。一方、Local Rewrite(spanのみの言い換え)は、この種の
「ASRが特定の1語を一貫して誤認識する」ケースに対し、本Trialの1例では
有効だった(全文の意味・role・前後接続を維持したまま解決)。

## 9. QCD

- Quality: attempt1-3は実データで完全再現(3/3 NG、同一classification)。
  Local Rewrite→局所QA→再TTSまで実行し、PASS達成。回帰テスト17件全PASS
  (API/sleed mock、¥0)。
- Cost: 実コスト合計¥4.664(budget¥20の23%)。内訳: gemini(TTS)¥4.18・
  openai_asr(ASR)¥0.21・openai(Luna、Local Rewrite+局所QA)¥0.27。
  別途、harness実装中にmkdir漏れで1回分のTTS呼び出しが無駄になった
  (約¥0.8、この¥4.664の集計には含まれない別ログ)。TTS実attempt数は
  1(初期バグによる無駄)+3(cool-down系列)+1(誤ったspanでの再TTS、
  旧attempt4)+1(訂正後の再TTS、attempt5)=6回、budget上限12の半分。
- Delivery: 予定通り1対象で完結。過去例2件の追加は再現成功のため不要。

## 10. Sonnet仮分類

**VALIDATED(Trial限定)**。cool-down・Local Rewrite・Connected Speech
role taxonomyのいずれもProduction未配線のまま。実データ1例
(comment_4)でLocal Rewriteが機能することを示したが、汎化性(他segment・
他種類のASR誤認識への適用可否)は未検証。実行中に発見したharness側の
2バグ(STOPPED-fallthrough時のフィールド欠落、独自tokenizerの
アポストロフィ非対応)は本Trialのharness内バグであり、Production側の
`classify_asr_match`等には影響しない(git diffで無変更を確認済み)。

## 11. Fable評価

(1)ユーザー決定仕様どおりの順序(attempt1→即時attempt2→10分待機→attempt3→
Local Rewrite→局所QA→再TTS)を実データで実証。10分待機はtime.sleep(600)
実行、timestamp差611秒で確認。Human介入なし。記録項目(segment/canonical/
attempt/timestamp/gap/model/voice/route/input hash/ASR/classification/
PASS-NG/human intervention)は網羅。(2)cool-down自体の効果: attempt1〜3は
すべて同じ誤認識(point→points)で、10分待機ではTTS/ASRの結果は変わらな
かった(この語の場合は時間依存の揺れではなく、TTSの発話とASRの単複判定に
由来する再現性のあるNG)。cool-downデータは1例のみで、有効性の判断は蓄積
待ち。(3)Local Rewrite: span特定は当初harnessのトークナイズ不一致(曲線
アポストロフィ)で誤span(let's)を書き換えるバグがあり、修正後に正しい
span(point→idea)へ収束。unchanged_ratio 0.96で全文書き換えでないことを
機械確認。局所QA PASS(意味・role・接続維持)。再TTSでNORMALIZED_MATCH
PASS、Human Review到達前に解決。『bring the main idea together』は意味
保持だが英語としてやや珍しい表現(『pull the main idea together』等が
より自然)—局所QAが自然さを厳しく見ていない可能性を留意点として記録。
(4)Connected Speech: role taxonomy(NARRATIVE_ENGLISH/HEADING_READOUT/
KEY_PHRASE)を設計。実態は『role単位ではなく関数単位』で適用が決まって
おり(comment群はvoice01.generate_charon_english経由で等価層引数なし)、
Production配線時はここを関数横断のrole判定へ変える必要がある(未配線)。
point→pointsが等価層で救済されないことは実行時evidenceでも一致。
(5)harnessバグ2件(STOPPED分岐のasr_text復元、トークナイズ)を修正・
test 17件で固定。無駄TTS 1回(mkdir漏れ)を含め¥4.66。

## 12. 分類

**VALIDATED**(Trial限定。cool-down・Local Rewrite・role taxonomyは
Production未配線)。ユーザー判断事項: ①cool-down+Local Rewrite経路を
Production retry仕様の候補(APPROVED_FOR_PRODUCTION)にするか、それとも
他segment・他NG種別での追加データ(2〜3例、¥10程度)を先に取るか(Fable
推奨: 追加データを先に取る。理由: cool-downの効果は1例では判断できず、
Local Rewriteの自然さQAも1例)。②Connected Speech適用範囲をrole単位へ
変更するProduction改修(Full Story/Comment/Preview/Topic intro/In One
Line=適用、見出し読み/Key Phrase=対象外)を着手するか(Fable推奨: ①の
追加データと同時に設計、実装はユーザー承認後)。③Local Rewrite局所QAに
『英語としての自然さ』の明示基準を加えるか(Fable推奨: 加える、ただし
Comment等の非Fact segment限定)。
