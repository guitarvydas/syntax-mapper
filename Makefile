all: dev

dev: lisp python

lisp:
	./fab odinproc.ohm odinproc2cl.fab support.js <test2.odin >test2.lisp

python:
	./fab odinproc.ohm odinproc2py.fab support.js <test2.odin >temp
	sed -e 's/, )/)/g' <temp >test2.py

identity:
	./fab odinproc.ohm identity-odinproc.fab support.js <test2.odin >test2.out
	diff -B test2.odin test2.out

