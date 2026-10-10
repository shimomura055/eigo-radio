# RESULT_01: WRITER-RISK-FLAGGER-META-ROLLBACK-CROSSMODEL-01(Phase 2、2026-10-10、MEASURED、Trial/DEVのみ)

Production・CURRENT_SPEC・Promptは変更していない。Status4件(A3+A4英訳後配置=VALIDATED / R0後Hard STOP除去・翻訳後Hard STOP除去・新Writer+Checkerなし+A3/A4+Human Review=APPROVED_FOR_PRODUCTION・未PRODUCTION_WIRED)は不変更。各条件A3/A4各1回(N=1x2、一般化・再現性は未評価)。結果を見た再実行なし。

## 0. 非エンジニア向け要約

- 何を調べたか: Metaの実在記事の1文「人間コンシェルジュ機能を元に戻した」(台帳では逆で、機能を当面ロールバック=撤回)を、モデルだけを替えた8条件のA3/A4が拾えるかを各1回ずつ確認した。
- 拾えた(方向反転を明示): Luna、Gemini 3.5 Flash-Lite、Gemini 3.8 Flash、Claude Haiku 4.5、Claude Sonnet 5。Claude Sonnet 5・Gemini 3.5 Flash-Lite・LunaはA3/A4の両方で方向反転を明示した(Haikuは両方でFlagしたが方向反転の明示はA3のみ、Gemini 3.8 FlashはA3のみFlag)。
- 部分的: DeepSeek V4 Flash(A4で文はFlagしたが方向の食い違いを断定せず。A3は出力形式不正で評価不能)。
- 拾えなかった: Sol(前回に続き両方で未検出)、DeepSeek V4 Flash Thinking(A3は別の文のみ、A4は出力が途中で切れて評価不能)。
- 費用: 合計JPY30.90(見積 低13.60/中央18.32/高位47.92。中央より高く高位より低い)。最も安い成功例はGemini 3.5 Flash-LiteのJPY0.54、最も高いのはClaude Sonnet 5のJPY11.34。
- 注意: 各条件1回ずつの結果であり、モデルの優劣や再現性を断定するものではない。DeepSeekの2条件は出力形式の失敗(判定不能)が含まれる。

## 1. 最終比較表(ユーザー指定形式)

| Model | actual model_id | A3対象文 Yes/No | A4対象文 Yes/No | 方向反転認識 Yes/Partial/No | 主な理由(要約。原文は3節) | 費用JPY(2call実費) |
|---|---|---|---|---|---|---|
| Luna | `gpt-6-luna` | Yes | Yes | A3 Yes / A4 Yes -> **Yes**(DETECTED) | 台帳のrollbackに対し本文は「機能を再開した」意味に読める、と明示(A3 conf .97、A4は.30と低信頼) | 0.42 |
| Sol | `gpt-6.1-sol` | No | No | A3 No / A4 No -> **No**(NOT_DETECTED) | s23未Flag。他Flagはs3/s14/s15等(前回と同傾向) | 5.78 |
| Gemini 3.5 Flash-Lite | `gemini-3.5-flash-lite` | Yes | Yes | A3 Yes / A4 Yes -> **Yes**(DETECTED) | 台帳の「当面rollback」に対し本文「元に戻した」は停止/撤回の逆、と明示(thinking 0 tokensで2call計JPY0.54) | 0.54 |
| Gemini 3.8 Flash | `gemini-3.8-flash` | Yes | No | A3 Yes / A4 No -> **Yes**(DETECTED) | 台帳(提供縮小・停止)に対し本文が「以前の状態に復元」と反転表現、と明示。A4はs23未Flag | 3.86 |
| DeepSeek V4 Flash | `deepseek-flash` | No(出力無効) | Yes | A3 No(無効) / A4 Partial -> **Partial**(PARTIALLY_DETECTED) | A3は出力無効(type enum違反x2)。A4はrollback反転でFlagしたが「同じ方向を表しているか確認が必要」止まり(Partial) | 1.04 |
| DeepSeek V4 Flash Thinking | `deepseek-flash` | No | No(出力無効) | A3 No / A4 No(無効) -> **No**(NOT_DETECTED) | A3はs3のみFlag(s23なし)。A4はreasoning 8000tokで2回とも出力打切り(無効、評価不能) | 5.05 |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` | Yes | Yes | A3 Yes / A4 Partial -> **Yes**(DETECTED) | A3は「rollback(機能を当面停止)したのでは」と明示。A4は「以前の状態」の指す先を問う形(Partial) | 2.86 |
| Claude Sonnet 5 | `claude-sonnet-5` | Yes | Yes | A3 Yes / A4 Yes -> **Yes**(DETECTED) | 台帳「当面rollback(停止)」に対し本文は機能を再開・維持したかの逆の印象、と明示(A3/A4とも) | 11.34 |

合計 JPY30.90。Closeout: DETECTED=総合Yes、PARTIALLY_DETECTED=Partial、NOT_DETECTED=No。UNAVAILABLE=0件(全8条件で呼び出し成功、403/404なし、置換なし)。

判定は事前登録(PREREGISTRATION_01.md 7節)の語基準で機械判定(`aggregate_xm_01.py`、人間確認なし)。Yes=台帳側語(ロールバック/rollback/撤回/保留/当面/停止等)+本文側語(restore/復元/元に戻/以前の状態/再開等)+食い違い語(逆/反転/ではなく/読め/ありますが等)の3群すべてをreasonに含む。Partial=s23をFlagしたが上記を満たさない。No=s23未Flag(出力無効を含む)。境界例: Haiku A4とDeepSeek V4 Flash A4はPartial(語基準で厳格に判定、緩く読めばYesの余地あり)。総合判定への影響: HaikuはA3がYesのため総合Yes不変、DeepSeek V4 Flashは緩く読むと総合Partial->Yesになり得る。

## 2. 整理リスト

- A3で拾えた(s23をFlag): Luna、Gemini 3.5 Flash-Lite、Gemini 3.8 Flash、Claude Haiku 4.5、Claude Sonnet 5
- A4で拾えた(s23をFlag): Luna、Gemini 3.5 Flash-Lite、DeepSeek V4 Flash、Claude Haiku 4.5、Claude Sonnet 5
- 両方で拾えた: Luna、Gemini 3.5 Flash-Lite、Claude Haiku 4.5、Claude Sonnet 5
- Flagはしたが方向反転を認識していない(総合Partial): DeepSeek V4 Flash
- 完全未検出(No): Sol、DeepSeek V4 Flash Thinking(DeepSeek V4 Flash ThinkingはA4が出力無効のため実質A3のみの評価)
- UNAVAILABLE: なし

## 3. s23のFlag詳細(reason原文、全文)

- **Luna A3**: type=`rollback反転` / confidence=0.97 / related Fact=MUSE-HC-012(MUSE-HC-012=台帳「人間コンシェルジュ機能を当面ロールバック」) / 判定=Yes
  - reason: 「restored the human concierge feature」は機能を再開した意味に読めますが、Factでは人間コンシェルジュ機能を当面ロールバックしたのではありませんか。
- **Luna A4**: type=`rollback反転` / confidence=0.3 / related Fact=MUSE-HC-012(MUSE-HC-012=台帳「人間コンシェルジュ機能を当面ロールバック」) / 判定=Yes
  - reason: “restored the human concierge feature”は、台帳の「人間コンシェルジュ機能をロールバックした」と逆に、機能を再開したように読める文ではありませんか。
- **Sol A3**: s23未Flag
- **Sol A4**: s23未Flag
- **Gemini 3.5 Flash-Lite A3**: type=`その他` / confidence=0.7 / related Fact=MUSE-HC-012(MUSE-HC-012=台帳「人間コンシェルジュ機能を当面ロールバック」) / 判定=Yes
  - reason: Metaが人間コンシェルジュ機能を「元の状態に戻した（restored... to the way it had been before）」とありますが、台帳Fact-012では「ロールバックした（当面ロールバックした）」とされています。機能をもとに戻したのではなく停止・撤回したという意味ではありませんか？
- **Gemini 3.5 Flash-Lite A4**: type=`rollback反転` / confidence=0.8 / related Fact=MUSE-HC-012(MUSE-HC-012=台帳「人間コンシェルジュ機能を当面ロールバック」) / 判定=Yes
  - reason: 「restored the human concierge feature to the way it had been before」とありますが、台帳では「ロールバックした(rolled back)」とされていませんか。
- **Gemini 3.8 Flash A3**: type=`rollback反転` / confidence=0.85 / related Fact=MUSE-HC-012(MUSE-HC-012=台帳「人間コンシェルジュ機能を当面ロールバック」) / 判定=Yes
  - reason: 台帳では人間コンシェルジュ機能そのものが当面ロールバック（取り下げ・無効化）されたとされていますが、文中では「人間コンシェルジュ機能を以前の状態に復元した」と反転して表現されていませんか。
- **Gemini 3.8 Flash A4**: s23未Flag
- **DeepSeek V4 Flash A3**: s23未Flag(出力無効: validate_flags不合格のため集計対象外)
- **DeepSeek V4 Flash A4**: type=`rollback反転` / confidence=0.4 / related Fact=MUSE-HC-012(MUSE-HC-012=台帳「人間コンシェルジュ機能を当面ロールバック」) / 判定=Partial
  - reason: 『restored the human concierge feature to the way it had been before』が、台帳の『機能を当面ロールバックした』と同じ向きの動作を表しているか確認が必要ではありませんか？
- **DeepSeek V4 Flash Thinking A3**: s23未Flag
- **DeepSeek V4 Flash Thinking A4**: s23未Flag(出力無効: validate_flags不合格のため集計対象外)
- **Claude Haiku 4.5 A3**: type=`rollback反転` / confidence=0.85 / related Fact=MUSE-HC-012(MUSE-HC-012=台帳「人間コンシェルジュ機能を当面ロールバック」) / 判定=Yes
  - reason: 「restored the human concierge feature to the way it had been before」という表現は、機能を「復旧した」という意味に読めますが、実際には「ロールバック（機能を当面停止）した」のではありませんか？
- **Claude Haiku 4.5 A4**: type=`rollback反転` / confidence=0.7 / related Fact=MUSE-HC-012(MUSE-HC-012=台帳「人間コンシェルジュ機能を当面ロールバック」) / 判定=Partial
  - reason: 「人間コンシェルジュ機能を以前の状態に戻した」という表現は、台帳の「機能をロールバックした」という説明と一致していますか？「以前の状態」が何を指すのか、ロールバック前の状態と相違ないでしょうか？
- **Claude Sonnet 5 A3**: type=`rollback反転` / confidence=0.45 / related Fact=MUSE-HC-012(MUSE-HC-012=台帳「人間コンシェルジュ機能を当面ロールバック」) / 判定=Yes
  - reason: 台帳では『機能を当面ロールバック(停止)した』とありますが、本文の『人間コンシェルジュ機能を以前の状態に“復元”した』という表現は、機能を停止・取りやめた事実と逆の印象を与えませんか。
- **Claude Sonnet 5 A4**: type=`rollback反転` / confidence=0.55 / related Fact=MUSE-HC-012(MUSE-HC-012=台帳「人間コンシェルジュ機能を当面ロールバック」) / 判定=Yes
  - reason: 台帳では人間コンシェルジュ機能を『ロールバックした(当面停止した)』とありますが、この文の『以前の状態に戻した(restored)』という表現は機能を再開・継続しているかのように読めてしまうのではありませんか?

### 3-1. 参考: 出力無効(validate_flags不合格)だった回の中身(集計対象外、判定は変更しない)

- DeepSeek V4 Flash A3: 違反=type enum外(`範囲の広げ縮め`等、許可語彙外)
  - attempt1: 無効出力内にs23のFlagあり: type=rollback反転 conf=0.7; type=範囲の広げ縮め conf=0.4
  - attempt2: 無効出力内にs23のFlagあり: type=rollback反転 conf=0.3
- DeepSeek V4 Flash Thinking A4: 違反=finish_reason=length(max 8000 tokをreasoningが使い切り、content空または不完全)
  - attempt1: s23 Flagなし/解釈不能(JSONとして解釈不能/空(JSONDecodeError))
  - attempt2: s23 Flagなし/解釈不能(JSONとして解釈不能/空(JSONDecodeError))

注: DeepSeek V4 Flash A3は無効出力(2回とも)の中にs23の「rollback反転」Flagが含まれていたが、type enum違反で現行validate_flagsが却下する出力であり、既存機構(format再試行1回)後も無効だったため、主指標ではNo(出力無効)のまま。

## 4. 他Flag(s23以外)一覧(評価指標ではない。件数が多い=優秀とは扱わない)

| Model | A3 他Flag(文ID:type:conf) | A4 他Flag |
|---|---|---|
| Luna | 3件(s3:その他:0.84, s14:不在断定:0.34, s15:その他:0.32) | 4件(s3:主体対象入替:0.38, s14:不在断定:0.72, s15:不在断定:0.55, s19:数量時系列:0.34) |
| Sol | 5件(s3:主体対象入替:0.4, s14:主体対象入替:0.93, s14:不在断定:0.72, s15:主体対象入替:0.91, s19:数量時系列:0.45) | 5件(s3:主体対象入替:0.58, s10:否定反転:0.48, s14:主体対象入替:0.94, s14:不在断定:0.76, s15:主体対象入替:0.9) |
| Gemini 3.5 Flash-Lite | 0件() | 0件() |
| Gemini 3.8 Flash | 1件(s14:主体対象入替:0.75) | 2件(s14:主体対象入替:0.7, s15:主体対象入替:0.7) |
| DeepSeek V4 Flash | (出力無効) | 8件(s6:その他:0.4, s6:その他:0.3, s8:その他:0.2, s14:その他:0.35, s17:その他:0.3, s19:その他:0.3, s22:主体対象入替:0.5, s29:その他:0.35) |
| DeepSeek V4 Flash Thinking | 1件(s3:その他:0.3) | (出力無効) |
| Claude Haiku 4.5 | 1件(s8:その他:0.72) | 4件(s3:その他:0.65, s8:その他:0.55, s12:その他:0.45, s29:その他:0.6) |
| Claude Sonnet 5 | 1件(s3:その他:0.2) | 1件(s22:主体対象入替:0.2) |

## 5. 実行条件の記録

- 再assert済(実行前、build()/system_for()のassertで強制): 記事sha cab7f5f3...、台帳sha 6e271bb2...、Prompt sha A3 9d995042.../A4 c87b95e5...、user message sha 88bcf14b...(前回raw requestと完全一致、dryで確認)。
- 上限変更(Fable判断): run上限JPY8->12、台帳累計上限JPY40->60(理由: ユーザー見積高位JPY47.9を上回る値にするため)。累計は最大JPY30.90でSTOPに至らず。
- retry: format再試行3件(DeepSeek V4 Flash A3[再試行後も無効]、DeepSeek V4 Flash A4[再試行後valid]、DeepSeek V4 Flash Thinking A4[再試行後も無効=2回ともlength])。transient再試行0件。他13 callは再試行なし。結果を見た再実行なし。
- Thinking実測(既定のまま、事前未確認だった点を事後記録):
  - Claude Sonnet 5: thinking/effortを送らない場合でも**thinkingブロックが1つ生成され**(A3 thinking_tokens 2119 / A4 1579、output_tokens 2414 / 1873)、省略時既定=thinking有りと実測。思考テキスト自体は空(非公開/要約なし)。
  - Claude Haiku 4.5: thinkingブロック0(省略時=OFFと実測、output 333/779)。
  - Gemini 3.5 Flash-Lite: thoughtsTokenCount 0/0(既定minimalでも実質0、output 106/89)。Gemini 3.8 Flash: thoughts 2645/1427(既定medium)。
  - DeepSeek V4 Flash(thinking disabled明示): reasoning_tokens非報告、output 915+498(A3、2回)/721+786(A4、2回)。DeepSeek V4 Flash Thinking(enabled明示、effort既定): reasoning 7757(A3、output 7862) / 7916, 8000(A4、2回ともlengthで打切り、content空または不完全)。**max_output_tokens 8000はThinking条件では不足(前回と同一条件を維持したため増やしていない)**。
  - Luna(effort=medium): reasoning 970/1494。Sol: reasoning 197/350。
- 実際に返ったmodel_id: Luna `gpt-6-luna`、Sol `gpt-6.1-sol`、Gemini `gemini-3.5-flash-lite`/`gemini-3.8-flash`、DeepSeek `deepseek-flash`(2条件同一)、Claude `claude-haiku-4-5-20251001`/`claude-sonnet-5`(runs/*/A*.jsonのmodel_ids_returned、raw_httpに保存)。

## 6. Sol前回比(非決定性の観察、主要指標ではない)

前回(META-ROLLBACK-CHECK-01、gpt-6.1-sol、同一Prompt/入力): A3/A4とも s23未Flag=NOT_DETECTED(実費JPY5.405)。今回: A3/A4とも s23未Flag=NOT_DETECTED(実費JPY5.781)で**一致**。他Flagは前回A3 4件(s3,s14,s15,s19)/A4 3件(s3,s14,s15)に対し今回A3 5件(s3,s14x2,s15,s19)/A4 5件(s3,s10,s14x2,s15)と件数・内容に差(s14の2type分割、A4でs10追加等)があり、完全には再現していない(非決定性の観察)。

## 7. 使用モデル名/最新か(PM_GOVERNANCE 25節)

全8条件はユーザー指定(精度比較の対象)であることを理由として採用。各Providerには上位/別世代のモデルが存在するが、今回対象外(ユーザー指定)。例: OpenAIの上位Astra(`gpt-6-astra`)、Anthropicの`claude-sonnet-5-5`/`claude-haiku-5-5`、`gpt-6-sol`、Geminiの`gemini-3.6/3.7-flash`、`gemini-3.1-flash-lite`(同名別世代の候補は不採用、置換なし)。本番ラインのモデル選定は別判断。

## 8. 費用

| model | 実費JPY(2call) | 見積 低 | 中央 | 高位 |
|---|---|---|---|---|
| Luna | 0.42 | 0.20 | 0.27 | 0.54 |
| Sol | 5.78 | 4.02 | 5.40 | 10.79 |
| Gemini 3.5 Flash-Lite | 0.54 | 0.71 | 1.02 | 3.87 |
| Gemini 3.8 Flash | 3.86 | 1.51 | 2.03 | 6.46 |
| DeepSeek V4 Flash | 1.04 | 0.57 | 0.75 | 1.43 |
| DeepSeek V4 Flash Thinking | 5.05 | 0.57 | 0.75 | 2.20 |
| Claude Haiku 4.5 | 2.86 | 2.01 | 2.70 | 5.40 |
| Claude Sonnet 5 | 11.34 | 4.02 | 5.40 | 17.24 |
| **合計** | **30.90** | 13.60 | 18.32 | 47.92 |

実費は中央見積(18.32)より+12.58、高位(47.92)より17.02低い。見積と実費の主な差: Sonnet 5(中央5.40->実11.34、thinking既定ON)、DeepSeek Thinking(0.75->5.05、reasoning 8000tok)、Gemini 3.8 Flash(2.03->3.86)、Sol(5.40->5.78)。ledger `cost_ledger_xm_01.jsonl` 19行(16 call + format再試行3)、合計JPY30.90(run集計と一致)。

## 9. やらないこと11項目(Phase 1の8節に対応、すべて実施していない)

1.課金API呼び出しはPhase 2の承認範囲(16 call)のみ 2.Production変更なし 3.CURRENT_SPEC変更なし 4.Prompt変更・Provider別最適化なし 5.前タスク結果の再解釈・再実行なし(Solは同一条件の新規1回のみ) 6.Human評価・Blind packet化なし 7.A5/A6・強制TopN・Rewrite・再生成・STOP処理の追加なし 8.Astra等8条件以外のモデル追加なし 9.pip installなし(REST/既存SDK) 10.SSOTはTrial結果の記録のみ(仕様変更なし) 11.配線・採用判断なし。Status4件不変更。

## 10. 成果物

`er052_output/writer_dev_risk_flagger_01/meta_rollback_crossmodel_01/`: RESULT_01.md、aggregate_xm_01.json、aggregate_xm_01.py、cost_ledger_xm_01.jsonl、runs/<model_key>/A3.json,A4.json(raw response含む)・d2_*.jsonl、xm_driver.py、PREREGISTRATION_01.md、xm_prices_01.json、estimate_01.json、dry_run/。前タスクdir(meta_rollback_check_01/, post_en_trial_01/)には書き込んでいない。
