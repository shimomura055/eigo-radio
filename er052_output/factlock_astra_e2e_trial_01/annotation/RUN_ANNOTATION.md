# 注記者A/B 起動・統合・検査・監査手順(委任_08、API支出0はプロンプト準備まで。注記実施は別委任)
作業ディレクトリ: `C:\Users\tensh\eigo-radio\er052_output\factlock_astra_e2e_trial_01`。スクリプトはUTF-8: `PYTHONUTF8=1 python ...`。
プロンプト: `annotation/prompts/<slug>__{A,B}.md`(sha256は `annotation/PROMPT_SHA256.json`。起動前に再計算して一致を確認する)。
slug 10個: byd_recall central_bank_mortgage hormuz inbound_tourism meta openai_copyright semiconductor_earnings small_bag space_weapons streaming_price

## 1 起動(Fableが委任文へそのまま貼る固定文言。A用)
```
あなたは注記者Aです。次の1ファイルを、Readツールで1回だけ読み、その中の指示だけに従って、返答の本文だけで答えてください。
ファイル: C:\Users\tensh\eigo-radio\er052_output\factlock_astra_e2e_trial_01\annotation\prompts\<slug>__A.md
このファイル以外のファイルを読まない。Grep/Glob/Bash/Web/他のツールを使わない。ファイルを作らない。説明文を付けない。
```
B用は `注記者Aです` を `注記者Bです`、`__A.md` を `__B.md` に置換するだけ。<slug> は10テーマ分を1つずつ差し替える。
- 隔離: A・Bは別々のsubagent(互いの返答を見せない)。各subagentには上記の文言以外(テーマの補足、事前の期待、他テーマの結果)を渡さない。
- 推奨形: 1テーマ=1 subagent呼び出し(A10回+B10回、独立なので並列可。テーマ間の持ち越し文脈を排除)。Fableが「1注記者=10テーマ連続」を選ぶ場合は、返答分離のため区切り規則が別途必要(仕様の出力形式は1テーマ1返答のみ定義。要Fable判断)。
- 各返答の本文を `annotation/out/<A|B>/<slug>/reply.md` に保存する(呼び出し側が保存。subagentは保存しない)。同時にsubagentのtranscript(jsonl)を `annotation/out/<A|B>/<slug>/transcript.jsonl` として保存(取得手段は実行時にFableが確認。取得できない場合は隔離手段(ii)の監査が不能のためFableへ報告)。

## 2 返答の取り出しと単独検査(各 slug・各 ann について)
```
S=<slug>; N=<A|B>; B=stage_r/$S/storyline_b3/selected_brief.md; L=stage_r/$S/research_ledger/verified_fact_ledger.txt; O=annotation/out/$N/$S
PYTHONUTF8=1 python b3_annotation_merge_01.py extract --reply $O/reply.md --out-md $O/annotated.md --out-sidecar $O/annotation.json
PYTHONUTF8=1 python b3_annotation_check_01.py --brief $B --annotated $O/annotated.md --ledger $L --sidecar $O/annotation.json --spec B3_ANNOTATION_SPEC_v2_ANNOTATOR.md --out $O/check_result.json
```
`extract` が STOP を返した場合(`=== STOP ===`返答)は理由を `STOP_<slug>_<N>.txt` に保存しFableへ報告(STOP条件は仕様§4)。check の終了コード1=形式FAIL。

## 3 統合(A・B両方がcheck PASSのslugのみ)
```
M=annotation/out/merged/$S
PYTHONUTF8=1 python b3_annotation_merge_01.py --brief $B --ledger $L --ann-a annotation/out/A/$S/annotated.md --side-a annotation/out/A/$S/annotation.json --ann-b annotation/out/B/$S/annotated.md --side-b annotation/out/B/$S/annotation.json --out-dir $M --spec B3_ANNOTATION_SPEC_v2_ANNOTATOR.md
```
出力: `$M/merged_selected_brief_factlock.md`, `merged_annotation.json`, `merged_core_numbers.json`, `resolution_log.json`, `agreement.json`, `merged_check_result.json`。統合STOP時は `$M/merge_stop.json`。人が裁定しない(不一致は統合規則で機械決定)。

## 4 判定線の確認(事前登録の線、結果を見て変更しない)
各 slug の `$M/agreement.json` を開き、分割一致率 >= 0.8 かつ 中核Jaccard >= 0.67 を確認。いずれか未満=「規則を機械的に適用できていない」と報告(`agreement.json` の flags に出る)。10テーマ分の一覧(slug・分割一致率・中核Jaccard・flags)を `annotation/out/AGREEMENT_SUMMARY.md` にまとめる。線を満たさなくても統合版の採否は仕様どおり(統合後checkがPASSなら採用可)、線未達の扱いはFableが判断。

## 5 事後監査(transcript)
```
PYTHONUTF8=1 python annotation/audit_strict_01.py --transcript annotation/out/$N/$S/transcript.jsonl --annotator $N --out annotation/out/$N/$S/audit.json
PYTHONUTF8=1 python b3_annotator_audit_01.py --transcript annotation/out/$N/$S/transcript.jsonl --out annotation/out/$N/$S/audit_base.json --allow-substring prompts/${S}__$N.md
```
期待: strict が `PASS_ONLY_ALLOWED_READS`(自分のプロンプトのRead 1件)または `PASS_NO_TOOL_USE`。`VIOLATION`(許可外Read・Grep等・解釈不能行)なら、その返答は採用せずFableへ報告。許可Read 2件以上も記録する(再読込は許容だが報告)。strict の自己テスト: `python annotation/audit_strict_01_test.py`(ALL_PASS)。

## 6 形式FAIL時
- 単独check FAIL または extract の形式不正(区切り欠落・JSON不正): 同じ固定文言で同slug・同注記者に再委任を**1回だけ**行う(元の返答は `reply_attempt1.md` として別名保存。良い方の採用はしない=再委任結果を採用、元結果は保存)。
- 再委任後も FAIL: STOPしてFableへ報告(3回目はしない)。Trial全体でも、仕様・プロンプトを直して再実行するか否かはFableが判断(静かな差替禁止)。
- 台帳に無い記述でSTOP返答(仕様§4)は形式FAILではない。再委任せず理由を記録しFableへ報告。

## 7 AMBIGUOUS記録の扱い(Fable決定2026-10-09)
`annotation/AMBIGUOUS_FACT_MAP.json` に、台帳のAMBIGUOUS記録とB3が選択した記録の突合結果を保存(注記者は台帳のstatusを見るが扱いを変えない)。統合後、`merged_annotation.json` を編集せず、評価時にこの表で「台帳AMBIGUOUS由来」を判別して別集計する(PREREGISTRATION v2.2 の5項12)。サイドカーへ `ambiguous_fact: true` を付ける作業は、統合スクリプト非編集の方針により評価側集計で代替する(Fable判断要: 付与が必須ならpost-merge用の小スクリプトを別委任)。

## 8 次委任で実行する手順(委任_10時点の残件。2026-10-09)
委任_10時点: hormuz / streaming_price(B3 v2基準)は A・B 単独PASS->統合PASS->final->inputs配線->G0実照合PASS済み。inbound_tourism(v1 brief)は再注記A・Bとも単独 c_numbers FAIL(統合せず)。
1. 再注記済み6本(hormuz / streaming_price / inbound_tourism の A・B)の transcript を `annotation/out/<N>/<slug>/transcript.jsonl` へ保存する(呼び出し側。現在置かれているのは旧v1ラウンドのもの)。保存後に節5の監査(strict / base / `annotation/run_audits_01.py`+`audit_extra_01.py`+`audit_bash_detail_01.py`)を実行し AUDIT_SUMMARY.md を更新する。判定は(d)に従い補助監査を正とする。
2. hormuz / streaming_price の単独検査・統合は B3 v2 を基準にする: `B=stage_r/$S/storyline_b3_v2/selected_brief.md`(節2・3の `$B` を差し替える)。final は `python annotation/make_final_01.py <slug>`(v2は自動選択)、inputs配線は `python annotation/wire_inputs_01.py <slug>...`、G0は `.venv/Scripts/python.exe -X utf8 er052_factlock_astra_e2e_runner_01.py run --root er052_output/factlock_astra_e2e_trial_01/g0_real_annotation_01 --themes <csv> --g0-only`。
3. inbound_tourism: 節6のとおり再委任は1回まで。v1ラウンド(委任_09)と今回の再注記で既に2回注記済み=これ以上は再委任せずFableへ報告(STOP)。選択肢(Fable判断): (i)検査scriptのID_REマスク欠陥(連字符なしID `F01` の数字を分類漏れと誤検出)を直す(ただし直してもA=`8`分類漏れ、B=概念重複2件+`2026`分類漏れが残る)、(ii)inbound_tourismを除外し9テーマで進める、(iii)プロンプト/仕様を直して再実行(静かな差替禁止)。
