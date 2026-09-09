# LEDGER-DEVIATION-CHECKER-SEARCH-COST-RECONCILIATION-01

管理ID: LEDGER-DEVIATION-CHECKER-SEARCH-COST-RECONCILIATION-01(Sonnet、**読み取り専用調査**、
コード・Prompt・SSOT編集/Production変更/API呼び出し/Git操作は一切行っていない)。

## 0. 最重要の訂正(前提の誤り)

`EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-02_REPORT.md` §6は「費用が前回比で増加した主因は、
Ledger Deviation Checker(`vfl01.run_deviation_check`、Production primitive、無変更)がattemptごとに
web_search呼び出し(11/8/8回)を行い、入力トークンが1回あたり6万〜10万に達したため」と記述しているが、
**この帰属はコード・実ログと矛盾しており誤りである**。根拠:

- `er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`(603〜626行目)の`client.responses.create()`
  呼び出しに`tools=`引数自体が存在しない(web_search未宣言)。同ファイル内で`tools=[{"type": "web_search"}]`が
  現れるのは`run_researcher`(175行目)と`run_verification`(258行目、いずれもLedger生成時の1回きりの
  Research/Verification stage)のみで、`run_deviation_check`には一度も現れない。
- Trial-02の実ログで直接照合した: `b1b_run01_attempt{1,2,3}/fact_qa.json`の`response_id`
  (`resp_0e6ff7a49df4dc29...`/`resp_023f856ce034...`/`resp_0e9963a8632c...`)は、
  `raw_usage_log_4v_writer.jsonl`中でweb_search_call_count=11/8/8を記録した行の`response_id`と
  **完全一致**した。この`fact_qa.json`は`run_fact_check_a_prime_4v()`(4V Trial-02スクリプト191〜225行目)
  →`er012_b_family_voices_production_01.py::run_fact_checker()`→`er002_ja_web_research_r3.py::
  make_fact_checker_fn()`(258〜290行目、`tools=[{"type": "web_search"}]`を明示的に宣言)が生成した
  **Fact Checker A'(独立Web検索Fact Checker)** の応答であり、Ledger Deviation Checkerとは別のProduction
  primitiveである。
- したがって27回(11+8+8)のweb_search呼び出しは、**MAX_WRITER_ATTEMPTS=3ループ(Analytical Leakage
  Check是正の全文書き直しリトライ)の中でFact Checker A'が毎回1回ずつ呼ばれた**ことによるものであり、
  Ledger Deviation Checker自体は同じ27回の呼び出しの中で**web_search呼び出し0回**である。

以下、この訂正済みの事実に基づき調査事項へ回答する。

## 1. 各Checkerの本来の目的(SSOT引用)

`CURRENT_SPEC.md`680〜681行目(「Fact Safety(共通)」行、`DECIDED`/`PRODUCTION_WIRED`、
根拠ER-003-A2-B1-N3-01・ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02・
ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12)を引用:

> 「Verified Fact Ledger(記事ごとに1つ、A2/B1で共有)→独立Fact Checker(web検索付き、
> `PASS`/`REVIEW_REQUIRED`/`FAIL`の3値)→Ledger Deviation Check(`LEDGER_COMPLIANT`/`LEDGER_DEVIATION`)
> の3段構成」
>
> 「**役割の区別**: Fact Checkerは独立Web検索によるexternal factとの整合性判定、Ledger Deviation
> CheckerはVerified Fact Ledgerとの整合性判定であり、両者のMAJOR/blocking判定を混同しない」

すなわち設計上、**Web検索を行うのはFact Checker A'だけ**であり、Ledger Deviation Checkerは
「記事本文がすでに検証済みのLedgerテキストと意味的に整合しているか」を、Ledger本文とのLLM推論的照合
だけで判定する(外部検索なし)。この役割分担はTrial-02固有の設計ではなく、通常News/Hanshin等
Production全記事で使われている既存の恒久設計。

## 2. 実ログ内訳(訂正後、Fact Checker A'の実体)

| attempt | 呼び出し元 | response_id(抜粋) | web_search呼出数 | input tokens | verdict |
|---|---|---|---|---|---|
| 1 | Fact Checker A' | resp_0e6ff7a49...73 | 11 | 100,061 | PASS |
| 2 | Fact Checker A' | resp_023f856ce...ae | 8 | 79,929 | PASS |
| 3 | Fact Checker A' | resp_0e9963a86...ca | 8 | 64,150 | PASS |

各回とも検索対象は、記事内で言及されるexternal citation群(例: Hilton「6 weeks→5 days」採用短縮統計、
CVS/HireVue/Affectivaの`Baker` Massachusetts訴訟和解、BBC Worklife「gestures/expressions」記事、
NYC Local Law 144、EU AI Act Annex III、Reuters Amazonチェス部主将のバイアス事例、
Paylocity/LabManager/Resume.org採用AI利用率調査、日本のAI法制)。いずれも記事本文の具体的主張の
外部裏付け確認であり、Ledger内容とは独立にreal worldソースを検索している(Fact Checkerの設計どおり)。

Ledger Deviation Checker自体(`run_deviation_check`、hook_aware=True)は各attemptで最低1回
(`run_ledger_deviation_and_local_rewrite`867行目)呼ばれ、attempt1はMINOR×3のみでLocal Rewrite不発、
attempt2/3も同様にMINORのみ(4V Trial-02 Report §3)。MAJORが出ずLocal Rewriteループ
(`while major_items ...`)が不発だったため、window再検証等の追加呼び出しも発生していない。
いずれの呼び出しもtools未宣言のためweb_search 0回。

## 3. 同一Ledgerへの再検証か、新規claimのみの検証か

- Ledgerは`ai_screening_ledger_trial_01`をTrial-01からそのまま再利用(4V Trial-02 Report §2、
  「新規Research呼び出しなし」)。3 attemptとも**同一のverified_ledger_text**を使用。
- Ledger Deviation Checkerは、attemptごとに**記事全文**(article_text)とLedger全文の突合を行う
  (`run_ledger_deviation_and_local_rewrite`、article_text単位、差分抽出なし)。ただしMAJORが出た
  claimのみ`_run_check_window`で該当sentenceの窓だけ再検証する仕組みは既に存在する(局所化済み、
  ただし今回は不発)。
- Fact Checker A'は、attemptごとに**書き直された記事全文**をゼロから独立検索する
  (`b1prod.run_fact_checker(TOPIC_JA, article_text, ...)`、直前attemptの検索結果・claimリストは
  一切引き継がない設計、`make_fact_checker_fn`docstring: 「writerの会話状態を一切引き継がない、
  新規・独立したResponses API呼び出し」)。

## 4. attempt間の重複検索

Fact Checker A'の実クエリ文字列を3 attempt間で完全一致比較した結果:

| 比較 | クエリ完全一致数 | 各attemptクエリ数 |
|---|---|---|
| attempt1(32件)∩attempt2(25件) | 0 | — |
| attempt1(32件)∩attempt3(18件) | 0 | — |
| attempt2∩attempt3 | 0 | — |

文字列としての完全一致は0%だが、**対象claim(トピック)は高頻度に重複**している。例:
Hilton「6 weeks→5 days」採用短縮統計はattempt1/2/3すべてで異なる言い回し
(`"6 weeks to 5 days" Hilton recruitment` / `Hilton AI recruitment six weeks five days...` /
`Hilton AI recruitment five days six weeks IBM 30%...`)で検索されている。同様にCVS/HireVue/Baker訴訟、
BBC Worklife「gestures/expressions」記事、NYC Local Law 144、EU AI Act Annex III、Reuters Amazon事例、
Paylocity/LabManager調査、日本のAI法制も3 attemptすべてで別クエリとして再検索されている。これは
「Writer側でLeakage是正のたびに記事全文をゼロから書き直す」設計(`build_leakage_corrective_note_4v`:
「今回はこの記事全文をゼロから新しく書き直してください」)により、参照する事実の集合(=同一Ledgerの
同じcitation群)自体は毎回ほぼ同一のまま、表現(クエリ)だけが変わるためと考えられる。

参考: この「Leakage/Writer retryのたびにFact Checker A'を1回ずつ再度呼ぶ」構造自体は4V Trial-02固有
ではなく、2V版Trial-07(`er012_editorial_b_voices_trial_07.py`)でも同一パターンで既に発生していた
(実測: run01 attempt1=8回・attempt2=6回、run02 attempt1=5回・attempt2=4回、いずれもverdict
REVIEW_REQUIRED)。単発記事(Hanshin A2=12回・B1B=7回、Theme2 B1B=12回・A2=15回等)の水準と比べても、
1回あたりの検索数(4〜17回)自体は異常な値ではない。異常なのは「1記事につきFact Checker A'が
MAX_WRITER_ATTEMPTS回(最大3回)フルで呼ばれる」構造であり、これはB-Family Voices系列の
Analytical Leakage Check是正ループ(既存Trial-07由来、無変更)に起因する。

## 5. キャッシュ不在の理由(設計判断か未実装か)

- Ledger Deviation Checker/Local Rewrite側にはそもそもWeb検索がなくキャッシュの必要自体がない
  (§1参照)。
- Fact Checker A'には、attempt間でのclaim単位・citation単位の検証結果キャッシュは**コード上に存在
  しない**(`run_fact_checker_with_gates`は毎回新規に`make_fact_checker_fn`を呼ぶのみ、Master Audio
  Store(`er006_output/master_audio_store_01/`)のようなcontent-hashベースの`manifest.json`/
  `reuse_telemetry.jsonl`に相当する機構はFact Checker側に存在しない)。
- CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.mdを「cache」「キャッシュ」「web_search」「二重検証」で
  横断検索したが、Fact Checker A'の検証結果キャッシュについて「意図的に導入しない」と明記した
  DECIDED/REJECTED/DEFERREDの記録は見つからなかった。すなわち**設計判断として明記されたものではなく、
  未実装(単に検討・実装されたことがない)** と判断する(不明な部分は不明のまま記載: 過去に非公式に
  検討され記録されなかった可能性は排除できない)。
- 一方、Fact Checker A'が「Ledger入力ミス自体」を検知した実例がDECISION_LOG(2026-09-05
  OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10エントリ)に記録されている(6月14日/17日の日付混同を
  Fact Checkerが検知)。この事実は、Fact Checker A'を単純にLedger単位でキャッシュしてしまうと
  「Ledger自体の誤りを繰り返し見逃す」設計リスクを持つことを示しており、キャッシュ設計を検討する際は
  この機能(Ledger自体の誤り検知)を失わない設計が必須という制約になる。

## 6〜7. 検索回数を減らせる余地(品質を落とさない前提)

- Ledger Deviation Checker/Local Rewriteは既に「MAJOR claim単位の窓検証」という差分検証相当の設計
  になっており(§2)、追加の削減余地は小さい(そもそも¥0)。
- Fact Checker A'側は、**Ledger未変更のattempt間で同一citation/claimを毎回ゼロから再検索している**
  ことが§4で確認された重複。ここに「Ledger内のcitation/claim単位でFact Checker A'の検証結果を
  記事横断・attempt横断でキャッシュする(Ledgerが変わらない限り再利用、Ledger変更時は無効化)」余地が
  ある。ただし§5の制約(Ledger入力ミスそのものの検知機能を失わないこと)を満たす設計(例:
  Ledgerのcitation単位ではなく記事本文の具体的主張[claim]単位でキャッシュし、Ledger再確定時は
  強制再検証する、等)が必要であり、これは既存Fact Checker仕様の変更を伴うため後述のとおり
  USER_DECISION_REQUIRED候補とする。

## 8. 責任分界(二重検証の有無)

同一claimを複数Checkerが別々に外部検索する二重検証は**確認されなかった**。Web検索を行うのは
Fact Checker A'のみ(Ledger Deviation Checker/Local Rewriteは0回)。CURRENT_SPEC.md 680行目が
明記するとおり、この役割分担(Fact Checker=外部web、Ledger Deviation=Ledgerとの内部整合)は
意図的な設計であり、両者のMAJOR/blocking判定も独立(Fact Checker REVIEW_REQUIREDはLedger Deviation
CheckerのMAJORとは無関係、Local Rewriteのトリガーにもならない)。今回の27回はFact Checker A'単体が
MAX_WRITER_ATTEMPTS回呼ばれたことによる「同一Checkerの反復呼び出し」であり、「複数Checkerによる
二重検証」ではない。

## 9. 過去の同種対策のReconciliation

- Ledger Deviation Checkerの判定基準自体は`ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02`で
  精度改善(誤検知削減)のため再設計されているが、これはコスト対策ではなく**検知精度**の話
  (10種類のフラグへの再設計、CURRENT_SPEC.md 681行目)。
- CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSを「web_search」「検証コスト」「cache」「Fact Safety」
  「二重検証」でGrepしたが、Fact Checker A'のweb_search回数・コストそのものを対象にした
  過去のREJECTED/DEFERRED提案は見つからなかった。
- 「Fact Checkerが是正ループのたびに再度呼ばれる」構造自体は2V Trial-07から存在する既知の挙動
  (§4参照)であり、4V Trial-02が新規に作った問題ではない。

## 10. コスト改善案比較表(品質低下を許容する案は除外)

前提: Trial-02実測、Writer stage(21 call、web_search 27回込み)¥74.49、QA stage¥2.08、合計¥76.6。
Fact Checker A'呼び出し3回(1回あたり¥20〜25相当、input token 6〜10万)がコストの大半を占める。

| 候補 | 概要 | 現状コスト(1記事) | 改善後推定 | 削減額/記事 | 1,000記事概算 | 10,000記事概算 | Latency影響 | Fact Safetyリスク | False accept/reject リスク | 実装複雑性 | UDR要否 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A. Fact Checker A'をLedger単位でclaim/citationキャッシュ(Ledger不変ならattempt間再利用、Ledger再確定時は強制無効化) | Ledgerのcitationごとに検証結果を保存し、同一Ledgerを使う次attempt/次記事で再利用 | ¥74.49(writer分) | 概算¥25〜35(初回1回分のみ課金、2回目以降はcache参照+新規claim差分のみ検索) | 約¥40〜50/記事 | 約¥4〜5万円 | 約¥40〜50万円 | 短縮(検索待ち時間減) | 中(§5の制約=Ledger入力ミス検知機能を失わない設計が必須、キャッシュ無効化条件の設計ミスでLedgerの誤りを継続的に見逃す恐れ) | キャッシュ無効化ロジック次第でfalse accept増(古いLedger誤りを検知できない)/実装ミスでfalse reject(誤って再検証不要と判定) | 中(citation正規化・Ledger変更検知・無効化ロジックの新設が必要) | **UDR候補**(Fact Checker仕様変更、Production挙動変更を伴う) |
| B. MAX_WRITER_ATTEMPTS到達前に「Leakage是正のみ」でFact Checker A'を毎回呼ばず、最終確定記事でのみ1回呼ぶ(中間attemptはLedger Deviation Checkerのみで足りるかを検証) | Leakage是正ループの中間段階はFact Safety最終ゲートではないと位置づけ、最終出力確定時のみFact Checker A'を実行 | ¥74.49 | 概算¥25(1/3) | 約¥50/記事 | 約¥5万円 | 約¥50万円 | 短縮 | 中〜高(中間attemptで新規に混入したunsupported claimがFact Checker未検証のまま次attemptへ持ち越される可能性、最終1回だけでは中間で追加された誤りの発見が遅れる) | 最終1回のみでも既存精度は維持できる可能性はあるが、中間で発生した新規claimに対するfalse negative(見逃し)リスクが増える懸念があり実測未検証 | 低(呼び出し位置の変更のみ) | **UDR候補**(Fact Checker運用の意味的変更、既存retry/fallbackとの整合再確認が必要) |
| C. Fact Checker A'のfail-closed gate(`MAX_FACT_CHECK_ATTEMPTS=2`)はそのまま維持しつつ、Local Rewrite同様に「新規に追加/変更された文のみ」を対象にした差分Fact Checkを新設し、既存の全文Fact Checkは記事confirm時のみ実行 | Writer全文書き直し方式(現状)ではテキストdiffが困難なため、Writer側にも「変更箇所を明示させる」仕組みが前提になる | ¥74.49 | 不明(Writer側の変更箇所追跡機構が未設計のため見積り不可) | 不明 | 不明 | 不明 | 不明 | 中(diffの取りこぼしで未検証claimが混入するリスク) | 不明 | 高(Writer全文書き直し方式自体の変更が前提、Diagnostic Full Retryとの整合も要確認) | **UDR候補**(新しいWriter/Checker仕様が必要) |
| D(参考、品質低下を伴うため不採用) | MAX_FACT_CHECK_ATTEMPTSやweb_search呼び出し回数の上限を模型側で強制的に絞る | ¥74.49 | ¥30〜40程度と推定 | — | — | — | 短縮 | **高(除外)**: 検索網羅性が落ち未検証claim見逃しリスクが直接増える | 増加 | 低 | 対象外(品質低下許容のため本調査の推奨対象から除外) |

**推奨**: 候補Aが最も筋が良い(Fact Checker A'の役割[外部web検証]を維持しつつ、Ledgerが変わらない
限り同じ外部citationを再検索しない設計)。ただし§5の制約(Ledger入力ミス自体の検知機能を失わない
無効化条件の設計)を満たせるかは未検証であり、**Production挙動・Fact Checker仕様の変更を伴うため
USER_DECISION_REQUIRED**とする。候補B/Cは中間attemptでのFact Safetyリスクが未検証で、コスト削減効果は
Aよりやや劣るか不明瞭なため、Aの代替/補完候補として提示するに留める。候補Dは品質低下を伴うため推奨しない。

## 参照ファイル

- `er003_v1_en_direct_vfl_01_generate.py`(vfl01、`run_deviation_check` 603〜626行目、
  `run_researcher`/`run_verification`の`tools=` 175/258行目)
- `er002_ja_web_research_r3.py`(`make_fact_checker_fn` 258〜290行目、`MAX_FACT_CHECK_ATTEMPTS` 351行目)
- `er012_b_family_voices_production_01.py`(`run_fact_checker` 95行目)
- `er012_editorial_b_voices_4v_article_trial_02.py`(`run_fact_check_a_prime_4v` 191〜225行目、
  `run_ledger_deviation_and_local_rewrite` 864〜965行目、`run_pipeline_4v`/`cl.logging_context`
  1142〜1204行目)
- `er010_ledger_local_rewrite_09.py`(`rewrite_ng_item`、`MAX_REWRITE_CYCLES`、tools未宣言)
- `er012_output/editorial_b_voices_4v_article_trial_02/b1b_run01/raw_usage_log_4v_writer.jsonl`
- `er012_output/editorial_b_voices_4v_article_trial_02/b1b_run01_attempt{1,2,3}/fact_qa.json`
  (queries一覧、response_id照合)
- `er012_output/editorial_b_voices_4v_article_trial_02/b1b_run01_attempt1/ledger_deviation.json`
- `CURRENT_SPEC.md` 680〜681行目(Fact Safety(共通)、Ledger Deviation Checker v2)
- `EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-02_REPORT.md` §6・§7(訂正対象の記述)
- 参考値: `er003_output/n3_01/hanshin/{a2,b1b}/fact_qa.json`、
  `er011_output/open112_trend_synthesis_production_wiring_01/{b1b,a2_rerun_02/attempt2}/fact_qa.json`、
  `er012_output/editorial_b_voices_trial_07/b1b_run0{1,2}_attempt{1,2}/fact_qa.json`
