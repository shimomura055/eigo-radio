# TRIAL_DESIGN_02(v2、Opus条件Aレビュー反映版)

> v2: Opus条件Aレビュー(OPUS_REVIEW_A_01_VERBATIM.md)反映版。Fable決定=OF-RLCT-R-01〜16採用(R-07/R-11は測定・記録のみ)。有料実行はユーザー費用承認#104後。CP1(harness実装・JPY0 dry-run)は承認待ちと並行可。
> 費用はCOST_ESTIMATE_02.md。v1(TRIAL_DESIGN_01.md)は履歴として残す。項番は「R-xx」でOpus指摘との対応を示す。

# 4. Trial設計書

## 4-1 4方式+統制の定義と再利用
共通: Research draftは全方式で共用(再実行しない)。**再利用入力(draft/ledger/B3)は `er082_output/rlct_trial_01/<article>/<method>/` へ複製してから処理する**(R-03)。
- 従来方式(M0): 既存Ledgerを再利用。B3は既存B3がsol6.1の記事(Coffee)なら再利用、他4記事は gpt-6.1-sol で新規1回。
- 案1(M1): 全Factに上限付きPromptでLedger検証を再実行 → B3(sol6.1)を新規1回。
- 案2(M2): 検証前draft全Factを渡す試験版B3(初回)→ 選定Factだけを検証 → REJECTEDなら再選定loop(最大2回)。
- 案1+案2(M3): M2の初回B3選定を共有 → 選定Factだけを上限付きPromptで検証。REJECTEDが出ればM3専用の再選定。**M3のB3構成差はM2と相関する**ことを報告で明示(R-12)。
- 統制M0b: 従来B3を各記事で追加1回(自然ばらつきの基準)。
- **統制M0'(R-04、Stage 1必須)**: 同日・上限なしの全Factレジャー再検証。対象=Coffee・inbound・streaming(上限が効くと予測された3記事)。openai/centralはM1の呼出ログで上限が拘束しなかったことを確認できればM1をM0'の代替とし、拘束した場合のみStage 2で追加。**判定基準=M0'**(M0とM0'の差=Web更新+Verifierばらつき、M0'とM1の差=上限効果)。
- 任意統制(R-12): Coffee・inboundに限りM2初回B3を追加1回(約JPY23、別行)。検証前draftを入力にしたB3のばらつきを測る。

## 4-2 harness構成(Production runnerは無変更)
- Trial専用script(案: `er082_rlct_trial_01_run.py`)。Productionファイルは触らない。
- **Trial専用の検証関数を複製する(R-01)**: model(`vfl01.MODEL`)・reasoning・tools・schema・developer messageは既存と同一、**Promptのみ引数で渡す**。raw responseから呼出単位ログを保存する。M0'/M1/M2/M3の新規検証は**すべてこの同じ関数経由**(方式差=Prompt末尾の上限文のみ)。**モジュール定数の書換え等のmonkey-patchは禁止**。
- **予算guard(R-02)**: web_search費用込み(`compute_stage_cost_breakdown`と同算式)で呼出ごとに判定し、承認額超過見込みでSTOP。既存の`efam.compute_cost_jpy_so_far`/`assert_budget_ok`(token費用のみ)は使わない。プロセス開始時に `cl.install("er082_output/rlct_trial_01/raw_usage_log.jsonl")`。dry-runで「web_search 1回が費用計上される」testを入れる。
- 上限付きVerifier: 既存`VERIFICATION_PROMPT_TEMPLATE`末尾に「各Factの確認のためのweb_search呼出は3回まで。超えて確認できなければAMBIGUOUS」を追加した試験版を使用(Prompt本体は複製)。
- **上限の単位(R-09)**: CP1で公式pricing(web_search_call課金単位、open_page/findの扱い)を確認。課金単位ならweb_search_call全件で上限を定義。未確認なら種別(search/open_page/find)ごとに記録し、遵守率と費用影響を別々に報告。上限は**ソフト上限**(Prompt指示)であり、「上限指示Promptという介入」の効果として測定する。報告に「hard capではない」旨と遵守率(ログ上、Fact群あたり3回を超えたと推定される件数)を併記。Fact別API分割と`max_tool_calls`系は主比較に入れない(後者は存在・挙動未確認。使うとしても過去最大の1.5倍程度の安全柵のみ)。
- **呼出計測点**: response.outputの`web_search_call`を1件ずつ保存(action.type、queries/query、順序、URL)。これにより**呼出単位ログでFact別推定の精度が上がる(Fact対応は依然heuristic)**。
- **案2のB3試験版(R-06)**: `run_storyline_b3_selection`と**同じ検証・技術retry構造**で関数を複製(全IDのテスト網羅チェック+1回の技術retry)。ID抽出regexは`[UNVERIFIED]`を受け付ける。違いは「検証済み」の語とタグに限る。検証前draftの描画欄=`build_verified_ledger_text`と同じ欄+Researcherの`ambiguity`(事前固定・記録)。
- **モデル(R-16)**: 新規検証=`vfl01.MODEL`、各呼出の`response.model`を記録しM0の`model_id_actual`と一致をCP1で確認。B3=`routing.require_model("FAMILY_X_STORYLINE_B3")`経由で返却modelを照合。報告に使用モデル記載(25節)。
- 検証結果の再利用: 検証済みFact(fact_id x draft sha256)は再検索しない。

## 4-3 案2の再選定loop(ユーザー§4の8手順を忠実に)
1. Research候補全体を渡して初回B3。
2. 選定Factだけを独立検証。
3. REJECTEDがあれば**機械的に削除せず**、B3へ(不合格Factのid・verdict・verification_notes、検証済み他Factのverdict・notes、未検証候補)を extra_note で返す。**再選定時の候補本文はその時点の状態をタグで示す**(`[VERIFIED]`/`[AMBIGUOUS - 断定禁止…]`/`[UNVERIFIED]`)。**REJECTEDは候補本文から外し、extra_noteに理由+「選定禁止」を明記**。REJECTED IDが選ばれたら機械的に検知して**技術的失敗**として扱う(B3による再評価は維持)。(R-06)
4. B3がStorylineを再評価(REJECTEDなしで成立するか/別Fact追加が要るか)。
5. 新規選定Factだけを検証。
6. 最大2回の再選定。上限到達または成立しない場合は**未成立として記録**し、品質を犠牲に確定しない(確定ファイルを出さない)。
- AMBIGUOUSは再選定トリガーにしない。**AMBIGUOUS断定の測定(R-07、測定のみ)**: 「中心Fact」=Storyline行が言及するFactと事前定義し、全方式で①Storyline行/Selected BriefがAMBIGUOUS Factを断定している件数、②M0/M0bとの比を記録(JPY0、Sonnet+Fable独立判定)。**0でなければTrial後のユーザー判断事項**(AMBIGUOUS時の再生成ルール追加は新仕様のため設計に入れない)。
- 最終Ledgerは選定Factの検証済み分のみで`vfl01.build_verified_ledger_text`により組み立て直す(未検証の非選定Factは混ぜない)。

## 4-4 評価手順
- 記録項目: LLM/検索費用別、呼出数・クエリ数(新規計測)、Fact verdict遷移(VERIFIED維持/AMBIGUOUS化/REJECTED/昇格)、B3の採用Fact・主題・展開・結論、再選定回数・追加費用・未成立。
- **B3構成差と品質(R-10)**: 機械指標(採用FactのJaccard、storyline文差)+3段階ルーブリック(軽微/中程度/重大)。**M0とM0bのペアをブラインド判定対象に混ぜ**、同じ評価者・基準で判定する。品質はM0との一対比較(良い/同等/悪い)x3観点(面白さ・一貫性・事実整合)。**判定ルールを事前登録**(例: M0-M0b差が中程度以上の記事では、方式差が中程度以下なら方式効果と認めない)。案2出力にはREJECTED痕跡が出るため完全ブラインドは困難、その限界を記録。構成差の大きさと品質の良し悪しは別列。
- 判定者: 机上=Sonnet、独立=Fable、重大判定または不一致のときだけOpus。
- ばらつき切り分け: M0とM0b(B3)、M0とM0'(Ledger検証)の差を自然ばらつきの基準とする。
- **M2とM3の判定差の帰属(R-12)**: 同Factの判定差を上限効果とみなすのは、そのFactでM2呼出数が上限超過の場合のみ。それ以外はVerifierばらつき。
- **既知欠陥の記録(R-08)**: 既知欠陥(Coffee F12/F07/F16・F17、inbound F05/F12、streaming F07)x方式を3値で記録: (a)選定され検出 (b)選定され見逃し=NG (c)非選定(最終台帳・Briefに含まれないことを確認)。
- **故障注入プローブ(任意・別小実験、費用を別行で見積、承認に含めて提示)**: M0/M0bの採用Factの数値・scope・日付を1か所だけ改変した複製を記事あたり2〜3件作り、上限なし/上限付きVerifierに検証させる(期待=REJECTED)。B3比較には混ぜない。
- 5記事では低頻度の重大誤りを統計的に否定できない(ユーザー§7どおり)。

## 4-5 Fact Lock / RFとの整合
- JPY0範囲(R-03/R-11): 各方式のTrial出力dir(**er082配下へ複製したもの**)に対し、`er053_b3_deterministic_producer_01.annot.produce_annotated_b3`(LLM 0 call)と`validate_annotated_b3`、RFの`parse_ledger_complete`による完全性検査のみ。**producerは入力dirの注記artifact削除・`fact_selection_evidence.json`上書きを行うため、Production/既存成果物dirに対して直接実行しない**。
- Stage 3(任意、費用を別行で見積、承認に含めて提示): Coffee・inboundのM0記事に**全台帳/縮小台帳の両方**でRFを実行しflag差を見る。`rq.save_queue`は既定root(`review_queue/post_en`、共用)を使わず`root=`にer082配下を明示。台帳縮小でRF検知力が下がるか厳しくなるかは未確認(R-11)。**`[UNVERIFIED]`を台帳に混ぜる案は不可**。

## 4-6 受入条件判定表(ユーザー§7)
| 条件 | 判定方法 |
|---|---|
| 採用Factに重大誤りが残らない | 既知欠陥3値記録(R-08)+故障注入プローブ(任意)+Sonnet/Fable独立確認。(b)見逃しが残れば当該方式NG |
| VERIFIED降格は根拠付き | 降格全件のverification_notes根拠と元verdictの対照。基準=M0'(R-04) |
| 不確実なFactをVERIFIEDに昇格させない | AMBIGUOUS/REJECTED→VERIFIED遷移が0 |
| B3ストーリー品質維持 | 4-4の構成差+一対比較、M0bとの比較 |
| AMBIGUOUS断定の非流入(R-07、測定) | Storyline行/BriefがAMBIGUOUSを断定する件数。0でなければUSER_DECISION |
| 実測総費用で削減 | 表2本番換算(Research+検証+B3+再選定、共有分も帰属。R-05)の削減率。Trial追加支出は承認額管理用で別 |
| Fact Lock・RF整合 | 契約検証PASS(4-5) |
| 5記事の傾向と例外 | 記事別表+Fact数・採用比率との関係 |

## 4-7 隔離(11-7)
- Production既定動作は不変。Trial scriptのみ。`CURRENT_SPEC.md`に未採用案を書かない。Productionに配線しない。出力は`er082_output/`のみ。新flagは作らない純粋なOffline Trial(11-7例外は不要)。
- **sha不変チェック(R-03)**: 対象=Productionコード(runner、B3、vfl01、routing、efam等)+**再利用する既存成果物**(Coffee run_fxpw_01、er052 stage_r 4記事のdraft/ledger/B3)。実行前後で比較、変化でSTOP。
- 共用Review Queue(`review_queue/post_en`)に書かない。

## 4-8 実行順序・STOP条件・CP(R-14)
- CP0: ユーザー費用承認(#104)。Opus条件Aレビューは実施済み(本v2に反映)。
- CP1: harness実装とJPY0 dry-run(保存出力でstub test、Prompt組立、契約検証、**web_search 1回が費用計上されるtest**、`response.model`照合、公式pricing確認[R-09])。承認待ちと並行可。
- **CP2=1a**: **冒頭でCoffee M2を1本だけ流してharness結合確認(smoke)**。続いてCoffee(M0b、M0'、M1、M3)、inbound(再選定loopがほぼ確実に動く記事)。→ Fable確認。
- **1a→1b進行条件(事前定義)**: 上限遵守率の記録が取れている / 再選定loopが仕様どおり動作 / 実測費用÷見積≦1.3 / Production・再利用成果物sha不変。
- CP3=1b: **streaming(先頭。案1で採用VERIFIED F04が失われる危険の主要例)**→ openai → central。openai/centralはM1呼出ログで上限非拘束を確認、拘束時のみStage 2のM0'。
- CP4: 集計・構成差判定・Fableレビュー・Status分類(REJECTED/VALIDATED/USER_DECISION_REQUIRED)→ STOP報告。
- STOP条件: 累計実費が承認額に達する(web_search費用込みguard)、承認前に有料呼出、STOP_NOTICE、外部停止、Production関連/再利用成果物のsha変化、原因不明rc≠0が2回、再選定上限到達時に確定させようとする動作。
- 実行は1記事ずつ。記事単位の費用ガード(承認額の記事按分)。

## 4-9 記事選定(R-15)
5記事(Coffee、openai_copyright、inbound_tourism、streaming_price、central_bank_mortgage)は**差し替えない**。理由(Opus R-15): Meta=基準がgpt-5.6-lunaで現行gpt-6-lunaと異なり交絡/byd=全VERIFIEDで検出力が増えない/semiconductor=採用比率約0.83で案2の差が出にくくstreamingと役割重複/openai・central=誤降格の測定と、上限が効かない記事の費用・構成確認の役割。見逃し検出力の不足は故障注入プローブで補う。

# 6. 案1+案2の相乗効果(事前の机上所見、実測は後。v1維持)
- 案1が削る反復(fxpw F16/F17)はB3が採用しないFactで起きており、案2で既に検証対象外。追加削減は小さい(数円未満〜約2円)見込み。ただし選定Factに採用VERIFIEDの反復があれば(streaming F04型)案1の効果が案2の後でも残る。Trialで測る。
- v2見積(COST_ESTIMATE_02表2)の本番換算削減率(期待)は5記事合計で案1約3%/案2約10%/案1+案2約11%(Coffeeのみ案2で約32%)。
- 70円目標: RLCO提案書のText工程JPY72.64(Coffee)が基準。音声工程は未実測。Research/Ledger改善だけでは70円に届かない見込みという所見は維持(音声実測が出るまで判定しない)。
