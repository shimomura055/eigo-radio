# STAGE2_TRIAL_DESIGN_02: 固有名詞発音 Stage 2 Trial 第2巡(Opus Step B 案1)設計・開始前チェック

管理ID: PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_08 / 2026-10-22 / 性質: Trial(Trial専用経路。Production・正式Ledger・HR queue・Master Audio Store・Validator・Prompt・モデル構成 無変更) / 到達Status: `TRIAL_R2_DONE_PENDING_FABLE`
ユーザー原文: `docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_STAGE2-TRIAL-GO_USER.md`。第1巡設計=`STAGE2_TRIAL_DESIGN_01.md`。Opusレビュー(Step B)=`OPUS_REVIEW_STAGE2_STEPB_01.md`(要旨)。

## 1. 開始前チェック(ユーザー§2〜§7+委任_08の要求と、満たす場所)
| 要求 | 本設計での満たし方 | 成果物 |
|---|---|---|
| 最終目的=正しい音声を安全に自動合格させHRを実際に削減。初回が小さくても終了しない(§4) | 第1巡の主因(受理集合が空×ASR綴り経由の直列)を同時に扱う第2巡。HR削減を「現行TTS実測」と「保存データ」に分けて報告 | RESULT_02 §1 |
| S2R-01/02 現行TTSでの再測定(30 segment、「Melos said.」含む)、Family別の現行voice/style | 全30本文をTTSクライアント関数直接呼出し(Production runner/Store/HR queue/attempt_history非経由)。設定値は`er019_family_x_style_profile_01.PD06_TEXT`(FULL_STORY現行profile)+Aoede+gemini-3.8-flash-lite-tts(`r2/plan.json`のtts_settings、sha256記録)。第1巡P2はCharon+旧FAMILY_X style(誤り)だったため置換 | `er100_..._r2_gen.py` `r2/plan.json` |
| S2R-02(a)(b) 0円の事実確認 | HR queue 87〜113行の内訳、承認再利用機構のコード確認、run種別の分類 | RESULT_02 §付録 |
| S2R-03 縮約(degemination)arm | N1。次語頭の音素と候補末尾が同一子音のときのみ末尾子音を省いた候補も許容。負例に「Melo said.」を追加(縮約と真の脱落が音響上区別できるかを検証) | `r2_arms.py` |
| S2R-04 弱化母音同一視・2出所支持 | N2(ASR側が無強勢[CMU stress 0]かつ両者が弱化クラス{AH,IH,UH,ER,OW,AA}のとき同一視。子音と強勢母音は厳密)。N3(E2/E3/取得の2出所以上が弱化母音同一視下で支持する候補を受理集合へ。E3b=Luna N-best≤3追加推定。取得根拠[許可リストA/媒体合意]がある語は推定を捨てる) | `r2_arms.py` `r2_est.py` |
| S2R-05 ASR側OOV→G2P+アクセント正規化 | N4。CMU未収録のASR語をg2p_enで音素化(長さ4字未満/母音字なしの断片は対象外=「kt」→K EY Tの捏造を防ぐ。test済) | 同上 |
| S2R-06 Primary正綴りの扱い(事実測定) | 全arm共通でPrimary単独のEXACTはPASS根拠に数えない(音素照合MATCHが少なくとも1つ必要)。確認済み誤読負例のうちPrimaryが正しい綴りを返した割合を記録 | `agg.json` |
| S2R-07 母音1つ差=判定不能 | N5。母音1つ差のみの不一致は、独立2エンジン以上が同一綴りを返さない限りNGでなく判定不能(HR件数は不変)。Khaite「kite」はNG維持 | `r2_arms.py` `r2_test_01.py` |
| S2R-08 official無視 | どの関数もLLMのofficialを読まない。unit test(AST走査+フラグ反転で受理集合不変) | `r2_test_01.py` |
| S2R-09 負例拡充≥28本 | 7語×{C子音置換,V強勢母音置換,S音節/語頭脱落,F語末子音脱落}=28本+縮約文脈2本=30本。2エンジン以上の逸脱で誤読確認、確認できないものは負例から除外(除外分は別表)。0/n でも95%上限(ルール・オブ・スリー 3/n)を開示 | `r2_gen.py` |
| S2R-10 TTS側置換・音素CTC | 本巡で実装しない。`tts_safe_name_pronunciation_en`の配線のみGrep記録(RESULT_02) | RESULT_02 |
| 費用 Guardrail JPY80(日次残314、Trial累計Cap300残) | 単価出典を`paid_calls.jsonl`に記録。見積は下記§3。ガード75円で新規有料呼出停止 | `r2/paid_calls.jsonl` |
| STOP/Production安全 | `stop_scope_check_01`(rc=0)。生成phase前後でHR queue/attempt_history/Store manifest/telemetry のsha256・行数が不変であることをassert | `r2/protect_{before,after}_*.json` |

## 2. arm定義(Trial内比較のみ。承認済みの自動PASS条件は変更しない)
R1_V4/R1_EXT(第1巡基準)→ N1_DEGEM → N2_WEAK → N3_SUP2 → N4_ASRG2P → N5_UND → N6_W2(ローカルWhisper small/medium追加要件。Production外エンジンの比較用)。判定は全armで「Production系ASR(Primary・Azure)のうち全て MATCH/EXACT かつ少なくとも1つが音素照合MATCH」でPASS_WITH_WARNING、MISMATCHでNG、それ以外は判定不能(HR維持)。PASS_WITH_WARNINGは機械検出の通過であり正解の保証ではない(耳確認が必要)。
合格基準(Opus案1): ハード=確認済み負例のPASS 0、Khaite「kite」8事象NG維持、Production/正式Ledger/HR queue/Store無変更。効果=現行TTSでHR(プロキシ)になる独立segmentの40%以上がPASS_WITH_WARNINGへ。

## 3. 費用見積(実測単価)と方法の変更点
第1巡の実測0.65円/本は短文(約7秒)での値。実本文30 segment(平均約500字、約35秒)を全長でTTS+OpenAI+Azureにかけると、概算でTTS約55円+Azure約100円+OpenAI約35円(2本分)で、Guardrail80円を超える。このため(1)OpenAI/Azure ASRは対象語を含む文だけの窓(Whisper medium単語時刻とcanonicalのdifflib整列で切り出し、12秒以下の音声は全体)へ送る、(2)take2は短文・Melos・予算に応じて優先選択、とした(限界として開示: ASRの文脈が全segmentより短い)。ローカルWhisperは全音声を0円で転写。
