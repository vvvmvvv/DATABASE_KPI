import npyscreen


class FullTextSearch(npyscreen.ActionFormV2):
    def create(self):
        self.value = None
        self.wgWords = self.add(npyscreen.TitleText, name="Obligatory entry of the words:")
        self.wgPhrase = self.add(npyscreen.TitleText, name="Whole phrase:")
        self.wgResults = self.add(npyscreen.TitleFixedText, name="Results:", value='')

    def beforeEditing(self):
        self.name = "Full text search"
        self.wgWords.value = ''
        self.wgPhrase.value = ''

    def on_ok(self):
        if self.wgWords.value:
            search_results = self.parentApp.database.text_search_by_words(self.wgWords.value.split())
        else:
            search_results = self.parentApp.database.text_search_by_phrase(self.wgPhrase.value)
        self.wgResults.value = ' '
        for t in search_results:
            self.wgResults.value += '\r\n' + (str(t) + '\r\n')

    def on_cancel(self):
        self.parentApp.switchFormPrevious()
