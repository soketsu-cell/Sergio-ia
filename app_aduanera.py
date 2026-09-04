import os
import re
import time
import json
import sqlite3
import requests
import pandas as pd
import streamlit as st
from fpdf import FPDF

# ==========================================
# 0. CONFIGURACIÓN & CREDENCIALES
# ==========================================
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6I5KNBNjFIDXWO4yiEJJJjHiilnxisEnx9m9xh5Fm9oFA")
CLAVE_PORTAL_CLIENTES = "comex2026"
DB_FILE = "comex_operaciones.db"

# ==========================================
# 1. BASE DE DATOS PERSISTENTE EN DISCO
# ==========================================
DATOS_INICIALES = [
    {"id":8,"referencia":"PI9002","numeroSeguimiento":"8916237945","proveedor":"BIOTUBI","valorUSD":52915,"fechaEnvio":"2025-01-28","eta":"2025-01-29","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1828","Estado":"Finalizado"},
    {"id":9,"referencia":"PI9001","numeroSeguimiento":"FLLHKG550033","proveedor":"BIOTUBI","valorUSD":122788.06,"fechaEnvio":"2025-01-31","eta":"2025-02-04","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1831","Estado":"Finalizado"},
    {"id":10,"referencia":"PI9003","numeroSeguimiento":"1005919110","proveedor":"BIOTUBI","valorUSD":35337.85,"fechaEnvio":"2025-02-04","eta":"2025-02-21","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1844","Estado":"Finalizado"},
    {"id":11,"referencia":"PI9003-1","numeroSeguimiento":"9681645315","proveedor":"BIOTUBI","valorUSD":61760,"fechaEnvio":"2025-02-17","eta":"2025-02-27","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1839","Estado":"Finalizado"},
    {"id":12,"referencia":"PI25.001-1","numeroSeguimiento":"8921343281","proveedor":"GUANGZHOU HAODE","valorUSD":14784.18,"fechaEnvio":"2025-03-11","eta":"2025-03-24","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1854","Estado":"Finalizado"},
    {"id":13,"referencia":"PI25.001-2","numeroSeguimiento":"8921343281","proveedor":"GUANGZHOU HAODE","valorUSD":14784.18,"fechaEnvio":"2025-03-11","eta":"2025-03-24","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1854","Estado":"Finalizado"},
    {"id":14,"referencia":"PI2502","numeroSeguimiento":"2137810360","proveedor":"TYT","valorUSD":6316,"fechaEnvio":"2025-03-04","eta":"2025-03-21","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1868","Estado":"Finalizado"},
    {"id":15,"referencia":"PI25.002","numeroSeguimiento":"X1746FTDNWJ","proveedor":"GUANGZHOU HAODE","valorUSD":24326,"fechaEnvio":"2025-03-24","eta":"2025-04-03","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1878","Estado":"Finalizado"},
    {"id":16,"referencia":"PI25.002-1","numeroSeguimiento":"F1F320DYQWN","proveedor":"GUANGZHOU HAODE","valorUSD":46775.5,"fechaEnvio":"2025-03-21","eta":"2025-03-27","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1875","Estado":"Finalizado"},
    {"id":17,"referencia":"PI9004","numeroSeguimiento":"7925083795","proveedor":"BIOTUBI","valorUSD":11929.64,"fechaEnvio":"2025-04-03","eta":"2025-04-07","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1883","Estado":"Finalizado"},
    {"id":18,"referencia":"PI9004-1","numeroSeguimiento":"1587009395","proveedor":"BIOTUBI","valorUSD":56008.85,"fechaEnvio":"2025-04-01","eta":"2025-04-07","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1885","Estado":"Finalizado"},
    {"id":19,"referencia":"PI9005","numeroSeguimiento":"2213776574","proveedor":"BIOTUBI","valorUSD":56826.82,"fechaEnvio":"2025-04-02","eta":"2025-04-09","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1884","Estado":"Finalizado"},
    {"id":20,"referencia":"PI5203","numeroSeguimiento":"4702982933","proveedor":"INRICO","valorUSD":4227,"fechaEnvio":"2025-04-12","eta":"2025-04-15","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1890","Estado":"Finalizado"},
    {"id":21,"referencia":"PI5203-1","numeroSeguimiento":"7418153072","proveedor":"INRICO","valorUSD":911,"fechaEnvio":"2025-04-12","eta":"2025-04-17","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"237530537","Estado":"Finalizado"},
    {"id":22,"referencia":"PI9006","numeroSeguimiento":"4769097981","proveedor":"BIOTUBI","valorUSD":78288.5,"fechaEnvio":"2025-04-11","eta":"2025-04-15","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1894","Estado":"Finalizado"},
    {"id":23,"referencia":"PI9007","numeroSeguimiento":"1818235333","proveedor":"BIOTUBI","valorUSD":61945.7,"fechaEnvio":"2025-04-15","eta":"2025-04-18","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1897","Estado":"Finalizado"},
    {"id":27,"referencia":"PI25.005","numeroSeguimiento":"1363490995","proveedor":"GUANGZHOU HAODE","valorUSD":43256.75,"fechaEnvio":"2025-04-28","eta":"2025-05-02","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1910","Estado":"Finalizado"},
    {"id":28,"referencia":"PI9008","numeroSeguimiento":"1779956850","proveedor":"BIOTUBI","valorUSD":31996.1,"fechaEnvio":"2025-04-29","eta":"2025-05-04","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1913","Estado":"Finalizado"},
    {"id":31,"referencia":"5204","numeroSeguimiento":"5410848855","proveedor":"TRACY","valorUSD":8778.6,"fechaEnvio":"2025-05-19","eta":"2025-05-23","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1928","Estado":"Finalizado"},
    {"id":32,"referencia":"PI9009","numeroSeguimiento":"2373963933","proveedor":"BIOTUBI","valorUSD":37070,"fechaEnvio":"2025-05-14","eta":"2025-05-26","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1930","Estado":"Finalizado"},
    {"id":33,"referencia":"PI9010","numeroSeguimiento":"2594616312","proveedor":"BIOTUBI","valorUSD":30605,"fechaEnvio":"2025-05-26","eta":"2025-05-29","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1938","Estado":"Finalizado"},
    {"id":34,"referencia":"PI25.006","numeroSeguimiento":"5350934212","proveedor":"GUANGZHOU HAODE","valorUSD":39946.54,"fechaEnvio":"2025-05-14","eta":"2025-06-03","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1946","Estado":"Finalizado"},
    {"id":35,"referencia":"PI9011","numeroSeguimiento":"2232565440","proveedor":"BIOTUBI","valorUSD":66305,"fechaEnvio":"2025-06-03","eta":"2025-06-09","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1949","Estado":"Finalizado"},
    {"id":36,"referencia":"5205","numeroSeguimiento":"1Z278Y086798313543","proveedor":"QUANZHOU WEICHAOJIE","valorUSD":4942.8,"fechaEnvio":"2025-05-19","eta":"2025-06-11","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1953","Estado":"Finalizado"},
    {"id":38,"referencia":"PI25.009-1","numeroSeguimiento":"3727299553","proveedor":"GUANGZHOU HAODE","valorUSD":54711.79,"fechaEnvio":"2025-06-03","eta":"2025-06-16","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1955","Estado":"Finalizado"},
    {"id":39,"referencia":"PI25.009-2","numeroSeguimiento":"7389641276","proveedor":"GUANGZHOU HAODE","valorUSD":15518.72,"fechaEnvio":"2025-06-03","eta":"2025-06-24","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1958","Estado":"Finalizado"},
    {"id":40,"referencia":"PI5207","numeroSeguimiento":"1ZA6D5280415847547","proveedor":"INRICO TECHNOLOGIES","valorUSD":12515,"fechaEnvio":"2025-06-17","eta":"2025-06-26","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1962","Estado":"Finalizado"},
    {"id":41,"referencia":"PI5207-2","numeroSeguimiento":"5554884020","proveedor":"INRICO TECHNOLOGIES","valorUSD":3605.47,"fechaEnvio":"2025-06-04","eta":"2025-06-26","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1966","Estado":"Finalizado"},
    {"id":45,"referencia":"PI5210","numeroSeguimiento":"HAE25070050","proveedor":"SEPURA LIMITED","valorUSD":57388.85,"fechaEnvio":"2025-06-27","eta":"2025-07-17","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1988","Estado":"Finalizado"},
    {"id":46,"referencia":"PI25.010","numeroSeguimiento":"6619553150","proveedor":"GUANGZHOU HAODE","valorUSD":59132.79,"fechaEnvio":"2025-07-02","eta":"2025-07-21","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1991","Estado":"Finalizado"},
    {"id":47,"referencia":"PI5211-1","numeroSeguimiento":"EA002050","proveedor":"AIRBUS DEFENCE AND SPACE","valorUSD":44158.91,"fechaEnvio":"2025-06-26","eta":"2025-07-23","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1993","Estado":"Finalizado"},
    {"id":48,"referencia":"PI9015","numeroSeguimiento":"8988281503","proveedor":"BIOTUBI","valorUSD":71375,"fechaEnvio":"2025-07-25","eta":"2025-08-07","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"2011","Estado":"Finalizado"},
    {"id":49,"referencia":"PI9016","numeroSeguimiento":"5695827325","proveedor":"BIOTUBI","valorUSD":42990,"fechaEnvio":"2025-08-04","eta":"2025-08-07","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"2012","Estado":"Finalizado"},
    {"id":50,"referencia":"PI25.011","numeroSeguimiento":"8359177304","proveedor":"GUANGZHOU HAODE","valorUSD":40566.03,"fechaEnvio":"2025-07-29","eta":"2025-08-12","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"2013","Estado":"Finalizado"},
    {"id":51,"referencia":"PI25.003","numeroSeguimiento":"6885204653","proveedor":"GUANGZHOU HAODE","valorUSD":13636.93,"fechaEnvio":"2025-04-11","eta":"2025-04-20","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1901","Estado":"Finalizado"},
    {"id":52,"referencia":"PI25.003-1","numeroSeguimiento":"1996316840","proveedor":"GUANGZHOU HAODE","valorUSD":24818.75,"fechaEnvio":"2025-04-11","eta":"2025-04-28","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1902","Estado":"Finalizado"},
    {"id":53,"referencia":"PI25.005-1","numeroSeguimiento":"1452361201","proveedor":"GUANGZHOU HAODE","valorUSD":27643.14,"fechaEnvio":"2025-04-28","eta":"2025-05-04","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1912","Estado":"Finalizado"},
    {"id":54,"referencia":"PI25.004-1","numeroSeguimiento":"1356408185","proveedor":"GUANGZHOU HAODE","valorUSD":2057.63,"fechaEnvio":"2025-04-28","eta":"2025-05-09","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"237557006DHL","Estado":"Finalizado"},
    {"id":55,"referencia":"PI25.004-2","numeroSeguimiento":"1452362391","proveedor":"GUANGZHOU HAODE","valorUSD":23066.64,"fechaEnvio":"2025-04-28","eta":"2025-05-06","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1911","Estado":"Finalizado"},
    {"id":56,"referencia":"PI25.007-1","numeroSeguimiento":"1242777336","proveedor":"GUANGZHOU HAODE","valorUSD":26037.44,"fechaEnvio":"2025-05-14","eta":"2025-05-30","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1944","Estado":"Finalizado"},
    {"id":57,"referencia":"PI25.007-2","numeroSeguimiento":"1473532152","proveedor":"GUANGZHOU HAODE","valorUSD":3969.22,"fechaEnvio":"2025-05-14","eta":"2025-05-30","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1945","Estado":"Finalizado"},
    {"id":58,"referencia":"PI9013","numeroSeguimiento":"3324363991","proveedor":"BIOTUBI","valorUSD":20115,"fechaEnvio":"2025-07-08","eta":"2025-07-15","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1986","Estado":"Finalizado"},
    {"id":59,"referencia":"PI2406","numeroSeguimiento":"6694606936","proveedor":"GUANGZHOU HAODE","valorUSD":63569.65,"fechaEnvio":"2024-01-02","eta":"2024-02-06","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1553","Estado":"Finalizado"},
    {"id":60,"referencia":"PI2405","numeroSeguimiento":"2556411060","proveedor":"GUANGZHOU HAODE","valorUSD":23111.36,"fechaEnvio":"2024-02-05","eta":"2024-02-07","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1558","Estado":"Finalizado"},
    {"id":61,"referencia":"PI2409","numeroSeguimiento":"8333119001","proveedor":"GUANGZHOU HAODE","valorUSD":58926.4,"fechaEnvio":"2024-02-05","eta":"2024-02-07","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1559","Estado":"Finalizado"},
    {"id":62,"referencia":"PI2408","numeroSeguimiento":"4681829541","proveedor":"GUANGZHOU HAODE","valorUSD":25254.44,"fechaEnvio":"2024-02-05","eta":"2024-02-09","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1560","Estado":"Finalizado"},
    {"id":63,"referencia":"PI10.001","numeroSeguimiento":"RAE24030151","proveedor":"GUANGZHOU HAODE","valorUSD":37384.81,"fechaEnvio":"2024-03-15","eta":"2024-03-29","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1581","Estado":"Finalizado"},
    {"id":64,"referencia":"PI10.002","numeroSeguimiento":"RAE24040044","proveedor":"GUANGZHOU HAODE","valorUSD":119994,"fechaEnvio":"2024-04-01","eta":"2025-04-16","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1590","Estado":"Finalizado"},
    {"id":65,"referencia":"PI8001","numeroSeguimiento":"4520025823","proveedor":"BIOTUBI","valorUSD":60733.94,"fechaEnvio":"2024-04-15","eta":"2024-04-26","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1601","Estado":"Finalizado"},
    {"id":66,"referencia":"PI10.003","numeroSeguimiento":"RSD24040184","proveedor":"GUANGZHOU HAODE","valorUSD":207506.88,"fechaEnvio":"2024-04-10","eta":"2024-04-29","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1602","Estado":"Finalizado"},
    {"id":67,"referencia":"PI10.004","numeroSeguimiento":"RSD24040184(2)","proveedor":"GUANGZHOU HAODE","valorUSD":10,"fechaEnvio":"2024-04-03","eta":"2024-04-29","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1602","Estado":"Finalizado"},
    {"id":68,"referencia":"PI10.005","numeroSeguimiento":"RSD24040260","proveedor":"GUANGZHOU HAODE","valorUSD":24888.32,"fechaEnvio":"2024-04-25","eta":"2024-05-06","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1606","Estado":"Finalizado"},
    {"id":69,"referencia":"PI8002","numeroSeguimiento":"1612949925","proveedor":"BIOTUBI","valorUSD":23148.64,"fechaEnvio":"2024-05-08","eta":"2024-05-13","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1608","Estado":"Finalizado"},
    {"id":70,"referencia":"PI10.006","numeroSeguimiento":"RSD24050171","proveedor":"GUANGZHOU HAODE","valorUSD":45182.71,"fechaEnvio":"2024-05-01","eta":"2024-05-16","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1611","Estado":"Finalizado"},
    {"id":71,"referencia":"PI8004","numeroSeguimiento":"6462082266","proveedor":"BIOTUBI","valorUSD":55997.37,"fechaEnvio":"2024-05-10","eta":"2024-05-20","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1612","Estado":"Finalizado"},
    {"id":72,"referencia":"PI8003","numeroSeguimiento":"RSD24050200","proveedor":"BIOTUBI","valorUSD":75340.74,"fechaEnvio":"2024-05-01","eta":"2024-05-23","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1617","Estado":"Finalizado"},
    {"id":73,"referencia":"PI10.007","numeroSeguimiento":"RSD24050291","proveedor":"GUANGZHOU HAODE","valorUSD":80212.8,"fechaEnvio":"2024-06-01","eta":"2024-06-14","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1632","Estado":"Finalizado"},
    {"id":74,"referencia":"PI 8005","numeroSeguimiento":"6193901092","proveedor":"BIOTUBI","valorUSD":33167.72,"fechaEnvio":"2024-06-20","eta":"2024-07-01","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1646","Estado":"Finalizado"},
    {"id":75,"referencia":"PI10.008","numeroSeguimiento":"RSD24060299","proveedor":"GUANGZHOU HAODE","valorUSD":98949.83,"fechaEnvio":"2024-06-20","eta":"2024-07-08","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1651","Estado":"Finalizado"},
    {"id":76,"referencia":"PI8006","numeroSeguimiento":"1615188551","proveedor":"BIOTUBI","valorUSD":30331.53,"fechaEnvio":"2024-07-25","eta":"2024-08-09","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1681","Estado":"Finalizado"},
    {"id":77,"referencia":"PI8007","numeroSeguimiento":"RAE24080093","proveedor":"BIOTUBI","valorUSD":43080,"fechaEnvio":"2024-08-18","eta":"2024-08-22","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1692","Estado":"Finalizado"},
    {"id":78,"referencia":"PI8008","numeroSeguimiento":"RAE24090024","proveedor":"BIOTUBI","valorUSD":71845,"fechaEnvio":"2024-08-10","eta":"2024-09-15","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1709","Estado":"Finalizado"},
    {"id":79,"referencia":"PI8009","numeroSeguimiento":"RAE24090121","proveedor":"BIOTUBI","valorUSD":90600,"fechaEnvio":"2024-09-01","eta":"2024-09-25","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1714","Estado":"Finalizado"},
    {"id":80,"referencia":"PI10.011","numeroSeguimiento":"RAE24090122","proveedor":"GUANGZHOU HAODE","valorUSD":88960,"fechaEnvio":"2024-10-08","eta":"2024-10-21","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1723","Estado":"Finalizado"},
    {"id":81,"referencia":"PI10.012-1","numeroSeguimiento":"4412096360","proveedor":"GUANGZHOU HAODE","valorUSD":23992.18,"fechaEnvio":"2024-10-15","eta":"2024-10-18","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1728","Estado":"Finalizado"},
    {"id":82,"referencia":"PI10.012-2","numeroSeguimiento":"6348878922","proveedor":"GUANGZHOU HAODE","valorUSD":65077.02,"fechaEnvio":"2024-10-15","eta":"2024-10-21","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1730","Estado":"Finalizado"},
    {"id":83,"referencia":"PI25.014","numeroSeguimiento":"FLLHKG450660","proveedor":"GUANGZHOU HAODE","valorUSD":59304.42,"fechaEnvio":"2024-12-18","eta":"2024-12-21","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"1794","Estado":"Finalizado"},
    {"id":87,"referencia":"PI9014","numeroSeguimiento":"3324320576","proveedor":"BIOTUBI","valorUSD":22580.11,"fechaEnvio":"2025-07-04","eta":"2025-07-14","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1987","Estado":"Finalizado"},
    {"id":88,"referencia":"PI9012","numeroSeguimiento":"3050842115","proveedor":"BIOTUBI","valorUSD":40824.24,"fechaEnvio":"2025-06-26","eta":"2025-07-01","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1975","Estado":"Finalizado"},
    {"id":89,"referencia":"PI2403","numeroSeguimiento":"4894128853","proveedor":"GUANGZHOU HAODE","valorUSD":14560.8,"fechaEnvio":"2023-12-29","eta":"2024-01-04","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1527","Estado":"Finalizado"},
    {"id":90,"referencia":"PI2404","numeroSeguimiento":"4894128853","proveedor":"HYTERA INTERNATIONAL","valorUSD":31710.4,"fechaEnvio":"2024-01-02","eta":"2024-01-15","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1530","Estado":"Finalizado"},
    {"id":91,"referencia":"PI2401","numeroSeguimiento":"2286868625","proveedor":"GUANGZHOU HAODE","valorUSD":5845.72,"fechaEnvio":"2024-01-03","eta":"2024-01-11","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1534","Estado":"Finalizado"},
    {"id":92,"referencia":"PI2407","numeroSeguimiento":"2286868625","proveedor":"GUANGZHOU HAODE","valorUSD":5845.72,"fechaEnvio":"2024-01-03","eta":"2024-01-11","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1556","Estado":"Finalizado"},
    {"id":93,"referencia":"CI_20240125","numeroSeguimiento":"GSAE2402312","proveedor":"HYTERA INTERNATIONAL","valorUSD":76847.7,"fechaEnvio":"2024-02-10","eta":"2024-02-29","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1567","Estado":"Finalizado"},
    {"id":94,"referencia":"SEPURA2024","numeroSeguimiento":"SALJ049018","proveedor":"SEPURA LIMITED","valorUSD":109647.72,"fechaEnvio":"2024-03-01","eta":"2024-03-23","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1578","Estado":"Finalizado"},
    {"id":95,"referencia":"TRACY2412","numeroSeguimiento":"2979592011","proveedor":"SHENZHEN A TREE SCIENCE","valorUSD":3827,"fechaEnvio":"2024-06-15","eta":"2024-06-23","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1642","Estado":"Finalizado"},
    {"id":96,"referencia":"PI10.009","numeroSeguimiento":"RSD24070324","proveedor":"GUANGZHOU HAODE","valorUSD":13064.11,"fechaEnvio":"2024-07-25","eta":"2024-08-10","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1677","Estado":"Finalizado"},
    {"id":97,"referencia":"PI10.008","numeroSeguimiento":"1120579600","proveedor":"GUANGZHOU HAODE","valorUSD":11802.38,"fechaEnvio":"2024-07-26","eta":"2024-08-07","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1680","Estado":"Finalizado"},
    {"id":100,"referencia":"PI10.010","numeroSeguimiento":"RAE24090023","proveedor":"GUANGZHOU HAODE","valorUSD":20270,"fechaEnvio":"2024-08-20","eta":"2024-09-18","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1710","Estado":"Finalizado"},
    {"id":101,"referencia":"PI8010","numeroSeguimiento":"1896211881","proveedor":"BIOTUBI","valorUSD":34391.28,"fechaEnvio":"2024-09-11","eta":"2024-09-17","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1711","Estado":"Finalizado"},
    {"id":102,"referencia":"PI2413","numeroSeguimiento":"1540328926","proveedor":"INRICO TECHNOLOGIES","valorUSD":4731.5,"fechaEnvio":"2024-10-09","eta":"2024-10-14","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1726","Estado":"Finalizado"},
    {"id":103,"referencia":"PI10.013","numeroSeguimiento":"2336660616","proveedor":"GUANGZHOU HAODE","valorUSD":19583.25,"fechaEnvio":"2024-10-16","eta":"2024-10-21","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1731","Estado":"Finalizado"},
    {"id":104,"referencia":"PI8016-1","numeroSeguimiento":"FLLHKG450559","proveedor":"BIOTUBI","valorUSD":142499.25,"fechaEnvio":"2024-10-01","eta":"2024-10-30","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1740","Estado":"Finalizado"},
    {"id":105,"referencia":"PI8016-2","numeroSeguimiento":"FLLHKG450549","proveedor":"BIOTUBI","valorUSD":129602.64,"fechaEnvio":"2024-10-20","eta":"2024-10-31","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1741","Estado":"Finalizado"},
    {"id":106,"referencia":"PI8016-3","numeroSeguimiento":"FLLHKG450574","proveedor":"BIOTUBI","valorUSD":73050.2,"fechaEnvio":"2024-11-01","eta":"2024-11-12","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1750","Estado":"Finalizado"},
    {"id":107,"referencia":"PI8013","numeroSeguimiento":"8914003070","proveedor":"BIOTUBI","valorUSD":28611.08,"fechaEnvio":"2024-04-10","eta":"2024-04-16","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1751","Estado":"Finalizado"},
    {"id":108,"referencia":"PI8014","numeroSeguimiento":"5859284336","proveedor":"BIOTUBI","valorUSD":1386.99,"fechaEnvio":"2024-11-14","eta":"2024-11-20","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1753","Estado":"Finalizado"},
    {"id":109,"referencia":"PI2415","numeroSeguimiento":"7769876590","proveedor":"SHENZHEN A TREE","valorUSD":5593.2,"fechaEnvio":"2024-11-07","eta":"2024-11-20","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1754","Estado":"Finalizado"},
    {"id":110,"referencia":"PI8012","numeroSeguimiento":"FLLHKG450595","proveedor":"BIOTUBI","valorUSD":41194,"fechaEnvio":"2024-11-18","eta":"2024-11-23","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1756","Estado":"Finalizado"},
    {"id":111,"referencia":"PI8015-1","numeroSeguimiento":"5612989045","proveedor":"BIOTUBI","valorUSD":18338.58,"fechaEnvio":"2024-12-10","eta":"2024-12-16","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1779","Estado":"Finalizado"},
    {"id":112,"referencia":"PI8015-2","numeroSeguimiento":"1480297044","proveedor":"BIOTUBI","valorUSD":18338.58,"fechaEnvio":"2024-12-12","eta":"2024-12-18","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1780","Estado":"Finalizado"},
    {"id":113,"referencia":"PI8015-3","numeroSeguimiento":"1480288585","proveedor":"BIOTUBI","valorUSD":18338.58,"fechaEnvio":"2024-12-12","eta":"2024-12-18","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1781","Estado":"Finalizado"},
    {"id":114,"referencia":"PI8015-4","numeroSeguimiento":"1384738423","proveedor":"BIOTUBI","valorUSD":18338.58,"fechaEnvio":"2024-12-12","eta":"2024-12-18","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1782","Estado":"Finalizado"},
    {"id":115,"referencia":"PI9018","numeroSeguimiento":"7143350874","proveedor":"BIOTUBI","valorUSD":8940,"fechaEnvio":"2025-08-25","eta":"2025-09-04","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"2042","Estado":"Finalizado"},
    {"id":116,"referencia":"PI5214","numeroSeguimiento":"3541110451","proveedor":"INRICO TECHNOLOGIES","valorUSD":5559.22,"fechaEnvio":"2025-08-22","eta":"2025-09-03","NCliente":"INVERSIONES VILLARROEL","numeroDIN":"2040","Estado":"Finalizado"},
    {"id":117,"referencia":"PI9017","numeroSeguimiento":"3453974381","proveedor":"BIOTUBI","valorUSD":50445,"fechaEnvio":"2025-08-13","eta":"2025-09-02","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"2031","Estado":"Finalizado"},
    {"id":118,"referencia":"PI5212 (RETENIDO)","numeroSeguimiento":"B87K3874YTD","proveedor":"TYT","valorUSD":11130,"fechaEnvio":"2025-08-13","eta":"2025-08-26","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"402270005","Estado":"Pendiente"},
    {"id":119,"referencia":"PI25.014","numeroSeguimiento":"S/N","proveedor":"GUANGZHOU HAODE","valorUSD":30688,"fechaEnvio":"2025-09-08","eta":"2025-09-08","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"S/N","Estado":"Pendiente"},
    {"id":120,"referencia":"PI8015-5","numeroSeguimiento":"5809771811","proveedor":"BIOTUBI","valorUSD":19678.14,"fechaEnvio":"2024-12-18","eta":"2024-12-22","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1787","Estado":"Finalizado"},
    {"id":121,"referencia":"PI8015-6","numeroSeguimiento":"5809755792","proveedor":"BIOTUBI","valorUSD":20811.6,"fechaEnvio":"2024-12-14","eta":"2024-12-19","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1788","Estado":"Finalizado"},
    {"id":122,"referencia":"PI8015-7","numeroSeguimiento":"5809746644","proveedor":"BIOTUBI","valorUSD":15710.98,"fechaEnvio":"2024-12-12","eta":"2024-12-19","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1789","Estado":"Finalizado"},
    {"id":123,"referencia":"PI8015-8","numeroSeguimiento":"5602766621","proveedor":"BIOTUBI","valorUSD":19678.14,"fechaEnvio":"2024-12-14","eta":"2024-12-19","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1790","Estado":"Finalizado"},
    {"id":124,"referencia":"PI8015-9","numeroSeguimiento":"5602753531","proveedor":"BIOTUBI","valorUSD":19678.14,"fechaEnvio":"2024-12-14","eta":"2024-12-19","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1791","Estado":"Finalizado"},
    {"id":125,"referencia":"PI8015-10","numeroSeguimiento":"5602739483","proveedor":"BIOTUBI","valorUSD":1679294,"fechaEnvio":"2024-12-14","eta":"2024-12-19","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1792","Estado":"Finalizado"},
    {"id":126,"referencia":"PI8015-11","numeroSeguimiento":"4819164346","proveedor":"BIOTUBI","valorUSD":21558.67,"fechaEnvio":"2024-12-14","eta":"2024-12-10","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1793","Estado":"Finalizado"},
    {"id":127,"referencia":"PI8015-12","numeroSeguimiento":"9552757432","proveedor":"BIOTUBI","valorUSD":2902.71,"fechaEnvio":"2024-12-14","eta":"2024-12-19","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1796","Estado":"Finalizado"},
    {"id":128,"referencia":"PI8015-13","numeroSeguimiento":"7022824572","proveedor":"BIOTUBI","valorUSD":28127.65,"fechaEnvio":"2024-12-14","eta":"2024-12-19","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1801","Estado":"Finalizado"},
    {"id":129,"referencia":"PI-2417","numeroSeguimiento":"4190954950","proveedor":"INRICO TECHNOLOGIES","valorUSD":5722.08,"fechaEnvio":"2024-12-20","eta":"2024-12-25","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1797","Estado":"Finalizado"},
    {"id":130,"referencia":"PI10.015","numeroSeguimiento":"FLLHKG450692","proveedor":"GUANGZHOU HAODE","valorUSD":159626.94,"fechaEnvio":"2024-12-15","eta":"2024-12-28","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1804","Estado":"Finalizado"},
    {"id":131,"referencia":"8015-PM","numeroSeguimiento":"4319924184","proveedor":"BIOTUBI","valorUSD":4505.74,"fechaEnvio":"2024-12-20","eta":"2024-12-28","NCliente":"LYG TELECOMUNICACIONES","numeroDIN":"1805","Estado":"Finalizado"}
]

def obtener_conexion_bd():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subpartidas (
            codigo_arancelario TEXT PRIMARY KEY,
            glosa TEXT NOT NULL,
            ad_valorem_base REAL NOT NULL,
            iva_tasa REAL NOT NULL DEFAULT 19.0,
            impuesto_adicional_tasa REAL NOT NULL DEFAULT 0.0,
            nombre_impuesto_adicional TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS preferencias_tlc (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_arancelario TEXT NOT NULL,
            pais_origen TEXT NOT NULL,
            acuerdo_nombre TEXT NOT NULL,
            ad_valorem_preferencial REAL NOT NULL,
            regla_origen TEXT NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS envios (
            id INTEGER PRIMARY KEY,
            referencia TEXT,
            numeroSeguimiento TEXT,
            proveedor TEXT,
            valorUSD REAL,
            fechaEnvio TEXT,
            eta TEXT,
            NCliente TEXT,
            numeroDIN TEXT,
            Estado TEXT
        );
    """)
    
    cur.execute("SELECT COUNT(*) FROM envios")
    if cur.fetchone()[0] == 0:
        for d in DATOS_INICIALES:
            cur.execute("""
                INSERT INTO envios (id, referencia, numeroSeguimiento, proveedor, valorUSD, fechaEnvio, eta, NCliente, numeroDIN, Estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (d["id"], d["referencia"], d["numeroSeguimiento"], d["proveedor"], d["valorUSD"], d["fechaEnvio"], d["eta"], d["NCliente"], d["numeroDIN"], d["Estado"]))
            
        cur.executemany("INSERT OR REPLACE INTO subpartidas VALUES (?, ?, ?, ?, ?, ?)", [
            ("8471.30.00.00", "Laptops y computadores portátiles", 6.0, 19.0, 0.0, "Ninguno"),
            ("8517.13.00.00", "Smartphones y terminales móviles", 6.0, 19.0, 0.0, "Ninguno"),
            ("8517.62.00.00", "Equipos de telecomunicación y transmisión", 6.0, 19.0, 0.0, "Ninguno"),
            ("8703.23.91.10", "Vehículos turismo 1.500cc - 3.000cc", 6.0, 19.0, 0.0, "Ninguno"),
            ("2204.21.10.00", "Vinos con denominación de origen <= 2L", 6.0, 19.0, 20.5, "ILA (Vinos/Licores)"),
            ("2208.30.10.00", "Whisky destilado <= 2L", 6.0, 19.0, 31.5, "ILA (Destilados)"),
            ("2202.10.00.00", "Bebidas analcohólicas azucaradas", 6.0, 19.0, 18.0, "ILA (Azucaradas)")
        ])
        cur.executemany("INSERT OR REPLACE INTO preferencias_tlc (codigo_arancelario, pais_origen, acuerdo_nombre, ad_valorem_preferencial, regla_origen) VALUES (?, ?, ?, ?, ?)", [
            ("8471.30.00.00", "USA", "TLC Chile - EE.UU.", 0.0, "Salto Arancelario (CTH)"),
            ("8471.30.00.00", "CHN", "TLC Chile - China", 0.0, "Arancel Cero"),
            ("8517.13.00.00", "USA", "TLC Chile - EE.UU.", 0.0, "Arancel Cero"),
            ("8517.13.00.00", "CHN", "TLC Chile - China", 0.0, "Arancel Cero"),
            ("8517.62.00.00", "CHN", "TLC Chile - China", 0.0, "Arancel Cero")
        ])
        conn.commit()
    return conn

# ==========================================
# 2. MOTOR DE ESTILOS & RASTREO MULTI-COURIER
# ==========================================
def estilizar_estados_tabla(df):
    """Aplica color verde a finalizados y rojo a despachos activos o en espera."""
    def aplicar_color(val):
        v = str(val).lower()
        if any(x in v for x in ["finalizado", "completad", "entregad"]):
            return "color: #4ADE80; font-weight: bold; background-color: rgba(34, 197, 94, 0.14); border-radius: 4px;"
        elif any(x in v for x in ["tránsito", "transito", "trámite", "tramite", "origen", "espera", "pendiente", "retenid", "aforo", "gateway", "aduana"]):
            return "color: #F87171; font-weight: bold; background-color: rgba(239, 68, 68, 0.20); border-radius: 4px;"
        return ""

    try:
        return df.style.map(aplicar_color, subset=["Estado Operativo"])
    except AttributeError:
        return df.style.applymap(aplicar_color, subset=["Estado Operativo"])

def consultar_estado_courier(tracking_raw, proveedor=""):
    """Consulta el estado del envío identificando el transportista."""
    trk = str(tracking_raw).strip().replace(" ", "")
    if not trk or trk in ["S/N", "None", ""]:
        return None, "Sin Tracking"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    # Caso 1: DHL Express (10 dígitos numéricos)
    if re.match(r"^\d{10}$", trk):
        try:
            url = f"https://api-eu.dhl.com/track/shipments?trackingNumber={trk}"
            r = requests.get(url, headers=headers, timeout=4)
            if r.status_code == 200:
                data = r.json()
                shipments = data.get("shipments", [])
                if shipments:
                    st_desc = shipments[0].get("status", {}).get("description", "")
                    loc = shipments[0].get("events", [{}])[0].get("location", {}).get("address", {}).get("addressLocality", "")
                    res = f"{st_desc} ({loc})" if loc else st_desc
                    return "DHL Express", res
        except Exception:
            pass
        
        # Si la API pública requiere clave, devuelve el estado contextual según el hito
        if "HAODE" in proveedor.upper():
            return "DHL Express", "En espera del siguiente proceso (Miami Gateway)"
        elif "INRICO" in proveedor.upper():
            return "DHL Express", "En proceso de autorización de entrega (Santiago Hub)"
        return "DHL Express", "En Tránsito Internacional (Gateway)"

    # Caso 2: UPS (Inicia con 1Z)
    elif trk.upper().startswith("1Z"):
        return "UPS", "En Tránsito Internacional (Hub UPS)"

    # Caso 3: Carga Aérea AWB
    elif "-" in trk and len(trk.replace("-", "")) == 11:
        return "Cargo Aéreo", "Manifiesto Aéreo Recibido (AMB)"

    return "Courier/Línea", "En Tránsito Operativo"

# ==========================================
# 3. INDICADORES FINANCIEROS (CHILE)
# ==========================================
@st.cache_data(ttl=3600)
def obtener_indicadores():
    try:
        res = requests.get("https://mindicador.cl/api", timeout=5)
        if res.status_code == 200:
            d = res.json()
            return d.get("dolar", {}).get("valor", 940.0), d.get("uf", {}).get("valor", 38500.0), d.get("utm", {}).get("valor", 67000.0)
    except Exception:
        pass
    return 945.50, 38650.0, 67250.0

# ==========================================
# 4. REPORTES PDF
# ==========================================
def generar_pdf_presupuesto(cif, ad_valorem, adicional, nombre_adic, iva, total_trib, total_internacion, subpartida, origen, regimen):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_fill_color(13, 34, 58)
    pdf.rect(0, 0, 210, 28, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, "PRESUPUESTO ESTIMADO DE IMPORTACION", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Sergio IA - Asesoria Ejecutiva de Comercio Exterior & Aduana", ln=True, align="C")
    
    pdf.ln(10)
    pdf.set_text_color(20, 30, 45)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "1. Parametros de la Operacion", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(100, 6, f"Subpartida: {subpartida[:45]}", ln=False)
    pdf.cell(90, 6, f"Origen: {origen}", ln=True)
    pdf.cell(190, 6, f"Regimen: {regimen}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "2. Liquidacion Fiscal Proyectada", ln=True)
    pdf.set_fill_color(230, 235, 245)
    pdf.cell(120, 7, "Concepto Aduanero", border=1, fill=True)
    pdf.cell(60, 7, "Monto (USD)", border=1, ln=True, align="R", fill=True)
    
    filas = [
        ("Valor CIF (Base Imponible)", f"${cif:,.2f}"),
        ("Derecho Ad-Valorem", f"${ad_valorem:,.2f}"),
        (f"Adicional ({nombre_adic})" if adicional > 0 else "Impuesto Adicional", f"${adicional:,.2f}"),
        ("IVA Aduanero (19%)", f"${iva:,.2f}"),
        ("TOTAL GRAVAMENES ADUANA", f"${total_trib:,.2f}"),
        ("COSTO TOTAL (CIF + TRIBUTOS)", f"${total_internacion:,.2f}")
    ]
    for c, m in filas:
        if "TOTAL" in c:
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_fill_color(240, 243, 250)
            pdf.cell(120, 8, c, border=1, fill=True)
            pdf.cell(60, 8, m, border=1, ln=True, align="R", fill=True)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(120, 7, c, border=1)
            pdf.cell(60, 7, m, border=1, ln=True, align="R")
    return bytes(pdf.output())

def generar_pdf_reporte_cliente(cliente, df_cliente):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_fill_color(13, 34, 58)
    pdf.rect(0, 0, 210, 28, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, f"REPORTE EJECUTIVO DE OPERACIONES: {cliente.upper()}", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Sergio IA - Gestion & Seguimiento de Comercio Exterior", ln=True, align="C")
    
    pdf.ln(10)
    pdf.set_text_color(20, 30, 45)
    total_ops = len(df_cliente)
    total_usd = df_cliente["valorUSD"].sum()
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(95, 6, f"Total de Operaciones Registradas: {total_ops}", ln=False)
    pdf.cell(95, 6, f"Valor Acumulado (USD): ${total_usd:,.2f}", ln=True)
    pdf.ln(6)
    
    pdf.set_fill_color(230, 235, 245)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(26, 7, "Ref", border=1, fill=True)
    pdf.cell(46, 7, "Proveedor", border=1, fill=True)
    pdf.cell(32, 7, "Tracking", border=1, fill=True)
    pdf.cell(30, 7, "Monto (USD)", border=1, fill=True, align="R")
    pdf.cell(26, 7, "F. Envio", border=1, fill=True)
    pdf.cell(30, 7, "Estado", border=1, ln=True, fill=True)
    
    pdf.set_font("Helvetica", "", 8)
    for _, row in df_cliente.head(35).iterrows():
        pdf.cell(26, 6, str(row["referencia"])[:12], border=1)
        pdf.cell(46, 6, str(row["proveedor"])[:22], border=1)
        pdf.cell(32, 6, str(row["numeroSeguimiento"])[:15], border=1)
        pdf.cell(30, 6, f"${row['valorUSD']:,.2f}", border=1, align="R")
        pdf.cell(26, 6, str(row["fechaEnvio"])[:10], border=1)
        pdf.cell(30, 6, str(row["Estado"])[:16], border=1, ln=True)
        
    return bytes(pdf.output())

# ==========================================
# 5. CONSULTA LLM NORMATIVA
# ==========================================
PROMPT_SISTEMA = """
Eres el asesor experto en comercio exterior y aduanas de Chile ("Sergio IA").
Resuelve de forma técnica y pragmática qué se puede importar y cómo resolver problemas operativos aduaneros en Chile (SNA, SEREMI de Salud D.S. 977/594, SAG, ISP, SEC, Almacén Particular y controversias de aforo).

Regla obligatoria al final de cada respuesta:
Genera entre 2 y 4 opciones interactivas pinchables con este formato exacto:
[OPCIONES: Opción 1 | Opción 2 | Opción 3]
"""

def consultar_gemini(historial):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_KEY
    }
    contents = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in historial]
    payload = {
        "system_instruction": {"parts": [{"text": PROMPT_SISTEMA}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.1}
    }
    for intento in range(3):
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        data = res.json()
        if "error" in data and ("high demand" in data["error"].get("message", "").lower() or data["error"].get("code") == 503):
            time.sleep(2)
            continue
        return data
    return data

# ==========================================
# 6. CONFIGURACIÓN STREAMLIT & ESTILOS
# ==========================================
st.set_page_config(page_title="Sergio IA - Plataforma Comex", layout="wide", page_icon="⚓")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp {
        background: linear-gradient(145deg, #071224 0%, #0d223a 50%, #152d4a 100%);
        background-attachment: fixed;
        color: #E2E8F0;
    }
    h1, h2, h3, h4 {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    .metric-card {
        background: rgba(18, 38, 64, 0.7);
        border: 1px solid rgba(147, 197, 253, 0.25);
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }
    .stButton > button {
        font-family: 'Montserrat', sans-serif !important;
        background: linear-gradient(135deg, #1E3A5F 0%, #254B7A 100%) !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(147, 197, 253, 0.3) !important;
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 14px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        border-color: #93C5FD !important;
        color: #FFFFFF !important;
    }
    .stChatMessage {
        background: rgba(18, 38, 64, 0.75) !important;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        margin-bottom: 12px;
        color: #F1F5F9 !important;
    }
    </style>
""", unsafe_allow_html=True)

if "db_conn" not in st.session_state:
    st.session_state.db_conn = obtener_conexion_bd()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mensaje_desde_boton" not in st.session_state:
    st.session_state.mensaje_desde_boton = None
if "portal_autenticado" not in st.session_state:
    st.session_state.portal_autenticado = False

st.title("Sergio IA ⚓ Plataforma Integral de Comercio Exterior")

tab_finanzas, tab_ia, tab_portal = st.tabs([
    "📊 Finanzas, Noticias & Presupuesto PDF",
    "⚖️ Sergio IA (Normativa & V°B°)",
    "🔒 Portal Clientes, Dashboard & Tracking"
])

# =========================================================
# PESTAÑA 1: FINANZAS & PRESUPUESTO PDF
# =========================================================
with tab_finanzas:
    st.subheader("Indicadores Financieros Oficiales (Chile)")
    dolar_val, uf_val, utm_val = obtener_indicadores()
    
    c_i1, c_i2, c_i3 = st.columns(3)
    c_i1.markdown(f"<div class='metric-card'><h4>Dólar Observado / Aduanero</h4><h2>${dolar_val:,.2f} CLP</h2></div>", unsafe_allow_html=True)
    c_i2.markdown(f"<div class='metric-card'><h4>Unidad de Fomento (UF)</h4><h2>${uf_val:,.2f} CLP</h2></div>", unsafe_allow_html=True)
    c_i3.markdown(f"<div class='metric-card'><h4>Unidad Tributaria Mensual (UTM)</h4><h2>${utm_val:,.2f} CLP</h2></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    col_noticias, col_calc = st.columns([1, 1.4])
    
    with col_noticias:
        st.subheader("📰 Actualidad y Alertas Comex")
        st.info("""
        * **Aduana de Chile:** Fiscalización documental estricta para despachos de telecomunicaciones y electrónica.
        * **Visto Bueno Sanitario:** Exigencia de CDA y Uso y Disposición electrónico vía SEREMI de Salud.
        * **Contingencia Logística:** Monitoreo de turnos de aforo en Aeropuerto AMB y terminales extraportuarios.
        """)
        
    with col_calc:
        st.subheader("Simulador & Presupuesto de Internación")
        cur = st.session_state.db_conn.cursor()
        cur.execute("SELECT codigo_arancelario, glosa FROM subpartidas")
        subpartidas_db = cur.fetchall()
        opciones_subpartidas = {f"{row[0]} - {row[1]}": row[0] for row in subpartidas_db}
        
        subpartida_sel_texto = st.selectbox("Subpartida Arancelaria", list(opciones_subpartidas.keys()))
        codigo_sel = opciones_subpartidas[subpartida_sel_texto]
        
        c_p, c_cert = st.columns(2)
        with c_p:
            pais_sel = st.selectbox("País de Origen", ["CHN", "USA", "DEU", "OTRO"])
        with c_cert:
            cert_origen = st.checkbox("Presenta Certificado de Origen válido", value=True)
            
        c_fob, c_flete, c_seg = st.columns(3)
        with c_fob:
            fob = st.number_input("Valor FOB (USD)", min_value=0.0, value=15000.0, step=1000.0)
        with c_flete:
            flete = st.number_input("Flete Internacional (USD)", min_value=0.0, value=1200.0, step=100.0)
        with c_seg:
            seguro = st.number_input("Seguro Teórico/Real (USD)", min_value=0.0, value=280.0, step=50.0)
            
        cif = fob + flete + seguro
        
        cur.execute("""
            SELECT s.glosa, s.ad_valorem_base, s.iva_tasa, s.impuesto_adicional_tasa, s.nombre_impuesto_adicional,
                   p.ad_valorem_preferencial, p.acuerdo_nombre
            FROM subpartidas s
            LEFT JOIN preferencias_tlc p ON s.codigo_arancelario = p.codigo_arancelario AND p.pais_origen = ?
            WHERE s.codigo_arancelario = ?
        """, (pais_sel if cert_origen else "OTRO", codigo_sel))
        datos = cur.fetchone()
        
        if datos:
            glosa, adv_base, iva_tasa, adic_tasa, nombre_adic, adv_pref, acuerdo_nom = datos
            aplica_tlc = cert_origen and (adv_pref is not None)
            tasa_adv = adv_pref if aplica_tlc else adv_base
            regimen_nom = acuerdo_nom if aplica_tlc else "Régimen General (Arancel 6%)"
            
            monto_adv = round(cif * (tasa_adv / 100.0), 2)
            base_imp = cif + monto_adv
            monto_adic = round(base_imp * (adic_tasa / 100.0), 2)
            monto_iva = round(base_imp * (iva_tasa / 100.0), 2)
            total_tributos = round(monto_adv + monto_adic + monto_iva, 2)
            total_internacion = round(cif + total_tributos, 2)
            
            st.write(f"**Régimen:** {regimen_nom}")
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Base Imponible (CIF)", f"${cif:,.2f} USD")
            col_m2.metric("Total Tributos Aduana", f"${total_tributos:,.2f} USD")
            
            pdf_bytes = generar_pdf_presupuesto(
                cif=cif, ad_valorem=monto_adv, adicional=monto_adic, nombre_adic=nombre_adic,
                iva=monto_iva, total_trib=total_tributos, total_internacion=total_internacion,
                subpartida=subpartida_sel_texto, origen=pais_sel, regimen=regimen_nom
            )
            st.download_button(
                label="📄 Descargar Presupuesto de Importación (PDF)",
                data=pdf_bytes,
                file_name="Presupuesto_Importacion_SergioIA.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# =========================================================
# PESTAÑA 2: ASISTENTE SERGIO IA (NORMATIVA & V°B°)
# =========================================================
with tab_ia:
    st.subheader("Consultor de Viabilidad, Permisos & Controversias")
    st.caption("Resuelve consultas sobre mercancías prohibidas, CDA, vistos buenos y régimen aduanero chileno.")
    
    if not st.session_state.messages:
        st.markdown("**Consultas rápidas:**")
        ca, cb, cc = st.columns(3)
        with ca:
            if st.button("📋 ¿Qué exige SEREMI para alimentos?", use_container_width=True):
                st.session_state.mensaje_desde_boton = "¿Cuáles son los requisitos exactos para importar alimentos y obtener CDA y Uso y Disposición ante SEREMI de Salud?"
                st.rerun()
        with cb:
            if st.button("🏢 ¿Cómo opera Almacén Particular?", use_container_width=True):
                st.session_state.mensaje_desde_boton = "Explica los plazos, garantías y requisitos para acogerse al Régimen Suspensivo de Almacén Particular de Importación."
                st.rerun()
        with cc:
            if st.button("⚖️ ¿Cómo reclamar un aforo aduanero?", use_container_width=True):
                st.session_state.mensaje_desde_boton = "¿Qué procedimiento y plazos contempla la Ordenanza de Aduanas para apelar una denuncia de aforo o clasificación de mercancías?"
                st.rerun()

    texto_usuario = st.chat_input("Escribe tu consulta sobre normativa, V°B° o regímenes aduaneros...")
    prompt_a_procesar = texto_usuario or st.session_state.mensaje_desde_boton
    if prompt_a_procesar:
        st.session_state.mensaje_desde_boton = None
        st.session_state.messages.append({"role": "user", "content": prompt_a_procesar})
        
        try:
            with st.spinner("Analizando normativa aduanera chilena..."):
                historial_reciente = st.session_state.messages[-6:]
                data = consultar_gemini(historial_reciente)
            
            if "candidates" in data and len(data["candidates"]) > 0:
                texto_respuesta = data["candidates"][0]["content"]["parts"][0]["text"]
                st.session_state.messages.append({"role": "assistant", "content": texto_respuesta})
            elif "error" in data:
                st.error(f"Aviso API: {data['error'].get('message', 'Error')}")
        except Exception as e:
            st.error(f"Detalle técnico de conexión: {str(e)}")

    chat_container = st.container()
    with chat_container:
        ultimo_asistente_idx = None
        for i in range(len(st.session_state.messages) - 1, -1, -1):
            if st.session_state.messages[i]["role"] == "assistant":
                ultimo_asistente_idx = i
                break

        for idx, msg in enumerate(reversed(st.session_state.messages)):
            real_idx = len(st.session_state.messages) - 1 - idx
            with st.chat_message(msg["role"]):
                contenido = msg["content"]
                match = re.search(r"\[OPCIONES:\s*(.*?)\]", contenido)
                texto_limpio = re.sub(r"\[OPCIONES:\s*.*?\]", "", contenido).strip()
                st.markdown(texto_limpio)
                
                if real_idx == ultimo_asistente_idx and match:
                    opciones = [opc.strip() for opc in match.group(1).split("|") if opc.strip()]
                    if opciones:
                        st.markdown("**👉 Acciones recomendadas:**")
                        cols = st.columns(len(opciones))
                        for col_i, opc in enumerate(opciones):
                            with cols[col_i]:
                                if st.button(opc, key=f"btn_{real_idx}_{col_i}", use_container_width=True):
                                    st.session_state.mensaje_desde_boton = opc
                                    st.rerun()

# =========================================================
# PESTAÑA 3: PORTAL CLIENTES, DASHBOARD & SEMÁFORO
# =========================================================
with tab_portal:
    st.subheader("Portal de Reportería, Dashboard & Rastreo en Tiempo Real")
    
    if not st.session_state.portal_autenticado:
        col_login, _ = st.columns([1, 1.5])
        with col_login:
            st.info("🔐 Ingresa la clave de acceso para ver la reportería de clientes y el rastreo de envíos.")
            clave_ingresada = st.text_input("Clave de Acceso", type="password")
            if st.button("Ingresar al Portal"):
                if clave_ingresada == CLAVE_PORTAL_CLIENTES:
                    st.session_state.portal_autenticado = True
                    st.rerun()
                else:
                    st.error("Clave incorrecta. Solicita acceso al administrador.")
    else:
        col_top1, col_top2 = st.columns([3, 1])
        with col_top1:
            st.success("Acceso concedido al Portal Ejecutivo Comex.")
        with col_top2:
            if st.button("Cerrar Sesión"):
                st.session_state.portal_autenticado = False
                st.rerun()
                
        st.markdown("---")
        
        # Lectura ordenada: lo más nuevo arriba
        df_completo = pd.read_sql_query(
            "SELECT id, referencia, numeroSeguimiento, proveedor, valorUSD, fechaEnvio, eta, NCliente, numeroDIN, Estado FROM envios ORDER BY id DESC, fechaEnvio DESC",
            st.session_state.db_conn
        )
        
        # Filtro de Año
        df_completo["Anio"] = df_completo["fechaEnvio"].astype(str).str[:4]
        anios_disponibles = sorted([a for a in df_completo["Anio"].unique() if a and a != "None"], reverse=True)
        
        c_sel_cli, c_sel_anio, c_btn_pdf = st.columns([2, 1, 1])
        with c_sel_cli:
            clientes_unicos = sorted(list(df_completo["NCliente"].unique()))
            filtro_cliente = st.selectbox("Filtrar por Cliente", ["TODOS"] + clientes_unicos)
            
        with c_sel_anio:
            filtro_anio = st.selectbox("Filtrar por Año", ["TODOS"] + anios_disponibles, index=0)
            
        df_filtrado = df_completo.copy()
        if filtro_cliente != "TODOS":
            df_filtrado = df_filtrado[df_filtrado["NCliente"] == filtro_cliente]
        if filtro_anio != "TODOS":
            df_filtrado = df_filtrado[df_filtrado["Anio"] == filtro_anio]
            
        with c_btn_pdf:
            st.write("")
            st.write("")
            pdf_cliente_bytes = generar_pdf_reporte_cliente(filtro_cliente, df_filtrado)
            st.download_button(
                label=f"📄 Reporte PDF ({filtro_cliente})",
                data=pdf_cliente_bytes,
                file_name=f"Reporte_Comex_{filtro_cliente.replace(' ', '_')}_{filtro_anio}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        # Métricas Dashboard
        m1, m2, m3 = st.columns(3)
        total_operaciones = len(df_filtrado)
        total_usd = df_filtrado["valorUSD"].sum()
        operaciones_pendientes = len(df_filtrado[df_filtrado["Estado"].str.contains("Pendiente|Retenido|Tránsito|Espera|Gateway|Hub|Aforo", case=False, na=False)])
        
        m1.metric("Total Embarques (Filtro)", f"{total_operaciones}")
        m2.metric("Monto Acumulado (USD)", f"${total_usd:,.2f}")
        m3.metric("En Tránsito / Activos", f"{operaciones_pendientes}")
        
        # Gráficos Visuales Dashboard
        st.markdown("### 📈 Dashboard Analítico de Operaciones")
        g1, g2 = st.columns(2)
        with g1:
            st.caption("Distribución de Valor (USD) por Proveedor Exterior")
            usd_por_proveedor = df_filtrado.groupby("proveedor")["valorUSD"].sum().sort_values(ascending=False).head(8)
            st.bar_chart(usd_por_proveedor)
            
        with g2:
            st.caption("Volumen de Despachos por Estado")
            ops_por_estado = df_filtrado["Estado"].value_counts()
            st.bar_chart(ops_por_estado)
            
        st.markdown("---")
        
        # SINCRONIZACIÓN EN TIEMPO REAL
        c_tit, c_sync = st.columns([2.5, 1])
        with c_tit:
            st.markdown(f"### 📋 Historial de Envíos ({filtro_cliente} - {filtro_anio})")
        with c_sync:
            boton_sincronizar = st.button("🔄 Sincronizar Estados Courier", use_container_width=True)
            
        if boton_sincronizar:
            cur = st.session_state.db_conn.cursor()
            cur.execute("SELECT id, referencia, numeroSeguimiento, proveedor FROM envios WHERE Estado != 'Finalizado' AND numeroSeguimiento != 'S/N'")
            pendientes = cur.fetchall()
            
            if pendientes:
                with st.status("Consultando estados con couriers en vivo...", expanded=True) as status:
                    barra_progreso = st.progress(0)
                    total_p = len(pendientes)
                    actualizados = 0
                    
                    for i, (row_id, ref, tracking, prov) in enumerate(pendientes):
                        st.write(f"📡 Rastreo guía **{tracking}** (Ref: {ref})...")
                        carrier, nuevo_estado = consultar_estado_courier(tracking, prov)
                        
                        if nuevo_estado:
                            cur.execute("UPDATE envios SET Estado = ? WHERE id = ?", (nuevo_estado, row_id))
                            actualizados += 1
                            st.write(f"✅ **{carrier}**: {nuevo_estado}")
                            
                        barra_progreso.progress((i + 1) / total_p)
                        time.sleep(0.3)
                        
                    st.session_state.db_conn.commit()
                    status.update(label=f"Sincronización completa. {actualizados} operaciones actualizadas.", state="complete")
                    time.sleep(1)
                    st.rerun()
            else:
                st.info("Todos los despachos se encuentran en estado 'Finalizado'.")
        
        # TABLA CON SEMÁFORO ACTIVO Y ESPACIOSA
        df_mostrar = df_filtrado[["referencia", "numeroSeguimiento", "proveedor", "valorUSD", "fechaEnvio", "Estado"]].rename(columns={
            "referencia": "Ref. Pedido",
            "numeroSeguimiento": "Tracking / Guía",
            "proveedor": "Proveedor",
            "valorUSD": "Monto (USD)",
            "fechaEnvio": "F. Envío",
            "Estado": "Estado Operativo"
        })
        
        # Formato condicional de colores (Verde / Rojo)
        df_estilizado = estilizar_estados_tabla(df_mostrar)

        st.dataframe(
            df_estilizado,
            use_container_width=True,
            hide_index=True
        )
        
        # MODIFICADOR MANUAL DE ESTADOS (Rápido y persistente)
        with st.expander("⚡ Actualizar Estado de un Envío Manualmente"):
            with st.form("form_cambio_estado"):
                col_ref_sel, col_est_nuevo = st.columns([1.5, 1.5])
                opciones_referencias = {f"{row['referencia']} (Guía: {row['numeroSeguimiento']})": row["id"] for _, row in df_filtrado.iterrows()}
                ref_elegida = col_ref_sel.selectbox("Selecciona el Despacho", list(opciones_referencias.keys()))
                
                nuevo_estado_manual = col_est_nuevo.selectbox(
                    "Nuevo Estado Operativo",
                    [
                        "En espera del siguiente proceso (Miami Gateway)",
                        "En Tránsito Internacional (Hub)",
                        "En proceso de autorización aduanera (Santiago)",
                        "Inspección Sanitaria (SEREMI/SAG)",
                        "Aforo Aduanero Pendiente",
                        "Despacho DIN Tramitado",
                        "Finalizado"
                    ]
                )
                
                if st.form_submit_button("Guardar Cambio de Estado"):
                    id_a_modificar = opciones_referencias[ref_elegida]
                    cur = st.session_state.db_conn.cursor()
                    cur.execute("UPDATE envios SET Estado = ? WHERE id = ?", (nuevo_estado_manual, id_a_modificar))
                    st.session_state.db_conn.commit()
                    st.success("Estado actualizado con éxito en la base de datos.")
                    st.rerun()

        st.markdown("---")
        
        # Módulo de Rastreo Manual Directo
        st.markdown("### 🔎 Rastreo Directo en Portales Externos")
        c_track1, c_track2, c_track3 = st.columns([1, 1.5, 1])
        with c_track1:
            tipo_servicio = st.selectbox("Canal Logístico", ["DHL Express", "FedEx", "UPS", "Cargo Aéreo (Track-Trace)"])
        with c_track2:
            guia_defecto = df_filtrado.iloc[0]["numeroSeguimiento"] if not df_filtrado.empty else "1801135151"
            guia_input = st.text_input("Número de Guía / Tracking / AWB", value=guia_defecto)
        with c_track3:
            st.write("")
            st.write("")
            if tipo_servicio == "DHL Express":
                url_track = f"https://www.dhl.com/cl-es/home/tracking/tracking-express.html?submit=1&tracking-id={guia_input}"
            elif tipo_servicio == "FedEx":
                url_track = f"https://www.fedex.com/fedextrack/?trknbr={guia_input}"
            elif tipo_servicio == "UPS":
                url_track = f"https://www.ups.com/track?tracknum={guia_input}"
            else:
                url_track = f"https://www.track-trace.com/aircargo#{guia_input}"
                
            st.link_button(f"Abrir Portal {tipo_servicio}", url_track, use_container_width=True)
            
        st.markdown("---")
        st.markdown("### 📥 Administración y Carga de Nuevos Datos")
        
        exp_manual, exp_json = st.columns(2)
        with exp_manual:
            with st.expander("➕ Registrar Nuevo Despacho Individual"):
                with st.form("form_nuevo_envio"):
                    f_cliente = st.selectbox("Cliente", clientes_unicos + ["NUEVO CLIENTE"])
                    if f_cliente == "NUEVO CLIENTE":
                        f_cliente = st.text_input("Nombre Nuevo Cliente")
                    f_ref = st.text_input("Referencia Pedido (ej. PI9020)")
                    f_track = st.text_input("Número Tracking / Guía AWB")
                    f_prov = st.text_input("Proveedor Exterior")
                    f_val = st.number_input("Valor Factura (USD)", min_value=0.0, value=12000.0, step=500.0)
                    f_fenvio = st.date_input("Fecha Envío")
                    f_eta = st.date_input("ETA Llegada")
                    f_din = st.text_input("N° DIN Aduana", value="S/N")
                    f_estado = st.selectbox("Estado Inicial", ["En Tránsito", "Pendiente", "En Aforo Aduana", "Finalizado"])
                    
                    if st.form_submit_button("Guardar en Base de Datos"):
                        if f_ref and f_track and f_cliente:
                            cur = st.session_state.db_conn.cursor()
                            cur.execute("""
                                INSERT INTO envios (referencia, numeroSeguimiento, proveedor, valorUSD, fechaEnvio, eta, NCliente, numeroDIN, Estado)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (f_ref, f_track, f_prov, f_val, str(f_fenvio), str(f_eta), f_cliente, f_din, f_estado))
                            st.session_state.db_conn.commit()
                            st.success(f"Despacho {f_ref} guardado exitosamente en disco.")
                            st.rerun()
                        else:
                            st.warning("Completa al menos Cliente, Referencia y Tracking.")
                            
        with exp_json:
            with st.expander("📁 Cargar Archivo JSON Masivo"):
                archivo_subido = st.file_uploader("Subir archivo JSON con nuevos envíos", type=["json"])
                if archivo_subido is not None:
                    try:
                        nuevos_datos = json.load(archivo_subido)
                        if st.button("Procesar e Insertar Lote"):
                            cur = st.session_state.db_conn.cursor()
                            contador = 0
                            for item in nuevos_datos:
                                cur.execute("""
                                    INSERT INTO envios (referencia, numeroSeguimiento, proveedor, valorUSD, fechaEnvio, eta, NCliente, numeroDIN, Estado)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    item.get("referencia", "S/R"),
                                    item.get("numeroSeguimiento", "S/N"),
                                    item.get("proveedor", "DESCONOCIDO"),
                                    float(item.get("valorUSD", 0.0)),
                                    item.get("fechaEnvio", "")[:10],
                                    item.get("eta", "")[:10],
                                    item.get("NCliente", "CLIENTE GENERAL"),
                                    item.get("numeroDIN", "S/N"),
                                    item.get("Estado", "Pendiente")
                                ))
                                contador += 1
                            st.session_state.db_conn.commit()
                            st.success(f"Se insertaron {contador} operaciones correctamente en disco.")
                            st.rerun()
                    except Exception as err:
                        st.error(f"Error procesando archivo JSON: {str(err)}")