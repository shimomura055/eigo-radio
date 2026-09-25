# audit.md — ADVANCED-VOCAB-DIFFICULTY-AUDIT-01

Auditのみ、仕様変更なし。API呼び出しなし(ローカル計算のみ、wordfreq由来の既存頻度順位リストとer015系lemma正規化ヒューリスティックを再利用)。

## 使用本文

- meta: `er012_output\e_family_two_level_wiring_01\meta\b1b\article.md` — Production E2E版、採用済み本文(er012_output/.../meta/b1b/article.md)。
- sewer: `er015_output\news_natural_advanced_standard_a2_trial_01\a1_advanced_sewer.md` — Production E2E側はdeviation MAJORで採用版が無い(sewer/b1b/audit/rejected_advanced_attempt2.md, deviation_check.json overall_status=LEDGER_DEVIATION)ため、Trial採用版(er015_output/news_natural_advanced_standard_a2_trial_01/a1_advanced_sewer.md)を使用。

### Meta Top 10(難語候補、頻出順位が低い順)

| Rank | Word / Lemma | 記事中の実際の形 | 一般英語の頻出順位 | 日本語意味 | 種別 | コメント |
|---|---|---|---|---|---|---|
| 1 | concierge | concierges | > 20000 (zipf=1.7) | コンシェルジュ(案内・取次係) | 業界語(サービス業由来、比喩的使用) | Advancedとして妥当。Meta社内呼称"human concierges"の直接引用であり記事固有性が高い一方、意味は一般にも通じる語。20,000位圏外(zipf=1.7、かなり低頻度)。Key Phrase候補になり得る。 |
| 2 | onstage | onstage | 15670 | 舞台上で、人前で | 一般語(やや文語・比喩表現) | "Who is speaking onstage?"という記事全体の比喩(舞台/演者)の一部。記事固有性が高いが、比喩表現として他文脈でも再利用価値あり。 |
| 3 | understandable | understandable | 10629 | 理解できる、もっともな | 一般語 | Advancedとして妥当、頻度は中程度。他文脈でも再利用価値あり。 |
| 4 | curtain | curtain | 8776 | 幕、カーテン | 一般語 | "behind the curtain"という定型句の一部(コメント: 単語単位で難易度を表しにくい)。基礎語彙に近く、Advancedとしてはやや易しい部類。 |
| 5 | pause | pause | 7166 | 一時停止、保留(put ... on holdと同義で使用) | 一般語 | Advancedとして妥当、他文脈でも再利用価値が高い一般語。 |
| 6 | leak | leaked | 6160 | 漏れる、漏洩する | 一般語 | Advancedとして妥当。プライバシー文脈で再利用価値が高い。 |
| 7 | convenient | convenient | 5588 | 便利な | 一般語 | Advancedとして妥当、頻度もそこまで低くない基礎的形容詞。 |
| 8 | unexpect | unexpected | 4907 | 予想外の(unexpected、simple_lemma()の規則活用ヒューリスティックにより語尾-edが削られた表示。実際の形はunexpected) | 一般語 | Advancedとして妥当、他文脈でも再利用価値が高い一般語。 |
| 9 | piano | piano | 4258 | ピアノ | 一般語(比喩表現、"hidden inside the piano"の一部) | 記事中心比喩(黒子の演奏者)の一部。記事固有性が高いが、一般語としての頻度自体は中程度。 |
| 10 | privacy | Privacy | 3898 | プライバシー、個人情報保護 | 一般語 | Advancedとして妥当、他文脈でも再利用価値が高い一般語。 |

### Sewer Top 10(難語候補、頻出順位が低い順)

| Rank | Word / Lemma | 記事中の実際の形 | 一般英語の頻出順位 | 日本語意味 | 種別 | コメント |
|---|---|---|---|---|---|---|
| 1 | septic | septic | > 20000 (zipf=3.21) | 浄化槽の、汚水処理の(septic tankで「浄化槽」) | 専門語(環境インフラ用語) | septic tank(浄化槽)という専門語の一部。記事理解上重要な専門語で除外対象ではないが、20,000位圏外(zipf=3.21、かなり低頻度)。記事固有性が高い。 |
| 2 | sewer | sewers | > 20000 (zipf=3.22) | 下水道、下水管(このエントリは複数形sewersの語幹処理結果) | 技術語(インフラ用語、ただし比較的一般にも浸透) | 記事タイトル語であり中核語。20,000位圏外(zipf=3.22、かなり低頻度)。Advancedとして妥当。simple_lemma()の限界により単数形sewerは別lemma"sew"として分裂している(下記参照)。 |
| 3 | wastewat | wastewater | 18216 | 排水、汚水(wastewater、simple_lemma()の既存ヒューリスティックにより語尾-erが比較級とみなされ削られた表示。実際の形はwastewater) | 技術語(環境インフラ用語) | 記事理解上重要な専門語。かなり低頻度だが下水道記事の中核語のため妥当。Key Phrase候補になり得る。 |
| 4 | artery | artery | 12006 | 動脈(比喩: 幹線) | 一般語(比喩表現、やや専門[解剖]語由来) | "hidden main artery"という中心比喩の一部。記事固有性が高いが、比喩表現として他文脈でも再利用価値あり。 |
| 5 | sew | sewer | 11459 | 下水道、下水管(このエントリは単数形sewerの語幹処理結果。"sew"[縫う]という別の一般語と同形になっているが、記事中の実際の形はsewerであり縫うの意味ではない) | 技術語(インフラ用語) | 上のsewer(複数形由来)エントリと同一語の表記ゆれ。simple_lemma()の既知の限界(既存ロジックそのまま、本Auditでは修正しない)により別lemmaとして分裂しているだけで、Advancedとしての妥当性評価は同上。 |
| 6 | municipality | municipalities | 11073 | 自治体、市町村 | 一般語(行政・ニュース語彙) | Advancedとして妥当、ニュース記事で頻出する一般的な語。 |
| 7 | flush | flush | 9610 | (トイレを)流す、洗い流す | 一般語 | Advancedとして妥当、下水道記事で再利用価値が高い一般語。 |
| 8 | convenience | convenience | 6887 | 便利さ | 一般語 | Advancedとして妥当、他文脈でも再利用価値が高い一般語。 |
| 9 | surprisingly | surprisingly | 6187 | 驚くほど、意外にも | 一般語 | Advancedとして妥当、他文脈でも再利用価値が高い一般語。 |
| 10 | invisible | invisible | 6153 | 目に見えない | 一般語 | Advancedとして妥当、他文脈でも再利用価値が高い一般語。 |

## Band別語数(参考、既存band方式の再利用)

- meta: A(<=3000)=96 / B(3001-5000)=5 / C(5001-10000)=4 / D(>10000)=3 / proper_noun=5 (異なり語数、既存bmod.measure_bands方式をそのまま再利用)
- sewer: A(<=3000)=98 / B(3001-5000)=10 / C(5001-10000)=8 / D(>10000)=6 / proper_noun=0 (異なり語数、既存bmod.measure_bands方式をそのまま再利用)

## 確認事項

1. **2記事共通傾向**: いずれもTop 10の大半が、記事の中心比喩(Meta: onstage/curtain/piano、Sewer: artery)または専門・業界語(Meta: concierge、Sewer: septic/wastewater/sewer(+sew))に集中している。純粋な「一般語だが理由なく難しい語」はunderstandable/pause/leak/convenient/privacy/municipality/flush/convenience/surprisingly/invisible程度で、いずれも一般英語として妥当な難度に見える。
2. **明らかに過剰な語の有無**: 機械測定上「明らかに過剰(記事の意味に無関係な難語)」と言えるものはTop10には見当たらなかった。Meta記事のcurtain("behind the curtain"定型句)は単独では頻度が低く出るが、複合表現としてはむしろ易しい部類であり、単語単位測定の限界(定型表現の過大評価)の例と考えられる。
3. **Standardと同じ順位制約をAdvancedへ適用可能そうか(所見、判断ではない)**: Standard側で使われているA(<=3000)/B(3001-5000)という帯をそのままAdvancedの合格基準として適用すると、Sewerのseptic(20,000位圏外)/sewer(圏外)/wastewater(18216位)、Metaのconcierge(圏外)/onstage(15670位)/artery(12006位)等、記事の核となる専門語・中心比喩語・タイトル語まで「置換対象」に含まれてしまう見込みである。Standard側の帯制約を無調整でAdvancedへ適用すると、記事の意味・比喩構造・タイトル語を壊すリスクが高いという所見のみ記録する(仕様上の要否判断はしない)。
4. **順位データSource**: wordfreq 3.1.1 (`wordfreq.top_n_list('en', 20000)`、PyPI/Apache-2.0、既存install[NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01/NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01で導入済み]を再利用、追加installなし)。20,000位圏外の語(rank=None)については、`wordfreq.zipf_frequency(word, 'en')`をその場で呼び出して補助値(値が小さいほど低頻度)を補い、"> 20000 (zipf=X.XX)"として表示・圏外語同士の並べ替えに使用した(順位そのものの補完ではなく、相対的な低頻度さの目安)。
5. **既存実装(再利用のみ、新規ロジックはlemma単位グルーピングのみ)**: 順位lookup=`bmod._word_band`(`er015_news_standard_a2_vocab_banding_trial_01.py`)、lemma化=`v3mod.simple_lemma`/`simple_lemma_candidates`、content word抽出=`v3mod.extract_content_words`(機能語・数字・記号・URLは正規表現[A-Za-z]+と`FUNCTION_WORDS`により自動除外)、固有名詞判定=`v3mod.capitalized_positions`(いずれも`er015_news_standard_a2_vocab_effectiveness_trial_01.py`)。
6. **使用本文path**: 上記「使用本文」節に記載の通り。Meta記事はProduction E2E採用版(`er012_output/e_family_two_level_wiring_01/meta/b1b/article.md`)、Sewer記事はProduction側にdeviation MAJOR (`er012_output/e_family_two_level_wiring_01/sewer/b1b/audit/deviation_check.json` overall_status=LEDGER_DEVIATION、rejected_advanced_attempt2.md)で採用版が無いため、Trial採用版(`er015_output/news_natural_advanced_standard_a2_trial_01/a1_advanced_sewer.md`)を使用した。
7. **限界・注記**: (a) lemma化は規則活用のみ対応(不規則活用は非対応、既存限界の継承)。同じ既存ヒューリスティックの限界の実例として、Sewer記事のsewer(単数)とsewers(複数)が別lemma("sew"と"sewer")に分裂した(末尾-erを比較級とみなして削る既存ルールが単数形にのみ適用されたため)。本Auditでは新規ロジックを追加せず、既存simple_lemma()のままの挙動を忠実に反映し、Top10表では両エントリにコメントで相互参照を付けた。(b) 固有名詞判定は機械ヒューリスティック(文頭以外での大文字出現)であり、全て大文字の略語等を誤判定しうる(既存限界の継承)。(c) 複合語・定型表現(curtain[behind the curtain]/artery[hidden main artery]/pause[put on hold]/septic[septic tank]等)は単語単位のTop10には反映されるが、本来は複合語・定型表現としての自然さ判断が必要であり、表内のコメント欄に個別注記した(表からは外していない)。(d) 日本語意味・種別・コメント欄はSonnetによる目視注記であり、Top10語のみ整備した(全lemmaへは付与していない、`words_ranked_{meta,sewer}.json`には未注記のまま含まれる)。(e) unexpect(Meta)・wastewat(Sewer)はsimple_lemma()が末尾-edや-erを規則活用として削った結果の表示lemmaであり、記事中の実際の形(unexpected/wastewater)は「記事中の実際の形」列に別途示した。