# EXISTING_SPEC_CHECK_01 (委任_27 Phase 0: 既決設計の正本と、既存Y音声Trial経路で今回の5パートを処理できるかの照合。API 0)

作成: 2026-10-25。SSOT全文読込はせず、節・行のGrepで照合。Status: 日本語R0=VALIDATED(限定)(FABLE_EVAL_03)。今回の到達上限=VALIDATED(音声化Trial)。Production採用・配線なし。

## 1. 既決設計の正本(節番号・ファイル:行)
| 項目 | 決定内容 | 正本(ファイル:行) |
|---|---|---|
| 本文5パート固定 | リード / Voice1 / Voice2 / Voice3 / Tension+Closing。3 Voices固定、独立Closing廃止。Tensionは旧B「共通前提→分岐点→非対称性」継承。ユーザー最新指示でも同一 | OPEN_ITEMS.md:976(OPEN-463 確定済み基本方針)、docs/pm/delegation_log/2026-10-25_FAMILY-Y-VOICES-DESIGN-01_USER_09.md §3、DESIGN_PROPOSAL_02.md:196(5パート表) |
| Comment 1〜3(Comment 4廃止) | D1=ユーザー決定(#163) | USER_DECISION_REGISTER_01.md:356(#163)、er110_family_y_audio_trial_01.py:10・:164・:247・:352(Comment 4は廃止の記述) |
| Voice割当(人物別) | **固定: Voice1=Algieba / Voice2=Zephyr / Voice3=Schedar**(ユーザー決定D3、#163)。ナレーター(リード/Tension+Closing/In One Line)=Aoede | USER_DECISION_REGISTER_01.md:356、docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER_02.md:17,88、er110_family_y_audio_trial_01.py:44-54 |
| Family Z正式Voice表・既定割当 | 男性=Algieba/Schedar/Fenrir/Orus/Puck、女性=Zephyr/Kore/Leda/Sulafat/Erinome。男女独立・登場順。ナレーター=Aoede | CURRENT_SPEC.md:1563、er062_family_z_structure_01.py:47-52(pool)・:105(assign_dialogue_voices) |
| **両者の整合(今回の確認)** | 今回の3人(V1=男・登場1番目、V2=女、V3=男・登場2番目)に`assign_dialogue_voices`を適用すると Algieba/Zephyr/Schedar で、ユーザー決定の固定割当と**完全に一致**する(新規Voice選定なし)。V1とV3は別Voice(Algieba/Schedar)。性別はVoice Card/PERSONAS_05 §1の明示情報(V1=私・男、V2=わたし・女、V3=僕・男、いずれも聞き分け用に補った旨がPERSONAS_05に明記) | er110_family_y_redelivery_audio_01.py:`verify_voice_assignment`(testで固定: er110_family_y_redelivery_audio_01_test_01.py::TestVoices) |
| 速度・Style・TTS設定 | fx_20261017 profile(PD06 Full Story ほか)を継承、TTS backend=speech_metadata_flash_lite(Pro系TTS不使用)。Std Full Storyは6%減速(Std Narrator/本文)。Y本文5segment全てで`slowdown_applied`を確認するY版M3 Gate | CURRENT_SPEC.md:680・:1684-1700(PD06/6%減速行)、er110_family_y_audio_trial_01.py:39-40・:521-562(y_style_gate) |
| 英訳方式(Family X承認方式) | Adv=忠実英訳(`generate_family_x_faithful_translation`)+In One Line(Adv限定)、Std=A2簡易化(`generate_family_x_standard_a2_no_heading`)。話者・一人称・迷いの保持は`must_fix`欄(A2 Prompt本体は無変更)で足す(OF-Y3-01(b)=Opus確認済み) | er110_family_y_text_trial_01_run.py:313-380、er110_family_y_persona_text_trial_01.py:`y_contrast_must_fix`、er012_e_family_entertainment_two_level_runner_01.py:361 |
| Preview/Comment/Key Phrase/In One Line | Xの最新承認仕様が基盤(KP=fulltext_p2選定+Canonicalization[所有格一般化・A-1]+gloss[X2p']、共通module)。Y版Comment 2/3 role・Comment 1=X COMMENT_1_ROLE。In One Line=Adv限定生成+Std側にも存在 | OPEN_ITEMS.md:999(OPEN-484)、er110_family_y_text_trial_01.py:809-835、er110_family_y_text_trial_01_run.py:231-270 |
| 音声検査(TTS/ASR) | 統一ASR(AUW共通基盤)・Connected Speech(Full Story/Comment等5 role)・Repetition QA(method D')・disfluency QA・Pronunciation Resolver・KP音声検査(canonical+3条件)・局所Rewrite(recovery)・retry/fallback上限・Audio Validation Gate(組立前)・HR Lock | CURRENT_SPEC.md:1684-1700(AUW共通基盤)、:2162-2163(発音Ledger)、er110_family_y_audio_trial_01.py:219-292(generate_y_b1_segments)・:296-389(a2)・:569-615(assemble) |
| 速度・ポーズ | 語り手切替pause=`CHARON_TO_AOEDE_PAUSE_SECONDS`(0.8秒)、Std Comment前後1.0/0.8秒、In One Line→Outro 0.5〜0.8秒(X値を継承) | CURRENT_SPEC.md「Cross-level仕様」ポーズ表、er110_family_y_audio_trial_01.py:57・:466-518 |
| 安全上限・STOP | HR Lock迂回禁止、再起動はFable許可回数のみ、予算Cap、STOP通知 | docs/pm/PM_GOVERNANCE.md 7-7・7-9・26節、CLAUDE.md |
| Y Production入口の不在 | `production_reachable=False`、`PRODUCTION_WIRED`と呼ばない。Y Production化時の必須受入条件=OPEN-484 | OPEN_ITEMS.md:999、er110_family_y_audio_trial_01.py:176 |
| 開示文・R0 | R0本文(日本語・3 Voice)は無変更。冒頭に『これから聞くのは、実在の特定の人の話ではない。ネットなどで公開されている複数の意見をもとに、組み立てた声だ。』の開示文がrunnerにより付く | er110_output/family_y_opinion_based_03/redelivery_fee/run_01/article_ja.md、EVAL_SET_04.md (A) |

## 2. 既存Y音声Trial経路で今回の5パートがそのまま処理できるか
**結論: 処理できる(音声段・Comment/KP scaffold・英訳段は既存5パート版をそのまま呼べる)。足りないのは「日本語5パート原稿の組立(リード+Tension+Closing)」「出力先の差替え」「権利・対応確認」だけで、いずれもデータ追加と薄いglueで済む。**

| 層 | 既存部品(5パート版) | 今回そのまま使えるか | 差分(新規・薄いglue) |
|---|---|---|---|
| 音声段(TTS/ASR/KP音声/組立) | `er110_family_y_audio_trial_01.py`(Y_BODY=lead/voice_1/voice_2/voice_3/final、alias ID full_story_part1/2/3/3_c2/3_c3、固定Voice、Y版M3 Gate、Std 6%減速確認、Trial名前空間のMaster Audio Store、Local Rewrite recoveryのer110配下付替え) | **そのまま**。candidate名`r0`のまま、`BASE/SRC/OUT_ROOT`をprocess内で差し替えるだけ(with内、finallyで復元。testで固定) | 出力先(`er110_output/family_y_redelivery_audio_01/`)の差替え |
| scaffold(Comment1〜3/Preview/KP/日本語タイトル) | `er110_family_y_text_trial_01_run.cmd_scaffold`(5パート版、Comment 4生成なし) | **そのまま呼ぶ**(run dirの配置をその規約に合わせる) | `y_writer/gate_r0/article_final.md`・`english_r0/`の配置(glue) |
| 英訳(Adv忠実/Std A2) | `adv_gen.generate_family_x_faithful_translation`・`std_gen.generate_family_x_standard_a2_no_heading`・`efam._advanced_in_one_line`・`y0.check_en_contract`(5段落) | **そのまま** | persona版`y_contrast_must_fix`の5パート版(段落番号のみ差替え)をmust_fix欄で渡す。Ledgerは「検証済み事実台帳なし」の明示placeholder(意見ベースのためFact主張を新たに述べない旨) |
| 日本語リード | 5パート契約のリード仕様(`Y_R0_HEAD`の1段落目)が既存。R0のrunnerは生成しなかった | 仕様は既存 | リード生成1 call(仕様は`Y_R0_HEAD`から逐語抽出、複製しない)。R0の開示文を逐語で後置 |
| 日本語Tension+Closing | persona版`generate_tension`+`run_gate(kind=tension)`(Leakage 6項目判定→局所書き換え→再判定、上限3判定)が既存(Opus確認済み) | 生成・Gateの部品は**そのまま**(共通前提・規則の例文をprocess内で差替えるだけ) | 人物ラベル・主張の要点・対比の具体物(PERSONAS_05 §1とR0本文の語のみ=データ) |
| 試聴ページ | `er110_family_y_audio_page_01.py`(5パート版標準形式) | 部品を再利用(出力先・人物ラベル・日本語原稿の読み先をprocess内差替え) | 限定共有注記・noindex・単一候補用JS(薄い) |
| 話者ラベル/パート順の機械検査 | なし(日本語・Adv・Stdの対応確認は既存になし) | — | `mapping_check`(決定論の記録。Gateにしない)を追加 |
| 権利照合 | なし | — | `cmd_rights`(出典との連続一致を機械チェック) |

### 2-1. 既存経路で足りない差分(列挙)
1. 日本語5パート原稿が存在しない(R0は3 Voice+開示文のみ)。リードとTension+Closingの補完が必要=上表。人物3人の本文は**無変更**(gate最終本文とsha一致をコードで確認)。
2. 英訳にR0固有の「話者保持」を足す必要=既存`must_fix`欄(OF-Y3-01(b))の5パート版。
3. 話者ラベル・パート順の対応確認(日本語/Adv/Std)=新規の決定論記録(新Gateではない)。
4. 出力先の分離(school_phone_banのパス固定を回避)=process内差替え。
5. 権利確認(出典との連続一致0件)と限定共有ページ=RIGHTS_CHECK_01。
6. 既存の古いページ生成`_ja_original`が`#`付きタイトルを前提にしており本Trialの`article_final.md`形式(タイトル行が`#`なし)ではずれる→ページ用wrapperで読み先を差替え(既存module無変更)。

### 2-2. 新しい処理フロー・Validator・Voice選定・Style変更に該当するか
- 該当しない。Voice選定は既存固定割当(Z表の結果と一致を機械確認)、Styleはfx_20261017継承、Validator・Gate閾値は無変更。追加した`mapping_check`と`cmd_rights`は記録用の決定論チェック(合否でSTOPさせない補助、新しい品質基準ではない)。
- Risk Flagger: Y列は「未定」(CURRENT_SPEC.md:1684表)。X/Zの音声経路ではRF未実施でもTTS前保険のみ。Yの過去Trialは非停止で記録していたが、意見ベース(事実主張なし)では台帳が存在しないため**今回は実行しない**(未適用として記録)。
