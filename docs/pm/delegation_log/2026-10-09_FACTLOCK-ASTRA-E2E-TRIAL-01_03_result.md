# 結果: FACTLOCK-ASTRA-E2E-TRIAL-01 委任_03(DESIGN/PREREGISTRATION v2、2026-10-09)

Status: DESIGN_READY(v2)。実行Go未。API支出¥0、Production変更なし、既存コード・Prompt・CURRENT_SPEC.md・OPEN_ITEMS.md無編集。委任_02のファイル(`B3_ANNOTATION_SPEC_v1*.md`、`b3_annotation_check_01*.py`)には触れず、stageもしていない。
check_delegation_prompt.py結果: FAIL(必須セクション3種・固定ブロックE-1/D-1/G-1/F-1欠落。設計書改訂のみでコマンド実行なしのため。続行)。記録=`2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_03_check.json`。

## 1. 成果物・commit・raw URL
- `er052_output/factlock_astra_e2e_trial_01/DESIGN_E2E_01.md`(v2、改訂履歴つき)
- `er052_output/factlock_astra_e2e_trial_01/PREREGISTRATION_01.md`(v2)
- `docs/pm/opus_a_review_factlock_astra_e2e_01.md`(新規、Opus要点のFable転記)
- `docs/pm/OPUS_FINDINGS_LEDGER.md`(OF-095〜OF-102の8行追記)、`DECISION_LOG.md`(末尾に1節)、`docs/pm/REPORT_LEDGER.md`(1行)
- `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_03.md`、`_03_check.json`、本ファイル
- `docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`は.gitignore対象のため更新のみ(commit対象外)
- commit hash: d1d8275d(追記コミットは別)。raw URL: 末尾「raw URL」節

## 2. v1→v2の変更点(Opus論点番号対応)
- 論点1: Arm C不要、影の対照を両腕化(M1(a)20対、M1(b)、M3旧腕起点)。v1 3節の「M1(b)は安く再現できない」を誤りと訂正(DESIGN 3節・8-2)。
- 論点2/決定6: 案B新腕=B1(Fact Lock R0+original_must_fix→Astra R1→R2→後処理→EN再実行、1記事1回・Trial全体3回)。初回JA_RECHECK率を両腕で記録。PREREGISTRATION 5-8を確定(DESIGN 2節・2-1・5-3、PREREG 2-7・5-8)。
- 論点3: R2後FC MAJORに`shadow_stop=true`、複合主指標「人手介入必要率」を両腕同定義で追加(DESIGN 1-2表L・1-3、PREREG 2-5)。
- 論点4: M1 Standardは実装せず、attempt1 MAJORを要約/本文に分類して記録、「M1効果は未測定」と明記(DESIGN 3節・4節(d))。
- 論点5/決定7: 全10記事を新仕様で再注記、独立二重注記、G0で`strip_tags`照合+`fact_selection_evidence.json`のsha256/内容照合、旧4/新6層別、「人手注記の上限性能」明記(DESIGN 2節・4節(h)・7節、PREREG 3・4節)。
- 論点6: EN STOP率を「3記事差以上かつtranslation MAJOR×0.75」へ厳格化、分母=予定run数20固定・STOP独立カテゴリ、rejected本文ラベル対象(別枠)、軽微判定を2-2に一本化(二重計上解消)、2-1は要確認フラグ化、盲検不完全を明記、(ii)検出器追加(PREREG 1・2-1〜2-7・3・6節)。
- 論点7: 旧4でresearch/B3呼び出し検出で即停止、横断予算予約、astra×1.5係数、G1拡張、旧4完了後の中間チェック、TTSをG2から切り離し(DESIGN 4節(k)(l)(m)(n)、5-0・5-2)。
- 論点8: R0復唱は検出のみ、R0と最終JAの両方、残れば軽微の別枠(DESIGN 4節(b)、PREREG 2-2・2-7)。
- ゲート順: B3注記仕様ユーザー確認→新6 Stage R→全10記事注記→G0→G1→G2(旧4→中間チェック→新6)。

## 3. 前提作業一覧 v2(対象・見積行数・リスク)
- (a) astra単価登録: 約36+15行。Production単価表編集、別commit、G1後に請求と照合(それまで×1.5)。
- (b) R0復唱検出(R0+最終JA、両腕): 約20行。検出のみで非対称なし。
- (c) タグ残存修正(B1に必要): 約30〜50行。漏れると次段に【事実N】が流入、G1で確認。
- (c2) B1回復経路+カウンタ(1記事1回・全体3回): 約80〜120行(見積)。1回約¥35、最大¥105。
- (d) M1 Standard: 実装なし。attempt1 MAJOR分類ログのみ約20行。Standard側M1効果は未測定。
- (e) 記号後変換・Markdown除去の組込: 約40行。記号Gateは記録のみ(TTS対象2本で残存確認)。
- (f) 2腕runner本体: 約450〜600行+テスト約250行(v1据置。他項を分離)。動的fixtureの`baseline_parsed=None`はG1で確認。
- (g) web_search課金計上の再確認: 約20行。是正済み(OPEN-242)。
- (h) B3注記仕様 v1依存+全10記事再注記+照合スクリプト: 約40行+人手/Sonnet作業。仕様確定まで着手不可、自動ルール未整備。
- (h2) TTS入口: 未確認(要調査)。G2から切り離し。
- (i) 影の対照ログ・(ii)検出器・集計(人手介入必要率等): 約200行。API追加¥10〜15相当。
- (j) 失敗方針: 設計のみ(5-3更新済み)。
- (k) 横断予算予約+×1.5: 約60〜80行(見積)。予約漏れで並列段が同時に上限超過しうる。
- (l) G1拡張: 手順のみ(約+¥8)。
- (m) 旧4の即停止検出: 約30行。検出漏れ=重複支出+B3原文変化。
- (n) 中間チェック: 手順のみ。系統的STOP時はFable判断。

## 4. 費用・時間見積 v2(すべて見積)
- 総額: v1の約¥650(560〜780)+追加約¥25〜30(影の対照¥10〜15・(ii)検出器約¥4・G1拡張約¥8)+B1最大¥105=推定約¥690〜900(Opus/Fable推定)。本書の単純加算の最悪は約¥915で、約¥15の差は未照合。上限¥1,000内。
- 新腕1記事約¥41〜42、旧腕約¥9.2。B1回復1回約¥35(見積)。G1は約¥43〜53。
- 時間: ラウンド1(旧4、4並列)約29分→中間チェック→ラウンド2(新6、3並列×2)約72分、B1最大3回で約15〜18分、G1約15分。G2全体はv1の約2〜2.5時間と概ね同等(注記作業・Stage Rは別途、Sonnet作業時間は未見積)。

## 5. 未確認事項・Fable判断が必要な点
1. 新6のresearch+B3(約¥100)は注記の前提のためG0より前に必要(Stage R)。実行Goの範囲をどこまでにするか。
2. B1の「1記事1回」枠: R2後FC MAJOR由来とEN段ja_source MAJOR由来を同一枠とみなす解釈案(別々なら上限3回の消費が増える)。
3. 影STOP・人手介入必要率の数え方、人手介入必要率の判定線(新≦旧−0.15等)、2-1要確認フラグを総合悪化に入れる条件は、いずれも本書で補った定義案(Opus文言に詳細なし)。
4. G1出力をMETA新腕の本番run扱いにするか(総額差 最大+¥35〜53)。
5. ラウンド1を4並列にする案(A5承認済みの単層4並列+自動降格)。3並列に抑えるか。
6. 総額の単純加算(約¥915)とOpus推定上限(約¥900)の差。v1の影の対照約¥6を置換か上乗せかも未照合。
7. Opus原文ファイルは未作成(転記のみ)。OPEN項目候補「B3自動注記」(Production化に必要)は起票していない(Fable判断待ち)。
8. 委任文のユーザー決定1〜3は、設計書・DECISION_LOG上は決定6〜8と採番した。
9. B3注記仕様 v1(委任_02)はユーザー確認待ちで、確認前に注記・実装・実行へ進めない。

## 6. 所要時間・API支出
- API支出: ¥0(生成API呼び出しなし)。所要時間は未計測(概ね数十分規模、記録なし)。

## raw URL(base https://raw.githubusercontent.com/shimomura055/eigo-radio/main/)
- er052_output/factlock_astra_e2e_trial_01/DESIGN_E2E_01.md
- er052_output/factlock_astra_e2e_trial_01/PREREGISTRATION_01.md
- docs/pm/opus_a_review_factlock_astra_e2e_01.md
- docs/pm/OPUS_FINDINGS_LEDGER.md
- DECISION_LOG.md
- docs/pm/REPORT_LEDGER.md
- docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_03.md
- docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_03_result.md
