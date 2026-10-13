# Round 2 事前登録(生成前に確定。結果を見て変更しない)
管理ID: FAMILY-X-KP-INTEGRATED-OPTIMIZATION-TRIAL-01 委任_02 / 2026-10-13 / モデル: gpt-6-luna(Production同一=最新モデル原則の例外「比較可能性」)、retryなし
Fable判断(委任文): M2固定(=(a)+(b2)+(c)、追加LLM呼出なし、`match:`注釈なし)/ (b1)LLM補助抽出はRound2に含めない / Production gate(Redundancy/canonicalization)は変更しない(NG/INVALIDは計測・分類のみ)。前提の訂正「(a)単独ではpump回収不可、M2=(a)+(b2)+(c)」はFable受理済み。

## 組合せ・n
| 区分 | 条件 | n | 実行/再利用 |
|---|---|---|---|
| 主比較 | Coffee Std/Adv x M2P5 | 3 (Stage1) -> 5 (Stage2) | 新規 |
| 主比較(対照) | Coffee Std/Adv x M2P0, M2P3 | 3 | **Round1のrunを再利用**(再実行しない)。再利用条件: 現在の構築Promptのmsg_sha256・rows_sha256がRound1 job_resultと全一致、shortlists_r1.jsonのsha一致。確認結果は`reuse_check_r2.json` |
| 回帰 | meta/hormuz x Std/Adv x M2P5 | 2 | 新規。比較対象はRound1のM2P0/M2P3(各n=2)と基準M0P0(前回Phase2 C0再利用、n=3) |
- 評価アンカー12件・簡易score(上限Std37/Adv47、Std+Adv合算84)・層2(gate)分離集計・低優先枠(アンカー9-12)・創作比喩定義はRound 1と**同一定義**(`anchors_r1.json`、`er064_kp_int_01_eval.py`をそのまま使用)。定義変更なし。
- n=3は方向の目安(1-2 runの差は有意でない)。n=5へ拡張したP5は対照(n=3)よりnが大きい点を明記して提示し、同一n=3での比較も併記する。

## Stage構成(各Stage 1回だけ起動、再起動・自動retry・監督ループなし)
- Stage1: Coffee M2P5 Std/Adv x run1-3 (6 job) + meta/hormuz M2P5 Std/Adv x run1-2 (8 job) = 14 job。
- Stage2: Coffee M2P5 Std/Adv x run4-5 (4 job) = 4 job。実行条件: Stage1の結果にかかわらず実行する(予算に余裕があり、nを増やして方向の確度を上げるだけで、判定規則は変えない)。ただしStage1でハードストップ/STOP/外部停止/原因不明のrc!=0が出た場合は実行しない。

## 費用規則・見積
- 上限Round2 JPY65、ハードストップJPY70(Round2累計)、本Trial累計JPY150.72以下(Round1実績80.72 + 70)。1 job上限JPY2.5。
- 見積(保守、Round1実績単価 Std1.185/Adv0.938): Stage1 14 job = 約14.9、Stage2 4 job = 約4.3、合計 約19.1(実績ベースでは約17)。本Trial累計見込 約99.8(150.72以内)。見積が上限超過見込みの場合は生成前にSTOP。runner内で`累計+見積<=70`と`80.72+累計+見積<=150.72`を自動確認。
- 使い切らない理由: 委任文の範囲(P5のn拡張のみ)に限定。余剰枠(約46)の使途(対照M2P0/M2P3のn=5拡張、他記事拡張、(b1)等)はFable/ユーザー判断。

## 判定の見方(事前登録。採用判断ではなく、Trial内の方向づけ)
1. pump不採用の回避: P5のCoffee pump full採用(Std+Adv)が、M2P1/M2P4の0/6型でないこと(0/6なら「不採用再現」)。目安: M2P3(4/6)以上ならP3と同等以上、M2P0(6/6)並みなら良好。
2. 低優先枠の維持: P5の低優先枠/run(Std/Adv別とStd+Adv平均)がM2P0(Std1.67/Adv0.67、平均1.17)を下回り、M2P3(Std1.0/Adv0.33、平均0.67)に近いこと。
3. アンカーscore: Std+Adv合算をM2P0(71.3)/M2P3(62.0)と比較(同一n=3の比較)。
4. 契約遵守(層2): P5の選定INVALIDが0であること、canonicalization INVALID率がM2P0(Coffee 1/6相当)以下、Redundancy NG率がM2P3以下であること(NG/INVALIDは計測・分類のみで、gateは変更しない)。INVALID理由の分類(source_span超え表示拡張[OPEN-310新サブクラス] / Rule7所有格系[35組] / その他)を記録。
5. 他記事回帰: meta Advの`concierge`採用(Round1 M2P3は0/4、M2P0はStd1/2・Adv2/2、基準Std3/3・Adv1/3)、hormuzのRedundancy NG率(基準NG、M2P0 Std 0/2 NG)。P5でM2P3の悪化(concierge 0/4)が回復するか、hormuzでNGが増えないかを事実として記す。
6. 判定語は「方向として有望/同等/不利」のみ。VALIDATED到達でも採用判断は人間ユーザー。Statusは`USER_DECISION_REQUIRED`候補。

## P5設計の記録(生成前確定、`prompts_r2.json`に逐語・sha・P0/P3比較・差分)
- P5 = P3を土台にした一から書き直しの全文。必須4要素: (i)Production P0の「未知単語、題材固有表現、短い複数語パターン、比喩・感情表現を同格の候補として扱ってください。構成語から…優先度を下げてください。」を逐語復活 / (ii)辞書見出しの定着表現は擬人的・比喩的な使用でも定着表現として評価し、創作的な言い回しは「筆者がその場で作った一回限りの言い回し(辞書にも載らず他の記事でも通用しない)」に限定 / (iii)P3の低優先抑制(「基本表現・透明表現は価値の高い候補が残る限り枠を使わない」+仮選定後の入れ替え確認)を逐語維持 / (iv)出力契約の再確認(日本語グロス括弧書き禁止・normalization_note必須)を【出力のルール】末尾へ追加。
- **P3との差で注釈説明が変わる点(要注意)**: P3(Round1)の注釈説明は`match:`ラベルの説明文を含んでいたが、M2固定では候補行に`match:`が付かないため、P5では`match:`の説明文を削除した(Fable判断「`match:`注釈は外す」に整合)。P5 vs P3の差にはこの削除が含まれる(P5の効果を分離するには別途要検証)。
- token(text-only): P0 1402 / P3 1278(Std)・1295(Adv) / **P5 1451(Std, P0比+3.5%, P3比+13.5%)・1468(Adv, +4.7%, +13.4%)**。P0比+10%以内。P3比+13%超の理由: 復活したP0同格文(約80token)+定着表現規則+出力再確認文。
- Rule7(所有格35組予測)への影響なし(静的): 【学ぶ単位】段落(動詞は基本形へ)はP3と逐語同一で、P5は所有格/人称/活用形に触れる指示を追加していない(testで確認)。canonicalizationはPrompt後段のProduction処理で、Promptからは変えない。
