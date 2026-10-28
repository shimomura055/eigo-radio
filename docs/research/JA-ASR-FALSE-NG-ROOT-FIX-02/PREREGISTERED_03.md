# PREREGISTERED_03(JA-ASR-FALSE-NG-ROOT-FIX-02 委任_03、2026-10-28。有料draw取得・eval_unified_03.py実行の**前**に凍結)
前提: PREREGISTERED_01/02 の定義(PASS/PASS_W/NG、増分誤PASS=L0がNGで当該構成が誤PASS、シナリオ P_only/PS_same/S_canon/explicit/real)を継承。Opus条件Aレビュー(OPUS_REVIEW_01.md)のM-1〜M-7/R-1〜R-7は全採用(Fable判断)。Production code・CURRENT_SPEC変更なし。有料はOpenAI gpt-4o-mini-transcribeのみ(Azure/TTS 0)。この文書の規則を、取得したdrawの結果を見て調整することは禁止(調整が必要なら新しい事前登録版PREREGISTERED_03Bとして、調整前後の数字を併記)。

## 1. 集約規則(主=M-3「矛盾なし合意」、参考=best-of-N[Phase 2既出])
主規則 CONSENSUS(分担: 判定対象はdraw集合D、|D|=N∈{1,2,3}、Azureは保存転写のみ[再試行しない、M-3(f)]):
1. d1(最初のdraw)を最終層構成(L1+L2+L3、後述)で単独判定。非NGならそのまま採用(再試行なし)。
2. d1がNGで、理由が**発火ホワイトリスト**(`p1_value_diff` / `secondary_not_accepted`)に該当し、かつ除外条件(否定差[negation_diff/否定マーカー差]・A7登録読み・C2[理由コードp2_exclusion*は元々非該当]・length[原稿正規化文字数比が0.8未満または1.25超])に当たらず、かつ**保存Secondary転写が存在する**(force_secondary必須。無ければ再試行不可=NG)ときだけ、追加draw(最大2本、N≤3)を使う。
3. D全体を判定する: 各drawを単独判定(再試行セグメントでは β の `secondary_reading_conflict="veto"`=M-4)し、drawごとに**矛盾判定** `contradicts(draw)`を行う。矛盾=(a)否定差 (b)値atomを除いた残り(原稿のnum/frac atom位置をdraw内の同位置の数字run+助数詞でmask)の発音(v2 `pron_hira`、助詞は→わ/へ→え)が原稿と不一致(=値以外の内容span食い違い) (c)原稿のnum atomに対応する数字runがdraw内に無い(欠落) (d)対応runが整数として解釈でき、原稿値と異なり、かつβの`explain_garble`で説明できない(=別の値)。例外(矛盾としない)=`explain_garble`で説明できる数値garble、および M-1/C2/R-1を通過した発音同一(PRON同音)。
4. 結果: 非NGのdrawが1本以上あり矛盾drawが0本 → **PASS_W_NEW**(警告 `JA_NEWLAYER_ASR_CONSENSUS_RETRY`、常に非ブロッキング事後試聴でなく**試聴リスト別枠**)。非NGdrawが1本以上あるが矛盾drawもある(釣り型) → **HR**(早期HR、エンジン間の内容矛盾のみを根拠。機械PASSにしない)。非NGdrawが0本 → **NG**(通常のregenerate/HR Lock経路)。
5. 評価の順序独立性: N=2,3 の効果は、draw集合の全(d1, 追加draw部分集合)の組合せ(各組合せ等重み)で平均する。保存順は参考列として別掲。
参考 BEST_OF_N(Phase 2の規則): D内に非NGが1本でもあれば合格(矛盾無視)。CONSENSUSとの差を併記する。
M-2: 新層で救済したPASSは必ず専用warning codeを`warning_labels`へ載せ、`APPROVED_EQUIVALENCE_BASES`に登録しない。最終判定は PASS / PASS_W_PROD(既存Production警告付き) / PASS_W_NEW(新方式) の3区分+HR+NG。

## 2. 層構成(Flagsで切替。既定は全OFF=L0同一=Production adapter呼出のみ)
- L0: 現行Production HEAD(基準)。
- L1: v2読み規則(Primary/Secondary値等価層差替、Production層へのフォールバックでL1⊇L0)+ M-1(原稿に不規則読み数詞があれば両側・PRON/VALUE_ONLY両経路でv2不適用=Production判定を返す)+ M-2(Productionの `_numeric_value_equivalence` が受理しない VALUE_ONLY 救済にも警告)+ **R-1(差分span内の漢字1文字ごとにC2逆方向検査:ASR側の差分span内の漢字1字でも読み候補が2つ以上あれば発音救済しない)**+ **R-2(v2の `ENGINE_reading_difference` 経路を除外)**。
- L2: β composite(`b_light_proto_02.composite_judge`)。M-7(secondary_meta の `phrase_list_hash` が空でなければ/鍵が無ければfail-closed)、M-4(再試行セグメントでは読み食い違い=veto)。
- L3: **「送り仮名省略形の訓読み」別表**(新層内のみ参照、汎用辞書 `er008_*_ja_kanji_readings.py` 不変)。原稿でnum atom直後が『超』のとき、Primary/Secondary**それぞれ**の同位置の `超え/越え/こえ`(直後が る/た/て/な/ば/ず/よ 以外)を『超』へ置換し、置換後の文が原稿と**残差0文字**(値形式+normalize_ja一致)であること、両engineの転写が揃っていること、C2候補span(`_scg_heterophone_candidate`)に当たらないことを要求。常にPASS_W_NEW(警告 `JA_NEWLAYER_KUNYOMI_OKURIGANA`)。v1経由の発音同一との併用(『月野詩は…超え』型)は**不可**(旧L3から意図的に狭める)。
- M-6: Primary分類の `candidate_e_rejections`(E3)が非空なら全新層(L1/L2/L3/再試行)を不適用(L0結果を返す)。`candidate_e_cascade_diffs`(E4)が非空なら全新層不適用(より保守側)とし、発火件数をauditへ記録。
- 評価構成: L0 / L1 / L1+L2 / L1+L2+L3(=最終層構成) / 最終層構成+CONSENSUS N=1,2,3(+参考BEST_OF_N)。ablation: R-1 OFF、M-4(veto→warn)の差も1列。

## 3. 母集団
- 正例(6音声): run_ms_03 a1-a3 / run_reselect_01 a1-a3(wav sha256照合、Phase 1/2と同一loader)。draw集合=記録済み全draw(ms_03:4本、reselect:5本)、Azure=保存転写。
- 正例拡張(新規有料draw、各4本): 人間承認(`human_approved_segments.json`の承認segment)で最終採用された**日本語a2のattemptのうちwav shaがattemptと一致し、Family A/B/C以外**のもの。列挙(下記は本文書凍結時点の実在確認): (1) `er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_mey_02` comment_2 attempt3(Azure保存転写あり) (2) `er026_output/family_z_production_e2e_01/melos/run_e2e_02` a2 comment_1 attempt3 (3) `er121_output/family_y_production_01/redelivery_fee/run_01` preview attempt5(= run_hrguard_ev_02_mock / run_voice_puck_ev_01 / stdchunk run_ev_01 の採用wavと同sha) (4) `redelivery_fee/run_style_fix_01` preview attempt1(= run_gpg5_y_01 / run_gpg5_y_01_s23f と同sha)。計4wav(sha重複は1本に畳む)。記録済みstored転写(attempt jsonの`asr_text`)+新規4 drawで5 draws。Azure転写が無いwav(Z comment_1・Y preview 2本)は P_only 判定(Secondary未保存=再試行不可・β/L3不可)とし、Azure追加呼出は**しない**。
- 負例(真値NEG=TTS入力が意図的に誤りの既知誤読音声): N3 30 wav(`n3_clips_01.json`)。draw集合=既出の新4 draw(`n3_redraw_02.json`、2026-10-28T20:33頃)+記録済みstored(Phase 3)=5 draws、Azure=保存転写。**これ以外に『人間がNG判定した実誤読wav』の台帳は存在しない**(探索範囲: `human_review_queue.jsonl`2本[er007/er006、日本語17行、判定記録なし・多くは誤NG側]、`human_approved_segments.json`[承認=PASS側のみ]、`ng_pool_cases_01.json`[TCM判定、真値ラベルなし]、docs/research配下のwav[英語OOV clips等]。HR queueの日本語entryのうち pool_pilot/family_c/e_family は系列がA/B/C・不明のため除外)。よって負例追加draw費用は0円。母集団を広げる案(既知誤値TTS入力の追加生成)はTTS呼出を伴うため本委任の範囲外=判断候補として報告のみ。
- 負例(テキスト、API 0): Phase 2と同一コーパス(NEG 1439行 sha d55f24e2…+L3_NEG+N3_redraw)。回帰基準=1706行(Phase 1と同一)+L3_NEG/N3追加分。

## 4. 指標と合否
- (P-1) 6音声: 最終判定を PASS / PASS_W_PROD / PASS_W_NEW / HR / NG の5区分で、N=1(d1=記録済み)・N=2・N=3(全組合せ平均)、およびCONSENSUS対BEST_OF_Nで別掲(R-6: 『4/6+HR』型の表記)。
- (P-2) 負例増分(L0がNG→誤PASS)を型別: T1同音異表記便乗(音素列同一=区別不能) / T2 β値garble(Secondary=原稿の最悪露出) / T3 不規則読み / OTHER。**OTHER>0の層は不合格**。R-3: 事前登録(Phase 1/2)どおりの数字(M4増分11相当)と、by-design再分類後の数字を併記し、再分類は事後であることを明記。
- (P-3) 回帰(L0 PASS系→NG)=0。M0基準線PASS_W(『三人で一日に会った』型)が不変。
- (P-4) CONSENSUS の誤PASS: 負例N3(各clip・全組合せ)で、N=1ではNG/HRだがN=2,3でPASS_W_NEWになる**再試行起因の誤PASS**を数える。目標0。0でない場合は当該規則を不合格とし、件数・clip・drawを全列挙。Clopper-Pearson 95%上限も提示(分母=再試行発火組合せ数)。
- (P-5) draw独立性: wav別のdistinct転写数・同一転写比率。時刻依存: 記録済みstored(旧)と新draw(2026-10-28)の分布差の有無。
- (P-6) Y/Preview型(思いどおり↔思い通り): L1(R-1入り)で救済されるか(期待=されない、修正は別ID)。
- (P-7) run単位の実益(参考): run_ms_03(a1→a2)・run_reselect_01(a1)が何attemptで完走するか。
- (P-8) 決定性: eval_unified_03.py を2回実行しJSON sha256一致。
- Statusは付けず「候補」のみ(最終はFable)。

## 5. 費用
見積: 正例拡張4wav(合計約62秒)×4draw=約249秒×¥0.0075/秒≈¥1.9(N3実績の分課金単価¥0.0075/秒)。上限¥15(個別Cap)、案件見積≪¥300、日次1,000円内。実行は1起動(`redraw_03.py`)、自動再試行・ラッパなし、エラー時は即停止してFableへ報告。cost_log=`redraw_03.cost_log.jsonl`。

## 6. 禁止
Production code(er0XX_*.py)編集、TTS/Azure呼出、再転写の再実行、socket guard迂回、Family A/B/C wav使用。

## 7. 補遺(実装確定事項。eval_unified_03.py の結果を見る前に追記。規則の意味は§1〜§6から変えない)
1. R-1(差分span内の漢字1字ごとのC2逆方向検査)は L1 のv2発音救済に加え、**βの発音同一経路にも適用**(βは凍結ファイル `b_light_proto_02.py` のため、β成立後に `JA_PRON_EQUIVALENT` を含む場合は同関数で事後検査しブロック)。R-1 ON/OFF は全表で併記する(主=R-1 ON[事前登録どおり]、比較=R-1 OFF[Opusの『4/6』想定に対応])。
2. E4(`candidate_e_cascade_diffs`)非空も全新層不適用(§2のとおり保守側)。件数をauditに残す。
3. 矛盾判定 `contradicts()` の実装: 否定差→矛盾。値atom位置をmaskした残りの正規化文が原稿と一致→矛盾なし。不一致で発音(v2 pron_hira)も不一致→矛盾(content_span)。発音一致でも C2/R-1/不規則読み原稿でブロックされるなら矛盾。値run: 欠落→矛盾、整数として解釈でき原稿値と異なり `explain_garble` で説明不能→矛盾。単独判定で非NGのdrawは矛盾判定の対象外(定義により矛盾なし)。
4. 再試行発火の長さ除外は正規化文字数比 0.8〜1.25 の外。ホワイトリストは理由コードの前方一致。
5. 『HR』区分=再試行発火後に「非NGdrawが1本以上かつ矛盾drawが1本以上」の早期HR(PASSにしない)。再試行後に非NGdrawが0本、または再試行不可(理由外・Secondary無し・N=1)は『NG』(既存のregenerate/HR Lock経路)。NGのうち U2.hr_candidate(Phase 2の機械条件)に該当するものは『HR候補』として別掲する(PASS/NGを変えない)。
6. 組合せ平均: draw集合 k 本(6音声は4〜5本、拡張wav・N3は5本)から、N=1は first のみ k通り、N=2は first×追加1本(k(k-1)通り)、N=3は first×追加2本(k·C(k-1,2)通り)を等重みで数える。保存順(first=記録済み、追加=記録順)は参考列。
7. run単位(参考): 同一runのattempt1,2,3を順に、記録順consensusで判定し最初にPASS系になったattemptで完走、HR区分でその時点でHR、全NGなら未完走とする。
8. 負例側の誤PASS: 真値NEGのN3 clipは scenario real(Secondary=保存Azure転写)と S_canon(Secondary=原稿=最悪露出)の両方を報告。再試行起因誤PASS=同一first drawでN=1がNG、N=2/3のconsensusがPASS系になった組合せ。
