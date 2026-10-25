# Claude Code指示｜Family Z 原作本質保持 Production Wiring ＋『告げ口心臓』正式再生成

## 1. ユーザー正式承認

以下の2件について、ユーザーの明示的な正式承認を得ました。

**① 原作本質保持方式：案Aを正式採用**

- Seedの「作品の本質」に `narration_voice` を追加する。
- 語り手の自称・立場・聞き手への語りかけなど、原作固有の語り口を定義する。
- 既存の情報伝達経路を利用し、R0・R1・R2・Standard調整まで一貫して伝える。
- 推敲工程に残る三人称固定指示を撤去し、原作の語り口を維持する指示へ置き換える。
- 人称だけでなく、語り手の心理・表現・作品の本質を維持する。
- 新Validator・追加LLM呼出・新retry機構は導入しない。

Status：**APPROVED_FOR_PRODUCTION → PRODUCTION_WIREDまで実施。**

**②『告げ口心臓』Standard／Advancedの正式再生成・公開差し替え**

案Aを正式Production経路へ配線した後、両レベルを正式経路で再生成し、品質検査を経て公開してください。

概算費用は報告済みの約40円を前提とします。

今回の正式承認は再生成・公開までです。**ユーザー最終試聴PASSを先取りして記録しないこと。**

## 2. Production Wiring

Trialで検証済みの案Aを、Family Zの正式Production経路へ実装してください。

対象：

- Seedの原作本質情報
- R0初稿生成
- R1／R2推敲
- Standardレベル調整
- retry／fallback／regeneration／resume
- 関連Prompt・テスト・SSOT

特に、Trial専用経路だけで動作する状態を避け、正式初回Production経路に適用してください。

既存の `in third person` 固定指示が残る箇所を確認し、今回の正式承認と矛盾する指示を撤去してください。

既存の「人物を名前ではなく役割で呼ぶ」指示についても、一人称の語り手を不自然に三人称化しないよう、承認済みの語り口保持方針と整合させてください。

ただし、ユーザーが承認していない新たな文学的品質基準や作品別の禁止ルールを独断で追加しないこと。

## 3. Cross-Family・既存作品との整合

今回の変更はFamily Zの文学作品に関する共通仕様として適用してください。

- 『賢者の贈り物』
- 『開いた窓』
- 『猿の手』
- 『走れメロス』
- その他既存のFamily Z作品

既存Seedへの必要な情報補完と、Production経路の整合を確認してください。

今回の配線を理由に、既存の完成記事をすべて再生成する必要はありません。

既存作品への副作用は、Trialで得られた検証結果を再利用し、必要十分な回帰テストで確認してください。

Family Xなど別Familyへの無断の仕様展開は行わないでください。

## 4. 『告げ口心臓』正式再生成

案AのProduction Wiringを確認したうえで、Standard／Advancedを正式経路で再生成してください。

品質上の重点：

1. 原作の一人称独白を維持する。
2. 語り手が聞き手へ直接語りかける特徴を維持する。
3. 語り手の自己正当化・自己陶酔・狂気を表現する。
4. 老人への執着、殺害、心臓音、警官の前での心理的崩壊、自白までの因果と緊張を維持する。
5. Standard／Advancedの語り口を整合させる。
6. 語彙・文長・表現は各レベルに適応しながら、原作の本質を損なわない。

これらは今回のTrialで承認された品質方針の確認であり、新たな内容ノルマを追加するものではありません。

## 5. 音声・公開品質

正式なTTS・ASR・音声品質検査・組立工程を通してください。

- 正式Productionのモデル・Prompt・Styleを使用
- 既存のretry／fallback／resume仕様を維持
- 音声Gate・必要なRegression／integration testをPASS
- Human Reviewが発生した場合は、既存の自律解決手順に従う
- Trial音声を正式Production音声と誤認しない
- 公開ページの再生・パート切替・スクリプト表示を確認

完成後は、Standard／Advancedの全体試聴・パート別試聴が可能なページを提出してください。

正式公開ページには、古い三人称Advancedが残らないよう確認してください。

## 6. PM Gate・受入条件

**PRODUCTION_WIRED判定には、次をすべて確認してください。**

- 正式初回Production経路への案A配線
- retry／fallback／regeneration／resumeとの整合
- Trial専用経路ではないこと
- 正式runtimeで `narration_voice` が各工程へ渡った証拠
- 旧三人称固定指示が正式経路に残っていないこと
- Standard／Advancedで原作の語り口が維持されていること
- 必須テスト・音声検査PASS
- actual model_id・Prompt・routing等の実行記録
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新
- 必要なGit commit／push
- Fable独立受入評価

コード変更やDEVテストのみをもってPRODUCTION_WIREDとは判定しないでください。

## 7. QCD・自律進行

品質 ＞ 速度 ＞ 量産単価 ≫ 開発費の優先順位を守ってください。

- TrialでVALIDATEDとなった案Aを再利用する。
- 不要な再Trialや全記事の再生成を行わない。
- 独立作業は並列化する。
- 承認範囲内の不具合は原因調査から修正・検証まで自律的に解決する。
- 追加LLM呼出・Validator・過剰な品質検査を増やさない。
- 量産単価の増分を最小化する。
- 約40円の再生成概算と実費を比較し、既存予算・STOP条件を遵守する。

必要十分な品質に達したら追加の磨き込みを行わず、完成・報告してください。

## 8. 完了報告

以下を簡潔に報告してください。

1. 案AのProduction Wiring完了状況とruntime evidence
2. 旧三人称固定指示の撤去確認
3. 既存Family Z作品への副作用確認
4. 『告げ口心臓』Std／Advの正式再生成結果
5. 語り口・原作本質の維持評価
6. 音声Gate・Regression・integration test結果
7. 正式試聴ページURL
8. 開発実費・量産単価への影響
9. SSOT／Git反映状況
10. Fable独立受入Statusと残存Open Item

**最終的な到達目標：案AをPRODUCTION_WIREDにし、『告げ口心臓』のStandard／Advancedを正式完成候補として公開すること。**

その後、ユーザーの最終試聴・承認を受けて記事をCloseoutしてください。
