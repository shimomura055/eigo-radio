# PREREGISTERED_CRITERIA_01 — 事前登録(有料実行前に固定。FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_01)

固定日: 2026-10-25(Phase 0、API 0、①②とも未観測の時点)。以後、結果を見てから基準を動かさない。新たな必須Gate・数値Gateは作らない(ユーザー指示)。

## 1. 評価6項目の見方(ユーザー指示の評価基準)

| 項目 | 見るもの | 機械指標(参考のみ) | 判定者 |
|---|---|---|---|
| 感情表現 | 場面の感情(不安/祈り/切迫/喜び/穏やかな告白)が声に出ているか。Madame『Twenty dollars.』は**感情が出すぎていないこと**(対照) | RMS・F0中央値・F0幅の①→②差 | ユーザー試聴(Fableは機械指標の方向だけ) |
| 抑揚 | 音の高低・強弱の動きが場面に合うか | F0幅(p10-p90半音)、話速 | 同上 |
| 会話の自然さ | 直前の発言への返答として自然か(間・食い気味・調子) | 先頭/末尾の無音、最長中間無音 | 同上 |
| 演出 | 『she whispered』『smiling through tears』『smiled gently』等が声に反映されるか | 『ささやき』なら低RMS・低F0・狭いF0幅の方向 | 同上 |
| 聞き取りやすさ | 語が明瞭か、混入・不自然な間が無いか | ASR一致、leakage、最長中間無音 | Fable(機械)+ユーザー |
| 安定性 | 同じ入力で結果が崩れないか、retryが増えないか、過度な演技が出ないか | attempts数、classification、対照armとのtake差、F0幅の極端な増大 | Fable(機械)+ユーザー |

## 2. Fable独立評価の手順(聴感はユーザー。AIに聴取手段は無い)

1. 機械指標: 8件×(①既存、②take1[、②take2、対照①'])の `analysis.json`(duration/RMS/F0中央値/F0幅/話速/最長中間無音/ASR/verbatim/leakage/attempts)を並べる。
2. 本文正確性: ②の`verbatim.token_equal`(ASR転写と本文のトークン一致)。ASR揺れ(句読点・数詞表記・同音)は既存judge(`asr_judgement`)のPASS/WARNINGに従う。
3. leakage: `leakage.flagged`が0件であること。1件でも真なら該当セリフの転写と音声長を確認し、混入と判断すれば『②NG』として報告(Phase 1の再生成可否はFable判断)。
4. **文脈に応じた変化の観測**: 同じ本文で②のF0幅・RMS・話速・無音が①と**対照armのtake間差を超えて**、かつ『期待方向』(下表)に変化しているかを件ごとに記録する。期待方向は結果を見る前に固定する:

| clip | 期待方向(②−①) | 根拠(原文) |
|---|---|---|
| part2_c7 (祈り・ささやき) | RMSが下がる/話速が遅くなる/F0幅が狭くなる(のうち少なくとも1) | `she whispered.` |
| part3_c4 (涙ながらの笑顔) | F0幅が大きくなる、または話速が遅くなる | `smiling through tears` |
| part3_c8 (Jim、穏やか) | 話速が遅くなる/F0幅が狭くなる | `smiled gently` |
| part3_c2 (動揺→必死の説明) | 話速またはF0幅が増える | `Della rushed toward him.` `His eyes stayed on her hair.` |
| part3_c6 (喜び) | F0幅またはF0中央値が増える | 本文の`Look!` + 場面(喜び) |
| part2_c2 / c5 | 変化は小さい〜中(不安・決意)。過剰変化(F0幅が①の1.5倍超)は『過度な演技』の疑い | `caught her breath` / `shut her eyes` |
| part2_c4 (Madame) | **ほぼ変化なし**(感情明記が無い対照)。大きく変化したら『創作された感情』の疑い | 明示的な感情・演出なし |

 期待方向は『聴感の良し悪し』ではなく、情報が声に届いたかの観測用。方向が合っても、聴いて不自然なら価値はユーザーが判断する。
5. 場面・人物像との整合: 感情欄(LLM出力)の `status`(ACCEPTED/NO_EXPLICIT_CUE/DISCARDED)と根拠引用を一覧し、創作の疑い項目を指摘する。
6. 結論は『②が①より優れる』と断定せず、機械的に観測できた事実と、ユーザー試聴で確認してほしい観点を件別に提示する。

## 3. Status判定の考え方(到達上限 VALIDATED。ユーザー最終試聴は別)

- **VALIDATED(限定)** = 次をすべて満たし、ユーザー試聴で判断可能な状態にあること:
  (a) ②の全8件で本文が正確(`verbatim`、ASR PASS)、(b) leakage 0件、(c) 発音悪化なし(固有名詞・語のASR一致、既存Gate PASS)、(d) 少なくとも数件で、上表の期待方向に、対照armのtake間差を超える変化が観測された(『文脈に応じた変化』の機械的観測)、(e) Madameの対照で過剰変化なし、(f) ①②の生成条件同一性と、②のStyle追加情報が実際のTTSリクエストに渡った証拠(request_full.jsonのprompt sha一致)が保存済み、(g) 実費が上限30円以内。
- (d)が観測されない場合: 『文脈・感情の追加は声に出ない』という否定的結果自体が有用なため、`TRIAL_COMPLETE_NO_EFFECT`として報告し、追加Trial(例: Style文の強度)はFableが費用・見込みで判断(自動で同方向を反復しない)。
- (a)(b)(c)のいずれかが崩れる場合: `TRIAL_FAILED_QUALITY`として原因(混入/発音)を示し、Style改訂の再Trialが妥当か、方式転換(例: 文脈をstyleでなく別方式で)かをFableが判断。
- ユーザー試聴で『改善』と判断されても、本Trialの到達上限はVALIDATED。Production採用は人間ユーザーのみ(量産化にはreuse key拡張・新Gate等が必要で別途承認)。

## 4. 事前に認識しているリスク(Opusレビュー論点と対応、OPUS_REVIEW_REQUEST_01参照)

CONTEXTの読み上げ(leakage)/『誇張しない』と既存style『台本に無い感情を足すな』『表情豊かに』の整合/LLM感情情報の創作/再利用分離/①②の交絡(take揺れ)。
