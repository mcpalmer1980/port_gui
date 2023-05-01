class Classer:
    def __init__(self, text=''):
        self._text = text
    
    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, other):
        print(f'text set to {other}')
        self._text = other
