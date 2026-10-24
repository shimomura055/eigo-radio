# BUDGET_LOG_T6_01: 補強Trial_06 費用台帳(委任_31、2026-10-24、UDR #178承認 KP案件上限500円)

call単位の台帳=`er112_output/kp_gm_trial_06/paid_calls.jsonl`(102行、1 API call=1行。usage・wall_s・cost_jpy)。stdout控え=本ディレクトリ `stdout_*.txt`。
使用モデル: Production gloss と同一の `gpt-6-luna`、reasoning effort=high固定(最新世代の最上位系ではない。例外理由=評価対象がProduction系列そのもの・本番同一条件・Trial_04/05と比較可能にするため)。

| 起動 | コマンド | call | 円 | 備考 |
|---|---|---|---|---|
| HC(初回) | `gen --set HC --siblings off --reps 1,2 --cap 5` | (HC合計32 callの一部) | (HC+R合計3.688円の一部) | **cap引数の設計ミス**: capは台帳(全gen合算)累計に対する値だが、S2を並列起動したため累計がcap 5に到達し、HCが16 job中途でHALT(SKIP_CAP、API未呼出) |
| S2 | `gen --set S2 --siblings on --cap 22` | 66 | 15.62(B0p 4.281 / X2pp 11.337) | 33 level x 2 arm、全ALIGN_PASS、retry 0、HALTなし |
| R(初回) | `gen --set R --siblings off --arm X2pp --cap 3` | 0 | 0 | 同じcap誤り(累計5.6>3)で全job SKIP_CAP。API 0 |
| HC(再開) | `gen --set HC ... --cap 28` | 残り(HC合計32 call中の残り) | HC+R合計3.688円(HC32 call+R4 call=36 call) | 既存resultsの`done`集合により未完のjobのみ実行(再実行ではなく同一gen残りの完了) |
| R(再開) | `gen --set R ... --cap 28` | 4 | (上に含む) | |
| 合計 | | **102 call** | **19.306円** | 見積20.99円(P案)以下、cap 28以下 |

- 事故の開示: 上記capの誤りは私(sonnet-worker)の起動引数設計ミス。実害=HC/Rの再開起動2回(費用は未実行jobの分のみで重複なし)。**重複call 0**(`done`集合で既存を除外、台帳の(arm,gid,rep)重複を下記で確認)。委任文の「各genを1回ずつ」から逸脱(再開2回)。原因は並列実行時のcap意味(累計)の取り違え。
- 案件累計(KP): 295.43 + 19.306 = **314.74円**(上限500円、63%)。KP累計450円/日次900円の事前報告閾値には未接近。
- 日次(JST 10-24、`daily_dev_cost_01.py`採用値): 実行前363.39円(Fable把握414円)。本Trial 19.306円を足すと **約382.7円(Fable把握値基準なら約433.3円)**、1,000円内。(同toolは本Trialのer112台帳を未捕捉の可能性があり加算値で記載)
- 重複確認: 台帳102行の(arm,gid,rep)重複=0(上記スクリプトで確認)。HC+R=36 call/3.688円、S2=66 call/15.618円、計19.306円。

## 委任_33(2026-10-24、Fable+Opus二重判定集計・Closeout記録)
- 本委任の費用 0円(API 0。Opus評価はClaude Code側、OpenAI/TTS呼出なし)。
- KP案件累計: 314.74円 / 上限500円(63%)。
- 日次(JST 10-24、Fable把握分): 約433円 / 1,000円(本委任追加0円)。
