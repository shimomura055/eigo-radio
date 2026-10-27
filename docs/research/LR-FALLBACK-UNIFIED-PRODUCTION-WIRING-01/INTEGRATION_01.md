# INTEGRATION_01: Phase A統合設計(Fable、2026-10-28、Opus条件Aレビュー対象)

管理ID: LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01。ユーザー原文=`docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER.md`。入力=W1(`W1_ROUTE_WIRING_AND_RECORDS_01.md`)/W2(`W2_UD1_BODY_REFLECTION_DESIGN_01.md`)/W3(`W3_UD3_GATE_DESIGN_01.md`)/W4(`W4_FINAL_HUMAN_REPORT_DESIGN_01.md`+`W4_SAMPLE_01.html`)。SSOT登録=PM-SSOT-SYNC-29(91767cb54、OPEN-569)。

## 1. 全体構造(新規の処理フロー=Opus条件A)

```
[TTS層: er127.BlockRun.finish / Z ctx policy]  ──追記──▶ clip entry に final_adoption{attempt_id, wav_sha256, style_name, style_sha, slot(①②③/①'②'③'), lr_applied, lr_block_depth, human_approval_superseded}
        (既存記録・Gate判定・retry/待機/Fallback Style/LR範囲は不変。追加のみ)
                     │
[導出層(新 er129_lr_display_reflection_01.py、純関数・読取専用)]
   入力: 最終entry群(tts_generation_results等)+LR記録(local_rewrite_recovery / resume形は before/after のトークン差分)+人間承認flag(resolve_expected_text_after_local_rewrite を唯一の参照点)
   出力: <run>/<level>/audit/lr_fallback_ledger.json(毎回全置換で導出。手編集不可)
        = clip毎 {role, segment/chunk id, final_adoption, lr{before,after,changed_spans,reason}, fallback{used, adopted_style, from_style}, text_parity{display,tts_input,asr_expected, verdict}}
                     │
      ┌──────────────┼──────────────────────────────┐
[表示本文overlay]  [三者一致Gate(assemble直前)]   [採用take分類核 classify_adopted_take]
 ページ描画・     表示=TTS入力=ASR正解の          X M3 / Y style gate / Z gate が共通で呼ぶ
 ハイライト解決は  文単位照合。不一致・位置不能     正常(承認済みFallback Style allowlist∧記録完全∧ASR PASS系∧
 ledger経由で     =技術STOP(HRキューへ入れない)      parity PASS∧確定KP非干渉)→通過(警告記録)
 書換え後文を表示                                   異常/UNKNOWN(記録欠落)→従来どおりBLOCK(fail-closed)
                     │
[最終Human報告生成器(新 er_final_human_report_01.py、読取専用CLI、E2E_STAGESに入れない)]
   出力: final_human_report/<family>/<slug>/<run>/{standard,advanced}.html(user_test/外)
   LR=赤(変更後語句 太字+二重下線、変更前 取消線、前後英文併記)/Fallback=濃青(対象テキスト全体+注記)/重複=青区間内に赤語句/履歴=灰(色の意味なし)/文字ラベル併記/記録欠落=「記録なし」
```

原本原稿(writer出力・article.md・parts.json・canonical_text・ユーザー承認済みスクリプト)は**書き換えない**。理由(W2 §2): parts.json書換えは既存LR音声の再生成・HR Lock key無効化・er128再バインド・V3照合コードt8無効化を誘発し、「LR承認が本文書換え+再生成に化ける」ため。overlay方式はこれらがすべて不変で、ユーザー決定「LR後の英文を最終表示本文にも反映」「三者一致」を満たす。

## 2. Fable統合判断(B項目の決定)

| # | 論点 | 決定 | 根拠 |
|---|---|---|---|
| F-1 | UD-1方式 | 派生overlay+導出台帳(W2推奨) | §1。原本不変・再生成誘発なし・確定内容保護sha不変 |
| F-2 | 採用take記録 | `final_adoption`新設(W1 J-1)。書込みは`er127.BlockRun.finish`1点+Z ctx 1点。Gate判定の入力は台帳経由 | 経路毎の記録キー差・entry直下`fallback_used`の誤表示(W1 §5・W4落とし穴1)を単一記録で解消 |
| F-3 | 台帳と報告資料の関係 | W2 ledger=唯一の導出物。W4生成器・W3分類核・三者一致Gate・表示overlayはすべてledgerを読む(W4の独自読取規則はledger導出関数へ統合) | 読取規則の二重化防止 |
| F-4 | UD-3適用範囲 | 全profile(W3 B-2)。Zの`Z_STYLE_FALLBACK_ADOPTED`停止(er063:2138-2140)も解除対象(W3 A-2) | 原文§5「他Familyの相当経路も対象」 |
| F-5 | リリース順序 | UD-3解除は三者一致Gate(UD-1)・final_adoption記録と同一commit群で配線(W3 B-1)。未配線中は一致検査が異常側(BLOCK)に倒れる設計 | 本文音声不一致を無検知で通さない |
| F-6 | 旧記録(OPEN-564以前のStd `fallback_used=True`等) | 記録完全なら警告、不完全ならBLOCK(W3 B-4)。旧run再生成なし、読取側で`retts_result`から再導出(W1 J-6) | UD-2「不要な再TTSなし」 |
| F-7 | Z `style_actual`の採用attempt誤同定(W4 A-1、告げ口心臓Adv KP2でK2記録/実採用ENGLISH_LOCK) | 11-8不具合として是正(Phase B) | UD-3「承認済みStyle照合維持」の精度 |
| F-8 | Z LR後attemptのStyle記録欠落(W4 B-1/W1 J-4) | 最小記録追加(final_adoption導入で充足) | 記録完全性=停止/通過判定の前提 |
| F-9 | Z公開ページのLR注記・Voice/Style表示(er063:2465,2468、W2 §8/W4 B-2) | 公開ページから撤去し最終Human報告へ移す | 原文§2(学習者向け本文に注記混入禁止) |
| F-10 | 既公開4件の実態 | AI島Std/Adv=未公開・未組立(UD-2適用→M3再評価→組立→候補ページ+最終Human報告)。メロスAdv=現行公開`family_z_melos_02`はLR 0で不一致なし(旧`_01`はsuperseded、対象外)。Word Gacha Adv・猿の手Std=各1語の表示overlay(API 0)を候補ページとして作成し、公開差替えは記事単位承認(ユーザー)へ | 原文§8「必要十分・一律作り直し禁止・記事単位承認」 |
| F-11 | 確定内容との重なり | T1語句(er128.lr_overlap 記録のみ→停止へ格上げ)/T2確定項目・文法の出典文/T3数字・固有名詞(W2 §5)。干渉=STOP/USER_DECISION_REQUIRED。実データ5件は全件1語replace・非干渉(W2 §6) | 原文§3 |
| F-12 | 人物名→代名詞(Melos→He)の許容 | 現行公開に該当なし(melos_02 LR 0)。CURRENT_SPEC:1486の解釈は変更せず、将来発生時はT3(固有名詞)でSTOP→ユーザー判断 | 新規判断を今は求めない |
| F-13 | A/B/C | 読取のみ(`fallback_used`/`instruction_type`/`local_rewrite_recovery`同形)で最終Human報告に「Fallback有無のみ/記録不足で表示不可」を明記。生成・Gate・待機は不変 | 原文§1「音声方式を置換しない」 |
| F-14 | 告げ口心臓 | LR 0・**Fallback 1**(Adv KP2「mock」=ENGLISH_LOCK、承認済みKP_EN 2+2内、ASR PASS)。本案件で変更なし。最終Human報告に青で表示。前報の「Fallback 0」は訂正 | 事実訂正 |
| F-15 | runtime evidence | (1)保存run読取再評価(AI島hr_02・Y E-1・Word Gacha Adv・tru_ev evidence run群、API 0) (2)既存承認済みdriver `tru_ev_*.py`で最小有料(見積¥10〜40、7-7の300円以下) (3)未実走9行(shell固定英語3は表外・固定mp3は生成なし・残りY chunk 2/Z legacy会話2/shell日本語2は各¥0.3〜3) | 原文§10-11 |
| F-16 | HR Lock/HRQ | 正常LR/Fallbackでは元々投入されない。解除対象=M3/Y gateの人承認待ちのみ。`LR_REWRITTEN`は記録維持・HR非要求。`pass_with_warning_listening_list`は無改修 | W3 §3 |

## 3. 変えないもの(原文§7の固定、受入で照合)
TTS試行回数・180秒待機・Fallback Style・LR適用範囲(49行policy)・ASR判定基準・Voice/速度・確定内容保護(G0-G4/照合コード)。leaf TTS関数・`er020`・`er127`のpolicy定義は編集しない(final_adoption追記はfinishの追加のみ)。A/B/C golden byte同一。

## 4. Phase B 実装分割(並列、API 0)
- B1 `final_adoption`記録(er127 finish+Z ctx)+test。
- B2 `er129_lr_display_reflection_01.py`(ledger導出・トークン差分・三者一致・T1-T3重なり)+test。W4 §3の43 LR entryに適用し偽STOP 0を確認(最初の作業)。
- B3 表示overlay配線(X `er019_family_x_listening_page_01`/Y/Z `er063` pages)+Z公開ページ注記撤去+混入検知test。
- B4 `classify_adopted_take`共通核+X M3/Y gate/Z gate接続+既存test 8ファイル更新+新規15ケース。
- B5 最終Human報告生成器+混入防止5層test+Family別integration。
- B6 Z `style_actual`是正(F-7)。
- B7 既公開是正: AI島UD-2適用→M3再評価→組立→候補ページ/Word Gacha Adv・猿の手Std候補ページ(1語overlay)。
- B8 runtime evidence(保存run再評価→最小有料)。
- B9 SSOT/Git/受入。
依存: B1→B2→(B3,B4,B5)。B6/B7/B8はB2後。

## 5. Opus条件Aレビューで特に見てほしい点
R-1 overlay方式で「表示本文=TTS入力=ASR正解」が4経路(初回/retry・fallback/regeneration/resume・再利用・人間承認原文復帰)で保証されるか、抜け(例: KP phrase再利用時のFallback記録継承、Z chunk境界をまたぐLR)。
R-2 `final_adoption`1点書込みで採用takeが常に一意になるか(Z ctx policy・ENGLISH_LOCK段・減速後再検証・HR個別採用の各経路)。
R-3 `classify_adopted_take`のfail-closed条件が「正常LR/Fallbackのみ解除」を超えてGateを弱めないか(allowlist導出元・UNKNOWN扱い・旧記録)。
R-4 確定内容重なりT1-T3の偽STOP/見逃し。
R-5 注記混入防止(5層)の抜け。
R-6 リリース順序(F-5)と部分配線時の安全性。
R-7 既公開是正(F-10)の範囲が原文§8の「必要十分」を超えないか。
