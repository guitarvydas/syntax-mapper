
// Creates a component that acts as a container. It is the same as a `Eh` instance
// whose handler function is `container_handler`.
make_container :: proc(name: string) -> ^Eh {
    eh := new(Eh)
    eh.name = name
    eh.handler = container_handler
    // eh.data, in this case, is "children" and "connections"
    return eh
}

leaf_new :: proc(name: string, handler: proc(^Eh, Message, ^any), data: ^any) -> ^Eh {
    eh := new(Eh)
    eh.name = name
    eh.handler = handler
    eh.data = data
    return eh
}
