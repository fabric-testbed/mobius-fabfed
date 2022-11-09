from .parser import Parser, ResourceConfig, ProviderConfig
from typing import List


class Config:
    def __init__(self, *, dir_path=None, content=None, var_dict=None):
        self.providers, self.resources = Parser.parse(dir_path=dir_path, content=content, var_dict=var_dict)

    def get_provider_config(self) -> List[ProviderConfig]:
        return self.providers

    def get_resource_config(self) -> List[ResourceConfig]:
        return self.resources