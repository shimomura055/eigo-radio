# ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_03 (2026-10-11、Sonnet実行層、Opus必須指摘M1〜M7反映)

Status: USER_DECISION_REQUIRED(提案のみ。目標フローは未採用・Trial級設計案・APPROVED_FOR_PRODUCTIONではない)。有料API 0円。Production/Prompt/Validator/Routing/CURRENT_SPEC/Coffee worktree/user_test無変更。
使用モデル: 実行層 Sonnet 5.5(API呼出なし)。

## 事実照合結果(read-only)
- (i) N3 L532: `_generate_a2_japanese_minimal_instruction(text, out_path, tts_backend=tts_backend)`にstyle引数なし=確定。JA_SPEC_SURVEY L78/L96と一致(M1の根拠、日本語もJ3を失う)。
- (ii) CS L1692「4回目以降は絶対にTTS生成しない」(減速の例外記載なし)。`er003_v1_n3_01_tts_generate.py` L248-262外側ループ(既定3周)。Coffee part2: attempt_history 15:13=1回、15:35=3回(累計4)+LR再TTS1=TTS 5回=違反確定。
- (iii) `er006_secondary_asr_01.py` L704-705/774-775 Phrase List付きAzure、L783-788 `should_pass`でPASS(entity追加確認なし)=確定。日本語SCG(Phrase Listなし+C1)との非対称。
- (iv) 「C1は旧承認と逆」: CS:1998は「entity-likeのみ」対象、旧Cascadeは`ASR_VALIDATION_UNCERTAIN`のみ起動、g8は非cascade差(熟->じく)を含むTCMで旧方針でも再生成、2026-09-09実運用も旧承認どおり。**Opus見解(言い過ぎ)を採用しv01を訂正**。真の矛盾は同じ濁点差がUNCERTAIN経路(救済)とC1(除外)で分かれる点。報告書v02は両論併記+判定根拠を0-2(iv)に記載。

## v02の変更点(RECONCILIATION_REPORT_02.md、v01は残置)
要点への追加(8〜11)、0章新設(M1〜M7反映表・事実照合)、3-補(C1訂正)、4-7、5-3(Opus統一ルール10項目の照合: 一致/相違/新規)、5-4(設計案修正)、7-1訂正(M1)、8-2追加、8-3全面再編(必要=最小対Trial約15〜20円/0円=試聴リスト[needs_listen 5+Coffee showed/raw bean URL]/縮小=T-1約40円/不要)、9章最終版(U-0〜U-19、選択肢・推奨・理由・QCD影響)、11-2(Dangling統合D1〜D12)、12章注記、13章更新、14章新設(L1692違反・Azure費用欠陥)。

## SSOT追記(CRLF維持、追記のみ)
- DECISION_LOG.md L20556(1エントリ、Status=USER_DECISION_REQUIRED、費用0円)
- OPEN_ITEMS.md OPEN-270(L1692違反)/271(Azure費用集計欠落・11ファイル・Budget Guard盲点)/272(固有名詞ヒューリスティック)/273(一時API障害)/274(LR再TTS依存・span選択)/275(Coffee費用補正)=L773-778。OPEN-263に辞書補強候補、OPEN-257/258に参照追記。各「ユーザー判断待ち・未実装」明記。
- docs/pm/REPORT_LEDGER.md L254

## 成果物
er056_output/asr_tts_cross_language_reconciliation_01/RECONCILIATION_REPORT_02.md、本ファイル、docs/pm/ACTIVE_TASK_ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01.md(更新)
