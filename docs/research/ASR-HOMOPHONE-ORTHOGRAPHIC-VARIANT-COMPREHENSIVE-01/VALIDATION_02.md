# VALIDATION_02(ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_02、2026-10-22。API 0・費用0。VALIDATEDの宣言はFable)

対象: (1) B不具合3件の最小修正(Productionへ反映済み・独立commit d9e36f54a) (2) er109 v1(Opus P-01〜P-09是正後。**未配線・既定OFF**)。Opusの十分条件F6(1)〜(7)に沿って記す。生データはすべて同ディレクトリのjson(再現コマンドは各scriptのヘッダ)。

## 0. 結論(先に)
- B修正: 前後比較12,342件で**PASS→NG 0件**、NG→PASS 26件(不合格→合格のみ)。Zの`seize`/`sees`は新判定でPASS、`seize`/`cease`・`lead`/`led`・`are`/`or`・`desert`/`dessert`・`billow`/`below`はNGのまま(testで固定)。
- er109 v1: 敵対的負例(CMU全体56,002語対+2語oronym 22,380+数oronym 2,766+略語50,036対)で**誤同値は閉じた略語表の正規展開4対(corp/corporation, ltd/limited, mrs/misses の双方向)のみ**。同じ負例セットで旧v0は誤同値が多数(下記§2)。保存4,879行のON/OFF比較は**PASS→NG 0**、NG→PASS 19行(13 distinct pair、X 10行/A・B・C 9行、Z 0行)。ユーザー指摘NG音声(問題音声21件=45転写+固定既知NG18対)で新規PASS 0。
- 正例の同値率は是正で低下(KP 100%→95.1%、本文99.2%→94.8%。ただし既存判定との合算[union]はKP 99.3%・本文98.6%)。低下は設計どおり(同形異音語・stress差・弱形・曖昧略語を同値にしないため)。
- 判定: **VALIDATED候補**(F6の1〜7を満たす)。ただし下記の未達/注意(Whisper裏付けが一部不一致、er094経路の短文到達性の拡大)をFableが評価すること。

## 1. B不具合3件の修正と前後比較(`bfix_before_after_01.json`、harness=`er109_b_fix_before_after_01.py`)
同一item集合(保存attempt行 primary 2,212+azure 88[distinct]、機械生成正例/負例 KP 1,130/3,057・本文 2,099/3,745、固定fixture 11)を、修正前コードと修正後コードで判定。非KPは本物のunified judgeと同じ最終ANDゲートも適用。
| set | n | PASS→NG | NG→PASS |
|---|---|---|---|
| stored_primary | 2,212 | 0 | 4(Z kp3/kp4 `seize`/`sees`・`Seas` 3件+B pool_n5 full_story_part2 の`twenty eighth`/`70 percent`) |
| stored_azure | 88 | 0 | 1(Z kp4 `Sees.`) |
| machine_kp_pos / neg | 1,130 / 3,057 | 0 / 0 | 11(1語KPのCMU同音: acknowledgment/acknowledgement, stakes/steaks, pairing/paring 等)/ 0 |
| machine_body_pos / neg | 2,099 / 3,745 | 0 / 0 | 4(`60 percent`/`60 %`・`68th`/`sixty eighth`)/ 0 |
| fixture | 11 | 0 | 6(twenty first/21st, sixty eighth/68th, 60 %, seize/sees, wait/weight, one/won) |
- **負例は0件が新規合格**(KP 3,057・本文3,745)。`seize`/`cease`、`lead`/`led`、`desert`/`dessert`、`are`/`or`、`take part`/`take tart`はfixtureでNGのまま。
- Family: A/B/C/X/Z共通のValidator関数の修正のため全Familyが同じ改善を受ける(NG→PASSのみ)。保存データでNG→PASSになった実行はZ(melos kp3/kp4)4行とA/B/C(pool_n5 cafes B)1行。**Production品質Gateの緩和ではない**: 承認済み規則(複合序数正規化・同音救済)が、層間不整合/ratioゲートの先行で到達できなかった不具合の是正。
- test: `er109_bfix_test_01.py` 15件PASS。

## 2. 敵対的負例(P-05。`adversarial_negatives_02_aho02.json`、`er109_adversarial_negatives_01.py`)
旧負例生成器は『stress除去後の全variantで交わらない語』を置換先にしており、er109自身の判定基準と循環していた。新方式は**逆にCMU全体(124,082語)から、stress除去・any-variantでは交わるが代表強勢読みが異なる(=非代表variant・弱形・stress差・同形異音語でしか交わらない)語対**を全数列挙する。
| 負例の系統 | 件数 | 旧v0の誤同値(サンプル) | 是正後v1の誤同値 |
|---|---|---|---|
| 語対 adversarial(stress差のみ2,330/同形異音語+非代表variant 3,232ほか。全5,622) | 全数 | 6,000組サンプル中635のadversarialのうち**631が誤同値**(stress差267・同形異音語359ほか) | **0**(例外なし。弱形・stress差・同形異音語の同値は全て非同値) |
| 2語oronym(任意語を2語へ音素分割) | 22,380(3,000語) | 300語サンプルで新規経路の誤同値12 | 新規経路の誤同値**0**(承認済み既存ルートer094/despacedで同値になる16,657は既存判定そのもの) |
| 数のoronym(`for tea`/`40`型) | 2,766 | - | 数詞語彙以外を含む誤同値**0**。同値315は全語が数詞語彙(とその厳密同音語)のみで音素列が同一の真の同音(`third e fore`↔`34`型)、29は数詞1語の真の同音(to/too/two, for/four, won/one, ate/eight 等) |
| 曖昧略語・大文字略語 | 24ケース + 50,036対 | `St./Dr./Mt./#`の誤展開すべて同値、TV↔television、大文字略語×同音語4,580対が誤同値 | 曖昧略語は全てfail-closed、TV↔televisionは非同値、大文字略語×同音語の誤同値**0**。同値は`Mr.`↔mister・`OK`↔okay(閉じた表の正規展開)のみ |
- 是正後の残存同値4対(corp↔corporation, ltd↔limited, mrs↔misses[双方向])は**閉じた略語表の単一展開**(曖昧でない)で意図どおり。分類=真の同音(略語の正規展開)。ユーザー採用判断§5(5)の対象。
- **旧v0の欠陥の開示**: v0は(a)アポストロフィを除去した表層keyで`we're`==`were`/`I'll`==`ill`を『表層一致』にしていた (b)弱形・stress・同形異音語・曖昧略語・tv→televisionを同値にしていた。委任_01の『新規誤同値0』は循環する負例によるもので、安全性の証拠として弱かった(Opus指摘どおり)。本是正で解消。
- 取りこぼし(正例=代表強勢読みが一致する通常の同音語50,376対のうち同値47,872=95.0%): canonicalが同形異音語2,196(4.4%、P-03で意図的)、単一文字token160(`tea`↔`T`型、意図的)、CMU未登録148。

## 3. 正例の再測定(`machine_pairs_eval_02_aho02.json`、旧=`machine_pairs_eval_01.json`)
| 母集団 | 正例n | 既存判定(B修正後) | er109 v1(旧v0) | 合算(union) |
|---|---|---|---|---|
| KP | 1,130 | 1,033(91.4%) | **1,075(95.1%)**(旧1,128=100%) | 1,122(99.3%) |
| 本文 | 2,099 | 1,776(84.6%) | **1,990(94.8%)**(旧2,083=99.2%) | 2,069(98.6%) |
負例(KP 3,057・本文 3,745): 既存の誤PASS 0、er109の誤同値 0、新規誤PASS 0。同値率低下の主因は`cmu_homophone_swap`(同形異音語)・`contraction_contract`/`hyphen_to_space`の一部・`$eighty five`型の生成器由来。パターン149件(`PATTERN_CATALOG_02.md`、probe=`pattern_probe_02_aho02.json`): 正例114のうちer109 97(旧107)、負例35の誤同値0、分類 A=67・B(修正済)=5・B/C境界=3・C=19・C-KP=14・D=36・E=5。

## 4. 保存データ全件ON/OFF(`stored_onoff_compare_02.json`、`er109_stored_onoff_compare_01.py`)
保存`*tts_generation_results*.json`の全attempt行4,879(+Azure転写225=5,104判定、distinct 2,314)を、OFF=現行Production判定(B修正後)、ON=OFFに加えer109同値を許すモデル(非KPは最終ゲートを丸ごとskipせず、値DIFF/否定差が同値spanで説明できる場合だけ解除=P-06。説明できず解除されなかった件数=0)で比較。
- **PASS→NG: 0件**。OFF合格3,831→ON合格3,850(+19)。
- NG→PASS 19行(distinct 13組・15 segment、HR/STOPPED到達 3 segment)。Family別: **X 10行(5組)**、**A/B/C 9行(8組)**、Z 0行(Zの`seize`/`sees`はB修正で既に救済済み)。内訳: `Pump 1's fist`(Azure、X coffee kp1 4行)、`Act 1 was 20%`(X hormuz 3行)、`point to`↔`Point 2.`/`brace oneself for`↔`Brace oneself 4.`(to/2, for/4。X 3行)、A/B/C 9行: `study's`↔`studies`型の同音(2行)・複合語spacing+同音/数(4行)・`third places`↔`third place is`(er094経路、2行)・`“slow”`の引用符+数(1行)。一覧は`new_pass_listen_list_02.json`。
- **ローカルWhisper再転写(API 0、保存wav10本)**: 6本はWhisperも期待文と同値/合格(pump one's fist 4本・brace oneself for・A/B/C `slow` 1本)。**4本はWhisper転写自体が期待文と同値でない**: `point to`の1本は Whisper=`Hold on.`(**裏付けなし**、Primary `Point 2.`のみ。KPならP単独=票は割れる)、hormuz `Act 1 was 20%`の3本はWhisper転写が`10.16`/`straits`/`numbers`等で別の差を持つ(er109が同値とした`Act 1`等のspanは一致しているが、Whisper自身のITN差でWhisper判定は不合格)。wav無し(古い実行で音声が残っていない)のA/B/C 8行と X 1行(`point to`の別attempt)は再転写不可。
- 試聴リスト: `user_test/aho_new_pass_listen_01/index.html`(B修正由来5行+er109由来19行=24行、wavありの14本を再生可能。ローカル再生検証14/14=`pages_play_evidence_local_02.json`)。

## 5. ユーザー指摘NG音声(`known_ng_recheck_02.json`、`er109_known_ng_recheck_01.py`)
- 問題音声21件(take_part_problem_13 + er091 problem 8)の転写45件: **新規PASS 0**。take part A(正常)・byUs presumed_normal 7・ng3 12 を含む203転写で新規PASSは`ng3_case`の`Pump 1's fist.`(Azure、本来の偽NG)7件のみ。
- 固定既知NG18対(`take part`/`Take Tart.`・`take apart`、`Melos`/`Mellows`・`Mello`・`Melo`、`blurt`/`Blur.`、`think up`/`Think.` ほか): **新規PASS 0**(er109同値は`take part`/`Take Part?`の1対のみ=既存でも合格の表記違い)。

## 6. 回帰(`work/regression_run.log`・`regression_summary.json`)
`run_project_regression.py`(unittest discovery `er0*_test_*.py`): collected 6,882 / passed 6,844 / failed 15 / errors 17 / skipped 6。失敗32件はすべて自分の変更と無関係な既存分(前委任KPQ evidenceの既知リスト: er003_test_bad・er003_test_p2j[件数突合]・er008 pricing・er012 TtsMode・er015/069/070/074 import・er020 RegressionCorpus・er025・er026 MockFullPipeline・er040/043・er053・er064 kp_int/opt・er066/068・er073、及び未commit差分を検出するer064 ProductionUnchanged)。**自分起因の新規失敗は3件を検出し是正済み**: `er094 StaticChecks.test_only_val_imports_er094`(er109がer094を直接importしていた→val保持のmoduleを再利用に変更)、`er078 ja_wiring test_new_ja_label_is_not_embedded`・`er104 wiring test_er104_core_is_imported_only`(er109_*研究scriptを許可リストに追加)。是正後、pytest群(er078/er103/er104/er105/er106/er108) 856 passed、er094・er109・bfix testはPASS。
新規test: `er109_asr_orthographic_equivalence_01_test.py` 28件、`er109_bfix_test_01.py` 15件。**DefaultOffIsolation**: flag既定OFF・読取は`is_enabled()`のみ・Production既存fileからのimport 0(AST)・通信/ファイル書込なし(ソース固定)・valにer109の記述なし(test `ProductionIsolation`)。
- **未確認/未実施**: 全Familyの実音声生成(ユーザー指示=保存音声・ローカル処理のみ)。Whisper small以外のモデル。

## 7. F6(Opus十分条件)の充足
1. P-01〜P-07適用+正例再測定: 済(§3)。2. CMU全体の敵対的負例で新規誤同値0: 済(§2、閉じた略語表の単一展開4対を除く)。3. 保存全件ON/OFF、PASS→NG 0、NG→PASS全件列挙(A/B/C分離): 済(§4)。4. 新規PASS保存wavのローカルWhisper再転写: 済(10本、6本一致/4本不一致を開示)。5. ユーザー指摘NG音声で新規PASS 0: 済(§5)。6. 全回帰+DefaultOffIsolation: 済(§6、自分起因の新規失敗は是正)。7. 試聴リスト: 済(§4)。
