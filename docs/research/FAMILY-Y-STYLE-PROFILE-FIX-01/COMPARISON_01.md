# COMPARISON_01 — 修正前(`_02`版)と修正後(run_style_fix_01)の比較

管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_02。到達Status=**Adv完了(Gate PASS)・Std 2 segmentがHR待ち(HUMAN_REVIEW_LOCKED)で未完成**。公開`_03`は未作成(Stdが組み立てられないため)。
前提: 旧=`run_voice_puck_ev_01`(Puck=Voice 1、承認Style未適用[default])、新=`run_style_fix_01`(承認profile fx_20261017適用、同じ入力・同じVoice 1=Puck/2=Zephyr/3=Schedar・Adv Comment 2削除維持)。
Opus M-3: Voice 1〜3(Std/Adv 6 segment)の聞こえ方(S9)は**未評価・ユーザー判断項目**。この比較は『Style値の事実』『長さ・話速』『品質Gate結果』で、聞こえ方の良否は含まない。

## 1. 部位別Style 前後表(全segment。旧=run_voice_puck_ev_01[`_02`版]、新=run_style_fix_01)
| level | segment | 旧Style | 新Style | Voice(新) | 新status/TTS回数 | 区分 |
|---|---|---|---|---|---|---|
| Std | comment_1 | 旧default(日本語)[ae68e3e6/65] | S3[060c08fd/199] | Aoede | OK/1 | Style変更→再生成 |
| Std | comment_2 | 旧default(日本語)[ae68e3e6/65] | S3[060c08fd/199] | Aoede | OK/1 | Style変更→再生成 |
| Std | comment_3 | 旧default(日本語)[ae68e3e6/65] | S3[060c08fd/199] | Aoede | OK/1 | Style変更→再生成 |
| Std | japanese_title | 旧default(日本語)[ae68e3e6/65] | 旧default(日本語)[ae68e3e6/65] | Aoede | OK/1 | Style不変(案Rで再生成) |
| Std | kp1_english | 旧default(KP英語)[2b0c7505/1076] | K2[9d905cfe/332] | Aoede | OK/1 | Style変更→再生成 |
| Std | kp1_japanese_meaning | 旧default(日本語)[ae68e3e6/65] | P8-KP[b12c8721/93] | Aoede | OK/1 | Style変更→再生成 |
| Std | kp2_english | 旧default(KP英語)[2b0c7505/1076] | K2[9d905cfe/332] | Aoede | OK/1 | Style変更→再生成 |
| Std | kp2_japanese_meaning | 旧default(日本語)[ae68e3e6/65] | P8-KP[b12c8721/93] | Aoede | OK/1 | Style変更→再生成 |
| Std | kp3_english | 旧default(KP英語)[2b0c7505/1076] | K2[9d905cfe/332] | Aoede | OK/1 | Style変更→再生成 |
| Std | kp3_japanese_meaning | 旧default(日本語)[ae68e3e6/65] | P8-KP[b12c8721/93] | Aoede | OK/1 | Style変更→再生成 |
| Std | preview | - | - | - | HUMAN_REVIEW_LOCKED/2 | **HR待ち(HUMAN_REVIEW_LOCKED)** |
| Std | topic_intro | 基底(Topic intro)[d16e099c/96] | 基底(Topic intro)[d16e099c/96] | Aoede | OK/1 | Style不変(案Rで再生成) |
| Std | y_closing | 旧default(Std本文+減速指示)[9293e0c3/272] | PD06[3a680861/177] | Aoede | OK/1 | Style変更→再生成 |
| Std | y_intro_1 | 旧default(Std本文+減速指示)[9293e0c3/272] | PD06[3a680861/177] | Aoede | OK/1 | Style変更→再生成 |
| Std | y_intro_2 | 旧default(Std本文+減速指示)[9293e0c3/272] | PD06[3a680861/177] | Aoede | OK/1 | Style変更→再生成 |
| Std | y_intro_3 | 旧default(Std本文+減速指示)[9293e0c3/272] | PD06[3a680861/177] | Aoede | OK/1 | Style変更→再生成 |
| Std | y_lead | 旧default(Std本文+減速指示)[9293e0c3/272] | PD06[3a680861/177] | Aoede | OK/1 | Style変更→再生成 |
| Std | y_voice_1 | 旧default(Std本文+減速指示)[9293e0c3/272] | - | - | HUMAN_REVIEW_LOCKED/2 | **HR待ち(HUMAN_REVIEW_LOCKED)** |
| Std | y_voice_2 | 旧default(Std本文+減速指示)[9293e0c3/272] | PD06[3a680861/177] | Zephyr | OK/2 | Style変更→再生成 |
| Std | y_voice_3 | 旧default(Std本文+減速指示)[9293e0c3/272] | PD06[3a680861/177] | Schedar | OK/1 | Style変更→再生成 |
| Adv | comment_1 | 基底(Adv英語)[57c3fda6/20] | 基底(Adv英語)[57c3fda6/20] | Charon | OK/1 | Style不変(案Rで再生成) |
| Adv | comment_3 | 基底(Adv英語)[57c3fda6/20] | 基底(Adv英語)[57c3fda6/20] | Charon | OK/1 | Style不変(案Rで再生成) |
| Adv | kp1_english | 旧default(KP英語)[2b0c7505/1076] | K2[9d905cfe/332] | Aoede | OK/1 | Style変更→再生成 |
| Adv | kp1_explanation | 旧default(KP解説)[f44ef4e2/52] | P7[05180006/136] | Aoede | OK/1 | Style変更→再生成 |
| Adv | kp2_english | 旧default(KP英語)[2b0c7505/1076] | K2[9d905cfe/332] | Aoede | OK/1 | Style変更→再生成 |
| Adv | kp2_explanation | 旧default(KP解説)[f44ef4e2/52] | P7[05180006/136] | Aoede | OK/1 | Style変更→再生成 |
| Adv | kp3_english | 旧default(KP英語)[2b0c7505/1076] | K2[9d905cfe/332] | Aoede | OK/1 | Style変更→再生成 |
| Adv | kp3_explanation | 旧default(KP解説)[f44ef4e2/52] | P7[05180006/136] | Aoede | OK/1 | Style変更→再生成 |
| Adv | preview | 基底(Adv英語)[57c3fda6/20] | E1[8862317f/68] | Charon | OK/1 | Style変更→再生成 |
| Adv | topic_intro | 基底(Topic intro)[d16e099c/96] | 基底(Topic intro)[d16e099c/96] | Charon | OK/1 | Style不変(案Rで再生成) |
| Adv | y_closing | 旧default(Adv本文)[07d72dd6/88] | PD06[3a680861/177] | Aoede | OK/1 | Style変更→再生成 |
| Adv | y_intro_1 | 旧default(Adv本文)[07d72dd6/88] | PD06[3a680861/177] | Aoede | OK/1 | Style変更→再生成 |
| Adv | y_intro_2 | 旧default(Adv本文)[07d72dd6/88] | PD06[3a680861/177] | Aoede | OK/1 | Style変更→再生成 |
| Adv | y_intro_3 | 旧default(Adv本文)[07d72dd6/88] | PD06[3a680861/177] | Aoede | OK/1 | Style変更→再生成 |
| Adv | y_lead | 旧default(Adv本文)[07d72dd6/88] | PD06[3a680861/177] | Aoede | OK/1 | Style変更→再生成 |
| Adv | y_voice_1 | 旧default(Adv本文)[07d72dd6/88] | PD06[3a680861/177] | Puck | OK/1 | Style変更→再生成 |
| Adv | y_voice_2 | 旧default(Adv本文)[07d72dd6/88] | PD06[3a680861/177] | Zephyr | OK/1 | Style変更→再生成 |
| Adv | y_voice_3 | 旧default(Adv本文)[07d72dd6/88] | PD06[3a680861/177] | Schedar | OK/1 | Style変更→再生成 |

## 2. 話速WPM前後表(R-1。語数÷narration wav秒数×60。Stdは生成後6%減速込み。**Std Voice 1の新はHR待ちfallback候補wav[未採用・未減速]のため参考外**)
| level | segment | 語数 | 旧秒 | 新秒 | 旧WPM | 新WPM |
|---|---|---|---|---|---|---|
| Adv | y_lead | 67 | 21.52 | 20.64 | 186.8 | 194.8 |
| Adv | y_intro_1 | 15 | 5.88 | 5.75 | 153.1 | 156.5 |
| Adv | y_voice_1 | 133 | 39.52 | 40.31 | 201.9 | 198.0 |
| Adv | y_intro_2 | 19 | 6.81 | 6.71 | 167.4 | 169.9 |
| Adv | y_voice_2 | 156 | 45.84 | 50.59 | 204.2 | 185.0 |
| Adv | y_intro_3 | 21 | 8.72 | 7.12 | 144.5 | 177.0 |
| Adv | y_voice_3 | 158 | 49.84 | 47.88 | 190.2 | 198.0 |
| Adv | y_closing | 124 | 37.56 | 35.64 | 198.1 | 208.8 |
| Std | y_lead | 62 | 22.34 | 21.56 | 166.5 | 172.5 |
| Std | y_intro_1 | 11 | 4.69 | 4.44 | 140.6 | 148.7 |
| Std | y_voice_1 | 121 | 41.7 | 34.88 (参考外:HR待ち) | 174.1 | 208.1 |
| Std | y_intro_2 | 18 | 6.99 | 5.99 | 154.4 | 180.2 |
| Std | y_voice_2 | 157 | 51.58 | 49.89 | 182.6 | 188.8 |
| Std | y_intro_3 | 18 | 7.62 | 7.19 | 141.8 | 150.3 |
| Std | y_voice_3 | 156 | 52.41 | 51.28 | 178.6 | 182.5 |
| Std | y_closing | 124 | 41.45 | 39.49 | 179.5 | 188.4 |

## 3. 品質(ASR・Gate・HR待ち。R-4)
| 項目 | Adv(b1b) | Std(a2) |
|---|---|---|
| Gate結果 | **PASS**(検査15件/期待15件、不足0・期待外0、照合表15行すべて一致) | **BLOCK**(検査18件/期待18件。違反は下記2 segmentのみ) |
| Gemini TTS呼出(cost_log実測) | 18回=全て1 segment 1回(retry 0。Puck×PD06含む) | 25回(通過した各segmentは1回、y_voice_2のみ2回、y_voice_1とpreviewは各3回[上限] ) |
| HR待ち | 0件 | **2件**: `y_voice_1`(Puck×PD06逐語)、`preview`(日本語S3) |
| fallback使用 | 0 | 2件(上記。いずれもHUMAN_REVIEW_LOCKED) |
| Local Rewrite | 0 | 0 |
HR待ち2件の原因(ASR判定の表記ゆれ。音声内容の欠落ではない。`REGEN_RESULT_01.md` §3):
- Std y_voice_1: 標準2回+fallback1回とも `NG_BOTH`(`secondary_not_accepted`)。ASRが「re-deliveries」(ハイフン付き)と転写、Azureは句読点位置が異なる転写。本文語句は一致。
- Std preview: 3回とも `NG_BOTH`。ASRが「思い通り」(漢字)と転写、正規本文は「思いどおり」。読みは同じ。
- 旧`run_01`でも同2 segmentはHR(ユーザー承認)を要した(承認はAlgieba/default音声に紐づくため新音声へ流用不可=OPEN-535)。
- Opus R-4の予測どおり、承認Styleの有効化でStd fallback規則が効き、HR待ちが顕在化した(件数: Adv 0 / Std 2)。

## 4. 費用(実測。COST_01.md)
合計 **30.79円**(Gemini 16.43 / OpenAI ASR 4.33 / Azure 10.03)。Adv 7.84円、Std 22.95円(Std y_voice_1・preview・y_voice_2のretryと180秒cooldown込みの3回cascade)。見積25〜45円・Cap60円の範囲内。
