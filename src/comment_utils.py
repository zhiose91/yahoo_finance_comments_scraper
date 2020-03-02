# comment class
# storing useful information about on column

class Comment():
    # Hello content
    def __init__(self, user, time_stamp, comment_text):
        self.user = user
        self.time_stamp = time_stamp
        self.comment_text = comment_text
