all: dev

dev: pass1

pass1:
	./fab odinproc.ohm odinproc.fab support.js <test2.odin >temp

junk:
	sed -e 's/, )/)/g' <temp >temp2
	./indenter.py <temp2 >test2.py

identity:
	./fab odinproc.ohm identity-odinproc.fab support.js <test2.odin >test2.out
	diff -B test2.odin test2.out

