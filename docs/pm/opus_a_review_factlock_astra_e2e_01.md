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


---

# B3注記仕様 v1 レビュー(2026-10-09、委任_04で追記)

性質: Opus独立技術レビュー(PM_GOVERNANCE 11-3 条件A=新しい構造・処理フロー)の結果要点。**本節はFableの手元にあるレビュー結果の要点転記で、Opus原文ファイルは未作成**(原文との照合はFableが保持)。
レビュー対象: `er052_output/factlock_astra_e2e_trial_01/B3_ANNOTATION_SPEC_v1.md`、`b3_annotation_check_01.py`、`B3_ANNOTATION_SPEC_v1_OPUS_POINTS.md`(8論点)。
反映先: `B3_ANNOTATION_SPEC_v2*.md`、`b3_annotation_check_01.py`(修正)、`b3_annotation_merge_01.py`(新設)ほか(委任_04)。Opusレビュー自体はユーザー承認Gateではない。Production採用は人間ユーザーのみ承認する。

## 「ユーザー提示前に必ず直すべき点」8件(Fable採用判断済み、全て反映)
1. 注記者用の版を分離: §7(旧4の予想解答)と過去の注記版のパス・汚染源(`annotate_briefs.py`のSPEC、`ANNOTATION_LOG.md`、`astra_revise_matrix_02/DESIGN.md` L21、`prep_inputs.py` L47-49)への言及を除いた注記者用版を作りsha256を固定。例示は架空の記事。完全版(Fable/評価用)とOLD4_EXPECTED(隔離)を別ファイル化。注記委任文は10記事共通の固定テンプレート(sha256固定、補足禁止)。隔離は(i)貼り付け渡し+返答本文受け取り、(ii)事後監査(transcriptのRead/Grep/Glob等を参照禁止リストと照合)の両方。新agent定義は新設しない。A・Bが同モデルで誤りが相関し一致率が高めに出る限界を明記。
2. 中核・周辺はスクリプトが計算: 表記・種類・台帳ID・概念から計算し、宣言との完全一致を検査(付け漏れも検出)。二重注記の食い違い解決は統合入力からの再計算(決定論の統合スクリプト、手作業禁止)。種類・分割の食い違いは保守側規則のまま。一致率の判定線を事前登録(推定値: 分割一致率0.8未満または中核Jaccard 0.67未満)。数値0件の記事はJaccardに含めず件数併記。
3. E1/E2の数字比較バグ: 先頭0を除きint/float正規化、`(numeric_scope: …)`除外、主数字(表記末尾の数字列、範囲は両端)限定、交差の緩さ廃止。ISOと和文の両方で日付一致。
4. E2→E2': 紐付く台帳factの`date_or_period`の先頭の日付表現と日付の数字が一致(年のみ対象外)、Storyline出現は条件にしない。Opus手計算で旧4の過去人手注記と全て一致する見込み→v2でスクリプト実測。E2'は設計選択として「推奨」と明記。
5. 分割・段落正規化の統一: 許す差分を`。`直後(または節先頭)の「改行と `- `」挿入のみに限定し、逆変換して原文と厳密一致で検査(全空白削除比較の廃止)。箇条書きbriefの分割でFAILになる矛盾を解消。限定文が別台帳ID由来なら別事実にせず(S2より優先)その台帳IDをledger_idsに追加。
6. 「全件中核禁止」の文言を式と整合: 式`max(3, min(6, floor(n/2)))`固定、文言は「上限は式による(n≤5では全件中核になりうる)」。優先順 Storyline量→他の量→日付。外れた概念数を記事ごとに報告。Writerプロンプトに中核上限なしを確認済み(影響なし)。
7. STOP範囲の縮小: 台帳外の記述はunmapped_claimsに種類別で記録しSTOPしない。評価時は該当文由来のNGを「B3由来」として両腕で別集計しFact Lock起因に数えない(PREREGISTRATIONに1項追加)。STOPは(i)Storylineの主張自体が台帳に無い、(ii)台帳に無い数字がE1/E2'適格の形で記事の中心にある、の2場合のみ。
8. スクリプトの穴: 架空の中核(宣言表記が本文に1回も出ない)検出、概念の束ね検出(概念内の台帳ID、短い表記が長い表記に含まれる、種類判定を先頭要素だけにしない)、サイドカーのsha256・annotator照合、台帳スキーマ点検と代替規則の事前登録、複合タグ禁止。`%`/`％`のNFKC・漢数字は警告のみ(持ち越し)。harness`load_core_numbers`の年月日分解による周辺数値の見逃しは記録のみ(harness変更禁止)。
- 名称内番号は案Y(【周辺数値】印)継続。分割単位(台帳fact ID境界、主体・行為・時期で割らない、1項目最大3)は採用可。

## Fable採用判断(2026-10-09)
- 上記8件を全て採用し、v2をユーザー提示用とする。USER_DECISION_REQUIREDに該当するProduction採用の判断はなし。STOP条件(11-3)の該当なし。

## 評価レビュー(任意、2026-10-09): EVAL_E2E_01 v1(委任_15)
性質: Opus任意レビュー(Fable裁量、1日2回枠内)の要点。**本節はFableの手元にあるレビュー全文からの転記(委任_16の委任文経由、Opus原文ファイルは未作成)**。レビュー対象: `er052_output/factlock_astra_e2e_trial_01/eval/EVAL_E2E_01.md` v1。反映先: EVAL_E2E_01.md v2・HUMAN_CHECK_E2E_01.md v2・`eval/judge_table_01.py`・`eval/merge_labels_01.py`。Opusレビュー自体はユーザー承認Gateではない。Production採用は人間ユーザーのみ承認する。
1. **semiconductor新 EN STOPの帰属訂正**: 『B3注記のqualifier文由来』は誤り。原因文は注記前のB3 Storyline本文(`runs/semiconductor_earnings/shared/brief_original.md` L7、旧腕briefにも同文)にある指示文。新腕ではFact Lock R0が本文化し【事実1】タグを付け(`new/new_writer/r0_with_tags.md` L11)、Astra R2が不在断定へ強め(`r2.raw.md` L13)、EN検査がMAJOR(`b1b/audit/deviation_checks/advanced_attempt1.json` L20)。帰属=brief内の指示文がFact Lock R0経由で事実扱いされ、Astraが不在断定へ強めた新腕固有の経路。注記の副作用ではない(箇条書き化が促した可能性は推測)。unmapped_claims該当のため事前登録§5-11の『B3由来』別集計値を併記(Adv STOP 新1/9、人手介入 5対6、判定不変)。
2. 2-2 JA列からopenai新(w3-40、未出荷本文)を除外。平均比と符号検定を再計算(判定『同等』は不変)。
3. 人手介入の感度値(実際に失ったChecker run: 新8/旧6=0.444対0.333)を主表へ格上げ。
4. ラベル基準の統一: semi(偽陽性)とspace B-02/B-03(不在断定=軽微境界)は同型。同じ基準(OC-8)に揃える。
5. 言い過ぎの訂正: 注記起因の過剰ブロックは確認0件(central周辺扱いが未検証の候補1件のみ)。『新腕はChecker欠陥に強い』は母数不足による見かけ。M3保護6件は便益・コストとも観測不能(床効果)。
6. 層別逆転の説明(妥当順): B1枠の消費順による移転(事実)、開発セットへの適合(旧4=Fact Lock/Astra matrixの開発テーマ、新5=out-of-sample。新5の新腕介入5/10対1/10は汎化性能の正直な推定値)、偶然、B3形式、注記粒度。
7. Fable最終判定(判定線ごと)、8. 人間確認パックに面白さpairwise追加(¥0)、9. OPEN候補の優先度(OC-1最上位、OC-3/OC-8次点)、Production Checker文分割器の配線確認、次の選択肢(a)〜(e)。

### Fable採用判断(2026-10-09)
- 上記を全て採用し、EVAL v2・HUMAN_CHECK v2へ反映(委任_16)。USER_DECISION_REQUIREDに該当するProduction採用の判断はなし。STOP条件(11-3)の該当なし。Opusレビュー後もProduction採用は人間ユーザーだけが承認する。
