#script(python)
from time import perf_counter

start = perf_counter()

def on_unsat(core):
	print("unsat", tick-start())

def cb(model):
	tick = perf_counter()
	print("model", tick-start, model.cost, model.optimality_proven)

	if model.optimality_proven:
		return False

def main(prg):
	try:
		prg.ground([("base",[])])
		prg.solve(on_model=cb)
	except:
		print("timeout", perf_counter()-start)

#end.

#show.
#show lift/2.
#project lift/2.
