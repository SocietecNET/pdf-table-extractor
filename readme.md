## How to run
- build the image ```docker build -t pdf-table-extractor-api .```
- run ```docker run -p 5000:5000 -e API_KEY=test123 pdf-table-extractor-api```

## How to use

Request example
```
curl --location 'http://localhost:5000/extract_tables' \
--header 'x-api-key: test123' \
--form 'file=@"///wsl$/Ubuntu/root/dev/pdfs/test01-79p.pdf"' \
--form 'pages="22"'
```

Response example
```
[
    {
        "bbox": [
            70.78573155985491,
            547.4399999999999,
            524.5342684401452,
            613.4399999999999
        ],
        "csv": "\"Bez.\",\"Typ\",\"Quell-\nhöhe \n[m]\",\"Koordinaten \nUTM WGS 84 \nZone 32 Ost\",\"Koordinaten \nUTM WGS84 \nZone 32 Nord\",\"Höhe \nüber NN \n[m]\",\"LWA \n[dB(A)]\"\n\"BHKW 1\",\"BHKW\",\"5\",\"525086\",\"5893937\",\"31\",\"83.0\"\n\"BHKW 2\",\"BHKW\",\"5\",\"521739\",\"5897435\",\"24\",\"85.0\"\n",
        "html": "<table border=\"1\" class=\"dataframe\">\n  <tbody>\n    <tr>\n      <td>Bez.</td>\n      <td>Typ</td>\n      <td>Quell-<br>höhe <br>[m]</td>\n      <td>Koordinaten <br>UTM WGS 84 <br>Zone 32 Ost</td>\n      <td>Koordinaten <br>UTM WGS84 <br>Zone 32 Nord</td>\n      <td>Höhe <br>über NN <br>[m]</td>\n      <td>LWA <br>[dB(A)]</td>\n    </tr>\n    <tr>\n      <td>BHKW 1</td>\n      <td>BHKW</td>\n      <td>5</td>\n      <td>525086</td>\n      <td>5893937</td>\n      <td>31</td>\n      <td>83.0</td>\n    </tr>\n    <tr>\n      <td>BHKW 2</td>\n      <td>BHKW</td>\n      <td>5</td>\n      <td>521739</td>\n      <td>5897435</td>\n      <td>24</td>\n      <td>85.0</td>\n    </tr>\n  </tbody>\n</table>",
        "parsing_report": {
            "accuracy": 100.0,
            "order": 1,
            "page": 22,
            "whitespace": 0.0
        },
        "raw":"{\"columns\":[0,1,2,3,4,5,6],\"index\":[0,1,2],\"data\":[[\"Bez.\",\"Typ\",\"Quell-\\nh\öhe \\n[m]\",\"Koordinaten \\nUTM WGS 84 \\nZone 32 Ost\",\"Koordinaten \\nUTM WGS84 \\nZone 32 Nord\",\"H\öhe \\n\über NN \\n[m]\",\"LWA \\n[dB(A)]\"],[\"BHKW 1\",\"BHKW\",\"5\",\"525086\",\"5893937\",\"31\",\"83.0\"],[\"BHKW 2\",\"BHKW\",\"5\",\"521739\",\"5897435\",\"24\",\"85.0\"]]}"
    }
]
```