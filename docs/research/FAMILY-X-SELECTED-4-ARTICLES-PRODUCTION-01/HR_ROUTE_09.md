# HR到達経路7項目(PM_GOVERNANCE 30節) - ⑨Meta Adv(b1b) Vocabulary「latter」英語音声 (委任_09、2026-10-30)

実測の出所: `er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01/b1b/` の `audit/tts_generation_results.json`(vocab_extra.v3.vocab_extra_english)、`audit/review_lock_state.json`(vocab_extra_3_en)、`narration/attempts/vocab_extra_3_en_attempt{1-4}_*.json`、`vocab_audio/vocab_audio.json`。API 0で採取。

1. **対象**: ⑨ AIペット(Meta Waddle World) Advanced(b1b) Vocabulary & Expressions 第3項目「latter」(candidate p_e0a06c2e39、②追加解説=KP重複なし)の英語音声 `narration/vocab_extra_3_en.wav`(1.02秒、canonical_text=`latter`、sha256=1c033d17...e981=attempt4)。seg_key=`kpv3_vocab_extra_english`。
2. **適用ルート**: role `vocab_extra_english` = KP英語音声と同じ3-ASR多数決Gate(`vote: kp_vote_check_v1`, `required: true`)。Primary=OpenAI ASR、Secondary=Azure。Whisper(第3票)は`whisper_called: false`(両方NGで多数決成立のため呼ばれず)。
3. **通過工程と判定**(全4 attemptが同一の判定):

| attempt | 経路(指示) | route | audio sha(先頭) | OpenAI ASR | Azure ASR | 判定 |
|---|---|---|---|---|---|---|
| 1 | styled(minimal、"smoothly connected chunk") | custom_60ebc452 | bee3c1b3 | Ladder | Ladder. | NG_BOTH / TTS_FAILURE |
| 2 | 同上 | custom_60ebc452 | 3ab5ddd0 | Ladder | Ladder. | NG_BOTH |
| 3 | english_lock fallback(1246字) | custom_31eb2f72 | f2abcba7 | Ladder | Ladder. | NG_BOTH |
| 4 | 同上 | custom_31eb2f72 | 1c033d17 | Ladder | Ladder. | NG_BOTH(最終) |

   4 TTS attempt x ASR2系統 = 8 ASR判定すべて「Ladder」。length_ok=true(6字/上限16)、実wavは存在。最終 status=STOPPED(reason「2回試行してもASR検証(内容+長さ)に合格しませんでした」)、primary_instruction_type=`STYLED_AND_ENGLISH_LOCK_BOTH_FAILED`、`vocab_audio.json` complete=false・errors=`kpv3_vocab_extra_english=STOPPED`。
4. **retry/fallback/LRの発動**: retry=発動(styled 2回)。fallback=発動(english_lock 2回、`fallback_used: true`)。Local Rewrite=対象外(単語1語の英語音声でLR候補なし。テキスト書換えは語そのものを変えるため不可)。累計TTS 4・ASR 4呼出、`budget_guard_triggered: false`。上限は既存どおり遵守(回数上限・Gateの迂回なし)。
5. **直接原因**: 米音のflap-t(語中の t が弾音)で latter と ladder は同音(/ˈlædɚ/)。ASRは語単独だと文脈がなく常に ladder を選ぶため、**ASRでは原理的に判別不能**。TTSは入力 `latter` に対し音声を生成しており、Gate側で「Ladder」と不一致になる。区分=**「不具合・未実行工程」ではなく、Gateが設計どおり作動して安全側にSTOPPEDした正常通過**。audio欠落・未実行工程・配線欠落はない(全工程実行済み、wav実在、sha整合)。
6. **残る自動救済**: なし。理由: (a) retry/fallback上限消化済み、(b) ASR基準(同音語許容・phrase_list等)の変更は承認範囲外(Charter 1)、(c) Whisperを加えても同音語は同結果と見込まれ新Gateにもなる、(d) 語の差替え(ladder接続の別表記)はコンテンツ変更で承認外。残る手段は人の耳での確認のみ。
7. **判断依頼内容**: HRページ `https://shimomura055.github.io/eigo-radio/user_test/family_x_meta_waddle_world_hr_02/index.html`(掲載は判断対象のattempt4の1本のみ。attempt1-3は`hr_page_listing_policy_record_09.json`に内部記録)。
   - 試聴OK(「latter」と聞こえる)→ 既存HR採用手順で本takeを採用(`tools/fx4h_hr_adopt_meta_vocab3.py --apply --statement <承認原文>`: record_human_approval + review_lock RESOLVED/HUMAN_APPROVED + vocab_audio再export、API 0、statusはSTOPPEDのまま正直に維持)→ ⑨ End Userを最新asset(当時rev01-g/最新)で再produce。
   - NG → 別takeの再生成はユーザー指示時のみ(有料・Aoede/別指示は別途見積)。
