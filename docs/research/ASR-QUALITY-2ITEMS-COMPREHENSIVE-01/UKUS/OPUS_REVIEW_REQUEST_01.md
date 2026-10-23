# ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ②英米綴り OPUS_REVIEW_REQUEST_01
(Opus独立レビュー依頼。条件A=新しい構造・処理フローの設計(PM_GOVERNANCE 11-3)。対象=DESIGN_01.md の推奨案A。レビュー自体はFableが起動する。)

## 依頼対象と読む順
1. ROOT_CAUSE_01.md(根本原因・定量・費用)
2. DESIGN_01.md(選択肢A〜H、推奨A、安全条件、検証V1〜V8、事前確認5-1)
3. 実データ: `work/ukus_census_01.json`(保存転写の英米綴り抽出)、`work/ukus_sim_01.json`(机上シミュレーション)、`work/ukus_rules_probe_01.json`(規則の再現率と誤同値)
4. 参照コード(file:line): `er109_asr_orthographic_equivalence_01.py:12-17,401,709`、`er109_xz_scope_01.py`、`er006_secondary_asr_01.py:1130-1141`、`er006_preprod_hardening_01_validation.py:56-62,446-447`、`er020_tts_retry_local_rewrite_01.py:57,64,181,708`

## 設計の要点(1段落)
英米綴り差を「同一語の地域綴り」という新カテゴリとして、VarCon(寛容license)+breameの英米辞書と、制限規則(ise/ize・yse/yze・our/or)でUS正規形へ写像し、er109の既存入口(`_units`のkey)に挿す。音素層(v1)は緩めない。X/Z限定・既存全層不合格時のみ・1:1位置対応・固有名詞/数/記号は対象外・他の実差があればNG維持・AMB対は一方向。A/B/Cとval(共有Validator)は無変更。

## Opusへ見てほしい論点(優先順)
1. **誤PASSリスク**: (a)辞書の誤り(VarCon level≤70にも`saki/sake`、`arse/ass`等が混在。人手レビュー+denylistで十分か、別の自動検出が必要か)。(b)ASR側が実際に別語を聞き取ったのに、辞書上の対と偶然一致するケース(例: canonical `tyre`、ASR `tire`=語義差)。AMB一方向+警告で十分か。(c)同じ文にUKUS差と実誤読が同居するとき、key正規化が実誤読の検出を弱めないか(difflib整列の副作用)。
2. **構造の妥当性**: `_units`のkey/pronsをpost-processする方式(案A)と、`evaluate`に専用spanルール(`_judge_span`)を追加する方式のどちらが、保守性・誤PASS・監査可能性で優れるか。key正規化は「語を等価にする」ため、audit上の `spans` に差分が現れない(equal扱い)点を、`ukus_pairs`の別記録で補う設計で十分か。
3. **固有名詞境界(①との整合)**: entity tokenを本層の対象外にした判断は妥当か(`Grey/Gray`人名で綴り違いのみ=PNAP側でどう扱われるべきか。①のPN設計と矛盾しない境界定義の提案)。
4. **規則フォールバックの範囲**: ise/ize・yse/yze・our/orのみ許容し、-ity→-ty等は却下した判断(誤同値の実測: 全規則202件、制限規則6件=同一語の変異)。さらに安全な絞り方(語幹長、wordfreq閾値、辞書要件)や、逆に不足する規則クラスがあるか。
5. **警告の扱い**: Tier-2とAMB一方向を PASS_WITH_WARNING にする案が、事後試聴リスト(ユーザー負担)を不要に増やさないか。綴り差は音声に影響しないため監査件数カウントのみに留める案との比較。
6. **PASS_WITH_WARNING/最終ANDゲート/Store再利用**: er109受理音声のStore再利用ブロック(X/Z限定)や `APPROVED_EQUIVALENCE_BASES` 非追加(P-06)との整合。UKUS層を追加してもこれらの既存挙動が変わらないか。
7. **検証計画V1〜V8の十分性**: 件数・成功基準・独立源(breame vs VarCon)の使い方・一般化(20%隠し)の妥当性。追加すべき失敗モード(例: 活用形、複合語、ハイフン、所有格、全角/ASCII引用符)。
8. **代替案の再評価**: H(LR入口の防御)を多層防御として併設すべきか。G(脚本米綴り統一)・E(ASR誘導)・D(3rd ASR)の却下理由に不足はないか。
9. **ライセンス/配布**: VarCon(SCOWL Copyright)とbreame(Apache-2.0)のリポジトリ同梱可否と表記要件。

## レビューで明確にしてほしい出力
- 設計の抜け漏れと誤PASSシナリオの具体例、修正案(必須/推奨の区別)。
- 推奨案を変更すべきか(A維持/修正/別案)。
- Trial実装に進んでよいか(条件付き可の場合は条件)。

## 制約(レビュアー向け)
- Production・Prompt・flag・閾値・脚本の変更は本件で一切していない。A/B/C凍結(PM_GOVERNANCE 27-3)。Production採用はユーザー判断(VALIDATED止まり)。
- 現時点の机上値は暫定で、正式な数値はTrialで取り直す。
