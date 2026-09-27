# design_key_phrase_db_based_selection_01 — Key Phrase DB照合方式 設計doc

管理ID: KEY-PHRASE-DB-BASED-SELECTION-DESIGN-01
性質: 設計フェーズ(到達可能な最大Status=`DESIGN_READY_FOR_TRIAL`)。
**Production code/Prompt/CURRENT_SPECのProduction仕様はこのタスクでは
変更しない。実Trial(DB照合→選定)は実行していない。** 本docは設計案
であり、`APPROVED_FOR_PRODUCTION`はユーザーのみが宣言できる
(`docs/pm/PM_GOVERNANCE.md`)。

参照: DB一次情報の逐語引用・URL・取得日時は
`docs/pm/db_survey_key_phrase_sources_01.md`。既存Production経路の
現状確認は本doc「0. 既存経路の実装確認」節。

---

## 0. 既存経路の実装確認(reconciliation、変更しない前提の記録)

現行Key Phrase Production経路は2段階のLLM呼び出しで構成される
(`er003_key_words_production.py`＋`er003_key_words_canonicalization.py`)。

1. **選定(Selection)**: Strategy L(Listening Blocker Ranking)。
   `SELECTOR_MODEL`(`gpt-5.6-sol`、モデルルーティング契約上は
   B1/A2 SupportとしてLuna系へ変更済み、`ER-006-MODEL-ROUTING-CONTRACT-01`)
   ・`reasoning_effort="high"`のStructured Output呼び出し1回
   (`run_production_selection_gate`、`MAX_PRODUCTION_RETRY_ATTEMPTS=2`
   =初回+技術的失敗/hard requirement不適合時の再試行1回のみ)。
   ちょうど5件(`PRODUCTION_ITEM_COUNT=5`)、schemaは
   `source_span`/`display_phrase`等を含む。
2. **正規化(Pedagogical Phrase Canonicalization)**: 同一モデル設定で
   別のLLM呼び出し1回(`run_canonicalization_gate`相当、
   `MAX_CANONICALIZATION_RETRY_ATTEMPTS=2`=同様に初回+再試行1回のみ)。
   `source_span→display_phrase→key_phrase→used_form`の変換を行う。
   `key_phrase`は1〜5語のMinimal Sufficient Unit、`used_form`は現状
   `key_phrase`と同値(将来のTTS分岐用に独立フィールドとして温存)。

したがって1level(A2 or B1)あたり通常2 LLM call(選定+正規化)、
リトライ発生時は最大4 call。A2+B1の2レベルなら通常4 call、最大8 call。
この数字はSection Gのコスト比較のベースラインとして使う。

**この設計案は、上記の既存2段階構造そのものを置き換える案ではなく、
「選定(1)」の入力候補生成方法を、DB照合ベースへ変更する案である。
「正規化(2)」の役割(display_phrase→key_phrase→used_formの整形)は
そのまま維持し、`used_form`/`key_phrase`のフィールド契約
(CURRENT_SPEC「`used_form`/`key_phrase`の関係」= 100%重複を整理しない
方針)にも従う。**

---

## A. DB調査(サマリ、詳細は`db_survey_key_phrase_sources_01.md`)

| DB | 収録 | 商用ローカル取込 |
|---|---|---|
| Oxford 3000/5000 | word | 不可(標準ToS) |
| Oxford Phrase List | phrase | 不可(標準ToS) |
| English Vocabulary Profile(Cambridge) | word/phrase | UNRESOLVED(要契約と推定) |
| CEFR-J Vocabulary Profile | word | **可(引用条件付き無償)** |
| NGSL/NAWL/NGSL-S/BSL | word | **可(CC、商用含む無償と明記)** |
| PHRASE List(Martinez & Schmitt 2012) | idiom的phrase 505件 | UNRESOLVED |
| PHaVE List(Garnier & Schmitt 2015) | phrasal verb 150件 | UNRESOLVED |
| Academic Collocation List(Pearson) | collocation 2,469件 | UNRESOLVED |
| Wiktionary(英語版) | word/phrase/idiom/discourse | **可(CC BY-SA、ShareAlike注意)** |

---

## B. Production DB候補構成案(2群分離)

### B-1. 群1: Productionへローカル取込可能(商用可・条件明確)

- **CEFR-J Vocabulary Profile**(word、CEFR band付き、引用必須)
- **NGSL / NAWL / NGSL-S / BSL**(word、頻度順、CC・商用可、引用推奨)
- **Wiktionary派生データ**(word/phrase/idiom/phrasal verb/discourse
  expression、CC BY-SA、ShareAlike注意=外部再配布しない内部照合用途
  に限定する運用ルールを設ける)

この3系統は性質が異なる(2つはword中心+CEFR/頻度情報、1つはphrase/
idiom/discourse expressionを含む)ため、「複数DB一致」判定を成立させる
最小構成として使える。ただし群1だけでは、CEFR-J・NGSL系がword中心
のため、**phrase/idiom/collocation側の複数DB一致件数は少なくなる
見込み**(Wiktionaryのidiom/phraseカテゴリタグの精度・網羅性に依存)。
これは実データで検証しないと分からない(dry-runでは確認していない)。

### B-2. 群2: Trial/評価参照のみ(未確認・制限あり)

- Oxford 3000/5000・Oxford Phrase List(商用不可、標準ToSの範囲では
  除外)
- English Vocabulary Profile(ライセンス条件UNRESOLVED)
- PHRASE List・PHaVE List・Academic Collocation List(商用可否
  UNRESOLVED、著者/発行元への直接確認が必要)

群2は、除外Gateの人間判断や、将来ライセンス確認が取れた場合の
「追加DB一致」候補として、**Production判定式には含めず**参考表示
(observedデータとしてログには残すが、選定のranking計算には使わない)
とする設計を推奨する。

### ライセンス衝突チェック

群1内でのライセンス衝突は確認されていない(CEFR-J個別ライセンス・
NGSL CC・Wiktionary CC BY-SAは、それぞれ独立に内部参照する分には
互いに矛盾しない)。ただし将来「複合DB(3者をマージした二次データ
セット)」自体を外部公開・再配布する場合は、Wiktionary側のShareAlike
条項により複合データセット全体がCC BY-SA相当の再配布条件を
引き継ぐ可能性がある。これは**社内の照合ロジックが参照するだけ
(非公開・非再配布)である限りは実務上の障害にならないと考えられるが、
断定はしない**。STOPには該当しない(内部利用に限定する前提を設計に
明記することで対応可能)。

---

## C. Candidate extraction設計(deterministic)

### C-1. 既存資産の再利用可否

- `wordfreq`(`er015_*`系Trialモジュールで使用実績あり、頻度ランクの
  取得に使える): **再利用可能**。ただし現状Key Phrase Production経路
  では未使用(Standard/Advanced語彙帯チェック専用のTrial資産)。
- `lemma_candidates_v2`/`rank_of_word_v2`(`er015_advanced_vocab_rule_trial_01_v2.py`
  等): 単語の活用形(複数形・過去形等)を規則ベースで削って基本形候補を
  作る関数。**単語単位の正規化には再利用可能**。ただし
  (a) phraseの活用形(例: "picked up the pace"→"pick up the pace")には
  対応しない、(b) discontinuous phrasal verb(pick it up⇄pick up)にも
  対応しない。これらは新規ロジックが必要(C-3参照)。
- `er003_key_words_min_unit.py`のdisplay_phrase 1〜5語制約・完全文/節
  排除・有限助動詞排除の判定関数: **候補の事後フィルタとして再利用
  可能**(除外Gateの構造的チェック層と統合できる)。
- `p9a.build_key_phrase_block()`(音声組版側): 入力はcanonicalization後の
  `used_form`/`ja_gloss`を想定した既存I/F。DB照合方式に変更しても、
  **canonicalization段階(既存のsource_span→key_phrase→used_form変換、
  LLM 1 call)をそのまま維持すれば、音声組版・Secondary ASR側との
  I/Fは無変更で済む**という設計にする(=変更はSelection段階のみに
  閉じ込める)。

### C-2. 候補抽出パイプライン(案)

1. 本文(最終確定Standard/Advanced本文、レベルごとに独立)をtokenize
   (単語境界、句読点・記号除去、大小文字は保持した表層形と正規化
   済み小文字形の両方を保持)。
2. 1〜5-gram(word n-gram)を全て機械的に生成する(「重要そうか」で
   この段階では絞らない、ユーザー確定原則2)。
3. Lemma化(`lemma_candidates_v2`拡張、複数語の場合は各構成語を
   個別にlemma化してから再結合したcanonical候補も追加生成)。
4. Dictionary phrase matching: 群1DB(CEFR-J・NGSL系・Wiktionary)の
   phrase/idiom/collocationエントリと、正規化済みn-gramを完全一致・
   活用ゆれ吸収一致で照合。
5. Phrasal verb変形吸収: 句動詞DB(Wiktionary category、将来ライセンス
   確認が取れればPHaVE List)を使い、(a) 隣接形(pick up)・(b)
   discontinuous形(pick it up / pick the ball up)の両方を検出する
   正規表現+lemma照合パターンを用意する(目的語代名詞・名詞句の
   間に挟まる1〜3語程度までを許容範囲とする、というルールの具体的
   閾値は実データを見てから決める=ユーザー確定原則5と同じ姿勢)。
6. 各候補をDB canonical formへnormalize(表層形→display候補→DB側の
   見出し形にマッピング、大文字小文字・ハイフン・アポストロフィ
   ゆれを吸収)。

### C-3. 新規に必要なロジック(既存資産にない部分)

- Phraseレベルの活用形正規化(単語のlemma化を複数語表現に拡張)。
- Discontinuous phrasal verb検出(新規、閾値未定)。
- DB canonical formへの逆引きmapping(DB側の見出し語表記ゆれ吸収)。

これらは本タスク(設計フェーズ)では実装しない。Trialで実データを見て
から実装する対象として明記する(STOP条件「deterministic抽出で重大な
漏れが避けられない」に該当するかどうかも、Trialでの実測が必要)。

### C-4. 抽出量dry-run(¥0、DB照合なし・選定なし)

既存本文6本(Meta a2/b1b、small_bag run_02 a2/b1b、hormuz run_02
a2/b1b)に対し、上記1〜2の「tokenize→1〜5-gram生成」のみをdeterministic
に実行した(DB照合・選定・LLM呼び出しは一切なし、markdown見出し記号
除去のみの単純tokenizer)。

| article | total tokens | unique 1-gram | unique 2-gram | unique 3-gram | unique 4-gram | unique 5-gram |
|---|---:|---:|---:|---:|---:|---:|
| meta_a2 | 317 | 145 | 288 | 309 | 312 | 313 |
| meta_b1b | 336 | 163 | 309 | 331 | 333 | 332 |
| small_bag_run02_a2 | 305 | 166 | 268 | 294 | 300 | 300 |
| small_bag_run02_b1b | 313 | 177 | 282 | 304 | 308 | 308 |
| hormuz_run02_a2 | 360 | 187 | 324 | 348 | 353 | 354 |
| hormuz_run02_b1b | 345 | 188 | 316 | 337 | 339 | 339 |

観察: 1本文あたり300〜360 tokenで、unique n-gram数はn=1で145〜188
(語彙の重複が多い=関数語の反復)、n=2以降は急速にほぼ「total-n+1」に
漸近する(=同じ2〜5-gramの反復はほとんどない、ニュース記事という
性質上当然)。つまり素朴に全n-gram(1〜5)をDB照合にかけると、**1記事
あたり合計で約1,500〜1,750件程度のn-gram照合(6本文合計では約9,900件)**
が発生する規模感になる。DB側の照合をハッシュ辞書引き(O(1)相当)に
すれば処理時間は無視できるレベルだが、「本文中に実在する候補すべてを
DB1件ずつ愚直に線形探索する」実装は避けるべきという設計上の示唆になる
(=DB側もcanonical formをkeyにしたhash setとして持つ)。

---

## D. Matching/scoring設計

### D-1. Candidate evidence schema(案)

```json
{
  "surface_form": "picked up the pace",
  "canonical_form": "pick up the pace",
  "source_span": "picked up the pace",
  "source_sentence": "...",
  "matched_dbs": ["wiktionary"],
  "db_match_count": 1,
  "db_categories": ["idiom"],
  "unit_type": "phrase",
  "cefr_level": null,
  "context_note": "...",
  "exclusion_gate_result": {
    "too_easy_or_common": false,
    "proper_noun": false,
    "article_specific_low_reuse": false,
    "semantic_functional_duplicate_of": null,
    "unnatural_out_of_context": false,
    "low_value_as_chunk": false
  },
  "final_selection_reason": null
}
```

- `matched_dbs`/`db_match_count`: 複数DB一致(=外部根拠の強さ)軸。
- `unit_type`(word/phrase/idiom/phrasal_verb/collocation/discourse
  expression): chunk価値の判断材料(hard rule化しない、あくまで
  ranking時の一参考情報)。
- `cefr_level`: 保持するが、除外Gateの主軸には使わない
  (ユーザー確定原則1・4)。
- `exclusion_gate_result`: 各Gate項目をbooleanで個別記録し、後から
  「どのGateで何件落ちたか」を集計できる形にする(Section E)。

### D-2. Ranking方針

ユーザー確定原則3のとおり、hardcodeされた優先順位式(例:
`score = db_match_count*10 + unit_type_weight`のような単一スカラー化)
は**行わない**。設計としては2軸(db_match_count、chunk価値=unit_type
を含む定性的判断)を別々に保持したまま、以下の順で人間可読な
tie-breakを適用する形を推奨する。

1. 複数DB一致(db_match_count>=2)を最優先グループとする。
2. 同程度(同じdb_match_count)の中では、phrase/idiom/collocation等の
   chunk価値がある候補を単語より先に見る(ただし「機械的に単語を
   全部後回し」にはしない。除外Gateで単語が有効な候補として残った
   場合は排除しない)。
3. 単一DB一致は上記2グループで必要数(4〜5件)に届かない場合に検討する。
4. 除外Gate(Section E)を先に通していない候補は、上記1〜3のどの
   グループにも入れない(除外Gateが優先)。

---

## E. 除外Gate観測項目(閾値は決めない)

Trial実行時に以下を表形式・JSON形式の両方で出力できるようにする
(閾値は決めずobservationのみ)。

| 観測項目 | 説明 |
|---|---|
| DB照合総数 | n-gram候補のうち、群1DBのいずれかにcanonical一致した数 |
| single word数 | 上記のうちunit_type=wordの数 |
| phrase系数 | 上記のうちphrase/idiom/phrasal_verb/collocation/discourse expressionの合計 |
| 複数DB一致数 | db_match_count>=2の数 |
| 単一DB一致数 | db_match_count==1の数 |
| 簡単すぎ・一般的すぎ候補数 | 除外Gate該当(人間 or 規則判定、閾値未定) |
| 記事固有・再利用性低候補数 | 同上 |
| 意味・機能重複候補数 | 同上(重複先candidate_idを記録) |
| 人間目線で残したい候補数 | Trial時に人間が目視で「これは残したい」と
  マークした数(除外Gateの妥当性を後から検証するための対照データ) |

これらはTrialで実データを取得してから、閾値(「何件以上あれば
どのGateを厳しくすべきか」等)をユーザーと確認する前提。本設計フェーズ
では閾値を決めない(委任条件どおり)。

---

## F. AI fallback設計

### F-1. LLM call 0案

DB照合+除外Gateのみで4〜5件確保できた場合、LLM呼び出しは行わない
(既存canonicalization段階は維持するため、そこでの1 LLM callは残る
=完全な0 callにはならない。「Selection段階のみ0 call」という意味)。

### F-2. 不足時のみ1 call案

DB照合+除外Gate後の候補が4件未満の場合のみ、不足数を補うための1回の
LLM呼び出しを行う。

- 入力: 本文(最終確定テキスト)、既選定候補一覧(重複を避けるため)、
  固定条件(1〜5語・完全文/節排除・有限助動詞排除等、既存
  `er003_key_words_min_unit`のhard requirementをそのまま流用)。
- 入力に**含めないもの**: 「重要な表現を選べ」という主観的指示、他記事・
  他レベルの選定結果、DB側のraw内部スコア(モデルに数値順位を
  自己申告させない、既存原則を踏襲)。
- 補完基準(ユーザー確定原則6の言い換えではなく、そのままプロンプトの
  条件として使う): 他文脈で再利用しやすい/chunkとして覚える価値/
  本文中に実在する/記事固有専門語だけではない/既選定と重複しない/
  学習者に意味のある表現。

### F-3. 比較

| 観点 | (1) LLM call 0案 | (2) 不足時のみ1 call案 |
|---|---|---|
| コスト | 最小(canonicalizationのみ) | 通常は(1)と同じ、不足時のみ+1 call |
| 品質リスク | DB網羅性に強く依存(群1が痩せているとphrase系が
  不足しやすい) | 不足を機械的に埋められる、ただし補完基準の運用が
  安定するかはTrialで検証が必要 |
| 推奨 | 群1DBの実際のcover率をTrialで見てから、(1)を既定・(2)を
  fallbackとして両方実装しておくのが妥当(排他ではなく併用) | 同左 |

---

## G. コスト/latency試算

### G-1. 現行方式(既存Key Phrase Production経路、実測ベース)

- 選定+正規化=2 LLM call/level(通常)、リトライで最大4 call/level。
- 実測コスト(既存ログより、逐語ではなく数値のみ引用):
  - `docs/pm/recon_family_z_production_e2e_01.md`: 「Key Phrase選定 ¥5〜15」
    (既存Family共通の実績と同水準の仮定値として記載)。
  - `ER-006-MODEL-ROUTING-CONTRACT-01_report.md`: 「Support(Key
    Phrase/Fact Check込み)」の期間集計でHistorical Actual ¥223.0 /
    Luna切替後Counterfactual ¥10.3(複数記事分の集計値であり単体記事
    コストではない点に注意)。
  - `DECISION_LOG.md`各所: 個別事例として「Key Phrase B1B試行2回¥27.75」
    「Key Phrase retry ¥2.89」等、失敗・リトライ発生時は+¥3〜30程度
    上振れする実績あり。
- 目安: 1level通常時¥5〜15、A2+B1で¥10〜30。リトライ・Human Review
  発生時はこれを上回る(実績で¥27〜70台の事例あり)。

### G-2. DB照合方式(設計値、実測ではない)

- ローカル抽出(tokenize+n-gram生成): 本タスクのdry-run実測で6本文
  (計約1,976 token)の処理は数百ミリ秒以内(n-gram生成のみ、Pythonの
  素朴な実装)。DB照合(hash lookup)を追加しても1記事あたり数百ms〜
  1秒程度と見込む(実測はTrialで行う)。
- DB(群1: CEFR-J語数千+NGSL系合計語数千+Wiktionary抽出idiom/phrase
  数万件)をメモリ上のhash setとして保持する場合のmemory使用量は
  数十MB程度と推定(数値はTrialで実測が必要、断定しない)。
- API呼び出し: 
  - Web access: 0回(DB取得は初回セットアップ時のみ、記事生成の都度は
    アクセスしない設計)。
  - LLM call: F-1案なら0(Selection段階)。F-2案は不足時のみ+1回。
    Canonicalization段階の1 call(既存維持)は残る。
  - 合計: 通常時1 LLM call/level(canonicalizationのみ)。既存の2 call/level
    から1call/levelへの削減(fallback発動時のみ2 call/levelで既存と同等)。
- 追加費用: LLM call削減分だけコスト減少(既存が¥5〜15/level中、
  選定呼び出し分がおおよそ半分程度を占めると仮定すれば¥2〜8/level
  程度の削減見込み、**この按分は仮定であり実測ではない**)。DB
  セットアップ・保守(ライセンス条件の順守、DB更新の取り込み)という
  非API的なコスト(開発・運用の手間)が新たに発生する点は費用試算に
  含めていない。

### G-3. 比較まとめ

| 項目 | 現行(LLM選定+LLM正規化) | DB照合(0 call案) | DB照合(fallback 1 call案) |
|---|---|---|---|
| LLM call/level(通常) | 2 | 1(正規化のみ) | 1(通常時) |
| LLM call/level(fallback/retry時) | 最大4 | 最大2(正規化retry含む) | 最大2〜3 |
| Web access/記事 | 0 | 0(DB事前取得済み前提) | 0 |
| 概算コスト/level | ¥5〜15 | 現行より減(実測要) | 現行同等〜微減 |

---

## H. Trial案(実行しない、手順のみ)

### H-1. 対象

Meta / Hormuz / small_bag × Advanced(A2)/Standard(B1B) = 最大6本文
(既存確定本文の再利用、新規記事生成は行わない)。

### H-2. 手順

1. 群1DB(CEFR-J・NGSL系・Wiktionary抽出)のローカル取り込み
   (ライセンス条件の記録・引用表記の保存を含む)。
2. Section Cのdeterministic抽出を6本文に対して実行(¥0、LLM呼び出し
   なし)。
3. DB照合+Section D evidence schema生成。
4. Section E除外Gate観測項目を出力(閾値は決めず、Fable/ユーザーが
   目視確認できる表形式で提示)。
5. 4〜5件確保できない本文があれば、Section F-2のfallback(1 LLM call)
   を実行(このときのみAPI費用が発生、既存Key Phrase選定と同程度の
   単価想定)。
6. 既存Key Phrase Production経路(現行方式)の同一本文に対する選定
   結果と並べて比較表を作成する(内容の質の違いは人間判断、Trialでは
   「同じ本文から何が選ばれるか」を並べるところまでとし、どちらが
   優れているかの判定はユーザーに委ねる)。

### H-3. 受入観測項目

- 4〜5件確保できた本文の割合(fallback発動率)。
- 除外Gate各項目の該当件数分布(Section E表)。
- 複数DB一致件数・phrase系件数の実測分布。
- 既存Key Phrase Production経路の結果との重複率・差分件数。
- 実測コスト(LLM call数×実測単価、Web access回数=0の確認)。
- 実測latency(抽出+照合+除外Gate、fallback有無別)。

### H-4. 費用見積

- Trial自体の費用: DB取得(¥0、公開データの直接ダウンロード)+
  deterministic抽出・照合(¥0、API呼び出しなし)+ fallback発動分の
  みLLM費用(1本文あたり¥5〜15程度×fallback発動本文数)。
- 6本文全てでfallbackが発動した場合の上限目安: ¥30〜90程度
  (既存単価からの外挿、実測ではない)。

### H-5. 既存Key Phrase Production経路との互換性

- Key Phrase block形式: Section 0の設計方針どおり、Canonicalization
  段階(`source_span→key_phrase→used_form`)をそのまま維持するため、
  `p9a.build_key_phrase_block()`側のI/Fは変更不要と見込む(Trialで
  実際に既存canonicalizationモジュールへDB照合由来の候補を通して
  確認する必要がある。現時点では設計上の見込みであり検証済みでは
  ない)。
- TTS/Secondary ASR: `used_form`/`ja_gloss`が最終的に既存経路と同じ
  フィールド名・値の型で出力される限り、TTS/Secondary ASR側の変更は
  不要と見込む(同上、未検証)。

---

## STOP条件チェック(該当なし/該当ありの記録)

- 商用利用・ローカル取込条件不明: 該当あり(EVP・PHRASE List・PHaVE
  List・Academic Collocation List)。ただしこれらをTrial/参考群へ
  退避し、群1(CEFR-J・NGSL系・Wiktionary)だけでTrialを成立させる
  設計にしたため、**設計全体としてはSTOPしない**。群2 DBを
  Productionへ加えたい場合は、各発行元への個別確認が別途必要
  (`USER_DECISION_REQUIRED`として`OPEN_ITEMS.md`への新規起票を提案、
  本タスクではSSOT編集を行わずRESULT_PACKETで提案のみ)。
- 有力DB間のライセンス衝突: 明確な衝突は確認されていない(B節参照)。
  Wiktionary ShareAlike条項は内部利用限定という運用ルールで対応
  可能と考えられる(断定はしない)。
- 網羅抽出にLLM常時利用が必要: 現時点のdry-run(Section C-4)からは
  「n-gram生成自体は完全にdeterministic・低コストで可能」ことは
  確認できたが、「DB一致だけで常に4〜5件確保できるか」はTrialで
  実データを見ないと判定できない。**この点はSTOPではなく
  Trial実施が必要な未検証事項として明記する**。
- deterministic抽出で重大な漏れ: 未検証(discontinuous phrasal verb・
  複数語表現の活用形正規化は新規ロジックが必要、Section C-3)。
- 除外Gate未決でTrialが成立しない: 該当しない(閾値を決めずに
  observationベースでTrialを実施する設計にしている)。
- Production DB候補がほとんど確保できない: 該当しない(群1で3系統
  確保済み)。
- 既存Key Phrase仕様との重大な互換性問題: 現時点で確認されていない
  (Section H-5、ただし未検証)。
- 想定より大きなコスト: 該当しない(Section Gの試算では現行以下と
  見込まれる)。

**総括: 本設計は`DESIGN_READY_FOR_TRIAL`として妥当と考えられるが、
群1DBの実際のphrase/idiom cover率・fallback発動率・discontinuous
phrasal verb対応の実装難易度はTrialでの実測が必要であり、これらは
「未検証」として明記した上でユーザー判断を仰ぐ。**
