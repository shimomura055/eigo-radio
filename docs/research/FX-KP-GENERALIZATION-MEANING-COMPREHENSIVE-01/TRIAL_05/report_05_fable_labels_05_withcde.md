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
| X2p | 12 | 11 | 1 | 0 | 0 | 0 | 0 | なし | **満たす** |
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
| draw a line | 1 | 一線を引く / PASS | 違いをはっきり示す / PASS | 境目をはっきりさせる / PASS | 違いをはっきり示す / PASS | 線引きをする / PASS | はっきりと区別する / PASS | 区別する / THIN |
| draw a line | 2 | 一線を引く / PASS | 線を引く / FAIL_LIT | 境目をはっきりさせる / PASS | 区別をつける / PASS | 線引きをする / PASS | 違いをはっきり示す / PASS | - |
| draw a line | 3 | 線を引く / FAIL_LIT | 違いをはっきりさせる / PASS | 線を引く / FAIL_LIT | 境目をはっきり示す / PASS | 境界線を引く / PASS | 区別をはっきりさせる / PASS | - |
| an unseen clock | 1 | 目に見えない時計 / FAIL_LIT | 見えない時計 / FAIL_LIT | 目に見えない独自の時間の流れ / PASS | 価格が変わるまでの見えない時間差 / THIN | 目に見えない時間の仕組み / PASS | 値札に隠れた独自のタイミング / PASS | 目に見えないタイミングの仕組み / PASS |
| an unseen clock | 2 | 目に見えない時計 / FAIL_LIT | 目に見えない時計 / FAIL_LIT | 目に見えない時計 / FAIL_LIT | 価格が変わるまでの見えない時間差 / THIN | 見えない時計 / FAIL_LIT | 値札に隠れた時間のずれ / THIN | - |
| an unseen clock | 3 | 目に見えない時計 / FAIL_LIT | 見えないところで時を刻む時計 / FAIL_LIT | 表には見えない独自の時間の流れ / PASS | 値札に隠れた時間差 / THIN | 目に見えない時間の仕組み / PASS | 表には見えない独自のタイミング / PASS | - |
| question shaped like a trophy | 1 | トロフィーの形をした質問 / FAIL_LIT | 賞を通じて投げかける問い / PASS | 賞の形をした問いかけ / FAIL_LIT | 賞を通じて投げかける問い / PASS | トロフィーの形を借りた問いかけ / THIN | 賞という形で投げかける問い / PASS | 賞という形で投げかける問い / PASS |
| question shaped like a trophy | 2 | トロフィーの形をした質問 / FAIL_LIT | トロフィーの形をした問いかけ / FAIL_LIT | 賞の形をした問いかけ / FAIL_LIT | 賞を通じて投げかける問い / PASS | 賞という形で投げかけられた問い / PASS | 賞という形で投げかける問い / PASS | - |
| question shaped like a trophy | 3 | トロフィーの形をした質問 / FAIL_LIT | トロフィーの形をした問いかけ / FAIL_LIT | 賞の形をした問いかけ / FAIL_LIT | 賞の形を借りた問いかけ / PASS | 賞を通して投げかける問い / PASS | 賞という形で投げかける問い / PASS | - |
| greener grass | 1 | より青く見える芝生 / FAIL_LIT | 自分より恵まれて見える人の暮らし / PASS | 人の暮らしのほうが自分より良く見えること / PASS | 他人の暮らしのほうがよく見えること / PASS | 自分の暮らしよりよく見える他人の暮らし / PASS | 自分より恵まれて見える他人の暮らし / PASS | 人のもののほうがよく見えること / PASS |
| greener grass | 2 | より青々とした芝生 / FAIL_LIT | 他人のほうが恵まれているように見えること / PASS | 隣の芝生のほうが青く見えること / PASS | 他人のほうがよく見える状況 / THIN | 自分より恵まれて見える他人の暮らし / PASS | 人の暮らしのほうがよく見えること / PASS | - |
| greener grass | 3 | より青々とした芝生 / FAIL_LIT | 自分より恵まれて見える他人の暮らし / PASS | 人の暮らしのほうが自分よりよく見えること / PASS | 他人の暮らしのほうがよく見えること / PASS | より青々とした芝生 / FAIL_LIT | 他人の暮らしが自分よりよく見えること / PASS | - |

## held-out(各1rep、B0/X2/Cp/X2p)

| KP | B0 | X2 | Cp | X2p | 悪化(B0=PASSでX2/Cp/X2p=THIN/FAIL/FAIL_LIT) |
|---|---|---|---|---|---|
| rise above | ～より大きく聞こえる / PASS | ほかの声より大きく響く / PASS | ～より大きく響く / PASS | ひときわ大きく響く / PASS | なし |
| tiny bomb | 小さな爆弾 / PASS | 小さな爆弾 / PASS | 小さな爆弾 / PASS | 小型爆弾 / PASS | なし |
| work to do | やるべきこと / PASS | これから取り組むべきこと / PASS | まだ取り組むべきこと / PASS | まだやるべきこと / PASS | なし |
| become like porches | 玄関先のような場所になる / THIN | 近所の人が気軽に立ち寄って交流できる場所になる / PASS | 人が気軽に立ち寄り、交流できる場所になる / PASS | ベンチが人々の憩いや交流の場になる / PASS | なし |
| carry a decision's weight | 決定の重さを背負う / PASS | 決定の負担を背負う / PASS | 決定の重みを背負う / PASS | 決定の重みを背負う / PASS | なし |
| a door inside the pain | 痛みの中にある扉 / THIN | 苦しみの中に見えた、記憶へ戻る道 / THIN | 苦しみの中にある戻り道 / THIN | 悲しみの中に見つけた、思い出と向き合い直す道 / THIN | なし |
| one doorway among several | いくつかある入り口の一つ / PASS | いくつもあるアクセス手段の一つ / PASS | 複数あるアクセス手段の一つ / PASS | 複数あるアクセス手段の一つ / PASS | なし |
| inner timekeeper | 体内時計 / PASS | 体内時計 / PASS | 体内時計 / PASS | 体内時計 / PASS | なし |
| two different speeds | 二つの異なるペース / PASS | 旅行への意識と実際の旅行計画の変化の速さの違い / PASS | 異なる二つのペース / PASS | 異なるペースで進む二つの動き / PASS | なし |
| all it takes | 必要なのは～だけ / PASS | 必要なのは～だけ / PASS | 必要なのは～だけ / PASS | それだけで十分 / PASS | なし |

held-out 悪化: X2=なし Cp=なし X2p=なし(基準: 0)

## Stage 2 (non-R 54 KP x X2p 1rep) 対 B0(Trial_04 2rep) / Cp_t4(rep1)

未ラベル/欠落KP: なし

### strict(B0良い方rep基準)

- PASS->FAIL 0 / PASS->THIN 2 / THIN->FAIL 0 / THIN->PASS 0 / FAIL->PASS 0 / FAIL->THIN 0 / 変化なし(同順位) 52 / 計 54
  - [PASS->THIN] move in the other direction | B0=反対の方向に動く / 反対の方向に動く (PASS/PASS) | X2p=売れ行きは逆に下がった (THIN)
  - [PASS->THIN] supply chain | B0=商品が作られて消費者に届くまでの流れ / 商品が作られて届くまでの供給の流れ (PASS/PASS) | X2p=商品が作られて店に届くまでの流れ (THIN)

### lenient(B0悪い方rep基準)

- PASS->FAIL 0 / PASS->THIN 2 / THIN->FAIL 0 / THIN->PASS 1 / FAIL->PASS 2 / FAIL->THIN 0 / 変化なし(同順位) 49 / 計 54
  - [PASS->THIN] move in the other direction | B0=反対の方向に動く / 反対の方向に動く (PASS/PASS) | X2p=売れ行きは逆に下がった (THIN)
  - [PASS->THIN] supply chain | B0=商品が作られて消費者に届くまでの流れ / 商品が作られて届くまでの供給の流れ (PASS/PASS) | X2p=商品が作られて店に届くまでの流れ (THIN)
  - [THIN->PASS] pump one's fist | B0=こぶしを突き上げて喜ぶ / 自分の拳を突き上げる (PASS/THIN) | X2p=喜んでガッツポーズをする (PASS)
  - [FAIL->PASS] reach for someone's wallet | B0=人の財布に手を伸ばす / 誰かが自分の財布に手を伸ばす (FAIL/PASS) | X2p=財布を出してお金を払おうとする (PASS)
  - [FAIL->PASS] settle at | B0=～で取引を終える / ～で落ち着く (PASS/FAIL) | X2p=～で取引を終える (PASS)

X2p ラベル分布: {'PASS': 52, 'THIN': 2}
B0_t4 ラベル分布(出力単位): {'PASS': 105, 'THIN': 1, 'FAIL': 2}
Cp_t4 ラベル分布(rep1、n=54): {'PASS': 53, 'THIN': 1}
X2pがCp_t4より劣る(順位): 1件 / 優る: 0件 []
  - move in the other direction | Cp_t4=逆の動きをする (PASS) | X2p=売れ行きは逆に下がった (THIN)

X2p 残存THIN一覧(Stage 2): [('move in the other direction', '売れ行きは逆に下がった'), ('supply chain', '商品が作られて店に届くまでの流れ')]

Stage 2 全54KP一覧(KP | B0 rep1/rep2 | X2p | Cp_t4):
  - add up | つじつまが合う (PASS) ; つじつまが合う (PASS) | X2p=つじつまが合わない (PASS) | Cp_t4=つじつまが合う (PASS)
  - at a moment's notice | 急なときでもすぐに (PASS) ; とっさに (PASS) | X2p=とっさに (PASS) | Cp_t4=急な場面でも即座に (PASS)
  - behind the curtain | 舞台裏に (PASS) ; 舞台裏に (PASS) | X2p=舞台裏で動いている (PASS) | Cp_t4=舞台裏で (PASS)
  - brace yourself for | ～に備えて心構えをする (PASS) ; ～に備えて心構えをする (PASS) | X2p=～に備えて心の準備をする (PASS) | Cp_t4=～に備えて心の準備をする (PASS)
  - can't wait | 待ちきれない (PASS) ; 待ちきれない (PASS) | X2p=待ちきれない (PASS) | Cp_t4=待ちきれない (PASS)
  - carry the load | 荷物を運ぶ (PASS) ; 荷物を運ぶ (PASS) | X2p=必要な荷物を運ぶ役目を担う (PASS) | Cp_t4=荷物を運ぶ (PASS)
  - catch one's breath | 息を整える (PASS) ; 息を整える (PASS) | X2p=息を整える (PASS) | Cp_t4=息を整える (PASS)
  - center stage | 注目の中心 (PASS) ; 注目の中心 (PASS) | X2p=注目の的になる (PASS) | Cp_t4=注目の的になる (PASS)
  - fill in | ～を補う (PASS) ; 補う (PASS) | X2p=足りない部分を補う (PASS) | Cp_t4=補う (PASS)
  - fire the starting gun | スタートの号砲を鳴らす (PASS) ; スタートの合図を出す (PASS) | X2p=物事を動かし始める (PASS) | Cp_t4=～の開始を告げる (PASS)
  - give back gains | 上昇分を失う (PASS) ; 上昇分の一部を失う (PASS) | X2p=上げ幅を一部縮める (PASS) | Cp_t4=上げ幅を縮める (PASS)
  - give one's word | 約束する (PASS) ; 約束をする (PASS) | X2p=約束する (PASS) | Cp_t4=約束する (PASS)
  - give way | 崩れる (PASS) ; 崩れる (PASS) | X2p=崩れる (PASS) | Cp_t4=崩れる (PASS)
  - go cold | ぞっとする (PASS) ; ぞっとする (PASS) | X2p=ぞっとする (PASS) | Cp_t4=ぞっとする (PASS)
  - go out of one's way | わざわざ手間をかける (PASS) ; わざわざ～する (PASS) | X2p=わざわざ～する (PASS) | Cp_t4=わざわざ～する (PASS)
  - grow lighter | 軽くなる (PASS) ; 軽くなる (PASS) | X2p=気持ちが軽くなる (PASS) | Cp_t4=気が楽になる (PASS)
  - hold out one's hands | 自分の両手を差し出す (PASS) ; 自分の両手を差し出す (PASS) | X2p=自分の両手を差し出す (PASS) | Cp_t4=自分の手を差し出す (PASS)
  - in the spotlight | 注目を浴びている (PASS) ; 注目を浴びている (PASS) | X2p=注目を浴びている (PASS) | Cp_t4=注目を浴びている (PASS)
  - jump to conclusions | 早まった結論を出す (PASS) ; 早まって結論を出す (PASS) | X2p=早合点する (PASS) | Cp_t4=早合点する (PASS)
  - keep someone company | 誰かの話し相手をする (PASS) ; 人の相手をする (PASS) | X2p=人の相手をする (PASS) | Cp_t4=人と一緒にいて相手をする (PASS)
  - leap into action | すぐに行動を起こす (PASS) ; すぐに行動を起こす (PASS) | X2p=すぐに行動を起こす (PASS) | Cp_t4=すぐさま行動に移る (PASS)
  - letter of introduction | 紹介状 (PASS) ; 紹介状 (PASS) | X2p=紹介状 (PASS) | Cp_t4=紹介状 (PASS)
  - move in the other direction | 反対の方向に動く (PASS) ; 反対の方向に動く (PASS) | X2p=売れ行きは逆に下がった (THIN) | Cp_t4=逆の動きをする (PASS)
  - not the same picture | 同じ状況ではない (PASS) ; 同じ状況ではない (PASS) | X2p=同じ傾向ではない (PASS) | Cp_t4=同じような傾向ではない (PASS)
  - off the hook | 責任を問われずに済む (PASS) ; 責任を問われずに済む (PASS) | X2p=責任を免れている (PASS) | Cp_t4=責任を問われずに済む (PASS)
  - on a regular basis | 定期的に (PASS) ; 定期的に (PASS) | X2p=定期的に (PASS) | Cp_t4=定期的に (PASS)
  - on paper | 書面上では (PASS) ; 書面上では (PASS) | X2p=理屈の上では (PASS) | Cp_t4=理論上は (PASS)
  - on the throne | 王座に就いている (PASS) ; 王座に就いて (PASS) | X2p=トップの座を占める (PASS) | Cp_t4=王座に君臨している (PASS)
  - play a part | 役割を果たす (PASS) ; 役割を果たす (PASS) | X2p=一因となる (PASS) | Cp_t4=一因となる (PASS)
  - pull back | 取り下げる (PASS) ; ～を取り下げる (PASS) | X2p=いったん提供を取りやめる (PASS) | Cp_t4=いったん取り下げる (PASS)
  - pump one's fist | こぶしを突き上げて喜ぶ (PASS) ; 自分の拳を突き上げる (THIN) | X2p=喜んでガッツポーズをする (PASS) | Cp_t4=自分の拳を突き上げて喜ぶ (PASS)
  - put on hold | ～を保留にする (PASS) ; 保留にする (PASS) | X2p=いったん保留にする (PASS) | Cp_t4=いったん保留にする (PASS)
  - reach for someone's wallet | 人の財布に手を伸ばす (FAIL) ; 誰かが自分の財布に手を伸ばす (PASS) | X2p=財布を出してお金を払おうとする (PASS) | Cp_t4=誰かが自分の財布に手を伸ばして支払いの準備をする (PASS)
  - rise above the other voices | ほかの声よりも際立つ (PASS) ; ほかの声よりひときわ大きく聞こえる (PASS) | X2p=ほかの声よりひときわ大きく響く (PASS) | Cp_t4=ほかの人たちの声よりも大きく響く (PASS)
  - run on | ～に合わせて動く (PASS) ; ～に合わせて進む (PASS) | X2p=別々の時間軸で動いている (PASS) | Cp_t4=～の時間軸で進む (PASS)
  - settle at | ～で取引を終える (PASS) ; ～で落ち着く (FAIL) | X2p=～で取引を終える (PASS) | Cp_t4=～で取引を終える (PASS)
  - shine a light on | ～に光を当てる (PASS) ; ～に光を当てる (PASS) | X2p=～を浮き彫りにする (PASS) | Cp_t4=～に光を当てる (PASS)
  - shock someone's wallet | 人の財布に大きな打撃を与える (PASS) ; 人の財布に大きな打撃を与える (PASS) | X2p=人の財布に大きな打撃を与える (PASS) | Cp_t4=人の財布に大きな打撃を与える (PASS)
  - spread through the whole market | 市場全体に広がる (PASS) ; 市場全体に広がる (PASS) | X2p=市場全体に広まる (PASS) | Cp_t4=市場全体に広がる (PASS)
  - step out | 外へ出る (PASS) ; 外へ出る (PASS) | X2p=人が姿を現す (PASS) | Cp_t4=姿を現す (PASS)
  - stone video | 石の動画 (PASS) ; 石の動画 (PASS) | X2p=石を映した動画 (PASS) | Cp_t4=石を映した動画 (PASS)
  - supply chain | 商品が作られて消費者に届くまでの流れ (PASS) ; 商品が作られて届くまでの供給の流れ (PASS) | X2p=商品が作られて店に届くまでの流れ (THIN) | Cp_t4=商品が作られて店に届くまでの流れ (THIN)
  - take a sharp turn | 急展開する (PASS) ; 急展開する (PASS) | X2p=急展開する (PASS) | Cp_t4=急展開する (PASS)
  - take off an ai costume | AIの衣装を脱ぐ (PASS) ; AIの着ぐるみを脱ぐ (PASS) | X2p=AIの裏に人がいると明かす (PASS) | Cp_t4=AIの仮面を脱ぐ (PASS)
  - take the wheel | ハンドルを握る (PASS) ; ハンドルを握る (PASS) | X2p=車を運転する (PASS) | Cp_t4=車を運転する (PASS)
  - tariff-driven | 関税による (PASS) ; 関税による (PASS) | X2p=関税による (PASS) | Cp_t4=関税による (PASS)
  - the new normal | 新しい当たり前 (PASS) ; 新たな当たり前 (PASS) | X2p=新たな当たり前 (PASS) | Cp_t4=新しい当たり前 (PASS)
  - too broad a label | 広すぎるくくり (PASS) ; 範囲が広すぎる呼び名 (PASS) | X2p=ひとくくりにするには広すぎる呼び方 (PASS) | Cp_t4=範囲が広すぎる分類 (PASS)
  - turn on its head | ～をひっくり返す (PASS) ; それをひっくり返す (PASS) | X2p=期待をひっくり返す (PASS) | Cp_t4=～を逆転させる (PASS)
  - turn out | 結局～だと分かる (PASS) ; ～だとわかる (PASS) | X2p=結局～だと分かる (PASS) | Cp_t4=結局～だとわかる (PASS)
  - walk out | 歩いて外へ出る (PASS) ; 歩いて出ていく (PASS) | X2p=歩いて立ち去る (PASS) | Cp_t4=歩いて外へ出る (PASS)
  - weak link | 弱いつながり (PASS) ; 弱いつながり (PASS) | X2p=弱い関連 (PASS) | Cp_t4=弱い関連 (PASS)
  - weakly linked to higher income | より高い収入と弱い関連がある (PASS) ; より高い収入と弱い関連がある (PASS) | X2p=収入が高いことと少し関係している (PASS) | Cp_t4=より高い収入と弱い関連がある (PASS)
  - without asking for another promise | 新たな約束を求めずに (PASS) ; 新たな約束を求めずに (PASS) | X2p=改めて約束を求めずに (PASS) | Cp_t4=新たな約束を求めずに (PASS)

