# hansard-analysis
Analysis of UK parliamentary speech data (Hansard) exploring topic modelling, classification, and language trends across governments.

## Hansard Data 

Data accessed: 2026-06-17

Source: https://www.theyworkforyou.com/pwdata/

Votes: rsync -az --progress --exclude '.svn' --exclude 'tmp/' data.theyworkforyou.com::parldata/votes/ ./votes/
People: rsync -az --progress data.theyworkforyou.com::parldata/people.json .

Debates: rsync -az --progress --exclude '.svn' --exclude 'tmp/' data.theyworkforyou.com::parldata/scrapedxml/debates/ ./debates/
Divisions: rsync -az --progress --exclude '.svn' --exclude 'tmp/' data.theyworkforyou.com::parldata/scrapedxml/divisionsonly/ ./divisionsonly/

Source: github.com/mysociety/parlparse:

Ministers: curl -L https://raw.githubusercontent.com/mysociety/parlparse/master/members/ministers.json -o ministers.json
Minister 2010: curl -L https://raw.githubusercontent.com/mysociety/parlparse/master/members/ministers-2010.json -o ministers-2010.json


## government_timeline.json

A custom json file containing one row per continuous PM tenure under a single electoral mandate; entries split where a PM won re-election or where a government changed composition mid-parliament without an election

### Built From

- https://www.electoralcalculus.co.uk/commentary.html
- https://en.wikipedia.org/wiki/List_of_prime_ministers_of_the_United_Kingdom
- https://en.wikipedia.org/wiki/Leader_of_the_Opposition_(United_Kingdom)
- https://en.wikipedia.org/wiki/List_of_British_governments
- https://en.wikipedia.org/wiki/United_Kingdom_coalition_government

end_reason and notes were filled out by Gemini 3.1 Pro (https://gemini.google.com/app)