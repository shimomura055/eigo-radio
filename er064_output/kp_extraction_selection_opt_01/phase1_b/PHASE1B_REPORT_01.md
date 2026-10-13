# PHASE1B_REPORT_01: FAMILY-X-KP-EXTRACTION-SELECTION-OPTIMIZATION-01 委任_01B(Phase 1-B)

日付2026-10-13。費用JPY0(有料LLM呼出なし)。Trial専用。Production Prompt/schema/コード無変更。`APPROVED_FOR_PRODUCTION`ではなく、Phase 2(有料Trial)はFable承認後。

## 1. 結論(先に)
1. 現行選定Promptは20ブロック中、**重複5・矛盾6・冗長5・Level差1**。代表: 「B1英語記事本文から」(本文は渡されない、Stdにも固定)、「難しい箇所を見つけて抽出」(候補から選ぶ契約と矛盾)、旧契約文言`source_span`の残存、「記事固有の長い説明は禁止」(短縮誘発の疑い)、グロス規則の3段落分散。**6指標の定義文は存在しない**(順序の列挙のみ)。
2. 改善Prompt(After、Trial専用)は、**6指標の順序行を逐語維持**、指標の追加0、上記の矛盾・重複・冗長を整理したうえで、(a) 同程度のときの定着度タイブレーク、(b) 既知の基本連語の相対的な優先度低下(Level別1文のみ)、(c) 学ぶ単位(目的語・補語まで、`含む/含まれる`注釈の利用)、(d) Topic=本文理解への貢献/Important=他記事でも使える定着表現/記事独自の創作的比喩はImportantに選ばない、(e) 出力schemaに記録用`established_or_article_specific`、を足した。Coffee語句はPromptに含まない(test)。
3. **tokenはBeforeより約+10%(Std +288、Adv +304)**。追記のみのPkg P(+433)より約130〜145 token少ないが、「できる限り短く」は達成していない。
4. 静的評価: 既存shortlistに対し**確実に効く(○)のは、断片・ラベルだけの基本連語を下げる方向と、問題候補が無い場合の無害性**。記事独自比喩のImportant回避・断片回避・Topic評価は**LLM判断依存の△**(ABCで現行LLMは記事独自比喩にimportantを付けた実績あり)。効果の有無はPhase 2でしか分からない。
5. Phase 2は、推奨3段階(Coffee C0/C1/C2 → meta C0/C2 → hormuz C0/C2、n=3、計42 job)で**推定JPY45.16 / JPY50**。3記事×3条件の完全版(54 job、JPY57.9)は収まらない。収まらない比較(meta/hormuzのC1、Coffee C3)は未検証と明示。

## 2. 成果物(すべて `er064_output/kp_extraction_selection_opt_01/phase1_b/`)
| ファイル | 内容 |
|---|---|
| `prompt_before_01.txt` | 現行Prompt全文(developer/静的instructions/候補形式/guidance/schema、逐語) |
| `prompt_after_01.txt` | 改善Prompt全文(Trial専用、LEVEL_RULE含む、逐語) |
| `specimen_after_std_v5_01.txt` / `specimen_after_adv_v5_01.txt` | Coffee v5実run候補を入れたAfter完成形 |
| `prompt_diff_01.md` | 棚卸し表・差分表・根拠・token |
| `static_eval_01.md` | 机上評価(受入2〜7の○△×)・矛盾チェック・Rule7切り分け |
| `phase2_plan_01.md` / `phase2_cost_estimate_01.json` / `phase2_expected_labels_draft_01.json` | Phase 2設計・費用・期待ラベルDRAFT |
| `token_measure_01.json` / `test_results_01.txt` | token計測(tiktoken o200k_base近似)/test 40件PASS |
コード(Trial専用、Production非接続): `er064_kp_opt_01_prompt_build.py`、`er064_kp_opt_01_prompt_test.py`、`er064_kp_opt_01_prompt_cost.py`。

## 3. 検証した事実(runtime evidence)
- Beforeは`extract_static_instructions`+`_FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE`から取得し、Coffee v5実run(`er019_output/.../coffee_prices__run_v5_ms_01/{a2,b1b}/.../keywords_selector_prompt.txt`)の先頭・末尾とバイト一致を確認(build内assert、test T6/T7)。Std/Advの文言は完全に同一で、差は候補リストだけ。
- developer message=「英語ポッドキャストの初回リスニング理解を助ける、短いKey Wordsを選定してください。」、reasoning effort=high、schema=strict(Production既定)。
- test 40/40 PASS: 順序行の逐語維持、Coffee語句の不在、必須語の保持、Std/Adv差=LEVEL_RULEのみ、候補セクションのバイト一致、schema差分=1フィールドのみ、Production 4ファイルに未コミット差分なし。
- token: Before Std 2,755/Adv 3,127、After Std 3,043/Adv 3,431(user全文)、schema +72。近似でありgpt-6-lunaの実tokenizerではない。
- 副次: 作業中、tiktoken導入確認で`pip download`がrepo直下にwheel 7個を作ったため、自分で全て削除済み(commit対象外、確認済み)。

## 4. 未決・Fable判断事項(実装せず報告)
1. **OPEN-J(Std「B1」)**: AfterはTrial専用に「B1」を除去しLEVEL_RULEへ移した。指摘のみの指示だったが、「本文から」の矛盾解消のため同時に動いた。効果の帰属を分離するか(C3)はFable判断。
2. **グロス段落の統合(D12)**で約-119 tokenだが、グロス出力が変わる可能性。圧縮を戻す選択肢あり(その場合 +119token)。Phase 2でja_gloss機械検査を入れる設計。
3. **新しい仕様候補(報告のみ)**: Rule7 INVALID対策としての「displayに候補に無い語を足さない」Prompt文。OPEN-310(Pkg R)との重複判断が必要。
4. **`pumps its fist`**: After文面では「他記事でも使える定着した動作表現」と読める余地(Important可)と、記事独自の擬人化と読む余地の両方がある。ユーザー基準は設計書§10-E=未確認。期待ラベルでは維持確認扱いに留めた。
5. Phase 1-A出力(改善shortlist、注釈`含む:`/`タグ:`)が未入手のため、`time lag`関連の受入1は本Phaseの対象外とし、条件付きで記載した。
6. 「5語上限」と「完結したまとまり優先」の残存矛盾(`putting the two figures in the ring`は6語)はPromptでは解けず抽出側(Pkg E)の領分。
7. 本委任文は抄録のため`check_delegation_prompt.py`はFAIL想定で未実行(記録のみ)。

## 5. 限界
- 机上評価・token近似であり、LLMの実挙動は未測定。○の多くは「該当候補が無い」型で改善の証拠ではない。
- 使用モデル: 本Phaseは呼出なし。Phase 2はgpt-6-luna(Production同一、最新モデル原則の例外=比較可能性)を予定。
