from .plotter import Plotter
import matplotlib.pyplot as plt

class WeightOverTimePlotter(Plotter):
    def plot(self):
        self.df.plot(x="Elapsed", y="Current Weight", title="Weight Over Time")
    
    def show(self):
        plt.show()
    
    def save(self, path):
        plt.savefig(path)