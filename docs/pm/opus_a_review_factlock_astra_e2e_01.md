# Opus条件Aレビュー: FACTLOCK-ASTRA-E2E-TRIAL-01 設計書・事前登録(2026-10-09)

性質: Opus独立技術レビュー(PM_GOVERNANCE 11-3 条件A=新しい構造・処理フロー)の結果要点。**本書はFableの手元にあるレビュー全文からの転記(委任_03の委任文経由)であり、Opus原文そのものではない**(OPUS_FINDINGS_LEDGERの他行と同じ扱い)。Fableが採用判断済み(2026-10-09)。
レビュー対象: `er052_output/factlock_astra_e2e_trial_01/DESIGN_E2E_01.md`(v1)・`PREREGISTRATION_01.md`(v1)の8論点(v1 DESIGN 8節)。
反映先: 同ディレクトリの DESIGN_E2E_01.md v2・PREREGISTRATION_01.md v2。反映の対応表は DESIGN v2 8-1節。
Opusレビュー自体はユーザー承認Gateではない。Production採用は人間ユーザーのみ承認する。

## 論点1 交絡(Writer変更とM1/M3)
- Arm C(旧JA×M1/M3 ON)は不要。影の対照を**両腕**で取る。
  - M1(a): 旧腕本文に「M1入力の要約+EN検査1回」、新腕本文に「旧入力の要約+EN検査1回」(20対)。
  - M1(b): 要約のみMAJOR発火時にもう一方の規則をログ専用で1回。新腕なら旧規則=Advanced再生成1回+EN検査1回(約¥0.6/発火、`er012_e_family_entertainment_two_level_runner_01.py` L556-579)、旧腕なら`open243_m1_summary_only_retry`。
  - M3: 旧腕runで「changed_actorがあれば保護されていた除外claim」を¥0で列挙し、任意でStage 2を1回。
- DESIGN v1 3節L106-107「M1(b)の反実仮想は安く再現できない」は**誤り**(訂正)。
- 追加費用見積 計¥10〜15。

## 論点2 案B(JA再確認)の新腕
- **B1採用**。必須(¥0): 主指標に「初回(回復前)のJA_RECHECK発生率」を両腕で記録(旧腕は`JARecheckRequiredError`捕捉時点)。
- 前提作業(c)タグ残存修正(30〜50行)が必要になる。PREREGISTRATION §5-8を確定する。

## 論点3 Production等価性
- 新腕のFC MAJORは「記録して続行」を維持しつつ、R2後のFC MAJORに`shadow_stop=true`を付ける。
- 複合主指標「人手介入必要率 =(JA STOP+影STOP+EN STOP+Human Review)÷予定run数」を両腕同定義で追加。
- B1採用時はR2のFC MAJORも同じ回復経路(1回)に統一してProduction等価にする。記号Gateは記録のみで可、残存はTTS対象2本で確認。

## 論点4 M1のStandard枝
- 実装しない。Standardのattempt1 MAJORを`open243_majors_only_in_summary`で要約/本文に分類して記録(¥0)。
- 「Standard側のM1効果は未測定」と明記する(Standardは修正済みAdvanced要約を含む全文をA2化するため部分的に伝わる、`er003_v1_n3_01_standard_a2_generate.py` L522/L541)。

## 論点5 注記briefの人手依存
- 条件付き可: 注記ルール固定・sha256凍結、注記者に生成結果・腕を見せない、独立二重注記で一致率を記録、不一致はルールで機械的決定。
- `strip_tags(注記版)`=旧腕B3原文をG0で照合。er019の再利用分岐はJSON `fact_selection_evidence.json`の`selected_fact_brief_text`を読む(L336-339)ので、JSONもsha256照合対象。
- 旧4/新6の層別報告。結果は「人手注記の上限性能」と明記。Production化にはB3自動注記が必要(OPEN項目候補)。
- ユーザー決定7(2026-10-09)により、全10記事を新仕様で再注記する(旧4の過去注記は使わない)に更新された。

## 論点6 統計・判定線
- EN STOP率は「3記事差以上**かつ**translation MAJOR×0.75」に厳格化(または記述指標へ格下げ)。
- 分母は予定run数(各腕20)に固定しSTOPを独立カテゴリに。
- STOP記事の採用されなかった本文(`rejected_*.md`)もラベル対象(「出荷されなかった」別枠)。
- 2-2(EN)/2-3(JA)の軽微二重計上を解消。2-1「1テーマでも悪化」は判定ではなく要確認フラグ。
- JAはAstra/Lunaの文体差で腕が推測できるため盲検不完全と明記。
- 新規具体主張(ii)検出器(約¥0.2/本)を両腕のJA最終本文に指標追加。

## 論点7 停止・費用
- 旧4テーマでresearch/B3のAPI呼び出し(web_search含む)を検出したら即停止(er019 L92分岐は台帳コピー漏れ時に黙って再実行する)。
- 予算は各API段の前に横断集計(worker別台帳合計+実行中見込みの予約)で判定。astra単価はG1後にダッシュボード請求増分と照合、照合までガードは×1.5安全係数。
- G1カナリアにChecker 1 run(動的fixture `baseline_parsed=None`のruntime確認)と旧腕の再利用分岐でAdvancedまで通す確認を追加(約+¥8)。
- 旧4完了後に中間チェック(フロー健全性のみ、新腕STOPが系統的[例4/4]ならFable停止判断)。TTSはG2から切り離して後回し。

## 論点8 R0復唱(OPEN-175)
- 検出のみ(案A)。R0と最終JA(R2)の両方で検出し、改稿後も残るかを記録。残れば表現上の軽微として別枠。

## 費用影響(Opus/Fable推定)
- 追加分約¥25〜30(B1除く)、B1上限3回で最大+¥105、総額推定約¥690〜900。上限¥1,000内。

## Fable採用判断(2026-10-09)
- 上記8論点を採用し、設計書・事前登録のv2へ反映する(委任_03)。USER_DECISION_REQUIREDに該当するProduction採用の判断はなし。STOP条件(11-3)の該当なし。
