import pandas as pd

class Plotter:
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def plot(self):
        raise NotImplementedError("plot method not implemented in child class")
    
    def save(self, path):
        raise NotImplementedError("save method not implemented in child class")
    
    def show(self):
        raise NotImplementedError("show method not implemented in child class")
