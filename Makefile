all: dev

dev: passes

passes:
	./fab odincomment.ohm odincomment.fab support.js <test2.odin >temp0
	./fab odinproc.ohm odinproc.fab support.js <temp0 >temp1
	./fab odinpass2.ohm odinpass2.fab support.js <temp1 >temp2

junk:
	sed -e 's/, )/)/g' <temp >temp2
	./indenter.py <temp2 >test2.py

identity:
	./fab odinproc.ohm identity-odinproc.fab support.js <test2.odin >test2.out
	diff -B test2.odin test2.out

