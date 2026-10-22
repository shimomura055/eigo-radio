FABLE-DELEGATION-MARKER: KP-QUALITY-2ITEMS-委任_01-20261022

管理ID: KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01(新規OPEN採番)。ユーザーがAPPROVED_FOR_PRODUCTIONとした2項目(①KP英語音声の数値・否定保護の解除=3-ASR真理値表の例外なし適用、②CMU発音辞書登録をKP選定の必須条件化)について、Family X/Z共通の**調査・実装設計・未配線module+test**までを行う(費用0、API禁止)。**Production既存ファイル(er104/er105/er003/er006/er078/er019/er026/er062/er063等)の編集は禁止**(別agentがFamily Xの正式Production run(新規2記事)を実行中のため、配線はその完了後の委任_02で行う)。新規moduleは`er108_*`。

## 0. 読む・保存する
- `docs/pm/PM_BRIEF.md`、`.claude/agents/sonnet-worker.md`、PM_GOVERNANCE 8節・11-3・27-7
- 本件の直接の根拠: `docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01/{EVIDENCE_01,AZURE_ITN_IMPACT_01}.md`(C1〜C6候補、判定器のfile:行)、`docs/research/KP-THREE-ASR-MAJORITY-PRODUCTION-01/{IMPLEMENTATION_DESIGN_01,OPUS_REVIEW_COND_A_01,RUNTIME_EVIDENCE_02}.md`(P-07解釈(b)=今回ユーザーが解除)、`docs/research/KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01/IMPLEMENTATION_DESIGN_01.md`(er105の機械検証・retry・診断note・shortfall)、CURRENT_SPEC KP節(Grepのみ。:1986 KPFT、:2914〜 KP3V)。
- ユーザー原文を `docs/pm/delegation_log/2026-10-22_KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01_USER.md` へ見出しから末尾まで逐語保存(§9)。T-0保存 `..._委任_01.md`(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、末尾から探索、本文先頭marker `FABLE-DELEGATION-MARKER: KP-QUALITY-2ITEMS-委任_01-20261022` 一致で確定)。

## 1. Fableの前提整理(設計に反映。異論があれば理由付きで報告)
- ①の適用範囲は**KP英語音声の投票(`er104_kp_three_asr_vote_01.py`の`make_voter`/`tally`/`whisper_needed`と、その呼出側の統一judge内KP分岐、Store再利用時の再判定`er104_kp_vote_reuse_01.py`)**のみ。各票のPASS/NGは既存のclassify_asr_match(本文一致判定)で決め、値ガード・否定差は票に影響させない。P/S割れ→必ずWhisper→2/3でPASS。両NG→NG(Whisper不呼出、既存どおり)。Whisper失敗はPASSにしない(既存`NG_WHISPER_UNAVAILABLE`維持)。`NG_PROTECTED_DISSENT`はKP経路から撤去(非KPの統一judge最終ANDゲート(値DIFF/否定差)は**維持**)。P-03由来の`PASS_WITH_WARNING`(S+W行)は維持。
- Store再利用時: 保存evidenceがP PASS/S NGなら、再利用時にローカルWhisperを保存音声へ実行して多数決(追加API 0)。保存evidenceに両PASSがあればそのまま。
- ②の実装点は**er105(全文選定)の機械検証**(X/Z共通入口)。Lunaの出力各itemについて、構成英単語ごとにCMU登録を確認(辞書は本番が使う`pronouncing`→`cmudict`パッケージの`cmudict.dict`。`pronouncing.phones_for_word`または同等)。正規化: 小文字化、前後句読点除去、アポストロフィ付き語(one's/don't等)はそのまま照合→無ければ分解して照合、ハイフン語は全体→分解の順、数字・記号のみのtokenは不適合、アクセント付き文字(minaudière等)はそのまま照合(登録なし=除外。綴り正規化で救済しない)。**LLM推測・外部辞書・発音台帳による代替合格は禁止**。
- 未登録語を含むitemは選定段階で除外し、既存の診断note(本文後置)に「除外した語句と理由(CMU未登録語: …)」を載せて再選定(既存のretry上限内)。基本形化・一般化後の形(`one's`/`someone's`等)もCMUで再確認(canonicalization後の後段検査を1箇所追加。不適合ならINVALID扱いで既存の外側retryへ)。候補不足時は既存のshortfall処理(3件未満可、数合わせしない。ユーザー原文の「5件」は現行3件の読み替え)。
- Prompt 2本文は不変(sha固定)。レベル別基準・本文一致・5語以内・一般化後段のみ・再生順序は不変。A/B/C(27-7)は不変。
- 配線は委任_02(2記事Production run完了後)。runtime evidence計画: ①=保存音声(coffee `pump one's fist` 8本+KP3V保存84件)を本番adapter経路で再判定(API 0)し偽NG回避を示す+正式run中のStore再利用再判定/新規KPで投票発火、②=X small_bag a2(`novelty minaudière`を含む本文)とZ melosのKP段を正式経路で実行し除外→再選定を記録(各≤数円)。合計≤40円見込み。

## 2. 成果物
1. `docs/research/KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/INVESTIGATION_01.md`: ①の判定経路図(file:行。値ガードがKP投票に効く全箇所、Store再利用、X/Zの呼出点、HR Lock/retryとの関係)、②の選定〜canonicalization〜gloss〜TTS plan間でKPテキストが確定する箇所と検査挿入点、CMU辞書の実体pathとversion、正規化が必要なtoken型の実例(保存KP 548 segmentのトークンをCMU照合して「未登録率」「誤除外になりうる型(固有名詞・省略形・ハイフン等)」を集計)。
2. `docs/research/KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/IMPLEMENTATION_DESIGN_01.md`: 変更箇所一覧(file:行、X/Z/共通)、新旧の判定表、撤去する分岐・識別子(`NG_PROTECTED_DISSENT`等)とDangling確認方法、Store再利用時の再判定仕様、②の正規化規則・除外→再選定→shortfallのフロー、retry/fallback/resume整合、既存test更新一覧、追加test一覧、runtime evidence計画と見積、SSOT更新文案(CURRENT_SPEC KP節のP-07解釈(b)の置換、KPFTブロックへのCMU条件追記)、Opus確認事項(Q形式)。
3. 未配線module `er108_kp_cmu_lexicon_gate_01.py`(②の照合・正規化・除外判定の純関数群)+`er108_kp_cmu_lexicon_gate_01_test_01.py`(登録語/未登録語/one's/don't/ハイフン/数字/アクセント/大文字/句読点/`novelty minaudière`除外/`pump one's fist`通過 等)、`er108_kp_vote_noguard_01.py`(①の票集計の純関数=既存`tally`の無保護版、既存voter構造と互換)+test(真理値表4行、Whisper失敗、PASS_WITH_WARNING行、保存evidenceの再判定で`Pump 1's fist`がWhisper経由PASSになる固定fixture)。Production参照0をtestで確認。
4. 保存データ検証(API 0): `er104_stored_audio_reeval_02.py`相当の経路で、保護解除版を仮適用した場合の保存84件+coffee 8本の判定変化(旧→新)を表にする(偽PASSが増える件(問題音声21件の中で新PASSになる件)があれば必ず明示)。
5. SSOT: 新OPEN採番(`APPROVED_FOR_PRODUCTION_DESIGN_PENDING_OPUS`)、`docs/pm/REPORT_LEDGER.md`1行。commit(自分のファイルのみ)、secret_scan hits=0、`git push origin HEAD:main`。`docs/pm/RESULT_PACKET_KPQ1.md`に4行+判定整合行、ACTIVE_TASK更新。

## 3. 報告
設計要点、Opus確認事項、保存データ検証の表(特に偽PASS増加の有無)、CMU未登録率の集計、配線委任への引継ぎ(所要見込み・並列化案)、raw URL。

## 9. ユーザー原文(逐語保存用)
# Claude Code／Fableへの指示
## Family X／Z共通 — Key Phrase品質改善2項目 Production Wiring

### 1. 目的・承認Status

以下2項目はユーザーが正式採用を承認済み。

**Status：APPROVED_FOR_PRODUCTION**

Family X／Zの両方について、現行Production経路への実装・検証・SSOT/Git反映を完了し、**PRODUCTION_WIRED**まで進めてください。

新たな採用判断や追加Trialの承認は不要です。

### 2. 変更① Key Phrase音声の数値・否定保護を解除

**対象：Family X／Z共通**

Key Phrase英語音声に対して、既存の「数値・否定の不一致を多数決より優先してNGにする保護機能」を解除してください。

承認済みの3-ASR判定ルールを例外なく適用します。

| OpenAI（Primary） | Azure（Secondary） | 最終処理 |
|---|---|---|
| PASS | PASS | PASS |
| PASS | NG | Whisperを実行し、多数決 |
| NG | PASS | Whisperを実行し、多数決 |
| NG | NG | NG |

- Whisperは3番目の判定者として使用。
- 2/3がPASSなら最終PASS。
- Key Phrase英語音声以外は、既存の数値・否定保護を維持。
- TTS・ASRモデルやVoiceの変更は不要。

**今回の確認済み事実：**

ユーザーは `pump one's fist` の対象音声を試聴し、正しい発音であることを確認済み。

Azureの `one's → 1's` という表記整形が数値保護に引っかかり、Whisperが実行されずHuman Reviewになった。

これは正常音声の不要なNGと判明しているため、同様の停止を防止すること。

### 3. 変更② CMU発音辞書への登録をKey Phrase選定の必須条件にする

**対象：Family X／Z共通**

Key Phraseの選定に以下を追加します。

**CMU発音辞書に登録されていない単語を含むKey Phraseは選定不可。**

実現方法はClaude／Fableに委任します。

ただし、次の要件を満たすこと。

- Key Phrase全体ではなく、構成する英単語ごとにCMU登録有無を確認する。
- 大文字・小文字や句読点等によって登録語が誤って除外されないようにする。
- 未登録単語がある候補は、選定時点で除外し、既存選定基準に基づき別候補を選ぶ。
- CMU辞書に登録されていない語を、LLMの推測や外部辞書の発音で代替して合格扱いしない。
- CMU登録条件を満たす候補が不足する場合は、既存の候補不足・例外処理との整合を確認する。条件を緩和して無理に5件を埋めない。
- 既存の選定品質基準、本文中に存在する表現を選ぶ条件、レベル別基準を維持する。

**選定段階で未登録語を確実に防ぐことが重要です。**

生成後の検査だけでなく、必要なら候補の再選定まで自動化してください。

### 4. 実装範囲と共通仕様の整合

両変更ともFamily X／Z共通仕様。

以下を確認し、必要な場所へ反映してください。

- 正式初回Production経路
- Key Phrase選定・検証・再選定
- TTS／ASR判定
- retry／fallback／regeneration／resume
- 保存済みデータの再利用時の適合性
- Validatorおよび既存テスト
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS
- Git commit／push

DEV／Trial専用経路への実装だけでは完了としない。

旧仕様の不要な分岐・検査は整理し、Dangling Referenceを残さないこと。

既存の完成記事や保存音声について、今回の変更だけを理由とする一括再生成は不要です。

### 5. テスト・Production Wiring Gate

最低限、以下を検証すること。

**変更①**

- Key Phraseで片側PASSの場合、数値・否定差があってもWhisperが呼ばれる。
- Whisperを含む2/3 PASSで最終PASSになる。
- 両NGの場合は従来どおりNG。
- Key Phrase以外では既存の保護機能が維持される。
- Family X／Z双方で正常動作する。

可能なら今回の保存音声を再利用し、`pump one's fist` の偽NGが回避されることを検証する。

**変更②**

- CMU未登録単語を含む候補が除外される。
- 登録済み単語だけで構成される候補は正常に選定できる。
- `minaudière` のような未登録語がKey Phraseに採用されない。
- 候補不足・再選定・retry経路でも制約が維持される。
- Family X／Z双方の正式経路で正常動作する。

**PRODUCTION_WIRED判定には、正式runtimeでの発火証拠、必須Regression／integration test PASS、両Familyへの配線、SSOT・Git反映が必要です。**

コード実装や単体テストだけでPRODUCTION_WIREDとは判定しないこと。

### 6. QCD・自律実行

優先順位：

**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- 必要十分な品質に到達したら追加検証を増やさず完了する。
- 独立工程は原則並列化し、不要な待機・日付分割を行わない。
- 保存済み成果・既存テストを最大限再利用する。
- 量産単価70円／記事セットを目標に、追加API・再生成コストを最小化する。
- 承認済み範囲の不具合は自律的に原因究明・修正・再検証する。
- 既存予算・個別承認枠・STOP条件を守る。
- 新たな仕様変更が必要な場合のみユーザー判断に回す。

### 7. 最終報告

FableはClaudeの完了報告を独立検証したうえで、以下を簡潔に報告すること。

1. 変更①・②それぞれのFamily X／Z別Status（PRODUCTION_WIRED可否）
2. 正式Production runtime evidence
3. ASR多数決とCMU制約のテスト結果
4. retry／fallback等の整合確認
5. 既存記事・音声への影響
6. 実費と量産単価への影響
7. commit hash／push結果／SSOT反映
8. 未解決Open Itemとユーザー判断要否

**両Family・両項目ともPRODUCTION_WIREDを目指し、承認範囲内で一括完了させてください。**