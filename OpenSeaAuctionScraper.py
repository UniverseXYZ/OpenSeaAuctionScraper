import requests
import time
import pickle

class OpenSeaAuctionScraper:
  def __init__(self, file_name='scrape.pkl'):
    self.API_BASE = "https://api.opensea.io/api/v1/events"
    self.API_PARAMS = {
      "collection_slug": "nfp",
      "event_type": "bid_entered",
      "limit": 300
    }

    self.file_name = file_name
    self.bidders = []

  def scrape(self, page=0):
    offset = max(0, ((page * 300) - 50))
    events = self.get_opensea_page(offset)
    num_events = len(events)

    if (num_events > 0):
      print(f"STATUS: Saving Page {page}")
      bidders = self.get_bidders(events)
      self.bidders.extend(bidders)

      if (num_events == 300):
          time.sleep(1)
          self.scrape(page+1)
      else:
        self.save_scrape()


  def save_scrape(self):
    bidders = self.remove_duplicates(self.bidders)
    with open(self.file_name, "wb") as fp:
      pickle.dump(bidders, fp)

  def load_scrape(self):
    with open(self.file_name, "rb") as fp:
       bidders = pickle.load(fp)
    return bidders

  def get_opensea_page(self, offset=0):
    self.API_PARAMS['offset'] = offset
    response = requests.get(self.API_BASE, params=self.API_PARAMS).json()
    events = response.get('asset_events')
    return events

  @staticmethod
  def get_bidders(events):
    return list(map(lambda e: e.get('from_account').get('address'), events))

  @staticmethod
  def remove_duplicates(l):
    return list(set(l))
  
def main():
  scraper = OpenSeaAuctionScraper()
  scraper.scrape()
  bidders = scraper.load_scrape()
  num_bidders = len(bidders)
  print(f"{num_bidders} bidders in database")

if __name__ == "__main__":
  main()
