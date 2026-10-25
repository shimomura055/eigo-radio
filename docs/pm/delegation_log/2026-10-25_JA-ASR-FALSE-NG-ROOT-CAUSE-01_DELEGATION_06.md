管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_06(OPEN-517 Opus条件Cレビュー反映: proto v4・事前登録02・未知データAPI 0評価・過去公開物の監査抽出。**Production変更0・有料API 0**)。

## 読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(本案件節のみ)、`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/{OPEN517_DESIGN_01,OPEN517_PREREGISTERED_01,OPEN517_EVAL_01,OPUS_REVIEW_REQUEST_01_OPEN517}.md`、`proto_value_gate_fix_03.py`、`eval_open517_api0_03.py`、`er078_asr_value_guard_01.py`(:147-159 KANA_NUMERALS/WEAK_KANA_NUMERALS、:420-427 `_drop_verdict_ja`)、`er078_asr_unified_judge_01.py`(:68-73, :509-559)、`er066_ja_asr_orthographic_equivalence_01_trial.py`(:186-279 `_cands`)、`er058_output/unified_all_roles_production_wiring_01/DESIGN_02_ADDENDUM_01.md`(L65)、同`OPUS_REVIEW_A_01_VERBATIM.md`(L43)、`CURRENT_SPEC.md`(L2850, L2855のみGrep)、DECISION_LOGでOF-AUW-01の採用経緯(承認者・日付・ユーザー承認の有無)をGrep。

## 1. Opusレビュー結果(逐語を`OPUS_REVIEW_01_OPEN517.md`へ保存。要点)
- 総合: F1は方向正しい(CURRENT_SPEC:2855とユーザー原文「保護すべき差異を…解放する仕様にはしない」へコードを戻す是正)。ただし依頼文の前提に事実誤認(M-1)。F2 v3には値違いを等価にする穴2系統(M-2, M-3)。Production適用はM-1〜M-5解消を条件に可。
- **M-1**: skipの出自は承認済み設計追補`DESIGN_02_ADDENDUM_01.md:65`「最終ANDゲートは…承認済みのequivalence(HOMOPHONE…、Tier1 diff-anchored、読み一致)で既にPASSと確定した結果を再否定しない」=前回Opus条件Aレビュー(`OPUS_REVIEW_A_01_VERBATIM.md:43`)の推奨をFableがOF-AUW-01として採用。CURRENT_SPEC:2850は追補を「正本設計(DESIGN_01と食い違う場合は追補優先)」と位置づけ。IMPLEMENTATION_02b:19はそれを実装しただけ。→DESIGN_01 §1と「個別承認原文は未発見」の記述、報告文を訂正。F1は11-8不具合判定T1(コードがCURRENT_SPEC:2855「すべての採用転写を独立に再確認」と矛盾)・合格範囲を狭めるだけ・上位のユーザー原文へそろえる是正。適用時SSOT: ADDENDUM L65から「読み一致」を外しOPEN-517で上書きと付記、DECISION_LOG記録。L65の元の理由「承認済み救済が値ガードで無効化される(誤NG防止)」を必ず併記=F2はその手当て。
- **M-2**: `_replace_kana`が`out.find(r)`で位置無関係に置換。`_cands(7,day)="なのか"`、`(8,day)="ようか"`、`(10,tsu)="とお"`はProductionが一般語衝突(何なのか/しようか/通り)で`WEAK_KANA_NUMERALS`として外した読み。例: 原稿「7日に…何なのか」転写「8日に…何なのか」→現行DIFF、F2後は「なのか」→「7日」置換でatom[8日,7日]、UNKNOWN→PASS。必須: (a)`WEAK_KANA_NUMERALS`の読みを置換候補から除外 (b)単調性ガード: F2前にDIFFだった結果がF2後にUNKNOWN/EQUALへ変わってよいのは置換spanに対応するpairだけ。他pairの判定変化や全体DIFF→UNKNOWNはF2前の結果を採用。
- **M-3**: 語境界を見ないため長いかな数詞の前半/後半に一致して置換(10人↔さんじゅうにん、4日↔にじゅうよっか、百円↔にひゃくえん、十代↔にじゅうだい、2時↔にじゅう…)。必須: 一致かなの直前・直後がかな数詞の一部(数字の読み・位の読み・「ゅ」等)でないことを確認、または最長一致でかな数詞全体を解析し値が相手atomと一致する場合のみ置換。上記例を負例testで固定。
- **M-4**: 適用範囲は呼出回数でなく明示引数(例`kana_unify=True`)でREADING_MATCH PASSのPrimary最終ゲートだけ有効。test固定: `negation_diff`は置換前の元テキストで判定/Primary NG(P1)とSecondaryゲートではF2無効。
- **M-5**: 基準7として合成負例test一式を事前登録(M-2/M-3の例、誤った音便・連濁「さんほん」、同値atom並び、否定語近接の数詞)、全件PASS以外が合格条件。
- R-1 未知データ: コーパス凍結後/未使用の保存済みJA judge監査(X/Z/Y直近run、legacy A/B/C)をAPI 0で再評価、判定変化全件を目視。有料live不要。R-2 過去公開物: 監査recordは`value_guard.primary`を記録(:510、skip:530)→過去run dirで「`skipped=approved_equivalence:READING_MATCH`かつ値ガード=DIFF」をAPI 0抽出、公開物該当はユーザー報告(遡及是正はユーザー判断)。R-3 適用後初回runで「reason=final_gate_value_diff かつ basis=READING_MATCH」件数とHR Lock到達数を集計。R-4 `一分↔いちふん`のDEMOTEはSecondary stub結果、実運用はAzure次第(開示)。R-5 適用手順の抜け: `READING_RESOLVED_MATCH`(LLM resolver)とCandidate E由来PHONETIC_MATCHのbasis別test/`force_secondary=True`経路test/`_ortho_unlock_primary`がREADING_MATCHでNone/reason文字列変更(`primary_pass_approved_equivalence:READING_MATCH`→`primary_pass`)の下流影響(集計・Grep・allowlist・静的監査)/`er007_ja_secondary_asr_01.py:407`コメント/1行rollback用module定数(env/flag禁止)。R-6 期待読み表移設時のparity testに弱い読み除外を意図差分として固定。R-7 「晩」等助数詞表外は含めない→別OPEN(既知の限界)。C-1〜C-6問題なし(他3根拠のskip維持可、PASS集合は現行の部分集合、警告3件は残す、否定差はF2非影響[M-4でtest固定]、N3-07はOPEN-333)。Q6: 基準不足=負例基準(M-5)・未知データ(R-1)・F2発動全件一覧と値同一確認(正常143件中の発動数)・DEMOTEはSecondary次第の明記。§1のF2定義をv3→最新へ更新。ユーザー確認: F1はユーザー承認必須ではない(T1・狭める方向・上位原文へ)が報告必須(追補L65との矛盾/前回Opus推奨を今回撤回する方向/再生成・HR Lock増リスク)。Fableが追補L65を「ユーザー承認済み仕様」と判断するなら仕様変更=ユーザー判断(追補の承認時期・範囲は未確認→Fable照合)。過去公開物該当時はユーザー判断。F2はユーザー判断不要。

## 2. Fable判断
- M-1〜M-5・R-1〜R-7すべて採用。DESIGN_01 §1の事実誤認を訂正(`OPEN517_DESIGN_02.md`)。
- 追補L65のユーザー承認の有無は**DECISION_LOGで事実確認**(OF-AUW-01の採用主体・日付・ユーザー承認の明示有無)し、結果を報告。Production適用の最終可否はFableがその結果と本委任の評価を見て判断し、ユーザーへは「報告+確認」の形で提示する(本委任ではProduction変更しない)。

## 3. 作業
A. `proto_value_gate_fix_04.py`(v4: M-2(a)(b)・M-3境界/最長一致・M-4明示引数・否定差は元テキスト)+test(M-5合成負例一式=基準7、M-3の表5例、M-2例、「さんほん」、同値atom並び、否定語近接、Primary NG/SecondaryでF2無効、`negation_diff`元テキスト)。v3は凍結保持。
B. `OPEN517_PREREGISTERED_02.md`(F2定義をv4へ、基準7追加、F2発動全件一覧+値同一確認、DEMOTEはSecondary次第、未知データ基準)。
C. `eval_open517_api0_04.py`: 既存771件の再評価(v3との差分表)+**未知データ**(R-1: コーパス凍結後/未使用の保存済みJA judge監査=X/Z/Y直近run・legacy A/B/C。対象の列挙方法と件数を明記)。判定変化全件を表で。F2発動件数と値同一確認。2回実行で決定的。`OPEN517_EVAL_02.md`。
D. R-2 過去公開物監査 `open517_public_audit_01.py`(API 0): 全run dirのjudge監査recordから「skipped=approved_equivalence:READING_MATCH かつ value_guard.primary=DIFF」を抽出、公開物(`user_test/`配下のmp3に対応するsegment)への該当有無を表に。`OPEN517_PUBLIC_AUDIT_01.md`。
E. R-5の適用手順の抜けをProduction適用計画`OPEN517_APPLY_PLAN_01.md`に追加(test一覧・reason文字列の下流影響調査結果・rollback定数・ADDENDUM L65/CURRENT_SPEC/DECISION_LOGの更新文案・R-3の集計方法)。R-7の別OPEN登録(「晩」等助数詞表外、分類=既知の限界)。
F. SSOT: OPEN-517更新(Opus反映・v4結果・未知データ・公開物監査結果)。直前再Read・最小Edit・バックアップ。CURRENT_SPEC/ADDENDUM変更なし(適用時)。
G. Git: 対象pathのみadd→`git commit --only`→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告)。禁止: `git add -A/-u`・amend・rebase・force・stash・reset --hard。secret grep 0件。
H. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_DELEGATION_06.md`(Nは591前後、先頭「管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_06」を585〜620で走査)。Opus依頼文(先頭「管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01(OPEN-517)。Opus必須レビュー」)も`..._OPUS_REQUEST_DELEGATION_02.md`へ。

## 禁止
Production code変更、有料API、v1〜v3 protoの変更、助数詞表の拡張、B-light実装。

## 報告(RESULT_PACKET_JAASR6.md+口頭要約)
OF-AUW-01の承認事実(DECISION_LOG引用)、v4の変更点、基準7の結果、既存771件+未知データの判定変化(件数・全件表の所在)、F2発動件数・値同一、公開物監査結果(該当件数・該当segment)、適用計画の要点とリスク(再生成・HR Lock増)、費用0円、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3)。