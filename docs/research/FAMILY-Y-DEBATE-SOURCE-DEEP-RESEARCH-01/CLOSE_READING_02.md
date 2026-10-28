# CLOSE_READING_02(FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01 委任_02: ◎ライセンス源の人物具体性の限定精読。調査のみ・API(LLM)0・費用0円)

実施: 2026-10-29 07:58〜08:05 JST(上限45分のうち約10分)。ユーザー原文§4「論理的賛否は豊富でも登場人物が評論家になる情報源は高く評価しない」を実測で確かめるために、Lane bが「Personaの作りやすさ」を『中』『低』とした2つの◎源(仏 Grand Débat National、Polis)で、**一人称の生活背景・職業・家族・感情が実際にどの程度書かれているか**を測った。登録≠採用承認、Production採用はユーザー判断待ち。

## 1. 取得(手動相当の単発取得。一括DLなし)

| 対象 | 取得 | 量 | ライセンス根拠(Lane b確認、再確認なし) |
|---|---|---|---|
| Grand Débat「環境」設問CSV `https://static.data.gouv.fr/resources/donnees-ouvertes-du-grand-debat-national/20200611-173104/la-transition-ecologique.csv`(64,239,619B)。data.gouv.fr/static.data.gouv.fr の robots.txt(07:58)は`/admin`・検索・一覧CSVのみDisallowで資源ファイルは対象外 | HTTP Range 2回(0-3999の見出し、3,000,000-4,199,999の本文窓)。UA=`Mozilla/5.0 (compatible; eigo-radio-research/1.0)`(自己申告型)。間隔3秒 | 全体の約1.9%(1.2MB窓。回答者638件、参照ID `2-1912`〜`2-2613`、2019-01-22 13:16〜14:34の投稿) | Licence Ouverte 2.0(複製・再配布・翻案・商用利用を許諾、出典表示が条件)。データセット=https://www.data.gouv.fr/datasets/donnees-ouvertes-du-grand-debat-national |
| Polis オープンデータ `austria-climate.5tzfrp5eaa.2022-07-07/comments.csv`(オーストリア気候市民会議、独語、2,138件) | `https://raw.githubusercontent.com/compdemocracy/openData/master/austria-climate.5tzfrp5eaa.2022-07-07/comments.csv` を単発GET1回(348,261B)。raw.githubusercontent.comのrobots.txtは404(なし) | 1ファイル | CC BY 4.0(README「All Polis data is licensed CC By 4.0」) |

読んだ範囲(「列N」=CSVの0始まりの列番号。列12=日常への影響の有無、列13=その理由、列15=自分の行動、列16=行動を変える条件、列17=負担できる解決策、列21=移動代替の条件、列25=自由記述): Grand Débatは「家族・働き方・車/移動」に関わる設問(列12-13 日常への影響、列15 自分の行動、列16-17 行動を変える条件、列21-22 移動手段の代替、列25 自由記述)を中心に、正規表現で絞った候補約30件を調査者が通読。Polisは全2,138件を機械集計し、自己開示候補25件を通読。**再現用script=`scripts_close_reading_02/`**(標準ライブラリのみ。入力は未commit。sha256先頭16桁: mid.bin=cd9c0a1d7fc5c1f8、head.bin=7514a92dd08e19d5、at.csv=a7db9ae7c7d090a6)。

## 2. 実測(正規表現による粗い代理指標。手読み判定ではない。語の誤検出・見落としがある)

Grand Débat(638件、空でない回答604件):

| 指標 | 件数(割合) | 備考 |
|---|---|---|
| 職業・通勤に触れる語(「je travaille」「mon métier」「domicile-travail」「retraité」「agriculteur」等) | 149(23.4%) | 「domicile-travail」のような設問用語の言及も含み過大 |
| 家族に触れる語(「mes enfants」「ma famille」「mon mari」等) | 39(6.1%) | |
| 距離の数値(「30km」等) | 57(8.9%) | |
| 感情語(「inquiet」「marre」「injuste」「colère」等) | 125(19.6%) | |
| 職業語かつ(家族語または距離) | 38(6.0%) | |
| 上記4種のうち3種以上を同じ回答者が書いた | 18(2.8%) | 手読みで確認した上位例が§3 |

Polis オーストリア(2,138件): コメント長の中央値106字。一人称+職業・居住地・家族・移動の具体を含む文は25件(1.2%)。うち6件(#14・#17・#18・#121・#124・#125)は運営側が置いた属性確認の定型文(「Eine Frage zu deiner Person: …」)なので、参加者が自発的に書いた自己開示は約19件(0.9%)。

## 3. 実例(原文+日本語要旨。Grand Débatは参照ID=CSV行`reference`、郵便番号上5桁、全て2019-01-22投稿)

出典URL(全例共通): CSVは上記static URL、データセット説明は https://www.data.gouv.fr/datasets/donnees-ouvertes-du-grand-debat-national 。出典表示(Licence Ouverte 2.0): 「Données ouvertes du Grand Débat National(data.gouv.fr)」。短い引用は精読の証拠としての掲載で、制作時は逐語転載しない。

**G1 参照ID `2-2195`(郵便番号60440)—地方の通勤者・子3人** (列16)
原文: 「vous ne pourrez pas me faire quitter ma voiture si aucun transport alternatif n'est possible (ex: je travaille à 30km, j'ai par ailleurs 3 enfants et aucun train, tram, bus à disposition!)」
要旨: 通勤30km、子ども3人、鉄道・路面電車・バスのいずれも無い。代替手段が無ければ車は手放せない、という人。職業は書かれていないが、距離・家族・怒りに近い口調が一続きで揃う最良級の例(列15でも堆肥化・暖房節約など実践を列挙)。

**G2 参照ID `2-2376`(25000)—山間の孤立した職場に通う女性** (列21)
原文: 「covoiturage impossible, je travaille à 52 kilomètres de chez moi dans une zone isolée de montagne et je suis la seule à aller là bas dans mon entourage. pas de transport en commun」
要旨: 52km先の山間の孤立した職場へ通う。同じ方向に通う知人がおらず相乗りも不可、公共交通なし。女性形の記述(列15: 「je suis attentive à la consommation électrique」)。自宅は地熱暖房・断熱・有機食品など、できる範囲の環境行動をしている点が「車だけは手放せない」の背景になる。

**G3 参照ID `2-2179`(91800)—小規模事業主** (列15・列21)
原文: 「chef d'une petite entreprise, je dois circuler en voiture avec du matériel pour intervenir chez mes clients : même la voiture électrique (déjà au dessus de mes moyens) ne me satisfait pas car très polluante à la production」
要旨: 客先に機材を積んで回る小さな会社の経営者。電気自動車は予算を超え、製造時の環境負荷にも納得できない。「やりたいが職業上できない」という職業理由が明示される例。

**G4 参照ID `2-2104`(69100)—規制に怒る低所得の運転者** (列25)
原文: 「ma voiture est classée en 4 et n'a que 150. 000 kilomètres et peut encore rouler deux ou trois ans … je n'ai pas les moyens financiers pour me payer un nouveau véhicule … les salaires n'augmentent plus et on voudrait me faire payer la facture de la transition écologique … c'est la DICTATURE écologique」
要旨: 2020年に導入される低排出ゾーン(ヴィルールバンヌ)でCrit'Air 4の自分の車(走行15万km)が走れなくなる。買い替える余裕がなく、賃金は上がらないのに環境の費用を負わされると憤る。目的には賛成だが「急ぎすぎ」とする複雑な感情。

**G5 参照ID `2-2325`(10150)—幼い子2人の親** (列13・列25)
原文: 「Inondation de toute ma propriete … mes enfants et moi même de plus en plus atteint par de simples pathologies respiratoires hivernales sévères et chroniques」/「Pour l'avenir de mes 2 garçons de 2 et 5 ans」
要旨: 自宅敷地の洪水、子どもと本人の慢性的な呼吸器疾患。2歳と5歳の息子たちの将来のために、と動機を語る。ただし同じ回答の後半は社会保障の不正受給批判など別論点へ広がる(テーマに沿った抜粋が必要)。

補足の例(都市の条件付き協力軸): 参照ID `2-2238`(78700)「Pour ma part je suis concerné par le RER ligne A et par la SNCF ligne Paris-Mantes, globalement lamentables」(パリ郊外の鉄道通勤者。代替手段が「清潔・安全・定時」なら乗るという条件。家族・職業は不明)。

Polis(CC BY 4.0、一文ずつ。出典: https://github.com/compdemocracy/openData/tree/master/austria-climate.5tzfrp5eaa.2022-07-07 、`comment-id`・同意/反対数):
- `#1098`(26/9): 「Ich wohne 5km vom nächsten Geschäft entfernt und hab keine Möglichkeit Öffis zu benutzen, sind nämlich ebenso weit entfernt」=最寄りの店まで5km、公共交通も同じ距離。
- `#215`(159/182): 「Ich arbeite mein Leben lang in der Automobilindustrie, in der Entwicklung und als testfahrer, E-Auto macht keinen Sinn!」=自動車産業の開発職・テストドライバー。職業が明示されるが、中身は主張のみで生活場面や家族は無い。
- `#1071`(87/21): 「Ich bin das letzte Mal 2011 geflogen」=2011年を最後に飛行機に乗っていない。生活習慣の断片のみ。
- `#317`(1/0): 「Ich habe keine Kinder und verzichte daher auf nichts!」=子無し、だから犠牲は感じない。
結論として、Polisの自己開示は**職業か居住か習慣のいずれか1点を1文で言うだけ**で、同じ人の職業・家族・感情が揃う例は確認できなかった。

## 4. 結論(「Personaの作りやすさ」の再評価)

1. **Grand Débat: 『中』を据え置き(上げない)。ただし根拠が実測で固まった**。638件中3要素以上を書く回答は18件(2.8%)、G1のように距離+家族+代替手段の無さが一続きに揃う例は数件だった。**供給量**(全体は約3万件規模[64MB÷1.2MB窓×638件の概算]のため、設問を絞れば候補は十分に出る)は確認できたが、**1人分の厚み**は1〜3文の断片で、年齢・職業・日々の生活場面・感情の経緯までは書かれない。名前・職業が回答者を特定する形で書かれることもなく、それはプライバシー上は望ましい。→ Debate系単独では『3 Voiceの一人称原稿』の素材として不足し、断片を束ねて別人格化する際に体験談系の補完が要る(Lane bの評価と一致)。
2. **Polis: 『低』を据え置き**。実在の肉声は匿名の一文(平均106字)で、自発的な自己開示は約0.9%。論点の発掘・票分布(同意/反対が拮抗する文の検出)には強いが、Personaの素材にはならない。
3. **テーマ単位の更新(TH-B1「自家用車を手放せるか」)**: Lane bは『職業・家族構成・感情は実在の発言から確認できていない』としていたが、Grand Débat精読で3軸それぞれに**職業・距離・子の数を持つ実在の断片**を確認できた(地方の通勤者=G1・G2、小規模事業主=G3、低所得で規制に反発=G4、都市の条件付き協力=`2-2238`と、Polis#27/#32の主張)。Family Y適性は『○』のまま(◎には上げない。根拠=断片が短く、一人称原稿の肉付けには別素材が要る)。
4. 設問選びの知見(制作時の収集設計の材料): 生活事情が出るのは列16(行動を変える条件)・列21(代替手段のために何が要るか)・列25(自由記述)。列12-13(気候の影響)は天候・健康の短い列挙が多い。
5. 限界: 窓は2019-01-22の最初の約78分に投稿された638件で、全体を代表しない(早期回答者に偏る可能性)。代理指標は粗い。精読は通勤・家族・生活の限定テーマで、国家制度・税の回答は対象外(国固有除外に該当)。Grand Débatの自由記述に他者の個人情報が混ざる可能性は残り(Lane b注意事項)、郵便番号は上2桁以下に丸めて扱うのが安全。
