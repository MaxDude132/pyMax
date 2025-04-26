from .clock import Clock
from .print import Print

from .BaseTypes.List import ListClass
from .BaseTypes.Map import MapClass
from .BaseTypes.Pair import PairClass
from .BaseTypes.Int import IntClass
from .BaseTypes.Float import FloatClass
from .BaseTypes.String import StringClass
from .BaseTypes.Bool import BoolClass
from .BaseTypes.VarArgs import VarArgsClass
from .BaseTypes.Void import VoidClass
from .BaseTypes.Object import ObjectClass
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


INTERNAL_TYPES = {
    func.name: func
    for func in (
        # Base types
        NextClass,
        VarArgsClass,
        VoidClass,
        ObjectClass,
    )
}


ALL_FUNCTIONS = {
    func.name: func
    for func in tuple(NATIVE_FUNCTIONS.values())
    + tuple(INTERNAL_TYPES.values())

}
