# RESULT PACKET — USER-TEST-AUDIO-COMPLETION-01-VOICES-CONT1(comment_2再生成+Assembly完成)

1. **最終Status: PARTIAL / USER TEST READY(Analytical Leakage残存)。
   PRODUCTION_WIRED未承認、OPEN-151のStatusは本タスクでは変更していない
   (RESULT_PACKET記載のみ)。** 前回STOP(comment_2 Human Review Cost
   Guard→Audio Validation GateがBLOCKED)から前進し、Assembly/Audio
   Validation Gate/完成episode(wav+mp3)/標準player/記事⇔音声一致確認/
   comment_fact_safety_evidence.jsonまで到達した。

2. **Comment 2再生成**: 既存の接続済み経路
   `er012_b_family_production_runner_01.py::run_comment_contract_for_
   new_theme(article_text, sections, 2, ledger_text, out_dir)`(無変更)
   を1attempt目で呼び出し、deviation_overall_status=`LEDGER_COMPLIANT`
   のため2attempt目は不要だった(最大2回のうち1回で終了)。この関数は
   Comment 2のみの部分再生成はできない設計のため、Preview+Comment 1-4
   全5件を再生成した(委任文の想定どおり「関数が全件生成しかできない
   場合」に該当)。
   - comment_2旧: "Now, you will hear two people speak in their own
     words, one after the other. Each one brings a different view to
     the same question."
   - comment_2新: "That question can feel different in everyday life.
     Now, listen to two readers speak for themselves, one after the
     other."(カンマ区切り挿入句"Each one brings..."を含む文構造自体が
     解消された)
   - 他4件(preview/comment_1/3/4)も全て新テキストへ変更(旧文と完全一致
     なし)。詳細(旧→新全文、Contract検証結果)は
     `audio/b1_2v/comment_2_regeneration.json`。

3. **TTS**: comment_2新テキストは**1attempt目でNORMALIZED_MATCH
   (OK)**、挿入句の読み飛ばしは再発しなかった(ASR: "That question can
   feel different in everyday life. Now, listen to two readers speak
   for themselves, one after the other."、旧問題箇所を含めて全文一致)。
   他4件(preview/comment_1/3/4)も新テキストで各1attempt目にOK。lockは
   バイパスしていない: 新テキストはcanonical_text_sha256が旧エントリと
   異なるため、`er011_human_review_lock_01.py::check_before_generation()`
   が「canonical_text changed since last lock; treated as new version」
   として通常のAUTO_PROCESSINGを許可した(`approve_regenerate()`は
   一度も呼んでいない、旧lockエントリも削除・編集していない)。14
   segment全てstatus=OK。

4. **Key Phrase音声(run1の欠落を本タスクで補完)**: run1のtts_generation_
   results.jsonはkp1-5の`status="OK"`を実体生成なしに記録していたバグが
   あり(text選定のみ完了、音声wav未生成)、本タスクのAssembly初回実行で
   `FileNotFoundError: kp1_en.wav`として発覚した。既存Production関数
   (`shared_narration.ensure_key_phrase_english_component`/`tts_gen.
   generate_charon_japanese_with_reading_safety`、`er012_editorial_b_
   voices_3v_audio_trial_01.py::run_key_phrase_tts()`と同一呼び出し
   規約、事前指定Read一覧外のため本節末尾に追加Read理由を記載)でkp1-5の
   en/ja音声を新規生成し、全件OK。Key Phraseのtext自体は再選定していない
   (run1のkeywords_canonicalized.jsonをそのまま使用)。

5. **Audio Validation結果**: **PASS**(`audio_validation.json`、
   `verify_episode_audio_validation_gate`、緩和・override一切なし)。
   14 segment全てVALIDATED。

6. **完成episode**: duration=309.485秒、peak=0.92155、clipping=False、
   headroom safety valve適用状況は`b1b/run_summary_assemble.json`参照。
   `audio/b1_2v/web/episode.mp3`(3.5MB)。

7. **記事⇔音声一致確認**: `article_audio_consistency.json`、
   `all_section_bodies_verbatim_from_article=true`、
   `all_tts_input_matches_parts=true`。Comment/Previewは記事本文ではなく
   Comment Contract経由の補助テキストのため逐語一致対象外(仕様どおり)。

8. **Comment/Fact Safety反映証拠**: `comment_fact_safety_evidence.json`。
   comment_contract節に新テキスト全文・support_status(全OK)・
   deviation_overall_status(LEDGER_COMPLIANT)・episode timeline開始秒
   (comment_1=94.466s/comment_2=131.309s/comment_3=227.247s/
   comment_4=273.229s)を記録。fact_safety_gate節は前回同様Writer stage
   専用機構のため新規判定なし(run2_clean時点の非発火理由を転記)。

9. **残存Leakage記録**: `comment_fact_safety_evidence.json`
   `analytical_leakage_check_residual_flag`節(`any_flagged=true`、
   flagged_items=voice_b[leak_evidence_subject等5項目]/tension
   [leak_discovery_syntax/leak_tension_reverts_to_research]、原文引用
   込み)。player.html本文にも同じ限界を明記し試聴対象から隠していない。
   comment_2 attempt3試聴ファイル(STOP時用に準備予定だったもの)は、今回
   Gate PASSに到達したため生成不要と判断(comment_2は新テキストで正式
   採用のためattempt3[旧テキスト]は不要)。

10. **mp3一覧・player・URL・gitignore**:
    - `player.html`: `Select-String -Pattern "file:///|C:\\"` 相当の
      grep確認で該当0件(相対パスのみ)。
    - `git check-ignore -v .../web/episode.mp3` → exit 1(無視されない、
      確認済み)。
    - episode.mp3(3.5MB)+segments/(33ファイル、2.1MB)、合計<50MB。
    - 想定URL(Push後):
      `https://raw.githubusercontent.com/shimomura055/eigo-radio/main/
      er014_output/four_type_observation_01/voices/audio/b1_2v/web/
      episode.mp3`(本タスクではGit操作なし、Push未実施)。

11. **費用**: 本タスク実費=**¥13.01**(budget_jpy_cap=60、内訳: openai
    ¥0.65[Comment Contract LLM 6 calls]+gemini ¥11.73[TTS: comment
    5件差し替え+Key Phrase音声10件]+openai_asr ¥0.63[ASR検証])。
    **Voices Production 1生成セット総原価 = ¥140.39(Writer/Comment/QA/
    Gate、run2_clean) + ¥32.34(音声化run1) + ¥13.01(本タスクCONT1)
    = ¥185.74**(`run2_clean/production_set_cost.json`更新済み)。

12. **model_id/TTS model・voice割当**: LLM(Comment Contract再生成+
    Ledger Deviation Check)=`gpt-5.6-luna`(openai、既存routing無変更)。
    TTS=`gemini-2.5-pro-preview-tts`/`gemini-3.1-flash-tts-preview`
    (既存Production、無変更)、ASR=`gpt-4o-mini-transcribe`。voice_a=
    Algieba、voice_b=Erinome(run1と同一、fallback発火なし)。Narrator見出し
    =Aoede固定。Preview/Comment/Topic intro=Charon。Key Phrase英語
    Component=Aoede(Master Audio Store経由)、日本語meaning=Charon。

13. **Open Item候補**:
    (a) 「B-Family Voices Comment(段落間ブリッジ文)で、カンマ区切りの
    挿入句(例: "one after the other. Each")をTTSが系統的に脱落させる
    ケースがある」(前回提起分、今回は同一パターンの文言自体が新テキストで
    解消されたため直接の追加証拠なし、既存Open Item提起は維持)。
    (b) 「B-Family Voices新規テーマ音声化(write_new_theme経路)は、
    Key Phrase音声(kp{rank}_en/ja_charon)を生成しないため、Assembly時に
    FileNotFoundErrorで初めて発覚する。run_comment_contract_for_new_theme
    と同様、write_new_theme経路にKey Phrase音声生成([
    shared_narration.ensure_key_phrase_english_component/tts_gen.
    generate_charon_japanese_with_reading_safety]呼び出し)を正式配線
    すべきか、ユーザー判断を仰ぎたい(現状は本タスクのような音声化
    driver側が都度気づいて個別に補う運用になっている)」(新規提起)。

14. **T-0/事前指定外Read/STOP**: T-0=PASS
    (`docs/pm/delegation_log/USER-TEST-AUDIO-COMPLETION-01-VOICES-CONT1_
    check.json`)。事前指定外Read: (a)
    `er012_editorial_b_voices_3v_audio_trial_01.py`(Key Phrase音声生成
    関数`shared_narration.ensure_key_phrase_english_component`/`tts_gen.
    generate_charon_japanese_with_reading_safety`の正しい呼び出し規約を
    特定するため。事前指定Grep一覧に無かったが、Assembly実行時に
    `FileNotFoundError: kp1_en.wav`で判明した実行時欠落[run1のtts_
    generation_results.jsonがKey Phrase音声のstatus="OK"を実体生成なしに
    記録していたバグ]への対応に必須だった)。(b)
    `er012_b_family_production_runner_01.py`内`run_key_phrases`周辺の
    Key Phrase音声reuse実装(`reuse_key_phrases`)を、正しい生成経路を
    特定する過程で参照。(c) `er003_v1_iran01_b1_kp_audio.py`(旧one-off
    scriptで同名関数の古い呼び出し例を確認、最終的にはTrial-01の新しい
    呼び出し規約[disfluency safety強化版]を採用した)。STOP: なし
    (最終Status PASS/PARTIAL到達、費用上限未超過)。

詳細証跡: `er014_output/four_type_observation_01/voices/audio/b1_2v/`
配下(`comment_2_regeneration.json`/`audio_validation.json`/
`article_audio_consistency.json`/`comment_fact_safety_evidence.json`/
`cost_summary_audio.json`/`player.html`/`web/episode.mp3`/`web/
segments/`)、driver`run_voices_2v_audio_completion_2.py`、
`run2_clean/production_set_cost.json`(累計原価更新)。
