# FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_01C(§3 減速処理適用範囲・§4 Attempt 4生成条件・§5 異音/途切れ検知Trial)
日付 2026-10-11 / 実行層 Sonnet / main(`C:\Users\tensh\eigo-radio`) / read-only調査+無料ローカル音声解析のみ。有料API 0、費用 JPY 0。Production/Prompt/Validator/Routing/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS 変更なし。worktree(`eigo-radio-tone`)読み取りのみ(snapshotへsha256付きコピー)。Part 2再生成なし。並行agent領域(part_AEF/part_BCD/intro_preview_fullstory/keyphrases_jacomments)に触れていない。

## 成果物(`er057_output/coffee_final_listening_tone_trial_01/part_45/`)
`SLOWDOWN_SCOPE_01.md`、`ATTEMPT4_CONDITIONS_01.md`(+`attempt4_reconstructed_prompt_01.txt`、`attempt4_style_verify_01.txt`)、`ANOMALY_CANDIDATES_01.md/.json`、`ANOMALY_DETECTION_TRIAL_01.md`、`PLAY_EVIDENCE_01C.md`(+`pages_play_evidence_01c.json`)、`whisper_words.json`、`evidence_snapshot/`(`SNAPSHOT_MANIFEST.json`、音声wavはgit非管理)。スクリプト: `er057_audio_anomaly_detect_trial_01.py`、`er057_anomaly_page_build_01c.py`、`part_45/{snapshot_01c.py,whisper_words_01c.py,play_verify_01c.py}`。確認ページ: https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/anomaly/index.html 。

## 確定した事項
1. 6%減速(`atempo`)の適用範囲 = Standardの英語本文4 role(full_story_part1/2/3・in_one_line)のみ。Intro/shell/topic_intro/日本語role/KP/Advanced全roleは対象外。
2. **Standard part2の最終wav(Attempt 4)には6%減速が未適用**(LR再TTSがASR NGのままHuman Reviewへ→減速はstatus=OK後のみ)。part1/part3/in_one_lineは実測5.87〜5.98%減速済み。part2の `_original.wav`(50.32s)は初回TTSの残骸。
3. Audio Validation Gateの `_segment_missing_mandatory_a2_slowdown` は part2 を「減速済み」と誤判定(残骸 `_original` と比1.0453が許容[1.03,1.09]に合致)。`full_story_part3` は `A2_SLOWDOWN_TARGET_SEGMENTS` に無くGate検査対象外。
4. 「Attempt 4」は資料で2種類(part2_review/採用記録=LR再TTS、attemptsフォルダ名 `attempt4_minimalfallback`=fallback)。ユーザー採用はLR再TTS(TTS通算5回目、52.6s、sha 3231abd8)。
5. Attempt 4 = **LRによる原稿変更(`US data`→`data from the United States`の1箇所のみ)+minimal fallback関数経由の再TTS**。ただしStyleはAttempt 1と逐語同一(F1.5+減速指示327字)でminimal wrapperなし。`two→2`/`nine→9`/引用符除去は全attempt共通のTTS入力正規化(委任_09記録の差分帰属は修正が必要)。main版コードなら簡略化style(OPEN-274)になる。
6. 異音検知Trial: segment 60本+assembled 2+公開mp3 43を解析。clip 0、abrupt dropout 0、edge 0。音響系候補はlow中心(segment 24件、medium以上3件)。注入19ケース中15検出。ユーザー報告の coffee 付近(episode 265.45〜265.71s)は**検知器では検出できなかった**(語の窓指標は他のcoffee 9箇所と同範囲、1.8秒後の`hidden`→whisper `hitting`が最近傍候補)。人間試聴が必要。

## 推測/未確認
- 聴感上のpart2の速度差・coffee/hiddenの違和感の有無(試聴待ち)。Azureの`raw bean→Robbing`が真の読み違いか誤転写か。送信バイト列そのもの(ログ200字切詰め、コード経路から再構成)。

## 新規仕様候補・要判断(実装せず報告のみ、SSOT未更新)
(1) Gateの減速検査の穴2件(残骸`_original`の弱い証拠規則、part3未登録)。(2) part2を減速するか(後処理のみで可能だがPart 2は最終承認扱いにしない方針)。(3) ログ固定ラベル `instruction: minimal (not ENGLISH_STYLE_PREFIX)` が実Promptを反映せず誤認を招く。(4) 異音検知を非ブロッキング警告としてValidatorへ組込む案(clip/abrupt dropout/edge中心。条件A=Opus独立レビュー+ユーザー承認が必要、`APPROVED_FOR_PRODUCTION`ではない)。(5) 委任_09 adoption記録の差分帰属補正。
OPENとの関係: OPEN-270(減速後検証の外側ループ)は本調査の事実整理と整合(TTS 5回)、是正案には触れていない。OPEN-274(LR再TTSがminimal fallback関数に依存、main/branchでStyle差)を実証拠で裏付け。OPEN-275(Azure費用補正)は無関係で触れていない。

## 検証・証跡
Playwright(公開URL)64 audio全PASS、ジャンプ13/13 PASS、PNG/mp3 124件HTTP 200、console error 0、HTTP>=400 0(`PLAY_EVIDENCE_01C.md`)。main commit `92bf1abe`(静的ページ+調査成果物+スクリプト)。モデル/ライブラリ: API未使用。numpy 2.5.1 / scipy 1.18.0 / soundfile 0.14.0 / lameenc 1.8.4 / Pillow 12.3.0 / faster-whisper 1.2.1(small、CPU int8、local_files_only)。最新モデル原則: モデルAPI呼出なしのため対象外。

## 禁止事項遵守の自己申告
`git add -A/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f: 不使用(`docs/pm/ACTIVE_TASK_..._C.md` は.gitignore対象のため非commit)。有料API・LLM呼出なし。worktree変更なし(importは`-B`、PYTHONDONTWRITEBYTECODE)。Production/Prompt/Validator/Routing/SSOT編集なし。
