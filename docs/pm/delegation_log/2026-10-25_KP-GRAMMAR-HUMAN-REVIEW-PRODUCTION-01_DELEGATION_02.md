管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_02(Opus条件Aレビュー反映→DESIGN_02→KP側実装・単体test。**有料API呼出0・Production runの実行0**。runtime evidence(R1〜R4)は本委任では実行しない=翌日JST 10/26以降の別委任)。

## 0. 最初に読むもの
- `docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(本案件の節。他タスクの節は消さない)
- `docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/{EXISTING_SPEC_CHECK_01,DESIGN_01,OPUS_REVIEW_REQUEST_01,TEST_PLAN_01,BUDGET_PLAN_01}.md`
- ユーザー指示原文 `docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_USER.md`
- 委任_01逐語 `docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_DELEGATION_01.md`

## 1. Opusレビュー結果(逐語。まず `docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/OPUS_REVIEW_01.md` に以下を無改変で保存すること)
<<<OPUS_REVIEW_BEGIN
## KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 Opus独立レビュー(条件A、DESIGN_01、読み取りのみ)

### 結論
**修正後に実装着手可(条件付き可)。**
大枠は妥当です。具体的には次の点です。
- 下流の接続面(後工程が読むファイル)は変えない
- Human確定を1つの正本ファイルにまとめる
- 宣言がなければ待機する
- 共有関数`sc.run_key_phrases`は変更しない
- 文法は分離する

ただし、NG候補の復活や古いKPの混入につながる経路が既存コード側に数本残っています。下記M-1〜M-9をDESIGN_02に反映してから実装に入ってください。Production採用の可否は判断していません。

### 必須修正(M)

**M-1 候補生成用の作業dirを分ける(O-1/O-4)**
- 問題: `run_key_phrase_canonicalization`は`{out_dir}/keywords_canonicalized.json`へ直接書き込みます(`er003_v1_n3_01_scaffold_generate.py:551-552`)。外側retryの退避処理(`_kp_retire_stale_artifact`:659)も同じ名前のファイルを操作します。候補生成で`kp_dir`をそのまま渡すと、Human確定前に8件入りの「後工程が読むファイル」ができてしまいます。X `--stage tts`の単独起動、Z `install_kp_assets`、`_load_gloss_hr_resume`(:1510)がこのファイルを読みます。
- 修正案: 候補生成は`<kp_dir>/kp_candidates/round_<n>/`のような専用dirで実行します。`<kp_dir>/keywords_canonicalized.json`を書けるのはfinalizeだけ、という不変条件にします。
- test: 候補生成直後に`kp_dir/keywords_canonicalized.json`が存在しないこと。

**M-2 Z gloss HR snapshotからの古いKPの復元を塞ぐ(O-1、NG復活経路)**
- 問題: `_load_gloss_hr_resume`(`er026…:1499-1514`)は本文shaが一致するだけでsnapshotの`res`を復元します。しかも`run_kp_stage`より前に呼ばれます(:1709)。確定後の人称修復に失敗してHR停止し、その後Humanが`reselect`や`select`で選び直した場合、再実行で旧選定(NG句を含みうる)が復元されます。
- 修正案: snapshotに`selection_signature`を含めます。不一致なら破棄(退避)します。select/reselectのCLIでも、未消費のsnapshotを失効させます。
- test: HR停止 → reselect(NG付与) → 再実行で、旧snapshotが使われないこと。

**M-3 Z `kp_<lv>`の来歴にHuman確定を含める(O-4)**
- 問題: `ensure_stage`はinput_sha(本文のみ)と出力shaの一致だけで再利用します(`er062…:702-712`)。そのため、`kp_<lv>_result.json`を書き換えない確定変更(事後Review、AUTO→REVIEWEDなど)では古いresultがそのまま再利用されます。
- 加えて、`_gloss_person_gate`→`_result_gloss_diff`/`_sync_kp_result`(:1590-1640)は**rankをキーに**gloss関連フィールドを同期します。確定集合が変わると、別の句のglossが移植されます(句とglossの取り違え)。
- 修正案:
  - (a) input_shaを`sha(text_sha|selection_signature)`にします。
  - (b) `--regenerate-stage kp_<lv>`は、DESIGN案の「確定済みならSTOP」ではなく「**現在のreviewからの再finalize(再選定なし)+子孫stale化**」と定義します。再選定は`reselect` CLIだけで行います。これなら既存の運用手順(`CURRENT_SPEC.md:2052`)や、既存STOP文言の「--regenerate-stage kp_*」案内(`_gloss_unevaluated_stop_message`:1517、`er026_family_z_src_posthoc_01.py:173`)も安全に生き残ります。どちらの文言も「再選定」の意味は外すよう修正します。
  - (c) `_sync_kp_result`/`_result_gloss_diff`の照合キーを`candidate_id`(ない場合はused_form)に変えるか、selection_signatureの一致を前提条件にします。
  - O-5論点(12)への回答: STOPより再finalizeの方が副作用は小さいです。

**M-4 X再開時にsupport(有料)を再生成させない(O-4/O-7)**
- 問題: Xの`--stage scaffold`/`all`は、各レベルでsupport生成(有料LLM)を行ってからKPに入ります(`er019…runner_01.py:656-665`)。rc=4待機の後に同じコマンドで再開すると、supportが再生成されて費用がかかり、文面も変わります。DESIGNでは`--scaffold-only kp`を再開経路として想定していますが、通常の`scaffold`/`all`で再開した場合の動作が規定されていません。
- 修正案: review/候補ファイルが有効なら、通常の`scaffold`/`all`は「support保存済み+sha一致ならsupport生成をskipし、KPはfinalizeのみ」、それ以外はSTOP、のどちらかに固定します。rc=4のメッセージには正確な再開コマンドを1つだけ出します。X Part 1の生成(scaffold内、b1bのKP PASS後)はfinalize後だけにします。
- test: mockのAPIカウンタで、再開時のsupport・選定呼出がともに0であること。

**M-5 NG registryの保存単位をrunではなく記事にする(O-1)**
- 問題: Xの`article_id`は`FAMILY_X_AUDIO_{basename(out_dir)}_{level}`(:662)で、run dir名を含みます。DESIGNの「記事ID単位で保持」をこのIDで実装すると、新しいrun dirで再生成したときにNGが消えます。この案件では`_01/_02`のようにrun dirを分けて作り直す運用が常態なので、「regenerationで復活させない」に反します。
- 修正案: registryは`family+slug+level`をキーとし、run dirの外にある共有storeに置きます。run内にはその参照とコピーを残します。
- test: 別のrun dirでも同じNGが除外されること。

**M-6 不在宣言の有効範囲を限定する(O-1/O-7、「不在宣言」と「Human未確認」の取り違え)**
- 問題: `declare-absent`はrun dirに`kp_review_mode.json`を書きます。このため、Humanが戻って`reselect`した後の新しい候補(`round`+1)まで、Humanが見ないままAUTO確定されます。
- 修正案: 宣言を`candidates_sha256`(またはround)に結びつけます。Humanの操作(select/reselect/ng)があった時点で、以後のroundについては宣言を失効させます。宣言には`declared_by`と出所を必須で記録します。AI(Fable)が宣言する場合は、ユーザー発言の参照を必須にするよう推奨します。これがないと「AIが不在とみなした」ことが誤った自動確定の新しい経路になります。
- test: 宣言 → reselect → 新roundが`PENDING_REVIEW`になること。

**M-7 候補段階での除外の具体化(O-2)。品質を実質的に緩めないための条件**
- item単位で除外すること自体は、各Gateの合否判定を変えない限り緩和にはあたりません。除外された句は旧方式でも採用されず、旧方式で再選定して出てくる代替句とrank 4〜8の句は同じ性質だからです。ただし実装上、次の3点が必須です。
- (a) canonicalizationのINVALIDは**応答全体の状態**で、INVALIDのときはmergeされません(:519-521)。INVALID応答から合格分だけを拾う方式は、承認済みGateの受理条件の変更になります。修正案: `item_reasons`のあるitemを除外し、**残りのitemでcanonicalizationを再実行して全体PASSの応答だけを受理**します。item別の理由がない構造不正は、既存のgate retryに任せます。
- (b) SRC D1(`srcz.gate`)は1件でも曖昧なら全体STOPし、rankで処理します(`er026_family_z_src_posthoc_01.py:161-182`)。候補段階では`apply_to_kp`のreportを候補単位に写し、該当句は`dropped(stage=src_d1)`とします。人称整合の修復(Zの`_gloss_person_gate`相当)も候補段階で候補ごとに適用し、修復できなければ`gloss_hr_pending`旗を付けます。DESIGN a-2の順序表に人称整合が入っていないので追加してください。
- (c) retryの発動条件を一意にしてください。現案は「目標数未満ならretry」と「shortfallは1件以上で許容」が混ざっています。推奨は「**KPにAUTO採用できる有効件数が3未満、かつGateによる除外が発生した場合だけ外側retry**。retryは候補list全体を置き換え、round内でのmergeはしない。vocabの4〜5件目の不足はshortfallとして受容(数合わせのretryはしない)」です。

**M-8 Redundancy QAを確定集合にも再適用する(O-2)**
- 問題: 承認済みのGateは「採用集合の相互重複判定」です。8件・28ペアの一括判定はPromptの想定(5件)から外れた入力条件で、品質は未検証です。それを部分集合へ流用すると、適用対象が実質的に変わります。
- 修正案: 候補全体への1回の判定は、提示用の旗として残します。それとは別に、finalizeでKP集合(Advはvocab集合も)を対象にRedundancy QAを1回実行します。費用は約0.02〜0.1円/レベルです。NGの場合、AUTOは次の候補へ繰り上げて再判定し、Humanは選び直しになります。

**M-9 `part1_items`のfallbackを旧runだけに限定する(O-5)**
- 問題: `vocab_confirmed.json`がない場合に`keywords_canonicalized.json`(3件)へ黙って戻る設計では、新方式のrunで生成漏れが起きても3件で公開されてしまいます(仕様違反が表に出ない)。
- 修正案: fallbackは`kp_human_review.json`が存在しない旧runに限ります。reviewが存在するなら`vocab_confirmed.json`を必須にします(fail-closed)。
- あわせて、`require_final_consistent`で`vocab_confirmed.json`の各itemにも既存の消費側検査を適用します: `collect_unresolved`、`select_consumer_unevaluated`、Z SRCの`has_contract`。追加2件が既存Gateの対象から外れないことは、この検査で担保します。
- Part 1・T1・`translations_by_rank`はrankで結合しています。vocabのrankとKPのrankは一致しないので、KP側のrankで他ファイルと結合しないことをtestで固定してください(Z `_stage_kp_part1(ctx, prov, items)`(:1784)は現状KPのitemsを渡しています)。

### 推奨(R)
- **R-1 Prompt 2-Rへの代替案(O-3、Opusとしてはこちらを推奨)**: Prompt 2は無変更のまま1 call目で上位3件(=現行の承認済み挙動そのもの)を取り、2 call目の新しいPromptで「前記3件を除き最大5件を順位付き+理由」を取る構成です。
  - 利点: AUTOのKP結果が承認済みの選定と同一になるので、上位3件の品質同等性の検証が不要になります。Prompt 2のshaも不変で、I-2の論点そのものが消えます。
  - 欠点: 費用は+約0.05円/レベル、時間は数秒増えます。1〜3位と4〜8位の間で順位の一貫性は弱くなりますが、1〜3位は常に上位として扱われるので実害は小さいです。
  - 2-Rを採る場合: E-0の1サンプル比較はLLMの揺らぎと区別できないので不十分です。各記事で旧P2と2-Rをそれぞれ3回ずつ実行し、「旧と旧」の重なりを基準に「旧と新」の重なりを比べます。(指標・基準・費用約5〜15円)
  - `reason_ja`はschema上`phrase`の後ろに置きます。
- **R-2 NG照合の強化**: `used_form_key`は所有格代名詞(one's/your/his/her/their/my)を同じプレースホルダへ正規化。NG句を含む/含まれる句は`similar_to_ng`旗を付けAUTO対象外・Human選択可。NGの解除は`unng`(理由・記録必須)だけ。
- **R-3 同時実行の制御**: `kp_human_review.json`の更新は排他ロックファイル(O_EXCL)+版番号比較更新(`revision`+`candidates_sha256`)+`os.replace`原子書換。runnerのfinalizeも同じロック。test: CLIとrunnerの同時実行で一方が拒否されること。
- **R-4 RESTART_STORMとの関係**: 「起動→rc=4→reselect→起動→rc=4→select→起動」が5分以内なら3起動で自動停止(`PM_GOVERNANCE.md:3496`)。安全機構は緩めず運用手順で間隔を明記、testで発火条件確認。Xで同機構が効くかは未確認。
- **R-5 公開後の事後Review**: `published_selection_signature`を別保存し、一致検証の比較対象を「公開版」と「確定版」に分ける。
- **R-6 `--accept-ai`**: REVIEWED扱いで妥当。表示した`candidates_sha256`を記録し、未表示候補へのaccept-aiは拒否。
- **R-7 宣言の手間を減らす(O-7)**: 期限による自動切替を採らない判断に同意。ユーザーが出す期限付き不在宣言(`declare-absent --until <日時> --scope <family/日付>`)を用意すると9記事/日でも1日1操作。明示宣言なので設計方針と矛盾しない。

### 問題なし確認(C)
- C-1: 3値判定・REVIEWED/UNREVIEWED_AUTO_ADOPTED区別・降格遷移なしは妥当(M-6前提)。
- C-2: REVIEW_REQUIRED(qa_fail)を「AUTO対象外・Human明示で採用可」は承認済み3状態モデル・OPEN-504是正と整合。
- C-3: 外側retry再利用は整合(M-1前提)。
- C-4: `read_mode_declaration()`単一読取点・DefaultOffIsolation型testは妥当。Zの`ctx.hooks`にmodeを載せられないこともassertに加える。
- C-5: er104 KP 3-ASR voteは差分のみ影響。中身未精査、回帰testで担保。
- C-6(O-6): 共通核kind非依存・grammar層は実装しない(fixture testのみ)は妥当。TOP 2は代替案で「2件目ロジック廃止」と矛盾しない。Yは未整備としてOPEN-484(g)で追跡、PRODUCTION_WIREDにしない。(g)に「NG registryと`part1_items`もY入口で共有すること」を追記。

### Fable暫定判断への意見
- G-1・I-1・G-2: 異議なし。
- I-2: R-1(2 call構成)を推奨。2-Rを採るならE-0を反復サンプリング版に拡充。
- 再選定上限2回/レベル/run: 妥当。
- 確定済みZ `--regenerate-stage kp_*`をSTOPにする案: M-3(b)の再finalize化への変更を推奨。
- item単位除外: M-7の3条件つきで可。

### TEST_PLAN・BUDGETへの追加
- 追加test: 候補dir分離(M-1)/snapshot旧選定復元防止(M-2)/rankキー同期の句・gloss取り違え(M-3)/X再開時の有料API 0回(M-4)/別runでのNG保持(M-5)/宣言失効(M-6)/canonicalization INVALID時の部分集合再実行(M-7a)/確定集合へのRedundancy QA(M-8)/`vocab_confirmed`欠落fail-closed・vocab itemへの消費側Gate適用(M-9)/ロック競合(R-3)
- evidence: R2かR4のどちらかに「前のroundでNG → 不在宣言 → AUTOでNGがskipされる」を組み込む。
- 予算: 量産単価+0.9〜2.5円/セット推定は妥当(実測で置換)。M-8とM-7aで+約0.1〜0.5円/セット。E-0はR-1を採らない場合約5〜15円。案件Cap 150円内。

### 未確認
- Part 1組立での`select_consumer_unevaluated`の適用範囲 / `srcz.apply_to_kp`を候補単位で使えるか / XにRESTART_STORMがあるか / er104の票再利用の詳細
OPUS_REVIEW_END>>>

## 2. Fable(PM)の確定判断(これに従う)
- M-1〜M-9: **すべて採用**。
- I-2/R-1: **R-1(2 call構成)を採用**。Prompt 2は無変更(sha不変)。2 call目「前記3件を除き最大5件を順位付き+理由1文(`reason_ja`は`phrase`の後)」の新Prompt(Prompt 2-V、sha固定・DEV→本件でProduction導入)。E-0は不要。
- M-3(b): 確定済み`--regenerate-stage kp_<lv>`=現在のreviewからの再finalize(再選定なし)+子孫stale化。再選定は`reselect` CLIのみ。既存STOP文言の案内も修正。
- M-6: 宣言は`candidates_sha256`(round)に結びつけ、Human操作で以後のroundは失効。`declared_by`・出所必須。AI(Fable)が宣言する場合はユーザー発言参照必須。
- R-2・R-3・R-5・R-6: 採用。R-4: 安全機構は変えず運用手順に間隔明記+test。R-7: `--until/--scope`付き宣言をCLIに用意してよい(明示宣言の一形態)。ただし既定は使わない。運用上の採否はユーザー報告事項。
- G-1: 文法(Part 2)のProduction採用は別途ユーザー承認待ち。**文法層は実装しない(共通核をkind非依存にし、grammar kindのfixture testのみ)**。
- I-1: 単語解説5件はAdvanced(b1b)のみ。G-2: 文法2位=同一文を除く次の適格(設計に記載のみ)。
- 再選定上限2回/レベル/run。`--accept-ai`=REVIEWED。
- Y: 共有関数無変更・Human Review非到達=未整備としてOPEN-484(g)で追跡(「NG registryと`part1_items`もY入口で共有」追記)。PRODUCTION_WIREDにしない。
- 既存Gate(外側retry・canonicalization・gloss再整合・CMU・Redundancy QA・SRC D1・人称整合・HR Lock・KP vote)の基準は一切変更しない。

## 3. 本委任のScope
A. `OPUS_REVIEW_01.md`保存(上記逐語)。`DESIGN_02.md`(M-1〜M-9・R採用分・Fable判断を反映。DESIGN_01との差分表付き)、`TEST_PLAN_02.md`(Opus追加test込み)、`BUDGET_PLAN_02.md`(R-1採用でE-0削除、M-7a/M-8加算、evidence R1〜R4の見積・Cap 150円)。
B. 実装(API 0): 新module `er119_kp_human_review_01.py`(衝突確認のうえ命名)に共通核(候補生成dir分離・状態機械・NG registry共有store・宣言・finalize・`part1_items`・`require_final_consistent`・`verify_selection_matches_outputs`・CLI status/show/select/reselect/ng/unng/declare-absent/--accept-ai/--from-json)、Prompt 2-V(ファイル+sha固定)、X `run_theme_scaffold`のKP呼出差替え+M-4再開規定、Z `stage_kp`差替え+M-2/M-3(a)(b)(c)、Part 1入力の`vocab_confirmed.json`化(M-9 fail-closed)。共有`sc.run_key_phrases`は無変更。
C. 単体test(mock/fixture、API 0): TEST_PLAN_02の全項目(検証7点×test、DefaultOffIsolation型=宣言なし→待機rc=4・API 0・副作用ファイル0、M-1〜M-9・R-3のtest、grammar kind fixture)。既存回帰test(er019/er026/er062/er063/er105/er109/er003系、Part 1 er003_kp_general_explanation)を実行しPASS確認。LLM/TTS呼出がtest中に0であることをカウンタで証明。
D. 運用手順書 `OPERATIONS_01.md`(Humanの操作手順、rc=4時の再開コマンド1つ、RESTART_STORM間隔、宣言の書式、`kp_human_review_request.md`の例)。
E. SSOT: OPEN-518更新(Status=IMPLEMENTED_PENDING_EVIDENCE、Opusレビュー反映済み、Production到達の有無と既定挙動[宣言なし→待機]を明記、PRODUCTION_WIREDとは書かない)、OPEN-484(g)追記、DECISION_LOGへ設計決定(R-1採用・M-3(b)再finalize化・宣言方式)を1エントリ。CURRENT_SPECは**本委任では変更しない**(runtime evidence後のPRODUCTION_WIRED時に反映)。
F. Git: 変更対象pathのみ`git add`→`git commit --only`→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`[競合は両方残しSTOP報告]→push)。`git add -A/-u`禁止、amend/rebase/force/stash/reset --hard禁止。secret grep 0件確認。commit前に`git status --porcelain`で意図外ファイル混入なしを確認。
G. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_DELEGATION_02.md`(Nは572前後。先頭が「管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_02」の行を570〜580で走査して特定。`--index -1`不可)。Opusレビュー依頼文(index 571前後、先頭「管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01。Opus必須レビュー」)も`..._OPUS_REQUEST_DELEGATION_01.md`へ保存。

## 4. 禁止・注意
- 有料API呼出0(LLM/TTS/ASR/Azure)。Production run(er019/er026)の実起動0。`.venv`不使用、`py`のみ。
- 文法(Part 2)のProduction配線禁止(fixture testのみ)。Family YのProduction入口を新設しない。
- 既存Prompt 2・閾値・正規表現・Gate基準の直接編集禁止。
- 公開ページ(`user_test/`)変更0。`er0XX_output/`配下の既存run成果物を変更しない。
- 新規OPEN登録時は11-8分類必須。ACTIVE_TASKは本案件節のみ更新(他節を消さない)。
- 実装が大きいため、Bが未完で時間切れの場合は、完成済み部分をtest PASS状態でcommitし、未完部分を明記して報告(中途半端な配線でProduction runnerを壊さない=差替えhookは共通核+testが揃ってから入れる)。

## 5. 報告(RESULT_PACKET_KPHR2.md + 口頭要約)
- 設計変更点(DESIGN_01→02差分)、実装したファイル/関数、test件数(新規/回帰、PASS数、API 0の証明)、Production runnerの既定挙動の変化(宣言なし→rc=4待機)と影響範囲、残課題、evidence run(R1〜R4)の実行計画(コマンド・見積費用・順序。翌日実施)、費用(0円のはず)、commit hash・raw URL。
- RESULT_PACKET 4行((1)既存仕様整合 (2)未承認機能の既定値 (3)失敗終了時の最終成果物 (4)撤去・残置)+判定整合。
- 判断候補はFable判断/ユーザー判断を27-3で仕分けて列挙(推測で進めない)。