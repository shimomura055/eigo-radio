# PUBLIC_REPLACEMENT_01: 『告げ口心臓』最終試聴ページをChunk分割版(run_chunk_01)へ差替え(委任_05/06、2026-10-25、API 0・Production code変更0)

ユーザー指示原文: `docs/pm/delegation_log/2026-10-25_FZ-TELL-TALE-HEART-CHUNK-FINAL-01_USER.md`。公開URL: https://shimomura055.github.io/eigo-radio/user_test/family_z_tell_tale_heart_01/index.html 。Status=**USER_LISTENING_PENDING**(試聴PASSは未取得・先取りしない)。

## 8点確認
| # | 項目 | 結果 | 根拠 |
|---|---|---|---|
| 1 | Std/Advとも正式完成音声 | 成立 | 公開dir58ファイルは候補ページ`user_test/family_z_tell_tale_heart_chunk_01/`と**全58本sha256一致**(html3本含む、差分0)。由来=`er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_chunk_01`(`e2e_stage_log.jsonl`の assemble→pages→page_verify、spent 16.6657円不変=今回API 0)。Gate: b1b/a2とも`audit/gate_result_04C.json` shared_gate=PASS・audio_text_deviations 0、`audit/tts_generation_results.json` 全segment status=OK(a2 19/b1b 22)、`audit/review_lock_state.json` RESOLVEDのみ(Human Review Lock 0) |
| 2 | AdvのB_r1適用 | 成立 | `b1b/audit/chunk_plan_b1b.json`: full_story_part2_c1=[58,62](_k1/_k2)、full_story_part3_c1=[65,61](_k1/_k2)、boundary_kind=paragraph、extra_pause_seconds=0.2。`b1b/assembly/timeline.json` `chunk_tts` |
| 3 | Stdは承認済み仕様どおり | 成立 | a2はChunk化なし(`a2/assembly/timeline.json` chunk_tts=無し、segment名に`_k`無し)、19 entry全OK、shared_gate=PASS(`a2/audit/gate_result_04C.json`)。a2 full=291.28秒 |
| 4 | 案A一人称・語り口保持 | 成立 | 公開advanced.html/standard.htmlのscriptセル(日本語セル除外)の語列を`writer/r2.md`/`writer/std.md`の段落と照合: **Adv 22/22段落一致・Std 22/22一致**。一人称(I/my/me)を含む段落 Adv 17/22・Std 18/22、聞き手youの段落 Adv 6・Std 5。冒頭Adv「You call me mad.」・Std「You think I am mad…」、結末は「…beating of his hideous heart!」/「…horrible heart!」。`housemate`は3ページとも0。`narrator`の4件はAdvのCharon英文preview/commentセル(「A narrator insists…」等、旧公開版にも同数4件の既存、本文ではない) |
| 5 | 0.2秒ポーズ | 成立 | `timeline.json` chunk_tts gap: 188.516〜188.716秒(part2)・249.376〜249.576秒(part3)。公開`audio_advanced/TellTaleHeart_b1b_full.mp3`をデコード(soundfile)し長さ**280.600秒**(timeline 280.6)、gap内max\|x\|=0.0004/0.00001(≤0.001)、前後±0.1秒を含めても≤0.0025。元wav(run_chunk_01/b1b/assembly)も同様(0.0004/0.0) |
| 6 | script・音声・パート再生一致 | 成立 | `run_chunk_01/page_verify_local.json`(15:06更新): index/standard/advanced の plays_failed=[]・console_errors=[]・http_ge400=[]、plays_ok=34/26/24、`user_page_standard_check` PASS。`seek_ok_all=false`はhttp.serverがRange非対応のための既知偽陰性(`er026_family_z_fiction_production_runner_01.py:2073`)。実Rangeは公開URLで確認(下記8) |
| 7 | 古い非分割音声が混在しない | 成立 | 差替え前一覧(58)と候補一覧(58)は同一path集合(旧のみ0・新のみ0)。退避dir内の旧58ファイルとsha一致する公開ファイルは**0本**(全58本変化。旧run_sf_prod_02由来なし) |
| 8 | 公開URLの全音声・Range・page_verify | (push後に下記へ追記) | |

追加: Part 1(Vocabulary & Expressions)blockは**index.html**に1つ(`<section class='study'>`=1、Advanced文由来の語句)。advanced.html・standard.htmlには0(従来から同blockはindexのみ)。Standardに無い点は成立。旧公開index.htmlには無かった。

## 退避・復旧
- 退避(差替え前58ファイル、Git外): scratchpad `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\d5\backup_tell_tale_heart_01_20261025_150429\`
- 差替え前の恒久記録: Git上のcommit `5f3e7dc15`(FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_04、run_sf_prod_02公開版)。
- 復旧手順: (a)退避dirを`user_test/family_z_tell_tale_heart_01/`へコピー、または(b)`git show 5f3e7dc15:user_test/family_z_tell_tale_heart_01/<file> > user_test/family_z_tell_tale_heart_01/<file>`(全58ファイル)。
- 変更ファイル要約: `user_test/family_z_tell_tale_heart_01/`のadvanced.html/standard.html/index.html(Part 1 block追加含む)と`audio_advanced/*`(27本)・`audio_standard/*`(28本)+html3=全58本が新sha。pathの増減なし。
