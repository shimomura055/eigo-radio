FABLE-DELEGATION-MARKER: ASR-PASS-CONDITION-AUDIT-委任_01-20261022

# 委任(FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01 委任_01: Family X/Z 正式Production経路のASR PASS条件について「承認済み正式仕様」と「実装」の対応表を作り、不一致箇所を特定する。**本委任は調査・対応表作成まで**。コード修正は行わない(修正可否=ケース1/2の判定はFableが本報告を受けて行う)。API 0・有料run禁止)

## 0. 並列実行の注意
別のsonnet-workerが同時に「多語同音救済 計画Fix(PNMH 委任_03)」を実行中で、`docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/`・OPEN-439行・#137・DECISION_LOGへ書く。共有ファイル(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/REPORT_LEDGER.md`)を編集する前に必ず `git status` → 対象箇所を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`があれば30秒待って再試行。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET_*.md`は一時ファイル(gitignore、force-add禁止)。pushは `git push origin HEAD:main`(localブランチ `work/post-merge-01`)。commit前に `.venv\Scripts\python.exe tools/secret_scan_01.py --staged` hits=0。作業treeには他agentや過去runの未commit差分(多数の`er0XX_output/*`)があるので、コード行番号・Ledger状態は `git show HEAD:<path>` 基準で確認し、他人の差分をcommitに混ぜない。

## 1. 背景(ユーザー原文、2026-10-22。§3・§4・§5・§6Bの逐語)
---
### 3. B：既存ASR PASS条件の仕様確認

今回、CURRENT_SPECと実装の不一致が報告された。

- CURRENT_SPEC：Secondaryも一致した場合のみ同音救済PASS
- 実装：Primary単独で同音救済PASS

しかし、**どのFamily・パーツに影響するのか確認されないまま、ユーザー判断事項として報告されたこと自体が不適切**。

まず現行仕様と承認履歴を確認すること。

**ユーザーが認識している正式仕様は、Family X/Z共通で以下。**

| 対象 | PASS条件 |
|---|---|
| Key Phrase | Primary・Secondaryの両方がPASS |
| Key Phrase以外 | PrimaryがPASSすればよい |

上記は、同音救済を含めた最終PASS判定に関するユーザー認識である。

ただし、ASRの実行順序、Primary PASS時のSecondary呼出要否、既存の例外・fallback等については、承認済み仕様を正確に確認すること。

**判断・対応分岐：**

**ケース1：承認済み正式仕様が上表と異なる場合**

- 修正せずSTOP。
- 相違するFamily・パーツ・条件・承認履歴を特定し、ユーザーへ報告。
- ユーザー承認なく仕様を変更しない。

**ケース2：承認済み正式仕様が上表どおりの場合**

- 実装との差異は仕様変更案件ではなく、不具合として扱う。
- ユーザーへの追加承認を求めず、原因究明→修正→検証まで自律的に進める。
- 問題がない経路は変更しない。

### 4. 調査・是正の範囲

Family X/Zの正式Production経路について、以下を確認する。

- Key Phraseの英語音声と、関連する必要な判定経路
- Key Phrase以外の英語音声
- 通常のASR一致判定
- 同音救済判定
- Primary／Secondary間の判定順序・拒否条件
- retry／fallback／regeneration／resume
- Family固有の設定・例外
- DEV／Trial専用経路との違い

最初に**Family × パーツ × 判定経路**の対応表を作り、どこに不一致が存在するか明確にすること。

特に、#136で検討中のKey Phrase限定Azure拒否権との関係を確認する。

既存の承認済み動作を回復する不具合修正と、#136で未承認の新仕様採用を混同しない。

修正する場合は、以下を満たすこと。

1. 正式初回Production経路で仕様どおりPASS/NGになる。
2. retry／fallback／regeneration／resumeでも判定条件が一貫する。
3. Family X/Z双方で必要なRegression・Validator・integration testがPASSする。
4. 必要な正式runtime evidenceを取得する。
5. 使用したactual model_id、routing、判定結果を記録する。
6. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSを整合させる。
7. 必要なGit commit・pushを完了する。
8. 全Gateを満たした経路のみPRODUCTION_WIREDと判定する。

コード修正・unit testのみではProduction是正完了と報告しないこと。

既存の承認・予算・安全STOP条件は遵守し、無関係な有料TrialやProduction生成は行わない。runtime証拠が取得できない場合は未確認事項として残すこと。

---

### 5. PM・QCD原則

**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- Aの計画FixとBの調査・是正は独立して並列実施する。
- Bの修正をASR比較Trialの完了まで不合理に待たせない。
- 既存仕様内の技術的問題は自律的に解決する。
- 見込みのない反復や不要な日付分割を避ける。
- 既存の仕組みを再利用し、最小限の変更で解決する。
- Family X/Z共通仕様の配線漏れを残さない。
- 量産時の追加費用を最小化する。
- 新仕様や品質基準の変更はユーザーの明示承認なしに行わない。

### 6. 最終報告
(略)
**B：既存ASR PASS条件**

- Family X/Zそれぞれの正式仕様
- Key Phrase／それ以外のPASS条件
- 仕様と実装の不一致があった具体的な箇所
- 修正した内容と対象範囲
- Production実経路での検証結果
- 残る不具合・未確認事項
- SSOT／Git反映結果

**重要：Bについて、正式仕様がユーザー認識どおりであれば、単に「不一致が見つかりました」と報告して終了しないこと。**

承認済みの範囲内で修正・検証まで進め、原則として是正完了結果を報告すること。

ただし、仕様の食い違い、承認範囲外の変更、重大な品質問題、予算・安全STOP条件に該当した場合は、その時点でSTOPして報告する。
---
ユーザー原文の**全文**(§1〜§6、上記に加えAの§2と§6Aを含む)は、Fableが別途提供する次のテキストを `docs/pm/delegation_log/2026-10-22_PNMH-PLAN-FIX-AND-ASR-PASS-CONDITION-AUDIT-01_USER.md` へ逐語保存すること(本委任末尾の【USER原文全文】を使う。文字数とsha256[本文のみ]を記録)。

## 2. Fableが既に確認した事実(鵜呑みにせず再照合すること。これらが「ケース1の可能性」を示している)
- `CURRENT_SPEC.md:2813-2838` 統一ASR判定仕様(AUW、2026-10-15ユーザー正式決定、2026-10-16ユーザー正式承認で`PRODUCTION_WIRED`)。L2818「基本フロー(全Section共通)… **Primary PASSならSecondary不要(最終ANDゲートのみ)**」。L2819「最終ANDゲート=採用転写すべてに値ガードDIFF・否定差が無いことの再確認」。L2827「Section固有の既存例外(維持。新規例外は追加していない)」の(1)Key Phrase英語phrase=4回構成(MINIMAL 2+ENGLISH_LOCK 2)のみで、KPについて「Primary・Secondary両方PASS」の記載は見当たらない。L2820/2828: `force_secondary=True`は`_run_a2_minimal_fallback_attempt`経由(2026-08-26承認のminimal fallback Secondary必須化)のみ、拡大なし(U2)。
- `CURRENT_SPEC.md:1839` 英語homophone `HOMOPHONE_EQUIVALENT`: 「Secondary(または2回目のASR)側の結果が(a)canonical文字一致または(b)ARPAbet完全一致を満たした場合のみPASS」(ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15、2026-08-28)。
- 実装: `er006_secondary_asr_01.py:937-951`付近でPrimary単独のcmu_alternate PASS(commit 2b40165dc、2026-08-28以降)。`er078_asr_unified_judge_01.py:436-441` Primary PASS→即PASS。`er078_asr_unified_judge_01.py` `force_secondary`= primary.passed AND secondary.accepted(minimal fallback経路)。KP経路=`generate_key_phrase_component_verified`(`er003_v1_repro01_main_generate.py:810-830`付近)、Z=`er063_family_z_audio_01.py`。
- 関連既存Trial(いずれも新仕様扱いで未採用): `FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01`(KP Primary+Secondary両方PASS方式のTrial、VALIDATED n=1)、`ASR-THREE-WAY-COMPARISON-TRIAL-01`(OPEN-438/UDR #136、KP限定Azure拒否権C1dK/C5K=未承認の新仕様)。
- MDJF是正記録 `CURRENT_SPEC.md:452-454`(Primary単独PASSを前提に書かれている)。
- 先行調査: `docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/BYUS_EQUIVALENCE_INVESTIGATION_01.md`、`docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/INVESTIGATION_01.md`のR-10節(1839 vs コードの不一致、「置換した後続決定なし」)。

## 3. 作業内容(調査のみ)
1. **承認履歴の確認**: `DECISION_LOG.md`/`DECISION_LOG_HISTORY.md`/`CURRENT_SPEC.md`/`docs/pm/delegation_log/*_USER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`をGrep(全文読込禁止)し、次を特定: (a)「Key PhraseはPrimary・Secondary両方PASS」をユーザーが承認した記録の有無(あれば逐語・日付・管理ID、無ければ「見当たらない」と範囲を明記)。(b)「Primary PASSならSecondary不要」の承認記録(AUW 2026-10-15/16ほか)。(c)1839(homophoneはSecondary確認必須)の承認記録と、それを置換・緩和した後続決定の有無(2b40165dcのcommit message・当時のREPORT `ER-008-*`を含む)。(d)KP英語phraseに関する承認済み例外(ER-010-NO9…-22、disfluency QA、4回構成、K2 Store再利用時の判定継承)。(e)minimal fallback Secondary必須化(2026-08-26)の承認記録と適用範囲。(f)Family Z固有の承認(er063、Dialogue/narrator/KP)。
2. **実装の確認(HEAD基準)**: Family X(A2/B1 Std/Adv)・Family Zの正式Production経路について、パーツ(KP英語phrase/KP英語解説/本文narration・full_story・in_one_line・見出し・短文/Dialogue/JA各種[JAは参考程度に列挙、英語が主])ごとに、呼出関数→judge入口→Primary判定(通常一致・homophone救済・CS/F1・M1・Case A)→Secondary呼出条件(NG時/force_secondary/cache)→最終判定(PASS/PASS_WITH_WARNING/NG_*)→retry/fallback/regeneration/resume/Store再利用時の再判定(`rejudge_with_current_judge`/`guard_entry`/K2 Store)を辿る。DEV/Trial専用経路(er088/er091/er092等)との違いを1行で。
3. **対応表**: `Family × パーツ × 判定経路` の表を作り、各行に「承認済み正式仕様(出典行)」「実装(ファイル:行)」「ユーザー認識表との一致/不一致」「仕様と実装の一致/不一致」「影響(どの条件で結果が変わるか)」を記入。特に次の4点を明示: (i)KPで「Primary PASS・Secondary未呼出」でPASSする経路の有無と出典、(ii)非KPでhomophone救済がPrimary単独でPASSする経路と、1839との関係、(iii)minimal fallback経路のforce_secondaryがKP/非KPのどこに効くか、(iv)#136のKP限定Azure拒否権(C1dK/C5K)が「承認済み動作の回復」なのか「新仕様」なのか(根拠付き)。
4. **ケース判定の材料**: ユーザー認識表(KP=両方PASS/非KP=Primaryのみ)と承認済み正式仕様を行ごとに照合し、「ケース1(仕様が表と異なる)」「ケース2(表どおり・実装不具合)」「一致(問題なし)」を行ごとに分類する。**判定の確定・修正着手はFable**。あなたは分類案と根拠を出す。曖昧な場合は両論を並記し、決め手となる出典を示す。
5. 費用0の範囲で、保存済み転写(`er019_output/.../tts_generation_results.json`等のattempts_log)から「KPでPrimary PASS・Secondary未呼出」「homophone救済でPrimary単独PASS」の実例件数を数える(既存のオフライン集計 `docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/OFFLINE_C5K_TRIGGER_RATE_01.md`[333 KP中28件Primary PASS+Whisper不一致]を再利用し、再計算は不要なら省略)。
6. 成果物: `docs/research/FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01/SPEC_IMPL_MATRIX_01.md`(対応表+承認履歴+分類案+修正する場合の最小変更案と影響範囲[実装はしない]+必要なtest/runtime evidence計画と費用見積[出典付き、未確認は「未確認」])。USER原文保存(上記)。T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01_委任_01.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: ASR-PASS-CONDITION-AUDIT-委任_01-20261022` を含むAgent tool_useの0始まり通番)。`check_delegation_prompt.py`実行(見出し不一致FAILは既知の偽陽性)。
7. SSOT: `OPEN_ITEMS.md`へ新規OPEN(次番号、`POST_USER_VALIDATION`)1行「ASR PASS条件 仕様/実装対応表(調査中、Fable判定待ち)」を追加(DECISION_LOGは本委任では書かない。修正判断後に書く)。`docs/pm/REPORT_LEDGER.md`に行追加。
8. commit(対象ファイルのみ明示add)→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭へ固定ヘッダ追記、`docs/pm/RESULT_PACKET_APCA1.md`へ報告。

## 4. 禁止・境界
- コード修正禁止(本委任は調査)。Production生成・有料API禁止。費用JPY0。
- 仕様の解釈を広げない。「ユーザー認識」と「承認済み正式仕様」を混同しない。#136の新仕様を「不具合修正」と呼ばない。
- A側(PNMH)の文書・OPEN-439・#137に触れない。

## 5. 報告(RESULT_PACKET_APCA1.md)
1) 対応表の要約(Family X/Z × KP/非KP の正式仕様とPASS条件、出典) 2) 承認履歴の確認結果(a)〜(f)(逐語+出典、無ければ「見当たらない」) 3) 仕様と実装の不一致箇所(ファイル:行、条件、影響) 4) ユーザー認識表との照合: 行ごとのケース1/ケース2/一致の分類案と決め手 5) #136との関係 6) 修正する場合の最小変更案・影響範囲・test/runtime evidence計画・費用見積(出典付き) 7) 保存転写からの実例件数 8) 残る未確認事項 9) SSOT/Git反映(commit hash、raw URL) 10) RESULT_PACKET 4行+費用JPY0+使用モデル名。

【USER原文全文】(以下を逐語で `docs/pm/delegation_log/2026-10-22_PNMH-PLAN-FIX-AND-ASR-PASS-CONDITION-AUDIT-01_USER.md` へ保存。先頭にメタ行[受領日2026-10-22、受領者Fable、管理ID 2件]を付けてよいが本文は改変しない)
# Claude Codeへの指示
## 多語同音救済計画Fix＋Family X/ZのASR PASS条件調査・是正

### 1. 目的と今回の承認範囲

以下2件を並行して進める。

- **A：多語同音救済（ByUs問題）** — ユーザー判断を反映した計画Fix。ASR選定後のTrialに備える。
- **B：既存ASR PASS条件の仕様・実装不一致** — 正式仕様を確認し、既存仕様に対する実装不具合なら自律的に修正・検証・完了させる。

Aは新仕様の検証計画、Bは既存仕様の遵守確認・不具合是正であり、承認境界を混同しないこと。

---

### 2. A：多語同音救済計画のFix

改善計画v2の基本方針を承認する。

**品質判断：**

- `ByUs` ⇔ `buy us` / `by us` のように、発音が同じなら単語数・綴り・辞書上のストレス記号の違いによってNGにしない。
- ストレス記号を無視した音素列比較をTrial計画に採用する。
- ただし、音素が異なる実際の誤発音はNG。
- 既存の誤PASS防止条件を維持する。
- `Bi-us`型については、現行仕様に従いNGを維持する。
- 対象は原則全語とし、固有名詞らしい語は代表発音限定など、v2の安全条件を維持する。

**#133との関係：**

- 固有名詞の正しい発音供給については、辞書外・未解決の実際の不一致が発生した場合に調査する方式を継続検討する。
- 全固有名詞を毎回調査する高コスト方式は採用しない。
- CMU辞書に同綴りの別人名があることだけで、対象ブランドの公式発音が確定したと判断しない。
- #133の既存ユーザー判断Statusを維持し、未承認事項を正式採用しない。

**Trial：**

- 現在進行中のOpenAI／Azure／ローカルWhisper精度比較の結果を待つ。
- 新Primary／Secondary確定後にTrialを実施する計画とする。
- Trial費用上限案は50円。
- 現時点ではTrial実行・Production採用・配線は行わない。
- 無料の準備・テストケース整備・計画更新は先行可能。

計画v2へ上記判断を反映してFixし、残る未決事項を明示する。

---

### 3. B：既存ASR PASS条件の仕様確認

今回、CURRENT_SPECと実装の不一致が報告された。

- CURRENT_SPEC：Secondaryも一致した場合のみ同音救済PASS
- 実装：Primary単独で同音救済PASS

しかし、**どのFamily・パーツに影響するのか確認されないまま、ユーザー判断事項として報告されたこと自体が不適切**。

まず現行仕様と承認履歴を確認すること。

**ユーザーが認識している正式仕様は、Family X/Z共通で以下。**

| 対象 | PASS条件 |
|---|---|
| Key Phrase | Primary・Secondaryの両方がPASS |
| Key Phrase以外 | PrimaryがPASSすればよい |

上記は、同音救済を含めた最終PASS判定に関するユーザー認識である。

ただし、ASRの実行順序、Primary PASS時のSecondary呼出要否、既存の例外・fallback等については、承認済み仕様を正確に確認すること。

**判断・対応分岐：**

**ケース1：承認済み正式仕様が上表と異なる場合**

- 修正せずSTOP。
- 相違するFamily・パーツ・条件・承認履歴を特定し、ユーザーへ報告。
- ユーザー承認なく仕様を変更しない。

**ケース2：承認済み正式仕様が上表どおりの場合**

- 実装との差異は仕様変更案件ではなく、不具合として扱う。
- ユーザーへの追加承認を求めず、原因究明→修正→検証まで自律的に進める。
- 問題がない経路は変更しない。

### 4. 調査・是正の範囲

Family X/Zの正式Production経路について、以下を確認する。

- Key Phraseの英語音声と、関連する必要な判定経路
- Key Phrase以外の英語音声
- 通常のASR一致判定
- 同音救済判定
- Primary／Secondary間の判定順序・拒否条件
- retry／fallback／regeneration／resume
- Family固有の設定・例外
- DEV／Trial専用経路との違い

最初に**Family × パーツ × 判定経路**の対応表を作り、どこに不一致が存在するか明確にすること。

特に、#136で検討中のKey Phrase限定Azure拒否権との関係を確認する。

既存の承認済み動作を回復する不具合修正と、#136で未承認の新仕様採用を混同しない。

修正する場合は、以下を満たすこと。

1. 正式初回Production経路で仕様どおりPASS/NGになる。
2. retry／fallback／regeneration／resumeでも判定条件が一貫する。
3. Family X/Z双方で必要なRegression・Validator・integration testがPASSする。
4. 必要な正式runtime evidenceを取得する。
5. 使用したactual model_id、routing、判定結果を記録する。
6. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSを整合させる。
7. 必要なGit commit・pushを完了する。
8. 全Gateを満たした経路のみPRODUCTION_WIREDと判定する。

コード修正・unit testのみではProduction是正完了と報告しないこと。

既存の承認・予算・安全STOP条件は遵守し、無関係な有料TrialやProduction生成は行わない。runtime証拠が取得できない場合は未確認事項として残すこと。

---

### 5. PM・QCD原則

**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- Aの計画FixとBの調査・是正は独立して並列実施する。
- Bの修正をASR比較Trialの完了まで不合理に待たせない。
- 既存仕様内の技術的問題は自律的に解決する。
- 見込みのない反復や不要な日付分割を避ける。
- 既存の仕組みを再利用し、最小限の変更で解決する。
- Family X/Z共通仕様の配線漏れを残さない。
- 量産時の追加費用を最小化する。
- 新仕様や品質基準の変更はユーザーの明示承認なしに行わない。

### 6. 最終報告

技術説明より、ユーザーが現状と必要な判断を理解できることを優先する。

**A：多語同音救済**

- 計画Fix結果とStatus
- 反映したユーザー判断
- ASR選定後のTrial実行条件・費用
- 残る未決事項

**B：既存ASR PASS条件**

- Family X/Zそれぞれの正式仕様
- Key Phrase／それ以外のPASS条件
- 仕様と実装の不一致があった具体的な箇所
- 修正した内容と対象範囲
- Production実経路での検証結果
- 残る不具合・未確認事項
- SSOT／Git反映結果

**重要：Bについて、正式仕様がユーザー認識どおりであれば、単に「不一致が見つかりました」と報告して終了しないこと。**

承認済みの範囲内で修正・検証まで進め、原則として是正完了結果を報告すること。

ただし、仕様の食い違い、承認範囲外の変更、重大な品質問題、予算・安全STOP条件に該当した場合は、その時点でSTOPして報告する。