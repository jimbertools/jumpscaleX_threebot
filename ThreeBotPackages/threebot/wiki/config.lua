local config = require("lapis.config")
config("development", function()
  gedis_port(8901)
  return gedis_host("127.0.0.1")
end)
return config("production", function()
  gedis_port(8901)
  return gedis_host("127.0.0.1")
end)
