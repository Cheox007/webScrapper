import json
import os
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler


DEFAULT_LIST = [
    "Microsoft.Advisor/Configurations", 
    "Microsoft.Advisor/Recommendations",
]


JSON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "json", "microsoft_sidebar.json"))

def get_missing_items(custom_list):
    """Checks what is missing from the provided list compared to the JSON."""
    if not os.path.exists(JSON_PATH):
        return [f"Error: Sidebar JSON not found at {JSON_PATH}. Run the scraper first!"], [], 0

    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            

        microsoft_resources = set()
        unique_hrefs = set()
        
        def flatten(items):
            for item in items:
           
                href = item.get('href', '').lower().strip("/")
                if href:
                    unique_hrefs.add(href)
                    microsoft_resources.add(href)
                    microsoft_resources.add(href.replace("/", "."))

        
                title = item.get('toc_title', '').lower().strip("/")
                if title:
                    microsoft_resources.add(title)

                if 'children' in item:
                    flatten(item['children'])
        
        flatten(data.get('items', []))

    
        missing = []
        for item in custom_list:
            item_clean = item.strip().strip('"').strip("'").lower()
            if not item_clean: continue
            
            is_found = item_clean in microsoft_resources or item_clean.strip("/") in microsoft_resources
            
            if not is_found:
                parts = item_clean.replace(".", "/").split("/")
                is_found = any(p in microsoft_resources for p in parts if p)

            if not is_found:
                missing.append(item)
                
        return missing, sorted(list(microsoft_resources)), len(unique_hrefs)
    except Exception as e:
        return [f"Processing error: {e}"], [], 0

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.render_page(DEFAULT_LIST)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(post_data)
        raw_input = params.get('list_input', [''])[0]
        
        try:
            user_list = json.loads(raw_input)
            if not isinstance(user_list, list):
                user_list = [str(user_list)]
        except:
            user_list = raw_input.replace(',', '\n').split('\n')
        
        user_list = [u.strip() for u in user_list if u.strip()]
        self.render_page(user_list, raw_input)

    def render_page(self, current_list, raw_textarea=""):
        missing, all_searchable, db_total = get_missing_items(current_list)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        if not raw_textarea:
            raw_textarea = json.dumps(current_list, indent=4)

        html = f"""
        <html>
        <head>
            <title>Microsoft Sidebar Checker</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f0f2f5; color: #333; }}
                .header {{ background: #0078d4; color: white; padding: 20px 40px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .container {{ display: flex; gap: 20px; padding: 20px; max-width: 1400px; margin: 0 auto; }}
                .panel {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); flex: 1; min-width: 0; }}
                h2 {{ margin-top: 0; color: #0078d4; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                textarea {{ width: 100%; height: 400px; padding: 15px; border: 1px solid #ccc; border-radius: 4px; font-family: 'Consolas', monospace; font-size: 14px; resize: vertical; box-sizing: border-box; }}
                button {{ background: #0078d4; color: white; border: none; padding: 12px 30px; border-radius: 4px; cursor: pointer; font-size: 16px; margin-top: 15px; transition: background 0.2s; font-weight: 600; }}
                button:hover {{ background: #005a9e; }}
                .result-list {{ list-style: none; padding: 0; max-height: 600px; overflow-y: auto; }}
                .item {{ padding: 12px; margin-bottom: 10px; border-radius: 4px; border-left: 6px solid; display: flex; align-items: center; }}
                .missing {{ background: #fde7e9; border-color: #d13438; color: #a4262c; }}
                .found {{ background: #dff6dd; border-color: #107c10; color: #107c10; }}
                .status-icon {{ font-size: 1.2em; margin-right: 15px; }}
                .summary {{ background: #e1dfdd; padding: 15px; border-radius: 4px; margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 20px; }}
                .summary-item {{ display: flex; flex-direction: column; }}
                .summary-label {{ font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: bold; }}
                .summary-value {{ font-size: 1.4em; font-weight: 700; color: #0078d4; }}
            </style>
        </head>
        <body>
            <div class="header"><h1>Microsoft Resource Checker</h1></div>
            <div class="container">
                <div class="panel">
                    <h2>1. Input Your List</h2>
                    <p>Paste your resources here. You can use JSON format or one per line.</p>
                    <form method="POST">
                        <textarea name="list_input" placeholder='["Microsoft.Network/virtualNetworks", ...]'>{raw_textarea}</textarea>
                        <button type="submit">⚡ Check Comparison</button>
                    </form>
                </div>
                
                <div class="panel">
                    <h2>2. Results</h2>
                    <div class="summary">
                        <div class="summary-item">
                            <span class="summary-label">Your Input Total</span>
                            <span class="summary-value">{len(current_list)}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Database Total</span>
                            <span class="summary-value" style="color: #333;">{db_total}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Found</span>
                            <span class="summary-value" style="color: #107c10;">{len(current_list) - len(missing)}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Missing</span>
                            <span class="summary-value" style="color: #d13438;">{len(missing)}</span>
                        </div>
                    </div>
                    <ul class="result-list">
        """
        
        for item in current_list:
            item_clean = item.strip().strip('"').strip("'")
            if not item_clean: continue
            
            if item in missing:
                html += f'<li class="item missing"><span class="status-icon">❌</span>{item_clean}</li>'
            else:
                html += f'<li class="item found"><span class="status-icon">✅</span>{item_clean}</li>'
                
        html += f"""
                    </ul>
                    <div style="font-size: 0.85em; color: #666; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee;">
                        <b>Searchable variations (titles/paths):</b> {len(all_searchable)}<br>
                        <b>Reference Data:</b> <code>{JSON_PATH}</code>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

def run_server(port=8080):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f"\n Server is LIVE on your local network!")
    print(f" Local access:   http://localhost:{port}")
    print(f" Network access: http://192.168.50.132:{port}") 
    print("\n  FIREWALL HINT: If other PCs can't connect, you may need to run this in PowerShell as Admin:")
    print('   New-NetFirewallRule -DisplayName "Python Web Server" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow')
    print("\nPress Ctrl+C to stop the server.")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
