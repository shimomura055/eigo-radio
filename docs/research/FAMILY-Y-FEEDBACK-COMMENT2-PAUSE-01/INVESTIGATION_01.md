# INVESTIGATION_01 — 『宅配』E-1 Full Story Voice 1(Std/Adv)の不自然なポーズ過多: 原因切り分け

管理ID: FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_02(Lane B)、2026-10-26。read-only・API 0・TTS 0。測定の詳細=`PAUSE_MEASUREMENT_01.md`、分割配線=`CHUNK_WIRING_CHECK_01.md`。
ユーザー原文§2の切り分け1〜6。表記: 【確認済み】/【推定】/【記録なし】。

## 結論
1. **分割・0.2秒・組立・減速は原因でない**(分割0/0.2秒0、組立後wavにも同一ポーズが元のまま存在、減速は無音を+6%伸ばすだけ)。【確認済み】
2. **主因 = Voice 1(Algieba)のTTS出力自体が『1秒を超える長い停止』を出しやすい**。E-1・E-3の2記事×Std/Adv=最終wav各4本で、≥1000msの停止がVoice 1=9個、Voice 2=0、Voice 3=3。停止占有率 22.4% / 19.9% / 15.2%。Std/Advとも、別々の生成で同傾向=共通原因。【確認済み(n=2記事、小標本)】
3. **副因(Stdのみ)**: Stdの『ゆっくり』指示+6%減速で停止占有率がAdvより平均+3.1pt(20.7% vs 17.6%)。うち減速分は停止長×1.06(約+1pt)。承認済みYL-A02仕様どおりの動作。【確認済み】
4. **E-1の採用wavは『同一本文の再生成の中で停止が多い側』が採られている**(Std採用attempt5は6本中で停止数最多・占有率25.7%、他は17.6〜19.8%)。選別基準(ASR一致+Gate+ユーザー試聴)に停止量の指標は無い。Voice 1は同条件の再生成で占有率が最大8pt変わる(ばらつき大)。【確認済み】
5. 1段落120〜135語を1 callで生成する点が悪化要因かは**未確定**: Voice 2/3は更に長い(147〜158語)が≥1000msの停止が0〜3個で、語数・長さだけでは説明できない。したがって『分割すれば直る』という仮説は現データでは支持も否定もできず、むしろ弱い。【推定】
6. 判断: **承認済み仕様内の不具合ではない**(適用範囲の不足でもない)。是正は新仕様判断を伴う(下記)。

## §2 切り分け1〜6への回答
| # | 項目 | 結果 | 根拠 |
|---|---|---|---|
| 1 | Voice固有の発話特性 | **主因候補(確度高)** | 同一Prompt/Styleで生成された3 Voiceのうちv1のみ≥1.0s停止が多い(9/0/3)。E-1・E-3の双方で再現。V1の最大停止1880ms(Std)/1320ms(E-3 Adv)。E-1のVoice 1再生成13本(Std 6+Adv 7)のうち10本で≥1.0s停止が出る(Voice 2/3は各1本ずつの生成で0〜2個)。停止の『個数』(文中停止の推定数)ではV2/V3と差が小さく、**差は長さ**。`PAUSE_MEASUREMENT_01.md` §2〜§5 |
| 2 | TTS Prompt・Style・速度指定 | **副因(Stdのみ)・全Voice共通** | 全Voiceに同一instruction(Std: "calm, steady news narration…slightly slower…Do not exaggerate pauses or sound instructional"、`attempts/y_voice_1_attempt1_custom53fd514d.json`)。Prompt自体はV2/V3にも掛かるがV2は停止が短い=Promptだけでは説明できない。Std全Voice平均は+3.1pt(Std 20.7%/Adv 17.6%)で、Std指示+減速の効果として説明できる |
| 3 | 段落分割の影響 | **影響なし** | 全segment `paragraphs=1`、chunk_ids=[](`audit/chunk_tts_decision.json`、`chunk_plan_b1b.json`) |
| 4 | 追加0.2秒の影響 | **影響なし** | 挿入0箇所。timeline上もVoice内部に無音追加なし |
| 5 | 音声結合・組立 | **影響なし** | 全編wavをVoice 1区間で切出して再計測すると元のnarration wavと同一の停止(21=21、20=20、16〜17)。segment間gapは固定0.8s(`er121_family_y_audio_01.py:752-762`)で『Voice 1内部』ではない |
| 6 | Std/Adv共通原因 | **Voice 1のTTS特性が共通**(別々の生成で再現) | Std V1とAdv V1はモデル/Voice同一・本文は別(英語化が異なる)・生成は別call。両方で≥1.0s停止が出る |
補足: Repetition QA D'(OPEN-525)がE-1 Voice 1でのみ繰り返し境界flagする点も、Voice 1の出力が『近接語周辺で間延び/反復状のぎこちなさ』を出す傾向と整合する【推定、D'は停止長を測る指標ではない】。

## 分類(承認済み仕様内の不具合 / 新仕様判断)
- 承認済み仕様内の不具合: **なし**。(a)追加0.2秒の二重挿入、(b)chunk末尾無音の未トリム、(c)分割が細かすぎる実装誤り、はいずれも該当せず(分割自体が0)。
- 新仕様判断(ユーザー判断候補・分類D): 以下は全て承認済み仕様(Voice固定=Algieba/Zephyr/Schedar `voice_assignment.json`、Style/Gate/ポーズ基準)の変更を含む。**本調査は『採用』と書かない**。
  | 案 | 内容 | QCD影響(見積) | 変更箇所/X・Z影響 |
  |---|---|---|---|
  | P1 | Voice 1の話者Voice差し替え(例: 他の既承認Voice)。Y Voice割当は『Z規則準拠・固定スロット』(`voice_assignment.json`) | Q: 長停止の根本回避が期待できる(Voice 2/3の水準)が、人物像と声の対応・Z規則との整合は再判断。D: 再生成+再試聴。C: 1記事あたりTTS数円。 | Y voice_assignment(slot定義)。X/Z不変(要確認) |
  | P2 | Voice 1の候補を増やして『停止の少ない候補を試聴選択』(HR採用の既存経路で停止量を参考表示) | Q: 現状の『最多側が採られた』偏りを防げる。D: 小。C: 候補1本あたりTTS 約0.4円+ASR 約0.1円(Stdは減速ASR再検証あり)×追加数本=数円。新Gateではなく選択材料の追加。ただし再生成回数が既存retry上限(chunkごと3 attempt等)を超える運用は承認範囲の確認が要る | `er121_e1_*`系HR運用(Production経路外) |
  | P3 | ポーズ上限Gate(例: 停止≥1.0s は不採用)の新設 | Q↑・C↑(再生成増)・D↓(retry増)。承認済みGateの新設=新仕様。閾値は本調査の標本(n=2記事)では較正不能 | Gate新設。X/Z共通Gateへ波及しやすい=Opus条件A |
  | P4 | Y Voiceの文境界分割(`CHUNK_WIRING_CHECK_01.md`の案1) | 因果が弱い(Voice 2/3が長尺でも問題なし)。効果はTrialで確認が必要 | `plan_y_chunks`のみ。X/Z不変 |
  | P5 | 現状維持(ユーザーは既に『問題なし』と試聴承認 `…USER_E1_APPROVAL.md`、今回Commentで再評価) | 追加費用0。ユーザー指摘への回答にはならない | — |
  推奨(Fable判断材料): まず**P2(候補追加+停止量の参考表示)**を『宅配』E-1のみで実施し、改善が出るかを確認。恒久策(P1/P3)は標本を広げてから判断。P4は優先度低(下記Trialを実施する場合のみ付随検証)。

## 追加TTSが必要か・最小構成と見積(実行せず)
既存データで原因切り分けは完了(上記1〜6)。**追加生成は不要**。次を確認したい場合のみ必要:
- **最小構成(P2+P4の効果検証)**: E-1 Voice 1の本文のみ、Adv b1b・Std a2それぞれ(a) 現行1 callで追加3 seed、(b) 文境界2 chunk(各約60語)で3 seed(= chunk 6 call)。計 TTS 12 call。
- 見積: TTS(gemini-3.8-flash-lite-tts) 実測 約0.38円/call(E-1 run: tts_a 24 call=9.157円、tts_b1b 21 call=8.850円)×12=約4.6円、ASR(gpt-4o-mini-transcribe) 約0.09円/call×12=約1.1円(+Azure STT cascade発動時 最大約0.7円/call)、Std減速ASR再検証3件 ≈0.3円。**合計およそ6〜10円**(委任の7-7 300円以下、日次枠内)。比較は停止数・≥1000ms個数・占有率(本計測scriptで即時算出)。
- 時間: 生成+計測 約20〜30分(2 levelを並列、独立)。

## 残リスク・未確認
- ポーズ位置の台本対応は推定(±2〜3語)。ASR語タイムスタンプ付きの再ASR(有料)でなければ正確化できない。必要なら追加でOpenAI/Azureのword timestamp ASRを数本(約数円)。
- 標本は2記事・Voice各4本。Voice 1固有性は強く示唆されるが『確定』は2記事までの観測。
- ユーザーが聞いて不自然と感じた具体の時刻は未取得(Commentに時刻が無い)。測定上の≥1.0s停止(`PAUSE_MEASUREMENT_01.md` §3)がそれに該当する可能性が高いが、一致確認はユーザー試聴で行う。
- 比較対象の『同一Voice名の他のX/Z音声・er110 trial』は今回未計測(時間優先でE-1/E-3に限定)。
