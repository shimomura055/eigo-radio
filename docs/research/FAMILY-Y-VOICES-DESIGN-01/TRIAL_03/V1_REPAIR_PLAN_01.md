# V1_REPAIR_PLAN_01: 人物1(V1・Algieba)の音声確定のための修正案(未実施・Fable判断待ち)

Status: 提案のみ(実装・再生成なし)。本委任の制約「有料runの再起動はHR Lock後も含め明示範囲のみ」「Gate・Human Review Lock迂回禁止」により、停止後のV1再生成は行っていない。

## 1. 現状
- Adv(b1b) `full_story_part1`: 4試行で未確定 -> `HUMAN_REVIEW_REQUIRED/STOPPED`(試行1・2=Repetition QA method D'が境界値[0.62/0.60秒、閾値0.6秒]でflag、試行3=ASRが原稿の「can」を「could」と転写、試行4=既存のLocal Rewrite recoveryで「can」->「just」に置換して再生成したがD'が0.63秒で再びflag[位置は21.9秒で別の区間])。
- Std(a2) `full_story_part1`: 試行3で`minimal_fallback`(代替指示)により確定 -> Y style gateが`BLOCKED_STYLE_PROFILE_GATE`(`FINAL_STYLE_SHA_MISMATCH_NO_HINT`+`STD_FALLBACK_USED_OR_UNKNOWN`)。
- それ以外の全segment(Adv: 見出し・V2・V3・Tension+Closing・In One Line・KP、Std: 同) は正式に確定済み(AUDIO_QA_03.md)。**V1以外の再生成は不要**。
- 詳細・原因仮説・根拠=AUDIO_QA_03.md「人物1の停止と原因仮説」。

## 2. 選択肢
| 案 | 内容 | 費用 | 所要 | 備考 |
|---|---|---|---|---|
| A | 人間がV1のテイクを聴いて承認(Adv take、Std fallback take)。承認後にassembleし通し音声を組み立てる | API 0 | 人間の試聴次第 | HR Lock・style gateの正式手順。Advの最終テイクは「can/could」の1語ASR差、Stdはfallback生成(声の調子の指定が標準と異なる)。人間判定が必要 |
| B | 英語V1の反復する短い語句の語順・文頭を言い換え(下記)、V1のみ両levelで再生成(他segmentはキャッシュ再利用) | 約4〜12円(1試行約1.5〜2.5円×最大3試行×2level+assemble API 0。Local Rewrite recoveryが働くと+1試行) | 約15〜25分(Gemini batch待ち) | 原因仮説(短い機能語句の反復区間・ASRの揺れやすい引用形)への直接対処。**成功保証なし**(flag位置がテイクごとに変わるため)。日本語は無変更 |
| C | A+B併用(Bで再生成し、なお停止したテイクだけAで人間確認) | B+API 0 | | 最も確実 |
- 推奨(Sonnet提案): **B**(Advの停止がHR Lock=人間待ちでなく、原稿修正で正式な形に戻せる見込みが高い)。ただしBの実行は委任の制約で私は実行しない。Fableが再委任で許可すれば、残予算内(現状の累計約50円、Y残予算約84円)で即実行できる。

## 3. B案の英語修正(V1のみ。日本語は無変更)
意味は日本語原文のまま。変更点=①「I + 動詞」の連続を避け文頭に変化(Her words left me speechless. / Still, a promise is a promise… / Yelling like my father…)、②ASRで「can/could」が揺れた「If I can say, “That's the rule at school too,”」を「If the school has the same rule,」に、③「in the charging basket in the living room」の「in the…in the」反復を「in the living-room charging basket」に。

**Adv(b1b) part1(現行→案)**: 太字が変更箇所。
```
(第5文)My daughter didn't keep our agreement to put her phone **in the charging basket in the living room**. -> ... to put her phone **in the living-room charging basket**.
```
```
... She also said, “If I'm the only one who replies late, I'll be left out.” **Her words left me speechless. Still, a promise is a promise, and I want it kept. Yelling like my father is out of the question, too.** But even if she can't use her phone at school during the day, ...
(第4文)If I **can say, “That's the rule at school too,”** then I don't have to be the only bad guy. -> If **the school has the same rule, then I'm not the only bad guy.**
```
**Std(a2) part1(現行→案)**:
```
(第8文)She was supposed to put her phone in the charging basket in the living room. -> She was supposed to put her phone in the living-room charging basket.

(第6文)If I can say, “It's the school rule too,” I won't be the only bad guy. -> If the school has the same rule, I won't be the only bad guy.
I had no answer. I want her to keep our promise. I don't want to shout like my father, either. -> Her words left me speechless. A promise is a promise, and I want it kept. Shouting like my father is not what I want, either.
```
- KP影響: AdvのKP=cut off contact(V3)/lose trust in(Tension)/off-limits(V2)、StdのKP=left out(V1の引用文は無変更)/off-limits(V2)/phone-free time(Tension)で、いずれも変更箇所を含まない -> KP再生成不要。
- 再実行手順(承認後): `it3/english/{a2,b1b}/article.md`のV1段落を上記へ更新 -> `er110_family_y_persona_audio_trial_01.py --it it3 --stage prep` -> `--stage tts --level both --budget-jpy <cap>`(`_generate_or_reuse`が本文一致のOK segmentを再利用、V1のみ再生成) -> `--stage assemble` -> `er110_family_y_persona_audio_page_03.py --it it3` -> push -> Playwright。

## 4. 注意
- 原稿修正はJA/EN間の意味同等を保つ範囲。Opus blind対比較用の`BLIND_PAIRS_02.md`のV1英文は、B案実施時に再生成する(現状は未修正のV1英文)。
- この修正は「Repetition QAの閾値変更」「HR Lock回避」ではない。検査は従来どおり。
