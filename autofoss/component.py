class AutofossComponent:
    def __init__(self, manager: 'ComponentManager'): # passing other components to allow for inter-component communication
        raise NotImplementedError("This is an abstract class and should not be instantiated.")
    
    def start(self):
        raise NotImplementedError("This is an abstract method and should be overridden.")
    
    def stop(self):
        raise NotImplementedError("This is an abstract method and should be overridden.")
    
    def reset(self):
        raise NotImplementedError("This is an abstract method and should be overridden.")
    
class ComponentManager:
    def __init__(self):
        self.components = {}
        self.prior = {}
    
    def add(self, name: str, component: AutofossComponent, priority: int=0):
        self.components[name] = component
        self.prior[name] = priority
        
    def start_all(self):
        for name in sorted(self.components.keys(), key=lambda x: self.prior[x]):
            if self.prior[name] < 0:
                continue
            self.components[name].start()
    
    def stop_all(self):
        for name in sorted(self.components.keys(), key=lambda x: self.prior[x], reverse=True):
            if self.prior[name] < 0:
                continue
            self.components[name].stop()
    
    def start(self, *names):
        for name in names:
            self.components[name].start()
    
    def stop(self, *names):
        for name in names:
            self.components[name].stop()
    
    def get(self, name):
        return self.components[name]
