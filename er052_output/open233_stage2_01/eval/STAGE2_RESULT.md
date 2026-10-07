# STAGE2_RESULT(OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01 委任_02、2026-10-07〜08)

位置づけ: Trial/検証(DEV)の結果。Production変更なし、`APPROVED_FOR_PRODUCTION`なし、SSOT未編集。全新規挙動は環境変数スイッチ既定OFF(`OPEN233_STAGE2_READER_BELIEF` / `OPEN233_STRUCTURAL_REWRITE_RULES`、W1/W2/r3保存は委任_01)。事前登録=`docs/pm/checker_action_policy_01/preregistration_stage2.md`(数値・ラインは不変のまま適用)。
詳細証跡: 本ディレクトリ(`replay_dev/`、`replay_heldout/`、`eval/`)。数値の出所は各`eval/*.json`。

## 1. 結論(機械適用)
**総合判定: FAIL**(②読者信念テストは不合格=rubric追記打ち止め[O3]、①構造要素規則はゲートとして機能したが、構造要素由来STOPが仮ライン超)。
総合の機械適用規則(事前登録に総合規則は無いため、本委任での適用): 全9ラインPASS→PASS / ライン1〜3のどれかFAIL→FAIL / それ以外でFAILあり→CONDITIONAL。ライン2がFAILのためFAIL。**Fable/ユーザーが読み替える余地あり**(下記ライン2は同一文2項目・サンプリング揺れの疑い)。

### 1-1. ライン別(dev、②=rubric v2[最終版]、①=規則ON)
| ライン | 内容 | 結果 | 判定 |
|---|---|---|---|
| 1 | 構造要素の規則違反(4照合違反・主体差し替え・`# `欠落)0件 | 規則ON出力14件(dev,3回反復)で違反**0**・`# `欠落0(規則OFF=現行相当は21件中9件が違反: 主体差し替え`I→Meta`/`AI→Muse`、極性「without clearly telling users」脱落等) | **PASS**(ゲートとして機能) |
| 2 | 現行BLOCKINGの既知NGが格下げへ回る退行0 | 現行BLOCKINGの既知NG 3件中**2件が非BLOCKING**(jb9k-n1/n2=同一文`brought under control about an hour after it was found`・限定語消失型・fact一致のみ)。現行構成の再実行(control_off)は退行0 | **FAIL**(注: 同一文×2項目。現行構成も同文で`llm=ACCEPTABLE→2nd opinion split`に頼る不安定。ガード対象外の文で②追記が効いたとは断定できない) |
| 3 | HC-012・A5-0は悪化しない | HC-012(dev 8件): 非BLOCKING 8→7、悪化0。A5-0: 新構成3/3 BLOCKING(belief=contradicts)、現行再実行も3/3 | **PASS**(held-outではHC-012系`meta-475j-n1`がBLOCKING→ACCEPTABLEで悪化=下記) |
| 4 | ガード対象型でStage1が候補化し現行が格下げしたdev NGの半数以上が格下げ不成立 | 12件中**1件(8.3%)**。文レベル確証の5件では0件。方向・極性型(6件)はガード対象に付かない(DIRWORD不採用、Stage1フラグ無し) | **FAIL** |
| 5 | 既知NGでない候補の新規BLOCKINGが+0.3件/記事以内かつ相対+15%以内 | 8→27件(22記事): **+0.86件/記事・相対+237%**。現行再実行(control_off)は10件(+0.09件/記事)=サンプリング揺れは小さい | **FAIL** |
| 6 | 削除文数+0.2件/記事以内 | ②で新たにBLOCKINGとなった24候補を実Rewrite: 削除13文(**+0.59件/記事**、消えた5候補の削除0)。①単独(構造要素Rewrite)は削除0(Hook最終手段削除の発動0) | **FAIL**(②由来。dev入力は`rewrite_kind`を`replace_with_ledger_value`で近似=下限側。held-outは保存値で+0.1件/記事) |
| 7 | belief_vs_ledgerの3回一致率80%以上 | 無作為10候補×3回で**9/10=90%** | **PASS**(注: 8/10は常にconsistentで易しい標本) |
| 8 | 費用+¥1/記事以内 | v2: +¥0.30/記事(新¥0.98 vs 保存済み¥0.68) | **PASS** |
| 9 | rubric調整は2版まで | v1(初版)+v2(調整1回)=2版 | **PASS** |
| 追加 | 構造要素由来STOP(ladder枯渇)が記事の3%以下 | 構造要素にBLOCKINGがある23記事(dev22+qvqc)で、3回反復の記事STOP率**8.7% / 8.7% / 13.0%**(held-out 1/10=10%) | **FAIL**(N小。原因=主体部分集合規則で`AI→Muse`型の書換えが全levelで却下されるHook/一行要約) |

### 1-2. 測定(0)〜(6)の結果
- (0) Stage1候補化率: 委任_01の結果を転記(下限23.4%[文レベル]〜上限61.7%[fact一致含む]、ガード型別は`precheck/stage1_candidate_rate.md`)。
- (1) W1/W2回帰replay(qvqc rep2、Rewrite決定論部分+Recheck実API1回、¥1.17): W1ON=`# `保持(`title_markup_restored=true`)、W2ON=Recheck対象単位に**`T`(タイトル)が入る**(`T_in_scope_new=true`、保存済みOFFは`false`)。Recheckは`LEDGER_DEVIATION`(タイトルの主体差し替えを検出)。
- (2) ②replay dev(22 run、259候補、ガード対象141): 上表。v1とv2の差は「3. rubric版履歴」。
- (3) ①Rewrite→Recheck(7対象×3反復×ON/OFF=42job): 上表ライン1・STOP。Recheck(構造要素の前後対つき)は書換えた14件中LEDGER_COMPLIANT 3/LEDGER_DEVIATION 11(新規逸脱13件の多くは書換えで直らなかった元指摘・隣接文の一般化の再検出で、Stage2トリアージ前の候補)。
- (4) held-out 1回(`replay_heldout/final`、10 run・14項目マッチ、費用¥10.6+Rewrite補助¥6.6): **devと同方向、回帰0ではない**。新規BLOCKING 8→13(+0.5件/記事・+62%)、現行BLOCKINGの既知NG 4件中**2件が非BLOCKING**(`meta-qvqc-n3`=タイトル`I Followed...`[M2の意図どおり非BLOCKINGへ]、`meta-475j-n1`=`But the humans who ended up in the main role had not been told.`[consistentが2回一致して誤る=整合チェックの限界])、HC-012系は非BLOCKING 3→4(悪化1)。ガード対象型の格下げ不成立1/5。費用+¥0.29/記事。構造要素Rewrite(ON、n=1)は6job中STOP 2(space_weapons一行要約、4照合却下3回)。
- (5) 人間確認パック: `eval/HUMAN_REVIEW_PACK_STAGE2.md` **71件**(dev 49・held-out 22。内訳: 上位10%記事28件[dev3記事+held-out1記事]、重大候補10件、分かれた文は大半)。Checkerの重大度は伏せ、対応表は`eval/_private/HUMAN_PACK_MAP.json`。人間判定は未実施(上位10%内の重大捕捉率は未算出)。
- (6) 面白さ代理指標: **非劣性は未確認**。`narrative_count.py`のJA正規表現はEN本文に適用できない(JA本文はEN-onlyのCheckerでは不変)ため、同ファイルの`align`を再利用したEN版を`proxy_pairs.py`で算出(`eval/narrative_proxy.json`)。ON/OFF(21件): 変更文比率 0.011/0.018、削除文比率 0/0、タイトルの一人称・二人称枠の消失 1件(ON)/3件(OFF)、Hook疑問・意外性の消失 0。ユーザー盲検読み比べ用ペア3組(タイトル・Hookが変わり出力が分かれた対象のみ)=`eval/pairs_for_user/`(A/Bは匿名、対応は非公開`eval/_private/PAIRS_MAP.json`)。

## 2. ①Checker由来の新規NG(目視、規則ON出力14件)
決定論の4照合では違反0。目視で次の**規則の盲点**を確認:
1. `The AI makes the call.`→`The human makes the call.`(qvqc Hook、3反復中2回): 一般名詞の主体入れ替え(`AI`→`human`)。固有名詞・代名詞・既存主体クラスに無い語のため主体照合を通る。Ledgerは「一部の電話を人間が担当」なので過度な一般化。
2. qvqcタイトル`# I Followed an AI Phone Agent and Found a Human`→`# AI Phone Agent Test Put Humans on the Line`: 部分集合(主体`I`の削除)として通るが、語り手の一人称の枠(演出)が消える(面白さ面の変化。代理指標で1件)。
3. 一行要約の限定語は`without users being told`→`without proper disclosure`/`without appropriately telling users`等へ言い換え(極性は不変、意味変化は軽微)。
- いずれも設計上は許容(部分集合)だが、1は事実の過度な一般化で、Recheck(`LEDGER_DEVIATION`)が検出している=W2配線の効果。

## 3. rubric版履歴(②、O3)
- **v1(初版、V7c相当)**: V7bへ読者信念テスト(reader_belief/belief_vs_ledger/contradicting_fact_ids)+M2「語り手の枠は世界主張として扱わない」+guard_targetは私(システム)が決める旨を追記(design_02 §2-4)。dev結果: 新規BLOCKING+1.05件/記事、ライン2/4/5 FAIL。原因: `unsupported_new_claim`が「Ledgerのfactの言い換え・要約」(例: 経営幹部がミスと認めた=Ledgerのfact)にも大量に付き(強制BLOCKING13件)、2回目(文を伏せる)もconsistentにならない(belief-only split 12件)。
- **v2(調整1回目)**: `consistent`=「Ledgerのfactを言い換えた・要約した・組み合わせたもの(同じ事実関係・主体・向き・程度)」、`unsupported_new_claim`=「Ledgerに無い新しい固有名詞・数値・日付・出来事・因果の追加だけ」と定義を明確化。guard_target=trueでnot_applicableを禁止、guard_target=falseのmaterialityは従来基準だけで判定。2回目(belief-only)も同定義。contradicts→BLOCKING・M2枠規則は不変。結果: 強制BLOCKING 13→3件、新規BLOCKING+0.86件/記事(なお超過)、belief-only split 15件(2回目の構造的厳しさは残る)。
- **解釈の注記(要Fable確認)**: 事前登録「rubric調整は2版まで」を「初版+調整1回=計2版」と保守的に解釈し、v2で打ち止めた。「調整2回=v3まで可」の解釈なら1版の余地が残るが、v2の失敗要因(ライン4=方向・極性型がガード対象に付かない設計、ライン5=belief-only 2回目の構造)はrubric文言の調整では解けない見込みで、v3は実施していない。
- **②不合格=rubric追記打ち止め(O3)として記録**。HC-012方向語は新ターゲットにしていない。
- 整合チェックの限界(明記): 「consistent+非BLOCKING」と**一貫して誤るケースは止められない**。実例: jb9k-n3(`Nor has anyone reported that an AI got out of the test environment.`)はv1/v2とも1回目consistent・2回目consistentでACCEPTABLEのまま(現行構成の再実行は2nd opinionの揺れでBLOCKINGになったが、これはサンプリング揺れ)。held-outの`meta-475j-n1`も同型。O1の2回目はreader_beliefの取り違えを持ち越しうる。jb9k/qvqc/HC-012は回帰確認枠として扱い、有効性を一般化しない。

## 4. 実装要点とテスト
- 新規モジュール `er052_open233_checker_action_policy_stage2_01.py`(guard_target・V7c prompt/schema・belief-only 2回目・4照合)+runnerへの配線(`run_stage2`の信念テスト/同一call整合チェック[contradictsなのに非BLOCKINGなら再判定1回、なお矛盾ならBLOCKING=Rewrite増側と記録]、`apply_belief_second_opinion`[guard_targetの格下げは1回目・2回目ともconsistentのみ]、再利用禁止、`rewrite_ranges_ladder`の構造要素4照合+再生成1回+Hook文削除の最終手段化+level6の4照合)。
- テスト: 新規58件(ON/OFF、M1/M2、(c)(d)(e)分岐、4照合、Hook最終手段、v2切替)+W1/W2 11件。`er052_open233*test*`全体**1042件PASS**(着手前の既存833件を含む)。
- 発見・修正した実装不備(devの実測で判明、いずれも決定論側): 固有名詞語彙がLedgerの小文字URL(meta.com)で`Meta/Muse/AI`を落とす/`By`等の位置大文字を拾う/文頭のみの固有名詞を拾わない/語彙に無い大文字語の持込(`Japan→Matsuyama`)を検出しない。修正後に①ON測定をやり直した(修正前のON結果は`replay_dev/_discarded_*`に退避、集計に不使用)。

## 5. 費用
- 段階2実費**¥157.5**(¥180のSTOP未到達、上限¥200内)。内訳: ②dev replay v1 ¥15.4 / v2 ¥21.6 / control_off ¥10.0 / qvqc ¥1.2、held-out ¥10.6、安定性¥2.5、A5 ¥1.4、①Rewrite(最終版)¥17.3、②Rewrite補助 ¥7.7、W1/W2 ¥1.2。
- **無駄の内訳(約¥68)**: バックグラウンド二重起動でdev v1とcontrol_offを2プロセス同時実行してしまい(同時≤4の単層規律に反した、¥30.9)、規則の語彙不備による①再実行3回(¥37.5)。結果は各run1回分の有効なreplayだが費用が重複。再発防止: 起動前にプロセス確認、バックグラウンドは1コマンドずつ。
- 夜間総予算: 消費済み≈¥21.4+段階2 ¥157.5=**≈¥178.9**(¥1000内、¥950停止ライン未到達)。

## 6. 制約・限界・Fable判断が要る点
1. 総合FAILの読み替え: ライン2の2件は同一文の重複項目(fact一致のみ・限定語消失型)で、現行構成も不安定。ライン1/3/7/8/9はPASS。
2. ①は4照合ゲートとして機能(違反0)する一方、構造要素由来STOPが8.7〜13%で仮ライン3%を超える。主体部分集合規則が`AI→Muse`型の事実的に正しい書換え(Ledgerに`Muse`あり)も却下するため。設計(M1)の許容範囲の再考(例: Ledgerに存在する固有名詞は新主体として許す)はFable/ユーザー判断。
3. 委任文(c)「不通過→再生成1回→不通過なら元のまま+QUALITY記録」は、**ladder枯渇経路(既存の許可リストSTOP)+`kept_original_quality_record`記録**として実装。元のまま未修正でパスさせる(BLOCKINGを直さずQUALITY扱いで出口へ出す)新経路は、`unrewritten_blocking_pass=0`の既存安全装置を回避することになるため作っていない。作る場合は設計判断が必要。
4. 規則の盲点: 一般名詞の主体入れ替え(`AI→human`)は通る(本書2節)。
5. replayは保存済みStage1候補を固定したcycle1の再判定で、cycle連鎖・実Recheck→cycle2は再現していない。(e)再利用禁止はソース配線のテストのみで、cycle2の実run未確認。
6. 候補↔既知NG項目の対応は機械近似(fact一致のみ=同factの別文の可能性)。held-outのqvqc rep2 runはdevでの回帰確認(W1/W2・qvqc構造要素)にも使っており、held-outの純度は完全ではない(設計上qvqc/jb9kは回帰確認枠)。
7. 保存済み判定との比較はサンプリング揺れを含む(control_off再実行: +0.09件/記事、退行0で揺れは小さい)。
8. ②の信念テストの効果: 有効な点=A5-0を3/3で`contradicts`と判定、M2によりqvqcタイトル(一人称枠)がBLOCKINGでなくなる。無効な点=jb9k型(否定・不在の格下げ見逃し)と方向・極性型は救えず、非NG候補のBLOCKINGを大きく増やす(Rewrite増側、削除+0.59件/記事)。
9. 面白さの非劣性は未確認(ユーザー盲検読み比べが必要)。人間確認パックは未判定。
