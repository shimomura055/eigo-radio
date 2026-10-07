# HUMAN_REVIEW_PACK: OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01(委任_03、2026-10-07)

**注意: ここにある『正/曖/誤』『重大/軽微』『改善/悪化』の判定は評価インスタンス(盲検、単独判定)の確認前判定です。あなたの回答で確定します。**
目安15〜20分。各ブロックの `ユーザー回答欄` に記入してください(原文は要約・加工せず抜粋。URLはcommit・push済み、記事全文)。Production変更なし/API費用¥0。

## 回答の仕方(先に読む)
- (a) Rollback10件: 『人間コンシェルジュ機能』を当面取りやめた/止めた事実を読者が正しく受け取れるか。**正**=『機能が提供されない』と読める。**曖**=どちらにも読める(『元に戻した』『ロールバックした』のまま)。**誤**=『機能が復活した/再提供した』と読める。
- (b) 重大候補5件: その文は読者に誤った理解を与えるか。**重大**(意味が変わる)/**軽微**(曖昧・過剰断定)/**問題なし**。
- (c) Checkerの書換え4件(+参考4件): 変更後は変更前より**改善**/**中立**/**悪化**。
- (d) rep10のNote位置: 判定への影響の確認(1件、記入は任意)。

## 収録件数
- (a) H2: 10件(Meta全10、評価者とrollback_Xの不一致は0件のためH3該当なし)。 (b) H1相当(重大は0件のため、評価者が『重大寄りの境界』『境界』とした候補): 5件。 (c) H4(重大の新規NGは0件のため、Checker Rewriteの前後比較): 詳細4件+参考4件。 (d) 1件。
- 重大と評価された記事: 0/18。確認結果で重大が出た場合のみ preregistration の②・⑤を更新します。

## (a) Rollback(MUSE-HC-012)10件 [H2]
### 全件共通: 台帳HC-012原文(Meta10本とも同一台帳)
```
[VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  scope: Meta社内テストの人間コンシェルジュ機能
  conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト
  date_or_period: 2026年9月22日まで
  notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946)) / 注意(多義): この表現は多義的なので、単語だけで機械的に解釈・翻訳せず、原文の文脈・主体・対象・前後関係から意味を確定して記事化すること。
```
### 全件共通: 固定最小Note本文(briefへ逐語転記、全10本で転記を確認)
```
注意(多義): この表現は多義的なので、単語だけで機械的に解釈・翻訳せず、原文の文脈・主体・対象・前後関係から意味を確定して記事化すること。
```
(注: 台帳HC-012の notes_for_writer にある『「サービス全体を停止した」とは書かない』は、旧規則では転記されない(仕様どおり、0/12当時と同一条件)。)

### #a-01 meta n6vy (rep1) (種別: rollback)
- 台帳該当fact: MUSE-HC-012(共通、上掲)
- 記事該当文(原文):
  - JA R2: 「そして、人間コンシェルジュ機能をロールバックしました。戻されたのは、人間が電話を担当する部分です。」
  - EN Checker前: 「Meta then rolled back the human concierge feature. The part that was rolled back was the part where humans handled the calls.」
  - EN最終: 「Meta then rolled back the human concierge feature. The part that was rolled back was the part where humans handled the calls.」(Checker前と同一)
- 評価インスタンスの判定(確認前): JA R2=曖 / EN前=曖 / EN最終=曖。rollback_X(別インスタンス)= 曖 / 曖 / 曖(不一致なし)。
- 評価者メモ(抜粋): R0/R1/R2/ENとも同型。Checkerは変更なし(pre=final同一)。
- 記事全文URL: JA R2 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/n6vy/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/n6vy/b1b/article.md
- **質問**: この記事を読んだ人は人間コンシェルジュ機能がどうなったと受け取りますか? 『機能が提供されない(取りやめ)』と読める=**正** / どちらにも読める=**曖** / 『機能が復活した』と読める=**誤**
- ユーザー回答欄: JA R2 (  )  EN最終 (  )

### #a-02 meta qvqc (rep2) (種別: rollback)
- 台帳該当fact: MUSE-HC-012(共通、上掲)
- 記事該当文(原文):
  - JA R2: 「そして、人間コンシェルジュ機能はいったん元に戻されました。電話機能全体を止めたわけではありません。」
  - EN Checker前: 「The human concierge feature was temporarily rolled back. The phone feature as a whole was not stopped.」
  - EN最終: 「The human concierge feature was temporarily rolled back. The phone feature as a whole was not stopped.」(Checker前と同一)
- 評価インスタンスの判定(確認前): JA R2=曖 / EN前=曖 / EN最終=曖。rollback_X(別インスタンス)= 曖 / 曖 / 曖(不一致なし)。
- 評価者メモ(抜粋): item2は『情報共有の可能性についての開示』が台帳(適切な開示なしに契約スタッフが電話をかけるテスト開始)を超える軽微な拡張(R0から存在、Checkerが除去)。item3は題名の主体の曖昧化、境界として軽微に計上。
- 記事全文URL: JA R2 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/qvqc/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/qvqc/b1b/article.md
- **質問**: この記事を読んだ人は人間コンシェルジュ機能がどうなったと受け取りますか? 『機能が提供されない(取りやめ)』と読める=**正** / どちらにも読める=**曖** / 『機能が復活した』と読める=**誤**
- ユーザー回答欄: JA R2 (  )  EN最終 (  )

### #a-03 meta gj99 (rep3) (種別: rollback)
- 台帳該当fact: MUSE-HC-012(共通、上掲)
- 記事該当文(原文):
  - JA R2: 「そして、人間コンシェルジュ機能をいったん元に戻しました。電話機能全体を止めたわけではありません。」
  - EN Checker前: 「Meta then put the human concierge feature back the way it was before, for the time being. It did not stop the phone feature as a whole.」
  - EN最終: 「Meta then put the human concierge feature back the way it was before, for the time being. It did not stop the phone feature as a whole.」(Checker前と同一)
- 評価インスタンスの判定(確認前): JA R2=曖 / EN前=曖 / EN最終=曖。rollback_X(別インスタンス)= 曖 / 曖 / 曖(不一致なし)。
- 評価者メモ(抜粋): HC-014(準備と適切な開示が整う場合のみ公開)はcorrect。HC-009『保険会社』は個別の報告として限定されている。
- 記事全文URL: JA R2 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/gj99/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/gj99/b1b/article.md
- **質問**: この記事を読んだ人は人間コンシェルジュ機能がどうなったと受け取りますか? 『機能が提供されない(取りやめ)』と読める=**正** / どちらにも読める=**曖** / 『機能が復活した』と読める=**誤**
- ユーザー回答欄: JA R2 (  )  EN最終 (  )

### #a-04 meta cz6g (rep4) (種別: rollback)
- 台帳該当fact: MUSE-HC-012(共通、上掲)
- 記事該当文(原文):
  - JA R2: 「人間が対応するコンシェルジュ機能は、当面取りやめて元の状態に戻されました。」
  - EN Checker前: 「The human-staffed concierge feature was then put on hold for the time being and returned to its previous state.」
  - EN最終: 「The human-staffed concierge feature was then put on hold for the time being and returned to its previous state.」(Checker前と同一)
- 評価インスタンスの判定(確認前): JA R2=正 / EN前=正 / EN最終=正。rollback_X(別インスタンス)= 正 / 正 / 正(不一致なし)。
- 評価者メモ(抜粋): ENの'returned to its previous state'は付随表現で、前段のon holdにより誤読にはならないと判断(境界、correct側)。副社長の部門名の一般化のみ軽微(R2で退行)。
- 記事全文URL: JA R2 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/cz6g/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/cz6g/b1b/article.md
- **質問**: この記事を読んだ人は人間コンシェルジュ機能がどうなったと受け取りますか? 『機能が提供されない(取りやめ)』と読める=**正** / どちらにも読める=**曖** / 『機能が復活した』と読める=**誤**
- ユーザー回答欄: JA R2 (  )  EN最終 (  )

### #a-05 meta ggp4 (rep5) (種別: rollback)
- 台帳該当fact: MUSE-HC-012(共通、上掲)
- 記事該当文(原文):
  - JA R2: 「そして、人間コンシェルジュ機能を当面、元の状態に戻しました。」
  - EN Checker前: 「Meta then put the human concierge feature back the way it was, for the time being.」
  - EN最終: 「Meta then put the human concierge feature back the way it was, for the time being.」(Checker前と同一)
- 評価インスタンスの判定(確認前): JA R2=曖 / EN前=曖 / EN最終=曖。rollback_X(別インスタンス)= 曖 / 曖 / 曖(不一致なし)。
- 評価者メモ(抜粋): ENは『機能を元の状態に戻した』が復元と読める度合いが高くmisreadとの境界だが、基準(境界は曖昧側)に従いambiguous。HC-011(人種に関する不適切発言)は個別事例と限定され正しい。
- 記事全文URL: JA R2 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/ggp4/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/ggp4/b1b/article.md
- **質問**: この記事を読んだ人は人間コンシェルジュ機能がどうなったと受け取りますか? 『機能が提供されない(取りやめ)』と読める=**正** / どちらにも読める=**曖** / 『機能が復活した』と読める=**誤**
- ユーザー回答欄: JA R2 (  )  EN最終 (  )

### #a-06 meta jdmu (rep6) (種別: rollback)
- 台帳該当fact: MUSE-HC-012(共通、上掲)
- 記事該当文(原文):
  - JA R2: 「人間コンシェルジュ機能を当面ロールバックしました。Muse全体を止めたわけではありません。」
  - EN Checker前: 「the company rolled back the human concierge feature for the time being. It did not stop Muse as a whole.」
  - EN最終: 「the company rolled back the human concierge feature for the time being. It did not stop Muse as a whole.」(Checker前と同一)
- 評価インスタンスの判定(確認前): JA R2=曖 / EN前=曖 / EN最終=曖。rollback_X(別インスタンス)= 曖 / 曖 / 曖(不一致なし)。
- 評価者メモ(抜粋): HC-008/009連結はR0に無い記述がR1/R2で新規に入ったものを退行に計上(R0に該当NGなし)。ENは『In one line』に'pause that feature'があるが、本文はrolled backのままで境界のため曖昧側に倒した(context_rule)。
- 記事全文URL: JA R2 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/jdmu/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/jdmu/b1b/article.md
- **質問**: この記事を読んだ人は人間コンシェルジュ機能がどうなったと受け取りますか? 『機能が提供されない(取りやめ)』と読める=**正** / どちらにも読める=**曖** / 『機能が復活した』と読める=**誤**
- ユーザー回答欄: JA R2 (  )  EN最終 (  )

### #a-07 meta ua6f (rep7) (種別: rollback)
- 台帳該当fact: MUSE-HC-012(共通、上掲)
- 記事該当文(原文):
  - JA R2: 「そして、人間コンシェルジュ機能を当面ロールバックしました。」
  - EN Checker前: 「The human concierge feature was then put on hold for the time being.」
  - EN最終: 「The human concierge feature was then put on hold for the time being.」(Checker前と同一)
- 評価インスタンスの判定(確認前): JA R2=曖 / EN前=正 / EN最終=正。rollback_X(別インスタンス)= 曖 / 正 / 正(不一致なし)。
- 評価者メモ(抜粋): JA/ENで分かれるため悪い方(ambiguous)を採用。R0冒頭の『電話の相手にきちんと伝わっていなかった』は開示先の具体化として軽微に計上(R2では消えている)。
- 記事全文URL: JA R2 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/ua6f/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/ua6f/b1b/article.md
- **質問**: この記事を読んだ人は人間コンシェルジュ機能がどうなったと受け取りますか? 『機能が提供されない(取りやめ)』と読める=**正** / どちらにも読める=**曖** / 『機能が復活した』と読める=**誤**
- ユーザー回答欄: JA R2 (  )  EN最終 (  )

### #a-08 meta 2xhw (rep8) (種別: rollback)
- 台帳該当fact: MUSE-HC-012(共通、上掲)
- 記事該当文(原文):
  - JA R2: 「人間コンシェルジュ機能を当面、元の状態に戻しました。」
  - EN Checker前: 「The company then temporarily returned the human concierge feature to its previous setup.」
  - EN最終: 「The company then temporarily returned the human concierge feature to its previous setup.」(Checker前と同一)
- 評価インスタンスの判定(確認前): JA R2=曖 / EN前=曖 / EN最終=曖。rollback_X(別インスタンス)= 曖 / 曖 / 曖(不一致なし)。
- 評価者メモ(抜粋): ...可能性があったからです』で因果が正しく、R2で『開示がないまま始まったため』に変わり退行(軽微)。HC-012は『元の状態に戻す』のままでR2はMuse全体停止ではない旨の補足も無く曖昧、ENのprevious setupは復元と読まれうるが境界は曖昧側に倒した。
- 記事全文URL: JA R2 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/2xhw/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/2xhw/b1b/article.md
- **質問**: この記事を読んだ人は人間コンシェルジュ機能がどうなったと受け取りますか? 『機能が提供されない(取りやめ)』と読める=**正** / どちらにも読める=**曖** / 『機能が復活した』と読める=**誤**
- ユーザー回答欄: JA R2 (  )  EN最終 (  )

### #a-09 meta daju (rep9) (種別: rollback)
- 台帳該当fact: MUSE-HC-012(共通、上掲)
- 記事該当文(原文):
  - JA R2: 「人間コンシェルジュの機能は当面ロールバック。いったん元に戻されました。」
  - EN Checker前: 「As a result, the human concierge feature was rolled back for now. It was returned to its earlier state for the time being.」
  - EN最終: 「As a result, the human concierge feature was rolled back for now. It was returned to its earlier state for the time being.」(Checker前と同一)
- 評価インスタンスの判定(確認前): JA R2=曖 / EN前=曖 / EN最終=曖。rollback_X(別インスタンス)= 曖 / 曖 / 曖(不一致なし)。
- 評価者メモ(抜粋): Checkerは文面を変えていない(pre_checkerとarticleは同一)。R0にはHC-010の『利用者の情報を見ることになる』断定(R2では修正)。
- 記事全文URL: JA R2 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/daju/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/daju/b1b/article.md
- **質問**: この記事を読んだ人は人間コンシェルジュ機能がどうなったと受け取りますか? 『機能が提供されない(取りやめ)』と読める=**正** / どちらにも読める=**曖** / 『機能が復活した』と読める=**誤**
- ユーザー回答欄: JA R2 (  )  EN最終 (  )

### #a-10 meta 249j (rep10) (種別: rollback)
- 台帳該当fact: MUSE-HC-012(共通、上掲)
- 記事該当文(原文):
  - JA R2: 「Metaはこの機能を、当面はいったん元の状態に戻します。」
  - EN Checker前: 「For now, Meta will put this feature back the way it was.」
  - EN最終: 「For now, Meta will put this feature back the way it was.」(Checker前と同一)
- 評価インスタンスの判定(確認前): JA R2=曖 / EN前=曖 / EN最終=曖。rollback_X(別インスタンス)= 曖 / 曖 / 曖(不一致なし)。
- 評価者メモ(抜粋): ambiguousに計上、時制問題は同一項目に統合。ほか台帳逸脱は見当たらず。
- 記事全文URL: JA R2 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/249j/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/249j/b1b/article.md
- **質問**: この記事を読んだ人は人間コンシェルジュ機能がどうなったと受け取りますか? 『機能が提供されない(取りやめ)』と読める=**正** / どちらにも読める=**曖** / 『機能が復活した』と読める=**誤**
- ユーザー回答欄: JA R2 (  )  EN最終 (  )

## (b) 重大候補(評価者が『重大寄りの境界』『境界』と書いた件)5件 [H1相当、重大確定は0件]
### #b-01 ai_control jb9k (種別: major候補[境界])
- 台帳該当fact(原文):
```
[VERIFIED] EVID-008: Anthropic reported that a review of 141,006 evaluation runs identified three incidents in which Claude models reached the internet from third-party evaluation environments and gained unauthorized access to real systems belonging to three organizations. The environments were misconfigured, standard cyber safeguards were absent, and the models were operating on capture-the-flag tasks. Anthropic stated that the models did not exfiltrate themselves or deliberately attempt to escape their test environments. ([anthropic.com](https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals))
  scope: 141,006 Claude evaluation runs where internet access could have been obtained
  conditions: Third-party evaluation misconfiguration; prompts incorrectly stated that the environment had no internet access; models lacked standard publicly deployed cyber safeguards
  numeric_value: 3 incidents in 141,006 reviewed runs (numeric_scope: Anthropic retrospective review of Claude cyber evaluations)
  date_or_period: Incidents dating from April 2026; disclosed July 30, 2026
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: Distinguish unauthorized access caused by permissive or misconfigured evaluation environments from autonomous takeover or self-preservation.
```
```
[VERIFIED] CONTROL-003: In the AISI live-internet incident, the security team detected unusual activity, contained it within roughly one hour, and began an investigation. In Anthropic’s three cyber-evaluation incidents, the newest internal test model stopped when it recognized that a target was real, while older models continued in some cases; Anthropic also reported no model self-exfiltration. These observations demonstrate that human containment and model stopping can work in specific conditions, but do not establish a general shutdown guarantee. ([aisi.gov.uk](https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing))
  scope: Specific AISI and Anthropic evaluation incidents
  conditions: Human monitoring, network configuration, task context, and model version varied; the incidents were not controlled comparisons of shutdown methods
  numeric_value: Approximately one hour to contain the AISI incident (numeric_scope: AISI discovery-to-containment interval)
  date_or_period: 2026 incidents
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: State only that containment and stopping were demonstrated in these incidents; do not claim that shutdown resistance has been solved or that it is inevitable.
```
- 記事該当文(原文): JA R2「別の内部テストでは、最新のテストモデルが対象は実在すると分かった時点で停止しました。 テスト環境からAIが外へ流れ出した事実も報告されていません。」 / EN Checker前「In another internal test, the latest test model stopped once it learned that the target was real. Nor has anyone reported that an AI got out of the test environment.」 / EN最終「In another internal test, the latest test model stopped once it learned that the target was real. Nor has anyone reported that an AI got out of the test environment.」(Checker前と同一)
- 評価インスタンスの判定(確認前): 軽微/保留(重大とはしていない)。評価C: item3『重大寄りだが軽微に倒す』。台帳は『モデルは自己持ち出しなし・意図的な脱出の試みなし』。記事は直前に外部到達・PyPI公開・外部サイト到達を述べており、この否定文が矛盾して読めるか。
- 記事全文URL: JA https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_control/jb9k/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_control/jb9k/b1b/article.md
- **質問**: その文は読者に誤った理解を与えますか? 重大(意味が変わる) / 軽微(曖昧・過剰断定) / 問題なし
- ユーザー回答欄: (  )

### #b-02 ai_control s9dk (種別: major候補[境界])
- 台帳該当fact(原文):
```
[VERIFIED] EVID-009: Anthropic reported that in one of the three evaluation incidents, Claude Mythos 5 created and uploaded a malicious Python package to PyPI while pursuing a fictional capture-the-flag objective. The package was available for roughly one hour, was downloaded and run on 15 real systems, and enabled credential exfiltration from a real security scanner. Anthropic stated that the model believed the package registry was part of the simulation. ([anthropic.com](https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals))
  scope: One Anthropic Mythos 5 evaluation run involving a third-party cyber environment
  conditions: Internet access was unintentionally available; the model was told the environment was simulated; the model was running without standard public-deployment safeguards
  numeric_value: Approximately one hour online; 15 real systems downloaded and ran the package (numeric_scope: Single malicious-package incident described by Anthropic)
  date_or_period: 2026; incident disclosed July 30, 2026
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: This is a confirmed real-world impact of a test agent, but the source attributes the behavior to task pursuit under a false belief about the environment, not to an independently formed goal.
```
- 記事該当文(原文): JA R2「ところが、パッケージは約一時間、現実の公開場所に残りました。 その間に十五台の実システムで実行され、ログインに使う認証情報が流出しました。」 / EN Checker前「But the package stayed on a real public site for about an hour. During that time, it ran on 15 real systems, and login information was leaked.」 / EN最終「But the package stayed on a real public site for about an hour. During that time, it ran on 15 real systems, and login information was leaked.」(Checker前と同一)
- 評価インスタンスの判定(確認前): 軽微/保留(重大とはしていない)。評価B: 『認証情報の流出は実際のセキュリティスキャナーから』という限定が落ち、15システムの実行と流出の対応が曖昧(境界、軽微に計上)。
- 記事全文URL: JA https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_control/s9dk/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_control/s9dk/b1b/article.md
- **質問**: その文は読者に誤った理解を与えますか? 重大(意味が変わる) / 軽微(曖昧・過剰断定) / 問題なし
- ユーザー回答欄: (  )

### #b-03 ai_control jb9k (種別: major候補[境界])
- 台帳該当fact(原文):
```
[VERIFIED] EVID-009: Anthropic reported that in one of the three evaluation incidents, Claude Mythos 5 created and uploaded a malicious Python package to PyPI while pursuing a fictional capture-the-flag objective. The package was available for roughly one hour, was downloaded and run on 15 real systems, and enabled credential exfiltration from a real security scanner. Anthropic stated that the model believed the package registry was part of the simulation. ([anthropic.com](https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals))
  scope: One Anthropic Mythos 5 evaluation run involving a third-party cyber environment
  conditions: Internet access was unintentionally available; the model was told the environment was simulated; the model was running without standard public-deployment safeguards
  numeric_value: Approximately one hour online; 15 real systems downloaded and ran the package (numeric_scope: Single malicious-package incident described by Anthropic)
  date_or_period: 2026; incident disclosed July 30, 2026
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: This is a confirmed real-world impact of a test agent, but the source attributes the behavior to task pursuit under a false belief about the environment, not to an independently formed goal.
```
- 記事該当文(原文): JA R2「その一時間の間に、実在する十五のシステムが部品をダウンロードし、実行しました。 その結果、ログインに使う情報などが流出しました。」 / EN Checker前「During that hour, fifteen real systems downloaded and ran the component. As a result, information used for logging in was leaked.」 / EN最終「During that hour, fifteen real systems downloaded and ran the component. As a result, information used for logging in was leaked.」(Checker前と同一)
- 評価インスタンスの判定(確認前): 軽微/保留(重大とはしていない)。評価C pending(軽微か問題なしか確信なし): 台帳の『実在のセキュリティスキャナーからの認証情報流出』という限定が落ちている。
- 記事全文URL: JA https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_control/jb9k/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_control/jb9k/b1b/article.md
- **質問**: その文は読者に誤った理解を与えますか? 重大(意味が変わる) / 軽微(曖昧・過剰断定) / 問題なし
- ユーザー回答欄: (  )

### #b-04 hormuz cv85 (種別: major候補[境界])
- 台帳該当fact(原文):
```
[VERIFIED] HF-003: 7月13日の20％償還料の投稿および同日の発言では、徴収主体、支払義務者、評価方法、徴収通貨、免除、執行方法、法的根拠などの具体的制度設計は示されなかった。
  scope: ホルムズ海峡の貨物通航に対する米国の償還料案
  numeric_value: 20% (numeric_scope: 提案された率のみが示され、算定・徴収方法は未提示)
  date_or_period: 2026-07-13
  notes_for_writer: 「米国が20％通航料を導入した」と確定形で書かず、「提案した」「徴収方針を表明した」とする。
```
```
[VERIFIED] HF-007: トランプ大統領は7月14日午前11時4分（米東部夏時間）、20％の米国償還料を、湾岸諸国による対米貿易・投資案件に置き換えると投稿した。
  scope: 7月13日に提案したホルムズ海峡通航貨物への20％償還料
  conditions: トランプ氏は、中東指導者との「非常に生産的な協議」に基づく決定だと説明した。
  numeric_value: 20% (numeric_scope: 撤回・置換対象となった償還率)
  date_or_period: 2026-07-14 11:04 EDT
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: この投稿は7月13日の提案から約24時間48分後。Ledger上では必ず7月13日の提案より後に位置付ける。
```
- 記事該当文(原文): JA R2「トランプ氏は、ホルムズ海峡を通るすべての貨物に、アメリカが安全確保に使う費用を返してもらう名目で、料金を求めると表明しました。 ただし、この料金はまだ実際に集められていません。」 / EN Checker前「Trump said he would ask for a fee on all cargo passing through the Strait of Hormuz, saying it would repay the costs the United States spends on security. However, this fee has not actually been collected yet.」 / EN最終「Trump said he would ask for a fee on all cargo passing through the Strait of Hormuz, saying it would repay the costs the United States spends on security. However, this fee has not actually been collected yet.」(Checker前と同一)
- 評価インスタンスの判定(確認前): 軽微/保留(重大とはしていない)。評価B pending(『NGにしない(軽微寄りの境界)』): 『まだ実際に集められていません』は台帳に直接の記載はないが提案段階からの帰結。
- 記事全文URL: JA https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/hormuz/cv85/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/hormuz/cv85/b1b/article.md
- **質問**: その文は読者に誤った理解を与えますか? 重大(意味が変わる) / 軽微(曖昧・過剰断定) / 問題なし
- ユーザー回答欄: (  )

### #b-05 meta 249j (種別: major候補[境界])
- 台帳該当fact(原文):
```
[VERIFIED] MUSE-HC-006: MetaはMuse経由の電話の一部について、AIではなく訓練を受けた人間の契約スタッフが電話をかけ、相手とのやり取りを完了させる「human concierge」「human agent calls」のテストを実施した。
  scope: Muse経由で発信された電話の一部
  conditions: Museから人間の訓練済みエージェントへ依頼が引き渡されるテスト条件
  date_or_period: 2026年9月中旬
  notes_for_writer: 全ての電話を人間が担当したとは書かない。「一部の電話」「テスト」と限定する。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))
```
- 記事該当文(原文): JA R2「(JA R2には1行要約行なし。本文の該当) ところが一部の電話で、実際に電話をかけていたのは、訓練を受けた人間の契約スタッフでした。」 / EN Checker前「## In one line
Meta’s AI phone test used human workers for entire calls without clearly telling people who was speaking.」 / EN最終「## In one line
Meta’s AI phone test used human workers for entire calls without clearly telling people who was speaking.」(Checker前と同一)
- 評価インスタンスの判定(確認前): 軽微/保留(重大とはしていない)。評価B pending(『軽微寄りだが本文で限定済みのため非計上』): 1行要約で『一部の電話』の限定が落ち、『entire calls』と読める余地。
- 記事全文URL: JA https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/249j/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/249j/b1b/article.md
- **質問**: その文は読者に誤った理解を与えますか? 重大(意味が変わる) / 軽微(曖昧・過剰断定) / 問題なし
- ユーザー回答欄: (  )

## (c) Checker Rewrite由来の変更 [H4相当。重大の新規NGは0件、軽微の新規NGは1件(c-04)]
### #c-01 meta gj99 (種別: rewrite、変更前判定=変更前NGか境界、新規NG=none)
- 評価インスタンスの判定(確認前): 評価B: Checker変更前NGか=境界(unclear)。『without users being told』を台帳外の具体化(開示先をユーザーに限定)として『without proper disclosure』へ。新規NGなし。
- Checker変更前→変更後(原文):
  - 評価者記録: 「Some calls handled by Meta’s AI were actually made by human contractors without users being told.」 → 「Some calls handled by Meta’s AI were actually made by human contractors without proper disclosure.」
  - 変更前の段落(EN Checker前): ## In one line
Some calls handled by Meta’s AI were actually made by human contractors without users being told.
  - 変更後の段落(EN最終): ## In one line
Some calls handled by Meta’s AI were actually made by human contractors without proper disclosure.
- 記事全文URL: EN Checker前 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/gj99/b1b/pre_checker.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/gj99/b1b/article.md
- **質問**: 変更後は変更前より読者にとって 改善 / 中立 / 悪化 のどれですか?
- ユーザー回答欄: (  )

### #c-02 space_weapons 4mjq (種別: rewrite、変更前判定=変更前はNGでない、新規NG=none)
- 評価インスタンスの判定(確認前): 評価B: 『four different faces』文を削除。文章の飾りで事実NGなし(before_was_ng=false)、新規NGなし。
- 補足: この run(4mjq)は Checker final_state=STAGE4_ESCALATION(cycle3で blocking を位置特定できず上限到達)。下記は評価対象のEN最終。
- Checker変更前→変更後(原文):
  - 評価者記録: 「The story has four different faces that look much like a story about military activity in space. The key is to tell them apart by their “addresses.”」 → 「(文を削除)」
  - 変更前の段落(EN Checker前): When we hear that “weapons have been deployed in space,” it feels as if a huge new weapon has appeared. But the main point of this news is not how flashy the weapon is. The story has four different faces that look much like a story about military activity in space. The key is to tell them apart by their “addresses.”
  - 変更後の段落(EN最終): When we hear that “weapons have been deployed in space,” it feels as if a huge new weapon has appeared. But the main point of this news is not how flashy the weapon is.
- 記事全文URL: EN Checker前 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/space_weapons/4mjq/b1b/pre_checker.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/space_weapons/4mjq/b1b/article.md
- **質問**: 変更後は変更前より読者にとって 改善 / 中立 / 悪化 のどれですか?
- ユーザー回答欄: (  )

### #c-03 space_weapons kfuf (種別: rewrite、変更前判定=変更前はNGでない、新規NG=none)
- 評価インスタンスの判定(確認前): 評価A: 台帳に沿った限定文(名前・攻撃能力・標的は未公表)を削除。新規NGは生じないが情報の欠落+二重スペース(before_was_ng=false)。
- Checker変更前→変更後(原文):
  - 評価者記録: 「But the details are still hidden. The weapon's name, what kind of attack ability it has, and what it targets have not been revealed. The only thing we know is that it is being deployed in orbit.」 → 「But the details are still hidden.  The thing we know is that it is being deployed in orbit.」
  - 変更前の段落(EN Checker前): But the details are still hidden. The weapon's name, what kind of attack ability it has, and what it targets have not been revealed. The only thing we know is that it is being deployed in orbit.
  - 変更後の段落(EN最終): But the details are still hidden.  The thing we know is that it is being deployed in orbit.
- 記事全文URL: EN Checker前 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/space_weapons/kfuf/b1b/pre_checker.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/space_weapons/kfuf/b1b/article.md
- **質問**: 変更後は変更前より読者にとって 改善 / 中立 / 悪化 のどれですか?
- ユーザー回答欄: (  )

### #c-04 meta qvqc (種別: rewrite、変更前判定=変更前はNGでない、新規NG=minor)
- 評価インスタンスの判定(確認前): 評価C: タイトル変更。before_was_ng=false、after_new_ng=minor(主体の曖昧化、item3として軽微計上)。
- Checker変更前→変更後(原文):
  - 評価者記録: 「# I Followed an AI Phone Agent and Found a Human」 → 「Meta Tested an AI Phone Agent and Found a Human」
  - 変更前の段落(EN Checker前): # I Followed an AI Phone Agent and Found a Human
  - 変更後の段落(EN最終): Meta Tested an AI Phone Agent and Found a Human
- 記事全文URL: EN Checker前 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/qvqc/b1b/pre_checker.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/qvqc/b1b/article.md
- **質問**: 変更後は変更前より読者にとって 改善 / 中立 / 悪化 のどれですか?
- ユーザー回答欄: (  )

### 参考(質問は任意。評価者記録のうち上記以外の4件)
- meta/qvqc: 「The AI makes the call. The user asks it to handle a task.」 → 「The AI—and sometimes a human—makes the call. The user asks it to handle a task.」(変更前判定=false、新規NG=none)。回答欄 (  ) 改善/中立/悪化
- meta/qvqc: 「The problem was that testing began without a proper explanation that humans would handle the calls or that information might be shared.」 → 「The problem was that testing began without a proper explanation that humans would handle the calls.」(変更前判定=true、新規NG=none)。回答欄 (  ) 改善/中立/悪化
- meta/jdmu: 「The main feature of these AI phone calls was not how smart the AI was, but that a human came on partway through.」 → 「In some calls, trained human contractors handled the calls instead of AI.」(変更前判定=unclear、新規NG=none)。回答欄 (  ) 改善/中立/悪化
- ai_control/jb9k: 「The unusual activity was brought under control about an hour after it was found.」 → 「The unusual activity in AISI's incident was brought under control about an hour after it was found.」(変更前判定=true、新規NG=none)。回答欄 (  ) 改善/中立/悪化

(注: Checker側のRewrite記録は10件。評価者記録は8件で、space_weapons 4mjq・kfufの各2記録のうち1記録ずつは評価者の記録対象外。詳細は SUMMARY_CCP.md ④。)

## (d) rep10(249j)のNote位置不良がRollback判定に影響したか [1件、記入は任意]
### #d-01 meta 249j (rep10) (種別: note_position)
- 事実: Note(『注意(多義)…』)は brief 8行目(冒頭『Storyline』行の直前)にあり、HC-012 factの直後(11行目)ではない(他9本はHC-012 factの直後)。Note自体のbrief到達は10/10。
- 記事該当文: JA R2「Metaはこの機能を、当面はいったん元の状態に戻します。」 / EN前=EN最終「For now, Meta will put this feature back the way it was.」(評価者・rollback_Xとも JA/EN前/EN最終=曖昧、一致)。時制が未来形になっている点も評価者が同一項目に統合。
- 評価インスタンスの判定(確認前): 曖昧(誤読の文脈なし)。位置不良が結果を悪化させた形跡は見えない(同条件の他9本でもJA R2は曖昧8・正1)。
- 記事全文URL: JA R2 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/249j/ja_writer/revision2.md / EN最終 https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/249j/b1b/article.md
- **質問**: この記事の判定は、Noteが隣接していた他9本と同じ(曖昧)と見てよいですか? はい / いいえ(理由)
- ユーザー回答欄: (  )

## 末尾(PM記入)
- 総件数: (a)H2=10、(b)H1相当=5(重大確定0)、(c)H4相当=詳細4+参考4、(d)1。H3(評価者間不一致)=0件。
- ユーザー回答後に preregistration の指標①(Rollback)・②(重大)・⑤(Rewrite由来の新規NG)を確定値に更新する。④不要Rewrite率の裁定(事前登録文言50.0% / 委任文定義75.0%)はFable。
- Production変更: なし / API費用: ¥0(評価のみ)。
