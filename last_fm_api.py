from requests import get
from bs4 import BeautifulSoup, Tag
from datetime import datetime
from time import sleep
from typing import Union
from utils import url_decode, flatten_list, is_cached, read_from_cache, write_to_cache


class LastFMApi():
  def __init__(self, use_chace=True, cache_folder="pages", delay=2, username="") -> None:
    self.use_cache = use_chace
    self.cache_folder = cache_folder
    self.delay = delay
    self.url = f"https://www.last.fm/user/{username}/library"

  def get_page(self, page_num: int) -> str:
    if self.use_cache:
      if is_cached(page_num, self.cache_folder):
        return read_from_cache(f"{page_num}.html", self.cache_folder)

    page = get(f"{self.url}?page={page_num}").content.decode()
    if self.use_cache:
      write_to_cache(f"{page_num}.html", self.cache_folder, page)

    return page

  def get_single_list_page_soup(self, page_num: int) -> BeautifulSoup:
    return BeautifulSoup(
      self.get_page(page_num),
      "html.parser"
    )

  def get_property_by_class(self, soup: BeautifulSoup, class_name: str) -> list[Tag]:
    return soup.find_all(class_=class_name)

  def get_class_text(self, soup: BeautifulSoup, class_name: str) -> list[str]:
    return list(
      map(
        lambda artist: artist.text.strip(), self.get_property_by_class(soup, class_name)
      )
    )

  def get_artists(self, soup: BeautifulSoup) -> list[str]:
    return self.get_class_text(soup, "chartlist-artist")

  def get_names(self, soup: BeautifulSoup) -> list[str]:
    return self.get_class_text(soup, "chartlist-name")
  
  def extract_album_name(self, album: Tag) -> str:
    album_link = album.find("a")
    if album_link:
      album_link = album_link["href"]
      return url_decode(album_link[album_link.rindex("/")+1:])

    return ""

  def get_albums(self, soup: BeautifulSoup) -> list[str]:
    return list(
      map(
        self.extract_album_name,
        self.get_property_by_class(soup, "chartlist-image")
      )
    )

  def get_timestamps(self, soup: BeautifulSoup) -> list[datetime]:
    return list(
      map(
        lambda song: datetime.strptime(
          song.find("span")["title"], "%A %d %b %Y, %I:%M%p"
        ),
        self.get_property_by_class(soup, "chartlist-timestamp")
      )
    )

  def get_pages_count(self) -> int:
    return int(
      self.get_single_list_page_soup(1).find_all(
        class_="pagination-page")[-1].text.strip()
    )

  def get_page_data(self, soup: BeautifulSoup) -> Union[list[str], list[str], list[datetime], list[str]]:
    return self.get_names(soup), self.get_artists(soup), self.get_timestamps(soup), self.get_albums(soup)

  def merge_data(self, names: list[str], artists: list[str], timestamps: list[datetime], albums: list[str]) -> list[dict]:
    return [
      {
        "name": name,
        "artist": artists[i],
        "album": albums[i],
        "timestamp": timestamps[i]
      }
      for i, name in enumerate(names)
    ]

  def get_songs(self, pages: list[int]) -> list[dict]:
    songs = []
    for page_num in pages:
      if not is_cached(page_num, self.cache_folder):
        sleep(self.delay)

      soup = self.get_single_list_page_soup(page_num)
      songs.append(self.merge_data(*self.get_page_data(soup)))

    return flatten_list(songs)
