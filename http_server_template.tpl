import tornado.ioloop
import tornado.web

class {{servicename}}_http:
  def get(self):
   args = dict({% for key, value in arguments.items() %}
      {{escape(key)}} = self.get_argument({{escape(key)}}, "{{escape(value)}}"),{% end %}
   )
   default_response = {{response}}
   self.write(default_response)

