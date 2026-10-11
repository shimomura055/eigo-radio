# PHASE A 既存仕様・資料の確認(FAMILY-Z-STORY-POOL-SCREENING-TRIAL-01 委任_01)

読み取りのみ(Grep限定、SSOT全文読込なし)。有料API 0円。確認日 2026-10-11。
Blind保持: 過去Trialの作品別判定内容は本書に転記しない(`SEALED_PAST_RESULTS_L01_L06.json`へ封印)。

## 1. Family Z Seed選定条件(正本)
- 正本: `CURRENT_SPEC.md` 1373行〜「Family Z(Fiction)」節。項目3「Seed必須条件(4項目)」は 1406〜1422行付近。
  - (a) Original/primary textを直接確認できる(検索要約だけをSeedにしない。一次資料を確認できなければNG)
  - (b) 日本国内でPublic Domain、または日本国内で適法に利用可能(米国PDは必須条件にしない)
  - (c) 短編化しても中心Storyを保持できる
  - (d) Story品質基準4項目中、原則3項目以上を満たす
- Z-1〜Z-4(`CURRENT_SPEC.md` 1460〜1476行付近、`APPROVED_FOR_PRODUCTION`、ただしFamily Zは`PRODUCTION_WIRED`ではない): Z-1=権利Gate、Z-2=Family C既存関数再利用の専用runner、Z-3=In One Line最小変更流用、Z-4=Story本文単一canonical text+Dialogue Voice既存ルール。
- (a)の運用整理(F-4): 一次資料確認の4条件(本文を直接確認/出所明確/rights確認/当該資料にないFactを継ぎ足さない)。

## 2. 日本国内の権利確認ルール(正本行の引用)
正本(ユーザー正式決定 2026-09-26、`DECISION_LOG.md` 9638行付近、Z-1逐語):
> 「日本人向け・日本国内向けサービスであるため、Family Zの権利条件は以下で正式採用: (1)日本国内でPublic Domain、または日本国内で適法に利用可能であることを必須条件とする (2)米国PDは必須条件にしない (3)海外向け配信・提供を将来行う場合のみ、その対象法域のrights確認を追加する (4)原作がPDでも、現代の第三者翻訳・英訳・挿絵等は別著作物として扱い、権利未確認のものは流用しない (5)Family Zのadaptationは、確認済み原文/正式Seedから自前生成する。」

反映先: `CURRENT_SPEC.md` 1408〜1420行(Seed必須条件(b)、旧「日本法+米国法双方」は履歴注記)、`OPEN_ITEMS.md` OPEN-185(366行)。
**米国PDを日本の利用条件に置き換えない**: 上記(1)(2)により、米国のPD/Gutenberg表示は「記録事項」に留め、日本国内の利用可否の根拠にしない。本Trial screening scriptは米国statusを判定に一切使わない(`us_pd_used_as_jp_basis: false`を各JSONに記録)。
権利Gate実装(fail-closed): `er026_family_z_fiction_production_runner_01.py` `RIGHTS_REQUIRED_FIELDS`(104行)/`check_rights_gate()`(114行)/`MELOS_RIGHTS_BLOCK`(128行)。必須フィールド=author, author_death_date, jp_public_domain_basis, source_url, confirmed_date, us_copyright_status_record_only, legal_use_basis。

## 3. 4項目Story品質評価の定義と判定基準の正本
- 正本: `FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02_REPORT.md` §2(25〜40行)。成果物: `er018_output/fiction_external_seed_selection_criteria_trial_02/`(`candidates_evaluation.md` 候補評価表、`stories/`・`stories_all.md`・`blind.md`・`blind_key.json`、`raw_usage_log.jsonl`、`cost.json`)。実行script: `er018_fiction_external_seed_selection_criteria_trial_02.py`(597行)。
- 必須Gate(1つでも欠ければ除外): Gate1 一次内容を実際に確認(HTTP GETで取得しURL・取得日時・冒頭/結末引用で証跡化)/Gate2 権利状態が利用目的上問題ない/Gate3 A2・280〜420語へ圧縮しても中心Story保持。
- Story品質基準(4項目中3項目以上でPASS):
  - A 中心となる出来事・変化(追える中心事件・行動・関係変化・選択)
  - B 読者の関心を維持する要素(Hook・緊張・意外性・疑問・人間関係・共感・皮肉・強い状況設定。派手なHook必須ではない)
  - C 意味のある展開・変化・余韻(明確なオチ必須ではない)
  - D 短編化(280〜420語)しても魅力が残る(文体・長い心理描写を削ると魅力が消える作品は不向き)
- 注意(基準の事実): Trial-02のGate2定義は「ソース自身の明示的なPD/CC0表示」依拠で、日本法/米国法のどちらをカバーするかがソース種別次第だった(`FICTION-FAMILY-Z-RIGHTS-RECHECK-01_REPORT.md` §2)。その後Z-1(日本国内PD)で置換済みのため、本Trialの権利判定はZ-1を正とし、Trial-02のGate2運用定義は使わない。

## 4. Story Poolに転用できる既存コード・データ
| 用途 | 所在 | 備考 |
|---|---|---|
| 権利Gate(必須フィールド検証) | `er026_...runner_01.py` `check_rights_gate` / `RIGHTS_REQUIRED_FIELDS` | Production runner。変更しない。Trialは同じフィールド構成を踏襲(import不可、`er054_*`にはコピーしない: 判定ロジックは別実装) |
| canonical text処理 | `er026` `strip_markdown_title`(223行)/`check_word_count`(232行, `ACCEPT_WORD_RANGE=(280,420)`)/`check_character_name_rule`(239行)/`resolve_canonical_text`(291行) | 英語Story(adaptation後)用。本Trialは原作評価のみで未使用 |
| 一次資料取得・証跡化の方式 | `er018_fiction_external_seed_selection_criteria_trial_02.py` `SEEDS`(61行、source_url・rights_status・取得確認) | Trial-02で青空文庫/Gutenberg URLを確認済み。URLをL01-L06のsource_urlとして再確認(再利用) |
| LLM呼出・JSON schema・cost計算 | 同 `call_seed`(335行)/`SEED_JSON_SCHEMA`(309行)/`load_pricing`(489行)/`compute_cost_jpy`(503行)/`budget_guard`(540行) | `er054_..._quality_eval_trial_01.py`が同形式(Responses API+json_schema)を踏襲 |
| 費用ロガー | `er005_cost_logger.py` `install`/`logging_context` | real実行時のみlazy import |
| 単価 | `er005_output/cost_baseline_01/pricing_snapshot.json`、`er009_n1_routing_governance_10_actual_model_cost.py` `PRICING_USD_PER_M` | gpt-6-astra=10/1/50、gpt-6.1-sol=2/0.10/10、gpt-6-luna=0.10/0.01/0.50 USD/1M(snapshot)。USD_TO_JPY=160 |
| モデルRouting | `er006_model_routing_contract_01.py`(全7定数gpt-6-luna、Family X B3/R0/R1/R2=gpt-6.1-sol) | 評価用途の工程名は無い。評価用途は25節の最新モデル原則に従い、本driverが許可モデルを固定 |

## 5. 旧評価の権利判定の訂正履歴の所在(内容は封印ファイル)
- 訂正が記録されている場所: `FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02_REPORT.md` §10〜§11、`FICTION-FAMILY-Z-RIGHTS-RECHECK-01_REPORT.md` §2〜§3、`DECISION_LOG.md` 9638行付近(Z-1決着)、`OPEN_ITEMS.md` OPEN-185。作品別の内容は`SEALED_PAST_RESULTS_L01_L06.json`に封印(Blind保持)。
- 規則としての帰結(作品非依存): 旧規則「日本法+米国法の双方でPD」は2026-09-26にZ-1(日本国内PD必須・米国PD非必須)へ置換済み。

## 6. 封印ファイル
`er054_output/family_z_story_pool_trial_01/SEALED_PAST_RESULTS_L01_L06.json`: L01〜L06の過去判定行を出典パス・行付きで格納(candidates_evaluation.md各行、REPORT §10、RECHECK §2-3)。新評価(Phase C/D)確定後に開示・比較する。本Phase A・Phase B・Phase C/E設計・報告本文は、このファイルを読まず・転記していない。

## 7. 今回の判断メモ(新規提案の扱い)
- 本Trialの権利判定は、Z-1+日本の保護期間(没後70年、2018-12-30改正前の50年は非遡及、連合国民の戦時加算3,794日)の機械適用であり、新しい仕様の追加ではない。ただし保護期間の根拠が二次資料(en.wikipedia Copyright_law_of_Japan)である点と戦時加算の境界処理(2年以内→REVIEW_REQUIRED)はTrial運用上の保守的設計であり、`APPROVED_FOR_PRODUCTION`の仕様ではない(Production反映なし)。
