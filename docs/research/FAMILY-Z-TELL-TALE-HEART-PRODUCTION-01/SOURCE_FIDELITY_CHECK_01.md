# SOURCE_FIDELITY_CHECK_01 (FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01 委任_03、2026-10-24)

対象: run_sf_prod_01 の最終本文 `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01/writer/std.md`(Std、一人称)・`writer/r2.md`(Adv、三人称)。維持対象はSOURCE_CHECK_01.md(原典Poe 1843、Seed)に準拠。目視照合(Writer最終稿 = 音声・ページの正本、Gate `article_text_source=canonical`)。

| 維持項目 | Std(std.md) | Adv(r2.md) |
|---|---|---|
| 老人のハゲワシ様の薄青い目が動機(老人は愛している・金目当てではない) | 「I loved the old man ... pale blue eye ... like a vulture's. It froze my blood.」 | 「He loved the old man ... pale blue eye ... like a vulture's, made his blood turn cold.」 |
| 「自分は狂っていない、神経質なだけ」+鋭い聴覚 | 「only nervous, not mad」「hear everything in heaven and on earth」 | 「not mad ... only nervous」「sharpened his senses ... heard everything in heaven and earth」 |
| 7夜の偵察(真夜中・覆った提灯・一筋の光・目は閉じていた) | 「For seven nights ... midnight ... covered lantern ... closed every time」 | 同等(eased open ... covered lantern ... Always closed) |
| 8夜目: 親指が提灯の金具で滑る→「Who's there?」 | 「thumb slipped on the lantern's metal catch」「Who is in here?」(old_man台詞) | 「thumb slipped on the lantern's metal fastening」「Who's there?」 |
| 目が開く→心臓音(綿に包んだ時計のような低く速い音) | 「wide open」「low, fast beat, like a watch inside cotton」 | 「Wide open」「a watch wrapped in cotton」 |
| 近所に聞こえる恐れ→飛びかかり殺害(悲鳴1回・ベッドを倒す) | 維持(shouted/jumped/screamed once/pulled the heavy bed over him) | 維持(rushed forward/shrieked once/pulled the heavy bed) |
| 床板3枚の下へ隠蔽・痕跡なし | 「three wooden floorboards ... leaving no mark」 | 「beneath three floorboards ... No mark remained」 |
| 午前4時に警官3名・近所が悲鳴を聞いた→悪夢と説明・老人は田舎 | 維持 | 維持 |
| 寝室の床下の真上に座る(自信) | 「sat right above the body, calm and sure of myself」 | 「sat directly above the hidden body」 |
| 耳鳴り→心臓音が戻る・椅子を引きずる・音が大きくなる・警官は気づかない風 | 維持 | 維持 |
| 警官は知っているという妄想(笑顔=嘲り) | 「they knew, and their friendly smiles were laughing at me」 | 「they knew ... smiles were mocking him」 |
| 結末: 自白(床板を剥がせ、老人の心臓の音だ) | 「I killed him! Pull up the floorboards ... It is his horrible heart beating!」 | 「I did it! Tear up the planks! ... his hideous heart!」 |

- 因果: 目への嫌悪→殺意→7夜の失敗→8夜目に目が開く→心臓音への恐怖→殺害→隠蔽→警官訪問→心臓音の再来→自白、の順序・因果を両レベルで維持(欠落なし)。
- 結末欠落: なし(最終段落が自白)。心臓音: Std/Adv各レベルで8夜目の殺害前・殺害後の余韻・警官の前(音が大きくなる)・自白の最終行に登場。
- 原典からの意図的な圧縮: 遺体解体・血痕を受ける桶の描写は未描写(SOURCE_CHECK_01.md:33のfree_to_cut。維持対象は「殺害→床下隠蔽」)。段落・場面の統合による短縮(Std440語/Adv434語、各約4.5〜4.8分)。
- 音が現実か妄想かを断定していない(原作どおり): 維持。
- Local Rewrite(部分再生成)開示: 本run(writer r0→r1→r2→std_adjust)でLocal Rewrite経路の使用なし(Writer自動3段+Std調整のみ)。Writer段の結果は`writer/provenance.json`。ユーザー向けページ(standard/advanced.html)に原作翻案である旨の注記は見当たらない(Grep `Local Rewrite|翻案|原作|Poe` 0件)=Z共通ページ様式のまま、本runでの新設・変更なし。

## 委任_04追補
- Std KP差替え(vulture's→sure of oneself[source_span=「sure of myself」、本文10行前後の「calm and sure of myself」]。metal catch・in heaven and on earthは本文内の連続span)。KPはいずれも本文のsource_spanに実在し、本文・Adv本文は無変更(本文改変0)。
