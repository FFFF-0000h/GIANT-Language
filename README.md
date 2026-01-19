# GIANT Language

**Generalized Intelligent Anchor-based Notation & Types**

A relational programming language rooted in Nigerian Indigenous mathematical philosophy, combining natural Nigerian Pidgin English syntax with revolutionary anchor-based relational programming.

---

## Overview

GIANT (pronounced "Giant"; GIANT comments out as it is unpronouncable) is a programming paradigm that fundamentally reframes how we think about numbers and computation—from absolute quantities to contextual relationships.

### The Paradigm Shift

**Traditional Programming (Absolute):**
```python
temperature = 92
if temperature > 100:
    print("Danger!")
```
The code *knows* `92 < 100` but *understands* nothing about what this relationship *means*.

**GIANT (Relational):**
```naija
@anchor danger_threshold = 100
@anchor optimal_temp = 75

relational temperature = 92 relative to [optimal_temp, danger_threshold]

when temperature is "over" optimal_temp:
    @action talk "Temperature elevated!"

talk temperature
```
**Output:**
```
Temperature elevated!
92 (17 over optimal_temp, 8 under danger_threshold)
```

The variable *knows* its semantic position—not just numeric distance, but *meaning*.

---

## Quick Start

### Prerequisites

- **Python 3.10+** (required)
- No external dependencies needed (pure Python implementation)

### Installation

```bash
# Clone the repository
git clone https://github.com/FFFF-0000h/GIANT-Language.git
cd GIANT-Language

# Optional: Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Running GIANT

**Interactive REPL:**
```bash
python main.py
```

**Execute a script file:**
```bash
python main.py your_program.naija
```

**Run comprehensive test suite:**
```bash
python main.py misc/spec_test.naija
```

### Your First Program

Create `hello.naija`:
```naija
*sidegist* This is a comment in Nigerian Pidgin
talk "Hello from GIANT!"

make name be "World"
talk "Welcome" 
talk name
```

Run it:
```bash
python main.py hello.naija
```

---

## Core Concepts

### 1. Natural Language Syntax

Multiple ways to express the same operation (Nigerian Pidgin English):

```naija
*sidegist* Variable assignment (4 styles)
make x be 10
set y to 20
let z be 30
let formal be equal to 40

*sidegist* Arithmetic operations
talk x plus y           *sidegist* 30
talk 10 added to 5      *sidegist* 15
talk 20 subtract 8      *sidegist* 12
talk 7 multiplied by 3  *sidegist* 21
talk 100 over 4         *sidegist* 25
```

### 2. Anchors (Reference Points)

Anchors are meaningful reference points that provide context for values:

```naija
@anchor freezing_point = 32 unit = "fahrenheit"
@anchor body_temp = 98.6 unit = "fahrenheit" tolerance = 1
@anchor fever_threshold = 100.4 unit = "fahrenheit"

*sidegist* List all anchors
list anchors

*sidegist* Inspect specific anchor
describe anchor body_temp
```

### 3. Relational Variables

Variables that understand their position relative to anchors:

```naija
@anchor normal_heart_rate = 75 unit = "bpm"
@anchor bradycardia = 60 unit = "bpm"
@anchor tachycardia = 100 unit = "bpm"

relational patient_hr = 58 relative to [normal_heart_rate, bradycardia, tachycardia]

talk patient_hr
*sidegist* Output: 58 (17 under normal_heart_rate, 2 under bradycardia, 42 under tachycardia)
```

### 4. Semantic Conditionals (When-Clauses)

React based on relational position, not just numeric comparison:

```naija
@anchor speed_limit = 60 unit = "mph"
@anchor reckless_driving = 80 unit = "mph"

relational current_speed = 65 relative to [speed_limit, reckless_driving]

when current_speed is "over" speed_limit:
    @action talk "Speeding detected!"

when current_speed is "under" reckless_driving:
    @action talk "Still below reckless threshold"
```

### 5. Comments (Nigerian Linguistic Style)

```naija
*sidegist* Single-line comment (Nigerian Pidgin for "side story")

*omo*
Multi-line comment block
"omo" is Yoruba for "child" or "wow!"
Used to express surprise or emphasis
*omo*
```

---

## Implemented Features

### Fully Working

- **Variable Assignment** (4 syntax styles: make/set/let/let...equal)
- **Arithmetic Operations** (plus, minus, times, divided by, with alternative phrases)
- **String Variables**
- **Comments** (single-line `*sidegist*` and multi-line `*omo*...*omo*`)
- **Output Statements** (talk, show, wetin be)
- **Anchor Declarations** (with metadata: unit, tolerance, description, context, confidence)
- **Anchor Management** (list anchors, describe anchor, inspect anchor)
- **Relational Variables** (automatic relationship tracking to multiple anchors)
- **Relational Metadata** (context, policy, confidence, sensor_id, etc.)
- **When-Clauses** (reactive conditions: is "over", is "under", is "near")
- **Semantic Position Qualifiers** (over, under, near with tolerance awareness)

### Not Yet Implemented

- Traditional conditionals (if/else/den)
- Loops (repeat/while)
- User-defined functions
- Boolean logic operators (and/or/not)
- Traditional comparison operators (>, <, ==)
- Advanced math (sqrt, power, modulo)
- Lists/Arrays
- File I/O

---

## Testing the Implementation

### Run All Tests

```bash
python main.py misc/spec_test.naija
```

This executes 35 test sections covering:
- Variable assignments (all 4 styles)
- Arithmetic operations (standard and alternative phrases)
- Comments (single and multi-line)
- String handling
- Anchor declarations and queries
- Relational variables with metadata
- When-clauses and semantic conditions
- Complex relational scenarios

### Manual Testing in REPL

```bash
python main.py
```

```naija
>>> talk "Testing GIANT"
Testing GIANT

>>> make x be 10
>>> talk x
10

>>> @anchor threshold = 50
>>> relational value = 55 relative to [threshold]
>>> talk value
55 (5 over threshold)

>>> when value is "over" threshold: @action talk "Above threshold!"
Above threshold!

>>> stop
```

---

## Example Programs

### Temperature Monitoring System

```naija
talk "=== Temperature Monitoring System ==="
talk ""

*sidegist* Define anchors
@anchor freezing = 32 unit = "fahrenheit"
@anchor optimal = 75 unit = "fahrenheit" tolerance = 5
@anchor warning = 90 unit = "fahrenheit"
@anchor danger = 100 unit = "fahrenheit"

*sidegist* Create relational sensors
relational room_temp = 78 relative to [optimal, warning]
relational outdoor_temp = 45 relative to [freezing, optimal]
relational boiler_temp = 92 relative to [warning, danger]

*sidegist* Reactive monitoring
when room_temp is "over" optimal:
    @action talk "Room temperature elevated"

when boiler_temp is "over" warning:
    @action talk "ALERT: Boiler approaching danger zone"

when outdoor_temp is "under" optimal:
    @action talk "Outdoor temp below optimal"

*sidegist* Display status
talk "Room:"
talk room_temp
talk ""
talk "Outdoor:"
talk outdoor_temp
talk ""
talk "Boiler:"
talk boiler_temp
```

### Healthcare Vital Signs

```naija
talk "=== Patient Vital Signs Monitor ==="
talk ""

@anchor normal_hr = 75 unit = "bpm" tolerance = 10
@anchor bradycardia = 60 unit = "bpm"
@anchor tachycardia = 100 unit = "bpm"

relational patient_hr = 58 relative to [normal_hr, bradycardia, tachycardia]
    context = "resting_state"
    sensor_id = "HR_001"

when patient_hr is "under" bradycardia:
    @action talk "WARNING: Bradycardia detected"

when patient_hr is "near" normal_hr:
    @action talk "Heart rate within normal range"

talk "Patient Heart Rate:"
talk patient_hr

describe anchor normal_hr
```

---

## The Philosophy: Yoruba Mathematical Foundations

GIANT is inspired by the Yoruba numeral system of southwestern Nigeria, which naturally encodes relational thinking.

**Example:** The Yoruba word for 17 is *mẹ́tàdínlógún*, literally meaning "three taken from twenty" (20 - 3).

This isn't just linguistic—it's a **computational paradigm**:
- Numbers are expressed as relationships to meaningful anchors (10, 20)
- Operations are embedded in the representation itself
- Context determines the appropriate anchor and operation

**Read more:**
- `misc/YorubaNumeralSystem` - Cultural and mathematical context
- `misc/GIANT_Paper.pdf` - Complete research paper (25 pages)
- `misc/RELATIONAL_PARADIGM_ANALYSIS.md` - Paradigm analysis

---

## Name Etymology

**GIANT**: **G**eneralized **I**ntelligent **A**nchor-Based **N**otation for **T**olerance-aware computation. A programming paradigm that transcends conventional value-based thinking.

**GIANT**: 
- **Acronym**: Generalized Intelligent Anchor-based Notation & Types
- **Cultural**: Represents the Nigerian influence and the "giant" contribution of indigenous African mathematical systems

---

## Documentation

- **`misc/Tutorial.md`** - Complete language tutorial with examples
- **`misc/spec_test.naija`** - Comprehensive test suite (35 test sections)
- **`misc/spec.ebnf`** - Formal EBNF grammar
- **`misc/GIANT_Paper.pdf`** - Academic research paper (25 pages)
- **`misc/GIANT_Glossary.md`** - Technical glossary (100+ terms)
- **`misc/RELATIONAL_PARADIGM_ANALYSIS.md`** - Paradigm deep-dive

---

## Contributing

GIANT is being prepared for open-source release. Contributions will be welcome in areas such as:

- Additional language features (loops, functions, conditionals)
- Performance optimizations
- Standard library development
- Documentation improvements
- Example programs and tutorials
- Integration with existing tools/frameworks

---

## Roadmap

### Euphrates (Current Stream)
- Core relational variable system
- Anchor-based reference points
- When-clause reactivity
- Natural language syntax (Nigerian Pidgin)

### Tigris (In Development)
- Traditional control flow (if/else, loops)
- User-defined functions
- Advanced relational operators
- Type system refinement

### Gihon (Planned)
- Standard library (math, strings, I/O)
- Module/import system
- Package manager
- IDE/editor plugins
- Debugger tools

### Pishon (Future)
- Compiler optimizations
- JIT compilation
- Foreign function interface (FFI)
- Web/mobile deployment

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Itunuayo Adebiyi

---

## Author

**Itunuayo Adebiyi**

For questions, suggestions, or collaboration opportunities, please open an issue on the GitHub repository.

---

## Acknowledgments

This work honors:
- The Yoruba mathematical tradition and its relational numeral system
- Nigerian Pidgin English as a bridge between cultures and technical precision
- Indigenous African knowledge systems that have encoded sophisticated computational thinking for centuries

---

**GIANT: Where culture meets computation, and numbers become relationships.**
