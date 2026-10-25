# Part 2(Grammar & Sentence Structure)Trial-08 結果: 倒置の優先順位変更(ユーザー閲覧用・1ファイル完結)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_18 / 日付: 2026-10-25 / 状態: Trial段階(DEV専用。Production採用・配線は未承認。到達上限VALIDATED)
開発者向けの判定・費用・要因分解は `EVAL_08.md` / `COMPARISON_08.md` / `analysis_08.json`、事前登録は `PREREGISTERED_CRITERIA_08.md`。

## 0. 結論(Sonnetの所見。最終評価はFable、採否はユーザー)
- 倒置への偏りは減った。**主表(各作品の代表標本=r1)では、倒置を選んだ作品が4/8 → 1/8**(賢者の贈り物のみ残る)。全標本で見ても、Trial-07の既存18標本へ新順位を機械的に再適用すると、旧規則で倒置を選んでいた標本10/18が4/18に減った。
- 倒置を一律に除外してはいない。倒置以外に適格な候補がない作品(賢者の贈り物は再抽出した3標本すべて、告げ口心臓r2)は、規則どおり倒置が残った。
- 学習価値は「明確に良くなった作品」と「同等〜やや良い作品」がある。**告げ口心臓は明確に改善**(場所句の倒置 → 挿入された分詞句による後置修飾)。開いた窓(→長い動名詞句の主語)・猿の手(→wish+目的語+補語)は倒置より多様になったが、学習価値の差は大きくない。
- 注意点(正直に記載): (1) 倒置以外に「十分な価値」の候補が乏しい作品がある(物語本文が平易)。 (2) 倒置以外の候補は標本によって出たり出なかったりする(LLMの抽出・学習価値判定のばらつき)。 (3) 旧データへの機械適用では、学習価値の低い非倒置(`Like Jim, it needed no decoration…`のLike A, B型、猿の手r2の同格)が倒置より優先される標本があった。事前登録の機械基準はすべて合格したが、(3)は質を落とす可能性があるためFable独立評価を要する。

## 1. 8作品 新旧比較表(代表標本r1。標本が揺れた作品は下の「標本別」に併記)
| 作品 | Trial-07選定 | 今回の選定 | 学習できる文法 | 評価(Sonnet所見) |
|---|---|---|---|---|
| 開いた窓 | 倒置 `Across the quiet garden came a young voice:`(P21) | **長い動名詞句の主語** `Inventing convincing stories at a moment’s notice was Vera’s speciality.`(P29)。3標本とも同じ | 動名詞から始まる長い句の全体が主語で、その後ろの`was`が動詞だと読む型 | 変更あり・偏り解消。学習価値は同等〜やや低い可能性(基礎項目「動名詞主語の単純形」に近い。Fable確認) |
| イグ・ノーベル | what節(疑似分裂文) `If you were expecting a fancy latte, what you got was a map of molecules.`(P4) | **同じ**(2標本とも) | `what`節が文の主語になり、`was`の後に内容が示される型 | 変更なし(候補に倒置が無い)。維持 |
| 賢者の贈り物 | 倒置 `Inside were the tortoise-shell combs she had so often admired in a shop window.`(P22) | **同じ(倒置が残った)**。再抽出3標本すべて | 場所句が文頭に出ると動詞の後ろが主語。`she had so often admired…`(目的格関係詞の省略)の修飾も含む | 倒置を残すのは妥当と判断(他に適格候補0)。ただし旧登録の中核P4(`handed down from his grandfather…`)が学習価値LOW判定=見落としの疑いを要Fable確認 |
| 猿の手 | 倒置 `Then came a soft knock.`(P24) | **wish+目的語+補語** `Wish him alive again!`(P18)(r1。r2は同格 `A knock announced an old friend, a retired sergeant-major home from India.`(P2)) | `wish`の後ろ`him`が目的語、`alive`がその状態(補語)。`again`は`alive`にかかる | 倒置より多様化。学習価値は同等〜やや良い。標本で選定が揺れ、r2の同格は価値が低め |
| 告げ口心臓 | 倒置 `From the bed came a small groan of terror.`(P8) | **挿入された後置修飾** `But that pale blue eye, covered by a thin film like a vulture’s, made his blood turn cold.`(P2)(r1。r2は倒置が残る) | 主語の直後に挿入された過去分詞句を外して、主語`eye`と動詞`made`を見つける型 | **明確に改善**(再利用できる読解スキルに変わった)。r2は他に適格が無く倒置が残った |
| 二十年後 | 0件 | **0件**(再抽出2標本とも0件) | (なし) | 変更なし。0件は妥当 |
| 退屈と攻撃性 | 長い前置要素 `This time, regardless of how strongly participants were inclined to enjoy seeing others suffer, those who watched…than those in the other conditions.`(P7) | **同じ**(r2は長い主語P5) | 長い前置要素の終わりを見極めて主節の主語・動詞を探す型 | 変更なし(候補に倒置が無い)。維持 |
| 走れメロス | 修飾関係 `Melos struck the man holding it with his walking stick and ran uphill, their shouts following him.`(P11) | **同じ**(r1。r2は0件) | 前置詞句`with his walking stick`の修飾先+付帯状況の分詞 | 変更なし。Trial-07で事前登録の許容集合∅に反した判定を継承(別掲。ユーザー指示のTier1例示「分詞構文・付帯状況」との関係はFable判断候補) |

標本別の揺れ(旧=Trial-07既存標本への再適用、新=今回の再抽出): 開いた窓 3/3がP29 / イグ 2/2がP4 / 賢者 旧r1・r2・新r1〜r3は倒置(旧r3のみCMP `Like Jim, it needed no decoration…`=Like A, B型で価値が低い疑い。再抽出標本では出現せず) / 猿の手 旧r1倒置・旧r2 P18・新r1 P18・新r2 P2同格 / 告げ口心臓 旧r1 P11(`Faster it beat, and louder.`)・旧r2倒置・新r1 P2・新r2倒置 / 二十年後 4/4で0件 / 退屈 P7(r1)・P5(r2) / メロス P11・0件。

## 作品1. 開いた窓(サキ)
**今回の選定**(P29、HEAVY=長い主語):

> Inventing convincing stories at a moment’s notice was Vera’s speciality.

**日本語訳**: その場ですぐに人を納得させる話を作り上げることは、ヴェラの得意技だった。

**選定理由**: 動名詞`Inventing`から`notice`までが1つの主語で、動詞`was`が文の後半にある。主語の終わりを誤ると`Vera’s speciality`を主語と読み違える(抽出時の判定: 主語の取り違え、学習価値HIGH)。倒置(P21)も適格だったが、倒置以外に適格な候補があるため第2優先に下がった(全3標本で同じ)。
**Trial-07との違い**: `Across the quiet garden came a young voice:`(場所句+動詞+主語の倒置)から変更。**要因は優先順位の変更のみ**(既存データでP29が3標本とも適格、再抽出なし)。
**学べる文法**: 長い動名詞句が主語になる文で、句全体を1つの主語として捉えてから動詞を探す読み方。ニュースや論説でも使える型。
**学習価値の変化**: 倒置は「場所句+動詞+主語」の型。長い主語を1つにまとめて読む型は一般の文章でも頻出。ただし文自体は短く、基礎項目の「動名詞主語の単純形」との境界に近いので、価値は同等〜やや低い可能性がある(Fable独立評価で確認)。

## 作品2. イグ・ノーベル賞2026
**今回の選定**(P4、疑似分裂文):

> If you were expecting a fancy latte, what you got was a map of molecules.

**日本語訳**: もししゃれたラテを期待していたのなら、手にしたのは分子の地図だった。
**選定理由**: 候補に倒置が無いため新旧で同じ。`what you got`が文の主語、`was`の後に内容が示される。**Trial-07との違い**: なし。**学べる文法**: 疑似分裂文(What節が主語)。

## 作品3. 賢者の贈り物(重点確認: 旧倒置)
**今回の選定**(P22、倒置が残った):

> Inside were the tortoise-shell combs she had so often admired in a shop window.

**日本語訳**: 包みの中には、彼女が店のショーウィンドウで何度も見とれていたべっ甲の櫛が入っていた。
**選定理由**: 場所の副詞`Inside`が文頭に出て、`were`の後ろ`the tortoise-shell combs`が主語。Trial-07と同じ文(再抽出した3標本すべて、既存の2標本でも)。**Tier1(倒置以外の適格)は再抽出3標本で0**のため、規則どおり倒置が残った。旧r3だけはCMP P12 `Like Jim, it needed no decoration to prove its worth.`が適格になり倒置に優先したが、これはLike A, B型で価値が低い疑いがある(再抽出標本では出現せず)。
**他に十分な候補がなかったか**: 再抽出3標本の抽出は倒置2件(P22・P30)のほかにP4(POSTMOD `handed down from his grandfather to his father, and then to him`)が1標本に出たのみで、**学習価値LOW**と判定されて不適格。P4はTrial-06以来の登録で「中核」とされた文なので、LLMの学習価値判定が厳しすぎる(見落とし)か、分詞の基本用法で価値が低いかは**Fableが判断する点**。Sonnetの目視では、P4は分詞の基本用法が中心で解説価値は高くないが、`and then to him`の省略を含む点はやや価値がある。結論: 倒置を残すのは「ほぼ妥当・条件付き」。
**Trial-07との違い**: なし(選定は同じ)。

## 作品4. 猿の手(重点確認: 旧倒置)
**今回の選定**(r1、P18、特殊な文型 wish+目的語+補語):

> Wish him alive again!

**日本語訳**: 彼がもう一度生きていてくれたらと願え！(同系統の`I wish Herbert alive again.`(P22): ハーバートがもう一度生きていてくれたらと思う。)
**選定理由**: `him alive again`を「ひとまとまりの目的語」と誤読しやすい。`him`が目的語、`alive`がその状態を表す補語。倒置(P24 `Then came a soft knock.`)も適格だが、倒置以外に適格があるため後回し。
**Trial-07との違い**: `Then came a soft knock.`から変更。**要因は優先順位の変更が主**(旧r2でもP18が適格だったが旧r1では抽出されず、再抽出r1で抽出された=抽出のばらつきが加わる)。
**学べる文法**: `wish + 目的語 + 状態の補語`。**学習価値の変化**: `Then came a soft knock.`は4語の短い倒置でTrial-07の品質評価でも学習価値「軽微」と指摘された。`wish`型は頻度は低いが文型の取り違えを防ぐ読み方で、倒置より同等〜やや高い。
**注意**: 同じ作品のr2は同格`A knock announced an old friend, a retired sergeant-major home from India.`(訳: ノックの音が、昔の友人――インドから帰国した退役曹長――の来訪を告げた。)を選んだ。他の3標本ではLOW判定の文で価値が低めであり、**標本間のばらつきが選定品質のリスク**。また`I wish Herbert alive again.`(P22)の方が文として自然だが、Tier内の順位(段落番号順)のためP18が先に選ばれる(Trial-07の規則を維持したため)。

## 作品5. 告げ口心臓(重点確認: 旧倒置。Trial-07と同じ本文)
**今回の選定**(r1、P2、挿入された分詞句による後置修飾):

> But that pale blue eye, covered by a thin film like a vulture’s, made his blood turn cold.

**日本語訳**: ハゲワシの目のような薄い膜に覆われた、その淡い青色の目を見て、彼は血の気が引いた。(訳注: 機械訳。原文の`like a vulture’s`は`film`にかかり、訳がやや曖昧)
**選定理由**: 主語`that pale blue eye`の直後に`covered by…`が入るため、動詞`made`を探しにくく、`covered by`が`eye`を修飾するか`blood`を修飾するかの取り違えが起きる。学習価値HIGH(挿入句を外して主節を確認する読み方)。
**Trial-07との違い**: `From the bed came a small groan of terror.`(場所句の倒置)から変更。**要因は優先順位の変更+再抽出**(旧r1ではP2もTier1にあったが、順位の都合でCMP P11が先に選ばれる。新r1ではP2が唯一のTier1適格)。
**学べる文法**: 主語と動詞の間に分詞句が挟まる文の読み方(挿入句を外して主節を確認する)。**学習価値の変化**: 倒置は短く見慣れれば分かる型。今回は小説・論説で頻出の「主語の後ろに修飾が挟まる」読解スキルで、**明確に改善**。
**倒置が残った標本**: r2(新旧とも)は他の適格が無く、`From the bed came…`(倒置)が残った。旧r1が選んでいた`Faster it beat, and louder.`は新r1ではLOW判定で不適格だった(学習価値判定の揺れ)。

## 作品6. 二十年後
**今回の選定**: 0件(再抽出2標本・既存2標本の4/4)。
**0件の妥当性**: 抽出された特徴が0件。`Twenty years can change a man, but not the shape of his nose.`(P23)は許容集合の「どちらでも可」にとどまり、抽出されなかった。倒置も無い。Trial-07と同じ結論で、0件は妥当。**Trial-07との違い**: なし。

## 作品7. 退屈と攻撃性
**今回の選定**(r1、P7、長い文頭要素):

> This time, regardless of how strongly participants were inclined to enjoy seeing others suffer, those who watched the stone video were more likely to reduce another person’s reward than those in the other conditions.

**日本語訳**: 今回は、参加者が他人の苦しむ姿を見ることをどれほど強く楽しむ傾向にあったかにかかわらず、石の動画を見た参加者は、他の条件の参加者よりも、他人の報酬を減らす可能性が高かった。
**選定理由**: 節を含む長い文頭要素の終わりを見極めて、主節の主語`those who watched…`を見つける。r2は長い主語のP5。新旧で変更なし(候補に倒置が無い)。**学べる文法**: 長い前置要素と、`than those…`の比較。

## 作品8. 走れメロス
**今回の選定**(r1、P11、修飾関係):

> Melos struck the man holding it with his walking stick and ran uphill, their shouts following him.

**日本語訳**: メロスは、それを持っていた男を杖で打ち、彼らの叫び声を背に坂を駆け上がった。
**選定理由**: `with his walking stick`が`struck`にかかるか`the man holding it`にかかるかを見分ける。新旧で変更なし(再抽出r1も同じ。r2は0件)。**注意**: Trial-07の事前登録では許容集合∅で不合格扱い、Step Bの解説品質も「問題あり(中2)」だった。Trial-08でもこの扱いを継承し、優先順位変更の合否には含めていない。ユーザー指示のTier1例示に「分詞構文・付帯状況」があり、P11の`their shouts following him`と重なるため、許容集合∅の取り扱いはFable判断候補。

## 2. 倒置→別構文へ変更された作品の学習価値
| 作品 | 旧(倒置) | 新 | 具体的な違い |
|---|---|---|---|
| 開いた窓 | 場所句+動詞+主語 | 長い動名詞句の主語 | 旧: 見慣れれば短時間で分かる型。新: 主語の範囲を誤ると文全体の意味を取り違える。ただし新も文は短く価値は同等〜やや低い可能性 |
| 猿の手 | 4語の短い倒置 | wish+目的語+補語 | 旧: 学習価値が小さい(Trial-07評価も軽微)。新: 文型の取り違えを防ぐが、頻度は低い |
| 告げ口心臓 | 場所句の倒置 | 挿入された分詞句の後置修飾 | 旧: 倒置は分かりやすい。新: 主語と動詞が離れる文は多数の英文に出現し、「句を外して主節を確認する」再利用可能な読み方 |
| (賢者の贈り物は倒置のまま) | – | – | 他に十分な候補なし。倒置は価値のある選定として残った |

## 3. 評価基準(事前固定6点)の判定(詳細 `EVAL_08.md`)
| 基準 | 判定 |
|---|---|
| 1 非INV適格候補の優先 | 合格(Tier1適格があるのにINVを選んだ標本0。変更標本: 開いた窓3・猿の手2・告げ口心臓1・旧賢者r3) |
| 2 学習価値の低い文を無理に選んでいないか | 再抽出した作品では許容集合内で合格(メロスは継承分を別掲)。ただし猿r2の同格と旧賢者r3の`Like Jim,`は目視で価値が低い疑い=要Fable確認 |
| 3 倒置を残すべき作品で残せたか | 合格(賢者3/3・告げ口心臓r2で、Tier1適格0を機械確認)。賢者P4は見落としの疑いとして要確認 |
| 4 見落とし | (a)中核がある作品の0件標本0: 合格。(b)登録中核(非INV)の出現: 賢者P4は新1/3・旧0/3(出現時も学習価値LOWで不適格)=質は要確認 |
| 5 最大1件・0件許容 | 合格(全標本で≤1。二十年後4/4・メロスr2が0件) |
| 6 逐語一致 | 合格(選定文は全て単一段落内の逐語span。新規抽出で連結検出0) |
**機械判定ALL_PASS=True**。ただし学習価値の質はFable独立評価待ち。

## 4. Fable独立評価
(空欄。Fableが記入)

## 5. 品質の改善・悪化(Sonnet所見)
- 改善: 倒置の偏り(4/8→1/8)。告げ口心臓は明確に改善、猿の手・開いた窓は多様化。
- 悪化の可能性: 学習価値が低い非倒置が、倒置より優先される標本(旧賢者r3 `Like Jim,`、猿r2の同格、旧tth r1の`Faster it beat, and louder.`)。学習価値HIGH判定がLLMの標本で揺れる性質による(適格条件はTrial-07と同一のまま)。
- 変えていないもの: 最大1件・0件許容・基礎構文の除外・逐語一致・適格条件。

## 6. 実費と量産単価への影響
- 実費: 再抽出11 call **3.4985円**(gpt-6-luna、全callstatus=completed) + 新選定文の翻訳(1 call、5文、T1 module) **0.0818円** = **3.5803円**(本委任上限12円の29.8%)。案件累計 35.2454 + 3.5803 = **38.8257円**(案件上限50円の77.7%)。
- 量産単価: 選定規則はコード(API 0)で、抽出Promptは1文差し替えのみのため、1セットあたり費用はTrial-07と同じ**約0.41円**(Step A'' 平均0.33円+Step B 平均0.079円)。70円/記事セット目標の約0.6%で、**単価への影響はほぼ0**。
- 最新モデル原則との関係: 再抽出はTrial-07と同一のgpt-6-luna・同一Promptを使用(比較条件の同一性のため。Trial-07採用時点で最新世代の推奨系)。

## 7. Status候補
**VALIDATED(候補。条件付き)**: 事前登録の機械基準にすべて合格し、倒置の偏りを減らしつつ(倒置を残すべき作品では残し)、告げ口心臓で学習価値が改善。ただし学習価値の質の最終判定はFable独立評価、Production採用は人間ユーザーのみ(APPROVED_FOR_PRODUCTIONではない)。

## 8. 正式採用に向けて必要なユーザー判断(判断候補。分類は PM_GOVERNANCE 27-3)
1. **この選定方式(倒置をTier2へ下げる)を正式採用するか**(D 新しい判断)。採用する場合はCURRENT_SPEC/DECISION_LOGへの反映とProduction配線が別途必要。
2. 「十分な学習価値」の閾値を現状(Trial-07と同じ`teaching_value=HIGH`)のままでよいか(D)。現状のままだと、LLMの揺れで低価値な非倒置が選ばれる標本がある。閾値強化は品質基準の変更に当たるため承認要。
3. ユーザー指示のTier1例示にある「分詞構文・付帯状況」「その他」(現行機構でOTHER分類=選定対象外)を、将来のTrialで選定対象に加えるか(D 仕様候補。現行機構では未対応のため今回は変更せず報告のみ)。走れメロスP11の許容集合∅の扱いとあわせて。
4. 告げ口心臓のProduction最新版への適用確認(C 現タスクと独立。ユーザー指示で別扱い済み)。
