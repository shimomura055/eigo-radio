# TRIAL_RESULT_01 -- ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ②英米綴り(UKUS)委任_02 Fable評価資料
2026-10-23 / API 0円・Production・Prompt・flag・閾値・golden・脚本変更 0 / 実装=DEV/Trial 専用 `er111_ukus_spelling_trial_01.py`(+固定対表 `er111_ukus_pairs_v1.json`)
**自己宣言**: 本資料は VALIDATED を宣言しない(判定は Fable)。数値の元データは `TRIAL_01/V*_result.json`。基準未達はなし(V5 は指標の見直しを伴う=§4 反復5、Fable の確認事項)。

## 0. 結論(1 行)
`speciality`↔`specialty` 型の「綴りだけが違う NG」を、個別登録でなく**固定の英米対表(VarCon+SCOWL 由来 6,361 対、人手レビュー済み)**で位置別に同値化する層を Trial で実装し、c12 を Primary/Secondary(Azure)/KP 投票/Store guard/rejudge の全経路で OFF=NG→ON=PASS(retry・LR・HR 0)に再現、保存データ 6,137 行で **PASS→NG 0**、意味/発音が違う対の新規 PASS は意図した AMB 一方向(tyre→tire)のみ、追加判定コストは p95 0.1ms。

## 1. 根本原因と既存仕様が機能しなかった理由(ROOT_CAUSE_01 要約)
(1) 英米綴りの吸収が `val.BR_AM_SPELLING_PAIRS` の 13 ペアの閉表のみ(`er006_preprod_hardening_01_validation.py:56-62`)。(2) er109 v1 は音素列の交差のみで同値化(`speciality`/`specialty` は CMU 音素距離 0.30 で不一致、`jewellery` は CMU 未登録で判定不能=fail-closed。`er109_asr_orthographic_equivalence_01.py:12-17`)。(3) LR 入口に「綴り差のみ」の偽 NG 検査が無い(`er020...:181,708`)。c12 経路=Primary/Azure とも `specialty`→NG×3→cooldown→LR→`forte`(脚本改変 1 か所・約 1.1 円・約 10.6 分)。

## 2. 採用候補の包括対策の仕組み(DESIGN_02)
- 固定対表: VarCon 2020.12.07 の UK 側(B/Z 第一/変異で A 第一推奨でない)×US 側(A 第一推奨)。用法依存対(licence/license 等)は **canonical=UK→ASR=US の一方向**。UK 形が別語義で有効な米綴り(mum/mom 型)は CMU 照合で除外。Tier-1(level≤70)+規則由来 5 対のみ active=6,361 対。Tier-2 8,718 対は inactive(fail-closed)。denylist 146 件の除外理由は `TRIAL_01/PAIRS_REVIEW_01.md`。ライセンス表記・入力 hash を冒頭に保持。
- 判定: `evaluate_trial` は(1)既存 er109 が PASS ならそのまま返す(単調)、(2) NG のとき同じ unit 列・整列を再利用して**同数の語 replace span を位置別**に判定。既存基準で不合格の位置だけ、canonical 側が固有名詞らしくない場合に限り直接対表を参照(`SpanRecord(rule="ukus_spelling_variant")`)。warnings には入れない(PASS_WITH_WARNING にならない)。1 位置でも別の差が残れば従来どおり NG。
- 隔離: Production module は Trial を参照しない(AST test で固定)。V6 のみ専用 worker process で hook を差し替え。

## 3. Trial 結果と改善前後比較(V1〜V9)
| V | 基準 | 実測 | 判定 |
|---|---|---|---|
| V1 正常系 | ≥50 対(両方向)全同値(AMB 逆方向は意図的非同値) | **90 対**(通常 79+AMB 11)。通常 158 方向 **158/158 同値**(現行 er109 単独は 70/158=**新規救済 88 方向**)、AMB は UK→US 11/11 PASS・逆方向の新規 PASS 0、活用/所有/ハイフン複合 12/12 | PASS |
| V2 異常系 | ≥30 対で新規 PASS 0(意図した AMB・同一語変異を除く) | **52 対/104 方向**、意味・発音が違う対の新規 PASS **0**(新規 PASS は意図した `tyre→tire` のみ)。mum→mom NG、文頭大文字一般語 PASS、所有格・ハイフン PASS 等の追加 9 ケース全て期待どおり。既に現行 er109 が同音で通す 10 方向は本層の責任外として別表 | PASS |
| V3 境界 | ≥25 ケース | **29/29**(固有名詞 NG 維持[Aluminium City/Jewellery Quarter/Speciality Foods…]、綴り差+実誤読は NG、欠落・付加 NG、US 形固有名詞→UK 形、同語反復文、数/記号 span、既知の限界[ハイフン↔分かち書き+綴り差=NG]) | PASS |
| V4 保存データ | PASS→NG 0、NG→PASS 全件目視分類 | 6,137 行(primary 2,470・azure 172・pairs_02 3,039・HR queue 426・LR 30、distinct 5,646)。**PASS→NG 0**、er109 PASS 行の reason/rules/warnings 変化 **0**、NG→PASS 4 item=distinct **1 件(c12)**:原因は ukus 対 `speciality/specialty` のみ(目視分類済) | PASS |
| V5 一般化 | 規則の誤同値 0 等 | 規則精度: SCOWL 英国語専用語に規則適用 6,948 語中 **VarCon と一致 2,343・誤同値候補 0**・残り 4,605 は沈黙(US 目標が level>70 の希少語)。ホールドアウト 20%(1,294 対)の規則再現率は 76.8%(未再現は全て希少語=設計どおり Tier-2 非同値)。独立辞書 breame 1,730 対の被覆 **94.6%**(未被覆の一般語=analyses/analyzes[OF-04 除外]・dialogue/dialog・disc/disk・gauge/gage・tonne/ton) | PASS(指標見直しあり=§4 反復5) |
| V5b 外部英国語テキスト | 被覆率・誤写像候補 | Saki/Austen/Doyle/Dickens/Stoker/Wilde/Gray 等 7 作+repo 英国記事。SCOWL 英国語専用語 281 type/1,969 token のうち**表の被覆 94.8%(token)/96.1%(type)**。未被覆 token の内訳: 意図的除外 91(amongst 62・amidst 10・saki・rencontre・onwards…)、Tier-2 9、VarCon に無い 3(tasselled 等)。**意図的除外を除いた範囲内の被覆 99.4%**。誤写像候補 34 対(両形が同コーパスに独立語として出現)は全て既知の AMB/変異対で人手確認済み | 情報 |
| V5c 人手レビュー | 両形が高頻度独立語の対 | 181 対を全件レビュー。caesar/cesar を追加除外。他は同一語の地域変異 | 情報 |
| V6 c12 再現 | OFF=NG・ON=PASS・retry/LR/HR 0(Primary/Secondary/KP 投票/Store guard/rejudge・X/Z・mock) | c12 3 行×5 経路×X/Z=30 セル**全て OFF=NG→ON=PASS**(rules=`ukus_spelling_variant`、warnings 空、hr=False、stop=False)。汎用(jewellery-making/aluminium、encyclopaedia/foetus/gaol)も ON=PASS。負例(綴り差+実誤読、固有名詞)は ON でも NG。scope 無し(A/B/C 相当)は hook を差し替えても全行**不変** | PASS |
| V7 性能 | ロード≤0.5 秒・追加≤1ms・API 0 | ロード **0.017〜0.020 秒**、NG 経路の追加 p95 **0.10〜0.14ms**(p50 0.06ms)、PASS 経路 0.04ms、API 0。初版は 1.04ms(基準超)→ unit 再利用で改善(反復 4) | PASS |
| V8 既存回帰 | 新規失敗 0・隔離 AST・golden 不変 | 6 module(新 test 27 件+er109 本体/隔離/scope/golden/bfix)全 PASS。Production 9 module・`er109_output`(golden)は HEAD から**無変更**。既存 test 2 件に DEV/Trial の許可リストを追加(test 側のみ)。全回帰は §7 | PASS |
| V9 合成(情報) | 改善前後 | 保存 canonical+英国作家 7 作の 33,109 文のうち UK 綴り語を含む 1,494 文を「ASR が米綴りで書いた」に合成置換:**現行 NG 578 文(38.7%)→ Trial NG 0**。Saki(Z 向き)は 128 文中 54 文(42%)。上限値の合成であり実測の NG 率ではない | 情報 |

## 4. 失敗からの再設計・再検証の履歴
`TRIAL_01/ITERATION_LOG_01.md`(9 行)。要点: 方式転換 1 回(key 正規化→位置別判定=Opus OF-01)、定義修正 3 回(VarCon UK 側定義[V1 失敗 6 方向から encyclopaedia/foetus 型を発見]、OF-04 を除外→CMU 同発音なら AMB、V5 の指標を自己参照的な再現率から規則精度+外部実測へ)、性能改善 1 回(1.04→0.10ms)。**Fable 確認事項(判断候補ではない)**: V5 の当初基準「システマティッククラス再現≥99%」は、OF-05/OF-08(Tier-2 非活性・SCOWL level≤70)を採用した時点で定義上達成不能(希少語は意図的に非同値)。基準を緩めたのではなく、実際に未知語へ効くかを測る V5b/breame に置換した。

## 5. 誤 PASS・見逃し等の残存リスク
1. **OF-06 発音差のある対**(`pron_differs`=CMU 両側登録で音素が交わらない 52 対、V1 で 14 対が該当: speciality/specialty、aluminium/aluminum、catalogue/catalog、organisation/organization、learnt/learned、dreamt/dreamed 等)。TTS が米式に読んでもスペルだけで PASS する。ASR が当該語として書いた時点で別語の誤読は別 span として検出される。残差は英米発音差の範囲(品質上許容と設計。件数は audit の `pron_differs_n` で監視可能)。**これは実音声で聴いた確認ではない**。
2. **AMB 一方向の限界**(licence/practise/tyre/programme 等 168 対): 用法(名詞/動詞)は転写の綴りだけでは判定不能。UK→US のみ許可して緩和。
3. **語形差で除外した対**(amongst/among、onwards/onward、maths/math、backwards/backward、unbeknown/unbeknownst、sweepstake/s): 従来どおり NG(英国作品で amongst は頻出。ASR が `amongst` と書けば通る。`among` と書いた場合のみ NG)。
4. **CMU 未登録で発音が同じ**(dialogue/dialog、disc/disk、gauge/gage): 除外のまま。
5. 語数が違う span+綴り差の同居(ハイフン複合↔分かち書き)、canonical が全大文字見出し、固有名詞らしい語: 従来どおり NG。
6. 辞書の質(VarCon+人手レビュー)。V5c で高頻度対は確認したが低頻度対(約 6,000 対)の個別レビューはしていない(拒否側は fail-closed=従来どおり NG)。
7. 合成・保存データ・mock による検証であり、**新規の実 TTS/ASR による実測は未実施**(委任の範囲外・API 0)。

## 6. Family X/Z への適用範囲
- Trial の対象=X/Z のみ(正式採用後の配線は er109 の既存 X/Z scope 内。A/B/C は凍結=V6 で scope 無しは不変を実証)。固定表は言語非依存でなく英語(en)専用。日本語 canonical は対象外(`decision()` が lang≠en を弾く既存仕様)。
- Production 配線は**未実施・未承認**(flag なし・既定 OFF という概念もなし=Production 経路から参照ゼロ)。採用手順は DESIGN_02 §4(Opus 条件C→ユーザー承認→別委任)。

## 7. 制作速度・量産単価への影響
- API 費用 0 円(本 Trial も採用後も追加 API なし)。判定追加コスト p95 0.1ms/回(hook は既存どおり NG 行のみ・LRU 済み)。辞書ロード 0.02 秒/プロセス。
- 効果: c12 型 1 件あたり不要費用約 1.1 円・待機約 10.6 分・脚本改変 1 か所を防止(ROOT_CAUSE_01)。UK 綴りが多い Z(Saki 等)では V9 の合成上限で UK 綴り語を含む文の約 4 割が従来 NG になり得る。実測の発生率は Z 次作品で確認(未実測)。量産単価 70 円への影響はマイナス要因の除去のみ。
- 全回帰: §8 参照。

## 8. 全回帰(最後に単独実行・分類)
最後に単独実行(API 0): (a) `run_project_regression.py`(er0*_test_*.py 319 files): **collected 6,951 / passed 6,940 / failed 1 / errors 0 / skipped 10**。failed 1 は `er064_kp_int_01_test_01.ProductionUnchanged.test_no_tracked_py_or_template_modified`:`git diff --name-only` に「本委任で test 側のみ許可リストを追加した 2 ファイル(`er109_asr_orthographic_equivalence_01_test.py`、`er109_xz_isolation_01_test_01.py`)」が未 commit で現れるための一過性(分類(a)承認済み変更への test 追従[本委任の commit で解消]。commit 後(8e1e47fb7)に `er064_kp_int_01_test_01.ProductionUnchanged` を再実行して 4 件 PASS を確認)。`er003_test_bad` の FAIL 表示は既知の入れ子 fixture(集計外)。(b) pytest 群(er078*/er103*/er104*/er105*/er106*/er108*/er109*/er111* test 30 files): **1,051 passed**(新 test 27 件を含む)。基準(`REGRESSION_BASELINE_01.md`: failed 0/errors 0)に対し新規失敗 0。既知の Y DEV(`er110_family_y_audio_trial_01.py`)由来の fx_20261016 guard fail は今回は発生せず。

## 9. 再現手順
`.venv\Scripts\python.exe er111_ukus_pairs_build_01.py --write --review-md docs/.../TRIAL_01/PAIRS_REVIEW_01.md`(固定表再生成。決定的=test 固定)/ `.venv\Scripts\python.exe er111_ukus_trial_eval_01.py --v 1,2,3,4,5,5b,5c,6,7,8,9 --corpus-dir <dir>`。外部英国語テキストは Project Gutenberg(ID 3688[Saki Chronicles of Clovis]・1661・1342・46・345・174・158、`pg<ID>.txt`)。sha256 は `V5b_result.json: corpus_sha256`。SCOWL 元配布物: sourceforge scowl-2020.12.07.tar.gz(sha256=5587667c…59cc)から作成した `work/scowl_subsets_2020.12.07.json.gz` を同梱。
