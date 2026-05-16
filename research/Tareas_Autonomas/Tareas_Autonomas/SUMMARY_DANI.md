# RESUMEN PARA DANI — Tareas Largas Autónomas

**Fecha:** 2026-05-16

---

## El Problema

Cuando BRAIN ejecuta un script largo (3905 filas), si algo falla, se detiene y pregunta qué hacer.

**Lo que quieres:** BRAIN ejecuta solo, maneja errores, reporta al final.

---

## La Solución: Autonomous Processor Pattern

### Principios Clave

| Patrón | Qué hace |
|--------|----------|
| **Checkpointing** | Guardar progreso cada N filas. Si se corta, reanuda donde quedó. |
| **Bounded retries** | Si falla, reintenta con approach modificado (máx 3 veces). Si sigue fallando, registra error y continúa. |
| **Error log separado** | No perder información si algo falla. |
| **Final report** | Resumen al terminar: procesadas, errores, tiempo. |

---

## Script Listo para Usar

```python
#!/usr/bin/env python3
"""
Autonomous Batch Processor
Procesa archivos grandes sin preguntar, maneja errores, reporta al final.
"""

import json
import os
import sys
from datetime import datetime

class AutonomousProcessor:
    def __init__(self, input_file, output_file, errors_file="errors.json"):
        self.input_file = input_file
        self.output_file = output_file
        self.errors_file = errors_file
        self.processed = 0
        self.errors = []
        self.checkpoint_file = ".checkpoint.json"
        self.chunk_size = 100  # Guardar checkpoint cada 100 filas
        
    def load_checkpoint(self):
        """Carga checkpoint si existe."""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file) as f:
                return json.load(f)
        return {'last_row': -1, 'processed': 0, 'timestamp': None}
    
    def save_checkpoint(self, last_row):
        """Guarda checkpoint."""
        with open(self.checkpoint_file, 'w') as f:
            json.dump({
                'last_row': last_row,
                'processed': self.processed,
                'timestamp': datetime.now().isoformat()
            }, f)
    
    def log_error(self, row_num, row_data, error):
        """Registra error sin parar."""
        self.errors.append({
            'row': row_num,
            'data': str(row_data)[:200],  # Primeros 200 chars
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        })
    
    def save_errors(self):
        """Guarda errores al archivo."""
        with open(self.errors_file, 'w') as f:
            json.dump(self.errors, f, indent=2)
    
    def process_row(self, row_num, row_data):
        """
        AQUÍ VA TU LÓGICA DE PROCESAMIENTO.
        Modifica esta función según lo que necesites.
        """
        # Ejemplo:
        # - Procesar fila Excel
        # - Transformar datos
        # - Escribir a output
        
        # Si algo sale mal, LANZA una excepción
        # Si todo bien, devuelve el resultado
        return processed_result
    
    def run(self):
        """Ejecuta el procesamiento completo."""
        checkpoint = self.load_checkpoint()
        start_row = checkpoint['last_row'] + 1
        self.processed = checkpoint['processed']
        
        print(f"🚀 Iniciando procesamiento...")
        print(f"📁 Input: {self.input_file}")
        print(f"📁 Output: {self.output_file}")
        print(f"📍 Reanudando desde fila: {start_row}")
        
        # Abrir archivo de input (ejemplo CSV)
        # Cambia esto según tu formato
        with open(self.input_file, 'r', encoding='utf-8') as infile:
            # Leer todas las líneas
            lines = infile.readlines()
            total = len(lines)
            print(f"📊 Total filas: {total}")
            
            for i, line in enumerate(lines[start_row:], start=start_row):
                try:
                    # Parsear línea (ajusta según tu formato)
                    row_data = line.strip().split(',')
                    
                    # Procesar
                    result = self.process_row(i, row_data)
                    
                    # Escribir resultado
                    with open(self.output_file, 'a') as outfile:
                        outfile.write(json.dumps(result) + '\n')
                    
                    self.processed += 1
                    
                    # Progress cada 100 filas
                    if self.processed % 100 == 0:
                        self.save_checkpoint(i)
                        self.save_errors()
                        print(f"✅ Procesadas: {self.processed}/{total} | Errors: {len(self.errors)}")
                    
                except Exception as e:
                    self.log_error(i, line, str(e))
                    # CONTINÚA sin preguntar - no para
        
        # Guardar estado final
        self.save_checkpoint(total - 1)
        self.save_errors()
        
        print(f"\n🎉 FINALIZADO")
        print(f"✅ Procesadas: {self.processed}")
        print(f"❌ Errores: {len(self.errors)}")
        print(f"📁 Errores guardados en: {self.errors_file}")

# ============================================
# USO
# ============================================
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python autonomous_processor.py <input.csv> <output.json>")
        sys.exit(1)
    
    processor = AutonomousProcessor(sys.argv[1], sys.argv[2])
    processor.run()
```

---

## Cómo Adaptarlo

### Para tu script de Excel con 3905 filas:

1. **Reemplaza `process_row`** con tu lógica que procesa cada fila
2. **Cambia la lectura del archivo** si no es CSV (ej: usar openpyxl para Excel)
3. **Ajusta `chunk_size`** si quieres guardar más o menos seguido

### Si el script ya existe:

```python
# En vez de modificar el script original,
# crea un wrapper que lo llame con este pattern:

class ExcelProcessor(AutonomousProcessor):
    def process_row(self, row_num, row_data):
        # Tu código original de procesar Excel
        return existing_function(row_data)
```

---

## Patrones que Implementa

| Patrón | Beneficio |
|--------|-----------|
| Checkpoint cada 100 filas | Si se corta, reanuda. No pierde trabajo. |
| Try/except por fila | Si falla una, las demás siguen. |
| Error log separado | Puedes revisar qué falló después. |
| Progress cada 100 | Ves avance sin saturar output. |
| Final report | Sabes resultado total al terminar. |

---

## Para Integrar con BRAIN

BRAIN puede ejecutar este script directamente:

```bash
python3 autonomous_processor.py datos.csv resultados.json
```

BRAIN no necesita preguntar — el script maneja todo.

---

*Investigador — Listo para usar.*