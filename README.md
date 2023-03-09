# crawl chewy projecdt



## purpose

To get alert if the product is in stock


## usage

- Change the information below
  - PRODUCTS variable in `crawl.py`
  - Set env for slack hook url
- Add crontab like
  - `crontab -e`
    - Add `* * * * cd ~/directory_to/chewy-crawl/ && python crawl.py >> ~/directory_to_log/cron.log 2>&1`


## TODO

- [o] Don't send duplication messages over and over
  - using database or file
  - solve with using history.log

