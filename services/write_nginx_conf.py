import os

def write_nginx_conf(port, output_dir):
    nginx_conf_path = os.path.join(output_dir, "nginx.conf")
    with open(nginx_conf_path, "w") as f:
        f.write(f"""server {{
    listen       {port};
    server_name  _;

    # gzip & security headers
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    root /usr/share/nginx/html;
    index index.html;

    # SPA catch-all
    location / {{
        try_files $uri $uri/ /index.html;
    }}

    # cache assets
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}
""")