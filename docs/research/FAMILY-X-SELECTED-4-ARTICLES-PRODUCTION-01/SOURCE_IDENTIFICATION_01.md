# SOURCE_IDENTIFICATION_01(FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01、2026-10-29)
選定フォーム概要はFact扱いしない。原文取得はcurl(2026-10-29 JST夕〜夜)。原文本文の控えは`source_texts/`。
注: 選定元`family_x_topic_selection_2026-10-29.html`はrepo・user_test配下に存在せず(find/ls確認)、GitHub issue #23も本環境(gh未導入)から取得不可。URL・タイトルは委任文のものを使用。

| # | 記事 | slug | 原記事(特定結果) | 一次情報 |
|---|---|---|---|---|
| ② | 部屋は少し散らかっている方が家族はうまくいく？ | untidiness_family_resource | GIGAZINE 2026-10-29「部屋は多少散らかっている方が家庭にとってよいという研究結果」(URL取得200、続きは会員限定だが主要部分は取得済) | ScienceDirect論文 pii S0148296326006168「The Upside of Mess: Conceptualising (Dis)order as a Dynamic Family Resource」(Abarashi et al.)、The Conversation解説 294343 |
| ④ | AIに勧められた商品、気づかないうちに選ばされている？ | ai_chat_sponsored_persuasion | **特定**: ITmedia NEWS 2026-10-29 12:00「AIチャットが勧める広告商品、選択率が約3倍に　こっそり他商品けなし誘導　米研究者らが検証」(連載「ちょっと昔のInnovative Tech」) https://www.itmedia.co.jp/news/article/2610/29/2000002680/ | arXiv:2604.04263 Salvi, Cuevas, Horta Ribeiro「Commercial Persuasion in AI-Mediated Conversations」(2026-04) |
| ⑨ | AIペットは、たまごっちの次のブームになる？ | meta_waddle_world | GIGAZINE 2026-10-29「Metaがたまごっち風のAIペットを育てて会話するアプリ「Waddle World」をこっそりリリース」 | App Store(ph)/Google Play公式説明、Matt Navarra氏投稿、TechCrunch(GIGAZINEが言及) |
| ⑭ | 地球の外にある天体、光だけでどこまで探せる？ | jwst_mystery_emission_line | ナゾロジー 2026-10-29「天文学者も首をかしげる「謎の光」が、何も写っていない宇宙から届いていた」(3ページ構成、全頁取得) | The Astrophysical Journal 2026-09-22 doi:10.3847/1538-4357/ae9a94(Huberty et al.、MOCSS) |

## ④ 特定の根拠
- ITmedia NEWSのRSS(news_bursts/news_technology、2026-10-29前後)のAI関連全件を確認。「AIに勧められた商品/選ばされる」に該当するのは上記1件のみ(他は決算・Muse提携・RentAHuman等で非該当)。代替候補なし。
- 本文: 2012人・約5500冊の電子書籍・5モデル(GPT-5.2/Claude Opus 4.5/Gemini 3 Pro/DeepSeek v3.2/Qwen3 235b)、検索上位表示22.4%/チャット先頭配置26.8%/説得指示61.2%(約3倍)、Sponsoredラベル明示でも55.5%、さりげなく誘導40.7%(見抜けた人9.5%)。選択後の満足(1ドルと交換するか)は条件間で有意差なし。選ばされていることに「気づかない」という方向性は本文と整合。
- 注意: 記事は4月公表の論文を取り上げた「ちょっと昔」連載。タイトルの『気づかないうちに』は9.5%/35.1%の特定精度で裏付く。『選ばされている』は実験条件(スポンサー指示を与えたAI)に限る点を本文で正確に扱う。

## ⑨ 注意(タイトルと内容の差)
タイトルの『次のブームになる？』は原記事では断定されない(TechCrunchが将来のAIペット型デバイスの先駆けになる可能性を指摘、ただしMuse Charmとの具体的関連は未確認とGIGAZINEが明記)。Waddle Worldはフィリピン限定提供・18歳以上。本文は「問い」として扱い、ブーム到来を事実として書かない。

## ⑭ 同一ニュースの別切り口候補との関係
選定フォーム本体を入手できないため、フォーム内の別切り口候補は確認不能(未確認)。ナゾロジー記事は論文(Huberty et al.、ApJ 2026-09-22)の解説で、「光だけで未知の天体を探す観測法MOCSS」と「正体不明の1本の輝線」が主題。タイトルの『地球の外にある天体、光だけでどこまで探せる？』=観測法(事前に天体を選ばないスリットレス分光)の側面に対応。別切り口候補(例: 『謎の光』側の切り口)があっても同一論文なので、本文は論文の事実(42本中大半は既知銀河、1.60μmの1本は持ち主不明、4種類の線で説明困難、正体未確定)に合わせる。一次情報はResearch段で論文を確認する。
