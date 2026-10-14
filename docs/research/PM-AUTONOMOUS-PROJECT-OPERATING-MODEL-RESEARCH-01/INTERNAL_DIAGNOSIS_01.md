# INTERNAL_DIAGNOSIS_01: eigo-radio 現行PM運用体制の内部診断(Repo read-only)

- 管理ID: PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01 委任_01B(2026-10-14、JPY0、対象文書・SSOT・Agent定義・Production無変更)
- 位置づけ: 成果物2(運営方式提案)の材料となる「現行Project運用の問題診断」。提案は§5に列挙するのみで、採用判断・実ファイル変更はしない。委任_01A(外部Deep Research)の成果物には触れていない。
- 表記: **[事実]**=Repo内の行・数値で確認済み、**[推測]**=事実からの推論(根拠を併記)。欠陥ラベル: **D**=文書の欠陥、**I**=実装の欠陥(ツール/Validator/runner/権限設定)、**A**=Agent運用の欠陥(Prompt/委任文/判断)。
- 文字数は全てPythonの`len()`による文字数(バイト数ではない)。集計scriptはscratchpad `pmar_b/`(sz.py, sec.py, dl.py, oi.py, udr.py, m.py)。
- STOP確認(開始時): `docs/pm/delegation_log/*STOP_NOTICE*`は2026-10-12 Melos 1件のみ(旧記録、本委任に非適用)。`er026_output/family_z_production_e2e_01/STOP_ALL`なし。API支出なし。

---

## §1 現行体制の構造図と定量サマリ

### 1-1 構造図(テキスト)

```
 ユーザー(人間)
    |  報告ブロック(9-0固定5節 / 9-8マーカー)          ^ 判断(UDR) / 指示原文
    v                                                   |
 Fable = sandwich-pm   tools: Agent(sonnet-worker, opus-consultant), Read, Grep, Glob  (Bash/Edit/Write無し)
    |  読む: CLAUDE.md -> sandwich-pm.md -> PM_BRIEF -> ACTIVE_TASK(28k字) -> 必要時SSOTをGrep
    |  禁止: 自分で編集/実装/調査、er0XX_output/の閲覧
    |  委任文 = DELEGATION_STANDARD_TEMPLATE + 固定ブロックE-1..T-3 + 事前指定Read一覧 + 実行コマンド全文
    +--> sonnet-worker (実行層: 調査/実装/test/SSOT編集/Git) --> RESULT_PACKET*.md / ACTIVE_TASK*.md (一時ファイル)
    +--> opus-consultant (read-only: 条件A-D独立レビュー / L3難問診断) --> OPUS_FINDINGS_LEDGER (OF-208まで)
    +--> haiku-worker (文面上のみ許可。tools欄に記載なし)
 規則の層: CLAUDE.md(4.4k字) / agents/*.md(計8.0k字) / PM_BRIEF(11.2k字) / PM_GOVERNANCE(156.9k字,26節) / templates(約30k字) / 個別委任文
 Gate:     PM Gate1-7 / Closeout Check(項目1-31) / Opus条件A-D / Sonnet上限(初回+3) / STOP_NOTICE,STOP,STOP_ALL / check_delegation_prompt(非blocking)
 記録簿:   CURRENT_SPEC(436k字) / DECISION_LOG(1,328k字) / OPEN_ITEMS(705k字,365行) / *_HISTORY(260k+722k字) /
           UDR_REGISTER(16.7k字,58行) / OPUS_FINDINGS_LEDGER(71k字) / REPORT_LEDGER(106k字,292行) /
           delegation_log(945ファイル,4.58M字) / erNNN_output + ER-*_REPORT / RESULT_PACKET_*(426) / ACTIVE_TASK_*(262)
```

### 1-2 定量サマリ

| 対象 | 文字数 | 行数 | 構造 | 備考 |
|---|---|---|---|---|
| CLAUDE.md | 4,407 | 112 | - | 自動読込。PM層の要約(Opus Gate/上限/Production採用/復帰手順/最新モデル/並列原則)を保持 |
| .claude/agents/sandwich-pm.md | 3,755 | 108 | - | 手順1-8、上限到達時、報告 |
| .claude/agents/sonnet-worker.md | 1,503 | 54 | - | 範囲/Production安全性/検証/報告/禁止/有料run(26節の複製) |
| opus-consultant.md / haiku-worker.md | 1,417 / 1,272 | 46 / 45 | - | |
| docs/pm/PM_BRIEF.md | 11,184 | 289 | 約10節 | 「案内板」だが規則本文を再掲(Opus Escalation/ループ上限/並列原則など) |
| docs/pm/PM_GOVERNANCE.md | **156,897** | 3,898 | **26節+変更履歴、`###`84小節** | 先頭ヘッダ(変更履歴埋込)6,480字、変更履歴節31,222字(20%)、`2026-`を含む行439、「ユーザー(正式)決定/指示/承認」170回、`USER_DECISION_REQUIRED`56回、「並列」85回 |
| 同 節別 | 11節 23,911 / 9節 19,227 / 2節(Gate1-7) 13,155 / 12節 9,391 / 8節 9,735 / 7節 8,375 | | | 上位6節で節本文(変更履歴・ヘッダ除く)の約7割 |
| docs/pm/ACTIVE_TASK.md | 28,247 | 292 | 「## 前タスク群(保持)」32ブロック | 「一時ファイル」だが実質は蓄積ログ。Fableが毎回最初に読む |
| USER_DECISION_REGISTER_01.md | 16,653 | 101 | 58行(UDR系34/判断済み14/他10) | 見出し「35件」、区分別集計「55件」「51件」、実体は58行。集計がずれている |
| OPUS_FINDINGS_LEDGER.md | 71,013 | 235 | OF-1..OF-208 | 有効に機能(§3-1) |
| REPORT_LEDGER.md | 105,851 | 292 | | 各行に定型句「初回報告日未報告(Fable判断)」 |
| OPEN_ITEMS.md | 705,454 | 862 | OPEN行365 | 行長中央値1,092字、**3,000字超32行**(最大43,853字)。T1で定めた「3,000字超は切り出し」が守られていない |
| DECISION_LOG.md | 1,327,614 | 21,020 | `##`428/`###`80 | 2026-10-12〜14のエントリ56件 |
| CURRENT_SPEC.md | 435,817 | 2,675 | `##`34/`###`23 | |
| delegation_log | 945ファイル / 4,576,774字 | | | 2026-10-10〜14分の.md 213件、中央値1,092字、平均2,310字、5,000字超27件、最大40,492字 |
| RESULT_PACKET_*.md / ACTIVE_TASK_*.* | 426 / 262ファイル | | | 一時ファイルがdocs/pm直下に累積 |

**起動時にFableが読む最小セット**(CLAUDE.md + sandwich-pm.md + PM_BRIEF + ACTIVE_TASK + RESULT_PACKET): 4,407+3,755+11,184+28,247+875 = **約48,500字**。その後に必要箇所のGrepが続く。[事実]

**典型委任文の規模**[事実]: XZ-M2P0-N01-WIRING-01 委任_01(全文保存)13,102字(うち事前指定Read一覧2,850字、固定ブロック830字)。COMPLETION-01 委任_01(ユーザー指示原文込み)10,270字。一方、COMPLETION-01の委任_02/_03、M1-OOV委任_03の保存版は1,885字/644字/628字で「要点保存」(固定ブロックは「要点保存のため省略」と明記)。固定ブロック(`DELEGATION_READ_EFFICIENCY_BLOCK.md`)2,491字、標準テンプレート6,158字、Opusレビューブロック3,618字。

**複数箇所に重複する規則**(grep件数、CLAUDE.md / sandwich-pm.md / PM_BRIEF / PM_GOVERNANCE): Opus条件A=1/1/2/12、`最大3回`(Sonnet上限)=1/1/1/7、`1日2回`(任意Opus)=1/1/3/3、`★★★★報告ここから`=1/1/1/4、`USER_DECISION_REQUIRED`=2/5/4/56、`APPROVED_FOR_PRODUCTION`=2/2/2/31。同一規則が最低3〜4層に再掲され、日付つき「更新」注記で層状に積まれている。

**記録の重複**[事実]: 管理ID `FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01` の言及数は DECISION_LOG 20 / OPEN_ITEMS 18 / OPUS_FINDINGS_LEDGER 21 / CURRENT_SPEC 3 / REPORT_LEDGER 3 / UDR_REGISTER 2。1委任の結果が、DECISION_LOG・OPEN・UDR・OF・REPORT_LEDGER・CURRENT_SPEC・FINAL_REPORT・CHECKLIST・RESULT_PACKET・ACTIVE_TASK・delegation_logの**11箇所**に記録される。2026-10-10以降だけで、6つの台帳(OPEN/DECISION_LOG/CURRENT_SPEC/UDR/REPORT_LEDGER/OF)に+1,303行追加。2026-10-12以降のcommit159件中43件がSSOT記録commit。

**check_delegation_promptの実績**[事実]: 全`_check.json`のうちPASS 285 / FAIL 276(FAIL率49%)。**2026-10-10〜14分は PASS 2 / FAIL 22(FAIL率92%)**。RESULT_PACKETで`check_delegation_prompt`に言及する120ファイルのうちFAIL言及78件。ほぼ全ての報告に「FAIL(要点保存形式のため。継続)」と定型で記録されている。

**Sonnet委任上限(初回+3=4回/管理ID)の実績**[事実]: 2026-10-10〜14のdelegation_logで、同一管理IDのファイル数は RISK-FLAGGER-PRODUCTION-WIRING-01=18、FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01=18、ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01=10、FAMILY-X-TTS-ASR-ROOTCAUSE-01=8。一方 FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01は3回で「Sonnet上限到達のため新ID」(COMPLETION-01_01冒頭)として管理IDが切り替えられた。上限は数える仕組みがなく、適用が不揃い。

---

## §2 具体例6件のトレース表

理由コード: K=知らなかった/読んでいない、S=解釈が割れた、C=競合規則が優先された、N=強制力がない、L=コンテキスト圧縮・要点保存で脱落、P=安全classifier/権限に阻まれた、W=設計・検証手順の欠落。

| # | 事例 | 適用されるべき規則 | 実際の振る舞い(出典) | なぜ機能しなかったか | 欠陥 |
|---|---|---|---|---|---|
| T1 | KP候補の短すぎるsource_span(候補ID方式が`source_span=surface_form`)とRule7の契約不整合(OPEN-349、OF-Y1) | PM_GOVERNANCE §14-1 手順4「failure mode一般化」(2026-09-12)、§21 Existing Spec/Prior Trial Check Gate、Gate 4、Opus条件A(WIRING_DESIGN_01は実施済み)、§2-1 Reconciliation | 2026-10-12 Melosで同系統のRule7 INVALIDが4連続(OPEN-310)。OPEN-310は「人称代名詞一般化表とPromptの不一致」の枝に限定し、「担当=Fable、次アクション=ユーザー/Fable判断」の**OPEN候補・リスク**として登録。Z限定の外側retry(`run_kp_with_outer_retry`、通算3)で暫定回避。10-13、WIRING_DESIGN_01のA-iv表は「canonicalization=無変更」と宣言し、Opus条件A必須9件(OF-159〜167)にも契約不整合は出ず。Coffee Stdでspan短小枝(`based on`)が4/4で再現(FIX1_ROOT_CAUSE_01 §2)。調査の結果、過去13ファイル/7パターンに同種INVALIDが既にあった(invalid_census_03) | (a)OPEN起票時に「同一failure modeの別の枝が存在するか」を確認する手順がない(W)。(b)Opus条件Aは「重要論点にスコープを絞って委任」(sandwich-pm手順7)されるため、委任文で「無変更」と宣言された領域は審査対象外になった[推測]。(c)Parity Gateが「canonicalization入力変更の証拠にならない」ことはOF-190で初めて指摘された。(d)OPENは記録簿で作業キューではない(担当/期限/優先度の強制なし) | A(主)+D |
| T2 | 最終英語KPと日本語glossの不一致(`based on interviews`/`～をもとにした`)をG運用STOP、UDR #57(G1/G2/G3)へ(OPEN-352) | §19(自明な修正の自律実施基準)、§14-1、COMPLETION-01_01 §6(2026-10-13枠組み)、sandwich-pm手順8(Opusレビュー後はFable判断で進む) | COMPLETION-01 委任_03でFableが「G運用: 不整合が1件でもあればSTOP。独自にglossを書き換えない」と指定。Sonnetはgloss_check_03.mdで「**軽度**、意味の方向は矛盾しない、`～`は目的語スロットを示す辞書的表記でStd TTSが決定論で『なになに』に変換」と自己評価しつつ、委任文のSTOP文言に従って停止。Fable経由でUDR #57/#58とOPEN-352/353に「USER_DECISION_REQUIRED」として登録 | (a)**STOPをFable自身の委任文が事前に敷設**(軽度でも1件でSTOP)。Workerは委任文に正しく従っただけ。(b)G2は「新工程=新仕様、Opus条件A要」と分類されたが、条件Aは「ユーザー承認Gateではない」(sandwich-pm手順8)ため、Opus→Fable判断で進める経路が文書上あったのに使われなかった(S)。(c)「STOP必須6条件」の曖昧語(QCD影響大/複数の妥当な選択肢)に当てはまると解釈されUDR化(C) | A(主)+D |
| T3 | 同じKP INVALIDを再生成で繰り返し、ユーザーに原因調査を促された(Opus条件B発動→A') | §14-1 手順3(原因切り分け)、§11-3条件B、(COMPLETION-01_01 §2が後から明文化) | WIRING-01 委任_02でStd KP 2 job x 2 attempt=4回INVALID。委任_03のFable補足「Std KP CANONICALIZATION_INVALIDに対しKP job再生成を**1回許可**」。結果は同じrank5『based on』で再INVALID。ユーザー指示(10-13)「再生成を繰り返すのではなく原因を特定」。COMPLETION-01で初めて根本原因(契約不整合)を特定、条件B(OF-Y1〜Y8)で案A'へ | 条件Bの定義は「**修正**しても2回再発」。入力が同一の**再生成は「修正」と数えられず**、条件B・§14の「原因切り分けが先」のどちらにも発火しなかった(S/W)。さらにWIRING_03の委任は「再生成1回」で、原因調査のタスク自体を含んでいなかった(A) | A(主)+D |
| T4 | 音声segmentの検証済み状態が引き継がれない(`--only-segments`でSKIPPED上書き)、UDR #47/#50 | §14-6(PASS済み成果物の不要再実行・上書き禁止、2026-10-11)、§11自明な修正、Gate 3 | §14-6自身が「**新機構は実装しない運用ルール**」と明記(PM_GOVERNANCE L2763)。OPEN-346②(10-13起票)は「V5委任でも同様、本委任では未修正」「修正は新仕様候補=ユーザー判断」と記録。Adv正式assembleがAudio Validation GateでBLOCK。ユーザー指示(10-13)で「開発側が自律的に実施」と是正され、COMPLETION-01で`er019_family_x_validation_inheritance_01.py`(REUSED_VALIDATED)+runner修正を実装 | (a)§14-6は文書のみで機構が無い(N)。(b)runnerの既存欠陥が10-12のV5で既知となりながらOPEN候補止まり(OPENは作業キューではない)(A/I)。(c)バグ修正を「新仕様候補」と誤分類(S) | I(主)+A |
| T5 | 承認済みN01の音声再生成(Std Part2のfallback take等)について逐次ユーザー判断を要求(UDR #47) | §7-7(Trial JPY100以下はFable承認)、§19(追加費用目安100円以内)、auto-memory「小額API支出で聞かない」、承認済みN01(10-13) | WIRING-01 委任_03のFable補足「Std part2(fallback take, M3 Gate BLOCK)は**再生成せずユーザー判断事項**」。UDR #47に「追加KP再生成の可否[約JPY1]」「fallback takeの人間承認か再生成か」と記載。ユーザー是正(COMPLETION-01_01 §4)「通常の再生成費用について逐一ユーザー判断を求めない」 | 費用・承認の自律規則は複数あるが(§19, 7-7, 7-8, §11, 26節)、**委任文側で判断事項として先に切り出す設計**が優先された(C)。規則が5箇所に分散し、どれが現行か探索が必要(D)。auto-memoryはFable相当のagentに常に載る保証がない[推測] | A(主)+D |
| T6 | M1 evidence runnerが旧STOP_NOTICE(別管理ID)のglob一致で停止しユーザー判断へ。Coffee側agentは同じNoticeを非適用と解釈して続行 | sonnet-worker.md「`*STOP_NOTICE*`の存在を確認、存在すれば新規API呼出をしない」、§26-2(d)「**該当管理ID**のSTOP NOTICE」、§26-4(Family Z以外は機械的阻止未展開) | M1: runnerのSTOP glob `docs/pm/delegation_log/*STOP_NOTICE*`が他管理IDの通知に一致し`--execute`を実行せず(commit 130e0133)、「globを狭める変更はSecurity Weaken判定で拒否された」ためFable/ユーザー判断待ち(RESULT_PACKET_M1OOV)。Coffee側(RESULT_PACKET_XZC)は委任文に「Melos旧STOP_NOTICE=非適用」と明記され継続。runnerを横断すると、同じ確認を少なくとも5通りに実装(全一致/`*KP-INTEGRATED*`等の名前付き/STOP_NOTICEを無視/`OLD_STOP_NOTICE_KEY`除外 等) | (a)STOP_NOTICEは**スコープ・有効期限・解除の機構がなく**、ファイルが残る限り永久に全体へ一致する(I)。(b)M1の委任_03は「固定ブロックは要点保存のため省略」で、非適用の明記が委任文に無かった(L)。(c)Worker側のclassifierは解釈変更を許さず、Fableが解釈を一元化する仕組みも無い(P) | I(主)+A |

補足(T1〜T6の共通点)[事実]: 6件すべてで、**既存規則は存在していた**(§11自明な修正=2026-09-09、§14=09-12、§19=09-17、§14-6=10-11、26節=10-12)。規則が無かったのではなく、(1)規則が委任文・agent定義に伝わらない、(2)STOP/UDRの閾値が曖昧、(3)記録簿が作業キューとして機能しない、(4)機構が文書止まり、のいずれかで機能していない。

---

## §3 調査項目1〜9の結果

### 3-1 既に存在する有効な規則(機能している証拠つき)

1. **Opus独立技術レビューGate(PM_GOVERNANCE 11-3、条件A〜D)**: [事実] OPUS_FINDINGS_LEDGERはOF-1〜OF-208(207件)。2026-10-13だけでWIRING-01条件A/C(OF-159〜167、MAJOR 9件: demoted_allowの方式、M1パラメータ明示、Parity Gate、M2例外の別reason_code、予算Guard全stage合算 等)、COMPLETION-01条件A(OF-188〜200)・条件B(OF-201〜208)。条件Bは実際にT3の「再生成の反復」を止め、案A'(候補ID方式全itemへ右方向原文窓5語)へ誘導した。実装レベルの指摘(OF-191 `--apply`のexpected_text必須化 等)が反映されている。**現行規則の中で最も機能している**。
2. **26節/26-5の機械的STOP(Family Z runner)**: [事実] `STOP_ALL`、`RUN_LOCK.json`二重起動拒否(rc=4)、RESTART_STORM自動STOP、各API呼出前のSDK入口wrap。2026-10-12事故(約JPY71の旧仕様TTS)の再発防止として文書規則(26-2)と**コード側阻止(26-5)の両方**を置いた例。他FamilyのrunnerへはM1側でglob実装が個別に存在する程度(T6)。
3. **コミット前のsecret scan(26-X、`tools/secret_scan_01.py`)**: [事実] 各RESULT_PACKETに`secret_scan hits=0`の記録が連続して存在(XZC委任_02/_03など)。ツールがあり、報告項目に組み込まれている。
4. **Production採用はユーザーのみ(`APPROVED_FOR_PRODUCTION`)/Trial結果の格上げ禁止**: [事実] 10-13の全RESULT_PACKETで「PRODUCTION_WIRED不付与」「Production無変更」が一貫して明記。CLAUDE.md・sandwich-pm・sonnet-worker・PM_GOVERNANCE 2節で多重に書かれ、実際に逸脱は見つからなかった。(多重記載のコストは3-8)
5. **Gate迂回の拒否(Audio Validation Gate、Rule7、M3)**: [事実] WIRING-01 委任_03/COMPLETION-01で、BLOCK/INVALIDを迂回せず停止した。安全性は保たれている(ただし「止まった後の動き」が弱い、3-4)。
6. **コスト上限Guardrail文言(T-3)**: [事実] COMPLETION-01_03「到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的ならば超過を記録して継続。暴走疑い時のみSTOP」。2026-10-05ユーザー指示(§11冒頭)の具体化で、STOP基準が絞られている好例。
7. **Managed-ID trailer・明示add・`git add -A`禁止**: [事実] 10-13のcommit履歴(例: 0696f68d, 13044f19)は「管理ID 委任_NN:」で統一。追跡性が高い。
8. **ユーザー指示原文の逐語保存**: [事実] COMPLETION-01_01の「ユーザー指示(原文)」節、Gate 2の「承認は原文全文をDECISION_LOGへ転記」。2026-10-13の「開発側責任」枠組みの出典はこの逐語保存でのみ確認できた(3-6)。

### 3-2 守られていない規則と実例

[事実] §2のT1〜T6を参照。追加の実例:
- **§11冒頭(2026-10-05)「Fable/Workerが独自に過度に厳しい停止条件を追加しない」** vs 委任文が敷設するSTOP: COMPLETION-01_02「canonicalization REVIEW_REQUIRED/INVALID再発」「新しい許容ルールが必要」、_03「kp_extends_beyond_candidate itemのgloss不整合」。STOP条件はユーザー承認値超過と構造的Wasteに限る、という規則と矛盾。
- **§11 自明な修正(2026-09-09)/§14(2026-09-12)/§19(2026-09-17)/10-13枠組み**: 同趣旨の「自明な修正でUDRにしない」が4回言明されている(09-09, 09-12, 09-17, 10-13)。それでも10-13に再発 = 規則の追加では直らなかったことの直接証拠。
- **§14-6(PASS済み成果物の再実行・上書き禁止)**: 10-11に違反事例(RISK-FLAGGER委任_15〜17のMETA b1b comment_2上書き)、規則化(10-11)の2日後に同種の`--only-segments`上書きがUDR化(T4)。
- **ループ上限(初回+3)**: 3-5・§1-2参照(18件/ID)。
- **OPEN_ITEMS行3,000字上限(T1、2026-09-10)**: 現在32行が超過(最大43,853字)。
- **UDR_REGISTERの区分別集計**: 見出し35件・集計55/51件・実58行。PM_GOVERNANCE 12-13「報告前にSSOTと照合して更新」を満たしていない。
- **sandwich-pm.md手順7/8・上限到達時**: ACTIVE_TASK冒頭(Melos)は「本管理IDのSonnet委任は上限4回に到達(追加はUSER_DECISION_REQUIRED)」と記載。上限到達=自動UDRの文面が、10-13のユーザー枠組み(「作業が必要だからという理由でUDRとしない」)と衝突(3-3の矛盾1,4)。

### 3-3 相互に矛盾・競合する規則

| # | 規則A | 規則B | 実害 | 欠陥 |
|---|---|---|---|---|
| 1 | sonnet-worker.md L24「新しい仕様候補は実装せず報告(既存SSOTの`USER_DECISION_REQUIRED`文化を踏襲)」、L14「拡大が必要なら…**Fableまたはユーザーへ**報告し判断を仰ぐ」 | 10-13枠組み(COMPLETION-01_01 §6)「作業が必要だからという理由でUDRとしない」、§11/§14/§19 | Workerの「迷ったら上げる」既定動作が自律規則を上書き。T2,T4,T5。グレーゾーン(バグ修正か新仕様か)の判定基準がWorker側定義に無い | D |
| 2 | sandwich-pm.md L97「**候補セクション制**(adaptive reporting)で報告」 | PM_GOVERNANCE §9-0「**固定5節順**(2026-10-05、最優先)。候補セクション制(9-1)は**廃止**」+9-8マーカー+9-9の6項目+9-5の7項目 | 実質4種類の報告形式が文書に併存。agent定義は廃止済み形式を指示。報告形式違反が2026-10-05と10-12に再発(auto-memory feedback_report_marker_format)した一因 | D |
| 3 | STOP確認義務(sonnet-worker: `*STOP_NOTICE*`の存在でAPI停止) | §26-2(d)「**該当管理ID**の」、委任文「旧記録=非適用」、STOP_NOTICE自体に有効範囲欄なし | T6。Worker間の解釈が割れ、runnerは少なくとも5通り | D+I |
| 4 | 上限到達=`USER_DECISION_REQUIRED`でSTOP(sandwich-pm L83-89、PM_BRIEF、§11) | 10-13枠組み「開発側完遂責任」、§19「念のため確認はUDRにしない」、実績(18件/ID、新ID発行で上限回避) | 上限が(a)名目的、(b)到達時にユーザー負荷化、(c)新ID発行で回避、の3経路。ユーザー指摘「担当は完遂せよ」とも逆向き | D+I |
| 5 | sonnet-worker.md L35「新しい証跡置き場を勝手に作らない」 | 実態: 管理IDごとに`erNNN_output/`が増える(er071〜er077)、`docs/pm/design_*`・`docs/pm/reports/`・`delegation_log`・`ER-*_REPORT.md`・本委任の`docs/research/` | 「既存構造」の定義が不明確。Workerは毎回「新規dirか既存構造か」を自問 | D |
| 6 | sandwich-pm手順8「Opusレビュー後はFable判断で進む(Opusレビュー自体をユーザーGateにしない)」 | G2を「新工程=新仕様、Opus条件A要」としてUDR化(T2) | Opus条件Aが「ユーザー判断前の前提」と誤読されやすい | A |
| 7 | 並列原則(8-X、CLAUDE.md)「独立作業は原則並列」 | 8節「commit/pushを伴うタスクは同時に1つだけ」、本委任のG-1(index.lock回避のためcommit禁止) | 並列化のたびにagent単位の例外禁止が委任文に書かれる。並行agentとの領域分離を委任文ごとに手書き(COMPLETION-01_01「並行タスク(領域分離)」) | I |
| 8 | PM_BRIEF「案内板、規則本文は複製しない」(CLAUDE.md) | PM_BRIEFがOpus Escalation・並列原則・ループ上限を複数段落で再掲 | 一箇所を更新しても他が古くなる(例: 「ループ上限」「任意Opus 1日2回」が4文書) | D |
| 9 | sandwich-pm L13「haiku-workerも委任可」 | 同L4 tools欄は`Agent(sonnet-worker, opus-consultant)`のみ | 文面は3 Agent、権限は2 Agent。haikuは実質呼べない可能性 | I |
| 10 | 「エラー再発だけでユーザーに戻さない」(COMPLETION-01_01 §2) | 同じ委任文のSTOP条件欄「canonicalization INVALID再発」など(委任_02) | 同一Fableが書く委任文内で矛盾 | A |

### 3-4 自律性を不必要に制限している規則

1. **STOP必須6条件の曖昧語**(§11 L1860-1868、低コストTrial節の同型6条件): 「QCD影響が大きい変更」「複数の妥当な選択肢がありユーザー価値判断が必要」「Production挙動の意味的変更」。バグ修正でも設計案が複数あれば該当しうる。T2のG1/G2/G3、OPEN-349の(A)〜(E)は、いずれも**解決後に見ればFable+Opusで判断可能**だった(案A'は委任_03でユーザー判断なしに実装された)。[事実] UDR #56は「Fable判断・Opus条件B/A」と自称しながらUDR扱い。
2. **STOP文言の事前敷設**(T2,T3): 委任文のSTOP欄に「再発」「軽度でも1件」を置くと、Workerは調査を続ける権限を失う。
3. **Sonnet委任上限→自動UDR**(sandwich-pm/PM_BRIEF/§11): 「上限到達=ユーザー判断」の既定が、Fableに「別手段で解く(Opus診断・方針転換)」より「ユーザーへ戻す」を選ばせる。
4. **難問診断(L3)後は「実装が必要なら人間ユーザーの判断を仰ぐ」**(sandwich-pm L79-81): 診断結果から実装まで自動で進まない規則。
5. **Fableのtools制限とer0XX_output閲覧禁止**(sandwich-pm L4, L29): Fableは検証を自分で再実行できない(Bashなし)。調査の主導には「委任→待つ」しかなく、受け取った報告の独立検証(再計算・再集計)ができない。[推測] T1で「18件」(OPEN-349)が「7パターン/13ファイル」(OF-207)と訂正された例のように、報告内数値の独立確認が構造的に困難。
6. **「Trial実装をProductionへ混入させない」「新しい仕様候補は報告」(sonnet-worker)** 自体は妥当だが、「改善Trial」(§14-1手順5、§7-8探索Trial一括承認)と「新仕様候補の発見」の境界が書かれておらず、Workerは常に上側(報告)に倒れる。
7. **セキュリティ権限(classifier)がrunnerのSTOP glob修正を拒否**(T6): 規則の解釈をWorkerが修正できない場面で、Fableが決める経路が無い(P)。

### 3-5 形式的な手続きが過剰な箇所(定量)

| 項目 | 数値 | 観察 |
|---|---|---|
| 固定ブロックE-1/D-1/G-1/F-1/T-0〜T-3 | ブロック2,491字、委任文1通ごとに830字で再掲 | 内容は「再読しない/Grepで範囲読み/git出力最小化」などWorker共通動作。agent定義(sonnet-worker.md 1,503字)に1回書けば足りる性質 |
| 事前指定Read一覧+実行コマンド全文 | 一覧2,850字(WIRING-01_01)。コマンド全文節 | Fableはtools上Bashを持たず、コマンドの実行可否を検証できないまま全文を書く [推測] |
| T-0保存+check_delegation_prompt | FAIL率49%(直近92%)、非blocking | 要点保存した時点で必須節が欠落するため、運用上**必ずFAILする設計**になっている。PASS/FAILが情報を持たない |
| 一時ファイルACTIVE_TASK/RESULT_PACKET | 262/426ファイル、ACTIVE_TASK.md 28,247字、「前タスク群(保持)」32ブロック | 「一時ファイル」の名目だが累積。compact復帰用の固定ヘッダ(UDR件数「35件」等)が古いまま |
| 二重・多重記録 | 1委任あたり11箇所 | §1-2。DECISION_LOG(委任1回あたり約1,600字)、OPEN行、UDR行、OF行、REPORT_LEDGER行、CURRENT_SPEC、FINAL_REPORT、CHECKLISTに同内容が展開 |
| REPORT_LEDGER | 292行、定型句「初回報告日未報告(Fable判断)」 | 各行が最後に追記される形式で、未報告状態の管理より履歴列挙になっている |
| UDR_REGISTER | 58行中、UDR系34。ブロックUDR2のみ | 「次工程をブロックするUDR」節は#1のみ記載、本文表では#47/#50/#57が「はい」。節と表が不整合 |
| 報告形式 | 9-0(5節)/9-1(候補)/9-5(7項目)/9-9(6項目)/9-8マーカー+Closeout項目31 | 報告ごとに複数形式の同時充足が必要で、形式違反の指摘が繰り返される(feedback memory) |
| 委任上限の記述 | CLAUDE.md/sandwich-pm/PM_BRIEF/§11/§12で5回 | 実績は上限を超えて運用されている |

### 3-6 実際には強制力のない規則

| 規則 | 強制手段 | 証拠 |
|---|---|---|
| Sonnet委任上限(初回+3) | なし(人手カウント) | 18件/ID、ID再発行 [事実] |
| STOP_NOTICE確認 | Family Z runnerのみコード化(26-5)。他はrunnerごとの任意実装 | 5通り以上のglob実装 [事実] |
| check_delegation_prompt | 非blocking | FAIL 276件が継続運用 [事実] |
| §14-6 上書き禁止 | 「新機構は実装しない」と明記 | T4 [事実] |
| 報告マーカー(9-8) | なし(auto-memoryとagent定義の文言のみ) | 2026-10-12に再発しmemoryが追加された [事実]。hooks設定なし(`.claude/settings.local.json`にhooks=0、`.git/hooks`は空) |
| OPEN_ITEMS 3,000字上限 | なし | 32行超過 [事実] |
| UDR_REGISTER更新(12-13) | なし | 集計がずれ [事実] |
| 2026-10-13「開発側責任」枠組み | **規則ファイルに存在しない** | `開発側が自律的に実施`/`開発側責任`をCLAUDE.md・PM_GOVERNANCE・PM_BRIEF・agents/*.mdでgrepして0件。DECISION_LOG/OPEN/UDR/委任文にのみ存在 [事実] |
| 「ユーザー向け報告は両マーカー確認」 | 自己確認 | 2回違反歴 |
| `.claude/agents`の各定義 | ツール制限はClaude Code側で強制 | 例外: tools欄は強制力あり(これが3-4-5の制約も生む) |

### 3-7 FableとWorker間の責任・権限の隙間

1. **宛先の二重化**: sonnet-worker.md L14「Fableまたはユーザーへ報告し判断を仰ぐ」。Workerは宛先を選べず、結果として`RESULT_PACKET`の「要判断」欄に書き、Fableが「ユーザーへ」を選ぶ連鎖(XZC委任_02「要判断: OPEN-349/350」、委任_03「要判断: UDR #57/#58」)。Fableの受入手順(sandwich-pm手順4,6)は「ズレがあれば修正指示」だが、「Worker提案の判断項目を**Fableが自分で決める**」基準はない。
2. **原因調査の責任主体が未定義**: sonnet-worker.mdに「原因調査を行う/自律是正する」記述がない([事実] `原因`はrc≠0の1箇所のみ)。§14-1手順3は「PM処理原則」でFable向けだが、Fableはtoolsに調査手段がない(Bash/編集なし)ため、委任文を介してのみ実行できる。結果、**「原因を調べる」は委任文に書かれなければ発生しない**。T3で委任文が「再生成1回」だったのが典型。
3. **Opusレビュー結果の採否**: 手順8は「照合のうえFable判断」を定めるが、採否の根拠記録は`OPUS_FINDINGS_LEDGER`(採用/不採用)に存在。有効(3-1)。一方、Opusに渡す論点をFableが絞る運用のため、論点漏れ(T1)は上流のFable判断に依存する。
4. **Fableの判断記録**[事実]: (a)WIRING-01_03「Std part2は再生成せずユーザー判断事項」(Fableが先に切り出し)、(b)同「KP再生成1回許可」、(c)COMPLETION-01_03「G運用: 1件でもSTOP」、(d)UDR_REGISTERの#56〜58が「(Fable経由)USER_DECISION_REQUIRED」(自分で決められる可能性を併記しつつ上げた)、(e)OPEN-310「担当=Fable、次アクション=ユーザー/Fable判断」(2026-10-12時点で原因調査を指示した記録なし)。→ ユーザー指摘8(転送役への偏り)は[事実]として裏付けられる。ただしFableには調査手段がなく(3-4-5)、これは個人のAgent運用だけでなく構造の問題でもある。
5. **ユーザー指示の取り込み経路**: ユーザーの一般方針(例: 10-13枠組み)は、そのときの委任文に引用されるだけで、次の委任文にはFableが毎回自分で再引用しない限り伝わらない(M1-OOV委任_03: 「ユーザー指示原文は_01参照」)。Workerがセッションをまたいで継承するのはagent定義とCLAUDE.mdのみ。
6. **STOP解除/閉鎖の権限**: STOP_NOTICEの閉鎖手順がなく、Fableが「非適用」と書く権限は暗黙(26-3(f)はSTOPセンチネルの解除のみ言及)。T6。
7. **安全classifierとPM規則の境界**: M1 Workerが「Security Weaken」で拒否され、Fableに戻した。これは設計上妥当だが、**Fableがその判断を行える経路・基準**が書かれていない(runner側の個別解釈変更をどう許可するか)。

### 3-8 長大なcontextや指示の重複による問題

- **Fable起動時48,500字**(§1-2)。うち28,247字(58%)はACTIVE_TASK.md([事実])。PM_BRIEF 11,184字は「案内板」と自称しつつ規則本文を再掲。
- **PM_GOVERNANCE 156,897字**は節単位の参照(Grep)前提。しかし節内に「2026-xx-xx追記」が層状に積まれ、同じ節で「現行の扱いは11-3節」と他節へ参照する形式(11節冒頭・MODEL ROUTING・L2事前レビューなど)が多く、現行規則を知るために複数箇所を辿る必要がある。11節だけで23,911字、`###`小節を含む。
- **重複規則のメンテコスト**: 一つの規則変更が最大4文書(CLAUDE.md, sandwich-pm, PM_BRIEF, PM_GOVERNANCE)+委任テンプレートに波及する。2026-10-12の報告マーカー再徹底(`PM-REPORT-MARKER-RECURRENCE-PREVENTION-01`)は、agent定義/CLAUDE.md/PM_GOVERNANCE 9-8-1/PM_BRIEF/DECISION_LOG/auto-memoryの**6箇所**を更新した(REPORT_LEDGER記載)。それでも遵守は強制されていない。
- **規則数と実行層**: Workerが実際に読む規則文書(CLAUDE.md+sonnet-worker.md+委任文)は約6k字+委任文(1〜13k字)。PM_GOVERNANCEを読む前提の規則は、委任文に転記されない限りWorkerに届かない([推測]: M1 STOP解釈・Melos 委任_10の「指示文にSTOP/仕様変更の記載が無く」(10-12 委任_10報告)が同型)。つまり**PM_GOVERNANCEの規則の大半は事実上Fableしか読まないが、Fableはそれを実行する手段(調査・実装)を持たない**。
- **コンテキスト圧縮**: compact復帰手順(CLAUDE.md)は(1)ACTIVE_TASK、(2)PM_BRIEF、(3)SSOT再照合と定めるが、復帰後にユーザー枠組み(10-13)が記録されている場所は委任文・DECISION_LOG・UDRのみ(grep上)。復帰手順の読み先にその内容がない。

### 3-9 ルール追加ではなく削除・統合すべき箇所

§5-1にまとめる(根拠は上記3-3, 3-5, 3-8)。

---

## §4 根本原因の分類(文書/実装/運用)とユーザー指摘1〜10との対応

### 4-1 根本原因一覧(25件、主ラベル)

| ID | 根本原因 | 主ラベル | 根拠 |
|---|---|---|---|
| R1 | 10-13「開発側責任/ユーザー判断」枠組みが規則ファイル(CLAUDE.md/PM_GOVERNANCE/agents)に昇格していない | D | 3-6 |
| R2 | STOP必須6条件が曖昧語(QCD影響大/複数案/意味的変更)で、バグ修正設計案でも該当しうる | D | 3-4-1 |
| R3 | sonnet-worker/sandwich-pmが「UDR文化」「上限到達=UDR」を既定とし、自律規則(§11/§14/§19)に言及しない | D | 3-3-1,4 |
| R4 | Fableの責務定義(§1)に原因分析・優先順位付け・問題解決の主導が無い(Gate判断・STOP・報告のみ) | D | §1 L136-139 |
| R5 | Fableのtools(Bash/Edit無し、er0XX_output閲覧禁止)により、独立検証・調査が構造的に不可能で中継役になる | I | sandwich-pm L4,L29 |
| R6 | STOP_NOTICEにスコープ/期限/閉鎖の機構がなく、runnerが少なくとも5通りに実装、Z以外は機械的阻止なし | I | T6, 26-4 |
| R7 | check_delegation_promptが非blocking・形式のみ・要点保存と衝突し、FAIL常態化 | I | 3-5 |
| R8 | 委任文の要点保存でSTOP情報・固定ブロック・ユーザー指示が脱落(Melos委任_10、M1委任_03) | A | T6 |
| R9 | 委任文にSTOP条件/ユーザー判断事項を事前敷設する癖(再発でSTOP、軽度でも1件でSTOP) | A | T2,T3,T5 |
| R10 | 同一入力の「再生成」を修正と数えず、条件B・§14手順3が発火しない | A | T3 |
| R11 | failure mode一般化(§14-1手順4)をOPEN起票時に適用せず、OPENが作業キューにならない(担当・期限なし) | A | T1, T4 |
| R12 | 設計時の契約整合確認(候補ID方式x canonicalization)がWIRING_DESIGNで「無変更」宣言のままOpus審査の対象外 | A | T1 |
| R13 | runnerの既存欠陥(`--only-segments`)がV5(10-12)で既知となりながら未修正 | I | T4 |
| R14 | 記録11箇所の二重記録、UDR_REGISTER集計の陳腐化 | D | 1-2 |
| R15 | OPEN_ITEMS/DECISION_LOGの肥大(3,000字ルール不遵守32行)、lint無し | D | 1-2 |
| R16 | PM_GOVERNANCEの層状パッチ(26節+84小節、変更履歴20%、他節参照の連鎖) | D | 1-2 |
| R17 | 報告形式の併存(候補セクション制 vs 固定5節 vs 7項目 vs 6項目)とagent定義の旧形式指示 | D | 3-3-2 |
| R18 | ループ上限の計数機構なし、ID再発行で回避可能、到達時UDRが既定 | I | 1-2, 3-3-4 |
| R19 | STOP_NOTICEの適用解釈がagent間で割れる(sonnet-worker/§26/委任文の3層) | A | T6 |
| R20 | 自律権限の基準が多重定義(§11, 7-7, 7-8, 14-3, 19, 26, 10-13枠組み, UDR 4区分)で現行が不明 | D | T5 |
| R21 | UDRの誤用(確認・記録型: #53「実装済み記録、異議時のみ差戻し」、#55「分離宣言の確認」、Fable判断可能な#56〜58) | A | UDR表 |
| R22 | Fableが「要判断」をそのままUDR化してユーザーへ転送 | A | 3-7-4 |
| R23 | Worker報告先が「Fableまたはユーザー」の二宛先で責任主体が不定 | D | sonnet-worker L14 |
| R24 | 証跡置き場の規則(新規作成禁止)と実態(管理IDごとにerNNN_output増加)の乖離 | D | 3-3-5 |
| R25 | Worker側の安全classifierとFableの解釈権限の境界が未定義(M1 glob修正拒否) | I | T6 |

主ラベル比率: **D=11(44%)、I=6(24%)、A=8(32%)**。ただし二次ラベルを含めると多くが複合(T1〜T6の主+副のうち、Aに関与するのは5/6件、Dに関与するのは5/6件、Iに関与するのは3/6件)。[推測] Aに分類した8件の多くは、Dの修正(R1,R3,R4,R20)が先に行われれば再発頻度が下がる性質で、「運用の欠陥」のうち判断のミスと言い切れるのは少数である(例: R9は委任文テンプレートがSTOP欄を必須にしているため生じる面がある)。

### 4-2 ユーザー指摘1〜10との対応

| # | ユーザー指摘 | 主に関与する根本原因 | 補足(根拠) |
|---|---|---|---|
| 1 | 明らかな不具合でも都度仕様確認 | R1, R2, R3, R9, R20, R21 | 自明修正規則は4回言明済み(09-09/09-12/09-17/10-13)。再発は規則不足ではなく、曖昧閾値と既定動作(UDR文化)が原因 |
| 2 | 原因を調べず失敗結果だけ報告してSTOP | R4, R5, R8, R9, R10, R22 | 「原因を調べる」は委任文に書かれなければ発生しない(3-7-2)。T3 |
| 3 | 原因調査が浅く部分修正を提案 | R10, R11, R12 | OPEN-310を人称代名詞の枝に限定、Z限定の外側retry、機能語限定の拡張→案A'(OF-201で「機能語末尾限定では再発」を指摘) |
| 4 | 効果・副作用・Regression検証が不十分なまま提案 | R12, R7, R13 | Parity Gateが入力変更の証拠にならない(OF-190)、OPEN-349の件数誤り(18件→7パターン/13ファイル、OF-207)。Opus条件Aが論点の絞りに依存 |
| 5 | QCD不考慮・その場限りの対策 | R9, R10, R11 | Z限定retry、再生成1回上限、費用¥1の判断をユーザーへ(T5)。QCD観点は§23/OPEN-233系にあるが、委任時の必須項目ではない |
| 6 | 量産性・運用コストを考えずHuman Review常態化 | R2, R21, R22 | 規則は§14(2026-09-12)にあるのに、HR関連はUDR#10/#35でユーザー個別承認が続いた(Melos HR個別承認)。`human_review_queue.jsonl`76行(audio_retry_cascade)。量産性評価がHR採否の判断基準に入っていない [推測] |
| 7 | 局所最適、Project全体との整合を見失う | R4, R11, R12, R14, R16 | 各管理IDの委任文は自己完結し、全体優先順位(OPEN-3xxの一覧上の位置づけ)を決める役割・文書がない。UDR58件の優先順位付けを誰も持たない |
| 8 | Fableが転送役に偏る | R4, R5, R22, R23, R8 | 責務定義・toolsともに中継向き。3-7-4のFable判断記録 |
| 9 | 厳格なSTOP・承認GateがTrialや調査まで阻害 | R2, R9, R6, R18, R19, R25 | STOP条件の事前敷設、STOP_NOTICE永久一致、Security classifier、上限=UDR |
| 10 | 毎回ユーザーが技術的な進め方を指示 | R1, R3, R20, R4 | 10-13の指示は§6「開発側が自律的に実施する事項」10項目を含む長文で、規則ファイルでなく委任文にしか残らない。指示の再入力が不可避 |

---

## §5 提案列挙(採用判断・実ファイル変更はしない)

### 5-1 削除・統合候補

1. **報告形式の統合**: §9-0(5節)に一本化し、9-1(廃止宣言済み)・9-5・9-9の旧形式と、sandwich-pm.mdの「候補セクション制」指示を除去する(R17)。
2. **自律権限基準の単一化**: §11「自明な修正の自律実施」・低コストTrial節・§14-3・§19・7-7・7-8・26節の判断基準・10-13枠組みを1節(「Fable/Workerが自律で実施する事項/ユーザーに必須な事項」)へ統合し、他は参照のみとする(R1, R20)。
3. **Closeout Mandatory Check(項目1-31)・Gate 5/6/7**の重複項目(未回答再掲・UDR確認・Status確認)を一覧1つへ統合(R14, R16)。
4. **記録の二重化の削減**: 1委任の結果を、(a)1つの詳細報告(`ER-*`/`erNNN_output/FINAL_REPORT`)+(b)台帳への1行ポインタ、に限定(DECISION_LOG/OPEN/UDR/OF/REPORT_LEDGERの本文再展開を廃止)(R14)。
5. **PM_BRIEF/CLAUDE.mdからの規則本文の再掲削除**: Opus Escalation・並列原則・ループ上限・最新モデル原則の本文をPM_GOVERNANCEに一本化し、PM_BRIEF/CLAUDE.mdは「参照先1行」へ(R14, R16)。
6. **固定ブロックE-1/D-1/G-1/F-1/T-0〜T-3**を、委任文への再掲からagent定義(sonnet-worker.md)側の常設指示へ移す(委任文ごとに2,491字×回数を削減)(R8)。
7. **ACTIVE_TASK.md「前タスク群(保持)」32ブロックの圧縮**(Fable起動時の58%)と、`RESULT_PACKET_*`/`ACTIVE_TASK_*`(計688ファイル)のアーカイブ化(R14)。
8. **PM_GOVERNANCEの変更履歴節(31,222字)とヘッダ内埋込履歴(6,480字)の分離**(別ファイル化)(R16)。
9. **Sonnet委任上限(初回+3)とそれに連動する自動UDR**の規則の再定義または撤廃(実績は18件/ID、新ID再発行で回避、10-13枠組みと逆向き)(R18)。
10. **「UDR文化を踏襲」(sonnet-worker.md L24)と「Fableまたはユーザーへ判断を仰ぐ」(L14)の二宛先表現**の見直し(R3, R23)。
11. **STOP必須6条件**を例示ベースで再定義(曖昧語の置換)または削減(R2)。
12. **UDR_REGISTERの見出し・集計行**の削除(行数自体は索引として残し、件数表記は機械生成)(R14)。

### 5-2 仕組み化(自動検証)候補

1. **STOP確認の共通ライブラリ化**: 全runner共通の`check_stop(management_id)`(STOP_NOTICEにfront-matterでmanagement_id/scope/status=ACTIVE|CLOSEDを持たせ、globではなく構造化判定)。Family Zで実装済みの26-5(STOP_ALL・RUN_LOCK・RESTART_STORM)の水平展開(R6, R19)。
2. **委任文Validatorの意味検査化**: 現行の見出しkeywordの有無(形式)から、「STOP条件に『再発』『軽度』等の曖昧語を使っていないか」「原因調査工程が含まれるか」「ユーザー判断項目に10-13枠組みの除外対象が混入していないか」の検査へ。要点保存版と全文版で別基準(R7, R9)。
3. **ループ上限の計数**: delegation_logの管理ID単位のファイル数を機械集計し、警告またはFableへの通知(R18)。
4. **UDRの出自検査**: `USER_DECISION_REQUIRED`起票時に必須フィールド(「新仕様/Gate緩和/承認仕様変更/予算超過/品質トレードオフ」のどれか1つ)を要求し、空なら起票不可。#53,#55,#56〜58型の誤用を防ぐ(R21, R22)。
5. **台帳lint**: OPEN行3,000字、UDR_REGISTER件数、REPORT_LEDGERの定型句、DECISION_LOG重複見出しの自動検査(R14, R15)。
6. **報告マーカー**: ユーザー向け報告の出力フックによる★★★★マーカー検査(`.claude/settings`のhooks。現在はhooks 0件)(R17)。
7. **OPEN→作業キュー**: OPEN候補・リスクに「担当/期限/優先度/Failure mode ID」を必須化し、同一failure modeの重複登録を検知(OPEN-310とOPEN-349/346の関連検出)(R11)。
8. **Parity・契約整合テストの標準化**: 「共有moduleの入力契約が変わる配線(候補ID方式等)では、下流stage(canonicalization/Rule7)の契約テストを必須にする」ためのテンプレートチェック(R12)。
9. **検証状態の引継ぎ機構の展開**: COMPLETION-01で実装した`REUSED_VALIDATED`型の引継ぎをrunner共通のcache確認前処理として他Familyへ(R13)。§14-6の運用ルールを機構化。
10. **Fableの読取権限の見直し**: 受入時の独立検証(read-onlyな集計・testの再実行)を可能にする専用の検証用ツール/Agent(例: haiku-worker相当の拡張)。tools欄とagent本文の不一致(haiku)も同時に解消(R5)。

### 5-3 維持すべき有効規則

1. **Opus独立技術レビューGate(11-3)**: 条件A〜D、Opus所見の台帳(OPUS_FINDINGS_LEDGER)への採否記録、「Opusレビュー自体をユーザーGateにしない」運用(3-1-1)。
2. **Production採用はユーザーのみ/Trial結果の自動格上げ禁止**(CLAUDE.md、sandwich-pm手順5)。
3. **Gate迂回の禁止(Audio Validation/Rule7/M3/ASR)と、BLOCK時に停止して原因調査へ進む姿勢**。ただし「止まった後は調査して直す」責任を明文化することが前提(3-4)。
4. **26-5の機械的STOP(STOP_ALL、RUN_LOCK、RESTART_STORM)**: 水平展開の候補(5-2-1)。
5. **secret scan必須(26-X)**とデバッグログcommit禁止。
6. **ユーザー指示の逐語保存(Gate 2)**: 10-13枠組みの出典が確認できた唯一の経路。
7. **Managed-ID trailer付きcommit、明示add、`git add -A`禁止**。
8. **費用Guardrailのcontinue/STOP書き分け(T-3、§11冒頭の2026-10-05指示)**: STOPをユーザー承認値超過と構造的Wasteに限る原則。
9. **PASS済み成果物の再利用優先(14-6)の趣旨**: 機構化(5-2-9)を前提に維持。
10. **新規記事テーマはユーザー選定(CLAUDE.md、§13)**。
11. **最新モデル原則の報告項目(§25)**: 軽量かつ検証可能。

---

## 付録 判断に使った主な出典(read-only)

- `CLAUDE.md`、`.claude/agents/{sandwich-pm,sonnet-worker,opus-consultant,haiku-worker}.md`、`docs/pm/PM_GOVERNANCE.md`(§1, §2, §9-0, §11, §14, §19, §26, 変更履歴)、`docs/pm/PM_BRIEF.md`
- `docs/pm/USER_DECISION_REGISTER_01.md`(#47, #50, #53〜#58)、`docs/pm/OPUS_FINDINGS_LEDGER.md`(OF-159〜208)、`docs/pm/REPORT_LEDGER.md`、`OPEN_ITEMS.md`(OPEN-310, 343, 346, 349, 352, 353)
- `docs/pm/delegation_log/2026-10-13_FAMILY-XZ-M2P0-N01-PRODUCTION-{WIRING,COMPLETION}-01_*.md`、`2026-10-13_ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01_*.md`、`2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_{10,STOP_NOTICE}.md`
- `docs/pm/RESULT_PACKET_{XZW,XZC,M1OOV}.md`、`docs/pm/ACTIVE_TASK.md`、`docs/pm/ACTIVE_TASK_{XZC,M1OOV}.md`
- `er071_output/m2p0_n01_production_wiring_01/{WIRING_DESIGN_01.md, completion_01/FIX1_ROOT_CAUSE_01.md, completion_03/{gloss_check_03.md, invalid_census_03.md}}`
- 各runner(`er064_kp_*_run.py`, `er065_*runner.py`, `er067_*`, `er073_*`ほか)のSTOP確認コード

## 限界

- [推測] Fableの会話内の判断(ユーザーへの実際の報告文)は会話ログとして残っておらず、委任文・UDR・OPEN・RESULT_PACKETから復元した。Fable自身の推論過程は確認できない。
- `docs/pm/transcripts/`に回収済みjsonl(81件)があるが、本診断では個別に読んでいない(read-only診断の範囲を優先)。会話の細部(例: ユーザー指摘への応答の語調)は未確認。
- 規則数・重複度はgrepと文字数に基づく概算で、意味的重複の厳密な判定ではない。
