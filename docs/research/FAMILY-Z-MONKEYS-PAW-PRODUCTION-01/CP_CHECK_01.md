# CP_CHECK_01 (FAMILY-Z-MONKEYS-PAW-PRODUCTION-01 委任_01、2026-10-24)

前半(§A)=着手時の既存仕様整合確認(委任文§0の1〜7)。後半(§B)=原作忠実性チェックポイント(委任_03で最終稿確定、Fable確認待ち)。

## §A 着手時の整合確認
| # | 確認事項 | 結果(照合箇所) |
|---|---|---|
| 1 | 正式Production経路 | er026 runner `er026_family_z_fiction_production_runner_01.py --story the_monkeys_paw --run run_sf_prod_01 --stages ...`(『二十年後』『賢者の贈り物』と同一経路)。E2E_STAGES順=seed_check,writer,std_adjust,plan,support,kp,tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify。作品追加は `STORY_REGISTRY["the_monkeys_paw"]`・`MONKEYS_PAW_RIGHTS_BLOCK`(runner)、`STORY_VOICE_ROSTER`/`STORY_SPEAKER_CONFIG`/`STORY_LINT_CONFIG`(er062_structure)、`STORY_MAIN_CHARACTER`(er062_writer)のdata表のみ(ロジック変更0)。完成段は `provision_shell,gate,assemble,pages,page_verify` を1起動(OPEN-480)。 |
| 2 | Std/Adv構成・長さ・Voice | 3パート構成、本文330-470語(`ACCEPT_WORD_RANGE`)。Voice=正式Voice表+決定的割当規則(er062 `assign_dialogue_voices`)、pinなし。Roster(原作の発話者のみ5名)の登場順はAdv/Std両方の初出順(Adv r2・Std std_adjustとも同じ): 軍曹(morris)1、Mr. White 2、Herbert 3、使者(visitor) 4、Mrs. White 5(女性Pool1番)。割当: narrator=Aoede、morris=Algieba、mr_white=Schedar、herbert=Fenrir、visitor=Orus、mrs_white=Zephyr(Charon=Adv補助、既存)。人選の個別例外なし。 |
| 3 | 原作忠実性基準 | Seedに`source_essentials`(ending_reveal/key_roles[keep_name: Mr. White・Mrs. White・Herbert]/key_causality/free_to_cut、維持必須5件=上限ESSENTIALS_MAX_ITEMS)を記入し`validate_source_essentials`でsource_quoteが原作最終段落に逐語で在ることを検証済み(登録test PASS、seed_check stage PASS)。維持必須=猿の手と3つの願い/危険の警告/White一家の人物関係/願いと悲劇の因果/終盤の緊迫/最後の願いと余韻の結末(ユーザー原文§3-1)。 |
| 4 | Key Phrase | A-1・課題②=PRODUCTION_WIRED(commit 4128fffeb以降がHEAD)。課題①X2p'(UDR #179未回答)等の未承認案は不適用(`EIGO_KP_GLOSS_ALIGNMENT`はdefault=既存Production既定のまま、ログ`[GLOSS-ALIGN] 実効flag=ON (source=default)`)。 |
| 5 | ASR/TTS/retry/fallback/HR | `TTS_EXECUTION_MODE=STANDARD`。OPEN-487/489/491/494のASR数値・時刻修正(commit d6d17562b/7d4ec5bc4/1d104d711)は`git merge-base --is-ancestor`でHEADに含まれることを確認(3件とも含まれる)。HR Lock時はapprove_regenerateしない。 |
| 6 | 作業ツリー確認 | `git status`(着手時)でtracked変更は `CURRENT_SPEC.md`(SSOT文書)・`er110_family_y_opinion_based_03.py`(Family Y、Z経路のimport graph外)・各種output系のみ。Z Production経路のimport graph(er026 runner/er062_*/er063/er006/er021/er078/er105/er003_*等)に他agentの未commit変更なし。本作の変更は er026 runner・er062_structure・er062_writer(data表のみ)と新規seed/test。 |
| 7 | 日次予算 | 10-24把握分約433円+Y≤30円+X≤100円+本作上限100円=663円で1,000円内(BUDGET_PLAN_01.md)。 |

## §B 原作忠実性チェックポイント(Adv=r2 434語・32段落 / Std=std_adjust 443語・32段落、Seed essentials sha 2b5ce66008dc、原作 `er026_seeds/the_monkeys_paw/story.md`)
r0/r1は中間稿(引用省略、writer/cp_checklist.md参照)。段落数はAdv/Std一致(32/32)。題名はWriterが"The Last Wish"と付けたが、ページ・音声の作品名は登録値(猿の手 / The Monkey's Paw)。

| # | 項目 | Adv(r2)本文の引用 | Std(std_adjust)本文の引用 | 判定 |
|---|---|---|---|---|
| 1 | ending_reveal(第三の最後の願い→ノックが止む→無人の道。願いの内容・外のものは語らない) | `Just as his wife was about to open the door, he made his third and last wish.` / `The terrible knocking stopped.` / `She pulled the door open. There was nobody there. Cold wind swept into the house, and her long wail of loss rose into the night.` / `The street lamp opposite shone on a quiet, deserted road.` | `Just as she reached to open the door, he grabbed the paw and made his third and last wish.` / `Suddenly, the terrible knocking ended.` / `She opened the door, but no one stood outside. Cold wind blew in as her long cry of loss rose into the night.` / `Across the street, the lamp shone on an empty, silent road.` | OK(最終段落が原作最終文の意味。第三の願いの内容を書いていない) |
| 2 | withhold_until_end(使者が話す前にHerbertの死・200ポンドの意味を示唆しない。結末の説明なし) | 使者登場前: `By breakfast, they were joking again. Herbert left for work, and Mrs. White cleared the table.`→`Later, a stranger from the firm arrived.`→`“Your son was caught in the machinery,” he said. “He is dead.”`。結末前後に説明・教訓の付加文なし | `They laughed about it again over breakfast before Herbert left for work.`→`Later, a man from Herbert’s company came to visit.`→`“Your son died after a machine caught him at work,” the man said.` | OK |
| 3 | key_role Mr. White | `Mr. White raised the paw with a smile. “I wish for two hundred pounds.”` / 全編Mr. White | `Mr. White smiled as he raised the paw. “I wish to have two hundred pounds.”` | OK |
| 4 | key_role Mrs. White | `Beside them, Mrs. White smiled over her knitting.` / `Mrs. White shook her husband awake.` | `Mrs. White smiled as she knitted beside them.` / `Mrs. White woke her husband with tears on her face.` | OK |
| 5 | key_role Herbert | `Herbert grinned over the chessboard` / `“Ask for two hundred pounds, Father. Enough to pay off the house!”` | `Mr. White lost at chess to his grown son, Herbert.` / `Herbert joked, “Ask for two hundred pounds, Father! That would pay for the house.”` | OK |
| 6 | 軍曹は役割で表現(無名) | `a retired sergeant-major home from India` / `his friend warned` | `a retired sergeant-major from India` | OK(Morrisの名は出ない) |
| 7 | 使者は役割で表現(無名) | `a stranger from the firm` | `a man from Herbert’s company` | OK(Maw and Megginsの名は出ない) |
| 8 | key_causality(猿の手・警告・200ポンドの願い→ねじれる→死と見舞金200ポンド→第二の願い→ノック→第三の最後の願い) | `“It grants three wishes,” he said, “but brings sorrow to anyone who interferes with fate.”`→`“Burn it,” his friend warned. “And don’t blame me if you keep it.”`→`It twisted in his hand.`→`offers you two hundred pounds in compensation`→`“I wish Herbert alive again.”`→`Then came a soft knock.`→`made his third and last wish` | `“The paw gives three wishes,” he said. “But trying to change your fate brings sadness.”`→`“Burn it, or don’t blame me for what happens,” his friend warned.`→`The paw twisted in his hand`→`offers two hundred pounds for your loss`→`“I wish for Herbert to live again.”`→`A quiet knock broke the silence.`→`made his third and last wish` | OK |

## §B 最終稿確定(委任_03、2026-10-24)
- 引用照合: 上表の8項目に含まれる引用43箇所(Adv r2・Std std_adjust、curly quote正規化のうえ完全一致検索)を `writer/r2.md` / `writer/std.md` に対して機械照合し、**43/43一致・不一致0**(引用の誤記なし)。本文は完成音声・公開ページの原稿(canonical)と同一(`article_text_source=canonical`)。
- 題名: ページ・音声ファイル名・KP・SSOT(`STORY_REGISTRY["the_monkeys_paw"]`)とも『猿の手 / The Monkey's Paw』。Writer本文題 "The Last Wish" は表示に使われない。
- 完成音声との差: Std `full_story_part1_c10` のみ Local Rewrite で音声が `guest`->`visitor`(スクリプト表示は原稿の `guest`)。意味・筋は不変(原作忠実性への影響なし)、RUNTIME_EVIDENCE_01.mdに記録。
- 判定(8項目): 全項目OK(結末の第三の最後の願い/ノックが止む/無人の道=維持、withhold_until_end維持、Mr./Mrs. White・Herbert維持、軍曹・使者は無名役割、因果連鎖維持)。ホラーの緊張感所見=下記A。

## 所見(軽微・処置不要の範囲、Fable確認)
- A(ホラーとしての緊張感の所見): 地の文を最小限にし会話と短文で運ぶ構成。(1)冒頭の穏やかな団欒(風・暖炉・チェス)から軍曹の警告、(2)猿の手が手の中で『ねじれる』不穏、(3)使者の登場で一転、(4)第二の願い後の沈黙(`listening to the clock`)→`soft knock`→`The knocking grew louder.`と音で恐怖を積み、(5)妻が椅子に乗ってかんぬきに手を伸ばし、夫が床で手探りする『時間との競争』、(6)最後は『誰もいない・無音』で終わる。語りと会話のみで緊張が増す。効果音語・未承認演出の追加なし。恐怖の山場(ドアの外のものを書かない)は原作どおり維持。台詞が少し説明的になる箇所(`I’m afraid of what might return`)は原作の`could only recognize him by his clothing`を圧縮した代替で、直接描写を避けつつ恐怖を保つ。
- B: 軍曹が自分の願いを語る部分は`Have you used it? / All three.`の2往復のみ。原作の『最初の持ち主の第三の願いは死』は省略(free_to_cut=軍曹の語り)。警告そのものは維持。
- C: 語数 Adv 434 / Std 443(330-470内)、段落数 32/32一致。
- D: 原作の`Sounds like the Arabian Nights`・チェスの冗談・葬儀の詳細・夫婦の寝室の長い言い争いはfree_to_cut相当で省略。固有名詞の増加なし(Morris/Maw and Meggins/Laburnamは出ない)。
- E: 地の文に`high bolt`(Std=`high door lock`)の表現を作ったのは原作の『最後のかんぬき』の言い換えで、原作の筋の変更ではない。
