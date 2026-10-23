# ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ②英米綴り ROOT_CAUSE_01
(UKUS 委任_01 / 2026-10-23 / read-only・API 0円 / Production・Prompt・flag・閾値・脚本の変更 0 / 原文=`docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER.md` §1②・§4②)

## 0. 結論
- 直接原因: 『開いた窓』Adv `full_story_part3_c12` の結末文の `speciality`(英綴り)を、Primary(OpenAI gpt-4o-mini-transcribe)もSecondary(Azure en-US)も `specialty`(米綴り)と転写した。**現行の判定連鎖のどの層にも「英米綴り差を同値とみなす一般的な仕組み」が無く、1語差のTRUE_CONTENT_MISMATCHとして3回NG→10分cooldown→Local Rewrite(`speciality`→`forte`)まで進んだ。**
- 根本原因(設計上の前提の欠落、3点):
  1. **英米綴り吸収が13ペアの閉じた手書き表だけ**(`er006_preprod_hardening_01_validation.py:56-62` `BR_AM_SPELLING_PAIRS`、`normalize_text` :446-447)。`speciality` はその13ペアに無い。規則(-ise/-ize等)も辞書も無い。
  2. **er109(同音・異表記救済v1)は「音素列が交わる場合のみ同値」**(`er109_asr_orthographic_equivalence_01.py:12-14`)で、許容辞書は記号・略語のみ(:17)。`speciality`(CMU `S P EH2 SH IY0 AE1 L IH0 T IY0`)と `specialty`(`S P EH1 SH AH0 L T IY0`)は**音節数が違い音素が交わらない**(音素列の正規化距離0.30)ため、設計上救済されない。つまり「綴り差=発音差が小さい」という暗黙の前提が、英米綴りの一部(-ity/-ty、aluminium/aluminum等)で崩れる。さらに `jewellery` 等は**CMU辞書に未登録**で、fail-closed原則により判定不能=非同値になる。
  3. **LR(Local Rewrite)の入口に「NG span=正当な綴り差のみ」の判定が無い**。`identify_ng_span`(`er020_tts_retry_local_rewrite_01.py:181`)はcanonical/ASRの差分語をそのまま問題spanとして扱い、Luna(gpt-6-luna)が `forte`(単語置換、rewrite_type=single_word_swap)等の候補を作り、7ゲート(意味/役割/事実/文脈/自然さ/局所性/非全文書換)を全通過して採用された(`er011_output/local_rewrite_recovery/run_sf_prod_01/b1b/local_rewrite_recovery_full_story_part3_c12.json` selection.selected id=1)。**ゲートは「意味が保たれるか」を見るため、綴り差のみの偽NGを書換えで消す行為自体を止める条件が無い。**

## 1. 現行判定連鎖と『開いた窓』c12で通った経路(証拠)
| 段 | 内容 | c12での結果 | 根拠 |
|---|---|---|---|
| Primary ASR | OpenAI gpt-4o-mini-transcribe | `...Vera's specialty.` | `er011_output/attempt_history.jsonl:17415` attempts_detail[0..3] |
| 分類 | `val.classify_asr_match` | TRUE_CONTENT_MISMATCH(`normalize_text`が13ペア表でspecialityを写像せず) | 同上 primary.label |
| 既存救済 | CMU alternate / M1 / er109 | いずれも非該当(er109は`phoneme_differs`) | 本調査で再現: `er109.evaluate(canon, asr)` → `NOT_EQUIVALENT: phoneme_differs` |
| Secondary | Azure STT(en-US) | 同じく `specialty`(accepted=false、reason `secondary_not_accepted`) | attempt_history.jsonl:17415 secondary.text |
| 3rd ASR(Whisper) | 本文segmentでは呼ばれない(KP3V=`vote_required`時のみ。`er006_secondary_asr_01.py` `_vote = actx.get("vote_required")`)。仮に呼んでも英語3エンジンは同じ米綴り傾向 | 未使用 | 同ファイル `signals`/`_vote` 周辺 |
| retry | attempt 1,2,3とも同じ転写(音声sha256は毎回違う) | NG×3 | attempts_detail 3件 + 4件目 |
| cooldown | 3回NG後に600秒待機(`er020_tts_retry_local_rewrite_01.py:57,64`) | 636.49秒 | attempt_history.jsonl:17415 duration_seconds、cost_log.jsonl:173→174のtimestamp差(03:18:56→03:28:58) |
| Local Rewrite | Luna候補5件→QA→選定 | id=1 `forte` 採用(`was Vera's speciality`→`was Vera's forte`) | LRファイル selection |
| 4回目TTS/ASR | `forte` 版を生成・検証 | OK(RESOLVED_BY_LOCAL_REWRITE) | attempt_history.jsonl:17414 |
| audio_text_deviation / ページ | 原稿(`speciality`)を表示、音声は `forte`(監査記録のみ) | 原稿と音声が不一致のまま | `PHASE4_RESULT_01.md:23,66-68` |
| HR Lock | c12では到達せず(LRで解消)。ただし `human_review_queue.jsonl` に2 stepが記録 | 記録あり | `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`(timestamp 2026-10-23T12:29:00) |

**どの段で「書き換え」が選ばれたか**: 3回NG後のcooldown終了直後に、`run_local_rewrite_recovery`(`er020_tts_retry_local_rewrite_01.py:708`)が起動し、`select_final_candidate`(:686)が最小差分の候補(single_word_swap)を選んだ。選定基準は7ゲートの全通過と局所性(unchanged_ratio=0.9)で、**元の綴りを維持する(=偽NGを許容する)選択肢は候補に存在しない**。

## 2. er109設計との照合(なぜ設計範囲外だったか)
- er109の目的は「発音が同一なのに転写の表記が違うだけ」(one↔1、Mr.↔mister等、`er109...py:6-8`)。判定は音素列の交差(:12-14)、新規許容辞書は閉じた記号・略語表のみ(:17)。`docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/INVESTIGATION_01.md:17` も `normalize_text` の英米綴り13組(:56 `BR_AM_SPELLING_PAIRS`)を「既存の吸収」と記録しており、**拡張可否は検討されたが、英米綴り全般は範囲外のまま**(PATTERN_CATALOG系は数・記号・同音語が中心)。
- 過去Trial(OPEN-459、three↔3:00の偽同値是正)で確立した原則は「欠落・付加は同値にしない/音素が1つでも違えば同値にしない/判定不能はfail-closed」。**この原則自体は正しいが、英米綴り差は『音素が違っても同じ語』という別カテゴリ**であり、音素厳密一致主義の下では構造的に救済できない(本件の根本)。したがって対策は音素層の緩和ではなく、**別カテゴリ(語彙的に同一語の地域綴り)を辞書で明示する新層**でなければならない(DESIGN_01)。
- 旧 er003 検証(`er003_audio_tts_asr_safety.py:253-258,334-370`)には `-ise/-ize`・`-our/-or` の規則吸収があったが、これは旧世代の簡易検証で、現行Production検証(val/er006/er078)には引き継がれていない(5接尾辞のみ・`grey/gray`等は「実務で問題になったら明示追加」と記載)。

## 3. 定量(API 0円・保存データの機械抽出)
手段: 英米異綴り辞書(VarCon 2020.12.07 + breame 0.1.2、DESIGN_01 §2)で、canonical/ASR転写のdifflib 'replace'が辞書対になっている行を抽出し、現行判定(`classify_asr_match`+`_step_alternate_pass`)と、US正規化後の再判定(上限シミュレーション)を比較。スクリプト・生データ=`work/ukus_census_01.py` / `work/ukus_census_01.json`。母集団: 全`*tts_generation_results*.json`のprimary 2,470行・azure 172行(distinct, 英語, 全Family)+`pairs_02.jsonl` 3,039(英語)+HR queue 426 step+LR recovery 30件。

| 区分 | 件数 | 内容 |
|---|---|---|
| 英米異綴りが差分に含まれる行(primary/azure/pairs/HR/LR) | 14/1/18/6/1 | 重複(同一canonical×attempt×複製)を含む行数 |
| **英米綴り差のみが原因のNG(他に差なし)** | **実質1事象**(c12 speciality。primary 1・HR queue 2 step・LR 1として重複計上) | 唯一、LRまで進んだ事象 |
| 英米綴り差が混在要因の既存NG | 4事象(`aging/ageing`+`center/centre` [pool_benches_pilot_02 a2]、`neighborhoods/neighbourhoods` [同b1b、他に固有名詞聞き違い]、`cancelling/canceling` ×2 [pool_subscriptions b1b、他にも差]、`acknowledgment/acknowledgement` [space_weapons a2・HR queue 4 step、他にも差]) | 混在のため綴り差だけを直しても救済されない(英米綴りを含むNG行20のうちUS正規化でPASSに転じたのは6=c12の4行+aging/ageingの2行、残り14行は他の実差が残る)。すべてFamily A/B/C系の保存データ |
| 現行PASSなのに対策後NGになる行(悪化) | **0** | 全4母集団で `now_PASS_sim_NG=0` |
| 対策後(US正規化)に新たにPASSする行 | 6行(c12の4行[primary/HR 2 step/LR]+aging/ageing混在の2行[他要因はHIGH_SIMILARITY_SAFEで通過]) | 目視分類は検証計画(DESIGN_01 §6)で全件実施 |

### 3-1 不要retry・LRの費用推定(c12)
- 費用: `cost_log.jsonl:168-180`(c12 b1b)を `er019_family_x_audio_production_runner_01.compute_cost_jpy_so_far` で計算: **合計1.47円**(Gemini TTS 0.49・OpenAI ASR 0.09・Azure 0.68・Luna 0.20)、うちattempt 1(必要な最初の1回)0.37円→**不要分≒1.10円**(量産単価70円の約1.6%)。
- 時間: cooldown含め**636.49秒**(約10.6分)。1語の綴り差で10分待機する。
- **本質的な被害は費用ではなく品質**: 原稿(ページ表示)は `speciality`、音声は `forte` になり、**脚本変更(監査上のaudio_text_deviation)が発生**する。Z(原作忠実)では原作結末文の改変に当たる。HR Lock到達時は更に人手が要る。
- 頻度見込み(小標本、参考): 保存データでcanonicalにUK専用綴り語があった行のうち、OpenAIが米綴りに変えた比率=5/8(英米異綴りの`oversized`誤検出を除く。n小)、c12は4/4(OpenAI・Azure両方)。Z台本はUK作家の原作(Saki等)由来でUK綴りが残りやすく(書き手出力114ファイル中18ファイルにUK専用綴り語。ほぼ`speciality`の再実行による重複、`work/ukus_exposure_01.py`)、Xの保存記事は294ファイル中2ファイル(`defence`)と少ない。**Z新作では1記事あたり複数語のUK綴りが入る可能性があり、同事象が量産で再発する構造的リスク**(例: UK作家作品でUK専用綴り3語/記事×米転写率60%≒1.8事象/記事×約1.1円+約10分/事象+脚本改変)。実際の頻度はZの次作品で要実測。
- A/B/C系の保存データにも混在要因が4事象あるが、A/B/C凍結(§27-3)のため調査範囲外(参考記録のみ)。

## 4. 過去Trial・既存仕様との整合
- `three↔3:00`是正(OPEN-459 委任_05、`er109...py`裸数詞): 本件の対策は**数・記号spanに触れない**(語の1:1置換のみ)ので衝突しない。
- ASR-HOMOPHONE包括対策のfail-closed原則(欠落・付加を同値にしない、判定不能は非同値): 新層も**欠落・付加は同値にしない**。辞書にない語は非同値のまま(規則フォールバックは制限付き)。
- 固有名詞(PNAP/①側): `Grey/Gray`等の人名・`Centre`等の地名は**新層の対象外**(entity token)とし、既存PNAP・①の再設計に委ねる(境界の取り決めはOpus論点)。
- KP 3-ASR投票(`er104`)・Store再利用guard・値/否定guard(`er078`)は、er109の既存hookに乗せるため追加配線不要(DESIGN_01 §3)。

## 5. 追加で判明した周辺事実(設計に影響)
- 既存の13ペア表(`BR_AM_SPELLING_PAIRS`)は`str.replace`の部分文字列置換で語境界を見ない(`val.normalize_text` :446-447)。語形(活用・派生)を網羅する設計でもない。**共有Validator(A/B/C含む)なので本調査・本設計では触らない**(凍結)。
- breame 0.1.2(Apache-2.0)のみでは `speciality`・`jewellery`・`practise`・`programme`・`licence` が**欠落**(確認済み)。**単一の公開表への依存は危険**で、複数辞書の合成と検証が必要。VarCon(寛容license)は`speciality/specialty`等を含む(SCOWL level 40)。
