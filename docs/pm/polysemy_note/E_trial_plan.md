# E: 多義語注意notes Trial計画(OPEN-233-LEDGER-POLYSEMY-NOTE-DESIGN-01 委任_D、未実行・¥0)
## 前提
- Fact台帳=Baseline固定(er019_output/{meta,hormuz}/run_03 の fact_ledger_draft.json+verification。P'版は不使用)。notes追加call(offline、出力{fact_id,note}のみ、既存notes末尾へコード連結、規則はB_design §11の4行)。
- Writer〜Checker後段=Trial-01同一(A2_trial01_config_freeze.md)。
- 条件: Control(notes追加なし) / 案N(notes追加) / 案N+B(notes追加+B3 promptへ転記規則1行=Writer側変更。ユーザー承認がなければ実行しない別arm)。
## Phase 0(¥0)
- Baseline台帳再構築+ledger_diff_p01.pyでnotes以外の差分0確認。A3候補表とのFP照合枠作成。Trial-01 FREEZE sha再確認。
## Phase 1(ふるい分け: B3+JA O/R1/R2まで)
- 条件×テーマ(meta・hormuz)×3 repeat。測定: ①briefへの注意文転記率 ②R0〜R2の逆転型誤読件数(3値ラベル・二重ラベル) ③断定強化・留保欠落件数 ④JA R2逐語率(Before R0 0.1518/R2 0.0843) ⑤注意付与件数・割合・誤付与(確度中・対象外をA3照合) ⑥Rewrite hint 400字切り詰めで注意文が切れるか(Checker側コード不変)。
- 費用: 1 run≈¥8(B3 1.5+JA 6.7、Trial-01実測)。2条件×2テーマ×3=12 run≈¥95、3条件=18 run≈¥140、notes call≈¥1×2。
## Phase 2(Phase 1で良かった条件のみ)
- EN+Checker 1〜2 run/テーマ(≈¥15/run: EN 3.1+Checker 2.5+deviation等)→¥30〜60。測定: EN Entertainment(前回E3指標・pairwise)、Checker候補数/後段AI判定/Rewrite/再判定/Human Review/最終重大NG/不要重大判定(ロジック不変)。
## 合格基準(事前固定)
- 案Nの逆転型誤読0/3かつControl未満 / 新規断定強化0 / 留保欠落≤Control / notes以外の台帳差分0 / 注意付与が確度高候補に限られ誤付与≤2 / EN Entertainment・Checker最終状態がControl比で悪化なし / 400字切り詰めで注意文欠落0。
## 費用上限案・所要
- 上限: 2条件¥130、3条件¥200(台帳生成費なし)。所要: Phase 1 約40分(並列3)、Phase 2 約30分、評価約40分。
## STOP
- 実費が見込み1.5倍/上限到達、Phase 0で差分0不成立、Phase 1で断定強化発生、Production経路混入。
## Status
- VALIDATED/REJECTED/USER_DECISION_REQUIRED。VALIDATEDでもProduction採用ではない。offline結果はProduction採用根拠にしない(本番Researcher prompt追記は別Trial)。
## 必要DEV
- notes追加callスクリプト(新規DEV)。B3転記規則はN+B armのみ・プロセス内DEV差替(Production file無変更、前回方式)。流用: ledger_diff_p01.py/fact_safety_p01.py/ja_copy_rate_p01.py/pairwise_p01.py/run_checker_after_p01.py。
## ユーザー判断事項
(1)Trial実施可否と上限 (2)案N/案N+B/3条件 (3)確度高のみ既定か (4)offline固定台帳の可否 (5)対象テーマ(meta+hormuz推奨)
