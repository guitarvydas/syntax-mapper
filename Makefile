all: dev

dev : identity

identity:
	./fab odinproc.ohm identity-odinproc.fab support.js <test2.odin >test2.out
	diff -B test2.odin test2.out

