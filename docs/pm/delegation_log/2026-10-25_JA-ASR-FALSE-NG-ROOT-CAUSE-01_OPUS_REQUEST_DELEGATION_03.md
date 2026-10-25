管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01(②B-light)。Opus必須レビュー(PM_GOVERNANCE 11-3 条件A: 新しい判定フローの設計、Trial拡張・採用提案前)。読み取り専用。日本語で報告。

## 背景
ユーザー承認(2026-10-25): B-lightの原因究明・設計・Trialを承認(Azure Secondaryの認識結果を安全に活用。Azureが数字を正しく認識しただけで無条件PASSさせない。UDR #136の変更は別途ユーザー承認)。③OPEN-517 F1+F2(読み一致PASSにも値・否定の最終確認)はXYZ共通で正式採用済み・Production適用中(別agent)。
Sonnet成果物(C:\Users\tensh\eigo-radio\docs\research\JA-ASR-FALSE-NG-ROOT-CAUSE-01\): B_LIGHT_ROOT_CAUSE_01.md / B_LIGHT_DESIGN_01.md / B_LIGHT_PREREGISTERED_01.md / B_LIGHT_EVAL_01.md / B_LIGHT_BUDGET_PLAN_01.md / OPUS_REVIEW_REQUEST_01_BLIGHT.md / b_light_proto_01.py(+test 44) / eval_b_light_api0_01.py。関連: OPEN517_DESIGN_02.md・proto_value_gate_fix_04.py(F1+F2)、proto_reading_compare_02.py(v2)、`er078_asr_unified_judge_01.py`(:567-568 P1がAzure前にNG_PROTECTED)、`er007_ja_secondary_asr_01.py`(:83,643 Secondary受理=EXACT/NORMALIZEDのみ)、`er078_reuse_value_guard_01.py`、CURRENT_SPEC L2179/L2856/L2865、DECISION_LOG:21995-22003(UDR #136)、:20663(2026-10-11安全条件)。

Sonnet設計の要点: 推奨=案β「Azureは値の証人としてのみ使い、読みはPrimaryで保証。PASS条件=Secondaryの値が原稿と一致 かつ Primaryの読みが一致 かつ Primaryの数値が原稿値と等しいか『位取り断片の連結崩れ』(8000900=8000+900)として説明できる場合のみ」。新受理クラス(composite)+PASS_WITH_WARNING、最終ANDゲートは常に通す、`APPROVED_EQUIVALENCE_BASES`に入れない、フック3点(P1緩和・F1最終ゲート降格・P3許容集合)、reuse guardは保存Secondary転写でcomposite再実行が必要。却下: α(効果0)、ε(Primary単独の数値解釈系統)、γ(ローカルWhisper第3票=UDR #136条件3に抵触)、δ(Secondary読みで受理=2026-10-11条件に抵触)。UDR #136は変更不要(βは非接触)。
評価(API 0、pin 89b630bd1+F1F2 v4再現): 増分誤PASS=N-3 30clip 0・合成負例55件 0・実履歴P-S対43件 0、回帰0、Melos副作用0。N-1確定負例151対の最悪ケース(Secondaryが原稿そのもの)で露出1件(N1-new-018 値garble型、自作合成)。月題12転写: 現行2→v2 4→F1F2後3→β5(+2、いずれもattempt3)。attempt1(Primary読み誤り)0/4、attempt2(2エンジンの値矛盾)1/4のまま。評価不能: P-4実attempt 562件(Secondary記録0)、未知493件、実履歴133件、N-1 151対(実転写なし)。新規所見: **F1適用後、読み一致+数詞崩れの正常音声(「月のシワ、8000九百本超」)が新たにNG化**(月題1/12、07Aの1,264件評価に含まれない型)。βはこれを戻す。追加有料Trial見積: T1=別題材40clipで汎化確認 約13〜38円。

## レビューしてほしい論点
1. βの安全性: 「Secondary値一致+Primary読み一致+Primary数値が原稿値と等しいか位取り断片連結として説明可能」の3条件に、誤PASSの穴(例: Primary読み一致の判定自体がVariant Layer/音韻救済で緩い場合、断片連結の説明可能性が広すぎる場合[8000900以外の崩れ方、桁欠落「千九百」の扱い]、Secondaryの読みが誤りでも値だけ一致する場合、否定・助数詞違い、複数atom)がないか。合成負例55件の網羅性。
2. F1との整合: F1が新たにNG化する「読み一致+数詞崩れ」型(正常音声)の扱い=βで戻すのが妥当か、F2(かな数詞統一)の拡張で扱うべきか、またはF1側に「Primary読み一致かつ値DIFFがatom連結崩れで説明可能」の救済を置くべきか。F1適用の先行(今日)で生じる誤NG増のリスク量。
3. UDR #136との整合判断(βは非接触)の妥当性。新受理クラス追加=ユーザー採用承認が必要という整理。
4. 効果の限定性(+2/12、attempt3のみ)を踏まえ、Trial継続の価値: T1(別題材40clip、13〜38円)を実施すべきか、方式見直し(γ等)の検討をユーザーに進言すべきか、ここでVALIDATED(限定)で止めるべきか。「効果の薄い方式を繰り返さない」原則との関係。
5. reuse guard(`er078_reuse_value_guard_01`)・HR Lock・retry cascadeへの影響と、X/Y/Z共通経路での位置。
6. 事前登録(B_LIGHT_PREREGISTERED_01)の過不足。

## 出力形式
必須修正(M-n)/推奨(R-n)/問題なし確認(C-n)/ユーザー確認が必要と考える点(理由付き)/Trial継続・採用提案の可否の総合所見。断定できない点は「未確認」。