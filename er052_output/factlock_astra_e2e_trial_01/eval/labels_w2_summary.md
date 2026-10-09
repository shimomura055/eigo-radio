# labels_w2 要約(FACTLOCK-ASTRA-E2E-TRIAL-01 委任_14b、worker2: small_bag / byd_recall / central_bank_mortgage)

**これは Sonnet の暫定ラベル(`label_source=sonnet_w2`)であり、人間確認の代わりの推測。確定扱いしない。** 判定線の評価・VALIDATED等の宣言はしていない。API支出¥0、git操作なし、runs配下は読み取りのみ。
ラベル本体: `er052_output/factlock_astra_e2e_trial_01/eval/labels_w2.jsonl`(242行、1行1ラベル)。基準は `docs/pm/open233_materiality_criteria_2026-10-03.md`(Fable案: 重大=事実関係の重大な誤解/軽微=核心は保たれ言い回しの精度低下/問題なし)と PREREGISTRATION_01 の運用(因果付与は軽微)。

## 0. 前提・注意

- 3テーマとも B3 `unmapped_claims`=空、AMBIGUOUS選択=空(`annotation/AMBIGUOUS_FACT_MAP.json`)。よって「B3由来(unmapped)」「AMBIGUOUS由来」の記録対象は無い。`origin=B3` は「注記済みbriefのStoryline/本文表現に由来する」意味で使った(`unmapped_claims`とは別)。
- 台帳は新旧同一(diff無し)。新腕 central_bank_mortgage は R0 で JA STOP のため、JA本文(採用)・EN・Checker は無い。
- 重複計上回避: JA由来の軽微は JA 列に計上し、EN には「JA由来の持ち越し」として記録(PREREGISTRATION 2-2)。
- **集計上の注意(重要)**: 旧腕 small_bag / byd_recall は案B(JA再生成)後に `ja_writer/*.md` が上書きされ、`telemetry/ii.json` の `final.text_sha256` は**案B前のR2**を指している(sha不一致で確認: small_bag 7275f… != eac0a2…、byd 684e2c… != a091e3…)。案B前の本文は保存されていない。したがって旧腕の(ii)件数(small_bag 3、byd 4)は**最終JAではなく案B前JA**の値で、`labels_w2.jsonl` の該当行は `text_available=false`・理由文とLedger照合のみの低確信ラベルとした。
- M3保護claim(新腕 byd Advanced n=5、small_bag Standard n=1)は telemetry に個別keyが無く特定不可。「再分類で除外されたがStage2に残ったclaim」を `reclassify_excluded_yet_in_stage2` として記録したが、M3保護と決定論候補は区別できない。

## 1. テーマ×腕 要約表(Sonnet暫定ラベル。重大の列は全て 0)

| テーマ | 腕 | JA FC指摘(系統判定→暫定ラベル) | JA最終に残る軽微 | EN最終(出荷側)に残るEN由来の軽微 | EN STOP/案B | Checker(一意claim: 真の軽微/総数) | Rewrite(必要/不要) |
|---|---|---|---|---|---|---|---|
| small_bag | 新 | 0件 | 0 | Adv 0 / Std 0 | なし | Adv 0/15、Std 0/13 | なし |
| small_bag | 旧 | original attempt1 MAJOR 1→軽微 | 3(排他的「ランウェイならでは」、記事+ランウェイへの一般化、「調べた結果ではない」) | Adv 0(JA持越し3)/ Std(STOP・rejected)MAJOR 2→軽微2 | 案B1回(発火理由=軽微2件)→Std STOP(軽微起因) | Adv 3/14 | なし |
| byd_recall | 新 | 0件 | 2(見出し/冒頭の無留保な現象描写[境界]、「足は踏んでいないのに…実況を続けてしまう状態」) | Adv 2(要約の「極端な場合」条件欠落、公告単数表記[低確信])/ Std(STOP・rejected)MAJOR 2→軽微2(要約:M1で解消、本文「will stop/prevent」) | Std STOP(軽微起因)、M1発火あり | Adv 4/21 | Adv 1件、**不要**(比喩ジョーク削除) |
| byd_recall | 旧 | original attempt1 MAJOR 2→軽微1・問題なし1 | 3(交換の因果付与、「ことがあります」[低確信]、公告単数[低確信]) | Adv 1(要約の条件・中国限定欠落)/ Std(STOP・rejected)MAJOR 1→軽微 | 案B1回(発火理由=軽微2件)→Std STOP(軽微起因) | Adv 2/17 | なし |
| central_bank_mortgage | 新 | R0: MAJOR 3件(初回1+再生成後2)→全て軽微(うち2件は軽微/重大の境界) | (R0 STOPで採用本文なし。rejected本文に軽微2) | 到達せず | **JA R0 STOP**(軽微起因の可能性が高い) | 到達せず | - |
| central_bank_mortgage | 旧 | 0件 | 0 | Adv 0 / Std 0 | なし | Adv 0/11、Std 0/6 | なし |

Checker 総括: 7 run・延べ一意claim 97件中、真の軽微は 9件(byd新4、small_bag旧3、byd旧2)、重大 0(small_bag新・central旧は0)。システムのBLOCKINGは1件のみ(byd新Advanced)で、それは偽陽性(下記)。

## 2. 重大見逃し一覧(最終本文に残る Ledger 食い違い、critical_trace形式)

**重大: 0件(両腕・担当3テーマ)。** 残存は全て軽微(暫定):

| テーマ | 腕 | 本文 | 該当文(要旨) | 台帳 | 暫定ラベル | origin | 確信度 | 備考 |
|---|---|---|---|---|---|---|---|---|
| small_bag | 旧 | JA(EN持越し) | ランウェイならではの華やかな出番です | MB-05 | 軽微 | Writer | 0.6 | StdのFCはMAJOR、Adv FC/Checkerは見逃し |
| small_bag | 旧 | JA(EN持越し) | ミニバッグが記事やランウェイで目立つこと | MB-01/05 | 軽微 | B3(Storyline) | 0.45 | MB-01+MB-05合成の一般化 |
| small_bag | 旧 | JA(EN持越し) | 売上や消費者全体を調べた結果ではありません | MB-06 | 軽微 | Writer | 0.4 | 台帳は「明示されていない」まで |
| byd_recall | 新 | JA(EN持越し) | 見出し/冒頭「踏んでないのに「ブレーキ中！」」 | BYD-07 | 軽微(境界) | Writer | 0.5 | 結果の核心を見出しで無留保に描写。本文は「おそれ」と留保。**人間確認候補** |
| byd_recall | 新 | JA | つまり…ランプだけが「踏んでます！」と実況を続けてしまう状態 | BYD-07 | 軽微 | Writer | 0.5 | 留保が弱い言い換え |
| byd_recall | 新 | EN Adv(翻訳由来) | In one line: faulty pedal pads may keep the brake lights on… | BYD-05/07 | 軽微 | translation | 0.6 | 「極端な場合」条件欠落、"may"は残る。Adv FC=compliant |
| byd_recall | 新 | EN Adv | A recall notice in China named 183,211 cars | BYD-01 | 軽微(低確信) | B3 | 0.4 | 実際は2公告の合算 |
| byd_recall | 旧 | JA(EN持越し) | 道路上の「送信ミス」を防ぐための部品交換 | BYD-11 | 軽微 | Writer | 0.6 | 因果付与。Adv FC合格、Std FC MAJOR |
| byd_recall | 旧 | JA | 極端な場合には…つき続けることがあります | BYD-07 | 軽微(低確信) | Writer | 0.35 | 「可能性」→「ことがあります」 |
| byd_recall | 旧 | JA | 中国国内の召回公告では…合わせて18万3211台 | BYD-01 | 軽微(低確信) | B3 | 0.35 | 公告は2件 |
| byd_recall | 旧 | EN Adv(翻訳由来) | A faulty part in some BYD cars could keep brake lights on… | BYD-05/07 | 軽微 | translation | 0.55 | 条件・中国限定欠落 |

出荷されなかった本文(別枠、判定線に入れない): small_bag旧 EN Standard、byd新 EN Standard(attempt1/2)、byd旧 EN Standard、central_bank_mortgage新 JA R0(attempt1/2)。いずれも重大なし、軽微のみ(`labels_w2.jsonl` の `shipped=false`)。

## 3. 特に丁寧に: central_bank_mortgage 新腕 R0 JA STOP

- 経緯: R0初回は FC MAJOR 1件(「APが示した固定型の住宅ローン金利の全米平均は5.98%から7.40%へ」、F007の「30年固定」を固定型全般へ拡張)。must-fixで1回再生成すると「長期固定ローン」に言い換えられ(前回指摘は未解消判定)、さらに別箇所「政策金利の目標を0.25ポイント引き上げ、3.75％から4.00％に」(「レンジ」脱落)が新たにMAJOR判定され、STOP。
- 暫定ラベル: 3件とも **軽微**(境界扱いは「固定型」と「レンジ脱落」の2件)。数値(5.98/7.40/0.25/3.75-4.00)自体は台帳と一致し、数値の創作・逆転・主体の取り違え・否定反転・因果創作は無い。その他の文(F003期待であり実現未確認、F007試算の留保、F008直接決めない、F010の複数要因、F001直近決定)は整合。本文に**重大な事実誤りは無い**と見る。
- 解釈(推測、要確認): (a) 「30年固定」は台帳notesが明示的に守らせたい帰属で、15年固定は6.73%(F006)。FCが厳格に見張った意義はあるが、STOP(人手介入)に値する水準ではなく過剰停止の可能性が高い。(b) 初回が「目標レンジ」と書いて合格していたのに再生成で「レンジ」が落ちたことから、must-fix再生成は無関係箇所に新しい揺れを生む。(c) B3注記は「30年固定」を `peripheral / name_embedded`(M6)に分類しており、Writerが言い換え可と解した可能性(未検証)。
- 比較: 旧腕は同じ台帳・同じ質問で「三十年固定型」と明記し FC 0件、EN・Checkerまで完走し真の問題0件。

## 4. その他の所見(各項目の根拠は labels_w2.jsonl)

- **B1回復**: 担当3テーマの新腕では発動なし(R2 FC MAJOR=0、`b1_counter.jsonl` の発動はhormuz/space_weapons/openai_copyright)。ラベル対象なし。
- **案B(旧腕2件)**: small_bag旧・byd旧とも、発火理由の指摘2件はいずれも軽微と推定(真に重大ではない)。再生成後に発火理由自体は解消(Advanced COMPLIANT)したが、Standardで別の軽微(ja_source MAJOR)が出てSTOPし、案Bは収束しなかった。
- **M1**: byd新 Standard で発火。attempt1の要約のみのMAJOR(軽微相当、極端な場合の条件欠落)は発火後に台帳整合となり解消。ただし再生成全体の揺れで本文に別の軽微("will stop…prevent")が生じてSTOP。同じ文の訳は Advanced では "is a measure to stop" で合格しており、Standard側の訳揺れ。M1の効果は要約の軽微解消に限り、STOP回避には至らなかった(交絡あり、単独効果とは書かない)。small_bag新・旧、central旧の m1a/shadow は全て COMPLIANT で差なし。byd旧の m1a alt は要約の条件欠落をMAJOR判定(軽微相当)、actualはCOMPLIANTで、FCの要約判定が揺れる証拠。
- **Checker**: 新腕byd Advanced の唯一のBLOCKING(「現場と広報が連絡していない」)は偽陽性、Rewrite(delete)は不要。Stage2の指摘の大半は決定論検査(否定・因果・fact_id欠落)や比喩文への偽陽性で、ACCEPTABLEへ降格。Checkerが出した関連factのID対応誤り(small_bag新Standard: MB-05をMB-03と誤対応)もあり。Stage1再分類のSUPPORTED/NO_FACT_CLAIM除外は全体に妥当で、除外が隠した事実問題は軽微1件(small_bag旧Adv の記事+ランウェイ一般化)のみ。

## 5. 所見3行

1. 担当3テーマ×両腕で、最終本文に残る重大(読者に事実の重大な誤解を与える)Ledger食い違いは暫定ラベル上0件。STOP 4件(small_bag旧Std・byd新Std・byd旧Std・central新R0)はいずれもFCのMAJOR判定が起点で、暫定ラベルでは軽微(境界2件)であり、軽微起因の人手介入だった可能性が高い。
2. FC(Luna)は同趣旨の文を段・attemptで判定を揺らし(Adv合格/Std MAJOR、同一箇所でattempt間の差)、案B・must-fix・M1による再生成は別箇所に新しい軽微を生んで収束しないことがある。出荷側本文には旧腕で軽微が約3件/テーマ、新腕byd 2〜3件・small_bag 0件が残り、FC・Checkerはこれらをほぼ見逃している(本Trialの軽微は許容されるレベルだが件数は腕で差がある)。
3. Checkerは新腕のRewriteが不要1件、システムBLOCKINGの偽陽性1件、M3保護の便益は確認できず。**人間確認候補: byd_recall(新旧、見出し断定の境界と軽微起因STOP)、central_bank_mortgage新(R0 STOPの軽微/重大の境界2件)、small_bag旧(軽微3件の残存とSTOP)**。
