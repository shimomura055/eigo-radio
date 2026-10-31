## 付録B: N5配線後のProduction実run(参考。同一本文、`KP-GENERALIZATION-N5-PRODUCTION-WIRING-01` M10、ev02/ev03)の phrase kind 最終候補

Production全工程(call1のP7＋B1 pool→SEL→pick cap7→GEN5/VER5/CHK5→救済→canonicalization QA→backfill)を通した実出力。比較の主表(Trial03のN5出力)とは別のB1抽出drawなので、**現行N5自体の実行間のばらつき**を示す。`origin=backfill`は補完工程で後から入った候補。

| run | 選定phrase → used_form | 日本語 | origin |
|---|---|---|---|
| untidi_a2/ev02 | `take points away from` → `take something away from` | 〜から何かを取り去る、差し引く | call1 |
| untidi_a2/ev02 | `hear it out` → `hear someone out` | 相手の言い分を最後まで聞く | call1 |
| untidi_a2/ev02 | `in Session` → `in session` | 会議や審理が開かれている | call1 |
| untidi_a2/ev02 | `something in the way` → `something in the way` | 邪魔になっているもの | call1 |
| untidi_a2/ev02 | `relied on` → `rely on` | 人や物を頼りにする | call1 |
| untidi_a2/ev02 | `turn the talk into` → `turn something into` | 何かを別の形や状態へ変える | call1 |
| untidi_a2/ev03 | `take points away from` → `take something away from` | 何かをあるものから取り除く、差し引く | call1 |
| untidi_a2/ev03 | `hear it out` → `hear someone out` | 人の話を最後まで聞く | call1 |
| untidi_a2/ev03 | `taking its job quite seriously` → `take something seriously` | 何かを重要なこととして真剣に扱う | call1 |
| untidi_a2/ev03 | `Not so fast` → `not so fast` | ちょっと待って、そう急ぐな | call1 |
| untidi_a2/ev03 | `take up space` → `take up space` | 場所を占める | call1 |
| untidi_a2/ev03 | `something in the way` → `something in the way` | 通行や行動の邪魔になっている状態 | call1 |
| untidi_a2/ev03 | `needs another look` → `need another look` | 改めて詳しく検討する必要がある | backfill |
| untidi_b1b/ev02 | `hear it out` → `hear someone out` | 相手の話を最後まで聞く | call1 |
| untidi_b1b/ev02 | `turn into an interrogation` → `turn into` | 別の状態や性質へと変わる | call1 |
| untidi_b1b/ev02 | `taking points away` → `take points away` | 点数を差し引いて評価を下げる | call1 |
| untidi_b1b/ev02 | `speaking for the side` → `speak for` | 人や集団を代表して意見を述べる | call1 |
| untidi_b1b/ev02 | `still on the job` → `on the job` | 勤務中で、仕事をしている状態 | call1 |
| untidi_b1b/ev02 | `relied on` → `rely on` | 人や物事を頼りにする | call1 |
| untidi_b1b/ev03 | `hear it out` → `hear someone out` | 人の話を最後まで聞く | call1 |
| untidi_b1b/ev03 | `turn into an interrogation` → `turn into` | 何か別のものへと変化する | call1 |
| untidi_b1b/ev03 | `end up taking points away` → `end up taking points away` | 最終的に点を差し引く | call1 |
| untidi_b1b/ev03 | `taking up space` → `take up space` | 空間を占める | call1 |
| untidi_b1b/ev03 | `still on the job` → `on the job` | 仕事中である | call1 |
| untidi_b1b/ev03 | `in Session` → `in session` | 裁判や会議などが開かれ、進行中である | backfill |
| untidi_b1b/ev03 | `in the way` → `in the way` | 邪魔になり、行動や進行を妨げる | backfill |
| melos_a2/ev02 | `in your place` → `in someone's place` | 人の代わりとして | call1 |
| melos_a2/ev02 | `pulled him under` → `pull someone under` | 人を水中へ引き込む | call1 |
| melos_a2/ev02 | `rose above everyone's voices` → `rise above something` | 音が他の音を上回って響く | call1 |
| melos_a2/ev02 | `lost my trust in you` → `lose one's trust in` | 人に対する信頼を失う | call1 |
| melos_a2/ev02 | `win such trust` → `win trust` | 信頼を得る | call1 |
| melos_a2/ev02 | `For once` → `for once` | 今回に限っては | call1 |
| melos_a2/ev02 | `lose his life instead` → `lose one's life` | 命を落とす | call1 |
| melos_a2/ev03 | `lost my trust in you` → `lose one's trust in` | 人への信頼を失う | call1 |
| melos_a2/ev03 | `pulled him under` → `pull someone under` | 人を水中へ引きずり込む | call1 |
| melos_a2/ev03 | `rose above everyone's voices` → `rise above something` | 〜より際立って聞こえる | call1 |
| melos_a2/ev03 | `lose his life` → `lose one's life` | 命を失う、死ぬ | call1 |
| melos_a2/ev03 | `kept his eyes on them` → `keep one's eyes on` | 人を見続け、注意を向けておく | call1 |
| melos_a2/ev03 | `win such trust` → `win trust` | 信頼を勝ち取る | call1 |
| melos_a2/ev03 | `in your place` → `in someone's place` | 人の代わりに、身代わりとして | call1 |

同runで落ちた候補(段・理由): 
- untidi_a2/ev02: `make life work`(n5_select) / `gets heated`(canonicalization_qa) / `did not test whether`(n5_select) / `make daily life work`(n5_select) / `rush to say`(n5_select)
- untidi_a2/ev03: `make life work`(n5_select) / `gets heated`(canonicalization_qa) / `relied`(canonicalization_qa) / `make daily life work`(n5_select)
- untidi_b1b/ev02: `cannot simply be applied`(n5_select) / `gets heated`(canonicalization_qa) / `did not test whether`(n5_select) / `prevents missed doses`(n5_select) / `participant's own explanation`(n5_select)
- untidi_b1b/ev03: `make life work`(n5_select) / `applied to every household`(n5_select) / `taking its job quite seriously`(n5_generalize) / `gets heated`(canonicalization_qa) / `cannot simply be applied to`(n5_select)
- melos_a2/ev02: `held out`(n5_select) / `blocked his way`(n5_select)
- melos_a2/ev03: `ordered his death`(n5_select) / `left you to die`(n5_select)

## 付録C: N5(現行cap7・A案cap10)から外れた表現の実測(display_formはGEN5→VER5→CHK5の実出力)

「pool/keep/cap10」=E2プールに出現したrep数 / SEL keepだったrep数 / A10 cap10に入ったrep数。価値は担当者の暫定評価。

| 記事 | source_span | display_form (GEN5出力) | 日本語の意味 | pool/keep/cap10 (rep数) | SEL多数ラベル | 価値(暫定)と所見 |
|---|---|---|---|---|---|---|
| untidi_b1b | `gets heated` | `get heated` | 感情的になり、議論などが白熱する | 13/13/0 (N=13) | C/collocation/upper_intermediate | 高: 議論が白熱するという会話・ニュースで頻出のcollocation。cap10では0/13repで入らない(現行N5のTrial03出力には入っている)。Production実runではcanonicalization QA再判定key不一致で落ちていた(OPEN-633で是正済み) |
| untidi_b1b | `In other words` | `in other words` | 言い換えると、つまり | 13/13/0 (N=13) | C/fixed_phrase/easy | 中: 談話標識。汎用性は高いが基礎的でSELはeasy判定。cap10では0/13rep |
| untidi_b1b | `No wonder` | `no wonder` | 当然だと思うこと、驚くにあたらないこと | 13/13/0 (N=13) | C/fixed_phrase/easy | 中: 会話表現として有用。cap10では0/13rep |
| untidi_b1b | `in a way` | `in a way` | ある意味では、ある点では | 13/13/0 (N=13) | C/fixed_phrase/easy | 中: 『ある意味では』。基礎的な固定表現。cap10では0/13rep |
| untidi_b1b | `on the job` | `on the job` | 勤務中で、仕事をしている状態で | 11/11/0 (N=13) | C/fixed_phrase/upper_intermediate | 中: 『勤務中』。cap10では0/13rep(現行N5は`still on the job`を選定する回がある) |
| untidi_b1b | `taking its job quite seriously` | `take something seriously` [MODIFIER_DROPPED_OK] | 何かを重要なものとして真剣に扱う | 9/9/0 (N=13) | C/collocation/upper_intermediate | 中: take something seriouslyの形で汎用。5語で本文形が長い |
| untidi_a2 | `Not so fast` | `not so fast` | 急ぐな、まだそう決めるな | 11/11/1 (N=11) | C/fixed_phrase/easy | 高: 会話の制止表現。cap10入りは1/11rep(現行N5のTrial03出力には入っている) |
| untidi_a2 | `take up space` | `take up space` | ある場所を占有して空間をふさぐ | 11/11/2 (N=11) | C/phrasal_verb/easy | 中: 場所を取るという汎用句動詞的表現。cap10入りは2/11rep |
| untidi_a2 | `No wonder` | `no wonder` | 〜なのも不思議ではない | 11/11/0 (N=11) | C/fixed_phrase/easy | 中: cap10入りは0/11rep |
| untidi_a2 | `In a way` | `in a way` | ある意味では、またはある点から見れば | 11/11/3 (N=11) | C/fixed_phrase/easy | 中: cap10入りは3/11rep |
| untidi_a2 | `in sight` | `in sight` | 視界に入って、見える状態に | 10/10/0 (N=11) | C/fixed_phrase/upper_intermediate | 中: 見える範囲にある。cap10入りは0/11rep(b1bでは12/13rep) |
| untidi_a2 | `leave it out` | `leave something out` | 物をしまわず外に出したままにする | 11/9/0 (N=11) | C/phrasal_verb/easy | 中: leave out系。cap10入りは0/11rep(b1bでは9/13rep)。記事主題の核(`Leaving Things Out`)に近い |
| melos_a2 | `waited for a reply` | `wait for` | 何かが来るのを待つ | 2/2/0 (N=2) | C/phrasal_verb/easy | 低: wait for。基礎語の自由な組合せに近い |
| melos_a2 | `blocked his way` | `block someone's way` | 人の進路をふさぐ | 2/1/0 (N=2) | C/collocation/upper_intermediate | 中: block someone's way。cap10入り0/2rep |
| melos_a2 | `turned around` | `turn around` | 向きを変えて後ろを向く | 1/1/0 (N=2) | C/phrasal_verb/easy | 低: turn around。基礎的な句動詞 |
| melos_a2 | `kept his eyes on them` | `keep one's eye on` | 視線を注ぎ続ける | 1/1/0 (N=2) | C/collocation/upper_intermediate | 中: keep one's eye on。現行N5のTrial03出力には入っている |
| melos_a2 | `For once` | `for once` | 今回に限って、いつもとは違い | 1/1/0 (N=2) | C/fixed_phrase/upper_intermediate | 中: 『今回に限って』。固定表現。cap10入り0/2rep |
| moon_b1b | `In other words` | `in other words` | 別の言い方を示し、前の内容を言い換える | 2/2/0 (N=2) | C/fixed_phrase/easy | 中: 談話標識。cap10入り0/2rep |
| moon_b1b | `no need for` | `no need for` | 必要がないこと | 2/2/0 (N=2) | C/fixed_phrase/easy | 中: no need for something。cap10入り0/2rep |
| moon_b1b | `For now` | `for now` | 今のところ、当面は | 2/2/0 (N=2) | C/fixed_phrase/easy | 中: 『当面は』。cap10入り0/2rep |
| moon_b1b | `quite a lot of` | `quite a lot of` | かなり多くの量や数があること | 2/2/0 (N=2) | C/fixed_phrase/easy | 低: 量の基礎表現 |
| moon_b1b | `too soon to say` | `too soon to say` | 判断を下すにはまだ早い | 2/1/0 (N=2) | C/fixed_phrase/easy | 中: 『まだ何とも言えない』。記事の論調に関わる表現。cap10入り0/2rep |
| surname_b1b | `got married` | `get married` | 結婚して夫婦になる | 2/2/0 (N=2) | C/collocation/easy | 低: get married。基礎的 |
| surname_b1b | `again and again` | `again and again` | 何度も繰り返して | 2/2/0 (N=2) | C/fixed_phrase/easy | 中: 繰り返しを表す固定表現。cap10入り0/2rep |
| surname_b1b | `got very upset` | `get upset` [MODIFIER_DROPPED_OK] | 動揺したり腹を立てたりする | 2/1/0 (N=2) | C/collocation/easy | 低: get upset。基礎的 |
| surname_b1b | `without getting too close` | `without getting too close` | 深入りしすぎる、親しくなりすぎる | 2/1/0 (N=2) | C/collocation/upper_intermediate | 低: VER5でrevertされ汎用形にならず、日本語訳も`without`を反映しない(『深入りしすぎる』) |
| surname_b1b | `decide for themselves` | (脱落 n5_generalize: 一般形の組立に失敗: lemma'oneself'が本文の語'themselves'の語形違いでない) | — | 2/2/1 (N=2) | C/fixed_phrase/upper_intermediate | 高: decide for oneself。A案cap10に入った回でGEN5が`oneself`再帰形のlemma不一致で組立失敗(QA脱落)。現行N5でも同じGEN5で同様に落ちる |
| surname_b1b | `get much time to myself` | (脱落 n5_generalize: 一般形の組立に失敗: lemma'oneself'が本文の語'myself'の語形違いでない) | — | 1/1/1 (N=2) | C/collocation/upper_intermediate | 中: time to oneself。同様にGEN5組立失敗(QA脱落) |
