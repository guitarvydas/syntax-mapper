# queues.py

from collections import deque

class FIFO:
    def __init__(self):
        self._elements = deque()

    def enqueue(self, element):
        return self._elements.append(element)

    def dequeue(self):
        return self._elements.popleft()

    def len (self):
        return len (self._elements)

    def isEmpty (self):
        return (0 >= len (self._elements))

    def asList (self):
        return list (self._elements)

    def __repr__ (self):
        return list (self._elements)

class Eh:
    def __init__ (self, given_name):
          self.name = ''
          self.input = FIFO ()
          self.output = FIFO ()
          self.priority = FIFO ()
          self.instance_data = None
          self.children = None
          self.handler = None
          self.state = None

class Container (Eh):
      def __init__ (self, name, handler):
            super().__init__("")
            self.name = name
            self.handler = handler

class Leaf (Eh):
      def __init__ (self, handler, instance_data):
            super().__init__("")
            self.name = name
            self.handler = handler
            self.instance_data = instance_data

class Message:
      def __init__ (self, port, data):
            self.port = port
            self.operand = data
            
def message_from_string_new (port_as_string, data):
      port_operand = Operand_from_string (port_as_string).clone ()
      data_operand = Operand_from_any (data).clone ()
      m = Message (port_operand, data_operand)
      return m
  
def message_clone (src):
      port_operand = Operand_from_string (src.port).clone ()
      data_operand = Operand_from_any (src.operand).clone ()
      m = Message (port_operand, data_operand)
      return m

def discard_message_innards (m):
    pass

def send (eh, port, operand):
    m = Message (port, operand)
    eh.output.enqueue (m)
    
def send_priority (eh, port, operand):
    m = Message (port, operand)
    eh.priority.enqueue (m)

def output_list (eh):
    return eh.output.asList ()

def container_handler (eh, msg, instance_data):
    eh.route (None, msg)
    for eh.any_child_ready ():
        eh.step_children ()

def set_state (eh, state):
    eh.state = state

def destroy_container (eh):
    pass


    
class Connector:
    def __init__ (self, direction, sender, receiver):
        self.direction = direction
        self.sender = sender
        self.receiver = receiver

# Direction :: enum {
#     Down,
#     Across,
#     Up,
#     Through,
# }

class Direction:
    def Down ():
        return 'Down'
    def Across ():
        return 'Across'
    def Up ():
        return 'Up'
    def Through ():
        return 'Through'

class Sender:
    def __init__ (self, component, port):
        self.component = component
        self.port = port

def sender_eq (self, other):
    return (self.component = other.component) and (self.port = other.port)
        
class Receiver:
    def __init__ (self, component, port):
        self.component = component
        self.port = port
        
def invoke (container, child, msg):
    child.handler (child, msg, child.instance_data)
    while not child.output.isEmpty ():
        msg = child.output.dequeue ()
        container.route (msg, child.instance_data)
        discard_message (msg)
    
def step_children (container):
    for child in container:
        msg = None
        if not child.yield.isEmpty ():
            msg = child.yield.dequeue ()
            invoke (container, child, msg)
        elif not child.input.isEmpty ():
            msg = child.input.dequeue ()
            invoke (container, child, msg)
            
def route (container, from_eh, msg):
    from_sender = Sender (from_eh, message.port)
    deposits = False
    for connector in container.connections:
        if sender_eq (from_sender, connector.sender):
            depost (container, connector, message)
            deposits = True
    # error check only during bootstrap, in general, N.C. is OK (maybe we want to add some sort of explicit syntax for this?)
    if not deposits:
        print (f'{### message ignored ## {container.name} {from_eh.name} {message.datum.repr ()}###')


def any_child_ready (container):
    for child in container.children:
        if child_is_ready (child):
            return True
    return False

def child_is_ready (eh):
    return (not eh.input.isEmpty ()) or (not eh.output.isEmpty ()) or (not eh.priority.isEmpty ())

def print_output_list (eh):
    print ('[')
    for m in eh.output:
        print (f'{m}')
    print (']')
    
