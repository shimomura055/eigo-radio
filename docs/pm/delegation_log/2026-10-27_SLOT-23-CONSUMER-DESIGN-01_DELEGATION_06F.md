## 管理ID

SLOT-23-CONSUMER-DESIGN-01 委任_06F(F班: ①②③表示仕様(Std②=①と同等の日本語詳細解説、①二重下線/②下線/③下線+短い訳、遡及なし)のX/Y/Z×Std/Adv 6経路 runtime evidence+実ブラウザ検証。前提=A〜E班+M班完了(マーク発行接続 commit 1684e19f5/ccf118a31)。ユーザー正式決定=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`+`2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_04.md` §2/§5(受入条件14=USER.md §6)。有料上限¥60(Fable自律枠)。並行Agent: AIF委任_06(AI島run `ai_island_temple__run_form_prod_01`のみ=**触らない**)、PM-SSOT-SYNC-26(SSOT)。あなたの所有=新evidence run dir(各Family、run名に`_s23f`付与)、`docs/research/SLOT-23-CONSUMER-DESIGN-01/{EVIDENCE_RESULT_06,BROWSER_CHECK_06,COST_06,ROUTE_STATUS_06}.md`+`tools/`+`evidence_runs/`+`screenshots/`(PNGは小さく、合計<5MB)、`..._DELEGATION_06F.md`(+check.json)、`docs/pm/RESULT_PACKET_S23F.md`(gitignore)。Productionコード編集禁止(不具合は文書化して停止。小修正も自分で直さない)。SSOT権なし。pathspec付きcommit、wav/raw_usage_log/STOP/lock不追跡、`git push origin HEAD:main`。時間見込み約3h。

## 性質/禁止

- 性質: evidence取得(DEV run dir、非公開)。到達上限=EVIDENCE(PRODUCTION_WIRED判定はFable)。
- 禁止: Full Story TTSの再生成(KP音声のみ許容≤¥5/経路)、STOP/HR Lock/Gate迂回、HRなし宣言、Production既定動作変更、禁止Git操作。
- 起動: 他runner稼働確認(`tasklist /v | findstr /i python`、AIF委任_06のX runnerと重ならないようX経路は最後・er019 process不在を確認)、全体150秒以上、**同一run起動間300秒以上**、有料前に`py tools/stop_scope_check_01.py --managed-id SLOT-23-CONSUMER-DESIGN-01 --run-dir <run> --out <scratch>`+必要性1行、`.venv\Scripts\python.exe`+`TTS_EXECUTION_MODE=STANDARD`。順序 Y→Z→X。

## 実施事項(各経路)

1. ベースrun: Y=`run_gpg5_y_01`、Z=`melos/run_kcp4_ev_z_01`、X=`part2_hr_evidence_01__run_gpg5_x_01`(各自のコピー`_s23f`。STOP/lockはコピーしない)。**正式初回経路の実証**のため、各levelでKP reviewを新規作成(`new_review`経由=既存reviewを退避し`--regenerate-stage kp_<lv>`等でreview再生成。P7/W5'候補抽出の費用≈¥1.5/level)→マーク`std_part1`/`display_spec`が自動付与されることを確認(受入条件1)。
2. 確定: 候補docから`--actor evidence`のpayload v2(①3件・②1〜2件・**③2件以上を必ず含む**、活用形を含む候補を優先)→`confirm --from-form --actor evidence --grammar-pending`→文法=`grammar-pregen`→0件または1件確定。G0/G1(不変条件含む)PASS。
3. 実行: runner通し(Std Part 1生成=①+②、T1訳、KP音声、assemble、pages、page_verify)。確認: (a)Std/AdvともPart 1がちょうど1個・①+②の全件・日本語解説(Std難易度差=Head差分のみ、Adv golden不変)、(b)①二重下線/②下線/③下線が本文に出る(`data-hl`件数=確定件数、NOTICEの有無と理由)、(c)③訳リスト=確定`japanese_gloss`逐語、(d)G3(`verify_highlights`+Part 1照合)PASS、`check_page(public)`PASS、public `⏸`0、(e)確定レコードcmp同一(実行前後)、(f)finalize/pagesのLLM 0(Part 1生成分のみ加算)、(g)retry/resume: pages stageを再実行して出力バイト同一・API 0、`--regenerate-stage`で確定不変、(h)actual model_id/routing(Part 1=`KEY_PHRASE_GENERAL_EXPLANATION`のmodel名)記録、(i)dev `--page-audience dev`(Y/X)で`⏸`が装飾の外。
4. 実ブラウザ検証(`BROWSER_CHECK_06.md`、playwright): 各Familyのpages出力をローカルHTTPで開き、PC(1280px)とスマホ(375px/390px、DPR2/3)で、①の二重下線が2本に見える・②③と太さ/下線の違いが判別できる・文字サイズ/色が本文と同一・背景なし・改行/段落/句読点不変・`document.body.innerText`に`⏸`やdata属性由来の文字混入なし・コピーテキストに余計な記号なし、をスクリーンショット+DOM計測(computed style: `text-decoration-style`、`font-weight`、`font-size`、`color`、`background-color`)で記録。
5. `ROUTE_STATUS_06.md`: 6経路×受入条件14の対応表(EVIDENCE/未取得+理由)。AI島(X Std/Adv実記事)は「AIF委任_06で適用中」と参照。
6. `COST_06.md`。commit: `SLOT-23-CONSUMER-DESIGN-01 委任_06F: ①②③表示仕様の6経路runtime evidence(新規review→マーク自動付与→Std Part 1→ハイライト→G3)+実ブラウザ検証(PC/スマホ)、¥<費用>`。Secret grep 0件。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: 有料=対象。

## 事前指定Read一覧

`IMPL_PLAN_03.md`(F/evidence計画R7)、`IMPL_{B,C,D,E,M}_01.md`(公開API・stage名・regenerate手順)、`docs/pm/RESULT_PACKET_S23{C,D,E,M}.md`、`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/EVIDENCE_RESULT_05C.md`(Y run手順)、`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/EVIDENCE_RESULT_04.md`(Z run手順)、`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/EVIDENCE_RESULT_05.md`(X run手順)。

## 報告

`RESULT_PACKET_S23F.md`: (0)T-0、(1)経路別evidence表(a〜i)、(2)ブラウザ検証要約、(3)費用、(4)不具合・修正案(あれば)、(5)判断候補、(6)必須4行+「判定整合」、(7)SSOT文案(OPEN-562 6経路Status)、commit hash・raw URL。末尾5行要約。