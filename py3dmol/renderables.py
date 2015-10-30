import os
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)


with open('%s/3DMol-min.js'%dir_path,'r') as infile:
    javascript_library = infile.read()

with open('%s/callbacks.js'%dir_path,'r') as infile:
    callbackjs = infile.read()
html_header = '<head><script>' + callbackjs + '</script></head>\n'

with open('%s/body.html'%dir_path,'r') as infile:
    html_body = infile.read()

def viewer_html(view_id,format,width,height,molstring):
    body = html_body%(view_id,view_id,
                      format,
                      view_id,view_id,width,height,
                      view_id,
                      molstring)

    return html_header + body