# PDDL Continuous Domain Evolution: Comprehensive Scenario Descriptions Catalog

This catalog provides **over 110 diverse, formal natural language evolution descriptions** across **11 classical and benchmark planning domain families**. 

Every description is formulated for **genuine schema-level domain evolution** (introducing new predicates, constraints, failure modes, inspection cycles, or restorative actions) rather than superficial problem-level object instantiations. They are designed to test oracular validation, diagnostic triage, surgical AST repair, and backward compatibility regression testing.

---

## Table of Contents
1. [Depot / Depots (10 Descriptions)](#1-depot--depots)
2. [Barman (10 Descriptions)](#2-barman)
3. [Logistics / Freight Logistics (10 Descriptions)](#3-logistics--freight-logistics)
4. [Blocksworld (10 Descriptions)](#4-blocksworld)
5. [Rovers / Planetary Exploration (10 Descriptions)](#5-rovers--planetary-exploration)
6. [Satellite / Earth Observation (10 Descriptions)](#6-satellite--earth-observation)
7. [DriverLog (10 Descriptions)](#7-driverlog)
8. [ZenoTravel / Air Transport (10 Descriptions)](#8-zenotravel--air-transport)
9. [Gripper / Warehouse Robotics (10 Descriptions)](#9-gripper--warehouse-robotics)
10. [Miconic / Elevators (10 Descriptions)](#10-miconic--elevators)
11. [FreeCell (10 Descriptions)](#11-freecell)

---

## 1. Depot / Depots

### Evolution 1.1: Hoist Mechanical Wear & Servicing
* **Prompt**:
  > "Extend the Depot domain so that hoists experience mechanical fatigue after lifting or dropping crates. Introduce a `needs-maintenance` predicate and a `service-hoist` action that requires an available hoist and clears the maintenance requirement, while preserving backward compatibility with single- and multi-hoist problems."
* **Schema Evolution**:
  - Predicate: `(needs-maintenance ?h - hoist)`
  - Effect addition in `Lift` or `Drop`: `(needs-maintenance ?h)`
  - New Action: `(:action service-hoist :parameters (?h - hoist ?p - place) :precondition (and (at ?h ?p) (available ?h) (needs-maintenance ?h)) :effect (not (needs-maintenance ?h)))`
* **Backward Compatibility**: Legacy problem instances where hoists begin without `needs-maintenance` continue to solve cleanly.

### Evolution 1.2: Truck Fuel Consumption & Refueling
* **Prompt**:
  > "Extend the Depot domain with vehicle fuel constraints. Introduce fuel level tracking for trucks and a `refuel` action that can only be executed when a truck is at a designated depot equipped with a fuel pump, while ensuring backward compatibility with historical routing problems."
* **Schema Evolution**:
  - Predicates: `(fuel-empty ?t - truck)`, `(has-fuel-pump ?p - place)`
  - Precondition addition in `Drive`: `(not (fuel-empty ?t))`
  - Effect in `Drive`: `(fuel-empty ?t)`
  - New Action: `refuel(?t - truck ?p - place)`

### Evolution 1.3: Heavy Payload & Two-Hoist Lifting
* **Prompt**:
  > "Extend the Depot domain to support heavy industrial crates that require two independent hoists at the same location to lift simultaneously, while regular crates can still be lifted by a single hoist."
* **Schema Evolution**:
  - Types: `heavy-crate regular-crate - crate`
  - Action: `dual-lift(?h1 - hoist ?h2 - hoist ?c - heavy-crate ?s - surface ?p - place)`
  - Preserves standard `lift` for `regular-crate`.

### Evolution 1.4: Fragile Crate Inspection & Cushioning
* **Prompt**:
  > "Extend the Depot domain with fragile cargo handling rules: fragile crates must be inspected and marked as cushioned before they can be loaded onto trucks for transit."
* **Schema Evolution**:
  - Predicates: `(fragile ?c - crate)`, `(cushioned ?c - crate)`, `(inspected ?c - crate)`
  - Action: `inspect-and-cushion(?c - crate ?h - hoist ?p - place)`
  - Precondition addition in `Load`: when `(fragile ?c)`, require `(cushioned ?c)`.

### Evolution 1.5: Pallet Locking & Surface Security
* **Prompt**:
  > "Extend the Depot domain with surface safety locking: pallets must be unlocked before crates can be removed and locked before heavy transit occurs at a depot."
* **Schema Evolution**:
  - Predicates: `(locked ?p - pallet)`, `(unlocked ?p - pallet)`
  - Actions: `lock-pallet(?p - pallet)`, `unlock-pallet(?p - pallet)`

### Evolution 1.6: Hazardous Material Quarantine Certification
* **Prompt**:
  > "Extend the Depot domain so that hazardous chemical crates must undergo a decontamination check and receive a hazmat certification before entering standard distributor warehouses."
* **Schema Evolution**:
  - Predicates: `(hazardous ?c - crate)`, `(hazmat-certified ?c - crate)`
  - Action: `certify-hazmat(?c - crate ?p - place)`

### Evolution 1.7: Conveyor Belt Transfer
* **Prompt**:
  > "Extend the Depot domain with motorized conveyor belts connecting adjacent bays, introducing a `transfer-conveyor` action to move crates directly between surfaces without loading onto trucks."
* **Schema Evolution**:
  - Predicates: `(connected-conveyor ?s1 - surface ?s2 - surface)`
  - Action: `transfer-conveyor(?c - crate ?src - surface ?dst - surface)`

### Evolution 1.8: Electric Truck Recharging
* **Prompt**:
  > "Extend the Depot domain for electric fleet operations: trucks have battery charges that deplete after driving and must be recharged at electric charging docks."
* **Schema Evolution**:
  - Predicates: `(battery-low ?t - truck)`, `(has-charger ?p - place)`
  - Action: `recharge-truck(?t - truck ?p - place)`

### Evolution 1.9: Severe Weather Road Condition Restrictions
* **Prompt**:
  > "Extend the Depot domain to model inclement weather: routes between locations can be flagged as flooded or icy, requiring a `clear-route` snowplow action before trucks can traverse them."
* **Schema Evolution**:
  - Predicates: `(route-blocked ?from - place ?to - place)`
  - Action: `clear-route(?from - place ?to - place)`

### Evolution 1.10: Truck Capacity Limit
* **Prompt**:
  > "Extend the Depot domain so that trucks have finite cargo capacity: a truck can hold at most one primary crate at a time or must be marked as `truck-empty` before loading."
* **Schema Evolution**:
  - Predicates: `(truck-empty ?t - truck)`
  - Precondition addition in `Load`: `(truck-empty ?t)`
  - Effect in `Load`: `(not (truck-empty ?t))`
  - Effect in `Unload`: `(truck-empty ?t)`

---

## 2. Barman

### Evolution 2.1: Dispenser Clogging & Maintenance
* **Prompt**:
  > "Extend the barman domain with operational maintenance constraints: introduce a needs-maintenance condition for dispensers after dispensing ingredients, and a service action while preserving backward compatibility with historical problems."
* **Schema Evolution**:
  - Predicates: `(needs-maintenance ?d - dispenser)`
  - Action: `(:action service :parameters (?d - dispenser ?h - hand) :precondition (and (handempty ?h) (needs-maintenance ?d)) :effect (not (needs-maintenance ?d)))`

### Evolution 2.2: Ice Dispensing & Chilled Cocktails
* **Prompt**:
  > "Extend the barman domain to support chilled cocktail preparation: introduce an ice dispenser, an `add-ice` action into shakers, and a `chilled` predicate required for specialty cocktails."
* **Schema Evolution**:
  - Predicates: `(contains-ice ?s - shaker)`, `(chilled ?c - cocktail)`
  - Action: `add-ice(?s - shaker ?h - hand)`
  - Action update in `shake`: produces `(chilled ?c)` if `(contains-ice ?s)`.

### Evolution 2.3: Shaker Hot Water Sanitization
* **Prompt**:
  > "Extend the barman domain so that shakers used with dairy or allergen ingredients must undergo a hot-water sanitization cycle with a `sanitize-shaker` action before mixing citrus cocktails."
* **Schema Evolution**:
  - Predicates: `(sanitized ?s - shaker)`, `(has-allergen ?i - ingredient)`
  - Action: `sanitize-shaker(?s - shaker ?h1 - hand ?h2 - hand)`

### Evolution 2.4: Ingredient Bottle Restocking
* **Prompt**:
  > "Extend the barman domain with cellar restocking: ingredient dispensers can become empty and must be replenished from cellar supply crates using a `restock-dispenser` action."
* **Schema Evolution**:
  - Predicates: `(dispenser-empty ?d - dispenser)`, `(stock-available ?i - ingredient)`
  - Action: `restock-dispenser(?d - dispenser ?i - ingredient ?h - hand)`

### Evolution 2.5: Glassware Fragility & Breakage Inspection
* **Prompt**:
  > "Extend the barman domain with glassware safety: glasses must be visually inspected for micro-cracks using an `inspect-glass` action before pouring carbonated or shaken cocktails."
* **Schema Evolution**:
  - Predicates: `(inspected ?g - glass)`
  - Action: `inspect-glass(?g - glass ?h - hand)`

### Evolution 2.6: Cocktail Garnish & Citrus Twist
* **Prompt**:
  > "Extend the barman domain to support cocktail garnishing: glasses containing finished cocktails can receive fruit garnishes or citrus twists via an `add-garnish` action to complete premium drink orders."
* **Schema Evolution**:
  - Types: `garnish - object`
  - Predicate: `(garnished ?g - glass ?ga - garnish)`
  - Action: `add-garnish(?g - glass ?ga - garnish ?h - hand)`

### Evolution 2.7: Strainer Attachment & Fine Straining
* **Prompt**:
  > "Extend the barman domain so that shakers require a fine wire strainer attachment using a `fit-strainer` action before pouring into glasses to remove pulp and ice shards."
* **Schema Evolution**:
  - Types: `strainer - object`
  - Predicates: `(strainer-fitted ?s - shaker ?st - strainer)`
  - Actions: `fit-strainer`, `remove-strainer`

### Evolution 2.8: Double-Shaker Simultaneous Mixing
* **Prompt**:
  > "Extend the barman domain to allow skilled two-handed bartenders to shake two independent shakers simultaneously using a `dual-shake` action when holding one shaker in each hand."
* **Schema Evolution**:
  - Action: `dual-shake(?c1 - cocktail ?c2 - cocktail ?s1 - shaker ?s2 - shaker ?h1 - hand ?h2 - hand ...)`

### Evolution 2.9: Measuring Jigger for Precise Volume Ratios
* **Prompt**:
  > "Extend the barman domain with precision jiggers: instead of pouring directly from dispensers into glasses, ingredients must first be measured in a jigger cup using `measure-ingredient` before entering the shaker."
* **Schema Evolution**:
  - Types: `jigger - container`
  - Actions: `fill-jigger`, `dump-jigger-to-shaker`

### Evolution 2.10: Bottle Cap Sealing for Quality Preservation
* **Prompt**:
  > "Extend the barman domain so that premium liquor dispensers have protective caps that must be uncapped prior to pouring and resealed when finished."
* **Schema Evolution**:
  - Predicates: `(capped ?d - dispenser)`, `(uncapped ?d - dispenser)`
  - Actions: `uncap-dispenser(?d - dispenser ?h - hand)`, `cap-dispenser(?d - dispenser ?h - hand)`

---

## 3. Logistics / Freight Logistics

### Evolution 3.1: Vehicle Routine Maintenance & Overhaul
* **Prompt**:
  > "Extend the Logistics domain so that delivery vehicles (trucks and airplanes) require routine maintenance after inter-city travel: introduce a needs-maintenance condition and a service-vehicle action while preserving backward compatibility."
* **Schema Evolution**:
  - Predicates: `(needs-maintenance ?v - vehicle)`, `(has-service-bay ?loc - location)`
  - Action: `service-vehicle(?v - vehicle ?loc - location)`

### Evolution 3.2: Fuel Limits & Highway Refueling Stations
* **Prompt**:
  > "Extend the Logistics domain with fuel constraints: airplanes consume aviation fuel per flight and must refuel at designated airport fuel depots before takeoff."
* **Schema Evolution**:
  - Predicates: `(fuel-depleted ?a - airplane)`, `(has-aviation-fuel ?ap - airport)`
  - Action: `refuel-airplane(?a - airplane ?ap - airport)`

### Evolution 3.3: Hazardous Cargo Clearance & Hazmat Certification
* **Prompt**:
  > "Extend the Logistics domain so that packages containing dangerous goods require hazardous materials inspection and a safety permit before being loaded onto passenger airplanes."
* **Schema Evolution**:
  - Predicates: `(hazmat ?p - package)`, `(hazmat-certified ?p - package)`
  - Action: `inspect-hazmat(?p - package ?loc - location)`

### Evolution 3.4: Weight Capacity & Cargo Load Limiting
* **Prompt**:
  > "Extend the Logistics domain so that trucks have finite capacity limits: each truck can only hold one package at a time or must be certified as empty before loading additional cargo."
* **Schema Evolution**:
  - Predicates: `(truck-empty ?t - truck)`
  - Action constraints in `load-truck` and `unload-truck`.

### Evolution 3.5: Cold-Chain Refrigerated Transport
* **Prompt**:
  > "Extend the Logistics domain to support temperature-sensitive pharmaceutical packages: introduce refrigerated trucks and a `check-temperature` action to guarantee climate compliance."
* **Schema Evolution**:
  - Predicates: `(refrigerated ?t - truck)`, `(temp-sensitive ?p - package)`, `(temp-ok ?p - package)`
  - Action: `monitor-cold-chain(?p - package ?t - truck)`

### Evolution 3.6: Express Air Courier Direct Routing
* **Prompt**:
  > "Extend the Logistics domain with express Priority-1 routing: priority packages can bypass regional sorting hubs and fly directly between local airfields."
* **Schema Evolution**:
  - Predicates: `(priority-package ?p - package)`
  - Action: `direct-air-courier(?p - package ?a - airplane ?from - location ?to - location)`

### Evolution 3.7: Severe Weather Ground Transport De-Icing
* **Prompt**:
  > "Extend the Logistics domain with winter weather handling: trucks traveling between snowy locations must pass through a de-icing bay before highway transit."
* **Schema Evolution**:
  - Predicates: `(icy-route ?from - location ?to - location)`, `(de-iced ?t - truck)`
  - Action: `de-ice-truck(?t - truck ?loc - location)`

### Evolution 3.8: Barcode Inventory Scanning at Hubs
* **Prompt**:
  > "Extend the Logistics domain with inventory tracking: packages unloaded at sorting facilities must be scanned with a barcode reader before they become eligible for truck loading."
* **Schema Evolution**:
  - Predicates: `(scanned ?p - package ?loc - location)`
  - Action: `scan-package(?p - package ?loc - location)`

### Evolution 3.9: Electric Delivery Vans & Solar Charging
* **Prompt**:
  > "Extend the Logistics domain for eco-friendly logistics: metropolitan delivery vans operate on electric batteries and must dock at charging stations between route deliveries."
* **Schema Evolution**:
  - Predicates: `(battery-empty ?v - van)`, `(charging-station ?loc - location)`
  - Action: `charge-van(?v - van ?loc - location)`

### Evolution 3.10: Delivery Confirmation & Recipient Signature
* **Prompt**:
  > "Extend the Logistics domain with last-mile proof-of-delivery: packages at destination offices must undergo a `sign-for-delivery` action before the goal condition is finalized."
* **Schema Evolution**:
  - Predicates: `(delivered ?p - package)`, `(signature-obtained ?p - package)`
  - Action: `sign-for-delivery(?p - package ?loc - location)`

---

## 4. Blocksworld

### Evolution 4.1: Robot Arm Mechanical Calibration & Servicing
* **Prompt**:
  > "Extend the Blocksworld domain so that the robot arm requires periodic calibration after moving blocks: introduce a `needs-maintenance` condition and a `calibrate-arm` action while preserving backward compatibility with standard block stacking problems."
* **Schema Evolution**:
  - Predicates: `(needs-maintenance)`
  - Precondition addition in `pick-up` / `unstack`: `(not (needs-maintenance))`
  - Effect in `stack` / `put-down`: `(needs-maintenance)`
  - Action: `(:action calibrate-arm :precondition (and (handempty) (needs-maintenance)) :effect (not (needs-maintenance)))`

### Evolution 4.2: Fragile Glass Blocks
* **Prompt**:
  > "Extend the Blocksworld domain to include fragile blocks: fragile blocks cannot have heavy blocks stacked directly on top of them unless a protective felt pad is placed."
* **Schema Evolution**:
  - Predicates: `(fragile ?b - block)`, `(padded ?b - block)`
  - Action: `place-pad(?b - block)`
  - Precondition in `stack`: `(or (not (fragile ?bottom)) (padded ?bottom))`

### Evolution 4.3: Two-Handed Heavy Block Lifting
* **Prompt**:
  > "Extend the Blocksworld domain with dual robot hands: heavy blocks require both `hand1` and `hand2` to be empty and lift simultaneously via a `dual-unstack` action."
* **Schema Evolution**:
  - Types: `hand - object`, `heavy-block normal-block - block`
  - Action: `dual-unstack(?b - heavy-block ?under - block ?h1 - hand ?h2 - hand)`

### Evolution 4.4: Magnetic Block Polarity Alignment
* **Prompt**:
  > "Extend the Blocksworld domain with magnetic blocks: blocks possess magnetic poles and must have opposite poles aligned before they can bond in a stack."
* **Schema Evolution**:
  - Predicates: `(north-pole ?b - block)`, `(south-pole ?b - block)`
  - Action: `flip-block(?b - block)`

### Evolution 4.5: Block Painting & Curing
* **Prompt**:
  > "Extend the Blocksworld domain with painting capabilities: raw wood blocks must be painted in a paint spray booth and air-cured before they can be stacked onto finished towers."
* **Schema Evolution**:
  - Types: `color - object`
  - Predicates: `(colored ?b - block ?c - color)`, `(cured ?b - block)`
  - Actions: `spray-paint(?b - block ?c - color)`, `cure-block(?b - block)`

### Evolution 4.6: Table Workspace Dust Clearance
* **Prompt**:
  > "Extend the Blocksworld domain with workspace clean-room rules: table surfaces accumulate debris and must be swept with a `clean-table` action before putting blocks down."
* **Schema Evolution**:
  - Predicates: `(table-clean)`, `(table-dusty)`
  - Action: `clean-table`

### Evolution 4.7: Dimension Stacking Hierarchy
* **Prompt**:
  > "Extend the Blocksworld domain with geometric size constraints: smaller blocks cannot support larger blocks; a block can only be stacked on top of an equal or larger block."
* **Schema Evolution**:
  - Predicates: `(larger ?b1 - block ?b2 - block)`
  - Precondition addition in `stack(?top ?bottom)`: `(not (larger ?top ?bottom))`

### Evolution 4.8: Robotic Hand Battery Recharging
* **Prompt**:
  > "Extend the Blocksworld domain so that the robot operates on a rechargeable battery that depletes with each pick-and-place cycle and requires docking at a charging pad."
* **Schema Evolution**:
  - Predicates: `(battery-depleted)`
  - Action: `recharge-gripper`

### Evolution 4.9: Ultrasonic Structural Crack Inspection
* **Prompt**:
  > "Extend the Blocksworld domain so that reclaimed blocks must undergo an ultrasonic flaw inspection before being certified as safe for load-bearing foundation stacks."
* **Schema Evolution**:
  - Predicates: `(inspected ?b - block)`, `(flawless ?b - block)`
  - Action: `inspect-structural-integrity(?b - block)`

### Evolution 4.10: Adhesive Bonding & Solvent Detachment
* **Prompt**:
  > "Extend the Blocksworld domain with chemical bonding: stacking blocks requires applying adhesive, and unstacking glued blocks requires applying solvent."
* **Schema Evolution**:
  - Predicates: `(glued ?b1 - block ?b2 - block)`
  - Actions: `apply-glue(?b1 ?b2)`, `apply-solvent(?b1 ?b2)`

---

## 5. Rovers / Planetary Exploration

### Evolution 5.1: Spectrometer Recalibration & Servicing
* **Prompt**:
  > "Extend the Rovers domain with scientific instrumentation maintenance: spectrometers must be recalibrated with a `calibrate-sensor` action after soil or rock analyses to clear sensor drift."
* **Schema Evolution**:
  - Predicates: `(sensor-drift ?r - rover ?s - spectrometer)`
  - Action: `calibrate-sensor(?r - rover ?s - spectrometer ?target - calibration_target)`

### Evolution 5.2: Solar Battery Depletion & Sun Exposure Recharging
* **Prompt**:
  > "Extend the Rovers domain with energy constraints: traverse maneuvers consume solar battery charge, requiring the rover to stop at sunlit waypoints and execute a `recharge-battery` action."
* **Schema Evolution**:
  - Predicates: `(battery-low ?r - rover)`, `(sunlit ?w - waypoint)`
  - Action: `recharge-battery(?r - rover ?w - waypoint)`

### Evolution 5.3: Sample Chamber Purging & Decontamination
* **Prompt**:
  > "Extend the Rovers domain so that sample collection chambers must be purged with inert nitrogen using a `purge-chamber` action to prevent cross-contamination between core samples."
* **Schema Evolution**:
  - Predicates: `(chamber-contaminated ?r - rover)`, `(chamber-purged ?r - rover)`
  - Action: `purge-chamber(?r - rover ?w - waypoint)`

### Evolution 5.4: Rough Terrain Hazard & Wheel Traction Inspection
* **Prompt**:
  > "Extend the Rovers domain with hazardous topography: traversing dune waypoints risks wheel slippage, requiring a `check-wheel-traction` action before proceeding onto bedrock."
* **Schema Evolution**:
  - Predicates: `(dune-terrain ?w1 - waypoint ?w2 - waypoint)`, `(traction-verified ?r - rover)`
  - Action: `check-wheel-traction(?r - rover ?w - waypoint)`

### Evolution 5.5: High-Gain Antenna Satellite Orbital Window Lock
* **Prompt**:
  > "Extend the Rovers domain so that data transmission to the orbiter requires establishing an antenna line-of-sight lock during active flyover communication windows."
* **Schema Evolution**:
  - Predicates: `(orbiter-window-open ?o - orbiter ?w - waypoint)`, `(antenna-locked ?r - rover ?o - orbiter)`
  - Action: `acquire-satellite-lock(?r - rover ?o - orbiter ?w - waypoint)`

### Evolution 5.6: Sample Cache Storage Capacity
* **Prompt**:
  > "Extend the Rovers domain with physical canister limits: the rover can hold only two rock cores simultaneously before it must offload them into a stationary Mars ascent depot."
* **Schema Evolution**:
  - Predicates: `(cache-full ?r - rover)`, `(cache-empty ?r - rover)`
  - Action: `deposit-sample-to-lander(?r - rover ?s - store ?l - lander ?w - waypoint)`

### Evolution 5.7: Nighttime Low-Power Sleep & Thermal Heating
* **Prompt**:
  > "Extend the Rovers domain with diurnal temperature cycles: rovers must activate survival heaters and enter a `sleep-mode` action during freezing Martian nights."
* **Schema Evolution**:
  - Predicates: `(night-cycle)`, `(heaters-active ?r - rover)`
  - Actions: `enter-sleep-mode`, `wake-rover`

### Evolution 5.8: Optical Dust Blower for Camera Lenses
* **Prompt**:
  > "Extend the Rovers domain so that camera lenses accumulate dust after driving, requiring a compressed-gas `clean-lens` action before acquiring high-resolution panoramas."
* **Schema Evolution**:
  - Predicates: `(lens-dusty ?c - camera)`, `(lens-clean ?c - camera)`
  - Action: `clean-lens(?r - rover ?c - camera)`

### Evolution 5.9: Robotic Arm Micro-Drill Bit Replacement
* **Prompt**:
  > "Extend the Rovers domain with tool wear: drill bits become blunted after penetrating basalt rock and must be swapped out at the lander tool rack."
* **Schema Evolution**:
  - Predicates: `(bit-blunted ?r - rover)`, `(bit-sharp ?r - rover)`
  - Action: `swap-drill-bit(?r - rover ?l - lander ?w - waypoint)`

### Evolution 5.10: Atmospheric Weather Monitoring & Storm Evasion
* **Prompt**:
  > "Extend the Rovers domain with atmospheric safety: rovers must take meteorological pressure readings with a `record-weather` action before initiating long traverses."
* **Schema Evolution**:
  - Predicates: `(weather-checked ?w - waypoint)`
  - Action: `record-weather(?r - rover ?w - waypoint)`

---

## 6. Satellite / Earth Observation

### Evolution 6.1: Imaging Instrument Sensor Calibration
* **Prompt**:
  > "Extend the Satellite domain with sensor calibration requirements: cameras and infrared sensors experience thermal drift and must target deep-space calibration stars via a `calibrate-sensor` action after taking Earth observations."
* **Schema Evolution**:
  - Predicates: `(sensor-drift ?i - instrument)`, `(calibrated ?i - instrument)`
  - Action: `calibrate-sensor(?s - satellite ?i - instrument ?d - direction)`

### Evolution 6.2: Solar Panel Orientation & Battery Storage
* **Prompt**:
  > "Extend the Satellite domain with power constraints: turning the satellite body consumes stored electrical charge, requiring a `point-to-sun` action to recharge solar arrays."
* **Schema Evolution**:
  - Predicates: `(battery-low ?s - satellite)`, `(charging ?s - satellite)`
  - Action: `point-to-sun(?s - satellite ?sun_dir - direction)`

### Evolution 6.3: Solid-State Memory Buffer Capacity & Downlink Flushing
* **Prompt**:
  > "Extend the Satellite domain so that on-board memory buffers can fill up with image data, requiring an explicit `downlink-and-flush` action to ground stations before capturing new scenes."
* **Schema Evolution**:
  - Predicates: `(memory-full ?s - satellite)`, `(memory-cleared ?s - satellite)`
  - Action: `downlink-and-flush(?s - satellite ?d - data ?g - ground_station)`

### Evolution 6.4: Lens Sun-Shield Protection During Slew
* **Prompt**:
  > "Extend the Satellite domain so that optical sensor apertures must be closed with a protective sun-shield before slewing near the solar limb to avoid burning focal plane detectors."
* **Schema Evolution**:
  - Predicates: `(shield-closed ?i - instrument)`, `(shield-open ?i - instrument)`
  - Actions: `close-shield(?i)`, `open-shield(?i)`

### Evolution 6.5: Cold-Gas Thruster Propellant Depletion & Orbit Keeping
* **Prompt**:
  > "Extend the Satellite domain with orbital momentum: attitude adjustments deplete cold-gas thruster fuel, requiring momentum wheel desaturation maneuvers."
* **Schema Evolution**:
  - Predicates: `(momentum-saturated ?s - satellite)`
  - Action: `desaturate-momentum-wheels(?s - satellite)`

### Evolution 6.6: Multi-Spectral Optical Filter Switching
* **Prompt**:
  > "Extend the Satellite domain to support multi-spectral imaging: cameras have rotating filter wheels (visual, near-infrared, thermal) that must be aligned with a `switch-filter` action."
* **Schema Evolution**:
  - Types: `filter_mode - object`
  - Predicates: `(active-filter ?i - instrument ?f - filter_mode)`
  - Action: `switch-filter(?i - instrument ?old_f - filter_mode ?new_f - filter_mode)`

### Evolution 6.7: Cryogenic Cooler Servicing for Infrared Sensors
* **Prompt**:
  > "Extend the Satellite domain so that high-precision thermal infrared detectors must be cryo-cooled below 70 Kelvin with a `cool-detector` action before acquiring thermal imagery."
* **Schema Evolution**:
  - Predicates: `(cryo-cooled ?i - instrument)`
  - Action: `cool-detector(?s - satellite ?i - instrument)`

### Evolution 6.8: Ground Station Tracking Acquisition Lock
* **Prompt**:
  > "Extend the Satellite domain so that downlinking data requires first establishing a radio frequency handshake with a ground receiving dish using an `acquire-tracking-lock` action."
* **Schema Evolution**:
  - Predicates: `(tracking-locked ?s - satellite ?g - ground_station)`
  - Action: `acquire-tracking-lock(?s - satellite ?g - ground_station)`

### Evolution 6.9: Gyroscope Stabilization Settle Time
* **Prompt**:
  > "Extend the Satellite domain so that slewing introduces structural vibration: the satellite must execute a `settle-attitude` action before high-magnification telescopes can expose image sensors."
* **Schema Evolution**:
  - Predicates: `(attitude-settled ?s - satellite)`
  - Action: `settle-attitude(?s - satellite)`

### Evolution 6.10: Cryptographic Key Exchange Before Downlink
* **Prompt**:
  > "Extend the Satellite domain with secure communications: observational telemetry must be encrypted using an authorized ground security key via an `encrypt-payload` action."
* **Schema Evolution**:
  - Predicates: `(encrypted ?d - data_packet)`
  - Action: `encrypt-payload(?s - satellite ?d - data_packet ?k - key)`

---

## 7. DriverLog

### Evolution 7.1: Driver Fatigue & Mandatory Rest Periods
* **Prompt**:
  > "Extend the DriverLog domain so that human drivers experience fatigue after long drives: introduce a `fatigued` condition and a `take-rest-break` action at rest stops while preserving backward compatibility."
* **Schema Evolution**:
  - Predicates: `(fatigued ?d - driver)`, `(is-rest-stop ?loc - location)`
  - Action: `take-rest-break(?d - driver ?loc - location)`

### Evolution 7.2: Truck Tire Pressure Inspection & Maintenance
* **Prompt**:
  > "Extend the DriverLog domain with vehicle maintenance: truck tires lose pressure over rough path roads, requiring a `service-tires` action at mechanical workshops."
* **Schema Evolution**:
  - Predicates: `(tires-low ?t - truck)`, `(has-workshop ?loc - location)`
  - Action: `service-tires(?t - truck ?loc - location)`

### Evolution 7.3: Commercial Driver Licensing & Security Checkpoints
* **Prompt**:
  > "Extend the DriverLog domain with regulatory compliance: drivers must present certified commercial licenses at interstate toll checkpoints via a `verify-driver-credentials` action."
* **Schema Evolution**:
  - Predicates: `(credential-verified ?d - driver ?loc - location)`
  - Action: `verify-driver-credentials(?d - driver ?loc - location)`

### Evolution 7.4: Heavy Cargo Strapping & Tie-Down Inspection
* **Prompt**:
  > "Extend the DriverLog domain so that heavy packages loaded onto trucks must be secured with ratchet straps using a `strap-cargo` action before the truck can drive."
* **Schema Evolution**:
  - Predicates: `(strapped ?p - package ?t - truck)`
  - Action: `strap-cargo(?d - driver ?p - package ?t - truck)`

### Evolution 7.5: Winter Snow Chain Installation
* **Prompt**:
  > "Extend the DriverLog domain with mountain road conditions: driving over steep mountain passes requires drivers to install tire snow chains with an `install-chains` action."
* **Schema Evolution**:
  - Predicates: `(chains-fitted ?t - truck)`
  - Actions: `install-chains(?d ?t ?loc)`, `remove-chains(?d ?t ?loc)`

### Evolution 7.6: Engine Oil & Fluid Top-Up
* **Prompt**:
  > "Extend the DriverLog domain so that trucks require engine fluid top-ups after inter-city travel before they can take on new delivery routes."
* **Schema Evolution**:
  - Predicates: `(fluid-low ?t - truck)`
  - Action: `service-fluids(?t - truck ?loc - location)`

### Evolution 7.7: Passenger Ride-Sharing Along Delivery Routes
* **Prompt**:
  > "Extend the DriverLog domain so that trucks have passenger seats allowing stranded secondary drivers to ride along between depots via `board-passenger` and `debark-passenger` actions."
* **Schema Evolution**:
  - Predicates: `(passenger-in ?d - driver ?t - truck)`
  - Actions: `board-passenger`, `debark-passenger`

### Evolution 7.8: Highway Weigh Station Axle Inspection
* **Prompt**:
  > "Extend the DriverLog domain with highway weigh station clearance: loaded trucks must stop at state weigh stations to receive weight compliance stamps."
* **Schema Evolution**:
  - Predicates: `(weight-cleared ?t - truck ?loc - location)`
  - Action: `inspect-axle-weight(?t - truck ?loc - location)`

### Evolution 7.9: Electric Delivery Trucks with Rapid Charging
* **Prompt**:
  > "Extend the DriverLog domain for zero-emission fleets: electric trucks consume battery energy while driving and must dock at charging plazas."
* **Schema Evolution**:
  - Predicates: `(battery-empty ?t - truck)`, `(charging-plaza ?loc - location)`
  - Action: `charge-truck(?t - truck ?loc - location)`

### Evolution 7.10: Recipient Delivery Signature Handover
* **Prompt**:
  > "Extend the DriverLog domain so that unloading a package at its final destination requires obtaining a customer signature via a `confirm-delivery` action."
* **Schema Evolution**:
  - Predicates: `(delivery-confirmed ?p - package)`
  - Action: `confirm-delivery(?d - driver ?p - package ?loc - location)`

---

## 8. ZenoTravel / Air Transport

### Evolution 8.1: Jet Aircraft Engine Overhaul & Maintenance
* **Prompt**:
  > "Extend the air transport domain with operational maintenance constraints: introduce a needs-maintenance condition for aircraft after high-speed flights, and a service action while preserving backward compatibility with historical problems."
* **Schema Evolution**:
  - Predicates: `(needs-maintenance ?a - aircraft)`, `(has-hangar ?c - city)`
  - Action: `service-aircraft(?a - aircraft ?c - city)`

### Evolution 8.2: Cabin Turnaround Sanitization
* **Prompt**:
  > "Extend the air transport domain so that passenger aircraft cabins must undergo a sanitization and restocking turnaround cycle using a `sanitize-cabin` action between deboarding and boarding."
* **Schema Evolution**:
  - Predicates: `(cabin-clean ?a - aircraft)`, `(cabin-dirty ?a - aircraft)`
  - Action: `sanitize-cabin(?a - aircraft ?c - city)`

### Evolution 8.3: Emergency Oxygen & Safety Check
* **Prompt**:
  > "Extend the air transport domain with pre-flight safety inspections: flight crews must certify life-support and emergency oxygen systems with an `inspect-safety-equipment` action before passenger boarding."
* **Schema Evolution**:
  - Predicates: `(safety-inspected ?a - aircraft)`
  - Action: `inspect-safety-equipment(?a - aircraft ?c - city)`

### Evolution 8.4: Air Traffic Control Runway Departure Clearance
* **Prompt**:
  > "Extend the air transport domain so that flights cannot depart without acquiring takeoff runway clearance from regional ATC towers via a `request-takeoff-clearance` action."
* **Schema Evolution**:
  - Predicates: `(clearance-granted ?a - aircraft ?c - city)`
  - Action: `request-takeoff-clearance(?a - aircraft ?c - city)`

### Evolution 8.5: Cargo Hold Weight Balancing
* **Prompt**:
  > "Extend the air transport domain with center-of-gravity balancing: passenger luggage holds must be verified as balanced via a `balance-cargo-holds` action before long-haul flights."
* **Schema Evolution**:
  - Predicates: `(cargo-balanced ?a - aircraft)`
  - Action: `balance-cargo-holds(?a - aircraft ?c - city)`

### Evolution 8.6: Severe Weather Storm Avoidance
* **Prompt**:
  > "Extend the air transport domain with meteorological constraints: air routes affected by convective thunderstorms require aircraft to engage storm-avoidance waypoints."
* **Schema Evolution**:
  - Predicates: `(stormy-corridor ?from - city ?to - city)`
  - Action: `fly-storm-detour(?a - aircraft ?from - city ?to - city)`

### Evolution 8.7: Winter Wing De-Icing Operations
* **Prompt**:
  > "Extend the air transport domain with ground de-icing: aircraft parked in freezing winter airports must be treated with heated glycol fluid using a `deice-wings` action before takeoff."
* **Schema Evolution**:
  - Predicates: `(wings-iced ?a - aircraft)`, `(wings-clean ?a - aircraft)`
  - Action: `deice-wings(?a - aircraft ?c - city)`

### Evolution 8.8: Flight Crew Duty Time Limits
* **Prompt**:
  > "Extend the air transport domain with pilot duty regulations: flight crews experience duty-hour expiration after zoom flights and must be swapped with a fresh crew via `relieve-crew`."
* **Schema Evolution**:
  - Predicates: `(crew-rested ?a - aircraft)`, `(crew-exhausted ?a - aircraft)`
  - Action: `relieve-crew(?a - aircraft ?c - city)`

### Evolution 8.9: Auxiliary Fuel Tank Transfer
* **Prompt**:
  > "Extend the air transport domain with auxiliary fuel tanks: long-distance flights can open cross-feed fuel valves using a `pump-aux-fuel` action to extend operational flight range."
* **Schema Evolution**:
  - Predicates: `(has-aux-fuel ?a - aircraft)`
  - Action: `pump-aux-fuel(?a - aircraft)`

### Evolution 8.10: Terminal Gate Pushback Tug Operations
* **Prompt**:
  > "Extend the air transport domain with airport ramp operations: aircraft parked at terminal gates require a ground pushback tug using a `pushback-from-gate` action before engines can spool up."
* **Schema Evolution**:
  - Predicates: `(at-gate ?a - aircraft ?c - city)`, `(on-taxiway ?a - aircraft ?c - city)`
  - Action: `pushback-from-gate(?a - aircraft ?c - city)`

---

## 9. Gripper / Warehouse Robotics

### Evolution 9.1: Gripper Finger Pad Wear & Maintenance
* **Prompt**:
  > "Extend the Gripper domain so that robotic grippers experience pad wear after carrying heavy objects: introduce a needs-maintenance condition and a service-gripper action at maintenance docks while preserving backward compatibility."
* **Schema Evolution**:
  - Predicates: `(needs-maintenance ?g - gripper)`
  - Action: `(:action service-gripper :parameters (?g - gripper ?r - room) :precondition (and (gripper-at ?r) (needs-maintenance ?g)) :effect (not (needs-maintenance ?g)))`

### Evolution 9.2: Autonomous Battery Depletion & Recharging Dock
* **Prompt**:
  > "Extend the Gripper domain with battery energy constraints: moving between rooms depletes the robot's battery, requiring it to return to a charging dock and execute a `recharge` action."
* **Schema Evolution**:
  - Predicates: `(battery-empty)`, `(has-charging-dock ?r - room)`
  - Action: `recharge(?r - room)`

### Evolution 9.3: Dual-Gripper Heavy Ball Handling
* **Prompt**:
  > "Extend the Gripper domain to support heavy medicine balls: heavy balls require both left and right grippers to grasp simultaneously using a `dual-pick` action."
* **Schema Evolution**:
  - Types: `heavy-ball small-ball - ball`
  - Action: `dual-pick(?b - heavy-ball ?r - room ?g1 - gripper ?g2 - gripper)`

### Evolution 9.4: Barcode Tag Scanning Before Room Transfer
* **Prompt**:
  > "Extend the Gripper domain with warehouse inventory scanning: every ball picked up in Room A must be scanned with a barcode reader before being deposited into Room B."
* **Schema Evolution**:
  - Predicates: `(scanned ?b - ball)`
  - Action: `scan-ball(?b - ball ?g - gripper)`

### Evolution 9.5: Clean-Room Floor Decontamination
* **Prompt**:
  > "Extend the Gripper domain with clean-room protocols: moving into sterile medical supply rooms requires the robot wheels to pass through a UV disinfectant wash station."
* **Schema Evolution**:
  - Predicates: `(sterile-room ?r - room)`, `(robot-sterilized)`
  - Action: `sterilize-robot(?r - room)`

### Evolution 9.6: Fragile Glass Spheres & Slow Transit Mode
* **Prompt**:
  > "Extend the Gripper domain with fragile object handling: holding fragile glass balls forces the robot to move at low speed, preventing transit through high-traffic doorways unless cleared."
* **Schema Evolution**:
  - Predicates: `(fragile ?b - ball)`, `(corridor-clear ?from - room ?to - room)`
  - Action: `clear-corridor(?from - room ?to - room)`

### Evolution 9.7: Automated Sorting Conveyor Handoff
* **Prompt**:
  > "Extend the Gripper domain with sorting conveyors: the robot can place balls onto an automated conveyor belt that automatically transports them to designated inspection rooms."
* **Schema Evolution**:
  - Predicates: `(on-conveyor ?b - ball)`, `(conveyor-connects ?r1 - room ?r2 - room)`
  - Action: `place-on-conveyor(?b - ball ?g - gripper ?r - room)`

### Evolution 9.8: Quarantine Bay for Damaged Objects
* **Prompt**:
  > "Extend the Gripper domain so that dropped or scuffed balls must be moved to an isolation quarantine room for quality assurance before they can enter the goal room."
* **Schema Evolution**:
  - Predicates: `(quarantined ?b - ball)`
  - Action: `quarantine-ball(?b - ball ?r - room)`

### Evolution 9.9: Vision Camera Calibration in Shaded Rooms
* **Prompt**:
  > "Extend the Gripper domain so that entering unlit storage rooms requires turning on auxiliary inspection floodlights and recalibrating the depth camera."
* **Schema Evolution**:
  - Predicates: `(lights-on ?r - room)`, `(camera-calibrated)`
  - Actions: `switch-lights(?r)`, `calibrate-camera(?r)`

### Evolution 9.10: Emergency Safety Interlock Reset
* **Prompt**:
  > "Extend the Gripper domain with factory safety protocols: human presence in a room triggers an emergency soft-stop that must be acknowledged via an `acknowledge-safety-interlock` action."
* **Schema Evolution**:
  - Predicates: `(safety-halt ?r - room)`
  - Action: `acknowledge-safety-interlock(?r - room)`

---

## 10. Miconic / Elevators

### Evolution 10.1: Cable & Motor Operational Servicing
* **Prompt**:
  > "Extend the Miconic elevator domain with operational maintenance constraints: introduce a needs-maintenance condition after vertical travel, and a service-lift action at ground floor workshops while preserving backward compatibility with passenger delivery problems."
* **Schema Evolution**:
  - Predicates: `(needs-maintenance ?l - lift)`, `(is-ground-floor ?f - floor)`
  - Action: `service-lift(?l - lift ?f - floor)`

### Evolution 10.2: Cabin Weight Capacity Limit
* **Prompt**:
  > "Extend the Miconic elevator domain with payload capacity constraints: the elevator cabin can hold at most two passengers simultaneously before triggering an overload sensor."
* **Schema Evolution**:
  - Predicates: `(cabin-full ?l - lift)`, `(cabin-available ?l - lift)`
  - Action updates in `board` and `depart`.

### Evolution 10.3: Priority VIP Keycard Access & Express Mode
* **Prompt**:
  > "Extend the Miconic elevator domain with executive access: VIP passengers holding keycards can activate express mode to travel directly to penthouse suites without intermediate stops."
* **Schema Evolution**:
  - Predicates: `(vip-passenger ?p - person)`, `(express-mode ?l - lift)`
  - Action: `activate-express-mode(?p - person ?l - lift)`

### Evolution 10.4: Cabin Sanitization Between Passenger Batches
* **Prompt**:
  > "Extend the Miconic elevator domain with hygiene protocols: hospital elevators must undergo a UV air sanitization cycle with a `sanitize-cabin` action after transporting infectious patients."
* **Schema Evolution**:
  - Predicates: `(cabin-contaminated ?l - lift)`, `(cabin-sterile ?l - lift)`
  - Action: `sanitize-cabin(?l - lift ?f - floor)`

### Evolution 10.5: Emergency Governor Brake Testing
* **Prompt**:
  > "Extend the Miconic elevator domain with safety checks: elevators must perform an emergency brake test at the basement floor before morning rush-hour service commences."
* **Schema Evolution**:
  - Predicates: `(brakes-tested ?l - lift)`
  - Action: `test-emergency-brakes(?l - lift ?f - floor)`

### Evolution 10.6: Firefighter Emergency Recall Mode
* **Prompt**:
  > "Extend the Miconic elevator domain with fire safety operations: in emergency mode, the elevator must override all passenger calls and travel directly to the primary exit floor."
* **Schema Evolution**:
  - Predicates: `(fire-alarm-active)`, `(recalled-to-exit ?l - lift)`
  - Action: `fire-recall(?l - lift ?exit - floor)`

### Evolution 10.7: Off-Peak Power-Saving Floor Parking
* **Prompt**:
  > "Extend the Miconic elevator domain with eco-modes: when the cabin is empty, the elevator can park at a central lobby floor and enter low-power sleep mode."
* **Schema Evolution**:
  - Predicates: `(parked ?l - lift ?f - floor)`, `(eco-sleep ?l - lift)`
  - Action: `park-eco-mode(?l - lift ?f - floor)`

### Evolution 10.8: Heavy Freight Loading & Floor Lockout
* **Prompt**:
  > "Extend the Miconic elevator domain to support heavy industrial cargo carts: loading cargo carts locks out passenger boarding until the cart is safely unloaded."
* **Schema Evolution**:
  - Types: `freight_cart - object`
  - Predicates: `(freight-locked ?l - lift)`
  - Actions: `load-freight(?c ?l ?f)`, `unload-freight(?c ?l ?f)`

### Evolution 10.9: Door Obstruction Optical Sensor Cleaning
* **Prompt**:
  > "Extend the Miconic elevator domain so that elevator door photo-eye sensors can become blocked by dust, requiring a `clean-door-sensor` action before doors can close."
* **Schema Evolution**:
  - Predicates: `(sensor-blocked ?l - lift ?f - floor)`
  - Action: `clean-door-sensor(?l - lift ?f - floor)`

### Evolution 10.10: Emergency Generator Backup Switchover
* **Prompt**:
  > "Extend the Miconic elevator domain with power resilience: during electrical grid blackouts, the elevator must switch to backup diesel generator power before resuming vertical transit."
* **Schema Evolution**:
  - Predicates: `(grid-offline)`, `(generator-powered ?l - lift)`
  - Action: `engage-backup-generator(?l - lift)`

---

## 11. FreeCell

### Evolution 11.1: Card Quality Wear & Sleeving Maintenance
* **Prompt**:
  > "Extend the FreeCell domain with playing card preservation rules: rare collectible cards can experience edge wear after cascade moves, requiring a `sleeve-card` action to protect them while preserving backward compatibility with classical Solitaire problems."
* **Schema Evolution**:
  - Predicates: `(needs-maintenance ?c - card)`
  - Action: `(:action sleeve-card :parameters (?c - card) :precondition (needs-maintenance ?c) :effect (not (needs-maintenance ?c)))`

### Evolution 11.2: Wildcard Joker Transformation
* **Prompt**:
  > "Extend the FreeCell domain with a Wildcard Joker: the joker card can temporarily adopt any suit or rank using a `transform-joker` action to bridge broken cascade sequences."
* **Schema Evolution**:
  - Types: `joker - card`
  - Action: `transform-joker(?j - joker ?s - suit ?v - value)`

### Evolution 11.3: Foundation Irreversible Lock Mechanism
* **Prompt**:
  > "Extend the FreeCell domain with foundation security rules: once an Ace-through-King sequence is completed on a home foundation, the foundation stack can be permanently locked to secure tournament points."
* **Schema Evolution**:
  - Predicates: `(foundation-locked ?h - homecell)`
  - Action: `lock-foundation(?h - homecell)`

### Evolution 11.4: Premium Freecell Slot Expansion
* **Prompt**:
  > "Extend the FreeCell domain with reserve cells: players can spend energy tokens to unlock an auxiliary 5th freecell slot using an `unlock-reserve-cell` action during complex deadlocks."
* **Schema Evolution**:
  - Predicates: `(reserve-cell-unlocked ?c - freecell)`
  - Action: `unlock-reserve-cell(?c - freecell)`

### Evolution 11.5: Cascade Top Inspection for Hidden Cards
* **Prompt**:
  > "Extend the FreeCell domain to model face-down deck variations: face-down cards at the base of cascades must be flipped face-up with a `reveal-card` action once the covering card is cleared."
* **Schema Evolution**:
  - Predicates: `(face-down ?c - card)`, `(face-up ?c - card)`
  - Action: `reveal-card(?c - card ?under - card)`

### Evolution 11.6: Multi-Card Supermove Coordination
* **Prompt**:
  > "Extend the FreeCell domain with classical multi-card supermoves: allow moving an entire sequenced cascade block of length N to another cascade if sufficient freecells and empty columns are verified."
* **Schema Evolution**:
  - Action: `supermove-sequence(?top - card ?bottom - card ?from_col - col ?to_col - col ...)`

### Evolution 11.7: Card Table Felt Surface Dusting
* **Prompt**:
  > "Extend the FreeCell domain with clean-surface tournament rules: empty cascade columns must have their table felt dusted with a `brush-felt` action before a King can establish a new column."
* **Schema Evolution**:
  - Predicates: `(felt-dusted ?col - col)`
  - Action: `brush-felt(?col - col)`

### Evolution 11.8: Two-Deck Double FreeCell Support
* **Prompt**:
  > "Extend the FreeCell domain to support Double FreeCell with two full decks: cards are distinguished by deck indices, allowing identical rank/suit cards from opposite decks to coexist."
* **Schema Evolution**:
  - Types: `deck_id - object`
  - Predicates: `(deck-source ?c - card ?d - deck_id)`

### Evolution 11.9: Card Discard Pile with Recycle Ability
* **Prompt**:
  > "Extend the FreeCell domain with a side waste pile: unplayable cards can be temporarily moved to a discard pile and retrieved once per game using a `retrieve-discard` action."
* **Schema Evolution**:
  - Predicates: `(in-waste-pile ?c - card)`
  - Actions: `discard-card(?c)`, `retrieve-discard(?c)`

### Evolution 11.10: Suit Harmony Balance Constraint
* **Prompt**:
  > "Extend the FreeCell domain with color balance constraints: the four foundation piles must advance harmoniously such that no suit foundation can exceed any other suit foundation by more than two ranks."
* **Schema Evolution**:
  - Predicates: `(rank-ahead ?s1 - suit ?s2 - suit)`
  - Precondition checks in `sendtohome`.

---

## How to Use These Descriptions in Streamlit

1. Launch the application:
   ```bash
   streamlit run app.py
   ```
2. In the sidebar, select:
   - **Mode**: `🧬 Continuous Evolution (Evolve Saved Domain)`
   - **Choose Domain to Evolve**: Select any of the saved domains (e.g., `depot`, `barman`, `logistics`, `blocksworld`, etc.).
   - **Choose Baseline Domain Run**: Select the latest domain run (e.g., `domain_2.pddl`).
   - **Active Target Problem**: Select the corresponding problem file.
3. Copy any of the **Evolution Prompts** from this catalog into the **Evolution & Maintenance Requirements Prompt** box.
4. Click **🚀 Run Closed-Loop AST Agent**.
5. Observe the live execution stream:
   - **Node 1 [ELICIT]**: LLM analyzes requirements and extracts the updated AST schema.
   - **Node 2 [GENERATE]**: Python compiler produces syntactically valid PDDL.
   - **Node 3 [VALIDATE]**: VAL and Fast Downward verify syntax and goal reachability.
   - **Node 4 [MAINTENANCE]**: The historical regression suite verifies backward compatibility against legacy problem instances.
