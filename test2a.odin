leaf_new :: proc(name: string, handler: proc(^Eh, Message, ^any), data: ^any) -> ^Eh {
    eh := new(Eh)
    eh.name = name
    eh.handler = handler
    eh.data = data
    return eh
}
