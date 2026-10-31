# RESULT_PACKET_N5R_01 KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01 委任_01(2026-10-31)

成果物: `docs/research/KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01/`(ROOT_CAUSE_01.md / DESIGN_OPTIONS_01.md / TRIAL_PLAN_01.md / tools/ / ev01/)、OPEN-635(INVESTIGATING)、ユーザー原文=`docs/pm/delegation_log/2026-10-31_KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01_USER.md`。Production変更0・新flagなし。

## 結論(根本原因の確度)
- モデルは`put away`/`in the way`/`leave out`/`in sight`を**認識できる**: 同一本文・同一モデル(gpt-6-luna)で「難易度不問の網羅列挙」Promptにすると4表現とも3/3(本番0/11〜1/9)。連続一致規則と分離形の衝突は棄却(L3が`put away`/`put it away`/`put that away`を同時に返す)。
- 層1(抽出): B1(`er138:316-324`)/P7(`er119_kp_p7w5_prompts_01.py:34-41`)が「網羅」と「価値順位付け」を1Promptに混ぜ、小さな件数枠(14/7)で出させる。`in the way`/`in sight`=条件4・5が主因(**高**: 条件除去で3/3)。`put away`/`leave out`=枠内の価値順位付け(**中〜高**: 14個0/3、30個2/3・1/3、網羅3/3、句動詞限定3/3)。
- 層2(選定): 抽出を広げても`pick`(`er138:950-961`、難易度順→上限7)で`put away`が落ちる(2/2)。SELの難易度ラベルは揺れる(`turn into an interrogation` easy/upper、`in sight` upper/easy)。繰り返し(`put away`6箇所)という中心性の信号はPrompt・pickのどちらにも使われていない。
- 最低達成条件には層1と層2の両方の対策が必要(層1だけでは`put away`が最終候補に残らない)。

## 切り分け表の要約(詳細=ROOT_CAUSE_01.md §1)
`put away`=(i)抽出で落ちる+(ii)pickで落ちる(両方)。`in the way`=(i)のみ(抽出されれば採用2/2)。`leave out`=(i)+SELで`leave it out`がF判定の標本あり。`in sight`=(i)主・(ii)ラベル揺れ(1/2)。`force away`=意味判定で除外(妥当)。

## 案の一覧(比較表=DESIGN_OPTIONS_01.md §3、判定はFable)
- E1 B1条件4・5除去(14/30個): `in the way`/`in sight`3/3、`put away`0/3〜2/3(不安定)。費用±0。
- E2 網羅列挙(recall専用)+既存SELで価値判定: 4表現3/3、辞書一致の網羅が本番B1の約3〜4倍。+約¥0.4/level。
- E3 句動詞pass追加: `put away`/`leave out`3/3、`in the way`/`in sight`0/3(単独不十分)。+約¥0.35。
- E4 3分割列挙: 4表現3/3だがE2に対する優位は観測されず。+約¥0.7。
- E5 辞書(WordNet多語見出し)seed: 決定論で4表現を検出(LLM追加0)、ノイズ多め。+約¥0.3(SEL件数増)。
- E6 E2∪E5: 再現性の下限保証。+約¥0.55。
- 選定側P1記録化(挙動不変、原文§6の担当)/P2型昇格/P3出現回数昇格(OPEN-632の集計規則と整合要)/P4 SEL value軸/P5易しいC予約枠/P6 cap見直し。poolpickではR1(型昇格)・R2(出現回数昇格)で`put (it) away`が7件に残った(SEL標本2)。

## Trial費用見積・推奨Cap(TRIAL_PLAN_01.md §7)
Phase 1(untidi Adv N=5+Std N=3)約¥33 / Phase 2(held-out 3記事[X/Y/Z]N=2)約¥26 / Phase 3(再設計予備)約¥33 = **約¥92、委任_02の個別Cap提案¥105**。止め線(累計)¥38/¥68/¥100の各手前で報告。Phase 1+2で基準達成なら実費約¥59。量産単価影響(採用時の見込み)=E2系+約¥0.8/記事セット(70円目標の約1.1%)。事前登録した成功基準S1〜S5・副作用基準N1〜N7はTRIAL_PLAN_01.md §3〜4。

## 使用費用(ledger=`ev01/cost_summary.json`)
**¥9.45 / Cap ¥25(止め線¥20)**。内訳: probe抽出 ¥7.83(gpt-6-luna、33呼出+再試行1)、SEL poolpick ¥1.63。使用モデル=gpt-6-luna(Production既定、最新世代系、旧/下位モデルなし)。

## 空き容量・環境
Cドライブ空き: 開始時 約43.3GB(>5GB のため sparse worktree `scratchpad\wt_n5r`を作成)→ 終了時 約68.8GB(並行回収の影響を含む)。

## 判断候補
1. 【分類D: 新しいTrial範囲・予算】委任_02の費用Cap ¥105(見積約¥92)の承認と、Trialに載せる案セット(A0〜A7)の確定。停止根拠=`TRIAL_PLAN_01.md` §7、ユーザー原文§5(予算は事前申告)、`docs/pm/PM_GOVERNANCE.md` 7-7(未承認Trial範囲は金額無関係に承認)。
2. 【分類D: 承認済み仕様の変更】Trial対象のうち、B1条件4・5の置換(E1〜E4、2026-10-22ユーザー指定の逐語維持条件)およびN5 pick/SEL選定基準の変更(P2〜P5、2026-10-30承認N5方式)は、VALIDATED後の**Production採用時にユーザー判断**(Trial実施自体は未承認Trial経路で可能)。停止根拠=`er138_kp_n5_generalization_01.py:308-310`、`ER-119`系N5採用記録、ユーザー原文§7。
3. 【分類B/C】`gets heated`型の救済QA再判定(OPEN-633)・`things left out`訳(OPEN-634)はFable予約・別系統。本Trialでは触れていない。

## 受入記録用4行
(1) 既存仕様整合: B1条件4・5=`er138_kp_n5_generalization_01.py:308-310`、P7=`er105_kp_fulltext_selector_01.py:60-61`・`er119_kp_p7w5_prompts_01.py:34-44`、pick=`er138:950-961`・`PHRASE_PICK_CAP`=`:47`、SEL方針=`er138:354`、ユーザー原文=`docs/pm/delegation_log/2026-10-31_KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01_USER.md`、前提=`KP-N5-PHRASE-COVERAGE-AUDIT-01/AUDIT_01.md`を照合。
(2) Production到達経路に入る未承認機能: **なし**(新flag・設定dict・環境変数・起動script変更なし。Production module/Prompt/閾値/Gate無編集)。確認=`git diff --name-only origin/main`が`docs/`配下とOPEN_ITEMS.mdのみ。
(3) 失敗終了時の最終成果物: 失敗終了なし(正常完了)。最終成果物=上記`docs/research/KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01/`。ユーザー原文§1「put awayとin the wayの両方を抽出できる方式を確立」には**本委任では未到達(原因究明・設計・計画まで。委任_02で実証)**。原因は特定済みで、probeではLLM網羅列挙で抽出自体は3/3まで確認済み、最終候補残存は層2対策が必要という所までを実証。
(4) 撤去・残置した規則/検査/test: 撤去なし・新規Productionルールなし。Trial専用scriptのみ追加(`tools/probe_extract_01.py`・`pool_pick_probe_01.py`・`dict_seed_probe_01.py`)。残存Grep: `grep -rn "OPEN-635" OPEN_ITEMS.md docs/research/KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01` で参照整合。Dangling Reference: OPEN-633/634(Fable予約、未push)への言及のみ。
判定整合: 重大NG=なし
