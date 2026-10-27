# FZ-TELL-TALE-HEART-NARRATOR-VOICE-01 委任_01 成果(Fenrir版、2026-10-28)

方針変更: 当初Schedar指定→ユーザー修正(USER_02)でNarrator=**Fenrir**(警官役Schedarと重複回避)。警官・老人のVoice不変。本作品限定。
## 実装
- er062_family_z_structure_01.py: `STORY_NARRATOR_VOICE_PINS={"the_tell_tale_heart":"Fenrir"}`+`narrator_voice_for()`。他story・FAMILY_Z_NARRATOR_VOICE(Aoede)不変。voice_assignment.jsonに`narrator_voice_pin`追記(当該作品のみ)。
- test: er062_family_z_voice_assignment_test_01(NarratorVoicePinTest追加、16件OK)/er026_..._tell_tale_heart_test_01(23件OK)。他story registry tests(monkeys_paw/after_twenty_years/gift_of_the_magi)OK。
## 変更対象clip(既存仕様どおり)
- 再生成=本文narration(speaker=narrator)の full_story_part1_c1/c2/c4, part2_c1_k1/k2, part3_c1_k1/k2 (+親part2_c1/part3_c1)を Std/Adv 各7chunk。narratorの引用(q21_1/q21_2)もnarrator Voice。
- 再利用(sha一致): dialogue(part1_c3 old_man=Algieba)、topic_intro/japanese_title/preview/comment/KP(en/ja/解説)/Shell。intro/preview/comment/KP/JA/ShellのVoiceはer063 role表の固定値でnarrator_voiceに紐付かない=変更せず(「本文を語るNarrator」のみ)。
- officer: dialogue_attribution_{a2,b1b}.json final={q6_1:old_man,q21_1/q21_2:narrator}。警官台詞clipは存在しない。officer再割当は撤回済みで実施せず。
## run
- run_voice_fenrir_01(run_reselect_01から許可リスト相当+audio/結果を複製、attempts/tts_block_progress/ログ類は除外、path文字列のみrun名置換、writer/KP review記録はバイト同一)。
- runner 1起動: stages tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify、pages=user_test/family_z_tell_tale_heart_fenrir_01、実費¥10.23(b1b 4.88/a2 5.35)。
- 先行Schedar版(run_voice_schedar_01): 修正指示受領時にb1b完了・a2途中でプロセス(自PID)停止。clipは破棄せず記録のみ。実費=b1b ¥5.04(実測)+a2途中(約10 TTS呼出、概算¥3〜5)=約¥8〜10(不要費用)。Cap¥60合算≈¥20。
## 検証(実測)
- 全narrator clip voice=Fenrir(Std/Adv)、dialogue=Algieba、再生成9エントリ/level(7chunk+親2)、他clipのsha不変、KP wav sha一致。
- ASR全PASS(status OK、asr_judgement PASS)、速度v2 gate OK(Std narrator slow6/Adv none/Adv dialogue fast6)、gate_result_04C m2_complete、chunk計画: Std [60,69][68,71]/Adv [58,62][65,61]で不変(voice欄のみ差)、writer sha Std b94c7305…/Adv(r2) e11b84dd…不変。
- page_verify: index 33/Std 25/Adv 24 全再生OK、console error 0、http>=400なし。
- LR採用: 0。Fallback: 本runでの新規採用0(reused KP: 元run Adv kp2_en ENGLISH_LOCKのFallback 1は再利用で継続)。
- 既存公開 user_test/family_z_tell_tale_heart_reselect_01/ と run_reselect_01 は未変更(git差分なし)。公開差替えなし。
## 状態
Production完成(候補ページ)。ユーザー試聴PASSは未(最終試聴待ち)。
