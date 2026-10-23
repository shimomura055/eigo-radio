# DESIGN_PROPOSAL_01: Family Y(Voices型)基本設計案(統合版)

管理ID: FAMILY-Y-VOICES-DESIGN-01 委任_02 / 2026-10-23(JST) / **DESIGN/RESEARCH ONLY**(Trial・API費用・Production/Prompt/コード変更なし)
Status: `DESIGN_DRAFT_PENDING_OPUS_REVIEW`。本書は**設計案**であり、仕様採用・`APPROVED_FOR_PRODUCTION`・`PRODUCTION_WIRED`の記録ではない。
ユーザー指示原文: `docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER.md`(以下「原文」)。入力: `INVENTORY_X_Z_SPEC_01.md`(以下01A)、`INVENTORY_OLD_B_VOICES_01.md`(以下01B)。
再照合した一次情報(今回Grep/Readで確認): `CURRENT_SPEC.md:1185-1192`(RF)・`:1692`(後述の古い記述)、`OPEN_ITEMS.md` OPEN-167/217/218/219/415/461/462、`er019_family_x_audio_production_runner_01.py:80,180,488,537,995-1002,1401-1408,1590,1724,1889,1994`、`er020_tts_retry_local_rewrite_01.py:125-150`、`er005_output/cost_baseline_01/pricing_snapshot.json`。それ以外の出典は01A/01Bが記載した`file:行`を引き継いでいる(再読していない行は「01A/01B引用」と読むこと)。

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

**Family Yの基本設計は成立する見込みが高い**(根拠: 設計の大半はXの承認済み経路をそのまま使えるため。Yに固有の新規設計は「5パート構造・Voice Card・Voice用検査の移植・最終パート」に限られる)。

- 継承の内訳は§② のとおり(A=X/Z承認済み共通仕様の継承、B=旧B承認済みVoices固有の継承設計、C=不継承、D=ユーザー判断)。**ユーザー判断が必要なのは4件**(§⑥、目標6件以内)。他の候補(OPEN-167のnuance境界、Tensionの事実衝突、尺・語数、RF/丸め判断の適用、事実創作検査の追加、局所書き換え方式)は、既存仕様の範囲または設計上の吸収で解けるため判断事項にしていない(§⑥-2に理由)。
- **新しい検査(Validator)は追加しない**。Voice用検査は旧Bで承認済みのLeakage Check(日本語原稿に対して1回)とAcceptance Gateの移植のみ。
- 費用は「Xの実測±約6円/セット」と推定(§⑤。推定であり実測ではない)。70円/セット目標に対する差の主因はXと同じResearch費の変動で、Y固有の構造差分では大きく悪化しない見込み。
- **重要な未解決事項**(いずれも設計では解消できず、最小Trial(§⑦)で実測する):
  1. 日本語先行の三段(日本語→忠実英訳→A2簡易化)で、人物らしさ(口調・迷い)が平板化しないか(未検証)。
  2. Leakage Checkは旧Bで英語原稿向けに作られ、校正された。日本語原稿への移植は未校正(誤検知・見逃しの率が不明)。
  3. Voice Cardの自動生成の品質(旧Bは人手作成。自動生成のprimitiveは存在しない=01B §2-1)。
  4. 一人称の体験談の中の**事実創作**を止める機械検出層がX経路にない(RFは事後・非停止)。Writer規則+Voice Card制約+RFで開始し、発生率をTrialで実測する。
  5. Xの音声Runnerが「本文3パート」前提で10箇所以上に固定されている(§③-4)。Yは別の薄い入口を新設する必要があり、実装は「新規runner+共有部品の再利用」の規模になる。
  6. Z会話速度Trial(OPEN-462、ユーザー判断待ち)の結果が出れば、Std 6%減速の扱いはそれに追従する。
- 調査で見つけた訂正1件: ご指示/01Aが`CURRENT_SPEC:1677`とした「M2P0+A方式=PRODUCTION_WIRED」の古い記述は、実際は**`CURRENT_SPEC.md:1692`**(1677は表の見出し行)。KPFT(OPEN-454)で撤去済みの事実に合わせ「(撤去済み、OPEN-454参照)」と注記する最小修正のみ行う(§SSOT整合メモ)。

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
| A09 | Risk Flagger(両Level、非停止) | PRODUCTION_WIRED(X) | `CURRENT_SPEC.md:1185-1192` | 承認原文はX。Zは対象外だがYは事実を扱うためXに近い→A継承(開示)。Voice体験談の創作事実の**事後**検知を担う |
| A10 | Writerの言語三段(日本語原稿→忠実英訳→A2簡易化) | PRODUCTION_WIRED | 01A §2 | 人物性の平板化リスクは未検証(§①-1)。Trialで確認 |
| A11 | Advanced忠実英訳(段落数・順序一致、追加削除なし) | PRODUCTION_WIRED | 01A §2 | 段落数=5を契約にする(T4) |
| A12 | Standard A2調整 | PRODUCTION_WIRED | 01A §2 | 簡易化指示にVoice口調保持の文言はない。Trial観察項目 |
| A13 | 段落境界での決定論分割+段落数不足は1回だけ再生成→STOP | PRODUCTION_WIRED | 01A §2(`split_family_x_article_text_v2`) | 方式を流用し、段落数=5(リード1+Voice各1+最終パート1)で新関数 |
| A14 | Preview(役割文・原則) | PRODUCTION_WIRED | 01A §3 | 各Voiceの立場・結論を先出ししない(Cross-level共通原則CS:1716) |
| A15 | Comment 1〜3の型(次の焦点/回収+次の問い/核心整理+次パートへの橋) | PRODUCTION_WIRED | 01A §3 | X定数は無変更、Y用role定数を**新規定義**(「第1部・第2部」前提文言の除去)。配置はD1推奨に従い§③ |
| A16 | Key Phrase(KPFT全文選定、最大3件、CMU gate、3-ASR投票、K2/P7/P8-KP) | PRODUCTION_WIRED | 01A §3 | 構造非依存で丸ごと継承 |
| A17 | In One Line(基本2文、新事実・結論追加禁止) | PRODUCTION_WIRED | 01A §3 | 要約圧縮層として維持し、最終パートの末尾は要約にしない(D1) |
| A18 | 日本語タイトル(Std) | PRODUCTION_WIRED | 01A §3 | 共通 |
| A19 | TTS backend(gemini-3.8-flash-lite-tts)・Style profile fx_20261017・PD06/S3/E1/K2/P7/P8-KP | PRODUCTION_WIRED | 01A §5 | Full Story相当の5パートはPD06を適用(Voice別Styleは設けない) |
| A20 | Std英語Narration生成後6%減速 | PRODUCTION_WIRED(X/Z) | 01A §5 | Z会話速度Trial(OPEN-462)の結果が出れば追従 |
| A21 | 統一ASR判定(AUW)・値ガード・HR Lock・3層ASR | PRODUCTION_WIRED | 01A §5(U7) | Y配線は既決 |
| A22 | 音声品質検査群(ratio/disfluency/repetition/Connected Speech/PASS_WITH_WARNING) | PRODUCTION_WIRED | 01A §5 | **segment_id対応が必要**(T8、§③-4) |
| A23 | TTS記号正規化、Pronunciation Ledger、PNAP、M1複数発音、多語同音救済、er109(表記違い同音) | PRODUCTION_WIRED / er109はFable受入作業中 | 01A §4 | コード上のscopeリテラル("X","Z")に"Y"を追加するのは技術対応(PM_GOVERNANCE 28-1運用7)でありユーザー判断にしない。**開示**: 該当は`er103_proper_noun_alarm_policy_01.py:42`・`er109_xz_scope_01.py:25`。er109の最終Statusは実装着手時に確認 |
| A24 | retry/fallback/Store/resume(TTS通算3回、KP外側retry、`--regenerate-stage`、Master Audio Store) | PRODUCTION_WIRED | 01A §6 | 上限回数・安全装置を回避しない |
| A25 | Local Rewrite(英語5role)・Connected Speech | PRODUCTION_WIRED | 01A §5 | `resolve_narrative_role`が`full_story_part1〜3`固定(`er020...:131`)。part4/5の追加が必要(加算のみでXに影響しない) |
| A26 | QA gates(style_profile/key_phrase_source/shared narration/Audio Validation Gate)・Assembly・headroom | PRODUCTION_WIRED | 01A §7 | timeline builderはYで新設(T11) |
| A27 | 試聴ページ標準フォーマット+check | 標準(2026-10-18) | 01A §7 | Voice人物名(職業ラベル)は内容として表に載せてよい。内部ID・Voice/Styleの内部情報は載せない |
| A28 | STOPセンチネル/RUN_LOCK | Z方式あり、X未実装(OPEN-354/355) | 01A §6 | 新規Yは**最初からZ方式を採用**(技術選択。判断事項にしない) |
| A29 | routing/pricing登録(未登録modelはfail-closed) | PRODUCTION_WIRED | 01A T17 | Y用キー(Y-B3、Voice Card、Leakage、Y-Writer)を追加登録 |

**A件数: 29**

### B: 旧Bの承認済みVoices固有仕様 → Y構造との整合を確認して継承設計
| ID | 項目 | Status(旧B) | 出典 | Y適用時の注意 |
|---|---|---|---|---|
| B01 | Voice Card起点・具体的状況から書き始める(外側紹介型"For an applicant who..."を使わない) | APPROVED/PRODUCTION_WIRED | 01B §2,§4 | カードは14項目→9項目程度に絞る(D2の中身) |
| B02 | Voice=その立場から"I"で語れる具体的な人物(論点・抽象軸ではない) | 3V方式は2026-09-10承認。原則自体は旧記録で「候補(未承認)」だが原文§2.3がユーザー再確認 | 01B §2-1(DECISION_LOG_HISTORY:8530-8552) | 抽象軸(Business/Legal)Voiceは禁止(4Vで失敗) |
| B03 | Voice本文は一人称"I"/リード・最終パートは語り手 | ユーザー決定2026-09-08 | 01B §4 | 日本語原稿では「私」。忠実英訳で"I" |
| B04 | 語り手の外側要約(narrator analysis)の禁止 | PRODUCTION_WIRED | 01B §4 | リードも最終パートも各Voiceを外から要約しない |
| B05 | 同じ意味を2回言わない | PRODUCTION_WIRED | 01B §4 | Voice内・Voice間・最終パートとの間 |
| B06 | 解決策・コンサル提案の禁止 | PRODUCTION_WIRED | 01B §4 | 最終パートにも適用 |
| B07 | 賛否・陣営の機械割当をしない、2対1陣営化の禁止 | 原文§2.2再確認 | 01B §2-2,§3 | Voice Card生成プロンプトに明記 |
| B08 | 候補A: Voiceは自分の経験・立場に徹する | PRODUCTION_WIRED(2026-09-17) | 01B §3 | |
| B09 | 候補E: 自陣営内の迷い・葛藤・条件付きのnuanceは許容 | PRODUCTION_WIRED | 01B §3 | 境界(OPEN-167)は据え置き(§⑥-2) |
| B10 | 候補C: Voice内の数字は本人の経験に属する数値のみ・最大1つ。外部統計を論証に使わない。「数字必須」要求は撤廃済み | PRODUCTION_WIRED | 01B §5 | Voice Cardに数値・統計欄を持たせない |
| B11 | 候補F: 他Voiceが担う中心懸念は最終パート(または他Voice)に置く | PRODUCTION_WIRED | 01B §3 | Voice Cardに`not_my_point`(他2人の中心論点)欄を持たせ、構造的に境界を運用 |
| B12 | 体験claimの根拠付け(数値・制度・他者の具体的行動は台帳に直接evidenceがあるものに限る。無根拠の未来結果は断定せず感情・判断として書く) | DECIDED(2026-09-12) | 01B §5 | 原文§2.3と一致。Y Writerプロンプトの恒久原則 |
| B13 | Leakage Check項目の考え方(Voice 7項目: evidence_subject/numbers_foreground/narrator_analysis/unknowable_analysis/discovery_syntax/evidence_memorable/position_blur。最終パート側: tension_reverts_to_research/binary_camp_split等) | PRODUCTION_WIRED | 01B §6 | **日本語原稿に対して1回**実行。Closing項目`leak_closing_simple_summary`は最終パートの末尾規則に吸収(C03)。日本語への移植は未校正(§①-2) |
| B14 | Acceptance Gate(是正後も残るflagは後続へ流さない、`LEAKAGE_RESIDUAL_STOP`)、是正上限=初回+2回(計3) | PRODUCTION_WIRED | 01B §6 | 上限3を維持(安全装置を外さない)。是正方式は局所書き換え(下記注) |
| B15 | Tension「共通前提→分岐点→非対称性」(再掲・時系列反復なし、勝者を決めない、Evidence主語禁止) | APPROVED(2026-09-08) | 01B §7 | 最終パートの前半。末尾規則はD1 |
| B16 | Hook(The Question)「3立場を簡潔に提示、結論を先取りしない、企業名・統計禁止」 | PRODUCTION_WIRED | 01B §1-2 | Yのリードに対応 |
| B17 | 軽い会話調トーン(レポート調禁止) | PRODUCTION_WIRED | 01B §4 | Xの最新Writer文体との整合はR0プロンプト設計時に確認 |

注(B14の是正方式): 旧Bは「全文書き直し×3」で、直した箇所の代わりに別Voiceで再発する現象(whack-a-mole)と費用上振れを起こした(Opus L3、01B §6)。Yでは**上限回数(計3)は維持**したまま、是正を「flagされたパートだけの局所書き換え→全体を1回再検査」にする。**Xのテキスト側には局所書き換えは存在しない**(Xの`--only-segments`は音声(TTS)専用で、本文再生成は`--regenerate-stage writer`の全体のみ。`er019_family_x_audio_production_runner_01.py:537`付近、01A §6)。旧Bの局所書き換えは台帳逸脱の言い換え用のみで、Leakage向けはOpusの提案止まり(未採用)。したがってYでは小規模な新規実装になる。これは「検査・回数の追加」ではなく旧B承認済みGateの内部方式変更であり内部実装として扱う(失敗時は旧B方式=全文書き直しへ戻せる)。Opusレビュー論点に入れる。

**B件数: 17**

### C: 不継承(旧仕様・不採用案・不要な独自実装)
| ID | 項目 | 理由 | 出典 |
|---|---|---|---|
| C01 | 2V/4V/可変Voice数対応 | 3V固定(原文§2.2) | 01B C1 |
| C02 | 2V/3Vで別テンプレート・別schema・別pipeline | 重複が不整合の温床(F10)。Yは単一テンプレート | 01B C2 |
| C03 | 独立Closing section、`leak_closing_simple_summary`、Closing語数配分、旧Comment 4の位置(Tension後・Closing前) | 原文§2.1,2.4 | 01B C3 |
| C04 | `voice_fact_safety_gate_mode`(保守版Fact Safety、テーマ依存辞書) | Stage1は実データで効果0、辞書がテーマ依存、runtime evidence未取得。YはX/ZのFact Lockを基盤 | 01B C4 |
| C05 | Fact Attribution A'(`[VOICE_n_EVIDENCE]`出典免除rule) | B10(Voiceに外部統計を語らせない)と思想が逆 | 01B C5 |
| C06 | 外部制約統合(任意の4段目) | 恒久ルール化しない任意パターンと決定済み | 01B C6 |
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
| D1 | 最終パート(Tension+Closing)の中身、尺配分、Comment 4の廃止 | 再定義要素なし+末尾1文の余韻、90〜110語、Comment 1〜3の3本 |
| D2 | Voice Cardの作成方式 | 半自動(Y版B3で視点候補→Card生成AI 1回→Leakage Checkで検査) |
| D3 | 3 VoicesのTTS Voice | 人物別(Z正式表の決定論関数を再利用)。flash-liteで品質が出ない場合のみ再判断 |
| D4 | Writerを「R0のみ」(R1/R2のエンタメ性up Revisionを使わない)にするか | R0のみ |

**D件数: 4**

**合計: 確定(U)8 / A 29 / B 17 / C 13 / D 4**

## ③ Family Yの構造案

### 1. 5パートの役割と境界(日本語原稿は5段落ちょうど。段落=パート)
| # | パート | segment_id(案) | 話者(TTS) | 役割 | 目安(英語語数/日本語字数) | 境界(やってはいけないこと) |
|---|---|---|---|---|---|---|
| 1 | リード | `full_story_part1` | 語り手(Aoede) | テーマ・問題提起・導入。具体的な場面か問いから始める | 40〜55語 / 約110字 | 3人の結論・立場の詳細を先に言わない、統計・企業名なし、結論先取りなし |
| 2 | Voice 1 | `full_story_part2` | 人物1(D3推奨=人物別) | 一人称。冒頭1文で「誰がどんな状況か」が分かる。自分の関心・懸念・守りたいもの | 65〜85語 / 約190字 | 外部統計・調査の説明なし、数字は本人の経験のみ最大1、他2人の中心論点を言わない、解決策なし、他人の具体的行動・制度を創作しない |
| 3 | Voice 2 | `full_story_part3` | 人物2 | 同上(視点はVoice 1と経験・価値観・利害・優先順位が異なる) | 同上 | 同上 |
| 4 | Voice 3 | `full_story_part4` | 人物3 | 同上 | 同上 | 同上 |
| 5 | Tension+Closing | `full_story_part5` | 語り手(Aoede) | 共通前提→分岐点(何を賭けているかの違い)→非対称性→末尾1文の余韻(D1推奨) | 90〜110語 / 約220字 | 各Voiceの再要約・時系列の反復なし、どれが正しいか決めない、新事実・解決策なし、固定修辞骨格(F8)なし |

合計目安: 本文約345〜400語+In One Line約35語 = 380〜435語。Xの実測(Std 385〜434語、Adv 416〜446語、01A §2)の範囲内。**語数・尺はGateにしない**(Xも規定値なし)。観測のみ。日本語原稿は800〜1000字(X実測837〜876字と同帯)。

Voice順: 当事者→遠い立場の順(旧Structure Trial-02の隣接対比、Trial知見で未承認の設計既定値)。

### 2. 学習支援構造の配置(D1推奨に従う場合)
音声順序: Intro → Welcome → Topic intro →(Std: 日本語タイトル)→ Notification1 → Preview intro → **Preview** → Notification2 → Key phrases intro → **KP×最大3** → Notification3 → Full story intro → **Comment1** → リード → **Comment2** → Voice1 → Voice2 → Voice3 → **Comment3** → 最終パート → **In One Line** → Outro。

- Comment 1(次に聞く焦点、答えを言わない)/ Comment 2(リード回収+「3人の違う人物が語る」への橋)/ Comment 3(3人を聞き終えて「なぜ違って感じるか」への視点移動、結論は言わない)。Xの型の再利用でCommentの数はXの4から3に減る。
- Voice 1〜3は連続(Voiceの間にCommentを入れない)。Voice切替の手がかり=冒頭1文の自己紹介的な具体状況(B01)+人物別TTS Voice(D3)+Assemblyの間。**Xが廃止した見出し読み上げ(Point One/Two、Narrator見出し)は使わない**(旧BでF11のASR欠落の原因)。
- In One Line: Xの仕様(基本2文)を維持。最終パート末尾が要約にならないよう制約(D1)することで、「最終パート=関係性と余韻」「In One Line=要点圧縮」と役割を分ける。
- 日本語タイトル(Std)・KPの音声構造(Std: 英語→日本語意味→英語、Adv: 英語→英語解説→英語)はX通り。

### 3. 処理フロー(X経路との差分は太字)
1. Research → Ledger(X通り)
2. **Y版B3**(Storyline1つ+必要最小fact+**3視点候補とVoice別背景fact割当**)→ 決定論B3 producer(数値注記)→ 丸め判断(X通り)
3. **Voice Card生成(AI 1回)**(D2)→ カード間の機械的整合確認(fact_id重複なし、`concern`/`stake`の文言が同一でない=スキーマ水準の確認であり新Validatorではない)
4. **Y Writer(R0のみ、D4)**: Fact Lock+Voice Cardブロック+5段落契約。段落数≠5なら1回だけ再生成、なおダメならSTOP(A13)
5. **Leakage Check(日本語原稿に1回)** → flagがあれば該当パートだけ局所書き換え→全体を再検査(計3回まで)→残れば`LEAKAGE_RESIDUAL_STOP`(B13,B14)
6. 忠実英訳(Adv、段落数5維持)→ RF → A2簡易化(Std)→ RF(X通り)
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
| T4 | 英訳/簡易化 | 既存関数を段落数パラメータ5で呼ぶ | A |
| T5 | Preview/Comment scaffold | Y用role定数(C1〜C3)、context構成を新規 | 新規(型はA15) |
| T6 | KP選定 | そのまま | A |
| T7 | In One Line | そのまま、重複防止は最終パート側の制約で吸収 | A |
| T8 | segment ID→role解決 | `full_story_part1〜5`を採用すると、`--only-segments`正規表現(`full_story_part[1-9]\d*`、runner:537)は**既に通る**。`resolve_narrative_role`(`er020...:131`)のpart4/5追加のみ必要(加算・Xに影響なし)。disfluency/repetition QAの範囲リストは実装時にGrepで全洗い出し | A+小改修 |
| T9 | TTS segment生成・Voice割当 | Y用generator。人物別VoiceはZ `assign_dialogue_voices`(決定論)を再利用(D3) | 新規+A |
| T10 | Style profile | `fx_20261017`をそのまま(Full Story相当=PD06)。OPEN-415(X/Z/Y横断エンジン化)は、Voice別Styleを持たない限りトリガーしない | A |
| T11 | Assembly timeline | Y用builder(新規) | 新規 |
| T12 | 試聴ページ | `render_standard_page`+Y用page script(Voice人物名を内容ラベルとして表示、内部ID非表示) | A+新規 |
| T13 | scope限定機構 | リテラルに"Y"追加(技術対応、開示済み=A23) | 技術対応 |
| T14 | RF | 採用(A09) | A |
| T15 | STOP/RUN_LOCK | Z方式を最初から採用(A28) | A |
| T16 | 来歴契約(U-1) | Y用`chain_method`を定義(U-1の拡張) | 新規(小) |
| T17 | routing/pricing | Y用キー追加登録 | 新規(小) |

## ④ 過去の品質NGと対策の対応表(旧B F1〜F12)

| ID | 旧Bの事例・原因 | 承認済み対策 | Y適用方針 | 残存リスク | §6対応 |
|---|---|---|---|---|---|
| F1 | Trial-04: 調査報告調で数字連続。Voice Cardなし・Evidence主役 | 一人称(09-08)、Voice Card起点、候補C | B01/B03/B10。Card起点を踏襲。Cardは自動生成(D2) | Card品質に依存(自動生成は未実証) | (1) |
| F2 | Trial-05: 語り手がVoiceを外から要約(6/6) | 一人称化でFAIL消失(Trial-06以降)、narrator_analysis項目 | B03/B04。リード・最終パートも各Voiceの外側要約禁止 | 日本語での判定校正が未実施 | (1) |
| F3 | 4V: 抽象軸Voice(Business/Legal)が制度解説へ逆戻り | 3V・具体的人物、外部制約はTension側へ | B02/C01 | 低(人物化で2 attemptで0件) | (1)(2) |
| F4 | 3V汎用化: 「数字を織り込め」命令とEvidence主語禁止の二律背反→whack-a-mole、全文書き直しで別Voiceに再発 | 候補C(数字必須撤廃)、「数字は本人経験のみ最大1」 | B10。Voice Cardに数値・統計欄なし。是正は局所書き換え(B14注) | 局所書き換えの有効性は未実証(Trialで実測) | (1)(5)(6) |
| F5 | Tension非対称性文(3人の役割・権限差の断定)が台帳逸脱検査(Ledger Deviation Checker)でMAJOR化、hedge増量で収束せず | (旧Bでは未解決のまま構造的衝突) | **Xには逸脱Checkerが存在しない**(2026-10-10撤去、`CURRENT_SPEC.md:1194`、01A §1)ため衝突の前提が消える。非対称性文はVoice Card・選定factに既に書かれた立場関係だけで書く(新事実導入なし)規則+RF(非停止)。→ 判断事項にしない | RFが当該文をflagしても人の確認待ちリストに入るだけで停止しない | (5) |
| F6 | PN A2旧版: Voiceが統計引用、立場が曖昧。上限後も「前例踏襲」で試聴へ流していた | 候補A/C/E/F、`leak_position_blur`、Acceptance Gate(残存は後続へ流さない) | B08〜B11/B13/B14 | Gateは流出防止であり原因解消ではない。局所書き換えで収束しない場合は止まる(安全側) | (1)(2)(6) |
| F7 | PN A2新版: 肯定派Voiceが相手の中心懸念を語る(許容) | 候補E/F、position_blur | B09/B11。Voice Cardの`not_my_point`欄で構造的に運用。**OPEN-167は据え置き**(判断事項にしない、§⑥-2) | nuance境界とユーザー知覚のずれ。Trialで頻度を実測してから判断 | (3) |
| F8 | Closingの修辞骨格が4/4同型。記事間類似を測るQAなし | (Closing廃止=原文) | D1推奨: 再定義要素なし、固定骨格をプロンプトの禁止例にする。最初の3記事で人が横並び比較(検査は追加しない) | 記事間類似の機械検知はなし | (4) |
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
| (5) 体験談の事実創作 | 検査層が薄い(RFは事後・非停止、Xの決定論ゲートは数字中心) | B12+Fact Lock規則1〜4+Voice Cardに「数値・制度・他者の具体的行動は書かない」制約+RF(A09)。Trialで**台帳に無い一人称の事実主張の数を人が全件確認**(基準=0件) | なし。**発生した場合のみ**Leakage Check既存callに1項目追加する案を、その時点で提示(D候補として予告) |
| (6) 検査・書き直しでも収束しない | 局所書き換えは未実証 | 上限計3回を維持、局所書き換え、Acceptance Gateで止める、内容理由の無制限retryは設けない(X思想と整合)。構造起因は「Card/Fact割当の問題」として前段(Card/B3)へ戻す判断を人が行う | 局所書き換え(内部方式) |

## ⑤ QCD評価

出典: X実測(`docs/research/FAMILY-X-NEWS-2ARTICLES-E2E-01/RESULT_01.md` §5、01A §9-1: 記事A 54.06円/記事B 131.61円、読み調査1回限りを除く定常平均約75.3円)、旧B実測(2V新規topic 1セット99.01円[TTS除く]、3V Writer 1 attempt約24.3〜28.3円、01B §9)。**以下の増減額は推定(実測ではない)**。算出根拠: Writer R0〜R2=16.55〜17.13円で1 callあたり約5.5〜6円(R0は入力が大きいので6〜8円と見る)。

### 費用(円/セット、Xを基準とした増減の推定)
| 要因 | 増減(推定) | 根拠 |
|---|---|---|
| Voice Card生成 1 call | +2〜5 | R0より入力が小さい |
| Y版B3の出力増(3視点+割当) | +0.5〜1.5 | 呼出回数は増えない |
| Leakage Check 1 call(日本語原稿+Card) | +2〜4 | 判定JSON出力。モデル未確定(Sol/Lunaの差) |
| 局所書き換え+再検査の期待値 | +1〜3 | 是正1回の確率を40〜50%と仮定(旧B: Trial実績はattempt1〜3まで分布) |
| R1/R2を使わない(D4) | **-9〜-11** | R0〜R2のうちR1,R2の2 call |
| Comment 4廃止(D1) | -0.2〜-0.5 | scaffold+TTS 1本 |
| 本文TTS/ASR(語数同等、5パート) | ±0〜1 | 総語数はX実測と同帯。per-call overheadの差 |
| 人物別TTS Voice(D3推奨)がflash-liteで可 | 0 | 同モデル、Store再利用は本文に効かないため差なし |
| 同、flash-liteで品質不足でPro TTSが必要な場合 | +12〜18 | `pricing_snapshot.json`: Pro 音声出力$20/Mトークン vs flash-lite $6/M(Standard同期)=3.3倍を本文TTS分(X TTS 11.3〜12.7円の6割強と仮定)に適用 |
| **合計(D4採用、D3=flash-lite)** | **約-5〜+6** | 記事A型で約48〜60円、記事B型で約126〜137円、定常平均約70〜81円(X 75.3円±6) |

- D4を不採用(R1/R2維持)なら+約9〜11円(定常平均約85〜92円)。Pro TTSが必要なら更に+12〜18円。
- **旧B比**: Y追加分のWriter段(Card+R0+Leakage+局所書き換え期待値)は約11〜20円で、旧B 3V Writer 1 attempt(24〜28円、Fact Checker A'のWeb検索・Ledger Deviationを含む)より低い。旧Bの「flaggedで全文×3」(上限約78円)に相当する上振れを局所書き換えで避ける狙い(未実証)。
- 70円目標に対し: 差の主因はXと同じResearch(web検索)費の記事間変動(X記事B 42.8円 vs 記事A 11.1円)で、Yの構造差分では悪化しない見込み。改善余地(Trial後に検討): Card生成をB3 callへ統合(-2〜-4円)、Leakage判定のモデル軽量化、Research再利用。Charter 3により原価増となる要素は上表のとおり必要性を確認済み(Card=人物性の源、Leakage=旧Bで品質NGを止めた承認済みGate)。

### 品質 / 開発工程(D)
- 品質: 旧B承認済み対策(B01〜B17)で§6の(1)(3)(5)の主要因をカバー。残るのは意味的な重複(2)(4)と創作事実(5)の検出層の薄さで、Trialで実測してから追加判断(追加する場合はD)。
- 開発工程(推定): 実装(DEV、API 0)は独立に並列化できる4束 ── (a)Y版B3・Card・R0・Leakage・局所書き換え(Writer系)、(b)Y用plan/segment/timeline/Comment role(音声系)、(c)scope追加("Y")・pricing/routing登録・segment_id拡張とテスト、(d)試聴ページ+check。X経路の大半を再利用するため新規コードは限定的(規模は概算でSonnet 3〜4委任単位=推定)。最大の遅延要因は設計判断(D1〜D4)の確定待ちと、テーマ選定(新規記事テーマはユーザー選定=PM_GOVERNANCE 13節)。
- 先行可能: 設計承認前でも(c)(d)の共通部品調査と、テーマ候補(英語/日本語/選定理由付き)の作成は並行可能。

## ⑥ ユーザー判断事項(D、4件・目標6件以内)

各項目は「既存仕組みで解決できないか」「過去に解決済みでないか」を確認済み。

### D1. 最終パート(Tension+Closing)の中身と、Comment 4の扱い
- 決まっていること: Tensionは「共通前提→分岐点→非対称性」を継承、独立Closing廃止、再要約や冗長な追加は避ける(原文§2.4)。
- 新しい判断が必要な理由: 旧Closingの「問題の見え方の再定義」を最終パートに残すか、Comment 4(Xでは全体の意味回収+In One Lineへの橋)をYで残すか。原文に指定なし(新しい編集仕様)。過去に解決済みではない(旧Bは独立Closingの再定義で承認、F8で同型化が出て、ユーザーが独立Closingを廃止)。
- **推奨**: (a)再定義の独立要素は置かない。最終パートは「共通前提→分岐点→非対称性」+**末尾1文の余韻**(リードの具体場面または未決の問いに戻る。要約・勝者・解決策・固定修辞骨格は禁止)、90〜110語。(b)**Comment 4は廃止し、Commentは1〜3の3本**。
- 理由: Comment 4の役割(意味回収+In One Lineへの橋)を残すと「最終パート→Comment 4→In One Line」で3重の締めになり、原文§6(4)の重複を設計で増やす。In One Lineが要点圧縮、最終パートが関係性と余韻、で分担できる。
- QCD: 費用-0.2〜-0.5円、尺-約15秒。リスク: 締まりが弱くなる可能性。Trialで**Comment 4あり版も並置**してA/B試聴(追加費用は約0.5円=Comment 4のTTS 1本。再組立のみで他は再生成しない)。
- 代替案: (a')再定義1〜2文を残す(旧Closing継承、尺+10〜15語)、(b')Comment 4を残す。

### D2. Voice Card(人物設計)の作り方
- 決まっていること: 3つの異なる視点を設計し、各Voiceは独立した人物(原文§2.2,2.3)。旧Bは人手作成で、自動生成のprimitiveは存在しない。
- 新しい判断が必要な理由: 量産(17記事構成にY 3記事)での工数・品質に直結する運用方式の選択で、旧Bに先例がない。
- **推奨(費用最小の半自動)**: ①Y版B3(X B3の枠組み、呼出回数は増えない)が「3視点候補(職業/立場ラベル、何が異なるか、賛否の機械割当禁止)とVoice別の背景fact割当」を出力 → ②**Voice Card生成をWriter前段のAI 1回**で実施(項目は旧14→9: 人物ラベル/性別[D3用]/状況+具体場面/必要/自分側の懸念/守りたいもの/制約/賭けているもの/`not_my_point`[他2人の中心論点]、+背景fact id 0〜1。数値・統計欄なし)→ ③Leakage Checkで検査。**量産時の人手ゲートなし**。最初のTrialだけFableがCardを目視評価。
- QCD: +2〜5円/セット(B3出力増+0.5〜1.5円は別)。人手方式は記事ごとに判断工数が発生しスケールしない。リスク: Card品質の劣化(F1/F3の源)。緩和: 視点選定基準をプロンプトに内包、Trialで評価。
- 代替案: 毎記事を人手でCard作成(品質上限は高いが工数大)。
- 注: ご指示にあった「B3で決定論的に出す」は、B3がAI判断のため「スキーマ検証付きで出力」と読み替えた(fail-closed契約V1〜V10と同じ形式で検証)。

### D3. 3 VoicesのTTS Voice(声)
- 決まっていること: Voice編集思想=各Voiceは独立した人物(原文§2.3)。XのStandardは語り手Aoede単独、見出し読み上げは廃止(01A §5)。旧Bは人物別Voice(Algieba/Erinome/Schedar)で承認(2026-09-08)、Zは登場人物Voice正式表(男女各5・初出順・循環、決定論関数、2026-10-23ユーザー最終決定)。
- 新しい判断が必要な理由: Yにどちらを適用するか未指定。聞き分けとコストに影響。
- **推奨: 人物別Voice**(Voice 1〜3のみ。リード/最終パート/Comment/Preview/In One Lineは従来の語り手Aoede/Charon)。Z正式表の決定論関数`assign_dialogue_voices`を再利用(性別はVoice Cardの明示項目で、名前からの推測はしない=Z規則と整合)。
- 理由: 見出しなしの連続する3人の一人称を、文面の自己紹介だけで聞き分けるのは難しい。旧BもZも人物別を承認済み。新たなVoice仕様は作らない。
- 費用差: 同じTTS model(flash-lite)で品質が出れば**±0円**。人物別Voiceがflash-liteで品質を満たさずPro系TTSが必要な場合は**+12〜18円/セット(推定)**となるため、その場合は結果を添えて再判断を求める。Trial評価項目に含める。
- 代替案: Aoede単独(費用差0、実装最小、聞き分けは自己紹介文のみ)。Std 6%減速のVoice別適用はOPEN-462結果に追従。

### D4. WriterをR0のみにする(R1/R2のエンタメ性up Revisionを使わない)
- 決まっていること: XのWriterはR0→R1→R2(R1/R2は「もっとエンターテインメント性の高い記事に」)でX承認済み。Yへの適用承認はない。
- 新しい判断が必要な理由: OPEN-217(2026-09-28)が「対処方針をユーザーが判断する」としたまま未決。Y Trial-01でX流R1→R2をVoice文脈へ適用すると旧Leakage fail-fieldが**2→3→11に悪化**し、AI評価(rubric)は改善と誤判定(OPEN-218)。品質と費用のトレードオフがある。
- **推奨: Y初期はR0のみ**。人物の面白さはVoice Card(具体的な状況・葛藤)で担保する。
- QCD: 費用-9〜-11円/セット(推定)、検査負荷減。リスク: Xより読み物としてのエンタメ性が低い可能性→Trial試聴で確認し、不足ならR1のみを追加する案を別途提示。
- 代替案: X通りR0→R1→R2(+9〜11円、Leakage悪化リスク。OPEN-217の根拠から非推奨)。
- 採用された場合、OPEN-217はY側の方針として確定(close候補)。

### ⑥-2. 判断事項にしなかった候補とその理由(判断水増し防止のための開示)
| 候補 | 判断不要とした理由 |
|---|---|
| nuance許容境界(OPEN-167) | 原文§2.3が方針(自陣営内の迷いは許容、他Voiceの中心論点は抱え込まない)を確定。厳密さの線引きだけが未決で、旧B承認済みA/E/F+position_blur+新設の`not_my_point`欄で開始し、Trialで頻度実測後に判断(OPEN-167はDEFERREDのまま)。今回は判断不要 |
| Tension非対称性×台帳逸脱の構造衝突 | Xに逸脱Checkerが無く前提が消える(F5)。非対称性文はCard/選定factの範囲に限る規則で足りる=既存規則内 |
| 総尺・語数 | X実測(385〜446語)を基準に配分(§③-1)。Xが規定値なしなので踏襲=判断不要 |
| 丸め判断/RF/PNAP等の「承認原文Xのみ」項目 | 当時Xが唯一のニュース系だったことによる限定で、Voicesの性質と衝突しない→A継承・開示 |
| er109等のscopeに"Y"追加 | 28-1運用7の技術対応・開示のみ |
| Leakage Check(日本語原稿1回)/局所書き換え | 旧B承認済みGateの流用と内部方式変更(上限3維持) |
| 事実創作検査の追加 | 今回は追加しない。発生時のみ既存call項目追加案を提示 |
| STOP/RUN_LOCK方式、試聴ページ、segment_id | 技術選択・内部実装 |
| Voice選定基準(Trial-06の「主要な意見から順/同一群内の違い」) | 恒久規則ではなくTrial基準(01B §12未確認)。B3プロンプトの設計入力として使い、新規仕様化しない |

## ⑦ 次工程: 最小Trial計画案(実施は別途承認)

- **前提**: 設計確定(D1〜D4)とOpusレビュー後。新規記事テーマは**ユーザーが選ぶ**(Fable/Claudeは候補を英語・日本語・選定理由付きで提示するのみ)。候補基準: 複数の当事者が一人称で語れる論点、X経路のResearchで台帳が作れる、統計を前提にしない。
- **対象**: 1テーマ、Std/Adv各1本(1記事セット)。X経路+Y差分のDEV実装(Production非配線。flagの扱いは別途設計)。
- **2段階で1回のTrial**: 段階1=テキスト(Research〜日本語原稿〜Leakage〜英訳/簡易化〜RF)、評価して合格なら段階2=音声(Preview/Comment/KP〜TTS/ASR〜Assembly〜試聴ページ)。段階1で構造起因のNGが出た場合は音声費用を使わず止める。
- **費用見込み(推定、§⑤の増減とX実測から)**: 段階1 約30〜76円(Research 6〜27+Ledger 5〜16+B3 7〜9+Card 2〜5+R0 6〜8+Leakage 2〜4+局所書き換え期待値1〜3+英訳/簡易化0.6〜1+RF 1.3〜1.6)、段階2 約18〜27円(scaffold 1.3〜2.9+TTS 11〜13+ASR 6〜11)。**合計約48〜103円**。人物別VoiceがPro TTSになる場合は+12〜18円。再試行余裕を含め**上限150円**を提案(案件見積300円以下だが新仕様/未承認Trial範囲のため承認が必要=PM_GOVERNANCE 7-7)。
- **評価項目**:
  1. 構造: 日本語原稿が決定論分割で5段落、Adv/Std段落数一致、segment_id・検査範囲の網羅。
  2. 尺・語数: 観測(X実測帯との比較。Gateにしない)。
  3. Voiceの人物性: Leakage 7項目+最終パート項目のPASS(attempt数と是正方式の有効性を記録)、Adv/Stdで口調・迷いが保たれているか(Fable+ユーザー試聴)、Cardの目視評価。
  4. 重複: 3Voiceの意味的重複(人)、最終パート対Voiceの語彙overlapを監視のみ(API 0)、最終パート末尾が固定骨格でないか。
  5. Tension: 再要約・時系列反復・新事実・勝者決定がないか、D1(再定義なし)の締まり、Comment 4あり/なし並置のA/B試聴。
  6. Fact Safety: 台帳に無い一人称の事実主張を人が全件確認(基準=0件)、RF flag数・内容、Std/Advの不整合。
  7. 音声QA: 既存gate(Audio Validation、ASR 3層、HR Lock、値ガード)、人物別Voiceの品質と費用(D3)、Std 6%減速(OPEN-462追従)。
  8. 実費の記録(推定値との比較、段階別)。
- **成功基準(既存の承認基準のみ)**: Leakage Check項目がAcceptance Gate(上限3、残存なし)を通る / Fact Lock・RFの既存基準 / Audio Validation Gate全PASSでHR Lock 0 / 事実創作0件 / 最終判定はユーザー試聴。語数・尺・費用は合否に使わず記録して次判断に使う(新基準を作らない)。
- **STOP/撤退**: Leakageが上限3で収束しない場合は止め、前段(Card/B3)の問題として原因を整理(音声費用を使わない)。

## SSOT整合メモ

- CURRENT_SPECは**変更しない**(未承認案を正式仕様として書かない)。例外=`CURRENT_SPEC.md:1692`の古い記述への注記のみ。
- 未承認案(本書のD1〜D4推奨、局所書き換え、R0のみ、Y用B3プロンプト等)はOPEN_ITEMSに「判断待ち候補」として記録し、確定済み基本方針(原文§2=U1〜U8)と分けた。
