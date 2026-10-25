# GATE_CALIBRATION_01: M-1(Tension判定promptの欠落定義の補完)の較正結果

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02A / 2026-10-25(JST)。有料(gpt-6-luna high、判定のみ。生成・書換えなし)。実費は本書末尾。
実行: `er121_family_y_calibration_01.py gate|repeat|leadrepeat`(証跡用runner。Production経路から参照されない)。生データ: `er110_output/family_y_production_launch_01/calibration_01/`(`calibration_table.json`・`repeat_table.json`・`leadintro_repeat_table.json`・各判定JSON・`raw_usage_log.jsonl`・`stop_check_*.json`)。

## 0. 結論(先に)

1. **M-1の欠陥はコードで確認した**(`er110_family_y_persona_text_trial_01.py:376-381,405-414`: Tension判定promptは『上記と同じ意味』と書きながら参照先の`_VOICE_ITEMS`を含まない)。Production版`er121_family_y_text_core_01.py`は、その3項目(`leak_evidence_subject`/`leak_discovery_syntax`/`leak_evidence_memorable`)の定義を`_VOICE_ITEMS`から**一字も変えず**に展開した。DEVは無変更。DEV差分が『展開のみ』であることはtestで固定済み(`test_tension_prompt_differs_from_dev_only_by_expansion`)。
2. **過去FAIL5件のうち3件は定義補完で消えた**(案A初回・R1宅配gen_1・R2 SNS medium_1: 新prompt各0/3)。ただし**R2宅配H2の`leak_discovery_syntax`(『見えてくる』)は新promptでも3/3 FAIL**=M-1では解消せず、G-2(Gate文言の扱い)のユーザー判断候補は残る。R2宅配medium_1は1/3。
3. **重大(STOP理由): 案B(ユーザー承認の固定本文)が新promptで2/7回 FAIL(`leak_evidence_memorable`)**。旧prompt(DEV原文)では0/7(単発の旧記録1回+再判定6回)。**Fable指示『案BがFAILならSTOPしてユーザー判断』に該当するため、案B関連の追加作業・追加判定はここで止めた**(下記§3の判断材料のみ報告)。
4. **同根の波及: Lead+人物紹介(ナレーター文)を新promptの補助適用で判定すると、適用対象項目`leak_evidence_memorable`が3/4回 FAIL**(旧prompt 0/4で適用対象項目のFAILなし)。Lead/紹介のGateもProduction移植時に影響を受ける。
5. 判定器(gpt-6-luna high)の**回ごとのばらつきが大きい**ため、単発の新旧比較は不確か(後述)。結論は反復の頻度で読む。

## 1. 方法

- 修正後Production版Tension判定prompt(`er121.build_leak_prompt('tension')`)で、過去Closing 11件(R1 4+R2 6+案A初回)+案B+Lead/紹介(最終版1件)を再判定(各1回)。
- 旧判定=各件の既存記録(`gate_leak_check.json`/`closing_*/gate/leak_check_1.json`)。
- 食い違い件は、同一本文を**旧prompt(DEV原文。Production版とは『上記と同じ意味』行の展開だけが違う)**で再判定(対照)し、判定器のばらつきとprompt変更の効果を切り分けた。
- さらにばらつき測定: 全Closing本文に新prompt追加2回、案Bは新prompt6回+旧prompt6回、Lead/紹介は新3回+旧3回。
- 使用モデル: 判定=`gpt-6-luna`(effort high。M7校正済み判定器。Charter 25節の最新世代下位系・判定専用。生成は行っていない)。routing keyは`FAMILY_Y_LEAK_JUDGE`(er006未登録のため、証跡runに限り本processの中でだけPROCESS_MODEL_MAPへ期待値を一時登録。`entry_point_*.json`に記録)。

## 2. 旧判定との差分表(Closing 11件+案B)

FAIL項目の`leak_`接頭辞は省略。『新prompt』列は同一本文の独立判定を並べた(1回目=較正run、2〜3回目=ばらつき測定。案Bは7回)。

| 本文 | 旧判定(単発・旧prompt) | 新prompt(Production版)の各回 | 新promptでFAIL | 対照: 旧promptでの再判定 |
|---|---|---|---|---|
| R1_redelivery_fee_gen1 | evidence_subject | - ／ - ／ - | **0/3** | evidence_subject,discovery_syntax,evidence_memorable |
| R1_redelivery_fee_gen2 | - | tension_reverts_to_research ／ - ／ tension_reverts_to_research | **2/3** | - |
| R1_sns_age_limit_gen1 | - | - ／ - ／ - | **0/3** | (一致のため未実施) |
| R1_sns_age_limit_gen2 | - | - ／ - ／ - | **0/3** | (一致のため未実施) |
| R2_redelivery_fee_high_1 | - | - ／ - ／ - | **0/3** | (一致のため未実施) |
| R2_redelivery_fee_high_2 | discovery_syntax,tension_reverts_to_research | discovery_syntax ／ discovery_syntax,tension_reverts_to_research ／ discovery_syntax | **3/3** | discovery_syntax |
| R2_redelivery_fee_medium_1 | discovery_syntax,evidence_subject | discovery_syntax ／ - ／ - | **1/3** | tension_reverts_to_research |
| R2_sns_age_limit_high_1 | - | - ／ - ／ - | **0/3** | (一致のため未実施) |
| R2_sns_age_limit_high_2 | - | - ／ - ／ - | **0/3** | (一致のため未実施) |
| R2_sns_age_limit_medium_1 | tension_reverts_to_research | - ／ - ／ - | **0/3** | - |
| A_v1_initial | tension_reverts_to_research | - ／ - ／ - | **0/3** | - |
| B_fixed | - | evidence_memorable ／ - ／ - ／ - ／ - ／ - ／ evidence_memorable | **2/7** | -; 旧prompt追加6回: FAIL 0/6 |

読み方:
- **旧判定が単発のため**、対照(同じ旧promptでの再判定)が旧と食い違う例が多い(R1 gen_1: 旧=1項目FAIL→対照=3項目FAIL、R2 medium_1: 旧=2項目→対照=別項目)。**判定器自体のばらつきが大きい**。
- R1宅配gen_1(『〜という声があった』=出所曖昧): 旧prompt=FAIL(定義なしで『外側の要約が主語』と広く解釈)→新prompt=0/3 PASS。定義(『主語が調査・研究・データ・割合・報告』)どおりに狭く判定されたため。出所曖昧はPrompt 02のP1(出所の曖昧な言い方の禁止)がPrompt側で防ぐ位置づけで、Gate側が捕らえなくなった形。
- R2宅配H2(『料金の話から見えてくる』): 新prompt 3/3 FAIL(`leak_discovery_syntax`)。**定義補完では解消しない**=Prompt 02の『見えてくることとして示す』とGate定義『発見・傾向を報じる記事の文構造』の衝突が本物であることの証拠(PROMPT_GATE_ALIGNMENT_01 不整合②)。
- R1宅配gen_2は旧PASS→新2/3 FAIL(`leak_tension_reverts_to_research`)。この項目は定義が元から1行完結(今回展開していない)なので、新prompt固有の悪化ではなく判定器のばらつきと読むのが妥当(対照=旧prompt再判定はPASS。n小のため断定はしない)。

## 3. 案B(ユーザー承認の固定本文)

- 新prompt: **2/7回 FAIL(`leak_evidence_memorable`)**。旧prompt(DEV原文): 0/7(記録1+再判定6)。Fisherの正確確率検定(両側)でp≈0.46(n小で有意とは言えない)が、**固定注入はFAILすると書換え禁止・同一本文の判定再試行禁止でSTOP**(DESIGN_01 §5 / I-4)の仕様なので、1回の判定でSTOPする確率は点推定で約29%(95%区間は広い: 約4〜71%)。
- 判定理由(逐語、要旨): 『匿名の不在票の一場面以外は、個人の経験や感情より料金・配達の仕組みについての一般的な説明が中心です』。
- 原因の見立て(仮説・未確認): `leak_evidence_memorable`の定義は『調査や事実よりも、**その人物の経験・感情**の方が記憶に残る書き方になっている場合PASS』(Voice用定義)。M-1でこの定義をTensionにも明示したため、判定器が『最終パート(語り手の声)に人物の経験・感情がどれだけあるか』を測るようになった。旧B(英語版)のTension欄も『上記(One Voice)と同じ意味』と書いており、**旧B原文でもTensionにこのVoice用定義が適用されていた**(`er012…:342-374`)=今回の展開は旧B原文に忠実。案Bは問い二つ・仕組みの説明が中心という文体特性のため引っ掛かりやすい。
- **Fable指示に従い、案B関連の追加判定・実装後の案B E2Eはここで止めた。** registry実装(`FIXED_CLOSING_REGISTRY`)は完成しているが、**Production runtimeで案Bを注入すると約3割の確率で`FIXED_CLOSING_GATE_FAIL`によりSTOP**する見込みである。
- 判断材料(`判断候補`、27-3のD=真に新しいユーザー判断):
  - 案I: **このまま進める**(M-1はユーザー§6『判定器への入力ミスの自律修正』に該当、Gate基準の文言は不変)。案BがSTOPした場合は、そのrunで本文をそのまま使えない旨を報告し、ユーザーが『案BのGate FAILの扱い』を判断する。立上げ自体は他記事(一般化経路)で進められる。
  - 案II: `leak_evidence_memorable`を**Tension(語り手の声)では適用しない/文言をナレーターに合わせる**=Gate基準の変更。承認済み品質条件の変更に当たるためユーザー承認必須。旧B原文との整合(旧Bも同定義を適用)と、QCD(FAIL回避で書換え・STOPが減る)を添えて提示する。
  - 案III: 案Bの判定を1回ではなく「承認Gateの標準どおり判定≤3回(書換えなし)」にする=『同一本文の判定再試行で通す』ことになり、DESIGN_01 I-4で自ら禁じた方式。ユーザー承認があれば可。
  - 02Aの推奨: **案I(まず進め、実際にSTOPが出たら案IIを提示)**。理由=現時点は2テーマのn小で、定義補完の効果と判定器のばらつきを分離できていない。実運用のgate_history(I-2)が溜まってから、G-1/G-2と一緒に1件のユーザー判断にまとめるのが合理的(PROMPT_GATE_ALIGNMENT_01 §6-3と同じ)。ただし『案BがFAILならSTOPしてユーザー判断』というFable指示が先行するため、**最終判断はFable**。

## 4. Lead+人物紹介(Tension項目の補助適用)

- 適用対象外の2項目(`leak_tension_reverts_to_research`/`leak_binary_camp_split`)を除いた**適用対象項目のFAIL**: 新prompt 3/4回が`leak_evidence_memorable`(『料金の仕組みの説明と一般的な問いが中心で、三人の具体的な経験や感情は示されていません』)。旧prompt 0/4(旧記録1+再判定3)。
- 同根(ナレーター文に人物の経験・感情を要求する定義が効く)。Lead/紹介のGateは承認済みGateの定義そのものではなく**補助適用**(DEV `LEADINTRO_NA_FIELDS`)なので、Productionでの扱い(`leak_evidence_memorable`も適用対象外にするか、判定対象から外すか)はFable判断。承認済みGate定義は変更しない形(補助適用の対象範囲の設定)で処理できる可能性があるが、**独断では変えていない**。
- 02Aの推奨: 案Bの判断と同時に決める(同根のため)。

## 5. 実費

`calibration_01`(判定のみ)= **5.969円**(gate 2.294 + repeat 2.913 + leadrepeat 0.762)。M-2書換えevidence分は`REWRITE_EVIDENCE_01.md`。本委任の有料run合計は`RESULT_PACKET_YPL2A.md`に記載(`er121_family_y_calibration_01.spent_jpy`による集計。単価=`er005_output/cost_baseline_01/pricing_snapshot.json`)。見積(5〜15円)の範囲内。
