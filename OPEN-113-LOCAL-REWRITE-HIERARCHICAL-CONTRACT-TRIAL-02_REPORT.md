# OPEN-113-LOCAL-REWRITE-HIERARCHICAL-CONTRACT-TRIAL-02 報告

管理ID: OPEN-113-LOCAL-REWRITE-HIERARCHICAL-CONTRACT-TRIAL-02
実施日: 2026-09-04
対象: Local Rewrite Prompt契約の改善のみ(Trial専用、Production未変更)
コード: `er011_open113_local_rewrite_hierarchical_contract_trial_02.py`
生データ: `er011_output/open113_local_rewrite_hierarchical_contract_trial_02/`
前提: Trial-01(`OPEN-113-LOCAL-REWRITE-CONTRACT-TIGHTENING-TRIAL-01_REPORT.md`)で発見した「過剰DELETE傾向」というtrade-offを、優先順位を明示的な階層(STEP1〜STEP4)として固定することで解消できるかを検証。

## 1. 最終Status

**REJECTED**

今回Trialした「STEP1(意味維持最小REWRITE)→STEP2(安全な縮退REWRITE)→STEP3(DELETE)→STEP4(NG)」という階層優先順位契約は、狙った過剰DELETEの改善を一切達成できず、それどころか既知の重複ケース自体を**未解決**にする新しい退行を起こした。この契約案はこのままでは採用不可と判断する。ただしOPEN-113自体(Local Rewriteの重複・過剰削除trade-off)は依然未解決であり、次にどう進めるかはユーザー判断が必要(17節参照)。

## 2. 新しい優先順位契約

`REWRITE_SYSTEM_PROMPT_V3` + `ATTEMPT{1,2,3}_TEMPLATE_V3`(Trial専用、Production未反映)。既存の3段階escalation構造(1attemptにつきgenerate 1回+check 1回、最大3attempt)はそのまま維持。

- モデルに「STEP1→STEP2→STEP3→STEP4の順に評価し、最初に当てはまった段階で止まる」ことを明示指示。
- 出力形式を2行固定にし、1行目に選択STEPタグ(STEP1〜STEP4)を必須で出させることで、どの段階が選ばれたかを機械的に記録できるようにした。
- STEP4(NG)を新設: STEP1〜3すべて不成立なら、無理に修正せず`LOCAL_REWRITE_NG`を返す正式な選択肢とした。
- Point全体をcontextとして渡す点、別Fact置換禁止・既出内容の言い換え禁止などの禁止事項はTrial-01から維持。
- ケース固有のhardcodeは一切入れていない(4ケースすべてに同一の汎用契約を適用)。

## 3. No.18 B1結果(既知の意味重複ケース)

**未解決(regression)。** attempt 1〜3のすべてでSTEP1またはSTEP2のREWRITEを選び続け、3回ともLedger基準を満たせなかった(`LEDGER_DEVIATION`)。3回目(最終attempt)でも契約通りSTEP3へ降格せず、`resolved: false`・`human_review_required: true`のまま終了した。

その結果、Local Rewriteは何も適用しなかった(元記事は無編集のまま)。記事全文の再判定は`LEDGER_DEVIATION`(MAJOR 2件)で、うち1件は未解決のまま残った対象文そのもの、もう1件は今回のRewrite対象と無関係な別セクション("Everyday expectations can make ignoring it feel difficult.")だった(16節参照、こちらは既知の別課題)。

Trial-01ではこの同じケースが**1回目のattemptでDELETEを選び、即座にLedger compliantで解決**していた。今回はそれよりも明確に悪化した。

## 4. No.9 #2結果("...tired of being guided by the screen.")

**過剰DELETEが再発(未改善)。** attempt 1回目でいきなりSTEP3(DELETE)を選択し、そのままLedger compliantで確定した。STEP1/STEP2は試された形跡がなく、Trial-01と全く同じ結果(DELETE)になった。過去に実在した安全な縮退REWRITE("...many customers are increasingly pushing back against digital prompts to tip.")と同等の候補は、今回も選ばれなかった。

## 5. No.18 A2結果("always"→"necessarily"の1語修正ケース)

**過剰DELETEが再発(未改善)。** attempt 1回目でいきなりSTEP3(DELETE)を選択し、文末の一文全体を削除した。過去に実際に機能していた1語だけのcertainty修正("does not always mean" → "does not necessarily mean")には到達せず、Trial-01と全く同じDELETE結果になった。

## 6. No.9 #1結果(範囲限定REWRITEが有効だったケース)

**期待通りSTEP1で解決。** attempt 1回目でSTEP1を選び、"The feeling of 'I must leave a tip' when a digital screen prompts a tip also fell..."という、元文の構造・役割をほぼそのまま保った最小限の条件限定REWRITEで即座にLedger compliantとなった。ただしこのケースはTrial-01でも既に安全なREWRITEで解決できていた「非診断的」なコントロールケースであり、今回の階層契約が過剰DELETE問題を解決したことの証明にはならない。

## 7. 各ケースでSTEP 1/2/3/4のどれを選んだか

| ケース | 選択STEP | 期待していたSTEP | 一致 |
|---|---|---|---|
| No.18 B1(既知重複) | 未解決(STEP1/2を3回試行後もLedger不適合のまま) | STEP2またはSTEP3 | **不一致(悪化)** |
| No.9 #2 | STEP3(DELETE) | STEP1またはSTEP2 | **不一致(過剰DELETE)** |
| No.18 A2 | STEP3(DELETE) | STEP1 | **不一致(過剰DELETE)** |
| No.9 #1 | STEP1 | STEP1 | 一致 |

4ケース中、期待通りだったのは1件のみ(かつ非診断的なコントロールケース)。STEP4(NG)は一度も選ばれなかった。

## 8. 意味維持

No.9 #1は元文の central meaning・役割を保った良い最小編集だった。一方、No.9 #2・No.18 A2はSTEP1/STEP2を試みた形跡なく直接DELETEされたため、元文が持っていた情報(チップ画面への心理的疲労感、「常にではない」という限定表現)がPointから完全に失われた。No.18 B1は何も変更されなかったため、元の意味は保たれているが、Ledger逸脱そのものが未解消のまま残っている。

## 9. Point全体の流れ

No.9・No.18 A2いずれも削除後の前後文のつながり自体は不自然ではなかった(文法的な破綻はなし)。No.18 B1は記事が無編集のため、当然流れも変化なし(ただしLedger逸脱が残ったまま)。

## 10. 重複

新しい意味重複の発生は確認されなかった。No.18 B1は変更が適用されなかったため、既存文との重複も新規には発生していない(=Trial-01が解決した「重複解消」という成果そのものが、今回は「そもそも変更しない」という形で維持されているに過ぎず、重複を積極的に防いだわけではない)。

## 11. 過剰DELETE

**未改善。** 4件中2件(No.9 #2、No.18 A2)で、Trial-01と全く同じ過剰DELETEが再発した。階層的な優先順位の明示だけでは、モデルにSTEP1/STEP2を実際に試させる効果がなく、「安全そうならとりあえずDELETE」という挙動を止められなかった。

## 12. Ledger compliance

No.9・No.18 A2の各fixtureの記事全文再判定はいずれも`LEDGER_COMPLIANT`(MAJOR 0件、MINORのみ)。No.18 B1のみ`LEDGER_DEVIATION`(MAJOR 2件、うち1件は未解決の対象文そのもの)。Fact捏造や別Factへの誤った置換は確認されなかった(Fact安全性そのものは破壊されていない)。

## 13. API call

既存アーキテクチャ(1attemptにつきgenerate 1回+check 1回、最大3attempt)のまま、新しい呼び出し箇所は追加していない。ただし今回はNo.18 B1が3回ともLedger不適合で終わったため、そのfixtureだけでattempt上限いっぱいの6回(+全文recheck1回=計7回)を消費した(Trial-01の同ケースはattempt1回で解決し計3回)。fixture合計: 7+5+3=15回(+切り分け検証で1回追加、16節参照)。呼び出し箇所数・上限自体は無変更(MUST条件「API call追加なし」は形式的には満たすが、実際の消費量は増えている)。

## 14. Prompt-onlyで十分そうか

**不十分と判断する。** 今回、モデルに「STEP1を必ず先に試せ」と明示しても、既知ケースでは3回とも同じSTEP1/STEP2帯から抜け出せず、逆に「これが最終attemptだ、必要ならSTEP3を使え」という明示的な退避指示(ATTEMPT3_TEMPLATE_V3)すら効かなかった。一方で、Trial-01の「DELETEを気軽な選択肢として許可する」契約は、過剰DELETEという別の失敗モードを生んだ。この2つのTrialを通じて、少なくとも今回試した2種類のprompt構造(許可型/階層型)のいずれも、DELETEとREWRITEの選択を安定的に制御できていない。

## 15. 追加QAが必要そうか

判断が割れる。新しいValidatorを追加すれば「STEP1/2で解決可能な安全なREWRITE案が実在するかどうか」を機械的に検証してからDELETEを許可する、といった制御は原理的に可能だが、これは今回のTrial-02のスコープ(禁止事項: 新Validator追加禁止)には含めていない。プロンプトの言い回しだけでの制御は2回のTrialで期待した効果を出せておらず、これ以上のprompt-only微調整を繰り返すより、追加QAの是非も含めてユーザーに判断を仰ぐべき段階だと考える。

## 16. Ledger Checker判定揺れ Open Item候補

Trial-01で確認された「Ledger Deviation Checkerの記事全文判定が、Rewrite対象と無関係な箇所でも揺れる」という現象について、今回追加で1回、同一の未変更記事に対して`run_deviation_check`を再実行した。結果は前回と全く同じ("Clear response windows could ease it."と"Everyday expectations can make ignoring it feel difficult."の2件がMAJOR)で、少なくとも今回はrun-to-run変動ではなく、**この記事に対しては安定して2件目のMAJORを検出する**ことを確認した。これはTrial-01時点の「非決定的なノイズ」という仮説を弱め、「Production側の元の全文判定がこの2件目を見落としていた可能性」または「Checkerのモデル・prompt側の判定基準が当時と現在で変化した可能性」を示唆する。

`OPEN_ITEMS.md`を確認したところ、この論点(Ledger Deviation Checkerの全文判定の再現性・安定性)はまだ独立したOpen Itemとして登録されていない。禁止事項10節・9節の指示に従い、**今回は実装を一切行わず**、新規Open Item候補(仮ID: OPEN-114)として報告のみ行う。ユーザーが承認した場合のみ、次回別タスクとして正式登録・調査する。

## 17. USER_DECISION_REQUIRED

Trial-02自体の結論(階層契約はREJECTED)は明確だが、OPEN-113という元の課題(Local RewriteのDELETE/REWRITE選択が安定しない)はまだ未解決。次にどう進めるか、以下からユーザーに選んでいただく必要がある。

- (a) Trial-01の「DELETE許可型」契約とTrial-02の「階層型」契約、どちらも不採用とし、Local Rewrite Prompt契約のprompt-only改善はここでいったん打ち切る(`DEFERRED`)。既知の重複バグ・過剰DELETEどちらも一定のリスクとして許容し、量産は現行Production契約のまま継続する。
- (b) 16節のLedger Checker全文判定の安定性(OPEN-114候補)を先に切り分け調査してから、Local Rewrite契約の再設計を検討する。
- (c) Prompt文言だけでの制御という前提そのものを再検討し、15節で触れた「安全なREWRITE案が実在するかを検証してからDELETEを許可する」ような軽量な追加チェック(新Validator)の実装可否を、あらためて正式に検討する。
- (d) 上記いずれでもなく、別の方向性(例: そもそもTrial-01のDELETE許可型契約を、"既出内容と重複しない場合に限りDELETEより先に必ずREWRITE候補を1案出させる"という2段階生成に変える等)で追加Trialを依頼する。

## 18. Production変更なし確認

確認済み。`er010_ledger_local_rewrite_09.py`・`er003_v1_n3_01_articles_generate.py`はいずれも一切編集していない(新規ファイル`er011_open113_local_rewrite_hierarchical_contract_trial_02.py`の追加のみ)。APPROVED_FOR_PRODUCTION・PRODUCTION_WIREDのいずれも実施していない。`OPEN_ITEMS.md`のOPEN-113行はcloseせず、Trial-02の結果のみ追記した。

## 19. 次アクション

ユーザーが17節の(a)/(b)/(c)/(d)のいずれかを選ぶまで、このTrialはこれ以上進めない。

---

今回Status: **REJECTED**(Trial-02の階層契約案そのものについて)
OPEN-113: Open継続(closeせず、Trial-01・Trial-02の結果のみ`OPEN_ITEMS.md`へ追記済み)
意味維持最小REWRITE: 4件中1件(No.9 #1)のみ機能。過剰DELETEが疑われた2件(No.9 #2、No.18 A2)では機能せず
安全な縮退REWRITE: 実質的に一度も選択されず(既知ケースでSTEP2は試みられたがLedger不適合で失敗)
DELETE: 4件中2件で発生、うち2件とも過剰DELETE(改善なし)。既知ケースはDELETEに到達できず未解決という新しい問題が発生
NG fallback: 一度も選択されず(既知ケースは"未解決"のまま終了し、正式なNG判定にも落ちなかった)
追加QA: 今回は未実装。必要性の判断はユーザーへ(15節)
Production変更: なし
次に進めてよい工程: なし(ユーザー判断待ち)
