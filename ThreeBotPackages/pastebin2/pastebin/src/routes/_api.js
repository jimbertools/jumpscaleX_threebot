import axios from 'axios'

export function getPaste(pasteId) {
    return (axios.post("/actors/pastebin/get_paste", { "args": { "paste_id": pasteId } }))
}

export function newPaste(code) {
    return (axios.post("/actors/pastebin/new_paste", { "args": { "code": code } }))
}