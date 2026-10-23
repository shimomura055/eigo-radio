# DESIGN_PROPOSAL_02: Family Y(Voices型)基本設計案(Opusレビュー是正反映版。DESIGN_PROPOSAL_01は履歴として残置)

管理ID: FAMILY-Y-VOICES-DESIGN-01 委任_03(委任_02の01を改訂) / 2026-10-23(JST) / **DESIGN/RESEARCH ONLY**(Trial・API費用・Production/Prompt/コード変更なし)
Status: `DESIGN_REVISED_PENDING_USER_DECISION`(Opusレビュー`OPUS_REVIEW_01.md`のM1〜M7・S1〜S13を反映済み。条件付きGO)。本書は**設計案**であり、仕様採用・`APPROVED_FOR_PRODUCTION`・`PRODUCTION_WIRED`の記録ではない。
ユーザー指示原文: `docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER.md`(以下「原文」)。入力: `INVENTORY_X_Z_SPEC_01.md`(以下01A)、`INVENTORY_OLD_B_VOICES_01.md`(以下01B)。
再照合した一次情報(今回Grep/Readで確認): `CURRENT_SPEC.md:1185-1192`(RF)・`:1692`(後述の古い記述)、`OPEN_ITEMS.md` OPEN-167/217/218/219/415/461/462、`er019_family_x_audio_production_runner_01.py:80,180,488,537,995-1002,1401-1408,1590,1724,1889,1994`、`er020_tts_retry_local_rewrite_01.py:125-150`、`er005_output/cost_baseline_01/pricing_snapshot.json`。今回(委任_03)に追加で再読したもの: `er003_v1_n3_01_tts_generate.py:115-118,194-242,395-404`、`er003_v1_n3_01_assemble.py:239-300,490`、`er020_tts_retry_local_rewrite_01.py:105-154`、`er053_family_x_factlock_ja_writer_01.py:401-426`、`er019_family_x_audio_production_runner_01.py:665-694`。それ以外の出典は01A/01Bが記載した`file:行`を引き継いでいる(再読していない行は「01A/01B引用」と読むこと)。

## 改訂要点: Opusレビュー(OPUS_REVIEW_01.md)の反映(M1〜M7・S1〜S13対応表)

Opusは条件付きGO(骨格は妥当、設計確定前の是正6件+)。**Fable照合の結果、全項目が設計書の記述で解決でき、設計内**。下表の「反映先」は本書内の節。台帳=`docs/pm/OPUS_FINDINGS_LEDGER.md` OF-FYD-M01〜M07/S01〜S13(Status=`DESIGNED`)。

| ID | 要点 | 本書での反映 | 反映先 |
|---|---|---|---|
| M1 | 人物スコープ/世界スコープの分離、Voice段落は数字を使わない | Y版R0/Card生成Promptに(a)個人スコープ(出典=Voice Cardのみ・タグ不要・実在の人名/組織名/製品名/出来事は不可)と(b)世界スコープ(出典=台帳のみ・Fact Lock規則1〜5・Voice段落ごと最大1件)を明記。Cardの世界スコープ記述は背景fact id参照のみ。Leakage Gateは「事実判定ではなく編集構造の判定、Voices限定の承認済み例外」と明記。Xの文言は変更しない | §③-3、§③-6(新)、§⑥開示 |
| M2 | 段落と話者の対応契約(T4訂正) | 既存の忠実英訳/A2簡易化関数に段落数引数がないことを訂正。日本語・Adv・Stdそれぞれで「本文ちょうど5段落+Title+In One Line」をY側で決定論確認(違反は1回再生成→STOP)、話者取り違え防止の決定論確認。代替=5要素JSON wrapper | §③-4 T4、§③-3 |
| M3 | segment_id検査の網羅(T8訂正) | 直書き一覧の全洗い出し表、parity test、X/Z出力byte一致回帰 | §③-4 T8、§③-5(新) |
| M4 | 同一run内再利用判定にTTS Voice名 | Y runnerの`_generate_or_reuse`相当の照合keyにvoice名を追加(X関数は無変更。Y用に包む) | §③-4 T9 |
| M5 | 局所書き換え仕様の明文化 | (a)〜(e)を明文化、「旧B方式へ戻せる」記述を削除(C11と矛盾) | §② B14注、§③-3、§④(6) |
| M6 | R0最終稿に`postprocess_ja`と最終記号QA | `er053:401-426`でR1/R2のみに掛かる点を明記し、Yは最終稿に適用 | §③-3 |
| M7 | 日本語Leakage事前校正 | Trial段階(0)として追加(旧B正解ラベル付き記事を日本語化、数円〜20円) | §⑦ |
| S1 | Card 6〜7項目、`not_my_point`は決定論生成、B3統合はTrial後 | 反映 | §② B01/B11、§③-3 |
| S2 | A2簡易化2通り比較(+0.5円) | Trialに追加 | §⑦ |
| S3 | Std英語に監視専用Leakage 1回(+2〜4円) | Trialに追加(記録専用) | §⑦ |
| S4 | 追加費用0の決定論モニタ(記録専用) | Trial評価項目に追加。Gate化は判断事項(D) | §③-6、§⑦ |
| S5 | Voice段落RF flag件数記録 | 反映 | §② A09、§⑦ |
| S6 | Local Rewrite時の一人称保持確認 | T8・A25に追加 | §② A25、§③-4 T8 |
| S7 | 最終パートの締めは2〜3型、定型化禁止 | D1推奨を改訂 | §⑥ D1 |
| S8 | Trialテキスト段階2テーマ・音声1テーマ、期待損失、書き換え確率の修正、R0+R1比較枠(任意+8円) | 費用表・Trial計画を改訂 | §⑤、§⑦ |
| S9 | 人物Voiceの聞き分けとPD06語り手化の評価 | D3とTrial評価項目に追加 | §⑥ D3、§⑦ |
| S10 | リードで「取材した」表現を回避 | R0 Prompt規則に追加(旧B先例あり、判断事項にしない) | §③-1、§③-3 |
| S11 | C06は「必須化しない・禁止しない」 | C06を改訂 | §② C06 |
| S12 | A16にKP日本語意味の人称一般化moduleの自動継承を明記 | A16に追記 | §② A16 |
| S13 | Y版R0に日本語の話し言葉・常体の指示 | R0 Prompt規則に追加 | §② A10、§③-3 |

**Fable判断(委任_03で確定)**: (i)D2(Voice Card作成方式)はユーザー判断から外し**開示事項**へ(人手作成は「安定量産」と両立せず実質的選択肢でない。Trial・試聴で問題が出たときだけ再判断)。(ii)M1は設計内+開示(Xの文言は変更しない。Y版R0の新規Promptでのみ規定。旧B承認済み「体験claim根拠付け」「候補C」の範囲内)。(iii)ユーザー判断は**D1/D3/D4の3件+最小Trialの実施承認**。

## 0. 用語(初出の短い説明)

| 用語 | 意味 |
|---|---|
| Fact Ledger(事実台帳) | Researchで集めた事実を検証済みかどうか付きで一覧にしたもの。Writerはここにない事実を書けない |
| B3 | 台帳から「記事の中心ストーリー1つ」と「必要最小限の事実」を選ぶ工程(AI 1回) |
| Fact Lock | Writerに課す「台帳にない事実を書かない」規則群 |
| Voice Card(人物設計カード) | 3人の人物それぞれの状況・懸念・守りたいものを書いた設計メモ。旧Bでは人手で作成 |
| Leakage Check | 各Voiceが「調査報告の説明者」に戻っていないかをAIが項目別にPASS/FAIL判定する検査(旧B承認済み) |
| Acceptance Gate | 検査に通らない記事を後続(音声化)へ流さず止める仕組み(旧B承認済み) |
| RF(Risk Flagger) | 完成英文を台帳と突き合わせ、怪しい文を人の確認待ちリストへ入れる**非停止**の検査(X承認済み) |
| KP | Key Phrase(重要フレーズ) |
| TTS / ASR | 音声合成 / 音声認識(生成した音声を聞き取り直して検査) |
| HR Lock | 音声検査が通らない時に人手確認待ちで停止する安全装置 |
| segment_id | 音声1パーツの内部名(例 `full_story_part2`)。検査の対象範囲がこの名前で決まるため、新構造では対応が必要 |
| DEV実装 | 本番(Production)と分けた検証用経路での実装。承認前の新機能はここにだけ置く |

## ① 結論

**Family Yの基本設計は成立する見込みが高い**(Opusレビュー: 条件付きGO、骨格はSonnet設計と一致)。設計の大半はXの承認済み経路をそのまま使え、Yに固有の新規設計は「5パート構造・Voice Card・Voice用検査の移植・最終パート」に限られる。

- 継承の内訳は§② (A=X/Z承認済み共通仕様の継承、B=旧B承認済みVoices固有の継承設計、C=不継承、D=ユーザー判断)。**ユーザー判断が必要なのは3件(D1/D3/D4)+最小Trialの実施承認**(§⑥、目標6件以内)。D2(Voice Card作成方式)は開示事項へ移した。
- **新しい検査(Validator)は追加しない**。Voice用検査は旧Bで承認済みのLeakage Check(日本語原稿に対して1回判定)とAcceptance Gateの移植のみ。S4の決定論モニタ・S3の監視専用Leakageは**記録専用でGateにしない**。
- 費用は「Xの実測±約6〜8円/セット」と推定(§⑤。推定であり実測ではない)。
- **重要な未解決事項**(設計では解消できず、Trialで実測する):
  1. 日本語先行の三段(日本語→忠実英訳→A2簡易化)で人物らしさ(口調・迷い)が平板化しないか。
  2. Leakage Checkは旧Bで英語原稿向けに校正された。日本語原稿は未校正 → **Trial段階(0)で事前校正(M7)**。
  3. Voice Card自動生成の品質(旧Bは人手作成)。
  4. 一人称の体験談の中の事実創作を止める機械検出層がX経路にない(RFは事後・非停止)。M1のスコープ分離+RFで開始し、発生率をTrialで実測する。
  5. Xの音声Runnerは「本文3パート」前提の固定が複数箇所ある(§③-5)。Yは別の薄い入口を新設し、parity testで検査範囲の同等性を保証する。
  6. Z会話速度Trial(OPEN-462)の結果が出れば、Std 6%減速の扱いはそれに追従する。
  7. 局所書き換え(旧B承認済みGateの内部方式変更)は未実証。旧B実績では1回で通過したのはPN A2新版のみで、2回=Trial-02、非収束=Trial-01・3V汎用化Regression(Opus所見)。
- 調査で見つけた訂正1件(委任_02): `CURRENT_SPEC.md:1692`の「M2P0+A方式=PRODUCTION_WIRED」の古い記述は、KPFT(OPEN-454)で撤去済みの事実に合わせ「(撤去済み、OPEN-454参照)」と注記する最小修正のみ(委任_02で実施済み)。
- 副次調査(委任_03、読取のみ・X側の別item): X Std part3の6%減速は**実際には適用されている**が、減速未適用を検知するAudio Validation Gateのガードが`full_story_part3`を対象外にしている(§③-5、OPEN-466)。Y範囲外で修正しない。

## ② 仕様継承マトリクス(A/B/C/D)

凡例: 出典=01A/01Bの節または`file:行`(上記「再照合」以外は引用)。Status=その仕様の現在の公式状態。**「確定(U)」は分類ではなく、ユーザー決定済みの基本方針**(再承認不要)。

### 確定(原文§2)=ユーザー決定済み基本方針(分類対象外・8件)
| ID | 内容 | 出典 |
|---|---|---|
| U1 | 本文5パート固定(リード/Voice1/Voice2/Voice3/Tension+Closing) | 原文§2.1 |
| U2 | 3 Voices固定(2V/4V・可変構造の実装不要)。賛否中立に限らず、経験・価値観・利害・優先順位の異なる3視点 | 原文§2.2 |
| U3 | 独立Closing廃止、最終パートにTensionと統合 | 原文§2.1,2.4 |
| U4 | Voice編集思想「Research is backstage. People are on stage.」+一人称・立場の独自性・迷いは許容・他Voiceの中心論点は抱え込まない・検証可能な数値/制度/他者の具体的行動/出来事を創作しない | 原文§2.3 |
| U5 | Preview/Comment/KP/In One LineなどはXの最新承認仕様が基盤 | 原文§2.1 |
| U6 | Tension=「共通前提→分岐点→非対称性」の継承、各Voiceの再要約・論点反復・冗長な追加を避ける | 原文§2.4 |
| U7 | AUW(音声自動判定)はYの開発時に正式配線 | CS:2822節、01A §5 |
| U8 | Yは旧Bの経路を改修・転用せず、X基盤に新設。Production採用・配線は今回行わない | 原文§1,§9 |

### A: Family X/Zの承認済み共通仕様 → 継承(開示付き)
| ID | 項目 | Status | 出典 | Y適用時の注意 |
|---|---|---|---|---|
| A01 | Research(gpt-6-luna+web検索) | PRODUCTION_WIRED(X) | 01A §1 | 3視点の材料も同じResearchで集める。Voice別の追加Researchは設けない |
| A02 | Fact Ledger検証(VERIFIED/AMBIGUOUS/REJECTED) | PRODUCTION_WIRED | 01A §1 | 旧B系の`[VOICE_n_EVIDENCE]`台帳形式は使わない(OPEN-219の非互換を避ける) |
| A03 | B3(Storyline+Fact選定)の枠組み、gpt-6.1-sol | PRODUCTION_WIRED | 01A §1 | **選定単位の調整は設計で吸収**: Y用B3プロンプト(新規・別ファイル、X版は無変更)に「3視点の候補+Voiceごとの背景fact割当」を出力に追加(呼出回数は増えない)。Y Trial-01で割当fact重複0を確認済み(OPEN-217記録) |
| A04 | B3採用Fact下限2件(未満は再評価1回→STOP)、契約V1〜V10のfail-closed | APPROVED_FOR_PRODUCTION、PRODUCTION_WIRED判定はFable側 | 01A §1 | 下限2はリード/最終パート用。Voice背景factは別枠で各0〜1件 |
| A05 | 決定論B3 producer(【中核数値】【周辺数値】) | PRODUCTION_WIRED | 01A §1 | Voiceは外部統計を語らない(B10)ため、【中核数値】はリード/最終パートだけで使用可と運用 |
| A06 | 中核数値の丸め判断(Luna 1回/記事) | PRODUCTION_WIRED(承認原文=Xのみ) | 01A §1,§11-8 | 承認原文がXのみなのは当時Xが唯一のニュース系だったため。Voicesの性質と衝突しないのでA継承(開示)。Zは到達しない |
| A07 | Writer Fact Lock規則1〜5(R0) | PRODUCTION_WIRED | 01A §1 | 規則2「主観文は番号不要、新事実断定禁止」をVoice本文の運用基盤にする(§④ F5、§6(5)) |
| A08 | Concreteness Control AN3-T0 | PRODUCTION_WIRED | 01A §1 | 「Fact is context, not script」と方向一致 |
| A09 | Risk Flagger(両Level、非停止) | PRODUCTION_WIRED(X) | `CURRENT_SPEC.md:1185-1192` | 承認原文はX。Zは対象外だがYは事実を扱うためXに近い→A継承(開示)。Voice体験談の創作事実の**事後**検知を担う。Voice個人内容は台帳に無いためflagが量産される可能性があり、**Voice段落のflag件数を記録**(S5、Trialで測定) |
| A10 | Writerの言語三段(日本語原稿→忠実英訳→A2簡易化) | PRODUCTION_WIRED | 01A §2 | 人物性の平板化リスクは未検証(§①-1)。Trialで確認。**Y版R0は日本語の話し言葉・常体で書かせる**(です・ます調のまま英訳され平板化するのを防ぐ、S13) |
| A11 | Advanced忠実英訳(段落数・順序一致、追加削除なし) | PRODUCTION_WIRED | 01A §2 | 既存関数`generate_family_x_faithful_translation`(`er003_v1_n3_01_advanced_adaptation_generate.py:674`)に**段落数引数はなく**Title+Body形式のみ検査する(委任_02の「段落数5で呼ぶ」は誤り、M2で訂正)。5段落契約はY側の決定論確認で担保(T4) |
| A12 | Standard A2調整 | PRODUCTION_WIRED | 01A §2 | `generate_family_x_standard_a2_no_heading`(`er003_v1_n3_01_standard_a2_generate.py:541`)も段落数引数なし。簡易化指示にVoice口調保持の文言はない。Trialで2通り比較(Xそのまま vs 「各段落の話者・一人称・迷いの表現を保つ」1文追加、約+0.5円、S2) |
| A13 | 段落境界での決定論分割+段落数不足は1回だけ再生成→STOP | PRODUCTION_WIRED | 01A §2(`split_family_x_article_text_v2`、Xは「3段落以上」確認のみ) | 方式を流用し、段落数**ちょうど5**(リード1+Voice各1+最終パート1)の新関数。Yでは段落=話者なので、ずれると別人物Voiceで読まれる重大事故になる(M2)。日本語・Adv・Stdの各段階で確認 |
| A14 | Preview(役割文・原則) | PRODUCTION_WIRED | 01A §3 | 各Voiceの立場・結論を先出ししない(Cross-level共通原則CS:1716) |
| A15 | Comment 1〜3の型(次の焦点/回収+次の問い/核心整理+次パートへの橋) | PRODUCTION_WIRED | 01A §3 | X定数は無変更、Y用role定数を**新規定義**(「第1部・第2部」前提文言の除去)。配置はD1推奨に従い§③ |
| A16 | Key Phrase(KPFT全文選定、最大3件、CMU gate、3-ASR投票、K2/P7/P8-KP) | PRODUCTION_WIRED | 01A §3 | 構造非依存で丸ごと継承。**KP日本語意味の人称一般化module(`er003_key_words_gloss_alignment.py`、`CURRENT_SPEC.md:1631`)も自動継承**(Voiceの一人称"I"を含む例文からKPを選んでも日本語意味が一般化される、S12) |
| A17 | In One Line(基本2文、新事実・結論追加禁止) | PRODUCTION_WIRED | 01A §3 | 要約圧縮層として維持し、最終パートの末尾は要約にしない(D1) |
| A18 | 日本語タイトル(Std) | PRODUCTION_WIRED | 01A §3 | 共通 |
| A19 | TTS backend(gemini-3.8-flash-lite-tts)・Style profile fx_20261017・PD06/S3/E1/K2/P7/P8-KP | PRODUCTION_WIRED | 01A §5 | Full Story相当の5パートはPD06を適用(Voice別Styleは設けない) |
| A20 | Std英語Narration生成後6%減速 | PRODUCTION_WIRED(X/Z) | 01A §5 | Z会話速度Trial(OPEN-462)の結果が出れば追従 |
| A21 | 統一ASR判定(AUW)・値ガード・HR Lock・3層ASR | PRODUCTION_WIRED | 01A §5(U7) | Y配線は既決 |
| A22 | 音声品質検査群(ratio/disfluency/repetition/Connected Speech/PASS_WITH_WARNING) | PRODUCTION_WIRED | 01A §5 | **segment_id対応が必要**(T8、§③-4/§③-5の全洗い出し表・parity test) |
| A23 | TTS記号正規化、Pronunciation Ledger、PNAP、M1複数発音、多語同音救済、er109(表記違い同音) | PRODUCTION_WIRED / er109はFable受入作業中 | 01A §4 | コード上のscopeリテラル("X","Z")に"Y"を追加するのは技術対応(PM_GOVERNANCE 28-1運用7)でありユーザー判断にしない。**開示**: 該当は`er103_proper_noun_alarm_policy_01.py:42`・`er109_xz_scope_01.py:25`。er109の最終Statusは実装着手時に確認 |
| A24 | retry/fallback/Store/resume(TTS通算3回、KP外側retry、`--regenerate-stage`、Master Audio Store) | PRODUCTION_WIRED | 01A §6 | 上限回数・安全装置を回避しない |
| A25 | Local Rewrite(英語5role)・Connected Speech | PRODUCTION_WIRED | 01A §5 | `resolve_narrative_role`が`full_story_part1〜3`固定(`er020...:130`)。part4/5の追加が必要(加算のみでXに影響しない)。FULL_STORYの役割説明は"the article's main narrated body"(`er020...:154`)で一人称を保つ指示がないため、書き換えでVoiceの一人称が消える恐れ → Voice segmentで書き換えが起きた場合は**一人称保持を確認し記録**(S6) |
| A26 | QA gates(style_profile/key_phrase_source/shared narration/Audio Validation Gate)・Assembly・headroom | PRODUCTION_WIRED | 01A §7 | timeline builderはYで新設(T11) |
| A27 | 試聴ページ標準フォーマット+check | 標準(2026-10-18) | 01A §7 | Voice人物名(職業ラベル)は内容として表に載せてよい。内部ID・Voice/Styleの内部情報は載せない |
| A28 | STOPセンチネル/RUN_LOCK | Z方式あり、X未実装(OPEN-354/355) | 01A §6 | 新規Yは**最初からZ方式を採用**(技術選択。判断事項にしない) |
| A29 | routing/pricing登録(未登録modelはfail-closed) | PRODUCTION_WIRED | 01A T17 | Y用キー(Y-B3、Voice Card、Leakage、Y-Writer)を追加登録 |

**A件数: 29**

### B: 旧Bの承認済みVoices固有仕様 → Y構造との整合を確認して継承設計
| ID | 項目 | Status(旧B) | 出典 | Y適用時の注意 |
|---|---|---|---|---|
| B01 | Voice Card起点・具体的状況から書き始める(外側紹介型"For an applicant who..."を使わない) | APPROVED/PRODUCTION_WIRED | 01B §2,§4 | カードは14項目→**6〜7項目**: 性別・人物ラベル・状況と具体場面・懸念・賭けているもの(守りたいものと統合)・制約・背景fact id 0〜1(S1。「必要」は「懸念」と重複するため削る) |
| B02 | Voice=その立場から"I"で語れる具体的な人物(論点・抽象軸ではない) | 3V方式は2026-09-10承認。原則自体は旧記録で「候補(未承認)」だが原文§2.3がユーザー再確認 | 01B §2-1(DECISION_LOG_HISTORY:8530-8552) | 抽象軸(Business/Legal)Voiceは禁止(4Vで失敗) |
| B03 | Voice本文は一人称"I"/リード・最終パートは語り手 | ユーザー決定2026-09-08 | 01B §4 | 日本語原稿では「私」。忠実英訳で"I" |
| B04 | 語り手の外側要約(narrator analysis)の禁止 | PRODUCTION_WIRED | 01B §4 | リードも最終パートも各Voiceを外から要約しない |
| B05 | 同じ意味を2回言わない | PRODUCTION_WIRED | 01B §4 | Voice内・Voice間・最終パートとの間 |
| B06 | 解決策・コンサル提案の禁止 | PRODUCTION_WIRED | 01B §4 | 最終パートにも適用 |
| B07 | 賛否・陣営の機械割当をしない、2対1陣営化の禁止 | 原文§2.2再確認 | 01B §2-2,§3 | Voice Card生成プロンプトに明記 |
| B08 | 候補A: Voiceは自分の経験・立場に徹する | PRODUCTION_WIRED(2026-09-17) | 01B §3 | |
| B09 | 候補E: 自陣営内の迷い・葛藤・条件付きのnuanceは許容 | PRODUCTION_WIRED | 01B §3 | 境界(OPEN-167)は据え置き(§⑥-2) |
| B10 | 候補C: Voice内の数字は本人の経験に属する数値のみ・最大1つ。外部統計を論証に使わない。「数字必須」要求は撤廃済み | PRODUCTION_WIRED | 01B §5 | Voice Cardに数値・統計欄を持たせない |
| B11 | 候補F: 他Voiceが担う中心懸念は最終パート(または他Voice)に置く | PRODUCTION_WIRED | 01B §3 | `not_my_point`は**AIに書かせず、他2人のCard`concern`から決定論で生成**してWriterに渡す(S1)。構造的に境界を運用 |
| B12 | 体験claimの根拠付け(数値・制度・他者の具体的行動は台帳に直接evidenceがあるものに限る。無根拠の未来結果は断定せず感情・判断として書く) | DECIDED(2026-09-12) | 01B §5 | 原文§2.3と一致。Y Writerプロンプトの恒久原則 |
| B13 | Leakage Check項目の考え方(Voice 7項目: evidence_subject/numbers_foreground/narrator_analysis/unknowable_analysis/discovery_syntax/evidence_memorable/position_blur。最終パート側: tension_reverts_to_research/binary_camp_split等) | PRODUCTION_WIRED | 01B §6 | **日本語原稿に対して1回判定**(判定は是正のたびに毎回全文)。Closing項目`leak_closing_simple_summary`は最終パートの末尾規則に吸収(C03)。日本語への移植は未校正(§①-2) |
| B14 | Acceptance Gate(是正後も残るflagは後続へ流さない、`LEAKAGE_RESIDUAL_STOP`)、是正上限=初回+2回(計3) | PRODUCTION_WIRED | 01B §6 | 上限3を維持(安全装置を外さない)。是正方式は局所書き換え(下記注) |
| B15 | Tension「共通前提→分岐点→非対称性」(再掲・時系列反復なし、勝者を決めない、Evidence主語禁止) | APPROVED(2026-09-08) | 01B §7 | 最終パートの前半。末尾規則はD1 |
| B16 | Hook(The Question)「3立場を簡潔に提示、結論を先取りしない、企業名・統計禁止」 | PRODUCTION_WIRED | 01B §1-2 | Yのリードに対応 |
| B17 | 軽い会話調トーン(レポート調禁止) | PRODUCTION_WIRED | 01B §4 | Xの最新Writer文体との整合はR0プロンプト設計時に確認 |

注(B14の是正方式=局所書き換え。M5で仕様を明文化): 旧Bは「全文書き直し×3」で、直した箇所の代わりに別Voiceで再発する現象(whack-a-mole)と費用上振れを起こした(Opus L3、01B §6)。Yでは**判定回数の上限(初回+書き換え2回=判定3回、旧B `MAX_WRITER_ATTEMPTS=3`同等)は維持**したまま、是正を局所書き換えにする。仕様:
- (a) 初回判定+書き換え最大2回=Leakage判定は最大3回。
- (b) flagされた段落のみAIで書き換え、**他段落は決定論でbyte固定**(差込は決定論)。別Voiceへの再発は構造上起きない。
- (c) 書き換え後の文章も、R0最終稿と同等の決定論検査を通す(Fact Lockタグ規則、`clean_ja_for_next`、記号QA、`postprocess_ja`、5段落確認)。
- (d) 判定は毎回**全文**に対して行い、無変更段落の判定反転(PASS→FAIL)は**判定ノイズとして記録**する(原因の切り分け材料)。
- (e) 上限後も残る場合は**全文書き直しへ戻さず**`LEAKAGE_RESIDUAL_STOP`→前段(Card/B3)診断。「失敗時は旧B方式=全文書き直しへ戻せる」とした委任_02の記述は、C11(全文書き直し×3の不継承)と矛盾するため**削除**した。

**Xのテキスト側には局所書き換えは存在しない**(Xの`--only-segments`は音声(TTS)専用で本文再生成は`--regenerate-stage writer`の全体のみ、`er019_family_x_audio_production_runner_01.py:537`付近)。旧Bの局所書き換えは台帳逸脱の言い換え用のみ。したがってYでは小規模な新規実装になる。これは「検査・回数の追加」ではなく旧B承認済みGateの内部方式変更として扱う(Opusレビュー済み)。

**B件数: 17**

### C: 不継承(旧仕様・不採用案・不要な独自実装)
| ID | 項目 | 理由 | 出典 |
|---|---|---|---|
| C01 | 2V/4V/可変Voice数対応 | 3V固定(原文§2.2) | 01B C1 |
| C02 | 2V/3Vで別テンプレート・別schema・別pipeline | 重複が不整合の温床(F10)。Yは単一テンプレート | 01B C2 |
| C03 | 独立Closing section、`leak_closing_simple_summary`、Closing語数配分、旧Comment 4の位置(Tension後・Closing前) | 原文§2.1,2.4 | 01B C3 |
| C04 | `voice_fact_safety_gate_mode`(保守版Fact Safety、テーマ依存辞書) | Stage1は実データで効果0、辞書がテーマ依存、runtime evidence未取得。YはX/ZのFact Lockを基盤 | 01B C4 |
| C05 | Fact Attribution A'(`[VOICE_n_EVIDENCE]`出典免除rule) | B10(Voiceに外部統計を語らせない)と思想が逆 | 01B C5 |
| C06 | 外部制約統合(任意の4段目) | **必須化しない・禁止もしない**(台帳に材料があれば最終パートで任意に使える。恒久ルール化しない任意パターンと決定済み)(S11) | 01B C6 |
| C07 | 語彙overlap monitoring(0.40閾値前提) | 語彙指標では推論構造の同一性を測れない、gate化もされていない | 01B C7 |
| C08 | Pairwise Voice Distinctness Check(Trial限定) | 判定ノイズあり、UDRのまま。新Validator目的化を避ける | 01B C8 |
| C09 | B専用入口/registry/Voice割当/`B_FAMILY_A2` Gate level/`tension_reflection`・`in_one_line`の名残命名 | 旧B経路の転用はしない(原文§1) | 01B C9 |
| C10 | Evidence Compression Editor | 分析文挿入・実名匿名化の副作用(Trial-05) | 01B C10 |
| C11 | 「全文書き直し×3」のretry方式そのもの | whack-a-mole・費用上振れ(上限3は安全装置として維持) | 01B C11 |
| C12 | テーマ固有モジュール`er012_b_family_voices_theme_*.py`・旧テーマLedger | 旧テーマ資産。Yは新テーマ(ユーザー選定) | 01B C12 |
| C13 | 旧BのTTS声割当方式(Algieba/Erinome/Schedar固定、Voice見出しをNarratorが読む) | 見出し読み上げはXで廃止、声の割当はD3で決める。旧見出しはASR欠落(F11)も起こした | 01B §2-2,F11 |

**C件数: 13**

### D: Y固有の新設計・実質的仕様変更 → ユーザー判断(詳細§⑥)
| ID | 項目 | 推奨 |
|---|---|---|
| D1 | 最終パート(Tension+Closing)の中身、尺配分、Comment 4の廃止 | 再定義要素なし+締め2〜3型(定型化禁止)、90〜110語、Comment 1〜3の3本。Trialで約0.5円のComment 4あり版を並置 |
| D3 | 3 VoicesのTTS Voice | 人物別(Z正式表の割当関数を再利用)。PD06・flash-liteリスクと+12〜18円の条件を明記 |
| D4 | Writerを「R0のみ」(R1/R2のエンタメ性up Revisionを使わない)にするか | R0のみ(OPEN-217はn=1で弱いが方向・費用が支持し、戻せる) |

**D2(Voice Card作成方式)は判断事項から外し開示事項とした**(Fable判断、§⑥): 半自動(Y版B3で視点候補→Card生成AI 1回→Leakage検査、量産時の人手ゲートなし)。

**D件数: 3(D2は開示事項へ)**

**合計: 確定(U)8 / A 29 / B 17 / C 13 / D 3(+開示事項へ移動1)**

## ③ Family Yの構造案

### 1. 5パートの役割と境界(日本語原稿は5段落ちょうど。段落=パート)
| # | パート | segment_id(案) | 話者(TTS) | 役割 | 目安(英語語数/日本語字数) | 境界(やってはいけないこと) |
|---|---|---|---|---|---|---|
| 1 | リード | `full_story_part1` | 語り手(Aoede) | テーマ・問題提起・導入。具体的な場面か問いから始める | 40〜55語 / 約110字 | 3人の結論・立場の詳細を先に言わない、統計・企業名なし、結論先取りなし。「取材した」「話を聞いた」等、実在の取材者と受け取られる表現を使わない(S10) |
| 2 | Voice 1 | `full_story_part2` | 人物1(D3推奨=人物別) | 一人称。冒頭1文で「誰がどんな状況か」が分かる。自分の関心・懸念・守りたいもの | 65〜85語 / 約190字 | 外部統計・調査の説明なし、**Voice段落では数字を使わない**(M1。B10上限「本人経験の数字のみ最大1」の内側)、他2人の中心論点を言わない、解決策なし、他人の具体的行動・制度を創作しない、実在の人名・組織名・製品名・出来事を出さない |
| 3 | Voice 2 | `full_story_part3` | 人物2 | 同上(視点はVoice 1と経験・価値観・利害・優先順位が異なる) | 同上 | 同上 |
| 4 | Voice 3 | `full_story_part4` | 人物3 | 同上 | 同上 | 同上 |
| 5 | Tension+Closing | `full_story_part5` | 語り手(Aoede) | 共通前提→分岐点(何を賭けているかの違い)→非対称性→締め(2〜3型から選び同型連続を避ける。D1推奨・S7) | 90〜110語 / 約220字 | 各Voiceの再要約・時系列の反復なし、どれが正しいか決めない、新事実・解決策なし、固定修辞骨格(F8)なし |

合計目安: 本文約345〜400語+In One Line約35語 = 380〜435語。Xの実測(Std 385〜434語、Adv 416〜446語、01A §2)の範囲内。**語数・尺はGateにしない**(Xも規定値なし)。観測のみ。日本語原稿は800〜1000字(X実測837〜876字と同帯)。

Voice順: 当事者→遠い立場の順(旧Structure Trial-02の隣接対比、Trial知見で未承認の設計既定値)。

### 2. 学習支援構造の配置(D1推奨に従う場合)
音声順序: Intro → Welcome → Topic intro →(Std: 日本語タイトル)→ Notification1 → Preview intro → **Preview** → Notification2 → Key phrases intro → **KP×最大3** → Notification3 → Full story intro → **Comment1** → リード → **Comment2** → Voice1 → Voice2 → Voice3 → **Comment3** → 最終パート → **In One Line** → Outro。

- Comment 1(次に聞く焦点、答えを言わない)/ Comment 2(リード回収+「3人の違う人物が語る」への橋。台帳外の事実を足さない)/ Comment 3(3人を聞き終えて「なぜ違って感じるか」への視点移動、結論は言わない)。Xの型の再利用でCommentの数はXの4から3に減る。
- Voice 1〜3は連続(Voiceの間にCommentを入れない)。Voice切替の手がかり=冒頭1文の自己紹介的な具体状況(B01)+人物別TTS Voice(D3)+Assemblyの間。**Xが廃止した見出し読み上げ(Point One/Two、Narrator見出し)は使わない**(旧BでF11のASR欠落の原因)。
- In One Line: Xの仕様(基本2文)を維持。最終パート末尾が要約にならないよう制約(D1)することで、「最終パート=関係性と余韻」「In One Line=要点圧縮」と役割を分ける。
- 日本語タイトル(Std)・KPの音声構造(Std: 英語→日本語意味→英語、Adv: 英語→英語解説→英語)はX通り。

### 3. 処理フロー(X経路との差分は太字)
1. Research → Ledger(X通り)
2. **Y版B3**(Storyline1つ+必要最小fact+**3視点候補とVoice別背景fact割当**)→ 決定論B3 producer(数値注記)→ 丸め判断(X通り)
3. **Voice Card生成(AI 1回、6〜7項目)** → 決定論整合確認(fact_id重複なし、`concern`/`stake`の文言が同一でない、Cardの世界スコープ記述は背景fact id参照のみ。スキーマ水準の確認であり新Validatorではない)→ **`not_my_point`を他2人の`concern`から決定論生成**(S1)。※B3とCardの統合はTrial後(Trial-01は原因切り分けのため別callのまま)
4. **Y Writer(R0のみ、D4)**。Y版R0 Prompt規則(新規ファイル、X Fact Lock文言は無変更):
   - **(a) 個人スコープ(M1)**: Voice本人の状況・感情・判断・身の回り。出典=Voice Cardのみ。Fact Lockタグ不要。実在の人名・組織名・製品名・出来事は不可。
   - **(b) 世界スコープ(M1)**: 制度・統計・他者や組織の具体的行動・出来事。出典=台帳のみ。Fact Lock規則1〜5(タグ付き)。Voice段落ごと最大1件。**Voice段落は数字を使わない**(本人経験の数字も含む。B10上限「最大1・必須ではない」の内側)。
   - **(c) 話し言葉・常体**(S13)、リードは「取材した」等を避ける(S10)、最終パートの締めは2〜3型から選ぶ(S7)。
   - 「Leakage Gateは**事実判定ではなく編集構造の判定**であり、Voices限定の承認済み例外」(2026-09-17承認のVoice固有編集Gate、ユーザー原文§2.3も継承指示)。X思想(内容理由の再生成撤去)とは矛盾しない。
   - **5段落契約(M2)**: 日本語原稿で「本文ちょうど5段落+Title+In One Line」と、話者取り違え防止(Voice段落に一人称あり、リード/最終パートは一人称で始まらない)を決定論確認。違反は1回再生成→STOP。
   - **最終稿処理(M6)**: R0最終稿に`postprocess_ja`と最終記号QAを適用(Xは`er053_family_x_factlock_ja_writer_01.py:401-426`でR1/R2出力にのみ掛けており、R0のみのYでは明示的に追加が必要)。
5. **Leakage Check(日本語原稿を1回判定)** → flagがあれば該当段落だけ局所書き換え(B14注(a)〜(e))→全文再判定(判定最大3回)→残れば`LEAKAGE_RESIDUAL_STOP`
6. 忠実英訳(Adv)→ 5段落確認 → RF → A2簡易化(Std)→ 5段落確認 → RF。5段落確認で違反なら1回再生成→STOP。代替案: 5要素JSON(リード/Voice×3/最終)で英訳・簡易化するY用wrapper(X関数は無変更のまま、文字列方式の違反率が高い場合に採用)
7. In One Line、Preview/Comment 1〜3、KP選定、日本語タイトル(X通り、Y用role定数)
8. TTS/ASR/検査/Assembly/試聴ページ(X共通部品を再利用、Y用plan/timeline)

R1/R2を使わない理由はD4。

### 4. Xの接続点T1〜T17との対応
実装方針: **Xのrunnerは本文3パートが少なくとも10箇所で固定**(`full_story_part1〜3`: runner:80,180,488,995-1002,1401-1408,1590,1724,1889,1994)。X runnerを一般化改修すると、承認済みX Production経路を触るリスクがあるため、**Yは新しい薄い入口(Y runner)を作り、TTS生成・ASR・検査・Store・Assembly部品はXの共有関数を呼ぶ**。X側コードは無変更。

| T | 接続点 | Yでの対応 | 区分 |
|---|---|---|---|
| T1 | Writer prompt | Y版R0(Fact Lock流用+Voice Card+5段落契約)。R1/R2なし(D4)。新規ファイル | A+新規 |
| T2 | B3/Fact選定 | Y版プロンプト/schema(別ファイル)。契約V1〜V10維持 | A+新規 |
| T3 | 構造定義・分割 | `split_family_y_article_v1`(5段落)、Y用segment順tuple | 新規(方式はA13流用) |
| T4 | 英訳/簡易化 | **訂正(M2)**: 既存の忠実英訳/A2簡易化関数に段落数引数はない(Title+Body形式のみ検査、A11/A12)。Y側で日本語・Adv・Stdそれぞれ「本文ちょうど5段落+Title+In One Line」と話者取り違え防止(Voice段落に一人称あり、リード/最終パートは一人称で始まらない)を決定論確認し、違反は1回再生成→STOP。代替=5要素JSONで英訳・簡易化するY用wrapper | A+新規(小) |
| T5 | Preview/Comment scaffold | Y用role定数(C1〜C3)、context構成を新規 | 新規(型はA15) |
| T6 | KP選定 | そのまま | A |
| T7 | In One Line | そのまま、重複防止は最終パート側の制約で吸収 | A |
| T8 | segment ID検査の網羅 | **訂正(M3)**: 「`resolve_narrative_role`のpart4/5追加のみ」では足りない。`--only-segments`正規表現(`full_story_part[1-9]\d*`、runner:537)は通るが、segment名の直書き一覧が複数ある(§③-5の全洗い出し表)。Y part1〜5がX本文segmentと同じ検査(disfluency/repetition QA、Std 6%減速の適用と未適用ガード、Local Rewrite/Connected Speechの役割、AUW、値ガード)を受けることを**parity test**で保証。共有moduleを変更する場合はX/Z出力のbyte一致回帰。Voice segmentのLocal Rewrite発生時は一人称保持を確認・記録(S6) | A+小改修+test |
| T9 | TTS segment生成・Voice割当 | Y用generator。人物別VoiceはZ `assign_dialogue_voices`(決定論)を再利用(D3)。**M4**: 同一run内の再利用判定(`_generate_or_reuse`、runner:665-694)は「segment名+正規テキスト+style_version」のみでTTS Voice名がkeyにない。YはCard(性別・順番)でVoiceが決まるためCard作り直し後に古い声が再利用される危険があり、Y runnerの照合keyに**voice名を含める**(X関数は無変更、Y用に包む)。Master Audio Storeは`speaker_voice`をkeyに含む(`er006_master_audio_store_01.py:43-54`)ので影響なし | 新規+A |
| T10 | Style profile | `fx_20261017`をそのまま(Full Story相当=PD06)。OPEN-415(X/Z/Y横断エンジン化)は、Voice別Styleを持たない限りトリガーしない | A |
| T11 | Assembly timeline | Y用builder(新規) | 新規 |
| T12 | 試聴ページ | `render_standard_page`+Y用page script(Voice人物名を内容ラベルとして表示、内部ID非表示) | A+新規 |
| T13 | scope限定機構 | リテラルに"Y"追加(技術対応、開示済み=A23) | 技術対応 |
| T14 | RF | 採用(A09) | A |
| T15 | STOP/RUN_LOCK | Z方式を最初から採用(A28) | A |
| T16 | 来歴契約(U-1) | Y用`chain_method`を定義(U-1の拡張) | 新規(小) |
| T17 | routing/pricing | Y用キー追加登録 | 新規(小) |

### 5. segment名直書き一覧の全洗い出し(M3、Grep結果。実装時に再Grepして最終化)
| # | 場所 | 内容 | Y part4/5への影響 | 対応 |
|---|---|---|---|---|
| 1 | `er003_v1_n3_01_tts_generate.py:115-118` `A2_SLOWDOWN_TARGET_SEGMENTS` | `full_story_part1/2`のみ(X part3も含まれない) | 6%減速自体は`generate_a2_segment_with_slowdown`が無条件適用(下記の事実確認)。ただし未適用検知ガードの対象外 | Yは共有定数を直接拡張せず、Y用の対象集合を渡す/またはX側修正(OPEN-466)後に追従。要Fable判断 |
| 2 | `er003_v1_n3_01_assemble.py:273`(`_segment_missing_mandatory_a2_slowdown`、呼出:490) | 上記定数に無い名前は常に`False`(=未適用でも検知しない) | part3〜5は未適用を検知できない | #1と同じ。parity testで「Y part1〜5の未適用を検知できる」を確認 |
| 3 | `er019_family_x_audio_production_runner_01.py:80` `_REQUIRED_FULL_STORY_SEGMENT_IDS` | part1〜3 | Y runnerは独自定義 | Y用タプルを新設(Xは無変更) |
| 4 | 同:488 `_BODY_SEGMENT_NAMES`(repetition QA対象、:1011,:1421で使用) | part1〜3 | part4/5がrepetition QAを受けない | Y用タプルを渡す。parity testで確認 |
| 5 | `er020_tts_retry_local_rewrite_01.py:130` `resolve_narrative_role`、:105,:122 | part1〜3 → FULL_STORY(Zは`_cN`パターン) | part4/5が未分類(None)になる | part4/5をFULL_STORYへ加算。Xへの影響なし(加算のみ) |
| 6 | `er019_family_x_style_profile_01.py:201` | `"FULL_STORY": (part1, part2, part3)` | part4/5にFull Story Style(PD06)が当たらない恐れ | Y用に拡張(実装時にGrepで確認) |
| 7 | `er019_family_x_audio_plan_01.py:266,294,324,351`、`er019_family_x_pointless_*` | X用plan(part1〜3) | 流用しない(Y用plan新設) | 新設 |
| 8 | `er056_en_asr_retry_replay_01.py:46` `BODY_SEGMENTS` | part1〜3+point_one/two(ASR retry replay) | Y part4/5が対象外 | 実装時に使用範囲を確認 |
| 9 | `er019_pp_hr_page_01.py:93`、assemble系(`er003_v1_n3_01_assemble.py:792`等) | 名前直書き | 試聴/Assembly | Y用builder新設(T11/T12) |

他にもあり得るため、**実装時に`full_story_part`のGrepを全モジュールに対して再実施**し、本表を最終化する(本表は網羅の宣言ではなく出発点)。

**parity test(M3)**: Y part1〜5を入力にして、X本文segmentと同じ検査(disfluency/repetition QA対象、Std 6%減速の適用+未適用ガードの発火、Local Rewrite/Connected Speechのrole、AUW、値ガード)が適用されることをsegmentごとに検証する。共有moduleを変更した場合は、X/Zの既存出力に対するbyte一致回帰を必須とする。

**事実確認(副次所見、委任_03、読取のみ)**: X Std part3は6%減速が**適用されている**。`er019_output/family_x_audio_production_wiring_01/tesla_spacex_merger_talks__run_nws_01/a2/narration/`のpart1〜3は全て`*_original.wav`があり、長さ比(減速後/原音)は part1=1.0601、part2=1.0595、part3=1.0597(6%の減速に整合)。つまり**減速自体は漏れていない**が、`A2_SLOWDOWN_TARGET_SEGMENTS`にpart3がないため、未適用を検知するガード(assemble:273,:490)は**part3では働かない**(潜在的な検知ガードの穴)。X側の別item(OPEN-466)として起票、修正はしない。

### 6. Y版R0の規則・決定論モニタ(M1/S4)
- M1の個人/世界スコープ規則、5段落契約、後処理は§③-3のとおり。
- **S4 決定論モニタ(記録専用・追加費用0・Gate化はD)**: Voice段落の数字の有無、段落ごとのFact Lockタグ数、一人称の有無、最終パートとVoiceの語彙overlap。合否に使わない。
- 機械検出できる一部の事実創作はこのモニタで補い、残りはRF(S5: Voice段落のflag件数を記録)とTrial人手確認で補う。

## ④ 過去の品質NGと対策の対応表(旧B F1〜F12)

| ID | 旧Bの事例・原因 | 承認済み対策 | Y適用方針 | 残存リスク | §6対応 |
|---|---|---|---|---|---|
| F1 | Trial-04: 調査報告調で数字連続。Voice Cardなし・Evidence主役 | 一人称(09-08)、Voice Card起点、候補C | B01/B03/B10。Card起点を踏襲。Cardは半自動生成(開示事項) | Card品質に依存(自動生成は未実証) | (1) |
| F2 | Trial-05: 語り手がVoiceを外から要約(6/6) | 一人称化でFAIL消失(Trial-06以降)、narrator_analysis項目 | B03/B04。リード・最終パートも各Voiceの外側要約禁止 | 日本語での判定校正が未実施 | (1) |
| F3 | 4V: 抽象軸Voice(Business/Legal)が制度解説へ逆戻り | 3V・具体的人物、外部制約はTension側へ | B02/C01 | 低(人物化で2 attemptで0件) | (1)(2) |
| F4 | 3V汎用化: 「数字を織り込め」命令とEvidence主語禁止の二律背反→whack-a-mole、全文書き直しで別Voiceに再発 | 候補C(数字必須撤廃)、「数字は本人経験のみ最大1」 | B10。Voice Cardに数値・統計欄なし、Voice段落は数字を使わない(M1)。是正は局所書き換え(B14注) | 局所書き換えの有効性は未実証(Trialで実測) | (1)(5)(6) |
| F5 | Tension非対称性文(3人の役割・権限差の断定)が台帳逸脱検査(Ledger Deviation Checker)でMAJOR化、hedge増量で収束せず | (旧Bでは未解決のまま構造的衝突) | **Xには逸脱Checkerが存在しない**(2026-10-10撤去、`CURRENT_SPEC.md:1194`、01A §1)ため衝突の前提が消える。非対称性文はVoice Card・選定factに既に書かれた立場関係だけで書く(新事実導入なし)規則+RF(非停止)。→ 判断事項にしない | RFが当該文をflagしても人の確認待ちリストに入るだけで停止しない | (5) |
| F6 | PN A2旧版: Voiceが統計引用、立場が曖昧。上限後も「前例踏襲」で試聴へ流していた | 候補A/C/E/F、`leak_position_blur`、Acceptance Gate(残存は後続へ流さない) | B08〜B11/B13/B14 | Gateは流出防止であり原因解消ではない。局所書き換えで収束しない場合は止まる(安全側) | (1)(2)(6) |
| F7 | PN A2新版: 肯定派Voiceが相手の中心懸念を語る(許容) | 候補E/F、position_blur | B09/B11。Voice Cardの`not_my_point`欄で構造的に運用。**OPEN-167は据え置き**(判断事項にしない、§⑥-2) | nuance境界とユーザー知覚のずれ。Trialで頻度を実測してから判断 | (3) |
| F8 | Closingの修辞骨格が4/4同型。記事間類似を測るQAなし | (Closing廃止=原文) | D1推奨: 再定義要素なし、締めは2〜3型から選び同型連続を避ける、「末尾でリードの場面に戻る」も定型化させない(S7)。Trialは2テーマ(S8)で横並び比較するが、記事間類似の判定は少数記事では限定的(検査は追加しない) | 記事間類似の機械検知はなし | (4) |
| F9 | PN B1: 台帳が新しい外部研究と矛盾(鮮度) | OPEN-166 | Yは新テーマごとにX経路のResearchを実行(A01)。台帳再利用は同一run内のみ | 低 | - |
| F10 | 2V templateに一人称指示が欠落(重複テンプレート) | 2026-09-15修正 | C02。単一テンプレート(3V固定) | 解消 | - |
| F11 | Narrator見出し"One Voice:"がASR欠落→HR Lock | 是正済み | C13。見出し読み上げ自体を使わない(Xと同じ) | 解消 | - |
| F12 | 語数・尺超過(3V 497語/395秒、Tensionが132語で主因) | soft target、是正再生成は語数を再強化しない | 最終パート90〜110語をプロンプト上限として明示。WARNのみ(X方式) | 超過してもGateにしない | - |

### 品質リスク§6(1)〜(6)と設計での抑え方(新Validatorなし)
| §6 | 残るリスク | 設計での抑え方 | 新規追加 |
|---|---|---|---|
| (1) 解説者化 | Card品質、日本語Leakage校正 | B01〜B04/B10、Cardに統計欄なし、Leakage 7項目(既存call) | なし |
| (2) 立場・論点の重複 | 意味レベルの重複を機械検知する承認済みgateはない(語彙overlapは不適、C07/C08) | **Voice Cardの独立性設計**: Y版B3が3視点を「経験/利害/価値観/優先順位のどれで異なるか」を明示して選ぶ。Card生成が各人の`concern`・`stake`・`not_my_point`を相互排他に作る。fact_idの重複なしはスキーマ水準で確認(Y Trial-01で重複0)。Trialでは人が評価 | なし |
| (3) 他Voiceの中心主張の取り込み | OPEN-167(nuance境界)は未決 | 候補E/F+position_blur+`not_my_point`欄。判断は実測後(§⑥-2) | なし |
| (4) Voiceと最終パートの重複 | 旧Bの語彙overlap監視はTension対Voiceを比較していなかった(01B §8-3) | 最終パートの役割を「違いの関係と余韻」に限定(D1)。Trialで**監視のみ**の語彙overlapをAPI費用0で計測(合否に使わない) | なし(Trial計測のみ) |
| (5) 体験談の事実創作 | 検査層が薄い(RFは事後・非停止、Xの決定論ゲートは数字中心) | B12+M1の個人/世界スコープ規則(Fact Lock規則1〜5は世界スコープに適用)+Voice Cardに「数値・制度・他者の具体的行動は書かない」制約+S4決定論モニタ+RF(A09、S5でVoice段落flag件数を記録)。Trialで**台帳に無い一人称の事実主張の数を人が全件確認**(基準=0件) | なし。**発生した場合のみ**Leakage Check既存callに1項目追加する案を、その時点で提示(D候補として予告) |
| (6) 検査・書き直しでも収束しない | 局所書き換えは未実証。判定ノイズ(無変更段落の反転)とR0同等の決定論検査を通らない書き換え文のリスクはM5で明文化 | 判定回数の上限3を維持、局所書き換え(B14注(a)〜(e)の仕様)、Acceptance Gateで止める、内容理由の無制限retryは設けない(X思想と整合)。上限後は全文書き直しに戻さずSTOP→前段(Card/B3)診断 | 局所書き換え(内部方式) |

## ⑤ QCD評価

出典: X実測(`docs/research/FAMILY-X-NEWS-2ARTICLES-E2E-01/RESULT_01.md` §5、01A §9-1: 記事A 54.06円/記事B 131.61円、定常平均約75.3円)、旧B実測(2V新規topic 1セット99.01円[TTS除く]、3V Writer 1 attempt約24.3〜28.3円、01B §9)。**以下は推定(実測ではない)**。Writer R0〜R2=16.55〜17.13円で1 callあたり約5.5〜6円(R0は入力が大きく6〜8円)。

### 費用(円/セット、Xを基準とした増減の推定)
| 要因 | 増減(推定) | 根拠 |
|---|---|---|
| Voice Card生成 1 call(6〜7項目) | +2〜4 | R0より入力が小さい |
| Y版B3の出力増(3視点+割当) | +0.5〜1.5 | 呼出回数は増えない |
| Leakage Check 1判定(日本語原稿+Card) | +2〜4 | 判定JSON出力。モデル未確定 |
| 局所書き換え+全文再判定の期待値 | **+4〜8**(委任_02の+1〜3から修正) | 旧B実績: 1回通過はPN A2新版のみ、Trial-02は2回、Trial-01と3V汎用化Regressionは非収束。書き換え発生確率は**60〜75%**と置く(従来の40〜50%は楽観的)。1サイクル=書き換え1〜2+再判定2〜4 |
| R1/R2を使わない(D4) | **-9〜-11** | R0〜R2のうちR1,R2の2 call |
| Comment 4廃止(D1) | -0.2〜-0.5 | scaffold+TTS 1本 |
| 本文TTS/ASR(語数同等、5パート) | ±0〜1 | 総語数はX実測と同帯 |
| 人物別TTS Voice(D3推奨)がflash-liteで可 | 0 | 同モデル |
| 同、flash-liteで品質不足でPro TTSが必要な場合 | +12〜18 | `pricing_snapshot.json`: Pro 音声出力$20/Mトークン vs flash-lite $6/M=3.3倍を本文TTS分(X TTS 11.3〜12.7円の6割強)に適用。Z Dialogueは`gemini-2.5-pro-preview-tts`でPD06非適用(`CURRENT_SPEC.md:1704`) |
| **合計(D4採用、D3=flash-lite)** | **約-3〜+8** | 定常平均で約72〜83円(X 75.3円±約6〜8) |

- **STOP時の期待損失(S8、新規)**: Leakageが上限3で収束せず`LEAKAGE_RESIDUAL_STOP`になった場合、その記事のResearch〜B3(約17〜50円: Research 6〜27+Ledger 5〜16+B3 7〜9)と書き換え分が無駄になる。旧B実績では収束しない例が少なくなく(Opus所見)、**量産単価ではSTOP率×(17〜50円)を上乗せして見る**(Trialで実測)。
- D4を不採用(R1/R2維持)なら+約9〜11円。Pro TTSが必要なら更に+12〜18円。
- **旧B比**: Writer段(Card+R0+Leakage+書き換え期待値)は約14〜24円で、旧B 3V Writer 1 attempt(24〜28円、Fact Checker A'・Ledger Deviation含む)と同等〜低め。
- 70円目標に対し: 差の主因はXと同じResearch費の記事間変動。改善余地(Trial後に検討): Card生成のB3統合(-2〜-4円)、Leakage判定モデルの軽量化、Research再利用。Charter 3により原価増となる要素は必要性確認済み(Card=人物性の源、Leakage=旧Bで品質NGを止めた承認済みGate)。

### 品質 / 開発工程(D)
- 品質: 旧B承認済み対策(B01〜B17)で§6の(1)(3)(5)の主要因をカバー。意味的な重複(2)(4)と創作事実(5)の検出は薄く、Trialで実測してから追加判断(追加する場合はD)。
- 開発工程(推定): 実装(DEV、API 0)は独立に並列化できる4束 ── (a)Y版B3・Card・R0・Leakage・局所書き換え、(b)Y用plan/segment/timeline/Comment role、(c)scope追加("Y")・pricing/routing登録・segment_id拡張とparity test、(d)試聴ページ+check。規模は概算でSonnet 3〜4委任単位(推定)。最大の遅延要因はD1/D3/D4の確定待ちとTrial承認、テーマ選定(ユーザー選定)。
- 先行可能: 判断確定前でも(c)(d)の共通部品調査、M7校正用データ整備は並行可能(M7の実行自体は有料でTrial承認後)。

## ⑥ ユーザー判断事項(D3件+Trial実施承認)と開示事項

各項目は「既存仕組みで解決できないか」「過去に解決済みでないか」を確認済み。

### D1. 最終パート(Tension+Closing)の中身と、Comment 4の扱い
- 決まっていること: Tensionは「共通前提→分岐点→非対称性」継承、独立Closing廃止、再要約や冗長な追加を避ける(原文§2.4)。
- 新しい判断が必要な理由: 旧Closingの「問題の見え方の再定義」を残すか、Comment 4(Xでは全体の意味回収+In One Lineへの橋)をYで残すか。原文に指定なし。Comment 4の廃止はX承認済み仕様(Comment 1〜4)から外れる。
- **推奨**: (a)再定義の独立要素は置かない。最終パートは「共通前提→分岐点→非対称性」+**締めは2〜3型から選ぶ**(例: 未決の問いを残す/具体的な場面に戻る/関係性を一言で言う)。**同型の連続を避け、「末尾でリードの場面に戻る」も定型化させない**(S7、旧BのClosing 4/4同型化の再発防止)。要約・勝者・解決策は禁止、90〜110語。(b)**Comment 4は廃止し、Commentは1〜3の3本**(旧B承認版のComment 1〜3の配置と一致)。
- 理由: Comment 4を残すと「最終パート→Comment 4→In One Line」の3重の締めになり重複を増やす。
- QCD: 費用-0.2〜-0.5円、尺-約15秒。リスク: 締まりが弱くなる。Trialで**Comment 4あり版を並置**してA/B試聴(約+0.5円、再組立のみ)。
- 代替案: (a')再定義1〜2文を残す(尺+10〜15語)、(b')Comment 4を残す。

### D3. 3 VoicesのTTS Voice(声)
- 決まっていること: 各Voiceは独立した人物(原文§2.3)。XのStandardは語り手Aoede単独、見出し読み上げは廃止。旧Bは人物別(承認2026-09-08)、Zは登場人物Voice正式表(2026-10-23ユーザー最終決定)。
- 新しい判断が必要な理由: Yにどちらを適用するか未指定。聞き分けと費用に影響する。
- **推奨: 人物別Voice**(Voice 1〜3のみ。リード/最終パート/Comment/Preview/In One Lineは従来の語り手)。Z正式表の割当関数`assign_dialogue_voices`を再利用(性別はVoice Cardの明示項目、名前から推測しない)。
- 理由: 見出しなしの連続する3人の一人称を自己紹介文だけで聞き分けるのは難しい。
- **リスク(明記)**: (1)人物別Voiceを**flash-lite+PD06で読ませた実績がない**(Z Dialogueは`gemini-2.5-pro-preview-tts`でPD06非適用)。PD06が人物を「語り手」化・平板化させる可能性があり(S9)、Trialで聞き分けとPD06の影響を評価する。(2)flash-liteで品質不足でPro TTSが必要なら**+12〜18円/セット(推定)**。その場合、またはStyle変更(PD06除外等)が必要な場合は、結果を添えて再判断を求める(判断事項D)。
- 代替案: Aoede単独(費用差0、実装最小、聞き分けは自己紹介文のみ)。Std 6%減速のVoice別適用はOPEN-462結果に追従。

### D4. WriterをR0のみにする(R1/R2のエンタメ性up Revisionを使わない)
- 決まっていること: XのWriterはR0→R1→R2でX承認済み。Yへの適用承認はない。
- 新しい判断が必要な理由: OPEN-217(2026-09-28)が「対処方針をユーザーが判断する」としたまま未決。Y Trial-01でX流R1→R2をVoice文脈へ適用すると旧Leakage fail-fieldが**2→3→11に悪化**し、AI評価(rubric)は改善と誤判定(OPEN-218)。
- **推奨: Y初期はR0のみ**。人物の面白さはVoice Card(具体的な状況・葛藤)で担保する。
- **弱さの明記**: 根拠のOPEN-217の観測は**n=1**で強くはない。ただし方向(Leakage悪化)と費用(-9〜-11円)が推奨を支持し、**不足ならR1のみを追加して戻せる**。Trialで任意に「R0+R1」比較枠(約+8円)を置ける(S8)。
- QCD: 費用-9〜-11円/セット。リスク: Xよりエンタメ性が低い可能性→Trial試聴で確認。
- 代替案: X通りR0→R1→R2(+9〜11円、Leakage悪化リスク)。採用でOPEN-217はY側方針として確定(close候補)。

### Trial実施承認(新仕様Trial、金額無関係に承認要=PM_GOVERNANCE 7-7)
- 内容: §⑦の段階(0)M7校正→(1)テキスト段階2テーマ→(2)音声段階1テーマ→ユーザー試聴。Production非配線・DEV経路のみ。
- 費用見込みと上限は§⑦(推定約96〜214円、上限250円を提案)。**テーマはユーザーが選ぶ**(§⑦に候補5件)。
- 承認があるまで実行しない。

### 開示事項(判断不要。異議があれば判断事項へ上げる)
1. **D2 Voice Card作成方式 = 半自動**(Y版B3で3視点候補→Card生成AI 1回→Leakage検査、量産時の人手ゲートなし)。人手作成は「安定量産」と両立せず実質的選択肢でないため判断事項から外した。品質はTrialと試聴で確認し、問題が出たときだけ再判断(原文§5にも沿う)。
2. **M1 スコープ分離とVoice段落の数字不使用**: Y版R0の新規Promptで、個人スコープ(出典=Voice Card)と世界スコープ(出典=台帳、Fact Lock規則1〜5、Voice段落ごと最大1件)を分け、Voice段落では数字を使わない。Xの文言は変更せず、旧B承認済み「体験claim根拠付け(B12)」「候補C(数字は本人経験のみ最大1、B10)」の範囲内(B10の上限の内側)。Fable判断=設計内。境界事例として「Fact Lock適用範囲の変更」と見なされる場合は判断事項に上げる。
3. 「Xのみ」承認項目(丸め判断・RF・PNAP等)のA継承(Voicesの性質と衝突しない。丸め判断は【中核数値】のみでリード/最終パートにしか作用しない。RFはVoice個人内容が台帳に無くflag量産の可能性→Trialで件数測定)。
4. er109/PNAP等のscopeリテラルへの"Y"追加(技術対応、PM_GOVERNANCE 28-1運用7。条件: X/Z出力byte一致回帰、実装時にer109最終Status確認)。
5. Y用の薄い入口(Y runner)新設(X runner無変更)。
6. STOPセンチネル/RUN_LOCKをZ方式で最初から導入。
7. Leakage Gate: 「事実判定ではなく編集構造の判定、Voices限定の承認済み例外」(M1)。局所書き換えは旧B承認済みGateの内部方式変更(判定上限3維持、M5仕様)。

### ⑥-2. 判断事項にしなかった候補とその理由(判断水増し防止)
| 候補 | 判断不要とした理由 |
|---|---|
| nuance許容境界(OPEN-167) | 原文§2.3が方針を確定。厳密な線引きは旧B承認済みA/E/F+position_blur+`not_my_point`で開始し、Trial実測後に判断 |
| Tension非対称性×台帳逸脱 | Xに逸脱Checkerが無く前提が消える。Card/選定factの範囲に限る規則で足りる |
| 総尺・語数 | X実測を基準、Gateにしない |
| Leakage Check(日本語原稿)/局所書き換え | 旧B承認済みGateの流用と内部方式変更(上限3維持)、M5で仕様明文化 |
| 事実創作検査の追加 | 追加しない。S4決定論モニタ+RFで記録。発生時のみ既存call項目追加案を提示 |
| STOP/RUN_LOCK、試聴ページ、segment_id | 技術選択・内部実装 |
| Voice選定基準 | 恒久規則ではなくTrial基準。B3プロンプトの設計入力 |

## ⑦ 次工程: 改訂Trial計画案(実施は別途承認)

- **前提**: D1/D3/D4確定とTrial実施承認。新規記事テーマは**ユーザーが選ぶ**(下の候補5件から2件。Fable/Claudeは決めない)。
- **段階**: (0)M7校正 → (1)テキスト段階 2テーマ(各Std/Adv) → (2)音声段階 1テーマ(余裕があれば2) → ユーザー試聴。段階(0)(1)で構造起因のNGが出たら音声費用を使わず止める。
  - **(0) M7: 日本語Leakage事前校正**: 旧B正解ラベル付き記事を日本語化し、誤検知・見逃しを測る。NG例=PN A2旧版、PN B1、3V汎用化Regressionでflagされた個体。OK例=PN A2新版、free_address。費用 数円〜20円(推定)。結果が悪ければGate化前に判定定義を調整(定義調整の範囲を超える場合は判断事項D)。
  - **(1) テキスト段階(各テーマ)**: Research〜Ledger〜Y版B3〜Card〜R0〜Leakage(+局所書き換え)〜忠実英訳/A2簡易化〜RF。評価: Leakage/Acceptance Gate、Fact Lock、RF(Voice段落のflag件数、S5)、S4決定論モニタ(記録のみ)、5段落契約。追加: S2 A2簡易化2通り比較(Xそのまま vs 話者・一人称・迷い保持の1文追加、+0.5円)、S3 Std英語に監視専用Leakage 1回(+2〜4円、Gateにしない)、局所書き換え時の一人称保持(S6)。任意: R0+R1比較枠(約+8円、D4補強、S8)。
  - **(2) 音声段階(1テーマ)**: Preview/Comment/KP〜TTS/ASR〜Assembly〜試聴ページ。**人物Voiceの聞き分け評価とPD06の語り手化の影響(S9)**、Comment 4あり/なしA/B(約+0.5円)、Std 6%減速(OPEN-462追従)、parity test結果。
- **費用表(推定、出典=§⑤とX実測)**:

| 段階 | 内容 | 費用(円) |
|---|---|---|
| (0) | M7校正(旧B記事5件を日本語化+Leakage判定) | 5〜20 |
| (1) | テキスト段階 1テーマ: Research 6〜27+Ledger 5〜16+B3 7〜9+Card 2〜4+R0 6〜8+Leakage初回2〜4+書き換え期待値4〜8+英訳/簡易化0.6〜1+RF 1.3〜1.6+S2 0.5+S3 2〜4 | 約36〜83 |
| (1) | 同 2テーマ | 約72〜166 |
| (2) | 音声段階 1テーマ: scaffold 1.3〜2.9+TTS 11〜13+ASR 6〜11+Comment4並置0.5 | 約19〜28 |
| 合計 | (0)+(1)×2+(2) | **約96〜214** |
| 任意・条件付き | R0+R1比較枠 +8/テーマ、Pro TTS必要時 +12〜18 | 通常合計に含めない(発生時はFable経由で再判断) |

- **STOP時の期待損失(S8)**: テーマがLeakage上限3で収束しない場合、その分のResearch〜B3(約17〜50円)と書き換え分が無駄になる(最大見積に含めて吸収)。
- **上限**: **250円**(通常範囲の最大見積214円+再試行余裕。新仕様Trialのため案件見積に関わらず承認が必要=PM_GOVERNANCE 7-7)。日次1,000円内。作業の分割・日付分割で境界を回避しない。
- **成功基準(既存の承認基準のみ)**: Leakage Check項目がAcceptance Gate(判定上限3、残存なし)を通る / Fact Lock・RFの既存基準 / Audio Validation Gate全PASSでHR Lock 0 / 事実創作0件 / 最終判定はユーザー試聴。語数・尺・費用・S3・S4は記録して次判断に使う(新基準を作らない)。
- **STOP/撤退**: Leakageが判定上限で収束しない場合は止め、前段(Card/B3)の問題として原因を整理(音声費用を使わない、全文書き直しへは戻さない)。M7校正で誤検知・見逃しが大きい場合はGate化前に定義調整。
- **テーマ候補(5件。ユーザーが2件選ぶ。基準=複数の当事者が一人称で語れる、X経路のResearchで台帳が作れる、統計を前提にしない、旧Bテーマと重複しない)**:

| # | English | 日本語 | 選定理由 | 3視点が立つ理由 |
|---|---|---|---|---|
| 1 | Should a small company move to a four-day work week? | 小さな会社は週4日勤務に移行すべきか | 近年の制度変更事例が多く台帳を作りやすい | 経営者(売上と人手)/社員(家庭・休息)/取引先・顧客(窓口が減る側) |
| 2 | Should schools ban smartphones during the day? | 学校は日中のスマホ持ち込みを禁止すべきか | 各国で制度化が進み公的な事例がある | 教師(授業運営)/保護者(連絡・安全)/生徒(友人関係・調べもの) |
| 3 | When tourists crowd a small town | 観光客が増えすぎた小さな町 | オーバーツーリズムの具体策が各地で報じられている | 住民(日常の静けさ)/店主(収入)/観光客・来訪者(体験と制約) |
| 4 | Allowing pets in rental apartments | 賃貸住宅でペット可にするか | 賃貸の制度・慣行の事例が調べやすい | 入居者(暮らしと責任)/大家(設備の損耗)/隣人(音・においへの感じ方) |
| 5 | Moving school club activities to the community | 学校の部活動を地域へ移行するか | 日本の制度変更で一次情報が多い | 教師(負担)/保護者(費用・送迎)/生徒・地域指導者(続けたい気持ちと関わり方) |

## SSOT整合メモ

- 本書はDESIGN_PROPOSAL_01の改訂版(Opusレビュー反映)。01は履歴として残す。
- CURRENT_SPECは**変更しない**(未承認案を正式仕様として書かない)。例外=`CURRENT_SPEC.md:1692`の古い記述への注記のみ。
- 未承認案(本書のD1/D3/D4推奨、局所書き換え、R0のみ、Y用B3プロンプト、M1のスコープ規定等)はOPEN_ITEMSに「判断待ち候補」として記録し、確定済み基本方針(原文§2=U1〜U8)と分けた。
