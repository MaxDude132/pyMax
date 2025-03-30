from .clock import Clock
from .print import Print

from .list import List
from .map import Map
from .pair import Pair


NATIVE_FUNCTIONS = {
    func.name: func for func in (
        Clock,
        Print,
        List,
        Map,
        Pair
    )
}
