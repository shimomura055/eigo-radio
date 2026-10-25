<!-- 保存メタ: 元session=a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl line19607 / 抽出日時=2026-10-25 / role=user / 補正=なし(孤立サロゲート0件・本文無補正) -->


<pasted_content id="a638">
# Claude Codeへの指示
## 日本語ASR誤PASS是正｜XYZ共通Production正式採用・Wiring完了

### 1. ユーザー正式決定

**OPEN-517の是正方式F1＋F2をFamily X／Y／Z共通で正式採用する。**

Status：**APPROVED_FOR_PRODUCTION**  
到達目標：**PRODUCTION_WIRED（X／Y／Zそれぞれ）**

承認内容：

- **F1：** 読み一致でPASSとなる場合も、数字の値・否定表現の最終確認を必ず実施する。
- **F2：** かな書き数詞の表記を適切に統一し、正常音声の不要なNGを防ぐ。
- 既存の承認済み品質基準を維持する。
- 正式Production経路に実装し、runtimeで動作を確認する。

今回の承認はF1＋F2の方式と適用であり、①v2・②B-lightのProduction採用を意味しない。

### 2. 検証済み結果の活用

今回のv4検証結果を基準とする。

- 既存771件＋未知493件＝1,264件
- 正常音声の追加NG：0件
- 既知負例：9/9件を遮断
- 合成負例：24/24件を遮断
- 既存判定の回帰：0件
- 実attempt 421件での追加再生成・HR Lock：0件
- 過去公開音声3,869ファイルの監査：該当不具合0件

この結果を再利用し、不要な有料Trialを繰り返さないこと。

### 3. Production実装

以下を実施する。

1. F1＋F2を正式Production経路に組み込む。
2. Family X／Y／Zの共通日本語ASR経路へ適用する。
3. 読み一致PASSでも値・否定の最終確認が必ず実行されることを保証する。
4. 再生成・retry・fallback・regeneration・resume時にも同じ品質条件を維持する。
5. 正常音声の誤NG増加を防止する。
6. 既存のrollback機構を維持する。
7. 実装方法は既存共通moduleの再利用を優先し、Familyごとに重複実装しない。

特にFamily YはProduction立ち上げ中のため、今回の承認済み共通仕様を初回Production経路へ組み込み、配線漏れを防止すること。

### 4. OPEN-523／524の扱い

併せて報告された数詞判定漏れについても、既存の承認済み品質基準に反する不具合修正として扱う。

- OPEN-523：弱いかな数詞の素通し
- OPEN-524：かな数詞の語境界欠如

両者の原因究明・修正・検証は自律的に進める。

ただし、F1＋F2のProduction反映を不合理に遅らせないこと。

独立して実装・検証できる場合は並列化し、共通のRegressionを再利用する。

必要なOpusレビューを実施し、承認済み品質基準に収まる修正であれば自律的に反映する。新しい品質基準や合格条件の変更が必要な場合は、ユーザー判断へ回す。

OPEN-522は今回の承認対象外とし、既知の限界として継続管理する。

### 5. Production Wiringの必須条件

Family X／Y／Zそれぞれについて、以下を確認する。

- 正式初回Production経路への配線
- retry／fallback／regeneration／resumeとの整合
- 正式runtimeでF1＋F2が発火した証拠
- 正例・負例・Regression／Validator／integration test PASS
- 実際のASR model_id・routing・判定結果の証拠
- 既存の再生成・Human Review Lockとの整合
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新
- OF-AUW-01追補L65の不整合解消
- Git commit／push
- Fableによる独立受入評価

**コード配線や単体テストだけではPRODUCTION_WIREDとしない。**

Family Yで正式runtime確認が立ち上げ作業の進捗に依存する場合は、コード配線完了とruntime未確認を区別し、OPEN_ITEMSで追跡する。

X／Zの完了をYの待機によって不合理に遅らせないこと。

### 6. ①v2・②B-lightは継続

今回のProduction採用とは独立して、以下を継続する。

**① v2再評価**
- 現Status：VALIDATED（限定）
- 誤NG削減効果は限定的。
- 既存データと検証結果を活用し、②との統合も含めて改善を検討する。

**② B-light**
- 原因究明・対策立案・Trialは承認済み。
- Azure Secondaryを活用した安全な誤NG救済を検証する。
- ③F1＋F2を組み込んだ状態との整合を確認する。
- UDR #136に関わる合格条件の変更は、ユーザーの正式判断を得る。

①②も、原因究明→対策→Trial→再評価を承認済み予算・Scope内で自律的に進める。

**①②の検証完了を待たず、③のProduction Wiringを進めること。**

### 7. QCD・予算

- 品質（Q）＞速度（D）＞量産単価（C）≫開発費用を遵守する。
- 承認済み予算・Scope内で自律的に実行する。
- 既存データ・テストを再利用し、不要なAPI支出を避ける。
- 独立作業は並列化する。
- 不具合は原因究明・修正・検証まで自律的に完結する。
- 承認範囲外の仕様変更、予算超過、重大な品質問題はSTOPして報告する。

### 8. 完了報告

③のProduction Wiring完了後、以下を報告する。

1. Family X／Y／ZそれぞれのStatus
2. F1＋F2の正式runtime evidence
3. 誤PASS防止・誤NG増加防止の検証結果
4. OPEN-523／524の対応状況
5. retry／fallback等との整合
6. 追加再生成・Human Reviewへの影響
7. 費用・量産単価への影響
8. Fable独立受入評価
9. SSOT・Git反映状況
10. 残Open Item

また、**①v2・②B-lightについても、検証の進捗と最終結果を別途報告すること。**

---

**最優先は③のXYZ共通Production Wiringを確実に完了させること。**

同時に①②の改善を継続し、日本語ASRの誤NG・誤PASSの包括的解決まで追跡してください。
</pasted_content id="a638">
