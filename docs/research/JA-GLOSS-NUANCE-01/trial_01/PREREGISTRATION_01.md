# JA-GLOSS-NUANCE-01 Trial 事前登録 (実行前に固定。2026-10-31、API呼出前に作成)

- 比較: A=現行Prompt(保存済み実入力をそのまま再生。現行Production文面と一致をassert) / B=改善案(NEWGEN_MEANING_TEXT内 japanese_gloss欄の差替え+「訳語の選び方」欄の追加のみ。他は1字も変えない)。文面はtools/gloss_nuance_trial_01.py の NEW_JG_BULLET / NEW_CHOICE_BULLET。
- 生成モデル: gpt-6-luna(Productionのgloss段と同一=ライン組込候補の性能確認[25-1例外2]。最新世代の効率系であり最上位ではない)、reasoning=high、developer/schema=Production NEWGEN定数、同一入力。
- 入力: X5記事(Advanced/b1b)の保存済みgloss Prompt(untidiness=対象、moon/jwst/aichat/meta=副作用確認)。対象記事はA,Bとも3反復(確率的ぶれの測定)、他4記事はA,B各1回。
- 評価者: 本agent(Claude Sonnet 5.5)。A/Bの順を乱数(seed固定)で伏せた表で、arm開示前に3段階(S2好/S1可/S0不可)と対比較(B better/same/worse)を付ける。必要時のみ追加の独立判定(gpt-6.1-sol)を費用内で併用。
- 対象item(verdict)の合格語: 評決/判決 およびそれを含む裁判語(S2)。判定/判断/評価(S1相当・要補足)。結論/決定/結果(S0~S1、近義語conclusionとの区別が伝わらないため不合格)。

## 合格基準(VALIDATED条件。全て満たす場合のみVALIDATED、1つでも欠ければNOT_VALIDATED)
- C1 対象: A(現行)で verdict が結論系になる再現率が 2/3以上(原因が確率的な偶然でなく系統的であることの確認)かつ、B で裁判語(評決/判決)になる再現率が 2/3以上。
- C2 副作用: 他item(対象以外の全item、約55件×1回)で、対比較 B worse が2件以下、かつ B worse ≤ B better。かつ B出力に既存検査違反(空・enum外・括弧/プレースホルダ記号・算用数字)が0件。
- C3 費用: B の出力token平均が A の 1.10倍以下(1記事gloss費用の増加が約0.1円以内)。
- C4 2訳語: B で「A、B」形式の2訳語gloss は全itemの5%以下、かつ各件を『必要/不要』判定し不要なものは0~1件。
- 参考(合否に使わない): Aの再生と保存済み本番出力の一致率(再現性の確認)。

---
## 追記1 (2026-10-31、確認Trial実行前に追記。探索段階の結果を見た後であることを明示)
探索段階(対象記事+X4記事、A/B/B2/B3)の結果: B(v1)・B2は対象verdictで0/3(裁判語にならず)、B3は3/3。B3の全体比較で C1=PASS、C2は厳格適用(B worse≤2)だとA1-vs-B3で4件・A2-vs-B3r2で4件=未達、C3(出力token比≤1.10)は matched比1.11で未達。
ただし A同士(A1 vs A2)でも worse 相当が55件中6件、出力tokenの標準偏差が平均の約20%あり、事前登録した閾値は run間ノイズを織り込んでいなかった(設計不備)。
よって探索段階の判定は『厳格適用=NOT_VALIDATED(C2・C3未達)』と記録した上で、新規データ(held-out: 対象記事に未使用のX 4記事のb1b gloss入力 coffee/yemen/island/part2)で、ノイズを織り込んだ次の基準を**実行前に**固定して確認Trialを行う:
- H1 副作用: B3 vs A(各1回、約28件)の盲検対比較で B3 worse ≤ 3件 かつ B3 worse ≤ B3 better。
- H2 検査違反0(空・括弧・記号・enum外)、2訳語(A、B形式)は全itemの5%以下。
- H3 費用: matched出力token比 ≤ 1.25 かつ 1call費用差 ≤ 0.15円(Aの標準偏差約20%を踏まえた基準)。
最終Status: 探索段階C1=PASS かつ H1~H3=全PASS ならVALIDATED(ただし閾値変更の経緯と探索/確認の区別を明記)。H1~H3のどれか未達ならNOT_VALIDATED。
