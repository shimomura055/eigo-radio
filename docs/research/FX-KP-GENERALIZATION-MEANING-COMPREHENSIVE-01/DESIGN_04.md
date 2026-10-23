# DESIGN_04: DESIGN_03のOpus条件Aレビュー反映版(委任_07、2026-10-23、設計+実施結果の対応)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_07 / 根拠=`OPUS_REVIEW_03.md`(逐語保存)/ 前版=`DESIGN_03.md`
状態: Trial実施済み(結果=`TRIAL_RESULT_02.md`)。Production/Prompt/flag/閾値/golden変更0(er112系とdocsのみ)。未承認の追加改善案であり、採否はユーザー判断(VALIDATED候補止まり)。

## 1. OF-KPGM-D3-01〜12の反映状況(実施した設計と、予算制約による縮小の別)

| OF | 反映した設計 | 実施状況 |
|---|---|---|
| 01 Adv arm要因分解 | E0 / E1(gloss入力行+それを参照する規則行を外す) / E1c(E1+core_sense、usage_typeなし) / E4(E1+usage_type→core_sense→explanation)。E1型を第一候補、E4は修正後Judgeで明確に上回った場合のみ | 実施(`er112_kp_gm_trial_02.py` `expl_message`/`expl_schema`)。E4は難例20+通常30(n=50)、E1/E1cはn=75、E0は難例20(G0入力)+通常55(production gloss入力) |
| 02 single再定義 | 「異なる2つの語義・用法を並べた場合だけ0。同じ1つの語義を同義語で補う場合は1」(Judge kind=E3、`er112_kp_gm_judge_01.py`。旧E2はTrial_01再現用に凍結) | 実施。**probe-03既存行の再判定キャリブレーションはAPI予算のため未実施**(旧E2判定との差の再測定=未確認)。代わりに本Trial行で2系統Judgeを比較(kappa下記) |
| 03 E0交差 | E0を「G0 gloss入力」「G2 gloss入力」「G3 gloss入力」「production gloss入力(通常KP)」で測定。E1/E1c/E4はgloss非依存で1回 | 実施(E0@G0/E0@G2/E0@G3/E0@prod) |
| 04 signatureへ仕様ID | `WIRING_DESIGN_02.md`(設計のみ。Production編集なし) | 設計のみ |
| 05 撤去漏れ | `WIRING_DESIGN_02.md` §3の撤去一覧 | 設計のみ |
| 06 Sol arm | draw a line単体は各Sol armで3rep(G0-sol/G2-sol)。難例バッチはG0-sol 1本(11 KP)。**Sol 1 call実測=1.13円(2048in/299out)**を先に取得 | 実施。Sol合計18.24円(上限25円内) |
| 07 G3 arm | luna G3: 新規生成(current=null)項目に「英和辞典の定訳→対応する日本語慣用句→無ければ中心義を平易に」の優先順で2〜3案(candidates)を同一callで出し1案を選択。draw a lineのfew-shot無し | 実施(n=26 KP、draw a lineは3rep) |
| 08 因果主張の強さ | 「glossは含意を持ち込みうる」まで。『モデルの判断力が律速』仮説は本Trialで反証寄り(下記) | TRIAL_RESULT_02に反映 |
| 09 Std/Adv整合 | 「同じ用法(字義/比喩)で矛盾しない」(Judge kind=P再定義)。矛盾件数を測定、条件付き再整合は入れない | 難例20×2組で測定(Sonnet1系統) |
| 10 Judge | gold_reference(難例20、draft)をJudge行へ付与。2系統Judge、arm伏せ、Fable目視サンプル | gold=`GOLD_LABELS_DRAFT_01.md`(**Fable確定待ち**)。**Judge再判定一致(約30行)・Fable確定後の差分再判定は未実施**。kappaは重複行で算出 |
| 11 統計 | 自己一致率(E0@G0/E1のhard20×3rep)、KP単位flip(改善/悪化/不変)、Wilson CI、方向判断 | 実施(`er112_kp_gm_analysis_02.py`/`er112_kp_gm_summary_02.py`)。許容差の事前宣言は本設計で次の通り: 非劣化の基準=E0の3rep自己一致率(約65%)と同程度以内を「差なし」と読む |
| 12 検証項目6 | Production関数`generate_kp_explanations`をDEV注入(`call_fn`)でX12+Z8バッチ×3arm実行、retry/QA統計、Production hash記録 | 実施(KP説明段のtext E2E)。**Writer等を含む記事全体のtext E2E(X1本+Z1本)は予算のため未実施** |

## 2. 評価指標の定義(事前宣言)

- 総合PASS(Adv) = sense_ok かつ core かつ single(PASS3)。over_generalは**参考値**(2系統Judgeのkappaが低く信頼できないため総合に入れない。Trial実施中に判明し、事後に除外した=事後変更として明記)。
- Std = Judge kind G(sense_ok & !literal & !deictic)。
- 事前宣言の許容差: 差が±10pt以内でKP単位flipの改善/悪化比が2:1未満のものは『差なし』とする。

## 3. 失敗終了時の最終成果物
Trial停止時も`er112_output/kp_gm_trial_02/`(results.jsonl/paid_calls.jsonl/judge/)と本docsが残る。Production成果物は無変更。目的(要求品質到達)の達成可否はTRIAL_RESULT_02の自己判定を参照(手段の成否と分離)。
