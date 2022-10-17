# Tabfile Dictionary

A small Python library for fast lookup of words in a tab-delimited dictionary.

It searches through all lemmas and inflections and returns all entries where either the headword or the inflection matches.

Testing it with a large dictionary, initializing it takes about 3-4 seconds, but then each lookup only takes one millisecond.


Install it using `git+https://github.com/Vuizur/tabfile-dictionary`

```
from tabfile_dictionary.dictionary import TabfileDictionary

dictionary = TabfileDictionary("spa_eng.txt")

entries = dictionary.lookup("oso")
for entry in entries:
print(entry.word, entry.definition)
```