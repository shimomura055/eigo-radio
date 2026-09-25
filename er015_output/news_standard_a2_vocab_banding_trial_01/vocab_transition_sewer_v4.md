# vocab_transition_sewer_v4.md — Sewer: Advanced → Standard v3 → Standard v4
# 語彙遷移表(Sonnet目視、根拠1行ずつ。最終判定はFable/ユーザー)

対象: `a1_advanced_sewer.md`(Advanced、改変禁止)→
`a2v3_standard_sewer.md`(Standard v3、既存Trial成果物、改変禁止)→
`a2v4_standard_sewer.md`(Standard v4、本Trial新規生成)。
帯: A(rank≤3,000、最頻出)/ B(3,001–5,000)/ C(5,001–10,000)/
D(rank>10,000、20,000超の表外語含む)。rank=Noneは表外(20,000超)。
機械集計は`vocab_bands_sewer_all.json`/`vocab_bands_sewer_evaluate.md`
(帯別)、`fact_diff_machine_sewer.json`(固有名詞/数値/否定・scope語)を
根拠に、本ファイルは語単位の意味・自然さ判定をSonnetが目視で行う。

4分類:
- **そのまま残った**: 同じ語(表層形の揺れは許容)がAdvanced→v3→v4を
  通じて保持された。
- **自然に置換**: より平易/高頻度な語・自然な言い換えに変わった。
- **不自然に置換**: 文法的・語法的にぎこちない、または不自然な言い回し。
- **難語→別の難語**: 難語が別の難語(同等かむしろ頻度が低い語)に
  交換されただけで、真の簡略化になっていない。

## A. ユーザー指定9語(+関連語)

| # | Advanced語(帯) | v3の表現(帯) | v4の表現(帯) | 判定 | 根拠 |
|---|---|---|---|---|---|
| 1 | municipalities (D, rank11073) | towns (A, rank580)×2 | 1回目: "towns or cities"(A) / 2回目: "local governments"(A) | **自然に置換**(ただしv4内で表現が不統一) | v3は2箇所とも"towns"で統一。v4は1回目"towns or cities"(原文に無い"cities"を追加、意味をわずかに拡張)、2回目"local governments"(より専門的)と、同一語に対しv4内で2通りの訳語が混在。読者が同一概念だと認識しにくい可能性(§Fact drift候補)。 |
| 2 | installation (C, rank5508) | "It still needs **putting in**, checks, and cleaning."(putting=A) | "It still needs to be **put in**, checked, and cleaned."(put=A) | **自然に置換**(型はv3と同一、ただし文法はv4で改善) | 名詞"installation"を句動詞"put in"へ置換する型はv3から変化なし(ユーザーが確認したかった「不自然な一語置換の解消」は語選択の面では未達成=同じ選択を再現)。ただしv3は"putting in, checks, and cleaning"(動名詞+名詞+動名詞の混在で文法的に不揃い、既存効果Trial REPORTで「やや不自然な句」と指摘)、v4は"put in, checked, and cleaned"(過去分詞3つで統一)と、文法的な自然さはv4の方が高い。 |
| 3 | inspections (C, rank5694) | "checks"(A, rank487) | "checked"(A, rank487の動詞形) | **自然に置換** | v3/v4とも名詞"inspections"を回避し平易な"check"系の語に言い換え。型はv3と同じ。 |
| 4 | artery ("main artery", D, rank12006) | "main artery"(D)保持×2 | "main artery"(D)保持×2 | **そのまま残った**(意図的な比喩保持) | Prompt指示「key metaphorは保持可」に該当する記事の中心比喩。Advanced/v3/v4で完全に同一語のまま、比喩の直喩("like a hidden/unseen main artery")構文も維持。 |
| 5 | wastewater (D, rank18216) | "wastewater"(D)保持(本文) | 本文: "wastewater"(D)保持 / **タイトルのみ** "Household Wastewater"→"Water from Homes"に置換 | 本文: **そのまま残った** / タイトル: **自然に置換**だが本文と不統一 | 本文中の"treats/clean wastewater near each home"はAdvanced/v3/v4で一貫して"wastewater"のまま。しかしv4はタイトルだけ"Wastewater"を避けて"Water from Homes"にしており、タイトルと本文で難易度基準が食い違う(v1/v3のタイトルはいずれも"Household Wastewater"のまま)。 |
| 6 | septic ("septic tank(s)", D, 表外) | "septic"保持×4 | "septic"保持×4 | **そのまま残った** | 記事の主題を成す技術用語(引用符付きで導入)。必須技術語としてAdvanced/v3/v4で完全一致。 |
| 7 | collects (A, rank2335) | "**gathers**"(B, rank4530) | "**gathers**"(B, rank4530) | **難語→別の難語**(v3から変化なし) | "collects"はもともと帯A(非常に平易)。v3がより頻度の低い"gathers"へ交換したのは既存Trial(NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01 REPORT)で「単なる語の交換、真の簡略化ではない」と指摘済み。v4は"gathers"をそのまま再生成しており、v4の「自然さ優先・不要な置換をしない」指示はこのケースを解消できなかった。 |
| 8 | distant (C, rank5212)×2 | "**faraway**"(D, 表外)×2 | "**faraway**"(D, 表外)×2 | **難語→別の難語**(v3から変化なし、むしろ頻度は悪化) | v3の"distant→faraway"は既存Trialで既知の問題(farawayは20,000語表にも入らないほど低頻度)。v4は一言一句同じ"faraway treatment plant"/"faraway plant"を再生成しており、全く解消されていない。 |
| 9 | installation→putting in (#2と同一事象) | 上記#2参照 | 上記#2参照 | (#2に統合) | ユーザー指定の「installation→putting in」はAdvanced→v3の変化であり、v4はv3のputting inを踏襲(#2参照)。 |

### 追加確認: invisible → hidden/unseen(ユーザー明示指定外だが最重要の新規発見)

| Advanced語(帯) | v3の表現(帯) | v4の表現(帯) | 判定 | 根拠 |
|---|---|---|---|---|
| invisible (C, rank6153) | "**hidden**"(A, rank2837) | "**unseen**"(D, rank12884) | v3: **自然に置換**(良好) / v4: **難語→別の難語(悪化)** | v3はinvisible(C)→hidden(A)で明確な簡略化に成功。v4はinvisible(C)→unseen(D)で、Advanced本体より難しい語に置換してしまっている(rank12884は表内でもD帯の中でもかなり低頻度側)。v4の同じ段落の別文("the hidden part of daily life")では"hidden"を使っており、同一記事内で"invisible"に対応する語が"unseen"(冒頭比喩)と"hidden"(後半)で不統一。v4 Promptの「明確に簡単で自然な代替がある場合のみ置換」というself-check指示が、この事例では機能しなかった(unseenはinvisibleより明確に難しい)。 |

## B. 帯B/C/D全content word(Advanced基準24語)の3段階推移

Advanced帯B(10語)+帯C(8語)+帯D(6語)=24語(帯Aは非常に平易なため対象外)。

### 帯B(10語)

| 語(Advanced帯・rank) | v3 | v4 | 判定 |
|---|---|---|---|
| underground (B,4200) | 同語×4 | 同語×4 | そのまま残った |
| toilet (B,4276) | 同語×3 | 同語×3 | そのまま残った |
| bath (B,3352) | 同語×2(いずれも単数) | "baths"(複数)×1+"bath"(単数)×1 | そのまま残った(語自体は同じだが単数/複数表記がv4のみ不統一) |
| pipes (B,4696) | 同語(×3、文分割で増) | 同語×2 | そのまま残った |
| repairs (B,3582) | 同語×2 | 同語×2 | そのまま残った |
| washing (B,3271、"washing machine") | 同語×2(比喩) | 同語×2(比喩) | そのまま残った(比喩保持) |
| arrive (B,3739) | 同語×1 | 同語×1(文分割で"surprisingly"との係り受けが変化、§Story参照) | そのまま残った |
| beneath (B,4739) | "under"(前置詞、機能語につき対象外) | "under"(同左) | 自然に置換(v3を踏襲) |
| rid (B,3022、"getting rid of") | "**removing**"(A,1702)に置換 | "**getting rid of**"(Advancedと同一表現に復帰) | v3: 自然に置換 / v4: そのまま残った(Advanced水準に後退、ただし"get rid of"は慣用句として自然であり実害は小さい) |
| tap (B,4496) | 同語×1 | 同語×1 | そのまま残った |

### 帯C(8語)

| 語(Advanced帯・rank) | v3 | v4 | 判定 |
|---|---|---|---|
| distant (C,5212) | faraway(D,表外) | faraway(D,表外) | 難語→別の難語(上表#8) |
| convenience (C,6887) | "life easy"へ言い換え(convenienceを回避、自然) | "**convenience**"をAdvancedのまま保持 | v3: 自然に置換 / v4: そのまま残った(v3の改善が後退) |
| divide (C,5876) | "**split**"(A,2270) | "**split**"(A,2270、v3と同一) | 自然に置換(新帯基準では明確な簡略化。旧Trialのtop2000基準では圏外扱いだったが、本Trialのrank≤3000基準ではA帯) |
| flush (C,9610) | 同語×1 | 同語×1 | そのまま残った(代替しにくい必須動詞) |
| inspections (C,5694) | checks(A) | checked(A) | 自然に置換(上表#3) |
| installation (C,5508) | putting in | put in | 自然に置換(上表#2、型は同一) |
| invisible (C,6153) | hidden(A) | unseen(D) | v3: 自然に置換 / v4: 難語→別の難語(上表、最重要の悪化事例) |
| surprisingly (C,6187) | 同語("surprisingly familiar place") | 同語だが係り先が"familiar"から"close"に変化(2文に分割) | そのまま残った(語自体)、ただしEnding文のニュアンスが変化(§Story参照) |

### 帯D(6語)

| 語(Advanced帯・rank) | v3 | v4 | 判定 |
|---|---|---|---|
| septic (D,表外) | 同語×4 | 同語×4 | そのまま残った |
| sewers (D,表外) | 同語(複数形、用例あり) | 同語(複数形、用例あり) | そのまま残った(記事主題語、簡略化不可能) |
| artery ("main artery", D,12006) | 同語×2(比喩) | 同語×2(比喩) | そのまま残った(比喩保持) |
| municipalities (D,11073) | towns(A)×2で統一 | "towns or cities"/"local governments"(不統一) | 自然に置換(上表#1、v4はv3より表現の一貫性が低い) |
| sewer (D,11459) | 同語(単数形、用例あり) | 同語(単数形、用例あり) | そのまま残った(記事主題語) |
| wastewater (D,18216) | 本文で同語保持 | 本文で同語保持、タイトルのみ置換 | そのまま残った(本文)/自然に置換だがタイトルと不統一(上表#5) |

## C. 集計(帯B/C/D、Advanced基準24語、v4時点の最終分類)

- そのまま残った: 14語(underground, toilet, bath, pipes, repairs, washing,
  arrive, tap, flush, surprisingly, septic, sewers, artery, sewer)
- 自然に置換(v3から継続、または新規): 7語(beneath→under, inspections→
  checked, installation→put in, divide→split, municipalities→towns or
  cities/local governments, wastewater[タイトルのみ])
- 難語→別の難語: 2語(distant→faraway, invisible→unseen)
- 自然な状態から後退(そのまま残った=Advanced水準へ回帰、v3の改善が
  失われた事例。上記どの4分類にも完全には一致しないため別掲): 2語
  (rid[v3:removing→v4:getting rid of], convenience[v3:言い換え→v4:
  そのまま])

## D. まとめ(Sonnet目視、最終評価はFable/ユーザー)

- ユーザーが名指しした3つの既知問題(installation→putting in /
  collects→gathers / distant→faraway)のうち、**collects→gathersと
  distant→farawayはv4でも一言一句同じ表現のまま再現され、全く解消され
  なかった**。installation→put inは語選択としてはv3と同じ型を再現した
  ものの、周辺の文法(過去分詞への統一)はv4で改善された。
- v4は新たに**invisible→unseen**という、v3の改善(invisible→hidden)を
  後退させ、Advanced本体より難しい語を導入する事例を生んだ。これは
  v4 Promptの「明確に簡単で自然な代替がある場合のみ置換する」という
  self-check指示が意図通りに機能しなかった直接的な反例。
- convenience・rid(getting rid of)でも、v3で達成されていた簡略化が
  v4ではAdvanced水準へ後退している。
- 一方、記事の中心比喩(main artery/washing machine)・主題語(septic/
  sewer/sewers/wastewater本文)は全版で一貫して保持され、比喩保持の
  指示自体は機能している。
