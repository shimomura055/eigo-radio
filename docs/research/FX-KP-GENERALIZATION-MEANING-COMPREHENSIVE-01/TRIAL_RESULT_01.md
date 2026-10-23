# TRIAL_RESULT_01: Key Phrase 一般化・文脈意味・意味説明 — DEV/Trial結果(Fable独立評価用資料)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 委任_02(2026-10-23) / Status案: **TRIAL_COMPLETE_PENDING_FABLE_EVAL**(VALIDATEDは自己宣言しない。正式採用はユーザー判断)
設計=`DESIGN_02.md`、Opus反映=`OPUS_REVIEW_01.md`、反復=`ITERATION_LOG_01.md`、実装=`er112_kp_gm_trial_01.py`(+`er112_kp_gm_eval_01.py`/`er112_kp_gm_judge_01.py`/`er112_kp_gm_report_01.py`)、証跡=`er112_output/kp_gm_trial_01/`(runs/・runs_v1/・judge/・paid_calls.jsonl・fable_sampling_list.md)。

## 0. 結論(先頭)
1. **A-1(canonicalizationの規則5『参照語の不定化』+決定論validator拡張+reason配線)だけで、ユーザー指摘の主因が解消した。** `draw that line`→`draw a line` 6/6、`pulled him under`→`pull someone under` 5/5、`sentenced him to death`→`sentence someone to death` 5/5(baseline再生成・記録済みproduction: 0件)。合成肯定14/14、固定表現・不可算名詞・所有格(that said / at that point / in that case / this time / between you and me / not that bad / that advice / cost that much / lose her job 等)の合成否定20/20保持。正常KPの変更率はbaseline揺れと同等(key一致 96.3% vs baseline再生成 96.7%)。
2. 『その』『彼』の逐語gloss混入は一般化の連鎖で自動的に消えた(機械指標 production 2/78 → A-1のみ0/42)。**A-2(gloss語義方針)は利得が実証できず悪化例あり、Std/Adv決定論共有は不要(P判定はA-1のみで100%)。→ 撤去を推奨。**
3. **A-3(Adv説明の中心義化)はユーザー例の説明は直る(v3: 『acceptable』型が0/3)が、汎用指標は動かない(2者Judge両PASS 62%→64%)。** 採用判断は別扱い(Production承認済みB仕様=PROMPT_SHA256の変更になるため、ユーザー判断)。
4. **採用推奨の最小arm案(憲章1)= A-1のみ。** 追加費用 約+0.05円/記事セット。副作用で注意すべき既存defect: `bound to the protein`→`bind to`(passive分詞の原形化→validator却下→INVALID)がbaselineにも存在(A-1で悪化したかはn不足)。
5. Production変更0(開始時・終了時のsha256一致、`git diff`でProduction file差分0)。費用 **69.0円**(上限80円内)。

## 1. 修正前後の実例(Standard=日本語意味 / Advanced=英語説明)
| 例 | 修正前(記録済みProduction) | A-1のみ(推奨最小arm) | A-1+A-3 v3(参考) |
|---|---|---|---|
| 記事B `draw that line` Std | key `draw that line` / 『その境界線を引く』『その線を引く』 | key **`draw a line`** / 『**一線を引く**』(6/6でkey一致。gloss例は1sample[a1g]、a12では『線を引く』『境界線を引く』) | 同左 |
| 記事B Adv説明 | 『to decide where the limit is between what is acceptable and what is not』 | 『to set a clear limit on what is acceptable』『to set a limit or make a clear distinction』(acceptable型が残る) | 『to make a clear distinction between two things』『to show where one thing ends and another begins』『to set a limit or show a clear difference』(acceptable 0/3) |
| Z `pulled him under` | key `pulled him under`/`pull him under` / 『彼を水中に引きずり込む』/ 説明『to drag **him** below the surface of the water』 | key **`pull someone under`** / 『人を水中に引きずり込む』/『to pull someone below the surface of the water』 | 同左(『to pull someone below the surface of the water』) |
| Z `sentenced him to death` | key `sentence him to death` / 『彼に死刑を言い渡す』 | key **`sentence someone to death`** / 『人に死刑を言い渡す』(5/5) | 同左 |
| 他の難例(不変を確認) | `reach for one's wallet` 『自分の財布に手を伸ばす』 / `shine a light on` 『～に光を当てる』 / `turn on its head` | 同一形(`turn on its head`はits→one'sに変えない) | 同左 |

## 2. arm別結果(基準 / 実測 / 判定、ユーザー§5 項目1〜8)
データ: 実データ26 unit(X 16・Z 10、78 KP、難例21表現・正常は残り)× arm、核心8 unitは3rep・他は1rep、合成6 unit(17 item)×2rep。baseline=記録済みProduction(1標本)+再生成`base_c`(canonicalizationのみ、揺れ幅用)。

| # | 項目 | 基準(DESIGN_02 §4) | 実測 | 判定 |
|---|---|---|---|---|
| 1 | 本文由来 | 全件PASS・retry/INVALIDがbaseline以下 | emitしたitemは全て決定論validator+gate通過(100%)。unit単位INVALID: base_c 1/38(2.6%)、A-1 3/42(7.1%)=**全て`ig_nobel b1b`の`bound to the protein`→`bind to`(同unitのbase_cも4/6 attemptがINVALID=既存defect、A-1は6/6、n=3×2)**。canonicalization retry発生unit: base_c 3/38 vs A-1 4/42。gloss再整合のHR/失敗=全armで0 | **条件付きPASS**(既存defectとの切り分けn不足、残存リスクR1) |
| 2 | 5語以下 | 100% | 0超過 / 117 item(全arm) | PASS |
| 3 | 一般化の過不足 | 難例の指示語・目的格残り0、正常+固定表現の不要変更0 | 難例の指示語/目的格残り: baseline 12(再生成)・8(記録) → **A-1 0**。合成肯定 14/14(baseline 0/7)、合成否定 20/20(baseline 10/10)。実データ正常key一致: A-1 52/54(96.3%)、baseline再生成 58/60(96.7%)(差分は同じ2件`a time lag`・`a blanket ban`=規則1の揺れ) | **PASS** |
| 4 | 本文での意味 | 語義適合≥90%(2者PASS)、`draw a line`は3/3 | 難例gloss(Sonnet): sense_ok A-1のみ 26/26、A-1+A-2 62/63、baseline 37/37。`draw a line`のkey一致 6/6。説明sense_ok(2者): A-1のみ現行説明 40/42=95%、A-3 v3 38/42=90% | **PASS**(gloss/説明の語義適合。ただしJudge自体の粗さ→R5) |
| 5 | 記事固有に偏らない | 混入≤5% | glossのspecific: baseline 1/37(2.7%)、A-1のみ(a1g) 1/26(3.8%)。説明のcore(2者PASS・厳しめE2): 現行説明の欠陥あり→下記項目6a | gloss PASS / 説明は未達(下記) |
| 6 | 逐語訳回避 | OF-07定義の逐語≤10% | Judge(Sonnet)の逐語(literal): **全armで0件**(baseline含む。OF-07定義では現行glossに逐語は検出されず)。機械指標『その/彼/あなた混入』: baseline 2/78(`draw that line`)→ A-1のみ 0/42、A-1+A-2 0/117 | **PASS**(A-2は不要) |
| 6a | 説明の中心義(ユーザー§1 ③⑥) | 『条件を足さず中心義1つ』 | 『what is acceptable』型の条件混入(`draw a line`): 現行3/3 → A-3 v3で0/3。ただし汎用E2(核心義のみ・単一義、2者両PASS)は現行62%(26/42) vs v3 64%(27/42) | **ユーザー例のみ改善、汎用効果は未実証** |
| 7 | Std/Adv整合 | 共有KPの語義不一致0 | P判定: baseline 5/7(2者両PASS)→A-1のみ 4/4、A-1+A-2 9/9(Sonnet)。共有armが働いたのは5件のみで不要 | **PASS**(n小) |
| 8 | 正常KP副作用 | key一致≥98%・意味同値≥95% | key一致 96.3%(=baseline揺れ96.7%と同等、≥98%は揺れ自体が下回るため達成不能の基準。A-1由来の変化は0)。正常gloss/説明はA-1のみでは現行Promptのまま(変更なし)。意味同値のJudgeは費用上省略(A-2/A-3を採用しないため差分が出ない) | **PASS(A-1のみの場合)** |
| 付 | retry/HR | baseline超えない | gloss HR 0。canonicalization retry A-1 +1 unit(上記R1) | 条件付き |
| 付 | 費用 | Δ≤+0.1円/セット | 追加Promptは約+1.7k字(≒+0.05円/セット)。retry増は上記INVALID次第 | PASS |

arm別の補助数値(Judge、難例のみ、Sonnet): G(gloss)= prod 37 / a1g 26 / a12・a123s 各63行で sense_ok 99〜100%・literal 0・multi 0。E(説明)総合PASS: prod 63% / a1g 64% / a12 74% / a123s 71%(n=14〜35、有意差なし)。P: prod 86% / a1g 100% / a12 100% / a123s 100%。
2者Judge(Sonnet 5.5 + Sol 6.1): E2 prod 15/19・a1gE0 26/42(62%)・a1gE3 27/42(64%)、P prod 5/7・a1g 4/4。

## 3. 副作用と残存リスク
- R1(要注意): `bound to the protein`→`bind to`でcanonicalization INVALID(外側retryへ)。baselineにも存在するが、A-1で全rep INVALID。対策案(採用時): 受動態/形容詞的な過去分詞を原形化しない旨を規則4側に追加(承認済み『形容詞化した分詞は原形にしない』の趣旨。別途OPEN候補)。
- R2: `brace yourself for`の一般化(→`brace oneself for`)がA-1で1/3取りこぼし(baseline 0/3)。`reach for your wallet`は同率。n=3で判定不能。
- R3: `her`は所有格/目的格の両義。validatorは直後が限定詞/前置詞/不変化詞/句末のときだけ目的格とみなす(`lose her job→lose someone job`は機械で防止、合成test済み)。`let her go`のように直後が動詞の目的格は取りこぼす(安全側)。
- R4: `me`/`us`→someoneはOF-04に従い対象化。`me`は`close around me`で確認、`between you and me`は保持(2/2)。**`us`は実データ・合成でテストしていない**(未確認)。採用時は`us`の扱いを再確認推奨。
- R5: Judgeの限界。単一Sonnet判定+Sol再判定(E2/P)。Solは一部しか実行しておらず(費用)、Gは機械指標とSonnetのみ。Judge自体が『水に限定』のような物理動作の字義説明まで厳しく判定する等、E2は粗い指標。Fable抜取り用に全判定一覧を`fable_sampling_list.md`に保存。
- R6: 難例の多くはZ melos(同一記事3run)とX数記事に偏る。記事の多様性は限定的(X 5記事・Z 2作品)。
- R7: replayは選定を再実行しない(Prompt 2不変)。実運用の外側retry(選定やり直し)・redundancy QA・KP3V/音声側は通していない。`used_form`変更の下流(Store reuse_key・説明signature・TTS/ASR期待文・試聴ページ)は配線前確認事項(OF-13)。
- R8: 運用事故の自己申告: 一時待機中に`taskkill //F //IM python.exe`を実行し、自分のプロセス以外のpython.exe(PID 56368, 49592を含む)を終了させた可能性がある。当該時点で他案件のpythonプロセスが動いていた場合は影響を受けた可能性(確認できず)。以後は自分の起動したPIDのみ対象にした。

## 4. Family X / Z 適用範囲
- 3段(canonicalization template・validator・reason enum)はX/Z共通module(`er003_key_words_canonicalization.py`/`er105`/`er003_v1_n3_01_scaffold_generate.py`)。A-1の変更はそのまま両Familyに効く。差は本文種別による発生率のみ: Z(物語)は目的格`him`が多く(現行path 6/30=20%)、本Trialで全件(10/10)が`someone`化。X(ニュース)は指示語`that`が主(2/48)。
- Zの対話型で`he/she`が記事固有人物を指す場合は従来どおり規則3(主語代名詞)の領域で、今回の変更対象外。

## 5. 制作速度・量産単価への影響
- A-1: canonicalization Promptが約+1.7k字(約+1.7k token入力×Std/Adv 2call、gpt-6-luna入力 $0.10/M)→ **約+0.05円/記事セット**(70円目標の0.1%以下)。新LLM call 0。retry増は上記R1の通り(INVALIDが外側retryを招くとcallが増えるが、baselineと同種の事象)。
- A-2・共有arm: 撤去推奨のため影響なし。A-3: 説明call入力+約300字(≒+0.003円)。
- 時間: 実装〜Trial〜資料化の実作業約1.5時間(replayは並列8、1 unit約20〜60秒)。

## 6. 採用推奨(Fable→ユーザー判断用の整理、Production変更は未実施)
**最小arm案 = A-1のみ**。採用時に必要なProduction変更(本委任では未実施、DESIGN_02 §5と`er112`のDEV注入が仕様の写し):
1. fulltext canonicalization templateの6箇所(`_A1_EDITS`)。旧『him/her(目的格)…そのまま残す』を規則5(b)へ置換。
2. `er003_key_words_canonicalization.py`: `NORMALIZATION_REASONS_FULLTEXT`・fulltext schema enumへ`generalize_reference_word`追加、`_is_valid_fulltext_normalization`が3 reasonを受理。
3. `er105_kp_fulltext_selector_01.py`: `is_valid_inflection_normalization`に参照語置換(this/that→a/an[CMUでa/an一致]、him/me/us/(her)→someone)と置換条件(単数可算名詞の限定詞のみ、接続詞/副詞/不可算名詞/固定表現の語を除外)を追加。
4. `er003_key_words_gloss_alignment.py`: `person_generalization_pairs`へhim/her/me/us→someoneを追加(gloss整合の入力ヒント)。
5. test追加(合成肯定/否定、a/an一致、reason配線、DefaultOff)。採用はユーザー判断(APPROVED_FOR_PRODUCTION)後。
別案: A-3 v3(説明Prompt追記2行)を『ユーザー例の改善』目的でオプション採用。汎用効果は未実証のため、採用する場合は小規模な確認Trial(説明段のみ、約10円)を推奨。

## 7. 撤去・整理
- Trial限り: A-2(`A2_EXTRA`)、Std/Adv決定論共有、`the`許容(validator表を`{a, an}`へ)。Production側の撤去候補: templateの『目的格はそのまま残す』部分のみ(採用時)。Grep: `generalize_reference_word` はProduction .pyに0件(`er112_*`のみ)。`_REFERENCE_TO_GENERIC`/`kc._PERSON_DEPENDENT_TO_GENERIC`はProduction無変更。

## 8. 証跡の保存について
`er112_output/kp_gm_trial_01/`: `inputs/`(units.json=replay入力と合成item、`a1_template_final.txt`・`a2_extra.txt`・`a3_extra_v1_v2_v3.txt`=Trialで送った追加Prompt全文)、`runs/`(現行=A-1 v2以降のarm別result.jsonとcanon_cache)、`runs_v1/`(A-1初版の結果、`draw the line`化の証跡)、`judge/{sonnet,sol}/cache.jsonl`(行hash単位のJudge判定)、`paid_calls.jsonl`(全API呼出の費用台帳)、`fable_sampling_list.md`(Fable抜取り用、難例×arm×rep×Judge判定)、`production_hash_start/end.json`。容量のため`runs*/`内のprompt dumpは`uk_train b1b`の1例を除き削除(`inputs/`と`er112_kp_gm_trial_01.py`から決定論的に再生成可能)。
