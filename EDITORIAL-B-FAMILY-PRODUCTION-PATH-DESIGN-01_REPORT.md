# EDITORIAL-B-FAMILY-PRODUCTION-PATH-DESIGN-01 報告書

**管理ID: EDITORIAL-B-FAMILY-PRODUCTION-PATH-DESIGN-01**
**種別: 設計案のみ(コード・Prompt・SSOT・出力ファイル変更ゼロ)**
**作成日: 2026-09-08**

**本タスクでは一切の実装・編集・API呼び出し・Git操作を行っていない。以下はすべて
設計案であり、ユーザーレビュー前に実装しない。**

---

## 0. 参照した既存資料と本タスクの位置づけ

- `ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02_REPORT.md`(git未追跡)、
  `ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md`(git未追跡)
- `CURRENT_SPEC.md`(2026-09-08 PM-CLOSEOUT-CONSOLIDATION-05エントリ、冒頭)
- `OPEN_ITEMS.md` OPEN-112行(2026-09-04追記:
  `OPEN-112-EDITORIAL-TYPE-PRODUCTION-RECONCILIATION-AUDIT-01/TOPIC-SSOT-AND-FAMILY-FRAME-02/CONTEXT-RECONCILIATION-03`)
- `EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FIX-TRIAL-10_REPORT.md`
- 実コード: `er003_v1_n3_01_articles_generate.py`、`er003_v1_sing01_news_tail_fix.py`、
  `er003_b1_p9a_audio.py`、`er003_v1_sing01_point_headings_aoede.py`、
  `er012_editorial_b_voices_trial_07.py`、`er012_editorial_b_voices_trial_09_audio.py`、
  `er012_editorial_b_voices_trial_09_heading_regen_03.py`、
  `er012_editorial_b_voices_trial_10_comment1.py`

**【重要・既存文書との整合確認結果】** `OPEN_112`行(2026-09-04追記)は、ER-010の
2文書を「正式仕様として採用せず、参考資料(design reference only)として扱う」と
ユーザーが明示的に判断したことを記録している。したがって本設計案は、ER-010の
2文書を**そのまま正式SSOTとして前提にはせず**、参考設計として引用しつつ、
2026-09-08時点の実コード読み取りで再検証した内容を優先している(矛盾があれば
実コードを優先し、下記で個別に明示する)。また同OPEN-112行は「A Family(Discovery/Why
+News/Trend)を優先し、B/C群の詳細設計はA群の結果が出るまで保留」とも記録しているが、
2026-09-08のユーザー承認4項目はこの保留方針とは別に、Voices Trial-09/10の**実際の
試聴結果**に基づく個別承認である。ただし本調査で確認した通り、**A Family側の
Editorial Type Module実装自体も現時点でゼロ件**(`er003_v1_n3_01_articles_generate.py`
を`editorial_type|EDITORIAL_TYPE|Editorial Type`でgrepし0マッチ)であるため、
「A群の結果」という前提条件は依然として未達である。この整合は第3・5節で扱う。

---

## 1. Editorial Type registry / Lane B構造定義の案

### 1-1. 現状(実コード確認済み)

- `er003_v1_n3_01_articles_generate.py`に`editorial_type`という概念・分岐は
  **存在しない**(0マッチ、再確認)。
- `COMMON_BLOCK_TEMPLATE`(101行目〜)は単一の巨大f-stringで、Discovery/Why固有の
  内容(阪神Master模倣・Main Story/Point役割定義)とCommon要素(Fact Ledger制約・
  Spoken-first数字ルール)が物理的に同じ文字列内に混在している。
- `build_common_block()`(348-364行目)は既に**後方互換オプション引数パターンを
  2回実績化済み**: `shared_point_blueprint_block: str = ""`・
  `evidence_compression: bool = False`。両方とも既定値時は旧来と完全同一テキストを
  返す設計。
- B-Family(Voices)の実際の記事生成は、上記のいずれの引数も使わず、**Trial側が
  `gen.COMMON_BLOCK_TEMPLATE`という文字列定数を直接`.replace()`で書き換えて
  Focus Module Blockを注入し**(`er012_editorial_b_voices_trial_07.py`
  `build_candidate_template()`、ANCHOR文字列`"【Spoken-first原則(数字の扱い)】"`の
  直前へ挿入)、さらに`gen.run_one_pattern()`を呼ばずprivate関数
  `gen._generate_and_compress_article()`・`gen._writer_process()`を直接呼び出す
  ことで実現している。Point Overlap QA/Diagnostic Full Retryも
  `gen.run_point_overlap_qa_and_regenerate()`を経由せず、内部で使われる
  `er008_point_overlap_qa_18.flag_possible_paraphrase()`・
  `er011_point_role_value_planning_01.run_point_value_qa()`を個別に直接呼び、
  結果はmonitoring専用(gateにしない)としている。
- Voice A/B本文の音声化(Algieba/Erinome)も同様に、Production
  `news_tail_fix.generate_news_narration_wide_margin()`(声固定`p9a.VOICE_NAME`=
  `p4b.VOICE_NAME`、実質Aoede固定、voice引数なし)を一切呼ばず、**Trial専用の
  ほぼ全ロジック同一コピー**`generate_voice_body_wide_margin()`
  (`er012_editorial_b_voices_trial_09_audio.py`629-714行目)を新規実装して
  `voice_name`パラメータだけを追加している。

**結論**: CURRENT_SPEC.md該当エントリの「(1)は既存共有Production関数
`point_headings.generate()`がすでに満たすため追加配線不要」という記述は、
**Narrator見出し(Aoede固定)の部分だけを指すなら正しいが、Voice A=Algieba/
Voice B=Erinomeという本文側の声指定は`point_headings.generate()`の対象外**
(この関数はNarrator見出し2箇所のみを扱い、本文は一切生成しない)であり、
Voice A/B本文側は現状どのProduction関数にも声の差し替え手段が存在しない
(`generate_news_narration_wide_margin()`はvoice引数を持たない)。この点は
CURRENT_SPECの記述がやや簡略化されすぎており、設計上は「(1)のうちNarrator部分は
配線不要、Voice A/B部分はLane B新規追加が必要」と正確化すべきと考える
(**CURRENT_SPEC自体の文言修正は本タスクの範囲外のため実施していない**、
第9節Open Questionへ記録)。

### 1-2. Editorial Type registry 設計案(未実装、案のみ)

**方式**: 新規Lane Bファイル`er012_b_family_editorial_type_registry_01.py`
(ファイル名は例、Fable判断)に、Editorial Type単位の設定を1箇所へ集約する
辞書/データクラスを定義する。

```python
# 案(擬似コード、未実装)
EDITORIAL_TYPES = {
    "b_family_voices": {
        "family": "B",
        "physical_structure": "five_section",  # Hook/Voice A/Voice B/Tension/Closing
        "section_labels": ["hook", "voice_a", "voice_b", "tension", "closing"],
        "voice_assignment": {"voice_a": "Algieba", "voice_b": "Erinome", "narrator": "Aoede"},
        "voice_fallback": {"voice_a": "Schedar", "voice_b": "Sulafat"},
        "focus_module_block": B_FAMILY_VOICES_FOCUS_MODULE_BLOCK,  # gen.COMMON_BLOCK_TEMPLATEへ注入する文字列
        "comment_roles": {
            "comment_1": VOICES_COMMENT_1_ROLE_FINAL,  # Trial-10/FINALIZE-11版
            "comment_2": VOICES_COMMENT_2_ROLE,
            "comment_3": VOICES_COMMENT_3_ROLE,
            "comment_4": VOICES_COMMENT_4_ROLE,
        },
        "key_phrase_position": "after_preview",  # 現状維持、変更なし
        "overlap_qa_mode": "monitoring_only",  # 第8節参照、gate化はしない
        "extra_qa": ["analytical_leakage_check"],  # 新規QA、既存Diagnostic Full Retryとは別枠
    },
    # 将来: "a_family_discovery_why": {...}, "a_family_news_trend": {...}
}
```

これは**新規Production構造(Lane B専用registry)であり、`er003_v1_n3_01_articles_generate.py`
本体には手を入れない**設計。既存Writer側は次節の通り、あくまで
「`editorial_type_module`という後方互換オプション引数を1つ受け取れるようにする」
という最小限の変更にとどめ、Editorial Typeごとの実体(声・Comment役割・
QAモード等)はこのregistry側が保持する。

### 1-3. ER-010報告書との整合/矛盾

- ER-010-WRITER-ARCH-01の推奨(6.1節「部分Module置換」、6.2節
  `COMMON_WRITING_CONTRACT`+`EDITORIAL_TYPE_MODULE`+`build_common_block(editorial_type_module=DISCOVERY_WHY_MODULE)`)
  とは**設計思想は一致**(後方互換デフォルト引数パターン)。ただし実コードは
  ER-010執筆時(2026-08-31)から変化しており、当時の行番号(99-217行目)は
  現在(101-347行目付近、`build_common_block`348行目・`build_prompt`419行目)
  とズレている。ER-010が前提にしていた「Voices Trial 1は2 Perspectiveに限定」
  という設計は、**2026-09-08承認範囲では既に5区切り構造(Hook/Voice A/Voice B/
  Tension/Closing)へ発展しており、ER-010の想定(見出し2つ固定)と一致しない**。
  実際、`split_five_voice_sections()`はTrial側の完全新規parserであり、
  Production `split_common_sections_for_point_qa()`(見出し=2固定、
  `## In one line`文言依存)は使われていない。ER-010報告書5節・6.2節が
  警告した「見出しブロックが2つ固定」という制約は、**B-Family Voicesでは
  実際には5区切り(見出し5つ)として実装されており、Point Overlap QA・
  Audio Validation Gate・disfluency QA必須segment名(`point_one_heading`等)
  はいずれも「2つの`###`」という前提を守れないため、ER-010が「コード変更不要」
  とした根拠は成立しない**。実際、Trial-09側は`asm.build_b1_timeline()`
  (11-part固定)を使わず、**Trial専用の`build_b1_voices_timeline_trial09()`
  へ丸ごと差し替えている**(この点はER-010の想定より変更範囲が大きい)。

---

## 2. Voice A/B固定・Tension slotのProduction配線先

### 2-1. Voice A/B固定音声

| 項目 | 配線先候補 | 根拠 |
|---|---|---|
| Voice A本文TTS(Algieba) | 新規Lane B関数(Trial実績: `generate_voice_body_wide_margin(text, out_path, "Algieba")`、`er012_editorial_b_voices_trial_09_audio.py`629行目) | Production `news_tail_fix.generate_news_narration_wide_margin()`は`voice_name`引数を持たず`p9a.VOICE_NAME`固定のため、無変更のまま流用不可(コード実物、`er003_v1_sing01_news_tail_fix.py`59-83行目) |
| Voice B本文TTS(Erinome) | 同上、`voice_name="Erinome"` | 同上 |
| Voice可用性チェック+fallback(Schedar/Sulafat) | `run_voice_availability_check()`/`resolve_voice_names()`(同ファイル293-345行目) | Trial実装済み、API側で声が技術的に使えない場合のfallback |
| Narrator見出し(Aoede) | **Production既存**`er003_v1_sing01_point_headings_aoede.py::generate()`(無変更で再利用可能、既にAoede固定) | 追加配線不要(CURRENT_SPECの記述通り、ただし1-1節の限定付き) |

**推奨**: `generate_voice_body_wide_margin()`は「`news_tail_fix.generate_news_narration_wide_margin()`
のvoice引数対応版」として、Production側`er003_v1_sing01_news_tail_fix.py`へ
**新関数として追加**(既存関数は無変更のまま温存し、新関数が内部で共有できる部分は
共有ヘルパー化を検討)するのが最小変更。Trial版をそのままコピー移設するだけでも
機能するが、既存関数とのロジック重複(ASR cascade・disfluency gate・attempt保存等)
が二重管理になるリスクがあるため、共通ロジックを`voice_name`引数を持つ内部
helperへ切り出し、既存`generate_news_narration_wide_margin(text, out_path, ...)`は
`voice_name=p9a.VOICE_NAME`を既定値として渡す薄いラッパーへ変える案が保守性は高い
(ただし影響ファイルがA-Family含む全既存呼び出し元に及ぶため、第4節Gate 4観点で
慎重な回帰確認が必須)。

### 2-2. Tension slot「Where the Difference Comes From」

- 記事本文側: `split_five_voice_sections()`(Trial-09実装、185-202行目)が
  5番目のラベルとして`"tension"`を検出。Production側に対応する検出関数は
  存在しない(新規)。
- 音声側: Trial-09では`EXTRA_SEGMENT_NAME = "tension_reflection"`という
  Trial専用segment名で扱われ、Aoede(Narrator/地の文と同じ声、見出し非読み上げ)
  で読まれる(`build_b1_voices_timeline_trial09()`843行目
  `"Tension: Where the Difference Comes From (Aoede, no heading)"`)。
- 配線先案: Comment3/4のRole文言(`VOICES_COMMENT_3_ROLE`/`VOICES_COMMENT_4_ROLE`、
  387-418行目)とセットで、Editorial Type registryの`focus_module_block`
  および`comment_roles`エントリへ格納する。Assembly側は`asm.build_b1_timeline()`
  (11-part固定)を無変更のまま流用できず、**B-Family専用のtimeline builder
  (Trial実績`build_b1_voices_timeline_trial09()`相当)を正式なProduction
  関数として`er003_v1_n3_01_assemble.py`内 or 新規Lane Bファイルへ追加する
  必要がある**(既存`build_b1_timeline()`は無変更のまま温存、呼び出し元で
  Editorial Typeにより分岐)。

---

## 3. 一人称"I"対応でLane A共有Writerへ及ぶ影響範囲

### 3-1. 現状の技術的事実

- Voice A/B本文の一人称記述は、Trial-07のFocus Module Block内で**明示的な
  必須ルールとして強制されたものではない**(ヘッダーコメント49-51行目
  「一人称/三人称は固定しない(必須にしない)」)。つまり2026-09-08承認済みの
  「一人称"I"記述」は、**複数Trialで自然に収束した書き方をユーザーが後追いで
  正式採用したものであり、現時点でこれを機械的に強制するPrompt文言はまだ
  存在しない**。
- Lane A共有Writer(`er003_v1_n3_01_articles_generate.py`)には
  `editorial_type`という概念そのものが無いため(1-1節)、「Voice A/Bのときだけ
  一人称を明示指示し、Discovery/Newsのときは何も変えない」という条件分岐を
  実現する仕組み自体が存在しない。

### 3-2. 影響を受ける関数・Prompt(変更が必要になる箇所)

| 対象 | 現状 | 変更内容(案) | A-Family非影響の保証方法 |
|---|---|---|---|
| `build_common_block()`(348-364行目) | `shared_point_blueprint_block`/`evidence_compression`の2既定引数のみ | 新規`editorial_type_module: str = ""`引数を追加し、既定値`""`時は`COMMON_BLOCK_TEMPLATE`を無改変のまま返す(既存2引数と同じ後方互換パターン) | 引数を渡さない既存全呼び出し元(A-Family全テーマ)は出力バイト列が1文字も変わらないことを単体テストで固定(ER-010報告書7-3節が提案した「Prompt文字列の完全一致比較」テストをそのまま採用) |
| `COMMON_BLOCK_TEMPLATE`(101行目〜) | Discovery/Why固有内容(阪神Master模倣・Main Story/Point役割)が物理的に混在 | ANCHORベースの挿入ではなく、`{editorial_type_module}`という新規f-string placeholderを1箇所追加し、`.format()`へ渡す(Trial-07の`.replace()`方式は本番採用しない。理由: `.replace()`はANCHOR文字列の将来的な変更・重複出現に対して脆弱、`.format()`のplaceholderの方が構造的に安全) | 新placeholderの既定値を空文字にし、既存`.format()`呼び出し(A-Family)には一切影響しないことを確認 |
| Comment1-4 Role定数(`er003_v1_b1_scaffold_01_generate.py`のCOMMENT_1_ROLE等) | B1/A2それぞれ専用モジュール内で1つに固定 | Editorial Type別のRoleセットを持つ辞書化(例: `COMMENT_ROLES_BY_TYPE["discovery_why"]`/`["b_family_voices"]`)。呼び出し元(`b1s.run_support_text()`自体は無変更、Trial実績通りRole文字列を外から渡すだけで対応可能なため、**この関数自体への変更は不要**) | 既定Editorial Type(discovery_why)を渡した場合、現状のROLE定数と完全一致することを確認 |
| Point Overlap QA/Diagnostic Full Retry(`er008_point_overlap_qa_18.py`・`er009_diagnostic_full_retry_modules_12.py`) | Main StoryとPointの言い換え判定、`###`見出し=2固定に依存 | B-Family(5区切り)では比較対象・閾値が異なる(第8節詳述)。Trial実績はmonitoring専用(gate化しない)のため、Production採用時も**当面はmonitoring専用のまま**にする案を推奨(閾値未検証のため) | 既存Discovery/News経路(`gen.run_point_overlap_qa_and_regenerate()`)は無変更、B-Family専用の別関数を新設して分離する(共有しない) |
| Analytical Leakage Check(Trial-07新規実装、963-1280行目付近) | Productionに存在しない、B-Family専用の新規QA | 新規モジュールとして正式化するか判断が必要(第7節Gate/第9節UDR) | Discovery/Newsからは一切呼ばれない設計にする(呼び出し元をLane B専用runnerに限定) |
| Writer全文retry上限 | Discovery/News: Diagnostic Full Retry最大2回 | B-Family: Trial-07は「Writer本体最大3回=初回+Leakage是正2回」という**別のretry上限**を独自に設けている | 既存Diagnostic Full Retryの上限(2回)とは別枠のB-Family専用上限として明示的に分離管理し、合算・混同しないようにregistry側でtype別に上限値を持たせる(第6節) |

### 3-3. A-Family出力が変わらないことの保証(具体策)

1. **既定値ゼロ影響の原則**: `build_common_block()`への新規引数は必ず
   既定値で旧来と完全同一のテキストを返すことを、リファクタ直後に
   `COMMON_BLOCK_TEMPLATE.format(...)`(旧)との**バイト単位完全一致テスト**で固定する
   (ER-010報告書7-3節の提案を正式採用)。
2. **呼び出し元の無変更**: 既存の全既知呼び出し元(`er006_pool_pilot_01_writer.py`、
   各`er0XX_n*_production_integration_*.py`)は一切コード変更しない(新引数を
   渡さないため既定値のまま動く)。
3. **Editorial Type未指定=discovery_why既定**: 万一将来`editorial_type`という
   引数自体を`run_one_pattern()`まで伝播させる場合も、既定値は必ず
   `"discovery_why"`(またはNoneで従来分岐)にし、A-Family呼び出し元の
   明示的なコード変更なしに従来動作を維持する。
4. **回帰テスト**: 既存No.9/No.18等のBaseline記事(ER-010-ARCH-BASELINE-DESIGN-02
   第7節のRegression Test Plan)を、リファクタ直後に実際に再実行し、
   Prompt文字列完全一致・構造抽出成功・Point Overlap QA正常動作・Fact Safety
   3チェック無エラーを確認する。

---

## 4. 既存A-Family/他Production経路への影響

| 対象 | 影響 | 確認方法(Gate 4観点) |
|---|---|---|
| Fact Checker/Ledger Deviation Checker v2/Directional Fact Precheck | **影響なし想定**(記事全文blobベース、構造非依存、ER-010報告書6-3節・8節で既に確認済み方針を維持) | 既存単体テスト再実行、B-Family記事でも同じ3関数がエラーなく動くことを確認 |
| Key Phrase選定・Model Routing Contract | **影響なし想定** | 同上 |
| Audio Validation Gate・disfluency QA必須segment判定(`er003_v1_n3_01_assemble.py`) | B-Familyが11-part固定(`point_one_heading`等)から外れた5区切り構造+専用timelineを使うため、**Production Assembly本体(`build_b1_timeline()`)は無変更のまま、B-Family専用timeline builderを別関数として追加する必要がある**(1-3節で確認済み、ER-010の想定より影響が大きい) | 新規timeline builder追加後も既存`build_b1_timeline()`が一切変更されないことをdiffで確認、既存A-Family Assemblyの回帰テストを実行 |
| Dangling Reference Check(Gate 4) | 新規`editorial_type_module`引数・新規Comment Role辞書・新規Voice A/B TTS関数・新規Analytical Leakage Check・新規B-Family timeline builderが、**Production呼び出し元(B-Family専用runner)が実際に存在しない限りDangling(誰にも呼ばれないコード)になる**リスクがある(現状のOPEN-112がまさにこの状態を指摘した前例) | B-Family専用Production runner(例: `er012_b_family_production_integration_01.py`)を新規作成し、実際にこの一連の関数を呼ぶ経路を1本用意した上でPRODUCTION_WIREDとする。呼ばれない中間関数を作らない |
| `run_project_regression.py` | 影響なし(pytest的globパターン`er0*_test_*.py`で自動収集、既存ファイル変更不要) | 新規テストファイルを`er012_test_*.py`または`er003_test_*.py`命名規則で追加するだけで自動的に収集対象になる(コード実物、`run_project_regression.py`40-48行目`DEFAULT_PATTERN = "er0*_test_*.py"`・`discover_test_files()`) |
| Human Review Lock・TTS retry cascade・ASR Validation・disfluency gate | **影響なし想定**。Trial実績(`generate_voice_body_wide_margin()`等)は`@review_lock.guarded_generate("en")`デコレータ・`secondary_asr.evaluate_attempt_with_cascade()`・`dq18.apply_disfluency_gate()`をいずれも無変更のまま呼んでおり、既存安全装置を独自に回避していないことを確認済み | Production採用時も同じデコレータ・関数を使い続けることを維持する(第6節) |

---

## 5. 最小変更で実現する場合の推奨構成(段階分け)

### Phase 1: Lane B内で閉じる部分(Lane A共有Writer変更なしで着手可能)

1. Editorial Type registry(1-2節案)を新規Lane Bファイルへ作成(データのみ、
   コード分岐なし)。
2. Voice A/B本文TTS関数を`er003_v1_sing01_news_tail_fix.py`(またはLane B新規
   ファイル)へ正式追加(2-1節、既存関数は無変更のまま新関数追加)。
3. B-Family専用Assembly timeline builder(`build_b1_voices_timeline_trial09()`
   相当)を正式関数化(既存`build_b1_timeline()`は無変更のまま別関数として追加)。
4. Comment1-4 Role辞書化・Voices Comment Contract確定版(FINALIZE-11反映後)を
   registryへ格納。
5. B-Family専用Production runner新規作成(4節Dangling Reference Check対応)。
6. Key Phrase位置は現状維持のため変更なし。
7. **Phase 1の範囲では、Voice A/Bの一人称"I"はまだ機械的に強制できない**
   (Focus Module Block自体がLane A共有Writer側の`editorial_type_module`
   placeholder導入を前提とするため、Phase 2待ち)。ただしTrial実績通り
   「一人称を必須にしない」運用のまま記事生成自体は可能(過去複数Trialで
   自然に一人称へ収束した実績があるため、Phase 1のみでも実用上大きな支障は
   出ない可能性がある。ただしユーザー承認は「正式仕様として一人称」である
   ため、機械的未保証のままPRODUCTION_WIREDと呼ぶのは正確でない、第9節UDR)。

### Phase 2: Lane A共有Writerへ及ぶ部分

1. `build_common_block()`へ`editorial_type_module: str = ""`引数追加、
   `COMMON_BLOCK_TEMPLATE`へ`{editorial_type_module}`placeholder追加
   (3-2節)。
2. Focus Module Block本文に「Voice A/Bは一人称("I")で記述する」という
   明示ルールを追加(Trial-07の自然収束実績を踏まえ、強制ルール化)。
3. Point Overlap QA/Diagnostic Full Retryのtype別分岐(B-Familyはmonitoring
   専用のまま維持するか、正式にgate化するかは実データ次第、第8節)。
4. 3-3節のバイト単位完全一致テスト・Baseline Regression Test Planを実行し、
   A-Family無回帰を確認してからPhase 2完了とする。

**推奨理由**: Phase 1だけでも「Voice A=Algieba/Voice B=Erinome/Narrator=Aoede」
「Tension slot」「Key Phrase位置維持」の3項目はPRODUCTION_WIREDにできる
可能性が高く、一人称"I"(4項目目)だけがPhase 2(Lane A変更)を待つ、という
段階的リリースが可能。ただしPhase 1単独でのPRODUCTION_WIRED宣言は、
「一人称が機械的に保証されていない」点をUSER_DECISION_REQUIREDとして
明示した上で行うべきである。

---

## 6. Gate・テスト・ロールバック観点

### 6-1. Gate 3 Production Wiring Checklistとの対応

| Checklist項目 | 対応方針 |
|---|---|
| Production正式初回経路 | Phase 1でB-Family専用runner新規作成(4節)、Phase 2で`build_common_block()`経由の正式経路確立 |
| retry・fallback・regenerationとの整合 | 既存Human Review Lock/TTS retry cascade/ASR Validation/disfluency gateは無変更のまま再利用(4節確認済み)。Analytical Leakage Check・B-Family専用Writer retry上限(3回)は既存Diagnostic Full Retry(2回)と混同せず別枠管理(3-2節) |
| DEV・Trial-onlyではないこと | Phase 1完了時点でTrialファイル(`er012_editorial_b_voices_trial_*.py`)への依存を断ち、正式Lane Bモジュールへ実体を移設する(Trialファイルはhistorical recordとして残すが呼び出し元にしない) |
| Production runtimeでの実発火 | B-Family専用runnerを実際に1回実行し、Voice A/B TTS・Tension slot・Comment Contract・Key Phrase位置がすべて実際のProduction関数経由で動作することを確認 |
| 必要testのPASS | 下記6-2節 |
| runtime evidence | 実際のepisode 1本をStandard同期で完成させ、cost・duration・clipping有無を記録(既存Trial-09と同水準) |
| Dangling Reference Check(Gate 4) | 4節の通り、新設関数がすべて実際にB-Family runnerから呼ばれることを確認 |
| approved specとProduction挙動の一致 | 2026-09-08承認4項目それぞれについて、Production実行結果とユーザー承認内容(Voice名・Tension slot名・Key Phrase位置・一人称)が一致することを確認 |

### 6-2. `run_project_regression.py`への追加案

- 命名規則`er012_test_editorial_type_registry_01.py`等(または`er003_test_*`)で
  以下を検証:
  1. `build_common_block()`既定引数でのバイト単位完全一致(3-3節)。
  2. Editorial Type registryの`voice_assignment`が実際のTTS呼び出し引数と一致。
  3. `split_five_voice_sections()`が5見出し以外(想定外構造)で`None`を返す
     ことの単体テスト(Trial実績のガードをそのまま正式化)。
  4. Voice A/B TTS関数のfallback分岐(API不可時にSchedar/Sulafatへ切替)の
     単体テスト(実API呼び出し不要、モック可)。
  5. B-Family専用timeline builderが既存`build_b1_timeline()`を一切呼ばず、
     かつ既存`asm.assemble_with_timeline()`等の共有primitiveは呼ぶことの
     契約テスト。
- 既存A-Family回帰(No.9/No.18 Baseline)は変更せずそのまま実行し、
  collected件数・failed件数が現状(既知failureのみ)から増えないことを確認。

### 6-3. ロールバック観点

- **feature flag**: `build_common_block(editorial_type_module="")`が事実上の
  feature flag(空文字=無効)。B-Family専用runner自体を呼ばなければA-Familyは
  一切影響を受けない。
- **経路分離**: B-Family専用runner・registry・timeline builder・Voice A/B TTS
  関数はすべて新規ファイル/新規関数として追加するため、ロールバックは
  「新規ファイルを削除する」+「`build_common_block()`の新規引数を削除する
  (Phase 2のみ)」の2アクションで完結し、既存A-Familyコードへの`git revert`は
  不要になる設計を推奨。
- **影響ファイル一覧(Phase 1)**: `er003_v1_sing01_news_tail_fix.py`(新関数追加のみ)、
  新規Lane Bファイル群(registry・timeline builder・runner・Comment Role辞書)。
- **影響ファイル一覧(Phase 2追加分)**: `er003_v1_n3_01_articles_generate.py`
  (`build_common_block()`・`COMMON_BLOCK_TEMPLATE`)、
  `er003_v1_b1_scaffold_01_generate.py`(Comment Role辞書化)。

---

## 7. 想定工数・費用・USER_DECISION_REQUIRED候補

### 7-1. 想定工数(目安、Sonnet実装ベース)

- Phase 1(Lane B内で閉じる部分): registry定義+Voice A/B TTS関数正式化+
  timeline builder正式化+Comment Role辞書化+B-Family専用runner新規作成+
  単体テスト。既存Trial資産(Trial-09/10)の実装を土台に「正式配線」する作業が
  中心のため、ゼロから設計するより工数は小さい。実行系はStandard同期TTS
  1 episode分(約350-450語+Comment/Preview/Key Phrase)で、Trial-09実績の
  コストオーダー(¥800上限設定、実測はそれ以下)を参考値とする。
- Phase 2(Lane A共有Writer変更): `build_common_block()`のリファクタ+
  バイト単位完全一致テスト+既存Baseline Regression実行(No.9/No.18)。
  コードの変更量自体は小さいが、**A-Family無回帰の確認(Regression実行)に
  実行時間・実API費用が発生する**(既存Baseline記事の再生成は不要、
  構造抽出・Prompt生成のみの静的テストで足りる想定)。

### 7-2. 費用

- Phase 1のRuntime evidence取得(B-Family 1 episode完成、Standard同期TTS):
  Trial-09実績ベースで数百円オーダー(上限設定次第、既存Trial-09は¥800上限
  設定で実測はより少額)。
- Phase 2のA-Family無回帰確認: 既存単体テスト+静的Prompt比較が中心のため
  追加API費用はほぼ発生しない想定(Baseline記事の実際の再生成をPASS基準に
  **しない**、ER-010報告書7-1節の既存結論を踏襲)。

### 7-3. USER_DECISION_REQUIRED候補

1. **CURRENT_SPEC記述の精度**: 「(1)は`point_headings.generate()`が
   すでに満たす」という記述を、Narrator部分限定という正確な記述へ修正するか
   (1-1節、本タスクでは修正権限がないため提案のみ)。
2. **Phase 1単独でのPRODUCTION_WIRED可否**: 一人称"I"が機械的に保証されない
   状態で、他3項目だけをPRODUCTION_WIREDと呼んでよいか(5節末尾)。
3. **Point Overlap QA/Diagnostic Full RetryのB-Family扱い**: monitoring専用の
   まま維持するか、実データを集めた上で正式にgate化するか(3-2節、
   ER-010報告書8節も同じ論点を未決として残している)。
4. **Analytical Leakage Checkの正式化可否**: 新規QA機構として正式採用するか、
   Trial限定のまま個別記事ごとの人手レビューで代替するか。
5. **既存`generate_news_narration_wide_margin()`の共通化リファクタ可否**:
   Voice引数対応のため、既存Production関数自体に手を入れる(内部helper共有)か、
   Trialのように完全別関数として複製するか(2-1節、複製は保守コスト増、
   共通化はA-Family既存呼び出し元への影響確認コスト増というトレードオフ)。
6. **B-Family専用Writer retry上限(3回)の正式採用可否**: 既存Diagnostic Full
   Retry上限(2回)とは別枠として正式にPM_GOVERNANCE 11節のループ上限規定に
   組み込むか(3-2節)。

---

## Status

**Status: DESIGN ONLY — NOT IMPLEMENTED, NOT VALIDATED, NOT APPROVED_FOR_PRODUCTION,
NOT PRODUCTION_WIRED**
