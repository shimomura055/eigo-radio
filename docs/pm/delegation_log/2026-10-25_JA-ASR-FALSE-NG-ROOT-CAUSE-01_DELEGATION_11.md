# 委任_11｜JA-ASR-FALSE-NG-ROOT-CAUSE-01 残課題「しわ↔すわ」(OPEN-333経路の誤PASS)の原因究明・是正設計・API 0評価(Production変更なし)

## 背景(Fableから)
- ユーザー指示(逐語 `docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_USER_02.md` §6・§8)の③受入条件に「『しわ』と『すわ』を区別できる」がある。07A(OPEN-517 F1+F2、commit `5e50613f5`)後も N3-07 しわ↔すわ はPASSのまま。07A報告では「音韻候補総当たり(OPEN-333)経由のため本是正の範囲外(Candidate E)」とされた。
- 同指示§2は③について「原因究明、対策設計、Trialを承認する/既存の承認済み安全条件が正しく機能するよう修正する」と承認済み。ただし**承認済みの救済仕様そのものを変える場合はユーザー承認**が必要。したがって本委任は、(a) しわ↔すわ PASSが「実装不具合(承認済み条件の機能不全)」なのか「承認済み救済仕様(OPEN-333)の設計どおりの結果」なのかを証拠で切り分け、(b) 是正案をAPI 0で評価し、(c) 採用判断に必要な材料を揃えるところまで。**Productionファイル(`er078_*`/`er007_*`/`er020_*`等)は編集しない**。
- 参照: `OPEN_ITEMS.md` の OPEN-333 行(Grepで該当行のみ)、CURRENT_SPEC の音韻類似/同音異字救済の節(Grep: 「音韻」「OPEN-333」「PHONETIC」)、DECISION_LOG の OPEN-333 採用エントリ(Grep)、`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/` の `OPEN517_DESIGN_02.md`・`OPEN517_EVAL_02.md`・`OPEN517_PUBLIC_AUDIT_01.md`・`proto_value_gate_fix_04.py`・`eval_open517_api0_04.py`・`open517_prod_parity_01.py`(凍結データの読み方)、`er078_asr_unified_judge_01.py`/`er078_asr_value_guard_01.py`(読取専用)。
- 並行agent: (A) KP HR evidence(X/Z runner)、(B) Y 委任_07(er020・er121・Y docs所有)。本委任は `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/` 配下の新規ファイルと `OPEN_ITEMS.md` の OPEN-333 行の最小追記のみ編集可。

## やること(すべてAPI 0・実費0円)
1. **経路の特定**: N3-07(しわ↔すわ)がPASSになる判定経路を、Production関数の実行trace(reason_code・label・equivalence_basis・候補生成の中身)で示す。OPEN-333の音韻候補総当たりが「し↔す」(子音同・母音違い)を同一視する規則は、承認時の設計意図(DECISION_LOG/CURRENT_SPECの記述)に含まれているか、それとも実装上の広がり(例: 候補生成の距離閾値・母音無視・五十音行内置換)かを、原文を引用して判定する。
2. **影響範囲の棚卸し**: 同じ規則で救済されている事例を凍結データ(N3 30 clip・正常143・実履歴43・P-4 562・未知493・合成負例91・保存転写1,098)で全件列挙し、「正しく救済(正常音声)」「誤PASS(真の読み違い)」「判定不能」に分類。母音違い(し↔す等)・濁音違い・長音違いなど規則の種別ごとに件数。
3. **是正案の設計とAPI 0評価**: 案は最小2つ(例: E1=母音違いを候補から除外、E2=固有名詞/重要語(既存のalarm語彙やvalue語)に限り音韻救済を不適用、など。既存仕様の用語を使う)。事前登録基準(`OPEN333_PREREGISTERED_01.md`: 誤PASS遮断率・正常NG化0・既存負例回帰0・月題等への副作用)を書いてから評価し、`proto_open333_fix_01.py`(Production関数をimportして差分だけ上書きする方式、07Aのproto v4と同形)と `eval_open333_api0_01.py` で結果を `OPEN333_EVAL_01.md`(+json)に出す。決定性(2回実行で同一sha)を確認。
4. **区分判定と材料**: `OPEN333_DESIGN_01.md` に、(i) 実装不具合か仕様どおりかの結論と根拠引用、(ii) 各案のQCD(遮断/副作用/再生成増の見込み/実装規模)、(iii) 不具合なら「承認済み条件の是正」として自律適用可能な範囲、仕様変更なら**ユーザー承認が必要な点を1〜3行に要約**(推奨案と理由付き)、(iv) Opus必須レビュー(11-3 条件C: 重要変更のProduction採用提案前)向けの依頼文 `OPUS_REVIEW_REQUEST_01_OPEN333.md`(論点を絞る)。Fableが次工程(Opus/ユーザー)を判断する。
5. OPEN-333 行へ最小追記(本委任の成果物名・結論の1文)。新規OPEN採番はしない。
6. Git: 対象pathのみ `git commit --only` → `git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP)。禁止=`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。secret grep 0件。OPEN_ITEMSは直前再Read・最小Edit・バックアップ。
7. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_DELEGATION_11.md`(直近既知index=600(委任_10)。601以降を試し、先頭行が「# 委任_11｜JA-ASR-FALSE-NG-ROOT-CAUSE-01」のものだけ採用)。

## 報告(`docs/pm/RESULT_PACKET_JAASR11.md`+最終報告)
1. 経路と区分判定(不具合/仕様どおり)+根拠引用
2. 影響範囲の件数表(規則種別×分類)
3. 各案の評価結果(事前登録基準との対応)と推奨案
4. ユーザー承認が必要な点(あれば1〜3行)/自律是正できる範囲
5. 成果物path・commit sha・raw URL
6. RESULT_PACKET 4行+判定整合行
事実と推測を分ける。Status語はVALIDATED(限定)候補までに留め、採用語は使わない。