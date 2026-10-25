# RUNTIME_EVIDENCE_02: 『告げ口心臓』run_sf_prod_02(案A配線後の正式再生成、FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_04)

2026-10-25 JST。Status候補=`WIRED_PENDING_FABLE`(案A) / `COMPLETE_USER_LISTENING_PENDING`(OPEN-503、run_sf_prod_02)。**ユーザー最終試聴PASSは未取得・先取りしない。** 設計=`docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/WIRING_DESIGN_02.md`。run dir=`er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_02`。

## 1. Production経路であること(Opus必須修正3-c)
- git HEAD(run時点の作業tree基準)=`94ab3e16f`(他agentのcommit混在。**Z writerを変更したcommit=`53ce7b397`**、`git log -1 -- er062_family_z_writer_01.py`)。`git diff --quiet HEAD -- er062_family_z_writer_01.py` rc=0=**runに使ったwriterはcommit済みHEADと一致**(未commit変更なし)。
- `er062_family_z_writer_01.py` file sha256=`09ab196258ad6664dc7783ca5e18f9fab0b847fb64c6d5e7d9d7fb4111d1b248`。
- 起動はProduction正式runner `er026_family_z_fiction_production_runner_01.py --story the_tell_tale_heart --run run_sf_prod_02 --mode real --approved-budget-jpy 80 --tts-execution-mode STANDARD`(DEV runner `fz_essence_dev_runner_01`は使用せず。fail-fast guardにより案A昇格後は起動不可、`test_historical_dev_runner_fail_fast_guard`で固定)。本番コードからDEV runnerへの参照0(`test_no_dev_runner_reference_from_production`)。
- 起動(`run_launch_log.jsonl`): ①10:35:57 `seed_check,writer,std_adjust` ②10:42:17 `plan,support,kp` ③10:47:42 `tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify`(1起動、OPEN-480準拠)。**起動3回・再起動0**、起動間隔5分以上(②→③ 5分25秒)、RESTART_STORM/`STOP`/`RUN_LOCK`異常なし。各起動直前`stop_scope_check_01` rc=0(`FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01`、結果json=scratchpad保管)。

## 2. 「dumpされたPrompt=実際に送ったPrompt」(Opus必須修正3-a/b)
(a) r0/r1/r2/std_adjustの4段は**新run dirで実際にLLMを呼んだ**(chain各entryのattempts=1・cost_jpy>0・`ensure_stage`のreused/skipではなくrunner経由。r0〜r2の本文は旧run_sf_prod_01と異なる新規出力)。(b) 各`writer/<stage>_prompt.txt`から`sha((dev or "") + "\n\n---\n\n" + user)`を再計算(r1/r2のdumpはdevも区切りも含まないため`"" + "\n\n---\n\n" + dump`)し、`provenance.json`の`prompt_sha256`と照合:

| stage | status | model / routing_key | provenance prompt_sha256 | dumpから再計算 | 判定 | Narration行 | `in the narration described…` | `in third person` |
|---|---|---|---|---|---|---|---|---|
| r0 | generated(attempts=1、cost_jpy=2.5722>0=LLM呼出あり) | gpt-6.1-sol / FAMILY_Z_WRITER_ADV_R0 | `4b91942a06092af5…` | `4b91942a06092af5…` | 一致 | 1 | 0 | 0 |
| r1 | generated(attempts=1、cost_jpy=2.8243>0=LLM呼出あり) | gpt-6.1-sol / FAMILY_Z_WRITER_ADV_R1 | `904c94e12cf84f52…` | `904c94e12cf84f52…` | 一致 | 1 | 1 | 0 |
| r2 | generated(attempts=1、cost_jpy=5.3408>0=LLM呼出あり) | gpt-6.1-sol / FAMILY_Z_WRITER_ADV_R2 | `0d20309bc82e9f03…` | `0d20309bc82e9f03…` | 一致 | 1 | 1 | 0 |
| std_adjust | generated(attempts=1、cost_jpy=6.5027>0=LLM呼出あり) | gpt-6.1-sol / FAMILY_Z_STD_ADJUST | `e2a4d927f01a9954…` | `e2a4d927f01a9954…` | 一致 | 1 | 0 | 0 |

- `essentials_sha256`(全段共通)=`5e74e34b91d62391e74b08c04b35c8d332deefc3a1ef542076324a0581a0432c`、`source_essentials_sha256`(top-level)=同値、`seed_sha256`=`355a317a9b18fc7b952ba1b23d6180279b799d629d9945d03d924b5234a2eaaa`(新Seed `355a317a9b18…`)。`narration_voice`自体はessentials shaと各Prompt dump、`writer/cp_checklist.md`#9で追跡できる(新しいログ機構は追加していない)。
- requested_model=actual_model_id=`gpt-6.1-sol`(4段とも。Production writer指定どおり、effort=Production既定)。
- **REVISE文言Grep**: R1/R2 dump に `in third person` = **0件**、`in the narration described in the Must-keep section below,` = 各1件。R0/Stdにも`in third person`0件。
- seed_check: `validate_source_essentials`がfail-closedで通過(`narration_voice`必須検査を含む)。**注記**: runnerの`e2e_stage_log.jsonl`は結果の**キー名のみ**(`result_keys`に`source_essentials`)を記録し、辞書の中身は残さない(runner無変更)。したがって「seed_check stage logにnarration_voiceが残る」とした設計(WIRING_DESIGN_01 §1 W5)は不正確で、実際の追跡経路は上記(essentials sha/Prompt dump/cp_checklist)。W5自体は戻り値へ`narration_voice`を含める(`test_validate_returns_narration_voice_for_stage_log`)。

## 3. CP(writer/cp_checklist.md)とGuardrail
- `cp_checklist.md`#9 重大/narration行に`narration_voice`が記載(処置規則(A)にnarration追加済み)。判定欄はFable記入(Sonnet所見=`COMPARISON_03.md`末尾)。
- Guardrails: r2 failures=[]、std_adjust failures=[](WARN `STD_AVG_SENT_LEN_NOT_SHORTER 8.39 vs adv 5.55`のみ)。語数 r0 424 / r1 430 / r2 411 / Std 428、段落数 Adv22/Std22一致。`housemate`/`narrator`は本文0件。
- 本文抜粋(一人称'I'・聞き手'you'・結末)=`COMPARISON_03.md`。

## 4. 音声(TTS)・Gate
- TTS: backend=`speech_metadata_flash_lite`(Production正式)、style_version=`z_v2_pd8_r2_e1_e2up_k2_m2_kpx_20261012`。model: narrator全clip=`gemini-3.8-flash-lite-tts`(Adv10/Std11 call)、老人台詞(`Who's there?`)=`gemini-2.5-pro-preview-tts`(各1 call)。voice: narrator=Aoede(story本文)、old_man=Algieba、導入/KP番号等=Charon(正式Voice表+決定的割当、pinなし)。style: story本文=PD06(Adv/Std)ほか(既存Production資産)。
- 全segment status=OK(Adv18/Std19)、**attempts=1(再試行0)**、review_lock_state=全RESOLVED(**Human Review Lock 0件**)、`approve_regenerate`未使用。Gate(`shared_gate`)=PASS(Adv/Std)、`audio_text_deviations`=[]。極短clip等の速度Gate(m1_slowdown)はStd 5 clip・Adv 1 clipで適用(既存Production機構)。
- PASS_WITH_WARNING: Std `japanese_title`(「告げ口心臓」を一次ASRが『すげぐ心臓』、二次`secondary_confirmed`)1件=旧run_sf_prod_01と同一条件(既存Gateどおり。試聴確認項目)。
- 尺: Advanced(b1b)全編273.9秒 / Standard(a2)全編291.7秒。

## 5. 公開・page_verify
- `user_test/family_z_tell_tale_heart_01/`(index/standard/advanced.html + audio_standard 28 + audio_advanced 27 mp3)を`pages`段が再生成。旧版はscratchpadへ退避済み(退避→再生成)。**旧58ファイルと新58ファイルのsha一致=0(全ファイルがrun_sf_prod_02由来、旧ファイル残存0)**、ファイル集合は旧新で同一(欠落・余剰なし)。`housemate`: advanced/standard/index.htmlとも0件。
- `page_verify_local.json`(runner、Playwright): index/standard/advanced HTTP200、console_errors=[]、plays_failed=[]、`user_page_standard_check` overall=PASS(seek_ok_allはrun_sf_prod_01と同じfalse=既存仕様)。**公開URL検証(push後、GitHub Pages反映は約8〜10分遅延)**: `https://shimomura055.github.io/eigo-radio/user_test/family_z_tell_tale_heart_01/{index,standard,advanced}.html`=HTTP 200、`housemate`0件、advanced.htmlに新本文『You call me mad.』を確認。audio_advanced 27 + audio_standard 28 の計55 mp3を公開URLから取得しlocalのsha256と全件一致(不一致0)。
- 一人称'I'/聞き手'you'の本文引用=`COMPARISON_03.md`の「公開ページ本文からの引用」(Fable目視用。自動判定なし)。

## 6. 費用(実費)
`BUDGET_LOG_01.md`の「委任_04 再生成」節。合計34.64円(概算約40円以内、`--approved-budget-jpy 80`の43%)。
