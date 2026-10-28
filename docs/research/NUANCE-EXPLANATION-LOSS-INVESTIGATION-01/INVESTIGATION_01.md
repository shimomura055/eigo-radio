# INVESTIGATION_01 ニュアンス解説の消失原因調査(NUANCE-EXPLANATION-LOSS-INVESTIGATION-01 委任_01)

調査専用・API 0・Production code/Prompt/SSOT/既存解説データの変更0。原文=`docs/pm/delegation_log/2026-10-29_FX-AI-ISLAND-FINAL-PUBLISH-01_USER.md` §2〜§5B。調査日2026-10-29。
`git log -S` は `--all`(全ブランチ)で実施。以下のfile:lineはHEAD(work/post-merge-01)の実測。

## 1. 結論(いつ・なぜなくなったのか)

1. **「ニュアンス解説」はProductionに存在したことが一度もない。** 該当語はユーザー自身が2026-10-24に出した学習テキストTrial指示(`docs/pm/delegation_log/2026-10-24_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER.md:10`「文法・構文解説とニュアンス解説の品質を重視」、同:43「Part 3. Nuance & Deeper Understanding」)で初出。`git log --all -S"ニュアンス解説"` は3 commitのみ(e3285a2d1[Trial-01]・192961b9a[Fable評価]・75b300f36[Part 2のOpus依頼文]。いずれも2026-10-24〜25で、2026-10-24より前は0件)。`git log --all -S"Nuance & Deeper"` は2026-10-24〜25のTrial 6 commitのみで、Production codeのGrep(`git grep -n "Nuance & Deeper" -- '*.py'` で `docs/research` 配下を除外)は0件。`docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/ADOPTION_NOTE_04.md:7`も「英語学習テキスト解説(Part 1〜4)はProductionに存在しない」と明記。
2. **消えた経緯=「Trialが途中からPart 1・Part 2だけに絞られ、Part 3(ニュアンス)とPart 4が処遇未記録のまま置き去りになった」。** 廃止の決定でも、Production承認済みの配線漏れでも、後続変更のRegressionでもない。
   - 2026-10-24〜10-25 Trial-01〜04(Part 3を毎回生成): Z『賢者の贈り物』・Z『開いた窓』・X『イグ・ノーベル賞2026』(全てAdvanced)。最後に生成されたのはTrial-04(commit ec2b5ef83、2026-10-25)。
   - Trial-05はTrial-04 r1のPart 3/4を無編集再利用(`PREREGISTERED_CRITERIA_05.md:11,58`)。Trial-06〜08(`run_trial_06/07/08.py`にPart 3の記述0件)はPart 2のみ。
   - ユーザー指示がPart 1/2に絞られた時点: `..._USER_03.md:81-86`(Part 3・4は改善対象外、現行Prompt維持)、`..._USER_04.md:26`(同)、`..._USER_05.md:1-24`(A=Part 1正式採用、B=Part 2 Trial-07。Part 3/4への言及なし)。以後Part 3/4について採用・不採用・保留のユーザー判断も、Fable起票のUDRも記録に存在しない。
3. **ユーザーが廃止を承認した証拠はない**(§4)。よって「仕様変更済み」とは解釈しない。同時に、Part 3をProductionへ採用する承認もない(`APPROVED_FOR_PRODUCTION`の記録0)。分類(④): 明示的な仕様変更=いいえ / 承認済み仕様の配線漏れ=いいえ(承認自体がない) / Regression=いいえ / 仕様と表示の不整合=SSOT記述の軽微な不正確のみ(§3-D)。正確には「**未決のまま範囲外化(処遇未記録)**」。
4. **ニュアンスの内容自体は現行に残っている**(§5): Part 2の「意味・ニュアンス・表現効果」節(ユーザー承認済み)と、Part 1(②追加解説)の「類義語・近似表現との違い」観点。独立した「ニュアンス解説」Part(Part 3)だけが存在しない。
5. **AI島の公開データにおける承認済み学習仕様の重大欠落=なし**(§6)。Part 3は承認仕様ではなく、AI島Part 2の文法0件はユーザー正式確定(`2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_03.md:9-13`)。公開STOP不要。
6. 「以前存在した」というユーザーの記憶の起点は、上記Trial-01〜04出力(`OUTPUT_*_RAW/USER.md`)でユーザーが読んだPart 3、またはPart 2の「意味・ニュアンス」節の可能性が高い(推測)。これ以外に該当する旧機能の記録は、git全履歴・SSOT・delegation_logに見つからない(未発見であり、存在しないことの証明ではない=この点は「未特定」)。

## 2. 過去の実際の解説例(逐語)

**例1: Trial-01(2026-10-24、Z『賢者の贈り物』Advanced、gpt-6-luna一発生成、commit e3285a2d1)`docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/OUTPUT_01_RAW.md:29-36`**
> ## Part 3. Nuance & Deeper Understanding
> ### **worthy of** と **worth** の違い
> - **本文中の英文:** “How could she buy Jim something worthy of him?”
> - **日本語訳:** どうすればジムにふさわしいものを買えるだろう。
> - **本文中の英文:** “Like Jim, it needed no decoration to prove its worth.”
> - **学習ポイント:** **worthy of + 人・物** は「～にふさわしい」という形容詞の表現です。一方、**worth** は「価値」を表す名詞で、ここでは **its worth** が「それ自身の価値」を指します。どちらも価値に関係する語ですが、**worthy** は何かに見合うかどうか、**worth** は価値そのものに焦点があります。

**例2: Trial-04(2026-10-25、X『イグ・ノーベル賞2026』Advanced、commit ec2b5ef83)`OUTPUT_04_ig_nobel_r1_USER.md:76-79`**
> ## Part 3. Nuance & Deeper Understanding
> **take that number on its own** は、「その数字だけを切り離して受け取る」という意味です。本文では、結晶と哺乳類のミルクのエネルギー量を比べた数字だけを見て、「飲めば人も3倍元気になる」と考えるのは誤りだと注意を促しています。数字を正しく理解するには、何と何を比べたのか、また、その結果から何が言えるのかという文脈も見る必要があります。
> > Take that number on its own, and before you know it, a science story can turn into a TV shopping show.

(同Trial-04の賢者: `OUTPUT_04_gift_r1_USER.md:68-73` showy / Like Jim / prove its worth。)

**参考(現行Productionに残るニュアンス記述、§5の裏付け): AI島Adv ②追加解説 `call on` の解説(公開候補ページ `user_test/family_x_ai_island_form_01_candidate_b7_01/index.html:21`)**
> `call upon` も同じ意味で使われますが、やや改まった響きになることがあります。… 必要なものを求める `call for` とは異なり、`call on` は人に働きかける表現です。

## 3. 変更前後の仕様・Prompt・表示の比較

### A. Part 3の仕様・Prompt(Trialのみ)
| 時点 | 内容 | 根拠 |
|---|---|---|
| 2026-10-24 ユーザー原文 | Part 3: 本文から価値ある英語表現・ニュアンスを0〜1テーマ。単語の意味だけでは伝わりにくいニュアンス、似た表現との違い、印象の違いを深掘り。Part 1・2と重複禁止。感想・一般論でなく英語学習価値。本文根拠のない説明禁止 | `2026-10-24_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER.md:43-50` |
| 同 Prompt実装 | `## Part 3. Nuance & Deeper Understanding`(0〜1テーマ) | `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/run_trial_01.py:42-46` |
| Trial-01 Fable評価 | worthy of/worthは品詞差で基礎的。ユーザーが重視した「ニュアンス解説」が学習価値の高い水準に達しない→`USER_DECISION_REQUIRED`、改善はPrompt側選定基準で見込み | `FABLE_EVAL_01.md:8-9`、UDR #182(`docs/pm/USER_DECISION_REGISTER_01.md:376`) |
| 2026-10-24 ユーザー回答 | A/B/Cでなく「Part 1のみ変更の比較Trial」を選択。Part 3は「Trial-01のPrompt・仕様を変更しない」「worthy of/worthの解説もユーザーの許容範囲」 | `2026-10-24_..._USER_02.md:75-78` |
| 2026-10-25 Trial-03/04 | 「Part 3・4は改善対象外、現行Prompt維持」。Trial-04でPart 3/4を別callに分離(03dブロック一致assert) | `2026-10-25_..._USER_03.md:81-86`、`..._USER_04.md:26`、`run_trial_04.py:174-182` |
| 2026-10-25 Trial-05以降 | Part 3は再生成されず(05は04再利用、06〜08は記述0) | `PREREGISTERED_CRITERIA_05.md:11,58`、`run_trial_06/07/08.py`のGrep 0 |
| 2026-10-25 ユーザー統合指示 | Part 1正式採用+Part 2 Trial-07。Part 3/4の記載なし | `2026-10-25_..._USER_05.md:1-60,120-175` |

### B. Part 1(②追加解説)のニュアンス記述の変遷(ユーザー指示による再定義)
- Trial-03(実用性重視版)はPromptに「使うとどんなニュアンスが伝わるかを…説明」「似た表現との使い分けやニュアンスの違いが理解できるように」を明記(`run_trial_03.py:13,16`。ユーザー指示 `2026-10-25_..._USER_03.md:23,29`)。
- Trial-04(案α)でユーザーが観点を5つに再定義: 核となる意味/主要な用法・場面/コロケーション/重要な類義語・近似表現との違い/自然な比喩的・拡張的用法(`2026-10-25_..._USER_04.md` §3「解説の観点」)。「ニュアンス」の語は入らない。ユーザーは案αを`APPROVED_FOR_PRODUCTION`(`2026-10-25_..._USER_05.md:10-54`)。
- Production Prompt(`er003_kp_general_explanation_01.py:49-53`)は案αとバイト一致。ユーザー指定の5観点のまま。ニュアンスは「類義語・近似表現との違い」「比喩的用法」で扱われる。**ユーザー承認済みの再定義であり、Regressionではない。** ただしユーザーが「ニュアンス」の明示語削除を意識して承認したかは記録から読み取れない(未特定)。

### C. Part 2(文法・構文解説)
- Trial-04の4節構成(日本語訳/仕組み/通常表現との比較/**意味・ニュアンス・表現効果**)をユーザーが2026-10-25に正式採用。採用文面に「意味・ニュアンス・表現効果を解説する」(`2026-10-25_PART2-GRAMMAR-PRODUCTION-WIRING-01_USER.md:31`)。Production実装=`er120_part2_grammar_production_01.py:135,154,163-164`(`EXPLANATION_REQUIRED`に「意味・ニュアンス・表現効果」を含む)。PMの表記でも「意味・ニュアンス解説」=Part 2の節(`2026-10-25_PART2-GRAMMAR-PRODUCTION-WIRING-01_OPUS_REQUEST_DELEGATION_01.md:4`)。
- 2026-10-27ユーザー正式決定で選定仕様が「AI評価Top1/Top2提示・原則1件・0件可」に変更(`CURRENT_SPEC.md:2110`)。内容仕様(4節)は不変。

### D. SSOT記述の不整合(軽微、実害なし)
- `CURRENT_SPEC.md:2088`「Part 2〜4は別[Trial-07・VALIDATED上限・配線禁止]」および`OPEN_ITEMS.md` OPEN-512(e)「Part 2〜4は別(Trial-07 VALIDATED(限定)・配線禁止)」は、Part 3/4がTrial-07の対象でなく、処遇未決である点を表現していない(Trial-07/08はPart 2のみ、`PART2_TRIAL08_RESULTS_01.md`)。Part 3/4は「Trial-04以降未再評価・採用/不採用未決」が実態。

## 4. ユーザーによる廃止承認の有無と証拠

- **廃止承認=証拠なし。** 検索範囲: `docs/pm/delegation_log/*USER*`(「ニュアンス」「Part 3」「Nuance」)、`USER_DECISION_REGISTER_01.md`(Part 3関連は#182・#185のみ、`:376,382`。#182は「Part 1方針変更の比較Trialへ置換」で判断済み、Part 3の廃止・採用は含まない)、`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`(Part 3の採否記述なし。`DECISION_LOG.md:22364`はTrial-01評価記録のみ)、`ADOPTION_NOTE_04/06.md`(「Part 3・4: Trial-04の判定のまま」)。
- **採用承認=証拠なし**(`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`の記録0)。
- 状況証拠(承認ではない): ユーザーがPart 3の`worthy of`/`worth`出力を「許容範囲」と評価(`2026-10-24_..._USER_02.md:78`)。ユーザーが「ニュアンス解説の品質を重視」と明言(`2026-10-24_..._USER.md:10,126`)。少なくともユーザーがPart 3を否定した記録はなく、むしろ重視していた。

## 5. 現行のどこに相当するか(役割整理)

| 区分 | 役割・内容 | ニュアンス相当の内容 | 根拠 |
|---|---|---|---|
| ① Key Phrase | 詳細な日本語解説(音声あり)、本文は太字+二重下線 | 解説は案α5観点(②と同一Prompt) | `CURRENT_SPEC.md` SYNC-26正式仕様表(3241-3245) |
| ② 追加解説 | ①と同じ詳細な日本語解説(音声なし)、太字+通常下線。Std/Adv共に表示(2026-10-27〜) | 「類義語・近似表現との違い」「比喩的用法」「やや改まった響き」等 | `er003_kp_general_explanation_01.py:49-53`、`CURRENT_SPEC.md:3228-3229` |
| ③ 本文意味表示 | 詳細解説なし、短い日本語訳のみ、通常下線 | なし(設計上) | `CURRENT_SPEC.md:3228` |
| Part 2 文法・構文 | 日本語訳/仕組み/通常表現との比較/**意味・ニュアンス・表現効果**。最大1件・0件可 | **あり(明示節)** | `er120_part2_grammar_production_01.py:135,154,163-164`、`PART2-GRAMMAR-PRODUCTION-WIRING-01_USER.md:31` |
| (Part 3 Nuance & Deeper Understanding) | **存在しない**(Trial専用) | 独立Partとしては**完全に未配線** | §1 |

実例(現行Production出力): X『月は縮んでいる』Part 2に「意味・ニュアンス・表現効果」節(`user_test/family_x_moon_shrinking_reselect_01/index.html:13`)、Y『再配達料』(`user_test/family_y_production_redelivery_fee_01/index.html:1`)、Z『走れメロス』(`user_test/family_z_melos_kphr_evidence_r3/index.html:1`)。Z『告げ口心臓』Part 1にも語感の記述(`user_test/family_z_tell_tale_heart_01/index.html:1`「not stir が『少しの動きも見せない』というニュアンスで使われることがあります」)。
結論: ニュアンス**内容**はPart 1(随時)・Part 2(明示節)に残存。**独立Partとしての「ニュアンス解説」は完全に未配線**(消失ではなく最初から未配線)。

## 6. X/Y/Z・Std/Advへの影響とAI島の実データ

- **Part 3は特定Family固有でなく、全Family・全レベルで未配線**(Trial対象はZ 2作品・X 1作品、Advancedのみ)。Part 1/2の表示はX/Y/Z×Std/Adv全6経路でPRODUCTION_WIRED(`CURRENT_SPEC.md:3234-3235`、Part 2 `:2113`)。Family A/B/Cは対象外(Part 3の起源でもない=事実として記録のみ)。
- **AI島(Std/Adv)実データ**(元run `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/`、公開候補 `user_test/family_x_ai_island_form_01_candidate_b7_01/index.html`):
  - Part 1(V&E): Std 5表現(carry over/take a detour/card to play/worth paying attention to/obstacle、同html:11)、Adv 5表現(carry over/call on/take a detour/card to play/obstacle、同:21)。各「本文中の意味/本文の英文/日本語訳/解説」あり。類義・近似の記述例: Std「`a card up one's sleeve` は、相手にまだ知らせていない切り札という意味合いがより強い表現です」「`challenge` … `obstacle` は進行を妨げるものという意味が中心です」、Adv「`challenge` は取り組むべき難しい課題… `obstacle` には…妨げるものという意味合い」。
  - Part 2(Grammar): Std/Adv共に0件でユーザー確定(`a2/study_text/confirmed_grammar.json` `items:[]` `confirmation_id=cf_aec83b8cbf53df86`、`b1b/...cf_e2fdc0b1f2914fe0`、`grammar_human_review.json` decision `choice=omit` `by=user` `channel=form`)。ユーザー原文: `docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_03.md:9-13`「Standard／Advancedともに文法0件を正式確定」。候補は各2件が提示され、解説全文(意味・ニュアンス・表現効果節を含む)が事前生成されたが(`grammar_explanations.json`)ユーザーが選択しなかった=消失ではない(保存データは未改変)。
  - ページ表示の0件文面は「今回の本文には、このPartで特に取り上げる難所となる構文はありませんでした。」(同html:11,21、出所`er120_part2_grammar_production_01.py:161,1436`。Trial-04由来の固定文)。候補が提示されたうえでユーザーが省略した場合にも同文が出る点は文面の厳密性として改善余地あり(実害なし・新文面は仕様候補)。
  - **判定: AI島の公開データに「承認済み学習仕様の重大欠落」は認められない。**
- Y・Z: 同じ共通module(`er003_kp_general_explanation_01.py`、`er120_part2_grammar_production_01.py`)を使う。Part 3が無い点はX/Y/Z共通。個別差異を示す記録は見つからなかった。

## 7. 必要な是正案とQCD影響(実装はしない)

| 案 | 内容 | QCD | 承認要否 |
|---|---|---|---|
| R-0(推奨・0円) | SSOT記述の訂正のみ: `CURRENT_SPEC.md:2088`・OPEN-512(e)の「Part 2〜4は別」を「Part 3/4=Trial-04以降未再評価・採用未決(処遇記録なし)」へ。Part 3の処遇をOPEN化(分類=ユーザー判断要) | Q±0 / D±0 / C 0 / 費用0 | 記録訂正(承認済み仕様の変更でない)。Fable判定 |
| R-1(要ユーザー判断) | Part 3(ニュアンス解説)をProduction仕様として採用するか、見送りか、Trial再開かを決める | 採用時: C +約0.10〜0.14円/set(`DESIGN_04.md:62`、70円の約0.2%)、D +並列なら実質0〜数秒。Q: Trial-01〜04でFable評価は「Part 3は揺れ・弱」(`FABLE_EVAL_01.md:8`、`EVAL_02.md:40`)。事前にPrompt改善版Trial(UDR #182のA案相当、約1円)とOpus条件A(新構造)が必要 | **要。新仕様**(Production仕様の追加) |
| R-2(要ユーザー判断・R-1の軽量代替) | Part 1の観点(`er003_kp_general_explanation_01.py:49-53`)へ「語感・ニュアンス」を明示追加 | Production Prompt直接編集=承認済み案αの変更。C ほぼ0、Q影響は要Trial | **要**(承認済み仕様の変更) |
| R-3 | AI島Part 2 0件文面の厳密化 | 新文面=仕様候補 | 不要と判断(実害なし) |

AI島: 追加作業なし。そのまま公開可。承認済み内容は変更しない。

## 8. ユーザー判断が必要な事項(`判断候補`、USER_DECISION_REQUIREDのラベルはFable付与)

1. **判断候補(分類D=真に新しい判断)** Part 3「Nuance & Deeper Understanding」の扱い: (a)Production採用を目指してPrompt改善版Trialを再開、(b)見送りを正式決定(SSOTに廃止として記録)、(c)保留継続。
   - 挙証: 既判断(分類A)は存在しない=廃止承認なし・採用承認なし(§4)。`2026-10-24_..._USER.md:10`でユーザーは当該品質を重視。Trial評価は弱(`FABLE_EVAL_01.md:8`)で、改善は未実施。停止根拠: 新仕様=Production追加は人間判断事項(CLAUDE.md共通Charter「人間に判断を求めるのは主に次」・PM_GOVERNANCE 11-1)。独断採用不可。
   - 現タスクとの関係=独立(分類C)。AI島公開を止める理由にはならない。
2. **判断候補(分類D、任意)** Part 1の観点にニュアンスを明示追加するか(R-2)。1.の(a)と統合して判断可能。
- 判断不要(分類B/C): SSOT記述訂正(R-0)、AI島の公開(重大欠落なし)。

## 付録: 調査実施範囲
`git log --all -S"ニュアンス"`(189 commit。大半は無関係な「ニュアンス」語)、`-S"ニュアンス解説"`(3 commit)、`-S"Nuance & Deeper"`(6 commit、全てdocs/research Trial)、`git grep`で`*.py`/`*.html`/SSOT 6種/delegation_log/USER_DECISION_REGISTER/research/Trialを検索。AI島は`confirmed_grammar.json`・`grammar_human_review.json`・`grammar_explanations.json`・公開候補htmlを直接確認。API呼出0、費用0円。
