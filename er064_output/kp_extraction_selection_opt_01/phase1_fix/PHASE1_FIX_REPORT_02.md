# PHASE1_FIX_REPORT_02: FAMILY-X-KP-EXTRACTION-SELECTION-OPTIMIZATION-01 委任_02(Phase 1修正: M1〜M4 + R1〜R3)

日付2026-10-13 / 費用JPY0(LLM/TTS/ASR呼出0、Wiktionaryはsnapshot再生のみ・追加照会0) / Trial専用(Production Prompt/schema/コード無変更) / **`VALIDATED`でも`APPROVED_FOR_PRODUCTION`でもない**。Phase 2(有料)は未実行でSTOP。使用モデル: LLM不使用(該当なし)。
本委任文は抄録のため`check_delegation_prompt.py`のFAILは記録のみ(未実行)。STOP通知(Melos E2E)は本件と無関係、新規API呼出なし。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)は編集していない。

## 1. 反映状況(結論)
| ID | 内容 | 結果 |
|---|---|---|
| M1 | 注釈書式の統一 | Prompt側をrows側の英語ラベル(`contains: Cn`/`contained_in: Cn`)へ統一。ラベルは`upstream_core.py`の定数に一本化。test追加。C1は説明なしの注釈が渡る旨を計画書に明記 |
| M2 | 固定shortlistの再固定 | 全条件を同一builder・**実タイトル**で再組立。sha再固定。C0がProduction実runの候補行とバイト一致(Coffee Std/Adv・meta Std/Adv。hormuzは旧方式Promptで照合不能) |
| M3 | 改善Promptの短縮 | C2のPrompt自体を短縮。**現行比 Std -168 / Adv -150 token**(目標=現行以下を達成)。6指標の順序行は逐語維持 |
| M4 | 計画書の明記と改訂 | 測定不能項目の明記、V2 shortlist向けC2' Coffee Adv 3 jobの追加、42 job / 約JPY44.58 |
| R1 | 閉じた語類終わりhitのimportant判定除去 | `alt_precision_guarded_r1`で検証。**希少単語の押し出しは減らない(6→6)ため主対照にしない** |
| R2 | U2 Tier-Hの発火条件 | 長い側がimportant判定またはdemotedでないときに限定(コード+test)。10記事の結果は変化なし |
| R3 | fragment_riskから助動詞始まりを除外 | コード+test。Phase 2の6記事のrowsには`fragment_risk`は出現しない(0件) |
| R4 | jobごとusage記録 | 計画書に記載(入力/出力/reasoning token) |

## 2. M1: 注釈書式
選択=Prompt側を英語ラベルへ。理由: 既存の候補行は英語key(`id:`/`candidate:`/`type:`/`occ:`/`evidence:`/`sentence:`)で、行側を日本語化すると現行Prompt(C0/C1)と混在する。`LABEL_CONTAINS="contains:"`等を`er064_kp_opt_01_upstream_core.py`に定義し、rows生成とPromptの両方が参照する。旧Prompt(01版)の「含む:Cn」は廃止。test: Promptがラベルを参照、旧ラベル無し、10記事x4構成のrows内注釈ラベルは全てPromptが説明済み。
**C1(現行Prompt+guarded)では注釈の説明なしで注釈行が渡る**(出現記事: Coffee Std/Adv、smallbag、semi。meta/hormuzは0件)。C1の差には「説明のない注釈の影響」が混ざる。

## 3. M2: 再固定shortlist
- 成果物: `shortlists_fixed_02.json`、sha256 = `2940d0716edf56a4f6b547d747549b04188ac5444bc2367e6f2508ee4a496121`(sidecar `shortlists_fixed_02.sha256.txt`)。snapshotは`phase1_a/wiktionary_snapshot_01.json`(sha256はファイル内`snapshot_sha256`)。10 article-level x 4構成(`current`/`improved`/`alt_precision_guarded`/`alt_precision_guarded_r1`)、各rows_textにsha256。
- 01版の不具合: rows_textのタイトルが全件`T`だった。今回は記事の先頭`# `行(Production実runの`【Topic】title:`と同一)を全条件に入れ、test(`'T'なし`・全rowsに実タイトル)で確認。01版`shortlists_improved_01.json`は無変更で残置(履歴)。
- **C0バイト一致(`c0_byte_match_02.json`)**: Coffee Std ○ / Coffee Adv ○ / meta Std ○ / meta Adv ○ (Production実runの`keywords_selector_prompt.txt`の【Topic】〜【選定方針】直前をバイト比較、全て一致)。hormuz Std/Advは、Production実run(`family_x_b3_diversity_trial_01/hormuz__run_02`)の選定Promptが候補一覧方式導入前の旧方式で候補行が存在せず**照合不能**(`byte_identical: null`と理由を記録)。hormuzのC0は「現行構成の再生」であり、Production実runとの一致は未確認。
- Wiktionary追加照会: 0(`network_misses_fallback`が空)。

## 4. M3: 短縮Prompt(全文は`prompt_after_02.txt`、差分・段落別は`prompt_diff_02.md`)
| | 現行 | 01版After | **02版After** | 02 vs 現行 |
|---|---|---|---|---|
| Std user全文(v5候補入り) | 2,755 | 3,043 | **2,587** | **-168** |
| Adv user全文 | 3,127 | 3,431 | **2,977** | **-150** |
| output schema | 1,113 | 1,185 | 1,113(Production同一) | 0 |
tiktoken `o200k_base`近似(gpt-6-lunaの実tokenizerではない)。実Phase 2のC2はguardedの候補行(平均+約51token)が加わるが現行以下。
主な短縮: 定着度と既知基本連語を1段落へ統合、区分3行を1文へ(「この区分の優先は、質が同程度のときの補充規則です」で『同格 vs 区分優先』を位置づけ)、topic段落を半分程度に、`take care`例示削除、`established_or_article_specific`欄削除、Level差を各1文。グロス統合は維持(ja_gloss機械検査をPhase 2に追加)。【判断の基準】の6指標順序行は逐語維持(test)=Opus再レビュー対象の変更なし。「5語上限 vs 完結まとまり」は抽出側(方式2)の問題としてPrompt側では対処せず計画書に注記。

## 5. R1の結果(`r1_and_metrics_02.json`、10 article-level平均)
| 構成 | shortlist平均件数 | 候補行token(現行比) | 希少単語の押し出し(Tier-H除く) |
|---|---|---|---|
| current | 22.7 | 基準 | 0 |
| improved | 28.6 | +246.9 | 18 |
| alt_precision_guarded | 23.3 | +50.8 | **6** |
| alt_precision_guarded_r1 | 22.9 | +32.7 | **6** |
- 押し出される単語(guarded): `inappropriate`/`negotiate`(meta Adv)、`lip`/`runway`(smallbag Std)、`clearer`/`luggage`(smallbag Adv)。R1適用後も同じ6件。
- R1が除去した重要語行は3種6行: `want to`(Coffee Adv・semi Std・semi Adv)、`call it`(meta Adv)、`close to`(hormuz Std/Adv)。`take care`/`be wrong`は最後が内容語のため残る(test)。R1は押し出しを減らさず、noise行の除去(-0.4件/記事)のみ。**Fable条件(押し出しが減るならR1を主対照)を満たさないため、主対照は`alt_precision_guarded`。**
- 数え方の訂正: 01報告の「8件」は`crude`x2(U2 Tier-Hで`brent crude`に包含され意図的に除去された語)を押し出しに含めていた。今回の再計算では意図的なTier-H除去(`lag`/`calculator`/`crude`x2)を除いた6件。Tier-H除去自体はguarded構成で4件(`lag`⊂`time lag`、`calculator`⊂`mental calculator`、`crude`⊂`brent crude` x2)。
- R2: R2のON/OFFで改善shortlist(10記事)の結果は同一=実記事への影響0、unit testで挙動を確認。R3: 同様に実記事のfragment_risk付与は0件(Phase 2の6記事のrowsに出現なし)、unit testで`been behind price increases`等が外れ`in the ring`は残ることを確認。

## 6. M4・Phase 2改訂計画(詳細は`phase2_plan_02.md`、費用は`phase2_cost_estimate_02.json`)
- 方式1のshortlistでは**測定不能**: Coffee `push prices up`/`be behind price increases`/`in the ring`/`its own hidden clock`/`pump one's fist`、hormuz `give back gains`/`take a sharp turn`(+`strait of hormuz`)はどの構成にも存在しない(test M4)。ゆえに受入2・受入4のnever_fragment・R8は方式1では測れず、方式2のV2 shortlist(C2')のみ。期待ラベルは「両条件のshortlistに共に存在する候補」に限って比較(`phase2_label_coverage_02.json`。`time lag`はC0に無くguardedのみ、`of a`はC0のみ)。
- 構成: Coffee C0/C2 両Level(12)+C1 Adv(3)+C2' Adv(3)=18、meta C0/C2(12)、hormuz C0/C2(12)=**42 job / 約JPY44.58 / 上限50 / 停止規則48**(残3.42)。C0'はABC-A既存結果の再利用。
- 評価層: 選定指標はgate前のselector生出力(5件+backup)で全jobを採点、gate(Rule7 INVALIDを`rule7_predicted_invalid_01.json`と自動照合、Redundancy QA)は別層。**実挙動(コード確認)**: canonicalizationがPASS/REVIEW_REQUIRED以外(INVALID等)のときRedundancy QAは**実行されず**(Trial: `er064_kp_idiom_trial_01_select.run_canonicalization_and_qa`、Production同型: `er003_v1_b1_scaffold_01_generate.py:307`)、Redundancy NG率の分母はcanonicalization通過jobのみ。jobごとのusage(入力/出力/reasoning token)を記録。ja_gloss機械検査。hormuzは`strait of hormuz`欠落を注記。

## 7. test(件数)
- `er064_kp_opt_01_fix_test_02.py`: **64/64 PASS**(M1〜M4・R1〜R3・Production 8ファイル無変更)、`test_results_fix_02.txt`
- 既存`er064_kp_opt_01_prompt_test.py`(01版build): 40/40 PASS / 既存`er064_kp_opt_01_upstream_test_01.py`: 34/34 PASS(コア変更が互換であること)
- 合計138件PASS。

## 8. 成果物
`phase1_fix/`: `PHASE1_FIX_REPORT_02.md`(本書)、`prompt_after_02.txt`(sha256 `f3d1bdba4e62697eb99326bf6383154408e9ca7e913b29e38b23e00582fd2786`)、`prompt_diff_02.md`、`token_measure_02.json`、`specimen_after_{std,adv}_v5_02.txt`、`shortlists_fixed_02.json`(+sha256.txt)、`c0_byte_match_02.json`、`r1_and_metrics_02.json`、`phase2_plan_02.md`、`phase2_cost_estimate_02.json`、`phase2_label_coverage_02.json`、`test_results_fix_02.txt`、`fix_run_02_log.txt`。
コード(Trial専用): `er064_kp_opt_01_upstream_core.py`(R1/R2/R3/ラベル定数/title引数を追加、既定は01互換)、`er064_kp_opt_01_fix_run_02.py`、`er064_kp_opt_01_prompt_build_02.py`、`er064_kp_opt_01_fix_test_02.py`、`er064_kp_opt_01_phase2_plan_02.py`。

## 9. 未決・Fable判断事項(実装せず報告)
1. R1適用版を主対照にするか(押し出し条件は未達、noise除去のみ)。
2. hormuzのC0はProduction実runとの照合不能(旧方式)。C0の代替確認方法が必要か。
3. V2 shortlist(C2')のrows書式が`contains: Cn`注釈を含むか未確認(Phase 2実行前に確認)。
4. 01報告の「押し出し8件」は`crude`x2の数え方の誤り(上記訂正)。
5. `tiktoken`はスクラッチ領域へ`pip install --target`で導入(repo外、commit対象外)。

## 10. 限界
机上・オフライン検証。LLMの実挙動は未測定。token数は近似。Phase 2の効果判定は方式1だけでは受入2・4の主要項目を測れない。
