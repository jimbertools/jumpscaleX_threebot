import localConfig from './config.local'
import stagingConfig from './config.staging'
import prodConfig from './config.prod'

// console.log(`process.env.NODE_ENV`, process.env.NODE_ENV)
var config
if (process.env.NODE_ENV === 'production') {
  config = prodConfig
} else if (process.env.NODE_ENV === 'staging') {
  config = stagingConfig
} else {
  config = localConfig
}

export default ({
  ...config,
  salutations: ['Mr', 'Miss', 'Mme']
})
