
CONFIG = {
    "csv_output_folder"       :   r"Saved_csv",
    "wordmap_output_folder"   :   r"Saved_wordmap",
    "log_output_folder"       :   r"Work_log",
    "xp_elems"                :   r"json/xp_elems.json",
    "soup_elems"              :   r"json/soup_elems.json",
    "ignore_words"            :   ["https", "http", "stock", "market", "week", "going", "people"],
}

SITES = [
    ("SP500", "https://finance.yahoo.com/quote/%5EGSPC/community?p=%5EGSPC")
]
