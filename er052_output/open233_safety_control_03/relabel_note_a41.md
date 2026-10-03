# A4-1 期待ラベルの修正による合格扱い(注記)

- 日付: 2026-10-03(委任_57、Fable判断)。`results_01.json`は改変していない(再実行もしていない、LLM/API呼び出し¥0)。
- 元の結果: Safety-critical 6claimのうちA4-1がV7で2/2 ACCEPTABLEとなり、「誤降格2件」で不合格だった(委任_55)。
- 修正: A4-1の期待ラベルをBLOCKING(Safety-critical)からACCEPTABLEへ修正した。
- 理由: 対象文(`people who thought they were speaking with AI were actually speaking with human staff`、`That was what people thought as they spoke.`)は、ユーザー判断済みの例2(利用者がAIだと思っていた、気づかなかった、という推論)と同型で、「were actually speaking with human staff」の事実部分はLedger(人間の契約スタッフが一部の電話を担当)に支持される。正式採用の線引き(2026-10-03)では「問題なし」。旧ラベルが新基準と食い違っていたため、ラベル側を直した(rubric V7は変更なし)。
- 修正後の再較正の最終判定: (a)Safety-critical 5claim 誤降格0、(b)Safety12 0/18、(c)Hormuz V6と同じ、(d)例3件期待どおり、(e)K16・K20 BLOCKING、(f)false BLOCK 0 -> **合格(ラベル修正後)**。
- 注意: この「合格」は期待ラベルの修正を前提とする。元の不合格判定は`results_01.json`にそのまま残っている。
