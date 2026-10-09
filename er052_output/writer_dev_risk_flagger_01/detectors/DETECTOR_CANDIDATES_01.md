# DETECTOR_CANDIDATES_01 (WRITER-DEV-RISK-FLAGGER-DESIGN-01 委任_01B, 2026-10-09)

Risk Flagger(開発時限定)の検出器候補。いずれも「合否判定しない/Productionを止めない/Rewriteしない/自動修正しない。人間が確認した方がよい箇所にFlagを立てる」。重大/非重大のみ。
Production採用の提案ではない(DEV/Trial専用。Production採用は人間ユーザーのみ承認)。本書の状態は設計であり、検出精度は未評価(評価は casebank 完成後の別委任)。

## 0. 共通仕様
- 入力unit: 1ケース(casebank: 1文+Fact1件+前後文) または 1記事(全文+台帳全Fact)。実装: `run_flagger_01.py`(`load_units`)。評価時はラベル列を落とした `*_blind.json` のみ読む(`make_blind_01.py`)。
- Flag構造: `unit_id / sentence_id / sentence(引用) / type / fact_ids(根拠Fact ID) / confidence(0-1) / severity(重大|非重大) / question(人間向け確認質問1文) / detector`。D0は追加で `basis`(発火根拠の語)。
- type: rollback反転 / 主体対象入替 / 否定反転 / 数量時系列 / 不在断定 / その他。
- 最新モデル原則(`docs/pm/PM_GOVERNANCE.md` 25節)に従い、**旧モデルは使わない**: 使用可能は gpt-6.1-sol(推奨系)、gpt-6-astra(最上位、最終確認のみ)、deepseek-v4-pro(DeepSeek最上位系)。gpt-5.6-sol / gpt-5.6-luna / deepseek-v4-flash(旧名) / gpt-6-luna(効率系で最上位・推奨系でない) は `flagger_lib.MODELS` に載せずテストで不在を確認。
- 疎通確認(2026-10-09、各1回): gpt-6.1-sol / gpt-6-astra / deepseek-v4-pro はいずれも当方キーで呼べた(実費合計 JPY 0.21、`cost_ledger.jsonl`)。除外モデルなし。
- 単価(登録、出典 `PRICING_SOURCES_01.md`): gpt-6.1-sol 入2.00/cache0.10/出10.00、gpt-6-astra 10.00/1.00/50.00、deepseek-v4-pro(Peak) 1.32/0.044/3.96 ($/1M)。USD_JPY=160。
- 費用見積の前提: 1記事=約25文(約35tok/文)+台帳Fact 10〜30件(約70tok/件)、出力は推論込みで 600〜4,000 tok/呼び出し。`estimate_cost_01.py` の出力(登録単価x見積トークン)。実際の出力量は疎通の最小入力では9tok(推論0)で、検出タスクでは未測定。幅は保守側。

## 1. 候補一覧(要約)
| ID | 方式 | 呼び出し/記事 | モデル | 想定費用/記事(JPY) 10Fact〜30Fact | 主に拾うタイプ |
|---|---|---|---|---|---|
| D0 | 決定論・方向語/不在cue/数量 | 0 | なし | 0 | rollback反転(方向語)、不在断定(cue)、数量時系列(数値差) |
| D1map | タイプ別専用Prompt x5、Fact対応=D0近似(上位3件) | 5 | gpt-6.1-sol | 8.2〜36.0 | 5タイプ |
| D1full | タイプ別専用Prompt x5、台帳全体を渡す | 5 | gpt-6.1-sol | 8.6〜38.0 | 5タイプ(対応付け漏れに強い) |
| D2 | 万能Flagger(重大のみ列挙) | 1 | gpt-6.1-sol | 1.7〜7.5 | 全般(軽微は出さない指示) |
| D3a | D0 ∪ D1(map or full) | 5 | gpt-6.1-sol | D1と同じ(D0は0円) | 和集合 |
| D3b | D0 ∪ D2 | 1 | gpt-6.1-sol | D2と同じ | 和集合 |
| D3c | D0 ∪ D1 ∪ D2 | 6 | gpt-6.1-sol | D1+D2 | 全和集合 |
| D4 | 最良構成(D1/D2/D3の勝者)を gpt-6-astra で再実行(最終確認のみ) | 1〜6 | gpt-6-astra | D2: 8.3〜37.7 / D1: 40.8〜190.2 | 同上 |
| (参考) D1/D2 の deepseek-v4-pro 版 | 同上 | 1〜5 | deepseek-v4-pro | D2: 0.8〜3.3 / D1: 4.1〜16.7 | 同上(別系統での補完・価格比較) |
casebank 1ケースあたり(1文+Fact1件): D2 sol 1.2〜6.7、D1 sol(5呼び出し) 6.5〜33.7、D2 astra 6.2〜33.4、D1 astra 32.4〜168.4、D2 pro 0.6〜2.7、D1 pro 3.0〜13.8。casebank 12ケースなら D1(sol)全タイプ 約78〜404、D2(sol) 約15〜80。総予算JPY1,000に対し、D1(astra)の全ケース実行は上限側で予算超過しうるためD4は最良構成のみ(要 `--max-yen`)。

## 2. 各候補の詳細
### D0 決定論・方向語(実装: `d0_directional.py`、API不要)
- 入力/出力: unit -> Flag list(上記構造)。方式: (a) 方向語グループ(rollback系 W=停止・撤回・ロールバック・無効化・on hold 等 / R=復元・再導入・再開・元に戻す・restore/put back/reinstate 等、他に増減・許可禁止)の対立。Fact側がWのみで文側がRのみ(またはその逆)ならFlag、type=rollback反転、confidence 0.7(対応付けが弱い複数Fact台帳では0.5)。語彙は `open233_directional_misread_trial_01/population_01.md` の語彙を拡張。(b) 不在断定cue(「公表されていない」「No one has」「has not been made public」等)を含む文、confidence 0.35。(c) 文中の数値(2桁以上)が対応Factの数値集合にない場合、type=数量時系列、confidence 0.3。
- 文とFactの対応付け: 固有名詞・数値・カタカナ/漢字語・英単語の重なり(小さい方の集合に対する割合)で上位3件を近似(0円)。台帳1件(casebank)は強制採用。複数件台帳は重なり0.15以上のみ。
- 想定費用: 0円。
- 長所: 無料・再現性100%・K01型の「用語の取り違え(rollback→restored)」を決定論で拾える。短所: 語彙にない言い換えは取りこぼす。不在cue・数量は高い偽陽性(cueだけでFlag)。主体対象入替・否定反転は拾えない(D0には実装なし)。
- 既知事故での見込み: K01(restored ... the way it had been before): 拾う(W=ロールバック / R=restored,the way it had been)。K03(put back): 拾う。K02/jb9k(Nor has anyone reported ...): 不在cueで拾う(低信頼)。K11/sw-p2r2-01(定義と発表内容のすり替え): 拾えない見込み(方向語なし)。K12(put on hold、忠実): Flagなし(確認済み)。K04(JA「以前の状態に戻しました」): 拾う(境界ケースの確認用Flag)。
- 設計時の参考確認(評価ではない): `eval_items_01.json` の10ケースをD0に通した結果は `results/d0_none_sanity10.jsonl`。Flag: hdr8y4(K03), y84g5r(K01), yjjmk8(K04), ur5649(K02), 7b6trp(K06)。z63yng(K11)は未検出、9ywt6e(K12)ほか3件(7suvyn, 6urnmg, sq5c2g)はFlagなし。正式な検出率は casebank で別途評価する(注意: D0語彙はK01〜K04の文面を見たうえで設計したため、この結果は設計時の動作確認であり検出率の根拠にはならない)。

### D1 専用Prompt x タイプ別(実装: `prompts_flagger.py` d1_system, `run_flagger_01.py` plan_calls)
- 方式: タイプごとに「このタイプの逸脱だけを探す」単機能プロンプト(rollback反転/主体対象入替/否定反転/数量時系列/不在断定の5本)を1文書あたり5回呼ぶ。モデル gpt-6.1-sol。台帳Fact渡し方を2方式比較: D1map=D0の近似対応(各文の上位3Factの和集合のみ)、D1full=台帳全体。出力はJSON(Flag構造)。形式違反は1回だけ再呼び出し。
- 長所: 単機能なので指示が明確で、K01型の「用語のズレ」を狙い撃ちできる(汎用評価が全モデルで見逃したK01型への対策)。タイプ別Recallが測れる。短所: 呼び出し5倍で費用が高い。D1mapは対応付け失敗で根拠Factを渡せず見逃す(D1fullとの比較で測る)。
- 想定費用: 上表。既知事故での見込み: K01/K03=rollback反転Promptが台帳の『ロールバック』と文の『復元/put back』の向きを明示比較する(拾える見込みは高いが未検証)。K02/jb9k・K06=不在断定Prompt(台帳が起きたと書く事柄を「起きていない」と断定)。K11/sw-p2r2-01=主体対象入替Prompt(定義を発表内容に差替え)。

### D2 万能Flagger(実装: `prompts_flagger.py` d2_system)
- 方式: 1プロンプトで重大候補のみ列挙(軽微・言い換え・文体は出さない指示)。gpt-6.1-sol、1記事1呼び出し。
- 長所: 最安・Flag過多になりにくい設計。短所: 3分類汎用評価がK01を全モデルで見逃した前例があり、指示が広いぶん特定タイプに弱い恐れ。既知事故の見込み: K02/K11は台帳との照合で拾える可能性、K01は不確実(未検証)。

### D3 組合せ(実装: `run_flagger_01.py --union`、API呼び出しなし)
- D3a=D0∪D1、D3b=D0∪D2、D3c=D0∪D1∪D2。既存results同士の和集合なので追加費用0。
- 重複除去規則: (unit_id, sentence_id, type) が同じFlagは1件に統合(confidenceは最大、questionは最大confidenceのもの、fact_idsは和集合、sourcesに検出元を列挙、severityは1つでも重大なら重大)。同じ文でもtypeが違えば別Flagとして残す。
- 長所: 決定論の確実性とLLMの意味理解を補完。短所: Flag数が増え人間確認コストが増える(Flag/記事を集計して許容性を判断)。

### D4 最上位モデルでの確認(gpt-6-astra)
- D1/D2/D3で最良と判定した構成だけを gpt-6-astra で再実行し、sol 結果と比較(最終確認のみ)。費用が約5倍のため `--max-yen` を必須とし、casebank全件 x D1 全タイプは予算上避ける。

## 3. harness / 集計(実装済み、ユニットテスト30件PASS)
- `run_flagger_01.py`: 入力(ケース集合 or 記事)→検出器→`results/<detector>_<model>_<set>.jsonl`。`--max-yen` 必須(LLM)、`--total-cap-yen`(既定900)で `cost_ledger.jsonl`(全検出器合算)の累計が上限に達したら呼び出し前に停止、`--dry-run`、JSON検証(sentence_id/fact_id/type/severity/confidence/question)、形式違反は再呼び出し1回、既存結果の上書き禁止、一時障害の再試行2回。
- `make_blind_01.py`: casebank_01.json からラベル列を落とした `casebank_01_blind.json` と、集計専用の `casebank_01_labels.json` を生成。runnerはラベル列を含む入力を拒否し、labelsファイルを開かない(テストで確認)。
- `aggregate_flagger_01.py`: Recall(重大)、精度(ケース/Flag単位)、Flag/unit、タイプ別Recall(labelsの `type_label`)、既知事故別(labelsの `known_incident`)、見逃し・誤Flagケース、費用。ラベル値は重大系/問題なし系/それ以外(境界)に正規化し、境界は分母から除外して別掲。
- casebank_01.json のスキーマ想定: `{"cases":[{case_id, fact(またはfacts), sentence, context_before/context_after(またはcontext), article_path, label, known_incident?, type_label?}]}`。01A側スキーマが違う場合は `case_to_unit` / `LABEL_KEYS` の調整のみで対応可能。

## 4. USER_DECISION_REQUIRED / 報告事項(実装していない)
- 評価実行(casebankへの実API実行)は未実施(本委任は設計・骨格のみ)。
- 候補の優先順位は評価後に決める。現時点の想定は D0(無料)を常設ベースにし、D1/D2/D3を同一casebankで比較。
- 新しい仕様候補: 記事全体に対するFlag/記事の許容上限、confidence閾値(`--min-conf`)の決め方は評価後の判断事項。


---
**委任_02 P0(v2)改訂注記**: D1mapは廃止しD1fullに一本化(台帳全体を渡す)。D1は各呼び出しFlag上限3件。D2rank(記事モード、上位3文を必ず列挙)を追加。D0の和集合投入はrollback方向のみ(gate_only除外)、D0の不在・数量・増減/許可は `--gate d0` のD1ゲート用。詳細は `../DESIGN_RISK_FLAGGER_01.md` §5・§13。
