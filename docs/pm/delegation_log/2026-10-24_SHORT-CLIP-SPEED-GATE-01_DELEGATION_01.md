FAMILY-Z-MONKEYS-PAW-PRODUCTION-01 委任_04 / SHORT-CLIP-SPEED-GATE-01 委任_01(Fableから、同一委任で実施): ユーザーが(①)『猿の手』Std/Adv最終試聴PASS・正式承認、(②)極短clip速度Gateの共通仕様をAPPROVED_FOR_PRODUCTIONとした。①のCloseoutと②のProduction Wiring(X/Y/Zを独立管理)を行う。

## 0. 最初に(0円)
- ユーザー指示原文(本委任文末尾【ユーザー原文】、逐語)を `docs/pm/delegation_log/2026-10-24_FAMILY-Z-MONKEYS-PAW-PRODUCTION-01_USER_02.md` に保存(同内容を `2026-10-24_SHORT-CLIP-SPEED-GATE-01_USER.md` にも)。
- UDR #180=判断済み(PASS)、UDR #181=判断済み(ユーザー採用値: 元音声1.5秒未満は長さ比0.90〜1.00、1.5秒以上は現行0.93〜0.96、1.5秒ちょうどは従来範囲。Fable推奨Aの絶対誤差方式ではなく比率範囲方式をユーザーが決定)に更新。

## A. 『猿の手』Closeout(0円)
- `OPEN_ITEMS.md`: 本作のUDR待ち項目をCLOSED(ユーザー最終試聴PASS 2026-10-24)。残存Open Itemが本作に紐づかないことをGrep確認(OPEN-495 CLOSED、OPEN-496は②で解決へ)。
- `DECISION_LOG.md` 1エントリ(正式承認、実費46.82円、Std 301.9s/Adv 291.2s、Local Rewrite 1件開示、commit 33565584a/8cf1f7726/fdf8a8e40)。
- `docs/research/FAMILY-Z-MONKEYS-PAW-PRODUCTION-01/CLOSEOUT_01.md`(『賢者の贈り物』の書式: 完了条件照合、成果物、費用、PM Closeout Mandatory Check、残存なし)。

## B. 極短clip速度Gate Production Wiring(API 0、音声再生成なし)
1. 現状確認(`docs/research/SHORT-CLIP-SPEED-GATE-01/CP_CHECK_01.md`): X/Y/Zの速度処理とGateの所在。Z=`er063_family_z_audio_01.py` `verify_z_speed_profile`(`ADV_DIALOGUE_RATIO_MIN/MAX`=0.93/0.96、Adv会話のみ)。X=同等のGateがあるか(`er019_*`/speed v2関連をGrep。委任_03の分析では「Xは対象外」)。Y=音声段(`er110_family_y_*audio*`)が共通音声段経由でZ/Xのどちらの速度処理を使うか、速度Gateの有無、Production実装状況(OPEN-484)。同等Gateが**存在するFamilyのみ**適用対象。存在しないFamilyは「対象Gateなし(適用不要)」として記録し、PRODUCTION_WIREDとは呼ばない。Yが未実装なら未配線事項をOPEN-484へ記録。
2. 実装(対象Familyの共通処理1箇所が望ましい): 元音声長(speed調整前の原音秒)が`< 1.5`なら許容`0.90〜1.00`、`>= 1.5`なら`0.93〜0.96`。境界は厳密(1.5ちょうど=従来)。比較は既存と同じ丸め/浮動小数の扱いで、境界testで固定。定数名・位置は既存慣例に従い、flagなし(ユーザー正式採用済み)。速度設定・他の品質条件は変更しない。旧条件の不要な残置がないことをGrepで確認。Dangling Reference(未承認仕様への参照)なし。
3. test: (1)<1.5で0.90〜1.00、(2)>=1.5で0.93〜0.96、(3)境界(1.5、1.4999、0.90、1.00、0.93、0.96の内外)、(4)『猿の手』の旧テイク"Wait!"(0.771s、比0.9670)がPASS、(5)真の異常(例 0.77sで比0.85や1.05、2.0sで比0.97)はNG、(6)既存の音声品質test・全回帰(REGRESSION_BASELINE_2026-10-24と比較、自分起因の新規失敗0)。
4. runtime evidence(正式経路、省略不可、音声再生成なし): 『猿の手』run `run_sf_prod_01` の保存clipに対し、正式Production経路のgate段(`--stages gate`等、既存のresume/再判定の口。assemble/pagesを再実行して公開物を変えないこと。必要なら run のコピーで実施し、コピーであることを明記)を実行し、新条件での判定ログ(全会話clipの原音長・比・適用範囲・結果)を取得。加えて、退避済みの旧テイク `_regen_backup_part3_c5_20261024/` を使って旧テイクがPASSすることを正式関数で確認(runを汚さない)。retry/fallback/regeneration/resume経路でも同じ関数が使われることをコードで確認(呼出箇所一覧)。X/Yに同等Gateがあれば同様に。
5. SSOT: `CURRENT_SPEC.md`の速度仕様v2/Gate該当節に新条件を追記(Family別Status: Z=PRODUCTION_WIRED(本委任)、X=対象Gateなし or WIRED、Y=未配線/対象なし)。`OPEN_ITEMS.md` OPEN-496→解決(Z PRODUCTION_WIRED、Fable受入待ち)、Y未配線はOPEN-484へ。`DECISION_LOG.md` 1エントリ。
6. Git: `git status`でindex確認→`git commit --only`(本委任ファイルのみ)→`git push origin HEAD:main`。他agent(ASR Trial)の差分を巻き込まない(一時index方式)。禁止操作(add -A/-u/-f/-N、amend、rebase、force push、stash、clean、reset --hard、checkout -f)。secret grep 0件。wav不追跡。
7. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_SHORT-CLIP-SPEED-GATE-01_DELEGATION_01.md`(Nは先頭「FAMILY-Z-MONKEYS-PAW-PRODUCTION-01 委任_04 / SHORT-CLIP-SPEED-GATE-01 委任_01」を含むAgent呼出の0始まり通番、直近472以降)。

## handback(ユーザー原文§6): A=試聴PASS記録・最終Status・費用・残Open Item。B=X/Y/Z実装状況(表)、新旧適用結果(猿の手の全会話clip)、境界値・異常検出・Regression結果、runtime evidence、SSOT/Git、未配線・判断事項。RESULT_PACKET 4行、commit hash、raw URL。Fable受入判定が必要な点を明示。

【ユーザー原文】
# Claude Codeへの指示
## Family Z『猿の手』Closeout ＋ XYZ共通・極短clip速度Gate改善

### 1. ユーザー承認事項

**① Family Z『猿の手』：最終承認**

- Standard／Advancedともにユーザー最終試聴PASS。
- 現行完成音声を正式承認。
- 追加の音声修正・再生成は不要。
- 最終承認を記録し、残存問題がないことを確認して記事制作案件をCloseする。

**② 極短clip速度Gate：正式採用（APPROVED_FOR_PRODUCTION）**

以下をFamily X／Y／Z共通仕様として正式採用する。

| 対象 | 速度調整後／調整前の長さ比の許容範囲 |
|---|---|
| 元音声1.5秒未満 | **0.90〜1.00** |
| 元音声1.5秒以上 | **0.93〜0.96（現行維持）** |

判定境界は厳密に適用すること。1.5秒ちょうどは従来範囲とする。

目的は、極短clipの速度処理に伴う微小な測定誤差による不要な停止・再生成を防ぐこと。

**実際に不自然な音声や速度異常が発生した場合の品質検出能力は維持する。**

### 2. 実装方針

- まずX/Y/Zの既存速度処理・Gate構成を確認する。
- 同等の速度Gateが存在するFamilyには共通仕様を適用する。
- 共通処理として統合可能なら、重複実装を避ける。
- Familyごとの既存速度設定や承認済み仕様は変更しない。
- 速度Gate以外の品質条件を緩和しない。
- 既存の正常音声を不要に再生成しない。

Family Yについては、Production実装状況を確認すること。未実装部分があれば、既存の承認範囲で対応できるか整理し、未配線事項をOPEN_ITEMSへ記録する。未実装FamilyをPRODUCTION_WIREDと報告しない。

### 3. 検証・受入条件

最低限、以下を検証する。

1. 元音声1.5秒未満では0.90〜1.00を適用。
2. 元音声1.5秒以上では従来の0.93〜0.96を維持。
3. 境界値（1.5秒、0.90、1.00など）の判定が正しい。
4. 今回停止した「Wait!」（0.77秒・比率0.967）がPASSする。
5. 真の異常（範囲外の速度・不正音声）は引き続きNGとなる。
6. 既存の音声品質検査・RegressionがPASSする。
7. 各Familyの正式Production経路に変更が反映されていることを確認する。

新規記事の全工程を再実行する必要はない。保存済み音声や既存テストを再利用し、必要十分な検証で完了させる。

ただし、PRODUCTION_WIRED判定に必要な正式経路でのruntime evidenceは省略しない。

### 4. PM Gate・SSOT

- ユーザーによる共通仕様の正式採用は完了。
- X/Y/Zそれぞれの実装・検証状況を独立して管理する。
- Production Wiringが完了したFamilyのみPRODUCTION_WIREDとする。
- 正式初回経路だけでなく、retry／fallback／regeneration／resumeとの整合を確認する。
- 未承認仕様への参照やDangling Referenceがないことを確認する。
- CURRENT_SPEC、DECISION_LOG、OPEN_ITEMS、必要なGit記録を更新する。
- 旧Gateの不要な条件・検査が残っていないか確認する。
- Fableによる独立受入評価を実施する。

### 5. QCD・STOP条件

優先順位は **品質 ＞ 完成速度 ＞ 量産単価**。

- 承認済み品質を維持しながら最速で完成させる。
- 独立した作業は並列化する。
- 既存データ・音声を再利用し、不要なAPI費用や再生成を避ける。
- 原則として既存の承認済み開発予算内で自律的に修正・検証する。
- 新たな仕様変更、重大な品質問題、承認範囲外の対応が必要になった場合のみユーザー判断へ上げる。
- 承認済み条件をすべて満たしたら、それ以上の追加Trialや磨き込みは行わない。

### 6. 最終報告

以下を簡潔に報告すること。

**A.『猿の手』Closeout**
- Standard／Advanced最終試聴PASSの記録
- 最終完成Status
- 費用・残Open Item

**B. 極短clip速度Gate**
- X/Y/Zそれぞれの実装状況
- 新旧仕様の適用結果
- 境界値・異常検出・Regressionの結果
- 正式runtime evidence
- Fable受入判定
- SSOT／Git反映状況
- 残存する未配線項目・ユーザー判断事項

**目標は『猿の手』の正式Closeoutと、承認済み共通仕様のProduction Wiring完了。**

不要な追加検証や日付分割を行わず、品質を守りながら最短で完了させること。