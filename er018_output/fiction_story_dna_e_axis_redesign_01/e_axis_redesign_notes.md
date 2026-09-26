# e_axis_redesign_notes.md

管理ID: FICTION-STORY-DNA-E-AXIS-REDESIGN-01
対象: Run5(Coverage Run)のE軸母集団を、新E軸のどの値に対応させるかの設計判断記録。

## 既存コードの参照方法

`er018_fiction_core_provocation_prompt_bias_retrial_01.py`(前回Trial、旧E軸)
の`select_dna()`は、Run5(`is_coverage_run=True`)でのみ以下を実行する。

```python
e_idx = rng.choice(E_FUTURE_VALUE_INDICES)
values["E"] = list(AXIS_DEFS["E"]["values"][e_idx])
```

旧`E_FUTURE_VALUE_INDICES = [1, 2, 3]`は、旧E軸の値リスト
`["contemporary everyday life", "a near future", "a greatly changed future",
"a world with technology or institutions that do not exist in reality",
"a supernatural or fantastical world", "a world almost identical to reality
except one rule is different"]`のうち、index1/2/3
(`a near future` / `a greatly changed future` / `a world with technology or
institutions that do not exist in reality`)、すなわち「Future系3値」を指して
いた。委任文(前タスク)ではこれを「Run5 Future Coverage Run」と呼んでいた。

新E軸(本タスクでユーザー決定済み)は以下の6値である。

```
0: contemporary everyday reality (現代の日常)
1: realistic but socially unusual situation (現実的だが社会的に珍しい状況)
2: realistic but emotionally unusual situation (現実的だが感情的に珍しい状況)
3: future (未来)
4: reality with one changed rule (ルールが1つだけ違う現実)
5: supernatural / fantastical world (超自然・幻想的な世界)
```

新E軸には旧E軸の「a near future」「a greatly changed future」に相当する複数の
未来段階が存在せず、「future」という単一値のみが対応する。したがって、旧
`E_FUTURE_VALUE_INDICES`が指していた「Future系3値」という集合を、新E軸の
どの値集合に対応させるかは、既存コードの参照方法(indexリストの中身)だけでは
一意に決まらず、設計判断が必要だった。

## 検討した2案

**(a) `future`の1値のみに対応させる**
`E_FUTURE_VALUE_INDICES = [3]`(indexは3のみ)。
- 根拠: 旧仕様の呼称は「Future Coverage Run」であり、字義どおり読めば
  「未来」を確実に引かせることが目的だったと解釈できる。新E軸では「未来」に
  相当する値は`future`(index3)の1つだけであり、追加解釈を挟まず対応させら
  れる。
- 欠点: 旧仕様は実質的に「Future系3値のどれか」という多様性を持たせていた
  (単一の`a near future`に固定してはいなかった)。新設計で単一値に固定すると、
  Coverage Runの「複数候補からランダムに引く」という構造上の役割(委任文が
  維持を求める「Run5 Coverage(E軸強制)の仕組み」の一部)が実質的に消え、
  Run5は常に同じE値になる(=多様性ゼロ)という副作用がある。

**(b) 非現実系3値(future / reality with one changed rule / supernatural or
fantastical world、index [3, 4, 5])に対応させる**
- 根拠: 旧E軸のFuture系3値は、いずれも「日常でない・非現実的な世界設定」
  という共通点を持っていた(near future/greatly changed future/technology-
  institution worldは全て「現実にない」設定)。新E軸で最も近い意味的グループ
  は、非現実寄りの3値(future/one changed rule/supernatural)だと解釈できる。
  これを採用すると、旧仕様同様に3値からランダムに1つ選ぶ構造(多様性)を維持
  できる。
- 欠点: 「Future」という呼称そのものと一致しない値(one changed rule、
  supernatural)まで含めることになり、新しい解釈(「非現実系」という新しい
  くくり)を追加することになる。委任文では「新しい解釈を挟まない対応」が
  望ましいとされている場合、(a)より解釈の追加が大きい。

## 実行した案と理由

**実行: (a) futureの1値のみ(`E_FUTURE_VALUE_INDICES = [3]`)**。

理由: 委任文の指示どおり、「旧仕様『Future coverage』の字義に最も近く、
追加解釈が最小」という基準で(a)を選択した。(b)は「非現実系」という新しい
分類基準をコード内に持ち込むことになり、これは追加の設計判断(=E軸の値
リスト以外の変更)に近いと判断した。

**これは暫定判断であり、Production採用ではない。** Run5が常に同じE値
(`future`)になり多様性を失う点は、REPORT §2/§9で明記し、必要であれば
USER_DECISION_REQUIRED(将来、Coverage Run自体の設計を見直すか判断)として
報告する。今回のTrialでは、Run5のE軸強制という「仕組み」自体(委任文が
変更禁止と明示)には手を加えていない(`rng.choice(E_FUTURE_VALUE_INDICES)`の
コードパスは維持、リストの中身だけを変更した)。

## 影響範囲の確認(乾式dna step実測、詳細はdna_diff.md)

- Run1-4(非Coverage): 各axisの選択されたindexは旧→新で完全一致(E軸の値
  リストが旧新とも6要素のため、`rng.randrange(6)`の返り値が同一)。ラベルの
  みが新E軸の値に変わった。
- Run5(Coverage): 旧`rng.choice([1,2,3])`(3要素)と新`rng.choice([3])`
  (1要素)は、Python標準ライブラリの`random.Random._randbelow`が消費する
  乱数ビット数が要素数に応じて異なるため、E軸自体の選択結果は「常にindex3」
  で確定するが、**後続のC/D軸の値選択に使われる乱数状態がRun5のみ変化し、
  結果としてC/D軸の値が旧Trialと異なるものになった**(旧: C=a reversal,
  D=a hospital / 新: C=a loss, D=a public space)。E軸を持たないRun(Run2)や
  Coverage Runでない他のE軸持ちRunには影響しない。詳細はdna_diff.md参照。
