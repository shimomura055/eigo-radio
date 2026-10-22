# STAGE2_TRIAL_CLOSEOUT_01: 固有名詞発音 Stage 2 Trial 終了報告(ユーザー§7の1〜8順、2026-10-22、委任_10)

到達Status: `STAGE2_TRIAL_CLOSED_USER_DECISION_REQUIRED`(判定側方式=`REJECTED`、TTS入力側供給=Khaite型限定で`VALIDATED(条件付き)`、Production採用はユーザー判断=UDR #147)。費用: Trial累計JPY128.94/300、本Closeout JPY0(API 0)。Production/正式Ledger/HR queue/Store/Validator/Prompt無変更(`closeout/protect_closeout.json`: 実行前後sha256一致)。
証跡: `er100_output/pnps_stage2_trial_01/closeout/{prod_judge_replay.json,baseline_table.json,protect_closeout.json}`、`er100_pnps_stage2_trial_01_closeout_replay.py`(+`_closeout_agg.py`)、本文詳細=`STAGE2_TRIAL_RESULT_03.md` §7・§8。

## 0. 基準値の取り直し(本番判定器・M1込み)
方法: 保存済み転写(Primary/Azure)を本番関数`er006_secondary_asr_01.evaluate_attempt_with_cascade_detail`(m1_enabled既定ON、CS Equivalence層ON、最終slot ctx、Tier3用segment_id=full_story_part1)へそのまま入力。Ledger=tmp複製、HR log=tmp、research/供給fetch/transcribe/Azure STT/local ASRはstub。local ASR転写は保存が無いためunavailable扱い(CS Equivalenceのlocal corroborationのみ不在)。clip単位のcanonicalで判定(HR queue行もsegment/clip単位)。全件Secondary(Azure)転写あり=「Primary判定のみ」は0件。

| 区分 | 件数 | 備考 |
|---|---|---|
| 現行TTS 30 segment(take1) 本番判定 | PASS 4 / 警告付きPASS 3 / **HR 23** | Melos別掲 |
| うちMelosを除く22 segment | **HR 19**(Khaite 9/10, Toteme 3/4, Altuzarra 3/3, Meink 2/2, Canelé 2/2, Zabelina 0/1) | Zabelina=Azure正綴りでSECONDARY_CONFIRMED、Khaite s09/Toteme s11=Primary正綴り |
| Melos(8 segment、別掲) | HR 4 / 解消 4(うちM1受理2) | 解消=Mello/Melo said型。HR継続4=Mallo/Mellus/Mellow Strength等の別語聞き取り |
| take2(16 segment再生成) | HR 11(take1とも9一致、いずれか13) | TTSの揺れあり |
| 保存HR事象58 | 混入25(全Melos、M1で全て警告付きPASS)+実質33 | |
| 実質33のうち現行判定でHR | **29**(Melos 7 / Khaite 10 / Toteme 7 / Meink 2 / Canelé 2 / Zabelina 1)、distinct segment 28 | |
| M1配線前(〜2026-10-13) | 30事象→HR継続26(M1で解消4=全てMelos 10-12) | |
| M1配線後(10-14〜) | 3事象(全てMelos、10-15・10-19×2)、全てHR継続 | 非Melosの実質HR事象はいずれも9月(旧TTS世代) |

(ii) Khaite型(綴り置換→Kate、4エンジン全一致)で救える件数: Khaite HR segment 9のうち実測した3本(s12, s13, s16): s12・s16は両take PASS(**実測2**)、s13は1take PASS+1takeは「palm-sized→palm-size」の無関係差でNG(部分、ASR転写は両エンジンKate)。同型推定=未測定のKhaite HR 6本(s08,s14,s15,s20,s21,s22)。上限=実測2〜3+推定6=最大9(Melos除くHR 19の47%)、実測根拠のみなら2〜3(11〜16%)。

## 1〜8(ユーザー§7の順)
1. **結論**: 判定側の改善でHR削減は0〜2件(天井約24%、実測0%)。TTS入力側の綴り置換で削減できたのはKhaite型のみ(実測2〜3 segment)。Melosは『別綴り聞き取り型』のみM1で解消済み。
2. **語別・階層別**: Khaite(B階層Nylon 1媒体)は有効、Meink(A)・Altuzarra(B)は置換でも別の読み、Toteme/Zabelina/Canelé/Melosは供給元なしまたは対象外。(`STAGE2_TRIAL_RESULT_03.md` §2)
3. **誤読対照**: 誤供給6本は本番判定でも全てNG。ただし置換後テキストで比較する第3巡方式では誤供給がPASSになる(Meink→Mink)=安全性は供給発音の正しさに全面依存。
4. **供給不可語**: Toteme/Zabelina=取得できず、Canelé=辞書サイト1件のみ、Melos=同一人物の根拠なし。
5. **原因**: HR主因は判定ではなくTTSの実誤読(複数ASRが揃って別語を転写)。Meink/Altuzarraは綴り置換でも制御不能。
6. **費用**: Trial累計128.94円(15.54/63.55/49.85)、Closeout 0円。量産単価は不採用なら影響0。
7. **Fable独立評価**: 判定側=REJECTED、TTS入力側=Khaite型限定VALIDATED(条件付き)、Stage 2全体=USER_DECISION_REQUIRED。残る代替案はいずれも合理的な改善見込みが小さくSTOP。(`STAGE2_TRIAL_RESULT_03.md` §7)
8. **ユーザー判断(1件、UDR #147)**: 取得発音のTTS入力側供給(綴り置換)を新仕様として採用するか。(ア)現状維持(推奨)/(イ)A階層のみ自動供給+B階層は人承認登録。(同§8)

## 限界
(1) 転写は保存済みのみ、local ASR無し。(2) Meinkのclipはcanonicalに「U.S.」が含まれず、ASRが前置語(US/As/West等)を付けて不一致を増やす境界アーティファクトあり(Meink NGの全てが名前だけが原因とは限らない)。(3) Altuzarra R armの置換後綴りは、ASRが原綴りを書くため本番判定では不成立=本番判定のR arm評価はKhaite型にのみ妥当。(4) 負例30本のうち警告付きPASS 2(n_toteme_V, n_melos_F2)の音声の真の正否は断定しない。(5) 保存HR行は最終slotのprimary/secondaryペアを現行判定で再判定した推定(旧cascade世代の行を含む)。(6) 発音の正否は耳での確認が最終。
