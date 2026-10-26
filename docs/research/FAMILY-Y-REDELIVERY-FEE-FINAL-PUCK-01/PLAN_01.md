# PLAN_01 — 完成版制作計画(委任_02用。FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_01、read-only・API 0)

到達上限Status=計画確定(PLAN_READY)。本計画は「現HEADで確認できた事実」(A)と「Y Voice配線完了後に再確認する項目」(B)を分ける。並行Agent(FAMILY-Y-VOICE-TABLE)の変更後コードは前提にしない(作業木の差分=`FIXED_VOICE_SLOTS["voice_1"]="Puck"`+`Y_DIALOGUE_VOICE_POOL`のみを確認、未commit)。

## A. 現HEADで確認できた事実

### A-1 制作方針の要点
- 再生成は **`y_voice_1`の2 segment(a2・b1b)のみ**(INVENTORY_01 §2)。他は全て再利用でき、現行Gateを実測PASS(INVENTORY_01 §4)。Comment 2削除は配線済み・追加実装不要(COMMENT2_WIRING_CHECK_01)。Preview再生成不要。
- **run dir方針: `run_01`をin-place(上書き再生成)で実施することを推奨**(別名`run_02`複製は非推奨)。理由:
  1. 正式cacheは**同一out_dir限定**(`er019_family_x_audio_production_runner_01.py:921` `_load_cached_tts_results(out_dir)`、`:1076-1118` `_generate_or_reuse`)。別run dirで`--regenerate-stage`も`--only-segments`も、複製なしではcacheを引き継げない。
  2. 複製する場合、KP/文法の `mode declaration`の`scope.run`が`run_01`の絶対pathに束縛され(`er119_kp_human_review_01.py:406,422`)、新run keyでは一致せず再宣言(Fable代行の宣言行為)が必要になる。並行Agentが作った複製`run_voice_puck_ev_01`の扱いは完了後に参考にできる(読取時点ではKP宣言のscope扱いは未確認)。
  3. `spent_jpy`は`run_01/cost_log.jsonl`の累積(`er121_family_y_runner_01.py:1283` `make_real_spent_fn`)=費用台帳の連続性が保てる。
  - 旧Algieba版の保全: wavはgit未追跡(`git ls-files …run_01 | grep wav`=0)なので、**書換え前にバックアップ**(S2)。公開済み旧版(`user_test/family_y_production_redelivery_fee_01/`、mp3は追跡済み)は残す。
- `--only-segments y_voice_1`は有効(`er121_family_y_audio_01.py:98-118` `_ONLY_OK_RE`/`validate_only_segments`が`y_voice_[1-3]`を許可、`runner.main` `ctx.only_segments`)。T-2追記(1)差分再生成=可。非選択segmentは`validation_inheritance.try_inherit_from_cached`(`er019…:1099-1110`、`er019_family_x_validation_inheritance_01.py:192-221`)で同一out_dirの検証済みentryを引継ぐ(STOPPED+sha一致も持越し=a2 previewのユーザー承認entry維持)。T-2追記(2)キャッシュ有=有(results+wav+`voice_guard_cached`)。T-2追記(4)全再生成化リスク: `--only-segments`未指定+`--regenerate-stage`だと各segmentは`_generate_or_reuse`でcache再利用になる(style_version一致、INVENTORY_01 §3)ので全再生成にはならないが、念のため`--only-segments y_voice_1`を必ず付ける。
- 旧Algieba cacheの復活防止(cache keyにVoiceが入るか): ①`er121_family_y_runner_01.py:965`の`_tts_input_sha`が`json.dumps(ya.segment_voice_map())`を含む=Voice変更でtts stage入力shaが変わり、`--regenerate-stage`無しだと`ensure_stage`(`er062_family_z_writer_01.py:705-715`)が`親sha不一致`でSTOP(=黙って旧版を使わない)。②`er121_family_y_audio_01.py:191-214` `voice_guard_cached`: 前回entryの`y_tts_voice_requested`≠現要求Voiceなら再利用せず再生成(y_voice_1はAlgieba≠Puckで必ず落とされる)。**ただし下記リスクR1(旧人間承認)により①②だけでは不十分**。

### A-2 リスク
- **R1(重大・要事前対処)**: y_voice_1の旧人間承認(a2/b1b)が`check_before_generation`で再生成を0 callで阻止し、`y_tts_voice_requested`の無条件刻印(`er121_family_y_audio_01.py:492,606`)と`_segment_gate_status`のtext sha照合(`er003_v1_n3_01_assemble.py:132-137`)により旧Algieba wavが「Puck」ラベルで組立へ通る恐れ(INVENTORY_01 §5。承認有/無の挙動をscratchで実測済み)。
- R2: 旧Voice 1候補表(Algieba)がページへ混入(INVENTORY_01 §4 障害2)。
- R3: Puck本文のRepetition QA/長さ/ポーズ。Trial知見(限定標本、`CURRENT_SPEC.md` Voice候補表節)=Puckは文境界外1.0秒以上の停止0.00回/sample・悪いtake率0%・fresh take最終OK率24/24。ただしa2は6%減速後ASR再検証(`er003_v1_n3_01_tts_generate.py` `generate_a2_segment_with_slowdown` L385-480、外側ループも通算3 TTS)で別途落ち得る。上限は`PRODUCTION_MAX_TTS_ATTEMPTS=3`/call。3回NGなら`HUMAN_REVIEW_REQUIRED`/`STOPPED`→停止して報告(Gateを回避しない)。
- R4: lockの累積TTS試行(`MAX_CUMULATIVE_TTS_ATTEMPTS=15`、`er011_human_review_lock_01.py:80,384-388`)。現在 a2=6、b1b=7、1回の再生成で最大+3=9/10。2回目の再生成までは超えない。3回目は`BUDGET_GUARD`でHUMAN_REVIEW_REQUIRED。第2回以降が要る場合はFable権限の`approve_regenerate`。
- R5: RESTART_STORM(5分間に3回以上の起動で自動STOP、`er062_family_z_structure_01.py:608`)。本計画は起動2回(Run A・Run B)。**5分以内に3回目を起動しない**。失敗時は再起動せずFableへ報告。
- R6: `--only-segments`併用時 `shared_narration`は`{}`になりresultsへ記録されない(`er121_family_y_audio_01.py:441` `shared_raw = {}`)。共有wavはdisk上に残り組立は可能。results上の`shared_narration`欄が空になる点を許容するか、委任_02でGateの`_shared_narration_gate_blocked_summary`(`er019…:1266`)がNone=通過になることを確認。
- R7: 公開ページはrun dir内`pages/`が出力先(`runner.py:160-172` `pages_dir`、公開は別手順)。公開dirはコピーで作る。

## B. 委任_02で実行する手順(コマンド全文)

前提: (P1) Fableが「Y Voice配線=PRODUCTION_WIRED」を確認済み(`FIXED_VOICE_SLOTS["voice_1"]=="Puck"`、並行Agentのevidence run `run_voice_puck_ev_01`の`y_voice_1`が`voice=Puck`で`status=OK`)。(P2) `er121_*.py`が未commit差分なし。(P3) 日次1,000円(JST)残額の確認。

S0 STOP確認(rc=3なら停止):
`.venv\Scripts\python.exe tools\stop_scope_check_01.py --managed-id FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 --run-dir er121_output\family_y_production_01\redelivery_fee\run_01 --out er121_output\family_y_production_01\redelivery_fee\run_01\stop_check_final_puck_01.json`

S1 事前確認(API 0): `--mode dry-run`でplan出力、`py -m unittest er121_family_y_voice_table_test_01 er121_family_y_comment2_removal_test_01 er121_family_y_runner_01_test_01`相当(既存test)がPASS。

S2 バックアップ(新規ディレクトリ`run_01/_pre_puck_backup_01/`を作り複製): `a2|b1b/narration/y_voice_1*.wav`(+`_original`/`pre_ypl7_adopt`)、`a2|b1b/audit/{tts_generation_results,human_approved_segments,review_lock_state}.json`、`tts_a2_stage.json`/`tts_b1b_stage.json`、`provenance.json`、`final_manifest.json`、`pages/`、`a2|b1b/assembled/`(任意)。

S3 旧承認の失効(**Fable権限の記録編集**): `a2|b1b/audit/human_approved_segments.json`から`y_voice_1`キーのみを除去(`a2`の`preview`は残す)し、除去事実と理由(「ypl7承認はAlgieba attempt限定[`ypl7_user_approval_record_y_voice_1.json` scope]。声変更に伴い無効」)を`run_01/puck_approval_invalidation_01.json`に記録。lockの`review_lock_state.json`は変更しない(RESOLVEDはブロックしない=`er011…:342-355`)。検証: scratchで`check_before_generation`が`proceed=True`になること。

S4 旧Voice 1候補表の退避: `a2|b1b/hr_adopt_prep/voice1_candidates/`を`_pre_puck_backup_01/`へ**移動**(`voice1_candidates_aux_html`が空文字を返し、`pages/audio/v1cand_*.mp3`が生成されなくなる)。`run_01/hr_listening/`は`pages/`に含まれないので移動不要。

Run A(Adv):
`.venv\Scripts\python.exe er121_family_y_runner_01.py --mode real --slug redelivery_fee --run run_01 --theme-package docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json --reuse-manifest docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json --approved-budget-jpy 70 --tts-execution-mode STANDARD --stages tts_b1b --regenerate-stage tts_b1b --only-segments y_voice_1`
→ rcを確認。rc≠0なら再起動せず報告。完了後、b1b `y_voice_1`の`voice==Puck`・`status==OK`を確認(下記C)。

Run B(Std+組立〜検証。Run Aから**5分以上空けず直列**でよいが3起動/5分を超えない):
`.venv\Scripts\python.exe er121_family_y_runner_01.py --mode real --slug redelivery_fee --run run_01 --theme-package … --reuse-manifest … --approved-budget-jpy 70 --tts-execution-mode STANDARD --stages tts_a2,gate,assemble,pages,page_verify --regenerate-stage tts_a2 --only-segments y_voice_1`
(`--only-segments`はTTS stageにのみ作用し、gate/assemble/pages/page_verifyには影響しない=`runner.py:986`)。

直列の理由: 同一run dirの`provenance.json`/`RUN_LOCK`/`tts_generation_results.json`の競合(両levelは別ファイルだが`provenance.json`・`cost_log.jsonl`が共有)。並列化は不可。Run Aの待機中に並列で進められるのは: 公開dir準備(下記D)・Comment 2除外確認スクリプトの用意・公開前チェック用scratchの準備(いずれもAPI 0)。

## C. 検証コマンド/項目(委任_02)

1. Puck actual voice: `a2|b1b/audit/tts_generation_results.json`の`segments.y_voice_1.voice`=="Puck"かつ`y_tts_voice_requested`=="Puck"、`sha256`≠旧(`c3f59b00…`/`821f2c18…`)、wav mtimeが今回、`attempts_log`の最終attemptが今回のもの、`narration/y_voice_1.wav`のshaが記録と一致。さらに`attempt_history.jsonl`/`cost_log.jsonl`に今回のGemini TTS呼出(model `gemini-3.8-flash-lite-tts`、voice名)があること(`BLOCKED_HUMAN_APPROVED`のイベントが無いこと)。
2. Std: `y_voice_1`の`slowdown_applied=True`、`y_voice_1_original.wav`と`y_voice_1.wav`の長さ比∈[1.03,1.09](`er003_v1_n3_01_assemble.py:233-234`)。
3. Voice 2/3等が再利用であること(`reused_from_previous_run`またはREUSED_VALIDATED、sha不変)。
4. gate PASS(`gate_summary.json`)、`assemble_summary.json` OK・clipping無し、`page_verify_local.json` ok。ASR/Repetition QA/disfluency/発音/長ポーズ/速度/音量は既存Gate(`y_style_gate`+`verify_episode_audio_validation_gate`+gain/headroom reportの確認)。
5. Comment 2除外(Adv): `b1b/audit/timeline.json`=43要素のまま、`b1b/parts.json`・`b1b/support_texts.json`・`pages/index.html`のAdv節にcomment_2=0件、`final_manifest.json`の`removed_by_spec.b1b.comment_2`と`support_segments.b1b==[preview,comment_1,comment_3]`。Std節のComment 2(std_16)は維持。
6. 旧Voice/Comment 2の復活なし: 旧`b1b/narration/comment_2.wav`の存在は許容(組立で未使用)だが、timeline・page・manifestに現れないこと。`voice_guard_cached`が`y_dropped_for_voice_mismatch`に`y_voice_1`を記録していること(resultsの該当欄)。
7. KP/Part1/Part2/文法が不変(`key_phrases/*/kp_selection_final.json`・`study_text/*`のsha不変。stage freshの`_require_fresh`通過)。
8. 総時間: Std/Adv通し再生秒数、タイムライン上のVoice 1の位置を試聴ページに反映。

## D. 公開

- 公開先(推奨): `user_test/family_y_production_redelivery_fee_02/`(旧`_01`はAlgieba版として保持。B3RD8等の「旧e2e保持」前例と同形)。`run_01/pages/`の`index.html`+`audio/`を複製(`listening/`は複製しない)。URL=`https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_02/index.html`。新規dir名はFable判断(上書き案`_01`も可。上書きなら旧Algieba版の公開が消えるのでS2の追跡済みmp3がgit履歴で残る)。
- 公開前: `er_user_listening_page_common_01.check_page`相当(page_verify内で実施済み)、ローカルでaudio参照(std_00〜25/adv_00〜24/full)の存在・秒数一致、通し/パート別再生リンク、確定スクリプト(Puck版Voice 1本文が従来とbyte一致)、KP/解説の表示、Previewの表示を確認。push後 HTTP 200確認(必要ならブラウザでconsole error 0、実再生)。
- 最終Statusは「完成版・ユーザー最終試聴待ち」(承認を先取りしない)。

## E. 費用見積・所要時間

- 根拠: ①Trialの実績2.34円/take(委任記載、`FAMILY-Y-VOICE1-MALE7-TRIAL-01`)、②run_01実績=a2のGemini TTS 24 call 9.16円(0.38円/call)+OpenAI ASR 31 call 2.78円+Azure secondary 8 call 5.41円、b1b同様(`cost_by_stage.json`)。③Puck fresh take最終OK率24/24。
- 期待値: 2 segment × 2.34円 × 約1.25 take = **約5.9円**。最悪(各3 take全使用+a2減速後再検証)=2×3×2.34=**約14円**。KP/support/translate等の再生成は0(再利用)。
- `--approved-budget-jpy 70`の根拠: `run_01`の累積費用が52.134円(`e2e_stage_log.jsonl`のspent_jpy_cumulative)で、予算guardは累積で判定(R上記)。52.13+最悪14=約66円→70円。警告閾値100円未満、案件個別Cap 170円(`runner.py:32`、OPEN-525 O8記載の200円も下回る)以内。**案件見積300円以下かつ承認済みScope内=7-7で都度承認不要**。日次1,000円(JST)内かは委任_02開始時に当日累計を確認。想定外に超過見込みならSTOPして報告。
- 所要時間: S0-S4 約10分、Run A 約2-3分、Run B 約4-6分(TTS+組立+pages mp3変換約15秒+verify)、検証・公開準備 約15分、合計 **約35-45分**。並列化: Run A/B自体は直列(上記)、公開dir準備・チェックスクリプトはRun中に並列。

## F. 配線完了後に再確認する項目(Y Voice配線依存)

1. `er121_family_y_structure_01.py` `FIXED_VOICE_SLOTS`/`verify_voice_assignment`の確定形とcommit(現在は作業木の未commit差分)。
2. 配線完了時点で`segment_voice_map()`のy_voice_1=="Puck"(それ以外のVoice 2/3=Zephyr/Schedarが不変であること。変わるとVoice 2/3が`voice_guard_cached`で落ちて再生成=費用増)。
3. 並行Agentのevidence run(`run_voice_puck_ev_01`)の結果: Puck生成が1 takeで通ったか、旧承認除去の方法、KP declarationのscope扱い、`--only-segments`でgate/assembleが通ったか(R6)。その結果で本計画のS3/S4/R6を更新。
4. 旧承認の自動失効guard(INVENTORY_01 §5)が別途コード化された場合はS3の手作業が不要になる。
5. `er121_family_y_runner_01_test_01`/`voice_table_test_01`が現HEADでPASS。

## G. 判断候補・起票候補

- 判断候補(分類付き): なし(新規の判断要素なし)。KP等のAUTO_ADOPTED扱いは INVENTORY_01 §7 に記載(B寄り)。
- OPEN起票候補: 「Y人間承認がVoice変更後の再生成を阻止/誤通過させる(承認がattempt/audio shaに束縛されず、Voice刻印が実Voiceを保証しない)」。分類=**修正へ進む**(11-8)。次委任案: 委任_02の前段または並行Agent完了後の小規模委任で、(a)承認はtext shaに加えて`audio sha`/`voice`を照合(または生成結果の`voice`≠要求Voiceで`y_tts_voice_requested`を刻印せずSTOP)、(b)DefaultOffIsolation不要(既存安全機構の厳格化)、(c)offline test固定。コード編集は`er121_family_y_audio_01.py`を並行Agentが編集中のため、そのcommit後に実施。
