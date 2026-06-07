#!/usr/bin/env python3
"""
Post-process: localiza el contenido genérico de Chihuahua → Saltillo.

Reemplaza menciones hardcoded de Chihuahua/Cd. Juárez/etc. por
referencias correctas a Saltillo, Ramos Arizpe, zona metropolitana,
cluster Chrysler-Stellantis.

Este script es REUTILIZABLE: cambiar el dict REPLACEMENTS al inicio
para clonar a otras ciudades (Torreón, Monclova, Querétaro, etc.).
"""
import json
import re
from pathlib import Path

DATA = Path('/Users/quiwistore/Downloads/repuve-saltillo/data/repuve.json')

# ============================================================
# Reemplazos en el contenido (orden importa, los más específicos primero)
# ============================================================
REPLACEMENTS = [
    # Referencias específicas a Chihuahua/Cd. Juárez (eliminar/sustituir)
    ('Ciudad Juárez', 'Saltillo capital'),
    ('Cd. Juárez', 'Saltillo'),
    ('Cd Juárez', 'Saltillo'),
    ('Cuauhtémoc', 'Ramos Arizpe'),
    ('Hidalgo del Parral', 'Arteaga'),
    ('Nuevo Casas Grandes', 'General Cepeda'),

    # Frases compuestas que mencionan Chihuahua estado
    ('en Chihuahua frontera', 'en zona industrial automotriz'),
    ('zona fronteriza con El Paso, Texas', 'cluster automotriz Chrysler-Stellantis'),
    ('cercanía con la frontera (El Paso, Las Cruces, Albuquerque)', 'cercanía con la planta Chrysler-Stellantis y General Motors'),
    ('estado fronterizo', 'capital industrial'),
    ('por ser frontera', 'por la industria automotriz local'),

    # Frontera Chihuahua → Frontera Coahuila
    ('frontera de Chihuahua', 'frontera de Coahuila (Piedras Negras y Cd. Acuña)'),
    ('en la frontera', 'en la frontera de Coahuila (~430 km de Saltillo)'),

    # Cantidad de oficinas
    ('7 oficinas', '2 oficinas'),
    ('7 sedes', '2 sedes'),
    ('siete oficinas', 'dos oficinas'),

    # Frases con "el estado" cuando se refiere al sitio (es ciudad, no estado)
    ('en el estado', 'en Saltillo'),
    ('del estado de Chihuahua', 'de Saltillo'),
    ('en el estado de Chihuahua', 'en Saltillo'),
    ('de Chihuahua', 'de Saltillo'),
    ('Chihuahua,', 'Saltillo,'),
    ('Chihuahua.', 'Saltillo.'),
    ('Chihuahua ', 'Saltillo '),
    ('Chihuahua y', 'Saltillo y'),
    ('Chihuahua tiene', 'Saltillo tiene'),
    ('en Chihuahua', 'en Saltillo'),
    ('REPUVE Chihuahua', 'REPUVE Saltillo'),

    # Referencias a "estado de Coahuila" deben quedar consistentes
    ('estado de Saltillo', 'estado de Coahuila'),
    ('REPUVE Saltillo: Cómo', 'REPUVE Saltillo, Coahuila: Cómo'),

    # Fixes específicos por contexto
    ('1.5M habitantes', '920K habitantes'),
    ('200,000 autos chocolate', '~30,000 autos chocolate (concentrados en frontera Coahuila)'),
    ('Av. Deportiva Sur 8403, Ávalos', 'Carretera a Torreón Km. 25, Cd. Satélite Norte'),

    # URL paths /oficinas/ciudad-juarez/ → /oficinas/saltillo-satelite/
    ('/oficinas/ciudad-juarez/', '/oficinas/saltillo-satelite/'),
    ('/oficinas/chihuahua-capital/', '/oficinas/saltillo-satelite/'),

    # H1 / titles que mencionan Chihuahua
    ('Consulta REPUVE Chihuahua', 'Consulta REPUVE Saltillo'),
    ('REPUVE Chihuahua 2026', 'REPUVE Saltillo 2026'),
]

def apply_replacements(obj):
    """Aplica replacements recursivamente a strings dentro de dicts/lists."""
    if isinstance(obj, str):
        for old, new in REPLACEMENTS:
            obj = obj.replace(old, new)
        return obj
    elif isinstance(obj, dict):
        return {k: apply_replacements(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [apply_replacements(item) for item in obj]
    return obj


# ============================================================
# Cargar JSON, aplicar replacements, guardar
# ============================================================
data = json.load(DATA.open())

# Solo procesamos las pages_centrales (las oficinas ya están bien)
print("Aplicando localización a 32 pages_centrales...")
data['pages_centrales'] = apply_replacements(data['pages_centrales'])

# Counter para verificar
import collections
text_blob = json.dumps(data['pages_centrales'], ensure_ascii=False)
mentions = {
    'Saltillo': text_blob.count('Saltillo'),
    'Chihuahua': text_blob.count('Chihuahua'),
    'Coahuila': text_blob.count('Coahuila'),
    'Ramos Arizpe': text_blob.count('Ramos Arizpe'),
    'Chrysler': text_blob.count('Chrysler'),
}

DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2))

print("\n✓ Localización completada")
print(f"\nMenciones en el contenido final:")
for k, v in sorted(mentions.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

if mentions['Chihuahua'] > 0:
    print(f"\n⚠️  Quedan {mentions['Chihuahua']} menciones de 'Chihuahua'. Algunas pueden ser intencionales (ej: 'no como Chihuahua que...') o requerir revisión manual.")
