FABLE-DELEGATION-MARKER: ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01-委任_03-20261023

# 委任_03: er109 v1 正式採用(APPROVED_FOR_PRODUCTION、X/Zのみ)の **配線設計**(実装前・Opus条件Aレビュー用)

## 0. 先に行うこと(T-0)
1. 本委任文の逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01_委任_03.md`。Nは最新index付近(約306〜316)から先頭行が上記MARKERに一致するものを探し、一致確認を報告に記す。
2. ユーザー指示原文(§1)を `docs/pm/delegation_log/2026-10-23_ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01_USER_02.md` に逐語保存。
3. `check_delegation_prompt.py` で本委任文を検証し結果をRESULT_PACKETへ。
4. `docs/pm/ACTIVE_TASK.md`: **別agent(FAMILY-Z-VOICE-PRODUCTION-WIRING-01)が並行作業中で同ファイルを更新する**。上書きせず、編集直前に再読込し、OPEN-459の「並行タスク」1行だけを自分の状態に更新する(他行は触らない)。

## 1. ユーザー指示原文(2026-10-23、逐語。保存時はこのブロックをそのまま使う)
```
# ASR包括対策 er109 v1 — 正式Production採用・Wiring指示

## 1. ユーザー正式決定

英語ASRの同一発音・異表記包括対策について、以下2項目を正式採用します。

**Status:APPROVED_FOR_PRODUCTION**

**対象Family:X / Zのみ。**

### ① 包括対策 er109 v1 — 正式採用

既存の数値・同音救済を維持し、今回VALIDATEDとなった追加救済範囲をProductionに採用する。

主な対象:

- `one ↔ 1`:既存で救済できていた経路は維持し、Key Phrase等の未対応経路へ拡張。
- `one's ↔ 1's`:新たに救済。
- `twenty percent ↔ 20%`:既存の救済を維持。重複実装しない。
- 短縮形、同音語、数字表記、スペース差など、er109 v1で検証済みの追加対象。

適用範囲は、**Family X/Zの英語ASR全体**とする。Key Phrase限定ではない。

OpenAI Primary、Azure Secondary、Whisper票、本文・Key Phrase・英語解説、Store再利用・retry・fallback・regeneration・resumeを含む正式経路で、承認済みの判定仕様と整合させること。

安全条件:

- 発音が異なる表現を同値にしない。
- 曖昧略語・同形異音語・危険なoronymは、承認済みの非同値判定を維持。
- 強勢・代表発音の判定はOpus是正後のv1を使用。
- 数値差・否定差の最終保護は全面解除せず、er109が同音と証明した箇所のみ解除する。
- 既存の本当の発音NGを誤PASSにしない。

### ② 否定語 `no ↔ know` — 正式採用

`no` と `know` の発音が一致する場合、表記差だけでNGにしない。

- `PASS_WITH_WARNING` として合格。
- 警告内容・根拠を内部記録。
- 事後試聴の対象として追跡可能にする。
- `can't/can`、`don't/do` など発音が異なるものは救済しない。

対象は①と同じく、Family X/Zの英語ASR全体。

決定的な数値・記号等の表記差は警告不要とし、Opusレビュー済みの警告方針を維持する。

## 2. ③ 開発対象Familyの厳守【重要】

**Family A/B/Cは開発停止中であり、今回の対象に含めない。**

この方針はすでに `docs/pm/PM_GOVERNANCE.md` §27-3に記録済み(2026-10-16ユーザー決定)。

Claude・Fableの双方で再確認し、遵守すること。

- A/B/Cの追加開発・コード修正・Trial・検証run・再生成・独立調査は行わない。
- 共通Validatorを使っていることを理由に、適用Familyを拡張しない。
- 共通コード変更で対象外Familyに挙動の変化が生じないよう、互換性と適用範囲を確保する。
- もし既存構造上、対象外Familyへの変更を避けられない場合は、その変更を実施せずSTOPし、理由と代替案を報告する。
- 対象外Familyへの展開を追加提案・ユーザー判断項目として提示しない。

今回のWiringでは、**X/Zだけに有効化できる構成**を必須とする。

既存の記録が不明瞭であればSSOTを補強する。ただし、新しい調査タスクを不要に増やさない。

## 3. Production Wiring

TrialでVALIDATEDとなったer109 v1を、正式Production経路に配線する。

既存コード・承認済み仕様を再利用し、重複実装や不要な再Trialを避ける。

Opus must-fixのうち設計段階に残っている事項も実装・検証する。

特に以下を確認:

1. Family X/Zの正式初回Production経路。
2. Primary/Secondary/Whisper各票の判定。
3. 最終保護Gateとの整合。
4. retry / fallback / regeneration / resume。
5. Store再利用と既存音声の判定。
6. 既存のKey Phrase多数決仕様との整合。
7. 誤PASSの防止、NG→PASSの改善。
8. 警告付きPASSの内部記録・事後試聴対象管理。
9. 対象Family以外でer109が有効化されないこと。

既存のASR判定条件や品質基準を、本承認範囲外で変更しないこと。

## 4. 検証・受入条件

**X/ZそれぞれでPRODUCTION_WIREDまで到達すること。**

必要な証拠:

- 正式Production経路への配線確認。
- X/Zそれぞれのruntime evidence。
- `one's ↔ 1's`、`no ↔ know` 等の新規救済ケースが期待どおり判定される証拠。
- 数値の実際の違い、否定脱落、異音語、同形異音語等が誤PASSしない証拠。
- 必須Regression / Validator / Integration test PASS。
- retry・fallback・Store・resumeでの判定一貫性。
- actual routing、flag、判定basis、警告記録の証拠。
- 既存Production仕様との整合。
- Dangling Referenceなし。
- CURRENT_SPEC / DECISION_LOG / OPEN_ITEMS更新。
- Git commit・push完了。
- Fable独立受入。

自然発火を得るためだけに不必要な記事生成を繰り返さない。正式runtime経路の実行証拠と、該当ケースの決定的な検証を組み合わせ、必要十分な品質で完了させること。

**単なるコード配線や単体テストPASSだけではPRODUCTION_WIREDとしない。**

## 5. QCD・実行方針

優先順位は **品質 > 完了速度 > 量産単価**。

- 承認済みのer109 v1を利用し、探索Trialをやり直さない。
- 独立作業は並列化し、不要な待機・日付分割をしない。
- 追加API費用は最小限に抑える。
- Wiring費用見込み40円以内を基本とする。
- 承認済み範囲内の不具合は、自律的に原因究明・修正・検証する。
- 新しい仕様変更、品質基準変更、重大な安全リスク、承認範囲外の変更が必要な場合のみSTOPして判断を求める。

## 6. 最終報告

①②についてFamily X/Z別に、APPROVED_FOR_PRODUCTIONからPRODUCTION_WIREDへの到達を報告すること。

実装内容の説明だけでなく、正式runtimeの動作証拠、テスト結果、既存仕様との整合、費用、SSOT/Git反映結果を提示する。

未確認事項を完了扱いにしない。

Fableによる独立受入まで完了し、残件がある場合はOPEN_ITEMSに明示する。

**今回の正式採用について、ユーザーへの再承認要求は不要。Production Wiring完了まで自律的に進めてください。**
```

## 2. 背景(Fable確認済み)
- 既存成果: `er109_asr_orthographic_equivalence_01.py`(v1、未配線・既定OFF、`ORTHOGRAPHIC_EQUIVALENCE_ENABLED=False`/`is_enabled()`)、`docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/{DESIGN_PROPOSAL_01,DESIGN_ADDENDUM_02,VALIDATION_02,OPUS_REVIEW_MANDATORY_01}.md`、OPEN-459、OF-AHO-P-01〜12(`docs/pm/OPUS_FINDINGS_LEDGER.md`)。設計済み・未実装のOpus must-fix=最終保護GateのSpan単位解除(P-06)、HR Lock済みentryの明示再判定手順、隔離条件(旧 既定OFF前提)。
- B不具合3件は既にProduction反映済み(d9e36f54a、共有Validator、全Family)。これは本委任の対象外(変更しない)。
- 配線予定点(従来案): `val.classify_asr_match`末尾(不合格時のみ)+`er078_asr_value_guard_01.py:68 APPROVED_EQUIVALENCE_BASES`。**この従来案は共有Validatorであり、A/B/Cにも効く。ユーザー決定によりA/B/Cへ効かせてはならないため、X/Zだけに有効化できる構成へ設計を改める必要がある**。これが本委任の中心課題。
- 前回のユーザー判断材料で「A/B/Cへの波及(a)共通呼出点/(b)X/Zのみopt-in」を提示していたが、ユーザーは**X/Zのみ**を決定した(A/B/Cは`PM_GOVERNANCE.md`§27-3で開発停止)。A/B/Cへの展開は以後提案しない。
- KP英語票はKP3V(`er104_kp_three_asr_vote_01.py`、`kp_vote_check_v1`、`guard_lifted:true`)、Store再利用の値ガードは`er078_reuse_value_guard_01.guard_entry(kp_vote_gate_follows)`、呼出点=Store `er006_master_audio_store_01.py:132`/X results `er019 runner:653/753`/X引継ぎ `er019_family_x_validation_inheritance_01.py:206`/Z `er063:731`。Secondary分岐 `er078:599`。短文はer094経路に到達し得る(VALIDATION_02の留意点)。
- 並行作業: 別agentがFamily Z Voice配線+『開いた窓』音声制作(有料run)を実施中。**本委任ではProductionファイル(.py)を変更しない**(設計のみ)。SSOT(OPEN_ITEMS/DECISION_LOG/CURRENT_SPEC/UDR/REPORT_LEDGER)は共有ファイル規約(編集直前に`git status`→再Grep→自分の行のみ編集→即`git add <file>`+commit、index.lockは30秒待機)。
- 本日費用累計0円(日次1,000円)。本委任はAPI費用0(読取・設計のみ)。

## 3. 設計で確定すること(成果物: `docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/WIRING_DESIGN_03.md`)
A. **X/Z限定の有効化機構**(最重要)
  1. 英語ASR判定の全呼出点を列挙(ファイル:行、Family、票種Primary/Secondary/Whisper、対象=本文/KP/英語解説、再利用/retry/fallback/regen/resume経路)。A/B/C側の呼出点も「変更しない対象」として列挙。
  2. 候補機構を比較し1案を推奨: 例 (a)明示引数(`scope`/`family`)をX/Zの呼出点からValidatorへ渡す、(b)X/Z runner起動時に設定するプロセス内コンテキスト(contextvar/明示setter)、(c)X/Z専用のラッパー関数(共有関数は無変更)。評価軸: A/B/Cの挙動がバイト同一で保証できるか/Store再利用・再評価経路(X引継ぎ・Z再利用)でも確実にX/Z文脈になるか/資格(flag)の既定値と起動script/.envでの扱い/rollback手段/Dangling/保守性。**共有関数の既定挙動は現状維持(A/B/Cから呼ばれると従来どおり)**を必須条件とする。
  3. A/B/C不変の証明方法: 既存の`er104_nonkp_before_after_01.py`方式(保存行の署名一致)を踏襲し、A/B/Cの保存判定行の前後sha一致を受入条件にする。
  4. 旧「11-7 既定OFF例外」の整理: 正式採用後は「X/Zで有効・A/B/Cで無効」が正式状態。flag名・既定値・`DefaultOffIsolation`テストの扱い(廃止/置換)を明記。
B. 各票への適用点: Primary(OpenAI)/Secondary(Azure)/Whisper票それぞれで、不合格時のみer109判定を追加する位置、`basis`/`warning`の記録先(既存の判定レコード構造名)、KP3V `kp_vote_check`との整合(票単位で適用→多数決は従来どおり)。
C. 最終保護Gate(`er078_asr_value_guard_01`の数値・否定保護)のSpan単位解除(P-06): er109が同音と証明したspanだけ解除する具体手順(どのデータをどう受け渡すか)、`APPROVED_EQUIVALENCE_BASES`の扱い、`one's↔1's`がこのGateで通ることの道筋、実数値差(`1`vs`2`等)・否定脱落は引き続きNGであることの道筋。
D. ②`no↔know`: `PASS_WITH_WARNING`、警告内容・根拠の内部記録、事後試聴対象の追跡方法(既存のPASS_WITH_WARNING/事後試聴管理の仕組みを再利用。Grepで既存を特定。新しい台帳は原則作らない)。`can't/can`・`don't/do`は非救済(既存の否定保護)。
E. Store再利用・既存音声: 再利用時の再評価経路(`guard_entry`、X引継ぎ、Z)でer109が同じ原則で効くこと/HR Lock済みentryの明示再判定手順(Opus指摘、HR Lock迂回ではなく明示操作としての再判定)/resume時の一貫性。
F. 短文・er094経路の扱い(VALIDATION_02留意点): X/Zで到達し得るか、到達する場合の適用点。
G. テスト計画: 単体(X/Z有効・A/B/C無効・既定挙動不変・決定的ケース=`one's↔1's`/`no↔know`PASS_WITH_WARNING/`1`vs`2`NG/否定脱落NG/同形異音語NG/曖昧略語NG/oronym NG)、統合(KP3V票・Store再利用・X引継ぎ・Z)、A/B/C署名一致、Dangling、全回帰。
H. runtime evidence計画(費用≤40円): X=既存記事の最小再実行(例: coffee_prices a2 KP段で`pump one's fist`、小bagの本文ASR)、Z=melos最小段(KP段/`seize`含むsegment)。「正式経路の実行証拠+決定的ケース検証」の組合せで、自然発火目的の記事生成を繰り返さない。各runの費用見積を出典付きで。**TTS/ASR段は並行する『開いた窓』runとStore manifestが競合するため、実行時は直列化(別agentのrun完了待ち)**を計画に明記。
I. SSOT更新計画(CURRENT_SPEC該当節、OPEN-459、DECISION_LOG、UDR、OF-AHO-P-xx)と、撤去対象(旧既定OFF記述・不要になる旧検査)。
J. リスク・未決: 設計上どうしてもA/B/Cへ変更が及ぶ場合は、その旨と代替案を明記(実施しない)。

## 4. 制約
- Productionの.py変更禁止(設計のみ)。新規testファイルの先行作成も不要(次委任で実装)。
- 探索Trial・新Voice・新規記事生成禁止。API費用0。
- SSOTはOPEN-459のStatusを`APPROVED_FOR_PRODUCTION_WIRING_DESIGN_PENDING_OPUS`(X/Z限定、A/B/C対象外)へ更新し、ユーザー決定(原文所在)をDECISION_LOGへ1エントリ、UDRの該当項目(er109採用3点)を判断済みへ。commitは変更ファイルのみ明示add、`git push origin HEAD:main`、secret_scan `--staged` hits=0。
- 設計書は「読めば実装できる」粒度(ファイル:行、関数名、引数、データ構造、既定値)。推測と事実を分ける。

## 5. 報告(docs/pm/RESULT_PACKET_AHO3.md、同内容を最終報告で返す)
(1)設計書path・要点(推奨機構と理由、代替案との比較表) (2)呼出点一覧の件数(X/Z/ABC別) (3)A/B/C不変の保証方法 (4)P-06のSpan解除手順要約 (5)②の記録・追跡方法 (6)テスト・runtime evidence計画と費用見積 (7)SSOT更新・commit hash・raw URL (8)Opusレビューで特に見てほしい論点(3〜5点) (9)未決・リスク + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。