







(struct Eh
    name
    input
    output
    yield
    data
    children
    connections
    handler
    state)

(struct Message
    port
    datum)

(defun make_container (self name )
  (let ((eh (make-Eh)))
    (setf (slot-value eh 'name) name)
    (setf (slot-value eh 'handler) container_handler)
    eh))

def leaf_new(self name handler data )
(-
    eh := new(Eh)
    eh.name = name
    eh.handler = handler
    eh.data = data
    return eh
    -)
def make_message(self port_as_string data )
(-
    return {
    port = port_clone (port_as_string),
    datum = dt.clone_datum (data) }
    -)
def make_message_from_string(self port s )
(-
    d := dt.create_datum (raw_data (s), len (s), dt.datum_to_string, "StringMessage")
    cloned_port := port_clone (port) return make_message (cloned_port, d)
    -)
def message_clone(self message )
(-
    new_message := Message {
    port = port_clone (message.port), datum = dt.clone_datum (message.datum)
    }
    return new_message
    -)
def port_clone(self port )
(-
    return strings.clone (port)
    -)
def discard_message_innards(self msg )
(-
    delete_string (msg.port)
    dt.reclaim_datum (msg.datum)
    -)
def send(self eh port datum )
(-
    msg := make_message (port, datum)
    fifo_push(&eh.output, msg)
    -)
def yield(self eh port data )
(-
    msg := make_message(port, data)
    fifo_push(&eh.yield, msg)
    -)
def output_list(self eh )
(-
    list := make([]Message, eh.output.len)
    iter := make_fifo_iterator(&eh.output)
    for msg, i in fifo_iterate(&iter) {
    list[i] = msg
    }
    return list
    -)
def container_handler(self eh message instance_data )
(-
    log.debug ("container handler routing")
    route(eh, nil, message)
    log.debug ("container handler stepping")
    for any_child_ready(eh) {
    step_children(eh)
    }
    -)
def set_state(self eh state )
(-
    eh.state = int(state)
    -)
def destroy_container(self eh )
(-
    drain_fifo :: proc(fifo: ^FIFO) {
    for fifo.len > 0 {
    msg, _ := fifo_pop(fifo)
    discard_message_innards (msg)
    }
    }
    drain_fifo(&eh.input)
    drain_fifo(&eh.output)
    free(eh)
    -)
FIFO :: queue.Queue(Message)
fifo_push :: queue.push_back
fifo_pop :: queue.pop_front_safe
def fifo_is_empty(self fifo )
(-
    return fifo.len == 0
    -)
defstruct FIFO_Iterator
(-
    q
    idx
    -)
def make_fifo_iterator(self q )
(-
    return {q, 0}
    -)
def fifo_iterate(self iter )
(-
    if iter.q.len == 0 {
    ok = false
    return
    }
    i := (uint(iter.idx)+iter.q.offset) % len(iter.q.data)
    if i < iter.q.len {
    ok = true
    idx = iter.idx
    iter.idx += 1
    #no_bounds_check item = iter.q.data[i]
    }
    return
    -)
defstruct Connector
(-
    direction
    sender
    receiver
    -)
Direction :: enum {
Down,
Across,
Up,
Through,
}
defstruct Sender
(-
    component
    port
    -)
defstruct Receiver
(-
    queue
    port
    -)
def sender_eq(self s1 s2 )
(-
    return s1.component == s2.component && s1.port == s2.port
    -)
def deposit(self c message )
(-
    new_message := message_clone(message)
    new_message.port = port_clone (c.receiver.port)
    log.debugf("DEPOSIT", message.port)
    fifo_push(c.receiver.queue, new_message)
    -)
def step_children(self container )
(-
    for child in container.children {
    msg: Message
    ok: bool
    switch {
    case child.yield.len > 0:
    msg, ok = fifo_pop(&child.yield)
    case child.input.len > 0:
    msg, ok = fifo_pop(&child.input)
    }
    if ok {
    log.debugf("INPUT 0x%p %s/%s(%s)", child, container.name, child.name, msg.port)
    child.handler(child, msg, child.data)
    log.debugf("child handler stepped 0x%p %s/%s(%s)", child, container.name, child.name, msg.port)
    discard_message_innards (msg)
    }
    for child.output.len > 0 {
    msg, _ = fifo_pop(&child.output)
    log.debugf("OUTPUT 0x%p %s/%s(%s)", child, container.name, child.name, msg.port)
    route(container, child, msg)
    discard_message_innards (msg)
    }
    }
    -)
def route(self container from message )
(-
    log.debugf("ROUTE", container.name, from.name, message.port)
    from_sender := Sender{from, message.port}
    no_deposits := true
    for connector in container.connections {
    if sender_eq(from_sender, connector.sender) {
    deposit(connector, message)
    no_deposits = false
    }
    }
    if no_deposits {
    log.error ("### message ignored ###")
    log.error ("###", container.name, from.name, message.port, message.datum.repr (message.datum))
    assert (false)
    }
    -)
def any_child_ready(self container )
(-
    for child in container.children {
    if child_is_ready(child) {
    return true
    }
    }
    return false
    -)
def child_is_ready(self eh )
(-
    return !fifo_is_empty(eh.output) || !fifo_is_empty(eh.input) || !fifo_is_empty(eh.yield)
    -)
def print_output_list(self eh )
(-
    write_rune :: strings.write_rune
    write_string :: strings.write_string
    sb: strings.Builder
    defer strings.builder_destroy(&sb)
    write_rune(&sb, '[')
    iter := make_fifo_iterator(&eh.output)
    for msg, idx in fifo_iterate(&iter) {
    if idx > 0 {
    write_string(&sb, ", ")
    }
    fmt.sbprintf(&sb, "{{%s, %v}", msg.port, msg.datum.repr (msg.datum))
    }
    strings.write_rune(&sb, ']')
    fmt.println(strings.to_string(sb))
    -)



