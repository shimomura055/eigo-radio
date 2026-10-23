# DESIGN_PROPOSAL_06: Family Y「Persona選定・Voice生成」6段階仕様(OPUS_REVIEW_03反映版、委任_14 T-1)

Status: `DEV_TRIAL_SPEC`(DEV/Trial専用。`VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない)。前版=`DESIGN_PROPOSAL_05.md`(履歴として残置。本書はその差分と確定値を記す。未記載の項目は05のまま)。
レビュー=`OPUS_REVIEW_03.md`(必須OF-Y5-01〜06全反映、推奨07〜12採用)。実装=`er110_family_y_persona_pipeline_01.py`(+`_run`+`_test_01`)。既存`er110_*`は無変更(testで固定)。

## 1. OF別の反映(要約表)
| OF | 反映内容 | 実装(関数/定数) |
|---|---|---|
| 01 固定Voice性別 | S4は性別を選定基準にしない。各メンバーに`gender_intrinsic`(男性/女性/不問)+理由を出力。S5前に決定論でスロット割当(固定Voice=V1男・V2女・V3男、`er110_family_y_text_trial_01.py:39`)。性別確定人物を先に置き、`不問`には空きスロットの性別を付与。割当不能(女性2人以上・男性3人)は**手作業で直さずSTOP報告**(`SLOT_ASSIGNMENT_INFEASIBLE`。声セット変更はユーザー判断)。一人称・年齢帯の3人重複も決定論で確認(一人称重複は後の人物のS5を1回だけやり直し、差戻し回数に数えない。年齢帯・18歳未満は記録) | `assign_slots`、`check_overlaps`、`stage_s5` |
| 02 英語音声版 | メインrunのStd英語(Adv→Std)にもA'/B'盲検を行う(BLIND_SET_03にStd英語を含める)。主張抽出E1を英語Stdで記録 | runner`stage_english`、`e1_claims` |
| 03 判定者校正 | 盲検セットに旧V1(ユーザー評価=良)と旧V2・V3(弱い)をセンチネルで混ぜる。センチネルを再現できない判定者は主評価に使わない。判定が割れたら低い方を採り引用付きでFable裁定。主要当事者リストはFableが実行前に固定(委任_14 §3)し、S2の網羅は**事前リストに対する網羅**で判定(別callのlunaで根拠つき判定。S2にはリストを見せない) | `BLIND_SET_03`、`stage_coverage` |
| 04 再現run | school_phone_banの再現runを**S2〜S6**(同一S1入力)まで実行。**Tension・英語は省略**(費用。Voice本文でA'/B'が測れる範囲)。sol補助盲検は外す | runner`--text-only` |
| 05 S6撤去範囲 | S5が`identity_cue_ja`を生成し、S6は規則3(身元手がかり)を残す(位置を冒頭2文→**3文以内**に緩和)。規則4は『核は1つだけ』『締めで核に戻る』を撤去し、目標1行(『聞き終えた人が"この人は何を言いたいか"を一言で言える』、位置・型指定なし)を残す。**残置**: 規則1(長さ・常体)・5(具体論)・9〜13(一般化禁止、事実の扱い、数字・実在名禁止、役割語禁止、記号禁止) | `VOICE_PROMPT_TMPL` |
| 06 構造監視 | 発火条件=**展開の型が一致 かつ (冒頭型か締め型のどちらかが一致)**(『その他』同士は一致としない)。締めの型の違いだけでは『異なる』とみなさない。タグのラベル集合を事前固定(締め型に『自嘲・告白で締める』を含む)。発火時は最初の該当ペアの後の方のVoice1本だけを`entry_mood`強調で1回再生成し、再タグ付けは記録のみ | `OPENING_TYPES`/`DEVELOPMENT_TYPES`/`CLOSING_TYPES`、`structure_fire`、`stage_voices` |
| 07 自然さ検証 | S5生成とは**別call(luna)**で『最も不自然な点を必ず1つ挙げ、聞き手に違和感を与えるか』を判定。`why_this_person_says_this`(因果説明)は見せない。差戻し発火回数を記録(0回なら『機能した』と結論しない) | `build_natural_prompt`、`naturalness_flags_total` |
| 08 V1収束対策 | S5で痛み・失敗・矛盾を必須にしない。矛盾・弱さは属性(`contradiction_or_weakness_ja`)として持たせ、語りに出すことは必須にしない。S4`diversity_note_ja`に『感情・矛盾の出方が3人で同型でないか』を追加 | `S5 prompt`、`S4 prompt` |
| 09 S1のLLM実行 | 学校題材でもS1をLLM 1 callで実行(外国Fact分離の検証)。出力は承認済み`WORLD_SETTING_01.md`を正解として機械照合(`compare_s1_to_approved`、Gateにしない)。以降の工程は承認済み設定(`SCHOOL_WORLD_FRAME_APPROVED`)を使い旧稿比較条件を保つ | `stage_s1`、`compare_s1_to_approved` |
| 10 制度誤説明対策 | S6入力に`world_frame.distinctions`(使用禁止/持込禁止/授業中のみ/預かり等の区別)を加える。許容する事実は`status_quo`のIDから選ぶ`known_fact_id`欄(S5)に定義し、S6はその1件のみ。事後盲検に『制度の取り違え(引用付き)』を記録(Gateにしない) | `VOICE_PROMPT_TMPL`の@@DISTINCTIONS@@/@@FACT@@ |
| 11 高校生本人 | S2/S4で除外しない。S5で18〜19歳へ寄せる誘導もしない。18歳未満が選ばれたらUJ-3として記録(`overlaps.under_18`)し、R0通過後の試聴でユーザー判断。ROOT_CAUSE_02に追記済み(§6) | `check_overlaps` |
| 12 量産費用 | +25〜35円/記事はTrialではQ>D>Cの範囲内。70円目標とのトレードオフはVALIDATED提案時にユーザー判断事項として明示。Phase B後の削減候補: S2+S3統合、S5 effort medium比較、S4候補trioを2組に(S5の3人1 call化は独立性の観点で後回し) | 報告に記載 |

## 2. 確定した仕様値(実装と一致)
- 使用model: 生成(S1〜S6本文・Tension・差戻し再評価・Leakage rewrite)=`gpt-6.1-sol`(最新世代最上位系、25節)。判定・補助(Leakage判定器・自然さ検証・構造タグ・網羅判定・E1)=`gpt-6-luna`(M7校正済み判定器と同系。判定の偏りは盲検で補う)。effort: S1/S4/S5/S6=high、S2/S3=medium、自然さ=medium、構造タグ=medium、E1=low。
- 呼出入口: `y0.chat`(既存)。Leakage判定器=`p.run_leak`(13項目の定義は不変)。局所書換の決定論検査=`p.apply_rewrites`。Acceptance Gateは判定最大3回で`p.run_gate`と同構造(題材非依存のrewrite promptだけ新module内)。Voice契約違反・記号QA違反は1回だけ再生成、残ればSTOP。
- S2: 8件以上・主要当事者1件以上・id重複なし・根拠なき除外なし。違反は1回やり直し、残ればSTOP。
- S3: 立場ごと3件以上・`origin_ja`あり。違反は1回やり直し。`kind`の種類数・自己都合/怒り/矛盾の有無は**警告として記録**(Gateにしない)。`factual_risk=yes`はS4入力から除外(除外件数を記録)。
- S4: 候補3組・組内で立場が異なる・主張はその立場に属する・選定組の`reason_A`が≥2メンバーの`contact_point`を8字以上の連続一致で引用、`reason_B`が≥2メンバーの`origin`を引用(欠ければ1回だけやり直し)。
- 差戻し: S5の自然さ判定`adjust_claim`→同一立場の次の`claim_seed`、`replace_person`→S4の選ばれなかった候補組の未使用立場(性別がスロットに合うもの)。**合計2回まで**(`REWORK_LIMIT_EXCEEDED`で手作業せずSTOP報告)。差戻し後はS4の`reason_C`だけ1 callで再評価。
- Tension(Gate後のVoiceから)・英訳(Adv→Std、既存X関数呼出)・Std英語E1は**メインrunのみ**。見出し・Comment・Preview・KP・音声は実施しない(本Trialの範囲外。音声化は後日)。
- 構造タグのラベル集合(事前固定): 冒頭型=自分の状況・立場の描写から/出来事・場面の描写から/感情・本音の吐露から/主張・意見の表明から/問いかけから/言い訳・弁明から/その他。展開型=主張から具体例へ/具体例から感情を経て主張へ/感情から具体例へ/経験の時系列/問いを重ねて考える/自分への突っ込みと本音を行き来する/その他。締め型=自嘲・告白で締める/問いを残して締める/約束・要求で締める/主張を言い切って締める/場面・情景で締める/迷いを残して締める/その他。

## 3. 撤去・残置の一覧(識別子。残存Grepは報告に記載)
- 新module `VOICE_PROMPT_TMPL`から撤去: `@@ORDER@@`(語りの順序、旧規則2)、`@@CLOSING@@`(締めの型、旧規則8)、旧規則4の『主張の核は1つだけ…締めの一言で主張の核に戻る』、旧規則6の『ためらいは多くても1か所』、旧規則14『他の人の領分』(`derive_not_my_point`相当は持ち込まない)、Sheetの`closing_type`/`order`/`closing_example`。
- 新moduleへ持ち込まない手作業表: `PERSONA_CANDIDATES_01.md`型の候補表、固定`SHEETS`。
- 残置: 旧B Leakage 13項目と判定器、Acceptance Gate、一人称、数字禁止・実在名禁止、Fact Safety(一般化禁止)、R0のみ、4パート構成(Y Trial仕様)、固定Voice(声セット変更はユーザー判断)。

## 4. 評価・盲検設計(OF-Y5-02/03、`BLIND_SET_03.md`)
- 対象: 題材ごとに 新run(メイン)・新run(再現、schoolのみ)・旧稿(school: it3 V1/V2/V3、office: 旧2V)のVoice本文(日本語、メインrunとschool旧稿のStd英語を含む)をラベルなしで混在。
- 校正センチネル: 旧V1(良)=期待『当事者性あり・必然性明確』/旧V2・V3(弱い)=期待『やや弱い〜弱い』。判定者がセンチネルを再現できない場合、その判定者の結果は主評価に使わない。
- 設問: Voiceごと A当事者性(あり/やや弱い/なし)・B主張の必然性(明確/やや弱い/弱い)+引用、制度の取り違え(引用)、Q『実在の人が自分の生活から語っているか』、組(trio)ごと C組合せ価値・同型化の有無。
- 判定割れ: 低い方を採り、引用つきでFableが裁定。主要当事者網羅=事前リストに対する網羅(S2出力の`s2_coverage.json`)。新しさでは評価しない(OF-Y5-15)。
- 自己判定は`VALIDATED`候補にしない(再現性の判断はFable)。

## 5. 合格判定の扱い(DESIGN_PROPOSAL_05 §4-3 P1〜P6のまま)
P3(再現性)は『S2〜S6を独立に2回通して質の下限が安定するか』になった(05の『S2〜S4のみ・S4止まり』を置換)。P2(旧稿比較)・P4(別題材)も同様に盲検資料で判定。判定はFable/Opus。
