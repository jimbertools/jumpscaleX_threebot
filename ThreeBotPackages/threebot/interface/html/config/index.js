import config from './config.prod'
import configLocal from './config.local'

var c = config
console.log(`process.env.NODE_ENV`, process.env.NODE_ENV)
if (process.env.NODE_ENV !== 'production') c = configLocal

export default (c)
