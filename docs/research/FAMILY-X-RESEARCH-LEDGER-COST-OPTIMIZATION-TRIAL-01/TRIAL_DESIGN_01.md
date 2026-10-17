# TRIAL_DESIGN_01(委任_01報告 §4+§6 抜粋)

> 本文は委任_01 sonnet-workerの最終報告(2026-10-17)を無改変で転記。Opusレビュー前。採用判断はユーザー(正本=TRIAL_PREP_REPORT_01.md)

**Opus条件Aレビュー前**(PM_GOVERNANCE 11-3。レビュー完了までは未確定設計)

# 4. Trial設計書(TRIAL_DESIGN_01相当、**Opusレビュー前**)
## 4-1 4方式の定義と再利用
共通: Research draftは全方式で共用(再実行しない)。以下は新規実行が必要な段。
- 従来方式(M0): 既存Ledgerを再利用。B3は、既存B3がsol6.1の記事(Coffee)なら再利用、他4記事は gpt-6.1-sol で新規1回(既存Ledger入力)。
- 案1(M1): 全Factに対しLedger検証を上限付きPromptで再実行 → その結果でB3(sol6.1)を新規1回。
- 案2(M2): 検証前のdraft全Factを渡す試験版B3(初回)→ 選定Factだけをtrial版Verifierで検証 → REJECTEDなら再選定loop(最大2回)。
- 案1+案2(M3): M2の初回B3選定を**共有**(同一入力なので、新規B3は呼ばない。選定の確率差を取り除く)→ 選定Factだけを、上限付きPromptで検証。REJECTEDが出ればM3専用の再選定。
- 統制(Stage 1に含める): M0b = 従来方式のB3を各記事で追加1回(自然な生成ばらつきの基準)。約JPY54。
- 統制(Stage 2、条件付き): 同日・上限なしのLedger再検証(M0')。Webの更新・版違いによる差と、上限による差を切り分ける。1〜2記事で約JPY16、全5記事で約JPY83。

## 4-2 harness構成(Production runnerは無変更)
- Trial専用script `er082_rlct_trial_01_run.py`(案)。既存関数を import して呼ぶだけ(`efam.run_verification_for_topic`、`b3._call_once`、`vfl01.build_verified_ledger_text`)。Productionのファイルは触らない。
- 出力先は `er082_output/rlct_trial_01/<article>/<method>/`。Production runnerの出力dirとは別。Productionのhash(runner、B3、vfl01、routing)をrun前後に記録し、不変を確認する。
- 上限付きVerifier: 既存 `VERIFICATION_PROMPT_TEMPLATE`(`er003_v1_en_direct_vfl_01_generate.py:228-250`)の末尾に、「各Factで確認のためのWeb検索はweb_search呼出3回まで。3回以内で確認できなければAMBIGUOUSとし、理由を記載(既存の曖昧Factを無理に確定しない規約=`:282-292` と整合)」の指示を追加した試験版Promptを使う(Prompt本体は複製し、Productionは編集しない)。
- 呼出計測点(新規): response.output の web_search_call を1件ずつ保存する。action.type、action.queries/query、順序、取得URL(あれば)。これで「Fact別・呼出別」が初めて復元可能になる。
- 案2のB3試験版:
  - 既存の `USER_PROMPT_TEMPLATE`(`er019_family_x_storyline_b3_fact_selection_01.py:51-80`)は「独立検証済み」と書かれ、`FACT_ID_LINE_RE`(`:129`)は `[VERIFIED]` / `[AMBIGUOUS` 始まりの行しか拾わない。検証前draftは `[UNVERIFIED]` タグ付きで渡すため、試験版Promptと試験版ID抽出関数が必要(複製)。
  - 違いは「検証済み」の語と、タグだけに限る(Prompt差による交絡を最小化)。
  - 再選定の入力口: `_call_once` に `extra_note` 引数があり、本文末尾へ文字列を追加できる。ここに不合格理由と既存検証結果を渡す(本体の改修は不要)。
- 検証結果の再利用: 検証済みFact(fact_id × draft sha256 をキー)は再検索しない。

## 4-3 案2の再選定loop(ユーザー§4の8手順を忠実に)
1. Research候補全体を渡して初回B3。
2. 選定Factだけを独立検証。
3. REJECTEDがあれば、**機械的に削除せず**、B3へ(不合格Factのid・verdict・verification_notes、既に検証済みの他Factのverdictとnotes、未検証の候補一覧)を extra_note で返す。
4. B3がStorylineを再評価。REJECTEDを使わずに成立するか、別Factの追加が必要かをB3が決める。
5. 新規に選ばれたFactだけを検証。
6. 最大2回の再選定。上限に達した、または検証済みFactで成立しない場合は**未成立として記録**し、品質を犠牲にして確定しない(確定ファイルを出さない)。
- AMBIGUOUS: 再選定のトリガーにしない(ユーザー指示はREJECTED)。ただしAMBIGUOUSが中心Factになった割合を指標として記録する(B3が未検証で選ぶため、断定禁止タグを知らないで選ぶ構造的な差)。
- 最終Ledger(`verified_fact_ledger.txt`)は選定Factの検証済み分だけを `vfl01.build_verified_ledger_text` で組み立て直す。その関数は検証結果が無いFactをAMBIGUOUS扱いにするので、未検証の非選定Factを混ぜない。

## 4-4 評価手順
- 記録項目(§6の全項目): LLM/検索費用別、呼出数・クエリ数(新規計測)、Fact verdictの遷移(VERIFIED維持/AMBIGUOUS化/REJECTED/昇格)、B3の採用Fact・主題・展開・結論、再選定回数・追加費用・未成立。
- B3構成差の判定: 機械指標(採用Fact ID のJaccard、storyline文の差)+3段階の人手ルーブリック(軽微=同じ主張・骨格、中程度=焦点・展開の変化、重大=主題・結論・骨格の変化)。方式名を伏せて判定する(ブラインド)。構成差の大きさと品質の良し悪しは別列で判定する。
- 判定者: 机上=Sonnet、独立=Fable、重大判定または不一致のときだけOpus。
- ばらつき切り分け: 従来B3を各記事で2回(M0とM0b)取り、その差を「自然なばらつき」の基準とする。方式間の差が基準の範囲を超えたら方式効果と見る。重大差が出て判別できないときだけ、Stage 2(追加費用ゲート内)で追加再現を検討。
- 誤りの見逃し: 既存の人手確認済みの欠陥(Coffee F12ラベル誤り、F07部分欠落、F16/F17版違い、inbound F05確定ラベル誤り・F12時期誤り、streaming F07)を既知の正解として、各方式が検出し続けるかを見る。ただし5記事では低頻度の重大誤りを統計的に否定できない(ユーザー§7どおり)。

## 4-5 Fact Lock / RFとの整合(JPY0で実施可能)
- 各方式のTrial出力dir(`research_ledger/verified_fact_ledger.txt`、`storyline_b3/selected_brief.md`、`fact_selection_evidence.json`)に対し、`er053_b3_deterministic_producer_01.annot.produce_annotated_b3`(LLM 0 call)と `er053_b3_annotation_contract_01.validate_annotated_b3` を実行する。契約検証がPASSすれば、W-1のFact Lock入力として成立する(入力パスは `er053_b3_deterministic_producer_01.py:844-845` で確認)。
- RFは `parse_ledger_complete`(`er053_risk_flagger_production_01.py:169-194`)で台帳の完全性を検査するだけなら、JPY0で台帳形式の整合を確認できる。記事を伴うRF本実行(Writer W-1が約JPY14/記事+RF)はStage 3(追加費用、本見積に含めない)。
- 案2の台帳は選定Factのみに縮むので、RFが「選定外Factに触れた文」を検知する力が下がる可能性がある。これは構造的な論点としてOpusレビューへ。

## 4-6 受入条件判定表(ユーザー§7)
| 条件 | 判定方法 |
|---|---|
| 採用Factに重大誤りが残らない | 既知欠陥の検出維持+Sonnet/Fable独立確認。残れば当該方式NG |
| VERIFIED降格は根拠付き | 降格したFact全件にverification_notesの根拠と元verdictの対照 |
| 不確実なFactをVERIFIEDに昇格させない | AMBIGUOUS/REJECTED→VERIFIED遷移の件数が0 |
| B3ストーリー品質維持 | 構成差3段階+品質の別判定、M0bとの比較 |
| 実測総費用で削減 | 再選定・追加検証・統制を含む実測合計 vs 従来方式 |
| Fact Lock・RF整合 | 契約検証PASS(§4-5) |
| 5記事の傾向と例外 | 記事別表+Fact数・採用比率との関係 |

## 4-7 隔離(11-7)
- Production既定動作は不変。Trial scriptのみ。`CURRENT_SPEC.md` に未採用案を書かない。新方式はProductionに配線しない。出力は `er082_output/` のみ。
- 隔離test(DefaultOffIsolation型)ではなく、「Production関連ファイルのsha不変+Trial scriptがProduction pathに書かない」を事前検査する(新機能flagは作らないため11-7の例外は不要で、純粋なOffline Trial)。

## 4-8 実行順序・STOP条件・CP
- CP0: ユーザー費用承認(#104)とOpus条件Aレビュー(Fable)。
- CP1: harness実装とJPY0 dry-run(保存済み出力を使った stub test、Prompt組立、契約検証。API呼出なし)。
- CP2: Coffee(M0b、M1、M2、M3)→ Fable確認。
- CP3: inbound(再選定loopが自然に動き得る記事)→ Fable確認。
- CP4: streaming、openai、central → 集計。
- CP5: 集計・構成差判定・Fableレビュー・Status分類(REJECTED/VALIDATED/USER_DECISION_REQUIRED)→ STOP報告。
- STOP条件: 累計実費が承認額に達する、承認前に有料呼出、STOP_NOTICE、外部停止、Production関連ファイルのsha変化、原因不明rc≠0が2回、再選定上限到達時に確定させようとする動作。
- 実行は1記事ずつ。記事単位で費用ガードを置く(承認額の記事按分)。

# 6. 案1+案2の相乗効果(事前の机上所見、実測は後)
- 事前分析からの示唆: 案1が削る反復(fxpw F16/F17)は、B3が採用しないFactで起きており、案2で既に検証対象外になる。つまり案1+案2の追加削減は小さい(数円未満〜約2円)見込み。相乗効果は低いとの予想。ただし選定Factに採用VERIFIEDの反復があれば(streaming F04型)案1の効果が案2の後でも残る。これはTrialで測る。
- 70円目標: RLCO提案書のText工程JPY72.64(Coffee)が基準。案2で約JPY53〜60(推定)。音声工程は未実測で、audio+scaffold計画は約JPY27.8。Research/Ledger改善だけでは70円に届かない見込みという所見は維持(実測音声費用が出るまで判定しない)。
