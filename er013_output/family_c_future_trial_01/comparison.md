# er013_output/family_c_future_trial_01/comparison.md

管理ID: EDITORIAL-FUTURE-FAMILY-C-PROTOTYPE-TRIAL-01

テーマ: 「家庭用ロボットと家事」(home robots and housework、ユーザー確定)。
baselineなし(A2/B1各1本、Family C独立経路のみ。理由は`EDITORIAL-FUTURE-FAMILY-C-PROTOTYPE-TRIAL-01_REPORT.md`§作業B参照)。
Audio/TTSなし。**Production採用・配線ではない**。

## 3層Ledger(Research→Layer1/2/3、実測)

```
[PRESENT_FACT]
[VERIFIED] HR-001: 世界で2023年に販売された家庭用床掃除ロボットは210万台超で、家庭用サービスロボット全体の約57%を占めた。国際ロボット連盟（IFR）は、家庭用床掃除ロボット市場を成熟市場と評価している。
  scope: 世界市場。IFRが把握する家庭用サービスロボット販売統計
  conditions: 販売台数ベース。家庭用サービスロボット全体に占める比率。
  numeric_value: 210万台超；約57% (numeric_scope: 世界の家庭用床掃除ロボット販売台数および家庭用サービスロボット全体に占める比率)
  date_or_period: 2023年
  causal_strength: OBSERVED_REPORTED
  source: 2.1 million domestic floor cleaning robots sold in 2023 ([ifr.org](https://ifr.org/post/21-million-domestic-floor-cleaning-robots-sold-in-2023)) (https://ifr.org/post/21-million-domestic-floor-cleaning-robots-sold-in-2023)
  notes_for_writer: 『家庭用ロボット全体が普及した』ではなく、主に床掃除ロボットが普及の中心であることを示す数字。

[VERIFIED] HR-002: 米国の成人の15%がロボット掃除機を所有していると回答した。
  scope: 米国の18歳以上の成人1,070人。YouGovの加重オンライン調査。
  conditions: ロボット掃除機の所有を自己申告。ロボットモップ単体やAI機能の有無は別集計。
  numeric_value: 15% (numeric_scope: 米国成人全体に占めるロボット掃除機所有者の割合)
  date_or_period: 2025年5月13〜14日調査
  causal_strength: OBSERVED_REPORTED
  source: How Americans use and replace their vacuum cleaners ([yougov.com](https://yougov.com/en-us/articles/52206-how-americans-use-and-replace-their-vacuum-cleaners)) (https://yougov.com/en-us/articles/52206-how-americans-use-and-replace-their-vacuum-cleaners)
  notes_for_writer: 所有率は『利用率』や『継続利用率』と同一視しない。

[VERIFIED] HR-003: 米国成人の13%が、AI機能を持つロボット掃除機を所有していると回答した。
  scope: 米国成人5,119人を対象としたPew Research Center調査。
  conditions: まず掃除機の所有を確認したうえで、AI機能の有無を質問。すべてのロボット掃除機所有者を含む数値ではない。
  numeric_value: 13% (numeric_scope: 米国成人全体に占めるAI機能付きロボット掃除機所有者の割合)
  date_or_period: 2026年2月17〜23日調査
  causal_strength: OBSERVED_REPORTED
  source: Roughly 1 in 3 U.S. adults have a smart speaker; fewer have other smart home devices ([pewresearch.org](https://www.pewresearch.org/chart/roughly-1-in-3-u-s-adults-have-a-smart-speaker-fewer-have-other-smart-home-devices/)) (https://www.pewresearch.org/chart/roughly-1-in-3-u-s-adults-have-a-smart-speaker-fewer-have-other-smart-home-devices/)
  notes_for_writer: HR-002の15%とは質問条件が異なるため、単純な時系列比較や矛盾のない統合をしない。

[VERIFIED] HR-004: 米国成人の38%が、家庭内作業を支援するロボットに関心があると回答した。
  scope: 米国成人1,247人を対象としたYouGovオンライン調査。
  conditions: 実際の購入・所有ではなく、家庭内作業を支援するロボットへの関心。
  numeric_value: 38% (numeric_scope: 調査対象の米国成人に占める関心層の割合)
  date_or_period: 2025年1月30〜31日調査
  causal_strength: OBSERVED_REPORTED
  source: Two in five Americans are interested in having a household robot take care of their chores ([yougov.com](https://yougov.com/en-us/articles/51596-two-in-five-americans-are-interested-in-having-a-household-robot-take-care-of-their-chores)) (https://yougov.com/en-us/articles/51596-two-in-five-americans-are-interested-in-having-a-household-robot-take-care-of-their-chores)
  notes_for_writer: 普及実績ではなく、潜在需要・期待の指標として扱う。

[VERIFIED] HR-007: RoborockのSaros Z70は、5軸の折りたたみ式機械アーム、3.14インチの薄型設計、障害物認識機能を備え、公式米国ストアで1,699.99ドルの掲載例がある。
  scope: Roborock Saros Z70。米国公式ストアの製品情報。
  conditions: 機械アームの物体認識・移動にはアプリでの設定が必要とされる。
  numeric_value: 1,699.99米ドル；高さ7.98cm；5軸機械アーム (numeric_scope: 製品の掲載価格および仕様)
  date_or_period: 2026年9月時点の公式掲載情報
  source: Roborock Saros Z70 Robot Vacuum with OmniGrip Mechanical Arm ([us.roborock.com](https://us.roborock.com/products/roborock-saros-z70?utm_source=openai)) (https://us.roborock.com/products/roborock-saros-z70)
  notes_for_writer: 『片付けができる汎用ロボット』ではなく、物体移動機能を追加したロボット掃除機として分類する。

[VERIFIED] HR-008: Weave RoboticsのIsaac 1は、汚れた衣類の回収、洗濯物の折り畳み・収納、ベッドメイク、玩具・靴・散らかった物の整理を想定した移動型家庭用ロボットで、価格は一括7,999ドルまたは月449ドルと発表されている。
  scope: Weave Robotics Isaac 1。家庭向け予約製品。
  conditions: 予約受付段階。メーカーは自律動作を基本とし、必要時には遠隔操作支援を行うとしている。
  numeric_value: 7,999米ドル一括；月449米ドルのサブスクリプション (numeric_scope: 家庭向け支払選択肢)
  date_or_period: 2026年9月時点の予約・製品発表情報
  source: Isaac 1 — Weave Robotics ([weaverobotics.com](https://www.weaverobotics.com/isaac-1?utm_source=openai)) (https://www.weaverobotics.com/isaac-1)
  notes_for_writer: 価格は完成・量産後の実売実績ではなく、メーカーの予約条件。

[VERIFIED] HR-009: Weave Roboticsは、Isaac 1の最初の出荷を2026年秋に開始し、カリフォルニアを先行地域として、米国全体への展開は2027年までに行う予定と説明している。
  scope: Weave Robotics Isaac 1のメーカー計画。
  conditions: 予定であり、実際の出荷完了・全国普及を示すものではない。
  numeric_value: 2026年秋；米国全体は2027年までに展開予定 (numeric_scope: 出荷・販売地域と時期)
  date_or_period: 2026〜2027年予定
  source: Isaac 1 — Weave Robotics ([weaverobotics.com](https://www.weaverobotics.com/isaac-1?utm_source=openai)) (https://www.weaverobotics.com/isaac-1)
  notes_for_writer: 現在の普及実績と将来の出荷計画を混同しない。

[VERIFIED] HR-010: Weave RoboticsのIsaac 1は、バッテリー駆動時間8時間、充電時間2時間、幅20.5インチ・奥行22インチの設置面積、3〜5フィート9インチの高さ調整機構をメーカー仕様として掲げている。
  scope: Weave Robotics Isaac 1。
  conditions: メーカー公表値。実際の作業内容、負荷、移動距離による稼働時間への影響は別途検証が必要。
  numeric_value: 稼働8時間；充電2時間；設置面積20.5×22インチ；高さ3〜5フィート9インチ (numeric_scope: 製品仕様)
  date_or_period: 2026年9月時点のメーカー仕様
  source: Isaac 1 — Weave Robotics ([weaverobotics.com](https://www.weaverobotics.com/isaac-1?utm_source=openai)) (https://www.weaverobotics.com/isaac-1)
  notes_for_writer: 数値は公称仕様であり、実作業での連続稼働時間とは区別する。

[VERIFIED] HR-011: ロボット掃除機は、手動掃除機よりも狭い範囲の作業に適しており、ある3週間の家庭内日記調査では、9種類の表面のうち7種類で手動掃除機より性能が劣るか、掃除できなかった。
  scope: 家庭利用者を対象とした比較研究。ロボット掃除機と3種類の手動掃除機を比較。
  conditions: 研究で比較された機種・表面条件に限定される。すべての市販機種に一般化できるとは限らない。
  numeric_value: 9種類中7種類 (numeric_scope: 研究対象となった表面のうち、ロボット掃除機が手動掃除機より劣るか、掃除できなかった表面の数)
  date_or_period: 2024年発表の3週間日記調査
  causal_strength: OBSERVED_REPORTED
  source: Inferior, yet Transformative: The User Experience with Robotic Vacuum Cleaners ([forskning.ruc.dk](https://forskning.ruc.dk/en/publications/inferior-yet-transformative-the-user-experience-with-robotic-vacu/?utm_source=openai)) (https://rucforsk.ruc.dk/ws/portalfiles/portal/106122597/VacuumCleanerUX_IWC2024_AuthorVersion.pdf)
  notes_for_writer: 『ロボット掃除機は手動掃除機より常に劣る』とは書かず、研究条件下での比較結果として扱う。

[VERIFIED] HR-012: 同じ研究では、ロボット掃除機は階段や天井を掃除できず、複数の床面で性能が低かった。また、別の先行研究として、ロボット掃除機の作動音が利用者の睡眠や活動選択を制約した事例が整理されている。
  scope: 家庭用ロボット掃除機の利用体験研究。
  conditions: 階段・天井など、床面以外の清掃は一般的な床掃除ロボットの設計対象外。騒音の影響は特定の利用者・住宅条件に依存。
  date_or_period: 2024年研究および引用された先行研究
  causal_strength: OBSERVED_REPORTED
  source: Inferior, yet Transformative: The User Experience with Robotic Vacuum Cleaners ([rucforsk.ruc.dk](https://rucforsk.ruc.dk/ws/portalfiles/portal/106122597/VacuumCleanerUX_IWC2024_AuthorVersion.pdf?utm_source=openai)) (https://rucforsk.ruc.dk/ws/portalfiles/portal/106122597/VacuumCleanerUX_IWC2024_AuthorVersion.pdf)
  notes_for_writer: 『床掃除の一部を自動化する機械』であり、家全体の掃除を代替する機械ではないことを示す根拠。

[VERIFIED] HR-013: Consumer Reportsは、ロボット掃除機は整理された部屋、硬い床、または低パイルのラグに適していると評価し、深い清掃では従来型掃除機に及ばないと報告した。試験例では、Mieleのアップライト掃除機がごみの半分超を回収した一方、Samsungのロボット掃除機は20%未満だった。
  scope: Consumer Reportsの試験対象機種・試験条件。
  conditions: 特定モデルの試験結果であり、市販ロボット掃除機全体の平均ではない。
  numeric_value: Samsungロボット掃除機：20%未満；Mieleアップライト：50%超 (numeric_scope: 試験で回収したごみの割合)
  date_or_period: 2020年頃のConsumer Reports試験記事
  causal_strength: OBSERVED_REPORTED
  source: Can a Robotic Vacuum Replace Your Upright Vac? ([consumerreports.org](https://www.consumerreports.org/appliances/vacuum-cleaners/can-a-robotic-vacuum-replace-your-canister-or-upright-a1557864633/?utm_source=openai)) (https://www.consumerreports.org/appliances/vacuum-cleaners/can-a-robotic-vacuum-replace-your-canister-or-upright-a1557864633/)
  notes_for_writer: 深い清掃性能と、定期的な自動運転による日常維持清掃を区別する。

[VERIFIED] HR-014: RTINGS.comは、2025年の試験体系でロボット掃除機99機種を購入・試験し、コード、ペットの排泄物、ボウルなどを用いた障害物回避試験を実施している。
  scope: RTINGS.comが購入・試験したロボット掃除機99機種。
  conditions: 試験室で再現した障害物条件。実家庭での全状況を網羅するものではない。
  numeric_value: 99機種 (numeric_scope: RTINGS.comが購入・試験したロボット掃除機の機種数)
  date_or_period: 2025年6月更新の試験体系
  causal_strength: OBSERVED_REPORTED
  source: Our Robot Vacuum Tests: Obstacle Avoidance ([rtings.com](https://www.rtings.com/robot-vacuum/tests/obstacle-avoidance?utm_source=openai)) (https://www.rtings.com/robot-vacuum/tests/obstacle-avoidance)
  notes_for_writer: AI・センサーの進歩があっても、コードやペット排泄物などの回避は依然として重要な評価項目であることを示す。

[VERIFIED] HR-015: 2026年に公表された英国10世帯・15〜18か月の縦断研究では、床掃除自動化の試行期間中、床掃除の頻度は平均32%、総掃除時間は189%増加した一方、居住者が手動で掃除する時間は45%減少した。
  scope: 英国10世帯。時間日記、スマートプラグ、アプリログ、インタビューを組み合わせた研究。
  conditions: 床掃除自動化の試行期間との比較。自動化により掃除頻度や清潔さの基準が変化した可能性がある。
  numeric_value: 掃除頻度＋32%；総掃除時間＋189%；手動掃除時間−45% (numeric_scope: 研究対象10世帯の試行期間中の平均変化)
  date_or_period: 15〜18か月の縦断研究；2026年公表
  causal_strength: OBSERVED_REPORTED
  source: How home automation reshapes household time use and energy demand ([sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S0378778825016500?utm_source=openai)) (https://www.sciencedirect.com/science/article/pii/S0378778825016500)
  notes_for_writer: 自動化は手動作業を減らしたが、掃除の頻度・総稼働時間を増やす場合もある。『時間がそのまま同じ量だけ節約された』とは断定しない。

[VERIFIED] HR-016: 2026年の日本のパネルデータ研究は、ロボット掃除機の利用が家事時間を統計的に有意に減少させたと推定したが、睡眠時間への統計的に有意な影響は確認しなかった。
  scope: 慶應義塾家計パネル調査を用いた日本の世帯分析。二方向固定効果モデルとマッチングを組み合わせた頑健性分析。
  conditions: 観察パネルデータに基づく推定。利用世帯と非利用世帯の差を完全に除去できるとは限らない。
  date_or_period: 2026年発表
  causal_strength: CAUSAL_STATED_BY_SOURCE
  source: The Effects of Time-Saving Technology Use on Household Time Allocation: Evidence from Robot Vacuum Use ([cir.nii.ac.jp](https://cir.nii.ac.jp/crid/1390308751666599168?utm_source=openai)) (https://cir.nii.ac.jp/crid/1390308751666599168)
  notes_for_writer: 『家事時間を有意に減らした』という研究推定は使えるが、具体的な削減時間を推測してはいけない。

[VERIFIED] HR-017: 同じ日本研究では、家事時間の減少は主に既婚女性で確認され、ロボット掃除機の利用と既婚女性の労働参加には正の関連が示された。
  scope: 慶應義塾家計パネル調査を用いた日本の既婚女性に関する分析。
  conditions: 観察データに基づく推定・関連。ロボット掃除機利用だけが労働参加を引き起こしたと確定するものではない。
  date_or_period: 2026年発表
  causal_strength: CORRELATIONAL
  source: The Effects of Time-Saving Technology Use on Household Time Allocation: Evidence from Robot Vacuum Use ([cir.nii.ac.jp](https://cir.nii.ac.jp/crid/1390308751666599168?utm_source=openai)) (https://cir.nii.ac.jp/crid/1390308751666599168)
  notes_for_writer: 『労働参加を増やした』ではなく、『利用と労働参加に正の関連が示された』とする。

[VERIFIED] HR-018: J.D. Powerの2021年米国掃除機満足度調査では、ロボット掃除機所有者の総合満足度は1,000点満点中872点だった。
  scope: J.D. Powerの米国掃除機満足度調査。ロボット掃除機を初めて調査対象に含めた年。
  conditions: 調査対象の所有者による満足度評価。現在の全製品・全地域の満足度を示すものではない。
  numeric_value: 872/1,000点 (numeric_scope: 米国ロボット掃除機所有者の総合満足度スコア)
  date_or_period: 2021年調査
  causal_strength: OBSERVED_REPORTED
  source: 2021 U.S. Vacuum Satisfaction Study ([jdpower.com](https://www.jdpower.com/business/press-releases/2021-us-vacuum-satisfaction-study?utm_source=openai)) (https://www.jdpower.com/business/press-releases/2021-us-vacuum-satisfaction-study)
  notes_for_writer: 満足度が高いことと、手動掃除機を完全代替できることは別の論点。

[VERIFIED] HR-019: 家庭用汎用ロボットの研究では、Dobb·Eがニューヨーク市周辺10家庭で109種類のタスクを試行し、全体の成功率81%を報告した。新しいタスクについて、利用者の5分間の実演と15分間のモデル適応を用いた。
  scope: ニューヨーク市周辺の10家庭、109タスク。研究用Stretch移動ロボットとDobb·Eシステム。
  conditions: 研究用ロボット・研究プロトコルに基づく結果。市販の汎用家庭用ロボットの性能ではない。
  numeric_value: 109タスク；10家庭；成功率81%；実演5分＋適応15分 (numeric_scope: 研究対象タスクと家庭、学習手順および成功率)
  date_or_period: 2023年公表研究
  causal_strength: OBSERVED_REPORTED
  source: Dobb·E: On Bringing Robots Home ([dobb-e.com](https://www.dobb-e.com/)) (https://www.dobb-e.com/)
  notes_for_writer: 家庭環境での学習可能性を示す研究結果だが、洗濯物たたみ・食器洗いなど特定家事の成功率ではない。

[VERIFIED] HR-020: 食器洗いロボットの研究では、1回の人間実演から手作業の食器洗いを学習するシステムが、個別工程で50〜100%の成功率、タスク全体で最大40%の成功率を報告した。
  scope: 模擬キッチンで学習し、外観・形状の異なる標準的な家庭キッチンで評価した研究。
  conditions: 研究用ロボット、特定の食器・工程・環境での結果。量産製品の性能ではない。
  numeric_value: 個別工程50〜100%；タスク全体最大40% (numeric_scope: 研究条件下の食器洗い工程および全体タスクの成功率)
  date_or_period: 2023年公表研究
  causal_strength: OBSERVED_REPORTED
  source: Kitchen Robot Case Studies: Learning Manipulation Tasks from Human Video Demonstrations ([publications.ri.cmu.edu](https://publications.ri.cmu.edu/kitchen-robot-case-studies-learning-manipulation-tasks-from-human-video-demonstrations?utm_source=openai)) (https://publications.ri.cmu.edu/kitchen-robot-case-studies-learning-manipulation-tasks-from-human-video-demonstrations)
  notes_for_writer: 食器の把持・すすぎ・こすり洗い・配置を一体化した家庭用製品が普及していることを示すデータではない。

[VERIFIED] HR-022: Figure AIは、Vision-Language-Action（VLA）モデルHelixを用いて、二本の多指ハンドを持つヒューマノイドが洗濯物を完全自律で折り畳むデモを2025年8月に公表した。Figureは、衣類が変形・しわ・絡まりを持つため、折り畳みは高度な把持・視覚・リアルタイム適応を必要とすると説明している。
  scope: Figure AIによる研究・製品デモ。
  conditions: メーカー発表のデモであり、一般家庭の多様な衣類を対象とした第三者評価ではない。
  date_or_period: 2025年8月12日発表
  causal_strength: OBSERVED_REPORTED
  source: Helix Learns to Fold Laundry ([figure.ai](https://www.figure.ai/news/helix-learns-to-fold-laundry)) (https://www.figure.ai/news/helix-learns-to-fold-laundry)
  notes_for_writer: AIの進歩を示す企業デモとして扱い、家庭での実用化・量産化の証拠とは分ける。

[VERIFIED] HR-023: LG CLOiDは、7自由度の腕を2本、各手に5本の独立駆動指、カメラ・センサー・自律走行ベースを備えるAI搭載家庭用ロボットとしてCES 2026で発表された。LGは、冷蔵庫から牛乳を取り出す、オーブンにクロワッサンを入れる、洗濯後の衣類を折り畳むなどのデモを予定した。
  scope: LG ElectronicsのCES 2026発表・デモ。
  conditions: 発表・展示段階。消費者向けの販売価格、量産時期、第三者による家庭内性能評価は示されていない。
  numeric_value: 腕1本あたり7自由度；各手5本の独立駆動指 (numeric_scope: LG CLOiDのメーカー公表ハードウェア構成)
  date_or_period: 2026年1月CES発表
  causal_strength: OBSERVED_REPORTED
  source: LG Electronics Presents LG CLOiD Home Robot to Demonstrate Zero Labor Home at CES 2026 ([lg.com](https://www.lg.com/us/newsroom/home-appliance/lg-cloid-home-robot?f-ec_category_3=Lifestyle+Products%2CProjectors%2CTVs&utm_source=openai)) (https://www.lg.com/us/newsroom/home-appliance/lg-cloid-home-robot)
  notes_for_writer: 家電メーカーが掃除機単体から、接続家電と物理ロボットを組み合わせる方向に進んでいる事例。

[VERIFIED] HR-024: 2025年の機械学習研究は、一般化可能な家庭用ロボットには、複雑な指示・実行中のフィードバック・開かれた家庭環境への適応を同時に処理する能力が必要だと位置づけ、階層型VLAモデルによるオープンエンド指示追従を研究対象とした。
  scope: Generalist robotと階層型Vision-Language-Actionモデルに関する研究。
  conditions: 研究モデル・実験環境の成果であり、市販家庭用ロボットの完成機能ではない。
  date_or_period: 2025年ICML発表研究
  causal_strength: CAUSAL_STATED_BY_SOURCE
  source: Hi Robot: Open-Ended Instruction Following with Hierarchical Vision-Language-Action Models ([proceedings.mlr.press](https://proceedings.mlr.press/v267/shi25d.html)) (https://proceedings.mlr.press/v267/shi25d.html)
  notes_for_writer: 将来トレンドとして、言語理解だけでなく、視覚・計画・動作・フィードバックを統合するVLA／階層型モデルに言及できる。

[FUTURE_ASSUMPTION]
assumption_id: FA-001
assumption: もし床掃除ロボット中心の普及と家庭内作業支援への関心が続けば、家庭用ロボットは家事を全面的に代替するよりも、日常の維持清掃を補助する機械として先に定着すると仮定できる。手動掃除や深い清掃、階段などは引き続き人が担う可能性がある。
based_on: HR-001, HR-004, HR-011, HR-012, HR-013, HR-015, HR-016

assumption_id: FA-002
assumption: もし物体認識・移動、衣類操作、食器洗い、VLAモデルによる指示理解と動作の統合が実用化されれば、家庭用ロボットは床掃除から、洗濯物の回収・折り畳み・収納や散らかった物の整理など、限定された複数の家事へ拡張すると仮定できる。
based_on: HR-007, HR-008, HR-019, HR-020, HR-022, HR-023, HR-024

assumption_id: FA-003
assumption: もし研究デモや予約製品が量産・実家庭向けに成熟すれば、家庭用ロボットは完全放置型ではなく、利用者による初期設定や実演、例外時の確認、必要に応じた遠隔支援を組み込んだ家事サービスとして普及すると仮定できる。
based_on: HR-008, HR-009, HR-010, HR-014, HR-019, HR-020, HR-024

[IMAGINED_FUTURE]
scene_id: IF-001
timeframe: around 2030
scene_summary: 朝、床掃除ロボットが家族の生活動線を避けながら日常清掃を続ける。住人の手動掃除時間は減っているが、階段や深い汚れ、ロボットが届かない場所は週末に人が掃除する。自動化によって掃除の回数そのものは増え、家を保つ方法が『一度に徹底的に掃除する』から『毎日少しずつ維持する』へ変わっている。
grounded_in: FA-001, HR-011, HR-012, HR-013, HR-015, HR-016

scene_id: IF-002
timeframe: around 2035
scene_summary: 住人が短い実演と音声指示で、洗濯物を回収して畳み、指定場所へ収納する手順を家庭用ロボットに教える。ロボットは標準的な衣類や決まった収納には対応するが、絡まった衣類や見慣れない物では動作を止め、住人に確認を求める。家事の中心は、作業をすべて任せることから、例外だけを人が処理することへ移る。
grounded_in: FA-002, FA-003, HR-008, HR-019, HR-022, HR-024

scene_id: IF-003
timeframe: around 2040
scene_summary: キッチンや居間では、家庭用ロボットが家電や収納場所と連携し、片付けや簡単な食器洗いをまとめて実行する。住人はロボットが扱える食器や物の置き場所をあらかじめ整え、コードや小物、ペットの排泄物のような危険・判断の難しい対象は作業前に片付ける。ロボットの導入が、家事の自動化だけでなく、家の設計や物の置き方の見直しも促している。
grounded_in: FA-002, FA-003, HR-014, HR-020, HR-023, HR-024
```

## A2

### A2: 読者向け最終本文(マーカー除去後)

```
## The First Quiet Change

The future of home robots may not begin with a machine that does everything.

It may begin with a machine that keeps the floor from becoming dirty.

In 2023, more than 2.1 million domestic floor-cleaning robots were sold around the world. They made up about 57% of all domestic service robots in that market. In the United States, 15% of adults said they owned a robot vacuum. Another 38% said they were interested in a robot that could help with household chores.

But a robot vacuum is not a full replacement for a person.

It is better at regular maintenance than deep cleaning. In one home study, it performed worse than a manual vacuum, or could not clean at all, on seven of nine types of surfaces. It could not clean stairs or ceilings. Cords, pet waste, and bowls remained among the obstacles used to assess its avoidance.

This limit may shape the future more than the dream of a perfect machine.

If floor robots continue to spread, home cleaning could change from one large weekly battle into many small daily actions. Human hands would still handle stairs, deep dirt, and difficult spaces. The robot would protect the ordinary parts of the home.

## Around 2030: The House That Is Always Being Maintained



Picture a Tuesday morning in 2030. The family is still asleep, but a small cleaning robot is moving across the floor. It slows near a chair. It waits for a person to pass. It turns away from a toy and returns later.

The floor is not perfectly clean. It does not need to be. Dust and crumbs are removed little by little. The home is kept ready by many short cleaning runs.

On the weekend, a person takes the manual vacuum to the stairs. They clean a deep stain near the kitchen. They reach the places the robot cannot reach.

The family does not say, “The robot cleaned the whole house.” They say, “The house stayed under control.”



This future could appear if automatic cleaning becomes normal, but remains limited to the right surfaces and spaces.

It could also bring a strange result. Automation may reduce the time people spend cleaning by hand, while increasing the total amount of cleaning. A long home study found this pattern during a period of floor-cleaning automation. Cleaning happened more often, and the machines ran for more total time, even as manual cleaning time fell.

The home might become cleaner because it is cleaned more often.

It might also become more demanding. Once a robot cleans every day, a little dirt may feel like a failure. The machine would save hands and time, but it could quietly raise the standard of cleanliness.

## The Robot That Does Not Just Vacuum

The next step could be small movements.

A robot vacuum with a mechanical arm can move some objects. Newer research and demonstrations show robots learning tasks such as folding laundry or handling dishes. Other systems are being designed to understand spoken instructions, see objects, plan actions, and change their movements while working.

This is a large jump from moving across a floor.

Yet it does not create a magic servant. A robot may recognize a shirt but fail to understand how a tangled shirt should be handled. It may know where a plate belongs but not know whether the plate is clean. It may stop when an object is unfamiliar.

The important question may not be, “Can the robot do housework?”

The question may be, “What kind of housework can the robot do without help?”

## Around 2035: People Teach the Exceptions



Picture a laundry room in 2035. A resident places a basket near a household robot. They give a short demonstration. This shirt goes on this shelf. Towels go in that drawer. Socks go in a small container.

The robot watches. It tries the task. It picks up a shirt, folds it, and carries it to the correct place.

Then it finds a tangled piece of clothing. The robot stops.

“Please check this item,” it says.

The resident removes the knot. The robot continues.

The family no longer gives the robot every instruction. They handle the unusual moments. The robot handles the repeated pattern.

Housework has not vanished. Its shape has changed. People manage the exceptions, while the machine repeats the ordinary work.



This future could become possible if home robots learn from short demonstrations and respond to feedback. It would require more than a strong arm. The robot would need to understand language, recognize objects, plan several steps, and notice when its plan was failing.

It would also need a way to ask for help.

A household robot might work alone most of the time. But difficult cases could require a person nearby, or a remote operator. This means the future home may not be fully automatic. It may depend on a new kind of service, where the machine works until human judgment is needed.

That could make the robot useful.

It could also make the robot hard to trust. A person might leave the house believing that laundry is being folded, only to return to a robot waiting beside one unknown shirt. The hardest part of housework may be the part that does not fit the robot’s learned pattern.

## Around 2040: A Home Built for Machines



Picture an evening in 2040. In the kitchen, a household robot carries used dishes toward their place. It works with the oven, the refrigerator, and storage areas. In the living room, it gathers toys and shoes.

Before the robot begins, the family clears away a charging cable. They move a small object from the floor. They check the area for anything unsafe.

The home has changed for the robot.

Plates have a regular place. Storage is easy to reach. Furniture leaves clear paths. The family has learned that a careless object can become a stopped task.

The robot cleans, carries, and sorts. But the people still decide what belongs where. They still decide what must never be touched.



This future could follow if robots connect with household appliances and learn several limited tasks. Cleaning, carrying, sorting, and simple dishwashing might become one connected service.

But the robot may also change the design of the home.

A room made for people alone can be full of narrow gaps, loose cables, fragile objects, and irregular storage. A room made for people and robots may be easier to map and easier to move through. Its objects may have fixed places. Its surfaces may be chosen for automatic cleaning.

The house could become calmer.

It could also become less forgiving. A messy room may not only look untidy. It may block the machine. A home may begin to reward people who organize their things in ways the robot can understand.

The promise is freedom from repeated work.

The fear is that people will start organizing their lives around the needs of the machine.

## The Real Future of Housework

The most exciting future is not a robot that performs every chore perfectly.

It is a home where a person can teach a machine a new task, watch it learn, and then step away. It is a home where laundry, dishes, objects, and floors move through the day with less human effort.

The most worrying future is also not a robot that suddenly takes control.

It is a quieter future. People may become supervisors of endless automatic cleaning. They may spend less time holding a vacuum, but more time preparing rooms, checking errors, and deciding what the machine is allowed to touch.

If these systems mature, housework may become less about doing everything by hand. It may become the art of setting the home so that a robot can act inside it.

And when the robot stops, the human will still be the one who knows why.

**The future home may not be chore-free; it may be a home where humans are called only when the mess becomes too strange for a machine to understand.**
```

### A2: 内部版(Layer構造マーカー付き、Writer生の出力+Local Rewrite反映後)

```
## The First Quiet Change

The future of home robots may not begin with a machine that does everything.

It may begin with a machine that keeps the floor from becoming dirty.

In 2023, more than 2.1 million domestic floor-cleaning robots were sold around the world. They made up about 57% of all domestic service robots in that market. In the United States, 15% of adults said they owned a robot vacuum. Another 38% said they were interested in a robot that could help with household chores.

But a robot vacuum is not a full replacement for a person.

It is better at regular maintenance than deep cleaning. In one home study, it performed worse than a manual vacuum, or could not clean at all, on seven of nine types of surfaces. It could not clean stairs or ceilings. Cords, pet waste, and bowls remained among the obstacles used to assess its avoidance.

This limit may shape the future more than the dream of a perfect machine.

If floor robots continue to spread, home cleaning could change from one large weekly battle into many small daily actions. Human hands would still handle stairs, deep dirt, and difficult spaces. The robot would protect the ordinary parts of the home.

## Around 2030: The House That Is Always Being Maintained

[[IMAGINED: around 2030]]

Picture a Tuesday morning in 2030. The family is still asleep, but a small cleaning robot is moving across the floor. It slows near a chair. It waits for a person to pass. It turns away from a toy and returns later.

The floor is not perfectly clean. It does not need to be. Dust and crumbs are removed little by little. The home is kept ready by many short cleaning runs.

On the weekend, a person takes the manual vacuum to the stairs. They clean a deep stain near the kitchen. They reach the places the robot cannot reach.

The family does not say, “The robot cleaned the whole house.” They say, “The house stayed under control.”

[[/IMAGINED]]

This future could appear if automatic cleaning becomes normal, but remains limited to the right surfaces and spaces.

It could also bring a strange result. Automation may reduce the time people spend cleaning by hand, while increasing the total amount of cleaning. A long home study found this pattern during a period of floor-cleaning automation. Cleaning happened more often, and the machines ran for more total time, even as manual cleaning time fell.

The home might become cleaner because it is cleaned more often.

It might also become more demanding. Once a robot cleans every day, a little dirt may feel like a failure. The machine would save hands and time, but it could quietly raise the standard of cleanliness.

## The Robot That Does Not Just Vacuum

The next step could be small movements.

A robot vacuum with a mechanical arm can move some objects. Newer research and demonstrations show robots learning tasks such as folding laundry or handling dishes. Other systems are being designed to understand spoken instructions, see objects, plan actions, and change their movements while working.

This is a large jump from moving across a floor.

Yet it does not create a magic servant. A robot may recognize a shirt but fail to understand how a tangled shirt should be handled. It may know where a plate belongs but not know whether the plate is clean. It may stop when an object is unfamiliar.

The important question may not be, “Can the robot do housework?”

The question may be, “What kind of housework can the robot do without help?”

## Around 2035: People Teach the Exceptions

[[IMAGINED: around 2035]]

Picture a laundry room in 2035. A resident places a basket near a household robot. They give a short demonstration. This shirt goes on this shelf. Towels go in that drawer. Socks go in a small container.

The robot watches. It tries the task. It picks up a shirt, folds it, and carries it to the correct place.

Then it finds a tangled piece of clothing. The robot stops.

“Please check this item,” it says.

The resident removes the knot. The robot continues.

The family no longer gives the robot every instruction. They handle the unusual moments. The robot handles the repeated pattern.

Housework has not vanished. Its shape has changed. People manage the exceptions, while the machine repeats the ordinary work.

[[/IMAGINED]]

This future could become possible if home robots learn from short demonstrations and respond to feedback. It would require more than a strong arm. The robot would need to understand language, recognize objects, plan several steps, and notice when its plan was failing.

It would also need a way to ask for help.

A household robot might work alone most of the time. But difficult cases could require a person nearby, or a remote operator. This means the future home may not be fully automatic. It may depend on a new kind of service, where the machine works until human judgment is needed.

That could make the robot useful.

It could also make the robot hard to trust. A person might leave the house believing that laundry is being folded, only to return to a robot waiting beside one unknown shirt. The hardest part of housework may be the part that does not fit the robot’s learned pattern.

## Around 2040: A Home Built for Machines

[[IMAGINED: around 2040]]

Picture an evening in 2040. In the kitchen, a household robot carries used dishes toward their place. It works with the oven, the refrigerator, and storage areas. In the living room, it gathers toys and shoes.

Before the robot begins, the family clears away a charging cable. They move a small object from the floor. They check the area for anything unsafe.

The home has changed for the robot.

Plates have a regular place. Storage is easy to reach. Furniture leaves clear paths. The family has learned that a careless object can become a stopped task.

The robot cleans, carries, and sorts. But the people still decide what belongs where. They still decide what must never be touched.

[[/IMAGINED]]

This future could follow if robots connect with household appliances and learn several limited tasks. Cleaning, carrying, sorting, and simple dishwashing might become one connected service.

But the robot may also change the design of the home.

A room made for people alone can be full of narrow gaps, loose cables, fragile objects, and irregular storage. A room made for people and robots may be easier to map and easier to move through. Its objects may have fixed places. Its surfaces may be chosen for automatic cleaning.

The house could become calmer.

It could also become less forgiving. A messy room may not only look untidy. It may block the machine. A home may begin to reward people who organize their things in ways the robot can understand.

The promise is freedom from repeated work.

The fear is that people will start organizing their lives around the needs of the machine.

## The Real Future of Housework

The most exciting future is not a robot that performs every chore perfectly.

It is a home where a person can teach a machine a new task, watch it learn, and then step away. It is a home where laundry, dishes, objects, and floors move through the day with less human effort.

The most worrying future is also not a robot that suddenly takes control.

It is a quieter future. People may become supervisors of endless automatic cleaning. They may spend less time holding a vacuum, but more time preparing rooms, checking errors, and deciding what the machine is allowed to touch.

If these systems mature, housework may become less about doing everything by hand. It may become the art of setting the home so that a robot can act inside it.

And when the robot stops, the human will still be the one who knows why.

**The future home may not be chore-free; it may be a home where humans are called only when the mess becomes too strange for a machine to understand.**
```

### A2: QA結果

- run_summary: {"level": "a2", "word_count": 1344, "marker_check_initial": {"balanced": true, "open_count": 3, "close_count": 3, "matched_blocks": 3}, "writer_attempts": 1, "fact_check_verdict": "REVIEW_REQUIRED", "deviation_overall_status": "LEDGER_COMPLIANT", "local_rewrite_cycles_used": 1, "future_framing_qa_overall_status": "PASS", "present_tense_leakage_heuristic_hits": 0, "unhedged_future_claims_heuristic_hits": 1, "overall_status": "NG_REVIEW_REQUIRED"}
- Fact Checker A'(Layer1のみ): verdict=REVIEW_REQUIRED
  - unsupported_specific_claims:
    - 「2023年に世界でmore than 2.1 million台が販売された」という表現は、IFRの本文が「more than 2 million units」、見出しが「2.1 million」としている内容より強く、厳密には裏付けが不足しています。IFRの「close to 57%」という割合は確認できます。 ([ifr.org](https://ifr.org/post/21-million-domestic-floor-cleaning-robots-sold-in-2023))
    - 「15%が所有」と「38%が関心を持つ」は、それぞれ2025年5月のYouGov調査と2025年2月の別のYouGov調査に基づく数値です。数値自体は確認できますが、記事では別調査であることや調査時期が示されていません。 ([yougov.com](https://yougov.com/en-us/articles/52206-how-americans-use-and-replace-their-vacuum-cleaners?utm_source=openai))
    - 「ロボットは通常のメンテナンスに向き、深い清掃には向かない」という表現は、確認できた研究の直接的な結論というより記事側の要約・解釈です。研究は、ロボット掃除機が9種類の床面のうち7種類で手動掃除機より劣るか、まったく清掃できなかったこと、階段や天井を掃除できないことを示しています。 ([rucforsk.ruc.dk](https://rucforsk.ruc.dk/ws/portalfiles/portal/106122597/VacuumCleanerUX_IWC2024_AuthorVersion.pdf))
    - 「折りたたみ洗濯物や食器を扱うロボットが学習している」という記述は、研究・実演の存在としては概ね確認できますが、実験環境、遠隔操作、事前学習、限定された課題である場合があります。Mobile ALOHAの公式資料も、50回のデモンストレーション後に特定課題を自律実行できると説明する一方、一般家庭で汎用的に家事を遂行できることまでは示していません。 ([mobile-aloha.github.io](https://mobile-aloha.github.io/))
  - notes: 指定どおり、Around 2030、Around 2035、Around 2040の想像上の場面は判定対象から除外しました。記事の中心的な事実関係には大きな矛盾はありませんが、販売台数の表現の精度、別調査の数値を並べる際の文脈不足、研究実演を家庭での汎用的・自律的な能力と受け取られ得る点があるため、PASSではなくREVIEW_REQUIREDと判定します。
- Ledger Deviation Checker(Layer1のみ、hook_aware=False): overall_status=LEDGER_COMPLIANT、MAJOR件数=0
  - Local Rewrite発火: 1 cycle(詳細は`a2/local_rewrite_log.json`)
- Future Framing QA(Layer2/3のみ、新設): overall_status=PASS、{"framing_violations": 0, "fabricated_present_facts": 0, "unlabeled_assumptions": 0, "discovery_style_leakage": 0, "future_stated_as_fact_outside_scenes": 0}

### A2: 評価表(0〜2点、主観・該当文引用必須)

| 観点 | 点 | 根拠(該当文引用) |
|---|---|---|
| 面白さ(わくわく/不安の強度) | 2/2 | "The fear is that people will start organizing their lives around the needs of the machine." |
| Futureらしさ(未来像の具体性・印象) | 2/2 | "Picture a laundry room in 2035. A resident places a basket near a household robot... Then it finds a tangled piece of clothing. The robot stops." |
| Discovery/Trend化していないか | 2/2 | 研究名・出典・サンプルサイズは想像場面の外側で1段落分の足場としてのみ使われ("In one home study, it performed worse than a manual vacuum...on seven of nine types of surfaces.")、3つの想像場面本文には研究・出典への言及がない。 |
| 事実と想像の区別 | 2/2 | Future Framing QA: fabricated_present_facts=0件、future_stated_as_fact_outside_scenes=0件、overall_status=PASS(枠外で確定事実化した未来文・捏造現在事実は0件)。 |
| throughline | 2/2 | "Housework has not vanished. Its shape has changed."(2035場面内)と、"the human will still be the one who knows why"(結び)が同じ筋(自動化は消滅ではなく形を変える)で一貫。 |
| 1ナレーターの自然さ | 2/2 | 全編を通じて単一の語り手視点のみ(Voice切替なし)。 |
| 時間軸の明示 | 2/2 | 見出し"Around 2030"/"Around 2035"/"Around 2040"で明示。 |
| **合計** | **14/14** | |

## B1

### B1: 読者向け最終本文(マーカー除去後)

```
# The House That Never Stops Cleaning

## The first robot is not a servant

The future of home robots may begin with a simple change: not a machine that cleans the whole house, but a machine that keeps the floor ready for life.

In 2023, more than 2.1 million domestic floor-cleaning robots were sold worldwide. They made up about 57% of all household service robots tracked in that market. Floor cleaning is already the main doorway into home robotics.

But this doorway is much smaller than many people imagine. A robot vacuum can maintain a tidy floor, yet it is not a complete replacement for a human with a vacuum cleaner. In one household study, the robot performed worse than a manual vacuum, or could not clean at all, on seven of nine surfaces. It could not clean stairs or ceilings. Deep cleaning remained a human job.

That limit may not stop the technology. It may define its first success.

A 2025 survey found that 15% of U.S. adults said they owned a robot vacuum. Another survey found that 38% were interested in a robot that could help with household work. The desire is already larger than the ownership. If that gap continues to close, the first great promise of home robots may be simple: the house does not become perfectly clean. It stays acceptably clean without asking for attention every day.



Picture a weekday morning around 2030. A floor-cleaning robot moves quietly through the home, changing its path when people cross the room. It works around the family’s daily movement instead of waiting for the house to become empty.

No one expects it to clean the stairs. No one sends it after deep dirt in the corners. On the weekend, a person still carries a manual vacuum to the places the robot cannot reach.

But the old cleaning routine has disappeared. The family no longer waits for one long battle with dust. The robot runs often, for shorter periods, keeping the floor under control. The home is maintained little by little.

The people spend less time doing the work by hand. At the same time, the cleaning machine runs more often than anyone once expected. The house is not free from cleaning. It is always, quietly, in the middle of cleaning.



This future could arrive because automation changes the meaning of “done.” A home may no longer need one perfect cleaning session. It may need a constant, low-level effort.

That sounds convenient. It also creates a strange new rule: the robot saves human effort, but it may make cleaning more frequent. One long task becomes many small machine tasks. The home feels cleaner, but the machine becomes part of the home’s rhythm.

## The second shift: from floors to objects

The next step could be more difficult. Dust has no arms, no shape to protect, and no personal meaning. Clothing, dishes, toys, and shoes are different.

Some machines are already moving toward this problem. The Roborock Saros Z70, for example, is a robot vacuum with a five-axis folding mechanical arm. It is designed to recognize and move objects when the user sets it up through an app. It is still a robot vacuum with an added function, not a general servant that understands every room.

A planned household robot called Isaac 1 points toward a wider role. Its announced tasks include collecting dirty clothes, folding and storing laundry, making beds, and organizing toys, shoes, and scattered objects. The company has described a purchase price of $7,999 or a monthly subscription of $449, with early shipments planned for California in autumn 2026 and wider U.S. expansion planned by 2027. These are announced plans, not proof that such robots will quickly become common.

The hard part is not simply making a robot move. It must understand what an object is, decide where it belongs, and know what to do when the object is unusual. A tangled shirt is not like a folded towel. A child’s toy is not like a shoe. A strange object may not have a safe or obvious place.

A general home robot would need to understand instructions, watch its own work, and change its plan when the real world refuses to cooperate. If that combination becomes reliable, housework could change from direct labor into supervision.



Picture a Tuesday evening in 2035. A resident stands beside a basket of laundry and gives the robot a short demonstration. These clothes go in this drawer. Towels go on that shelf. Socks are placed in the small box.

The robot watches, then begins. It collects the clothes, carries them to the table, folds the pieces, and places them in the chosen spaces. A voice asks it to continue with the next basket.

Then it finds a shirt twisted inside a pair of trousers. The robot stops. It does not pull harder. It does not guess. A message appears: “Please check this item.”

The resident fixes the problem and sends the robot back to work. Most of the task is now automatic. The human handles the exceptions.

Housework has not vanished. Its center has moved. The important skill is no longer folding every shirt. It is teaching the robot the home’s rules and answering when the home becomes unpredictable.



This future could depend on a new kind of relationship between people and machines. Research systems have explored how robots can learn new tasks from a short human demonstration. Other demonstrations have shown robots folding laundry or attempting parts of dishwashing. These results suggest a direction, but they do not yet mean that a mass-produced household robot can safely manage every home.

The likely path is not complete independence. It is shared responsibility. The robot does the repeated work. The person sets the rules, gives the first example, and appears when the robot reaches a difficult case.

That may feel like freedom. It may also feel like having a very strong, very expensive employee who constantly asks questions.

## The house designed for the machine

The third shift may happen not inside the robot, but inside the home.

Today, people often arrange rooms for people. In a future with more capable robots, they might arrange rooms so machines can see, reach, carry, and return objects easily. Storage could become more regular. Important objects might receive fixed places. Loose cables and small items could be moved before the robot starts. A home that is easy for a robot may also be easier for a person to keep in order.

This could create a new kind of comfort. A robot might connect with household appliances, collect objects, place dishes, and move clothes through a series of tasks. But it could also create pressure. The home may need to follow the robot’s rules before the robot can follow the human’s wishes.

Manufacturers are already showing ideas for this wider role. LG CLOiD has been presented with two arms, independent fingers, cameras, sensors, and a moving base. Demonstrations have been planned around taking milk from a refrigerator, placing food in an oven, and folding clothes. These are presentation-stage examples, not proof of ordinary home performance.

The closer robots come to human spaces, the more important their mistakes become. Testing still pays attention to objects such as cords, bowls, and pet waste. A robot that fails to pick up dust is disappointing. A robot that grabs the wrong object, spreads a mess, or moves something important creates a new problem.



Picture an evening in 2040. In the kitchen, the home robot receives a simple instruction: clear the table and prepare the dishes for washing.

Before it begins, the room is ready. Cords have been moved. Small objects are off the floor. Pet waste is nowhere near the robot’s path. Plates and cups have assigned places, because the robot works best when the home has clear rules.

The robot carries dishes to the washing area, returns a few items to storage, and places a toy in a box. It works with the home’s appliances, moving between the kitchen and the living room.

The family is not watching every movement. But they have shaped the room for the robot. They have chosen what it may touch, where things belong, and when it must stop.

The home is cleaner, but it is also more organized around the machine. The robot has entered the family’s space. Now the family has entered the robot’s system.



If this future arrives, the greatest change may not be that robots perform more chores. It may be that homes become easier or harder to live in depending on how well they fit the robot.

The dream is a house where the boring work fades into the background. The fear is a house where every object must behave correctly. A home full of flexible human life could become a difficult environment for a machine. A home made easy for the machine could begin to feel less flexible for the people inside it.

## The choice hidden inside the convenience

Home robots may not give people a life without housework. They could give people a life with fewer repeated actions, fewer heavy routines, and fewer moments spent cleaning the same floor again.

But the remaining work may become more important. Someone must decide what the robot is allowed to do. Someone must prepare the room. Someone must answer when the machine cannot tell a towel from a shirt, or a toy from a problem.

The future of housework could therefore be neither human-only nor robot-only. It could be a new division: machines handle repetition, while people handle meaning, risk, and surprise.

**The home of the future may not be free from chores—it may be a home where even the mess must learn to live with a robot.**
```

### B1: 内部版(Layer構造マーカー付き、Writer生の出力)

```
# The House That Never Stops Cleaning

## The first robot is not a servant

The future of home robots may begin with a simple change: not a machine that cleans the whole house, but a machine that keeps the floor ready for life.

In 2023, more than 2.1 million domestic floor-cleaning robots were sold worldwide. They made up about 57% of all household service robots tracked in that market. Floor cleaning is already the main doorway into home robotics.

But this doorway is much smaller than many people imagine. A robot vacuum can maintain a tidy floor, yet it is not a complete replacement for a human with a vacuum cleaner. In one household study, the robot performed worse than a manual vacuum, or could not clean at all, on seven of nine surfaces. It could not clean stairs or ceilings. Deep cleaning remained a human job.

That limit may not stop the technology. It may define its first success.

A 2025 survey found that 15% of U.S. adults said they owned a robot vacuum. Another survey found that 38% were interested in a robot that could help with household work. The desire is already larger than the ownership. If that gap continues to close, the first great promise of home robots may be simple: the house does not become perfectly clean. It stays acceptably clean without asking for attention every day.

[[IMAGINED: around 2030]]

Picture a weekday morning around 2030. A floor-cleaning robot moves quietly through the home, changing its path when people cross the room. It works around the family’s daily movement instead of waiting for the house to become empty.

No one expects it to clean the stairs. No one sends it after deep dirt in the corners. On the weekend, a person still carries a manual vacuum to the places the robot cannot reach.

But the old cleaning routine has disappeared. The family no longer waits for one long battle with dust. The robot runs often, for shorter periods, keeping the floor under control. The home is maintained little by little.

The people spend less time doing the work by hand. At the same time, the cleaning machine runs more often than anyone once expected. The house is not free from cleaning. It is always, quietly, in the middle of cleaning.

[[/IMAGINED]]

This future could arrive because automation changes the meaning of “done.” A home may no longer need one perfect cleaning session. It may need a constant, low-level effort.

That sounds convenient. It also creates a strange new rule: the robot saves human effort, but it may make cleaning more frequent. One long task becomes many small machine tasks. The home feels cleaner, but the machine becomes part of the home’s rhythm.

## The second shift: from floors to objects

The next step could be more difficult. Dust has no arms, no shape to protect, and no personal meaning. Clothing, dishes, toys, and shoes are different.

Some machines are already moving toward this problem. The Roborock Saros Z70, for example, is a robot vacuum with a five-axis folding mechanical arm. It is designed to recognize and move objects when the user sets it up through an app. It is still a robot vacuum with an added function, not a general servant that understands every room.

A planned household robot called Isaac 1 points toward a wider role. Its announced tasks include collecting dirty clothes, folding and storing laundry, making beds, and organizing toys, shoes, and scattered objects. The company has described a purchase price of $7,999 or a monthly subscription of $449, with early shipments planned for California in autumn 2026 and wider U.S. expansion planned by 2027. These are announced plans, not proof that such robots will quickly become common.

The hard part is not simply making a robot move. It must understand what an object is, decide where it belongs, and know what to do when the object is unusual. A tangled shirt is not like a folded towel. A child’s toy is not like a shoe. A strange object may not have a safe or obvious place.

A general home robot would need to understand instructions, watch its own work, and change its plan when the real world refuses to cooperate. If that combination becomes reliable, housework could change from direct labor into supervision.

[[IMAGINED: around 2035]]

Picture a Tuesday evening in 2035. A resident stands beside a basket of laundry and gives the robot a short demonstration. These clothes go in this drawer. Towels go on that shelf. Socks are placed in the small box.

The robot watches, then begins. It collects the clothes, carries them to the table, folds the pieces, and places them in the chosen spaces. A voice asks it to continue with the next basket.

Then it finds a shirt twisted inside a pair of trousers. The robot stops. It does not pull harder. It does not guess. A message appears: “Please check this item.”

The resident fixes the problem and sends the robot back to work. Most of the task is now automatic. The human handles the exceptions.

Housework has not vanished. Its center has moved. The important skill is no longer folding every shirt. It is teaching the robot the home’s rules and answering when the home becomes unpredictable.

[[/IMAGINED]]

This future could depend on a new kind of relationship between people and machines. Research systems have explored how robots can learn new tasks from a short human demonstration. Other demonstrations have shown robots folding laundry or attempting parts of dishwashing. These results suggest a direction, but they do not yet mean that a mass-produced household robot can safely manage every home.

The likely path is not complete independence. It is shared responsibility. The robot does the repeated work. The person sets the rules, gives the first example, and appears when the robot reaches a difficult case.

That may feel like freedom. It may also feel like having a very strong, very expensive employee who constantly asks questions.

## The house designed for the machine

The third shift may happen not inside the robot, but inside the home.

Today, people often arrange rooms for people. In a future with more capable robots, they might arrange rooms so machines can see, reach, carry, and return objects easily. Storage could become more regular. Important objects might receive fixed places. Loose cables and small items could be moved before the robot starts. A home that is easy for a robot may also be easier for a person to keep in order.

This could create a new kind of comfort. A robot might connect with household appliances, collect objects, place dishes, and move clothes through a series of tasks. But it could also create pressure. The home may need to follow the robot’s rules before the robot can follow the human’s wishes.

Manufacturers are already showing ideas for this wider role. LG CLOiD has been presented with two arms, independent fingers, cameras, sensors, and a moving base. Demonstrations have been planned around taking milk from a refrigerator, placing food in an oven, and folding clothes. These are presentation-stage examples, not proof of ordinary home performance.

The closer robots come to human spaces, the more important their mistakes become. Testing still pays attention to objects such as cords, bowls, and pet waste. A robot that fails to pick up dust is disappointing. A robot that grabs the wrong object, spreads a mess, or moves something important creates a new problem.

[[IMAGINED: around 2040]]

Picture an evening in 2040. In the kitchen, the home robot receives a simple instruction: clear the table and prepare the dishes for washing.

Before it begins, the room is ready. Cords have been moved. Small objects are off the floor. Pet waste is nowhere near the robot’s path. Plates and cups have assigned places, because the robot works best when the home has clear rules.

The robot carries dishes to the washing area, returns a few items to storage, and places a toy in a box. It works with the home’s appliances, moving between the kitchen and the living room.

The family is not watching every movement. But they have shaped the room for the robot. They have chosen what it may touch, where things belong, and when it must stop.

The home is cleaner, but it is also more organized around the machine. The robot has entered the family’s space. Now the family has entered the robot’s system.

[[/IMAGINED]]

If this future arrives, the greatest change may not be that robots perform more chores. It may be that homes become easier or harder to live in depending on how well they fit the robot.

The dream is a house where the boring work fades into the background. The fear is a house where every object must behave correctly. A home full of flexible human life could become a difficult environment for a machine. A home made easy for the machine could begin to feel less flexible for the people inside it.

## The choice hidden inside the convenience

Home robots may not give people a life without housework. They could give people a life with fewer repeated actions, fewer heavy routines, and fewer moments spent cleaning the same floor again.

But the remaining work may become more important. Someone must decide what the robot is allowed to do. Someone must prepare the room. Someone must answer when the machine cannot tell a towel from a shirt, or a toy from a problem.

The future of housework could therefore be neither human-only nor robot-only. It could be a new division: machines handle repetition, while people handle meaning, risk, and surprise.

**The home of the future may not be free from chores—it may be a home where even the mess must learn to live with a robot.**
```

### B1: QA結果

- run_summary: {"level": "b1", "word_count": 1629, "marker_check_initial": {"balanced": true, "open_count": 3, "close_count": 3, "matched_blocks": 3}, "writer_attempts": 1, "fact_check_verdict": "PASS", "deviation_overall_status": "LEDGER_COMPLIANT", "local_rewrite_cycles_used": 0, "future_framing_qa_overall_status": "PASS", "present_tense_leakage_heuristic_hits": 0, "unhedged_future_claims_heuristic_hits": 1, "overall_status": "PASS"}
- Fact Checker A'(Layer1のみ): verdict=PASS
  - notes: 明確な事実誤認や信頼できる情報との矛盾は確認できないためPASS。特にIsaac 1の価格・配送時期は、2026年9月13日時点でもWeave Roboticsが示している企業計画であり、記事自身も計画であって普及の証拠ではないと明記している。なお、記事中の将来予測や「家事の意味が変わる」といった部分は検証可能な事実ではなく、明確な事実主張としては扱わなかった。
- Ledger Deviation Checker(Layer1のみ、hook_aware=False): overall_status=LEDGER_COMPLIANT、MAJOR件数=0
- Future Framing QA(Layer2/3のみ、新設): overall_status=PASS、{"framing_violations": 0, "fabricated_present_facts": 0, "unlabeled_assumptions": 0, "discovery_style_leakage": 0, "future_stated_as_fact_outside_scenes": 0}

### B1: 評価表(0〜2点、主観・該当文引用必須)

| 観点 | 点 | 根拠(該当文引用) |
|---|---|---|
| 面白さ(わくわく/不安の強度) | 2/2 | "The home of the future may not be free from chores—it may be a home where even the mess must learn to live with a robot." |
| Futureらしさ(未来像の具体性・印象) | 2/2 | "Picture an evening in 2040. In the kitchen, the home robot receives a simple instruction: clear the table and prepare the dishes for washing." |
| Discovery/Trend化していないか | 1/2 | "LG CLOiD has been presented with two arms, independent fingers, cameras, sensors, and a moving base. Demonstrations have been planned around taking milk from a refrigerator..."の段落は、想像場面の外側とはいえ製品スペック列挙がやや前面化しており、A2よりDiscovery寄りの筆致。 |
| 事実と想像の区別 | 2/2 | Future Framing QA: 5項目全て0件、overall_status=PASS。Fact Checker A'もverdict=PASSでunsupported_specific_claims=0件。 |
| throughline | 2/2 | "machines handle repetition, while people handle meaning, risk, and surprise."が全場面の帰結として一貫して回収される。 |
| 1ナレーターの自然さ | 2/2 | 全編を通じて単一の語り手視点のみ。 |
| 時間軸の明示 | 2/2 | 見出し"around 2030"/"2035"/"2040"で明示。 |
| **合計** | **13/14** | |
