# Magnetron R08 design record

R08 retains the 2-inch target, 68.8 mm cathode, rear-mounted magnet pack, inward-lip shield and NW100 chamber interface. All clearance values are nominal millimetres in the native model.

## Ceramic head support

- The stepped alumina carrier has a Ø60 rear shoulder that seats against the end of the grounded stem. A separate stainless keeper captures the shoulder and uses three M3 screws inserted from the rear of the grounded shield seat. The keeper pilot has 0.25 mm nominal radial clearance at the shoulder and 0.20 mm at the smaller diameter. The unshimmed CAD stack shows nominal axial contact. Set shoulder capture with selective shims and a tolerance stack, with load limited to avoid point-loading the ceramic.
- Three separate live M3 screws and load-spreading washers clamp the carrier to the magnet-pack stack and end in blind holes in the yoke. The inner screws attach the carrier while the existing outer head screws attach the copper stack. The ground keeper screws are driven from the stem side of the shield seat. Assemble the ceramic, locator and yoke on the bench before fitting the keeper.
- The carrier has two independent coolant clearances. The electrical conductor and coolant pipes should be relieved of structural loading. The ceramic carrier is inside vacuum and does not serve as a vacuum seal.
- Nominal minimum keeper-to-live-yoke axial gap is 6.0 mm. This is a geometric dimension. Characterize isolation in the actual argon and deposition conditions, including metal deposition on the ceramic, and establish the permissible operating envelope.

## Coolant

- Flow path in each line runs from welded NW100 bulkhead through the R07 stainless transition, a C10100 copper reducing adapter, an OFHC socket and alumina break, another socket and reducing adapter, then the existing copper tube and brazed jacket. The second line carries the return with reverse flow. Copper male ends at the sockets are Ø6.35 mm OD with 5 mm modeled engagement. The two axes are 20.4 mm apart at the breaks and 6.18 mm apart at the jacket.
- Both breaks reserve Ø14 × 38 mm including their end sockets. Lesker CFT05W0321 is the first candidate. Its published 5 kV DC value applies to dry atmosphere on one side and below 1e-4 Torr on the other. The model contains a reserved envelope. Obtain seller STEP, pressure rating and joining instructions, then confirm suitability with the ceramic exterior in process argon and with flowing coolant at DC and RF.
- Ground-side stainless-to-copper joint and copper-to-socket joints need supplier-approved vacuum-compatible joining procedures. Install the jacket tubes and braze the jacket before adding magnets or the ceramic parts. Establish an assembly and repair sequence for the two permanent coolant joints across the removable head interface. The two coolant legs each require isolation. Monitor coolant conductivity as well as flow. For illustration, at 1 µS/cm, a 24 mm long, Ø4.8 mm ideal water column gives approximately 13.3 MΩ per leg, or 0.18 mA total at 1.2 kV DC. Actual leakage depends on wetted geometry, coolant state and additional paths. RF current and heating require separate measurement.
- The current guard surrounds the two atmospheric coolant stubs. Finalize sealed or finger-safe side exits and the external elbow/hoses alongside the cable entry and interlock, keeping grounded fittings out of the live terminal clearance.

## Power termination

- The shaft from the Ceramaseal is live. A copper terminal socket envelope stays inside a bolted conductive enclosure on the atmosphere side. The shell bolts to the NW100 plate and the rear cover bolts to the shell. Prepare clean conductive seams. The cable supply-side connection is a manual one-at-a-time swap with both sources disabled and stored charge discharged.
- Use the RF matcher output cable center for the socket and bond its shield circumferentially at entry. Provide a short, wide bond from the enclosure/plate to matcher chassis and a protective-earth bond. For the DC cable, wire its return and chassis bond per the chosen supply. Implement a cover interlock that inhibits both sources, a verified discharge procedure, and cable strain relief that does not load the feedthrough.
- The cable, terminal and rear aperture are packaging envelopes. Choose the exact output cable/connector and interlock hardware against the matcher and DC supply models, including peak RF voltage/current under ignition and mismatch. A good impedance match can coexist with high feedthrough voltage.

## Materials and release checks

- A4-80 stainless M3 screws are the design selection. SolidWorks uses 316L as the density/appearance proxy and retains A4-80 in the engineering material field. Verify actual certified stock and usable copper thread engagement. Avoid torque tables based on steel nuts for copper threads or ceramic washers. Confirm preload, pull-out, thermal cycle, and unintended ceramic loading.
- N42SH is the provisional grade for both axially magnetized magnet shapes. The outer eight share one polarity and the center has the opposite polarity toward the yoke. The native custom material uses an approximate 7,500 kg/m³ density. It includes no magnetic constitutive data. Determine a vacuum-compatible coating and check supplier demagnetization curves against actual temperature and operating point. Map the face-parallel field across the intended racetrack after assembly and repeat after thermal cycling. The rear-of-yoke arrangement and 5 mm magnet thickness need that check.
- Before powering, verify pressure-drop and flow, hydraulic proof and helium leakage, protective-earth continuity, cover interlock and discharge function, wet isolation with argon over the operating pressure range, and matched RF temperature/rise under power. The shield removes toward the substrate after the three shield screws are withdrawn. Its open rear bore passes around the head. The front lip starts ahead of the target and moves farther forward. Nominal shield travel to clear the front of the retaining ring is 41 mm, plus handling allowance. Verify available space and tool access with the actual chamber adapter.

Sources

- [Lesker CFT05W0321](https://www.lesker.com/feedthroughs/ceramicbreaks-liquid/part/cft05w0321)
- [Lesker matching network manual](https://www.lesker.com/newweb/process_instruments/pdf/manuals/manual-kjlc-ejmm-manualimpedancematchingnetwork.pdf)
- [Arnold N42SH material data](https://www.arnoldmagnetics.com/products/neodymium-iron-boron-magnets/)
- [Bossard stainless fastener properties](https://media.bossard.com/global-en/-/media/bossard-group/website/documents/technical-resources/en/f-021-en.pdf)


