# Required modules: wordcloud, matplotlib


class Comment_word_cloud_generator:

    def __init__(self):
        pass

    def draw_word_cloud(self, wc_show=False):
        """Generating word cloud using the stored comments"""
        from wordcloud import WordCloud as wc
        import matplotlib.pyplot as plt

        self.log(f'Generating word cloud: [{self.ins_title}]')

        wc_graph = wc(
            max_words=200, background_color="white",
            collocations = False).generate(self.words_chunck)

        self.wc_plot = plt

        self.wc_plot.figure(figsize=(12,8))
        self.wc_plot.imshow(wc_graph, interpolation="bilinear")
        self.wc_plot.title(f"[{self.ins_title}]\n[{self.ins_index}]  [{self.movement}]")
        self.wc_plot.axis("off")
        self.wc_plot.tight_layout(pad=1)

        if wc_show:
            self.wc_plot.show()


    def save_word_cloud(self, file_name: str=""):
        """Save word cloud locally"""
        if file_name:
            self.wc_file_name = file_name
        else:
            self.wc_file_name = os.path.join(
                check_n_mkdir(self.__word_cloud_output_folder),
                f"{self.ins_title} - {self.log_date_str}.JPG"
            )

        self.log(f'Saved word cloud as: {self.wc_file_name}', mode="sub")
        self.wc_plot.savefig(self.wc_file_name)
