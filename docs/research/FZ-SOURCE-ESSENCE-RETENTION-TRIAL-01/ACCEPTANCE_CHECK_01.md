# ACCEPTANCE_CHECK_01: Fable受入前の確認(委任_05、2026-10-25、read-only中心・API 0・Production変更0・公開ファイル変更0)

## 確認1: 公開Standardページの本文 -> 結論 (a)
**COMPARISON_03のセル抽出の不具合。公開Stdは正しい(run_sf_prod_02の最終Std本文)。**

原因(推定、再現確認済み): Standardの本文セルは`<div class='voice'>…</div><div class='note'>6%減速適用(比 1.0595)</div><div class='script'>英文</div>`で、Voice行とscriptの間に日本語の`note`が入る。旧抽出は「日本語を含むセルを除外」する条件だったため本文セルを全て落とし、Advanced(noteなし)だけ拾えた。Standardの結果(0件)が誤り。同じ抽出器でnoteを無視して再計測した値は下表。COMPARISON_03の該当節は修正済み。

### 取得物の一致
| 項目 | 結果 |
|---|---|
| local `standard.html` vs 公開URL | CRLF(作業tree)を除くと**byte一致**(standard/advanced/index 3ページとも) |
| 本文(narration 6セル)の正規化語列 vs `run_sf_prod_02/writer/std.md` 本文 | local・公開とも **435語=435語で完全一致** |
| 段落単位(std.md 22段落を語列で順に照合) | **22/22 MATCH**(下表) |
| 語数/一人称/you(本文セル、`I/my/me/I'm`・`you`) | 432語/47/6 (std.md全体 440語/47/6。差=タイトル行5語+引用符・省略形の語分割差) |
| 冒頭 | 「You think I am mad, but I am only nervous.」(std.md冒頭と一致) |
| 結末 | 「"I killed him!" I screamed. "Pull up the floorboards here! That is the beating of his horrible heart!"」(一致) |
| `housemate` | index/standard/advanced 全て0 |

段落一致: 1(35語)〜22(18語)の22段落全てMATCH(語数: 35,45,30,7,20,20,6,24,11,5,22,30,20,19,41,9,19,10,18,7,19,18)。ページは22段落を6セルに連結して表示(c1=段1-2, c2=段3-6, c3=台詞, c4=he shouted, part2=段8-14, part3=段15-22)。

### 音声(audio_standard、28ファイル)
- **local 28本 = 公開URL 28本 sha256全件一致**(Std全28本を含む。委任_04の「55本一致」=Std28+Adv27)。
- **run_sf_prod_02のassembly出力との一致**: `a2/assembly/Family_Z_the_tell_tale_heart_a2.wav`を`soundfile`でMP3化すると`TellTaleHeart_a2_full.mp3`と**bit一致**。`timeline.json`の24パートで切り出し再エンコードした結果が`a2_00〜a2_23`と**24/24 bit一致**(a2_20=a2_p2、a2_22=a2_p3と同一、a2_p1=part1_c1〜c4の連結)。つまり公開Std音声28本は全て今回のrun_sf_prod_02 Std wavに由来(旧run_sf_prod_01音声ではない。なお5f3e7dc15で全mp3のサイズが変更されている)。
- index.html: `standard.html`/`advanced.html`の詳細リンクは正しい(`#std`節=audio_standard、`#adv`節=audio_advanced+補助節のStd WARNリスト)。index本文に`You think I am mad`(Std)と`You call me mad`(Adv)が両方あり`housemate`なし。

## 確認2: Std guardrail WARN `STD_AVG_SENT_LEN_NOT_SHORTER`
- 定義(`er062_family_z_writer_01.py:56,610-611`): `STD_AVG_SENT_FACTOR=0.85`、Std平均文長 > Adv平均文長×0.85 でWARN(**soft gate**、`failures`には入らない)。failure閾値は別で、`STD_IDENTICAL_FAIL=0.50`(同一文率)と`STD_NO_TITLE_LINE`のみ。WARN時の再生成/STOPはない(語数・段落数WARNと同様)。
- Family X A2(CURRENT_SPEC 552-553行): 平均文長11語以下・最長18語以下は「生成方針、機械的gateとしては未実装」。語彙は定性方針のみ(厳密なCEFR語彙上限/wordlistは意図的に設けない、`REJECTED`)。Z固有のA2語彙指標は無い。
- 発生履歴: **Z全6作品(最終版)でWARN発生**(Adv平均文長が短いほど発火しやすい。仕様上は常態)。

| 作品/run | Std 平均文長 | Adv 平均文長 | 閾値(Adv×0.85) | Std最長 | Std 11語超の文数 | Std 8文字以上語の割合 | Std異なり語数 |
|---|---|---|---|---|---|---|---|
| 告げ口心臓 **run_sf_prod_02(今回)** | **8.39** | 5.55 | 4.72 | **11** | **0** | 4.8% | 232 |
| 告げ口心臓 run_sf_prod_01(旧) | 8.57 | 6.95 | 5.91 | 16 | 7 | 5.0% | 228 |
| 開いた窓 sf_prod_01 | 8.61 | 7.75 | 6.59 | 12 | 1 | 7.6% | 258 |
| 猿の手 sf_prod_01 | 7.08 | 5.73 | 4.87 | 19 | 9 | 3.1% | 235 |
| 賢者の贈り物 sf_prod_01 | 9.23 | 7.64 | 6.49 | 16 | 4 | 3.3% | 224 |
| Melos(run_e2e_03) | 8.87 | 6.79 | 5.77 | 14 | 3 | 2.7% | 227 |

所見(判断・修正はしない): 今回のWARNはStdが難しくなったのではなく、**Advが短文化(6.95->5.55)してWARN閾値が4.72まで下がった**ため。Std自体は旧Stdより平均文長8.57->8.39、最長16->11語、11語超の文7->0、語彙指標(8文字以上語率・異なり語数)もほぼ同等で、Family X A2の生成方針(平均11語以下・最長18語以下)も満たす。語数はStd435(目標330-470内)。測定は`st.avg_sentence_len`/`split_sentences`(文長)と語分割の簡易指標(本checkで算出、gate外)。

## 確認3: 回帰testの他agent起因分類の再現(clean worktree)
clean worktree=`git worktree add <scratchpad>/wt_fzse5 HEAD`(HEAD=0d8fe4cd6、作業後`git worktree remove --force`済み・残存0)。`.venv`のpythonをcwd=worktreeで実行(API 0)。注意: このrepoはcore.autocrlf=trueで、worktreeは全ファイルCRLF化されるため、sha固定の資産を読むtestは環境起因で落ちる(下表「worktree CRLF」)。該当資産だけLFで再checkoutして再実行した。

| test | 開発tree(委任_04記載) | clean worktree | 分類 |
|---|---|---|---|
| unittest `er053…StaticTests.test_w1_rf_queue_contract_referenced_only_by_entertainment_runner_after_c2` | FAIL | **FAIL** | **HEAD内commit起因**。`er115_fx_numeric_retention_trial_01.py`(FX-CORE-NUMERIC-RETENTION-TRIAL-01、最古commit 5c51184c9 以降の19828d7ff等、全て2026-10-25)がer053をimport。未commitではない。自分(FZSE)起因でない |
| unittest `er095…TestIsolation.test_not_imported_by_any_production_py_in_c1` | FAIL | **FAIL** | 同上(er115が許可リスト外でimport) |
| unittest `er064…ProductionUnchanged.test_no_tracked_py_or_template_modified` | FAIL | **PASS** | **未commit DEVファイル起因で確定**(clean worktreeは変更なし) |
| unittest `er064…MachinePatterns.test_sha_file`(補足) | PASS | worktree CRLFでFAIL->LF再checkoutで**PASS** | 環境起因(CRLF) |
| unittest `er095…TestArticleAReal`(補足、setUpClass) | PASS | worktree CRLFでERROR->対象2ファイルをmain側bytesにするとPASS(56 test中の失敗はisolation 1件のみ) | 環境起因(CRLF。commit済みblobは1622byte、作業treeは1632byte) |
| unittest `er003_test_bad` | 意図的fixture(集計外) | 本確認では未実行 | 既知(REGRESSION_BASELINE_01) |
| pytest `er103…TestInheritance` x3、`TestStoreGuard` x1(+`test_restored…`)=5件 | FAIL | **PASS(5件とも)** | **未commit DEVファイル起因で確定** |
| pytest `er103…TestEquivalenceW02::test_trial_replay_sc4…` | PASS | FAIL(`assert n >= 1`、n=0) | worktree限定(replay用の未追跡/CRLF資産が無く照合0件)。HEAD起因ではなく環境起因 |
| pytest `er104_kp_vote_wiring…test_AST_attempt_ctx_vote_flag_is_forwarded_from_strict_only` | FAIL | **FAIL** | **HEAD内commit起因**: `er103_ret_baseline_signature_01.py`(78a2c7c6e、2026-10-23 ASR-QUALITY PN 委任_04)の`kwargs_from_record`が許可リスト(er003/er006/er103_pnap)外 |
| pytest `er109_wiring_golden…` x3(X/Z/unset) | FAIL | **FAIL** | **既知OPEN-501**(帰属未特定)。本checkでは、8dd3d4d7e(RET実装)のProduction 5ファイルを^へ戻しても、ASR関連11ファイルを719de3adc(golden最終更新)へ戻してもFAILのまま=その2点は主因でない。FZSEの変更(er062 writer/Seed)とは無関係 |
| pytest `er109_xz_isolation…test_importers_of_scope_module_are_a_fixed_production_list` | FAIL | **FAIL** | **HEAD内commit起因**: assertion値に`er113_fx_paragraph_chunk_trial_01.py`(09b01a287/644d6e8e6)と`er114_fz_narration_chunk_trial_02.py`(94ab3e16f/e5ebe03bb)=他agentのDEV Trial scriptがscopeモジュールをimport |
| pytest `er109_xz_isolation…test_m3_scope_entry_call_sites_are_fixed_and_literal` | FAIL | **FAIL** | 同じtest class。呼出箇所のCounterが期待と不一致(上と同系統の新規DEV script起因と推定。個別の呼出元は未itemize) |

要約: 開発treeの14失敗(unittest 3+pytest 11)のうち、**未commit DEV起因で確定**=er064 1件+er103 5件。**HEAD内commit起因(clean worktreeでも再現)**=er053 1・er095 isolation 1・er104 AST 1・er109 golden 3(OPEN-501既知)・er109 isolation 2。いずれもFZSE(案A、er062_family_z_writer_01/Seed/narration_voice)の変更を参照しない。HEAD内の失敗の担い手commitは上表のとおり(FX-CORE-NUMERIC=er115、ASR-QUALITY PN=er103_ret_baseline_signature、FX-PARAGRAPH/FZ-NARRATION-CHUNK=er113/er114)。修正はしていない(Fableの再委任判断)。
