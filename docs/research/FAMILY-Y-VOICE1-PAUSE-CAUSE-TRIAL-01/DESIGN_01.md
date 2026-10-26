# DESIGN_01 — FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01(生成前に固定。観測後に基準を変えない)

作成: 2026-10-26(生成開始前)。Trial専用。Production(Voice・Style・選別方式)は変更しない。run_01配下は読取のみ。

## 1. 比較単位と条件同一性
- **サンプル単位=raw attempt wav 1本(=独立なTTS 1 draw)**。Stdは減速(6%)前のattempt wav、Advは生成されたそのままのattempt wav。
  根拠: attemptは同一入力の独立再抽選で、`attempts/`に全て保存される(`PAUSE_MEASUREMENT_01.md` §5が同じ単位)。減速は後処理なので別分析(H4a)。
- 「統一条件」と「Production設定」は**同一**: Y本文3Voiceは全て同じ`_role_style_slower("FULL_STORY")`(Std, `er121_family_y_audio_01.py:560`)/`_role_style("FULL_STORY")`(Adv, 同:454付近)・同モデル(`gemini-3.8-flash-lite-tts`)・同ASR/Repetition QA・同6%減速で、Voice名だけが違う(`tts_voice(voice)`のみ)。よってVoice比較は1条件。生成script(`tools/yvp_cross_generate_01.py`)は`yfb_voice1_candidates_01.py`と同一呼出しでVoice・本文だけ引数化(offline testで設定同一性をassert)。
- 本文・句読点は`run_01/{a2,b1b}/parts.json`のy_voice_1/2/3を一字も変えず使用。Stdの3本文(120/157/156語)とAdvの3本文(133/155/158語)は**別文**(レベル差と本文差は交絡。H4bの注意点)。
- 適格サンプル=route が `custom`(Std)/`wide_margin`(Adv)の「main」のみ。`minimal_fallback`(Std、Style簡略化)は別条件のため分析本体から除外し付表に載せる。
- 計測(全サンプル共通・既存tool再利用): `yfb_silence_scan_01`(-40 dBFS・10msフレーム・>=150ms)、<120msの有音は前後停止を結合(`yfb_pause_stats_01.merge`)、位置は`yfb_pause_align_01`(推定位置±2〜3語)。
- 指標: n1=>=1000msの停止数(語数補正 r1=100語あたり)、最長停止、停止占有率occ(%)=内部停止合計/全体尺、発話速度(語/分、停止除外=speech_wpm・全体=gross_wpm)、文中>=500ms停止、ASR/QA(attemptのverified・audio_classification・repetition QA flag、takeのstatus)。聴感(7)はユーザー試聴(試聴ページ)に委ね、本Trialでは数値proxyのみ(自然さは判定しない)。

## 2. 比較マトリックス(Voice=列、本文=行。各レベル。n=main rawサンプル数の既存数)
| 本文＼Voice | V1 Algieba | V2 Zephyr | V3 Schedar |
|---|---|---|---|
| 本文1(V1担当) | **reuse** Std 9 / Adv 14 (run_01 attempts+候補take) | fresh 2 take | fresh 2 take |
| 本文2(V2担当) | fresh 2 take | reuse 1 + fresh 1 take | fresh 2 take |
| 本文3(V3担当) | fresh 2 take | fresh 2 take | reuse 1 + fresh 1 take |
Phase 1 = fresh 14 take/レベル = **28 take**(Fable既定どおり)。1 takeは正式経路のretry(最大3 TTS)を通るためsample数は>=take数。
- reuse(run_01正式attempt/Voice1候補take): 計測値の出典=`measure/samples_measured.json`のsrc=run01_prod|v1cand。fresh=src=trial。
- 件数内訳は結果表ごとに fresh/reuse を併記する。
Phase 2: **判定が「未確定(n不足)」のcellにのみ**1 takeずつ追加(最大12 take)。

## 3. 判定規則(生成前固定)
共通: cell(b,v)=本文b×Voice v のmainサンプル集合。occ(b,v)/r1(b,v)=cell平均、mx(b,v)=cellの最長停止の最大。Occ_v=bで等重み平均、Occ_b=vで等重み平均。判定はレベル(Std/Adv)ごと。
**n要件**: 判定に使うcellのどれかが main sample n<3 なら、その仮説は「支持/否定」にせず**未確定(n不足)**とし、Phase 2の対象にする(少数標本からの過剰断定防止)。

**H1 Voice固有(Algieba)**
- 支持: 全3本文で occ(b,1) > mean(occ(b,2),occ(b,3)) かつ Occ_1 − max(Occ_2,Occ_3) >= 2.0pt かつ R1_1 >= 1.5×max(R1_2,R1_3) かつ R1_1 − max(R1_2,R1_3) >= 0.3(/100語)。
- 否定: Occ_1 − max(Occ_2,Occ_3) < 1.0pt、または occ(b,1) <= mean(occ(b,2),occ(b,3)) となる本文が2本以上。
- それ以外=未確定。最悪take: 参考として V1の最悪(最長停止)がV2/V3最悪を上回るかを併記(判定には使わない)。
**H2 本文固有**
- 支持: ある本文Bについて、>=2 Voiceで occ(B,v)がそのVoiceの3本文中最大、かつ Occ_B − max(他2本文のOcc_b) >= 2.0pt。
- 否定: どの本文も「>=2 Voiceで最大」にならない、または max_b Occ_b − min_b Occ_b < 2.0pt。それ以外=未確定。
**H3 生成ばらつき(take間不安定)**
- 支持: V1×本文1 cell(n>=6)で occ の max−min >= 5.0pt、かつ 全main sampleの総平方和に占める cell内平方和の割合 >= 50%(=Voice×本文のcell差より同一条件の揺れが大きい)。
- 否定: V1×本文1 cellの occ 範囲 < 3.0pt、または cell内平方和割合 < 25%。それ以外=未確定。
**H4 生成条件**
- H4a(減速): Std `*_original.wav`(減速前)と最終wavの対で occ変化と>=1000ms個数変化を測る。「影響あり」= 対平均Δocc >= 1.0pt または Δ(>=1000ms個数)の対平均 >= 1.0。「影響なし(否定)」= |Δocc|<0.5pt かつ Δ個数<0.5。なお6%時間伸長は停止長を機械的に1.06倍するため、閾値跨ぎ(例:950→1007ms)による>=1000ms個数増は「機械的」と注記。
- H4b(レベル/Style差): 全main sample のStd−Adv の occ平均差。支持=差>=2.0ptが「V1」と「V2+V3」の両方で同符号、否定=両方で|差|<1.0pt。注: Std/Advは別文・別Style指示(Std=ゆっくり指示、Adv=wide margin)で交絡あり→「レベル差」であり単独Style効果とは言わない。Style単独の因果はこのTrialでは検証しない(未確定として残す)。
**H5 相互作用(Voice×本文)**
- D(b)=occ(b,1) − mean(occ(b,2),occ(b,3))。支持=max_b D − min_b D >= 3.0pt、否定=< 1.5pt、それ以外=未確定(n>=3要件を適用)。
**ばらつきの基準値**: cell内SD・範囲、最悪take、「>=1000ms停止が1つ以上あるsampleの割合」も全cellで併記(再現性)。

## 4. Phase 運用・停止
- 起動: レベルごとに1 process(a2, b1b)。起動前に`tools/stop_scope_check_01.py`(rc=0確認)、起動間隔>=150秒、同一run 5分以内3回起動なし。`TTS_EXECUTION_MODE=STANDARD`、`--budget-jpy 150`(cost logから実測、超過見込みで停止)。
- 費用: 見積 Phase 1 約82円(2.92円/take × 28)、Phase 2 最大約35円。Guardrail 150円。
- 書込先: `er121_output/family_y_voice_pause_trial_01/**`のみ(+共有台帳`er011_output/attempt_history.jsonl`等へ正式経路が追記する場合は行数をRESULT_PACKETへ記録)。

## 5. 実施記録(生成後に追記。§1〜§4の基準は変更していない)
- Phase 1: 28 take(a2 14 + b1b 14)、起動 a2 13:35:10 / b1b 13:37:45(間隔155秒)。生成待ち短縮のため同レベルの末尾cellを逆順で担当する並列process(a2 13:47:54 / b1b 13:50:31、各々起動間隔>=150秒、同一run 5分以内の起動は2回以下)を追加。cellの先頭でresult.json有無を確認するため重複生成なし(重複take 0)。
- Phase 2(§2の規則どおり「main sample n<3のcellのみ」): a2 5 take(b1v2,b1v3,b2v2,b2v3,b3v3)、b1b 6 take(b1v2,b1v3,b2v2,b2v3,b3v2,b3v3)=11 take(上限12以内)。起動 a2 13:59:49 / b1b 14:02:2x(launch_b1b_phase2_time.txt)。b3v1(Adv)はPhase 1の原processが完走。
- 生成中の挙動: 正式経路のretry規則(最終attempt前に10分cool-down `er020...maybe_cooldown_before_attempt`)で、3回目のattemptが必要なtakeは10分停止する。回避・短縮していない(Production retry規則の尊重)。
- 事前登録外の分析(すべて「事後・探索」と明記): (1) Voice対ごとの>=1s停止率の本文層別置換検定 (2) 位置別(hotspot)の発生率 (3) best-of-k選別の復元抽出シミュレーション(`tools/yvp_selection_sim_01.py`)。判定規則(§3)の結果とは別枠で、判定には使っていない。
- 所見(規則どおり): H1否定(Std/Adv)=占有率差が基準未満。ただし事前基準は占有率主体で、利用者が問題にしている「長い個別停止」の差は事後探索でのみ見える点を RESULT_PACKET_YVP1.md に明記。
