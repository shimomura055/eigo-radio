# FAMILY-X-KP-IDIOM-PRIORITY-ABC-TRIAL-01 委任_01(2026-10-13、Sonnet)
- 範囲: 固定Coffee候補リストで選定Prompt優先順位A/B/Cを Std/Adv n=3比較、押し出し評価、ばらつき、Rule7監査(JPY0)、SSOT。Production無変更。抽出再実行なし、TTSなし、timeout/監督ループなし。
- 結果: pump-fist選定採択 A5/6 B5/6 C4/6。run最終gate完全PASS A6/6 B2/6 C1/6。Status案 A=現行維持、B/C=REJECTED案。
- 費用: JPY19.1078 / 20(見込み16.38)。有料runは1回のみ起動(再起動なし)。
- STOP確認: 開始前と有料run前に本件STOP/STOP_NOTICE不在を確認。Melos STOP_NOTICEは別案件。並行する③④⑤の出力dirには触れていない。
- 制約・注意: retry(選定やり直し)未実行。固定候補は各Levelのrun1のみ(別runで結果が変わり得る)。std_B_run3の選定INVALIDはvalidation_reasons空(原因未特定)。n=3で統計的断定はしない。
- SSOT: DECISION_LOG.md末尾に記録、OPEN-310/325へ追記(新規OPENなし)。CURRENT_SPEC.md未変更。
- 詳細: `er064_output/kp_idiom_priority_abc_01/ABC_REPORT_01.md`。
