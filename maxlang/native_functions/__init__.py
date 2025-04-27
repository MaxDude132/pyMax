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
from .BaseTypes.Next import NextClass

from .Interators.IntIterator import IntIteratorClass
from .Interators.ListIterator import ListIteratorClass
from .Interators.MapIterator import MapIteratorClass
from .Interators.StringIterator import StringIteratorClass
from .Interators.VarArgsIterator import VarArgsIteratorClass


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


INTERNAL_TYPES = {
    func.name: func
    for func in (
        # Base types
        VarArgsClass,
        VoidClass,
        ObjectClass,

        # Iterators
        IntIteratorClass,
        ListIteratorClass,
        MapIteratorClass,
        StringIteratorClass,
        VarArgsIteratorClass,
    )
}


ALL_FUNCTIONS = {
    func.name: func
    for func in tuple(NATIVE_FUNCTIONS.values())
    + tuple(INTERNAL_TYPES.values())

}
