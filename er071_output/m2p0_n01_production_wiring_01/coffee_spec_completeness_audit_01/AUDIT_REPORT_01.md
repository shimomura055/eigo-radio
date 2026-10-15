# AUDIT_REPORT_01(FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01 委任_02、2026-10-15、Read-only・JPY0)

最終Status: **`AUDIT_COMPLETE`**(監査完了)。結論を左右する未確認項目は無い(未確認は§11、いずれも結論=「要求を満たしていない」を覆さない)。音声成果物・Production仕様のStatusは変更していない(`PRODUCTION_WIRED`へ変更していない)。有料API 0・音声再生成0・SSOT/コード/Prompt/profile/音声/`user_test/`無編集。
入力: 01A(`A_COMPLETION_CRITERIA_RECONSTRUCTION_01.md`/`A_IN_ONE_LINE_TIMELINE_01.md`/`A_ROOT_CAUSE_CANDIDATES_01.md`)・01B(`B_ARTIFACT_OBSERVATION_01.md`/`B_SEGMENT_PROVENANCE_01.csv`)・OPEN_ITEMS(OPEN-298/299/313/316/321/350)・CURRENT_SPEC:2615-2630/583・`IN_ONE_LINE_REWRITE_01.md`・費用出典。**新規の観測は、統合中に追加で確認した2点のみ**(§4のFamily X In One Line Writer Prompt、§6の費用出典)。それ以外は01A/01Bの記載を引用。
マトリクス: `SPEC_REFLECTION_MATRIX_01.md`(+`.csv`、62行)。VALIDATED(Trial)とAPPROVED_FOR_PRODUCTIONは区別して記載した。

## §0 超サマリ(非エンジニアPM向け)

1. **結論: Coffee完成版(final_03)は当初のご要求を満たしていない。** 「最新の改善成果を網羅した完成版」にはなっておらず、承認済みなのに反映されていない項目が複数あります。
2. 反映されていなかった主なもの: (a)In One Lineが両レベルとも1文のまま(2文方針だけでなく、2026-08-09の正式仕様「中心1文+補足2文程度」にも未達)、(b)Key Phrase英語の読み方指示(K2)が両レベルで未反映、(c)Standardの日本語の意味(M2)が未反映。
3. 反映済みで問題なし: Full Story(N01)、Standard日本語のPreview/Comment(R2)、Advanced Key Phrase解説(P3)、Advanced Preview(E1)、Standard 6%減速、KP候補選び(M2P0)。
4. 確認できなかった(証拠不足)もの: 冒頭のWelcome/Preview intro(A5/B5)。Trialで作った音声ファイルは使われているが、生成時の指示文の記録がない。Advanced Commentの声の指示はユーザー判断待ち。
5. In One Lineが1文だった根本原因は2層。(1)生産ラインのIn One Line作成指示文自体が「Exactly one sentence(必ず1文)」になっていて、正式仕様と食い違っていた。(2)2文方針を決めた後も、2文版の原稿は試験用ファイルにしか無く、10-13の「検証済み音声を引き継ぐ」処理で古い1文の音声に置き換わったが、誰も文数を確認しなかった。
6. 制作・受入の工程に、「承認済みの仕様を全部、完成品と照合する表」がなかった。技術テストが全部通ったことが「仕様が全部入った」と読まれた。
7. 音声の作り直しは全体ではなく、最大17個の音声ファイル(In One Line 2、Key Phrase英語 Std5+Adv5、Std日本語の意味5)で足りる。Full Story・Preview・Commentは作り直し不要。費用は確定した単価の出典がなく未確認(参考値は§6)。
8. 現状のまま公開しても、記事の内容に誤りは見つかっていない(体裁・声のStyle・要点整理の長さの差)。
9. ユーザー判断が本当に必要なのは4点(§9): In One Lineの仕様の持ち方、是正範囲と順序の承認、Advanced Commentの声、Coffee原稿の正本(既存の判断待ち)。
10. 本監査はここでSTOPします。是正の実施はご判断後です。

## §1 結論: Coffee完成版(final_03)は当初要求を満たしていたか

**結論: 満たしていない(Standard・Advanced共に)。** 判定の根拠は、区分1(正式採用済み)・区分2(Coffee限定採用)・区分4(個別指示)の「必須」「今回対象」行(マトリクス参照)。区分3(VALIDATED未採用)は「完成版に入れてはならない項目」であり、混入は確認されなかった(3-1,3-2,3-4=非混入、3-3,3-5,3-6は証拠不足)。VALIDATEDであってもProduction未採用の仕様(ポーズ緩和・H-speed/8way等)は、要求に含まれず反映対象でもない。

| level | 満たした範囲 | 満たさなかった範囲 | 判定できなかった範囲 |
|---|---|---|---|
| Standard | M2P0 KP供給(1-2)、N01+6%減速(1-3S,1-4,2-7,2-8)、Comment4『最後に』(1-5)、Rule7/Source gate(1-6)、gloss整合(1-7S、legacy版)、Topic intro/IOL/title Style(1-9,1-10,2-9)、R2(2-3,4-2c)、Fragment方針(4-6)、ASR(D-3)、構成(1-13) | **In One Line 1文(1-1,4-1,4-2a)、KP英語K2未反映(2-4S)、KP日本語意味M2未反映(2-5)、承認済み仕様の照合なし(4-8)** | A5/B5(2-1S)、Fact Lock経路(1-11)、JA配分(1-12)、KP繰返し構成(1-13b)、試聴ページの数値掲載(4-4) |
| Advanced | M2P0 KP供給、N01(1-3A,2-7)、E1(2-2)、P3(2-6,4-2b)、IOL Style(2-9)、Fragment方針、ASR | **In One Line 1文(1-1,4-1)、KP英語K2未反映(2-4A)** | A5/B5(2-1A)、Adv Comment正本(4-5、E0=Production定数、Trial v3はE2_UPBEAT) |
| 両共通の部分反映 | 再Assemblyの必須反映5点のうち(2)P3・(3)R2は反映済み | (1)In One Line確定仕様は未反映。(4)変更対象音声の更新と(5)runtime evidence+試聴ページ確認は部分反映(IOL/K2/M2/A5/B5/Adv Commentが旧take・既定Style・Trial seedのまま、試聴ページは適用仕様を表示しない) | - |

「必須反映5点」は5点中、完全に満たされたのは2点(P3/R2)のみ。

## §2 Std/Adv別の仕様反映一覧(マトリクス要約、62行)

詳細・証拠は`SPEC_REFLECTION_MATRIX_01.md`。行数は分割後(S/A枝番・4-2をa〜eへ展開・1-13b追加)。同一欠陥が複数行に出る(1-1/4-1/4-2aは同一のIOL問題)ため、**実質の欠陥種別は「IOL文面」「K2」「M2」「照合表なし」の4種**。

| 区分 | 反映済み | 部分反映 | 未反映 | 証拠不足 | 非混入(適正) | 参考値のみ | 該当なし | 計 |
|---|---|---|---|---|---|---|---|---|
| 区分1 正式採用済み | 10 | 1 | 1 | 3 | 0 | 0 | 1 | 16 |
| 区分2 Coffee限定採用 | 6 | 1 | 3 | 2 | 0 | 0 | 0 | 12 |
| 区分3 VALIDATED未採用・保留 | 0 | 0 | 0 | 3 | 3 | 0 | 0 | 6 |
| 区分4 個別指示 | 4 | 3 | 3 | 2 | 0 | 0 | 0 | 12 |
| 区分5 不採用・保留・対象外 | 0 | 0 | 0 | 0 | 5 | 0 | 1 | 6 |
| 区分6 完成後承認 | 0 | 0 | 1 | 0 | 0 | 0 | 2 | 3 |
| 区分D 品質・完成状態 | 2 | 2 | 0 | 1 | 0 | 2 | 0 | 7 |
| 合計 | 22 | 7 | 8 | 11 | 8 | 2 | 4 | 62 |

「必須」「今回対象」かつ未反映/部分反映は14行(未反映7:1-1,2-4S,2-4A,2-5,4-1,4-2a,4-8 / 部分反映7:1-8,2-10,4-2d,4-2e,4-3,D-4,D-5)。区分6の6-1(corrected gloss)の未反映は完成後承認のため過失ではない(時系列上正当)。

## §3 未反映・部分反映・証拠不足の項目(優先度付き)

**優先度1(要求を直接満たしていない)**
- IOL 1文(1-1,4-1,4-2a): Std/Adv。
- KP英語K2未反映(2-4S,2-4A): Std 4件+1件証拠不足、Adv 8件+2件証拠不足。実使用=Production既定MINIMAL Prompt(1076字、sha 2b0c7505…)、K2(332字、9d905cfe…)ではない。
- KP日本語意味M2未反映(2-5): Std 5件。実使用=ae68e3e6(65字)、M2(67字、e7617e15…)ではない。
- 承認済み仕様の照合表なし(4-8): CHECKLIST_05に網羅項目なし。

**優先度2(部分反映・結論は変えないが完成宣言の根拠が弱い)**
- A5/B5(2-1S,2-1A、証拠不足): 音声ファイルのshaはTrial A5/B5.wavと一致するが、生成時Prompt hashの記録なし、Audio Gate走査対象外。
- 2-10 profile機構: K2/M2/A5/B5/IOLはprofile外(`er019_family_x_style_profile_01.py:16-17`「後続Phase」、OPEN-313申し送り)。
- 4-2d/4-2e/4-3 必須反映5点(4)(5)と旧新識別: 試聴ページはComment/Preview/IOL/英英解説の本文・使用Style・再利用由来を表示しない。
- 1-8,D-4,D-5 Gate/継承: Gate対象はoverride済みroleのみ、固定Master phrase 18wavはGate外、Adv Full Storyの継承根拠はmtime+長さ、Adv preview/comment_1-4にsha256欄なし。
- 4-5 Adv Comment: Production定数E0(`calm, conversational`、57c3fda6)で、Trial v3「E2_UPBEAT」・tone-run(`warm, upbeat…`、37c52d6e…)とは不一致。承認Style正本が未確定(OPEN-350)。

**優先度3(結論に影響しない確認事項)**
- 1-11(Fact Lock経路)、1-12/3-6(Coffee原稿正本=OPEN-326)、1-13b(Std KP繰返し構成)、3-3(異音検知混入)、3-5(F1記録)、4-4(試聴ページへの数値掲載)、D-7(日本語読みの聴感)。
- 6-1 corrected gloss: final_03はlegacy版(完成後承認)。Std rank4(`based on interviews`)のみ再判定対象。

## §4 In One Lineが1文のままになった根本原因

**2層に分けて記述する。「正式仕様未達」と「2文方針未反映」は別の問題。**

### 層A: 正式仕様未達(CURRENT_SPEC:583、2026-08-09)
- 正式仕様は「中心1文+英語の短い補足2文程度」。ところが**Family Xの本番In One Line作成Promptは`Exactly one sentence.`**(`er003_v1_n3_01_advanced_adaptation_generate.py:551-558`の`FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE`。ER-045 Trialの逐語Promptの再利用、`build_family_x_in_one_line_prompt`:605)。当該文言を導入した最新のコミットは2026-09-29(`git log -S`)、最初の導入日は未確認。
- この「1文化」を決めたSSOT記録は、本監査のGrep範囲(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSで`In One Line v2`/`one sentence`/`Exactly one sentence`)では確認できなかった(未確認)。つまり**CURRENT_SPEC:583と本番Promptが食い違ったまま運用**され、Coffeeを含むFamily Xの通常生成は1文になる構造だった。これはIn One Line単独の見落としではなく、approved spec(583)がFamily X本番Promptに反映されていない(原因分類2)。`IN_ONE_LINE_REWRITE_01.md:4`は「現行完成版は中心1文のみ=この既存仕様の履行不足」と過去から認識していた。
- 参考: `er003_v1_n3_01_articles_generate.py:167`(旧A2/B1 Writer)は「1〜2文の結び」で、これも583の「中心1文+補足2文程度」とは完全一致しない。

### 層B: 2文方針(OPEN-299)の未反映
| # | 日付 | 事象 | 誰が/どの段で何を見落としたか(証拠) |
|---|---|---|---|
| 1 | 2026-10-12 | ユーザーが両レベル「2文基本(必要なら3文)」と決定。v3制作時にIOL新原稿をLLMで生成(Std31語/Adv40語、各1 call、JPY0.0806/0.1237)。**Trialではなく個別指示**で、VALIDATED・仕様化とも無し | 決定の逐語はRepo外(未確認)。Sonnetは2文版を`iol_final_text_01.json`(Trial隔離)にだけ保存し、記事ソース`parts.json`へ戻さなかった。Trial隔離の設計上の帰結(`IN_ONE_LINE_REWRITE_01.md:7-13`) |
| 2 | 2026-10-12 | OPEN-299起票(OPEN候補・未仕様化・未承認)。必須反映5点の(1)に「確定したIn One Line関連仕様」。ただし前提のUDR #1はComment4採否に寄り、IOL文数の独立した判断依頼になっていない | Fable/Sonnet。仕様化の判断が独立項目として提示されず、確定前に再Assemblyが進行(`A_IN_ONE_LINE_TIMELINE_01.md` #5,#6) |
| 3 | 2026-10-12〜13 | v4→v5→M2P0/N01設計はIOLを「再利用・同一text」と想定。OPEN-299/316/321・REASSEMBLY計画への参照0件 | Sonnet設計。「再利用=同一text」が検証されていない(WIRING_DESIGN_01.md:116) |
| 4 | 2026-10-13 | COMPLETION-01 FIX2設計が「同一textでの再生成」「e_tone_01検証済み別take引継ぎ」を選択肢に挙げたが、(b)が文面(1文⇔2文)を変える点は指摘なし | Sonnet設計(`FIX2_DESIGN_01.md:9-11,38-40`) |
| 5 | 2026-10-13 21:55-56 | **決定的な段**: 検証状態引継ぎ処理。Advのv3 2文版wav(sha 645cac39…)は`WITNESS_SHA256_MISMATCH`で不採用となり、tone-run由来の旧1文wav(897ca8bf…、5.28秒)がREUSED_VALIDATEDとして採用。Stdもtopic_intro/IOLはe_tone_01 seed。判定基準は「style sha一致」と「textがparts.jsonと一致」のみ。DECISION_LOG:21007にIOL文面変更の記載なし | Sonnet実装。**文数が仕様(583/OPEN-299)と合うかを見る箇所はどの工程にも無かった**。Std置換前の実態は未確認(Stdの`_replaced_02`退避なし) |
| 6 | 2026-10-13 | `F1_RUNTIME_EVIDENCE_02.md:17,19`にIOL asr_textの旧1文冒頭が表示されていた | Sonnet→Fable。2文版との差として認識された記録なし(Fable側の個別メモはRepo内に無く未確認) |
| 7 | 2026-10-14 | final_03・CHECKLIST_05(12項目)。IOL/K2/M2/A5/B5の照合項目なし(「In One Line」語0件) | Sonnet作成・Fable受入。網羅性確認が無く、`PRODUCTION_WIRED`を付与しないことで未完を示したが、反映漏れの有無は検出されなかった |
| 8 | 2026-10-15 | ユーザーが試聴で発見 | 自己検出なし(ユーザー発見) |

**一文の要約**: 本番のIn One Line作成指示が「必ず1文」で、正式仕様(中心1文+補足2文程度)と食い違ったまま運用されていた(層A)。さらに、2文方針の原稿は記事ソースに戻らず試験用ファイルにしか無かったため、10-13の検証状態引継ぎで旧1文の検証済み音声に置き換わったが、文数を照合する工程と完成宣言時の仕様照合表がなく、誰も気付けなかった(層B)。

## §5 Key Phrase/Voice Prompt等の実際の反映証拠

### 5-1 Style照合の集計(`B_SEGMENT_PROVENANCE_01.csv`、SFX除く64行)
- 一致 26(Std 11+Adv 15)/不一致 17(Std 9+Adv 8)/証拠不足 7(Std 3+Adv 4)/部分一致 14(Std 7+Adv 7)。**委任文の「一致17」は01B集計(§3 集計)と異なり、01Bの合計は26+17+7+14=64**。
- 一致: Std Preview/Comment1〜4=R2(625826c1)、Adv Preview=E1(8862317f)、Adv KP英英解説5=P3(a8aaec59)、Full Story 6=N01(d1956c91)、Std Topic intro/title/IOL Style。
- 不一致: KP英語(Std 4+Adv 8)が既定MINIMAL(2b0c7505)、Std KP日本語意味5が既定(ae68e3e6)。K2・M2のhashとは一致しない。
- 証拠不足: Welcome/Preview intro×2level(4)、Std KP1英語(Master cache hit、style記録なし)、Adv kp2英語/繰返し(記録なし)。
- 部分一致: 固定Master phrase(KP intro/FS intro/num)はmanifest sha一致のみ。

### 5-2 K2/M2が未適用の構造的理由
- Coffee限定のStyle profile機構(OPEN-300 Phase 1)の対象roleは`FULL_STORY/SUPPORT_JA/KP_EXPLANATION_EN/PREVIEW`のみ。`er019_family_x_style_profile_01.py:16-17`が「他Role(K2/M2/A5/B5/E1/R2等)は後続Phase」と明記。OPEN-313(Phase 2申し送り)に「E1・M2・K2は未着手」と記録(E1とR2のみその後配線)。
- 2026-10-12のユーザー決定はK2/M2/A5/B5をCoffee限定`APPROVED_FOR_PRODUCTION`(Style選択のみ)としたが、実装単位(profile)への落とし込み起票が無いまま、Full Story→N01/R2/P3/E1だけが順次配線された。OPEN-350は「E1」だけを未配線STOPとして拾い、K2/M2は同じ構造なのに判定表に載らなかった(`ADV_STYLE_FACTCHECK_02.md`のrole表にKP英語/日本語意味の行がない)。
- M3 Style Gateの対象は`_gate_targets`のoverride済みroleのみのため、K2/M2不一致はGateでは検出できない構造だった(`B_ARTIFACT_OBSERVATION_01.md` §3末)。

### 5-3 gloss再整合
- final_03はlegacy版: `a2/key_phrases/gloss_alignment_runtime_metadata.json:3-4`(version `ER-003-KP-GLOSS-ALIGN-01`、`ALIGN_PASS`、targets=[4])、`keywords_canonicalized.json:145-148`(`GLOSS_REALIGNED`、`gloss_alignment_status`/`mode`/HRキー0件)。実行2026-10-14 20:14 JST、corrected設計commit 7ca292b44(2026-10-15 12:40)より前。Std rank4のみ`～をもとにした→インタビューをもとにした`。Advは日本語glossを音声に使わず未実行。corrected採用(2026-10-15)は完成後なので過失ではない(6-1)。

### 5-4 E0/E2(Adv Comment)
- Adv Comment1〜4=`calm, conversational`(E0、57c3fda6)。Production定数(CURRENT_SPEC「PREVIEW/COMMENTはE0のまま」)とは一致するが、Trial v3の「既存承認E2_UPBEAT」とは不一致、tone-runは`warm, upbeat…`(37c52d6e…)。main SSOTにwarm,upbeatの承認記載はなく、2026-10-14のユーザー指示は「E0の新規採用は承認していない」。**どれが承認Style正本かが未確定のためPASS/FAIL判定不能**(4-5=証拠不足)。内容・語彙は本文Partと話題接続(人手意味判定は未実施)。

### 5-5 A5/B5
- Welcome/Preview introは`seed_provenance_04`/`03`のとおりTrial生成wav(origin T)を無加工で組込み(sha 44f6ceb9…=Trial A5.wav、19932746…=Trial B5.wav)。生成時Prompt hashはRUN内に記録なし。Trial SPECSの文字列hash(A5 2c530b21…/B5 5e28dd28…)との間接照合のみ。Audio Validation Gateの走査対象外(`shared_narration={}`、assemble.py:469-508)。**Production経路で生成されたものではない**(経路の違いであって、同一Promptの音声である可能性は残るが、証拠は間接のみ)。
- A5/B5の記録なし: Production runnerのresults/audit内に生成記録が無い(2-1S/2-1A=証拠不足)。

## §6 必要な是正内容と最小限の再生成範囲

**全記事・全segmentの無条件再生成は不要。** 変更対象は以下のsegmentのみ(Full Story・Preview・Comment1〜4・Topic intro・title・固定phrase・N01/R2/P3/E1適用済みsegmentは不変)。

| 是正 | 対象segment | 数 | 前提条件 |
|---|---|---|---|
| A. In One Line 2〜3文化 | Std `in_one_line`(+6%減速+減速後ASR)、Adv `in_one_line` | 2 | (1)ユーザー判断§9 a。(2)2〜3文原稿をLLM(`gpt-6-luna`)で作成し、`parts.json`(記事ソース)へ反映してから生成(Trial付属ファイルに留めない)。(3)Family X本番Prompt(`Exactly one sentence`)を変更する場合はProduction Prompt変更=別承認・Opus条件C対象(Coffee限定の個別反映なら本番Prompt無変更で可能かは設計判断。実装は本監査範囲外)。(4)Comment4との接続(Std C4は「最後に」+豆以外の費用)は2文目で回収できるか再確認 |
| B. K2適用 | Std `kp1〜5`英語、Adv `kp1〜5`英語(繰返しと同ファイル共有) | 最大10(Std5+Adv5ファイル) | profile拡張(OPEN-313 Phase 2: reuse判定のprofile照合、Master Storeの`style_instruction_id`を`coffee_*`に分離)。設計変更を伴うため、Opus条件Aの要否はFable判断(PM_GOVERNANCE 11-3) |
| C. M2適用 | Std `meaning_1〜5` | 5 | Bと同じprofile拡張 |
| D. corrected gloss再判定 | Std `meaning_4`のみ(rank4 `based on interviews`) | 0〜1 | KGCPW 委任_03完了後。再判定でglossが変わった場合のみ再生成。他rankは再整合targetに入らない(変化は未確認) |
| E. A5/B5の来歴固定(再生成ではなく記録) | Welcome/Preview intro×2level(固定phrase 4wav) | 0〜4 | まずTrial生成記録とwavの対応を確認(無料)。対応が確認できなければ再生成を検討 |
| F. Adv Comment | Adv `comment_1〜4` | 0〜4 | §9 cの判断でE2_UPBEAT等に変更する場合のみ |
| 共通 | assemble再実行、試聴ページ(適用仕様の表示を追加)、final_04として旧版と識別 | - | 再生成segment以外は継承。Adv Full Storyの継承根拠(mtime+長さ)の再確認 |

合計: 確定分は最大17ファイル(A=2、B=10、C=5)。D/E/Fは条件付き。順序は 判断→KGCPW 委任_03完了→profile拡張(B,C)→A(原稿確定)→D→assemble→適用仕様一覧付き試聴ページ。`--only-segments`系を使う場合、OPEN-329記載の設計欠陥(選択外entry上書きによる正式assembleのBLOCK)が委任_02の是正②③でどこまで解消されたかを実行前に確認すること(未確認)。

**費用見積(出典のある値のみ)**: 
- IOL原稿LLM: Trial v3実績 Std JPY0.0806+Adv JPY0.1237=JPY0.2043(`IN_ONE_LINE_REWRITE_01.md:8`、実績。2文版の再生成が必要な場合の目安。ただし2〜3文版の再作成は別callで、同額とは限らない)。
- IOL TTS2 call+ASR: 約JPY0.4(`FINAL_V3_BUILD_PLAN_01.md:20`、事前概算)。
- KP英語TTS: Adv K2 Trial 5 call 実費約JPY0.15(`FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01_04.md:10`、請求画面未確認、ASR費の含有は記載なし)。
- **1 segment TTS+ASRの確定単価は出典から確定できない=未確認**。参考(単価ではない): final_03生成の累計はStd JPY34.45/Adv JPY30.01(run全体、scaffold等込み)、Trial v3全体は約JPY14.3。上記を積み上げた合計額は出さない(単価前提が未確認のため)。
- 予算境界: ユーザー側の既存運用(Trial費用JPY100以下はFable判断承認)の範囲に収まる見込みだが、これは見積であって確認済みの数字ではない。

## §7 反映漏れを引き起こしたPM・制作工程の問題(ユーザー§5の6分類)

| # | 分類 | 該当度 | 証拠 |
|---|---|---|---|
| 1 | Trial成果が正式な採否判断につながっていなかった | 中 | 2文IOLはTrialですらなく個別指示で、OPEN-299は未仕様化のまま(`OPEN_ITEMS.md:802`)。K2/M2/A5/B5はCoffee限定採用(Style選択のみ)とされたが、実装起票がOPEN-313の申し送りのみで、profile実装単位への落とし込みが進まなかった |
| 2 | 採用済み仕様がProduction経路に反映されていなかった | **高** | (a)Family X本番IOL Promptが`Exactly one sentence`で、CURRENT_SPEC:583と食い違い(§4 層A)。(b)K2/M2/A5/B5はprofile外(§5-2)。OPEN-350はE1だけを拾った |
| 3 | Production側にはあるが旧artifact/seedを再利用した | **高** | Adv IOLは旧1文wavへ置換(witness mismatch→旧take採用)、Std IOL/topic_intro=e_tone_01 seed、固定phrase=Trial seed/Master Store、Adv Full Story継承がmtime+長さ(D-5) |
| 4 | 完成条件に必要仕様の網羅性確認がなかった | **最高** | CHECKLIST_05は配線12項目。承認済み仕様の全件照合表なし。`In One Line`語0件。#11(b)は「Std KP=既存」としか見ていない。必須反映5点・OPEN-299/316/321への参照0件。PM_GOVERNANCEのGate 7補足(a)〜(m)・Closeout項目3/7も、ユーザー承認項目と完成物の照合を直接は求めていない(`PM_GOVERNANCE.md:243-262`、`:476-`) |
| 5 | Fableが実際の完成物を照合せず受入れた | 中(証拠不足) | CHECKLIST_05に網羅項目がなく、受入は配線完了度に偏った可能性。Fable個別メモはRepo外で未確認。`F1_RUNTIME_EVIDENCE_02.md:17,19`にIOL旧1文が表示されていたが差異報告なし |
| 6 | CURRENT_SPEC/Decision Log/Open Itemsが制作時に参照されなかった | **高** | Style系SSOT(OPEN-350/313、CURRENT_SPEC:2620-2625)は参照された一方、文面系(IOL: OPEN-299/316/321、583)は参照されず。SSOT自体も二重記述(CURRENT_SPEC:2620はStd Preview/CommentをP2、2624がR2。2620の同段落は『K2/M2は後続』を明示せず)で読みにくかった |

**構造的な共通原因**: 「Style(profile)」は配線されるが「文面(IOL)」と「profile外のStyle」は配線対象として追跡されない。承認の単位(Coffee限定のStyle選択+個別指示)と実装・検証の単位(profile role、配線チェックリスト)が一致していなかった。

### Day 2運営モデル刷新との関係(再発防止の検討事項。進行中の実装へは介入しない)
今回の問題は、Day 2運営モデルで検討中のF3独立受入・承認済み指示欄(W6)・Gate 7集約が狙う領域と直接重なる。検討事項として: (1)ユーザー承認済み指示(必須反映5点、IOL 2文、K2/M2/A5/B5等)を1か所の承認済み指示欄に束ね、完成宣言時にその全件を「反映済み/未反映/部分」で受入側が照合できるか。(2)受入判定が実装者の配線チェックリスト(CHECKLIST_05型)とは別の独立した照合を持てるか。(3)Trial隔離の付属成果物(IOL原稿等)が記事ソース/仕様へ戻る経路を、Coffee限定採用の登録時点で決められるか。本監査は提案ではなく検討事項の提示に留め、運営モデル側の設計・規則・SSOTには触れていない。

## §8 QDC影響・費用見込み

- **Q(品質)**: 是正の効果は、(a)In One Lineが記事の要点を意味・示唆まで述べる長さになる、(b)KP英語が「ひとまとまりに読む」K2、日本語意味がM2になる(声のStyle差)、(c)承認済み仕様と完成物が一致し、以後の判断が正しい前提でできる。
- **現状のまま公開した場合の学習者への影響(重大誤解原則の観点)**: 内容の誤りは観測されていない。IOL 1文は記事の事実(段落6の「少なくとも約9か月」、hedgeの"may")に整合しており、事実誤認・数値誤りは見つかっていない(01Bの事実対応表と整合、新規のfact checkは未実施)。差は**体裁・Style・要点整理の厚み(1文 vs 2〜3文)**で、仕様違反ではあるが学習者に誤解を与える種類の問題ではない。KP gloss(legacy整合)の文字列は意味整合しているが、聴感・人手の意味判定は未実施。
- **D(工数)の相対規模**: 小〜中。再生成は最大17ファイルと小規模だが、profile拡張(B,C)は設計変更を伴い、Aは原稿確定とparts.json反映が前提。KGCPW 委任_03完了待ちがクリティカルパス。実時間は未確認(見積の根拠となる直近実績の出典を確認していない)。
- **C(費用)**: §6のとおり確定単価の出典なし(未確認)。参考として、2文IOL原稿LLM実績JPY0.2043、IOL TTS+ASR概算約JPY0.4、KP英語5 call約JPY0.15(Trial)。

## §9 未解決事項・ユーザー判断が本当に必要な事項

### ユーザー判断が必要(4点)
**(a) In One Lineの仕様の持ち方**
- 選択肢: A) 正式仕様(CURRENT_SPEC:583「中心1文+補足2文程度」)に準拠して作り直し(Family X本番Promptの`Exactly one sentence`を是正する前提で、Coffeeは個別反映)。B) 2文方針(OPEN-299、両レベル2文基本・必要なら3文)を正式仕様として確定し、583とFamily X本番Promptを揃える。C) Coffeeだけ2〜3文で完成させ、仕様化は保留。
- 影響: Aは仕様改訂なしで整合するが、2文基本の意図(1+補足1文)より長くなり得る。Bは仕様化(Writer/Checker/難易度/Comment4接続)の作業が増え、全記事へ及ぶためProduction Prompt変更(Opus条件C対象)になる。Cは最小だが仕様の食い違いが残る。
- **推奨: C(Coffeeを2〜3文で作り直し)+仕様化の判断(A/B)は完成後に別途**。理由: ユーザーが「2文基本(必要なら3文)」と決定済みで、2〜3文は583の「計約3文」とも両立するため、Coffee完成版はどちらの解釈にも合致する。仕様化は全記事共通のProduction変更になり、Coffee完成の足止めにすべきでない。

**(b) 是正範囲と順序の承認**
- 選択肢: 1) §6のA+B+C(最大17ファイル)をKGCPW 委任_03完了後に実施。2) Aのみ先行(IOL 2ファイル)、K2/M2は後続。3) 実施せず現状を『Trial扱い』として記録。
- 影響: 1)は要求充足、2)はK2/M2の未反映が残る(承認済み)、3)は『完成版』とは言えない。
- **推奨: 1)**。理由: K2/M2はCoffee限定で`APPROVED_FOR_PRODUCTION`済みの要求で、反映しないとユーザー要求の「網羅」を満たさない。profile拡張が前提のため、設計はOpus条件Aの要否をFableが判断する。

**(c) Adv Comment1〜4の承認Style正本(E0 / E2_UPBEAT / tone-runの warm, upbeat)**
- 影響: 現状はE0(Production定数)。Trial v3の聴感に近づけるならE2_UPBEAT相当の再生成4 segment。
- **推奨: ユーザーが試聴して決定(現状維持E0、または変更)**。理由: 2026-10-14にE0の新規採用は承認していないと明示済みで、Fable/Sonnetが決められない聴感判断のため。

**(d) Coffee原稿の正本(OPEN-326: v5 Tone原稿 vs Production L3原稿)**
- 既存の判断待ち(UDR #4)。final_03はv5 Tone原稿。**推奨: 現状のv5維持を確認する**(X-1推奨で進行済み、変更は全segment再生成になるため)。判定: 本件の結論には影響しない。

### 開発側で是正(承認不要。技術的に自明・既存機構の範囲)
1. CURRENT_SPEC:2620のStd日本語Preview/CommentのP2記述を、2624のR2が後勝ちである旨を明記して整理(二重記述の整理)。
2. A5/B5のTrial生成記録(`er057_tone_trial_tts_gen_01.py` SPECS)とseed wavの対応確認と文書化(無料。確認できなければ再生成を§9へ再提示)。
3. Std rank4のcorrected gloss再判定(KGCPW 委任_03完了後、結果が変われば`meaning_4`のみ再生成)。
4. Fact Lock/Risk guard経路(1-11)、F1記録(3-5)、Std KP繰返し構成の仕様出典(1-13b)の確認。
5. 試聴ページに適用仕様の要約と生成日時を表示(4-3、既存ページ生成の拡張)。
6. CHECKLIST系の運用: 完成宣言時に「承認済み仕様×完成物」の照合表を1表で添付(既存のGate 7/Closeout Check項目3の運用強化。新Validator・新管理制度ではない)。
7. K2/M2のprofile拡張(OPEN-313 Phase 2)は、承認済みだが未配線の項目の実装であり、(b)の承認後に実施。

## §10 SSOT追記文案(本委任では書かない)

- CURRENT_SPEC:2620付近の整理案: 「Std日本語Preview/Comment1〜4のCoffee限定Styleは**R2**(2026-10-12 V5委任_01、sha 625826c1…)。本段落冒頭の『P2』は2026-10-12の旧決定で、R2が後勝ち。」
- OPEN-299更新案(2026-10-15 CFSA監査): 「final_03のIn One Lineは両レベル1文15語で、正式仕様(CURRENT_SPEC:583)にも本方針にも未達。原因: Family X本番IOL Prompt(`FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE`)が`Exactly one sentence`で、583と食い違い。2文版原稿はTrial付属ファイルのみで、10-13の検証状態引継ぎで旧1文wavへ置換。是正はユーザー判断(CFSA監査§9 a)待ち。」
- OPEN-313更新案: 「K2/M2/A5/B5が`APPROVED_FOR_PRODUCTION`(Coffee限定、2026-10-12)のままprofile外であることが、final_03で未反映の原因(CFSA §5)。Phase 2配線を要する。」
- 新規Open Item候補(起票は別委任): (i)`FAMILY-X-IN-ONE-LINE-PROMPT-VS-SPEC-583-MISMATCH-01` Family X本番IOL Prompt(`Exactly one sentence`)とCURRENT_SPEC:583の不一致の解消(Production Prompt変更を伴う場合はOpus条件C)。(ii)`COFFEE-FINAL-APPROVED-SPEC-CHECK-AT-COMPLETION-01` 完成宣言時の承認済み仕様×完成物の照合(既存Gate 7/Closeout Check運用の範囲)。

## §11 確認できなかった事項(推定/事実の区別)

**事実として未確認**:
1. ユーザーが2文基本と決定した2026-10-12のチャット原文、およびCoffee完成版を最初に依頼した原文(Repo内に逐語なし)。
2. Fableがfinal_03/COMPLETION-01 委任_02/04を受入れた際の個別メモ(Repo外)。
3. Std In One Lineの置換前の実態(Stdは`_replaced_02`退避が無い)。
4. A5/B5/固定phraseの生成時Prompt全文、IOL原稿LLMのPrompt本文・hash、Adv `in_one_line` wav(897ca8bf…)のe_tone_01側の生成時刻。
5. 日本語読みの聴感、KP難易度・自然さの人手判定、Adv Commentの意味接続の人手判定。
6. Std KPの英語繰返し音声の有無と、その仕様出典(1-13b)。
7. `Exactly one sentence`の最初の導入日と、その決定を記録したSSOT(Grep範囲では無し)。
8. Fact Lock/Risk guardがv5原稿に適用された実績、F1がfinal_03 resultsに記録されているか、試聴ページの数値掲載、`--only-segments`系のOPEN-329欠陥の解消範囲。
9. 1 segment TTS+ASRの確定単価(§6)。

**推定(事実と区別)**: Std KP1英語・Adv kp2英語/繰返しは他KPと同じMINIMAL(K2でない)と推定。Fable受入が配線完了度に偏った可能性(§7-5)。profile Phase 2の設計にOpus条件Aが必要かはFable判断。

**統合時の差異**: 委任文の「一致17」は01B集計と異なり26(01Bの内訳17は不一致)。
