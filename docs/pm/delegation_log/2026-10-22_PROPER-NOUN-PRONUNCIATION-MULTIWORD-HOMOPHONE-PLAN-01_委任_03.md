FABLE-DELEGATION-MARKER: PNMH-PLAN-FIX-委任_03-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_03: ユーザー判断を反映した計画Fix v3。API 0・有料run禁止・Production/Prompt/Validator無変更)

## 0. 並列実行の注意
別のsonnet-workerが同時に「ASR PASS条件 仕様/実装調査(管理ID案 FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01)」を実行中。共有ファイル(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`)を編集する前に必ず `git status` → 対象箇所を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`があれば30秒待って再試行。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f は禁止。`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET_*.md`は一時ファイル(gitignore、commit不要・force-add禁止)。push は `git push origin HEAD:main`(localブランチ `work/post-merge-01`)。commit前に `.venv\Scripts\python.exe tools/secret_scan_01.py --staged` hits=0 を確認。

## 1. 目的(ユーザー原文§1・§2の逐語を根拠にする)
ユーザーは改善計画v2(commit 31f7a877a、`docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/`)の基本方針を承認し、次の判断を示した。これを計画へ反映して**Fix版(v3)**にし、残る未決事項を明示する。Trial実行・Production採用・配線は行わない。無料の準備(テストケース整備・計画更新・純関数試作のunit test[Trial専用ファイル内])は先行可。

ユーザー原文(2026-10-22、本委任に関係する§1〜§2・§5・§6A。逐語):
---
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

(§3〜§4はB側の指示のため省略。§3冒頭にはBの背景として「今回、CURRENT_SPECと実装の不一致が報告された。CURRENT_SPEC：Secondaryも一致した場合のみ同音救済PASS/実装：Primary単独で同音救済PASS」「どのFamily・パーツに影響するのか確認されないまま、ユーザー判断事項として報告されたこと自体が不適切」とある。)

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
---
(ユーザー原文全文[§3・§4・§6Bを含む]はFableが保持。B側workerが `docs/pm/delegation_log/2026-10-22_PNMH-PLAN-FIX-AND-ASR-PASS-CONDITION-AUDIT-01_USER.md` へ全文を保存する。あなたはそのファイルを**作成しない**(衝突回避)。計画文書からの引用は上記逐語を使い、出典として同ファイル名を参照してよい。)

## 2. 作業内容
1. 既存計画v2の5文書(`INVESTIGATION_01.md`/`DESIGN_OPTIONS_01.md`/`TRIAL_PLAN_01.md`/`REVIEW_QUESTIONS_01.md`/`PLAN_SUMMARY_01.md`)と`TRIAL_CASES_01.json`、`OPEN_ITEMS.md`のOPEN-439行(現在 `PLAN_V2_PENDING_USER_FIX`)、`docs/pm/USER_DECISION_REGISTER_01.md`の#137を読む(SSOT全文読込禁止、Grepで該当箇所のみ)。
2. ユーザー判断を#137の各論点へ対応付ける(Fable事前整理。あなたが原文と照合して確定し、ズレがあれば報告):
   - U2 案A採否(ストレス無視・1語⇔連続2〜3語の音素列連結比較): **採用(Trial計画として)**。「発音が同じなら単語数・綴り・ストレス記号の違いでNGにしない」「音素が異なる実際の誤発音はNG」。
   - `Bi-us`型の合否: **NG維持**(現行仕様CURRENT_SPEC:454と整合、V8ガード維持)。
   - U1 適用範囲: **原則全語+固有名詞らしい語(entity_like)は代表発音限定**、v2の安全条件(G5・V8・隣接spanのみ・辞書外=判定不能・数値/否定ガード先行)維持。
   - U7 有料Trial: **新Primary/Secondary確定後に実施、費用上限案JPY50**。現時点では実行しない。
   - U5 既存の穴(`AI→Eye`/`us→u s`/`am→a m`/`Tse→sea`等): ユーザー原文は「既存の誤PASS防止条件を維持する」とのみ述べ、既存の穴の是正可否には明示回答していない→**未決のまま**(計画は「悪化させない」のみ。是正は別判断事項として残す)。原文の解釈を広げない。
   - #133/L2(発音供給): 「辞書外・未解決の実際の不一致が発生した場合に調査する方式を継続検討」「全固有名詞を毎回調査する高コスト方式は採用しない」「#133の既存Statusを維持し未承認事項を正式採用しない」→ L2縮小案(反応的調査)を**継続検討の候補**として記載、採用ではない。#133のStatusは変更しない。
   - J7(日本語公式読み「バイアス」を根拠にしてよいか)/byUs発音確定: 「CMU辞書に同綴りの別人名があることだけで公式発音が確定したと判断しない」→ byUsの英語発音は**未確定のまま**と明記。現行の`Bias`救済がCMU `byus`(姓)綴り依存であることを計画のリスク欄へ明記。J7は未決のまま。
   - GitHub Issue #133本文の確認: 未確認のまま(変更なし)。
3. 計画v3への反映: 各文書に「v3 Fix(2026-10-22ユーザー判断反映)」節を追加するか版を上げる(既存v2本文の履歴は消さない)。`PLAN_SUMMARY_01.md`冒頭にStatus=`PLAN_FIXED_WAITING_ASR_SELECTION`(管理ラベル。Trial未実行・Production無変更)と「反映したユーザー判断」「残る未決事項」「Trial実行条件(トリガー=#136に基づく新Primary/Secondary確定のユーザー通知、Cap JPY50、P1=構成音声13本+記事B既存wav約5本の再ASR、見積JPY18〜28)」「ASR確定時に差し替える条件チェックリスト(v2既存)」を1画面で分かるように書く。
4. 無料の先行準備(API 0): (a)`TRIAL_CASES_01.json`にユーザー判断を反映(`Bi-us`=期待NG、`byus→buy us`/`by us`=期待PASS相当、ストレス差のみの組=期待一致、音素相違=NG)。(b)Trial専用の純関数試作 `proto_multiword_span_01.py` に対するunit test(同ディレクトリ内、Production import無し・Production経路無変更)を整備し実行、結果を記録。(c)既存v2のO0再適用結果(4,032ペア、変化4件、PASS→NG 0)はv3でも前提が変わっていないことを確認(再計測は差分がある場合のみ)。
5. SSOT: `OPEN_ITEMS.md` OPEN-439行のStatusを`PLAN_FIXED_WAITING_ASR_SELECTION`へ更新(履歴追記、3,000字超なら`OPEN_ITEMS_HISTORY.md`へ切り出し)。`DECISION_LOG.md`へユーザー判断エントリ1件(逐語引用は上記§2、出典=USERファイル名、管理ID、決定=計画v2基本方針承認+品質判断4点+#133関係3点+Trial条件4点。「Production採用ではない」「新仕様の正式採用ではなくTrial計画の承認」と明記)。`docs/pm/USER_DECISION_REGISTER_01.md` #137を「判断済み(一部)」へ更新し、未決の残項目(U5既存の穴/J7/GitHub Issue #133本文)を別途明示。`docs/pm/REPORT_LEDGER.md`に本委任の行を追加。
6. T-0保存: 本委任文を逐語保存 `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01_委任_03.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: PNMH-PLAN-FIX-委任_03-20261022` を含むAgent tool_useの0始まり通番。保存後に先頭行一致を確認)。`check_delegation_prompt.py`実行(見出し不一致のFAILは既知の偽陽性、結果だけ記録)。
7. commit(対象ファイルのみ明示add)→push→`git log origin/main -1`で到達確認。
8. `docs/pm/ACTIVE_TASK.md`先頭へ固定ヘッダ(PM_BRIEF書式)を追記、`docs/pm/RESULT_PACKET_PNMH3.md`へ報告。

## 3. 禁止・境界
- Production経路(`er006_*`/`er078_*`/`er008_*`/`er003_*`/`er063_*`等)・Prompt・Validator・Ledger・Phrase Listの変更禁止。新flag追加禁止。
- 有料API(TTS/ASR/LLM/Perplexity)呼出禁止。費用JPY0。
- ユーザー判断の範囲を広げない(「承認」と書けるのは原文で承認された事項のみ。VALIDATED≠APPROVED_FOR_PRODUCTION≠PRODUCTION_WIRED)。
- B側の調査・是正に関する文書・SSOT行には触れない。

## 4. 報告(RESULT_PACKET_PNMH3.md、ユーザー§6Aの順)
1) 計画Fix結果とStatus 2) 反映したユーザー判断(#137論点との対応表) 3) ASR選定後のTrial実行条件・費用(トリガー・Cap・見積・手順) 4) 残る未決事項(U5/J7/GitHub Issue #133本文/その他) 5) 無料先行準備の結果(unit test件数・PASS数、ケース表更新) 6) SSOT/Git反映(commit hash、raw URL: PLAN_SUMMARY_01.md/TRIAL_PLAN_01.md/TRIAL_CASES_01.json) 7) RESULT_PACKET 4行((1)既存仕様整合 (2)未承認機能の既定値 (3)成果物 (4)撤去・残置)+費用JPY0の明記+使用モデル名。