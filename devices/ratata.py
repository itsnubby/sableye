"""
ratata.py - Disposable code.
  ) 0 o .

"""
# Global declarations
i = 'mongeese'

# Halpers
def _print(things):
    """
    Print the things.
    """
    print(' '.join(things))

_print([
    'out poop',
    '\ni',
    i])
# Module-level classes
class Poop():
    def __init__(self):
        i = 'puppies'
        _print([
            'within poop',
            '\ni',
            i])

if __name__ == '__main__':
    Poop()

