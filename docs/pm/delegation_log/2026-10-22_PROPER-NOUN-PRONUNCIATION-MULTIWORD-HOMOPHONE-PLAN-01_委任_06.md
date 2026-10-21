FABLE-DELEGATION-MARKER: PNMH-PROD-A1-委任_06-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_06 [A-1]: 多語同音救済のProduction実装設計書+未配線module/test先行実装+承認記録。**Production経路への配線(既存ファイルの編集)はまだ行わない**=Opus独立レビュー(11-3条件A/C)後のA-2で行う。API 0・JPY0)

## 0. 運用ルール・並列注意
- 別agent(B-1: 固有名詞発音取得の改善計画策定)が同時に `docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/`(新dir)・`OPEN_ITEMS.md`(新OPEN 1行)・`docs/pm/REPORT_LEDGER.md`へ書く。あなたはそのdirに触れない。共有ファイル(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/REPORT_LEDGER.md`)編集前に `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。
- `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。secret_scan `--staged` hits=0。push=`git push origin HEAD:main`(local `work/post-merge-01`)。一時ファイル(`ACTIVE_TASK.md`/`RESULT_PACKET_*.md`)はforce-add禁止。SSOT全文読込禁止。他人の未commit差分(`er0XX_output/*`)を混ぜない。

## 1. ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_PNMH-PRODUCTION-WIRING-AND-PRONUNCIATION-SUPPLY-PLAN-02_USER.md` へ本文無改変で全文保存し、文字数・sha256[本文のみ]を記録。B-1 agentはこのファイルを作成しない)
---
# Claude Codeへの指示
## 多語同音救済のFamily X/Z正式Production配線＋固有名詞発音取得の改善計画策定

### 1. 目的・承認範囲

以下2件を**並行して進める**。

**A：多語同音救済のProduction実装・検証**

- Status：`APPROVED_FOR_PRODUCTION`
- TrialはVALIDATED、ユーザーが正式採用を承認済み。
- Family X/Z双方の正式Production経路へ配線し、必要な検証・記録まで完了させる。
- `PRODUCTION_WIRED`まで到達することを目標とする。

**B：固有名詞の正しい発音情報を必要時のみ取得する仕組み**

- Status：計画策定段階
- Claudeが改善計画を作成し、Fable独立レビューを受けてユーザーへ提出する。
- Trial実行・Production採用・実装は未承認。

**AのProduction実装とBの計画策定を混同しないこと。**

---

### 2. A：多語同音救済の正式Production実装

承認済み仕様：

- `ByUs` ⇔ `buy us` / `by us` のように、発音が同じなら1語⇔複数語の表記差を救済する。
- 辞書上のストレス記号の差だけでNGにしない。
- 実際に音素が異なる誤発音はNG。
- 隣接する語句だけを比較し、離れた語を恣意的に結合しない。
- 固有名詞らしい語の代表発音限定、短い語・機能語の制限、数値・否定の保護など、VALIDATEDとなったTrial v3の安全条件を維持する。
- `Bi-us`型の誤発音は現行仕様どおりNGとする。
- 既存の1語⇔1語同音救済を壊さない。

**Trialで検証済みの方式を採用し、未承認の機能拡張や品質基準変更を加えないこと。**

#### Family X/Zへの配線

最重要条件は、**両FamilyでProduction配線漏れを起こさないこと**。

- Family Xの正式初回Production経路
- Family Zの正式初回Production経路
- retry／fallback／regeneration／resume
- Key Phraseおよびそれ以外の対象パーツ
- 共通ValidatorとFamily固有の呼出経路

以上を確認し、実際に多語同音救済が発火することを検証する。

共通関数を修正しただけで、両Familyへの配線が完了したと判断しない。

#### 既存ASR PASS条件との整合

現在進行中の「Key PhraseのPrimary／Secondary両方PASS条件」の是正と整合させる。

ユーザー認識：

| 対象 | 合格条件 |
|---|---|
| Family X/ZのKey Phrase | Primary・Secondary両方PASS |
| Family X/Zのそれ以外 | PrimaryがPASSすればよい |

既存の承認済み正式仕様・修正状況を確認し、両作業が同じ判定関数群に関わる場合は、可能な限り実装・レビュー・Regression・runtime確認をまとめる。

ただし、両ASR合格条件について承認済み仕様に食い違いがある場合は、勝手に仕様を変更しない。

#### 必須検証

- Trial v3の正例・負例・Regressionの再実行
- 保存転写4,032ペアの再適用
- 既存PASS→NGの発生有無
- 新規誤PASSの発生有無
- `Bi-us`型の実音声負例を1本追加し、正しくNGになることを確認
- Family X/Zそれぞれの正式経路での発火証拠
- Key Phraseとそれ以外のPASS条件の維持
- retry／fallback／regeneration／resumeとの整合
- 実行model_id、routing、Validator判定の記録
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新
- 必要なGit commit・push

`Bi-us`の実音声検証では、負例として意図した発音が実際に生成されていることを確認する。生成に失敗した音声を負例PASSの証拠にしない。

**Family X/Zそれぞれで必須Gateを満たして初めて`PRODUCTION_WIRED`とする。**

一方のみ完了した場合は、他方を未完了として明示し、解消まで追跡する。

---

### 3. B：固有名詞の発音取得方式の改善計画

#### 背景

当初の改善目的は以下2つをセットで解決することだった。

1. 1語⇔複数語の同音判定を可能にする。
2. 比較対象となる固有名詞の正しい発音情報を取得できるようにする。

1はTrial成功・正式採用済み。

2は前回の計画で切り離されたが、**改善対象から取り除くことはユーザーの意図ではない**。

今回、2の具体的な改善計画を策定する。

#### 設計方針

**必要な場合だけ発音を調査・登録・再利用する低コスト方式**を基本とする。

検討項目：

1. 既存Ledger・CMU辞書・発音取得機構の調査と再利用。
2. 発音情報が不足している固有名詞を検出する方法。
3. 調査が必要な条件と不要な条件の定義。
4. 公式情報・信頼できる辞書・公式音声等の調査優先順位。
5. 複数の発音候補がある場合の扱い。
6. 正しい発音をIPA・音素列等へ変換する方法。
7. Ledgerへの登録、情報源・信頼度の管理。
8. 登録済み情報のキャッシュ・再利用。
9. 発音情報が取得できない場合の自律的な解決方法。
10. 既存の同音判定Validator・ASR Cascadeとの統合方法。
11. Family X/Zおよび将来のFamily Yへの共通適用。
12. 誤PASS・過剰NG・量産費用への影響。

特に、`ByUs`のように、辞書に同じ綴りの別人名が存在しても、それだけでブランドの公式発音を確定できない問題を解決すること。

AIによる推測のみで発音を確定しない。

#### 検討すべき重要な観点

- すべての固有名詞を事前に検索する方式は避ける。
- 既存辞書で確実に解決できる場合は余計な調査をしない。
- 辞書未収録でも、必ずしも毎回Web検索する必要があるとは限らない。
- 過去に検証済みの発音情報を最大限再利用する。
- 不確実な発音を自動登録して、以降の量産で誤PASSを繰り返すリスクを防ぐ。
- Human Reviewは最後の手段とし、自律的に解決できる問題はAI側で処理する。
- 追加費用が必要な場合は発生頻度を踏まえ、1記事セット当たりの期待原価で評価する。
- 量産単価70円／記事セットの目標を踏まえる。

この設計方針より優れた方法があれば、Claudeから積極的に提案すること。

#### Fable独立レビュー

Claudeの設計案に対してFableが独立レビューを行う。

評価観点：

- 正しい発音情報を取得できるか
- 誤った発音を確定・登録するリスク
- 不要なWeb検索やLLM呼出の有無
- 既存機構との重複
- 同音判定拡張との整合
- 未知の固有名詞への対応力
- 再利用・キャッシュの有効性
- Failure時の適切な自律対応
- Family X/Z共通適用
- QCDと実装複雑性
- より単純・安全・低コストな代替案

レビューで見つかった問題は計画に反映する。必要十分な計画となった時点で完成とし、過剰な再レビューは行わない。

#### 今回の到達点

- 改善方式の比較と推奨案
- 既存機構との具体的な統合設計
- Trial方法・合格基準
- 品質リスクと対策
- 開発費・量産単価への影響
- Fableレビュー結果
- 残るユーザー判断事項

**Bは計画提出まで。Trial・Production実装を無断開始しないこと。**

---

### 4. PM管理・再発防止

今回、当初セットで進めるはずだった「発音情報の取得」が途中で改善対象から外れていた。

また、Family X/Z共通仕様の配線漏れも過去に発生している。

同種の抜け漏れを防ぐため、以下を必須とする。

- 当初目的・承認済みScope・現在の作業成果を照合する。
- Scopeを分割する場合でも、残した課題のStatus・担当工程・次の判断点を管理する。
- 共通仕様の変更では、対象Family全体の配線・検証状況を確認する。
- 完了報告前に、未配線・未検証・未報告Trial・未処理判断・SSOT不整合を確認する。
- 未完成項目を完成済みとして報告しない。
- 再発防止自体が過剰な検査や遅延を生まないようにする。

**AのProduction実装とBの計画策定は原則並列で進め、不要な待機・日付分割をしないこと。**

既存承認の予算・STOP条件を遵守し、技術的問題は委任範囲内で自律解決する。

### 5. 最終報告

ユーザーが現状と必要な判断をすぐ理解できるよう、以下を簡潔に報告する。

**A：多語同音救済**

- Family X：Production配線・正式実走の結果
- Family Z：Production配線・正式実走の結果
- Key Phrase両ASR合格条件との整合
- 誤PASS・過剰NG・Regression結果
- `Bi-us`実音声負例の検証結果
- 量産原価への影響
- SSOT・Git反映と最終Status

**B：固有名詞発音取得**

- 推奨する方式と理由
- 具体的に、いつ・どうやって発音情報を調査するか
- 発音の正しさをどう保証するか
- Ledgerへの登録・再利用方法
- 既存の同音救済との連携
- Fable独立レビュー結果
- Trial計画と概算費用
- ユーザー判断が必要な事項

**報告では管理番号だけを使わず、必ず課題の具体的な名称を示すこと。**

Aは両FamilyのProduction完成、Bはレビュー済み改善計画の提出を目標とする。

承認済み仕様・品質・予算・安全条件の範囲内で最大限自律的に進めること。
---

## 2. Fableの前提整理(再照合すること)
- 承認範囲=Trial v3でVALIDATEDになった判定層L1(`proto_multiword_span_01.py` `multiword_span_equivalent_v3`相当: 隣接span・1語⇔連続2〜3語・CMU音素列連結・ストレス無視・entity_like代表発音限定・G5(台本側3字未満除外)・V8(複数語側2字tokenは閉じた機能語集合のみ)・辞書外=判定不能・数値/否定ガード先行)。これ以外の拡張禁止。
- **KP両方PASS条件は未承認のまま**: 承認済み正式仕様=CURRENT_SPEC:2818(Primary PASSならSecondary不要、全Section共通、KP含む)、`SPEC_IMPL_MATRIX_01.md`(OPEN-440)で確認済み。ユーザー原文§2は「食い違いがある場合は勝手に仕様を変更しない」。したがって本実装は**現行承認済み仕様の判定順序のまま**行い、KP両方PASSは実装しない。ただし設計上、将来KPに`force_secondary`等が入っても多語救済がPrimary/Secondary双方の判定で同一に働くよう、Primary判定経路(`er006_preprod_hardening_01_validation.py` 1:1 homophone入口 L750付近)とSecondary判定経路(`er006_secondary_asr_01.py` `_step_alternate_pass` L592付近・受理判定 L993付近)の両方に同じ純関数を使う(Trialのpatch点2箇所に対応)。
- Family X/Zの判定入口は共通関数(`val.classify_asr_match`/`sec._step_alternate_pass`→統一judge `er078_asr_unified_judge_01.py`)だが、**Family X runner(`er003_v1_repro01_main_generate.py`・`er003_v1_crosslevel_audio_02_common.py`等)とFamily Z runner(`er063_family_z_audio_01.py`)からの呼出行を個別に特定**し、KP英語phrase/KP解説/本文/Dialogue/見出し等の各パーツ・retry/fallback(minimal fallback `_run_a2_minimal_fallback_attempt`)/regeneration/resume・Store再利用時再判定(`rejudge_with_current_judge`/`guard_entry`、K2 Store)の全経路が同じ関数を通ることを表で示す。
- Trial証跡: `er093_output/pnmh_trial_01/`、`er093_pnmh_trial_01_core.py`(patch方式)、`TRIAL_RESULT_01.md`、`TRIAL_CASES_01.json`(41件)、`measure_v2_01.py`(4,032ペア)。
- `Bi-us`実音声負例: Trialでは構成に失敗(TTSが`bias`と読んだ)。A-2で取り直す。設計書に「意図した区切り発音が生成されたことの確認方法」(例: 綴り`"Bye-us"`/`"Bi us"`/句読点・休止を使った複数候補を生成し、Primary/Secondary転写とローカル確認で2音節分離を確認してから負例として採用。ASRが`by us`へ正規化した場合は新規則でPASSになりうる=既知の限界として**隠さず報告**し、Fableが判断)を書く。

## 3. 作業(A-1、API 0)
1. 承認記録(SSOT): `DECISION_LOG.md`へ「多語同音救済(L1)`APPROVED_FOR_PRODUCTION`(2026-10-22ユーザー原文§1・§2逐語、出典=USERファイル)」エントリ。`docs/pm/USER_DECISION_REGISTER_01.md` #138→判断済み(採用)。`OPEN_ITEMS.md` OPEN-439→`APPROVED_FOR_PRODUCTION_WIRING_IN_PROGRESS`(PRODUCTION_WIREDではない)。**Scope台帳**をOPEN-439行または`PLAN_SUMMARY_01.md`冒頭に追加(ユーザー§4再発防止): L1判定層=採用・配線中/L2発音取得=計画策定中(B-1、新管理ID PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02)/KP両方PASS=OPEN-440ユーザー回答待ち(未承認)/U5既存の穴=未回答/J7=未回答/GitHub Issue #133本文=未確認、それぞれStatus・担当工程・次の判断点。
2. 実装設計書 `docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/IMPLEMENTATION_DESIGN_01.md`(Opusレビュー用、簡潔): (a)新module `er094_multiword_homophone_01.py`(純関数、Trial v3の`multiword_span_equivalent_v3`を移植。CMU辞書アクセスは既存`er008_asr_variant_hardening_15_homophone_en.py`の手段を再利用、entity_like判定は既存の判定を再利用、機能語集合・G5/V8定数はmodule定数)。(b)配線点2箇所の最小diff案(Primary側 validation L750付近の1:1 homophone入口の直前/直後に「1:1で不一致かつ隣接n:m spanなら新関数」を追加、Secondary側`_step_alternate_pass`の同等箇所)。既存1:1経路は無変更で、n:m一致時の戻り値ラベルは`HOMOPHONE_EQUIVALENT`系の既存ラベル+`multiword=True`等additiveな根拠フィールド。(c)rollback=module定数1つ(`MULTIWORD_HOMOPHONE_ENABLED=True`、env/flagではない。承認済みのため既定ON)。(d)Family×パーツ×経路の配線表(上記2.)。(e)挙動変化4点(NX1数値例外併存/M1矛盾拒否/CS・F1迂回/F1残差1:1限定)の扱いとtest。(f)検証計画: unit(41ケース移植)・4,032ペア再適用(PASS→NG 0/新規誤PASS 0)・golden 193件・`Bi-us`実音声負例の構成手順・X/Z正式経路の発火証拠の取り方(X=記事B `byUs`segmentのProduction関数で再生成1本[`TTS_EXECUTION_MODE=STANDARD`]、Z=Z runnerのProduction関数で`byUs`を含む短い英語segment 1本。いずれもStore/HR Lockを汚さないrun_id・出力dirを使い、既存Production成果物を上書きしない)・費用見積(出典付き、目安JPY30以内)。(g)KP両方PASSとの関係(未承認・不実装、将来の`force_secondary`追加と干渉しない理由)。
3. 先行実装(未配線): `er094_multiword_homophone_01.py`と`er094_multiword_homophone_01_test_01.py`(41ケース+V8/G5/entity_like/辞書外/隣接限定/数値否定ガードの単体)を作成し実行PASS。**Production既存ファイルは編集しない**(`git diff HEAD`でer094以外のProduction .pyが0であることを確認)。
4. T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01_委任_06.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: PNMH-PROD-A1-委任_06-20261022` を含むAgent tool_useの0始まり通番、241前後)。`check_delegation_prompt.py`実行(見出し不一致FAILは既知の偽陽性)。
5. commit(対象のみ)→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ。`docs/pm/RESULT_PACKET_PNMH6.md`へ報告: 設計書要約(配線点・配線表・rollback・検証計画・費用見積)/unit test結果/SSOT・commit/Opusレビューで特に見てほしい論点3〜5個/RESULT_PACKET 4行/JPY0。