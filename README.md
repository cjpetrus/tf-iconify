# tf-iconify
annotate your terraform graphs with aws icons. way too lazy to build a hashmap of services so decided to use some fuzzy matching instead
![Alt text](graph2.png?raw=true "Title")

useage:

1. you might want to run get_icons to download the iconset and autofix naming conventions.
2. pipe the terraform graph output into this python script.
3. magic. uses multiple fuzzy matching algorithms to match up the best icon with the infrastructure component