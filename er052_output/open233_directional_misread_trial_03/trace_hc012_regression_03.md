# TRIAL-03 HC-012/A5-0 trace(read-only、事実のみ、原因断定なし)

## 1 Ledger events MUSE-HC-012 (subjX/state/phase) T03 | T02
- rep1 T03(2ev): 契約スタッフによる電話発信テスト/STARTED/INTERIM ; 電話発信機能/PAUSED/FINAL
  rep1 T02(2ev): 契約スタッフが適切な開示なしに電話をかけるテスト/STARTED/(なし) ; 機能/STOPPED/(なし)
- rep2 T03(2ev): 契約スタッフが電話をかけるテスト/STARTED/INTERIM ; 機能/PAUSED/FINAL
  rep2 T02(2ev): 契約スタッフが電話をかけるテスト/STARTED/(なし) ; 機能/PAUSED/(なし)
- rep3 T03(2ev): 契約スタッフによる電話テスト/STARTED/INTERIM ; 電話機能/PAUSED/FINAL
  rep3 T02(2ev): 契約スタッフが電話をかけるテスト/STARTED/(なし) ; 機能/PAUSED/(なし)
- quote(T03 rep1): テストを開始した

## 2 G-01/G-02
### G-01 exp=REVERSED evsubj=機能 phase=None | T02: r1 sel=機能 L=STOPPED A=AVAILABLE cmp=REVERSED / r2 sel=機能 L=PAUSED A=AVAILABLE cmp=REVERSED / r3 sel=機能 L=PAUSED A=AVAILABLE cmp=REVERSED
- X r1 sel=NONE aphase=FINAL mphase=None L=None A=NOT_MENTIONED cmp=NOT_MENTIONED fb=True/2 det=[契約スタッフによる電話発信テスト|INTERIM|L=STARTED|A=NOT_MENTIONED|NOT_MENTIONED,電話発信機能|FINAL|L=PAUSED|A=NOT_MENTIONED|NOT_MENTIONED] aq=The company also restored the human concierge feature to the
- X r2 sel=機能 aphase=INTERIM mphase=None L=PAUSED A=AVAILABLE cmp=REVERSED fb=False/0 det=[] aq=The company also restored the human concierge feature to the
- X r3 sel=NONE aphase=INTERIM mphase=None L=None A=NOT_MENTIONED cmp=NOT_MENTIONED fb=True/2 det=[契約スタッフによる電話テスト|INTERIM|L=STARTED|A=UNCHANGED|UNCLEAR,電話機能|FINAL|L=PAUSED|A=NOT_MENTIONED|NOT_MENTIONED] aq=The company also restored the human concierge feature to the
- Y r1 sel=NONE aphase=UNSPECIFIED mphase=None L=None A=NOT_MENTIONED cmp=NOT_MENTIONED fb=True/1 det=[電話発信機能|FINAL|L=PAUSED|A=NOT_MENTIONED|NOT_MENTIONED] aq=The company also restored the human concierge feature to the
- Y r2 sel=機能 aphase=INTERIM mphase=None L=None A=AVAILABLE cmp=UNCLEAR fb=False/0 det=[] aq=The company also restored the human concierge feature to the
- Y r3 sel=NONE aphase=INTERIM mphase=None L=None A=NOT_MENTIONED cmp=NOT_MENTIONED fb=True/1 det=[契約スタッフによる電話テスト|INTERIM|L=STARTED|A=NOT_MENTIONED|NOT_MENTIONED] aq=The company also restored the human concierge feature to the
### G-02 exp=REVERSED evsubj=機能 phase=None | T02: r1 sel=機能 L=STOPPED A=AVAILABLE cmp=REVERSED / r2 sel=機能 L=PAUSED A=AVAILABLE cmp=REVERSED / r3 sel=機能 L=PAUSED A=AVAILABLE cmp=REVERSED
- X r1 sel=電話発信機能 aphase=INTERIM mphase=None L=PAUSED A=STARTED cmp=UNCLEAR fb=False/0 det=[] aq=They also temporarily put back the feature in which humans h
- X r2 sel=機能 aphase=INTERIM mphase=None L=PAUSED A=AVAILABLE cmp=REVERSED fb=False/0 det=[] aq=They also temporarily put back the feature in which humans h
- X r3 sel=電話機能 aphase=INTERIM mphase=None L=PAUSED A=STARTED cmp=UNCLEAR fb=False/0 det=[] aq=They also temporarily put back the feature in which humans h
- Y r1 sel=電話発信機能 aphase=INTERIM mphase=None L=None A=AVAILABLE cmp=UNCLEAR fb=False/0 det=[] aq=They also temporarily put back the feature in which humans h
- Y r2 sel=機能 aphase=INTERIM mphase=None L=None A=AVAILABLE cmp=UNCLEAR fb=False/0 det=[] aq=They also temporarily put back the feature in which humans h
- Y r3 sel=電話機能 aphase=INTERIM mphase=None L=None A=AVAILABLE cmp=UNCLEAR fb=False/0 det=[] aq=They also temporarily put back the feature in which humans h

## 3 H-G4
### H-G4 exp=REVERSED evsubj=機能 phase=FINAL | T02: -
- X r1 sel=NONE aphase=UNSPECIFIED mphase=None L=None A=NOT_MENTIONED cmp=NOT_MENTIONED fb=True/2 det=[契約スタッフによる電話発信テスト|INTERIM|L=STARTED|A=NOT_MENTIONED|NOT_MENTIONED,電話発信機能|FINAL|L=PAUSED|A=NOT_MENTIONED|NOT_MENTIONED] aq=Meta kept the human concierge feature running.
- X r2 sel=機能 aphase=FINAL mphase=None L=PAUSED A=AVAILABLE cmp=REVERSED fb=False/0 det=[] aq=Meta kept the human concierge feature running.
- X r3 sel=NONE aphase=UNSPECIFIED mphase=None L=None A=NOT_MENTIONED cmp=NOT_MENTIONED fb=True/2 det=[契約スタッフによる電話テスト|INTERIM|L=STARTED|A=AVAILABLE|UNCLEAR,電話機能|FINAL|L=PAUSED|A=NOT_MENTIONED|NOT_MENTIONED] aq=Meta kept the human concierge feature running.
- Y r1 sel=NONE aphase=UNSPECIFIED mphase=None L=None A=NOT_MENTIONED cmp=NOT_MENTIONED fb=True/1 det=[電話発信機能|FINAL|L=PAUSED|A=NOT_MENTIONED|NOT_MENTIONED] aq=Meta kept the human concierge feature running.
- Y r2 sel=機能 aphase=FINAL mphase=FINAL L=PAUSED A=UNCHANGED cmp=UNCLEAR fb=False/0 det=[] aq=Meta kept the human concierge feature running.
- Y r3 sel=NONE aphase=UNSPECIFIED mphase=None L=None A=NOT_MENTIONED cmp=NOT_MENTIONED fb=True/1 det=[電話機能|FINAL|L=PAUSED|A=NOT_MENTIONED|NOT_MENTIONED] aq=Meta kept the human concierge feature running.

## 4 誤重大 X:H-F2, Y:H-F1
### H-F2 exp=SAME evsubj=上げ幅 phase=INTERIM | T02: -
article: Oil prices briefly dipped.
- X r1 sel=NONE aphase=UNSPECIFIED mphase=None L=None A=NOT_MENTIONED cmp=REVERSED fb=True/2 det=[Brent先物|INTERIM|L=DECREASED|A=DECREASED|SAME,Brent先物|FINAL|L=INCREASED|A=DECREASED|REVERSED] aq=Oil prices briefly dipped.
- X r2 sel=NONE aphase=INTERIM mphase=None L=None A=NOT_MENTIONED cmp=REVERSED fb=True/2 det=[Brent先物の上げ幅|INTERIM|L=DECREASED|A=DECREASED|SAME,Brent先物の価格|FINAL|L=INCREASED|A=DECREASED|REVERSED] aq=Oil prices briefly dipped.
- X r3 sel=Brent先物の水準 aphase=INTERIM mphase=None L=INCREASED A=DECREASED cmp=REVERSED fb=False/0 det=[] aq=Oil prices briefly dipped.

## 4b
### H-F1 exp=SAME evsubj=Brent先物価格 phase=FINAL | T02: -
article: Prices initially fell but recovered.
- Y r1 sel=Brent先物 aphase=INTERIM mphase=INTERIM L=DECREASED A=INCREASED cmp=REVERSED fb=False/0 det=[] aq=Prices initially fell but recovered.
- Y r2 sel=Brent先物の価格 aphase=INTERIM mphase=None L=None A=UNCHANGED cmp=UNCLEAR fb=False/0 det=[] aq=Prices initially fell but recovered.
- Y r3 sel=NONE aphase=UNSPECIFIED mphase=None L=None A=NOT_MENTIONED cmp=UNCLEAR fb=True/1 det=[Brent先物の水準|FINAL|L=INCREASED|A=UNCLEAR|UNCLEAR] aq=Prices initially fell but recovered.

## 5 D61 G-03 / H-G1-3 (Y)
### G-03 exp=REVERSED evsubj=水準 phase=None | T02: r1 sel=NONE L=None A=NOT_MENTIONED cmp=NOT_MENTIONED / r2 sel=NONE L=None A=NOT_MENTIONED cmp=NOT_MENTIONED / r3 sel=NONE L=None A=NOT_MENTIONED cmp=NOT_MENTIONED
- Y r1 sel=NONE aphase=UNSPECIFIED mphase=None L=None A=NOT_MENTIONED cmp=NOT_MENTIONED fb=True/1 det=[Brent先物|FINAL|L=INCREASED|A=NOT_MENTIONED|NOT_MENTIONED] aq=oil prices fell.
- Y r2 sel=NONE aphase=FINAL mphase=None L=None A=NOT_MENTIONED cmp=REVERSED fb=True/1 det=[Brent先物の価格|FINAL|L=INCREASED|A=DECREASED|REVERSED] aq=After the plan was withdrawn, oil prices fell.
- Y r3 sel=NONE aphase=FINAL mphase=None L=None A=NOT_MENTIONED cmp=REVERSED fb=True/1 det=[Brent先物の水準|FINAL|L=INCREASED|A=DECREASED|REVERSED] aq=After the plan was withdrawn, oil prices fell.
### H-G1 exp=REVERSED evsubj=Brent先物価格 phase=FINAL | T02: -
- Y r1 sel=NONE aphase=FINAL mphase=None L=None A=NOT_MENTIONED cmp=REVERSED fb=True/1 det=[Brent先物|FINAL|L=INCREASED|A=DECREASED|REVERSED] aq=Oil prices dropped after the withdrawal.
- Y r2 sel=NONE aphase=FINAL mphase=None L=None A=NOT_MENTIONED cmp=REVERSED fb=True/1 det=[Brent先物の価格|FINAL|L=INCREASED|A=DECREASED|REVERSED] aq=Oil prices dropped after the withdrawal.
- Y r3 sel=Brent先物の水準 aphase=FINAL mphase=FINAL L=INCREASED A=DECREASED cmp=REVERSED fb=False/0 det=[] aq=Oil prices dropped after the withdrawal.
### H-G2 exp=REVERSED evsubj=Brent先物価格 phase=FINAL | T02: -
- Y r1 sel=Brent先物 aphase=FINAL mphase=FINAL L=INCREASED A=DECREASED cmp=REVERSED fb=False/0 det=[] aq=Brent fell
- Y r2 sel=Brent先物の価格 aphase=FINAL mphase=FINAL L=INCREASED A=DECREASED cmp=REVERSED fb=False/0 det=[] aq=Brent fell
- Y r3 sel=Brent先物の水準 aphase=FINAL mphase=FINAL L=INCREASED A=DECREASED cmp=REVERSED fb=False/0 det=[] aq=Brent fell
### H-G3 exp=REVERSED evsubj=Brent先物価格 phase=FINAL | T02: -
- Y r1 sel=NONE aphase=FINAL mphase=None L=None A=NOT_MENTIONED cmp=REVERSED fb=True/1 det=[Brent先物|FINAL|L=INCREASED|A=DECREASED|REVERSED] aq=Prices ended lower.
- Y r2 sel=Brent先物の価格 aphase=FINAL mphase=FINAL L=INCREASED A=DECREASED cmp=REVERSED fb=False/0 det=[] aq=Prices ended lower.
- Y r3 sel=NONE aphase=FINAL mphase=None L=None A=NOT_MENTIONED cmp=REVERSED fb=True/1 det=[Brent先物の水準|FINAL|L=INCREASED|A=DECREASED|REVERSED] aq=Prices ended lower.

## 6 事実のみの所見
- HC-012のLedger「機能」系eventは全rep FINAL(rep1のみPAUSED、T02 rep1はSTOPPED)、テストeventはINTERIM/STARTED。T03のsubject_xはrep毎に「電話発信機能/機能/電話機能」と揺れ、T02は「機能」で3rep一致。
- G-01/G-02は記事phaseがINTERIM(または不定)で、mphaseは全rep None。selected_subject=NONEのrepはfallbackでINTERIM+FINAL両eventを個別比較しNOT_MENTIONED/UNCLEARになった。sel=「機能」の時のみREVERSED(X G-01 r2、X G-02 r2)。Y G-02は全rep L=None。
- H-F2(X)はFINAL event(L=INCREASED)に対し記事「briefly dipped」(A=DECREASED)でREVERSED、INTERIM eventでは同記事がSAME。H-F1(Y r1)はmphase=INTERIMだがaphase=INTERIM・A=INCREASEDでREVERSED、r2/r3はUNCLEAR。
