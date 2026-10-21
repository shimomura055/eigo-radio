# INVESTIGATION_01: 固有名詞の正しい発音情報の取得・登録・再利用 現状調査と定量化(費用0)

管理ID: PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_01(B-1) / 作成日: 2026-10-22 / Status管理ラベル: `PLAN_DRAFT_PENDING_FABLE_REVIEW`(計画のみ・API 0・JPY0・Trial未実行・Production/Ledger/Validator/Prompt無変更)。
ユーザー原文(2026-10-22 §3 B・§5 B)の出典=`docs/pm/delegation_log/2026-10-22_PNMH-PRODUCTION-WIRING-AND-PRONUNCIATION-SUPPLY-PLAN-02_USER.md`(保存はA側)。委任文=`docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_委任_01.md`。
位置づけ: 目的は「固有名詞の正しい発音情報を、必要なときだけ取得・登録・再利用する仕組み」の計画。前回計画(`docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/`)で「判定層(L1: 1語と複数語の同音判定)」は採用済み。本計画は「供給層(L2: 比較の基準になる正しい発音情報をどう持つか)」の具体化。改善対象から外さないというユーザー意図(原文§3 B 背景)に従う。

## 1. 結論(調査の要点)
1. 「発音情報が不足している」状況は実在するが少数派: 保存された英語原稿1,889種から取り出した固有名詞らしい語703種のうち、辞書(CMU)収録が642(91.3%)、辞書外が61(8.7%)。辞書外61のうち既にLedgerに登録があるのは13(21.3%)(`quant_tokens_01_result.txt`)。
2. 最終判定まで残り、人間確認(Human Review)へ到達した発音lookup(実path)は延べ55件・18語。辞書外7語が36件(melos 11、khaite 10、toteme 7、altuzarra 3、meink 2、canele 2、zabelina 1)で最多(`quant_hr_queue_01_result.txt`)。残り19件は辞書収録語で、`main story`・`another voice`・`one voice`・`plus`・`us`・`mini`等の一般語の誤トリガーを含む。
3. 現行Ledger 38件のうち、根拠の引用文(quote)を持つものは0件、全件が「AIの調査出力+検索結果URL一覧」で、`human_approved`欄も0件。新方式の基準では、既存entryは1件もPASS根拠階層へ自動昇格できない(安全側)。
4. 既存機構にはすでに「Ledger lookup→なければ1回だけ調査→登録して記事横断で再利用」(`er006_secondary_asr_01.py:341-387`)がある。足りないのは(a)調査結果の信頼度の区別(引用確認・出典種別)、(b)「見つからなかった」事実の記録(negative cache)と一時失敗の区別、(c)人間確認結果の語単位での再利用、(d)辞書に同綴りがあっても同一物か判定できない問題(byUs型)の扱い、の4点。ゼロから作る必要はない。

## 2. 「発音情報が不足している」実事例の分類
| 事例 | 何が起きたか | 現行でどう解決/未解決か | 発音情報の不足の種類 |
|---|---|---|---|
| ブランド名`byUs`(漫画AIチャット記事) | ASRが`Bias`/`Buy Us`/`by us`と書く。CMU辞書は`byus`を姓として収録(`B AY1 AH0 S`)=`bias`と同音 | `Bias`は1語対1語の同音で救済済み。`buy us`はL1(多語同音救済、採用済み)で救済。ただしブランドの公式な英語発音は確認されていない(公式英語情報源に発音記載なし、日本語公式の読み「バイアス」のみ。PNEP K1=安全終了) | 辞書に同綴りの別物がある(同綴り衝突)/公式英語発音が存在しない |
| 人名`Kristie Tse` | `Tse`の発音が複数あり、ASRが`Sea`等と書く | 研究結果は複数候補(tsee/tsay/see系)。ユーザーが実音声を試聴し「seeに近い許容発音」と判断しHuman Approved(CURRENT_SPEC.md:1837)。承認は区間(segment)単位で、語単位のLedgerには残らない(`er003_v1_n3_01_assemble.py:96-113`は`canonical_text`のsha256のみ保存) | 許容発音が複数/人間承認が再利用できない |
| 人名`Stephen Reicher` | Ledgerのconfidence=highの唯一の根拠がテキスト書き起こしだった | 恒久対策として「highは本人の音声源のみ」を研究Promptに追加(`er006_pronunciation_research_01.py:72-80`、CURRENT_SPEC.md:1837) | 根拠が音声でなくテキスト |
| `Melos`(Family Zの主題。ASR誤認識`Mullos`/`Mellows`等) | 辞書外。ASR側が別の語に書く | 登録読み辞書(A7)・Phrase List重み2.0・M1(Ledger IPA)で救済。`melos`は`ja_reading_katakana`(JAのみ)と`cascade_unresolved_entity`(low、汚染hint)が同じ綴りで2件併存(`quant_ledger_01_result.txt`) | 辞書外/英語読みの根拠がない/Ledger重複 |
| `iCapital`/`Bisnow`(記事: assigned desks) | Primaryが`Bisnow`を`BizNow`と書く、`iCapital`は辞書外でLedger未登録 | Human Review queueに到達(`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`)。`Bisnow`の公式発音は未確認 | 辞書外・Ledger未登録 |
| `FamilyMart` | 辞書外だが`Family Mart`/`FamilyMart`の空白差のみ | Ledger登録済み(cascade、medium)。空白差は`_is_compound_spacing_only_span`(story-making是正、PRODUCTION_WIRED)が吸収するため発音情報なしで解決 | 不足ではない(既存の空白差規則で解決) |
| `LINE`/`Lion`(記事B) | 公式発音は一般語`line`と同じ`/laɪn/`だが、実音声が`Lion`寄りだった可能性(独立2エンジン) | PNEP K5: 要試聴。CMU層で期待発音は足りる(登録不要が妥当) | 期待発音は足りている(音声側の問題) |
| `Framton Nuttel`/`Sappleton`(Open Window) | 公式発音は音声(Forvo等)のみ、テキストで検証不能 | PNEP: `UNCONFIRMED`で登録せず | 音声源のみ(自動確認不能) |
| `Vera` | 辞書にある一般的な人名 | PNEP: Oxford Learner's `/ˈvɪərə/ /ˈvɪrə/`を引用確認し1件登録(medium) | 成功例(テキスト辞書源) |

## 3. 定量化(保存データ・費用0。再現スクリプトは同dirの`quant_*_01.py`)
前提・限界: 「記事」を独立に数える手段が無いため、(i)英語原稿の種類数、(ii)パス3階層で束ねた記事群(概算。Trial再実行・合成ケースを含む上限寄り)、(iii)Human Review queueの実行path行、のいずれかで示す。固有名詞らしい語の抽出は大文字始まり(文頭除く)・CamelCase・全大文字の簡易規則で、ハイフン複合は除外(取りこぼし・誤抽出あり)。

### 3-1. 固有名詞らしい語の辞書カバー(`quant_tokens_01.py`)
| 指標 | 値 |
|---|---|
| 英語canonical(原稿)の種類数(`pairs_02.jsonl`由来) | 1,889 |
| 固有名詞らしい語の異なり数 | 703 |
| 辞書(CMU)収録 | 642(91.3%) |
| 辞書外(OOV) | 61(8.7%)。2箇所以上の記事群に出現30、1箇所のみ31 |
| 辞書外のうちLedger登録あり | 13(21.3%): triangeln, mta, boavida, meink, familymart, canele, khaite, altuzarra, toteme, melos, zabelina, oimo, ottoni |
| 辞書収録語でLedger登録あり | 10 |

辞書で既に扱える割合が高く、「全固有名詞を事前に調べる」ことの無駄が大きいことを裏づける(ユーザー方針と一致)。

### 3-2. 実際に不一致(content diff)まで至った辞書外語(`quant_mismatch_topics_01.py`。既存`demand_oov_result_01.json`の再実行と拡張)
- 保存転写4,032ペアのうち、非PASSの内容差で期待側が辞書外の語: 異なり41語(合成の乱数造語8語を除く実名・実語33語)。
- そのうちLedger登録済み(利用可能なIPAあり): 12/33(36%)(triangeln, boavida, ottoni, malmo, meink, khaite, altuzarra, toteme, melos, zabelina, canele, oimo)。未登録21語: teruaki, elehuris, seishiro, torai, rbi, mayu, akb48, sukisshu, kokoro, anhui, mimoun, ruller, neukolln, kuratko, hbtss, minaudiere, viii, bisnow, counterspace, miu ほか合成語。
- 記事群(パス3階層で束ねた84群、概算): 辞書外の内容差が一度でも出た群19(23%)、固有名詞らしい内容差が一度でも出た群34(40%)。再試行で後に解消した試行も含む上限値であり、最終的に人間確認へ残った割合ではない。
- 最頻の辞書外語(記事群数): melos 5、toteme 4、triangeln/ottoni/mimoun/meink/khaite/minaudiere/altuzarra 各3。

### 3-3. Human Review queueの内訳(`quant_hr_queue_01.py`、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`)
- 総行数105(実pathの行79、`Temp`配下のテスト行26)。最終ステータス: `ASR_VALIDATION_UNCERTAIN` 91、`TRUE_CONTENT_MISMATCH` 14。実pathの異なり原稿56。
- 実pathの行が属する記事群21、うち発音lookupを伴うのは17群・49行(延べ55語件)。語の内訳は§1-2のとおり。
- 全行(lookupを伴う66行)のうち、全lookupが`low`または`unconfirmed`の行が45。lookup件数の信頼度内訳: low 34・medium 20・unconfirmed 17・high 1(合計72)。
- 発見: 辞書収録の一般語が誤ってentity-like扱いされHRの発音lookupに入っている(`main story`・`another voice`・`one voice`・`plus`・`us`・`mini`)。これらは既に`ledger_disabled`/`tts_injection_disabled`で隔離済み(OPEN-436)。新方式のトリガーは「辞書外または同綴り衝突」に絞るため、この誤トリガー経路を設計上避けられる。

### 3-4. 現行Pronunciation Ledgerの棚卸し(`quant_ledger_01.py`)
- 38件。entity_type: cascade_unresolved_entity 21、ja_reading_katakana 7、person 4、place 3、organization 1、product 1、abbreviation 1。
- 英語IPAあり31、`ja_reading_katakana`(IPAなし)7。confidence: high 12(ja_reading 7を含む)、medium 12、low 14。
- `ledger_disabled`(隔離)5、`tts_injection_disabled` 6、quote欄0、human_approved欄0。`sources`がちょうど15件の検索結果URL一覧のentryが29件(Perplexityの`citations`をそのまま保存、どのURLがどの主張の根拠かは不明)。
- 同綴りが別entity_typeで重複: `melos`、`muse`(ledger_idが(surface, entity_type, source_context)のhashのため別entry扱い)。
- 新方式の階層(PLAN_01.md §2)に当てはめると、既存entryでPASS根拠階層に該当するものは0件(quote未確認)。HRパッケージ用途の階層には全件が入る。

## 4. 既存機構の調査と再利用可否(ファイル:行は2026-10-22 HEAD)
| 機構 | 場所 | 現状 | 再利用判断 |
|---|---|---|---|
| CMU辞書の発音取得 | `er008_asr_variant_hardening_15_homophone_en.py:49-100`(`_phone_variants`、`homophone_arpabet_equivalent`) | 辞書にあれば全variant、無ければNone(判定不能) | そのまま再利用。辞書外のとき供給層が音素列を渡す口を作る(PLAN_01.md §6) |
| Case A(固有名詞の自動PASS) | `er006_secondary_asr_01.py:331,592-595`(`PROPER_NOUN_ENTITY_ARPABET_CONFIRMED`) | canonical・ASR候補とも辞書収録かつ代表発音一致のみPASS。調査費0 | 無改変。「辞書で確実に解決できるなら調べない」を担う |
| Case B/反応的調査 | `er006_secondary_asr_01.py:341-387`(`_resolve_unresolved_entity_for_review`)、`:1056-1070`(最終slot・entity-like不一致時) | Ledger lookup→なければPerplexity 1回→`cascade_unresolved_entity`で登録。HRパッケージ用途のみ(CURRENT_SPEC.md:1837)。失敗は`unconfirmed`としてHRへ | 骨格を再利用(新規の調査機構を作らない)。階層・negative cache・引用確認を足す |
| 調査Prompt/基準 | `er006_pronunciation_research_01.py:72-80`(confidence=highは本人音声のみ、他はmedium以下)、`:92-`(`research_pronunciations`) | Perplexity sonar、JSONスキーマにquote欄なし | 基準は維持。調査手段はPerplexity枠切れ(UDR #134未回答)のためバックエンド非依存で設計 |
| Ledger本体・登録時validator | `er006_pronunciation_ledger_01.py:20,77-98,140-191,237-283`(`entry_invalid_reason`、`upsert`、`get_hint_for_text`) | OPEN-436でplaceholder/汚染canonicalを隔離 | 再利用。階層は既存フィールドと任意の追加キーで表現(スキーマ破壊なし) |
| M1(複数発音候補) | `er006_m1_multi_candidate_01.py:76-103,208-250,251-`(`IPA_TABLE`、`ipa_to_arpa`、`_c2_candidates`、`freeze_candidates`) | Ledger IPAを決定論でARPAbet化(ストレス除去、未知記号はNone=候補不成立)。凍結はsegment最初の試行前に1回(OF-179)。除外: ja_reading、ledger_disabled、canonical≠surface、sources空、segment開始以降の更新 | IPA→音素列変換はM1の既存変換器をそのまま使う(新しい近似を作らない)。発見: M1はconfidenceで絞らない(low entryも候補、`m1:235`)。受理自体はF1内側・Pattern A/B/C限定でPASS_WITH_WARNING |
| L1(多語同音救済) | `er094_multiword_homophone_01.py:38-66,101-120`(A側が実装した未配線module。純関数`multiword_span_equivalent_v3`) | 辞書外は`OOV_or_too_many_variants`で判定不能 | 供給層の出口。辞書外語に階層を満たす音素列があるときだけ判定可能にする(PLAN_01.md §6-2) |
| Azure Phrase List | `er006_secondary_asr_01.py:75-111`(重み2.0) | LedgerのsurfaceをSecondaryへ供給 | 無改変。PLはASRの認識を寄せるだけで発音の根拠ではない(PNEP K5でLion→LINEの隠蔽例)ため、階層は参照のみ |
| 登録読み保護(A7) | CURRENT_SPEC.md:2817,2820 | JAのSecondary事前除外 | 無関係(JA側) |
| Human Review表示ルール | CURRENT_SPEC.md:1837 (a)〜(f) | 表記・IPA・guide・根拠・confidenceを必ず表示 | 維持・拡張(階層名と出典種別を追加表示) |
| 人間承認の記録 | `er003_v1_n3_01_assemble.py:96-113`(`record_human_approval`)、`er011_human_review_lock_01.py:179` | 区間(segment)+canonical_text sha256単位。語単位では残らない | 語単位の再利用が無いことが不足点(PLAN_01.md §5) |
| PNEP Trial資産 | `er089_proper_noun_en_pronunciation_trial_01_lib.py`(`verify_quote_in_source`:823、`en_pron_info_qualifies`:410)、結果`docs/research/FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01/TRIAL_RESULT_01.md` | 引用確認(V1')・形式(V3)・競合(V5)・隔離。Trial専用、Production無配線 | 検証ロジックとして再利用(Trial段階) |
| 手動同音グループ | `er008_asr_variant_hardening_15_homophone_en.py`の`_HOMOPHONE_OVERRIDE_GROUPS`(空) | 個別whitelist(主方式にしない方針) | 使わない |

## 5. 承認済み原則・制約(本計画の前提。矛盾するものは採らない)
- ASR consensusは発音検証ではない(CURRENT_SPEC.md:1837)。M1は「ASR転写からの後付け候補・綴りからの推定は自動PASSの根拠にしない」(`er006_secondary_asr_01.py:344-356` docstring、CURRENT_SPEC.md「M1」節)。よってASR転写から音素列を逆算して基準にする案(P4)は不採用。
- 発音の許容基準: 本人→公式プロフィール等→信頼できる情報源の一般的な英語圏発音→許容発音集合(ER-008-N8-…-16、CURRENT_SPEC.md:1837)。完全な単一正解は要求しない。
- 自動PASSの近似禁止の範囲: IPA→ARPAbetの近似で自動PASSしない(1837)。ただし2026-10-13ユーザー承認のM1は、決定論変換+F1内側の厳しい受理条件に限りLedger IPAを候補に使うことを認めている。本計画は同じ変換器・同じ厳しさの範囲に留める。
- 本人音声が確認できたときのみconfidence=high(`er006_pronunciation_research_01.py:72-80`)。テキストのみはmedium以下。
- Human Reviewは最後の手段(PM_GOVERNANCE 14節)。AI推測のみで発音を確定しない(ユーザー原文§3 B)。
- 未回答のまま残る事項(Statusを変えない): UDR #133(固有名詞英語発音供給の扱い、OPEN-434)、#134(Perplexity利用枠切れ)、J7(権利者公式日本語読み「バイアス」を英語期待発音の根拠にしてよいか)。本計画は未回答のまま分岐として扱う。

## 6. 調査で見つかった既存の不足点(是正は本計画の対象外。報告のみ)
1. 「見つからなかった」の記録(negative cache)が無い: 調査が空/失敗のとき`None`を返し何も保存しない(`er006_secondary_asr_01.py:361-372,381`)ため、次の記事でも同じ語を再調査する。
2. 一時失敗(ネットワーク/枠切れ)と「情報なし」の区別が無い。
3. M1がconfidence/出典種別を見ない(§4)。lowのAI出力も候補になる(受理自体はF1内側の厳しい条件)。
4. 人間確認の結果が語単位で残らない(§4)。
5. 同綴りがentity_type違いで重複(melos、muse)。lookupはledger_id一致(`er006_pronunciation_ledger_01.py:133`)のため、`cascade_unresolved_entity`と`person`等を取りこぼし得る。
6. 調査結果のURL一覧は主張との対応が無く、検証されていない(§3-4)。
