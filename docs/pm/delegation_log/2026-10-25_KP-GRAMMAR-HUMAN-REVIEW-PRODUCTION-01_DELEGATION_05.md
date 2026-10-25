# 委任_05｜KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 / PART2-GRAMMAR-PRODUCTION-WIRING-01: R3(Z・HRあり)完成段の実走、R2の1回再生成、Fable受入のSSOT反映、原文保存の是正

## 背景(Fableから)
委任_04(commit `170a5cfa3`、報告 `docs/pm/RESULT_PACKET_KPHR4.md`、`docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/EVIDENCE_01.md`)の結果: R1(X・HRあり)完走、R4(Z・HRなし)完走・公開、R2(X・HRなし)はb1b `comment_4` の既存disfluency検査(「…now. Now, …」の誤検知)でHR Lock、R3(Z・HRあり)は委任_04自身の起動間隔ミスでRESTART_STORM→`STOP`自動作成、KP/Part 2確定(文法はhuman_rejected_all→ZERO)まで。

**Fable判定**:
- **X = `PRODUCTION_WIRED`(Fable受入2026-10-25)**: ①Part 2 ②Trial-08選定方式 ③KP Human Review ④文法Human Review の4機能とも、R1で正式runner経由の候補保存→rc=4待機→CLI選定→再開→Part 1/Part 2→TTS→assemble→playerまで一致検証PASS。R2で未レビュー継続(明示宣言のみ自動確定・NG skip・`user_ref`)がPart 1/Part 2生成まで確認。R2のLockは本件と無関係の既存検査。
- **Z = 保留**: ③の人手選定→ページ反映と、①Part 2の非ZERO本文のページ掲載がまだ正式runで未確認(R3未完成、R4は文法候補0件)。本委任でR3を完成させて確認する。
- R3の`STOP`解除(`--clear-stop`)はFable権限で許可する(理由: 委任_04の運用ミスによる自行発動、製品不具合なし)。`--reason` には「Fable権限: 委任_04の起動間隔ミスによるRESTART_STORM自行発動の解除(2026-10-25)」と書く。
- R2の`approve_regenerate`(追加再生成の許可)もFable権限で1回だけ許可する(b1b `comment_4`)。それでもLockなら再承認せず、途中停止のまま記録する。`approved_by="user"` は付けない。
- 費用上限: 本委任の有料は**合計15円**(R3完成段2〜4円+R2再生成〜5円+余裕)。KP HR Cap 300円のうち既支出は委任_02の≤25円+委任_04の45.44円。日次は `py docs/pm/tools/daily_dev_cost_01.py` 表示値+94.28円が実累計、+15円で1,480円を超えるなら有料をせず報告。

## 並行agent(衝突回避)
(A) Y 委任_08(er121系・`er121_output/`・`user_test/family_y_production_redelivery_fee_01/`所有)、(B) JA ASR 委任_11(`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/`・OPEN-333行所有)。これらは触らない。本委任の所有: er119/er120系、er019/er026/er062 runner(編集は不具合是正の最小限のみ)、`er019_output/.../part2_hr_evidence_01__run_r2/`、`er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3/`、`docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/`、`docs/research/PART2-GRAMMAR-PRODUCTION-WIRING-01/`、`user_test/family_z_melos_kphr_evidence_r3/`(新規なら)、OPEN-518/519/484行、CURRENT_SPEC/DECISION_LOG最小追記、`docs/pm/delegation_log/`。

## やること
### 1. R3(Z・HRあり)完成段
- 委任_04の再開手順(RESULT_PACKET_KPHR4「R3の再開手順」①〜④)に従う。①`--clear-stop --reason "<上記>"` → ②`--stage kp --regenerate-stage kp_b1b` → ③`--regenerate-stage kp_expl_b1b` → ④完成段を1起動(`--stages tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify --pages-dir .../run_p2_evidence_r3/pages_evidence`)。
- **文法HRの操作**: 再抽出で候補が1件以上あれば、**human選定(`grammar-select`等)で1件採用**し、Part 2の非ZERO本文がAdvancedページにのみ・Part 1直後に載ることを確認する(human_rejected_allにしない。候補0件なら`NO_CANDIDATE`で進め、その事実を記録)。KPは人手で順位と異なる選定を1件以上含める(R1と同じ検証)。CLI操作はAI代行(`declared_by`/`user_ref`の既存規則どおり。ユーザー原文参照)。
- **起動間隔は150秒以上を `Get-Date` で前後記録して確認**(委任_04は66秒で違反した。同じ誤りを繰り返さない)。同一run 5分3回禁止。各起動前に `py tools/stop_scope_check_01.py --managed-id KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 --run-dir <run> --out <run>/stop_check_05_<n>.json`(rc=3なら起動しない)。有料run=`.venv\Scripts\python.exe`。
- 完走後: `verify_selection_matches_outputs`(KP・grammar)PASS、gate/assemble/pages/page_verify rc=0、`user_test_page_standard_check` PASS、Part 2固定文面/本文がAdvanced節のみ、を確認し、ページを `user_test/family_z_melos_kphr_evidence_r3/` に配置・公開(R4と同形式)。
### 2. R2(X・HRなし)の1回再生成
- `approve_regenerate` を b1b `comment_4` に1回適用し、assemble→player.htmlまで進める。再Lockなら停止し記録。
### 3. Fable受入のSSOT反映
- Zの結果に応じて: R3完走・検証PASSなら **Z = `PRODUCTION_WIRED`(Fable受入2026-10-25)**。未達なら「正式runで途中まで確認・runtime未完」のまま(あなたの判定で変えない)。
- `OPEN_ITEMS.md` OPEN-518(KP HR)/OPEN-519(Part 2): Status行を機能×Family(X/Z/Y)で最小追記(Y=未配線→**委任_06でY runnerへ接続済み・文法HRありの実走は未**、と事実を書く。OPEN-484/520参照)。`INTEGRATED_PENDING_EVIDENCE`→X/Zの到達Statusへ。
- `CURRENT_SPEC.md`: KP HR・文法HR・Part 2・Trial-08選定方式の節に、Family別Status 1〜2行(Prompt sha・既定=待機・明示宣言のみ自動確定・期限付き不在宣言不採用、は既存記述を確認し重複しない)。
- `DECISION_LOG.md`: 1件(機能×Family Status確定、根拠run・commit・証拠ファイル)。**他agentの未commit差分(CRLF全行差分を含む)を巻き込まない一時index+commit-tree方式**。追記前に、HEADの`DECISION_LOG.md`に本日の他agentのエントリ(FAMILY-Y 委任_05/委任_07、JA-ASR 委任_10のStatus確定)が存在することをGrepで確認し、欠けていれば報告(復元はしない)。
### 4. ユーザー原文の逐語保存の是正
- `docs/pm/delegation_log/` の KP HR指示(2026-10-25「Family XYZ共通：Part 2文法解説・Key Phrase／文法Human Review 正式Production Wiring」および追加指示「KP・文法Human Review Production Wiring／予算増額・ASAP実行」)とPart 2指示(`..._PART2-GRAMMAR-PRODUCTION-WIRING-01_USER.md`)の保存ファイルが文字化けしている。JA ASR側で成功した方法(jsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl` から role=user の該当メッセージを scratchpad の小scriptで抽出、`py -I`、孤立サロゲートは置換のみ・件数報告、内容無補正)で再抽出し、化けていない本文が得られたら既存ファイルを**上書き**(先頭にメタ1行: 再抽出日時・置換件数)。得られなければ現状維持で報告。対象メッセージの識別は見出し文字列で検索。
### 5. 不具合是正(あれば)
- 完成段で製品不具合が出たら、Prompt/Gate/閾値を変えない範囲で最小是正+test、報告に明記。
### 6. Git・ログ
- 禁止=`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。対象pathのみcommit→`git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP)。secret grep 0件。wav/raw_usage_log/STOP/lock不追跡(公開mp3は`user_test/`配下のみ)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <上記jsonl> --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_DELEGATION_05.md`(直近既知index=603付近。604以降を試し、先頭行が「# 委任_05｜KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01」のものだけ採用)。

## 報告(`docs/pm/RESULT_PACKET_KPHR5.md`+最終報告)
1. R3の結果(各起動の時刻と間隔・stage結果・文法候補数と選定・検証PASS一覧・公開URL)
2. R2の結果
3. **機能×Family表**(①Part 2 ②Trial-08選定 ③KP HR ④文法HR × X/Z/Y: Status・根拠run)— Fable判定の転記
4. 費用(本委任・KP HR案件累計/300・日次実累計)
5. SSOT差分・commit sha・raw URL・原文再保存の結果
6. RESULT_PACKET 4行+判定整合行
7. 残Open(EVIDENCE_01 §10の3件の扱い、Z小説でStep A''候補0件が多い観察(分類Dの可能性)を含む)
事実と推測を分ける。