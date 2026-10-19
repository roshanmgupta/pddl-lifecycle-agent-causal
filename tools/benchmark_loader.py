"""
Dynamic IPC Benchmark Loader for PDDLLifeCycleAgent.

Discovers and loads domains and problem instances directly from
pddl_benchmark_instances/ (IPC-1998, IPC-2000, etc.) without hardcoding.
"""

import os
import re
from typing import List, Dict, Any, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCHMARK_ROOT = os.path.join(PROJECT_ROOT, "pddl_benchmark_instances")

# Predefined Pure Natural Language Descriptions for classic IPC domains
# Formulated without explicit PDDL formalisms (no types/predicates/actions)
# to strictly evaluate the Elicitation Phase of the Lifecycle Agent.
IPC_NL_DESCRIPTIONS = {
    # Classic IPC Domains (IPC-1998, IPC-2000, IPC-2002)
    "gripper": (
        "A mobile warehouse robot operates across multiple rooms to transport physical items. "
        "The robot has two mechanical grippers, each capable of holding at most one ball at a time. "
        "The robot can navigate between connected rooms. To pick up a ball, the robot must be located "
        "in the same room as the ball and have an empty gripper. The robot can carry grasped balls "
        "while moving between rooms, and release balls into destination rooms to free up its grippers. "
        "The objective is to coordinate the robot's movement, grasping, and release operations to "
        "relocate all specified balls to their designated target rooms."
    ),
    "logistics": (
        "A supply-chain freight transportation network distributes parcels across multiple metropolitan cities. "
        "Each city contains multiple local delivery addresses and a central regional airport. "
        "Ground transit is handled by delivery vans, which can only drive between locations within their assigned city. "
        "Inter-city long-distance transit is handled by cargo airplanes, which fly between regional airports of different cities. "
        "Parcels begin at designated origin addresses and must be loaded, transported via road or air, unloaded, "
        "and delivered to their final destinations. The system must sequence vehicle movements and parcel transfers "
        "to fulfill all shipments without loss or routing conflicts."
    ),
    "movie": (
        "An automated home entertainment preparation system prepares snacks and equipment before playing a film. "
        "Before viewing, the system must retrieve a full selection of movie snacks, including popcorn, chips, dip, "
        "cheese, and crackers from the pantry. Additionally, the videotape player counter must be reset, and the physical "
        "tape must be rewound to the beginning before the movie can be played. The system must coordinate acquiring all "
        "refreshments and preparing the playback equipment to complete movie night setup."
    ),
    "assembly": (
        "An advanced manufacturing facility constructs complex physical assemblies out of individual mechanical "
        "sub-components and parts. Sub-components must be fitted together in specific hierarchical sequence, requiring "
        "temporary access to specialized assembly fixtures and tools. Certain components must be installed before others, "
        "while some transient alignment pins or brackets must be removed after installation to allow subsequent parts to fit. "
        "Tools and shared fixtures must be reserved before assembly and released back to the toolpool once the operation "
        "completes to avoid resource deadlocks. The system must schedule part fittings, tool commitments, and component "
        "removals to assemble the final product."
    ),
    "grid": (
        "A mobile exploration robot navigates a two-dimensional grid of interconnected rooms. Adjacent rooms are "
        "connected through doorways, some of which are locked with specialized mechanical locks. Scattered throughout "
        "the grid are keys of distinct shapes. The robot can move between unlocked adjacent rooms, pick up a key from "
        "the floor using its arm if free, use the matching key to unlock a locked door, and deposit keys or transported "
        "payload items in target goal rooms."
    ),
    "miconic": (
        "A passenger elevator operates in a multi-story building, traveling vertically between floors. "
        "Passengers arrive at designated origin floors and request transport to specific destination floors. "
        "The elevator cabin can move up or down between adjacent floors. When stopped at a floor, the elevator can open "
        "its doors to board waiting passengers who are currently at that floor. Once boarded, passengers remain inside "
        "the cabin as it moves, and alight when the cabin arrives at their desired destination floor. The system must "
        "sequence elevator movements, passenger boardings, and departures to serve all passengers efficiently."
    ),
    "blocksworld": (
        "A robotic manipulator works above a flat table surface containing solid cubic blocks. The robot arm has a single "
        "gripper that can grasp at most one block at a time from above. A block is clear if no other block rests on top of it. "
        "A block can rest directly on the table surface or stacked on top of another block. An empty gripper can pick up "
        "a clear block from the table or unstack a clear block from another block. A held block can be placed down onto the "
        "table or stacked onto another clear block. The objective is to rearrange the blocks from their initial configuration "
        "into a specified target vertical stacking arrangement."
    ),
    "blocks": (
        "A robotic manipulator works above a flat table surface containing solid cubic blocks. The robot arm has a single "
        "gripper that can grasp at most one block at a time from above. A block is clear if no other block rests on top of it. "
        "A block can rest directly on the table surface or stacked on top of another block. An empty gripper can pick up "
        "a clear block from the table or unstack a clear block from another block. A held block can be placed down onto the "
        "table or stacked onto another clear block. The objective is to rearrange the blocks from their initial configuration "
        "into a specified target vertical stacking arrangement."
    ),
    "depot": (
        "A freight logistics and warehousing domain combining transportation and block-like stacking mechanics. "
        "Trucks transport crates between different depots and distributor locations. At each location, hoists lift "
        "and drop crates on and off pallets or other crates, as well as loading and unloading them onto trucks. "
        "Crates can be stacked in vertical piles on top of pallets or other crates. "
        "The objective is to coordinate trucks and hoists to deliver and stack designated crates at their target locations."
    ),
    "depots": (
        "A freight logistics and warehousing domain combining transportation and block-like stacking mechanics. "
        "Trucks transport crates between different depots and distributor locations. At each location, hoists lift "
        "and drop crates on and off pallets or other crates, as well as loading and unloading them onto trucks. "
        "Crates can be stacked in vertical piles on top of pallets or other crates. "
        "The objective is to coordinate trucks and hoists to deliver and stack designated crates at their target locations."
    ),
    "satellite": (
        "An earth observation satellite constellation performs remote imaging missions. Each satellite has onboard "
        "scientific instruments (cameras, sensors) supporting different operational modes (infrared, spectrograph, etc.). "
        "Instruments must be powered on and calibrated by aiming at specific calibration targets before they can capture images. "
        "Satellites turn between directional targets, take images in specified modes, and consume power. "
        "The objective is to turn satellites, calibrate instruments, and acquire observation data for all requested targets."
    ),
    "rover": (
        "Autonomous planetary exploration rovers navigate across waypoints on Mars. Each rover carries specialized equipment: "
        "soil analysis tools, rock sampling tools, and cameras. Rovers must navigate between navigable waypoints, "
        "collect soil or rock samples, calibrate cameras, take panoramic or high-resolution images, and transmit "
        "scientific data back to an orbiting lander when line-of-sight communication is available."
    ),
    "rovers": (
        "Autonomous planetary exploration rovers navigate across waypoints on Mars. Each rover carries specialized equipment: "
        "soil analysis tools, rock sampling tools, and cameras. Rovers must navigate between navigable waypoints, "
        "collect soil or rock samples, calibrate cameras, take panoramic or high-resolution images, and transmit "
        "scientific data back to an orbiting lander when line-of-sight communication is available."
    ),
    "zenotravel": (
        "Air passenger transit network across multiple cities. Aircraft fly between cities transporting passengers. "
        "Aircraft consume discrete fuel levels and can fly at normal speed or zoom at supersonic speed. "
        "Passengers board and debark aircraft at city airports, and aircraft can refuel to increase fuel levels. "
        "The goal is to transport all passengers to their target cities while managing aircraft fuel levels."
    ),
    "driverlog": (
        "A transportation logistics network where delivery trucks must be driven by licensed human drivers. "
        "Drivers walk between path-connected locations or board trucks to drive them along road networks between locations. "
        "Trucks are used to load, transport, and unload packages between warehouse docks and delivery addresses. "
        "The objective is to coordinate driver walking, truck boarding, and package transport to fulfill deliveries."
    ),
    "driver-log": (
        "A transportation logistics network where delivery trucks must be driven by licensed human drivers. "
        "Drivers walk between path-connected locations or board trucks to drive them along road networks between locations. "
        "Trucks are used to load, transport, and unload packages between warehouse docks and delivery addresses. "
        "The objective is to coordinate driver walking, truck boarding, and package transport to fulfill deliveries."
    ),
    "mystery": (
        "A resource-constrained logistics routing network transports discrete cargo items between locations while "
        "constrained by local fuel capacities and vehicle capacities. Moving between locations consumes finite fuel "
        "resources, and locations can exchange or balance fuel under strict conservation constraints. The system must "
        "deliver goods to their target destinations while strictly respecting local payload capacities and energy balances."
    ),
    "freecell": (
        "A card solitaire planning domain modeled after Freecell. Cards have values (ranks) and suits. Values follow "
        "a successor order from Ace up to King. Columns have stacks of cards where each card rests on another card or directly "
        "on an empty column space. Only the clear top card of a column can be moved. A card can be moved onto another card "
        "in a column only if its value is the immediate predecessor and their suits have alternating colors. Cards can be "
        "moved to home foundation cells only in ascending value order for the same suit, starting from Ace. A card can be "
        "placed in an empty freecell if a freecell is available, and later moved back to a column or to a foundation. "
        "When a card is removed from a column, the card underneath becomes clear, or the column becomes empty. "
        "The objective is to move all target cards from initial columns into their respective foundation home cells."
    ),
    "thoughtful": (
        "A card solitaire planning domain modeled after Freecell. Cards have values (ranks) and suits. Values follow "
        "a successor order from Ace up to King. Columns have stacks of cards where each card rests on another card or directly "
        "on an empty column space. Only the clear top card of a column can be moved. A card can be moved onto another card "
        "in a column only if its value is the immediate predecessor and their suits have alternating colors. Cards can be "
        "moved to home foundation cells only in ascending value order for the same suit, starting from Ace. A card can be "
        "placed in an empty freecell if a freecell is available, and later moved back to a column or to a foundation. "
        "When a card is removed from a column, the card underneath becomes clear, or the column becomes empty. "
        "The objective is to move all target cards from initial columns into their respective foundation home cells."
    ),
    "schedule": (
        "A factory job-shop scheduling and metalworking domain. Workpieces of varying metal types and shapes must be "
        "manufactured to specific dimensions, surface finishes, and hole drillings. The workshop contains machine tools: "
        "lathes, shapers, polishers, grinders, drill presses, and paint sprayers. Workpieces must be scheduled on appropriate "
        "machine tools, machined to target tolerances, smoothed, polished, and painted with designated colors while "
        "avoiding machine tool scheduling conflicts."
    ),
    "translog": (
        "A comprehensive multi-modal freight logistics and transport network. Freight cargo consisting of general merchandise, "
        "liquids, hazardous chemicals, and bulk materials must be transported across regional transit networks. The system "
        "features a fleet of specialized transport vehicles: flatbed trucks, tanker trucks, boxcars, hopper cars, and cargo "
        "aircraft. Cargo is loaded at manufacturing sites, transported via roads, railways, and air corridors between distribution "
        "centers, freight train depots, and airports, and unloaded or transferred between vehicle types to fulfill delivery orders."
    ),
    "umtranslog": (
        "A comprehensive multi-modal freight logistics and transport network. Freight cargo consisting of general merchandise, "
        "liquids, hazardous chemicals, and bulk materials must be transported across regional transit networks. The system "
        "features a fleet of specialized transport vehicles: flatbed trucks, tanker trucks, boxcars, hopper cars, and cargo "
        "aircraft. Cargo is loaded at manufacturing sites, transported via roads, railways, and air corridors between distribution "
        "centers, freight train depots, and airports, and unloaded or transferred between vehicle types to fulfill delivery orders."
    ),

    # IPC-2004 Domains
    "airport": (
        "An airport ground traffic management system coordinates airplane movements on the surface taxiway and runway network. "
        "Airplanes move between parking gates, designated taxiway segments, and active runways. Airplanes can push back from "
        "gates, taxi forward along connected segments, hold at intersections, enter runways to take off, or land from inbound "
        "flights and vacate the runway onto taxiways. Each runway and taxi segment has limited physical capacity and safety "
        "clearance zones to prevent wingtip collisions and runway incursions. Airplanes must navigate their assigned taxi paths, "
        "enter runway slots according to air traffic control clearance, and either depart or reach designated parking gates "
        "without blocking or colliding with other aircraft."
    ),
    "pipesworld": (
        "A petroleum logistics and pipeline transportation network moves liquid petroleum products (such as crude oil, "
        "gasoline, and diesel) between refinery areas and storage distribution terminals. The areas are connected by pipeline "
        "segments. Each pipeline segment has a fixed capacity and is always filled with contiguous batches of liquid products. "
        "When a batch of a product is pumped into one end of a pipeline segment from an area, it simultaneously pushes and "
        "displaces the batch at the other end into the receiving area. Batches must not mix in an incompatible manner at the "
        "interface between liquids. At distribution terminals, tankage tanks hold batches subject to volume storage limits. "
        "The goal is to sequence pumping and displacement operations across the pipeline network to deliver all specified "
        "product batches to their destination terminal areas."
    ),
    "promela-dining-philosophers": (
        "A concurrent process synchronization system models Dijkstra's classic Dining Philosophers mutual-exclusion protocol. "
        "Philosophers sit around a circular table with a shared fork placed between each adjacent pair. Each philosopher "
        "alternates between thinking and eating. To eat, a philosopher must acquire both their immediate left and right forks. "
        "Once both forks are held, the philosopher eats for a period and then releases both forks back to the table for neighbors "
        "to use. The system must coordinate philosopher state transitions and resource requests to ensure all philosophers get "
        "to eat while avoiding circular wait deadlocks and starvation."
    ),
    "philosophers": (
        "A concurrent process synchronization system models Dijkstra's classic Dining Philosophers mutual-exclusion protocol. "
        "Philosophers sit around a circular table with a shared fork placed between each adjacent pair. Each philosopher "
        "alternates between thinking and eating. To eat, a philosopher must acquire both their immediate left and right forks. "
        "Once both forks are held, the philosopher eats for a period and then releases both forks back to the table for neighbors "
        "to use. The system must coordinate philosopher state transitions and resource requests to ensure all philosophers get "
        "to eat while avoiding circular wait deadlocks and starvation."
    ),
    "promela-optical-telegraph": (
        "A telecommunication protocol verification model represents an optical telegraph message-passing network. Multiple "
        "station nodes arranged in a network topology communicate by signaling through shared channels, flag registers, "
        "and local transmission buffers. Stations coordinate read, write, handshake, and acknowledgment actions to pass "
        "message packets along the network without message loss, buffer overflow, or channel contention. The objective is to "
        "verify protocol liveness and successfully transmit all communication packets to their destination stations."
    ),
    "optical-telegraph": (
        "A telecommunication protocol verification model represents an optical telegraph message-passing network. Multiple "
        "station nodes arranged in a network topology communicate by signaling through shared channels, flag registers, "
        "and local transmission buffers. Stations coordinate read, write, handshake, and acknowledgment actions to pass "
        "message packets along the network without message loss, buffer overflow, or channel contention. The objective is to "
        "verify protocol liveness and successfully transmit all communication packets to their destination stations."
    ),
    "psr": (
        "An electrical power distribution network consists of power generation stations, electrical buses, circuit breakers, "
        "sectionalizing switches, and customer load lines. When an electrical fault or short-circuit occurs on a line segment, "
        "protection breakers automatically trip to de-energize the faulty line, leaving customer downstream areas without "
        "electricity. An automated grid restoration controller must operate available switches and breakers: opening switches "
        "to isolate faulty line sections and closing tie switches to route alternative power flows from operational substations "
        "to unpowered customer loads. Operations must strictly avoid feeding power into short circuits or overloading electrical "
        "lines, with the objective of restoring power to all eligible customer supply nodes."
    ),
    "settlers": (
        "An economic infrastructure and resource production settlement simulates resource harvesting, logistics, and "
        "construction. Workers, carts, trains, and cargo ships operate across regions connected by roads, rail lines, and sea "
        "routes. Primary resources including timber, stone, coal, and iron ore are gathered from natural deposits. Resource "
        "processors refine timber into wood planks, burn coal to smelt iron ore into iron, and construct specialized production "
        "facilities (cabins, quarries, mines, sawmills, and smelters). Transport vehicles haul materials between settlements "
        "and construction sites. The objective is to manage the economic supply chain, produce necessary materials, and erect "
        "all requested infrastructure and settlements."
    ),
    "umts": (
        "A Universal Mobile Telecommunications System (UMTS) radio access protocol manages mobile station connections to network "
        "controllers. Mobile user equipment entities request, establish, reconfigure, and release radio access bearers and "
        "communication channels with base station agents. Operations include allocating radio frequency and quality-of-service "
        "parameters, verifying transmission resource management, executing handovers, and negotiating protocol states between "
        "mobile handsets and network controllers. The objective is to coordinate telecommunication signaling sequences and "
        "state machine transitions to successfully establish and maintain requested application connections."
    ),

    # IPC-2006 Domains
    "openstacks": (
        "A production scheduling and warehouse staging facility processes custom customer orders. Each order requires a specific "
        "combination of manufactured products. The facility uses a single production machine that can make products one by one, "
        "requiring machine setup changes between different product types. An order is considered open once the first product "
        "belonging to that order begins manufacturing, and it occupies a physical stacking space until all of its required "
        "products are finished and the order is shipped. Because the warehouse floor has limited capacity for open stacks, "
        "products and order deliveries must be scheduled to satisfy all customer orders while never exceeding the maximum "
        "allowed number of simultaneously open stacks."
    ),
    "pathways": (
        "A biological molecular pathway and intracellular signal transduction network models metabolic reactions and gene "
        "regulation. Biochemical species (proteins, enzymes, transcription factors, and small molecules) undergo complex "
        "molecular interactions: association to form multi-protein complexes, phosphorylation and dephosphorylation reactions, "
        "enzymatic catalyzed synthesis, and receptor binding. Molecular reactions are triggered only when all required reactant "
        "substrates and active co-factors are present, creating downstream reaction cascades. The goal is to coordinate available "
        "biochemical reactions and catalytic steps to synthesize target molecular compounds and activate specific metabolic pathways."
    ),
    "storage": (
        "An automated storage depot logistics domain models freight movement within an indoor warehouse facility. Forklift "
        "hoists navigate across interconnected floor spaces, transit areas, depot bays, and storage containers. Forklifts have "
        "mechanical arms capable of lifting and carrying heavy freight crates one at a time. Transit corridors and storage "
        "bays have spatial clearance and topological connectivity, meaning a forklift cannot move through spaces obstructed "
        "by other hoists or crates. Hoists must enter loading bays, lift crates, maneuver through open transit aisles, and drop "
        "crates into designated storage locations to organize warehouse inventory."
    ),
    "tpp": (
        "A supply chain purchasing and transport network coordinates procurement across regional commodity markets. Delivery "
        "trucks travel along a road network connecting a central distribution depot to multiple market locations. Each market "
        "offers specific goods and commodities in available supply quantities. Trucks drive to markets, purchase desired "
        "quantities of goods, load the purchased items into cargo compartments, and transport them back to the central depot "
        "to be unloaded. The objective is to route trucks, execute market purchases, and deliver all requested amounts of goods "
        "to the central depot."
    ),
    "trucks": (
        "A scheduled freight parcel delivery logistics network utilizes cargo trucks with discrete loading areas. Trucks "
        "travel between geographic locations across a road network to deliver customer packages. Each truck's cargo bed is "
        "divided into distinct capacity areas (such as front and rear compartments) that must be loaded and unloaded in specific "
        "order without blocking access. Shipments have strict delivery deadlines or transit time windows. Trucks must load "
        "packages, navigate routes between locations, unload shipments at destination sites, and deliver all packages within "
        "their permitted operational windows."
    ),

    # IPC-2008 Domains
    "crew-planning": (
        "A crew schedule and mission task planner coordinates daily activities for astronauts aboard a space station. Crew "
        "members follow strict daily circadian schedules partitioned into operational shifts and rest days. Astronauts must "
        "perform payload scientific experiments, change environmental filters, conduct medical self-checks, and communicate "
        "with ground control, while also completing mandatory daily exercise on specialized workout equipment, eating meals, "
        "and observing mandatory sleep cycles. The system must sequence daily crew tasks, respect resource and equipment "
        "availability, and ensure all mission payloads and maintenance duties are completed without violating human endurance "
        "or rest rules."
    ),
    "crewplanning": (
        "A crew schedule and mission task planner coordinates daily activities for astronauts aboard a space station. Crew "
        "members follow strict daily circadian schedules partitioned into operational shifts and rest days. Astronauts must "
        "perform payload scientific experiments, change environmental filters, conduct medical self-checks, and communicate "
        "with ground control, while also completing mandatory daily exercise on specialized workout equipment, eating meals, "
        "and observing mandatory sleep cycles. The system must sequence daily crew tasks, respect resource and equipment "
        "availability, and ensure all mission payloads and maintenance duties are completed without violating human endurance "
        "or rest rules."
    ),
    "cyber-security": (
        "A cyber defense and network security penetration-testing domain models computer network vulnerabilities and attack graphs. "
        "A security assessment agent navigates an enterprise network comprising multiple subnets, firewalls, and host computers "
        "running various operating systems and services. By scanning hosts, discovering open network ports, identifying software "
        "vulnerabilities, deploying exploits, capturing authorization credentials, and escalating administrative privileges, "
        "the agent pivots across compromised machines to gain authorized access to target hosts and inspect sensitive network services."
    ),
    "cybersecurity": (
        "A cyber defense and network security penetration-testing domain models computer network vulnerabilities and attack graphs. "
        "A security assessment agent navigates an enterprise network comprising multiple subnets, firewalls, and host computers "
        "running various operating systems and services. By scanning hosts, discovering open network ports, identifying software "
        "vulnerabilities, deploying exploits, capturing authorization credentials, and escalating administrative privileges, "
        "the agent pivots across compromised machines to gain authorized access to target hosts and inspect sensitive network services."
    ),
    "elevator": (
        "A high-rise building vertical transit system dispatches multiple passenger elevators across building floors. The building "
        "features different elevator classes: slow local elevators that serve every consecutive floor within local zones, and "
        "fast express elevators that travel between designated hub floors at high speed. Passengers arrive at origin floors and "
        "request transportation to destination floors. Elevators travel vertically, open doors to board waiting passengers, "
        "transport them across floors, and disembark them at destination floors or intermediate transfer hub floors. The objective "
        "is to coordinate elevator travel and passenger transfers to deliver all passengers to their destination floors."
    ),
    "elevators": (
        "A high-rise building vertical transit system dispatches multiple passenger elevators across building floors. The building "
        "features different elevator classes: slow local elevators that serve every consecutive floor within local zones, and "
        "fast express elevators that travel between designated hub floors at high speed. Passengers arrive at origin floors and "
        "request transportation to destination floors. Elevators travel vertically, open doors to board waiting passengers, "
        "transport them across floors, and disembark them at destination floors or intermediate transfer hub floors. The objective "
        "is to coordinate elevator travel and passenger transfers to deliver all passengers to their destination floors."
    ),
    "model-train": (
        "A model railway dispatching network controls miniature trains traveling across an interconnected rail track layout. "
        "The railway consists of track segments, turnouts, passing sidings, and controllable track switches. Trains navigate "
        "the tracks between origin stations and destination platforms. Switches must be thrown and aligned before trains enter "
        "junctions, and trains must obey block occupancy rules so that no two trains ever occupy the same track block simultaneously. "
        "The objective is to route all trains to their destination tracks without track derailments, collisions, or signal deadlocks."
    ),
    "parc-printer": (
        "A high-throughput modular digital printing system manages paper sheets moving through a multi-engine printing press. "
        "Sheets of paper feed from input paper trays, traverse transport tracks, pass through monochrome and color print markers, "
        "and exit into finishing output trays. The paper path includes inverter tracks that flip sheets upside-down to allow "
        "double-sided (duplex) printing. Sheet movements must be synchronized down to discrete time intervals so that consecutive "
        "sheets do not collide on tracks or at printheads. The system must route, invert, print, and deposit every sheet to "
        "complete customer print jobs in proper collation order."
    ),
    "parcprinter": (
        "A high-throughput modular digital printing system manages paper sheets moving through a multi-engine printing press. "
        "Sheets of paper feed from input paper trays, traverse transport tracks, pass through monochrome and color print markers, "
        "and exit into finishing output trays. The paper path includes inverter tracks that flip sheets upside-down to allow "
        "double-sided (duplex) printing. Sheet movements must be synchronized down to discrete time intervals so that consecutive "
        "sheets do not collide on tracks or at printheads. The system must route, invert, print, and deposit every sheet to "
        "complete customer print jobs in proper collation order."
    ),
    "peg-solitaire": (
        "The classic peg solitaire puzzle is played on a board with an array of holes, initially filled with pegs except for "
        "designated empty holes. A valid move consists of a peg jumping orthogonally (horizontally or vertically) over an "
        "immediately adjacent peg into an empty hole located directly beyond it. The jumped peg is permanently removed from the "
        "board. Jumps can be chained or executed individually. The objective is to sequence peg jumps to remove pegs until only "
        "a single peg remains on the board at a designated target hole position."
    ),
    "pegsol": (
        "The classic peg solitaire puzzle is played on a board with an array of holes, initially filled with pegs except for "
        "designated empty holes. A valid move consists of a peg jumping orthogonally (horizontally or vertically) over an "
        "immediately adjacent peg into an empty hole located directly beyond it. The jumped peg is permanently removed from the "
        "board. Jumps can be chained or executed individually. The objective is to sequence peg jumps to remove pegs until only "
        "a single peg remains on the board at a designated target hole position."
    ),
    "scanalyzer-3d": (
        "An automated agricultural plant phenotyping and conveyor scanning facility monitors plant growth in a high-throughput "
        "greenhouse. Potted plants rest on transport cars that move along closed-loop conveyor tracks and carousel segments. "
        "The facility includes 3D imaging and scanning chambers that capture multispectral morphological data as plants pass "
        "through. Conveyor tracks can rotate car positions in 2-car and 4-car cycles. The system must coordinate conveyor "
        "rotations and scan chamber activations to process, image, and return all designated plant batches to storage without stalls."
    ),
    "scanalyzer": (
        "An automated agricultural plant phenotyping and conveyor scanning facility monitors plant growth in a high-throughput "
        "greenhouse. Potted plants rest on transport cars that move along closed-loop conveyor tracks and carousel segments. "
        "The facility includes 3D imaging and scanning chambers that capture multispectral morphological data as plants pass "
        "through. Conveyor tracks can rotate car positions in 2-car and 4-car cycles. The system must coordinate conveyor "
        "rotations and scan chamber activations to process, image, and return all designated plant batches to storage without stalls."
    ),
    "sokoban": (
        "A classic grid warehouse box-pushing puzzle. A warehouse keeper moves around a maze-like grid of floor tiles bordered "
        "by impassable walls. Scattered across the floor are heavy storage boxes. The keeper can walk to adjacent empty floor "
        "squares and push a box forward into an immediately adjacent empty square (boxes can only be pushed, never pulled, and "
        "two boxes cannot be pushed together). If a box is pushed against a wall or into a corner, it may become permanently "
        "immobilized. The objective is to maneuver the keeper to push every box onto a designated goal square."
    ),
    "transport": (
        "A vehicle routing and freight parcel delivery domain with explicit vehicle payload capacities. Cargo delivery trucks "
        "navigate a network of road segments connecting city locations. Each truck has a finite maximum cargo capacity, "
        "representing the maximum number of packages it can carry simultaneously. Trucks pick up packages from locations "
        "(if the truck has remaining capacity), transport them along roads, and drop packages at destination addresses. "
        "The objective is to plan vehicle routes, pickups, and drop-offs to deliver all shipments to their destinations while "
        "never exceeding vehicle payload limits."
    ),
    "woodworking": (
        "An automated woodworking workshop manufactures finished wooden components from raw timber. Timber pieces possess "
        "attributes including size, wood species (e.g., pine, oak, mahogany), surface finish, and color. The workshop contains "
        "specialized processing machinery: high-speed saws to cut boards into smaller parts, planers and grinders to smooth "
        "surfaces, and immersion varnishing booths, sprayers, and glazers to apply desired surface treatments and colors. "
        "Workpieces must be loaded into machines, processed through cutting, smoothing, and coating stages, and unloaded to "
        "produce finished wood parts meeting exact size, finish, and color specifications."
    ),

    # IPC-2011 Domains
    "barman": (
        "A robotic bartender operates behind a cocktail bar preparing mixed drinks and cocktails. The robot bartender has two "
        "hands that can hold shakers, shot glasses, or bottles. The bar contains ingredient dispensers, cocktail shakers, shot "
        "glasses of fixed capacity, and a cleaning sink. Making a cocktail requires pouring an ingredient into a clean shot glass, "
        "emptying or pouring the shot into a shaker, repeating for additional ingredients, shaking the shaker to blend the cocktail, "
        "and pouring the mixed beverage into a target cocktail glass. Used shot glasses and shakers become dirty and must be "
        "rinsed and cleaned before preparing different recipes. The robot must coordinate grasping, pouring, shaking, and "
        "cleaning to serve all requested cocktails."
    ),
    "floor-tile": (
        "An autonomous mobile robotic painting system paints decorative tile patterns on floors. Robots equipped with spray "
        "paint arms navigate a two-dimensional grid of floor tiles. Tiles must be painted in alternating black and white color "
        "patterns. A robot can move between adjacent tiles only if the destination tile is currently unpainted; a robot can "
        "never step onto a painted tile because it would damage the wet finish. A robot can paint a tile located immediately "
        "above or below its current position. Robots can also visit paint stations to switch paint applicator colors between "
        "black and white. The objective is to coordinate robot navigation, color changes, and tile painting to paint all designated "
        "tiles with their specified colors without trapping any robot."
    ),
    "floortile": (
        "An autonomous mobile robotic painting system paints decorative tile patterns on floors. Robots equipped with spray "
        "paint arms navigate a two-dimensional grid of floor tiles. Tiles must be painted in alternating black and white color "
        "patterns. A robot can move between adjacent tiles only if the destination tile is currently unpainted; a robot can "
        "never step onto a painted tile because it would damage the wet finish. A robot can paint a tile located immediately "
        "above or below its current position. Robots can also visit paint stations to switch paint applicator colors between "
        "black and white. The objective is to coordinate robot navigation, color changes, and tile painting to paint all designated "
        "tiles with their specified colors without trapping any robot."
    ),
    "match-cellar": (
        "A maintenance technician navigates a pitch-black cellar to repair damaged electrical fuses. The technician has a box "
        "of matches. Because the cellar is completely dark, the technician can only navigate between rooms or inspect and mend "
        "fuses while holding a burning match. Lighting a match consumes one match, and each match burns for a limited duration "
        "before extinguishing. The technician must coordinate lighting matches, moving between cellar locations, and mending "
        "all broken fuses before running out of matches or being stranded in the dark."
    ),
    "no-mystery": (
        "A resource-constrained parcel delivery logistics network where vehicle fuel is non-renewable. Delivery trucks "
        "transport cargo packages across a network of locations connected by road routes. Each road connection consumes a "
        "specific quantity of fuel when traversed. Unlike standard transportation domains, there are no refueling stations: "
        "trucks start with a fixed initial fuel level that cannot be replenished. Picking up and dropping off packages does not "
        "consume fuel, but every driving move permanently depletes fuel. The objective is to load, transport, and deliver all "
        "packages to their target destinations while strictly ensuring that no truck ever runs out of fuel along its route."
    ),
    "nomystery": (
        "A resource-constrained parcel delivery logistics network where vehicle fuel is non-renewable. Delivery trucks "
        "transport cargo packages across a network of locations connected by road routes. Each road connection consumes a "
        "specific quantity of fuel when traversed. Unlike standard transportation domains, there are no refueling stations: "
        "trucks start with a fixed initial fuel level that cannot be replenished. Picking up and dropping off packages does not "
        "consume fuel, but every driving move permanently depletes fuel. The objective is to load, transport, and deliver all "
        "packages to their target destinations while strictly ensuring that no truck ever runs out of fuel along its route."
    ),
    "parking": (
        "A valet parking lot car repositioning puzzle models traffic management in a congested parking lot. The parking lot "
        "is arranged in curb spaces where cars park bumper-to-bumper. Each curb slot can hold up to two cars: one car parked "
        "directly against the curb, and a second car parked directly behind it. A car parked behind blocks the front car from "
        "exiting until the rear car is moved. Cars can be driven from a curb slot to another empty curb slot, from behind "
        "another car to an empty curb slot, or behind another car if space permits. The objective is to maneuver and rearrange "
        "vehicles so that every car ends up parked in its designated assigned target stall."
    ),
    "temporal-machine-shop": (
        "An industrial high-precision machine shop manufactures heat-treated ceramic and metal components. Raw workpieces "
        "must be baked and annealed in high-temperature industrial kilns. Kilns have distinct thermal capacities and require "
        "pre-heating to operating temperatures and controlled cool-down cycles. Baking operations require dedicated heat-resistant "
        "tools and consumable energy. The shop must schedule furnace operations, load and unload workpieces, and regulate "
        "baking cycles to manufacture all workpieces to quality standards without thermal degradation or equipment conflicts."
    ),
    "tidybot": (
        "An autonomous domestic service robot cleans up cluttered household living spaces. The robot is equipped with a mobile "
        "base, an articulated manipulator arm, and a multi-compartment cart. Misplaced household items (such as books, toys, "
        "cups, and clothing) are scattered on floors and tables across rooms. The robot navigates between rooms, grasps misplaced "
        "objects, deposits them into its mobile cart, pushes or carries the cart to designated storage fixtures (shelves, "
        "laundry baskets, cupboards, and bins), and unloads each item into its correct target storage location to tidy the home."
    ),
    "turn-and-open": (
        "A mobile indoor service robot navigates across rooms separated by closed and latched doors. The robot has two "
        "mechanical grippers used for manipulating objects and operating door hardware. To traverse between rooms, the robot "
        "must approach a closed door, grasp the door handle or knob with an empty gripper, rotate the latch mechanism to "
        "disengage the lock, pull or push the door open, release the handle, and navigate through the open doorway. The robot "
        "can also pick up, carry, and deliver payload objects between rooms once access doorways are opened."
    ),
    "visit-all": (
        "An autonomous exploration rover surveys an environment modeled as an interconnected grid or graph of topological places. "
        "The rover begins at an initial location and can move along connected pathways to adjacent locations (north, south, east, west). "
        "The environment contains designated inspection waypoints that must be surveyed. The goal is to plan an efficient "
        "traversal path for the rover that visits every specified waypoint at least once."
    ),
    "visitall": (
        "An autonomous exploration rover surveys an environment modeled as an interconnected grid or graph of topological places. "
        "The rover begins at an initial location and can move along connected pathways to adjacent locations (north, south, east, west). "
        "The environment contains designated inspection waypoints that must be surveyed. The goal is to plan an efficient "
        "traversal path for the rover that visits every specified waypoint at least once."
    ),

    # IPC-2014 Domains
    "cave-diving": (
        "An underwater cave exploration and survey mission coordinates divers exploring submerged tunnel networks. Divers "
        "navigate through flooded cave passages consisting of submerged chambers and narrow bottlenecks. Breathing air is "
        "provided by scuba diving tanks of limited capacity. Divers can swim between connected underwater cavern locations, "
        "carry air tanks, deposit spare tanks at intermediate waypoints for return journeys, retrieve cached tanks, take "
        "scientific photographs of cave features, and navigate back to the surface decompression habitat before exhausting "
        "their breathing gas supply."
    ),
    "cavediving": (
        "An underwater cave exploration and survey mission coordinates divers exploring submerged tunnel networks. Divers "
        "navigate through flooded cave passages consisting of submerged chambers and narrow bottlenecks. Breathing air is "
        "provided by scuba diving tanks of limited capacity. Divers can swim between connected underwater cavern locations, "
        "carry air tanks, deposit spare tanks at intermediate waypoints for return journeys, retrieve cached tanks, take "
        "scientific photographs of cave features, and navigate back to the surface decompression habitat before exhausting "
        "their breathing gas supply."
    ),
    "child-snack": (
        "A school cafeteria sandwich preparation and meal distribution system caters to children, including those with gluten "
        "allergies. Kitchen staff prepare sandwiches on trays using bread and sandwich contents (e.g., cheese, spreads). "
        "Sandwiches made with gluten-free bread must be strictly reserved for allergic children to prevent allergic reactions, "
        "while non-allergic children can eat any sandwich. Trays loaded with prepared sandwiches are carried from the kitchen "
        "to dining tables, where sandwiches are served to seated children. The objective is to prepare and serve appropriate "
        "sandwiches so that every child receives lunch and all dietary safety requirements are met."
    ),
    "childsnack": (
        "A school cafeteria sandwich preparation and meal distribution system caters to children, including those with gluten "
        "allergies. Kitchen staff prepare sandwiches on trays using bread and sandwich contents (e.g., cheese, spreads). "
        "Sandwiches made with gluten-free bread must be strictly reserved for allergic children to prevent allergic reactions, "
        "while non-allergic children can eat any sandwich. Trays loaded with prepared sandwiches are carried from the kitchen "
        "to dining tables, where sandwiches are served to seated children. The objective is to prepare and serve appropriate "
        "sandwiches so that every child receives lunch and all dietary safety requirements are met."
    ),
    "city-car": (
        "An urban municipal traffic management system directs vehicles through a dynamic street grid. Cars start at parking "
        "garages and must navigate through intersections to destination drop-off points. Traffic controllers can dynamically "
        "build straight and diagonal one-way road segments between adjacent intersections, as well as clear or dismantle "
        "road links to reconfigure traffic flows. Roads have finite traffic capacities to prevent congestion. The system must "
        "construct road pathways and route cars safely to their destination intersections without gridlock."
    ),
    "citycar": (
        "An urban municipal traffic management system directs vehicles through a dynamic street grid. Cars start at parking "
        "garages and must navigate through intersections to destination drop-off points. Traffic controllers can dynamically "
        "build straight and diagonal one-way road segments between adjacent intersections, as well as clear or dismantle "
        "road links to reconfigure traffic flows. Roads have finite traffic capacities to prevent congestion. The system must "
        "construct road pathways and route cars safely to their destination intersections without gridlock."
    ),
    "genome-edit-distances": (
        "A computational biology and comparative genomics domain models the evolutionary transformation between genetic "
        "sequences. Given an initial chromosome or genome represented as an ordered sequence of genes, the system applies "
        "biological rearrangement operations: cutting chromosome fragments, inverting gene segments, transposing sequences "
        "to new locations, and splicing fragments back together. The objective is to sequence minimum-distance genetic "
        "rearrangements to transform the source chromosome into a target gene order."
    ),
    "ged": (
        "A computational biology and comparative genomics domain models the evolutionary transformation between genetic "
        "sequences. Given an initial chromosome or genome represented as an ordered sequence of genes, the system applies "
        "biological rearrangement operations: cutting chromosome fragments, inverting gene segments, transposing sequences "
        "to new locations, and splicing fragments back together. The objective is to sequence minimum-distance genetic "
        "rearrangements to transform the source chromosome into a target gene order."
    ),
    "hiking": (
        "A hiking expedition plans a long-distance trekking journey along a mountain trail for outdoor hiking partners. "
        "Hikers walk along scenic trail segments connecting campsites and trailheads. To rest safely overnight at a destination "
        "campsite, a tent must be pitched and ready. Hikers can pack tents, load them into off-road support vehicles, drive "
        "vehicles between accessible trailheads, unpack and pitch tents at arrival campsites, and walk together along hiking "
        "trails from origin campsites to destination summits."
    ),
    "maintenance": (
        "A commercial airline fleet maintenance planning system schedules mandatory technical inspections for passenger aircraft. "
        "Over a multi-day planning horizon, airplanes fly scheduled routes between commercial airport hubs. Each airplane must "
        "undergo a comprehensive maintenance check at an airport equipped with inspection facilities before completing its "
        "scheduled flight duty. Maintenance hangars have daily service capacities limiting how many aircraft can be serviced "
        "simultaneously. The objective is to assign aircraft to maintenance hangars on available days so that all fleet aircraft "
        "receive required inspections."
    ),
    "map-analyzer": (
        "An aerial cartography and automated geographic map analysis domain. Observation vehicles and mapping sensors navigate "
        "an urban or regional grid of topological junctions. The system coordinates vehicle movements along connected road "
        "networks, deploys imaging and radar sensors to scan terrain sectors, captures aerial imagery, and analyzes map features "
        "across designated geographic survey coordinates."
    ),
    "road-traffic-accident-management": (
        "An emergency response coordination system manages vehicular accidents on public highway networks. When collisions "
        "occur, emergency services dispatch specialized response vehicles: police cruisers to secure the perimeter, fire engines "
        "to extinguish blazes, ambulances to treat and transport injured victims to hospitals, and tow trucks to remove damaged "
        "vehicles to repair garages. Responders navigate the road network, administer medical care, clear wreckage, and reopen "
        "blocked roadway segments to restore traffic circulation."
    ),
    "tetris": (
        "A geometric grid placement puzzle based on Tetris shapes. Polyomino pieces of various geometric configurations "
        "(such as square blocks, straight lines, and L-shaped tetrominoes) are manipulated across a two-dimensional grid of "
        "position squares. Pieces can be shifted and rotated into open grid positions without overlapping already occupied "
        "squares or colliding with grid boundaries. The objective is to maneuver and place pieces onto the board to achieve "
        "designated geometric patterns or target tile coverages."
    ),
}

def list_ipc_years() -> List[str]:
    """
    Returns available IPC benchmark directories that adhere strictly to PDDL 2.1 typed semantics.
    """
    if not os.path.exists(BENCHMARK_ROOT):
        return []
    years = [
        d for d in os.listdir(BENCHMARK_ROOT)
        if d.startswith("ipc-") and d not in ["ipc-1998", "ipc-2000"] and os.path.isdir(os.path.join(BENCHMARK_ROOT, d))
    ]
    years.sort()
    return years

def is_domain_typed(year: str, domain_name: str) -> bool:
    """Verifies that a domain specifies ':typing' requirement adhering to PDDL 2.1 typed semantics."""
    dom_path = os.path.join(BENCHMARK_ROOT, year, "domains", domain_name, "domain.pddl")
    if os.path.exists(dom_path):
        try:
            with open(dom_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().lower()
                return ":typing" in content
        except Exception:
            return False
    return False

def list_ipc_domains(year: str = "ipc-2002") -> List[str]:
    """
    Returns strictly PDDL 2.1 typed domain subdirectories within a given IPC year.
    Filters out legacy untyped domains (e.g. *-untyped or domains without :typing).
    """
    domains_dir = os.path.join(BENCHMARK_ROOT, year, "domains")
    if not os.path.exists(domains_dir):
        return []
    doms = [
        d for d in os.listdir(domains_dir)
        if os.path.isdir(os.path.join(domains_dir, d))
        and not d.endswith("-untyped")
        and "-numeric" not in d
        and "-time" not in d
        and is_domain_typed(year, d)
    ]
    doms.sort()
    return doms

def list_domain_instances(year: str, domain_name: str) -> List[str]:
    """Returns list of instance problem files for a domain."""
    instances_dir = os.path.join(BENCHMARK_ROOT, year, "domains", domain_name, "instances")
    if not os.path.exists(instances_dir):
        return []
    files = [f for f in os.listdir(instances_dir) if f.endswith(".pddl")]
    # Natural sort e.g. instance-1, instance-2, ..., instance-10
    def sort_key(name):
        nums = re.findall(r"\d+", name)
        return int(nums[0]) if nums else 0
    files.sort(key=sort_key)
    return files

def get_ipc_domain_pddl(year: str, domain_name: str) -> str:
    """Reads the reference domain.pddl for the given IPC domain."""
    domain_path = os.path.join(BENCHMARK_ROOT, year, "domains", domain_name, "domain.pddl")
    if os.path.exists(domain_path):
        with open(domain_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""

def get_ipc_instance_pddl(year: str, domain_name: str, instance_filename: str) -> str:
    """Reads a specific problem instance PDDL file."""
    inst_path = os.path.join(BENCHMARK_ROOT, year, "domains", domain_name, "instances", instance_filename)
    if os.path.exists(inst_path):
        with open(inst_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""

def get_nl_requirement_for_domain(domain_name: str) -> str:
    """Returns a natural language prompt template for a domain family."""
    d_clean = domain_name.lower().replace("-", "").replace("_", "")
    
    # Priority matching: match longer/more specific keys first to avoid substrings (e.g. nomystery before mystery)
    sorted_keys = sorted(
        IPC_NL_DESCRIPTIONS.keys(),
        key=lambda k: len(k.replace("-", "").replace("_", "")),
        reverse=True
    )
    for key in sorted_keys:
        k_clean = key.lower().replace("-", "").replace("_", "")
        if k_clean in d_clean:
            return IPC_NL_DESCRIPTIONS[key]
            
    # Generic fallback
    clean_title = (
        domain_name.replace("-round-1", "")
        .replace("-round-2", "")
        .replace("-strips", "")
        .replace("-adl", "")
        .replace("-", " ")
        .title()
    )
    return f"Model the classic {clean_title} planning domain in PDDL with standard state predicates, preconditions, and action schemas."

def parse_pddl_problem_to_blueprint(pddl_str: str) -> Dict[str, Any]:
    from tools.blueprint_parser import parse_pddl_problem_to_blueprint as _parse
    return _parse(pddl_str)



def load_historical_case_from_ipc(year: str, domain_name: str, instance_filename: str) -> Optional[Dict[str, Any]]:
    """Loads a real IPC instance file and prepares it as a HistoricalProblemCase."""
    raw_pddl = get_ipc_instance_pddl(year, domain_name, instance_filename)
    if not raw_pddl:
        return None
    bp = parse_pddl_problem_to_blueprint(raw_pddl)
    return {
        "case_id": f"{year}_{domain_name}_{instance_filename.replace('.pddl', '')}",
        "problem_blueprint": bp,
        "raw_pddl": raw_pddl
    }


# ==============================================================================
# AutoPlanBench (ICAPS 2025 Pure Typed STRIPS) Loader Helpers
# ==============================================================================
AUTOPLANBENCH_ROOT = os.path.join(BENCHMARK_ROOT, "autoplanbench")

def list_autoplanbench_domains() -> List[str]:
    """Returns sorted list of available pure typed STRIPS domains from AutoPlanBench."""
    if not os.path.exists(AUTOPLANBENCH_ROOT):
        return []
    domains = [
        d for d in os.listdir(AUTOPLANBENCH_ROOT)
        if os.path.isdir(os.path.join(AUTOPLANBENCH_ROOT, d)) and not d.startswith(".")
    ]
    return sorted(domains)

def get_autoplanbench_nl_description(domain_name: str) -> str:
    """Returns the natural language specification from domain_description.txt."""
    desc_path = os.path.join(AUTOPLANBENCH_ROOT, domain_name, "domain_description.txt")
    if os.path.exists(desc_path):
        with open(desc_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    return f"Natural language domain specification for {domain_name}."

def get_autoplanbench_domain_pddl(domain_name: str) -> str:
    """Returns ground-truth domain.pddl text for an AutoPlanBench domain."""
    dom_path = os.path.join(AUTOPLANBENCH_ROOT, domain_name, "domain.pddl")
    if os.path.exists(dom_path):
        with open(dom_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    return ""

def list_autoplanbench_instances(domain_name: str) -> List[str]:
    """Lists problem instance filenames (e.g. instance-1.pddl) for a domain."""
    prob_dir = os.path.join(AUTOPLANBENCH_ROOT, domain_name, "problems")
    if not os.path.exists(prob_dir):
        return []
    instances = [f for f in os.listdir(prob_dir) if f.endswith(".pddl")]
    # Natural sort by instance index
    def _sort_key(s):
        m = re.search(r"(\d+)", s)
        return int(m.group(1)) if m else s
    return sorted(instances, key=_sort_key)

def get_autoplanbench_instance_pddl(domain_name: str, instance_filename: str) -> str:
    """Returns the PDDL text of a specific problem instance."""
    inst_path = os.path.join(AUTOPLANBENCH_ROOT, domain_name, "problems", instance_filename)
    if os.path.exists(inst_path):
        with open(inst_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    return ""

def load_historical_case_from_autoplanbench(domain_name: str, instance_filename: str) -> Optional[Dict[str, Any]]:
    """Loads an AutoPlanBench problem instance as a HistoricalProblemCase."""
    raw_pddl = get_autoplanbench_instance_pddl(domain_name, instance_filename)
    if not raw_pddl:
        return None
    bp = parse_pddl_problem_to_blueprint(raw_pddl)
    return {
        "case_id": f"apb_{domain_name}_{instance_filename.replace('.pddl', '')}",
        "problem_blueprint": bp,
        "raw_pddl": raw_pddl
    }


# ==============================================================================
# PDDLLifeCycleBench (24 Domains: Flaws & Evolution) Helpers
# ==============================================================================
PDDL_LIFECYCLE_BENCH_ROOT = os.path.join(PROJECT_ROOT, "PDDLLifeCycleBench")

def list_lifecycle_domains() -> List[str]:
    """Returns list of canonical domains in PDDLLifeCycleBench."""
    if not os.path.exists(PDDL_LIFECYCLE_BENCH_ROOT):
        return []
    return sorted([
        d for d in os.listdir(PDDL_LIFECYCLE_BENCH_ROOT)
        if os.path.isdir(os.path.join(PDDL_LIFECYCLE_BENCH_ROOT, d)) and not d.startswith((".", "__"))
    ])

def list_lifecycle_flaws(domain_name: str) -> List[str]:
    """Returns list of flaw directories in PDDLLifeCycleBench/<domain>/flaws."""
    flaw_dir = os.path.join(PDDL_LIFECYCLE_BENCH_ROOT, domain_name, "flaws")
    if not os.path.exists(flaw_dir):
        return []
    return sorted([
        f for f in os.listdir(flaw_dir)
        if os.path.isdir(os.path.join(flaw_dir, f))
    ])

def get_lifecycle_flaw_pddl(domain_name: str, flaw_name: str) -> Dict[str, Any]:
    """Returns flawed domain, problem, metadata, and specification for a flaw task."""
    flaw_path = os.path.join(PDDL_LIFECYCLE_BENCH_ROOT, domain_name, "flaws", flaw_name)
    res = {
        "domain_flawed": "",
        "problem": "",
        "specification": "",
        "metadata": {}
    }
    if not os.path.exists(flaw_path):
        return res
    dom_file = os.path.join(flaw_path, "domain_flawed.pddl")
    if os.path.exists(dom_file):
        with open(dom_file, "r", encoding="utf-8", errors="ignore") as f:
            res["domain_flawed"] = f.read()
    prob_file = os.path.join(flaw_path, "problem_flawed.pddl")
    if not os.path.exists(prob_file):
        prob_file = os.path.join(PDDL_LIFECYCLE_BENCH_ROOT, domain_name, "orig_problems", "instance-1.pddl")
    if os.path.exists(prob_file):
        with open(prob_file, "r", encoding="utf-8", errors="ignore") as f:
            res["problem"] = f.read()
    spec_file = os.path.join(flaw_path, "complete_specification.txt")
    if os.path.exists(spec_file):
        with open(spec_file, "r", encoding="utf-8", errors="ignore") as f:
            res["specification"] = f.read()
    meta_file = os.path.join(flaw_path, "flaw_metadata.json")
    if os.path.exists(meta_file):
        import json
        with open(meta_file, "r", encoding="utf-8", errors="ignore") as f:
            res["metadata"] = json.load(f)
    return res

def list_lifecycle_evolutions(domain_name: str) -> List[str]:
    """Returns list of evolution directories in PDDLLifeCycleBench/<domain>/evolution."""
    evo_dir = os.path.join(PDDL_LIFECYCLE_BENCH_ROOT, domain_name, "evolution")
    if not os.path.exists(evo_dir):
        return []
    return sorted([
        e for e in os.listdir(evo_dir)
        if os.path.isdir(os.path.join(evo_dir, e))
    ])


