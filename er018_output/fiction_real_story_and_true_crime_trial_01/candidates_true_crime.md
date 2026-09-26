# FICTION-REAL-STORY-AND-TRUE-CRIME-TRIAL-01 -- candidates_true_crime.md (3-B Historical True Crime)

Trial専用。Production Fiction仕様への反映は本タスクの対象外。到達上限VALIDATED。
Gate定義はFICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02(VALIDATED)を流用。
すべて1930年より大幅に前の事件・刊行物(現代事件は対象外)。

## 方法論上の注記

委任文で例示された`chroniclingamerica.loc.gov`および`www.loc.gov`の検索エンドポイント
(`/search/pages/results/`等)は、本Trial実行時点でCloudflareの`Just a moment...`
チャレンジページを返し(HTTP 403相当、JS実行が必要)、直接HTTP GETでの検索・取得が
できなかった(Trial-02がLOCの個別アイテムページで遭遇した403と同種の問題。今回は
`tile.loc.gov`のような回避経路も見つからず)。そのため、委任文が代替として明示した
「古いPublic Domainの犯罪記録」「Public Domainのhistorical crime collections
(例: The Newgate Calendar等)」の経路を採用し、Project Gutenberg上の
**Camden Pelham『The Chronicles of Crime; or, The New Newgate Calendar』(1841年、
vol.1、Gutenberg #46585)**から3件の実在事件を候補として検討した。この本自体が
1841年出版のNewgate Calendar系犯罪記録集であり、委任文の例示にそのまま合致する。

著者「Camden Pelham」はpseudonym(筆名)であることをLibrary of Congress Name
Authority(`id.loc.gov/search/?q=Camden+Pelham&format=json`、Cloudflare非対象で
直接HTTP GET可能)で確認した("Pelham, Camden, pseud" という表記が複数の書誌
レコードに一貫して現れる)。日本の著作権法は無名・変名の著作物について公表後70年
(実名の届出等がない場合)としており、1841年公表から70年は1911年で遥かに経過済み
のため、没年が特定できない筆名著者でも日本におけるPD状態は明確である。

## 候補表

| Source(Pelhamの各項目) | 一次テキスト確認(URL/HTTP status/該当箇所引用、約200語) | 権利(日本/米国) | G1〜G4・事実性 | 採用/非採用 | 理由 |
|---|---|---|---|---|---|
| **[採用]** Eugene Aram(1745年殺人、1758年白骨発見、1759年処刑) | https://www.gutenberg.org/ebooks/46585.txt.utf-8 / HTTP 200 / "On the 8th of February 1745, in conjunction with a man named Richard Houseman, he committed the murder... Fourteen years afterwards elapsed... a labourer named Jones was employed to dig for stone in St. Robert's Cave... he found the bones of a human body... Houseman... exclaimed, 'This is no more Daniel Clarke's bone than it is mine!'... He was executed at York on the 16th August 1759."(全文はprimary_text_evidence/eugene_aram_full_case_section.txt) | Pelham(1841年出版、pseud、id.loc.gov確認)/日米ともPD(上記「方法論上の注記」参照) | G1 PASS(全文取得・確認)/G2 PASS/G3 PASS(単一arc、280-420語へ圧縮可能)/G4: A是(中心事件=14年後の白骨発見と自白の連鎖)・B是(ミステリー的関心、共犯者の恐慌による自白という劇的転換)・C是(平穏な14年間から突然の破綻へ)・D是。事実性: Wikipediaの独立記述(発見1758年・裁判1759年8月)とも整合。 | **採用** | 単一の明確な中心事件(埋もれた殺人の偶然の発覚)、雄弁だが失敗する法廷弁論という知的興味、必要以上に暴力描写を伴わずに成立する(実際の殺害場面は「数回殴打し倒れるのを見た」程度の簡潔な記述のみ)。原文にある自殺未遂・晒し刑等のより凄惨な事後処理の詳細は、事実改変ではなく尺調整のための省略として扱った(fidelity_true_crime.md参照)。 |
| Jonathan Bradford(オックスフォードの宿屋主人が無実の罪で処刑された誤判事件) | https://www.gutenberg.org/ebooks/46585.txt.utf-8 / HTTP 200 / "The details of this case reach us in a very abridged form; and we have been unable to collect any information on which any reliance can be placed beyond that which is afforded us by the ordinary channels."(編纂者自身が情報の信頼性の限界を明記。全文はprimary_text_evidence/jonathan_bradford_excerpt.txt) | 同上(Pelham 1841年、PD) | G1 PASS(取得・確認)/G2 PASS/**G3 FAIL**(原文自体が数百語程度と極端に短く、編纂者が「信頼できる詳細情報が集められなかった」と明記している)/G4: 発想としては興味深い(状況証拠の危険性を示す教訓話、実際の真犯人は使用人だったという反転)が、A/Dは事実上「原文に情報がなさすぎて、280-420語へ展開するには本文にない場面・心理描写を創作する必要がある」という問題 | **非採用** | 情報密度が薄すぎるため、委任文の「資料に無い動機・台詞・心理描写を創作しない」制約下で280-420語の物語を構成すると、資料にない場面(客室での発見の様子、使用人の犯行動機等)を実質的に創作せざるを得ない。フィクションではなくTrue Crimeとしての忠実性要件を満たせないため除外。 |
| Mary Blandy(1752年、父親を毒殺したとして処刑された女性) | https://www.gutenberg.org/ebooks/46585.txt.utf-8 / HTTP 200 / "Captain Cranstoun... informed her that he was engaged in a disagreeable lawsuit with a young lady in Scotland who had claimed him as her husband... Mr. Francis Blandy was an attorney residing at Henley-on-Thames..."(全文はprimary_text_evidence/mary_blandy_excerpt_opening.txt) | 同上(Pelham 1841年、PD) | G1 PASS/G2 PASS/G3 PASS(情報量は十分、圧縮可能)/G4: A是(中心事件=既婚の年上将校に騙され「惚れ薬」と称する粉末を父に盛った末の毒殺)・B是(著名な事件、道徳的複雑性)・C是(恋愛感情による判断の誤り、破滅)・D是 | 採用可能(今回は非選択) | G1〜G4すべてPASS(4/4)の有力候補だったが、(a)実の父親の毒殺という主題は「被害者・犯罪描写を必要以上に残酷にしない」という委任文の配慮により一層の慎重な扱いを要すること、(b)Eugene Aramの「隠された秘密が14年後に偶然発覚する」という構造の方が、単純な家庭内毒殺劇より知的興味(状況証拠論・法廷弁論の対比)の点で新規性が高いと判断し、今回はAramを優先した。Blandy案は将来のバックログとして有効(候補として記録のみ)。 |

## 費用・調査方法

- 一次テキスト取得はすべて直接HTTP GET(`requests`、Project Gutenberg `.txt.utf-8`)で実施し、web_search呼び出しは0回・$0。
- `chroniclingamerica.loc.gov`および`www.loc.gov`検索エンドポイントはCloudflareブロックのため利用不可だった(上記「方法論上の注記」)。`id.loc.gov`(Library of Congress Linked Data Service、Name Authority検索)はCloudflareの対象外で直接HTTP GET可能だったため、著者名の典拠確認にのみ使用した。
