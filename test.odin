
// Message passed to a leaf component.
//
// `port` refers to the name of the incoming or outgoing port of this component.
// `datum` is the data attached to this message.
Message :: struct {
    port:  string,
    datum: any,
}

// Utility for making a `Message`. Used to safely "seed" messages
// entering the very top of a network.
make_message :: proc(port: string, data: $Data) -> Message {
    data_ptr := new_clone(data)
    data_id := typeid_of(Data)

    return {
        port  = port,
        datum = any{data_ptr, data_id},
    }
}
}
