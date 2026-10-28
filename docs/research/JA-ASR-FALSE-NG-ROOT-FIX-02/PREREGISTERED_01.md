# PREREGISTERED_01(JA-ASR-FALSE-NG-ROOT-FIX-02 委任_01B、2026-10-28。eval_unified_01.py 実行前に凍結)

目的: 既存方式(Production HEAD / v2 / P-1 / β / 併用)を**同一条件**で再評価する。API 0・TTS 0・ASR 0(保存転写のみ、socket guard)。Production code・SSOT編集なし。新方式の実装・新Trialなし(Phase 1)。

## 1. 方式の定義と包含関係(二重評価の防止)
| ID | 定義 | 包含関係 |
|---|---|---|
| M0 | 現行Production HEAD(930c31ff2: F1+F2/E3/E4/R4R3込み)の**最終判定**。`er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail`→`er078_asr_unified_judge_01`(Primary→P1/P2→Secondary 1回→最終AND gate)。Azure呼出はstub(保存転写を返す) | 基準 |
| M1 | v2読み規則(`proto_reading_compare_02.pron_value_equivalence`: 助詞は→わ/へ→え発音等価 + c2_blocked + A7 + A4(a)不規則読み)を、Production `_numeric_value_equivalence` の位置(Primary層と Secondary受理層の両方)へ差替。v2が救済しない場合は**Production層へフォールバック**(M1 ⊇ M0) | M3 ⊂ M1 |
| M3 | **P-1**=v2のうち「助詞は→わ/へ→えが必要な救済」(cause=A2_particle / A3_value+A2_particle)とVALUE_ONLYのみ。同形の別読み救済(ENGINE_reading_difference / A3_value+pron)は除外。**P-1はv2の部分集合**であり別方式ではない(表では M3 列として併記するが、「M1−M3」差=v2のみの追加救済として扱う) | ⊂ M1 |
| M2 | M0の後段に β(`b_light_proto_02.composite_judge`: 値=Secondary由来、読み=Primary由来、読み規則=v2、断片説明[観測形のみ]、listen_required)を追加。Primary/Secondary NG理由が ELIG(p1_value_diff / final_gate_value_diff / p1_protected_diff:number_mismatch / secondary_not_accepted)のときだけ評価。**βは読み規則としてv2を内包する**(b_light_proto_02.py V2-1)ので、βとv2は独立方式ではない(β=v2読み+Secondary値証人) | β ⊃ v2読み(compositeの内部) |
| M4 | M1 + M2(v2をPrimary/Secondary層へ入れ、残NGにβ) | M4 ⊇ M1, M2 |
| M5 | 判定前のASR再試行(同一wavをOpenAI/Azureにもう1回)。保存済み再転写(再ASR12転写+Phase3再転写)から**正例のdraw集合**でのみ best-of-N 集計。負例は再転写が無いため**実測不能**(理論: N draw のOR=誤PASSがN倍までありうる、を設計案に明記) | 判定方式ではなく前処理 |

## 2. 結果カテゴリ(混同禁止)
- **PASS**: 最終判定がPASSで、新方式のlayer(v2発音救済 / β)を経由しない。
- **PASS_W**: (a)判定器が `PASS_WITH_WARNING`(Production既存の警告付きPASS)、(b)新方式の救済経由(v2 JA_PRON_EQUIVALENT、β composite)=試聴必須扱い。**PASSと別集計**。「無条件PASS」とみなさない。
- **NG**: 上記以外(reason_codeを記録)。
- 負例の「誤PASS」= PASS + PASS_W の合計。ただし内訳(PASS/PASS_W)も出す。**増分誤PASS** = 方式Mxが誤PASS かつ M0が NG の件数。

## 3. 正例(必須): 6音声
run_ms_03 a1-a3、run_reselect_01 a1-a3(wav sha256で紐付け、attempt jsonのsha256と一致をassert)。各音声について保存済み**全**転写を収集: OpenAI(保存 + Phase3再転写3[ms_03] / 再ASR4[reselect])、Azure(保存scg_info + Phase3 + 再ASR)、ローカルWhisper(small/medium、第三証人=参考、判定に不使用)。
- **決定対(stored pair)**: 当時の記録OpenAI転写 × 当該wavのAzure転写(最初の1本)。これを「最終Gate結果」とする。
- **draw集合**: 全 OpenAI draw × 全 Azure 転写(+Azure不呼出=Primaryのみ)の分布。安定性(同一wavでの判定変動)を数値化する。
- Azure転写が無い音声: 6本とも保存Azure転写あり(Phase3 A1/A3 + 保存scg_info + 再ASR)→ **補完ASR不要・追加API 0**。

## 4. 負例・対照(すべて保存・合成テキスト。API 0)
| group | 件数の目安 | 真値 | 備考 |
|---|---|---|---|
| N1_150 | 150(+structural 1=UNL) | NEG | `n1_pairs_01.all_pairs()` |
| OPEN333_sweep8 | 40 | block→NEG / keep→POS | 8クラス(P-1負例 はし→わし/はな→わな/へや→えや 含む) |
| OPEN333_E4 | 72 | neg_hira/e4n→NEG、out_of_scope→UNL | |
| R4R3_extra18 / R4R3_pos / er066_POSITIVE | 18 / 4 / 既存 | NEG / POS / POS | |
| UC6_U1..U6(新規) | 6分類×(MOON 5+汎用2-3) | NEG | **§4-3の6分類**。既存に無い/不足の分を合成追加(U1異なる発音/U2異なる数値/U3助数詞違い/U4語句脱落/U5意味を変える読み違い/U6同音異表記便乗)。各分類>=3件 |
| OPEN517_wrongvalue_kana | 決定的サンプル(20助数詞×8値) | NEG | 原稿=数字+助数詞、転写=別値のかな読み |
| BLIGHT_synthetic | 55+17+19 | NEG | B_LIGHT_EVAL_02 の合成負例(値/読み/複数atom/同一助数詞/FB) |
| N3_real30 | 30 | NEG | 実TTS(意図的誤読)→実OpenAI+実Azure |
| HIST_43pairs | 43 | UNL(真値不明) | 実Production履歴のP-S対。**増分PASSを全件列挙し個別審査**(誤PASS率には算入しない) |
- テキスト負例は3シナリオ: `P_only`(Secondary不可)/ `PS_same`(Secondary=同じ誤転写=両エンジンが同じ誤りを出す)/ `S_canon`(Secondary=原稿そのもの=Primary誤りに対しAzureが正解を出す最悪露出)。`explicit`/`real` は与えられた(P,S)。
- 汎化(「月のしわ」固有でないこと): 汎用題(売上/参加者/犬/本/橋・箸 等)を UC6・BLIGHT・OPEN517 に含める。

## 5. 合格写像(Phase 1は評価・比較の提示まで。Statusは付けない)
- 各方式について: (a) 6音声の stored pair 最終結果 PASS/PASS_W/NG、(b) draw集合の PASS+PASS_W 率、(c) 負例 NEG 全群の誤PASS(PASS/PASS_W別)・**増分誤PASS(M0比)**、(d) UNL(HIST)の増分PASS列挙、(e) POS対照の回復/回帰(M0 PASS→NG の回帰件数は 0 であるべき=M1⊇M0、M3⊇M0 の確認)。
- 「増分誤PASS=0」は強い合格材料、>0は個別に型を分類(garble断片型 / 同音異表記便乗 / 構造的に区別不能)して設計案のリスクとして開示する。**安全基準の緩和による見かけのPASS率向上は採用根拠にしない**。
- 決定性: 2回実行で出力JSONのsha256が一致すること(不一致なら原因を開示)。

## 6. 禁止
Production code(er0XX_*.py)・SSOT編集、TTS呼出、新規ASR呼出(補完が必要なら上限¥30・事前にBUDGET_PLAN_01.mdへ見積)。Family A/B/C非接触。
