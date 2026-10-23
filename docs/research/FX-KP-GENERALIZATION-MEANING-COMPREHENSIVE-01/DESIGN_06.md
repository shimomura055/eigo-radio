# DESIGN_06: 2課題(①Std字義訳 / ②見出し語の人称placeholder)の改訂設計(委任_14、Opus条件Aレビュー[OPUS_REVIEW_05.md]の必須修正OF-D5-01〜05を全て、推奨06〜13も反映)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_14 / 前版=`DESIGN_05.md`(委任_13)/ 根拠=`ROOT_CAUSE_03.md`・`OPUS_REVIEW_05.md`・ユーザー指示`delegation_log/..._USER_06.md`
状態: **設計(未承認の新仕様案)**。Production/Prompt/flag/閾値/golden変更0。A-1は`APPROVED_FOR_PRODUCTION`のまま(併存設計、§4)。
作成上の注記(事実): 本書は実装・Trial後にまとめて書いた。ただし(a)事前層別(`TRIAL_04/strata_04.json`)・(b)検査のflag規則(`er112_kp_gm_trial_04_c.py`の`is_flag`、V2_inv)・(c)②のgold(`er112_kp_gm_trial_04_poss.py`の`GOLD`)は、該当API呼出の**前**にfileとして確定済み(file作成順は下記§7のコマンド履歴/台帳tsで確認できる)。Phase 0後に変えた点(検査Prompt v1->v2、effort medium->low)は§3-2に変更理由つきで記録した(1回限りの改訂)。

## 0. 結論(推奨案)と、Trialで分かったこと

| 課題 | 推奨(改訂後) | 追加LLM call | Adv(B仕様)変更 | Trial結果の要点(詳細=`TRIAL_RESULT_04.md`) |
|---|---|---|---|---|
| ② 見出し語の人称placeholder | **`possessor_roles`(display内の所有格1個ごとの{token, role})を`rank`直後に出させ(role先行判定)、決定論の後処理でrole↔見出し語の食い違いを1トークン置換で修復する**。再帰代名詞は決定論でself。置換しない選択は常に許可 | **0** | なし | 所有格項目42件(目視gold付き): 現行+A-1は**誤り9件(21%)→本案0件**、role判定の正解40/42、INVALID/REVIEW_REQUIRED 3→1、対照(非所有格)項目の同一率99/102。**ただし決定論修復は発火0**(効果の源泉は『role先行判定』によるLLM出力の変化)。正しい一般化の2件が許容形(無変更)へ後退 |
| ① Stdの字義訳 | **C(独立検査+flag項目のみ再生成)を推奨。C'(同一call自己監査)は不採用(自己監査flag 0/61=検出力ゼロ)、M(新規生成だけ再整合用の指示を除くmessage)は不採用(字義NGが減らず出力の62%が変わる)** | **+1回/記事**(検査)+flag時のみ再生成 | なし | 検査(effort low)はflag 19/122出力(15.6%)。字義NG(既知2出力)は2/2検出、ただし**再生成後も字義寄りが残る**(an unseen clock→「目に見えない時間の流れ」)。flag項目内は改善4・不変12・悪化3(Sonnet参考)。**precision低(2/19)で「解消」とは言えない**。Fable盲検判定待ち |

- 採用までの経路: Offline Trial(DEV)→VALIDATED(Fable判定)→**ユーザー正式採用**→Production配線(11-7の限定例外は、既存Prompt/validatorを直接編集する本件には適用しない)。
- ①の追加費用は実測で**約+0.2〜0.25円/記事**(検査0.12〜0.15+再生成0.07/call)で、事前に置いた「追加≤0.15円/記事」を**超える**(§5)。②は+0.03円/記事。

## 1. Opus条件A必須修正・推奨の反映状況(OPUS_REVIEW_05.md)

| ID | 内容 | 反映(本書節/実装) |
|---|---|---|
| 01[必須] | ②roleを項目単位→人称トークン単位。再帰代名詞は決定論でself。所有格は`possessor_roles`出現順配列、要素数=display内所有格数を決定論照合 | §2-2。`er112_kp_gm_poss_04.py` `possessive_slots/validate_roles`。再帰代名詞は閉じた許可表がoneselfのみ許可=変更不要(決定論) |
| 02[必須] | ②修復の範囲と整合: (i)置換しないことは常に許可 (ii)noneなのに置換はINVALIDでなくrevert (iii)fulltext keyの部分窓対応 (iv)修復後に`changed_from_display_phrase`・`normalization_reason`・QA実効値を決定論で再計算 | §2-3。`repair_item/find_window/recompute_fields`、test 16件(`er112_kp_gm_poss_04_test_01.py`) |
| 03[必須] | ①検査callの逆訳設計: 出力順(1)usage_meaning_en->(2)gloss_alone_reading_en->(3)gloss_conveys、KPの内容語との重なりを決定論検査、flag条件2種を同一出力から事後比較 | §3-2。`er112_kp_gm_trial_04.py` `INSPECT_*`/`overlap`/`flag_variants` |
| 04[必須] | ①C/C'採否規則を対称に(C'採用条件=(a)recallがC以上 かつ (b)未flag悪化がノイズ内。欠ければC。同等ならC優先) | §3-4。Trial結果: C'のrecall=0(flag 0/61)→**C** |
| 05[必須] | ①事象が少ない場合の事前宣言(B0のNG<6件なら比率でVALIDATEDとせず、既知NG+recall/precision+Before/After) | §4。Trial内のB0字義NGは2出力(1 KP)=閾値未満→この規則で判定。Phase 0(既存出力で較正)実施: `TRIAL_04/PHASE0_CALIBRATION_01.md` |
| 06[推奨] | ①原因に生成Prompt側の誘因(再整合用の指示・例・qa名)。G3参考armを「新規生成だけ再整合用指示を除くmessage」armに置換 | §3-3 M arm(`build_m_message`)。結果=字義NGが減らない(§0)→不採用 |
| 07[推奨] | ②規則3の例示の偏り(their/your->someone's、pumps its fist->pump one's fist)を均等化(特定記事の語句は使わない) | §2-4。self/other/non_personの一般例3つ(`lost his temper`/`praised their effort`/`challenged its conclusions`)+規則4の例も同じ語へ |
| 08[推奨] | ②roleとkeyの食い違い時に「roleに合わせる」vs「displayへ戻す」をC1A同一出力へ事後適用(API 0) | §2-3。`process_response_text`が両方をlogへ保存。**結果: 食い違い0件のため両者同一(比較不能)**。fake入力のtestで挙動確認 |
| 09[推奨] | ②roleの2軸定義(動作主と同一か/人か物か)、物が動作主の定型句は現状維持許容、QA定義も「roleに従った現状維持はPASS」 | §2-4(`ROLE_BLOCK`、QA文言) |
| 10[推奨] | ①再生成後の再検査変種(C-recheck)、attempt 2採用済みは`FLAGGED_UNREPAIRED_NO_ATTEMPT` | §3-2。E2E注入に実装(`er112_kp_gm_trial_04_e2e.py`)。再検査は14出力(0.19円) |
| 11[推奨] | C-Solの費用基準不整合 | **C-Solは実施しない**(予算上の理由+luna再生成で残存が確認できた時点で別途検討)。実施するなら別の費用基準(1call 1.13円x flag率)を事前明記する |
| 12[推奨] | 非劣化の分母: flag項目内の悪化数・率を主指標、goldのPASS->FAIL 0を要件 | §4。結果は`TRIAL_RESULT_04.md`のflag項目表 |
| 13[推奨] | test影響(my/ourにsomeone's追加) | §6。`er064_kp_idiom_trial_01_test_01.py:56`が反転(`my`->someone'sは現行テストでFalse期待)。他2 test fileは環境(wordfreq未導入)でcollect不可と判明 |
| 14〜19[情報] | 決定論字義検出不可/Std-Adv整合不採用/fail-open件数を必ず出す/Store reuse崩れ/「解消」の条件/§7に規則3例示変更・M armを追加 | §3-5・§5・`WIRING_DESIGN_04.md`に反映。「解消」表記はOF-18の条件(F層残存・anchor残存ほぼ0)を満たさないため**使わない** |

## 2. 課題②: 見出し語の人称placeholder(改訂設計)

### 2-1 仕組み(要約)
1. **fulltext専用schemaの`rank`直後**に`possessor_roles`: `[{token, role}]`を追加(`key_phrase`の前=生成順でrole判定が先)。role enum=`self`/`other_person`/`non_person`/`none`。A/B/C schema・Production schemaは不変(deepcopy)。
2. **fulltext template(DEV写し)**に、規則3のrole判定ブロックと均等化した例示を追記(§2-4)。
3. **decoding後処理(決定論、API 0)**: LLM応答JSONを`possessor_roles`検証(個数=displayの所有格数、tokenが出現順に一致、roleがenum内)→`find_window`でkeyがdisplayのどの連続窓かを特定→窓内の各所有格についてrole別の許可を照合→食い違いを1トークン置換で修復→`changed_from_display_phrase`/`normalization_reason`/QA実効値を再計算→`possessor_roles`を取り除いてProduction側のparse/validateへ渡す。
4. 許可表`_PERSON_DEPENDENT_TO_GENERIC`の`my`・`our`に`someone's/somebody's`を追加(DEV: install時に追加、uninstallで復元)。

### 2-2 role定義と許可(OF-D5-01/09)
| role | 意味(2軸) | 許可する見出し語 | 食い違い時の修復(role mode) |
|---|---|---|---|
| self | 動作主(または経験・所有の主体)自身を指す**人**(擬人化を含む) | displayの語のまま / `one's` | `someone's/somebody's`->`one's` |
| other_person | 動作主とは別の人 | displayの語のまま / `someone's`/`somebody's` | `one's`->`someone's` |
| non_person | 人でないもの(物・組織・場所・研究・概念。**動作主自身が物でもnon_person**) | **displayの語のまま** | 一般形(one's/someone's)->displayの語へrevert |
| none | 所有格として働かない(目的格her等) | displayの語のまま | 一般形->displayの語へrevert |
- 再帰代名詞(yourself等)はroleを問わず決定論でself扱い(閉じた許可表が`oneself`のみ許可)=roleの対象外。
- **置換しない(displayの語のまま)ことは、どのroleでも常に許可**。迷えば置換しない。`mind your own business`型などを一般化へ強制しない。
- roleが検証不能(個数/token/enum不一致)の場合は**触らない**(`UNVERIFIED_ROLES`、現行出力どおり)。件数を記録して測る(Trial: 0件)。
- 窓対応: keyがdisplayの部分窓・lemma併用でも、`er105._token_pair_ok`(Production)+A-1の参照語対応を再利用した`find_window`で窓を特定し、窓内の所有格にだけroleを対応させる(`persons_generalization_pairs`の等長前提[gloss_alignment:240-241]に依存しない)。

### 2-3 修復mode比較(OF-D5-08)
`process_response_text`は同一のLLM出力に対し、`role`(roleに合わせる)・`revert`(displayへ戻す)・修復なし(raw)を並べて記録する(API 0)。Trial実測では食い違いが42件中0件で、3モードの結果は同一だった(§TRIAL_RESULT_04)。『正しかったのはroleかkeyか』は**測定不能**(データ不足)。fake入力のunit testで3モードの挙動の違いは確認済み。

### 2-4 規則3の例示の均等化(OF-D5-07、特定記事の語句を使わない)
- 規則3の例: 旧=`catch their attention`->`catch someone's attention`/`a piece of your attention`->`a piece of someone's attention`(両方someone's)。新=self(`lost his temper`->`lose one's temper`)・other_person(`praised their effort`->`praise someone's effort`)・non_person(`challenged its conclusions`->`challenge its conclusions`)の3例。
- 規則4の例: 旧=`pumps its fist`->`pump its fist`(併用時`pump one's fist`)。新=`lost his temper`->`lose his temper`(併用時はroleに従い`lose one's temper`)。
- QA`qa_person_reference_generalized`の定義に「possessor_rolesに従って一般化しなかった場合[non_person・none、または置換しない選択]もPASS」を追加。
- Trial集合(45実データ+合成)に新例示の語句は含めていない(合成unitの語句は`raised her voice`/`admired their courage`/`questioned its methods`等、別語)。

### 2-5 retry/fallback・費用・Store reuse
追加call 0。canonicalizationの技術retry(上限2)・外側retry・Strategy L fallbackは不変。修復はretryを消費しない。canonicalization1callの平均費用は実測で+0.015円(0.279->0.294円、+5%)=+0.03円/記事(a2+b1b)。見出し語が変わった項目のみ`used_form`が変わり、既存signature(`explanation_phrase`/gloss_signature)でAdv説明が再生成される(E2Eで確認、§TRIAL_RESULT_04)。

## 3. 課題①: Std日本語意味の字義訳(改訂設計)

### 3-1 方式比較(Trial後の確定)
| 案 | 結果 | 判定 |
|---|---|---|
| **C 独立検査+flag項目のみ再生成** | flag 19/122出力、未flag103出力はB0とバイト同一(構造保証)、flag項目内は改善4・不変12・悪化3(Sonnet参考)。字義NG(FAIL_LIT)2->0だが再生成後も像寄り(THIN)が残る | **推奨(暫定)**。Fable盲検待ち。precision低・費用>0.15円/記事が課題 |
| C' 同一call自己監査 | 自己監査flag 0/61(`gloss_conveys`が一度も`literal_image_only`にならない)=検出力0 | **不採用**(OF-D5-04: recallがC未満) |
| M 新規生成だけ再整合用の指示・例・qa名を除くmessage | 出力の62%が変化(同一46/122)、検査器flag 13/122(B0は19/122)、既知字義NG出力は4出力中3(B0は2) | **不採用**(OF-06仮説[生成側誘因]はこのTrialでは支持されない)。Prompt変更の副作用(churn)が大きい |
| G2/G3、Sol全面切替 | 過去Trialで不採用/見送り(DESIGN_05 §3-1) | 変更なし |

### 3-2 検査call仕様(確定版。Phase 0で1回だけ改訂)
- 対象: gloss段で**新規生成されたgloss**(`is_fulltext_gloss_missing`だったitem)のみ。既存glossの修復経路(HUMAN_RESOLVED等)は対象外。
- 入力: 各itemの`key_phrase`・`source_sentence`・`japanese_gloss`(記事全文なし)。luna、`reasoning.effort=low`(Phase 0 v1[medium]は1call 0.259円で高すぎたため。v2[low]は0.124円)。1 call=8項目まで。
- 出力順(OF-D5-03): `usage_in_sentence`->`usage_meaning_en`(KPの内容語を使わない平易な英語)->`ja_expression_shares_figure`(v2で追加: 日本語表現が同じ比喩を日本語として自然に想起させるか)->`gloss_alone_reading_en`(日本語だけを読んだ受け取り、これもKPの内容語を使わない)->`gloss_conveys`。
- **KPの内容語との重なり**を決定論で検査(`overlap`)。重なれば`invalid=True`(検査不成立)を記録。Phase 0で、字義NG「線を引く」が検査不成立(overlap=draw)になりながらflag相当の判定を出す事象があったため、**flagは検査不成立でも`literal_image_only`なら有効(V2_inv)**と事前宣言した(失うrecall>増えるFP)。検査不成立の件数・割合は全て記録する。
- flag規則(事前宣言、`C.is_flag`): `usage_in_sentence=="figurative"` かつ `gloss_conveys=="literal_image_only"`。同一出力から事後に V1(conveys単独)/V2(figurative AND conveys)/V3 を比較(追加費用0)。Phase 0ではV1とV2は同一(flag 15件)で差が出なかった。
- 再生成: flag項目だけ、既存の`previous_attempt_rejected`機構(`build_user_message_corrected(prior=...)`)で**attempt 2**として再実行(reason=『日本語意味だけを読むと「X」の意味に取れ、本文での意味「Y」を伝えていない。本文での意味を日本語で表す』、X/Yは検査出力の英語)。attempt上限2を超えない。attempt 2で採用済みの項目は`FLAGGED_UNREPAIRED_NO_ATTEMPT`。再生成が検証失敗なら元のgloss採用+`FLAGGED_UNREPAIRED`(HR/STOPにしない)。
- 検査call自体の技術失敗は検査をスキップ(fail-open)し`SKIPPED_TECH_FAIL`を記録(**run summaryと記事報告に件数を必ず出す**: OF-D5-16)。E2Eで実装済み(`er112_kp_gm_trial_04_e2e.py`)。
- C-recheck(再生成出力を再検査し、まだflagなら元を採用): Trial(14出力・0.19円)で測定。再検査でもflagが残ったのは19再生成中3(an unseen clock x2, pump one's fist rep2)。

### 3-3 M arm(OF-D5-06)の中身
`build_m_message`: 再整合用の手順1〜3・判定の参考例(fall into等)・qa名・`過不足なく一致`・`current_japanese_gloss`/`added_content_words`を除き、承認済みgloss規則(直訳調を避ける等)・人称規則は維持。schemaは`rank, japanese_gloss`のみ。developer messageも再整合の語を除去。追加call 0。

### 3-4 C/C'採否の対称規則(OF-D5-04)
C'採用条件=(a)recall点推定がC以上 かつ (b)未flag項目の悪化がB0の2rep間ノイズ内。(a)(b)のいずれか欠ければC。差額が約0.05円/記事で同等ならC優先。**Trial結果: C'の自己監査は61/61出力が`same_meaning`(自己矛盾0・flag 0件。Sonnet参考でFAILだった2出力[question shaped like a trophy / take the wheel]も未flag=recall 0/2)、Cは既知字義NG(an unseen clock 2出力)を2/2 flag。よってC**(Claude案[C'優先]は退けた)。

### 3-5 「解消」表記の条件(OF-D5-18)
「解消」はF層残存・anchor残存がほぼ0のときのみ。本Trialでは an unseen clock がflag後の再生成でも「見えない時間の流れ」と像寄りに留まる(Sonnet参考でTHIN)ため**「解消」とは書かない**。

## 4. 判定基準(事前宣言。Fable確定可、採用時の品質水準は§7(4)に残す)
(i) 既知字義NG(draw a line / an unseen clock)の**検出recall**。F層の**残存字義NG**(目標ほぼ0)。
(ii) **flag項目内**の悪化(主指標。新規悪化の分母を全出力にしない)。gold PASS->FAIL 0件。
(iii) ②: 既存45実データ+合成の所有格項目で不一致0・正しいKP破壊0・INVALID/REVIEW_REQUIRED増0。
(iv) 追加費用≤0.15円/記事(合計)。
(v) 事象が少ない場合(B0字義NG<6件): 比率でVALIDATEDとせず、既知NG+recall/precision+flag項目のBefore/Afterで判定(OF-D5-05)。
*判定の主体は確定goldとFable盲検。Sonnet Judgeは参考値のみ。*

## 5. 費用(実測。上限60円、全体)
`TRIAL_04/BUDGET_LOG_01.md`参照。要点: Phase 0=7.0円(計画3円に対し**超過**: 検査callの費用を0.06円/call想定したが実測0.26円[medium]/0.12円[low])。Trial全体=56.6円(上限60円内)。Sonnet参考Judgeは5 callで10.0円(想定1.6円の約6倍、cap検査を発行前累計で行わず並列dispatchしたため52円capを超過)。
①追加費用/記事: 検査(low)0.12円/call(8項目)=約0.15円(a2+b1bで2callなら約0.2円)+再生成0.07円/call(flag率15%、E2E実測)=**約0.2〜0.25円/記事**。②: +0.03円/記事。合計約0.25円(70円目標の約0.35%)。C-Solは実施しない(OF-D5-11)。

## 6. test影響・撤去対象(OF-D5-13、Grep済み)
Grep対象: `_PERSON_DEPENDENT_TO_GENERIC`・`generalize_person_dependent_reference`・`CANONICALIZATION_JSON_SCHEMA_FULLTEXT`・fulltext template path。該当test: `er003_test_key_words_canonicalization.py`・`er003_test_kp_fulltext_wiring_01.py`・`er064_kp_idiom_trial_01_test_01.py`・`er064_kp_opt_01_upstream_test_01.py`・`er112_kp_gm_trial_01_test_01.py`。
- `my`/`our`にsomeone's追加をDEVで再現して実行: `er003_test_key_words_canonicalization.py`+`er112_kp_gm_trial_01_test_01.py` は **77 passed(変更前後で同一)**。
- `er064_kp_idiom_trial_01_test_01.py:55-56`は『表: my -> {one's} のみ。someone'sは許可されない』とassertFalseで固定=**採用時に期待値反転が必要**(本環境は`wordfreq`未導入でcollect不可=実行は未確認)。`er003_test_kp_fulltext_wiring_01.py`も同環境要因でcollect不可(未確認)。採用時の配線委任でwordfreq導入環境で実行して確定する。
- 撤去する規則・検査・testは無い(新規追加のみ)。旧規則の残存Grep: 規則3旧例示(`catch their attention`->`catch someone's attention`)・規則4旧例示(`pumps its fist`->`pump its fist`)は採用時にtemplate内から置換される(DEV写しに限り置換済み、Production templateは不変=hash一致)。

## 7. 採用段階でユーザー判断が必要になる事項(Trial実施自体は継続承認の範囲内)
(1) 記事あたり+1回のLLM call(検査)と約0.2円/記事の追加費用を許容するか。 (2) canonicalization規則3の追記・例示変更とschema欄追加(承認済みPromptの変更)。 (3) 許可表`my`/`our`へのsomeone's追加(承認済み仕様ER-011-NO18の表の拡張)。 (4) 検査call失敗時のfail-open、再生成失敗時のattempt 1採用(WARN記録、STOPなし)という安全方針、および事前宣言の判定基準値(新規悪化・recall・費用)。 (5) 既存完成記事の扱い(KP stage再実行で見出し語・gloss・Adv・TTS[Store reuse]が変わりうる=自動では再生成しない方針の確認)。
