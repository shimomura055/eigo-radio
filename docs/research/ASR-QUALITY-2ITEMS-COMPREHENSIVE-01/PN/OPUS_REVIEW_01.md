# OPUS_REVIEW_01: ①固有名詞 Run Entity Table(RET)設計への Opus 条件Aレビュー結果

管理ID: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-PN / 2026-10-23
**本文はFable(sandwich-pm)が受領したOpusレビュー所見を、委任_02の委任文経由でSonnetが転記したもの**(Opus原文そのものではなく、委任文に含まれた「逐語要約」。原文のトランスクリプトは本リポジトリに別途保存されていない)。
対象: DESIGN_01.md / OPUS_REVIEW_REQUEST_01.md / ROOT_CAUSE_01.md。

## Fable判定(記録用)
Opus総合判定=「必須修正後にTrial実装可、再設計不要」。方向は実質一致(RC-1〜4、RET、受理境界不変、P-02残置、Iran/Mark型ブロック維持、音素ゲート不採用、HR Lock済み4clipは採用後再生成)。対立点4つ(2シグナルの実態=LLM単独/集合ではなく出現位置に紐づけ/SC-5 parityはトートロジー/作品名中の低頻度一般語)はいずれも誤PASS防止の技術修正でProduct原則変更ではない→Fable判断でTrial実装へ進む。区分: LLM NER新証拠源+G3変更は「新仕様候補」(OF-PN2-12)として扱い、採用はユーザー判断(VALIDATED止まり)。RET-3は11-7限定例外の対象外になる可能性が高い(将来は VALIDATED→ユーザー正式採用→Production実装の経路)。

## 所見
- **OF-PN2-01[必須]** 証拠は語の集合(bag)でなく「実体の出現位置」に紐づける。`ledger_surface_tokens`(er103:697-712)は語集合化するため複数語実体中の一般語(Will/University/Said)が記事全体で証拠化し、固有名詞混在句のdiffやRET-3で通る。修正: (i)表から証拠を付けるのは非一般語tokenと実体内部イニシャルのみ (ii)Primary diffのcanonical句が当該segmentのcanonical_text内の実体出現範囲に連続して含まれる場合のみ証拠付与 (iii)実体がそのsegmentに出現しなければ証拠なし。
- **OF-PN2-02[必須]** RET-3厳密化: 現行G3(er103:358-366)は `c_set & noun_tokens` 交差条件。語集合判定だと別実体tokenの偶然隣接(`Reicher will`→`riker well`)を通す。Secondary合成spanは `by_canon_s` に入らずP-03(:394-397)を経由しない。修正: (i)Secondary spanが当該位置で連続する1実体出現(または区切り語なし隣接複数実体)とtoken単位一致 (ii)spanがPrimary diffの固有名詞tokenを全て含む (iii)合成spanにも `_noun_checks` とP-03適用。負例test: 隣接実体の一般語token、機能語(the/and)巻き込み、数値・否定語巻き込み、`melos drank`。補足: C類16件中10件は同一segment(pool_n5_cafes L. Mimoun)再試行で実質母数は数件。
- **OF-PN2-03[必須]** 「2シグナル」の実態: confirmed=「LLM∧大文字一貫性∧決定論大文字出現」だが後2つは独立でない(1回出現語は必ず真)→Bertie型は実質LLM単独。修正: 独立裏付けなし(宣言なし・文中大文字なし・CMU収録)のentryは、2回の独立call(prompt変更or温度違い)一致時のみconfirmed。Std/Adv統合1callなら計2callで≤0.1円。記述も実態に合わせる。
- **OF-PN2-04[必須]** 作品名・スローガン・一般名詞句中の低頻度一般語(The Crimson Petal の petal→pedal)を証拠化しない。修正: CMU収録tokenに表証拠を付けるカテゴリは person/place/organization のみ。work_title/other_named はCMU未収録tokenのみ(=cmu_oov同等)。brand_product はCMU収録可だがSC-3で別集計。
- **OF-PN2-05[必須]** 表の入力は「実際にTTSへ渡るsegment canonical textの和集合」(対象roleはPREVIEW/TOPIC_INTRO/IN_ONE_LINE/COMMENT含む er103:89、canonicalは供給後tts_input er019:353-358)。planの対象role(KP/JA/HEADING除外)全canonicalの和集合にNER、逐語検証はsegmentごとに供給前後の両textで、正規化ずれ(引用符向き・数字展開)をtest固定。
- **OF-PN2-06[必須]** 継承再判定(er019:349-366→er103:724 正式Ledgerのみ)とLocal Rewriteで揺れない設計: 表sha不一致で表なし(DESIGN_01:48)だとLR毎に他segmentの受理が戻り再生成費用発生。修正: (i)アラームblockに受理に使った実体entry(surface/tokens/category/grade)を保存し、再判定ではそのsegment textへの逐語出現のみ確認して再利用(表sha一致不要) (ii)LRでは表を作り直さず変更segmentのみNERして和集合に追加(減らない) (iii)再判定経路ではLLMを呼ばない。SCに追加。
- **OF-PN2-07[必須]** SC-5 parityはトートロジー(誤PASS証明にならない)。SC-5は実装同値testとして残し、別に「D1で新規受理となった全件+Stage 2実誤読データ(複数ASRが揃って別語)を人がadjudication→意味が変わる受理・一般語誤読受理=0」をSCに。SC-2 recallは表が実際に必要な層(CMU収録・非一般語・文中大文字なし)で層別≥0.90。SC-4はユニーク(text,名前)単位も併記。SC-9にJaccardに加え「3回構築の和集合でも非固有名詞への証拠付与0」。
- **OF-PN2-08[推奨]** 「区別」は関門でなくアラームのラベル(音素距離帯/P・S両ASRが同じ別語か/ASR語zipf 3.5〜4.0境界付近)で応え試聴優先度に使う。カテゴリ別閾値は入れない。wordfreq version固定、境界付近受理を集計。
- **OF-PN2-09[推奨]** (i)X英語出典メタデータ(記事題名・人名)が保存されていれば宣言型R2として使う (ii)R_GENERAL_WORDで止まった person/place を件数記録 (iii)日本語由来ローマ字名はOOV処理で可、Tokyo/Japan等は許容 (iv)小文字始まりブランド(iPhone/eBay)は対象外と明記 (v)KP/ja_readingはG0除外で問題なし。
- **OF-PN2-10[推奨]** Std/Adv統合1call(2call合意でも約0.06円)。構築は脚本確定直後に並行。run単位保持は `_RUN_SCOPE` 同様process内状態、finallyで必ず解除。
- **OF-PN2-11[推奨]** TrialでG3を複製する場合はer103該当関数sourceのhash照合drift guard test。`evaluate_alarm_eligibility` は `enabled=True` 明示・scope未設定(er103:319-322)。将来配線: RET-2は11-7限定例外可、RET-3は既存G3直接変更で対象外の可能性→VALIDATED→ユーザー採用→Production実装経路。②UKUSとの境界整合、表共有は読み取りのみ。
- **OF-PN2-12[情報]** Stage 2 REJECTEDは「発音正否判定方式」で本案と矛盾なし。新規受理の多くは実誤読がアラーム付き受理になる→承認済み方針範囲内であることを最終報告で明示。P-02縮小せず同意。HR Lock済み4clipは採用後再生成。NG_BOTH起点の再評価拡張はHR Lock解除を伴う仕様変更で先送り同意。Perplexity 401は別OPEN追跡。
- **OF-PN2-13[情報]** 費用0.05〜0.10円/記事セット。Std/Adv統合が最も効果大。モデル比較はSC-3/SC-9達成を条件に。
