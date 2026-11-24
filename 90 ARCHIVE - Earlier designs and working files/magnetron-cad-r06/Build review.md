# 2-inch magnetron gun R06

Open Magnetron gun R06.SLDASM with its referenced files in this folder. The assembly contains eight subassemblies and 45 part instances. SolidWorks opened the assembly with all references resolved. Its interference check reported four overlaps, all where the two angled coolant transitions meet their bulkheads and dielectric lines. The modeled overlaps are about 1.4 to 1.5 mm³ each.

## Assembly interfaces

| Interface | R06 layout | Detail needed before machining |
|---|---|---|
| Gun mount | NW100 plate, welded stem, and KF25 stub. The removable feedthrough uses the KF25 clamp and centering seal. | Confirm the chamber port bore, centering seal envelope, and clamp service space using the actual hardware. The shield mounting flange is Ø92 mm. |
| Power | Ceramaseal feedthrough, socket and power rod, ceramic guide and head carrier. | Define the rod socket contact and retention. Detail the grounded terminal enclosure and RF return. Verify electrical clearance and isolation at the 1,200 V DC design basis and measured RF peak. |
| Head support | Ceramic carrier between the grounded stem and live yoke. The copper jacket backplate seats against the yoke. | Define positive capture of the ceramic using separate retainers on the grounded and powered sides. Check that attachment hardware preserves electrical isolation and clears the water passages. |
| Magnet pack | One annular center magnet and eight outer magnets sit in the 5 mm nonmagnetic locator behind the yoke. | Confirm field at the target face with the actual magnet grade and dimensions. Detail positive retention and confirm how the pack is assembled around the tubing. |
| Cooling | Two bulkheads, angled transitions, dielectric sections, cathode-side tubes, copper backplate, C-channel core with divider, and target-seat cover. | Replace both overlapping transition envelopes with matched tube ends and specified sealed joints. Define how the copper stack is sealed and verify the channel is continuous through both ports. Check the coolant's electrical leakage and the tube material's vacuum compatibility. |
| Target | Ø50.8 mm aluminum disc and Ø68.8 mm clamp with a Ø48 mm opening. Three screws on a Ø58.8 mm bolt circle. | Confirm screw stock, recess depth, clamp load, usable tapped depth, and clearance from the water jacket. |
| Shield | Removable grounded shield with a bolted rear seat, Ø72.8 mm bore, and Ø46.8 mm lip opening. The nominal side gap is 2 mm. | Confirm the grounding joint, clamp-to-lip clearance under tolerance, and space to withdraw the shield toward the chamber interior before removing the target. |

R06 is a detailed assembly model for design review. Purchased parts, screws, seals, and several fabricated interfaces still use layout geometry. Fabrication release depends on the interface checks above, coolant pressure and vacuum leak tests, and commissioning in DC and RF.
