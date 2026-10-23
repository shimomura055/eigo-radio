# OPUS_REVIEW_05 (Opus独立技術レビュー・条件A、DESIGN_05/ROOT_CAUSE_03対象、2026-10-23。逐語。出所=委任_14 §2)

Opus独立技術レビュー(条件A) DESIGN_05/ROOT_CAUSE_03 2026-10-23
総合: 必須修正後にTrial可。②方向性妥当だがroleが項目単位で複数人称語KP(put oneself in someone's shoes)を壊す/修復がfulltext部分窓・lemma併用に未対応。①方式C妥当だが検査の英語逆訳が「英語の字義=英語の慣用」型(draw a line/an unseen clock)で元に戻りsame_meaningと判定→目標事例を見逃す欠陥。原因分析は必要条件としては正しいが生成側誘因2つを見落とし(OF-06/07)。
[必須]OF-D5-01 ② roleを項目単位から人称トークン単位へ: 再帰代名詞(yourself等→oneself)はroleを問わず決定論でself。所有格は `possessor_roles:[{token,role}]` 出現順配列(要素数=display中の所有格数を決定論照合)。根拠 gloss_alignment:208。
[必須]OF-D5-02 ② 修復の適用範囲と整合: (i)置換しないことはどのroleでも常に許可と明記(mind your own business型・迷えば置換しないを一般化へ強制しない)。(ii)「noneなのに置換」はINVALIDでなくdisplayの語へrevert。(iii)fulltextのkeyはdisplayの部分窓・lemma併用あり(er105:694-709)、`person_generalization_pairs`は等長前提(gloss_alignment:240-241)→窓対応をer105から再利用。(iv)修復後に `changed_from_display_phrase`・`normalization_reason`・QA実効値(`qa_person_reference_generalized`は修復前keyの自己申告。FAIL残りはCANONICALIZATION_REVIEW_REQUIRED[:672-678]増)を決定論で再計算、前例 `_qa_field_effective_verdict`(:508-518)。
[必須]OF-D5-03 ① 検査callの逆訳設計: `gloss_alone_reading_en`を英語短句にすると「線を引く」→"draw a line"に戻り見逃す。修正: 出力順 (1)`usage_meaning_en`(KP+文から本文での意味)→(2)`gloss_alone_reading_en`(日本語意味だけから)→(3)`gloss_conveys`。(1)(2)は「KPの内容語を使わない平易な言い換え」とし内容語との重なりを決定論検査、重なれば「検査不成立」記録。flag条件 `usage_in_sentence=="figurative"` は再現率を下げる恐れ→「conveys単独」と「figurative AND conveys」を同一出力から事後計算で比較(追加費用0)。
[必須]OF-D5-04 ① C/C'採否規則を対称に: C'採用条件=(a)recall点推定がC以上 かつ(b)未flag項目の悪化がB0の2rep間ノイズ内。欠ければC。差額約0.05円/記事、同等ならC優先(Claude案と対立)。
[必須]OF-D5-05 ① 事象が少ない場合の事前宣言: B0のNGが閾値(例6件)未満なら比率でVALIDATEDとせず「既知NG+検出recall/precision+flag項目のBefore/After」で判定。推奨Phase 0: Trial_02/03の既存出力(gold/Fableラベル付き約360セル、字義NG5件、take the wheel/carry the load含む)を検査器にかけて較正(約2〜3円)。
[推奨]OF-D5-06 ①原因に生成Prompt側の誘因: 新規生成は再整合用Prompt流用(gloss_alignment:549-608): 字義訳を良しとする例 fall into→「～に落ちる」(:602)、「全語と過不足なく一致」(:585)、QA名 `qa_reflects_all_key_phrase_words`(:95,637)、`added_word_mappings`。G1はn=14・1rep・Sonnet判定で否定根拠にならず、方式Cの再生成も同Promptを通り字義再発経路。修正: 「G3参考」armを「新規生成項目だけ再整合用の指示・例を除いたmessage」armに置換(追加call 0)。
[推奨]OF-D5-07 ②原因に例示の偏り: 規則3の例が their→someone's/your→someone's のみ(:11)、規則4の例 pumps its fist→pump one's fist(:12)+its→{one's}許可表が apply its findings→one's を誘発。修正: self/other/non_personの一般例を均等に(特定記事の語句は使わない)。
[推奨]OF-D5-08 ② roleとkey食い違い時: 「roleに合わせる修復」と「displayへ戻す」をC1A同一出力に事後適用して比較(API 0)、「正しかったのはroleかkeyか」指標を追加。閉じた語彙内でLLM自身の構造化判定に基づく1トークン置換は自由文補正に当たらず思想矛盾なし。
[推奨]OF-D5-09 ② roleの2軸定義: 軸1=動作主と同一指示か、軸2=人か物か。動作主と同一で人/擬人化→one's、動作主でない人→someone's、動作主でない物・組織→現状維持(their enforce their rules含む)。物が動作主の定型句(find its way/run its course/take its toll)は現状維持(its)許容と明記。テンプレ:39 `qa_person_reference_generalized` 定義も「roleに従った現状維持はPASS」へ。
[推奨]OF-D5-10 ① 再生成後の再検査: flag項目のみ再検査する変種を測る(約0.05円/回)。attempt 2採用済み項目は `FLAGGED_UNREPAIRED_NO_ATTEMPT` で区別記録。
[推奨]OF-D5-11 C-Solの費用基準不整合: 実行するなら別の費用基準を事前明記。
[推奨]OF-D5-12 非劣化の分母: 「新規悪化≤全出力1%」は薄まる→flag項目内の悪化数・率を主指標、goldのPASS→FAIL 0件を要件。
[推奨]OF-D5-13 test影響: my/ourにsomeone's追加で `er064_kp_idiom_trial_01_test_01.py`(Rule7 INVALID固定)・`er003_test_key_words_canonicalization.py` の期待値が変わりうる→Grep対象明記。
[情報]OF-D5-14 決定論字義検出不可(「一線を引く」が「線」を含む)。gloss callへusage_type追加=C'と同じ。 OF-D5-15 Std/Adv整合不採用に同意。 OF-D5-16 fail-open妥当、ただし `SKIPPED_TECH_FAIL`/`FLAGGED_UNREPAIRED` 件数をrun summaryと記事報告に必ず出す。 OF-D5-17 b1bでgloss変化→Adv 5件まとめて再生成(約0.07円/回)、flagは確率的でKP stage再実行時にStore reuseが崩れうる(TTS再生成)。 OF-D5-18 「1/3以下」は「解消」ではない。残存NG率とCI・既知事例の結果を明示、「解消」はanchor・F層残存ほぼ0の場合のみ。判定基準値はTrial内事前宣言としてFable確定可、採用時の品質水準は§7(4)に残す。 OF-D5-19 §7概ね適切(B仕様不変、signature再生成連鎖で吸収、11-7不適用)。§7に「規則3の例示変更(OF-07)」「新規生成message変更armを採る場合のgloss Prompt変更」を追加。
一致: ②(a)追加call 0/①方式C/不採用群/fail-open/attempt上限2/Production不変。対立: トークン単位role(01)/none+置換はrevert(02)/英語逆訳(03)/同等ならC(04)/生成Prompt誘因とG3参考armの差替え(06)/例示偏り(07)。
