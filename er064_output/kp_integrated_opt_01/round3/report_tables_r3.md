# report_tables_r3 (自動生成。Stage 0 b1供給品質。Stage 1は事前登録Go条件不成立のため未実施)

## b1供給品質(抽出run単位)
| 記事 | run | LLM生件数 | 逐語 | b2等との重複除外 | reject | accepted(rank順) | b1予約(Tier H後) | Tier H削除(既存) | 縮約ガード発動 | 費用 | reasoning tok | 秒 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D5 | 1 | 0 | 0/0 | [] | [] | [] | None | None | [] | 0.0491 | 318 | 5.274 |
| D6 | 1 | 1 | 1/1 | ['make up'] | [] | [] | None | None | [] | 0.0793 | 625 | 8.857 |
| N1 | 1 | 0 | 0/0 | [] | [] | [] | None | None | [] | 0.0452 | 266 | 4.055 |
| R3 | 1 | 3 | 3/3 | ['under way'] | [] | ['sleep inertia', 'gets the first word'] | None | None | [] | 0.2732 | 2924 | 32.33 |
| coffee_adv | 1 | 3 | 3/3 | ['your wallet pumps its fist'] | [] | ['in the ring', 'unseen clock of its own'] | ['in the ring', 'unseen clock of its own'] | [] | [] | 0.2988 | 3227 | 34.91 |
| coffee_adv | 2 | 3 | 3/3 | ['your wallet pumps its fist'] | [('had been behind price increases', 'excluded_by_existing_gate')] | ['in the ring'] | ['in the ring'] | [] | ['had been behind price increases'] | 0.227 | 2639 | 28.439 |
| coffee_adv | 3 | 3 | 3/3 | ['wallet pumps its fist'] | [] | ['unseen clock of its own', 'figures in the ring'] | ['unseen clock of its own', 'figures in the ring'] | [] | ['figures in the ring'] | 0.211 | 2431 | 27.089 |
| coffee_std | 1 | 3 | 3/3 | ['your wallet pumps its fist'] | [] | ['in the ring just yet', 'its own hidden clock'] | ['in the ring just yet', 'its own hidden clock'] | [] | ['in the ring just yet'] | 0.1511 | 1400 | 15.966 |
| coffee_std | 2 | 3 | 3/3 | ['your wallet pumps its fist'] | [] | ['numbers in the ring', 'hidden clock'] | ['numbers in the ring', 'hidden clock'] | [] | ['numbers in the ring'] | 0.1812 | 2070 | 22.757 |
| coffee_std | 3 | 3 | 3/3 | ['wallet pumps its fist'] | [] | ['in the ring', 'own hidden clock'] | ['in the ring', 'own hidden clock'] | [] | [] | 0.1398 | 1552 | 18.967 |
| hormuz_adv | 1 | 3 | 3/3 | ['gave back'] | [] | ['stood at center stage', 'curtain rose'] | ['stood at center stage', 'curtain rose'] | [] | [] | 0.2652 | 2823 | 31.331 |
| hormuz_std | 1 | 3 | 3/3 | [] | [] | ['stood at center stage', 'gave back some gains', 'refuses to stay down'] | ['stood at center stage', 'gave back some gains', 'refuses to stay down'] | [] | [] | 0.2572 | 2734 | 30.031 |
| meta_adv | 1 | 3 | 3/3 | ['behind the scenes'] | [] | ['small twist', 'on the other end'] | ['small twist', 'on the other end'] | [] | [] | 0.216 | 2223 | 26.619 |
| meta_std | 1 | 2 | 2/2 | ['behind the scenes'] | [] | ['in stock'] | ['in stock'] | [] | [] | 0.1748 | 1774 | 19.493 |
| semi_adv | 1 | 3 | 3/3 | ['catches the eye'] | [] | ['skip over this', 'fit for leading roles'] | ['skip over this', 'fit for leading roles'] | [] | [] | 0.2738 | 2902 | 31.903 |
| semi_std | 1 | 3 | 3/3 | [] | [] | ['take the seat', 'switch off quietly', 'feel heavy'] | ['take the seat', 'switch off quietly', 'feel heavy'] | [] | [] | 0.2 | 1999 | 22.312 |
| smallbag_adv | 1 | 3 | 3/3 | [] | [] | ['having a big moment', 'carry the mood', 'sits on the throne'] | ['having a big moment', 'carry the mood', 'sits on the throne'] | [] | [] | 0.1734 | 1690 | 18.903 |
| smallbag_std | 1 | 3 | 3/3 | [] | [] | ['having a big moment', 'on the throne', 'carry the mood'] | ['having a big moment', 'on the throne', 'carry the mood'] | [] | [] | 0.2435 | 2588 | 26.843 |

## 目視精度ラベル(LLM生span単位、暫定)
{'正': 31, '誤': 3, '粒度不良': 11, '未ラベル': 0} 精度(正/ラベル済)=0.689

- D5 run1: 
- D6 run1: make up=正
- N1 run1: 
- R3 run1: sleep inertia=正 / under way=正 / gets the first word=誤
- coffee_adv run1: your wallet pumps its fist=正 / in the ring=粒度不良 / unseen clock of its own=正
- coffee_adv run2: your wallet pumps its fist=正 / had been behind price increases=粒度不良 / in the ring=粒度不良
- coffee_adv run3: wallet pumps its fist=正 / unseen clock of its own=正 / figures in the ring=正
- coffee_std run1: in the ring just yet=粒度不良 / your wallet pumps its fist=正 / its own hidden clock=正
- coffee_std run2: your wallet pumps its fist=正 / numbers in the ring=正 / hidden clock=正
- coffee_std run3: in the ring=粒度不良 / wallet pumps its fist=正 / own hidden clock=粒度不良
- hormuz_adv run1: gave back=正 / stood at center stage=正 / curtain rose=正
- hormuz_std run1: stood at center stage=正 / gave back some gains=正 / refuses to stay down=正
- meta_adv run1: behind the scenes=正 / a small twist=誤 / on the other end=粒度不良
- meta_std run1: in stock=誤 / behind the scenes=正
- semi_adv run1: catches the eye=正 / skip over this=粒度不良 / fit for leading roles=正
- semi_std run1: take the seat=正 / switch off quietly=粒度不良 / your eyes feel heavy=粒度不良
- smallbag_adv run1: having a big moment=正 / carry the mood=正 / sits on the throne=正
- smallbag_std run1: having a big moment=正 / on the throne=粒度不良 / carry the mood=正

## 揺れ(Coffee)
{
 "coffee_std": {
  "accepted_sets": [
   [
    "in the ring just yet",
    "its own hidden clock"
   ],
   [
    "hidden clock",
    "numbers in the ring"
   ],
   [
    "in the ring",
    "own hidden clock"
   ]
  ],
  "jaccard_accepted_mean": 0.0,
  "jaccard_rawspan_mean": 0.067
 },
 "coffee_adv": {
  "accepted_sets": [
   [
    "in the ring",
    "unseen clock of its own"
   ],
   [
    "in the ring"
   ],
   [
    "figures in the ring",
    "unseen clock of its own"
   ]
  ],
  "jaccard_accepted_mean": 0.278,
  "jaccard_rawspan_mean": 0.233
 }
}

## 陰性対照
{"N1": {"raw_n": 0, "accepted": [], "dup": []}, "D6": {"raw_n": 1, "accepted": [], "dup": ["make up"]}, "D5": {"raw_n": 0, "accepted": [], "dup": []}, "R3": {"raw_n": 3, "accepted": ["sleep inertia", "gets the first word"], "dup": ["under way"]}}
accepted平均/呼出=0.5

## 既存run(Round1/2)のCI付き要約(b1なし)
| 条件(既存run、b1なし) | Std score(n) | Adv score(n) | 合算 [95%CI] | pump Std/Adv | time lag Adv | 低優先枠/run Std/Adv | 全gate PASS | 費用/job | reasoning tok sel Std/Adv |
|---|---|---|---|---|---|---|---|---|---|
| M2P0 | 33.3 (n=3) | 38.0 (n=3) | 71.3 [69.3, 73.3] | 3/3 , 3/3 | 3/3 | 1.67 / 0.67 | 2/3 , 3/3 | 0.879 / 0.897 | 3141 / 2842 |
| M2P5 | 32.4 (n=5) | 34.8 (n=5) | 67.2 [62.8, 71.2] | 5/5 , 4/5 | 5/5 | 1.2 / 0.4 | 5/5 , 5/5 | 1.025 / 0.944 | 5756 / 3473 |
