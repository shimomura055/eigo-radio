# RECONCILIATION_REPORT_01 日英統合報告書(ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_02、2026-10-11)

Status: **USER_DECISION_REQUIRED候補**(提案のみ。Opus独立レビューが並行中。Production・SSOT無変更、有料API 0円)。
「目標共通フロー」(初回 -> Primary NG -> Secondary -> 両NG -> 再生成(1) -> (2) -> Human Review、TTS最大3回、再生成は同一Prompt、minimal fallback/Local Rewriteは通常retry外、技術失敗/ASR障害は区別)は**ユーザー要件に基づく目標案であり、未採用**。本書の「統一推奨」「維持すべき例外」はすべて**提案**で、新しい例外仕様・閾値は何も採用していない。

用語メモ(エンジニアでない方向け):
- **Primary ASR** = 最初の音声認識(OpenAI gpt-4o-mini-transcribe)。**Secondary ASR** = 別会社の2つ目の音声認識(Azure Speech)。「ASR」は音声を文字にする機械。
- **TTS** = 文字を音声にする機械(Gemini TTS)。**再生成** = TTSをやり直して音声を作り直すこと。
- **Validator** = 音声認識の文字と原稿を比べて合否を決める判定器。**TCM**(TRUE_CONTENT_MISMATCH)=「内容が違う」判定。**UNCERTAIN**=「固有名詞等でASRの誤認識か判別できない」判定。
- **SCG** = 日本語のSecondary Confirm Gate(Primary NGの時に再生成の前にAzureで1回確認する仕組み、2026-10-11採用)。**旧Cascade** = Primary#2 -> Azure#1 -> Azure#2 の4段確認(UNCERTAIN時のみ)。
- **Human Review(HR)** = 人間が聞いて判断する待ち行列。**Local Rewrite(LR)** = 3回失敗後に問題箇所だけ文章を書き換えて再TTSする英語専用の救済。
- 根拠の略記: CS=`CURRENT_SPEC.md`の行、DL=`DECISION_LOG.md`の行(`[履歴]`見出し行は見出しのみ、本文は`DECISION_LOG_HISTORY.md`)、OI=`OPEN_ITEMS.md`の行。「確定」=コード・ログ・SSOT行で確認、「推測」=確認できていない解釈。
- 入力: 英語側 `er056_output/en_asr_confirm_retry_redesign_01/*`(委任_01、commit 7ef4eed2)、日本語側 `er056_output/asr_tts_cross_language_reconciliation_01/*`(委任_01、commit 6468a21e)。今回は新しい有料実測なし。追加で実施したread-only確認: コード行・SSOT行の照合、Azure費用の再計算(別紙)、参照関係のgrep、commit内容のサイズ確認。

## 要点(先に・PM向け)
1. **日英の差の大半は「必要な違い」ではなく、導入時期の違いによる継ぎ足し**(2章)。言語そのものが要求する違いは、判定器の中身(日本語=読み/漢字、英語=発音辞書/表記ゆれ)と、英語A2の6%減速だけ。
2. **Coffee Standard `full_story_part2` のNGは、「音声が壊れていた」と確認できたものは0件**。主因は(a)合格済み音声を減速後の簡易チェックで捨てる設計、(b)`US`と`U.S.`等の表記差の偽NG、(c)Azureの聞き間違い、(d)Local Rewriteが無関係な箇所を書き換えた、の組み合わせ(4章)。標準1回目とLR後の音声だけは**人間が聞くまで未確定**。
3. **g8「ガス->カス」は誤PASS防止の実績ではなく、救済機会を失った副作用**。Primary NGの直接原因は別の語「熟->じく」、SCG除外はカタカナ率の粗いヒューリスティックが原因(3章)。
4. **Coffeeの費用は少なくとも約10.3円過少報告**。Azure STT 8回(231.8秒)が累計20.73円に入っていない。補正後は約31.03円/50円(別紙 `COFFEE_AZURE_COST_ADDENDUM_01.md`)。
5. **「英語側がwavを16MB commitした」という前提は事実と異なる**(wavは`.gitignore`の`*.wav`で除外済み。commitされたのは約1.5MBのテキスト/JSONのみ。13章の付録参照)。
6. 目標フローはおおむね実現可能だが、**日本語の「UNCERTAIN -> HR直行」と英語のcascade 4段を目標型へ寄せる部分、minimal fallback廃止、6%減速、Local Rewrite、cool-downは承認済み仕様の変更**であり、ユーザー判断(9章)とOpus独立レビュー(新構造のため必須)が前提。
7. 参照整合の発見(11章): 目標フローでminimal fallbackを廃止すると、**Local Rewriteの再TTSがfallback関数を内部で再利用している**ため(`er003_v1_crosslevel_audio_02_common.py` L383)連動して壊れる。また`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`は`welcome`共有殻の通常styleとしても使われており(`er006_audio_cost_pilot_02_shared_narration.py` L166)、「到達不能にする」だけでは済まない。

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
- 承認根拠(確定): C1(entity_like/辞書読み/ラテン除外)はOpus必須1をFableが採用したもので、**ユーザーがg8を13/14のまま受け入れるという逐語決定は無い**(DL:20550は最終確認待ち)。旧承認(CS:1998)は「entity-like差分が検出されたらSecondaryへ送る」で、C1とは**向きが逆**。
- 実装上の問題(確定): `entity_like`は意味上の固有名詞判定ではなく「カタカナ率のヒューリスティック」。一般語「ガス」も1文字の濁点差も巻き込む一方、挿入/脱落(メタ->メタン)は取りこぼす(合成確認)。

### 推測(確認できていない)
- g8の音声は「ガス」と正しく発音され、Primaryの誤認識だった可能性が高い(3系統が「ガス」)。ground truthは**試聴のみ**で、人間の確認は未実施。
- 「音声が実際に『カス』だった場合にAzureが『ガス』へ丸めて誤PASSするか」は、**濁点誤りを含む実標本が0件のため未測定**。社外->社会の例(旧Cascade queue、Primary/Azure 4回とも「社会」)は、高頻度語へのASR偏りが起きうることを示す(TTSが「しゃがい」と言ったかは不明)。
- C1が守ろうとした本質(名前・社名・外来語など、全文一致では発音の正否を判断できない語)は妥当だが、g8のような一般カタカナ語・濁点単独差まで除外する根拠は薄い(評価: 一般カタカナ語は**B(統一可能)**、真の固有名詞は**A**。最終は9章U-1)。

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
| 6%減速後の「3回超過」の是正 | 推奨(案B) | 3回上限(CS:1692)と実装が矛盾(Coffee: TTS 5回、理論最大12)。案Bは仕様変更を伴わず、attempt内に折り込む |
| 証跡の保存漏れの解消(減速後転写、fallback cascade_steps、HRキュー重複排除) | 推奨 | 今回の原因究明で証跡欠落が最大の障害だった。判定には影響しない |
| HRキューの統合、Azure取得関数のstrict統一(X13/X14) | 推奨(低優先) | 運用上の見落としと、途中キャンセル時の誤判定リスクの解消。実害の報告は無い |
| Secondary PASSは「厳格集合」で日英共通 | 推奨だが論点あり(U-3) | 日本語はユーザー決定済み。英語のHIGH_SIMILARITY_SAFE(単数/複数)を含めるかは別判断 |

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

### 8-3. 追加Trial候補(いずれも**未実行・未承認**。実行層は実施しない)
目的別に、日英で重複する測定を統合した案。モデル名と最新性は実行前にFableが確認(PM_GOVERNANCE 25節)。

| ID | 対象・内容 | 規模 | 費用(見積) | 使用モデル | 最新か/例外理由 |
|---|---|---|---|---|---|
| X-T1(統合案) | **Secondary比較**: 保存済みの英語wav 約60本(Primary NG約20+Primary PASS対照約40、既にローカルに存在)をAzure(Phrase List有/無)とローカルfaster-whisper mediumで転写し、救済率・原稿寄りの自動補正・偽NG率を比較 | 約60本x平均30秒 | **約80円(上限120円)**(Azureのみ有料) | Azure Speech STT(en-US)=現行Production、faster-whisper medium/small(ローカル、ASR評価でありLLM/TTSではない) | ASR評価のため最新LLM原則の対象外(英語側の整理どおり) |
| J-T1 | **濁点最小対**: ガス/カス、ゴミ/コミ等20対x2方向=40クリップをTTS合成し、Azure/Primaryの濁点感度と「Azureが原稿語へ丸めて誤PASSするか」を測定(g8判断の根拠) | 40クリップ | **約9〜10円**(TTS約4+Azure約3.6+Primary 1未満) | TTS=現行Production標準(`gemini-3.1-flash-tts-preview`、JA側記載)。ASR=gpt-4o-mini-transcribe+Azure ja-JP | **最新性は未確認**。例外理由案=「測定対象がProduction経路そのもの」。ただしCoffeeの実runは`gemini-3.8-flash-lite-tts`(最新)を使っており、JAのProduction標準がどちらか実行前に確認し、可能なら両方で測るか最新を使う |
| J-T2 | **HR実segmentへのSCG再計算**: Human Reviewに回った日本語26件の保存音声にAzure 1回ずつ(母集団でのSCG救済率) | 保存音声のある分 | 約3〜8円 | Azure Speech STT ja-JP(ASRのみ) | ASR評価のため対象外 |
| E-T2 | **英語E2E**: 新モード実装後にCoffee part2相当+別3 segmentを実run | 4 segment | 約10〜15円(上限30円) | TTS=`gemini-3.8-flash-lite-tts`(最新、RUNTIME_EVIDENCE記載)、LLM=`gpt-6-luna`(最新)、ASR=gpt-4o-mini-transcribe+Azure | **実装後**に別途承認(実装前は不可) |
| Z-T3 | **Primary単独PASSの事後監査**: Primary PASSの標本をローカルmediumで再転写し、見逃し(誤PASS)の疑いを拾う。**新規提案(Cに分類)** | 標本数は要設計 | 0円(ローカル) | faster-whisper medium | ASR評価のため対象外。ただし良品の32.5%をsmallがNG判定した事実から、**最終権威にはできない**(参考指標) |
| H-T4 | **人間聴取**: 8-2の(a)(b)(c)。ユーザー作業 | 約8音声 | 0円 | - | - |

推奨の順序(提案): H-T4(0円、誰でも先にできる) -> J-T2(安価、既存データ) -> X-T1とJ-T1 -> Opus独立レビュー(新構造のため必須。実装前) -> E-T2。X-T1/J-T1は互いに独立で並列実行できる(並列化の理由: 対象音声・API・書込先が重ならない)。

---

## 9. ユーザー判断事項(英語D-1〜D-11と日本語C区分・g8を統合、重複排除)

「推奨」は実行層の提案で、決定ではない。Production採用は人間ユーザーのみが承認する。

| ID | 判断事項(元ID) | 選択肢 | 推奨と短い理由 |
|---|---|---|---|
| U-0 | **目標共通フロー全体の扱い**(新規、全体) | (a)方向性を承認し設計の細部をOpus/Trialで詰める (b)日本語先行 (c)英語先行 (d)今回は見送り | **(a)、実装前にOpus独立レビュー+X-T1/J-T1**。日本語は既に目標型に近く、英語は構造変更が大きいので、日英同時の本番変更より段階的に |
| U-1 | **g8/C1の扱い**(JA C1/X5、g8 13/14受入) | 案1: 濁点のみのentity_likeはSCGを許す / 案2: 旧Cascadeと同じ扱いに統一 / 案3: 現行維持(g8は救済しない) / 案4: J-T1で測ってから決める | **案4 -> 結果が良ければ案1**。C1は旧承認(CS:1998)と向きが逆で、誤PASSを防いだ実績が無く(0件)、一般カタカナ語まで巻き込む。真の固有名詞は残す |
| U-2 | **UNCERTAIN経路の統一**(JA X10、EN cascade 4段、D-11の一部) | (a)現行維持(HR直行、承認済み) (b)目標型(Secondary 1回 -> 両NGなら再生成) (c)混合: 両NGでも「ASR側の偽NGと見られる種別(表記差・濁点・entityのみ)」は再生成せずHR | **(c)を検討、まず実測**(再生成しても解決しない種別があるため。HR 8件は全て同一転写、Coffee標準2回目も同型)。承認済み仕様(2026-08-25 U)の変更になる |
| U-3 | **PHONETIC_MATCH / HIGH_SIMILARITY_SAFEをSecondary PASSに含めるか**(JA X9、EN D-3) | (a)両言語とも厳格集合のみ (b)英語は`HIGH_SIMILARITY_SAFE`(単数/複数)を含める (c)日本語もPHONETICを許す | **(a)**(JAのPHONETIC許容は+3 groupだが決定済みの安全条件。変更根拠はまだ弱い) |
| U-4 | **minimal fallbackの廃止**(JA X11、EN D、ユーザー決定25/26の変更) | (a)廃止し同一Prompt 3回 (b)現行維持 (c)Flash-Lite期の短styleで再発率を測ってから | **(c)->(a)**。導入理由の現行backendでの再発率は未測定(英語の過去fallback利用4.4%)。廃止は構造上Style一貫性を確実に改善するが、再発時は同じPromptで3回失敗する |
| U-5 | **Local Rewriteの位置づけ**(EN D-6、JA OPEN-260) | (a)通常retryから外し「HR後に人間が起動する選択肢」として残す (b)完全撤去 (c)現行維持 | **(a)**(救済能力を維持: 過去18記録中8件回復、ただし本文を書き換え、Primary PASS・Azure NG型には原理的に効かない)。日本語対応(OPEN-260)は別 |
| U-6 | **cool-down(600秒)**(EN D-5) | (a)廃止 (b)再生成(2)の前だけ維持 (c)現行(attempt3の前) | **(b)を暫定**(効果の対照データなし。廃止で約10分/segment短縮)。決め手が無いのでX-T1等の副産物で観測 |
| U-7 | **6%減速後の検証**(EN D-4、OPEN-76の承認仕様) | (a)案B: attempt内へ折込み(仕様変更なし) (b)案C: 減速後は簡易チェックのみ、NGでも再生成しない(承認仕様の変更) | **(a)**(Coffeeの直接原因を、承認仕様を変えずに是正できる) |
| U-8 | **Secondary ASRの選択・Phrase List・費用**(EN D-1/D-2/D-10) | (a)Azureのみ(Phrase List無) (b)Azure+ローカルmedium併用 (c)Phrase List有(現行) | **まずX-T1で測定**。暫定は(a)(Phrase List無、誤PASS余地を作らない)。Azureは英語本文で1回約2.2円、segment当たり約+0.2〜0.3円。品質目的で許容できるか判断 |
| U-9 | **Key Phraseを対象外とするか**(EN D-7) | (a)対象外(現行4回構成) (b)対象 | **(a)**(KP 96%が1回目合格、ユーザー決定済み) |
| U-10 | **技術失敗・ASR障害の扱い**(EN D-8、ユーザー要件) | (a)attempt非消費の技術再試行(最大2回) (b)attempt消費 | **(a)**(音声不良と区別、費用微増のみ) |
| U-11 | **適用範囲**(EN D-9)と**既存Tier3・CS層・entity cascadeとの統合**(EN D-11) | (a)5role一斉 (b)Full Storyのみ先行 / 統合: Secondary転写を共有 | **(b)先行**(影響が最大のsegmentで実測)。Secondary転写の共有は二重呼出を避けるため推奨 |
| U-12 | **類似度<0.4でSecondary不実行**(JA X3、EN TTS_FAILURE) | (a)現行維持 (b)短文は閾値を適用しない等 | **(a)維持**(新閾値は採用しない。標本1件(g7)で、誤PASS防止の実績も無い)。J-T2の結果で再確認 |
| U-13 | **新規仕様候補(未承認)**: 否定の活用ギャップ補強(JA「来なかった」)、辞書補強(OPEN-263)、C1のentity判定の拡張/縮小、Primary側`entity_like`のカナ率見直し | それぞれ採用/保留/不採用 | **保留**(根拠は合成のみ。実データ頻度をJ-T2等で確認してから) |
| U-14 | **Trialの実施可否と予算**(8-3) | 全実施 / H-T4+J-T2のみ / 見送り | **H-T4+J-T2 -> X-T1+J-T1(合計約90〜130円)** |
| U-15 | **費用集計へのAzure計上**(新規、別紙) | (a)集計関数にAzureを追加 (b)報告で別枠明記のみ | **(a)**(Budget Guardも盲目のため。Production費用集計コードの変更はFable/ユーザー判断) |
| U-16 | **wav等の大容量証跡の運用**(13章付録) | (a)現状維持 (b)今後もwavはgit管理しない運用を明文化 (c)履歴書換え(禁止) | **(a)+(b)**(wavは既に`.gitignore`で除外。履歴書換えはしない) |

英語D番号との対応: D-1->U-8、D-2->U-8、D-3->U-3、D-4->U-7、D-5->U-6、D-6->U-5、D-7->U-9、D-8->U-10、D-9->U-11、D-10->U-8/U-14、D-11->U-11/U-2。日本語: C1/X5(g8)->U-1、X9->U-3、X10->U-2、X11->U-4、X3->U-12、X8補強・X2補強->U-13。

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
| 未実施の追加Trial | X-T1、J-T1、J-T2、E-T2(承認待ち) | 費用は8-3 | 8-3 |
| Gate | 目標フローは新しい構造・処理フロー(Gate条件A) | **Opus独立レビュー必須**。並行レビュー中。レビュー後もProduction採用は人間ユーザーのみ | CLAUDE.md、`docs/pm/PM_GOVERNANCE.md` 11-3節 |
| 運用上の注意 | Coffee Standard `full_story_part2`はHUMAN_REVIEW_REQUIRED(承認はユーザーのみ)。Coffeeのworktree branchは`main`未merge | 本書では変更しない | RUNTIME_EVIDENCE_01 |

---

## 13. 使用モデル・作成物一覧・付録

### 13-1. 使用モデル
本委任(委任_02)は**有料API未使用**(OpenAI/Azure/Gemini/LLM呼出0回)。実行層=Sonnet 5.5。ローカルで実行したもの: Pythonによる集計(Coffee費用の再計算、worktree側の費用集計関数の読取実行)、grep、git参照。Opus独立レビューは並行中(結果は未取得)。評価用モデルの最新性: 今回の検証はLLM/TTS/ASRのモデル選定を伴わないため該当なし。8-3の追加Trial案は、実行前に最新性をFableが確認する(J-T1のTTSは最新性が未確認)。

### 13-2. 作成物(すべて read-only調査。Production・SSOT・Coffee worktree無変更)
- `er056_output/asr_tts_cross_language_reconciliation_01/RECONCILIATION_REPORT_01.md`(本書)
- `er056_output/asr_tts_cross_language_reconciliation_01/COFFEE_AZURE_COST_ADDENDUM_01.md`
- `docs/pm/delegation_log/2026-10-11_ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01_02.md`
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
