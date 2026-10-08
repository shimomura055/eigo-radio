# DESIGN_E2E_01 (v2): FACTLOCK-ASTRA-E2E-TRIAL-01 設計書(v1=委任_01 2026-10-09、v2=委任_03 2026-10-09)

性質: Trial/DEV。到達上限Status=`DESIGN_READY`(実行Go未)。本書作成時点のAPI生成支出=¥0、Production変更なし、既存コード・Prompt・CURRENT_SPEC.md・OPEN_ITEMS.md無編集。`APPROVED_FOR_PRODUCTION`ではなく、E2Eの結果も`MEASURED`止まりでProduction採用は人間ユーザーのみ承認する。
本書の数値は、出典を併記したものだけを「実測/確認済み」とし、それ以外は「見積」「推定」「未確認」と明記する。USD/JPY=160(astra単価正本と同じ)。

## 改訂履歴
| 版 | 日付 | 内容 | 反映元 |
|---|---|---|---|
| v1 | 2026-10-09 | 初版(委任_01) | ユーザー決定1〜5 |
| v2 | 2026-10-09 | 案B新腕=B1(新Writer再実行で回復)、B3注記を全10記事で新仕様再注記、影の対照を両腕化、Production等価性(shadow_stop・人手介入必要率)、G0照合拡張、横断予算予約・×1.5係数、G1拡張、即停止条件追加、中間チェック、ゲート順更新、8節をOpus結果の採否表へ置換 | ユーザー決定6〜8(下記0節)、Opus条件Aレビュー論点1〜8(`docs/pm/opus_a_review_factlock_astra_e2e_01.md`、Fable採用判断済み) |

v2の変更点の箇所対応(論点N=Opus論点番号、決定N=ユーザー決定番号): 2節W4b/W5/B1=論点2・3・決定6 / 2節「注記」=決定7・論点5 / 2-1スイッチ表=論点2 / 3節=論点1・4・8 / 4節(c)(c2)(d)(h)(i)(k)(l)(m)(n)=論点1〜5・7 / 5-0ゲート・5-1割付・5-2停止・5-3失敗扱い=論点2・3・7 / 6節=論点1・2・7の費用 / 7節=論点5・6 / 8節=Opus採否表。

## 0. ユーザー決定
### 0-1. 2026-10-09(1回目、v1で記録済み)
1. 10記事 / TTS 2本 / 予算上限¥1,000(途中停止を避けるため¥700から引き上げ)。
2. Astra=Standard同期(Flexは別評価、Batchは対象外)。
3. M2は見送り(OFF維持)。
4. 旧4テーマ(META/ホルムズ/宇宙兵器/ミニバッグ)+新6テーマ(候補提示→ユーザー選定)、全記事で旧仕様腕を併走(paired)。
5. 設計書作成へGo(「OKです。開始してください。」)。**実行(API支出)はGo未**。

### 0-2. 2026-10-09(2回目、v2で追加。DECISION_LOG末尾に記録)
6. **案B(JA再確認)の新腕の扱い=B1採用**: 新腕は「新Writerの再実行」で回復する(Fact Lock R0に既存must-fixブロック`original_must_fix`を付けて再生成→Astra R1→R2[系列X逐語]→後処理→EN再実行)。1記事1回まで、Trial全体の上限3回(見積約¥105)、超過はSTOP記録。
7. **B3注記仕様をTrial前に正式なTrial仕様として先に固定する**(ユーザー逐語は委任_02の委任文`docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_02.md`に保存。要旨=都度判断の注記では記事ごとに条件が揺れFact Lockの性能が測れない。何を【事実N】とするか/複数要素の分け方/重要数値の定義/数字が主役の場合/名称内番号/台帳由来制約/迷った場合/注記後の照合、を固定し、旧4+新6の全10記事を同一仕様で**再注記**する)。手順: B3注記仕様作成(¥0)→Opusレビュー→ユーザー提示・確認→E2E実装・実行。
8. 新6テーマの選定は**未回答**(候補10件は`NEW_THEME_CANDIDATES_01.md`で提示済み)。

## 1. 目的・評価対象・指標・比較対象

### 1-1. 評価対象と比較対象
| 評価対象 | 何を見るか | 比較(新=新仕様腕 / 旧=旧仕様腕) |
|---|---|---|
| (1) Writer変更 | Fact Lock R0[Luna]+Astra R1→R2[系列X]が、旧Production Writer(Luna R0→R1→R2)より日本語記事のFact品質を良化するか(面白さは副指標) | 同一台帳・同一B3から生成した新R2 対 旧R2(同時にfresh生成) |
| (2) 翻訳仕様変更(M1/M3) | 要約へのJA+Ledger入力と要約のみ再生成(M1)、changed_actor候補の再分類保護(M3)が、EN段の重大/軽微NG・STOP率を良化するか | 新EN(M1/M3 ON) 対 旧EN(全OFF)。**JA本文が腕で異なるため(1)と交絡する。分離は3節の影の対照テレメトリ(両腕、v2)** |
| (3) Checker | 重大/軽微の件数、Rewrite率、Human Review率、費用 | 新腕 対 旧腕(同一Checker構成: 承認スイッチ`OPEN233_APPROVED_FLOW_SWITCHES`、`FLOOR_MODE=number_only`。M3だけ新腕のみON) |

旧仕様腕=「現Production経路」: 同一台帳・同一B3から`er019_family_x_entertainment_production_runner_01.py`のWriter(`jaw.run_ja_writer_o_r1_r2`、gpt-6-luna)→EN(M1/M2/M3全OFF)→Checker。

旧4テーマ(META/ホルムズ/宇宙兵器/ミニバッグ)は、上記の同時fresh旧腕に加えて**過去の凍結出力とも並記**する(参考のみ、条件が違うため判定には使わない)。
- Checker: `er052_output/open233_prod_e2e_02/`(REPORT §81の新仕様9 run。meta_run03_advanced/standard、hormuz_run03_advanced/standard等。実測合計¥31.519、平均¥3.502/run、平均345.5秒/run[`e2e_summary_02.json`])。旧仕様の9 run(frozen)は§81-2〜§81-5の「旧9 run」列。
- Writer: Fact Lock v1の24本(`er052_output/factlock_writer_trial_01/runs/`、`RESULT.md`)、all6/baselineの44本(`er052_output/all6_writer_redesign_necessity_01/runs/`)、Astra Revise matrix(`astra_revise_matrix_01/02`、REPORT §107・§108)。

### 1-2. 指標定義(REPORT §81の集計表と同じ行立て)
集計単位=「1記事の1腕」。Advanced(Family X忠実英訳)とStandard(A2)は別のChecker runとして数え、記事×腕あたり2 run、全体で最大40 run(10記事×2腕×2レベル)。表は§81-2〜§81-5と同形で、新腕/旧腕の2列+差分列。

| 区分 | 指標 | 定義 | 定義元 |
|---|---|---|---|
| A | Checker初回候補 | AI判定の候補(延べ)/うち真に問題(Y)・不要(N)・判断不能/機械判定の候補/重複除外後の総候補/再分類で除外されたclaim数 | §81-2 |
| B | 後段判定 | Stage 2のAI 重大/軽微/問題なし、事後評価の真に重大・不要に重大・真に重大なのに軽微/問題なし、機械判定(数字のみ)の発火と重複、S1 second opinionのBLOCKING化 | §81-3 |
| C | Rewrite率 | Rewrite発生件数/発生run数(分母=Checker run数)、必要/不要の別、再修正が必要だった件数 | §81-4 |
| D | Human Review率 | 出口BLOCKINGありでHuman Review/STAGE4へ到達したrun数 ÷ Checker run数 | §81-4 |
| E | Safety・Cost | 真の重大Fact見逃し(最終本文に未修正で残存)、重大Fact検出(最終本文までに修正)、run別費用・合計・平均、Checker/後段/Rewrite別費用 | §81-5 |
| F | 重大/軽微(最終記事) | 最終EN本文・最終JA本文に残る重大/軽微の件数(記事あたり)。盲検ラベル(7節)による。重大/軽微の線引きはPREREGISTRATION_01.mdで固定 | PREREGISTRATION_01.md |
| G | JA Writer(1) | JA R2のFC(Luna、全台帳、`run_deviation_check(hook_aware=False, include_related_fact_id=True)`)MAJOR/MINOR、決定論指標(字数・段落・問い・記号Gate・台帳外数値)、盲検ラベルの重大/軽微 | astra_revise_matrix_02/DESIGN.md「評価」節 |
| H | EN段(2) | EN deviation check初回のMAJOR数(由来translation/ja_source別、要約/本文別)、EN STOP率(M1後を含む)、M1発火数と解決率、盲検ラベルのEN由来NG | OPEN-243 ANALYSIS_01 §3 |
| I | M3(2) | 保護されたclaim件数、その後のStage 2判定(BLOCKING/QUALITY/ACCEPTABLE)、Rewrite誘発件数と必要/不要 | RESULTS_M123.md V3 |
| J | 副指標 | 面白さ(新R2対旧R2のpairwise、LLM判定+人間確認2〜3記事)、字数、所要時間、記号Gate | RESULT.md §1〜§2 |
| K(v2) | 初回JA_RECHECK率(回復前) | 初回(回復前)にJA_RECHECK相当が発生した記事数 ÷ 10(両腕)。旧腕=`JARecheckRequiredError`捕捉時点、新腕=EN段の`JARecheckRequiredError`捕捉時点。回復後の最終状態とは別に記録 | 論点2 |
| L(v2) | 人手介入必要率(複合主指標) | (JA STOP+影STOP+EN STOP+Human Review)÷予定run数(各腕20)。両腕同一定義(下記1-3) | 論点3 |
| M(v2) | 新規具体主張(ii) | 両腕のJA最終本文に`untagged_check`の`new_specific_claim`検出器(約¥0.2/本)を適用した件数(定義: astra_revise_matrix_01/02 DESIGN.md)。R0との増減も記録 | 論点6 |
| N(v2) | shadow_stop・B1回復 | 新腕のR2後FC MAJORの`shadow_stop`件数、B1回復の発動数/成功数、旧腕の案B(Luna再生成)発動数 | 論点3・決定6 |

### 1-3. v2で固定する定義(本書の定義案、Fable確認要の箇所は明記)
- **分母**: 各腕の予定Checker run数=20(10記事×Advanced/Standard)に固定。STOPで到達しなかったrunは分母に残し、独立カテゴリ「STOP」に入れる(「Rewriteなし」「Human Reviewなし」に混入させない)。記事単位の指標(初回JA_RECHECK率、EN STOPのレベル別率等)の分母は10記事(レベル別)。
- **人手介入必要率の数え方(定義案)**: 記事単位のSTOP(JA STOP・影STOP)は当該記事の予定Checker run 2本分、EN STOPは該当レベル1 run分、Human Reviewはrun単位。同一runを重複計上しない(1 runは最大1回)。
- **影STOP(定義案)**: 新腕のR2後FC MAJORに付く`shadow_stop=true`のうち、B1回復後(または回復枠切れ)にもR2 FC MAJORが残った記事。Productionなら止まる記事に相当する。記号Gateの残存は記録のみで影STOPにしない(残存はTTS対象2本で確認)。

## 2. 処理フロー(1記事、v2)

```
[Stage R: 新6テーマのみ] research+ledger+B3 (web_searchあり、1テーマ1回、両腕で共有)
   ★注記の前提になるため、注記より前に実行する必要がある(8-3節の判断事項)
[共有: テーマ1件]
 旧4テーマ: 凍結済み台帳・B3原文を共有dirへコピー(sha256照合、下表)。research/B3のAPI呼び出しなし。
            呼び出しを検出したら即停止(5-2。er019 L92分岐は台帳コピー漏れ時に黙って再実行する)
 全10記事 : B3注記仕様 v1(委任_02成果物、ユーザー確認後に確定)で再注記 → 注記版brief(【事実N】+重要数値)
            (旧4の過去注記[annotate_briefs.py SPEC]は使わない。決定7)
[旧仕様腕]  共有ledger + 原本B3(注記なし)
            er019 runner --stage all (既存の再利用分岐: ledger/selected_brief.mdが既にあれば再生成しない)
            Luna R0→R1→R2(現Production、FC+must-fix1回+記号Gate込み) → EN Advanced+Standard(M1/M2/M3全OFF) → Checker
            旧腕のEN段で`JARecheckRequiredError`を捕捉した時点を「初回JA_RECHECK」として記録(その後は案B=Production Luna再生成で回復、従来どおり)
[新仕様腕]  共有ledger + 注記版brief
 W1 Fact Lock R0: Production関数 jaw.run_ja_writer_o_r1_r2 のOriginal段(R0_PROMPT+Fact Lock R0ブロック、gpt-6-luna、
    JA FC Full Ledger、must-fix1回→STOP、記号Gate)をR1直前で打切り(astra_revise_matrix_02/tools/gen_r0_small_bag.py と同手順)
    → タグ照合(測定のみ) → strip_tags
    → R0復唱検出(OPEN-175、検出のみ・修正しない。結果をR0として記録)
 W2 Astra R1: model=gpt-6-astra、Standard同期(service_tier指定なし=既定)、reasoning={"effort":"high"}、previous_response_id不使用、
    developer/systemメッセージなし。userメッセージ逐語(系列X):
    "以下の記事:\n\n{前段本文}\n\n事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。長さは800〜1000字程度でお願いします。"
    (出典: astra_revise_matrix_01/02 の DESIGN.md、run_matrix2.py USER_TMPL。800〜1000字はソフトキャップ=字数を理由にSTOP/再生成しない)
    → JA FC(Luna、全台帳)
 W3 Astra R2: 入力=R1の生出力(Markdown除去前、matrixと同じ)。同条件 → JA FC
 W4 後処理(API無し・決定論): strip_markdown(P1) → 「……」「…」を文末は「。」文中は「、」へ(normalize_ellipsis_pause_ja)
    → 「——」を「、」へ(dash_to_comma) → 記号Gate(detect_prohibited_symbols、記録のみ)
    → 最終JAを ja_writer/revision2.md として保存(= er019 runnerの「既存JA記事(R2)再利用」分岐に乗せる)
    → R0復唱検出を最終JA(R2)にも適用し、R0の復唱が改稿後も残るかを記録(残れば表現上の軽微として別枠)
 W4b R2後のJA FC(最終JA本文)にMAJORがあれば `shadow_stop=true` を付けて記録し、B1回復経路(下記)へ(1記事1回の枠を消費)
 W5 EN: efam.run_writer_stage (advanced → standard)。OPEN243_M1=1(Advanced枝のみ有効)。
    storyline_line / selected_fact_brief_text = None を渡して案B(Production Luna Writerによる本文再生成)を無効にし、
    新腕への旧Writer混入を防ぐ。ja_source MAJOR → `JARecheckRequiredError` 捕捉時点を「初回JA_RECHECK」として記録 → B1回復経路へ
 B1回復経路(決定6、新腕のみ): 
    Fact Lock R0に既存must-fixブロック(`jaw.run_ja_writer_o_r1_r2`の`original_must_fix`引数[er019_family_x_ja_writer_o_r1_r2_01.py L237・L264、
    呼び出し例 er012_...runner_01.py L773])を付けて再生成 → Astra R1 → R2(系列X逐語) → W4後処理 → EN再実行(W5から)
    上限: 1記事1回(W4bのR2後FC MAJOR由来の回復とW5由来の回復は同じ枠を共有=解釈案、Fable確認要)・Trial全体3回。
    超過、または回復後もMAJORが残る場合はSTOPとして記録(止まった記事も分母に残す)。
    Production等価性: 新腕のFC MAJORを「記録して続行」から、上記回復1回→残れば影STOP、へ統一する(旧腕のProduction安全装置と対応)
 W6 Checker(Advanced/Standard各1 run): runner.apply_open233_approved_flow_switches() + FLOOR_MODE=number_only確認
    + OPEN233_RECLASSIFY_PROTECT_FLAGS=changed_actor (M3)
TTS: 結果確認後に選ぶ2記事のみ、Standard同期(TTS_EXECUTION_MODE=STANDARD、ASR突合込み)。G2から切り離して後回し(論点7)。
     対象はFable/ユーザーが選定。TTS入口スクリプトは未特定(前提作業h2)
```

確認済み根拠(コード): er019 runnerは既存の`research_ledger/verified_fact_ledger.txt`(`run_research_and_ledger`先頭)・`storyline_b3/selected_brief.md`+`fact_selection_evidence.json`・`ja_writer/revision2.md`が揃っていれば再生成せず再利用する(`er019_family_x_entertainment_production_runner_01.py` L91-98、`main`のstoryline/writer再利用分岐)。**再利用分岐は`fact_selection_evidence.json`の`selected_fact_brief_text`を読む**(同runner L336-339)ため、B3原文を照合する際はJSONも対象にする(G0照合拡張)。`efam.run_writer_stage`は`storyline_line`か`selected_fact_brief_text`が`None`のとき案Bを行わず`JARecheckRequiredError`をそのまま送出する(`er012_e_family_entertainment_two_level_runner_01.py` L737-753)。

凍結入力(共有dirへコピー。sha256先頭16桁は本書作成時に`sha256sum`で実測、コピー後に再照合する):
| テーマ | 台帳 | 旧腕B3(原本・注記なし) |
|---|---|---|
| META(b2) | `er052_output/factlock_writer_trial_01/runs/meta/control/b2__factlock__r1/research_ledger/verified_fact_ledger.txt` ea0ce587e605beea | `er052_output/open233_b3_trial_01/runs/meta/nb/V0/b2/storyline_b3/selected_brief.md` 055b1385b6db97e9 |
| ホルムズ(b2) | 同`runs/hormuz/control/b2__factlock__r1/...` 9bd6834e68e7e437 | `open233_b3_trial_01/runs/hormuz/nb/V0/b2/storyline_b3/selected_brief.md` e1f892dffb7ff3cf |
| 宇宙兵器(b2) | 同`runs/space_weapons/control/b2__factlock__r1/...` f172a253f24b99d6 | `open233_b3_trial_01/runs/space_weapons/nb/V0/b2/storyline_b3/selected_brief.md` e29575ffe46ba132 |
| ミニバッグ | `er052_output/gpt6_wiring_e2e_01/run_02/research_ledger/verified_fact_ledger.txt` 0cc8ca3f2e73a1f9 | `.../run_02/storyline_b3/selected_brief.md` 55bb9ba3ef209214 |
(v1にあった「新腕B3(注記版)」列は削除: 旧4の過去注記版[`selected_brief_factlock.md`等]は決定7により使わず、全10記事を新仕様で再注記する。過去注記版のsha256はv1を参照。)
META・ホルムズの台帳は`open233_b3_trial_01`側の同名ファイルとsha256一致を確認済み(ea0ce587.../9bd6834e...)。宇宙兵器の`open233_b3_trial_01`側台帳との一致は未確認(実行前に照合)。b2を選ぶ理由=Astra matrix(META b2、ホルムズ b2)と同じ入力に揃えるため(宇宙兵器もb2に統一)。
**G0照合(v2拡張)**: 新腕の`strip_tags(注記版brief)`が旧腕のB3原文(`selected_brief.md`)と一致することを確認する(注記がタグ付けだけで本文を変えていないこと)。さらに旧腕が再利用分岐で読む`fact_selection_evidence.json`(`selected_fact_brief_text`)も、sha256と、その`selected_fact_brief_text`が`selected_brief.md`と一致することを照合する(照合対象にJSONを含める。論点5)。
確認済み事実: 旧来の注記は手付け(`er052_output/factlock_writer_trial_01/tools/annotate_briefs.py`のSPEC辞書)だったが、v2では注記を委任_02の注記仕様 v1で固定し、全10記事を再注記する(決定7)。

### 2-1. 構成スイッチ表(腕ごと、v2)
| スイッチ | 旧仕様腕 | 新仕様腕 | 備考 |
|---|---|---|---|
| JA Writer | 現Production(gpt-6-luna、Luna R0→R1→R2) | Fact Lock R0[Luna]→Astra R1→R2 | |
| `OPEN243_M1` | 未設定 | `1` | Advanced枝のみ。StandardはM1非対応(論点4、§4(d)) |
| `OPEN243_M2` | 未設定 | 未設定(見送り) | ユーザー決定3 |
| `OPEN233_RECLASSIFY_PROTECT_FLAGS` | 未設定 | `changed_actor` | M3 |
| `OPEN233_APPROVED_FLOW_SWITCHES`(Checker) | 適用 | 適用(同一) | `FLOOR_MODE=number_only`確認 |
| `OPEN243_G3_TELEMETRY_PATH` | 腕別ファイル | 腕別ファイル | 観測のみ、API費用0 |
| JA再確認(案B)の回復手段 | 有効(Production: Luna Writer再生成) | **B1**(新Writer再実行: Fact Lock R0+original_must_fix→Astra R1→R2→後処理→EN再実行、1記事1回、Trial全体3回) | 決定6。新腕に旧Luna Writerを混入させない |
| 注記版brief | 使わない(原本B3) | 使う(B3注記仕様 v1で再注記) | 決定7 |
| 影の対照(ログ専用) | あり(他方の規則を1回、3節) | あり | 論点1。判定に使わない |

プロセス分離: (テーマ,腕,段)ごとに`subprocess`で起動し、環境変数をホワイトリストで明示する(`os.environ`の持ち越しとrunnerモジュールグローバルの汚染を防ぐ)。腕の環境変数が期待値と一致しない場合は開始前にSTOP(provenance違反)。

## 3. M1/M3の寄与分離テレメトリ(v2: Arm C不要、影の対照を両腕で取る。論点1)
前提: 2腕比較ではJA本文が違うためM1/M3の効果はWriter効果と交絡する。Arm C(旧JA×M1/M3 ON)は採用せず、**各腕のrun内で「もう一方の規則を当てたら」を再構成できるログ(影の対照)を両腕で取る**。影の対照の結果は判定に使わず記述のみ。保存先=`<theme>/<arm>/telemetry/`。追加費用見積 計¥10〜15(Opusレビュー値)。

- **M1(a) 入力追加の効果(両腕・同一本文上の対照、20対)**: 旧腕の本文に「M1入力(JA+Ledgerを追加した要約生成)の要約+EN検査1回」を、新腕の本文に「旧入力(`generate_family_x_in_one_line(client,title,body)`)の要約+EN検査1回」を、ログ専用で実行する。同一本文上で入力の有無だけが違う対照が得られる(Advanced枝のみ)。
- **M1(b) 要約のみ再生成の効果**: 要約のみMAJORで再生成が発火した場合に、もう一方の規則をログ専用で1回実行する。
  - 新腕(M1 ON)で発火 → 旧規則=Advanced本文ごと再生成1回+EN検査1回(約¥0.6/発火、`er012_e_family_entertainment_two_level_runner_01.py` L556-579の経路)。
  - 旧腕(M1 OFF)で要約のみMAJOR → 新規則=`open243_m1_summary_only_retry`(同L397)をログ専用で1回。
  - **v1訂正**: v1 3節の「M1(b)の反実仮想は安く再現できない」は誤り。上記のとおり約¥0.6/発火で再現できる。
  - 発火件数・解決率・過去実績(従来6/14 対 M1 14/14、REPORT §110 V1)との対比も併記する。
- **M3(旧腕run起点、¥0が基本)**: 旧腕のCheckerログから、`changed_actor`保護があれば保護されていた除外claimを機械的に列挙する(¥0)。任意で、その保護claimをStage 2に1回通す(ログ専用、約¥0.05〜0.1/run)。新腕側は従来どおり(i)保護claim本文・fact_id・フラグ・route、(ii)その後のStage 2判定・floor・S1・Rewrite誘発・最終処置を`m3_protected.jsonl`へ1 claim 1行で出力する。Checker run JSONの`stage1_coverage.candidate_filter`(`n_protected_keys`、`n_excluded_claims`、`verdicts`)が既存(`open233_prod_e2e_02/runs/meta_run03_advanced.json`で確認)。
  評価は「保護されて重大が拾えた(便益)」対「保護されて不要なRewriteになった(コスト)」を盲検ラベルと突合する。
- **Standard(M1非対応、論点4)**: M1のStandard版は実装しない。Standardのattempt1 MAJORを`open243_majors_only_in_summary`(同L377)で「要約/本文」に分類して記録する(¥0)。**「Standard側のM1効果は未測定」と明記**する。ただしStandardは修正済みAdvanced要約を含む全文をA2化する(`er003_v1_n3_01_standard_a2_generate.py` L522・L541)ため、Advanced側の修正は部分的にStandardへ伝わる。
- 初回の要約(M1 ON入力で生成)と初回EN検査の全deviation(既存`b1b/audit/deviation_checks/advanced_attempt1.json`)、再生成が発火した場合の各attemptの要約・must-fix入力・EN検査結果(`advanced_attempt{2,3}.json`、`rejected_advanced_m1_summary_retry.md`)も全件保存する。
- 腕の同定: すべてのrun JSON・telemetryに`arm`、フラグ実値、スクリプトsha256を記録する。
- 解釈の限界: 腕比較の結果をM1/M3単独の効果と書かない。影の対照は同一本文上の記述的対照であり、有意性検定の対象にしない。

## 4. 前提作業一覧(v2、実装は本委任では行わない)
| 項 | 内容 | 対象ファイル・行(確認済み) | 見積行数 | リスク |
|---|---|---|---|---|
| (a) | gpt-6-astra Standard単価の正式登録(input 10 / cached 1 / output 50 USD per 1M、出典`extracted_pricing.json`、2026-10-08 16:38 JST取得、raw html sha256 161df7d8...)。未登録のままだと`_load_pricing().price()`が`PricingNotFoundError`でfail-closed(`er012_e_family_entertainment_two_level_runner_01.py` L106-118)。routing contractはastraをprocessへ割り当てず`require_model_or_override`(`er006_model_routing_contract_01.py` L163〜)で扱うため契約側の変更は不要 | `er005_output/cost_baseline_01/pricing_snapshot.json`(luna登録例 L228〜L262に倣い3 meter)、`er006_model_routing_pricing_coverage_test_01.py`(L50〜)にテスト追加 | 約36行(JSON)+約15行(test) | Production用単価表の編集。登録=astra採用ではない旨を明記し別commit。**G1後にダッシュボード請求増分と照合し、照合までガードは×1.5安全係数(下記k)**。cache_write(12.5)は未登録(本用途で未使用)。guardは`cached_input_tokens`を割引計上せず安全側の過大計上 |
| (b) | R0本文冒頭の復唱(OPEN-175)の**検出のみ**(案A、修正しない)。R0と最終JA(R2)の両方で検出し、改稿後も残るかを記録。残れば表現上の軽微として別枠(論点8)。実測: Fact Lock v1のR0 24本中1本(ホルムズ b2 r1、Astra matrixで使われたR0そのもの)、all6/baselineのR0 44本中4本。原因=`R0_PROMPT`(`er019_family_x_ja_writer_o_r1_r2_01.py` L52)の引用文。Productionプロンプト修正は未承認仕様のため行わない | 新runner内の正規表現(両腕で記録) | 約20行 | 検出のみで腕間の非対称なし |
| (c) | **タグ残存修正(B1に必要、v1の「0行」から変更)**: 再生成(B1回復)のたびに`ja_writer/original.md/revision1.md/revision2.md`がタグ付きで上書きされ、`postprocess_phase1`が1回しか走らず除去されない(`factlock_writer_trial_01/RESULT.md` §3)。再生成後にも`strip_tags`+照合を再適用する | `er052_factlock_writer_trial_01_run.py`のpostprocess呼び出し、または新runner側の同等処理(既存編集を避けるなら新runner側) | 約30〜50行 | 修正漏れは次段に【事実N】タグが流入する。G1で実測確認 |
| (c2) | **B1回復経路(新規)**: W4b/W5の失敗検出 → `original_must_fix`付きでFact Lock R0再生成 → Astra R1→R2 → 後処理 → EN再実行。1記事1回・Trial全体3回のカウンタ(state.jsonに追記専用)、超過はSTOP記録。回復で生成した成果物は元の失敗成果物を上書きせず別名保存(事前登録5-4) | 新runner内 | 約80〜120行(見積、(c)と別) | 回復1回あたり約¥35(見積: R0 1.4+Astra 31.3+FC 0.35+EN 1.0〜1.5)。3回で約¥105 |
| (d) | M1のStandard(A2)分岐は**実装しない**(論点4)。代わりにStandardのattempt1 MAJORを`open243_majors_only_in_summary`で要約/本文に分類して記録(¥0)。「Standard側のM1効果は未測定」と明記 | 新runnerのtelemetry出力(`er012_...runner_01.py` L377の関数を呼ぶのみ) | 約20行 | Standard枝のM1効果は未測定のまま |
| (e) | 記号後変換+Markdown除去の組込位置。既存部品を再利用: `strip_markdown`(`er052_step2_astra_r3_01_run.py` L154)、`dash_to_comma`(同L168)、`normalize_ellipsis_pause_ja`(`er003_audio_tts_asr_safety.py` L929)、`detect_prohibited_symbols`(同L1026)。組込=Astra R2出力の直後、FCの前、`revision2.md`保存の前。R2の入力にするR1は生出力のまま(matrixと同一) | 新runner内(既存ファイル変更なし) | 約40行 | matrixのFCはP1本文、本設計は変換後本文でFC(句読点のみの差)。記号Gateは記録のみ(論点3: 記録のみで可、残存はTTS対象2本で確認) |
| (f) | 2腕並走runner。新規`er052_factlock_astra_e2e_runner_01.py`(仮称): テーマ共有dir管理、旧腕=er019 runnerのsubprocess、新腕=W1〜W6+B1、Checker起動(`er052_output/open233_prod_e2e_01/e2e_run_02.py`の`run_one`/`RunCapHook`を流用し、**生成記事から動的にinstanceを組む**)。fixtureのキー=`id, ledger_text, article_text, source_article_text(=JA R2), include_related_fact_id(=True), hook_aware(=False), baseline_parsed`(`er050_gpt6_checker_comparison_trial_01.py` L133-151)、inst側は`stage1_mode="fresh"`・`substitute_baseline_on_stage1_miss=False`・`s1u_eligible=False`。状態分離: `runner.OUT_DIR`/`BUDGET_STATE_PATH`をworker別、telemetry/G3パスを腕別、出力は`<theme>/<arm>/`に閉じる、書込は一時ファイル→rename | 新規ファイル(既存編集なし) | 約450〜600行+単体テスト約250行(v1見積。(c2)(i)(k)(m)を別項に分けたため本項は据置) | 最大の新規実装。**動的fixtureの`baseline_parsed=None`が通るかはG1のChecker 1 runで確認**(論点7) |
| (g) | 予算ガードのweb_search未計上差(`E2E_EVIDENCE.md` L44)は**既に是正済み**(OPEN-242、commit 0110d6f1、`web_search_call_usd` `er012_...runner_01.py` L124-130)。本実行前に¥0で再確認: run_02の`raw_usage_log.jsonl`からガード値を再計算し`cost.json`=19.105と一致(±0.01) | 確認スクリプト | 約20行 | 残る穴は(a)単価未登録と(k)横断集計 |
| (h) | **B3注記仕様 v1への依存(委任_02成果物、ユーザー確認待ち)**: 全10記事を新仕様で再注記。注記ルールはsha256凍結し、注記者(Sonnet worker)に生成結果・腕を見せない。**独立二重注記**で一致率を記録、不一致はルールで機械的に決定。G0で`strip_tags(注記版)`=旧腕B3原文を照合(`fact_selection_evidence.json`のJSONも対象、2節)。旧4/新6を層別報告。結果は「人手注記の上限性能」と明記(論点5)。Production化にはB3自動注記が必要=**OPEN項目候補**(起票はFable判断後) | `er052_output/factlock_astra_e2e_trial_01/`配下に注記ログ・照合スクリプト | 照合スクリプト約40行+注記作業(10記事×2名) | 注記仕様 v1が確定するまで着手不可。注記者バイアス・再現性の限界(自動ルール未整備) |
| (h2) | TTS 2本の入口。er019 runnerはStandardで終了しTTS stageを持たない(同runner L394)。DEV TTS Standard同期の既存スクリプトは未特定。**G2から切り離して後回し**(論点7) | 未確認(要調査) | 未確認 | TTS費用「約¥40」はFable見積で根拠ファイルは未確認 |
| (i) | **影の対照ログ(両腕)**・R0復唱検出・ブラインド化・集計スクリプト・新規具体主張(ii)検出器(両腕のJA最終本文、約¥0.2/本)・人手介入必要率/初回JA_RECHECK率/shadow_stopの集計。M1(a)・M1(b)・M3は3節のとおり | 新runner+`tools/` | 約200行(v1の約150行から増) | 影の対照はAPIを追加で使う(計¥10〜15、Opus見積)。判定には使わない |
| (j) | 新腕の失敗・STOP方針(5-3)の確定 | 設計のみ | - | v2で更新(B1、shadow_stop) |
| (k) | **横断予算予約**: 各API段の前に、worker別台帳合計+実行中見込みの予約で累計を判定する(Checker runnerは別budget stateで動くため、3〜4 workerの合計を横断集計する必要がある)。astra単価はG1後にダッシュボード請求増分と照合し、**照合までガードは×1.5安全係数** | 新runner内 | 約60〜80行(見積) | 予約を忘れた並列段が同時に上限を超えうる |
| (l) | **G1カナリア拡張**(論点7): META新腕のEN段までに加え、Checker 1 run(動的fixture `baseline_parsed=None`のruntime確認)と、旧腕の再利用分岐でAdvancedまで通す確認を追加(約+¥8) | G1手順(5-0) | - | 追加費用の見積は未実測 |
| (m) | **旧4テーマの即停止検出**: 旧4テーマでresearch/B3のAPI呼び出し(web_search含む)を検出したら即停止(er019 L92分岐は台帳コピー漏れ時に黙って再実行する)。subprocessのAPIログ・stage出力の新規生成を監視 | 新runner内 | 約30行 | 検出漏れは¥15〜17の重複支出+B3原文が変わる(凍結違反) |
| (n) | **中間チェック**: 旧4完了後、フロー健全性のみ確認(品質評価はしない)。新腕STOPが系統的(例4/4)ならFableが停止判断 | 手順(5-0) | - | 判定線を決めない「停止判断」はFable裁量 |

## 5. 実行計画(v2)

### 5-0. ゲート順(v2)
1. **B3注記仕様 v1のユーザー確認**(委任_02成果物→Opusレビュー→ユーザー提示・確認。未完了)
2. 新6テーマ選定(ユーザー回答待ち)+(実行Go後)Stage R: 新6のresearch+ledger+B3(約¥100、web_search込み。注記の前提のためG0より前)
3. 全10記事を新仕様で注記(独立二重注記、一致率記録、不一致はルールで機械決定)
4. **G0(¥0)**: 前提(a)(c)(c2)(f)(i)(k)(m)の実装・単体テスト・dry-run(API stub)、(g)再確認、メモリ確認、sha256照合(`strip_tags(注記版)`=旧腕B3原文、`fact_selection_evidence.json`のJSON含む)、動的fixtureのdry-run
5. **G1(カナリア、見積約¥43〜53[v1の約¥35〜45+拡張約¥8]・約15分[見積])**: METAの新腕をEN段(Advanced+Standard)まで1本だけ実行してフロー破綻(モデルID、タグ残存、記号、STOP、費用)を確認。加えて(l): Checker 1 run(動的fixture `baseline_parsed=None`のruntime確認)、旧腕の再利用分岐でAdvancedまで通す確認。品質評価はしない。astra単価をダッシュボード請求増分と照合。
6. **G2 本番**: 旧4テーマ → **中間チェック**(フロー健全性のみ。新腕STOPが系統的[例4/4]ならFableが停止判断)→ 新6テーマ。TTSはG2から切り離し、結果確認後に別途。

直列化の理由=新規runnerの初回runtime evidence確認(破綻時の損失を数十円に限定)、注記は注記仕様の確定に依存(順序依存)、中間チェックは新腕の系統的失敗の早期検出(予算・品質Gate)。
G1の出力をMETA新腕の本番run扱いにするか否かは未決(扱いにより総額が最大+¥35〜53変わる。8-3)。

### 5-1. 並列度と割付(v2、割付を中間チェックのため変更)
単層並列(worker=プロセス)。二重並列(ThreadPool×xargs)は禁止(2026-10-07 PCクラッシュ、WinError 1455の教訓)。各worker開始前と各stage前に空き物理メモリを確認し4GB未満なら待機(前回E2Eの上限60分待機を踏襲)。実測根拠: 前回の単層4並列で最大Private約1.2GB・空き物理≧4.2GB・降格0(ACTIVE_TASK A5記載)。単層4並列+自動降格はユーザー決定済み(A5)の選択肢。
割付案(見積で時間均等化。旧テーマ約29分、新テーマ約36分、6-4):
- **ラウンド1(旧4テーマ)**: 4worker各1テーマ(META/ホルムズ/宇宙兵器/ミニバッグ)の単層4並列(約29分)。→ 中間チェック。
- **ラウンド2(新6テーマ)**: 3worker×各2テーマ(約72分)。
- 4並列が不可(メモリ待機・降格)の場合の代替: ラウンド1を3worker(1workerが2テーマ)に落とす。その場合のラウンド1は約58分。
旧腕を先にする理由=安価で、途中停止時に必ず対(paired)で揃う側から止まるため。1テーマ内は直列(旧腕→新腕)。新テーマのresearchで台帳が使えない場合(例: kept facts<3、API障害が再試行2回後も継続)は、ユーザーが指名する補欠テーマと入替(事前登録)。

### 5-2. 費用・停止条件(前回計画書`e2e_plan_open233_stage1_loop2_01.md`のWaste検知を踏襲、数値は本E2E用の提案)
| 区分 | 閾値(提案) | 動作 |
|---|---|---|
| 累計上限(ユーザー決定) | ¥1,000 | 到達でhard stop。ソフトアラート¥800で新テーマ開始を止めFableへ報告 |
| 見積超過 | 累計が推定上側(約¥900)を超える見込み | 一時停止してFableへ報告(具体値は実行Go時にFableが再設定) |
| research+ledger+B3(1テーマ) | 見積約¥15〜17(実測根拠6節)。¥30超でアラート、¥40超でabort | abort時は補欠へ |
| Astra R1+R2(1記事) | 見積約¥27〜34。¥50超で当該記事abort(ガード計上は×1.5係数込み) | |
| Checker 1 run | 実測最大¥5.66、平均¥3.50(§81)。¥10超でabort、記録して次へ | |
| 新腕1記事合計 | 見積約¥42(B1回復を含まない)。¥70超でアラート | |
| B1回復 | 1記事1回・Trial全体3回。4回目以降の発動要求はSTOP記録(実行しない) | |
| **即停止(全体STOP)** | (1)provenance違反: 腕のフラグ・モデルIDが期待と不一致(Astra段の`model`が`gpt-6-astra`で始まらない、`fallback_detected`) (2)API失敗>3/run (3)単価未登録例外 (4)出力NUL/破損 (5)予算state不整合 (6)承認スイッチ不一致 (7)新腕でLuna R1/R2呼び出しを検出(旧Writer混入) **(8)v2追加: 旧4テーマでresearch/B3のAPI呼び出し(web_search含む)を検出** | |
| 品質起因(Human Review、重大、STOP) | **止めない**(記録のみ。前回E2Eと同じ) | |

予算判定(v2): 各API段の前に、worker別台帳合計+実行中見込みの予約で横断集計して判定する((k))。astra単価は照合(G1後のダッシュボード請求増分)までガードで×1.5安全係数。
Waste検知: 前回の`RunGuard`(call数>80、cycle番号>5、同一claim_identityのRewrite>3)を流用し、abort記録のうえ全体STOP判断はFable。

### 5-3. 新腕の失敗扱い(v2、論点2・3)
- Astra APIの一時エラー: 最大2回再試行(前回E2Eの技術障害再試行MAX_RETRY=2と同じ)。
- JA FC(R1後)のMAJOR: 記録のみ(再生成しない)。**R2後のJA FC MAJOR**: `shadow_stop=true`を付けて記録し、B1回復(1記事1回)へ。回復後も残れば影STOP(Productionなら止まる記事)として記録して続行(分母に残す)。R0は既存のmust-fix1回→STOPを維持。
- 記号Gateの残存: 記録のみ(必要ならTTS対象2本で確認)。字数: ソフトキャップのため判定せず記録のみ。
- EN段の`JA_RECHECK_REQUIRED`(ja_source MAJOR): 初回として記録 → B1回復(1記事1回・Trial全体3回)→ 回復後もMAJORまたは上限超過ならSTOP記録。
- 初回(回復前)の状態は旧腕・新腕とも主指標K(初回JA_RECHECK率)に記録する(回復で見かけ上消える失敗を隠さないため)。

### 5-4. 途中停止時の再開
- stage完了マーカー(各stageの出力が存在・非空・NUL無し・JSON妥当)を`<theme>/<arm>/state.json`へ追記専用で記録。再開は未完了stageのみ、完了済みstageのAPI再呼び出しは禁止(R1済みならR2から)。B1回復カウンタもstate.jsonに追記専用で記録し、再開時にも1記事1回・Trial全体3回を維持する。
- 費用台帳はworker別`ledger_costs_worker{N}.jsonl`(追記専用、他workerのファイルは読取のみ)。累計=全ファイルの合計。
- 破損疑い(0バイト、NUL埋め)は当該stageだけ破棄して再実行し、破棄分の費用も台帳に残す。
- 再開時はスクリプトsha256が同一であること(変更した場合は事前登録の「変更禁止」違反として記録しFableへ)。

## 6. 費用・時間見積(v2、**見積**。実測根拠は出典併記)

### 6-1. 単価・実測根拠(確認済み、v1から変更なし)
- astra Standard 10 / cached 1 / cache write 12.5 / output 50 USD per 1M(Batch・Flexは50%): `er052_output/factlock_writer_trial_01/astra_pricing_01/extracted_pricing.json`(2026-10-08 16:38 JST取得)。USD/JPY=160。ダッシュボード請求との突合は未実施=未確認(G1後に実施)。
- Astra R1+R2 Standard換算(実測トークン由来)=3記事・系列X・平均約¥31.3/記事(範囲約¥27.1〜33.6): `docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_18_result.md` §5、`astra_revise_matrix_02/eval/COST_MATRIX_02.md`。
- Luna Writer(R0〜R2+FC)約¥1.40: `er052_output/gpt6_wiring_e2e_01/E2E_EVIDENCE.md` run_02。
- EN段(Advanced+Standard)約¥0.76: 同上 advanced 0.318+standard 0.443。
- research+ledger+B3: run_02 約¥16.95(web_search込み)。別run(委任_03 run_01)約¥14.97。
- Checker: §81の9 run実測 合計¥31.519、平均¥3.502/run(範囲¥1.97〜5.66)、平均345.5秒/run(最大548.7秒)(`open233_prod_e2e_02/e2e_summary_02.json`)。
- Astra所要: R1+R2平均約98秒(委任_18結果 §4(a))。

### 6-2. 1記事あたり(見積、v1据置。v2の追加分は6-3)
| 項目 | 新仕様腕 | 旧仕様腕 | 根拠 |
|---|---|---|---|
| Fact Lock R0 / Luna Writer | 約¥1.4 | 約¥1.4 | 6-1 |
| Astra R1+R2 | 約¥31.3(範囲27〜34) | - | 委任_18 |
| JA FC(R1後・R2後) | 約¥0.35 | (Writer内) | COST_MATRIX_02 |
| EN(Advanced+Standard) | 約¥1.0〜1.5 | 約¥0.8 | 6-1 |
| Checker(2 run) | 約¥7.0 | 約¥7.0 | §81 |
| 小計 | 約¥41〜42(v1小計は影の対照約¥0.4〜0.7込みで約¥42、範囲約36〜52) | 約¥9.2(範囲約7〜14) | |

### 6-3. 総額(見積、v2)
| 項目 | 見積 |
|---|---|
| v1総額(新腕10記事約¥420、旧腕10記事約¥92、新6 research+B3約¥100、TTS約¥40) | 約¥650(範囲約¥560〜780) |
| v2追加: 影の対照(両腕、M1(a)20対・M1(b)発火分・M3) | 約¥10〜15(Opus見積。v1の影の対照約¥6相当を置換するか上乗せかは未照合) |
| v2追加: 新規具体主張(ii)検出器(両腕JA最終本文20本×約¥0.2) | 約¥4 |
| v2追加: G1拡張(Checker 1 run+旧腕Advanced再利用分岐) | 約+¥8 |
| 追加分合計(B1除く) | 約¥25〜30(Opusレビュー値。上3項の単純和は約¥22〜27で、差は未照合) |
| B1回復(1回約¥35の見積、上限3回) | 最大+¥105 |
| **推定総額** | **約¥690〜900**(Opus/Fable推定)。本書の単純加算では最悪ケース 780+30+105=約¥915(約¥15の差は未照合) |
| 上限¥1,000に対する余裕 | 推定上限で約¥100、単純加算の最悪でも約¥85 |

未確認: G1出力を本番run扱いにするか(8-3)。新6 research+B3の前倒し(Stage R、約¥100)はv1総額に含まれており追加ではない。
最大のブレ要因=Astraのreasoning量(出力トークン)、Checkerの幅(¥1.97〜5.66/run、最大40 run)、B1の発動回数。

### 6-4. 時間(見積)
1テーマ: research+B3約2〜3分(新6のみ。run_02全体326秒からの上限推定、単独実測は未確認)+旧腕(Writer約2分+EN約2分+Checker 2×345秒)+新腕(R0約1分+Astra約98秒+FC+後処理+EN約2分+M1再試行+Checker 2×345秒)。新テーマ約36分、旧テーマ約29分(いずれも見積)。B1回復は1回あたり約5〜6分(見積: R0約1分+Astra約98秒+FC+EN約2分)。
v2の割付(ラウンド1=4並列約29分→中間チェック→ラウンド2=3並列×2テーマ約72分)で、実行部は約100分+B1(最大3回で約15〜18分)+中間チェック+G1(約15分)。注記作業(10記事×独立二重注記)と新6のStage Rは別途(Sonnet worker時間は未見積)。TTS・ASRは切り離し。**G2全体は約2〜2.5時間(v1見積)と概ね同等**(4並列が可能な場合の短縮と、中間チェック待ち・G1追加で相殺)。

## 7. 評価手順(v2)
1. **自動集計(¥0)**: run JSON・cost.json・telemetryから1-2の表A〜E・H・I・K〜Nを機械集計(§81と同形、分母は予定run数20に固定)。旧4テーマは凍結値を別列で併記。
2. **盲検ラベル**: 新R2/旧R2、新EN/旧ENを腕・順序を隠してコピー(MAPは非公開、git add対象外)。Sonnet worker×3(テーマで分割)が重大/軽微をラベル。Sonnetラベルは推測でありユーザー確認前は確定ではない。**盲検の限界(v2明記)**: JAはAstra/Lunaの文体差で腕が推測できるため盲検は不完全。ENは文体差が小さい想定だが未確認。
   **ラベル対象にSTOP記事の採用されなかった本文(`rejected_*.md`)も含める**(「出荷されなかった」別枠。出荷された本文の重大/軽微とは混ぜない)。
3. **Fable突合**: Sonnetラベルと自動集計・Checker判定を突合し、不一致・重大候補を判定(`confirmed_by`付き)。
4. **ユーザー人間確認(2〜3記事)**: 重大候補があるテーマと、面白さの差が大きいテーマ。提示パックの形式=テーマごとに「元記事(旧腕R2)」と「新R2(新腕)」だけを、腕を伏せたX/Yで並べる(`USER_PACK_02.md`形式)。対応は`_private/MAP.json`、回答後に開示。
5. **Opus条件C**: 結果が「重要変更のProduction採用提案前」に該当する場合、Opus独立レビューを入れる(`PM_GOVERNANCE.md` 11-3)。採用判断は人間ユーザーのみ。
6. 層別報告: 旧4/新6(注記は全10記事新仕様に統一済みだが、旧4は過去E2E・過去台帳が既知で、新6は未知テーマ)。独立二重注記の一致率も併記。
7. 報告: `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`に新節(次の空き番号)として記録(生データは本ディレクトリ配下の`runs/`)。

## 8. Opus条件Aレビュー(2026-10-09)の採否と残論点
### 8-1. 論点別の採否(全文は`docs/pm/opus_a_review_factlock_astra_e2e_01.md`)
| 論点 | Opus結論(要点) | 本書での反映 |
|---|---|---|
| 1 交絡 | Arm C不要。影の対照を両腕で取る(M1(a)20対、M1(b)、M3)。v1 3節L106-107の「M1(b)は安く再現できない」は誤り。追加¥10〜15 | 3節、4節(i)、6-3 |
| 2 案B | B1採用。初回JA_RECHECK率を両腕で記録。(c)タグ残存修正が前提。PREREGISTRATION §5-8確定 | 2節、2-1、4節(c)(c2)、5-3、事前登録5-8 |
| 3 Production等価性 | FC MAJORは記録して続行を維持しつつR2後に`shadow_stop=true`。複合主指標「人手介入必要率」を両腕同定義で追加。B1採用時はR2のFC MAJORも同じ回復経路(1回)に統一。記号Gateは記録のみで可 | 1-2表L、1-3、2節W4b、5-3 |
| 4 M1 Standard | 実装しない。attempt1 MAJORを要約/本文に分類して記録。「Standard側のM1効果は未測定」と明記 | 3節、4節(d) |
| 5 注記brief | 条件付き可(ルール固定・sha256凍結、注記者に腕を見せない、独立二重注記、不一致は機械決定、G0照合にJSON含む、旧4/新6層別、人手注記の上限性能と明記)。ユーザー決定7により全10記事を新仕様で再注記 | 2節、4節(h)、7節 |
| 6 判定線 | EN STOP率は「3記事差以上かつtranslation MAJOR×0.75」に厳格化。分母は予定run数に固定しSTOPを独立カテゴリに。rejected本文もラベル対象。2-2/2-3の二重計上解消。2-1は判定でなく要確認フラグ。盲検不完全を明記。(ii)検出器を両腕JA最終本文に追加 | 1-3、7節、事前登録2節 |
| 7 停止・費用 | 旧4のresearch/B3呼び出しで即停止、横断予算予約、×1.5係数、G1拡張(+約¥8)、旧4完了後の中間チェック、TTSをG2から切り離し | 4節(k)(l)(m)(n)、5-0、5-2 |
| 8 R0復唱 | 検出のみ(案A)。R0と最終JA(R2)で検出し改稿後も残るか記録。残れば軽微の別枠 | 4節(b)、2節W1・W4 |

### 8-2. v1の誤り訂正
- v1 3節L106-107「M1(b)の反実仮想は安く再現できない」は誤り(Opus論点1)。新腕なら旧規則=Advanced再生成1回+EN検査1回(約¥0.6/発火)で再現できる。

### 8-3. Fable判断が必要な点(本書の解釈・未確認)
1. **Stage Rの前倒し**: 新6テーマのresearch+B3は注記の前提のため、注記(=G0より前)に必要になる。実行Go後の最初のAPI支出(約¥100、web_search込み)となる。実行Goの範囲をどこまでにするか。
2. **B1の1記事1回枠**: W4b由来(R2後FC MAJOR)とW5由来(ja_source MAJOR)の回復を同じ1回の枠とみなす解釈案。別々に1回ずつなら上限3回の消費が増える。
3. **影STOP・人手介入必要率の数え方**(1-3の定義案)。Opus文言に詳細がないため本書で補った。
4. **G1出力の扱い**: META新腕の本番run扱いにするか否か(総額に最大+¥35〜53の差)。
5. **4並列ラウンド1**: A5で承認済みの単層4並列+自動降格を使う案(5-1)。3並列に抑えるか。
6. 総額の単純加算(最悪約¥915)とOpus推定上限(約¥900)の約¥15の差は未照合。
