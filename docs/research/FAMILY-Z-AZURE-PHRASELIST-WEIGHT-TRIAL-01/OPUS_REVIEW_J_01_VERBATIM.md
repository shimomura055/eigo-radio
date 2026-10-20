## Opus_J レビュー結果: GO_WITH_CHANGES

対象: FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01、Phase B/C の有料実走前の方法論レビュー(read-only、Production 採用可否は判断しない)

要点: Phase A の判定注入(offline 注入=Production 判定関数に記録済み転写を流し込む方式)には、本番と異なる経路を通る欠陥があります。このため `pl_w2.0`=NG_BOTH という結果は、本番条件では PASS_WITH_WARNING になる可能性が高いです(推測ですが、コード上の根拠は強い)。負例も、ラベルの付け方に誤りが2件あります。この2点を直さずに Phase B を走らせると、副作用(誤PASS)の評価と重み比較の結論が両方とも歪みます。どちらも API 0〜少額で直せます。

---

### 必須修正(Phase B 実走前)

**M-1 offline 注入が本番の経路を再現していない(Tier3/CS 層が動いていない)**
- 根拠
  - `er084_azure_phraselist_weight_trial_01_judge.py:13,26-28` は `segment_id="plw_trial"` で呼び、CS 層の flag と attempt_ctx は既定値のままです。
  - `er020_tts_retry_local_rewrite_01.py:125-150` により "plw_trial" の role は None になります。その結果、`er006_secondary_asr_01.py:841-846` の Tier3(Secondary 補強 PASS 経路)は不発です。
  - 本番の記録(`run_e2e_04/.../full_story_part3_c1_attempt2_customa3c4625e.json:4,43-50`)では `segment_id=full_story_part3_c1` で、`tier3_corroboration_secondary` が実際に動いています。
  - 本番の story 系呼出は `enable_connected_speech_equivalence_layer=connected_speech_enabled_for(name)` です(`er003_v1_n3_01_tts_generate.py:1112,1152`、FULL_STORY では True)。
- 影響
  - Tier3 の `corroboration_supports` は差分位置の1語しか見ません(`er021_en_asr_semantic_equivalence_production_01.py:731-739`)。
  - そのため `pl_w2.0` の `Melos ... unto` は本番なら Tier3 で SECONDARY_ASR_CORROBORATED_MATCH になり、そのまま PASS_WITH_WARNING に至る見込みです(推測)。つまり onto→unto の揺れは story role では判定に効かない可能性があります。
  - 同じ理由で、負例の誤PASSは本番の方が通りやすい(より許容的な)経路で起きます。今の注入はこれを過小評価します。
- 修正案
  - judge に本番相当の値を渡す: `segment_id`(wav の本番 segment 名、新規 wav は `full_story_part1_c1` など FULL_STORY 型)、`enable_connected_speech_equivalence_layer=connected_speech_enabled_for(segment_id)`、本番と同じ `force_secondary` の扱い。
  - Phase A の判定を API 0 で再注入する。
  - golden replay test を追加する: 本番記録の Azure 転写(`Mellows drank`)を注入し、記録どおり `tier3_corroboration_secondary` step が出て NG_BOTH になることを assert する。今の `test_judge_offline_matches_production_and_no_side_effects`(`er084_..._test_01.py:157-172`)は期待値を自作しているだけで、本番の記録と照合していません。

**M-2 副作用ガードの範囲が足りない**
- 根拠
  - M-1 で Tier3 が動くようになると、`semantic_equivalence.append_telemetry_log` が本番 telemetry に追記します(`er006_secondary_asr_01.py:892-900`)。
  - `is_last_slot=True` を渡すと、HR package 用の発音 lookup(`_resolve_unresolved_entity_for_review`、`er006_secondary_asr_01.py:1038-1043`)が走ります。
  - 現行 test は HR log のサイズしか見ていません(`er084_..._test_01.py:163-172`)。
- 修正案
  - judge 内で telemetry 関数を no-op に差し替える。
  - `is_last_slot` は False のまま固定し、「HR が要るか」は eval 側で「最終 slot なら NG=HR」と換算して出す。
  - test で、次のファイルの size と mtime が不変であることを assert する: er021 telemetry.jsonl、`er006_output/pronunciation_ledger_01/ledger.json`、`er011_output/attempt_history.jsonl`、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`、HR log。

**M-3 負例のラベルに誤りがあり、件数も足りない(論点2)**
- 根拠
  - Ledger の Melos 項目(`er006_output/pronunciation_ledger_01/ledger.json:1171-1175`)は、期待発音を /ˈmiː.lɑːs/(MEE-lahs)とし、別読みに /ˈmɪlɒs/ と /ˈmɛloʊs/ を挙げています。
  - そのため N4 `Milos` はほぼ Ledger の主発音そのもので、N2 `mellows` /ˈmɛloʊz/ も別読み /ˈmɛloʊs/ と有声・無声の差しかありません。Azure がこれらを `Melos` と出しても、本番の観点では「誤認識」と言い切れません。
  - N1/N3 は語末 s が落ちた形なので有効な負例ですが、正例と文脈が違い、置換後の canonical(`The Melos sound of the bell`)も不自然です。
  - 本番で守るべき状況は「canonical=Melos、TTS が同じ文脈で許容外の音を発音した」です。Primary=`Milos`/`Mello`、Azure=`Melos` の組合せは、Tier3(位置一致)でも Secondary 経路(完全一致)でも PASS になります。負例はこの状況を直接突く必要があります。
- 修正案
  - N2/N4 は「境界例」に分類し直し、②の分母から外して別枠で報告する。
  - 正例と同じ文脈の minimal pair(Melos だけを差し替えた対の文)を負例の主軸にする。TTS 原稿の綴りで誘導し、例えば P1/P3/P4 の文脈で `Mello`(s 脱落)と `Melon`(別子音)を作る。必要なら許容外の母音として `Mullos` 型も加える。
  - Voice は Aoede 通常/減速と Charon で、有効負例を24〜30件以上確保する(短文なので追加費用は約 JPY20、推測)。
  - 誤PASSが0件でも、上限の目安を併記する(rule of three: 0/n なら95%上限≈3/n)。今の有効負例6件では、0件でも誤PASS率は最大50%まで否定できません。

**M-4 判定基準が小標本で甘い/主要指標の定義がずれている(論点1)**
- 根拠
  - §3(`TRIAL_DESIGN_01.md:59-63`)の fixed は Melos の綴り単位で数えています。しかし Phase A の w2.0 が示すとおり、Melos が正しくても判定は NG になり得ます。
  - 重みの変更は、両方向の flip(結果の反転)を起こします。fixed=3・悪化=0 でも符号検定は片側 p=0.125、fixed=4・悪化=1 なら p≈0.19 で、偶然と区別できません。
  - REJECTED の「fixed<3」は、R<6 なら INCONCLUSIVE とする規則とどちらが優先か定義されていません。
  - 録音2は失敗していたから選ばれた wav なので、確認用の集計に入れると選択バイアスになります。
  - P1 の4 takes(同じ文の撮り直し)は互いに相関します。
- 修正案
  - 主要指標を「本番判定の flip」にする。対象は Primary が NG の wav で、NG→PASS系の件数と PASS→NG の件数を数える。Melos 正認識率は副指標に下げる。
  - VALIDATED 候補には、片側 exact 符号検定 p≤0.05(5:0、7:1、9:2 など)を要求する。fixed は (文,Voice/話速) の cluster 単位でも3 cluster 以上を要求する。
  - R<6 なら INCONCLUSIVE を REJECTED より優先する。録音2は確認用の集計から除き、参考値として別記する。
  - ③の「悪化」には、Melos 以外の語の揺れで判定が NG に転じたケースも含める。
  - これらの変更は §9 に v02 として記録する。

**M-5 他語の揺れ(副作用)を指標として定義する(論点3)**
- 修正案: (wav, 重み)ごとに次を記録する。
  - (i) canonical に対する新規誤り語数(Melos の位置を除き、ベースラインとの差分として数える)
  - (ii) そのうち保護対象(数値・否定・固有名詞・内容語)の数
  - (iii) 本番判定の flip
  - (iv) Melos からの語距離
- 判定は二つの条件で行う: M-1 で直した FULL_STORY role(Tier3 あり)と、Tier3 が無い role(KP など、`segment_id=None` 相当)。重みは Tier3・CS 層・非ラテン KP・Secondary のすべての Azure 呼出に共通でかかるため(`er006_secondary_asr_01.py:795`、共有 `_AzureShared`)、両方の条件を見る必要があります。

---

### 任意改善

- **S-1(論点4・6、推奨度高)既存の本番 take を再利用する**
  - 既存の Melos 本番 take(`er026_output/family_z_production_e2e_01/melos/run_*/a2/narration/attempts/`、attempt json が524件)には、本番 Primary と Azure 転写が記録されています。
  - このうち「Melos を含み Primary が NG」の take を主評価集合に加えることを推奨します。本番と同じ長さ・style・実際の Primary を持ち、TTS 費用は0、HR 削減の効果を最も直接的に示せます。R≥6 も早く満たせる可能性があります。
  - Azure は約 JPY1.1/本×条件数。合成短文は文脈を分けて見る補助に回す。

- **S-2 費用を圧縮する**
  - `pl_w1.0` は送信内容がバイト同一で、Phase A でも決定論的と確認済みです。Phase B では全 wav の10%程度の spot-check に絞れます。
  - 決定論性も録音2の1本でしか確かめていないため、B でも同じく10%程度で rep2 を抜き打ちする(仮定しない)。

- **S-3 多重比較**
  - 「1.5 または 2.0 のいずれか」(§3:60)は、二つのうち良い方を選ぶ構造です。主たる重みを事前に1.5と宣言するか、α/2 で判定する。

- **S-4 PhraseList の現実性**
  - 本番の segment によっては、ledger_phrases に複数の名前が入ります(Dionysius/Selinuntius など)。長文 passage 型だけでも、本番どおりの複数語 PL の条件を1つ加えると、名前同士の取り違え(cross-substitution)も見られます。

- **S-5 1.25/1.75 の追加について(Fable の判断材料)**
  - ユーザー指示原文は、承認事項1で値を「1.0/1.5/2.0」と明示しています(`2026-10-20_..._USER.md:19`)。一方 §5 は「比較条件…を最適化」を委任しています(:150)。
  - 私の意見: 値を明示した承認を要約で広げることは禁止事項に当たり得るので、Phase B の既定には入れないのが妥当です。1.5 では fix が足りず、2.0 では副作用が出るというトレードオフが実データで見えた場合に限り、中間報告で1行確認をとってから追加する。VALIDATED の対象は承認済みの3値に限る。

- **S-6 一般化(論点6)**
  - Melos と2 Voice だけの結果は「Melos・Family Z 限定」としか言えません。Closeout の文言もその範囲に限定すべきです。
  - 本番採用を提案する前(条件Cレビュー時)には最低限、別記事の固有名詞を2〜3種類見る必要があります。種類は、長い多音節語(Selinuntius 型)、CMU 辞書に無い短い名前、一般語と同音の名前、の3系統が目安です。
  - 本 Trial 内では、既存の HR queue や本番 take のうち固有名詞の不一致があった音声を API 少額で流す「一般化 probe」程度に留めることを推奨します。新規 TTS による本格的な検証は、別 Trial または条件C の前に回す。

- **S-7 Primary の再現性**
  - 新規 wav の Primary は、本番と同じ関数・モデル・prompt(story は asr_prompt なし)で呼び、使用モデル名を記録する(PM_GOVERNANCE 25節)。

- **S-8 Closeout の整理**
  - ユーザー原文 §6(:189-197)は、差が出なかった場合に5つの観点で原因を整理するよう求めています(条件が簡単すぎた/PL が効いていない/1.0 で既に十分/文脈・音声品質で変わる/重みでは解決できない)。eval の出力をこの5分類に対応させておくと、Closeout で説明しやすくなります。

---

### 補足(問題なし、または確認済み)
- 送信 bias の wire 証拠、未指定≡1.0 の実証、全行集計で除外なしとした設計(§6)、逐次実行の理由付けは妥当です。
- M1 の凍結は現在の Ledger を読む read-only 経路で(`er006_secondary_asr_01.py:233-237`)、本番の run 時点の snapshot とは異なります。「今後の本番挙動を見る」目的なら現在の Ledger で妥当ですが、その旨を文書に注記してください。

確認に使った主なファイル(すべて `C:\Users\tensh\eigo-radio\` 配下):
- `er084_azure_phraselist_weight_trial_01_judge.py`
- `er084_azure_phraselist_weight_trial_01_test_01.py`
- `er006_secondary_asr_01.py`
- `er020_tts_retry_local_rewrite_01.py`
- `er021_en_asr_semantic_equivalence_production_01.py`
- `er006_output\pronunciation_ledger_01\ledger.json`
- `er026_output\family_z_production_e2e_01\melos\run_e2e_04\a2\narration\attempts\full_story_part3_c1_attempt2_customa3c4625e.json`
- `docs\research\FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01\TRIAL_DESIGN_01.md`
- `docs\research\FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01\design_matrix_01.json`
- `docs\research\FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01\PHASE_A_RESULT_01.md`
- `docs\pm\delegation_log\2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_USER.md`