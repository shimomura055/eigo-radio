# ROOT_CAUSE_01: Key Phrase 一般化・文脈意味・意味説明の包括対策 — 原因究明

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 委任_01(2026-10-23) / 状態: ROOT_CAUSE_DESIGN_IN_PROGRESS
範囲: read-only調査+小規模probe(API実費 約1.4円、gpt-6-luna、DEV専用、Production無変更)。ユーザー指示原文=`docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER.md`。

## 0. 結論(先頭)

`draw that line` の問題は「一般化指示が無視された」ことではなく、**現行の一般化・意味生成の仕組みが、そもそもその出力を作れない(または作らせない)構造**になっていたことが主因。個別の不具合ではなく、同じ構造から次の種類が量産時に発生し得る(現行path 78 KPの目視集計で、一般化の残り 8〜15件/78=10〜19%、慣用句の逐語glossが確定4〜境界例込み10件/78)。

| 項目 | 原因(確度) | 要点 |
|---|---|---|
| (a) 一般化されなかった | 構造(高) | canonicalizationの許可変換が閉集合で、`that→a`を作れない。作っても決定論validatorが却下する(実測: `draw a line`/`draw line`とも ok=False) |
| (c) Stdが逐語訳 | Prompt設計+(a)の連鎖(高) | gloss Promptが「key_phrase全体のすべての語の意味を反映」を要求→`that`を「その」と訳す。慣用句・比喩の扱い指示なし。`a line`入力なら「その」は5/5で消える(実測) |
| (b) Adv説明がnarrow | 部分的に確認(中) | 一般化形にしても「what is acceptable」型は3/5残る。記事文脈由来というより、LLMが辞書的な下位語義(draw the line at〜)を既定に選ぶ。出力は毎回揺れる |
| (d) Std/Adv不整合 | 構造(高) | 2レベルが完全に独立のpipeline(選定・canon・gloss各2call)。説明はAdv側glossを参照するだけで、Std側と共有する意味定義がない |
| (e) 既存ルールが効かなかった | 範囲・優先度・検査欠落(高) | 一般化ルールは「人称/所有格」と「活用形」だけが承認・実装済み。指示語/目的格代名詞/慣用句の意味は承認ルールも検査も存在しない |

## 1. 現行X/ZのKP工程(共通/別実装)

X・Zは**同一module**を呼ぶ。Z runnerは `er019_family_x_kp_explanation_01` を直接import(`er026_family_z_fiction_production_runner_01.py:1515,1532`)、gloss/canonicalizationも `er003_*` を共用(同:1284,1342)。Family固有の差は入力本文(news vs fiction)のみ。

| 段 | 実装 | model / Prompt | 入力 | 備考 |
|---|---|---|---|---|
| 1 選定(Std/Advで各1call) | `er105_kp_fulltext_selector_01.py`(backend `fulltext_p2`、:48-67) | gpt-6-luna、**正式Prompt 2は逐語固定**(sha256 a12896f4…)。『本文中の連続した語句だけ。変更・言い換え禁止(絶対条件)』『5語以内(絶対条件)』 | 記事全文 | 最大3件。CMU gate、数値placeholder precheck |
| 2 canonicalization(各1call) | `er003_key_words_canonicalization.py` + `er003_v1_translator_briefs/b1_p2_keywords_canonicalization_fulltext_prompt_template.txt` | gpt-6-luna | 記事全文+選定candidate | 許可変換=規則1 限定語除去/2 span内復元/3 人称・所有格→one's等/4 語形の基本形化。ここが唯一の「一般化」段(OPEN-454の方針『一般化は後段』) |
| 3 決定論validator | `er003_key_words_canonicalization.py:540-594`、`er105_kp_fulltext_selector_01.py:670-709` | API 0 | — | key_phraseは (i)display_phraseと同一 (ii)source_span内の連続部分文字列 (iii)閉じた人称表の1対1置換 (iv)活用形→基本形の1対1置換 のいずれか必須(Rule7) |
| 4 gloss生成(Stdの日本語意味) | `er003_key_words_gloss_alignment.py:575-612`(`build_user_message_corrected`)。fulltext itemは `current_japanese_gloss=null`→新規生成(:315-321) | gpt-6-luna、effort high | 最終key_phrase+source_sentence+**記事本文(参考)** | 実効Promptは§3(c) |
| 5 Adv英語説明(`explanation_en`) | `er019_family_x_kp_explanation_01.py`(Advのみ、Trial-02のB候補を逐語転記:54-82) | gpt-6-luna、effort medium | phrase+**source_sentence(1文のみ)**+gloss(『accuracy check only』) | 3件を1callで生成。語数≤15、新規Fact検査(:199-213) |
| 6 後段検査 | source gate(`er003_key_phrase_source_gate_01.py:85-109`はsource_spanで照合)、redundancy QA、gloss機械検査(record-only)、KP3V/kp_vote_check(音声側) | — | — | **指示語残り・慣用句の逐語訳・Std/Adv不整合を見る検査は存在しない** |

`used_form`=key_phrase(`er003_key_words_canonicalization.py:807`)。TTS入力・ASR期待文・試聴ページ表示はすべて `used_form`(`er019_family_x_audio_production_runner_01.py:1159-1170,1491-1502,2175-2180`)。KP-QUALITY-IMPROVEMENT-2ITEMS(OPEN-458 ①②)は「ASR票の数値・否定保護解除」と「CMU辞書登録語のみ選定」であり、**一般化・意味生成とは無関係**(確認: `OPEN_ITEMS.md:971`)。

## 2. 記事B(uk_train_speaker_playback run_nws_02)の実ログ追跡

証跡: `er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02/{a2,b1b}/key_phrases/`。

1. **選定**(`keywords_selector_raw_attempts.json`): 本文S29「The words draw that line simply」から `draw that line`(3語、`fulltext_exact_unique`)を採用。Prompt 2は本文一致が絶対条件のため、この時点で `that` を含む表層形になるのは**仕様どおり**。
2. **canonicalization**(`keywords_canonicalized.json` rank3): `key_phrase="draw that line"`、`normalization_reason=none`、全QA PASS。LLMのreasoning=「`that`を除くと文法的に不自然になります。**語を加えたり置き換えたりせず**、そのまま維持します」。すなわちLLMは『置換は許されない』と**正しく**読んで従った。
3. **validator実測**(本調査で実行、API 0): `is_valid_inflection_normalization("draw a line","draw that line")=False`、`validate_canonicalization_item("draw a line","draw that line","draw that line","other")` → ok=False(理由=『source_span内の連続部分文字列でも、人称一般化にも該当しない(Rule7)』)。`draw line`/`draw the line`/`draw one's line` も全てok=False。**仮にLLMが `draw a line` を出力しても、現行validatorは必ず却下する**(外側retry→OUTER_RETRY_EXHAUSTEDの経路)。
4. **gloss**(a2): 『「その」で that を表し、「線を引く」で draw a line の意味を表しています』→ `その線を引く`。b1bでは別callで `その境界線を引く`。
5. **Adv説明**(b1b `kp3_explanation_en_attempt1_*.json`): `to decide where the limit is between what is acceptable and what is not`(14語、上限15)。

## 3. 原因(a)〜(e)

### (a) `draw that line` が一般化されなかった原因

- **構造的原因(確度高)**: canonicalizationの変換許可は閉集合(規則1〜4)。規則1は先頭・末尾の限定語**除去**のみで、語中の `that`(draw **that** line)は除去すると `draw line`(非文法)となり、かつvalidatorが非連続として却下。規則3の人称表(`er003_key_words_canonicalization.py:431-449`)は `my/your/his/her/its/their/our/you/they/he/she/…` のみで、**指示語(this/that/these/those)も目的格(him/her/them/it/me/us)も表に無い**。LLM提示の列挙もこれと一致(template:11『列挙外の置換は決定論検証で却下されます』)。
- **経緯(確度高)**: JRE委任_02(commit 1d501f74d)で、Z melosのKPが `him→someone` を過剰に一般化して決定論validatorに却下されOUTER_RETRY_EXHAUSTEDになったため、templateに『目的格はそのまま残せ』を追記して解消した。この是正は妥当だったが、結果として**目的格・指示語の一般化経路が閉じたまま**運用されている。
- **Prompt誘導(確度中)**: template:7『まず「display_phraseは既にそのままで自然で、単独で聞いても意味が分かる最小十分な単位か?」を自問。YESなら完全に同一にせよ』。`draw that line` は文法的に自然なため、この自問がYESに倒れる。『学習用の辞書形か』という問いは無い。
- **選定側ではない**: Prompt 2(逐語・本文一致絶対)は一般化を担わない設計(OPEN-454『一般化は後段』)。選定を変える案は逐語固定違反なので採らない。

### (b) Adv説明が narrow になった原因

- 実測(probe-01、同一Prompt・同一model、各5回): 現行(`draw that line`入力)=『set a limit between what is acceptable and what is not』系 3/5(残り2/5は『decide where a (the) boundary should be』)。一般化形(`draw a line`入力)にしても 3/5 が『acceptable』を含み(2/5は『show where one thing ends and another begins』)、**一般化だけでは直らない**。
- したがって「記事文脈に引っ張られた」というより、**LLMが辞書的な代表語義(draw the line at X=許容限界を決める)を既定に選び、毎回揺れる**というのが実態(確度中。記事内の『ルールで許容される音』という話題の影響は否定できないが、`that`を外しても残るため主因ではない)。
- 構造要因: 説明call(`er019_family_x_kp_explanation_01.py:164-178`)の入力は **phrase+1文(S29のみ)+日本語参考意味**で、記事全体も前後文も無い。Prompt(:55-82)は『one sentence, plain words, easier than the phrase itself; not a dictionary definition』『different contextでも通用』とあるが、**『中心的な1義を、条件を足さず最も一般的な形で』という指示は無い**。ユーザー期待(`to establish a clear boundary or limit`)は『許容/不許容の判断』という条件を含まない広い中心義。
- 注意(誠実な開示): 現行出力は辞書上は正しい語義の一つであり「誤訳」ではない。ユーザー要求③(汎用的・中心義1つ)に対して**狭すぎる/条件付き**という品質問題。

### (c) Stdが逐語訳になった原因

- gloss Prompt(`er003_key_words_gloss_alignment.py:586-604`)は『最終的なkey_phrase全体(目的語・補語・修飾語を含む**すべての語**)の意味と過不足なく一致』『key_phrase全体の意味を反映できている場合のみPASS』を要求する。LLMはこれを『全語を訳出』と読み、`that`→「その」(reasoning実文:『「その」で that を表し』)。
- 承認済みglossルール(『直訳調…は避けてください』)は**文体(硬い漢語)**の規則で、慣用句の語義選択ではない。位置もPrompt末尾の『日本語グロスの規則』で、前半の『すべての語を反映』の方が強く効く。慣用句・比喩を扱う文言・例は無い。新規生成ブロック(:315-321)も『source_sentenceは語義選択のために使う』のみ。
- 実測(probe-01 P3/P4): `draw that line`入力→「その線引きをする」3/5・「その境界線を引く」2/5(**5/5で「その」が混入**)。`draw a line`入力→「一線を引く」4/5・「境目をはっきりさせる」1/5(**「その」0/5**)。つまり本件のStd逐語化の大半は(a)の連鎖で、一般化されればgloss Promptは**無改変でも**かなり改善する。
- 慣用句の逐語glossは(a)と独立にも発生している(probe-02、現行Prompt・各3回再生成): `reach for one's wallet`→「財布に手を伸ばす」系 3/3(慣用義は『(お金を)払う』)、`shine a light on`→「～に光を当てる」2/3(1回のみ「～を明らかにする」)、`fire the starting gun`→「スタートの合図を出す/鳴らす」3/3、`Carry the Load`→「荷物を運ぶ」3/3、`on the throne`→「王座に就いている/君臨している」混在。**慣用句・比喩の中心義に寄せる誘導が現行Promptに無い**(確度高)。

### (d) Std/Adv間の意味解釈が一致しない構造的原因

- Std(a2)とAdv(b1b)は**選定から別call**で、同一記事でもKP集合が異なる(78KP中、同一run内で両レベルに現れた同一KPは7件=Adv 33件の21%)。同一phraseでもgloss callは別(`draw that line`: Std「その線を引く」/Adv「その境界線を引く」)。
- Advの英語説明はAdv側glossを『accuracy check only, do not translate literally』で受けるだけ。**Std/Advで共有する「中心義」データは存在しない**。実際の不一致(同一run同一KP 7件中): `reach for one's wallet`(Std「自分の財布に手を伸ばす」=逐語 / Adv説明『to get ready to spend money』=慣用義)、`draw that line`(Std「線」/Adv「境界・限界」)=2/7。他5件は整合(`articles of incorporation`・`letter of introduction`等の辞書語/`pump one's fist`等の具体動作)。
- ただしStd/AdvはCEFR別の独立生成が既存仕様(Stdは日本語意味、Advは英語説明)。**共有すべきは『同じ方針で同じ中心義に着地するPrompt原則』であり、データ共有機構を新設する必要は小さい**(DESIGN_01で扱う)。

### (e) 既存ルールが実効性を欠いた理由(単純な再指示では直らない理由)

| 既存ルール | 実効性を欠いた理由 |
|---|---|
| 人称・所有格の一般化(ER-011-NO18、承認2026-09-02) | 閉じた対応表。承認範囲がそこまで。指示語・目的格は対象外 |
| 語形の基本形化(OPEN-454 規則4) | 活用形↔基本形のみ。冠詞・指示語の置換は含まない |
| 規則1 限定語除去 | 先頭/末尾のみ。語中は不可(validator Rule7が連続部分文字列を要求) |
| 『直訳調は避ける』(承認gloss規則) | 文体規則で、慣用句の語義選択ではない。『全語を反映』に埋もれる |
| 説明Promptの『different contextでも通用』 | 抽象的要請のみ。『条件を足さず中心義』の具体指示・例が無い。入力は1文のみ |
| Meaning Preservation Rule | 語を**削る**場面のみ対象。置換・意味選択は対象外 |
| 検査(source gate/QA/redundancy/KP3V) | いずれも『本文実在』『音声がテキストと一致』を見るもので、指示語残り・逐語訳・Std/Adv不整合を見る検査は無い |

## 4. 過去の同種問題・Trial・承認済み対策との関係

- ER-011-NO18(2026-09-02 PRODUCTION_WIRED): 人称・所有格の閉集合一般化を導入(`catch their attention→catch someone's attention`)。今回の問題は**その閉集合の外**。
- KPFT/OPEN-454(2026-10-22 PRODUCTION_WIRED): fulltext_p2へ移行。**旧db_hybrid経路は辞書見出し形で供給したため `inherit_selection_normalization` で `pull someone under`・`sentence someone to death`・`lose trust in someone` 等が出ていた**(旧path census参照)。新pathは本文surface起点のため一般化の責務がcanonicalizationへ移ったが、許可変換が閉集合のまま=**一般化能力の後退**(本調査で新規に確認)。
- FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02(`docs/research/FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02/TRIAL_RESULT_02.md:72`): 独立した一般化LLM工程(Haiku)はREJECTED(適用漏れ22/70)。結論=『新たな一般化LLMを足すより既存のcanonicalization経路で担う方が合理的』。**本設計もこの結論に沿い、新規LLM callを追加しない**。
- KP-QUALITY-IMPROVEMENT-2ITEMS(OPEN-458 ①②)・ASR-QUALITY-2ITEMS(OPEN-471/472、並行Trial実装中・未編集): 音声/ASR側。本件との接点はDESIGN_01 §音声/ASR側整合。
- 記事Bの当該KPはOPEN-467に品質未解決事項として追記する(成果物は保全)。

## 5. 定量(API 0・機械+目視)

データ: 現行path(fulltext_p2、2026-10-22/23の正式Production run)=**15 run・8記事(coffee_prices/ig_nobel_2026/prix_pascal/small_bag/tesla_spacex/uk_train/melos[Z]/the_open_window[Z])・78 KP(X 48/Z 30、Std 45/Adv 33)**。`census_items_01.json`(全項目)・`census_labels_01.json`(ラベル)・`kp_census_01.py`(再現script)。追加で旧path(db_hybrid、paycheck/boredom/manga/middle_east+melos旧run)の参考分を含む重複排除142 KP・12記事(`census_items_03_unique.json`)。判定は**目視1名(Sonnet)+機械flag**で主観を含む(境界例はborderlineとして区別。Opus/Fableの再確認対象)。

| 分類(現行path 78 KP) | 件数 | 率 | 内訳 |
|---|---|---|---|
| 一般化不足:指示語残り | 2 | 2.6% | `draw that line`(Std・Adv両レベルで同記事) |
| 一般化不足:目的格代名詞残り(`him`等) | 6 | 7.7% | Z melos `pulled him under`/`sentenced him to death`(全てZ) |
| 一般化不足:時制未原形化 | 1 | 1.3% | Z `pulled him under`(reason=none、上記と重複) |
| 表記:タイトル/文頭の大文字残り | 6 | 7.7% | `Carry the Load`×3、`For once`×2、`A most peculiar visitor`(template:14が大小文字の変更を禁止) |
| 所有格`its`残り(軽微) | 1 | 1.3% | `turn on its head` |
| **一般化不足 合計(指示語+目的格+時制)** | **8** | **10.3%**(Z 6/30=20%、X 2/48=4.2%) | 大文字・its含めると15件=19.2% |
| 記事固有/再利用性が低い(文脈名詞が残る) | 11 | 14.1% | `three times as much energy`・`bound to the protein`・`question shaped like a trophy`・`spread through the whole market`・`vote as a separate group`・`without asking for another promise`等(選定段の性質。一般化段の直接対象外だが開示) |
| 逐語gloss(確定) | 4 | 5.1% | `reach for one's wallet`・`shine a light on`・`draw that line`×2 |
| 逐語gloss(境界例) | 6 | 7.7% | `fire the starting gun`・`on the throne`×2・`Carry the Load`×3 |
| Adv説明に文脈/人称が混入 | 4 | 12.1%(Adv 33件中) | `rise above the other voices`(than the other voices)・`he`/`him`混入×2・`draw that line`(acceptable) |
| Std/Adv不整合(同一run同一KP 7件中) | 2 | 28.6%(n小) | `reach for one's wallet`・`draw that line` |
| 5語超 | 0 | 0% | 全件5語以内(既存ルールは機能) |
| 同一phraseのgloss揺れ | — | — | `pump one's fist`が3通り、`hold out`が3通り(同phrase・異run) |

所見: (1) **5語・本文由来・語頭語尾の限定語除去は機能している**。(2) 欠けているのは『目的格/指示語の不定化』『慣用句の中心義gloss』『Adv説明の中心義化』。大文字残りは仕様上禁止(template:14)のため現状は仕様どおり(是非は設計で扱う)。(3) Zは物語本文のため目的格代名詞の発生率が高く、`him`残りは全てZ由来。

## 6. 費用・実行記録

probe-01(原因切り分け: 4条件×5回=20call、一般化形の効果検証)0.5633円+予備1回0.1665円、probe-02(慣用句gloss 4記事×3回=12call)0.6636円=**約1.39円**(gpt-6-luna、本番builder・本番Prompt無改変、DEV script `kp_probe_01.py`/`kp_probe_02.py`、結果=`kp_probe_01_result.json`/`kp_probe_02_result.json`)。上限10円内。Production・Prompt・閾値・flag・記事B成果物は無変更。限界: probeは1記事中心・各3〜5回で統計的に弱い(傾向確認のみ。Trialで再測定する)。
