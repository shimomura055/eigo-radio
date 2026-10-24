# HISTORY_REPORT_01: Key Phrase日本語意味の字義訳問題(`draw a line`→「線を引く」に代表)の経緯・現状の再報告

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_34 / 作成日 2026-10-24 / Read-only調査のみ(API 0・Trial 0・Prompt/仕様/Productionコード変更 0)。
根拠ユーザー原文: `docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_09.md`(注: 委任文が指定した`_USER_08.md`は既にUDR #178承認原文で使用済みのため`_USER_09.md`に保存)。
出典表記: 「OI」=`OPEN_ITEMS.md`(OPEN-474は989行)、「UDR」=`docs/pm/USER_DECISION_REGISTER_01.md`、「RC4」=本フォルダ`ROOT_CAUSE_04.md`、「TR06」=`TRIAL_06/TRIAL_RESULT_06.md`。**不明は推測せず「未確認」と書く。**

> **最重要の区別**: 「日本語意味(gloss)を自然にする仕組み」はProductionに**ある**が、`draw a line`型の**字義訳を防ぐ・直す仕組みはProductionに無い**。字義訳対策(X2p')は検証(Trial)済みだがユーザー未採否(UDR #179)で、Productionには**一行も入っていない**。

---

## 1. 結論: 現在どう決着しているか

| 論点 | 現状 | 区分(承認/実装/runtime) |
|---|---|---|
| 字義訳問題(課題①)は解決したか | **未解決**。Productionの意味生成は問題発見時と同じ作りのまま | 承認なし・実装なし |
| 字義訳への対策案(X2p') | Trialで「新難例9KPで字義訳 1→0、過剰解釈0」を確認。ただし通常KPで「正しいが弱い訳」が増える(厳しい側7/54)ためFableはVALIDATEDを宣言せず、**ユーザー判断待ち(UDR #179、未回答)** | 承認なし・実装なし(DEV専用コードのみ)・Production runtimeなし |
| 一般的な日本語gloss自然化(gloss再整合段) | Production既定ONで稼働(`APPROVED_FOR_PRODUCTION`)。ただし役割は「見出し語と日本語意味の語の欠落・人称の不整合を直す」ことで、**字義訳の検査は含まない** | 承認済み・実装済み(字義訳は防げない) |
| 見出し語の一般化(`draw that line`→`draw a line`。A-1・所有格一般化=課題②) | X/Z=`PRODUCTION_WIRED`(2026-10-24 Fable受入)。Y=未配線(OPEN-484) | 承認済み・実装済み・runtime evidenceあり |
| `draw a line`自体 | 見出し語は`draw a line`に直った。日本語意味は「一線を引く」になる例がある一方、現行Promptでは「線を引く」(字義訳)も出る確率的な状態(§5)。**確実に直ったとは言えない** | 未解決(確率的) |

---

## 2. 問題発見から現在までの時系列

### ① 問題の発端
- 発見: 2026-10-23、Family X新規記事B「英国の電車マナー」(slug `uk_train_speaker_playback`、タイトル『その動画、車内で勝手にプレミア上映していませんか』)の試聴レビュー(UDR #166、記事Bは最終承認保留)で、ユーザーがKey Phraseの品質を指摘 [出典: `docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER.md`、OI OPEN-467 品質未解決事項、UDR #166]。
- 実際の出力: KP `draw that line`、Std日本語意味「その線を引く」、Adv英語説明 `to decide where the limit is between what is acceptable and what is not` [USER.md §1]。本文は「The words draw that line simply」(許容できる/できないの区別をはっきり示す意味) [TRIAL_02/GOLD_LABELS_FINAL_01.md: draw a line行]。
- 適切な訳: ユーザー例は「境界線を設ける」(KP=`draw a line`、Adv=`to establish a clear boundary or limit`) [USER.md §1]。Fableが確定した評価用の正解範囲(gold)は、許容=「一線を引く/区別をはっきりさせる/線引きをする/境界をはっきりさせる」、不可=「線を引く/境界線を引く」(描く動作の字義訳) [GOLD_LABELS_FINAL_01.md「Fable確定」節]。
  - 注意(事実): ユーザー期待の「境界線を設ける」と、goldの不可「境界線を引く」は文字が近いが別表現。goldに「境界線を設ける」の明記は無い(未確認: goldとの突合せ判定は未実施)。
- 単発か複数か(複数。ただし「字義訳」と確定した件数は少数で、特定の型に集中):
  - 最初の指摘は`draw that line`1件。この指摘は、見出し語の一般化不足・Adv説明の文脈引きずり・Std逐語の**3点セット**で、字義訳はその一部 [USER.md §1-3]。
  - 初期調査(RC1)の現行path 78KP集計: 逐語gloss(確定)4件(5.1%)=`reach for one's wallet`・`shine a light on`・`draw that line`×2 [ROOT_CAUSE_01.md l.105]。**後に訂正**: `reach for someone's wallet`は見出し語の人称placeholder問題で字義訳NGではない、`shine a light on`は「光を当てる」が比喩として同じ意味で通じるため字義訳に数えない [RC4冒頭、GOLD_LABELS_FINAL_01.md]。
  - ユーザー判断(2026-10-23): `reach for someone's wallet`→「他人の財布に手を伸ばす」は、見出し語どおりなら**問題ない**(本文でどうかは関係ないでしょ、という趣旨) [`..._USER_05.md`]。これを受け同件・`apply one's findings`は字義訳集計から外し別課題(課題②)へ [RC4冒頭]。
  - 確定した字義訳NGの型(RC4): `an unseen clock`→「目に見えない時計」、`question shaped like a trophy`→「トロフィーの形をした質問」、`greener grass`→「より青く見える芝生」、`draw a line`→「線を引く」の**4KP**。現行Prompt(G0/B0)出力で字義訳 8/11(73%)[`draw a line`のみ確率的で2/5、他3KPは各2/2] [RC4 §0。注: この4KPは字義訳が出たために選ばれた事後層別で、率は過大(RC4 l.99)]。
  - Trial_05(2026-10-24)のhard-core 4KP×3rep=12出力では、現行(B0)で10/12が字義訳NG/FAIL系 [OI OPEN-474委任_25〜29、TRIAL_05/TRIAL_RESULT_05.md §C]。`draw a line`のB0 3rep: 「一線を引く」(PASS)/「線を引く」(字義)/「線を引く」(字義) [TRIAL_05/report_05_fable_labels_05_withcde.md l.49-51、TRIAL_RESULT_05.md l.32]。
  - 新造比喩の追加事例(Trial_06、新難例9KP): 現行(B0p)では`feel like friction`→「摩擦のように感じる」が字義訳1件(+THIN 2件) [TR06 §2-2]。

### ② 原因究明(RC1→RC2→RC3→RC4)
**主因(RC4・OPUS_REVIEW_07反映後の改訂、2026-10-24)**: 日本語意味(gloss)を作る呼出に、**「その表現が本文でどういう意味か」を確定する段が無い**。翻訳モードで日本語を直接1本書く形のため、辞書に載らない新造比喩や、ことわざの断片では、直訳が「指示どおりの出力」になる [RC4 §0-R]。
- 増悪因子(未検証): gloss Promptの文脈限定句「key_phrase単体で他の文脈でも再利用できる自然な訳にし、本文固有の固有名詞・文脈の追加はしない」(`er003_key_words_gloss_alignment.py:620`)と、新規生成規則「source_sentenceは語義選択のためだけに使う」(同:332-346のNEW_GENERATION_TEXT)。ただし、この句を残したまま字義訳が消えたarmがあり(Cp: hard-core 0/4)、**必要条件ではない**と判断 [RC4 §0-R]。
- 型: 「具体名詞を含み、字義どおり読んでも文法が通り、直訳した日本語では比喩の意味が運ばれない、新造または断片化した比喩」。辞書にある完全な慣用で日本語にも同種の比喩があるもの(光を当てる等)は現行でも字義訳0 [RC4 l.157]。
- 発生の上流: KP選定は表現と語数しか出力せず意味・用法を持たない(`er105`のSELECTOR_JSON_SCHEMA)。選定規則が再利用しにくい新造比喩を選び、慣用を断片化する(`greener grass`は選定が`greener`1語に縮約) [RC4 §0-R・§2-2]。canonicalization段は「比喩的な意味」を認識している例があるのにgloss段へ渡さない(reasoningに比喩・慣用を述べる項目は260 unique中36=13.8%) [RC4 l.68]。
- 「確率的」か: 当初の「LLMが確率的に選ぶ」は誤りで、特定の型に集中する**高確率の失敗**。ただしPromptの揺れにも敏感で、各KP2rep程度ではp=0.7とp=1.0の区別はつかない [RC4 §0-R 性質の表現]。

**なぜ既存のPrompt・Validator・QAが防げなかったか**(事実):
1. 承認済みgloss再整合段(`er003_key_words_gloss_alignment.py`)の検査項目は、gloss空・括弧/算用数字/…/音声化禁止記号・current_gloss_consistentの真偽矛盾・追加内容語のspan対応(mapping gate)・人称語の不整合・`qa_reflects_all_key_phrase_words` PASSである [同ファイルvalidate_item_corrected l.629-690]。**字義/慣用を判定するコードは無い**(同ファイルを「字義」「literal」でGrep: 0件)。
2. Prompt側には、むしろ字義寄りの訳を手本にする判定例がある。「key_phrase『fall into』にcurrent『～に落ちる』: 意味は表れているので一致です」(同:618付近)。字義訳との因果は未検証 [RC4 0-R few-shot行]。
3. 「再利用できる訳」句が、文脈で意味が決まる比喩に対して文脈を使わない辞書訳を出させる(増悪因子、未検証) [同:620]。
4. 「全体の1〜3%がランダムに外れる」という薄まった率や、副作用指標で評価されたため、過去のPrompt言い換えTrialは「効かない」と見えた。言い回しだけを変えたarm(G1・M)は効かず、**処理を変えたarm(G2・G3・Cp・C)は対象KPで効いていた** [RC4 §0 No.5]。

**過去Trialの結果要約**(いずれもDEV専用・Production変更0):
| Trial | 日付 | 内容と結果 | 出典 |
|---|---|---|---|
| Trial_01/02 | 2026-10-23 | A-1(`this/that→a/an`等)で`draw that line`→`draw a line` 6/6。A-3 v3(Adv説明Prompt)は効果が統計的に未確認。G3(定訳優先)は難例合格96%対現行85%、`draw a line`はG3 3/3慣用義(現行は字義2/3)。実費69.0+68.98円 | OI OPEN-474委任_02/07 |
| A-3追加検証 | 2026-10-23 | 改善7/悪化6/維持22/判断分かれ3、総合PASS 72→73%(差なし)。8.04円 | A3_VERIFICATION_01.md |
| Trial_03 | 2026-10-23 | Fable盲検(各120出力)でStd確定FAIL G0=3(+境界1)/G2=1/G3=2、誤り率は全armで1〜3%同等域。`draw a line`合算字義NG G0 2/5・G2 1/5・G3 0/5。G0の誤りは「比喩の字義訳」型。30.12円 | TRIAL_03/FABLE_BLIND_RESULT_03.md |
| Trial_04 | 2026-10-23 | 方式C(独立検査+flag項目のみ再生成): 字義NG 6→1/122、検出19件中14件は修正不要(誤検知)、`question shaped like a trophy`型が未修復。費用+0.2〜0.25円/記事 | TRIAL_04/FABLE_JUDGMENT_04.md、USER_07 §2-1 |
| Trial_05 | 2026-10-24 | 意味確定段付き生成X2/X2p。R hard-core B0 10/12 FAIL系→X2p 0/12、held-out悪化0、Stage 2(通常54KP)でstrict PASS→FAIL 0・PASS→THIN 2。累計17.401円 | TRIAL_05/TRIAL_RESULT_05.md |
| Trial_06(補強) | 2026-10-24 | 本番構成・新難例9KP・Stage 2再検証(UDR #178承認)。102 call・19.306円。結果はTR06のとおり(§5-3) | TR06 |

---

## 3. 承認済み対策とユーザー判断(提案→採否)

| # | 提案/対策 | 判断(ユーザー) | 日付 | 根拠記録 |
|---|---|---|---|---|
| 1 | A-1(参照語の不定化: this/that→a/an、him/her/me/us→someone) | **採用(`APPROVED_FOR_PRODUCTION`)**。X/Z共通で配線 | 2026-10-23 | UDR #169、`..._USER_02.md` §1-2 |
| 2 | A-3 v3(Adv英語説明Promptの変更) | **不採用**(手段の不採用であり、改善タスク自体は終了せず継続) | 2026-10-23 | `..._USER_03.md` §1、OI OPEN-474 |
| 3 | G3(Std gloss 定訳優先の新規生成Prompt)の採用(UDR #171) | **保留→採用せず**(原因精査後に別途。USER_06で「G3など未承認の新仕様はProduction採用しない」) | 2026-10-23 | UDR #171、`..._USER_06.md` §3 |
| 4 | 検査方式C(独立再読検査+該当itemだけ再生成) | **現段階でProduction採用しない**(検出19件中14件が修正不要で誤検知・再生成・運用負荷が大)。ただし字義訳解決は諦めない | 2026-10-24 | `..._USER_07.md` §2-1 |
| 5 | OPEN-476(`bound→bind` INVALID既存defect) | 保留(DEFERRED、Open Item維持) | 2026-10-23 | UDR #169、`..._USER_02.md` §1 |
| 6 | 課題②(所有格一般化 `possessor_roles`+付帯(a)〜(f)) | **採用(`APPROVED_FOR_PRODUCTION`)**。X/Y/Z共通Production Wiring | 2026-10-24 | UDR #173②、`..._USER_07.md` §1 |
| 7 | 課題①の原因究明やり直しと根本対策Trial(正しい意味を最初から生成する方向、追加検査は必要性が説明できる場合のみ) | 継続を指示(未承認仕様のProduction Wiringは許可せず、到達上限=VALIDATED) | 2026-10-23/24 | `..._USER_06.md`、`..._USER_07.md` §2 |
| 8 | 補強Trial(X2p') | **承認**。KP案件累計上限300→500円、想定20〜21円・retry込み約28円、到達上限=VALIDATED | 2026-10-24 | UDR #178、`..._USER_08.md` |
| 9 | **X2p'をProduction採用候補に確定するか** | **未回答(USER_DECISION_REQUIRED)** | - | UDR #179(§6) |
| (内部) | Opus独立レビュー | OPUS_REVIEW_07: 主因を「意味確定段の欠如」に訂正。OPUS_REVIEW_08(条件C): 「採用提案の前に追加検証が必要」→補強Trialへ | 2026-10-24 | OPUS_REVIEW_07/08.md、DECISION_LOG.md:20 |

**一般的なgloss自然化対策との関係(事実)**:
- 承認済み: 「KP gloss再整合(修正版corrected)」(UDR #60、2026-10-15 `APPROVED_FOR_PRODUCTION`)。内容は、最終英語KPが表示候補より語を足したitemに対し日本語意味を全語反映に直す、人称一般化したitemで「あなた/彼」等を残さない(`person_reference_mismatch`)、全文選定itemではglossの新規生成も担う [CURRENT_SPEC.md:1633, 2794、er003_key_words_gloss_alignment.py:141-160, 270-346]。既定ON(kill switch=`EIGO_KP_GLOSS_ALIGNMENT=0`のみ、実質はgloss生成停止=本番停止)。
- ただし**この段の「意味の作り方」自体が字義訳を生む側**で、字義訳を検査・修正する機能は無い(§2)。ゆえに「gloss自然化がある」ことは字義訳の解決を意味しない。
- 委任_20のG1/G1'(`er003_key_words_gloss_alignment.py:242-243`)は、A-1・所有格一般化で変わった見出し語(him→someone、my→someone's等)と日本語意味の**人称対応表**の拡張であり、字義訳対策ではない。

---

## 4. 現在のProduction実装状況

### 4-1. 字義訳対策(X2p')
- **未配線・DEV専用**。Production moduleに該当コードなし: `meaning_in_text_en`等のX2p'欄の語を、`er112_kp_gm_*`以外のProduction対象`er*.py`でGrep: 0件。DEV harness(`er112_kp_gm_trial_05.py`・`_06.py`)はProductionからimportされない(import Grep: 0件)。Production moduleはTrial前後のhash一致(`TRIAL_06/production_hash_start.txt`=`_end.txt`、TR06 §1)。
- 状態: VALIDATED未宣言/REJECTEDでもない(TR06 §4)。配線設計案(`WIRING_DESIGN_07.md`、**未承認・実装なし**)は単一commit・`git revert`撤退。flagは新設しない設計(`EIGO_KP_GLOSS_ALIGNMENT`のOFFは「元に戻る手段」ではなく本番停止になるため。WIRING_DESIGN_07 §6)。
- 採用すると変わる原則: gloss設計原則「単体で再利用できる訳」→「本文での意味」への変更はユーザー承認事項(OI OPEN-474委任_29)。

### 4-2. 承認済みで配線済みの対策(字義訳対策ではない点に注意)
| 対策 | 承認 | X | Z | Y | 出典 |
|---|---|---|---|---|---|
| A-1(参照語の不定化)+課題②(所有格one's/someone's一般化) | UDR #169/#173 | **PRODUCTION_WIRED**(2026-10-24 Fable受入、委任_31) | **PRODUCTION_WIRED** | **未配線**: Y専用の正式Production入口が無く、DEV/Trial scaffoldが同じ共通moduleを呼ぶだけ。`PRODUCTION_WIRED`と呼ばない(OPEN-484。Y Production化時の必須受入条件(a)〜(f)登録済み) | OI OPEN-474/484、CURRENT_SPEC.md:1972 |
| KP gloss再整合(corrected) | UDR #60 | 既定ON | 既定ON | 共通module(Y正式経路は未存在) | CURRENT_SPEC.md:2794 |
| 字義訳対策(X2p')/検査方式C/G3/A-3 v3 | 未承認/不採用 | なし | なし | なし | §3 |

### 4-3. 経路ごとの適用(A-1・課題②の事実。字義訳対策は全経路で非適用)
- 正式初回経路: X=`er019_family_x_audio_production_runner_01.py:441 sc.run_key_phrases` → `er003_v1_n3_01_scaffold_generate.py`の`run_kp_with_outer_retry`→`run_key_phrase_canonicalization`、Z=`er062_family_z_writer_01.py:1289 run_kp_stage`→同関数。canonicalization gate呼出は1箇所で、初回・再利用・`--regenerate-stage kp_*`・外側retry(最大3)・resumeはいずれも同関数を通る [PROD_WIRING_EVIDENCE_07.md l.17-19]。
- gloss再整合段は`sc`内でcanonicalization後に呼ばれ、item単位retry上限2、2回失敗はHuman Review(KPは維持、完成禁止の保証はX/Zのみ)[CURRENT_SPEC.md:2794、er003_v1_n3_01_scaffold_generate.py:525-545]。
- **KP段が再実行される経路**: Z=`--stage kp --regenerate-stage kp_a2/kp_b1b`等、X=`--stage`/`--scaffold-only kp`再実行 [PROD_WIRING_EVIDENCE_07.md l.17-19、CURRENT_SPEC.md:2794のE11d]。既存完成記事は自動再生成されない(KP段を再実行したときだけ新規則が反映) [UDR #173付帯(f)]。
- A/B/C旧ラインは非適用(`fulltext_source_ref`なしのitemは新経路に入らない) [PROD_WIRING_EVIDENCE_07、WIRING_DESIGN_07 §7]。
- Validator/自動修正: A-1・課題②は決定論後処理(revertのみ)とvalidatorあり。**字義訳専用のValidator・自動修正はProductionに無い**。

### 4-4. runtime evidenceとRegression
- A-1・課題②: runtime evidence取得済み(P-T2 35unit WRONG 0/44、X/Z正式KP段で発火、実費13.79円、新規TTS 0) [OI OPEN-474委任_20、PROD_WIRING_EVIDENCE_07.md]。全回帰(委任_20時点)collected=7061 passed=7045 failed=6、自分起因0、他agent起因/state変動6件。委任_24〜27でOpus条件C必須修正W-02/W-03を是正し、replay変化0 [OI OPEN-474委任_27、PROD_WIRING_EVIDENCE_08/09.md]。
- 字義訳対策: Production runtime evidence **なし**(未配線のため存在しない)。Trial_06のDEV実測のみ(§5-3)。
- 実記事での確認: `draw that line`→`draw a line`(A-1発火)、Std gloss「一線を引く」(ALIGNED)の1サンプルあり [PROD_WIRING_EVIDENCE_07.md l.40](X・uk_train記事の`--scaffold-only kp`実行)。**これは1サンプル**で、字義訳が出ない保証ではない。
- **記事Bの成果物の再生成・最終承認: 未確認(本調査では「実施した」記録を確認できず)**。OPEN-467は「KP修正→最終版試聴ページ再提出」を前提に最終承認保留とされたまま [OI OPEN-467]。

---

## 5. 未解決の問題・品質リスク

### 5-1. `draw a line`自体は解決済みか → **未解決(確率的)**
- 見出し語: 解決(A-1で`draw that line`→`draw a line` 6/6、Production runtimeでも発火)。
- 日本語意味(現行Production相当B0): Trial_05の3repで「一線を引く」/「線を引く」(字義)/「線を引く」(字義)=字義2/3、Trial_02+03合算(G0)で字義2/5 [§2]。**確率的に字義訳が出る**。
- X2p'(未採用)の`draw a line`: Trial_05で「はっきりと区別する」「違いをはっきり示す」「区別をはっきりさせる」(PASS×3)。Trial_06でも「線引きをする」(PASS)。
  - 訂正(報告済み内容との差分): 委任文には「Trial_06 B0p出力『線引きをする』」とあるが、`blind_06b_key.json`で確認すると「線引きをする」は**X2pp(X2p')のrep1の出力**であり、B0pの出力ではない。Trial_06のR集合(元難例7出力)はX2ppのみ実行でB0pは未実行 [TRIAL_06/blind_06b_key.json 行2、METRICS_06.md l.22]。

### 5-2. 再発可能性
- 比喩・慣用として認識されたKP: 全体13.1%(36/274 unique、Production run限定 11.1%)、Xで15.4%(35/228)、Zで2.2%(1/46)。分母は選択的標本 [ADOPTION_PROPOSAL_02.md l.34]。
- 字義訳NGが確認された型: 評価集合115KP中4(3.5%)、重複排除census 142KP中3(2.1%) [同l.36]。1記事セット(約10KP)あたり約0.2〜0.35KP(確認型基準)〜1.3KP(上限13.1%基準) [同l.38]。
- 結論(事実のみ): 現行のままでは、**今後も同じ型(新造比喩・断片化した慣用)で字義訳は発生しうる**。発生率は上記の幅で、正確な実率は未確認。

### 5-3. 採用時の副作用(X2p'のトレードオフ、TR06)
- 改善: 新難例9KPで字義訳(FAIL系) B0p 1→X2pp 0、Stage 2のPASS→FAIL系 0、過剰解釈(字義が正解のKPを比喩化) 0。
- 悪化: 通常54KPでPASS→THIN(意味は誤りでないが弱い・説明調・対象の持ち込み)が厳しい側7件(Fable単独2件)。R集合に継承FAIL_LIT 1(『賞の形をした問いかけ』、今回のFableはTHIN、OpusはPASS)。
- 事前基準を全ては満たさないため、Fableは**VALIDATEDを宣言せず、REJECTEDとも判定せず**、品質トレードオフ(意味の誤りの解消 対 通常KPでの弱い訳の微増)としてUSER_DECISION_REQUIREDとした。
- 費用/時間: +0.438円/記事セット(70円目標の約0.63%)、level当たり+25.8s。KP案件累計314.74円/500円 [TR06 §2-5, §7]。
- 他のFamily: Zは比喩KP発生率2.2%で利益が小さく(TR06 §5)、Yは共通KP段に依存しOPEN-484と同時配線になる(実装なし)。

### 5-4. 関連OPEN/UDRと現在のStatus
| ID | 内容 | Status |
|---|---|---|
| OPEN-474 | 本件の親(KP一般化・意味の包括対策) | ②=PRODUCTION_WIRED(X/Z)。①=Trial_06完了、USER_DECISION_REQUIRED(UDR #179待ち) |
| UDR #169 | A-1/A-3 | 判断済み(A-1採用・A-3不採用) |
| UDR #171 | G3採否 | 保留→G3採用なし |
| UDR #173 | ②採用と①方針 | ②判断済み(採用)、①は再調査後に#178/#179へ |
| UDR #178 | 補強Trial費用(上限300→500円) | 判断済み(承認) |
| **UDR #179** | **X2p'(意味確定段付きgloss生成)の採否** | **未回答(非blocking)** |
| OPEN-467 | 記事B(`draw that line`のKP)最終承認 | 最終承認保留(KP修正と試聴再提出待ち) |
| OPEN-476 | `bound→bind` INVALID | DEFERRED |
| OPEN-481 | non_person_agent分割 | 候補・未着手・未承認 |
| OPEN-484 | Y未配線(必須受入条件) | 未配線・非blocking |
| OPEN-475 | Key Phraseのタイトルケース残り(表示のみ) | 記録のみ |

OPEN登録の分類(27-3/11-8): 本件で新規OPENは登録していない(Read-only調査)。

---

## 6. 必要なユーザー判断と推奨方針

**判断が必要なのは UDR #179 のみ**(字義訳対策の採否)。

| 選択肢 | 内容 | 影響 |
|---|---|---|
| A-1 | X2p'を採用候補に確定→Production採用の正式判断へ。X/Z共通 | Zは利益が小さく副作用のみ残る可能性(仮説)。配線はユーザー承認後 |
| A-2 | 同上、Xのみ | Zは現行維持 |
| B | 説明調・持ち込みを抑える規則を1回追加して再検証(約20円。KP累計約335円/500円) | 改善見込み中。採否判断が遅れる |
| C | 現行維持(REJECTED) | 字義訳は残る(§5-2の発生率)。追加費用0 |
- Fable推奨は**A**(A-1/A-2の別はUDR #179本文のとおり)。理由: 学習者に誤った意味を教える字義訳を本番構成で0にでき、悪化は「正しいが弱い訳」に限られ単価増0.6%。弱い訳は配線後の監視と定訳辞書で漸減できる(UDR #179。Fable推奨は記録のみ、採否はユーザー)。
- 採用前提の確認(承認事項): gloss設計原則「単体で再利用できる訳」→「本文での意味」への変更。X2p'は検査追加ではなく既存callの出力構造変更で、通常の新規生成の追加LLM callは0(混在batchのみ+1) [WIRING_DESIGN_07 §1]。
- Production採用は人間ユーザーのみ。VALIDATED止まりで自動配線しない(USER_08・USER_07 §2-5)。

---

## 7. 報告済み内容からの差分(直近=本日のTrial_06 Closeout報告[UDR #179起票、委任_33]との差)
1. 委任文の「B0p出力『線引きをする』」は**誤り**。`blind_06b_key.json`行2では「線引きをする」はX2pp/rep1。Trial_06のRセットはX2ppのみ実行。
2. 「G1/G1'」は字義訳対策ではなく、A-1・所有格一般化に伴う人称対応表の拡張(`er003_key_words_gloss_alignment.py:242-243`)。
3. 追加の事実確認: gloss再整合段のコードに字義/literal判定は無い(Grep 0件)。Productionに`meaning_in_text_en`は無い。
4. 本調査での新規の未確認: 記事Bの最終版再生成・再提出の実施有無、goldと「境界線を設ける」の突合せ。
5. 上記以外にUDR #179・Status・金額の変更はない(KP累計314.74円/500円、Production変更0のまま)。
6. 保存ファイル名: 委任文指定の`_USER_08.md`は既存(UDR #178原文)のため、本依頼の原文は`_USER_09.md`。

---

## 8. 未確認事項の一覧
1. 記事B(`uk_train_speaker_playback`)のKP修正版の再生成・音声・ページ再提出の実施有無(OPEN-467は保留記載のまま)。
2. ユーザー期待訳「境界線を設ける」を、goldの許容/不可のどちらとして扱うか(goldに明記なし)。
3. 字義訳の本番での実発生率(census 2.1〜13.1%の幅は選択的標本由来)。
4. A-1のOpus必須修正W-01〜04本文の照合結果(OPUS_REVIEW_A1_CONDC_01)の内容は本調査では再照合していない。
5. Y正式Production入口完成後のKP段の挙動(未存在のため未確認)。
6. `draw a line`が字義訳になる実Production確率(Trial値は2/3、2/5。本番構成での測定なし)。
