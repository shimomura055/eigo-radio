FABLE-DELEGATION-MARKER: PNMH-CLOSEOUT-F1-委任_08-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_08 [F-1]: ユーザー回答(多語同音救済 受入・追加提案3件の回答・PM運用是正)の記録。API 0・JPY0・コード無変更。※警告ラベル(①)の実装とOPEN-439最終CloseoutはKey Phrase両方PASS配線(D-2、`er006_secondary_asr_01.py`編集中)完了後のF-2で行う)

## 0. 運用ルール・並列注意
他agent稼働中: (D-2)`er078_*`/`er006_secondary_asr_01.py`/`er003_*`/`er019_family_x_kp_en_k2_store_01.py`/`er063_*`/CURRENT_SPEC ASR節、(C-2)`er019_family_x_entertainment_production_runner_01.py`/`er053_*`/`er095_*`、(E-1)`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/`/`er097_*`。あなたはSSOT行・`docs/pm/PM_GOVERNANCE.md`・PNMH docs・memoryのみ。Production .py編集禁止。共有ファイル(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/PM_GOVERNANCE.md`)編集前に `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。secret_scan `--staged` hits=0。push=`git push origin HEAD:main`。一時ファイルはforce-add禁止。SSOT全文読込禁止。

## 1. ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_PNMH-CLOSEOUT-AND-PM-DECISION-REDUCTION_USER.md`へ本文無改変で保存、文字数・sha256記録)
---
# Claude Codeへの回答・指示
## 多語同音救済のCloseout＋不要なユーザー判断の削減

### 1. 多語同音救済のProduction実装

Family X/ZともにFable判定 `PRODUCTION_WIRED` を受領。

- 両Familyの正式Production経路への配線を確認済み。
- 新規誤PASS 0件、既存PASS→NG 0件。
- 量産APIコスト増0円。
- 今回の実装結果を受け入れる。

残っているSSOT最終反映を完了し、両Familyの配線・検証結果・Statusを整合させてCloseoutすること。

**既に完了した検証を不必要に繰り返さないこと。**

### 2. 追加提案3件への正式回答

**① 同音救済PASS音声への警告ラベル：承認**

- 内部記録のみとする。
- 人間による試聴義務、Human Reviewへの自動転送、量産停止は追加しない。
- 既存の記録機構を優先利用し、必要最小限の対応とする。
- 警告記録のために追加APIを呼び出さない。

**② 大文字・小文字の組み合わせによる固有名詞判定の拡張：不採用**

- `ByUs` のような表記を特別扱いする新機能は追加しない。
- 今回承認済みの多語同音救済は維持する。
- 不採用判断を記録し、同じ提案を繰り返さない。

**③ 中断後の再判定・不要な再生成への追加対策：対応不要**

- 今回報告されたのは、主にイレギュラーな中断後の再開・再利用に関する潜在的懸念。
- 通常の制作フローで無駄な再生成が発生したという証拠は提示されていない。
- 現段階では追加調査・新規対策・Trialを実施しない。
- 既存の再開・再利用仕様は変更しない。

ただし、将来、実際の品質・費用・Production正常動作への重大な影響が確認された場合は、通常の不具合管理原則に従う。

### 3. PM運用の是正【重要】

今回、実害や重要性が明確でない技術的懸念まで、ユーザー判断事項として報告されていた。

これは改善すること。

今後は以下を徹底する。

1. **問題を発見したら、まず事実・発生条件・影響範囲・QCD影響を確認する。**
2. 既存承認仕様内で解決できる不具合は、Claude/Fable側で自律的に修正・検証する。
3. 実害未確認・影響軽微・対応不要の潜在的懸念を、安易にユーザー判断へ上げない。
4. 新仕様採用・品質基準変更・重大なQCDトレードオフなど、本当にユーザー判断が必要な事項だけを提示する。
5. ユーザー判断が必要な場合は、何が起きており、放置すると何が困るのか、推奨案は何かを平易な言葉で説明する。
6. 管理番号だけで課題を説明せず、必ず具体的な内容を示す。
7. 過去に回答済みの事項を再度ユーザーに質問しない。

ただし、重大な品質・安全問題、承認範囲外の変更、予算・STOP条件に該当する場合の報告義務は維持する。

**不要なユーザー判断を減らすこと自体が、Deliveryを短縮する重要なPM改善である。**

### 4. 引き続き優先して進める作業

**A：Key PhraseのPrimary／Secondary両方PASS条件**

- Family X/Z共通の承認済み仕様に従い、Production配線・検証を完了する。
- 実装・Regression・正式runtime evidence・SSOT/Gitまで確認する。
- 既存承認範囲内の不具合は自律的に是正する。

**B：固有名詞の正しい発音情報の取得**

- 承認済みStage 1をProduction改善まで完了する。
- Stage 2は、公式発音→英語圏での実際の呼ばれ方→合理的な発音推定、という承認済み方針を反映して計画を完成させる。
- 公式発音が確認できない場合の合理的な発音による警告付きPASSを、Trialで検証できるようにする。
- Stage 2のTrial実施・Production採用は、別途ユーザー判断を必要とする。

独立作業は並行化し、不要な待機・日付分割を避けること。

### 5. 報告・完了条件

今回の回答をDECISION_LOG・OPEN_ITEMS等の必要な記録へ反映する。

多語同音救済は、SSOT整合完了後にCloseoutする。

今後の報告は、**結論→実際の問題と影響→完了状況→本当に必要なユーザー判断**の順で簡潔に行う。

未確認の些細な懸念を列挙するのではなく、プロジェクトの品質・完成速度・量産単価に実質的な影響がある事項を優先すること。

**最重要：ユーザーに技術的な問題の仕分けをさせない。Claude/Fable側で調査・判断・自律解決したうえで、ユーザーには重要な経営・品質判断だけを求めること。**
---

## 2. 作業
1. `DECISION_LOG.md`: エントリ1件(原文§1・§2・§3逐語。多語同音救済=ユーザー受入[Fable判定PRODUCTION_WIREDを受領]/①警告ラベル=承認(内部記録のみ、試聴義務・HR転送・停止なし、既存記録機構・追加API 0、実装はF-2)/②camelCase固有名詞拡張=不採用(再提案禁止)/③再判定・再生成追加対策=対応不要(既存仕様維持、重大影響が確認されたら通常の不具合管理)/PM運用是正7項目)。
2. `OPEN_ITEMS.md`: OPEN-439に「ユーザー受入2026-10-22、残=①内部警告記録の実装(F-2、D-2完了後)→Closeout」追記(Statusは`PRODUCTION_WIRED_USER_ACCEPTED_CLOSEOUT_PENDING`)。OPEN-443(再判定経路の許容集合)→`CLOSED_NO_ACTION_USER_DECISION`(再提案禁止、将来の重大影響時のみ)。
3. `docs/pm/USER_DECISION_REGISTER_01.md`: #138に受入+①②③回答を記録。新番号は振らない。
4. `docs/pm/PM_GOVERNANCE.md`: 10-2節(ユーザーへ上げるOpen Itemの8分類)または11節の末尾に「2026-10-22ユーザー是正: 不要なユーザー判断の削減」小節を追加し、原文§3の7項目を逐語で記載、報告順序「結論→実際の問題と影響→完了状況→本当に必要なユーザー判断」(§5)を9節の報告フォーマット補足として追記(既存文言は書換えず追記)。`docs/pm/PM_BRIEF.md`のPM運用メモに1行要約を追加。
5. memory: `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\memory\` に `feedback_user_decision_reduction.md`(内容: 実害・影響範囲・QCD影響を確認してからでないと潜在的懸念をユーザー判断へ上げない/既存仕様内はFable側で自律解決/回答済み事項を再質問しない/管理番号だけで説明しない/報告順序 結論→問題と影響→完了状況→必要な判断。出典=本原文ファイル名)を作成し、`MEMORY.md`索引に1行追加。
6. PNMH `PLAN_SUMMARY_01.md`のScope台帳を更新(①実装待ち、②不採用、③対応不要)。REPORT_LEDGER行追加。
7. T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01_委任_08.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: PNMH-CLOSEOUT-F1-委任_08-20261022` を含むAgent tool_useの0始まり通番、255前後)。
8. commit(対象のみ)→push→到達確認。`docs/pm/RESULT_PACKET_PNMH8.md`へ短い報告(変更ファイル・commit・RESULT_PACKET 4行・JPY0)。