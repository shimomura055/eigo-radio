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
