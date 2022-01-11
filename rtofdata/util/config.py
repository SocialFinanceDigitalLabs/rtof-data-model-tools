from pathlib import Path
import os

_config = None


class Config:

    def __init__(self):
        self.__data_root = None
        self.__root = Path(__file__).parent / '../..'

    @property
    def data_root(self):
        if self.__data_root:
            return self.__data_root

        value = os.getenv("DATA_ROOT")
        if value:
            return Path(value)
        else:
            return Path(__file__).parent / '../../rtof-data-model'

    @data_root.setter
    def data_root(self, value):
        self.__data_root = Path(value)

    @property
    def assets_dir(self):
        return self.data_root / 'assets'

    @property
    def data_dir(self):
        return self.data_root / 'data'

    @property
    def root(self):
        return self.__root

    @root.setter
    def root(self, value):
        self.__root = Path(value)

    @property
    def template_dir(self):
        return self.root / 'templates'

    @property
    def output_dir(self):
        output_dir = self.root / 'output'
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    @property
    def jekyll_dir(self):
        return self.output_dir / 'website'

    @property
    def output_filename_base(self):
        return "../specification"

