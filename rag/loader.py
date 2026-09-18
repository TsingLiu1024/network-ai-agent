from pathlib import Path



class DocumentLoader:


    def load(
        self,
        path
    ):


        file = Path(path)


        if not file.exists():

            raise FileNotFoundError(
                path
            )


        content = file.read_text(

            encoding="utf-8"

        )


        return content