# Tareas Largas Autonomas — Investigación

**Fecha:** 2026-05-16

---

## Fuentes

1. **Building AI Agents That Actually Complete Tasks** — atticusli.com/blog/posts/building-ai-agents-that-complete-tasks/
2. **Long-running Agents** — addyosmani.com/blog/long-running-agents/
3. **Microsoft: Agent Autonomous Batch Processing** — learn.microsoft.com

---

## El Problema

BRAIN usa exec para ejecutar scripts. Si el script es largo (3905 filas), y algo falla, se detiene y espera input de Dani.

**Lo que Dani quiere:** Que BRAIN ejecute sin parar, maneje errores, y reporte al final.

---

## Patrones de Ejecución Autónoma

### 1. Ralph Loop (Geoffrey Huntley / Ryan Carson)

El patrón más simple para agentes autónomos:

```
1. Pick next unfinished task from list
2. Build prompt with task + context
3. Call agent
4. Run tests/checks
5. Append what happened to progress.txt
6. Update task list (done/failed/blocked)
7. Go back to step 1
```

**Por qué funciona:** Separa el trabajo en chunks manejables con checkpointing.

---

### 2. ReAct Pattern (Reason Then Act)

Después de cada acción, el agente razona sobre el resultado antes de decidir la siguiente.

```python
for step in plan:
    action_result = execute(step)
    reasoning = analyze(action_result)
    if not reasoning.is_ok:
        retry_with_modified_approach(step)
```

---

### 3. State Checkpoints

Para tareas largas, guardar estado a intervalos regulares.

```python
# Cada N filas, guardar checkpoint
if row_number % 100 == 0:
    save_checkpoint({
        'last_processed_row': row_number,
        'errors': error_log,
        'timestamp': datetime.now()
    })
```

---

### 4. Bounded Retries

Cuando una acción falla:
- Retry con approach modificado (no el mismo)
- Máximo 3 intentos
- Si falla, registrar en error log y continuar

```python
MAX_RETRIES = 3
for attempt in range(MAX_RETRIES):
    try:
        result = process_row(row)
        break
    except Exception as e:
        if attempt == MAX_RETRIES - 1:
            log_error(row, str(e))
            continue  # Continue to next row
        else:
            row = modify_approach(row)  # Try different approach
```

---

### 5. Verify After Every Action

```python
result = process_row(row)
if not verify(result):
    log_error(row, "Verification failed")
    continue
```

---

## Errores Comunes en Agentes Largos

| Error | Síntoma | Prevención |
|-------|---------|-----------|
| **Infinite loops** | Repite misma acción | Track action history, force different approach |
| **Goal drift** | Pierde el objetivo original | Re-evaluate cada N pasos |
| **Context overflow** | Se queda sin contexto | Compaction, checkpoints |
| **Over-confidence** | Dice "listo" sin verificar | Success criteria definidos |

---

## Solución para BRAIN

### Script Template para 3905 Filas

El script debe:

1. **Batch processing** — procesar en chunks de 100-500 filas
2. **Checkpointing** — guardar progreso cada N filas
3. **Error handling** — try/except por fila, continuar si falla
4. **Progress logging** — guardar qué se hizo
5. **Final report** — resumen al terminar

```python
import json
import os
from datetime import datetime

class AutonomousProcessor:
    def __init__(self, input_file, output_file, checkpoint_file):
        self.input_file = input_file
        self.output_file = output_file
        self.checkpoint_file = checkpoint_file
        self.processed = 0
        self.errors = []
        self.errors_file = "error_log.json"
        
    def load_checkpoint(self):
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file) as f:
                return json.load(f)
        return {'last_row': -1, 'processed': 0}
    
    def save_checkpoint(self, last_row):
        with open(self.checkpoint_file, 'w') as f:
            json.dump({
                'last_row': last_row,
                'processed': self.processed,
                'timestamp': datetime.now().isoformat()
            }, f)
    
    def process_batch(self, rows):
        results = []
        for row in rows:
            try:
                result = self.process_row(row)
                results.append(result)
                self.processed += 1
            except Exception as e:
                self.errors.append({
                    'row': row,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                # Continue processing - don't stop
        return results
    
    def process_row(self, row):
        # Tu lógica aquí
        pass
    
    def run(self):
        checkpoint = self.load_checkpoint()
        start_row = checkpoint['last_row'] + 1
        
        print(f"Resuming from row {start_row}")
        
        # Tu código para leer input y procesar
        # ...
        
        # Guardar checkpoint cada 100 filas
        if self.processed % 100 == 0:
            self.save_checkpoint(current_row)
        
        # Report final
        self.save_errors()
        print(f"Done. Processed: {self.processed}, Errors: {len(self.errors)}")
```

---

## Recomendación para BRAIN

Para ejecutar tareas largas sin preguntar:

1. **Usar checkpoint pattern** — guardar progreso cada 100-500 filas
2. **Try/except por item** — si falla uno, continuar con el siguiente
3. **Log de errores separado** — no perder información
4. **Resume capability** — si se corta, continuar desde donde quedó

---

*Investigador — Tareas_Autonomas investigación completada.*