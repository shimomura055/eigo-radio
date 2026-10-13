# CHECKLIST_02 (Production Wiring Checklist 1-12、2026-10-13 委任_03)

判定: **Family X = 配線済み・未完了(`PRODUCTION_WIRED`は付与しない)**。**Family Z = 配線済み・runtime未確認(Z-1はTrial中)**。

| # | 項目 | Family X | Family Z |
|---|---|---|---|
| 1 | 正式初回経路 | 充足: selector(Stage1直後)にM2、runner新out_dirは既定n01(Coffeeは明示`--style-profile coffee_n01_r2_p3`)。Fallback通知もscaffold正式経路に実装 | 充足(N01定数差替)。M2はZ-1(Trial中・Production実装は移行方式のユーザー採用判断後)で未着手=承認範囲どおり |
| 2 | retry/fallback/regen整合 | 充足: PATH_MAP_01+回帰全PASS。M2失敗時は既存Strategy L fallbackに乗せ、通知を追加(上限・Gateは無変更) | 充足(共有module、回帰PASS) |
| 3 | Trial専用実装に依存しない | 充足: Production module(`er030_..._m2_supply_01`等)はer064/er073等をimportしない(grep確認) | 同左 |
| 4 | Regression/Validator/integration test PASS | 充足: er030 108/er019 357/er063 59/er026 107(+全体regression結果はEVIDENCE_02末尾) | 充足 |
| 5 | 正式経路でのruntime発火 | **未充足**: KP M2は3回発火(a2/b1b/a2再生成、kp_supply=m2)。N01はStd 3part+Adv 3part。**Std KPが2回続けてcanonicalization INVALID=Std完走せず**。**Adv正式`--stage assemble`はAudio Validation GateでBLOCK**(seed segmentがUNVALIDATED)。Fallback通知の実発火(Production run)は未観測(mockのみ。Coffeeではfallback発生なし) | **未確認**(Z記事再生成・音声化STOP中) |
| 6 | actual model_id/routing | 充足: gpt-6-luna(KP、telemetry/metadataにactual記録)/gemini-3.8-flash-lite-tts/既存ASR cascade | **未確認** |
| 7 | CURRENT_SPEC更新 | 充足(委任_02+委任_03追記: M2 Fallback、N01 Fictionでも不変) | 同左 |
| 8 | DECISION_LOG更新 | 充足 | 同左 |
| 9 | OPEN_ITEMS更新・整理 | 充足(OPEN-343更新/344更新/345 CLOSED/346追記/347新規) | 同左 |
| 10 | commit/push/merge | 充足見込み(最終commit後に確定、明示add・secret scan・Managed-ID trailer付き) | 同左 |
| 11 | 承認内容とProduction挙動の一致 | **部分**: M2P0仕様・N01逐語・6%減速/再検証維持・M2失敗時Strategy L Fallback+必須報告(summary/notice/stdout)は一致。**Std episodeでの完走確認とAdv正式assembleでの確認は未** | 未確定(Z-1/移行方式のユーザー採用判断待ち) |
| 12 | Dangling Referenceなし | 充足: SSOT内のOPEN/UDR/ファイル参照を確認(下記)。新規参照はEVIDENCE_02/evidence_02.json/seed scriptすべて実在。Z-1のTrial成果物(`er073_*`)は別IDで未コミットのため、参照は「別管理ID」と記載しファイル名では参照しない | 同左 |

## Family X が PRODUCTION_WIRED にならない理由(未達)
1. **Std KP**: 既存canonicalizationがrank5『based on』→『based on interviews』でRule7 INVALIDを2回連続(委任_02+本委任、通算retry各2回=4回不合格)。selection段が同じ`based on`を再選択し続ける確定的再発。KP再生成の追加はループ化するため再実行しない(Fable許可1回を使用済み)。
2. **Std Full Story part2**: N01 attempt1がASR不合格→既存Standard fallback take(N01でない)で合格、M3 Gate(Std)=BLOCK。ユーザー判断(人間承認 or 再生成)待ち。
3. **正式`--stage assemble`未完走**: Adv正式assembleがAudio Validation GateでBLOCK(OPEN-346②と同根: `--only-segments`で生成していないsegmentは`SKIPPED_NOT_SELECTED`=UNVALIDATED)。Gateは迂回していない。Std assemble不可。
4. Fallback通知のProduction runでの実発火は未観測(mock testのみ。Coffee run 3回はfallback発生なし)。
