# 委任_02e 委任文(逐語保存、T-0)

## 管理ID

OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01(委任_02e: 設計docの改訂。Opus前段スキャン(Part 1)と委任_02dのセンサー品質検証により「決定論検査=方向反転センサー」の前提が崩れたため、設計docへ反映し、代替案を追加する)。**git操作・SSOT編集・コード変更をしない。** 書込先: `docs/pm/design_open233_directional_misread_safety_01.md`、`docs/pm/RESULT_PACKET_DESIGN.md`(更新)、`docs/pm/delegation_log/`。

**作業方式(必須)**: §ごとに別Edit、1回30行以内、箇条書き中心、Bash heredoc不使用、説明最小。T-0は委任文をWrite 3分割で逐語保存。時間目安25分。

## 性質/到達上限Status/禁止事項

- 性質: Safety flow設計の改訂(¥0)。到達上限: DESIGN_READY_FOR_REVIEW候補(採否はOpus Part 2後にFable/ユーザー)。
- 禁止: 残11 run/Production変更/全機械floor復活/一律Checker厳格化/gold・KPI変更/Human Reviewへの安易な振替/有料API/コード・prompt変更/新Safety原則を「決定」として書くこと/数字floor穴の修正。
- Opus Gate: 条件A該当(Part 2をFableが本改訂後に依頼)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う(一覧外は理由記録)。T-0(2026-09-13常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_02e.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ(FAILでも継続)。T-2/T-2追記(7-5): TTSなし。T-3: ¥0のため対象外。

## ユーザー指示(原文、要点)

> 決定論検査=センサーとして専用の独立確認を起動する(ユーザー仮説)。一律floorではない。意味関係のタクソノミーを検討。機械信号は保持。¥0で: HC-012捕捉/既知gold維持/正常文の大量重大化回避/追加確認件数を比較。
> 報告項目: 原因/揺れか系統的読み癖か/専門検査対象タイプ/2〜3案比較/反実仮想/誤爆見込み/追加処理件数/追加費用/推奨案/Opusレビュー/次の限定Trial案。

## 反映すべき新事実(確定)

(a) 委任_02d【確認】: HC-012の`negation_polarity_mismatch`はLedger行「適切な開示なしに」の「なし」(是正案a `STAGE1_NEGATION_MODE="a"`)への偶発反応。向き反転は見ていない。HC-012根拠で英語否定語を持たない肯定文は、忠実文(rolled back)も反転文(restored/expanded)も同じ理由で発火(向きの区別なし)。新9 runのnegation反応39件=問題なし38/重大1(精度1/39)、旧9 run 47件。number/causal反応は新9 runで0件。gold感度: A5-0・HC-012は是正案aの「なし」のみで発火、HF-009(K16/K19)は「ほどなく」の「なく」でlegacyのみ発火。比較・方向専用センサーはcheckerに存在しない。数字floor穴(`number_not_in_fact`がchanged_numberへ未変換、checker L554-555/L640-643)は実在、新9 runで実害0。出典: `er052_output/open233_directional_misread_offline_01/sensor_quality_01.md`。
(b) Opus Part 1【確認/推測はそのまま付す】: (1) Checkerの`issue`/`flags`/`sub_reasons`はStage 2 promptへ渡っていない(calib L652-662)。S1も同入力。DV/Tier0はissueを見るが承認構成でOFF。Recheckの`prior_issues`はBLOCKINGのみ。S-4非BLOCKING再利用(L8765-8775)のキーにsub_reasonsが無く、以降cycleで素通り。出口検査はRewriteがあった記事のみ。再分類filterはmodel由来候補のみ。Rewrite hintに決定論理由名がそのまま入り役に立たない。(2) 潜在不具合: `apply_stage2_two_of_two`(L4106-4122)が`fact:<id>`キーで兄弟文を上書き、現在OFF(L430)。(3) 系統的誤読の型: T1状態変化の向き反転(A5-0/HC-012)、T2推移・比較の向き反転(委任_61/HF-009)、T3当事者取り違え(A4-0)、T4未指定役割の充填(A2A3-0/HF-003)、T5因果・条件の捏造(B3/B4-a)、T6可能性の既成事実化(軽微)。共通核=「語彙はLedgerと大きく重なるが、事象の枠(主体/行為/相手/向き・結果状態/条件)が1つだけ入れ替わる」。(4) 代替案「判定役でなく抽出役」: LLMにLedger側・記事側の枠の値を別々に抽出させ、一致/逆転の比較はPython側で行う(同一モデル相関誤りの遮断)。(5) 最単純案: Stage 2 promptへissue・決定論理由を渡す(priming前例=委任_16あり)。(6) 入力限定に使えるデータ: claim_text/local_context/related_fact_id/unit_ids、`floor_verify_fact_block`、`ledger_block_fields`、DV骨組み(L3584-3628)流用可。取れない: r3の`ledger_quotes`、`support_fact_ids`2件目以降。(7) 失敗時はBLOCKING→Rewrite(Human Review増やさない)、hintに両側の枠を入れる。

## 改訂内容(§番号は既存に合わせる。既存文は削除せず「改訂」「訂正」で追記)

- §1末尾「§1-訂正(委任_02d)」: (a)の反応機構。「決定論信号の喪失」は事実だが、その信号は方向を見ていなかった(保持しても方向反転を拾う根拠にならない)と明記。
- §2末尾: Opus T1〜T6を既存(i)〜(vi)と対応付け(表1つ)、共通核の定義案を追加。第1段対象=T1+T2(枠「向き・結果状態」)、第2段候補=T3+T4(枠「主体・相手」)、T5/T6は対象外の理由。
- §3末尾「案の追加・再評価」: 案E=枠抽出方式(Opus(4)): 対象claimについてLLMがLedger側/記事側の枠を別々に抽出(schema固定・逐語引用付き)、Python比較で一致/逆転/未指定充填/不明を決定。案F=最単純(Stage 2へissue渡し)。比較表を案A〜Fで再掲(Safety/独立性/誤爆/件数/費用/複雑性/HC-012捕捉の根拠が偶然か否か)。案A・Dは「trigger前提が崩れたため、triggerを差し替えない限り推奨不可」と明記。
- §4末尾「trigger再定義(委任_02d後)」: T-A/T-Bは方向非識別(精度1/39、偶然依存)→センサー不適。新候補: T-D=Ledger事実側の分類(fact作成時またはrun開始時に1回、facts数ぶんのcall: 各factが「状態変化・推移・比較を含むか」+向き語を抽出)×その事実に紐づく全claim(記事側の語彙に依存しない)。T-E=fact紐付き全claim(新9 run=123件/9 run≒14/run)に案Eを適用(trigger無し、全件抽出)。T-C語彙は補助。各候補の件数見込み(¥0で既存jsonから計算可能なもの: fact紐付きclaim数、T-C該当数=55。T-Dのfact数・該当比率は未集計→【推測】か「要集計」)。
- §6末尾「訂正」: HC-012「3案ともtrigger」はT-A/T-Bについては偶然(「なし」)による。gold A5-0も同様。T-Cのみ記事側の語(restored)を見ている。
- §7末尾: T-D/T-E/案Eの費用再推計(件数×Stage 2単価比、low/mid/high、【推測】)。
- §8「推奨案(改訂)」: Sonnet所見を更新(決定ではない)。少なくとも「案E(枠抽出+Python比較)をT-D or T-Eで起動、曖昧は別model再確認→QUALITY、失敗時BLOCKING」を候補として、旧推奨Dとの差・理由を明記。ユーザー仮説(決定論=センサー)との関係: 既存決定論検査はセンサーに不適だが「センサー→専用確認」の構造自体は、センサーをT-D(事実側分類)に置き換えれば成立、と整理(【推測】付き、ユーザー判断事項)。
- §9: 限定Trial案を改訂(対象: HC-012 4文[忠実/反転]、A5-0候補3、K16/K19/委任_61合成、新9 runのT-C該当55件またはfact紐付き123件、旧floor誤爆24件。測定: 反転検出/忠実文を「一致」と返す率/枠抽出の逐語引用成功率/曖昧率。費用low/mid/high。STOP条件)。
- §10末尾: Opus Part 1(3)の論点1〜7を追加。
- §13(新設)「Part 1: 信号喪失箇所の整理と潜在不具合」: (b)(1)(2)を表で記録(行番号付き)。数字floor穴は「ユーザー確認事項(承認範囲内の是正か)」、two_of_two潜在不具合は「再有効化前に修正要(今は影響なし)」。
- §12: STOP判定を更新(ユーザー仮説の前提が崩れた=新しい設計判断が必要→USER_DECISION_REQUIRED候補。Opus Part 2後にFable判定)。
- `docs/pm/RESULT_PACKET_DESIGN.md`: 11項目要約を改訂(特に「反実仮想」「推奨案」「誤爆見込み」「追加処理件数」「追加費用」)、SSOT追記文案(OPEN_ITEMS進捗・REPORT §82案・DECISION_LOG案)を更新、成果物一覧にsensor_quality_01.*を追加。

## 事前指定Read/Grep一覧

1. `docs/pm/design_open233_directional_misread_safety_01.md`: Grep `^## |^### ` で構成確認→§1/§3/§4/§6/§7/§8/§9/§10/§12の該当範囲Read(全文1回で可、約270行)。
2. `er052_output/open233_directional_misread_offline_01/sensor_quality_01.md`: 全文。
3. `docs/pm/RESULT_PACKET_DESIGN.md`: 全文。
4. fact紐付きclaim数・fact数: `er052_output/open233_directional_misread_offline_01/trigger_replay_01.json` Grep `n_claims|related_fact|n_facts` →既存集計で取れる値のみ転記(無ければ「要集計」と書く、新規scriptは書かない)。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_02e.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_02e.md_check.json`
2. Editのみ。

## SSOT追記文

なし(文案のみRESULT_PACKET_DESIGNへ)。

## Git

git操作なし。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_DESIGN.md`。最終報告は10行以内(改訂後の推奨案と、USER_DECISION_REQUIRED候補の理由を含む)。

(注: Write 1回で保存。Writeは追記不可のため3分割せず全文を単一Writeで逐語保存した。)
