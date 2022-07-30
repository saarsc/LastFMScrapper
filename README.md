# LastFM Scrapper

Pull all of your scrobbles from lastFM. Exports songs, artist, albums and scrobble timestamp

## Basic Usage

```bash
  python script.py username 
```

## Additional Flags

|flag|role|
|-|-|
--use-cache | Save the pages into a local folder to prevent spamming LastFM
--cache-folder | Where to save the cached files - default is "pages".
--reset-cache | Removed all of the cached files
--delay | Delay between each time we grab another page. Cached pages are not delayed
--export-csv | Save result to a CSV file
--export-json | Save result to JSON file
--export-db | Save result to local sqlfile **not supported ATM**
