import axios from "axios";


export function getJobs() {
    return axios.post("/actors/myjobs/list_jobs");
}

export function getWorkers() {
    return axios.post("/actors/myjobs/list_workers");
}

