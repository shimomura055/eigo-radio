FABLE-DELEGATION-MARKER: FAMILY-Y-VOICES-DESIGN-01-委任_03-REVISION-20261023

# 委任_03: Family Y設計案へのOpusレビュー是正反映(DESIGN/RESEARCH ONLY・API費用0・Production/Prompt変更禁止)

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_委任_03.md`(N≈327〜337、先頭行MARKER一致確認)。
2. Opusレビュー全文(§2)を `docs/research/FAMILY-Y-VOICES-DESIGN-01/OPUS_REVIEW_01.md` に逐語保存し、`docs/pm/OPUS_FINDINGS_LEDGER.md` に OF-FYD-M01〜M07・S01〜S13 を起票(設計反映後 Status=`DESIGNED`)。
3. ACTIVE_TASK.md: 別agent複数が並行中。編集直前に再読込し、FAMILY-Y行だけ更新。

## 1. Fable判断(Opusレビューの照合結果)
- 総合: 条件付きGO。Sonnet設計とOpusは骨格で一致(X基盤+薄いY入口、旧B承認済みLeakage/Acceptance Gateの移植、新Validatorなし、R0のみ、Comment4廃止)。must-fix M1〜M7は設計書への反映で解決可能=設計内。
- **D2(Voice Card作成方式)はユーザー判断から外し「開示事項」にする**(Opus提案を採用。人手作成は「安定量産」と両立せず実質的選択肢でない。Trial・試聴で問題が出たときだけ再判断)。
- **M1(人物スコープ/世界スコープの分離、Voice段落は数字を使わない)は設計内+開示**とする(Xの Fact Lock文言は変更しない。Y版R0の新規Promptでのみ規定。旧B承認済み「体験claim根拠付け」「候補C(数字は本人経験のみ最大1)」の範囲内)。ただし設計書の⑥に「開示事項」として明記し、ユーザーが異議を述べれば判断事項へ上げる。
- ユーザー判断は **D1(最終パートの中身+Comment4廃止)/D3(人物別TTS Voice)/D4(R0のみ)の3件+最小Trialの実施承認(費用・テーマ選定)** に確定。
- Opusの副次所見「X自身の`full_story_part3`が`A2_SLOWDOWN_TARGET_SEGMENTS`に含まれず、Std 6%減速の未適用ガードが効かない可能性」は、**本委任内で読取のみで事実確認**し(X Std part3は実際に減速されているか=直近run `er019_output/family_x_audio_production_wiring_01/tesla_spacex_merger_talks__run_nws_01/a2` のpart3 clipに`_original.wav`があるか/長さ比)、結果をOPEN_ITEMSに別item(X側)として起票(修正はしない。Fable判断後に別委任)。

## 2. Opusレビュー全文(逐語保存用。以下をそのまま保存する)
```
(Fableが受領した本文をここに貼る代わりに、要点を§3に展開した。保存ファイルには本委任文末尾§6の全文を使う)
```

## 3. 設計書(`DESIGN_PROPOSAL_01.md`→`DESIGN_PROPOSAL_02.md`として改訂版を新規作成、01は履歴として残す)への反映事項
### must-fix
- M1: Y版R0/Card生成Promptに(a)個人スコープ(出典=Voice Cardのみ、タグ不要、実在の人名・組織名・製品名・出来事は不可)/(b)世界スコープ(出典=台帳のみ、Fact Lock規則1〜5、Voice段落ごと最大1件)を明記。Cardの世界スコープ記述は背景fact id参照のみ。Voice段落は数字を使わない(B10上限内であることを開示)。「Leakage Gateは事実判定ではなく編集構造の判定であり、Voices限定の承認済み例外」と明記。
- M2: T4の記述訂正(既存の忠実英訳/A2簡易化関数に段落数引数はない)。日本語・Adv・Stdそれぞれで「本文ちょうど5段落+Title+In One Line」をY側で決定論確認、違反は1回再生成→STOP。話者取り違え防止の決定論確認(Voice段落に一人称あり、リード/最終パートは一人称で始まらない)。代替=5要素JSONで英訳・簡易化するY用wrapper。
- M3: T8の記述訂正。segment名直書き一覧の全洗い出し(`A2_SLOWDOWN_TARGET_SEGMENTS` er003_v1_n3_01_tts_generate.py:115-118、assemble.py:273のガード、runner `_BODY_SEGMENT_NAMES`:488、`_REQUIRED_FULL_STORY_SEGMENT_IDS`:80、`resolve_narrative_role` er020:130、他Grepで追加)。parity test(Y part1〜5がX本文segmentと同じ検査=disfluency/repetition QA・Std 6%減速の適用と未適用ガード・Local Rewrite/Connected Speechの役割・AUW・値ガードを受ける)。共有module変更時はX/Z出力のbyte一致回帰。
- M4: Y runnerの同一run内再利用判定にTTS Voice名を含める(runner:665-694の照合keyにvoice不在)。
- M5: 局所書き換え仕様の明文化(判定3回=初回+書き換え2回、flag段落のみ差替え他段落byte固定、書き換え後もR0同等の決定論検査[Fact Lockタグ・`clean_ja_for_next`・記号QA・`postprocess_ja`・5段落確認]、毎回全文再判定+判定ノイズ記録、失敗時は全文書き直しへ戻さずSTOP→前段診断)。設計書の「失敗時は旧B方式へ戻せる」記述を削除(C11と矛盾)。
- M6: R0最終稿に`postprocess_ja`と最終記号QAを適用(er053:401-426でR1/R2のみに掛かる点を明記)。
- M7(Trial計画): 日本語Leakage Checkの事前校正段階(旧B正解ラベル付き記事を日本語化して誤検知・見逃し測定、NG例: PN A2旧版/PN B1/3V汎用化Regression、OK例: PN A2新版/free_address、費用数円〜20円)。
### should-fix(採用して反映)
- S1 Card 6〜7項目、`not_my_point`は他2人の`concern`から決定論生成、B3統合はTrial後/S2 A2簡易化2通り比較(+0.5円)/S3 Std英語に監視専用Leakage 1回(+2〜4円)/S4 決定論モニタ(記録専用、Gate化はD)/S5 RF flag件数記録/S6 Local Rewrite時の一人称確認/S7 最終パートの締めを2〜3型・定型化禁止/S8 Trialテキスト段階2テーマ・音声1テーマ、期待損失(STOP時にResearch〜B3約17〜50円が無駄)を費用表に追加、書き換え発生確率の前提を旧B実績(1回通過はPN A2新版のみ)で修正、R0+R1比較枠(+8円)は任意/S9 人物Voiceの聞き分けとPD06語り手化の評価(Style変更が必要ならD)/S10 リードの「取材した」表現回避/S11 C06「必須化しない・禁止しない」/S12 A16にKP日本語意味の人称一般化moduleの自動継承を明記/S13 Y版R0に話し言葉・常体の指示。
### ⑥ユーザー判断事項(改訂)
- D1(推奨: 再定義要素なし+締め2〜3型、Comment4廃止。Trialで約0.5円のComment4あり版を並置)/D3(推奨: 人物別、Z正式表の割当関数再利用。PD06・flash-liteリスクと+12〜18円の条件を明記)/D4(推奨: R0のみ。OPEN-217 n=1の弱さと「戻せる」ことを明記)/**Trial実施承認**(改訂費用: テキスト2テーマ+音声1テーマ+M7校正+S2/S3、合計見込みと上限を提示。7-7により新仕様Trialは金額無関係に承認要)。
- 開示事項(判断不要): D2半自動Card、M1スコープ分離とVoice段落の数字不使用、「Xのみ」承認項目のA継承、er109/PNAP scopeへの"Y"追加(技術対応)、Y用の薄い入口新設、STOPセンチネル/RUN_LOCKをZ方式で導入。
### ⑦次工程(改訂Trial計画)
- 段階: (0)M7校正 →(1)テキスト段階2テーマ(各Std/Adv、Leakage/Acceptance/Fact Lock/RF/決定論モニタ)→(2)音声段階1テーマ(人物Voice聞き分け評価含む)→ユーザー試聴。成功基準は既存承認基準のみ。費用表(推定、出典)と上限。
- **テーマ候補**: 新規記事テーマはユーザー選定(PM_GOVERNANCE 13節)。3 Voicesに向く候補を5件(英語・日本語・1行の選定理由・なぜ3視点が立つか)提示し、ユーザーに2件選んでもらう形にする(Fable/Claudeは決めない)。

## 4. その他
- 副次所見(X Std part3の減速ガード)の事実確認結果をOPEN_ITEMSへ別item起票(Status=`INVESTIGATED_PENDING_FABLE`、修正なし)。
- OPEN-463 Status=`DESIGN_REVISED_PENDING_USER_DECISION`。DECISION_LOG 1件、REPORT_LEDGER 1行。commitは明示add、secret_scan `--staged` hits=0、`git push origin HEAD:main`。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 5. 報告(docs/pm/RESULT_PACKET_FYD3.md、同内容を最終報告で)
(1)DESIGN_PROPOSAL_02の変更要点(M/S対応表) (2)⑥の最終形(D1/D3/D4+Trial承認、開示事項) (3)改訂Trial計画と費用表 (4)テーマ候補5件 (5)X part3減速ガードの事実確認結果 (6)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。

## 6. Opusレビュー全文(逐語)
総合判定: 条件付きGO。設計の骨格は妥当(X基盤+Y差分、X runner無変更の薄い入口、旧B承認済みLeakage Check/Acceptance Gate移植、新Validator追加なし、R0のみ、Comment 4廃止)。設計確定前に直すべき点6件(うち2件は設計書記述の誤り: §③-4 T4・T8)。
論点1 旧B品質NG再発 → 条件付きGO。1-(i) 忠実英訳とA2簡易化は「事実を追加しない」契約のため、Leakage項目が英訳後に新規に持ち込まれる経路は論理上ほぼない。後段で起きうるのは平板化でLeakageとは別問題。日本語原稿で判定・修正するのは正しい。日本語版Leakage未校正はGateの意味を左右するためTrial前に校正(M7)。旧Leakage promptは日本語指示文だが判定基準は英語前提(`er012_b_family_voices_writer_generic_01.py:1029-1041`)。1-(ii) 該当パートのみ書き換え・他段落byte固定なら別Voiceへの再発は構造上起きない。残リスク: 判定AIノイズで無変更段落がFAIL反転/書き換え後文がR0の決定論検査(記号QA・タグ除去・後処理)を通らない→M5で明文化。「失敗時は旧B方式=全文書き直しへ戻せる」はC11と矛盾→戻り先は「STOP→前段(Card/B3)診断」に統一。1-(iii) Pairwise Distinctness不採用とCard段階の相互排他+人評価は妥当。`not_my_point`はAIに書かせず他2人の`concern`から決定論生成(S1)。1-(iv) 最重要欠陥(M1): X Fact Lock R0規則3「ニュース欄にないことは書かない」規則5「印のない数字は使わない」(`er053_family_x_factlock_ja_writer_01.py:79-93`)をY Writerに適用するとVoice Cardの「具体的場面から書き始める」と正面衝突(旧B F4と同型の指示矛盾)。Writerは平板化か規則違反に倒れる。X思想(内容理由の再生成撤去)と旧B Acceptance Gateの併存は、Gateが2026-09-17承認のVoice固有編集Gateでユーザー原文§2.3も継承指示のため矛盾しないが、「Leakage Gateは事実判定ではなく編集構造の判定・Voices限定の承認済み例外」と明記。機械検出は追加費用0の決定論モニタで一部補える(S4)。1-(v) 再定義要素なし・固定骨格禁止は妥当だが「末尾1文でリードの場面に戻る」は記事をまたぐ定型(F8再発)になりやすい→締めは2〜3型から選び同型連続回避(S7)。記事間比較は1記事Trialでは判定不可(S8)。
論点2 継承漏れ → 要修正。T4誤り: `generate_family_x_faithful_translation`(`er003_v1_n3_01_advanced_adaptation_generate.py:674`)と`generate_family_x_standard_a2_no_heading`(`er003_v1_n3_01_standard_a2_generate.py:541`)に段落数引数はなくTitle+Body形式のみ検査。X側は`split_family_x_article_text_v2`で「段落3つ以上」確認のみ。Yは段落=話者なのでずれると別人物Voiceで読まれる重大事故(M2)。T8不足: segment名直書き一覧は他にもある。`A2_SLOWDOWN_TARGET_SEGMENTS`(`er003_v1_n3_01_tts_generate.py:115-118`)は`full_story_part1/2`のみで、Audio Validationの「6%減速未適用」検知ガード(`er003_v1_n3_01_assemble.py:273`)に使われるためpart3〜5は未検知。runner `_BODY_SEGMENT_NAMES`(:488 repetition QA対象)、`_REQUIRED_FULL_STORY_SEGMENT_IDS`(:80)、`resolve_narrative_role`(er020:130)→M3。副次所見(Y範囲外): X自身の`full_story_part3`も上記一覧に無い。X Std part3の減速適用漏れ検知が別にあるかFableで確認。同一run内音声再利用判定にTTS Voice名なし: `_generate_or_reuse`(runner:665-694)は「segment名+正規テキスト+style_version」のみ。YはCard(性別・順番)でVoiceが決まるためCard作り直しで古い声が再利用される危険(M4)。Master Audio Storeは`speaker_voice`をkeyに含む(`er006_master_audio_store_01.py:43-54`)。R0のみの後処理漏れ: `postprocess_ja`(Markdown除去、「……」「——」正規化)はR1/R2出力のみ(`er053...:401-426`)。R0最終稿にも同じ後処理と最終記号QAが必要(M6)。C分類: C04/C05/C08/C10/C13妥当。C06は「必須にはしない・禁止もしない(台帳にあれば最終パートで任意に使える)」(S11)。「Xのみ」項目のA継承は妥当(丸め判断は【中核数値】のみでM1採用ならリード/最終パートにしか作用しない。RFはVoiceの個人的内容が台帳にないためflag量産の可能性→Trialで件数測定 S5)。er109/PNAP scope追加は28-1運用7の技術対応でよい(条件: X/Z出力byte一致回帰、er109最終Status確認)。Local Rewrite: Voice segmentはFULL_STORY扱いで役割説明が"the article's main narrated body"(`er020...:154`)→書き換えで一人称が消える危険(S6)。
論点3 不要な複雑化 → 概ねGO。Card 9項目は6〜7項目(性別・人物ラベル・状況と具体場面・懸念・賭けているもの[守りたいものと統合]・制約・背景fact id 0〜1)で足り「必要」は「懸念」と重複。`not_my_point`は決定論(S1)。CardのB3統合はTrial後(Trial-01は原因切り分けのため別callのまま)。Leakage項目数は過剰でない。Closing項目の最終パート規則への吸収は妥当。Y新runnerはOPEN-354/355/415と衝突せず、STOPセンチネル/RUN_LOCKをZ方式で最初から入れるのは有利(条件M3 parity test)。Comment 4廃止は過剰でなく旧B承認版Comment1〜3配置と一致、並置案(約0.5円)も合理的。
論点4 QCD → 条件付きGO。単価推定は概ね妥当だが(S8): 局所書き換え発生確率40〜50%は楽観的(旧B実績: 1回通過はPN A2新版のみ、Trial-02は2回、Trial-01と汎用化Regressionは非収束)/上限3回STOP時のResearch〜B3約17〜50円の期待損失が費用表にない。D4根拠(OPEN-217)はn=1で弱いが方向と費用が支持し戻せるので推奨維持。補強ならTrialテキスト段階に「R0+R1」比較枠(約+8円)。人物別Voice: Z Dialogueは`gemini-2.5-pro-preview-tts`でPD06非適用(`CURRENT_SPEC.md:1704`)。flash-lite+PD06で人物を読ませた実績なし、PD06が語り手化・平板化させる可能性(S9)。+12〜18円は計算として妥当。最小Trialは1テーマではテーマ固有問題と構造問題を区別できず(旧B Opus L3も「次テーマで判別」)、記事間同型化(F8)も判定不可(S8)。
論点5 ユーザー判断事項。D1正当(X承認済みComment 4から外れる)、推奨賛成(S7補正)。D2は判断事項から外し開示事項に(人手Card作成は「安定量産」と両立せず実質的選択肢でない。品質はTrialと試聴で確認、問題時のみ再判断。原文§5にも沿う。最終判断はFable)。D3正当(聞こえ方・費用)、人物別推奨に賛成、S9リスクを判断材料に。D4正当(OPEN-217が明示的にユーザー判断待ち)、R0のみ推奨に賛成。追加Dなし。開示が必要: M1の人物スコープ規定はU4・B12・B10から導ける設計内解決でXの文言は変えない/「Voiceは数字を一切使わない」はB10上限(最大1、必須ではない)の内側で承認済み仕様との衝突にならない/Fableが「Fact Lock適用範囲の変更」と判断するならD5に上げる(境界事例)。
must-fix一覧: M1 人物スコープとFact Lockの矛盾解消((a)個人スコープ: Voice本人の状況・感情・判断・身の回り、出典Voice Cardのみ、タグ不要、実在の人名・組織名・製品名・出来事不可/(b)世界スコープ: 制度・統計・他者や組織の具体的行動・出来事、出典台帳のみ、Fact Lock規則1〜5でタグ、Voice段落ごと最大1件/Cardの世界スコープ記述は背景fact id参照のみ/Voice段落では数字を使わない[本人経験の数字も含む、B10上限内を開示])。M2 段落と話者の対応契約(T4訂正/日本語・Adv・Stdで「本文ちょうど5段落+Title+In One Line」をY側で決定論確認、違反は1回再生成→STOP/話者取り違え防止の決定論確認: Voice段落に一人称、リード・最終パートは一人称で始まらない/代替: 5要素JSONで英訳・簡易化するY用wrapper)。M3 segment_id検査の網羅確認(T8訂正/直書き一覧全洗い出し: 少なくとも`A2_SLOWDOWN_TARGET_SEGMENTS`、`_BODY_SEGMENT_NAMES`、`_REQUIRED_FULL_STORY_SEGMENT_IDS`、`resolve_narrative_role`/parity test: Y part1〜5がX本文segmentと同じ検査[disfluency/repetition QA、Std 6%減速の適用と未適用ガード、Local Rewrite/Connected Speechの役割、AUW、値ガード]/共有module変更時はX/Z出力byte一致回帰)。M4 同一run内再利用判定にTTS Voice名を加える。M5 局所書き換え仕様明文化((a)初回判定+書き換え最大2回=判定3回[旧B `MAX_WRITER_ATTEMPTS=3`同等](b)flag段落のみ決定論差込・他段落byte固定(c)書き換え後もR0同等の決定論検査[Fact Lockタグ規則、`clean_ja_for_next`、記号QA、`postprocess_ja`、5段落確認](d)毎回全文再判定、無変更段落の判定反転は判定ノイズとして記録(e)失敗時は全文書き直しへ戻さずSTOP→前段診断)。M6 R0最終稿に`postprocess_ja`と最終記号QA。M7(Trial計画)日本語Leakageの事前校正(正解ラベル付き旧B記事を日本語化して誤検知・見逃し測定。NG例: PN A2旧版、PN B1、3V汎用化Regressionでflagされた個体。OK例: PN A2新版、free_address。費用数円〜20円。悪ければGate化前に定義調整)。
should-fix: S1 Card6〜7項目・`not_my_point`決定論・B3統合はTrial後/S2 A2簡易化2通り比較(Xそのまま vs 「各段落の話者・一人称・迷いの表現を保つ」1文追加、約+0.5円)/S3 Std英語に監視専用Leakage 1回(+2〜4円)/S4 追加費用0の決定論モニタ(記録専用、Gate化はD): Voice段落の数字、段落ごとのタグ数、一人称有無、最終パートとVoiceの語彙overlap/S5 Voice段落RF flag件数記録/S6 Voice segmentのLocal Rewrite発生記録と一人称保持確認/S7 最終パートの締め2〜3型、「リードの場面に戻る」も定型化させない/S8 Trialテキスト段階2テーマ(ユーザーに一度に2テーマ選定)、音声段階1テーマ(余裕あれば2)、費用表にSTOP時期待損失追加、書き換え確率前提修正、必要ならR0+R1比較枠/S9 人物Voiceの聞き分けとPD06語り手化の評価、Style変更が必要ならD/S10 リードで「取材した人」と受け取られる表現("we talked to"等)回避(旧B先例あり、判断事項にしない)/S11 C06「必須化しない・禁止しない」/S12 A16にKP日本語意味の人称一般化module(`er003_key_words_gloss_alignment.py`、`CURRENT_SPEC.md:1631`)の自動継承を明記/S13 Y版R0に日本語の話し言葉・常体の指示(です・ます調のまま英訳され平板化するのを防ぐ)。
推奨案を変える提案の区分: 設計内で解決=M1〜M7・S1〜S13全部。ユーザー判断の扱いを変える=D2を開示事項に(Fable判断で可)、M1をD5に上げるかは境界事例で見解は「設計内・開示で足りる」。
根拠ファイル: er053_family_x_factlock_ja_writer_01.py(:68-95、:364-426)、er003_v1_n3_01_tts_generate.py(:115-118)、er003_v1_n3_01_assemble.py(:273)、er019_family_x_audio_production_runner_01.py(:80、:488、:537、:665-694)、er020_tts_retry_local_rewrite_01.py(:125-154)、er006_master_audio_store_01.py(:43-54)、er062_family_z_structure_01.py(:84-101)、er012_b_family_voices_writer_generic_01.py(:965-1115)、er003_v1_n3_01_advanced_adaptation_generate.py(:674)、er003_v1_n3_01_standard_a2_generate.py(:541)。Production採用の可否は判断していない。実装も開始しない。