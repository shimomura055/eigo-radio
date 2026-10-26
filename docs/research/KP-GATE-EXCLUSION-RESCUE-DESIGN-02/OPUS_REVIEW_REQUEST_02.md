# OPUS_REVIEW_REQUEST_02: 設計が実質的に変わった部分のみの独立技術レビュー依頼(条件A、read-only、API 0)

管理ID: KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_01 / 起動=Fable(11-3、Opus枠は管理IDごとの運用に従う)。
**レビュー対象外(前回レビュー済み・同じ論点を繰り返さない)**: 救済フローの骨格(revert+validator再適用)、M1(LLM提案語の部分集合)、M2(HR経路限定)、M3(gloss再整合強制)、M4(QA未再判定・AUTO不可)、M5(外側retry現行維持)、M6(同一引数)、R2〜R4。前回指摘は`KP-GATE-EXCLUSION-RESCUE-DESIGN-01/OPUS_REVIEW_01.md`、反映状況は`DESIGN_01.md` §0。

## 対象(実質的に変わった/新規の部分)と観点

| # | 対象 | 何が新しいか | 見てほしい点 |
|---|---|---|---|
| Q1 | **副詞前の原形化の検査設計** (`PATTERN_DESIGN_01.md` B、`er123 RulePatch(adverb/quant)`、`_doubling_options`/`forms`) | guard(`er105:662`)に「manner副詞後続」「量化詞限定詞後続」を足す。追加経路にだけ前方活用生成一致(CMU強勢で重子音化)・副詞の句内位置条件を課す | (a)三重検査(LLM提案語・CMU実在・前方活用一致)+文脈条件で、`heated debate`型の誤変換防止という元の目的を損なわないか。(b)**区分1(規則文に無い内部条件の是正)と判定したが、受理面の拡大と見るべきか**(境界判定の妥当性)。(c)副詞の閉表(-ly形容詞除外表・`again/alone/hard/well…`)の漏れ・過剰 |
| Q2 | **lexical have/has/had の役割判定** (`have_role`、`finite_aux_roles`) | 語形リストの`have/has/had`を役割判定(語彙/aux)にする。fulltext経路限定。迷えばaux | (a)倒置・副詞挟み・形容詞化分詞+目的語・文頭大文字の扱いの網羅。(b)**OPEN-152(語彙動詞have誤検知、`USER_DECISION_REQUIRED`/Non-blocking)との整合**: 本設計は区分1(誤判定の是正)としたが、OPEN-152は『Production QA変更に当たるためユーザー判断』と記録している。どちらが妥当か。(c)P-04(3)の`has/had→have`が現行で成立しない(dead path)という主張の検証 |
| Q3 | **語数超過の救済方式** (`PATTERN_DESIGN_01.md` A、`subspan_candidates`/`slot_generalization_candidates`) | A1: 連続部分列+演算子作用域の決定論禁止+動詞句末の目的語欠落禁止+(任意)LLM評価者。A2: スロット一般化`too soon to do`を検証したうえで区分3推奨 | (a)意味反転・比喩喪失の歯止めは足りるか(演算子語の閉表)。(b)A2を区分3とする根拠(独立評価で不自然/意味changed、本文に無い語)は十分か、ユーザー判断材料として区分2に残すべきか。(c)LLMを「評価者」に使う設計(生成は決定論)がRule7/決定論Gateの思想と矛盾しないか |
| Q4 | **トリガー拡張・その他の新規救済** (`rescue_structural_revert`、`reanchor`、`contains_finite_aux_role_based_idiom`、`rederive_m1`の範囲拡張tail破棄) | cmu_post_canon/構造違反→revert(R1)、原形で返された選定句の本文再アンカー(既存validatorの逆向き使用)、辞書見出し(Wiktionary)の核に限る法助動詞例外+主語除去、LLMの窓外tailの破棄 | (a)再アンカーが新しい受理基準を作っていないか(窓一意性・複数窓の扱い)。(b)慣用句例外が「完全文・節の排除」(ER-003-P2G)の原意図を保つか(主語除去の設計)。(c)外部辞書(Wiktionary、CC BY-SA、延べ17,389件)をGateの受理根拠に使う妥当性・運用リスク |

## 読ませたい資料(最小)
1. `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/{DESIGN_01,PATTERN_DESIGN_01,CASE_ANALYSIS_01,RESCUE_TABLE_01,LOOP_LOG_01}.md`
2. `er123_kp_rescue_dev_01.py`(`RulePatch`:1行目から約150行、`have_role`、`forms`/`_doubling_options`、`subspan_candidates`、`rederive_m1`、`reanchor`、`decide`)と `er123_kp_rescue_dev_01_test_01.py`
3. 実測: `selection_probe_01.json`(実選定句315種・単調性違反0・新規受理3変換)・`have_probe_01.json`(71窓)・`irregular_gap_01.json`・`judge_06〜08.json`
4. 既存仕様: `er105_kp_fulltext_selector_01.py:213-222,570-690`・`er003_key_words_canonicalization.py:439,576-632`・`er003_key_words_min_unit.py:3-9,258-261`・`OPUS_REVIEW_COND_A_01.md:118-123`(P-04)・`DECISION_LOG.md:7408`・`OPEN_ITEMS.md:328`(OPEN-152)

## 回答形式(希望)
Q1〜Q4それぞれに 採用/修正要(M)/推奨(R) と理由。特にQ1(b)・Q2(b)は区分判定(11-8)に直結するので、結論を先に。
