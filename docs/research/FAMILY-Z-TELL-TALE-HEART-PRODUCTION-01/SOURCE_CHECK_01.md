# SOURCE_CHECK_01 (原作確認・登録、FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01 委任_01、2026-10-24、API 0)

## 出典・権利
- Project Gutenberg eBook #2148 "The Works of Edgar Allan Poe — Volume 2"(Edgar Allan Poe、credits: David Widger)。取得 2026-10-24、HTTP 200(`https://www.gutenberg.org/cache/epub/2148/pg2148.txt`)。pg2148.txt sha256 = `159989d413c3240447627d0964a15ad10e4535ba1d25e0468c02f9ecdab9e12e`(10,696行)。**『告げ口心臓』は同巻所収の1作品**(本文 l.9279-9483。次の作品 BERENICE は l.9488 から)。Gutenberg冒頭: 『free for use ... in the United States and most other parts of the world ... with almost no restrictions』。Gutenberg Licenseに従い利用(商標のProject Gutenberg名は作品名の出典表記として記録に使うのみ、頒布物にlicense全文は含めない[本文のみ引用])。
- 作品発表: 1843-01 *The Pioneer*(en.wikipedia.org/wiki/The_Tell-Tale_Heart、HTTP 200、infobox 'The Pioneer, Vol. I, No. I ... January 1843')。原作者 Edgar Allan Poe 没 1849-10-07(en.wikipedia.org/wiki/Edgar_Allan_Poe、HTTP 200、'October 7, 1849'を確認)。
- 日本: 死後50年(没年翌年起算、1899-12-31満了)+戦時加算3,794日 = **1910-05-22**(`datetime.date(1899,12,31)+timedelta(3794)`、保守的な上限の計算値)。2018年の70年化は満了済み作品に遡及しない。日本でパブリックドメイン(最終的な法的判断ではない)。米国も1931年前の出版(1843)でPD。コード側 `TELL_TALE_HEART_RIGHTS_BLOCK`(`er026_family_z_fiction_production_runner_01.py`)、`check_rights_gate` PASS確認済み(登録test)。権利条件=**Public Domain(US)・Gutenberg License(ebook自体は無償・ほぼ無制限)**。
- 利用テキスト: `er026_seeds/the_tell_tale_heart/story.md`(pg2148.txt l.9279-9483の本文、空白正規化と斜体記号 `_..._`(`very`/`louder!`の2か所)の除去のみ。**2,076語/18段落**)。sha256は `er026_seeds/the_tell_tale_heart/SOURCE_PROVENANCE.json`。登録testで raw extract と story.md が語・順序とも一致することを検査。第三者の翻訳・翻案・あらすじは不使用。
- 版の注意: Gutenberg本巻は全集で(版の来歴は未確認)、Gutenberg冒頭『Redactor's Note—Some endnotes are by Poe and some were added by Griswold』あり。本作のテキストには初出(1843)との細部の異同があり得るが、**筋・結末・主要台詞は同じ**(出典としてはGutenberg #2148の本文に忠実)。

## 原文の要素確認表(原文照合、行はpg2148.txt)
| 要素 | 原文での内容 |
|---|---|
| 語り手 | 一人称・名なし。『True!—nervous—very, very dreadfully nervous I had been and am; but why will you say that I am mad?』。聴覚が鋭い(『I heard all things in the heaven and in the earth』)ので狂っていないと主張。聞き手『you』に語りかける |
| 老人 | 同居の老人(名なし)。語り手は老人を愛している・恨みも金への欲もない。動機は**老人の目**(淡青色で膜がかかった『vulture eye』)のみ |
| 7夜の偵察 | 毎夜ちょうど真夜中、ラッチを回し、完全に閉じたランタンを入れ、細い光線を目に当てる。目はいつも閉じていて実行できず。毎朝、老人に温かく声をかける |
| 8夜目 | 慎重に戸を開け、得意になって笑う→老人が動く。暗闇で親指がランタンの錫の留め具で滑り、老人が『Who's there?』と叫ぶ。語り手は1時間動かない。老人のうめき(死の恐怖) |
| 心臓の音 | 光線が開いた目に当たる。『a low, dull, quick sound, such as a watch makes when enveloped in cotton』=老人の心臓。速く大きくなり、隣人に聞こえると恐れた語り手が叫んで飛び込む |
| 殺害・隠蔽 | 老人は一度だけ叫ぶ。床に引きずり下ろし重いベッドを倒す。心臓は止まる。遺体を解体し、床板3枚を外して隠し、血痕なし(桶で受けた) |
| 警官 | 午前4時、3人の警官が訪問(隣人が悲鳴を聞いた)。語り手は愛想よく招き入れ、悲鳴は夢の中の自分のもの、老人は田舎に出かけたと説明。家中を案内し、老人の部屋に椅子を置き、遺体を隠した場所の真上に座る |
| 幻聴の増大・自白 | 警官は雑談。語り手は青ざめ、耳鳴りがやがて『the noise was not within my ears』。低く鈍い速い音が増大し、早口・大声・歩き回り・椅子をきしませる。警官は聞こえないふりか笑って談笑している(と思い込む)。『Villains!... dissemble no more! I admit the deed!—tear up the planks!—here, here!—It is the beating of his hideous heart!』で終わる |

結末の開示タイミング(音が老人の心臓であること・自白)は最終場面まで先回りしない(Seedの withhold_until_end、Preview/Comment lintのspoiler語に反映)。音が現実か語り手の妄想かは原作どおり書かない(Seed ending_reveal.meaning/conversion_planで明示)。

## 維持項目(Seed `source_essentials`、validate_source_essentialsで検査済み、上限5件)
- ending_reveal(1): 語り手の自白で終わる。`source_quote`=`It is the beating of his hideous heart!`(原作最終段落に逐語)。
- setups_and_payoffs(2): ①鋭い聴覚の主張→最終場面で語り手だけが聞く心臓の音 ②淡青色の『vulture eye』が動機・7夜閉じていた→8夜目に開いた目と心臓の音→殺害。
- key_causality(1): 目への執着→7夜の偵察→8夜目の目覚め・光線・心臓の音→殺害・床下への隠蔽→警官の来訪→音の増大→自白。
- key_roles: 語り手・老人・警官3人はいずれも**名なし(keep_name=false)**。原作に人名なし→`forbidden_names`は空list。
- free_to_cut: 語り手の自己弁護の繰り返し、老人の想像上の独白、死の擬人化、遺体処理の詳細、警官の正式な名乗り。

## ユーザー指示の維持要件との対応
- 老人の目への執着→維持(setups_and_payoffs②)/7夜の偵察→維持/8夜目の殺害と床下への隠蔽→維持/警官来訪→維持/幻聴の心臓音の増大→維持/自白→維持(ending_reveal)/『狂ってなどいない』という自己主張→維持(setups_and_payoffs①、seed_elements[0]、conversion_plan)/恐怖の源=心理と音→維持(conversion_planが『fear comes from the narrator's calm, over-confident voice and from sound and silence』)。
- 遺体解体の描写は原作の出来事だが、グラフィックな詳細はfree_to_cut(『床下に隠した』の1文に圧縮可)。『重要な出来事』の維持対象は『殺害→床下への隠蔽』であり、解体そのものではない。これは**Seed内の圧縮指示**(新仕様・Prompt変更ではない)。Fable確認事項(CP_CHECK_01 §C)。

## 登録(data表のみ、ロジック変更0)
- `STORY_REGISTRY["the_tell_tale_heart"]`・`TELL_TALE_HEART_RIGHTS_BLOCK`(`er026_family_z_fiction_production_runner_01.py`)、`STORY_VOICE_ROSTER`/`STORY_SPEAKER_CONFIG`/`STORY_LINT_CONFIG`(`er062_family_z_structure_01.py`)、`STORY_MAIN_CHARACTER`(`er062_family_z_writer_01.py`)にentry追加のみ。既存5作品のentryは無変更(`git diff --numstat`: runner +60/-1[`# Story Registry (...)`のコメント行に作品名を追記]、structure +43/-0、writer +3/-1[`STORY_MAIN_CHARACTER`辞書の閉じ括弧行に新entryを追記])。
- 登録test `er026_family_z_story_registry_tell_tale_heart_test_01.py` **23 tests OK**。既存の登録test(猿の手・賢者の贈り物・二十年後・開いた窓)+`er062_family_z_source_essentials/speaker_roster_story/voice_assignment`+`er063_family_z_audio_01_test_01`+`er026_family_z_fiction_production_runner_01_test`+`er062_family_z_writer_01_test_01` 合計294 tests OK(PASS)。

## Voice割当(決定的割当規則 `derive_dialogue_voice_tts_names`、pinなし、正式Voice表 FAMILY-Z-VOICE-PRODUCTION-WIRING-01 APPROVED_FOR_PRODUCTION 2026-10-23)
| 話者 | 性別 | 登場順 | Voice |
|---|---|---|---|
| narrator(語り手本人[一人称の『I』]の引用台詞も含む) | — | — | **Aoede** |
| old_man(老人: `Who's there?`) | male | 1 | **Algieba** |
| officer(警官3人を1話者) | male | 2 | **Schedar** |
- 『ホラー・一人称語りで会話が少ない作品』への対応: 原作の直接話法は老人の『Who's there?』と語り手の最後の絶叫のみ。**語り手本人の台詞は narrator(Aoede)が読む**(一人称の地の文と同一人物のため。`attr_roster_text`で明示)。警官は原作で直接話法がない(間接話法)ため、Writerが台詞化した場合のみ officer が使われる。**登場順はWriter出力(Adv/Std初出順)確認後に、plan前に訂正し得る**(『猿の手』と同じ手順、data表の順序のみ)。Charon(Adv補助)は別枠。
- 既存3パート構成(`er062` Part構成)・速度仕様v2(Z会話速度: 会話clipのみ atempo、Std限定6%後処理)がそのまま適用される(**仕様変更・効果音・新Promptは追加していない**)。会話clipが極めて少ない作品のため、極短clip速度Gate(SHORT-CLIP-SPEED-GATE-01、OPEN-496)の対象clipが生じる可能性は低いが、生じた場合は既存Gateの仕様どおりに扱う(Gate緩和なし)。

## 懸念(Fable参考、次委任の初回run前に認識)
1. **決定論話者判定の窓キーワード**(`old_man`/`officer`のspeech tag)は『猿の手』の教訓(起動2: 人名単体だと誤判定→会話タグ型へ変更)を反映済み。一人称『I said』『I shrieked』は決定論の対象外(LLM判定=narrator)。plan stageで`DIALOGUE_ATTRIBUTION_MISMATCH`が出た場合のみ、data表の修正を**まとめて1回**行い、起動間隔150秒を守る(RESTART_STORM回避)。
2. **Comment lint**(spoiler語)は結末(自白・床板を剥がせ・自分の心臓・幻聴)に限定。殺害・床下隠蔽は後半Commentに現れ得るため禁止語にしていない(『猿の手』起動3の教訓)。
3. **Writerが名前を付ける恐れ**: `STORY_MAIN_CHARACTER`を『the narrator (who stays unnamed, as in the original)』としたため、REVISE promptは `only the narrator (who stays unnamed, as in the original) may have a personal name`。Seed conversion_planにも『Neither the narrator nor the old man nor the officers have personal names』と明記。
4. 本作は2,076語の原作を約400語に圧縮する。短い独白ホラーなので、『猿の手』(3,934語→434語)より圧縮率が低く、原作忠実性のCP(CP_CHECK_01 §C)で8項目を確認する。
