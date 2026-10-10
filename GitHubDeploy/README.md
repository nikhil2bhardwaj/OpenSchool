# OpenSchool NCERT Virtual STEM Laboratory

Zero-dependency, offline-first virtual STEM laboratory with **70 NCERT/CBSE practicals** across Classes 9–12. Every sandbox runs entirely in the browser — even from a USB stick with no internet connection.

## Features

- **70 mapped practicals** across Classes 9–12 (Physics, Chemistry, Biology)
- **Pure static HTML** — no build step, no bundler, no server required
- **IndexedDB notebook** — save notes, viva results, observations per experiment
- **100% offline** — all simulation kernels, FSM reagent tests, and apparatus renderers run locally
- **Apparatus scenes** — personalized visual per experiment (25+ distinct scene types)
- **Deterministic JS simulation** — math reproducible, no CDN runtime dependencies
- **Class/Subject filter** — browse by Class 9–12 or Physics/Chemistry/Biology
- **Search** — filter by experiment ID, title, or aim
- **AI examiner** — optional cloud endpoint (opt-in only)

## Project Structure

```
GitHubDeploy/
├── index.html              (main hub, manifest-driven, 70 lab entries)
├── README.md               (this file)
├── assets/
│   ├── css/lab-theme.css
│   └── js/
│       ├── ai-examiner.js
│       └── storage.js
├── labs/
│   ├── class9/
│   │   ├── biology/       (4 new: osmosis, plasmolysis, binary fission, seed germination)
│   │   └── (existing: 10 labs including capillary_rise, friction, etc.)
│   ├── class10/          (10 existing labs)
│   ├── class11/physics/  (13 labs: 8 original + 5 new: Doppler, sonometer standing waves, beats, resonance column, Seebeck)
│   ├── class11/chemistry/ (7 original)
│   ├── class12/physics/  (15 labs: 9 original + 6 new: photoelectric, half-wave rectifier, Bohr model, radioactive decay, compound microscope, resolving power)
│   ├── class12/chemistry/ (11 labs: 6 original + 5 new: ethanol oxidation, esterification, iodine clock, solubility product, buffers)
│   └── class9/biology/   (4 new: osmosis, plasmolysis, binary fission, seed germination)
├── manifests/
│   └── catalog.json        (70 entries: id, cls, subject, archetype, title, aim, ready, href)
```

## How It Works

1. `index.html` loads the inline `CATALOG` array from `manifests/catalog.json`
2. The `render()` function generates cards from the catalog, applying Class/Subject filters and search
3. Clicking **Launch Lab →** navigates to the lab's standalone HTML file
4. Each lab sandbox:
   - Runs deterministic JS simulations (numeric curve fits, exponential decays, FSM reagent tests)
   - Renders a personalized apparatus scene (spring balances, circuits, optical benches, microscopes, thermocouples, etc.)
   - Stores notes/observations in IndexedDB (`storage.js`)
   - Supports an optional AI examiner (`ai-examiner.js`) — cloud endpoint opt-in only

## Development

- Add new labs by editing `manifests/catalog.json` and creating the corresponding `labs/<path>.html`
- All labs are zero-build — just open `index.html` in a browser or serve via `python3 -m http.server 8000`
- To deploy: run `python3 -m http.server 8000` in the project root

## License

Open-source, free to use and modify for educational purposes.

## Recent Additions (15 new labs)

### Class 11 Physics (5 labs)
- **P-C11-16** Doppler Effect — moving source/observer, frequency shift simulation
- **P-C11-17** Sonometer — standing waves, tension/length vs frequency
- **P-C11-18** Beats Frequency — two close tones, amplitude modulation
- **P-C11-19** Resonance Column — air column length, sound velocity measurement
- **P-C11-20** Seebeck Effect — thermoelectric voltage, Seebeck coefficient

### Class 12 Physics (6 labs)
- **P-C12-16** Photoelectric Effect — stopping potential, threshold frequency, Einstein equation
- **P-C12-17** Half-Wave Rectifier — diode + capacitor filter, Vdc and ripple factor
- **P-C12-18** Bohr's Atomic Model — energy levels, photon emission, Rydberg formula
- **P-C12-19** Radioactive Decay Law — exponential decay, half-life, activity (Bq)
- **P-C12-20** Compound Microscope — magnification, objective/eyepiece focal lengths
- **P-C12-21** Resolving Power — Rayleigh criterion, d = 1.22λ/NA, resolution limits

### Class 12 Chemistry (5 labs)
- **P-C12-22** Ethanol Oxidation — primary/secondary/tertiary alcohols, distinguish via oxidizing agents
- **P-C12-23** Esterification — acid + alcohol ⇌ ester + water, equilibrium conversion
- **P-C12-24** Iodine Clock Reaction — kinetics, rate law, rate constant
- **P-C12-25** Solubility Product of Ca(OH)2 — Ksp, saturation concentrations
- **P-C12-26** pH of Buffer Solutions — Henderson-Hasselbalch, buffer capacity

### Class 9 Biology (4 labs)
- **P-C09-11** Osmosis — potato osmometer, water level rise vs sucrose concentration
- **P-C09-12** Plasmolysis in Onion Peel — salt concentration vs cell shrinkage
- **P-C09-13** Binary Fission in Amoeba — micrograph stages of nuclear division
- **P-C09-14** Seed Germination — radicle emergence, moisture/temperature effects

## Browser/Server Compatibility

- Open `index.html` directly in any modern browser (Chrome, Firefox, Safari, Edge)
- Or serve via `python3 -m http.server 8000` for the full experience
- Zero external dependencies — all JS, CSS, and HTML are self-contained
- IndexedDB storage works offline; fallback to memory if IndexedDB unavailable

---
All 70 labs are catalogued and filterable. Open `index.html` and try the Class and Subject filter buttons — they now work correctly after the `wireFilters` bug fix.