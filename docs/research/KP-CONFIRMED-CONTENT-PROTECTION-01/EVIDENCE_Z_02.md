# EVIDENCE_Z_02(Family Z Std/Adv。コピーdirで実測。委任_03)

コピー元: `er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3`(02Bと同じ。b1b=KP review・Part 2あり、a2=旧run)。コピーdir: `er026_output/family_z_production_e2e_01/melos/run_kcp3_ev_z_01`(runnerのrun root直下へ実コピー、junction無し。完了時に `C:\Users\tensh\kcp3_evidence_copies_20261027\z\` へ退避)。**TTS再生成なし**。

## Std(a2)の制約(重要)
現存するZ runのa2は全て旧run(KP Human Review導入前・KP5件)で、現行仕様(KP最大3+vocab最大5)のa2 runは存在しない(`key_phrases/a2/kp_human_review.json`を持つZ run=`kp75/kpbf/kprescue`は候補のみでTTS無し)。Z runnerは旧runのa2を再選定せず「旧run互換」で再利用する(`_kp_legacy_run`)。
そのため a2 は次の方法で保護下に置いた: (i) `tools/kcp3_ev_z_a2_seed_01.py` で既存a2 KP成果物を「候補生成の結果」として注入し review(候補+PENDING)を作成(API 0。実runnerが新記事で行う候補生成→pendingの再現)、(ii) 先頭3件でフォーム確定(KPは最大3件のため。旧runは5件)、(iii) `--stages kp`(Redundancy QA実呼出)でfinalize。kp_a2来歴は`tools/kcp3_ev_z_rebind_01.py`で付け替え(D1と同じ事情)。
このため **a2 の runner 通し(gate〜page_verify)は旧TTSのKP5件が確定3件と一致せず `FAMILY_Z_KP_SELECTION_OUTPUT_MISMATCH(a2): TTSのKP件数(5)が確定KP(3)と一致しません` で停止する**(07_stages…txt)。新規のZ Std生成(TTS)は¥20 Cap・TTS再生成禁止に抵触するため行わず、Std の実runner通しは未観測とする。

| # | 手順 | 結果 | 証跡(`evidence_runs/z2/`) |
|---|---|---|---|
| a | b1b: payload(KP3+文法`g50e12a388f`)→`confirm`→`--stages kp`(real) | rc=0。spent 5.7398→5.7423(Redundancy QA 1 call) | 01_confirm_form_b1b.txt, 03_stage_kp.txt |
| a | a2: seed→3件確定→`--stages kp`(real) | rc=0。G1 PASS。spent →5.8058(Redundancy QA 1 call。本委任のZ合計 ¥0.066) | 04_a2_seed.txt, 05_*, 06_stage_kp_a2.txt |
| b | `--stages provision_shell,gate,assemble,pages,page_verify --pages-dir <copy>/pages_ev`(1起動) | b1b側は通過、**a2のKP件数不一致でSTOP**(上記)。追加API 0 | 07_stages_gate_to_page_verify.txt |
| c | 改変マトリクス(a2・b1b) | a2 G1: 英語/訳/category、G2: TTS英語/日本語 → BLOCK。a2 G3: `standard.html`のみ改変は**PASS(止まらない)**(D3)、`index.html`+`standard.html`両方改変でBLOCK。b1b G1〜G4 全てBLOCK | 10_tamper_matrix.{txt,json}, 11_z_std_g3_pages.txt |
| c' | 実runner(Std): a2 assets copyの訳を改変→`--stages provision_shell,gate` | **rc=2** `FAMILY_Z_KP_REVIEW_INCONSISTENT(a2) at load_level_inputs(a2): CONFIRMED_CONTENT_INTEGRITY_VIOLATION … 確定=水中に引きずり込む 観測=…改変`。API 0 | 09_rt_tamper_a2_gate.txt |
| d | resume / STALE再バインド / ISSUE(a2・b1b) | 両方 FINALIZED / revision 1→2・G1 PASS / PENDING・不変 | 20_ops.{txt,json} |
| e | 操作ガード(a2・b1b) | 全て LOCKED | 20_ops.txt |
| f | Adv: `--stage kp --regenerate-stage kp_b1b`(実runner。1起動) | **rc=0・API 0・拒否ではない**: 確定レコード/review選択集合/署名/revision(8)は不変、`downstream_stale` は空。再実行は確定値で再finalizeするだけで確定内容を変えない(`status`・G1 PASS)。委任文の「拒否」想定とは異なり **LOCKED拒否ではなく無害な再finalize** | 08_regen_kp_b1b.txt, 08a_after_regen_state.txt |
| f | Adv: `part2_cand_b1b` | 02B(`evidence_runs/z/12_regen_part2_cand.txt`)で LOCKED rc=2・API 0 を実測済み。再実行せず統合 | 02B |
| g | 公開URL G3(read-only、取得: `…/user_test/family_z_melos_kphr_evidence_r3/{index,advanced,standard}.html` すべてHTTP 200) | **index.html: PASS**(確定3訳が表示)。`advanced.html`: BLOCK だがこれは利用者向けページ(index.html)ではなく詳細確認ページで **Part 1を描画しない**ためで、保護の欠陥ではない。→ **02Bの「旧公開訳≠現doc」という記述は誤り(検査対象ページの取り違え)**。根拠: 公開index.htmlは候補doc訳「誰かを水中に引きずり込む」を表示、repoの `user_test/family_z_melos_kphr_evidence_r3/index.html`(commit `81e70d4f0` 2026-10-26 00:14:46+09:00で公開)とCRLF差のみで一致、候補docは2026-10-25 21:17生成・訳の改訂履歴なし | 50_public_g3_pages.txt, _pub_z_*.html |
| h | Std「～」gloss表示 | 02B(`evidence_runs/z/40_m2b_std_display.txt`)で実測済み | 02B |

## 結論(Z)
Adv(b1b): 確定→kp→gate〜page_verify(02B)・改変BLOCK・STALE・guard・`part2_cand`LOCKED・`kp_b1b`再実行無害を実測。公開URL(index)もPASS。Std(a2): 関数レベルのG1〜G3と実runnerの改変STOPは実測、**現行仕様のa2 run(KP3)が現存しないため通しは未観測**(Z Std生成が必要=Cap外)。
