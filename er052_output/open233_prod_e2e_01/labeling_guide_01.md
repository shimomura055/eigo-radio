# ラベル付け基準書 01(OPEN-233 新仕様E2E 9 run 事後評価、委任_05c)

性質: 評価手順書(¥0)。ラベルは事後評価の【推測】であり、Fable/ユーザー確認前は確定扱いしない。新しいSafety原則は追加しない。既存の重大誤解原則(design_open233_self_recovery_flow_01.md §0)と、ユーザー正式採用の線引き(委任_55/57)をそのまま使う。

## §1 用語定義

### 1-0 判定の最初の問い(§0-1、逐語)
「この違いは英語学習者に深刻な誤解を与えるか?」。目的は「記事の本質について重大な誤解を与えるものだけを止め、それ以外はできるだけ元記事を守る」こと。Ledgerとの差異を全部直すことではない。

### 1-1 3段階の重大度(severity_eval)
- **重大**: Ledgerとの食い違い、またはLedgerにない具体的新事実の追加で、記事の主要な意味・主体・方向・規模・時間軸を誤認させるもの(§0-2のBLOCK候補: 方向反転、主体A→別主体B、1企業→市場全体、継続→消えて戻った、未確認の人物・行動・仕組み・数字・動機の断定の追加 等)。
- **軽微**: 誤り/拡張はあるが、記事の本質を損なわない(原則許容候補: Brent futures→oil prices、2.6%→about 3% 等の近似・一般化、確認済みFactから自然に導けるHook演出)。
- **問題なし**: Ledgerと整合、または具体的Factを含まない修辞・比喩・つなぎ・一般論・問いかけ。Ledgerのnotes_for_writer(「断定しない」等)と整合する否定文も含む。

### 1-2 ラベル列の定義
- **true_problem**(Y/N/UNDECIDABLE): 重大または軽微ならY、問題なしならN。「Checkerが候補にして正しかったか」の根拠。
- **true_critical**(Y/N/UNDECIDABLE): 重大(上記)ならY。判断材料は(a)gold 6件の定義、(b)線引き例。
  - gold 6件(SAFETY_CRITICAL_CLAIM_DEFS、expected=BLOCKINGのもの): B3(HF-007、「so/because/led to ... flashy 20% plan」の因果)、A2A3-0(HF-003、repay the money)、A4-0(MUSE-HC-006、completed the exchanges with users)、A5-0(MUSE-HC-012、temporarily put back the feature)、B4-a(MUSE-HC-002)、B3-same@neg5(HF-007、flashy 20% plan)の計6件。runner内`SAFETY_CRITICAL_CLAIM_DEFS`(expected=BLOCKING)を正本とし、具体的な逐語核心句はそちらで確認する。gold定義は広げない。
  - 線引き例(ユーザー正式採用): Meta-1/Meta-2(「Also, some calls needed user information to continue.」)は軽微(QUALITY)でSafety-critical外。A4-1(「actually speaking with human staff」、MUSE-HC-012)は問題なし(ACCEPTABLE)へ再ラベル(委任_57、例2の適用)。
- **rewrite_needed**(Y/N/UNDECIDABLE): Rewrite前の文が重大または軽微で、修正が妥当だったか。Rewrite前の文が問題なしならN(不要Rewrite)。
- **再修正要**(人が付けない): 集計scriptが自動算出。Rewrite後、次cycleの同fact_idがまだBLOCKINGなら「再修正要」(`needs_refix`)。次cycleなし/ID無は判定不能。ラベラーは記入不要。
- **UNSURE(=UNDECIDABLE)**: どちらとも決められない場合のみ。reason列に「どのLedger項目のどの点が曖昧か」を必須記載。UNSUREは集計で別枠となりFable/ユーザー確認へ回る。迷ったら安易にNとせずUNDECIDABLE+理由。

## §2 手順(1 claimごと)
1. 対象文(claim_text)を読む。floor/AI判定(checker_ai/checker_machine/llm_materiality/floor_reason/final_materiality)の列は**見ない**(§3)。
2. 関連fact_idを確認(空なら具体的Factを含まない文の可能性。それでも別fact_idへの越境がないか確認)。
3. Ledger原文(`verified_fact_ledger.txt`のscope/conditions/numbers等)とnotes_for_writerを**逐語で**確認する。
4. 4観点で照合: (1)主体 (2)相手先・対象 (3)範囲 (4)限定条件。加えて数値・日付・因果・否定・比較を照合。
5. §1-0の問いを当てる。Ledger未記載というだけではmismatchにしない(未確認の具体的新事実の追加のみ問題)。
6. ラベル(true_problem→severity_eval→true_critical→rewrite_needed)と1行理由(reason)、label_sourceを記入。
- 境界例: 将来予測・一般傾向・読者/ユーザー認識の推測文(例 "They will want to know if it is AI or human.")は具体的FactでなければN(問題なし)。ただしLedger事実の主体を一般化して拡張する場合(ユーザー全員へ拡張等)は軽微またはUNDECIDABLE。「Ledger未記載のみ」で4観点mismatchなしの文はN。

## §3 禁止
- 推測でLedgerを補完しない(Ledgerに無い事実を「常識的にありそう」で正当化しない)。
- 記事全体の印象で判定しない(1 claim単位で判定)。
- gold定義・Safety-critical定義を広げない。新しいSafety原則を作らない。
- floor/AI/機械判定の結果を見てから判定しない(判定前に列を隠した作業用シートを使う。Fableが作成)。
- 他workerの結果を見ない。既存の推測ラベル(rca_22_sonnet_guess等)をコピーしない。

## §4 シート形式
作業用CSV列(workerが記入): `run, cycle, claim_key, claim_text, fact_id, true_problem, true_critical, severity_eval, rewrite_needed, reason, label_source, confirmed_by`
- 値: true_problem/true_critical/rewrite_needed = `Y` / `N` / `UNDECIDABLE`。severity_eval = `重大` / `軽微` / `問題なし`(UNDECIDABLE時は空でも可、reason必須)。
- `label_source`(必須): `sonnet_worker_<A|B|C>_guess`(worker記入時)。Fable確認後は`fable_confirmed`、ユーザー確認後は`user_confirmed`。`rca_22_sonnet_guess`は旧9 run専用で新規には使わない。
- `confirmed_by`(必須列): 初期は空=未確認。`fable`/`user`のみ記入可。空のラベルは「推測・未確認」としてKPIに併記する。
- `claim_key`: `run|cycle|norm(claim_text)`(集計scriptのnorm=空白正規化)。claim_textは改変しない。
- 集計script(`aggregate_report_abcde_01.py --labels`)入力json(Fableが突合後にCSVから変換): `{"labels":[{"run","cycle","claim","fact_id","true_problem","true_critical","rewrite_needed","label_source"}]}`。scriptは`run`+正規化`claim`で照合し、`cycle`が一致またはnull、かつ当該fieldが空でない最初の行を採用。未記入はUNLABELED。severity_eval/reason/confirmed_byはscriptが読まないため、Fableが別途保持する(KPI報告時のprovenance併記用)。
- 既存の`label_sheet.csv`(script出力)の列`true_problem,true_critical,rewrite_needed_fact_level,label_source,note_fill_Y_N_UNDECIDABLE`が記入先の原型。上記作業用CSVはその部分集合+severity_eval/reason/confirmed_byを加えたもの。

## §5 分配方法
- run単位で3 workerへ分配(A/B/Cで9 runを3 runずつ。Fableが分配表を作る。meta系とhormuz系を混在させLedger読込負荷を均す)。
- 3 workerは同じ本基準書と同じLedgerを使い、互いの結果を見ない。判定前にfloor/AI/機械判定列を隠した作業用シートを渡す。
- 完了後Fableが突合する。UNDECIDABLE、およびtrue_critical=Yは全件Fable/ユーザー確認へ回す(confirmed_by記入はそこで行う)。
- 二重ラベル(同一runを2 workerへ)は本委任では不要。必要ならFable判断で重大判定のみ別worker再判定。

## §6 所要時間目安
claim数×1〜2分(Ledger逐語確認込み)。例: 1 runが約30 claimなら30〜60分、3 runで1.5〜3時間/worker。重大候補・UNDECIDABLEの確認は別枠。
