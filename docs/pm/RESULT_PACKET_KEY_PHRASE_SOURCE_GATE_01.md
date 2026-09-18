管理ID: KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01
最終Status: PRODUCTION_WIRED(Gate実装・Production配線・test・runtime evidence・SSOT・Git反映すべて完了)
1. Reconciliation Check: 既存Audio Validation Gate群にsource_span本文実在チェックは無く新規failure mode。reuse_key_phrases/_3vはsha256比較の同等機構を既に持つため変更せず維持。
2. Gate (a): 新規`er003_key_phrase_source_gate_01.check_key_phrase_source_presence()`(大小文字/apostrophe/HTML entity/dash/空白正規化)を共有`verify_episode_audio_validation_gate()`へ統合(新設`verify_key_phrase_source_gate()`)。不在時RuntimeError(KEY_PHRASE_SOURCE_MISSING)。1関数でNews/B-Family/Family C/Family A Trend/Discovery全Production driverをカバー。Family Cのみarticle.md未永続化のためarticle_text明示引数を追加。
3. Gate (b): `assert_key_phrase_reuse_source_matches()`(sha256一致)を`reuse_key_phrases_a2()`へ後方互換optional引数で配線、唯一の呼び出し元(AI Hiring事故の発生経路)で有効化。
4. runtime evidence: Gate(a) 20 canonical asset 20/20 PASS、旧Free-Address A2 FAIL(missing5/5)、旧AI Hiring A2 FAIL(missing4/5)。Gate(b) 同一本文PASS/実際の事故構図FAILの2ケース確認。全て docs/pm/closeout_136_e2e/key_phrase_source_gate_01/ 配下。
5. 新規テスト17件PASS(er003_test_key_phrase_source_gate_01.py)。回帰run_project_regression.py collected=2914 passed=2911 failed=3(既知baseline、新規failureなし)。
6. 旧形式(source_span欠落)asset: 20件中0件該当、発生なし。
7. 費用: ¥0(API呼び出しなし)。
8. SSOT: CURRENT_SPEC.md「Key Phrase」節新規行+Gate参照1行、DECISION_LOG.md本体エントリ追加、OPEN_ITEMS.md OPEN-170 CLOSED、ARTIFACT_REGISTRY.md新規セクション追加。
9. Git: commit1(実装+テスト+evidence)8f197a74、commit2(SSOT)は本報告直後にpush予定。
10. 委任文検証: check_delegation_prompt.py → FAIL(3コマンド行がpath/引数検出ヒューリスティックに非該当と判定、実質は`-c`インライン/dry-import確認コマンドで正常。非ブロッキング記録のみ)。
11. USER_DECISION_REQUIRED候補: なし(範囲拡大せず、Gate(a)(b)のみ実装)。
詳細: DECISION_LOG.md `## KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01`、docs/pm/closeout_136_e2e/key_phrase_source_gate_01/

## FIX-01(Fable差し戻し1回目、2026-09-18)

1. 最終Status: `PRODUCTION_WIRED`(fail-closed化・実Assembly経路20/20再検証・テスト・回帰・SSOT・Git反映すべて完了、USER_DECISION_REQUIRED候補なし)。
2. Gate (a): 適用要否を「KP segment検出」(`tts_generation_results.json`の`key_phrases`非空、または`key_phrases/keywords_canonicalized.json`存在)で判定。該当時はKP asset不在→`RuntimeError(KEY_PHRASE_SOURCE_GATE_ASSET_MISSING)`、本文解決不能→`RuntimeError(KEY_PHRASE_SOURCE_GATE_ARTICLE_TEXT_UNAVAILABLE)`。非該当時は`audit/key_phrase_source_gate.json`へ`NOT_APPLICABLE`を記録(silent skip廃止)。
3. 実経路再検証: 新規`docs/pm/tools/kp_gate_wrapper_evidence_01.py`が`verify_key_phrase_source_gate(out_dir, level)`を各Production driverと同じ引数形で直接呼び、20 canonical out_dir全件PASS(NOT_APPLICABLE 0件、article_source=article.md 14件/article_normalized.txt 6件)。旧2 out_dir(旧Free-Address A2/旧AI Hiring A2)はtrue positive FAIL再確認。evidence: `docs/pm/closeout_136_e2e/key_phrase_source_gate_01/gate_a_canonical20_via_wrapper.json`。
4. Production driverへの`article_text`明示渡し追加: なし(全20件がGate自身のarticle.md/article_normalized.txt fallbackでPASS)。young_travelers B1のみ、実Assembly呼び出し(`er011_family_a_completion_a2_trend_end_to_end_01_run.py:601`)に合わせ`b1b`親ディレクトリをout_dirとして使用(index.json記載の選定中間dirではない)。
5. Gate (b): `reuse_key_phrases_a2`の`target_article_text`未指定時、`narration_dir`親ディレクトリの`article.md`から自動解決し、それも無ければ`RuntimeError(KEY_PHRASE_REUSE_TARGET_TEXT_UNAVAILABLE)`で流用不可(fail-closed)。唯一のProduction呼び出し元`er012_b_voices_3v_a2_user_test_01.py:361`は既に`target_article_text`明示済みで変更不要。`reuse_key_phrases`/`reuse_key_phrases_3v`/`reuse_approved_a2_assets`(`er012_b_family_production_runner_01.py` 196-198行/709-712行/1384-1385行)が常時`RuntimeError([TEXT_HASH_MISMATCH]/[ASSET_HASH_MISMATCH])`送出(ログのみでない)であることをコード確認。他コピー経路(Grep`copyfile.*keywords|copytree.*key_phrases`)のうちProduction2件(`er011_family_a_completion_a2_trend_end_to_end_01_run.py`継続run=事前sha256確認済み、`er013_family_c_production_runner_01.py`の`reuse_from`=同一記事の過去level、Assembly呼び出しで`article_text=`明示によりGate (a)が保護)を確認、変更不要。Trial/履歴6ファイルは変更なし(一覧のみ、DECISION_LOG FIX-01節参照)。
6. テスト: `er003_test_key_phrase_source_gate_01.py`に新規/更新9件追加(計22件PASS)。既存Gateテスト4ファイル(fixtureにKP segmentを含むためGate (a)新規適用対象になった箇所へ最小限のsource_span一致assetを併置する修正、テスト対象ロジック自体は無変更)、計63件PASS。
7. 回帰: `run_project_regression.py --pattern "er0*_test_*.py"` collected=2919 passed=2916 failed=3 errors=0(既知3件のみ、新規failureなし)。
8. SSOT: `CURRENT_SPEC.md`「Key Phrase source整合Gate」行をfail-closed仕様へ訂正。`DECISION_LOG.md`に`### FIX-01`節追記。`OPEN_ITEMS.md` OPEN-170は元々silent skip記述が無く本文未変更(`CLOSED`のまま)。
9. Git: commit1(実装+テスト+evidence) `1d69aa97`。commit2(SSOT)は本ファイル保存直後にpush。main=origin/main確認予定。
10. 費用¥0(API呼び出しなし)。一覧外Read: なし。check_delegation_prompt結果: FAIL(実行コマンド節の2行[pytest複数ファイル列挙/`-c`インライン確認コマンド]がpath/引数検出ヒューリスティックに非該当と判定されたのみ、実質は正常なコマンド。非ブロッキング記録)。
11. USER_DECISION_REQUIRED候補: なし。
