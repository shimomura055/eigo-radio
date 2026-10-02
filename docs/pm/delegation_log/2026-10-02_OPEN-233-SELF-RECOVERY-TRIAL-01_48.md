## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_48)。並行タスク: 委任_47(rep22の正解ラベル照合、read-only)が同時に動く。委任_47は`er052_output/open233_rep22_truth_label_check_01/`と`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_47.md*`を作る。本委任はこれらを編集せず、`git add`もしない。

## 性質/到達上限Status/禁止事項

- 性質: 設計書の作成(実装前のOpus独立レビューに出すための設計案)と、前の委任の成果物の保存・commit。**実装しない。Trialを回さない。**
- 到達上限Status: なし(OPEN-233のStatusは変更しない)。
- 禁止事項:
  - コード・Prompt・テストの編集禁止(runner、er003、er051、er052_*の`.py`すべて)。
  - Production正式pathの変更禁止。
  - SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/PM_GOVERNANCE.md`)の編集禁止。既存の設計書`docs/pm/design_open233_self_recovery_flow_01.md`とREPORTも編集しない(新しい設計書を1つ作るだけ)。
  - `ACTIVE_TASK.md`/`RESULT_PACKET.md`は本委任の内容で上書きしてよい(一時ファイル、addしない)。
  - LLM/TTS/ASR/Web Searchの呼び出し禁止(費用¥0)。
  - `git add -A`/`stash`/`amend`/`rebase`/force push禁止。既存の未commit差分(`er006_output`等のM表示のファイル、他の未追跡ファイル)には触れない・addしない。
- 費用上限: ¥0(API呼び出しなしのためT-3は対象外)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 条件A(新しい構造・処理フローの設計)に該当。本委任は設計案の作成までで、Opusレビューは本委任の後にFableが依頼する。実装はその後。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)

T-0の補足(本委任での実値): 保存先は `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_48.md`。受領した委任文を全文・見出しを省略せずそのまま保存すること(要約保存は不可)。

## ユーザー指示(原文)

今回のフェーズのユーザー指示全文は`DECISION_LOG.md`末尾付近(委任_42が逐語で追記済み、Grep `委任_42`で位置特定)にある。設計書の「前提」節には、そこから該当箇所を逐語で引用すること(要約しない)。特に守るべき原文:

- 「Production正式pathは変更禁止です。Trial/検証用の範囲で進めてください。」
- 「Checkerが示した違反範囲を後段で再推測しない/複数文なら複数文のままRewriteへ渡す/離れた複数箇所なら複数範囲として渡す/別AIの引用でRewrite対象を決めない/類似度や単語重なりで勝手に1文へ縮小しない/文ID・文字オフセット方式は現時点では採用しない/最小修正優先ルールを維持する」
- 「文の一部が違反だからといって、最初から文全体Rewriteへ広げないでください。」
- 「判定基準そのものは変えず、**違反範囲の出力形式だけを変える**こと。」
- 「日本語は、エンターテイメント性のある英語記事を作るための手段。LedgerとのDeviationが英語側にあるなら、英語を直せばよい。」
- 「単に「日英整合を保ちたい」という理由だけなら、日本語まで遡って修正する必要はありません。」
- STOP条件: 「新しいProduct原則の採用が必要 / Safety原則の変更が必要 / Production正式仕様の変更判断が必要 / ¥600予算上限超過が必要 / Claude案とOpusレビューが重要点で対立し、Fableで解消できない / 複数の合理的な設計案に明確なQCDトレードオフがあり、ユーザー判断が必要」
- 周回の扱い: 周回上限を単純に増やす対策は採らない(ユーザー指示§5、原文は`DECISION_LOG.md`で確認して引用)。

## 作業1: 前の委任の報告を保存する

委任_43〜46の報告は最終メッセージで返されただけで、ファイルになっていない。次のtranscript(JSONL)から、各委任の**最終報告本文**(最後のassistantメッセージ、またはSubagentHandbackに渡した報告文)をスクリプトで抽出し、Markdownとして保存する。transcriptは巨大なので全文Readしない(Pythonで該当メッセージだけ取り出す)。

- 場所: `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\f9ae115b-0305-437d-ac2d-b452b22a5e2a\tasks\`
- 委任_44: `a04340bc6b32522cb.output`、委任_45: `adde5e36bfe4009ab.output`、委任_46: `a8401b13fe2a002ff.output`、委任_42: `abdb0c692f17f4fa9.output`。
- 委任_43と委任_41はファイル名が不明。同ディレクトリの`.output`を、冒頭の委任文にある「委任_43」「委任_41」の文字列で特定する(スクリプトで検索)。
- 保存先: `docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_<番号>_result.md`(番号は41、42、43、44、45、46)。本文は改変・要約せずそのまま保存し、冒頭に「抽出元transcriptのファイル名、抽出日時、本文は改変していない旨」を1〜3行で付ける。
- 抽出できないものは作らず、「未保存」と理由を報告する(推測で本文を再構成しない)。

抽出した報告は、作業2の設計書の事実の出所として使う。

## 作業2: 対策設計書を作る

新規ファイル: `docs/pm/design_open233_countermeasures_after_handoff_01.md`

目的: 受け渡し修正(委任_42、commit `850cfe3f`)の後に残る問題への対策を、**Trial/検証用の範囲**でまとめて設計し、実装前にOpusの独立レビューへ出す。Fableが決めた設計の骨子は下記のとおり。あなたの仕事は、(1)骨子を現在のコードに当てて実現方法と影響範囲を具体化する、(2)各案の比較表を事実で埋める、(3)骨子に無理・矛盾・見落としがあれば、設計書の中に「Fable骨子への指摘」として明記する、の3つ。**骨子を黙って変えない。良い代替案があれば併記する。**

書き方: ユーザー(プロジェクト責任者、実装担当者ではない)が読んでも分かる日本語で書く。技術用語は最初に短い説明を付ける。各節の冒頭に結論を2〜3行で書き、詳細(関数名・行番号)はその後に置く。数値には出所(どの委任の、どのファイルか)を付ける。測定していないことは「未測定」「見積もり」と書く。

### 設計書の構成(この見出し順で作る)

**0. 前提とスコープ**: ユーザー指示の逐語引用、Trial専用であること、Production正式pathに触れないこと、今回やらないこと(文ID・文字オフセット方式、文単位スナップ、別AIの引用による救済、周回上限の単純な引き上げ、降格ルールの変更)。

**1. 現状の事実**(委任_41〜46の結果。作業1で保存した報告から、数値と出所を表にする)
- 受け渡し修正の限定Trial rep22の結果(T1/T2/T3、成功条件、T1 s2のStage 4の原因、T2のJA未解決2/2、T3の不具合と是正)。
- 特定不能35件の原因分類(句読点22/説明文混入12/省略記号1、言い換え0)。
- 周回2以降の新規BLOCKING 85行の原因内訳(見逃し34/書き換え起因20/重大度の揺れ15/取りこぼし8/判定不能8)。
- `meta_run03_standard`の「Also, some calls needed user information to continue.」(MUSE-HC-010)が正解ラベルでSafety-critical(Meta-1)であること、23実行中5実行で「残ったまま・未指摘・人間確認なしで終了」、Recheckでの検出は8回中4回、freshのStage 1では16実行中12実行で検出(委任_46 A-5の表から数え直して確認すること)。
- rep22のT1 4実行について同じ照合を委任_47が実施中。**結果は未確定なので、設計書では「委任_47で確認中」と書き、数値を推測で書かない。**
- 日本語側: 日本語本文はユーザーへ届かない、届くのは日本語タイトルだけで英語記事を入力にしない、英語見出しがBLOCKING指摘された例6行(触れる指摘16行)、JA関連の検査費用¥35.9(約13.9%)、Stage 4理由の最多が`ja_deviation_unresolved`(40件中11件)。

**2. 対策A: 受け渡し修正の追補**(委任_42の実装への差分。小さい順に)
- A1 末尾句読点の同値変換: Checker文字列の両端の句読点(`. , ; : ! ? 。 、`)を除いた文字列が、記事内にちょうど1箇所あれば確定とする照合段階を追加する(委任_45のC2、22行/3種類が解消する見込み)。確定範囲は「文の途中までの節」になる。**文単位スナップはしない**(ユーザー不採用)。水準①はその節を対象にし、解消できなければ既存の水準③(範囲を含む文)へ上がる。これが「再推測」ではなく「文字単位の同値変換」と言える根拠と、言えなくなる境界(例: 短い断片が複数箇所に一致する場合は確定不能のまま)を書く。
- A2 位置ラベルの誤確定の防止: `“In one line”`のような位置ラベルだけの文字列が、記事の区切り見出し(ラベル行)に一致して「確定」になる問題(委任_45 §2-4)。対策案を2つ以上比較する(例: 確定範囲が既知の構造ラベル行そのものと一致したら確定不能にする/ラベル行を照合対象の本文から除く)。この問題が`claim_in_article`の照合でも起きるか、`same_fact_id_locations`だけの問題かを、現在のコードで確認して書く。
- A3 同じ周回に同じ範囲を指す指摘が2件ある場合: 委任_42は`carry_forward_resolution`(先行指摘のRewrite対象に含まれていれば、後続指摘はRewriteを重ねず全文Recheckに任せる)を追加した。これはOpusレビュー#5の設計に無い追加機構。代替案「Rewriteの前に、確定範囲が同じ(または包含関係の)指摘をまとめ、1回のRewrite呼び出しに全部の`issue`を渡す」と比較する。比較軸: 後続指摘の`issue`がRewriteに伝わるか、Recheckの見逃し(検出率が5〜7割程度)に依存するか、追加LLM呼び出しの有無、実装の単純さ、fail-closedか。Fableの現時点の考え: 後続指摘の`issue`がRewriteに渡らないまま「書き換え済み」とするのは、Recheckの見逃しに依存するため弱い。まとめて渡す案を第一候補とするが、コード上の実現性を確認してほしい。
- A4 主体置換ガードの誤棄却: T2で水準③が、範囲の外・同じ段落に既にある語(`users`)を「新しい主体語」として棄却し、水準④(段落)まで広がった(2/2)。ガードの現在の判定範囲(関数名・行)を確認し、選択肢を比較する: (a)変更しない、(b)「新しい主体語」の基準を、書き換え前の同じ段落に既にある語は新規としない、に変える。**(b)は安全用のガードを緩める変更に当たるかどうか**(ガードの目的が「記事に無い主体を持ち込ませない」なら(b)は目的の範囲内、という読みが成り立つか)を、ガードの導入経緯(設計書・DECISION_LOGをGrep)から事実で書く。判断はFableとOpusが行うので、材料を示す。
- A5 省略記号「A ... B」(1行のみ): 実装しない(人間確認のまま)。理由を1〜2行。
- A6 委任_42が仕様外で判断した2点(delete型で範囲が文の一部のとき文へ拡張/JA本文でのみ確定しoriginがja_sourceでない指摘は確定不能)の妥当性を1〜3行ずつ。

**3. 対策B: Checkerの違反範囲の出力形式(Trial専用Prompt)**
- 骨子: Trial側のschemaに`violation_spans`(文字列の配列)を設け、**違反範囲の唯一の情報源**にする(委任_45のD-2)。各要素は英語記事本文からの逐語引用、1箇所=1要素、説明文・位置ラベル・接続語を入れない、指せない場合は空配列(→人間確認、fail-closed)。`claim_in_article`はコードが配列から組み立てて既存処理へ渡す。固定fixture(配列が無い)は、既存の`claim_in_article`から受け渡し修正の照合で範囲を復元するアダプタで読む。判定基準(何を逸脱とするか、severity、10種類のフラグ)は変えない。
- 委任_45のPrompt文案(§5-4)を土台にするが、**文案中の「文の一部だけが問題でも、その語句を含む文全体を引用してください」は採用しない**(ユーザーの「最初から文全体Rewriteへ広げない」に反するため)。代わりに「問題の語句だけを引用してよい。ただし記事内でちょうど1箇所に定まる長さにする」とする案を書き、短すぎて複数箇所に一致する危険とのバランスを検討する。
- `same_fact_id_locations`(同じ事実の他の箇所の列挙)との関係: 1つの配列へ統合する案と、別のままにする案を比較する。現在`same_fact_id_locations`がどこで使われ、どう照合されているか(受け渡し修正後のコードで)を確認して書く。
- 英語だけ修正(対策D)との関係: 引用は英語記事から行うよう指示する。日本語記事からの引用しか返らなかった場合の扱い。
- Stage 1初回とRecheckの両方に同じ形式を適用する方法(Trial専用の追記の仕組み: runnerの`SAFETY`以外の既存の追記ブロック、`build_deviation_schema_with_enumeration`、`build_recheck_schema`、`run_recheck`、er051のV4Aブロックを確認)。**er003(Production pathが使う)には触れない**ことを、呼び出し関係で示す。
- D-1(単一文字列の書き方だけ指定)・D-2・D-3(位置種別つき)の比較表(委任_45 §5-3を、現在のコードで再確認して更新)。
- 必要性の評価: 直近の特定不能は0件だが、実LLMのRecheckでは8/58(13.8%)が説明文混入型で、10行が「複数箇所のうち1箇所しか直せていない」。rep22での特定不能件数(委任_42報告では最終runで0件)も踏まえ、入れる/入れないの両方の根拠を書く。

**4. 対策C: 見逃しと重大度の揺れ**(周回を増やさず、1周目でまとめて検出する)
- C1(委任_44のE1): Trial専用Promptに「Ledgerの各factについて、記事内の該当箇所を全件確認する」手順を追記する。追加呼び出しなし。検出が増える見込みと、誤検出・書き換え・人間確認が増える危険。現在のChecker Promptに「全件列挙せよ」に当たる指示が無いことの確認(er003の該当行、Trial追記ブロック)。
- C2(委任_44のE2): 1周目の検査を2回行い、結果を合わせる(和集合)。同じ範囲・同じfactの指摘が両方にある場合の重大度は重い方を採る(安全側)。追加費用(1記事あたり、過去の単価記録から)、過去に「2×V4-Aの和集合」が不採用になった経緯(設計書・REPORTをGrep `union`/`和集合`で確認し、理由を逐語で引用)と、今回との違いがあるかどうか。
- C3(委任_44のE4): 重大度の揺れの記録(同じ範囲・同じfactの最終判定が周回間で変わったら記録する)。¥0、判定は変えない。
- C4: 降格ルールの変更(委任_44のE3a、`changed_scope`を降格の除外条件から外す等)は**今回やらない**。理由: 決定論的な安全ルールを緩める変更で、ユーザーのSTOP条件「Safety原則の変更が必要」に当たりうる。
- C5(選択肢として記載のみ): 重大度を安全側に固定する案(同じ範囲・同じfactが一度でもBLOCKINGになったら、以後の周回でも降格させない)。安全側だが書き換え・人間確認が増える。採否はOpusレビュー後にFableが判断。
- C1とC2の比較表: 検出率への効果(未測定なら未測定)、費用、非決定性、人間確認・不要な書き換えへの影響、実装の単純さ。**既存の記録から無料で推定できるものは推定する**: 例えば「同じ記事・同じ条件のStage 1/Recheckを2回取った組」が既存記録にあれば、2回の和集合でMUSE-HC-010などの見逃しがどれだけ減るかを数える(委任_46 A-5の表: freshのStage 1は16実行中12実行で検出、など)。推定に使える記録が無ければ「無い」と書く。

**5. 対策D: 英語だけを修正する構造(Trial runner内)**
- 骨子: 切替スイッチ(例 `JA_MODE = "english_only"`、既定は現行のまま残し、Trialで切り替える)を設け、english_onlyのときは次を行わない: `paired_rewrite`、日本語側の対応箇所の推定(5段)、JA Recheck、`ja_pending_deviation`、`ja_fail_open_guard`、日英等価チェック、JA側の指摘の統合、JA precheck。英語側のRewrite・Recheck・人間確認は変えない。
- Checkerへ日本語記事を渡し続けるか(D1: 渡す。originの区別に使う/D2: 渡さない)の比較。originの値が後段のどこで使われているか(english_onlyにした後も必要か)を現在のコードで確認する。
- 日本語記事からの引用しか無い指摘(英語本文に一致しない)の扱い: 確定不能→人間確認(fail-closed)とする案と、対策BのPromptで英語から引用させる案。
- 英語の見出しを書き換えた場合: 記録(`en_title_rewritten`等)を残す。日本語タイトルの作り直しは**Production正式pathの変更が必要なので今回やらない**(委任_46 C-4の候補1〜5を引用し、Production採用時のユーザー判断事項として1節にまとめる)。
- 外す処理ごとに、関数名・呼び出し箇所・外した場合に影響を受けるテスト件数(テスト名のGrepで概数)を表にする。削除ではなくスイッチで迂回する形にし、既存テストと旧方式(`HANDOFF_MODE=legacy`)が動き続けることを条件にする。
- Production採用時に必要になるユーザー判断(承認済みの「忠実英訳」「案B(JA差し戻し1回)」(`CURRENT_SPEC.md`、Grep `忠実英訳`と`案B`で該当行番号だけ確認)との関係)を、今回のスコープ外として明記する。

**6. 実装順序・相互作用・切替**
- 対策A〜Dの依存関係(例: Bの配列を入れるとA1・A2の必要性が変わるか、DとBの引用言語の関係、A3とC2[同じ範囲の指摘が増える]の関係)。
- すべてスイッチで切り替え可能にし、既定値は現行のまま(Trialで明示的に有効化)。固定fixtureとの互換。
- 必要なテストの一覧(実例ベース: 委任_45のU01〜U13、T3の同一範囲2指摘、T2の主体置換ガード)。

**7. 限定確認の設計(実行しない。設計だけ)**
- 予算: Phase累計¥494.03/総枠¥600、残り¥105.97(委任_42報告)。この残りで、(i)対策の限定確認と、(ii)その後の29件横断の再確認、の両方をまかなう必要がある。過去の29件横断の実費(REPORTまたは設計書をGrep `29`と`横断`で確認)を示し、(i)に使える上限を逆算する。**(i)+(ii)が残額に収まらない場合は、その旨と不足額を明記する**(ユーザーのSTOP条件「¥600予算上限超過が必要」に関わるため、Fableへ必ず報告)。
- 測るもの: ユーザー指示§3の5項目(特定不能率/検出漏れ/false PASS/出力失敗/Human Reviewへの影響、原文を引用)と、正解ラベルに対する「Safety-criticalな文が残ったまま人間確認なしで終了」の数、周回数、成立した水準、費用。
- 比較の組み方: 同じ記事・同じLedger・同時期に、対照(現行)と処置を取る。処置を一度に全部入れると原因が分けられないので、分け方の案(例: Stage 1単体で 対照/B/B+C1 を比較し、C2は対照の2サンプルから追加呼び出しなしで模擬する)を、呼び出し数と費用概算つきで2案以上示す。単価は既存の実測(委任_45 §6、委任_42のrep22実費)を使う。
- 対象記事の選び方: `meta_run03_standard`(MUSE-HC-010の見逃し)、複数箇所型(hormuz_run03_standard、neg1_meta_b3prod_a2、bgroup_B4、safety_A4)、Safety対照。n。
- 合否の基準案(Fableが決めるための案): 何が起きたらREJECTEDか(例: Safety対照で対照に無い見逃しが出る)、何を満たせばVALIDATEDか。

**8. 残るリスク・未確定点**

**9. ユーザーのSTOP条件への該当性**(6条件それぞれについて、該当/非該当/要注意と理由)

**10. Opusに特に見てほしい論点**(10項目以内。A3の2案、A4がガードの緩和に当たるか、Bの必要性と配列を唯一の情報源にする是非、`same_fact_id_locations`との統合、C1対C2、C5、Dの切り方、限定確認の組み方)

**11. Fable骨子への指摘**(骨子の無理・矛盾・見落とし。無ければ「なし」)

## 事前指定Read一覧

- 作業1で保存した`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_41〜46_result.md`(自分で作るファイル。設計書の事実の出所)。
- `DECISION_LOG.md`: Grep `委任_42` で位置特定 → ユーザー指示原文の範囲だけRead(全文Read禁止)。
- `docs/pm/design_open233_self_recovery_flow_01.md`: Grep `6-18` で位置特定 → §6-18(委任_42が追記)の範囲をRead。ほかはGrep(`和集合`、`union`、`主体置換`、`正解ラベル`、`Meta-1`)で該当範囲だけ。全文Read禁止。
- `docs/pm/opus_l2_review_open233_self_recovery_05.md`: 全文(Opusレビュー#5。構造把握目的、既にレビュー済みの範囲と今回の差分を区別するため)。
- `docs/pm/design_open233_violation_span_handoff_01.md`: Grepで§2-2(`violation_spans`)と§4-3(J1)の位置特定 → 該当範囲だけRead。
- `er052_open233_self_recovery_flow_runner_01.py`(commit `850cfe3f`時点、現在の作業ツリー): Grepで次を位置特定し該当範囲だけRead: `HANDOFF_MODE`、`resolve_violation_spans`、`vs_match_levels`、`vs_resolve_in_text`、`carry_forward_resolution`、`collect_replaced_units`、`rewrite_ranges_ladder`、`run_stage3_for_claim_spans`、`_run_stage3_spans_core`、`paired_rewrite`、`ja_fail_open_guard`、`ja_pending_deviation`、`SAME_FACT_ID_ENUMERATION_INSTRUCTION`、`build_deviation_schema_with_enumeration`、`build_recheck_schema`、`run_recheck`、`same_fact_id_locations`、`SAFETY_CRITICAL_CLAIM_DEFS`、主体置換ガード(Grep `actor`)、`apply_disclosure_gap_downgrade`、`FLOOR_FLAGS`、`MAX_CYCLES`。
- `er003_v1_en_direct_vfl_01_generate.py`: Grep `DEVIATION_PROMPT_TEMPLATE` → テンプレート範囲だけRead(編集しない。Production pathが使うことの確認用)。
- `er051_open233_checker_trial_variant_01.py`: Grep `V4A` → Trial追記ブロックの範囲だけRead。
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`: Grep `29` と `横断`、`§35`/`35.` → 29件横断の実費と§35の範囲だけRead。
- `CURRENT_SPEC.md`: Grep `忠実英訳` と `案B` → 行番号の確認だけ(本文Readは該当数行のみ)。
- `docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md`: 全文(63行。Opusの12観点。設計書がその観点に答えられる形になっているか自己点検するため)。

一覧外のReadが必要になった場合は、理由をRESULT_PACKETと最終メッセージに1行で記録する。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 上記Read一覧に書いたGrepパターンを使う。
- 追記・更新: 既存ファイルへの追記はしない。新規作成は設計書1点、報告保存の`_result.md`(最大6点)、委任ログ2点のみ。

## 実行コマンド全文

T-0:

C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_48.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_48.md_check.json

報告抽出スクリプトは、Claude Codeのscratchpad(`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\f9ae115b-0305-437d-ac2d-b452b22a5e2a\scratchpad`)に置いて`C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe`で実行する(リポジトリには入れない)。

テスト・回帰の実行は不要(コードを変更しないため)。

## SSOT追記文

なし(本委任はSSOTを編集しない。設計がOpusレビューを通り、実装に進む段階でFableが別途指示する)。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: なし。
- 明示`git add`対象(存在するものだけ。1ファイルずつパスを指定し、`-A`やディレクトリ丸ごとの指定は使わない):
  - `docs/pm/design_open233_countermeasures_after_handoff_01.md`
  - `docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_41_result.md`〜`_46_result.md`(作成できたもの)
  - `docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_43.md`、`_43.md_check.json`、`_44.md`、`_44.md_check.json`、`_45.md`、`_45.md_check.json`、`_46.md`、`_46.md_check.json`、`_48.md`、`_48.md_check.json`
  - `er052_output/open233_cycle_new_issue_analysis_01/analyze_01.py`、`results_01.json`、`cases_detail_01.csv`
  - `er052_output/open233_handoff_log_aggregation_01/classify_unverified_01.py`、`unverified35_classification_01.csv`
  - `er052_output/open233_missed_detection_truth_check_01/check_01.py`、`results_01.json`、`cases_01.csv`
- addしないもの: 委任_47のファイル、`ACTIVE_TASK.md`/`RESULT_PACKET.md`、既存のM表示ファイル、その他の未追跡ファイル。
- commit前に`git status --porcelain`でステージ内容が上記だけであることを確認する。違うものが混ざっていたらcommitせず報告する。
- コミットメッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 受け渡し修正後の対策設計案(受け渡し追補・Checker出力形式・見逃し対策・英語のみ修正)を作成、委任_41〜46の報告と分析成果物を保存。未実装・未Trial、Opus独立レビュー前(委任_48)`
- trailer: リポジトリの直近commitの慣例に従う(`git log -3 --format=%B`で確認)。
- `git push origin main`まで行う。競合・エラーが出たら自動解決せず報告する。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージの両方に、次を書く。

1. 結論(10行以内): 設計書の各対策の要点、Fable骨子への指摘の有無、予算が残額に収まるか。
2. 作業1: 保存できた報告の一覧(ファイル名)と、未保存のもの・理由。
3. 設計書の節ごとの要約(各2〜4行)。特に: A3の2案の比較結果、A4がガードの緩和に当たるかの材料、Bの必要性の両論、C1対C2の無料推定の結果、Dで外す処理の一覧、限定確認の案と費用概算、29件横断の過去実費と予算の収まり。
4. STOP条件への該当性(6条件)。
5. Opusに見てほしい論点。
6. 骨子どおりに書けなかった点、迷った点、未確認点(確認できたことと推測を分ける)。
7. T-0の結果、commit hash、push結果、変更ファイルのraw.githubusercontent.com URL(`https://raw.githubusercontent.com/shimomura055/eigo-radio/main/<path>`形式)、一覧外の追加Read。
