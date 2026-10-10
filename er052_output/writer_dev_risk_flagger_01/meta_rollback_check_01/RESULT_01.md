# RESULT_01: WRITER-RISK-FLAGGER-META-ROLLBACK-CHECK-01(精度確認のみ、Trial/DEV、2026-10-10)

**結果分類: NOT_DETECTED。方向反転として正しく認識したか: No。** 仕様変更・Prompt改善・追加Trial・Production変更は一切行っていない(改善提案も書かない)。以降の「実測」は実際のAPI応答/ファイルから確認した値、【推測】は解釈。

## 0. 対象(実測)
- 記事: `er019_output/meta/run_03/b1b/article.md`(Advanced B1b EN)sha256 `cab7f5f3a147b3944558b738fdcb8888f5c754267d47cf177a9438f3d400b327`、ファイル日時 2026-09-29 15:46(Production相当run、er019 run_03)。同一shaの複製が `er019_output/family_x_refresh_e2e_01/meta/run_03/b1b/article.md` にある。casebank MUSE-HC-012/K01の出所(open233_prod_e2e_02 meta_run03_advanced)と同じ系統の記事(rollback_misread_history_01.md #2/#4)。
- 対象文はs23(29文中): 「The company also restored the human concierge feature to the way it had been before, at least for now.」
- 台帳: `er019_output/meta/run_03/ledger/verified_fact_ledger.txt` sha256 `6e271bb24fdf3a587bd803d80cec5d32aaaaeb047ca3389c1597283aa3719db4`。
- Fact完全性: 見出し行数(広義`[`始まり)15 = HDR正規表現一致15 = parsed 15 = MUSE-HC-001..015(連番)。一致、API前確認済み(`precheck_01.json`)。
- 台帳のロールバック関連Fact原文(ラベル・評価語なし、逐語): 
  - MUSE-HC-012: 「MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。」(notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。)
  - MUSE-HC-014 notes_for_writer: 「公開済みの一般機能と、ロールバックされた人間コンシェルジュ実験を区別する。」

## 1. 条件(実測)
A3 sha `9d995042...`/A4 sha `c87b95e5...`(`antenna_system(level)`のsha、POST-EN-TRIAL-01と一致)。モデル gpt-6.1-sol(応答のmodel_id実測: gpt-6.1-sol)、effort=medium、既存英語splitter、完全台帳、各attempts=1・valid JSON・再試行なし。最新モデル原則: POST-EN-TRIAL-01/ANTENNA-TRIAL-01と同一構成のため、条件比較可能性を優先(新たな最新性の再確認はしていない)。Promptにラベル・誘導語・記事評価を加えていない。強制TopN/閾値/A5・A6/Rewrite/再生成/STOP処理なし。実行はA3・A4同時刻 2026-10-10T12:13:17+0900開始。
- 事前見積: 中央 A3 JPY2.29 + A4 JPY2.59 = JPY4.88、高位 JPY7.48(基準JPY20以内)。
- 実測費用: A3 JPY2.726(in 5060 / out 692 tok、reasoning 248、cached 0、15.4秒)、A4 JPY2.678(in 5210 / out 632、reasoning 298、cached 0、14.7秒)。合計 **JPY5.405**。見積内。
- 実行上の注記: 初回実行時、driverがpost_en_common由来の`HERE`変数を上書きしたため、出力(結果JSON・raw・cost ledger・precheck)が一時的に`post_en_trial_01/`配下に新規作成された。既存ファイルの上書きはなく、新規ファイルのみを直ちに本ディレクトリへ移動し、driverを修正済み。post_en_trial_01の既存ファイルは未変更(git status上、同ディレクトリの新規untrackedは残っていない)。

## 2. 表(ユーザー指定)

| 項目 | A3 | A4 |
|---|---|---|
| 対象文(s23)をFlagしたか | **No** | **No** |
| type | -(該当なし) | -(該当なし) |
| confidence | - | - |
| related Fact | - | - |
| reason | -(s23へのFlagなし) | -(s23へのFlagなし) |

方向反転として正しく認識したか: **No**(未Flag。s23に隣接する「restored…」を含む別文へのFlagも無く、restore/put back方向の指摘は両者ともゼロ)。

## 3. 全Flag一覧(全て重大扱い、s23以外。rollback/withdrawal/hold↔restoreの方向を扱うものは無い)
A3: 4件 / A4: 3件 / Union 4文 / A3∩A4 3文(s3, s14, s15)。

| 文ID | 文(抜粋) | A3 type conf | A4 type conf | Related Fact | Reason(question原文) |
|---|---|---|---|---|---|
| s3 | Behind a service that lets people ask AI to make phone calls, humans were actually making the calls. | 主体対象入替 0.50 | 主体対象入替 0.55 | HC-006 | A3: 「humans were actually making the calls」はサービスの電話全般を人間が担当したとも読め、台帳の「一部の電話」「テスト」より範囲を広げているのではありませんか。/ A4: 同旨(電話全般を人間が担当していたと読め、「一部の電話」「テスト」という限定より範囲が広い)。 |
| s14 | And if this was not properly explained, users had no way to know whether they were talking to AI or a person. | 主体対象入替 0.94 | 不在断定 0.88 | A3: HC-004,006,012 / A4: HC-006,012 | A3: 依頼したユーザー自身が通話していたことを示すが、台帳ではAIまたは契約スタッフが企業・店舗と通話する仕組みであり、通話の当事者が入れ替わっているのではありませんか。/ A4: 台帳の「ユーザーに代わって契約スタッフが電話を担当した」「適切な開示がなかった」を、ユーザー自身が通話し、相手を知る手段もなかったという別の事実に変えているのではありませんか。 |
| s15 | They were enjoying the convenience of AI, only to find a human on the other end of the call without realizing it. | 主体対象入替 0.88 | 主体対象入替 0.87 | A3: HC-004,006 / A4: HC-006,012 | A3: 「a human on the other end of the call」は利用者の通話相手が人間だったと読めるが、台帳の人間は利用者に代わって企業・店舗へ電話する契約スタッフであり、役割が入れ替わっているのではありませんか。/ A4: 同旨(発信者と相手の関係が入れ替わっている)。 |
| s19 | News reports also cited an employee's report that human staff made inappropriate comments about race during calls to negotiate internet or cable fees. | 主体対象入替 0.38 | - | HC-011 | A3: 「human staff」「during calls」は複数スタッフ・複数通話とも読め、台帳の「人間の契約スタッフによる発言」「料金交渉の1件」という個別事例より範囲を広げているのではありませんか。 |

HC-012は s14(両方)・s15(A4)のrelated Factに現れるが、指摘内容は「通話当事者の入れ替わり」「開示なし」であり、機能のロールバック/復元の方向とは無関係(Partial基準も満たさない)。理由欄に「撤回/停止/保留→復元/再開」の向きへの言及は全Flagの中に無い(実測: 全7 Flag理由を確認)。

## 4. 判定(Fable補足の定義による)
対象文(s23)は未Flag、他文でも方向反転の指摘なし、HC-012関連で出た指摘は別問題 → **NOT_DETECTED**。方向反転の認識: **No**。
【推測・断定しない】A3/A4とも1回ずつの測定(N=1×2)であり、再現性・一般化は本確認では評価していない。

## 5. 実行・変更範囲
- Production変更ゼロ。A3/A4 prompt・既存コード(detectors/、antenna_trial_01/、post_en_trial_01/)は変更なし。SSOT・ACTIVE_TASK・RESULT_PACKET・git操作は未実施(統合委任で実施)。
- 追加ファイルは本ディレクトリのみ: `rb_driver.py`、`precheck_01.json`、`cost_ledger_rb_01.jsonl`、`inputs/`(article・ledgerの複製、sha同一)、`runs/`(A3/A4 result JSON、d2結果jsonl、raw応答jsonl、A3_stdout.txt)。
