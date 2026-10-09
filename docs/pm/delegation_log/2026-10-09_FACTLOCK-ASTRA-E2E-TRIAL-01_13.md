# 委任_13 FACTLOCK-ASTRA-E2E-TRIAL-01(2026-10-09) G2 round1残り再開 + round2実行 委任文(要約)
- Fable中間チェック判断: 新腕STOPは系統的でない、runner欠陥(worker_shadow)は修正済みでテスト33件PASS -> 再開・続行承認。「1 run 20円超」はChecker run capと解釈(Astra段は腕cap 100円)。
- 予算: Trial累計raw 425.21(Stage R 178.99 + runner 246.22)。runner cap=guard基準 `--cap-jpy 1000 --alert-jpy 850`。runner台帳rawが800円に達したら即停止。B1回復は残り1回(超過はSTOP記録)。
- 範囲: (1)round1残り再開(STOP.json改名、failed段reset、--allow-script-change、worker3/4) (2)round2(新5テーマ: byd_recall/central_bank_mortgage/openai_copyright/semiconductor_earnings/streaming_price、両腕・最終段まで、worker5=byd+cbm / worker6=openai+semi / worker7=streaming、3並列) (3)全9テーマ集計 AGGREGATE.md (4)ユーザー提示パック(JA/EN、旧腕vs新腕対) (5)記録。
- 停止条件: runner例外・provenance違反・(m)不正research・API失敗3 run超・Checker run 20円超・guard累計1000到達・raw累計800到達・空き物理メモリ4GB未満10分継続。品質起因STOPは停止理由にしない。runner欠陥は全停止->最小修正->テスト->再開(1回まで)。
- 禁止: TTS、Prompt文言変更、品質STOP記事の再実行、Production/SSOT本体(CURRENT_SPEC/OPEN_ITEMS)編集、未確認数値の確定記載、VALIDATED/APPROVED宣言。
