# DESIGN_01 (FZ-NARRATION-CHUNK-TTS-TRIAL-01 委任_01 Phase 0、API 0・Production変更0)

状態: 設計のみ。**有料生成は開始しない**(次委任=Opus条件Aレビュー後のFable Go)。原文=`docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-TRIAL-02_USER.md` §3〜§8。既存仕様照合=`EXISTING_SPEC_CHECK_01.md`。Status=`TRIAL_DESIGN_PENDING_OPUS_A`。Trialであり`APPROVED_FOR_PRODUCTION`ではない。

## 1. 構成(DEV専用、Production fileの編集0)
| 物 | path | 備考 |
|---|---|---|
| planner(決定論、Phase 0実装済み) | `er114_fz_narration_chunk_trial_01.py` + `er114_fz_narration_chunk_trial_01_test_01.py`(6件PASS) | 純粋関数。Production moduleは読取importのみ(`er062`のtitle/段落分割)。出力=DEV dirのみ |
| 出力dir | `er026_output/family_z_dev_trials/fz_narration_chunk_01/` | `chunk_plan_*_01.json`、`clip_distribution_01.json`(+Phase 1以降で`gen/`,`sinks/`,`measure_01.json`) |
| 試聴ページ | `user_test/fz_narration_chunk_trial_01/index.html`+`audio/*.mp3`(Phase 1後に生成) | `user_test/`配下のみ追跡可 |
| 読取専用入力 | 下記§3の本文・音声 | 書込禁止、before/after sha256で不変確認 |

## 2. 分割規則(Phase 0で決定、決定論)
**対象**: Advanced(`b1b`)のnarrator story clipだけ。Dialogue/話者切替clip(voice≠narrator)は**一切変更しない**(既存plan_clipsの境界は入力としてそのまま受け、narrator clipの内部だけを見る)。Std・KP・Comment・Previewは対象外。

**閾値**: clip語数 > **100語** のnarrator clipのみ分割。
- 根拠1: 既存`plan_story_segments`の`target_words=100`(`er013_family_c_production_01.py:306-326`)と同値で、新しい独自数値を作らない。
- 根拠2: 全作品Advのnarrator clip(59本)の語数別WPM(`EXISTING_SPEC_CHECK_01.md` §2): <30語127、30〜59語156、60〜99語160、>=100語163。長いほど速い傾向の増分は60語超では小さく(+3〜7 WPM)、>=100語の3本が最も高い。
- 根拠3: 閾値100語で分割対象になるのは『告げ口心臓』(135/118)と『賢者の贈り物』(123)だけで、セリフが多く既存分割が細かい作品(猿の手最長71語、開いた窓45語、二十年後74語)には何も足さない=『必要十分』。
- 閾値を下げる(例: 60語)と、分割対象clipが増えるが、WPM差の増分が小さい(60語超)のに接続点が増えP6B不合格の論点(声質の一貫性)のリスクが増える。上げる(例: 150語)と、『告げ口心臓』の分割対象が0になり検証にならない。

**分割数**: `k = ceil(語数/100)`(135→2、118→2、148→2、123→2)。大半は2 chunk。

**切る位置の優先順位**(`plan_clip_chunks`):
1. 段落境界(clip内の段落の切れ目=Writerが付けた場面・意味のまとまり)を最優先。
2. 段落境界で最小chunk語数(25語)を満たす候補が無い場合のみ、段落内の文境界(文末の`. ! ?`の直後)。**二重引用符の途中(未閉じの引用)は候補から除外**。
3. 同優先内は、残り語数をk等分した目標語数との差が最小の位置。
4. 固定文字数・固定秒数による一律分割はしない。最小chunk語数25語(Xの最短chunk14語で『文脈なし短文のTTS品質』が論点になったため、より大きく取る)。満たす位置が無ければ分割しない(不変)。
5. 結合検証: chunkを`" "`連結すると元clip.textと完全一致(欠落・重複0、planner内`assert`+test)。

**接続**: chunk間の追加無音=**0.2秒**(ユーザー指定、既存のZ story clip gapのうち『voice≠narratorの後』と同一秒数で新規独自秒数ではない)。元clipの後ろのgap(narrator=0.5秒、Comment挿入時1.0/0.8秒)は既存のまま。音量=chunkごとに同一`target_rms`へ`compute_gain_for_target_rms`(独立TTS出力ごとの承認済み適用単位。Xと同方式)、結合=`np.concatenate`のみ。crossfade・EQ・コンプなし。

### 2-1. 『告げ口心臓』への適用結果(`chunk_plan_*_01.json`、Phase 0で生成・test固定)
| 対象本文 | clip | 語数(段落数) | 分割後chunk語数 | 切る位置 |
|---|---|---|---|---|
| Trial 1b_s1 Adv(一人称) | part1_c1 | 141(4) | 78 / 63 | 段落境界(『I loved him…A vulture's eye…That eye had to go.』の後=段落2末、独白の導入→7夜の描写) |
| 同 | part2_c3 | 118(6) | 69 / 49 | 段落境界(『It grew faster. Louder. Surely a neighbour would hear!』の後、『I rushed in.』の前=心音の知覚→行動) |
| 同 | part3_c1 | 148(6) | 74 / 74 | 段落境界(『Beneath their voices came a low, quick beating.』の後、『I talked louder.』の前) |
| 同 | part2_c1/c2(5語+セリフ2語) | — | 不変 | 話者切替境界(不変) |
| 現行run_sf_prod_01 Adv(三人称、参考) | part1_c1 135 / part2_c3 118 | — | 85/50、57/61 | 段落境界。part3_c1(91語)以降は閾値以下で不変 |
(1b_s1: 3 clip→6 chunk。Xの10 chunk[14〜63語]より粗く、長さは49〜78語。全て段落境界で切れ、文・引用の途中での分割は0。)

## 3. 対象本文の選択(重要: 並行案件との競合回避)
別案件 FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01(OPEN-508、委任_04)が、案A配線後に『告げ口心臓』Std/Advを新run `run_sf_prod_02`として正式再生成する予定(未生成を確認)。

| | 案(i) 正式再生成後の新Adv本文を読取専用で再利用 | 案(ii) Trial 1b_s1のAdv(音声あり)をAとして使う |
|---|---|---|
| 本文 | 正式採用候補と同一(以後の公開版に近い) | 案Aの一人称Trial本文(正式再生成とは別take/別本文の可能性。ただし同一Seed・同一Writerの一人称) |
| 待ち時間 | 委任_04のOpusレビュー→実装→再生成(約40円)完了待ち。完了時期は未定 | なし。すぐ開始可 |
| Aの音声 | 正式run(`run_sf_prod_02`)の既存clip wavをそのまま使える(新規A生成0。Gate済み) | `1b_s1/b1b/narration/full_story_part{1_c1,2_c3,3_c1}.wav`が存在(Gate/HR状態は要確認[§5で確認項目]) |
| 競合リスク | 完了後は競合なし。完了前は不可 | 1b_s1 dirは読取専用なら正式再生成と干渉しない(別dir) |
| ユーザー試聴の意味 | 最も高い(最終採否が実際の公開物に直結) | 高い(同じ一人称・同規模clipで、効果とリスクは本文差が小さい) |

**推奨: 案(ii)で先に開始し、案(i)は『分割規則と判断結果の確認用』として任意で追加**。理由: (1)Charter原則2(最速)、(2)本Trialの分割規則は本文の言い回しではなく語数・段落構造に依存する決定論ruleで、1b_s1(一人称・3つの長いclip 118〜148語)は正式再生成Advと同種の構造(同じSeed・Writer)、(3)正式再生成の完了を待つと、ユーザー試聴の時期が不定になる、(4)案(i)を後から実行しても、plannerをそのまま再利用でき追加コストは約4円/arm。
案(ii)の注意: 1b_s1のAは『Trial生成take』であり、正式Std/Advとは本文が一致しない可能性がある。ユーザーに『本文は異なるが同種のAdv』と明示する。正式再生成の完了後、本文が1b_s1から大きく変わった場合のみ、案(i)で確認用の追加Trialをするかを判断(**判断候補**ではなくFable判断範囲)。

**隔離・競合回避(両案共通)**:
- 書込先は `er026_output/family_z_dev_trials/fz_narration_chunk_01/` と `user_test/fz_narration_chunk_trial_01/` のみ。Production run dir(`family_z_production_e2e_01/*/run_sf_prod_*`)・Production store・公開ページへ書き込まない。
- Production sinkはXのTrialと同様にDEV dirへプロセス内で向ける(`redirect_production_sinks`: review-lock attempt history、HR queue、ASR semantic equivalence telemetry、entity pronunciation telemetry、cost logger[Trial専用`raw_usage_log.jsonl`])。before/afterのsha256を`PROTECTED_STORES`(attempt_history、human_review_queue、telemetry×2、master_audio_store manifest/reuse_telemetry、pronunciation ledger、cost_summary、negative_cache)と`PROTECTED_TREES`(`run_sf_prod_01`、案(i)なら`run_sf_prod_02`、1b_s1、公開ページ`user_test/`のFamily Z公開dir)で比較し、1つでも変化したら即STOP・事実報告。
- **TTS直列化**: 本Trialの有料生成は、別案件のFamily Z正式TTS(`tts_b1b`/`tts_a2`)のプロセスが走っていない時間帯に限る(起動前に`tools/stop_scope_check_01.py`とプロセス一覧で確認、同時刻に走っていれば待つ。Z runnerの直列化運用、`RESULT_PACKET_FXZ2W1.md:30`に準拠。Gemini TTSのrate limit・費用ログ・Gate stateを共有しないため、別プロセス・別dir・別cost logで実行する)。
- 正式再生成成果物の再利用: 案(i)では読取専用でAの音声・テキスト・`target_rms`を使う。ファイル移動・上書き・lockは一切しない。
- 他agentのdirty working tree(`git status`多数)には触らない。`git add`は対象pathのみ。

## 4. A/B条件(同一性の対応表。差異は★)
| 項目 | A(現行clip構成) | B(長いnarrator clipのみ追加分割+0.2秒) | 同一? |
|---|---|---|---|
| 本文 | clip.text | clip.textを§2規則で分割(結合=元textを検証) | 同一(分割のみ) |
| TTS関数 | `news_tail_fix.generate_news_narration_wide_margin`(Adv narrator) | 同じ関数を各chunkに | 同一 |
| model/voice | `gemini-3.8-flash-lite-tts`(`tts_backend=speech_metadata_flash_lite`)/ Aoede | 同左 | 同一(最新モデル原則の例外理由=A/B条件同一性) |
| Style | `style_text_for(spec)`(Z role style、`z_v2_pd8_r2_e1_e2up_k2_m2_kpx_20261012`) | 同左(各chunkのspecをnarratorとして作る) | 同一(style_record sha一致を実行時検証) |
| 速度仕様v2 | Adv narrator=後処理なし | 後処理なし | 同一 |
| 品質Gate | 既存のASR judge・RepetitionQA・Connected Speech・Pronunciation resolver | 各chunkで同一関数内蔵のGateを通す | 同一規則(★chunkが短いため絶対許容は小) |
| segment role | `full_story_part{n}_c{k}` → FULL_STORY | 出力ファイル名を元clipと同一(`…/gen/<arm>_<chunk>/b1b/narration/full_story_part{n}_c{k}.wav`)にし、role判定を変えない(Xと同じ手法) | 同一 |
| ★ chunk間文脈 | 1 callで通して読む | 各chunkは独立call(前後文脈なし) | **差異(検証対象)** |
| ★ 接続 | clip内部は1 call、clip間はnarrator後0.5秒 | chunk間=trim残置(約0.24〜0.35秒×2)+0.2秒、clip間は不変 | 差異 |
| ★ 音量 | clipごとに1 gain | chunkごとに1 gain(同target_rms=Aの`target_rms`を維持) | 差異(承認済み適用単位) |
| ★ take | 既存1 take(1b_s1の記録 or 正式run) | 新規take | 差異。**take間ばらつき見積のため分散基準arm A_r2を追加** |
| ★ sink | Production path | DEV dir | 差異(非汚染) |

**arm構成(Phase 1)**: B_r1(主、事前固定)、A_r2(現行構成の別take=take間ばらつき基準)、B_r2(Bの別take)。Aは既存音声。(A_r2・B_r2は、結論を『take違いの偶然』から切り分けるため。Xで必要性確認済み。)
**段階運用(費用最小化)**: ①B_r1+A_r2を並列(別プロセス・別dir、ただし別案件TTSとは直列)→②計測→B_r1の改善が機械的に明確(下記判定基準)かつ接続異常なしの場合のみB_r2。不要なら省略(『改善効果が十分に確認できたら追加の磨き込みをしない』、原文§7)。

**Phase 1のB音声組立(DEV assembler、新規音声加工なし)**:
1. Aの`gain_report.json`の`target_rms`を使う(chunk分割でfirst story clipが変わっても他segmentのgainが変わらない)。
2. `build_z_sequence`(既存)で作ったsequenceのうち、対象clipのエントリを[(id_k1, gs(chunk1)), ("_silence_0.2",…), (id_k2, gs(chunk2))…]へ展開。以後のsilence(0.5秒、Comment前後)は既存のまま。`assemble_with_timeline`・`apply_headroom_safety_valve`を既存のまま呼ぶ。
3. 比較区間(試聴ページ)は『分割した3 clipそれぞれのAとB』+『Part単位のAとB』+『Advanced通し(Intro〜Outro、1b_s1ならKP・Comment含む)』。

## 5. 計測・評価(原文§5①②③)
**① 速度**(Xと同一の計測法、`er113_fx_paragraph_chunk_trial_01.py`の関数を再利用): 全体WPM(全長ベース)、実発話WPM(`art300`/`art500`、閾値に依存しないM4分解[Δ発話区間/Δclip内gap/Δ両端])、追加ポーズによる時間増(B−A、決定的: 分割境界数×0.2秒、1b_s1では3境界=0.6秒)と発話そのものの減速の分離、take間ばらつき(A vs A_r2、B_r1 vs B_r2)。断定規則: 『段落(chunk)単位の比較』と`art300`が同方向で、take間ばらつきより大きい場合のみ断定(Xの`_verdict_speed`と同じ)。
**② 音声品質**: chunk境界の音量差(dB、前chunk末尾1秒vs次chunk先頭1秒)、無音長分布(500ms超ポーズ)、欠落・重複(ローカルfaster-whisper整列[API 0]、ASR語数/台本語数)、既存音声Gate(各chunkの`status`/attempts/classification/RepQA/条件差異フラグ)、ヘッドルーム弁。声質・抑揚の一貫性は機械指標で断定しない。
**③ 物語品質(ユーザー試聴で判断、機械で代替しない)**: セリフ・話者切替の自然さ(不変のはず)、語りの流れ、心理描写の連続性、緊張感・没入感、一人称独白の自然さ、**chunk境界で声質・抑揚が変わって聞こえないか(P6B不合格の論点)**、独白の迫力(特に『I rushed in.』の前後、『I talked louder.』の前後=クライマックス接続)。ページに『ここを聴く』区間を明示。
**判定基準(事前固定)**: 速度=B_r1の`art300`がA比で-3%以上遅い(take間ばらつき以上)ならば『減速効果あり』、接続=境界音量差<=Aのpart境界差の最大値(1b_s1では比較値をAから計測)・語欠け/二重0・Gate全OK・条件差異0。この基準を満たしても**音質改善とは断定せずユーザー試聴で採否を判断**する。基準を満たさない場合は『REJECTED候補』ではなくFableが再計画を判断する。

## 6. 費用・時間見積(Fable上限=30円)
出典: X Trial実績(`BUDGET_LOG_01.md:14-16`): A_r2(3 call)3.98円 / B_r1(10 chunk)4.27円 / B_r2(10 chunk+retry+Azure)5.64円=本文428語の1armあたり約4〜5.6円(TTS+OpenAI ASR+Azure)。分割によるTTS増分は+7%(+0.29円、7 call増)。
- Z(1b_s1 Adv: 3 narrator clip、407語): A_r2 3 call ≈ 約4.0円、B_r1 6 chunk ≈ 約4.2円、B_r2 6 chunk ≈ 約4.2〜5.6円。**3 arm合計 約12〜14円(上限30円に対し余裕あり)**。retry最悪でも約20円。比較対象の追加(案(i)の正式本文で再実行)を含めても約28円で上限内。
- 段階運用(B_r1+A_r2のみ)なら約8.2円で終了する可能性。
- 所要時間: TTSは1 arm約5〜10分(直列)、ローカル整列・組立・ページは約10分。並列化=B_r1とA_r2は別プロセス可(別案件のZ TTSがないとき)。
- **量産単価への影響(採用した場合)**: 閾値100語超のnarrator clipが約2〜3本/作品なので、追加TTS call +3〜4回(Adv)。X実績の1 callあたり約+0.04円より、約+0.12〜0.2円/Advanced、Stdも対象にする場合は同程度の+0.2円で、1記事セット(70円目標)に対し+0.3〜0.6%。処理時間は+数十秒/記事(call増分)。

## 7. 試聴ページ設計(Phase 1後に生成、技術者でないユーザー向け)
`user_test/fz_narration_chunk_trial_01/index.html`: 冒頭に状態(Trial、Production採用ではない)と条件(『同じ本文・声・設定で、長い地の文だけを分けて読み上げた版と比較』)、対象作品・区間の明示。主表示: ①分割した3区間(各: A 現行 / B 追加分割0.2秒)、②Part1・2・3単位、③Advanced通し(A/B)。『聴く観点』=語りの流れ、緊張感、声や抑揚が途中で変わって聞こえないか、速さ。折りたたみ参考=別take(A_r2/B_r2)。速度表(全体WPM/実発話WPM)は簡易表示のみ。開発者向け詳細(M4分解・gain等)は非表示/折りたたみ。mp3は`audio/`配下(`user_test/`のみ追跡)。

## 8. Phase 0で確認が必要な前提(Phase 1の最初に実施)
1. 1b_s1のAdv音声のGate/HR状態(`audit/`内のtts結果。Trial生成のため未Gate/未approveの可能性あり。Aとして使えない場合は、その事実を記録して案(ii)の対象clip音声を再確認)。
2. 1b_s1・`run_sf_prod_01`の`style_record.json`から`style_text_for`のshaが現行と一致(Style同一性)。
3. 別案件のZ TTSプロセスが走っていないことの確認(`stop_scope_check_01.py`、プロセス一覧)。
4. PROTECTED_STORES/TREESのbefore snapshot。

---

# 委任_02 改訂(2026-10-25、Phase 1。Opus条件Aレビュー結果=OPUS_REVIEW_01.md反映。**有料生成の前に固定**)

状態: Status=`TRIAL_PAID_RUN_PENDING`(commit後に有料生成)。以下の§9〜§13が§3〜§6を上書きする箇所は明示する。Trialであり`APPROVED_FOR_PRODUCTION`ではない。上限30円(ユーザー承認)。

## 9. arm構成(Fable決定、事前固定)
| arm | 内容 | 音声 | 見積 |
|---|---|---|---|
| A | 既存1b_s1 Adv(1 call通し、生成済み・status OK・Gate RESOLVED) | 再利用のみ(新規0) | 0 |
| A_r2 | Aと同条件の別take(3 clipを各1 call)。take間ばらつきの基準 | 新規 | 約4.0円 |
| B_r1 | 主規則: k=ceil(語数/100)・最小25語・段落境界>文境界・引用途中除外 +0.2秒(3 clip→6 chunk[78/63,69/49,74/74]) | 新規 | 約4.3円 |
| B_fine | 細分割: k=ceil(語数/50)・最小25語・同じ優先順 +0.2秒(3 clip→9 chunk[36/42/63,44/25/49,57/35/56]) | 新規 | 約4.3円 |
| B_alt | part2_c3・part3_c1だけR1の代替切断(手動plan、段落境界)で切り直し。part1_c1はB_r1のchunk音声を再利用 | 新規(4 chunk) | 約3.0円 |
- B_r2(主規則の別take)は行わない。plannerの決定論規則は不変(`target_words`引数とmanual関数の追加のみ。既定値=従来と同一)。
- B_altの手動plan(事前登録): `chunk_plan_tth_1b_s1_adv_B_alt_manual_01.json`。part2_c3は段落P5〜P10[30/14/2/23/27/22語]の**P7「Wide open.」の直後**で切る→46語/72語。part3_c1は段落P11〜P16[32/25/17/18/35/21語]の**P12「You see how little I feared?」の直後**で切る→57語/91語。いずれも段落境界・引用外。切断位置は本文(1b_s1/writer/r2.md)を見て、Opusが挙げた「約43/75」「約57/91」に最も近い段落境界として固定した(結果を見て変えない)。
- 実行順: 無料修正→commit→①B_r1+A_r2→計測→②B_fine→③B_alt。**各arm起動前に累計+予約額(見積x1.5)が30円を超える起動はしない**。同一runの再起動なし(各armは1起動)。
- 合計見積約15.6円(予約額ベースでも30円内)。

## 10. Opus必須N1〜N4の反映(対応表)
| ID | 反映内容 | 実装 |
|---|---|---|
| N1 | X隔離M1〜M3を引継ぎ(新規実装しない): `redirect_production_sinks`(er113)を再利用=sink4種+Pronunciation Ledgerのコピー切替(negative_cacheも追随)+`run_local_rewrite_recovery` wrapperでout_dirをDEV化。cwd==ROOT assert。Ledger hint/low-confidenceの事前計算(Z TTS入力・Z Styleで全chunk+A_r2)が空でなければSTOP。監視に`negative_cache.json`・`er009…human_review_queue`・`er011_output/local_rewrite_recovery`tree。gen_resultに`instruction_type`/`local_rewrite_recovery`/`canonical_text_before_local_rewrite`/`style_prefix(sha)`/`tts_model_id`を記録 | `er114_fz_narration_chunk_trial_02.py` `cmd_gen`/`ledger_preflight`、`X.PROTECTED_STORES`(再利用) |
| N2 | `sys.addaudithook`で自プロセスの書込みopen/remove/rename/mkdir/copy/Popenを記録、許可dir(`OUT`、postは+`PAGE_DIR`・HFcache・temp)外は例外で阻止+即STOP。mtime走査・sha比較は補助(差分→STOP・事実報告、自動続行なし)。起動時にimportされる全repo module(約130)のsha256とgit未commit差分を記録、TTS/組立経路moduleが未commitなら5分間隔で最大30分待ち、解消しなければSTOP。終了時に再確認 | `_audit_hook`/`module_identity`/`wait_modules_clean` |
| N3 | (1)target_rms=1b_s1 `timeline.json` gain_report.target_rms(0.07332)に固定(再計算しない。参考として(preview+part1_c1)/2との差を記録)。(2)展開後の並びを`k1, _silence_0.2, k2, (既存0.5/1.0), Comment 2`とassert。(3)A_r2の音声sha256≠Aのsha(Aの`61957c46…`ほか)をassert・記録 | `dev_assemble`/`cmd_post` n3 |
| N4 | 判定基準の基準点をAの同じ段落境界位置に変更(§12) | `judge_all` |
| R1 | B_alt arm(手動plan事前登録)。試聴ページに「part2_c3/part3_c1の切断はクライマックス直前の最悪ケース負荷テスト」と明記。不合格でも方式全体のREJECTと即断しない | §9 |
| R2 | 閾値100語の正当化に本Trialの結果を使わない(1b_s1の3 clip[141/118/148語]は閾値を6〜117語のどこに置いても同じ分割対象)。検証対象は『約70語のchunk+0.2秒』と『約47語のchunk+0.2秒』 | §12末尾 |
| R3 | B_fine arm採用 | §9 |
| R4 | chunkごとの中央値F0・スペクトル重心をAの同じ区間と並べて「参考値・判定なし」で表示(自己相関簡易推定、閾値/Gateにしない) | `f0_and_centroid` |
| R5 | plannerに`paragraph_info_lost`フラグ、`sum(chunk words)==clip word_count` assert(test追加) | er114_fz_narration_chunk_trial_01.py |
| R6 | 試聴ページに「OPEN-508案A本文の試聴とは別ページ」「本文はTrial版で正式再生成版とは異なる。本ページは読み上げ方式の比較のみ」「本文の良し悪しはここでは判断しない」を明記 | `build_page` |

## 11. DEV assembler(N3)・書込み先
- 組立: A側run_assemblyのDEV版(`dev_assemble`)。A側`build_z_sequence`(既存関数)でsequenceを作り、対象clipのentryをarmの音声へ差替え(chunk間は`_silence_0.2`)。`assemble_with_timeline`・`apply_headroom_safety_valve`は既存のまま。**Aのみ再組立してオリジナルのtimeline(全長273.789秒・各pieceのstart)と一致することを検証済み**(無料)。
- 書込み先は`er026_output/family_z_dev_trials/fz_narration_chunk_01/`と`user_test/fz_narration_chunk_trial_01/`のみ。Productionのrun dir・store・公開ページ・並行案件の`run_sf_prod_02`へは書かない。Xの比較ページ(`user_test/fx_paragraph_chunk_trial_01/`)は**編集しない**(Zページ→Xページの片方向リンク。Xページ側からZへのリンクは書込み先限定のため追加しない)。

## 12. 判定基準(事前固定。N4反映。合否でなく『基準到達/未達/判定不能』の機械判定)
1. **速度**: 段落単位span(16段落=3 clipの段落、X M4と同じ考え方)で比較。
   - 基準ノイズ D_noise = 平均(段落span比 A_r2/A) − 1(同一方式の別takeとの差=take間ノイズ)。
   - 「基準到達(減速効果あり)」= art300(B)/art300(A) ≤ 0.97(3%以上遅い) かつ 段落span平均比(B/A)−1 > 0(Bが遅い方向で一致) かつ |D_B| > |D_noise|。
   - 「未達」= Bが速くなる/同じ(art300比>1.0かつ段落span比<1)。それ以外(閾値到達と段落spanの方向が不一致、またはノイズ以内)=「判定不能」。
   - 全体WPM・art300・art500は参考併記。M4分解(Δ全長=Σ発話差+Σgap差+両端差)を併記。
2. **境界音量差(N4)**: Bの各chunk境界(前chunk末尾発話1秒 vs 次chunk先頭発話1秒のRMS差dB)を、**Aの同じ段落境界位置**(段落末尾1秒 vs 次段落先頭1秒、ASR整列で位置決定、A・Bとも同じ方法)と比較。「基準到達」= 全境界で |B − A同位置| ≤ 3.0 dB。3.0dB=一般に音量差として気づかれにくい下限の目安として**本Trialで事前固定する評価用の値**(Xの実測≤5.8dB[境界差の絶対値]は外挿しない)。A_r2のA同位置差(take間ノイズ)と、Aのpart/clip境界値は参考併記。判定対象外=内容によるA内の差。
3. **欠落・二重再生**: 各clip・各armで ASR語数/台本語数 ∈ [0.97, 1.03]、全段落が整列(`all_paragraphs_aligned`)、match_ratio ≥ A − 0.02。
4. **Gate/条件**: 全chunkの`status=OK`、`condition_diff`(local_rewrite/text_changed/minimal_fallback/pronunciation_hint)空、Style sha・model・Voice一致。
5. **声質・緊張感・クライマックスの連続性**: 機械判定しない(ユーザー試聴)。R4のF0/重心は参考値・判定なし。
6. 上記を満たしても**音質改善とは断定しない**。ユーザー試聴で採否判断(Production採用はユーザーのみ)。基準未達は『REJECTED候補』ではなくFableが再計画を判断。
7. R2: 本Trialの結果を閾値100語の正当化に使わない。閾値100の根拠は既存`target_words=100`との同値性とユーザー指示「長く続く区間のみ」のみ。

## 13. STOP条件(即停止・事実報告、自動続行なし)
Ledger事前計算が空でない / TTS・組立経路moduleに未commit変更が30分解消しない / audit hookが許可dir外書込みを検知 / 保護store sha変化 / 上限30円超過見込み(予約方式) / 他Z TTSが稼働中で直列化できない(待機は可) / Production file差分が生じた / chunkのstatus≠OK(自動再実行しない)。
