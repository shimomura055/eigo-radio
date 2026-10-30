# KP-DIFFICULTY-4LEVEL-DISPLAY-01 DESIGN_01(委任_01、2026-10-30)

前提: 原文§4。難易度は**Gateではない**(候補の削減ゼロ)。新方式D(OPEN-621、未採用)に依存せず、現行Production方式(P7/W5')で動く。

## 1. 判定方式の比較

| 案 | 内容 | 品質 | 精度根拠 | 追加API | 費用(70円比) | 評価 |
|---|---|---|---|---|---|---|
| (i) 選定callのschemaにfield追加 | P7/W5'のJSON schema+Prompt末尾に判定基準を足す | 選定の挙動が変わるリスク(Prompt sha固定・変更は承認要。`er119_kp_p7w5_prompts_01.py`のsha assert)。選定と自己採点の混在 | 選定時の1文脈で同時判定=難易度の一貫性が弱い | 0 | 0 | **不採用**。承認済み選定Promptを触る=候補品質を回帰させ得る(Charter 1・8)。補完(backfill)・既存docには効かない |
| (ii) 独立した軽量判定call | 最終候補集合に対し1 generate=1 call(gpt-6-luna) | 選定に無影響(追加fieldのみ)。判定専用Promptで基準を明示でき、全候補を相対的に見て段階をそろえられる | 候補の意味(日本語訳)・例文も入力。4段階の定義を明文化 | 1 call/レベル(失敗時最大2) | 約0.1〜0.3円/レベル(約0.2〜0.6円/記事セット=0.3〜0.9%) | **推奨** |
| (iii) ローカル語彙リソース+規則 | 頻度表・CEFRリスト+語数規則 | 句動詞/イディオム/多義語の「用法難易度」を表せない。原文4.2「単語数や文字数だけで判定しない」と整合しにくい | 頻度表は未導入(`wordfreq`未導入)。新規依存・保守が発生 | 0 | 0 | 不採用(単独では要件を満たせない)。将来、(ii)の入力に頻度ヒントを足す拡張余地として記録 |

推奨=(ii)。理由: 選定品質を一切変えず(Q)、全経路(初回/外側retry/補完/再選定)を1か所で覆い(D、実装位置が1つ)、追加費用は量産単価の1%未満(C)。既存工程(canonicalization・gloss整合・Redundancy QA)の置換による相殺は無い(それらは別の責務)。

## 2. 付与位置・fail-open・データ

- 位置: `_generate_candidates_impl`の`while`ループを抜けた直後(`cands_final`確定後)。`stop_check_fn("kp_difficulty:...")`を課金前に呼ぶ(STOPを迂回しない)。補完・Redundancy QAの後なので、**最終候補集合の全件**に付く。
- 追加のみ: 候補への`difficulty`と`doc["difficulty_grading"]`の追加。candidate_id・ai_rank・順序・dropped・flags・Gate・件数・上限は不変(testで固定)。`candidates_sha256`は生成時に確定するため整合。
- fail-open: API失敗/parse不能/欠落/定義外は`unknown`(表示「未判定」)。attempt最大2(他の補助段と同じ上限)。routing違反・モデル不一致(`FulltextSelectionError`系)とSTOPは握らず伝播(`bf.is_propagating_exception`)。
- 保存形: `candidate["difficulty"]={level: easy|medium|hard|rare|unknown, label_ja: 易|中|難|激難(レア)|未判定, reason_ja, source: llm|fail_open}`。`doc["difficulty_grading"]={version, prompt_id, prompt_sha256, model_id, response_id, status[OK|PARTIAL|FAILED_OPEN|SKIPPED], n_graded, n_unknown, attempts}`(監査: 実model_idとPrompt shaが残る)。
- Prompt: `er119_kp_difficulty_01.PROMPT_TEXT`(sha256を`doc`に記録)。4段階の定義、総合要素(使用頻度/語彙・熟語としての難しさ/意味・用法の習得難易度/特殊性・希少性)、単語数・文字数だけで判定しない、学習レベルは境界例の参考のみ。目安の例にはユーザー原文の例(rely on/make room for/narrow down)を**入れない**(委任_02の保留検証用=過適合防止。testで固定)。
- 透過: `export_form_data_01.py`の`entry()`が`difficulty`({level,label_ja,reason_ja,source})を各Phrase/Word entryへ、`convert()`がdoc要約`difficulty_grading`をトップへ出力。旧doc(難易度なし)は`unknown`/`not_graded`(候補は減らない)。
- readable/AIF1コード: **含めない**(照合コード互換維持)。確定record(`er128_kp_confirmed_content_01._item_from_cand`)の`reference.difficulty`に参考情報として保持(難易度がある候補のみ追加。旧doc・難易度なしはバイト同一)。

## 3. 表示仕様(委任_02で実装。本委任はform_logic.js/index.htmlを編集しない)

- 場所: V3(単体・一括)の各Phrase/Word候補の用語の横に小さなバッジ「｜易 / 中 / 難 / 激難(レア) / 未判定」。例: `rely on｜易`。
- 一覧性: バッジは用語行の末尾1要素(1行を増やさない)。色は段階の差が分かる程度(易=淡、激難=強調)。未判定はグレーで「未判定」(欠落を隠さない・選択は妨げない)。
- 非干渉: 選択チェック・日本語訳・理由・コメント入力・Done・コピー(readable/AIF1)・一括の記事/レベル切替を変更しない。バッジは`data.phrases[].difficulty.label_ja`のみ参照(新fieldが無い旧dataでは非表示でなく「未判定」)。
- 一括(02A)との競合回避: 02A完了後に委任_02で`form_logic.js`/`index.html`へ小さな差分として追加。

## 4. 精度検証計画(委任_02、実LLM)

- 対象: 既存run(Std/Adv各3記事程度=約6セット・約60候補)の保存済み`kp_candidates.json`に判定を付与(`kpd01_*`の検証script、docは書き換えず別outputへ)。
- 判定の独立確認: (a) Sonnet(私)が全候補を実読して目視ラベル、(b) 別系列モデル(gemini-3.8-flash等)に同じ定義で判定させ、gpt-6-lunaと3者の一致率を見る。許容: 隣接段階の差は許容、2段階以上の乖離をNG(目標: 2段階乖離0〜1件/60件)。
- 目安確認(ユーザー表示例): `rely on`=易、`make room for`=中、`narrow down`=難相当になるか(Promptにこれらを入れていないため保留検証として有効)。
- Std/Advで同一表現の段階が大きく割れないこと。分布が1段階に偏らないこと(易は選定Promptの条件5により少ないと予想=偏りは仕様)。
- 費用見込み: 6セット×約0.2円+別系列判定=約¥3以内(個別承認Cap内のはず。委任_02で確定)。

## 5. 委任_02以降の計画

1. 表示側(form_logic.js/index.html、02A完了後): バッジ+test(JS)+一括/単体/コピー整合。2. 精度検証(上記)。3. 正式runtime evidence(実run 1〜2レベルの`kp_candidates.json`の難易度付与・actual model_id・Prompt sha・cost logger)。4. X/Y/Z・Std/Advの適用確認(共通経路のためwiring testで3family確認+実run)。5. Fable受入、PRODUCTION_WIRED判定(§7 12項目)。
