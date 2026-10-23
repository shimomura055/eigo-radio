# TRIAL_RESULT_04: 2課題(①Std字義訳 / ②見出し語の人称placeholder)の改善Trial結果(委任_14、DEV専用・Production変更0・未承認仕様の配線なし)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_14 / 設計=`DESIGN_06.md` / 配線案=`WIRING_DESIGN_04.md` / 較正=`TRIAL_04/PHASE0_CALIBRATION_01.md` / 費用=`TRIAL_04/BUDGET_LOG_01.md`
使用モデル: 生成・検査・canonicalization・gloss再生成・Adv説明=luna(本番ラインと同一)、参考Judge=`claude-sonnet-5-5`(最新世代の推奨系)。判定の主体=確定gold+**Fable盲検**(盲検表`TRIAL_04/fable_blind_04.md`+`fable_blind_04_key.json`)。**本書の①の数値はFable未判定の段階のため、Sonnet参考Judge+既存Fable確定ラベルによる暫定値**。②は決定論スコア(目視goldとの突合、API 0)でJudge不要。
実施日: 2026-10-23。費用 56.57円/上限60円(うちPhase 0 7.0円=計画超過、Judge 10.0円=想定超過)。

## 0. 結論(先頭)
- **② 見出し語の人称placeholder: 改善を確認(VALIDATED候補)。** 所有格を含む目視gold付き項目42件で、現行(+A-1)の誤り(自分/別の人/物の取り違え)**9件(21%)→本案0件**。INVALID/REVIEW_REQUIRED 3→1。追加call 0。ただし (a)1 repのみ・合成unit(型網羅)を含む、(b)効果の源泉は『role先行判定』であり決定論修復の発火は0、(c)正しい一般化2件(`pump one's fist`、擬人化された財布の`its`)がroleのnon_person誤判定で無変更へ後退(許容形だが一般化を喪失)。
- **① Stdの字義訳: 部分的改善。「解消」とは言えない。** 独立検査+flag項目のみ再生成(C)は、既知字義NG(an unseen clock 2出力)を2/2検出し字義NG(FAIL_LIT) 2→0にしたが、再生成後も『目に見えない時間の流れ』と像寄りに留まる(暫定でTHIN)。検査のprecisionが低く(flag 19/122出力=15.6%、字義NGは2)、flag項目内の悪化が出る(暫定で3/19)。自己監査(C')は検出力0、生成message変更(M)は効果なし。追加費用は約0.2〜0.25円/記事で事前宣言の0.15円を超える。
- 2課題とも**Closeせず継続**(USER_06)。②は採用提案へ進める段階、①は方式の追加検討(§6の次の一手)が必要。

## 1. 各課題の根本原因(`ROOT_CAUSE_03.md`、本Trialで裏づけられた点)
- ②: canonicalization段に『所有格が誰を指すか』の判定工程・規定がなく、one's/someone's/無変更の選択が確率的に決まる(許可表も語->許可集合のみで指示対象を見ない)。**Trialの裏づけ**: roleを先に判定させるだけで、現行の誤り9件が0件になった(table/validator側の修復は不要だった)=原因は『判定の欠落』で、LLMに易しい判定を先に書かせれば解ける種類。
- ①: 『字義読みも文法的に成立する比喩・慣用』でモデルが語彙既定を確率的に選ぶ点と、出力後に誰も見ていない点。**Trialの裏づけ/修正**: (a)生成messageの再整合用の指示を除く(M)だけでは減らない=『再整合用Promptが字義訳を誘発する』仮説(OF-06)はこのTrialでは支持されず(字義NG出力 B0 2/4→M 3/4、出力の62%が変化)。(b)同一callの自己監査(C')は『自分のglossは常にsame_meaning』と答え検出力0=確証バイアスが強い。(c)独立した第2の読み(C)は検出できるが、precisionが低い。

## 2. 対策内容と仕組み
- ②(推奨): `possessor_roles`(display内の所有格1個ごとの{token,role})を`key_phrase`より**先に**出させ、決定論の後処理で個数・token・enumを検証し、roleと見出し語の食い違いを1トークン置換で修復。置換しない選択は常に許可、non_person/noneの置換はdisplayへrevert。再帰代名詞は決定論でself。追加call 0。
- ①(暫定推奨): gloss新規生成直後に独立検査(luna、effort low、8項目/call)→flag(figurative AND literal_image_only)項目だけを既存の`previous_attempt_rejected`機構でattempt 2として再生成。未flag項目はバイト同一。検査失敗はスキップ(fail-open)。
- 手段と目的の区別: 目的=『本文の用法に合った一般的な意味が出る』『見出し語が本文の指示対象と整合する』。検査・role・再生成は手段で、目的の達成は(②は達成、①は未達)を成果物の中身で判断した。

## 3. Before/After(具体例)

### ② 見出し語(目視gold付き42件のうち、変化した全11件[pump系2件は1行にまとめた]。C0A=現行+A-1 / C1A=本案、rep1)
| display | gold(role) | C0A(現行+A-1) | C1A(本案) | 判定 |
|---|---|---|---|---|
| make something your whole life | self | make something **someone's** whole life | make something **one's** whole life | 誤り->正 |
| occupy their thoughts | self | occupy **someone's** thoughts | occupy **one's** thoughts | 誤り->正 |
| take my place | other_person | take **one's** place | take **someone's** place | 誤り->正 |
| apply its findings | non_person | apply **one's** findings | apply **its** findings | 誤り->許容(無変更) |
| compete through its presence | non_person | compete through **one's** presence | compete through **its** presence | 誤り->許容 |
| enforce their rules | non_person | enforce **someone's** rules | enforce **their** rules | 誤り->許容 |
| find its way back | non_person | find **one's** way back | find **its** way back | 誤り->許容 |
| keeps its promise | non_person | keep **one's** promise | keep **its** promise | 誤り->許容 |
| questioned its methods | non_person | question **one's** methods | question **its** methods | 誤り->許容 |
| pumps its fist / pump its fist(2件) | self(擬人化された財布) | pump **one's** fist | pump **its** fist | 正->許容(後退。roleをnon_personと誤判定) |
- 不変: 正しい一般化26件+許容(無変更)5件。

### ① gloss(flagされ再生成された19出力のうち主なもの。ラベルはSonnet参考+Fable既存確定、**Fable最終判定待ち**)
| KP | Before(B0) | After(C) | 暫定 |
|---|---|---|---|
| an unseen clock | 目に見えない時計(Fable FAIL字義) | 目に見えない時間の流れ / 見えない時間の流れ | FAIL_LIT->THIN(像寄り残存) |
| greener grass | より青々とした芝生 | 自分のものよりよく見える他人の暮らし | FAIL->PASS |
| grow lighter | 軽くなる | 胸の重苦しさが和らぐ | PASS->PASS(より明確) |
| on paper | 書面上では | 理屈の上では | PASS->PASS(用法に近づく) |
| take off an AI costume | AIの衣装を脱ぐ / AIの着ぐるみを脱ぐ | AIのふりをやめる / AIのふりをやめて、人間の姿を現す | PASS->PASS / **PASS->FAIL(rep2、文脈追加)** |
| behind the curtain | 舞台裏に | 陰で関わっている / 陰で動いている | PASS->**THIN**(2) |
| take the wheel | ハンドルを握る(gold許容) | 主導権を握る | PASS->PASS |
| question shaped like a trophy | トロフィーの形をした問い | 成果や地位を誇示するような問い | FAIL->FAIL(不変) |
- draw a lineはTrial内のB0出力が全て『一線を引く』で未flag(過去の字義NG『線を引く』は検出済み=Phase 0で確認)。

## 4. 改善件数・残存NG・新規悪化

### ②(決定論スコア、rep1、n=42所有格項目)
| 指標 | C0A | C1A |
|---|---|---|
| 誤り(WRONG) | 9 (21%) | **0** |
| 正しい一般化 | 28 | 29 |
| 無変更(許容) | 5 | 13 |
| role判定の正解(vs目視gold) | - | 40/42(誤り2=`pumps its fist`/`pump its fist`の2件、擬人化された財布のitsをself->non_personと判定) |
| 決定論修復の発火 | - | **0/42**(roleとkeyの食い違いが無かった。3モード[role/revert/raw]は同一) |
| canon_status(36 unit) | PASS 33・INVALID 2・REVIEW_REQUIRED 1 | PASS 35・INVALID 1 |
| 対照(非所有格)項目のkey同一率(C0A vs C1A) | - | 99/102(差3=語形のlemma差`third places`/`bean shortages`/`turned on its head`等のrep間ノイズ相当と推定。**rep2未実施でノイズ基準は未測定**) |
- INVALID残り1件(`close around me`->`close around someone`)はC0A・C1Aに共通で、既知のOPEN-357。

### ①(出力単位。61KP=F層41+N標本20、2rep、122出力。暫定=Sonnet参考+既存Fable確定ラベル)
| arm | 出力数 | PASS | 薄 | FAIL(うち字義) | 備考 |
|---|---|---|---|---|---|
| B0(現行) | 122 | 91 | 23 | 8 (2) | 字義NGは an unseen clock x2 |
| **C**(flag項目のみ再生成) | 122 | 90 | 27 | **5 (0)** | 未flag103出力はB0と同一 |
| M(再整合用指示を除くmessage) | 122 | 85 | 29 | 8 (2) | 出力の62%がB0と異なる(churn)。『線を引く』『見えない時計』が出る |
| Cp(C'自己監査) | 61(1rep) | 46 | 13 | 2 (0) | 自己監査flag 0/61 |
- F層のみ: B0 FAIL 7 (字義2)→C FAIL 4 (字義0)。N標本: flag 0件でC=B0(FAIL 1・薄7は両方同じ)。
- C のflag項目内(19出力): **改善4・不変12・悪化3**(悪化=behind the curtain PASS->THIN x2、take off an AI costume rep2 PASS->FAIL)。goldのPASS->FAIL: 0件(gold KPはtake the wheelのみflagされPASS->PASS)。
- 検査器(V2_inv) vs ラベル(字義NG): recall 2/2(an unseen clock x2)、precision 2/19(11%)。C-recheck: 再生成19出力のうち再検査でもflagが残るもの3(an unseen clock x2、pump one's fist rep2)=`FLAGGED_UNREPAIRED`相当(元の採用に戻す設計)。
- B0の字義NG出力が6件未満(2件)のため、OF-D5-05に従い比率ではなく『既知NG+recall/precision+flag項目のBefore/After』で判定した。**「解消」条件(OF-D5-18: F層残存・anchor残存ほぼ0)は未達**(an unseen clockが像寄りに残る)。

### X/Z DEV注入 text E2E(TTSなし、各1本、`e2e_runs/a1ri/rep1`、費用1.7円)
| 記事 | unit | canon_status | gloss_alignment | 注入の結果 |
|---|---|---|---|---|
| X uk_train_speaker_playback | a2 | PASS(attempt 1) | ALIGN_PASS | 検査: 3項目中1 flag(reach for one's wallet)->REPAIRED『自分の財布に手を伸ばす』->『財布を出してお金を払おうとする』 |
| X 同 | b1b | PASS | ALIGN_PASS | 同じく1 flag->REPAIRED『お金を払おうとする』。Adv説明3件OK(`to get ready to pay for something`) |
| Z melos run_kpq_01 | a2 | PASS | ALIGN_PASS | flag 0 |
| Z 同 | b1b | PASS | ALIGN_PASS | flag 0。Adv説明3件OK |
- retry/fallback: canonicalization attempt数=1、expl retry=[False,False]、`SKIPPED_TECH_FAIL`0・`FLAGGED_UNREPAIRED*`0(本E2Eでは再生成が全て有効)。
- **signature**(API 0、`e2e_signature_check.json`): X=Production `_resolve_kp_explanations_text`をAPI呼出スタブでexecして確認。同一入力->reuse(generate 0回)、変更入力(2項目のgloss/key変化)->再利用されず1回再生成。Z=署名式(er026:1575-1581)の複写でhashが変化(同一入力は一致)。
- **Production module sha256**(10ファイル)は開始/終了で一致(`production_hash_start.json`==`production_hash_end_{a1_c,a1r_c,e2e}.json`)。`git status`でも対象Production fileに差分なし。

## 5. X/Z共通仕様・Productionへの影響
- X/Zとも共有moduleを通るため、仕様は共通(`WIRING_DESIGN_04.md`)。**Productionは無変更**(DEV注入はプロセス内attribute差し替えのみ、install前は既定OFF[`er112_kp_gm_poss_04_test_01.py`のDefaultOffIsolationで確認])。
- 未承認機能の既定値: 本Trialの機能はProduction到達経路に入っていない(flag/配線なし)。承認後に配線する場合は新規コード経路+設計どおりの配線委任が必要。
- A-1(規則5)は`APPROVED_FOR_PRODUCTION`のまま、本案と**同一template・同一回帰で連結**する設計(責務は重ならない)。

## 6. QCDと必要な判断
- **Q**: ②は誤りを0にした一方、正しい一般化2件が無変更へ後退(roleのnon_person誤判定)。①は重大失敗(FAIL)を減らしたが、検査の低precisionによりflag項目の一部で品質低下(THIN/FAIL化)が出る。Fable盲検での確定が必要。
- **D**: 追加call(②:0、①:+1/記事)による遅延は小(検査はgloss直後の1call)。
- **C**: ②+0.03円/記事、①+0.2〜0.25円/記事(合計約0.25円=70円目標の0.35%)。事前宣言(≤0.15円/記事)は**未達**。
- **次の一手の候補(①、改善見込みの自己評価)**: (a)flagをさらに絞る(二重検査で一致時のみflag、または検査器をSolで1回だけ)=precision改善見込み中〜高、費用+0.1〜0.3円/記事、(b)再生成だけをSolにする(C-Sol)=an unseen clock型(著者が作った比喩)の残存に効く見込み中、1call 1.13円x flag率で約0.15〜0.3円/記事、(c)A案『ユーザーへ字義NG許容(約2〜3%/KP)の判断を求め①は現状維持』=費用0。**推奨は、②を先に採用提案へ進め、①は(a)+(b)を追加Trial(上限は別途承認枠)で検証するか、(c)をユーザーに諮ること**。
- 判断候補(`判断候補`、D=真に新しい判断): §`WIRING_DESIGN_04.md` §4の一覧(特に#1費用、#2/#3 Prompt・許可表の変更、#4 fail-open、#7 既存記事)。Trial追加(上記(a)(b))は新Trial範囲として別承認が必要。

## 7. 限界・未確認(推測で埋めない)
- ②は1 repのみ・合成13項目(型網羅用)と実データ29項目の混在。rep間ノイズ基準は未測定(予算不足で未実施)。roleの目視gold自体が実行層の目視(29件+新規13件)。
- ①の最終数値は**Fable盲検待ち**(盲検表=`TRIAL_04/fable_blind_04.md`、51行・232セル、key分離。ingest scriptは`er112_kp_gm_trial_04_report.py report --labels <json>`で再集計可)。Sonnet参考Judgeは過去にFableとの乖離(83/360セル)があり、特にtake the wheel『車を運転する』(goldは許容)をFAILと判定した例がある。
- `er003_test_kp_fulltext_wiring_01.py`・`er064_*`の一部は本環境で`wordfreq`未導入のためcollect不可(採用時の配線委任で確認)。
- 検査器はPhase 0で1回のみ改訂(v1->v2low)。精度向上の余地は未探索(予算上限のため)。
