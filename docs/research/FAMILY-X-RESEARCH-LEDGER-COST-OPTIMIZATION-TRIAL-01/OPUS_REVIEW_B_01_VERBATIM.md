> 注記: 本文は2026-10-17のOpus独立技術レビュー_B(条件A、確認パス実装)subagent transcriptから無改変で逐語抽出(この1行のみ付加)。

## 総合判定: GO(有料実行の前に直すべきコードはない)
理由: 確認パスの流れ(ループ・上限・確定時の防御・1a補正の復元・費用の分け方・隔離)に、誤った確定、無限ループ、元データの書き換えにつながる欠陥は見つからなかった。ただし評価の手順と注記は修正が必要。下のR-B1/R-B9-1/R-B7/R-B5の注意点は、有料実行のあと評価(R-07とブラインド評価)を始める前までに、評価手順へ反映すること(JPY0、コード変更は不要)。

---

**R-B1 D1(ii)の確定条件の十分性 — 判定: 軽微(測定に留めるのが妥当。機械的な判定条件は追加しない)**
- 根拠: OPUS_REVIEW_A_01_VERBATIM.md:51 によると、Fact本文の留保は後段のproducerが決定論的に付ける。断定が残り得る経路はStoryline行がWriterへのテーマ文になる部分だけ。M0(Production基準)でも、B3はタグを見たうえでStoryline行を自由に書く。D1(ii)によって案2の情報条件はM0と同等以上になる(確認noteで理由も渡すため)。
- Storyline/Briefに留保表現があるかの文字列検査を判定条件(Gate)として加えると、M0にはない条件を案2にだけ課すことになり、方式比較が不公平になる。またAMBIGUOUS時の再生成ルールは新仕様にあたる(前回R-07の結論と同じ)。そのため測定に留める。
- 修正案(JPY0、評価手順への追加): R-07の人手判定を、M0/M0b/M1/M2c/M3c/1bの全方式に同じ基準で行う。下のR-B9-1にあるとおり、Storyline冒頭の汎用ラベル「【独立検証前の編集仮説】」は、Fact固有の留保として数えないと明記する。判定がNGだった場合は「確定条件は満たしたが断定が残った」として別集計し、Trial後のユーザー判断事項にする(前回の決定どおり)。

**R-B2 合算上限2回 — 判定: 問題なし(報告での注記が必要)**
- 根拠: ユーザー§2は、確認パスを「B3にストーリー構成を再評価させ、必要に応じてFactを再選定する」と書いている。確認パスは再選定の一形態であり、合算で2回とするのが文言にもっとも忠実で保守的な解釈。確認パスを別枠にすると追加B3が最大4回になり、上限の緩和=承認範囲外の疑いが生じるので、採らない。
- 不当に不利になるか: 選定してから検証する方式は、検証後に追加のB3呼出が要る。そのため未成立が増えるのは方式そのものの性質で、測るべき対象である。ただし報告では次の2点を必ず書く: (1)未成立を`unmet`の内訳(REJECTED_SELECTED / AMBIGUOUS_NOT_CONFIRMED)で分けて示す。(2)M0系は構造上つねに確定条件を満たすので、「確定条件のもとでの成立率」は案2だけの指標であること。
- 注意: 「上限に達した時点のBriefは実際には留保していた」という未成立もあり得る。ユーザーの「上限到達時は未成立」に従って成立扱いには戻さない。必要なら参考値として、上限時点の選定を人手で見た所見を併記してよい。

**R-B3 再帰・即確定・誤確定 — 判定: 問題なし**
- 根拠: er082_rlct_trial_01_lib.py:695-767。ループの各周は、確定・上限での未成立・技術失敗での未成立のどれかで抜けるか、`b3_used`を必ず1増やす。`b3_used`は`max_reselect`で上限がかかるため、無限ループにはならない。
- 新しく選ばれたFactがAMBIGUOUSだった場合: そのFactは選定時の`visible_now`に入っていない(:743)ので、`_ambiguous_unseen`がREQUIREDを返す。枠が残っていれば2回目の確認パス、なければUNRESOLVED(:728-734)。test_r3/r4/r5bでこれらの経路が再現されている。
- VERIFIEDだった場合: :719-727 で即確定する。上限の判定(:728)は確定判定より後にあるので、2回目の呼出の結果が適合していれば正しく確定する。
- 防御: `_finalize_sel`(:772-775)がREJECTEDの混入と、B3に見せていないAMBIGUOUSを再検査している。検証結果が欠けたFactは安全側でAMBIGUOUSになり、これも未提示として扱われる(:709-711)。

**R-B4 候補Ledger上のAMBIGUOUS表示 — 判定: 軽微(設計書の記述修正)**
- 根拠: 「断定禁止」タグはLedger本文に出ている(er003_v1_en_direct_vfl_01_generate.py:292)。一方で理由の行は`fact.get('ambiguity') or v.get('verification_notes')`(:305)なので、Researcherの`ambiguity`欄が空でなければVerifierの理由はLedgerに出ない。理由が確実に渡るのはnote側で、今回の確認対象のAMBIGUOUSは[:600]で切り詰め(lib.py:642)、それ以外の検証済みFactは[:300](:618, :648)。初回より後のB3呼出には必ずnoteが付くので、「タグ+理由」は実際には満たされている。ただし理由の経路はLedgerではなくnoteである。
- 修正案: TRIAL_DESIGN_03 D1(ii)の「候補Ledger上で…verification_notes付き」を「Ledgerでタグ+notes(Researcherのambiguity優先)、Verifierのnotesはextra_noteで渡す(300/600字で切り詰め)」に直す。コード変更は任意。以前の回で検証されたAMBIGUOUSが[:300]で切られる点は、M0のLedgerより情報が少なくなるわけではないので、そのままで可。

**R-B5 1a補正の再利用忠実性 — 判定: 問題なし(注記1点)**
- 根拠: er082_rlct_trial_01_run.py:153-199。判定は`verify_r*.json`の`parsed`から理由ごと復元し、`final_verdicts`と全件照合して、一致しなければSTOPする。最終selの保存物も選定IDと照合している。`sel_visible`を`round < r_last`で決める処理は、「B3呼出rはそれより前の回の判定しか見ていない」という構造と合っている。費用は`_cost_for`の接頭辞に`prefix + "|"`を付けている(:57)ので、M2とM2cが混ざらない。
- `cost_production_equivalent`: 新設計で最初から実行した場合の呼出列(初回B3 → 選定Factの検証 → 確認B3 → [新規Factの検証])と、補正で行う呼出列は構造上同じ。違うのは実行時刻だけで、近似の精度は高い。Sonnetの懸念(c)の記述で足りる。
- M3cがM2の初回B3を共有するのは、設計4-1と前回R-12のとおりで妥当。
- 注記(必須): M2cとM3cの確認B3は、同じselと、ほぼ同じ判定・理由を入力にした独立した2回の呼出である。そのためM2cとM3cのBrief差は、主にB3の出力の揺らぎであり、案1の上限の効果ではない。報告では「M2c↔M3cの差=B3の揺らぎの標本」と明記する。

**R-B6 CoffeeのPASS照合 — 判定: 問題なし**
- 根拠: conform_check.py:42-61。Coffee M2はround0が[F01,F07,F09,F15]で、F07がREJECTED、他の選定FactはVERIFIEDだった(result.json:12-52)。round0の選定にAMBIGUOUSがないので、新設計でもnoteは`build_reselect_note`と同じ文面になる(lib.py:633-634)。つまり実際に通った経路そのものが新設計と同一である。
- 「REJECTEDを単純削除しただけ」かどうか: 最終選定は初回からF07を除いた集合だが、B3がStoryline自体を書き直している(b3_initial.json:3 と b3_reselect1.json:3 を比べると、カフェの仕入れの記述が消えている)。機械的に削除しただけのものではない。
- 任意の改善(JPY0): conform_checkに「最終選定=前回選定からREJECTEDを引いた集合か」と「Storylineが変わったか」の列を足すと、この確認をファイル上の証拠として残せる。

**R-B7 1bと1aの方式間条件同一性 — 判定: 軽微(報告への注記で対応)**
- 同一の設計と言える範囲: 5記事のM2/M3列は、Coffee=元のM2/M3(経路が新設計と同じ)、inbound=M2c/M3c、1b=新設計で集計すれば、処理フローは同一である。inboundの元のM2/M3は、旧設計の参考行としてだけ並べる(5記事の集計には入れない)。
- 注記案: 「inboundのM2c/M3cは、10-17に行った初回B3と検証の結果を再利用し、確認B3だけを後から実行した。Coffee M2/M3は旧harnessで実行したが、選定AMBIGUOUSがなかったため経路は新設計と同一。1bは新設計で通しで実行。評価者と評価日は1aと1bで異なる。」

**R-B8 Production混入 — 判定: 問題なし(Grepで独立に確認)**
- リポジトリ全体の`*.py`で`er082`をGrepした結果、ヒットはer082_*の6ファイルだけだった(er002_/er053_/er019_などからの参照はゼロ)。bat/ps1/cmd/sh/env/toml/yaml/cfg/iniでもヒットなし。なお、test_o(test_01.py:298-306)が調べるのはルート直下の*.pyだけだが、今回のGrepはサブディレクトリも含めて確認した。
- 未確認: commit 9d0c41473の変更ファイル一覧(gitは実行していない)。

**R-B9 有料実行前後に対応すべき点(優先度順)**
1. [高] Storylineに「【独立検証前の編集仮説】」というラベルが混入している。inboundのM2/M3の実測Storylineはこのラベルで始まっている(inbound_tourism/M2/result.json:62、M3:61)。Coffeeと他の方式にはない。原因は、`allow_unverified`時のPrompt文言(lib.py:504)を受けてB3が付けたと考えられる(推定)。確認パスでも同じ文言を使うので、M2c/M3cや1bで再び出る可能性がある。影響は3つ: (a)ブラインド評価で方式がわかってしまう。(b)人手判定でFact固有の留保と取り違えるおそれ。(c)前回R-07の経路により、このラベルがWriterへのテーマ文にそのまま入る。Promptを変えると1aとの条件が変わるので、変えない。修正案(JPY0、評価手順): ブラインド評価ではラベルを隠す。R-07ではラベルを留保として数えない。ラベルの出現件数を方式別に、方式固有の欠陥の候補として記録する。
2. [中] M2c↔M3cの差の読み方(R-B5の注記)と、合算上限による未成立の内訳表示(R-B2)を、STAGE_1A_EVAL/1Bの評価手順に事前に書いておく。
3. [低] TRIAL_DESIGN_03 D1(ii)の文言修正(R-B4)。

---

**Fableへの注意(ユーザー判断が必要になり得る点)**
- R-07の測定で、M2c/M3c/1bのM2/M3に「確定条件は満たしたが、Storyline行でAMBIGUOUSを断定」が0件でない場合、留保表現の機械Gateや再生成ルールを追加するかは新仕様になる。Trial後のユーザー判断事項である(前回の決定を維持)。
- 「【独立検証前の編集仮説】」ラベルを、案2を本番化する場合に除去する仕組みを入れるかどうかは、Production挙動の変更にあたる。今回のTrial内では、測定と評価時に隠す処理だけを行う。
- 合算上限のために未成立が多く出た場合、確認パスを別枠にするかどうかは、上限の変更=ユーザー判断事項。Fableが独自に緩めないこと。

関連ファイル:
- C:\Users\tensh\eigo-radio\er082_rlct_trial_01_lib.py (504, 512-540, 607-653, 656-785)
- C:\Users\tensh\eigo-radio\er082_rlct_trial_01_run.py (55-63, 150-267)
- C:\Users\tensh\eigo-radio\er082_rlct_trial_01_conform_check.py
- C:\Users\tensh\eigo-radio\er003_v1_en_direct_vfl_01_generate.py (279-309)
- C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\inbound_tourism\M2\result.json (62)
- C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\coffee_prices\M2\_work\b3_initial.json, b3_reselect1.json
- C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\TRIAL_DESIGN_03.md