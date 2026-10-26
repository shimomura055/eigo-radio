# PREVENTION_01 — 再発防止設計(Gate / 受入 / Family新設チェック / test)

管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_01 / read-only。原因=ROOT_CAUSE_01(共通の盲点=「記録の有無」は確認するが「実行時の実測値==承認値」を確認しない)。
方針: 新Gate・新報告工程を作らず、(1)既存のGate呼出し(`y_style_gate`)に「実測値と承認値の照合(fail-closed)」を加え、(2)受入の**証拠の定義**を具体化し、(3)機械照合testで台帳と実装の乖離を落とす。(b)のPM_GOVERNANCE改訂は**提案文**であり、実質変更か明確化かの判定(29-3 C-14〜C-18)とユーザー承認要否はFableが決める。

## (a) Gate: 承認profile名と実測prefixのaudit必須化(fail-closed)
Y(新設・委任_02で実装。`y_style_gate`内、課金後のassemble前):
| 検査 | BLOCK理由 | 現状(事実) |
|---|---|---|
| `audit/style_profile.json`の存在 | `Y_STYLE_PROFILE_RECORD_MISSING` | 現状は記録なしでPASS(Yは記録を作らない) |
| 記録のsha256が現行定義と一致(`verify_record`) | `Y_STYLE_PROFILE_RECORD_MISMATCH` | 未検査 |
| `record.profile_id == Y_APPROVED_STYLE_PROFILE`(waiver時のみ例外) | `Y_STYLE_PROFILE_NOT_APPROVED` | `default`がPASS |
| 当該levelに適用される全role(FULL_STORY=Y 8本文segment、SUPPORT_JA[a2]、PREVIEW[b1b]、KP_EN、KP_JA_MEANING[a2]、KP_EXPLANATION_EN[b1b])で検査対象(`checked`)が≥1件 | `Y_STYLE_COVERAGE_EMPTY(role)` | `checked=[]`でPASS |
| 各segmentの`style_profile.style_base_sha256`==承認roleのsha256(実測prefixの照合=既存`evaluate_segment_evidence`) | 既存reason | defaultでは非実行 |
| 出力: `audit/style_actual_vs_approved.json`(role・segment・承認sha・実測sha・voice・model_id・減速適用有無の表) | — | 無し。受入(b)の証拠になる |
Xは既存の`resolve_run_profile`(新out_dir既定=`fx_20261017`)+`m3_assembly_gate`で新規runは同等(`er019_family_x_style_profile_01.py:187-189,458-`、runner`:2353-2380`)。ただしX/Zにも「`checked=[]`/記録なしでPASS」となる経路(legacy `default`明示resume)は残る:
- **X**: 提案=上記の`checked`非空・role網羅の検査を共通helperとして`er019_family_x_style_profile_01.py`に置きXでも呼ぶ(legacy default明示runは除外)。X Production挙動に触れるため委任_02には含めず、Fableが別委任の要否を判断(判断候補ではなく11-8 B未満の強化=任意)。
- **Z**: runner起動時`assert_style_table_integrity`(`er026_family_z_fiction_production_runner_01.py:1335`)でsha固定表を検査するが、生成segmentの実測prefixを承認値と突き合わせる検査の有無は本委任では**未確認**(別read-only確認を提案)。
- 全Family共通の最小要件(提案): 「承認profile/定数のid」と「実測prefix(sha)」を各runのauditに必須で残し、空はFAIL。

## (b) 受入: PM_GOVERNANCE改訂案(Fableが提案・判定)
1. **Gate 7(`PM_GOVERNANCE.md:276-`)「(3)証拠」の具体化**(明確化案): 「Family/共通仕様を扱う受入では、正式経路で実測した値(Style profile id と role別prefixのsha256、Voice、model_id、速度処理の適用有無)を承認仕様の値と**1行ずつ照合した表**を証拠に含める。実測値が空・記録なし・`checked=[]`は『一致』ではなく『不一致』として扱う。」(必須5項目の項目数は変えない。証拠の定義を具体化するのみ)
2. **Closeout項目33(`:618-625`)の具体化案**: 「OPEN_ITEMSへの記録のみでは充足としない。当該Familyの初回/新規の正式runを完成・公開する前に、(i)配線済み(実測照合表あり)または(ii)ユーザー承認済みの例外(ref付き、Status表に記載)のいずれかであること。未配線のままのrunを『完成』『PRODUCTION_WIRED』と呼ばない。」
3. **11-8の適用確認**(`:2564,2568`の再確認で、新規規則ではない): 不具合(B)に「ユーザー判断待ち」「適用時期=ユーザー判断」を付けない。OPEN登録時に「分類(不具合/仕様候補)」と「状態ラベル」の整合を確認する(OPEN-537はB+ユーザー判断待ちで不整合だった)。
4. **28-2運用2の補足案**: 新規Family E2E開始/終了チェックに「共通仕様Status表の当該Family列に『未着手』が残っていない(または例外ref付き)」こと、および機械照合test(下記(c))の存在・PASSを加える。
5. **CURRENT_SPEC更新責任**: 「共通仕様のFamily別配線Status表」のY列は、Y run公開・PRODUCTION_WIRED判定のたびに、Fable受入の同一commitで更新する(更新契機の明記)。
分類(Fable判定用の事実): 1・2・4・5は新Gateや新報告工程ではなく既存規則(28-1運用3/4/7/8、項目33)の運用具体化。ただし受入の証拠要件の強化にあたるため、29-3の「実質変更(緩和・新規追加)」に当たるかの判定が必要。強化方向の変更であり承認済み品質基準の緩和ではない。

## (c) Family新設チェックリスト+機械照合test
- test新設(委任_02): `er121_family_y_common_style_coverage_test_01.py`。内容=
  1. Y側カバレッジ表`Y_ROLE_COVERAGE`(role→対象Y segment/level or `exception={id, user_ref}`)。`set(Y_ROLE_COVERAGE) == set(STYLE_PROFILES[Y_APPROVED_STYLE_PROFILE]["overrides"])`。X側にroleが増えるとYが落ちる(Zの`CROSS_FAMILY_COMMON_STYLE_MAP`と同型: `er063_family_z_audio_01.py:268-`)。
  2. 各roleの`ROLE_LEVELS`とYのlevel/segmentが矛盾しない。例外にはuser_refが必須。
  3. Y runnerのAST検査: `resolve_run_profile`と`assert_profile_backend`を呼ぶこと、`"default"`リテラルをstyle_profile引数に渡さないこと(`er121_family_y_structure_match_test_01.py`の許可リスト方式を拡張。現行は音声層関数のみでrunner `main`層と引数値は対象外=ROOT_CAUSE Q2-3)。
- チェックリスト(新Family用、28-2運用2の具体化): ① 共通仕様Status表の当該列に未着手が無い ② `resolve`相当の呼出しがrunnerにある(上記AST test) ③ 実測照合表が出る(Gate出力) ④ Family固有例外はユーザー承認ref付きで表に記載。

## (d) test: runner profile == 承認値の固定
`er121_family_y_runner_01_test_01.py`等に追加:
1. `Y_APPROVED_STYLE_PROFILE == "fx_20261017" == er019_family_x_style_profile_01.DEFAULT_NEW_RUN_PROFILE`(Xの既定が変わればYが落ち、Y側の承認判断を強制=自動追従しない)。
2. 6 roleのsha256をリテラル固定(`FULL_STORY=3a680861…`等。`style_matrix_01.json`の`roles`と一致)。
3. mock実行で`audit/style_profile.json`生成・Gate出力の`checked_roles`が全role網羅・`default`注入でBLOCK。
4. CURRENT_SPEC承認値との照合: Status表の文言はmarkdownで機械読取りに不安定なため、`style_matrix_01.json`(本委任成果)を承認値のスナップショットとしてtestに取り込み、CURRENT_SPEC表の更新はFableの受入commitで同時に行う(testが読むのはjson)。

## 想定外れ・残余リスク
- 実測照合はStyle prefixの文字列であり、**音の聞こえ方**(平板化=S9)は検出できない→再試聴(ユーザー)が必要。
- LR再TTSのStyle脱落(CC-F2)はGateで人間承認要求になるが根本はOPEN-540側。
- Z実測照合の網羅性は未確認(上記)。
