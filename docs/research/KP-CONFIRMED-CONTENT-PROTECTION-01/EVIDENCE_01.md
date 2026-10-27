# KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02B Evidence(総括 EVIDENCE_01)

ユーザー確定ではなく、既存の確定済みrunの**コピーdir**上で `confirm --from-form --actor evidence` により確定レコード(actor=evidence、記録に「ユーザー確定ではない」と明記)を作り、保護の挙動を実測した。元run・公開済み成果物は変更していない。
保護の強度はactor=userと同じ(`ENFORCING_ACTORS`)。上限は EVIDENCE_COLLECTED(PRODUCTION_WIREDではない)。

置き場: `docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/evidence_runs/{x,y,z}/`(ログ・JSON)、道具は `tools/`(`kcp2b_ev_01.py` payload/g1、`kcp2b_ev_matrix_01.py` 改変マトリクス、`kcp2b_ev_ops_01.py` STALE/resume/操作ガード、`kcp2b_ev_part2_01.py` Part 2 MODEL patch、`kcp2b_ev_m2b_01.py` Std表示、`kcp2b_ev_public_g3_01.py` 公開ページG3、`kcp2b_ev_lr_agg_01.py` LR集計)。
コピーdir: `er128_output/evidence_01/{x,y,z}/`(gitに載せない。Y/Zはrunner固定のrun rootへNTFS junctionで接続していた→終了時にjunctionのみ撤去)。

## 1. 実測結果(Family別の詳細は EVIDENCE_X_01 / Y_01 / Z_01)

| 項目 | X | Y | Z |
|---|---|---|---|
| (a) form payload v2(schema_minor:1)→confirm(actor=evidence)→下流 | a2/b1b確定OK→tts(a2)/assemble/player rc=0、G1〜G4通過 | a2/b1b確定OK→G1 PASS。runner下流は不可(限界参照) | b1b(文法つき)確定OK→kp実run rc=0→provision_shell,gate,assemble,pages,page_verify rc=0 |
| (b) 改変 G1(英語/日本語訳/vocab訳/category/assets copy) | BLOCK(INTEGRITY) 全件 | BLOCK 全件 | BLOCK 全件 |
| (b) G2(TTS英語・日本語) | BLOCK | BLOCK | BLOCK(英語。a2は旧run=レコード無し) |
| (b) G3(ページ日本語訳 / Part 1行) | BLOCK / BLOCK | BLOCK(a2ページ) / —(Part 1無し) | — / BLOCK(Part 1行) |
| (b) G4(解説全文/日本語訳/選定文) | BLOCK 3件 | —(Part 2無し) | BLOCK 3件 |
| (c) resume(同一本文) | FINALIZED・レコード不変・生成API 0 | 同左 | 同左 |
| (c) STALE 再バインド(出典文以外の本文変更) | revision 1→2、content_sha256不変、API 0、G1 PASS | 同左 | 同左 |
| (c) STALE ISSUE(出典文変更) | PENDING `confirmed_content_issue`、レコード不変 | 同左 | 同左 |
| (c) `--regenerate-stage` | (Part 2再抽出はfunction levelでrevoke必須を確認) | — | `part2_cand_b1b` → LOCKED拒否・API 0・レコード不変(実runner)。`kp_b1b`は RESTART_STORM自己発動のため未実施 |
| (d) 操作ガード(select/reselect/ng/resolve-gloss/declare-absent/再confirm) | 全て CONFIRMED_CONTENT_LOCKED | 同左 | 同左 |
| (e) ISSUE rc=4 | STALE ISSUEで実測(上段)。provisional glossのconfirm→ISSUEは単体test | 同左 | 同左 |
| (f) Part 2 MODEL patch | extract 0 / explain 0、凍結 frozen:a77260c1f0478ee5 | —(Part 2無し) | extract 0 / explain 0、frozen:39ca140a69483f6d |
| (g) 公開URL G3(read-only) | — | PASS(sns_age_limit 公開ページ、確定3訳が表示) | BLOCK(公開 melos kphr_evidence_r3 は旧訳「水中に引きずり込む」、コピーの現候補doc訳は「誰かを水中に引きずり込む」=旧公開ページと現docの差を検出) |
| (h) Std「～」gloss表示 | — | mock/単体test PASS | 実Z 3 runで表示用gloss=「～…」、TTS入力不変(40_m2b_std_display.txt) |
| 実改変STOP(runner) | `--stage player` rc=3(`CONFIRMED_CONTENT_INTEGRITY_VIOLATION`) | `tts_a2`はrunnerの旧run前提(style_profile.json未作成)で別理由停止=未到達 | `--stages gate` rc=2(FamilyZ既存のSTOP写像。`load_level_inputs(b1b)`で`CONFIRMED_CONTENT_INTEGRITY_VIOLATION`) |

## 2. LR重なり(API 0)
`evidence_runs/lr_overlap_aggregate.json`: 既存のLR解決記録28件のうち run のKPと対応づけられた18件で、確定KP語と重なるLR書換えは 0件(0.0%)。残り10件は記録のpathからrunを特定できない。LRの挙動は不変。

## 3. M2-b(既存記事の表示変更一覧)
`evidence_runs/m2b_scan.txt` `m2b_scan2.txt`: repo内のY/Z a2 TTS結果44件を走査。「表示用gloss≠TTS用canonical_text」となるのは、ZのMelos試験run 4件(gloss整合の試験でrank対応がずれた記録。公開記事ではない)のみ。「～」を含むglossを持つ既存Z run(after_twenty_years/run_sf_prod_01、the_monkeys_paw/run_fzcw_e1_01・e1_02・run_sf_prod_01、the_open_window/run_e2e_01)は、TTS側のcanonical_textも「～…」で保存されており、再構築しても表示は変わらない。**再構築で表示が変わる公開済み記事: 該当なし(走査範囲)**。公開済みかどうかの正本リストはrepo内に無いため「公開状態は未確認」。

## 4. 実モデル・routing・費用・所要
COST_01.md。X: Gemini TTS `gemini-3.8-flash-lite-tts`(voice Aoede)、ASR=OpenAI+Azure、¥7.39。Z: `gpt-6-luna`(Redundancy QA 1 call)、¥0.0596。Y: ¥0。合計 約¥7.45(上限¥30)。

## 5. 発見した不具合と是正(同一委任内)
1. M8の出典文照合が曲線引用符(’)で不一致になりISSUEに倒れる(fail-closedだが誤検出)→ `_norm_ws` を NFKC+引用符正規化に是正、test追加。実Xの a2 で検出。
2. Z/Yの `part2_cand_b1b` 来歴がmodel変更で親sha不一致STOP→`--regenerate-stage`はrevoke必須で拒否され解消不能になる→確定済み文法では記録済みinput_shaを据え置く `cand_input_sha`、test追加。
3. 自分のevidence対照(保護OFFでPart 2候補を再抽出)が実コピーの`grammar_candidates.json`を`SUPERSEDED_N`へ退避した→`SUPERSEDED`から元へ戻し、対照は使い捨てコピーに変更(実成果物は復元済み、diff確認)。
