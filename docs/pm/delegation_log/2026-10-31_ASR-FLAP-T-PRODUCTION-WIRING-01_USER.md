# Claude Codeへの指示｜米国英語Flap-T救済方式 正式Production採用・配線

## 1. ユーザー決定

ASR-FLAP-T-EQUIVALENCE-TRIAL-01で検証した**米国英語Flap-T救済方式（M1）を正式採用**します。

- 現在のStatus：**APPROVED_FOR_PRODUCTION**
- 目標Status：**PRODUCTION_WIRED**
- 対象：Family X／Y／Z、Standard／Advanced
- 優先順位：品質（Q）＞完成速度（D）＞量産単価（C）
- 量産単価：**増加0円**。不要な再生成の削減を目指す。
- Trialの再実施ではなく、検証済み方式のProduction導入を進める。

ユーザーは追加検証・必要な修正・Production Wiringまで承認済みです。承認済み範囲内の技術的問題は自律解決し、不要な確認や作業停止を挟まないでください。

## 2. 採用する仕様

既存のASR同音救済機構に、Flap-T救済を第3層として組み込みます。

基本仕様：

1. 文字列の単純な`t↔d`置換は禁止。CMU辞書の音素列と音韻環境に基づいて判定する。
2. 強勢母音と無強勢音節の間にある/t/↔/d/の差のみを救済対象とする。
3. 母音の一致、canonical単一読み、辞書登録など、Trialで確定した条件を維持する。
4. `writer/rider`、`title/tidal`などAY/AW核の組合せは自動救済しない。
5. 未確認Voice、未登録語、複数読みなどは安全側に倒し、救済対象外とする。
6. 救済時は必ず`PASS_WITH_WARNING`とし、判定根拠を内部ログに記録する。
7. 既存のASR閾値、Primary／Secondary判定条件、最終ANDゲートは変更しない。

**今回承認された品質定義の変更は、上記条件を満たす米国英語Flap-T発音を許容する範囲に限定します。**

既存の同音救済、Connected Speech救済、その他の音声QAの品質基準を独断で変更しないでください。

## 3. 実装前の確認と追加検証

Trialの設計・Closeout資料、Opusレビュー、Fable評価、CURRENT_SPEC、DECISION_LOG、OPEN_ITEMS、既存Production実装を照合してください。

特に以下を実施します。

- Opus指摘の実装前修正M1〜M6をすべて確認・反映する。
- 数字を含むtokenの一致条件を確認する。
- Voice情報が実際のASR判定まで正確に引き渡される設計にする。
- 警告ラベルが後続処理でも確実に保持されるようにする。
- 未probeのVoice／TTS経路を追加確認する。
- 許可リストの根拠に循環がないことを確認する。
- 過去のTrial結果を再利用し、不要なAPI実行を避ける。

追加Voice probeの想定費用は約20円です。既存の承認済み予算・日次上限内で実施し、上限超過が必要な場合のみSTOPして報告してください。

一部のVoiceが確認できない場合は、その組合せだけ救済対象外とするfail-closedを維持し、他の確認済み経路の実装を不合理に止めないこと。

## 4. Production Wiring

正式Production初回経路へ実装してください。

単にmoduleやflagを追加しただけでは完了と認めません。

以下をすべて確認します。

- Family X／Y／Z、Standard／Advancedの正式経路への接続
- 既存のASR同音救済・Connected Speech救済との整合
- retry／fallback／regeneration／resume経路との整合
- 実際のVoice設定と救済許可条件の一致
- 正式runtimeでの救済ルール発火証拠
- 救済対象外ケースが従来どおりNGとなること
- 既存のPrimary／Secondaryおよび最終ANDゲートの維持
- 必須Regression／Validator／integration testのPASS
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSへの反映
- 必要なGit commit／push

flagを使用する場合も、**正式Productionで有効化されていること**を確認してください。既定OFFのまま実装完了と報告しないこと。

## 5. 検証と受入条件

Trialの34ケース、実音声191clip、保存ASR記録6,979件を可能な範囲で再利用します。

少なくとも以下を確認してください。

1. `latter/ladder`、`metal/medal`等の正例が救済される。
2. 既存Trialの反例は誤救済されない。
3. `writer/rider`、`title/tidal`はNGを維持する。
4. 未確認Voiceは救済されない。
5. 救済時の警告と根拠ログが残る。
6. 通常のASR PASS／NG判定に意図しない変化がない。
7. Family別・レベル別に正式Productionへの到達性と実動作が確認できる。

実装途中で不具合が見つかった場合は、原因究明→修正→再検証を承認範囲内で自律的に実施してください。

同じ方法で改善しない場合は、原因と手段を見直してください。品質基準を緩めてPASSさせることは禁止します。

## 6. QCD・STOP条件

**Q：** TrialでVALIDATEDとなった救済条件を守り、誤救済を防止する。

**D：** 独立作業は並列化し、不要な待機・日付分割・逐次確認を避ける。承認済みの必要十分な品質に達したら追加Trialを行わず完成させる。

**C：** 新しいASR・TTS API呼び出しを量産経路に追加しない。量産単価増加0円を受入条件とする。

以下の場合はSTOPして報告してください。

- 承認された品質基準・仕様の変更が必要
- 誤救済など重大な品質問題が解消できない
- 費用・作業範囲が承認上限を超える
- 正式Productionへの安全な配線が不可能
- 新しい仕様・別方式の正式採用判断が必要

技術的な軽微問題については、都度ユーザー判断を求めず自律解決してください。

## 7. 完了報告

Fableによる独立照合を含め、次の順で簡潔に報告してください。

1. **最終Status：Family X／Y／Z、Standard／Advanced別**
2. 救済対象・非対象の実際の判定結果
3. Production runtimeの発火証拠
4. retry／fallback／regeneration／resumeと既存ASR Gateの検証結果
5. 誤救済の有無、未解決事項
6. 量産単価への影響（目標＋0円）と追加開発実費
7. SSOT／Git反映状況
8. ユーザー判断が必要な事項（ある場合のみ）

**PRODUCTION_WIREDの全条件を満たしたFamily・レベルのみ完了扱い**としてください。

一部のVoiceでfail-closedが残る場合は、対象と理由を明示し、承認仕様どおりの適用外なのか、未完了のOpen Itemなのかを区別してください。

Dangling Reference、未承認仕様の混入、旧ルール・旧検査との矛盾も最終確認してください。

今回の目的は、単にFlap-T救済コードを追加することではなく、**音声が正しいにもかかわらずASRの綴り違いによって制作が止まる問題を、安全に解消し、量産単価を増やさず正式Productionで動作させること**です。
