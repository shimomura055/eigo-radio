# MIGRATION_DESIGN_01 (Family Z KP: Strategy L -> DB Hybrid + M2P0 適用方式の設計案、Trial。Production無変更・未採用)

## 1. 案1(Family X経路をそのまま流用)

- 配線点: `w62.run_kp_with_outer_retry(..., select_fn=partial(sc.run_key_phrase_selection, kp_backend="db_hybrid", shortlist_cache=cache))`。`select_fn`は既存引数。canonicalization/Redundancy QA/symbol gate/Z外側retryは**そのまま共通**。DB Hybrid内部でDbHybridFailure時は既存契約どおりStrategy Lへfallback(`fallback_allowed=False`のときだけSTOP)。
- Prompt(P0)差分表:

| 部位 | Family X | Family Z案1 | 差分 |
|---|---|---|---|
| 静的instructions(`b1_p2_keywords_l_prompt_template.txt`の本文差込前) | そのまま | そのまま | **なし**(Strategy Lと同一テンプレ、現状もZに適用済み) |
| `_FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE`(選定方針) | 逐語 | 逐語 | **なし**(News⇔物語の置換不要。「専門用語」の語がNews色だが置換しない=最小原則) |
| 候補行/SENTENCE REFERENCE/【Topic】title | 自動 | 自動(Zのcanonical本文は題名なし -> `# 見出し`を渡すとTopic行に題名が入る。shortlistは不変[Phase1実測]) | 入力アダプタのみ |
| Z外側retryの汎用note(所有格回避) | 無し | 付与される(現行Zと同じ) | Zの既存挙動の維持。OPEN-310暫定策の要否は別判断 |

  -> **Family Z用guidanceの新規作成は不要**(STOP条件に非該当)。
- 既存Validator整合: gate内`p2g.validate_min_unit_selection`(5件・4+1役割等)、canonicalization Rule7、有限助動詞系、Redundancy QA、symbol gateは**同一module**を同一順序で通る。緩和なし。
- Rule7: DB Hybridはdisplay_phraseが候補canonical_form(source_span由来)のためZ現行のOPEN-310型(`pulled him under`->`pull someone under`)は構造的に減る見込み。ただしcanonicalization LLM段は共通のため0になる保証はなく、Trialで測定する。
- retry/fallback: M2供給例外=`M2_SUPPLY_EXCEPTION`/Wiktionary失敗=`SELECTOR_EXCEPTION`(いずれもDbHybridFailure -> Strategy L fallback)、上限は既存(`KP_ARTICLE_COST_CAP_JPY`=¥15/記事・Level、Z外側retry 3、Redundancy retry上限)を**変更しない**。M2->M0への黙示fallbackは存在しない(Production契約どおり)。
- Master Store/HR: KP段は音声を作らないため無影響。ただしPhase 2運用ではtelemetry関数をno-op化し、Master Store/HR/attempt_history/run_e2e_02へ書き込まない。
- 処理時間: 現行Strategy L(Melos kp段13 call 616秒)に対し、DB HybridはM2のWiktionary照会が単独185秒/記事/Level加算(Std+Adv=約6分)。LLM callはStrategy L(本文全文入力)より入力が短いが、reasoning長は同等。
- 費用: Strategy L(Melos kp段 JPY5.35)に対し、selection単価はX実績¥0.29-0.40(er064 cost_r1.json)で同等。canon/redundancyは共通。

## 2. 案2(必要時のみ)

- 案2a: DB Hybrid shortlistのFiction補強(物語の比喩・句動詞・台詞表現を拾うZ専用候補供給)。**N01・M2P0以外の方式探索に当たるため本委任では設計のみ言及、実装・Trialしない**(ユーザー判断事項)。
- 案2b: ハイブリッド(DB Hybrid候補 + Strategy L全文選定の併用)。同上、本委任の範囲外。

## 3. 必要なProduction変更一覧(いずれも**未実装・未承認**)

1. Z配線: `er062_family_z_writer_01.run_kp_stage`または`er026 stage_kp`が`select_fn`/`kp_fn`にDB Hybridを渡す(1-2箇所、`ctx.hooks`で注入可)。
2. (任意)`SUPPORTED_FAMILY_PROFILES`への`family_z`追加(telemetry上のFamily識別。guidance差分なし)。
3. Telemetry識別(family_z/db_hybrid)の追加。
4. OPEN-310暫定外側retryの扱い(維持/撤去)。

## 4. Opus論点(Production採用提案時、条件A/C)

- shortlist段の取りこぼし(Fiction比喩・台詞)が構造要因か(Phase 1/2実測で確認)。M2の(a)(b2)ルールがFictionで低価値断片を予約枠に入れる点。
- 「重要語枠(important noun)」の定義がFictionで名詞句(fruit shop等)に偏る点。
- Strategy L fallbackの存在がZ品質評価を曖昧にしないか(fallback発火時は結果をDB Hybrid成功として数えない運用)。
- 処理時間3分/Level増の許容。
