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


NATIVE_FUNCTIONS = {
    func.name: func for func in (
        # Builtin functions
        Clock,
        Print,

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
