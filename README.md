# Syntax Mapping
- attempt at gradually transforming the syntax of one language into the syntax of another language
- one way 
  - round-trip might be harder ; let's just avoid this issue for now
  - it is easier to go from a language with a lot of semantic content ("structure") to a language with less semantic content ("unstructured", e.g. Assembler)
- use Pattern Matching and rewriting
  - Ohm-JS for Pattern Matching
  - FAB for rewriting
  
# First Attempt
- map Python to Common Lisp
- map `x.y` into `(y x)`
- see Makefile
  - see sm.ohm for pattern
  - see sm.fab for rewrite
- run `make` and compare the output with the input `test.py`
- ignore `super()...` for now
