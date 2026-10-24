# 委任文(Fable→sonnet-worker)
管理ID: FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_01(Phase 0: 『告げ口心臓』Advanced三人称化の根本原因追跡[runtime evidenceベース]+上流工程の対策設計+Opus条件Aレビュー依頼書+SSOT記録。**API 0円**。LLM呼出・有料runは禁止。実装・Phase 1生成は次委任=Opusレビュー後のFable Go)
Family: Z / 対象: 『告げ口心臓(The Tell-Tale Heart)』Advanced=ユーザー最終試聴NG・受入不可(2026-10-25) / 改善Trial: ユーザー承認済み / Production仕様変更・採用: 未承認

## 0. ユーザー原文(2026-10-25、逐語。まず `docs/pm/delegation_log/2026-10-25_FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01_USER.md` に以下を一字一句そのまま保存すること)

```
# Claude Code指示｜Family Z 原作の本質・エッセンス保持改善Trial

## 1. ユーザー評価・現状

Family Z『告げ口心臓（The Tell-Tale Heart）』Advancedは、**ユーザー最終試聴NG・受入不可**です。

理由は、原作が主人公自身による一人称（I）の独白であるにもかかわらず、Advanced版が三人称（He）の語りに変更されていることです。

『告げ口心臓』の魅力は、狂気を帯びた主人公が自ら語り、その異常な心理を読者に直接伝えるところにあります。

三人称への変更は、出来事自体が維持されていても、作品のエンターテインメント性を著しく損ないます。

これは単なる人称の不一致ではなく、**原作の本質を損なう重大な品質問題**です。

- 現行Advanced：ユーザー受入NG
- 作品全体：最終承認保留
- 改善Trial：ユーザー承認済み
- Production仕様変更・採用：未承認

## 2. 改善の基本原則

**原作の長さ・語彙・構文・枝葉の描写は変更してよい。しかし、原作の語り口や物語の面白さを成立させている本質的要素は変更しない。**

### 語り口

原則として、原作の語り口・視点・人称を維持してください。

- 原作が一人称なら一人称を維持する。
- 原作が三人称なら三人称を維持する。
- 人称だけでなく、語り手の立場や語り方も不用意に変更しない。

重要なのは一人称か三人称かではありません。

**原作の語り方を、理由なく変更しないこと**です。

真に必要な例外は認めますが、原則として変更する必要はないはずです。例外が必要な場合は理由と作品品質への影響を明確にし、ユーザー判断を求めてください。

### 原作の面白さ・本質の保持

語り口に限らず、以下のような作品の本質を損なう変更を禁止します。

- 出来事の因果関係を変える
- 登場人物の心理や動機を変える、または重要な心理描写を失わせる
- 重要な出来事を省略・改変する
- 伏線とその回収の関係を崩す
- 物語の緊張感、意外性、結末の意味を損なう
- その他、原作の面白さを成立させている重要な要素を失わせる

一方、時間尺や英語学習レベルに合わせた編集・要約・表現調整は認めます。

**原作のすべてを残すことではなく、原作の面白さを損なわずに必要十分な長さへ編集すること**が目的です。

## 3. 根本原因の調査

『告げ口心臓』Advancedで、原作の一人称が三人称へ変更された原因を特定してください。

原作 → Seed → Writer → レベル別生成 → 最終本文の流れを追跡し、以下を明らかにしてください。

1. どの工程で語り口が変わったのか。
2. なぜその変更が行われたのか。
3. 既存仕様・Promptのどこに問題があるのか。
4. 語り口以外の原作の重要要素も失われる設計になっていないか。
5. 既存の原作忠実性対策がなぜ今回の問題を防げなかったのか。

推測ではなく、実際のPrompt・入力・出力・runtime evidenceに基づいて分析してください。

## 4. 対策設計｜上流工程を改善する

**新たなCheck機能やValidatorの追加によって解決する方式は、基本的に採用しません。**

目指すのは、問題が発生してから検出する仕組みではなく、**そもそも原作の本質を損なう文章が生成されない設計**です。

既存のSeed・Writer・レベル別生成工程の役割を確認し、最も適切な上流工程で対策してください。

特に以下を重視します。

- 原作分析の段階で、作品の面白さを成立させる重要要素を正しく把握する。
- その情報がWriterまで適切に伝達される。
- Writerが時間尺・語彙・構文を調整しても、重要要素を維持する。
- Standard／Advancedのレベル調整によって原作の本質が変わらない。
- 既存の情報伝達・生成機構を活かし、重複する仕組みを増やさない。

既存の承認済み仕様、過去Trial、Family ZのProduction経路との整合を確認してください。

新たなチェック項目の大量追加や、作品ごとの例外ルールの増殖は避けてください。

Opusによる独立設計レビューを行い、根本対策として成立しているか確認してください。

## 5. Trial検証

### Phase 1：『告げ口心臓』Advanced

上流改善を適用したTrial版を生成してください。

確認事項：

- 原作の一人称による語りが維持されている。
- 主人公の異常な心理や執着が適切に表現されている。
- 緊張感の積み重ねが損なわれていない。
- 重要な出来事、因果関係、心臓音、自白に至る展開が保持されている。
- 時間尺・英語レベル・聞きやすさとのバランスが取れている。

形式的な一致だけでなく、**物語としての面白さが保持されているか**を評価してください。

### Phase 2：既存Family Z作品への横展開検証

Phase 1で改善方式が成立したら、過去のFamily Z作品にも適用して検証してください。

特定作品への過剰適合を避け、原作ごとに重要な要素を適切に保持できるか確認します。

また、過剰に原作忠実性を求めた結果、文章が長くなる、冗長になる、テンポが悪化するなどの副作用がないかも確認してください。

既存の完成版・公開音声は変更しないこと。

## 6. 自律的な原因究明・改善

今回のTrialでは、初回の失敗を理由にすぐユーザー判断へ戻さないでください。

承認済みの範囲内で、

**原因究明 → 対策設計 → Trial → 結果分析 → 必要な改善・再Trial**

まで自律的に進めてください。

同じ方法で成果が出ない場合は、原因や設計方針から見直してください。

ただし、承認済みScope・品質基準・予算上限・必須Gate・STOP条件を遵守し、重大な仕様変更やProduction採用はユーザー判断を必須とします。

## 7. QCD・効率化

優先順位：品質 ＞ 完成速度 ＞ 量産単価 ≫ 開発費

- 既存成果物・中間データを最大限再利用する。
- 独立した調査・設計・評価準備は並列化する。
- 不要な全文再生成・音声再生成は避ける。
- Trialの初期検証はテキスト中心に行い、必要な段階で音声化する。
- 追加LLM工程・Validatorを安易に増やさない。
- 品質を維持しながら、量産単価70円／記事セットを意識した設計とする。

必要十分な品質に到達した時点で追加Trialを終了してください。

## 8. Trial Closeout・報告

Fableによる独立評価を行い、以下を報告してください。

1. 一人称から三人称へ変更された根本原因
2. 原作の本質を失わせていた上流設計上の問題
3. 採用候補となる改善方式と適用工程
4. 『告げ口心臓』Advancedの改善結果
5. 過去Family Z作品への横展開検証結果
6. 原作の面白さ・語り口・因果関係・心理描写・伏線回収などへの影響
7. 費用・所要時間・量産単価への影響
8. Fable独立評価とTrial Closeout Status
9. ユーザー確認用の比較原稿・必要に応じた試聴URL
10. SSOT／Git反映状況と残存Open Item

Trial成功時もProductionへ自動配線しないでください。

**最終目的は、『告げ口心臓』の一人称を直すことだけではありません。Family Zで原作の本質・エッセンスを損なわず、魅力ある英語ストーリーを安定して制作できる上流設計を確立することです。**
```

## 1. Fableが把握している前提(鵜呑みにせず、実際のartifactで確認)
- 対象run: `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01/`(`_bak_pre04/`退避・`_evidence_kcrr1/`あり)。seed: `er026_seeds/the_tell_tale_heart/{seed.json,story.md,source_gutenberg_raw_extract.txt,SOURCE_PROVENANCE.json}`、Production seed置き場 `er026_output/family_z_production_e2e_01/the_tell_tale_heart/seed/`(seed.json+primary_text_excerpt.md+SEED_PROVENANCE.json)。関連docs `docs/research/FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01/{SOURCE_CHECK_01,CP_CHECK_01,SOURCE_FIDELITY_CHECK_01,RUNTIME_EVIDENCE_01}.md`(SOURCE_FIDELITY_CHECK_01がなぜ三人称化を見逃したかも対象)。
- Z経路: `er026_family_z_fiction_production_runner_01.py`(stage順 seed_check,writer,std_adjust→plan,support→kp→tts…)、`er062_family_z_structure_01.py`、`er062_family_z_writer_01.py`、STORY_REGISTRY data-only登録。Std KPに「sure of myself」「froze my blood」があった=Standardは一人称だった可能性が高い→**StdとAdvで人称が異なるなら、レベル別生成(std_adjust/Adv生成)のどこで変わったかが焦点**。Std/Adv両方の最終本文の人称を事実として確認。
- 既存の原作忠実性対策: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01(修正版B=APPROVED_FOR_PRODUCTION→PRODUCTION_WIRED、Seed conversion_plan+結末維持条項、`docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/`)。CURRENT_SPECを「Family Z」「Seed」「conversion_plan」「結末」「忠実」「人称」「語り」「narrat」「point of view」でGrep。Opusレビュー済みのZ設計文書(OPUS_REVIEW_*)も確認。
- 過去Trial照合(PM_GOVERNANCE 21節 A/B/C分類)必須: `DECISION_LOG.md`/`DECISION_LOG_HISTORY.md`/`OPEN_ITEMS.md`/`OPEN_ITEMS_HISTORY.md`/`docs/research/FAMILY-Z-*` を「人称」「一人称」「三人称」「視点」「語り手」「narrator」「POV」でGrep。過去に不採用になった方式の無断再導入禁止。
- 既存Z作品(横展開候補の下調べ): 猿の手・開いた窓・二十年後・賢者の贈り物・メロス等、各原作の人称・語り口と現行完成版の人称を一覧化(読み取りのみ)。『告げ口心臓』以外にも語り口が変わっている作品がないかを事実として確認(公開版は変更しない)。
- 管理: OPEN-503(告げ口心臓)、UDR #188(最終試聴)。本指示=UDR #188への回答(Adv NG・作品全体保留・改善Trial承認・Production採用未承認)。

## 2. Phase 0 作業(API 0)
A. **根本原因の追跡 `ROOT_CAUSE_01.md`**: 原作→seed.json/story.md/primary_text_excerpt→Writer入力Prompt(実際に送られた全文、run内のprompt dump/log)→Writer出力(R0等)→std_adjust/plan/Adv生成→最終Std/Adv本文の各段で、人称・語り手・語り口を実物で確認し、「どの段で」「どの指示/入力の影響で」変わったかを特定。§3の1〜5に逐一回答。Prompt文言のうち三人称化を誘発しうる箇所(例: 「narrator」「characters」「登場人物の名前」「dialogue配分」「Voice割当=語り手+人物」の構造要請など)を行番号つきで引用。語り口以外の重要要素(因果・心理・心臓音・自白)の保持状況もStd/Advで事実確認。既存忠実性対策(conversion_plan・結末維持条項・SOURCE_FIDELITY_CHECK)が人称を対象にしていたか。
B. **既存設計の役割整理**: Seed(原作分析)に何が記録され、Writerへ何が渡り、レベル別生成が何を変えてよい設計か。Family Z Voice割当(決定的Voice割当、語り手+人物)や会話生成器の構造が、一人称独白作品と整合するか(独白中心の作品で「人物の会話」を要請する構造が人称変更を誘発していないか)。
C. **対策設計 `DESIGN_01.md`**(複数案比較→推奨1案、Validator追加方式は原則不採用):
   - 方向性の例(採否はSonnet判断): Seed/原作分析段に「語り口(人称・視点・語り手の立場)」「面白さを成立させる本質要素(因果・心理・伏線/回収・結末の意味)」を既存のconversion_plan等の既存欄で明示→Writer契約に「本質要素は維持、長さ・語彙・構文・枝葉は調整可」を渡す→レベル別生成(std_adjust/Adv)に「語り口・本質要素は変更しない」を既存機構で伝達。既存の情報伝達経路を使い、作品ごとの例外ルールや大量のチェック項目を増やさない。真に必要な例外(例: Voice構造上の制約)があるなら、理由と品質影響を明記してユーザー判断候補にする。
   - 影響範囲: Z Production経路のどのPrompt/構造が変わるか、X/Yへ波及しないか、既存Z作品の再生成が必要になるか(採用時の判断材料、本Trialでは公開版不変)。
   - 評価計画: Phase 1=『告げ口心臓』Advanced(テキスト中心、音声は必要段階で)で§5-1の5項目+「物語としての面白さ」の評価方法(決定論で測れる人称一致+人手評価の観点リスト、Std/Adv両方の確認)、Phase 2=既存Z作品2〜3本(人称・語り口が多様なものを選ぶ: 一人称/三人称/会話中心)へのテキスト適用と副作用(長さ・冗長・テンポ)の計測。
   - 費用: Phase 1(Adv writerチェーン再生成テキスト、必要なら音声)・Phase 2(2〜3作品テキストのみ)の見積(出典のある単価のみ: 『告げ口心臓』run cost.json、『猿の手』等の実績)。Fable案件上限=150円(300円以下=自律枠)。モデルはProduction同一。
   - 撤退条件・STOP条件・Production不変の保証方法(DEV module/Prompt override注入、DEV出力dir)。
D. `OPUS_REVIEW_REQUEST_01.md`(条件A): 論点=(a)根本原因の特定がevidenceに基づくか、(b)対策が上流(Seed/Writer契約/レベル別生成)に置かれ、Validator追加に頼っていないか、(c)作品固有の例外ルール化・過剰適合になっていないか(Z全体で汎用か)、(d)Voice構造・会話生成器との整合(一人称独白とVoice割当)、(e)既存忠実性対策(conversion_plan等)との重複なし・整合、(f)過剰忠実による長さ・冗長・テンポ悪化の副作用、(g)量産単価増分、(h)過去Trial/不採用方式の再導入なし。
E. SSOT: `OPEN_ITEMS.md` に新規OPEN登録(11-8分類必須、種別=Trial、Status=TRIAL_APPROVED_DESIGN_PENDING_OPUS_A、DEV専用・Production変更0)、OPEN-503へ「Adv=ユーザー最終試聴NG(2026-10-25、三人称化)・作品全体保留・本管理IDで対応」を追記、`docs/pm/USER_DECISION_REGISTER_01.md` #188を判断済み(Adv NG・保留・Trial承認・原文path)に更新、`DECISION_LOG.md` 1件、`docs/pm/ACTIVE_TASK.md` 固定ヘッダに本管理IDの行を1行追加しFAMILY-Z-TELL-TALE-HEART行のStatusへ「Adv=USER_NG(2026-10-25)→FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01で対応中」を追記。**並行agent2本(FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 委任_02、FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_02)が同じSSOTを同時編集中。編集直前に再Read・自行のみ最小Edit・衝突時は再Read→再Edit。**編集前にscratchpad(`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\`)へバックアップ、編集後 `git diff --stat -- <file>` で異常な大量差分・空ファイル化がないことを確認。
F. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 503 --out docs/pm/delegation_log/2026-10-25_FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01_DELEGATION_01.md`。冒頭が「管理ID: FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_01」と一致するか確認、不一致なら index 501〜506 を順に試す(`--index -1`不可)。
G. Git: `git status` → 対象pathのみ `git add`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status`(意図外D/Aなし・secret 0件・Production file差分0) → `git commit --only -- <path…>` → `git push origin HEAD:main`。他agent差分混在時は一時index方式。ACTIVE_TASK/RESULT_PACKETはgitignore。
H. 報告 `docs/pm/RESULT_PACKET_FZSE1.md`: ①Std/Adv最終本文の人称の事実、②段別追跡結果と根本原因(§3の1〜5)、③既存Z作品の人称一覧(原作vs完成版)、④21節A/B/C分類、⑤推奨方式と代替案の比較(上流性/汎用性/副作用/量産単価増分/開発費)、⑥Phase 1/2見積と計画、⑦OPUS_REVIEW_REQUEST_01.mdの所在、⑧変更ファイル・commit、⑨`check_delegation_prompt.py`結果、⑩費用(0円)・問題点。**Phase 0完了でSTOP。実装・生成は開始しない。**

## 3. 禁止・注意
- Production code/Prompt/flag/閾値の変更、公開版・Production出力の変更(読み取りのみ。『告げ口心臓』run_sf_prod_01配下も変更禁止)。
- LLM/Web検索/TTS等の有料呼出(Phase 0は完全無料)。
- Validator/Check追加を主対策にすること、作品固有の例外ルール増殖、大量のチェック項目追加。
- `.venv\Scripts\python.exe` を使用。自PID以外のprocess終了禁止。