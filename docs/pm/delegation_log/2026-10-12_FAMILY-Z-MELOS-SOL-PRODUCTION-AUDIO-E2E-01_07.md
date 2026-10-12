# FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_07 (2026-10-12) STOP報告(KP a2 canonicalization)

到達stage: seed_check -> writer -> validate_b1b -> std_adjust -> validate_a2 -> plan -> support -> kp(STOP)。TTS以降は未実行。試聴ページ未公開。
STOP: `FAMILY_Z_KP_CANONICALIZED_MISSING`(a2)。原因: KP backend の canonicalization が a2 で attempt1/2 とも CANONICALIZATION_INVALID
 (rank1 selection "take my place" -> LLMが "take someone's place" に一般化したが、source_span 内の連続部分文字列でもなく、閉じた語彙集合の人称代名詞置換にも該当せず Rule7 違反)。
 b1b は KP PASS(selection 2回目で STRUCTURE_PASS)。自動retry/再生成は未実施。

## 実施事項
1. override: runnerに human-confirmed override の読込機構が無かった(`dialogue_override.json` は出力専用)。最小hook `er062_family_z_writer_01.apply_human_confirmed_override` を追加
   (status==mismatch かつ quote_id・引用text完全一致・speaker妥当の行のみ採用、problemsは解消しない、決定論/LLM判定ロジックは無変更、既存の人間確定は上書きしない)。
   test追加1件、er062/er026/er063 test 計144件OK。
2. `dialogue_override.json` に human_confirmed を記録(b1b: q1_1=melos, q1_2=melos, q9_1=king / a2: 同一3引用の対応文 同じ根拠、Fable PM確定・2026-10-12・根拠文逐語引用・誤り種別 addressee_keyword/in_quote_keyword)。mismatch原本は `dialogue_override_b1b_mismatch_06.json`。
   Std(a2)側の不一致も同じ3引用の対応文のみ(新規不一致なし)。
3. plan以降を再開(writer/validator/std_adjustはprovenance再利用: elapsed 0秒・再課金なし)。再課金はplan(b1b/a2)+support+kpのみ。

## 文章系
- 話者表(`speaker_table.md`): 全引用、Adv17件/Std17件、疑義なし(human_override 各3件、他agree/llm_only)。other無し。
- validator: b1b PASS / a2 WARN(Std検査: 段落47/47一致、同一文率0.0、平均文長 adv6.633/std7.217のみ。第1層・第2層PASS)。OPEN-302 WARNなし。
- Preview/Comment lint: 全て違反なし(retryなし)。注意: Std Comment3(Part3紹介)は結末(「待ってください」と叫び、友の足元に倒れ「戻ってきた」)まで詳述しており、Part3の事実のみとはいえネタバレ度が高い(lint通過、判断はFable)。
- KP: b1b PASS / a2 STOP(上記)。

## 費用
累計約JPY31.86(委任_06まで30.96 + plan約0.06 + support約0.62 + kp(a2 selection/canonicalization/b1b)約0.2未満、estimate; e2e_stage_log参照)/上限300、警告200未到達。
