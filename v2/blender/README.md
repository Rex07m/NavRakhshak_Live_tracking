# NavRakhshak Blender workflow

The primary local Blender builder is `build_navrakshak_cinematic.py`.

## Blender 5.2 LTS

1. Open **Blender 5.2 LTS** on the PC.
2. Open the **Scripting** workspace.
3. Open `v2/blender/build_navrakshak_cinematic.py` from this repository, or paste it into a new Text block.
4. Click **Run Script**.
5. The script clears the previous scene and rebuilds the upgraded NavRakhshak cinematic scene.
6. It writes the GLB, `.blend`, and preview PNG into `Downloads/NavRakhshak_Blender/`.

## What's included

- Hydrodynamic tapered rescue/work-boat hull instead of box-only geometry.
- Raised wheelhouse with marine glazing, roof, deck rails, fenders, safety belt, mast, radar dish, navigation lights and emergency beacon.
- A **horizontal XY ocean surface** with wave height on Blender's Z axis. The previous builder accidentally put wave height on Y, which made the ocean effectively vertical and invisible from the intended camera.
- Multi-frequency procedural wave geometry plus animated swell shape keys.
- PBR-style ocean material with procedural noise/bump for visible water texture.
- Procedural atmospheric sky, physical sun light, warm/cool cinematic lights and a visible sun disc.
- Cinematic camera movement and animated vessel/radar elements.
- Tactical range rings, wake foam and geofence remain available in the Blender source scene.
- **GLB export is selection-limited to `NAVRAKHSHAK_VESSEL`**, so the web viewer does not accidentally scale the ocean/geofence together with the boat.

## Blender 5.2 render-engine fix

Blender 5.2 LTS exposes EEVEE as `BLENDER_EEVEE`. The current builder uses `BLENDER_EEVEE` first and has a fallback for other Blender 5.x builds. **Do not change it to `BLENDER_EEVEE_NEXT` in Blender 5.2.**

## Website role

The production web experience uses Three.js for real-time interaction and Firebase for live telemetry. Blender supplies the higher-fidelity vessel asset and cinematic source scene; the browser supplies interactive ocean waves, lighting, camera controls, radar, geofence and live vessel movement.

After running the builder, replace the deployed `v2/blender/navrakshak_vessel.glb` with the newly generated GLB so the upgraded hull appears on the live site.

`navrakshak_scene.py` is retained as the older scene-builder reference; use `build_navrakshak_cinematic.py` for the current asset pipeline.
