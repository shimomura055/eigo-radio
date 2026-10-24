# PROMPT_DIFF_03 (委任_21: PROMPT_DIFF_02からの差分。Prompt本体[THINK_BLOCK・規則3置換]は無変更。変わったのはSheet(データ)と runnerの起動方式)

DEV/Trial専用。Production(X/Z)のPrompt・正規表現・閾値・辞書は無編集。`er110_family_y_opinion_based_01.py`ほか既存er110 moduleはgit diffで無変更(testで固定)。

| # | 変更 | 場所 | 根拠 |
|---|---|---|---|
| 1 | V1 Sheet: TBS-07内容を2か所に限定、ONE_e削除、「安心」「自分も例外ではない」削除 | `SHEETS_02["voice_1"]`(`_v1()`) | OF-Y7-01/02 |
| 2 | V2 Sheet: wishes_public置換、葛藤組み直し、troublesの「かといって」除去、TWO_fの監視を任意・理由1か所に、MR-T041-03由来の記述の全除去 | `_v2()` | OF-Y7-03/04 |
| 3 | V3 Sheet: 「全部禁止も全部解禁も違う」をvalues 1か所に(補った整理と明記)、troublesの言い換え、声=男性、arc/identity_cueに仮定・「うちの子」(細部なし)・結びの型 | `_v3()` | OF-Y7-01/05、推奨(男性) |
| 4 | 結びの型を3人で分担(arc_jaに明記) | 3 Sheetの`arc_ja` | OF-Y7-05。Promptの規則3「結びの言葉は話し方から自然に決める」「考え方C」は維持(Sheetの目安として渡る) |
| 5 | runnerを`run_02a`/`run_02b`の2本起動に(引数=run名のみ。許可リスト外は終了コード7)。予算承認ファイルは`{"cap_jpy": 45, "runs": 2}`で、1runの歯止め=22.5円(`read_cap`) | `main(run_name)`、`read_cap` | 委任_21 §0/§2。費用台帳は`BUDGET_LOG_OB_02.md`(当初run別の台帳は、test起因の事故で4run分が混在したため作り直し)。APIにseed指定はなく、2本の差はサンプリングのばらつきのみ |
| 6 | test: OF-Y7-01〜05と男性声の固定、run名・承認ファイルのtestに更新(20 PASS) | `er110_family_y_opinion_based_02_test_01.py` | 委任_21 §1 |

## 残存・撤去のGrep
- 撤去: V1の`ONE_e`・「安心」「自分も例外ではない」、V2の「未成年だから…仕方がない」・「かといって」、V3 sketch/stake/emotion_habit/arc/claim_coreの「全部禁止も全部解禁も」。02の`SHEETS_02`内の残存0(testで固定)。01の`SHEETS`には残置(run_01再現用)。
