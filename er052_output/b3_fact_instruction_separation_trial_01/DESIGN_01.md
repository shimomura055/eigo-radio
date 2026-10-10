# DESIGN_01: 根本対策候補の設計(Phase 1、設計のみ。Production不変更)

目標: Fact/指示分離のための**追加LLM call 0**(既存B3 call内、または決定論)。後段AI(新Checker・二重チェック・A/B統合・多数決・補正AI)は一切増やさない。上流構造で解決する。
前提(INVESTIGATION_01.md): 台帳は既に欄が分離済み。混ざるのは工程4(B3の自由記述brief)だけ。R1/R2はbriefを見ない=影響するWriter入力はR0の「ニュース欄」のみ。

## 1. 候補の整理

| 案 | 概要 | 追加call | 決定論性 | 変更箇所(Trial実装先。Production不変更) | 状態 |
|---|---|---|---|---|---|
| **D(第一候補)** B3は「選ぶ」だけ・briefは決定論で組む | B3 LLMは従来どおり`selected_storyline`/`selected_fact_ids`/4テストを出す。`selected_fact_brief`(自由記述)は使わず、採用fact_idの台帳`claim`(出典リンク除去)を1 fact=1行で並べて`## Selected Facts`を決定論生成。`notes_for_writer`は別ブロックへ決定論転記 | 0(B3 callは従来どおり1回、むしろ出力が減る) | 完全に決定論(同じ選定結果→同じbrief) | Trial: `b3sep_trial_01.py`(新規、本ディレクトリ)で既存`selected_fact_ids`をreplay。Production採用時: `build_selected_brief_markdown`(er019 L252)置換+Promptの手順5/schema `selected_fact_brief`(L68, L78, L117)の削除 | 設計済み・¥0予備検証済(5. 参照) |
| **A'** Prompt変更(Factのみ) + 制約は決定論転記 | B3 Promptを「`selected_fact_brief`にはFactの記述文だけを書く。注意・禁止・指示は書かない。冒頭のStorylineは含めない」に変更。注意文は台帳notesを決定論で別ブロックへ転記(LLMに書かせない) | 0(同一call) | brief本文はLLM任せ(確率的)。制約側は決定論 | Trial: B3 Prompt/schemaの**コピー**を本ディレクトリに置き差替え(Productionファイル不変)。Production採用時: er019のPrompt変更=ユーザー判断 | 設計済み |
| B 後処理で文を正規表現分離 | 既存briefを文単位に割り、命令形パターンを別欄へ | 0 | 決定論だがパターン依存 | 後処理module新規 | **非推奨**: 言い換え文に追随できない(例: 「分けて扱う」「帰属させない」の語尾が毎回違う)、事実の確かさの限定文(「…確定した事実ではない」)を誤って剥がすと意味を壊す、BYD型の「落ちたnotes」を戻せない、briefの主体・対象ずれ(言い換え)を直せない。評価用の検出器としてのみ使う |
| C notes経路の復旧(単独) | Writerへ台帳notesを別経路で渡す(B3 briefには入れない) | 0 | 決定論 | runnerのR0入力組立 | 単独では不十分(B3が自由記述でnotesを取り込む挙動は残る)。**DとA'の制約側部分として内包** |
| E Researcher側で欄を分ける | `notes_for_writer`を`writer_constraints`/`fact_qualifiers`に分割 | 0 | Researcherの確率的出力 | Researcher schema/Prompt | **STOP候補**(Research仕様変更)。台帳が既に分離欄を持つため不要と判断 |

## 2. 第一候補D の詳細

### 2-1 Selected Facts(Fact側)
- 採用fact_id(B3が選定した`selected_fact_ids`)ごとに1行:`- {claim}`。出典リンク`([host](url))`は除去(space_weaponsのclaimにmarkdownリンクが含まれることを確認)。
- 欄の扱い:
  - `claim` = 常にFact側。
  - `scope`/`conditions` = 事実の範囲・条件の記述なのでFact側候補(D-minは含めず、D-fullは含める)。**Trialで2変種を比較**(長さ・Writerに必要な情報)。
  - `numeric_value`/`date_or_period` = 数字の根拠欄。claimに既に入っているため既定ではFact側に追加しない(注記・数値印のサイドカー側で使用される欄)。
  - `ambiguity_note`(AMBIGUOUS fact) = 記述文(確かさの限定)。**Fact側の補足行**として`- {claim}`の直後に置くか、制約側に置くか → **Fable判断事項(Q3)**。
- 1 fact=1行のため`【事実N】`とfact_idが**1:1**になる(現行は5 factが1段落に統合され単一`【事実1】`になるテーマあり=semiconductor)。注記工程の「事実の境界」問題(Luna central_bankの中核数値落ち、byd文途中分割)が構造的に消える。

### 2-2 Writer Constraints(制約側)
- 採用fact_idの`notes_for_writer`を**逐語**で並べる:`- ({fact_id}) {notes}`(リンク除去のみ)。LLMは触らない。
- ブロック見出し(例): `【Writerへの注意(事実ではない。台帳のnotes_for_writerをそのまま転記)】`。
- Storyline行(`selected_storyline`)はB3 LLMの出力のまま維持(Writerの「テーマ：」行になる既存仕様)。ただしStoryline内の書き方指示(space「誇張せず整理する」)は残りうる → 対象外(Q4)。

### 2-3 Fact Lockへの受け渡し(配置の2案)

| 配置 | 内容 | 長所 | 短所 |
|---|---|---|---|
| **P-out(推奨)** | `selected_brief.md`はStoryline+Facts(Factのみ)。制約は別artifact(`writer_constraints.md`、`full_ledger.json`と同じ`storyline_b3/`配下)。runnerがR0呼出直前に`facts = brief_facts + "\n\n" + constraints_block`として連結し`jaw.run_ja_writer_o_r1_r2(storyline, facts)`へ渡す | `selected_brief.md`の形式が現行契約のまま(注記契約V1〜V10、`parse_brief_md`、注記仕様v2の「Selected Facts節の全行が`- 【事実N】`」と矛盾しない)。R0 Promptテンプレートは**不変**(`[ニュース]`欄に入る文字列が増えるだけ。規則4「ニュース欄に〜断定しないとあることは守って」は成立) | runnerのR0入力組立にコード変更が1箇所(Prompt文言ではなくデータ連結)。Lane A(委任_07進行中)の実装と競合しうる→調整要 |
| P-in | `selected_brief.md`に`## Writer Constraints`節を追加 | artifactが1つ | 注記契約V4(`parse_brief_md`)・V5(Facts節全行が`FACT_LINE_RE`)・V10(Facts連結一致)の定義を節認識に改める必要=W-1入力契約の変更(Lane A設計v3.1に介入) |

Writer R0のFact Lock規則との整合(静的確認済): 規則1は「ニュース欄の各事実の行頭の【事実N】」に出典タグを付ける。制約行は行頭タグなし=事実ではないことがPrompt上も自然。規則3「ニュース欄に書かれていないことは書かない」「分からないことを推測で埋めない」、規則4「〜ではない・断定しないとあることは守る」は制約ブロックがニュース欄にあることで満たされる。**Writerが制約行に`【事実N】`を付ける・制約文を記事に引用する可能性**は静的には排除できない→ 任意の有料R0少数確認(PREREGISTRATION 5-3)で測る。

### 2-4 W-1 / 既存仕様との整合性
| 仕様 | 影響 | 評価 |
|---|---|---|
| Fact Lock R0 Prompt(`FACTLOCK_R0_BLOCK_HEAD` L53) | 不変(データ連結のみ) | 問題なし。"W-1 Prompt改変禁止"に抵触しない |
| 注記契約V1〜V10(DESIGN_03 3節) | P-outなら不変。briefがFactのみで注記対象が単純化(V5/V10は更に満たしやすい) | 問題なし(P-in時は要契約拡張) |
| B3注記仕様v2 | 「限定する文は直前の主張と同じ事実」規則は、Factのみのbriefでは該当文が減る。仕様改訂不要、むしろ「Storyline：」「素材:」除外規則が不要になる | 問題なし |
| Standard/Advanced・Key Phrase | briefはR0入力のみ。Key Phraseはfinal本文由来 | 影響なし(静的確認) |
| JA Fact Check / must-fix | 台帳全文を直接読む(notes込み) | 不変 |
| B3 4テスト・Fact数目安・recheck_note | 不変(Dは選定ロジックを一切変更しない) | 問題なし |
| B3の「brief本文はLLM出力」(ユーザー確定事項(7)の読み方) | Dはbrief本文を決定論生成に変える | **仕様変更に当たる可能性 = ユーザー判断(Q1)** |

## 3. 副次的に解消/悪化するもの(Trialで測る)

解消見込み: ①命令文混入(構造的に0。ただしClaim内に命令形が元から無いことは予備検証で確認、5.参照) ②B3のbrief言い換えによる主体・対象ずれ(Dはclaim逐語) ③`Storyline：`/`素材:`重複行の特殊規則 ④5 factが1段落へ統合される問題(1 fact=1行) ⑤BYD型の「notesがWriterに届かない」(Dは採用factのnotesを常に届ける)。
悪化/要注意: ⑥Writer入力が長くなる(openai 570→1,007字、space 596→617、semiconductorは314→274と短縮)=R0トークン増はごく小(ただしWriterの要約・Storytellingの出来は変わりうる→Writer出力品質はこのPhase 2では主評価にしない。回帰方向の変化がないかを人間確認用に少数のみ出す選択肢) ⑦notesに混じる記述的限定(central_bank F003など)が制約側へ移る → 事実本文だけを根拠にするタグ照合(`PAIR_PROMPT`は`facts_map`のFact行のみ参照)で限定が見えなくなる可能性 → **D-full+ambiguity_noteのFact側補足**の設計余地を残す(Q3) ⑧B3注記工程の完全不要化はこの案では**証明されていない**(数値印の中核/周辺付与は残る。ただし【事実N】付与とledger_ids対応は決定論化できる=別管理ID候補) ⑨Dの「完成記事の読み物としての面白さ」への影響は未測定。

## 4. A'(Prompt変更案)の詳細(Trial対照)

- 目的: 現行仕様(brief=LLMが書く文章)を維持しつつ、混入だけを止められるか。
- 変更(Trialコピー上): 手順5を「Selected Fact Briefは**事実の記述文のみ**。注意・禁止・書き方の指示、台帳に無い確かさの限定、Storyline行の再掲は書かない。注意事項はシステムが台帳から別途付ける」へ。schemaは不変(フィールド追加なし)。
- 制約側は案Dと同じ決定論転記(LLMが書いた注意は捨てる/検出する)。
- 弱点: LLMがPromptに従う保証はない(評価指標E1で測る)。従わない場合に後段で補正AIを足すのは禁止なので、**従わなければA'は不採用**。
- 利点: B3出力の読み物性は維持。仕様変更の程度がDより小さい(Prompt1箇所)。

## 5. 予備検証(¥0、本Phaseで実施済み)

`preview_armD_01.py`(既存9テーマの`selected_fact_ids`をreplay、API不使用)→ `armD_preview_summary_01.json`・`armD_preview_01/<theme>__brief.md|__constraints.md`:
- 9/9テーマで `parse_brief_md` 成功、`dryrun_annotate`(runnerの決定論仮注記)が成功し`【事実N】`数==採用fact数(1 fact=1行が成立)。
- Fact行内の命令形パターン検出 0件/9テーマ(現行briefは問題5テーマで10件)。
- 出典リンクmarkdownの残存 0(除去regexで足りる)。
- 制約ブロック件数 = 採用factのnotes件数(BYD 4件=現行briefで届いていなかった分が復活)。
限界: これは**機械的に通ることの確認**であり、Writer出力の質や、限定文の移動によるFact Lock照合への影響は未測定。

## 6. コスト・時間・複雑性(根拠付き)

- D: 追加call 0。B3 callは従来通り(実測¥0.38〜0.60/call、平均¥0.50、約50秒; `stage_r/cost_by_theme.json`)。`selected_fact_brief`をschemaから外せば出力がわずかに減る(未測定)。実装: assembler 1関数+runner連結1箇所+テスト。
- A': 追加call 0。Prompt1箇所+制約転記。
- 注記コスト(B3注記Sonnet約¥15.7/記事)の削減可否は、Dで【事実N】付与が決定論化できるかに依存(別管理ID候補)。

## 7. Production採用時に必要な変更種別(Trial結果次第、現時点では実施しない)

| 変更 | 種別 | 承認 |
|---|---|---|
| er019 `build_selected_brief_markdown`置換+B3 Prompt手順5/schema変更(D) | Production Prompt/code変更 | **人間ユーザー承認必須**(`USER_DECISION_REQUIRED`) |
| runnerのR0入力へ制約ブロック連結(P-out) | Production code変更 | ユーザー承認+Lane A調整 |
| 注記契約の節拡張(P-inの場合のみ) | W-1入力契約の変更 | ユーザー判断 |

## 8. Opus独立技術レビューGate

「新しい構造・処理フローの設計」(PM_GOVERNANCE 11-3条件A)に該当する。**Phase 2実装前にOpus独立レビューを推奨/必須**(Fable手配。本委任ではOpusを起動しない)。

## 9. 新仕様候補の報告(実装しない)

①B3 briefの決定論生成(D) ②制約ブロックをR0ニュース欄へ別連結 ③`ambiguity_note`の置き場所 ④ledger txtがVERIFIED factのResearcher`ambiguity`を印字しない件(情報欠落の可能性、別件) ⑤notesのうちLedger内部向け文言(「Ledger上では必ず…」HF-007)の扱い。いずれも未承認の新仕様候補。
