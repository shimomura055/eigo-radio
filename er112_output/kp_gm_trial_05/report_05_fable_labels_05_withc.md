# Trial_05 集計(ラベル=docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/TRIAL_05/fable_labels_05.json)

## OF-KP1-08 盲検の再現性(既存ラベル済み文字列の再判定)

- 厳密一致 7/10、粗区分(PASS/THIN/NG)一致 7/10
  - play a part | 一因となる | 前回=PASS 今回=PASS 
  - an unseen clock | 目に見えないタイミングの仕組み | 前回=PASS 今回=PASS 
  - an unseen clock | 見えない時計 | 前回=FAIL_LIT 今回=FAIL_LIT 
  - sound no one asked for | 誰も頼んでいない音 | 前回=PASS 今回=PASS 
  - draw a line | 区別する | 前回=THIN 今回=PASS **不一致**
  - greener grass | より青々とした芝生 | 前回=FAIL_LIT 今回=FAIL_LIT 
  - question shaped like a trophy | トロフィーの形をした質問 | 前回=FAIL_LIT 今回=FAIL_LIT 
  - brace yourself for | ～に備える | 前回=THIN 今回=THIN 
  - reach for someone's wallet | 人の財布に手を伸ばす | 前回=FAIL 今回=PASS **不一致**
  - on the throne | トップの座にいて | 前回=THIN 今回=PASS **不一致**

## R(hard-core 4KP x 3rep=12出力/arm) と 事前宣言基準(TRIAL_DESIGN_06 §4)

| arm | n | PASS | THIN | FAIL | FAIL_LIT | 未ラベル | (FAIL_LIT+FAIL) | 2rep以上失敗のKP | 基準(<=1/12 かつ 2rep以上失敗KP=0 かつ THIN<=B0+1) |
|---|---|---|---|---|---|---|---|---|---|
| B0 | 12 | 2 | 0 | 0 | 10 | 0 | 10 | ['an unseen clock', 'question shaped like a trophy', 'greener grass'] | - |
| M | 12 | 6 | 0 | 0 | 6 | 0 | 6 | ['an unseen clock', 'question shaped like a trophy'] | 満たさない |
| X1 | 12 | 7 | 0 | 0 | 5 | 0 | 5 | ['question shaped like a trophy'] | 満たさない |
| X2 | 12 | 8 | 4 | 0 | 0 | 0 | 0 | なし | 満たさない |
| Cp | 12 | 9 | 1 | 0 | 2 | 0 | 2 | なし | 満たさない |
| X2p | 12 | 6 | 0 | 0 | 0 | 6 | 0 | なし | **満たす** |
| Cp_t4 | 4 | 3 | 1 | 0 | 0 | 0 | 0 | なし | **満たす**(n<12参考) |

(Mは Trial_04の既存rep1-2 + 新規rep3。X1対M=H5の比較。)

### R co-KP(come down / behind the scenes / sound no one asked for)の悪化確認

| KP | rep | B0 | M | X1 | X2 | Cp | X2p | Cp_t4 |
|---|---|---|---|---|---|---|---|---|
| come down | 1 | 下がる (PASS) | 下がる (PASS) | 下がる (PASS) | 値下がりする (PASS) | 下がる (PASS) | 値下がりする (PASS) | 下がる (PASS) |
| come down | 2 | 下がる (PASS) | 値下がりする (PASS) | 値段が下がる (PASS) | 下がる (PASS) | - | 値下がりする (PASS) | - |
| come down | 3 | 下がる (PASS) | 下がる (PASS) | 値段が下がる (PASS) | 値下がりする (PASS) | - | 下がる (PASS) | - |
| behind the scenes | 1 | 舞台裏で (PASS) | 表に出ずに裏で (PASS) | 表に出ないところで (PASS) | 人目につかないところで (PASS) | 表に出ないところで (PASS) | 人目につかないところで (PASS) | 人目につかないところで (PASS) |
| behind the scenes | 2 | 舞台裏で (PASS) | 人目につかないところで (PASS) | 表に出ずに (PASS) | 人目につかないところで (PASS) | - | 人目につかないところで (PASS) | - |
| behind the scenes | 3 | 舞台裏で (PASS) | 舞台裏で (PASS) | 人目につかないところで (PASS) | 表に出ないところで (PASS) | - | 表に出ずに (PASS) | - |
| sound no one asked for | 1 | 誰も頼んでいない音 (PASS) | 誰も求めていない音 (PASS) | 誰も頼んでいない音 (PASS) | 誰も聞きたくない音 (THIN) | 誰も求めていない音 (PASS) | 誰も聞きたくない音 (THIN) | 誰も求めていない音 (PASS) |
| sound no one asked for | 2 | 誰も求めていない音 (PASS) | 誰も求めていない音 (PASS) | 誰も求めていない音 (PASS) | 誰も望んでいない音 (PASS) | 誰も求めていない音 (PASS) | 誰も求めていない音 (PASS) | - |
| sound no one asked for | 3 | 誰も頼んでいない音 (PASS) | 誰も求めていない音 (PASS) | 誰も求めていない音 (PASS) | 誰も聞きたくない音 (THIN) | - | 誰も頼んでいない音 (PASS) | - |

### R Before/After (KP x arm x rep)

| KP | rep | B0 | M | X1 | X2 | Cp | X2p | Cp_t4 |
|---|---|---|---|---|---|---|---|---|
| draw a line | 1 | 一線を引く / PASS | 違いをはっきり示す / PASS | 境目をはっきりさせる / PASS | 違いをはっきり示す / PASS | 線引きをする / PASS | はっきりと区別する / ? | 区別する / THIN |
| draw a line | 2 | 一線を引く / PASS | 線を引く / FAIL_LIT | 境目をはっきりさせる / PASS | 区別をつける / PASS | 線引きをする / PASS | 違いをはっきり示す / PASS | - |
| draw a line | 3 | 線を引く / FAIL_LIT | 違いをはっきりさせる / PASS | 線を引く / FAIL_LIT | 境目をはっきり示す / PASS | 境界線を引く / PASS | 区別をはっきりさせる / PASS | - |
| an unseen clock | 1 | 目に見えない時計 / FAIL_LIT | 見えない時計 / FAIL_LIT | 目に見えない独自の時間の流れ / PASS | 価格が変わるまでの見えない時間差 / THIN | 目に見えない時間の仕組み / PASS | 値札に隠れた独自のタイミング / ? | 目に見えないタイミングの仕組み / PASS |
| an unseen clock | 2 | 目に見えない時計 / FAIL_LIT | 目に見えない時計 / FAIL_LIT | 目に見えない時計 / FAIL_LIT | 価格が変わるまでの見えない時間差 / THIN | 見えない時計 / FAIL_LIT | 値札に隠れた時間のずれ / ? | - |
| an unseen clock | 3 | 目に見えない時計 / FAIL_LIT | 見えないところで時を刻む時計 / FAIL_LIT | 表には見えない独自の時間の流れ / PASS | 値札に隠れた時間差 / THIN | 目に見えない時間の仕組み / PASS | 表には見えない独自のタイミング / ? | - |
| question shaped like a trophy | 1 | トロフィーの形をした質問 / FAIL_LIT | 賞を通じて投げかける問い / PASS | 賞の形をした問いかけ / FAIL_LIT | 賞を通じて投げかける問い / PASS | トロフィーの形を借りた問いかけ / THIN | 賞という形で投げかける問い / PASS | 賞という形で投げかける問い / PASS |
| question shaped like a trophy | 2 | トロフィーの形をした質問 / FAIL_LIT | トロフィーの形をした問いかけ / FAIL_LIT | 賞の形をした問いかけ / FAIL_LIT | 賞を通じて投げかける問い / PASS | 賞という形で投げかけられた問い / PASS | 賞という形で投げかける問い / PASS | - |
| question shaped like a trophy | 3 | トロフィーの形をした質問 / FAIL_LIT | トロフィーの形をした問いかけ / FAIL_LIT | 賞の形をした問いかけ / FAIL_LIT | 賞の形を借りた問いかけ / PASS | 賞を通して投げかける問い / PASS | 賞という形で投げかける問い / PASS | - |
| greener grass | 1 | より青く見える芝生 / FAIL_LIT | 自分より恵まれて見える人の暮らし / PASS | 人の暮らしのほうが自分より良く見えること / PASS | 他人の暮らしのほうがよく見えること / PASS | 自分の暮らしよりよく見える他人の暮らし / PASS | 自分より恵まれて見える他人の暮らし / PASS | 人のもののほうがよく見えること / PASS |
| greener grass | 2 | より青々とした芝生 / FAIL_LIT | 他人のほうが恵まれているように見えること / PASS | 隣の芝生のほうが青く見えること / PASS | 他人のほうがよく見える状況 / THIN | 自分より恵まれて見える他人の暮らし / PASS | 人の暮らしのほうがよく見えること / ? | - |
| greener grass | 3 | より青々とした芝生 / FAIL_LIT | 自分より恵まれて見える他人の暮らし / PASS | 人の暮らしのほうが自分よりよく見えること / PASS | 他人の暮らしのほうがよく見えること / PASS | より青々とした芝生 / FAIL_LIT | 他人の暮らしが自分よりよく見えること / ? | - |

## held-out(各1rep、B0/X2/Cp/X2p)

| KP | B0 | X2 | Cp | X2p | 悪化(B0=PASSでX2/Cp/X2p=THIN/FAIL/FAIL_LIT) |
|---|---|---|---|---|---|
| rise above | ～より大きく聞こえる / PASS | ほかの声より大きく響く / PASS | ～より大きく響く / PASS | ひときわ大きく響く / ? | なし |
| tiny bomb | 小さな爆弾 / PASS | 小さな爆弾 / PASS | 小さな爆弾 / PASS | 小型爆弾 / ? | なし |
| work to do | やるべきこと / PASS | これから取り組むべきこと / PASS | まだ取り組むべきこと / PASS | まだやるべきこと / ? | なし |
| become like porches | 玄関先のような場所になる / THIN | 近所の人が気軽に立ち寄って交流できる場所になる / PASS | 人が気軽に立ち寄り、交流できる場所になる / PASS | ベンチが人々の憩いや交流の場になる / ? | なし |
| carry a decision's weight | 決定の重さを背負う / PASS | 決定の負担を背負う / PASS | 決定の重みを背負う / PASS | 決定の重みを背負う / PASS | なし |
| a door inside the pain | 痛みの中にある扉 / THIN | 苦しみの中に見えた、記憶へ戻る道 / THIN | 苦しみの中にある戻り道 / THIN | 悲しみの中に見つけた、思い出と向き合い直す道 / ? | なし |
| one doorway among several | いくつかある入り口の一つ / PASS | いくつもあるアクセス手段の一つ / PASS | 複数あるアクセス手段の一つ / PASS | 複数あるアクセス手段の一つ / PASS | なし |
| inner timekeeper | 体内時計 / PASS | 体内時計 / PASS | 体内時計 / PASS | 体内時計 / PASS | なし |
| two different speeds | 二つの異なるペース / PASS | 旅行への意識と実際の旅行計画の変化の速さの違い / PASS | 異なる二つのペース / PASS | 異なるペースで進む二つの動き / ? | なし |
| all it takes | 必要なのは～だけ / PASS | 必要なのは～だけ / PASS | 必要なのは～だけ / PASS | それだけで十分 / ? | なし |

held-out 悪化: X2=なし Cp=なし X2p=なし(基準: 0)

