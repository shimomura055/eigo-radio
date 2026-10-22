# STAGE1_IMPLEMENTATION_DESIGN_01: 固有名詞の発音情報取得 Stage 1 の Production実装設計書(Opus独立レビュー用)

管理: PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_03 [E-1] / 2026-10-22 / Status管理ラベル: `STAGE1_DESIGN_REVIEWED_WIRING_PENDING_D2`(ユーザー承認=Stage 1実施。Opus独立レビュー[OF-PNPS-S1-01〜10]のFable採否を反映済み[委任_04 E-1b]。**Production .py未編集・未配線**。配線はD-2完了後のE-2。API 0・JPY0。VALIDATED / PRODUCTION_WIREDではない)。
根拠承認: `docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_STAGE1-GO-STAGE2-POLICY_USER.md` §1・§2(Stage 1実施、**発音の合否判定基準・自動PASS条件は変更しない**)。計画=`PLAN_01.md` v2-0〜v2-9。
未配線module=`er097_pronunciation_supply_stage1_01.py`(+`_test_01.py` 56 test PASS[42+Opus反映14])。効果測定=`stage1_effect_measure_01.py`/`_result.txt`。
コード行番号は `git show HEAD:` 基準(HEAD=`7e17a8338`)。

## 0. 先に言うこと(結論と、計画v2からの訂正・開示)

1. **対象は「最終slotでNGになった後の、Human Review用の発音情報取得」だけ**(`er006_secondary_asr_01.py:1061-1076`)。この取得結果(`pronunciation_lookups`)を読むのはHRパッケージ書込(`:419`)と`er008_n8_revalidation_15.py:106`(記録のみ)だけで、PASS/NG・retry・fallbackの分岐は読まない(Grep確認)。したがって**判定関数の入出力は不変**。変わるのは(a)調査を呼ぶか (b)Ledger lookupの命中 (c)HR表示 (d)登録時の検証と階層キーのみ。
2. **計画v2の試算の訂正**: v2は「24ペア中11ペア(46%)が省ける」(一般語9+同一語再調査2)としたが、**同一語の再調査は元々Ledger命中(API 0)であり、省ける調査ではなかった**。実測(`stage1_effect_measure_01_result.txt`)で、Stage 1で省ける有料調査は**18種の語のうち一般語6種の初回調査=33%**(再調査由来の削減は0)。さらに現行Ledger 38件・保存調査ログ32件(成功32・失敗0・items空0)では、**否定記録・統一lookupが実データで効いた件数は0**(構造的リスクの解消・Stage 2の保険として実装する)。詳細は §6。
3. **判定ロジック・閾値・自動PASS条件は不変。将来のLedger蓄積だけが「減る方向にのみ」変わり得る(S1-01・論点B、3経路を開示)**: Ledger entryのcanonical_spellingは`get_hint_for_text(min_confidence="low")`経由でSecondary ASRのPhrase List(重み2.0)になり(`er003_v1_n3_01_tts_generate.py:135-140`、`er006_secondary_asr_01.py:75-111`)、M1のC2候補(CMU未収録語のみ。`er006_m1_multi_candidate_01.py:208-250,276`)にもなる。Stage 1でこれらへ入る将来のentryが減る経路は次の3つで、**いずれも「新entryを作らない」ことによる減少であり、既存entryの変更・追加は無い**:
   (a) 一般語(CMU収録かつzipf>=4.0)のentryを新規に作らない(Phrase Listの語句が減る。M1のC2はCMU未収録語のみなので不変)。
   (b) 否定記録期間中(60日)の語は再調査しない(`items=[]`の語は元々entryが作られないため、Ledger蓄積は不変。再調査が省かれるだけ)。
   (c) 別typeの有効entryが既にある語は、調査用type(cascade_unresolved_entity)のentryを作らない(同綴りの重複entryが増えない。M1は同綴りの全entryを候補化するため、候補集合は不変)。
   保存データでの実発生: 反事実replay(95文)でPhrase Listが変わるのは18文、**原因は`mini`1語のみ**(誤entryだがOPEN-436のvalidatorに掛からず有効のまま。現行でもPhrase Listに載る)。M1の`candidate_set_hash`差異0件。**Fable判断(論点B)**: Phrase List間接影響は許容する。加えて既存の一般語entry `mini` はOPEN-436の枠で**隔離する**(E-2で実施。隔離の前後のPhrase List差分と、保存データでの判定差分0を記録)。Opus所見S1-01に従い、「判定は不変・入力データの蓄積が減る方向にのみ変わる」と整理する(承認範囲B: 自己解決)。
4. **sidecar採用(計画の「Ledger entryの任意キー」からの設計変更)**: 否定記録は「見つからなかった」語であり、現行実装ではLedger entryが存在しない(`items=[]`のときupsertされない)。擬似entryを作るとM1 C2(`er006_m1_multi_candidate_01.py:208-250`)・Phrase List・`get_low_confidence_entries_for_text`(`er006_pronunciation_ledger_01.py:284-`)等のreaderに混入する。このため否定記録は**別file(sidecar)**にし、Ledger本体`ledger.json`を読み書きしない。階層キー(`evidence_tier`等)は実在entryの任意キーとして追加する(§1-5)。

5. **副作用の到達範囲(S1-02)**: 調査API・Ledger登録・sidecar書込・出典ページ取得(HTTP)の**すべては`_resolve_unresolved_entity_for_review`の内側からのみ到達**する。呼出側(`:1061-1076`)は、このmockが`None`を返しても従来どおりstubで動く。したがって既存testのmock隔離(下記)を壊さない配線にする(§2)。
6. **Opus所見の反映(委任_04 E-1b)**: S1-03(例外の捕捉)・S1-04(調査用type entry先処理)・S1-05(別type注記)・S1-07(語境界照合)・S1-08(全体ON/OFF単一定数)はer097に反映済み(test 14件追加)。S1-02/06/09と論点B/E/Fは本書で規定し、E-2で実装する。S1-10(否定記録の即時無効化ロジックは残置可・害なし。sidecar fileは`er006_output/`配下でgit管理**する**[再現性のため。サイズが大きくなれば見直し])。

## 1. 項目別設計

### 1-1. 否定記録(調べて見つからなかった語を60日再調査しない)
- **配線点**: `er006_secondary_asr_01.py:341-387`(`_resolve_unresolved_entity_for_review`)。現行の最終ブロック`:1061-1076`は呼出し元として無変更。
- **「見つからなかった」の定義**(`classify_research_outcome`): `status=="OK"`かつ`items==[]`のみ。現行実装でLedgerに何も残らず、次回も再調査になる**唯一のケース**。item が1件でもあれば(IPA/hintが空でも)現行どおりupsertされ、次回は命中扱い=再調査されないため否定記録は不要(挙動不変)。一時失敗(例外/`CREDENTIAL_REQUIRED`/HTTP失敗/応答不正)は**保存しない**(`TRANSIENT`)。
- **最小diff**: sidecar `er006_output/pronunciation_ledger_01/negative_cache.json`(key=`norm_surface`=アクセント除去・小文字・空白正規化。entity_type非依存)。値=`{key, surface, searched_at, negative_until(=+60日・暫定), ttl_days, reason}`。`negative_status`が`ACTIVE`なら調査せずHRへ「調査済み・未取得」を表示。**即時無効化**: 同綴りの有効entry(ja_reading_katakana・ledger_disabled除く)が記録より後に発音情報つきで作成/更新された、または`human_approved`entryがある場合は`INVALIDATED`。破損file=記録なし扱い(安全側=従来どおり調査)。書込は`os.replace`による原子的置換。
- **Family X/Z・retry/fallback/resume**: 呼出点は統一judge adapter1箇所(`:1061`)。X(`er019_family_x_audio_production_runner_01.py:49`→`er003_v1_n3_01_tts_generate.py:144`)とZ(`er063_family_z_audio_01.py:761`→同)は同じ`evaluate_attempt_with_cascade_detail`を通る。retry/fallback/regenerationの回数・分岐は不変(HR到達後の処理)。resume時に同じ語が再び最終slotに来ても調査が省かれる(費用減のみ)。並列run(X/Z同時)で read-modify-write が競合すると記録が1件欠落し得るが、結果は「再調査が1回増える」だけ(現行Ledger書込と同じ競合特性)。
- **判定不変の保証**: 戻り値`info`はHR用dictのみ。判定語(`final_status/verified/classification/human_review_required/stop_retrying`)を一切返さない(`test_resolver_no_judgement_outputs`)。
- **例外の扱い(S1-03、er097で実装・test済み)**: 否定記録のget/put・出典ページ照合・HR表示キー生成・一般語判定(辞書import失敗)・`is_safe_url`の例外は**すべて捕捉して従来動作へ**(調査する/登録する/表示キーなし)。調査API(`research_fn`)の`transient_exceptions`以外の例外(cost logger未初期化等)・ledger_loader・upsert_fnの例外は従来どおり素通し。sidecarの一時fileは`<path>.<pid>.<uuid>.tmp`(並列runで衝突せず、失敗時も残さない)。
- **rollback(S1-08)**: `er006_secondary_asr_01.py`冒頭にmodule定数**1個** `PRON_SUPPLY_STAGE1_ENABLED = True` を置き、Falseなら従来関数(旧コードを`_legacy_resolve_unresolved_entity_for_review`として保持)の経路に完全に戻る(出力・副作用はバイト一致をtestで確認)。**サポートする組合せは「全ON」「全OFF」のみ**(項目別定数は持たない。持つ場合も併用可だが、testは全ON/全OFFのみで、その他の組合せは非サポートと明記)。er097側にも同名定数と`enabled`引数があり、OFF時は副作用ゼロで`DISABLED_USE_LEGACY`を返す(test済み)。
- **test**: er097 test(否定のTTL境界59/60日・一時失敗は保存されない・破損file・Ledger無接触[sha256]・即無効化4条件)。Production配線後: 実関数で`items=[]`をmockし、2回目に`research_fn`が呼ばれないこと。
- **runtime evidence計画**: 実関数`evaluate_attempt_with_cascade_detail`にmock researchを注入してX経路・Z経路それぞれで「1回目research→否定記録→2回目research呼出0」を確認(API 0)。

### 1-2. entity_type非依存のLedger lookup(取りこぼし解消)
- **現状**: `lookup(LedgerKey(span, "cascade_unresolved_entity"))`(`:341-`、`er006_pronunciation_ledger_01.py:133`)は`ledger_id=sha256(surface,entity_type,source_context)`一致のみ。`person/place/organization/...`の同綴りentry(現行Ledgerに10件: Ottoni/Malmö/Triangeln/Boavida/MTA/Vancouver/Katz/Shapiro/Oimo no Canele/OPEC)は構造的に命中しない。
- **処理順(S1-04、er097実装済み)**: ①**調査用type(cascade_unresolved_entity)のentryが同綴りにあれば、従来のlookupと同じ扱いを最優先**(有効=返す[発音情報の有無を問わない]/`ledger_disabled`=隔離でNone・再調査なし)。②調査用typeが無い場合のみ`unified_lookup`で別typeの有効entry(発音情報つき)を採用。③旧「発音情報の無い有効entryは命中扱い」の対象は調査用type entryに限定(別typeの情報なしentryや別typeの隔離entryは、旧lookupが命中しなかったので従来どおり調査する)。
- **別type採用時の注記(S1-05)**: 採用entryのtypeが調査用typeでない場合、HR表示に「同綴りの別entry(type=○○)の情報。同一対象かは未確認」を1行追加し、`same_spelling_other_type`キーを付ける(test済み)。
- **最小diff**: `unified_lookup(ledger, span)`=同綴り(`norm_surface`一致)から最上位1件。除外=`ledger_disabled`・**`ja_reading_katakana`(日本語読みは英語発音の根拠にしない。M1も除外。melos/museは「日本語読み+英語cascade」の2件であり、日本語読みを返さないことをtestで固定)**・canonical_spellingがsurfaceと無関係(OF-181(a)型)。順位=human_approved > confidence > 発音情報あり > 出典あり > 新しい。
- **互換性不変条件**: 旧lookupが命中していた語(同surfaceのcascade entryがある)は決して`RESEARCH`にならない(`test_decide_priority_and_legacy_invariant`)。隔離entry(`ledger_disabled`)は旧実装どおり「命中・再調査なし・HRに情報なし」(`SKIP_ISOLATED_ENTRY`)。
- **効果(実測)**: 保存HR span 18種で新規命中0件(melos/museは日本語読みが別にあるだけ)。**実データ上の取りこぼし解消件数は0**。構造的リスク(上記10件は旧lookupから見えない)の解消であり、Stage 2で人名・地名のentryが増える前提の下地。
- **判定への影響**: 命中entryはHR表示に使うだけ。ただし**新規entryの作成が減る**(別typeのentryがある語は再調査・再登録されない)ため、Phrase List・M1 C2へ供給されるentryが重複しない方向に変わる。M1はC2をCMU未収録語のみに使い、同綴りの全entryを候補化する(`:208-250`,`:276`)ので、**別typeのentryが既にある語では候補集合は不変**(新規cascade entryが増えないだけ)。replay=§6。
- **rollback/test**: 上記定数`unified_lookup`。er097 test 5件+実Ledger replay。

### 1-3. 一般語の誤トリガー除外
- **規則**(`is_general_word_span`): spanの全tokenが「CMU収録 かつ wordfreq zipf>=4.0」(`wordfreq`は`er015_*`で既に使用中の依存)。実測: `main story`/`one voice`/`another voice`/`us`/`plus`/`mini`=該当、`toteme`/`khaite`/`stephen reicher`(reicherがzipf1.5)/`lindberg`/`altuzarra`/`byus`/`melos`(1.92)/`muse`(3.59)=非該当。閾値4.0は一般語の最小4.44と固有名詞系の最大3.59の間(中間値)。他の候補(CMU収録のみ)は`lindberg/reicher/kallmeyer/ganis`も収録のため判別力がない(実測)。
- **位置づけ**: 「調査を呼ばない」判定専用。判定(NG/UNCERTAIN)・`_unresolved_entity_spans`(`:599`)・HR行きは不変。HRにはstub(`confidence="unconfirmed"`、現行の失敗時stub形式)+階層表示「通常の英語語彙のため調査省略」を載せる。優先順は §1の`decide_span_action`(Ledger命中・隔離が先)。
- **stubの`ambiguity_note`(S1-06、E-2で実装)**: 現行stubの`ambiguity_note`を省略理由別(通常の英語語彙のため調査省略/調査済み・未取得[否定記録]/隔離entry[情報なし])に変える。
- **既存entry `mini`(論点B、E-2で実施)**: 誤entryがOPEN-436のvalidatorに掛からず有効のため、OPEN-436の枠で隔離する。隔離の前後のPhrase List差分(§6-3の18文)と保存データでの判定差分0を記録する。
- **OPEN-436との関係**: OPEN-436(`entry_invalid_reason`、`:77-97`)は「登録後に不正entryを隔離する」事後対策。本項は「そもそも一般語を調査・登録しない」事前対策で、validatorは無改変のまま残す(二重の安全網)。既存の隔離entryはそのまま。
- **誤除外の最悪ケース**: CMU収録かつ一般語として頻出するブランド/人名(例 Apple/Jordan)が除外される。影響=HRに発音情報が載らない(判定は不変・HRは従来どおり発生)。Stage 2ではこの種の語を「合理的推定」層で扱う。
- **効果(実測)**: 初回調査18種中6種(33%)=`another voice/main story/mini/one voice/plus/us`。そのうち5種は既に隔離済みで以後の再調査は元々0。**削減されるのは今後の新たな一般語の「初回調査」**。
- **rollback/test**: 定数`general_word_skip`。er097 parametrize 15件。

### 1-4. Human Review画面の根拠階層表示(表示のみ)
- **配線点**: `:1067-1075`で`pronunciation_lookups[span]`を作る箇所へ`hr_display(...)`の戻り値を**追加キーとして重ねる**(既存キーは上書きしない)。追加キー: `evidence_tier`/`evidence_tier_label_ja`/`lookup_action`/`lookup_entity_type`/`source_urls`/`negative_searched_at`/`negative_until`/`citation_check`/`display_lines_ja`。HR queue(`:410-431`)のJSONLにそのまま乗る。
- **階層(Stage 1は検証状態のみ。公式/実使用/推定の区別は未判定)**: `QUOTE_VERIFIED`/`PRON_IN_CITED_PAGE`/`NAME_IN_CITED_PAGE`/`UNVERIFIED_AI_OUTPUT`/`NO_SOURCE`/`HUMAN_APPROVED`/`NEGATIVE_SEARCHED_NOT_FOUND`/`GENERAL_WORD_NOT_SEARCHED`。**PASS根拠にしない**(CURRENT_SPEC:1837(B)「Ledger情報は自動PASSの根拠にしない」維持)。ユーザー原文の3階層(公式/英語圏実使用/合理的推定)はStage 2(PLAN_01 v3-1)で導入する。
- **CURRENT_SPEC:1837の(a)〜(f)との関係**: (a)表記(b)IPA(c)IPA確定不能の旨(d)pronunciation guide(e)発音根拠source(f)confidenceは全て維持。追加するのは根拠階層・否定記録の2点で、既存6項目を省略・変更しない。E-2でCURRENT_SPEC該当行に追記(追記のみ)。
- **rollback/test**: 定数`hr_display`。追加キーが既存キーと衝突しないこと・Ledger dictを破壊しないこと(copy)をtest済み。

### 1-5. 発音情報登録時の出典ページ照合(V1'。保存キー`source_page_check_v1`)
- **名称と報告上の位置づけ(論点F)**: V1'は「**出典ページ照合(名称・発音表記の出現確認、弱い確認)**」と呼び、保存キーは`source_page_check_v1`(er097のtier名・`evidence_check`キーは互換のため維持し、E-2でLedger保存時に`source_page_check_v1`としても書く)。ユーザー報告では「**ご承認の引用実在確認のうちStage 1で実施できたのは弱い照合のみ。本来の引用確認はStage 2の調査形式変更(Prompt変更で承認が必要)と同時に行う**」と明示する。
- **現状の制約**: 現行researchの出力スキーマにquote欄はなく(`quote欄0`、`INVESTIGATION_01.md`)、`sources`はURLのみ(`citations`)。Promptを変更すると「Production Promptの直接編集」になるためStage 1では**行わない**(Stage 2で新research形式を導入)。
- **Stage 1の確認内容**: 出典URL(最大3件)を取得し、(1)`evidence[].quote`があればその実在(Stage 2用の口、Stage 1では通常空) (2)無ければ「名称」と「IPA/hint」が本文に**語境界つきで**実在するか(S1-07: 空白を残した正規化テキスト上の語境界一致。`ottoni`は`bottonix`にマッチしない。照合に使う発音表記は正規化後5文字以上。`æ`等も許可。IPAは強勢・長音・括弧を除いて比較)。結果=`PRON_IN_CITED_PAGE`/`NAME_IN_CITED_PAGE`/`UNVERIFIED_AI_OUTPUT`/`NO_SOURCE`。**失敗は拒否ではなく`UNVERIFIED_AI_OUTPUT`として登録を継続**(現行の登録挙動を変えない)。
- **安全条件**(`is_safe_url`/`default_fetch`/`html_to_text`、test済み): GETのみ・http/httpsのみ・loopback/private/link-local/reserved宛を遮断(名前解決後の全アドレス検査、redirectは手動で最大3回、各hopで再検査)・応答512KB上限・timeout 5秒・Content-Typeがtext/html系のみ・取得物はメモリ上でscript/style除去のテキスト化のみ(保存・実行・外部resource読込なし)。専用dir保存は行わない(保存しないため。PLAN v2-7の「専用dir」は保存する場合の規則で、Stage 1は非該当)。
- **配線点**: 調査成功後のupsert直前(`:384`付近)。`er006_pronunciation_ledger_01.py:140-191`の`upsert`は固定キーdictを作り直すため、任意キー`evidence_tier`・`evidence_check`・`evidence`の**素通し3行を追加**する(既存キーの値・順序は不変、`entry_invalid_reason`も無改変)。**S1-09: 素通し3キーは「今回`upsert`に渡されたentryにそのキーがある場合だけ」書き、既存entryから引き継がない**(キーを渡さない呼出=既存の全呼出のLedger出力はバイト一致。E-2で「キー無し呼出のバイト一致test」を追加する)。
- **費用/遅延**: HTTP GETのみ(API課金0)。調査1回につき最大3 GET×5秒=最悪15秒。既存の調査自体が60秒timeout(`er006_pronunciation_research_01.py`)なので許容範囲。最終slot・HR到達時のみ発生。
- **実Webでの未検証事項**: 既存Ledger 31件の出典URLが実際に何%取得・照合できるかは**未測定**(今回はWeb取得禁止)。E-2のruntime evidenceで調査1回分のURLに対して1回だけ実測する(HTTP、課金0)。**論点E: 実調査1回・実URL取得は、Ledger/sidecarのpathを一時コピーへ差し替えて行い、架空語をProduction Ledgerへ登録しない**。
- **rollback/test**: 定数`citation_check`。er097 test 9件(script内文字列の除外・偽引用はQUOTE_VERIFIEDにならない・SSRF遮断・サイズ/URL数上限・例外非伝播)。

### 1-6. 効果測定(API 0)— §6
### 1-7. M1整合確認(複数発音候補)— §6-3

## 2. 統合関数と最小diff(E-2の配線設計。S1-02「既存testのmock隔離を壊さない」形)
`er097.resolve_span_for_review(span, ledger_loader, research_fn, upsert_fn, neg_store, now, fetch)`が副作用をすべて注入で受ける。
- **配線の原則**: 副作用(調査API・Ledger登録・sidecar書込・HTTP取得)は**すべて`_resolve_unresolved_entity_for_review`の内側からのみ**到達する。呼出側(`:1061-1076`)はこの関数の戻り値だけを使い、関数がmockされて`None`を返しても従来どおりstub(`confidence="unconfirmed"`)で動く(呼出側にsidecar・HTTP・Ledger書込を置かない)。
- **既存の関数名・シグネチャ・戻り値の形を維持**する。`_resolve_unresolved_entity_for_review(span)`の内部で、`PRON_SUPPLY_STAGE1_ENABLED`がTrueなら`er097.resolve_span_for_review(...)`を呼び、`info`を従来と同形で返す(追加の`extra`は、呼出側が`pronunciation_lookups[span]`に重ねるため関数外のmodule変数やcontextには出さず、戻り値のdictに**予約キー`_stage1_extra`**として載せ、呼出側が取り出して除去する。mockが返す従来形dictには`_stage1_extra`が無い=追加キー無しで従来どおり動く)。Falseなら`_legacy_resolve_unresolved_entity_for_review`(旧コードそのまま)。
- **ledger_loader/research_fn/upsert_fn**: `ledger_loader=pronun_ledger._load`、`research_fn=lambda s: pronun_research.research_pronunciations([{...従来と同じ引数...}])`、`upsert_fn`=従来の`upsert`+`lookup`、`transient_exceptions=(requests.exceptions.RequestException,)`(**現行どおりそれ以外の例外=cost logger未初期化等は握りつぶさない**)。
- **既存testのmock隔離が壊れないことの確認対象(E-2の最初の作業、配線前後で全PASS)**: `er006_secondary_asr_01_test.py:125,354,501`、`er006_secondary_asr_01_m1_wiring_test_01.py:119-184`、`er020_*`、`er026_*`、`er078_*`、`er096_*`、`er057_*`、`er006_pronunciation_ledger_invalid_entry_remediation_01_test.py:108-122`。これらは`_resolve_unresolved_entity_for_review`(または`research_pronunciations`/`lookup`/`upsert`)をmonkeypatchしている。配線後も(a)関数名とシグネチャ不変、(b)`research_pronunciations`等の呼出経路が従来と同じ位置から呼ばれる、(c)sidecar/HTTPがmockの外側で動かない(sidecar pathは既定でtmp/disabled扱いとせず、mockされた経路では到達しない)ことを、配線前に上記testを実行して基準線を取り、配線後に同一結果であることで確認する。
- **Ledger `upsert`の素通し3キー(S1-09)**: 「今回渡されたentryにある場合だけ」書き、既存entryから引き継がない。キー無し呼出のバイト一致testをE-2で追加。

## 3. 「合否判定基準・自動PASS条件を変えない」ことの保証
1. 判定関数(`val.evaluate_attempt`/統一judge/Case A/M1/L1/PNMH/B3/KP dual)のコード・入力を変更しない。`er097`は`er006_secondary_asr`・`er078_`・`er094_`・`er006_m1`・`er006_pronunciation_ledger`をimportしない(test済み)。
2. `pronunciation_lookups`の消費者はHR書込(`:419`)と記録専用の`er008_n8_revalidation_15.py:106`のみ(Grep: `*.py/*.html/*.js`)。
3. 呼出位置は最終slot・最終NG確定後(`:1061`、`result["verified"]/final_status`設定後)。調査の有無は判定の前に影響しない。
4. 入力データへの間接影響は Phrase List(§0-3)のみ。M1候補集合は replay で不変(§6-3)。
5. E-2で実施する差分検証: ① 同一mock入力で Stage 1 ON/OFF の`evaluate_attempt_with_cascade_detail`戻り値から`pronunciation_lookups`を除いた全キーが一致(既存`er006_secondary_asr_01_test.py`の最終slotケース群+`m1_wiring_test`を流用) ② 保存転写(PNMH 4,032ペア+544転写)で判定結果の差分0 ③ regression。**論点E(開示)**: 保存転写(PNMH 4,032ペア+544転写)での判定差分0は、**回帰確認(既存入力で判定が変わらない)に留まる**。Stage 1で新規に発火する経路(否定記録・別type採用・一般語省略)が自然発生した実データでの検証ではない。

## 4. Family X/Z共通経路への影響
- X/Zとも`er003_v1_n3_01_tts_generate.py:144`の`secondary_asr.evaluate_attempt_with_cascade_detail`を通る(X=`er019_family_x_audio_production_runner_01.py:49`、Z=`er063_family_z_audio_01.py:761,774`)。Family別分岐は作らない。将来のFamily Yも同関数を呼ぶ前提で自動適用。
- sidecar/Ledgerは共有。resume・regen・並列runでの影響は §1-1。
- **配線は`er006_secondary_asr_01.py`(D-2担当が編集中)と`er006_pronunciation_ledger_01.py`の素通し3行を伴うため、D-2のcommit後に着手する(E-2)**。この設計書の時点では編集しない。

## 5. 費用・QCD
- API費用: Stage 1実装による量産費は**下がる側のみ**(一般語の初回調査削減)。V1'のHTTP GETは課金0。
- 開発・検証費: runtime evidenceは「mock注入でのX/Z実関数発火(API 0)」+「最終slotの実調査1回(≈PNEP実測5.4円/語を上限として見積。現行最終slot調査の単価自体は未確認)」+「出典URL 1回分のGET(0円)」。**合計≈JPY10以内**(日次1,000円・個別300円の内側)。実調査を1回に限る理由=否定記録の実証はmockで足り、実調査は「registration時のV1'が実Webで動くこと」と「HR packageに追加キーが載ること」の確認だけが目的。
- Delivery: 並列化=E-2の配線はD-2完了待ち(同一ファイル競合)。それ以外(本設計・module・test・Stage 2 v3)は先行済み。

## 6. 効果測定(API 0、保存データ再集計。`stage1_effect_measure_01_result.txt`)
測定時点: HR queue 106行(実path79、調査対象語あり49)、Ledger 38件(sha256 `6bc3c45f…2f857`)。※並行agentがqueueへ追記するため行数は実行時点で変わる。
### 6-1. 調査呼出
- 調査対象になった語=18種(27ペア)。Stage 1適用判断(空Ledger=初回調査時点を再現): **`SKIP_GENERAL_WORD` 6種(33%)/`RESEARCH` 12種**。6種=`another voice`,`main story`,`mini`,`one voice`,`plus`,`us`。
- 現行Ledgerで再判定: `USE_LEDGER` 13/`SKIP_ISOLATED_ENTRY` 5=**RESEARCHになる語0**(全18語が既にLedger化済み=同一語の再調査は元々API 0。計画v2の「再調査2ペア」は訂正)。
- 保存調査ログ(全`raw_usage_log`のdedup): 調査呼出32件(成功32・失敗0・items空0・単一item24)。トークン合計24,120。**単価は未確認**(PNEP実測5.4円/語を代理にすると、6種×5.4=約32円/18種×5.4=約97円相当の33%)。
### 6-2. HR表示
- HR行(実path)のうち調査対象語あり49行中、一般語spanの行は10行(20%)。これらは現行では「情報なし/誤entry由来の情報」だったが、Stage 1後は「通常の英語語彙のため調査省略」と明示される。
- 否定記録・統一lookup・階層表示の実データ上の発火件数: 否定0(`items=[]`が保存ログに0件)、統一lookup新規命中0、階層表示=全HR行の`pronunciation_lookups`に付与(表示改善は全49行)。
### 6-3. M1整合・Phrase List(複数発音候補)
- 反事実Ledger(一般語のcascade entry6件を持たない)に対し、保存canonical文95種(HR queue+attempt_history+Ledger surface)で`freeze_candidates`の`candidate_set_hash`を比較: **差異0件**(OOV語の出現218)。理由=M1のC2はCMU未収録語のみ(`er006_m1_multi_candidate_01.py:276`)で、一般語規則はCMU収録を必須とするため。統一lookupは読取専用でM1に渡すsnapshotを変えない。
- 同replayでPhrase List(`get_hint_for_text(min_confidence="low")`)は95文中18文で差異、**全て`mini`のみ**(§0-3)。
- 複数発音候補(`alternate_pronunciations`)の扱い: 統一lookupはentryを丸ごと返すだけで、候補の統合・選択はしない。M1の候補生成(IPA→ARPAbet、C2)・L1・Case Aは無改変。

## 7. test計画と結果
- 実施済み(API 0): `er097_pronunciation_supply_stage1_01_test_01.py` **56 test PASS**(42+Opus反映14。否定記録・統一lookup[melos/muse再現含む]・一般語・V1'[mock fetch]・default_fetch[mock http_get]・resolver[全副作用注入]・判定語を返さない)。
- E-2で追加: 配線test(`er006_secondary_asr_01`の最終slot経路でON/OFF差分0、旧経路バイト一致)、`er006_pronunciation_ledger_01_test`への素通しキーtest、X/Z実関数発火(mock research)、regression(`run_project_regression.py`)。

## 8. 残リスクとレビュー論点
1. **Phrase Listの間接影響**(§0-3): 将来の一般語がPhrase Listに載らない。許容か、一般語でもentryは作る(調査は省く)別案が要るか。
2. **一般語閾値zipf>=4.0**の妥当性(誤除外=CMU収録の頻出ブランド/人名)。判定不変・HR情報欠落のみの影響。
3. **sidecar採用**の妥当性(Ledger任意キーでなく別file)。
4. **V1'の弱い確認**(名称+発音表記の実在。quoteなし)をStage 1の「引用実在確認」と呼んでよいか。quote付きはStage 2のresearch形式で導入。
5. **自然発生は未観測(残事項、論点E)**: 否定記録・別type採用の実発火は保存データで0件。4,032ペアの判定差分0は回帰確認のみで、これらの経路の自然発生検証ではない。実調査1回と実URL取得は一時コピーpathで行う(架空語をProduction Ledgerへ登録しない)。
6. **Production実走証拠の不足の扱い**: 否定記録は実APIで`items=[]`を再現できず(保存ログ0件)、mock注入でのみ実関数発火を確認できる。実走で自然発生するまで「Production実走証拠は部分的」と残事項に明記する。

---
Fable判定(2026-10-22): Stage 1=`PRODUCTION_WIRED`(条件付き残事項あり)。根拠=X/Z共通の`evaluate_attempt_with_cascade_detail`内に配線、判定基準・自動PASS条件は不変(ON/OFFで実関数の判定出力一致、保存HR 79行の再判定差分0、4,032ペアはバイト一致、Ledger upsertキー無し呼出は配線前版とバイト一致)。実関数での発火=X(crosslevel)・Z(er063 kp_en)でmock注入により最終slot NG→調査→出典ページ照合→Ledger登録/USE_LEDGER/否定記録/SKIP_NEGATIVE_CACHEの各分岐を記録。実機で一般語(`good morning`/`main story`)の調査不呼出とLedger命中時の調査0を確認。出典ページ照合は保存済み調査結果3語の実HTTP取得で動作確認。`mini`隔離(OPEN-436の枠)はPhrase List差分18文(mini由来のみ)・M1候補集合差0・判定差分0。**残事項(完了と誤認しない)**: (1)実調査API(Perplexity)の端から端の確認は枠切れ(401、UDR #134未回答)のため未実施。枠復旧後に1語で確認する。(2)否定記録・別type採用の自然発生は未観測(過去データで発火0)。(3)「引用実在確認」はStage 1では弱い照合(出典ページに名称・発音表記の出現確認)のみ。本来の引用確認はStage 2の調査形式変更(Prompt変更=別承認)と同時。費用JPY0。
---
