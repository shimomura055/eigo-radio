# THEME_PACKAGE_NOTE_01 (FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01 委任_02)

作成: 2026-10-29 / LLM・TTS API 0円、有料stage未起動、Productionコード変更なし。
成果物: `docs/research/FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01/theme_packages/surname_choice_package_01.json`(slug `surname_choice`)、取得ログ `FETCH_LOG_02.jsonl`、`.gitignore`(出典原文dir追加)。

## 1. 追加取材の結果
- **V1(男声)は「実在男性の自己記述(再構成)」で成立。ただし1名**: note の同一著者の無料2記事(YSC-NOTE-01 `https://note.com/miyamagi44/n/n2b0030c992aa`、YSC-NOTE-02 `.../nef7c361fdd57`)。アラフォーの男性。4年前に婿養子になって苗字が変わり、妻の実家で8年同居。苗字が変わることに抵抗はなく、自分の親もすんなり受け入れ、義両親の方が何度も確かめてくれた。自分の親は寂しがっていない。同居は「無理をしない」。ひとりの時間は少ない。複数本の別人記事は見つからなかったため【合成】ではなく【実在個人の自己記述(再構成)】。fallback(兄弟・親族型)は不要だった。
- **注意(判断候補B)**: この男性は**婿養子(養子縁組あり)**。婚姻届で妻の氏を選ぶだけの人ではない。Packageの`distinctions`に「妻の姓を選ぶ(養子縁組なし)」と「婿養子」を分けて定義し、V1は婿養子と明記した。ユーザー原文§4(男性が妻の姓を選ぶ話を主役)の範囲内と判断(男性の苗字が妻の家のものになる経験)。「養子縁組なしで妻の氏を選んだ男性本人」は取得範囲に無かった。
- 取得範囲: note=ハッシュタグ3(`妻の名字`/`婿養子`/`婿入り`、`妻の姓`は404)+記事4=計8ページ(上限8)。ママスタBBS=検索結果は動的描画で結果取得不能(計3ページ、有用0)。e戸建て・インターエデュ=robotsのみ確認(e戸建ては検索`/search/`を禁止のため不使用、スレ発見手段なし)。ガルちゃんは委任_01の取得キャッシュ(トピ6317841、#1〜#2500)を再利用(新規取得なし)。

## 2. 3 Voiceの区分と根拠ID
| Voice | 人物 | 区分 | 根拠ID |
|---|---|---|---|
| V1 Puck(男) | 婿養子になって妻の家の苗字になった父親(当事者) | 【実在個人の自己記述(再構成)】 | YSC-NOTE-01, YSC-NOTE-02 |
| V2 Zephyr(女) | 息子が妻の姓にすると聞いて寂しさを感じた母親 | 【実在個人の自己記述(再構成)】(ガルちゃんトピ主) | GC6317841-C1, C176, C379 |
| V3 Schedar(男) | 本人たちの意思を尊重しつつ、双方の親の気持ちも考える親世代の第三者 | 【合成】 | C170, C1324, C859, C1089, C387, C1426, MULTI-A(C2/3/6/7/8/10/11/13/14/17/18/23/24) |
- V2の前提は「相手の両親の希望を息子が受け入れた」。人物シート(TWO_a・`voice_basis.voice_2.caveat`)に事情として明記し、一般化していない。変化(寂しさ→離れていく感覚→子離れ→適度な距離)は実在の#1→#176→#379の範囲。
- V3の性別は、性別不明コメント(#170/#1324/#859/#1089)の合成で男声スロットに整合。妻側の女性コメント(#387/#1426)は意見(O)としてだけ参照し、V3自身の経験にしていない。

## 3. 差別化
- V1=選んだ側の当事者。争点は「抵抗の無さ」「家ごとのあたりまえの違い」「同居の距離感」。語りは穏やか・事実を順に置く(一人称「僕」)。
- V2=継がれる側が揺れる母。争点は「姓より息子が離れていく感覚」と「古い価値観への気づき」。気持ちの吐露から入り、寂しさは少し残る(一人称「私」)。
- V3=当事者でも渦中の親でもない第三者。争点は「相談の有無」「当然という態度」「身内の例」。V2に反論せず、条件をつけて語る(一人称「自分」)。
- V1の「自分の親は寂しがっていない」はV2の寂しさと対になる実在の別経験で、賛否の繰り返しにならない。V1/V2/V3で「寂しさを理解する」言い回しに収束しないよう、arc_jaに結びの禁止事項を入れた。

## 4. 使わなかったユーザー候補
- 「自分の姓を選んだ女性(#387/#1426)」: 女声スロットが1つ(V2)で、V2は母(トピ主)が実在の変化を持つため主役にしない。経験としては使わず、V3の意見(THREE_e/THREE_f)の参照素材だけに使用(最終報告でFableが開示)。
- #142(22歳の長男の母)・#1052(兄が婿に行った家族)・#531/#125/#1170 等: 同一人物でないため人物シートに混ぜず不使用(#1052は兄弟型fallback候補として保留)。
- 有料記事(`right_knot2175`)は取得ページが有料記事の公開プレビューだった。内容は使わず(Package・source_rawに不使用)。取得ログのとおり記録。

## 5. 制度論の扱い
- 中心テーマに置かない。`world_frame.shared_premise_ja`で選択的夫婦別姓の制度論・女性が夫の姓を選ぶ一般論は中心にしないと明記し、`fact_scopes.out_of_scope`に統計・制度を入れた。
- 法務省 https://www.moj.go.jp/MINJI/minji36.html (夫の氏を選ぶ割合令和6年約94.1%)は`facts[FACT-MOJ-01]`に固定のみ。Voice本文では使わない(`known_fact_id`は空)。使うなら正式工程のFact確認で再照合が必要(Y runnerに専用Fact stageなし。PRODUCTION_PLAN_01 A-2)。

## 6. Package検証結果(API 0)
- `er121_family_y_text_core_01.validate_theme_package` → `[]`(違反0)。`load_theme_package` OK(sha256 `d5a0c9831092...`、file_bytes)。`er121_family_y_structure_01.theme_package_is_post_based` → True(全experienceにsource_ids非空→承認済みVoice説明文が表示される)。`lead_inputs` → source=package。`intro_spec` → derived(SNS先例と同じ。intro検査の`object_words`=婿養子・姓を継ぐ)。
- 先例SNSとのschema差異: 必須キーは全充足(`REQUIRED_SHEET_KEYS`/`REQUIRED_WORLD_KEYS`/`REQUIRED_SPEECH_KEYS`)。追加キー(runnerは読まない): `sources`/`facts`/`voice_basis`/`tension_notes_ja`。任意の`lead_premise_ja`/`lead_scope_lines`は設定(先例SNSは未設定)。`restricted_voice_ids`は空(制限出典なし)。
- Voice性別とスロット整合: V1男/V2女/V3男=`FIXED_VOICE_SLOTS`(structure:60-64)と一致。
- Package自身の逐語混入検査: Package全文を`verbatim_report`(20字連続)で出典原文と照合し、修正後ヒット0。
- 出典原文は`er121_output/family_y_production_01/surname_choice/source_raw/`(`.gitignore:66`でignore確認済み)。Package`source_dir`はこのdirを指し、runnerの連続一致検査が有効になる。

## 7. 次の有料run案(Fable承認後。未起動)
- 前提: 未commit差分(er121 runner/er120/er128のNUANCE配線途中)がcommit・Fable受入されるまで有料runは開始しない(PRODUCTION_PLAN_01 A-4)。開始時にSTOP確認(`tools/stop_scope_check_01.py`)。
- 1回目(前半・rc=4でHR待機): `py er121_family_y_runner_01.py --mode real --slug surname_choice --run run_01 --theme-package docs/research/FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01/theme_packages/surname_choice_package_01.json --approved-budget-jpy 130 --stages seed_check,text,translate,support,kp`
- 2回目(HR確定後、完成段を1起動): 同引数で `--stages tts_b1b,tts_a2,gate,assemble,pages,page_verify`(OPEN-480回避。provision_shellはY runnerのSTAGESに無い)。
- 予算提案: 見積85〜110円・悪化時〜130円(PLAN A-3)。`--approved-budget-jpy 130`(Cap170以内)。警告閾値100円を超える見込みのため、**超過見込みで新規API前にSTOPする可能性があり、`--ack-warn-threshold`はFable確認後に付与**。本文再生成は+約60円のため、Packageを確定してから1回で通す。
- 注意: `world_frame.title_ja`(仮題「妻の姓を選ぶ、それぞれの声」)は、runnerが記事タイトルとして**そのまま使う**(text_core:2075。`title`生成stageなし)。ユーザー原文§1「最終タイトルは正式Productionで決定」との整合は、Fableがtitle_jaを仮題のまま通すか、正式な決定手順を別途定めるか判断(判断候補)。

## 8. 委任_03 タイトル確定・V1重み付け(2026-10-29)
- 確定title_ja=「夫が妻の姓を選ぶとき、それぞれの声」(Std/Adv共通、runnerは単一title_jaを使用: text_core:2075)。理由: Family Y先例は全て「<争点>、それぞれの声」(SNS=Package title_ja・宅配=REVISION_SCRIPT_01:103・TRIAL_03/WORLD_SETTING_01:104・規則文=er110_family_y_persona_pipeline_01.py:237「25字以内・争点が分かる・『それぞれの声』で終わる」)。Fable案「夫が妻の姓を選ぶとき」を保ち末尾のみ先例体裁に合わせた最小調整(17字、疑問形/制度論なし)。
- V1(sheets.voice_1)のpersona_sketch_ja/arc_ja/claim_core_jaを調整: 語りの中心=苗字が変わることへの本人・双方の親の受け止めと周囲の反応、婿養子は明示、同居は背景(experiences追加・変更なし)。Package sha256 d5a0c983...→d1bc9fe2...、validate_theme_package=[]。

## 9. 委任_04 リード矛盾の是正(2026-10-29)
- 是正理由: 旧リード第2文「妻の姓を選ぶのは…養子縁組は伴わない」は制度定義であり(ユーザー原文§4「中心テーマを制度解説に置き換えない」に反する)、直後のV1が「婿養子として妻の姓を名乗る」と語る矛盾を聞き手に与えた。
- 変更: Packageの`lead_premise_ja`(「妻の姓を選ぶ」→「妻の姓を名乗る」)・`lead_scope_lines`(定義文を撤去し「婚姻届で妻の姓を選ぶ場合も婿養子になる場合も両方を自然に含める・定義説明はしない」)・`distinctions`2件(「養子縁組は伴わない」を撤去し、婿養子も妻の姓を名乗る形の一つと明記)。Voice sheets/experiences/sourcesは不変。Package sha d1bc9fe2...→fa2c7a58...、validate=[]。
- 再生成経路: runnerにlead単体再生成が無いため、`--reuse-manifest`(y_reuse_v1: Voice R0=run_01の確定Voice 3本、人物紹介3本)を指定して新run_02へ。Voice本文・人物紹介は逐語同一で再利用(Gate PASS記録再利用)、Lead新規生成。Closingはキャッシュ鍵にPackage shaを含むため再生成され本文が変わった(案Bの固定注入は本件非登録)。以降translate/support/kpも新runで再実行(run_01は旧版の記録として残置)。
