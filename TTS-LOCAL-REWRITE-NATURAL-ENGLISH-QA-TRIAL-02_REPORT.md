# TTS-LOCAL-REWRITE-NATURAL-ENGLISH-QA-TRIAL-02

DEV/Trial(最大分類VALIDATED)。Natural English Gateを含む7項目QAは
Production未配線(APPROVED_FOR_PRODUCTIONなし)。

## 要点(6行)

1. 前回Trial(TTS-COOLDOWN-LOCAL-REWRITE-TRIAL-01)が採用した1語置換
   ("main point"→"main idea")は、TTS/ASRには通ったが「英語として自然
   か」を独立Gateとして評価していなかった。本Trialでは、意味/role/Fact/
   文脈の4QAに加え、独立した**Natural English Gate**を含む7項目QAを
   新設し、局所Rewrite候補を複数(新規5件+前回"main idea"版=6件)生成して
   比較した。
2. 独立judge(Luna、前回とは別call)は、前回採用の"bring the main idea
   together"を**Natural English Gate不合格**と判定した
   (「不自然/stiltedで、'sum up the main idea'等の方が自然」)。一方、
   新規に生成した5候補は本実行では**5/5とも7 Gate全PASS**だった。
3. 全7 Gate PASSの候補の中から、TTS安定性ヒューリスティック
   (単数/複数混同リスク語数)が最少の候補を機械的に選定し
   (`sum up the key lesson`)、採用候補のみをTTS(STANDARD)+ASRで実検証
   した。**attempt1でNORMALIZED_MATCH・PASS**(cool-downなし、attempt
   上限2のうち1回で解決)。
4. Natural English Gate・局所性(criterion 6)・非全文Rewrite(criterion
   7)はharness側で機械判定、意味/role/Fact/文脈/自然さの5項目はLuna判定
   (json_schema strict)。FAIL候補は一切TTSへ渡らないことをテストで固定
   (`SevenGateIntegrationTest`)。
5. 実行時に発見したharness実装バグ1件を修正・回帰テスト化: 候補生成
   プロンプトの指示不足により、初回実行では`rewritten_segment`に全文
   ではなく置換phraseのみが返り、局所性判定(criterion 6/7)が全候補で
   誤ってFAILしていた。プロンプトを明確化し、再発防止の安全網
   (`validate_candidate_is_full_segment`)を追加して再実行、正しく
   機能した(詳細§7-補足)。
6. 実コスト合計¥3.085(budget¥15の21%、内訳: openai[Luna候補生成+QA
   2call]¥2.23・gemini[TTS]¥0.81・openai_asr[ASR]¥0.04)。offline test
   14件全PASS(API呼び出し0件、¥0)。git commit・pushはユーザーのGit運用
   ルールに従い自動実行する。

---

## 1. 目的

前回Trial(TTS-COOLDOWN-LOCAL-REWRITE-TRIAL-01)の指摘
「TTSが通ったこと」と「英語として自然であること」は別問題)に基づき、
Local Rewrite後・TTS前のQAへ、意味保持/role保持/Fact非矛盾/前後接続に
加えて**独立したNatural English Gate**を新設し、複数の局所Rewrite候補を
比較したうえで最終候補を1件選定し、選定候補のみを実TTS/実ASRで検証する。
Production正式経路(`er003_v1_sing01_voice01_generate.py`・
`er011_human_review_lock_01.py`・`er007_*`・`er019_*`)は無変更
(read-onlyでimport)。前回Trial harness
(`er020_tts_cooldown_local_rewrite_trial_01.py`)も無変更、純粋関数
(`compute_unchanged_ratio`/`run_single_tts_attempt`/`_extract_json_object`
等)のみread-onlyでimportして再利用した。

## 2. QA定義(7項目、Natural English Gate)

ユーザー正式決定(`docs/pm/ACTIVE_TASK_TC2.md`)の逐語:

1. 元の意味を保持(LLM判定)
2. segment roleを保持(LLM判定)
3. 記事Factと矛盾しない(LLM判定)
4. 前後文脈と自然につながる(LLM判定)
5. **英語として自然で一般的な言い回し(Natural English Gate)**(LLM判定)
   — PASS条件: 文法的に成立するだけでなく、実際の会話・ナレーションで
   自然に選ばれる表現。FAIL: 文法的には可能だが普通あまり言わない/
   意味は分かるが不自然/LLM的には成立するが慣用的でない/元文構造を無理に
   維持してぎこちない/TTSを通すためだけの不自然な言い換え。
6. 発音問題を起こしたword/span周辺だけを必要最小限変更(harness機械判定)
   — 元canonical内の問題span位置("bring the main point together"、
   token index 20-25)から前後3 token以内に、候補との差分がすべて収まって
   いるかをdifflibで検証。
7. 不要な全文Rewriteをしない(harness機械判定)— harness独立算出の
   `unchanged_ratio`(語単位diff)が閾値0.7以上か(前回Trialと同一閾値・
   同一関数`compute_unchanged_ratio`を再利用)。

1-5はLuna(`gpt-5.6-luna`、reasoning effort=high、json_schema strict、
候補6件まとめて1 call)、6-7はharness側の機械判定。**全7項目PASSの候補
のみ**が採用候補選定の対象になり、FAIL候補は一切TTSへ渡らない
(`build_full_candidate_records`/`select_final_candidate`、
`SevenGateIntegrationTest`で固定)。

## 3. Original/前回Rewrite/今回候補一覧

対象: Family X comment_4 canonical(前回Trialと同一、
`er019_output/family_x_pointless_trial_01/meta/b1b/audit/
tts_generation_results.json`から取得)。問題span:
`"bring the main point together"`(ASRが一貫して"point"を"points"と
聞き取り、前回Trialで3回連続ASR_VALIDATION_UNCERTAIN)。

| id | 種別 | 変更後span | 全7 Gate PASS |
|---|---|---|---|
| Original | - | (無変更、"point") | - |
| 前回Rewrite(candidate_main_idea_previous) | single_word_swap | "bring the main idea together" | **False**(Natural English Gate不合格) |
| 候補1(新規) | single_word_swap | "bring the main threads together" | True |
| 候補2(新規) | short_phrase_rewrite | "sum up the story's main takeaway" | True |
| 候補3(新規) | short_phrase_rewrite | "bring the central message into focus" | True |
| 候補4(新規) | short_phrase_rewrite | "bring the main lesson home" | True |
| 候補5(新規、**採用**) | short_phrase_rewrite | "sum up the key lesson" | **True** |

新規候補はLuna 1 call(json_schema strict、`build_candidate_gen_schema`)
で5件生成、前回"main idea"版はread-only参照(`er020_output/
tts_cooldown_local_rewrite_trial_01/local_rewrite/rewrite_result.json`)
で6件目として追加(スタイルの幅: single_word_swap 2件・
short_phrase_rewrite 4件)。詳細:
`er020_output/tts_local_rewrite_natural_english_qa_trial_02/
candidate_gen_raw.json` / `candidates.json`。

## 4. 各候補のNatural English判定と理由

Luna(独立judge、候補生成callとは別call)による判定理由(抜粋):

- **前回"main idea"版(FAIL)**: 「plain point→ideaの置換そのものであり
  同程度に自然」だが「'bring the main idea together'は不自然でstilted。
  ネイティブなら'sum up the main idea'や'bring the main idea into
  focus'と言う方が自然」。
- **候補1 "bring the main threads together"(PASS)**: 「ナレーションで
  ストーリーを統合する際の確立した言い回しで、単純なpoint→ideaの置換
  より自然」。
- **候補2 "sum up the story's main takeaway"(PASS)**: 「'sum up'は
  一般的な口頭の転換句、'main takeaway'は説明的ナレーションで慣用的」。
- **候補3 "bring the central message into focus"(PASS)**: 「'bring...
  into focus'は締めのナレーションで標準的・慣用的なcollocation」。
- **候補4 "bring the main lesson home"(PASS)**: 「'bring...home'は
  慣用的な強調表現。'bring the main idea together'はぎこちない」。
- **候補5 "sum up the key lesson"(PASS、採用)**: 「'sum up the key
  lesson'は口語の説明的英語における通常の締めの言い回し」。

全文・生プロンプト・生応答: `er020_output/
tts_local_rewrite_natural_english_qa_trial_02/qa_raw.json` /
`qa_results.md`。

## 5. 最終採用候補と選定理由

全7 Gate PASSの候補5件(候補1-5、前回"main idea"版は不合格のため対象外)
から、`select_final_candidate()`が以下の決定的規則で1件を選定した:
(1) TTS安定性ヒューリスティックのrisk flag数(単数/複数混同リスク語+
語末破裂音語)が最少の候補を優先、(2) 同点ならunchanged_ratioが高い方
(より最小限の変更)、(3) それでも同点ならid昇順。

結果: risk flag数は候補1=4・候補2=4・候補3=5・候補4=5・**候補5=2**
(最少)であり、**候補5「sum up the key lesson」**を採用した。

選定理由(harness自動生成、`selected.json`より、risk flag内訳は
`candidates.json`で確認):
> 全7 Gate PASSの候補は5件(['1','2','3','4','5'])。その中でTTS安定性
> ヒューリスティックのrisk flag数が最少(plural_s_risk=['lesson'],
> word_final_plosive=['up']、合計2件)かつunchanged_ratio=0.84である
> '5'を採用。Natural English Gateの理由: 'sum up the key lesson' is a
> normal concluding phrase in spoken explanatory English.

(注: このヒューリスティックはリスクの**目安**であり、実TTS/ASRの結果を
保証しない。診断的事実として、'point'/'points'は既存
`protected_check()`内で既にbenign plural pairと判定されるにもかかわらず
`classify_asr_match()`全体はASR_VALIDATION_UNCERTAINのままだった
[正規化後ratio 0.96が合格閾値未満]ことを本Trialで直接確認済み。よって
最終判断は必ず実TTS/ASR結果で行う設計とした。)

## 6. 7 QA結果(採用候補)

採用候補「sum up the key lesson」(全文: "The service looked like AI,
but the work behind it was not always done by AI alone. Now, let's sum
up the key lesson."):

| # | 項目 | 判定 | 理由(要約) |
|---|---|---|---|
| 1 | 意味保持 | PASS | "the key lesson"は原文の"main point"と等価な機能、"sum up"は締めの要約を保持 |
| 2 | role保持 | PASS | Comment(ストーリー回収+In One Lineへのbridge)として機能を維持 |
| 3 | Fact非矛盾 | PASS | 新規factを追加せず、原文・前後文脈と矛盾しない |
| 4 | 前後文脈接続 | PASS | 人間concierge説明からの流れを受け、In One Lineへ自然に接続 |
| 5 | Natural English Gate | PASS | 口語の説明的英語における通常の締めの言い回し |
| 6 | 局所性(harness機械判定) | PASS | diff token range [20,25]、許容window[17,25]内 |
| 7 | 非全文Rewrite(harness機械判定) | PASS | unchanged_ratio=0.84(閾値0.7以上) |

全項目PASS。詳細: `candidates.json`(id="5"のレコード)。

## 7. 変更範囲

- 変更前span: `"bring the main point together"`(5 token、canonical内
  token index 20-24)
- 変更後span: `"sum up the key lesson"`
- unchanged_ratio(harness独立算出、語単位diff): 0.84(28語中の大部分が
  無変更、閾値0.7を上回る)
- 局所性: diff token range [20,25]は許容window[17,25]内(前回harnessと
  同じcontext_words=3の判定ロジックを再利用)

### 補足: 実行時に発見・修正したharnessバグ

初回実行時、候補生成プロンプトが「'rewritten_segment'は全文であること」
を明示していなかったため、Lunaが`rewritten_segment`へ置換phraseのみ
(例: `"sum up the main takeaway"`)を返し、5候補全てが局所性判定
(criterion 6/7)で誤ってFAILし、`NO_CANDIDATE_PASSED_ALL_SEVEN_GATES`に
到達した(TTSは未実行、追加コストなし)。プロンプトへ「rewritten_segment
は元segment全文をverbatimで含み、問題phraseのみ置換すること」を明記して
再実行し、正しく全文が返るようになったことを確認した。再発防止のため、
`validate_candidate_is_full_segment()`(canonical_textとの書き出し一致を
機械確認、不一致ならその候補を強制的にall_seven_gates_pass=Falseへ)を
追加し、回帰テスト3件(`FullSegmentFormatSafetyNetTest`)で固定した。

## 8. TTS/ASR結果

採用候補のみ、Production関数`voice01.generate_charon_english`経由
(Review Lockデコレータの外側`.__wrapped__`、前回harnessと同一技法)で
TTS実行(STANDARD、attempt上限2、cool-downなし)。

| attempt | timestamp(JST) | route | classification | PASS/NG | ASR text |
|---|---|---|---|---|---|
| 1 | 2026-09-26T13:36:14 | english_style_prefix | NORMALIZED_MATCH | **PASS** | "...let's sum up the key lesson." |

attempt1でPASS(NORMALIZED_MATCH、表記正規化後に一致)。model=
gemini-2.5-pro-preview-tts、voice=Charon、tts_execution_mode=STANDARD。
attempt2は不要(cool-downも未実施)。詳細: `attempt_log.jsonl` /
`attempt_summary.md` / `run_summary.json`。human_intervention=False
(全attempt共通)。

## 9. 前回"main idea"との比較

| 観点 | 前回Trial("main idea") | 今回採用("sum up the key lesson") |
|---|---|---|
| QA項目数 | 4項目(意味/role/Fact/文脈) | 7項目(+局所性+非全文+**Natural English Gate**) |
| Natural English Gate(本Trialで遡及適用) | **FAIL**("bring the main idea together"は不自然・stilted) | PASS(口語の通常の締めの言い回し) |
| TTS/ASR結果 | PASS(attempt5、NORMALIZED_MATCH) | PASS(attempt1、NORMALIZED_MATCH) |
| unchanged_ratio | 0.96(1語のみ変更) | 0.84(短phraseへの変更) |

前回"main idea"版は、TTS/ASRには通ったが、独立したNatural English Gateを
本Trialで遡及適用した結果、**不合格**と判定された。「TTSが通ること」と
「英語として自然であること」は別問題であるという前回の指摘が、本Trialの
独立judgeによって裏付けられた。一方、今回新規生成した5候補は
(本実行では)5/5とも自然さGateを含む7項目全てにPASSしており、単純な
1語置換に固執せず短phraseへ言い換える選択肢を与えたことで、より自然な
候補が得られた。

## 10. QCD

- **Quality**: 独立judgeによりNatural English Gateが実際に機能し、前回
  採用文を不合格と判定できることを確認。全7 Gate PASSの候補のみが
  TTSへ渡ることをコード・テスト両方で保証(`SevenGateIntegrationTest`)。
  offline test 14件全PASS(API呼び出し0件、¥0)。
- **Cost**: 実コスト合計¥3.085(budget¥15の21%)。内訳: openai(Luna、
  候補生成1call+QA1call)¥2.23・gemini(TTS 1attempt)¥0.81・
  openai_asr(ASR 1回)¥0.04。TTS実attempt数1(上限2の半分)。
- **Delivery**: 予定通り1対象(comment_4)で完結。実行時に発見した
  harnessバグ1件を修正・回帰テスト化し、再実行して正常動作を確認した
  (無駄になったのは候補生成+QA各1callのみ、¥1.72相当、追加TTSコストは
  発生していない)。

## 11. Sonnet仮分類

**VALIDATED(Trial限定)**。Natural English Gateを含む7項目QAは
Production未配線のまま。実データ1例(comment_4)で、独立judgeが前回採用
文を「不自然」と判定し、代替の複数候補が「自然」と判定される実例を
示したが、以下の留保点がある:
- サンプルは1 segment・1種類のASR誤認識(単数/複数混同)のみ。他segment・
  他種類のNG(homophone等)への汎化性は未検証。
- Natural English Gateの判定は同一モデル(Luna)の1 callによる自己完結
  judgeであり、人間評価・別モデルでのクロスチェックは行っていない
  (本Trial内で2回実行し、両方とも前回"main idea"版がFAIL・新規候補が
  概ねPASSという同じ傾向を示したが、判定基準そのものの妥当性は今回の
  範囲外)。
- 選定規則(TTS安定性ヒューリスティックのrisk flag数によるtie-break)は
  機械的ヒューリスティックであり、言語学的な正確さの保証ではない
  (§5の注記参照)。
- 実行時に発見したharnessバグ(候補生成プロンプトの指示不足)は本Trial
  自身の実装バグであり、Production側`classify_asr_match`等には影響しない
  (git diffで無変更を確認済み)。

## 12. Fable評価

(1)Natural English Gateを独立必須Gateにしたことで、前回『TTSが通ったから
採用』だった "bring the main idea together" が不合格となり、自然な候補
(採用: "sum up the key lesson")へ置き換わった。候補複数生成→7 QA→1件の
みTTSの流れは無駄な課金を抑えつつ機能(¥3.09、TTS attempt1でPASS)。
(2)留意: 判定はLuna 1 callの自己判定で人間評価・クロスチェックなし。Fable
の見立てでは候補1 "bring the main threads together"・候補2 "sum up the
story's main takeaway" が原文の意味(まとめる)に最も近く、採用候補の
"key lesson" は『教訓』へ意味がわずかに寄る(Commentのrole上は許容範囲)。
採用はTTS安定性ヒューリスティック(threadsの複数形/s/リスク回避)による
もので合理的。
(3)harnessバグ1件(候補が全文でなく置換句のみ返る)を修正し安全網+test 3件
で固定、test 14件PASS。
(4)n=1 segment・1種類のNG(単複)のみ。
(5)Co-Authored-Byトレーラー欠落は運用上必須ではなく対応不要。

## 13. 分類

**VALIDATED**(Trial限定、Production未配線)。ユーザー判断事項:
①cool-down+Local Rewrite(7項目QA、候補複数生成→Natural English Gate→
1件TTS)をProduction retry仕様候補にするか、他segment・他NG種別で追加
データ(2〜3例、¥10)を先に取るか(Fable推奨: 追加データ先行)。
②Connected Speech適用範囲のrole単位改修の着手(Fable推奨: ①と同時に設計、
実装は承認後)。
③Natural English判定を同一モデル1 callのままにするか、2回一致等を入れるか
(Fable推奨: 追加データ取得時に2回一致を試す)。
