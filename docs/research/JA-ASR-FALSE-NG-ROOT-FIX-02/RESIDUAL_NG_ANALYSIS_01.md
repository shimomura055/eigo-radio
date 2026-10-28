# RESIDUAL_NG_ANALYSIS_01(残NGの原因分析。JA-ASR-FALSE-NG-ROOT-FIX-02 委任_01B。API 0、保存転写のみ)
数値の出所: `residual_analysis_01.out.txt`(residual_analysis_01.py)、`EVAL_UNIFIED_01.md` §1・2a-2d。分類=「TTS側の発音ゆれ / ASR側の誤認識 / 判定規則の不足」。**ground truthは人間試聴OK(6本とも)のみ**で、音声の実際の読みは転写から推定した(推定と断定は区別して記す)。

## 0. 先に結論(最終Gateが決定対で残るNG)
方式適用後も決定対がNGなのは **ms_03 a1** と **reselect a3** の2本(M4。M2/M4でもNG)。原因は別系統で、**どれも新しい判定規則1つでは直らない**。

| 音声 | 残NGの主因(分類) | 従因 | 機械確定 |
|---|---|---|---|
| reselect a3 (minimalfallback) | **ASR側の誤認識**: stored OpenAI『スギノ市は』+Azure『Sukino氏は』(両Production engineが同方向)。第三証人ローカルWhisper small/medium はどちらも『月の詩は/死は』=しわ互換 | OpenAIの値崩れ(再転写4本中3本が『8000坪』『発生900』) | **不可**(2エンジン一致して原稿と異音)。Human Review or ASR再試行 |
| ms_03 a1 | **TTS側の読みゆれ(推定・強)**: 『超』を『こえ』と読んだ。OpenAI 4/4『超え』、Azure『越え』、Whisper medium『超え』が一致。他5本は『超』のまま、または『ちょ(う)』『長・調』など「ちょう」系の表記 | OpenAI数詞崩れ(storedが『8000句800』。再転写4本中2本は8,900); **判定規則(読み候補辞書)の不足**: `reading_candidates_for_span('超')=['ちょう']`、`'超え'=['こえ']` | **不可**(音声の読みが原稿の標準読みと異なる。人間OK) |

## 1. (a) reselect #3: 『スギノ/Sukino/杉野』
- 転写(全文は EVAL_UNIFIED_01.md §1): OpenAI stored『スギノ市は、八千九百本超、…』、再転写4本=『杉の市は、8000坪の…』『月野市は、八千九百本超。…』『月の死は、発生900本超。…』『月野氏は、発生900本超。…』。Azure『Sukino氏は8900本超。…』(当時記録と再ASRで完全一致=Azure変動0)。Whisper small『月の詩は8900ポンチョ』/medium『月の死は8,900ポンチョウ』。
- 5 OpenAI draw中スギノ系は2(stored+杉の)、月系は3。Azure 1/1がスギノ系。ローカルWhisper 2/2が月系。ms_03 a3(同じminimalfallback route)でもAzureは『杉野氏は』(Phase3記録)=**Azureが fallback route 音声2/2で『杉野/Sukino』、custom route 4/4で『月の詩は/月野市は』**。n=2のためroute起因は仮説に留める(TTS側で『つ』が弱く『す』に近く聞こえる可能性と、固有名詞prior[杉野氏]の両方がありうる)。
- 判定規則の観点: 『スギノシワ』≠『ツキノシワ』なので規則は正しくNG。**規則側に直す余地はない**。分類=ASR側の誤認識(推定。TTS側の弱い「つ」の寄与は否定できない)。
- 同一wav再ASRの結果変動: OpenAI 5 draw中、v2 Primary単独でPASS_Wとなるのは1(『月野市は、八千九百本超』)。ASR再試行N=3で到達(2d: `..o..`)。

## 2. (b) ms_03 #1/#3 と reselect #2 の OpenAI 数詞崩れ(同一wavでも時点で変動)
| 音声 | OpenAI draw(stored含む)の値 | 崩れ方 |
|---|---|---|
| ms_03 a1 | 4中2が『8,900』 | stored『8000句800』 |
| ms_03 a2 | 4中1(stored『八千九百』のみ) | 再転写3本は同一『月の島は千九百本超』(『八』脱落) |
| ms_03 a3 | 4中2 | stored『8000900』、『8000九百』 |
| reselect a1 | 5中5 | 崩れなし |
| reselect a2 | 5中1(stored) | 再転写4本中3本『8000900』、1本『発線900』 |
| reselect a3 | 5中2 | 『8000坪』『発生900』×2 |
- 合計 **27 draw中13(48%)のみ値が正しい**(値ガードEQUAL)。**再ASR12転写(reselect 3wav×4)では5/12、12転写中10が異なる転写**(wav別distinct=4/2/4)。同一wavでstoredと再転写が逆転する(reselect a2はstored正→再転写4本中3本崩れ、ms_03 a1はstored崩れ→再転写2/3正)ので**時点(モデル更新)ではなくdraw間のランダム変動**が主。
- **Azureは6本すべて値8,900を正しく転写**し、ローカルWhisper mediumも5/6で正しい(reselect a3のみ『本』欠落)。→ 分類=**ASR側の誤認識(OpenAI gpt-4o-mini-transcribe の数詞断片化)**。TTS側の寄与は証拠なし(他engineが正しく読めているため)。観測形は『d×10^k+残り』(8000+900 / 8000句800)で、βの断片説明(`explain_garble`)の対象型と一致。
- 判定規則の観点: 現行は p1_value_diff で即NG(Secondary不呼出)。βはSecondary値を証人にして救済(試聴必須)。**ASR再試行**でも確率的に解ける(独立と仮定すれば値正解率p=0.48でN=2→73%、N=3→86%。ただしwav別pは0.2〜1.0で、独立性は未検証)。

## 3. (c) 『詩は/氏は/市は/死は』の同音異表記+助詞
- 全転写(OpenAI27+Azure6+Whisper12)の「しわ」部分の表記: OpenAI=月の詩は7・月野氏は5・月野詩は3・月の島は3(値崩れ)・好きの詩は2・月の死は2・月の氏は1・月のシワ1・スギノ市は1・杉の市は1・月野市は1、Azure=月の詩は3・月野市は1・杉野氏は1・Sukino氏は1、Whisper=月の死は6・月の詩は3・月の種は2・月のしは1。**『月のしわ』と漢字+ひらがなで書いた転写はほぼ0(OpenAI『月のシワ』1のみ)**。
- 『月野氏は』『月の詩は』『月の死は』は音素列がいずれも ツキノシワ=原稿と同一。分類=**判定規則の不足**(助詞は→わの発音等価と同音異表記を許さない現行規則)。TTS側・ASR側の誤りではなく、**表記の曖昧性**。v2/P-1が解く(M1で決定対3本、全draw対でも解消)。
- 注意: この救済は音素列が同一な場合に限る(『月の詩は』≠『月の歯は』のようにASRが別音を書けば不一致で落ちる)。誤PASSの増分は「音素列が原稿と同一」型のみ=音声としては原稿と同じ音(EVAL_UNIFIED_01.md §3a)。

## 4. 同一wav再ASRで結果が変わる割合(数値化)
- OpenAI: 27 draw中 **値が正しい48%**、v2 Primary単独PASS_W **26%(7/27)**。wav別のv2 Primary単独PASS_W: ms_03 a1=0/4, a2=1/4, a3=1/4, reselect a1=3/5, a2=1/5, a3=1/5。再ASR12転写の distinct=10/12。
- Azure: 再ASR3/3で当時記録と完全一致(変動0)。ms_03 a2も一致。→ **変動はOpenAI側に集中**。Azureは系統誤差(スギノ/ちょ/越え)を持つが再現的。
- 決定対と全draw対の差: M4で決定対PASS_W 4/6、全draw対 12/27。best-of-N(2d): N=1で4本、N=3で5本(reselect a3が3本目で到達)、ms_03 a1は何回でもNG(こえ+規則)。
- 費用の実測: OpenAI再転写 ¥0.0056/本(6秒題。約¥0.0009/秒)、Azure ¥0.27〜0.31/本(約¥0.045/秒)、TTS ¥0.65/clip(Phase3 N3 30本の平均)。→ ASR 1回の再転写は TTS再生成(¥0.65+ASR2本¥0.27≈¥0.92)の約0.6%。

## 5. 6本の残NGと原因の対応(まとめ)
| 音声 | M0 | M4 | 解けない障害 | 解くのに必要な手段 |
|---|---|---|---|---|
| ms_03 a1 | NG | NG | (1) OpenAI数詞崩れ[ASR] (2) 超→こえ[TTS読みゆれ+辞書不足] (3) 月野詩は/市は[規則不足=v2で解決] | (1)はβ/ASR再試行、(2)は読み候補の拡張 or TTS入力側の読み固定 or Human Review |
| ms_03 a2 | NG | PASS_W | 読みの同音異表記[規則不足] | v2/P-1 |
| ms_03 a3 | NG | PASS_W(β) | OpenAI数詞崩れ[ASR] + Azure『杉野氏』 | β(Azure値証人)、残り読みconflictは試聴必須 |
| reselect a1 | NG | PASS_W | 同音異表記[規則不足] | v2/P-1 |
| reselect a2 | NG | PASS_W | 同音異表記[規則不足] | v2/P-1(OpenAI stored正値だったため) |
| reselect a3 | NG | NG | スギノ[ASR誤認識+音響的近接] | ASR再試行N=3 / 第三証人 / Human Review |
