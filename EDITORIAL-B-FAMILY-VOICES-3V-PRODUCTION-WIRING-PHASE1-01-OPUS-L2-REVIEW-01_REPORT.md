## 要点(5行)

1. 2V(2声)Production挙動の不変性は**コード構造上は概ね担保**されている(`voice_c`既定None・新規関数分離・共有Gate辞書追加は既存episodeを素通り)。ただし**唯一の実質的な例外がComment 2/3のPrompt本文書換**で、これは2V B1だけでなく**B-Family A2(既にPRODUCTION_WIRED・ユーザー試聴承認済み)にも同時に効く**(Sonnet報告は2Vのみ言及)。
2. **新規のfail-open候補を1件検出(HIGH)**: `VOICE_FALLBACK["voice_a"]="Schedar"`と`VOICE_ASSIGNMENT["voice_c"]="Schedar"`が同一のため、Algieba不可時に**Voice 1とVoice 3が同じ声になる**。警告もGateも無く、新規テストがこの衝突を「期待挙動」として固定している。
3. Voice 3使用不可時に既存Human Review Lockへ倒す設計は**実コード上そのとおり**で、無音・欠落でAssemblyへ進むfail-openは見つからなかった(Gate → `GATE_BLOCKED`で停止)。
4. Phase 2のruntime確認の価値を最も損なうのは、(a) Voice衝突/distinctnessの無記録、(b) 6区切りparserのcontent integrity checkがTrialから未移設、(c) 3V経路が**Ledgerを一切読まない**(deviation checkだけでなくLedger接続自体が無く、2Vより監視が薄い)の3点。
5. Comment 3/4には「どちらが正しいか」(二者択一の言い回し)が3箇所残っており、「count固有表現のみ除去」という報告記述は**部分的にしか達成されていない**。PRODUCTION_WIRED可否・Phase 2着手可否は本レビューでは判断しない(ユーザー判断事項)。

---

## 論点1: 2V既存Production挙動の不変性

**所見(不変性が担保されている部分)**
- `build_required_structure()`は`voice_c=None`のとき従来の`cfg["b1"]`/`cfg["a2"]`+2引数resolverをそのまま通り、出力は従来と同一。`editorial_type`の後ろに`voice_c`を足しているため、既存の位置引数呼び出し(`er011_open129_structural_completeness_production_wiring_evidence_01.py` L84/86ほか)も無影響。
- 共有Assembly辞書への`point_three_heading`追加は**fail-openにもfalse rejectにもならない**。Gateは「記録されたsegmentを回す」実装(`C:\Users\tensh\eigo-radio\er003_v1_n3_01_assemble.py` L394-402、判定は`_segment_missing_mandatory_disfluency_qa()` L191-195)なので、`point_three_heading`を持たない2V/A-Family episodeは対象外のまま。逆に「mandatoryに足したのに必須化されない」種類のfail-openも起きない(3Vは必ずこのsegmentを記録するため)。
- runner側の2V関数群(`run_scaffold`/`run_tts`/`finalize_tts_results`/`run_assembly`)は3V関数と完全に別実体で、共有しているのはmodule定数`EDITORIAL_TYPE`(=registry辞書)のみ。

**所見(不変ではない箇所 — 報告の記載より影響が広い)**
- `VOICES_COMMENT_2_ROLE`/`VOICES_COMMENT_3_ROLE`(`er012_b_family_editorial_type_registry_01.py` L118-151)は`COMMENT_ROLES`経由で、2V B1 runner(`er012_b_family_production_runner_01.py` L253)**と** B-Family A2 Production module(`er012_b_family_voices_a2_production_01.py` L485-499)の両方が読む。A2はComment出力が日本語のため、「2つの声を聞き終えたリスナー」→「複数の声を〜」の書換は**日本語出力の文面に直接効く**。A2は2026-09-09に`PRODUCTION_WIRED`+試聴承認済みの経路。
- テストは`assertNotIn`(旧文言が消えたこと)中心で、**新文言の意味・出力への影響を固定するテストは無い**(そもそもLLM生成物なので不可能)。つまり「2V挙動不変」はPrompt本文については成立していない。

**新規fail-open候補(HIGH)**
- `resolve_voice_names_3v()`(`er012_b_family_voices_production_01.py` L332-349)はVoice A/Bを既存`resolve_voice_names()`に委ね、`voice_c`は常に`Schedar`固定。registry L61-64で`VOICE_FALLBACK["voice_a"] = "Schedar"`。したがって**Algieba技術不可 → voice_a=Schedar、voice_c=Schedar**で、3声のうち2声が同一になる。
- これを検知する仕組みが1つも無い(Gateのrequired_structureも「渡された名前」で照合するため一致してしまう。distinctnessログも無し)。
- さらに新規テスト`test_voice_a_unavailable_still_uses_existing_fallback_logic`(`er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py` L265-271)が`voice_a=="Schedar"`かつ`voice_c=="Schedar"`を**期待値として固定**しており、衝突が仕様として凍結されている。

**その他(軽微)**
- `build_required_structure("a2", ..., voice_c="Schedar")`は`voice_c`を**黙って無視**して2V A2構造を返す(L506-522)。3VはB1のみなので実害は低いが、Phase 2のevidence取得スクリプトが誤って渡した場合に「別構造で検証してPASS」になる。
- runnerのCLI level名は`"b1_3v"`、registryのlevel名は`"b1"`+`voice_c`。`build_required_structure("b1_3v", ...)`は`ValueError`(fail-closedではあるが命名が非対称で、Phase 2でevidence取得スクリプトを書く人が踏みやすい)。

**重大度**: 声衝突=**HIGH**、Comment Prompt波及=**MED-HIGH**、`a2`+`voice_c`黙殺/level名非対称=**LOW-MED**、共有辞書追加=**LOW(問題なし)**。

**Fableへの提案**
- 声衝突ガードは**Phase 1修正**を推奨(数行): `resolve_voice_names_3v()`で`len({voice_a, voice_b, voice_c}) < 3`のとき`RuntimeError`でSTOP(またはreasons記録+runner側で明示STOP)し、テストの期待値も「衝突時はSTOP」へ変更する。Voice 3にfallbackを与えない2026-09-10ユーザー決定と矛盾しない(代替声を発明せず止めるだけ)。
- `a2`+`voice_c`は`ValueError`化、または`level="b1_3v"`を別名として受理する — **Phase 1修正(軽微)かPhase 2着手前**のいずれか。
- Comment Prompt波及は論点2へ。

---

## 論点2: Comment 2/3の汎用文言化の意味保存

**所見**
- 役割の骨格(Comment 2=Hookの問いから複数Voiceへの橋渡し、Comment 3=「正しさの判定」ではなく「なぜ違って感じるか」への視点移動)は**保存されている**(registry L118-151、避けるべき事項リスト・文数指定・構造ラベル禁止も維持)。
- ただし**汎用化は不完全**。二者択一を含意する「どちらが正しいか」が3箇所残存する:
  - Comment 3 タイトル行(L139)
  - Comment 3 役割行「『どちらが正しいか』という判定ではなく」(L142)
  - **Comment 4(今回未変更)L158「『どちらが正しいか』という表面的な対立から」** ← 3Vにも適用される
  報告4節は「タイトル行のみ意図的に残した」と書いているが、実際は役割行とComment 4にも残っている。3声に対する指示としては不整合(致命的ではないが、LLMが"which of the two"型の英文を出す誘因になる)。
- **承認済み3V音声との差分**: ユーザーが試聴してVALIDATEDとした3V episodeのComment 2/3は、Trial側の**手動固定英文**(`er012_editorial_b_voices_3v_audio_trial_01.py` L371-379、"Now, you will hear three different voices..."/"You have heard three different ways...")であり、LLM生成ではない。Phase 2ではここが初めてLLM生成に置き換わるため、**Phase 2の音声はユーザーが承認した音声と同一ではない**。Gate 3項目(m)「approved specとProduction挙動の一致」に直接関わる。
- 新Comment 2の役割文からは声の個数情報が完全に消え、個数はcontext(`run_scaffold_3v()`が渡すVoice 1/2/3見出し3行、runner L719-725)からのみ推測される。2V側contextは「One Voice heading/Another Voice heading」のままで整合。
- **SSOTとの乖離**: 承認済み正本は`EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FINALIZE-11_REPORT.md` §4(L118-149に旧文言全文)で、`CURRENT_SPEC.md` L604が「役割定義はFINALIZE-11 Comment Contractを共有」と参照している。現在コードはこの正本と**文言レベルで不一致**(未SSOT反映)。

**重大度**: MED(意味は保存、ただし(i)不完全な汎用化、(ii)承認済み音声との差分、(iii)SSOT乖離の3点は明示処理が必要)。

**Fableへの提案**
- 「どちらが正しいか」→「どの声が正しいか」または「正しさの判定」への統一(Comment 3の2箇所+Comment 4の1箇所)は、やるなら**Phase 1修正**が安い。ただしComment 4は今回スコープ外だったため、**ユーザーに「3箇所とも直すか/現状のまま3V音声を1本聴いて判断するか」を提示**するのが筋。
- Phase 2実行時は、Comment 2/3/4の**実出力英文全文をRESULT/Reportに転記**し、(a) 3声に対する言い回しの不整合が出ていないか、(b) 2V/A2でも同じ文言変更が効くことをユーザーが受け入れるか、を**Phase 3 SSOT反映(FINALIZE-11文言の改訂記録)とセットで**確認する。
- SSOT反映は**Phase 3必須**(`CURRENT_SPEC.md` L604の参照先文言が変わったことを明記しないと、正本と実装の恒久的乖離になる)。

---

## 論点3: retry / fallback / regeneration整合

**所見(設計どおりで、fail-openは見つからない)**
- Voice 3本文は`generate_voice_body_wide_margin()`(`er012_b_family_voices_production_01.py` L387-)で生成され、この関数は`@review_lock.guarded_generate("en")`付き。出力先`er012_output/editorial_b_family_voices_3v_production_wiring_01/b1b/narration/point_three.wav`は`_has_valid_narration_layout()`(`er011_human_review_lock_01.py` L119-136)の`.../<theme>/<level>/narration/<seg>.wav`規約を満たすため、**lock機構は2Vと同一に効く**(segment_id=`point_three`)。
- 失敗時のstatus(`STOPPED`/`HUMAN_REVIEW_LOCKED`)は`finalize_tts_results_3v()`(runner L755-768)がそのまま`tts_generation_results.json`へ記録 → `load_b1_sources_3v()`が**wav読み込み前に**`asm.verify_episode_audio_validation_gate(out_dir, "B1")`を呼ぶ(production_01 L601) → `AUDIO_GATE_ALLOWED_STATUSES=("VALIDATED","HUMAN_APPROVED")`(assemble L88)から外れて`RuntimeError` → `run_assembly_3v()`が捕捉して`status="GATE_BLOCKED"`(runner L780-786) → player.htmlも生成されない(L1019-1025)。**無音・欠落でAssemblyへ進む経路は無い**。
- `approve_regenerate()`はout_pathキー方式(`er011_human_review_lock_01.py` L357-384)なので、`point_three`系も2Vと**同一機構**。同一引数での再呼び出しで1回だけ再生成される点も同じ。

**注意点(defectではないが Phase 2で効いてくる)**
- voice_check段階でSchedarがNGでも**runは止まらず**、Comment/見出しTTSを消費してから本文TTSでlockに当たる(¥が先に出る)。仕様どおりだが、Phase 2のSTOP条件として明記しておくべき。
- Gateは`tts_generation_results.json`が存在しないと**早期return**(assemble L386-387)。`assemble`だけを単独stageで回すとGate素通りになり得る(2Vと同じ既存性質)。Phase 2は必ず`all`または`tts`→`assemble`の順で実行し、証跡ファイルの存在を確認すること。
- `load_b1_sources_3v()`のwav欠落は`FileNotFoundError`で、`run_assembly_3v()`は`RuntimeError`しか捕捉しない → GATE_BLOCKED summaryではなくtracebackで落ちる(2Vと同じ、fail-closedではある)。
- **2V配線時の前例が3Vでは3倍に**: 2V配線では`point_two`がrepetition QAで`STOPPED`→`GATE_BLOCKED`となり、attempt試聴artifact作成・`record_human_approval()`・wav差し替えという**runnerに存在しない手作業**で解消した(`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01_REPORT.md` §9-10)。3Vでは本文が3本になるため発生確率は上がるが、この復旧経路は3V runnerにも入っていない。

**重大度**: 主要設計=**LOW(問題なし)**。Phase 2運用リスク(STOP時の手作業・部分stage実行)=**MED**。

**Fableへの提案**
- Phase 1修正は不要。Phase 2の実行計画に「(1)`all`で通す、(2)`GATE_BLOCKED`時はoverrideせずSTOPして報告、(3)attempt試聴→`record_human_approval()`が必要になった場合は再度ユーザー承認を取る」を**事前に明記**しておくことを推奨。

---

## 論点4: Phase 2のruntime確認を無意味にしうる欠陥候補(優先順)

| # | 項目 | 影響 | 重大度 | 提案 |
|---|---|---|---|---|
| 1 | **Voice distinctness/衝突の無検知・無記録**(論点1) | fallbackが1回でも走ると「3声で構成された」という主張自体が成立しないのに、evidenceからは判別できない | HIGH | **Phase 1修正**(衝突guard)+Phase 2で解決3声名を必ず記録 |
| 2 | **content integrity check未移設**(Trial側`run_content_integrity_check()`、`er012_editorial_b_voices_3v_audio_trial_01.py` L879-903) | 新規の6区切りparserが本文を正しく割り当てた証跡がProductionに無い。見出し数6でも順序違いなら**Voice本文の入れ違いが黙って通る**(`build_parts_3v()`は数だけ検証) | HIGH | ¥0・小規模。**Phase 1修正 or Phase 2 evidence取得の一部**として移設を推奨(`build_parts_3v()`が`"sections"`を返している以上、消費側が無いのは片手落ち) |
| 3 | **3V経路がLedgerを一切読まない**(`run_scaffold_3v()`は引数に`ledger_text`が無い。2Vは`run_scaffold()` L293で`vfl01.run_deviation_check`実行) | Ledger Deviation Checkが無いだけでなく、OPEN-131 Fact Attribution(`build_voice_attribution_block(ledger_text)`)の入口も3Vには存在しない。**3V Productionは2Vより監視が薄い**状態で配線される | MED-HIGH | Phase 2着手前に「2V相当のmonitoringを付けるか、付けない理由をSSOTに明記するか」をユーザー判断へ。実装するならPhase 1b/2 |
| 4 | **OPEN-129 opt-in構造Gateが3V経路から一度も呼ばれない**+既存evidence script(`er011_open129_structural_completeness_production_wiring_evidence_01.py` L84-86)に3V分岐が無い | 「16 segment・voice割当が承認構造どおり」というruntime証明手段が現状ゼロ | MED | Phase 2のevidence取得で`build_required_structure("b1", va, vb, voice_c=vc)`を1回通してPASSを記録(mandatory化はdeferredのままでよい) |
| 5 | **Key Phrase 10 segmentが検証記録なしで`status:"OK"`**(`finalize_tts_results_3v()` L760-763、sha256もdisfluency_checkedも無し。Gateは`kp*_en`をmandatory対象外として素通り) | Phase 2のevidenceに「全segment OK」と出るが、うち10件は**今回のrunで検証していない再利用物** | MED(2Vと同一の既存性質) | evidence記載時に「再利用・検証はTrial-01時点」と明示分離。修正は不要 |
| 6 | Trial側`build_required_structure_3v()`(trial L261)が**そのまま残存**。報告の「2重定義解消」は文字通りには成立していない | 将来のdrift源 | LOW-MED | Phase 3でTrial script冒頭にdeprecation注記、またはSSOTに正本所在を明記 |
| 7 | Tension尺/Analytical Leakage/distinctnessの観測ログ皆無 | Phase 2は**Trial-01と同一記事**なので既測値があり、Phase 2自体は無意味化しない。Phase 1b(新テーマ)以降で必須になる | LOW(Phase 2)/HIGH(Phase 1b) | Phase 1b設計時に、OPEN-131と同じ「別evidence scriptで観測」パターンで計画 |

---

## 論点5: PRODUCTION_WIRED判定の前提(Phase 2で必ず記録すべきruntime evidence)

Gate 3(d)(f)(g)(m)を満たすために、最低限これらを実測値として残すことを推奨する(判定自体はユーザー)。

1. **実行同一性**: 実行コマンド(`python er012_b_family_production_runner_01.py all b1_3v`)・commit hash・実行日時・入力記事のsha256。
2. **model_id/routing**: Support LLM の実解決値(`routing.require_model("B1_SUPPORT")`の戻り値)と TTS model(`p9a.ENGLISH_MODEL_NAME`)を**ログ実測**で(定数の転記ではなく)。
3. **Voice**: `audit/voice_resolution.json`の`voice_a`/`voice_b`/`voice_c`3値+`reasons`が空であること+**3値が相互に異なること**(論点1の衝突が起きていない証明)。
4. **segment構造**: `audit/tts_generation_results.json`の16 segment名一覧(`point_three`/`point_three_heading`含む)、各`status`・`sha256`・`voice`。
5. **必須post-process**: B1 mandatory 9件(`preview`/`comment_1-4`/`in_one_line`/`point_one_heading`/`point_two_heading`/**`point_three_heading`**)の`disfluency_checked: true`。
6. **OPEN-121/122**: Voice 1/2/3本文とHook part1/2で`enable_connected_speech_equivalence_layer`/`enable_repetition_qa`が実際に有効化された記録(attempts JSON)。
7. **Human Review Lock非発火**: `b1b/audit/review_lock_state.json`に`HUMAN_REVIEW_REQUIRED`0件、`attempt_history.jsonl`の当該run_id分。発火した場合はoverrideせずSTOPし、その事実自体をevidenceとする。
8. **Gate発火**: `run_summary_assemble.json`が`status:"OK"`(=`GATE_BLOCKED`でない)。加えて論点4-#4のopt-in構造Gate 1回PASS。
9. **音声実測**: 総尺(Trial実測356.6秒との比較)・peak・clipping・headroom report。
10. **Key Phrase**: `audit/key_phrase_reuse.json`の`hash_match: true`と再利用元パス、および「10 segmentは今回未生成」の明示。
11. **費用**: `audit/raw_usage_log.jsonl`実測¥と内訳、cap 150円との関係。
12. **Comment実出力**: Comment 1-4・Previewの生成テキスト全文(論点2のユーザー確認材料)+**Trial承認音声のComment 2/3は手動固定文だった差分の明記**(Gate 3(m))。
13. **SSOT側の前提**: `CURRENT_SPEC.md` L612は現在「`APPROVED_FOR_PRODUCTION`(未配線)・配線に必要な5項目未実装」と書かれたままなので、Phase 3でここ・`OPEN-120`・`DECISION_LOG.md`の3点更新が完了して初めて`PRODUCTION_WIRED`の形式要件が揃う。

---

## Sonnet/Fableが見落としている可能性のある点

1. **Voice衝突(Algieba fallback = Schedar = Voice 3)** — 新規テストが衝突を期待値として固定してしまっており、レビューを通ると「検証済みの正しい挙動」に見える。今回の最大の指摘。
2. **Comment 2/3書換の影響先はB-Family A2にも及ぶ**(`er012_b_family_voices_a2_production_01.py` L485-499)。報告は2Vのみ言及。A2は日本語出力なので文面変化がより直接的。
3. **「どちらが正しいか」は3箇所残存**(Comment 3タイトル+役割行、Comment 4)。報告は「タイトル行のみ残した」と記載しており、実態と食い違う。
4. **content integrity check(6区切りparserの正当性証跡)がTrialにあってProductionに無い** — 見出し数だけ合っていれば通るため、Voice本文の入れ違いを検知しない。
5. **3V経路はLedgerを読み込む口が無い** — Deviation Check未実装として報告済みだが、より根本的に「3V ProductionにはLedgerが接続されていない」状態(OPEN-131 Fact Attributionの3V適用余地も現状ゼロ)。2Vとの安全機構の非対称。
6. **報告の「2重定義解消」は未達**(Trial側`build_required_structure_3v()`は残存)。
7. **CLI level名`"b1_3v"`とregistry level名`"b1"+voice_c`の非対称** — Phase 2でevidence取得スクリプトを書く際の踏み台になりやすい。`build_required_structure("a2", ..., voice_c=...)`の黙殺も同種。
8. **Phase 2の音声は「ユーザーがVALIDATEDと判断した3V音声」とは別物**(Comment 2/3がLLM生成に変わる)。Gate 3(m)の判断材料として、Phase 2 artifactは「再試聴が必要な新規成果物」として扱うべきで、Trial VALIDATEDを流用しない。
9. **2V配線時の`point_two` GATE_BLOCKED前例と同型の事象が3本の本文で起こり得る**が、復旧手順(attempt試聴artifact/`record_human_approval()`)はrunnerに無く、都度ad-hocスクリプトが必要になる。Phase 2の所要時間・費用見積りに織り込むべき。

以上は診断であり、Phase 1修正を行うか・Phase 1b/2へ持ち越すか・PRODUCTION_WIREDを宣言するかの決定は行っていない。
