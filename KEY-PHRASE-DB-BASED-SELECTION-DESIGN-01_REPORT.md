# KEY-PHRASE-DB-BASED-SELECTION-DESIGN-01_REPORT.md

管理ID: KEY-PHRASE-DB-BASED-SELECTION-DESIGN-01(Sonnet実行、2026-09-27)

性質: **設計フェーズのみ**(到達最大Status=`DESIGN_READY_FOR_TRIAL`)。
Production code・Prompt・CURRENT_SPECのProduction仕様は一切変更して
いない。DB照合→選定の実Trialも実行していない。API費用**¥0**
(OpenAI web_search・LLM呼び出しは一切使用せず、公式サイト・
リポジトリへの直接HTTP GETのみで一次情報を取得)。

詳細設計: `docs/pm/design_key_phrase_db_based_selection_01.md`
DB調査(逐語ライセンス引用+URL+取得日時): `docs/pm/db_survey_key_phrase_sources_01.md`

## 1. 使えそうなDB一覧

Oxford 3000/5000、Oxford Phrase List、English Vocabulary Profile
(Cambridge)、CEFR-J Vocabulary Profile(東京外国語大学)、NGSL/NAWL/
NGSL-S/BSL(New General Service List Project)、PHRASE List(Martinez &
Schmitt 2012、idiom的表現505件)、PHaVE List(Garnier & Schmitt 2015、
phrasal verb 150件)、Academic Collocation List(Pearson、collocation
2,469件)、Wiktionary(英語版、word/phrase/idiom/discourse expression)
の計9件を調査。

## 2. Productionへローカル取込可能なDB

- **CEFR-J Vocabulary Profile**: 商用利用込みで無償(引用表記必須)。
  東京外国語大学のページに逐語で明記あり。
- **NGSL/NAWL/NGSL-S/BSL**: 公式サイトに「Free under Creative
  Commons, including commercial use」と明記。
- **Wiktionary**: CC BY-SA 4.0(商用可、ただし「同一ライセンスで
  再配布」という条件があり、社内の照合専用DBとして非公開利用する
  分には問題になりにくいと考えられる)。

いずれも単体では手薄な面がある(CEFR-J・NGSLは単語中心、Wiktionaryは
phrase/idiomの網羅性・タグ精度が未検証)ため、3つを組み合わせて
使う設計にした。

## 3. ライセンス上保留のDB

- **Oxford 3000/5000・Oxford Phrase List**: 利用規約に「商業目的での
  利用禁止」と明記(私的・家庭内利用限定)。商用利用にはOUPとの別契約
  が必要で、今回は取得していない。
- **English Vocabulary Profile(Cambridge)**: サイトがJavaScript製で
  詳細規約を直接取得できなかったが、姉妹サービスのCambridge
  Dictionaryのデータライセンスページには「データ利用は個別見積り」
  と明記されており、無償の一括データ利用は期待しにくい。
- **PHRASE List・PHaVE List・Academic Collocation List**: 著者/発行元
  のページに明確な商用可否の記載が見つからず、`UNRESOLVED`(未確認を
  「不可」とも「可」とも推測していない)。

## 4. 本文からどう広く候補を拾うか

最初にAIで絞り込まず、本文の1〜5語すべての組み合わせ(n-gram)を
機械的に生成し、そのあとで上記DBと照合する設計。実際に既存記事6本
(Meta a2/b1b、small_bag run_02 a2/b1b、hormuz run_02 a2/b1b)へこの
n-gram生成だけを試したところ(DB照合なし、選定なし、¥0)、1記事
300〜360語に対し、1〜5語の組み合わせ候補が合計で1,500件前後発生する
ことを確認した(詳細は下記5.)。

## 5. DB照合後の候補一覧の想定(dry-run候補数表)

| 記事 | 総語数 | 1語候補(unique) | 2語 | 3語 | 4語 | 5語 |
|---|---:|---:|---:|---:|---:|---:|
| Meta A2 | 317 | 145 | 288 | 309 | 312 | 313 |
| Meta B1 | 336 | 163 | 309 | 331 | 333 | 332 |
| small_bag A2 | 305 | 166 | 268 | 294 | 300 | 300 |
| small_bag B1 | 313 | 177 | 282 | 304 | 308 | 308 |
| Hormuz A2 | 360 | 187 | 324 | 348 | 353 | 354 |
| Hormuz B1 | 345 | 188 | 316 | 337 | 339 | 339 |

DB照合をかけた後の実際の一致件数(何件がCEFR-J/NGSL/Wiktionaryと
一致するか)は、DBを実際にローカル取込みしてTrialを行わないと分から
ない(今回は生成量の確認のみ、¥0)。

## 6. 想定追加コスト・latency

現行方式(既存Key Phrase生成)は1レベルあたり通常2回のAI呼び出し
(候補選定+表記整え)で、実績ログでは1レベル¥5〜15程度(失敗・
やり直し発生時は¥27〜70程度まで上振れした実例あり)。DB照合方式
では「候補選定」をAI呼び出しからDB照合(無料・高速)に置き換え、
「表記整え」のAI呼び出し1回は現行どおり残す設計とした。DB照合で
候補が4〜5件確保できない場合のみ、不足分を補うAI呼び出しを1回追加
する。したがって通常時は現行の半分程度(1回)のAI呼び出しで済み、
コストは現行以下になると見込まれる(ただし按分は仮定であり実測では
ない)。ローカル処理(語の切り出し・DB照合)自体の追加費用は¥0
(インターネットアクセス不要、記事生成のたびに外部通信しない設計)。

## 7. Trial具体案

Meta・Hormuz・small_bagの既存確定本文(Advanced/Standard、最大6本文)
を対象に、(1)DB取込み→(2)本文からのn-gram抽出→(3)DB照合→(4)除外
(簡単すぎる・固有名詞・記事固有すぎる等を機械的/人力で除く)→
(5)4〜5件に届かない場合のみAI呼び出しで補完、という手順で実施する
Trialを提案。既存のKey Phrase選定結果と並べて比較する。実施予定
コストは、DB取込み・抽出・照合が¥0、AI呼び出しが発動した記事分のみ
1記事¥5〜15程度(全6記事で発動しても目安¥30〜90程度)。**本タスク
ではこのTrial自体は実行していない。**

## 8. Trial前にユーザー判断が必要な事項(推奨案+理由)

1. **English Vocabulary Profile(Cambridge)・Oxford系DBを個別に商用
   契約するかどうか**: 現状はライセンス条件が壁になり除外している。
   推奨: いったんCEFR-J・NGSL・Wiktionaryの3つだけでTrialを実施し、
   phrase/idiom側の一致件数が実際に不足するようであれば、その時点で
   追加契約の要否を判断する(先に契約費用をかけない)。
2. **PHRASE List/PHaVE List/Academic Collocation Listの著者・発行元へ
   商用利用可否を直接問い合わせるかどうか**: 現状は「未確認」であり
   使っていない。推奨: 内容的な魅力(phrasal verb・collocationの
   実証的リスト)は高いので、Trial結果を見てから問い合わせの要否を
   判断する(今すぐ問い合わせなくてもTrialは成立する設計)。
3. **Wiktionary由来データのShareAlike条項をどう扱うか**: 社内限定の
   照合用DBとして使う分には支障が小さいと考えられるが、将来この
   複合DB自体を何らかの形で外部に出す(公開・販売等)予定があるかは
   ユーザーの事業判断次第。推奨: 現時点では「非公開の内部照合専用」
   という運用ルールを明記した上でTrialへ進める。

## 9. リスク

(Fableレビュー欄、空欄)

## 10. 次に進めてよい作業・まだ進めてはいけない作業

- 進めてよい(ユーザー承認があれば): 群1DB(CEFR-J・NGSL系・
  Wiktionary抽出)のローカル取込み実装、Section H記載のTrial
  (既存6本文への適用、AI呼び出しは不足時のみ発生)。
- まだ進めてはいけない: 本設計をProduction Key Phrase経路へ配線する
  こと(`APPROVED_FOR_PRODUCTION`はユーザーのみが決定)。群2DB
  (Oxford系・EVP・PHRASE/PHaVE/ACL)を商用契約なしにProductionへ
  組み込むこと。Discontinuous phrasal verb検出等、未実装ロジックの
  実装(Trialで実データを見てから)。

## 費用・証跡

- API費用: ¥0(HTTP GETのみ、LLM呼び出し0回)。
- コミット: `<commit_hash>`(本レポート直後に記載)
- raw URL: 本レポートpush後に追記。
- 詳細証跡: `docs/pm/design_key_phrase_db_based_selection_01.md`、
  `docs/pm/db_survey_key_phrase_sources_01.md`

Management-ID: KEY-PHRASE-DB-BASED-SELECTION-DESIGN-01
