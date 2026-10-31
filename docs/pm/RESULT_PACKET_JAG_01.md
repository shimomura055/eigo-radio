# RESULT_PACKET JAG_01 (JA-GLOSS-NUANCE-01 委任_01、2026-10-31、OPEN-630)

要約: 『結論』になった根本原因=gloss新規生成Prompt(er003_key_words_gloss_alignment.py:152-156)の規則構造(1語でも見出し訳を使わせない/比喩の像を剥がす/近義語の区別を確かめない)。入力文脈・後処理・モデル能力は反証。最適訳語=評決(判決は許容)。推奨=案B3(規則1行差替え+確認1行、追加call 0)。Trial: verdict 裁判語3/3(現行0/3)、副作用139 itemで悪化はnoise範囲、出力+約11%(1記事セット+約¥0.1〜0.3)。**Status案=VALIDATED(条件付き)**、採用=ユーザー判断。Production変更0・記事/音声再生成0。
1. 根本原因: CURRENT_STATE_01.md §3(R1定訳回避[OF-KP1-05 anchoring対策の副作用]/R2比喩の像剥がし/R3近義語区別なし)。実出力: naive_ja=評決, conveys=partly, gloss=結論(gloss_alignment_runtime_metadata.json item_log.9)。
2. 現在の文脈の最適訳語: 評決(裁判の比喩・解説との一致・sentenceとの区別)。判決は許容。結論/最終判断は不可寄り(§4)。
3. 同種の問題: あり。1語key_phraseで一般語化(culprit→原因, charge→非難等)・定義文化(radius→中心から外側までの長さ等)。母集団449件の1語157件の約9%、公開Adv 1語18件で明確1・中程度4(§5)。
4. 1訳語/2訳語: 1訳語で足りる。2訳語が必要な実例は0件(gloss449件・公開84件に複数訳語なし)。
5. 推奨方式: B3(DESIGN_01.md §4)。個別辞書ルールではない。
6. 影響: Q=verdict裁判語3/3・同型1語が改善、悪化はA同士のnoise以内(B3 22良/11悪/106同等、p≈0.08)。D=追加call無・出力+約11%。C=+¥0.05〜0.07/call、1記事セット+約¥0.1〜0.3(70円の0.2〜0.4%)。
7. Trial: TRIAL_01.md。事前登録の厳格C2(worse≤2)・C3(token比≤1.10)は未達(worse 4/4, 1.11)、noise込み再登録H1〜H3(held-out 4記事)で達成=条件付きVALIDATED。限界=単独ラベラー・対象非盲検・Z/Y未検証。費用¥25.35/Cap¥30(43 call)。使用モデル=gpt-6-luna(25-1例外2:ライン組込候補の性能確認。最新世代の効率系)、評価者=本agent。
判断候補: J1【分類D】X2p'のgloss規則を案B3へ改める採否(承認済みUDR #179文面の変更=CURRENT_SPEC.md:2892, 原文:56)。J2【分類B・Fable判断】採用前にZ/Yの副作用Trial・独立評価者での再採点を行うか。J3【分類C・別件】公開Adv Comment 4のJA訳誤り(OPEN-631 AUDIT_01.md:143-144 J4)を本OPENに含めるか(修正へ進む)。
(1) 既存仕様整合: CURRENT_SPEC.md:2892,2001,2002,1998,2000,2230 / DESIGN_07.md:116 / OPUS_REVIEW_07.md:54 / er003_key_words_gloss_alignment.py:152-156,780,784-845 / er006_model_routing_contract_01.py:50 / 原文:28-60。B3は2語以上のanti-anchoringを維持し、1語のみ緩和(OF-KP1-05の適用範囲の変更=Opus条件A相当の可能性)。
(2) Production到達経路の未承認機能: なし。Production コード/Prompt/Gate/設定の変更0(git diffはdocs/research/JA-GLOSS-NUANCE-01・OPEN_ITEMS.md・docs/pm/ACTIVE_TASK.md・本ファイルのみ)。再生ツールはdocs/research配下で、Productionから参照なし。11-7限定例外は不適用(既存Prompt直接編集のため)。flag作成なし。
(3) 失敗終了時の最終成果物: 失敗終了なし(全43 call完走、STOP/外部停止なし)。成果物=docs/research/JA-GLOSS-NUANCE-01/{CURRENT_STATE_01,DESIGN_01,TRIAL_01}.md・tools/・data/・trial_01/。原文要求(原因特定・最適訳語・類似事例・1/2訳語・推奨方式・影響・Trial)に適合。
(4) 撤去・残置: 撤去0。旧規則『yesなら、naive_jaをそのまま写さず』は er003_key_words_gloss_alignment.py:156 に残置(Production無変更)、golden fixture docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/WIRING_35/golden_dev_x06_messages_01.json にも残置(採用時に更新)。Grep結果: 『naive_jaをそのまま写さず』の.py参照は上記1箇所のみ。
判定整合: 重大NG=なし
詳細: docs/research/JA-GLOSS-NUANCE-01/。次手候補(改善見込み): 採用なら単一commit実装+Z/Y追加Trial(高)。環境注意: C:ドライブ空き<1GBでsparse worktree使用。
