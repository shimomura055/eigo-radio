# TEST_PLAN_01 M1/F1 配線後のテスト計画(実装時用。本委任では未実装・未実行)

原則: 共有ファイルへ追記する既存test(`er026_post_slowdown…test`、`er011*`一括、`er026_family_z_stop_sentinel_test_01.py`)は実行しない。新規testは `no-op telemetry` + 一時ディレクトリ出力。unit test PASSはProduction実行証拠ではない(EVIDENCE_PLAN_01参照)。

## 1. F1(Validator単体、API 0)
| ID | 内容 | 期待 |
|---|---|---|
| F1-1 | ユーザー例 `The studies suggest cats today.`/`The study suggests dogs today.` | 非PASS(`TRUE_CONTENT_MISMATCH`) |
| F1-2 | 後半の別不一致: 名詞置換・否定追加・数値変更・時制・固有名詞置換・語欠落・語追加 | すべて非PASS |
| F1-3 | 複数の連結発音箇所(Pattern A+C等) | PASS/PASS_WITH_WARNING維持 |
| F1-4 | 正規化後に別差分が残る文(M1後) | 不受理 |
| F1-5 | Pattern B/C/KP それぞれの先頭だけ説明可能な誤PASS反例 | 非PASS |
| F1-6 | 回帰: 現行PASSだった実データ(census A: 10件、B: 正常側全件) | PASS維持(例外=`US sea blockade` 4件は人の聴取確認後に確定) |
| F1-7 | 緩和なし確認: 非PASS→PASS 0件(census全データ) | 0 |

## 2. M1(Validator単体、API 0)
| ID | 内容 | 期待 |
|---|---|---|
| M1-1 | CMU収録語の同音綴り(Pattern A/B/C形のみ受理)、受理理由限定、所有格正規化、audit trail項目 | 設計どおり |
| M1-2 | `Melo/Mello/Mellow` の同一原則評価(OOV扱いは承認後の選択肢に従う) | 選択肢(i): 現行と同じ4/12(M1不発)。(iii)承認時のみ12/12 |
| M1-3 | 一般化テスト(他の固有名詞・一般語の正/誤): probe 15件 + `TEXT_COUNTER`/`NORMAL_TEXT` | 誤PASS 0 |
| M1-4 | 異なる語を同等扱いしない: `Mellon/Melas/Milo/Sad`、`Sirius→Serious` | すべてNG |
| M1-5 | `segment_id` 非依存(None / `point_heading` / dialogue)で同結果 | 同一 |
| M1-6 | 日本語・KP・非en-US では不発 | 不発 |

## 3. 配線・統合(API 0、モックASR転写を注入)
| ID | 内容 | 期待 |
|---|---|---|
| W-1 | Primary#1直後・`cascade_eligible` early return前で呼ばれる(呼出ログ/`layer_invoked`) | 呼ばれる |
| W-2 | P2/S1/S2各stepでも呼ばれる | 呼ばれる |
| W-3 | fallback(`force_secondary=True`)ではSecondary同意なしではM1受理しない | HR/retry維持 |
| W-4 | retry上限・HR到達・予算Guardを緩めていない(既存testの上限値アサート) | 不変 |
| W-5 | 各呼出点(#1〜#8、dialogue、point_headings_aoede)で同じ関数に到達(grepとスタブ呼出) | 全経路到達 |
| W-6 | Dangling Reference Check: Productionから参照される新module/仕様名が `CURRENT_SPEC`/`DECISION_LOG` に存在 | 存在 |

## 4. Opus論点(5件以内、条件A/C)
1. OOV扱い: (iii)を新基準として申請する価値と危険(`Cleos→Clio`型の誤許容、発音誤りと表記揺れの区別不能)。(i)/(ii-a)で止める妥当性。
2. F1設計の「通常Validatorに委ねる」(benign判定を`protected_check`再利用)が新たな抜け(数字・否定は`protected_check`で捕捉済みだが機能語の欠落/追加)を作らないか。`that`欠落がNGになる現挙動を維持してよいか。
3. 配置: `cascade_eligible` early return前+P2/S1/S2への複数適用が、retry/fallback/HR上限・コストを変えないか(特にfallbackのSecondary同意必須条件)。
4. Eq Layerの同種F1不備を今回の是正範囲に含めるか(最小変更原則との関係)。
5. `US sea blockade` 型(アクロニム表記)を許容する新規ルール不要で運用上の誤NG(HR/retry増)が許容範囲か。

## 5. USER_DECISION_REQUIRED候補
- **UDR-1(必須)**: OOV語の扱い。(A) (iii)を新基準として承認 / (B) 英語読みを作品単位で試聴確定しLedger高信頼化(OPEN-318 C-a) / (C) (i)で止めMelos 12件は4/12のまま。判断なしに追加Trial・実装拡張は不可。
- UDR-2: Eq Layerの同種F1不備の是正範囲(今回含める/別Open Item)。
- UDR-3: `US sea blockade` 4件の扱い(聴取確認後の判断。誤NGなら承認範囲外の新規アクロニム規則は作らず、HR/retryへ回る運用を容認するか)。
- UDR-4: `PRODUCTION_WIRED` 宣言は、UDR-1が(A)または(B)で完了するまで保留(M1の主目的が未達のため)。
