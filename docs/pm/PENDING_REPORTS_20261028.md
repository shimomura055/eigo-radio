# 再起動後に即時再掲する報告(2026-10-28、ユーザー指示: PC再起動後すぐ報告)

再掲順: (1) 月 ユーザー判断依頼 (2) 告げ口心臓Voice完了報告 (3) LR統一配線完了報告。各報告は★★★★報告ここから★★★★〜★★★★報告ここまで★★★★で囲む。内容は本ファイルの逐語を用いる(要約しない)。

---
## (1) FX-MOON-SHRINKING-RESELECT-REMAKE-01(月は少しずつ縮んでいる？ 再制作)ユーザー判断依頼(例外即時報告)

結論: Advancedは完成し候補ページで試聴できます。Standardは本文・学習項目の音声は完成しましたが、日本語タイトルの音声だけが完成していません。両level版の第2回報告の前に、1点の判断をお願いします。

問題と影響:
- Standardの日本語タイトル「月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密」は、今回の再制作でもTTS 3回(通常2回+Fallback 1回)すべてASR(音声認識による読み上げ照合)がNGでした。公開版(run_ms_03)でも同じ題が3回NGとなり、当時は2回目の音声をあなたが個別承認して採用しています(承認範囲は「この1区間・この音声のみ、ASR検査の一般免除ではない」)。
- 今回は音声を新規生成したため、その承認を自動では引き継げず、Standard の組立が安全停止しています。Gateは迂回していません。

選択肢:
- (a) 推奨: 公開版で承認済みの同一タイトル音声(文・音声とも承認時と同一、sha照合のうえ)を今回のStandardにそのまま再利用する。費用0円。承認記録を参照した再利用記録を残し、新規免除は作らない。
- (b) タイトル音声だけ再生成する(¥1〜3)。公開版でも3回NGだったため通る見込みは低い。
- (c) タイトル文を変える(承認済み内容の変更になるため、ご指定が必要)。

(a)は承認済み音声の再利用で承認範囲内と判断しましたが、承認記録の注入操作にあたるため、自動実行せずご判断を仰ぎます。回答後、Standard組立→両level候補ページ完成→検証→第2回報告(試聴URL・QA・費用)を行います。

現状: Advanced候補ページ https://shimomura055.github.io/eigo-radio/user_test/family_x_moon_shrinking_reselect_01/index.html (Standardは未掲載)。本文は不変、公開版 `family_x_moon_shrinking_02` は無変更。費用: run累計¥20.78(本委任分約¥15.5、Cap¥60内)。

必要なユーザー判断: (a)/(b)/(c)のいずれか。

---
## (2) FZ-TELL-TALE-HEART-NARRATOR-VOICE-01(USER_03 不具合調査・修正)完了報告

1. 真因
- Family Zの語り(Narrator)音声生成は、Family Xと共有する下位の生成関数に処理を渡しますが、その際に「Fenrir」というVoice指定を渡していませんでした。下位関数は固定値のAoedeでAPIへ送信していました。
- 計画記録・再利用キーにはFenrirと書かれていましたが、これは送信値ではなく記録値でした。生成試行記録の「voice: Aoede」は実送信値そのものでした。
- 同種の穴が2つありました。再開(resume)時の進捗照合にVoiceが含まれず別Voiceの旧結果を引き継げること、誤記録の「Fenrirキー・Aoede音声」が再利用されうることです。いずれも修正しました。

2. 修正内容
- 語りの生成呼出全体(retry・fallback・LR・減速後再検証を含む)を「指定Voiceで送信する」範囲で包み、API送信直前の設定と試行記録が同じ決定関数を使うようにしました。本作品以外(語り=Aoedeの他作品、X/A/B/C)は動作不変です。環境変数等でONにはできません。
- コスト記録に、APIへ渡す設定から読み取った「送信Voice」を独立記録する欄を追加しました。
- 計画Voice・送信記録・試行記録を1クリップずつ機械照合する受入ツールを新設しました(Gateには未接続)。
- Style・Prompt・回数・待機・ASR・速度は変えていません。

3. 検証証拠(Fableが独立に再確認)
- 送信記録: 語り全14クリップ(Std 7・Adv 7)で、計画=送信記録=試行記録=Fenrir。送信記録はAPIに渡す設定オブジェクトから読んでおり、コード上の決定点も追跡済みです。
- 実音声: 基本周波数の分布が、Aoede版2本(ほぼ同一分布)から明確に離れ、男声Fenrir参照の方向へ低下しています(下位10%値で約20Hz低下)。
- 老人(Algieba)・警官・学習項目など語り以外の40音声はハッシュ一致で不変、再生成なし。
- 候補ページは全再生OK、GitHub Pages上の音声ファイルがローカルと一致。公開版(reselect_01)は無変更。
- 既存回帰テストは全PASS。新規テスト11件PASS。

4. 試聴URL(Standard/Advanced同ページ)
https://shimomura055.github.io/eigo-radio/user_test/family_z_tell_tale_heart_fenrir_01/index.html

5. 追加費用: ¥24.86(本案件累計 約¥45、上限¥60内)。

6. 再発防止(実施済み)
- 受入判定の誤り: 前回のWorker検証は記録値のみで送信と実音声を見ておらず、Fableは矛盾する観測(試行記録のAoede)をコード追跡なしに「ラベル」と解釈しました。独立した送信記録も存在しませんでした。
- 対策: Voice/Style/話者/モデル変更の受入は「送信記録・実音声の客観指標・計画記録値」の3点一致を必須とし、矛盾する観測を解釈で処理する場合はコード追跡記録を必須にしました(PM_GOVERNANCE・CURRENT_SPECに反映、受入ツール新設)。

Status: PRODUCTION_WIRED(送信Voice修正)+ユーザー最終試聴待ち(PASS未取得、公開差替えなし)。SSOT同期・Git反映済み(commit a760a4689・1f2f980e2・f0a4da900・1e834896c)。

必要なユーザー判断:
- 上記URLで最終試聴(Std/Adv)。PASSなら公開版への差替えを実施します。
- 受入ツールをrunnerの正式Gateへ接続するか(Gate追加=仕様変更のため未実施。現状はFable受入手順として義務化のみ)。

https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/research/FZ-TELL-TALE-HEART-NARRATOR-VOICE-01/VOICE_DEFECT_FIX_01.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/OPEN_ITEMS.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/CURRENT_SPEC.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/DECISION_LOG.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/PM_GOVERNANCE.md

---
## (3) LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 完了報告(原文§12の10項目)

1. 結論: Local Rewrite(LR、英文の最小修正)とFallback(代替Style再生成)の横断仕様を正式Production経路に配線し、Fable受入でX/Y/Z × Standard/Advanced を PRODUCTION_WIRED と判定しました。既公開記事の差替えは未実施(記事単位でご承認待ち)。

2. 実装内容(UD-1/2/3+報告資料)
- UD-1: LR後の英文が表示本文・TTS入力・ASR正解原稿で一致する三者一致Gateを組立に追加。確定KP/KW/文法/Factとの重なり検査(T1〜T3)で保護。
- UD-2: AI島 Std「AIs→AI agents」/Adv「AIs→AI systems」をLR済み音声の再利用で反映(再TTSなし)。
- UD-3: 承認済みStyle照合は維持。正常なLR/Fallbackでは停止・Human Review要求を解除。未承認Style・記録欠落・ASR NG等は従来どおり停止。
- 報告資料=試聴ページ(全Family共通): 実Chunk境界の⏸、LR=赤(修正前後)、Fallback=濃い青+Style名。注記は試聴ページの注記欄のみで、制作本文・TTS・ASR・学習者本文には混入しません。A/B/Cは最終Human報告のみ(52件生成)。

3. 検証: 実走evidence 26本(X/Y/Z 各Std/Adv、LR・Fallback・両者同居・kill→resumeを含む)、保存run 295件の読取再評価で「旧PASS→新BLOCK」0件、関連テスト203件PASS、三者一致OK、注記混入0。
4. 検証中に見つけ修正した不具合(6件): 正常Fallbackが停止するもの2件(KP解説Style登録漏れ、Z会話代替経路の分類)、LRを含むChunkで⏸が欠落(X/Y/Z)、再開後のLR理由未記録、旧検査(赤青併存NG)の撤去、再利用音声のASR記録参照漏れ(月Std組立で実発生)。修正後に再実走で通過を確認。
5. Production Wiring状況: PRODUCTION_WIRED(X/Y/Z Std/Adv)。証拠上の未観測(不具合ではない): Y/Zのresume実走、Y本文Chunk・Y Std本文Fallback採用・Z旧会話経路・X Std本文ChunkのLR/Fallback実走、確定内容保護(条件4)の実走(unit+保存run台帳で担保)。
6. 既公開4件の是正状況(候補ページ、公開版は無変更)
- Word Gacha Adv: 差分1語(you've→you have、LR赤1) https://shimomura055.github.io/eigo-radio/user_test/family_x_word_gacha_01_candidate_b7_01/index.html
- 猿の手 Std: 差分1語(guest→visitor)+旧注記撤去 https://shimomura055.github.io/eigo-radio/user_test/family_z_monkeys_paw_01_candidate_b7_01/index.html
- AI島 Std/Adv(UD-2適用、初公開候補、LR赤各1・⏸各5) https://shimomura055.github.io/eigo-radio/user_test/family_x_ai_island_form_01_candidate_b7_01/index.html
- メロス_02: LR 0・不一致なし(是正不要)。告げ口心臓: 整合確認のみ。
7. 費用: 実走検証¥39.92+再実走¥1.97=¥41.89(配線・是正・SSOTはAPI 0)。
8. 撤去: 旧「Local Rewrite採用」注記表示、旧赤青併存NG検査。旧公開ページ2件の旧注記は差替え承認で解消。
9. 軽微な残件(OPEN-573〜576、実害なし/軽微): 候補ページのscan警告、X runner開発用playerの⏸旧規則、テスト環境汚染1件、Z旧テスト1件の失敗。
10. SSOT/Git: OPEN-569等・CURRENT_SPEC・DECISION_LOG・USER_DECISION_REGISTER #198〜#200 更新済み。commit 4475cebf8/641e1c81c/60f8d839c/88433ec82/369e89972/cc03a76a2。

必要なユーザー判断(記事単位):
- Word Gacha Adv を候補版へ差替えるか
- 猿の手 Std を候補版へ差替えるか
- AI島 UD-2適用版を初公開するか(試聴のうえ)

https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/B8_RUNTIME_EVIDENCE_01.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/B10_UD3_FIXES_01.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/OPEN_ITEMS.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/CURRENT_SPEC.md
