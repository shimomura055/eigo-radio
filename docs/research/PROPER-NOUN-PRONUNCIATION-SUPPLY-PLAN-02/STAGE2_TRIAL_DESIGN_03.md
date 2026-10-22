# STAGE2_TRIAL_DESIGN_03: Stage 2 Trial 第3巡(TTS入力側の読み制御)設計

管理ID: PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_09 / 2026-10-22 / Opus OF-PNPS-S2R-10(1)の実行(Step B済み、追加レビュー不要)。到達Status上限=`TRIAL_R3_DONE_PENDING_FABLE`。

## 目的と仮説
第2巡で、HRプロキシ25の主因はTTSの実誤読(18/25)と判明。判定側を改善してもHRは減らない。取得済み(公式/実使用)発音をTTS入力側で制御し、HRを「発生させない」方式の効果と安全性をTrial内で測る。

## 供給候補(0円、第1巡 `o1_free_sources.json`/`r0_extractions.json`の再照合)
| 語 | 取得した読み | 出典 | 階層 | 引用実在確認 | 供給可否 |
|---|---|---|---|---|---|
| Meink | MEENK(/miːnk/) | en.wikipedia.org/wiki/Troy_Meink 本人記事 | A相当 | 第1巡extraction(原文context保存、sha256付)で確認 | 供給可(A) |
| Khaite | "kate" | nylon.com ファッション発音ガイド 1媒体 | B | 同上(quoted_word、contextにKhaite直後) | 供給可(B。ユーザー未承認の扱い=Trial内比較のみ) |
| Altuzarra | ahl-too-ZAH-rah | businessinsider/nylon/elle.com.au/herworld ほか(5件一致) | B | 同上 | 供給可(B) |
| Canele | /kænəˈleɪ/(辞書サイト1件) | youpronounce.it | B未満 | 弱い | 供給しない(HR維持) |
| Toteme / Zabelina / Melos | 取得なし(Melosは同定未確認) | - | - | - | **供給しない**(ESTIMATED供給禁止 v4-5) |

## arm
- **N(無供給対照)**: 第2巡r2のtake1/take2同一segment音声を再利用(追加生成なし)。alt_short(Altuzarra専用の短文)のみ新規2本。
- **R(綴り置換、Reicher→Riker方式)**: TTS入力の対象語のみを置換(Khaite→Kate、Meink→Meenk、Altuzarra→Altoozahra)。判定は (a)置換後テキストで比較(既存方式に忠実)、(b)原綴りで比較(N5_UND/R1_EXT)の両方。
- **H(発音ヒント注入)**: 本文は原綴りのまま、styleへ`- "Khaite" is pronounced approximately "kate".`を追記(既存`er006_pronunciation_tts_injection_01`の注入形式を読取のみ利用。Ledger読取なし)。判定は原綴り比較。
- **誤読対照(wrong供給)**: 各語1本×{R,H}。Khaite→Kite、Meink→Mink、Altuzarra→Altuzairah(R)/al-tuh-ZAIR-ah(H)。置換後比較でPASSになる=方式の安全性は供給発音の正しさに全面依存、を明示。

## 構成
- 実本文segment: Khaite s09/s12/s13/s16、Meink s02/s03、Altuzarra s17(Toteme同居)+alt_short。各 {R,H}×2 take=32 + 対照6 + alt_short無供給2 = **40音声**。
- TTS設定は第2巡と同一(gemini-3.8-flash-lite-tts・Aoede・PD06、Production設定を読取のみ)。生成は`er100_pnps_stage2_trial_01_r3_gen.py`(r2_genの`process()`を再利用、台帳を`r3/paid_calls.jsonl`へ分離)。Store/HR queue/attempt_history非書込をsha256+行数でassert。
- ASR: OpenAI/Azureは対象文の窓、Whisper small/mediumは全体(第2巡と同じ)。

## 合格基準
(1) Production/正式Ledger/HR queue/Store無変更(assert)。(2) 誤読対照: 置換後比較でPASS化するか否かを記録(PASS化=方式の限界の事実)。(3) A階層供給でPASS化した件数・B階層でPASS化した件数を語別・arm別に記録。(4) 7語全体のHR削減率(供給不可語は削減0)。効果の閾値は事前に新設しない(第2巡の40%基準を参考に併記)。

## 見積/Guardrail
約40音声×約0.85円(第2巡実測: TTS約0.46+ASR窓約0.37)≒34円。Guardrail JPY60(本巡台帳が52円に達したら新規有料呼出を止める)。Trial累計79.09→+本巡/300。当日既使用約749.6→+本巡(≤1,000、超過見込みなし)。LLM呼出0。

## 開始前チェック(22節/STOP)
`stop_scope_check_01.py --managed-id PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02` rc=0(`r3_stop_check_start.json`、`r3/stop_check_gen.json`)。有料runは1回のみ起動(再起動なし)。
