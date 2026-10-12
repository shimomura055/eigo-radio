# COFFEE-FINAL-REASSEMBLY-PLAN-01(Coffee最終版 再Assembly作業計画)

- 管理ID: PM-COFFEE-REASSEMBLY-CONDITIONS-AND-USER-DECISION-REGISTER-01 委任_01
- 日付: 2026-10-12 / 種別: 計画書(実行はしない。API費用JPY0、コード・音声・Prompt・Production変更なし)
- SSOT: DECISION_LOG(本日付エントリ)、OPEN-321(本計画の参照)、OPEN-316/317/300/312/313
- 本書は仕様の複製ではない。実行時は必ずSSOTを再照合する。

## 1. 必須反映5点(ユーザー指示 2026-10-12、逐語要旨)

In One Line関連仕様が確定した後、Coffee最終版を再Assemblyする際には必ず次をすべて行う。

1. 確定したIn One Line関連仕様を反映する。
2. **Advanced Key Phrase英英解説の正式選択済みP3音声Styleを必ず反映する。**
3. Standard Preview/Commentの承認済み**R2**も反映する。
4. 既存音声の流用だけで済ませず、変更対象の音声を更新する。
5. 最終Assembly後、対象Styleの適用を**runtime evidenceと試聴ページで確認**する。

加えて: Production正式経路への反映完了(`PRODUCTION_WIRED`)は**Gate 3の全条件**を満たしてから判定する。

## 2. 前提(ブロッキング)

| 前提 | 状態 | 備考 |
|---|---|---|
| In One Line関連仕様の確定(=Comment4 Trial-03採否、OPEN-316) | **USER_DECISION_REQUIRED(未確定)** | 全体の前提。確定前は再Assemblyを開始しない。OPEN-299(IOL 2文方針の仕様化)も関連 |
| Adv KP英英解説=P3 | 判断済み(2026-10-12) | 再質問禁止。OPEN-317 |
| Std Preview/Comment=R2 | 承認済み(2026-10-12) | 再質問禁止。DECISION_LOG STANDARD-JA-AOEDE-STYLE-TRIAL-02 |
| Full Story=P8 | 判断済み(OPEN-311/300) | 既存音声流用可 |

## 3. 対象音声

| 対象 | 方針 | 理由 |
|---|---|---|
| Std Comment 4 | **再生成** | Trial-03採否の結果(採用ならPrompt反映後のComment4、不採用でもR2 Styleで再生成) |
| Adv KP英英解説(5 KP分、2026-10-12訂正: 4件→5件) | **P3 Styleで再生成** | 現行v4はP0(`KEY_PHRASE_EXPLANATION_EN`)。必須反映2 |
| Std Preview / Comment 1〜3 | **R2 Styleで再生成** | v4 Std Comment 1〜4音声は provenance 上 P2、R2未反映(OPEN-316付随) |
| Std/Adv In One Line | 確定仕様に従い再生成 | 必須反映1。仕様確定(OPEN-316/299)次第で必要範囲が決まる |
| Full Story Part1〜3(Std/Adv) | **既存v4音声を流用可** | P8は反映済み(Stdのみ6%減速、Advは減速なし)。sha一致を確認して流用 |
| Intro A5/B5、Adv Preview E1、K2、M2、タイトル等 | 既存流用(Style不変) | 変更対象外。ただしreuse判定が`style_version`のみでprofileを見ない点(OPEN-313 a)に注意し、流用前にstyle sha照合 |

## 4. 工程(直列の理由: 前工程出力に依存)

1. **前提確認**: OPEN-316が確定済みか、STOP_NOTICE/STOP/STOP_ALL不在を確認。予算を確認(下記5)。
2. **生成**: (a)Std Comment 4 Prompt反映(採用時のみ別委任・Production Prompt変更・Opus条件C)(b)Adv KP解説P3再生成(c)Std Preview/Comment1〜3 R2再生成(d)IOL再生成。生成は既存Production runner経由。独立な生成(b/c/d)は並列可(同一ファイル/state競合なし、runner分離時のみ)。
3. **Assembly**: 全clipを既存Assembly経路で結合(流用分はsha照合)。Coffee限定Style profile機構(OPEN-300、`--style-profile coffee_p8`相当を、P3/R2/IOLのroleへ拡張=OPEN-313(a)(b)(c)が前提)。
4. **QA/速度測定**: ASR Gate(Primary→Secondary、Cascade)、duration Gate、WPM実測(Std: 6%減速後、Adv: 減速なし)、境界無音測定(OPEN-317の(b)は別件、測定のみ)。
5. **runtime evidence**: 各対象clipについて`style_profile.json`等でP3/R2/IOL適用(style_base_sha256・最終prompt sha)を実測、reuseしたclipとの区別を記録。
6. **試聴ページ**: `user_test/`配下に再Assembly版ページを作成し、対象Style適用clipを明示。ユーザー試聴はP3/R2の採否ではなく**品質確認**(P3/R2の採用判断は再度求めない)。
7. **Gate 3確認**(下記6)→ `PRODUCTION_WIRED`判定はFable/ユーザー。

## 5. 費用見積(概算・実測単価からの推定。実行前に再見積し予算確認)

根拠となる実測: KP英語解説Trial 30サンプル=JPY5.353(約JPY0.18/サンプル、TTS)、P8 wiring evidence(両level Full Story 6 segment)=JPY13.19、Comment4 Trial-03 3 call=約JPY0.17(文章のみ)、IOL各1 call=約JPY0.1。

| 項目 | 概算 |
|---|---|
| Adv KP解説P3 5 KP(訂正: 4→5、retry込み最大3回) | 約JPY0.7〜2.2 |
| Std Preview/Comment1〜4 R2(5clip+retry、ASR込み) | 約JPY1〜4 |
| Std/Adv IOL再生成(文章+TTS+ASR) | 約JPY0.5〜2 |
| Std 6%減速後の再検証・Secondary ASR | 約JPY1〜3 |
| Full Story | 流用なら0(再生成が必要になった場合のみ別途、前回実績JPY13前後) |
| **合計(Full Story流用)** | **約JPY3〜11、上限目安JPY15** |

注: 上記は推定であり、実行時に`--approved-budget-jpy`を設定する。累計の取り扱いはOPEN-315(cost_log.jsonlにJPY列なし・run単位のBudget guard)に注意。

## 6. Gate 3条件(`PRODUCTION_WIRED`の前提。PM_GOVERNANCE Gate 3を正本とし、ここへは複製しない)

すべて満たすまで`PRODUCTION_WIRED`としない。

- 初回生成 / retry / fallback / Local Rewrite / resume の各経路でStyle(P3/R2/IOL)が維持される実測。特にLocal Rewrite再TTSでrole styleが落ちる既存の穴(OPEN-312)と、fallback時のBLOCK実動作(OPEN-300、未実測)。
- runtime evidence(実TTS、新out_dir、Std/Adv両level)。style sha・WPM・Gate通過。
- Regression: 既存test群で新規failureなし(共有module変更時は特に)。
- SSOT: CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSの整合(「判断済み」を未決へ戻さない)。
- Git: commit/push、secret scan PASS。
- Dangling Reference Check: 変更したStyle定数・Prompt・runnerを参照する他箇所(他Family/Master Store/reuse判定)に取り残しがない。
- Opus独立技術レビュー: 新構造(Style profile機構のrole拡張)は条件A、Production採用提案前は条件C(11-3節)。

## 7. 再質問禁止事項

- **P3(Adv KP英英解説Style)**・**R2(Std Preview/Comment)**の採否をユーザーへ再度求めない。
- 推薦P5/P8(OPEN-317旧記載)、他候補(Q1〜Q8等)を再提示しない。
- 提示してよいのは: OPEN-316(IOL関連仕様=Comment4 Trial-03採否)、および実際に新規で判断が必要になった事項のみ(PM_GOVERNANCE 12節の4区分に従う)。

## 8. リスク・注意

- OPEN-313(a)(b)(c)未対応のままP3/R2を既存Master Store/reuseに載せると既存共通masterを汚染/誤流用する恐れ(`style_instruction_id`を`coffee_*`に分離)。
- OPEN-312(Local Rewrite再TTSでStyle脱落)により、LR発火時にP3/R2が落ちる可能性。M3相当Gateで検知・BLOCKし、無承認でAssemblyしない。
- 全記事共通への展開は本計画の範囲外(OPEN-298、未決定)。
