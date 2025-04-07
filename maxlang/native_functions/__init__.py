from .clock import Clock
from .print import Print

from .BaseTypes.List import ListClass
from .BaseTypes.Map import MapClass
from .BaseTypes.Pair import PairClass
from .BaseTypes.Int import IntClass
from .BaseTypes.Float import FloatClass
from .BaseTypes.String import StringClass
from .BaseTypes.Bool import BoolClass
from .next import NextClass


BUILTIN_TYPES = {
    func.name: func
    for func in (
        # Base types
        IntClass,
        FloatClass,
        StringClass,
        BoolClass,
        ListClass,
        MapClass,
        PairClass,
        NextClass,
    )
}


NATIVE_FUNCTIONS = {
    func.name: func
    for func in (
        # Builtin functions
        Clock,
        Print,
    )
    + tuple(BUILTIN_TYPES.values())
}
