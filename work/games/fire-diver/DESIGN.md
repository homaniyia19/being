# Fire-Diver — design

Inspired by Wilhelm Bauer's *Brandtaucher* (Kiel, 1850): a submarine driven by men on tread wheels, with no ballast tanks,
so the ballast water sloshed loose in the bottom of the hull. That flaw is the heart of the game.

## The boat (units: metres, seconds)
- 8 m long. Facing left or right. Pitch angle, nose-down positive, limited to about ±40°.
- **Pedalling:** alternate ← and → (or A and D). Each alternation adds to the crank; pressing the same key twice does nothing.
  The crank decays. Thrust goes along the hull, so a nose-down boat drives itself deeper.
- **Ballast:** Q floods (heavier, sinks), E pumps out (lighter, rises). Neutral at half full. Pumping is hard work: it uses air.
- **Slosh:** the loose water runs to whichever end is lower, and pushes that end further down. The more water aboard, the worse.
- **Trim weight:** W shifts a weight aft (nose up), S forward (nose down). This is how you fight the slosh.
- **F** turns the gear around (face the other way).
- **Space** grabs an item from the seabed under the boat, or drops it. One item at a time; it adds weight.
- **X** is Bauer's escape: let water in until the pressure inside equals the sea, open the hatch, swim up.
  The dive is lost, the crew lives. It also happens on its own when the air runs out or the flooded hull hits bottom.

## Limits
- **Air** runs down all the time, faster when pedalling or pumping. Surfacing anywhere refills it.
- **Hull** rated to 9.5 m. Deeper, it creaks and takes damage. Hitting the bottom hard also damages it.
  A breached hull floods steadily.

## Levels
1. **Kiel harbour, morning.** Shallow, calm. Two things to bring up. Tutorial hints.
2. **The outer harbour.** Deeper. Three things, one below the hull's rating: a quick dip and back.
3. **Night.** Dark water, the boat's lamp shows a cone. Three things on a jagged bottom.
4. **Kronstadt, 6 September 1856.** The coronation dive. Hold the boat level at the marked depth.
   The music plays only while you hold it steady. Keep it steady long enough to finish the tune.

## Feel
- Side view, cold green-blue water, light shafts from the surface, bubbles, kelp, small fish, ships' hulls above.
- Sound from WebAudio: pedal clicks, bubbles, hull creaks, a chime on delivery, a tune at the end.
- A small cut-away of the hull in the corner shows where the water is sloshing. That's the most important instrument.
