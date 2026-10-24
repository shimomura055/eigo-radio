# QUALITY_CHECK_35: X2p'配線後の品質確認(委任_35。Fableが独立受入で読む)

2026-10-24。新規LLM評価call 0(判定は本ファイルの機械的突合と、Trial_06既存成果の再利用)。追加Trial・Prompt改変・磨き込みなし。使用モデル=`gpt-6-luna`(Production gloss同一系列、最新世代の推奨系)。証跡=`WIRING_35/`、各KPの生出力は `<run>/<level>/key_phrases/keywords_canonicalized.json` の `gloss_alignment`(`meaning_in_text_en`・`naive_ja`・`naive_ja_conveys`・`import_flags`)。

## 1. 記事B(uk_train_speaker_playback、X)全KP: 旧→新(本文での語義と訳の対応)
本文での用法は `source_sentence` と `meaning_in_text_en`(モデルが本文から確定した語義)で確認。判定は私(Sonnet)の機械的・言語的確認であり、最終耳確認ではない。

| Lv | # | KP(旧→新) | 旧gloss | 新gloss | 本文での語義(`meaning_in_text_en`) | naive_ja / conveys | 判定 |
|---|---|---|---|---|---|---|---|
| Std | 1 | sound no one asked for(不変) | 誰も求めていない音 | 誰も望んでいない音 | 誰も頼まず/望んでもいない音 | 誰も頼まなかった音 / yes | 意味同等(言い換え)。誤りなし |
| Std | 2 | reach for one's wallet(不変) | 自分の財布に手を伸ばす | 自分の財布に手を伸ばす | 財布を取り出すために手を財布へ動かす | 自分の財布の方へ手を伸ばす / yes | 旧と同一。字義訳が許容される用法(本文は「ボリュームボタンより先に財布に手が伸びる」)で比喩化していない。誤りなし |
| Std | 3 | **draw that line → draw a line**(A-1) | その線を引く | **一線を引く** | 二つの側/選択肢を分ける境界を設ける | 線を描く / **no** | **字義訳(「線を引く/描く」)を避け、定訳「一線を引く」に確定**。目的(draw a line→字義訳防止)達成 |
| Adv | 1 | a blanket ban(不変) | 全面的な禁止 | 全面的な禁止 | 例外を設けず全体に及ぶ禁止 | 毛布の禁止 / no | 旧と同一。「毛布」の字義訳を回避。誤りなし |
| Adv | 2 | reach for one's wallet(不変) | 自分の財布に手を伸ばす | **お金を払おうとする** | 自分の資金から支払う用意をする | 自分の財布に手を伸ばす / partly | 本文(「音量ボタンより先に財布に手が伸びる=お金を払う気になる」)に沿った慣用的意味。字義(財布に手)でなく意図(支払う)を表す。意味の誤りなし。Std(字義)とAdv(意味)で表現が異なるのは各levelの独立生成による(いずれも許容) |
| Adv | 3 | **draw that line → draw a line**(A-1) | その境界線を引く | **境目をはっきりさせる** | 物事の間に明確な区別・境界を設ける | 線を引く / yes | 字義訳「線を引く」でなく本文の意味(区別を明確にする)。定訳ではなく説明的だが誤りなし(Trial_06で許容済みのTHIN級) |

- `import_flags`(持ち込み検出・記録のみ): 記事B 6件すべて空。
- `draw a line`: Std/Adv とも字義訳(「線を引く」)でない。STOP条件「`draw a line`が新経路でも字義訳のまま」に該当せず。
- 字義が正解のKPの比喩化: `reach for one's wallet`(Std)は字義のまま=過剰解釈なし。Adv側は意図(支払う)へ寄せたが、本文が比喩的用法のため適切。
- 意味の誤り・不自然な訳: 0(THIN相当の弱さがAdv #3のみ。ユーザー許容済み範囲)。

## 2. Z evidence(『猿の手』コピーrun `the_monkeys_paw/run_kpgm35_01`、公開物 `run_sf_prod_01` は不変)の新gloss vs 既存Production(公開中)
KPの選定・canonicalizationは再実行されるため、KP自体が異なる項目がある(選定LLMの非決定性。Regression観点では同一KPの訳を比較)。

| Lv | KP | 公開中gloss(旧経路) | 新gloss(X2p') | 本文での語義 | 判定 |
|---|---|---|---|---|---|
| Std | sergeant-major(同一KP) | 曹長 | 曹長 | 陸軍の上級下士官 | 同一。Regressionなし(naive_ja「軍曹・少佐」conveys=no→定訳に確定) |
| Std | rise into the night(同一KP) | 夜の中へと響き渡る | 夜の闇へ高く響いていく | 音が夜空へ上がり広がる | 意味同等。「闇」「高く」の付加は本文の描写の範囲(誤りなし) |
| Std | break the silence(新選定、公開版は take hold of) | (比較対象外) | 沈黙を破る | 音で静けさを破る | 定訳。誤りなし |
| Adv | interfere with fate(同一KP) | 運命に干渉する | 運命に手を加える | 運命として定められたことを変えようとする | 意味同等。誤りなし |
| Adv | wail of loss(同一KP) | 失った悲しみの叫び | 失った悲しみの叫び | 喪失を嘆く叫び | 同一 |
| Adv | caught in the machinery(新選定、公開版は in compensation) | (比較対象外) | 機械に巻き込まれた | 機械の部品に挟まれる | 誤りなし。`past_tense_ending`が付くがKPが過去分詞のため誤検出(記録のみ、合否に使わない) |

- 同一KPの比較5件: 同一2、言い換え同等3、意味の悪化0。Regression重大0。
- 公開物は差し替えない(別run dir `run_kpgm35_01`、`run_sf_prod_01`は不変)。

## 3. Trial_06既存成果の再利用(新規LLM評価call 0)
- `TRIAL_06/TRIAL_RESULT_06.md`・`AGREE_06_FINAL.md`: 本番相当構成で字義訳(FAIL_LIT)解消、過剰解釈0、通常KPのTHIN(厳しい側7/54)は意味の誤りではなく弱い・説明調。ユーザーが実例確認のうえ許容済み(UDR #179)。**本委任はその承認品質基準を変更していない**。Production Promptは `build_x_message06` とbyte一致(golden WC-12)のため、Trial_06の評価結果がそのまま適用される。
- 本委任の追加サンプル(記事B 6KP + Z 6KP)は上記表のとおり意味の誤り0。承認品質を満たしたため、検証をここで終了(追加Trial・磨き込みなし)。

## 4. Standard/Advanced双方での機能
- X: Std a2・Adv b1b とも `meaning_stage=applied`、ALIGN_PASS(attempt 1)。Z: a2・b1b とも `applied`。
