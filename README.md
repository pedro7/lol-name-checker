# lol-name-checker
Checks when a League of Legends summoner name will be available.

## Usage:
~~~~ python
from checker import Checker

# paste your API key here
key = ''

# choose your desired server (br, eune, euw, lan, las, na, oce, ru, tr, jp, kr)
server = ''

checker = Checker(key, server)

print(checker.check_name('desired_name'))
~~~~

The code below prints when the summoner name "Red" will be available in the north american server.

~~~~ python
from checker import Checker

na = Checker('RGAPI-bc8d0641-aec7-4992-9d44-9fc43700ed3e', 'NA')

print(na.check_name('Red'))
~~~~

You can get a key at: https://developer.riotgames.com
