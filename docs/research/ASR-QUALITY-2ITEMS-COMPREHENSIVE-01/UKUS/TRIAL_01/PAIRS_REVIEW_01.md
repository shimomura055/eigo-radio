# PAIRS_REVIEW_01 -- 固定対表(er111_ukus_pairs_v1.json)の人手レビュー結果(自動生成: er111_ukus_pairs_build_01.py --review-md)

- 件数: {"pairs_total": 15079, "active": 6361, "T1": 6356, "T2_inactive": 8718, "R": 5, "amb_uk2us": 168, "pron_differs_active": 52, "excluded": 146, "rule_new": 0, "rule_upgrade_T2": 5}
- 入力: VarCon 2020.12.07 / SCOWL 2020.12.07 (許諾文は json 冒頭 meta.license。breame不採用)。UK側=B/Zタグ(x/-なし)でA第一推奨でない語、US側=A第一推奨(OF-03)。
- レビュー観点: (a)編集距離>2/短語/語頭相違 (b)CMU両側登録で音素が異なる (c)両形が高頻度独立語 (d)AMB(用法付き)全件 (e)OF-04自動検出 (f)UK側定義拡張(Bv/B.)で増えた約430対 (g)規則(SCOWL固定)出力。
- レビュー者: 実装担当(Sonnet)。除外はすべて下表の理由付き。判断が割れるものは安全側(除外=従来どおりNG)。

## 1. 除外(146件)

| UK形 | US形 | 理由 | level |
|---|---|---|---|
| aeric | eric | OF04_uk_form_also_valid_us_elsewhere / unregistered | 80 |
| analogues | analogs | OF04_uk_form_also_valid_us_elsewhere / unregistered | 10 |
| analyses | analyzes | OF04_uk_form_also_valid_us_elsewhere / pron_differs | 20 |
| apprise | apprize | OF04_uk_form_also_valid_us_elsewhere / unregistered | 60 |
| apprise's | apprize's | OF04_uk_form_also_valid_us_elsewhere / unregistered | 60 |
| apprised | apprized | OF04_uk_form_also_valid_us_elsewhere / unregistered | 60 |
| apprises | apprizes | OF04_uk_form_also_valid_us_elsewhere / unregistered | 60 |
| apprising | apprizing | OF04_uk_form_also_valid_us_elsewhere / unregistered | 60 |
| areometric | aerometric | OF04_uk_form_also_valid_us_elsewhere / unregistered | 80 |
| busses | buses | OF04_uk_form_also_valid_us_elsewhere / pron_differs | 20 |
| castors | casters | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| catalyses | catalyzes | OF04_uk_form_also_valid_us_elsewhere / unregistered | 50 |
| caulked | calked | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| caulking | calking | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| caulking | caulk | OF04_uk_form_also_valid_us_elsewhere / pron_differs | 35 |
| caulks | calks | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| dialogue | dialog | OF04_uk_form_also_valid_us_elsewhere / pron_differs | 20 |
| dialyses | dialyzes | OF04_uk_form_also_valid_us_elsewhere / unregistered | 50 |
| digitalises | digitalizes | OF04_uk_form_also_valid_us_elsewhere / unregistered | 70 |
| diploe | diple | OF04_uk_form_also_valid_us_elsewhere / unregistered | 80 |
| draughtsman | draftsman | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| draughtsman's | draftsman's | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| draughtsmen | draftsmen | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| electrolyses | electrolyzes | OF04_uk_form_also_valid_us_elsewhere / unregistered | 70 |
| faggot | fagot | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| faggot's | fagot's | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| faggots | fagots | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| foregoes | forgoes | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| foregone | forgone | OF04_uk_form_also_valid_us_elsewhere / pron_differs | 35 |
| forewent | forwent | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| hooray | hurrah | OF04_uk_form_also_valid_us_elsewhere / pron_differs | 35 |
| hydrolyses | hydrolyzes | OF04_uk_form_also_valid_us_elsewhere / unregistered | 60 |
| jibed | gibed | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| jibing | gibing | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| mum | mom | OF04_uk_form_also_valid_us_elsewhere / pron_differs | 35 |
| paralyses | paralyzes | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| pouf | pouffe | OF04_uk_form_also_valid_us_elsewhere / unregistered | 55 |
| pouf's | pouffe's | OF04_uk_form_also_valid_us_elsewhere / unregistered | 55 |
| poufs | pouffes | OF04_uk_form_also_valid_us_elsewhere / unregistered | 55 |
| prefoliation | perfoliation | OF04_uk_form_also_valid_us_elsewhere / unregistered | 80 |
| prelection | perlection | OF04_uk_form_also_valid_us_elsewhere / unregistered | 80 |
| psychoanalyses | psychoanalyzes | OF04_uk_form_also_valid_us_elsewhere / unregistered | 40 |
| reanalyses | reanalyzes | OF04_uk_form_also_valid_us_elsewhere / unregistered | 60 |
| sheikhs | sheiks | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| sheiks | sheikhs | OF04_uk_form_also_valid_us_elsewhere / unregistered | 35 |
| spelt | spelled | OF04_uk_form_also_valid_us_elsewhere / unregistered | 10 |
| typhoemia | typhemia | OF04_uk_form_also_valid_us_elsewhere / unregistered | 95 |
| whiskies | whiskeys | OF04_uk_form_also_valid_us_elsewhere / unregistered | 20 |
| zoea | zea | OF04_uk_form_also_valid_us_elsewhere / unregistered | 80 |
| zoeas | zeas | OF04_uk_form_also_valid_us_elsewhere / unregistered | 80 |
| mum's | mom's | denylist:OF04_mother_sense_pron_differs | 35 |
| mums | moms | denylist:OF04_mother_sense_pron_differs | 35 |
| stoor | stor | denylist:dialect_short_pair | 70 |
| caulkings | caulks | denylist:different_inflection | 35 |
| noseys | nosies | denylist:different_inflection | 35 |
| formulae | formulas | denylist:different_number_form_pron_differs | 20 |
| coelomata | celomata | denylist:different_plural_form | 80 |
| coelomata | celoms | denylist:different_plural_form | 70 |
| oesophaguses | esophagi | denylist:different_plural_form | 35 |
| tempi | tempos | denylist:different_plural_form | 35 |
| virtuosos | virtuosi | denylist:different_plural_form | 35 |
| nanogrammes | micrograms | denylist:different_unit(nano!=micro) | 60 |
| nanogrammes | nanograms | denylist:different_unit(nano!=micro) | 80 |
| disc | disk | denylist:different_usage_not_regional_spelling(disc/disk) | 10 |
| discs | disks | denylist:different_usage_not_regional_spelling(disc/disk) | 10 |
| disk | disc | denylist:different_usage_not_regional_spelling(disc/disk) | 10 |
| disks | discs | denylist:different_usage_not_regional_spelling(disc/disk) | 10 |
| crees | ceres | denylist:different_word | 70 |
| kyloes | kyles | denylist:different_word | 70 |
| loury | lory | denylist:different_word | 70 |
| vires | viers | denylist:different_word | 70 |
| groyne | groin | denylist:different_word(groin_body_part) | 35 |
| groyne's | groin's | denylist:different_word(groin_body_part) | 35 |
| groyned | groined | denylist:different_word(groin_body_part) | 35 |
| groynes | groins | denylist:different_word(groin_body_part) | 35 |
| groyning | groining | denylist:different_word(groin_body_part) | 35 |
| lupin | lupine | denylist:different_word(lupin_plant/lupine_adj) | 35 |
| lupins | lupines | denylist:different_word(lupin_plant/lupine_adj) | 35 |
| matt | mat | denylist:different_word(matt!=mat) | 35 |
| matts | mats | denylist:different_word(matt!=mat) | 35 |
| matte | mat | denylist:different_word(matte!=mat) | 35 |
| mattes | mats | denylist:different_word(matte!=mat) | 35 |
| prise | prize | denylist:different_word(prise_vs_prize) | 20 |
| prise's | prize's | denylist:different_word(prise_vs_prize) | 20 |
| prised | prized | denylist:different_word(prise_vs_prize) | 20 |
| priser | prizer | denylist:different_word(prise_vs_prize) | 20 |
| prisers | prizers | denylist:different_word(prise_vs_prize) | 20 |
| prises | prizes | denylist:different_word(prise_vs_prize) | 20 |
| saki | sake | denylist:different_word(saki=monkey/sake) | 10 |
| saki's | sake's | denylist:different_word(saki=monkey/sake) | 10 |
| sakis | sakes | denylist:different_word(saki=monkey/sake) | 10 |
| cicatrice | cicatrix | denylist:different_word_form | 50 |
| forego | forgo | denylist:different_words(forego!=forgo) | 35 |
| foregoing | forgoing | denylist:different_words(forego!=forgo) | 35 |
| premiss | premise | denylist:different_words(premiss!=premise) | 20 |
| premisses | premises | denylist:different_words(premiss!=premise) | 20 |
| oversized | oversize | denylist:grammatical_form_not_spelling(d_dropped) | 40 |
| backwards | backward | denylist:grammatical_form_not_spelling(s_dropped) | 10 |
| maths | math | denylist:grammatical_form_not_spelling(s_dropped) | 35 |
| onwards | onward | denylist:grammatical_form_not_spelling(s_dropped) | 20 |
| sweepstake | sweepstakes | denylist:grammatical_form_not_spelling(s_dropped) | 35 |
| sweepstake's | sweepstakes's | denylist:grammatical_form_not_spelling(s_dropped) | 35 |
| hah | ha | denylist:interjection_short_pair | 20 |
| unbeknown | unbeknownst | denylist:lexical_variant_pron_differs(st_added) | 50 |
| amidst | amid | denylist:lexical_variant_pron_differs(st_dropped) | 35 |
| amongst | among | denylist:lexical_variant_pron_differs(st_dropped) | 10 |
| dike | dyke | denylist:offensive_or_ambiguous_term_hygiene | 35 |
| dikes | dykes | denylist:offensive_or_ambiguous_term_hygiene | 35 |
| dyke | dike | denylist:offensive_or_ambiguous_term_hygiene | 35 |
| dykes | dikes | denylist:offensive_or_ambiguous_term_hygiene | 35 |
| faggoted | fagoted | denylist:offensive_term_hygiene | 35 |
| faggoting | fagoting | denylist:offensive_term_hygiene | 35 |
| amoebae | amoebas | denylist:plural_form_not_spelling | 35 |
| arse | ass | denylist:profanity_or_other_word(ass) | 20 |
| arse's | ass's | denylist:profanity_or_other_word(ass) | 20 |
| arsehole | asshole | denylist:profanity_or_other_word(ass) | 40 |
| arsehole's | asshole's | denylist:profanity_or_other_word(ass) | 40 |
| arseholes | assholes | denylist:profanity_or_other_word(ass) | 40 |
| arsenicise | arsenicize | denylist:profanity_or_other_word(ass) | 95 |
| arsenicises | arsenicizes | denylist:profanity_or_other_word(ass) | 95 |
| arses | asses | denylist:profanity_or_other_word(ass) | 20 |
| rencontre | rencounter | denylist:pronunciation_differs_different_word | 70 |
| caesar | cesar | denylist:proper_name_collision(Caesar/Cesar) | 70 |
| aeq | eq | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| aeros | eros | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| aet | et | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| bael | bel | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| bour | bor | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| cre | cer | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| goey | gey | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| gre | ger | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| jour | jor | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| kaed | ked | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| oecus | ecus | denylist:short_or_rare_junk_pair(VarCon_edge) | 55 |
| poe | pe | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| ren | ern | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| renes | ernes | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| rens | erns | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| resh | ersh | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| ret | ert | denylist:short_or_rare_junk_pair(VarCon_edge) | 70 |
| diss | dis | denylist:slang_short_pair | 40 |
| wiz | whiz | denylist:slang_short_pair | 35 |
| wizzes | whizzes | denylist:slang_short_pair | 35 |
| coe | ce | tripwire_cmu_distance>0.5 | 95 |
| crea | cera | tripwire_cmu_distance>0.5 | 95 |
| synch's | sync's | tripwire_cmu_distance>0.5 | 40 |

## 2. AMB(一方向=canonical UK形 -> ASR US形のみ。112件、'sを除く)

| UK形 | US形 | 用法/理由 | pron_differs |
|---|---|---|---|
| absinth | absinthe | :1 | None |
| absinths | absinthes | :1 | None |
| analogue | analog | OF04_auto | False |
| barque | bark | <N> (-) ship | None |
| barques | barks | <N> (-) ship | None |
| blonde | blond | OF04_auto | False |
| blondes | blonds | OF04_auto | False |
| bussed | bused | OF04_auto | False |
| bussing | busing | OF04_auto | False |
| bussings | busings | <N> | None |
| castor | caster | OF04_auto | False |
| caulk | calk | OF04_auto | False |
| cheque | check | <N> bank | False |
| chequer | checker | pattern | None |
| chequered | checkered | pattern | None |
| chequering | checkering | pattern | None |
| chequers | checkers | pattern | None |
| cheques | checks | <N> bank | False |
| convertor | converter | :1 | None |
| convertors | converters | :1 | None |
| dependant | dependent | <N> | None |
| dependants | dependents | <N> | None |
| descendent | descendant | <Adj> | False |
| digitalise | digitalize | :1 | None |
| digitalised | digitalized | :1 | None |
| digitalising | digitalizing | :1 | None |
| draught | draft | OF04_auto | False |
| draughted | drafted | <V> writing | None |
| draughting | drafting | <V> writing | None |
| draughts | drafts | OF04_auto | False |
| electrolyse | electrolyze | :1 | None |
| electrolysed | electrolyzed | :1 | None |
| electrolysing | electrolyzing | :1 | None |
| eyrie | aerie | <N> | False |
| eyries | aeries | <N> | None |
| flyer | flier | <N> | False |
| flyers | fliers | <N> | False |
| foetider | fetider | (-) | None |
| foetidest | fetidest | (-) | None |
| gramme | gram | unit of mass | None |
| grammes | grams | unit of mass | None |
| gybe | jibe | sailing | None |
| gybed | jibed | sailing | None |
| gybes | jibes | sailing | None |
| gybing | jibing | sailing | None |
| hippy | hippie | <N> | None |
| hoorayed | hurrahed | :1 | None |
| hooraying | hurrahing | :1 | None |
| hoorays | hurrahs | :1 | None |
| hurray | hurrah | :1 | True |
| hurrayed | hurrahed | :1 | None |
| hurraying | hurrahing | :1 | None |
| hurrays | hurrahs | :1 | None |
| ikon | icon | :2 | False |
| ikons | icons | :2 | None |
| imbed | embed | <V> | False |
| imbedded | embedded | <V> | True |
| imbedding | embedding | <V> | None |
| imbeds | embeds | <V> | None |
| inthrall | enthrall | (-) enslave | None |
| inthralled | enthralled | (-) enslave | None |
| inthralling | enthralling | (-) enslave | None |
| inthralls | enthralls | (-) enslave | None |
| jibe | gibe | OF04_auto | False |
| jibes | gibes | OF04_auto | False |
| kerb | curb | street edge | False |
| kerbed | curbed | street edge | None |
| kerbing | curbing | street edge | None |
| kerbs | curbs | street edge | False |
| licence | license | <N> | False |
| licenced | licensed | <V> | None |
| licences | licenses | <N> | False |
| licencing | licensing | <V> | None |
| manilla | manila | :lower | False |
| matt | matte | <Adj> without lustre | False |
| metre | meter | <N> metric meter, rhythmic pattern | False |
| metres | meters | <N> metric meter, rhythmic pattern | False |
| micrometre | micrometer | metric meter | None |
| micrometres | micrometers | metric meter | None |
| nought | naught | <N> digit zero | None |
| noughts | naughts | <N> digit zero | None |
| phoney | phony | <N> | False |
| phoneys | phonies | <N> | None |
| practise | practice | <V> | False |
| practised | practiced | <V> | False |
| practises | practices | <V> | False |
| practising | practicing | <V> | None |
| prising | prizing | otherwise | None |
| programme | program | <N> | False |
| programmes | programs | <N> | None |
| racquet | racket | <N> game, related implement | False |
| racquets | rackets | <N> game, related implement | True |
| ravelled | raveled | <V> | None |
| ravelling | raveling | <V> | None |
| ravellings | ravelings | <N> | None |
| shaykh | sheikh | Arab chief | None |
| shaykhs | sheikhs | Arab chief | None |
| sheik | sheikh | OF04_auto | False |
| sheikh | sheik | OF04_auto | False |
| storey | story | level of building | False |
| storeys | stories | level of building | None |
| teazel | teasel | <N> | None |
| teazels | teasels | <N> | None |
| teazle | teasel | <N> | None |
| teazles | teasels | <N> | None |
| tranquillisings | tranquilizings | (-) -- normally an adj. | None |
| tranquillizings | tranquilizings | (-) -- normally an adj. | None |
| tyre | tire | wheel | True |
| tyres | tires | whell | False |
| unlearnt | unlearned | <V> | None |
| whisky | whiskey | drink | False |
| whizz | whiz | :1 | None |

## 3. 発音も違う対(pron_differs=True。OF-06: 監査記録・件数監視。33件)

| UK形 | US形 | dir | cmu_dist |
|---|---|---|---|
| aluminium | aluminum | both | 0.12 |
| anaesthesia | anesthesia | both | 0.12 |
| anaesthesiologist | anesthesiologist | both | 0.07 |
| anaesthesiologists | anesthesiologists | both | 0.06 |
| anaesthetist | anesthetist | both | 0.2 |
| catalogue | catalog | both | 0.14 |
| catalogued | cataloged | both | 0.12 |
| catalogues | catalogs | both | 0.12 |
| cataloguing | cataloging | both | 0.11 |
| colouring | coloring | both | 0.29 |
| dentine | dentin | both | 0.17 |
| dreamt | dreamed | both | 0.4 |
| empanel | impanel | both | 0.14 |
| enquire | inquire | both | 0.33 |
| enquiry | inquiry | both | 0.14 |
| gelatine | gelatin | both | 0.14 |
| hurray | hurrah | uk2us | 0.5 |
| imbedded | embedded | uk2us | 0.14 |
| learnt | learned | both | 0.25 |
| macintosh | mackintosh | both | 0.12 |
| marvelled | marveled | both | 0.29 |
| odours | odors | both | 0.25 |
| organisation | organization | both | 0.09 |
| organisations | organizations | both | 0.08 |
| ploughshare | plowshare | both | 0.17 |
| ploughshares | plowshares | both | 0.14 |
| racquets | rackets | uk2us | 0.17 |
| speciality | specialty | both | 0.3 |
| spilt | spilled | both | 0.2 |
| synch | sync | both | 0.5 |
| tyre | tire | uk2us | 0.33 |
| worshipped | worshiped | both | 0.17 |
| worshipping | worshiping | both | 0.14 |

## 4. 採用(active)のうち観点(a)に該当し、レビューの結果『採用』としたもの(167件。外したものは1.の理由付きdenylist)

| UK形 | US形 | 該当 |
|---|---|---|
| aeolipile | eolipile | first |
| aeolipiles | eolipiles | first |
| aeolotropic | eolotropic | first |
| aeon | eon | short,first |
| aeonian | eonian | first |
| aeonism | eonism | first |
| aeonisms | eonisms | first |
| aeons | eons | first |
| aerogenic | erogenic | first |
| aerose | erose | first |
| aerugo | erugo | first |
| aerugos | erugos | first |
| aesthesia | esthesia | first |
| aesthesias | esthesias | first |
| aesthetician | esthetician | first |
| aestheticians | estheticians | first |
| aestival | estival | first |
| aestivate | estivate | first |
| aestivated | estivated | first |
| aestivates | estivates | first |
| aestivating | estivating | first |
| aestivation | estivation | first |
| aestivations | estivations | first |
| aetiologically | etiologically | first |
| aetiologist | etiologist | first |
| aetiology | etiology | first |
| axe | ax | short |
| barque | bark | lev3 |
| barques | barks | lev3 |
| cheque | check | lev3 |
| chequebook | checkbook | lev3 |
| chequebooks | checkbooks | lev3 |
| cheques | checks | lev3 |
| decagramme | dekagram | lev3 |
| decagrammes | dekagrams | lev3 |
| decalitre | dekaliter | lev3 |
| decalitres | dekaliters | lev3 |
| decametre | dekameter | lev3 |
| decametres | dekameters | lev3 |
| desulphurise | desulfurize | lev3 |
| desulphurised | desulfurized | lev3 |
| desulphurises | desulfurizes | lev3 |
| desulphurising | desulfurizing | lev3 |
| downdraught | downdraft | lev3 |
| draught | draft | lev3 |
| draughted | drafted | lev3 |
| draughtier | draftier | lev3 |
| draughtiest | draftiest | lev3 |
| draughtilier | draftilier | lev3 |
| draughtiliest | draftiliest | lev3 |
| draughtily | draftily | lev3 |
| draughtiness | draftiness | lev3 |
| draughtinesses | draftinesses | lev3 |
| draughting | drafting | lev3 |
| draughts | drafts | lev3 |
| draughtsmanship | draftsmanship | lev3 |
| draughtsmanships | draftsmanships | lev3 |
| draughtswoman | draftswoman | lev3 |
| draughtswomen | draftswomen | lev3 |
| draughty | drafty | lev3 |
| empanel | impanel | first |
| empanelled | impaneled | first |
| empanelling | impaneling | first |
| empanelment | impanelment | first |
| empanels | impanels | first |
| enquire | inquire | first |
| enquired | inquired | first |
| enquires | inquires | first |
| enquiries | inquiries | first |
| enquiring | inquiring | first |
| enquiry | inquiry | first |
| eyrie | aerie | first |
| eyries | aeries | first |
| gaol | jail | first |
| gaoled | jailed | first |
| gaoler | jailer | first |
| gaolers | jailers | first |
| gaoling | jailing | first |
| gaols | jails | first |
| gybe | jibe | first |
| gybed | jibed | first |
| gybes | jibes | first |
| gybing | jibing | first |
| hoorayed | hurrahed | lev3 |
| hooraying | hurrahing | lev3 |
| hoorays | hurrahs | lev3 |
| imbed | embed | first |
| imbedded | embedded | first |
| imbedding | embedding | first |
| imbeds | embeds | first |
| indraught | indraft | lev3 |
| indraughts | indrafts | lev3 |
| inthrall | enthrall | first |
| inthralled | enthralled | first |
| inthralling | enthralling | first |
| inthralls | enthralls | first |
| jibe | gibe | first |
| jibes | gibes | first |
| kaftan | caftan | first |
| kaftans | caftans | first |
| kerb | curb | first |
| kerbed | curbed | first |
| kerbing | curbing | first |
| kerbs | curbs | first |
| manoeuvre | maneuver | lev3 |
| manoeuvres | maneuvers | lev3 |
| nett | net | short |
| oedema | edema | first |
| oedemas | edemas | first |
| oedematous | edematous | first |
| oenologist | enologist | first |
| oenologists | enologists | first |
| oesophagi | esophagi | first |
| oesophagitis | esophagitis | first |
| oesophagus | esophagus | first |
| oestradiol | estradiol | first |
| oestradiols | estradiols | first |
| oestrin | estrin | first |
| oestrins | estrins | first |
| oestriol | estriol | first |
| oestriols | estriols | first |
| oestrogen | estrogen | first |
| oestrogenic | estrogenic | first |
| oestrogens | estrogens | first |
| oestrone | estrone | first |
| oestrones | estrones | first |
| oestrous | estrous | first |
| oestrum | estrum | first |
| oestrums | estrums | first |
| oestrus | estrus | first |
| oestruses | estruses | first |
| outmanoeuvre | outmaneuver | lev3 |
| outmanoeuvres | outmaneuvers | lev3 |
| phantasied | fantasied | first |
| phantasies | fantasies | first |
| phantasy | fantasy | first |
| phantasying | fantasying | first |
| plough | plow | lev3 |
| ploughable | plowable | lev3 |
| ploughboy | plowboy | lev3 |
| ploughboys | plowboys | lev3 |
| ploughed | plowed | lev3 |
| plougher | plower | lev3 |
| ploughers | plowers | lev3 |
| ploughing | plowing | lev3 |
| ploughman | plowman | lev3 |
| ploughmen | plowmen | lev3 |
| ploughs | plows | lev3 |
| ploughshare | plowshare | lev3 |
| ploughshares | plowshares | lev3 |
| snowplough | snowplow | lev3 |
| snowploughs | snowplows | lev3 |
| spilt | spilled | lev3 |
| sulphurise | sulfurize | lev3 |
| sulphurised | sulfurized | lev3 |
| sulphurises | sulfurizes | lev3 |
| sulphurising | sulfurizing | lev3 |
| teazle | teasel | lev3 |
| teazles | teasels | lev3 |
| throughway | thruway | lev3 |
| throughways | thruways | lev3 |
| tsar | czar | first |
| tsars | czars | first |
| tzar | czar | first |
| tzars | czars | first |
| updraught | updraft | lev3 |
| updraughts | updrafts | lev3 |

## 5. 規則(OF-08: SCOWL固定)

- 規則適用: 変換前=SCOWL英国語専用語、変換後=SCOWL米国語/共通語 level<=70、stem>=4。新規対 0 件(=VarConに無い対は生成されない)、Tier-2->R昇格 5 件。
- Tier-2(level71-99)は active=False(初回Trialでは非同値)。件数: 8718

