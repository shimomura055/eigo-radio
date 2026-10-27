# KP-CONFIRMED-CONTENT-PROTECTION-01 委任_03 Evidence(総括 EVIDENCE_02): 6経路 × Std/Adv

到達上限=EVIDENCE_COLLECTED(PRODUCTION_WIRED判定はFable)。確定レコードの actor は全て `evidence`(ユーザー確定ではない。保護の強度は user と同じ)。全て**コピーdir**上の実測(原本・公開済みは不変、HR Lock不解除、TTS再生成0)。
経路別の詳細: EVIDENCE_X_02 / EVIDENCE_Y_02 / EVIDENCE_Z_02。02Bの結果(EVIDENCE_01/X_01/Y_01/Z_01)は再実行せず統合(「02B」と表記)。

凡例: ○=実runner実測 / ○f=関数レベル(実artifact)で実測、実runner段は別欄 / ×=不成立・停止 / 未=未観測。

| 項目 | X-Std(a2) | X-Adv(b1b) | Y-Std(a2) | Y-Adv(b1b) | Z-Std(a2) | Z-Adv(b1b) |
|---|---|---|---|---|---|---|
| 確定→下流の実走 | ○ 02B(tts/assemble/player rc=0) | ○ study_text/assemble/player rc=0, API 0 | ○ kp→assemble→pages→page_verify rc=0。**gate=×(preview HR Lock。保護外の理由)** | ○ 同左(Part 1/Part 2も通過) | ×/未: a2通しはTTS KP5件≠確定3件でSTOP(旧run。現行KP3のa2 runは現存せず) | ○ 02B(kp→gate→…→page_verify rc=0)+今回b1b側は同様に通過 |
| 改変BLOCK G1(英語/訳/区分/assets) | ○f 02B | ○f(英語/訳/vocab訳/category) | ○f(英語/訳/category/assets copy) | ○f(+vocab訳) | ○f(英語/訳/category) | ○f(+assets copy訳) 02B+今回 |
| G2(TTS英語/日本語) | ○f 02B | ○f(英語)。**復唱 phrase_repeat 漏れを発見→是正** | ○f(英語/日本語) | ○f(英語) | ○f(英語/日本語) | ○f(英語)02B+今回 |
| G3(ページ/Part 1行) | ○f 02B | ○f(Part 1行) | ○f + **○ runner(page_verify rc=2)** | ○f(Part 1行) | ○f(**any-ofの弱点 D3**) | ○f(Part 1行) |
| G4(Part 2解説/訳/選定文) | —(Stdに無し) | ○f(3件) | —(Stdに無し) | ○f(3件)+**○ runner(`pages` rc=2)** | — | ○f(3件)02B+今回 |
| 実runnerの改変STOP | ○ 02B(player rc=3) | ○ player rc=3 | ○ `page_verify` rc=2(G3)/ `kp` rc=2(G0) | ○ `pages` rc=2(G4)/ `kp` rc=2(G0) | ○ gate rc=2(a2) | ○ gate rc=2(02B) |
| resume / STALE再バインド / ISSUE | ○f 02B | ○f(FINALIZED/rev1→2/PENDING) | ○f | ○f | ○f | ○f |
| 操作ガード(select/reselect/ng/resolve-gloss/declare-absent/再confirm) | ○f 02B | ○f LOCKED | ○f LOCKED | ○f LOCKED | ○f LOCKED | ○f LOCKED |
| `--regenerate-stage` の扱い | —(Xに無し) | — | —(KP regenerateは未観測) | ○ `part2_cand_b1b` LOCKED rc=2 API 0。**`kp_b1b` は未観測**(他Agent WIPで停止、D6) | — | `part2_cand_b1b` LOCKED(02B)。`kp_b1b`: **rc=0・無害な再finalize**(拒否ではない) |
| 公開URL G3 | — | — | ○f 02B PASS(sns_age_limit) | 同左 | — | **PASS**(index.html)。02Bの「旧訳」記述は誤り(advanced.htmlは詳細ページ) |
| API費用(本委任) | ¥0 | ¥0 | 約¥0.64(Y y_01+y_02 Redundancy QA) | 同左 | ¥0.07(Z合計) | 同左 |
| 未観測 | — | — | gate通過後(HR Lock未解除)/ a2 `kp_a2`再実行 | gate通過後 / `kp_b1b`再実行 | 実runner通し(現行a2 runが無い) | — |

## 発見した不具合・観測(詳細は RESULT_PACKET_KCP3.md §3/§5)
- D1(Y/Z runner・所有外): 自動採用(UNREVIEWED_AUTO_ADOPTED)runへ後から確定を入れると kp来歴の入力shaがずれて親sha不一致STOPになる。`--regenerate-stage kp_<lv>` で解消すると子孫(tts)がstale化=TTS再生成コストに波及する恐れ。
- D2(er128・是正済み): G2が `phrase_repeat`(KP復唱)を見ていなかった。
- D3(er128・低): Std G3 は「複数ページのどれか1つに出ていればよい」(Zのindex+standard)ため、片方のページだけの改変は止まらない(ページは同一builderが全て再生成するため実害は小さい)。
- D4(Y/Z runner・所有外): 拒否された `--regenerate-stage part2_cand_b1b` が `part2_failed.json` を書き、その「次の一手」が拒否されたコマンドと同一(ループ)。
- D5(02B記述の訂正): Z公開URL G3のBLOCKは検査ページの取り違え。
- D6(他Agent干渉): GRAMMAR-PREGEN-ALL-LEVELS-01 の`er120`/`er119_grammar_review`編集中(`level`必須引数化)に当たり、runner経由の一部起動とer128 test 12件が一時的に落ちる(本委任の変更とは無関係)。
