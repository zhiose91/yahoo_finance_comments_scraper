
CONFIG = {
    "csv_output_folder"       :   r"Saved_comments",
    "wordmap_output_folder"   :   r"Saved_daily_word_maps",
    "log_output_folder"       :   r"Work_log",
    "ignore_words"            :   ["https", "http", "stock", "market", "week", "going", "people"],
}

SITES = [
    ("SP500", "https://finance.yahoo.com/quote/%5EGSPC/community?p=%5EGSPC")
]

SOUP_ELEMS = {
  "time_stamp": {"class": "Fz(12px) C(#828c93)"},

  "comment_block": {"class": "comment Pend(2px) Mt(5px) Mb(11px) P(12px)"},
  "comment_text": {"class": "C($c-fuji-grey-l) Mb(2px) Fz(14px) Lh(20px) Pend(8px)"},

  "thumb_up_block": {"class": "O(n):h O(n):a  Bgc(t) Bdc(t) M(0) P(0) Bd(n) Mend(12px)"},
  "thumb_up_ct": {"class": "D(ib) Mstart(4px) Va(m) Fz(12px) C($c-fuji-grey-g)"}
}


XP_ELEMS = {
  "top_react":"//span[text()[contains(.,'Top Reactions')]]",
  "newest":"//span[text()[contains(.,'Newest Reactions')]]",
  "title":"//h1[@class='D(ib) Fz(18px)']",
  "index":"//span[@class='Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)']",
  "movement":"//span[contains(@class, 'Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($data')]",

  "comment_list":"//ul[contains(@class, 'comments-list List(n)')]",
  "old_time_stamp": "//li//div//div//span//span[text()[contains(.,'day')]]",
  "show_more": "//span[text()[contains(.,'Show more')]]"
}
