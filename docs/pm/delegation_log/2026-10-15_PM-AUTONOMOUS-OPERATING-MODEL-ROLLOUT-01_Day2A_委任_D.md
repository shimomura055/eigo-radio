## 管理ID

PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day 2 Phase A 委任_D(Opus条件Aレビュー所見OF-D2-01〜22の反映=成果物v2作成+Opusレビュー全文保存+台帳記録。2026-10-15)。**本管理ID Day2 Phase AのSonnet委任はこれが4回目=最後。** 前委任: A(bc3f49718)/B(1f77f431c)/C(8c3f80aeb)。並行タスク: なし。

## 性質/到達上限Status/禁止事項

性質: read-only調査+設計文書の改訂(規則・Agent定義・SSOT本体・Production・Prompt・Gate・flag無変更、有料API・Opus呼出なし、費用JPY0)。到達上限Status: DAY2_PHASE_A_V2_COMPLETE(Fable独立受入→ユーザー設計承認待ちSTOP)。
Opus独立技術レビューGate判定: 条件A実施済み(本委任文末尾に全文)。本委任はその反映。
時間見込み: 90〜120分(所見→変更対応表15分/CHARTER v2 15分/USER_DECISIONS v2 30分/MINIMUM v2 20分/RECON追補・AGENT_ROLE追補15分/台帳・保存・commit 15分)。並列化: 不要。
禁止: `CLAUDE.md`/`.claude/agents/*`/`docs/pm/PM_GOVERNANCE.md`/`docs/pm/PM_BRIEF.md`/`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`.py`/Prompt/flagの編集、Day3〜4先行実装、既決事項の再質問、承認済み規則の独断廃止・緩和、v1ファイルの上書き(v2は別ファイル名で作成し、v1は履歴として残す)、`git add -A`/`-f`/amend/rebase/force push/stash/clean/reset --hard/checkout -f。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0: 受領した委任文を**全文(末尾のOpusレビュー全文を含む)**`docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_Day2A_委任_D.md`へ保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_Day2A_委任_D.md --json-out docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_Day2A_委任_D_check.json`を実行し結果をRESULT_PACKETへ1行記録。
T-2: TTSなし。T-3: 費用JPY0。

## ユーザー指示(原文)

(委任_A〜_Cと同一。要点)「既存ルールを大量に書き換えることではない。8原則を共有し、Fableが本当にPMとして機能し、既存仕様との矛盾や未承認Production変更を防ぎながら、品質を守って開発を速めること。この目的に必要な最小限の変更だけを提案する。」「今回の新設計を理由に、既存のユーザー承認済みルールを独断で廃止・緩和しない。」「役割を文書に追加するだけで、手段・権限がなく実行不能になる設計は認めない。」「過去に既にユーザーが判断した事項を再質問しない。技術的な設計詳細はFableが判断し、本当にユーザーの承認が必要な規則・権限・予算・品質の変更だけを提示する。」「Day 2 Phase Aの終了時はSTOPし、ユーザーの設計承認を待つ。」

## Fableの所見採否(これに従う。Opus所見を機械的に採用したのではなく、「承認済み境界を文言で狭めない・広げない」というユーザー指示との整合で判断した)

| 所見 | Fable採否 | 反映内容 |
|---|---|---|
| OF-D2-01 BLOCKER | 採用 | Charter L24「次だけ」→「主に次。網羅と詳細は`PM_GOVERNANCE.md` §11 STOP条件・10-1・11-1を正本とする」。漏れ項目(新仕様の追加/Production挙動の意味的変更/最終人間品質判断/Writer・Prompt原則変更/QA blocking条件変更/Git例外/新規記事テーマ)を主要項目として追記するか参照で示す(Charterが長くなりすぎないよう主要3〜4項目+参照)。W5bの「Charter正本化」は撤回 |
| OF-D2-02/03/04 MAJOR | 採用 | U2を書き直す: 条件B該当なら**Opusを先に**→所見を受けて再計画1回→再計画後の追加Sonnet委任は**最大2回(数値はユーザー承認事項として明示)**、D1(検証専用)は別枠→2度目の到達は必ずSTOPし「現状・原因・試した手段・目処」付き報告。11-1 STOP(3)「構造的問題」とL3診断後(L2212/L2257、sandwich-pm L80-81)の扱いが変わることをU2本文に開示し「変えない」選択肢も残す。11-4はOpus/Fable改善ループ専用の別カウントでSonnetループの絶対上限ではない旨を正確に記載。LOOP-03原文(`DECISION_LOG_HISTORY.md`をGrep「LOOP-03」)で「到達=UDR」のユーザー原文承認の有無を確認し結果を記載 |
| OF-D2-05 MAJOR | 採用 | U3(d)を**単独項目U3'**に分離。「D1は1件の安全措置承認であり常設の一般許可ではない。本項は一般化=承認範囲の拡大である」と明示。例外を置く場合の5条件((i)新コード経路+単一flag読取関数に限りmode・引数・設定dictからのON禁止 (ii)既存Production Prompt・正規表現・閾値・辞書の直接編集には不適用 (iii)`DefaultOffIsolation`型test PASS必須 (iv)起動script・.envでのON禁止 (v)flag名と「承認前・既定OFF」をOPEN_ITEMS該当行に記録しPRODUCTION_WIREDと呼ばない)を文言化。「例外を置かない」代替案(未承認コードはTrialモジュールのみ)を選択肢として併記。Charter L30も同じ5条件に整合(短縮形+参照) |
| OF-D2-06 MAJOR | 採用 | W5a(d)の「のみ」を外し、11-3再レビュー5条件は維持+「所見反映でretry/fallback既定やPass/Failルールを変えた場合は(2)(3)該当とみなし軽量確認」の追加型文言へ |
| OF-D2-07 MAJOR | 採用 | W2(a)に「有料run・外部停止されたprocess・STOP該当時は26節を優先し、再現のための再実行をしない」を明記 |
| OF-D2-08 MAJOR | 採用 | Charter原則4の例外括弧に「作業継続を妨げるblocker・12-2の即時報告対象」を追加 |
| OF-D2-09 MAJOR | 採用 | F3: L29の制限は「量」(ディレクトリ走査・大量ログ全文)のみとし「Worker記載パスに限る」を削除。受入記録の「照合した証拠」はファイル:行+**観測値の引用**必須。受入記録(3行)を**ユーザー向け報告本体にも必ず載せる**(9-0固定5節の「3 重要な問題・残作業」の直前または「1 結論」末尾に`受入記録:`見出しで置く案を提示、Fableが最終決定)。tool回数要件は置かない |
| OF-D2-10 MINOR | 採用 | 失敗経路確認はGate 7+W7(設計時)を主、§6「安全≠成功」の失敗経路版として記述。Gate 3追記は補助 |
| OF-D2-11 MAJOR | 採用 | D1は「編集・実装禁止の検証専用、ループ上限とは別カウント、1受入につき最大2回。受入時にgit状態無変化を確認」と明記 |
| OF-D2-12 MINOR | 採用 | W2(d): Sonnetは作業開始時に`tools/stop_scope_check_01.py`をBashで実行しrc=3なら停止/NOTICE本文を自分で解釈しない/helper実行不可またはrun-dirなしの作業では全NOTICE適用(fail-closed) |
| OF-D2-13/14 MINOR | 採用 | §11 L1872をW4対象に追加。W7にOpus packet「承認状況・Production到達経路か」欄とSonnet報告「撤去・残置した規則・検査・testの識別子と残存Grep結果」1行を追加 |
| OF-D2-15 MINOR | 採用 | U4に任意項目「観点11注記1行を12観点ブロック本体にも追加(2026-10-02正本の改変を伴うため承認要)」を追加 |
| OF-D2-16 MINOR | 採用 | U3(c)をA(tools欄に`haiku-worker`追加1語、実機確認要)/B(本文から記述整理=2026-09-10承認機能の事実上廃止と明示)の選択肢に。推奨はA(既存ユーザー決定に忠実・変更量最小。Fable注: 本セッションの起動可能一覧にhaiku-workerが無いため、Aでも実機確認でNGなら再提示) |
| OF-D2-17/18 MINOR | 採用 | 原則4に「委任範囲内で」。W6欄名を「承認済み指示(原文引用+DECISION_LOG出典)」へ |
| OF-D2-19 MINOR | 採用 | T7を盲検リプレイ(新セッションのsandwich-pmに欠陥前の材料を告知なしで渡す)+陰性対照(c21cce27a)+事後実測(次の実委任3〜5件で受入記録・観測値引用・失敗経路行・技術理由UDR件数を計数)へ |
| OF-D2-20 MINOR | 採用 | W5bを後回し(P群へ)。必須は8単位。Day3-4ではW4で「上限到達=UDR」矛盾箇所のみ修正、既存STOP文言は削らずCharter参照の追記のみ。7箇所整理はリプレイ後に1対1対応表を作ってから |
| OF-D2-21 MINOR | 採用 | 安全境界に隣接する3文言(Charter判断区分/既定OFF例外/U2)は**変更前の実文と変更後の実文**を並記 |
| OF-D2-22 MINOR | 採用 | P13(既定ONフラグ約12件のSSOT突合)をDay5リプレイ試験に含める(JPY0・約1h) |
| 代替案5(CP短縮) | 採用 | S-aをCLAUDE.md+PM_BRIEF/sandwich-pmの2ストリームに分割、CP約2.7hを§6に反映 |

## KPI provenance欄

該当なし。

## Opus台帳更新

`docs/pm/OPUS_FINDINGS_LEDGER.md`は本委任では編集しない(SSOT編集権なし)。代わりに`day2/OPUS_FINDINGS_D2_LEDGER_DRAFT_01.md`にOF-D2-01〜22の台帳行(ヘッダ10列形式、Fable採否・反映先・状態=FABLE_DECIDED→DESIGN_REVISED)を作成し、SSOT反映は承認後の委任で行う。

## 事前指定Read一覧

- `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day2/CHARTER_DRAFT_01.md`・`USER_DECISIONS_01.md`・`MINIMUM_CHANGE_PLAN_01.md`: 全文(改訂元)
- 同 `DAY2_DESIGN_RECONCILIATION_01.md`: §3-2(裁定D-1〜D-7)・§4
- 同 `AGENT_ROLE_DELTA_01.md`: §1(F3)・§2・§5
- `docs/pm/PM_GOVERNANCE.md`: 行指定 L132-163、L164-246、L606-610、L1662-1673、L1858-1874、L2030-2049、L2123-2156、L2212、L2229-2237、L2257、L2315-2334、L2349-2354、L3215-3242(Opus根拠行の確認。変更前実文の引用元)
- `CLAUDE.md`: L29-33、L59-64、L84-88
- `.claude/agents/sandwich-pm.md`: L4、L12-21、L29、L80-90/`.claude/agents/sonnet-worker.md`: L12-24、L47-49
- `DECISION_LOG_HISTORY.md`: Grep「LOOP-03」→該当エントリ全文(「到達=UDR」の原文承認確認)
- `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`: 全文((a)欄の有無)

## 事前指定Grep一覧+追記位置・更新位置の手順

1. `rg -n "LOOP-03" DECISION_LOG_HISTORY.md DECISION_LOG.md docs/pm/PM_GOVERNANCE.md` → 到達時動作の原文。
2. `rg -n "USER_DECISION_REQUIRED" .claude/agents/sandwich-pm.md .claude/agents/sonnet-worker.md CLAUDE.md docs/pm/PM_BRIEF.md` → W4対象の網羅確認(§11 L1872含む)。
3. 変更前実文の引用: 3文言(Charter判断区分↔PM_GOV §11 STOP6条件・10-1・11-1 STOP(1)〜(5)/既定OFF例外↔sonnet-worker L19-20/U2↔CLAUDE.md L59-64・sandwich-pm L80-90・PM_GOV 11-1 L2044-2049)を逐語で取り、USER_DECISIONS_02の該当項目に「変更前(逐語)/変更後(案)」を並記。
更新位置: 新規 `day2/CHARTER_DRAFT_02.md`、`day2/USER_DECISIONS_02.md`、`day2/MINIMUM_CHANGE_PLAN_02.md`、`day2/DAY2_DESIGN_RECONCILIATION_02_ADDENDUM.md`(v1への追補: 所見→変更対応表、裁定D-1〜D-7の更新、A/B文書の記述で改訂が必要な箇所の一覧[A/B本体は編集しない])、`day2/OPUS_REVIEW_D2_01_VERBATIM.md`(本委任文末尾のOpusレビュー全文を改変なしで保存)、`day2/OPUS_FINDINGS_D2_LEDGER_DRAFT_01.md`。v1ファイルは無変更。

## 実行コマンド全文

- Charter v2本文の文字数: `.venv\Scripts\python.exe -c "import sys,re;t=open(sys.argv[1],encoding='utf-8').read();m=re.search(r'<!-- CHARTER_BEGIN -->(.*?)<!-- CHARTER_END -->',t,re.S);print(len(m.group(1).strip()))" docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day2/CHARTER_DRAFT_02.md`(目標1,000〜2,000字。所見反映で超える場合は参照化で圧縮し、安全・承認境界は削らない)
- T-0のcheck_delegation_prompt.py。`git status --porcelain`→明示add→commit→`git push origin main`。PATH上の素のpythonは使わない。

## SSOT追記文

本委任ではSSOT編集なし。USER_DECISIONS_02 §3の承認後記録文案をv2の内容に更新。

## Git(明示add対象・コミットメッセージ・trailer)

SSOT編集権: なし。明示add: 上記新規6ファイル、delegation_log 2ファイル。`RESULT_PACKET_ROLL2D.md`/`ACTIVE_TASK_ROLL.md`はgitignored確認のうえaddしない(ACTIVE_TASK_ROLL.mdヘッダはStatus=DAY2_PHASE_A_V2_FABLE_ACCEPTANCE_PENDINGへ更新)。
コミットメッセージ: `PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day2 Phase A 委任_D: Opus条件A所見OF-D2-01〜22反映(Charter v2[判断区分を非網羅+正本参照]、U2再構成[条件B先行・再計画後上限・開示]、既定OFF例外を5条件付き単独項目化、F3観測値引用+報告掲載、W5b後回し=必須8単位、盲検リプレイ)、Opus全文保存。規則/SSOT/Production無変更、JPY0`、trailer `Managed-ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01`。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_ROLL2D.md`(35行以内): Status/T-0/所見22件の反映状況(反映済み/一部/未反映と理由)/Charter v2文字数/LOOP-03原文確認の結果(「到達=UDR」はユーザー原文承認か否か)/U一覧v2(U1〜U6+U3'、各ブロック/非ブロック、推奨)/必須8単位・任意・後回しの件数とCP/3文言の変更前後並記の所在/Fableが独立受入で確認すべき箇所(ファイル:節)/未確認事項/commit。
`USER_DECISIONS_02.md`冒頭の超サマリ(非エンジニア向け10行以内)もv2に更新(Opusレビューで安全境界を狭める文言が見つかり修正した旨を1行入れる)。

## Opus条件Aレビュー全文(2026-10-15、改変なしで`OPUS_REVIEW_D2_01_VERBATIM.md`へ保存)

(以下、同一内容を`docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day2/OPUS_REVIEW_D2_01_VERBATIM.md`として保存。本ファイルへは下記に連結)

PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day2 Phase A: Opus独立技術レビュー(条件A、実装前、2026-10-15、read-only)

レビュー者: opus-consultant(Opus 5.5、claude-opus-5-5。最新世代の最上位系)。本レビューでは実装・規則変更・採用可否の宣言を行わない。採用はユーザーが判断する。

---

## 1. 総評

- **必要/不要**: 必要。ただし、範囲を絞ったうえで、文言を直してからユーザーへ出すべき。今回の対応で中核になるのは次の4点。(1)F3受入の実行手段(L29の明確化と、受領と受入の区別)、(2)「失敗終了時の最終成果物」を、設計時(Opus packetと委任文)と受入時(Gate 7)の両方で問うこと、(3)「上限到達=UDR」という既定動作の置換、(4)Sonnet報告先の一本化。KGORAの連鎖(Sonnet原設計→Opus提案→Fableが照合せず採用→test固定→受入なしで転送)に直接効くのはこの4点で、新機構0・新規ファイル0の方針は妥当。
- **推奨構造**: 必須はW1・W2・W3・W4・W5a・W6・W7・W8の8単位とし、W5b(UDR/STOP条件の一本化と曖昧語の例示化)は後回しにする。予防の主軸は、受入時ではなく設計時(W7)に置く。受入記録は「次の委任文冒頭」だけでなく、ユーザー報告本体にも必ず載せる。
- **最大リスク**: 計画そのものの中に、承認済みの安全・承認境界を**文言で狭める・広げる**箇所が少なくとも6つある。具体的には、Charterの「次だけ」+W5bの正本化、U2の再計画予算が未定義、11-3再レビューの「のみ」、既定OFF例外の一般化、W2(a)と26-2(a)の衝突、L3診断後の扱いの変更をU2で開示していないこと。これは再発防止項目(1)「承認済み仕様と矛盾する仕様変更」を、この計画自身が繰り返す型である。ユーザーに承認を求める前に、すべて直す必要がある(§4のBLOCKER 1件とMAJOR群)。

---

## 2. 12観点の判定(1行ずつ)

1. **必要性**: 必要。KGORAの受入は37秒・tool_use 0で、失敗経路は誰も確認しておらず、受入規定は5か所に分散し手段もない(AUDIT_REPORT_01.md L10, L116、GATE_MECHANISM_MAP_01.md L27, L31)。ただしW5bは今回の不全の原因ではないので、後回しでよい(MINIMUM_CHANGE_PLAN_01.md L24)。
2. **より単純な構造**: 3点で単純化できる。W5bの後回し/受入記録をユーザー報告に載せる(委任文冒頭だけに書くより確実)/「失敗終了時」の確認を既存§6「安全≠成功」(PM_GOVERNANCE.md L606-610)の失敗経路版として書く。
3. **既存処理・データの利用**: 良好。Gate 7・delegation_log・`tools/stop_scope_check_01.py`(L5-21で、構造化scopeとfail-closedが実装済みであることを確認)を使っている。§6の既存原則は未活用。
4. **前段情報の喪失**: 改善はあるが残りがある。Opus原文の保存(W5a(e))は良い。一方、受入記録が委任文冒頭にしか残らないと、最終報告では委任文が生成されず欠落する(AGENT_ROLE_DELTA_01.md L58)。
5. **不要なLLM処理**: 概ね問題なし。D1(検証専用sonnet-worker)は高リスク時のみ。ただし回数上限との関係が未定義(OF-D2-11)。
6. **非決定性**: 小さい。リスク階層の判定がFableの裁量なので、定義を明確にすれば足りる。
7. **Human Review増**: 増えない。UDRへの転送は減る方向。ただし判断区分を狭めると、本来ユーザーに上げるべき事項が漏れる側の危険がある(OF-D2-01)。
8. **不要Rewrite**: 該当なし(文書変更のみ)。
9. **コスト**: API費用はJPY0。D1分のトークン増は軽微。
10. **retry/fallback/regenerationとの整合**: 問題あり。U2の再計画と11-3条件B(3回目のパッチ前にOpus)の順序、11-1のループ上限が拡張されないという明文(PM_GOVERNANCE.md L2047-2049)、26-2(a)の再実行禁止(L3223)とW2(a)の「原因究明ループ2周」が衝突する。
11. **Failure時に安全側へ倒れるか**: 現状の文言では不十分。具体的には、Charterの判断区分が既存のSTOP条件より狭い(CHARTER_DRAFT_01.md L24 と PM_GOVERNANCE.md L1864-1870, L2044-2046)、既定OFF例外が一般化されている(CHARTER_DRAFT_01.md L30、MINIMUM L20)、再計画後の実行回数が未定義(MINIMUM L22)。
12. **再発防止か**: 設計時の問い(W7)と受入時の失敗経路確認(W5a)は型への対策になっている。ただし文書だけの規定で強制力はないため、効果はリプレイ試験の設計次第(OF-D2-19)。

---

## 3. 追加観点(a)〜(j)

### (a) F3の実行可能性

- **実行可能か**: S1〜S5はRead/Grep/Globで実行できる。D1はAgent(sonnet-worker)で実行できる。記録先(委任文はT-0でdelegation_logに永続)もFableの道具の範囲で成立している。文書を足しただけで実行不能、という設計ではない。
- **37秒型を防げるか**: 部分的にしか防げない。理由は3つ。
  - (1)「少なくとも1回のtool使用」は、RESULT_PACKETを1回Readするだけで形式的に満たせてしまう。
  - (2)L29の置換文案「読取対象は委任文またはRESULT_PACKETに記載されたパス・行に限る」(AGENT_ROLE_DELTA_01.md L61)では、何を読むかを実装者(Sonnet)が決めることになり、独立性がない。KGORAの欠陥test(`test_failed_alignment_keeps_kp_flags_failed_not_human_review`)は、Sonnetが報告に挙げなければ読めない。
  - (3)KGORAで最も危険だった37秒の転送は「hand-back → そのままユーザー報告」の経路で起きた。次の委任文が存在しない場面で、記録が作られない。
- **MUST**:
  - L29の制限は「量」(ディレクトリ走査・大量ログ全文の禁止)に限り、「出所」(Workerが列挙したパスのみ)では制限しない。読取対象にはD1で得た`git diff --stat`のファイル、該当test、SSOT Grepを含める。
  - 受入記録の「照合した証拠」は、ファイル:行に加えて**観測値の引用**(例: `:45 GLOSS_ALIGNMENT_ENABLED = os.environ.get(..., "0")`)を必須にする。tool回数ではなく内容で検査できる形にする。
  - 受入記録(3行)を**ユーザー向け報告本体に必ず載せる**。最終承認者であるユーザーが欠落に気づける唯一の場所だから。委任文冒頭・SSOT記録委任への転記は永続化のために併用する。
- **SHOULD**: 記録の固定見出し文字列(例: `受入記録:`)を決め、Grepで検索できるようにする(GATE_MECHANISM_MAP_01.md L149の未設計事項)。
- **より確実な手段**: KGORAの欠陥は、受入より前に「Opus所見を採用する時点」で生じた。最も効果が高く安いのは、W7(Opus packetと委任文に「目的1文」と「失敗終了時の最終成果物は目的を満たすか」を入れる)と、Fableが所見を採否する時点での照合1行(AUDIT B2)。F3は第2の防壁と位置づけ、W7を第1の防壁として優先する。

### (b) U2「上限到達=UDR」の置換

- **安全停止を緩めていないか**: 現在の文言では緩める余地がある。
  - (1)**再計画の実行予算が未定義**。上限4回に到達した後の「再計画1回」で新しいSonnet委任を何回してよいかが書かれていない。11-1には、ユーザー原文に基づく「ループ上限は本項により変更・拡張されない」(PM_GOVERNANCE.md L2047-2049)がある。再計画で委任を追加すれば、実質的にこの上限を拡張することになる。
  - (2)**条件Bとの順序**。U2の案は「(1)再計画→(2)条件BならOpus」の順になっている。しかし11-3条件Bは「3回目の個別パッチ前にSTOPしてOpus」(L2150-2156)。再計画の中にパッチ実装が含まれると、Opusなしで3回目のパッチになる。
  - (3)**開示漏れ**。W4は、PM_GOVERNANCE L2212/L2257(L3難問診断後は人間判断)と、sandwich-pm L80-81まで書き換える対象に含めている(MINIMUM L22、RECONCILIATION L65)。しかしUSER_DECISIONS U2の説明文(L57-64)はこの変更に触れていない。11-1 STOP(3)「構造的問題」(L2045)の扱いが変わることにも触れていない。
- **MUST**:
  - 条件Bに該当する場合は、**Opusを先に**実施し、Opus所見を受けて再計画する順序に直す。
  - 再計画後の追加Sonnet委任に明示の上限を置く(例: 最大2回、D1は別枠)。2度目の到達では必ずSTOPし、「現状・原因・試した手段・目処」を付けて報告する。数値はユーザー承認事項にする。
  - U2の説明文に「11-1 STOP(3)とL3診断後の扱いも変わる」ことを明記し、ユーザーが選べるようにする(変えない選択肢も残す)。
- **歯止めとして十分なもの**: 11-4(4回目以降は毎回ユーザーGate)、予算Cap、明示STOPは維持されている。ただし11-4はOpus/Fable改善ループ専用の別カウント(L2324)で、Sonnetループの絶対上限にはならない。この点を正確に書くこと。

### (c) Charter草案

- **8原則の反映**: 概ね正確。安全・承認境界(Production採用は人間のみ/3状態の区別/STOP・予算・Gateの迂回禁止/無言承認禁止)も省略されていない(CHARTER_DRAFT_01.md L28-33)。
- **問題1(BLOCKER、OF-D2-01)**: 「人間(ユーザー)に判断を求めるのは**次だけ**」(L24)は網羅列挙として書かれており、次の既存のユーザー承認済み判断事項が漏れている。
  - §11 STOP 1「新仕様の追加」、3「Production挙動の意味的変更」(L1865, L1867)
  - 11-1 STOP(5)「最終的に人間判断でしか解決できない品質問題」(L2046。ユーザー原文L2035の「最終人間品質判断」)
  - 10-1「Writer・Prompt原則変更」「QA blocking条件変更」(L1671-1672)
  - CLAUDE.md Git例外(L29-33)、§13新規記事テーマ
  
  さらにW5bはこのCharterを判断区分の「正本」にする(MINIMUM L24)。結果として、既存条件が実質的に狭まる。
- **問題2(MAJOR、OF-D2-08)**: 原則4の「問題を見つけるたびに報告せず」は、12-2の即時報告トリガ「重要な途中結果判明/blocker発生」(L2351-2353)と衝突する。RECONCILIATION §4(a)は「12-2は報告単位が対象なので競合しない」としているが、12-2はblockerを明示的にトリガにしている。例外の括弧に「作業継続を妨げるblocker・12-2の即時報告対象」を加えること。
- **問題3(MINOR)**: 原則4は全Agent共通で読まれるため、Sonnetが委任範囲外の不具合まで直す誘因になる。「委任範囲内で」を加えること(sonnet-worker L12-13との整合)。
- **配置**: CLAUDE.md冒頭への配置は妥当。全Agentへの自動注入を確認済みで、このセッションのOpusにも注入されている。増える文字量(+1.4k字)は軽微。ただし判断区分の正本をCLAUDE.md(Fableが編集できず、変更のたびにユーザー確認が要る文書)に置くと、保守が重くなる。
- **MUST**: 「次だけ」を「主に次。詳細と網羅は`PM_GOVERNANCE.md` §11 STOP条件・10-1・11-1を正本とする」に直す。漏れている項目(新仕様の追加/Production挙動の意味的変更/最終人間品質判断)を列挙に加える。

### (d) 再発防止7項目の充足(委任背景の7項目)

| # | 項目 | 塞がるか | 弱点 |
|---|---|---|---|
| 1 | 承認済み仕様との矛盾 | 概ね塞がる(W5a(c)・W7・F3のS5) | 計画自身が文言で矛盾を作っている(OF-D2-01/05/06) |
| 2 | 不要Validatorの残存 | **弱い** | Gate項目(文書)とOpus側の問いだけ。Sonnet報告3行に「撤回・置換した規則・検査・testの識別子と、その残存Grep結果」の行がない → W2(b)/W7に1行追加(SHOULD) |
| 3 | 正常系PASSのみ | 塞がる(Sonnet報告3行目、Gate 7、D1) | Gate 3は`APPROVED_FOR_PRODUCTION`の**後**にしか適用されない(PM_GOVERNANCE L182-183)。KGORAの配線は承認前だった。必ずGate 7と設計時(W7)を主に置き、§6「安全≠成功」の失敗経路版として書く |
| 4 | Fableが受入せず転送 | 部分的 | (a)のMUST 3点が必要 |
| 5 | 未承認仕様の既定ON | 部分的 | Opus packetに「承認状況(APPROVED?/Production到達経路か)」欄がない。KGORAの既定ONはOpus OF-235の推奨が出所(GATE_MECHANISM_MAP_01.md L66, L99)。W7(b)に1項目追加(MUST)。既存の既定ONフラグ約12件の突合(P13)はJPY0で約1h。リプレイ試験に含めることを推奨(SHOULD) |
| 6 | 技術不具合を安易にUDR | 塞がる(W4・W2・Charter) | §11 L1872「失敗・副作用…が発生した場合のみ…USER_DECISION_REQUIREDとしてSTOP」が、W4/W5bの対象一覧にない → W4に追加(MINOR) |
| 7 | 既決事項の再質問 | 塞がる(W8+Charter確認(1)) | なし |

- 「失敗終了時の最終成果物」(Gate 3/7への追記): 文書追記だけでも、委任文テンプレの報告必須行(W7)とFable受入の観測値引用(a)を組み合わせれば運用上は機能する。単独では機能しない。
- 「不要になった旧ルールの撤去確認」: 現状はOpus側の問いとGate項目しかない。上の表のとおり、Sonnet報告に1行追加しない限り弱い。

### (e) 既定OFF限定例外(sonnet-worker L19-20とCharter L30)

- **抜け道を広げるか**: 広げる余地がある。
  - USER_DECISIONS U3(d)は「本日D1の承認範囲に合わせる、例外を拡大しない」と説明している。しかしD1は**KGORAの1件の安全措置(既定ONをOFFへ)の承認**であり、「未承認仕様を既定OFFでProductionコードへ実装してよい」という**常設の一般許可**ではない。一般化は承認範囲の拡大で、ユーザーへの説明として不正確(MAJOR、OF-D2-05)。
  - 条件が「既定OFF・明示flag・既定動作無変更」だけでは、V1(mode引数・Python引数での迂回)、V3(env・起動script)、V4(Prompt・正規表現・閾値の直接編集)、V9(共通到達点での一括ON)を閉じられない。
- **MUST(例外を置く場合)**: 条件を次のように明記する。
  - (i)新しいコード経路と単一のflag読取関数に限る(mode・引数・設定dictからのONを禁止)
  - (ii)既存Production Prompt・正規表現・閾値・辞書の直接編集には適用しない
  - (iii)`DefaultOffIsolation`型test(flag未設定でAPI 0・出力がバイト一致・副作用ファイル0)のPASSを必須にする
  - (iv)起動script・`.env`でのONを禁止する
  - (v)flag名と「承認前・既定OFF」をOPEN_ITEMS該当行に記録し、PRODUCTION_WIREDとは呼ばない
- **例外を置かない代替案との得失**:
  - 例外なし(未承認コードはTrialモジュールのみ。承認後に配線)は、最も安全で文言も単純。欠点は、Production経路上でのE2E Trialができず、承認後の配線作業が二度手間になること。
  - 推奨は「限定例外+上記5条件」。U3(d)は単独項目として、一般化であることを明示して諮るべき。

### (f) D-1〜D-7の裁定案

- **D-1**: B案(本文からhaikuの記述を削除)は、2026-09-10にユーザー承認された機能を事実上廃止することになる。その旨を明示しないまま「実在しない経路の整理」と扱うのは不正確。A案(tools欄へ`haiku-worker`を追加)のほうが既存のユーザー決定に忠実で、変更量も1語。どちらを採るかはU3(c)でユーザーに選ばせる。B案を採る場合、CLAUDE.md L84-88とPM_GOVERNANCE L155に食い違いが残る(MINOR)。
- **D-2**: 「B案を主、A案を補助」の方向に賛成。ただしL29の置換文の「Worker記載パスに限る」は削除すること(上記(a))。
- **D-3**: 部分的に異論がある。packet(a)欄は、Fableがテンプレートを使わずに依頼する場合に欠落する。毎回必ず貼られるのは12観点ブロックだけなので、観点11への注記1行をブロック側にも置くことを、U4の任意項目としてユーザーに提示するのがよい。同じ承認バッチに入れるため、追加コストはほぼない(MINOR)。
- **D-4**: 賛成(厳しい側に統一)。
- **D-5**: 2段階化に賛成。次の2点を加えること。(i)失敗経路のない変更(docsのみ等)では、失敗経路の照合を「N/A+理由」とすることを許す。(ii)D1の回数カウントの扱いを明記する(OF-D2-11)。
- **D-6**: 賛成。
- **D-7**: helperの存在を確認した(L5-21)。ただしW2(d)の「存在すれば報告は維持、未使用helperなら全NOTICEをfail-closed」は曖昧。次のように書く必要がある。
  - Sonnetは作業開始時にhelperを**Bashで実行**し、rc=3なら停止する。
  - NOTICE本文を自分で読んで適用範囲を判断しない。
  - helperを実行できない場合や、run-dirのない作業では、全NOTICEを適用とみなす。
  
  なお26-2(d)をhelperに揃えると、26-2(d)の適用範囲は広がる(安全側)。sonnet-worker側は狭まるが、これは承認済みの案a(D5)の範囲内。

### (g) 乱立回避

- 新規ファイル0・新機構0・任意3・後回し14は妥当。
- **不要(後回しにすべき)**: W5bの「曖昧語の例示化」。例示は事実上の網羅列挙として読まれ、緩和を生みやすい。(c)で指摘したCharter正本化とも同じ問題を抱える。代わりに、Day3-4ではW4で「上限到達=UDR」の矛盾箇所だけを直し、各STOP条件の既存文言は削らず、Charterへの参照は追記だけにとどめる。7箇所の整理は、リプレイ試験後に1対1対応表を作ってから行う。
- **欠けている最小単位**:
  - (i)Opus packetの「承認状況」欄
  - (ii)Sonnet報告の「撤去・残置のGrep」1行
  - (iii)§11 L1872をW4の対象に追加
  - (iv)受入記録をユーザー報告にも載せること(9-0固定5節のどこに入れるかを指定)

### (h) 工数とクリティカルパス

- 11.2hは、Sonnetの編集時間としては妥当から若干多め。
- W5bを後回しにすると、S-b(PM_GOVERNANCE)は約2.7hになる。
- S-aはファイルが異なるので2つに分けられる: CLAUDE.md+PM_BRIEF(W1+W4該当部+W6、約2h)と、sandwich-pm(W4該当部+W3、約1.8h)。分ければCPは約2.7hになる。
- 実際のクリティカルパスは、ユーザー承認と、安全文言に関わる受入(Fableによる旧新の1対1照合)。
- リプレイ試験の採点基準(期待される検出・誤検出なし条件)は、実装待ちの間に先行して作れる。

### (i) ユーザー判断U1〜U6の切り分け

- 区分は概ね適切。既決事項D1〜D12の再質問は見当たらない(U3(e)は既決D5の反映と明記済み)。
- **直すべき点**:
  - U2に、開示漏れ(L3診断後・11-1 STOP(3))と再計画の予算の数値を加える。
  - U3(d)は「一般化である」ことを明示して単独項目にする。
  - U4(a)の11-3再レビューは「のみ」を外す(OF-D2-06)。
  - U4(b)は後回しを推奨に変える。
  - 安全境界に隣接する3文言(Charterの判断区分、既定OFF例外、U2)は、**変更前と変更後の実文**をユーザーに見せる。一括回答の「全て推奨で」だけでは、非エンジニアのユーザーが文言上の緩和に気づけない。
- U5・U6を非ブロッキングとした扱いは適切。

### (j) Day5以降の効果確認(リプレイ試験)

- 現案は**結論を知った状態での再現**になっている。調査者は欠陥①②を既に知っているので、「見つかった」ことは手順の検出力を示さない。また、検証役がSonnetなので、Fableが手順を守るかは検証されない。
- **推奨する検証法(いずれもJPY0)**:
  - (1)**盲検リプレイ**: 新しいセッションの`claude --agent sandwich-pm`に、欠陥が入る前の材料を、欠陥の存在を告げずに渡し、新手順で受入させる。材料は、3b64e5632時点の状態、Opus所見原文、a337d8accのhand-back。受入記録が①②を指摘するか、tool_useの有無、所要時間を記録する。
  - (2)**陰性対照**: 正しい変更(例: c21cce27aの既定OFF化)に同じ手順を当て、誤った差し戻しや過剰な手間が出ないかを確認する。
  - (3)**事後の実測**: 次の実委任3〜5件で、受入記録の有無、観測値引用の有無、失敗経路行の有無、技術的理由によるUDRの件数を数える。

---

## 4. 所見一覧

**OF-D2-01 [BLOCKER]** Charterの判断区分「次だけ」と、W5bによる正本化で、既存のSTOP/UDR条件が実質的に狭まる
- 内容: (c)のとおり、5種類以上の既存判断事項が列挙から漏れている。
- 根拠: CHARTER_DRAFT_01.md L24、MINIMUM L24、PM_GOVERNANCE.md L1864-1870, L1670-1673, L2035, L2044-2046、CLAUDE.md L29-33。
- 推奨対応: 非網羅の表現にし、正本はPM_GOVERNANCEに残す。漏れた項目を追記する。
- 採用で生じ得るFailure: 列挙を増やしすぎると、原則6(人間には重要な判断だけ)が再び弱まる。そのためCharterには主要項目と正本への参照だけを置く。

**OF-D2-02 [MAJOR]** U2の再計画後に許される実行回数が未定義
- 内容: 11-1の「ループ上限は変更・拡張されない」と衝突する。
- 根拠: MINIMUM L22、PM_GOVERNANCE.md L2047-2049。
- 推奨対応: 再計画後の委任上限を数値で決め、2度目の到達では必ずSTOPする。数値はユーザー承認事項にする。
- 採用で生じ得るFailure: 上限を小さくしすぎると、再計画が書面上の計画だけで終わり、UDR転送が実質的に続く。

**OF-D2-03 [MAJOR]** U2の順序(再計画→条件B Opus)が、11-3条件B(3回目のパッチ前にOpus)と逆
- 根拠: MINIMUM L22、PM_GOVERNANCE.md L2150-2156。
- 推奨対応: 条件Bに該当する場合は「Opusを先に、その後に再計画」とする。
- 採用で生じ得るFailure: Opusの出番が増えるが、条件Bは必須レビューで回数上限の対象外なので、規則上の問題はない。

**OF-D2-04 [MAJOR]** W4がL3診断後の扱い(L2212/L2257、sandwich-pm L80-81)と11-1 STOP(3)を書き換えるのに、U2の説明文がそれを開示していない
- 根拠: RECONCILIATION L65、USER_DECISIONS L57-64。
- 推奨対応: U2に明記し、「変更する/しない」をユーザーが選べるようにする。
- 採用で生じ得るFailure: 選択肢が増えて判断負荷が上がる。推奨を明示して軽減する。

**OF-D2-05 [MAJOR]** 既定OFF例外を「D1の範囲に合わせるだけ」と説明しているが、実際は一般許可への拡大。条件も不足
- 根拠: USER_DECISIONS L71, L18、CHARTER_DRAFT_01.md L30、GATE_MECHANISM_MAP_01.md L88-99。
- 推奨対応: (e)の5条件を付け、単独のユーザー判断項目にする。
- 採用で生じ得るFailure: 条件が厳しいと、承認前のE2E Trialが組みにくくなる。Trialモジュール経由の代替を案内する。

**OF-D2-06 [MAJOR]** W5a(d)の「再レビューの実施は…のみ」が、11-3の再レビュー5条件(ユーザー決定)を狭める
- 根拠: MINIMUM L23、PM_GOVERNANCE.md L2229-2237。
- 推奨対応: 「5条件は維持し、所見反映でretry/fallbackの既定やPass/Failルールを変えた場合は(2)(3)に該当するとみなし、軽量確認を行う」という追加型の文言にする。
- 採用で生じ得るFailure: 再レビューの回数がわずかに増える。

**OF-D2-07 [MAJOR]** W2(a)「仮説→反証→再現のループを2周まで自力で」が、26-2(a)「原因不明のrc≠0が2回続いたら再起動せず即STOP、自己判断で原因調査の再実行を続けない」と衝突する
- 根拠: MINIMUM L20、AGENT_ROLE_DELTA_01.md L111、PM_GOVERNANCE.md L3223。
- 推奨対応: 「有料run・外部停止されたprocess・STOP該当時は26節を優先し、再現のための再実行をしない」を明記する。
- 採用で生じ得るFailure: 有料経路の不具合では原因究明が遅れる。D1(読取・mock)で補う。

**OF-D2-08 [MAJOR]** 原則4「見つけるたびに報告せず」が、12-2の即時報告(blocker・重要な途中結果)と衝突する
- 根拠: CHARTER_DRAFT_01.md L18、PM_GOVERNANCE.md L2351-2354。
- 推奨対応: 例外にblockerと12-2の対象を明記する。
- 採用で生じ得るFailure: 報告の頻度がわずかに増える。

**OF-D2-09 [MAJOR]** F3の手段が形式的に満たせ、独立性も欠ける
- 内容: 読取対象をWorkerが記載したパスに限定している。「1回のtool使用」で足りてしまう。受入記録がユーザー報告に載らない。
- 根拠: AGENT_ROLE_DELTA_01.md L58, L61-62、MINIMUM L21。
- 推奨対応: (a)のMUST 3点。
- 採用で生じ得るFailure: Fableが読む量が増え、Fable自身が作業者化する。量の上限(ディレクトリ走査・全文ログの禁止)は維持する。

**OF-D2-10 [MINOR]** 失敗経路の確認をGate 3に置いても、承認前の配線(KGORAの型)では発火しない
- 根拠: PM_GOVERNANCE.md L182-183、AUDIT_REPORT_01.md L39-40。
- 推奨対応: Gate 7とW7(設計時)を主とし、§6「安全≠成功」の失敗経路版として書く。
- 採用で生じ得るFailure: なし。

**OF-D2-11 [MAJOR]** D1(検証専用委任)とSonnetループ上限(4回)の関係が未定義
- 内容: カウントすれば上限到達を早めてU2の発火を増やす。カウントしなければ抜け道になる。
- 根拠: AGENT_ROLE_DELTA_01.md L37, L45、PM_GOVERNANCE.md L1733-1736(該当記述をGrepで検索し、0件)。
- 推奨対応: 「D1は編集・実装禁止の検証専用で、別カウント。1回の受入につき最大1〜2回」と明記する。
- 採用で生じ得るFailure: 検証専用委任が実装に流用される。委任文で「編集禁止」を固定し、受入時にgit状態に変化がないことを確認する。

**OF-D2-12 [MINOR]** STOP文言の統一(W2(d))が曖昧で、Sonnetが自分で適用範囲を判断する余地が残る
- 根拠: MINIMUM L20、tools/stop_scope_check_01.py L20-21(`--run-dir`が必須)。
- 推奨対応: (f) D-7のとおり、helperの実行義務と、run-dirのない作業での扱いを明記する。
- 採用で生じ得るFailure: run-dirのない作業での誤停止。この場合は全NOTICEを適用とみなすので安全側。

**OF-D2-13 [MINOR]** §11 L1872「失敗・副作用…が発生した場合のみUDRとしてSTOP」が、W4/W5bの修正対象から漏れている
- 根拠: PM_GOVERNANCE.md L1872-1874。
- 推奨対応: W4の対象に追加する。
- 採用で生じ得るFailure: なし。

**OF-D2-14 [MINOR]** W7の不足
- 内容: Opus packetに「承認状況・Production到達経路か」欄がない。Sonnet報告に「撤去・残置のGrep」行がない。
- 根拠: MINIMUM L26、GATE_MECHANISM_MAP_01.md L99, L106, L128。
- 推奨対応: それぞれ1行追加する。
- 採用で生じ得るFailure: 委任文が2行長くなる。

**OF-D2-15 [MINOR]** D-3: 観点11の注記をpacket側だけに置くと、テンプレートを使わない依頼で欠落する
- 根拠: RECONCILIATION L82。
- 推奨対応: U4の任意項目としてブロック本体への1行追加を提示する。
- 採用で生じ得るFailure: ユーザー決定の正本を改変することになる(承認があれば問題ない)。

**OF-D2-16 [MINOR]** D-1のB案は、ユーザー承認済み機能(haiku-worker)の事実上の廃止になるが、その旨を開示していない
- 根拠: RECONCILIATION L80、CLAUDE.md L84-88、PM_GOVERNANCE.md L155。
- 推奨対応: A/BをU3(c)の選択肢として明示する。A案は1語の追加で済む。
- 採用で生じ得るFailure: A案は実機で起動できるかが未確認。

**OF-D2-17 [MINOR]** 原則4がSonnetの作業範囲拡大を誘発しうる
- 根拠: CHARTER_DRAFT_01.md L18、sonnet-worker.md L12-14。
- 推奨対応: 「委任範囲内で」を追記する。
- 採用で生じ得るFailure: なし。

**OF-D2-18 [MINOR]** W6の欄名「承認済み指示(逐語要旨)」は、逐語と要旨が矛盾している。T9の原因は要約による変形だった
- 根拠: MINIMUM L25。
- 推奨対応: 「原文引用+DECISION_LOG出典」の欄にする。
- 採用で生じ得るFailure: ヘッダが長くなる。

**OF-D2-19 [MINOR]** リプレイ試験は結論を知った状態での再現で、Fableが手順を守るかを測れない
- 根拠: GATE_MECHANISM_MAP_01.md L134、MINIMUM L96。
- 推奨対応: (j)の盲検リプレイ、陰性対照、事後実測。
- 採用で生じ得るFailure: 試験が約1h増える。

**OF-D2-20 [MINOR]** W5b(曖昧語の例示化)の整合リスクが高く、今回の不全の原因でもない
- 根拠: MINIMUM L24、RULE_CHANGE_MATRIX_01.md L135。
- 推奨対応: 後回しにし、Day3-4は参照の追記だけにする。
- 採用で生じ得るFailure: 7箇所の散在がしばらく残る(不全の原因ではない)。

**OF-D2-21 [MINOR]** U3が5項目を束ねており、安全文言の変更前と変更後の実文がユーザーに提示されていない
- 根拠: USER_DECISIONS L66-78, L106-107。
- 推奨対応: U3(d)を分離し、3つの文言について変更前と変更後の実文を添える。
- 採用で生じ得るFailure: 判断項目が1つ増える。

**OF-D2-22 [MINOR]** 既定ONフラグ約12件の突合(P13)を後回しにしている
- 内容: ユーザーの最重要指示(未承認Production変更の防止)に直結し、JPY0・約1hでできる。
- 根拠: GATE_MECHANISM_MAP_01.md L64-73。
- 推奨対応: Day5のリプレイ試験に含める。
- 採用で生じ得るFailure: 承認根拠が見つからないflagが出た場合、扱いの判断が新たに必要になる(ユーザー判断ではなく、まずFableの技術判断で既定OFF化を検討する)。

---

## 5. 代替案

1. **防壁の順序を逆にする**: 第1の防壁=設計時(W7: 目的1文、失敗終了時の最終成果物、承認状況、旧ルール撤去。Opus所見の採否時に照合1行)。第2の防壁=受入時(F3)。F3は、観測値の引用とユーザー報告への掲載で、内容を検査できる形にする。tool回数のような形式要件は置かない。
2. **判断区分の正本**: PM_GOVERNANCEの1節に置く。Charterは要約と参照だけを持つ。W5bは後回し。
3. **U2**: 「条件B該当ならOpusが先」「再計画後の委任上限(数値はユーザー承認)」「2度目の到達でSTOP」の3点を固定する。
4. **既定OFF例外**: (e)の5条件付きの限定例外とし、単独のユーザー判断にする(例外を置かない案も選択肢として提示)。
5. **必須8単位+欠けていた4つの最小追記**(OF-D2-13/14、受入記録の報告掲載、D1の別カウント)。CPは約2.7hに短縮できる。

---

## 6. ユーザー承認前に解消すべき未確認事項

1. 「上限到達=UDR」の原文承認の有無(DECISION_LOG_HISTORYのLOOP-03全文)。11-1 L2047-2049のユーザー原文との関係も合わせて確認。
2. OF-D2-01〜09・11の文言修正の反映。特にBLOCKER 01と、安全境界に関わる02/03/05/06/07。
3. U2の再計画後の委任上限の数値案。D1を別カウントとする文言。
4. W2(c)の5条件の最終文言と、Charter L30との一致。
5. sandwich-pmの`Agent(...)`許可リストが実際にhaikuを拒否するか(D-1をA案にするなら実機で確認)。
6. 受入記録を9-0固定5節のどこに置くか。

---

## 7. 確認した範囲/確認していない範囲

**確認した範囲(Read/Grep)**:
- DAY2_DESIGN_RECONCILIATION_01.md、MINIMUM_CHANGE_PLAN_01.md、USER_DECISIONS_01.md、CHARTER_DRAFT_01.md、AGENT_ROLE_DELTA_01.md(いずれも全文)
- GATE_MECHANISM_MAP_01.md(全文)、RULE_CHANGE_MATRIX_01.md §2〜§5
- .claude/agents/sandwich-pm.md、.claude/agents/sonnet-worker.md、CLAUDE.md(いずれも全文)
- PM_GOVERNANCE.md: §1 L132-163、Gate 1〜7 L164-246、§6 L606-610、10-1/10-2 L1662-1715、§11 L1725-1884、11-1 L2030-2049、11-3 L2123-2272、11-4/11-5 L2315-2334、12-2 L2349-2354、26節 L3215-3242
- AUDIT_REPORT_01.md(超サマリ、§1、§6〜§10)
- tools/stop_scope_check_01.py L1-60

**確認していない範囲**:
- PM_BRIEF.md(L110・L214-279)
- docs/pm/templates/の3ファイル本文
- USER_DECISION_REGISTER_01.md
- PM_GOVERNANCE 14-3・§19・12-13・9-0本文・7-7/7-8
- DECISION_LOG(LOOP-03・2026-10-15の各決定の原文)
- OPUS_REQUEST_AND_FINDINGS_VERBATIM_01.md
- stop_scope_check_01.pyの61行目以降とtest
- RULE_CHANGE_MATRIX §1の57行表
- 実機の挙動(Agent許可リスト、`--agent`での定義反映)

上記のうち、W4/W6の行番号の正確さと、テンプレートの既存欄との衝突有無は、実装時の受入で実際のファイルを読んで確認する必要がある。

本レビューは採用可否を判断しない。次工程へ進むかは、sandwich-pmが11-3節に従って判断する。なお本レビューは、Claude案と重要な結論が対立する点(OF-D2-01・02・05など)を含むため、11-3のSTOP条件(1)(L2251)に該当しうる。
