class Article:
    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id")
        self.title = kwargs.get("title")
        self.source = kwargs.get("source")
        self.image_from = kwargs.get("image_from")
        self.image_url = kwargs.get("image_url")
        self.audio_from = kwargs.get("audio_from")
        self.audio_url = kwargs.get("audio_url")
        self.summary = kwargs.get("summary")
        self.transcript = kwargs.get("transcript")
        self.date = kwargs.get("date")
