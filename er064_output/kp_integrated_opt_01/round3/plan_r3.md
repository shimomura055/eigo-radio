# Round 3 事前登録(生成前に確定。結果を見て変更しない)
管理ID: FAMILY-X-KP-INTEGRATED-OPTIMIZATION-TRIAL-01 委任_03 / 2026-10-13 / モデル: gpt-6-luna(Production同一。最新モデル原則の例外「比較可能性」、全call同一) / retryなし / Trial専用
ユーザー承認(2026-10-13): (b1)LLM補助抽出をRound 3のTrialに含める(Trialのみ、Production採用ではない、累計JPY300遵守、結果はVALIDATED等のTrialステータスで報告)。
Opus独立レビュー(条件A)の必須修正M1-M5・推奨R1-R8を反映(委任文)。以下に各項を対応づける。

## 1. (b1)設計(M1: Phase D抽出器の再利用。新規設計しない)
- 土台: `er064_kp_idiom_trial_01_extractor.py`(extractor v3 Prompt `prompts/extractor_prompt_v3.txt` sha256=`9133f1c1434aa629a9e7df956d4c1ef4e46b20b04162cb4cb2f4db56f074ed74`、2〜5語、`verify_span`、`narrow_to_core_span`、`build_llm_candidates`、ITEM_CAP=3)。Prompt本文は無変更で再利用(凍結)。新規モジュール `er064_kp_int_03_b1.py` は呼出ラッパ・決定論後処理・append・Tier H記録のみ。
- 入力(O1): 本文のみ。既存shortlistはLLMへ渡さない。重複・包含の除外はコード側の決定論処理(`build_llm_candidates`: 既存canonical重複、既存複数語候補を含み差分が閉クラスのみの包含重複)。
- M2: b1 Promptに評価アンカー・評価10記事の語句を入れない。例文(`out of the blue`/`a blessing in disguise`/`a cup of tea`/`go to school`)は10記事に出現しない(test)。testでCoffee語句BAN一覧+`anchors_r1.json`の全アンカー(label・full正規表現)の不在をb1 Promptへ適用。b1モジュールは評価アンカーを読まない(test)。
- M3: shortlistの`surface_form`はLLM spanを`verify_span`で本文token列と照合した逐語`source_span`(例 `been behind price increases`)。`canonical_form`は(b2)ルール候補と同じ関数 `ext._normalize_key(surface)`(test)。LLMの`expression`相当(`span`/`core_span`/`reason_en`/`kind`/`transparency`/`rank`)はsidecar(`b1/*/run*.json`)記録のみ。評価では「選定された」と「canonicalization PASS」を分けて数える。事前登録の合否基準: `be behind price increases`系が`be behind`へ倒れないこと(設計書L245)。
- M4: 挿入は(c)予約枠の直後に同形式でappend(`er064_kp_int_01_machine.py` L140-145と同手順: `attach_compact_context`→`fragment_risk(no_aux=True)`→`compute_containment(r2=True)`→Tier H削除)。順序=LLM rank昇順→同順位は本文初出位置。絞り規則(事前登録): 逐語検証・閾値(2〜5語)・閉クラスのみ除外・既存重複・包含除外を通過した候補をrank昇順に並べ、上位3件のみ採用(`ROUND3_CAP=3`、超過分は`over_cap`として記録)。LLMがPromptどおり最大3件を返すため、実際にはcapは稀にしか効かない。
- M5: 追加後の`compute_containment`再計算でTier Hにより削除される既存候補を、記事×レベル×抽出runごとに記録(`tier_h_deleted_existing`、b1自身が削除された場合は`tier_h_deleted_b1`、b1追加前の再計算差は`tier_h_recompute_base`)。集計は`tierh_deletions_r3.json`。
- R2: 選定Promptの候補行に`source: llm_aux`は表示しない(metadataの`evidence=llm_noncompositional`のみ)。行形式は(b2)と同一(`evidence: rule_poss_pattern`の同一文言を表示。実体はb1であることはsidecarとjob_resultの`evidence`欄で追跡)。`fragment_risk`は(b2)と同じ関数`U.fragment_risk(no_aux=True)`。
- R8: 非逐語率STOPの分母=出力1件以上の呼出の累計出力件数(出力0件の呼出は別途件数記録)。非逐語率>50%でStage 1中止。Stage 0で目視精度ラベル(正/誤/粒度不良)を付ける(`b1_labels_r3.json`、sonnet-workerの暫定ラベル)。

### Phase D(`phase_d/PHASE_D_REPORT_02.md`)がREJECTED as-isとなった理由(転記)と既知の失敗3件への対策
- 理由: 陰性対照FAIL(R3 run1の最終5件に偽陽性`get the first word`が混入)、D3_shortlist FAIL(run2でb1のみ候補の回収0)、副次的に`loan against the future`のcanonicalization INVALID(Rule7)。b1の費用対効果は「本文全文をLLMへ送る原則との衝突」込みで疑問、と結論。
- 失敗1 `in the ring`短縮(`two numbers in the ring`→断片`in the ring`): 対策=`guard_narrowing`(core_span縮約後の先頭が閉クラス語になる場合は縮約せずLLMのspanを維持)+`fragment_risk`注釈(閉クラス始まりの複数語は行末に付く、(b2)と同関数)。LLMがspan自体を`in the ring`で返す場合は防げない(Stage 0で件数記録)。
- 失敗2 陰性対照の偽陽性`gets the first word`(R3): 対策=Stage 0でPhase Dの陰性対照記事(N1 Std/D6 Adv/D5 Std/R3 Adv、`phase_d/inputs/`、各1呼出)に同一b1を適用し偽陽性をsidecarで測定。選定側はP5の「創作的な一回限りの言い回しはimportantに選ばない」とP0で挙動を測る(Round3では陰性対照の選定は行わない=抽出の偽陽性率のみ測定)。決定論の追加除外は新規仕様になるため行わない。
- 失敗3 `been behind price increases`→`be behind`割れでRule7 INVALID: 対策=shortlistの`surface_form`は逐語4語を維持、含む/含まれる注釈(`contains:`/`contained_in:`)で完結側を選ぶ手がかりが付く(U2/U3/R2既存機構)。canonicalizationは変更せず(gate無変更)、割れた場合は`be behind`型INVALIDとして分類・計測。合否は上記M3基準(選定/canon PASS別)。

## 2. 比較設計
### Stage 0(R1): b1抽出のみ、選定なし(18呼出)
- 評価記事10キー(coffee/meta/hormuz/smallbag/semi x Std/Adv = 本文はレベル別なので10記事)x1呼出=10、Coffee Std/Advのみ各2呼出追加(run2,3、揺れ測定。選定に使うのは事前登録した各キーのrun1)=4、Phase D陰性対照4記事x1=4。計18呼出。※委任文の「評価10記事xStd/Adv=20呼出」は、評価記事が10キー(Std/Adv別本文)なので二重計上と解釈し10呼出とした(解釈の記録)。
- 測定: 出力件数、逐語率、重複・包含除外数、目視精度ラベル、陰性対照での偽陽性、b1予約枠に入った語句、Tier H削除。
- **Go/No-Go(機械適用)**: Coffee Adv run1のb1予約(Tier H後の最終shortlistに残ったb1候補、最大3枠)に`behind price increases`系(anchor rank2のfull正規表現一致)が入ればGo。入らない、または非逐語率>50%ならb1選定arm(Stage 1全体)を中止し、残額は使わず報告(無駄打ち防止、対照揃えも実行しない)。
- 非ノーオペ規則: b1追加後のshortlistがM2と同一(accepted 0件、または全件Tier H等で追加0)のセルは、そのM2B jobを実行しない(M2P0 runと同一Promptのため)。

### Stage 1(Go時): 選定(38 job)
| 区分 | 条件 | n | 実行/再利用 |
|---|---|---|---|
| 最優先 | Coffee Adv x {M2+b1 P0, M2+b1 P5} | 5 | 新規(10 job) |
| 害検出・定性(R3) | Coffee Std x M2+b1 P0 n=5 / M2+b1 P5 n=3 | 5 / 3 | 新規(8 job) |
| 対照揃え | Coffee M2P0 n=3→5(run4,5) x Std/Adv | +2/Lv | 新規(4 job)。run1-3はRound1再利用 |
| 他記事(R5) | meta x {M2P0 n=2→4, M2P5 n=2→4} x Std/Adv | +2/条件/Lv | 新規(8 job)。run1-2はRound1(M2P0)/Round2(M2P5)再利用 |
| 他記事回帰 | meta/hormuz x {M2+b1 P0} x Std/Adv | 2 | 新規(8 job) |
- M2P3のn=5化は削除(R6)、hormuz P5追加なし。既存runの再利用は現在の構築Prompt/rowsのsha256照合(`reuse_check_r3.json`)。M2+b1のshortlistは全runで事前登録したrun1抽出を固定使用(job毎の再抽出はしない)。
- 条件名: `M2BP0`=M2+b1 P0、`M2BP5`=M2+b1 P5。

### 判定(R4)の事前登録
- 合算score(Std37+Adv47=84満点)の大小で判断しない。|差|≦5点は実質同等。run単位bootstrap(B=5000、seed固定、Std/Advは独立に再標本し合算)の95%信頼区間を併記。n=3-5は方向の目安。
- 判断に効く指標: per-anchor採用数(分母付き。特に`pump`・`be behind price increases`(選定/canonicalization PASS別)・`time lag`)、低優先枠占有/run、gate PASS率(選定INVALID/canonicalization INVALID/Redundancy NG別)、費用/job(b1呼出を同一キーのb1 job数で等配賦)、所要時間・reasoning token、`concierge`、b1由来候補の採用率、Tier H削除数。
- R7: Advで`pump`が押し出されないかをper-anchorで必ず確認(M2P0 Adv pump 3/3、M2P5 Adv 4/5を基準)。
- 判定語は「方向として有望/同等/不利」のみ。Status到達上限=VALIDATED(採用判断は人間ユーザー)。

## 3. 費用(E-1)
- Round 3上限JPY60、ハードストップJPY65(Round 3累計)、本Trial累計≦JPY164/300(Round1+2実績99.00+65)。1 job上限JPY2.5。
- Stage 0見積: 18呼出 x JPY0.25(設計書L176=Phase D M1実測0.25/回/level)=JPY4.5。Phase D抽出実測は0.116/呼出(2.0924/18)で約JPY2.1。**保守上限**として「1呼出JPY2」まで振れた場合の最悪JPY36を事前記録するが、Stage 0に独自上限JPY8を課し超えたら停止(runner内assert)。委任文の「JPY5〜40の幅」の下端〜中央に相当。
- Stage 1見積(保守): Std1.30/Adv1.10 x job数 = JPY45.4(38 job)。Round2実績ベースの期待値は約JPY38-42。Stage 0 4.5 + Stage 1 45.4 = 約49.9 <60。runner内で `累計+見積≦60` と `99.00+累計+見積≦164` を自動確認。見積が上限を超える場合は生成前にSTOP。
- 実績は`cost_r3.json`(呼出ごとに即時追記: model/入出力/reasoning token/cost)。

## 4. STOP条件
- STOP/STOP_ALL/KP用STOP_NOTICEの存在(生成前に確認・`prep_stage*_r3.json`の`stop_scan`に記録。Melos用STOP_NOTICE(FAMILY-Z-MELOS...)はrun_e2e_01限定の別件で、KP用ではない)。
- 非逐語率>50%(R8分母定義)、Go条件不成立、予算ハードストップ、1 job上限超過、外部停止/原因不明rc≠0が2回。再起動はしない(各Stage 1回のみ起動)。

## 5. 評価の同一定義
アンカー12件・簡易score(Std37/Adv47)・層2(gate)・低優先枠(9-12)・創作比喩定義はRound 1/2と同一(`anchors_r1.json`、`er064_kp_int_01_eval.py`をそのまま使用)。変更なし。
