# RISK-FLAGGER-PRODUCTION-WIRING-01 委任_15 (META再生成、L3比較用) 2026-10-11

使用モデル: Sonnet 5.5(実行層)。Writer/RF等のProduction経路モデルは正式配線どおり(R0 gpt-6-luna、R1/R2 gpt-6-astra、RF luna+gemini-3.5-flash-lite)。仕様・Prompt変更なし。

## 経路
- ledger再利用: er019_family_x_entertainment_production_runner_01.run_research_and_ledger が out_dir/research_ledger/verified_fact_ledger.txt 既存なら再利用(正式サポート、コード確認済み)。旧run_03のresearch_ledger/(15 facts, V15)を er019_output/meta/run_regen_01/research_ledger へ複製。
- テーマ文は旧researcher_full_record.jsonのpromptから抽出: 「Meta Muse AI電話代行「人間コンシェルジュ」実験」(er053_output/.../meta_regen_01/theme.txt)。
- entertainment: `--slug meta --out-dir er019_output/meta/run_regen_01 --run-label meta_regen_l3 --budget-jpy 150 --stage all` -> 全stage OK、Mandatory STOPまで。費用 JPY38.46(by stage: b3 0.41/r0 0.31/r1 18.65/r2 16.28/adv 0.35/std 0.63/RF計1.84)。
- audio: `--slug meta --run run_regen_01 --stage all --budget-jpy 100 --tts-backend speech_metadata_flash_lite` -> scaffold OK / 三者sha一致(a2,b1b) / tts完走 / **assemble STOP(a2: japanese_title=STOPPED)**。
- 追加でb1bのみ `--level b1b --stage all` を再実行 -> tts再走でb1b comment_2が `ASR_VALIDATION_UNCERTAIN`(1 attempt)となり assemble STOP(comment_2=UNVALIDATED)。**この再実行は私の判断で、結果として初回に OK だった b1b comment_2 の状態を上書きした(不要な再実行だった)**。初回の状態は audio_stdout.log に残る。
- 完成wav/player.html: 生成されず(a2/b1bとも assemble 未到達)。

## STOP理由(既存安全装置、回避していない)
- a2 japanese_title「AIの電話に人間が出演。問題は「キャスト変更」のお知らせでした」: 標準2回+fallback1回(上限3回)とも ASR が「出演」を「出現」と転写 -> TRUE_CONTENT_MISMATCH -> STOPPED -> Audio Validation Gate が assemble をブロック。
- b1b: comment_2 / in_one_line で ASR が固有名詞 "Muse" を "use/user" と転写(connected speech/local rewrite recovery が in_one_line で発火、comment_2は最終UNCERTAIN)。
- いずれも Gate/retry上限の正規動作。上限回避・手動承認・コード変更は未実施。

## runtime evidence
- ja_writer/runtime_evidence.json: chain_method=W-1(factlock_r0_luna__astra_r1_r2_independent)、R0 gpt-6-luna、R1/R2 gpt-6-astra(model_mismatch false)、producer deterministic_v2(LLM 0 call、rules_sha 525f2309..)、symbol_qa findings 0。
- RF: b1b luna A3=2/A4=4, gemini A3=0/A4=0 -> issue4。a2 luna A3=1/A4=5, gemini 0/0 -> issue6。model_id=gpt-6-luna / gemini-3.5-flash-lite。Queue: review_queue/post_en/meta__run_regen_01/{b1b__rf20261010T153209Z-bdfa,a2__rf20261010T153335Z-8c45}。旧Checker非発火。

## 費用(実測、runnerログ)
entertainment 38.46 + audio 16.99(1回目14.16+b1b再実行分2.83、runner累計表示) = 55.45。L3累計110.43+55.45=165.88。合計600に対する残 434.12。本委任上限250内。

## 観測事項調査
1. a2_derived_from_advanced_sha_mismatch: 原因特定=Windowsの改行変換。er012 runner は `sha256_text(advanced_text)`(メモリ上のLF文字列のUTF-8)を記録し、save_text(text mode "w")が\nを\r\nでディスク保存、audio runner `_derived_sha_warning`(er019_family_x_audio_production_runner_01.py L1912-1928)は `file_sha256`(raw bytes)で b1b/article.md を比較するため、CRLF有無でshaが必ず不一致になる。確認: coffee b1b/article.md rawは CRLF含有でsha 5e8979df、text読みLF正規化で 2c627b38(記録値と一致)。META再生成でも同じ(raw c6318609 vs LF 8bd506a6=記録値)、同警告が出た。M1(a)変換やstdregenは無関係。観測専用警告のため影響なし。Windows環境では常時発火する偽陽性。
2. retry_count=0でattempt2が残る: 仕様どおり(ただし紛らわしい)。segmentレコードの retry_count/call_count は `er003_b1_p9a_audio.generate_narration_snippet`(L288)等が返す「最後に採用された1回のTTS呼出内の技術API retry回数」(_call_tts_with_retry由来)で、ASR不一致に基づく再生成ループ(attempts_log)は外側。`{**r, "attempts_log":...}`で最終attempt分のみ載るため、attempts_log長>1でも retry_count=0/call_count=1。実際のTTS呼出総数は attempts_log 長(+fallback)で数える必要がある。不具合ではなくメトリクス定義の混乱。OPEN候補案(起票はFable判断): 「segmentレコードのretry_count/call_countが最終attempt分のみで、ASR再生成の累計(cumulative_tts_attempts)と不整合。報告・集計用には cumulative_tts_attempts を正とする旨の注記または累計フィールド追加を検討」。

## 旧META vs 新META 比較(Sonnetの読解による分析。人間判定ではない)
旧=er019_output/family_x_refresh_e2e_01/meta/run_03(2026-09-29、旧Writer+旧Fact Checker世代、旧ja=revision2.md)。新=er019_output/meta/run_regen_01。ledgerは同一(15 facts)。
- (a) Storyline: 旧=「実験→ユーザー情報共有懸念+開示不足→ミス認定→ロールバック」(懸念と開示不足の2要素を主張に含む)。新=「一部をテスト→開示なしを『ミス』と認めロールバック」(開示一点に絞る)。新はdeterministic producerの制約(事実1「全部ではない」、事実2「サービス全体停止ではない」)を明示。
- (b) Fact選定: 旧=HC-006/010/012(3件、10=プライバシー懸念)。新=HC-006/012(2件)。HC-010を落とした。旧JAは選定外のHC-004(散髪等)・HC-011(人種発言報告)も本文に使っていた(旧Writerはledger全体参照)。新は選定2件の範囲に収まり、004/010/011は不使用。
- (c) エンタメ性(記述): 旧=「どんでん返し」の導入と「舞台裏」の反復はあるが、全体は報道調で比喩は弱い。具体例(散髪予約・在庫・見積)あり、締めは教訓型。新=「SFからお仕事ドラマへ」「キャスト変更」「番組の打ち切りとコーナー休止」「シークレットゲスト」と一貫した番組/配役比喩を導入から落ちまで通し、ツッコミ口調あり。具体的事例(散髪等)は無く、事実量が少ない分、比喩と論点整理(全部人力ではない/機能のみ撤回)で構成。読み物としての起伏は新が大きい一方、事実密度は旧が高い。
- (d) Fact保持: 数値・日付は本記事のbrief範囲に無く(旧新ともJA/Adv/Stdに数値・日付なし)、改変なし。固有名詞: Meta/Muse/Superintelligence Labs(新JAに保持、旧JAは「Metaの幹部」)。新Std ENは「paused」(ロールバックの言い換え、軽微な弱化)、Advは「rolled back」。旧は「restored ... to the way it had been」。欠落: 新は事実HC-010/011/004の内容を扱わない(選定外のため仕様どおり)。
- (e) 制約文漏れ: 新旧とも JA(original/revision1/revision2)・Adv・Std に「事実N」「について：」「【事実」「MUSE-HC」「Writerへの注意」等の漏れ0(grep確認)。旧でも本ファイル群には漏れなし(旧で問題だった混入が過去版に限られるか、本比較では旧revision2に見当たらない)。新は漏れなし。
- (f) RF: Adv issue4(luna A3=2/A4=4、gemini 0/0)=s5「相手側で依頼を処理した人」(主体入替0.3)、s18「They did not stop all calls through Muse」(不在断定、A3 0.34+A4 0.3)、s26「人は言葉選びや感じ方が変わる」(台帳外の一般化0.25)、s34 In one line「without telling the people they called」(開示対象の特定0.35)。Std issue6(luna A3=1/A4=5、gemini 0/0)=s5、s21(全電話停止せず)、s24「人間への引継ぎが会話を進める」(台帳外効果0.2)、s30/s31(感じ方の変化の一般化0.2)、s41(In one line、0.7)。gemini2条件はともに0件、luna単独検出。旧METAはRF配線前のため比較RFなし(旧Fact Checker世代)。
- 総括(分析のみ): 新は制約遵守と構成は良いが、台帳外の一般論(人は感じ方が変わる等)と「Muse経由の全通話は止めていない」という断定がRFで候補化されている。「Meta自身がミスと認めたのは開示の点」はHC-012に整合。

## 改善案候補(未実施、報告のみ)
1. 固有名詞「Muse」のASR誤転写(use/user)でcomment_2/in_one_lineがgate/local rewriteに掛かる: Muse読み・ASR許容(pronunciation/ASR hint)追加候補。JA「出演」→「出現」のASR誤認識は日本語読み辞書/同音許容の候補。
2. a2 title STOPPED時の運用: 再生成/Writerタイトル差替のoperator手順をRunbook化するか、title用の同音異義許容の検討。
3. a2_derived_from_advanced_sha 警告のCRLF偽陽性: 比較時に正規化するか、記録側をraw bytes shaに揃える(観測専用)。
4. retry_count/call_countの累計化または注記(上記)。
5. 新Writerの台帳外一般論(「人は感じ方が変わる」等)を抑える制約。
