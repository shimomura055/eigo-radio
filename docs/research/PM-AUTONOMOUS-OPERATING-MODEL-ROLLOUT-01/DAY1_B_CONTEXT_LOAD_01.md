# DAY1_B 読み込み量・頻度の実測調査(管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day 1 委任_01B)

日付2026-10-14。read-only、JPY0。区分: **[実測]**=ログ/ファイルから直接計測、**[推定]**=仕様や換算による推定、**[未確認]**。
データ源: セッションログ `f2c17cf7-...jsonl`(2026-10-07〜14、Fable=claude-fable-5-1、API呼出1,251件、ユーザー指示243件)。他セッションの初回turnも併用。集計script・中間結果はscratchpad(`rollout_b/`)。本文は転記せず数値のみ。

## 1. 起動時の読込量(現在の文字数、改行込みlen())

| 区分 | ファイル | 字数[実測] |
|---|---|---|
| 自動注入 | CLAUDE.md | 4,407 |
| 自動注入 | .claude/agents/sandwich-pm.md(frontmatter込) | 3,755 |
| 自動注入 | memory/MEMORY.md | 495 |
| 明示Read | docs/pm/PM_BRIEF.md | 11,184 |
| 明示Read | docs/pm/ACTIVE_TASK.md | 28,247 |
| 小計(起動時) | | **48,088** |
| 参考(委任後に読む) | RESULT_PACKET.md | 875 |

- 既存Research(INTERNAL_DIAGNOSIS §1-2)の「約48,500字」=CLAUDE+sandwich-pm+BRIEF+ACTIVE_TASK+RESULT_PACKET=48,468字で**再現できた**。訂正点: (a)RESULT_PACKETは起動時でなく委任後に読む(sandwich-pm.md手順1は BRIEF+ACTIVE_TASKのみ)ため起動時は48,088字(MEMORY込)。(b)ACTIVE_TASKが58.7%(28,247/48,088)、BRIEFが23.3%、自動注入3ファイル計8,657字(18.0%)。
- ACTIVE_TASK.md内訳[実測]: 固定ヘッダ(1-11行)1,181字、残り(「前タスク群(保持)」約30節)27,065字。つまり**復帰に必要な固定ヘッダは全体の4%**。PM_BRIEF: 1-92行(参照順序)3,838字、93行以降7,345字(Gate/ループ上限/固定ヘッダ書式等)。
- 増加傾向[実測]: 2026-10-07のセッション冒頭のRead結果はACTIVE_TASK 5,643字+PM_BRIEF 11,653字=17,296字。7日でACTIVE_TASKは約5倍(28,247字)。
- 参照のみ(自動では読まない)[実測]: PM_GOVERNANCE.md 156,897字(うち「変更履歴」31,222字、§11が23,912字、§9が19,228字、§2が13,156字)、CURRENT_SPEC.md 435,817字、OPEN_ITEMS.md 705,454字、DECISION_LOG.md 1,327,614字。settings.local.jsonは2,766字だが権限設定でありcontext注入は未確認。

## 2. Token実測(セッションログ usage 集計)

| 項目 | 値 | 区分 |
|---|---|---|
| (a) 初回assistant turnのinput系合計 | **13,821**(input 2 + cache_creation 13,819 + read 0) | 実測 |
| 同上、他のsandwich-pm新規セッション(9/9〜10/5の7件) | 9,644〜16,500(中央約11,900) | 実測 |
| (a)の位置づけ | Claude Codeのsystem prompt+tool定義+CLAUDE.md+agent.md+MEMORY+最初のユーザー文。**PM_BRIEF/ACTIVE_TASKのRead前**の値。内訳分離は不可 | 実測+未確認(内訳) |
| (b) ユーザー指示1回の最初のAPI呼出input(cache_read含む) | 平均200,831 / 中央173,395 / 最大465,189 | 実測(n=243) |
| (b') 同、cache_read除く(新規入力のみ) | 平均8,074 / 中央1,904 | 実測 |
| (b'') 指示1回あたり全API呼出の合計(平均5.1呼出) | input計 平均1,025,043(うちcache_read約97%)、新規(input+cache_creation) 平均29,194 / 中央12,585、output平均9,533 | 実測 |
| 全1,251呼出の合計 | input 14,482 / cache_creation 7,079,632 / cache_read 241,991,365 / output 2,316,513 | 実測 |
| (e) cache_read比率(input系合計に対し) | **97.15%**(cache_creation 2.84%、非キャッシュ0.006%) | 実測 |
| 1呼出あたり平均context | 199,109(中央180,938) | 実測 |
| (c) サブagent1件あたり `subagent_tokens` | 449件(重複除去)平均132,163 / 中央118,422 / 最大444,689 / 最小14,233 / 合計59,341,143。所要中央約600秒 | 実測(定義=cache read含むか否かは**未確認**) |
| (d) compact 15回 | 発動時context 201k〜473k(平均約358k)→compact後の要約 6.4k〜14.1k tokens。**直後の最初のAPI呼出input合計25,462〜45,570(平均31,844)**(cache_creation 19〜39k、cache_read 0または6,345) | 実測 |

注: 「ユーザー指示」は人間入力のうちtool_result/task-notification/メタ以外。キュー経由の自動入力が混じる可能性は**未確認**。1時間cache(ephemeral_1h)が使われている[実測]。

文字/token比[実測+推定]: Read結果長と次API呼出のinput増分の比(55件、並列Read等でノイズ大)の中央値は約**1.25字/token**。日本語比率85%前後の2ファイルでは約1.0字/token[実測n=2]。ASCII中心のJSONは約1.7。よって**日本語主体は1字≈1token前後**と置く[推定]。この比で現在の起動時48,088字≈**約38k〜48k token**、うちBRIEF+ACTIVE_TASK(39,431字)は約32k〜39k token[推定]。ただしこれは「初回turn 13.8k」への上乗せであり、実測の起動直後は約46k〜53k tokenになると推定(未実測: 現在値でのセッション起動は未実施)。

## 3. 同一セッション内の再送(仕様上の推定と実測の裏付け)

- 仕様上の推定: Claude Codeは毎回の呼出で会話履歴全体(system+過去turn+tool結果)を送り、prompt cacheにより再送分は安価なcache_readになる。
- 実測の裏付け: 再送分はcache_read(全input系の97.15%)に現れ、追加指示1回あたりの**新規**入力は中央12.6k・平均29.2k token。一方、指示1回の総送信量は平均約100万tokenで、**contextが大きいほど毎呼出の再送量(=cache_read)が増える**(平均約20万/呼出)。同一セッションで読んだ規則(48k字級)は以後ずっとcontextに残り、毎呼出cache_readに乗る。
- compactが約10〜11時間(15回/約6.5日)ごとに自動発動し(auto、上限は約47万付近)、その都度「復帰手順の再読」が発生する。

## 4. Fable→Worker/Opus委任時の読込

| 項目 | 字数 | 区分 |
|---|---|---|
| sonnet-worker.md / opus-consultant.md / haiku-worker.md | 1,503 / 1,417 / 1,272 | 実測 |
| CLAUDE.md(サブagentにも適用) | 4,407 | 実測(適用は仕様上の推定) |
| 委任文(docs/pm/delegation_log/2026-10-10〜14、n=215) | 中央1,152 / p75 2,250 / p90 5,729 / 最大40,492(FAMILY-X-COFFEE-KP-SELECTION-INVESTIGATION-01) / 5,000字超26件、10,000字超5件 | 実測(保存版の長さ。実送信文との差は未確認) |
| 委任1回の静的読込(sonnet-worker) | 約1,503+4,407+1,152=**約7,100字**(中央値ケース) | 推定 |
| 日別委任数(保存ファイル数) | 10/10: 33、10/11: 50、10/12: 65、10/13: 62、10/14: 5 | 実測 |
| サブagentが実際に消費するtoken | 上記(c): 平均132k/件。大半は委任後の調査・読込・実行で、起動時の静的読込(約2〜3k token相当)は支配的でない | 実測+推定 |

サブagentの初回turn規模(ログ上のsidechain)は本ログでは未収録(isSidechain=false のみ)のため**未確認**。サブagent側でPM_BRIEF/GOVERNANCEを読むかは委任文次第(委任文が参照指定したものを読む)。

## 5. 新セッション/compact復帰時

| 復帰手順 | 字数 | 区分 |
|---|---|---|
| CLAUDE.md復帰手順(1)ACTIVE_TASK固定ヘッダ | 1,181(ヘッダ部)。ただしReadは全体28,247字 | 実測 |
| (2)PM_BRIEF全文 | 11,184 | 実測 |
| 現状の復帰時の再読合計(+CLAUDE等自動注入8,657) | 約48,000字 | 実測 |
| 実測: compact直後の最初の呼出 | 25.5k〜45.6k token(平均31.8k)。復帰Read後に再び数万tokenが加わる | 実測 |

[事実] 復帰のたびにACTIVE_TASK全文(うち96%は「保持」された過去タスク)を読むため、固定ヘッダ(1,181字)で足りる局面でも約28kを消費する。

## 6. Prompt cacheと費用(区分して記述)

- Anthropic仕様: cache_read単価は通常inputの約10%、cache書込は5分cacheで約125%・1時間cacheで約200%(私の知識ベース)。**出典URLは本調査で取得できず「未確認」**(Web取得ツールなし)。Day 2で公式pricing/prompt-cachingページ(docs.claude.com 配下)で確認要。
- 固定月額契約下のClaude Codeは従量課金でない旨はユーザー委任文の前提[ユーザー申告]。契約形態自体はログ・設定から**未確認**。従って読込量は「費用」でなく「速度・context枯渇(compact頻度)・規則遵守精度」の問題。cache_creation(2.84%)とcompact頻度が時間(duration)面のコストとして残る。
- 開発コスト予算(API実行費)の対象は直接課金される開発用API実行費(OpenAI/Gemini/Azure等)。Claude Code利用は当面対象外の別管理候補(詳細はDAY1_D)。

## 7. 提案: イベント別の推奨読込量(設計目安。採否は未判断)

| イベント | 読む量の目安 | 読む内容(既存節の候補列挙) | 現状比 |
|---|---|---|---|
| セッション開始(常駐核) | 1,000〜2,000字+固定ヘッダ約1,200字 | 核候補: CLAUDE.md「説明方法」「Git運用」の要点、sandwich-pm.md「禁止・Production安全」、PM_GOVERNANCE §1責任分担/§6/§26-2・26-3(STOP)、PM_BRIEF「正式Status語彙」、報告マーカー規則(§9-8)、予算Capの位置づけ(§7-6)、`APPROVED_FOR_PRODUCTION`は人間のみ | 48,088→約3,500 |
| compact復帰 | 核+固定ヘッダ(1,181字)+現行管理IDの節のみ=約3,000〜5,000字 | ACTIVE_TASKの現行節、USER_DECISION_REGISTER該当行、REPORT_LEDGER確認 | 約48,000→約5,000 |
| 委任作成 | 核+委任文標準(D-2)+対象管理IDの要点=約2,000〜3,000字追加 | PM_BRIEF「委任文標準」「ループ上限」、DELEGATION_STANDARD_TEMPLATE | 要時のみ |
| 受入判定 | 約2,000〜3,000字追加(節単位Grep) | PM_GOVERNANCE §2 Gate、§11 Gatekeeper(各節全文でなく該当項目のみ) | §2は13.2k/§11は23.9k |
| ユーザー報告 | 約1,000〜1,500字追加 | §9報告フォーマット要点・マーカー、§12報告単位、REPORT_LEDGER | §9は19.2k |
| Opusレビュー起動 | 約2,000字追加 | §11-2/11-3(発火条件・観点)、委任文に論点を絞って記載 | |
| Worker(Sonnet)起動 | 静的約7,000字+委任文。STOP確認(§26-2)を委任文へ必須記載 | agent.md、CLAUDE.md(核化できれば縮小)、委任文 | 現状もこの規模 |

要点: 常駐核を数値目標内に収めるため、PM_BRIEFの規則再掲(93行以降7,345字)とACTIVE_TASKの「前タスク群(保持)」27,065字を常駐対象から外す設計が最大の効果(合計約34k字、起動時の約70%)。ただし削減はDay 2以降の設計判断。文字数のために重要規則(STOP条件・Production承認境界・予算Guardrail)は削らない。

## 8. 未確認事項
1. 初回turn 13.8kの内訳(system prompt/tool定義 vs 自動注入文書)。2. 現在の48k字構成でセッション起動した場合の実測token(未起動)。3. `subagent_tokens`の定義(cache read含有)。4. サブagent初回turnの実測。5. Anthropic cache単価の出典URL。6. 契約形態(固定月額)の確認。7. 「ユーザー指示」243件に自動入力が混じる程度。8. 委任文の実送信長(保存版との差)。9. settings.local.jsonがcontextへ入るか。
