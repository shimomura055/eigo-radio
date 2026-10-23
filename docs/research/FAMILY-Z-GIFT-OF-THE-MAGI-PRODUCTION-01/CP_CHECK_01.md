# CP_CHECK_01 (FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01 委任_01、2026-10-24)

前半(§A)=着手時の既存仕様整合確認(委任文§1の1〜6)。後半(§B)=原作忠実性チェックポイント(Sonnet記入→Fable確認待ち)。

## §A 着手時の整合確認
| # | 確認事項 | 結果(照合箇所) |
|---|---|---|
| 1 | 正式Production経路 | er026 runner `er026_family_z_fiction_production_runner_01.py --story <key> --run run_sf_prod_01 --stages ...`、E2E_STAGES順=seed_check,writer,std_adjust,plan,support,kp,tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify(`--help`で確認)。『二十年後』と同一経路。作品追加は `STORY_REGISTRY["the_gift_of_the_magi"]`(runner)・`STORY_VOICE_ROSTER`/`STORY_SPEAKER_CONFIG`/`STORY_LINT_CONFIG`(er062_structure)・`STORY_MAIN_CHARACTER`(er062_writer)のdata表のみ(ロジック変更0)。完成段は `provision_shell,gate,assemble,pages,page_verify` を1起動(OPEN-480)。 |
| 2 | Std/Adv構成・長さ・Voice | 3パート構成、本文330-470語(runner `ACCEPT_WORD_RANGE`)、Voice=正式Voice表+決定的割当規則(er062 `assign_dialogue_voices`、2026-10-23ユーザー最終決定): narrator=Aoede、Della(女1番)=Zephyr、Madame Sofronie(女2番)=Kore、Jim(男1番)=Algieba。pin(個別例外)なし。Charon=Adv補助(KP番号等、既存)。選定理由: 規則が登場順・性別で決定的に割当てる仕様のため作品別の人選はしない。Dellaは若い妻(Zephyr=女Pool先頭=主人公)、Madameは年配の店主(女Pool 2番Kore、声の区別が付く)、Jimは若い夫(男Poolの先頭Algieba、唯一の男性話者)。配役を増やしていない(ROSTERは原作の発話者のみ)。 |
| 3 | 原作忠実性基準(修正版B) | Seedに`source_essentials`(ending_reveal/setups_and_payoffs/key_roles/key_causality/free_to_cut、維持必須5件=上限ESSENTIALS_MAX_ITEMS)を記入し、`validate_source_essentials`でsource_quoteが原作最終段落に逐語で在ることを検証済み(登録test PASS)。維持必須=Della/Jimの人物像と夫婦関係、髪と時計、各自が手放した物と贈った物、最後の皮肉と愛情、原題とMagiの意味(Seed conversion_planで結語段落を保持と明示)。判定は§B。 |
| 4 | Key Phrase正式承認・配線状況 | A-1=PRODUCTION_WIRED(UDR #169)。課題②(所有格一般化)=2026-10-24 APPROVED_FOR_PRODUCTION、別agent(FX-KP 委任_20)が配線中(着手時点: `er105_kp_fulltext_selector_01.py`等が未commitの変更あり=配線作業中)。kp段の実行時点で②がcommit済み・Fable受入済みか確認し、未配線なら現行(A-1のみ)で実行し、finalize前に再確認(RUNTIME_EVIDENCEにkp実行時刻と配線状況を対応させて記録)。G3/課題①検査方式C等の未承認案は適用しない(DEV flagをONにしない、`EIGO_KP_GLOSS_ALIGNMENT`は既定のまま)。 |
| 5 | ASR/TTS/retry/fallback/HR | `TTS_EXECUTION_MODE=STANDARD`。RET/PNAP/UKUS(X/Z WIRED、Fable受入2026-10-23)、OPEN-479修正済み(Z会話segment_id)。HR Lock発生時は自分でapprove_regenerateしない(委任文§2-C)。 |
| 6 | 時刻表現検査 | 第1層(er006)=commit b5138e452、第2層(er078)=commit e0eb13ab4で修正済み。OPEN-482残存2件(`ten thirty`純語形↔`10:30`がUNKNOWN、`ten thirty`↔`1030`桁連結EQUAL)は別管理ID ASR-TIME-NUMERAL-EQUIVALENCE-01で対応中。本作の時刻語形: Adv/Std本文とも `By seven, dinner...` のみ(単一数詞`seven`。隣接数詞語の`ten thirty`型ではない)。通貨`$1.87`(Std)・`One dollar and eighty-seven cents`(Adv)・`twenty-one dollars`・`eighty-seven cents`の数語が音声↔ASRで正規化差を起こす可能性がある(通貨/数詞語、OPEN-482の時刻型とは別)。HR Lockになった場合は原稿改変で回避せずFableへ。 |

## §B 原作忠実性チェックポイント(Adv=r2 434語・30段落 / Std=std_adjust 449語・30段落、Seed essentials sha 64f183e39162、原作 `er026_seeds/the_gift_of_the_magi/story.md`)
r0/r1は中間稿(引用省略、cp_checklist.md参照)。

| # | 項目 | Adv(r2)本文の引用 | Std(std_adjust)本文の引用 | 判定 |
|---|---|---|---|---|
| 1 | ending_reveal(互いの贈り物が使えなくなった皮肉+Magi) | `Her hair was gone; the combs could not hold it. His watch was gone; the chain had nothing to carry. Each had sold their greatest treasure to buy the other a gift.` / `The magi were wise men who brought gifts on the first Christmas. Yet here, with gifts they could not use, sat two foolish young people whose love made them the wisest of all gift-givers. They were the magi.` | `Without her hair, she could not use the combs. Without his watch, he could not use the chain. Both had sold their greatest treasure for the other’s gift.` / `Wise men called the magi brought gifts on the first Christmas. The two young people seemed foolish with their useless gifts. But their love made them wiser than all other gift-givers. In every place, they are the wisest; these two are the magi.` | OK |
| 2 | withhold_until_end(Jim告白前に時計売却・櫛・皮肉の示唆なし) | 告白前: `Jim stopped. / His eyes stayed on her hair.` `Inside were the tortoise-shell combs...`(櫛はJimが渡す場面で初出=原作どおり)、`Give me your watch.`→`I sold the watch to buy your combs.`の順。告白前の付加文なし | `Jim stood still in the doorway. / He stared at her hair...`、同順 | OK(付加文なし。告白後〜結語前の1段落は原作の因果を要約する範囲で、独自の教訓ではない) |
| 3 | setup/payoff(髪と時計→鎖と櫛) | setup: `They owned two things that made them proud. One was Jim’s gold watch, handed down from his grandfather to his father, and then to him. The other was Della’s long brown hair.` payoff: `Inside were the tortoise-shell combs`→`Jim sat down... “I sold the watch to buy your combs.”` | setup: `They were proud of two things: Della’s long brown hair and Jim’s gold watch. His grandfather, then his father, had owned the watch before him.` payoff: `“To buy your combs, I had to sell my watch.”` | OK |
| 4 | keep_name Della | 全編でDella | 全編でDella | OK |
| 5 | keep_name Jim | `Jim’s gold watch`・`I sold it, Jim.` | 同左 | OK |
| 6 | 店主は役割で表現(無名) | `Outside a hair-goods shop... The owner lifted the heavy waves.` | `Outside a shop selling hair... The shop owner lifted her thick waves of hair.` | OK(Sofronieの名は出ない) |
| 7 | key_causality(贈り物のために各自が宝物を手放す→使えなくなる) | `“Cut it quickly, please.”`→`a simple platinum watch chain`→`“I sold the watch to buy your combs.”`→`Each had sold their greatest treasure to buy the other a gift.` | `“Please cut it off right now.”`→`a simple platinum watch chain`→`“To buy your combs, I had to sell my watch.”`→`Both had sold their greatest treasure for the other’s gift.` | OK |
| 8 | 原題の意味(Magi) | `The magi were wise men who brought gifts on the first Christmas.` | `Wise men called the magi brought gifts on the first Christmas.` | OK(原作の『Babe in the manger』『Christmas presentsを発明した』の2点は省略。学習者向けの短縮として許容。原題の意味=最も賢い贈り手、は維持) |

## 所見(軽微・処置不要の範囲、Fable確認)
- A: Jimの台詞は両レベルとも1つ(`I sold the watch to buy your combs.`/`To buy your combs, I had to sell my watch.`)。原作でJimが語る`You've cut off your hair?`等は省略(free_to_cut=繰り返し会話)。ユーザー§2「DellaとJimの会話で感情が伝わる」は、Dellaの6〜7台詞とJimの告白で満たすが、Jimの発話量は少ない(Writer承認済みの400語圧縮による)。
- B: Stdの結語`In every place, they are the wisest; these two are the magi.`は原作`Everywhere they are wisest. They are the magi.`の直訳に近く、やや硬い。意味は保持。
- C: 語数 Adv 434 / Std 449(330-470内)、段落数 30/30一致。
- D: `Madame Sofronie`の名・Jimの正式名・原作の語り手の冗談・鎖の価格21ドルの根拠(`$21`は保持)等はfree_to_cut相当。固有名詞の増加なし。
