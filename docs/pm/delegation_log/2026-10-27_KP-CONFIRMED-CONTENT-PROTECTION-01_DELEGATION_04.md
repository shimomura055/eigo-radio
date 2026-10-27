## 管理ID

KP-CONFIRMED-CONTENT-PROTECTION-01 委任_04(全6経路のうち唯一runtime evidence未取得の**Z Standard(a2)**について、確定内容保護(KCP: G0〜G3)の実run evidenceを取得する。ユーザー条件「全6経路揃うまでPRODUCTION_WIREDと判定しない」(全面修正版USER.md)への対応。有料・上限¥30(Fable自律枠)。前提=委任_03(12aede6f7)の`EVIDENCE_RESULT_03.md`(X Std/Adv・Y Std/Adv・Z Advの手順)、GPG委任_05/05C(Z `melos/run_p2_evidence_r3|r4`はStd KPが旧run互換でKCP sidecar未生成=「Z Std は KCP対象外」と記録)、KP75 evidence(082d5ec6c、Z Std候補docの7+5形式run)。並行Agent: SLOT-23設計(read-only)、AIF委任_04(read-only診断)。あなたの所有=新evidence run dir(Z配下、run名に`_kcp4`付与)、`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/{EVIDENCE_RESULT_04,COST_04}.md`、`docs/pm/delegation_log/2026-10-27_KP-CONFIRMED-CONTENT-PROTECTION-01_DELEGATION_04.md`(+check.json)、`docs/pm/RESULT_PACKET_KCP4.md`(gitignore)。Productionコード編集禁止(不具合は文書化して停止)。SSOT権なし。pathspec付きcommit、wav/raw_usage_log/STOP/lock不追跡。

## 性質/禁止

- 性質: evidence取得(DEV run dir、公開なし)。到達上限=EVIDENCE。
- **go/no-go(先に判定)**: Z Std のKP確定→finalizeが来歴上どの下流をstaleにするかを`er026`/Z runnerの来歴定義(Grep `downstream|stale|parents|kp_a2`)で確認。Full Story TTSがstaleになる構成なら**起動せず**、理由と代替案(次回Z新規記事で取得/来歴の切り分け提案)を報告して終了。KP音声(Key Phrase TTS)のみの再生成(見込み≤¥5)は許容。
- 起動間隔: 他runner稼働確認(`tasklist /v | findstr /i python`)、全体150秒以上、同一run 5分3回禁止(**起動間に最低300秒空ける**運用にする)。有料run前に`py tools/stop_scope_check_01.py --managed-id KP-CONFIRMED-CONTENT-PROTECTION-01 --run-dir <run> --out <scratch>`+必要性1行、`.venv\Scripts\python.exe`+`TTS_EXECUTION_MODE=STANDARD`。
- 禁止: STOP/HR Lock/Gate迂回(STOPが出たら停止し報告。`--clear-stop`はFable権限)、HRなし宣言、Production既定動作変更、禁止Git操作。
- 時間見込み: 約1.5h。

## 実施事項

1. ベースrun選定: KP75 evidenceのZ Std run(7+5形式の候補doc`kp_candidates`+`reason_ja`あり)を`_kcp4`名でコピー(STOP/lockはコピーしない。コピー後に`attempt_history`の連続性を確認)。候補docが旧形式しかない場合は、Std KP候補抽出のみ再実行(P7/W5'、見込み≤¥3)。
2. 確定: 候補docから`actor=evidence`で payload v2(①3件・②0〜2件・③数件、`candidate_id`/`kind`/`candidates_sha256`/`text_sha256`)を生成し、`confirm --from-form --grammar-pending --actor evidence --by <名> --user-ref <EVIDENCE_PLAN参照>`でG0→確定レコード(`confirmed_selection.json`+auditミラー、hash chain)。文法は`grammar-pregen`→`confirm --grammar-from-form`(Top1があれば1件、なければ0件)。
3. 実行: Z runner `--stages kp,...,pages,page_verify`(必要なら`--regenerate-stage kp_a2`=再finalize)→G1(`require_final_consistent`/stage_kp post-install)、G2(TTS record含`phrase_repeat`。KP音声再生成が発生した場合のみ)、G3(pages: `japanese_gloss`表示=M2-b)、`page_verify kp_selection_verified ok=true legacy=false`、finalize LLM 0(usage差分=KP音声のみ)、確定前後で`confirmed_selection` cmp同一。
4. ガード実証(API 0): 確定後の`reselect`/`ng`/`declare-absent`が`ConfirmedContentLocked`で拒否、`confirm-revise --user-ref`経路の存在確認(実行はdry-run)。
5. `EVIDENCE_RESULT_04.md`(Z Std経路表、go/no-go記録、G0〜G3結果、費用)、`COST_04.md`。6経路Status表(KCP: X Std/Adv・Y Std/Adv・Z Adv=EVIDENCE(委任_03)、Z Std=本委任)。
6. commit: `KP-CONFIRMED-CONTENT-PROTECTION-01 委任_04: Z Standard の確定内容保護 runtime evidence(G0〜G3、Full Story音声不変、¥<費用>)`、trailer `Delegation: KP-CONFIRMED-CONTENT-PROTECTION-01/04`、`git push origin HEAD:main`。Secret grep 0件。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: 有料=対象。

## 事前指定Read一覧

`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/EVIDENCE_RESULT_03.md`(Z Adv節・手順)、`docs/research/KP-CANDIDATE-PHRASE7-WORD5-PRODUCTION-01/EVIDENCE_RESULT_*.md`(Z Std run名)、`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/EVIDENCE_RESULT_05.md`(Z節)、Z runner(Grep `stale|downstream|regenerate-stage|kp_a2|provision_shell` ±10)、`er128_kp_confirmed_content_01.py`(Grep `def cmd_from_form|actor|grammar_pending` ±10)。

## 報告

`RESULT_PACKET_KCP4.md`: (0)T-0、(1)go/no-go、(2)evidence表、(3)費用、(4)不具合(あれば)、(5)判断候補、(6)必須4行+「判定整合」、(7)SSOT文案(OPEN-556 6経路Status)、commit hash・raw URL。末尾5行要約。