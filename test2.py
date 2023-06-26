package zd

import "core:container/queue"
import "core:fmt"
import "core:mem"
import "core:strings"
import "core:intrinsics"
import "core:log"
import dt "../../datum"

// Data for an asyncronous component - effectively, a function with input
// and output queues of messages.
//
// Components can either be a user-supplied function ("leaf"), or a "container"
// that routes messages to child components according to a list of connections
// that serve as a message routing table.
//
// Child components themselves can be leaves or other containers.
//
// `handler` invokes the code that is attached to this component. For leaves, it
// is a wrapper function around `leaf_handler` that will perform a type check
// before calling the user's function. For containers, `handler` is a reference
// to `container_handler`, which will dispatch messages to its children.
//
// `leaf_data` is a pointer to any extra state data that the `leaf_handler`
// function may want whenever it is invoked again.
//
// `state` is a free integer that can be used for writing leaves that act as
// state machines. There is a convenience proc `set_state` that will do the
// cast for you when writing.
Eh :: struct {
name:         string,
input:        FIFO,
output:       FIFO,
yield:        FIFO,
data:	  ^any,   // this should be a Union: a Leaf has (instance) data, while a Container
children:     []^Eh, // has instance data, too, but the shape is predefined to be "children" and
connections:  []Connector,  // "connections"
handler:      #type proc(eh: ^Eh, message: Message, data: ^any),
state:        int,
}


// Message passed to a leaf component.
//
// `port` refers to the name of the incoming port to this component.
// `datum` is the data attached to this message.
Message :: struct {
port:  string,
datum: dt.Datum,
}

// Creates a component that acts as a container. It is the same as a `Eh` instance
// whose handler function is `container_handler`.
def make_container(self, name):

    eh := new(Eh)
    eh.name = name
    eh.handler = container_handler
    // eh.data, in this case, is "children" and "connections"
    return eh
    

def leaf_new(self, name, handler, data):

    eh := new(Eh)
    eh.name = name
    eh.handler = handler
    eh.data = data
    return eh
    

// Utility for making a `Message`. Used to safely "seed" messages
// entering the very top of a network.
def make_message(self, port_as_string, data):

    return {
    // This is written to be ultra-conservative.
    // Can this be optimized away?
    // Is it necessary to clone the port and the datum or can we simply just use them?
    
    // Constant strings start out life being scoped by the caller in Odin.  Unlike in C, where
    // constant strings a allocated in a pool with an infinite lifetime.
    
    port  = port_clone (port_as_string),
    datum = dt.clone_datum (data)
    }
    
def make_message_from_string(self, port, s):

    d := dt.create_datum (raw_data (s), len (s), dt.datum_to_string, "StringMessage")
    cloned_port := port_clone (port) // Ultra-conservative strategy.  See comment in make_message.
    return make_message (cloned_port, d)
    

// Clones a message. Primarily used internally for "fanning out" a message to multiple destinations.
def message_clone(self, message):

    new_message := Message {
    port = port_clone (message.port), // Ultra-conservative Strategy.  See comment in make_message.
    datum = dt.clone_datum (message.datum)
    }
    return new_message
    

def port_clone(self, port):

    return strings.clone (port)
    

// Frees a message.
def discard_message_innards(self, msg):

    delete_string (msg.port)
    dt.reclaim_datum (msg.datum)
    // caller frees the msg struct (typically scoped and automagically freed)
    

// Sends a message on the given `port` with `data`, placing it on the output
// of the given component.
def send(self, eh, port, datum):

    msg := make_message (port, datum)
    fifo_push(&eh.output, msg)
    

// Enqueues a message that will be returned to this component.
// This can be used to suspend leaf execution while, e.g. IO, completes
// in the background.
//
// NOTE(z64): this functionality is an active area of research; we are
// exploring how to best expose an API that allows for concurrent IO etc.
// while staying in-line with the principles of the system.
def yield(self, eh, port, data):

    msg := make_message(port, data)
    fifo_push(&eh.yield, msg)
    

// Returns a list of all output messages on a container.
// For testing / debugging purposes.
output_list :: proc(eh: ^Eh, allocator := context.allocator) -> []Message {
list := make([]Message, eh.output.len)

iter := make_fifo_iterator(&eh.output)
for msg, i in fifo_iterate(&iter) {
list[i] = msg
}

return list
}

// The default handler for container components.
def container_handler(self, eh, message, instance_data):

    // instance_data ignored ...
    log.debug ("container handler routing")
    route(eh, nil, message)
    log.debug ("container handler stepping")
    for any_child_ready(eh) {
    step_children(eh)
    }
    

// Sets the state variable on the Eh instance to the integer value of the
// given enum.
set_state :: #force_inline proc(eh: ^Eh, state: $State)
where
intrinsics.type_is_enum(State)
{
eh.state = int(state)
}

// Frees the given container and associated data.
def destroy_container(self, eh):

    drain_fifo :: proc(fifo: ^FIFO) {
    for fifo.len > 0 {
    msg, _ := fifo_pop(fifo)
    discard_message_innards (msg)
    }
    }
    drain_fifo(&eh.input)
    drain_fifo(&eh.output)
    free(eh)
    

// Wrapper for corelib `queue.Queue` with FIFO semantics.
FIFO       :: queue.Queue(Message)
fifo_push  :: queue.push_back
fifo_pop   :: queue.pop_front_safe

def fifo_is_empty(self, fifo):

    return fifo.len == 0
    

FIFO_Iterator :: struct {
q:   ^FIFO,
idx: int,
}

def make_fifo_iterator(self, q):

    return {q, 0}
    

def fifo_iterate(self, iter):

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
    

// Routing connection for a container component. The `direction` field has
// no affect on the default message routing system - it is there for debugging
// purposes, or for reading by other tools.
Connector :: struct {
direction: Direction,
sender:    Sender,
receiver:  Receiver,
}

Direction :: enum {
Down,
Across,
Up,
Through,
}

// `Sender` is used to "pattern match" which `Receiver` a message should go to,
// based on component ID (pointer) and port name.
Sender :: struct {
component: ^Eh,
port:      string,
}

// `Receiver` is a handle to a destination queue, and a `port` name to assign
// to incoming messages to this queue.
Receiver :: struct {
queue: ^FIFO,
port:  string,
}

// Checks if two senders match, by pointer equality and port name matching.
sender_eq :: proc(s1, s2: Sender) -> bool {
return s1.component == s2.component && s1.port == s2.port
}

// Delivers the given message to the receiver of this connector.
def deposit(self, c, message):

    new_message := message_clone(message)
    new_message.port = port_clone (c.receiver.port)
    log.debugf("DEPOSIT", message.port)
    fifo_push(c.receiver.queue, new_message)
    

def step_children(self, container):

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
    log.debugf("INPUT  0x%p %s/%s(%s)", child, container.name, child.name, msg.port)
    child.handler(child, msg, child.data)
    log.debugf("child handler stepped  0x%p %s/%s(%s)", child, container.name, child.name, msg.port)
    discard_message_innards (msg)
    }
    
    for child.output.len > 0 {
    msg, _ = fifo_pop(&child.output)
    log.debugf("OUTPUT 0x%p %s/%s(%s)", child, container.name, child.name, msg.port)
    route(container, child, msg)
    discard_message_innards (msg)
    }
    }
    

// Routes a single message to all matching destinations, according to
// the container's connection network.
def route(self, container, from, message):

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
    

def any_child_ready(self, container):

    for child in container.children {
    if child_is_ready(child) {
    return true
    }
    }
    return false
    

def child_is_ready(self, eh):

    return !fifo_is_empty(eh.output) || !fifo_is_empty(eh.input) || !fifo_is_empty(eh.yield)
    

// Utility for printing an array of messages.
print_output_list :: proc(eh: ^Eh) {
write_rune   :: strings.write_rune
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
}



