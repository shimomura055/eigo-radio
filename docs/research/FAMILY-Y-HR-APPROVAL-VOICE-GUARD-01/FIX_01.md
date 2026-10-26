# FIX_01 (OPEN-535)

方針: Y経路のみ(`er121_family_y_audio_01.py`)・fail-closed・共有module(er011/er003/er019/er063)無変更。X/Zの既定挙動は構造上不変。

## 変更(`er121_family_y_audio_01.py`)
1. `reconcile_hr_approvals_for_request(out_dir, level, style_profile)`: Y本文segment(`y_*`とそのchunk id。preview/comment/KP等は対象外)の承認について、
   承認時のVoice/Styleが現要求と一致しなければ `audit/human_approved_segments.voice_guard_quarantine.json`へ退避(承認recordは保全・削除しない)。冪等・API 0。
   - 承認時Voice: 新形式=承認recordの`y_binding.tts_voice`、旧形式=同runのresults entryの`voice`(実TTS記録)/`y_tts_voice_requested`。両方ありで不一致/どちらも無い=判定不能=退避(Y_HR_APPROVAL_VOICE_UNDETERMINABLE)。
   - Style: `y_binding.style_profile` もしくは entry の `style_profile` record(profile_id/expected_base_sha256/style_base_sha256)が現要求(`current_style_record`)と異なれば退避(Y_HR_APPROVAL_STYLE_MISMATCH)。default profile同士(None)は一致。
   - 一致する承認(正常再利用・resume)は一切触らない。
2. 呼出位置(承認を消費する前): `generate_y_b1_segments`/`generate_y_a2_segments`(課金前)、`y_style_gate`、`assemble_level`(chunk親再構築・共有Gateより前)。
3. `stamp_requested_voice`(旧5箇所の無条件刻印を置換): 実TTS記録`voice`が要求と異なる/承認スキップ結果で承認時Voiceが要求と異なる場合は刻印せず`YAudioStop`(Y_VOICE_STAMP_MISMATCH / Y_HR_APPROVAL_VOICE_MISMATCH)。
4. `record_y_human_approval(...)`: 既存`asm.record_human_approval`を呼んだうえ`y_binding={tts_voice,style_profile,tts_model}`を追記(新規承認用。既存形式と上位互換)。

## 既定挙動不変の根拠
- `er011/er003/er019/er063`は無変更(`git diff`に出ない)。X/Zの承認照合は従来どおりtext shaのみ(test `TestSharedModuleUnchanged`)。
- Yでも Voice/Style一致の承認、非Y segment承認(preview等)、承認なしrunは出力不変。quarantineは不一致時のみ発火。
- `y_binding`はer011等の既存読取が参照しないadditive key(`_human_approved`は`canonical_text_sha256`のみ参照)。

## 残る制約(報告)
- 旧形式承認のVoice判定は「現在のresults entry」に依存する。承認後に別Voiceで再生成されentryが更新された場合、旧承認は新Voiceに一致して残り得る(その時点でentryは新attemptであり、承認はスキップ対象になる点が残る)。新規承認は`record_y_human_approval`で`y_binding`を持つため影響しない。
- `er121_e1_hr_adopt_r0_01.py`(旧承認書込script)は無変更(旧形式で書込み、上記旧形式判定でカバー)。
- 既存`er019_x_std_chunk_opus_test_01 R4HunkClassifierTest`は本変更前から赤(`er121_family_y_structure_01.py verify_voice_assignment/FIXED_VOICE_SLOTS`がUNCLASSIFIED)。本変更で`_generate_y_body_segment_chunked`/`generate_y_b1_segments`/`y_style_gate`がUNCLASSIFIEDに加わった(Adv出力は不変=reconcileは不一致時のみ発火)。classifier tool(別管理IDの所有)への`MANUAL_REVIEW`登録を次委任案とする。
