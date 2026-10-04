# Opus独立レビュー#15 保存記録
管理ID `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`、2026-10-05、条件A+C必須レビュー
packet `opus_packet_open233_production_wiring_01.md`、Opus追加Read約15万字
本文はFableセッション記録からスクリプト抽出(委任_04e)

# Opus独立レビュー#15(条件A+条件C、必須)OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01: rep30構成をProduction正式経路へ配線する設計

## 結論

1. **配線の要否**: 必要。ユーザーはrep30の構成をそのまま採用すると決めている。現行Production(MAJORならLocal Rewrite、尽きたらSTOP/NG_REVIEW)を残すと、採用済みの仕様が使われない。
2. **推奨構造**: 案Mを修正して採用する。
   - 新しいProduction moduleに入口を1つだけ作り(例: `run_self_recovery(ledger, en_text, ja_text, family_profile)`)、Feature flag(機能の入/切スイッチ)で制御する。Production初期値はOFF。
   - P1〜P5は「入力を渡す/結果を各familyの既存の終端に写す」だけの薄いアダプタにする。
   - `er010`は変更せず併存させる(DEV/Trialの20以上の呼出元を守る)。
   - Trial runnerは今回は新moduleへ切り替えない。rep30の再現性は、¥0の再生テストとprompt sha256一致で担保する(論点6)。
3. **K分類の要旨**

| K | 分類 | 要点 |
|---|---|---|
| K1 | 非競合 | ユーザーが「Rewrite上限後の判定専用cycle」とTを名指しで承認している |
| K8 | 非競合 | 兄弟箇所の把握は決定論処理 |
| K4 | 吸収可能 | 全文再生成はrep30に存在しない。残す方がrep30との不一致になる |
| K7 | 本物のユーザー判断 | CURRENT_SPEC L2329〜2330が「Routing変更は別途ユーザー判断」と明記している |
| K14 | 条件付き | 配線前の小さな実測で決まる。rep30のStage 1は単一構成ではなく、Safety-criticalのB3検出はProduction V0出力への差替えで成立していた(下記) |

4. **Fableの「実装前にSTOPしてユーザーへ報告」方針は妥当**。ただしSTOP理由の中心はK7(+K14の測定結果次第)。K1/K4/K8を「構造的競合」としてユーザーへ投げるのは過剰。Fableが設計判断し、報告で開示すれば足りる。

### 新たに確認した重要な事実(Gap文書に無い、またはGap文書を訂正するもの)

- **(F1)rep30でのStage 1差替え**: B2_hormuz s1、B3 s1、B3 s2の3 runは、凍結したV4A出力が見逃していた。そのため、Trial専用の`substitute_baseline_on_stage1_miss`でProduction V0(vfl01)の実出力に差し替えて走っていた。
  - 根拠: runner L7686、L8192〜8200。`summary_kpi_01.json`の`stage1_recall_miss_substituted: true`が3件。
  - B3はSafety-critical登録(CURRENT_SPEC L2369)。つまり**rep30の「重大見逃し0」のうちB3分は、Stage 1が上記の差替えで成立している**。
- **(F2)V4Aの昇格ルールはrep30の流れに効いていない**: Trial Checkerの「post-hoc昇格ルール」(`classify_deviation_trial`、er051 L76〜159)は`severity_final`を付けるだけ。runnerは`severity == "MAJOR"`だけをStage 2へ渡す(L8269)。runner内の`severity_final`参照は0件(Grep)。
  - Gap §6-1の「Trial Checkerは昇格ルールを上乗せ」は、実際の挙動としては誤り。
  - **Productionへ昇格ルールを入れるとrep30と不一致になる**ので、入れないこと(より厳しくはなるが、未検証)。
- **(F3)Stage 1が非検出だと決定論floorも走らない**: Stage 1が`LEDGER_DEVIATION`でなければ、その時点で`ACCEPTABLE_STAGE1`として終了する(L8203〜8235)。precheckの決定論floorはこの後(L8317)にしか実行されない。
  - 新flowでも、**Stage 1の検出力(recall)が唯一の入口**。現行Productionも同じなので悪化ではないが、K14の重みはここから来る。
- **(F4)凍結した35件のStage 1出力の生成元**は`er051_output/.../trial_02/step1|step2/.../V4A/run_1.json`(L7655〜7698)。
  - 重大誤解原則のdeveloper message(委任_30で既定化)が付いていたかは未確認(推測: 付いていない)。
  - したがってrep30のStage 1は「V4A(原則なしの可能性)×凍結35」「V4A+原則+列挙×新規実行3」「V0差替え3(35の内数)」の混成。**rep30は「Stage 1の出力を所与とした後段の検証」と解釈するのが正確**。

## 論点別判定

### 論点1 K14(最重要)【判定: 条件付き(配線前の実測で決める)。設計案(ア)を修正して採用】

- **Stage 1の構成**: Productionの初回Checkerは、rep30で新規実行時の既定構成にそろえる。具体的には、V4A追加promptブロック+重大誤解原則のdeveloper message+列挙instruction+schemaの追加フィールド。昇格ルールは除く(F2)。
  - これは`vfl01.run_deviation_check`へのopt-in引数(指定しない限り不変)として入れる。既存の前例: vfl01 L708〜、L782〜787の`prior_issues`等の方式。40超の呼出元は不変のまま。
  - 理由: 新規実行時のStage 1はrunnerの既定(L8140〜8148)であり、Productionは常に新規実行になる。この既定はrep30で有効だった仕様に含まれるので、ユーザーの一括採用範囲内と読める。Checker変更だから新しいProduct判断、とはならない。
- **(イ)vfl01をそのまま使う案は推奨しない**。既知の弱点として、changed_actorのflagが立ってもseverityがMINORのまま、という現象がある(gpt-5.6-luna+V0で0/6、DECISION_LOG L12872〜12875)。MINORはStage 2へ渡らないので、この弱点がそのまま残る。
- **ただし(ア)にも劣後リスクがある**: 凍結したV4Aは、V0が検出していたB2_hormuz/B3を見逃している(F1)。**配線前に次の実測を必須にする**(推定¥3〜6、gpt-6-luna)。
  - 対象: Safety-critical 5件(B3・B4-a・A2A3-0・A4-0・A5-0)+B2_hormuz+Safety12(er009の9種)+負例2〜3件。
  - 方法: Production候補のStage 1構成でn=2の新規実行を行い、V0の記録出力と比べる。
  - 判定: V0が2/2で検出し、候補が0/2のclaimが1件でもあれば、STOP条件「既存Production品質を明確に悪化させる」/「初回pathへ安全に入れられない」に該当し、本物の競合(ユーザー判断)になる。その場合の選択肢は、V0を維持(未検証の組合せ)、V0とV4Aの併用(和集合。新設計なので不採用寄り)、劣後を受容、の3つ。
  - 劣後がなければ吸収可能。
- **「一致」と言うために最低限測るもの**:
  - (a)¥0: 新moduleが組み立てるStage 1/Stage 2/Recheck/Rewriteのpromptのsha256が、rep30の`call_log.prompt_sha256`と一致すること。
  - (b)¥0: 後段の決定論部分(span解決・floor・ladder範囲・許可リスト判定・BLOCKING固定・再利用判定)について、rep30の記録入力で同値になること。
  - (c)上記のStage 1実測。
  - (d)Production正式pathで、新規Stage 1から許可リスト出口/PASSまで通すruntime evidence。

### 論点2 K7(モデル)【判定: 本物のユーザー判断。推奨=選択肢1】

選択肢(ユーザーへ提示):

1. **(推奨)Self-Recoveryの経路だけ`gpt-6-luna`にする**
   - 内容: Stage 1 Checker、Stage 2、S1、floor_verify、Rewrite、Recheckを`gpt-6-luna`にする。Writerは`gpt-5.6-luna`のまま。Model Routing Contractに新しいprocess(例: `SELF_RECOVERY_CHECK`/`SELF_RECOVERY_REWRITE`)を追加し、`require_model`経由にする。モデルが使えないときは`api_failure`で止め、`gpt-5.6-luna`へ自動で切り替えない(未検証の組合せになるため)。
   - Safety: rep30と同じモデル。V7bの再較正・時期の単体確認・S1は、すべて`gpt-6-luna`で取れている。
   - 費用: Checker単価が下がるため、現行Productionより安くなる見込み。
   - 工数: 小(Contract表・`PROCESS_MODEL_MAP`・テスト・静的監査)。
2. **全部`gpt-5.6-luna`にする**
   - Contractは変わらない。
   - ただし、V7b・floor_verify・S1の較正はモデルに依存するため、結果は無効になる。再較正と全体の再検証が必要で、実質は新しいTrialになり、ユーザー決定「追加N増しTrialは不要」と衝突する。
   - 費用は単価で入力2倍・出力2.4倍。reasoningの出力が多いため、2.2〜2.4倍寄りになる見込み(推測): 平均約¥1.2〜1.4/run、worst約¥9〜10。
   - 推奨しない。
3. **混在(Stage 2以降だけ`gpt-6-luna`)**: rep30の構成を分解することになり、不採用寄り。

- **費用の見積り方(¥0)**: rep30の38 runの`call_log.usage`を両方の単価で再計算すれば、推定ではなく確定値が出る。
- **KPIの基準**: Productionの平均追加費用は「現行Production(vfl01+er010のloop、gpt-5.6-luna)の1記事あたり費用」を基準に定義し直す必要がある(rep24との比較はTrial内の指標)。既存の`raw_usage_log`から¥0で算出できる。
- **SSOTの細かい不整合**: CURRENT_SPEC L2330の「正確に半額」は出力単価($0.50 vs $1.20)では成り立たない。SSOTを直すだけでよい。

### 論点3 K4(Family X)【判定: 吸収可能(Fableが判断し、報告で開示)。採用案=must-fixによる全文再生成はSelf-Recoveryの経路では廃止】

- **全文再生成を廃止してよい理由**: rep30のFamily X fixture(hormuz/meta)は、全文再生成なしでladder→T→許可リストという流れで検証されている。全文再生成を残す(Self-Recoveryの前でも、ladderが尽きた後でもTの前でも)と、検証されていない経路を足すことになり、「rep30と一致」に反する。
  - Self-Recoveryの前に置くと、本文が丸ごと変わり、位置の状態も費用もリセットされる。
  - ladderが尽きた後に置くと、Human Review出口の代わりに未検証のloopが入る。
- **段落数のガード(必須)**: ladder④(段落Rewrite)とT(文の削除)の後には、毎回`split_family_x_article_text_v2`を実行する。`status!="OK"`なら、そのRewriteを不成立として扱い、元に戻してladderを一段上げる(STOPにはしない)。上げる段が無ければ、構造要素扱いの検証付きで`blocking_structural_after_ladder`とする。
- **変更しないもの**: 逸脱チェック前の段落数retry(`_family_x_ensure_split_or_paragraph_retry` L294)は別の軸なので残す。
- **`JARecheckRequiredError`の扱い**: 承認済みの`JA_MODE=english_only`とrunnerの`english_only_ja_source_requires_full_recheck`(L7249)に従い、ja_source由来のMAJORは英語側だけ直し、その周回は全文Recheckを必須にする。rep30はhormuz_run01/02_advanced(現行ProductionでSTOPした実例)をこの方式で解消している。
  - 開示が必要な点: 日本語側の誤りは残る。日本語本文がユーザーに表示される製品かどうかは未確認。「英語だけ修正」の承認範囲内だが、報告にはその帰結として1行書くこと。
  - `ja_source`の検出件数は監査ログに記録してmonitorする。
- **終端の扱い**: Family Xの許可リスト出口は、既存の`RuntimeError("[STOP] ...")`に理由コードを付けて写す。operatorの運用(STOPしてから手で対応)は変えない。

### 論点4 K1(cycle上限)【判定: 非競合。Trialの定義をそのまま採用】

- 新moduleの定数はrep30どおり、`MAX_CYCLES=2`+条件付きcycle 3、その後に判定専用cycle、T(1記事1回)とする。`er010.MAX_REWRITE_CYCLES=3`は旧経路用として据え置く。
- ユーザー指示にはこれらが名指しで含まれており、新しい再定義ではない。
- **開示が必要な点(確認)**: cap後のT(L8598〜8601)は削除による本文変更である。最悪の場合、ladderの3回+Tの1回で、本文を変える処理が計4回になる。Tは承認済み(「非構造要素の最終手段処理」)だが、CURRENT_SPECには正確に書くこと。

### 論点5 K8【判定: 非競合】

- cycle 1の兄弟箇所把握は、`same_fact_id_locations=None`に上書きしてから決定論で列挙する(L8297〜8313)ため、Checkerの出力に依存しない(確認)。
- 新規実行のStage 1が持つ列挙フィールド(`expand_same_fact_id_locations`、L1732)は、rep30の新規実行時の既定。opt-inのschemaに含めれば一致する。
- 不採用とされた`violation_spans`は別の仕組み。しかも記録上はFableの判断で、ユーザーの逐語は見つかっていない(Gap §6-3)。

### 論点6 アーキテクチャ【判定: 案Mを修正して採用】

- **入口と出力**: 入口は1つ。戻り値は`{status: PASS | HUMAN_REVIEW, reason∈4種, sub_reason, audit}`。4種以外の理由が出たら`AssertionError`で安全側にSTOPし、バグとして扱う(property testで0件を保証)。
- **アダプタの責務**: P1〜P5の各アダプタは「Checkerの文脈(hook_aware、source_article_text等)の受け渡し」と「終端への写し方」だけを持つ。
  - P1/P2: `RuntimeError` STOP
  - P3/P4: `NG_REVIEW_REQUIRED`
  - P5: 戻り値のflag
  - P3〜P5で複製されている3つのloop本体は、flagがONのときは新moduleの呼出しに置き換わる。
- **retry/fallback/regenerationの扱い**: どれも新しい本文を作るので、同じ入口へ新規実行のStage 1から入り直す。対象は、手動CLIの`--regenerate-stage`、Stage 1 QA再生成(K5)、段落数retry。全文再生成のときは、位置履歴とTの使用回数をリセットする(本文が新しいため)。費用は累積で報告する。
- **Trial依存を作らないこと**:
  - Production module側は`er05x`をimportしないことを`git grep`で機械的に検査する。
  - 同値テストだけはテストファイルからrunnerの関数を参照してよい。ただしProductionの回帰テストとは別名にする。
  - Trial runnerを新moduleへ切り替えるのは別タスクにする。
  - 誤配線の防止: V7bの正本は`s2c` L612を使う。`s2p.MATERIALITY_RUBRIC_V7B`は別物なので使わない(Gap §2-5)。

### 論点7 Production Gateの意味が変わることのSafety【判定: 非競合(承認の中核)。条件付きで採用】

- **「AI1回で重大→問題なし」の禁止は保たれる(確認)**:
  - 主体/数値/否定/比較のflagと、因果known6は決定論でBLOCKINGを維持する。
  - 時期は追加確認2回が両方逐語で非BLOCKINGのときだけ解放する。
  - MAJORを降格するにはS1で2回一致が必要。
  - 本文が変わらない限りBLOCKINGを固定する。
- **条件**:
  - (i)これら4つの仕組みは必ず同時に配線する。
  - (ii)Stage 1のMINORは後段へ渡さない(rep30どおり)。ただし、Stage 1が非検出だった記事でもprecheckの結果をログに残す(¥0、挙動は不変)。将来の検出力改善の材料になる。
- **既存6出口と新出口の対応(推奨)**

| 既存の出口 | 新しい扱い |
|---|---|
| locateがNone(P3〜P5) | span fallbackの連鎖→持ち越し→`blocking_confirmed_unlocatable_after_cap` |
| `NG_REVIEW_REQUIRED`(cycle切れ) | 判定専用cycle→T→`post_T_new_blocking`、unlocatable、またはstructural |
| Family X再生成後のMAJOR | Self-Recoveryの経路へ |
| Family X再生成後に段落数<3 | 再生成を廃止。段落数ガード→ladder |
| `JARecheckRequiredError` | english_only+全文Recheck |
| Stage 1 `qa_exhausted` | 逸脱の出口ではなく品質の軸なので残す(K5) |

### 論点8 部分配線・順序【判定: 機能ごとの部分配線は不採用。family単位でまとめて有効化する案を採用】

- 開発中はflag OFFで、Productionは旧経路(現状の品質)のまま動かす。**仕組みの一部だけをProductionで有効にする中間状態は作らない**。
- 新moduleを全部そろえてから、familyごとに「integration test+runtime evidence」を済ませ、flagをONにする。各familyには検証済みの構成一式が入るので、中間状態でもSafety holeは生じない。
- 中間状態のStatusは`APPROVED_FOR_PRODUCTION`(配線未完)でよい。動いているのは旧経路だから。`PRODUCTION_WIRED`は全family完了後。
- familyの順序: P3/P4(Local Rewrite系、構造が単純)→P5→P1/P2(再生成の廃止とJA関連の変更があるため最後)を推奨する。ユーザーに聞く必要はない。

### 論点9 runtime evidence【判定: 修正して採用。新規記事は不要】

- **Phase 0(¥0)**: prompt sha256の一致、決定論部分の同値性、費用の再計算。
- **Phase 1(配線前、約¥3〜6)**: 論点1のStage 1実測。
- **Phase 2(配線後、Production正式path、8〜10 run)**:
  - (a)Family Xの既存テーマを`--regenerate-stage`で再生成(Advanced+Standard、実writer)。
  - (b)現行ProductionでSTOPした実例(hormuz_run01_advanced、ja_source)の本文をP1アダプタへ入力。
  - (c)P3・P4・P5を既存テーマで各1回。
  - (d)Safety fixture 3件(時期floor_verify/因果+S1/構造title)をProductionの入口・routing経由で通す。
  - (e)上記のうちクリーンにPASSする例を最低1件。
  - (f)fixtureで¥0確認: cap/T 4経路/unlocatable/API failure/許可リスト外の理由/段落数ガード。
- **費用の推定**: 選択肢1なら、writer費用込みで¥20〜40(推定)。新規テーマは不要(既存テーマの再生成で足りる)。
- **P6の扱い**: P6の位置づけが決まるまで、「全経路」の主張はできない(下記「十分に答えられなかった点」)。

### 論点10 SSOTの整備【最小範囲】

CURRENT_SPECのOPEN-233節に「Self-Recovery Production Flow仕様」を1節新設する。内容:

- 入口の条件
- Stage 1の構成(opt-inの中身、昇格ルールを除くこと)
- モデル/routing(K7の決定後)
- V7bの正本(s2c L612)
- floor 5種+known6+issue_actor
- 時期のみのfloor_verify
- S1の定義(`floor_verify`で解放済みのclaimを除外。K13の読替)
- BLOCKING固定と再利用
- 兄弟箇所(決定論)
- span解決L0〜L6とP-strict-closed
- ladderの水準①③④(⑥はOFF)
- 位置の引継ぎとrevert guard
- AG1-strict
- 構造要素
- cycleの定義(T後に本文変更が計4回になりうることを含む)
- 許可リスト4理由+sub_reason+familyごとの終端への写し方
- english_onlyと`JARecheckRequiredError`の廃止
- Family X全文再生成の廃止と段落数ガード
- Cost KPIの基準の再定義

あわせて、DECISION_LOGにFableの設計判断を記録し、OPEN_ITEMSの`OPEN-233-A1-PROD`必須9項目を更新する。K7の決定前に書けるのはK7に関係しない部分だけ。

### 論点11 総合

| K | 分類 | 推奨 |
|---|---|---|
| K1 | 非競合 | Trialの定義を採用し、開示する |
| K4 | 吸収可能 | 全文再生成を廃止、段落数ガード、english_only。開示する |
| K7 | 本物のユーザー判断 | 選択肢1 |
| K8 | 非競合 | rep30どおり |
| K14 | 条件付き | Phase 1の結果次第。劣後があればユーザー判断 |
| K3/K5/K13 | 非競合または吸収可能 | 上記のとおり |

## Safety hole

1. **(F1)B3等のStage 1検出が未証明**: Production候補のStage 1で、B3・B2_hormuzの検出が実証されていない。Phase 1を行わないと、Productionの見逃しリスクが不明なまま。
2. **(F2)昇格ルールの誤配線**: Gap文書どおりに「Trial Checkerの追加分すべて」を入れると、効いていない昇格ルールまで有効になり、rep30と不一致になる(厳しくなる方向で、未検証)。
3. **未検証経路(§4-4、L8593〜8597で確認)**: T使用済み/T無効のとき、構造要素かどうかを検証しないまま`blocking_structural_after_ladder`が返る。結論がHuman Reviewになるのは安全側だが、理由名が事実と合わない。
   - 推奨: top-levelの4理由は変えずに`sub_reason`(例: `t_already_used`、`t_delete_failed`)を必須にし、4つの強制経路をfixtureで確認する。
   - funnelや次cycleへ戻す案は、cap違反と無限loopの危険があるので不採用を推奨する。
4. **Family Xのladder④とT**: 段落数・In one lineを壊す可能性がある。段落数ガードが必須(論点3)。
5. **モデルが使えないときの扱い**: `gpt-5.6-luna`へ自動で切り替えると未検証の組合せになる。Fail-Closedで`api_failure`にすること。
6. **4種以外の理由が出たとき**: 必ずSTOP(安全側)。

## ユーザー判断が必要な点

1. **K7(モデルroutingの変更)**: 選択肢1/2/3と、それぞれの費用・Safety・工数(論点2)。推奨は選択肢1。
2. **K14の条件付き判断**: Phase 1で劣後(V0は検出、候補は非検出)が出た場合のみ。選択肢はV0を維持/併用(和集合)/劣後を受容。
3. **判断ではなく開示でよいもの**(報告に記載): K1(Tによる計4回目の本文変更)、K4(全文再生成の廃止、`JARecheckRequiredError`の廃止と日本語側の誤りが残ること)。

## STOP条件(8項目)の該当

| STOP条件 | 該当 | 根拠 |
|---|---|---|
| 構造的競合 | 該当する | K7。K14は条件付き |
| 初回pathへ安全に入れられない | 未確定 | K14、Phase 1次第 |
| retry/fallbackとの仕様矛盾 | しない | 論点3・論点6で吸収できる |
| 新しいProduct判断が必要 | 該当する | K7(CURRENT_SPECにRouting変更は別途判断と明記) |
| runtimeでの重大見逃し/Human Review | 未実施 | runtimeはまだ動かしていない |
| 平均費用の大幅悪化 | しない | 選択肢1の場合。選択肢2なら約2.2〜2.4倍 |
| 既存品質の明確な悪化 | 未確定 | K14 |
| 改善ループ4回目 | しない | |

## 追加で読んだファイルと概算文字数(合計約15万字)

- `docs/pm/production_wiring_gap_open233_01.md` 全文(約4.5万字)
- `er012_e_family_entertainment_two_level_runner_01.py` L370〜529(約0.9万字)
- `CURRENT_SPEC.md` L2291〜2429(約2.5万字)
- `DECISION_LOG.md` L18785〜18894、L12862〜12891(約0.6万字)+Grep
- `er051_open233_checker_trial_variant_01.py` L55〜189(約0.6万字)
- `er052_open233_self_recovery_flow_runner_01.py` L1672〜1751、L7228〜7257、L7640〜7744、L8090〜8329、L8440〜8609(約3.5万字)+Grep
- `er052_output/open233_self_recovery_flow_runner_01_rep30/summary_kpi_01.json`(Grep)
- `er006_model_routing_contract_01.py`(Grep)
- `docs/pm/opus_l2_review_open233_kpi_recovery_02_14.md`(見出しのみ)

## 十分に答えられなかった点

- **P6**(`er012_b_family_production_runner_01`、`voices_a2_production`、`er009_n1_diagnostic`): MAJOR時の挙動が未確認。配線対象かどうか(check-onlyなのか、MAJORのまま出荷する経路なのか)を¥0の棚卸しで決めるまで、「全経路」の完了条件は判定できない。
- **凍結V4A出力の生成条件**(重大誤解原則の有無、モデル)が未確認(F4は推測)。
- **¥0の再生テストの可否**: rep30が各callのLLM生出力まで保存しているかは未確認。保存していなければ、同値性は決定論部分とprompt sha256に限られる。
- **Family Xの日本語本文がユーザーに表示されるか**: 論点3の開示文の重さに関係する。
- **Closeout時の未解決3点**(`issue_focus_absent_recheck_only`、「and」版ACCEPTABLE等)の個別評価は今回行っていない。
- **選択肢2の費用**は推定。rep30の`call_log`で再計算すれば確定する。

Opusは採用可否を判断しない。Production採用を決めるのは人間ユーザーのみ。
