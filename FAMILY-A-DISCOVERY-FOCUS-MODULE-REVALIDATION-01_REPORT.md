# FAMILY-A-DISCOVERY-FOCUS-MODULE-REVALIDATION-01

管理ID: FAMILY-A-DISCOVERY-FOCUS-MODULE-REVALIDATION-01
性質: Trial(Article-only、Production変更なし)。到達Status: **VALIDATED**
(Gate 1判定材料の提示まで。Production採用判断[APPROVED_FOR_PRODUCTION/
PRODUCTION_WIRED]は本タスクの範囲外であり、Fable/人間ユーザーの判断に委ねる)。

## 1. テーマ・Ledger選定

- テーマ: **"Why do we sometimes wake up right before the alarm rings?"**
  (目覚まし時計が鳴る直前に自然に目が覚めることがあるのはなぜか)
- Ledger再利用元: `er011_output/discovery_generalization_wake_before_alarm_trial_12/research/verified_fact_ledger.txt`
  および同ディレクトリの`research/writer_topic.json`(topic_ja)。**新規Research/
  Ledger作成はしていない**(read-only再利用)。
- 選定理由:
  1. Towels Trial-11・Wake Trial-12はいずれも`ledger_deviation.json`の
     `overall_status = "LEDGER_COMPLIANT"`で検証済み(両テーマとも条件を満たす)。
  2. Wake Trial-12はTowels Trial-11より新しい(同日2026-09-13close)。
  3. Wake Trial-12の記事生成コスト実測(writer_a2=13.71円、writer_b1=20.59円、
     1 arm分)がTowels Trial-11(writer_a2=28.30円、writer_b1=33.94円)より低く、
     4 arm実行時の予算余裕が大きかった。

## 2. 設計

条件差は`editorial_type_module_block`(Discovery Focus Module Part A、
`er011_discovery_stage3_rule_adjustment_trial_09.CURRENT_FOCUS_BLOCK`一字一句
不変)の有無のみ。他パラメータ・モデル・Prompt・QAは現行Production経路
(`er003_v1_n3_01_articles_generate.run_one_pattern`)を無変更で直接呼ぶ。
切替のためのTrial専用ドライバ`er011_discovery_focus_module_revalidation_01_run.py`
を新規作成したが、Productionファイル(`er003_v1_n3_01_articles_generate.py`
等)は一切変更していない。Gate 4相当の静的確認(`gate4_check.json`)で
Production関数の再定義・monkeypatchがないことを機械確認済み(PASS)。

A2/B1(B1B_DIRECT)× baseline/focus 各1本、計4記事を生成した(N増しなし)。

## 3. 実行結果サマリ

| Arm | status | fact_verdict | ledger_status | word_count | Local Rewrite | retry |
|---|---|---|---|---|---|---|
| A2 baseline | OK | PASS | LEDGER_COMPLIANT | 471 | 0 cycle | 0 |
| A2 focus | OK | PASS | LEDGER_COMPLIANT | 363 | 1 cycle/1 item(resolved) | 0 |
| B1 baseline | OK | PASS | LEDGER_COMPLIANT | 507 | 0 cycle | 0 |
| B1 focus | OK | PASS | LEDGER_COMPLIANT | 442 | 0 cycle | 0 |

REVIEW_REQUIRED相当(fact_verdict=REVIEW_REQUIRED、または最終status=
NG_REVIEW_REQUIRED): **0/4**。全arm status=OK、Fact Checker verdict=PASS、
Ledger最終status=LEDGER_COMPLIANT。旧Trial-07の「baseline約17%/Focusあり
約67%」水準は再現されず、Household Ledger v5相当の現行Ledger品質下では
観察されなかった(Trial-09/10のcurrent_focus 0/6と整合)。

## 4. 比較表(必須形式)

| 指標 | Baseline | Focus | 差 |
|---|---|---|---|
| Discoveryらしさ(0-2、主観採点) | 1 | 2 | +1 |
| Main Story(現象提示に留めるか、0-2) | 1 | 2 | +1 |
| Point One価値(0-2) | 1 | 2 | +1 |
| Point Two価値(0-2) | 2 | 2 | 0 |
| Point多様性(記事内、0-2) | 2 | 2 | 0 |
| Fact Safety | PASS/COMPLIANT(4本とも) | PASS/COMPLIANT(4本とも) | 差なし |
| REVIEW_REQUIRED | 0/2 | 0/2 | 0 |
| Point Overlap記事全体retry | A2=0,B1=0 | A2=0,B1=0 | 0 |
| Local Rewrite | A2=0,B1=0 | A2=1cycle(resolved),B1=0 | Focus A2のみ発火 |
| 差分QA(Local Rewrite後) | 該当なし | Focus A2の1件でPASS | Focus A2で1回実施 |
| コスト(4本合計) | — | — | 113.91円/上限320円 |

0〜2点の定性スコアは本タスク(Sonnet実行層)による**主観評価**であり、
統計的検定ではない。根拠文の引用・詳細は
`er011_output/discovery_focus_module_revalidation_01/comparison.md`参照。

## 5. 論点A(書き分け)の要点

- **Main Story抑制**: Baseline(A2/B1)はMain Story内でACTH上昇・前頭前野
  活動・心拍上昇といった生理学的知見を具体的に列挙しており、Focus Moduleが
  禁止する「Main Storyだけで『なぜ』を説明しきる」パターンに近かった。
  Focus(A2)はMain Storyを現象提示と問いの提示に留め、具体値をPoint One
  へ明示的に繰り延べていた。Focus(B1)はA2ほど徹底されていなかった
  (ACTHの具体値がMain Storyにも残存)。
- **Point多様性(記事内)**: Baseline・Focusともに、Point One・Twoは記事内で
  明確に異なる角度を持っていた(スコア2、差なし)。
- **観察(N=1のため確定的ではない)**: Baseline 2本はいずれもPoint Twoに
  「睡眠段階(sleep architecture)」角度を採用したが、Focus 2本はどちらも
  この角度を採用せず、代わりに「概日ペースメーカーの限定範囲」または
  「生理学的段階的countdown」角度に収束した。Focus条件下でA2・B1間の
  「角度の引き出し」がやや似通う可能性があるが、N=1×2では偶然か
  Focus固有の効果かを判別できない。
- **「へえ」・throughline**: Focus armはIn One Lineで比喩的表現
  ("a quiet countdown, not a perfect time reading" 等)を用い、Main Story
  冒頭の「問い」からPoint内容へ戻る一貫したthroughlineを保っていた。
  Baseline armのIn One Lineは要約寄りで、持ち帰り感がFocus armよりやや弱い。

## 6. 論点B(副作用)の要点

- Fact Checker: 4本ともverdict=PASS、unsupported_specific_claims=0件。
- Ledger Deviation: 4本とも最終status=LEDGER_COMPLIANT。A2 focusのみ
  MAJOR逸脱1件を検出しLocal Rewrite cycle 1で解消(human_review_required
  =false)。既存の安全装置(Local Rewrite+差分QA)が想定通り機能した
  事例であり、新しいfailure modeではない。
- Local Rewrite後の差分QA(OPEN-141、2026-09-13配線、既定ON):
  A2 focusの1件でtarget-sentence-matching使用、Fact Checker A'再実行
  (verdict=PASS)、Ledger再確認(COMPLIANT)、Point Overlap再計算
  (overlap_ratio=0.229、flagged該当なし)、blocks_acceptance=falseで受理。
- Point Overlap QA: 4本とも記事全体retry 0回。cross_point_overlap比率は
  Focus armの方がやや高め(A2 focus 0.15/0.171 vs A2 baseline 0.03/0.029)
  だが閾値未満(語彙的近さの微増であり、内容重複の指摘ではない)。
- Directional Fact Precheck: 4本すべてDIRECTION_REVIEW_REQUIRED
  (baseline/focus差ではなくこのPrecheck層自体の一律挙動、non-blocking
  advisoryでstatus=OKには影響しない)。
- word count: Focus armの方がやや短め(A2: 471→363語、B1: 507→442語)。
  avg_sentence_lengthは11.9〜14.5語で大差なし。

## 7. 論点C(Point Role PlanningがFocusを知らない構造)の観察

Gate 4静的確認で機械確認済み:
`er011_point_role_value_planning_01.run_point_role_planning(client, topic,
verified_ledger_text, model, reasoning_effort)`のシグネチャに
`editorial_type_module_block`引数は存在しない(4 armとも同一のtopic/
ledgerがrole planningへ渡っており、Focus Moduleの有無はrole planning
自体には伝わっていない)。**接続実装は行っていない(範囲外)。**

- 4 armの役割計画は互いに異なる角度を割り当てていたが、これは主に
  モデルの非決定性によるものであり(role planningにFocusは渡っていない
  ため)、Focus Moduleの有無による系統的な差ではない。
- WriterとRole Planの競合(役割指定を無視・矛盾する記述)の実例は
  4 armとも見つからなかった。Focus armのWriterはrole planが指定した
  角度・比喩(例: B1 focus Point Oneの"synchronizer, not a perfect
  stopwatch")をそのまま採用していた。
- 一方、Focus ModuleはMain Storyの記述方針(現象提示に留める)を直接
  指示するが、role planningはMain Story側の方針を一切考慮しない
  (topic文字列とledgerのみを見てPoint役割を決める)。B1 focusで
  ACTHの具体値がMain Storyに残存したのは、この構造(role planが
  Main Story側の抑制を意識していない)が一因である可能性がある。

## 8. Gate 1判定材料

- **差は明瞭か**: Main Story抑制・In One Lineのthroughline/「へえ」の点で
  Focus armが一貫して優位(A2で最も明瞭、B1でもやや弱いが同方向)。
  Point Two価値・記事内Point多様性は両arm同水準で差が明瞭でない。
- **品質問題の有無**: 4本ともFact Checker PASS・Ledger最終COMPLIANT・
  REVIEW_REQUIRED 0件。Focus A2で発生したLedger MAJOR逸脱1件は既存
  Local Rewrite+差分QA機構で自動解消(新しいfailure modeではない)。
- **N増しの要否(材料、追加実行はしていない)**:
  1. Main Story抑制効果はA2で明瞭・B1でやや弱く、レベル間差の再現性
     確認にはN増しが有用と考えられる。
  2. cross-article角度収束(睡眠段階角度の消失)がFocus固有の効果か
     偶然かはN=1×2では判別不可。追加テーマまたは追加runでの確認が
     望ましい。
  3. Point One価値・Discoveryらしさの差自体はA2/B1とも同方向に出ており、
     大きな追加Nなしでも方向性の判断材料にはなり得る。

## 9. 費用実測

API呼び出し別実測(pricing_snapshot換算、全てOpenAI gpt-5.6-luna):

| 区分 | 実測(円) | 呼び出し数 |
|---|---|---|
| A2 baseline | 31.16 | 6 |
| A2 focus | 30.54 | 11(Local Rewrite+差分QA分を含む) |
| B1 baseline | 28.39 | 6 |
| B1 focus | 23.81 | 6 |
| **合計** | **113.91** | **29** |

上限¥320に対し実測113.91円(36%)。事前見込み(既存Trial実測からの
概算)通り、上限超過は発生しなかった。STOP該当なし。

## 10. 限界

- N=1×2(baseline/focus × A2/B1)のみ。定性スコアは主観評価であり、
  統計的有意性は主張しない。
- Directional Fact Precheckの一律REVIEW_REQUIRED挙動、cross-article
  角度収束の観察はいずれも本Trial単独では原因を特定できていない
  (Focus Module固有の効果か、topic/ledgerや役割計画の非決定性による
  偶然かを切り分けるには追加runが必要)。
- B1レベルでのMain Story抑制効果がA2ほど明瞭でなかった理由(role
  planningがMain Story抑制を考慮しない構造)は観察に基づく仮説であり、
  検証(接続実装を伴う)は本タスクの範囲外。

## 11. SSOT追記文案(編集はしていない、Fable/ユーザー判断待ち)

> Discovery Focus Module Part Aは、現行Production基盤・現行Ledger/QA条件
> (Household Ledger v5相当・Fact Checker/Ledger Deviation/Local Rewrite/
> 差分QA既定ON)下で、wake-before-alarmテーマのN=1×2(A2/B1)再検証において
> REVIEW_REQUIRED 0/4・Fact Safety劣化なしを確認し、Main Story抑制・
> In One Lineのthroughline明瞭化という書き分け上の利点を観察した
> (FAMILY-A-DISCOVERY-FOCUS-MODULE-REVALIDATION-01、2026-09-13、
> VALIDATED相当、Production採用は別途判断)。Point Role PlanningはFocus
> Moduleの有無を認識しない構造(接続なし)であり、Main Story抑制の
> 一貫性はWriter側の指示遵守にのみ依存する観察が得られた。

## 12. 成果物パス

- `er011_discovery_focus_module_revalidation_01_run.py`(Trial実行スクリプト)
- `er011_output/discovery_focus_module_revalidation_01/`(4記事・QAログ・
  role plan・comparison.md・index.html)
- `docs/pm/RESULT_PACKET_DFM.md`(短縮報告)
