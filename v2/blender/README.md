# NavRakhshak Blender workflow

The primary local Blender builder is `build_navrakshak_cinematic.py`.

## Run it locally

1. Open **Blender 5.x** on the PC.
2. Open the **Scripting** workspace.
3. Open `v2/blender/build_navrakshak_cinematic.py` from this repository, or paste it into a new Text block.
4. Click **Run Script**.
5. The script builds the upgraded NavRakhshak cinematic scene.
6. It writes the GLB, `.blend`, and preview PNG into `Downloads/NavRakhshak_Blender/`.

## What's new

- Hydrodynamic tapered rescue/work-boat hull instead of box-only geometry.
- Raised wheelhouse with marine glazing, roof, deck rails, fenders, safety belt, mast, radar dish, navigation lights and emergency beacon.
- Multi-layer animated ocean with procedural waves and sea foam.
- Warm cinematic sun, cool fill lighting and a deeper maritime world setup.
- Cinematic camera movement and animated vessel/radar elements.
- Tactical range rings and geofence remain available in the Blender scene.
- **GLB export is selection-limited to `NAVRAKHSHAK_VESSEL`**, so the web viewer does not accidentally scale the ocean/geofence together with the boat.

## Website role

The production web experience uses Three.js for real-time interaction and Firebase for live telemetry. Blender supplies the higher-fidelity vessel asset and cinematic source scene; the browser supplies interactive ocean waves, lighting, camera controls, radar, geofence and live vessel movement.

After running the builder, replace the deployed `v2/blender/navrakshak_vessel.glb` with the newly generated GLB so the upgraded hull appears on the live site.

`navrakshak_scene.py` is retained as the older scene-builder reference; use `build_navrakshak_cinematic.py` for the current asset pipeline.
