# TRIAL_PLAN_01(事前登録。Phase 1(d)、2026-10-31。本格Trialは委任_02。ここに書いた基準は結果を見た後に変更しない)

## 1. 目的・範囲
生成訳へ渡す**文脈入力**だけを変えて、文脈不足の誤訳(語義・指示対象・訳語整合)を減らし、正常な訳を悪化させないか。範囲外=Prompt本文・モデル(gpt-6-luna)・routing・verify基準文の変更(例外=因子V、下記)、独立品質アラーム(OPEN-636)、B3(REJECTED、再採用しない)。到達Status=VALIDATED / REJECTED / USER_DECISION_REQUIRED。Production採用・配線は禁止。

## 2. 評価セット(分割は記事単位で凍結)
母集団=公開済み10記事の生成訳 **61 part・310文**(`ev03/pool_all_generated_03.json`)。
- **dev(34 part・171文)**: X ai_chat_sponsored_persuasion / jwst_mystery_emission_line / moon_shrinking_reselect(21 part)、Y redelivery_fee_03(3)、Z melos_kphr_evidence_r3(10)。方式選択と閾値確認に使う。
- **held-out(27 part・139文)**: X meta_waddle_world / untidiness_family_resource(14)、Y surname_choice_01(3)、Z yuki_onna_01(10)。devでの選択・改善に**一切使わない**。dev確定後に初めて実行。
- 層: Family X/Y/Z、Std/Adv、種別(story/comment/preview/oneline)を両セットに含む。改善候補(文脈依存文)は事後に`ev03`の裁定+旗(中・軽NG、TERM候補)で特定し、**正常訳の悪化検知**は旗の有無に関係なく全文を対象とする(無作為抽出ではなく全件=標本誤差なし)。
- 任意 Stage 3: 承認済み訳のあるX/Y story part(金標準あり)から10 partをheld-out追加(A+採用候補のみ)。

## 3. 比較条件
方式 A(現行)・A'(Aの再生成=ノイズ基準)・B・C・D・E(`DESIGN_OPTIONS_01.md`)。devで全6条件。Fは「E適用後も訳語不整合(TERM)の改善が基準未達」の場合のみStage 2に追加。因子V(verifyに同じ文脈を付ける)は、devでG1〜G4を通った方式の最良1つに1回だけ追加。
- 実行: **Production関数 `er135_enduser_translate_01.translate_part` をimportして呼ぶ**(検査・対訳照合・再試行・モデル契約はそのまま)。文脈は`tools/ctx_probe_02.py`方式(Production `build_translate_prompt`の文脈欄に決定論の文listを入れる)。cache_dir=使い捨てtempdir、Production出力・キャッシュ・公開dir・`er*_output`・`user_test`へは書かない。Trial出力は`ev05_*`(dev)・`ev06_*`(held-out)のみ。
- 各条件は独立process(並列実行。理由=条件間に依存が無く、各自の使い捨てcache・出力dir)。1partの全条件は同一入力文・同一モデル。乱数seed固定は不可(APIは非決定)→ノイズはA'で測る。
- 記録: partごとに訳・translate/verify call数・usage(input/output/reasoning token)・cost_jpy・wall time・verify不合格理由・fail-closed有無・ledger追記。

## 4. ブラインド裁定
`ADJUDICATION_RUBRIC_01.md`。シート=(文ID, 英文, 前後文[裁定者の理解用。訳の対象ではない], 訳X, 訳Y)。X/Yは A対M を乱数で左右入替。方式名・費用・verify結果は伏せる。出力=改善/同等/悪化、重大度(重大/中/軽)、理由コード(CTX/MIX/NOISE/OTHER)。同一訳(文字列一致)は自動で「同等」(裁定対象から除く)。割れ/不確実は`exclude`、件数を報告。一次=実行層Sonnet(AIなので同系列の偏りあり)、**Fableが独立再裁定(10%以上+全重大)**し一次との一致率を受入評価に記載。
集計: (理由不問) と (理由一致) の2種。ノイズ補正=A'対Aの同じ集計を基準値とする。

## 5. 成功基準(事前登録。全てdevとheld-outの**両方**で満たすこと)
文はA(現行)との文単位比較。
- **G1(重大悪化)**: A=OK→M=重大NG の文 = **0**。
- **G2(中悪化)**: M対Aの「中以上へ悪化」数 ≤ A'対Aの同数 + 1。
- **G3(悪化率、全重大度)**: M対Aの悪化文率 ≤ A'対Aの悪化文率 + **3ポイント**。
- **G4(運用)**: ① fail-closed(英語のみ表示)のpart数 ≤ A、かつ ② partあたり平均 translate+verify call数 ≤ A × 1.25(再生成率の増加を抑える)。
- **B1(改善)**: Aで中・軽NGだった文のうちMで解消した割合(理由不問) ≥ A'の解消割合 + **15ポイント**、かつ(理由一致=CTX)で解消した文 ≥ 5(dev)/ ≥ 4(held-out)。[母数小のため絶対数の下限を併記]
- **C1(費用)**: 追加費用(再試行込みの実費の増分)/記事セット ≤ **1.0円**かつ総実費増 ≤ **+30%**(Aの実費比)。追加token(translate input)の方式別平均も報告。
- **T1(時間)**: part平均wall time ≤ A × 1.3。
- 判定規則: devでG1〜G4・B1・C1・T1を全て満たす方式のうち追加費用最小を1つ選び(同順なら文脈が小さい方)、held-outで同じ基準を判定。devで該当なし→REJECTED(基準変更で救済しない。元基準の結果を保持し、変更が必要なら別Trialとして理由と共に報告)。held-outで不合格→REJECTED(dev過学習)。A'のノイズが大きく差が判別不能(A対A'の悪化文率が8%超)→USER_DECISION_REQUIREDではなく「判別不能」として母数を増やす再設計を1回行い再報告。
- VALIDATED=dev・held-out両方でPASS。**Production採用・配線はユーザーの正式承認後**(CLAUDE.md「安全・承認境界」)。

## 6. 副作用の個別検査(全方式)
(1)MIX: 訳に英文対象外の情報(文脈文の固有名・数字・内容)が入った文を裁定で抽出 (2)訳語整合: 記事内の同一英語表現の訳語の種類数(A対M)を裁定者が主要語(df2〜8)で集計 (3)数値・構造の決定論検査の不合格率(Production Gate出力) (4)文数/段落対応(`build_ja_fields`成立率)。

## 7. 費用見積・Cap・止め線(gpt-6-luna、probe実測単価で積算)
probe実績: 費用 **1.0022円**(8 part-run、`ev04_probe/probe_result_02.json`)。1part-run費用 実測 X短part 0.036〜0.148円(verify不合格×2で悪化)、Z story part 0.137〜0.162円。
| 段階 | 実行 | 見積 |
|---|---|---|
| dev | A・A'・B・C・D・E の6条件×34 part(X21・Y3・Z10。1条件≈3.4円) | 約20.4円 |
| dev 因子V | 最良1方式+V | 約3.4円 |
| held-out | A・A'・採用候補・採用候補+V・(F)の5条件×27 part(1条件≈2.9円) | 約14.5円 |
| 任意Stage 3 | 金標準X/Y story 10 part×3条件(0.2円/part-run) | 約6円 |
| 小計 | | 約44円 |
| 再試行・誤差の余裕(+25%) | | 約11円 |
- **合計見積 約55円(±15円)。Cap提案 60円、止め線 48円(到達で停止して報告、追加が要る見込みが立った時点で上限拡大を申請)**。案件見積300円以下・承認済みScope内=PM_GOVERNANCE 7-7でAI自律範囲。日次1,000円内。量産単価への影響は本番採用後の追加費用で別途計上(DESIGN_OPTIONS_01: D最大でも+0.1円/セット)。本Trialの費用は開発費(量産単価に算入しない)。
- 裁定・集計はAPI 0(実行層の作業)。

## 8. probe(Phase 1、Cap 15円・止め線12円の範囲、実施済み)
X untidiness adv_19(Comment 4)とZ melos std_13を A/B/D/E で再翻訳(8 part-run)。実測=token・費用・時間・出力形式。結果と判明事項=CURRENT_STATE_01 §3・DESIGN_OPTIONS_01・`ev04_probe/`。出力形式(JSON `translations`)は全方式で契約どおり(parse不合格0)。**費用 1.0022円**(止め線12円の8.4%)。n=2 partのためgood/badの効果判定には使わない。

## 9. Production分離・安全
Trial専用dir(`docs/research/ENDUSER-TRANSLATION-CONTEXT-TRIAL-01/`)とtempdir cacheのみ書込。`er*.py`への変更0を終了時に`git diff --stat`で確認。flag・env・runner変更なし。失敗・停止時の成果物=本dirの途中結果とledger(Productionに影響する成果物なし)。独立品質アラーム(OPEN-636)・B3とは別軸で干渉しない。
## 10. 採用検討で整理する事項(Trial後。VALIDATED時のみ)
既存の生成訳仕様(OPEN-618系・ja_source=generated・fail-closed)、X/Y/Z共通、retry/fallback/resume(キャッシュ鍵への文脈・方式ID、公開済み記事の再produce時の移行)、verify入力、独立品質アラームとの役割分担、Opus独立レビュー(条件A新構造/条件C採用前)、ラベル文言「同じパートの他の文」。
