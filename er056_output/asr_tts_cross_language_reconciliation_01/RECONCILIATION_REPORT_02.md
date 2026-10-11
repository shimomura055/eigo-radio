# RECONCILIATION_REPORT_02 日英統合報告書 v02(ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_03、2026-10-11)

Status: **USER_DECISION_REQUIRED**(提案のみ。Opus独立レビュー[条件A]の必須指摘M1〜M7を反映済み。Production・CURRENT_SPEC無変更、有料API 0円)。
v01(`RECONCILIATION_REPORT_01.md`、委任_02、commit f556e4c3)は残してある。本書v02は**v01の章構成を維持**し、(a)Opus必須指摘M1〜M7の反映、(b)事実照合4件の結果、(c)統一ルール案の照合(5-3)、(d)Trial計画の再編(8-3)、(e)ユーザー判断の最終版(9章)、(f)Dangling追加(11-2)、(g)新章14(承認済み仕様違反・費用計上欠陥)を加えたもの。v01から変えた箇所には「**Opusレビュー反映**」「**委任_03で訂正/追加**」と明記してある。

「目標共通フロー」(初回 -> Primary NG -> Secondary -> 両NG -> 同一Promptで再生成(最大2回、TTS総3回) -> Human Review)は**ユーザー要件に基づく目標案であり未採用**。本書の「統一推奨」「維持すべき例外」「統一ルール案」はすべて**提案・候補**で、新しい例外仕様・閾値は何も採用していない。**目標フローはTrial級の設計案で`APPROVED_FOR_PRODUCTION`ではない**。Production採用は人間ユーザーだけが承認できる。

用語メモ(エンジニアでない方向け):
- **Primary ASR** = 最初の音声認識(OpenAI gpt-4o-mini-transcribe)。**Secondary ASR** = 別会社の2つ目の音声認識(Azure Speech)。「ASR」は音声を文字にする機械。
- **TTS** = 文字を音声にする機械(Gemini TTS)。**再生成** = TTSをやり直して音声を作り直すこと。
- **Validator** = 音声認識の文字と原稿を比べて合否を決める判定器。**TCM**(TRUE_CONTENT_MISMATCH)=「内容が違う」判定。**UNCERTAIN**=「固有名詞等でASRの誤認識か判別できない」判定。
- **SCG** = 日本語のSecondary Confirm Gate(Primary NGの時に再生成の前にAzureで1回確認する仕組み、2026-10-11採用)。**旧Cascade** = Primary#2 -> Azure#1 -> Azure#2 の4段確認(UNCERTAIN時のみ)。
- **Human Review(HR)** = 人間が聞いて判断する待ち行列。**Local Rewrite(LR)** = 3回失敗後に問題箇所だけ文章を書き換えて再TTSする英語専用の救済。
- **Phrase List** = ASRへ「この語が出るはず」とヒントを与える機能。ヒントを与えると原稿寄りに転写されやすく、確認の独立性が下がる。**最小対(minimal pair)** = 1音/1語だけ違う対(ガス/カス、show/showed等)。**fingerprint** = TTSへ渡した条件(model・voice・style・減速比等)の組を識別する指紋。
- 根拠の略記: CS=`CURRENT_SPEC.md`の行、DL=`DECISION_LOG.md`の行、OI=`OPEN_ITEMS.md`の行。「確定」=コード・ログ・SSOT行で確認、「推測」=確認できていない解釈。
- 入力: 英語側 `er056_output/en_asr_confirm_retry_redesign_01/*`(commit 7ef4eed2)、日本語側/統合 `er056_output/asr_tts_cross_language_reconciliation_01/*`(commit 6468a21e、f556e4c3)、Opus独立レビュー結果(2026-10-11、原文はFable保持)。今回(委任_03)も新しい有料実測なし(read-only照合のみ)。

## 要点(先に・PM向け)
1. **日英の差の大半は「必要な違い」ではなく、導入時期の違いによる継ぎ足し**(2章)。言語そのものが要求する違いは、判定器の中身(日本語=読み/漢字、英語=発音辞書/表記ゆれ)と、英語A2の6%減速だけ。
2. **Coffee Standard `full_story_part2` のNGは、「音声が壊れていた」と確認できたものは0件**。主因は(a)合格済み音声を減速後の簡易チェックで捨てる設計、(b)`US`と`U.S.`等の表記差の偽NG、(c)Azureの聞き間違い、(d)Local Rewriteが無関係な箇所を書き換えた、の組み合わせ(4章)。標準1回目とLR後の音声だけは**人間が聞くまで未確定**。
3. **g8「ガス->カス」は誤PASS防止の実績ではなく、救済機会を失った副作用**。Primary NGの直接原因は別の語「熟->じく」、SCG除外はカタカナ率の粗いヒューリスティックが原因(3章。**v02で訂正: 旧承認との「向きが逆」は言い過ぎ、要点8・0-2(iv)**)。
4. **Coffeeの費用は少なくとも約10.3円過少報告**。Azure STT 8回(231.8秒)が累計20.73円に入っていない。補正後は約31.03円/50円(別紙 `COFFEE_AZURE_COST_ADDENDUM_01.md`)。
5. **「英語側がwavを16MB commitした」という前提は事実と異なる**(wavは`.gitignore`の`*.wav`で除外済み。commitされたのは約1.5MBのテキスト/JSONのみ。13章の付録参照)。
6. 目標フローはおおむね実現可能だが、**日本語の「UNCERTAIN -> HR直行」と英語のcascade 4段を目標型へ寄せる部分、minimal fallback廃止、6%減速、Local Rewrite、cool-downは承認済み仕様の変更**であり、ユーザー判断(9章)とOpus独立レビュー(新構造のため必須)が前提。
7. 参照整合の発見(11章): 目標フローでminimal fallbackを廃止すると、**Local Rewriteの再TTSがfallback関数を内部で再利用している**ため(`er003_v1_crosslevel_audio_02_common.py` L383)連動して壊れる。また`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`は`welcome`共有殻の通常styleとしても使われており(`er006_audio_cost_pilot_02_shared_narration.py` L166)、「到達不能にする」だけでは済まない。

---

## 要点への追加・訂正(v02、委任_03)
8. **訂正(g8、要点3)**: v01は「C1は旧承認(CS:1998)と向きが逆」と書いたが**言い過ぎ**。CS:1998は「entity-like**のみ**の不一致(UNCERTAIN)でCascade」であり、g8(「熟->じく」を含むTCM)は旧方針でも再生成対象。真の内部矛盾は「同じ濁点差が、UNCERTAIN経路では`phonetic_uncertain`(救済)、SCGでは`entity_like`(除外)と扱われる点」(0-2、3-補)。
9. **新規(最重要)**: 英語の6%減速外側ループは、承認済みCS:1692「4回目以降は絶対にTTS生成しない」に**違反している**(Coffee part2でTTS 5回、attempt_historyで確認)。単独OPEN(OPEN-270)として起票(14章)。
10. **M1**: 目標フローは**日本語にも適用すべき**。日本語にもminimal fallbackでJ3(Role Style)が失われる経路(N3 L532)、UNCERTAIN 4ステップ後HR、fingerprint無しがある。v01の「日本語は既に目標型に近い」を訂正(0-1、7-1)。
11. 英語のSecondaryはPhrase List付き(`er006:704-705/774-775`)で独立性が構造的に低く、entity差でもSecondary一致だけでPASSする(`er006:783-788`)。日本語(Phrase Listなし・C1で固有名詞除外)の方が厳しく非対称(0-2)。

---

## 0. Opusレビュー反映表(M1〜M7)と事実照合(委任_03)

### 0-1. Opus必須指摘M1〜M7の反映先
Opus独立レビュー(条件A、2026-10-11)結論: **構造(初回+同一Promptで再生成最大2回、Primary NGならSecondary、両NGならHR)は進めてよいが、M1〜M7を反映または選択肢として明記すること**。以下がv02での反映先(いずれも提案で、採用ではない)。

| # | Opus必須指摘 | v02での反映 | 反映先 |
|---|---|---|---|
| M1 | 日本語も新モード対象に(TARGET §3-9「日本語: 対象外(既に目標型)」は事実誤り) | 日本語の「J3喪失(minimal fallback)」「UNCERTAIN 4ステップ後HR」「fingerprint無し」を根拠付きで記載し、適用範囲を日英両方に訂正 | 0-2(i)、7-1、9章U-0/U-11 |
| M2 | 固有名詞の統一ルール、PASS判定用SecondaryはPhrase Listなし・原稿を与えない | 日英非対称(英語=Phrase List付き+entityでもSecondary一致でPASS、日本語=C1除外)を確認。統一案(辞書・Ledger判定、推定廃止、Phrase Listなし)を5-3に | 0-2(iii)、5-3、U-8、U-17 |
| M3 | 6%減速は案B'(生成->stretch->最終音声のみPrimary->Secondary 1系統)を追加。L1692違反を別OPEN起票 | U-7に案B'を追加(推奨)。L1692違反はOPEN-270として起票 | 5-3、U-7、14-1 |
| M4 | 一時的技術失敗(5xx/429/timeout)はattempt外・上限付き。無音・異常長はattempt消費 | U-10を改訂。OPEN-273として起票 | 5-3、U-10、OPEN-273 |
| M5 | UNCERTAIN->HR(再生成しない)は新モードでは廃止、例外案C(両ASRが同じ誤りで一致なら即HR)。承認済み仕様変更として明記。stop_retryingの扱い | U-2を「承認済み仕様(2026-08-25 U)の変更」と明記し、選択肢に例外案Cを残す | 5-3、U-2 |
| M6 | 最小対・形態素型の差分(-ed脱落、-s、冠詞、濁点、長音/促音等)は`PASS_WITH_WARNING`として最終試聴リストへ自動連動 | 新ルール案8とU-18。Secondaryが原稿寄りに丸めるリスクの本体(ASRのLM prior)を5-3に | 5-3、U-18、8-3 |
| M7 | F-5複合偽NG(US<->U.S.+cost<->costs同時)をスコープに | 5-3ルール6・14-1・Trial対象ペアに含める。同型の根はC1と同じ「固有名詞ヒューリスティックの粗さ」(OPEN-272) | 5-3、8-3、OPEN-272 |

Opus推奨(必須ではない)の扱い: F-7 Azure費用計上修正 -> 14-2/OPEN-271/OPEN-275。Primary単独PASSのlocal medium無料サンプル監査 -> 8-3の0円項目(標本設計は未着手、提案)。

### 0-2. 事実照合の結果(委任_03、read-only。確定=コード・ログで確認)
**(i) N3 L532のminimal fallbackにstyle引数が無い(M1の根拠)**: **確定**。`er003_v1_n3_01_tts_generate.py` L532は `_generate_a2_japanese_minimal_instruction(text, out_path, tts_backend=tts_backend)` で、Role Style(`style_prefix_override`)を渡していない。同関数の定義(L394-)は固定のminimal instruction(`_A2_JA_MINIMAL_INSTRUCTION_PREFIX`)を使い、「backendに関わらず意図的に無変更」(FAMILY-X-02 D-1コメント)。`JA_SPEC_SURVEY_01.md` L78(「Role Style(J3)を渡さない」)・L96(「J3を喪失」)と一致。標準経路(L516)のみStyleを転送する。**帰結**: 日本語でも3回目だけStyleが変わる(J3->minimal)。Voice/Model/Textは同じ。B1のCharon側は`er003_v1_sing01_voice01_generate.py` L395/L414(同種)。

**(ii) CURRENT_SPEC L1692と外側ループ(Coffee part2で5回生成)**: **確定**。
- CS:1692の文言: 「TTS生成の同一segment総試行回数上限 | **3回**(初回を含め最大3回。「初回+3 retry」ではない。**4回目以降は絶対にTTS生成しない**)」。標準2+fallback1=3に固定(2026-09-04ユーザー正式決定)。減速後の例外は書かれていない(L1692行内に「減速」「slowdown」の語は無い)。
- 実装: `er003_v1_n3_01_tts_generate.py` L248-262。`for attempt in range(1, max_slowdown_attempts + 1)`(既定3、L198)の各周で`generate_english_segment_with_fallback`(標準2+fallback1)を**新しい予算で**呼び直し、減速後検証が`STOPPED`ならもう一周する。
- Evidence(`er056_output/en_asr_confirm_retry_redesign_01/evidence_snapshot/ssot_logs/attempt_history_coffee_run_e.jsonl`、Coffee Standard `full_story_part2`、run_e): 1行目 15:13:34 `tts_attempts_this_call=1`/`result_status=OK`/`final_lock_state=RESOLVED`(初回合格。減速後検証でSTOPPEDだがLockはRESOLVEDのまま、Review Lock特例L242-252)、2行目 15:35:44 `tts_attempts_this_call=3`/`cumulative_tts_attempts=4`/`STOPPED`/`HUMAN_REVIEW_REQUIRED`(2周目で標準2+fallback1)、`full_story_part2_attempt1〜4`のwav/jsonが4本、これにLR再TTS1回(Lock非計上)。**合計TTS 5回**(`COFFEE_NG_ROOTCAUSE_01.md`)。標準2+fallback1=3の上限を超え、Lockの累計記録(4)もLR分を数えない。`slowdown_attempts_log`は`[{"attempt":1,"status":"STOPPED",...}]`の1件のみ(2周目は`generate_english_segment_with_fallback`が`STOPPED`を返し`status!=OK`のbreak[L252-253]で追記前に抜けるため)。理論最大は外側3周x3=9(LR等を含めると12)。
- 結論: **承認済み仕様(CS:1692)への違反**。単独OPEN(OPEN-270)で起票し、14-1に詳述。

**(iii) `er006_secondary_asr_01.py` Phrase Listとentity PASS**: **確定**(行の挙動)。
- L704-705: fallback経由のforced Secondaryは`get_full_text_via_azure_stt_with_phrase_list(wav_path, language, phrases=ledger_phrases)`、L774-775: 通常のSecondary #1も同じくPhrase List付き。どちらも`phrase_list_used`を記録。
- L783-788: `cls_s1.should_pass`がTrueならそのまま`verified=True`(`final_status=cls_s1.classification`)で戻る。ここでentity由来かどうかの追加確認(ARPAbet等)は行われない。Secondaryが原稿と一致した時点でPASSする。
- 補足(推測を含む): Primary段階で`is_entity_like_mismatch`/`homophone`でcascade対象になった音声は、Secondary(Phrase List付き)が原稿を返せばPASSする。Phrase Listは「この語が出るはず」というヒントなので、**確認の独立性は構造的に弱い**(Opus指摘どおり)。日本語SCGはPhrase Listなし(DL:20550の安全条件)で、さらにC1がentity差を持つTCMを除外するため、**英語の方が緩く非対称**。固有名詞をASR consensusだけでPASSさせないというCS:1693の原則(CMU辞書、Ledger)とも、英語Secondary経路の実装は完全には整合していない可能性がある(コード全体の網羅確認は未実施、推測)。

**(iv) 「C1は旧承認と向きが逆」(委任_02/v01)対「言い過ぎ」(Opus)の判定**:
- 確定した事実:
  1. CS:1998の文言は「固有名詞・略語らしき語**のみ**のASR不一致(entity-like)が疑われる場合、TTSを即座に再生成せず...Azure Secondary ASR #1(entity-like mismatch検出時のみ)」。対象は「entity-likeのみ」の不一致(`ASR_VALIDATION_UNCERTAIN`)。
  2. 旧Cascade(`evaluate_attempt_ja_with_cascade`)は`ASR_VALIDATION_UNCERTAIN`のときだけ起動する。g8は「熟->じく」(非cascade差)を含むTCMなので、**旧方針でも対象外=再生成**になる。
  3. 2026-09-09の実運用記録: g8はattempt1=NG(TCM)->再生成attempt2=「熟すと出るガス。」でNORMALIZED_MATCH合格(再生成1回、`kp4_ja_charon_attempt2_standard.json`)。**旧承認どおりの動作**で、C1が旧承認と逆の結果を生んだ事実はない。
  4. `_scg_exclusion_reason`(`er007_ja_secondary_asr_01.py` L183-210)のC1(L199-202: entity_like差を含むTCMはSCGに送らない)は、「旧方針と同じ=再生成」を維持する側。SCG(新設)は旧方針より**救済を増やす**仕組みで、C1はその一部を旧方針に戻す条件。
- 見解の分かれ(両論併記):
  - 委任_02(v01)の見解: 旧承認は「entity-like差分が検出されたらSecondaryへ送る」方針なので、C1が同種の差分でSecondaryを呼ばないのは向きが逆。
  - Opusの見解: 旧方針でもCascade非対象差分(g8の「熟->じく」)を含むTCMは再生成であり、「逆向き」は言い過ぎ。
- **判定(Fable向けの根拠、実行層の判定)**: **Opus見解を採用**。根拠は上記1〜3(CS:1998が「のみ」であること、旧Cascadeの起動条件が`ASR_VALIDATION_UNCERTAIN`であること、9/9実運用が旧承認どおりであること)。v01の「向きが逆」は**撤回**し、「C1と旧承認は矛盾というより、旧承認の範囲外の領域に新設SCGが入り、その一部をC1が旧方針へ戻している」と訂正する。
- 残る**真の内部矛盾**: 同じ濁点差(ガ->カ)が、単独ならUNCERTAIN経路で`phonetic_uncertain`として旧Cascadeの救済対象になる一方、非cascade差と同居するとC1で「固有名詞(entity_like)」扱いとなりSCG除外になる。同じ差分が、同居する語によって救済側/除外側に分かれる。根はカタカナ比率(>=0.5)による**固有名詞の粗いヒューリスティック**。英語の`entity_like_source=capitalized`(大文字始まり=固有名詞扱い、`US`/`U.S.`の偽NG、F-5)も同型で、**日英共通原因は「固有名詞のヒューリスティック推定の粗さ」**(OPEN-272)。

---

## 1. 現在の日本語・英語仕様の比較表

「承認」: U=ユーザー正式承認/決定、F=Fable/Opusレビュー判断で実装(ユーザー個別承認の逐語なし)、T=Trialのみ。「配線」: P=Production正式経路で配線済み。英語側のコード行は`main`基準。Coffee実runは`main`未merge branch(`feature/coffee-new-tone-01`)で実行されており、差があるものは[branch]と明記。

| # | 論点 | 日本語(現行) | 英語(現行、`main`) | 目標案 | なぜ存在 / 承認(CS・DL行) / 配線(コード行) |
|---|---|---|---|---|---|
| 1 | Primary ASRと判定器 | OpenAI gpt-4o-mini-transcribe(ja-JP)。6分類(EXACT/NORMALIZED/PHONETIC/UNCERTAIN/TCM/READING_RESOLVED) | 同モデル(en-US)。`classify_asr_match`(Tier1数値等価、表記ゆれ正規化、内容語差、entity/homophone) | 初回Primary 1回 | JA: 旧「文頭一致+文字数」方式を全文Validatorへ置換(2026-08-25 U、CS:1945/1993、DL:148[履歴]、`er007_ja_asr_validator_01.py` L333-504、SEC L28)。EN: Cascade導入2026-08-22〜24(CS:1945/1997、DL:145[履歴])、Tier1/3は2026-09-27 U(CS:2000、DL:9735)。EN配線 P: `er006_preprod_hardening_01_validation.py` L1159-1291 |
| 2 | Primary NGの種別 | TCM(数字・否定・非cascade差)とUNCERTAIN(カナ置換/濁点差のみ)の二分 | TCM / UNCERTAIN(entity-like/homophone-like) / TTS_FAILURE(類似度<0.4)。差の無い一致率不足のUNCERTAINもある | 「Primary NG」で一本化 | JA: VAL L491-498、DL:149[履歴](ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01、2026-08-25 U)。EN: val L958-1135、`er006_secondary_asr_01.py` L182-205 |
| 3 | Secondary起動条件 | (1)Primary=TCMのとき**再生成前に**Azure 1回(SCG、除外9条件)。(2)UNCERTAIN時は旧Cascade 4段 | (1)**TCMでは呼ばない(即再生成)**。(2)entity/homophoneのUNCERTAINのみ Primary#2 -> Azure#1 -> Azure#2。(3)Tier3(複数形・固有名詞1語差)・CS Equivalence Layer(5role)・Key Phrase非ラテン文字では個別にAzureを呼ぶ | Primary NGなら(除外を除き)Secondary 1回 | JA(1): 2026-10-11 U(SCG V1採用、CS:1994、DL:20550)。配線 P: SEC L399-425。JA(2)は2026-08-25 U(CS:1998)。EN(2): 2026-08-24 U(CS:1997、DL:145)。EN配線 P: `er006_secondary_asr_01.py` L723-864、CS層 L542-591(2026-09-07 U、CS:2007、DL:212)、Tier3 L593-674(2026-09-27 U、CS:2000)。**英語に「TCM時のSecondary確認」が無いのがSCGとの最大の非対称** |
| 4 | Secondary側のPASS条件 | SCG: EXACT/NORMALIZEDのみ(PHONETIC不可)。旧Cascade: PHONETICもPASS | `should_pass`(HIGH_SIMILARITY_SAFE等を含む)。Tier3は「Azureがdiff位置で原稿語を支持」したとき。Azureは**Phrase List付き** | 両エンジンNGで再生成 | JA SCGのPHONETIC不可=ユーザー決定済みの安全条件(DL:20550)。EN Phrase List: Azureが綴りを揃えやすい代わりに原稿寄りになる余地(CS:1994が日本語で不採用とした理由)。日英内で不統一(JA内もSCG/旧Cascade) |
| 5 | 数字・否定・固有名詞・同音異義 | 数字/否定差=SCG不実行。辞書読み不一致・カナ置換・ラテン文字=SCG不実行(C1)。同形異音語=SCG不実行(C2)。PHONETIC_MATCHは漢字の正誤を問わずPASS | 数字/否定差=`protected_check`で再生成(Secondary呼ばず)。固有名詞はCMU辞書で発音一致のときのみ自動PASS(「ASR同士の収束だけではPASSしない」)。同音異義はhomophone判定 | 例外は10章 | JA: 数字/否定=2026-08-25 U、C1=F(ユーザー個別承認の逐語なし、DL:20550は「g8 13/14受入=最終確認待ち」)、C2=2026-10-11 U。EN: CS:1693(2026-08-28 U) |
| 6 | TTS総回数 | 3回(標準2+minimal fallback 1) | A2: 3回(標準2+fallback 1)だが、**6%減速NGで全体が最大3周し、理論最大12**。Advanced: 3(+技術失敗時の別Prompt 2回目TTSで最大6)。Key Phrase英語は4回(Minimal 2+English lock 2) | 3回 | 3回=2026-09-04 U(CS:1692、DL:58/59[履歴]、LOCK L80/L102-104)。KP 4回=2026-09-01 U(CS:1911、DL:79[履歴]、`er003_v1_repro01_main_generate.py` L633-635)。英語の外側ループ=`er003_v1_n3_01_tts_generate.py` L248-266 |
| 7 | fallback(3回目) | minimal instruction(日本語J3 styleを渡さない) | A2: minimal(`natural, clear, conversational`、減速指示なし)かつ**Primary PASSでもAzure必須(force_secondary)**。[branch]ではA2のStyleを維持 | 除外(同一Prompt) | JA: ER-003-N3-ROOT-FIX-01(instruction leakage対策、DL:132[履歴])、N3 L473-532・V01 L434-。EN: 導入2026-08-08、force_secondary必須化2026-08-26(CS:1911、DL:156[履歴])。**force_secondaryは、fallback経路での誤PASS事故(point_one_heading)の暫定対策**で、根本原因は未決(OPEN-66/67、CS:1911)。EN配線: `er003_v1_crosslevel_audio_02_common.py` L165-259・L292-355 |
| 8 | Local Rewrite | **なし**(OPEN-260未承認。Gate7がASCII語数で日本語非対応) | あり: 3回NG後に問題spanだけLunaで書換え、7 Gate、再TTS 1回。5role限定 | 通常retry外 | EN: 2026-09-26 U(CS:1971、DL:9586)。配線 P: crosslevel L252-258/L282-288/L383-412、`er003_v1_sing01_news_tail_fix.py` L290-368、`er003_v1_sing01_voice01_generate.py` L291-359。JA: OI:762 |
| 9 | cool-down | なし | attempt3の直前のみ固定600秒(5role+CS層ON) | 未規定(D-5) | EN: CS:1971。配線 P: `er020_tts_retry_local_rewrite_01.py` L63-90。効果の対照データなし(`FREE_VERIFICATION_01.md` 4-4) |
| 10 | 6%減速後の再検証 | なし | A2英語のみ。減速後に**Primary 1回だけ**で再検証、NGなら標準2+fallback+LRを丸ごとやり直し | 「3回」を破らない形に | EN: 2026-08-26 U(CS:1916、DL:163[履歴])。配線 P: `er003_v1_n3_01_tts_generate.py` L117-268。Review Lockは`RESOLVED`でも再実行をブロックしない(`er011_human_review_lock_01.py` L242-252、6%減速retryのため) |
| 11 | Human Review移行 | 3回後STOPPEDまたはUNCERTAINで旧Cascade尽き。キュー`er007_output/ja_asr_cascade_01/` | 3回(+LR)後。キュー`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`。fallback経路はcascade_steps未保存、重複排除でAzure転写が残らない | 再生成(2)後 | EN: CS:2001(2026-08-22 U)。JA: LOCK L255-310。**日英でキューが別パス**。累計TTS15/ASR60のBudget Guard(LOCK L68-69) |
| 12 | role/Family別 | 全JA segment同一Validator+SCG | CS層・LR・Tier1/3は5role限定(Full Story/Comment/Preview/Topic intro/In One Line)。Key Phrase・共有殻は別構成 | 全role共通か役割別か未決(D-9) | EN段階拡張: 2026-09-07(A2/B1本文のみ)-> 2026-09-26/27(5role)(CS:2007/1971/2000) |
| 13 | Voice/Style一貫性 | 標準=J3、fallbackでminimalに変化 | 標準=role style、fallbackでminimalに変化([branch]は維持) | 同一Prompt固定 | J2_BRIGHT/E2_UPBEAT(Tone Trial、2026-10-11 approved-but-unwired、`docs/pm/design/2026-10-11_FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01_X_INVENTORY_01.md` L85)導入後はfallbackで失う差が目立つ |
| 14 | 費用・時間の目安 | SCG 1回約0.16円・1.4秒(短文)。再生成1回約0.1円・120〜170秒 | Azure 50秒の本文で約2.2円・12〜24秒。TTS 1回約0.135円・約120秒。cool-down 600秒 | - | JA: RESULT_01(5)。EN: Coffee raw_usage_log(別紙で再計算)。**英語のAzure 1回は日本語SCGの約10倍高い**(音声が長いため) |

---

## 2. なぜ異なる仕様になったか(必要な違い vs 歴史的継ぎ足し)

判定の基準: 「その言語の性質がその違いを要求するか」「両言語で同じ根拠を同じ水準で当てはめた結果か」。「以前からある」「固有名詞だから」は根拠にしない。

| 項目 | 判定 | 理由(確定/推測) |
|---|---|---|
| 判定器の中身(日本語=読み・漢字・かな、英語=発音辞書・短縮形・複数形) | **必要な違い** | 日本語は同じ音に複数の漢字/読みがあり、英語は綴りと発音が一致しない。判定の材料自体が違う(確定) |
| Primary/Secondaryのエンジン(OpenAI/Azure) | 違いなし | 2026-08-25に両言語で統一(CS:1945) |
| Primary NG時のSecondary起動(JA=TCMで確認、EN=TCMでは確認しない) | **歴史的継ぎ足し** | 英語Cascadeは2026-08-22〜24、日本語SCGは2026-10-11と導入時期が離れ、英語には後追いで同等の機構が入っていない(確定)。英語側で入れない理由の記録は見当たらない(英語側が起票候補(a)としている) |
| Secondary PASS条件(JA=厳格、EN=Tier3等で広め)・Phrase Listの有無 | **歴史的継ぎ足し + 要判断** | 日本語は誤PASS防止の安全条件としてユーザーが決定、英語は救済率優先で段階的に増えた。どちらが正しいかは実測が無い(Phrase Listが誤PASSを生むかは**未測定**) |
| 数字・否定でSecondaryを呼ばない | 違いなし(両言語で既に同じ) | 数量・肯否の反転は意味が逆になる。両言語とも実装済み |
| UNCERTAINの扱い | 現行は日英ほぼ同型。**目標案(再生成へ)との差**がある | 現行のHR直行は「再生成しても解決しない可能性が高い」というユーザー承認(DL:149[履歴]、CS:1998)に基づく。英語queue 67行中49行が「Primary#2・Azure#2まで4段全て実行して未解決」の形で、再試行の効果が薄いことを示唆する(確定: 行数・段の並び。**転写が同一かは英語では全件未確認**、Coffee標準2回目の1件は同一。`FREE_VERIFICATION_01.md` 4-5) |
| TTS総3回・2+1内訳 | 違いなし | 2026-09-04 U。ただし英語は外側ループで破られる(下記) |
| 英語の6%減速後再検証と外側ループ | **減速自体は必要な違い(英語A2の学習者向け速度仕様)、外側ループは継ぎ足し** | 外側ループが「3回」を実質12回に広げる構造は、承認(CS:1692)と整合しない副作用(確定。F-1) |
| minimal fallback | **歴史的継ぎ足し(導入理由が弱まった可能性)** | 長いStyle指示でモデルが読み上げず応答する現象の対症療法として導入(確定、crosslevel L50-59)。現行のFlash-Lite backendではStyleが短く発生条件が違う(確定)。再発率の実測は**無い**ので「不要」とも断定できない |
| Local Rewrite・cool-down(英語のみ) | **日本語に無いのは「必要な違い」ではなく未対応** | Gate7がASCII語数で日本語非対応という実装上の理由(OI:762)。英語の実績: 過去18記録中8件を回復(約47%)、ただし本文を書き換える |
| role gating(英語は5role限定) | **歴史的継ぎ足し** | 2026-09-07の限定導入 -> 09-26/27の拡張という段階的追加(確定)。役割ごとに本質的に違う根拠は記録に無い |
| HRキューの出力先が日英別 | **歴史的継ぎ足し** | 品質の違いではなく運用上の別実装(確定) |
| Azure取得関数(JA SCG=strict、旧Cascade=共通関数) | **歴史的継ぎ足し** | Opus必須2の指摘をSCG内だけに適用し、共通関数は無変更とした判断(確定) |

要約: **言語の性質が要求する違いは「判定器の中身」と「英語A2の減速」だけ**。それ以外の差(Secondaryの起動範囲、PASS条件、fallback、Local Rewrite、role範囲、キュー)は、導入順序・承認時期・実装の都合による。

---

## 3. g8「ガス->カス」調査結果(確定/推測を分離)

対象: Phase 0 Trial g8(原稿「熟すと出るガス」、`kp4_ja_charon` attempt1、2.28秒)。

### 確定したこと
- Primary(OpenAI)の転写は「じくすと出るカス。」。Azure(Phase 0、Phrase Listなし)は「熟すと出るガス。」(NORMALIZED一致)。ローカルwhisper small/mediumも「ガス」(濁音)と転写。
- **Primary NGの直接原因は「熟 -> じく」(「じゅくす」の「ゅ」が欠落)**。これは読みが一致しない非cascade差で、TCMになる。「ガ -> カ」は単独ならUNCERTAIN(旧Cascadeで確認される)の濁点差。
- **SCGが走らなかった理由**: `_scg_exclusion_reason`(`er007_ja_secondary_asr_01.py` L183-210)が、同じ発話内の「ガ->カ」を`entity_like`(カナ置換でカタカナ率>=0.5)と判定し、L200-201で`entity_like_diff:ガ->カ`として除外した。Azure呼出は0回。
- 実行確認(委任_01、Azureのみmock): 現行コードでは`scg_result=NOT_APPLIED / verified=False`。C1の`entity_like`除外だけ外した仮想では`scg_result=PASS / azure_calls=1`。`er007_ja_scg_phase0_regression_test_01.py` 12件PASS。
- 除外を外しても、Phase 0のC群(真のTTS誤り5音声)の誤PASSは**0件**(CURRENT/NO_C1/HARD_ONLY/ALL全て)。
- 実運用結果(2026-09-09、SCG導入前): attempt1 NG -> 再生成attempt2で合格。再生成1回。
- 承認根拠(確定): C1(entity_like/辞書読み/ラテン除外)はOpus必須1をFableが採用したもので、**ユーザーがg8を13/14のまま受け入れるという逐語決定は無い**(DL:20550は最終確認待ち)。(旧承認との関係は**v02で訂正**: 下の3-補、0-2(iv)。v01の「向きが逆」は撤回。)
- 実装上の問題(確定): `entity_like`は意味上の固有名詞判定ではなく「カタカナ率のヒューリスティック」。一般語「ガス」も1文字の濁点差も巻き込む一方、挿入/脱落(メタ->メタン)は取りこぼす(合成確認)。

### 推測(確認できていない)
- g8の音声は「ガス」と正しく発音され、Primaryの誤認識だった可能性が高い(3系統が「ガス」)。ground truthは**試聴のみ**で、人間の確認は未実施。
- 「音声が実際に『カス』だった場合にAzureが『ガス』へ丸めて誤PASSするか」は、**濁点誤りを含む実標本が0件のため未測定**。社外->社会の例(旧Cascade queue、Primary/Azure 4回とも「社会」)は、高頻度語へのASR偏りが起きうることを示す(TTSが「しゃがい」と言ったかは不明)。
- C1が守ろうとした本質(名前・社名・外来語など、全文一致では発音の正否を判断できない語)は妥当だが、g8のような一般カタカナ語・濁点単独差まで除外する根拠は薄い(評価: 一般カタカナ語は**B(統一可能)**、真の固有名詞は**A**。最終は9章U-1)。


### 3-補. C1と旧承認の関係(委任_03で訂正、両論併記は0-2(iv))
- **訂正**: 上の「旧承認との不整合」は**撤回**する(v01の「向きが逆」は言い過ぎ)。Opusレビューとコード照合の結果、旧承認(CS:1998)は「entity-like**のみ**の不一致(UNCERTAIN)」が対象で、g8のような非cascade差を含むTCMは旧方針でも再生成。2026-09-09の実運用(再生成1回で合格)は旧承認どおり。
- 残る問題は2点: (1)C1の`entity_like`が「カタカナ比率>=0.5」の粗い推定で一般語(ガス)も巻き込む、(2)同じ濁点差が`phonetic_uncertain`(救済)と`entity_like`(除外)に分かれる内部矛盾。後者は日英共通の「固有名詞ヒューリスティック推定の粗さ」(英語`capitalized`、US<->U.S.の偽NG)と同型(OPEN-272)。
- g8の最終判断(13/14受入かC1見直しか)は9章U-1。**C1見直しは新しい例外仕様の変更にあたるため採用ではなく選択肢**。

---

## 4. Coffee NG判定・不要再生成の原因

対象: Coffee Standard `full_story_part2`(worktree `eigo-radio-tone`、branch `feature/coffee-new-tone-01`、Phase 2 run_e)。総計: TTS 5回、OpenAI ASR 7回、Azure 4回(197.8秒)、LLM 2回、所要24分57秒。Lock上のTTS記録は4(LR再TTSを数えない)。

### 4-1. 減速前のPrimary PASSがなぜ次attemptに進んだか
- **確定**: 初回TTS(15:13)はPrimary=NORMALIZED_MATCHで合格。直後の6%減速処理(`apply_a2_slowdown_postprocess`、`er003_v1_n3_01_tts_generate.py` L117-194)が、**Primaryだけ1回**で再検証し、結果は`ASR_VALIDATION_UNCERTAIN`。これで`status=STOPPED`となり、外側ループ(最大3周、L248-266)が**新しい3回分の予算で標準2+fallback1を最初から再実行**した。
- **確定**: 減速後に何と聞こえたかの転写は**保存されていない**(結果dictが上書きされる、F-2)。
- **推測**: 原因は標準2回目と同じ表記差の偽NG(`US`/`U.S.`+`cost`/`costs`)。根拠は(i)減速を再現してローカルwhisper smallに通すと原稿一致(mediumは`People`脱落で不一致)、(ii)同型のUNCERTAINが標準2回目で実際に起きている。**減速そのものが内容を壊した証拠は無い**。
- 分類: **retry制御の設計**(仕様どおりに動作した結果、合格済みの音声を捨てた)。

### 4-2. Attempt 1・2(標準1回目・2回目)は仕様どおりか
- **標準1回目**(15:16): Primary=TCM(`showed -> show`、非固有名詞の内容語差)。CS層は事前チェックで対象外(NEVER_ELIGIBLE)。英語にはTCM時のSecondaryが無いので**Azureを呼ばず即再生成 = 仕様どおり**。Validator再実行で記録と一致(確定)。ローカルwhisper small/mediumは原稿どおり(`showed`)と転写。**OpenAIの誤認識か本当に`show`と発音されたかは未確定**(人間の耳が必要)。**目標フローなら、ここでAzureが確認でき、救済または確定できた**。
- **標準2回目**(15:18): Primary#1・#2とも`UNCERTAIN`(差分は`us`->`u s` x3のみ、`capitalized`でentity-like扱い)。cascadeでAzure x2を呼び、AzureはTCM(`raw bean -> robbing`、文の入れ替わり)。**仕様どおり**。ただし**Validatorの偽NG**(`US`と`U.S.`の差は単独なら問題なしだが、`cost`/`costs`と同時に出ると落ちる、F-5)と**Azureの聞き間違い**の複合。OpenAIとローカルwhisper 2モデルは同じ音声を原稿どおりに転写。
- 帰結: HRログ -> `stop_retrying` -> 10分cool-down(約13分消費)。

### 4-3. Attempt 3(fallback)はなぜ「転写に差が無いのにNG」か
- **確定**: Primary転写は原稿と実質同一でPASS。attempt jsonの`TRUE_CONTENT_MISMATCH`は**Azureの強制確認(force_secondary)の判定**。fallbackは「Primaryが合格でもAzureを必ず呼び、Azureが不一致なら不合格」という仕様(CS:1911、`er006_secondary_asr_01.py` L699-721)。
- **確定**: Azureがどんなテキストを返してNGにしたか、**転写は保存されていない**(fallback経路はcascade_stepsを持たず、HRキューは同一音声+同一原稿の重複排除で追記されなかった、F-3)。
- **推測**: Azureの誤認識(ローカルwhisper 2モデルは原稿一致)。**断定不可**(欠けている証跡: attempt 3[fallback]のAzure転写全文)。

### 4-4. Attempt 4(Local Rewrite再TTS)のNG
- **確定**: Primary PASS、Azure不一致(`raw bean -> Robbing/Robbins`)で最終NG。**Local Rewriteが書き換えた箇所は無関係**(NG spanをPrimary転写と原稿の最初の差=`us`/`u s`で選び、`US data -> data from the United States`に書換え。実際のAzure不一致箇所`raw bean`は未変更、F-4)。この「Primary PASS・Azure NG」型の失敗に対し、Local Rewriteは**原理的に効かない**。
- **未確定**: ローカルwhisper smallもAzureと同じ`robbing`、mediumとOpenAIは`raw bean`。2/4系統が`robbing`なので、**この音声で本当に`raw bean`が曖昧に発音された可能性は排除できない**(人間の耳が必要)。

### 4-5. 不要再生成の有無(総括)
| # | 再生成 | 判定 | 区分 |
|---|---|---|---|
| 0 | 初回合格後の再生成 | 合格済み音声を捨てた。減速自体が内容を壊した証拠なし | 設計不備は**確定**、「再検証NG自体が偽」は推測 |
| 1 | 標準1回目の次(標準2回目へ) | `showed/show`は未確定。ローカル2モデルは原稿一致 | **未確定**(人間の耳待ち) |
| 2 | 標準2回目の次(fallbackへ) | Validator偽NG+Azure聞き違いの可能性が高い(OpenAI/ローカル2モデルが原稿一致) | 推測(確度高) |
| 3 | fallback後(LRへ) | Primary PASS・Azure NG。Azure転写が無い | 推測(確度中) |
| 4 | LR再TTS後(HR) | 本当に曖昧な発音の可能性あり | **未確定** |

**合格相当だった可能性が高い音声は5本中3本以上**(標準1・2回目、fallbackの3本はローカルASR 2モデルとも原稿一致。初回はsmall一致・medium不一致で2系統一致ではない)。**「真の音声不良」として確認できたものは0件**。確実に不要だったと断定できる再生成は、人間の試聴が済むまで**1件も無い**(推測を事実に混ぜない)。

### 4-6. 英語ASR-first仕様(CS:1997)の適用状況
- 標準1回目: ASR-first対象外(TCM、entity/homophone UNCERTAINでない)-> 仕様どおり即再生成。
- 標準2回目: ASR-firstが**適用された**(Primary#2 -> Azure#1 -> #2 -> HR)。ただし結果は「Primary#2は同一転写、Azure#2も同一転写」で、追加確認に独立性が薄い(確定)。
- Tier3(複数形・固有名詞の1トークン差の救済)は、差分が3トークンのため**対象外**と推測(コード条件の読み取りで、個別には再現していない)。CS Equivalence Layerは事前チェックで対象外(確定)。
- 結果: 偽NGを救う仕組みはいくつもあるが、条件が分散していて今回の2種(`showed/show`の内容語差、`US`の表記差+複数形の同時発生)にはどれも届かなかった。


### 4-7. 委任_03で追加した事実(Opusレビュー反映)
- **L1692違反**: 外側ループにより標準2+fallback1の予算が周ごとに再設定される。Coffee part2はTTS 5回(0-2(ii))。減速後の検証は`evaluate_attempt_with_cascade`ではなくPrimary + homophone(`should_pass`のみ)で、cascade/Tier3/CS層は未配線(`er003_v1_n3_01_tts_generate.py` L184-193、L208-210)。**通常経路より厳しい別経路**になっている(Opus確認)。
- **Local Rewriteの再TTSもminimal fallback関数を通る**: `er003_v1_crosslevel_audio_02_common.py` L383(`_retts_fn`が`_run_a2_minimal_fallback_attempt`を呼ぶ)。したがってLR再TTSはfallback用の短いStyle(`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`)を使い、(main上では)**Styleも変わる**。Coffee branchのstyle維持は`feature/coffee-new-tone-01`のみ。
- **LRのNG span選択**(`crosslevel` L260)はPrimary転写と原稿の最初の差から選ぶため、Primary PASS・Secondary NG型では正しい箇所を特定できない(4-4、F-4)。
- **Secondary#1(Azure)はPhrase List付き**(`er006:704-705/774-775`)。Coffeeの`raw bean -> robbing`もPhrase List付きの結果。Phrase Listは原稿寄りの転写を促すため、PASS判定用としては独立性が弱く、NG判定側(偽NG)でも「聞き違い」を排除できていない点に注意。

---

## 5. 統一を推奨するルール(日英共通の判定軸・フロー)

提案のみ。採用はユーザー判断(9章)とOpus独立レビューが前提。

### 5-1. 共通フロー(目標案に沿った骨格)
1. 初回TTS -> Primary。**PASSなら完了**(Secondaryは呼ばない。fallback用の強制Secondaryは廃止)。
2. Primary NG -> まず**「重大差分ゲート」**: 数字差/否定差/類似度極小(TTS異常疑い)/長さ超過/辞書読み不一致/繰り返し・言い淀みQA不合格のどれかなら**Secondaryを呼ばず**再生成へ(日英共通の「真の内容誤りを救わない」層)。
3. 重大差分に該当しなければ**Secondary 1回**(同じ音声に対し、Phrase List無し推奨は英語D-2と同じ論点)。Primary#2・Secondary#2は廃止(同一転写の再実行は独立性が低い、確定)。
4. Secondary PASS(厳格集合のみ)-> 完了。両NG -> 同一Promptで再生成(1)、(2)。各回で同じ判定。
5. 両NGが3回続けば Human Review。
6. **技術失敗(TTS 400/空応答/無音)・ASR障害(転写None、Secondaryエラー/タイムアウト/途中キャンセル)を、音声不良と区別**して記録。attemptを消費するか(D-8)は別判断。
7. 全attemptでPrimary/Secondaryの転写全文・判定・理由を保存(現在は英語のfallback・減速後、日本語SCGのHR投入などで欠落)。
8. Prompt fingerprint(model・voice・style・減速有無・原稿の組)を3回とも同一にassert(英語設計案§3-1)。

### 5-2. 統一を推奨する項目と理由
| 項目 | 推奨 | 理由(根拠) |
|---|---|---|
| 英語にも「TCM時のSecondary確認」を入れる | 推奨(要承認) | 日本語に既にある。Coffee標準1回目のような偽NGを再生成前に確認できた(4-2)。過去のcascade救済率は35%(8/23)、独立ASRによる救済余地は内容語・表記型に偏り、数値/否定/固有名詞では小さい(ローカルASR代理検証: 数値・否定0/4、entityのみ0/5) |
| Primary#2・Secondary#2の廃止 | 推奨 | 日本語HR 8件は全てPrimary#2=#1、Azure#2=#1の同一転写(確定)。英語queue 67行中49行が4段全て実行の形(転写の同一性は英語では未確認、Coffeeの1件は同一)。ASR呼出が4->2に減る |
| force_secondary(Primary PASSでもAzure必須)の廃止 | 推奨(fallback廃止が前提) | Primary PASS・Azure NGの4件(重複除き)はAzure側の誤認識・脱落・表記差が大半に見える(確定)が、元のfallback経路での誤PASS事故(point_one_heading)の根本原因は未決なので、**fallbackを廃止する場合にのみ**自然に消える |
| 6%減速後の「3回超過」の是正 | 推奨(案B。**Opusレビュー反映: 案B'へ変更**、5-4・U-7) | 3回上限(CS:1692)と実装が矛盾(Coffee: TTS 5回、理論最大12)。案Bは仕様変更を伴わず、attempt内に折り込む |
| 証跡の保存漏れの解消(減速後転写、fallback cascade_steps、HRキュー重複排除) | 推奨 | 今回の原因究明で証跡欠落が最大の障害だった。判定には影響しない |
| HRキューの統合、Azure取得関数のstrict統一(X13/X14) | 推奨(低優先) | 運用上の見落としと、途中キャンセル時の誤判定リスクの解消。実害の報告は無い |
| Secondary PASSは「厳格集合」で日英共通 | 推奨だが論点あり(U-3) | 日本語はユーザー決定済み。英語のHIGH_SIMILARITY_SAFE(単数/複数)を含めるかは別判断 |


### 5-3. 推奨ルール(Claude案+Opus案の照合結果)
Opusが提示した統一ルール案10項目(私見)と、v01の5-1/5-2(Claude案)を照合した。**すべて提案で、採用はユーザー判断**(9章)。「一致」=両案が同方向、「相違」=結論または細部が異なる(判断が必要)、「新規」=v01に無く、Opus案で追加。

| # | Opus統一ルール案 | v01(Claude案)との照合 | 区分 | 関連判断 |
|---|---|---|---|---|
| 1 | TTS最大3回・同一fingerprintをassert・一時的技術失敗は**attempt外**・上限付き | 3回・fingerprint assertは一致(5-1の8)。技術失敗: v01は「attempt消費か非消費か別判断(D-8)、非消費2回案」 -> Opusは「5xx/429/timeoutはattempt外で上限付き、**無音・異常長はattempt消費**」(M4)。fingerprintに`tts_execution_mode`/model ID/stretch比を含める点は**新規** | 一致+細部相違 | U-10 |
| 2 | 検証対象は**最終納品音声のみ**(6%減速は案B') | v01は案B(attempt内折込み)。Opusは「案Bは偽NG倍増、案Cは最終音声未検証、案B'(生成->stretch->最終音声のみPrimary->Secondary 1系統)」(M3) | **相違** | U-7 |
| 3 | Secondary不呼出条件: 数値(漢数字・数詞語含む)・否定(日本語マーカー・英語短縮形含む)・length_ok=False・反復/言い淀みQA NG・言語ドリフト・ASR障害はASR再試行へ | v01の重大差分ゲート(数字/否定/類似度極小/長さ/辞書読み/QA)と一致。**新規**: 言語ドリフト、漢数字・数詞語(日本語数値判定が`\d+`のみで漢数字漏れ、X1)、ASR障害の扱い | 一致+追加 | U-12 |
| 4 | 類似度下限は一定長以上のみ(短文は除外、C) | v01 U-12は「維持(新閾値を採用しない)」。Opusは短文では下限を適用しない案(g7「湿度->死図塔」型の救済)。標本は1件のため暫定 | **相違**(判断) | U-12 |
| 5 | Secondary 1回、**Phrase Listなし**、厳格ラベル(EXACT/NORMALIZED/TRANSCRIPT_STYLE/NUMERIC_EQ)でPASS判定(should_passではなくラベル)。日本語PHONETICは案C | Phrase Listなしは一致(v01 U-8暫定)。**相違**: (a)Secondaryを何で使うか(Azure/local/併用)は未決、(b)日本語PHONETICの扱い: v01 U-3は厳格のみ、Opus私見は「Primaryと同じ制約下で対称許容(+3 group、誤PASS 0)」 | 一致+**相違** | U-3、U-8 |
| 6 | 固有名詞は**辞書・Pronunciation Ledger・登録語**で判定。カタカナ比率・大文字推定は廃止。ASR一致だけではPASSさせない | v01は「C1の扱い(U-1)」と「ASR consensus ≠ verification(E5)維持」。Opusは**推定ヒューリスティック自体の廃止**まで踏み込み、英語のentity+Secondary一致PASS(0-2(iii))を問題視(M2、M7)。英語TARGET §3-9「固有名詞: 残りは確認ゲート」と日本語C1の矛盾を解消する統一ルールが必要 | **相違**(範囲) | U-1、U-17 |
| 7 | 同形異音語(日本語C2)は維持。**英語の異音同綴語(read/lead等)は最終試聴** | C2維持は一致(E6)。英語の異音同綴語は**新規**(実装/辞書は未設計) | 一致+新規 | U-13、OPEN-263 |
| 8 | 最小対・形態素型差分(-ed脱落・-s・冠詞・濁点/半濁点・長音/促音・社外/社会型)は`PASS_WITH_WARNING`+最終試聴へ自動連動。推奨: local whisper mediumが差分箇所で原稿を支持することを追加条件(M6) | v01に**無い**。v01は「誤PASS 0/16(Validator側のみ)」を根拠にしていたが、Opusは「リスク本体はASRのLM prior(原稿側が高頻度語で音声が最小対の低頻度形)」と指摘。Azureの丸め実例は偽NG側、社外->社会はPrimary/Azure 4回とも「社会」 | **新規**(最重要) | U-18 |
| 9 | 両NG -> 再生成 -> 3回後HR。minimal fallback・Local Rewrite・force_secondary・Primary#2/Secondary#2は**通常経路外** | v01の5-1/5-2(Primary#2/Secondary#2廃止、force_secondary廃止、U-4、U-5)と概ね一致。**相違**: UNCERTAIN->HR(再生成しない)を廃止するか(M5、例外案C: 両ASRが同じ誤りで一致なら即HR)。minimal fallbackは「廃止」か「決定論的技術失敗専用の隔離経路(`style_deviation=True`+最終試聴必須)として残す」かが論点 | 一致+相違 | U-2、U-4、U-5 |
| 10 | 言語固有を維持: 日本語=読み照合(辞書・C2)・否定活用マーカー、英語=CMU/ARPAbet・CS層の音韻カテゴリ、Key Phrase 4回構成(例外A) | v01の6章(E4/E5/E6/E8)と一致 | **一致** | U-9 |

要約: **一致点**=骨格(3回、同一Prompt、Primary NG->Secondary 1回、両NG->再生成)、Phrase Listなし、Primary#2/Secondary#2廃止、言語固有例外の維持。**相違点(ユーザー判断)**=6%減速(案B/B')、日本語PHONETIC許容、固有名詞推定の廃止範囲、類似度下限の短文扱い、UNCERTAIN->HRの廃止、minimal fallbackの隔離。**Opusだけが指摘した新規リスク**=ASRのLM prior(原稿寄せ丸め)による誤PASS、英語の異音同綴語。

### 5-4. 5-1の設計案の修正点(**Opusレビュー反映**)
5-1の共通フローは次のように修正する(提案)。
1. 適用範囲は**日本語・英語の両方**(M1)。ただしKey Phraseの4回構成(例外A)は維持。
2. 検証は最終納品音声のみ(6%減速は案B')(M3)。減速のために外側ループを持たない(L1692違反の解消)。
3. Secondaryを呼ばない条件を5-3の3のとおり拡張(言語ドリフト・漢数字等)。ASR障害は**ASR再試行**(attemptを消費しない)へ。
4. PASS判定用SecondaryはPhrase Listなし・原稿を与えない。PASSは厳格ラベルのみ(`should_pass`ではなく分類ラベルで判定)(M2)。
5. 最小対・形態素型の差分は`PASS_WITH_WARNING`として最終試聴リストへ自動連動(M6)。
6. 一時的API失敗(5xx/429/timeout)はattempt外・上限付き。無音・異常長はattempt消費(M4)。
7. UNCERTAIN->HR直行は新モードでは廃止(例外案C: 両ASRが同じ誤りで一致なら即HR)。承認済み仕様(2026-08-25 U)の変更であり、`stop_retrying`の意味(Cascadeを尽くした印)もそれに合わせて再定義が必要(M5、OPEN未起票だがU-2に含める)。
8. fingerprintに`tts_execution_mode`/model ID/stretch比を含め、3回とも同一であることをassert。

---

## 6. 維持すべき例外とその理由

「例外」=共通フローから外れる処理。分類A=必要(維持)。具体的な誤PASS例・過去根拠・代替策を併記。**合成例は「経路確認」であり、ASRの実力の証拠ではない**ことを明記する。

| ID | 例外 | 具体的な誤PASS例(実=実標本、合成=経路確認) | 過去の根拠 | 代替策 | 判定 |
|---|---|---|---|---|---|
| E1 | 数字差でSecondaryを呼ばず再生成 | 合成: 「理由は3つ」->音声「4つ」(JA: NOT_APPLIED確認)。英語: 合成16種の変異(6.1->6.7、9->10 months、2->3 numbers等)で厳格PASS集合の誤PASSは0/16(**Validator側のみ**) | JA 2026-08-25 U。EN: Primary NG 255ユニーク組中、数値差79(31%)、数値/否定計82(32%)。hormuz Full Story part1は数値・否定差が3回連続(本物のTTS読み違いの可能性が高い) | なし。「数値が原稿へ寄せられる」リスク(Secondaryの自動補正)は未測定のため、呼ばない方が安全 | **A** |
| E2 | 否定差でSecondaryを呼ばず再生成 | 実: g12「縛られず自由に」->Primary/Azureとも「縛られる自由に」(C群、TCMのまま)。合成: 「行かない->行く」NOT_APPLIED | JA 2026-08-25 U。推奨4(否定マーカー補強)は2026-10-11 U | JAに活用ギャップ(「来なかった->来た」はマーカー対象外でSCG実行、合成確認): 補強案は**新規仕様候補・未承認** | **A**(補強はC) |
| E3 | 長さ超過・Repetition/Disfluency QA不合格では救済しない | 目的は幻覚追加文・反復の検出。実害の誤PASS実績なし | JA `length_ok`(推奨6=F)、EN Repetition QA。英語は反復/追加文の合成テストで誤PASS 0 | なし。コスト最適化(Azure無駄呼出防止)も兼ねる | **A** |
| E4 | 辞書で読みが確定した語は読み一致で判定(辞書読み不一致=SCG不実行) | 辞書語Meta=メタをPrimaryが別読みで転写し、Azureの表記一致だけでPASSさせると読みの正否が検証されない(構造的想定、実データでの発火は未測定) | Opus必須1、CS:1693「ASR consensus != pronunciation verification」(2026-08-28 U)。EN CMU ARPAbet一致のみ自動PASS | 辞書の拡充(`expected_readings`) | **A**(概念) |
| E5 | 固有名詞はASR同士の一致だけではPASSしない | 実: OPEN-257 Muse事例。OpenAI/Azure(Phrase List付き)/ローカルwhisperの3系統が同じ誤聴("Some Muse"->"some use")。run1でTier3が`Some US calls`をverifiedにした(人間聴取は**未確認**) | CS:1693、OI:759(2026-10-11、包括対策は今回見送り) | HR、Case A(CMU一致)。包括対策B1〜B4は保留 | **A**(ただし「固有名詞」の範囲の定義がC1のように粗いのが問題 -> 9章U-1) |
| E6 | 同形異音語(原稿側漢字の別読み候補)ガード(JA C2) | 合成: 市場(いちば/しじょう)は漢字の正誤を問わずPHONETICでPASS(既存の盲点)。実: g5(名所/旅程)はC2で除外(結果はNGのまま) | 2026-10-11 U(DL:20550) | 辞書補強(OPEN-263)は**未承認候補** | **A**(概念)/ 補強は**C** |
| E7 | TTS技術失敗(400/空応答/無音)・ASR障害の区別 | 現行: Primary転写がNoneだとTTS_FAILURE扱い(音声不良と区別されない)。Secondary失敗はNG扱い | 英語設計案§3-9 | attempt非消費の技術再試行(最大2回)を設ける案(D-8) | **A**(区別の必要性。具体回数はC) |
| E8 | 英語Key Phraseの4回構成(Minimal 2+English lock 2) | 短語は別Prompt前提。KP 77 call中74が1回目合格(96%)で現行で十分 | 2026-09-01 U(CS:1911) | 対象外のまま(D-7) | **A**(ユーザー決定) |
| E9 | 共有殻(num_*等)の再利用優先 | OPEN-222(極短語の言語ドリフト): 47 call中17が未合格(36%)。Secondaryでは救えない(TTS側の問題) | OI:405 | 対象外 | **A**(本テーマ外) |

注: **過度に保守的になっている例**が実際にある。JAのC1(g8、一般カタカナ語)、類似度<0.4(g7「湿度」->Primary「死図塔」、Azureは正解)は誤PASSを防いだ実績がなく、救済機会を失っている(10章でB/C)。**Secondary(Azure)を「権威」にしすぎている例**もある(英語のforce_secondary: 4件はAzureの誤認識が大半に見える)。

---

## 7. 目標フローの実現可能性・QCD比較

優先順位: (1)音声品質(誤PASS防止、Voice/Style一貫性) (2)完成率 (3)コスト (4)時間。

### 7-1. 実現可能性(構造)
| 項目 | 日本語 | 英語 |
|---|---|---|
| Primary NG -> Secondary 1回 | **既にSCGで実装済み**(除外が多い、UNCERTAINは別経路) | 新ゲート(英語版SCG)が必要。Tier3/CS層とAzure呼出を共有する設計が必要 |
| 同一Prompt3回 | 日本語minimal fallbackの廃止(`generate_a2_japanese_with_fallback`・`generate_charon_japanese`、定数2+1の見直し) | A2: `generate_english_segment_with_fallback`の`fixed_prompt_mode`化+B1B技術fallback廃止 |
| Local Rewrite・cool-down | なし(差なし) | 呼出3箇所のガード、HR後オプション化(再TTS関数を独立させる必要あり、11章) |
| 6%減速の取り直し | なし | 案B(attempt内折込み)で仕様変更なし、実装は`n3_tts`の構造変更 |
| 実現可能性の総合 | 高(変更範囲は小さい) | 中(構造変更が大きい。Opus独立レビュー必須: 新しい処理フロー) |


**Opusレビュー反映(M1、7-1の訂正)**: 上表の日本語欄「既に目標型」「変更範囲は小さい」は**訂正**する。日本語にも、(a)minimal fallbackで3回目だけJ3(Role Style)が失われる(N3 L532、0-2(i))、(b)UNCERTAINは4ステップ後にHR(再生成しない)、(c)fingerprint(Prompt同一性の検証)が無い、という目標型との差がある。したがって新モードは**日英両方を対象**とし、日本語の変更は(1)minimal fallback廃止または隔離、(2)UNCERTAIN経路の目標型化(承認済み仕様の変更)、(3)fingerprint追加、(4)TTS回数定数(2+1、日英共有)の見直し。日本語の実現可能性は「中」。

### 7-2. QCD比較(現行 vs 目標)

**標本の偏り(先に)**: 日本語=Phase 0の25音声・20 group(Primary NGの保存音声から「救済できそうなもの」+誤PASS検証用C群を選んだもので、**母集団の率ではない**)。誤PASS判定は代理ラベル(whisper2モデル+Primaryが原稿と不一致)で、試聴確認が要る`needs_listen`5音声が未確定。英語=narrative5 160 call(2026-09-27〜のFlash-Lite期)。**A/B Trial arm・回帰テスト由来が混在**(未合格11のうちTrial arm由来6)。英語の目標側は実測ではなく確率モデル(2回目通過率0.59・3回目0.25の近似、信頼区間が広い)と合成テストによる**見込み**。Coffeeは1 segmentの事例のみ。

| 指標 | 日本語 現行(SCG) | 日本語 目標に近い設定(HARD_ONLY) | 英語 現行 | 英語 目標(見込み) |
|---|---|---|---|---|
| 誤PASS件数 | C群0/5(代理ラベル)。`needs_listen`5音声は試聴待ちで確定でない | 同0/5(濁点誤読を含む実標本が無い) | 合成16種で0/16(Validator側のみ、Secondary自身の補正は未測定)。実: Muse run1のTier3 verifiedが人間未確認 | 同左(Secondary自動補正は**未測定**。T-1で確認) |
| 不要NG(確定正解なのにNG)件数 | 7/15音声(g2,g8,g11a2,g21,g23,g36,g7) | 5/15(g8,g7が救済) | Coffee: 合格相当の可能性が高い音声が5本中3本以上。全体の偽NG数は**未集計** | Coffeeの同3本は「Secondary=local併用」なら救済されうる(Azureのみは保証なし) |
| TTS再生成回数 | 20 group合計35 attempt(SCG前48) | 33 | 平均1.188/call。理論最大12(外側ループ)、Coffee 5 | 平均1.09〜1.23、最大3(固定) |
| HR率 | 標本1/20(5%)(SCG前5/20=25%)。運用母集団: 26/550=4.7% | 1/20 | 未合格6.9%(11/160) | 0.5%〜5.0%(Secondary救済率0.6〜0.0の感度) |
| 完成率 | 標本19/20=95%。運用母集団: 初回成功91.3%(502/550) | 19/20 | 93.1%(149/160) | 下限91.9%〜上限95.6% |
| コスト | Azure 21回約4.04円/20 group、回避した再生成約13回x約0.1円=約1.3円 -> **標本で純増約2〜3円** | Azure 24回約4.40円 | 1 segment平均約0.39円(Azureの未記録分は推定込み)。**Coffee part2単体は実費約14円(Azure 8.8円含む)** | Azure使用で約0.59〜0.69円(+50〜75%)、local併用なら約0.23〜0.25円。Azureは**本数と音声長で大きく変わる**(日本語短文は約0.16円/回、英語本文50秒は約2.2円/回) |
| 時間 | 再生成削減13回x120〜170秒=約26〜37分。Azure 1.4秒/回 | 約28〜40分 | 平均約143秒/segment。cool-down到達5%x600秒。Coffee 24分57秒 | 136〜148秒+Azure約3秒。理論最大: 約18分(cool-down廃止なら約8分) |
| Voice/Style一貫性 | 3回目でJ3->minimalに変化(minimal 19 attemptで合格7=36.8%、選択バイアスあり)。標本のminimal 4件は全て不合格 | **構造上ゼロの変化**(同一Prompt)。ただしinstruction leakage再発リスクは未測定 | 3回目でStyle/速度が変化([branch]は是正済み) | 構造上ゼロ(fingerprint assert)。"Model tried to generate text"型の再発率は未測定(過去のFlash-Lite期fallback利用は7/160=4.4%、うち合格2・不合格5) |

読み取り: (1)品質側は「Style/Voice一貫性」が目標案で最も確実に改善する(構造上)。(2)誤PASSは両言語とも**現在の標本では0**だが、濁点誤読・Secondaryの自動補正はどちらも**測定していない**ので、「増えない」とは言えない。(3)完成率・HR率は標本の偏りと確率モデルの仮定が大きく、**目標案で必ず改善するとは言えない**(英語下限は現行より1.2pt低い)。(4)コストはAzureの本数・音声長で決まり、英語本文でAzureを使うと現行より増える。

---

## 8. Trial結果(今回のオフライン検証)・未解決事項・追加Trial候補

### 8-1. 今回までに得られた結果(有料API 0円、本委任では新規の有料実測なし)
| 検証 | 結果 | 出典 |
|---|---|---|
| JA オフライン再計算(25音声、5ポリシー) | 誤PASS 0/5(全ポリシー)。不要NGは現行7/15、除外撤廃で5/15 | `JA_OFFLINE_COMPARISON_01.md`、`ja_offline_replay_01.json` |
| JA g8 実コード経路確認(Azureのみmock) | 現行NOT_APPLIED、C1の1条件を外すとPASS(Azure 1回) | `G8_GAS_KASU_INVESTIGATION_01.md` |
| EN Coffee Validator再現 | 記録済み分類を全て再現(Validator不具合・記録不整合は検出されず) | `FREE_VERIFICATION_01.md` 4-1 |
| EN 保存音声のローカルASR再転写 | 標準1・2回目・fallbackは2モデルとも原稿一致。LR音声のみ2/4系統が`robbing` | 同 4-2 |
| EN 合成変異テスト | 真の内容誤り16種で厳格PASS集合の誤PASS 0/16(Validator側のみ) | 同 4-7 |
| EN 過去記録の再計算 | 完了率 現行93.1% -> 目標案の下限91.9%〜上限95.6% | 同 4-3、`QCD_COMPARISON_01.md` |
| **今回追加**: Azure費用の再計算 | Azure 8回・231.83秒・約10.30円が未計上。累計約31.03円 | `COFFEE_AZURE_COST_ADDENDUM_01.md` |
| **今回追加**: commit内容のサイズ確認 | wavはcommitされていない(13章付録) | 本書13章 |
| **今回追加**: 参照関係のgrep | 目標フローで孤立/競合する箇所を特定(11章) | 本書11章 |

### 8-2. 未解決事項(未確定のもの)
1. **人間の聴取が必要**(ユーザー作業、費用0): (a)Coffee標準1回目の`showed/show`、(b)LR最終音声の`raw bean/robbing`。試聴ページ`user_test/coffee_new_tone_01/part2_review/`。(c)Phase 0の`needs_listen` 5音声(誤PASSの最終確定)`user_test/open258_phase0_listen_01/`(Phase 0当日HTTP 200確認、今回未再確認)。
2. **Secondary ASRが原稿へ「自動補正」するか**(濁点・数値・時制)は**両言語とも未測定**。g8の最終判断と、英語でSecondaryを呼ぶ範囲の両方に効く。
3. 減速後Primary転写、fallbackのAzure転写は**証跡が無く再構成不能**(再現には約0.07円/約1.9円の有料呼出が必要)。
4. 英語の偽NG(`US`/`U.S.`型)の全体件数は未集計。
5. 同一Promptの3回目の成功率、instruction leakage再発率は**直接比較データなし**(選択バイアス)。
6. Azureの契約tier(F0無料枠/S0)が不明で、実請求額は未確認。

7. **(委任_03で追加)** Secondaryを原稿なしで使った場合の「丸め」(原稿寄せ誤PASS)の実測が無い。最小対Trial(8-3)で測る。
8. **(委任_03で追加)** 6%減速後の転写・フォールバックのSecondary転写・Lock記録(LR分を数えない)は保存/計上されていない(証跡欠落)。案B'採用なら検証関数が一本化され解消する。

### 8-3. 追加Trial候補(**Opus要否判定で再編**、いずれも**未実行・未承認**。実行層は実施しない)
Opus判定(論点6): **必要**=日英統合「既知誤りの最小対Trial」約15〜20円。**必要(0円)**=needs_listen 5音声+Coffee `showed`/LR `raw bean`の試聴。**縮小実施**=T-1(v01 X-T1)をPhrase Listあり群削減で約40円。**不要**=日本語HR 26件の再計算(v01 J-T2)、E2E(v01 E-T2、実装前不可)。モデルの最新性は実行前にFableが確認(PM_GOVERNANCE 25節)。

#### 8-3-A. 【必要】日英統合「既知誤りの最小対Trial」(旧J-T1を統合・拡張) 約15〜20円
- **目的**: 「誤った原稿をTTSで合成し、ASRが原稿(正解形)寄りに丸めて誤PASSするか」を測る唯一の手段(ASR原稿寄せ誤PASSの測定)。g8の判断根拠(濁点)と、英語でSecondaryを呼ぶ範囲の両方に効く。
- **方法**: 各ペア(A=正しい形、B=最小対の誤った形)について、A・Bそれぞれをテキストとして**TTS合成**(両方向)。各クリップをPrimary(gpt-4o-mini-transcribe)/Azure(**Phrase Listなし**、原稿を与えない)/ローカルfaster-whisper mediumで転写し、**正解形Aを「原稿」としたときの判定ラベル**を記録。B音声がA原稿でPASS=誤PASS(原稿寄せ)、A音声がA原稿でNG=偽NG。
- **clip数**: 日本語20ペア x 2方向 = 40、英語20ペア x 2方向 = 40、**合計80クリップ**。
- **対象ペア一覧案**(案。実行前にFable/Opusが確認):
  - 日本語(20): 濁点/半濁点10(ガス/カス、ゴミ/コミ、バス/パス、ビル/ヒル、ダイ/タイ、ザイ/サイ、ドク/トク、ブン/プン、デンキ/テンキ、グン/クン)、長音・促音5(おじさん/おじいさん、ビル/ビール、さか/さっか、きて/きって、ゆき/ゆうき)、社外/社会型(同音・近似形態素)3(社外/社会、紹介/照会、以下/異化)、否定・数値の対照2(来なかった/来た、3つ/4つ。Secondaryを呼ばない条件の確認)。
  - 英語(20): -ed脱落5(showed/show、asked/ask、raised/raise、needed/need、looked/look)、-s 4(costs/cost、prices/price、beans/bean、days/day)、冠詞3(a price/the price、a cup/the cup、an hour/the hour)、母音最小対3(beans/bins、ship/sheep、raw/row)、US<->U.S.の偽NG対照1、**F-5複合**(「US data ... costs」<->「U.S. data ... cost」同時)1(M7)、数値・否定の対照2(nine/ten months、can/can't)、異音同綴語1(read/lead系、最終試聴が必要な型の確認)。
- **使用モデル**: TTS=`gemini-3.8-flash-lite-tts`(Coffee run_eで使用した最新世代。**最新**)。日本語Production標準が`gemini-3.1-flash-tts-preview`のままなら(JA側記載、未確認)、日本語40クリップのみ両モデルで測るか最新で測る(両方測る場合の追加約4円は別途承認)。ASR=Primary gpt-4o-mini-transcribe(Production固定)、Azure Speech STT(ja-JP/en-US、Phrase Listなし)、ローカルfaster-whisper medium(無料)。ASR評価のため最新LLM原則の対象外(英語側整理どおり)。ASRの最新性は未確認(実行前にFableが確認)。
- **費用内訳(見積。TTS単価は旧J-T1の約4円/40クリップ、Azure単価は約0.0444円/秒[$1/時間、1ドル160円]から外挿)**: TTS 80クリップ約8円 + Azure 約80クリップx平均2.3秒=約184秒で約8円 + Primary ASR約1円未満 + ローカル0円 = **約15〜20円(上限20円)**。Phrase Listあり群は含めない(T-1縮小に回す)。
- **成功条件の例(提案)**: 型ごとの原稿寄せ誤PASS率、偽NG率、local mediumが差分箇所で原稿を支持するか。結果で5-3のルール5・8、U-1・U-3・U-17・U-18を決める。

#### 8-3-B. 【必要・0円】試聴リスト(ユーザー作業、費用0)
試聴ページはいずれも2026-10-11に公開URLへのHTTP 200を確認(index.html、mp3)。
| 区分 | 内容 | URL |
|---|---|---|
| needs_listen 5音声(日本語、誤PASSの最終確定) | g11_kp5_ja_aoede_a1(理屈の上では/肉の上では)、g27_kp1_ja_charon_a1(吐き出す/履きます)、g18_meaning_2_a2・a3(拒絶された/強制された)、g1_meaning_4_a1(活動し続ける/活動をし続ける)。**ページ内の12本のうち上記5本を聴く** | https://shimomura055.github.io/eigo-radio/user_test/open258_phase0_listen_01/index.html |
| Coffee標準1回目(`showed`か`show`か) | `attempt1_standard.mp3` | https://shimomura055.github.io/eigo-radio/user_test/coffee_new_tone_01/part2_review/index.html |
| Coffee LR最終音声(`raw bean`か`robbing`か) | `attempt4_local_rewrite.mp3` | 同上 |
| (任意)Primary単独PASSのlocal medium無料サンプル監査(Opus推奨) | 標本設計は未着手。0円。見逃しの疑いを拾う参考指標(良品の32.5%をsmallがNG判定した事実から最終権威にはできない) | - |

#### 8-3-C. 【縮小実施】T-1(v01のX-T1: Secondary比較)約40円
- 内容: 保存済み英語wavをAzureで転写し、救済率・原稿寄りの自動補正・偽NG率を測る。**Phrase Listあり群を削減**し、Primary NG約20本+Primary PASS対照約10本=**約30本**をPhrase Listなし1パスのみ。
- 費用内訳(見積): 30本 x 平均30秒 = 約900秒 x 約0.0444円/秒 = **約40円**(旧案は60本・Phrase List有/無で約80円、上限120円)。ローカルmedium/smallは0円。Phrase Listあり代表(約5本)の比較は8-3-Aの英語クリップに吸収する案。
- モデル: Azure Speech STT en-US(現行Production)、faster-whisper medium/small(ローカル、ASR評価)。最新性: ASR評価のため最新LLM原則の対象外。
- 実施条件: 8-3-Aの結果でSecondary選択(U-8)の方針が見えてから、または並列で(対象音声・API・書込先が重ならないため並列可)。

#### 8-3-D. 【不要】と判定されたもの
| 項目 | 不要の理由(Opus判定) |
|---|---|
| 日本語HR 26件のSCG再計算(v01 J-T2、約3〜8円) | 新モードでSCG/UNCERTAIN経路自体が設計変更される(UNCERTAIN->HR廃止案、C1の扱い未決)ため、現行SCGの母集団救済率を測る価値が薄い。結論は最小対Trialと設計決定で出る |
| E2E(v01 E-T2、約10〜15円) | 新モードの実装が無いと実行できない。実装後に別途承認 |
| Z-T3(Primary単独PASSの事後監査)の有料実施 | 無料(ローカル)サンプル監査のみ推奨(8-3-B) |

推奨の順序(提案): 8-3-B(0円、ユーザー作業、先に) -> 8-3-A(約15〜20円、承認後) と 8-3-C(約40円、縮小)は並列可 -> 結果でユーザー判断(9章) -> 実装前に追加のOpus確認が必要ならそれ(内容が変われば再レビュー) -> 実装後E2E。**合計見込み: 約55〜60円**(v01比で約30〜70円減)。

---

## 9. ユーザー判断事項(最終版: 英語D-1〜D-11・日本語C区分・g8・Opus指摘を統合、重複排除。U-0〜U-19)

「推奨」は実行層の提案で、決定ではない。Production採用は人間ユーザーのみが承認する。**Opusレビュー反映**の項目は「[Opus]」と記す。QCD影響=品質(Q)/コスト(C)/時間(D)への影響(見込み。標本が小さい項目は推測を含む)。

| ID | 判断事項(元ID) | 選択肢 | 推奨と短い理由 | QCD影響 |
|---|---|---|---|---|
| U-0 | **目標共通フロー全体の扱い・適用範囲**(新規、全体) [Opus: M1] | (a)方向性を承認し、日英両方を対象に設計の細部をTrial/Opusで詰める (b)日本語先行 (c)英語先行 (d)見送り | **(a)、実装前に最小対Trial(8-3-A)**。日本語も目標型との差が残る(J3喪失・UNCERTAIN HR・fingerprint無し、0-2(i))。ただし段階導入(Full Story先行等)は可 | Q: Style一貫性が構造上改善。C: Azure追加で英語+50〜75%(見込み)。D: 再生成減で短縮 |
| U-1 | **g8/C1の扱い**(JA C1/X5、g8 13/14受入) [Opus: 論点1c/4] | 案1: 濁点のみのentity_likeはSCGを許す / 案2: 旧Cascadeと同じ扱い / 案3: 現行維持(g8は救済しない) / 案4: 最小対Trialで測ってから決める / 案5: 推定自体を廃止し辞書・Ledger判定へ(5-3の6、U-17と連動) | **案4 -> 結果が良ければ案5(または案1)**。C1は旧承認と「逆向き」ではない(0-2(iv)で訂正)が、粗いヒューリスティックで一般カタカナ語まで巻き込み、誤PASS防止の実績は0件 | Q: 誤PASS余地は最小対Trialで確認要。C: Azure+1回/件。D: 救済でHR/再生成減 |
| U-2 | **UNCERTAIN経路の統一**(JA X10、EN cascade 4段、D-11の一部)[Opus: M5] | (a)現行維持(HR直行、承認済み) (b)目標型(Secondary 1回->両NGなら再生成) (c)例外案C: **両ASRが同じ誤りで一致なら即HR**、それ以外は再生成 (d)混合: 表記差・濁点・entityのみはHR | **(c)を検討、最小対Trialの後に確定**。(b)(c)(d)は**承認済み仕様(2026-08-25 U、CS:1997/1998)の変更**であり、`stop_retrying`(Cascadeを尽くした印)の意味も再定義が必要。HR 8件は全て同一転写で再実行の効果が薄い | Q: 再生成しても直らない型を早くHRへ。C: ASR呼出4->2で減。D: 約1段短縮 |
| U-3 | **PHONETIC_MATCH / HIGH_SIMILARITY_SAFEをSecondary PASSに含めるか**(JA X9、EN D-3)[Opus] | (a)両言語とも厳格集合のみ (b)英語は`HIGH_SIMILARITY_SAFE`(単数/複数)を含める (c)日本語PHONETICもPrimaryと**対称に許容**(+3 group、誤PASS 0、Opus私見) | **(a)を暫定、最小対Trial後に(c)を再検討**。PASS判定は`should_pass`ではなく分類ラベルで行う(5-3の5)。許容するなら最小対型はPASS_WITH_WARNING(U-18) | Q: 許容で誤PASS余地(最小対型)。C: 不変。D: 救済増(+3 group/25標本) |
| U-4 | **minimal fallbackの廃止/隔離**(JA X11、EN D、ユーザー決定25/26の変更)[Opus: 論点3] | (a)通常のcontent retryから廃止、同一Prompt 3回 (b)現行維持 (c)Flash-Lite期の再発率を測ってから (d)**決定論的技術失敗(400 "Model tried to generate text"/指示文読み上げ)専用の隔離経路として残す**(`style_deviation=True`+最終試聴必須) | **(a)+(d)を検討**(救済影響は小さい: 英語160件中fallback合格2件、日本語19件中7件[選択バイアス])。隔離する場合は内容NGの救済には使わない | Q: Style一貫性が確実に改善。C: 微減。D: 不変。再発時は同Promptで3回失敗 |
| U-5 | **Local Rewriteの位置づけ**(EN D-6、JA OPEN-260)[Opus] | (a)通常retryから外し**HR後の人間手動オプション**に隔離 (b)完全撤去 (c)現行維持 | **(a)**。残す場合、spanの選択はNGを出したASR転写基準にする(OPEN-274)。LR再TTSが使うminimal fallback関数(L383)は独立させる(11章)。日本語対応(OPEN-260)は別 | Q: 本文書換えを通常経路から排除。C: LR分(LLM+TTS)を削減。D: 不変 |
| U-6 | **cool-down(600秒)**(EN D-5) | (a)廃止 (b)再生成(2)の前だけ維持 (c)現行(attempt3の前) | **(b)を暫定**(効果の対照データなし。廃止で約10分/segment短縮、決め手が無いので副産物で観測) | D: 廃止で約10分短縮。Q: 影響不明(対照なし) |
| U-7 | **6%減速後の検証**(EN D-4、OPEN-76の承認仕様)[Opus: M3] | (a)案B: attempt内に折込み (b)案C: 減速後は簡易チェックのみ、NGでも再生成しない (c)**案B'**: 生成->stretch->**最終音声に対してのみ**Primary->Secondaryを1系統で検証。減速前の検証は行わない | **(c)案B'**(案Bは偽NG倍増、案Cは最終音声未検証、B'はOPEN-76[減速後の音声を検証する承認仕様]に忠実で検証関数も一本化)。外側ループはL1692違反のため廃止(OPEN-270) | Q: 最終音声を確実に検証。C: ASR回数は減速前検証を省略で減。D: 外側ループ廃止で最大約18分->約8分(見込み) |
| U-8 | **Secondary ASRの選択・Phrase List・費用**(EN D-1/D-2/D-10)[Opus: M2] | (a)Azureのみ(**Phrase Listなし**、原稿を与えない) (b)Azure+ローカルmedium併用 (c)Phrase List有(現行英語) | **PASS判定用はPhrase Listなしが必須(構造的な独立性)。AzureかAzure+local併用かはTrial(8-3-A/C)で測定**。英語Azureは1回約2.2円、segment当たり約+0.2〜0.3円(見込み) | Q: 独立性向上。C: Azure追加分(14-2のとおり集計補正も必要)。D: 約+3秒/回 |
| U-9 | **Key Phraseを対象外とするか**(EN D-7) | (a)対象外(現行4回構成) (b)対象 | **(a)**(KP 96%が1回目合格、ユーザー決定済み=例外A) | 影響小 |
| U-10 | **技術失敗・ASR障害の扱い**(EN D-8、ユーザー要件)[Opus: M4] | (a)5xx/429/timeoutは**attempt外・上限付き**、無音・異常長はattempt消費 (b)全てattempt消費 (c)全てattempt外 | **(a)**(音声不良と区別。一時障害でattemptを失わない=OPEN-273) | Q: 影響なし。C: 微増。D: 微増(再試行待ち) |
| U-11 | **適用範囲・既存Tier3/CS層/entity cascadeとの統合**(EN D-9/D-11)[Opus: M1] | (a)5role・日英一斉 (b)Full Storyのみ先行 / 統合: Secondary転写を共有 | **(b)先行**(影響が最大のsegmentで実測)。Secondary転写の共有は二重呼出を避けるため推奨(11章) | C: 二重Azure呼出の回避で節約 |
| U-12 | **Secondary不呼出条件・類似度下限**(JA X3、EN TTS_FAILURE、X1)[Opus] | (a)現行維持(類似度<0.4でSecondaryなし) (b)**短文は下限を適用しない**(5-3の4、Opus案C) (c)漢数字・数詞語・言語ドリフト・英語短縮形を不呼出条件へ追加(X1: 日本語数値判定が`\d+`のみ) | **(c)は採用検討(安全側の追加)、(b)は最小対Trial後**(標本1件=g7「湿度->死図塔」のみ。新閾値は**未採用**) | Q: (c)で誤PASS防止強化。(b)は救済増+誤PASS余地。C: 不変 |
| U-13 | **新規仕様候補(未承認)**: 否定の活用ギャップ補強(JA「来なかった」)、辞書補強(OPEN-263)、英語の異音同綴語、Primary側`entity_like`のカナ率見直し | それぞれ採用/保留/不採用 | **保留**(根拠は合成のみ)。辞書補強はOPEN-263へ追記、英語の異音同綴語は最終試聴対象(U-18) | 影響小(保留) |
| U-14 | **Trialの実施可否と予算**(8-3)[Opus: 論点6] | 全実施(8-3-A+B+C) / 8-3-B+Aのみ / 見送り | **8-3-B(0円) -> 8-3-A(約15〜20円)とC(約40円、縮小)を並列**(合計約55〜60円) | C: 約55〜60円 |
| U-15 | **費用集計へのAzure計上**(別紙、14-2) | (a)集計関数にAzure(音声秒x単価)を追加 (b)報告で別枠明記のみ | **(a)**(Budget Guardも盲目のため。Production費用集計コードの変更はユーザー判断) | C: 報告の過少計上を是正 |
| U-16 | **wav等の大容量証跡の運用**(13章付録) | (a)現状維持 (b)wavはgit管理しない運用を明文化 (c)履歴書換え(禁止) | **(a)+(b)** | 影響なし |
| U-17 | **固有名詞のSecondary一致の扱い**(新規、M2)[Opus] | (a)Secondary一致でもentity/固有名詞は**再生成/HR**(辞書・Ledger判定でのみPASS) (b)Secondary一致なら**PASS_WITH_WARNING**で採用し最終試聴 (c)現行(英語=Secondary一致でPASS、日本語=C1除外)のまま | **(a)を基本、辞書・Ledgerで確定できる語のみPASS**。(b)は最小対Trial後。日英の非対称(0-2(iii))を解消する統一ルールが必要。推定ヒューリスティック(カタカナ比率・大文字)は廃止案(OPEN-272) | Q: 誤PASS防止。C: 再生成/HR微増。D: 微増 |
| U-18 | **最小対・形態素型差分の`PASS_WITH_WARNING`+最終試聴連動**(新規、M6)[Opus] | (a)採用: 該当差分は`PASS_WITH_WARNING`、最終試聴リストへ自動連動、(推奨)local mediumが差分箇所で原稿を支持することを追加条件 (b)現行(自動PASS) (c)該当差分は再生成 | **(a)**(リスク本体はASRのLM prior。完全防止は不可能なので人間の最終試聴で受ける)。最小対Trialで型ごとの危険度を測ってから条件を確定 | Q: 誤PASSを人間確認で捕捉。C: 試聴負荷増(件数は未測定)。D: 微増 |
| U-19 | **承認済み仕様違反・費用欠陥の即時対応**(新規、14章)[Opus: M3] | (a)OPEN-270(L1692違反)とOPEN-271(Azure費用不計上)を今回の統一設計とは**別に先に対処** (b)統一設計と同時に対処 (c)保留 | **(a)**(違反は設計決定を待たずに是正価値がある。ただしProduction変更=ユーザー判断) | Q/C: 再生成上限の遵守、費用の正確化 |

英語D番号との対応: D-1->U-8、D-2->U-8、D-3->U-3、D-4->U-7、D-5->U-6、D-6->U-5、D-7->U-9、D-8->U-10、D-9->U-11、D-10->U-8/U-14、D-11->U-11/U-2。日本語: C1/X5(g8)->U-1、X9->U-3、X10->U-2、X11->U-4、X3->U-12、X1->U-12、X8補強・X2補強->U-13。Opus挙げのユーザー判断(UNCERTAIN経路、minimal fallback廃止/隔離、日本語PHONETIC許容、固有名詞Secondary一致、6%減速案、Secondary選択/Azure費用、cool-down、g8、Trial実施)は上表U-2/U-4/U-3/U-17/U-7/U-8/U-6/U-1/U-14に1対1で対応(重複なし)。

---

## 10. 統一例外分類表(日英突合)

分類: **A**=必要(維持)、**B**=統一可能(共通フロー側へ寄せても品質低下の根拠が見当たらない)、**C**=要判断(根拠が割れる/実測不足/ユーザー決定済み仕様と衝突しうる)。「以前からある」「固有名詞だから」は根拠にしていない。

| ID | 例外/差分 | 日本語の現状(JA ID) | 英語の現状 | 根拠(実データ/承認) | 分類 |
|---|---|---|---|---|---|
| UX01 | 数字差でSecondary不実行 | X1 | `protected_check`(数字) | JA 2026-08-25 U。EN: Primary NGの31%が数字差、合成16種0誤PASS | **A** |
| UX02 | 否定差でSecondary不実行 | X2(+推奨4) | `protected_check`(否定) | JA 2026-08-25 U・2026-10-11 U。補強案は未承認 | **A**(補強はC) |
| UX03 | 類似度<0.4でSecondary不実行 | X3(g7が不救済) | `TTS_FAILURE`(0.4) | 誤PASS防止の実績なし、不救済が標本に1件 | **C** |
| UX04 | 長さ超過・Repetition/Disfluency QAで救済しない | X4 | あり | 費用最適化+幻覚検出。害なし | **A** |
| UX05 | entity_like(カナ/英字略語の置換)でSecondary不実行 | X5(C1) | entity-likeはcascadeへ(逆向き) | 誤PASS実績0、g8は救済機会喪失、旧承認と逆向き。真の固有名詞は発音の正否が全文一致で分からない | **B**(一般カタカナ語・濁点単独差)/ **A**(真の固有名詞)。分け方はC(U-1) |
| UX06 | 辞書読み不一致/CMU辞書による発音確認 | X6 | CMU ARPAbet一致のみ自動PASS | CS:1693 2026-08-28 U | **A** |
| UX07 | 原稿側diffにラテン文字でSecondary不実行 | X7 | 略語は表記ゆれ正規化が先 | 実測根拠なし(JA) | **A**(暫定。実発火頻度が未確認) |
| UX08 | 同形異音語/homophoneガード | X8(C2) | homophone-like判定 | JA 2026-10-11 U | **A**(辞書補強OPEN-263はC) |
| UX09 | Secondary PASSにPHONETIC/HIGH_SIMILARITY_SAFEを含めるか | X9(非許容、決定済み) | EN: `should_pass`は広い | JA: ユーザー決定の安全条件。+3 group・誤PASS 0 | **C** |
| UX10 | UNCERTAINは再生成せずHR(旧Cascade 4段) | X10 | cascade 4段 -> HR | 2026-08-25 U。同一転写の再実行は独立性が低い | **C** |
| UX11 | 3回目=minimal fallback(style喪失) | X11 | あり(A2、`main`)+force_secondary | ユーザー決定25/26。Flash-Lite期の再発率は未測定 | **C** |
| UX12 | force_secondary(fallbackでPrimary PASSでもAzure必須) | なし | あり | 暫定対策、根本原因未決(OPEN-66/67)。fallback廃止なら消滅。Azure偽NGが大半に見える | **B**(fallback廃止が採用された場合に限る) |
| UX13 | Local Rewrite(3回NG後の局所書換え) | なし(X12) | あり(5role) | 過去18記録中8回復、本文を書換え、Primary PASS型に無効、Gate7は日本語非対応 | **C**(HR後オプション化が推奨案。U-5) |
| UX14 | cool-down 600秒 | なし | あり | 効果の対照データなし | **C** |
| UX15 | 6%減速後Primary-only再検証+外側ループ | なし(減速は英語A2のみ) | あり | 「3回」の承認(CS:1692)と矛盾する副作用。減速自体は必要 | **B**(外側ループの是正、案B)/ 案CはC |
| UX16 | Phrase List(英語=有、日本語=無) | 無(誤PASS防止) | 有 | 誤PASSへの影響は未測定 | **C** |
| UX17 | role gating(英語=5role、日本語=無し) | 差なし | 5role限定 | 段階的拡張の履歴 | **C**(適用範囲、U-11) |
| UX18 | Azure取得のstrict化 | SCGのみstrict(X13) | 非strict | 実害報告なし | **B** |
| UX19 | HRキューの出力先が日英別 | X14 | 別パス | 運用上の別実装 | **B** |
| UX20 | 英語Key Phraseの4回構成 | KPは標準2+fb1 | 4回 | ユーザー決定、96%が1回目合格 | **A** |
| UX21 | 共有殻(num_*)再利用優先・OPEN-222 | 同様 | 同様 | 47 callの36%が未合格(TTS側の問題) | **A**(本テーマ外) |
| UX22 | 技術失敗/ASR障害の区別(新規) | 区別なし(ASR失敗の記録は限定的) | Primary転写Noneは音声不良扱い | ユーザー要件、設計案§3-9 | **A**(区別)/ 回数はC(U-10) |
| UX23 | 証跡の全保存(Primary/Secondary転写・attempt別) | SCG証跡はmanifestに記録、HRキューには入らない | fallback・減速後で欠落 | 今回の原因究明の最大の障害 | **B**(判定に影響しない) |

---

## 11. Dangling Reference Check(参照関係と、目標フロー採用時の孤立/競合)

方法: main作業ツリーのPythonファイルをgrep(テスト・Trial・runスクリプトを区別)。既存の`er053_dangling_reference_check_01.py`は**今回は実行していない**(実装が無いため、「定義だけで配線されない」型の検査は実装後に行う)。「呼出元」はProduction関連の主要箇所。ファイル数はテスト・Trial・旧一回限りスクリプトを含む。

| 対象 | 定義 | 主な参照元(行) | 目標フロー採用時の孤立/競合 |
|---|---|---|---|
| **旧Cascade**(英語) `evaluate_attempt_with_cascade`(35ファイル、テスト13) | `er006_secondary_asr_01.py` L342/L459 | `er003_v1_crosslevel_audio_02_common.py` L338、`er003_v1_repro01_main_generate.py` L338、`er003_v1_sing01_news_tail_fix.py` L202、`er003_v1_sing01_point_headings_aoede.py` L126、`er003_v1_sing01_voice01_generate.py` L238。静的監査`er006_audio_cost_spec_fix_01_static_audit.py` L50(呼出文字列を数える)、`er006_pool_benches_luna_audio_wiring_test.py` L47 | **競合**: `CASCADE_CONFIG`(Primary#2/Azure#2 各2回、CS:1997)を確認ゲートで置換すると、5呼出元のうち一部だけ置換した状態で2方式が混在しやすい(KP・見出し(`point_headings_aoede`)は対象外の案)。**孤立の恐れ**: 呼出文字列を数える静的監査・配線テストが、関数名/呼び方の変更で失敗する。CS:1997の「旧経路への後退禁止」との整合要 |
| **旧Cascade**(日本語) `evaluate_attempt_ja_with_cascade`(19ファイル、テスト10) | `er007_ja_secondary_asr_01.py` L370/L503 | `er003_v1_n3_01_tts_generate.py` L540、`er003_v1_repro01_main_generate.py` L363、`er003_v1_sing01_voice01_generate.py` L515/L563 | **競合**: UNCERTAINをSecondary 1回へ統一するとCS:1998(`CASCADE_CONFIG_JA`)と矛盾。Primary#2/Azure#2のAPI呼出が不要になる(費用減) |
| **SCG** `_scg_exclusion_reason`(5ファイル、テスト3) | `er007_ja_secondary_asr_01.py` L183-210 | 同ファイル L399-425、`er007_ja_scg_phase0_regression_test_01.py`(g8除外を固定する`test_g8_excluded_by_implementation_not_fixture` L239) | **競合**: U-1でC1を変更するとg8除外を固定する回帰テストが失敗する(意図した更新が必要)。SCG証跡はHRキューに入らない(日英のキュー統合時に要検討) |
| **er011 Human Review Lock** | `er011_human_review_lock_01.py`(`PRODUCTION_STANDARD_TTS_ATTEMPTS`=2、`MINIMAL`=1、`assert 2+1==3` L102-104) | 既定引数として`crosslevel` L82、`n3_tts` L476、`voice01` L436(**日英のfallback関数**)。`check_before_generation`/`record_outcome` L199/L255 | **競合**: 目標が「標準3+fallback 0」なら定数・既定引数・assertを日英で同時に変更する必要がある(英語だけ変えると日本語の既定が崩れる)。`RESOLVED`でも再実行をブロックしない特例(L242-252)は「6%減速retry」のためで、案Bで外側ループが無くなると**根拠が消える孤立した特例**になる。TTS計数がLR再TTS・外側ループを数えない(Coffeeで記録4/実際5) |
| **er021 English ASR Semantic Equivalence**(Tier1/3) | `er021_en_asr_semantic_equivalence_production_01.py` | import: `er006_preprod_hardening_01_validation.py` L49、`er006_secondary_asr_01.py` L161。telemetry: `er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl` | Tier1(数値等価)は`classify_asr_match`内でPrimary単独のため**無変更**。**競合**: Tier3とCS層は`evaluate_attempt_with_cascade_detail`内でAzureを別に呼ぶ。確認ゲートが別にAzureを呼ぶと**1音声に2回のAzure**(費用増)。設計案どおり転写を共有する改修が必要 |
| **6%減速後処理** `apply_a2_slowdown_postprocess`(12ファイル)、`generate_a2_segment_with_slowdown`(27ファイル、テスト5) | `er003_v1_n3_01_tts_generate.py` L117/L197 | 本流: 同ファイル L1048/L1065。**旧一回限りスクリプト**: `er008_n8_a2_resume_01.py`、`er008_n8_location_compression_24.py`、`er008_n8_wait_and_date_fix_retts_22.py`、`er008_pool_n4_audio_qa_sync_01.py`、`er009_pool_n5_a2_slowdown_01.py`、`er009_n1_a2_slowdown_apply_06.py` | **孤立/競合**: 関数の外側ループを廃止すると、旧スクリプトの挙動が変わる(再実行の予定が無ければ低リスクだが「定義だけ残る」)。`slowdown_attempts_log`・`{name}_original.wav`を読む側(`er003_v1_n3_01_assemble.py` L241等)のフィールド意味が変わる。減速後検証の転写が保存されない問題(F-2)も同時に解消すべき |
| **minimal fallback(英語A2)** `_run_a2_minimal_fallback_attempt` | `er003_v1_crosslevel_audio_02_common.py` L292 | 同 L181(標準2回後)、**L383(Local Rewrite再TTSが同じ関数を呼ぶ)** | **競合(重要)**: fallbackを廃止してもLRがこの関数を再利用しているため、**LR(HR後オプション案)の再TTSが壊れる**。LR用に同一Promptの再TTS関数を独立させる必要がある |
| **fallback style定数** `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`(13ファイル、テスト6) | `er033_tts_flash_lite_family_x_styles_01.py` L61 | `er003_v1_repro01_main_generate.py` L543(A2 fallback/KP minimal)、`er003_v1_sing01_point_headings_aoede.py` L97、`er003_v1_sing01_voice01_generate.py` L187、**`er006_audio_cost_pilot_02_shared_narration.py` L166(`welcome`共有殻の通常style)** | **競合**: 設計案の「到達不能にして定数は残す」は妥当だが、`welcome`共有殻は**通常styleとしてこの定数を使っている**(名前が「FALLBACK」でも通常経路)ので、定数・文言を変えると既存音声のキャッシュ整合(style_version)が崩れうる。名前と用途のズレは混乱の元 |
| **minimal fallback(日本語)** | `er003_v1_n3_01_tts_generate.py` L394/L400/L532、`er003_v1_sing01_voice01_generate.py` L395/L414 | `er011_final26_runtime_evidence_01.py` L78が文言を参照 | U-4で日本語も廃止するなら、定数2+1への依存(上のLock行)とセットで変更 |
| **Local Rewrite・cool-down** `run_local_rewrite_recovery`(9ファイル、テスト3)、`maybe_cooldown_before_attempt`(7ファイル、テスト3) | `er020_tts_retry_local_rewrite_01.py` L677 / L63 | LR: `crosslevel` L400、`news_tail_fix` L368、`voice01` L359。cool-down: `crosslevel` L177、`news_tail_fix` L143、`voice01` L149 | 呼出元の接続を外す(機構は残す)方針なら孤立ではなく**休眠機構**。ただしOPEN-256の全文性検証・OPEN-259(短文の誤拒否)等の保守対象が残る。HR後オプションにする場合は「人間の起動点」を新設する必要(未設計) |
| **HR queue** | `er006_secondary_asr_01.py _log_human_review`、`er011_human_review_lock_01.py` L429-452(重複排除) | 英語: `er006_output/audio_retry_cascade_prod_01/`、日本語: `er007_output/ja_asr_cascade_01/` | 重複排除キーにattempt番号/音声sha256を足す改修が必要(F-3)。日英統合は新規仕様 |
| **再利用判定** `_generate_or_reuse` | `er019_family_x_audio_production_runner_01.py` L405-432 | 再利用条件は`style_version`と`canonical_text`のみ | Prompt fingerprintを足すと旧キャッシュは再利用不可になる(既存音声の再生成が発生しうる)。`FAMILY_X_VARIABLE_ROLE_STYLE_VERSION`の更新とセット |

要約: **目標フロー採用時に最初に壊れるのは(1)LR再TTSの内部依存(L383)、(2)日英共有のTTS回数定数、(3)呼出文字列を数える静的監査/配線テスト、(4)g8除外を固定する回帰テスト**。`welcome`共有殻のstyle定数共用は見落としやすい。


### 11-2. 委任_03で追加したDangling発見とOpus指摘の統合(**Opusレビュー反映**)
上の表(v01)の発見に、Opusレビュー(条件A)の指摘と委任_03の照合を統合した一覧。目標フロー採用時の「孤立/競合/意図的失敗」を、対応方針案とともに示す(すべて提案)。

| # | 発見 | 内容 | 出典/確認度 | 対応案(提案) |
|---|---|---|---|---|
| D1 | **LR再TTSがminimal fallback関数に依存** | `crosslevel` L383 `_retts_fn`が`_run_a2_minimal_fallback_attempt`を呼ぶ。fallback廃止/隔離でLR再TTSが壊れる。LR再TTSも(main上では)Styleが変わる | コードで確認(v01 11章、0-2、4-7) | LR用に同一Prompt再TTS関数を独立させる(OPEN-274) |
| D2 | **`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`が`welcome`共有殻の通常styleとして使用** | `er006_audio_cost_pilot_02_shared_narration.py` L166。名前は「FALLBACK」でも通常経路。変更/削除でstyle_versionキャッシュ整合が崩れる | コードで確認(v01) | 「到達不能にする」だけで定数は残す。名称と用途のズレは別途整理 |
| D3 | **`ATTEMPTS`既定引数の日英共有** | `er011`の`PRODUCTION_STANDARD_TTS_ATTEMPTS`(2)/`MINIMAL`(1)、`assert 2+1==3`(L102-104)が`crosslevel` L82、`n3_tts` L476、`voice01` L436の既定引数。英語だけ変更すると日本語の既定が崩れる | コードで確認(v01) | 日英同時に変更(M1と整合: 日本語も新モード対象) |
| D4 | **静的監査/回帰テストが意図的に失敗する** | 呼出文字列を数える静的監査(`er006_audio_cost_spec_fix_01_static_audit.py` L50)、配線テスト(`er006_pool_benches_luna_audio_wiring_test.py` L47)、g8除外を固定する回帰テスト(`er007_ja_scg_phase0_regression_test_01.py` L239) | v01の表 | 意図した仕様変更として更新(テストを緩めない)。実装時に「定義だけ残る」型を`er053_dangling_reference_check_01.py`で検査 |
| D5 | **Review Lockの特例が根拠を失う** | `RESOLVED`でも再実行をブロックしない特例(`er011` L242-252)は6%減速retry用。外側ループ廃止で孤立。TTS計数もLR再TTS・外側ループを数えない(Coffeeで記録4/実際5) | コードとattempt_historyで確認 | 案B'で特例を撤去。計数にLR再TTSを含めるか判断 |
| D6 | **Tier3/CS層のAzure重複呼出** | Tier3とCS層は`evaluate_attempt_with_cascade_detail`内でAzureを別に呼ぶ。新ゲートが別にAzureを呼ぶと1音声に2回のAzure(費用増) | v01 | Secondary転写を共有する改修(U-11) |
| D7 | **旧Cascadeが残る経路(Opus指摘)** | 旧Cascade(`evaluate_attempt_with_cascade`/`_ja_`)は5〜6呼出元から直接呼ばれ、Key Phraseの非ラテン経路(`er003_v1_repro01_main_generate.py`の`non_latin_cascade`)からも到達しうる。新モードで一部だけ置換すると2方式が混在する | Opus指摘+コードにnon_latin_cascade引数の存在を確認(個別の到達経路追跡は未実施、推測を含む) | 旧Cascadeを呼ぶ全呼出元を列挙し、KP(例外A)・見出し(`point_headings_aoede`)の扱いを先に決める |
| D8 | **SCGは新ゲートへ吸収(Opus)** | 日本語SCG(`_scg_exclusion_reason`等)は新しいSecondary確認ゲートへ吸収される。C1の扱い(U-1/U-17)とg8回帰テストを同時更新 | Opus指摘 | SCGを共通ゲートの日本語実装として統合 |
| D9 | **er011 HRL重複排除キーの変更が日英queueに影響** | `er011_human_review_lock_01.py` L429-452の重複排除キー(同一音声+同一原稿)にattempt番号/音声sha256を足すと、日英のHR queue(`er006_output/audio_retry_cascade_prod_01/`、`er007_output/ja_asr_cascade_01/`)の挙動が変わる | v01+Opus | queue統合は新規仕様。キー変更と一緒に設計 |
| D10 | **er021 Tier1がSecondary転写にも適用(Opus)** | Tier1(数値等価)は`classify_asr_match`内で動くため、Secondary転写にも適用される。PASSをshould_passで判定するとTier1等価PASSが混ざる -> **ラベル判定が必須**(5-3の5) | Opus指摘 | PASS集合を厳格ラベルで固定 |
| D11 | **6%減速はB'で検証関数一本化** | 現行は減速後Primary+homophoneのみの別経路(cascade/Tier3/CS層なし)。案B'なら最終音声の検証が通常経路と同一関数になる | コードで確認(L184-193、L208-210) | 案B'(U-7) |
| D12 | **旧一回限りスクリプトの孤立** | `er008_n8_a2_resume_01.py`等6本が`generate_a2_segment_with_slowdown`を使う(v01) | v01 | 再実行予定がなければ低リスク。「定義だけ残る」を許容か整理か判断 |

要約(11-2): 実装時に最初に壊れる/見落としやすいのは、**D1(LR再TTS)**、**D3(日英共有の定数)**、**D4(意図的な静的監査/回帰テスト失敗)**、**D2(welcome共有殻)**、**D6(Azure重複呼出)**。いずれもOpus追加レビュー対象になりうる(新しい処理フローの具体設計時)。

---

## 12. 承認済み未配線・未解決USER_DECISION_REQUIRED・未報告Trialの一覧(本テーマに関係するもの)

| 区分 | 項目 | 状態 | 根拠 |
|---|---|---|---|
| 承認済み・未配線 | J2_BRIGHT / E2_UPBEAT(Tone Trial) | `main`未配線。Coffeeは`feature/coffee-new-tone-01` branchで実装・実run済み(未merge)。fallbackでのStyle維持も同branchのみ | `docs/pm/design/..._X_INVENTORY_01.md` L85、`RUNTIME_EVIDENCE_01.md` |
| 承認済み・配線待ち | EN ASR Semantic Equivalence Layer(Tier1/3) | `APPROVED_FOR_PRODUCTION`(2026-09-27)、CS:2000は`PRODUCTION_WIRED`をPhase B live telemetry取得後と記載 | CS:2000 |
| 配線済みだが一部ユーザー最終確認待ち | OPEN-258 SCG(PRODUCTION_WIRED 2026-10-11) | C1(entity_like/辞書読み/ラテン)の個別承認なし。g8 13/14受入の最終確認が`USER_DECISION_REQUIRED` | OI:760、DL:20550 |
| 未解決(未承認・OPEN候補) | OPEN-257 音韻衝突型固有名詞(Muse) | 包括対策は2026-10-11に保留。人間聴取は未確認 | OI:759 |
| 未解決(未承認) | OPEN-259 Local Rewriteの短文長さ比(誤拒否の緩和方向) | 緩和方向のため要ユーザー判断。顕在化していない | OI:761 |
| 未解決(未承認) | OPEN-260 Local Rewriteの日本語対応(Gate7 ASCII語数) | OPEN-258/本件の結論次第 | OI:762 |
| 未解決(未承認) | OPEN-263 SCG同形異音語ガードの辞書欠落(「行った」等) | 実装なし | OI:766 |
| 未解決(未承認・未起票) | 英語側が起票候補とした6件(英語Primary TCMにSecondary無し、減速外側ループのTTS上限破り、費用集計のAzure未計上、fallbackのcascade_steps/Azure転写未保存とqueue重複排除、`US`/`U.S.`表記偽NG、LRのNG span誤り) | SSOT未登録(英語側は登録を後続委任とした) | `QCD_COMPARISON_01.md` (10) |
| 未解決(未承認・未起票) | 日本語側が気付いた新規仕様候補3件(否定活用ギャップ、C1のentity判定の範囲、Primary側カナ率ヒューリスティック) | SSOT未登録 | `JA_EXCEPTION_CLASSIFICATION_DRAFT_01.md` |
| 未起票(今回新規) | Coffee費用のAzure未計上と、同型の集計関数が11ファイルにある件 | 別紙参照。未起票 | `COFFEE_AZURE_COST_ADDENDUM_01.md` |
| 未報告/未実施のTrial・確認 | Phase 0 `needs_listen` 5音声の試聴、Coffee標準1回目・LR音声の人間聴取 | ユーザー作業、未実施 | 8-2 |
| 未実施の追加Trial(**v02で再編**) | 最小対Trial(旧J-T1を日英統合、必要)、T-1縮小(旧X-T1)、試聴(0円)。旧J-T2・E-T2は不要/実装後(8-3-D)。すべて承認待ち | 費用は8-3 | 8-3 |
| Gate | 目標フローは新しい構造・処理フロー(Gate条件A) | **Opus独立レビュー必須**。並行レビュー中。レビュー後もProduction採用は人間ユーザーのみ | CLAUDE.md、`docs/pm/PM_GOVERNANCE.md` 11-3節 |
| 運用上の注意 | Coffee Standard `full_story_part2`はHUMAN_REVIEW_REQUIRED(承認はユーザーのみ)。Coffeeのworktree branchは`main`未merge | 本書では変更しない | RUNTIME_EVIDENCE_01 |


**委任_03での状態更新**: 上表の「未解決(未承認・未起票)」の英語側6件・日本語側3件・今回新規のAzure費用不計上は、**委任_03でOPEN-270〜275として起票済み**(14章、OPEN_ITEMSに「OPEN候補・未承認、ユーザー判断待ち・未実装」と明記)。OPEN-263(同形異音語)には辞書補強候補を、OPEN-257/258関連には本IDの参照を追記した。起票は記録であり、実装・Production変更ではない。

---

## 13. 使用モデル・作成物一覧・付録

### 13-1. 使用モデル
本委任(委任_03)は**有料API未使用**(OpenAI/Azure/Gemini/LLM呼出0回、費用0円)。実行層=Sonnet 5.5(Claude Code)。ローカルで実行したもの: grep、コード行の読取、attempt履歴JSONの読取、公開URLのHTTP 200確認(curl、無料)。Opus独立レビュー(条件A)は2026-10-11に完了し、指摘をFableが転記したものを反映した(原文はFable保持)。評価用モデルの最新性: 今回はモデル選定を伴う検証なしで該当なし。8-3の追加Trial案はモデル名・最新性を併記した(TTS=gemini-3.8-flash-lite-tts[最新]、ASR=gpt-4o-mini-transcribe+Azure+local whisper medium[ASR評価のため最新LLM原則の対象外、最新性は実行前にFableが確認])。

### 13-2. 作成物(委任_02はread-only調査。委任_03はSSOT[DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER]のみ追記、Production・CURRENT_SPEC・Coffee worktree無変更)
- `er056_output/asr_tts_cross_language_reconciliation_01/RECONCILIATION_REPORT_01.md`(本書)
- `er056_output/asr_tts_cross_language_reconciliation_01/COFFEE_AZURE_COST_ADDENDUM_01.md`
- `docs/pm/delegation_log/2026-10-11_ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01_02.md`
- **(委任_03で追加)** `er056_output/asr_tts_cross_language_reconciliation_01/RECONCILIATION_REPORT_02.md`(本書、v01は残置)、`docs/pm/delegation_log/2026-10-11_ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01_03.md`、DECISION_LOG/OPEN_ITEMS(OPEN-270〜275)/REPORT_LEDGER追記
- `docs/pm/ACTIVE_TASK_ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01.md`(更新)

### 13-3. 付録: 英語側commitの容量確認(wav 16MB問題)
**結論(確定): wavはmainにcommitされていない。** 指摘の「16MB」は、ローカルの`evidence_snapshot/`ディレクトリ全体(15,410,411バイト≒15.4MB)の大きさに近い。

| 区分 | 件数 | 容量 | 内容 |
|---|---|---|---|
| commit 7ef4eed2に含まれる全ファイル | 37 | **約1.55MB**(1,546,939バイト) | テキスト/JSON/ログ/スクリプトのみ。最大: `evidence_snapshot/ssot_logs/worktree_human_review_queue.jsonl` 307KB、`b1b_audit/tts_generation_results.json` 249KB、`replay_results_01.json` 246KB、`a2_audit/tts_generation_results.json` 105KB |
| `er056_output/en_asr_confirm_retry_redesign_01/`配下のgit管理 | 34 | 1,506,700バイト | 上記のうち |
| **git管理外**(`.gitignore` L11 `*.wav`で除外) | wav 6本 | 14,341,704バイト(約14.3MB) | `evidence_snapshot/a2_attempts/full_story_part2_attempt1〜4(2,415,404/2,355,404/2,340,044/2,290,604)`、`a2_final/full_story_part2.wav`(2,524,844)、`a2_final/full_story_part2_original.wav`(2,415,404、attempt1と同じsha256)。ローカルディスクのみに存在 |

- 影響: `MANIFEST.sha256`(commit済み)は6本のwavのsha256を記録している。**wav本体はこのPCのローカルにしか無い**(Coffee worktree側の原本もgit管理外)ため、別の環境では再検証できない(推測: 英語側が試聴用音声だけ別途公開していない場合)。
- 別件(英語側ではなくCoffee側): 公開試聴ページ用に`user_test/coffee_new_tone_01/`へ**mp3**がcommit済み(commit f8e63c8b: 36ファイル約8.77MB、c93c10ea: 12ファイル約4.00MB、合計約12.8MB)。これはGitHub Pages公開のための仕様どおりの追加で、英語側の証跡とは別。
- `.git`全体は約765MB(pack 741MiB)。今回の増分は小さい。
- 今後の方針候補(**提案のみ、何もしない**): (a)現状維持(wavは既に除外、証跡はJSON+sha256で十分と見なす) (b)「大きな音声はgit管理しない、必要ならsha256+保管場所の記録のみを残す」を運用として明文化(推奨) (c)履歴書換え(**禁止、必要なし**)。

### 13-4. 付録: 英語側と日本語側の発見事項の対応(重複排除用)
| 英語側(F-番号) | 日本語側に該当するもの | 統合先 |
|---|---|---|
| F-1 減速外側ループがTTS上限3を破る | なし(日本語に減速なし) | 5-2、U-7 |
| F-3 fallbackのcascade_steps/Azure転写未保存、queue重複排除 | SCG証跡がHRキューに入らない | 5-1の7、UX23 |
| F-4 LRのNG spanがPrimary転写基準 | なし | U-5 |
| F-5 `US`/`U.S.`の表記偽NG | 日本語のkakasi読み限界(頃/ころ) | 4-2、UX05 |
| F-6 Azureの誤認識(`raw bean`等)でforced確認が偽NGを生む | g8でAzureは正しい、g23は同一誤聴(Muse型) | UX12、U-8 |
| F-7 費用にAzure未計上 | SCGは`est_cost_jpy`を自前で記録するが集計に入らない | 別紙、U-15 |

---

## 14. 承認済み仕様違反・費用計上欠陥(即時対応候補、委任_03で新設)

Opusレビュー(M3、論点1・5)で明確になった、**統一設計の決定を待たずに対処価値がある**2件。いずれもProduction変更を伴うため、実行層は対処せず**ユーザー判断待ち**(U-19)。

### 14-1. 承認済み仕様違反: 6%減速の外側ループがTTS総3回を破る(OPEN-270)
- **仕様**(CS:1692、2026-09-04ユーザー正式決定): 同一segmentのTTS総試行回数は**3回**(標準2+fallback1)、「**4回目以降は絶対にTTS生成しない**」。
- **実装**: `er003_v1_n3_01_tts_generate.py` L248-262の外側ループ(`max_slowdown_attempts`既定3)が、減速後検証がNGのたびに`generate_english_segment_with_fallback`を**新しい予算で**呼び直す。結果、理論最大は3周x3回(LRを含めるとさらに増える)。
- **実害(runtime evidence)**: Coffee Standard `full_story_part2`で**TTS 5回**(初回1+2周目3+LR再TTS1)。`attempt_history_coffee_run_e.jsonl`(15:13 1回、15:35 3回、累計4)+LR1回、`full_story_part2_attempt1〜4`のwavが4本。Lockの記録(4)はLR再TTSを数えず、記録上も上限を超えていることが見えにくい。
- **副作用**: 減速後検証はPrimary+homophoneのみで、cascade/Tier3/CS層が未配線(通常経路より厳しい別経路)。初回合格の音声を捨てた(4-1)。減速後の転写は上書きで保存されない。
- **是正案(提案、未実装)**: 案B'(生成->stretch->最終音声のみ検証、外側ループ廃止、U-7)。OPEN-76の「減速後の音声を検証する」承認仕様に忠実。
- **注意**: 本件は上限回数という既存の安全装置(Review Lock/CS:1692)への違反であり、実行層は独自判断で回避・無効化していない。是正はProduction変更なのでユーザー判断。

### 14-2. 費用計上欠陥: Azure Secondary費用が集計に入っていない(OPEN-271、OPEN-275)
- **確定**: Coffee Phase 2の累計 JPY 20.73 には、Azure STT 8回(231.83秒)の**約10.30円(上限側10.44円)が1円も入っていない**。補正後は**約31.03円/50円**(62.1%、上限側31.17円)。Phase 2の累計費用の補正反映が必要(OPEN-275)。
- **根拠**: `COFFEE_AZURE_COST_ADDENDUM_01.md`(worktreeの`raw_usage_log.jsonl`でAzure 8行、`compute_cost_jpy_so_far`を実行して`azure=0.0`を確認、単価=pricing_snapshotのAzure $1/音声時間、USD/JPY=160)。
- **同型の集計コードが`main`の11ファイルにある**(`provider in ("gemini","openai","openai_asr")`のパターン。例: `er012_b_family_production_runner_01.py`、`er012_e_family_entertainment_two_level_runner_01.py`、`er019_family_x_audio_production_runner_01.py` ほか。ファイル一覧は別紙4節/OPEN-271)。過去の費用報告(英語のcascade/forced Secondary、日本語SCGが走ったrun)にも過少計上がある可能性が高い(未集計、推測)。
- **Budget Guardの盲点**: 予算上限の自動停止(Budget Guard)もAzureを数えないため、Azure呼出が多いrunでは実費が上限を超えても止まらない構造。英語の長い本文(約50秒)でAzureを呼ぶ設計は1回約2.2円で、日本語SCG(数秒の短文、約0.16円/回)の約10倍。Azure 8.79円 > TTS 3.02+OpenAI ASR 1.77+LLM 0.37(Coffee part2)。
- **未確認(推測)**: Azureの契約tier。F0(無料枠5時間/月)なら実費は0円になりうる。S0なら補正後の費用が実費に近い。**契約tierは本調査で未確認**。
- **是正案(提案、未実装)**: (a)集計関数にAzure(音声秒x単価)を加える、(b)報告で「Azure別枠」と明記。Production費用集計コードの変更に当たるため、ユーザー判断(U-15、U-19)。
