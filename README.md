# CDL-Stats
An AIO for CDL statistics including a web scraper, data visualisation tools and machine learning models

## Setup

Firstly, import the requirements into the python (3.9 reccomended) environment of your choice.
This can be done by typing the following into the terminal:
> pip3 install -r requirements.txt

### How to Scrape Data from Cod-Fandom
To do this, you must:
- Download the contents of this repository
- Create a new python file
- Import the following function
  > from cod_fandom_formatter import major_csv
- Next, call the function with the parameters:
  > major_csv(major={major of your choice}, week={week of your choice})

## Initial Analysis of Some Imported Data
Some intial analysis of player data covering the entire year can be seen in the analysis folder. This contains breakdowns for different gamemodes and some other research into the data.
