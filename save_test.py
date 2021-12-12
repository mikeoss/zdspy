from zdspy import dataio as d, zmb

og_file = d.ReadFile("./isle_main_00.zmb")

_zmb = zmb.ZMB(og_file)

save_zmb = _zmb.save()

print("Same file: " + str(og_file == save_zmb))
