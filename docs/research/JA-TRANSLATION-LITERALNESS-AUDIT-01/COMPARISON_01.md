# 調査④ 実データ照合 (COMPARISON_01)

管理ID=JA-TRANSLATION-LITERALNESS-AUDIT-01 / 委任_01B / 2026-10-31。調査のみ・API 0・LLM API呼出0・SSOT編集0。判定者=LLM agent(Sonnet)自身が読んで判定(外部LLM呼出なし)。証跡は全て `ev01/`。

## 0. 結論(先に)
1. **公開済みEnd User 10記事の「英語に対応する日本語訳」全1,164ユニットを100%照合した**(層化抽出ではなく全数。第1判定)。内訳: 日本語が表示される1,132件+日本語が非表示(`ja_align`安全側null)の32件。第2判定(順序・ID再シャッフル、第1判定非表示)は397件。
2. **問題は「出所」で明確に分かれる**。`approved_*`(X=R2日本語台本、Y=Voice日本語原稿)は表示ありの453件中100件(22.1%)が不適切(分類1〜5)、うち中以上64件(14.1%)。**Std限定では表示あり213件中75件(35.2%)、中以上55件(25.8%)**。一方`generated`(英文からの翻訳)は310件中0件(0.0%)。学習項目(KP/gloss/Vocab/文法の訳)は359件中12件(3.3%、全て軽)。
3. 問題の中心は**分類3「複数英文が1つの日本語文に統合され文単位の対応が取れない」**(64件=不適切の57%)。原因は設計: 日本語原稿が先にあり、Std英文はAdvをさらに簡易化(文を分割)したものなのに、**StdとAdvに同一の日本語原稿を並置**している(INVENTORY_01 G2)。**重大(意味の誤り・事実情報の追加)は第1判定0件**(第2判定で境界1件=後述)。
4. **ユーザー問題①②は実データで確認できた**(§4)。①=Std`ai_chat_sponsored_persuasion`の「It sat…/At least…/In fact…」3英文が日本語1文(2断片)。②=「They used the share…」と、ユーザー引用の範囲外にある直後の「People who did not think…」の2文が1文に統合され、「指標なのだ」と名詞化(英文4文目に内容は存在するため『原文にない事実の追加』ではなく分類3+軽2。委任_01Aと同結論)。
5. **approved(R2由来)は問題率が高く、generated(翻訳)は0%**。ただしこれは「translate出力が全て完璧」ではなく、(a)generatedは1文=1訳(統合禁止+LLM校閲+数値照合)で構造的に統合が起きない、(b)approvedは**日本語が原本で英文がその派生**という逆向きの関係、が理由。

## 1. 方法と限界(固定したrubric)
- rubric=`COMPARISON_RUBRIC_01.md`(判定開始前に固定)。分類1〜6=ユーザー原文§6、重大度=重大(意味の誤り・情報追加)/中(対応消失・欠落)/軽(ニュアンス)。**分類3(統合)は定義上すべて中**。そのうち「内容は全部含まれ文境界のみ不一致=mf」「圧縮・欠落を伴う=cmp」「隣接群と食い違う=shift」をnoteで区別した(§3.3)。
- 単位=End Userページで英文の隣に表示される1ブロック(story/comment/preview/oneline=`ja_align`群、kp/gloss/vocab語句、vocab/grammar英文1文、タイトル)。抽出=`ev01/extract_pairs_01.py`→`pairs_all_01.jsonl`(1,164行)。
- 第1判定=blind(`ev01/blind/p1_*.txt`: ID・訳種別・英文・日本語のみ。ja_source/Family/Level/align/過去所見を伏せ、seed固定で順序・IDを無作為化)。判定記録=`judge_p1.txt`+`judge_p1_overrides.txt`、結合=`merge_p1_01.py`→`judged_p1.json`。
- 第2判定=`ev01/blind/p2_*.txt`(397件: 第1判定で6以外の全113件+第1判定=6の層別無作為284件[各層最大8]。ID・順序を再シャッフル、第1判定・理由は非表示)。結果=`judge_p2.txt`、一致率=`agree_01.py`。
- **限界(重要)**: (i)判定者は同一モデル・同一セッション。第2判定は独立評価者ではなく自己一貫性の確認であり、一致率の高さ(§5)は「rubricが機械的に適用できた」ことを示すだけで、人間評価との一致を保証しない。Fable抜き取り用ブラインド20件(`FABLE_BLIND_SHEET_20.md`+キー`FABLE_BLIND_KEY_20.json`)で外部確認が必要。(ii)文体の強調語(「必死に」「なかなか」等)は軽微な付加として分類しない運用。(iii)分類3の「軽/中」はrubric定義に従い全て中。(iv)解説文に埋め込まれた対訳は正規表現で抽出できた83件のみ確認(§6)で、抽出できなかった分の総数は不明(**未確認**)。(v)日本語非表示の32件は判定不能=「未表示」として別計上し、PASSとは扱わない。

## 2. 母集団(全数)
公開済みEnd Userページ=origin/main `user_test/*/enduser/` の10記事(X5・Y2・Z3)。

| Family | 記事 |
|---|---|
| X | ai_chat_sponsored_persuasion / jwst_mystery_emission_line / meta_waddle_world / moon_shrinking_reselect / untidiness_family_resource |
| Y | production_redelivery_fee_03 / production_surname_choice_01 |
| Z | in_a_grove(日本語訳なし。INVENTORY G6) / melos_kphr_evidence_r3 / yuki_onna |

| 訳種別 | ユニット数 | うち日本語非表示 |
|---|---|---|
| story(本文) | 695 | 32 |
| comment | 58 | 0 |
| preview | 19 | 0 |
| oneline | 23 | 0 |
| title | 10 | 0 |
| kp_ja / gloss / vocab_meaning | 31 / 148 / 84 | 0 |
| vocab_sentence / grammar_sentence | 84 / 12 | 0 |
| **合計** | **1,164** | **32** |

Family×Level×訳種別×ja_source別の件数・分類分布・重大度の全表=`ev01/aggregate_tables_01.md`(表F)。各層の内訳は全数照合のため「各層≥20文」の要件は、層の母数が20未満の層は全数(母数不足)、20以上の層も全数を満たす。

## 3. 結果(第1判定、全数)
### 3.1 全体(表示あり1,132件)
| 分類 | 件数 |
|---|---|
| 6 適切 | 1,019 |
| 1 情報欠落 | 1 |
| 2 情報追加 | 4 |
| 3 要約・統合で対応消失 | 64 |
| 4 意味・ニュアンス変化 | 29 |
| 5 自然だが対訳として不適切 | 15 |
| 日本語非表示(未表示) | 32 |

重大度: **重大0件**、中64件(分類3全件。未表示の32件を「中」に含めるなら96件)、軽49件(分類1×1・2×4・4×29・5×15)。問題(広義)=分類1〜5=113件/1,132件(10.0%)。未表示を含めると145/1,164(12.5%)。

### 3.2 出所別(ja_source)
| 出所 | 全件 | 表示あり | 未表示 | 6適切 | 1 | 2 | 3 | 4 | 5 | 問題(表示あり内) | 中以上 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| approved_ja_manuscript(X本文) | 337 | 309 | 28 | 246 | 1 | 3 | 35 | 11 | 13 | 63 (20.4%) | 35 (11.3%) |
| approved_ja_original_in_dev_page(Y本文) | 148 | 144 | 4 | 107 | 0 | 0 | 29 | 6 | 2 | 37 (25.7%) | 29 (20.1%) |
| **approved 計** | 485 | 453 | 32 | 353 | 1 | 3 | 64 | 17 | 15 | **100 (22.1%)** | **64 (14.1%)** |
| generated(翻訳: Z本文+X/Y Adv補助+X Std In One Line) | 310 | 310 | 0 | 310 | 0 | 0 | 0 | 0 | 0 | **0 (0.0%)** | 0 |
| 学習項目(kp/gloss/vocab/grammar) | 359 | 359 | 0 | 347 | 0 | 1 | 0 | 11 | 0 | 12 (3.3%) | 0 |
| title(題の日英) | 10 | 10 | 0 | 9 | 0 | 0 | 0 | 1 | 0 | 1 | 0 |

**approved vs generated: 本文系で22.1%対0.0%。差は構造的**(§0-5)。

### 3.3 Level別(approved本文)と分類3の内訳
| 区分 | 表示あり | 問題(広義) | 中以上 |
|---|---|---|---|
| approved / **Std** | 213 | 75 (35.2%) | 55 (25.8%) |
| approved / **Adv** | 240 | 25 (10.4%) | 9 (3.8%) |

StdがAdvの約3.4倍。Std英文はAdv英文をさらに簡易化し文が増える(X: Std EN 214文/Adv 175文/共通JA 188文[。！？で計数。委任_01Aは171文と計数=数え方の差]、Y: Std EN 105文/Adv 79文/共通JA 74文)ため、日本語1文に英文2〜3文が当たる。分類3の64件の内訳(note): **mf(内容は保持・文境界のみ不一致)55件**、cmp(圧縮・欠落を伴う)3件、shift(隣接群と食い違い、日本語断片が文の途中から始まる/次の英文の内容を先食い)3件、その他3件(2文→1文に統合し一部要素脱落)。すなわち**情報の欠落を伴う深刻な統合は少数で、多くは「1対1で英文と照合できない」対応消失**。ユーザーの要求(英文と照合できること)に照らすと問題であることに変わりはない。

文数×出所: 英文2文以上の群は approved(X)38群中31(82%)・approved(Y)29群中29(100%)が不適切、英文1文の群は X 271群中32(12%)・Y 115群中8(7%)、generated 310群中0。

### 3.4 記事別(approved本文の群)
| 記事 | Level | 群 | 問題(広義) | 中以上 | 未表示 |
|---|---|---|---|---|---|
| x_ai_chat_sponsored_persuasion_01 | std | 29 | 11 (38%) | 8 | 0 |
| 同 | adv | 30 | 7 (23%) | 4 | 0 |
| x_jwst_mystery_emission_line_01 | std | 35 | 9 (26%) | 7 | 5 |
| 同 | adv | 35 | 2 (6%) | 0 | 0 |
| x_meta_waddle_world_01 | std | 33 | 6 (18%) | 3 | 5 |
| 同 | adv | 33 | 0 (0%) | 0 | 1 |
| x_moon_shrinking_reselect_01 | std | 35 | 12 (34%) | 8 | 5 |
| 同 | adv | 35 | 4 (11%) | 0 | 2 |
| x_untidiness_family_resource_01 | std | 36 | 9 (25%) | 5 | 10 |
| 同 | adv | 36 | 3 (8%) | 0 | 0 |
| y_production_redelivery_fee_03 | std | 34 | 14 (41%) | 13 | 2 |
| 同 | adv | 34 | 4 (12%) | 3 | 0 |
| y_production_surname_choice_01 | std | 40 | 14 (35%) | 11 | 2 |
| 同 | adv | 40 | 5 (12%) | 2 | 0 |

(全7記事でStdがAdvを上回る。問題率の範囲: Std 18〜41%・Adv 0〜23%。)

### 3.5 具体例(各分類)
(代表例。全件は`ev01/judged_p1.json`、サンプル=`ev01/examples_01.md`)
- **分類1 情報欠落**(軽、1件): Std`meta_waddle_world`「Your smartphone is already like a packed train at rush hour.」→「スマホの中は、すでに満員電車だ。」(rush hour脱落、simile→断定)。※1件のみ。「各分類≥2例」は分類1のみ満たせない。
- **分類2 情報追加**(軽): Adv`ai_chat`「“We couldn’t confirm a difference” and “there is no effect” do not mean the same thing.」→「…同じではないからだ。」(因果「からだ」を追加。前の日本語文の続きを訳として表示している)。Std`meta_waddle_world`「Meta’s “Waddle World” is an AI pet app in the Philippines.」→「フィリピン向けに提供された…」(「向けに」)。Z`in_a_grove`gloss「sink into the darkness」→「死の闇へ沈んでいく」(「死の」)。
- **分類3 要約・統合**(中): Std`moon_shrinking`「Insulation in a house keeps heat from getting out. This rock layer may have made it harder for heat inside the Moon to get out.」→「家の断熱材が熱を逃がしにくくするように、月の内部の熱も逃げにくくなったのかもしれない。」(2文→1文、主語"This rock layer"脱落、語順逆転)。Std`jwst`「The authors used the line’s absence…a measure of the line’s features.」→「…等価幅の下限を7620 Åと見積もりました。」(次のEN文「at least 7,620 Å」の内容を先食い=shift)。Y Std`redelivery_fee`の3文→1文(「結局は対面で受け取ることもある」は表示英文3文目に無い)。
- **分類4 意味・ニュアンス変化**(軽): Std`moon_shrinking`「But it does not need beauty cream.」→「美容液の出番ではない」(creamとserum)。Std`jwst`「…narrow down the source.」→「相手を絞り込む」(sourceが相手に)。KP gloss「sponsored」→「広告主に宣伝されている」(定訳「スポンサー付き」から外れる)。Z`melos`題「The Three-Day Promise.」→「走れメロス」(題が対応しない)。
- **分類5 自然だが対訳として不適切**(軽): Std`ai_chat`「People can think, “This is an ad,” and still think, “But I want it.”」→「『広告だな』と思いながら、『でも欲しい』は起こりうる。」(主語people消失)。Std`untidiness`「Don’t call it wrong just because it is out.」→「出ているという理由だけで、問答無用の退場処分にしない。」(退場処分の比喩+問答無用)。Adv`moon`「These aren’t figures measured under the same conditions.」→「同じ条件で測った数字同士の勝負ではないのだ。」。
- **日本語非表示**(未表示32): Std`untidiness` std_19 の6群が全て日本語なし、Std`moon` std_16 の5群など(`ev01/pairs_all_01.jsonl`の`unaligned`)。

## 4. ユーザー問題①②の同記事全文照合(Std/Adv、全件)
全群の表=`ev01/AI_CHAT_FULL_01.md`(Std 29群・Adv 30群)。要点:
- **①(Std std_15 g5+g6)**: EN3文「It sat at an advice desk like a helpful guide. / At least, that was how it seemed. / In fact, it was also doing the job of a salesperson.」↔JA「相談カウンターに座っているのは、親切な案内役。と思いきや、実は営業担当も兼務している、というわけだ。」(1文を2群に分割、2つ目が「と思いきや」で始まる断片)。主語"it(AI)"が「座っているのは」に、"At least, that was how it seemed"が「と思いきや」に、"also doing the job of a salesperson"が「兼務」に意訳。**分類3(中)**。Advも同様(adv_14 g6+g7、"or so it seemed"が次群へ移動)。
- **②(Std std_17 g4+g5 / Adv adv_16 g4+g5)**: ユーザー原文の引用英文は3文(In the experiment…/ The researchers asked them…/ They used the share…)だが、**記事の実データではその直後に4文目「People who did not think the advice favored one product were also counted as people who missed the sales pitch.」(`std_17-s031`)がある**。日本語「…その回答の中でスポンサー商品が占める割合を使い、偏りを感じなかった人も『見抜けなかった』扱いで集計した指標なのだ。」は英文3文目+4文目の2文を1文に統合したもの(`ja_align` g5=[s030,s031])。したがって**ユーザー引用の3文の範囲だけ見ると『原文にない情報』に見えるが、実データでは英文4文目の訳であり、純粋な情報追加ではない**(委任_01Aの結論と一致)。ただし、英文2文→日本語1文の統合に加え、「指標」という名詞化(英文に無い言い方)と「〜のだ」が付く。**分類3(中)+副因2(軽)**。ユーザーが実画面で見た群の境界は未確認。
- 同記事の同種の問題: g1(2文→1文+引用台詞が別内容「売り込み発見」)、g7(2文→1文)、g8(3文→1文)、std_17 g4/g8、std_19 g1(因果「からだ」追加)、g4(主語消失)ほか。Std 11/29群(38%)、Adv 7/30群(23%)が不適切。

## 5. 第2判定(自己一貫性の確認)
- 対象397件(第1判定で6以外113件+6の層別無作為284件)。
- 分類一致 392/397 = 98.7%。適切/不適切の2値一致 396/397 = 99.7%(κ=0.994)。中以上の2値一致 393/397 = 99.0%(κ=0.962)。
- 不一致5件=分類3↔5が3件(文統合か意訳か)、3↔2が1件(`jwst`の「下限7620 Å」先食いを、第2判定は"情報追加=重大"と判定。第1判定は"先食い(shift)=中"。**重大の境界1件**)、6→3が1件。
- **注意**: 同一モデル・同一セッションのため独立評価ではない。人間(Fable)抜き取りが必要(`FABLE_BLIND_SHEET_20.md`)。一致率の高さをrubricの客観性の証明として扱ってはならない。

## 6. 解説文に埋め込まれた対訳(補足)
Vocab解説・文法解説の本文中の「英語(日本語訳)」型を正規表現で抽出して全件確認(`ev01/extract_embedded_01.py`→`pairs_embedded_01.json`): **抽出83件、不適切0件**(多くはコロケーション例の語句訳であり、記事本文の対訳ではない)。抽出できなかった表記の対訳は**未確認**(総数不明)。

## 7. 事実と推定の分離
- **実データで確認した事実**: 公開済み10記事全ユニットの上記数値。StdとAdvで日本語原稿が同一(X5記事・Y2記事すべて「JA同一=True・EN同一=False」)。`generated`は310件中0件が不適切(rubric範囲)。
- **他記事・今後の記事への推定(未検証)**: X/Yの新記事も同経路(`attach_translations`)で生成されるため、Stdで同様の統合が起きると推定される(構造的要因のため確度は高いが、個別記事の実測ではない)。Zは翻訳経路(`generated`)のため問題が出にくいと推定される(Zの公開済み3記事のうち実測は2記事)。
- **未確認**: 実機での見え方(連動ハイライト時に日本語がどの程度対応して見えるか)、ユーザーが実画面で見た群の境界(②の見え方)、ユーザー向け画面での未表示32件の見え方。

## 8. 証跡
`ev01/`: `pairs_all_01.jsonl`(全1,164件)、`blind/`(p1_*, p2_*)、`key_p1.json`/`key_p2.json`、`judge_p1.txt`/`judge_p1_overrides.txt`/`judge_p2.txt`、`judged_p1.json`/`judged_p2.json`、`aggregate_tables_01.md`、`AI_CHAT_FULL_01.md`、`examples_01.md`、`pairs_embedded_01.json`、`FABLE_BLIND_SHEET_20.md`/`FABLE_BLIND_KEY_20.json`、各生成script。
