# EVIDENCE_PLAN_01(KP HR + Part 2文法 の統合 runtime evidence R1〜R4。**次委任で本日JST 10/25中に実施**)

管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_03 兼 PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_03 / 作成日: 2026-10-25 / **本委任(委任_03)の実費=0円・有料API 0・Production run 0**。
「翌日(JST 10/26)に実施」の計画は撤回済み(Charter 2: 不要な日付分割をしない)。本計画は **実施委任(委任_04)が着手と同時に実行する手順書**。
関連: `BUDGET_PLAN_02.md`(KP HR)、`../PART2-GRAMMAR-PRODUCTION-WIRING-01/BUDGET_PLAN_02.md`、`OPERATIONS_01.md`、`TEST_PLAN_02.md §4`。

## 0. 費用・上限・STOP
| 項目 | 見積 | 根拠 |
|---|---|---|
| KP HR evidence(R1〜R4) | 30〜60円(最悪約110円) | `BUDGET_PLAN_02.md §2` |
| Part 2(R1〜R4の4セット + reselect/reextract等の追加 call) | 約3〜5円 | Part 2 `BUDGET_PLAN_02.md §4`(約0.4円/セット×4 + 再選定/再抽出0.08〜0.4円 + 予備) |
| 合計(予備20〜30%込み) | **約35〜70円**(最悪約120円) | |
| **案件Cap** | **150円**(Fable確定。超過見込みは実装せずFableへ報告) | 7-7: 承認済みScope内で300円以下→都度承認不要 |
| 日次 | 着手時に `py tools/daily_dev_cost_01.py` で当日(JST)累計を確認し、1,000円を超える見込みなら着手前にFableへ報告 | 7-9 |
| モデル | gpt-6-luna(`routing.SUPPORT_MODEL`=Part 2の`STUDY_TEXT_GRAMMAR_EXTRACT`/`EXPLAIN`、KP系と同一。最新世代の推奨系)。旧/下位モデルの使用なし。報告に記載 | 25節 |
| STOP確認 | 各run開始前と有料run開始前に `py tools/stop_scope_check_01.py --managed-id KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 --run-dir <run> --out <scratchpad>/stop_<run>.json`(rc=3なら新規API呼出なしで停止報告)。Part 2の管理IDでも同様に1回 | 26節 |
| 再起動 | 各runの「HR待ちrc=4→操作→再開」は仕様上の再起動(失敗の再試行ではない)。**原因不明のrc≠0が2回続いたら即STOP**。外部停止されたらその場で再起動しない | 26節 |
| 遮断 | evidence本番は実API。ただし**事前**に同じ手順をmockで通したnetwork遮断harness下の統合test(本委任で実施済み)が全PASSであること、`NETBLOCK`無しで起動するのは実run(R1〜R4)のみ | |

## 1. 事前確認(読取のみ・API 0・5分)
1. `git status --porcelain` で他agentの未コミット変更と衝突しないこと、`py tools/daily_dev_cost_01.py`、`stop_scope_check`(上記)。
2. **実リポジトリのstoreが空であること**: `er119_output/kp_human_review_store_01/` が存在しないこと(本委任の§0確認で不在を確認済み。evidenceで初めて作られる=R1のNG登録。以後はevidenceの成果物として扱い、test用には使わない)。
3. X source: `er019_output/coffee_prices/run_fxpw_01/{a2,b1b}/article.md` が存在し、`b1b/article.md` が3段落以上(TOO_FEW_PARAGRAPHSにならない)であること(`plan.split_family_x_article_text_v2`の事前実行はAPI 0)。
4. Z source: `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_02`(KP Human Review導入前に完成した公開済みrun。`writer/provenance.json`に`r2`・`kp_b1b`等のentry、`key_phrases/b1b_result.json`あり)。複製元は**無改変**のまま、`cost_log.jsonl`・`pages*`・`page_verify_local.json`・`STOP`系を除いてコピーする(Part 1 evidenceと同じ手順: `PART1_WIRING_EVIDENCE_01.md §1`)。audio dirはコピーして**clipの再利用に使う**(TTSは変更したKP segmentの差分だけ。Master Storeも併用)。
5. Part 1の判断記録 `docs/pm/decisions/part1_translation_decision.json` が存在する(Part 1ブロックが描画される=Part 2がその直後に連結される構成を実ページで確認できる)。

## 2. 対象記事・run名(固定)
| run | 区分 | 入力 | 出力dir |
|---|---|---|---|
| **R1** | X・HRあり(`--kp-review`なし) | `er019_output/part2_hr_evidence_01/run_r1/{a2,b1b}/article.md`(上記coffee_pricesのcopy) | `er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1` |
| **R2** | X・auto | `er019_output/part2_hr_evidence_01/run_r2/`(同じarticleのcopy。**slugが同じ**=`part2_hr_evidence_01`なのでR1のNGが共有registryで効く) | `.../part2_hr_evidence_01__run_r2` |
| **R3** | Z・HRあり | `run_p2_evidence_r3`(`the_tell_tale_heart/run_sf_prod_02`の複製) | `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_p2_evidence_r3` |
| **R4** | Z・auto | `run_p2_evidence_r4`(同じ複製元から) | `.../run_p2_evidence_r4` |
公開ページ・既存run・`user_test/`は変更しない(Zは`--pages-dir`で候補ページを`<run>/pages_evidence`へ分離)。

## 3. 並列実行計画(クリティカルパス)
```
t0   R1(X) 起動 ─┬─ scaffold(a2,b1b): [Part 2 抽出 → support → KP候補(a2,b1b)] → rc=4(KP+文法を1回)
     R3(Z) 起動 ─┘  --stage kp:       [Part 2 抽出 → KP候補(b1b,a2)]                  → rc=4(KP+文法を1回)
t0+~10分 候補確認(統合依頼書 review_request.md の内容をFable/委任agentが読む)→ CLI操作(下記)
t0+~15分 R1/R3 再開(同じコマンド)→ 完走 → 検証
t0+~15分 R2(X) と R4(Z) を並列起動(宣言は起動前に)→ 検証(R1のNGがskipされる)
```
- R1とR3はFamily・本文・run別で独立=並列。R2はR1のHuman操作(NG登録)後、R4はR3の操作後に起動(NG skipを確認するため)。それ以外の待ちを作らない。
- 直列にする理由: 同一run内は「候補→Human操作→再開」の依存。R2/R4の「NG skip」確認はR1/R3のreselectが先。
- 起動間隔(RESTART_STORM): Zは同一runを5分間に3回起動すると`STOP`が自動作成される。R3は「起動1(rc=4)→ reselect/select → 起動2」で2起動、grammar `reselect`を挟む場合も候補は即時(API 0)に更新されるため再起動不要。**R3の起動は5分以内に3回行わない**(必要なら起動2と3の間を5分以上あける)。XにはRESTART_STORMは無いが同じ間隔で運用する。

## 4. コマンド列(実施委任がそのまま実行できる形)
共通の宣言は **AI宣言** なので `--by Fable --user-ref` が必須(`user_ref`にユーザー原文を参照):
`USERREF="docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_USER.md §8 検証項目3(Human未レビュー時にTOP3/TOP5/文法TOP1で制作を継続できる)の検証指示"`

### R1(X・HRあり)
```
# 準備(API 0)
mkdir -p er019_output/part2_hr_evidence_01/run_r1/a2 er019_output/part2_hr_evidence_01/run_r1/b1b
cp er019_output/coffee_prices/run_fxpw_01/a2/article.md  er019_output/part2_hr_evidence_01/run_r1/a2/
cp er019_output/coffee_prices/run_fxpw_01/b1b/article.md er019_output/part2_hr_evidence_01/run_r1/b1b/
# 1) 候補生成(KP a2/b1b + 文法)。期待: rc=4 [KP_REVIEW_PENDING]、統合依頼書 <out>/review_request.md
py er019_family_x_audio_production_runner_01.py --slug part2_hr_evidence_01 --run run_r1 --level both --stage scaffold --budget-jpy 40
py er119_kp_human_review_cli_01.py status --run <out_dir>             # KP×2 + 文法 の PENDING_REVIEW を確認
# 2) Human操作(KP: b1bで reselect+NG登録 → 新roundのselect、a2はselect。文法: top2)
py er119_kp_human_review_cli_01.py reselect --run <out_dir> --level b1b --ng 1:<理由> --by <名前>     # KP b1b: NGを共有registryへ
py er119_kp_human_review_cli_01.py grammar-select --run <out_dir> --choice top2 --reason "<理由>" --candidates-sha <sha> --by <名前>
# 3) 再開(同じコマンド): KP b1b は候補再生成(round 2, 1回)→ 再度rc=4(KP b1bのselect待ち)
py er019_family_x_audio_production_runner_01.py --slug part2_hr_evidence_01 --run run_r1 --level both --stage scaffold --budget-jpy 40
py er119_kp_human_review_cli_01.py select --run <out_dir> --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 --by <名前>
py er119_kp_human_review_cli_01.py select --run <out_dir> --level a2  --accept-ai --candidates-sha <sha> --by <名前>
# 4) 完走(同じコマンド): KP finalize → Part 1(T1訳含む) → Part 2 finalize(Step B 1 call) → rc=0
py er019_family_x_audio_production_runner_01.py --slug part2_hr_evidence_01 --run run_r1 --level both --stage scaffold --budget-jpy 40
# 5) 検証(API 0): study_text再実行がreuse、tts入口のM-2検査
py er019_family_x_audio_production_runner_01.py --slug part2_hr_evidence_01 --run run_r1 --level b1b --stage study_text --budget-jpy 40     # 期待: API 0・reused
```
- 文法の期待: `grammar_human_review.json` `status=REVIEWED`・`selection.choice=top2`・`decision.reason`に理由・`verdicts`でTOP1=NOT_SELECTED。`part2_result.json`の`selection.source=human_top2`。
- TTS/player(任意・実費あり): Part 2の入口検査(`--stage tts`でrc=3/4の分岐、player HTML合成)はmock統合testで固定済み。実音声のplayerまで通すのは費用が増える(KP segmentの差分TTS 約1〜3円+body/Preview等のTTSが再利用できない場合は増える)ため、**R1では `--stage tts` の入口検査(待機中にrc=4、確定後にPart 2 freshを通過)までを必須**とし、`--stage all`は見積が上限内のときだけ。

### R3(Z・HRあり)
```
# 準備(API 0): 複製(cost_log.jsonlとpages*を除く。audio dirは再利用のため含める)
mkdir -p er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_p2_evidence_r3
robocopy または cp -r で run_sf_prod_02 の中身を複製(除外: cost_log.jsonl, pages*, page_verify_local.json, STOP*, kp_review_pending.json)
# 1) 候補生成。期待: rc=4(KP b1b/a2 + 文法)。stdout [KP_REVIEW_PENDING]、<run>/review_request.md
py er026_family_z_fiction_production_runner_01.py --mode real --story the_tell_tale_heart --slug the_tell_tale_heart --run run_p2_evidence_r3 --stage kp --approved-budget-jpy 20
# 2) Human操作: KPはselect(b1b, a2)。文法は reselect → 候補が尽きる(または NG)→ omit
py er119_kp_human_review_cli_01.py select --run <run_dir> --level b1b --accept-ai --candidates-sha <sha> --by <名前>
py er119_kp_human_review_cli_01.py select --run <run_dir> --level a2  --accept-ai --candidates-sha <sha> --by <名前>
py er119_kp_human_review_cli_01.py grammar-select --run <run_dir> --choice reselect --reason "<理由>" --candidates-sha <sha> --by <名前>     # 次順位
py er119_kp_human_review_cli_01.py grammar-ng --run <run_dir> --rank 1 --reason "<理由>" --by <名前>                                      # 候補を順にNG→枯渇(実際の候補数による)
py er119_kp_human_review_cli_01.py grammar-select --run <run_dir> --choice omit --reason "<理由>" --candidates-sha <sha> --by <名前>        # human_rejected_all
# 3) 再開(5分以上あけて、同じコマンド): KP finalize → Adv解説 → Part 1 → Part 2 finalize(ZERO: Step B 0 call)
py er026_family_z_fiction_production_runner_01.py --mode real --story the_tell_tale_heart --slug the_tell_tale_heart --run run_p2_evidence_r3 --stage kp --approved-budget-jpy 20
# 4) 完成段(1起動で。provision_shell欠落禁止): TTSはKP segmentの差分のみ
py er026_family_z_fiction_production_runner_01.py --mode real --story the_tell_tale_heart --slug the_tell_tale_heart --run run_p2_evidence_r3 --stages tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify --pages-dir er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_p2_evidence_r3/pages_evidence --approved-budget-jpy 40
```
- 文法の期待: `part2_result.json` `status=ZERO`・`zero_reason=human_rejected_all`、ページに`ZERO_P2`固定文面が**Advancedの節にだけ**載る(R-3の`part2_verified`)。reselect→次順位でTOP2を採用するバリエーション(SELECTED)は別runで1回だけ確認するか、**R3の文法は「reselect→SELECTED(新TOP)」を主、「枯渇→omit」はmock統合test(固定済み)**とする。実候補数に依存するため、実施委任が候補確認時に選ぶ(候補が2件以下ならreselect→枯渇→omit、3件以上ならreselect→top1)。
- `--regenerate-stage part2_b1b`(再finalize)の確認: 選定を変えた後に `--stage kp --regenerate-stage part2_b1b` で Step Aは呼ばれず(Step A'' 0 call)、`part2_b1b`だけ再生成されること(任意・費用0.08円)。

### R2(X・auto。R1のNGがskipされる確認)
```
(R1のreselect後に実行。source copyは R1 と同じ article)
py er119_kp_human_review_cli_01.py declare-absent --runs <out_dir_R2> --reason "Humanなし経路の検証" --by Fable --user-ref "$USERREF"      # runの出力dirが未作成なら scaffold 初回起動直前に作る
py er019_family_x_audio_production_runner_01.py --slug part2_hr_evidence_01 --run run_r2 --level both --stage scaffold --budget-jpy 40
```
- ※出力dirは初回起動でできる。宣言ファイルは `<out_dir>/kp_review_mode.json` なので、**先に出力dirだけ作って宣言**するか、`--kp-review auto --kp-review-by Fable --kp-review-reason "..." --kp-review-user-ref "$USERREF"`(runner引数。内部で同じ宣言ファイルを書く=`source: cli_runner_arg`)で1起動にする。**後者を推奨**(宣言が起動1回に収まる)。
- 期待: 1起動で rc=0(待機なし)。KP=`UNREVIEWED_AUTO_ADOPTED`・文法=`UNREVIEWED_AUTO_ADOPTED`(auto_top1)。R1でNGにしたKP句・文法の文は `filtered_by_ng` に入り(文法: `grammar_candidates.json` の `filtered_by_ng`、KP: 候補の`dropped(human_ng)`)、**採用されない**。`summarize_review_statuses`で「Human確認済み 0・未レビュー採用 2」と表示される(レビュー済みに数えない)。

### R4(Z・auto)
`--kp-review auto --kp-review-by Fable --kp-review-reason "Humanなし経路の検証" --kp-review-user-ref "$USERREF"` を付けて `--stage kp` を1起動(R3と同じ複製元から `run_p2_evidence_r4`)。期待はR2と同様(Zの文法NG skipはR3で登録したNGの有無に依存。R3で`grammar-ng`/`reselect`した文がR4の抽出でskipされる)。完成段まで通す。

## 5. 期待成果物と検証項目(ユーザー検証7点 + Part 2)
| # | 検証 | 取得する証跡 |
|---|---|---|
| 1 | KP TOP8/文法TOP2が保存される | `kp_candidates.json`(≤8)、`grammar_candidates.json`(TOP1/TOP2 + 残り + `tier_table`) |
| 2 | Human選定が最終出力へ反映 | `part2_result.json`の`selection.source`(human_top2等)、`kp_selection_final.json`、ページ(R3: index.htmlのAdvancedにPart 2 1個・Standardに0)、R-3の`part2_verified` |
| 3 | 未レビュー時 KP TOP3/Part1 TOP5/文法TOP1で継続 | R2/R4で rc=0、status=UNREVIEWED_AUTO_ADOPTED(KP・文法)、`mode_declaration.source=cli_runner_arg`・`user_ref`にユーザー原文参照 |
| 4 | NGは自動採用されない | R2/R4の候補で R1/R3 のNG句・文が `filtered_by_ng`(文法)/ dropped(KP)に入る |
| 5 | 再生成・再開で選定保持 | 再開起動でStep A''/KP選定/supportが0 call(`raw_usage_log.jsonl`/`cost_log.jsonl`のstage別call数で確認)、`--stage study_text`がreuse |
| 6 | 正式経路で機能 | X: `er019...runner` main経由、Z: `er026...runner` main経由。Y: 正式入口なし(別案件`FAMILY-Y-PRODUCTION-LAUNCH-01`)=PRODUCTION_WIREDにしない |
| 7 | 既存Gate・音声構成に意図しない変更なし | gate/assemble/page_verify PASS、非KP clipはMaster Store/audio再利用(TTS新規clip数を記録)、`user_page_standard_check` PASS |
| P2-a | **stage順序** | Z: `writer/provenance.json`の`downstream_stages`(`part2_cand_b1b`の`generated_at`が`kp_b1b`より前、`part2_b1b`が`kp_part1_ja_b1b`より後)、`e2e_stage_log.jsonl`。X: stdoutの`[FAMILY-X-AUDIO-SCAFFOLD]`行順(Part 2 抽出 → support → KP候補 → rc=4)と`raw_usage_log.jsonl`のstageタグ(`part2_cand`が`scaffold`内のsupport/KPより前) |
| P2-b | 待機が1回 | R1/R3の初回起動のrc=4が1回で、stdoutに`[KP_REVIEW_PENDING]`が1回・`再開コマンド`が1つ。統合依頼書 `<run>/review_request.md` にKP×2と文法が載る |
| P2-c | 再開でStep A''/support/KPを再生成しない | 再開起動のcall数: Step A'' 0(`part2_cand` stageタグのcall 0)。Step B はfinalize時のみ1 call |
| P2-d | 費用タグ | Z: `stage=part2_cand` / `part2_final`、X: 同名のlogging_context。1セットあたりのPart 2原価(約0.4円)を実測 |
| P2-e | 失敗系(任意・mockで固定済み) | `part2_failed.json`+rc=3+案内は`--stage study_text`の1つ(mock統合testで固定) |

## 6. 失敗時・異常時
- 候補が0件の記事: 文法は`NO_CANDIDATE_UNREVIEWED`で待たずに確定(ZERO_P2)。R1/R3の文法操作は、候補がある別記事に差替えて取り直す(同じ複製元で候補0なら、`the_tell_tale_heart`以外=`melos`の複製に変更)。
- Step A''/Step Bの構造失敗(2 call)→`part2_failed.json`+rc=3。再実行は記載の`--stage study_text`(X)/`--stage kp`(Z)の1回だけ。失敗が2回続いたらSTOPしてFableへ報告。
- 実費がCap(150円)の80%を超えた時点で、残りのrunを実施せずFableへ報告。
- 汚染防止: evidenceは専用のrun dir・専用slugだけに書く。既存の`er019_output/coffee_prices/*`・`er026_output/.../run_sf_prod_02`・公開dir・`user_test/`は変更しない(複製元は読取のみ)。
- 事後: `er119_output/kp_human_review_store_01/`（実repoのstore。evidenceのNG registryなので**コミットしない**。`git status`で不追跡のままか、`.gitignore`対象かを確認）。
