from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from last_fm_api import LastFMApi
from utils import split_to_chunks, flatten_list, reset_cache
from exporter import Exporter
from alive_progress import alive_bar
import argparse


def export_songs(api, pool_size):
  result = []
  page_count = api.get_pages_count()
  print(page_count)
  items = list(split_to_chunks(
    [*range(1, page_count+1)], page_count // pool_size))

  with ThreadPoolExecutor(pool_size) as executor:
    futures = [executor.submit(api.get_songs, pages) for pages in items]
    with alive_bar(len(items)) as bar:
      for future in as_completed(futures):
        result.append(future.result())
        bar()

    return flatten_list(result)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description="Pull all of the scrobbels data for a Last FM user")
  parser.add_argument("--use-cache", default=True, type=bool, choices=[
                      "true", "false"], help="In order to be nice to LastFM cache the raw data locally", dest="use_cache")
  parser.add_argument("--cache-folder", default="pages", type=str,
                      help="Where to save the downloaded files. Must be used with --use-cache", dest="cache_folder")
  parser.add_argument("--reset-cache", default=False,
                      help="Remove all of the cached data", dest="reset_cache", action="store_true")
  parser.add_argument("--delay", default=2, type=int,
                      help="Static delay between each time we grab a page", dest="delay")
  parser.add_argument("--export-csv",
                      help="Save ouput to CSV", dest="export_csv", action="store_true")
  parser.add_argument("--export-json",
                      help="Save ouput to JSON", dest="export_json", action="store_true")
  parser.add_argument("--export-database",
                      help="Save ouput to sql database", dest="export_db", action="store_true")
  parser.add_argument("--threads", default=5, type=int,
                      help="The amount of threads to use", dest="threads")
  parser.add_argument("username", type=str, help="The username to scrap")

  args = parser.parse_args()
  if args.reset_cache:
    reset_cache(args.cache_folder)

  api = LastFMApi(
    use_chace=args.use_cache,
    cache_folder=args.cache_folder,
    delay=args.delay,
    username=args.username
  )

  songs = export_songs(api, args.threads)
  Exporter(args.export_csv, args.export_json,
           args.export_db, "out").export(songs)
