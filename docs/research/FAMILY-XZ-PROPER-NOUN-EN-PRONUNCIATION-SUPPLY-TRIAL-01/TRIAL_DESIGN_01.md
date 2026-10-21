# TRIAL_DESIGN_01: 固有名詞の英語発音供給(検出→調査→登録→供給) Offline Trial設計書

管理ID: FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01 委任_01(設計のみ。API 0・費用JPY0・Production/Ledger/Prompt/設定 無変更)
Status(到達上限): `DESIGN_READY_PENDING_OPUS_REVIEW`(実行は委任_02、Opus条件Aレビュー+Fable照合の後)。Trial結果の上限は`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`、Production採用はユーザーのみ。
作成日: 2026-10-21。並行: `FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01`(①、判定関数の不具合是正。本Trialは①の関数を呼ぶだけで変更しない)。
ユーザー原文: `docs/pm/delegation_log/2026-10-21_FAMILY-XZ-ASR-MULTI-DIFF-FIX-AND-PROPER-NOUN-EN-PRONUNCIATION_USER.md`(①agentが保存する正本。下記の引用は①委任文[`docs/pm/delegation_log/2026-10-21_FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01_委任_01.md`]内の「原文ここから〜ここまで」から逐語)。

## 1. 目的とユーザー原文の該当条文(逐語)

### 1-1. 目的(§1)
> **② 未登録の英語固有名詞について、正しい発音を調査・登録し、Azure Phrase Listなどの後続工程へ供給する共通仕様を検証する。**
> 対象はFamily X・Zの両方。片方だけの改善で完了としない。
> 既存の品質基準・同音等価ルール・Azure Phrase List重み2.0・TTS Fallback仕様は変更しない。

### 1-2. §3「固有名詞の英語発音供給」(逐語)
> **位置づけ：仕様設計・Offline Trial。Production正式採用は未承認。**
> 対象はFamily X/Zの英語本文に登場する、英語発音情報が未登録の固有名詞・ブランド名・造語等。
> 既存のPronunciation Ledger、固有名詞検出、読み解決、Azure Phrase List、TTSヒントの仕組みを調査し、共通資産を最大限再利用する。
> 設計・Trialで以下を実現する。
> 1. `byUs` のような小文字始まりの名称も、文脈を踏まえて固有名詞候補として検出する。
> 2. 未登録の場合は、公式サイト・公式発表など信頼できる情報源を検索し、**正しい英語での発音**を確認する。
> 3. 日本語のカタカナ読みから英語発音を機械的に推定・確定しない。
> 4. 根拠を記録したうえで、Pronunciation Ledgerへ英語発音情報を登録する。
> 5. 登録情報をAzure Phrase Listおよび必要なTTS・ASR工程へ供給する。
> 6. Azure Phrase Listへの実投入内容と重み2.0の適用を、実行証拠で確認できるようにする。
> 7. 読みが確定できない場合は、誤った読みを登録・強制しない。既存の安全な判定経路を維持する。
> Family X/Zの共通仕様として設計し、Familyごとの適用結果を確認する。

### 1-3. §4(必須再現ケース、逐語)・§5・§6(②)
> | `byUs`（公式の英語読み） | 未登録検出→根拠確認→Ledger登録→Phrase List投入 |
> | `byUs → Bias` | 同音等価として適切にPASS |
> | `byUs → Bias` ＋ `story-making → storymaking` | 複数の許容差分が共存してもPASS |
> | `LINE` | 正しい固有名詞として扱い、必要な読み情報を供給 |
> | `LINE → Lion` | 実際の発音が異なる場合、誤PASSさせない |
> | `two works → 20 works` | 数値の重大な不一致としてNG |
>
> 実際の音声が誤発音している可能性と、ASRの誤記は区別する。実音声が誤っている場合は、ASR判定だけをPASSさせて品質改善完了としない。

§5(要旨): 既存の音声・ASRログ・Ledger情報を優先的に再利用し、A機能面/B品質面(正しい音声を誤NGにしない・誤発音/単語違い/数値違いを誤PASSさせない・既存LedgerやPhrase Listに悪影響を与えない)/C QCD(TTS再生成削減・API検索費用・待機時間・70円/記事セット)を検証。追加の有料検証は既存証拠で不足する部分に絞る。

> **②はTrial専用経路で実施し、正式Productionには配線しない。** Trialで良好な結果が出ても `VALIDATED` にとどめ、ユーザーの正式採用判断を待つ。(…)判定基準・同音等価ルールを独断で拡張しない。必要十分な品質に到達したら追加Trialを行わず終了する。

(`two works→20 works`と`byUs→Bias`系の判定自体は①の担当。②は「Ledger/Phrase List供給を加えても①の判定結果が変わらない」ことだけを検証する。)

## 2. 既存資産の棚卸しと再利用方針、21節 A/B/C 分類

### 2-1. 棚卸し(すべてGrep→Readで確認、行は2026-10-21時点)
| # | 資産 | 内容(確認事項) | 出典 |
|---|---|---|---|
| R1 | Pronunciation Ledger | entry構造=surface/entity_type/canonical_spelling/language_origin/expected_pronunciation_ipa/pronunciation_hint/alternate_pronunciations/confidence/sources/ja_reading_*/tts_injection_disabled。ledger_id=sha256(surface小文字+entity_type+source_context)なので、**既存`byus`(entity_type=ja_reading_katakana)と別entity_typeのEN entryは別キーで共存**できる。`LEDGER_PATH`はモジュール変数で`_load()`が呼出し時に読むため、Trial processで差替え可能 | `er006_pronunciation_ledger_01.py:15,95-105,107-148` |
| R2 | `get_hint_for_text` | 本文にsurface(大小無視・語境界付き)があり**`pronunciation_hint`が非空**のentryだけ返す。**Phrase Listは`h["canonical_spelling"]`のみ**がAzureへ送られ(発音文字列は送られない)、TTSヒントは`surface`+`pronunciation_hint`。X(`er003_v1_repro01_main_generate.py:357`,`er003_v1_crosslevel_audio_02_common.py:366`)とZ(`er012_b_family_voices_production_01.py:551`、`er063`は`er012`経由)が**同一関数を同一引数(min_confidence="low")で呼ぶ**=X/Z共通 | `er006_pronunciation_ledger_01.py:164-206` |
| R3 | Azure Phrase List | `if phrases:`内でのみ`PhraseListGrammar`生成・`setWeight(2.0)`(定数、flag迂回不可、2026-10-20 APPROVED_FOR_PRODUCTION)。全Azure呼出が同一関数経由。**投入内容の記録機構は現行なし**(usageは`phrase_list_size`のみ)。実投入証拠は`Speech_LogFilename`診断ログの`speech.context`(`dgi.Items`/`bias`)で取得可能(Z重み採用で実証済み) | `er006_secondary_asr_01.py:68-75,88-111`、`docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01/wire_evidence_prod_01.py:1-31`、同`wire_evidence_prod_01.json`(`"bias":2.000000`と`dgi.Items`を確認)、`er084_azure_phraselist_weight_trial_01_lib.py:67`(`extract_weight_evidence`) |
| R4 | EN研究(Perplexity) | `research_pronunciations`(model既定`sonar`)。Prompt=一次情報源優先、**confidence=highは本人音声sourceのみ**(テキスト書起しのみ・二次情報源はmedium以下)、`ambiguity_note`に音声/テキスト区別を明記。出力に`pronunciation_hint`(平易な綴り発音、例`oh-TOH-nee`)・IPA・alternate | `er006_pronunciation_research_01.py:48-85,92-140`、`CURRENT_SPEC.md:1829` |
| R5 | JA側の未知語検出+Web調査(参照実装) | `resolve_unknown_ja_tokens`=Gate検出の未知Latin語→cache→Ledger→OpenAI Responses `web_search`(`gpt-5.6-sol`、`make_writer_research_fn`)→confidence判定。run上限5回、negative cache(6h)、`disable_web_lookup_for_test`。今回byUsのカタカナはこの経路(telemetry 13:11:24、sources=prtimes) | `er025_entity_pronunciation_resolver_core_01.py:129-255,266-406`、`er002_ja_web_research_r3.py:106-135` |
| R6 | EN側resolver | **キャッシュ参照+「Ledgerにlow登録済み」語の再research(上限5/run)のみ**。**未登録のEN固有名詞を事前に抽出する工程は存在しない** | `er025_entity_pronunciation_resolver_core_01.py:439-531` |
| R7 | ASR側reactive lookup | ASR Cascade尽くしても解決できなかった`entity_like`なspanだけ`cascade_unresolved_entity`で登録(HR用、PL用にhintが入る場合あり)。TTS注入は`cascade_unresolved_entity`を除外(誤entry事故対策、BLOCKER-1) | `er006_secondary_asr_01.py:341-372`、`er006_pronunciation_ledger_01.py:28-39` |
| R8 | entity_like | 原文で先頭大文字の語+非ASCII外来語のみ。**Ledger登録語のentity_like化は`LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION=False`(2026-09-28ユーザー判断、DEFERRED/NOT_ADOPTED、OPEN-208)** | `er006_preprod_hardening_01_validation.py:467-489,525-536,1056`、`CURRENT_SPEC.md:2390-2420` |
| R9 | M1複数発音候補(2026-10-13 APPROVED_FOR_PRODUCTION、配線済み) | CMU未収録のcanonical単語に限り、Ledger entryのIPA(expected/alternate)を凍結候補(C2)とする。条件=surface一致・単語1語・`ja_reading_katakana`除外・canonical_spelling==surface・**sources非空**・segment開始前のentry。F1で全差分説明可能な場合のみPASS_WITH_WARNING。**既に承認済みの「Ledger発音情報→ASR同音判定」の供給路** | `er006_m1_multi_candidate_01.py:208-247`、配線=`er006_secondary_asr_01.py:197,236-287`、原文=`docs/pm/delegation_log/2026-10-13_ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01_01.md:45` |
| R10 | CMU層 | `byus`=B AY1 AH0 S(`bias`と同一)で、CMU収録語同士は既存の同音機構で判定済み(Ledger不要) | `PROPER_NOUN_PHRASELIST_INVESTIGATION_01.md` §3-3 |
| R11 | TTS発音ヒント注入 | `augment_style_prefix_with_pronunciation`が`min_confidence="medium"`で本文中のLedger語の`"surface" is pronounced approximately "hint"`をstyle_prefixへ追記。`tts_injection_disabled`/`cascade_unresolved_entity`は除外。**TTS音声が変わる経路** | `er006_pronunciation_tts_injection_01.py:26-66`、`er025_entity_pronunciation_resolver_core_01.py:439-` |
| R12 | 前調査 | byUs: JA entryのみ(hint空・IPA空・sources空)→PL空(Azure 12/12行`phrase_list_size=0`)→`setWeight(2.0)`未実行。LINE: Ledger未登録。Family Z: `melos/dionysius/selinuntius`はJAカタカナentryのみ(hintなし)、`melos`の`cascade_unresolved_entity`(low)のhintに括弧付き別案の混入文字列あり | `docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/PROPER_NOUN_PHRASELIST_INVESTIGATION_01.md` §1,§3、`ledger.json`の現行38件を本書で再読(read-only) |

### 2-2. 本書での追加確認(read-only・API 0)
1. 現行Ledgerで記事B(`run_byus_01`)の全10segment(`tts_generation_results.json`の`canonical_text`)に`get_hint_for_text(min_confidence="low")`を再計算 → **全segmentでPhrase List空**(`byus`はhint空のため除外)。前調査の結論を独立に再確認。
2. **新発見(本Trialの設計範囲外、参考報告)**: Ledgerに`us`(cascade_unresolved_entity, low, hint=`uhn-NOHN`)が登録されている。`get_hint_for_text`の語境界一致により、本文に単語`us`を含む**任意のsegment**でPhrase Listに`"us"`が入り得る(記事Bの10segmentには単語`us`が無く未発火)。さらに`melos`(cascade)のhintに括弧付き別案が混入。誤entryが実害を出す型の既知問題(BLOCKER-1)と同種。本Trialの登録validator(3-5 V3)で新規登録は防ぐが、既存entryの是正は別件(判断候補J5)。
3. M1(R9)があるため、**CMU未収録のZ人名(Dionysius/Selinuntius/Framton/Sappleton等)は、EN entryにIPA+sources+canonical_spelling==surfaceを登録するだけで、既存承認済みのM1経路が自動的に利用する**(コード変更・判定基準拡張なし)。一方`byUs`/`LINE`はCMU収録語なのでM1のC2は不使用(既存CMU層が対象)。なお現状の`melos/dionysius/selinuntius`はJAカタカナentryでM1のC2から明示除外される(R9)。

### 2-3. 21節 Existing Spec / Prior Trial Check Gate 分類
| 要素 | 分類 | 根拠 |
|---|---|---|
| Azure Phrase List重み2.0 / PL内容=ledger canonical_spelling | **A 既存仕様あり**(変更しない) | `er006_secondary_asr_01.py:68-75`、2026-10-20 APPROVED。PLへの内容供給経路(R2)も既存 |
| CMU同音・M1のLedger IPA利用・F1 | **A** | `CURRENT_SPEC.md:1829`、2026-10-13承認(R9)。本Trialは使うだけ・拡張しない |
| Perplexity発音調査Prompt・confidence基準(high=本人音声のみ)・許容発音集合(2026-08-28 APPROVED) | **A** | `CURRENT_SPEC.md:1829`、R4 |
| Ledger登録語→entity_like化 | **B 過去判断あり(未採用)** | 2026-09-28ユーザー判断 DEFERRED/NOT_ADOPTED、OPEN-208。**本Trialで再有効化も検証もしない** |
| 外部発音根拠とTTS実音声の自動照合によるAUTO PASS | **B(STOP済み)** | OPEN-83、2026-08-28。本Trialは範囲外 |
| Ledger EN entryの事前登録(TTS前)→PL/TTS供給 | **B/C境界** | JA側は事前登録が正式採用済み(R5、PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01)。EN側は`resolve_and_augment_en_style_prefix`のlow-confidence再researchまでで、**未登録語の事前検出は未実装**(R6) |
| **未登録EN固有名詞の事前検出(小文字始まり・造語・文脈手がかり)→調査→登録→供給の一連** | **C 本当に新規(新仕様候補)** | 過去Trial・決定に同等なし(前調査案B=「新仕様候補、判断候補」と整理済み)。Trial専用経路で検証、VALIDATED止まり |
| 読み未確定語へのPhrase List spelling-only供給 | **C(新仕様候補、本Trialでは測定のみ)** | ユーザー§3-7(確定不能なら登録・強制しない)と緊張関係。供給の是非は採用時のユーザー判断(J2) |
| 判定基準・同音等価の拡張(多語→1語`Buy Us`、辞書外綴り、Ledger許容発音集合をCMU収録語の判定に使う) | **D 新判断(本Trialでは実施しない)** | ユーザー§6「独断で拡張しない」。必要性の件数だけ測定し分離報告(J3) |

## 3. 処理フロー案(Trial専用経路)

### 3-0. 構成原則
- **Production関数はimportして読み取り・呼出しのみ**(`get_hint_for_text`、`research_pronunciations`/`make_writer_research_fn`、`LedgerKey`/`upsert`、`classify_asr_match`、`evaluate_attempt_with_cascade`、`get_full_text_via_azure_stt_with_phrase_list`、`m1_multi.freeze_candidates`)。新規実装は**検出器・登録validator・harness・集計**のみ(`er089_proper_noun_en_supply_trial_01_*.py`、`er089_output/proper_noun_en_supply_trial_01/`)。
- **Trial用Ledger**: 実`ledger.json`を実行開始時に**コピー**(sha256記録)し、harness内で`pronun_ledger.LEDGER_PATH`をコピーpathへ差し替える(importしたProduction関数が同じモジュール変数を読むため、関数側は無改変)。実Ledgerへ書かない。実Ledgerは他runで更新され得るため、開始/終了のsha256を記録し、Trial processの書込先がコピーのみであることをtestで固定する。
- 未承認機能のflag/Productionへの新コード経路は**置かない**(Production側変更0)。

### 3-1. フロー(文章図)
```
[入力: EN本文(segment text) + 文脈(記事タイトル/テーマ/Writer事実カードのFact内の固有名詞・サービス名)]
   | (a) 候補検出  D1 規則抽出(決定的,API 0) 和 D2 LLM文脈抽出 -> 候補集合 {surface, 種別, 根拠スニペット}
   v
   | (b) 未登録判定  Trial Ledgerを大小無視で引く。「EN発音情報あり」=entity_type != ja_reading_katakana かつ hint非空 かつ sources非空 かつ 汚染検査OK かつ confidence>=medium
   |        - あり -> 登録済み(再調査しない)
   |        - なし -> 調査対象(JAカタカナentryのみ/hint空/low/汚染あり を含む)
   v
   | (c) 発音調査  既存Perplexity研究(R4,ベースライン腕B) と OpenAI web_search(最新推奨モデル,腕A) を同一入力で比較
   |        Prompt: 公式サイト/公式発表/本人・公式動画で確認できる「英語発音」。カタカナ/日本語読み/綴りからの推定を禁止。根拠URL・該当文言の逐語・音声/テキスト区別を必須
   v
   | (d) 登録判定(validator V1-V6) -> 確定可: Trial Ledgerへ登録 / 確定不能: 登録しない(UNCONFIRMED_SAFE、理由コード記録)
   v
   | (e) 供給  Production関数がTrial Ledgerをそのまま読む
   |        E1 Azure Phrase List: get_hint_for_text(text,"low") -> canonical_spellingのみ(+重み2.0、既存関数)
   |        E2 ASR同音: 既存CMU層(無変更)+M1 C2(CMU未収録語のみ、承認済み、無変更)。Ledger許容発音集合をCMU収録語の判定に使う拡張は【しない】
   |        E3 TTSヒント: 既存注入経路が自動で拾う(音声が変わる)。本Trialは tts_injection_disabled=True で登録しTTS生成なし(設計のみ)
   v
   | (f) 実投入証拠  Trial harnessが各Azure呼出でSDK診断ログを取り dgi.Items / bias を抽出して1行/呼出で記録
```
再利用資産と新規実装の境界: **既存=R1〜R11の全関数(無改変)**/**新規(Trialファイルのみ)=D1/D2検出器、validator、EN発音版研究Prompt(新規文面、R4と同形式のJSON)、harness、集計**。Production側変更は0(記録機構の追加は3-6の提案のみ)。

### 3-2. (a) 候補検出
- **D1 規則(API 0)**: (i)文中の大文字始まり語(文頭語は除外し文脈判定へ)、(ii)CamelCase/語中大文字(`byUs`,`iPhone`,`YouTube`)、(iii)引用符・強調マーカー付き語、(iv)手がかり語の前後(`called/named/known as/pronounced/spelled/dubbed/so-called/app/service/platform/brand/company`の直後n語)、(v)本文中の読み明示文(`It is pronounced “bias.”`の型。**候補を拾う手がかりにだけ使い、発音の根拠にはしない**=Writer自己生成のため)、(vi)Writer事実カード(Research Ledger)のFact内の固有名詞(サービス名・組織名。格納場所は委任_02 S0でGrep確定、現時点では未確認)、(vii)ハイフン/数字入り造語。除外: CMU収録の一般語で文脈手がかりなし、Ledgerで「EN発音情報あり」の語。
- **D2 LLM文脈抽出**: 入力=segment本文+記事タイトル/テーマ+Fact固有名詞リスト、出力=`{surface, kind(brand/person/place/org/coinage/product), why(本文の手がかり引用)}`のJSON。**LLMは"候補提案"のみ**でD1の候補を捨てる権限を持たない(D1とD2の和集合。再現率優先、誤検出の増加はコスト増にしかならず登録validatorで安全側に落ちる)。
  - モデル: **gpt-6.1-sol(OpenAI推奨・バランス、25節の最新世代推奨系)**。比較として本番ライン候補の**gpt-6-luna**(効率系・低コスト)を同入力で併走し、検出結果の一致/不一致を比較(例外理由=本番採用時の単価検討用、評価報告に明記)。出典=`docs/pm/dev_eval_model_inventory_01.md`(2026-10-09取得)。`gpt-6.1-sol`は`pricing_snapshot.json`未登録のため、委任_02 S0で単価登録が前提(費用ガード、Fable確認)。最新モデルID/可用性は委任_02 S0で再確認(**未確認**)。
  - 費用見積: 入力~1.5k tok+出力~0.5k tok/呼出の想定で、sol(入力$2/出力$10 per 1M)≈$0.008(JPY1.3)/呼出、luna($0.1/$0.5)≈JPY0.07/呼出。検出対象=記事B全10segment+Melos代表3+Open Window代表3程度=約16呼出 → sol≈JPY 20、luna≈JPY 1(想定tokenに基づく概算。実測は委任_02で記録)。記事単位1呼出にまとめる運用も比較(sol≈JPY 3〜5/記事)。

### 3-3. (b) 未登録判定
- Trial Ledgerを`_surface_matches_text`相当(大小無視・語境界)で検索。「EN発音情報あり」の定義は上記フロー(b)のとおり。それ以外は調査対象。
- 現Ledgerからの期待: `byUs`=JA entryのみ→調査対象、`LINE`=未登録→調査対象、`melos`=cascade(low、汚染hint)→再調査対象、`dionysius`/`selinuntius`=JA entryのみ→調査対象。

### 3-4. (c) 発音調査
- ベースライン腕B=既存`research_pronunciations`(Perplexity `sonar`、無改変、まとめて1 request)。比較腕A=OpenAI Responses `web_search`(`make_writer_research_fn`を無改変で呼び、**新規user_message=EN発音版Prompt**。R4と同形式のJSON schemaを要求しparseを容易にする)。両腕とも同一対象・同一Promptの意味内容で、結果を腕間比較(sourceの質・hint一致・confidence)。最新原則(25節)上、本命は腕A、腕Bは現行資産のベースラインであることを報告に明記。Perplexity側の最新世代モデルの存否は未確認(委任_02 S0で公式一覧確認、あれば追加)。
- Prompt要点(英語版・新規文面): ①英語話者がこの名称をどう発音するかを、公式サイト・公式発表・本人/公式動画/ポッドキャスト等の**一次情報源**で確認 ②日本語のカタカナ表記・日本語読み・綴りからの推定を発音の根拠にしてはならない。根拠が日本語表記しか無い場合は`UNCONFIRMED` ③各項目に`source_url`・`quote`(該当箇所の逐語)・`source_type(audio_video/official_text_phonetic/dictionary/other)`・`confidence`(R4基準:highは本人/公式の音声のみ)・IPA・`pronunciation_hint`(英語綴りベースの平易な発音綴り)・複数の英語圏発音があれば`alternate_pronunciations`(許容発音集合、2026-08-28基準) ④公式な英語発音が存在しない/不明の場合は`UNCONFIRMED`と理由。
- 呼出回数: Family単位で未登録候補をまとめて1呼出(X: byUs,LINE,他候補、Z: Dionysius,Selinuntius,Framton Nuttel,Sappleton,Vera等)。既存の1プロセス5回上限(R5/R6)の範囲内。
- 費用見積(中央): 腕A: web_search 3〜6回×$0.01=JPY5〜10(`pricing_snapshot.json` web_search $10/1,000 calls)+token(入力~15k×$2/M+出力~3k×$10/M≈$0.06=JPY10)≈**JPY 15〜20/呼出**。2呼出(X,Z)≈JPY 30〜40。腕B(Perplexity sonar): ≈JPY 1〜2/呼出(`raw_usage_log.jsonl`の`pronunciation_research`実測 224〜268 in/155〜268 out token。リクエスト課金は未確認)。**総研究費の中央≈JPY 35〜45**。時間: 1呼出30〜90秒。

### 3-5. (d) 登録判定と記録(安全側ルール)
登録は**V1〜V6すべて満たす場合のみ**。1つでも不成立なら**登録しない**(`UNCONFIRMED_SAFE`として理由コードを記録し、Trial Ledgerへも書かない=§3-7準拠)。
- V1 根拠: `sources`に実在URLが1件以上、かつ`quote`(発音または英語読みに言及する逐語)がある。`source_type`が日本語表記のみの場合は不可(§3-3)。
- V2 非カタカナ推定: `pronunciation_hint`/IPAの根拠が「カタカナ読みからの変換」でないこと(Prompt禁止+`quote`がカタカナのみのとき不可+`ambiguity_note`が日本語表記のみを根拠と示す場合は不可)。
- V3 形式: `pronunciation_hint`が単一の平易な綴り(ASCII、括弧・全角・"or/または/英国寄り"等の別案混入なし、長さ上限)、`canonical_spelling`==本文中の綴り(大小除く)。複数の許容発音は`alternate_pronunciations`へ構造化。**既存Ledger`melos`型の汚染を作らない**。
- V4 confidence: R4基準のまま(high=音声source、それ以外medium以下)。lowは登録しない(PLは`min_confidence="low"`で拾うため、低品質なhintを流さない安全側)。
- V5 競合: 同surfaceの既存entry(別entity_type含む)とhint/IPAが矛盾する場合は登録せず競合を記録(上書き禁止)。
- V6 追跡: `retrieved_at`・モデル名・Prompt sha・`response_id`・腕(A/B)を記録し、既存フィールド`resolution_method="en_web_research_trial"`・`resolved_at_stage="trial_pre_tts"`を使う(スキーマに新規フィールドは追加しない)。
- 登録entry: `entity_type`=研究結果のtype(product/organization/person/place等。`cascade_unresolved_entity`は使わない=M1/PL/TTSの扱いを混在させないため。M1は`pronun_ledger._load()`のsnapshotを使うため`LEDGER_PATH`差替えで追随=`er006_secondary_asr_01.py:232-236`)、`tts_injection_disabled=True`(Trialの切り分け)、`sources`=URL配列。

### 3-6. (e) 供給と(f) 実投入証拠
- **E1 Azure Phrase List**: 既存`get_hint_for_text`が自動で拾う(登録=供給)。**送るのはcanonical spellingのみ**。ASRが出した異表記(Bias/Byus/Buy Us等)はPLに入れない(誤綴りへ重みを付け許容拡張になるため禁止)。
- **E2 ASR同音判定**: `byUs→Bias`はCMU収録語同士でLedger不要(R10)。CMU未収録のZ人名は、登録したIPA/alternateが**既存M1のC2として自動で使われる**(R9。sources空等の条件未達entryは使われない)。**判定基準の拡張に当たる項目は実装しない**:(x)`Buy Us`(多語→1語)、(y)辞書外綴り`Baias/BAYAS/FAYAS`、(z)Ledger許容発音集合をCMU収録語の判定に使う。仮にあれば救えた件数だけ測定報告し(判定は変えない)、要否は採用時のユーザー判断(J3)。
- **E3 TTSヒント**: 既存注入経路(R11)は`pronunciation_hint`を`min_confidence="medium"`で自動注入する(**登録すると音声が変わる**)。本Trialは`tts_injection_disabled=True`で登録しTTS生成を行わず、効果は別Trial(J1、要TTS費用)。
- **(f) 実投入証拠**: Trial harnessが各Azure呼出で`SpeechConfig.set_property(Speech_LogFilename, <log>)`を付与(Production関数は無改変。`wire_evidence_prod_01.py`方式、`SpeechConfig`の呼出前ラップ)。呼出ごとに1行JSONL(`phrase_list_evidence.jsonl`): `wav, segment, condition(pl_off/pl_on), phrases_expected(get_hint_for_text由来), dgi_items(SDKログから抽出), bias(SDKログ), weight_const, match(phrases_expected==dgi_items かつ bias==2.0), transcript, err, sdk_version`。SDKログにキー/regionが出ないことをredact確認。**Production側への記録追加は提案のみ**: `raw_usage_log`のAzure行に`phrase_list`(語リスト)と`phrase_list_weight`を追加(現行`phrase_list_size`のみ)。実装は採用判断後。

## 4. 必須ケースの事前固定表

共通条件: 判定関数は**①の是正反映後のProduction関数**(`er006_preprod_hardening_01_validation.classify_asr_match`、`er006_secondary_asr_01.evaluate_attempt_with_cascade`、`_step_alternate_pass`)を無改変で呼ぶ。委任_02開始時にgit shaと①の完了状態を記録。①未完了なら該当ケースは`BLOCKED_BY_FIX01`と記録し、①の期待値を②が独自に固定しない。各ケースで**Trial Ledger有/無の2条件**で判定結果を取り、差が出ないこと(Ledger/PL供給が判定基準を動かしていない)を確認する。

| ID | 再現ケース | 入力(既存データ) | 判定に使う関数 | 期待(事前固定) | PASS/NG根拠 |
|---|---|---|---|---|---|
| K1 | `byUs`: 未登録検出→根拠確認→Ledger登録→PL投入 | 本文=`er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/b1b/audit/tts_generation_results.json`のsegments.`full_story_part1`/`full_story_part3`の`canonical_text`。Ledger=現行コピー | 検出器(a)、(b)、研究(c)、validator(d)、`get_hint_for_text`、SDKログ(f) | **要求達成(機械PASS)**=byUsが候補に出る ∧ 未登録判定=調査対象 ∧ 登録成功 ∧ `get_hint_for_text`→`["byUs"]` ∧ SDKログ`dgi.Items`にbyUs ∧ bias=2.0。**安全終了**=`UNCONFIRMED_SAFE`(登録0・PL空のまま、理由コード付き)は§3-7に適合する安全側だが**"要求の達成"にはならない**=USER_DECISION_REQUIRED候補として明示 | 予想: byUsの公式情報(PR TIMES等)は日本語表記"バイアス"のみの可能性が高く、V1/V2で`UNCONFIRMED`になり得る(**未確認**)。この場合のASR効果測定は4-1の腕M |
| K2 | `byUs→Bias`単独 | part1の転写から他差分を除いた形(①のgolden fixture。実attempt3 Primary=`Byus`/Azure=`bias`の実転写[`ADV_FULLSTORY_RETRY_ANALYSIS_01.md`]) | `classify_asr_match`→`_step_alternate_pass` | `HOMOPHONE_EQUIVALENT`/`cmu_alternate`でPASS系(`B1B_RES` adapter.layers=['cmu_alternate']の既存挙動と同一) | 既存CMU層(R10)。**Ledger有/無で結果同一** |
| K3 | `byUs→Bias`+`story-making→storymaking` | part1 attempt1 Primary転写(実データ) | 同上(①是正後) | ①是正後にPASS(①のgolden期待に従う。②は独自固定しない)。①未反映=`BLOCKED_BY_FIX01` | ②は「Ledger/PL供給でこの判定が変わらない(悪化しない)」だけを確認 |
| K4 | `LINE`: 正しい固有名詞として扱い必要な読み情報を供給 | part1の`LINE Manga`を含む文。Ledger未登録 | 検出器(大文字語は既存entity_like=True)、(b)〜(e) | 候補に出る ∧ 研究 ∧ [登録→PL=`["LINE"]`]または`UNCONFIRMED_SAFE`。一般語`line`とCMU同音(L AY1 N)だが**公式英語読みの根拠は研究結果が出るまで固定しない(未確認)** | V1〜V6 |
| K5 | `LINE→Lion`: 実音声が異なる場合に誤PASSさせない | (i)実転写: part1 attempt2 Azure=`Lion Manga`、同wavのPrimary=`LINE Manga`(`B1B_RES`)。(ii)canonical`LINE Manga`×転写`Lion Manga` | (ii)`classify_asr_match`(Case A: `line` L AY1 N vs `lion` L AY1 AH0 N、CMU代表発音不一致) | (ii)**PASS系にならない**(`TRUE_CONTENT_MISMATCH`等)。腕N: 実音声が確実に`Lion`のwavで、PL有でも`LINE`と転写されて誤PASSにならない | (i)は4-2の多数決で音声側を区別。(ii)は関数の決定的出力 |
| K6 | `two works→20 works` | part3 attempt2 Primary転写(`B1B_RES`、数値protected) | `classify_asr_match`(protected_number) | NG維持。PL/Ledgerの有無で変化しない。part3 att2のwavをPL有でAzure再転写した結果も、数値違いが残る限りNG | 既存仕様(数値保護) |
| Z1 | Z: Melos/Dionysius/Selinuntius等 | `er026_output/family_z_production_e2e_01/melos/run_e2e_06`等のwav(202本中、固有名詞を含む要retry/不一致attemptを委任_02 S1で既存結果から選定) | 検出、研究、登録、`get_hint_for_text`、M1(C2)、Azure PL | 必須名の候補再現率100%。CMU未収録名はIPA登録後に`m1_multi.freeze_candidates`が候補化(M1 auditで確認) | R9の条件 |
| Z2 | Z: The Open Window(Framton Nuttel/Sappleton/Vera) | 音声未生成(`the_open_window/run_e2e_01`はwriter段まで)。`the_open_window/seed/seed.json`とwriter出力本文 | 検出〜登録〜`get_hint_for_text`まで(ASR A/Bは音声がないため`N/A`) | 検出・登録・PL供給の証拠まで。Z実音声での効果検証は音声生成後(別管理) | Zで検出〜供給が共通コードで動くことの確認 |

### 4-1. 腕M(登録非依存のASR測定)
K1が`UNCONFIRMED_SAFE`でも、PLへ`["byUs"]`を入れた場合のAzure認識の変化は測定できる(PL内容=canonical spellingのみで、発音の確定とは独立)。腕Mは機構・効果の測定であって「Ledger登録」の代替ではない(報告で明確に区別。spelling-only供給の是非はJ2)。

### 4-2. 実音声の誤発音とASR誤記の区別
- 複数ASR一致: 同一wavを、Primary(OpenAI gpt-4o-mini-transcribe、既存転写を再利用=費用0)、Azure(PL無)、Azure(PL有)、**ローカルfaster-whisper(medium。`models--Systran--faster-whisper-medium`がローカルキャッシュ済みであることを確認、費用0)**で比較する。
- 区分(事前固定): `AUDIO_LIKELY_CORRECT`=独立エンジン(Primary/whisper/Azure)の過半数がcanonical(またはCMU同音)、`AUDIO_LIKELY_MISPRONOUNCED`=過半数が別語(Lion等)、`AMBIGUOUS`=割れる。`AMBIGUOUS`は誤発音の可能性を排除できないので**PASS扱いにせず**、ユーザー試聴の要否としてFableへ報告。
- 試聴ground truth: **現時点で無い**(記事Bは試聴ページ公開済みだがユーザー試聴PASS未取得、OPEN-431)。得られたattemptがあれば優先(委任_02 S0で確認)。無ければ上記3エンジン多数決+腕N。
- 腕N(5-3): 正解既知の合成wav(確実に`Lion`)で「PLがLion音声をLINEと誤PASSさせない」を直接検証。

## 5. 検証計画(§5 A/B/C)

### 5-0. 原則
既存wav・既存転写・既存Ledgerを最優先で再利用し、不足部分だけ有料。判定基準・同音等価は変えない。必要十分(§6)に達したら追加Trialしない(反復はAzure非決定性評価の2回まで)。

### 5-1. A 機能面
| 項目 | 方法 | 事前基準 |
|---|---|---|
| 検出精度 | 正解セット(委任_02 S0で固定、Fable確認): 必須=byUs, LINE(X)/Dionysius, Selinuntius, Melos, Framton Nuttel, Sappleton, Vera(Z)。非候補セット=一般語や別途処理される語(例 story-making, Manga, AI。S0で本文から選定)。D1,D2,D1∪D2の再現率/誤検出数 | 必須語の再現率100%(D1∪D2)。誤検出は件数報告のみ(安全側、コストにだけ影響) |
| 英語発音の根拠妥当性 | 腕A/B比較。Fableが`quote`の妥当性を確認。V1〜V6適合率 | 登録された全entryがV1〜V6を満たす(100%)。誤登録(無関係URL/カタカナ推定)があれば即REJECTED材料 |
| Ledger登録の正確性 | Trial Ledger差分(追加entryのみ・既存entry無変更)を機械検証、実Ledgerはshaで不変確認 | 既存38件のハッシュ不変、追加は新規entryのみ |
| PL実投入・重み2.0実適用 | 3-6(f)の記録。X: part1/part3、Z: Melos代表 | PL期待==dgi.Items ∧ bias==2.0 が全PL有呼出で100% |
| ASR・同音判定への効果 | 5-2 | 5-2の基準 |
| 未登録/検索不能語の安全対応 | 存在しない擬似造語1〜2件(例 "Zorbleflux")を候補に混ぜ、`UNCONFIRMED_SAFE`(登録0)になること | 誤登録0 |
| X/Z両方 | X(記事B)/Z(Melos、Open Window[検出〜供給のみ])を同一コードで実行し結果を並置 | 両Familyで同一コードが動作 |

### 5-2. ASR A/B(既存wav再ASR、有料の中心)
- 対象wav(X): `er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/b1b/narration/attempts/full_story_part1_attempt{1,2,3}_englishstyleprefixwidemargin.wav`、`full_story_part3_attempt{1,2,3}_...wav`(byUs/LINE/two worksを含む)+対照`full_story_part2_attempt1_...wav`(byUs/LINE無し=PLで悪化しないか)=**7本**(各約2.4MB≒約50秒、サンプリング仕様は委任_02 S1でwav headerから実測)。(Z): Melos既存wavから固有名詞(Dionysius/Selinuntius等)を含み過去にASR不一致のあったattempt**4本**(委任_02 S1で抽出)。
- 条件: `pl_off`(PL空=現行Production相当)vs `pl_on`(`get_hint_for_text`由来のTrial Ledger PL、重み2.0)。Azureは非決定のため**各条件2回**。計 (7+4)本×2条件×2回=**44呼出**。各転写を既存関数に通して分類(NG→PASS/PASS→NG/変化なし)。
- 費用: Azure `USD1.0/audio-hour`、JPY160/USD → JPY0.0444/秒(`er084_azure_phraselist_weight_trial_01_lib.py:24,54`、`pricing_snapshot.json`)。約50秒/本→JPY≈2.2/呼出 → **44呼出≈JPY 97**(上限見込み。Zのwavが短ければ減)。Primary転写は既存結果を使用(再ASRしない)=0、ローカルwhisper=0。
- 評価基準(事前固定、**判定基準は変更しない**):
  - 悪化なし: PASS→NG が0件(対照part2を含む)。
  - 誤PASS増なし: 腕N、およびer084の負例(`er084_output/azure_phraselist_weight_trial_01/`、Melosの誤認識負例)で、Ledger由来の新規PL語による新規誤PASS(NG→PASS系かつ実音声は別語)が0件。2026-10-20の重み2.0採用時に既知の副作用(`Mullos→Melos`等+3)はユーザー承知で採用済みのため、それに積み増さない(Ledger由来の追加語分を別集計)。
  - 効果(情報): byUs/LINE等で`pl_on`が`pl_off`よりcanonical/CMU同音に近い転写を出す割合。効果が出ない場合は`VALIDATED_NO_ASR_BENEFIT`相当としUDR(価値対費用の判断材料)。「必ず改善」は基準にしない(Z重みTrial Phase Bは410行・正例9件中flip up 2件と効果が限定的だった=`docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01/PHASE_B_RESULT_01.md` §1)。
- 誤NG評価: 既存PASS済み音声(対照part2、Z PASS済み数本)で`pl_on`により判定が悪化しないこと(上記「悪化なし」)。

### 5-3. 腕N(合成負例、TTS極小)
- 目的: K5「実音声が異なる」を正解既知で検証。`Lion Manga`/`LINE Manga`/`bias`(=byUsの誤読)/`Buy us`を含む短文(各<5秒)を既存TTS関数で生成=**TTS 4〜6クリップ**(≈JPY 0.5〜1.5/クリップ想定、実測は`raw_usage_log`のTTS行から。上限JPY 10)。`pl_off`/`pl_on`×2回でAzure(短クリップ≈JPY 0.2/呼出)。期待: 音声`Lion`の転写が`pl_on`で`LINE`へ誘導されない(誘導=誤PASS)。
- **TTSを使うため委任_02の委任文でFableが明示許可すること**(本委任_01は「T-2: TTSなし」)。許可されない場合は腕Nを省略し、K5は実音声多数決(4-2)+関数の決定的出力のみで評価、PL誤誘導リスクは**未確認**として報告。

### 5-4. Family Z側
- Melos(既存wav多数): M1 C2が使えるCMU未収録名(Dionysius/Selinuntius等)。現ledgerは`ja_reading_katakana`のみでC2から明示除外(R9)。登録後の`m1_multi_candidate` audit(候補・一致・no_match理由)を記録。
- The Open Window: 音声未生成。検出〜登録〜供給(PL期待値)まで。人名(Framton Nuttel/Sappleton/Vera)は公式音声が無い可能性が高く、辞書/一般発音(許容発音集合)で`medium`登録になり得る(2026-08-28基準(3)(4)、CURRENT_SPEC.md:1829)。V4に従いlowは非登録。
- 現Zの`melos`(`cascade_unresolved_entity`、low、hint汚染)は**変更しない**(実Ledger書込禁止)。Trial Ledgerコピー上で「再調査候補」としての扱いを記録するのみ。

### 5-5. QCD見積
| 項目 | 見積 | 出典/根拠 |
|---|---|---|
| 検索費用(運用想定) | 語ごと1回きり(Ledger cache永続)。バッチ1呼出≈JPY 15〜20で2〜5語 → **JPY 3〜8/新規語**(腕A)。Perplexity経路ならJPY 1前後/語 | 3-4 |
| 検出LLM費用(運用想定) | 1記事1呼出でluna≈JPY 0.1〜0.3 / sol≈JPY 3〜5 | 3-2 |
| 削減効果 | 実測: byUs起因+他要因で第1部/第3部の計10.31円/本+待機20分。うち確実に削減可能と言えるのは**①(story-making)起因の第1部5.16円/10分**であり、PL(②)で第3部が通るかは辞書外綴り`Baias/BAYAS/FAYAS`のため**未確認** | `PROPER_NOUN_PHRASELIST_INVESTIGATION_01.md` §2(5),§4 |
| 70円/記事セットへの影響 | 新規語2語/記事でJPY≈10〜16/記事の追加(2記事目以降は0)。再試行1組回避(5.16円+10分)の頻度が低ければ**原価中立〜やや悪化**。Perplexity経路 or luna検出ならJPY≈2〜4/記事。採用判断はTrial結果の効果頻度次第 | 概算(委任_02実測で置換) |
| 時間 | 事前処理(検出+調査)≈1〜2分/記事増。再試行回避で10分/組短縮 | 同上 |

### 5-6. 評価ラベル(事前固定、最終ラベルはFable)
- `VALIDATED`: A(機能)全基準達成 ∧ B(悪化0・誤PASS増0) ∧ ASR効果が「悪化なし」かつ何らかの改善あり。
- 機能・安全は達成だが効果なし → `USER_DECISION_REQUIRED`(価値対費用)。
- `REJECTED`: 誤登録・誤PASS増・既存Ledger悪化・Production影響のいずれか。
- K1が`UNCONFIRMED_SAFE`で要求未達 → `USER_DECISION_REQUIRED`(代替=spelling-only供給の是非、J2)。

## 6. 安全・境界
- Production非配線。Production codeはimport/呼出のみ。`git diff`でProduction `.py`の差分0をtestで固定(委任_02終了時)。
- 実Ledger書込禁止: Trialは`LEDGER_PATH`差替え+コピー(`er089_output/proper_noun_en_supply_trial_01/ledger_trial_copy/`)。実`ledger.json`のsha256を開始/終了で記録。
- 判定基準不変: 判定関数・閾値・辞書・M1条件・entity_like(`LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION=False`)に触れない。Ledger有/無の判定結果同一性をtestで固定(K2〜K6)。
- 既存TTS音声・正式記事成果物・Master Store・review_queueは変更しない(読み取りのみ)。
- STOP条件: run前に`tools/stop_scope_check_01.py`(rc=3で停止)、外部停止時は再起動しない、原因不明のrc≠0が2回続いたら停止。誤登録(V1〜V6違反の登録)・Trial LedgerではなくProductionパスへの書込・Cap超過見込みは即STOPしてFable報告。
- 費用上限案(Fableが確定): 中央見積≈JPY 150(研究≈40、検出≈5〜20、Azure ASR≈97)+腕N≈10。**Cap案=JPY 250(委任_02単位)**。7-7: 承認済みScope内で300円以下は都度承認不要だが、本Trialは新仕様候補/未承認Trial範囲のため、Fableが委任文でScope・Cap・TTS有無を明示すること。日次はS0で実測(1,000円/日)。
- 並行agent: ①が`er006_preprod_hardening_01_validation.py`等を修正中。②のharnessは①のコミット後のshaに固定して実行し、baseline(PL無)とtreatment(PL有)を同一コードで走らせる(比較条件の同一性)。

## 7. Opus条件Aレビュー観点案(新しい処理フロー)
1. **検出段**: 再現率(小文字・造語・CamelCase・複数語名・文頭語)と、未検出が静かに従来動作へ落ちる点(安全だが効果ゼロ)。D2(LLM)出力のJSON崩れ/幻覚候補が下流を汚染しないか。
2. **調査段**: LLMが日本語記事/カタカナから英語発音を"それらしく"生成する(§3-3違反)リスク。V2の機械検査の限界。腕A/Bの回答差・出典の質。出典URLの実在性検証の要否。
3. **登録段(誤登録の伝播)**: 誤hintの伝播先=①PL(spelling送信のみで発音は送らないが、**spelling自体が誤ならば誤認識を誘導**。重み2.0採用時の既知副作用`Mullos→Melos`型)、②M1 C2(IPA→凍結候補。**誤IPAは誤PASSを直接生む唯一の経路**。sources非空・canonical一致・F1説明条件・secondary_agreeの防壁が十分か)、③TTS注入(誤hintは誤発音。本Trial外だが採用時に致命)。誤登録の撤回手段(`set_tts_injection_disabled`はTTS用のみ。PL/M1用の隔離手段が無い=採用時の設計課題)。
4. **供給段**: `get_hint_for_text`の語境界一致が既存の`us`型汚染entryを拾う(2-2)=既存問題の悪化可能性。PL件数増加時の上限・重み2.0の副作用。
5. **X/Z共通化の落とし穴**: Xは`er003`、Zは`er012`で呼出しは別だがR2で同一関数。entity_type/source_contextの扱い(`seed_work_canon_reading`のsource_context="family_z_melos"型)がEN entryと衝突しないか(V5)。Zは古典/ギリシャ語由来で唯一の英語発音が無い(許容発音集合)。
6. **安全≠成功**: 登録0(`UNCONFIRMED_SAFE`)は安全だが要求未達。機械PASSの定義が"安全な未達"を成功と誤判定しないか。
7. **判定基準を動かしていないことの証明**(Ledger有/無で判定同一)の網羅性。**M1 C2は承認済みの既存経路だが、新規にEN entryが増えるとM1の発動範囲が広がる**(=既存承認の範囲内か、実質的な許容範囲の拡大か)という論点が本設計の最大のグレー点。
8. **評価設計**: Azure非決定性に対し2回反復で十分か、効果判定の統計力(Z重みTrialは正例9件で検出力が低かった)。腕Nの合成負例が実運用のASR誤認識分布を代表するか。

## 8. 委任_02(実行)の作業分解と見積(参考。Fableが確定)
| 工程 | 内容 | 並列 | 時間 | 費用 |
|---|---|---|---|---|
| S0 | stop check、日次実測、①の完了/sha確認、`gpt-6.1-sol`単価登録、Trial Ledgerコピー+sha、正解セット/対象wav/gold固定、モデル可用性再確認(Perplexity最新含む) | - | 30分 | 0 |
| S1 | 検出器(D1/D2)・validator・harness・単体test実装(API 0) | S2準備と並列 | 1〜1.5h | 0 |
| S2 | 検出実行(D1,D2[sol/luna])、候補集計、再現率 | S1後 | 15分 | ≈JPY 5〜20 |
| S3 | 研究実行(腕A/B × X/Z)、validator適用、Trial Ledger登録 | S2後、X/Z並列 | 30〜40分 | ≈JPY 35〜45 |
| S4 | 供給証拠(`get_hint_for_text`再計算、SDKログ付きAzure 1〜2呼出で`dgi.Items`/`bias`) | S3後 | 15分 | ≈JPY 5 |
| S5 | ASR A/B(既存wav 11本×2条件×2回=44呼出、3 process並列) | S3後、S6と並列 | 30〜40分 | ≈JPY 97 |
| S6 | 腕N(TTS 4〜6クリップ+Azure) *Fableの明示許可時のみ* | S5と並列 | 20分 | ≈JPY 10 |
| S7 | 判定再計算(K2〜K6、Ledger有/無)、whisper三者比較、集計、QCD、評価ラベル案 | S5後 | 1h | 0 |
| S8 | SSOT(OPEN_ITEMS/REPORT_LEDGER)、secret scan、commit・push | - | 20分 | 0 |
| 合計 | クリティカルパス S0→S1→S2→S3→S5→S7→S8 ≈ **3.5〜5h**、中央費用≈**JPY 150〜160**、Cap案JPY 250(未確定) | | | |

## 9. 判断候補(Fable付与待ち、27-3 A/B/C/D分類案)
| ID | 内容 | 分類案 | 根拠 |
|---|---|---|---|
| J1 | 採用時の供給範囲: PL+M1のみ / +TTS注入(音声が変わる)。TTS注入は別TTS Trialが必要 | D(新判断、Trial後) | TTS注入は`min_confidence="medium"`で自動(R11)=Production音声挙動の意味的変更 |
| J2 | 読み未確定語のPL供給(spelling-only)の是非。§3-7とは緊張 | D(新判断) | ユーザー原文§3-7。腕Mで測定のみ |
| J3 | 判定基準の拡張(多語→1語、辞書外綴り、Ledger許容集合のCMU収録語判定への利用) | D(新判断・必要性次第) | §6「独断で拡張しない」、2026-09-28 OPEN-208、CURRENT_SPEC.md:1829 |
| J4 | 委任_02のScope/Cap(JPY 250案)・TTS極小使用(腕N)の許可 | Fable確定事項(7-7、新仕様Trial) | 7-7 |
| J5 | 既存Ledgerの汚染entry(`us`、`melos`cascade)の是正 | B(承認範囲内・不具合調査。Fable判断) | 2-2の2、BLOCKER-1同種 |
