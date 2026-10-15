# STANDARD-KP-JA-TTS-STYLE-TRIAL-02 委任_01 (委任文保存, T-0)

管理ID: STANDARD-KP-JA-TTS-STYLE-TRIAL-02(SKJT-02)委任_01。現在Status USER_APPROVED_FOR_TRIAL。前Trial STANDARD-KP-JA-TTS-STYLE-TRIAL-01(commit 9c4b1437a、er057_std_kp_ja_style_trial_01.py、er057_output/std_kp_ja_style_trial_01/、user_test/coffee_std_kp_ja_style_trial_01/)の第2弾。ユーザー試聴結果(新事実): P5が最も希望に近い。ただしP5は少し抑制的すぎる。並行: KGCPW 委任_04(er026_output/.../run_kgcpw_z_e2e_01/・er071_output/.../gloss_alignment_production_wiring_01/のみ、SSOT不編集)。git index.lock衝突時は30秒待ち最大3回再試行。

## 性質/到達上限/禁止
- Offline Trial。到達上限 REJECTED/VALIDATED/USER_DECISION_REQUIRED(Sonnetは分類案、Fableが分類)。Production採用・変更・正式配線禁止。APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDへ変更しない。
- Opus独立技術レビューGate: 該当なし。
- 費用上限JPY10(Guardrail。T-3定型文)。見積: 新規TTS 25 call+ASR 25件 約JPY1.1(前回実費約1.08、cost_actual.json)。当日累計 約JPY20+KGCPW_04(上限80)/1,000。
- 禁止: 正式J3 Style・Standard Preview/Comment Style・英語KP TTS・Advanced・Full Story音声・KP日本語意味テキスト・gloss再整合工程・Production runner/retry/fallback/regeneration・Coffee完成版(user_test/coffee_m2p0_n01_final_03/および元run dir)の変更禁止。Prompt P5〜P10はユーザー提示文を逐語使用。Batch不使用、TTS_EXECUTION_MODE=STANDARD明示。Human Review queue/Lock不使用。git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f禁止。
- 時間見込み約1.5h。P6〜P10は同時3+2 process、ASR・客観指標は並列。

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(委任文のとおり。T-2: TTS_EXECUTION_MODE=STANDARD明示、7-5の4点[差分再生成可否・再利用cache・--budget-jpy明示・想定外全再生成ならSTOP]。本委任: J3・P5は既存再利用=新規0、P6〜P10の25 callが意図した新規生成。25超見込みなら実行前STOP。T-3: Cap到達=自動STOPではなく暴走疑い時のみSTOP)。

## 事前指定Read/Grep/手順(要点)
- er057_std_kp_ja_style_trial_01.py をコピーして er057_std_kp_ja_style_trial_02.py を作る(前回scriptは不変)。P5 Prompt shaをユーザー提示文と比較(不一致なら報告しP5は前回音声のまま再利用)。
- 出力先 er057_output/std_kp_ja_style_trial_02/(P6..P10/、J3_reuse/・P5_reuse/はhash・出典json、evidence/、cost_actual.json、asr_results.jsonl、objective_metrics.json、TRIAL_REPORT_02.md)。試聴ページ user_test/coffee_std_kp_ja_style_trial_02/index.html + audio/{J3,P5,P6..P10}_kp{1..5}.mp3(35本)。「すぐに」をページ先頭、7列、J3/P5に「既存音声の再利用」バッジ、Prompt全文折りたたみ。
- 手順: (1)STOP確認 (2)script_02作成+prompts_sha.json (3)dry-run (4)P6〜P10生成(3+2並列) (5)ASR 25件・客観指標(F0大=感情的/F0小=自然と判定しない旨を注記) (6)7x5比較表+「すぐに」詳細+P5との差(聴感未実施明記) (7)試聴ページ+再生確認 (8)共有state不変の証明(coffee_m2p0_n01_final_03・元run dir・er057 trial_01・Production Style定数ファイルのgit status差分0+sha一覧) (9)Dangling Reference Check。
- Status分類案: 原則USER_DECISION_REQUIRED。VALIDATEDはユーザー試聴でのみ。

## 実行コマンド
T-0 check_delegation_prompt / STOP確認 / dry-run / 生成(TTS_EXECUTION_MODE=STANDARD ... --styles P6,P7,P8 --budget-jpy 10、並列 --styles P9,P10) / secret scan(tools/secret_scan_01.py --staged) / git status --porcelain。

## SSOT追記
編集権あり(DECISION_LOG/OPEN_ITEMS/CURRENT_SPEC/REGISTER/REPORT_LEDGER)。DECISION_LOG: Trial-01ユーザー試聴結果(ユーザー原文§1逐語)+Trial-02実施事実+Production採用なし。OPEN_ITEMS: OPEN-367更新(新規起票なし)。CURRENT_SPEC: 事実1行のみ「(参考Trial・採用なし) 2026-10-15 STANDARD-KP-JA-TTS-STYLE-TRIAL-01/02でStyle候補P1〜P10を比較中(OPEN-367)。正式Style J3は無変更。」REGISTER #68更新。REPORT_LEDGER 1行。

## Git
明示addのみ(script_02、er057_output/std_kp_ja_style_trial_02/[wav除く]、user_test/coffee_std_kp_ja_style_trial_02/、SSOT5本、delegation_log本ファイル+_check.json)。コミットメッセージ指定あり。push to origin/main。push後Pages URL https://shimomura055.github.io/eigo-radio/user_test/coffee_std_kp_ja_style_trial_02/index.html のHTTP statusを1〜2分後に確認(404ならdeploy遅延として記録、再試行1回)。

## 報告
docs/pm/RESULT_PACKET_SKJT2.md へ (1)〜(14)項目(T-0/STOP、J3/P5再利用sha、P6〜P10 Prompt sha、見積と実費、7x5表、ASR、URL/再生確認、共有state不変、Dangling Ref、SSOT差分、commit/raw URL、Status案、逸脱、Fable向け判断材料)。Fableは(2)(3)(7)(8)を照合。

## ユーザー指示(原文・逐語)

# Claude Code／Fableへの指示
## Standard Key Phrase 日本語TTS Style改善 Trial 第2弾

**管理ID：STANDARD-KP-JA-TTS-STYLE-TRIAL-02**
**現在Status：USER_APPROVED_FOR_TRIAL**
**今回到達してよいStatus：REJECTED／VALIDATED／USER_DECISION_REQUIRED**
**Production採用・Production変更は禁止。**

## 1. 目的
前回Trial（STANDARD-KP-JA-TTS-STYLE-TRIAL-01）をユーザーが試聴した結果、P5が最も希望に近かった。
ただし、P5は少し抑制的すぎるため、**P5をベースに、もう少しだけ自然な抑揚・感情を加えたい。**
今回の目的は、次のバランスを探すこと。
- P5の落ち着き、過剰な感情表現の少なさを維持
- P5よりわずかに自然な抑揚・温かみを加える
- 「すぐに」など短い日本語訳を演技的にしない
- 機械的な棒読みにはしない
- 発音・明瞭さ・テンポなど、問題のない要素を維持する
今回も新規Styleを自動採用しない。

## 2. 比較対象
Coffee完成版のStandard Key Phrase日本語意味5件。
1 pump one's fist 大喜びする / 2 raw bean 生豆 / 3 right away すぐに / 4 based on interviews インタビューをもとにした / 5 take time 時間がかかる
テキストは前回Trialと完全同一。比較Style7種: J3(現行Production Baseline)/P5(前回Trialでユーザーが最も希望に近いと評価)/P6(新規・P5＋微弱な抑揚)/P7(新規・P5＋自然な抑揚)/P8(新規・ニュースキャスター風)/P9(新規・Podcastホスト風)/P10(新規・穏やかな音声ガイド風)

## 3. Prompt全文
J3: 落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。演技がかった話し方は避けてください。
P5: 落ち着いた、明瞭で自然な話し方で。短い言葉の意味を簡潔に、控えめな抑揚で読み上げてください。感情を強く込めたり、語尾を不必要に強調したりしないでください。
P6: 落ち着いた、明瞭で自然な話し方で。短い言葉の意味を簡潔に、控えめながらも自然な抑揚を少し加えて読み上げてください。感情を強く込めたり、語尾を不必要に強調したりしないでください。
P7: 落ち着いた、明瞭で自然な話し方で。短い言葉の意味を簡潔に伝えながら、普段の会話のような自然な抑揚と、ほんの少しの温かみを持たせてください。感情を強く込めたり、語尾を不必要に強調したりしないでください。
P8: 落ち着いたニュースキャスターのように、明瞭で安定した声で読み上げてください。自然な抑揚を保ちながら、短い言葉の意味を端的に伝えてください。大げさな強調や演技的な感情表現は避けてください。
P9: 落ち着いたPodcastホストのように、親しみやすく自然な会話調で読み上げてください。聞き手に意味を伝える程度の穏やかな抑揚と温かみを持たせてください。過剰な感情表現や大げさな語尾の変化は避けてください。
P10: 穏やかで自然な音声ガイドのように、明瞭で聞き取りやすい声で読み上げてください。平板にならない程度の柔らかな抑揚をつけ、短い言葉の意味を落ち着いて伝えてください。感情的な演出や不必要な強調は避けてください。
上記Promptを逐語使用すること。独断で文言を変更しない。

## 4. Trial実施方法
7 Style x 5 Phrase=35音声。J3: Coffee完成版音声を再利用。P5: 前回Trial音声を再利用。P6〜P10: 新規25音声。Voice Aoede / gemini-3.8-flash-lite-tts / speech_metadata_flash_lite。前回と同条件、Style以外変更しない。J3/P5既存音声は元の生成条件・ファイルhash・出典を確認。既存音声と新規音声に比較上重要な差があれば報告。費用: 前回実費約JPY1.08参考、新規TTSは原則25 call。新規Trial専用成果物を作成し、既存Coffee完成版・Production音声/Promptは変更しない。並列化するが過剰な同時呼出は避ける。

## 5. 試聴ページ
必須: Phrase単位でJ3/P5/P6〜P10比較、5 Phrase全掲載、個別再生、Prompt全文表示、J3とP5は既存音声再利用と明示、スマホ/PC対応、実音声再生確認、アクセス可能URL報告。「すぐに」をページ先頭に配置。

## 6. 評価方法
①P5からの改善(自然な抑揚・温かみ) ②感情過多の防止(J3の「すぐに」の不要な感情・演技の再発なし) ③自然さ(棒読み/平板でない) ④明瞭さ・安定性(5 Phrase全体で発音・聞き取りやすさ・テンポ)。ASR照合・F0・無音比率は参考指標。F0が大きい＝感情的、小さい＝自然、とは判定しない。最終的な良否はユーザー試聴。各候補1 TakeのためStyle差と生成ゆらぎを厳密に分離できない点も明記。

## 7. 非対象範囲・Production Gate
Standard Preview/Comment Style、英語KP TTS、Advanced、本文Full Story音声、KP日本語意味テキスト、日本語gloss再整合工程、Production runner/retry/fallback/regeneration、既存Coffee完成版上書き、いずれも変更しない。選定Promptを正式Production側へ配線しない。ユーザー正式採用までAPPROVED_FOR_PRODUCTIONにしない。Trial結果が良好でもPRODUCTION_WIREDとしない。既存仕様への参照についてDangling Reference Checkを行う。

## 8. STOP・報告
既存の予算・安全・運用STOP規則を守る。Trial終了時、REJECTED/VALIDATED/USER_DECISION_REQUIREDのいずれかで分類。ユーザー試聴前に正式な採用判定をしない。報告: 1.試聴ページURL 2.7候補の比較結果とFable推奨 3.P5との差(抑揚、感情、無音、自然さ) 4.日本語ASR照合結果 5.生成数・実費 6.既存Production・Coffee完成版が無変更である証拠 7.CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSへのTrial記録 8.ユーザー判断事項・未解決事項。FableはSonnet報告をそのまま採用せず実成果物・ログ・受入条件を照合。比較試聴ページを提出したところでSTOPし、ユーザーの採用判断を待つ。

## 9. 最重要事項
今回は新しい方向へ大きく変更するTrialではない。P5を基準に、抑揚と感情をほんの少しだけ足した、自然な日本語意味の読み上げを探す。P6・P7を中心候補とし、ニュースキャスター風・Podcastホスト風・音声ガイド風を比較対象として評価すること。Production採用はユーザー判断まで行わない。
