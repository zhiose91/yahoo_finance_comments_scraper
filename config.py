import re

CONFIG = {
    "csv_output_folder"       :   r"Saved_comments",
    "wordmap_output_folder"   :   r"Saved_daily_word_maps",
    "log_output_folder"       :   r"Work_log",
    "ignore_words"            :   ["https", "http", "stock", "market", "week", "going", "people"],
}

SITES = [
    ("SP500", "https://finance.yahoo.com/quote/%5EGSPC/community?p=%5EGSPC")
]

# Yahoo Finance frequently changes class names, use 'contains' for fuzzy matches
XP_ELEMS = {
  "top_react"       :   "//span[text()[contains(.,'Top Reactions')]]",
  "newest"          :   "//span[text()[contains(.,'Newest Reactions')]]",

  "old_time_stamp"  :   "//li//div//div//span//span[text()[contains(.,'day')]]",
  "show_more"       :   "//span[text()[contains(.,'Show more')]]",

  "title"           :   "//h1[@class='D(ib) Fz(18px)']",
  "index"           :   "//span[contains(@class, 'Trsdu(0.3s) Fw(b)')]",
  "movement"        :   "//span[contains(@class, 'Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px)')]",

  "comment_list"    :   "//ul[contains(@class, 'comments-list')]",

  "comment_block"   :   "//ul//li[contains(@class, 'comment')]",
  "comment_user"    :   ".//button[contains(@aria-label, 'See reaction history')]",
  "time_stamp"      :   ".//div//div//span[contains(@class, 'Fz(12px)')]//span",

  "comment_text"    :   ".//div[contains(@class, 'Wow(bw)')]",
  "comment_urls"    :   ".//a[contains(@href, 'http')]",
  "comment_media"   :   ".//source",

  "thumbup"         :  ".//button[contains(@aria-label, 'Thumbs Up')]",
  "thumbdown"       :   ".//button[contains(@aria-label, 'Thumbs Down')]"

}
