# B3Z_DESIGN_01: Family X B3 の確認とFamily Z向け B3Z Prompt 設計 + (2)(3)工程設計

管理ID: FAMILY-Z-MELOS-SOL-B3Z-COMPARISON-TRIAL-01 委任_01 / 2026-10-12。以下は**Trial内仮説**(Production仕様ではない)。実Prompt本文は `er059_melos_sol_b3z_trial_01.py`(`B3Z_USER_TMPL` / `B3Z_DEVELOPER` / `B3Z_SCHEMA`)、実行時の完全文は `m3_sol_b3z/b3z_prompt.txt`。

## 1. Family X B3(storyline_b3)の確認結果(事実)
- 実装: `er019_family_x_storyline_b3_fact_selection_01.py`(LLM 1 call)。入力=Full Fact Ledger(Web調査済み検証済みFact)。
- 処理: (1)中心Storylineを1つ決定 (2)1行で明示 (3)全Factへ4テスト(削除しても理解できるか/因果に使うか/「なぜ?」を説明するか/面白い・具体的だけが残す理由でないか) (4)採用/除外 (5)必要最小Factだけの「Selected Fact Brief」を出力(目安3〜5件、6件以上は再検討理由)。技術retry 1回(JSON不正/不明fact_id)。モデルはrouting `FAMILY_X_STORYLINE_B3`=gpt-6.1-sol。
- 後段: 決定論annotator(`er053_b3_deterministic_producer_01`)が【事実N】注記・数値印を付与、`validate_annotated_b3`(V1〜V10、sha/schema/Fact番号連続/数値印/Storyline完全一致 等、LLM非依存の契約検証)を通ったものだけがW-1 R0へ渡る。
- W-1: R0(Fact Lockブロック付き、日本語、effort=high)→記号QA→R1「事実関係は変えずにもっとエンタメ性を上げる」→R2(R1生出力を入力、同指示)。

## 2. B3Z設計(Family Z向け最小変更)と差分・理由
| 項目 | Family X B3 | B3Z(Trial) | 理由 |
|---|---|---|---|
| 入力 | Full Fact Ledger(多数の事実) | Seed(seed_elements 6件+conversion_plan、story_prompt.txtのSeedブロック逐語) | FictionにFact台帳は無い。(1)(2)と同一情報のみ(情報量の公平性) |
| 目的 | 事実の選別(4テスト)で最小Fact集合 | 中心Story・重要場面・引き込み展開・クライマックス/余韻・維持条件の整理 | ユーザー指定5項目。Fictionでは「削る」より「魅力の核を守る」 |
| 4テスト | 全Factに適用 | 適用しない。代わりに key_scenes[].why(なぜ必要か)を要求 | 事実選別Gateの構造はFictionに不要。ただし「必要理由の明示」は踏襲 |
| 出力 | selected_fact_brief(Storyline1行+Fact) | 5項目+may_simplify_or_omit+brief_text(120〜250語、`Storyline:`1行で開始) | Writerに渡す素材はbrief_textのみ |
| 新規創作 | 台帳外Factは禁止(V10/ID検証) | **新しい出来事・人物・因果・結末の創作禁止**。細部の簡略・省略は可 | ユーザー指示。検証は下記 |
| 検証 | V1〜V10(sha/注記/Fact番号) | Z-V: JSON schema、key_scenes>=4、preservation>=3、brief先頭`Storyline:`、brief 60〜320語、原作人名(Selinuntius等)混入なし。技術retry1回 | V1〜V10は注記契約でFictionに該当しない。同じ「技術のみ・内容では再試行しない」思想 |
| 注記・Fact Lock | あり | **なし** | Fictionは世界の事実断定ではない。Fact Lockタグはメロス英語Storyには不適 |
| model | gpt-6.1-sol | gpt-6.1-sol | (2)(3)同一 |
- 無条件流用しなかった点: Fact 4テスト、注記・タグ、V1〜V10契約、数値印、日本語Prompt文言。流用した思想: 1 call整理→Writerには整理済みBriefだけ渡す、技術retryのみ、不明要素創作禁止。
- Family Z既存仕様との整合: A2・280〜420語・主人公のみ固有名・原作忠実を維持。B3Zは**既存Family Z仕様に無い工程**であり、Trial内仮説。Production採用なら別途ユーザー承認が必要(OPEN候補)。

## 3. (2)(3)工程設計
- R0: 既存Trial `story_prompt.txt` 逐語+`WRITER_DEVELOPER_MESSAGE`(er018 e_axis)逐語。(3)のみ Seedブロック直後、共通原則の前に `[Story Brief]` を挿入。
- R1/R2: Family X W-1 の「事実は変えずにエンタメ性を上げる」指示の英語版+Family Z要件(A2・約280〜420語・三人称・主人公のみ固有名・タイトルと本文のみ)。R2の入力=R1の出力。R1/R2はBriefを見ない(Xと同じ)。
- (2)(3)とも同一 model(gpt-6.1-sol)・effort(high)・Prompt。温度は推論モデルのため指定なし(全call同一)。
- Writerモデル選択: pricing/routingには `gpt-6.1-sol` のみ登録(`gpt-6-sol`は未登録)。25節(最新原則)とJA Production採用実績により **gpt-6.1-sol** を使用。ユーザーの「GPT-6 Sol」の解釈であり、ID確認は報告に残す(OPEN候補)。routing/pricingは変更せず、実行時に routing `FAMILY_X_FACTLOCK_R0` 値との一致をassert。
- Seed: (1)と同一rawの `story_prompt.txt` Seedブロック。
