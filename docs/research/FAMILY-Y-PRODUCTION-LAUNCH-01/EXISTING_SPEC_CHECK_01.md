# EXISTING_SPEC_CHECK_01: Y既存仕様・Prompt 02・Gate・X基盤の照合(Phase 0、API 0)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_01 / 2026-10-25。Production変更0。照合は全て既存ファイルの読取り。`file:行`は2026-10-25時点。

## 1. Y承認済み構成の正本(変更しない)

| 項目 | 内容(正式) | 根拠 |
|---|---|---|
| 本文構成 | リード / Voice1 / Voice2 / Voice3 / Tension+Closing(1段落)の**5パート**。独立Closing廃止 | USER_LAUNCH §2-1、`2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER_02.md`、OPEN_ITEMS.md:976(OPEN-463) |
| Voice原則 | 3人・3つの異なる立場。各Voiceは明確な人物像を持ち、その人の立場・経験・価値観から**一人称で主観的に**語る。意見の割り振りではない | USER_LAUNCH §2-1、OPEN-463 確定基本方針(「他Voice中心論点を抱え込まない」「迷い許容」「検証可能な数値/制度/他者行動を創作しない」) |
| 生成方式 | 実在意見ベース(Theme Package=World frame+Persona Sheet+出典付き意見採録)→Voice **R0のみ**(R1/R2は不使用、OPEN-217) | OPEN-463(委任_19〜26)、`FABLE_EVAL_03.md`、`er110_family_y_opinion_based_03.py`(テーマ非依存runner) |
| 人物紹介ナレーション | 各Voice冒頭にナレーション(32〜62字、本人の語りの先取り禁止・紹介の具体物は本人の語りにあるものだけ)。音声は**各levelの既存Full Storyナレーター設定**(Aoede全level固定ではない) | USER_10 §2①、`er110_family_y_redelivery_revision_01.py` `INTRO_RANGE=(32,62)`(:46)、`check_intro` |
| AI編集音声アナウンス | **廃止**。代わりに記事/試聴ページに注意書き: 「本コンテンツのVoiceは、実在する人々の意見を参考に、AIが編集・構成したものであり、特定の実在人物の発言を再現したものではありません。」。Lead(115〜160字)は生成工程で作り直す(単純削除・手動補填禁止) | USER_10 §2②、`PAGE_NOTICE_JA`(`er110_family_y_redelivery_revision_01.py:39`)、`LEAD_RANGE=(115,160)`(:45) |
| In One Line | **Yのみ廃止**(X/Z不変)。原稿・英訳・音声・ページから除外 | USER_10 §2③ |
| Comment | Comment1〜3(Comment4なし)。Preview/Key PhraseはX共通仕様 | DESIGN_PROPOSAL_02 D1、USER_09 §3 |
| 3 VoiceのTTS Voice | Voice1=Algieba / Voice2=Zephyr / Voice3=Schedar(固定)。Z正式表の決定論割当関数`assign_dialogue_voices`の結果と一致(新規選定なし) | USER_02、OPEN-463 委任_27記載、`er110_family_y_audio_trial_01.py:44-50`(`Y_BODY`) |
| Level構成 | **Standard(a2)とAdvanced(b1b)の両方**を作る。Y既存Trial: Std 342.8秒/Adv 321.5秒(宅配、旧構成)。Std英訳=Advancedからの簡易化、Adv=日本語の忠実英訳 | USER_09 §3、OPEN-463 委任_27、`er110_output/family_y_redelivery_audio_01/audio/r0/{a2,b1b}/parts.json` |
| 公開範囲 | Family Y限定共有(unlisted・noindex・権利確認前の転載不可注記)。既存運用に従う | 委任文§3、`REDELIVERY_AUDIO_01/RIGHTS_CHECK_01.md` |

## 2. 『宅配の再配達』個別採用の案B(正式本文)

- 正式採用: USER_LAUNCH §2-3(案A・案C・Round 2生成案へ差し替えない)。
- **本文(改行なしの1段落、200字)**:
  > 午前を指定した人の家にも、不在票が入っていた。受け取り方を選べる人には、再配達の料金は工夫を促す合図になる。でも、受け取る人が払うだけでは、配達の遅れや日時の知らせ方は変わらない。送料をいくらにして、運ぶ人にいくら回すかも、受け取る人の手では変えられない。あなたが家にいられず困ったとき、受け取り方は選べたか、届く日時は分かっていたか？その困りごとは、受け取る人に料金を求めて変えられることだろうか？
- sha256(本文のみ、前後空白なし、UTF-8)= **`26745165e33be3ea5cf4548f365c6d145862d94ad0201cc69695c0a954800e71`**(`closing_B/closing.txt`・`REVISION_SCRIPT_01.md`パート5案B・`article_revised_B.md`で一致を確認)。`closing_final.txt`(末尾LFあり)のsha256=`e9a853e3c3ca645d0f9cbb4132f6427c66f3d31084aa300bbe6084a409fd8c69`。Production注入はLFなし本文のshaで照合する。
- 完成5パート原稿: `er110_output/family_y_redelivery_audio_01/revision_01/article_revised_B.md`(sha256 `e84b7b7ceab27bc867227f37d998827789d52fef5dd4bbdd84fd333e99a155d7`)。Voice本文の元=R0 `er110_output/family_y_opinion_based_03/redelivery_fee/run_01/article_ja.md`(sha256 `566ebd97d7ba1c81dcaa64305c8e5f02228a44cf1b5aa64f5f0105b1e5498a89`、Leakage Gate PASS・byte一致検査済み)。Theme Package=`OPINION_BASED_02/THEME_DATA_02.json`(sha256 `f0d0af367950735bb0264162d3cb45e3ef330759d8077e9d6f9bb5c3dadf0288`)。
- 案Bの既存検査: 決定論`check_closing` PASS(175〜245字、1文55字以内、「？」終わり、数字・一人称・AI編集語・定型結論句なし)、Leakage Gate(tension 6項目、gpt-6-luna high)**1判定でPASS**(`closing_B/gate/gate_result.json`: `n_judgements=1`、`first_judgement_flagged=False`)。出典との連続一致(日20字/英8語)0件。
- **確認事項(Production設計への入力)**: 案Bは「最後の疑問文が2つ」(「…分かっていたか？」「…変えられることだろうか？」)で、Prompt 02の『最後の問いは1つ』とは異なる。案Bは**ユーザー承認の人手設計案**なので一般化方式の規則で再検査して修正しない(承認本文を改変しない)。固定注入は一般化方式の決定論検査・選定処理を通さず、Gateのみ通す設計とする(DESIGN_01 §5)。

## 3. Prompt 02・入力構造・出力schema・選定処理・Gate

### 3-1. Prompt 02(変更しない)
- ファイル: `docs/research/FAMILY-Y-VOICES-DESIGN-01/CLOSING_GENERAL_01/prompt_closing_general_02.txt`、sha256 **`4713ceff2dd00a2f67eb9313ae9e206a4a3236c5b158e624c10ccf6fc20e5f07`**(`sha256sum`で再確認。コード上の期待値=`er110_family_y_closing_general_trial_01.py:40-44` `PROMPT_VERSIONS["02"]`)。形式: `=====DEVELOPER=====`/`=====USER=====`の2部、読込時にCRLF→LFへ正規化してからshaを取る(`load_prompt_parts` :80)。
- モデル/設定: 生成=`gpt-6.1-sol`(`y0.MODEL_TOP`)・effort **high**(`EFFORTS`、既定high)、判定=`gpt-6-luna`(`y0.MODEL_CHEAP`)・effort high(`generate_one`内`leak(..., model=y0.MODEL_CHEAP, effort="high")`)。mediumはRound 2で不採用候補(宅配で劣る)=採用しない。
- 見積単価: 1生成+判定 high平均19.21円(宅配21.0/SNS17.4、`EVAL_02.md`(vi))、`GEN_EST_BY_EFFORT={"high":20.0}`(:49)。

### 3-2. 入力構造(Production module化で正確に移植する)
`normalize_input`→`render_blocks`(:108-143)。Promptの3プレースホルダへ置換、未置換`@@`が残ればエラー:
- `@@THEME_BLOCK@@` = `【テーマ・論点】{question}\n【前提と範囲】{premise}\n【用語の意味】\n- {term}: {definition}…`
- `@@PERSONA_BLOCK@@` = `【3人の人物像】\n- 人物i: {role}。{sketch} 大事にしていること: {stake}`
- `@@VOICE_BLOCK@@` = `【人物iの語り】\n{Voice本文}`(3本、区切り空行)
- **Research/Fact欄は無い(空)**。入力に入れないもの: 既存Closing(案A/B/C等)・切り口・Gate結果。Theme PackageからPersona(`role_ja/persona_sketch_ja/stake_ja`)・World frame(`question_ja/shared_premise_ja/distinctions`)を読む。

### 3-3. 出力schema(strict JSON、`family_y_closing_general`、:59-76)
`observations[{kind∈{共通点,相違点,矛盾,意外性}, note, evidence_quotes[]}]` / `candidates[{id,new_view,evidence_quotes[],deepens,listener_question,pitfall}]`(3〜5件) / `selected_id` / `selection_reason`(全候補の順位付け+選定理由+見送り理由+受ける語りの一節) / `closing_ja`。**記事に使われるのはclosing_jaのみ**、他は監査用(gen_metaと共にrunに保存)。

### 3-4. 候補選定処理・決定論検査(生成後)
- `check_structure`(:198): 候補数3〜5、id重複なし、`selected_id`が候補内、observations非空。
- `rev.check_closing`(`er110_family_y_redelivery_revision_01.py:312`): 空/複数段落/一人称/ラベル開始/取材者表現/算用数字/です・ます調/AI編集語/定型結論句/「？」終わり/**175〜245字**/**1文55字以内**。
- 記号: `p._fin`(タグ漏れ=`TagLeak`)+`safety.symbol_gate_requires_stop`。
- 違反時の再生成は**1回**(前回の問題を`_PROBLEM_JA`説明付きで同Promptへ追記)→なお違反なら`CLOSING_GENERAL_CONTRACT_STOP`(:300-304)。Round 2の再生成率=0/6。
- 根拠引用の逐語照合(`grounding_report`、記録専用・合否に使わない)。`style_report`(推量語/逆接/出所曖昧/「もし」)も記録専用。

### 3-5. Leakage Gate(Closing=Tension 6項目。定義は変更しない)
判定関数: `p.run_leak(client,"tension",{"tension": final},model=luna,effort="high")`(`er110_family_y_persona_text_trial_01.py`)。項目逐語(同:376-381 `_TENSION_ITEMS`、旧B由来=`er012_b_family_voices_writer_generic_01.py:1053`):
- `leak_evidence_subject` / `leak_discovery_syntax` / `leak_evidence_memorable`: Voiceと同じ意味(最終パート本文に対して判定)。定義=「文の主語が、調査・研究・データ・割合・報告になっている文が無い場合PASS」「『〜が明らかになった』『〜という傾向がある』のような、発見・傾向を報じる記事の文構造へ戻っていない場合PASS」「調査や事実よりも、その人物の経験・感情の方が記憶に残る書き方になっている場合PASS」(`y0`:458-470)。
- `leak_numbers_foreground`(最終パート用): 「具体的な数字・比較結果が、3人の合理性を制約する力の描写より前面に出ていない場合PASS」。
- `leak_tension_reverts_to_research`: 「最終パートの中心が、3人がなぜ違う答えに至るのかの掘り下げになっており、調査・研究データそのものの説明・比較へ戻っていない場合PASS」。
- `leak_binary_camp_split`: 「最終パートが3人を単純に対称的な2対1の陣営へ分けて描いていない場合PASS(分けている場合FAIL)」。
- 正式運用時の再判定/書換え: `p.run_gate`(:617)=判定→局所書換え→再判定、**判定最大3回**、残れば`LEAKAGE_RESIDUAL_STOP`(全文書き直しに戻さない)。Closing一般化Trialは**判定1回のみ・書換えなし**(切り口を失わせないため)で測定した=Production運用はTrialと異なる(DESIGN_01 §6)。

## 4. X基盤のstage構成とYに必要な差異

X正式Production基盤は2 runnerの連携: ①`er019_family_x_entertainment_production_runner_01.py`(日本語記事: Research→Ledger→B3→W-1 Writer→英訳→簡易化→RF) ②`er019_family_x_audio_production_runner_01.py`(`--stage plan|scaffold|study_text|tts|assemble|player|all`、:2809-2810)。Zは`er026_family_z_fiction_production_runner_01.py`が**stage framework**(`E2E_STAGES`:1130-1131=seed_check, writer, std_adjust, plan, support, kp, tts_b1b, tts_a2, provision_shell, gate, assemble, pages, page_verify。`run_stage`:2330、stage別推定費用guard`E2E_STAGE_EST_JPY`:1132、`stage_context`:1264)を持ち、X部品を呼んで新Familyを立ち上げた先例である。

| X/Z stage | Y対応 | 方針 |
|---|---|---|
| Research/Ledger/B3/W-1 Writer/RF | なし(Research/Fact空) | **除外**(YL-B01/B02)。Theme Package検査stageに置換 |
| (新)Voice生成+Voice Leakage Gate | Y固有 | `ob`/`ob2`/`ob3`のDEV runnerをProduction moduleへ移植(patched_*のモジュール差替えを使わない形に展開) |
| (新)Lead+人物紹介 | Y固有 | `rev.generate_intros`/`generate_lead`相当を移植。Lead/introのGateは「Tension専用2項目[`leak_tension_reverts_to_research`/`leak_binary_camp_split`]はLead・紹介に非適用」の既存扱い(`rev.LEADINTRO_NA_FIELDS`:464)を移植(Gate省略ではなく適用外項目) |
| (新)Closing(一般化 or 固定注入) | Y固有 | §3の移植。固定注入は案Bのみ |
| 英訳(Adv忠実英訳→Std簡易化) | A(YL-A16) | X関数(`generate_family_x_faithful_translation`/`..._standard_a2...`)を再利用。ただしYは5パート+紹介+Lead。In One Lineを生成しない |
| 3分割`split_family_x_article_text_v2` | Y用splitter | 新設(5パート、紹介行とVoice本人行のパート内2行構成) |
| Plan/scaffold(Preview/Comment/KP選定/gloss) | A/C | Preview/KP=共通moduleを再利用、Comment=Y版role(Comment1〜3) |
| study_text(Part 1)・Part 2(er120)・KP HR(er119) | F/A | **接続点**(§6)。X runnerの`--stage study_text`と同様に、KP段の後に挿入 |
| TTS(Adv→Std) | A/C | `generate_family_x_b1_segments`相当のY版(Voice別TTS Voice、ナレーター=Full Story設定導出)。Chunkは非適用(YL-B08) |
| provision_shell/gate/assemble/pages/page_verify | A | ZのstageをY用timelineで。Gate=style_profile gate/audio validation gate/key_phrase_source_gate/shared narration gate |
| STOP/RUN_LOCK | A | Zの方式(`er062_family_z_structure_01.py:236-414`)を採用(Xには無い) |
| 試聴ページ | A/C | 共通builder+注意書き枠。ページscriptは記事別(X=`er019_nws2_final_page_01.py`相当) |

## 5. 既定値のGrep(未承認機能の到達経路)

| 確認 | 結果 | 根拠 |
|---|---|---|
| Y機能がProduction runnerから到達するか | **しない**。`production_reachable=False`、`er110_family_y_*`はどのProduction runner/.env/起動scriptからも参照されない(testでGrep固定) | `er110_family_y_audio_trial_01.py:176`、`er110_family_y_closing_general_trial_01.py:6-14` |
| 共有scope定数 | `APPROVED_SCOPES=frozenset({"X","Z"})` | `er103_proper_noun_alarm_policy_01.py:42` |
| routing keyにY | 0件(`FAMILY_Y_*`をGrep) | `er006_model_routing_contract_01.py`(L119-171に`FAMILY_X_*`/`FAMILY_Z_*`のみ) |
| DEV-onlyの歯止め | 有料runは`--paid`+`BUDGET_APPROVED.json`の両方が必要、Leakage Gate累計22円超で`SKIPPED_BUDGET`(後追い運用) | OPEN-463 委任_22/25記載。**Productionでは移植しない**(Gate省略禁止) |
| 新flag | 本Phase 0で追加なし | — |

## 6. 進行中仕様の接続点(別agentが実装中=読むだけ。確定I/Fに依存する部分は「接続点」)

| 仕様 | 現状(2026-10-25) | Yの接続点(確定後に結線) |
|---|---|---|
| KP/文法HR(OPEN-518, er119) | `docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/DESIGN_02.md`。commit d7a5713d4でKP側X/Z共通核を実装(`IMPLEMENTED_PENDING_EVIDENCE`、単体test 104件PASS、Production run 0。実API evidence R1〜R4は10/26以降)。共有`sc.run_key_phrases`は無変更。新module er119をX/Z runnerからだけ呼ぶ設計。**Yは「正式入口なし=PRODUCTION_WIREDにしない」と明記**(DESIGN_01:102)。OPEN-484(g)へ『Y正式KP段が`er119.run_kp_with_review`を通る・Y用`part1_items`』を追跡 | Y KP段が`er119`を呼ぶ(HRあり=`wait`→選択→再開、HRなし=明示auto宣言dict)。NG registryと`part1_items`はY入口で共有 |
| Part 2(OPEN-519, er120) | module完成(test 99 PASS)・runner未接続。Adv限定 | Y Adv KP段の後。er119 kind=grammar経由 |
| Part 1(OPEN-512) | X/Z `PRODUCTION_WIRED`。共通module`er003_kp_general_explanation_01.py`+`er003_kp_source_sentence_ja_01.py` | Y Advに接続 |
| Chunk TTS | X/Zのみ承認(YL-B08) | 非適用(判断待ち=Fable確認) |

## 7. 未確認事項
- Launch原文は取得元jsonlで文字化けしており、委任文§0要旨に依拠した。要旨と矛盾する記述が原文にあれば台帳を更新する。
- er119/er120の最終I/Fと、Fable受入後のStatus(`WIRED_PENDING_FABLE`→`PRODUCTION_WIRED`)は並行案件。
- Y宅配Advの音声で速度問題が出るか(Chunk要否)は聴取結果待ち。
- Standardのレベル構成: 既存Y Trialは両level作成済みで問題なし。Y固有の「Std人物の語りだけ減速なし」版の採否は未決(X準拠既定で配線、YL-A02)。
