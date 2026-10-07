# E_sewer (OPEN-233-NOTE-TRANSFER-MATRIX-TRIAL-01 委任_C3)
単独評価・人間確認なし。rubric準拠、API/SSOT/git操作なし。11本(T0M1 rep2は再実行中のため対象外、後で追補)。

| 記事 | ①JA重/軽 | ②EN重/軽 | 退行重/軽 | F-010 | F-012 | pending |
|---|---|---|---|---|---|---|
| T0M0 rep1 | 0/1 | 0/1 | 0/1 | not_selected | correct | 0 |
| T0M0 rep2 | 0/1 | 0/1 | 0/0 | not_selected | correct | 1 |
| T0M1 rep1 | 0/1 | 0/1 | 0/0 | not_selected | correct | 1 |
| T1M0 rep1 | 0/0 | 0/0 | 0/0 | not_selected | correct | 0 |
| T1M0 rep2 | 0/1 | 0/1 | 0/0 | not_selected | correct | 1 |
| T1M1 rep1 | 0/0 | 0/0 | 0/0 | not_selected | correct | 0 |
| T1M1 rep2 | 0/0 | 0/0 | 0/0 | not_selected | correct | 0 |
| T2M0 rep1 | 0/1 | 0/1 | 0/0 | not_selected | correct | 0 |
| T2M0 rep2 | 0/1 | 0/1 | 0/0 | not_selected | correct | 1 |
| T2M1 rep1 | 0/1 | 0/1 | 0/0 | not_selected | correct | 0 |
| T2M1 rep2 | 0/1 | 0/2 | 0/0 | not_selected | correct | 0 |

重大NG: 0件。F-011もbrief外でnot_selected。

## 軽微NGの型(全て台帳基準)
- 「福島県」喜多方市(F-012、added_fact): 台帳に県名なし。現実には正しいが台帳未提示の軽い具体化として軽微。該当: T0M1r1, T1M0r2, T2M0r1, T2M0r2, T2M1r1, T2M1r2。ここは判定が割れうるので、集計時は別枠にする余地あり(PM判断)。
- T0M0r1: 「毎年一回の法定検査」(F-019 scope、退行。R0は「法定検査もあります」で正しかった)。
- T0M0r2: 「この作戦/この考え方で見直した」(F-012 causal、R0から継続)。
- T2M1r2 EN: 「1.6倍...the current level」(F-002 time、EN新規)。

## 判定保留(件数集計外)
- T0M0r2 EN一行要約のscope、T0M1r1/T1M0r2 の「補助を上乗せします/will provide」時制、T2M0r2「地下の管を減らす話」。

## 注記
- T2M1r2 R2にF-002(2018→2048年度1.6倍推計)が出現。briefの採用6件に無いため、brief外factの混入疑い(判定自体は推計として正しく記載、NGなし)。
- 個別根拠は eval/articles/sewer_*.json の ng_items・notes・pending に記載。


## 追補(委任_D1、2026-10-07): T0M1 rep2(停止枠の再実行成果)
単独判定・人間確認なし。記事本文を先に判定し、その後に条件ラベルを記録。既存本文は不変。

| 記事 | ①JA 重大/軽微 | ②EN 重大/軽微 | 退行 重大/軽微 | ★fact | 保留 |
|---|---|---|---|---|---|
| T0M1 rep2 | 0/0 | 0/0 | 0/0 | F-012 correct(F-010/011/013/016 not_selected) | 1 |

- 喜多方市(F-012)・合併処理浄化槽(F-005)・維持管理率(F-020)・保守点検/清掃/法定検査の区別(F-017〜019)は台帳と整合。
- 保留1件(no_ng寄り): 導入の「この主役選びが注目されています」(台帳に注目の事実なし、修辞)。詳細は articles/sewer_T0M1_rep2.json。
