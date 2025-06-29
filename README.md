# catics

catics is a platform designed to evaluate and compare different strategies for the board game
[boop](https://boardgamegeek.com/boardgame/355433/boop).
You can create and code your own agents to implement specific strategies. Once defined, you can
either play against your custom agent, have two agents compete to evaluate their performance, or
simply play a match between two human players.

## Current status

For now, you can only play against human opponents, agents are coming soon.

## Notation

Each piece is represented using a combination of the player identifier and the piece type.
-	`p1` and `p2` denote player 1 and player 2, respectively.
-	`k` stands for a kitten, and `c` stands for a cat.

For example:
-	`p1k` refers to a kitten belonging to player 1.
-	`p2c` refers to a cat belonging to player 2.

## Requirements

- Python >= 3.11
- make

## Play

- Clone this repo
- run `make install`
- `cd cli`
- Create an account : `./register [username] [email]`
- Create a game with someone : `./play new -u [username]`

You can resume a game anytime with `./play resume [game_id]`

## Run your own instance

- Clone this repo
- run `make install`
- edit the file `catics/settings_local.py`
- run `make run`

You can select on which instance you want to play on with `./cli/set_instance [url]`
