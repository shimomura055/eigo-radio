# Opus独立技術レビュー(条件A) FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01 / 委任_01設計+未配線実装

## 総合判定: 条件付きGO
Comment 3の考え方(役割文は`a2gen.COMMENT_2_ROLE`をそのまま使う、Part 3は文単位で切り出す、割合では切らない、LLMは使わない、C1/C2/C4/Previewの呼出は変えない)は、ユーザー決定と整合しています。ただし配線前に直すべき欠陥が2つあります。
- 失敗時に下流を止める仕組みが、実際には既存コードに存在しません。
- AI島をComment 3だけ作り直す経路が、現行コードでは実現できません。

M-1〜M-5を委任_02の配線と同時に満たすことを条件に、次工程へ進んでよいと判断します。

---

## 必須(M)

### M-1 結果文の検出漏れ(否定の短縮形・助動詞の否定)を塞ぐ
- 根拠: `er019_family_x_std_comment3_z_method_01.py:42`
- 否定の結果を表す語は`(had|has|have|did|does|do|was|were|is|are) not`と`never`/`no longer`だけです。次の書き方はすり抜けます。
  - 短縮形: `didn’t` / `wasn’t` / `can’t` / `won’t` / `couldn’t` / `doesn’t`(本文コーパスは曲がった’を多用)
  - 助動詞+not: `will/would/could/can/may/might/should not`
  - `cannot` 単独(paycheckで止まったのは`prove`に当たったため)
  - 例:「It didn’t work.」「Experts say the plan will not help.」はどちらもexcerptとして渡ってしまいます。
- 重要な理由: X Stdには、Part 3の先取りを禁じるPrompt文がありません。
  - 流用元の`COMMENT_2_ROLE`(`er003_v1_iran01_a2_generate.py:137-146`)には「後半の結論を言うな」がありません。
  - `SUPPORT_PROHIBITIONS:108`の禁止はPoint One/Twoの答えについてで、XにはPointがないため効きません。
  - 旧X C3役割文(`er019_family_x_audio_plan_01.py:215`)にあった「第3部の結論を先に言ってはいけません」は、Z方式に変えると消えます。
  - 新Prompt文を作れない制約の下では、**先取りを防ぐ主な手段は「入力の切り出し」だけ**です。事後lintは、excerptに混入した結果を構造上検出できません(excerptは「見えている本文」扱いになるため)。
- 要求:
  1. 上記の否定形をRESULT_SENTENCE_REへ追加する。
  2. 7記事の机上表を再生成し(API 0)、fallback件数の変化を記録する。
  3. 短縮形・助動詞否定のtestを追加する。

### M-2 fail-closed後の下流停止は「既存の扱い」に任せられない(新設が必要)
- 根拠: 設計書`WIRING_DESIGN_01.md:34`は「下流は既存のsupport失敗扱い=停止/HR」としていますが、実コードにそういう扱いはありません。
  - `run_family_x_a2_scaffold`は`text=None`のまま`a2_support_texts.json`を保存します(`er019_family_x_audio_production_runner_01.py:359`)。
  - scaffold本体はsupportのstatusを記録するだけで、KP(有料)へ進みます(`:867→:875`、`:905`)。
  - TTSは`support[name]`を検査せずに音声生成へ渡します(`:2011`、`:2065`)。
  - これは既存の技術失敗(TECHNICAL_GENERATION_FAILED)でも同じ穴ですが、今回`COMMENT3_SPOILER_LINT_FAILED`という新しい失敗経路が増えるため、配線と同時に塞ぐ必要があります。
- 要求(最小構成):
  - (a) C3が非OKなら、その場でC4/Previewを呼ばない(無駄な費用を防ぐ)。
  - (b) `a2_support_texts.json`を書かない。少なくともnullを含む形では書かず、却下文と監査情報は`audit/`側にだけ保存する。これで`scaffold_only=="kp"`経路(`:844-855`、ファイルの存在しか見ていない)がnull入りファイルを拾う道を断ちます。
  - (c) level dirへ専用marker(例`support_stage_failed.json`)を置き、`result[level]["support_stage_status"]`を記録して`break`する。KP・Part 1・Part 2のfinalizeを実行しない。`main()`は非0のrcで終了する。成功時はmarkerを削除する(KP markerと同じ型、`:895-898`)。
  - (d) TTS入口(`:2011`直後)に、5キーすべてが空でない文字列であることの検査を入れ、満たさなければ有料TTSの前に例外で止める。b1bも同じ形にするのが望ましいですが、b1bはOutOfScopeなので記録だけでも可です。
  - (e) 停止時は「次の一手」を表示する(`--stage scaffold`の再実行。KP未実施なので`_resume_review`はFalseになり、supportを再生成)。
- 観点11との関係: 止めることが常に安全側とは限りません。ただし最終lintまで失敗するのは、実質的に言い回しの問題(下記R-1)で起きるものです。このとき偽のOKを公開物に残さない、という意味でfail-closedは妥当です。発生頻度はR-1で下げてください。

### M-3 「Comment 3だけ再生成」の正式経路を新設する(AI島Standard再制作の前提)
- 根拠: 設計(g)「実Prod経路でAI島Standardのsupport再生成(Comment 3のみLLM 1回)」は、現行コードでは成立しません。
  - AI島はKP reviewが有効なので、`--stage scaffold`を再実行すると`_resume_review`(`:843`、`:856-863`)でsupport生成自体がskipされ、**Comment 3は再生成されません**。
  - 逆にKP reviewが無効と判定されると`run_family_x_a2_scaffold`が5件すべてを再生成し、C1/C2/C4/Previewの承認済み文面が変わります。これはユーザー指示4章「承認済み内容は維持」「変更が必要な音声のみ」に反します。
- 要求:
  - Production runnerに、Comment 3だけを再生成する経路を追加する(例`--regenerate-support comment_3`)。Z側`run_support_std`の`prior`再利用(`er062_family_z_writer_01.py:1252-1274`)と同じ考え方です。
  - 中身:
    - 既存の`a2_support_texts.json`を読む。
    - 初回生成経路と**同一のhelper**(例`_a2_comment3_z(client, parts)`=`run_comment3_z_method`+`_a2_run_support_text_j2`+`_a2_support_model()`の束縛)でC3だけを生成する。
    - 他4キーのshaが書込み前後で一致することをassertする。
    - KP・Part 2・study_textには触れない。
    - `audit/a2_support_generation.json`は上書きせず、C1/C2/C4/Previewの元のaudit記録を保持したままC3のauditを追記・マージする。
  - TTSは既存の`--only-segments comment_3`で回し、他の音声は`validation_inheritance`で引き継ぐ。
  - 初回生成経路(`:342-344`)も同じhelperを呼ぶようにし、2経路の仕様が分かれないことをtestで固定する(ユーザー要求3章-2「regenerationでも一貫」)。

### M-4 runtime evidenceは「初回経路」と「再生成経路」の両方で取る
- 記録やfake testだけで受け入れない、という既存の教訓(API引数+音声の証拠)に従います。
- 再生成経路(AI島Standard、公開物): 次を保存する。
  - 実際のAPI呼出の`prompt`全文(`COMMENT_2_ROLE`で始まり、`【これから聞く本文(後半)】\nThe researchers also erased …`を含み、`went down`と`Even so`を含まないこと)
  - `response_id`、model
  - `comment3_z_audit`(mode=Z_EXCERPT、role_sha256、passed_excerpt_sha256、part3_sha256)
  - 他4キーのsha不変の証拠
  - comment_3.wavのTTS/ASR結果
  - 公開ページのcomment_3文面が新文面と一致すること
- 初回経路: 実在のProduction関数`run_family_x_a2_scaffold`を、scratch out_dirで1回だけ実API実行する(LLM 5回、約0.5円)。公開物には使いません。
  - 狙い: 「正式初回生成経路で発火した」ことの直接証拠を取る。
  - 代替: 次の新規X Std記事の初回生成で取る。ただしその場合、PRODUCTION_WIREDの報告はその実行後になります。
- Part 3の先取りがないことの検証(ユーザー要求3章-5)は次の3点で行う。
  - (i) 7記事の切り出し表(M-1適用後)
  - (ii) AI島の実出力をFableが目視で照合する
  - (iii) lintの結果
  - lintは「渡していない部分」しか見られないので、lintだけで先取りなしの証明とはしないこと。

### M-5 監査記録を十分にする
- 根拠: 各attemptのentry(`er019_family_x_std_comment3_z_method_01.py:219`)は、status/lint/context_shaしか持ちません。lint不合格だった1回目・2回目の生成文、response_id、model、prompt shaが残りません(`last`以外は捨てられる、`:216-218`)。
- 要求:
  - 各attemptに`text`(却下文)、`response_id`、`model`、`prompt_sha256`、J2適用有無を記録する。
  - 入力として使った`parts`のsha(part1/part2/part3)を記録する。
  - `method_version`を`scaffold_run_summary.json`のlevel別結果にも記録する(例`comment3_method: FX-STD-COMMENT3-Z-V1`)。

---

## 推奨(R)

### R-1 CONCLUSION_WORDの偽陽性を下げる
- 根拠: `JA_CONCLUSION_WORDS`(`:147`)
- 「では、最終的に塔作りの結果はどう変わるのでしょうか」「結局、何が分かったのでしょうか」「これで証明できるのでしょうか」は、役割どおりの「後半への問い」なのに違反になります。
- 3回とも当たるとfail-closedになり、記事が止まります(D損失)。
- 提案: 該当語を含む文が疑問文(「か。」「か？」「?」で終わる)なら除外する。決定論のまま、閾値の変更ではなく誤検出の除去にとどめる。
- 「二つ」によるWITHHELD_NUMBERの偽陽性は頻度が低く、retryで吸収できるので許容します。

### R-2 結果語彙の追加候補(M-1とは別。fallbackの増加と天秤)
- 候補: `worked|failed|succeeded|won|lost|approved|rejected|ruled|decided|agreed|chose`、文頭の`So|Thus|Therefore`(例: moonのPart 3「So the Moon may have cooled…」型)、`Still`(カンマなし)、`most|none`
- 7記事表でfallbackが4/7を超えるなら、追加を見送るか語を絞り、判断理由を記録する。
- 新しい品質基準の追加ではなく、承認済みの「先取りしない」の実装精度の範囲です。

### R-3 方式の混在(resume・作業途中のrun)
- 配線時点で、support生成済みで未公開のX Std runを列挙し、該当があればM-3の経路でC3だけを作り直すかを決める。
- `_resume_review`/`scaffold_only kp`の再利用時には、`audit/a2_support_generation.json`の`comment3_z_audit.method_version`の有無をsummaryへ記録する(WARN)。
- 旧仕様で承認済みの既存記事の再作業を止めないよう、hard STOPにはしない。

### R-4 旧`FAMILY_X_A2_COMMENT_3_ROLE`は撤去を推奨(共通Charter原則8: 不要になった旧ルールの撤去確認)
- 配線後はProductionで参照されなくなり、誤って再配線される余地だけが残ります。
- 参照は次の3か所のみ(Grepで確認済み)で、小規模な変更です。
  - `er019_family_x_audio_production_runner_01_test_01.py:274,281`(役割文リストから外す)
  - `er019_family_x_style_profile_01_test_01.py:593`(このassertionを削除、またはC4側の検証へ置き換え)
  - 新testのLEGACY pin(`_test_01.py:212,224,268`)
- 追加test: 「runnerのソースが旧C3役割文を参照しない」ことを固定する。
- 旧文面はSSOT(DECISION_LOG)に履歴として残る。

### R-5 C2とC3で役割文を共用することへの対応
- AI島の実例では、C2(既存)もC3(新)も「〜しました。では、〜のでしょうか。」という同じ型になります(COMPARISON_01.md:39,64)。
- ユーザーはTrialの文面を見たうえで採用しているので、Prompt修正はしない(制約どおり)。
- 対応は次の2点に限る。
  - Zの`compute_support_overlap_notes`と同等の、非blockingの4-gram重複メモをC2×C3についてauditへ記録する(Gateにしない)。
  - FableがAI島の受入時にC2/C3の内容重複(同じ1点を回収していないか)を目視で確認する。
- 内容が実際に重複して試聴に支障が出た場合に限り、ユーザーへ進言する。

### R-6 AI島のparts入力を確定する
- Trial時の`parts.json`は「AIs sent」ですが、完成版の音声はLocal Rewriteで「AI agents sent」になっています(METHOD_DIFF_01.md:36)。
- C3の入力には、公開中の本文と一致するpartsを使い、そのshaをauditへ記録する。不一致なら差分と採用理由を明記する。

### R-7 配線後のtest
- 未配線pinのtest(`_test_01.py:265-272`)を反転する。
- 配線後のtestには次を含める。
  - excerptありのケース(現在のfake parts「P3 text. It rose…」は2語でfallbackになり、Z_EXCERPTを検証できない)
  - C3にJ2が適用されること
  - 通常時のLLM呼出が5回であること
  - C3失敗時はC4/Previewを呼ばず、markerを置き、null入りの`a2_support_texts.json`を書かないこと
  - b1bのscaffoldが不変であること(既存のX_B1 pin)

---

## 論点ごとの結論(参考)
1. **fallback時の役割文はZ(COMMENT_2_ROLE)のままでよい。** 旧X C3役割文へ戻すべきではありません。
   - ユーザー仕様の「1点回収+後半への具体的な問い+原則1〜2文」は役割文の側で定まる要件です。旧役割文(2〜3文で整理)へ戻すと仕様違反と方式の混在になります。
   - fallbackになる3本(coffee/moon/small_bag)は、Part 3冒頭そのものが結論・答え・留保です。ユーザーの「結論・重要な結果を先取りしない」「一定割合を無条件に渡さない」を優先すると、渡す範囲が0になるのは仕様の範囲内の結果です。
   - 例: moonはPart 2末尾の「What matters is how well it holds heat in.」でPart 3への問いを立てる材料がそろっており、Part 1+Part 2だけでも問いを作れます。
   - ただし、fallback率(現状3/7)と理由は完了報告に明記してください(隠さない)。
2. **lintは補助線と位置づける。** 渡していない文はLLMが見ていないので、WITHHELD系の違反は偶然の一致か推測でしか起きず、主な防御は入力の切り出し(M-1)です。日本語の言い換えによる偽陰性は、この構造では「excerpt内の結果を言い換えた場合」に集中し、lintでは検出できません。LLMによる判定は費用と再現性の面から入れず、M-1とFableの目視で補う方針で妥当です。retry1回→Part1+2へ縮退→fail-closedの流れ(最大LLM 3回、技術retryを含めても約0.3円)は、量産単価への影響が無視できる範囲で妥当です。
3. M-2のとおり。
4. 技術retryは`run_support_text`内部の2回(`er003_v1_iran01_a2_generate.py:207-235`)のまま整合しています。Local Rewrite系にComment文面をLLMで再生成する経路がないことは設計書の確認を採用します(未再検証)。もし将来comment_3の文面を後から編集する経路ができたら、`comment3_spoiler_lint`を再適用してください(決定論・費用0)。`audit/a2_support_generation.json`を読むX側の処理はなく(Grepで確認済み)、キー追加による副作用はありません。
5. C1/C2/C4/Previewは、fake client経由で(役割+context)全文sha・呼出順を固定するtestがあり、実効的です。Y/Zが新moduleをimportしていないことの確認も有効です。旧定数はR-4のとおり。
6. R-5のとおり。新Prompt文を作らない制約の範囲では、非blockingの記録と受入時の目視が最小の差分です。

## 委任_02への具体的要求(まとめ)
1. M-1(regex修正+7記事表の再生成、API 0)
2. M-2(停止の配線とTTS入口の検査)
3. M-3(初回生成と再生成で共通のhelper+Comment 3だけの再生成経路)
4. R-1/R-4/R-7を実装・test
5. 初回経路のruntime evidence(scratch、約0.5円)と、AI島のComment 3再生成(約0.1円)→TTS(comment_3のみ)→ASR→組立→公開検査を実施し、M-4の証拠を保存
6. Fableの受入で、C3の先取りなし・C2/C3の重複・他4キーのsha不変を確認する

## ユーザー判断が必要な点
現時点ではありません。
- fallback率3/7は、ユーザーの2条件(先取りしない・割合で渡さない)の帰結として仕様の範囲内と判断し、完了報告で開示すれば足ります。
- 前提: M-1/R-2の適用後にfallbackが過半(4/7超)になり、「Part 3冒頭を限定的に参照する」が実質的に働かない状態になった場合に限り、現状・原因・代替案を整理してユーザーへ進言してください。
