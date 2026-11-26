#!/usr/bin/env python3
"""Unisce tutti i feed del repository in tutti-i-feed.xml (ordinato per data, senza duplicati)."""
import glob, os, sys
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime, format_datetime
from datetime import datetime, timezone

SRC = {
    "motosprint-velocita.xml": "Motosprint",
    "skysport-motogp.xml": "Sky Sport",
    "corsedimoto-velocita.xml": "Corsedimoto",
    "motorsportmagazine-motogp.xml": "Motor Sport Magazine",
    "speedweek-velocita.xml": "Speedweek",
    "motomatters-velocita.xml": "MotoMatters",
    "todocircuito-velocita.xml": "Todocircuito",
    "motorsport-total-motorrad.xml": "Motorsport-Total",
    "motosan-corse.xml": "Motosan",
}
OUT = "tutti-i-feed.xml"
MAX = 200

here = os.path.dirname(os.path.abspath(__file__))
items = {}
for fn in sorted(glob.glob(os.path.join(here, "*.xml"))):
    name = os.path.basename(fn)
    if name == OUT:
        continue
    label = SRC.get(name, name[:-4])
    for it in ET.parse(fn).getroot().iter("item"):
        link = (it.findtext("link") or "").strip()
        title = (it.findtext("title") or "").strip()
        pub = (it.findtext("pubDate") or "").strip()
        if not link or link in items:
            continue
        try:
            dt = parsedate_to_datetime(pub)
        except Exception:
            dt = datetime(1970, 1, 1, tzinfo=timezone.utc)
        items[link] = (dt, title, pub, label, name)

rows = sorted(items.items(), key=lambda kv: kv[1][0], reverse=True)[:MAX]
rss = ET.Element("rss", version="2.0")
ch = ET.SubElement(rss, "channel")
ET.SubElement(ch, "title").text = "Moto Notizie – Tutti i feed"
ET.SubElement(ch, "link").text = "https://lb9104.github.io/motonotizie-feed-claude/"
ET.SubElement(ch, "description").text = "Tutte le notizie dei feed di motociclismo riunite in uno solo, ordinate per data; la fonte è indicata nell'elemento source di ogni notizia (feed non ufficiale)"
ET.SubElement(ch, "language").text = "it"
ET.SubElement(ch, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc))
BASE = "https://lb9104.github.io/motonotizie-feed-claude/"
for link, (dt, title, pub, label, fname) in rows:
    e = ET.SubElement(ch, "item")
    ET.SubElement(e, "title").text = title
    ET.SubElement(e, "link").text = link
    g = ET.SubElement(e, "guid", isPermaLink="true")
    g.text = link
    ET.SubElement(e, "pubDate").text = pub
    ET.SubElement(e, "source", url=BASE + fname).text = label
ET.indent(rss)
ET.ElementTree(rss).write(os.path.join(here, OUT), encoding="utf-8", xml_declaration=True)
print(f"{OUT}: {len(rows)} notizie da {len(set(SRC))} fonti", file=sys.stderr)
