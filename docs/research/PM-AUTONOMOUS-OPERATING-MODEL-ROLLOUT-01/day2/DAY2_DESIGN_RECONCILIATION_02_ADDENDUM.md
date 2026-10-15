# DAY2_DESIGN_RECONCILIATION_02_ADDENDUM: v1への追補(Opus条件A所見の反映)
管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day2 Phase A 委任_D / 2026-10-15 / Status上限: DAY2_PHASE_A_V2_COMPLETE
性質: v1(`DAY2_DESIGN_RECONCILIATION_01.md`)への**追補**。v1本体・A(`RULE_CHANGE_MATRIX_01.md`)・B(`AGENT_ROLE_DELTA_01.md`/`GATE_MECHANISM_MAP_01.md`)は編集していない(履歴として残す)。規則・Agent定義・SSOT・Production無変更、JPY0。
表記: [確認]=本委任で一次ファイルを読んだ、[未確認]=確認できていない。

## §1 所見→変更対応表(OF-D2-01〜22)
反映状況: 反映済み=22件、一部=0件、未反映=0件(すべてFable採否表のとおり設計文書v2に反映した。規則・SSOT・Agent定義への反映は承認後)。台帳行は`OPUS_FINDINGS_D2_LEDGER_DRAFT_01.md`。
| 所見 | 区分 | 反映先(v2、ファイル:節) | 状況 |
|---|---|---|---|
| OF-D2-01 | BLOCKER | `CHARTER_DRAFT_02.md` §1【人間に判断を求めるのは主に次】・§2#1。`MINIMUM_CHANGE_PLAN_02.md` §0・§3 P15(旧W5b撤回) | 反映済み |
| OF-D2-02 | MAJOR | `USER_DECISIONS_02.md` U2(追加委任最大2回・数値選択・必ずSTOP) | 反映済み |
| OF-D2-03 | MAJOR | 同 U2案A(1)(条件B該当はOpus先行) | 反映済み |
| OF-D2-04 | MAJOR | 同 U2(変更前の逐語4点・案A/B/C/D・L3診断後と11-1 STOP(3)の開示) | 反映済み |
| OF-D2-05 | MAJOR | 同 U3'(一般化の明示・5条件・例外なし案B)。`CHARTER_DRAFT_02.md` §1第2項・§2#4 | 反映済み |
| OF-D2-06 | MAJOR | 同 U4(a)(11-3の5条件維持+追加型。逐語並記)。`MINIMUM_CHANGE_PLAN_02.md` W5a(d) | 反映済み |
| OF-D2-07 | MAJOR | 同 U3(b)。`MINIMUM_CHANGE_PLAN_02.md` W2 | 反映済み |
| OF-D2-08 | MAJOR | `CHARTER_DRAFT_02.md` §1原則4 | 反映済み |
| OF-D2-09 | MAJOR | `USER_DECISIONS_02.md` U3(a)。`MINIMUM_CHANGE_PLAN_02.md` W3 | 反映済み |
| OF-D2-10 | MINOR | `MINIMUM_CHANGE_PLAN_02.md` W5a(b)。`USER_DECISIONS_02.md` U4(a) | 反映済み |
| OF-D2-11 | MAJOR | `USER_DECISIONS_02.md` U2(3)・U3(a) | 反映済み |
| OF-D2-12 | MINOR | 同 U3(e)。`MINIMUM_CHANGE_PLAN_02.md` W2 | 反映済み |
| OF-D2-13 | MINOR | `MINIMUM_CHANGE_PLAN_02.md` W4。`USER_DECISIONS_02.md` U2「この変更が及ぶ範囲」 | 反映済み |
| OF-D2-14 | MINOR | `MINIMUM_CHANGE_PLAN_02.md` W2(b)・W7(現行`OPUS_CONTEXT_PACKET_TEMPLATE.md`に承認状況欄が無いことをGrepで確認) | 反映済み |
| OF-D2-15 | MINOR | `USER_DECISIONS_02.md` U4(c)。`MINIMUM_CHANGE_PLAN_02.md` O4 | 反映済み |
| OF-D2-16 | MINOR | `USER_DECISIONS_02.md` U3(c) | 反映済み |
| OF-D2-17 | MINOR | `CHARTER_DRAFT_02.md` §1原則4 | 反映済み |
| OF-D2-18 | MINOR | `MINIMUM_CHANGE_PLAN_02.md` W6。`USER_DECISIONS_02.md` §2 T12 | 反映済み |
| OF-D2-19 | MINOR | `MINIMUM_CHANGE_PLAN_02.md` §5。`USER_DECISIONS_02.md` §2 T7 | 反映済み |
| OF-D2-20 | MINOR | `MINIMUM_CHANGE_PLAN_02.md` §0・§3 P15 | 反映済み |
| OF-D2-21 | MINOR | `USER_DECISIONS_02.md` §1参考・U1・U2・U3'(変更前/変更後の逐語並記) | 反映済み |
| OF-D2-22 | MINOR | `MINIMUM_CHANGE_PLAN_02.md` §3・§5(4)。`USER_DECISIONS_02.md` §2 T8 | 反映済み |
代替案5(CP短縮): S-aを2分割(S-a1/S-a2)、さらにS-cをS-c1/S-c2に分け、CP=S-b約2.9h(Opus試算2.7hに所見反映の追加0.2hを加算)。`MINIMUM_CHANGE_PLAN_02.md` §6。

### Opus「ユーザー承認前に解消すべき未確認事項」6件の解決状況
| # | 内容 | 状況 |
|---|---|---|
| 1 | 「上限到達=UDR」の原文承認の有無 | 解決: `USER_DECISIONS_02.md` §0 D13。LOOP-03のエントリ(`DECISION_LOG_HISTORY.md` L498〜)に到達時の動作の記載はなく、「到達=UDR」はサンドイッチ導入時(commit 12989ecb7、2026-09-05)の運営文書の記述。個別のユーザー原文は未確認(会話ログ全体の検索はしていない)。11-1 L2047-2049の「変更・拡張されない」は原文引用の外側の記録側注記 |
| 2 | OF-D2-01〜09・11の反映 | 解決: 上表 |
| 3 | U2の再計画後の委任上限の数値案・D1の別カウント | 解決: 推奨=追加最大2回、D1は別枠(1受入最大2回)。数値は承認事項 |
| 4 | W2(c)の5条件の最終文言とCharter L30の一致 | 解決: `USER_DECISIONS_02.md` U3'(案A実文)と`CHARTER_DRAFT_02.md` §1第2項(短縮形)で5条件の項目が一致 |
| 5 | `Agent(...)`許可リストが実際にhaikuを拒否するか | **未確認のまま**。U3(c)案Aは実機確認が前提と明記。本セッション(Sonnet)の起動可能一覧にhaiku-workerがあるかの確認も未実施(Fableの申告のみ)。承認後のW3実装時に実機確認 |
| 6 | 受入記録を9-0固定5節のどこに置くか | 案を提示: 「1 結論」の末尾に`受入記録:`見出しで3行(5節順序は不変)。代替=5節後の補足。Fableが最終決定(`USER_DECISIONS_02.md` U3(a)) |

## §2 裁定D-1〜D-7の更新(v1 §3-2に対する追補)
| ID | v1裁定 | v2での扱い(Opus所見) |
|---|---|---|
| D-1 | B案(本文のhaiku記述を整理) | **A案(tools欄に`haiku-worker`追加、1語)を推奨に変更し、A/BをU3(c)でユーザーに選ばせる**。B案は2026-09-10に承認された機能の事実上の廃止になり、`CLAUDE.md` L84-88・`PM_GOVERNANCE.md` L155に食い違いが残ることを明示(OF-D2-16)。A案は実機で起動できるかが未確認 |
| D-2 | B案を主、A案を補助 | 方向維持。ただし置換文の「Worker記載パスに限る」を**削除**。制限は「量」のみ。観測値の引用必須、受入記録のユーザー報告本体掲載、tool回数要件なし(OF-D2-09) |
| D-3 | packet(a)欄のみ、ブロック本体は無改変 | **一部修正**: (a)欄のみは維持するが、テンプレートを使わない依頼で欠落するため、**ブロック本体への1行追加をU4(c)の任意項目**として提示(承認が得られた場合のみ。OF-D2-15) |
| D-4 | 厳しい側に統一 | 維持(Opus賛成) |
| D-5 | Gate 7へ集約、2段階 | 維持+追加: 失敗経路のない変更は「N/A+理由」を許す。D1は別カウント(編集・実装禁止、1受入最大2回、git状態無変化確認)。OF-D2-11 |
| D-6 | 自動抽出script等は見送り | 維持(Opus賛成) |
| D-7 | helperは実装済み、文言統一のみ | **文言を具体化**: Sonnetはhelperを**Bashで実行**しrc=3で停止/NOTICE本文を自分で解釈しない/helper実行不可またはrun-dirなしの作業では全NOTICEを適用(fail-closed)。26-2(d)をhelperに揃えると適用範囲は広がる(安全側)。OF-D2-12 |
v1 §4の補足(a)「12-2は報告単位が対象なので競合しない」は**修正**: 12-2はblocker・重要な途中結果を明示的にトリガとするため、Charter原則4の括弧にblocker・12-2の即時報告対象を追記して整合させた(OF-D2-08)。

## §3 A/B文書の記述で、改訂が必要な箇所の一覧(A/B本体は編集しない)
承認後の実装委任・Fable受入では、下表の旧記述を**使わない**(v2側を正とする)。
| 文書 | 箇所 | 旧記述 | v2での扱い |
|---|---|---|---|
| `AGENT_ROLE_DELTA_01.md` §1 F3 | 変更案(L29の置換文) | 「読取対象は委任文またはRESULT_PACKETに記載されたパス・行に限る」 | 削除。量のみ制限(OF-D2-09) |
| 同 §1 F3 | 手順4-2 | 「少なくとも1回のtool使用で」 | tool回数要件を置かない。観測値引用必須 |
| 同 §1 F3 | 記録先 | 「次の委任文冒頭」のみ(ユーザー報告は「要約」) | 固定見出し`受入記録:`でユーザー報告本体にも載せる |
| 同 §2-2 | Sonnet原因究明ループ「2周まで自力で」 | 26節への言及なし | 「有料run・外部停止process・STOP該当時は26節を優先し再現のための再実行をしない」を追加(OF-D2-07) |
| 同 §1 F3・§5 | D1(検証専用委任)の回数 | 上限との関係が未定義 | 別カウント、1受入最大2回、編集・実装禁止(OF-D2-11) |
| 同 §2/§5 | 案(haiku-worker削除側を推奨) | B案推奨 | A案推奨、U3(c)で選択 |
| 同 §2-3 | 既存仕様整合3行 | 3行 | 4行(撤去・残置Grep行を追加。OF-D2-14) |
| `GATE_MECHANISM_MAP_01.md` §5/§6 | 失敗経路の確認をGate 3に置く案 | Gate 3中心 | Gate 7+設計時(W7)が主、Gate 3は補助(OF-D2-10) |
| 同 §6-3 | P13(約12件突合)を後回し | 後回し | Day5試験に含める(OF-D2-22) |
| 同 L149付近 | 受入記録の検索性が未設計 | 未設計 | 固定見出し`受入記録:`で解決 |
| `RULE_CHANGE_MATRIX_01.md` | R34,R36,R45,R49→W5b | 必須 | 後回し(P15)。矛盾箇所のみW4で修正 |
| `DAY2_DESIGN_RECONCILIATION_01.md` §0-4,§0-5,§2,§4 | 「判断4点+非ブロッキング2点」「W5b」 | v1 | 判断5点(U1,U2,U3,U3',U4)+非ブロッキング(U4(b)(c),U5,U6) |
| 同 §3-2 D-1,D-2,D-3,D-5,D-7 | 上表 | v1 | §2のとおり |
| 同 §4(a) | 12-2は競合しない | 競合しない | blockerが競合しうるため括弧に追記 |
| 同 §5 #1 | LOOP-03原文未再確認 | 未確認 | 解決(§1表#1) |
| `MINIMUM_CHANGE_PLAN_01.md` | W5b、工数11.2h、CP4.7h、リプレイ試験 | v1 | v2: 8単位、10.3h、CP2.9h、盲検リプレイ |
| `USER_DECISIONS_01.md` | U1〜U4、超サマリ | v1 | v2。U3(d)→U3'分離、U2再構成 |
| `CHARTER_DRAFT_01.md` | L18原則4、L24、L30 | v1 | v2 |

## §4 未確認
1. haiku-workerを実機で起動できるか([未確認]。U3(c)A案の前提)。
2. 「到達=UDR」を個別に指示したユーザー原文の有無([未確認]。`DECISION_LOG*`と`PM_GOVERNANCE.md`のLOOP-03周辺・上限到達の語のGrepでは見つからなかった。会話ログ全体は未検索)。
3. 追加委任の数値(最大2回)の妥当性は設計推定であり、実績データによる裏付けはない(Opus例示に従った推奨値)。
4. 盲検リプレイの「欠陥前の材料」(3b64e5632時点の状態・Opus所見原文・a337d8acc hand-back)がそのまま再構成できるかは未確認(Day5で確認)。
5. v1の未確認事項(Gate 1〜7個別項目・Closeout 31項目の網羅精査、`CURRENT_SPEC.md`のDangling Reference Check本文)は継承。
