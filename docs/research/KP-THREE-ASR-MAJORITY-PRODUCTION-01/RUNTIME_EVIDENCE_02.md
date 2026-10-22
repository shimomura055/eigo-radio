# KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_02 runtime evidence (2026-10-22)

実行driver=`er104_kp3v_runtime_evidence_01.py`(Production関数を薄く呼ぶだけ。判定・retry・fallbackは変更しない)。出力=`er104_output/kp3v_runtime_evidence_01/`(wav/Store音声はgit対象外、json/jsonl/logのみ追跡)。
STOP確認: `tools/stop_scope_check_01.py --managed-id KP-THREE-ASR-MAJORITY-PRODUCTION-01` を x_k2 / z_s1 / z_new の各run-dirで実行、全て rc=0(stop=false)。各コマンドは1回ずつ実行、再起動なし。
使用モデル: Primary=OpenAI(routing既定ASR)、Secondary=Azure STT、Whisper=faster-whisper small int8 cpu(preflight ok=True load 1.76s)、TTS=gemini-3.8-flash-lite-tts(speech_metadata_flash_lite、Aoede)。いずれも本番既定(最新世代原則の例外ではなく本番ライン設定そのもの)。

## 1. Family X(正式runner `er019_family_x_audio_production_runner_01 --stage tts --only-segments kp1,kp2,kp3_english`、専用out_dir・専用Store seed)
| KP | 経路 | 行 | 判定 | API呼出 |
|---|---|---|---|---|
| think up | Store再利用の保存転写再判定(旧entry: P PASS "ThinkUp." / S NG "Think.") | P+W | PASS_VOTE_2OF3(警告なし) | Whisper 1回のみ(2.1s)。Primary/Azure/TTS 0 |
| blurt | 同上(旧: P NG "Blur." / S PASS "Blurt.") | S+W | PASS_VOTE_2OF3 / PASS_WITH_WARNING(SECONDARY_CONFIRMED=事後試聴対象) | Whisper 1回のみ(2.1s)。Primary/Azure/TTS 0 |
| bring in | Store無し=新規生成 | P+S | PASS_DUAL(Whisper不呼出) | TTS 1・Primary 1・Azure 1 |
- 再利用entryの`kp_dual_check`は`kp_vote_check_v1`へ書換え(source=stored_evidence_rejudged、旧`kp_dual_check_v1`は読取専用)。
- x_rerun(同一out_dirの前回results再利用点): API呼出0(spy fileが生成されず、費用累計0.08のまま)。
- 費用(runner記録): 0.08 JPY(gemini 0.01 / openai_asr 0.01 / azure 0.05)。HR queue追記0(専用queueへ隔離)。

## 2. Family Z(正式関数 `run_tts_stage`)
- z_s1: 多数決導入前の実Z KP entry(Melos run、証跡なし)10本を専用run_dirへ置き再利用点6のS1経路を通した。a2 5本=全てP+S。b1b: kp2/kp3=P+S、kp1(sentence someone to death)=P+W(S NG "Sentenced…")、kp5(abandon)=P+W(S NG "Abandoned.")、kp4=Whisper不成立で再生成(seize、再生成後 P "seize"/S "Sees."=NG/W "Seize"=PASS → P+W)。**Z正式経路でWhisperが自然発火した(4回、2.1-3.7s)**。人工entry・HR Lock迂回なし。
- z_rerun: 同一run_dir再実行=API呼出0(保存証跡による再利用)。
- z_new: 新規KP生成(b1b 5本: based on interviews / green beans / settle down / human concierge feature / jump to conclusions)=全て1回でP+S(PASS_DUAL、Whisper不呼出)。**注意**: driver側のtimeout(590秒)で打切りとなり(rc=124、外部停止ではなく自己設定のtimeout)、a2・8本目までの計画は未完。TTSが1本75-180秒(batch)かかるため。再起動はしていない(未完の事実として記録、Z新規はb1b 5本の観測のみ)。
- 推定費用: Azure 17回・OpenAI 7回・TTS 7回 ≈ 1.0 JPY(単価はrunner記録0.05/0.01/0.01から推定、Whisperは0円)。X 0.08と合わせ**約1.1 JPY(上限10円以内)**。

## 3. 観測した事実と限界
- 3系統の判定行(P+S / P+W / S+W)が正式経路で記録された。Whisperは割れた時だけ(X 2回・Z 4回)呼ばれ、P+S一致時は0回。
- Whisper失敗・preflight失敗・circuit open時の技術STOPはtestで固定(`er104_kp_vote_wiring_test_01.py`)。実run上でのWhisper障害の自然発生は未観測。
- 運営者試聴: blurtは語末のt音が聞こえない(人間NG)がASR 2/3 PASS=多数決方式の限界の実例(仕様変更なし、品質知見)。試聴ページ=`user_test/kp3v_vote_evidence_01/index.html`。
