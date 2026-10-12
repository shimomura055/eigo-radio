# 委任_05B 報告: Opus総合レビューM1〜M5反映・0円追加確認・統合報告書v01・未確定音声の試聴ページ(2026-10-12)

管理ID: ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_05B。Status: USER_DECISION_REQUIRED(設計案+Trial統合。Production/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER無変更、SSOTは委任_06)。有料API 0円。
使用モデル: 新規モデル呼出なし(保存ログ・保存転写の再判定、既存validator純関数、静的ページ生成のみ)。

## 成果物
- 統合報告書: `er058_output/RECONCILIATION_FINAL_REPORT_01.md`(ユーザー指定11章、判断材料先頭)
- 設計書v04(v03/v01は残す): `er058_output/design/UNIFIED_FLOW_SPEC_V04.md`、`MINIMAL_FALLBACK_REMOVAL_DEPENDENCY_V04.md`、`KP_K2_VS_EXISTING_COUNTERMEASURES_V04.md`
- 試聴ページ: https://shimomura055.github.io/eigo-radio/user_test/asr_misread_listen_01/index.html (40音声、Pages 200・実再生40/40 OK)。evidence: `er058_output/PLAY_EVIDENCE_05B.md`/`.json`、対応表 `er058_output/trial_abc/listen_items_05B.json`
- 再現script: `er058_05b_two_label_rejudge_01.py`(M1)、`er058_05b_zero_yen_checks_01.py`(0円確認)、`er058_05b_listen_page_01.py`、`er058_05b_play_evidence_01.py`。出力 `er058_output/trial_abc/two_label_rejudge_05B/`、`zero_yen_checks_05B/`

## M1〜M5の反映結果
- M1: 2ラベル版で再判定。**この標本では救済(4/22)・誤PASS(0/11、Secondary起因1/30)・対照不採用(0/29)は不変**。差は「Primary PASS対照をSecondary単独判定した偽NG」0/6→2/6(`20%/20 percent`=NUMERIC_EQUIVALENCE)。英語4/日本語2の非対称を選択肢化(D-3)。
- M2: 「数値・否定37/37ブロック」を**否定26/26・数値11/15**へ訂正。穴4件は全て`N%`付き数値の変更(S03/S17/S25/S30)。日本語S1は`\d+`のみで、**漢数字の値変更(三人→四人)を見逃し、表記差(二人/2人、三十人/30人、十分/10分、100円/百円)で発火**を実測。方針=値の不一致で判定し個別正規化(PHONETIC一括許容は不可)。
- M3: PASS_WITH_WARNINGの試聴リスト連動を導入の前提条件に(V04 2-6)。
- M4: 見出しは`point_headings_aoede` L77-100で`max_attempts=3`時に標準1+minimal2。**見出し経路は元から`force_secondary`なし(L126-128)=撤去で外れる保護は無い**(Opus指摘の見出し部分は厳密には不正確、v04で明記)。`force_secondary=True`を渡すのはA2 minimal fallback(LR後再TTS含む)のみ。ユーザー判断事項D-5へ。
- M5: (a)cool-down廃止は平均約30〜48秒/segment(最大600秒は通算3回目到達の5〜8%のみ)、導入理由を外した影響の対照データなし (b)V03 1章の技術失敗/無音の矛盾を統一 (c)Trial D「V4でK2効果が薄れた」→区別不能(n=1、差0.1〜0.2秒)。
- C-6: 累積ガード(`MAX_CUMULATIVE_TTS_ATTEMPTS=15`/ASR 60)再計算、**A2のLR再TTS未計数(`count_tts_generations_in_result`/`resolved`)を必須是正**と明記。D6(Tier3/CS層とAzure二重呼出、+約2円/件)を費用に加算。

## 0円追加確認(R4)
1. KP 2段目(English Lock)救済: 2026-09-01以降294 call中**4件(1.4%)**(Flash-Lite現行の保存音声で確認できた1件を含む3件はMinimal 2回NG後にEnglish Lockで合格)。**ゼロではない**=P-a(現行Minimal維持)の根拠にはならず、追加Trial(数円)が妥当。
2. LR再TTS: **minimal依存はA2経路(crosslevel L383)のみ**。voice01 L359/news_tail_fix L368は標準Prompt 1 attempt(`__wrapped__(max_attempts=1)`)。
3. Master Store: 全378件`instruction_path=primary`、**minimal/English Lock由来を示す印なし**(キーにstage情報なし)。標準キー混入の有無はmanifestだけでは判定不能。KP Prompt変更(P-b/P-c)で既存241件が再利用不可。
4. 日本語minimal leakage: Flash-Lite+`speech_metadata`(Production現行)は**0/87**。発生は旧方式(AB trial、指示文同居)のみ(標準7/8、minimal 3/5)。
5. 400エラー: 保存audit 59ファイル・138事象、同一instruction_typeの後続attempt 91件で**同一Prompt再試行成功51件(56%)・再400 37件・他3件**=**確率的、決定論的ではない**(V03 2-5を訂正)。Flash-Lite期の400実績は保存ログに無い。
6. minimal残存経路: A2英語/日本語(撤去対象)、B1/Charon技術的fallback(`trimmed is None`時)、**見出し(標準1+minimal2)**、legacy label、KP専用Minimal、汎用定数(V04 9-6、MINIMAL V04 10章)。

## 検証
- 2ラベル再判定、0円確認、Playwright実再生(Pages上40/40、HTTP 200、幅360px、`file:///`なし、結果テキスト化ボタン動作)を実行。
- Production無変更: 追加はer058_05b_*.py、er058_output、user_test/asr_misread_listen_01、docs/pm配下のみ。worktree(eigo-radio-prodfix/-tone)は読み取りのみ(target_rmsの値参照)。
- 既存の無関係な未commit差分には触れていない。
