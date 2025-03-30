from .clock import Clock
from .list import List
from .map import Map


NATIVE_FUNCTIONS = {
    func.name: func for func in (
        Clock,
        List,
        Map,
    )
}
