import tigramite
from tigramite import plotting as tp
from tigramite.pcmci import PCMCI as tigramite_PCMCI
from tigramite import data_processing as pp
import numpy as np
import matplotlib.pyplot as plt
from tigramite.independence_tests.parcorr import ParCorr
from tigramite.independence_tests.gpdc import GPDC
from tigramite.independence_tests.cmiknn import CMIknn
import inspect

class PCMCI():
    def __init__(self, config):
        self.symbols = config["data"]["symbols"]
        

        self.data_index = None
        self.alpha_level = config['model'].get("alpha_level", 0.05)
        self.tau_max = config['model'].get("tau_max", 1)
        self.pc_alpha = config['model'].get("pc_alpha", 0.05)
        self.studied_variable = config["model"].get("studied_variable", "prices")

        self.independence_test = self._build_independence_test(config)
        
    def set_data_index(self, data_index):
        self.data_index = data_index
    
    def _build_independence_test(self, config):
        independence_test_args = config['model']['independence_test'].get("args", dict())
        independence_test_name = config['model']['independence_test']['name']
        sig = inspect.signature(eval(independence_test_name))
        params = sig.parameters
        func_args = {k: v for k, v in independence_test_args.items() if k in params}
        return eval(f"{independence_test_name}(**{func_args})")

    def __call__(self, data, datatime:np.array=None):
        if not self.data_index is None:
            data = data[:,:,self.data_index[self.studied_variable]]
        if datatime is None:
            dataframe = pp.DataFrame(data, 
                                var_names=self.symbols)
        else:
            dataframe = pp.DataFrame(data, 
                                datatime = datatime, 
                                var_names=self.symbols)
        pcmci = tigramite_PCMCI(
            dataframe=dataframe, 
            cond_ind_test=self.independence_test,
            verbosity=0)
        results = pcmci.run_pcmci(tau_max=self.tau_max, pc_alpha=self.pc_alpha, alpha_level=self.alpha_level)
        return results
        print("DONE")