管理ID: FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_15(ASTRA-REVISE-MATRIX-01: Fact Lock R0 を起点に Astra で R1→R2→R3 を2系列、計6本生成+評価)。日付 2026-10-08。ユーザーGo取得済み(2026-10-08「はい、Goしてください。」)。

## 予算・制約
- API予算 上限 ¥60(見込み約¥40)。超過見込みが出たら生成を止めて報告。astra の単価は routing contract 未登録のため、トークン数を全て記録し、推定単価(gpt-6-sol の 2.00/0.20/10.00 USD per 1M × 2.5、USD/JPY=160)で円換算する。推定であることを全ての費用表に明記。
- Production コード(er019_*/er006_*/er012_*/er003_* 等)・CURRENT_SPEC.md は変更しない。
- `git add -A` 禁止。対象ファイルを個別に add。`_private/` は add しない。
- 委任文(このメッセージ全文)を一字一句そのまま `docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_15.md` に保存し、`docs/pm/tools/check_delegation_prompt.py --file <path>` を実行して結果を記録(FAILでも続行)。
- 結果は `docs/pm/RESULT_PACKET.md` と `docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_15_result.md` の両方に書く。

## 試験設計(ユーザー確定)
- 起点 R0: Fact Lock v1 の meta b2、Writer直後本文(R1/R2未通過)、inline タグ `【事実N】` 除去済み。候補パス: `er052_output/factlock_writer_trial_01/step2_astra_r3_01/inputs/FL_R0/meta/b2/source.md`(委任_14 が準備、未追跡)。これが Fact Lock v1 の meta b2 の R0(`original.md` 相当)と一致することを元ファイルと突合して確認し、元パス・SHA・採用 rep(r1/r2)を記録。台帳(verified_fact_ledger)と B3 brief の所在も記録。
- 2系列 × 3段(R1→R2→R3)、モデルは全て `gpt-6-astra`、reasoning は Step 1(`er052_output/factlock_writer_trial_01/step1_chat_repro_01/conditions.json` と実行スクリプト)と同一設定。
  - 系列A「ユーザーPromptのみ」: developer/system メッセージ**なし**。user メッセージのみ。
  - 系列B「熟練編集者」: developer メッセージ = Step 1 の F2 developer 文を `conditions.json` から一字一句コピー(「あなたは熟練の編集者です。元記事の事実はそのままに、読者が思わず続きを聞きたくなる記事に書き直してください。構成の組み替え、段落の分け方、語りかけ、問いかけ、余韻のある結びなど、必要だと思う手段は自由に使ってください。」)。
  - 各段の user メッセージ(両系列共通、Step 1 の `build_fresh_input` と同じ形): `以下の記事:\n\n{前段本文}\n\n事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。長さは800〜1000字程度でお願いします。`
  - 逐次: R1 の入力 = R0、R2 の入力 = R1 出力、R3 の入力 = R2 出力。`previous_response_id` は使わない(本文テキストを渡す)。記号禁止リストは付けない。
  - 系列A と系列B は並列実行可(2プロセス)。段内は逐次。
- 出力先: `er052_output/factlock_writer_trial_01/astra_revise_matrix_01/`
  - `DESIGN.md`(上記設計、固定SHA、実行コマンド)、`runs/{A,B}/r{1,2,3}.md`(本文)、`runs/{A,B}/r{1,2,3}.response.json`(usage・model・reasoning 設定を含む生レスポンス要約)、`usage_log.jsonl`。

## 評価(7本: R0 + A r1〜r3 + B r1〜r3)
1. JA Fact Check 全台帳(gpt-6-luna、sweep `eval/EVAL_RULES_V2.md` / R3-MINIMAL と同一の呼び出し・プロンプト)。MAJOR/MINOR 件数と各指摘(NG文・台帳・理由)。4スレッド並列可。
2. 決定論指標: 字数、段落数、1文段落数、問い(?/？)、ダッシュ(——/――)、Markdown残存(#, **)、記号Gate `detect_prohibited_symbols`(計測のみ)、台帳外数値(台帳に無い数値の件数)。
3. R0 と比較した「新規具体主張」数(sweep の (ii) new_specific_claim と同一手法。R0→各段で増えるか)。
4. 重大候補一覧 `eval/HUMAN_CHECK_MATRIX.md`: FC MAJOR(あれば MINOR のうち主体・因果・否定の型)を、NG文・台帳の該当行・理由の3行で列挙(ユーザー確認用)。
5. 集計 `eval/SUMMARY_MATRIX.md`: 4段×2系列の表(FC MAJOR/MINOR、新規主張、字数、段落、1文段落、Markdown、記号Gate、費用、秒)。

## ユーザー提示パック
- `USER_PACK.md`: 7本の本文を全文掲載。段(R0/R1/R2/R3)は明示、**系列は伏せる**(ラベル X/Y にランダム割当、対応は `_private/MAP.json`)。Markdown 見出し・太字は提示用に除去した本文を使う(除去前も `runs/` に残す)。各本文の冒頭に字数のみ併記。FC 結果は載せない(先入観回避)。

## コスト比較 `eval/COST_MATRIX.md`
- 系列ごとに各段の実測トークン・推定円。累積: R1 のみ / R1+R2 / R1+R2+R3。
- 差し引き: Fact Lock v1 meta b2 の同 run の Luna R1+R2 の実費(当該 run の raw_usage_log / cost 記録から実測。無ければ Trial A の平均値で代替し明記)。
- 1記事セット換算(文字数一定の前提): 現行 1 セット約¥52(TTS Standard同期)/¥43(Batch)に対し、Astra 段数ごとの増分と合計。astra 単価推定の注記。

## SSOT・Git
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` に新§(§106 の次)を追加: 設計、7本の指標表、FC 結果、費用、Status=MEASURED(人間確認待ち、Production変更なし)。
- `DECISION_LOG.md` に本日分エントリ(ユーザー確定設計の逐語: 「モデル Astra / ベース Fact Lock R0 / R0>R1>R2>R3 文字数800-1000ソフト / 日本語まで / 各段を人間がチェック+AI判定 / 軽微・重大カウント / META 1記事 / 2系列(ユーザーPromptのみ・熟練編集者)4×2」、結果要約、人間確認待ち)。
- `docs/pm/REPORT_LEDGER.md` に新§を登録。
- `docs/pm/PM_BRIEF.md` の運用注意欄(無ければ末尾に「PM運用メモ」節)に1行追加: 「2026-10-08 ユーザー指示: 明確なGo指示があるまで、委任(先行準備・設計下書きを含む)を一切出さない(先行委任はユーザー混乱の原因になった)」。
- 個別 `git add`(`astra_revise_matrix_01/` 配下から `_private/` を除く、SSOT 3ファイル、PM_BRIEF.md、delegation_log の委任文・check・result)。`git status` で混入確認後 commit(例: 「FACTLOCK-WRITER-REDESIGN-TRIAL-01 ASTRA-REVISE-MATRIX-01: Fact Lock R0起点 Astra R1-R3 ×2系列 MEASURED(FC MAJOR x/x、…)、REPORT §xxx、実費¥xx(astra単価推定)」)、`git push origin main`。conflict/エラー時は中断して報告。

## result に書くこと
実費(推定単価注記、トークン数合計)、所要時間、7本の指標表、FC 指摘全文、重大候補、USER_PACK.md のパス、COST_MATRIX の要点、commit hash と raw URL(https://raw.githubusercontent.com/shimomura055/eigo-radio/main/<path>)、check_delegation_prompt 結果、未解決点・逸脱。
