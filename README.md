# DocManager

## Motivation
I'm currently a Ph.D student who has huge amount of papers in hand. Sometimes, when you would like to search for one piece of paper, even though you are 100 percent sure that you have seen it before, you are searching a needle in a haystack. Furthermore, papers have heritage relationship with each other. One paper may be inspired by another one.  

I would like to create a tool to manage papers and preserve their connections.

## Language
Since I don't have time to familiar myself with other languages, python is the current development language I selected. I know that C++/Java may be better, since I'm in a hurry, I'll choose the language I'm comfortable with. 


## Progress
10/04/2019 I decede to ignore authors in papers and focus on the relationship between paper at present. Even though the corresponding relationships are created in the sql file, in the near future, I'm not going to realize it.

10/14/2019 The current version is a useable. The GUI version looks ugly but contains most of the useful functions. To run the GUI, execute

``` 
python3 src/DocManagerGUI.py
```
After running once, a configuration file *config.json* will be generated at the target folder. 
