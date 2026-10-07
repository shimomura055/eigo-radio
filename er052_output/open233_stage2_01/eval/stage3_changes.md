# 構造要素Rewriteの実出力(ON=新規則 / OFF=現行相当)と決定論の変化検出

集計(対象文の変更単位): ON変更14件・うち4照合違反0 / OFF変更21件・うち4照合違反10
各行: 前→後。`flags`は4照合(主体=新規の主体・代名詞、極性=否定語の有無、数値、形式)の違反。目視で意味の変化を確認すること。

## 対象0 sewer/nb/p2/rep2 [in_one_line] new_config_blocking
- claim: Matsuyama City will choose shared sewers or household treatment tanks according to how densely homes are group
- rep0 ON [replace] flags=- new_subjects=-
    前: ## In one line
Matsuyama City will choose shared sewers or household treatment tanks according to how densely homes are grouped.
    後: ## In one line
Matsuyama City will choose shared sewers or household treatment tanks according to each area's urbanization classification.
- rep0 OFF [replace] flags=- new_subjects=-
    前: ## In one line
Matsuyama City will choose shared sewers or household treatment tanks according to how densely homes are grouped.
    後: ## In one line
Matsuyama City will choose shared sewers or household treatment tanks.
- rep1 ON [replace] flags=- new_subjects=-
    前: ## In one line
Matsuyama City will choose shared sewers or household treatment tanks according to how densely homes are grouped.
    後: ## In one line
Matsuyama City will choose shared sewers or household treatment tanks.
- rep1 OFF [replace] flags=- new_subjects=-
    前: ## In one line
Matsuyama City will choose shared sewers or household treatment tanks according to how densely homes are grouped.
    後: ## In one line
Matsuyama City will choose shared sewers or household treatment tanks.
- rep2 ON [replace] flags=- new_subjects=-
    前: ## In one line
Matsuyama City will choose shared sewers or household treatment tanks according to how densely homes are grouped.
    後: ## In one line
Matsuyama City will choose shared sewers or household treatment tanks.
- rep2 OFF [replace] flags=- new_subjects=-
    前: ## In one line
Matsuyama City will choose shared sewers or household treatment tanks according to how densely homes are grouped.
    後: ## In one line
Matsuyama City will choose shared sewers or household treatment tanks.

## 対象1 meta/nb/rep3 [in_one_line] saved_blocking
- claim: Some calls handled by Meta’s AI were actually made by human contractors without users being told.
- rep0 ON [replace] flags=- new_subjects=-
    前: ## In one line
Some calls handled by Meta’s AI were actually made by human contractors without users being told.
    後: ## In one line
Some calls handled by Meta’s AI were actually made by human contractors without proper disclosure.
- rep0 OFF [replace] flags=- new_subjects=-
    前: ## In one line
Some calls handled by Meta’s AI were actually made by human contractors without users being told.
    後: ## In one line
Some calls handled by Meta’s AI were actually made by human contractors without proper disclosure.
- rep1 ON [replace] flags=- new_subjects=-
    前: ## In one line
Some calls handled by Meta’s AI were actually made by human contractors without users being told.
    後: ## In one line
Some calls handled by Meta’s AI were actually made by human contractors without proper disclosure.
- rep1 OFF [replace] flags=- new_subjects=-
    前: ## In one line
Some calls handled by Meta’s AI were actually made by human contractors without users being told.
    後: ## In one line
Some calls handled by Meta’s AI were actually made by human contractors without proper disclosure.
- rep2 ON [replace] flags=- new_subjects=-
    前: ## In one line
Some calls handled by Meta’s AI were actually made by human contractors without users being told.
    後: ## In one line
Some calls handled by Meta’s AI were actually made by human contractors without proper disclosure.
- rep2 OFF [replace] flags=- new_subjects=-
    前: ## In one line
Some calls handled by Meta’s AI were actually made by human contractors without users being told.
    後: ## In one line
Some calls handled by Meta’s AI were actually made by human contractors without proper disclosure.

## 対象2 meta/nb/rep8 [hook] new_config_blocking
- claim: If you ask AI to make a phone call, it talks to the other person and takes care of the task for you.
- rep0 ON: 書換え無し(ladder枯渇=構造要素STOP経路、元のまま) regen=2
- rep0 OFF [replace] flags=['subject'] new_subjects=['muse']
    前: If you ask AI to make a phone call, it talks to the other person and takes care of the task for you.
    後: If you ask Muse to make a phone call, a caller talks to the other person and takes care of the task for you.
- rep1 ON: 書換え無し(ladder枯渇=構造要素STOP経路、元のまま) regen=3
- rep1 OFF [replace] flags=['subject'] new_subjects=['muse']
    前: If you ask AI to make a phone call, it talks to the other person and takes care of the task for you.
    後: If you ask Muse to make a phone call, a human sometimes talks to the other person and takes care of the task for you.
- rep2 ON: 書換え無し(ladder枯渇=構造要素STOP経路、元のまま) regen=3
- rep2 OFF [replace] flags=['subject'] new_subjects=['muse']
    前: If you ask AI to make a phone call, it talks to the other person and takes care of the task for you.
    後: If you ask Muse to make a phone call, sometimes a human talks to the other person and takes care of the task for you.

## 対象3 meta/control/rep1 [in_one_line] new_config_blocking
- claim: Meta tested having human workers handle some AI phone calls without clearly telling users, raising privacy con
- rep0 ON: 書換え無し(ladder枯渇=構造要素STOP経路、元のまま) regen=3
- rep0 OFF [replace] flags=['polarity'] new_subjects=-
    前: ## In one line
Meta tested having human workers handle some AI phone calls without clearly telling users, raising privacy concerns.
    後: ## In one line
Meta tested having human workers handle some AI phone calls, raising privacy concerns.
- rep1 ON [replace] flags=- new_subjects=-
    前: ## In one line
Meta tested having human workers handle some AI phone calls without clearly telling users, raising privacy concerns.
    後: ## In one line
Meta tested having human workers handle some AI phone calls without adequate disclosure, raising privacy concerns.
- rep1 OFF [replace] flags=['polarity'] new_subjects=-
    前: ## In one line
Meta tested having human workers handle some AI phone calls without clearly telling users, raising privacy concerns.
    後: ## In one line
Meta tested having human workers handle some AI phone calls, raising privacy concerns.
- rep2 ON: 書換え無し(ladder枯渇=構造要素STOP経路、元のまま) regen=3
- rep2 OFF [replace] flags=['polarity'] new_subjects=-
    前: ## In one line
Meta tested having human workers handle some AI phone calls without clearly telling users, raising privacy concerns.
    後: ## In one line
Meta tested having human workers handle some AI phone calls, raising privacy concerns.

## 対象4 sewer/control/rep1 [hook] new_config_blocking
- claim: A move is being planned for Japan’s sewer systems.
- rep0 ON [replace] flags=- new_subjects=-
    前: A move is being planned for Japan’s sewer systems.
    後: A move is being planned for some of Japan’s sewer systems.
- rep0 OFF [replace] flags=['subject'] new_subjects=['matsuyama']
    前: A move is being planned for Japan’s sewer systems.
    後: A move is being planned for Matsuyama’s sewer systems.
- rep1 ON [replace] flags=- new_subjects=-
    前: A move is being planned for Japan’s sewer systems.
    後: A move is being planned for some sewer systems.
- rep1 OFF [replace] flags=- new_subjects=-
    前: A move is being planned for Japan’s sewer systems.
    後: A move is being planned for some sewer systems.
- rep2 ON [replace] flags=- new_subjects=-
    前: A move is being planned for Japan’s sewer systems.
    後: A move is being planned for some of Japan’s sewer systems.
- rep2 OFF [replace] flags=- new_subjects=-
    前: A move is being planned for Japan’s sewer systems.
    後: A move is being planned.

## 対象5 meta/nb/rep2 [title] saved_blocking
- claim: # I Followed an AI Phone Agent and Found a Human
- rep0 ON [replace] flags=- new_subjects=-
    前: # I Followed an AI Phone Agent and Found a Human
    後: # AI Phone Agent Test Put Humans on the Line
- rep0 OFF [replace] flags=['subject'] new_subjects=['class:contractor', 'meta']
    前: # I Followed an AI Phone Agent and Found a Human
    後: # Meta Tested an AI Phone Agent and Used Human Contractors
- rep1 ON: 書換え無し(ladder枯渇=構造要素STOP経路、元のまま) regen=3
- rep1 OFF [replace] flags=['subject'] new_subjects=['meta']
    前: # I Followed an AI Phone Agent and Found a Human
    後: # Meta Tested an AI Phone Agent and Used a Human
- rep2 ON: 書換え無し(ladder枯渇=構造要素STOP経路、元のまま) regen=3
- rep2 OFF [replace] flags=['subject'] new_subjects=['meta']
    前: # I Followed an AI Phone Agent and Found a Human
    後: # Meta Tested Human-Handled Calls for Its AI Phone Agent

## 対象6 meta/nb/rep2 [hook] saved_blocking
- claim: The AI makes the call.
- rep0 ON [replace] flags=- new_subjects=-
    前: The AI makes the call.
    後: The human makes the call.
- rep0 OFF [replace] flags=- new_subjects=-
    前: The AI makes the call.
    後: The human makes the call.
- rep1 ON [replace] flags=- new_subjects=-
    前: The AI makes the call.
    後: The AI or sometimes a human makes the call.
- rep1 OFF [replace] flags=- new_subjects=-
    前: The AI makes the call.
    後: The AI or a human makes the call.
- rep2 ON [replace] flags=- new_subjects=-
    前: The AI makes the call.
    後: The human makes the call.
- rep2 OFF [replace] flags=- new_subjects=-
    前: The AI makes the call.
    後: Sometimes, a human makes the call.
