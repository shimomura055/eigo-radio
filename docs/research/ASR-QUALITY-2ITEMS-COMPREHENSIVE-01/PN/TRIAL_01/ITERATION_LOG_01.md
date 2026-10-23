# ITERATION_LOG_01: ①固有名詞 RET Trial の反復履歴(自律改善ループ)

管理ID: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-PN 委任_02 / 2026-10-23。ループ=原因分析 → 対策設計 → (Opusレビュー済み条件A) → Trial実装 → 検証 → 結果分析 → 必要なら再設計。
再実行は全てcache経由(`llm_cache.jsonl`)で、同じ入力にはAPIを再呼出ししない。実API費用は累計 **5.30円 / 上限30円**(`usage_log.jsonl`、gpt-6-luna、単価は`er006_model_routing_pricing_coverage_test_01.py:50-52`の0.10/0.50 USD per 1M token・160円/USD)。

## 反復0: 初回実装(DESIGN_02、Opus OF-PN2-01〜11反映)
実装=`er111_pn_entity_table_trial_01.py`/`er111_pn_trial_evaluate_01.py`/test。SC-1(表なし/空/無関係表でer103原本とバイト一致: D1 88×2条件、D2 EN 1,309判定、39件test)は初回からPASS。

## 反復1: 検出(SC-2)の取りこぼし分析
- 観測: 合成D4(97 gold)の初回で eligible 76中 usable 74(97.4%)。未達2件+検出漏れ。原因を分解:
  1. **評価script側の不備**(実装不具合ではない): 段落を文に切る際に `Mrs. Sappleton` を `Mrs.` と `Sappleton…` に分断 → 逐語検証が失敗。splitterを略語対応に修正。
  2. **実装の不備(実測で発見)**: LLMが `L. Mimoun` を `L.` と `Mimoun` の2 entityに分けた。`L.`だけでは eligible token が無く weak → RET-3の実体span(`l mimoun`)が組めない。→ **対策**: `_merge_initials`(本文の `X. <entity>` を1実体として復元、裸のイニシャルentityは捨てる。決定論・API 0)。
  3. gold側の取りこぼし(Alta Zara/Typhoon/Ig Nobel を gold に未記載): LLMが正しく検出していたため gold を補正。
- 結果: usable 79/79(100%)、層別(表が必要な層=既存証拠が成立しない出現)42/42。

## 反復2: SC-4(初見語)の未受理分析 — Altuzarra, Toteme
- 観測: HR queue 88(Ledger全除外)で RET受理 54。残るC類(Secondary span跨ぎ)5のうち 2(`altuzarra toteme`→`altusara totem` 行37, 44)が `span_not_one_entity_run` で不受理。
- 原因: 本文は `Celine, Altuzarra, Toteme`(**カンマ区切り**の隣接2実体)。私の`_gap_ok`が句読点を許さず連結できなかった。Opus OF-PN2-02は「区切り語なしの隣接複数実体」としている。
- 判断: 「区切り語」= 語(and/the/of等)であり、**語を含まない句読点(,;)は区切り語ではない**と解釈(両tokenとも表のconfirmed実体、`_noun_checks`・P-03は合成spanに適用されるため境界は不変)。語が挟まる連結は引き続き不許可(testで固定: `Altuzarra and Toteme`)。
- 結果: 54 → 56。残るC類3は `melos drank`×3(意図どおり不受理)。**この解釈はFable確認事項**(TRIAL_RESULT §7)。

## 反復3: Bertie の再構築安定性 — 80% → 100%
- 動機: SC-4「Bertie 3/3必須」は初回構築では満たしたが、同一textを5回再構築すると Bertie が usable になる率が **4/5(80%)**(`bertie_stability_01.py`)。必須要件の信頼性として不十分。
- 原因(仮説→反証→再現): 「LLMがBertieを見落とす(recall揺れ)」を仮説 → キャッシュ全件確認で**反証**(call A/Bとも5/5回 Bertie を挙げている)。実際は call B が `"Bertie, why do you bound?"`(歌詞行)を **work_title** として挙げ、私の「判定が割れたら厳しい側のカテゴリへ」規則が、**別実体(歌詞行)の分類で Bertie(person)を work_title に下げていた**(→ CMU収録tokenに証拠を付けない=weak)。再現=該当rep(2)の単体構築で `category_downgraded_by_call2`。
- 対策: カテゴリの比較は**同じ語列(完全一致)の entity どうし**に限定。call Bがより長いspanの一部として挙げた場合は存在の一致のみ(カテゴリは変えない)。unit test追加(`test_call_b_longer_span_does_not_change_category`)。
- 結果: Bertie usable 5/5(100%)。以後の全検証を再実行(結果は数値同一または改善)。
- 教訓: 安定性は**LLM出力の揺れ**より**自作の仲裁規則**が原因だった。仲裁規則は「同一性が確かなもの同士」でのみ働かせる。

## 反復4: アブレーション — 一般語tokenの位置紐づけ付与(`general_in_phrase`)
- 懸念: OF-PN2-01(i)を文言どおり「eligible tokenのみ」にすると `Stephen Reicher` の文頭`stephen`(一般語)に証拠が付かず落ちる可能性。
- 実装: 実体出現範囲に**全体が含まれる**句で eligible token を含む場合のみ、同じ実体内の一般語tokenにも位置紐づけで付与する変種(V2)をablationとして実装。
- 結果: HR queue 88で V1(文言どおり)= V2 = 56 受理(差0)。理由=既存の`proper_noun_evidence`のTitle Case連なり規則(文中の大文字語の連なりに『強い語』が含まれれば連なり全体が根拠になる)が、表が`reicher`に証拠を付けた時点で連なりの`stephen`を救うため(ラベルは`entity_table:...`と表示されるが、一般語tokenに独立の証拠は付与していない)。→ **文言どおりのV1を採用**(V2のコードは残すが既定False)。

## 反復5: SC-5 負例の定義見直し(測定の妥当性)
- 観測: 合成変種のうち「Primaryが一般語 `water`/`very`、Secondaryがほぼ正しい転写」の組合せで33件受理(例 Reuters→water, sim 0.5)。
- 分析: 同じ入力を「同一tokenをLedger登録した原本」でも評価 → **33件とも原本と同判定**(表が緩めた差ではない)。さらにこの組合せは、Secondaryがほぼ正しいため統一judgeが既にSecondary受理するので**PNAPに到達しない非現実的な形**。
- 対応: 負例基準は「Primary/Secondaryが同じ別語に揃う」(Stage 2の実誤読型、NG_BOTHの現実的な形)に限定し、alt組合せは参考値として別掲(開示)。基準値: 一般語/数値/否定/脱落への受理 = 0。
- 副産物(既存境界の所見・変更はしない): Ledger登録済みの語でも、Secondaryが正しいのにPrimaryだけ一般語へ崩れた入力が到達すれば受理される構造は原本にもある(到達経路が無いため実害なし)。

## 反復6: SC-9 安定性 — 未完(残課題として開示、これ以上は費用対効果が低い)
- 観測: 27 text×3回構築で confirmed entry集合 Jaccard の text別最小の平均 0.953(個別0.90未満が4/27: `Meta’s Superintelligence Labs`⇔`Superintelligence Labs`の表記粒度、`Reicher`⇔`Stephen Reicher`、`Vogue`が work_title に揺れる1回、Houthi/Houthis)。token単位(証拠が付くtoken集合)では平均 0.984、個別0.90未満は2/27(最小0.80)。**3回の和集合でも非固有名詞への証拠付与は0**。
- 分析: 揺れの大半は**表記の粒度**で、証拠tokenは変わらない。実害のある揺れは Vogue の category 揺れ(work_title になると CMU収録tokenに証拠が付かない)だが、失敗方向は「証拠が減る=HRのまま」で安全側。
- 検討した追加策: 多数決(3 call)= 費用が約3倍(0.2円)で0.1円目標を超える/entry正規化(所有格の除去等)= entry単位指標は改善するが運用上の差は無い。→ **今回は追加せず**、Fable判定の材料として開示。次の一手の候補=「det裏付けのあるentryはA/Bの和集合」(費用0.05円、precision悪化の懸念は和集合実測0で小さい)。見込みは中。

## 未実施(理由)
- モデル比較(OF-PN2-13): 「SC-3/SC-9達成を条件」→ SC-9が条件付きのため未実施。
- X英語出典メタデータの宣言型利用(OF-PN2-09(i)): 構造化保存なし。
- HR Lock済み4clipの実再生成・stage実行: 禁止事項(机上再判定のみ)。
