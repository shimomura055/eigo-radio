# RISK-FLAGGER-PRODUCTION-WIRING-01 委任_09 = SSOT記録(main) + Phase 2 C3 実装(feature branch)

- 日付: 2026-10-10 / 実行: Sonnet(実行層) / **課金API 0件**(RF/TTS/LLMは全てstub)
- 設計正本: DESIGN_03(+15-2是正)、委任ログ_06/_07/_08の持ち越し。
- 使用モデル(PM_GOVERNANCE 25節): 本作業のLLM呼出0件。コード中の予定モデルはC1/C2固定(W-1 R0 gpt-6-luna / R1,R2 gpt-6-astra / RF gpt-6-luna・gemini-3.5-flash-lite)。

## 0. git手順の実績
1. mainで確認(HEAD f71dbb41)後、SSOT 3ファイル(DECISION_LOG末尾3エントリ/OPEN_ITEMS OPEN-244・248/REPORT_LEDGER 2行)を明示addして1 commit、`git push origin main` -> **0982498d**。
   `docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は.gitignore対象(一時ファイル)のため更新のみ(commitなし)。
2. `git checkout feature/factlock-rf-wiring-01` -> `git merge main`(通常merge、競合なし、merge commit d86d08a9)。
3. C3を論理単位で commit(明示add、`-A`/`-f`未使用) -> push -> `git checkout main`。rollback tagは付与していない(merge時に案Y)。
4. 他agent由来のuntracked/modified(ROOTFIX-02の`er052_output/b3_rootfix_trial_02/`、`docs/pm/RESULT_PACKET_B3SEP2_*.md`等)は不触・不add。
   テスト実行で変化した追跡ファイル2件(er005 cost_summary.json / er025 telemetry.jsonl)は`git checkout --`で原状復帰。

## 1. 実装(C3-1〜C3-5)
| ID | 内容 | 場所 |
|---|---|---|
| C3-1 | scaffold時に元記事sha256を`out_dir/audit/scaffold_article_sha256.json`へ記録 / TTS直前`ensure_rf_record`で三者照合(scaffold sha == source記事sha == Queue(index.jsonl、およびQueue保存失敗時のsource_dir/risk_flagger_fallback)のsha)。不一致またはQueueなしならその場でRF実行(非Blocking、Level明示、producer=W-1 evidenceの注記manifest producer、run_label=`audio_tts_guard[:<label>]`)+Queue保存。S3-2(a2派生元sha不一致)は警告記録のみ。結果は`out_dir/audit/rf_tts_guard.json`・entry_point.json | audio runner `record_scaffold_article_sha`/`ensure_rf_record`/main tts分岐(`assert_production_tts_backend`直後、`cl.logging_context`の外) |
| C3-2 | `_load_pricing().price()`が`StopIteration`を`routing.PricingNotFoundError`へ(efam側と同じ)。`compute_cost_jpy_so_far`の`except StopIteration: usd=0.0`撤去。`cost_usd`付きレコードは従来どおり実額採用。RF Geminiレコードに`cost_usd`(G-2式、cached割引込み)を併記(model_id=pinned、output_tokens=thinking込み) | audio runner / RF module `_record_gemini_cost(prices=)` |
| C3-3 | entertainment runner `_write_cost_json`を`er053_cost_aggregate_01.compute_stage_cost_breakdown_multi`へ切替(by_stage_jpy/total_jpy互換+by_provider_jpy+RF Level別内訳)。旧`compute_stage_cost_breakdown`は他経路用に残置 | entertainment runner |
| C3-4 | Astra 4エントリのnoteを「W-1 Production採用(2026-10-10ユーザー決定)、Production予算ガードは請求照合(OPEN-246)まで係数1.0、Cap設定にマージン」へ。価格値不変(10/1/50/12.5) | pricing_snapshot.json |
| C3-5 | `_IndexLock`の`except (FileExistsError, PermissionError)` | er053_review_queue_01.py |

## 2. 解釈・判断メモ(Fableへ)
1. **audio runnerにはstage別cost.jsonが存在しない**(最終printの`compute_cost_jpy_so_far`のみ)。C3-3の「audio runnerの呼出側」は、audio側の集計
   (`compute_cost_jpy_so_far`、openai_asr・Batch cost_usdを含む)をG-4でfail-closed化しRF Geminiレコードを実額採用させる形で充足と解釈した。
   audio側に`er053_cost_aggregate_01`の集計を導入しなかった理由=(a)multi版はopenai_asr/gemini_batchを数えず過少表示になる、(b)er053_cost_aggregate_01はefamをimportし、efamはaudio runnerをimportするため循環import。新ファイル(audio cost.json)は作っていない。
2. **article_id整合**: Writer側`derive_article_id(out_dir)`とaudio側`derive_article_id(source_dir)`が同じ値になるのは、writerの`--out-dir`が`er019_output/<slug>/<run>`(audioの`--slug/--run`が指す`source_dir`)のときのみ。別パスに出力した記事は照合で「Queueなし」と判定されTTS前にRFが再実行される(安全側。RF 1記事1Levelの実費はE2E実測前のため未確定)。運用手順の確認事項。
3. **scaffold後に記事を変更した場合の再実行コスト**: scaffold shaは更新しないため、記事がscaffold後に変わると以降の`--stage tts`実行ごとに「scaffold sha != source sha」でRFが再実行される(仕様どおり安全側)。再scaffoldで解消。繰り返しTTS再実行時のRF重複費用が気になる場合は仕様判断(未実装)。
4. **scaffold sha未記録(C3以前にscaffold済みのrun)**: `scaffold_sha_missing`として扱いRF実行(安全側)。
5. RF予算超過STOP(`BudgetCheckStop`)・記事sha変化(`ArticleModifiedError`)は握りつぶさず伝播(既存安全装置を回避しない。stub E2E S6で確認)。
6. 既存test更新: `er053_cost_aggregate_01_test_01`(HEAD比較テストでAstra noteのみ許容)、`er053_family_x_factlock_ja_writer_01_test_01`(audio runnerにRF module+Review Queue moduleだけの参照を許可、W-1・契約moduleは不可のまま)。
7. 新仕様候補: なし。Prompt・schema・contract変更: 0件。

## 3. 検証(詳細: `er053_output/risk_flagger_production_wiring_01/`)
- `c3_test_results_01.md`: C3+C2 set 644 passed / 14 skipped / 0 failed(C2 baseline 610)。全suite 36 failed / 5781 passed(36件はC2で分類済みの既存32+順序依存4と一致、新規failure 0、C2時のflaky queue test解消)。
- `stub_e2e_c3_01/summary.json`(`run_stub_e2e_c3_01.py`): Writer main -> RF -> Queue -> audio scaffold -> `--stage tts`単独の6シナリオ。S1三者一致=RF再実行なし(API 0) / S2 Queueなし=audio側でRF実行(Level別、run_label=audio_tts_guard、producer記録、Queue保存)->TTS / S3 再実行は照合一致 / S4 a2のみ変更=a2のみRF / S5 RF全滅でもTTSへ / S6 予算超過でRF STOP。audio費用: RF Geminiレコード全成功分にcost_usd(0.0032 USD/call = 4000in*0.30+800out*2.50)、集計で採用。
- `dangling_after_c3.json`: Fact Checker専用シンボル 0(技術QA語彙11・Opus所見ラベル25=C2と同一、孤立0)。
- `pricing_coverage_audio_c3.json`: G-4前提(Production全model単価網羅)。
- C3-5再現: pre-fix 1/6 runでPermissionError、post-fix 0/15 + pytest PASS。

## 4. 禁止事項の遵守
Agent起動なし。課金API 0件。rollback tag未付与。SSOT(CURRENT_SPEC)・Prompt・schema未変更。mainへのC3 merge未実施(featureブランチ限定)。
