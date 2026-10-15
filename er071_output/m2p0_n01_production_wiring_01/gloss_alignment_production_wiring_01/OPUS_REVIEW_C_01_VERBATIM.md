## KGCPW Opus条件C独立レビュー(実装前の安全性確認。採用可否は判断しません)

## 1. 総括
- **BLOCKER 0件 / MAJOR 6件**(M1〜M6)、MINORは複数。
- 判定は**「是正後に進めてよい」**です。設計の骨格(mode廃止とcorrected唯一化、既定ON、kill switch残置、artifact直読みの関所)は妥当です。
- 新規記事を初回から作る経路で、不整合glossが完成物へ流れる反例は見つかりませんでした。OPEN-359の論証(gloss HRの関所は迂回されない)も、第一義(不整合glossが完成物へ流れない)では成立します。
- 一方、**再利用経路(cache・コピーしたrun・`--regenerate-stage`・ON化前の成果物)**と**HR通知の網羅性**に穴があります。どれも数行で直せるので、委任_02の実装セルに含めることを推奨します。
- 以下「安全側(1)」=不整合glossが完成物へ流れない、「安全側(2)」=承認済み仕様が動く、の意味で使います。

## 2. 論点別

**論点1 legacy撤去・golden test・mode廃止・接尾辞: MINOR**
- mode廃止に反対理由はありません。`_corrected`接尾辞を残す判断も妥当です。
- 撤去順序の罠が1つあります。legacy schemaがcorrected schemaのdeepcopy元です(ga:631-641)。現在のproperty順は`rank, current_gloss_consistent, japanese_gloss, qa_reflects…, reasoning, added_word_mappings`(末尾に追加)です。strict schemaでは出力の生成順がこの順に従うため、順序は挙動に効きます。
- golden testの作り方を3点指定すべきです。
  - (a)**撤去前のHEADで先に作る**(mode="corrected"で記録し、撤去後に同じshaを要求する)。
  - (b)対象はmessage文字列だけでなく、fake clientで捕捉した`responses.create`の全kwargs(model・reasoning.effort・`text.format`全体・input)。
  - (c)shaは`json.dumps`を**sort_keysなし**で取る(順序の変化を検出するため)。
- 見落としが1点あります。corrected本体はartifactと戻り値に`"mode": GLOSS_ALIGNMENT_MODE_CORRECTED`を書いています(ga:836/846/866/886)。§2で定数を削除し、§2-4のgrep(`"corrected"`が0件)を満たすには、このフィールドを消すか置き換える必要がありますが、設計に記載がありません。
- さらに`GLOSS_ALIGNMENT_VERSION`はlegacyとcorrectedで同じ値(`ER-003-KP-GLOSS-ALIGN-01`)です。実在するCoffee artifactにはlegacyで再整合した痕跡があります(er019_output/.../coffee_prices__run_m2p0_n01_01/a2/key_phrases/keywords_canonicalized.json:145-146)。
- 代替案: modeフィールドを削除し、**versionを`-02`へ上げる**。旧版の成果物と区別できるようにするためです。

**論点2 撤去範囲: OK(撤去しすぎは無し)**
- correctedが依存しているもの(`_norm_tilde_space`、`_extra_tokens`、`kp_adds_words_beyond_display`、`DEVELOPER_MESSAGE`、`STATUS_*`)は残す側に入っています。
- `gloss_alignment_fallback*`、`gloss_review_hint`を読む外部コードはありません(canonicalizationは自分で書くのみ)。
- 撤去漏れは上記のmodeフィールドと`make_alignment_fn`の既定schema(ga:212、設計に記載済み)だけです。
- grepの追加を推奨: `GLOSS_ALIGNMENT_MODE_CORRECTED`、`"mode": `。

**論点3 正しいglossの不要な書換え: OK(条件差は小さい)**
- モデルはTrialと同一です。A2_SUPPORTもB1_SUPPORTも`gpt-6-luna`(er006_model_routing_contract_01.py:50,89-90)、effortは既定のhigh(ga:199)。
- 対象選定は決定論的なので同一。retry上限も同じ2回です。
- 差は2点です。(i)Productionは1記事の全対象を1 callにまとめる(Trialはパターン別に投入)。(ii)入力本文がlevelごと(Std/Adv)の記事本文。
- どちらも書換え率への影響は小さいと推定しますが、E4で「Std/Adv各1回+整合済みの対照item」を同じcallに混ぜて確認すれば足ります。

**論点4 完成禁止・X rc=0・迂回路: MAJOR(M4、安全側(2))+MINOR**
- 第一義(安全側(1))は満たします。TTS B1(er019:967)、A2(1282)、assemble(1582/1790。Gateの早期return[assemble:472-473]より前)、ページ(2009)は、すべてartifactを直接読みます。
- `--only-segments`、`--stage`の個別起動、`--stage all`、`kp=None`の各経路でも迂回はありません。B1解説LLMはHR判定の後でしか呼ばれません(er019:967→972)。
- **M4(通知の欠落)**: `run_key_phrases`はHR報告を「最終attemptのメモリ上のmerged」から作ります(sc:824-831)。
  - 途中のattemptでHRが出た後に、次のattemptでselection失敗・canonicalization非PASS・cost cap超過になると、`final_merged=None`になり報告が出ません。
  - ところがディスク上には前のattemptのartifact(HR itemを含む)が残ります(sc:713-714は非PASS時に書かない)。消費側はこれを読んで止まるため安全側(1)はOKですが、**HR報告書・event・最終stdoutが一つも出ない**停止になります。停止理由には存在しない報告書名が表示されます。
  - さらに`--stage all`/`assemble`では`_assert_no_gloss_alignment_hr`のRuntimeError(er019:1560)が`print_gloss_hr_final_line`(2520)より先に発生するため、最終stdoutの1行が出ません。
  - 是正(≈5行): (a)Zと同じく**ディスク上のartifactを読んで**HR判定・報告する(Zはer026:1205で実施済み)。(b)最終行の出力を`try/finally`化する。
- X rc=0について: `kp_run_status`をsummaryに記録し、最終stdoutが必ず出るなら「STOP status」要件は満たすと言えます。ただし`kp.get("status")`だけでは、NG_REVIEW_REQUIREDとHRが重なった場合にgloss停止が隠れます(sc:833は既存status優先)。
  - 推奨: `gloss_alignment_run_status`を別キーにする。
  - 任意: main末尾でHRが残っていればrc=2(Zと一致、≈3行)。
- 誤報(MINOR): `resolve_gloss`はHR報告書を消しません(ga:1068-1118)。このため`print_gloss_hr_final_line`(er019:2355、報告書ファイルの有無で判定)が**解消後も「停止中」を出し続けます**。判定をartifactの`collect_unresolved`に変えるべきです。

**論点5 後続工程とcache: MAJOR×3(M1〜M3)**
- **(a) X解説cache = M1(安全側(1))**: Sonnet案の「`gloss_signature`の無い旧bundleは再利用」はfail-openです。
  - 完成済みrunをコピーしてKPを再生成し(E7がまさにこの手順)、display_phraseの並びが同じなら、旧gloss入力で作った解説が再利用されます。
  - なおHR→resolveの経路では旧bundleがNoneで上書きされる(er019:876-896)ため、穴は「コピー+再生成」経路に限られます。
  - 代替案(Zと同じ規則): artifactに`gloss_alignment_status`を持つitemが1件でもあれば`gloss_signature`の一致を必須にする(欠落も不一致扱い)。無ければ従来の署名。
  - 併せて署名に**`key_phrase`も入れる**べきです。既存の穴として、表示候補が同じでcanonicalizationの結果だけ変わるケースを検出できません(er019:921)。
- **(b) Z `kp_expl_b1b`署名: Sonnet案(statusを持つitemがあればgloss含有)が妥当**です。代替案(署名は従来のまま、明示的な再生成に任せる)は危険です。`--regenerate-stage kp_b1b`→HR→resolve→再実行の経路で、display列が同じなら旧gloss入力の解説が再利用されます。既存Melos runは状態フィールドが無いので互換は保たれます。
- **(c) ON化前の成果物 = M2(安全側(1))**: 「残存リスクとして報告」だけで済ませず、**決定論的な未評価検出**を推奨します(≈10行、LLM 0)。
  - 内容: flag ONで消費・再利用する時点で`select_alignment_targets(items)`を評価し、「対象なのに`gloss_alignment_status`が無いitem」があればSTOPして`--regenerate-stage kp_*`を要求する。
  - 適用箇所: XのTTS関所、Zの`stage_kp`再利用後。
  - 効果: 対象0件の成果物(約93%)は互換のまま。対象ありのON化前成果物、legacyの旧プロンプトで再整合されたCoffee artifactも同様に、fail-closedになります。
  - 代替案(kp stageの入力shaにversionを含める)は全run一律でSTOPになり、過剰です。
- **M3(Zの再生成時HR、安全側(2)、一部(1))**: `--regenerate-stage kp_*`でHR停止した場合の問題です。
  - (i)再開時に`ctx.regenerate_stage == kp_lv`だとsnapshot復元がスキップされ(er026:1234)、人間の確定値を捨てて選定をやり直します(E6がZで失敗します)。
  - (ii)runner内の例外で止まるため、`install_kp_assets`も`mark_stale_descendants`も走りません(er062:515-520)。インストール済みの**旧artifact**(ON化前)が残り、`--stage tts_*`を単独で起動するとload_level_inputsが旧KP・旧glossで通過します(安全側(1)の穴。ON化前の成果物の範囲)。
  - 是正: 未消費のsnapshotがあればregenerate指定時でも優先復元する。`_gloss_hr_gate`でraiseする前に`install_kp_assets`を呼ぶ(各1〜2行)。

**論点6 QDC監視: OK(指標の提案)**
- level単位の`gloss_alignment_status`分布(NO_TARGETS/ALIGN_PASS/HR/DISABLED)。
- 対象率: 基準約7%。直近20記事levelで15%超ならアラート。
- attempt≥2の発生: 基準0/145。1件でもあれば当該バッチで報告。
- HR: 1件で即時報告(既存)。
- 対象内のREALIGNED比率。
- 1記事セットあたりのalign費用: 0.6円超ならアラート。
- DISABLEDのProduction run: 1件でもあればアラート。
- 記録のみの機械検査で`uncovered`が出た率(将来gate化を判断する材料)。
- level単位のalign所要秒: 60秒超ならアラート。

**論点7 OPEN-359: 結論OK、反例は通知面のみ(M4)**
- gloss不整合KPが完成版へ流れる反例は**ありません**。
  - retryループ: どのattemptのartifactも「整合済み/NO_TARGETS/HR」のどれかで、不整合のまま通るartifactは生まれません。
  - canonicalization非PASS・`kp=None`・`--only-segments`・stage順・解説LLMの位置も迂回なし。
- ただし通知の欠落(M4)と、「放棄されたattemptのartifactがTTSへ進む」(redundancy NGのKP集合。OPEN-359の本体と同類)は残ります。
- 「今回は(a)のみ、(b)(c)は別承認」は技術的に妥当です。受入条件(gloss)は(b)(c)なしで満たし、(b)(c)は冗長NG・記号NGのKPを止めるという仕様変更だからです。
- ただしM4の「ディスク上のartifactでHR判定」は、gloss通知の受入範囲として今回含めるべきです。

**論点8 既定ONの波及(約65 script): MINOR(許容+明文化)**
- A/B/C系の消費側(er003_v1_n3_01_tts_generate.py等)には関所がありません(`collect_unresolved`はX/Zのみ。Grepで確認)。
- HR時は旧glossで完成しますが、これは現状(OFF)と同じ結果で、悪化はしません。
- 呼出元ごとのopt-inは、DEV専用化の再発や引数ミスによるOFF化の危険があるため**不採用を推奨**します。
- 「完成禁止の保証はX/Zのみ」とSSOTに明記してください。
- 任意の代替案: 共有の`verify_episode_audio_validation_gate`の早期return(assemble:472)より前に`collect_unresolved`を1か所入れる。全Familyに効く集中関所になりますが、A/B/C read-onlyとの整合はFableが判断してください。
- 旧Trial scriptを再実行すると実APIを叩く点にも注意(論点11)。

**論点9 kill switch: OK+MINOR**
- import時評価のままでよいです(call時評価に変えるとtestのmonkeypatch資産を壊し、途中で切り替わる危険もあります)。
- 読込順の差は事実として確認できました。Zはer026:63でvfl01(import時に`load_dotenv`)をscaffold(65)より先にimportするため、`.env`指定が効く見込みです。Xはsc(er019:47)がvfl01(main内2457)より先で、効かない可能性があります(推移的import次第で未確定)。
- 是正: 両runnerがrun開始時に**実効値(ON/OFF)と取得元**をstdoutとsummaryへ必ず記録する。運用では「プロセス環境変数のみ」と定める。

**論点10 失敗注入・E2Eの主張: MAJOR(M5、evidence)**
- 案Cは妥当ですが、より単純で同等の方法があります(案B')。harnessが`ga.make_alignment_fn`をwrapし、**本物の`make_alignment_fn`をfake `client=`付きで呼ぶ**方式です(引数は既にあります、ga:198)。
  - モデル照合・usage・JSON解析・retry・HRまで本物を通り、他のOpenAI呼出を横取りする心配もありません。
- **M5**: E7は自然発生の対象が出る確率が約7%で、ほぼNO_TARGETSになります。これでは「再整合済みglossが完成音声とページへ届く」証拠になりません。
  - 対策: E4の合成対象artifact(実LLMで再整合済み)をE7のTTS→assemble→playerへつなぐ(provenance=synthetic入力+production_formal_path)。
  - 解説の`reused_from_previous_run=false`も確認する。
- E7はコピーしたrunの差分再生成なので、「fresh Production初回path」とは主張できません(「KP段〜KP TTS〜assembleはfresh、他segmentは再利用」と書くべきです)。

**論点11 旧Trial script: OK+MINOR**
- T3の27シナリオをtestへ移植するのは必須で、妥当です。
- 他の6本はコメント注記ではなく、**冒頭で`raise SystemExit("HISTORICAL…")`**にするのが安全です。注記だけだと、legacyのシンボルに届く前にselection等の有料APIを叩いてからクラッシュしえます。

**論点12 Dangling Reference: MINOR(追加検出)**
- (1)`HR_RESOLVE_PROCEDURE_01.md`のファイル名だけを参照する文字列がコード内にあります(ga:946/992、er019:532/1563)。手順書を移すなら同時に更新が必要です。
- (2)docstringの「legacy artifactは常に[]」(ga:901、er019:519/1554)。
- (3)SSOT内の`GLOSS_ALIGNMENT_FAILED_NOTICE.md`/fallback(i)記述はGrepで要確認。
- (4)legacyの`gloss_alignment_status="FAILED"`(ga:388/395)を`collect_unresolved`が認識しません(ga:905)。現在ディスク上に該当0件(Grep確認)ですが、`"FAILED"`も未解決として扱う1行の防御を推奨します。`resolve_gloss`の受理状態にも追加してください。

## 3. チェック表(12観点+条件C 6点)
| 観点 | 判定 |
|---|---|
| 1 必要性 | 必要(承認済み仕様の配線) |
| 2 単純化 | mode廃止で単純化。失敗注入は案B'がより単純 |
| 3 既存流用 | 関所・HR報告とも既存を流用。Zの`_gloss_hr_gate`方式(ディスク直読み)をXへ揃える |
| 4 情報喪失 | M4: HR判定がメモリ上の値に依存し、ディスク上の実体と食い違う |
| 5 不要LLM | 対象itemのみ。解説の再生成はM1是正で必要時のみ |
| 6 非決定性 | 対象選定は決定論的。LLMは対象時のみ |
| 7 HR増 | 約0.2%未満。解消後の誤報(論点4)は要是正 |
| 8 不要Rewrite | Trial 0/32。golden testで固定 |
| 9 コスト | +0.014〜0.08円。E7の上限は事前算出 |
| 10 retry整合 | 本体はOK。Zの再生成×HR再開が不整合(M3) |
| 11 Failure安全 | 新規初回経路は安全側(1)。再利用経路はM1〜M3 |
| 12 再発防止 | 未評価検出(M2)で構造的に塞げる |
| C-1 Trial専用化 | mode廃止で解消 |
| C-2 全体矛盾 | A/B/Cは関所なし(明文化) |
| C-3 初回/retry/fallback一致 | 一致。再生成経路のみM3 |
| C-4 Dangling | 論点12 |
| C-5 Failure安全 | 上記11と同じ |
| C-6 QCD新問題 | 小。監視指標は論点6 |

## 4. 設計文書に無い追加所見
- **MAJOR(M6、範囲外・別OPEN推奨)**: Adv英語解説LLMの「phrase」は**display_phrase(候補)**で、glossは参考情報です(er019_family_x_kp_explanation_01.py:152-155。Zもer026:1269で同じ)。
  - 再整合後は「phrase "based on" × 参考訳『インタビューをもとにした』」という食い違った入力になります。完成音声も「EN: based on interviews → 解説: based onの解説 → EN再掲」となります。
  - これは元からある構造ですが、再整合の対象item(約7%)にまさに集中します。解説のphraseは`key_phrase`にすべきか、別件としてユーザー判断が必要です。
- MINOR: 完成済みrunでKPを再生成した後、TTSを飛ばしてassembleすると、旧音声で通過します(Gateはstatusのみ見て、テキストとartifactを照合しない)。元からある問題です。
- MINOR: `--level both`でa2がHRになるとassembleの例外でb1bのassembleも止まります(er019:2507-2511)。健全なlevelが巻き添えになります。

## 5. 委任_02で必ず入れるべきtest・evidence
- golden test: 撤去前に作成し、`responses.create`の全kwargsのsha(順序込み)を固定する。
- attempt0でHR→attempt1でselection失敗の場合に、ディスク上のartifactからHR報告・event・最終行が出る(M4)。
- `--stage all`でHRがあるとき、最終stdoutの1行が出る。
- NG_REVIEW_REQUIRED+HR itemでX TTS/assembleが止まり、summaryに`gloss_alignment_run_status`が出る。
- X解説cache: 旧bundle+status付きartifactで再生成され、key_phraseの変化でも再生成される(M1)。
- Z署名: status無し→従来署名(Melos互換)、status有り→gloss含有。
- 未評価検出: 対象ありでstatus無し→STOP、対象0件→通過(X/Z)(M2)。
- Zの`--regenerate-stage kp_a2`→HR→resolve→同じ指定で再実行するとsnapshotから復元し、インストール済みの旧assetでTTSが通らない(M3)。
- `resolve_gloss`後に最終行の誤報が出ない。
- legacyの`"FAILED"`をartifactから検出し停止する。
- Production呼出元が`mapping_gate=True`を渡さない、引数`gloss_alignment_mode`が存在しない、を固定する。
- 実効flag値の記録(ON/OFF、取得元)。
- E8はOPENAI_API_KEYを空にして実行し、raw usage 0件を確認する(実API誤呼出の検出)。
- E4の合成対象artifactをE7へ連結し、解説の`reused_from_previous_run=false`を確認する(M5)。

## 6. 配線後も残るリスクと報告方法
- (1)実LLMでのretry/HR経路は未発火(0/145)。HR経路の証拠は失敗注入のみ。
- (2)完成禁止の保証はX/Zのみ(A/B/Cは関所なし)。
- (3)ON化前の既存完成物(Melos run_e2e_01/02、Coffee。Coffeeにはlegacyで再整合したglossあり)は再評価していない。M2を入れれば再利用時に止まる。
- (4)OPEN-359本体(冗長NG・記号NGのKPがXで完成へ進む)は未解決。
- (5)Adv解説がdisplay_phrase基準である件(M6)。
- (6)kill switchの`.env`経由はXで効かない可能性。
- 報告では「安全側(1)は新規初回経路で成立」と「再利用経路・既存完成物は対象外または是正後」を分けて書いてください。`PRODUCTION_WIRED`の根拠にE2E(合成対象を連結したもの)が含まれるかを明示し、TrialのVALIDATEDと混同しないでください。

## 7. 追加で読んだファイルと答え切れなかった点
- 自己申告: (e)の手順に反し、一部は読む前の1行宣言をせずに読みました。
- 追加で読んだもの(計約45k文字): er019の範囲外(770-880、1935-2000、2365-2526)、約25k文字/er003_key_words_canonicalization.py:707-752、約3k文字/er019_family_x_kp_explanation_01.py:140-164とGrep、約2k文字/er062:470-522、約3k文字/OPEN_ITEMS.md 865行、約2.5k文字/Grep多数: routing、artifactの`gloss_alignment_status`の実在確認、test呼出元、er026のimport順
- DESIGN_DRAFT_01とHR_RESOLVE_PROCEDURE_01は読んでいません。A'構造は再レビュー対象外のため。
- 答え切れなかった点: Xの推移的importで`load_dotenv`がga importより先に走るか。SSOT内のlegacy記述の有無。Z mainの終了時stdoutの文言。

(Fable付記: 上記はopus-consultantの最終回答を逐語転記したもの。Fableは本委任前に`"mode": `フィールド4箇所(ga:836/846/866/886)・`final_merged`経路(sc:825-828)・`HR_RESOLVE_PROCEDURE_01`参照(ga:946/992)をGrepで実在確認済み。)
