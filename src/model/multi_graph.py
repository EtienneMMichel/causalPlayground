from copy import copy
from .pcmci import *
from .dummy import *


class MultiGraph():
    def __init__(self, config):
        self.mode = config["model"].get("mode", "union")
        self.models = {}
        for m_config in config["model"]["models"]:
            sub_model_config = copy(config)
            sub_model_config["model"] = m_config["model"]
            self.models[m_config["input"]] = eval(f"{sub_model_config['model']['name']}(sub_model_config)")
    
    def set_data_index(self, data_index):
        self.data_index = data_index

    def __call__(self, data):
        results = {}
        for data_input_name, data_index in self.data_index.items():
            submodel_results = self.models[data_input_name](data[:,:,data_index])
            results[data_input_name] = submodel_results

        return self.__group(results)
    
    def __group(self, results):
        if self.mode == "union":
            return self.__group_union(results)
        
        if self.mode in list(self.data_index.keys()):
            return results[self.mode]
        return None
    
    def __group_union(self, results):
        return None