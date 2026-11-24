# Sputter gun — working bill of materials

Updated: 15 November 2026. Entries are added as each part is reviewed. This is a partial procurement BOM, not the complete assembly inventory. Quantity is per gun; no spare target is included.

| Item | Description | Qty | Make / buy | Material / purity | Nominal dimensions | Supplier | Supplier part number | Unit price excluding GST (INR) | Listed GST | Unit price including GST (INR) | Source | Review status |
|---|---|---:|---|---|---|---|---|---:|---:|---:|---|---|
| 401 | Aluminium (Al) sputtering target | 1 | Buy | Aluminum, 99.99% purity (supplier listing) | Diameter 2.000 in / 50.800 mm; thickness 0.125 in / 3.175 mm | Vritra Technologies | Not stated on product page | 8,300 | 18% | 9,794 | [Product page](https://www.vritratech.com/store/product/aluminium-al-sputtering-target/) | Selected by user; nominal size updated in SolidWorks. Clamp adaptation pending. |
| 308 | Integral copper target seat and coolant-channel body | 1 | Make, from one blank | Copper; grade and temper not yet specified | Diameter 68.800 mm × 9.000 mm; rear C-channel 4.000 mm deep, radii 10.400–25.000 mm; front wall 5.000 mm; six M3 thread locations on diameter 58.800 mm circle | Fabricator TBD | Internal item 308; replaces separate 306 and 308 | TBD | TBD | TBD | R09 308 Integral copper target seat and channel.SLDPRT | One-solid body verified and installed in assembly. Rear closure, venting, machining radii, tolerances and preload pending. |
| 305 | Rear coolant closure with brazing lands and dry vent groove | 1 | Make | Copper; grade/temper to be coordinated with 308 and braze process | OD 68.800 mm; 3.000 mm outer rim; 2.950 mm central thickness; groove radii 26.2–27.2 mm, depth 0.5 mm; two diameter 4.60 mm tube bores; three diameter 3.30 mm mounting holes | Fabricator TBD | Internal item 305 | TBD | TBD | TBD | R09 305 Brazing-land rear closure.SLDPRT | Proposed J1 face-braze and J2/J3 tube joints. CAD gap 0.050 mm provisional. Filler, process, structural and leak qualification outstanding. |

## Item 401 procurement notes

- Supplier page checked 15 November 2026. It lists 2 units in stock; availability and price are snapshots, not a reservation or quotation.
- Listed price: INR 8,300 + INR 1,494 GST = INR 9,794 per target. Shipping is not specified and is excluded from this amount.
- Supplier lists CAS 7429-90-5, HSN 84862000 and DC sputtering. CAS and HSN are not supplier part numbers.
- Diameter/thickness tolerances, rear-face flatness, face parallelism, surface finish, edge treatment, and whether a purity certificate is included are not stated on the page. Obtain these before final fit/release.
- The existing SolidWorks material entry is 1060 Alloy. It is a legacy CAD material proxy, not the procurement specification. The procurement requirement is the listed 99.99% aluminum target.
- The target rear face remains at X = 168.700 mm; its revised front face is X = 171.875 mm. The unchanged clamp lip remains at X = 174.700 mm, leaving a 2.825 mm axial gap. The current clamp must be redesigned during its review.

## Item 308 fabrication notes

- Custom part; quantity one per gun. No supplier or price selected.
- Updated after user approval: former channel core 306 is integral with 308, not a separately manufactured or purchased item. Overall jacket thickness remains 12 mm including the separate 3 mm rear plate 305.
- The six holes alternate between three head-attachment holes and three target-clamp holes. M3×0.5 threads are represented by 2.5 mm pilot bores. Rear head holes retain 3.3 mm clearance for the rear 4 mm, then the 5 mm thread zone. Front clamp holes are now blind 5 mm pilot pockets with a nominal 4 mm backing thickness; full thread/runout/drill-point details and dry-side venting remain to be finalized.
- The integral body has a flat front target seat and an open rear C-channel. The separate backplate 305 must seal the rear opening, including the divider. The eliminated seat-to-core interface is no longer a joining seam.
- The selected 3.175 mm target retains the same rear seating plane at X = 168.700 mm. The clamp must be adapted separately.
- See [the dimensional review](magnetron-cad-r09/308%20part%20review.md) for the complete hole coordinates, clearances and release questions.

## Item 305 sealing revision

- New native closure replaces the old flat backplate in the active assembly. The target seat position, head envelope, three mounting-screw axes and three target-clamp axes are unchanged.
- See [the coolant joint specification](magnetron-cad-r09/Coolant%20joint%20design%20revision.md). This defines proposed joining geometry, not a certified pressure/vacuum component.
- The annular dry groove and radial vent are outside the primary water seal. They are open to chamber vacuum, not a drain or secondary containment system. A failed primary seal remains a water-to-vacuum failure.
