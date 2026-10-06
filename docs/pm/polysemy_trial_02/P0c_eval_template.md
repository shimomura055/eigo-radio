# P0c 評価表テンプレ(OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-02、記入前・未実行)
性質: DEV Trial評価。VALIDATEDでもProduction採用ではない。ラベルは人手+決定論検査。Before参照値は要約転記(REPORT未照合)。
## 合格基準(事前固定、ユーザー指示§8の9項目をE_trial_plan.md合格基準へ対応づけ)
1. 逆転・重大変質型誤読: N+Bで0/3(各テーマ)かつControl未満
2. Noteが正しい(確度高のみ付与、誤付与<=2、A3照合)
3. B3 briefへ注意文が逐語/意味維持で届く(欠落・改変0を目標)
4. WriterがR0/R1/R2で保持(忠実維持、逆転0)
5. 新しい誤断定(断定強化)0
6. 留保欠落 <= Control
7. 説明的・不自然な文が増えない(Entertainment/Story、notes由来の説明過多0)
8. EN Entertainment(pairwise)・Checker最終状態がControl比で悪化なし
9. Controlとの差が測定可能(Rewrite hint 400字切り詰めで注意文欠落0を含む)
Before参照: E2E_02 meta復元型誤読3/5、P-TRIAL-01(復元型0、JA R2逐語率+16.4pt NG、Before R0 0.1518/R2 0.0843)。
## Phase 1: 記事 x 条件 x repeat(段別追跡)
段別ラベル: 忠実/逆転/曖昧。brief転記: 逐語/意味維持/欠落/改変。
| テーマ | 条件(control/nb) | rep | Note内容OK(Y/N) | brief転記 | R0 | R1 | R2 | 新誤断定 | 留保欠落 | 説明的/不自然 | JA R2逐語率 | 費用円 | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| meta | control | 1 | | | | | | | | | | | |
| meta | control | 2 | | | | | | | | | | | |
| meta | control | 3 | | | | | | | | | | | |
| meta | nb | 1 | | | | | | | | | | | |
| meta | nb | 2 | | | | | | | | | | | |
| meta | nb | 3 | | | | | | | | | | | |
| hormuz | control | 1-3 | | | | | | | | | | | |
| hormuz | nb | 1-3 | | | | | | | | | | | |
## Phase 2(Phase 1で良好な条件のみ)
| テーマ | 条件 | rep | EN反転(Y/N) | Checker候補数 | blocking数 | Rewrite回数 | 再Check結果 | Human Review | Entertainment(pairwise) | notes由来の説明過多 | 費用円 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | |
## 判定
Status(VALIDATED/REJECTED/USER_DECISION_REQUIRED): ____ / STOP該当(断定強化発生・費用1.5倍・Production混入): ____
