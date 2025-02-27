local lapis = require("lapis")
local ChatApp
do
  local _class_0
  local _parent_0 = lapis.Application
  local _base_0 = {
    [{
      index = "/chat/session/:topic"
    }] = function(self)
      local req = self.req.parsed_url
      local scheme = "ws"
      if req.scheme == "https" or self.req.headers['x-forwarded-proto'] == "https" then
        scheme = "wss"
      end
      self.url = scheme .. "://" .. req.host
      if req.port then
        self.url = self.url .. ":" .. 4444
      end
      self.topic = self.params.topic
      return {
        render = "chat.index"
      }
    end
  }
  _base_0.__index = _base_0
  setmetatable(_base_0, _parent_0.__base)
  _class_0 = setmetatable({
    __init = function(self, ...)
      return _class_0.__parent.__init(self, ...)
    end,
    __base = _base_0,
    __name = "ChatApp",
    __parent = _parent_0
  }, {
    __index = function(cls, name)
      local val = rawget(_base_0, name)
      if val == nil then
        local parent = rawget(cls, "__parent")
        if parent then
          return parent[name]
        end
      else
        return val
      end
    end,
    __call = function(cls, ...)
      local _self_0 = setmetatable({}, _base_0)
      cls.__init(_self_0, ...)
      return _self_0
    end
  })
  _base_0.__class = _class_0
  local self = _class_0
  self:enable("etlua")
  if _parent_0.__inherited then
    _parent_0.__inherited(_parent_0, _class_0)
  end
  ChatApp = _class_0
  return _class_0
end
