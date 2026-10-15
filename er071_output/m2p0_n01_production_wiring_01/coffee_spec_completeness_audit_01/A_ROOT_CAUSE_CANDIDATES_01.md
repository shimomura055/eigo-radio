# A_ROOT_CAUSE_CANDIDATES_01 (CFSA 委任_01A、2026-10-15、Read-only・JPY0)

位置づけ: ユーザー§5の6分類ごとに、仕様側調査で見えた**候補**(証拠付き)と、01B(成果物側)/委任_02で確認が必要な点を整理する。断定ではない。既存機構の範囲での是正方向のみ記す(新Validator・新管理制度は提案しない)。出典は`A_COMPLETION_CRITERIA_RECONSTRUCTION_01.md`(以下「再構成」)と`A_IN_ONE_LINE_TIMELINE_01.md`(以下「時系列」)。

## 1. Trial成果が正式な採否判断へつながっていなかった
候補(該当度: 中)
- 2文IOLは**Trialですらなく**、v3制作中の個別決定。VALIDATEDも`APPROVED_FOR_PRODUCTION`もない(OPEN-299「OPEN候補・未仕様化・未承認」、`OPEN_ITEMS.md:802`)。仕様化(Writer/Checker/難易度/Comment4接続)の判断依頼が、UDR #1(`USER_DECISION_REGISTER_01.md:18`)では「Comment4 Trial-03採否」の文脈に寄り、IOL文数の独立した判断項目として提示された記録がない。
- K2/M2/A5/B5は「Coffee限定`APPROVED_FOR_PRODUCTION`(Style選択のみ)」(2026-10-12)だが、Production側の実装単位(profile)に落ちたのはFull Story(P8→N01)・R2・P3・E1だけ。K2/M2/A5/B5は「後続Phase」の申し送り(`er019_family_x_style_profile_01.py:16`)のまま、採用後に実装へつなぐ起票が見当たらない(OPEN-300/313の後続Phaseの扱いは01Bで確認)。
- OPEN-332(ポーズ)・H-speed/8way候補は採否未決のまま(UDR #27-29)。これは意図どおり完成版に入れないべき項目で、問題ではない。
01Bで確認: K2/M2/A5/B5の後続Phaseを起票するOPENが存在するか。

## 2. 採用済み仕様がProduction経路に反映されていなかった(approved-but-unwired)
候補(該当度: 高)
- profile定義(`STYLE_PROFILES`/`ROLE_SEGMENTS`/`ROLE_LEVELS`)に、**K2(KP英語)・M2(KP日本語意味)・A5/B5(固定Intro)・IN_ONE_LINE用overrideが存在しない**。profile内に`FULL_STORY`/`SUPPORT_JA`/`KP_EXPLANATION_EN`/`PREVIEW`のみ(`er019_family_x_style_profile_01.py:116-160`)。runnerが共通定数のままKP英語・日本語意味を生成するなら、Production runnerで新規生成したKPは承認Styleにならない(暫定観測: Std KP日本語意味=J3 `ae68e3e6ac8e`、Std KP英語=style空、Adv KP英語=`2b0c7505f48e` warm podcast announcer。`再構成`§2暫定観測)。
- OPEN-350(Adv Preview E1未配線)は2026-10-13に発見され、委任_03で配線された(profile `coffee_n01_r2_p3_e1`)。E1だけが「承認済みなのに未配線」としてSTOP判定に載り、K2/M2は同じ構造なのに(profile外)判定表に載っていなかった。`ADV_STYLE_FACTCHECK_02.md`は承認Styleのsource一覧にKP英語/日本語意味の行を持たない(role表: topic_intro/preview/comment_1-4/in_one_line、Std: topic_intro/japanese_title/preview/comment_1-4/in_one_line)。
01Bで確認: 最終音声のKP各segmentのstyle sha実測(暫定観測の再確認)、A5/B5固定音声のseed由来と承認Styleの一致。

## 3. Production側には存在するが、Coffee完成版では旧artifactやseedを再利用した
候補(該当度: 高、In One Lineの直接原因)
- Adv in_one_line: v3の2文版wav(sha `645cac39…`)が`_replaced_02/`へ退避され、e_tone_01の旧1文版検証済みtakeに置換(`DECISION_LOG.md:21007`、実ファイルmtime 2026-10-13 21:56)。Std in_one_lineも「e_tone_01 seed」で旧1文版(`時系列`#10)。
- seed再利用の判定基準は(1)style sha(2)textが`parts.json`と一致(`er019_family_x_validation_inheritance_01.py:17,76-78`)。2文版原稿が`parts.json`へ入っていなかったため、(2)が旧1文版を正とする方向に働いた。
- 固定Master phrase(welcome/preview_intro/key_phrases_intro/num_one〜five等)もsha provenance付きseedで、Audio Validation Gateの走査対象外(`CHECKLIST_05.md:9`、既知の限界)。承認Style(A5/B5)との一対一照合は同チェックリストにない。
- Std Preview/Comment1-4は`v5_ms_01` entry sha経路の再利用(R2、Style一致)、topic_intro/IOLはe_tone_01 seed(`DECISION_LOG.md:21007`)。
01Bで確認: seedごとの由来(v3 Trial raw / e_tone_01 / v5_ms_01)と、承認Style・承認原稿との一致を全role分。

## 4. 完成条件に必要仕様の網羅性確認がなかった
候補(該当度: 最高)
- `CHECKLIST_05.md`は12項目の配線チェックで、承認済み仕様の全件照合表がない。「In One Line」の語は0件。#11(b)は「Std KP=既存」(`再構成`§3)。
- 「必須反映5点」(`REASSEMBLY-PLAN-01.md:8-16`、OPEN-321)はfinal_03の制作工程のどの成果物からも参照されていない(`er071_output/m2p0_n01_production_wiring_01`と`docs/pm/delegation_log/2026-10-1[34]_FAMILY-XZ*.md`のrgで`OPEN-299|OPEN-316|OPEN-321|REASSEMBLY-PLAN`が0件)。
- COMPLETION-01_01の指示は「CURRENT_SPECと過去のユーザー決定を照合し、承認済み範囲で進めること」(`:7節`)で照合対象の一覧が委任文に無く、「単に作業が必要だからUSER_DECISION_REQUIREDとしない」(`:189-`)という開発側自律の強化が、停止して照合する動機を弱めた可能性がある(推測。断定しない)。
- PM_GOVERNANCEにも既存ギャップ: Gate 7補足(a)〜(m)は「見える要素の確認」、Closeout項目3/7は「SSOT記載の整合」で、「ユーザー要求・承認項目が完成物に出ているか」の照合を直接要求する条項はない(`docs/pm/PM_GOVERNANCE.md:243-262`、`:476-`)。
是正方向(既存機構内): Gate 7/Closeout Check項目3「正式採用項目が追跡済みであること」の解釈として、完成宣言時に「承認済み仕様×完成物」の一覧照合を1表にまとめる(既存`ER-*_REPORT.md`/CHECKLISTへ追加する運用。新Validatorではない)。

## 5. Fableが実際の完成物を照合せず受入れた
候補(該当度: 中、証拠不足)
- CHECKLIST_05(受入物)に網羅項目がなく、Fable受入判定が「配線の完了度」に限られていた可能性。Fable個別メモはRepoにないため**未確認**。
- `F1_RUNTIME_EVIDENCE_02.md:17,19`にIOLのasr_text冒頭(旧1文版)が表示されていたが、2文版との差異が報告で言及された記録なし。
- 2026-10-15にユーザー自身が試聴で発見(`時系列`#13)=Sonnet/Fableの自己検出なし。
01B/委任_02で確認: Fable受入時にSonnetの完了報告の「再利用segment」節で、IOL text/文数が提示されていたか。

## 6. CURRENT_SPEC/Decision Log/Open Itemsの情報が制作時に参照されなかった
候補(該当度: 高)
- 参照されなかった: OPEN-299/316/321、REASSEMBLY-PLAN(上記rg 0件)。参照された: OPEN-326(Coffee原稿正本、V5 PRECHECK)、OPEN-350/313(Style)、CURRENT_SPEC:2620-2625(Style)。**Style系SSOTは参照され、文面(原稿)系SSOT[IOL]は参照されなかった**という偏りがある。
- SSOT内の不整合も参照を難しくした: (a)`CURRENT_SPEC.md:2620`はStd Preview/CommentをP2と記し、2624(後段)でR2に更新(同一節内で二重記述) (b)UDR #1(Comment4)がV5で(A)採用済みだが、UDRに「判断済み」更新されていない可能性(`USER_DECISION_REGISTER_01.md:18`はUDR表記)(c)OPEN-299は`OPEN_ITEMS.md:802`で複数追記済みだが、「final_03はIOLが1文」という事実の追記はまだない。
01Bで確認: final_03時点のSSOT(CURRENT_SPEC/OPEN)の参照可能性(committed状態で上記が読めたか)。

## 7. その他の構造候補(上記6分類の外)
- 時系列の根本: 2文版原稿が**Trial隔離の付属ファイルにしか存在しない**構造。Production runnerは`parts.json`を正とするため、Trialで承認されたtext変更が記事ソースへ戻る経路がない。「Coffee限定採用」を記事ソース/profileへ落とす手順が、Style(profile)にはあるが文面(IOL)には無い。
- 「ユーザー判断と開発側責任の区分」(`COMPLETION-01_01.md:189-`)は有効な是正だったが、**仕様側の網羅確認は「開発側自律」の対象として明文化されていない**。

## Day 2運営モデル刷新との関係(検討事項、進行中の実装へ介入しない)
今回の反映漏れは、Day 2運営モデルで検討されているF3独立受入・W6承認済み指示欄・Gate 7集約が狙う領域と直接重なる。具体的には(1)ユーザー承認済み指示(必須反映5点・IOL 2文・K2/M2等)を1か所の「承認済み指示欄」に束ね、完成宣言時にその全件を「反映済み/未反映/部分」で受入側が機械的に確認できる形にすること、(2)受入判定が実装者の配線チェックリスト(CHECKLIST_05型)とは別の独立した照合を持つこと、(3)Trial隔離の付属成果物(IOL原稿等)が記事ソース/仕様へ戻る経路を、Coffee限定採用の登録時点で決めること、が検討事項になる。ただしこれらは運営モデル側の設計課題であり、本委任は提案のみで、進行中の実装・規則・SSOTには触れていない。

## 01B/委任_02で確認が必要な点(一覧)
1. 最終音声のKP各segment(Std/Adv)のstyle shaと承認Style(K2/M2)の実測一致(暫定観測は不一致示唆)。
2. A5/B5固定音声(welcome/preview_intro)のseed由来と承認Styleの一致。
3. IOL: Std置換前の実態、final_03 MP3内の実際の読み上げ(1文)と試聴ページ表示の一致。
4. Adv Comment 1-4(`calm, conversational`)とOPEN-350の整理結果、e_tone「warm, upbeat」との関係。
5. Std KP #4(`based on interviews`)のgloss: legacy書換え結果と、corrected版で結果が変わるか(再生成要否)。
6. Fact Lock/Risk Flagger(`rf_tts_guard.json`)がv5原稿に適用された実績。
7. Outro/終端の仕様記述と実音声(仕様側で記述を特定できなかった)。
8. 最小再生成範囲の候補(監査後・ユーザー判断後): IOL(Std/Adv 2 segment、原稿をparts.jsonへ反映→正式経路で生成)、KP英語/日本語意味(K2/M2適用時のみ、Std 10・Adv 5+、profile拡張が前提)、Std KP #4 glossとcorrected版(KGCPW完了後、該当KPのみ)。**全記事の無条件再生成は不要**(Full Story/Preview/Comment/Intro等は変更なし)。費用見込みは委任_02で統合(IOL 2 call約JPY0.5〜2、KP再生成各約JPY0.2/clip級、REASSEMBLY計画§5の実測単価を参照)。
