管理ID: FAMILY-Z-IN-A-GROVE-PRODUCTION-01(新規)。委任_01「『藪の中』(芥川龍之介) 原作・権利確認+Seed(source_essentials付き)準備+CP checklist+予算計画+STORY_REGISTRY登録」。制作本体(writer以降の有料run)は**本委任では起動しない**(FableのSeed CP後に委任_02)。前例テンプレート=`docs/pm/delegation_log/2026-10-24_FAMILY-Z-MONKEYS-PAW-PRODUCTION-01_DELEGATION_01.md`と`2026-10-24_FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01_DELEGATION_02.md`§前提(成果物の形・起動コマンド列)、`docs/research/FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01/{SOURCE_CHECK_01,CP_CHECK_01,BUDGET_PLAN_01}.md`、seed `er026_seeds/the_tell_tale_heart/`を先に読み、同じ形式で作る。正式仕様=`CURRENT_SPEC.md:1630`(原作忠実性包括対策v1: source_essentials最大5件・source_quoteは原作最終段から逐語・fail-closed)+Family Z節(Grep「Family Z」「Voice割当」「3分割」「速度仕様v2」)。過去Trial方式やsuperseded仕様と取り違えない。

並行worker: JA-ASR 委任_03(SSOT・ACTIVE_TASK編集中)、X Comment3 委任_01(er019/er003系X Std Comment code編集中)、Family Y Deep Research×2(docs/research/FAMILY-Y-*)。**本委任ではSSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/UDR)・ACTIVE_TASK・er0XX Production code(STORY_REGISTRY登録に必要な最小追加を除く)を編集しない。** Family A/B/C不可。
**ファイル範囲**: `docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/`(新規)、`er026_seeds/in_a_grove/`(新規)、STORY_REGISTRY該当ファイル(前例と同じ場所・同じ形式の1エントリ追加+登録test)、`docs/pm/delegation_log/2026-10-28_FAMILY-Z-IN-A-GROVE-PRODUCTION-01_USER.md`(下記ユーザー原文を**逐語**保存、最初に)、同`_委任_01.md`(本文逐語)、`docs/pm/RESULT_PACKET_FZIG1.md`。
開始時 `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-Z-IN-A-GROVE-PRODUCTION-01 --run-dir docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01 --out docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/stop_check_01.json`(rc=3で停止)。本委任はAPI 0(LLM/TTS/ASR呼出なし。原作取得はhttps経由の青空文庫のみ)。

## ユーザー原文(逐語)
```
# Claude Codeへの指示｜Family Z『藪の中』新規制作

## 1. 目的・制作作品

Family Zの次回作品として、芥川龍之介『藪の中』を制作してください。

対象：
- 作品：『藪の中』
- 原作者：芥川龍之介
- Family：Z
- Level：Standard／Advanced
- 制作方式：現行Family Z正式Production仕様

**既存の承認済みProduction仕様を使用し、Standard／Advanced両方の完成版を制作してください。**

今回の作品選定はユーザー承認済みです。新たな制作方式の採用を意味しません。

## 2. 作品の重要な魅力

本作の核心は、同じ事件について異なる人物がそれぞれの立場から証言し、その内容が食い違うことです。

特に以下を重視してください。

1. 証言者ごとに異なる人物像・心理・語り方が伝わること。
2. 証言の矛盾が、聞き手の興味を引き続けること。
3. 証言を統合して、単一の客観的な真相を作り上げないこと。
4. 語り手の主観・自己正当化・隠したい事情など、原作の心理的な面白さを活かすこと。
5. 短編化しても、作品の核心である「真相の不確かさ」を失わないこと。

ただし、これらは作品固有の編集上の重点です。

既存のFamily Z品質基準を独断で引き上げたり、新たなValidatorや追加Gateを設けたりしないでください。

## 3. 原作・著作権確認

制作開始時に、正式Seed条件を確認してください。

- 芥川龍之介の原作全文を一次資料で確認する。
- 日本国内での著作権・利用条件を確認する。
- 現代語訳・英訳・第三者による翻案を権利確認なく流用しない。
- 確認済みの原作から、Family Zの既存方式で独自に英語版を制作する。

参考原作：
https://www.aozora.gr.jp/cards/000879/card179.html

原作を確認せず、あらすじやAIの記憶だけで制作を進めないこと。

## 4. 既存Family Z仕様の適用

CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・Production実装を確認し、現行の正式仕様に従ってください。

特に以下を維持してください。

- 原作Seedとsource_essentialsの作成・承認手順
- 原作の重要要素と語りの視点を保持する現行方式
- Advanced原稿の作成・推敲後、Standardへ難易度調整
- 現行の本文長・3分割構成
- Comment 1〜3とPreviewの現行生成方式
- Standard日本語Comment／Advanced英語Comment
- 各レベルのKey Phrase／Key Word、学習項目
- TTSのVoice割当、速度、感情・文脈制御
- ASR、retry、fallback、regeneration、resume
- 正式Assemblyと公開ページの品質確認

過去のTrial方式やsuperseded仕様を、現行Production仕様と取り違えないこと。

## 5. 『藪の中』固有の制作上の留意点

### 証言者とVoice

この作品では、登場人物の発言そのものが物語を構成します。

現行のFamily Z Voice割当・登場人物Voice仕様を確認したうえで、証言者を聞き分けられる自然な構成にしてください。

- 人物ごとの立場や感情の違いを表現する。
- 証言者の切替が聞き手に理解できるようにする。
- 声色を極端に演じ分けること自体を目的にしない。
- 原作の語りの視点と証言構造を尊重する。
- 既存の承認済みVoice候補を優先し、不要な新Voice探索を行わない。

### Storytelling

単に「Aはこう言った、Bはこう言った」と事実を並べるのではなく、それぞれの証言に引き込まれる構成を重視してください。

特に、証言を省略・統合する場合は、矛盾の構造や人物の心理が損なわれないか確認してください。

原作にない明確な真犯人・決定的な証拠・客観的な結論をAIが創作してはなりません。

### Comment／Preview

原作の核心的な矛盾や、後から明らかになる証言内容を先取りしないこと。

各Commentは聞き手の理解と興味を支える役割に徹し、物語の解釈や真相を一方的に決めつけないでください。

## 6. 制作の進め方

必要な原作調査・Seed準備・原稿生成・英語品質確認・音声化・検証・組立を、既存のProduction工程に沿って進めてください。

- 独立作業は原則として並列化する。
- 品質を守りながら最短で完成させる。
- 不具合は既承認の仕様・予算内で原因究明から再検証まで自律解決する。
- 既存成果物や検証結果を再利用し、不要なAPI呼出を避ける。
- 作品固有の事情を理由に、未承認の新仕様をProductionへ追加しない。
- 承認済みのGate・Human Review・STOP条件は維持する。

特にSeed承認など、正式仕様上ユーザー判断が必要な箇所は省略しないこと。一方、不要な逐次確認で制作を止めないこと。

## 7. QCD

優先順位：

**品質（Q）＞完成速度（D）＞量産単価（C）≫開発費**

- 品質：現行Family Z承認基準を必要十分に満たす。
- 速度：品質を守る範囲で最速。
- 量産単価：目標70円／記事セットを意識し、不要な再生成を抑制する。
- 開発費：既存の予算管理ルール（原則1,000円／日、JST）および個別承認枠を遵守する。

日次予算内であることを理由に、未承認の制作範囲変更・仕様採用を行わないこと。

## 8. 最終成果物・報告

Standard／Advancedの完成候補を、ユーザーが試聴できるページとして提出してください。

最終報告には以下を含めてください。

1. Standard／Advancedの試聴URL
2. 原作・権利・Seed確認結果
3. 証言者の構成とVoice割当
4. 原作の魅力・証言の矛盾をどう維持したか
5. 本文・Comment・Preview・学習項目の品質確認
6. TTS／ASR／Assembly検証結果
7. 実際の制作費と量産単価への示唆
8. 未解決事項・Human Review項目
9. Git／SSOT反映状況
10. Fableの独立受入判定

**完成候補の提出と、ユーザー最終試聴PASS・正式公開承認は区別してください。**

ユーザーの試聴承認前に、正式公開済みと扱わないこと。

## 9. PM Gate・STOP条件

- 既存Family Z正式仕様を維持する。
- 新しい品質基準や制作方式の採用はユーザー承認事項。
- 原作の利用権利が確認できない場合はSTOP。
- Seed承認など既存Gateを通過してから後続工程へ進む。
- 重大な品質問題・予算超過・承認範囲外の変更はSTOPして報告。
- FableはClaudeの完了報告を追認せず、Production実経路・品質・QCD・当初目的を独立して照合する。
- VALIDATED／APPROVED_FOR_PRODUCTION／PRODUCTION_WIRED／ユーザー試聴PASSを混同しない。

中間報告は原則不要です。ユーザーの判断が必要なSTOP条件に達した場合のみ報告し、それ以外は承認範囲内で自律的に進めてください。

**最重要：『藪の中』の面白さは、複数の証言がそれぞれもっともらしく、それでいて互いに矛盾することにあります。この構造を活かし、聞き手が最後まで真相を考え続ける英語学習ラジオを完成させてください。**
```

## 成果物
1. `SOURCE_CHECK_01.md`: 青空文庫 card179 から原作全文を取得(本文保存先・sha256・取得日時・文字数)。権利: 芥川龍之介(1927年没)=日本国内パブリックドメイン、青空文庫の利用条件(入力者・校正者クレジットの扱い)を引用して記録。現代語訳・英訳・翻案は参照も流用もしない(英語版はFamily Z既存方式で独自制作)。原作の構造(7証言: 木樵り/旅法師/放免/媼/多襄丸の白状/清水寺に来れる女の懺悔/巫女の口を借りたる死霊の物語)、各証言者の立場・主張・矛盾点を表にし、原作最終段(死霊の最後の言葉)を逐語で引用。
2. Seed `er026_seeds/in_a_grove/`(前例と同一形式・同一ファイル構成): `source_essentials`最大5件(`ending_reveal`+`withhold_until_end`、`setups_and_payoffs`、`key_roles`[`keep_name`: 多襄丸=Tajomaru・武弘=Takehiro・真砂=Masago の扱いを現行固有名詞ルールで判定]、`key_causality`[矛盾する3証言=各自が「自分が殺した/死んだ」と語る構造そのもの]、`free_to_cut`)、`source_quote`は原作最終段から逐語。**真相を一本化する記述を入れない**(essentialsの文言自体で「客観的真相を作らない」ことを担保)。視点: 原作は語り手不在の証言集=現行Z方式の「語りの視点保持」で、証言の一人称構造をどう扱うか(narrator枠=証言の見出し/枠付け、各証言=当該人物Voice)を設計し、現行Voice割当仕様(承認済み候補pool、narrator+登場人物、`er062`/`er063`のvoice assignment)で**証言者7人の割当案**を決定論的に提示(poolが足りない場合の現行仕様上の扱いを示す。新Voice探索禁止。極端な演じ分けを目的にしない)。
3. `CP_CHECK_01.md`: `build_cp_checklist`で機械生成したCPチェックリスト+§Bの起動コマンド列(`--story in_a_grove --run run_sf_prod_01 --mode real --approved-budget-jpy 70`、stage列は前例と同一)+Fable CP用の照合点(source_quote vs 原作最終段、essentials fail-closed検査=seed_checkのdry run結果)。
4. `BUDGET_PLAN_01.md`: 前例実績(告げ口心臓・猿の手)に基づく見積(Writer/support/KP/TTS b1b・a2/ASR/assemble)、上限70円、本作固有の増要因(証言者数→clip数・Voice数)。
5. STORY_REGISTRY登録+登録test PASS、seed_check dry-run(API 0で可能な範囲)PASSの証拠。
6. `docs/pm/RESULT_PACKET_FZIG1.md`(≤15行)。
7. Git: `git diff --cached --name-only`空確認→自分のファイルのみ明示`git add … && git commit -m "FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_01: 藪の中 原作・権利確認+Seed(essentials)+CP checklist+予算計画+REGISTRY登録(API 0)"`を1コマンド、`git add -A`禁止、他workerファイル不可、sources(原作本文)は前例に倣い追跡可否を確認。`git push origin HEAD:main`(FFのみ、拒否時fetch後再試行、force禁止)。hand-back: 権利確認結果、essentials 5件(逐語)、source_quote(逐語)、Voice割当案(7証言者)、seed_check結果、見積、commit sha、判断候補。
