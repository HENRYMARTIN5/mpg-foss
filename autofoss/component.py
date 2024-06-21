class AutofossComponent:
    def __init__(self, other_components: dict): # passing other components to allow for inter-component communication
        raise NotImplementedError("This is an abstract class and should not be instantiated.")
    
    def start(self):
        raise NotImplementedError("This is an abstract method and should be overridden.")
    
    def stop(self):
        raise NotImplementedError("This is an abstract method and should be overridden.")
    
    def reset(self):
        raise NotImplementedError("This is an abstract method and should be overridden.")