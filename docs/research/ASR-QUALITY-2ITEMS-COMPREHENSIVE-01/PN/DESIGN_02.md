# DESIGN_02: 固有名詞の認識・分類の包括対策(Run Entity Table = RET) — Opus条件Aレビュー反映版

管理ID: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-PN 委任_02 / 2026-10-23 / Status: TRIAL_IMPLEMENTED(DEV/Trial専用・Production未配線・承認前・既定OFF相当。VALIDATEDの自己宣言はしない)
前版=DESIGN_01.md(方向・代替案比較・旧規則の撤去/残置はそのまま有効)。Opus所見=OPUS_REVIEW_01.md(OF-PN2-01〜13、Fable判定「必須修正後にTrial実装可、再設計不要」)。
実装=`er111_pn_entity_table_trial_01.py`(表の構築・位置紐づけ・保存/復元)、`er111_pn_trial_evaluate_01.py`(er103の判定関数の複製+RET差分)、test=`er111_pn_entity_table_trial_01_test_01.py`(40件)。検証=`TRIAL_01/`。

## 1. OF反映差分表(DESIGN_01 → DESIGN_02)

| OF | 区分 | DESIGN_01 | DESIGN_02(反映内容) | 実装の場所 / 固定test |
|---|---|---|---|---|
| OF-PN2-01 | 必須 | 表のtokenを`ledger_surfaces`(語集合)へ渡す想定 | **証拠は実体の出現位置に紐づける**。(i)表が証拠を付けるのは **eligible token(非一般語・カテゴリ規則適合・小文字形なし)と実体内部イニシャルのみ**(文言どおり=`general_in_phrase=False`が既定。一般語tokenを実体内で位置紐づけして付ける変種は ablation として実装・測定し、**採否の差は出なかった**[V1=V2、sc4]ため採用しない) (ii)Primary diffのcanonical句の**全出現**が当該segment textの実体出現範囲(連続する語・大文字一貫)に含まれる場合のみ付与(一部でも範囲外なら付与しない=保守側) (iii)実体がそのsegmentに無ければ証拠なし。**付与はPrimary diff 1句ごと**(`ledger_surfaces`は句ごとに `base ∪ その句のgrant` で渡すので他句へ漏れない) | `EntityTable.occurrences/grant_for_phrase`、`evaluate_alarm_eligibility_pn`のG5ループ / `PositionBindingTest`(7件) |
| OF-PN2-02 | 必須 | G3: 「全tokenが実体表token」なら許容 | **RET-3厳密化**。Secondary spanは (i)当該位置で連続する1実体出現、または**区切り語[and/the/of等の語]なしで隣接する複数実体**(語を含まない句読点[,;]は区切り語としない=解釈。語が挟まる場合は連結しない)とtoken単位で一致(所有格's末尾可) (ii)spanと重なるPrimary diffは全てspanに含まれ、少なくとも1つ含まれる (iii)**合成spanにも`_noun_checks`(類似度≥0.40・ASR長≤2×・数値/否定・一般語)とP-03(Primary側ASR句・Secondary側ASR句が両方とも全token一般語なら不受理)を適用**。er103原本の「rest tokenがASR側に保存されていれば受理」経路は無変更で、RET-3は**従来不受理になる場合のみ**作用(緩めるのは実体span一致時だけ)。G3の複製+drift guard(OF-11) | `EntityTable.entity_run_for_span`、`_ret3_check` / `Ret3Test`(負例: Melos drank, Reicher will, 機能語/数値/否定の巻き込み, P-03, comma連結可/and連結不可) |
| OF-PN2-03 | 必須 | 「2シグナル」=LLM∧大文字一貫性∧決定論大文字出現(実質LLM単独) | **記述を実態に合わせて修正**: confirmed = LLM(call A)∧ **独立裏付け**。独立裏付け = (a)宣言済み(Z Seed key_roles)、または (b)既存の決定論証拠(`proper_noun_evidence`=CMU未収録・ALLCAPS単独・文中大文字[P-02位置規則込み])が eligible token でいずれかのsegmentに成立、または (c)**独立call B(文言・枠組みを変えたprompt、call Aの出力は見せない)が同じ実体を挙げる**。(a)(b)(c)のいずれも無い entry は `weak`(証拠にしない)。call Bは(a)(b)が無いentryがあるときだけ呼ぶ(無ければ1 call)。 | `build_entity_table` / `BuilderTest.test_bertie_needs_second_independent_call`, `test_second_call_not_made_when_independent_support_exists` |
| OF-PN2-04 | 必須 | カテゴリ規則なし | **CMU収録tokenに表証拠を付けてよいカテゴリは person/place/organization/brand_product のみ**。work_title/other_named は CMU未収録(OOV)tokenのみ(=cmu_oov同等)。call Bが同じ語列を work_title/other_named と判定して割れた場合は厳しい側へ(B が**より長いspan**の一部として挙げた場合[歌詞行 "Bertie, why do you bound?"]は存在の一致のみでカテゴリは比較しない=実測で見つけた不具合の修正、ITERATION_LOG参照)。5語超(題名/スローガン/長句)・見出し行そのものは除外。brand_product は SC-3 で別集計。 | `_token_class`, `build_entity_table` / `test_category_rule_work_title_cmu_in_token_not_evidence`, `test_hallucination_and_title_and_heading_dropped`, `test_call_b_longer_span_does_not_change_category` |
| OF-PN2-05 | 必須 | 入力=最終脚本text | 入力は**実際にTTSへ渡るsegment canonical textの和集合**(対象role=`APPLICABLE_ROLES`[FULL_STORY/COMMENT/PREVIEW/TOPIC_INTRO/IN_ONE_LINE]のみ。KP/JA/HEADING除外=呼び側で選別)。`Seg(text=供給後, pre_text=供給前)`で**逐語検証は両textで**行う。引用符向き(’‘“”)・空白はNFC正規化して比較。 | `Seg`, `nq`, `_verbatim_in`, `group_key_and_segments`(audit/tts_generation_results) / `test_verbatim_pre_and_post_supply_and_quotes` |
| OF-PN2-06 | 必須 | 表sha不一致なら表なし | **(i)アラームblockに受理に使ったentry(surface/words/category/grade/eligible/initials)を保存**(`decision.detail["entity_table"]["entries_used"]`)。再判定は`table_from_saved_entries`でそのentryから表を復元し、**当該segment textへの逐語出現(`occurrences`)だけ確認**(表sha一致不要・LLM 0 call) (ii)Local Rewriteは`merge_for_local_rewrite`: 変更segmentのみNER→**和集合**(entryは減らない。NER失敗でも既存entry維持) (iii)再判定経路はLLMを呼ばない(関数にllm引数なし) | `table_from_saved_entries`, `merge_for_local_rewrite` / `SavedEntriesAndLocalRewriteTest` |
| OF-PN2-07 | 必須 | SC-5 parity | SC-5を**実装同値test**として残す(tautologyであることを明記)。**別にSC-5b**: D1の新規受理全件+Stage 2実誤読型(両ASRが同じ別語)を人手adjudicate(意味が変わる受理・一般語誤読受理=0)。SC-2 recallは表が実際に必要な層(CMU収録・非一般語・既存証拠不成立)で層別。SC-4はユニーク(text,名前)単位を併記。SC-9にtoken単位Jaccardと「3回構築の和集合でも非固有名詞への証拠付与0」を追加。 | §3 |
| OF-PN2-08 | 推奨 | — | アラームに**ラベル**を付与(`alarm_labels`: 類似度帯[low/mid/high]・P/S両ASRが同じ別語か・ASR語zipfが3.5〜4.0[一般語境界]付近か)。**試聴優先度用で受理境界は不変**。カテゴリ別閾値は入れない。wordfreq version記録。 | `alarm_labels`, `build_entity_table.meta.wordfreq_version` |
| OF-PN2-09 | 推奨 | — | (i)Z Seed key_rolesを宣言型R2として使用(`declared_from_z_seed`)。**X側の英語出典メタデータ(記事題名・人名)は構造化保存が無く今回は未使用**(X記事題名は見出し行として除外される)。 (ii)R_GENERAL_WORDで止まる person/place を `meta.blocked_general_person_place` に件数記録。 (iii)日本語由来ローマ字名はOOV処理で可、Tokyo/Japan等の一般語は許容(証拠を付けない)。 (iv)小文字始まりブランド(iPhone/eBay)は対象外(大文字一貫性が前提)。 (v)KP/ja_readingはG0除外のまま。 | `declared_from_z_seed`, `blocked_general_person_place` |
| OF-PN2-10 | 推奨 | Std/Adv別call | **Std/Adv統合1call**(和集合1text)。構築は脚本確定直後に並行可。run単位保持は`run_table()`(process内状態、finallyで必ず解除)。 | `run_table` / `test_run_holder_is_cleaned_in_finally` |
| OF-PN2-11 | 推奨 | G3を差分実装 | **er103の判定関数を複製**し、複製元5関数のsha256を`ORIG_SOURCE_SHA256`に固定、変わったらtestが落ちる(drift guard)。`enabled=True`明示・scope未設定。表が空/無ければ原本と**判定・detail・evidenceがバイト一致**(SC-1)。 | `source_hashes`, `evaluate_alarm_eligibility_pn` / `EquivalenceTest` |
| OF-PN2-12 | 情報 | — | LLM NER新証拠源+G3変更は**新仕様候補**(採用はユーザー判断、VALIDATED止まり)。Stage 2 REJECTEDは「発音正否判定方式」で本案と矛盾しない。新規受理の多くは**実誤読がアラーム付き受理になる**=承認済み方針の範囲内(TRIAL_RESULT §6)。P-02は縮小せず残置。HR Lock済み4clipは採用後に再生成。NG_BOTH起点の再評価拡張は先送り。Perplexity 401はOPEN-473で別追跡。 | TRIAL_RESULT_01.md |
| OF-PN2-13 | 情報 | — | 費用0.05〜0.1円/記事セット。モデル比較はSC-3/SC-9達成後(今回は比較せず)。 | TRIAL_RESULT §SC-7 |

実装中に見つけた設計外の補正(いずれもfail-closed側/証拠を増やさない側):
- **裸のイニシャルの復元**(`_merge_initials`): LLMが「L.」と「Mimoun」を別entityに分けた場合に本文の`L. Mimoun`を1実体として復元(裸のイニシャルentityは捨てる)。RET-3の実体spanに必要。
- **call B 一致時のカテゴリ比較は同じ語列のときだけ**(上記OF-04)。
- **隣接実体の連結は語を含まない句読点(,;)を許容**(`Celine, Altuzarra, Toteme`のAzure span跨ぎ2件を救済)。語が挟まる(and/of)場合は不許可。

## 2. 構成(Trial)

```
[Seg 和集合(対象role, 供給後+供給前)]
   ├─(R2) 宣言 declared (Z Seed key_roles)
   ├─(R3) call A (gpt-6-luna, strict JSON schema, Std/Adv統合1call) → 逐語検証[供給前後]→題名/長句/見出し除去→イニシャル復元
   │        → token 判定(_token_class: 小文字形なし∧非一般語∧カテゴリ規則) → eligible token / 内部イニシャル
   │        → 独立裏付け(既存決定論証拠 or 宣言)なし→ call B(別prompt)一致なら confirmed、なければ weak
   ▼
 EntityTable(entries[surface,words,category,grade,eligible,initials,sources,notes], status, meta[usage,dropped,blocked_general...])
   ▼ (判定時)
 evaluate_alarm_eligibility_pn = er103原本の複製 + (a) G5: Primary diff句ごとに grant_for_phrase を `ledger_surfaces` に加算
                                                    + (b) G3: 不受理になる Secondary span のみ RET-3(厳密)で再検査
 → 受理時 detail に entity_table{sha, entries_used, per_diff, ret3} と alarm_labels を保存(OF-06)
```
失敗: LLM例外/timeout/不正出力/空/refusal/幻覚 → status=LLM_UNAVAILABLE等・宣言entryのみ(=現行同等)。例外を投げない。operator report: `operator_report_lines`(「実体表: 未構築または縮退」を明記)。

## 3. 検証基準 SC-1〜SC-10(改訂版)

| ID | 基準 |
|---|---|
| SC-1 同値性 | 表なし/空/無関係表で、D1 HR queue 88(現行Ledger・Ledger全除外の両方)・D2 保存EN pair・既存test全件の判定が er103 原本とバイト一致。drift guard一致。flag未設定でAPI 0・副作用0。 |
| SC-2 検出 | gold出現≥150。表が実際に必要な層(CMU収録・非一般語・既存証拠が成立しない出現)で recall ≥0.90、カテゴリ別 ≥0.85。Bertie型(CMU収録の人名×文頭/引用直後)n≥10で 100%。再構築安定性(Bertie 5回構築の usable 率)を併記。 |
| SC-3 精度 | 証拠付与entry/tokenの非固有名詞率 ≤2%。偽候補(inventing/canceling/fats/roasting/unwanted/farther/muddy/withdrawn、見出し語、Title Case一般語)・題名中の低頻度一般語(petal/crimson等)の証拠化=0。brand_productは別集計。 |
| SC-4 受理(初見語) | Ledger全除外で、B類9件 ≥8受理(Bertie 3/3必須)、C類entity-only 13件 ≥12受理、Melos drank×3は不受理維持、A類41は維持(退行0)、D/E類は不受理維持。ユニーク(text,名前)単位を併記。Ledger leave-one-out(各entry)で依存受理の≥90%を表で維持。 |
| SC-5 実装同値(parity) | 全usable entry×合成ASR変種(≥200)で「表由来判定=同一tokenをLedger登録した判定」が100%一致、表が緩い側に差が出ない。※tautologyであることを明記。 |
| SC-5b 誤PASS adjudication | D1の新規受理全件+Stage 2実誤読型を人手(一次=Sonnet、最終=Fable)でadjudicate。意味が変わる受理=0、一般語誤読の受理=0。D5負例(一般語/数値/否定/脱落/他実体への置換)の受理=0(Primary/Secondaryが同じ別語に揃う現実的な形)。 |
| SC-6 フェイルセーフ | LLM失敗の全注入で例外0・表由来受理0・現行と同一挙動・operator reportに未構築を明記。 |
| SC-7 費用・時間 | NER ≤0.1円/記事セット(実測の平均と最大を併記)、call遅延p50/p95/max。 |
| SC-8 横断 | Z 2作品+X≥6記事で構築・カテゴリ分布・weak/dropped一覧。 |
| SC-9 安定性 | 同一text 3回構築で confirmed entry集合 Jaccard ≥0.90(entry単位とtoken単位を併記)、3回の和集合でも非固有名詞への証拠付与0。 |
| SC-10 継承/LR | 保存entryからの再判定が元の受理と一致(LLM 0 call・表sha不一致でも可)、LRで表が減らない(NER失敗でも維持)。 |

## 4. 将来の配線区分(Trialでは配線しない)

| 部分 | 内容 | 経路 |
|---|---|---|
| RET-2(PNAP証拠源への表の追加、G5) | 新コード経路+単一flag読取関数・既定OFF・DefaultOffIsolation testの11-7限定例外の**対象になり得る**(`ledger_surfaces`へ足すだけ) | ユーザー採用判断後(11-7の5条件を満たす場合のみ限定例外、それ以外はOffline Trial→VALIDATED→ユーザー採用→Production実装) |
| RET-3(G3のSecondary span規則) | 既存G3の**直接変更**(er103の関数本体の編集)となるため11-7限定例外の**対象外の可能性が高い** | VALIDATED→ユーザー正式採用→Production実装 |
| LLM NER(新しい証拠源・新規API call) | 新仕様候補(OF-PN2-12) | 同上(ユーザー判断) |
| 配線点 | `er103_pnap_runner_hooks_01.run_with_alarm_hook`(scope内・fn前に表を構築/読込→run-scoped holder→finallyで解除)。Zは`er063_family_z_audio_01.py:1300`、Xは`@pnap_hooks.family_scope`(er019_family_x_audio_production_runner_01.py:886,1232) | 採用承認後 |
| ②UKUSとの境界 | ②はorthographic variant(綴り差)の救済、①は固有名詞の証拠源。同じ判定関数を触る可能性があるため、配線時は`evaluate_alarm_eligibility`への差分を一本化する。表は読取のみで共有(②は表を変更しない)。Trialでは`er111_pn_*`と`er111_ukus_*`を完全分離。 | 配線時に整合を再確認 |

## 5. 撤去・残置(DESIGN_01 §7を継承)
撤去0・縮小0。P-02/`proper_noun_evidence`/`R_GENERAL_WORD`/G3(原本)/P-03/`val.capitalized_flags`は無変更(残存Grep=TRIAL_RESULT §9)。Trialでの新設はRET(builder/evidence/span/audit)のみ。
