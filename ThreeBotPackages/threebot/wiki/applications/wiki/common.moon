load_metadata = (name) ->
    path = "/docsites/"..name.."/.data"
    file = io.open(path)
    if file
        return file\read("*all")
    -- empty json object if file is not found
    return "{}"

{ :load_metadata }
