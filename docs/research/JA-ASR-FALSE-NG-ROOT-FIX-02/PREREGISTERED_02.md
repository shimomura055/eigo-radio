# PREREGISTERED_02(JA-ASR-FALSE-NG-ROOT-FIX-02 委任_02B、2026-10-28。eval_unified_02.py・n3再転写の実行前に凍結)
前提: PREREGISTERED_01.md の定義(結果カテゴリ PASS/PASS_W/NG、誤PASS=PASS+PASS_W、増分誤PASS=M0がNGで当該構成が誤PASS、シナリオ P_only/PS_same/S_canon/explicit/real)をそのまま継承。Production code・SSOT編集なし。有料はN3再転写のみ(上限¥3、見積¥0.7)。

## 1. 評価セットと固定sha
- 正例: 6音声(run_ms_03 a1-a3 / run_reselect_01 a1-a3、wav sha256照合)。決定対(stored pair)+全draw対(27 OpenAI draw × Azure)。Phase 1と同一 loader(`eval_unified_01.load_positives`)。
- 負例(Phase 1と同一): `eval_unified_01.out.json`(sha256 e5b4f6f14d4efd63…)の truth==NEG 1439行。行集合sha256(sorted[group,tag,canon,primary,scenario,secondary]) = d55f24e239d3eb024951c01e57a8d186d9cd6a8ebf979c6470399b5cea2405dd。eval実行時に再生成コーパスのNEG集合shaが一致することをassert。
- 新規負例: (a) `N3_redraw`: N3 30wavの新規OpenAI 4 draw(`n3_redraw_02.json`)× Azure保存転写(scenario real)および S_canon(Secondary=原稿そのもの=最悪露出)。(b) `L3_NEG/L3_POS`: 『超/越/超え/こえ』を含む合成負例・正例(値違い・助数詞違い・本長/本帳/本蝶[E4/C2同形異音]・語句挿入・数量に付かない超 等)。各シナリオ P_only/PS_same/S_canon。月題固有でない汎用題(100人超/売上1,200円超 等)を含める。
- 既存のPOS(180)・UNL(87)は回帰/参考として同じく評価(POSのM0→NG回帰=0が必須)。

## 2. 層の定義(切替可能。既定は全OFF=L0)
| 層 | 内容 | 位置 |
|---|---|---|
| L0 | 現行Production HEAD(adapter→統一judge→最終AND gate)。Azureはstub(保存転写) | 基準(Phase 1のM0と**行ごと同一**であること) |
| L1 | v2読み規則(proto_reading_compare_02.pron_value_equivalence)を `_numeric_value_equivalence` 位置(Primary層とSecondary受理層)へ差替、v2が救済しない時はProduction層へフォールバック。**追加ガード(新規)**: 原稿に不規則読み数詞(`er078_asr_value_guard_01.extract_atoms_ja`のnum atomで`is_irregular_sig`該当: 一日/二日/…/二十日/二十歳 等)があれば、PRON・VALUE_ONLYとも**Primary/Secondary両側で**v2を適用せずProduction層へ戻す(fail-closed) | M1相当+ガード |
| L2 | β composite(b_light_proto_02.composite_judge)。L0/L1後段でNG理由が ELIG(p1_value_diff / final_gate_value_diff / p1_protected_diff:number_mismatch / secondary_not_accepted)のときだけ、保存Secondary転写で評価。常にPASS_W(試聴必須) | M2/M4相当 |
| L3 | 読み候補辞書拡張(汎用規則): **原稿で数量atom(数字+助数詞)の直後に『超』**があるとき、ASR転写のその位置の `超え/越え/こえ`(直後がる/た/て/な/ば/ず/よ以外)を『超』へ正規化してからL1比較する。**発火条件**: (1)PrimaryとSecondaryの転写が両方ある (2)両転写とも原稿との値ガードEQUAL(数量・桁・助数詞一致) (3)正規化後の残差はL1(v2)が従来どおり判定(=差分が『超え』だけでなくv2の助詞/同音規則で説明できない他の差があればNG)。月題固有語・固定文字列なし(atom位置からの導出)。L3はL1を前提(L1 OFFでは不可、評価は L1+L3 と L1+L2+L3)。L3経由のPASSは常にPASS_W(監査キー layer=L3_dict_koe)。Primary NGでSecondary未呼出のとき発火には**Azure追加呼出が要る**(単価に反映) | 新規 |
| L4 | (ii)best-of-N: 判定前に同一wavをOpenAIへ再転写。評価は保存drawで「N個目まで順に判定し最初にPASS/PASS_Wになったdrawで停止」をシミュレーション(Azureは同一転写=変動0を仮定)。N≤3を主、N=4は参考。**承認済み仕様『同一音声のASR再試行廃止』の変更を伴う**ためProduction採用はユーザー判断事項 | 前処理 |
- 組合せ(6音声表): L0 / L1 / L1+L2 / L1+L3 / L1+L2+L3 / L1+L2+L3+L4[N=2] / [N=3] / (参考 N=4)。
- 各構成の判定ログに `layers_fired`(層名・根拠)を出力。

## 3. 合格写像
- 6音声(ユーザー§6-1): 最終判定を PASS / PASS_W / NG で**別集計**(決定対と全draw対)。PASS_Wは『試聴必須・無条件PASSではない』。
- 負例: 増分誤PASSを層別・型別に集計。**Phase 1の3型**(同音異表記便乗=音素列が原稿と同一[区別不能] / β値garble[Secondary=原稿そのものの最悪露出] / 不規則読み(L1ガードで0になる想定))**以外で増分>0の層は不合格**(Fableへ『不合格』として開示。緩和での調整は禁止)。回帰(M0 PASS→NG)0必須。
- L3: L3_NEG(値違い・助数詞違い・本長/本帳/本蝶・語句挿入・脱落)で増分0、L3_POSは救済(PASS_W)を確認。月題以外の汎用題でも同様。
- best-of-N誤PASS率: N3 30wavの新規4 drawで、N=1..4 の「いずれかのdrawがPASS/PASS_Wとなる率」を構成(L0 / L1+L2+L3)別に報告。保存済みOpenAI転写(Phase 3 N3_asr)を第0drawとして加えた参考値(N=1..5)も併記。順序依存を避けるため、順列平均(draw集合からN個を無作為に選ぶ超幾何確率)も併記。釣りリスク=N増加に伴う誤PASS率増分。
- 正例のbest-of-N: 各wavの「N個以内に到達する確率」(順序=保存順の到達indexと、超幾何による平均)。
- Human Review条件(iv): 機械条件案を定義し、(a)6音声の残NGがキューに乗るか、(b)負例(text 1439+N3新規)のうち何件がキュー候補になるか(=人間負担)、(c)キューは人間判断のみでPASSに自動昇格しないこと(抜け道: 自動PASSパスが無いこと)をコード上で確認。既存HR機構(Lock/個別採用registry)との差分を file:line で明記。
- 決定性: eval_unified_02.py を2回実行して出力JSON sha256 が一致。
- Statusは付けず『候補』のみ(VALIDATED判定はFable)。
- 単価: 記事あたり増減を区間(誤NG率未知)で提示。

## 4. 禁止
Production code(er0XX_*.py)・SSOT・ACTIVE_TASK編集、TTS呼出、N3再転写以外のネットワーク、Azure呼出、再転写の再実行(1起動のみ、失敗時は再起動せず報告)。Family A/B/C非接触。
