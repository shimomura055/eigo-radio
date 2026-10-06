# ledger_diff_p01 (判定なし/照合材料)
regex: duplicated(checker L428-446 equivalent)

- fact数 Before=15 After=15 / 追加=['MMHC-001', 'MMHC-002', 'MMHC-003', 'MMHC-004', 'MMHC-005', 'MMHC-006', 'MMHC-007', 'MMHC-008', 'MMHC-009', 'MMHC-010', 'MMHC-011', 'MMHC-012', 'MMHC-013', 'MMHC-014', 'MMHC-015'] 削除=['MUSE-HC-001', 'MUSE-HC-002', 'MUSE-HC-003', 'MUSE-HC-004', 'MUSE-HC-005', 'MUSE-HC-006', 'MUSE-HC-007', 'MUSE-HC-008', 'MUSE-HC-009', 'MUSE-HC-010', 'MUSE-HC-011', 'MUSE-HC-012', 'MUSE-HC-013', 'MUSE-HC-014', 'MUSE-HC-015']

## 共通factの集合差(空=差分0)
(差分あり 0/0)

## M4 claim行の新規括弧/番号/否定/因果
該当: なし

## 書式違反(M4: 日本語キー行/ブロック内空行)
- Before 0件 / After 0件

## ID不一致の類似候補(自動対応付けは確定しない)
- MUSE-HC-001: {"side": "before_only", "candidate_in_after": "MMHC-013", "jaccard": 0.238}
- MUSE-HC-002: {"side": "before_only", "candidate_in_after": "MMHC-013", "jaccard": 0.17}
- MUSE-HC-003: {"side": "before_only", "candidate_in_after": "MMHC-013", "jaccard": 0.119}
- MUSE-HC-004: {"side": "before_only", "candidate_in_after": "MMHC-002", "jaccard": 0.264}
- MUSE-HC-005: {"side": "before_only", "candidate_in_after": "MMHC-011", "jaccard": 0.208}
- MUSE-HC-006: {"side": "before_only", "candidate_in_after": "MMHC-001", "jaccard": 0.148}
- MUSE-HC-007: {"side": "before_only", "candidate_in_after": "MMHC-003", "jaccard": 0.327}
- MUSE-HC-008: {"side": "before_only", "candidate_in_after": "MMHC-008", "jaccard": 0.309}
- MUSE-HC-009: {"side": "before_only", "candidate_in_after": "MMHC-012", "jaccard": 0.167}
- MUSE-HC-010: {"side": "before_only", "candidate_in_after": "MMHC-012", "jaccard": 0.078}
- MUSE-HC-011: {"side": "before_only", "candidate_in_after": "MMHC-006", "jaccard": 0.214}
- MUSE-HC-012: {"side": "before_only", "candidate_in_after": "MMHC-007", "jaccard": 0.511}
- MUSE-HC-013: {"side": "before_only", "candidate_in_after": "MMHC-009", "jaccard": 0.878}
- MUSE-HC-014: {"side": "before_only", "candidate_in_after": "MMHC-010", "jaccard": 0.152}
- MUSE-HC-015: {"side": "before_only", "candidate_in_after": "MMHC-014", "jaccard": 0.102}
- MMHC-001: {"side": "after_only", "candidate_in_before": "MUSE-HC-006", "jaccard": 0.148}
- MMHC-002: {"side": "after_only", "candidate_in_before": "MUSE-HC-004", "jaccard": 0.264}
- MMHC-003: {"side": "after_only", "candidate_in_before": "MUSE-HC-007", "jaccard": 0.327}
- MMHC-004: {"side": "after_only", "candidate_in_before": "MUSE-HC-006", "jaccard": 0.088}
- MMHC-005: {"side": "after_only", "candidate_in_before": "MUSE-HC-009", "jaccard": 0.136}
- MMHC-006: {"side": "after_only", "candidate_in_before": "MUSE-HC-011", "jaccard": 0.214}
- MMHC-007: {"side": "after_only", "candidate_in_before": "MUSE-HC-012", "jaccard": 0.511}
- MMHC-008: {"side": "after_only", "candidate_in_before": "MUSE-HC-008", "jaccard": 0.309}
- MMHC-009: {"side": "after_only", "candidate_in_before": "MUSE-HC-013", "jaccard": 0.878}
- MMHC-010: {"side": "after_only", "candidate_in_before": "MUSE-HC-014", "jaccard": 0.152}
- MMHC-011: {"side": "after_only", "candidate_in_before": "MUSE-HC-005", "jaccard": 0.208}
- MMHC-012: {"side": "after_only", "candidate_in_before": "MUSE-HC-009", "jaccard": 0.167}
- MMHC-013: {"side": "after_only", "candidate_in_before": "MUSE-HC-001", "jaccard": 0.238}
- MMHC-014: {"side": "after_only", "candidate_in_before": "MUSE-HC-014", "jaccard": 0.118}
- MMHC-015: {"side": "after_only", "candidate_in_before": "MUSE-HC-002", "jaccard": 0.08}

## claim逐語併記
| fact_id | Before claim | After claim |
|---|---|---|
| MUSE-HC-001 | Metaは2026年9月8日、個人向けAIエージェント「Muse」を発表した。米国でiOS、Android、muse.ai向けに展開すると説明している。 | (なし) |
| MUSE-HC-002 | Metaの説明では、Museは専用のクラウド仮想マシン「Muse Secure VM」上で動作し、ブラウザーを開く、フォームに入力する、ユーザーに代わって交渉するなどの作業を実行できる。 | (なし) |
| MUSE-HC-003 | Metaの公式説明では、Muse Secure VMではユーザーごとに専用のクラウドコンピューターが割り当てられ、接続サービスのデータや認証情報を保存する。Sentinelという別のエージェントが外部通信やコネクター操作の許可を管理する。 | (なし) |
| MUSE-HC-004 | Museの電話機能では、ユーザーが米国内の企業・店舗へ電話をかけるよう指示し、散髪の予約、在庫確認、業者からの見積もり取得などを依頼できるとReutersが報じた。 | (なし) |
| MUSE-HC-005 | MetaはMuseの電話発信機能を、2026年8月から従業員にテストさせ、Museの一般公開後の数日間にユーザー向けへ段階的に展開したと、社内投稿に基づくReuters報道で伝えられた。 | (なし) |
| MUSE-HC-006 | MetaはMuse経由の電話の一部について、AIではなく訓練を受けた人間の契約スタッフが電話をかけ、相手とのやり取りを完了させる「human concierge」「human agent calls」のテストを実施した。 | (なし) |
| MUSE-HC-007 | 人間コンシェルジュ機能は、2026年9月22日のReuters報道時点で、Meta従業員の半数に有効化されていた。利用を望まない従業員向けにオプトアウト用のグループも設けられていた。 | (なし) |
| MUSE-HC-008 | Metaの社内投稿では、人間が電話を担当した一部テストで、成功率が95〜98%に達する可能性が示された。一方、AIだけで電話をかけた場合の成功率は、それより低いとされたが、具体的な数値は示されていない。 | (なし) |
| MUSE-HC-009 | 社内投稿では、MuseがAIだと認識した相手側から電話を切られる事例が報告された。報道では、保険会社がMuseのAI発信だと分かると繰り返し電話を切ったという従業員の報告が紹介された。 | (なし) |
| MUSE-HC-010 | Meta従業員は、人間の契約スタッフが電話を担当すると、電話中にユーザーの機微情報がコールセンターの契約スタッフへ意図せず共有される可能性があるとして、社内でプライバシー上の懸念を示した。 | (なし) |
| MUSE-HC-011 | Museにインターネット・ケーブル料金の交渉を依頼した従業員は、電話の記録に人間の契約スタッフによる人種に関する不適切な発言があったと報告した。 | (なし) |
| MUSE-HC-012 | MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。 | (なし) |
| MUSE-HC-013 | Metaの広報担当者Daniel Robertsは、従業員の反応は「圧倒的に肯定的」だったと述べ、テストの目的を、安全・プライバシー保護を実装し、公開前に機能を改善するためのフィードバック収集だと説明した。 | (なし) |
| MUSE-HC-014 | Metaは、電話機能について、商業者との改善を続け、準備が整い、適切な開示ができる場合にのみ公開展開すると広報担当者を通じて説明した。 | (なし) |
| MUSE-HC-015 | Metaは公式説明で、Museについて、ユーザーが接続アプリとアクセス権限を選択でき、メール送信や購入などの敏感な操作の前に確認を求め、操作履歴を表示すると説明している。 | (なし) |
| MMHC-001 | (なし) | Metaは、パーソナルAIアシスタント「Muse」を通じて発信される電話の一部を、人間の請負業者が処理する「human concierge」を試験していた。 |
| MMHC-002 | (なし) | Museの電話機能では、利用者が米国の事業者の電話番号に発信し、相手と話して、ヘアカットの予約、店舗在庫の確認、請負業者からの見積もり取得などを処理するよう指示できる。 |
| MMHC-003 | (なし) | Metaは、human concierge機能を2026年9月中旬に従業員の半数へ有効化した。対象に入りたくない従業員向けにオプトアウトグループが設けられた。 |
| MMHC-004 | (なし) | 社内告知では、Museが依頼を訓練を受けたエージェントに引き渡し、そのエージェントが電話をかけて対応を進める仕組みと説明された。 |
| MMHC-005 | (なし) | 社内投稿では、一部の従業員が、人間が電話を処理すると、機微情報がコールセンターの請負業者に意図せず共有される可能性があると懸念を示した。 |
| MMHC-006 | (なし) | あるMeta従業員は、Museにインターネット・ケーブル事業者との料金交渉を依頼した後、通話記録に人間の請負業者による人種差別的な言及が含まれていたと述べた。 |
| MMHC-007 | (なし) | MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに請負業者が電話をかけるテストを始めたことを「miss」と認め、human concierge機能を当面ロールバックしたと社内投稿で述べた。 |
| MMHC-008 | (なし) | Metaの副社長の投稿によると、一部のテストでは、人間が電話をかけた場合の成功率が95%から98%に達し、AIによる発信はそれより低い割合だった。 |
| MMHC-009 | (なし) | Metaの広報担当者Daniel Robertsは、従業員の反応は「overwhelmingly positive」だったと述べ、テストの目的を、公開前に安全性・プライバシー保護を実装し機能を改善するためのフィードバック収集だと説明した。 |
| MMHC-010 | (なし) | Robertsは、Metaは事業者とともに電話機能を改善しており、準備が整い、適切な開示を伴う場合にのみ一般公開すると述べた。 |
| MMHC-011 | (なし) | 社内投稿によると、MetaはMuseの電話機能を2026年8月に従業員で試し、Museアプリの公開後数日以内に利用者へ段階的に展開し始めた。 |
| MMHC-012 | (なし) | あるMeta従業員は、保険会社に電話するようMuseへ依頼したところ、相手がAIだと分かるとMuseとの通話を繰り返し切ったと報告した。 |
| MMHC-013 | (なし) | Metaは2026年9月8日、Museを発表し、Muse Secure VM上で動作する、エージェントと利用者のデータを収容する専用の仮想マシンだと説明した。 |
| MMHC-014 | (なし) | Metaは、Museについて、利用者が接続するアプリとアクセス範囲を選べ、アクセス権の変更やサービスとの接続解除をいつでも行えると説明した。 |
| MMHC-015 | (なし) | Metaは、Museの利用者の会話や仮想マシン内のデータをMetaの広告システムと共有しないと説明した。 |