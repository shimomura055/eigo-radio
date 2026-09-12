# EDITORIAL-B-FAMILY-VOICES-3V-PHASE1B-04-OPUS-L3-DIAGNOSIS-01
日付: 2026-09-12 / 実施: opus-consultant(L3診断、読み取り専用) / 入力: context packet方式(packet 33,556字+追加開示約9,600字)
注: Opus転記ファイルが0バイトで消失したため、Fableが受領した最終出力をそのまま転記(CONSOLIDATION-98B)。本REPORTの提案(修正(A)〜(F)、案1〜3)はすべて候補であり、採用はユーザー判断。

## 要点(5行)

1. **Leakage 2/2再現の主因は「汎用化」ではなく、旧prompt由来の構造的二律背反(double-bind)である。** Voice Cardのbullet(`er012_b_family_voices_writer_generic_01.py:402-404`)は「数字を必ず1つ織り込め」と命じ、ルール節(同`251-256`)は「調査・報告・データを主語にするな」と禁じるが、theme側のsupporting evidenceは集計統計(49%/79%/90%)しか持たない。旧採用版はこの矛盾を「数字を全部捨てる」ことで回避し、新2本は「数字を残す」ことで検出された。旧prompt(`er012_editorial_b_voices_3v_person_voice_trial_02.py:376-380`)にも同じ矛盾が語一致で存在する。
2. **統計的には旧との差は判別不能(Fisher片側 p=0.25〜0.33)だが、「新経路が本番基準を満たしていない」ことは既に2/2で言える。** 追加本数は帰無仮説の置き方で変わる(下記論点1)。ただしメカニズムが特定できているため、追加生成より¥0のテキスト検証のほうが情報量が大きい。
3. **ablationは「未回答」ではない。保存済みの`article.md`(packet 196-222行)を直接読むと、3 Voiceに統計主語文が1つも無い**(Voice3の数字は"In one reported case, a hotel chain's hiring time fell..."で人・企業が主語)。単体Leakage Checkを保存記事に当てるだけ(Writer再生成不要、推定¥5〜10)で当初設問に答えが出る。
4. **ablationのLedger逸脱4件を「原則除去の効果」とするのは文面上根拠がない。** 当該原則は`:346`で明示的に「Voice本文で」に限定されており、地の文への抑制経路がない。加えて5件中2件はLocal Rewriteが生成した文(cycle1再判定で新規発見)、かつablationのみattempt1段階での比較であり、他3本(attempt2/3)と同列比較できない。
5. **3V方式の意味は4本すべてで保持されている**(単純合計否定・非二元・一人称)。むしろリスクは「意味の喪失」ではなく**Closingの修辞骨格が4/4で同型固定化していること**で、これは同一テーマ4個体では判別できず、次テーマ1本が決定的な判別材料になる。

---

## 論点1: Leakage 2/2再現は系統差かrun分散か

**確率評価**

| 集計単位 | 旧 | 新 | Fisher片側p |
|---|---|---|---|
| attempt単位(1件以上flagged) | 1/2 flagged | 6/6 flagged | 0.25 |
| run単位(3attempt内に0件へ収束) | 1/1 収束 | 0/2 収束 | 0.33 |

旧attempt1は3 Voice全滅(packet 236-238行)、新はattempt1で7項目→attempt2で1件→attempt3で1〜2件。**どちらの単位でもα=0.05では旧との差を主張できない。**

一方、**帰無仮説を「本番基準=8割のrunがflagged 0件へ収束する」に置くと、2/2の非収束は p=0.2²=0.04 で既に棄却される。** 「旧と有意に違うか」は未決着だが、「新経路の現状を本番品質として受け入れられるか」は既に否定側に振れている。この2つは別問題として分けてユーザーへ出すべき。

**必要な追加本数(参考値)**
- 緩い帰無(収束率≥50%)を棄却: 5連続非収束が必要 → **新経路あと3本**(¥75〜235)。
- 「汎用化由来」と帰属させる: 上記に加え**旧経路の再実行3本**が必要(旧はn=1)→ 合計6本(¥150〜470)。

**ただし追加生成は推奨しない。** 理由は、REPORT 9-1の全文diff(367行中、意味のある差分3点、うち2点は番号振り直しと言い換え)で**prompt由来の系統差はすでに¥0で概ね否定されている**ため、追加runは主にモデル/run雑音を測ることになる。代わりに¥0で得られる強い判別材料がある。

**¥0の決定的テスト(推奨)**: 既存9個体(旧attempt1・2、新1回目attempt1-3、N+1 attempt1-3、ablation attempt1)について「Voice本文に数量(数字または"about half"等の割合語)が文の主語位置にあるか」を機械的に数え、flagged有無との一致を見る。予測は9/9一致(=clean個体は数量主語文が0の個体のみ)。N+1 attempt3が49%→"About half"へ書き換えても`leak_numbers_foreground`込みでflaggedになった事実(packet 245-246行)は、この予測を支持する。

**run分散ではなく「whack-a-mole」の構造的証拠**: flagが毎attemptで別Voiceへ移動している(新1回目: voice_2/3→voice_2→voice_1、N+1: voice_2→voice_3→voice_1+2)。全文書き直し方式のretryは、直した箇所の代わりに別Voiceで同じ型を再生産している。これは分散ではなく**retry設計の欠陥**の指標。

---

## 論点2: 「体験claim根拠付け」原則が統計調を誘発しているか

**文面からの評価(部分的にYes、ただし主因ではない)**

該当ブロックの実文(`:346-348`):
> Voice本文で、その人物自身の体験として語る箇所において、数値・制度・他者(第三者)の具体的な行動を事実として断定する場合は、必ずVerified Fact Ledgerに直接のevidenceがあるものに限ってください。

この文は「数値を出すなら Ledger にあるものに限れ」という**制限**であり、同時に「Ledgerにある数値なら断定して良い」という**許可**として読める。theme側のsupporting evidenceがLedger由来の49%/90%しか持たないため、実質的に「その統計を使え」という誘導になる。したがってFable仮説は**方向としては正しい**。

ただし、より強い誘発源はこの原則ではなく**Voice Card bulletの数字命令**(`:403-404`)である。
> この裏付けの中から、1つのVoiceにつき最大1つの具体的な数字だけを、人を主語にした自然な話し言葉で織り込んでください(詳細ルールは上記【Evidenceは脇役であること】参照)

「最大1つだけ」は上限表現だが、文脈上「織り込んでください」という**指示**であり、モデルは遵守しようとする。原則ブロックを消しても(ablation)このbulletは残っており、それでも統計主語文が出なかったことは、原則ブロック側の寄与を示す弱い証拠になる。

**ablationがLeakage Checkに到達しなかった問題の代替設計(いずれも既存Production未改変)**
- **案A(最安・推奨)**: 保存済み`er012_output/editorial_b_voices_3v_ablation_no_grounding_block_01_attempt1/article.md`に対し、Leakage Checkerを**単体で1回呼ぶ**。Writer再生成なし、Ledger gateを通らない。推定¥5〜10。当初設問(原則除去でLeakageが出るか)に直接回答が出る。
- **案B(¥0)**: 上記の目視判定で代替。4本の実文から、ablationのVoice本文には統計主語文が無いことは既に読み取れる(Voice1は数字なし、Voice2は"at one large company"、Voice3は"In one reported case, a hotel chain's..."で企業が主語)。
- **案C(非推奨)**: 早期停止分岐(`run_voices_pattern_3v`の`992`行)を診断用に回避する経路を作る。Production安全装置の迂回であり、L2で安全装置が「仕様どおり機能した」と確認された直後に緩める変更はガバナンス上のリスクが大きい。

---

## 論点3: ablation Ledger逸脱4件の解釈

**「原則除去の系統的効果」とは言えない。3つの理由がすべて実文で裏付けられる。**

1. **原則の適用範囲がVoice本文限定**(`:346`「Voice本文で」、`:354`「このルールは全Voiceに等しく適用してください」)。地の文・Tensionへの経路がない。packet 479行の「間接的抑制効果を持っていた可能性」は文面上の根拠がない推測である。
2. **5件中2件はLocal Rewriteの生成物**(packet 286-287行、"The recruiter must use the system." / "I have no say in the system." は cycle1再判定で新規発見)。つまり元稿のNGは3件で、残り2件は是正機構が作り出した二次被害。「4個体中最多」という比較は水準が揃っていない。
3. **ablationのみattempt1段階の評価**。他3本はattempt2/3(自己修正1〜2回後)。旧attempt1のLedger逸脱件数がpacketに無いため、同段階比較ができない(packet不足点)。

**代わりに見えている本当のパターン**: 逸脱・指摘の発生箇所が4本すべてで**Tensionの権限非対称性列挙文**という同一スロットに集中している。
- ablation(Ledger MAJOR、3回rewrite失敗): "Their power is uneven: the applicant cannot choose the process; the recruiter runs it but does not choose adoption; the owner chooses and bears the consequences."
- N+1(Fact Checker REVIEW): "Their power is uneven: the applicant is judged, the recruiter operates but does not choose the tool, and the owner chooses it and owns the result."(packet 320-321行)
- 旧採用版(通過): "The applicant cannot choose the system; the recruiter runs it and may also help decide whether to adopt it; the owner may make the final call."

**これは第二の二律背反である**: Tension指示は「非対称性を明示せよ」と求め、Ledger/Fact Checkerは「役割・権限の一律断定」を罰する。旧が通ったのは`may`が2箇所入っていたためで、紙一重。ablationのrewriteは`may`を9箇所まで増やしてもLEDGER_DEVIATIONのままで、Tensionが166語(caveat 9)へ膨張した(packet 224-227行)。**hedge量を増やす方向の是正は原理的に収束しない**ことを示す実測値であり、論点4の案3への直接の反証材料になる。

なお、Fable指摘の訂正値(near-duplicate 0.559)を入れると4個体は0.582 / 0.471 / 0.590 / 0.559となり、**ablationは外れ値ではない**。「ablationが全般的に悪化した」という印象はこの取り違えに一部起因している。

---

## 論点4: Sonnet提示3案の妥当性と見落とし候補

REPORT 870-880行の3案の評価。

| 案 | 妥当性 | 副作用リスク |
|---|---|---|
| 1. 現状維持(N+2以降で再検証) | 消極的には妥当。ただし二律背反を残すため、本番で毎記事attempt3まで消費し1本¥53〜78の上振れが常態化する | 費用の恒常的上振れ、flagged残存の常態化 |
| 2. 「根拠付け」→「統計で正当化するな」の否定形追加 | **方向は正しいが置き場所が誤り。** この原則はFact Safety(Ledger裏付け強制)の規則であり、そこへ「統計を挙げるな」を混ぜるとLedger引用そのものを抑制し、Fact Checkerの`unsupported_specific_claims`が増える逆効果の恐れ | Fact安全性の希薄化。**形式規則は`:251-256`側へ置くのが正しい** |
| 3. 原則をTension/Closingへ拡張 | **最もリスクが高い。** ablationのrewrite実測(hedge 9箇所・166語でも不合格)が「hedge増量では収束しない」ことを示しており、加えてトーン規則(`:260-263`のlight/conversational)と語数soft target(410-450語)に正面衝突する | 語数膨張、曖昧化、可読性劣化 |

**Sonnetが挙げていない原因候補(重要度順)**

- **(A) Voice Card bulletの数字命令とCheckerの衝突(主因候補)**。修正方向: bulletを「自然に人を主語にして織り込めない場合は、数字を使わなくて構いません」と**任意化**し、許容例("I'm not the only one — most of the job seekers I know feel the tools are more biased than people.")と禁止例("49% of job seekers say...")を**英文で併記**する。原則ブロックは無改変。意味変更なし、Fact安全性に触らない。
- **(B) theme側データの粒度(Fable指摘どおり実在の問題)**。voice_1のsupporting evidenceが49%/79%という集計統計のみ(旧`:376-378`、新も同一転記)。**集計統計は「Tension用」とタグ付けし、Voice本文用には個人体験レベルのevidenceを割り当てる**というtheme config設計(`er012_b_family_voices_theme_ai_screening_01.py:157-174`)の改訂候補。次テーマ以降に効く恒久策。
- **(C) retry機構の型**。Leakage flaggedに対して全文書き直し×3を当てているため、直った箇所が別Voiceで再発する。**Ledger側に既にある局所書き換え(`er010_ledger_local_rewrite_09.py`)と同じ方式をLeakageにも適用**すれば1attemptで収束する見込み。費用も1本あたり¥25〜50削減。ただしProduction配線変更でユーザー承認必須。
- **(D) Checker側の基準と retry trigger**。`any_flagged`→retryという設計のため、「主語位置」という形式のみの指摘が3attempt全消費を引き起こす。severity階層(主語位置のみ=WARN/監視、Discovery構造=retry)を入れる案。品質基準の変更に当たるためユーザー判断事項。
- **(E) 上記/下記誤記(`:404`「上記」、実際の参照先は`:251`でVoice Card `:219/223/227`より後)**。単独では影響小(Sonnet判定に同意)。ただし参照名も旧【Voice内の数字】→新【Evidenceは脇役であること】へ変わっており、**数字ルールへのポインタとしての明示性が下がっている**。(A)と同時に修正すべき衛生項目(¥0)。
- **(F) generic/theme分離で失われた暗黙文脈**: prompt diff結果(367行/意味差3点)からほぼ否定される。唯一未検証なのは**転記漏れ復元の前後でどのrunが実行されたか**(下記不足点)。
- **(G) disputed 2ブロック**: 3a→3の番号振り直しのみで本文語一致(REPORT 302-304行)。原因候補から外して良い。

---

## 論点5: Regressionを「PASS(同等)」と判定できる条件

**現状のままでは「同等」とは言えない。ただし「不合格」でもない。2層で表現すべき。**

- **層1(機能PASS)**: hard gate(Fact Checker FAIL 0、Ledger MAJOR未解決 0、human_review_required 0)を最終採用版が満たす。新1回目・N+1は満たす。**ablationは診断runでありPASS判定の母集団に含めない**(この明示が必要)。
- **層2(品質同等性)**: 同一attempt段階での比較が必要。最終採用版では旧 Leakage 0件 vs 新 1件/2件 → **同等ではない**。attempt1段階では旧3件 vs 新7件/3件で、こちらは同水準。

**「同等」と言えるための条件(候補)**
1. ¥0で原因が新経路固有でないことを示す(prompt diff済み + 既存9個体のテキスト一致テスト)。
2. 修正(A)(E)適用後に、**同一テーマで連続2本 Leakage flagged 0件**かつ hard gate PASS。
3. その2本のClosingが4/4の同型骨格から外れているか、または次テーマ1本で骨格が変わることを確認。

**スマホ制限テーマへ進む前の最小追加検証(費用付き、残¥40.1)**

| 内容 | 費用 | 得られるもの |
|---|---|---|
| 保存済みablation記事への単体Leakage Check | 約¥5〜10 | 論点2に確定回答 |
| 既存9個体の数量主語文カウント(offline) | ¥0 | 論点1のメカニズム確定 |
| 4本のClosing/Hook相互overlap計測(offline) | ¥0 | 論点6の定型化リスク定量化 |
| prompt修正(A)(E)適用後のrender diff + 既存offlineテスト | ¥0 | 意味不変の確認 |
| 修正適用後の実生成1本(AI採用テーマ) | ¥25.5〜78 | 修正の効果確認 |

**残¥40.1では最後の1本を安全に賄えない**(上振れ時¥78)。現予算内で完結させるなら「生成なし・¥10以内」に留め、実生成は追加予算承認後とするのが整合的。

---

## 論点6: 3V方式の意味は損なわれていないか

**損なわれていない(4本の本文から判定)。**

- **Voices=Perspectives / 賛否二元論ではない**: 4本すべてで3者が役割・利害・責任の重さで分化し、2対1の陣営化が起きていない。Tensionは4本すべてで「単純合計では答えにならない」を明示 — 旧"Their views cannot simply make one answer."(118行)、新1回目"their reasons cannot simply be added"(151行)、N+1"Their views cannot simply be added into one answer."(184行)、ablation"no one person's reasonable need can settle it"(217行)。
- **Comment 3「どの声が正しいかではない」の表現**: N+1 Closingが最も明示的で"One voice cannot settle it."(188行)で終わる。旧・新1回目・ablationも「誰が定義し、誰が説明し、誰が負うか」という三項に置き換えており、正否判定を回避する構えは維持。**汎用化で劣化ではなく、N+1はむしろ強化されている。**
- **懸念は別のところにある**: Closingが4/4で「Xは単に〜かという問いではない。それは誰がA、誰がB、誰がCかという問いだ」という同型骨格。Hookも「application→softwareがresume/test/videoをscan/score→3人が同じ場面」で4/4共通。**これは3V方式の意味の喪失ではなく、テンプレート固着(記事間の自己類似)のリスク**。同一テーマ4個体では「テーマ由来」と「テンプレート由来」を分離できないため、**次テーマ(スマホ制限)1本のClosingが同じ骨格を再生産するかが唯一の判別材料**。既存QAは記事内類似(Point Overlap最大0.16、near-dup 0.47〜0.59)しか見ておらず、**記事間類似の測定が存在しない**(packet不足点)。

---

## 新規結果/過去再掲/進行中の区別

- **今回の新規結果**: N+1 run(3attempt、Leakage 2件残存)、ablation run(NG_REVIEW_REQUIRED停止、Ledger逸脱)、prompt全文diff(367行)と転記漏れ1件の復元、Directional Fact Precheck辞書に「削減」欠落という特定原因、上記/下記誤記の発見。
- **過去再掲(新規劣化ではない)**: 語数soft target超過(旧488語も同様)、旧attempt1のLeakage 3件、Point Overlap全個体threshold下、near-dup 0.47〜0.59帯。
- **未決着(進行中)**: 二律背反(A)(B)への対処方針、Leakage retry方式(C)とtrigger基準(D)、Voice2 caveat=0の固定性、記事間定型化、「削減」辞書追加、追加予算。

## Fableへの推奨(ユーザー提示用、2〜3案とQCD)

**案1「¥10以内で診断を閉じ、修正案をユーザー提示」(推奨)**
- 内容: ablation保存記事への単体Leakage Check(約¥5〜10)+ ¥0 offline計測3種 + 文言修正(A)(E)の確定案提示。判定は「hard gate PASS / soft指摘はNOT-EQUAL、原因は旧経路から持ち越しの二律背反」と2層で確定。
- Q: 診断確度 中〜高(メカニズムは確定、修正の効果は未検証) / C: ≈¥10(予算内) / D: 即日。
- リスク: 修正の実効性が未検証のまま次テーマへ進む場合、同じflaggedが再発する。

**案2「修正適用 → 実生成で効果確認 → 次テーマへ」**
- 内容: 案1 + 文言修正(A)(E)適用後、AI採用テーマで1本(Leakage 0件確認)、続けてスマホテーマ1本。
- Q: 高(修正効果とテンプレート固着の両方を同時に検証) / C: ¥55〜160(**追加予算承認が必須**) / D: 1〜2日。
- リスク: 予算追加。prompt変更はProduction配線への変更であり採用可否はユーザー判断。

**案3「統計的決着(新3本+旧3本)」**
- Q: 統計的には決着(p≈0.03) / C: ¥150〜470 / D: 数日。
- **非推奨**。prompt差分が3点の化粧的差異しかないことが¥0で判明しており、追加runはモデル雑音の測定に近い。同額を(A)(B)(C)の修正検証に振る方が費用対効果が高い。

いずれもProduction採用(`APPROVED_FOR_PRODUCTION`)の可否は判断していない。修正(A)〜(F)はすべて候補であり、実装着手はユーザー承認後。

---

## 追加開示ログ(宣言・実施済み)

| 対象 | 行範囲 | 理由 | 概算文字数 |
|---|---|---|---|
| `C:\Users\tensh\eigo-radio\EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04_REPORT.md` | grep(見出し・「修正案」等)+ 285-324 + 860-899 | 論点4の必須材料「修正案3つ」がpacketに転記されていなかったため | 約3,800字 |
| `C:\Users\tensh\eigo-radio\er012_b_family_voices_writer_generic_01.py` | 210-264、340-414 | 原則ブロック全文・Voice Card bullet・ルール節の**実際の前後関係**の確認(論点2・4の因果の核) | 約4,500字 |
| `C:\Users\tensh\eigo-radio\er012_editorial_b_voices_3v_person_voice_trial_02.py` | 362-391 | 旧prompt同一箇所との一次比較(packet経由の要約ではなく実文で確認) | 約1,300字 |

合計約9,600字の追加開示。packet(33,556字)と合わせて約43,000字。

## packet不足点(次回改訂への申し送り)

1. **論点4の材料が実際には入っていない**。対応チェック表は「(d)Sonnet要約」にあると宣言しているが、(d)に修正案3つの転記はない。**論点ごとに「材料が実際に転記されているか」の自己検証が機能していない。**
2. **prompt修正(転記漏れ復元)の適用タイミングと各runの実行順が不明**。復元前後でどのrunが走ったかは新旧比較の交絡要因そのもの。REPORT 474行が「復元適用後のN+1で再現するかは未確認」と述べており、ここは診断上の必須情報。
3. **原則ブロック・Voice Card bullet・ルール節の実文**が(c)で「行範囲の指定」のみに留まり本文が無かったため、論点2・4の因果判断ができなかった(今回追加開示で補完)。**因果を問う論点では、該当promptブロックの実文転記が必須。**
4. **旧Trial-02 attempt1のLedger逸脱件数・Local Rewrite件数**が無い。ablationの4件を「4個体中最多」と評価するには同attempt段階の対照が必要。
5. **記事間(4個体間)のoverlap測定値が無い**。論点6(定型化)は記事内指標だけでは判定不能。
6. **Writer/Checker呼び出しにweb_searchが含まれる**(ablationでweb_search 6件)。live searchはrun間の内容分散源になり得るため、旧Trial-02実行時と同条件かの記載が必要。
7. near-duplicate ablation値の0.143はPoint Overlap値の取り違え(Fable指摘どおり、正: 0.559)。**異なる計測方式の値を代用する場合は「代用」と明記するだけでなく、代用しない=未計測と書くほうが安全。**
