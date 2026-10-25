# OPERATIONS_01(KP Human Review 運用手順。Human(担当者)・Fable/運用AI向け)

管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_02 / 日付: 2026-10-25 / 対象: Family X・Z(Y・文法Part 2は本手順の対象外)
設計: `DESIGN_02.md`、コード: `er119_kp_human_review_cli_01.py`ほか。実API runでの確認(R1〜R4)は翌日JST 10/26以降の別委任。

## 1. 全体像(1行)
制作コマンドを実行 → KP候補(最大8件)が作られて**止まる(rc=4。失敗ではない)** → Humanが候補表を見て選ぶ(または「不在として進める」を明示宣言)→ **同じ制作コマンドをそのまま再実行**して先へ進む。

何もしない場合、制作は止まったままです(自動で確定されることはありません)。自動確定(AI推奨の上位をそのまま採用)は、明示の「不在宣言」があるときだけ起きます。

## 2. Human操作の手順
1. 制作コマンドを実行。KP候補ができると、標準出力に次が出て、終了コードが4になります。
   ```
   [KP_REVIEW_PENDING] KP Human Review待ちです(失敗ではありません。有料の後続工程には進みません)。
     - level=b1b: 依頼書 <run>/b1b/key_phrases/kp_human_review_request.md
     次の一手: 依頼書の表を見て `py er119_kp_human_review_cli_01.py select ...` で選ぶ(または明示の `declare-absent`)。
     再開コマンド(同じコマンドを1つだけ再実行): <実行したコマンドそのまま>
   ```
   (Zでは`RUN_LOCK`保持=二重起動もrc=4です。区別は標準出力の`[KP_REVIEW_PENDING]`の有無です。)
2. 依頼書 `kp_human_review_request.md`(または `py er119_kp_human_review_cli_01.py show --run <run> --level b1b`)を開く。表の「番号」を使います。例は§6。
3. 次のいずれか1つを実行する(`--by`は操作者名):
   | 状況 | コマンド |
   |---|---|
   | AI推奨をそのまま了承 | `select --run <run> --level <lv> --accept-ai --candidates-sha <表に出ているsha> --by <名前>` (REVIEWED扱い。表示したshaが必要=未表示の候補への了承は拒否) |
   | 自分で選ぶ(Std) | `select --run <run> --level a2 --kp 1,2,3 --by <名前>` |
   | 自分で選ぶ(Adv) | `select --run <run> --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>` (vocabはKP3件を含む最大5件。Stdは単語解説なし) |
   | 気に入らない句を二度と出さない | `--ng <番号>:<理由>`(select時)または `ng --run <run> --level <lv> --ng <番号>:<理由> --by <名前>`。NGは記事(family+slug+level)単位で共有storeに保存され、新しいrun dirでも復活しません |
   | 候補を選び直す(新しい候補を作らせる) | `reselect --run <run> --level <lv> [--ng 番号:理由] --by <名前>` (**上限2回/レベル/run**) |
   | NGを取り消す | `unng --run <run> --level <lv> --phrase "<句>" --reason <理由> --by <名前>` (理由と記録が必須) |
   | gloss(日本語の意味)が要確認の候補を解消 | `resolve-gloss --run <run> --level <lv> --rank <番号> --gloss "<意味>" --by <名前>` |
   | 状況確認 | `status --run <run>` |
   | JSONで一括指定 | `select --run <run> --level <lv> --from-json sel.json` (`{"kp":[1,2,3],"vocab":[1,2,3,4,5],"ng":{"6":"理由"},"by":"名前"}`) |
4. 実行後、表示された`next`のとおり、**§3の再開コマンド**を実行する。
- CLIが拒否した場合は終了コード2で理由が出ます(件数超過、NGとの重複、重複ペアの同時選択、`qa_fail`旗の候補[`--accept-qa-fail <番号>`の明示が必要]、gloss要確認の候補など)。状態は変わりません。
- `kp_human_review.json`を**手で編集しない**でください(署名不一致で全工程が停止します)。

## 3. 再開コマンド(rc=4の後は「これを1つだけ」)
- **制作を実行したときと同じコマンドを、そのまま1回だけ再実行**します。標準出力の`再開コマンド`行をコピーしてください。
  - X: `py er019_family_x_audio_production_runner_01.py --slug <slug> --run <run> --out-dir <out> --stage scaffold|all ...`(同じ引数)
  - Z: `py er026_family_z_fiction_production_runner_01.py --mode real --story <story> --slug <slug> --run <run> --stage all [--stages ...] ...`(同じ引数)
- 再開時の動作: 候補が同じなら**再選定しない(API 0)**。Xはsupport(有料)も再生成しません(support成果物が無い場合はSTOP)。確定集合のRedundancy QA(1 call/レベル)が再開で最初の有料呼出になります。
- Zで「選定そのものをやり直したい」ときは `--regenerate-stage kp_<lv>` ではなく `reselect` を使います。`--regenerate-stage kp_<lv>` は**現在のreviewからの再確定(再選定なし)+子孫stale化**です(KP表現が変わった場合の解説・Part 1の2段再生成は従来どおり: `kp_expl_b1b` → `kp_part1_b1b`)。
- Zの完成段の再実行は `--stages provision_shell,gate,assemble,pages,page_verify` を**1起動**で指定します(provision_shell欠落でgateが失敗し、再起動してRESTART_STORMを自行発動するのを防ぐ)。

## 4. RESTART_STORM(再起動の間隔)
- Z: 同じrunの起動が**5分(300秒)間に3回**に達すると`<run>/STOP`を自動作成して止まります(`--clear-stop --reason "..."`でのみ解除)。**安全機構は変更していません**。
- Xには同機構はありません(grep確認)。ただしXも「起動→rc=4→select→起動」を連続して行わず、下の間隔を守ってください。
- 運用ルール(Z): 「起動(rc=4)→ select → 再開」は起動2回なので通常は問題ありません。`reselect`を行う場合は「起動(rc=4)→ reselect → 再起動(新しい候補、rc=4)→ select → 再起動」で3起動になるため、**1回目と3回目の起動を5分以上あけて**ください(2回目の再起動を5分以上待つのが安全です)。
- testで固定: `er119_z_wiring_test_01.TestRestartStormInterval`(3起動が5分以内=STOP、窓の外=発動しない)。
- 万一STOPされた場合は自分で`STOP`ファイルを削除しない。Fableへ報告し、`--clear-stop`の判断を仰ぐ。

## 5. 「不在として進める」宣言(自動確定。Humanが見ないまま上位をAI採用)
- 位置づけ: **明示宣言**。期限による自動切替・環境変数・起動script・`.env`・hooksからは自動確定になりません。
- 宣言の記録先: `<run>/kp_review_mode.json`(runごと)、または範囲宣言は共有store `er119_output/kp_human_review_store_01/`。自動確定の判断は`read_mode_declaration()`(単一読取点)だけが宣言ファイルを読んで行います。
- 書式(CLI):
  ```
  py er119_kp_human_review_cli_01.py declare-absent --runs <run>[,<run>] --reason "<理由>" --by "<名前>" [--user-ref "<ユーザー発言の参照>"] [--rounds 1]
  py er119_kp_human_review_cli_01.py declare-absent --scope-family x --scope-date 2026-10-26 [--until <ISO日時>] --reason "<理由>" --by "<名前>" [--user-ref ...]
  ```
  runner引数で同時に宣言する場合: `--kp-review auto --kp-review-by <名前> --kp-review-reason "<理由>" [--kp-review-user-ref <参照>]`(`--kp-review wait`または省略=宣言なし=待機)。
- 規則(M-6):
  - 宣言は**round(=その候補sha)に結びつく**。既定は round 1 のみ有効。`reselect`した新しいroundは**宣言が失効して再び待機**します(Humanが見ていない候補を自動確定しない)。
  - Humanの操作(`select`/`reselect`/`ng`/`unng`/`resolve-gloss`)があった時点で、以後の宣言は失効します。
  - `--by`と出所の記録は必須。**AI(Fable/Claude/Opus/Sonnet等)が`--by`の場合は`--user-ref`(ユーザー発言の参照)が必須**です(AIが「不在とみなした」ことを自動確定の新しい経路にしない)。
  - 範囲宣言(`--scope-family`/`--scope-date`/`--until`)はCLIで可能ですが、**時間境界のない範囲宣言は拒否**されます。既定の運用では使いません(R-7: 使う場合はユーザーが期限付きで出す)。
- 自動確定の結果: status=`UNREVIEWED_AUTO_ADOPTED`(未レビュー≠NG)。KP=AI順位の上位3件(`auto_eligible`外[qa_fail/gloss要確認/NG/NG類似/重複ペア片方]を飛ばす)、Advのvocab=上位5件。0件ならSTOP。
- 事後Review(公開後など): `select`で内容を変えると REVIEWED になります。公開した版の署名を残すには `mark-published --run <run> --level <lv> --by <名前>`。公開版と確定版が異なる場合は`status`に差が表示されますが、**自動では差し替えません**(差替えは別の明示操作)。

## 6. `kp_human_review_request.md` の例(mock候補で生成した実出力)
```
# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `176b6a6b7fff6a1a` / 本文sha: `e2f36536420e`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | pushed prices up | 意味一 | Some owners pushed prices up in May |  |  |
| 2 | KP | took a sharp turn | 意味二 | Others took a sharp turn toward cheaper blends |  |  |
| 3 | KP | time lag | 意味三 | Market insiders say a time lag is built in |  |  |
| 4 | 単語 | feel a spike | 意味四 | Cafes keep raw beans in stock, so they don't feel a spike at once | 理由A |  |
| 5 | 単語 | in stock | 意味五 | Cafes keep raw beans in stock, so they don't feel a spike at once | 理由B |  |
| 6 |  | built in | 意味六 | Market insiders say a time lag is built in | 理由C |  |
| 7 |  | raw beans | 意味七 | Retail prices follow raw beans slowly | 理由D |  |
| 8 |  | Before you know it | 意味八 | Before you know it, the bill rises | 理由E |  |

## 操作(コマンド)
- 状況確認: `py er119_kp_human_review_cli_01.py status --run <run>`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run <run> --level b1b --accept-ai --candidates-sha <sha> --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run <run> --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run <run> --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言): `py er119_kp_human_review_cli_01.py declare-absent --runs <run> --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
```
- 「旗」欄: `QA FAIL(採用には --accept-qa-fail)`(canonicalization QAがFAIL=AUTO対象外)、`gloss HR待ち(resolve-gloss必要)`(解消後に選択可)、`NG済み`、`NG句に類似(AUTO対象外)`(NG句を含む/含まれる句。Human選択は可)、`重複: <番号>`(Redundancy QAで他候補と重複=同時選択不可)、`AUTO対象外`。Gateで除外された候補は表の下に理由つきで参考表示されます。
- 文面(上記)は実際の生成物のとおりです(`er119_kp_human_review_01.render_request_md`)。

## 7. 注意
- 公開ページは本番公開先へ自動では書かれません。事後Reviewで公開済みページを差し替える場合は別途の明示操作です。
- X: 公開後のsegment失効(事後Reviewで確定が変わったときの音声segment再生成)は本版では未実装です(`mark-published`と差の表示まで)。
- 文法(Part 2)・Y入口はこの手順の対象外です。
- 有料の後続(TTS、解説、Part 1)は、全レベルの確定後にだけ進みます。待機中(rc=4)に有料の後続は実行されません。
