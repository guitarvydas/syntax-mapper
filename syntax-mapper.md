```
def any_child_ready ($C):
    for child in $C.children:
        if child_is_ready (child):
            return True
    return False
```

```
(defun any_child_ready ($C)
  (loop for child in (children $C)
        do (if (child_is_ready child)
               (return-from any_child_ready t)))
	(return-from any_child_ready nil))
```

```
(defun $F ($C)
  (loop for child in (children $C)
        do (if (child_is_ready child)
               (return-from $F t)))
	(return-from $F nil))
```

---

```
def child_is_ready (eh):
    return (not eh.input.isEmpty ()) or (not eh.output.isEmpty ()) or (not eh.priority.isEmpty ())
```

```
def $F ($E):
    return (not $E.input.isEmpty ()) or (not $Eoutput.isEmpty ()) or (not $E.priority.isEmpty ())
```

```
(defun $F ($E)
  (or (not (isEmpty (input $E)))
      (not (isEmpty (output $E)))
      (not (isEmpty (priority $E)))))
```
```
(defun child_is_ready (eh)
  (or (not (isEmpty (input eh)))
      (not (isEmpty (output eh)))
      (not (isEmpty (priority eh)))))
```

---

```
$A.$B
```
-->
```
($B $A)
```

---

```
def print_output_list (eh):
    print ('[')
    for m in eh.output:
        print (f'{m}')
    print (']')
```
```
(defun print_output_list (eh)
    print ('[')
    for m in eh.output:
        print (f'{m}')
    print (']')
)
```
---
```
def $F $$
```
```
(defun $F $$)
```

```
` --> "
```

```
(defun print_output_list (eh)
    print ("[")
    for m in eh.output:
        print (f"{m}")
    print ("]")
)
```

