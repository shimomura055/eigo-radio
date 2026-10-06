## 管理ID

OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01(委任_02b: 設計docの前半§0〜§5の執筆。委任_02はAPI側中断のため分割再開)。並行タスク: 委任_02a(反実仮想replay、`er052_output/open233_directional_misread_offline_01/`・`docs/pm/RESULT_PACKET_DESIGN_A.md`へ書込)。**本委任は委任_02aのファイルを読まない・書かない。git操作・SSOT編集・コード変更をしない。** 書き込み先: `docs/pm/design_open233_directional_misread_safety_01.md`(新規、§0〜§5のみ)、`docs/pm/RESULT_PACKET_DESIGN_B.md`(新規)、`docs/pm/delegation_log/`。

**作業方式(必須・最重要)**: §ごとに別々のWrite/Editで書く(1回あたり30行以内、各§は箇条書き中心で簡潔に)。Bash heredoc不使用。思考・説明文は最小限。T-0の委任文保存はWriteを3分割して逐語保存。時間目安30分。

## 性質/到達上限Status/禁止事項

- 性質: Safety flow設計(¥0)。到達上限: §0〜§5完成(後半§6〜§12は委任_02c)。採否はOpus条件Aレビュー後にFable/ユーザー。
- 禁止(ユーザー指定): 残11 run/Production変更/全機械floor復活/一律Checker厳格化/gold変更/KPI変更/Human Reviewへの安易な振替/有料API/コード・prompt・runner変更/新Safety原則を「決定」として書くこと(提案はユーザー判断事項と明記)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: 条件A該当(Safety flow構造変更、設計後・実装前、必須)。Fableが別途依頼。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read(runner全文Read禁止)。G-1: git出力不使用。F-1: transcript退避不要。T-1: 事前指定Read/Grep一覧に従う(一覧外は理由を記録)。T-0(2026-09-13、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。T-2(2026-09-25): TTSなし。T-2追記(7-5): TTSなし。T-3(2026-09-26): ¥0のため適用対象外。

## ユーザー指示(原文、設計課題部分を逐語)

> 設計課題: 「同じAIにもう一度重大かどうか聞く」のではなく、読み違いの種類そのものを直接検査する仕組みを設計する。特に検討すること：1. 方向反転専用確認(Ledger側では何が起きたのか/Article側では何が起きたのか/両者は同方向か逆方向か、を直接判定させる) 2. 対象となる意味関係(rollback / restore、withdraw / reinstate、increase / decrease、start / stop、expand / shrink、allow / prohibit、approve / reject、add / remove、その他、既存gold・過去事故から一般化できる方向反転。単語リストだけに依存せず、意味関係として一般化できる設計を考えること) 3. Checkerの機械信号の扱い(negation_polarity_mismatch 等の決定論検査が出した警告を、後段AIが単純に消してしまわないようにできるか/強制重大化ではなく、専用追加確認を起動するtriggerとして利用する案を検討する) 4. 独立性(同じmodel/同じrubric/同じ入力をそのまま繰り返す方式は避ける。別Prompt、限定された入力、別model等のどの組み合わせが最も費用対効果がよいか設計する) 5. 最終判定(専用確認で明確な方向反転 → 重大/一致 → 通過/本当に曖昧 → どう扱うか、を提案する)。
> 設計仮説: 決定論検査 = 重大判定器ではなく「専門検査を起動するセンサー」という構造を評価すること。Checkerの機械検査が異常を検知した場合だけ、「この表現は重大か？」ではなく「LedgerではXは撤回されたのか復活したのか。Articleではどちらか。方向は一致しているか？」のように、誤読しやすい一点だけを直接比較する独立確認へ送る。ただし、この案をそのまま採用せず、Claude側でも代替案を検討すること。

## 確定事実(§1に転記、再調査不要)

HC-012 claim(meta_run03_advanced cycle1)「The company also restored the human concierge feature to the way it had been before, at least for now.」: Stage 1 AI=SUPPORTED(routes=r3)、決定論検査`negation_polarity_mismatch`で候補化(`dev.issue`「決定論検査で戻した」)、`changed_*`6フラグ全false、Stage 2=ACCEPTABLE(basis none)、S1=ACCEPTABLE(basis ledger_claim、confirmed_downgrade=True)、floor_reason=None、floor_cited=ACCEPTABLE、最終本文に残存。旧floor全ONでも不発火(フラグ無し)。同型=gold A5-0(HC-012「temporarily put back the feature」)。過去: Stage 2較正V2でA4-0/A5-1 false downgrade→V3修正、B3/A2A3-0誤降格はgold手動照合で発見→自動検知追加(委任_33)。S1は同model・同rubricの再サンプル(runner L4055)。旧time verifyはStage 2と同model(L3010)で「2回確認+逐語引用」方式、委任_61で比較の方向反転がverifyで誤解放され決定論へ戻した経緯(L2760)。

## KPI provenance欄

設計docの事実は上記確定事実(frozen)。反実仮想の数値は委任_02aの出力(本委任では参照しない。§6で委任_02cが転記)。

## Opus台帳更新

参照のみ: `docs/pm/OPUS_FINDINGS_LEDGER.md` Grep `OF-044|OF-04[3-9]|OF-05[0-5]` →ID・要旨のみ(根拠引用用、台帳編集なし)。

## 事前指定Read一覧

1. `er052_open233_self_recovery_flow_runner_01.py`: Grep `SAFETY_CRITICAL_CLAIM_DEFS` →定義ブロック(L9817付近、gold 6件の型)。Grep `def floor_verify_target|verify_prompt|VERIFY_PROMPT` →旧time verifyの問い方の構造(±25行、別prompt方式の前例)。
2. `er052_open233_stage1_coverage_checker_01.py`: Grep `negation_polarity|def _negation|polarity` →決定論検査の実装(±25行、何を比較しているか)。
3. `docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`: L38-L60(23種集計)。
4. `docs/pm/design_open233_self_recovery_flow_01.md`: Grep `重大誤解原則` →§0(1段落)。
5. `docs/pm/OPUS_FINDINGS_LEDGER.md`: 上記Grep。

## 事前指定Grep一覧+追記位置・更新位置の手順

設計doc(§ごとに別Write/Edit、各30行以内):
- §0 前提: 管理ID・Status(設計段階、到達上限)・provenance・禁止事項・「本docは提案であり決定ではない」。
- §1 見逃しの正確な原因: 上記確定事実を表に。揺れ vs 系統の判定: (a)3段階が同一の読み(系統)、(b)S1は同rubric再サンプル=独立でない(相関)、(c)決定論信号が後段で消える構造、(d)n=1のため揺れの寄与は未分離→結論「系統的読み癖+相関構造が主、揺れは副」【推測】。過去同型(A5-0/A5-1/B3誤降格)との関係。
- §2 専門検査対象の意味関係タクソノミー: 単語リストではなく意味関係で定義: (i)極性(polarity: 実施/撤回、肯定/否定)、(ii)方向(direction: 増/減、開始/停止、拡大/縮小、許可/禁止、承認/却下、追加/削除、復元/撤回)、(iii)主体・相手先(agent/patient: A4-0型)、(iv)時間順序・一時性(HF-009型: 一時的縮小→回復)、(v)範囲(B4-a型)、(vi)因果(B3型)。各型に既存gold/過去事故の対応を付ける。第1段の対象=(i)(ii)(ユーザー指定の方向反転)、第2段候補=(iii)(iv)。ユーザー列挙の語対(rollback/restore…)は(i)(ii)の例として位置付け、語彙は「検出の近似」であり判定は意味関係で行う。
- §3 設計案の比較(案A/B/C/D、表): 案A=ユーザー仮説「決定論検査=センサー→方向反転専用の独立確認」(別prompt: 3問[Ledger側事象の極性・方向/Article側/一致・逆転・曖昧]、入力=該当fact+notes+該当文+前後1文のみ、出力schema固定、model=Stage 2と別系統を第一候補・同modelでも別prompt+限定入力を第二候補)/案B=Stage 2 rubricへ「決定論信号がある候補は極性を明示比較」を追加(同model同rubric拡張、独立性低、費用増なし)/案C=Stage 1再分類(4観点)に第5観点「極性・方向」を追加し、不一致なら`polarity_mismatch`をStage 2へ明示的に渡す(前段で信号保持、専用確認なし)/案D=A+C(前段で信号保持+後段で専用確認)。比較軸: Safety(HC-012捕捉見込み・gold維持)/独立性(model・prompt・入力)/誤爆・不要Rewrite/追加確認件数(委任_02aの数値を§6で転記予定と注記)/費用/実装複雑性/retry・fallback・regen整合/既存信号の保持/旧time verify失敗(委任_61)との違い。
- §4 Checker機械信号の保持: 決定論検査の警告を`cycle_record`の「未解消機械信号」として保持し、後段AIがACCEPTABLEにしても消さず、専用確認の起動triggerにする(強制重大化はしない)。triggerの定義候補(T-A: 決定論由来候補×後段非BLOCKING/T-B: T-Aのうち決定論とStage 1 AIの食い違い/T-C: 極性・方向語彙)。専用確認後の信号の消し方(一致→解消記録、逆転→BLOCKING、曖昧→§5)。
- §5 最終判定ルール案: 明確な逆転→重大(BLOCKING→Rewrite、方向語をLedger語へ)/一致→通過(信号解消)/曖昧→選択肢(i)QUALITY記録のみ(ii)限定Rewrite(方向語のみ置換)(iii)別modelで再確認→なお曖昧ならQUALITY。推奨と理由(Human Reviewへの振替は禁止、過剰Safety回避)。「本当に曖昧」の定義(Ledger側の極性自体が不明確な場合に限る)。
- `docs/pm/RESULT_PACKET_DESIGN_B.md`: T-0結果、§0〜§5の要点(各2行)、Opus論点メモ、一覧外Read理由、委任_02cへの引継ぎ(§6〜§12の構成案)。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_02b.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_02b.md_check.json`
2. 設計doc §0〜§5を順にWrite/Edit。
3. git操作なし。

## SSOT追記文

なし。

## Git

git操作なし。SSOT編集権なし。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_DESIGN_B.md`へ上記。最終報告は8行以内。

