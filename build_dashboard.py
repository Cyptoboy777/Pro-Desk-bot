"""Build the standalone dashboard page: docs/sim.html (used by GitHub Pages).

    python3 export_runs.py      # writes dashboard_data.json from real paper runs
    python3 build_dashboard.py  # wraps the template in a full HTML document
"""
t = open("dashboard_template.html").read().replace("__DATA__", open("dashboard_data.json").read())
head, body = t.split("</style>", 1)
doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       '<style>html{-webkit-text-size-adjust:100%}body{margin:0}</style>\n'
       + head + "</style>\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")
import os
os.makedirs("docs", exist_ok=True)
open("docs/sim.html", "w").write(doc)
print("wrote docs/sim.html", len(doc))
