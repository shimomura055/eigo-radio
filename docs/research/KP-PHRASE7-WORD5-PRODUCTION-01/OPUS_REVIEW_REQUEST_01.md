# OPUS_REVIEW_REQUEST_01: 条件A(新しい構造・処理フローの設計)独立技術レビュー依頼
KP-PHRASE7-WORD5-PRODUCTION-01 委任_01 / 2026-10-27。依頼者=Fable。レビュー対象=設計(コード未編集)。実装前に実施(PM_GOVERNANCE 11-3 条件A)。結果は`docs/pm/OPUS_FINDINGS_LEDGER.md`へFableが反映(本委任はledger未更新)。

## 0. 背景(5行)
ユーザー正式採用(APPROVED_FOR_PRODUCTION 2026-10-27): KP最大7+KW最大5の分離抽出を、X/Y/Z x Std/Advの正式経路へ配線。Key Word優先順位5条件・補足(KP含有語はKW候補から除外)・出力規則は原文固定。補完・KP救済・HR・フォーム整合は承認済み仕様を維持。共通配線点=`er119_kp_candidates_01._generate_candidates_impl`。資料: `DESIGN_01.md`(§番号)、`CURRENT_PIPELINE_01.md`、`IMPL_PLAN_01.md`、`TEST_PLAN_01.md`、`EVIDENCE_PLAN_01.md`、`INVENTORY_ABC_01.md`。原文: `docs/pm/delegation_log/2026-10-27_KP-PHRASE7-WORD5-PRODUCTION-01_USER.md`。

## 1. 論点(必須回答。各「問題なし/要修正+理由」)
| # | 論点 | 見てほしい点 | 設計の位置 |
|---|---|---|---|
| Q1 | **Prompt置換の影響範囲** | Prompt 2/2-Vを残置しP7/W5'を新moduleに置く方式で、`er105`のkeyword-only引数拡張(既定=従来動作)が、legacy経路(`er003:753 run_kp_with_outer_retry`、`er106`evidence、A/B/Cの隔離)へ副作用を出さないか。`select_p7`が`sc.run_key_phrase_selection`(telemetry含む)を経由しないことの影響(`kp_backend_telemetry`集計) | §1,§6 / IMPL F2,F3 |
| Q2 | **attempt loopとP7の整合** | P7最大7件でも`run_selection_gate`の「1件でもitem不適合なら全件再選定、最終attemptはCMU/除外句のみ落とす」を維持した場合の全体INVALID(外側retry)確率・費用。K1(item単位化=承認済み仕様変更)を今回導入しない判断の妥当性。Trial-02 P7 34件で不合格0という根拠の十分性 | §6, INVENTORY C-1 |
| Q3 | **containment二重化** | KP含有語除外を(i)W5'本文(ii)`duplicate_of_top3`(双方向containment)の二重で担保する設計。方向性/表層形のずれ(語形違い`price`/`prices`、基本形化後のフレーズと単語)で承認補足を取りこぼす/過剰除外するケース。W5'補足行の文言案(第2文の要否、D4) | §1-2, §3 |
| Q4 | **補完計数の7・5** | `plan_quota`を種類別上限(7-現存フレーズ, 5-現存単語)・E_phrase/E_word上限へ。`not_single_word`のE計数(kind=word固定)の妥当性(D3)。`overflow_kind`をEに数えない扱い。承認仕様(Eを超えない/初回保持/再課金防止)との整合。委任文の「初回上限到達」条件を採らない解釈(原文優先)の妥当性 | §3-A, §5 |
| Q5 | **補完Promptの種類別化と並列2 call** | 補完をP7(フレーズ)/W5'(単語)に分け、ALREADY節をP7へ後置する方式(P7本文は不変だが本文が「すでに選ばれた表現」に言及しない)でLLMが現存候補を避けるか。結合した1回の`_gate_chain`、contextvars(`rescue_context`・`_person_repair_subdir`)のスレッド引継ぎ、STOP伝播(R-8)、stop_check位置(M-4) | §5 / IMPL §4-5 |
| Q6 | **HR自動推奨とAdv vocab5** | `auto_select`無変更(kp=P7上位3、Adv vocab=P7上位5=単語は含まれない)の判断(D2)。旧挙動(call2混在)との差の許容性、`render_request_md`の「単語」印の意味ずれ。AUTO(不在宣言)で単語を組入れる案は新仕様として分離してよいか | §4 |
| Q7 | **resume二重生成・確定内容保護の境界** | 保存済みdoc読戻し・reselect(round2が7+5、round1が3+5)・本文変更(STALE)・外側retryのP7再課金構造で、二重生成/確定内容書換えが起きないか。「既存単語を含む新規補完フレーズ」で既存合格単語を保持する扱い(原文§4保持 vs 原文§3補足)の整合。KCP設計との境界(確定前=本件/確定後=KCP) | §7 |
| Q8 | **sha固定test** | Prompt 2/2-V pin据置+P7/W5'新規pinの方針。W5'のsha案(`187f1b87…`)確定手順。`er106`の`KPFT_PROMPT_2_SHA256`扱い。`er124`(Trial module)の回帰維持 | §8 / TEST_PLAN §0,§3 |
| Q9 | **旧方式復帰手段の要否** | R0(flagなし、git revert 1手順・旧Prompt残置)かR1(`EIGO_KP_P7W5=0`)か。11-7の趣旨(superseded方式を環境変数で再現可能にするリスク)との関係。推奨=R0 | §9 |
| Q10 | **費用・時間** | +約¥0.24/level、+約¥0.5/記事セット、+25秒/level(Trial実測の外挿)。補完2 call・P7再選定を含む悪い場合の上限見積。call1->call2直列の妥当性(W5'がcall1のフレーズを要する) | §10 |

## 2. 追加で確認してほしい点(任意)
- 種類別cap強制(`overflow_kind`)を新設する必要性/代替(Prompt側のみ)。
- 12件を1回のcanonicalization call(Luna)に渡す際の出力トークン・失敗率(Trial-02は9〜11件で実績)。
- Z固有: 単語候補のSRC D1(複数文に出現する語のambiguous扱い)で単語が落ちやすくならないか(Trial-02 猿の手Std4/Adv4で通過実績)。
- テストの網羅性(`TEST_PLAN_01.md`の受入条件1〜9と抜け)。

## 3. 範囲外(レビュー不要・判断済み)
Trial-01/02の有用候補閾値(Y/B)・猿の手Adv偏り・易語混入の是非・追加Trial要否(原文§2/§7で判断済み)。フォームv3の送信schema・UI(並行委任)。確定内容不変性Gateの詳細(KCP委任)。A/B/C(27-7で開発対象外)。

## 4. 回答形式の希望
各Q: 判定(問題なし/要修正/要判断)+理由+修正案。D1〜D6(`DESIGN_01.md §11`)へのOpus意見。GO / GO with changes / NO-GO。GO with changesの場合は必須変更(M-n)と任意(R-n)を分けて列挙。

## 5. 実行メモ
同一内容の重複レビューは不要(`OPUS_FINDINGS_LEDGER.md`の既存指摘[KP-GATE-DROP-BACKFILL M-1〜M-7/R-1〜R-10、KP-GATE-EXCLUSION-RESCUE M1〜M4]は継承済みとして扱い、今回の差分[Prompt差替・種類別上限・補完Prompt]に集中)。内容が変われば再レビュー。レビュー後の次工程判断はFable(11-3のSTOP条件に該当しなければ委任_02へ)。
