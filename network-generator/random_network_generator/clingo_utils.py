import clingo
import builtins
import numpy as np


def as_clingo_term(obj):
    match type(obj):
        # TODO: Orribile, conviene fare il cast lato generazione da numpy
        case np.int64:
            return clingo.Number(obj)
        case builtins.int:
            return clingo.Number(obj)
        case np.bool:
            rep = "true" if bool(obj) else "false"
            return clingo.Function(rep)
        case builtins.float:
            # antonio: stiamo generando tutto noi, non dovrebbe succedere
            # conviene ragionare con le latenze in ms in int
            # oppure ragionare in precisione fissa,
            # 3.42 ms --> 342 con prec=2
            return clingo.Number(int(obj))
        case builtins.bool:
            # str(True) == "True", in ASP è una variabile
            rep = "true" if bool(obj) else "false"
            return clingo.Function(rep)

        case builtins.str:
            return clingo.String(obj)
        case _:
            raise ValueError("Unexpected type as clingo term:", obj, type(obj))
