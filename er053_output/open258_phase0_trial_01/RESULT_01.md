# RESULT_01 (OPEN-258-JA-SECONDARY-ASR-PHASE0-TRIAL-01 委任_01) 2026-10-11

Trial専用(Production未変更)。Phase 0限定。Phase 1実装・本番ONは未承認。
検証方式=V1(Primary TCM -> 既存除外 -> Azure Secondary 1回・Phrase Listなし -> EXACT/NORMALIZED一致のみPASS候補)。事前登録=`PREREGISTRATION_01.md`(Azure実行前に確定)。
使用: Azure Speech STT(region japanwest、Speech SDK 1.50.0、ja-JP、continuous recognition、Phrase Listなし)、補助=faster-whisper small/medium(ローカル、課金0)。Primary=既存ログのgpt-4o-mini-transcribe(再実行なし)。新規LLM/TTS/記事生成なし。
証跡: `results_01.jsonl`(Azure認識全文・判定根拠・差分・秒数・遅延・費用、25行)、`manifest_all_candidates_01.json`/`manifest_selected_01.json`、`whisper_aux_01.json`、`summary_01.txt`、各script。

## 重要な前提訂正(設計書との差)
設計書の「原稿」は『後で合格したattemptのASR文字列(proxy)』だったが、本Trialは`attempt_history.jsonl`/lock stateの`canonical_text_sha256`とsha256一致する**確定原稿**を使用。結果、proxyが原稿でない例が判明(g23: 原稿=焙煎前、proxy=倍線前。g18: 原稿=拒絶、proxy=話し声より大きく感じられる)。設計書の14群は維持して集計し、proxyでは非救済扱いだったg18/g1を別枠で記載。

## (1) 出演/出現 3音声(META a2 japanese_title、原稿「AIの電話に人間が出演。問題は「キャスト変更」のお知らせでした」)
| attempt | Primary | Azure Secondary転写(逐語) | 判定 | 根拠 | whisper small/medium(補助) |
|---|---|---|---|---|---|
| 1 | …人間が出現。問題は、キャスト変更… | AIの電話に人間が出演。問題はキャスト変更のお知らせでした。 | NORMALIZED_MATCH=PASS候補 | 句読点・「」除去のnormalize後に一致 | 出面/出面(不一致) |
| 2 | 同上 | 同上 | NORMALIZED_MATCH=PASS候補 | 同上 | 出演/出演(一致) |
| 3(fallback) | …出現、… | 同上 | NORMALIZED_MATCH=PASS候補 | 同上 | 出演/出演(一致) |
3/3救済可。V1ならattempt1でPASSし、再生成2回(実測123/122秒)とSTOPPEDを回避できた。attempt1はwhisper 2モデルが「出面」と聞いたが、Azureは出演(ユーザー試聴も出演)=whisper 2-of-3を正式条件にするとattempt1は救えない(attempt2で救済)。

## (2) 14群(設計書V1の救済候補)の結果(確定原稿で再判定)
| 結果 | 件数 | 群(設計書index) |
|---|---|---|
| 救済成功(Secondary NORMALIZED_MATCH) | 7 | g8 熟すと出るガス / g11 理屈の上では(a1) / g17 / g20 / g27 / g31 / g33(2 attempt) |
| 救済失敗(Secondary NG) | 6 | g2(「においを出す」vs「匂いを出す」PHONETIC_MATCH)、g21(コーヒー長文: 表れる/現れる・ふまえ/踏まえの表記差のみ、PHONETIC_MATCH)、g23(焙煎前を「焙煎米」とAzureも誤認識=TCM)、g36(あと/後の表記差のみ、PHONETIC_MATCH)、g24=g21と同一音声、g26=g23と同一音声(sha同一) |
| 既存除外で呼ばれず(救済漏れ) | 1 | g7 湿度(Primary「死図塔」。全体類似度<0.4で既存除外。プローブではAzure「湿度」=PASS) |
| 音声欠落 | 0 | 全音声が保存済み |
| 誤PASS(C群=TTS誤り代理) | **0/5音声** | g12 縛られず→Azure「縛られる」NG、g3 体内時計→「体内どこ」NG、g4 証拠だと→「証拠が?と」NG、g5 名所を…旅程→「名称を中心にした料亭」NG、g6 形になり始める→「形に始める」NG |
設計書外の追加PASS: g18(3 attempt中a2/a3、原稿=拒絶。Primary「強制」、Azure「拒絶されたように感じる」PASS)、g1(a1、Primary「活動をし続ける」、Azure「活動し続ける」PASS)。
Secondary PASS=合計 META3 + 14群内7群(8 audio)+g18 2 + g1 1 + probe g7。
Azureが原稿以外に厳格NGにしたC群: 5/5=100%(標本小)。
PHONETIC_MATCH(表記差のみ・読み一致)をPASSに含める案を採った場合: g2/g21/g36が救済に加わり計10/14群。C群はすべてTRUE_CONTENT_MISMATCHでPHONETIC該当なし=この標本では誤PASS増なし(ただし設計書の厳格化方針=新規仕様判断、ユーザー判断事項)。

## (3) 除外条件の妥当性(既存ルールのみ vs 設計書の追加除外あり)
- 既存除外(数字/否定/ratio<0.4/echo): 救済漏れ=g7(湿度、短いkey phraseで文字重複が0のため<0.4。Azure転写は原稿と一致、whisper small一致)。除外しなかった場合の誤PASS=0。ratio<0.4は「TTS異常(echo等)」目的だが、1〜3文字の短いkey phraseでは正しい発音でも類似度が0になり得て救済を妨げる(要観察)。
- 設計書の追加除外(Phase1候補の新規小ルール): (a)単独格助詞replace除外(だ->が含む)は該当=g4のみ(C群、Azureは元々NG)。救済漏れ0・誤PASS防止の実測効果も0(Azureが既にNG)。(b)漢数字/年月日除外は**g27(「いったん吐」vs「一旦履」、救済成功群)を誤って除外**(「一旦」の「一」を数字と誤判定)=安全性の効果が観測されず救済漏れ1(成功7->6)。このままの実装は不適。
- 結論: 本標本では追加除外ルールが無くても誤PASS 0。追加ルールの採用判断はユーザー(新規ルール)。特に漢数字ルールは粗すぎるため要見直し(例: 数詞+助数詞に限定)。

## (4) 誤PASS残余リスク
- 実測0/5(C群)だが標本小。サンプル0件でも将来0ではない。構造リスク: Secondaryが原稿寄りに丸める(本Trialではg12 ずる/縛られる等を丸めず原文どおり転写)、Primary/Secondary同一誤聴(Muse型、SCGでは救えず従来再生成のまま=悪化しない)。
- **要試聴(Azure PASSだがwhisperまたはPrimaryと不一致、真のground truthは試聴のみ)**: g11 a1(Primary肉/whisper small肉術 vs medium・Azure 理屈)、g18 a2・a3(Primary強制/small強絶 vs medium・Azure 拒絶)、g1 a1(Primary活動をし続ける/small同 vs medium・Azure 活動し続ける)、g27(medium「文」)、META a1(whisper 出面)。パス: g18=`er014_output/four_type_observation_01/discovery/audio/a2/narration/attempts/meaning_2_attempt2_standard.wav`(+attempt3)、g1=`er011_output/discovery_generalization_towels_trial_11/a2/narration/attempts/meaning_4_attempt1_standard.wav`、g27=`er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_02/b1b/narration/attempts/kp1_ja_charon_attempt1_standard.wav`、g11=`er012_output/editorial_b_family_voices_a2_production_wiring_01/kp_fix_01/a2/narration/attempts/kp5_ja_aoede_attempt1_standard.wav`、g7(probe)=`er011_output/household_unified_final_candidate_01/a2/narration/attempts/meaning_4_attempt1_standard.wav`。これらはC群ではないため「誤PASS検出」には数えていない(ground truth不明)。試聴で誤りと判明すれば誤PASS=STOP条件。
- whisper補助(正式条件にしない): Azure PASSのうちwhisper small・medium両方が原稿と一致=9音声(META a2/a3、g8、g17、g20、g31、g33x2、g7)。片方のみ=g27、g11a1、g18x2、g1(Azureと食い違い=試聴要)。逆にAzure NGでwhisper両方一致=g2/g11a2(Azureが「理屈の上で」と助詞脱落)/g21/g23/g36 = Azure厳格判定は保守側(見逃し=従来再生成へ戻るだけ)。

## (5) 再生成回数・待ち時間・費用
- 救済成功群の削減再生成(n_attempts - 救済attempt): g8 1、g11 3、g17 1、g20 1、g27 1、g31 1、g33 2=**10回**(14群内)。META 2回(+STOPPED 1回回避)。合計12回。BATCH再生成は1回120〜170秒(META実測172/123/122秒)=約24〜34分短縮(META分約4分含む)。
- Secondary実測遅延: 25回 合計34.1秒、1回平均1.4秒(0.5〜2.0秒、長文19秒音声のみ7.5秒)。再生成1回(120〜170秒)の1/80程度。
- 費用: 25回・音声90.2秒、登録単価$1/h x 160円/USD=0.0444円/秒で**約4.01円**(各回秒切上げの保守見積4.58円)。1回平均約0.16円。回避した再生成の費用(Gemini TTS+Primary ASR約0.1円/回)x12=約1.2円。標本では純増約2.8〜3.4円/25呼出(成功は約8/25のため、NGに終わったSecondaryが費用の主因)。設計書推定(履歴全体約11円)と整合し、課金額としては小さい。Azure実請求は未確認(無料枠の可能性あり)。
- Secondary NGは従来の再生成/STOP維持(待ち時間は+約1.4秒のみ)。

## (6) Production実装時の影響範囲とリスク(実装は未実施・未承認)
- 変更ファイル/箇所(最小): `er007_ja_secondary_asr_01.py` `evaluate_attempt_ja_with_cascade_detail`(L104〜)の早期return(L128 `if cls.should_pass or not cascade_enabled or not is_entity_like_mismatch_ja(cls): return result`)の直前にTRUE_CONTENT_MISMATCH専用ブロック(約40〜60行)。呼び出し元`er003_v1_repro01_main_generate.py` L363 `evaluate_attempt_ja_with_cascade`(drop-in戻り値)は無変更。除外判定ヘルパーは`er007_ja_asr_validator_01.py`(任意)。test: `er007_ja_secondary_asr_01_test.py`にmock追加。FEATURE_FLAGで既定OFF可能。
- 整合: attempt上限(`PRODUCTION_MAX_TTS_ATTEMPTS=3` `er011_human_review_lock_01.py` L80)・fallback voice・Human Review lock・budget guardは無変更(SCGはattemptを消費しない)。Secondary NG/取得不能は従来の再生成。ASR_VALIDATION_UNCERTAIN経路は無変更。Local Rewrite(`er020_*`、英語TTS role専用)に非干渉。
- Dangling Reference Check: Trial scriptは`er053_output/open258_phase0_trial_01/`内のみ。Production(`*.py`、SSOT実装)からの参照は0(grep確認)、Productionコード変更なし。
- リスク: 誤PASS(上記)、PASS条件の仕様判断(PHONETIC_MATCHを含めるか)、ratio<0.4除外の短文での過剰除外、漢数字除外ルールの粗さ、Azure quota/請求未確認、Phase0標本が小さい。**Production実装は新しい処理フロー(Opus条件A該当見込み)**で、Phase 1前にOpus独立レビューが必要(Fable判断)。

## (7) 実測費用
Azure STT 25回・90.2秒 = 約4.01円(切上げ保守4.58円)。上限5円内。他の課金API(TTS/LLM/Primary ASR)0。whisperはローカル。

## (8) Status分類案(Phase 0限定)
**案: VALIDATED_PHASE0(条件付き)かつ Phase 1可否は USER_DECISION_REQUIRED**。根拠=META 3/3救済、14群で7/14成功(+g18/g1)、誤PASS 0/5(C群)、再生成10+2回削減。ただし標本が小さく、要試聴5音声の確認が未了=誤PASS率の確定ではない。REJECTED条件(誤PASS検出)には該当せず。
ユーザー判断事項: (i)要試聴音声の確認(誤PASSの最終判定)、(ii)PHONETIC_MATCHをSCG-PASSに含めるか(含めると+3群)、(iii)追加除外ルール(助詞/漢数字)の採否と漢数字ルールの見直し、(iv)短文でのratio<0.4除外の扱い、(v)whisper 2-of-3の採否(本標本ではMETA a1を救えないため非推奨寄り)、(vi)Phase 1(Production実装、Opus独立レビュー要見込み)に進むか。
