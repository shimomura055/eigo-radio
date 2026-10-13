# COST_03_actual (委任_03)
| step | 内容 | JPY |
|---|---|---|
| 比較run | canonicalization-only 5呼出(hormuz_b1b/meta_b1b 初回2呼出は保存前スクリプト不具合で結果消失→3記事再実行) gpt-5.6-sol系、run dir外(未ログ) | 概算2〜3(1呼出あたりKP scaffold実測0.76[選定+canon]以下) |
| Std KP | `--scaffold-only kp`(選定+canonicalization、PASS) | 0.76 |
| Adv TTS | preview(E1)+comment_1〜4 (gemini TTS 0.79 + ASR 0.31 + openai/azure補助) | 1.47 |
| 合計 | 委任_03 | 約4.3〜5.3(上限35、ハード38に対し十分内) |
run dir累計: 27.78 -> 30.01(`--budget-jpy 62`以内)。
