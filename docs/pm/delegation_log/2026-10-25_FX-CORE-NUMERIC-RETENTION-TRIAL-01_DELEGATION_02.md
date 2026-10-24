# 委任文(Fable→sonnet-worker)
管理ID: FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_02(Opus条件A必須修正M1〜M5+推奨R1〜R5の反映→較正[0円]→DEV/Trial実装(er115)→Phase 1 月の記事→事前登録基準を満たせばPhase 2 過去記事へ継続)
前提: 委任_01(RESULT_PACKET_FXNR1.md、DESIGN_01.md、ROOT_CAUSE_02.md、commit e7f649a1d)。**Fable判断: Opusレビューと設計は実質一致(O3採用)、新仕様のProduction採用は含まない、DEV/Trial専用、予算は自律枠(300円以下)内→案件上限を200円から230円へ更新(Fable設定値の変更、ユーザー承認枠の変更ではない)。Phase 1≤120円、Phase 2≤115円。M1〜M5反映後にPhase 1へ進んでよい(Fable Go)。**

## 0. 最初に
- `docs/research/FX-CORE-NUMERIC-RETENTION-TRIAL-01/OPUS_REVIEW_01.md` を作成し、§1のOpusレビュー全文を保存(先頭に「Fable転記、2026-10-25、条件A」)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 502 --out docs/pm/delegation_log/2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_DELEGATION_02.md`。冒頭が「管理ID: FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_02」と一致するか確認、不一致なら index 500〜505 を順に試す(`--index -1`不可)。

## 1. Opusレビュー全文(逐語)
```
# Opus独立技術レビュー(条件A) FX-CORE-NUMERIC-RETENTION-TRIAL-01 Phase 1前の設計

## 判定: 必須修正あり(設計見直しは不要)
O3の骨格は妥当です。B3 StorylineからR0の「テーマ：」行へ数値を渡し、derive_ranksのStoryline優先(in_story)と決定論の保持Gateを組み合わせる構成です。
- 根本原因(R0の1段だけで落ちる)に合った位置に対策を置いている。
- 追加のLLM呼び出しは0。
- 「全部必須」と「重複した選定システム」の禁止を守っている。
- 却下案O1/O2/O4/O5/O6の扱いも妥当。過去の不採用方式の再導入はない。

ただし、月の台帳の実データで具体的な失敗経路が見つかったため、下記M1〜M5をPhase 1前に直す必要があります。

## 必要か/推奨構造/リスク/代替案(要約)
- **必要か**: 必要。今は保持の担保が仕様上どこにもない(規則5は「使ってよい」という許可だけで、Gateもない)。一方、月の42〜46mはユーザーが「必須」と明示している。
- **推奨構造**: O3に次の3点を加える。
  1. Storylineに入った数値の決定論検証(M1)
  2. 時間・前提の数値をGate対象から外すこと(M2)
  3. 再実行枠の共有(M3)
- **主なリスク**: B3がStorylineに周辺数値を入れる(台帳の実例あり)、照合Gateの誤判定、Writer・B3の結果のばらつき(標本が少ない)。
- **代替案**: Storyline方式が成立しない場合は、撤退ではなくR5(B3の構造化欄)へ切り替える。

## 必須修正
**M1 Storylineに入った数値の検証を追加する(観点a・11・12)**
- 月の台帳のF06は、1文の中に「約45 m」「約4億年前」「約11 cm/100万年」が並んでいる(`er019_output/moon_shrinking/run_ms_02/research_ledger/verified_fact_ledger.txt:35`)。B3が「約4億年で約45m縮んだ」と書く可能性は十分ある。
- その場合の流れ:
  - 45mはF06のnumeric_value欄にないので、eligible=Falseで周辺数値のままになる。
  - 結果、「テーマ：」行に周辺数値が載る。これは規則5「周辺数値は書かない」と直接矛盾する。
  - Eから42〜46mが抜けることもありうる。
- 表記揺れも問題になる。B3が「42〜46メートル」と書くと、derive_ranks:494-503のstory_only経路で別の概念ができる可能性がある。その表記はニュース欄にないため、Eの照合対象とWriterが見る印付きの表記がずれる。
- 修正: B3出力の直後に決定論検査を置く。Storylineの数値はすべて「ニュース欄に【中核数値】として印が付いた同じ概念の表記」に対応し、合計は2個以下でなければならない。違反したらB3を1回だけ再実行(既存のRETRY_APPEND_NOTEと同型)する。それでも違反ならE=∅として記録・WARNし、Fableへ報告する。
- Eの照合に使う表記は、Storylineの表記ではなく、ニュース欄にある中核数値の表記にする。

**M2 時間・前提の数値はGateの必須対象から外し、§5の「E2を必須にするか」を事前に固定する(観点c)**
- 台帳上、「約4億年」はF06の「一定速度を仮定した計算」の前提値であり、開始時期の本来の出典はF05(AMBIGUOUS、「約3〜4億年前」、8億年前説もある)。
- 4億年をGateで強制すると、WriterはF06を引用して書く方向へ押される。これはユーザーが警告した「今も同じ速度で縮んでいると誤解させる」リスクを強める。
- 推奨: Gateで必須にするのは「答えの数値」だけにする。時間単位の数値(年前・万年・億年)は前提として扱い、有無と表現は観察のみとし、人手で評価する。
- 予定のソフトWARN(同じ段落に「推定・仮定」があるか)は効かない。42〜46mの文自体に「推定」が入るのでほぼ常に通過し、見逃しになる。代わりに、時間数値の近くにある誤解表現(「今も」「毎年」「一定の速さ」「ずっと」)を検出するWARNにする。これは観察のみでブロックしない。実質的なGateにはならないので、品質基準の無断追加にも当たらない。
- 月の評価基準(事前登録)に加えるべき点: 期間は「後期の縮み。開始時期は研究上の推定で確定していない」という扱いであること。「月の誕生以来」と書かないこと(F05とF07のnotes)。

**M3 再実行枠と判定表を明文化する(観点d・10)**
- R0は「記号QAだけ不合格/保持だけ不合格/両方不合格」と「再生成後にどちらかが不合格」の組合せ表を作る。初回R0は記号だけで不合格・Eはあり、という場合に、再生成でEが消えるとSTOPが増える点も明記する。
- R2は記号QAの再実行と保持の再実行で枠を共有し、1回だけにする(最大2回の再実行にしない)。
- R1の再実行は今のProductionにはない新しい仕組みなので、新規として明記する。記事ごとの上限はR0・R1・R2とも各2呼び出し。
- 最悪ケースの費用にはM1のB3再実行分(約12円)を加えて約28円に更新し、期待増分の式にもP(B3再実行)×12円を足す。

**M4 Gateの照合を較正する(観点d)**
- `er114.ja_present`(:66-80)は計測器と同じ関数なので、それで誤判定率を測っても自分で自分を検証することになる。
- 照合の弱点:
  - 「m/メートル」「km/キロメートル」「%/パーセント」などの単位の言い換えがないため、本来ある数値を「ない」と判定しうる。
  - 単位のない数字同士も一致扱いになる(`not unit or not tunit`)ため、ないものを「ある」と判定しうる。
- Phase 1の前に次をやる:
  - 既存15runのR0とR2について、Fableが人手でラベルを付けて照合結果と突き合わせる(0円)。
  - 単位の言い換え表を追加する。
  - 英語側の照合で、`_UNIT_HINT`に「m/meters」がないことも直す。

**M5 B3の標本を増やす(観点6)**
- 方式全体の土台は「B3が正しい数値を安定してStorylineに入れるか」。B3が1回だけでは、45mや11cmの混入率が分からない。
- 月はB3だけを3回実行する(+約24円)。R0の追加標本よりこちらの方が情報価値が高い。

## 推奨(任意)
- R1 B3への追記ブロックは「Storylineを決めた後」の手順として置き、「Storylineの選び方とFactの採否は、数値の有無で変えない」と明記する(既存のTest4「数字がある、だけの理由では残さない」との整合、数値偏重の防止)。
- R2 中心的な問いが数値でない記事(例: uk_train_speaker_playback、manga_ai_chat)を1本、B3だけで対照に加える(約12円)。指示によって数値が無理に入らないこと(E=∅)を確認するため。
- R3 過剰掲載の判定は、R2の数値表記のユニーク数を基準run比+1以内と見る方式だと、基準runが1本のためばらつきに埋もれる。「E以外の中核数値の掲載数」と「周辺数値の混入数」を主指標にし、coffeeなど複数runがある記事は基準を複数にする。
- R4 範囲値の正規化は「数字〜数字」の形だけに限定する。対象はニュース欄と「テーマ：」行だけで、R0_PROMPT本体の「800～1000字」には触れない(sha不変)。丸め注記(【概数表記】)の挿入後に適用する。照合は「〜」と「から」の両方を許容する。
- R5 Storyline方式が成立しない場合の代替は、撤退ではなく、B3の同じ呼び出しのJSONに「答えの数値(中核数値の表記から2個以下)」の欄を足す案。B3自身の判断なので重複システムには当たらず、文章からの抽出より検証しやすい(schema変更が入る)。DESIGN_01 §6.4の撤退条件の前に、この案を検討する。

## Phase 1のアーム構成と費用
- アームA/Bの構成は妥当(Aで足りればBは使わない)。AとBの並列実行も可。ただしn=3同士ではAとBの差は判別できないため、Bは「Aが不合格のときの予備」と位置づける。
- 範囲値の正規化だけのアームは不要。J2はn=4の相関ではなく、「承認済み規則同士の矛盾」と「Normalizerが範囲を『42なになに46』と読む欠陥」という論理だけで成立するため。
- 費用見込み: Phase 1 元見積 約79円 / M5 B3追加2回 +24円 / R2 対照記事 +12円 / Phase 1 合計 約115円 / Phase 2 113円 / 総額 約228円
- 総額は案件300円の自律枠内だが、Fableが設定した上限200円を超える。上限を見直すか、Phase 2のR0追加標本(22.8円)を削るか、Fableが判断してください。
- 量産単価の継続増分(期待0〜2円程度、M1分を加えても小さい)の見積根拠は妥当。Phase 1の実測で確定させる。

## 観点別(問題がある観点のみ)
- 観点6(非決定性): B3のStorylineが新たなばらつきの源になる → M1、M5
- 観点10(retry): 再実行枠が重なる → M3
- 観点11(安全側): J3参照
- (a)について: E=中核∩Storylineは既存機構の再利用と言える。上限はcap_of≥3なので、Eが2個以下であれば常に中核に入る。
- (h)について: B3のPromptファイルはFamily Xの名前だが、Family YのTrial(`er036_family_y_voice_structure_trial_01.py:33`)など多数のTrialからimportされている。Production採用時は、Y/ZのProduction経路が`USER_PROMPT_TEMPLATE`と`selected_storyline`を使っていないことのGrep確認をIsolation testに含める。撤退は容易(追記型の変更で、OFF時はバイト一致)。

## J1〜J3への技術的所見(採用判断はユーザー)
- **J1(B3 Promptの変更)**: 意味的な変更で、分類Cとする判断は妥当。M1の検証とセットでなければ、周辺数値がテーマ行に漏れる経路が残る。
- **J2(範囲値の正規化)**: 承認済み規則同士の矛盾の是正として技術的に妥当。Writer入力側だけに限定するのが最小で安全。TTS Normalizerの一律変換には手を付けず、Writer入力側で予防する方が影響範囲が小さい。
- **J3(保持Gate不足時の動作)**: 本文を自動で書き換えないのは正しい。再生成1回の後も不足する場合、必須数値が欠けた記事を出荷するより、既存のHuman Review/STOP枠へ両方の初稿を付けて回す方が、U4(c)の安全側(最終成果物が目的要件を満たす側)に合う。Production既定は「STOP→HR」が技術的に妥当。そのうえでPhase 1/2でSTOP率(P_R0)を測り、HR増加量を報告する。
```

## 2. Fable判断(反映指示)
- M1〜M5: 全て反映。M4の「人手ラベル」は、Sonnetが照合関数を使わずに本文を読んでラベル付け(盲検: 関数結果を見る前にラベルを確定しファイル保存)→関数結果と突き合わせ、不一致を分析・単位言い換え表等を較正。較正結果 `CALIBRATION_01.md`(FP/FN件数、修正前後)。Fableは報告後に抜き取り確認する。
- M2: Gate必須=「答えの数値」(月は42〜46m)のみ。「約4億年前からの推定」はユーザー原文§3で「必要」だが、Gate強制はせず、Phase 1の事前登録評価基準で「本文に期間情報があり、推定条件(後期の縮み・開始時期は研究上の推定で未確定)を正確に扱い、『今も同じ速さで』『月の誕生以来』等の誤解表現がない」を人手評価項目として必ず判定する。誤解表現WARNは観察のみ。Phase 1で4億年の脱落が頻発すればE2必須化を再検討してFableへ報告(自己判断で必須化しない)。
- M3: 判定表・再実行枠(R0/R1/R2各最大2呼出、R2は記号QAと枠共有)をDESIGN_02.mdに明文化。Trial中の不足時動作=STOP(記録)。Production既定(STOP→HR)はJ3としてユーザー判断事項に記録。
- M5・R2: 採用(月B3×3回、対照記事1本B3のみ。対照はuk_train_speaker_playbackかmanga_ai_chatのうち既存ledgerが完全に残っている方)。
- R1/R3/R4: 採用。R5: 実装はしないが、Storyline方式がM1検査で成立しない(3回中2回以上E=∅またはM1違反)場合の代替として設計書に残し、その場合はPhase 1を中断してFableへ報告(自己判断でR5実装へ進まない)。
- 予算: 案件上限230円、Phase 1≤120円、Phase 2≤115円。費用台帳 `BUDGET_LOG_01.md`(出典=cost.json/raw_usage_log)。有料run起動は最小回数、同一run起動間隔150秒以上、再起動回数記録。
- モデル: Production同一(B3/R0/R1/R2)。評価LLMは使わない(決定論計測+人手評価)。

## 3. 実装(DEV/Trial専用、Production file編集禁止)
- 新規DEV module(例 `er115_fx_numeric_retention_trial_01.py` + test)。B3 Prompt追記ブロック・M1検査・範囲値正規化(R4、数字〜数字のみ、ニュース欄と「テーマ：」行のみ、R0_PROMPT sha不変)・保持Gate(M4較正済み照合、本文書換えなし)・R0/R1/R2段限定再実行・計測(選定数/必要数/掲載数/不要掲載数、周辺数値混入数、誤解表現WARN)を、既存Production関数をimportしてDEV側で合成する。Production到達経路への新機能0をIsolation testで固定(`grep er115_` がProduction fileで0件)。
- 既存ledger・B3入力は再利用、Web検索・Research再実行禁止。出力は `er115_output/fx_numeric_retention_trial_01/<article>/<arm>/` に限定し、Production出力dir・公開ページ・store・telemetryへ書き込まない(委任_02 FX-PARAGRAPH同様、attempt_history/HR queue等のsinkがProduction関数内にあれば DEV dirへ付替え、実行前後のsha比較)。
- 事前登録: Phase 1開始前に `PREREGISTERED_CRITERIA_01.md` に月の合否基準(E保持、不要数値混入0、期間情報の正確性[M2]、文章の不自然さ、事実・単位・推定条件、丸め整合)と過去記事の必要数判定N1〜N3・過剰掲載指標(R3)をcommitしてから生成する。

## 4. Phase 1(月の記事、≤120円)
- B3 DEV ×3(M5)→M1検査→E確定。対照記事B3×1(R2)。
- アームA(Storyline指示+範囲正規化+Gate)でフルチェーン R0→R1→R2→英訳Std/Adv(既存の忠実英訳段をDEVから呼ぶ)を2本。R0追加標本は、Opus指摘どおりB3標本を優先し、残予算内で可能なら実施。アームBはAが事前登録基準を満たさない場合のみ。
- 結果 `PHASE1_RESULT_01.md`: 各標本の段別保持表、E/不要数値/周辺数値、期間表現の人手評価、文章品質所見(Std/Adv)、Gate発火・再実行回数・STOP、費用・時間、Normalizerで「42〜46」がどう読まれるかの確認(TTSは呼ばず正規化関数のみ)。
- **月のProduction再実行・公開ページ差替えは禁止**(採用判断後)。

## 5. Phase 2(過去記事、≤115円)— Phase 1アームAが事前登録基準を全て満たし、STOP/R5条件に該当しない場合のみ同一委任内で継続
- 対象: ig_nobel_2026、coffee_prices、semiconductor_earnings(設計どおり、既存ledger再利用)。各1本フルチェーン(R0追加標本は残予算内で任意)。公開版は変更しない。
- 結果 `PHASE2_RESULT_01.md`: 記事別の中核数値数・必要数・掲載数・不要掲載数・周辺数値混入数、文章品質所見、過剰掲載の有無、Gate発火率・STOP率、費用。
- Phase 1が基準未達・STOP・R5条件の場合はPhase 2に進まず報告。

## 6. 文書・SSOT・Git・報告
- `TRIAL_RESULT_01.md`(ユーザー原文§8の1〜5に対応する事実。Status候補はSonnet所見、最終はFable評価)、`DESIGN_02.md`(M1〜M5/R1〜R5反映後の設計)、`CALIBRATION_01.md`、`PREREGISTERED_CRITERIA_01.md`、`BUDGET_LOG_01.md`。Production採用時の必要作業・影響範囲(X専用の確認、B3 PromptのY/Z Trial import状況、Isolation test、撤退=revert)を`ADOPTION_NOTE_01.md`に。
- SSOT: OPEN-507 Status更新、`DECISION_LOG.md` 1件、`docs/pm/ACTIVE_TASK.md` 自行のみ(並行agent FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 委任_02が同時編集中。編集直前に再Read・最小Edit・衝突時再試行)。SSOT編集前にscratchpadへバックアップ、編集後 `git diff --stat -- <file>` 確認。
- Git: `git status` → 対象pathのみ `git add`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status`(意図外D/Aなし・secret 0件・Production file差分0・telemetry/ledger/raw_usage_log不混入) → `git commit --only -- <path…>` → `git push origin HEAD:main`。他agent差分混在時は一時index方式。事前登録はPhase 1生成前に別commit。
- 報告 `docs/pm/RESULT_PACKET_FXNR2.md`: ①M1〜M5/R1〜R5反映、②較正結果、③Phase 1結果(E保持率、4億年の扱い、不要数値、品質所見、STOP/再実行)、④Phase 2結果(実施した場合)、⑤費用(Phase別実費/上限)・有料run記録(起動回数・JST・再起動)、⑥量産単価増分の実測ベース見積、⑦Status候補と根拠、⑧J1〜J3ほかユーザー判断候補、⑨変更ファイル・commit、⑩`check_delegation_prompt.py`結果、⑪問題点。

## 7. 禁止
Production code/Prompt/flag/閾値の変更(B3 Prompt本体含む。追記はDEV側の合成のみ)、月・過去記事の公開版/Production出力の変更、「全部必須」化、不要数値の追加、Gateによる本文自動書換え、Web検索/Research再実行、Cap超過、`.venv\Scripts\python.exe`以外の使用、自PID以外のprocess終了。Trial成功でもProduction採用・配線・月のProduction再実行へ進まない。