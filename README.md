# Learning to play Hanabi

Hanabi is cooperative game: cards are of 5 different colours, with values ranging from 1 to 5. Each player sees everyone's cards but its own. 
The goal is to put all the play all the cards in the right order. 
Three actions are possible at each turn: 
  * Play a card: if the card is well played, the score increments. If not, penaltys increment. If penaltys = 3, the game stops. Take another card from the deck.
  * Discard a card: the card is not usable again, but this gives one point of information (POI), available to every player. Take another card from the deck.
  * Give information to another player, if POI > 0. Information may targets the colour OR the value of another player's cards. Information must be complete. This costs 1 POI. 

The game stops when all the cards have been played *or* when penaltys=3. The final reward is the score. 

Various papers aimed at designing an optimal policy. Yet, they often assumes that *all the players* play along the same policy. 

## Outline

I started by **computing the probabilities** of having each specific card in one's hand. I think it is a necessary information for a relevant decision to be made by the player. 

## More information

Visit the [wikipedia page](https://en.wikipedia.org/wiki/Hanabi_(card_game)) to get more information. Various papers can be found dealing with this game. 
