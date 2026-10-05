# OPEN-233 Stage 1 ループ2設計 準備(論点整理のみ、設計ではない。委任_09、¥0)

根拠: er052_output/open233_kpi_recovery_02_offline_01/stageA_candidate_composition_01.{json,md}。Trial専用、Production未配線、APPROVED_FOR_PRODUCTIONではない。

## 事実(確認)
- NORMAL 12 runの候補は24.0/記事(判定単位31.2の77%)。内訳: LLM両経路8.2、LLM r3のみ10.9、LLM r5のみ0.7、決定論のみ4.3。LLM候補513件はissue・claim_in_article 100%、related_fact_id 96%付きだが、フラグが汎用(changed_fact/unsupported_new_claim/changed_scopeのみ)の候補が40%、unsupported_new_claim付きが89%。
- NORMAL先頭5候補x6=30件の目視相当ラベル(推測): 真の逸脱(軽微含む)4件13%、自然な推論・言い換え6件20%、迷って候補にしただけ(導入・修辞・見出し・評価語)20件67%。
- negation_polarity_mismatch 149件は、確定した真の極性不一致0件。誤発火98.7%(字面「ほどなく」60、「AIではなく」対比40、「意図せず」21、「なし」の否定語リスト欠落15、英語Ledger非対応4ほか)。
- Stage 2負荷(rep30実測fit、候補24へ外挿): 費用線形¥1.85/記事(候補10上限でも¥0.83)。rep30のBLOCKING率は全体0.29(35/121)、NORMAL 0.10(2/20)→期待BLOCKING 2.4〜6.9/記事、0件になる確率は4〜9%。
- 平均追加費用: Stage 1 fresh ¥1.51/run +Stage 2 +追加Rewrite。同一instance照合のrep30比で下限+1.5、線形+3.0、cap10 +2.5(rep24比は+0.44加算)。基準+2円/記事を超える見込み。
- 結論: 段階B(E2E)でKPI 3つを満たす見込み=No(Cost KPI。Human Review 0は不明、見逃し0は見込みYes)。

## ループ2の論点(構造。Prompt文言の小修正ではない)
(A) Stage 1出力の2層化: CANDIDATEに「どのfactのどの要素(数値・主体・時期・範囲・因果・確信度・否定・比較)とどう食い違うか」の具体的discrepancyを必須化し、具体化できないもの(導入・修辞・見出し・評価語。サンプル67%)はUNSUREとして、Stage 2本体ではなく安価な決定論/小batch triageへ回す。Safety維持の根拠: UNSUREも捨てず別経路で判定する(捨てるのではなく経路分離)。ただしSC 6件の検出がdiscrepancy具体化可能な側に残るかの再測定が必須(SC候補は現状「changed_*」フラグ付きが多いが、汎用フラグのみのSC候補の割合は未集計)。
(B) 決定論検査の精度是正: negation_polarity_mismatchは誤発火98.7%で、候補を約4.3/記事(NORMAL)押し上げているだけ。構造的原因は日本語Ledger1行目の部分文字列照合(「ほどなく」「ではなく」「意図せず」「なし」欠落)と英語Ledger非対応。是正案は否定の「対象・種類」を限定する(文末否定のみ等)、または否定検査をLLM判定のchanged_negationへ一本化し、決定論検査は引用実在・数値のみに戻す。Safety維持の根拠: changed_negation SC(er009 hold-out)はLLM経路で検出済み、決定論検査は「OK判定を覆す」補助でしかない。是正後に旧149件のうち真の不一致が落ちていないことを再集計する(¥0で可能)。
(C) Stage 2のbatch化: 候補を件数ごとの個別判定から、同一fact・同一段落でまとめる/上位N件のみ詳細判定する構造にして、費用を候補数に比例させない。ただし候補上限を設けるとSafety低下の恐れ(Fableの「上限なし」原則)があるので、「上限」ではなく「同一fact束ね」でのみ圧縮する。Stage 2のBLOCKING率(NORMAL 0.10)が束ね後も維持されるかの測定が必須。
(D) r3とr5の差: r3 23.5、r5 13.8だが、r5のみの候補は0.67/記事でr3が実質上位集合。SC 6件は r3単独で18/18(r5単独は17/18)。r3の追加分は「factに対応しない文」(r5ではUNMENTIONED 23.5%)の候補が中心と推測(未検証)。r5はfact駆動のため、少なくとも2経路∪の「r3全文」側が過剰の主因。ただしr5もNORMALで13.8候補/記事あり、r5だけにすれば解決する訳ではない。Safety維持の根拠: r3単独のSC検出18/18は小標本(n=18)で、経路別の検出率差はまだ有意に言えない。
Opus#17: 本ループ2は構造変更(出力の2層化・経路再編)なので、PM_GOVERNANCE 11-3の条件A(新しい構造・処理フロー設計)に該当し必須。設計案はFable確認後、実装前にOpus独立レビューへ。
